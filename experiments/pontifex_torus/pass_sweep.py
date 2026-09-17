# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Scale sequential shared-space torus by passes, not by seed count.

Embeddings/response field are built once. For each seed we vary the train/held-out
partition, stream order, and learner initialization, then run independent protocols
with N consecutive passes over each current text before advancing.

Default checkpoints: 1,2,4,8,16,32,64,128,256,500 passes.
Default seeds: 10.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error

from run import build_rows, features, load_rows, make_texts


def rows_for_ids(rows, ids):
    ids = set(map(int, ids))
    return [r for r in rows if r.text_id in ids]


def evaluate(model, rows):
    x = features(rows, "torus")
    y = np.asarray([r.response_b for r in rows], dtype=float)
    pred = model.predict(x)
    return float(mean_squared_error(y, pred) ** 0.5)


def protocol(rows, sequence_ids, heldout_ids, seed, passes):
    model = SGDRegressor(
        loss="squared_error",
        penalty="l2",
        alpha=1e-4,
        learning_rate="constant",
        eta0=0.002,
        fit_intercept=True,
        shuffle=True,
        random_state=seed,
        max_iter=1,
        tol=None,
    )

    heldout = rows_for_ids(rows, heldout_ids)
    seen_ids = []
    state_deltas = []
    prev_coef = None

    for text_id in sequence_ids:
        current = rows_for_ids(rows, [text_id])
        x = features(current, "torus")
        y = np.asarray([r.response_b for r in current], dtype=float)

        for _ in range(passes):
            model.partial_fit(x, y)

        seen_ids.append(int(text_id))
        coef = model.coef_.copy()
        state_deltas.append(
            float(np.linalg.norm(coef - prev_coef))
            if prev_coef is not None
            else float(np.linalg.norm(coef))
        )
        prev_coef = coef

    seen = rows_for_ids(rows, seen_ids)
    return {
        "passes_per_text": passes,
        "seen_rmse": evaluate(model, seen),
        "heldout_rmse": evaluate(model, heldout),
        "mean_state_delta_l2": float(np.mean(state_deltas)),
        "late_state_delta_l2": float(np.mean(state_deltas[-10:])),
    }


def summarize(records, checkpoints):
    by_pass = {}
    baseline = {}
    for rec in records:
        p = rec["passes_per_text"]
        by_pass.setdefault(p, []).append(rec["heldout_rmse"])
        if p == 1:
            baseline[rec["seed"]] = rec["heldout_rmse"]

    summary = {}
    for p in checkpoints:
        vals = np.asarray(by_pass[p], dtype=float)
        deltas = np.asarray(
            [
                rec["heldout_rmse"] - baseline[rec["seed"]]
                for rec in records
                if rec["passes_per_text"] == p
            ],
            dtype=float,
        )
        summary[str(p)] = {
            "mean_heldout_rmse": float(vals.mean()),
            "std_heldout_rmse": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            "median_heldout_rmse": float(np.median(vals)),
            "mean_delta_vs_1_pass": float(deltas.mean()),
            "median_delta_vs_1_pass": float(np.median(deltas)),
            "fraction_better_than_1_pass": float(np.mean(deltas < 0)),
            "min_heldout_rmse": float(vals.min()),
            "max_heldout_rmse": float(vals.max()),
        }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=120)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--field-seed", type=int, default=17)\n    ap.add_argument("--field-store", type=Path, default=None)
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument(
        "--passes",
        type=int,
        nargs="+",
        default=[1, 2, 4, 8, 16, 32, 64, 128, 256, 500],
    )
    ap.add_argument("--heldout-frac", type=float, default=0.25)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-torus-pass-sweep.json"),
    )
    args = ap.parse_args()

    texts = make_texts(args.texts, args.field_seed)
    rows = load_rows(args.field_store) if args.field_store else build_rows(texts, args.positions, args.field_seed)

    records = []
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        ids = np.arange(args.texts)
        rng.shuffle(ids)
        n_hold = max(4, int(round(args.texts * args.heldout_frac)))
        heldout_ids = list(map(int, ids[:n_hold]))
        sequence_ids = list(map(int, ids[n_hold:]))

        for passes in args.passes:
            rec = protocol(rows, sequence_ids, heldout_ids, seed, passes)
            rec["seed"] = int(seed)
            records.append(rec)

    result = {
        "experiment": "Pontifex Torus pass-count sweep",
        "scope": (
            "Shared torus map; different texts in sequence; no reset. "
            "Manipulated variable is repeated forward passes over each current text. "
            "No optical/cavity interpretation."
        ),
        "texts": args.texts,
        "positions_per_text": args.positions,
        "field_seed": args.field_seed,
        "seeds": args.seeds,
        "pass_checkpoints": args.passes,
        "protocol_count": len(args.seeds) * len(args.passes),
        "records": records,
        "summary_by_pass": summarize(records, args.passes),
    }

    # Identify best checkpoint by mean held-out RMSE.
    best = min(
        result["summary_by_pass"].items(),
        key=lambda kv: kv[1]["mean_heldout_rmse"],
    )
    result["best_by_mean_heldout_rmse"] = {
        "passes_per_text": int(best[0]),
        **best[1],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
