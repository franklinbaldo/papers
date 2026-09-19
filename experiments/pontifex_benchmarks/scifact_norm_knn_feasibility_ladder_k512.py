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
"""Feasibility-frozen local coupling null for Pontifex SciFact at K=512.

The first hard A-locality protocol fixed donor rank <=16 and failed before any
D_test grade read because the induced bipartite graph had no perfect
derangement.  This follow-up freezes a rank ladder and selects the smallest
combinatorially feasible graph using D_student geometry only.  The selected
graph and both null banks are frozen before D_test grades are opened.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

import scifact_coupling_specificity as coupling
import scifact_coupling_specificity_k512 as parent
import scifact_norm_knn_matched_coupling_k512 as knn_parent
import scifact_norm_matched_coupling_k512 as norm_parent
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NULL = 63
N_NORM_STRATA = 8
RANK_LADDER = (16, 20, 24, 32, 48, 63)
SEED = 20260919
EXPECTED_ANCHOR_SHA = "5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a"


def graph_has_perfect_derangement(
    norm_chunks: list[np.ndarray], candidates: list[np.ndarray]
) -> bool:
    """Check Hall feasibility per norm stratum using only the frozen graph."""
    for raw_chunk in norm_chunks:
        chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
        local_pos = {int(idx): pos for pos, idx in enumerate(chunk)}
        big = 1_000_000.0
        cost = np.full((len(chunk), len(chunk)), big, dtype=np.float64)
        for row_pos, anchor in enumerate(chunk):
            for donor in candidates[int(anchor)]:
                col_pos = local_pos.get(int(donor))
                if col_pos is not None:
                    cost[row_pos, col_pos] = 0.0
        rows, cols = linear_sum_assignment(cost)
        if np.any(cost[rows, cols] >= big):
            return False
    return True


def select_feasible_graph(
    anchors_a: np.ndarray, norm_chunks: list[np.ndarray]
) -> tuple[int, list[np.ndarray], np.ndarray, list[dict[str, int | bool]]]:
    """Select the smallest feasible cap in the predeclared D_student-only ladder."""
    record: list[dict[str, int | bool]] = []
    selected: tuple[int, list[np.ndarray], np.ndarray] | None = None
    for rank_cap in RANK_LADDER:
        candidates, ranks = knn_parent.knn_candidates(anchors_a, norm_chunks, rank_cap)
        feasible = graph_has_perfect_derangement(norm_chunks, candidates)
        record.append(
            {
                "rank_cap": int(rank_cap),
                "perfect_derangement_exists": bool(feasible),
            }
        )
        if feasible:
            selected = (rank_cap, candidates, ranks)
            break
    if selected is None:
        raise RuntimeError("no feasible perfect derangement in frozen KNN rank ladder")
    return selected[0], selected[1], selected[2], record


def locality_diagnostic(
    anchors_a: np.ndarray,
    bank: list[np.ndarray],
    ranks: np.ndarray,
    selected_rank: int,
) -> dict[str, float]:
    z = knn_parent._row_normalize(np.asarray(anchors_a, dtype=np.float64))
    dist_rows: list[np.ndarray] = []
    rank_rows: list[np.ndarray] = []
    for p in bank:
        dist_rows.append(1.0 - np.sum(z * z[p], axis=1))
        rank_rows.append(ranks[np.arange(K), p].astype(np.float64))
    d = np.stack(dist_rows, axis=0)
    r = np.stack(rank_rows, axis=0)
    if np.any(r < 1) or np.any(r > selected_rank):
        raise RuntimeError("selected null bank violated its frozen donor-rank cap")
    return {
        "mean_A_cosine_distance": float(d.mean()),
        "median_A_cosine_distance": float(np.median(d)),
        "p95_A_cosine_distance": float(np.quantile(d, 0.95)),
        "max_A_cosine_distance": float(d.max()),
        "mean_donor_rank": float(r.mean()),
        "p95_donor_rank": float(np.quantile(r, 0.95)),
        "max_donor_rank": float(r.max()),
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
        default=Path("pontifex-scifact-norm-knn-feasibility-ladder-k512.json"),
    )
    args = ap.parse_args()

    frozen_args = {
        "seed": (args.seed, SEED),
        "k": (args.k, K),
        "n_null": (args.n_null, N_NULL),
        "n_norm_strata": (args.n_norm_strata, N_NORM_STRATA),
    }
    for name, (observed, expected) in frozen_args.items():
        if observed != expected:
            raise RuntimeError(f"protocol freezes {name}={expected}, got {observed}")

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = side.text_only_data(root)

    # Reproduce the exact K=512 D_student / D_val membership without qrel grades.
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
    selected_rank, candidates, ranks, feasibility = select_feasible_graph(aa, norm_chunks)

    query_perms = knn_parent.constrained_permutation_bank(
        norm_chunks, candidates, N_NULL, args.seed + 1_400_000
    )
    document_perms = knn_parent.constrained_permutation_bank(
        norm_chunks, candidates, N_NULL, args.seed + 1_500_000
    )
    for j in range(N_NULL):
        if np.array_equal(query_perms[j], document_perms[j]):
            raise RuntimeError(f"independent rank-constrained permutations coincide at {j}")

    # Freeze all adaptive D_student/D_val objects before the first D_test grade read.
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
        "selected_rank": int(selected_rank),
        "rank_ladder_sha256": base.sha256_lines([str(x) for x in RANK_LADDER]),
        "knn_candidate_graph_sha256": knn_parent.candidate_manifest(candidates),
        "query_permutation_bank_sha256": coupling.permutation_manifest(query_perms),
        "document_permutation_bank_sha256": coupling.permutation_manifest(document_perms),
    }
    expected = {
        "student_ids_sha256": parent.EXPECTED_STUDENT_SHA,
        "validation_ids_sha256": parent.EXPECTED_VAL_SHA,
        "test_ids_sha256": parent.EXPECTED_TEST_SHA,
        "corpus_ids_sha256": parent.EXPECTED_CORPUS_SHA,
        "anchor_ids_sha256": EXPECTED_ANCHOR_SHA,
    }
    for key, value in expected.items():
        if frozen_manifest[key] != value:
            raise RuntimeError(
                f"frozen manifest mismatch for {key}: {frozen_manifest[key]} != {value}"
            )

    # First official D_test relevance-grade read occurs only here.
    test_qrels = base.load_qrels(root / "qrels" / "test.tsv")
    if sorted(test_qrels) != test_ids:
        raise RuntimeError("test qrel manifest changed between membership and grade load")

    true_q = coupling.mapped(coarse_q, wq, residual, None, lam)
    true_d = coupling.mapped(coarse_d, wd, residual, None, lam)
    true_nd = side.per_query_ndcg(
        test_qrels, test_ids, data.corpus_ids, side.scores(true_q, true_d)
    )

    coupled_rows: list[np.ndarray] = []
    independent_rows: list[np.ndarray] = []
    for qp, dp in zip(query_perms, document_perms, strict=True):
        q_scrambled = coupling.mapped(coarse_q, wq, residual, qp, lam)
        d_coupled = coupling.mapped(coarse_d, wd, residual, qp, lam)
        d_independent = coupling.mapped(coarse_d, wd, residual, dp, lam)
        coupled_rows.append(
            side.per_query_ndcg(
                test_qrels,
                test_ids,
                data.corpus_ids,
                side.scores(q_scrambled, d_coupled),
            )
        )
        independent_rows.append(
            side.per_query_ndcg(
                test_qrels,
                test_ids,
                data.corpus_ids,
                side.scores(q_scrambled, d_independent),
            )
        )

    coupled = np.stack(coupled_rows, axis=0)
    independent = np.stack(independent_rows, axis=0)
    coupled_global = coupled.mean(axis=1)
    independent_global = independent.mean(axis=1)
    true_global = float(true_nd.mean())

    semantic_per_query = true_nd - coupled.mean(axis=0)
    coherence_per_query = coupled.mean(axis=0) - independent.mean(axis=0)
    semantic_boot = side.bootstrap_summary(semantic_per_query, args.seed + 1_600_000)
    coherence_boot = side.bootstrap_summary(coherence_per_query, args.seed + 1_700_000)
    semantic_p = coupling.finite_bank_p(true_global, coupled_global)

    semantic_supported = bool(
        semantic_p <= 0.05 and semantic_boot["ci95_percentile_low"] > 0.0
    )
    coherence_supported = bool(coherence_boot["ci95_percentile_low"] > 0.0)

    result = {
        "experiment": "Pontifex SciFact residual-norm + feasible A-KNN matched coupling specificity K=512",
        "classification": "adaptive/prospective follow-up; KNN cap selected by D_student graph feasibility only",
        "k": K,
        "n_null": N_NULL,
        "n_residual_norm_strata": N_NORM_STRATA,
        "rank_ladder": list(RANK_LADDER),
        "feasibility_ladder": feasibility,
        "selected_max_neighbor_rank": int(selected_rank),
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder identities; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; transport, residual norms, KNN graph and feasibility selection defined here",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only tau/lambda selection",
            "D_test": "official SciFact test qrels loaded only after map, norm strata, selected KNN graph, feasibility record and both null banks are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "null_contract": {
            "matching_variables": [
                "L2 norm stratum of the K=512 D_student residual vector",
                "donor among the nearest non-self normalized D_student A-space anchors inside that stratum, with cap chosen solely by perfect-derangement feasibility",
            ],
            "rank_selection": "smallest feasible cap in frozen ladder [16,20,24,32,48,63], using D_student geometry only",
            "identity_destroyed": "perfect matching is a derangement; no anchor retains its true residual",
            "coupled": "same norm+KNN constrained permutation applied to query and document maps",
            "independent": "different norm+KNN constrained permutations applied to query and document maps",
            "query_norm_diagnostic": norm_parent.norm_match_diagnostic(residual, query_perms),
            "document_norm_diagnostic": norm_parent.norm_match_diagnostic(residual, document_perms),
            "query_A_locality_diagnostic": locality_diagnostic(
                aa, query_perms, ranks, selected_rank
            ),
            "document_A_locality_diagnostic": locality_diagnostic(
                aa, document_perms, ranks, selected_rank
            ),
        },
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "manifests": frozen_manifest,
        "test_ndcg_at_10": {
            "TRUE": true_global,
            "NORM_KNN_MATCHED_COUPLED_mean": float(coupled_global.mean()),
            "NORM_KNN_MATCHED_COUPLED_median": float(np.median(coupled_global)),
            "NORM_KNN_MATCHED_COUPLED_min": float(coupled_global.min()),
            "NORM_KNN_MATCHED_COUPLED_max": float(coupled_global.max()),
            "NORM_KNN_MATCHED_INDEPENDENT_mean": float(independent_global.mean()),
            "NORM_KNN_MATCHED_INDEPENDENT_median": float(np.median(independent_global)),
            "NORM_KNN_MATCHED_INDEPENDENT_min": float(independent_global.min()),
            "NORM_KNN_MATCHED_INDEPENDENT_max": float(independent_global.max()),
        },
        "primary_contrasts": {
            "semantic_specificity_TRUE_minus_NORM_KNN_MATCHED_COUPLED_mean": float(
                true_global - coupled_global.mean()
            ),
            "semantic_specificity_finite_bank_p_upper": float(semantic_p),
            "semantic_specificity_paired_query_bootstrap": semantic_boot,
            "shared_warp_NORM_KNN_MATCHED_COUPLED_mean_minus_INDEPENDENT_mean": float(
                coupled_global.mean() - independent_global.mean()
            ),
            "shared_warp_paired_query_bootstrap": coherence_boot,
        },
        "predeclared_decision": {
            "semantic_specificity_supported": semantic_supported,
            "shared_warp_coherence_supported": coherence_supported,
        },
        "interpretation_boundary": {
            "evidence": "whether exact residual identity adds held-out SciFact retrieval utility beyond residual-magnitude matching plus the tightest feasible frozen source-space donor-rank constraint; and whether a common constrained deformation beats independent constrained deformations",
            "not_evidence": "causal semantic locality, intrinsic or physical torus topology, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, or Assembly-to-student generalization",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
