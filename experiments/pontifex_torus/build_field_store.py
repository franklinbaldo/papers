# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Build/load a reusable Pontifex Torus response field.

The expensive operation is encoding original/masked texts in MiniLM and BGE.
Persist the resulting scalar response field as a compact NPZ so downstream
experiments can run without loading model weights at all.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ENCODER_A = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_B = "BAAI/bge-small-en-v1.5"
SIZES = (1, 2, 4, 8)

SUBJECTS = ["The doctor", "The teacher", "The pilot", "The engineer", "The farmer", "The lawyer", "The scientist", "The artist", "The nurse", "The baker"]
VERBS = ["confirmed", "rejected", "explained", "measured", "reported", "observed", "questioned", "revised", "compared", "verified"]
OBJECTS = ["the unusual result", "the final estimate", "the clinical finding", "the legal argument", "the weather pattern", "the test outcome", "the experimental signal", "the historical claim", "the design choice", "the safety concern"]
TAILS = ["after reviewing the evidence carefully", "before the meeting ended", "because the earlier report was incomplete", "while the rest of the team watched", "despite the initial uncertainty", "after comparing several independent sources"]


def make_texts(n: int, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    out, seen = [], set()
    while len(out) < n:
        text = f"{rng.choice(SUBJECTS)} {rng.choice(VERBS)} {rng.choice(OBJECTS)} {rng.choice(TAILS)}."
        if text not in seen:
            seen.add(text)
            out.append(text)
    return out


def mask_tokens(tokens: list[str], start: int, size: int) -> str:
    end = min(len(tokens), start + size)
    return " ".join(tokens[:start] + ["[MASK]"] * (end - start) + tokens[end:])


def cos_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / np.clip(np.linalg.norm(a, axis=1, keepdims=True), 1e-12, None)
    b = b / np.clip(np.linalg.norm(b, axis=1, keepdims=True), 1e-12, None)
    return 1.0 - np.sum(a * b, axis=1)


def build_arrays(texts: int, positions: int, seed: int):
    corpus = make_texts(texts, seed)
    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)
    originals_a = model_a.encode(corpus, batch_size=64, convert_to_numpy=True)
    originals_b = model_b.encode(corpus, batch_size=64, convert_to_numpy=True)

    masked, meta = [], []
    rng = np.random.default_rng(seed)
    for text_id, text in enumerate(corpus):
        toks = text.split()
        max_start = max(1, len(toks) - 1)
        starts = np.arange(max_start) if positions >= max_start else np.sort(rng.choice(max_start, size=positions, replace=False))
        for start in starts:
            pos = float(start) / max(1, len(toks) - 1)
            for size in SIZES:
                masked.append(mask_tokens(toks, int(start), int(size)))
                meta.append((text_id, pos, int(size)))

    masked_a = model_a.encode(masked, batch_size=128, convert_to_numpy=True)
    masked_b = model_b.encode(masked, batch_size=128, convert_to_numpy=True)
    orig_a = np.stack([originals_a[t] for t, _, _ in meta])
    orig_b = np.stack([originals_b[t] for t, _, _ in meta])
    da = cos_distance(orig_a, masked_a)
    db = cos_distance(orig_b, masked_b)

    return {
        "text_id": np.asarray([m[0] for m in meta], dtype=np.int32),
        "pos": np.asarray([m[1] for m in meta], dtype=np.float64),
        "size": np.asarray([m[2] for m in meta], dtype=np.int16),
        "response_a": da.astype(np.float64),
        "response_b": db.astype(np.float64),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, required=True)
    ap.add_argument("--positions", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    arrays = build_arrays(args.texts, args.positions, args.seed)
    meta = {
        "texts": args.texts,
        "positions": args.positions,
        "seed": args.seed,
        "encoders": {"A": ENCODER_A, "B": ENCODER_B},
        "sizes": list(SIZES),
        "rows": int(len(arrays["text_id"])),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **arrays, metadata=np.asarray(json.dumps(meta)))
    print(json.dumps({"field_store": str(args.output), **meta}, indent=2))


if __name__ == "__main__":
    main()
