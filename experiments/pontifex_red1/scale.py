# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Scaling study for Pontifex RED-1.

Measures delta = AUPRC(Pontifex) - max(AUPRC(best single), AUPRC(mean))
across increasing sample sizes, held-out semantic families, repeated seeds,
and channel corruption. No fixed effect-size pass/fail threshold is imposed.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from run import (
    ENCODERS,
    FAMILIES,
    Example,
    candidates_for,
    encoder_features,
    fit_head,
    permute_channel,
    sentence_metrics,
    split_families,
)

QUALIFIERS = (
    "today",
    "yesterday",
    "during testing",
    "in the current record",
    "in the archived record",
    "during review",
    "in the control sample",
    "in the comparison sample",
)

NOTES = (
    "The record was checked twice.",
    "The reference was stored separately.",
    "A neutral observer logged the case.",
    "The surrounding details were unchanged.",
)


def build_expanded_dataset(n: int) -> list[Example]:
    """Build up to 6,144 unique examples without changing the causal variable.

    The extra clauses increase surface diversity and distractor load. This is a
    sample-scale study, not yet the semantic-family diversity study.
    """
    capacity = len(FAMILIES) * 4 * 4 * len(QUALIFIERS) * len(NOTES)
    if not 100 <= n <= capacity:
        raise ValueError(f"n must be between 100 and {capacity}")

    out: list[Example] = []
    local_index = [0 for _ in FAMILIES]
    while len(out) < n:
        for fi, (family, template, targets, contexts) in enumerate(FAMILIES):
            if len(out) >= n:
                break
            j = local_index[fi]
            target = targets[j % len(targets)]
            ctx = contexts[(j // len(targets)) % len(contexts)]
            q = QUALIFIERS[(j // (len(targets) * len(contexts))) % len(QUALIFIERS)]
            note = NOTES[(j // (len(targets) * len(contexts) * len(QUALIFIERS))) % len(NOTES)]
            base = template.format(ctx=ctx, target=target)
            text = f"{base} This case was observed {q}. {note}"
            start = base.rfind(target)
            if start < 0:
                raise AssertionError((family, target, base))
            out.append(Example(f"scale-{len(out):05d}", family, text, start, start + len(target)))
            local_index[fi] += 1
    if len({e.text for e in out}) != len(out):
        raise AssertionError("expanded dataset contains duplicates")
    return out


def indices_for_examples(rows, example_ids: set[str]) -> np.ndarray:
    return np.array([i for i, row in enumerate(rows) if row.example_id in example_ids], dtype=int)


def evaluate_point(rows, x, examples: list[Example], seed: int, corruption: float) -> dict[str, object]:
    train_fams, test_fams = split_families(seed)
    subset_ids = {e.id for e in examples}
    train = np.array(
        [i for i, r in enumerate(rows) if r.example_id in subset_ids and r.family in train_fams],
        dtype=int,
    )
    test = np.array(
        [i for i, r in enumerate(rows) if r.example_id in subset_ids and r.family in test_fams],
        dtype=int,
    )
    y = np.array([r.label for r in rows], dtype=int)

    single_scores = [1.0 - x[:, k * 3] for k in range(3)]
    train_single = [sentence_metrics(rows, s, train).macro_auprc for s in single_scores]
    best_k = int(np.argmax(train_single))
    a_scores = single_scores[best_k]
    b_scores = np.mean(np.column_stack(single_scores), axis=1)

    c_head = fit_head(x[train], y[train], seed)
    c_scores = c_head.predict_proba(x)[:, 1]

    x_eval = x
    if corruption > 0:
        rng = np.random.default_rng(seed + 70_000 + int(corruption * 1000))
        corrupt_test = np.array(test, copy=True)
        rng.shuffle(corrupt_test)
        take = max(1, int(round(len(test) * corruption)))
        chosen = corrupt_test[:take]
        x_eval = permute_channel(x_eval, chosen, channel=2, seed=seed + 80_000)
    c_corrupt_scores = c_head.predict_proba(x_eval)[:, 1]

    a = sentence_metrics(rows, a_scores, test)
    b = sentence_metrics(rows, b_scores, test)
    c = sentence_metrics(rows, c_scores, test)
    cc = sentence_metrics(rows, c_corrupt_scores, test)
    best_simple = max(a.macro_auprc, b.macro_auprc)

    return {
        "seed": seed,
        "corruption": corruption,
        "best_single_encoder": ENCODERS[best_k],
        "test_families": sorted(test_fams),
        "A_best_single": asdict(a),
        "B_mean3": asdict(b),
        "C_pontifex": asdict(c),
        "C_corrupt": asdict(cc),
        "delta": c.macro_auprc - best_simple,
        "delta_corrupt": cc.macro_auprc - best_simple,
    }


def summarize(points: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, float], list[dict[str, object]]] = {}
    for p in points:
        grouped.setdefault((int(p["n"]), float(p["corruption"])), []).append(p)
    out = []
    for (n, corruption), rows in sorted(grouped.items()):
        d = np.array([float(r["delta"]) for r in rows], dtype=float)
        dc = np.array([float(r["delta_corrupt"]) for r in rows], dtype=float)
        out.append(
            {
                "n": n,
                "corruption": corruption,
                "seeds": len(rows),
                "median_delta": float(np.median(d)),
                "mean_delta": float(np.mean(d)),
                "positive_fraction": float(np.mean(d > 0)),
                "p10_delta": float(np.quantile(d, 0.10)),
                "p90_delta": float(np.quantile(d, 0.90)),
                "median_delta_corrupt": float(np.median(dc)),
            }
        )
    return out


def markdown(summary: list[dict[str, object]]) -> str:
    lines = [
        "# Pontifex scale study",
        "",
        "Primary quantity: `delta = AUPRC(C) - max(AUPRC(A), AUPRC(B))`.",
        "No fixed effect-size threshold is imposed; persistence and trajectory with scale are the target.",
        "",
        "| N | corrupt ch.3 | seeds | median delta | mean delta | P(delta>0) | p10 | p90 | median delta corrupt |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary:
        lines.append(
            f"| {r['n']} | {r['corruption']:.0%} | {r['seeds']} | {r['median_delta']:+.3f} | "
            f"{r['mean_delta']:+.3f} | {r['positive_fraction']:.0%} | {r['p10_delta']:+.3f} | "
            f"{r['p90_delta']:+.3f} | {r['median_delta_corrupt']:+.3f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[100, 300, 1000, 3000])
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--corruption", type=float, nargs="+", default=[0.0, 0.25, 0.5, 1.0])
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--output", type=Path, default=Path("pontifex-scale.json"))
    args = ap.parse_args()

    if any(not 0 <= c <= 1 for c in args.corruption):
        raise ValueError("corruption must be in [0,1]")
    max_n = max(args.sizes)
    examples = build_expanded_dataset(max_n)
    rows = [row for ex in examples for row in candidates_for(ex)]
    print(f"max_examples={max_n} candidates={len(rows)}")

    per_encoder = []
    for model in ENCODERS:
        print(f"encoding with {model}")
        per_encoder.append(encoder_features(model, rows, args.batch_size))
    x = np.concatenate(per_encoder, axis=1)

    points: list[dict[str, object]] = []
    for n in sorted(set(args.sizes)):
        subset = examples[:n]
        for seed in args.seeds:
            # Clean result only needs computing once per (n, seed); evaluate_point
            # also emits the requested corruption diagnostic.
            for corruption in args.corruption:
                p = evaluate_point(rows, x, subset, seed, corruption)
                p["n"] = n
                points.append(p)
                print(
                    f"n={n} seed={seed} corrupt={corruption:.2f} "
                    f"delta={p['delta']:+.4f} delta_corrupt={p['delta_corrupt']:+.4f}"
                )

    summary = summarize(points)
    result = {
        "experiment": "Pontifex scale study",
        "sizes": sorted(set(args.sizes)),
        "seeds": args.seeds,
        "corruption": args.corruption,
        "encoders": list(ENCODERS),
        "points": points,
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = args.output.with_suffix(".md")
    md.write_text(markdown(summary), encoding="utf-8")
    print(markdown(summary))


if __name__ == "__main__":
    main()
