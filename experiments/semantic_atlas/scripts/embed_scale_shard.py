from __future__ import annotations

import argparse
import json
from pathlib import Path

from semantic_atlas.scale_embeddings import (
    OBSERVER_SPECS,
    encode_texts,
    load_corpus,
    shard_bounds,
    write_shard,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--observer", choices=sorted(OBSERVER_SPECS), required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    corpus = load_corpus(args.corpus)
    start, end = shard_bounds(len(corpus), args.shard_index, args.shard_count)
    rows = corpus[start:end]
    spec = OBSERVER_SPECS[args.observer]
    raw, token_lengths = encode_texts(spec, [str(row["abstract"]) for row in rows])
    manifest = write_shard(
        output_dir=args.output_dir,
        observer_key=args.observer,
        spec=spec,
        rows=rows,
        global_start=start,
        global_end=end,
        shard_index=args.shard_index,
        shard_count=args.shard_count,
        raw=raw,
        token_lengths=token_lengths,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
