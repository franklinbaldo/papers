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
"""Norm-and-locality-matched coupling null for Pontifex SciFact at K=512.

Prospective follow-up to the completed global- and norm-matched K=512 nulls.
This stronger null preserves residual-magnitude strata and coarse local
neighborhoods in the A-space anchor geometry while destroying exact residual
identity. D_test grades stay sealed until the map, local groups, and both null
banks are frozen.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import scifact_coupling_specificity as coupling
import scifact_coupling_specificity_k512 as parent
import scifact_norm_matched_coupling_k512 as norm_parent
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NULL = 63
N_NORM_STRATA = 8
LOCAL_GROUP_SIZE = 8
SEED = 20260919
EXPECTED_ANCHOR_SHA = "5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a"


def _row_normalize(x: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(denom, 1e-12, None)


def balanced_local_groups(
    anchors_a: np.ndarray,
    norm_chunks: list[np.ndarray],
    group_size: int,
) -> list[np.ndarray]:
    """Create deterministic balanced A-local groups inside each norm stratum.

    For every 64-anchor residual-norm stratum, select farthest-first centers in
    normalized A-space, then greedily assign remaining anchors to the most
    similar center that still has capacity. Only D_student A coordinates and
    already-frozen residual-norm strata are used.
    """
    if K % (len(norm_chunks) * group_size) != 0:
        raise RuntimeError("K must divide evenly into norm-stratum local groups")
    z = _row_normalize(np.asarray(anchors_a, dtype=np.float64))
    groups: list[np.ndarray] = []
    expected_per_stratum = K // len(norm_chunks)
    n_centers = expected_per_stratum // group_size

    for raw_chunk in norm_chunks:
        chunk = np.asarray(sorted(int(i) for i in raw_chunk), dtype=np.int64)
        if len(chunk) != expected_per_stratum:
            raise RuntimeError(
                f"expected {expected_per_stratum} anchors per norm stratum, got {len(chunk)}"
            )
        sim = z[chunk] @ z[chunk].T
        local_pos = {int(idx): pos for pos, idx in enumerate(chunk)}

        centers = [int(chunk[0])]
        while len(centers) < n_centers:
            remaining = [int(i) for i in chunk if int(i) not in centers]
            scored: list[tuple[float, int]] = []
            for idx in remaining:
                pos = local_pos[idx]
                max_sim = max(sim[pos, local_pos[c]] for c in centers)
                scored.append((float(max_sim), idx))
            # Farthest from the nearest existing center; low index breaks ties.
            next_center = min(scored, key=lambda item: (item[0], item[1]))[1]
            centers.append(next_center)

        buckets: dict[int, list[int]] = {c: [c] for c in centers}
        remaining = {int(i) for i in chunk if int(i) not in centers}
        while remaining:
            best: tuple[float, int, int] | None = None
            for idx in sorted(remaining):
                pos = local_pos[idx]
                for c in centers:
                    if len(buckets[c]) >= group_size:
                        continue
                    candidate = (float(sim[pos, local_pos[c]]), -idx, -c)
                    if best is None or candidate > best:
                        best = candidate
            if best is None:
                raise RuntimeError("balanced local assignment exhausted capacity")
            _, neg_idx, neg_center = best
            idx, center = -neg_idx, -neg_center
            buckets[center].append(idx)
            remaining.remove(idx)

        for center in centers:
            group = np.asarray(sorted(buckets[center]), dtype=np.int64)
            if len(group) != group_size:
                raise RuntimeError(f"local group has {len(group)} anchors, expected {group_size}")
            groups.append(group)

    flattened = np.concatenate(groups)
    if len(groups) != K // group_size:
        raise RuntimeError(f"expected {K // group_size} local groups, got {len(groups)}")
    if not np.array_equal(np.sort(flattened), np.arange(K, dtype=np.int64)):
        raise RuntimeError("local groups do not form an exact partition of K anchors")
    return groups


def group_manifest(groups: list[np.ndarray]) -> str:
    labels = np.empty(K, dtype=np.int64)
    for label, group in enumerate(groups):
        labels[group] = label
    return base.sha256_lines([f"{i} {int(labels[i])}" for i in range(K)])


def local_geometry_diagnostic(
    anchors_a: np.ndarray, bank: list[np.ndarray]
) -> dict[str, float]:
    z = _row_normalize(np.asarray(anchors_a, dtype=np.float64))
    rows = []
    for p in bank:
        donor_cos = np.sum(z * z[p], axis=1)
        rows.append(1.0 - donor_cos)
    d = np.stack(rows, axis=0)
    return {
        "mean_A_cosine_distance_mean": float(d.mean(axis=1).mean()),
        "mean_A_cosine_distance_min": float(d.mean(axis=1).min()),
        "mean_A_cosine_distance_max": float(d.mean(axis=1).max()),
        "p95_A_cosine_distance": float(np.quantile(d, 0.95)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--n-norm-strata", type=int, default=N_NORM_STRATA)
    ap.add_argument("--local-group-size", type=int, default=LOCAL_GROUP_SIZE)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-scifact-norm-local-matched-coupling-k512.json"),
    )
    args = ap.parse_args()

    frozen_args = {
        "seed": (args.seed, SEED),
        "k": (args.k, K),
        "n_null": (args.n_null, N_NULL),
        "n_norm_strata": (args.n_norm_strata, N_NORM_STRATA),
        "local_group_size": (args.local_group_size, LOCAL_GROUP_SIZE),
    }
    for name, (observed, expected) in frozen_args.items():
        if observed != expected:
            raise RuntimeError(f"protocol freezes {name}={expected}, got {observed}")

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = side.text_only_data(root)

    # Reproduce the exact parent D_student / D_val membership.
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
    local_groups = balanced_local_groups(aa, norm_chunks, LOCAL_GROUP_SIZE)
    query_perms = norm_parent.matched_permutation_bank(
        local_groups, N_NULL, args.seed + 1_000_000
    )
    document_perms = norm_parent.matched_permutation_bank(
        local_groups, N_NULL, args.seed + 1_100_000
    )
    for j in range(N_NULL):
        if np.array_equal(query_perms[j], document_perms[j]):
            raise RuntimeError(f"independent local-matched permutations coincide at {j}")

    # Freeze all map state and both null banks before D_test grades are opened.
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
        "local_A_groups_sha256": group_manifest(local_groups),
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

    # First read of official D_test relevance grades: after every adaptive object is frozen.
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
    semantic_boot = side.bootstrap_summary(semantic_per_query, args.seed + 1_200_000)
    coherence_boot = side.bootstrap_summary(coherence_per_query, args.seed + 1_300_000)
    semantic_p = coupling.finite_bank_p(true_global, coupled_global)

    result = {
        "experiment": "Pontifex SciFact norm+local-A matched coupling specificity K=512",
        "classification": "prospective mechanism follow-up after completed global and norm-matched K=512 tests",
        "k": K,
        "n_null": N_NULL,
        "n_residual_norm_strata": N_NORM_STRATA,
        "local_A_group_size": LOCAL_GROUP_SIZE,
        "n_local_A_groups": len(local_groups),
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder identities; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; transport, residual norms and A-local groups defined here",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only tau/lambda selection",
            "D_test": "official SciFact test qrels loaded only after map, norm strata, A-local groups and both null banks are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "null_contract": {
            "matching_variables": [
                "L2 norm stratum of the K=512 D_student residual vector",
                "balanced local neighborhood in normalized D_student A-space anchor geometry",
            ],
            "norm_stratification": "8 stable equal-count strata (64 anchors each)",
            "local_partition": "within each norm stratum: 8 deterministic balanced A-space groups of 8 anchors; farthest-first centers plus capacity-constrained nearest-center assignment",
            "identity_destroyed": "every local-group permutation is a derangement; no anchor retains its true residual",
            "coupled": "same norm+local-A matched permutation applied to query and document maps",
            "independent": "different norm+local-A matched permutations applied to query and document maps",
            "query_norm_diagnostic": norm_parent.norm_match_diagnostic(residual, query_perms),
            "document_norm_diagnostic": norm_parent.norm_match_diagnostic(residual, document_perms),
            "query_A_locality_diagnostic": local_geometry_diagnostic(aa, query_perms),
            "document_A_locality_diagnostic": local_geometry_diagnostic(aa, document_perms),
        },
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "manifests": frozen_manifest,
        "test_ndcg_at_10": {
            "TRUE": true_global,
            "NORM_LOCAL_MATCHED_COUPLED_mean": float(coupled_global.mean()),
            "NORM_LOCAL_MATCHED_COUPLED_median": float(np.median(coupled_global)),
            "NORM_LOCAL_MATCHED_COUPLED_min": float(coupled_global.min()),
            "NORM_LOCAL_MATCHED_COUPLED_max": float(coupled_global.max()),
            "NORM_LOCAL_MATCHED_INDEPENDENT_mean": float(independent_global.mean()),
            "NORM_LOCAL_MATCHED_INDEPENDENT_median": float(np.median(independent_global)),
            "NORM_LOCAL_MATCHED_INDEPENDENT_min": float(independent_global.min()),
            "NORM_LOCAL_MATCHED_INDEPENDENT_max": float(independent_global.max()),
        },
        "primary_contrasts": {
            "semantic_specificity_TRUE_minus_NORM_LOCAL_MATCHED_COUPLED_mean": float(
                true_global - coupled_global.mean()
            ),
            "semantic_specificity_finite_bank_p_upper": semantic_p,
            "semantic_specificity_paired_query_bootstrap": semantic_boot,
            "shared_warp_NORM_LOCAL_MATCHED_COUPLED_mean_minus_INDEPENDENT_mean": float(
                coupled_global.mean() - independent_global.mean()
            ),
            "shared_warp_paired_query_bootstrap": coherence_boot,
        },
        "predeclared_decision": {
            "semantic_specificity_supported": bool(
                semantic_boot["ci95_percentile_low"] > 0.0 and semantic_p <= 0.05
            ),
            "shared_warp_coherence_supported": bool(
                coherence_boot["ci95_percentile_low"] > 0.0
            ),
        },
        "interpretation_boundary": {
            "evidence": "whether exact residual identity adds held-out SciFact retrieval utility beyond a coherent deformation preserving both residual-magnitude strata and coarse local A-space anchor geometry; plus whether a common matched deformation beats independent matched deformations",
            "not_evidence": "causal semantic locality, intrinsic or physical torus topology, universal transport superiority, native-B superiority, low-budget superiority, cross-dataset generalization, or Assembly-to-student generalization",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
