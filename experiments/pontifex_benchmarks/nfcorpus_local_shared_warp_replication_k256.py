# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.28",
#   "numpy>=2.0",
#   "scikit-learn>=1.7",
#   "scipy>=1.14",
#   "sentence-transformers>=5.0",
#   "huggingface-hub>=0.34",
# ]
# ///
"""Independent NFCorpus replication of Pontifex shared-warp coherence.

Preregistered protocol:
PROTOCOL-NFCORPUS-LOCAL-SHARED-WARP-REPLICATION-K256-2026-09-19.md

The script deliberately keeps D_test relevance grades sealed until the paired
A->B map, D_val selector output, residual-norm strata, two local derangement
banks, locality calibration, and all membership manifests are frozen.

Primary claim under test: a shared query/document residual warp preserves more
held-out retrieval structure than independently warped query/document sides.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import zipfile
from pathlib import Path

import httpx
import numpy as np
from scipy.optimize import linear_sum_assignment
from sentence_transformers import SentenceTransformer

import scifact_transport as base

DATASET = "nfcorpus"
BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nfcorpus.zip"
BEIR_MD5 = "a89dba18a62ef92f7d323ec890a0d38d"

MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_A_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
MODEL_B = "sentence-transformers/all-mpnet-base-v2"
MODEL_B_REVISION = "e8c3b32edf5434bc2275fc9bab85f82640a19130"

K = 256
N_NULL = 31
N_NORM_STRATA = 8
SEED = 20260919
LOCALITY_CAPTURE_MIN = 0.50
JITTER_LADDER = (0.01, 0.02, 0.05, 0.10, 0.20, 0.40)
MAX_CANDIDATES_PER_JITTER = 400
BOOTSTRAP_RESAMPLES = 5000


def md5_file(path: Path) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_lines(lines: list[str]) -> str:
    h = hashlib.sha256()
    for line in lines:
        h.update(str(line).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def ensure_dataset(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / f"{DATASET}.zip"
    root = cache_dir / DATASET
    if not archive.exists():
        with httpx.stream("GET", BEIR_URL, follow_redirects=True, timeout=120) as response:
            response.raise_for_status()
            with archive.open("wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
    digest = md5_file(archive)
    if digest != BEIR_MD5:
        raise RuntimeError(f"NFCorpus archive md5 mismatch: {digest} != {BEIR_MD5}")
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
        raise RuntimeError(f"missing NFCorpus files: {missing}")
    return root


def load_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def qid_membership(path: Path) -> list[str]:
    """Read split membership only; relevance scores are ignored."""
    qids: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not reader.fieldnames or "query-id" not in reader.fieldnames:
            raise RuntimeError(f"unexpected qrels header in {path}: {reader.fieldnames}")
        for row in reader:
            qids.add(str(row["query-id"]))
    return sorted(qids)


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


def encode(model_name: str, revision: str, texts: list[str], batch_size: int) -> np.ndarray:
    model = SentenceTransformer(model_name, revision=revision)
    return model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)


def norm_strata(residual: np.ndarray, n_strata: int) -> tuple[np.ndarray, list[np.ndarray]]:
    if residual.shape[0] % n_strata != 0:
        raise RuntimeError("K must divide evenly into residual-norm strata")
    order = np.argsort(np.linalg.norm(residual, axis=1), kind="mergesort")
    chunks = [np.asarray(x, dtype=np.int64) for x in np.array_split(order, n_strata)]
    labels = np.empty(residual.shape[0], dtype=np.int64)
    for s, idx in enumerate(chunks):
        labels[idx] = s
    return labels, chunks


def cosine_distance_matrix(x: np.ndarray) -> np.ndarray:
    z = base.l2norm(x)
    return np.clip(1.0 - (z @ z.T), 0.0, 2.0).astype(np.float64)


def mincost_derangement(dist: np.ndarray, chunks: list[np.ndarray]) -> np.ndarray:
    perm = np.empty(dist.shape[0], dtype=np.int64)
    for idx in chunks:
        cost = dist[np.ix_(idx, idx)].copy()
        np.fill_diagonal(cost, 1e9)
        rows, cols = linear_sum_assignment(cost)
        if not np.array_equal(rows, np.arange(len(idx))):
            raise RuntimeError("unexpected assignment row order")
        donor = idx[cols]
        if np.any(donor == idx):
            raise RuntimeError("minimum-cost assignment contains a fixed point")
        perm[idx] = donor
    return perm


def random_within_stratum_expected(dist: np.ndarray, chunks: list[np.ndarray]) -> float:
    total = 0.0
    n = 0
    for idx in chunks:
        block = dist[np.ix_(idx, idx)]
        mask = ~np.eye(len(idx), dtype=bool)
        total += float(block[mask].sum())
        n += int(mask.sum())
    return total / n


def locality_capture(actual: float, random_mean: float, optimum_mean: float) -> float:
    denom = random_mean - optimum_mean
    if denom <= 0:
        raise RuntimeError("invalid locality reference ordering")
    return float((random_mean - actual) / denom)


def local_derangement_bank(
    dist: np.ndarray,
    chunks: list[np.ndarray],
    n: int,
    seed: int,
    capture_min: float,
) -> tuple[list[np.ndarray], dict[str, float | int | list[float]]]:
    """Freeze diverse local perfect derangements from D_student geometry only.

    Candidates solve a noisy assignment problem inside each residual-norm
    stratum. A candidate is accepted only if its unperturbed donor distance
    captures at least `capture_min` of the random->minimum-cost locality gap.
    The jitter ladder and attempt budget are preregistered.
    """
    optimum = mincost_derangement(dist, chunks)
    optimum_mean = float(np.mean(dist[np.arange(dist.shape[0]), optimum]))
    random_mean = random_within_stratum_expected(dist, chunks)
    gap = random_mean - optimum_mean
    if gap <= 1e-12:
        raise RuntimeError("locality gap is degenerate")

    rng = np.random.default_rng(seed)
    seen: set[bytes] = {np.arange(dist.shape[0], dtype=np.int64).tobytes()}
    bank: list[np.ndarray] = []
    captures: list[float] = []
    distances: list[float] = []
    accepted_by_jitter: list[float] = []

    for jitter in JITTER_LADDER:
        if len(bank) >= n:
            break
        scale = jitter * gap
        for _ in range(MAX_CANDIDATES_PER_JITTER):
            if len(bank) >= n:
                break
            perm = np.empty(dist.shape[0], dtype=np.int64)
            for idx in chunks:
                cost = dist[np.ix_(idx, idx)].copy()
                noise = rng.gumbel(loc=0.0, scale=scale, size=cost.shape)
                noisy = cost + noise
                np.fill_diagonal(noisy, 1e9)
                rows, cols = linear_sum_assignment(noisy)
                if not np.array_equal(rows, np.arange(len(idx))):
                    raise RuntimeError("unexpected assignment row order")
                perm[idx] = idx[cols]
            if np.any(perm == np.arange(dist.shape[0])):
                raise RuntimeError("candidate assignment contains a fixed point")
            key = perm.tobytes()
            if key in seen:
                continue
            actual = float(np.mean(dist[np.arange(dist.shape[0]), perm]))
            capture = locality_capture(actual, random_mean, optimum_mean)
            if capture + 1e-12 < capture_min:
                continue
            seen.add(key)
            bank.append(perm.copy())
            captures.append(capture)
            distances.append(actual)
            accepted_by_jitter.append(float(jitter))

    if len(bank) != n:
        raise RuntimeError(
            f"failed closed before D_test: only {len(bank)}/{n} unique local "
            f"derangements met locality_capture>={capture_min}"
        )

    return bank, {
        "minimum_cost_mean_A_cosine_distance": optimum_mean,
        "random_within_stratum_expected_mean_A_cosine_distance": random_mean,
        "bank_mean_A_cosine_distance": float(np.mean(distances)),
        "bank_max_A_cosine_distance": float(np.max(distances)),
        "bank_mean_locality_capture": float(np.mean(captures)),
        "bank_min_locality_capture": float(np.min(captures)),
        "locality_capture_threshold": float(capture_min),
        "accepted_jitter_values": accepted_by_jitter,
    }


def bank_manifest(bank: list[np.ndarray]) -> str:
    return sha256_lines([" ".join(map(str, p.tolist())) for p in bank])


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


def scores(q: np.ndarray, d: np.ndarray) -> np.ndarray:
    return base.l2norm(q) @ base.l2norm(d).T


def per_query_ndcg(
    qrels: dict[str, dict[str, int]],
    qids: list[str],
    doc_ids: list[str],
    score_matrix: np.ndarray,
    k: int = 10,
) -> np.ndarray:
    vals: list[float] = []
    for i, qid in enumerate(qids):
        order = np.argsort(score_matrix[i])[::-1][:k]
        rels = np.asarray([qrels[qid].get(doc_ids[j], 0) for j in order], dtype=np.float64)
        discounts = 1.0 / np.log2(np.arange(2, len(rels) + 2))
        dcg = float(np.sum((np.power(2.0, rels) - 1.0) * discounts))
        ideal = np.sort(np.asarray(list(qrels[qid].values()), dtype=np.float64))[::-1][:k]
        idcg = float(
            np.sum(
                (np.power(2.0, ideal) - 1.0)
                / np.log2(np.arange(2, len(ideal) + 2))
            )
        )
        vals.append(0.0 if idcg == 0.0 else dcg / idcg)
    return np.asarray(vals, dtype=np.float64)


def bootstrap_summary(values: np.ndarray, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(BOOTSTRAP_RESAMPLES):
        means[i] = float(values[rng.integers(0, n, size=n)].mean())
    lo, hi = np.quantile(means, [0.025, 0.975])
    return {
        "mean": float(values.mean()),
        "ci95_percentile_low": float(lo),
        "ci95_percentile_high": float(hi),
        "bootstrap_probability_mean_gt_zero": float(np.mean(means > 0.0)),
        "n_queries": int(n),
        "n_resamples": BOOTSTRAP_RESAMPLES,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/pontifex-nfcorpus"))
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("pontifex-nfcorpus-local-shared-warp-k256.json"),
    )
    args = ap.parse_args()
    if args.seed != SEED:
        raise RuntimeError(f"protocol freezes seed={SEED}")

    root = ensure_dataset(args.cache_dir)

    corpus_rows = load_jsonl(root / "corpus.jsonl")
    query_rows = load_jsonl(root / "queries.jsonl")
    corpus_ids = [str(r["_id"]) for r in corpus_rows]
    corpus_texts = [
        (" ".join([str(r.get("title", "")), str(r.get("text", ""))])).strip()
        for r in corpus_rows
    ]
    queries = {str(r["_id"]): str(r["text"]).strip() for r in query_rows}
    train_ids = qid_membership(root / "qrels" / "train.tsv")
    test_ids = qid_membership(root / "qrels" / "test.tsv")

    missing_queries = [q for q in train_ids + test_ids if q not in queries]
    if missing_queries:
        raise RuntimeError(f"qrel query IDs missing from queries.jsonl: {missing_queries[:5]}")

    test_texts = {queries[q] for q in test_ids}
    eligible_ids = [q for q in train_ids if queries[q] not in test_texts]
    rng = np.random.default_rng(args.seed)
    order = rng.permutation(len(eligible_ids))
    eligible_ids = [eligible_ids[i] for i in order]
    cut = max(1, int(math.floor(0.80 * len(eligible_ids))))
    student_ids = eligible_ids[:cut]
    val_ids = eligible_ids[cut:]
    if len(student_ids) < K:
        raise RuntimeError(f"K={K} exceeds NFCorpus student pool {len(student_ids)}")

    a_train = encode(MODEL_A, MODEL_A_REVISION, [queries[q] for q in train_ids], 128)
    b_train = encode(MODEL_B, MODEL_B_REVISION, [queries[q] for q in train_ids], 64)
    a_test = encode(MODEL_A, MODEL_A_REVISION, [queries[q] for q in test_ids], 128)
    a_docs = encode(MODEL_A, MODEL_A_REVISION, corpus_texts, 128)

    train_pos = {qid: i for i, qid in enumerate(train_ids)}
    student_idx = np.asarray([train_pos[q] for q in student_ids], dtype=np.int64)
    val_idx = np.asarray([train_pos[q] for q in val_ids], dtype=np.int64)
    a_student = a_train[student_idx]
    b_student = b_train[student_idx]
    a_val = a_train[val_idx]
    b_val = b_train[val_idx]

    aa = a_student[:K]
    bb = b_student[:K]
    tau, lam, val_loss, coarse, residual = base.select_torus(aa, bb, a_val, b_val)
    norm_labels, norm_chunks = norm_strata(residual, N_NORM_STRATA)
    dist = cosine_distance_matrix(aa)

    query_bank, query_locality = local_derangement_bank(
        dist, norm_chunks, N_NULL, args.seed + 1_000_000, LOCALITY_CAPTURE_MIN
    )
    document_bank, document_locality = local_derangement_bank(
        dist, norm_chunks, N_NULL, args.seed + 2_000_000, LOCALITY_CAPTURE_MIN
    )
    query_keys = {p.tobytes() for p in query_bank}
    if any(p.tobytes() in query_keys for p in document_bank):
        raise RuntimeError(
            "query/document local banks overlap; protocol requires disjoint banks"
        )

    coarse_q = base.apply_procrustes(a_test, *coarse).astype(np.float32)
    coarse_d = base.apply_procrustes(a_docs, *coarse).astype(np.float32)
    wq = local_weights(a_test, aa, tau)
    wd = local_weights(a_docs, aa, tau)

    frozen_manifest = {
        "dataset_archive_md5": BEIR_MD5,
        "model_A": f"{MODEL_A}@{MODEL_A_REVISION}",
        "model_B": f"{MODEL_B}@{MODEL_B_REVISION}",
        "train_ids_sha256": sha256_lines(train_ids),
        "student_ids_sha256": sha256_lines(student_ids),
        "validation_ids_sha256": sha256_lines(val_ids),
        "anchor_ids_sha256": sha256_lines(student_ids[:K]),
        "test_ids_sha256": sha256_lines(test_ids),
        "corpus_ids_sha256": sha256_lines(corpus_ids),
        "norm_strata_sha256": sha256_lines([str(x) for x in norm_labels.tolist()]),
        "query_local_bank_sha256": bank_manifest(query_bank),
        "document_local_bank_sha256": bank_manifest(document_bank),
    }

    test_qrels = load_qrels(root / "qrels" / "test.tsv")
    if sorted(test_qrels) != test_ids:
        raise RuntimeError("test qrel membership changed between seal and grade load")

    true_q = mapped(coarse_q, wq, residual, None, lam)
    true_d = mapped(coarse_d, wd, residual, None, lam)
    true_per_query = per_query_ndcg(
        test_qrels, test_ids, corpus_ids, scores(true_q, true_d)
    )

    coupled_rows: list[np.ndarray] = []
    independent_rows: list[np.ndarray] = []
    for qp, dp in zip(query_bank, document_bank, strict=True):
        q_null = mapped(coarse_q, wq, residual, qp, lam)
        d_coupled = mapped(coarse_d, wd, residual, qp, lam)
        d_independent = mapped(coarse_d, wd, residual, dp, lam)
        coupled_rows.append(
            per_query_ndcg(test_qrels, test_ids, corpus_ids, scores(q_null, d_coupled))
        )
        independent_rows.append(
            per_query_ndcg(
                test_qrels, test_ids, corpus_ids, scores(q_null, d_independent)
            )
        )

    coupled = np.stack(coupled_rows, axis=0)
    independent = np.stack(independent_rows, axis=0)
    coupled_global = coupled.mean(axis=1)
    independent_global = independent.mean(axis=1)
    coupled_per_query = coupled.mean(axis=0)
    independent_per_query = independent.mean(axis=0)

    shared_warp_delta = coupled_per_query - independent_per_query
    exact_identity_delta = true_per_query - coupled_per_query
    shared_boot = bootstrap_summary(shared_warp_delta, args.seed + 3_000_000)
    identity_boot = bootstrap_summary(exact_identity_delta, args.seed + 4_000_000)

    result = {
        "experiment": "Pontifex NFCorpus independent local shared-warp replication K=256",
        "classification": "independent dataset replication preregistered before first NFCorpus D_test relevance-grade read",
        "protocol": "PROTOCOL-NFCORPUS-LOCAL-SHARED-WARP-REPLICATION-K256-2026-09-19.md",
        "k": K,
        "n_null": N_NULL,
        "n_residual_norm_strata": N_NORM_STRATA,
        "seed": args.seed,
        "split_contract": {
            "D_assembly": "canonical NFCorpus archive, text/split membership, frozen encoder revisions; no relevance grades used for fit/selection",
            "D_student": "80% deterministic exact-test-text-overlap-filtered train-query A/B representation pairs; anchors, residual strata, local nuisance banks defined here",
            "D_val": "remaining 20% train-query A/B pairs; coordinate-only tau/lambda selection",
            "D_test": "official NFCorpus test relevance grades loaded only after map, selector output, strata, local banks, locality calibration, manifests, and A-side mapped-coordinate ingredients are frozen",
            "B_test_coordinates_encoded": False,
            "B_corpus_coordinates_encoded": False,
            "task_labels_used_for_fit_or_selection": 0,
        },
        "selection": {
            "tau": float(tau),
            "lambda": float(lam),
            "D_val_coordinate_loss": float(val_loss),
        },
        "local_null_contract": {
            "residual_norm_strata": N_NORM_STRATA,
            "identity_destroyed": True,
            "locality_capture_definition": "(random-within-stratum distance - bank distance) / (random-within-stratum distance - minimum-cost derangement distance)",
            "minimum_required_capture": LOCALITY_CAPTURE_MIN,
            "query_bank": query_locality,
            "document_bank": document_locality,
            "query_document_banks_disjoint": True,
            "jitter_ladder": list(JITTER_LADDER),
        },
        "manifests": frozen_manifest,
        "test_ndcg_at_10": {
            "TRUE": float(true_per_query.mean()),
            "LOCAL_COUPLED_mean": float(coupled_global.mean()),
            "LOCAL_COUPLED_median": float(np.median(coupled_global)),
            "LOCAL_INDEPENDENT_mean": float(independent_global.mean()),
            "LOCAL_INDEPENDENT_median": float(np.median(independent_global)),
        },
        "primary_contrast": {
            "shared_warp_LOCAL_COUPLED_minus_LOCAL_INDEPENDENT_mean": float(
                shared_warp_delta.mean()
            ),
            "paired_query_bootstrap": shared_boot,
            "predeclared_supported": bool(shared_boot["ci95_percentile_low"] > 0.0),
            "criterion": "paired-query 95% percentile CI strictly above zero",
        },
        "secondary_contrast": {
            "exact_identity_TRUE_minus_LOCAL_COUPLED_mean": float(
                exact_identity_delta.mean()
            ),
            "paired_query_bootstrap": identity_boot,
            "status": "secondary; not the preregistered replication target",
        },
        "null_global_ndcg_at_10": {
            "LOCAL_COUPLED": [float(x) for x in coupled_global],
            "LOCAL_INDEPENDENT": [float(x) for x in independent_global],
        },
        "interpretation_boundary": {
            "evidence_if_positive": "replication across an independent BEIR dataset, with the same frozen encoder pair, that a shared two-sided local residual deformation preserves more held-out retrieval structure than independent local deformations",
            "evidence_if_negative": "failure of that shared-warp claim to replicate under this NFCorpus representation pair and frozen local-null design",
            "not_evidence": "physical or intrinsic torus topology, causal semantic locality, universal transport superiority, native-B superiority, exact residual identity necessity, low-budget dominance, or Assembly-to-student generalization",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
