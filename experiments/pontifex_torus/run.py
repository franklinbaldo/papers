# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex Torus v0: occlusion-lens and local-to-global mapping toy.

This experiment tests the core geometric hypotheses *without* MaleCNS first:

H1. Occlusion size is useful for localizing/predicting the response surface.
H2. A periodic (torus-like) local map over text position + occlusion scale predicts
    a second embedding space better than a size-agnostic map.
H3. The learned map interpolates an unseen occlusion scale (train 1/2/8, test 4).
H4. The map becomes useful with partial coverage, i.e. does not require exhaustive
    sampling of the response field.

The torus here is represented by periodic Fourier coordinates for normalized text
position (theta) and log occlusion size (phi-like scale coordinate). The learned
ridge model is the first cheap approximation to a smooth deformation field. It is
not yet the embodied / connectome-controlled version.
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

SUBJECTS = [
    "The doctor", "The teacher", "The pilot", "The engineer", "The farmer",
    "The lawyer", "The scientist", "The artist", "The nurse", "The baker",
]
VERBS = [
    "confirmed", "rejected", "explained", "measured", "reported",
    "observed", "questioned", "revised", "compared", "verified",
]
OBJECTS = [
    "the unusual result", "the final estimate", "the clinical finding",
    "the legal argument", "the weather pattern", "the test outcome",
    "the experimental signal", "the historical claim", "the design choice",
    "the safety concern",
]
TAILS = [
    "after reviewing the evidence carefully",
    "before the meeting ended",
    "because the earlier report was incomplete",
    "while the rest of the team watched",
    "despite the initial uncertainty",
    "after comparing several independent sources",
]


def make_texts(n: int, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    out: list[str] = []
    seen: set[str] = set()
    while len(out) < n:
        s = (
            f"{rng.choice(SUBJECTS)} {rng.choice(VERBS)} {rng.choice(OBJECTS)} "
            f"{rng.choice(TAILS)}."
        )
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def mask_tokens(tokens: list[str], start: int, size: int) -> str:
    end = min(len(tokens), start + size)
    masked = tokens[:start] + ["[MASK]"] * (end - start) + tokens[end:]
    return " ".join(masked)


def cos_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / np.clip(np.linalg.norm(a, axis=1, keepdims=True), 1e-12, None)
    b = b / np.clip(np.linalg.norm(b, axis=1, keepdims=True), 1e-12, None)
    return 1.0 - np.sum(a * b, axis=1)


@dataclass
class Row:
    text_id: int
    pos: float
    size: int
    response_a: float
    response_b: float


def build_rows(texts: list[str], positions_per_text: int, seed: int) -> list[Row]:
    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)

    originals_a = model_a.encode(texts, batch_size=64, convert_to_numpy=True, normalize_embeddings=False)
    originals_b = model_b.encode(texts, batch_size=64, convert_to_numpy=True, normalize_embeddings=False)

    masked_texts: list[str] = []
    meta: list[tuple[int, float, int]] = []
    rng = np.random.default_rng(seed)

    for text_id, text in enumerate(texts):
        toks = text.split()
        max_start = max(1, len(toks) - 1)
        if positions_per_text >= max_start:
            starts = np.arange(max_start)
        else:
            starts = np.sort(rng.choice(max_start, size=positions_per_text, replace=False))
        for start in starts:
            pos = float(start) / max(1, len(toks) - 1)
            for size in SIZES:
                masked_texts.append(mask_tokens(toks, int(start), int(size)))
                meta.append((text_id, pos, int(size)))

    masked_a = model_a.encode(masked_texts, batch_size=128, convert_to_numpy=True, normalize_embeddings=False)
    masked_b = model_b.encode(masked_texts, batch_size=128, convert_to_numpy=True, normalize_embeddings=False)

    orig_a = np.stack([originals_a[m[0]] for m in meta])
    orig_b = np.stack([originals_b[m[0]] for m in meta])
    da = cos_distance(orig_a, masked_a)
    db = cos_distance(orig_b, masked_b)

    return [
        Row(text_id=t, pos=p, size=s, response_a=float(a), response_b=float(b))
        for (t, p, s), a, b in zip(meta, da, db)
    ]


def features(rows: list[Row], mode: str) -> np.ndarray:
    x: list[list[float]] = []
    for r in rows:
        theta = 2.0 * math.pi * r.pos
        base = [r.response_a, math.sin(theta), math.cos(theta)]
        if mode in {"lens", "torus"}:
            l = math.log2(r.size)
            base += [l, l * l]
        if mode == "torus":
            # periodic local-deformation basis: response coupled to location + scale
            l = math.log2(r.size)
            base += [
                r.response_a * math.sin(theta),
                r.response_a * math.cos(theta),
                r.response_a * l,
                math.sin(2 * theta),
                math.cos(2 * theta),
            ]
        x.append(base)
    return np.asarray(x, dtype=np.float64)


def rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(mean_squared_error(y, pred) ** 0.5)


def neighborhood_overlap(y_true: np.ndarray, y_pred: np.ndarray, rows: list[Row], k: int = 10) -> float:
    # Compare local ordering within each text using scalar response_B as a 1-D proxy.
    by_text: dict[int, list[int]] = {}
    for i, r in enumerate(rows):
        by_text.setdefault(r.text_id, []).append(i)
    overlaps: list[float] = []
    for idxs in by_text.values():
        if len(idxs) <= k:
            continue
        yt = y_true[idxs, None]
        yp = y_pred[idxs, None]
        kt = min(k + 1, len(idxs))
        n1 = NearestNeighbors(n_neighbors=kt).fit(yt).kneighbors(return_distance=False)
        n2 = NearestNeighbors(n_neighbors=kt).fit(yp).kneighbors(return_distance=False)
        for a, b in zip(n1, n2):
            sa = set(a[1:])
            sb = set(b[1:])
            overlaps.append(len(sa & sb) / max(1, len(sa | sb)))
    return float(np.mean(overlaps)) if overlaps else 0.0


def fit_eval(train: list[Row], test: list[Row], mode: str, alpha: float = 1.0) -> dict[str, float]:
    model = Ridge(alpha=alpha)
    xa = features(train, mode)
    ya = np.asarray([r.response_b for r in train])
    xb = features(test, mode)
    yb = np.asarray([r.response_b for r in test])
    model.fit(xa, ya)
    pred = model.predict(xb)
    return {
        "rmse": rmse(yb, pred),
        "neighbor_overlap": neighborhood_overlap(yb, pred, test),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=120)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-torus.json"))
    args = ap.parse_args()

    texts = make_texts(args.texts, args.seed)
    rows = build_rows(texts, args.positions, args.seed)

    rng = np.random.default_rng(args.seed)
    ids = np.arange(args.texts)
    rng.shuffle(ids)
    n_train = max(2, int(0.7 * len(ids)))
    train_ids = set(map(int, ids[:n_train]))
    test_ids = set(map(int, ids[n_train:]))

    train_all = [r for r in rows if r.text_id in train_ids]
    test_all = [r for r in rows if r.text_id in test_ids]

    # H1/H2: does explicit scale + torus-local interaction improve held-out text prediction?
    heldout_text = {
        mode: fit_eval(train_all, test_all, mode)
        for mode in ("agnostic", "lens", "torus")
    }

    # H3: interpolate unseen size=4 from sizes 1,2,8.
    interp_train = [r for r in train_all if r.size != 4]
    interp_test = [r for r in test_all if r.size == 4]
    interpolate_size4 = {
        mode: fit_eval(interp_train, interp_test, mode)
        for mode in ("agnostic", "lens", "torus")
    }

    # H4: sample efficiency. Keep test fixed, subsample training response-field rows.
    sample_efficiency: dict[str, dict[str, dict[str, float]]] = {}
    for frac in (0.1, 0.2, 0.4, 0.8, 1.0):
        n = max(20, int(len(train_all) * frac))
        idx = rng.choice(len(train_all), size=n, replace=False)
        subset = [train_all[int(i)] for i in idx]
        sample_efficiency[f"{frac:.1f}"] = {
            mode: fit_eval(subset, test_all, mode)
            for mode in ("agnostic", "lens", "torus")
        }

    result = {
        "experiment": "Pontifex Torus v0",
        "scope": "No MaleCNS yet; cheap falsification of occlusion-lens and local deformation hypotheses.",
        "encoders": {"inner": ENCODER_A, "outer": ENCODER_B},
        "texts": args.texts,
        "positions_per_text": args.positions,
        "occlusion_sizes": list(SIZES),
        "rows": len(rows),
        "train_texts": len(train_ids),
        "test_texts": len(test_ids),
        "heldout_text": heldout_text,
        "interpolate_unseen_size_4": interpolate_size4,
        "sample_efficiency": sample_efficiency,
        "derived": {
            "lens_gain_rmse": heldout_text["agnostic"]["rmse"] - heldout_text["lens"]["rmse"],
            "torus_gain_rmse": heldout_text["agnostic"]["rmse"] - heldout_text["torus"]["rmse"],
            "torus_interpolation_gain_rmse": interpolate_size4["agnostic"]["rmse"] - interpolate_size4["torus"]["rmse"],
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
