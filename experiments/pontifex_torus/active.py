# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Active cartography for Pontifex Torus.

Compare random observation of the inner/outer response field with a label-free
geometry-coverage policy. The active policy selects intervention points that are
far from the already observed points in torus feature space; it never looks at the
outer-space target response before selecting a point.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

from run import build_rows, features, make_texts


def rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(mean_squared_error(y, pred) ** 0.5)


def fit_score(train_rows, test_rows) -> float:
    model = Ridge(alpha=1.0)
    x_train = features(train_rows, "torus")
    y_train = np.asarray([r.response_b for r in train_rows])
    x_test = features(test_rows, "torus")
    y_test = np.asarray([r.response_b for r in test_rows])
    model.fit(x_train, y_train)
    return rmse(y_test, model.predict(x_test))


def kcenter_indices(x: np.ndarray, budget: int) -> np.ndarray:
    """Greedy farthest-point coverage, using only observable/source geometry."""
    budget = min(budget, len(x))
    if budget <= 0:
        return np.asarray([], dtype=int)
    xs = StandardScaler().fit_transform(x)
    # Deterministic first landmark: point closest to the feature-space centroid.
    center = xs.mean(axis=0)
    first = int(np.argmin(np.sum((xs - center) ** 2, axis=1)))
    chosen = [first]
    min_d2 = np.sum((xs - xs[first]) ** 2, axis=1)
    min_d2[first] = -1.0
    for _ in range(1, budget):
        nxt = int(np.argmax(min_d2))
        chosen.append(nxt)
        d2 = np.sum((xs - xs[nxt]) ** 2, axis=1)
        min_d2 = np.minimum(min_d2, d2)
        min_d2[chosen] = -1.0
    return np.asarray(chosen, dtype=int)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=100)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--random-repeats", type=int, default=8)
    ap.add_argument("--output", type=Path, default=Path("pontifex-active.json"))
    args = ap.parse_args()

    texts = make_texts(args.texts, args.seed)
    rows = build_rows(texts, args.positions, args.seed)
    rng = np.random.default_rng(args.seed)
    ids = np.arange(args.texts)
    rng.shuffle(ids)
    cut = max(2, int(0.7 * len(ids)))
    train_ids = set(map(int, ids[:cut]))
    test_ids = set(map(int, ids[cut:]))
    train = [r for r in rows if r.text_id in train_ids]
    test = [r for r in rows if r.text_id in test_ids]

    x_observable = features(train, "torus")
    results: dict[str, object] = {}
    for frac in (0.05, 0.10, 0.20, 0.40):
        budget = max(20, int(len(train) * frac))
        active_idx = kcenter_indices(x_observable, budget)
        active_rmse = fit_score([train[int(i)] for i in active_idx], test)

        random_scores: list[float] = []
        for rep in range(args.random_repeats):
            rrng = np.random.default_rng(args.seed + 1000 + rep)
            ridx = rrng.choice(len(train), size=budget, replace=False)
            random_scores.append(fit_score([train[int(i)] for i in ridx], test))

        results[f"{frac:.2f}"] = {
            "budget": budget,
            "active_kcenter_rmse": active_rmse,
            "random_rmse_mean": float(np.mean(random_scores)),
            "random_rmse_std": float(np.std(random_scores)),
            "gain_vs_random": float(np.mean(random_scores) - active_rmse),
        }

    full_rmse = fit_score(train, test)
    result = {
        "experiment": "Pontifex Torus active cartography v0",
        "selection_contract": "k-center uses only inner-space response + intervention coordinates; no outer target is observed during selection",
        "texts": args.texts,
        "rows": len(rows),
        "train_rows": len(train),
        "test_rows": len(test),
        "full_torus_rmse": full_rmse,
        "budgets": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
