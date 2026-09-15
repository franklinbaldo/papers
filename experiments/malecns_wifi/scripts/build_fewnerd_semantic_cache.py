"""Stage A: encode Few-NERD once as frozen, byte-synchronised multiscale channels.

Writes one parquet table per encoder into ``--output-dir`` plus ``manifest.json``.
Run with a single ``--models`` entry per machine to parallelise encoders.
``--limit-per-split`` is for engineering benchmarks only: a deterministic
prefix of each official split, marked ``partial`` in the manifest.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from malecns_wifi.fewnerd_cache import (
    DEFAULT_CONFIG,
    DEFAULT_HUB_REPO,
    DEFAULT_MODELS,
    DEFAULT_SCALES,
    DEFAULT_SPLITS,
    TokenCacheSpec,
    build_cache,
    push_to_hub,
)
from malecns_wifi.telemetry import Telemetry, progress_fields


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", choices=["supervised", "intra", "inter"], default=DEFAULT_CONFIG)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--scales", type=int, nargs="+", default=list(DEFAULT_SCALES))
    parser.add_argument("--splits", nargs="+", default=list(DEFAULT_SPLITS))
    parser.add_argument("--max-tokens", type=int, default=64, help="cap on pre-tokenized WORDS per sentence")
    parser.add_argument("--limit-per-split", type=int, default=None)
    parser.add_argument("--push-to-hub", action="store_true")
    parser.add_argument("--hub-repo", default=DEFAULT_HUB_REPO)
    parser.add_argument("--hub-private", action="store_true")
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    spec = TokenCacheSpec(
        config=args.config, models=tuple(args.models), scales=tuple(args.scales), splits=tuple(args.splits),
        limit_per_split=args.limit_per_split, max_tokens=args.max_tokens,
    )
    telemetry = Telemetry("stage-a-fewnerd-cache", config={
        "config": args.config, "models": args.models, "scales": args.scales, "splits": args.splits,
        "max_tokens": args.max_tokens, "limit_per_split": args.limit_per_split,
        "device": args.device, "batch_size": args.batch_size,
    })

    def progress(model_name, done, total, started):
        telemetry.log({f"{model_name.split('/')[-1]}/{k}": v for k, v in progress_fields(done, total, started, "bytes").items()})
        print(json.dumps({"event": "fewnerd_cache_progress", "model": model_name, "done": done, "total": total}), flush=True)

    manifest = build_cache(spec, output_dir=args.output_dir, device=args.device, batch_size=args.batch_size, progress=progress)
    telemetry.summary({
        "sentences": manifest["sentences"], "bytes": manifest["bytes"], "bytes_on_disk": manifest.get("total_bytes_on_disk"),
        "fingerprint": manifest.get("fingerprint"),
        **{f"{e['slug']}/encode_seconds": e["encode_seconds"] for e in manifest["encoders"]},
        **{f"{e['slug']}/bytes_per_second": e["bytes_per_second"] for e in manifest["encoders"]},
    })
    print(json.dumps({"event": "fewnerd_semantic_cache_complete", "manifest": manifest}), flush=True)
    if args.push_to_hub:
        if spec.limit_per_split is not None:
            raise SystemExit("refusing to publish a partial (--limit-per-split) cache as the official dataset")
        token = args.token or os.environ.get("HF_TOKEN")
        if not token:
            raise SystemExit("--push-to-hub needs --token or $HF_TOKEN")
        commit = push_to_hub(args.output_dir, repo_id=args.hub_repo, token=token, private=args.hub_private)
        print(json.dumps({"event": "fewnerd_semantic_cache_published", "repo": args.hub_repo, "commit": commit}), flush=True)
        telemetry.summary({"published_repo": args.hub_repo, "published_commit": commit})
    telemetry.finish()


if __name__ == "__main__":
    main()
