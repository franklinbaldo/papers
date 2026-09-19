# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "datasets>=3.0",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "scipy>=1.14",
#   "sentence-transformers>=5.0",
# ]
# ///
"""External STS-B benchmark for low-budget Pontifex latent-space transport.

Scientific question
-------------------
Given frozen semantic spaces A and B, how much of B's downstream STS utility can
be recovered from A using only K shared, unlabeled A<->B sentence correspondences?

The primary Pontifex condition is anchor transport: a held-out A vector is located
relative to K A-side anchors; the same barycentric weights reconstruct a point in
B from the corresponding B-side anchors. No task labels are used to fit the
transport. STS labels are used only on validation to choose temperature and on the
untouched test split for final evaluation.

Baselines at the same K:
- A-only
- B-oracle ceiling
- Orthogonal/rectangular Procrustes A->B
- multi-output Ridge A->B with alpha selected on validation
- shuffled-anchor Pontifex control

Leakage contract
----------------
- anchors come only from STS-B train sentences;
- any train sentence appearing verbatim in validation or test is excluded;
- no validation/test sentence is used to fit A->B transport;
- no test label participates in model/hyperparameter selection;
- B test embeddings are computed only for the oracle ceiling and geometry
  diagnostics; Pontifex and baselines never consume them for fitting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from datasets import load_dataset
from scipy.stats import pearsonr, spearmanr
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import Ridge

DATASET = "sentence-transformers/stsb"
MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_B = "sentence-transformers/all-mpnet-base-v2"
TEMPERATURES = (0.01, 0.02, 0.04, 0.07, 0.1, 0.2, 0.4, 0.7, 1.0)
RIDGE_ALPHAS = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)


def normalized_text(x: str) -> str:
    return " ".join(str(x).strip().split())


def sha256_lines(lines: Iterable[str]) -> str:
    h = hashlib.sha256()
    for line in lines:
        h.update(str(line).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def l2norm(x: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(denom, 1e-12)


def cosine_pairs(x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
    x1n = l2norm(x1)
    x2n = l2norm(x2)
    return np.sum(x1n * x2n, axis=1)


def correlations(scores: np.ndarray, gold: np.ndarray) -> dict[str, float]:
    p = pearsonr(scores, gold).statistic
    s = spearmanr(scores, gold).statistic
    return {"pearson": float(p), "spearman": float(s)}


def unique_in_order(xs: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        x = normalized_text(x)
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def split_sentences(split) -> tuple[list[str], list[str], np.ndarray]:
    s1 = [normalized_text(x) for x in split["sentence1"]]
    s2 = [normalized_text(x) for x in split["sentence2"]]
    y = np.asarray(split["score"], dtype=np.float64)
    return s1, s2, y


@dataclass
class Embeddings:
    texts: list[str]
    a: np.ndarray
    b: np.ndarray

    def lookup(self) -> dict[str, int]:
        return {t: i for i, t in enumerate(self.texts)}


def encode_all(texts: list[str], cache: Path | None) -> Embeddings:
    text_hash = sha256_lines(texts)
    if cache and cache.exists():
        payload = np.load(cache, allow_pickle=False)
        if (
            str(payload["text_hash"].item()) == text_hash
            and str(payload["model_a"].item()) == MODEL_A
            and str(payload["model_b"].item()) == MODEL_B
        ):
            return Embeddings(
                texts=texts,
                a=np.asarray(payload["a"], dtype=np.float32),
                b=np.asarray(payload["b"], dtype=np.float32),
            )

    model_a = SentenceTransformer(MODEL_A)
    model_b = SentenceTransformer(MODEL_B)
    a = model_a.encode(
        texts,
        batch_size=128,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)
    b = model_b.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)

    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            cache,
            text_hash=np.asarray(text_hash),
            model_a=np.asarray(MODEL_A),
            model_b=np.asarray(MODEL_B),
            a=a,
            b=b,
        )
    return Embeddings(texts=texts, a=a, b=b)


def gather(matrix: np.ndarray, index: dict[str, int], texts: list[str]) -> np.ndarray:
    return matrix[np.asarray([index[t] for t in texts], dtype=np.int64)]


def fit_procrustes(a_anchor: np.ndarray, b_anchor: np.ndarray) -> np.ndarray:
    """Rectangular orthogonal Procrustes map for unequal embedding dimensions."""
    a0 = a_anchor - a_anchor.mean(axis=0, keepdims=True)
    b0 = b_anchor - b_anchor.mean(axis=0, keepdims=True)
    cross = a0.T @ b0
    u, _, vt = np.linalg.svd(cross, full_matrices=False)
    return (u @ vt).astype(np.float32)


def apply_centered_map(
    x: np.ndarray,
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    w: np.ndarray,
) -> np.ndarray:
    return (x - a_anchor.mean(axis=0, keepdims=True)) @ w + b_anchor.mean(
        axis=0, keepdims=True
    )


def softmax_rows(x: np.ndarray) -> np.ndarray:
    z = x - x.max(axis=1, keepdims=True)
    ez = np.exp(z)
    return ez / np.maximum(ez.sum(axis=1, keepdims=True), 1e-12)


def anchor_transport(
    x_a: np.ndarray,
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    temperature: float,
) -> np.ndarray:
    sims = l2norm(x_a) @ l2norm(a_anchor).T
    weights = softmax_rows(sims / temperature)
    return weights @ b_anchor


def score_transport(
    pred_b_1: np.ndarray,
    pred_b_2: np.ndarray,
    gold: np.ndarray,
) -> dict[str, float]:
    return correlations(cosine_pairs(pred_b_1, pred_b_2), gold)


def choose_temperature(
    val_a1: np.ndarray,
    val_a2: np.ndarray,
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    val_gold: np.ndarray,
) -> tuple[float, dict[str, float]]:
    best: tuple[float, dict[str, float]] | None = None
    for tau in TEMPERATURES:
        p1 = anchor_transport(val_a1, a_anchor, b_anchor, tau)
        p2 = anchor_transport(val_a2, a_anchor, b_anchor, tau)
        m = score_transport(p1, p2, val_gold)
        if best is None or m["spearman"] > best[1]["spearman"]:
            best = (tau, m)
    assert best is not None
    return best


def choose_ridge(
    val_a1: np.ndarray,
    val_a2: np.ndarray,
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    val_gold: np.ndarray,
) -> tuple[float, Ridge, dict[str, float], float]:
    best = None
    for alpha in RIDGE_ALPHAS:
        t0 = time.perf_counter()
        model = Ridge(alpha=alpha, fit_intercept=True)
        model.fit(a_anchor, b_anchor)
        train_seconds = time.perf_counter() - t0
        p1 = model.predict(val_a1)
        p2 = model.predict(val_a2)
        m = score_transport(p1, p2, val_gold)
        candidate = (alpha, model, m, train_seconds)
        if best is None or m["spearman"] > best[2]["spearman"]:
            best = candidate
    assert best is not None
    return best


def fraction_recovered(score: float, a_score: float, b_score: float) -> float | None:
    denom = b_score - a_score
    if abs(denom) < 1e-12:
        return None
    return float((score - a_score) / denom)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", nargs="+", type=int, default=[8, 16, 32, 64, 128, 256])
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=Path("pontifex-stsb-transport.json"))
    args = ap.parse_args()

    ds = load_dataset(DATASET)
    train1, train2, _ = split_sentences(ds["train"])
    val1, val2, val_gold = split_sentences(ds["validation"])
    test1, test2, test_gold = split_sentences(ds["test"])

    eval_sentence_set = set(val1) | set(val2) | set(test1) | set(test2)
    raw_train_candidates = unique_in_order(train1 + train2)
    anchor_candidates = [s for s in raw_train_candidates if s not in eval_sentence_set]
    excluded_exact_overlap = len(raw_train_candidates) - len(anchor_candidates)

    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(len(anchor_candidates))
    anchor_candidates = [anchor_candidates[i] for i in perm]

    budgets = sorted({int(k) for k in args.budgets if 1 < int(k) <= len(anchor_candidates)})
    if not budgets:
        raise RuntimeError("no valid budgets")

    # Encode exactly the union needed by the experiment. B embeddings for test are
    # present only to compute the oracle ceiling and diagnostics; they are not
    # referenced by any fitting function.
    all_texts = unique_in_order(anchor_candidates[: max(budgets)] + val1 + val2 + test1 + test2)
    emb = encode_all(all_texts, args.cache)
    idx = emb.lookup()

    val_a1, val_a2 = gather(emb.a, idx, val1), gather(emb.a, idx, val2)
    val_b1, val_b2 = gather(emb.b, idx, val1), gather(emb.b, idx, val2)
    test_a1, test_a2 = gather(emb.a, idx, test1), gather(emb.a, idx, test2)
    test_b1, test_b2 = gather(emb.b, idx, test1), gather(emb.b, idx, test2)

    a_test_metrics = correlations(cosine_pairs(test_a1, test_a2), test_gold)
    b_test_metrics = correlations(cosine_pairs(test_b1, test_b2), test_gold)
    a_val_metrics = correlations(cosine_pairs(val_a1, val_a2), val_gold)
    b_val_metrics = correlations(cosine_pairs(val_b1, val_b2), val_gold)

    rows = []
    for k in budgets:
        anchors = anchor_candidates[:k]
        a_anchor = gather(emb.a, idx, anchors)
        b_anchor = gather(emb.b, idx, anchors)

        # Pontifex anchor transport: select one scalar temperature on validation.
        tau, pont_val = choose_temperature(val_a1, val_a2, a_anchor, b_anchor, val_gold)
        t0 = time.perf_counter()
        pont_test_1 = anchor_transport(test_a1, a_anchor, b_anchor, tau)
        pont_test_2 = anchor_transport(test_a2, a_anchor, b_anchor, tau)
        pont_infer_seconds = time.perf_counter() - t0
        pont_test = score_transport(pont_test_1, pont_test_2, test_gold)

        # Same-budget shuffled correspondence negative control.
        shuffled = np.arange(k)
        rng_k = np.random.default_rng(args.seed + k)
        rng_k.shuffle(shuffled)
        shuffled_b = b_anchor[shuffled]
        shuffled_tau, shuffled_val = choose_temperature(
            val_a1, val_a2, a_anchor, shuffled_b, val_gold
        )
        shuffled_test = score_transport(
            anchor_transport(test_a1, a_anchor, shuffled_b, shuffled_tau),
            anchor_transport(test_a2, a_anchor, shuffled_b, shuffled_tau),
            test_gold,
        )

        # Rectangular Procrustes: no task-label hyperparameter.
        t0 = time.perf_counter()
        w_proc = fit_procrustes(a_anchor, b_anchor)
        proc_train_seconds = time.perf_counter() - t0
        t0 = time.perf_counter()
        proc_test_1 = apply_centered_map(test_a1, a_anchor, b_anchor, w_proc)
        proc_test_2 = apply_centered_map(test_a2, a_anchor, b_anchor, w_proc)
        proc_infer_seconds = time.perf_counter() - t0
        proc_test = score_transport(proc_test_1, proc_test_2, test_gold)
        proc_val = score_transport(
            apply_centered_map(val_a1, a_anchor, b_anchor, w_proc),
            apply_centered_map(val_a2, a_anchor, b_anchor, w_proc),
            val_gold,
        )

        # Multi-output Ridge: alpha selected only on validation.
        alpha, ridge, ridge_val, ridge_train_seconds = choose_ridge(
            val_a1, val_a2, a_anchor, b_anchor, val_gold
        )
        t0 = time.perf_counter()
        ridge_test_1 = ridge.predict(test_a1)
        ridge_test_2 = ridge.predict(test_a2)
        ridge_infer_seconds = time.perf_counter() - t0
        ridge_test = score_transport(ridge_test_1, ridge_test_2, test_gold)

        a_s = a_test_metrics["spearman"]
        b_s = b_test_metrics["spearman"]
        rows.append(
            {
                "shared_correspondences_k": k,
                "anchors_sha256": sha256_lines(anchors),
                "validation_selection": {
                    "pontifex_temperature": tau,
                    "pontifex": pont_val,
                    "shuffled_temperature": shuffled_tau,
                    "shuffled": shuffled_val,
                    "ridge_alpha": alpha,
                    "ridge": ridge_val,
                    "procrustes": proc_val,
                },
                "test": {
                    "A_only": a_test_metrics,
                    "B_oracle": b_test_metrics,
                    "Pontifex_anchor_transport": pont_test,
                    "Procrustes": proc_test,
                    "Ridge": ridge_test,
                    "shuffled_correspondence": shuffled_test,
                },
                "fraction_of_B_utility_recovered_spearman": {
                    "Pontifex_anchor_transport": fraction_recovered(
                        pont_test["spearman"], a_s, b_s
                    ),
                    "Procrustes": fraction_recovered(proc_test["spearman"], a_s, b_s),
                    "Ridge": fraction_recovered(ridge_test["spearman"], a_s, b_s),
                    "shuffled_correspondence": fraction_recovered(
                        shuffled_test["spearman"], a_s, b_s
                    ),
                },
                "cost": {
                    "Pontifex_anchor_transport": {
                        "fit_labels": 0,
                        "stored_anchor_floats": int(k * (emb.a.shape[1] + emb.b.shape[1])),
                        "trainable_parameters": 1,
                        "selected_scalar": "temperature",
                        "test_pair_inference_seconds": pont_infer_seconds,
                    },
                    "Procrustes": {
                        "fit_labels": 0,
                        "map_parameters": int(w_proc.size),
                        "fit_seconds": proc_train_seconds,
                        "test_pair_inference_seconds": proc_infer_seconds,
                    },
                    "Ridge": {
                        "fit_labels": 0,
                        "map_parameters": int(ridge.coef_.size + ridge.intercept_.size),
                        "fit_seconds_selected_alpha": ridge_train_seconds,
                        "test_pair_inference_seconds": ridge_infer_seconds,
                    },
                },
            }
        )

    result = {
        "experiment": "Pontifex external STS-B latent-space transport benchmark",
        "classification": "real benchmark result",
        "dataset": {
            "id": DATASET,
            "train_rows": len(ds["train"]),
            "validation_rows": len(ds["validation"]),
            "test_rows": len(ds["test"]),
            "train_fingerprint": getattr(ds["train"], "_fingerprint", None),
            "validation_fingerprint": getattr(ds["validation"], "_fingerprint", None),
            "test_fingerprint": getattr(ds["test"], "_fingerprint", None),
            "primary_metric": "Spearman correlation of cosine similarity",
            "secondary_metric": "Pearson correlation of cosine similarity",
        },
        "spaces": {
            "A": MODEL_A,
            "B": MODEL_B,
            "pretraining_overlap_between_A_B": "possible",
            "benchmark_pretraining_overlap_A": "unknown",
            "benchmark_pretraining_overlap_B": "unknown",
            "interpretation": (
                "Possible shared pretraining knowledge is part of the method premise, "
                "not adapter leakage. The adapter may only use unlabeled train-split "
                "A<->B correspondences."
            ),
        },
        "leakage_audit": {
            "status": "PASS",
            "adapter_fit_uses": "unlabeled train-split sentences only",
            "train_candidates_before_eval_overlap_filter": len(raw_train_candidates),
            "train_candidates_after_filter": len(anchor_candidates),
            "exact_train_sentences_excluded_for_validation_or_test_overlap": excluded_exact_overlap,
            "validation_use": "hyperparameter selection only",
            "test_use": "final scoring only",
            "test_labels_used_for_fit_or_selection": False,
            "B_test_embeddings_use": "oracle ceiling and diagnostics only",
            "anchor_pool_sha256": sha256_lines(anchor_candidates),
            "validation_pairs_sha256": sha256_lines(
                f"{a}\t{b}\t{y:.8f}" for a, b, y in zip(val1, val2, val_gold)
            ),
            "test_pairs_sha256": sha256_lines(
                f"{a}\t{b}\t{y:.8f}" for a, b, y in zip(test1, test2, test_gold)
            ),
            "seed": args.seed,
        },
        "fixed_protocol": {
            "budgets": budgets,
            "temperatures": TEMPERATURES,
            "ridge_alphas": RIDGE_ALPHAS,
            "anchor_order": "deterministic RNG permutation of leakage-filtered train sentences",
            "selection_rule": "maximize validation Spearman; test inspected only after selection",
        },
        "oracle_context": {
            "validation": {"A_only": a_val_metrics, "B_oracle": b_val_metrics},
            "test": {"A_only": a_test_metrics, "B_oracle": b_test_metrics},
        },
        "results_by_budget": rows,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
