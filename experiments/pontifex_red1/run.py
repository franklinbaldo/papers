# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "scikit-learn>=1.5",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex RED-1: learned multi-space convergence vs trivial baselines.

The experiment is intentionally small and falsification-first. It uses synthetic
sentences whose causal span is known by construction, frozen independent text
encoders, held-out template families, and a tiny learned convergence head.

Primary preregistered claim:
    C (Pontifex) must beat max(A, B) by >= 0.05 macro AUPRC on held-out data.

Conditions:
    A: best single encoder, selected on training families only.
    B: simple mean saliency across the three encoders.
    C: learned convergence head over bilateral multi-space signals.
    D: the same head class trained/evaluated with encoder 3 semantically
       contaminated by within-split permutation; it should learn to ignore the
       bad channel or degrade in an understandable way.

A diagnostic also evaluates the clean C head after corrupting encoder 3 only at
held-out time. If this does not hurt at all, the third channel was likely unused;
if it improves, leakage/artifact hunting is warranted.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics import average_precision_score
from sklearn.neural_network import MLPClassifier

ENCODERS = (
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/paraphrase-MiniLM-L3-v2",
    "BAAI/bge-small-en-v1.5",
)

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


@dataclass(frozen=True)
class Example:
    id: str
    family: str
    text: str
    causal_start: int
    causal_end: int


@dataclass(frozen=True)
class Candidate:
    example_id: str
    family: str
    text: str
    span_text: str
    start: int
    end: int
    label: int
    masked: str
    left: str
    right: str


@dataclass
class Metrics:
    macro_auprc: float
    precision_at_1: float
    causal_mass: float


FAMILIES: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("animal", "The animal near {ctx} is a {target}.", ("cat", "dog", "fox", "rabbit"), ("the gate", "the tree", "the pond", "the barn")),
    ("sentiment", "The {ctx} review was {target}.", ("wonderful", "terrible", "excellent", "awful"), ("short", "verified", "customer", "editorial")),
    ("temperature", "The water in the {ctx} cup feels {target}.", ("hot", "cold", "warm", "icy"), ("glass", "metal", "paper", "ceramic")),
    ("direction", "After the signal, the {ctx} robot moved {target}.", ("left", "right", "forward", "backward"), ("small", "blue", "test", "service")),
    ("truth", "The {ctx} statement is {target}.", ("true", "false", "correct", "wrong"), ("final", "quoted", "formal", "written")),
    ("urgency", "The {ctx} request is {target}.", ("urgent", "routine", "critical", "optional"), ("support", "travel", "repair", "access")),
    ("safety", "The {ctx} route is {target}.", ("safe", "dangerous", "secure", "risky"), ("mountain", "night", "river", "coastal")),
    ("quantity", "The {ctx} box contains {target} marbles.", ("many", "few", "several", "zero"), ("red", "wooden", "sealed", "open")),
    ("permission", "The {ctx} visitor {target} enter.", ("may", "cannot", "must", "should"), ("registered", "late", "invited", "unknown")),
    ("intent", "The {ctx} user wants to {target} the file.", ("delete", "keep", "share", "rename"), ("new", "admin", "remote", "local")),
    ("relation", "In the {ctx} diagram, Alice is {target} Bob.", ("above", "below", "beside", "behind"), ("simple", "printed", "final", "training")),
    ("color", "The {ctx} indicator light is {target}.", ("red", "green", "blue", "yellow"), ("status", "power", "network", "warning")),
)


