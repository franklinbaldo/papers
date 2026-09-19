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
"""Coupling-specificity null for the Pontifex SciFact residual map.

The experiment is deliberately label-sealed until the map, hyperparameters and
all null permutations are frozen. It never encodes B/MPNet coordinates for
SciFact test queries or corpus documents.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import scifact_residual_side_ablation as side
import scifact_transport as base


def permutation_bank(k: int, n: int, seed: int) -> list[np.ndarray]:
    """Deterministic unique non-identity permutations."""
    rng = np.random.default_rng(seed)
    identity = np.arange(k, dtype=np.int64)
    seen = {identity.tobytes()}
    out: list[np.ndarray] = []
    while len(out) < n:
        p = rng.permutation(k).astype(np.int64)
        key = p.tobytes()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def permutation_manifest(bank: list[np.ndarray]) -> str:
    return base.sha256_lines([" ".join(map(str, p.tolist())) for p in bank])


def local_weights(x: np.ndarray, anchors: np.ndarray, tau: float) -> np.ndarray:
    sims = base.l2norm(x) @ base.l2norm(anchors).T
    return base.softmax_rows(sims / tau).astype(np.float32)


def mapped(
    coarse: np.ndarray,
    weights: np.ndarray,
    residual: np.ndarray,
    permutation: np.ndarray | None,
    lam: float,
) -> np.ndarray:
    bank = residual if permutation is None else residual[permutation]
    return (coarse + lam * (weights @ bank)).astype(np.float32)


def finite_bank_p(true_score: float, null_scores: np.ndarray) -> float:
    return float((1 + int(np.sum(null_scores >= true_score))) / (len(null_scores) + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=256)
    ap.add_argument("--n-null", type=int, default=31)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument(
        "--cache-dir", type=Path, default=Path(".cache/pontifex-scifact")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-scifact-coupling-specificity.json")
    )
    args = ap.parse_args()

    if args.k != 256:
        raise RuntimeError("protocol freezes the experiment at K=256")
    if args.n_null != 31:
        raise RuntimeError("protocol freezes a 31-permutation null bank")

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
    if len(student_ids) < args.k:
        raise RuntimeError(f"K={args.k} exceeds student pool {len(student_ids)}")

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

    # Phase 1: freeze all map information without test relevance grades.
    aa = a_student[: args.k]
    bb = b_student[: args.k]
    tau, lam, val_loss, coarse, residual = base.select_torus(aa, bb, a_val, b_val)
    query_perms = permutation_bank(args.k, args.n_null, args.seed + 100_000)
    document_perms = permutation_bank(args.k, args.n_null, args.seed + 200_000)

    # Guard against accidental same-permutation independent cells.
    for j in range(args.n_null):
        if np.array_equal(query_perms[j], document_perms[j]):
            raise RuntimeError(f"independent null permutations coincide at index {j}")

    coarse_q = base.apply_procrustes(a_test, *coarse).astype(np.float32)
    coarse_d = base.apply_procrustes(a_docs, *coarse).astype(np.float32)
    wq = local_weights(a_test, aa, tau)
    wd = local_weights(a_docs, aa, tau)

    frozen_manifest = {
        "anchor_ids_sha256": base.sha256_lines(student_ids[: args.k]),
        "student_ids_sha256": base.sha256_lines(student_ids),
        "validation_ids_sha256": base.sha256_lines(val_ids),
        "test_ids_sha256": base.sha256_lines(test_ids),
        "corpus_ids_sha256": base.sha256_lines(data.corpus_ids),
        "query_permutation_bank_sha256": permutation_manifest(query_perms),
        "document_permutation_bank_sha256": permutation_manifest(document_perms),
    }

    # Phase 2: unseal D_test grades only after fit/selection/permutations freeze.
    test_qrels = base.load_qrels(root / "qrels" / "test.tsv")
    if sorted(test_qrels) != test_ids:
        raise RuntimeError("test qrel manifest changed between membership and grade load")

    true_q = mapped(coarse_q, wq, residual, None, lam)
    true_d = mapped(coarse_d, wd, residual, None, lam)
    true_nd = side.per_query_ndcg(
        test_qrels, test_ids, data.corpus_ids, side.scores(true_q, true_d)
    )

    coupled_rows: list[np.ndarray] = []
    independent_rows: list[np.ndarray] = []
    for qp, dp in zip(query_perms, document_perms, strict=True):
        q_scrambled = mapped(coarse_q, wq, residual, qp, lam)
        d_coupled = mapped(coarse_d, wd, residual, qp, lam)
        d_independent = mapped(coarse_d, wd, residual, dp, lam)
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
    total_per_query = true_nd - independent.mean(axis=0)

    result = {
        "experiment": "Pontifex SciFact coupling-specificity null",
        "classification": "prospective mechanism follow-up after side-ablation observation",
        "k": args.k,
        "n_null": args.n_null,
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder weights; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs",
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
            "semantic_specificity_TRUE_minus_COUPLED_median": float(
                true_global - np.median(coupled_global)
            ),
            "semantic_specificity_finite_bank_p_upper": finite_bank_p(
                true_global, coupled_global
            ),
            "shared_warp_COUPlED_median_minus_INDEPENDENT_median": float(
                np.median(coupled_global) - np.median(independent_global)
            ),
            "semantic_specificity_paired_query_bootstrap": side.bootstrap_summary(
                semantic_per_query, args.seed + 300_000
            ),
            "shared_warp_paired_query_bootstrap": side.bootstrap_summary(
                coherence_per_query, args.seed + 400_000
            ),
            "TRUE_minus_INDEPENDENT_paired_query_bootstrap": side.bootstrap_summary(
                total_per_query, args.seed + 500_000
            ),
        },
        "null_global_ndcg_at_10": {
            "COUPLED": [float(x) for x in coupled_global],
            "INDEPENDENT": [float(x) for x in independent_global],
        },
        "interpretation_boundary": {
            "evidence": "whether correct train-side residual-to-anchor correspondence adds held-out SciFact utility beyond a shared scrambled warp, and whether shared scrambling beats independent scrambling",
            "not_evidence": "physical torus, causal semantic locality, universal transport superiority, or native-B superiority",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
