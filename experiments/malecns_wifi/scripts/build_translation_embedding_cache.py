"""Encode one corpus once with two frozen encoders, for A -> B translation.

Defaults to MiniLM (384-d) as space A and E5-base-v2 (768-d) as space B. The two
are independent enough that the map between them is a real translation rather
than a rotation, and both are already in this experiment's stack.

The corpus defaults to the STS-B sentence pool, deduplicated: short, diverse,
public, and small enough that a CPU run is honest about its own scale.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_wifi.translation_pairs import build_cache

DEFAULT_SOURCE = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_TARGET = "intfloat/e5-base-v2"


def load_texts(dataset: str, split: str, limit: int) -> tuple[list[str], list[int], dict]:
    from datasets import load_dataset

    data = load_dataset(dataset, split=split)
    columns = [name for name in ("sentence1", "sentence2", "text", "sentence")
               if name in data.column_names]
    if not columns:
        raise ValueError(f"no text column in {data.column_names!r}")
    # Row index is the group: the two sentences of an STS-B pair are near
    # paraphrases and must never straddle a split. Iteration is row-major so a
    # truncated corpus still contains both members of each pair -- column-major
    # iteration would take only `sentence1` and quietly turn the grouping into a
    # no-op.
    seen: dict[str, int] = {}
    per_column = [data[column] for column in columns]
    for row in range(len(data)):
        for values in per_column:
            text = " ".join(str(values[row]).split())
            if text and text not in seen:
                seen[text] = row
    items = list(seen.items())[:limit]
    texts = [text for text, _ in items]
    groups = [group for _, group in items]
    return texts, groups, {
        "dataset": dataset,
        "split": split,
        "columns_used": columns,
        "deduplicated": True,
        "available_unique_texts": len(seen),
        "kept": len(texts),
        "group_key": "source row index; both sentences of a pair share it",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="sentence-transformers/stsb")
    parser.add_argument("--split", default="train")
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--source-model", default=DEFAULT_SOURCE)
    parser.add_argument("--target-model", default=DEFAULT_TARGET)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    texts, groups, corpus = load_texts(args.dataset, args.split, args.limit)
    manifest = build_cache(
        texts=texts,
        source_model=args.source_model,
        target_model=args.target_model,
        output=args.output,
        corpus=corpus,
        groups=groups,
        device=args.device,
        batch_size=args.batch_size,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