def build_dataset(n: int) -> list[Example]:
    if not 100 <= n <= 300:
        raise ValueError("RED-1 is preregistered for 100-300 examples")
    out: list[Example] = []
    i = 0
    while len(out) < n:
        family, template, targets, contexts = FAMILIES[i % len(FAMILIES)]
        target = targets[(i // len(FAMILIES)) % len(targets)]
        ctx = contexts[(i // (len(FAMILIES) * len(targets))) % len(contexts)]
        text = template.format(ctx=ctx, target=target)
        start = text.rfind(target)
        if start < 0:
            raise AssertionError((family, target, text))
        out.append(Example(f"e{i:04d}", family, text, start, start + len(target)))
        i += 1
    return out


def candidates_for(ex: Example) -> list[Candidate]:
    rows: list[Candidate] = []
    for m in WORD_RE.finditer(ex.text):
        start, end = m.span()
        label = int(start == ex.causal_start and end == ex.causal_end)
        masked = ex.text[:start] + "[MASK]" + ex.text[end:]
        left = ex.text[:start].strip() or "[EMPTY]"
        right = ex.text[end:].strip() or "[EMPTY]"
        rows.append(Candidate(ex.id, ex.family, ex.text, m.group(), start, end, label, masked, left, right))
    if sum(r.label for r in rows) != 1:
        raise AssertionError(f"expected one causal candidate: {ex}")
    return rows


def cos_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    an = np.linalg.norm(a, axis=1)
    bn = np.linalg.norm(b, axis=1)
    denom = np.maximum(an * bn, 1e-12)
    return np.sum(a * b, axis=1) / denom


def encoder_features(model_name: str, rows: list[Candidate], batch_size: int) -> np.ndarray:
    model = SentenceTransformer(model_name)
    originals = [r.text for r in rows]
    masked = [r.masked for r in rows]
    left = [r.left for r in rows]
    right = [r.right for r in rows]
    unique = list(dict.fromkeys(originals + masked + left + right))
    emb = model.encode(unique, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=False)
    by_text = {text: emb[i] for i, text in enumerate(unique)}
    o = np.stack([by_text[x] for x in originals])
    m = np.stack([by_text[x] for x in masked])
    l = np.stack([by_text[x] for x in left])
    r = np.stack([by_text[x] for x in right])
    # Bilateral signal contract: all values are within-space similarities; no
    # embedding vectors from different encoders are ever aligned or compared.
    return np.column_stack((cos_rows(o, m), cos_rows(l, o), cos_rows(r, o)))


def sentence_metrics(rows: list[Candidate], scores: np.ndarray, indices: np.ndarray) -> Metrics:
    grouped: dict[str, list[int]] = {}
    for idx in indices:
        grouped.setdefault(rows[int(idx)].example_id, []).append(int(idx))
    aps: list[float] = []
    p1: list[float] = []
    masses: list[float] = []
    for ids in grouped.values():
        y = np.array([rows[i].label for i in ids], dtype=int)
        s = np.array([float(scores[i]) for i in ids], dtype=float)
        aps.append(float(average_precision_score(y, s)))
        p1.append(float(y[int(np.argmax(s))]))
        # Convert any arbitrary score to positive saliency mass monotonically.
        z = s - np.max(s)
        w = np.exp(np.clip(z, -50.0, 0.0))
        w /= max(float(w.sum()), 1e-12)
        masses.append(float(w[np.flatnonzero(y)[0]]))
    return Metrics(float(np.mean(aps)), float(np.mean(p1)), float(np.mean(masses)))


def split_families(seed: int) -> tuple[set[str], set[str]]:
    fams = sorted({f[0] for f in FAMILIES})
    rng = random.Random(seed)
    rng.shuffle(fams)
    n_test = max(3, round(len(fams) * 0.33))
    test = set(fams[:n_test])
    return set(fams[n_test:]), test


def permute_channel(x: np.ndarray, indices: np.ndarray, channel: int, seed: int) -> np.ndarray:
    out = x.copy()
    cols = slice(channel * 3, channel * 3 + 3)
    rng = np.random.default_rng(seed)
    shuffled = np.array(indices, copy=True)
    rng.shuffle(shuffled)
    out[indices, cols] = x[shuffled, cols]
    return out


def fit_head(x: np.ndarray, y: np.ndarray, seed: int) -> MLPClassifier:
    head = MLPClassifier(
        hidden_layer_sizes=(16,),
        activation="relu",
        solver="adam",
        alpha=0.01,
        learning_rate_init=0.003,
        max_iter=1200,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=40,
        random_state=seed,
    )
    head.fit(x, y)
    return head


def run_seed(rows: list[Candidate], x: np.ndarray, seed: int) -> dict[str, object]:
    train_fams, test_fams = split_families(seed)
    train = np.array([i for i, r in enumerate(rows) if r.family in train_fams], dtype=int)
    test = np.array([i for i, r in enumerate(rows) if r.family in test_fams], dtype=int)
    y = np.array([r.label for r in rows], dtype=int)

    # A: pick best single encoder strictly on training families.
    single_scores = [1.0 - x[:, k * 3] for k in range(3)]
    train_single = [sentence_metrics(rows, s, train).macro_auprc for s in single_scores]
    best_k = int(np.argmax(train_single))
    a_scores = single_scores[best_k]

    # B: unweighted mean of the same simple occlusion saliency.
    b_scores = np.mean(np.column_stack(single_scores), axis=1)

    # C: learned convergence over all 9 scalar signals (3 per encoder).
    c_head = fit_head(x[train], y[train], seed)
    c_scores = c_head.predict_proba(x)[:, 1]

    # D: encoder 3 is semantically broken by permutation in both train/test.
    x_bad = permute_channel(x, train, channel=2, seed=seed + 1000)
    x_bad = permute_channel(x_bad, test, channel=2, seed=seed + 2000)
    d_head = fit_head(x_bad[train], y[train], seed + 10_000)
    d_scores = d_head.predict_proba(x_bad)[:, 1]

    # Cruel diagnostic: corrupt only held-out input to the clean C head.
    x_c_test_bad = permute_channel(x, test, channel=2, seed=seed + 3000)
    c_bad_test_scores = c_head.predict_proba(x_c_test_bad)[:, 1]

    metrics = {
        "A_best_single": asdict(sentence_metrics(rows, a_scores, test)),
        "B_mean3": asdict(sentence_metrics(rows, b_scores, test)),
        "C_pontifex": asdict(sentence_metrics(rows, c_scores, test)),
        "D_pontifex_bad_channel": asdict(sentence_metrics(rows, d_scores, test)),
        "C_corrupt_only_at_test": asdict(sentence_metrics(rows, c_bad_test_scores, test)),
    }
    best_simple = max(metrics["A_best_single"]["macro_auprc"], metrics["B_mean3"]["macro_auprc"])
    margin = metrics["C_pontifex"]["macro_auprc"] - best_simple
    return {
        "seed": seed,
        "train_families": sorted(train_fams),
        "test_families": sorted(test_fams),
        "best_single_encoder": ENCODERS[best_k],
        "metrics": metrics,
        "C_minus_best_simple_auprc": margin,
        "h1_pass": margin >= 0.05,
    }


def markdown_report(result: dict[str, object]) -> str:
    lines = [
        "# Pontifex RED-1 result",
        "",
        "Preregistered H1: `C - max(A, B) >= 0.05` macro AUPRC on held-out template families.",
        "",
        "| seed | A single | B mean | C Pontifex | D bad channel | C test-corrupt | C-best simple | H1 |",
        "|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for s in result["seeds"]:
        m = s["metrics"]
        lines.append(
            f"| {s['seed']} | {m['A_best_single']['macro_auprc']:.3f} | {m['B_mean3']['macro_auprc']:.3f} | "
            f"{m['C_pontifex']['macro_auprc']:.3f} | {m['D_pontifex_bad_channel']['macro_auprc']:.3f} | "
            f"{m['C_corrupt_only_at_test']['macro_auprc']:.3f} | {s['C_minus_best_simple_auprc']:+.3f} | "
            f"{'PASS' if s['h1_pass'] else 'FALSIFIED'} |"
        )
    agg = result["aggregate"]
    lines += [
        "",
        f"Median C-best-simple margin: **{agg['median_margin']:+.3f}**.",
        f"Seeds passing +5 pp: **{agg['passes']}/{agg['n_seeds']}**.",
        f"Overall RED-1 verdict: **{agg['verdict']}**.",
        "",
        "The scientific verdict does not control the process exit code: a falsified hypothesis is a successful experiment, not a broken CI job.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--examples", type=int, default=240)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--output", type=Path, default=Path("pontifex-red1-result.json"))
    args = ap.parse_args()

    examples = build_dataset(args.examples)
    rows = [row for ex in examples for row in candidates_for(ex)]
    print(f"examples={len(examples)} candidates={len(rows)} families={len(FAMILIES)}")

    per_encoder = []
    for model in ENCODERS:
        print(f"encoding with {model}")
        per_encoder.append(encoder_features(model, rows, args.batch_size))
    x = np.concatenate(per_encoder, axis=1)
    if x.shape != (len(rows), 9) or not np.isfinite(x).all():
        raise AssertionError(f"bad feature matrix {x.shape}")

    seed_results = [run_seed(rows, x, seed) for seed in args.seeds]
    margins = [float(s["C_minus_best_simple_auprc"]) for s in seed_results]
    passes = sum(bool(s["h1_pass"]) for s in seed_results)
    # "Consistent" is preregistered as all seeds non-negative plus >=5 pp on
    # a majority of seeds and on the median margin.
    consistent = min(margins) >= 0.0 and np.median(margins) >= 0.05 and passes >= math.ceil(len(margins) / 2)
    verdict = "SURVIVES" if consistent else "FALSIFIED_OR_NOT_SUPPORTED"

    result = {
        "experiment": "Pontifex RED-1",
        "examples": len(examples),
        "candidate_spans": len(rows),
        "encoders": list(ENCODERS),
        "preregistered_h1": "C must improve >= 0.05 macro AUPRC over max(A,B) on held-out template families",
        "seeds": seed_results,
        "aggregate": {
            "n_seeds": len(seed_results),
            "passes": passes,
            "median_margin": float(np.median(margins)),
            "min_margin": float(np.min(margins)),
            "max_margin": float(np.max(margins)),
            "verdict": verdict,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = args.output.with_suffix(".md")
    md.write_text(markdown_report(result), encoding="utf-8")
    print(markdown_report(result))
    print(f"wrote {args.output} and {md}")


if __name__ == "__main__":
    main()
