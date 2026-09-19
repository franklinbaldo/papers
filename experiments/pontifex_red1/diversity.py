# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "scipy>=1.14",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex diversity study: semantic families and encoder-bank diversity.

Two independent axes are studied at controlled N:
1. semantic-family count: 12 -> 24 -> 48 -> 96;
2. encoder-bank size: 3 -> 5 -> 8.

Baselines:
A: best single encoder selected on train only.
B: unweighted mean saliency.
W: learned convex weighted mean (non-negative weights summing to one).
C: Pontifex nonlinear convergence head over bilateral signals.

The key interaction quantity is:
    delta_interaction = AUPRC(C) - AUPRC(W)
If this remains positive with scale/diversity, the head is doing more than
learning better static encoder weights.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import log_loss

from run import Candidate, Example, candidates_for, encoder_features, fit_head, sentence_metrics

ENCODER_BANK = (
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/paraphrase-MiniLM-L3-v2",
    "BAAI/bge-small-en-v1.5",
    "intfloat/e5-small-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
    "intfloat/multilingual-e5-small",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

# 12 semantic variables. Each receives 8 independently held-out language frames,
# yielding 96 family IDs. Increasing the family budget adds both semantic and
# compositional/syntactic diversity while keeping one causal span by construction.
SEMANTICS: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("animal", ("cat", "dog", "fox", "rabbit"), ("gate", "tree", "pond", "barn")),
    ("sentiment", ("wonderful", "terrible", "excellent", "awful"), ("review", "report", "comment", "note")),
    ("temperature", ("hot", "cold", "warm", "icy"), ("water", "metal", "surface", "liquid")),
    ("direction", ("left", "right", "forward", "backward"), ("robot", "vehicle", "cursor", "drone")),
    ("truth", ("true", "false", "correct", "wrong"), ("statement", "claim", "answer", "record")),
    ("urgency", ("urgent", "routine", "critical", "optional"), ("request", "task", "message", "repair")),
    ("safety", ("safe", "dangerous", "secure", "risky"), ("route", "procedure", "zone", "plan")),
    ("quantity", ("many", "few", "several", "zero"), ("marbles", "items", "tokens", "boxes")),
    ("permission", ("may", "cannot", "must", "should"), ("visitor", "operator", "agent", "user")),
    ("intent", ("delete", "keep", "share", "rename"), ("file", "record", "folder", "entry")),
    ("relation", ("above", "below", "beside", "behind"), ("Bob", "the marker", "the node", "the target")),
    ("color", ("red", "green", "blue", "yellow"), ("indicator", "signal", "lamp", "marker")),
)

FRAMES = (
    "The {ctx} value is {target}.",
    "For this case, {ctx} was recorded as {target}.",
    "Observers classified {ctx} as {target}.",
    "The final label assigned to {ctx} was {target}.",
    "In the archived sample, {ctx} appears {target}.",
    "During review, the property of {ctx} became {target}.",
    "The controlled trial reports {ctx} as {target}.",
    "According to the test record, {ctx} remains {target}.",
)

DISTRACTORS = (
    "The reference code was stored separately.",
    "A neutral observer logged the surrounding details.",
    "No other field changed during this trial.",
    "The timestamp and source identifier were preserved.",
)


@dataclass(frozen=True)
class FamilySpec:
    family: str
    semantic: str
    frame: str
    targets: tuple[str, ...]
    contexts: tuple[str, ...]


def family_specs() -> list[FamilySpec]:
    out: list[FamilySpec] = []
    for semantic, targets, contexts in SEMANTICS:
        for frame_idx, frame in enumerate(FRAMES):
            out.append(FamilySpec(f"{semantic}-f{frame_idx}", semantic, frame, targets, contexts))
    return out


