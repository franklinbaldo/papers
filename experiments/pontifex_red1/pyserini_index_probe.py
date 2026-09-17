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
running the passage encoder?

This script deliberately does not instantiate a query encoder. It only downloads
and opens already-materialized index artifacts.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import faiss
import numpy as np
from pyserini.search.faiss import FaissSearcher
from pyserini.search.lucene import LuceneSearcher

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
    print(
        f"disk_before total={disk_before.total} free={disk_before.free} used={disk_before.used}",
        flush=True,
    )

    # Passing None is explicitly supported by Pyserini docs for opening a prebuilt
    # FAISS artifact when no query inference is needed.
    dense = FaissSearcher.from_prebuilt_index(args.index, None)
    info = describe_index(dense.index)
    print(f"dense index: {info}", flush=True)
    print(f"docids={len(dense.docids)} num_docs={dense.num_docs}", flush=True)

    if dense.num_docs != len(dense.docids):
        raise AssertionError("FAISS vector count and docid mapping length differ")

    sparse = LuceneSearcher.from_prebuilt_index(args.corpus_index)

    samples: list[dict[str, object]] = []
    for pos in args.positions:
        if not 0 <= pos < dense.num_docs:
            raise ValueError(f"position {pos} outside [0, {dense.num_docs})")

        pid = dense.docids[pos]
        vector = dense.index.reconstruct(pos)
        vector = np.asarray(vector, dtype=np.float32)
        if vector.shape != (dense.dimension,):
            raise AssertionError((pos, vector.shape, dense.dimension))
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

    # Strong consistency check for the canonical MS MARCO v1 ordering claim. We
    # report rather than assume it: the artifact itself decides whether pos==pid.
    positional_identity = all(str(s["position"]) == str(s["pid"]) for s in samples)

    disk_after = shutil.disk_usage("/")
    result = {
        "experiment": "Pyserini prebuilt embedding artifact provenance probe",
        "dense_alias": args.index,
        "corpus_alias": args.corpus_index,
        "index": info,
        "docid_count": len(dense.docids),
        "positional_identity_on_samples": positional_identity,
        "samples": samples,
        "disk": {
            "before_free": disk_before.free,
            "after_free": disk_after.free,
            "consumed": disk_before.free - disk_after.free,
        },
        "conclusion": (
            "CHAIN_VERIFIED" if samples and all(s["passage_preview"] for s in samples) else "INCOMPLETE"
        ),
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
        f"- docid mapping rows: **{len(dense.docids):,}**",
        f"- sampled `position == pid`: **{positional_identity}**",
        f"- conclusion: **{result['conclusion']}**",
        "",
        "| internal position | external pid | shape | norm | passage preview |",
        "|---:|---:|---:|---:|---|",
    ]
    for s in samples:
        preview = str(s["passage_preview"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {s['position']} | {s['pid']} | {s['vector_shape']} | {s['vector_norm']:.4f} | {preview} |"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
