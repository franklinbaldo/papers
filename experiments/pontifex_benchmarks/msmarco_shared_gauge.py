# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "ir_datasets>=0.5.11",
#   "numpy>=2.0",
#   "pyserini>=2.4.0",
#   "scikit-learn>=1.7",
# ]
# ///
"""Prospective shared-gauge follow-up to the frozen MS MARCO transport pilot.

The parent pilot fitted query and document transports independently. This follow-up preserves
its external task, candidate manifest, train/validation/test boundary and 2K total paired
observation budget, but ties the learned linear/orthogonal orientation across retrieval sides.
Dev qrels are opened only after every ranking is frozen.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pyserini.encode import AnceQueryEncoder, TctColBertQueryEncoder
from sklearn.linear_model import Ridge

from msmarco_transport_pilot import (
    INDEX_A,
    INDEX_B,
    KS,
    LAMBDAS,
    MODEL_A_QUERY,
    MODEL_B_QUERY,
    RIDGE_ALPHAS,
    SEED,
    TAUS,
    apply_procrustes,
    bm25_rankings,
    coordinate_loss,
    derangement,
    encode_many,
    fit_pontifex,
    fit_procrustes,
    fit_ridge,
    freeze_rankings,
    l2norm,
    load_relevant,
    load_store,
    mrr_at_10,
    residual_predict,
    select_train_queries,
    sha_lines,
    split_pairs,
)

EXPECTED_CANDIDATE_ROWS_SHA = "a129eadf935f495914f69f9f74266f4421751b091e0925802a7ad0b2c086d1f1"
EXPECTED_QUERY_IDS_SHA = "1ee39d7850762f834d6b4c851534814f2354c21952027df2a85b10eab0af0520"


@dataclass
class TiedProcrustes:
    w: np.ndarray
    aq_mean: np.ndarray
    bq_mean: np.ndarray
    ad_mean: np.ndarray
    bd_mean: np.ndarray

    def map_query(self, x: np.ndarray) -> np.ndarray:
        return ((x - self.aq_mean) @ self.w + self.bq_mean).astype(np.float32)

    def map_document(self, x: np.ndarray) -> np.ndarray:
        return ((x - self.ad_mean) @ self.w + self.bd_mean).astype(np.float32)


@dataclass
class TiedRidge:
    model: Ridge
    aq_mean: np.ndarray
    bq_mean: np.ndarray
    ad_mean: np.ndarray
    bd_mean: np.ndarray

    def map_query(self, x: np.ndarray) -> np.ndarray:
        return (self.model.predict(x - self.aq_mean) + self.bq_mean).astype(np.float32)

    def map_document(self, x: np.ndarray) -> np.ndarray:
        return (self.model.predict(x - self.ad_mean) + self.bd_mean).astype(np.float32)


@dataclass
class TiedPontifex:
    coarse: TiedProcrustes
    aq_anchor: np.ndarray
    q_residual: np.ndarray
    ad_anchor: np.ndarray
    d_residual: np.ndarray
    tau: float
    lam: float

    def map_query(self, x: np.ndarray) -> np.ndarray:
        return self.coarse.map_query(x) + self.lam * residual_predict(
            x, self.aq_anchor, self.q_residual, self.tau
        )

    def map_document(self, x: np.ndarray) -> np.ndarray:
        return self.coarse.map_document(x) + self.lam * residual_predict(
            x, self.ad_anchor, self.d_residual, self.tau
        )


def _means(aq: np.ndarray, bq: np.ndarray, ad: np.ndarray, bd: np.ndarray):
    return (
        aq.mean(axis=0, keepdims=True).astype(np.float32),
        bq.mean(axis=0, keepdims=True).astype(np.float32),
        ad.mean(axis=0, keepdims=True).astype(np.float32),
        bd.mean(axis=0, keepdims=True).astype(np.float32),
    )


def fit_tied_procrustes(
    aq: np.ndarray, bq: np.ndarray, ad: np.ndarray, bd: np.ndarray
) -> TiedProcrustes:
    aqm, bqm, adm, bdm = _means(aq, bq, ad, bd)
    cross = (aq - aqm).T @ (bq - bqm) + (ad - adm).T @ (bd - bdm)
    u, _, vt = np.linalg.svd(cross, full_matrices=False)
    w = (u @ vt).astype(np.float32)
    return TiedProcrustes(w, aqm, bqm, adm, bdm)


def mean_two_side_loss(q_pred, q_true, d_pred, d_true) -> float:
    return 0.5 * (coordinate_loss(q_pred, q_true) + coordinate_loss(d_pred, d_true))


def fit_tied_ridge(
    aq: np.ndarray,
    bq: np.ndarray,
    ad: np.ndarray,
    bd: np.ndarray,
    aq_val: np.ndarray,
    bq_val: np.ndarray,
    ad_val: np.ndarray,
    bd_val: np.ndarray,
) -> tuple[TiedRidge, dict]:
    aqm, bqm, adm, bdm = _means(aq, bq, ad, bd)
    x = np.vstack([aq - aqm, ad - adm])
    y = np.vstack([bq - bqm, bd - bdm])
    best = None
    best_state = None
    for alpha in RIDGE_ALPHAS:
        model = Ridge(alpha=alpha, fit_intercept=False).fit(x, y)
        state = TiedRidge(model, aqm, bqm, adm, bdm)
        loss = mean_two_side_loss(
            state.map_query(aq_val),
            bq_val,
            state.map_document(ad_val),
            bd_val,
        )
        candidate = (loss, alpha)
        if best is None or candidate < best:
            best = candidate
            best_state = state
    assert best is not None and best_state is not None
    return best_state, {"alpha": best[1], "D_val_two_side_coordinate_loss": best[0]}


def fit_tied_pontifex(
    aq: np.ndarray,
    bq: np.ndarray,
    ad: np.ndarray,
    bd: np.ndarray,
    aq_val: np.ndarray,
    bq_val: np.ndarray,
    ad_val: np.ndarray,
    bd_val: np.ndarray,
) -> tuple[TiedPontifex, dict]:
    coarse = fit_tied_procrustes(aq, bq, ad, bd)
    q_residual = (bq - coarse.map_query(aq)).astype(np.float32)
    d_residual = (bd - coarse.map_document(ad)).astype(np.float32)
    q_coarse_val = coarse.map_query(aq_val)
    d_coarse_val = coarse.map_document(ad_val)
    best = None
    for tau in TAUS:
        q_local = residual_predict(aq_val, aq, q_residual, tau)
        d_local = residual_predict(ad_val, ad, d_residual, tau)
        for lam in LAMBDAS:
            loss = mean_two_side_loss(
                q_coarse_val + lam * q_local,
                bq_val,
                d_coarse_val + lam * d_local,
                bd_val,
            )
            candidate = (loss, tau, lam)
            if best is None or candidate < best:
                best = candidate
    assert best is not None
    loss, tau, lam = best
    return (
        TiedPontifex(coarse, aq.copy(), q_residual, ad.copy(), d_residual, tau, lam),
        {"tau": tau, "lambda": lam, "D_val_two_side_coordinate_loss": loss},
    )


def fitted_floats_tied_procrustes(state: TiedProcrustes) -> int:
    return int(
        state.w.size
        + state.aq_mean.size
        + state.bq_mean.size
        + state.ad_mean.size
        + state.bd_mean.size
    )


def fitted_floats_tied_ridge(state: TiedRidge) -> int:
    return int(
        np.asarray(state.model.coef_).size
        + state.aq_mean.size
        + state.bq_mean.size
        + state.ad_mean.size
        + state.bd_mean.size
    )


def fitted_floats_tied_pontifex(state: TiedPontifex) -> int:
    return int(
        fitted_floats_tied_procrustes(state.coarse)
        + state.aq_anchor.size
        + state.q_residual.size
        + state.ad_anchor.size
        + state.d_residual.size
        + 2
    )


def independent_rotation_disagreement(qproc, dproc) -> float:
    qw = np.asarray(qproc[0])
    dw = np.asarray(dproc[0])
    return float(np.linalg.norm(qw - dw, ord="fro") / math.sqrt(qw.shape[0]))


def min_k(rows: list[dict], key: str, target: float) -> int | None:
    for row in rows:
        if row[key] >= target:
            return int(row["K"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--a-store", type=Path, required=True)
    ap.add_argument("--b-store", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("msmarco-shared-gauge.json"))
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest["candidate_rows_sha256"] != EXPECTED_CANDIDATE_ROWS_SHA:
        raise RuntimeError("candidate-row manifest differs from frozen parent pilot")
    if manifest["query_ids_sha256"] != EXPECTED_QUERY_IDS_SHA:
        raise RuntimeError("pilot query manifest differs from frozen parent pilot")

    a_pids, a_docs_all = load_store(args.a_store)
    b_pids, b_docs_all = load_store(args.b_store)
    if a_pids != b_pids:
        raise AssertionError("ANCE and TCT feature stores do not have identical PID order")
    if sha_lines(a_pids) != manifest["explicit_extraction_pid_sequence_sha256"]:
        raise AssertionError("feature-store PID hash does not match frozen manifest")

    pid_to_row = {pid: i for i, pid in enumerate(a_pids)}
    transport_doc_pids = [str(x) for x in manifest["transport_doc_pids"]]
    candidate_pids = [str(x) for x in manifest["candidate_pids"]]
    if set(transport_doc_pids) & set(candidate_pids):
        raise AssertionError("document transport pool overlaps pilot candidates")

    doc_rows = np.asarray([pid_to_row[pid] for pid in transport_doc_pids], dtype=np.int64)
    doc_split = split_pairs(
        transport_doc_pids, a_docs_all[doc_rows], b_docs_all[doc_rows]
    )

    pilot_qids = [str(x) for x in manifest["pilot_qids"]]
    pilot_texts = [str(manifest["queries"][qid]) for qid in pilot_qids]
    train_qids, train_texts = select_train_queries(set(pilot_texts), n=1024)

    t0 = time.perf_counter()
    a_encoder = AnceQueryEncoder(MODEL_A_QUERY)
    a_queries = encode_many(a_encoder, train_texts + pilot_texts)
    a_encode_seconds = time.perf_counter() - t0
    del a_encoder

    t0 = time.perf_counter()
    b_encoder = TctColBertQueryEncoder(MODEL_B_QUERY)
    b_queries = encode_many(b_encoder, train_texts + pilot_texts)
    b_encode_seconds = time.perf_counter() - t0
    del b_encoder

    n_train_q = len(train_qids)
    query_split = split_pairs(train_qids, a_queries[:n_train_q], b_queries[:n_train_q])
    a_pilot_q = a_queries[n_train_q:]
    b_pilot_q = b_queries[n_train_q:]

    candidate_rows = np.asarray([pid_to_row[pid] for pid in candidate_pids], dtype=np.int64)
    a_candidate_docs = a_docs_all[candidate_rows]
    b_candidate_docs = b_docs_all[candidate_rows]
    candidate_pid_to_row = {pid: i for i, pid in enumerate(candidate_pids)}

    rankings: dict[str, dict[str, list[str]]] = {
        "BM25": bm25_rankings(manifest),
        "A_only": freeze_rankings(manifest, a_pilot_q, a_candidate_docs, candidate_pid_to_row),
        "B_oracle": freeze_rankings(manifest, b_pilot_q, b_candidate_docs, candidate_pid_to_row),
    }
    selection: dict[str, dict] = {}
    costs: dict[str, dict] = {}
    gauge_diagnostics: dict[str, dict] = {}

    qav = np.asarray(query_split["a_val"], dtype=np.float32)
    qbv = np.asarray(query_split["b_val"], dtype=np.float32)
    dav = np.asarray(doc_split["a_val"], dtype=np.float32)
    dbv = np.asarray(doc_split["b_val"], dtype=np.float32)

    for k in KS:
        aq = np.asarray(query_split["a_student"][:k], dtype=np.float32)
        bq = np.asarray(query_split["b_student"][:k], dtype=np.float32)
        ad = np.asarray(doc_split["a_student"][:k], dtype=np.float32)
        bd = np.asarray(doc_split["b_student"][:k], dtype=np.float32)

        # Reconstruct the parent separate-gauge controls in this same runner.
        qproc = fit_procrustes(aq, bq)
        dproc = fit_procrustes(ad, bd)
        rankings[f"Separate_Procrustes_K{k}"] = freeze_rankings(
            manifest,
            apply_procrustes(a_pilot_q, qproc),
            apply_procrustes(a_candidate_docs, dproc),
            candidate_pid_to_row,
        )

        qridge, qridge_sel = fit_ridge(aq, bq, qav, qbv)
        dridge, dridge_sel = fit_ridge(ad, bd, dav, dbv)
        rankings[f"Separate_Ridge_K{k}"] = freeze_rankings(
            manifest, qridge(a_pilot_q), dridge(a_candidate_docs), candidate_pid_to_row
        )

        qpont, qpont_sel = fit_pontifex(aq, bq, qav, qbv)
        dpont, dpont_sel = fit_pontifex(ad, bd, dav, dbv)
        rankings[f"Separate_Pontifex_K{k}"] = freeze_rankings(
            manifest, qpont(a_pilot_q), dpont(a_candidate_docs), candidate_pid_to_row
        )

        gauge_diagnostics[str(k)] = {
            "independent_procrustes_rotation_disagreement_normalized_frobenius": independent_rotation_disagreement(qproc, dproc)
        }

        # Tied Procrustes: one orientation, side-specific means.
        t0 = time.perf_counter()
        tied_proc = fit_tied_procrustes(aq, bq, ad, bd)
        tied_proc_fit = time.perf_counter() - t0
        t0 = time.perf_counter()
        rankings[f"Tied_Procrustes_K{k}"] = freeze_rankings(
            manifest,
            tied_proc.map_query(a_pilot_q),
            tied_proc.map_document(a_candidate_docs),
            candidate_pid_to_row,
        )
        tied_proc_map_rank = time.perf_counter() - t0

        t0 = time.perf_counter()
        tied_ridge, tied_ridge_sel = fit_tied_ridge(aq, bq, ad, bd, qav, qbv, dav, dbv)
        tied_ridge_fit = time.perf_counter() - t0
        t0 = time.perf_counter()
        rankings[f"Tied_Ridge_K{k}"] = freeze_rankings(
            manifest,
            tied_ridge.map_query(a_pilot_q),
            tied_ridge.map_document(a_candidate_docs),
            candidate_pid_to_row,
        )
        tied_ridge_map_rank = time.perf_counter() - t0

        t0 = time.perf_counter()
        tied_pont, tied_pont_sel = fit_tied_pontifex(aq, bq, ad, bd, qav, qbv, dav, dbv)
        tied_pont_fit = time.perf_counter() - t0
        t0 = time.perf_counter()
        rankings[f"Tied_Pontifex_K{k}"] = freeze_rankings(
            manifest,
            tied_pont.map_query(a_pilot_q),
            tied_pont.map_document(a_candidate_docs),
            candidate_pid_to_row,
        )
        tied_pont_map_rank = time.perf_counter() - t0

        # Type-preserving shuffled correspondence: destroy identity within each side,
        # then fit exactly the same tied-gauge architecture and validation procedure.
        qperm = derangement(k, SEED + 3000 + k)
        dperm = derangement(k, SEED + 4000 + k)
        t0 = time.perf_counter()
        tied_shuf, tied_shuf_sel = fit_tied_pontifex(
            aq, bq[qperm], ad, bd[dperm], qav, qbv, dav, dbv
        )
        tied_shuf_fit = time.perf_counter() - t0
        t0 = time.perf_counter()
        rankings[f"Tied_Shuffled_K{k}"] = freeze_rankings(
            manifest,
            tied_shuf.map_query(a_pilot_q),
            tied_shuf.map_document(a_candidate_docs),
            candidate_pid_to_row,
        )
        tied_shuf_map_rank = time.perf_counter() - t0

        selection[str(k)] = {
            "separate_ridge_query": qridge_sel,
            "separate_ridge_document": dridge_sel,
            "separate_pontifex_query": qpont_sel,
            "separate_pontifex_document": dpont_sel,
            "tied_ridge": tied_ridge_sel,
            "tied_pontifex": tied_pont_sel,
            "tied_shuffled": tied_shuf_sel,
        }
        supervision_bytes = int(
            k * (aq.shape[1] + bq.shape[1] + ad.shape[1] + bd.shape[1]) * 4
        )
        costs[str(k)] = {
            "paired_observations_total": 2 * k,
            "paired_representation_supervision_bytes_float32": supervision_bytes,
            "tied_procrustes_fitted_floats": fitted_floats_tied_procrustes(tied_proc),
            "tied_ridge_fitted_floats": fitted_floats_tied_ridge(tied_ridge),
            "tied_pontifex_fitted_floats": fitted_floats_tied_pontifex(tied_pont),
            "tied_procrustes_fit_seconds": tied_proc_fit,
            "tied_ridge_fit_selection_seconds": tied_ridge_fit,
            "tied_pontifex_fit_selection_seconds": tied_pont_fit,
            "tied_shuffled_fit_selection_seconds": tied_shuf_fit,
            "tied_procrustes_map_plus_rerank_seconds": tied_proc_map_rank,
            "tied_ridge_map_plus_rerank_seconds": tied_ridge_map_rank,
            "tied_pontifex_map_plus_rerank_seconds": tied_pont_map_rank,
            "tied_shuffled_map_plus_rerank_seconds": tied_shuf_map_rank,
        }

    # Evaluation boundary: qrels are opened only after every ranking above is frozen.
    relevant = load_relevant()
    scores = {name: mrr_at_10(ranking, relevant, pilot_qids) for name, ranking in rankings.items()}
    a_score = scores["A_only"]
    b_score = scores["B_oracle"]
    gap = b_score - a_score

    rows: list[dict] = []
    for k in KS:
        tied_pont_score = scores[f"Tied_Pontifex_K{k}"]
        frac = None if gap <= 0 else (tied_pont_score - a_score) / gap
        rows.append(
            {
                "K": k,
                "paired_observations_total": 2 * k,
                "Separate_Procrustes_MRR10": scores[f"Separate_Procrustes_K{k}"],
                "Separate_Ridge_MRR10": scores[f"Separate_Ridge_K{k}"],
                "Separate_Pontifex_MRR10": scores[f"Separate_Pontifex_K{k}"],
                "Tied_Procrustes_MRR10": scores[f"Tied_Procrustes_K{k}"],
                "Tied_Ridge_MRR10": scores[f"Tied_Ridge_K{k}"],
                "Tied_Pontifex_MRR10": tied_pont_score,
                "Tied_Shuffled_MRR10": scores[f"Tied_Shuffled_K{k}"],
                "Tied_Pontifex_fraction_of_B_utility_recovered": frac,
            }
        )

    target50 = None if gap <= 0 else a_score + 0.5 * gap
    target90 = None if gap <= 0 else a_score + 0.9 * gap
    frontier = {}
    for key in ("Tied_Procrustes_MRR10", "Tied_Ridge_MRR10", "Tied_Pontifex_MRR10"):
        frontier[key] = {
            "min_K_50pct": None if target50 is None else min_k(rows, key, target50),
            "min_K_90pct": None if target90 is None else min_k(rows, key, target90),
        }

    payload = {
        "experiment": "Pontifex MS MARCO Passage shared-gauge transport follow-up",
        "classification": "pilot; prospective post-result mechanism/fairness follow-up",
        "primary_metric": "MRR@10 on the frozen parent 256-query candidate pool",
        "spaces": {
            "A_index": INDEX_A,
            "A_query_encoder": MODEL_A_QUERY,
            "B_index": INDEX_B,
            "B_query_encoder": MODEL_B_QUERY,
            "pretraining_overlap_A_B": "pretraining_overlap_possible",
            "benchmark_training_overlap": "known_ms_marco_family_models",
        },
        "manifest": {
            "query_ids_sha256": manifest["query_ids_sha256"],
            "query_text_sha256": manifest["query_text_sha256"],
            "candidate_rows_sha256": manifest["candidate_rows_sha256"],
            "candidate_pid_sequence_sha256": manifest["candidate_pid_sequence_sha256"],
            "query_student_ids_sha256": sha_lines(list(query_split["student_ids"])),
            "query_val_ids_sha256": sha_lines(list(query_split["val_ids"])),
            "doc_student_ids_sha256": sha_lines(list(doc_split["student_ids"])),
            "doc_val_ids_sha256": sha_lines(list(doc_split["val_ids"])),
        },
        "leakage_audit": {
            "status": "PASS",
            "dev_qrels_used_for_candidate_generation": False,
            "dev_qrels_used_for_fit_or_selection": False,
            "task_labels_used_for_transport_fit_or_selection": 0,
            "candidate_pids_excluded_from_document_transport_fit": True,
            "dev_qrels_loaded_after_rankings_frozen": True,
            "shared_gauge_rule_applied_to_simple_baselines_and_pontifex": True,
            "parent_negative_result_preserved": True,
        },
        "pilot": {
            "queries": len(pilot_qids),
            "candidate_depth": manifest["candidate_depth"],
            "unique_candidate_pids": len(candidate_pids),
        },
        "encoder_seconds": {"ANCE": a_encode_seconds, "TCT": b_encode_seconds},
        "reference_scores": {
            "BM25_candidate_order_MRR10": scores["BM25"],
            "A_only_ANCE_MRR10": a_score,
            "B_oracle_TCT_MRR10": b_score,
            "B_minus_A_MRR10": gap,
        },
        "results_by_budget": rows,
        "selection": selection,
        "gauge_diagnostics": gauge_diagnostics,
        "costs": costs,
        "quality_matched": {
            "target_50pct_A_to_B": target50,
            "target_90pct_A_to_B": target90,
            "frontier": frontier,
        },
        "interpretation_boundary": {
            "primary_question": "whether tying the query/document orientation repairs retrieval under an unchanged 2K correspondence budget",
            "pontifex_specific_question": "whether tied Pontifex beats tied Procrustes, tied Ridge and tied shuffled correspondence at the same K",
            "not_evidence": "full-dev competitiveness or a leaderboard-comparable native full-corpus result",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
