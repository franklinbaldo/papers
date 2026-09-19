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
"""Rank-constrained local coupling null for Pontifex SciFact at K=512.

This follow-up exists because the prior balanced-group "local" null had a weak
locality diagnostic (mean donor cosine distance ~0.79, p95 ~1.00).  Here every
residual donor is forced to be among the 16 nearest non-self A-space anchors
*within the same frozen residual-norm stratum*.  Query/document coupled and
independent banks are frozen before D_test grades are read.
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
import scifact_norm_matched_coupling_k512 as norm_parent
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NULL = 63
N_NORM_STRATA = 8
MAX_NEIGHBOR_RANK = 16
SEED = 20260919
EXPECTED_ANCHOR_SHA = "5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a"


def _row_normalize(x: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(denom, 1e-12, None)


def knn_candidates(
    anchors_a: np.ndarray,
    norm_chunks: list[np.ndarray],
    max_neighbor_rank: int,
) -> tuple[list[np.ndarray], np.ndarray]:
    """Return allowed donors and donor ranks for each anchor.

    Candidate search is restricted to the anchor's residual-norm stratum.  Rank
    1 is the nearest non-self anchor in normalized A-space.  The function uses
    D_student coordinates only.
    """
    z = _row_normalize(np.asarray(anchors_a, dtype=np.float64))
    candidates: list[np.ndarray | None] = [None] * K
    ranks = np.full((K, K), -1, dtype=np.int16)
    for raw_chunk in norm_chunks:
        chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
        if len(chunk) != K // len(norm_chunks):
            raise RuntimeError("unexpected residual-norm stratum size")
        sim = z[chunk] @ z[chunk].T
        for row_pos, anchor in enumerate(chunk):
            donor_pos = [j for j in range(len(chunk)) if j != row_pos]
            donor_pos.sort(key=lambda j: (-float(sim[row_pos, j]), int(chunk[j])))
            ordered = chunk[np.asarray(donor_pos, dtype=np.int64)]
            allowed = ordered[:max_neighbor_rank]
            if len(allowed) != max_neighbor_rank:
                raise RuntimeError("not enough non-self anchors for KNN constraint")
            candidates[int(anchor)] = allowed
            for rank, donor in enumerate(ordered, start=1):
                ranks[int(anchor), int(donor)] = rank
    if any(c is None for c in candidates):
        raise RuntimeError("candidate construction did not cover all anchors")
    return [np.asarray(c, dtype=np.int64) for c in candidates], ranks


def constrained_permutation_bank(
    norm_chunks: list[np.ndarray],
    candidates: list[np.ndarray],
    n_null: int,
    seed: int,
) -> list[np.ndarray]:
    """Generate unique perfect-match derangements using only allowed KNN edges."""
    rng = np.random.default_rng(seed)
    bank: list[np.ndarray] = []
    seen: set[tuple[int, ...]] = set()
    attempts = 0
    max_attempts = max(2000, 50 * n_null)

    while len(bank) < n_null and attempts < max_attempts:
        attempts += 1
        perm = np.empty(K, dtype=np.int64)
        feasible = True
        for raw_chunk in norm_chunks:
            chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
            local_pos = {int(idx): pos for pos, idx in enumerate(chunk)}
            big = 1_000_000.0
            cost = np.full((len(chunk), len(chunk)), big, dtype=np.float64)
            for row_pos, anchor in enumerate(chunk):
                allowed = candidates[int(anchor)]
                for donor in allowed:
                    col_pos = local_pos.get(int(donor))
                    if col_pos is not None:
                        cost[row_pos, col_pos] = float(rng.random())
            rows, cols = linear_sum_assignment(cost)
            if np.any(cost[rows, cols] >= big):
                feasible = False
                break
            perm[chunk[rows]] = chunk[cols]
        if not feasible:
            raise RuntimeError(
                "top-K A-neighbor graph has no perfect derangement; protocol rank cap is infeasible"
            )
        if np.any(perm == np.arange(K, dtype=np.int64)):
            raise RuntimeError("constrained assignment unexpectedly retained identity")
        key = tuple(int(x) for x in perm)
        if key not in seen:
            seen.add(key)
            bank.append(perm.copy())

    if len(bank) != n_null:
        raise RuntimeError(f"only generated {len(bank)} unique constrained nulls")
    return bank


def locality_diagnostic(
    anchors_a: np.ndarray,
    bank: list[np.ndarray],
    ranks: np.ndarray,
) -> dict[str, float]:
    z = _row_normalize(np.asarray(anchors_a, dtype=np.float64))
    dist_rows: list[np.ndarray] = []
    rank_rows: list[np.ndarray] = []
    for p in bank:
        dist_rows.append(1.0 - np.sum(z * z[p], axis=1))
        rank_rows.append(ranks[np.arange(K), p].astype(np.float64))
    d = np.stack(dist_rows, axis=0)
    r = np.stack(rank_rows, axis=0)
    if np.any(r < 1) or np.any(r > MAX_NEIGHBOR_RANK):
        raise RuntimeError("rank-constrained bank violated its donor-rank contract")
    return {
        "mean_A_cosine_distance": float(d.mean()),
        "median_A_cosine_distance": float(np.median(d)),
        "p95_A_cosine_distance": float(np.quantile(d, 0.95)),
        "max_A_cosine_distance": float(d.max()),
        "mean_donor_rank": float(r.mean()),
        "p95_donor_rank": float(np.quantile(r, 0.95)),
        "max_donor_rank": float(r.max()),
    }


def candidate_manifest(candidates: list[np.ndarray]) -> str:
    return base.sha256_lines(
        [f"{i} " + " ".join(str(int(x)) for x in candidates[i]) for i in range(K)]
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--n-norm-strata", type=int, default=N_NORM_STRATA)
    ap.add_argument("--max-neighbor-rank", type=int, default=MAX_NEIGHBOR_RANK)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-scifact-norm-knn-matched-coupling-k512.json"),
    )
    args = ap.parse_args()

    frozen_args = {
        "seed": (args.seed, SEED),
        "k": (args.k, K),
        "n_null": (args.n_null, N_NULL),
        "n_norm_strata": (args.n_norm_strata, N_NORM_STRATA),
        "max_neighbor_rank": (args.max_neighbor_rank, MAX_NEIGHBOR_RANK),
    }
    for name, (observed, expected) in frozen_args.items():
        if observed != expected:
            raise RuntimeError(f"protocol freezes {name}={expected}, got {observed}")

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = side.text_only_data(root)

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
    candidates, ranks = knn_candidates(aa, norm_chunks, MAX_NEIGHBOR_RANK)
    query_perms = constrained_permutation_bank(
        norm_chunks, candidates, N_NULL, args.seed + 1_400_000
    )
    document_perms = constrained_permutation_bank(
        norm_chunks, candidates, N_NULL, args.seed + 1_500_000
    )
    for j in range(N_NULL):
        if np.array_equal(query_perms[j], document_perms[j]):
            raise RuntimeError(f"independent rank-constrained permutations coincide at {j}")

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
        "knn_candidate_graph_sha256": candidate_manifest(candidates),
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
                test_qrels, test_ids, data.corpus_ids, side.scores(q_scrambled, d_coupled)
            )
        )
        independent_rows.append(
            side.per_query_ndcg(
                test_qrels, test_ids, data.corpus_ids, side.scores(q_scrambled, d_independent)
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
        "experiment": "Pontifex SciFact residual-norm + A-KNN matched coupling specificity K=512",
        "classification": "adaptive/prospective follow-up motivated by weak locality diagnostics in the prior balanced-group null",
        "k": K,
        "n_null": N_NULL,
        "n_residual_norm_strata": N_NORM_STRATA,
        "max_neighbor_rank": MAX_NEIGHBOR_RANK,
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder identities; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; transport, residual norms and A-KNN graph defined here",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only tau/lambda selection",
            "D_test": "official SciFact test qrels loaded only after map, norm strata, A-KNN candidate graph and both null banks are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "null_contract": {
            "matching_variables": [
                "L2 norm stratum of the K=512 D_student residual vector",
                "donor among the 16 nearest non-self normalized D_student A-space anchors inside that stratum",
            ],
            "identity_destroyed": "perfect matching is a derangement; no anchor retains its true residual",
            "coupled": "same norm+KNN constrained permutation applied to query and document maps",
            "independent": "different norm+KNN constrained permutations applied to query and document maps",
            "query_norm_diagnostic": norm_parent.norm_match_diagnostic(residual, query_perms),
            "document_norm_diagnostic": norm_parent.norm_match_diagnostic(residual, document_perms),
            "query_A_locality_diagnostic": locality_diagnostic(aa, query_perms, ranks),
            "document_A_locality_diagnostic": locality_diagnostic(aa, document_perms, ranks),
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
            "evidence": "whether exact residual identity adds held-out SciFact retrieval utility beyond residual-magnitude matching plus a hard source-space donor-rank constraint; and whether a common constrained deformation beats independent constrained deformations",
            "not_evidence": "causal semantic locality, intrinsic or physical torus topology, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, or Assembly-to-student generalization",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
