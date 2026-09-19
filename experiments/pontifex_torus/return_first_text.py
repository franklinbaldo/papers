# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Sequential 16-pass text accumulation with a return to the first text.

Protocol per seed:
1. choose T1..T11 and a disjoint held-out set;
2. update the same shared torus geometry with T1 for 16 passes;
3. update with T2..T11, each for 16 passes, saving geometry after every text;
4. revisit T1 for 16 passes and save the returned geometry.

The experiment measures:
- accumulation/generalization after every new text;
- forgetting of T1 across ten intervening texts;
- recovery of T1 after revisit;
- collateral effect of that revisit on T2..T11 and held-out texts.

No optical/cavity interpretation is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error

from run import build_rows, features, load_rows, make_texts


def select_rows(rows, ids):
    wanted = set(map(int, ids))
    return [r for r in rows if r.text_id in wanted]


def rmse(model, rows):
    if not rows:
        return float("nan")
    x = features(rows, "torus")
    y = np.asarray([r.response_b for r in rows], dtype=float)
    pred = model.predict(x)
    return float(mean_squared_error(y, pred) ** 0.5)


def snapshot(model):
    return np.concatenate([model.coef_.copy(), np.asarray([model.intercept_[0]])])


def run_seed(rows, n_texts, seed, passes, heldout_count):
    rng = np.random.default_rng(seed)
    ids = np.arange(n_texts)
    rng.shuffle(ids)

    sequence = list(map(int, ids[:11]))
    heldout_ids = list(map(int, ids[11:11 + heldout_count]))
    first_id = sequence[0]

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

    heldout = select_rows(rows, heldout_ids)
    first_rows = select_rows(rows, [first_id])
    stages = []
    geometries = []
    prev_geom = None

    for stage_idx, text_id in enumerate(sequence, start=1):
        current = select_rows(rows, [text_id])
        x = features(current, "torus")
        y = np.asarray([r.response_b for r in current], dtype=float)
        for _ in range(passes):
            model.partial_fit(x, y)

        geom = snapshot(model)
        delta = (
            float(np.linalg.norm(geom - prev_geom))
            if prev_geom is not None
            else float(np.linalg.norm(geom))
        )
        prev_geom = geom
        geometries.append(geom.tolist())

        seen_ids = sequence[:stage_idx]
        previous_other_ids = sequence[1:stage_idx]
        stages.append({
            "stage": stage_idx,
            "event": f"T{stage_idx}_x{passes}",
            "text_id": int(text_id),
            "current_rmse": rmse(model, current),
            "first_text_rmse": rmse(model, first_rows),
            "seen_rmse": rmse(model, select_rows(rows, seen_ids)),
            "other_seen_rmse": (
                rmse(model, select_rows(rows, previous_other_ids))
                if previous_other_ids else None
            ),
            "heldout_rmse": rmse(model, heldout),
            "geometry_delta_l2": delta,
        })

    before_return = stages[-1].copy()
    other_rows = select_rows(rows, sequence[1:])

    x1 = features(first_rows, "torus")
    y1 = np.asarray([r.response_b for r in first_rows], dtype=float)
    for _ in range(passes):
        model.partial_fit(x1, y1)

    geom_return = snapshot(model)
    return_delta = float(np.linalg.norm(geom_return - prev_geom))
    geometries.append(geom_return.tolist())

    after_return = {
        "stage": 12,
        "event": f"T1_return_x{passes}",
        "text_id": int(first_id),
        "current_rmse": rmse(model, first_rows),
        "first_text_rmse": rmse(model, first_rows),
        "seen_rmse": rmse(model, select_rows(rows, sequence)),
        "other_seen_rmse": rmse(model, other_rows),
        "heldout_rmse": rmse(model, heldout),
        "geometry_delta_l2": return_delta,
    }
    stages.append(after_return)

    return {
        "seed": int(seed),
        "sequence_ids": sequence,
        "heldout_ids": heldout_ids,
        "stages": stages,
        "geometries": geometries,
        "derived": {
            "t1_rmse_after_first_16": stages[0]["first_text_rmse"],
            "t1_rmse_after_10_intervening_texts": before_return["first_text_rmse"],
            "t1_forgetting_delta": before_return["first_text_rmse"] - stages[0]["first_text_rmse"],
            "t1_rmse_after_return_16": after_return["first_text_rmse"],
            "t1_recovery_delta": after_return["first_text_rmse"] - before_return["first_text_rmse"],
            "other_seen_delta_due_to_return": after_return["other_seen_rmse"] - before_return["other_seen_rmse"],
            "heldout_delta_due_to_return": after_return["heldout_rmse"] - before_return["heldout_rmse"],
            "seen_delta_due_to_return": after_return["seen_rmse"] - before_return["seen_rmse"],
            "return_geometry_delta_l2": return_delta,
        },
    }


