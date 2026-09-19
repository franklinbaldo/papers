# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.28",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "scipy>=1.14",
#   "sentence-transformers>=5.0",
#   "huggingface-hub>=0.34",
# ]
# ///
"""D_student-only calibration of locality in the Pontifex K=512 KNN null.

This script never opens SciFact relevance grades.  It asks a narrower
methodological question: how local is the frozen feasible KNN derangement bank
relative to (a) a random within-residual-norm-stratum donor and (b) the
minimum-cost perfect derangement permitted by those strata?

The resulting locality-capture score is descriptive, not a new significance
test:
    0 ~= random-within-stratum locality
    1 ~= minimum-cost feasible derangement locality
Values outside [0, 1] are left unclipped so a worse-than-random bank remains
visible rather than being cosmetically bounded.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

import scifact_coupling_specificity_k512 as parent
import scifact_norm_knn_feasibility_ladder_k512 as feasible
import scifact_norm_knn_matched_coupling_k512 as knn_parent
import scifact_norm_matched_coupling_k512 as norm_parent
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NULL = 63
N_NORM_STRATA = 8
SEED = 20260919
EXPECTED_ANCHOR_SHA = "5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a"


def cosine_distance_matrix(x: np.ndarray) -> np.ndarray:
    z = knn_parent._row_normalize(np.asarray(x, dtype=np.float64))
    return 1.0 - z @ z.T


def minimum_cost_derangement(dist: np.ndarray, chunks: list[np.ndarray]) -> np.ndarray:
    perm = np.arange(len(dist), dtype=np.int64)
    big = 1_000_000.0
    for raw_chunk in chunks:
        chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
        cost = dist[np.ix_(chunk, chunk)].copy()
        np.fill_diagonal(cost, big)
        rows, cols = linear_sum_assignment(cost)
        if np.any(cost[rows, cols] >= big):
            raise RuntimeError("norm stratum has no perfect derangement")
        perm[chunk[rows]] = chunk[cols]
    if np.any(perm == np.arange(len(perm))):
        raise RuntimeError("minimum-cost assignment retained a self donor")
    return perm


def random_within_stratum_mean(dist: np.ndarray, chunks: list[np.ndarray]) -> float:
    total = 0.0
    count = 0
    for raw_chunk in chunks:
        chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
        block = dist[np.ix_(chunk, chunk)]
        mask = ~np.eye(len(chunk), dtype=bool)
        total += float(block[mask].sum())
        count += int(mask.sum())
    return total / count


def nearest_nonself_mean(dist: np.ndarray, chunks: list[np.ndarray]) -> float:
    vals: list[float] = []
    for raw_chunk in chunks:
        chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
        block = dist[np.ix_(chunk, chunk)].copy()
        np.fill_diagonal(block, np.inf)
        vals.extend(np.min(block, axis=1).tolist())
    return float(np.mean(vals))


def bank_distance_summary(dist: np.ndarray, bank: list[np.ndarray]) -> dict[str, float]:
    per_perm = np.asarray(
        [float(np.mean(dist[np.arange(K), p])) for p in bank], dtype=np.float64
    )
    all_edges = np.concatenate([dist[np.arange(K), p] for p in bank])
    return {
        "mean": float(all_edges.mean()),
        "median": float(np.median(all_edges)),
        "p95": float(np.quantile(all_edges, 0.95)),
        "permutation_mean_min": float(per_perm.min()),
        "permutation_mean_max": float(per_perm.max()),
        "permutation_mean_sd": float(per_perm.std(ddof=1)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--n-norm-strata", type=int, default=N_NORM_STRATA)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-scifact-knn-null-locality-calibration-k512.json"),
    )
    args = ap.parse_args()

    frozen = {
        "k": (args.k, K),
        "n_null": (args.n_null, N_NULL),
        "n_norm_strata": (args.n_norm_strata, N_NORM_STRATA),
        "seed": (args.seed, SEED),
    }
    for name, (observed, expected) in frozen.items():
        if observed != expected:
            raise RuntimeError(f"protocol freezes {name}={expected}, got {observed}")

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = side.text_only_data(root)

    # Reproduce D_student membership from split/text membership only; no qrel grades.
    test_texts = {data.queries[q].strip() for q in test_ids}
    eligible_ids = [q for q in train_ids if data.queries[q].strip() not in test_texts]
    rng = np.random.default_rng(args.seed)
    order = rng.permutation(len(eligible_ids))
    eligible_ids = [eligible_ids[i] for i in order]
    cut = max(1, int(math.floor(0.80 * len(eligible_ids))))
    student_ids = eligible_ids[:cut]
    val_ids = eligible_ids[cut:]
    if len(student_ids) < K:
        raise RuntimeError(f"K={K} exceeds student pool {len(student_ids)}")

    emb = side.minimal_embeddings(
        data, train_ids, test_ids, args.cache_dir / "scifact-side-minimal.npz"
    )
    train_pos = {qid: i for i, qid in enumerate(train_ids)}
    student_idx = np.asarray([train_pos[q] for q in student_ids], dtype=np.int64)
    val_idx = np.asarray([train_pos[q] for q in val_ids], dtype=np.int64)

    a_student = emb["a_train"][student_idx]
    b_student = emb["b_train"][student_idx]
    a_val = emb["a_train"][val_idx]
    b_val = emb["b_train"][val_idx]
    aa = a_student[:K]
    bb = b_student[:K]

    tau, lam, val_loss, _coarse, residual = base.select_torus(aa, bb, a_val, b_val)
    norm_labels, norm_chunks = norm_parent.residual_norm_strata(residual, N_NORM_STRATA)
    selected_rank, candidates, ranks, feasibility_record = feasible.select_feasible_graph(
        aa, norm_chunks
    )
    bank = knn_parent.constrained_permutation_bank(
        norm_chunks, candidates, N_NULL, args.seed + 1_400_000
    )

    dist = cosine_distance_matrix(aa)
    optimal_perm = minimum_cost_derangement(dist, norm_chunks)
    optimal_mean = float(np.mean(dist[np.arange(K), optimal_perm]))
    random_mean = random_within_stratum_mean(dist, norm_chunks)
    nearest_mean = nearest_nonself_mean(dist, norm_chunks)
    bank_summary = bank_distance_summary(dist, bank)

    denominator = random_mean - optimal_mean
    if denominator <= 0:
        raise RuntimeError("invalid locality calibration denominator")
    locality_capture = (random_mean - bank_summary["mean"]) / denominator

    manifests = {
        "anchor_ids_sha256": base.sha256_lines(student_ids[:K]),
        "student_ids_sha256": base.sha256_lines(student_ids),
        "validation_ids_sha256": base.sha256_lines(val_ids),
        "test_ids_sha256": base.sha256_lines(test_ids),
        "norm_strata_sha256": norm_parent.stratum_manifest(norm_labels),
        "selected_rank": int(selected_rank),
        "knn_candidate_graph_sha256": knn_parent.candidate_manifest(candidates),
    }
    expected = {
        "anchor_ids_sha256": EXPECTED_ANCHOR_SHA,
        "student_ids_sha256": parent.EXPECTED_STUDENT_SHA,
        "validation_ids_sha256": parent.EXPECTED_VAL_SHA,
        "test_ids_sha256": parent.EXPECTED_TEST_SHA,
    }
    for key, value in expected.items():
        if manifests[key] != value:
            raise RuntimeError(f"frozen manifest mismatch for {key}")

    result = {
        "experiment": "Pontifex SciFact KNN-null locality calibration K=512",
        "classification": "D_student-only methodological calibration; no D_test relevance grades read",
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder identities; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; all locality calibration computed here",
            "D_val": "20% deterministic filtered train-query representation pairs; tau/lambda coordinate-only selection reproduced for exact residual definition",
            "D_test": "membership used only to exclude exact text overlap and hash the frozen split; relevance grades never opened",
            "task_labels_used": 0,
        },
        "k": K,
        "n_null": N_NULL,
        "n_residual_norm_strata": N_NORM_STRATA,
        "selected_max_neighbor_rank": int(selected_rank),
        "feasibility_ladder": feasibility_record,
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "locality_calibration": {
            "individual_nearest_nonself_mean_A_cosine_distance": nearest_mean,
            "minimum_cost_perfect_derangement_mean_A_cosine_distance": optimal_mean,
            "random_within_norm_stratum_expected_mean_A_cosine_distance": random_mean,
            "frozen_KNN_bank": bank_summary,
            "locality_capture_vs_random_to_optimal": float(locality_capture),
            "interpretation": "0 is random-within-stratum mean locality; 1 is the minimum-cost feasible derangement mean locality; score is descriptive and unclipped",
        },
        "manifests": manifests,
        "interpretation_boundary": {
            "evidence": "quality of the KNN null as a source-space-local nuisance control on D_student geometry",
            "not_evidence": "held-out retrieval performance, semantic specificity, causal locality, torus topology, or cross-dataset generalization",
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
