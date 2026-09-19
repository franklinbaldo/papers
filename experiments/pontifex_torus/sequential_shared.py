# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex Torus sequential shared-space experiment.

E1: forward-only ("vai, vai, vai")
    One shared torus map is updated once per new text and never reset.

E2: forward + revisit
    Same stream, same initialization, same shared space, but each text is
    presented twice consecutively before advancing to the next text.

No optical cavity, Q-factor, reverse direction, or MaleCNS is modeled here.
The only manipulated variable is number of passes over the current text.
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


def rmse(model, rows):
    if not rows:
        return float("nan")
    x = features(rows, "torus")
    y = np.asarray([r.response_b for r in rows], dtype=float)
    pred = model.predict(x)
    return float(mean_squared_error(y, pred) ** 0.5)


def run_protocol(rows, sequence_ids, heldout_ids, seed, passes_per_text):
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
    history = []
    prev_coef = None

    for step, text_id in enumerate(sequence_ids, start=1):
        current = rows_for_ids(rows, [text_id])
        x = features(current, "torus")
        y = np.asarray([r.response_b for r in current], dtype=float)

        for _ in range(passes_per_text):
            model.partial_fit(x, y)

        seen_ids.append(int(text_id))
        seen = rows_for_ids(rows, seen_ids)

        coef = model.coef_.copy()
        state_delta = (
            float(np.linalg.norm(coef - prev_coef))
            if prev_coef is not None
            else float(np.linalg.norm(coef))
        )
        prev_coef = coef

        history.append(
            {
                "step": step,
                "text_id": int(text_id),
                "passes_on_current_text": passes_per_text,
                "current_text_rmse": rmse(model, current),
                "seen_texts_rmse": rmse(model, seen),
                "heldout_texts_rmse": rmse(model, heldout),
                "state_delta_l2": state_delta,
            }
        )

    final_seen = rows_for_ids(rows, seen_ids)
    return {
        "passes_per_text": passes_per_text,
        "history": history,
        "final": {
            "seen_texts_rmse": rmse(model, final_seen),
            "heldout_texts_rmse": rmse(model, heldout),
            "mean_state_delta_l2": float(
                np.mean([h["state_delta_l2"] for h in history])
            ),
            "late_state_delta_l2": float(
                np.mean([h["state_delta_l2"] for h in history[-10:]])
            ),
            "mean_heldout_rmse_over_time": float(
                np.mean([h["heldout_texts_rmse"] for h in history])
            ),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=80)
    ap.add_argument("--positions", type=int, default=6)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument(
        "--field-store",
        type=Path,
        default=None,
        help="Optional cached response-field NPZ produced by build_field_store.py.",
    )
    ap.add_argument(
        "--heldout-frac",
        type=float,
        default=0.25,
        help="Fraction of texts never used to update the shared space.",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-torus-sequential.json"),
    )
    args = ap.parse_args()

    if not 0.1 <= args.heldout_frac <= 0.5:
        raise SystemExit("--heldout-frac must be between 0.1 and 0.5")

    if args.field_store:
        rows = load_rows(args.field_store)
        observed_ids = sorted({int(r.text_id) for r in rows})
        expected_ids = list(range(args.texts))
        if observed_ids != expected_ids:
            raise SystemExit(
                "cached field/text-count mismatch: "
                f"expected ids 0..{args.texts - 1}, got {len(observed_ids)} ids"
            )
    else:
        texts = make_texts(args.texts, args.seed)
        rows = build_rows(texts, args.positions, args.seed)

    rng = np.random.default_rng(args.seed)
    ids = np.arange(args.texts)
    rng.shuffle(ids)
    n_hold = max(4, int(round(args.texts * args.heldout_frac)))
    heldout_ids = list(map(int, ids[:n_hold]))
    sequence_ids = list(map(int, ids[n_hold:]))

    forward = run_protocol(
        rows, sequence_ids, heldout_ids, args.seed, passes_per_text=1
    )
    revisit = run_protocol(
        rows, sequence_ids, heldout_ids, args.seed, passes_per_text=2
    )

    f = forward["final"]
    r = revisit["final"]
    result = {
        "experiment": "Pontifex Torus sequential shared space",
        "scope": (
            "E1 forward-only and E2 forward+revisit. Same text order, same "
            "features, same initialization policy, no reset between texts, "
            "no optical/cavity interpretation."
        ),
        "texts": args.texts,
        "field_store": str(args.field_store) if args.field_store else None,
        "training_sequence_texts": len(sequence_ids),
        "heldout_texts": len(heldout_ids),
        "positions_per_text": args.positions,
        "sequence_ids": sequence_ids,
        "heldout_ids": heldout_ids,
        "E1_forward_only": forward,
        "E2_forward_plus_revisit": revisit,
        "comparison": {
            "final_heldout_rmse_revisit_minus_forward": (
                r["heldout_texts_rmse"] - f["heldout_texts_rmse"]
            ),
            "final_seen_rmse_revisit_minus_forward": (
                r["seen_texts_rmse"] - f["seen_texts_rmse"]
            ),
            "mean_heldout_rmse_revisit_minus_forward": (
                r["mean_heldout_rmse_over_time"]
                - f["mean_heldout_rmse_over_time"]
            ),
            "late_state_delta_revisit_minus_forward": (
                r["late_state_delta_l2"] - f["late_state_delta_l2"]
            ),
        },
        "interpretation_rule": {
            "E1": (
                "Inspect held-out RMSE and state-delta trajectories across successive "
                "different texts. Falling held-out RMSE indicates accumulating shared "
                "structure; rising RMSE indicates interference; state_delta -> 0 "
                "indicates stabilization."
            ),
            "E2": (
                "Compare against E1 only. Negative revisit-minus-forward held-out RMSE "
                "supports a useful second pass; zero suggests no added value; positive "
                "suggests revisit harms generalization or overweights the current text."
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
