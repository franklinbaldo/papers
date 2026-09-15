"""Reproducible wrapper around the Few-NERD contextual token cache builder.

Pins the public dataset and both frozen semantic encoders to immutable Hub
commits, verifies that Transformers actually resolved those commits, and folds
the pins into the cache fingerprint.  No NER labels enter either encoder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import datasets
import transformers

import fewnerd_semantic_cache as cache

DATASET_REVISION = "205f3e9c9f3577ea2561d43f2f62dc249ab92d5b"
MODEL_REVISIONS = {
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
    "intfloat/multilingual-e5-small": "614241f622f53c4eeff9890bdc4f31cfecc418b3",
}


def _repro_fingerprint(base: str) -> str:
    payload = {
        "base_fingerprint": base,
        "dataset_revision": DATASET_REVISION,
        "model_revisions": MODEL_REVISIONS,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build(*, split: str, limit: int, output: Path, device: str, batch_size: int, dtype: str) -> dict:
    real_load_dataset = datasets.load_dataset
    real_tokenizer = transformers.AutoTokenizer.from_pretrained
    real_model = transformers.AutoModel.from_pretrained

    def pinned_dataset(path, *args, **kwargs):
        if path == "DFKI-SLT/few-nerd":
            requested = kwargs.get("revision")
            if requested not in (None, DATASET_REVISION):
                raise RuntimeError(f"conflicting Few-NERD revision: {requested}")
            kwargs["revision"] = DATASET_REVISION
        return real_load_dataset(path, *args, **kwargs)

    def pinned_tokenizer(name, *args, **kwargs):
        if name in MODEL_REVISIONS:
            requested = kwargs.get("revision")
            if requested not in (None, MODEL_REVISIONS[name]):
                raise RuntimeError(f"conflicting tokenizer revision for {name}: {requested}")
            kwargs["revision"] = MODEL_REVISIONS[name]
        return real_tokenizer(name, *args, **kwargs)

    def pinned_model(name, *args, **kwargs):
        if name in MODEL_REVISIONS:
            requested = kwargs.get("revision")
            if requested not in (None, MODEL_REVISIONS[name]):
                raise RuntimeError(f"conflicting model revision for {name}: {requested}")
            kwargs["revision"] = MODEL_REVISIONS[name]
        return real_model(name, *args, **kwargs)

    with (
        patch.object(datasets, "load_dataset", side_effect=pinned_dataset),
        patch.object(transformers.AutoTokenizer, "from_pretrained", side_effect=pinned_tokenizer),
        patch.object(transformers.AutoModel, "from_pretrained", side_effect=pinned_model),
    ):
        manifest = cache.build_cache(
            split=split,
            limit=limit,
            output=output,
            models=tuple(MODEL_REVISIONS),
            device=device,
            batch_size=batch_size,
            dtype=dtype,
        )

    resolved = {row["name"]: row.get("revision") for row in manifest["models"]}
    for name, revision in MODEL_REVISIONS.items():
        if resolved.get(name) != revision:
            raise RuntimeError(
                f"revision invariant failed for {name}: expected {revision}, got {resolved.get(name)}"
            )

    manifest["dataset_revision"] = DATASET_REVISION
    manifest["model_revisions"] = dict(MODEL_REVISIONS)
    manifest["base_fingerprint"] = manifest["fingerprint"]
    manifest["fingerprint"] = _repro_fingerprint(manifest["base_fingerprint"])
    manifest["reproducible_pins"] = True
    output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", default="train")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--device", default="cuda")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--dtype", choices=("float16", "float32"), default="float16")
    args = p.parse_args()
    manifest = build(
        split=args.split,
        limit=args.limit,
        output=args.output,
        device=args.device,
        batch_size=args.batch_size,
        dtype=args.dtype,
    )
    print(json.dumps({"event": "fewnerd_pinned_cache_ready", **manifest}), flush=True)


if __name__ == "__main__":
    main()
