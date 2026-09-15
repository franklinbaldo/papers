"""Pinned-dataset entrypoint for the full-whole-brain Few-NERD NER smoke."""
from __future__ import annotations

import datasets

import fewnerd_malecns_ner_smoke as runner
from fewnerd_semantic_cache_pinned import DATASET_REVISION, MODEL_REVISIONS

_real_load_dataset = datasets.load_dataset


def _pinned_load_dataset(path, *args, **kwargs):
    if path == "DFKI-SLT/few-nerd":
        kwargs["revision"] = DATASET_REVISION
    return _real_load_dataset(path, *args, **kwargs)


def main() -> None:
    runner.load_dataset = _pinned_load_dataset
    original = runner._load_cache

    def checked_cache(path):
        manifest, arrays = original(path)
        if manifest.get("dataset_revision") != DATASET_REVISION:
            raise RuntimeError("cache is not pinned to the registered Few-NERD revision")
        if manifest.get("model_revisions") != MODEL_REVISIONS:
            raise RuntimeError("cache semantic model revisions do not match registered pins")
        if not manifest.get("reproducible_pins"):
            raise RuntimeError("cache lacks reproducible pin invariant")
        return manifest, arrays

    runner._load_cache = checked_cache
    runner.main()


if __name__ == "__main__":
    main()
