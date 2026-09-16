"""Stage A: deduplicate and encode Few-NERD's byte-synchronised multiscale windows.

Writes ``sentences.parquet`` (id/split/text/byte-labels) plus, per encoder, a
sorted-key array and a flat float32 file of embeddings for every **unique**
window text across all sentences and scales (see ``fewnerd_cache`` module
docstring for why: naive per-byte persistence would be ~860 GB on the full
corpus; deduplication cuts it to ~20 GB and the unique-window count to ~10% of
occurrences). This cache is a local intermediate, not published.

Run with a single ``--models`` entry per machine to parallelise encoders.
``--limit-per-split`` is for engineering benchmarks only: a deterministic
prefix of each official split, marked ``partial`` in the manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_wifi.fewnerd_cache import (
    DEFAULT_CONFIG,
    DEFAULT_MODELS,
    DEFAULT_SCALES,
    DEFAULT_SPLITS,
    TokenCacheSpec,
    build_cache,
)
from malecns_wifi.telemetry import Telemetry, progress_fields


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", choices=["supervised", "intra", "inter"], default=DEFAULT_CONFIG)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--scales", type=int, nargs="+", default=list(DEFAULT_SCALES))
    parser.add_argument("--splits", nargs="+", default=list(DEFAULT_SPLITS))
    parser.add_argument("--max-tokens", type=int, default=64, help="cap on pre-tokenized WORDS per sentence")
    parser.add_argument("--limit-per-split", type=int, default=None)
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
        telemetry.log({f"{model_name.split('/')[-1]}/{k}": v for k, v in progress_fields(done, total, started, "windows").items()})
        print(json.dumps({"event": "fewnerd_cache_progress", "model": model_name, "done": done, "total": total}), flush=True)

    manifest = build_cache(spec, output_dir=args.output_dir, device=args.device, batch_size=args.batch_size, progress=progress)
    telemetry.summary({
        "sentences": manifest["sentences"], "bytes": manifest["bytes"],
        "unique_windows": manifest["dedup"]["unique_windows"], "total_occurrences": manifest["dedup"]["total_occurrences"],
        "dedup_ratio": manifest["dedup"]["dedup_ratio"], "bytes_on_disk": manifest.get("total_bytes_on_disk"),
        "fingerprint": manifest.get("fingerprint"),
        **{f"{e['slug']}/encode_seconds": e["encode_seconds"] for e in manifest["encoders"]},
        **{f"{e['slug']}/windows_per_second": e["windows_per_second"] for e in manifest["encoders"]},
    })
    telemetry.finish()
    print(json.dumps({"event": "fewnerd_semantic_cache_complete", "manifest": manifest}), flush=True)


if __name__ == "__main__":
    main()
