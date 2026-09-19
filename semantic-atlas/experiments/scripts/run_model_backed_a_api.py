from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

from semantic_atlas.atlas import SemanticAtlas
from semantic_atlas.embedding_cache import write_embedding_cache
from semantic_atlas.frame import QuasarFrame

# This variant reuses v1 helpers so corpus derivation, split rules and metrics
# cannot drift between local and API observer runs.
_SCRIPT = Path(__file__).resolve().parent / "run_model_backed_a.py"
_SPEC = importlib.util.spec_from_file_location("run_model_backed_a_v1", _SCRIPT)
_v1 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_v1)

_RETRYABLE = {429, 500, 502, 503, 504}


def _http_json(url: str, payload: dict, headers: dict[str, str], max_retries: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(max_retries):
        request = urllib.request.Request(
            url,
            data=body,
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            if exc.code in _RETRYABLE and attempt < max_retries - 1:
                time.sleep(min(2**attempt * 2, 30))
                last_error = RuntimeError(f"HTTP {exc.code} from {url}: {detail}")
                continue
            raise RuntimeError(f"HTTP {exc.code} from {url}: {detail}") from exc
        except urllib.error.URLError as exc:
            if attempt < max_retries - 1:
                time.sleep(min(2**attempt * 2, 30))
                last_error = exc
                continue
            raise RuntimeError(f"network error calling {url}: {exc}") from exc
    raise RuntimeError(f"retries exhausted calling {url}: {last_error}")


def _credential(env_name: str) -> str:
    value = os.getenv(env_name, "").strip()
    if not value:
        raise RuntimeError(f"missing credential: set the {env_name} environment variable")
    return value


def _key_pool(env_name: str) -> list[str]:
    keys = [part.strip() for part in os.getenv(env_name, "").replace(";", ",").split(",")]
    keys = [key.strip().strip('"').strip("'") for key in keys if key.strip()]
    if not keys:
        raise RuntimeError(f"missing credential: set the {env_name} environment variable")
    return keys


def _gemini_encode(texts: list[str], spec: dict, api_cfg: dict, usage: dict) -> np.ndarray:
    keys = _key_pool(spec["credential_env"])
    vectors: list[list[float]] = []
    batch_size = int(api_cfg.get("gemini_batch_size", 16))
    interval = float(api_cfg.get("gemini_request_interval_seconds", 0))
    attempts = max(int(api_cfg.get("max_retries", 5)), 1) * len(keys)
    url = f"{spec['endpoint']}/models/{spec['model']}:batchEmbedContents"
    key_index = 0
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        payload = {
            "requests": [
                {
                    "model": f"models/{spec['model']}",
                    "content": {"parts": [{"text": text}]},
                }
                for text in batch
            ]
        }
        response = None
        for _ in range(attempts):
            key = keys[key_index % len(keys)]
            try:
                response = _http_json(url, payload, {"x-goog-api-key": key}, 1)
                break
            except RuntimeError as exc:
                if "HTTP 429" not in str(exc):
                    raise
                key_index += 1
                rotated = key_index // len(keys) + 1
                time.sleep(min(20 * rotated, 90))
        if response is None:
            raise RuntimeError("gemini quota exhausted across the whole credential pool")
        embeddings = response.get("embeddings")
        if embeddings is None or len(embeddings) != len(batch):
            raise RuntimeError("gemini batchEmbedContents returned a malformed response")
        vectors.extend(item["values"] for item in embeddings)
        usage["gemini_requests"] = usage.get("gemini_requests", 0) + 1
        if interval:
            time.sleep(interval)
    return np.asarray(vectors, dtype=np.float64)


def _jina_encode(texts: list[str], spec: dict, api_cfg: dict, usage: dict) -> np.ndarray:
    key = _credential(spec["credential_env"])
    collected: list[list[float]] = []
    batch_size = int(api_cfg.get("jina_batch_size", 32))
    url = f"{spec['endpoint']}/v1/embeddings"
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        payload: dict = {
            "model": spec["model"],
            "task": spec.get("task", "retrieval.passage"),
            "input": batch,
        }
        if spec.get("dimensions"):
            payload["dimensions"] = int(spec["dimensions"])
        response = _http_json(
            url,
            payload,
            {"Authorization": f"Bearer {key}"},
            int(api_cfg.get("max_retries", 5)),
        )
        rows = sorted(response.get("data", []), key=lambda item: item.get("index", 0))
        if len(rows) != len(batch):
            raise RuntimeError("jina embeddings returned a malformed response")
        collected.extend(item["embedding"] for item in rows)
        usage["jina_requests"] = usage.get("jina_requests", 0) + 1
    return np.asarray(collected, dtype=np.float64)


_PROVIDERS = {
    "gemini": _gemini_encode,
    "jina": _jina_encode,
}


def _encode_with(spec: dict, api_cfg: dict, usage: dict):
    provider = spec["provider"]
    if provider not in _PROVIDERS:
        raise RuntimeError(f"unsupported observer provider: {provider}")
    encoder = _PROVIDERS[provider]

    def encode(texts: list[str]) -> np.ndarray:
        return encoder(texts, spec, api_cfg, usage)

    return encode


def _load_local_generator(spec: dict):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(spec["model"], revision=spec["revision"])
    model = AutoModelForCausalLM.from_pretrained(
        spec["model"], revision=spec["revision"], torch_dtype="auto", device_map="auto"
    )
    model.eval()
    return torch, tokenizer, model


def _generate_paths_api(manifest: dict, prompts: list[str], encode_reference, frame):
    cfg = manifest["trajectory"]
    torch, tokenizer, model = _load_local_generator(manifest["generator"])

    rows = []
    for prompt_index, source in enumerate(prompts):
        prompt = source + "\n\nContinue coherently:"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        for seed in cfg["seeds"]:
            torch.manual_seed(int(seed))
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(int(seed))
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=cfg["max_new_tokens"],
                    do_sample=cfg["do_sample"],
                    temperature=cfg["temperature"],
                )
            new_ids = generated[0, inputs["input_ids"].shape[1] :]
            cumulative = []
            for end in range(cfg["chunk_tokens"], len(new_ids) + cfg["chunk_tokens"], cfg["chunk_tokens"]):
                chunk_ids = new_ids[: min(end, len(new_ids))]
                continuation = tokenizer.decode(chunk_ids, skip_special_tokens=True)
                cumulative.append(prompt + continuation)
                if end >= len(new_ids):
                    break
            path = frame.coordinates(encode_reference(cumulative))
            rows.append(
                {
                    "prompt_index": prompt_index,
                    "seed": int(seed),
                    "generated_tokens": int(len(new_ids)),
                    "continuation": tokenizer.decode(new_ids, skip_special_tokens=True),
                    "path": np.asarray(path, dtype=np.float64).tolist(),
                }
            )
    return rows


def _observer_cache_identity(spec: dict) -> dict:
    # Keep scientific call identity, but never credential names/values or headers.
    return {key: value for key, value in spec.items() if key != "credential_env"}


def run(manifest_path: Path, output: Path, embedding_cache_dir: Path | None = None) -> dict:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    started = _dt.datetime.now(_dt.timezone.utc).isoformat()

    corpus = manifest["corpus"]
    cal_paths, held_paths, trajectory_paths = _v1._split_corpus(manifest)
    commit = manifest["source_commit"]
    limit = corpus["excerpt_chars"]
    cal_texts = [_v1._git_text(commit, path, limit) for path in cal_paths]
    held_texts = [_v1._git_text(commit, path, limit) for path in held_paths]
    trajectory_texts = [_v1._git_text(commit, path, limit) for path in trajectory_paths]

    api_cfg = manifest.get("api", {})
    usage: dict = {}
    encode_reference = _encode_with(manifest["reference_observer"], api_cfg, usage)
    encode_transfer = _encode_with(manifest["transfer_observer"], api_cfg, usage)

    # These four arrays are provider observations. Persist them before using them
    # for alignment so a later method comparison never has to re-query an API.
    ref_cal = encode_reference(cal_texts)
    transfer_cal = encode_transfer(cal_texts)
    ref_held = encode_reference(held_texts)
    transfer_held = encode_transfer(held_texts)

    embedding_caches: dict[str, dict[str, str]] = {}
    if embedding_cache_dir is not None:
        paths_by_split = {"calibration": cal_paths, "heldout": held_paths}
        texts_by_split = {"calibration": cal_texts, "heldout": held_texts}
        ref_cache = write_embedding_cache(
            embedding_cache_dir / "reference_observer",
            observer=_observer_cache_identity(manifest["reference_observer"]),
            source_commit=commit,
            paths_by_split=paths_by_split,
            texts_by_split=texts_by_split,
            raw_by_split={"calibration": ref_cal, "heldout": ref_held},
            normalized_by_split={
                "calibration": _v1._l2_normalize(ref_cal),
                "heldout": _v1._l2_normalize(ref_held),
            },
        )
        transfer_cache = write_embedding_cache(
            embedding_cache_dir / "transfer_observer",
            observer=_observer_cache_identity(manifest["transfer_observer"]),
            source_commit=commit,
            paths_by_split=paths_by_split,
            texts_by_split=texts_by_split,
            raw_by_split={"calibration": transfer_cal, "heldout": transfer_held},
            normalized_by_split={
                "calibration": _v1._l2_normalize(transfer_cal),
                "heldout": _v1._l2_normalize(transfer_held),
            },
        )
        embedding_caches = {
            "reference_observer": _v1._cache_ref_dict(ref_cache),
            "transfer_observer": _v1._cache_ref_dict(transfer_cache),
        }

    frame, canonical_targets = QuasarFrame.reference(ref_cal, dim=manifest["srf_dim"])
    transfer_frame = QuasarFrame.fit(transfer_cal, canonical_targets)
    ref_canonical = frame.canonical_vectors(ref_held)
    transfer_canonical = transfer_frame.canonical_vectors(transfer_held)
    paired_rmse = float(np.sqrt(np.mean((ref_canonical - transfer_canonical) ** 2)))
    paired_cosine = float(np.mean(_v1._cosine_rows(ref_canonical, transfer_canonical)))
    ref_quasar = np.argmax(frame.coordinates(ref_held), axis=1)
    transfer_quasar = np.argmax(transfer_frame.coordinates(transfer_held), axis=1)
    quasar_agreement = float(np.mean(ref_quasar == transfer_quasar))

    rng = np.random.default_rng(991)
    shuffled = transfer_cal[rng.permutation(len(transfer_cal))]
    shuffled_frame = QuasarFrame.fit(shuffled, canonical_targets)
    shuffled_canonical = shuffled_frame.canonical_vectors(transfer_held)
    shuffled_rmse = float(np.sqrt(np.mean((ref_canonical - shuffled_canonical) ** 2)))

    calibration_coordinates = frame.coordinates(ref_cal)
    centers = calibration_coordinates[: manifest["atlas"]["center_count"]]
    atlas = SemanticAtlas(centers)
    trajectories = _generate_paths_api(manifest, trajectory_texts, encode_reference, frame)
    for trajectory in trajectories:
        atlas.observe_path(np.asarray(trajectory["path"], dtype=np.float64))
    occupied = sum(cell.count > 0 for cell in atlas.cells)

    result = {
        "schema_version": 2,
        "experiment": manifest["experiment"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "source_commit": commit,
        "collected_at_utc": started,
        "models": {
            "reference_observer": manifest["reference_observer"],
            "transfer_observer": manifest["transfer_observer"],
            "generator": manifest["generator"],
        },
        "api_usage": usage,
        "corpus_paths": {
            "calibration": cal_paths,
            "heldout": held_paths,
            "trajectory": trajectory_paths,
        },
        "embedding_caches": embedding_caches,
        "metrics": {
            "heldout_coordinate_rmse": paired_rmse,
            "heldout_canonical_cosine": paired_cosine,
            "nearest_quasar_agreement": quasar_agreement,
            "shuffled_coordinate_rmse": shuffled_rmse,
            "shuffled_worse_than_paired": bool(shuffled_rmse > paired_rmse),
            "atlas_coverage": occupied / len(atlas.cells),
            "transition_count": len(atlas.transitions),
        },
        "atlas": {
            "centers": atlas.centers.tolist(),
            "cells": [
                {"cell_id": cell.cell_id, "count": cell.count, "mean_radius": cell.mean_radius}
                for cell in atlas.cells
            ],
            "transitions": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "count": edge.count,
                    "mean_distance": edge.mean_distance,
                }
                for edge in atlas.transitions.values()
            ],
        },
        "trajectories": trajectories,
        "claim_boundary": (
            "This artifact is an API-hosted replication of Experiment A. Observers are "
            "provider-served models identified by name, not weight hashes. Like v1 it "
            "tests Experiment A only and cannot support MPC/steering claims."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("model_backed_a_v2_api.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/model_backed_a_v2_api.json"))
    parser.add_argument(
        "--embedding-cache-dir",
        type=Path,
        default=Path("artifacts/embedding_cache_v2_api"),
        help="Persist API observer outputs before alignment or metric computation.",
    )
    args = parser.parse_args()
    result = run(args.manifest, args.output, args.embedding_cache_dir)
    print(json.dumps(result["metrics"], indent=2))
    print(f"artifact={args.output}")
    for observer, ref in result["embedding_caches"].items():
        print(f"embedding_cache[{observer}]={ref['data_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
