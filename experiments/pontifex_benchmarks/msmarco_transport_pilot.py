# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "ir_datasets>=0.5.11",
#   "numpy>=2.0",
#   "pyserini>=2.4.0",
#   "scikit-learn>=1.7",
# ]
# ///
"""Run a frozen-candidate MS MARCO Passage transport pilot.

This is a PILOT, not the final 6,980-query benchmark. Adapters are fit and selected only from
MS MARCO train-query pairs and deterministic non-candidate corpus PID pairs. Dev qrels are
loaded only after every method/K has produced a frozen ranking over the label-blind BM25
candidate manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import ir_datasets
import numpy as np
from pyserini.encode import AnceQueryEncoder, TctColBertQueryEncoder
from sklearn.linear_model import Ridge

MODEL_A_QUERY = "castorini/ance-msmarco-passage"
MODEL_B_QUERY = "castorini/tct_colbert-v2-hnp-msmarco"
INDEX_A = "msmarco-v1-passage.ance"
INDEX_B = "msmarco-v1-passage.tct_colbert-v2-hnp"
TRAIN_DATASET = "msmarco-passage/train"
DEV_QRELS_DATASET = "msmarco-passage/dev/small"
SEED = 20260919
KS = (16, 32, 64, 128, 256, 512)
TAUS = (0.02, 0.05, 0.1, 0.2, 0.4)
LAMBDAS = (0.25, 0.5, 1.0, 1.5)
RIDGE_ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0)


def sha_lines(values: list[str]) -> str:
    h = hashlib.sha256()
    for value in values:
        h.update(str(value).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def l2norm(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def coordinate_loss(pred: np.ndarray, true: np.ndarray) -> float:
    return float(1.0 - np.mean(np.sum(l2norm(pred) * l2norm(true), axis=1)))


def softmax_rows(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / np.maximum(e.sum(axis=1, keepdims=True), 1e-12)


def fit_procrustes(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    am = a.mean(axis=0, keepdims=True)
    bm = b.mean(axis=0, keepdims=True)
    u, _, vt = np.linalg.svd((a - am).T @ (b - bm), full_matrices=False)
    return (u @ vt).astype(np.float32), am.astype(np.float32), bm.astype(np.float32)


def apply_procrustes(x: np.ndarray, state: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    w, am, bm = state
    return ((x - am) @ w + bm).astype(np.float32)


def residual_predict(x: np.ndarray, a_anchor: np.ndarray, residual: np.ndarray, tau: float) -> np.ndarray:
    sims = l2norm(x) @ l2norm(a_anchor).T
    return (softmax_rows(sims / tau) @ residual).astype(np.float32)


@dataclass
class PontifexMap:
    procrustes: tuple[np.ndarray, np.ndarray, np.ndarray]
    a_anchor: np.ndarray
    residual: np.ndarray
    tau: float
    lam: float

    def __call__(self, x: np.ndarray) -> np.ndarray:
        coarse = apply_procrustes(x, self.procrustes)
        return coarse + self.lam * residual_predict(x, self.a_anchor, self.residual, self.tau)


def fit_pontifex(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray) -> tuple[PontifexMap, dict]:
    proc = fit_procrustes(a, b)
    coarse_anchor = apply_procrustes(a, proc)
    residual = b - coarse_anchor
    coarse_val = apply_procrustes(a_val, proc)
    best = None
    for tau in TAUS:
        local = residual_predict(a_val, a, residual, tau)
        for lam in LAMBDAS:
            loss = coordinate_loss(coarse_val + lam * local, b_val)
            candidate = (loss, tau, lam)
            if best is None or candidate < best:
                best = candidate
    assert best is not None
    loss, tau, lam = best
    return PontifexMap(proc, a.copy(), residual.copy(), tau, lam), {
        "tau": tau,
        "lambda": lam,
        "D_val_coordinate_loss": loss,
    }


def fit_ridge(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray) -> tuple[Callable[[np.ndarray], np.ndarray], dict]:
    best = None
    best_model = None
    for alpha in RIDGE_ALPHAS:
        model = Ridge(alpha=alpha)
        model.fit(a, b)
        loss = coordinate_loss(model.predict(a_val).astype(np.float32), b_val)
        candidate = (loss, alpha)
        if best is None or candidate < best:
            best = candidate
            best_model = model
    assert best is not None and best_model is not None
    loss, alpha = best
    return lambda x: best_model.predict(x).astype(np.float32), {
        "alpha": alpha,
        "D_val_coordinate_loss": loss,
    }


def derangement(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.arange(n)
    for _ in range(10_000):
        perm = rng.permutation(n)
        if np.all(perm != base):
            return perm
    raise RuntimeError("unable to construct derangement")


def encode_many(encoder, texts: list[str]) -> np.ndarray:
    if hasattr(encoder, "encode_batch"):
        out = encoder.encode_batch(texts)
        return np.asarray(out, dtype=np.float32)
    rows = [np.asarray(encoder.encode(text), dtype=np.float32) for text in texts]
    return np.vstack(rows).astype(np.float32)


def load_store(path: Path) -> tuple[list[str], np.ndarray]:
    payload = np.load(path, allow_pickle=False)
    pids = [str(x) for x in payload["pids"].tolist()]
    vectors = np.asarray(payload["embeddings"], dtype=np.float32)
    if len(pids) != len(vectors):
        raise AssertionError("PID/vector length mismatch")
    return pids, vectors


def select_train_queries(pilot_texts: set[str], n: int = 1024) -> tuple[list[str], list[str]]:
    ds = ir_datasets.load(TRAIN_DATASET)
    pool: list[tuple[str, str]] = []
    for query in ds.queries_iter():
        qid = str(query.query_id)
        text = str(query.text).strip()
        if text and text not in pilot_texts:
            pool.append((qid, text))
        if len(pool) >= 4096:
            break
    pool.sort(key=lambda item: hashlib.sha256(f"pontifex-msmarco-train-v1\0{item[0]}".encode()).hexdigest())
    chosen = pool[:n]
    if len(chosen) < n:
        raise RuntimeError(f"only {len(chosen)} eligible train queries")
    return [x[0] for x in chosen], [x[1] for x in chosen]


def split_pairs(ids: list[str], a: np.ndarray, b: np.ndarray) -> dict[str, object]:
    if len(ids) != len(a) or len(ids) != len(b):
        raise AssertionError("split pair length mismatch")
    n_student = int(round(len(ids) * 0.8))
    n_student = min(max(n_student, max(KS)), len(ids) - 1)
    return {
        "student_ids": ids[:n_student],
        "val_ids": ids[n_student:],
        "a_student": a[:n_student],
        "b_student": b[:n_student],
        "a_val": a[n_student:],
        "b_val": b[n_student:],
    }


def freeze_rankings(
    manifest: dict,
    query_vectors: np.ndarray,
    doc_vectors: np.ndarray,
    candidate_pid_to_row: dict[str, int],
) -> dict[str, list[str]]:
    qids = manifest["pilot_qids"]
    rankings: dict[str, list[str]] = {}
    for qi, qid in enumerate(qids):
        rows = manifest["candidates"][qid]
        pids = [str(row["pid"]) for row in rows]
        matrix = np.vstack([doc_vectors[candidate_pid_to_row[pid]] for pid in pids])
        scores = matrix @ query_vectors[qi]
        order = np.argsort(-scores, kind="stable")
        rankings[qid] = [pids[int(i)] for i in order]
    return rankings


def bm25_rankings(manifest: dict) -> dict[str, list[str]]:
    return {
        qid: [str(row["pid"]) for row in manifest["candidates"][qid]]
        for qid in manifest["pilot_qids"]
    }


def load_relevant() -> dict[str, set[str]]:
    # Called only after every ranking has been frozen.
    ds = ir_datasets.load(DEV_QRELS_DATASET)
    relevant: dict[str, set[str]] = {}
    for qrel in ds.qrels_iter():
        if int(qrel.relevance) > 0:
            relevant.setdefault(str(qrel.query_id), set()).add(str(qrel.doc_id))
    return relevant


def mrr_at_10(rankings: dict[str, list[str]], relevant: dict[str, set[str]], qids: list[str]) -> float:
    total = 0.0
    for qid in qids:
        rel = relevant.get(qid, set())
        rr = 0.0
        for rank, pid in enumerate(rankings[qid][:10], start=1):
            if pid in rel:
                rr = 1.0 / rank
                break
        total += rr
    return total / len(qids)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--a-store", type=Path, required=True)
    ap.add_argument("--b-store", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("msmarco-transport-pilot.json"))
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
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
    a_doc_pairs = a_docs_all[doc_rows]
    b_doc_pairs = b_docs_all[doc_rows]
    doc_split = split_pairs(transport_doc_pids, a_doc_pairs, b_doc_pairs)

    pilot_qids = [str(x) for x in manifest["pilot_qids"]]
    pilot_texts = [str(manifest["queries"][qid]) for qid in pilot_qids]
    train_qids, train_texts = select_train_queries(set(pilot_texts), n=1024)

    print("encoding ANCE train+pilot queries", flush=True)
    t0 = time.perf_counter()
    a_encoder = AnceQueryEncoder(MODEL_A_QUERY)
    a_queries = encode_many(a_encoder, train_texts + pilot_texts)
    a_encode_seconds = time.perf_counter() - t0
    del a_encoder

    print("encoding TCT train+pilot queries", flush=True)
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

    for k in KS:
        if k > len(query_split["student_ids"]) or k > len(doc_split["student_ids"]):
            continue
        aq = np.asarray(query_split["a_student"][:k], dtype=np.float32)
        bq = np.asarray(query_split["b_student"][:k], dtype=np.float32)
        ad = np.asarray(doc_split["a_student"][:k], dtype=np.float32)
        bd = np.asarray(doc_split["b_student"][:k], dtype=np.float32)

        qproc = fit_procrustes(aq, bq)
        dproc = fit_procrustes(ad, bd)
        rankings[f"Procrustes_K{k}"] = freeze_rankings(
            manifest,
            apply_procrustes(a_pilot_q, qproc),
            apply_procrustes(a_candidate_docs, dproc),
            candidate_pid_to_row,
        )

        t0 = time.perf_counter()
        qridge, qridge_sel = fit_ridge(
            aq,
            bq,
            np.asarray(query_split["a_val"]),
            np.asarray(query_split["b_val"]),
        )
        dridge, dridge_sel = fit_ridge(
            ad,
            bd,
            np.asarray(doc_split["a_val"]),
            np.asarray(doc_split["b_val"]),
        )
        ridge_fit_seconds = time.perf_counter() - t0
        rankings[f"Ridge_K{k}"] = freeze_rankings(
            manifest, qridge(a_pilot_q), dridge(a_candidate_docs), candidate_pid_to_row
        )

        t0 = time.perf_counter()
        qpont, qpont_sel = fit_pontifex(
            aq,
            bq,
            np.asarray(query_split["a_val"]),
            np.asarray(query_split["b_val"]),
        )
        dpont, dpont_sel = fit_pontifex(
            ad,
            bd,
            np.asarray(doc_split["a_val"]),
            np.asarray(doc_split["b_val"]),
        )
        pont_fit_seconds = time.perf_counter() - t0
        rankings[f"Pontifex_K{k}"] = freeze_rankings(
            manifest, qpont(a_pilot_q), dpont(a_candidate_docs), candidate_pid_to_row
        )

        qperm = derangement(k, SEED + 1000 + k)
        dperm = derangement(k, SEED + 2000 + k)
        qshuf, qshuf_sel = fit_pontifex(
            aq,
            bq[qperm],
            np.asarray(query_split["a_val"]),
            np.asarray(query_split["b_val"]),
        )
        dshuf, dshuf_sel = fit_pontifex(
            ad,
            bd[dperm],
            np.asarray(doc_split["a_val"]),
            np.asarray(doc_split["b_val"]),
        )
        rankings[f"Shuffled_K{k}"] = freeze_rankings(
            manifest, qshuf(a_pilot_q), dshuf(a_candidate_docs), candidate_pid_to_row
        )

        selection[str(k)] = {
            "ridge_query": qridge_sel,
            "ridge_document": dridge_sel,
            "pontifex_query": qpont_sel,
            "pontifex_document": dpont_sel,
            "shuffled_query": qshuf_sel,
            "shuffled_document": dshuf_sel,
        }
        costs[str(k)] = {
            "ridge_fit_selection_seconds": ridge_fit_seconds,
            "pontifex_fit_selection_seconds": pont_fit_seconds,
            "paired_query_representation_bytes_float32": int(2 * k * aq.shape[1] * 4),
            "paired_document_representation_bytes_float32": int(2 * k * ad.shape[1] * 4),
        }

    # Qrels are intentionally opened only here, after every ranking is frozen.
    relevant = load_relevant()
    scores = {name: mrr_at_10(ranking, relevant, pilot_qids) for name, ranking in rankings.items()}
    a_score = scores["A_only"]
    b_score = scores["B_oracle"]
    denom = b_score - a_score
    result_rows = []
    for k in KS:
        key = f"Pontifex_K{k}"
        if key not in scores:
            continue
        frac = None if denom <= 0 else (scores[key] - a_score) / denom
        result_rows.append(
            {
                "K": k,
                "Procrustes_MRR10": scores[f"Procrustes_K{k}"],
                "Ridge_MRR10": scores[f"Ridge_K{k}"],
                "Pontifex_MRR10": scores[key],
                "Shuffled_MRR10": scores[f"Shuffled_K{k}"],
                "fraction_of_B_utility_recovered": frac,
            }
        )

    result = {
        "experiment": "Pontifex MS MARCO Passage transport pilot",
        "classification": "pilot",
        "primary_metric": "MRR@10 on frozen 256-query subset of msmarco-passage-dev-subset",
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
            "explicit_extraction_pid_sequence_sha256": manifest["explicit_extraction_pid_sequence_sha256"],
            "train_query_ids_sha256": sha_lines(train_qids),
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
            "B_true_dev_coordinates_role": "B-oracle and post-freeze evaluation only",
        },
        "pilot": {
            "queries": len(pilot_qids),
            "candidate_depth": manifest["candidate_depth"],
            "unique_candidate_pids": len(candidate_pids),
            "train_query_pool": len(train_qids),
            "document_transport_pool": len(transport_doc_pids),
        },
        "encoder_seconds": {"ANCE": a_encode_seconds, "TCT": b_encode_seconds},
        "reference_scores": {
            "BM25_candidate_order_MRR10": scores["BM25"],
            "A_only_ANCE_MRR10": a_score,
            "B_oracle_TCT_MRR10": b_score,
            "B_minus_A_MRR10": denom,
        },
        "results_by_budget": result_rows,
        "selection": selection,
        "costs": costs,
        "quality_matched": {
            "target_50pct_A_to_B": None if denom <= 0 else a_score + 0.5 * denom,
            "target_90pct_A_to_B": None if denom <= 0 else a_score + 0.9 * denom,
        },
        "interpretation_boundary": {
            "evidence": "external-task plumbing and provisional budget-matched transport signal on a frozen label-blind MS MARCO candidate pool",
            "not_evidence": "official full-dev competitiveness or a leaderboard-comparable native full-corpus retrieval result",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
