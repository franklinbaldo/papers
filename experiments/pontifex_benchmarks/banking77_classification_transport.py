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
"""External Banking77 benchmark for low-budget cross-model semantic transport.

The transport sees no Banking77 labels. Downstream labels come from a disjoint train pool.
Canonical test labels are materialized only after all maps, hyperparameters, heads, and test
predictions have been frozen.
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

DATASET = "PolyAI/banking77"
MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_B = "BAAI/bge-small-en-v1.5"
SEED = 20260919
PARTITION_SEED = "pontifex-banking77-v1"
KS = (16, 32, 64, 128, 256, 512, 1024)
HEAD_CS = (0.01, 0.1, 1.0, 10.0)
RIDGE_ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0)
COMPONENTS = (2, 4, 8, 16, 32)
RFF_GAMMAS = (0.25, 0.5, 1.0)
RFF_WIDTHS = (64, 128, 256)
RFF_ALPHAS = (0.01, 0.1, 1.0, 10.0)
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


def ordered_ids(n: int) -> list[str]:
    ids = [str(i) for i in range(n)]
    ids.sort(key=lambda x: hashlib.sha256(f"{PARTITION_SEED}\0{x}".encode()).hexdigest())
    return ids


def l2norm(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def row_cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.sum(l2norm(a) * l2norm(b), axis=1)


def coordinate_loss(pred: np.ndarray, true: np.ndarray) -> float:
    values = 1.0 - row_cosine(np.asarray(pred, dtype=np.float32), true)
    if not np.all(np.isfinite(values)):
        return math.inf
    return float(np.mean(values))


def neighbor_overlap_at_10(pred: np.ndarray, true: np.ndarray) -> float:
    pred_n, true_n = l2norm(pred), l2norm(true)
    pred_s = pred_n @ pred_n.T
    true_s = true_n @ true_n.T
    np.fill_diagonal(pred_s, -np.inf)
    np.fill_diagonal(true_s, -np.inf)
    k = min(10, len(pred) - 1)
    p = np.argpartition(-pred_s, kth=k - 1, axis=1)[:, :k]
    t = np.argpartition(-true_s, kth=k - 1, axis=1)[:, :k]
    return float(np.mean([len(set(a) & set(b)) / k for a, b in zip(p, t)]))


def count_arrays(obj: object) -> int:
    total = 0
    for value in vars(obj).values():
        if isinstance(value, np.ndarray):
            total += int(value.size)
        elif isinstance(value, list) and value and all(isinstance(x, np.ndarray) for x in value):
            total += sum(int(x.size) for x in value)
    return total


@dataclass
class LinearMap:
    w: np.ndarray
    am: np.ndarray
    bm: np.ndarray
    rank: int
    rank_constrained: bool

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return ((x - self.am) @ self.w + self.bm).astype(np.float32)

    @property
    def fitted_floats(self) -> int:
        return int(self.w.size + self.am.size + self.bm.size)


def fit_procrustes(a: np.ndarray, b: np.ndarray, *, rank_constrained: bool) -> LinearMap:
    am = a.mean(axis=0, keepdims=True)
    bm = b.mean(axis=0, keepdims=True)
    cross = (a - am).T @ (b - bm)
    u, s, vt = np.linalg.svd(cross, full_matrices=False)
    tol = max(cross.shape) * np.finfo(s.dtype).eps * (float(s.max()) if len(s) else 0.0)
    identified_rank = max(1, int(np.sum(s > tol)))
    if rank_constrained:
        w = u[:, :identified_rank] @ vt[:identified_rank, :]
    else:
        w = u @ vt
    return LinearMap(
        w.astype(np.float32), am.astype(np.float32), bm.astype(np.float32), identified_rank, rank_constrained
    )


def softmax_rows(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / np.maximum(e.sum(axis=1, keepdims=True), 1e-12)


def residual_predict(x: np.ndarray, anchors: np.ndarray, residual: np.ndarray, tau: float) -> np.ndarray:
    sims = l2norm(x) @ l2norm(anchors).T
    return (softmax_rows(sims / tau) @ residual).astype(np.float32)


@dataclass
class PontifexMap:
    coarse: LinearMap
    anchors: np.ndarray
    residual: np.ndarray
    tau: float
    lam: float

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.coarse(x) + self.lam * residual_predict(x, self.anchors, self.residual, self.tau)

    @property
    def fitted_floats(self) -> int:
        return int(self.coarse.fitted_floats + self.anchors.size + self.residual.size + 2)


def fit_pontifex(
    a: np.ndarray,
    b: np.ndarray,
    a_val: np.ndarray,
    b_val: np.ndarray,
    *,
    rank_constrained: bool,
) -> tuple[PontifexMap, dict]:
    coarse = fit_procrustes(a, b, rank_constrained=rank_constrained)
    residual = (b - coarse(a)).astype(np.float32)
    coarse_val = coarse(a_val)
    best: tuple[float, float, float] | None = None
    for tau in TAUS:
        local = residual_predict(a_val, a, residual, tau)
        for lam in LAMBDAS:
            loss = coordinate_loss(coarse_val + lam * local, b_val)
            candidate = (loss, tau, lam)
            if best is None or candidate < best:
                best = candidate
    assert best is not None
    loss, tau, lam = best
    return PontifexMap(coarse, a.copy(), residual, tau, lam), {
        "identified_rank": coarse.rank,
        "rank_constrained": rank_constrained,
        "tau": tau,
        "lambda": lam,
        "D_transport_val_coordinate_loss": loss,
    }


def fit_ridge(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray) -> tuple[Ridge, dict, float]:
    t0 = time.perf_counter()
    best = None
    for alpha in RIDGE_ALPHAS:
        model = Ridge(alpha=alpha).fit(a, b)
        loss = coordinate_loss(model.predict(a_val).astype(np.float32), b_val)
        candidate = (loss, alpha, model)
        if best is None or candidate[0] < best[0]:
            best = candidate
    assert best is not None
    return best[2], {"alpha": best[1], "D_transport_val_coordinate_loss": best[0]}, time.perf_counter() - t0


def component_grid(k: int) -> list[int]:
    return [c for c in COMPONENTS if c < k]


def fit_cca(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray) -> tuple[CCA, dict, float]:
    t0 = time.perf_counter()
    best = None
    for c in component_grid(len(a)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = CCA(n_components=c, scale=True, max_iter=500, tol=1e-6).fit(a, b)
                loss = coordinate_loss(model.predict(a_val).astype(np.float32), b_val)
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue
        if best is None or loss < best[0]:
            best = (loss, c, model)
    if best is None:
        raise RuntimeError("CCA produced no valid candidate")
    return best[2], {"components": best[1], "D_transport_val_coordinate_loss": best[0]}, time.perf_counter() - t0


def fit_pls(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray) -> tuple[PLSRegression, dict, float]:
    t0 = time.perf_counter()
    best = None
    for c in component_grid(len(a)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = PLSRegression(n_components=c, scale=True, max_iter=500, tol=1e-6).fit(a, b)
                loss = coordinate_loss(model.predict(a_val).astype(np.float32), b_val)
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue
        if best is None or loss < best[0]:
            best = (loss, c, model)
    if best is None:
        raise RuntimeError("PLS produced no valid candidate")
    return best[2], {"components": best[1], "D_transport_val_coordinate_loss": best[0]}, time.perf_counter() - t0


def fit_rff(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray, seed: int):
    t0 = time.perf_counter()
    best = None
    for gamma in RFF_GAMMAS:
        for width in RFF_WIDTHS:
            rff = RBFSampler(gamma=gamma, n_components=width, random_state=seed + width + int(gamma * 1000))
            za = rff.fit_transform(a)
            zv = rff.transform(a_val)
            for alpha in RFF_ALPHAS:
                ridge = Ridge(alpha=alpha).fit(za, b)
                loss = coordinate_loss(ridge.predict(zv).astype(np.float32), b_val)
                if best is None or loss < best[0]:
                    best = (loss, gamma, width, alpha, rff, ridge)
    assert best is not None
    selection = {
        "gamma": best[1], "width": best[2], "alpha": best[3],
        "D_transport_val_coordinate_loss": best[0],
    }
    return best[4], best[5], selection, time.perf_counter() - t0


def fit_mlp(a: np.ndarray, b: np.ndarray, a_val: np.ndarray, b_val: np.ndarray, seed: int):
    t0 = time.perf_counter()
    best = None
    for width in MLP_WIDTHS:
        for alpha in MLP_ALPHAS:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = MLPRegressor(
                    hidden_layer_sizes=(width,), activation="relu", alpha=alpha,
                    max_iter=300, random_state=seed + width, early_stopping=False,
                ).fit(a, b)
            loss = coordinate_loss(model.predict(a_val).astype(np.float32), b_val)
            if best is None or loss < best[0]:
                best = (loss, width, alpha, model)
    assert best is not None
    return best[3], {"width": best[1], "alpha": best[2], "D_transport_val_coordinate_loss": best[0]}, time.perf_counter() - t0


def derangement(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.arange(n)
    for _ in range(10000):
        p = rng.permutation(n)
        if np.all(p != base):
            return p
    raise RuntimeError("could not build derangement")


def fit_head(x_train: np.ndarray, y_train: np.ndarray, x_val: np.ndarray, y_val: np.ndarray):
    t0 = time.perf_counter()
    best = None
    for c in HEAD_CS:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = LogisticRegression(C=c, max_iter=1200, solver="lbfgs").fit(x_train, y_train)
        score = float(accuracy_score(y_val, model.predict(x_val)))
        candidate = (-score, c, model)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    assert best is not None
    return best[2], {"C": best[1], "head_val_accuracy": -best[0], "fit_selection_seconds": time.perf_counter() - t0}


def encode_or_load(
    cache: Path,
    revision: str,
    model_name: str,
    groups: dict[str, list[str]],
    prefix: str,
) -> dict[str, np.ndarray]:
    path = cache / f"{prefix}-{revision}.npz"
    if path.exists():
        payload = np.load(path, allow_pickle=False)
        if set(payload.files) == set(groups):
            return {k: np.asarray(payload[k], dtype=np.float32) for k in groups}
    model = SentenceTransformer(model_name, revision=revision)
    out: dict[str, np.ndarray] = {}
    for name, texts in groups.items():
        print(f"encoding {prefix}/{name}: {len(texts)}", flush=True)
        out[name] = np.asarray(
            model.encode(texts, batch_size=128, show_progress_bar=True, convert_to_numpy=True),
            dtype=np.float32,
        )
    cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **out)
    return out


def map_geometry(mapper: Callable[[np.ndarray], np.ndarray], a_val: np.ndarray, b_val: np.ndarray) -> dict:
    pred = np.asarray(mapper(a_val), dtype=np.float32)
    return {
        "D_transport_val_mean_cosine_to_B": float(np.mean(row_cosine(pred, b_val))),
        "D_transport_val_neighbor_overlap_at_10": neighbor_overlap_at_10(pred, b_val),
    }


def metric_payload(y: np.ndarray, pred: np.ndarray, a_acc: float, b_acc: float) -> dict:
    acc = float(accuracy_score(y, pred))
    f1 = float(f1_score(y, pred, average="macro"))
    denom = b_acc - a_acc
    frac = None if denom <= 0 else (acc - a_acc) / denom
    return {"accuracy": acc, "macro_f1": f1, "fraction_of_B_utility_recovered": frac}


def min_k(rows: list[dict], method: str, target: float) -> int | None:
    for row in rows:
        if row["test"][method]["accuracy"] >= target:
            return int(row["K"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-banking77"))
    ap.add_argument("--output", type=Path, default=Path("pontifex-banking77-classification.json"))
    args = ap.parse_args()

    dataset_revision = HfApi().dataset_info(DATASET).sha
    a_revision = model_info(MODEL_A).sha
    b_revision = model_info(MODEL_B).sha
    ds = load_dataset(DATASET, revision=dataset_revision)
    train, test = ds["train"], ds["test"]
    if len(train) < 9548:
        raise RuntimeError(f"Banking77 train unexpectedly small: {len(train)}")

    ids = ordered_ids(len(train))
    transport_ids = ids[:2048]
    cut = int(math.floor(0.8 * len(transport_ids)))
    student_ids, transport_val_ids = transport_ids[:cut], transport_ids[cut:]
    head_train_ids = ids[2048:8548]
    head_val_ids = ids[8548:9548]
    if len(set(transport_ids) | set(head_train_ids) | set(head_val_ids)) != 9548:
        raise AssertionError("train pools overlap")

    def train_text(row_id: str) -> str:
        return str(train[int(row_id)]["text"]).strip()

    groups = {
        "transport_student": [train_text(i) for i in student_ids],
        "transport_val": [train_text(i) for i in transport_val_ids],
        "head_train": [train_text(i) for i in head_train_ids],
        "head_val": [train_text(i) for i in head_val_ids],
        "test": [str(x).strip() for x in test["text"]],
    }
    a = encode_or_load(args.cache_dir, a_revision, MODEL_A, groups, "a")
    b = encode_or_load(args.cache_dir, b_revision, MODEL_B, groups, "b")

    y_head_train = np.asarray([int(train[int(i)]["label"]) for i in head_train_ids], dtype=np.int64)
    y_head_val = np.asarray([int(train[int(i)]["label"]) for i in head_val_ids], dtype=np.int64)
    a_head, a_head_sel = fit_head(a["head_train"], y_head_train, a["head_val"], y_head_val)
    b_head, b_head_sel = fit_head(b["head_train"], y_head_train, b["head_val"], y_head_val)

    # Freeze reference and transport predictions before canonical test labels are materialized.
    prediction_bank: dict[str, np.ndarray] = {
        "A_only": a_head.predict(a["test"]),
        "B_oracle": b_head.predict(b["test"]),
    }
    frozen_rows: list[dict] = []

    for k in KS:
        aa = a["transport_student"][:k]
        bb = b["transport_student"][:k]
        av, bv = a["transport_val"], b["transport_val"]
        methods: dict[str, dict] = {}
        mappers: dict[str, tuple[Callable[[np.ndarray], np.ndarray], int, float, int]] = {}

        for name, rank_flag in (("Procrustes", False), ("RankProcrustes", True)):
            t0 = time.perf_counter()
            proc = fit_procrustes(aa, bb, rank_constrained=rank_flag)
            fit_s = time.perf_counter() - t0
            methods[name] = {
                "selection": {"identified_rank": proc.rank, "rank_constrained": rank_flag},
                "geometry": map_geometry(proc, av, bv),
                "cost": {
                    "fitted_floats": proc.fitted_floats,
                    "fit_plus_validation_selection_seconds": fit_s,
                    "approx_mapping_flops_per_item": int(2 * aa.shape[1] * bb.shape[1]),
                },
            }
            mappers[name] = (proc, proc.fitted_floats, fit_s, int(2 * aa.shape[1] * bb.shape[1]))

        ridge, sel, fit_s = fit_ridge(aa, bb, av, bv)
        ridge_map = lambda x, m=ridge: m.predict(x).astype(np.float32)
        methods["Ridge"] = {"selection": sel, "geometry": map_geometry(ridge_map, av, bv), "cost": {
            "fitted_floats": count_arrays(ridge), "fit_plus_validation_selection_seconds": fit_s,
            "approx_mapping_flops_per_item": int(2 * aa.shape[1] * bb.shape[1]),
        }}
        mappers["Ridge"] = (ridge_map, count_arrays(ridge), fit_s, int(2 * aa.shape[1] * bb.shape[1]))

        cca, sel, fit_s = fit_cca(aa, bb, av, bv)
        cca_map = lambda x, m=cca: m.predict(x).astype(np.float32)
        c = int(sel["components"])
        methods["CCA"] = {"selection": sel, "geometry": map_geometry(cca_map, av, bv), "cost": {
            "fitted_floats": count_arrays(cca), "fit_plus_validation_selection_seconds": fit_s,
            "approx_mapping_flops_per_item": int(4 * aa.shape[1] * c),
        }}
        mappers["CCA"] = (cca_map, count_arrays(cca), fit_s, int(4 * aa.shape[1] * c))

        pls, sel, fit_s = fit_pls(aa, bb, av, bv)
        pls_map = lambda x, m=pls: m.predict(x).astype(np.float32)
        c = int(sel["components"])
        methods["PLS"] = {"selection": sel, "geometry": map_geometry(pls_map, av, bv), "cost": {
            "fitted_floats": count_arrays(pls), "fit_plus_validation_selection_seconds": fit_s,
            "approx_mapping_flops_per_item": int(4 * aa.shape[1] * c),
        }}
        mappers["PLS"] = (pls_map, count_arrays(pls), fit_s, int(4 * aa.shape[1] * c))

        rff, rr, sel, fit_s = fit_rff(aa, bb, av, bv, SEED + k)
        rff_map = lambda x, f=rff, m=rr: m.predict(f.transform(x)).astype(np.float32)
        rff_floats = count_arrays(rff) + count_arrays(rr)
        width = int(sel["width"])
        methods["RFF_Ridge"] = {"selection": sel, "geometry": map_geometry(rff_map, av, bv), "cost": {
            "fitted_floats": rff_floats, "fit_plus_validation_selection_seconds": fit_s,
            "approx_mapping_flops_per_item": int(4 * aa.shape[1] * width),
        }}
        mappers["RFF_Ridge"] = (rff_map, rff_floats, fit_s, int(4 * aa.shape[1] * width))

        mlp, sel, fit_s = fit_mlp(aa, bb, av, bv, SEED + k * 3)
        mlp_map = lambda x, m=mlp: m.predict(x).astype(np.float32)
        mlp_floats = count_arrays(mlp)
        width = int(sel["width"])
        methods["MLP"] = {"selection": sel, "geometry": map_geometry(mlp_map, av, bv), "cost": {
            "fitted_floats": mlp_floats, "fit_plus_validation_selection_seconds": fit_s,
            "approx_mapping_flops_per_item": int(4 * aa.shape[1] * width),
        }}
        mappers["MLP"] = (mlp_map, mlp_floats, fit_s, int(4 * aa.shape[1] * width))

        for name, rank_flag in (("Pontifex", False), ("RankPontifex", True)):
            t0 = time.perf_counter()
            pont, sel = fit_pontifex(aa, bb, av, bv, rank_constrained=rank_flag)
            fit_s = time.perf_counter() - t0
            flops = int(2 * aa.shape[1] * bb.shape[1] + 2 * k * aa.shape[1])
            methods[name] = {"selection": sel, "geometry": map_geometry(pont, av, bv), "cost": {
                "fitted_floats": pont.fitted_floats, "fit_plus_validation_selection_seconds": fit_s,
                "approx_mapping_flops_per_item": flops,
            }}
            mappers[name] = (pont, pont.fitted_floats, fit_s, flops)

        perm = derangement(k, SEED + 9000 + k)
        t0 = time.perf_counter()
        shuf, sel = fit_pontifex(aa, bb[perm], av, bv, rank_constrained=False)
        fit_s = time.perf_counter() - t0
        flops = int(2 * aa.shape[1] * bb.shape[1] + 2 * k * aa.shape[1])
        methods["ShuffledPontifex"] = {"selection": sel, "geometry": map_geometry(shuf, av, bv), "cost": {
            "fitted_floats": shuf.fitted_floats, "fit_plus_validation_selection_seconds": fit_s,
            "approx_mapping_flops_per_item": flops,
        }}
        mappers["ShuffledPontifex"] = (shuf, shuf.fitted_floats, fit_s, flops)

        for name, (mapper, _, _, _) in mappers.items():
            t0 = time.perf_counter()
            pred = b_head.predict(mapper(a["test"]))
            elapsed = time.perf_counter() - t0
            prediction_bank[f"{name}_K{k}"] = pred
            methods[name]["cost"]["test_map_plus_head_predict_seconds"] = elapsed

        frozen_rows.append({
            "K": k,
            "anchor_ids_sha256": sha_lines(student_ids[:k]),
            "shared_text_bytes": int(sum(len(train_text(i).encode("utf-8")) for i in student_ids[:k])),
            "paired_embedding_supervision_bytes_float32": int(k * (aa.shape[1] + bb.shape[1]) * 4),
            "methods": methods,
        })

    # Canonical test labels are opened only after every prediction above has been frozen.
    y_test = np.asarray(test["label"], dtype=np.int64)
    a_ref = {
        "accuracy": float(accuracy_score(y_test, prediction_bank["A_only"])),
        "macro_f1": float(f1_score(y_test, prediction_bank["A_only"], average="macro")),
    }
    b_ref = {
        "accuracy": float(accuracy_score(y_test, prediction_bank["B_oracle"])),
        "macro_f1": float(f1_score(y_test, prediction_bank["B_oracle"], average="macro")),
    }
    a_acc, b_acc = a_ref["accuracy"], b_ref["accuracy"]

    rows: list[dict] = []
    method_names = ["Procrustes", "RankProcrustes", "Ridge", "CCA", "PLS", "RFF_Ridge", "MLP", "Pontifex", "RankPontifex", "ShuffledPontifex"]
    for item in frozen_rows:
        k = int(item["K"])
        test_payload = {}
        efficiency = {}
        supervision_bytes = int(item["paired_embedding_supervision_bytes_float32"])
        for name in method_names:
            metric = metric_payload(y_test, prediction_bank[f"{name}_K{k}"], a_acc, b_acc)
            test_payload[name] = metric
            delta = metric["accuracy"] - a_acc
            cost = item["methods"][name]["cost"]
            efficiency[name] = {
                "accuracy_delta_over_A_per_shared_probe": delta / k,
                "accuracy_delta_over_A_per_fitted_float": delta / max(1, int(cost["fitted_floats"])),
                "accuracy_delta_over_A_per_supervision_byte": delta / max(1, supervision_bytes),
                "accuracy_delta_over_A_per_fit_second": delta / max(1e-12, float(cost["fit_plus_validation_selection_seconds"])),
            }
        rows.append({**item, "test": test_payload, "efficiency": efficiency})

    target50 = None if b_acc <= a_acc else a_acc + 0.5 * (b_acc - a_acc)
    target90 = None if b_acc <= a_acc else a_acc + 0.9 * (b_acc - a_acc)
    frontier = {
        "target_50pct_A_to_B": target50,
        "target_90pct_A_to_B": target90,
        "min_k_50pct": {m: None if target50 is None else min_k(rows, m, target50) for m in method_names},
        "min_k_90pct": {m: None if target90 is None else min_k(rows, m, target90) for m in method_names},
    }

    payload = {
        "experiment": "Pontifex Banking77 fine-grained single-item cross-model transport",
        "classification": "real external fixed-label-budget cross-task replication",
        "dataset": {
            "name": DATASET, "revision": dataset_revision,
            "canonical_train_rows": len(train), "canonical_test_rows": len(test),
            "primary_metric": "accuracy", "secondary_metric": "macro-F1",
        },
        "spaces": {
            "A": MODEL_A, "A_revision": a_revision,
            "B": MODEL_B, "B_revision": b_revision,
            "pretraining_overlap_A_B": "pretraining_overlap_possible",
            "benchmark_pretraining_overlap_A": "unknown",
            "benchmark_pretraining_overlap_B": "unknown",
        },
        "manifests": {
            "transport_student_ids_sha256": sha_lines(student_ids),
            "transport_val_ids_sha256": sha_lines(transport_val_ids),
            "head_train_ids_sha256": sha_lines(head_train_ids),
            "head_val_ids_sha256": sha_lines(head_val_ids),
            "test_ids_sha256": sha_lines([str(i) for i in range(len(test))]),
            "transport_student_text_sha256": sha_lines(groups["transport_student"]),
            "test_text_sha256": sha_lines(groups["test"]),
            "K_prefix_sha256": {str(k): sha_lines(student_ids[:k]) for k in KS},
            "partition_seed": PARTITION_SEED,
            "random_seed": SEED,
        },
        "information_budgets": {
            "transport_student_rows": len(student_ids), "transport_validation_rows": len(transport_val_ids),
            "labeled_head_train_rows": len(head_train_ids), "labeled_head_validation_rows": len(head_val_ids),
            "test_rows": len(test), "task_labels_used_for_transport_fit_or_selection": 0,
        },
        "head_selection": {"A_only": a_head_sel, "B_oracle": b_head_sel},
        "reference_scores": {"A_only": a_ref, "B_oracle": b_ref, "B_minus_A_accuracy": b_acc - a_acc},
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
            "cross_task_replication": "same MiniLM-to-BGE-small pair as the already-frozen negative AG News benchmark; Banking77 does not revise AG News criteria",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
