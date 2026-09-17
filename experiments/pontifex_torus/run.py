# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex Torus v0: occlusion-lens and local-to-global mapping toy.

Cheap tests, before MaleCNS:
H1. Occlusion size helps predict a second semantic response surface.
H2. Periodic local interactions improve over a size-agnostic map.
H3. The map interpolates an unseen occlusion size (train 1/2/8, test 4).
H4. Useful cross-space structure appears before exhaustive traversal.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import NearestNeighbors

ENCODER_A = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_B = "BAAI/bge-small-en-v1.5"
SIZES = (1, 2, 4, 8)

SUBJECTS = ["The doctor", "The teacher", "The pilot", "The engineer", "The farmer", "The lawyer", "The scientist", "The artist", "The nurse", "The baker"]
VERBS = ["confirmed", "rejected", "explained", "measured", "reported", "observed", "questioned", "revised", "compared", "verified"]
OBJECTS = ["the unusual result", "the final estimate", "the clinical finding", "the legal argument", "the weather pattern", "the test outcome", "the experimental signal", "the historical claim", "the design choice", "the safety concern"]
TAILS = ["after reviewing the evidence carefully", "before the meeting ended", "because the earlier report was incomplete", "while the rest of the team watched", "despite the initial uncertainty", "after comparing several independent sources"]


@dataclass
class Row:
    text_id: int
    pos: float
    size: int
    response_a: float
    response_b: float


def make_texts(n: int, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    out: list[str] = []
    seen: set[str] = set()
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


def build_rows(texts: list[str], positions_per_text: int, seed: int) -> list[Row]:
    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)
    originals_a = model_a.encode(texts, batch_size=64, convert_to_numpy=True)
    originals_b = model_b.encode(texts, batch_size=64, convert_to_numpy=True)

    masked: list[str] = []
    meta: list[tuple[int, float, int]] = []
    rng = np.random.default_rng(seed)
    for text_id, text in enumerate(texts):
        toks = text.split()
        max_start = max(1, len(toks) - 1)
        starts = np.arange(max_start) if positions_per_text >= max_start else np.sort(rng.choice(max_start, size=positions_per_text, replace=False))
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
    return [Row(t, p, s, float(a), float(b)) for (t, p, s), a, b in zip(meta, da, db)]


def load_rows(path: Path) -> list[Row]:
    data = np.load(path, allow_pickle=False)
    return [
        Row(int(t), float(p), int(s), float(a), float(b))
        for t, p, s, a, b in zip(
            data["text_id"],
            data["pos"],
            data["size"],
            data["response_a"],
            data["response_b"],
        )
    ]


def features(rows: list[Row], mode: str) -> np.ndarray:
    out: list[list[float]] = []
    for r in rows:
        theta = 2.0 * math.pi * r.pos
        row = [r.response_a, math.sin(theta), math.cos(theta)]
        if mode in {"lens", "torus"}:
            l = math.log2(r.size)
            row += [l, l * l]
        if mode == "torus":
            l = math.log2(r.size)
            row += [r.response_a * math.sin(theta), r.response_a * math.cos(theta), r.response_a * l, math.sin(2 * theta), math.cos(2 * theta)]
        out.append(row)
    return np.asarray(out, dtype=float)


def neighborhood_overlap(y_true: np.ndarray, y_pred: np.ndarray, rows: list[Row], requested_k: int = 5) -> float:
    """Compare local ordering per text; adapt k so small slices stay defined."""
    by_text: dict[int, list[int]] = {}
    for i, row in enumerate(rows):
        by_text.setdefault(row.text_id, []).append(i)
    scores: list[float] = []
    for idxs in by_text.values():
        if len(idxs) < 3:
            continue
        k = min(requested_k, len(idxs) - 1)
        yt = y_true[idxs, None]
        yp = y_pred[idxs, None]
        nn_true = NearestNeighbors(n_neighbors=k + 1).fit(yt).kneighbors(yt, return_distance=False)
        nn_pred = NearestNeighbors(n_neighbors=k + 1).fit(yp).kneighbors(yp, return_distance=False)
        for local_i, (a, b) in enumerate(zip(nn_true, nn_pred)):
            sa = set(int(v) for v in a if int(v) != local_i)
            sb = set(int(v) for v in b if int(v) != local_i)
            sa = set(list(sa)[:k])
            sb = set(list(sb)[:k])
            scores.append(len(sa & sb) / max(1, len(sa | sb)))
    return float(np.mean(scores)) if scores else float("nan")


def fit_eval(train: list[Row], test: list[Row], mode: str) -> dict[str, float]:
    model = Ridge(alpha=1.0)
    xtr = features(train, mode)
    ytr = np.asarray([r.response_b for r in train])
    xte = features(test, mode)
    yte = np.asarray([r.response_b for r in test])
    model.fit(xtr, ytr)
    pred = model.predict(xte)
    return {
        "rmse": float(mean_squared_error(yte, pred) ** 0.5),
        "neighbor_overlap": neighborhood_overlap(yte, pred, test),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=120)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)\n    ap.add_argument("--field-store", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=Path("pontifex-torus.json"))
    args = ap.parse_args()

    rows = load_rows(args.field_store) if args.field_store else build_rows(make_texts(args.texts, args.seed), args.positions, args.seed)
    rng = np.random.default_rng(args.seed)
    ids = np.arange(args.texts)
    rng.shuffle(ids)
    cut = max(2, int(0.7 * len(ids)))
    train_ids = set(map(int, ids[:cut]))
    train = [r for r in rows if r.text_id in train_ids]
    test = [r for r in rows if r.text_id not in train_ids]

    heldout = {m: fit_eval(train, test, m) for m in ("agnostic", "lens", "torus")}
    interp_train = [r for r in train if r.size != 4]
    interp_test = [r for r in test if r.size == 4]
    interpolation = {m: fit_eval(interp_train, interp_test, m) for m in ("agnostic", "lens", "torus")}

    sample_efficiency = {}
    for frac in (0.1, 0.2, 0.4, 0.8, 1.0):
        n = max(20, int(len(train) * frac))
        idx = rng.choice(len(train), size=n, replace=False)
        subset = [train[int(i)] for i in idx]
        sample_efficiency[f"{frac:.1f}"] = {m: fit_eval(subset, test, m) for m in ("agnostic", "lens", "torus")}

    result = {
        "experiment": "Pontifex Torus v0",
        "scope": "No MaleCNS yet; cheap falsification of occlusion-lens and local deformation hypotheses.",
        "encoders": {"inner": ENCODER_A, "outer": ENCODER_B},
        "texts": args.texts,
        "positions_per_text": args.positions,
        "occlusion_sizes": list(SIZES),
        "rows": len(rows),
        "train_texts": len(train_ids),
        "test_texts": args.texts - len(train_ids),
        "heldout_text": heldout,
        "interpolate_unseen_size_4": interpolation,
        "sample_efficiency": sample_efficiency,
        "derived": {
            "lens_gain_rmse": heldout["agnostic"]["rmse"] - heldout["lens"]["rmse"],
            "torus_gain_rmse": heldout["agnostic"]["rmse"] - heldout["torus"]["rmse"],
            "torus_interpolation_gain_rmse": interpolation["agnostic"]["rmse"] - interpolation["torus"]["rmse"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
