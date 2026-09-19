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
"""Norm-matched coupling null for Pontifex SciFact at K=512.

Prospective mechanism follow-up to the completed global-permutation K=512 null.
The stronger null preserves coarse residual-magnitude strata while destroying exact
residual-to-anchor identity. Test relevance grades remain sealed until the map,
strata, and all permutation banks are frozen.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import scifact_coupling_specificity as coupling
import scifact_coupling_specificity_k512 as parent
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NULL = 63
N_STRATA = 8
SEED = 20260919
EXPECTED_ANCHOR_SHA = "5a581b24b09b874bd65e759dfeabbe721eb66f947994470ceb3cee8768f4e80a"


def residual_norm_strata(residual: np.ndarray, n_strata: int) -> tuple[np.ndarray, list[np.ndarray]]:
    """Stable equal-count strata based only on D_student residual magnitude."""
    if len(residual) != K:
        raise RuntimeError(f"expected K={K} residual rows, got {len(residual)}")
    norms = np.linalg.norm(residual, axis=1)
    order = np.argsort(norms, kind="stable")
    chunks = [np.asarray(x, dtype=np.int64) for x in np.array_split(order, n_strata)]
    if any(len(chunk) < 2 for chunk in chunks):
        raise RuntimeError("every norm stratum must contain at least two anchors")
    labels = np.empty(len(residual), dtype=np.int64)
    for label, chunk in enumerate(chunks):
        labels[chunk] = label
    return labels, chunks


def derangement(indices: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Random derangement of one stratum; no anchor keeps its true residual."""
    while True:
        candidate = indices[rng.permutation(len(indices))]
        if np.all(candidate != indices):
            return candidate


def matched_permutation_bank(
    chunks: list[np.ndarray], n: int, seed: int
) -> list[np.ndarray]:
    """Unique permutations that reassign residuals only within norm strata."""
    rng = np.random.default_rng(seed)
    identity = np.arange(K, dtype=np.int64)
    seen = {identity.tobytes()}
    out: list[np.ndarray] = []
    while len(out) < n:
        p = identity.copy()
        for chunk in chunks:
            p[chunk] = derangement(chunk, rng)
        key = p.tobytes()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def stratum_manifest(labels: np.ndarray) -> str:
    return base.sha256_lines([f"{i} {int(labels[i])}" for i in range(len(labels))])


def norm_match_diagnostic(residual: np.ndarray, bank: list[np.ndarray]) -> dict[str, float]:
    norms = np.linalg.norm(residual, axis=1)
    deltas = np.asarray(
        [np.mean(np.abs(norms - norms[p])) for p in bank], dtype=np.float64
    )
    return {
        "mean_abs_residual_norm_delta_mean": float(deltas.mean()),
        "mean_abs_residual_norm_delta_min": float(deltas.min()),
        "mean_abs_residual_norm_delta_max": float(deltas.max()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--n-strata", type=int, default=N_STRATA)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-scifact-norm-matched-coupling-k512.json"),
    )
    args = ap.parse_args()

    if args.seed != SEED:
        raise RuntimeError(f"protocol freezes seed={SEED}")
    if args.k != K:
        raise RuntimeError(f"protocol freezes K={K}")
    if args.n_null != N_NULL:
        raise RuntimeError(f"protocol freezes n_null={N_NULL}")
    if args.n_strata != N_STRATA:
        raise RuntimeError(f"protocol freezes n_strata={N_STRATA}")

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = side.text_only_data(root)

    # Reproduce the already frozen student/validation membership exactly.
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

    labels, chunks = residual_norm_strata(residual, N_STRATA)
    query_perms = matched_permutation_bank(chunks, N_NULL, args.seed + 600_000)
    document_perms = matched_permutation_bank(chunks, N_NULL, args.seed + 700_000)
    for j in range(N_NULL):
        if np.array_equal(query_perms[j], document_perms[j]):
            raise RuntimeError(f"independent matched-null permutations coincide at {j}")

    # Freeze all A-side map state and null assignments before opening test grades.
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
        "norm_strata_sha256": stratum_manifest(labels),
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

    # D_test relevance grades are first read here, after map/strata/null banks freeze.
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
    semantic_boot = side.bootstrap_summary(semantic_per_query, args.seed + 800_000)
    coherence_boot = side.bootstrap_summary(coherence_per_query, args.seed + 900_000)
    semantic_p = coupling.finite_bank_p(true_global, coupled_global)

    result = {
        "experiment": "Pontifex SciFact norm-matched coupling specificity K=512",
        "classification": "prospective mechanism follow-up after the global-permutation K=512 result",
        "k": K,
        "n_null": N_NULL,
        "n_residual_norm_strata": N_STRATA,
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder identities; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; residual norms and strata defined here",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only tau/lambda selection",
            "D_test": "official SciFact test qrels loaded only after map, norm strata and all null permutations are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "null_contract": {
            "matching_variable": "L2 norm of the K=512 D_student residual vector",
            "stratification": "8 stable equal-count quantile strata (64 anchors each)",
            "identity_destroyed": "every within-stratum permutation is a derangement; no anchor retains its true residual",
            "coupled": "same norm-matched permutation applied to query and document maps",
            "independent": "different norm-matched permutations applied to query and document maps",
            "diagnostic_query_bank": norm_match_diagnostic(residual, query_perms),
            "diagnostic_document_bank": norm_match_diagnostic(residual, document_perms),
        },
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "manifests": frozen_manifest,
        "test_ndcg_at_10": {
            "TRUE": true_global,
            "NORM_MATCHED_COUPLED_mean": float(coupled_global.mean()),
            "NORM_MATCHED_COUPLED_median": float(np.median(coupled_global)),
            "NORM_MATCHED_COUPLED_min": float(coupled_global.min()),
            "NORM_MATCHED_COUPLED_max": float(coupled_global.max()),
            "NORM_MATCHED_INDEPENDENT_mean": float(independent_global.mean()),
            "NORM_MATCHED_INDEPENDENT_median": float(np.median(independent_global)),
            "NORM_MATCHED_INDEPENDENT_min": float(independent_global.min()),
            "NORM_MATCHED_INDEPENDENT_max": float(independent_global.max()),
        },
        "primary_contrasts": {
            "semantic_specificity_TRUE_minus_NORM_MATCHED_COUPLED_mean": float(
                true_global - coupled_global.mean()
            ),
            "semantic_specificity_finite_bank_p_upper": semantic_p,
            "semantic_specificity_paired_query_bootstrap": semantic_boot,
            "shared_warp_NORM_MATCHED_COUPLED_mean_minus_INDEPENDENT_mean": float(
                coupled_global.mean() - independent_global.mean()
            ),
            "shared_warp_paired_query_bootstrap": coherence_boot,
        },
        "predeclared_decision": {
            "semantic_specificity_supported": bool(
                semantic_boot["ci95_percentile_low"] > 0.0 and semantic_p <= 0.05
            ),
            "shared_warp_coherence_supported": bool(coherence_boot["ci95_percentile_low"] > 0.0),
        },
        "interpretation_boundary": {
            "evidence": "whether exact residual-to-anchor identity adds held-out SciFact utility beyond a shared warp that preserves coarse residual-magnitude strata, and whether the same matched deformation beats independent matched deformations",
            "not_evidence": "low-budget transport, physical torus, causal semantic locality, universal transport superiority, native-B superiority, or Assembly/student generalization",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
