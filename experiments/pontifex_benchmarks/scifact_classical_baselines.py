# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.28",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "sentence-transformers>=5.0",
#   "huggingface-hub>=0.34",
# ]
# ///
"""Information-matched classical A->B transport baselines on BEIR/SciFact.

This is a prospective follow-up to the frozen Pontifex SciFact transport run.
All hyperparameters are selected from held-out TRAIN-query A/B coordinates only;
SciFact qrels are used only after each K-specific model is frozen.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import warnings
from pathlib import Path

import numpy as np
from huggingface_hub import model_info
from sklearn.cross_decomposition import CCA, PLSRegression
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import Ridge

from scifact_transport import (
    BEIR_MD5,
    BEIR_URL,
    MODEL_A,
    MODEL_B,
    encode_or_load,
    ensure_dataset,
    fraction_recovered,
    load_data,
    retrieval_metrics,
    row_cosine,
    sha256_lines,
)

SEED = 20260919
COMPONENT_GRID = (2, 4, 8, 16)
RFF_GAMMAS = (0.25, 0.5, 1.0)
RFF_WIDTHS = (32, 64, 128, 256)
RFF_ALPHAS = (0.01, 0.1, 1.0, 10.0)
EXPECTED_STUDENT_SHA = "bd5775940da2cb20d0ec5ee5ec4c9e35d871f82f12c0ff87e1955e38bd69ccf5"
EXPECTED_VAL_SHA = "7a699f93186bd3b8c6042c8941b045ed8197438fceb396b0d7178af34e9c349c"
EXPECTED_TEST_SHA = "c307ee1faa37715704375e5c59a071b0c579b3114bedcbf263d43111a2f15ebf"
EXPECTED_CORPUS_SHA = "bcb266241b6c749fe993de0353d1ce95cc3b9fbd47b86d356ba54acab09ccfd4"


def coord_loss(pred: np.ndarray, target: np.ndarray) -> float:
    values = 1.0 - row_cosine(np.asarray(pred, dtype=np.float32), target)
    if not np.all(np.isfinite(values)):
        return math.inf
    return float(np.mean(values))


def component_candidates(k: int) -> list[int]:
    return [c for c in COMPONENT_GRID if c < k]


def fit_best_cca(
    aa: np.ndarray, bb: np.ndarray, a_val: np.ndarray, b_val: np.ndarray
) -> tuple[CCA, dict, float]:
    best: tuple[float, int, CCA] | None = None
    t0 = time.perf_counter()
    for n_components in component_candidates(len(aa)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = CCA(
                    n_components=n_components,
                    scale=True,
                    max_iter=500,
                    tol=1e-6,
                ).fit(aa, bb)
                loss = coord_loss(model.predict(a_val), b_val)
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue
        candidate = (loss, n_components, model)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        raise RuntimeError("CCA produced no valid candidate")
    elapsed = time.perf_counter() - t0
    return best[2], {"n_components": best[1], "D_val_coordinate_loss": best[0]}, elapsed


def fit_best_pls(
    aa: np.ndarray, bb: np.ndarray, a_val: np.ndarray, b_val: np.ndarray
) -> tuple[PLSRegression, dict, float]:
    best: tuple[float, int, PLSRegression] | None = None
    t0 = time.perf_counter()
    for n_components in component_candidates(len(aa)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = PLSRegression(
                    n_components=n_components,
                    scale=True,
                    max_iter=500,
                    tol=1e-6,
                ).fit(aa, bb)
                loss = coord_loss(model.predict(a_val), b_val)
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue
        candidate = (loss, n_components, model)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        raise RuntimeError("PLS produced no valid candidate")
    elapsed = time.perf_counter() - t0
    return best[2], {"n_components": best[1], "D_val_coordinate_loss": best[0]}, elapsed


def fit_best_rff(
    aa: np.ndarray,
    bb: np.ndarray,
    a_val: np.ndarray,
    b_val: np.ndarray,
    *,
    seed: int,
) -> tuple[RBFSampler, Ridge, dict, float]:
    best: tuple[float, float, int, float, RBFSampler, Ridge] | None = None
    t0 = time.perf_counter()
    for gamma in RFF_GAMMAS:
        for width in RFF_WIDTHS:
            feature_seed = seed + width * 17 + int(gamma * 1000)
            rff = RBFSampler(
                gamma=gamma,
                n_components=width,
                random_state=feature_seed,
            )
            z_train = rff.fit_transform(aa)
            z_val = rff.transform(a_val)
            for alpha in RFF_ALPHAS:
                ridge = Ridge(alpha=alpha, fit_intercept=True).fit(z_train, bb)
                loss = coord_loss(ridge.predict(z_val), b_val)
                candidate = (loss, gamma, width, alpha, rff, ridge)
                if best is None or candidate[0] < best[0]:
                    best = candidate
    if best is None:
        raise RuntimeError("RFF produced no valid candidate")
    elapsed = time.perf_counter() - t0
    return (
        best[4],
        best[5],
        {
            "gamma": best[1],
            "n_components": best[2],
            "ridge_alpha": best[3],
            "D_val_coordinate_loss": best[0],
        },
        elapsed,
    )


def fitted_floats(model: object) -> int:
    total = 0
    for name in ("coef_", "intercept_"):
        value = getattr(model, name, None)
        if value is not None:
            total += int(np.asarray(value).size)
    return total


def rff_storage_floats(rff: RBFSampler, ridge: Ridge) -> dict[str, int]:
    return {
        "random_feature_floats": int(
            np.asarray(rff.random_weights_).size + np.asarray(rff.random_offset_).size
        ),
        "fitted_ridge_floats": fitted_floats(ridge),
    }


def min_k(rows: list[dict], method: str, target: float) -> int | None:
    for row in rows:
        if row["test"][method]["official"]["ndcg_at_10"] >= target:
            return int(row["shared_correspondences_k"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", nargs="+", type=int, default=[16, 32, 64, 128, 256, 512])
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-scifact-classical-baselines.json"))
    args = ap.parse_args()

    root = ensure_dataset(args.cache_dir)
    data = load_data(root)
    train_ids = sorted(data.train_qrels)
    test_ids = sorted(data.test_qrels)
    test_texts = {data.queries[q].strip() for q in test_ids}
    eligible_ids = [q for q in train_ids if data.queries[q].strip() not in test_texts]

    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(len(eligible_ids))
    eligible_ids = [eligible_ids[i] for i in perm]
    cut = max(1, int(math.floor(0.80 * len(eligible_ids))))
    student_ids = eligible_ids[:cut]
    val_ids = eligible_ids[cut:]
    budgets = sorted({k for k in args.budgets if 4 <= k <= len(student_ids)})

    manifests = {
        "student_ids_sha256": sha256_lines(student_ids),
        "validation_ids_sha256": sha256_lines(val_ids),
        "test_ids_sha256": sha256_lines(test_ids),
        "corpus_ids_sha256": sha256_lines(data.corpus_ids),
    }
    expected = {
        "student_ids_sha256": EXPECTED_STUDENT_SHA,
        "validation_ids_sha256": EXPECTED_VAL_SHA,
        "test_ids_sha256": EXPECTED_TEST_SHA,
        "corpus_ids_sha256": EXPECTED_CORPUS_SHA,
    }
    if manifests != expected:
        raise RuntimeError(f"frozen split manifest mismatch: {manifests} != {expected}")

    emb = encode_or_load(data, args.cache_dir / "scifact-minilm-mpnet.npz")
    train_pos = {qid: i for i, qid in enumerate(train_ids)}
    student_idx = np.asarray([train_pos[q] for q in student_ids], dtype=np.int64)
    val_idx = np.asarray([train_pos[q] for q in val_ids], dtype=np.int64)
    a_student, b_student = emb["a_train"][student_idx], emb["b_train"][student_idx]
    a_val, b_val = emb["a_train"][val_idx], emb["b_train"][val_idx]

    # Freeze every K-specific candidate using TRAIN-derived coordinates only.
    frozen: list[dict] = []
    for k in budgets:
        aa, bb = a_student[:k], b_student[:k]
        cca, cca_selection, cca_fit = fit_best_cca(aa, bb, a_val, b_val)
        pls, pls_selection, pls_fit = fit_best_pls(aa, bb, a_val, b_val)
        rff, rff_ridge, rff_selection, rff_fit = fit_best_rff(
            aa, bb, a_val, b_val, seed=args.seed + k * 10000
        )
        frozen.append(
            {
                "k": k,
                "anchor_ids": student_ids[:k],
                "CCA": (cca, cca_selection, cca_fit),
                "PLS": (pls, pls_selection, pls_fit),
                "RFF_Ridge": (rff, rff_ridge, rff_selection, rff_fit),
            }
        )

    # Test labels and true-B test/corpus coordinates are used only after all choices above freeze.
    a_test, b_test = emb["a_test"], emb["b_test"]
    a_docs, b_docs = emb["a_docs"], emb["b_docs"]
    a_official, a_retrieval = retrieval_metrics(data.test_qrels, test_ids, data.corpus_ids, a_test, a_docs)
    b_official, b_retrieval = retrieval_metrics(data.test_qrels, test_ids, data.corpus_ids, b_test, b_docs)
    a_ndcg = a_official["ndcg_at_10"]
    b_ndcg = b_official["ndcg_at_10"]

    rows: list[dict] = []
    for item in frozen:
        k = item["k"]
        anchor_ids = item["anchor_ids"]
        test_payload: dict[str, dict] = {}
        cost_payload: dict[str, dict] = {}
        selection_payload: dict[str, dict] = {}

        cca, cca_selection, cca_fit = item["CCA"]
        t0 = time.perf_counter()
        cca_q = np.asarray(cca.predict(a_test), dtype=np.float32)
        cca_d = np.asarray(cca.predict(a_docs), dtype=np.float32)
        cca_map = time.perf_counter() - t0
        cca_official, cca_retrieval = retrieval_metrics(data.test_qrels, test_ids, data.corpus_ids, cca_q, cca_d)
        test_payload["CCA"] = {
            "official": cca_official,
            "fraction_of_B_utility_recovered_ndcg10": fraction_recovered(cca_official["ndcg_at_10"], a_ndcg, b_ndcg),
            "B_query_coordinate_mean_cosine": float(np.mean(row_cosine(cca_q, b_test))),
            "B_document_coordinate_mean_cosine": float(np.mean(row_cosine(cca_d, b_docs))),
        }
        selection_payload["CCA"] = cca_selection
        cost_payload["CCA"] = {
            "fitted_floats": fitted_floats(cca),
            "fit_plus_validation_selection_seconds": cca_fit,
            "map_test_queries_plus_corpus_seconds": cca_map,
            "retrieval_seconds": cca_retrieval,
        }

        pls, pls_selection, pls_fit = item["PLS"]
        t0 = time.perf_counter()
        pls_q = np.asarray(pls.predict(a_test), dtype=np.float32)
        pls_d = np.asarray(pls.predict(a_docs), dtype=np.float32)
        pls_map = time.perf_counter() - t0
        pls_official, pls_retrieval = retrieval_metrics(data.test_qrels, test_ids, data.corpus_ids, pls_q, pls_d)
        test_payload["PLS"] = {
            "official": pls_official,
            "fraction_of_B_utility_recovered_ndcg10": fraction_recovered(pls_official["ndcg_at_10"], a_ndcg, b_ndcg),
            "B_query_coordinate_mean_cosine": float(np.mean(row_cosine(pls_q, b_test))),
            "B_document_coordinate_mean_cosine": float(np.mean(row_cosine(pls_d, b_docs))),
        }
        selection_payload["PLS"] = pls_selection
        cost_payload["PLS"] = {
            "fitted_floats": fitted_floats(pls),
            "fit_plus_validation_selection_seconds": pls_fit,
            "map_test_queries_plus_corpus_seconds": pls_map,
            "retrieval_seconds": pls_retrieval,
        }

        rff, rff_ridge, rff_selection, rff_fit = item["RFF_Ridge"]
        t0 = time.perf_counter()
        rff_q = rff_ridge.predict(rff.transform(a_test)).astype(np.float32)
        rff_d = rff_ridge.predict(rff.transform(a_docs)).astype(np.float32)
        rff_map = time.perf_counter() - t0
        rff_official, rff_retrieval = retrieval_metrics(data.test_qrels, test_ids, data.corpus_ids, rff_q, rff_d)
        test_payload["RFF_Ridge"] = {
            "official": rff_official,
            "fraction_of_B_utility_recovered_ndcg10": fraction_recovered(rff_official["ndcg_at_10"], a_ndcg, b_ndcg),
            "B_query_coordinate_mean_cosine": float(np.mean(row_cosine(rff_q, b_test))),
            "B_document_coordinate_mean_cosine": float(np.mean(row_cosine(rff_d, b_docs))),
        }
        selection_payload["RFF_Ridge"] = rff_selection
        cost_payload["RFF_Ridge"] = {
            **rff_storage_floats(rff, rff_ridge),
            "fit_plus_validation_selection_seconds": rff_fit,
            "map_test_queries_plus_corpus_seconds": rff_map,
            "retrieval_seconds": rff_retrieval,
        }

        rows.append(
            {
                "shared_correspondences_k": k,
                "anchor_ids_sha256": sha256_lines(anchor_ids),
                "shared_text_bytes": int(sum(len(data.queries[q].encode("utf-8")) for q in anchor_ids)),
                "paired_embedding_supervision_bytes_float32": int(k * (a_student.shape[1] + b_student.shape[1]) * 4),
                "selection": selection_payload,
                "test": test_payload,
                "cost": cost_payload,
            }
        )

    midpoint = a_ndcg + 0.50 * (b_ndcg - a_ndcg)
    p90 = a_ndcg + 0.90 * (b_ndcg - a_ndcg)
    methods = ("CCA", "PLS", "RFF_Ridge")
    payload = {
        "experiment": "Pontifex BEIR/SciFact classical transport baseline expansion",
        "classification": "real external benchmark baseline follow-up",
        "dataset": {
            "name": "BEIR/SciFact",
            "url": BEIR_URL,
            "archive_md5": BEIR_MD5,
            "official_primary_metric": "nDCG@10",
        },
        "spaces": {
            "A": MODEL_A,
            "A_revision": model_info(MODEL_A).sha,
            "B": MODEL_B,
            "B_revision": model_info(MODEL_B).sha,
            "pretraining_overlap_between_A_B": "pretraining_overlap_possible",
            "benchmark_pretraining_overlap_A": "unknown",
            "benchmark_pretraining_overlap_B": "unknown",
        },
        "leakage_audit": {
            "status": "PASS",
            "task_labels_used_for_transport_fit_or_selection": 0,
            "qrels_used_for_hyperparameter_selection": False,
            "all_models_frozen_before_test_scoring": True,
            "frozen_split_manifest_reproduced": True,
            "seed": args.seed,
            **manifests,
        },
        "oracle_context": {
            "A_only": {"official": a_official, "retrieval_seconds": a_retrieval},
            "B_oracle": {"official": b_official, "retrieval_seconds": b_retrieval},
            "B_minus_A_ndcg_at_10": b_ndcg - a_ndcg,
        },
        "candidate_grids": {
            "CCA_components": list(COMPONENT_GRID),
            "PLS_components": list(COMPONENT_GRID),
            "RFF_gamma": list(RFF_GAMMAS),
            "RFF_width": list(RFF_WIDTHS),
            "RFF_ridge_alpha": list(RFF_ALPHAS),
        },
        "results_by_budget": rows,
        "quality_matched_frontier_ndcg10": {
            "target_midpoint_A_to_B": midpoint,
            "target_90pct_A_to_B": p90,
            "min_k_midpoint": {m: min_k(rows, m, midpoint) for m in methods},
            "min_k_90pct": {m: min_k(rows, m, p90) for m in methods},
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
