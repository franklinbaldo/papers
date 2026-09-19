# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "datasets>=4.0",
#   "huggingface-hub>=0.34",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "sentence-transformers>=5.0",
# ]
# ///
"""External AG News benchmark for low-budget cross-model semantic transport.

The transport sees no AG News labels. Labels used for downstream heads come from a disjoint
train pool. Canonical test labels are opened only after every map, classifier, hyperparameter,
and test prediction is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from datasets import load_dataset
from huggingface_hub import HfApi, model_info
from sentence_transformers import SentenceTransformer
from sklearn.cross_decomposition import CCA, PLSRegression
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neural_network import MLPRegressor

DATASET = "fancyzhx/ag_news"
MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_B = "BAAI/bge-small-en-v1.5"
SEED = 20260919
PARTITION_SEED = "pontifex-agnews-v1"
KS = (16, 32, 64, 128, 256, 512, 1024)
HEAD_CS = (0.01, 0.1, 1.0, 10.0, 100.0)
RIDGE_ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0)
COMPONENTS = (2, 4, 8, 16, 32)
RFF_GAMMAS = (0.25, 0.5, 1.0)
RFF_WIDTHS = (64, 128, 256)
RFF_ALPHAS = (0.1, 1.0, 10.0)
MLP_WIDTHS = (32, 64)
MLP_ALPHAS = (1e-4, 1e-3)
TAUS = (0.02, 0.05, 0.1, 0.2, 0.4)
LAMBDAS = (0.25, 0.5, 1.0, 1.5)


def sha_lines(values: list[str]) -> str:
    h = hashlib.sha256()
    for value in values:
        h.update(str(value).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def l2norm(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def coord_loss(pred: np.ndarray, target: np.ndarray) -> float:
    pred_n, target_n = l2norm(pred), l2norm(target)
    return float(1.0 - np.mean(np.sum(pred_n * target_n, axis=1)))


def mean_cosine(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean(np.sum(l2norm(pred) * l2norm(target), axis=1)))


def neighbor_overlap(pred: np.ndarray, target: np.ndarray, k: int = 10) -> float:
    pred_n, target_n = l2norm(pred), l2norm(target)
    sp, st = pred_n @ pred_n.T, target_n @ target_n.T
    np.fill_diagonal(sp, -np.inf)
    np.fill_diagonal(st, -np.inf)
    kp = min(k, len(pred_n) - 1)
    if kp <= 0:
        return 0.0
    ip = np.argpartition(-sp, kth=kp - 1, axis=1)[:, :kp]
    it = np.argpartition(-st, kth=kp - 1, axis=1)[:, :kp]
    total = 0.0
    for a, b in zip(ip, it, strict=True):
        total += len(set(a.tolist()) & set(b.tolist())) / kp
    return total / len(ip)


def softmax_rows(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x, axis=1, keepdims=True)
    e = np.exp(x)
    return e / np.maximum(np.sum(e, axis=1, keepdims=True), 1e-12)


def partition_indices(n: int) -> dict[str, list[int]]:
    order = list(range(n))
    order.sort(key=lambda i: hashlib.sha256(f"{PARTITION_SEED}\0{i}".encode()).hexdigest())
    transport = order[:4096]
    cut = int(math.floor(0.80 * len(transport)))
    return {
        "transport_student": transport[:cut],
        "transport_val": transport[cut:],
        "head_train": order[4096:16096],
        "head_val": order[16096:19096],
    }


def texts_for(split, indices: list[int]) -> list[str]:
    return [str(split[i]["text"]) for i in indices]


def labels_for(split, indices: list[int]) -> np.ndarray:
    return np.asarray([int(split[i]["label"]) for i in indices], dtype=np.int64)


def encode(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    return np.asarray(
        model.encode(
            texts,
            batch_size=128,
            show_progress_bar=True,
            normalize_embeddings=True,
        ),
        dtype=np.float32,
    )


def resolve_revisions() -> dict[str, str]:
    api = HfApi()
    dataset_sha = api.dataset_info(DATASET).sha
    a_sha = model_info(MODEL_A).sha
    b_sha = model_info(MODEL_B).sha
    if not dataset_sha or not a_sha or not b_sha:
        raise RuntimeError("unable to resolve immutable Hugging Face revisions")
    return {"dataset": dataset_sha, "A": a_sha, "B": b_sha}


def load_or_encode(cache_dir: Path, revisions: dict[str, str]) -> tuple[dict[str, np.ndarray], dict, object, object]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    npz_path = cache_dir / "agnews-embeddings.npz"
    meta_path = cache_dir / "agnews-embeddings.json"
    ds = load_dataset(DATASET, revision=revisions["dataset"])
    train, test = ds["train"], ds["test"]
    pools = partition_indices(len(train))
    pool_ids = {k: [f"train:{i}" for i in v] for k, v in pools.items()}
    manifests = {
        f"{k}_ids_sha256": sha_lines(ids) for k, ids in pool_ids.items()
    }
    manifests["test_ids_sha256"] = sha_lines([f"test:{i}" for i in range(len(test))])
    manifests["transport_student_text_sha256"] = sha_lines(texts_for(train, pools["transport_student"]))
    manifests["test_text_sha256"] = sha_lines([str(x) for x in test["text"]])
    expected_meta = {
        "dataset": DATASET,
        "model_A": MODEL_A,
        "model_B": MODEL_B,
        "revisions": revisions,
        "manifests": manifests,
    }
    if npz_path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta == expected_meta:
            z = np.load(npz_path, allow_pickle=False)
            return {k: np.asarray(z[k], dtype=np.float32) for k in z.files}, {"pools": pools, "manifests": manifests}, train, test

    groups = {
        "transport_student": texts_for(train, pools["transport_student"]),
        "transport_val": texts_for(train, pools["transport_val"]),
        "head_train": texts_for(train, pools["head_train"]),
        "head_val": texts_for(train, pools["head_val"]),
        "test": [str(x) for x in test["text"]],
    }
    arrays: dict[str, np.ndarray] = {}
    for side, model_name, revision in (("a", MODEL_A, revisions["A"]), ("b", MODEL_B, revisions["B"])):
        print(f"loading {side} {model_name}@{revision}", flush=True)
        model = SentenceTransformer(model_name, revision=revision)
        for name, texts in groups.items():
            print(f"encoding {side}/{name}: {len(texts)}", flush=True)
            arrays[f"{side}_{name}"] = encode(model, texts)
        del model
    np.savez_compressed(npz_path, **arrays)
    meta_path.write_text(json.dumps(expected_meta, indent=2) + "\n", encoding="utf-8")
    return arrays, {"pools": pools, "manifests": manifests}, train, test


def fitted_float_count(model: object) -> int:
    total = 0
    for key, value in vars(model).items():
        if key.endswith("_") and isinstance(value, np.ndarray):
            total += int(value.size)
        elif key.endswith("_") and isinstance(value, list):
            for x in value:
                if isinstance(x, np.ndarray):
                    total += int(x.size)
    return total


@dataclass
class MapResult:
    fn: Callable[[np.ndarray], np.ndarray]
    selection: dict
    fitted_floats: int
    approx_flops_per_item: int
    fit_seconds: float


def fit_procrustes(a: np.ndarray, b: np.ndarray, *, rank_constrained: bool) -> MapResult:
    t0 = time.perf_counter()
    am, bm = a.mean(0, keepdims=True), b.mean(0, keepdims=True)
    cross = (a - am).T @ (b - bm)
    u, s, vt = np.linalg.svd(cross, full_matrices=False)
    if rank_constrained:
        tol = float(s[0]) * max(cross.shape) * np.finfo(np.float32).eps if len(s) and s[0] > 0 else 0.0
        rank = max(1, min(len(s), len(a) - 1, int(np.sum(s > tol))))
        w = u[:, :rank] @ vt[:rank, :]
    else:
        rank = min(cross.shape)
        w = u @ vt
    w, am, bm = w.astype(np.float32), am.astype(np.float32), bm.astype(np.float32)
    return MapResult(
        fn=lambda x, w=w, am=am, bm=bm: ((x - am) @ w + bm).astype(np.float32),
        selection={"identified_rank": int(rank), "rank_constrained": rank_constrained},
        fitted_floats=int(w.size + am.size + bm.size),
        approx_flops_per_item=int(2 * w.shape[0] * w.shape[1]),
        fit_seconds=time.perf_counter() - t0,
    )


def fit_ridge(a: np.ndarray, b: np.ndarray, av: np.ndarray, bv: np.ndarray) -> MapResult:
    t0 = time.perf_counter()
    best = None
    best_model = None
    for alpha in RIDGE_ALPHAS:
        m = Ridge(alpha=alpha).fit(a, b)
        loss = coord_loss(m.predict(av), bv)
        cand = (loss, alpha)
        if best is None or cand < best:
            best, best_model = cand, m
    assert best is not None and best_model is not None
    return MapResult(
        fn=lambda x, m=best_model: np.asarray(m.predict(x), dtype=np.float32),
        selection={"alpha": best[1], "D_transport_val_coordinate_loss": best[0]},
        fitted_floats=fitted_float_count(best_model),
        approx_flops_per_item=int(2 * a.shape[1] * b.shape[1]),
        fit_seconds=time.perf_counter() - t0,
    )


def fit_cross_decomposition(kind: str, a: np.ndarray, b: np.ndarray, av: np.ndarray, bv: np.ndarray) -> MapResult:
    t0 = time.perf_counter()
    candidates = [c for c in COMPONENTS if c < len(a) and c <= min(a.shape[1], b.shape[1])]
    best = None
    best_model = None
    for c in candidates:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if kind == "CCA":
                    m = CCA(n_components=c, scale=True, max_iter=500, tol=1e-6).fit(a, b)
                else:
                    m = PLSRegression(n_components=c, scale=True, max_iter=500, tol=1e-6).fit(a, b)
                loss = coord_loss(m.predict(av), bv)
            cand = (loss, c)
            if best is None or cand < best:
                best, best_model = cand, m
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue
    if best is None or best_model is None:
        raise RuntimeError(f"{kind} produced no valid candidate at K={len(a)}")
    return MapResult(
        fn=lambda x, m=best_model: np.asarray(m.predict(x), dtype=np.float32),
        selection={"components": best[1], "D_transport_val_coordinate_loss": best[0]},
        fitted_floats=fitted_float_count(best_model),
        approx_flops_per_item=int(4 * best[1] * (a.shape[1] + b.shape[1])),
        fit_seconds=time.perf_counter() - t0,
    )


def fit_rff(a: np.ndarray, b: np.ndarray, av: np.ndarray, bv: np.ndarray, seed: int) -> MapResult:
    t0 = time.perf_counter()
    best = None
    for gamma in RFF_GAMMAS:
        for width in RFF_WIDTHS:
            rs = seed + width * 31 + int(gamma * 1000)
            rff = RBFSampler(gamma=gamma, n_components=width, random_state=rs)
            za, zv = rff.fit_transform(a), rff.transform(av)
            for alpha in RFF_ALPHAS:
                ridge = Ridge(alpha=alpha).fit(za, b)
                loss = coord_loss(ridge.predict(zv), bv)
                cand = (loss, gamma, width, alpha, rff, ridge)
                if best is None or cand[:4] < best[:4]:
                    best = cand
    assert best is not None
    _, gamma, width, alpha, rff, ridge = best
    return MapResult(
        fn=lambda x, rff=rff, ridge=ridge: np.asarray(ridge.predict(rff.transform(x)), dtype=np.float32),
        selection={"gamma": gamma, "width": width, "alpha": alpha, "D_transport_val_coordinate_loss": best[0]},
        fitted_floats=fitted_float_count(rff) + fitted_float_count(ridge),
        approx_flops_per_item=int(2 * a.shape[1] * width + 2 * width * b.shape[1]),
        fit_seconds=time.perf_counter() - t0,
    )


def fit_mlp(a: np.ndarray, b: np.ndarray, av: np.ndarray, bv: np.ndarray, seed: int) -> MapResult:
    t0 = time.perf_counter()
    best = None
    for width in MLP_WIDTHS:
        for alpha in MLP_ALPHAS:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = MLPRegressor(
                    hidden_layer_sizes=(width,),
                    activation="relu",
                    solver="adam",
                    alpha=alpha,
                    batch_size=min(128, len(a)),
                    learning_rate_init=1e-3,
                    max_iter=200,
                    random_state=seed + width,
                ).fit(a, b)
            loss = coord_loss(m.predict(av), bv)
            cand = (loss, width, alpha, m)
            if best is None or cand[:3] < best[:3]:
                best = cand
    assert best is not None
    m = best[3]
    return MapResult(
        fn=lambda x, m=m: np.asarray(m.predict(x), dtype=np.float32),
        selection={"width": best[1], "alpha": best[2], "D_transport_val_coordinate_loss": best[0]},
        fitted_floats=fitted_float_count(m),
        approx_flops_per_item=int(2 * a.shape[1] * best[1] + 2 * best[1] * b.shape[1]),
        fit_seconds=time.perf_counter() - t0,
    )


def fit_pontifex(
    a: np.ndarray,
    b: np.ndarray,
    av: np.ndarray,
    bv: np.ndarray,
    *,
    rank_constrained: bool,
) -> MapResult:
    t0 = time.perf_counter()
    coarse = fit_procrustes(a, b, rank_constrained=rank_constrained)
    coarse_anchor = coarse.fn(a)
    residual = (b - coarse_anchor).astype(np.float32)
    coarse_val = coarse.fn(av)
    a_anchor = np.asarray(a, dtype=np.float32).copy()
    best = None
    sims = l2norm(av) @ l2norm(a_anchor).T
    for tau in TAUS:
        local = softmax_rows(sims / tau) @ residual
        for lam in LAMBDAS:
            loss = coord_loss(coarse_val + lam * local, bv)
            cand = (loss, tau, lam)
            if best is None or cand < best:
                best = cand
    assert best is not None
    loss, tau, lam = best

    def mapper(x: np.ndarray) -> np.ndarray:
        local = softmax_rows((l2norm(x) @ l2norm(a_anchor).T) / tau) @ residual
        return (coarse.fn(x) + lam * local).astype(np.float32)

    fitted = coarse.fitted_floats + int(a_anchor.size + residual.size)
    flops = coarse.approx_flops_per_item + int(2 * a.shape[1] * len(a) + 2 * len(a) * b.shape[1])
    return MapResult(
        fn=mapper,
        selection={**coarse.selection, "tau": tau, "lambda": lam, "D_transport_val_coordinate_loss": loss},
        fitted_floats=fitted,
        approx_flops_per_item=flops,
        fit_seconds=time.perf_counter() - t0,
    )


def derangement(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.arange(n)
    for _ in range(10000):
        p = rng.permutation(n)
        if np.all(p != base):
            return p
    raise RuntimeError("failed to construct derangement")


def fit_head(x_train: np.ndarray, y_train: np.ndarray, x_val: np.ndarray, y_val: np.ndarray) -> tuple[LogisticRegression, dict]:
    best = None
    best_model = None
    t0 = time.perf_counter()
    for c in HEAD_CS:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = LogisticRegression(C=c, max_iter=1000, solver="lbfgs", random_state=SEED).fit(x_train, y_train)
        acc = float(accuracy_score(y_val, m.predict(x_val)))
        cand = (-acc, c)
        if best is None or cand < best:
            best, best_model = cand, m
    assert best is not None and best_model is not None
    return best_model, {"C": best[1], "head_val_accuracy": -best[0], "fit_selection_seconds": time.perf_counter() - t0}


def min_k(rows: list[dict], method: str, target: float) -> int | None:
    for row in rows:
        value = row["test"][method]["accuracy"]
        if value >= target:
            return int(row["K"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-agnews"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-agnews-classification.json"))
    ap.add_argument("--budgets", nargs="+", type=int, default=list(KS))
    args = ap.parse_args()
    budgets = [k for k in KS if k in set(args.budgets)]

    revisions = resolve_revisions()
    emb, meta, train, test = load_or_encode(args.cache_dir, revisions)
    pools = meta["pools"]
    student_ids = [f"train:{i}" for i in pools["transport_student"]]
    val_ids = [f"train:{i}" for i in pools["transport_val"]]
    head_train_ids = [f"train:{i}" for i in pools["head_train"]]
    head_val_ids = [f"train:{i}" for i in pools["head_val"]]
    if len(set(student_ids) | set(val_ids) | set(head_train_ids) | set(head_val_ids)) != sum(map(len, (student_ids, val_ids, head_train_ids, head_val_ids))):
        raise AssertionError("train information pools overlap")

    # Only the disjoint head pools expose task labels before the prediction bank freezes.
    y_head_train = labels_for(train, pools["head_train"])
    y_head_val = labels_for(train, pools["head_val"])
    a_head, a_head_sel = fit_head(emb["a_head_train"], y_head_train, emb["a_head_val"], y_head_val)
    b_head, b_head_sel = fit_head(emb["b_head_train"], y_head_train, emb["b_head_val"], y_head_val)

    # Freeze reference predictions before test labels are opened.
    prediction_bank: dict[str, np.ndarray] = {
        "A_only": np.asarray(a_head.predict(emb["a_test"]), dtype=np.int64),
        "B_oracle": np.asarray(b_head.predict(emb["b_test"]), dtype=np.int64),
    }
    frozen_rows: list[dict] = []
    a_student, b_student = emb["a_transport_student"], emb["b_transport_student"]
    av, bv = emb["a_transport_val"], emb["b_transport_val"]
    transport_texts = texts_for(train, pools["transport_student"])

    for k in budgets:
        if k > len(a_student):
            continue
        a, b = a_student[:k], b_student[:k]
        methods: dict[str, MapResult] = {
            "Procrustes": fit_procrustes(a, b, rank_constrained=False),
            "RankProcrustes": fit_procrustes(a, b, rank_constrained=True),
            "Ridge": fit_ridge(a, b, av, bv),
            "CCA": fit_cross_decomposition("CCA", a, b, av, bv),
            "PLS": fit_cross_decomposition("PLS", a, b, av, bv),
            "RFF_Ridge": fit_rff(a, b, av, bv, SEED + k * 11),
            "MLP": fit_mlp(a, b, av, bv, SEED + k * 13),
            "Pontifex": fit_pontifex(a, b, av, bv, rank_constrained=False),
            "RankPontifex": fit_pontifex(a, b, av, bv, rank_constrained=True),
        }
        p = derangement(k, SEED + k * 17)
        methods["ShuffledPontifex"] = fit_pontifex(a, b[p], av, bv, rank_constrained=False)

        row = {
            "K": k,
            "anchor_ids_sha256": sha_lines(student_ids[:k]),
            "shared_text_bytes": int(sum(len(t.encode("utf-8")) for t in transport_texts[:k])),
            "paired_embedding_supervision_bytes_float32": int(k * (a.shape[1] + b.shape[1]) * 4),
            "methods": {},
        }
        for name, result in methods.items():
            val_pred = result.fn(av)
            t0 = time.perf_counter()
            test_mapped = result.fn(emb["a_test"])
            test_pred = np.asarray(b_head.predict(test_mapped), dtype=np.int64)
            map_predict_seconds = time.perf_counter() - t0
            prediction_bank[f"{name}_K{k}"] = test_pred
            row["methods"][name] = {
                "selection": result.selection,
                "geometry": {
                    "D_transport_val_mean_cosine_to_B": mean_cosine(val_pred, bv),
                    "D_transport_val_neighbor_overlap_at_10": neighbor_overlap(val_pred, bv, 10),
                },
                "cost": {
                    "fitted_floats": result.fitted_floats,
                    "fit_plus_validation_selection_seconds": result.fit_seconds,
                    "test_map_plus_head_predict_seconds": map_predict_seconds,
                    "approx_mapping_flops_per_item": result.approx_flops_per_item,
                },
            }
        frozen_rows.append(row)

    # Evaluation boundary: all maps, heads, hyperparameters and test predictions are frozen above.
    y_test = np.asarray(test["label"], dtype=np.int64)
    scores: dict[str, dict[str, float]] = {}
    for name, pred in prediction_bank.items():
        scores[name] = {
            "accuracy": float(accuracy_score(y_test, pred)),
            "macro_f1": float(f1_score(y_test, pred, average="macro")),
        }
    a_acc, b_acc = scores["A_only"]["accuracy"], scores["B_oracle"]["accuracy"]
    gap = b_acc - a_acc

    rows: list[dict] = []
    for frozen in frozen_rows:
        k = frozen["K"]
        test_payload: dict[str, dict] = {}
        efficiency: dict[str, dict] = {}
        for name, method_data in frozen["methods"].items():
            score = scores[f"{name}_K{k}"]
            frac = None if gap <= 0 else (score["accuracy"] - a_acc) / gap
            test_payload[name] = {**score, "fraction_of_B_utility_recovered": frac}
            delta = score["accuracy"] - a_acc
            cost = method_data["cost"]
            efficiency[name] = {
                "accuracy_delta_over_A_per_shared_probe": delta / k,
                "accuracy_delta_over_A_per_fitted_float": None if cost["fitted_floats"] == 0 else delta / cost["fitted_floats"],
                "accuracy_delta_over_A_per_supervision_byte": delta / frozen["paired_embedding_supervision_bytes_float32"],
                "accuracy_delta_over_A_per_fit_second": None if cost["fit_plus_validation_selection_seconds"] <= 0 else delta / cost["fit_plus_validation_selection_seconds"],
            }
        rows.append({**frozen, "test": test_payload, "efficiency": efficiency})

    methods = list(rows[0]["test"]) if rows else []
    if gap > 0:
        target50, target90 = a_acc + 0.5 * gap, a_acc + 0.9 * gap
        frontier = {
            "target_50pct_A_to_B": target50,
            "target_90pct_A_to_B": target90,
            "min_k_50pct": {m: min_k(rows, m, target50) for m in methods},
            "min_k_90pct": {m: min_k(rows, m, target90) for m in methods},
        }
    else:
        frontier = {"status": "not_applicable_B_does_not_beat_A", "B_minus_A_accuracy": gap}

    result = {
        "experiment": "Pontifex AG News single-item cross-model transport",
        "classification": "real external fixed-label-budget benchmark",
        "dataset": {
            "name": DATASET,
            "revision": revisions["dataset"],
            "canonical_train_rows": len(train),
            "canonical_test_rows": len(test),
            "primary_metric": "accuracy",
            "secondary_metric": "macro-F1",
        },
        "spaces": {
            "A": MODEL_A,
            "A_revision": revisions["A"],
            "B": MODEL_B,
            "B_revision": revisions["B"],
            "pretraining_overlap_A_B": "pretraining_overlap_possible",
            "benchmark_pretraining_overlap_A": "unknown",
            "benchmark_pretraining_overlap_B": "unknown",
        },
        "manifests": {
            **meta["manifests"],
            "K_prefix_sha256": {str(k): sha_lines(student_ids[:k]) for k in budgets},
            "partition_seed": PARTITION_SEED,
            "random_seed": SEED,
        },
        "information_budgets": {
            "transport_student_rows": len(student_ids),
            "transport_validation_rows": len(val_ids),
            "labeled_head_train_rows": len(head_train_ids),
            "labeled_head_validation_rows": len(head_val_ids),
            "test_rows": len(test),
            "task_labels_used_for_transport_fit_or_selection": 0,
        },
        "head_selection": {"A_only": a_head_sel, "B_oracle": b_head_sel},
        "reference_scores": {
            "A_only": scores["A_only"],
            "B_oracle": scores["B_oracle"],
            "B_minus_A_accuracy": gap,
        },
        "results_by_budget": rows,
        "quality_matched_frontier": frontier,
        "leakage_audit": {
            "status": "PASS",
            "transport_labels_read": False,
            "test_labels_opened_before_prediction_freeze": False,
            "test_information_used_for_fit_or_selection": False,
            "B_test_coordinates_used_for_transport_selection": False,
            "head_labels_disjoint_from_transport_pairs": True,
            "shuffled_control_information_matched": True,
            "pretraining_overlap_treated_as_evaluation_leakage": False,
        },
        "interpretation_boundary": {
            "primary": "official canonical-test classification utility under fixed labeled-head budget",
            "geometry_role": "secondary diagnostic only",
            "rank_control_status": "prospectively added before any AG News scoring because K<d leaves full Procrustes nullspace underidentified",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
