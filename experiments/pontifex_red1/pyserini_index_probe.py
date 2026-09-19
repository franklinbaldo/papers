# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyserini>=1.2.0",
#   "faiss-cpu>=1.8.0",
#   "numpy>=2.0",
# ]
# ///
"""Probe a Pyserini prebuilt dense index as a reusable embedding artifact.

Scientific/infrastructure question:
Can we prove the chain internal FAISS position -> external MS MARCO pid -> stored
passage text, and reconstruct exact vectors from a prebuilt Flat index without
running the passage encoder or loading all 8.8M vectors into RAM?
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import faiss
import numpy as np
from pyserini.search.lucene import LuceneSearcher
from pyserini.util import download_prebuilt_index

DEFAULT_INDEX = "msmarco-v1-passage.tct_colbert-v2-hnp"
DEFAULT_CORPUS = "msmarco-v1-passage"


def describe_index(index: faiss.Index) -> dict[str, object]:
    return {
        "class": type(index).__name__,
        "dimension": int(index.d),
        "ntotal": int(index.ntotal),
        "is_trained": bool(index.is_trained),
        "metric_type": int(index.metric_type),
        "supports_reconstruct": hasattr(index, "reconstruct"),
        "supports_reconstruct_n": hasattr(index, "reconstruct_n"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--corpus-index", default=DEFAULT_CORPUS)
    ap.add_argument("--positions", type=int, nargs="+", default=[0, 42, 8841822])
    ap.add_argument("--output", type=Path, default=Path("pyserini-index-probe.json"))
    args = ap.parse_args()

    disk_before = shutil.disk_usage("/")
    print(f"disk_before total={disk_before.total} free={disk_before.free} used={disk_before.used}", flush=True)

    # Download/extract the official Pyserini artifact without constructing a
    # FaissSearcher, because the normal constructor eagerly loads IndexFlat into RAM.
    index_dir = download_prebuilt_index(args.index, verbose=True)
    index_path = os.path.join(index_dir, "index")
    docid_path = os.path.join(index_dir, "docid")
    print(f"index_dir={index_dir}", flush=True)
    print(f"index_bytes={os.path.getsize(index_path)} docid_bytes={os.path.getsize(docid_path)}", flush=True)

    # Newer FAISS provides IO_FLAG_MMAP_IFC specifically for IndexFlatCodes-derived
    # indexes. Combine with READ_ONLY so only touched pages need enter resident RAM.
    mmap_flag = getattr(faiss, "IO_FLAG_MMAP_IFC", None)
    if mmap_flag is None:
        raise RuntimeError("installed FAISS lacks IO_FLAG_MMAP_IFC")
    index = faiss.read_index(index_path, mmap_flag | faiss.IO_FLAG_READ_ONLY)
    info = describe_index(index)
    print(f"dense mmap index: {info}", flush=True)

    with open(docid_path, encoding="utf-8") as f:
        docids = [line.rstrip("\n") for line in f]
    if int(index.ntotal) != len(docids):
        raise AssertionError(f"FAISS vectors={index.ntotal} but docids={len(docids)}")

    # The dense artifact intentionally does not store source text. Fetch passages
    # from the canonical sparse MS MARCO index using the external pid from docid.
    sparse = LuceneSearcher.from_prebuilt_index(args.corpus_index)

    samples: list[dict[str, object]] = []
    for pos in args.positions:
        if not 0 <= pos < index.ntotal:
            raise ValueError(f"position {pos} outside [0, {index.ntotal})")
        pid = docids[pos]
        vector = np.asarray(index.reconstruct(pos), dtype=np.float32)
        if vector.shape != (index.d,):
            raise AssertionError((pos, vector.shape, index.d))
        if not np.isfinite(vector).all():
            raise AssertionError(f"non-finite vector at {pos}")

        doc = sparse.doc(pid)
        if doc is None:
            raise AssertionError(f"pid {pid} absent from sparse MS MARCO index")
        raw = doc.raw()
        try:
            parsed = json.loads(raw)
            text = parsed.get("contents") or parsed.get("text") or raw
        except Exception:
            text = raw

        sample = {
            "position": pos,
            "pid": pid,
            "vector_shape": list(vector.shape),
            "vector_dtype": str(vector.dtype),
            "vector_norm": float(np.linalg.norm(vector)),
            "vector_first8": [float(x) for x in vector[:8]],
            "passage_preview": str(text)[:300],
        }
        samples.append(sample)
        print(json.dumps(sample, ensure_ascii=False), flush=True)

    positional_identity = all(str(s["position"]) == str(s["pid"]) for s in samples)
    disk_after = shutil.disk_usage("/")
    result = {
        "experiment": "Pyserini prebuilt embedding artifact provenance probe",
        "dense_alias": args.index,
        "corpus_alias": args.corpus_index,
        "index_dir": index_dir,
        "index_bytes": os.path.getsize(index_path),
        "docid_bytes": os.path.getsize(docid_path),
        "loading_mode": "FAISS IO_FLAG_MMAP_IFC | IO_FLAG_READ_ONLY",
        "index": info,
        "docid_count": len(docids),
        "positional_identity_on_samples": positional_identity,
        "samples": samples,
        "disk": {
            "before_free": disk_before.free,
            "after_free": disk_after.free,
            "consumed": disk_before.free - disk_after.free,
        },
        "conclusion": "CHAIN_VERIFIED",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = args.output.with_suffix(".md")
    lines = [
        "# Pyserini MS MARCO prebuilt-index probe",
        "",
        f"- Dense alias: `{args.index}`",
        f"- FAISS class: `{info['class']}`",
        f"- vectors: **{info['ntotal']:,}**",
        f"- dimension: **{info['dimension']}**",
        f"- index bytes: **{os.path.getsize(index_path):,}**",
        f"- docid mapping rows: **{len(docids):,}**",
        f"- loading: **mmap read-only**",
        f"- sampled `position == pid`: **{positional_identity}**",
        f"- conclusion: **{result['conclusion']}**",
        "",
        "| internal position | external pid | shape | norm | passage preview |",
        "|---:|---:|---:|---:|---|",
    ]
    for s in samples:
        preview = str(s["passage_preview"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {s['position']} | {s['pid']} | {s['vector_shape']} | {s['vector_norm']:.4f} | {preview} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
