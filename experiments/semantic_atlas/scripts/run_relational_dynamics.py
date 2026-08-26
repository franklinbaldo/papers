from __future__ import annotations

import argparse
import functools
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from semantic_atlas.embedding_cache import write_embedding_cache
from semantic_atlas.frame import QuasarFrame
from semantic_atlas.relational_dynamics import (
    churn_trace,
    cosine_scores,
    csls_scores,
    deterministic_kmeans,
    empirical_mutual_proximity_scores,
    gap_churn_summary,
    hubness_summary,
    l2_normalize,
    null_summary,
    rankings_from_scores,
    resolution_summary,
    semantic_drift_score,
    trace_correlation,
    trace_divergence,
)


@functools.lru_cache(maxsize=1)
def _repo_root() -> str:
    here = Path(__file__).resolve().parent
    output = subprocess.check_output(
        ["git", "-C", str(here), "rev-parse", "--show-toplevel"], text=True
    )
    return output.strip()


def _git_paths(commit: str) -> list[str]:
    output = subprocess.check_output(
        ["git", "-C", _repo_root(), "ls-tree", "-r", "--name-only", commit], text=True
    )
    paths = [line.strip() for line in output.splitlines() if line.strip().endswith(".md")]
    return sorted(paths, key=lambda path: hashlib.sha256(path.encode()).hexdigest())


def _git_text(commit: str, path: str, limit: int) -> str:
    raw = subprocess.check_output(["git", "-C", _repo_root(), "show", f"{commit}:{path}"])
    return raw.decode("utf-8", errors="replace").strip()[:limit]


def _first_touch_unix(commit: str, path: str) -> int:
    output = subprocess.check_output(
        [
            "git",
            "-C",
            _repo_root(),
            "log",
            "--follow",
            "--format=%ct",
            commit,
            "--",
            path,
        ],
        text=True,
    )
    rows = [line.strip() for line in output.splitlines() if line.strip()]
    if not rows:
        raise RuntimeError(f"no git history for corpus path: {path}")
    return int(rows[-1])


def _split_corpus(base_manifest: dict) -> dict[str, list[str]]:
    corpus = base_manifest["corpus"]
    total = corpus["calibration_count"] + corpus["heldout_count"] + corpus["trajectory_count"]
    paths = _git_paths(base_manifest["source_commit"])
    if len(paths) < total:
        raise RuntimeError(f"need {total} markdown files at source_commit, found {len(paths)}")
    chosen = paths[:total]
    a = corpus["calibration_count"]
    b = a + corpus["heldout_count"]
    return {
        "calibration": chosen[:a],
        "heldout": chosen[a:b],
        "trajectory": chosen[b:],
    }


def _load_sentence_model(spec: dict):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(spec["model"], revision=spec["revision"])


def _encode_raw(model, texts: list[str]) -> np.ndarray:
    return np.asarray(
        model.encode(texts, convert_to_numpy=True, normalize_embeddings=False),
        dtype=np.float64,
    )


def _cross_model_retrieval(reference: np.ndarray, transfer: np.ndarray) -> dict[str, float]:
    reference = l2_normalize(reference)
    transfer = l2_normalize(transfer)
    sim = reference @ transfer.T
    n = len(sim)
    target = np.arange(n)

    def direction(values: np.ndarray) -> tuple[float, float]:
        ranks = np.argsort(-values, axis=1, kind="stable")
        p1 = float(np.mean(ranks[:, 0] == target))
        p5 = float(np.mean([target[i] in ranks[i, : min(5, n)] for i in range(n)]))
        return p1, p5

    p1_ab, p5_ab = direction(sim)
    p1_ba, p5_ba = direction(sim.T)
    paired = float(np.mean(np.sum(reference * transfer, axis=1)))
    upper = np.triu_indices(n, k=1)
    pair_ref = (reference @ reference.T)[upper]
    pair_transfer = (transfer @ transfer.T)[upper]
    corr = (
        float(np.corrcoef(pair_ref, pair_transfer)[0, 1])
        if np.std(pair_ref) > 1e-12 and np.std(pair_transfer) > 1e-12
        else float("nan")
    )
    return {
        "paired_canonical_cosine": paired,
        "self_retrieval_p1_reference_to_transfer": p1_ab,
        "self_retrieval_p5_reference_to_transfer": p5_ab,
        "self_retrieval_p1_transfer_to_reference": p1_ba,
        "self_retrieval_p5_transfer_to_reference": p5_ba,
        "pairwise_cosine_correlation": corr,
    }


