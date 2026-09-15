"""Run the official MTEB MultiEURLEX-21 Portuguese task on frozen MaleCNS.

`--smoke` is pipeline validation only and deliberately truncates official splits.
Without `--smoke`, the task's own MTEB evaluator and official Portuguese splits
are used unchanged.

Two encoder sources:

* live (default): frozen MiniLM/E5 + MaleCNS computed per MTEB batch;
* `--document-embeddings <stage-B npz>`: precomputed label-free document
  embeddings served by text hash (stage C of the staged pipeline). The evaluator,
  splits and metrics are identical; only where the embedding comes from changes.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from typing import Any

import numpy as np

from malecns_mteb_encoder import CachedDocumentEncoder, FrozenMaleCNSEncoder, MaleCNSEncoderConfig

TASK_NAME = "MultiEURLEXMultilabelClassification"
HF_SUBSET = "pt"
EXPECTED_DATASET_REVISION = "2aea5a6dc8fdcfeca41d0fb963c0a338930bde5c"


def _jsonable(value: Any):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump())
    return value


def _trim_for_smoke(task, *, train_cap: int, test_cap: int) -> dict[str, int]:
    task.load_data()
    subset = task.dataset[HF_SUBSET]
    train_n = min(train_cap, len(subset[task.train_split]))
    test_n = min(test_cap, len(subset["test"]))
    subset[task.train_split] = subset[task.train_split].select(range(train_n))
    subset["test"] = subset["test"].select(range(test_n))
    task.samples_per_label = 2
    task.n_experiments = 1
    return {"train": train_n, "test": test_n}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--document-embeddings", type=Path, help="stage-B npz; skips live encoding")
    parser.add_argument("--readout-width", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-chunks", type=int, default=4)
    parser.add_argument("--chunk-chars", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--backend", choices=["canonical", "fast"], default="canonical")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--smoke-train-cap", type=int, default=5000)
    parser.add_argument("--smoke-test-cap", type=int, default=96)
    args = parser.parse_args()
    if args.document_embeddings is None and args.graph is None:
        parser.error("--graph is required unless --document-embeddings is given")

    import mteb
    import torch

    task = mteb.get_task(
        TASK_NAME,
        hf_subsets=[HF_SUBSET],
        eval_splits=["test"],
    )
    revision = task.metadata.dataset.get("revision") if isinstance(task.metadata.dataset, dict) else None
    if revision != EXPECTED_DATASET_REVISION:
        raise RuntimeError(
            f"unexpected MultiEURLEX MTEB revision: {revision}; expected {EXPECTED_DATASET_REVISION}"
        )

    smoke_counts = None
    if args.smoke:
        smoke_counts = _trim_for_smoke(
            task,
            train_cap=args.smoke_train_cap,
            test_cap=args.smoke_test_cap,
        )

    if args.document_embeddings is not None:
        encoder = CachedDocumentEncoder(args.document_embeddings)
        stage_b = encoder.manifest
        encoder_payload = {
            "name": f"Cached-{stage_b.get('variant', 'unknown')}",
            "source": "stage-B document embeddings",
            "document_embeddings": args.document_embeddings.name,
            "stage_b_manifest": _jsonable(stage_b),
            "stats": _jsonable(encoder.stats),
            "uses_benchmark_labels_inside_encoder": False,
        }
    else:
        encoder = FrozenMaleCNSEncoder(MaleCNSEncoderConfig(
            graph=args.graph,
            readout_width=args.readout_width,
            seed=args.seed,
            max_chunks=args.max_chunks,
            chunk_chars=args.chunk_chars,
            batch_size=args.batch_size,
            backend=args.backend,
            device=args.device,
        ))
        encoder_payload = {
            "name": "FrozenMaleCNS-MiniLM-E5",
            "source": "live",
            "models": list(encoder.config.models),
            "readout_width": encoder.config.readout_width,
            "max_chunks": encoder.config.max_chunks,
            "chunk_chars": encoder.config.chunk_chars,
            "seed": encoder.config.seed,
            "backend": encoder.config.backend,
            "uses_benchmark_labels_inside_encoder": False,
        }

    started = time.perf_counter()
    scores = task.evaluate(
        encoder,
        split="test",
        subsets_to_run=[HF_SUBSET],
        encode_kwargs={"batch_size": args.batch_size},
        prediction_folder=args.predictions,
    )
    elapsed = time.perf_counter() - started
    encoder_payload["stats"] = _jsonable(encoder.stats)

    cuda = torch.cuda.is_available()
    payload = {
        "schema": "papers/malecns-multieurlex21-pt-mteb-v1",
        "claim_status": "pipeline smoke only" if args.smoke else "official MTEB Portuguese benchmark evidence",
        "task": TASK_NAME,
        "hf_subset": HF_SUBSET,
        "language": "por-Latn",
        "dataset": {
            "path": "mteb/eurlex-multilingual",
            "revision": revision,
            "official_splits_preserved": not args.smoke,
            "smoke_counts": smoke_counts,
        },
        "mteb": {
            "version": getattr(mteb, "__version__", None),
            "main_score": task.metadata.main_score,
            "samples_per_label": task.samples_per_label,
            "n_experiments": task.n_experiments,
            "scores": _jsonable(scores),
        },
        "encoder": encoder_payload,
        "runtime": {
            "seconds": elapsed,
            "python": platform.python_version(),
            "torch": torch.__version__,
            "cuda_device": torch.cuda.get_device_name(0) if cuda else None,
            "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()) if cuda else None,
        },
        "comparability": {
            "direct_public_mteb_comparison": not args.smoke,
            "reason": (
                "official task/subset/evaluator; frozen encoder; no benchmark-label adaptation"
                if not args.smoke
                else "smoke truncates official splits and is not leaderboard-comparable"
            ),
        },
        "preregistration": "preregistered-multieurlex21-pt-2026-09-15.md",
        "protocol_amendment": "preregistered-multieurlex21-pt-amendment-encoder-protocol-2026-09-15.md",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "multieurlex21_pt_complete",
        "smoke": args.smoke,
        "seconds": elapsed,
        "scores": _jsonable(scores),
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
