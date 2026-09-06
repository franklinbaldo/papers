from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from transformers import AutoTokenizer


OAI = "https://export.arxiv.org/oai2"
OAI_NS = "http://www.openarchives.org/OAI/2.0/"
ARXIV_NS = "http://arxiv.org/OAI/arXiv/"
START = date(2025, 7, 1)
END = date(2026, 6, 30)
TARGET = 120_000
TOKENIZER = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "1110a24"
MAX_TOKENS = 256
SLEEP_SECONDS = 3.1
CHUNK_BYTES = 50 * 1024 * 1024


def normalize_text(text: str | None) -> str:
    return " ".join((text or "").split())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_xml(params: dict[str, str]) -> ET.Element:
    url = OAI + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "semantic-atlas-scale-study/1.0 (research; GitHub franklinbaldo/papers)"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return ET.fromstring(response.read())


def text(node: ET.Element | None, name: str) -> str:
    if node is None:
        return ""
    child = node.find(f"{{{ARXIV_NS}}}{name}")
    return normalize_text(child.text if child is not None else "")


def harvest_records() -> list[dict]:
    records: list[dict] = []
    params = {"verb": "ListRecords", "metadataPrefix": "arXiv", "from": START.isoformat()}
    page = 0
    while True:
        root = fetch_xml(params)
        page += 1
        listed = root.find(f"{{{OAI_NS}}}ListRecords")
        if listed is None:
            raise RuntimeError("OAI response missing ListRecords")
        for record in listed.findall(f"{{{OAI_NS}}}record"):
            header = record.find(f"{{{OAI_NS}}}header")
            if header is not None and header.attrib.get("status") == "deleted":
                continue
            meta = record.find(f"{{{OAI_NS}}}metadata")
            arxiv = meta.find(f"{{{ARXIV_NS}}}arXiv") if meta is not None else None
            if arxiv is None:
                continue
            created_s = text(arxiv, "created")
            try:
                created = date.fromisoformat(created_s)
            except ValueError:
                continue
            if not (START <= created <= END):
                continue
            arxiv_id = text(arxiv, "id")
            abstract = text(arxiv, "abstract")
            title = text(arxiv, "title")
            categories = text(arxiv, "categories").split()
            if not arxiv_id or not abstract or not categories:
                continue
            records.append(
                {
                    "arxiv_id": arxiv_id,
                    "created": created_s,
                    "updated": text(arxiv, "updated") or None,
                    "title_sha256": hashlib.sha256(title.encode("utf-8")).hexdigest(),
                    "abstract": abstract,
                    "abstract_sha256": hashlib.sha256(abstract.encode("utf-8")).hexdigest(),
                    "categories": categories,
                    "primary_category": categories[0],
                    "selection_sha256": hashlib.sha256(arxiv_id.encode("utf-8")).hexdigest(),
                }
            )
        token_node = listed.find(f"{{{OAI_NS}}}resumptionToken")
        token = normalize_text(token_node.text if token_node is not None else "")
        print(json.dumps({"page": page, "eligible_date_records_so_far": len(records), "has_more": bool(token)}))
        if not token:
            break
        time.sleep(SLEEP_SECONDS)
        params = {"verb": "ListRecords", "resumptionToken": token}
    dedup = {}
    for row in records:
        dedup.setdefault(row["arxiv_id"], row)
    return list(dedup.values())


def apply_length_guard(records: list[dict]) -> tuple[list[dict], dict]:
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, revision=REVISION, use_fast=True)
    kept = []
    lengths = []
    for idx, row in enumerate(records, 1):
        ids = tokenizer(
            row["abstract"],
            add_special_tokens=True,
            truncation=False,
            return_attention_mask=False,
            return_token_type_ids=False,
        )["input_ids"]
        n = len(ids)
        lengths.append(n)
        if n <= MAX_TOKENS:
            item = dict(row)
            item["minilm_wordpieces_including_special"] = n
            kept.append(item)
        if idx % 10_000 == 0:
            print(json.dumps({"tokenized": idx, "kept": len(kept)}))
    return kept, {
        "records_before_length_guard": len(records),
        "records_after_length_guard": len(kept),
        "token_length_min": min(lengths) if lengths else None,
        "token_length_max": max(lengths) if lengths else None,
        "max_allowed": MAX_TOKENS,
    }


def write_deterministic_gzip_jsonl(rows: list[dict], path: Path) -> tuple[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            for row in rows:
                gz.write((json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    data = path.read_bytes()
    return sha256_bytes(data), len(data)


def split_if_needed(path: Path) -> list[dict]:
    if path.stat().st_size <= 95 * 1024 * 1024:
        return [{"path": path.name, "sha256": sha256_bytes(path.read_bytes()), "bytes": path.stat().st_size}]
    parts = []
    with path.open("rb") as src:
        index = 0
        while True:
            chunk = src.read(CHUNK_BYTES)
            if not chunk:
                break
            part = path.with_name(f"{path.name}.part-{index:03d}")
            part.write_bytes(chunk)
            parts.append({"path": part.name, "sha256": sha256_bytes(chunk), "bytes": len(chunk)})
            index += 1
    path.unlink()
    return parts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/scale_corpus_v1"))
    args = parser.parse_args()

    harvested = harvest_records()
    length_ok, length_stats = apply_length_guard(harvested)
    if len(length_ok) < TARGET:
        raise RuntimeError(f"need at least {TARGET} length-safe records, found {len(length_ok)}")

    selected = sorted(length_ok, key=lambda row: row["selection_sha256"])[:TARGET]
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    corpus_path = out / "arxiv_abstracts_120k.jsonl.gz"
    corpus_sha, corpus_bytes = write_deterministic_gzip_jsonl(selected, corpus_path)
    parts = split_if_needed(corpus_path)

    category_counts: dict[str, int] = {}
    for row in selected:
        category_counts[row["primary_category"]] = category_counts.get(row["primary_category"], 0) + 1

    summary = {
        "schema_version": 1,
        "experiment": "semantic-atlas-large-scale-relational-geometry-v1",
        "source": OAI,
        "created_start": START.isoformat(),
        "created_end": END.isoformat(),
        "unit": "full normalized abstract only",
        "tokenizer": TOKENIZER,
        "tokenizer_revision": REVISION,
        "truncation": False,
        "max_tokens_including_special": MAX_TOKENS,
        "master_size": TARGET,
        "selection": "ascending sha256(base_arxiv_id)",
        "length_guard": length_stats,
        "selected_created_min": min(row["created"] for row in selected),
        "selected_created_max": max(row["created"] for row in selected),
        "category_counts": dict(sorted(category_counts.items())),
        "compressed_corpus_sha256_before_split": corpus_sha,
        "compressed_corpus_bytes_before_split": corpus_bytes,
        "parts": parts,
    }
    (out / "corpus_manifest.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
