"""Stage A: encode MultiEURLEX-21 PT documents once with frozen MiniLM/E5.

Writes one parquet table per encoder into ``--output-dir`` plus ``manifest.json``
(provenance fingerprints and timings). Run with a single ``--models`` entry on
different machines to parallelise encoders; the manifest merges as tables land in
the same directory. ``--push-to-hub`` publishes the directory as a versioned
Hugging Face dataset (token from ``--token`` or ``HF_TOKEN``).

``--limit-per-split`` is for engineering benchmarks only: it takes a deterministic
prefix of each official split and marks the cache ``partial``.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from malecns_wifi.telemetry import Telemetry, progress_fields
from malecns_wifi.multieurlex_cache import (
    model_slug,
    DEFAULT_HUB_REPO,
    DEFAULT_MODELS,
    DEFAULT_SPLITS,
    CacheSpec,
    build_cache,
    push_to_hub,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--splits", nargs="+", default=list(DEFAULT_SPLITS))
    parser.add_argument("--max-chunks", type=int, default=4)
    parser.add_argument("--chunk-chars", type=int, default=3000)
    parser.add_argument("--limit-per-split", type=int, default=None)
    parser.add_argument("--push-to-hub", action="store_true")
    parser.add_argument("--hub-repo", default=DEFAULT_HUB_REPO)
    parser.add_argument("--hub-private", action="store_true")
    parser.add_argument("--token", default=None, help="Hugging Face token (defaults to $HF_TOKEN)")
    args = parser.parse_args()

    spec = CacheSpec(
        models=tuple(args.models),
        max_chunks=args.max_chunks,
        chunk_chars=args.chunk_chars,
        splits=tuple(args.splits),
        limit_per_split=args.limit_per_split,
    )
    telemetry = Telemetry("stage-a-semantic-cache", config={
        "models": args.models, "splits": args.splits, "max_chunks": args.max_chunks,
        "chunk_chars": args.chunk_chars, "limit_per_split": args.limit_per_split,
        "device": args.device, "batch_size": args.batch_size,
    })

    def progress(model_name, done, total, started):
        slug = model_slug(model_name)
        telemetry.log({f"{slug}/{k}": v for k, v in progress_fields(done, total, started, "chunks").items()})
        print(json.dumps({"event": "semantic_cache_progress", "model": model_name, "done": done, "total": total}), flush=True)

    manifest = build_cache(spec, output_dir=args.output_dir, device=args.device, batch_size=args.batch_size,
                           progress=progress)
    telemetry.summary({
        "documents": manifest["documents"], "chunks": manifest["chunks"], "bytes": manifest.get("bytes"),
        "fingerprint": manifest.get("fingerprint"),
        **{f"{e['slug']}/encode_seconds": e["encode_seconds"] for e in manifest["encoders"]},
        **{f"{e['slug']}/chunks_per_second": e["chunks_per_second"] for e in manifest["encoders"]},
    })
    print(json.dumps({"event": "multieurlex_semantic_cache_complete", "manifest": manifest}), flush=True)
    if args.push_to_hub:
        if spec.limit_per_split is not None:
            raise SystemExit("refusing to publish a partial (--limit-per-split) cache as the official dataset")
        token = args.token or os.environ.get("HF_TOKEN")
        if not token:
            raise SystemExit("--push-to-hub needs --token or $HF_TOKEN")
        commit = push_to_hub(args.output_dir, repo_id=args.hub_repo, token=token, private=args.hub_private)
        print(json.dumps({"event": "multieurlex_semantic_cache_published", "repo": args.hub_repo, "commit": commit}), flush=True)
        telemetry.summary({"published_repo": args.hub_repo, "published_commit": commit})
    telemetry.finish()


if __name__ == "__main__":
    main()
