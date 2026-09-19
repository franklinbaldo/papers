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
"""Frozen distance-optimal local derangement test for Pontifex SciFact K=512.

Protocol: PROTOCOL-SCIFACT-NORM-MINCOST-DERANGEMENT-K512-2026-09-19.md

The null is a single deterministic minimum-cost perfect derangement within the
frozen residual-norm strata.  It is constructed from D_student geometry only.
No finite-bank p-value is reported because there is no permutation reference
bank; the predeclared inference is a paired-query bootstrap confidence interval.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import scifact_coupling_specificity as coupling
import scifact_coupling_specificity_k512 as parent
import scifact_knn_null_locality_calibration_k512 as calibration
import scifact_norm_matched_coupling_k512 as norm_parent
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NORM_STRATA = 8
SEED = 20260919
BOOTSTRAP_SEED = SEED + 1_800_000
EXPECTED_ANCHOR_SHA = "5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--n-norm-strata", type=int, default=N_NORM_STRATA)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-scifact-norm-mincost-derangement-k512.json"),
    )
    args = ap.parse_args()

    frozen = {
        "k": (args.k, K),
        "n_norm_strata": (args.n_norm_strata, N_NORM_STRATA),
        "seed": (args.seed, SEED),
    }
    for name, (observed, expected) in frozen.items():
        if observed != expected:
            raise RuntimeError(f"protocol freezes {name}={expected}, got {observed}")

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = side.text_only_data(root)

    # Reproduce D_student/D_val from split membership and text only.
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
    a_test = emb["a_test"]
    a_docs = emb["a_docs"]

    aa = a_student[:K]
    bb = b_student[:K]
    tau, lam, val_loss, coarse, residual = base.select_torus(aa, bb, a_val, b_val)

    norm_labels, norm_chunks = norm_parent.residual_norm_strata(residual, N_NORM_STRATA)
    dist = calibration.cosine_distance_matrix(aa)
    optimal_perm = calibration.minimum_cost_derangement(dist, norm_chunks)
    optimal_mean = float(np.mean(dist[np.arange(K), optimal_perm]))
    random_mean = calibration.random_within_stratum_mean(dist, norm_chunks)
    nearest_mean = calibration.nearest_nonself_mean(dist, norm_chunks)

    # Freeze all D_student/D_val adaptive objects and all mapped A-side coordinates
    # before the first official D_test relevance-grade read.
    coarse_q = base.apply_procrustes(a_test, *coarse).astype(np.float32)
    coarse_d = base.apply_procrustes(a_docs, *coarse).astype(np.float32)
    wq = coupling.local_weights(a_test, aa, tau)
    wd = coupling.local_weights(a_docs, aa, tau)

    frozen_manifest = {
        "anchor_ids_sha256": base.sha256_lines(student_ids[:K]),
        "student_ids_sha256": base.sha256_lines(student_ids),
        "validation_ids_sha256": base.sha256_lines(val_ids),
        "test_ids_sha256": base.sha256_lines(test_ids),
        "corpus_ids_sha256": base.sha256_lines(data.corpus_ids),
        "norm_strata_sha256": norm_parent.stratum_manifest(norm_labels),
        "minimum_cost_derangement_sha256": coupling.permutation_manifest([optimal_perm]),
    }
    expected = {
        "anchor_ids_sha256": EXPECTED_ANCHOR_SHA,
        "student_ids_sha256": parent.EXPECTED_STUDENT_SHA,
        "validation_ids_sha256": parent.EXPECTED_VAL_SHA,
        "test_ids_sha256": parent.EXPECTED_TEST_SHA,
        "corpus_ids_sha256": parent.EXPECTED_CORPUS_SHA,
    }
    for key, value in expected.items():
        if frozen_manifest[key] != value:
            raise RuntimeError(
                f"frozen manifest mismatch for {key}: {frozen_manifest[key]} != {value}"
            )

    # Reproduce the D_student-only locality reference before opening test grades.
    reference = {
        "individual_nearest_nonself_mean_A_cosine_distance": nearest_mean,
        "minimum_cost_perfect_derangement_mean_A_cosine_distance": optimal_mean,
        "random_within_norm_stratum_expected_mean_A_cosine_distance": random_mean,
    }
    expected_locality = {
        "individual_nearest_nonself_mean_A_cosine_distance": 0.5138589106455074,
        "minimum_cost_perfect_derangement_mean_A_cosine_distance": 0.5390020166430645,
        "random_within_norm_stratum_expected_mean_A_cosine_distance": 0.8771154157297493,
    }
    for key, expected_value in expected_locality.items():
        if not np.isclose(reference[key], expected_value, rtol=0.0, atol=1e-10):
            raise RuntimeError(
                f"locality calibration mismatch for {key}: {reference[key]} != {expected_value}"
            )

    # First official D_test relevance-grade read occurs only here.
    test_qrels = base.load_qrels(root / "qrels" / "test.tsv")
    if sorted(test_qrels) != test_ids:
        raise RuntimeError("test qrel manifest changed between membership and grade load")

    true_q = coupling.mapped(coarse_q, wq, residual, None, lam)
    true_d = coupling.mapped(coarse_d, wd, residual, None, lam)
    null_q = coupling.mapped(coarse_q, wq, residual, optimal_perm, lam)
    null_d = coupling.mapped(coarse_d, wd, residual, optimal_perm, lam)

    true_nd = side.per_query_ndcg(
        test_qrels, test_ids, data.corpus_ids, side.scores(true_q, true_d)
    )
    null_nd = side.per_query_ndcg(
        test_qrels, test_ids, data.corpus_ids, side.scores(null_q, null_d)
    )
    delta = true_nd - null_nd
    bootstrap = side.bootstrap_summary(delta, BOOTSTRAP_SEED)
    supported = bool(bootstrap["ci95_percentile_low"] > 0.0)

    result = {
        "experiment": "Pontifex SciFact residual-norm minimum-cost local derangement K=512",
        "classification": "adaptive/prospective follow-up frozen before this D_test relevance-grade read",
        "protocol": "PROTOCOL-SCIFACT-NORM-MINCOST-DERANGEMENT-K512-2026-09-19.md",
        "k": K,
        "n_residual_norm_strata": N_NORM_STRATA,
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder identities; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; map, residual strata and minimum-cost derangement defined here",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only tau/lambda selection",
            "D_test": "official SciFact test qrels loaded only after map, strata, minimum-cost derangement, manifests and mapped coordinates are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "null_contract": {
            "identity_destroyed": "minimum-cost assignment is a perfect derangement within each residual-norm stratum; no anchor retains its true residual",
            "matching_variables": [
                "L2 norm stratum of the K=512 D_student residual vector",
                "globally minimum total normalized A-space cosine donor distance subject to perfect derangement",
            ],
            "finite_bank_p_value_reported": False,
            "reason": "single deterministic optimum is not a permutation reference distribution",
        },
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "locality_calibration_D_student_only": reference,
        "manifests": frozen_manifest,
        "test_ndcg_at_10": {
            "TRUE": float(true_nd.mean()),
            "MINCOST_COUPLED": float(null_nd.mean()),
            "TRUE_minus_MINCOST_COUPLED": float(delta.mean()),
        },
        "paired_query_bootstrap": bootstrap,
        "predeclared_decision": {
            "exact_identity_utility_beyond_distance_optimal_null_supported": supported,
            "criterion": "paired-query 95% percentile CI strictly above zero",
        },
        "interpretation_boundary": {
            "evidence": "whether exact residual identity adds held-out SciFact retrieval utility beyond residual magnitude plus the minimum-distance feasible A-space perfect-derangement nuisance",
            "not_evidence": "causal semantic locality, intrinsic or physical torus topology, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, or Assembly-to-student generalization",
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
