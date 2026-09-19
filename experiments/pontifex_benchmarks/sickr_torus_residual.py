# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "datasets>=3.0,<4.0",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "scipy>=1.14",
#   "sentence-transformers>=5.0",
# ]
# ///
"""Prospective SICK-R benchmark for Pontifex Torus coarse+local transport.

The transport budget is exactly K unlabeled A<->B train-split sentence
correspondences. No SICK relatedness label is used for transport fitting or
hyperparameter selection. Torus hyperparameters are selected by strict
cross-fitting within those K correspondence pairs; validation and test are
never used for transport selection.
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
from sklearn.linear_model import RidgeCV

DATASET = "RobZamp/sick"
MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_B = "sentence-transformers/all-mpnet-base-v2"
TAUS = (0.02, 0.05, 0.10, 0.20, 0.40, 0.80)
LAMBDAS = (0.25, 0.50, 1.00, 1.50)
RIDGE_ALPHAS = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)
SELECTION_FOLDS = 4


def normalized_text(x: str) -> str:
    return " ".join(str(x).strip().split())


def sha256_lines(lines: Iterable[str]) -> str:
    h = hashlib.sha256()
    for line in lines:
        h.update(str(line).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def unique_in_order(xs: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        t = normalized_text(x)
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def l2norm(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def cosine_pairs(x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
    return np.sum(l2norm(x1) * l2norm(x2), axis=1)


def row_cosine(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.sum(l2norm(x) * l2norm(y), axis=1)


def corr(scores: np.ndarray, gold: np.ndarray) -> dict[str, float]:
    return {
        "pearson": float(pearsonr(scores, gold).statistic),
        "spearman": float(spearmanr(scores, gold).statistic),
    }


def task_metrics(x1: np.ndarray, x2: np.ndarray, gold: np.ndarray) -> dict[str, float]:
    return corr(cosine_pairs(x1, x2), gold)


def pair_geometry_metrics(
    pred1: np.ndarray,
    pred2: np.ndarray,
    true_b1: np.ndarray,
    true_b2: np.ndarray,
) -> dict[str, float]:
    pred = cosine_pairs(pred1, pred2)
    true = cosine_pairs(true_b1, true_b2)
    return {
        "rmse": float(np.sqrt(np.mean((pred - true) ** 2))),
        "spearman": float(spearmanr(pred, true).statistic),
    }


def split_rows(split) -> tuple[list[str], list[str], np.ndarray]:
    s1 = [normalized_text(x) for x in split["sentence_A"]]
    s2 = [normalized_text(x) for x in split["sentence_B"]]
    y = np.asarray(split["relatedness_score"], dtype=np.float64)
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
    a0 = a_anchor - a_anchor.mean(axis=0, keepdims=True)
    b0 = b_anchor - b_anchor.mean(axis=0, keepdims=True)
    u, _, vt = np.linalg.svd(a0.T @ b0, full_matrices=False)
    return (u @ vt).astype(np.float32)


def apply_coarse(
    x: np.ndarray,
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    w: np.ndarray,
) -> np.ndarray:
    return (x - a_anchor.mean(axis=0, keepdims=True)) @ w + b_anchor.mean(
        axis=0, keepdims=True
    )


def softmax_rows(z: np.ndarray) -> np.ndarray:
    z = z - np.max(z, axis=1, keepdims=True)
    ez = np.exp(z)
    return ez / np.maximum(ez.sum(axis=1, keepdims=True), 1e-12)


def predict_residual(
    x_a: np.ndarray,
    a_anchor: np.ndarray,
    residual_anchor: np.ndarray,
    tau: float,
) -> np.ndarray:
    sims = l2norm(x_a) @ l2norm(a_anchor).T
    return softmax_rows(sims / tau) @ residual_anchor


def choose_residual_hparams_pseudo_loo(
    a_anchor: np.ndarray,
    coarse_anchor: np.ndarray,
    target_b: np.ndarray,
) -> tuple[float, float, float]:
    """Legacy diagnostic: excludes self only from residual weights, not coarse fit."""
    residual = target_b - coarse_anchor
    sims = l2norm(a_anchor) @ l2norm(a_anchor).T
    best: tuple[float, float, float] | None = None
    for tau in TAUS:
        logits = sims / tau
        np.fill_diagonal(logits, -1e9)
        weights = softmax_rows(logits)
        pred_residual = weights @ residual
        for lam in LAMBDAS:
            pred_b = coarse_anchor + lam * pred_residual
            loss = float(np.mean(1.0 - row_cosine(pred_b, target_b)))
            candidate = (tau, lam, loss)
            if best is None or loss < best[2]:
                best = candidate
    assert best is not None
    return best


def choose_residual_hparams_crossfit(
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    folds: int = SELECTION_FOLDS,
) -> tuple[float, float, float]:
    """Choose tau/lambda by strict outer cross-fit using only the K anchors.

    Every held-out anchor is excluded from both the Procrustes coarse map and
    the residual basis used to predict it. Fold identity is deterministic from
    the already-seeded anchor order, so no validation/test information enters
    selection.
    """
    n = len(a_anchor)
    if n < folds:
        raise ValueError(f"need at least {folds} anchors for {folds}-fold selection")

    losses = {(tau, lam): [] for tau in TAUS for lam in LAMBDAS}
    fold_id = np.arange(n, dtype=np.int64) % folds

    for fold in range(folds):
        held = fold_id == fold
        train = ~held
        a_train, b_train = a_anchor[train], b_anchor[train]
        a_held, b_held = a_anchor[held], b_anchor[held]

        w_fold = fit_procrustes(a_train, b_train)
        coarse_train = apply_coarse(a_train, a_train, b_train, w_fold)
        residual_train = b_train - coarse_train
        coarse_held = apply_coarse(a_held, a_train, b_train, w_fold)
        sims = l2norm(a_held) @ l2norm(a_train).T

        for tau in TAUS:
            pred_residual = softmax_rows(sims / tau) @ residual_train
            for lam in LAMBDAS:
                pred_b = coarse_held + lam * pred_residual
                losses[(tau, lam)].extend(
                    (1.0 - row_cosine(pred_b, b_held)).astype(float).tolist()
                )

    best: tuple[float, float, float] | None = None
    for tau in TAUS:
        for lam in LAMBDAS:
            loss = float(np.mean(losses[(tau, lam)]))
            candidate = (tau, lam, loss)
            if best is None or loss < best[2]:
                best = candidate
    assert best is not None
    return best


def torus_predict(
    x_a: np.ndarray,
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    w: np.ndarray,
    tau: float,
    lam: float,
    *,
    residual_override: np.ndarray | None = None,
) -> np.ndarray:
    coarse_anchor = apply_coarse(a_anchor, a_anchor, b_anchor, w)
    residual = b_anchor - coarse_anchor
    if residual_override is not None:
        residual = residual_override
    coarse_x = apply_coarse(x_a, a_anchor, b_anchor, w)
    return coarse_x + lam * predict_residual(x_a, a_anchor, residual, tau)


def method_eval(
    pred1: np.ndarray,
    pred2: np.ndarray,
    true_b1: np.ndarray,
    true_b2: np.ndarray,
    gold: np.ndarray,
    pred_unique: np.ndarray,
    true_b_unique: np.ndarray,
) -> dict[str, object]:
    return {
        "task": task_metrics(pred1, pred2, gold),
        "B_coordinate_alignment_mean_cosine": float(
            np.mean(row_cosine(pred_unique, true_b_unique))
        ),
        "B_pair_geometry": pair_geometry_metrics(pred1, pred2, true_b1, true_b2),
    }


def fraction_recovered(score: float, a_score: float, b_score: float) -> float | None:
    d = b_score - a_score
    if abs(d) < 1e-12:
        return None
    return float((score - a_score) / d)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", nargs="+", type=int, default=[8, 16, 32, 64, 128, 256])
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=Path("pontifex-sickr-torus-residual.json"))
    args = ap.parse_args()

    ds = load_dataset(DATASET, trust_remote_code=True)
    train1, train2, _ = split_rows(ds["train"])
    val1, val2, val_gold = split_rows(ds["validation"])
    test1, test2, test_gold = split_rows(ds["test"])

    eval_sentences = set(val1) | set(val2) | set(test1) | set(test2)
    raw_candidates = unique_in_order(train1 + train2)
    anchor_candidates = [t for t in raw_candidates if t not in eval_sentences]
    excluded = len(raw_candidates) - len(anchor_candidates)

    rng = np.random.default_rng(args.seed)
    order = rng.permutation(len(anchor_candidates))
    anchor_candidates = [anchor_candidates[i] for i in order]
    budgets = sorted({k for k in args.budgets if k >= SELECTION_FOLDS and k <= len(anchor_candidates)})
    if not budgets:
        raise RuntimeError("no valid budgets")

    val_unique = unique_in_order(val1 + val2)
    test_unique = unique_in_order(test1 + test2)
    all_texts = unique_in_order(anchor_candidates[: max(budgets)] + val_unique + test_unique)
    emb = encode_all(all_texts, args.cache)
    idx = emb.lookup()

    val_a1, val_a2 = gather(emb.a, idx, val1), gather(emb.a, idx, val2)
    val_b1, val_b2 = gather(emb.b, idx, val1), gather(emb.b, idx, val2)
    test_a1, test_a2 = gather(emb.a, idx, test1), gather(emb.a, idx, test2)
    test_b1, test_b2 = gather(emb.b, idx, test1), gather(emb.b, idx, test2)
    val_au, val_bu = gather(emb.a, idx, val_unique), gather(emb.b, idx, val_unique)
    test_au, test_bu = gather(emb.a, idx, test_unique), gather(emb.b, idx, test_unique)

    a_val = task_metrics(val_a1, val_a2, val_gold)
    b_val = task_metrics(val_b1, val_b2, val_gold)
    a_test = task_metrics(test_a1, test_a2, test_gold)
    b_test = task_metrics(test_b1, test_b2, test_gold)

    rows: list[dict[str, object]] = []
    for k in budgets:
        anchors = anchor_candidates[:k]
        a_anchor = gather(emb.a, idx, anchors)
        b_anchor = gather(emb.b, idx, anchors)

        t_fit = time.perf_counter()
        w = fit_procrustes(a_anchor, b_anchor)
        coarse_anchor = apply_coarse(a_anchor, a_anchor, b_anchor, w)
        legacy_tau, legacy_lam, legacy_loss = choose_residual_hparams_pseudo_loo(
            a_anchor, coarse_anchor, b_anchor
        )
        tau, lam, crossfit_loss = choose_residual_hparams_crossfit(a_anchor, b_anchor)
        fit_seconds = time.perf_counter() - t_fit

        t0 = time.perf_counter()
        proc_val1 = apply_coarse(val_a1, a_anchor, b_anchor, w)
        proc_val2 = apply_coarse(val_a2, a_anchor, b_anchor, w)
        proc_valu = apply_coarse(val_au, a_anchor, b_anchor, w)
        proc_test1 = apply_coarse(test_a1, a_anchor, b_anchor, w)
        proc_test2 = apply_coarse(test_a2, a_anchor, b_anchor, w)
        proc_testu = apply_coarse(test_au, a_anchor, b_anchor, w)
        proc_infer_seconds = time.perf_counter() - t0

        t0 = time.perf_counter()
        torus_val1 = torus_predict(val_a1, a_anchor, b_anchor, w, tau, lam)
        torus_val2 = torus_predict(val_a2, a_anchor, b_anchor, w, tau, lam)
        torus_valu = torus_predict(val_au, a_anchor, b_anchor, w, tau, lam)
        torus_test1 = torus_predict(test_a1, a_anchor, b_anchor, w, tau, lam)
        torus_test2 = torus_predict(test_a2, a_anchor, b_anchor, w, tau, lam)
        torus_testu = torus_predict(test_au, a_anchor, b_anchor, w, tau, lam)
        torus_infer_seconds = time.perf_counter() - t0

        residual = b_anchor - coarse_anchor
        residual_perm = np.arange(k)
        np.random.default_rng(args.seed + 10_000 + k).shuffle(residual_perm)
        shuffled_residual = residual[residual_perm]
        sr_test1 = torus_predict(
            test_a1, a_anchor, b_anchor, w, tau, lam, residual_override=shuffled_residual
        )
        sr_test2 = torus_predict(
            test_a2, a_anchor, b_anchor, w, tau, lam, residual_override=shuffled_residual
        )
        sr_testu = torus_predict(
            test_au, a_anchor, b_anchor, w, tau, lam, residual_override=shuffled_residual
        )

        b_perm = np.arange(k)
        np.random.default_rng(args.seed + 20_000 + k).shuffle(b_perm)
        b_shuf = b_anchor[b_perm]
        w_shuf = fit_procrustes(a_anchor, b_shuf)
        tau_shuf, lam_shuf, _ = choose_residual_hparams_crossfit(a_anchor, b_shuf)
        fs_test1 = torus_predict(test_a1, a_anchor, b_shuf, w_shuf, tau_shuf, lam_shuf)
        fs_test2 = torus_predict(test_a2, a_anchor, b_shuf, w_shuf, tau_shuf, lam_shuf)
        fs_testu = torus_predict(test_au, a_anchor, b_shuf, w_shuf, tau_shuf, lam_shuf)

        ridge_t0 = time.perf_counter()
        ridge = RidgeCV(alphas=RIDGE_ALPHAS, fit_intercept=True)
        ridge.fit(a_anchor, b_anchor)
        ridge_fit_seconds = time.perf_counter() - ridge_t0
        ridge_test1 = ridge.predict(test_a1)
        ridge_test2 = ridge.predict(test_a2)
        ridge_testu = ridge.predict(test_au)

        methods_test = {
            "Procrustes_coarse": method_eval(
                proc_test1, proc_test2, test_b1, test_b2, test_gold, proc_testu, test_bu
            ),
            "Pontifex_Torus_residual": method_eval(
                torus_test1, torus_test2, test_b1, test_b2, test_gold, torus_testu, test_bu
            ),
            "shuffled_residual_control": method_eval(
                sr_test1, sr_test2, test_b1, test_b2, test_gold, sr_testu, test_bu
            ),
            "fully_shuffled_correspondence_control": method_eval(
                fs_test1, fs_test2, test_b1, test_b2, test_gold, fs_testu, test_bu
            ),
            "RidgeCV": method_eval(
                ridge_test1, ridge_test2, test_b1, test_b2, test_gold, ridge_testu, test_bu
            ),
        }
        methods_val = {
            "Procrustes_coarse": method_eval(
                proc_val1, proc_val2, val_b1, val_b2, val_gold, proc_valu, val_bu
            ),
            "Pontifex_Torus_residual": method_eval(
                torus_val1, torus_val2, val_b1, val_b2, val_gold, torus_valu, val_bu
            ),
        }

        a_p = a_test["pearson"]
        b_p = b_test["pearson"]
        rows.append(
            {
                "shared_correspondences_k": k,
                "anchors_sha256": sha256_lines(anchors),
                "selected_without_task_labels": {
                    "torus_tau": tau,
                    "torus_lambda": lam,
                    "torus_anchor_crossfit_cosine_loss": crossfit_loss,
                    "selection_folds": SELECTION_FOLDS,
                    "ridge_alpha": float(ridge.alpha_),
                },
                "selection_audit": {
                    "legacy_pseudo_loo_not_used_for_model_selection": {
                        "tau": legacy_tau,
                        "lambda": legacy_lam,
                        "optimistic_anchor_cosine_loss": legacy_loss,
                    },
                    "strict_crossfit_used_for_model_selection": {
                        "tau": tau,
                        "lambda": lam,
                        "anchor_cosine_loss": crossfit_loss,
                    },
                },
                "validation_diagnostic": methods_val,
                "test": methods_test,
                "fraction_of_B_utility_recovered_official_pearson": {
                    name: fraction_recovered(float(payload["task"]["pearson"]), a_p, b_p)
                    for name, payload in methods_test.items()
                },
                "incremental_torus_over_same_procrustes": {
                    "official_pearson_delta": float(
                        methods_test["Pontifex_Torus_residual"]["task"]["pearson"]
                        - methods_test["Procrustes_coarse"]["task"]["pearson"]
                    ),
                    "B_coordinate_cosine_delta": float(
                        methods_test["Pontifex_Torus_residual"]["B_coordinate_alignment_mean_cosine"]
                        - methods_test["Procrustes_coarse"]["B_coordinate_alignment_mean_cosine"]
                    ),
                    "B_pair_geometry_rmse_delta": float(
                        methods_test["Pontifex_Torus_residual"]["B_pair_geometry"]["rmse"]
                        - methods_test["Procrustes_coarse"]["B_pair_geometry"]["rmse"]
                    ),
                    "B_pair_geometry_spearman_delta": float(
                        methods_test["Pontifex_Torus_residual"]["B_pair_geometry"]["spearman"]
                        - methods_test["Procrustes_coarse"]["B_pair_geometry"]["spearman"]
                    ),
                },
                "cost": {
                    "task_labels_used_for_transport_fit_or_selection": 0,
                    "Procrustes_coarse": {
                        "map_floats": int(w.size),
                        "fit_plus_torus_selection_seconds": fit_seconds,
                        "test_inference_seconds": proc_infer_seconds,
                    },
                    "Pontifex_Torus_residual_increment": {
                        "stored_residual_floats": int(residual.size),
                        "selected_scalars": 2,
                        "test_inference_seconds_including_coarse": torus_infer_seconds,
                    },
                    "RidgeCV": {
                        "map_parameters": int(ridge.coef_.size + ridge.intercept_.size),
                        "fit_seconds": ridge_fit_seconds,
                    },
                },
            }
        )

    result = {
        "experiment": "Pontifex Torus prospective SICK-R coarse+local residual transport benchmark",
        "classification": "real benchmark result / prospective cross-benchmark replication",
        "protocol_file": "experiments/pontifex_benchmarks/PROTOCOL-SICKR-TORUS-RESIDUAL-2026-09-19.md",
        "dataset": {
            "id": DATASET,
            "benchmark": "SICK / SemEval-2014 Task 1 semantic relatedness",
            "train_rows": len(ds["train"]),
            "validation_rows": len(ds["validation"]),
            "test_rows": len(ds["test"]),
            "train_fingerprint": getattr(ds["train"], "_fingerprint", None),
            "validation_fingerprint": getattr(ds["validation"], "_fingerprint", None),
            "test_fingerprint": getattr(ds["test"], "_fingerprint", None),
            "official_primary_metric": "Pearson correlation of cosine similarity with relatedness_score",
            "secondary_metric": "Spearman correlation",
        },
        "spaces": {
            "A": MODEL_A,
            "B": MODEL_B,
            "pretraining_overlap_between_A_B": "possible",
            "benchmark_pretraining_overlap_A": "unknown",
            "benchmark_pretraining_overlap_B": "unknown",
        },
        "leakage_audit": {
            "status": "PASS",
            "adapter_fit_and_hparam_selection": "same K unlabeled train A<->B pairs only; Torus selector uses strict 4-fold outer cross-fit",
            "task_labels_used_for_transport_fit_or_selection": 0,
            "raw_unique_train_sentence_candidates": len(raw_candidates),
            "eligible_train_candidates_after_exact_eval_overlap_filter": len(anchor_candidates),
            "exact_train_sentences_excluded_due_to_validation_or_test_overlap": excluded,
            "validation_use": "diagnostic only; not used to select transport hyperparameters",
            "test_use": "final scoring and B-oracle diagnostics only",
            "test_labels_used_for_fit_or_selection": False,
            "B_test_embeddings_use": "evaluation oracle only",
            "anchor_pool_sha256": sha256_lines(anchor_candidates),
            "validation_pairs_sha256": sha256_lines(
                f"{a}\t{b}\t{y:.8f}" for a, b, y in zip(val1, val2, val_gold)
            ),
            "test_pairs_sha256": sha256_lines(
                f"{a}\t{b}\t{y:.8f}" for a, b, y in zip(test1, test2, test_gold)
            ),
            "seed": args.seed,
        },
        "split_contract": {
            "D_assembly": "not used in this benchmark; frozen external encoders",
            "D_student": "eligible SICK train anchor pool only",
            "D_val": "diagnostic only",
            "D_test": "final scoring only",
        },
        "fixed_protocol": {
            "budgets": budgets,
            "torus_tau_grid": TAUS,
            "torus_lambda_grid": LAMBDAS,
            "ridge_alpha_grid": RIDGE_ALPHAS,
            "torus_selection": "deterministic 4-fold outer cross-fitted B-coordinate cosine loss; held-out fold excluded from both Procrustes fit and residual basis",
            "selection_folds": SELECTION_FOLDS,
            "fold_assignment": "anchor index modulo 4 after deterministic seeded anchor permutation",
            "legacy_pseudo_loo": "diagnostic only; prohibited from model selection",
            "ridge_selection": "RidgeCV generalized leave-one-out on same K A<->B anchors",
            "anchor_order": "deterministic RNG permutation after exact eval-overlap removal",
        },
        "oracle_context": {
            "validation": {"A_only": a_val, "B_oracle": b_val},
            "test": {"A_only": a_test, "B_oracle": b_test},
        },
        "results_by_budget": rows,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