def summarize(runs):
    keys = [
        "t1_forgetting_delta",
        "t1_recovery_delta",
        "other_seen_delta_due_to_return",
        "heldout_delta_due_to_return",
        "seen_delta_due_to_return",
        "return_geometry_delta_l2",
    ]
    out = {}
    for key in keys:
        vals = np.asarray([r["derived"][key] for r in runs], dtype=float)
        out[key] = {
            "mean": float(vals.mean()),
            "median": float(np.median(vals)),
            "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            "fraction_negative": float(np.mean(vals < 0)),
            "min": float(vals.min()),
            "max": float(vals.max()),
        }

    trajectory = []
    for i in range(12):
        stage_rows = [r["stages"][i] for r in runs]
        trajectory.append({
            "stage": i + 1,
            "event": stage_rows[0]["event"],
            "mean_first_text_rmse": float(np.mean([x["first_text_rmse"] for x in stage_rows])),
            "mean_seen_rmse": float(np.mean([x["seen_rmse"] for x in stage_rows])),
            "mean_heldout_rmse": float(np.mean([x["heldout_rmse"] for x in stage_rows])),
            "mean_geometry_delta_l2": float(np.mean([x["geometry_delta_l2"] for x in stage_rows])),
        })
    out["mean_trajectory"] = trajectory
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=120)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--field-seed", type=int, default=17)
    ap.add_argument(
        "--field-store",
        type=Path,
        default=None,
        help="Optional cached response-field NPZ produced by build_field_store.py.",
    )
    ap.add_argument("--passes", type=int, default=16)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--heldout-count", type=int, default=30)
    ap.add_argument("--output", type=Path, default=Path("pontifex-torus-return-t1.json"))
    args = ap.parse_args()

    if args.field_store:
        rows = load_rows(args.field_store)
        observed_ids = sorted({int(r.text_id) for r in rows})
        if observed_ids != list(range(args.texts)):
            raise SystemExit(
                "cached field/text-count mismatch: "
                f"expected ids 0..{args.texts - 1}, got {len(observed_ids)} ids"
            )
    else:
        texts = make_texts(args.texts, args.field_seed)
        rows = build_rows(texts, args.positions, args.field_seed)

    runs = [
        run_seed(rows, args.texts, seed, args.passes, args.heldout_count)
        for seed in args.seeds
    ]

    result = {
        "experiment": "Pontifex Torus: 11 texts at 16 passes, then return to T1",
        "scope": (
            "Same shared torus geometry, no reset. T1..T11 each receive 16 forward passes; "
            "then T1 receives 16 more. Geometry is snapshotted after every stage. "
            "No optical/cavity interpretation."
        ),
        "texts": args.texts,
        "positions_per_text": args.positions,
        "field_seed": args.field_seed,
        "field_store": str(args.field_store) if args.field_store else None,
        "passes_per_exposure": args.passes,
        "seeds": args.seeds,
        "runs": runs,
        "summary": summarize(runs),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