def _knn_overlap(rank_a: np.ndarray, rank_b: np.ndarray, k: int) -> float:
    return float(
        np.mean(
            [
                len(set(rank_a[i, :k]) & set(rank_b[i, :k])) / k
                for i in range(len(rank_a))
            ]
        )
    )


def _trace_public(trace: dict) -> dict:
    return {
        "k": trace["k"],
        "initial_n": trace["initial_n"],
        "batch_size": trace["batch_size"],
        "transitions": trace["transitions"],
    }


def _model_correction_bundle(raw_scores: np.ndarray, csls_q: int) -> dict[str, np.ndarray]:
    return {
        "raw_cosine": raw_scores,
        "csls": csls_scores(raw_scores, neighborhood=csls_q),
        "mutual_proximity": empirical_mutual_proximity_scores(raw_scores),
    }


def _permutation_metrics(
    score_a: np.ndarray,
    score_b: np.ndarray,
    order: np.ndarray,
    *,
    k: int,
    initial_n: int,
    batch_size: int,
    region_labels: np.ndarray,
) -> tuple[float, float]:
    ta = churn_trace(
        score_a,
        order,
        k=k,
        initial_n=initial_n,
        batch_size=batch_size,
        region_labels=region_labels,
    )
    tb = churn_trace(
        score_b,
        order,
        k=k,
        initial_n=initial_n,
        batch_size=batch_size,
        region_labels=region_labels,
    )
    return trace_divergence(ta, tb), trace_divergence(ta, tb, regional=True)


