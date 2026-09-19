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
"""BEIR/SciFact A->B latent transport benchmark for Pontifex.

Protocol:
- benchmark data are the canonical BEIR SciFact archive;
- only TRAIN query texts provide A<->B transport correspondences;
- train queries are split deterministically into student/validation pools;
- transport hyperparameters are selected by B-coordinate reconstruction on the
  held-out TRAIN validation pool, never by qrels;
- TEST qrels are opened only for final official retrieval scoring;
- B embeddings on TEST/corpus are oracle/evaluation-only and never fit a map.

The benchmark asks whether a small number K of paired MiniLM/MPNet observations
lets a cheap transport from A recover downstream B utility on untouched SciFact
test retrieval.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

import httpx
import numpy as np
from huggingface_hub import model_info
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor

BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
BEIR_MD5 = "5f7d1de60b170fc8027bb7898e2efca1"
MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_B = "sentence-transformers/all-mpnet-base-v2"
RIDGE_ALPHAS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)
TAUS = (0.02, 0.05, 0.10, 0.20, 0.40, 0.80)
LAMBDAS = (0.25, 0.50, 1.00, 1.50)
MLP_HIDDEN = 64


def sha256_lines(lines: list[str]) -> str:
    h = hashlib.sha256()
    for line in lines:
        h.update(str(line).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def l2norm(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def row_cosine(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.sum(l2norm(x) * l2norm(y), axis=1)


def softmax_rows(z: np.ndarray) -> np.ndarray:
    z = z - np.max(z, axis=1, keepdims=True)
    ez = np.exp(z)
    return ez / np.maximum(ez.sum(axis=1, keepdims=True), 1e-12)


def ensure_dataset(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / "scifact.zip"
    root = cache_dir / "scifact"
    if not archive.exists():
        with httpx.stream("GET", BEIR_URL, follow_redirects=True, timeout=120) as response:
            response.raise_for_status()
            with archive.open("wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
    digest = md5_file(archive)
    if digest != BEIR_MD5:
        raise RuntimeError(f"SciFact archive md5 mismatch: {digest} != {BEIR_MD5}")
    if not root.exists():
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(cache_dir)
    required = [
        root / "corpus.jsonl",
        root / "queries.jsonl",
        root / "qrels" / "train.tsv",
        root / "qrels" / "test.tsv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise RuntimeError(f"missing SciFact files: {missing}")
    return root


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            qid = str(row["query-id"])
            did = str(row["corpus-id"])
            score = int(row["score"])
            out.setdefault(qid, {})[did] = score
    return out


@dataclass
class Data:
    corpus_ids: list[str]
    corpus_texts: list[str]
    queries: dict[str, str]
    train_qrels: dict[str, dict[str, int]]
    test_qrels: dict[str, dict[str, int]]


def load_data(root: Path) -> Data:
    corpus_rows = load_jsonl(root / "corpus.jsonl")
    query_rows = load_jsonl(root / "queries.jsonl")
    return Data(
        corpus_ids=[str(r["_id"]) for r in corpus_rows],
        corpus_texts=[
            (" ".join([str(r.get("title", "")), str(r.get("text", ""))])).strip()
            for r in corpus_rows
        ],
        queries={str(r["_id"]): str(r["text"]).strip() for r in query_rows},
        train_qrels=load_qrels(root / "qrels" / "train.tsv"),
        test_qrels=load_qrels(root / "qrels" / "test.tsv"),
    )


def encode_texts(model_name: str, texts: list[str], batch_size: int) -> np.ndarray:
    model = SentenceTransformer(model_name)
    return model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)


def encode_or_load(data: Data, cache: Path) -> dict[str, np.ndarray]:
    train_ids = sorted(data.train_qrels)
    test_ids = sorted(data.test_qrels)
    ordered_texts = (
        data.corpus_texts
        + [data.queries[q] for q in train_ids]
        + [data.queries[q] for q in test_ids]
    )
    text_sha = sha256_lines(ordered_texts)
    if cache.exists():
        payload = np.load(cache, allow_pickle=False)
        if (
            str(payload["text_sha"].item()) == text_sha
            and str(payload["model_a"].item()) == MODEL_A
            and str(payload["model_b"].item()) == MODEL_B
        ):
            return {
                k: np.asarray(payload[k], dtype=np.float32)
                for k in (
                    "a_docs",
                    "b_docs",
                    "a_train",
                    "b_train",
                    "a_test",
                    "b_test",
                )
            }

    n_docs = len(data.corpus_ids)
    n_train = len(train_ids)
    a = encode_texts(MODEL_A, ordered_texts, 128)
    b = encode_texts(MODEL_B, ordered_texts, 64)
    out = {
        "a_docs": a[:n_docs],
        "b_docs": b[:n_docs],
        "a_train": a[n_docs : n_docs + n_train],
        "b_train": b[n_docs : n_docs + n_train],
        "a_test": a[n_docs + n_train :],
        "b_test": b[n_docs + n_train :],
    }
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        cache,
        text_sha=np.asarray(text_sha),
        model_a=np.asarray(MODEL_A),
        model_b=np.asarray(MODEL_B),
        **out,
    )
    return out


def fit_procrustes(
    a: np.ndarray, b: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    am = a.mean(axis=0, keepdims=True)
    bm = b.mean(axis=0, keepdims=True)
    u, _, vt = np.linalg.svd((a - am).T @ (b - bm), full_matrices=False)
    return (u @ vt).astype(np.float32), am.astype(np.float32), bm.astype(np.float32)


def apply_procrustes(
    x: np.ndarray, w: np.ndarray, am: np.ndarray, bm: np.ndarray
) -> np.ndarray:
    return (x - am) @ w + bm


def residual_predict(
    x: np.ndarray, a_anchor: np.ndarray, residual: np.ndarray, tau: float
) -> np.ndarray:
    sims = l2norm(x) @ l2norm(a_anchor).T
    return softmax_rows(sims / tau) @ residual


def select_torus(
    a_anchor: np.ndarray,
    b_anchor: np.ndarray,
    a_val: np.ndarray,
    b_val: np.ndarray,
) -> tuple[
    float,
    float,
    float,
    tuple[np.ndarray, np.ndarray, np.ndarray],
    np.ndarray,
]:
    w, am, bm = fit_procrustes(a_anchor, b_anchor)
    coarse_anchor = apply_procrustes(a_anchor, w, am, bm)
    residual = b_anchor - coarse_anchor
    coarse_val = apply_procrustes(a_val, w, am, bm)
    best: tuple[float, float, float] | None = None
    for tau in TAUS:
        local = residual_predict(a_val, a_anchor, residual, tau)
        for lam in LAMBDAS:
            pred = coarse_val + lam * local
            loss = float(np.mean(1.0 - row_cosine(pred, b_val)))
            cand = (tau, lam, loss)
            if best is None or cand[2] < best[2]:
                best = cand
    assert best is not None
    return best[0], best[1], best[2], (w, am, bm), residual


def apply_torus(
    x: np.ndarray,
    a_anchor: np.ndarray,
    residual: np.ndarray,
    coarse: tuple[np.ndarray, np.ndarray, np.ndarray],
    tau: float,
    lam: float,
) -> np.ndarray:
    w, am, bm = coarse
    return apply_procrustes(x, w, am, bm) + lam * residual_predict(
        x, a_anchor, residual, tau
    )


def ndcg_at_k(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    scores: np.ndarray,
    k: int = 10,
) -> float:
    vals = []
    for i, qid in enumerate(qids):
        order = np.argsort(scores[i])[::-1][:k]
        rels = np.asarray(
            [qrels[qid].get(doc_ids[j], 0) for j in order], dtype=np.float64
        )
        discounts = 1.0 / np.log2(np.arange(2, len(rels) + 2))
        dcg = float(np.sum((np.power(2.0, rels) - 1.0) * discounts))
        ideal = np.sort(
            np.asarray(list(qrels[qid].values()), dtype=np.float64)
        )[::-1][:k]
        idcg = float(
            np.sum(
                (np.power(2.0, ideal) - 1.0)
                / np.log2(np.arange(2, len(ideal) + 2))
            )
        )
        vals.append(0.0 if idcg == 0 else dcg / idcg)
    return float(np.mean(vals))


def recall_at_k(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    scores: np.ndarray,
    k: int = 100,
) -> float:
    vals = []
    for i, qid in enumerate(qids):
        positive = {d for d, r in qrels[qid].items() if r > 0}
        order = np.argsort(scores[i])[::-1][:k]
        got = sum(doc_ids[j] in positive for j in order)
        vals.append(got / max(1, len(positive)))
    return float(np.mean(vals))


def mrr_at_k(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    scores: np.ndarray,
    k: int = 10,
) -> float:
    vals = []
    for i, qid in enumerate(qids):
        positive = {d for d, r in qrels[qid].items() if r > 0}
        order = np.argsort(scores[i])[::-1][:k]
        rank = next((r + 1 for r, j in enumerate(order) if doc_ids[j] in positive), None)
        vals.append(0.0 if rank is None else 1.0 / rank)
    return float(np.mean(vals))


def map_at_k(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    scores: np.ndarray,
    k: int = 100,
) -> float:
    vals = []
    for i, qid in enumerate(qids):
        positive = {d for d, r in qrels[qid].items() if r > 0}
        order = np.argsort(scores[i])[::-1][:k]
        hits = 0
        acc = 0.0
        for rank, j in enumerate(order, start=1):
            if doc_ids[j] in positive:
                hits += 1
                acc += hits / rank
        vals.append(acc / max(1, min(len(positive), k)))
    return float(np.mean(vals))


def retrieval_metrics(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    q: np.ndarray,
    d: np.ndarray,
) -> tuple[dict[str, float], float]:
    t0 = time.perf_counter()
    scores = l2norm(q) @ l2norm(d).T
    elapsed = time.perf_counter() - t0
    return {
        "ndcg_at_10": ndcg_at_k(qrels, qids, doc_ids, scores, 10),
        "mrr_at_10": mrr_at_k(qrels, qids, doc_ids, scores, 10),
        "recall_at_100": recall_at_k(qrels, qids, doc_ids, scores, 100),
        "map_at_100": map_at_k(qrels, qids, doc_ids, scores, 100),
    }, elapsed


def fraction_recovered(score: float, a: float, b: float) -> float | None:
    denom = b - a
    return None if abs(denom) < 1e-12 else float((score - a) / denom)


def min_k_at_target(rows: list[dict], method: str, target: float) -> int | None:
    for row in rows:
        if row["test"][method]["official"]["ndcg_at_10"] >= target:
            return int(row["shared_correspondences_k"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--budgets", nargs="+", type=int, default=[16, 32, 64, 128, 256, 512]
    )
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument(
        "--cache-dir", type=Path, default=Path(".cache/pontifex-scifact")
    )
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-scifact-transport.json")
    )
    args = ap.parse_args()

    root = ensure_dataset(args.cache_dir)
    data = load_data(root)
    train_ids = sorted(data.train_qrels)
    test_ids = sorted(data.test_qrels)

    test_texts = {data.queries[q].strip() for q in test_ids}
    eligible_ids = [q for q in train_ids if data.queries[q].strip() not in test_texts]
    overlap_excluded = len(train_ids) - len(eligible_ids)

    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(len(eligible_ids))
    eligible_ids = [eligible_ids[i] for i in perm]
    cut = max(1, int(math.floor(0.80 * len(eligible_ids))))
    student_ids = eligible_ids[:cut]
    val_ids = eligible_ids[cut:]
    budgets = sorted({k for k in args.budgets if 4 <= k <= len(student_ids)})
    if not budgets:
        raise RuntimeError("no valid K budgets")

    emb = encode_or_load(data, args.cache_dir / "scifact-minilm-mpnet.npz")
    train_pos = {qid: i for i, qid in enumerate(train_ids)}
    student_idx = np.asarray([train_pos[q] for q in student_ids], dtype=np.int64)
    val_idx = np.asarray([train_pos[q] for q in val_ids], dtype=np.int64)

    a_student, b_student = emb["a_train"][student_idx], emb["b_train"][student_idx]
    a_val, b_val = emb["a_train"][val_idx], emb["b_train"][val_idx]
    a_test, b_test = emb["a_test"], emb["b_test"]
    a_docs, b_docs = emb["a_docs"], emb["b_docs"]

    a_official, a_infer = retrieval_metrics(
        data.test_qrels, test_ids, data.corpus_ids, a_test, a_docs
    )
    b_official, b_infer = retrieval_metrics(
        data.test_qrels, test_ids, data.corpus_ids, b_test, b_docs
    )
    a_ndcg = a_official["ndcg_at_10"]
    b_ndcg = b_official["ndcg_at_10"]

    rows: list[dict] = []
    for k in budgets:
        aa, bb = a_student[:k], b_student[:k]
        anchor_ids = student_ids[:k]

        t0 = time.perf_counter()
        coarse = fit_procrustes(aa, bb)
        proc_fit = time.perf_counter() - t0
        t0 = time.perf_counter()
        proc_q = apply_procrustes(a_test, *coarse)
        proc_d = apply_procrustes(a_docs, *coarse)
        proc_map_seconds = time.perf_counter() - t0
        proc_official, proc_retrieval_seconds = retrieval_metrics(
            data.test_qrels, test_ids, data.corpus_ids, proc_q, proc_d
        )

        t0 = time.perf_counter()
        tau, lam, val_loss, torus_coarse, residual = select_torus(
            aa, bb, a_val, b_val
        )
        torus_fit = time.perf_counter() - t0
        t0 = time.perf_counter()
        torus_q = apply_torus(a_test, aa, residual, torus_coarse, tau, lam)
        torus_d = apply_torus(a_docs, aa, residual, torus_coarse, tau, lam)
        torus_map_seconds = time.perf_counter() - t0
        torus_official, torus_retrieval_seconds = retrieval_metrics(
            data.test_qrels, test_ids, data.corpus_ids, torus_q, torus_d
        )

        shuf = np.random.default_rng(args.seed + k).permutation(k)
        t0 = time.perf_counter()
        stau, slam, sval_loss, scoarse, sresid = select_torus(
            aa, bb[shuf], a_val, b_val
        )
        shuffled_fit = time.perf_counter() - t0
        sq = apply_torus(a_test, aa, sresid, scoarse, stau, slam)
        sd = apply_torus(a_docs, aa, sresid, scoarse, stau, slam)
        shuffled_official, shuffled_retrieval_seconds = retrieval_metrics(
            data.test_qrels, test_ids, data.corpus_ids, sq, sd
        )

        t0 = time.perf_counter()
        ridge_candidates = []
        for alpha in RIDGE_ALPHAS:
            model = Ridge(alpha=alpha, fit_intercept=True)
            model.fit(aa, bb)
            val_loss_r = float(
                np.mean(1.0 - row_cosine(model.predict(a_val), b_val))
            )
            ridge_candidates.append((val_loss_r, alpha))
        _, ridge_alpha = min(ridge_candidates)
        ridge = Ridge(alpha=ridge_alpha, fit_intercept=True).fit(aa, bb)
        ridge_fit = time.perf_counter() - t0
        rq, rd = ridge.predict(a_test), ridge.predict(a_docs)
        ridge_official, ridge_retrieval_seconds = retrieval_metrics(
            data.test_qrels, test_ids, data.corpus_ids, rq, rd
        )

        t0 = time.perf_counter()
        mlp = MLPRegressor(
            hidden_layer_sizes=(MLP_HIDDEN,),
            activation="relu",
            alpha=1e-3,
            learning_rate_init=1e-3,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.20,
            n_iter_no_change=30,
            random_state=args.seed,
        ).fit(aa, bb)
        mlp_fit = time.perf_counter() - t0
        mq, md = mlp.predict(a_test), mlp.predict(a_docs)
        mlp_official, mlp_retrieval_seconds = retrieval_metrics(
            data.test_qrels, test_ids, data.corpus_ids, mq, md
        )

        methods = {
            "Procrustes": (proc_official, proc_q, proc_d),
            "Pontifex_residual": (torus_official, torus_q, torus_d),
            "shuffled_correspondence": (shuffled_official, sq, sd),
            "Ridge": (ridge_official, rq, rd),
            "MLP_64": (mlp_official, mq, md),
        }
        test_payload = {}
        for name, (official, pred_q, pred_d) in methods.items():
            test_payload[name] = {
                "official": official,
                "fraction_of_B_utility_recovered_ndcg10": fraction_recovered(
                    official["ndcg_at_10"], a_ndcg, b_ndcg
                ),
                "B_query_coordinate_mean_cosine": float(
                    np.mean(row_cosine(pred_q, b_test))
                ),
                "B_document_coordinate_mean_cosine": float(
                    np.mean(row_cosine(pred_d, b_docs))
                ),
            }

        procrustes_params = int(coarse[0].size + coarse[1].size + coarse[2].size)
        ridge_params = int(ridge.coef_.size + ridge.intercept_.size)
        mlp_params = int(
            sum(w.size for w in mlp.coefs_) + sum(b.size for b in mlp.intercepts_)
        )
        pair_bytes = int(k * (aa.shape[1] + bb.shape[1]) * 4)
        text_bytes = int(
            sum(len(data.queries[q].encode("utf-8")) for q in anchor_ids)
        )
        rows.append(
            {
                "shared_correspondences_k": k,
                "anchor_ids_sha256": sha256_lines(anchor_ids),
                "shared_text_bytes": text_bytes,
                "paired_embedding_supervision_bytes_float32": pair_bytes,
                "selection": {
                    "Pontifex_tau": tau,
                    "Pontifex_lambda": lam,
                    "Pontifex_train_validation_coordinate_loss": val_loss,
                    "shuffled_tau": stau,
                    "shuffled_lambda": slam,
                    "shuffled_train_validation_coordinate_loss": sval_loss,
                    "Ridge_alpha": ridge_alpha,
                },
                "test": test_payload,
                "incremental_Pontifex_over_same_Procrustes": {
                    "ndcg_at_10_delta": torus_official["ndcg_at_10"]
                    - proc_official["ndcg_at_10"],
                    "B_query_coordinate_cosine_delta": test_payload[
                        "Pontifex_residual"
                    ]["B_query_coordinate_mean_cosine"]
                    - test_payload["Procrustes"]["B_query_coordinate_mean_cosine"],
                    "B_document_coordinate_cosine_delta": test_payload[
                        "Pontifex_residual"
                    ]["B_document_coordinate_mean_cosine"]
                    - test_payload["Procrustes"]["B_document_coordinate_mean_cosine"],
                },
                "cost": {
                    "task_labels_used_for_transport_fit_or_selection": 0,
                    "Procrustes": {
                        "trainable_or_fitted_floats": procrustes_params,
                        "fit_seconds": proc_fit,
                        "map_test_queries_plus_corpus_seconds": proc_map_seconds,
                        "retrieval_seconds": proc_retrieval_seconds,
                    },
                    "Pontifex_residual_increment": {
                        "stored_residual_floats": int(residual.size),
                        "selected_scalars": 2,
                        "coarse_plus_selection_fit_seconds": torus_fit,
                        "map_test_queries_plus_corpus_seconds": torus_map_seconds,
                        "retrieval_seconds": torus_retrieval_seconds,
                    },
                    "shuffled_correspondence": {
                        "fit_seconds": shuffled_fit,
                        "retrieval_seconds": shuffled_retrieval_seconds,
                    },
                    "Ridge": {
                        "parameters": ridge_params,
                        "fit_plus_validation_selection_seconds": ridge_fit,
                        "retrieval_seconds": ridge_retrieval_seconds,
                    },
                    "MLP_64": {
                        "parameters": mlp_params,
                        "fit_seconds": mlp_fit,
                        "retrieval_seconds": mlp_retrieval_seconds,
                    },
                },
            }
        )

    methods = [
        "Procrustes",
        "Pontifex_residual",
        "Ridge",
        "MLP_64",
        "shuffled_correspondence",
    ]
    if b_ndcg > a_ndcg:
        target_mid = a_ndcg + 0.5 * (b_ndcg - a_ndcg)
        target_90 = a_ndcg + 0.9 * (b_ndcg - a_ndcg)
        quality_frontier = {
            "status": "applicable",
            "target_midpoint_A_to_B": target_mid,
            "target_90pct_A_to_B": target_90,
            "min_k_midpoint": {
                m: min_k_at_target(rows, m, target_mid) for m in methods
            },
            "min_k_90pct": {m: min_k_at_target(rows, m, target_90) for m in methods},
        }
    else:
        quality_frontier = {
            "status": "not_applicable_as_B_ceiling",
            "reason": "B-oracle nDCG@10 does not exceed A-only; B-recovery quality targets would be misleading",
        }

    result = {
        "experiment": "Pontifex BEIR/SciFact A->B transport benchmark",
        "classification": "real external benchmark result" if rows else "planned",
        "dataset": {
            "name": "BEIR/SciFact",
            "url": BEIR_URL,
            "archive_md5": BEIR_MD5,
            "documents": len(data.corpus_ids),
            "train_queries": len(train_ids),
            "test_queries": len(test_ids),
            "official_primary_metric": "nDCG@10",
            "secondary_metrics": ["MRR@10", "Recall@100", "MAP@100"],
        },
        "spaces": {
            "A": MODEL_A,
            "A_revision": model_info(MODEL_A).sha,
            "B": MODEL_B,
            "B_revision": model_info(MODEL_B).sha,
            "pretraining_overlap_between_A_B": "pretraining_overlap_possible",
            "benchmark_pretraining_overlap_A": "unknown",
            "benchmark_pretraining_overlap_B": "unknown",
        },
        "split_contract": {
            "D_student": "80% deterministic subset of exact-test-overlap-filtered BEIR SciFact TRAIN queries; only unlabeled A<->B representations",
            "D_val": "remaining 20% of filtered TRAIN queries; B coordinates only for transport hyperparameter selection; qrels unused",
            "D_test": "official BEIR SciFact TEST qrels, final scoring only",
            "B_test_and_corpus_embeddings": "oracle/ceiling and evaluation diagnostics only; never used to fit/select transport",
        },
        "leakage_audit": {
            "status": "PASS",
            "train_query_count_raw": len(train_ids),
            "train_queries_excluded_for_exact_test_text_overlap": overlap_excluded,
            "student_query_count": len(student_ids),
            "validation_query_count": len(val_ids),
            "test_query_count": len(test_ids),
            "student_ids_sha256": sha256_lines(student_ids),
            "validation_ids_sha256": sha256_lines(val_ids),
            "test_ids_sha256": sha256_lines(test_ids),
            "corpus_ids_sha256": sha256_lines(data.corpus_ids),
            "test_qrels_used_for_fit_or_selection": False,
            "train_qrels_used_for_transport_fit_or_selection": False,
            "task_labels_used_for_transport_fit_or_selection": 0,
            "seed": args.seed,
        },
        "protocol": {
            "budgets": budgets,
            "same_information_for_all_transport_methods": True,
            "Pontifex_tau_grid": TAUS,
            "Pontifex_lambda_grid": LAMBDAS,
            "Ridge_alpha_grid": RIDGE_ALPHAS,
            "MLP_hidden": MLP_HIDDEN,
            "hyperparameter_selection": "held-out TRAIN-query B-coordinate cosine only",
        },
        "oracle_context": {
            "A_only": {"official": a_official, "retrieval_seconds": a_infer},
            "B_oracle": {"official": b_official, "retrieval_seconds": b_infer},
            "B_minus_A_ndcg_at_10": b_ndcg - a_ndcg,
        },
        "results_by_budget": rows,
        "quality_matched_frontier_ndcg10": quality_frontier,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
