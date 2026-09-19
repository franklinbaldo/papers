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
"""Frozen query/document-side residual ablation for BEIR SciFact.

The crucial structural property is label sealing: qrel IDs are read before fit so
canonical split membership is known, but relevance grades are not loaded until
all K-specific transports and hyperparameters have been frozen.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

import scifact_transport as base


def qrel_ids(path: Path) -> list[str]:
    ids: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ids.add(str(row["query-id"]))
    return sorted(ids)


def text_only_data(root: Path) -> tuple[base.Data, list[str], list[str]]:
    corpus_rows = base.load_jsonl(root / "corpus.jsonl")
    query_rows = base.load_jsonl(root / "queries.jsonl")
    train_ids = qrel_ids(root / "qrels" / "train.tsv")
    test_ids = qrel_ids(root / "qrels" / "test.tsv")
    data = base.Data(
        corpus_ids=[str(r["_id"]) for r in corpus_rows],
        corpus_texts=[
            (" ".join([str(r.get("title", "")), str(r.get("text", ""))])).strip()
            for r in corpus_rows
        ],
        queries={str(r["_id"]): str(r["text"]).strip() for r in query_rows},
        train_qrels={qid: {} for qid in train_ids},
        test_qrels={qid: {} for qid in test_ids},
    )
    return data, train_ids, test_ids


def per_query_ndcg(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    scores: np.ndarray,
    k: int = 10,
) -> np.ndarray:
    vals = np.empty(len(qids), dtype=np.float64)
    for i, qid in enumerate(qids):
        order = np.argsort(scores[i])[::-1][:k]
        rels = np.asarray([qrels[qid].get(doc_ids[j], 0) for j in order], dtype=np.float64)
        discounts = 1.0 / np.log2(np.arange(2, len(rels) + 2))
        dcg = float(np.sum((np.power(2.0, rels) - 1.0) * discounts))
        ideal = np.sort(np.asarray(list(qrels[qid].values()), dtype=np.float64))[::-1][:k]
        idcg = float(
            np.sum((np.power(2.0, ideal) - 1.0) / np.log2(np.arange(2, len(ideal) + 2)))
        )
        vals[i] = 0.0 if idcg == 0.0 else dcg / idcg
    return vals


def bootstrap_summary(delta: np.ndarray, seed: int, n_boot: int = 5000) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    n = len(delta)
    draws = rng.integers(0, n, size=(n_boot, n))
    means = delta[draws].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return {
        "mean_delta": float(delta.mean()),
        "median_delta": float(np.median(delta)),
        "ci95_percentile_low": float(lo),
        "ci95_percentile_high": float(hi),
        "bootstrap_probability_mean_gt_0": float(np.mean(means > 0.0)),
        "n_queries": int(n),
        "bootstrap_resamples": int(n_boot),
    }


def scores(q: np.ndarray, d: np.ndarray) -> np.ndarray:
    return base.l2norm(q) @ base.l2norm(d).T


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", nargs="+", type=int, default=[16, 32, 64, 128, 256, 512])
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-scifact"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-scifact-side-ablation.json"))
    args = ap.parse_args()

    root = base.ensure_dataset(args.cache_dir)
    data, train_ids, test_ids = text_only_data(root)

    test_texts = {data.queries[q].strip() for q in test_ids}
    eligible_ids = [q for q in train_ids if data.queries[q].strip() not in test_texts]
    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(len(eligible_ids))
    eligible_ids = [eligible_ids[i] for i in perm]
    cut = max(1, int(math.floor(0.80 * len(eligible_ids))))
    student_ids = eligible_ids[:cut]
    val_ids = eligible_ids[cut:]
    budgets = sorted({k for k in args.budgets if 4 <= k <= len(student_ids)})
    if 256 not in budgets:
        raise RuntimeError("predeclared primary K=256 is unavailable")

    emb = base.encode_or_load(data, args.cache_dir / "scifact-minilm-mpnet.npz")
    train_pos = {qid: i for i, qid in enumerate(train_ids)}
    student_idx = np.asarray([train_pos[q] for q in student_ids], dtype=np.int64)
    val_idx = np.asarray([train_pos[q] for q in val_ids], dtype=np.int64)
    a_student, b_student = emb["a_train"][student_idx], emb["b_train"][student_idx]
    a_val, b_val = emb["a_train"][val_idx], emb["b_train"][val_idx]
    a_test, b_test = emb["a_test"], emb["b_test"]
    a_docs, b_docs = emb["a_docs"], emb["b_docs"]

    # Phase 1: fit/select using D_student and D_val only. No relevance grades exist in memory.
    frozen: list[dict] = []
    for k in budgets:
        aa, bb = a_student[:k], b_student[:k]
        tau, lam, val_loss, coarse, residual = base.select_torus(aa, bb, a_val, b_val)
        coarse_q = base.apply_procrustes(a_test, *coarse).astype(np.float32)
        coarse_d = base.apply_procrustes(a_docs, *coarse).astype(np.float32)
        residual_q = base.apply_torus(a_test, aa, residual, coarse, tau, lam).astype(np.float32)
        residual_d = base.apply_torus(a_docs, aa, residual, coarse, tau, lam).astype(np.float32)
        frozen.append(
            {
                "k": int(k),
                "anchor_ids_sha256": base.sha256_lines(student_ids[:k]),
                "tau": float(tau),
                "lambda": float(lam),
                "validation_coordinate_loss": float(val_loss),
                "coarse_q": coarse_q,
                "coarse_d": coarse_d,
                "residual_q": residual_q,
                "residual_d": residual_d,
            }
        )

    # Phase 2: only now unseal D_test relevance grades. Nothing below may alter a fitted map.
    test_qrels = base.load_qrels(root / "qrels" / "test.tsv")
    if sorted(test_qrels) != test_ids:
        raise RuntimeError("test qrel ID manifest changed between split-membership and grade load")

    rows: list[dict] = []
    for item in frozen:
        k = item["k"]
        cq, cd = item["coarse_q"], item["coarse_d"]
        rq, rd = item["residual_q"], item["residual_d"]
        cell_scores = {
            "CC_coarse_query_coarse_document": scores(cq, cd),
            "RC_residual_query_coarse_document": scores(rq, cd),
            "CR_coarse_query_residual_document": scores(cq, rd),
            "RR_residual_query_residual_document": scores(rq, rd),
        }
        nd = {name: per_query_ndcg(test_qrels, test_ids, data.corpus_ids, s) for name, s in cell_scores.items()}
        cc = nd["CC_coarse_query_coarse_document"]
        rc = nd["RC_residual_query_coarse_document"]
        cr = nd["CR_coarse_query_residual_document"]
        rr = nd["RR_residual_query_residual_document"]
        deltas = {
            "query_side_Q_RC_minus_CC": rc - cc,
            "document_side_D_CR_minus_CC": cr - cc,
            "full_RR_minus_CC": rr - cc,
            "interaction_RR_minus_RC_minus_CR_plus_CC": rr - rc - cr + cc,
        }
        rows.append(
            {
                "shared_correspondences_k": k,
                "primary_mechanism_point": k == 256,
                "anchor_ids_sha256": item["anchor_ids_sha256"],
                "selection": {
                    "tau": item["tau"],
                    "lambda": item["lambda"],
                    "D_val_coordinate_loss": item["validation_coordinate_loss"],
                },
                "test_ndcg_at_10": {name: float(v.mean()) for name, v in nd.items()},
                "paired_query_bootstrap": {
                    name: bootstrap_summary(delta, args.seed + k + i * 100000)
                    for i, (name, delta) in enumerate(deltas.items())
                },
                "B_coordinate_diagnostics": {
                    "query_coarse_mean_cosine": float(np.mean(base.row_cosine(cq, b_test))),
                    "query_residual_mean_cosine": float(np.mean(base.row_cosine(rq, b_test))),
                    "document_coarse_mean_cosine": float(np.mean(base.row_cosine(cd, b_docs))),
                    "document_residual_mean_cosine": float(np.mean(base.row_cosine(rd, b_docs))),
                },
            }
        )

    result = {
        "experiment": "Pontifex SciFact residual-side ablation",
        "classification": "held-out external mechanism ablation",
        "primary_k": 256,
        "split_contract": {
            "D_assembly": "SciFact text/split membership plus frozen encoder weights; no relevance grades",
            "D_student": "80% deterministic filtered train-query representation pairs",
            "D_val": "20% deterministic filtered train-query representation pairs; coordinate-only hyperparameter selection",
            "D_test": "test relevance grades loaded only after every K-specific transport is frozen",
            "task_labels_used_for_fit_or_selection": 0,
        },
        "manifests": {
            "student_ids_sha256": base.sha256_lines(student_ids),
            "validation_ids_sha256": base.sha256_lines(val_ids),
            "test_ids_sha256": base.sha256_lines(test_ids),
            "corpus_ids_sha256": base.sha256_lines(data.corpus_ids),
        },
        "interpretation_boundary": {
            "evidence": "which side of a frozen residual transport contributes to held-out SciFact retrieval and whether the full residual beats the same Procrustes coarse map",
            "not_evidence": "physical torus, causal semantic locality, or general transport superiority",
        },
        "results_by_budget": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
