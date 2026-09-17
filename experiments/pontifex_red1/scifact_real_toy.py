# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb>=1.4.0",
#   "httpx>=0.28.0",
#   "numpy>=2.0",
#   "scikit-learn>=1.7.0",
# ]
# ///
"""Real-data Pontifex toy on SciFact without running an encoder.

Data source:
  CohereLabs/beir-embed-english-v3 on Hugging Face.

The Hugging Face dataset already contains SciFact corpus/query embeddings from
Cohere embed-english-v3.0 plus qrels. This script resolves the Hub's Parquet
shards, scans them directly with DuckDB, and compares four fusion conditions:

A  best single channel selected on train queries (dense or lexical)
B  simple mean of per-query standardized dense + lexical scores
W  learned linear fusion (logistic regression)
C  learned nonlinear fusion (small MLP)

The two channels are intentionally heterogeneous:
  - dense: precomputed Cohere dot-product score
  - lexical: TF-IDF cosine similarity computed from the published text

This is an exploratory real-data control, not a test of the full multi-encoder
Pontifex claim. It proves the no-reencode Parquet path and asks whether learned
convergence can add signal on real SciFact relevance judgments.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import duckdb
import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.neural_network import MLPClassifier

DATASET = "CohereLabs/beir-embed-english-v3"


@dataclass
class Loaded:
    corpus_ids: list[str]
    corpus_text: list[str]
    corpus_emb: np.ndarray
    query_ids: list[str]
    query_text: list[str]
    query_emb: np.ndarray
    positives: dict[str, set[str]]


def parquet_urls(config: str, split: str) -> list[str]:
    endpoint = "https://datasets-server.huggingface.co/parquet"
    response = httpx.get(endpoint, params={"dataset": DATASET, "config": config}, timeout=60)
    response.raise_for_status()
    payload = response.json()
    urls = [
        row["url"]
        for row in payload.get("parquet_files", [])
        if row.get("split") == split
    ]
    if not urls:
        available = sorted({row.get("split") for row in payload.get("parquet_files", [])})
        raise RuntimeError(f"no parquet URLs for {config}/{split}; available={available}")
    return urls


def sql_urls(urls: list[str]) -> str:
    quoted = ", ".join("'" + u.replace("'", "''") + "'" for u in urls)
    return f"[{quoted}]"


def rows_from_parquet(con: duckdb.DuckDBPyConnection, urls: list[str], columns: str):
    return con.execute(f"SELECT {columns} FROM read_parquet({sql_urls(urls)})").fetchall()


def load_scifact(max_queries: int) -> Loaded:
    con = duckdb.connect()
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")

    corpus_rows = rows_from_parquet(
        con,
        parquet_urls("scifact-corpus", "train"),
        'CAST(_id AS VARCHAR), title, text, emb',
    )

    # SciFact's BEIR evaluation uses the test split. We deterministically sample
    # eligible test queries later, then split those query IDs train/test locally.
    query_rows = rows_from_parquet(
        con,
        parquet_urls("scifact-queries", "test"),
        'CAST(_id AS VARCHAR), text, emb',
    )
    qrel_rows = rows_from_parquet(
        con,
        parquet_urls("scifact-qrels", "test"),
        'CAST(query_id AS VARCHAR), CAST(corpus_id AS VARCHAR), score',
    )

    positives: dict[str, set[str]] = {}
    for qid, cid, score in qrel_rows:
        if float(score) > 0:
            positives.setdefault(str(qid), set()).add(str(cid))

    eligible = sorted(
        [row for row in query_rows if str(row[0]) in positives],
        key=lambda row: str(row[0]),
    )
    if max_queries > 0:
        eligible = eligible[:max_queries]
    if len(eligible) < 10:
        raise RuntimeError(f"too few eligible queries: {len(eligible)}")

    corpus_ids = [str(r[0]) for r in corpus_rows]
    corpus_text = [((r[1] or "") + " " + (r[2] or "")).strip() for r in corpus_rows]
    corpus_emb = np.asarray([r[3] for r in corpus_rows], dtype=np.float32)
    query_ids = [str(r[0]) for r in eligible]
    query_text = [str(r[1] or "") for r in eligible]
    query_emb = np.asarray([r[2] for r in eligible], dtype=np.float32)

    if corpus_emb.ndim != 2 or query_emb.ndim != 2:
        raise RuntimeError((corpus_emb.shape, query_emb.shape))
    if corpus_emb.shape[1] != query_emb.shape[1]:
        raise RuntimeError((corpus_emb.shape, query_emb.shape))

    return Loaded(
        corpus_ids=corpus_ids,
        corpus_text=corpus_text,
        corpus_emb=corpus_emb,
        query_ids=query_ids,
        query_text=query_text,
        query_emb=query_emb,
        positives=positives,
    )


def zscore_rows(x: np.ndarray) -> np.ndarray:
    mean = x.mean(axis=1, keepdims=True)
    std = x.std(axis=1, keepdims=True)
    return (x - mean) / np.maximum(std, 1e-8)


def labels(data: Loaded) -> np.ndarray:
    cid_to_col = {cid: i for i, cid in enumerate(data.corpus_ids)}
    y = np.zeros((len(data.query_ids), len(data.corpus_ids)), dtype=np.uint8)
    for qi, qid in enumerate(data.query_ids):
        for cid in data.positives.get(qid, set()):
            col = cid_to_col.get(cid)
            if col is not None:
                y[qi, col] = 1
    return y


def macro_ap(y: np.ndarray, scores: np.ndarray) -> float:
    values = [average_precision_score(y[i], scores[i]) for i in range(len(y)) if y[i].sum()]
    return float(np.mean(values))


def recall_at_k(y: np.ndarray, scores: np.ndarray, k: int = 10) -> float:
    recalls = []
    for i in range(len(y)):
        n_pos = int(y[i].sum())
        if not n_pos:
            continue
        top = np.argpartition(scores[i], -min(k, scores.shape[1]))[-min(k, scores.shape[1]):]
        recalls.append(float(y[i, top].sum() / n_pos))
    return float(np.mean(recalls))


def training_pairs(
    dense: np.ndarray,
    lexical: np.ndarray,
    y: np.ndarray,
    query_indexes: np.ndarray,
    seed: int,
    negatives_per_positive: int = 40,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    features = []
    targets = []
    n_docs = y.shape[1]
    for qi in query_indexes:
        pos = np.flatnonzero(y[qi])
        if len(pos) == 0:
            continue
        for di in pos:
            features.append([dense[qi, di], lexical[qi, di]])
            targets.append(1)

        hard_dense = np.argpartition(dense[qi], -min(100, n_docs))[-min(100, n_docs):]
        hard_lex = np.argpartition(lexical[qi], -min(100, n_docs))[-min(100, n_docs):]
        pool = np.unique(np.concatenate([hard_dense, hard_lex]))
        pool = pool[y[qi, pool] == 0]
        want = negatives_per_positive * len(pos)
        if len(pool) < want:
            extra = rng.choice(n_docs, size=want - len(pool), replace=True)
            pool = np.concatenate([pool, extra[y[qi, extra] == 0]])
        if len(pool) > want:
            pool = rng.choice(pool, size=want, replace=False)
        for di in pool:
            features.append([dense[qi, di], lexical[qi, di]])
            targets.append(0)
    return np.asarray(features, dtype=np.float32), np.asarray(targets, dtype=np.uint8)


def predict_pair_model(model, dense: np.ndarray, lexical: np.ndarray, qidx: np.ndarray) -> np.ndarray:
    out = np.empty((len(qidx), dense.shape[1]), dtype=np.float32)
    for oi, qi in enumerate(qidx):
        x = np.column_stack([dense[qi], lexical[qi]]).astype(np.float32)
        out[oi] = model.predict_proba(x)[:, 1]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", type=int, default=96)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--output", type=Path, default=Path("pontifex-scifact-real-toy.json"))
    args = ap.parse_args()

    data = load_scifact(args.queries)
    y = labels(data)

    dense = data.query_emb @ data.corpus_emb.T

    tfidf = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=50_000,
        sublinear_tf=True,
        norm="l2",
    )
    doc_lex = tfidf.fit_transform(data.corpus_text)
    query_lex = tfidf.transform(data.query_text)
    lexical = (query_lex @ doc_lex.T).toarray().astype(np.float32)

    dense_z = zscore_rows(dense)
    lexical_z = zscore_rows(lexical)
    simple_mean = (dense_z + lexical_z) / 2.0

    n_queries = len(data.query_ids)
    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(n_queries)
    cut = max(1, int(round(n_queries * 0.6)))
    train_idx = np.sort(perm[:cut])
    test_idx = np.sort(perm[cut:])

    dense_train_ap = macro_ap(y[train_idx], dense[train_idx])
    lexical_train_ap = macro_ap(y[train_idx], lexical[train_idx])
    best_name = "dense" if dense_train_ap >= lexical_train_ap else "lexical"
    best_scores = dense if best_name == "dense" else lexical

    x_train, y_train = training_pairs(dense_z, lexical_z, y, train_idx, args.seed)

    linear = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=args.seed)
    linear.fit(x_train, y_train)

    mlp = MLPClassifier(
        hidden_layer_sizes=(8,),
        activation="relu",
        alpha=0.01,
        learning_rate_init=0.003,
        max_iter=800,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=30,
        random_state=args.seed,
    )
    mlp.fit(x_train, y_train)

    y_test = y[test_idx]
    test_scores = {
        "A_best_single": best_scores[test_idx],
        "B_simple_mean": simple_mean[test_idx],
        "W_linear_fusion": predict_pair_model(linear, dense_z, lexical_z, test_idx),
        "C_nonlinear_fusion": predict_pair_model(mlp, dense_z, lexical_z, test_idx),
    }

    metrics = {
        name: {
            "macro_auprc": macro_ap(y_test, scores),
            "recall_at_10": recall_at_k(y_test, scores, 10),
        }
        for name, scores in test_scores.items()
    }

    result = {
        "experiment": "Pontifex real-data SciFact no-reencode toy",
        "source": DATASET,
        "source_model": "Cohere embed-english-v3.0",
        "scientific_scope": (
            "Exploratory heterogeneous-channel convergence control; not evidence for the full multi-encoder Pontifex claim."
        ),
        "queries_total": n_queries,
        "queries_train": len(train_idx),
        "queries_test": len(test_idx),
        "documents": len(data.corpus_ids),
        "embedding_dimension": int(data.corpus_emb.shape[1]),
        "best_single_selected_on_train": best_name,
        "train_channel_auprc": {"dense": dense_train_ap, "lexical": lexical_train_ap},
        "metrics": metrics,
        "delta_simple": metrics["C_nonlinear_fusion"]["macro_auprc"]
        - max(metrics["A_best_single"]["macro_auprc"], metrics["B_simple_mean"]["macro_auprc"]),
        "delta_interaction": metrics["C_nonlinear_fusion"]["macro_auprc"]
        - metrics["W_linear_fusion"]["macro_auprc"],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