def build_dataset(n: int, family_count: int) -> list[Example]:
    specs = family_specs()[:family_count]
    if family_count not in (12, 24, 48, 96):
        raise ValueError("family_count must be one of 12,24,48,96")
    if n < family_count * 4:
        raise ValueError("N too small to populate each family")
    out: list[Example] = []
    local = [0] * len(specs)
    while len(out) < n:
        for fi, spec in enumerate(specs):
            if len(out) >= n:
                break
            j = local[fi]
            target = spec.targets[j % len(spec.targets)]
            ctx = spec.contexts[(j // len(spec.targets)) % len(spec.contexts)]
            distractor = DISTRACTORS[(j // (len(spec.targets) * len(spec.contexts))) % len(DISTRACTORS)]
            repeat = j // (len(spec.targets) * len(spec.contexts) * len(DISTRACTORS))
            prefix = "" if repeat == 0 else f"Trial {repeat + 1}. "
            base = spec.frame.format(ctx=ctx, target=target)
            text = f"{prefix}{base} {distractor}"
            start = text.find(target)
            if start < 0:
                raise AssertionError((spec.family, target, text))
            out.append(Example(f"div-{family_count}-{len(out):06d}", spec.family, text, start, start + len(target)))
            local[fi] += 1
    if len({e.text for e in out}) != len(out):
        raise AssertionError("diversity dataset contains duplicate texts")
    return out


def split_families(families: list[str], seed: int) -> tuple[set[str], set[str]]:
    fams = sorted(set(families))
    rng = random.Random(seed)
    rng.shuffle(fams)
    n_test = max(3, round(len(fams) * 0.25))
    return set(fams[n_test:]), set(fams[:n_test])


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()


def fit_convex_weights(saliency: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Learn non-negative static encoder weights plus scalar calibration.

    The representation is strictly a convex weighted mean of per-encoder simple
    occlusion saliencies. beta/bias only calibrate probability for log-loss; the
    ranking score returned by the caller is the convex weighted mean itself.
    """
    k = saliency.shape[1]

    def objective(theta: np.ndarray) -> float:
        w = softmax(theta[:k])
        beta = np.exp(theta[k])
        bias = theta[k + 1]
        raw = saliency @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(beta * raw + bias, -30, 30)))
        return float(log_loss(y, p, labels=[0, 1]))

    init = np.zeros(k + 2, dtype=float)
    result = minimize(objective, init, method="L-BFGS-B")
    if not result.success:
        raise RuntimeError(f"weighted baseline optimization failed: {result.message}")
    theta = result.x
    return softmax(theta[:k]), float(np.exp(theta[k])), float(theta[k + 1])


def evaluate(rows: list[Candidate], x: np.ndarray, encoder_names: tuple[str, ...], seed: int) -> dict[str, object]:
    families = [r.family for r in rows]
    train_fams, test_fams = split_families(families, seed)
    train = np.array([i for i, r in enumerate(rows) if r.family in train_fams], dtype=int)
    test = np.array([i for i, r in enumerate(rows) if r.family in test_fams], dtype=int)
    y = np.array([r.label for r in rows], dtype=int)
    k = len(encoder_names)

    single = np.column_stack([1.0 - x[:, j * 3] for j in range(k)])
    train_scores = [sentence_metrics(rows, single[:, j], train).macro_auprc for j in range(k)]
    best_k = int(np.argmax(train_scores))
    a_score = single[:, best_k]
    b_score = np.mean(single, axis=1)

    weights, beta, bias = fit_convex_weights(single[train], y[train])
    w_score = single @ weights

    c_head = fit_head(x[train], y[train], seed)
    c_score = c_head.predict_proba(x)[:, 1]

    a = sentence_metrics(rows, a_score, test)
    b = sentence_metrics(rows, b_score, test)
    w = sentence_metrics(rows, w_score, test)
    c = sentence_metrics(rows, c_score, test)
    best_simple = max(a.macro_auprc, b.macro_auprc)
    best_linear = max(best_simple, w.macro_auprc)

    return {
        "seed": seed,
        "test_families": sorted(test_fams),
        "best_single_encoder": encoder_names[best_k],
        "weighted_mean_weights": {name: float(weight) for name, weight in zip(encoder_names, weights, strict=True)},
        "weighted_mean_calibration": {"beta": beta, "bias": bias},
        "A_best_single": asdict(a),
        "B_mean": asdict(b),
        "W_learned_weighted_mean": asdict(w),
        "C_pontifex": asdict(c),
        "delta_vs_simple": c.macro_auprc - best_simple,
        "delta_interaction": c.macro_auprc - w.macro_auprc,
        "delta_vs_best_linear": c.macro_auprc - best_linear,
    }


def summarize(points: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int], list[dict[str, object]]] = {}
    for p in points:
        grouped.setdefault((int(p["families"]), int(p["encoders"])), []).append(p)
    out: list[dict[str, object]] = []
    for (families, encoders), rows in sorted(grouped.items()):
        ds = np.array([float(r["delta_vs_simple"]) for r in rows])
        di = np.array([float(r["delta_interaction"]) for r in rows])
        dl = np.array([float(r["delta_vs_best_linear"]) for r in rows])
        out.append({
            "families": families,
            "encoders": encoders,
            "seeds": len(rows),
            "median_delta_vs_simple": float(np.median(ds)),
            "positive_vs_simple": float(np.mean(ds > 0)),
            "median_delta_interaction": float(np.median(di)),
            "positive_interaction": float(np.mean(di > 0)),
            "median_delta_vs_best_linear": float(np.median(dl)),
            "positive_vs_best_linear": float(np.mean(dl > 0)),
            "p10_interaction": float(np.quantile(di, 0.10)),
            "p90_interaction": float(np.quantile(di, 0.90)),
        })
    return out


def markdown(summary: list[dict[str, object]], n: int) -> str:
    lines = [
        "# Pontifex diversity study",
        "",
        f"Controlled sample size: **N={n}**.",
        "`delta_interaction = AUPRC(Pontifex) - AUPRC(learned convex weighted mean)`.",
        "A persistent positive interaction delta is evidence that the convergence head does more than learn static encoder weights.",
        "",
        "| families | encoders | seeds | median Δ simple | P(Δs>0) | median Δ interaction | P(Δi>0) | p10 Δi | p90 Δi |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary:
        lines.append(
            f"| {r['families']} | {r['encoders']} | {r['seeds']} | {r['median_delta_vs_simple']:+.3f} | "
            f"{r['positive_vs_simple']:.0%} | {r['median_delta_interaction']:+.3f} | {r['positive_interaction']:.0%} | "
            f"{r['p10_interaction']:+.3f} | {r['p90_interaction']:+.3f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--examples", type=int, default=1920)
    ap.add_argument("--families", type=int, nargs="+", default=[12, 24, 48, 96])
    ap.add_argument("--encoder-counts", type=int, nargs="+", default=[3, 5, 8])
    ap.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--output", type=Path, default=Path("pontifex-diversity.json"))
    args = ap.parse_args()

    max_encoders = max(args.encoder_counts)
    encoder_names = ENCODER_BANK[:max_encoders]
    points: list[dict[str, object]] = []

    # Each family-count condition receives the same N, so family diversity is
    # varied independently from total sample count.
    for family_count in args.families:
        examples = build_dataset(args.examples, family_count)
        rows = [row for ex in examples for row in candidates_for(ex)]
        print(f"families={family_count} examples={len(examples)} candidates={len(rows)}")

        per_encoder = []
        for model in encoder_names:
            print(f"encoding families={family_count} with {model}")
            per_encoder.append(encoder_features(model, rows, args.batch_size))
        x_full = np.concatenate(per_encoder, axis=1)

        for k in args.encoder_counts:
            x = x_full[:, : k * 3]
            names = tuple(encoder_names[:k])
            for seed in args.seeds:
                p = evaluate(rows, x, names, seed)
                p["families"] = family_count
                p["encoders"] = k
                p["n"] = args.examples
                points.append(p)
                print(
                    f"families={family_count} encoders={k} seed={seed} "
                    f"delta_simple={p['delta_vs_simple']:+.4f} "
                    f"delta_interaction={p['delta_interaction']:+.4f}"
                )

    summary = summarize(points)
    result = {
        "experiment": "Pontifex diversity study",
        "examples_per_condition": args.examples,
        "family_counts": args.families,
        "encoder_counts": args.encoder_counts,
        "seeds": args.seeds,
        "encoder_bank": list(encoder_names),
        "baseline_W": "learned non-negative convex weighted mean of per-encoder occlusion saliency",
        "points": points,
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = args.output.with_suffix(".md")
    md.write_text(markdown(summary, args.examples), encoding="utf-8")
    print(markdown(summary, args.examples))


if __name__ == "__main__":
    main()
