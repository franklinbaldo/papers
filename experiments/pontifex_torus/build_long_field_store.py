# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Build a longer-input Pontifex response field without perturbing existing caches.

This uses the same MiniLM/BGE response definition as build_field_store.py, but each
synthetic text concatenates several independently sampled clauses. The purpose is
not to claim realistic long-context semantics; it is to keep K=4..24 genuinely
sparse while testing whether interaction-topology evidence changes as acquisition
error falls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from build_field_store import ENCODER_A, ENCODER_B, OBJECTS, SUBJECTS, TAILS, VERBS, cos_distance, mask_tokens

CONNECTORS = ["Then", "Meanwhile", "Afterward", "Separately", "Later", "In parallel"]


def make_long_texts(n: int, seed: int, clauses: int) -> list[str]:
    if clauses < 2:
        raise ValueError("--clauses must be >= 2; use build_field_store.py for the original one-clause corpus")
    rng = np.random.default_rng(seed)
    out: list[str] = []
    seen: set[str] = set()
    while len(out) < n:
        parts = []
        for c in range(clauses):
            sentence = f"{rng.choice(SUBJECTS)} {rng.choice(VERBS)} {rng.choice(OBJECTS)} {rng.choice(TAILS)}."
            if c:
                sentence = f"{rng.choice(CONNECTORS)}, {sentence[0].lower()}{sentence[1:]}"
            parts.append(sentence)
        text = " ".join(parts)
        if text not in seen:
            seen.add(text)
            out.append(text)
    return out


def build_arrays(texts: int, positions: int, seed: int, clauses: int):
    corpus = make_long_texts(texts, seed, clauses)
    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)
    originals_a = model_a.encode(corpus, batch_size=64, convert_to_numpy=True)
    originals_b = model_b.encode(corpus, batch_size=64, convert_to_numpy=True)

    masked: list[str] = []
    meta: list[tuple[int, float, int]] = []
    token_counts: list[int] = []
    rng = np.random.default_rng(seed)
    for text_id, text in enumerate(corpus):
        toks = text.split()
        token_counts.append(len(toks))
        max_start = max(1, len(toks) - 1)
        starts = np.arange(max_start) if positions >= max_start else np.sort(
            rng.choice(max_start, size=positions, replace=False)
        )
        for start in starts:
            pos = float(start) / max(1, len(toks) - 1)
            masked.append(mask_tokens(toks, int(start), 1))
            meta.append((text_id, pos, 1))

    masked_a = model_a.encode(masked, batch_size=128, convert_to_numpy=True)
    masked_b = model_b.encode(masked, batch_size=128, convert_to_numpy=True)
    orig_a = np.stack([originals_a[t] for t, _, _ in meta])
    orig_b = np.stack([originals_b[t] for t, _, _ in meta])

    return {
        "text_id": np.asarray([m[0] for m in meta], dtype=np.int32),
        "original_a": originals_a.astype(np.float32),
        "original_b": originals_b.astype(np.float32),
        "pos": np.asarray([m[1] for m in meta], dtype=np.float64),
        "size": np.ones(len(meta), dtype=np.int16),
        "response_a": cos_distance(orig_a, masked_a).astype(np.float64),
        "response_b": cos_distance(orig_b, masked_b).astype(np.float64),
        "token_count": np.asarray(token_counts, dtype=np.int16),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, required=True)
    ap.add_argument("--positions", type=int, required=True)
    ap.add_argument("--clauses", type=int, default=4)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    arrays = build_arrays(args.texts, args.positions, args.seed, args.clauses)
    counts = arrays["token_count"].astype(float)
    meta = {
        "texts": int(args.texts),
        "positions_requested": int(args.positions),
        "clauses_per_text": int(args.clauses),
        "seed": int(args.seed),
        "encoders": {"A": ENCODER_A, "B": ENCODER_B},
        "sizes": [1],
        "rows": int(len(arrays["text_id"])),
        "token_count_mean": float(np.mean(counts)),
        "token_count_min": int(np.min(counts)),
        "token_count_max": int(np.max(counts)),
        "purpose": "longer synthetic acquisition/topology diagnostic; not future assembly/student benchmark data",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **arrays, metadata=np.asarray(json.dumps(meta)))
    print(json.dumps({"field_store": str(args.output), **meta}, indent=2))


if __name__ == "__main__":
    main()
