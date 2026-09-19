# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyserini>=2.4.0",
# ]
# ///
"""Freeze a label-blind MS MARCO Passage pilot candidate manifest.

The script uses only dev query text plus BM25 retrieval. It never opens dev qrels.
Candidate membership is therefore frozen before any Pontifex transport is fitted or scored.
It also selects a deterministic corpus-PID pool for document-side A<->B transport, excluding
every pilot candidate PID so no evaluation candidate participates in adapter fitting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pyserini.search import get_topics
from pyserini.search.lucene import LuceneSearcher

CORPUS_SIZE = 8_841_823
START = 4_271_903
STEP = 1_888_861
PILOT_SEED = "pontifex-msmarco-pilot-v1"
TOPICS_ALIAS = "msmarco-passage-dev-subset"
SPARSE_INDEX = "msmarco-v1-passage"


def sha_lines(values: list[str]) -> str:
    h = hashlib.sha256()
    for value in values:
        h.update(str(value).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def topic_text(topic: dict) -> str:
    for key in ("title", "query", "text", "description"):
        value = topic.get(key)
        if value:
            return str(value).strip()
    raise ValueError(f"topic has no query text: keys={sorted(topic)}")


def ordered_pilot_qids(topics: dict, n: int) -> list[str]:
    qids = [str(qid) for qid in topics]
    qids.sort(
        key=lambda qid: hashlib.sha256(f"{PILOT_SEED}\0{qid}".encode()).hexdigest()
    )
    if n > len(qids):
        raise ValueError(f"requested {n} pilot queries but only {len(qids)} topics exist")
    return qids[:n]


def deterministic_doc_pool(excluded: set[str], n: int) -> list[str]:
    out: list[str] = []
    i = 0
    while len(out) < n:
        pid = str((START + i * STEP) % CORPUS_SIZE)
        i += 1
        if pid not in excluded:
            out.append(pid)
        if i > CORPUS_SIZE:
            raise RuntimeError("exhausted corpus while selecting transport PIDs")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", type=int, default=256)
    ap.add_argument("--hits", type=int, default=100)
    ap.add_argument("--transport-docs", type=int, default=1024)
    ap.add_argument("--output", type=Path, default=Path("msmarco-pilot-manifest.json"))
    ap.add_argument("--pid-output", type=Path, default=Path("msmarco-pilot-pids.json"))
    args = ap.parse_args()

    topics = get_topics(TOPICS_ALIAS)
    qids = ordered_pilot_qids(topics, args.queries)
    query_texts = {qid: topic_text(topics[int(qid)] if int(qid) in topics else topics[qid]) for qid in qids}

    searcher = LuceneSearcher.from_prebuilt_index(SPARSE_INDEX)
    candidates: dict[str, list[dict[str, object]]] = {}
    candidate_order: list[str] = []
    candidate_seen: set[str] = set()

    for index, qid in enumerate(qids, start=1):
        hits = searcher.search(query_texts[qid], k=args.hits)
        rows: list[dict[str, object]] = []
        for rank, hit in enumerate(hits, start=1):
            pid = str(hit.docid)
            rows.append({"pid": pid, "rank": rank, "bm25_score": float(hit.score)})
            if pid not in candidate_seen:
                candidate_seen.add(pid)
                candidate_order.append(pid)
        candidates[qid] = rows
        if index % 32 == 0:
            print(f"queries={index}/{len(qids)} unique_candidate_pids={len(candidate_order)}", flush=True)

    transport_doc_pids = deterministic_doc_pool(candidate_seen, args.transport_docs)
    explicit_pids = transport_doc_pids + candidate_order
    if len(set(explicit_pids)) != len(explicit_pids):
        raise AssertionError("explicit extraction PID sequence contains duplicates")

    query_lines = [f"{qid}\t{query_texts[qid]}" for qid in qids]
    candidate_lines = [
        f"{qid}\t{row['rank']}\t{row['pid']}\t{row['bm25_score']:.9g}"
        for qid in qids
        for row in candidates[qid]
    ]

    manifest = {
        "type": "pontifex_msmarco_pilot_candidate_manifest",
        "classification": "pilot; label-blind candidate freeze",
        "spec_version": PILOT_SEED,
        "topics_alias": TOPICS_ALIAS,
        "sparse_index_alias": SPARSE_INDEX,
        "pilot_query_count": len(qids),
        "candidate_depth": args.hits,
        "transport_doc_count": len(transport_doc_pids),
        "query_ids_sha256": sha_lines(qids),
        "query_text_sha256": sha_lines(query_lines),
        "candidate_rows_sha256": sha_lines(candidate_lines),
        "candidate_pid_sequence_sha256": sha_lines(candidate_order),
        "transport_doc_pid_sequence_sha256": sha_lines(transport_doc_pids),
        "explicit_extraction_pid_sequence_sha256": sha_lines(explicit_pids),
        "pilot_qids": qids,
        "queries": query_texts,
        "candidates": candidates,
        "candidate_pids": candidate_order,
        "transport_doc_pids": transport_doc_pids,
        "leakage_boundary": {
            "dev_qrels_opened": False,
            "dev_labels_used": False,
            "B_scores_used_for_candidates": False,
            "pontifex_scores_used_for_candidates": False,
            "candidate_generation": "BM25 from dev query text only",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    args.pid_output.write_text(json.dumps(explicit_pids, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "pilot_queries": len(qids),
                "candidate_rows": sum(len(v) for v in candidates.values()),
                "unique_candidate_pids": len(candidate_order),
                "transport_doc_pids": len(transport_doc_pids),
                "extraction_pids": len(explicit_pids),
                "candidate_rows_sha256": manifest["candidate_rows_sha256"],
                "extraction_pid_sha256": manifest["explicit_extraction_pid_sequence_sha256"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
