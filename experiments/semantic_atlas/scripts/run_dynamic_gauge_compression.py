from __future__ import annotations

import argparse
import gc
import hashlib
import json
from pathlib import Path

import numpy as np

from semantic_atlas.dynamic_gauge import (
    FrozenFieldSpec,
    compression_report,
    paired_concordance,
)
from semantic_atlas.frame import QuasarFrame
from run_model_backed_a import (
    _encode_raw,
    _l2_normalize,
    _load_sentence_model,
    _split_corpus,
    _texts,
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json_with_bytes(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    return json.loads(raw), raw


def _generate_text_trajectories(base_manifest: dict, prompts: list[str]) -> list[dict]:
    """Generate once; both semantic observers later see these exact same texts."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    spec = base_manifest["generator"]
    cfg = base_manifest["trajectory"]
    tokenizer = AutoTokenizer.from_pretrained(spec["model"], revision=spec["revision"])
    model = AutoModelForCausalLM.from_pretrained(
        spec["model"],
        revision=spec["revision"],
        torch_dtype="auto",
        device_map="auto",
    )
    model.eval()

    rows: list[dict] = []
    for prompt_index, source in enumerate(prompts):
        prompt = source + "\n\nContinue coherently:"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        for generation_seed in cfg["seeds"]:
            generation_seed = int(generation_seed)
            torch.manual_seed(generation_seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(generation_seed)
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=int(cfg["max_new_tokens"]),
                    do_sample=bool(cfg["do_sample"]),
                    temperature=float(cfg["temperature"]),
                )
            new_ids = generated[0, inputs["input_ids"].shape[1] :]
            cumulative = [prompt]
            chunk_tokens = int(cfg["chunk_tokens"])
            for end in range(chunk_tokens, len(new_ids) + chunk_tokens, chunk_tokens):
                chunk_ids = new_ids[: min(end, len(new_ids))]
                continuation = tokenizer.decode(chunk_ids, skip_special_tokens=True)
                cumulative.append(prompt + continuation)
                if end >= len(new_ids):
                    break
            final_continuation = tokenizer.decode(new_ids, skip_special_tokens=True)
            rows.append(
                {
                    "prompt_index": prompt_index,
                    "generation_seed": generation_seed,
                    "generated_tokens": int(len(new_ids)),
                    "continuation_sha256": hashlib.sha256(
                        final_continuation.encode("utf-8")
                    ).hexdigest(),
                    "texts": cumulative,
                }
            )

    del model
    del tokenizer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return rows


def _trajectory_split(
    rows: list[dict], *, seed: int, train_fraction: float
) -> tuple[list[int], list[int]]:
    if len(rows) < 2:
        raise ValueError("DGCT needs at least two generated trajectories")
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must lie in (0, 1)")

    def split_key(index: int) -> str:
        row = rows[index]
        raw = f"{seed}:{row['prompt_index']}:{row['generation_seed']}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    ordered = sorted(range(len(rows)), key=split_key)
    train_count = int(round(len(rows) * train_fraction))
    train_count = min(max(train_count, 1), len(rows) - 1)
    return sorted(ordered[:train_count]), sorted(ordered[train_count:])


def _flatten_step_texts(rows: list[dict]) -> tuple[list[str], list[tuple[int, int]]]:
    texts: list[str] = []
    spans: list[tuple[int, int]] = []
    for row in rows:
        start = len(texts)
        texts.extend(row["texts"])
        spans.append((start, len(texts)))
    return texts, spans


def _canonical_paths(canonical_states: np.ndarray, spans: list[tuple[int, int]]) -> list[np.ndarray]:
    return [canonical_states[start:end] for start, end in spans]


def _samples_from_paths(
    paths: list[np.ndarray], trajectory_indices: list[int]
) -> tuple[np.ndarray, np.ndarray]:
    states: list[np.ndarray] = []
    dynamics: list[np.ndarray] = []
    for index in trajectory_indices:
        path = np.asarray(paths[index], dtype=np.float64)
        if path.ndim != 2 or len(path) < 2:
            raise ValueError("each trajectory must contain at least two canonical states")
        states.append(path[:-1])
        dynamics.append(np.diff(path, axis=0))
    return np.vstack(states), np.vstack(dynamics)


def _observer_paths(
    observer_spec: dict,
    calibration_texts: list[str],
    trajectory_step_texts: list[str],
    *,
    reference_targets: np.ndarray | None,
    srf_dim: int,
) -> tuple[QuasarFrame, np.ndarray, np.ndarray | None]:
    model = _load_sentence_model(observer_spec)
    calibration = _l2_normalize(_encode_raw(model, calibration_texts))
    trajectory = _l2_normalize(_encode_raw(model, trajectory_step_texts))
    if reference_targets is None:
        frame, targets = QuasarFrame.reference(calibration, dim=srf_dim)
    else:
        frame = QuasarFrame.fit(calibration, reference_targets)
        targets = None
    canonical = frame.canonical_vectors(trajectory)
    del model
    gc.collect()
    return frame, canonical, targets


def _public_report(report: dict[str, object]) -> tuple[dict[str, object], np.ndarray, np.ndarray]:
    public = dict(report)
    train_residual = np.asarray(public.pop("train_residuals"), dtype=np.float64)
    test_residual = np.asarray(public.pop("test_residuals"), dtype=np.float64)
    return public, train_residual, test_residual


def _field_key(spec: FrozenFieldSpec) -> str:
    return f"{spec.family}:seed={spec.seed}:scale={spec.scale:g}"


def _concordance_delta(raw: dict[str, float], residual: dict[str, float]) -> dict[str, float]:
    raw_rmse = max(float(raw["normalized_rmse"]), 1e-12)
    return {
        "mean_row_cosine_gain": float(residual["mean_row_cosine"])
        - float(raw["mean_row_cosine"]),
        "normalized_rmse_ratio": float(residual["normalized_rmse"]) / raw_rmse,
        "pairwise_distance_correlation_gain": float(
            residual["pairwise_distance_correlation"]
        )
        - float(raw["pairwise_distance_correlation"]),
    }


def run(manifest_path: Path, output_path: Path) -> dict:
    manifest, manifest_bytes = _load_json_with_bytes(manifest_path)
    base_path = manifest_path.parent / manifest["base_manifest"]
    base_manifest, base_bytes = _load_json_with_bytes(base_path)

    srf_dim = int(base_manifest["srf_dim"])
    for raw_spec in manifest["fields"]:
        if int(raw_spec["dim"]) != srf_dim:
            raise ValueError("every frozen field dim must equal base-manifest srf_dim")

    cal_paths, _, trajectory_paths = _split_corpus(base_manifest)
    source_commit = base_manifest["source_commit"]
    excerpt_chars = int(base_manifest["corpus"]["excerpt_chars"])
    calibration_texts = _texts(source_commit, cal_paths, excerpt_chars)
    trajectory_prompts = _texts(source_commit, trajectory_paths, excerpt_chars)

    generated_rows = _generate_text_trajectories(base_manifest, trajectory_prompts)
    step_texts, spans = _flatten_step_texts(generated_rows)

    reference_frame, reference_states, canonical_targets = _observer_paths(
        base_manifest["reference_observer"],
        calibration_texts,
        step_texts,
        reference_targets=None,
        srf_dim=srf_dim,
    )
    if canonical_targets is None:
        raise RuntimeError("reference observer did not produce canonical targets")
    transfer_frame, transfer_states, _ = _observer_paths(
        base_manifest["transfer_observer"],
        calibration_texts,
        step_texts,
        reference_targets=canonical_targets,
        srf_dim=srf_dim,
    )

    reference_paths = _canonical_paths(reference_states, spans)
    transfer_paths = _canonical_paths(transfer_states, spans)

    split_cfg = manifest["trajectory_split"]
    train_trajectories, test_trajectories = _trajectory_split(
        generated_rows,
        seed=int(split_cfg["seed"]),
        train_fraction=float(split_cfg["train_fraction"]),
    )

    ref_train_q, ref_train_f = _samples_from_paths(reference_paths, train_trajectories)
    ref_test_q, ref_test_f = _samples_from_paths(reference_paths, test_trajectories)
    transfer_train_q, transfer_train_f = _samples_from_paths(
        transfer_paths, train_trajectories
    )
    transfer_test_q, transfer_test_f = _samples_from_paths(
        transfer_paths, test_trajectories
    )
    if ref_test_f.shape != transfer_test_f.shape:
        raise RuntimeError("paired observers produced incompatible DGCT sample shapes")

    amplitude_cfg = manifest["amplitude"]
    complexity_cfg = manifest["complexity"]
    shared_kwargs = {
        "amplitude_basis": amplitude_cfg["basis"],
        "amplitude_ridge": float(amplitude_cfg["ridge"]),
        "predictor_ridge": float(complexity_cfg["predictor_ridge"]),
        "sample_fractions": tuple(float(x) for x in complexity_cfg["sample_fractions"]),
        "target_relative_mse": float(complexity_cfg["target_relative_mse"]),
    }

    raw_concordance = paired_concordance(ref_test_f, transfer_test_f)
    fields: dict[str, object] = {}
    for raw_spec in manifest["fields"]:
        spec = FrozenFieldSpec(**raw_spec)
        ref_report = compression_report(
            ref_train_q,
            ref_train_f,
            ref_test_q,
            ref_test_f,
            reference_frame.quasars,
            spec,
            **shared_kwargs,
        )
        transfer_report = compression_report(
            transfer_train_q,
            transfer_train_f,
            transfer_test_q,
            transfer_test_f,
            transfer_frame.quasars,
            spec,
            **shared_kwargs,
        )
        ref_public, _, ref_test_residual = _public_report(ref_report)
        transfer_public, _, transfer_test_residual = _public_report(transfer_report)
        residual_concordance = paired_concordance(
            ref_test_residual, transfer_test_residual
        )
        fields[_field_key(spec)] = {
            "field_spec": spec.to_dict(),
            "field_fingerprint": spec.fingerprint,
            "reference_observer": ref_public,
            "transfer_observer": transfer_public,
            "cross_model": {
                "raw_test_dynamics": raw_concordance,
                "test_residuals": residual_concordance,
                "delta": _concordance_delta(raw_concordance, residual_concordance),
            },
            "descriptive_checks": {
                "energy_lower_in_both_observers": bool(
                    float(ref_public["test_energy_ratio"]) < 1.0
                    and float(transfer_public["test_energy_ratio"]) < 1.0
                ),
                "effective_rank_lower_in_both_observers": bool(
                    float(ref_public["test_effective_rank_ratio"]) < 1.0
                    and float(transfer_public["test_effective_rank_ratio"]) < 1.0
                ),
                "cross_model_cosine_improves": bool(
                    residual_concordance["mean_row_cosine"]
                    > raw_concordance["mean_row_cosine"]
                ),
                "cross_model_rmse_improves": bool(
                    residual_concordance["normalized_rmse"]
                    < raw_concordance["normalized_rmse"]
                ),
            },
        }

    trajectory_public = []
    train_set = set(train_trajectories)
    for index, row in enumerate(generated_rows):
        trajectory_public.append(
            {
                "prompt_index": row["prompt_index"],
                "generation_seed": row["generation_seed"],
                "generated_tokens": row["generated_tokens"],
                "continuation_sha256": row["continuation_sha256"],
                "state_count": len(row["texts"]),
                "split": "train" if index in train_set else "test",
            }
        )

    result = {
        "schema_version": 1,
        "experiment": manifest["experiment"],
        "manifest_sha256": _sha256_bytes(manifest_bytes),
        "base_manifest": manifest["base_manifest"],
        "base_manifest_sha256": _sha256_bytes(base_bytes),
        "source_commit": source_commit,
        "models": {
            "reference_observer": base_manifest["reference_observer"],
            "transfer_observer": base_manifest["transfer_observer"],
            "generator": base_manifest["generator"],
        },
        "freeze_order": manifest["freeze_order"],
        "field_fingerprints": {
            _field_key(FrozenFieldSpec(**raw)): FrozenFieldSpec(**raw).fingerprint
            for raw in manifest["fields"]
        },
        "trajectory_split": {
            "seed": int(split_cfg["seed"]),
            "train_fraction": float(split_cfg["train_fraction"]),
            "train_trajectory_count": len(train_trajectories),
            "test_trajectory_count": len(test_trajectories),
            "reference_train_step_count": len(ref_train_q),
            "reference_test_step_count": len(ref_test_q),
        },
        "trajectories": trajectory_public,
        "raw_cross_model_test_dynamics": raw_concordance,
        "fields": fields,
        "claim_boundary": manifest["claim_boundary"],
        "execution_note": (
            "A successful process exit means the preregistered DGCT measurement ran. "
            "It is not a positive scientific result and does not test a Navier-Stokes-inspired field."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("dynamic_gauge_compression_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/dynamic_gauge_compression_v1.json"),
    )
    args = parser.parse_args()
    result = run(args.manifest, args.output)
    print(
        json.dumps(
            {
                key: {
                    "reference_test_energy_ratio": value["reference_observer"]["test_energy_ratio"],
                    "transfer_test_energy_ratio": value["transfer_observer"]["test_energy_ratio"],
                    "cross_model_delta": value["cross_model"]["delta"],
                }
                for key, value in result["fields"].items()
            },
            indent=2,
        )
    )
    print(f"artifact={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
