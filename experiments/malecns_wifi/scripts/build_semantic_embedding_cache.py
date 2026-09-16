"""Precompute frozen MiniLM/E5 semantic fields once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import smoke_concept_flavour_gpu as base
import semantic_embedding_cache as cachelib


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=["openvino", "torch"], default="torch")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--models", nargs="+", default=[
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ])
    parser.add_argument("--scales", type=int, nargs="+", default=[8, 32, 128])
    args = parser.parse_args()
    examples = [base.Example(*row) for row in base.TRAIN_EXAMPLES + base.VAL_EXAMPLES]
    for example in examples:
        example.mask = base._mask_for(example)
    manifest = cachelib.build_cache(
        model_names=args.models,
        examples=examples,
        scales=tuple(args.scales),
        output=args.output,
        backend=args.backend,
        device=args.device,
        batch_size=args.batch_size,
    )
    print(json.dumps({"event": "semantic_embedding_cache_complete", "manifest": manifest}), flush=True)


if __name__ == "__main__":
    main()