def run(protocol_path: Path, output_path: Path, cache_dir: Path) -> dict:
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    base_manifest_path = protocol_path.parent / protocol["base_manifest"]
    base_manifest = json.loads(base_manifest_path.read_text(encoding="utf-8"))
    source_commit = base_manifest["source_commit"]
    split_paths = _split_corpus(base_manifest)
    excerpt_chars = base_manifest["corpus"]["excerpt_chars"]
    split_texts = {
        split: [_git_text(source_commit, path, excerpt_chars) for path in paths]
        for split, paths in split_paths.items()
    }

    observers = {
        "reference_observer": base_manifest["reference_observer"],
        "transfer_observer": base_manifest["transfer_observer"],
    }
    raw_by_observer: dict[str, dict[str, np.ndarray]] = {}
    normalized_by_observer: dict[str, dict[str, np.ndarray]] = {}
    cache_refs = {}
    for observer_name, spec in observers.items():
        model = _load_sentence_model(spec)
        raw_splits = {
            split: _encode_raw(model, split_texts[split]) for split in split_paths
        }
        normalized_splits = {split: l2_normalize(values) for split, values in raw_splits.items()}
        raw_by_observer[observer_name] = raw_splits
        normalized_by_observer[observer_name] = normalized_splits
        ref = write_embedding_cache(
            cache_dir / observer_name,
            observer=spec,
            source_commit=source_commit,
            paths_by_split=split_paths,
            texts_by_split=split_texts,
            raw_by_split=raw_splits,
            normalized_by_split=normalized_splits,
        )
        cache_refs[observer_name] = {
            "manifest": str(ref.manifest_path),
            "data": str(ref.data_path),
            "data_sha256": ref.data_sha256,
            "corpus_sha256": ref.corpus_sha256,
        }
        del model

    split_order = ["calibration", "heldout", "trajectory"]
    all_paths = [path for split in split_order for path in split_paths[split]]
    ref_all = np.vstack(
        [normalized_by_observer["reference_observer"][split] for split in split_order]
    )
    transfer_all = np.vstack(
        [normalized_by_observer["transfer_observer"][split] for split in split_order]
    )
    n = len(all_paths)

    cal_n = len(split_paths["calibration"])
    frame, canonical_targets = QuasarFrame.reference(
        ref_all[:cal_n], dim=int(base_manifest["srf_dim"])
    )
    transfer_frame = QuasarFrame.fit(transfer_all[:cal_n], canonical_targets)
    ref_canonical = frame.canonical_vectors(ref_all)
    transfer_canonical = transfer_frame.canonical_vectors(transfer_all)
    midpoint = l2_normalize(ref_canonical + transfer_canonical)
    region_labels = deterministic_kmeans(midpoint, k=int(protocol["region_count"]))

    first_touch = [_first_touch_unix(source_commit, path) for path in all_paths]
    chronological_order = np.asarray(
        sorted(
            range(n),
            key=lambda i: (
                first_touch[i],
                hashlib.sha256(all_paths[i].encode("utf-8")).hexdigest(),
            ),
        ),
        dtype=np.int64,
    )

    primary_k = int(protocol["k"])
    initial_n = int(protocol["initial_n"])
    batch_size = int(protocol["batch_size"])
    permutations = int(protocol["null_permutations"])
    seed = int(protocol["null_seed"])
    csls_q = int(protocol["hubness_controls"]["csls"]["neighborhood"])

    raw_ref_scores = cosine_scores(ref_all)
    raw_transfer_scores = cosine_scores(transfer_all)
    ref_scores = _model_correction_bundle(raw_ref_scores, csls_q)
    transfer_scores = _model_correction_bundle(raw_transfer_scores, csls_q)

    static_alignment = _cross_model_retrieval(ref_canonical, transfer_canonical)
    static_alignment["native_final_knn_overlap_k"] = primary_k
    static_alignment["native_final_knn_overlap"] = _knn_overlap(
        rankings_from_scores(raw_ref_scores), rankings_from_scores(raw_transfer_scores), primary_k
    )

    observed = {}
    hubness = {}
    for correction in ref_scores:
        ta = churn_trace(
            ref_scores[correction],
            chronological_order,
            k=primary_k,
            initial_n=initial_n,
            batch_size=batch_size,
            region_labels=region_labels,
        )
        tb = churn_trace(
            transfer_scores[correction],
            chronological_order,
            k=primary_k,
            initial_n=initial_n,
            batch_size=batch_size,
            region_labels=region_labels,
        )
        observed[correction] = {
            "global_dynamic_divergence": trace_divergence(ta, tb),
            "regional_dynamic_divergence": trace_divergence(ta, tb, regional=True),
            "hazard_correlation": trace_correlation(ta, tb),
            "reference": {
                "trace": _trace_public(ta),
                "gap_churn": gap_churn_summary(ta),
                "resolution": resolution_summary(ta, region_labels, n),
            },
            "transfer": {
                "trace": _trace_public(tb),
                "gap_churn": gap_churn_summary(tb),
                "resolution": resolution_summary(tb, region_labels, n),
            },
        }
        hubness[correction] = {
            "reference": hubness_summary(rankings_from_scores(ref_scores[correction]), primary_k),
            "transfer": hubness_summary(rankings_from_scores(transfer_scores[correction]), primary_k),
        }

    observed_drift = semantic_drift_score(
        ref_all,
        transfer_all,
        chronological_order,
        initial_n=initial_n,
        batch_size=batch_size,
    )
    null_rng = np.random.default_rng(seed)
    null_orders = [null_rng.permutation(n) for _ in range(permutations)]
    null_drift = np.asarray(
        [
            semantic_drift_score(
                ref_all,
                transfer_all,
                order,
                initial_n=initial_n,
                batch_size=batch_size,
            )
            for order in null_orders
        ],
        dtype=np.float64,
    )

    null_tests = {"semantic_drift": null_summary(observed_drift, null_drift)}
    for correction in ref_scores:
        global_null = []
        regional_null = []
        for order in null_orders:
            global_value, regional_value = _permutation_metrics(
                ref_scores[correction],
                transfer_scores[correction],
                order,
                k=primary_k,
                initial_n=initial_n,
                batch_size=batch_size,
                region_labels=region_labels,
            )
            global_null.append(global_value)
            regional_null.append(regional_value)
        null_tests[correction] = {
            "global_dynamic_divergence": null_summary(
                observed[correction]["global_dynamic_divergence"], np.asarray(global_null)
            ),
            "regional_dynamic_divergence": null_summary(
                observed[correction]["regional_dynamic_divergence"], np.asarray(regional_null)
            ),
        }

    sensitivity = {}
    for k_value in protocol.get("sensitivity_k", []):
        k_value = int(k_value)
        obs_global, obs_regional = _permutation_metrics(
            raw_ref_scores,
            raw_transfer_scores,
            chronological_order,
            k=k_value,
            initial_n=initial_n,
            batch_size=batch_size,
            region_labels=region_labels,
        )
        global_null = []
        for order in null_orders:
            value, _ = _permutation_metrics(
                raw_ref_scores,
                raw_transfer_scores,
                order,
                k=k_value,
                initial_n=initial_n,
                batch_size=batch_size,
                region_labels=region_labels,
            )
            global_null.append(value)
        sensitivity[str(k_value)] = {
            "global_dynamic_divergence": null_summary(obs_global, np.asarray(global_null)),
            "observed_regional_dynamic_divergence": obs_regional,
        }

    raw_p = null_tests["raw_cosine"]["global_dynamic_divergence"]["p_upper"]
    alpha = float(protocol["alpha"])
    drift_sig = null_tests["semantic_drift"]["p_upper"] < alpha
    effective_controls = []
    control_significance = {}
    raw_hub = hubness["raw_cosine"]
    for correction in ("csls", "mutual_proximity"):
        reduced_ref = abs(hubness[correction]["reference"]["k_occurrence_skewness"]) < abs(
            raw_hub["reference"]["k_occurrence_skewness"]
        )
        reduced_transfer = abs(hubness[correction]["transfer"]["k_occurrence_skewness"]) < abs(
            raw_hub["transfer"]["k_occurrence_skewness"]
        )
        effective = bool(reduced_ref and reduced_transfer)
        if effective:
            effective_controls.append(correction)
        control_significance[correction] = {
            "reduced_hubness_in_both_observers": effective,
            "dynamic_divergence_p_upper": null_tests[correction]["global_dynamic_divergence"]["p_upper"],
        }

    if not drift_sig:
        classification = "stationary-null-not-rejected"
    elif raw_p >= alpha:
        classification = "dynamic-transfer-not-rejected"
    elif effective_controls and all(
        null_tests[name]["global_dynamic_divergence"]["p_upper"] < alpha
        for name in effective_controls
    ):
        classification = "model-specific-relational-dynamics-survive-hubness-controls"
    elif any(
        null_tests[name]["global_dynamic_divergence"]["p_upper"] >= alpha
        for name in effective_controls
    ):
        classification = "raw-divergence-hubness-sensitive"
    else:
        classification = "raw-divergence-hubness-controls-ineffective"

    chronology = [
        {
            "rank": rank,
            "path": all_paths[int(doc_id)],
            "first_touch_unix": int(first_touch[int(doc_id)]),
            "first_touch_utc": datetime.fromtimestamp(first_touch[int(doc_id)], tz=UTC).isoformat(),
            "region": int(region_labels[int(doc_id)]),
        }
        for rank, doc_id in enumerate(chronological_order.tolist())
    ]

    result = {
        "schema_version": 1,
        "experiment": protocol["experiment"],
        "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "source_commit": source_commit,
        "corpus_count": n,
        "observers": observers,
        "embedding_caches": cache_refs,
        "chronology": chronology,
        "static_alignment": static_alignment,
        "hubness": hubness,
        "observed": observed,
        "null_tests": null_tests,
        "sensitivity": sensitivity,
        "control_effectiveness": control_significance,
        "classification": classification,
        "interpretation_rule": protocol["interpretation_rule"],
        "dbnorm_note": protocol["hubness_controls"]["dbnorm_note"],
        "claim_boundary": (
            "Frozen encoders only. Coordinates never move; only corpus-induced relational structure is replayed. "
            "The stationary/exchangeable insertion null is the primary falsifier. No generator, labels, or policy are used."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol", type=Path, default=Path("relational_dynamics_v1.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/relational_dynamics_v1.json")
    )
    parser.add_argument(
        "--embedding-cache-dir",
        type=Path,
        default=Path("artifacts/embedding_cache_relational_v1"),
    )
    args = parser.parse_args()
    result = run(args.protocol, args.output, args.embedding_cache_dir)
    summary = {
        "classification": result["classification"],
        "static_alignment": result["static_alignment"],
        "semantic_drift": result["null_tests"]["semantic_drift"],
        "raw_dynamic_divergence": result["null_tests"]["raw_cosine"]["global_dynamic_divergence"],
        "csls_dynamic_divergence": result["null_tests"]["csls"]["global_dynamic_divergence"],
        "mp_dynamic_divergence": result["null_tests"]["mutual_proximity"]["global_dynamic_divergence"],
    }
    print(json.dumps(summary, indent=2))
    print(f"artifact={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
