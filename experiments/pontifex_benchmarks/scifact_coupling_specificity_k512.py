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
"""K=512 scaling diagnostic for SciFact coupling specificity.

This is prospective only relative to the already observed K=256 coupling-null and
K=512 residual-side results. It keeps D_test sealed until the map and both null
permutation banks are frozen and never encodes target-space B coordinates for
SciFact test queries or corpus documents.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import scifact_coupling_specificity as prior
import scifact_residual_side_ablation as side
import scifact_transport as base

K = 512
N_NULL = 63
SEED = 20260919
EXPECTED_STUDENT_SHA = "bd5775940da2cb20d0ec5ee5ec4c9e35d871f82f12c0ff87e1955e38bd69ccf5"
EXPECTED_VAL_SHA = "7a699f93186bd3b8c6042c8941b045ed8197438fceb396b0d7178af34e9c349c"
EXPECTED_TEST_SHA = "c307ee1faa37715704375e5c59a071b0c579b3114bedcbf263d43111a2f15ebf"
EXPECTED_CORPUS_SHA = "bcb266241b6c749fe993de0353d1ce95cc3b9fbd47b86d356ba54acab09ccfd4"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-scifact-coupling-specificity-k512.json"),
    )
    args = ap.parse_args()
    if args.seed != SEED:
        raise RuntimeError(f"protocol freezes seed={SEED}")

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

    manifests = {
        "student_ids_sha256": base.sha256_lines(student_ids),
        "validation_ids_sha256": base.sha256_lines(val_ids),
        "test_ids_sha256": base.sha256_lines(test_ids),
        "corpus_ids_sha256": base.sha256_lines(data.corpus_ids),
    }
    expected = {
        "student_ids_sha256": EXPECTED_STUDENT_SHA,
        "validation_ids_sha256": EXPECTED_VAL_SHA,
        "test_ids_sha256": EXPECTED_TEST_SHA,
        "corpus_ids_sha256": EXPECTED_CORPUS_SHA,
    }
    if manifests != expected:
        raise RuntimeError(f"frozen split manifest mismatch: {manifests} != {expected}")

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

    # Phase 1: freeze map, selector output, and all null assignments without D_test grades.
    aa = a_student[:K]
    bb = b_student[:K]
    tau, lam, val_loss, coarse, residual = base.select_torus(aa, bb, a_val, b_val)
    query_perms = prior.permutation_bank(K, N_NULL, args.seed + 610_000)
    document_perms = prior.permutation_bank(K, N_NULL, args.seed + 710_000)
    for j in range(N_NULL):
        if np.array_equal(query_perms[j], document_perms[j]):
            raise RuntimeError(f"independent null permutations coincide at index {j}")

    coarse_q = base.apply_procrustes(a_test, *coarse).astype(np.float32)
    coarse_d = base.apply_procrustes(a_docs, *coarse).astype(np.float32)
    wq = prior.local_weights(a_test, aa, tau)
    wd = prior.local_weights(a_docs, aa, tau)

    frozen_manifest = {
        **manifests,
        "anchor_ids_sha256": base.sha256_lines(student_ids[:K]),
        "query_permutation_bank_sha256": prior.permutation_manifest(query_perms),
        "document_permutation_bank_sha256": prior.permutation_manifest(document_perms),
    }

    # Phase 2: unseal D_test only after every learned/null object above is immutable.
    test_qrels = base.load_qrels(root / "qrels" / "test.tsv")
    if sorted(test_qrels) != test_ids:
        raise RuntimeError("test qrel manifest changed between membership and grade load")

    true_q = prior.mapped(coarse_q, wq, residual, None, lam)
    true_d = prior.mapped(coarse_d, wd, residual, None, lam)
    true_nd = side.per_query_ndcg(
        test_qrels, test_ids, data.corpus_ids, side.scores(true_q, true_d)
    )

    coupled_rows: list[np.ndarray] = []
    independent_rows: list[np.ndarray] = []
    for qp, dp in zip(query_perms, document_perms, strict=True):
        q_scrambled = prior.mapped(coarse_q, wq, residual, qp, lam)
        d_coupled = prior.mapped(coarse_d, wd, residual, qp, lam)
        d_independent = prior.mapped(coarse_d, wd, residual, dp, lam)
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
    semantic_boot = side.bootstrap_summary(semantic_per_query, args.seed + 810_000)
    coherence_boot = side.bootstrap_summary(coherence_per_query, args.seed + 910_000)
    finite_p = prior.finite_bank_p(true_global, coupled_global)

    semantic_supported = bool(
        semantic_boot["ci95_percentile_low"] > 0.0 and finite_p <= 0.05
    )
    coherence_supported = bool(coherence_boot["ci95_percentile_low"] > 0.0)

    result = {
        "experiment": "Pontifex SciFact coupling-specificity scaling diagnostic K=512",
        "classification": "prospective scaling diagnostic after K=256 coupling-null and K=512 side-ablation observations",
        "k": K,
        "n_null": N_NULL,
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder weights; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs; first 512 are anchors",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only tau/lambda selection",
            "D_test": "test relevance grades loaded only after map and all null permutations are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "manifests": frozen_manifest,
        "test_ndcg_at_10": {
            "TRUE": true_global,
            "COUPLED_NULL_mean": float(coupled_global.mean()),
            "COUPLED_NULL_median": float(np.median(coupled_global)),
            "COUPLED_NULL_min": float(coupled_global.min()),
            "COUPLED_NULL_max": float(coupled_global.max()),
            "INDEPENDENT_NULL_mean": float(independent_global.mean()),
            "INDEPENDENT_NULL_median": float(np.median(independent_global)),
            "INDEPENDENT_NULL_min": float(independent_global.min()),
            "INDEPENDENT_NULL_max": float(independent_global.max()),
        },
        "primary_contrasts": {
            "semantic_specificity_TRUE_minus_COUPLED_mean": float(
                true_global - coupled_global.mean()
            ),
            "semantic_specificity_finite_bank_p_upper": finite_p,
            "semantic_specificity_paired_query_bootstrap": semantic_boot,
            "shared_warp_COUPLED_mean_minus_INDEPENDENT_mean": float(
                coupled_global.mean() - independent_global.mean()
            ),
            "shared_warp_paired_query_bootstrap": coherence_boot,
        },
        "predeclared_decision": {
            "semantic_specificity_supported": semantic_supported,
            "shared_warp_coherence_supported": coherence_supported,
        },
        "null_global_ndcg_at_10": {
            "COUPLED": [float(x) for x in coupled_global],
            "INDEPENDENT": [float(x) for x in independent_global],
        },
        "interpretation_boundary": {
            "evidence": "whether correct residual-to-anchor correspondence contributes SciFact retrieval utility beyond a generic shared warp at K=512, and whether shared two-sided warping remains useful when correspondence is destroyed",
            "not_evidence": "low-budget transport, physical torus, causal semantic locality, universal transport superiority, or native-B superiority",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
