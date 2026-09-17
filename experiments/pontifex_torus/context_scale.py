# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Test local-to-global context transfer across embedding spaces.

Hypotheses:
- responses to occlusion at short context are easier/more stable than full-context responses;
- short-context observations in one or more spaces improve prediction of a richer
  outer-space full-context response;
- therefore context scale can act as a second semantic lens.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

from run import ENCODER_A, ENCODER_B, SIZES, make_texts, mask_tokens

CONTEXTS = (8, 12, 10_000)  # last means full available text


def cos_dist(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / np.clip(np.linalg.norm(a, axis=1, keepdims=True), 1e-12, None)
    b = b / np.clip(np.linalg.norm(b, axis=1, keepdims=True), 1e-12, None)
    return 1.0 - np.sum(a * b, axis=1)


def crop(tokens: list[str], center: int, width: int) -> tuple[list[str], int]:
    if width >= len(tokens):
        return tokens, center
    half = width // 2
    lo = max(0, min(center - half, len(tokens) - width))
    hi = min(len(tokens), lo + width)
    return tokens[lo:hi], center - lo


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=80)
    ap.add_argument("--positions", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-context-scale.json"))
    args = ap.parse_args()

    texts = make_texts(args.texts, args.seed)
    rng = np.random.default_rng(args.seed)
    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)

    original_inputs: list[str] = []
    masked_inputs: list[str] = []
    meta: list[tuple[int, int, int, int, float]] = []
    # meta: text_id, position, occlusion_size, context_width, normalized position
    for tid, text in enumerate(texts):
        toks = text.split()
        max_start = max(1, len(toks) - 1)
        if args.positions >= max_start:
            starts = np.arange(max_start)
        else:
            starts = np.sort(rng.choice(max_start, size=args.positions, replace=False))
        for start in starts:
            for size in SIZES:
                for ctx in CONTEXTS:
                    local, local_start = crop(toks, int(start), int(ctx))
                    original_inputs.append(" ".join(local))
                    masked_inputs.append(mask_tokens(local, local_start, int(size)))
                    meta.append((tid, int(start), int(size), int(ctx), float(start) / max(1, len(toks) - 1)))

    a0 = model_a.encode(original_inputs, batch_size=128, convert_to_numpy=True)
    a1 = model_a.encode(masked_inputs, batch_size=128, convert_to_numpy=True)
    b0 = model_b.encode(original_inputs, batch_size=128, convert_to_numpy=True)
    b1 = model_b.encode(masked_inputs, batch_size=128, convert_to_numpy=True)
    ra = cos_dist(a0, a1)
    rb = cos_dist(b0, b1)

    grouped: dict[tuple[int, int, int], dict[int, tuple[float, float, float]]] = {}
    for m, av, bv in zip(meta, ra, rb):
        tid, pos, size, ctx, normpos = m
        grouped.setdefault((tid, pos, size), {})[ctx] = (float(av), float(bv), normpos)

    rows: list[dict[str, float | int]] = []
    for (tid, pos, size), vals in grouped.items():
        if not all(c in vals for c in CONTEXTS):
            continue
        a8, b8, p = vals[8]
        a12, b12, _ = vals[12]
        af, bf, _ = vals[10_000]
        rows.append({
            "tid": tid, "pos": pos, "size": size, "p": p,
            "a8": a8, "b8": b8, "a12": a12, "b12": b12,
            "afull": af, "bfull": bf,
        })

    ids = np.arange(args.texts)
    rng.shuffle(ids)
    cut = max(2, int(0.7 * len(ids)))
    train_ids = set(map(int, ids[:cut]))
    train = [r for r in rows if int(r["tid"]) in train_ids]
    test = [r for r in rows if int(r["tid"]) not in train_ids]

    def matrix(rs, names):
        cols = []
        for r in rs:
            row = []
            for n in names:
                if n == "log_size":
                    row.append(float(np.log2(int(r["size"]))))
                else:
                    row.append(float(r[n]))
            cols.append(row)
        return np.asarray(cols, dtype=float)

    ytr = matrix(train, ["bfull"]).ravel()
    yte = matrix(test, ["bfull"]).ravel()
    conditions = {
        # What can A say about B at full context without local observations?
        "A_full_only": ["afull", "p", "log_size"],
        # Does A's local-to-global trajectory help predict B full context?
        "A_local_to_global": ["a8", "a12", "afull", "p", "log_size"],
        # Stronger shared-world hypothesis: B local observations help predict B full.
        "B_local_to_global": ["b8", "b12", "p", "log_size"],
        # Cross-space local observations together predict B full.
        "cross_space_local": ["a8", "a12", "b8", "b12", "afull", "p", "log_size"],
    }
    metrics = {}
    for name, cols in conditions.items():
        model = Ridge(alpha=1.0).fit(matrix(train, cols), ytr)
        pred = model.predict(matrix(test, cols))
        metrics[name] = {"rmse": float(mean_squared_error(yte, pred) ** 0.5)}

    result = {
        "experiment": "Pontifex context lens v0",
        "encoders": {"A": ENCODER_A, "B": ENCODER_B},
        "context_widths": [8, 12, "full"],
        "occlusion_sizes": list(SIZES),
        "rows": len(rows),
        "train_rows": len(train),
        "test_rows": len(test),
        "metrics": metrics,
        "derived": {
            "A_local_gain": metrics["A_full_only"]["rmse"] - metrics["A_local_to_global"]["rmse"],
            "cross_space_local_gain": metrics["A_full_only"]["rmse"] - metrics["cross_space_local"]["rmse"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
