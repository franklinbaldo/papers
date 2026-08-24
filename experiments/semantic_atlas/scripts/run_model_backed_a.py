from __future__ import annotations

import argparse
import functools
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from semantic_atlas.atlas import SemanticAtlas
from semantic_atlas.frame import QuasarFrame


@functools.lru_cache(maxsize=1)
def _repo_root() -> str:
    here = Path(__file__).resolve().parent
    output = subprocess.check_output(
        ["git", "-C", str(here), "rev-parse", "--show-toplevel"], text=True
    )
    return output.strip()


def _git_paths(commit: str) -> list[str]:
    # The corpus domain is every markdown file in the tree of source_commit.
    # ls-tree is CWD-sensitive, so pin git to the repository root: running from
    # experiments/semantic_atlas would otherwise collapse the corpus to the 7
    # markdown files inside that subdirectory instead of the whole repo.
    root = _repo_root()
    output = subprocess.check_output(
        ["git", "-C", root, "ls-tree", "-r", "--name-only", commit], text=True
    )
    paths = [line.strip() for line in output.splitlines() if line.strip().endswith(".md")]
    return sorted(paths, key=lambda path: hashlib.sha256(path.encode()).hexdigest())


def _git_text(commit: str, path: str, limit: int) -> str:
    raw = subprocess.check_output(["git", "-C", _repo_root(), "show", f"{commit}:{path}"])
    text = raw.decode("utf-8", errors="replace").strip()
    return text[:limit]


def _split_corpus(manifest: dict) -> tuple[list[str], list[str], list[str]]:
    corpus = manifest["corpus"]
    total = corpus["calibration_count"] + corpus["heldout_count"] + corpus["trajectory_count"]
    paths = _git_paths(manifest["source_commit"])
    if len(paths) < total:
        raise RuntimeError(f"need {total} markdown files at source_commit, found {len(paths)}")
    chosen = paths[:total]
    a = corpus["calibration_count"]
    b = a + corpus["heldout_count"]
    return chosen[:a], chosen[a:b], chosen[b:]


def _texts(commit: str, paths: list[str], limit: int) -> list[str]:
    return [_git_text(commit, path, limit) for path in paths]


def _cosine_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.sum(a * b, axis=1) / np.maximum(denom, 1e-12)


def _load_sentence_model(spec: dict):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(spec["model"], revision=spec["revision"])


def _encode(model, texts: list[str]) -> np.ndarray:
    return np.asarray(
        model.encode(texts, convert_to_numpy=True, normalize_embeddings=True),
        dtype=np.float64,
    )


def _generate_paths(manifest: dict, prompts: list[str], reference_model, frame: QuasarFrame):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    spec = manifest["generator"]
    cfg = manifest["trajectory"]
    tokenizer = AutoTokenizer.from_pretrained(spec["model"], revision=spec["revision"])
    model = AutoModelForCausalLM.from_pretrained(
        spec["model"], revision=spec["revision"], torch_dtype="auto", device_map="auto"
    )
    model.eval()

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
            embeddings = _encode(reference_model, cumulative)
            path = frame.coordinates(embeddings)
            rows.append(
                {
                    "prompt_index": prompt_index,
                    "seed": int(seed),
                    "generated_tokens": int(len(new_ids)),
                    "continuation": tokenizer.decode(new_ids, skip_special_tokens=True),
                    "path": path.tolist(),
                }
            )
    return rows


def run(manifest_path: Path, output: Path) -> dict:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    corpus = manifest["corpus"]
    cal_paths, held_paths, trajectory_paths = _split_corpus(manifest)
    commit = manifest["source_commit"]
    limit = corpus["excerpt_chars"]
    cal_texts = _texts(commit, cal_paths, limit)
    held_texts = _texts(commit, held_paths, limit)
    trajectory_texts = _texts(commit, trajectory_paths, limit)

    reference_model = _load_sentence_model(manifest["reference_observer"])
    transfer_model = _load_sentence_model(manifest["transfer_observer"])
    ref_cal = _encode(reference_model, cal_texts)
    transfer_cal = _encode(transfer_model, cal_texts)
    ref_held = _encode(reference_model, held_texts)
    transfer_held = _encode(transfer_model, held_texts)

    frame, canonical_targets = QuasarFrame.reference(ref_cal, dim=manifest["srf_dim"])
    transfer_frame = QuasarFrame.fit(transfer_cal, canonical_targets)
    ref_canonical = frame.canonical_vectors(ref_held)
    transfer_canonical = transfer_frame.canonical_vectors(transfer_held)
    paired_rmse = float(np.sqrt(np.mean((ref_canonical - transfer_canonical) ** 2)))
    paired_cosine = float(np.mean(_cosine_rows(ref_canonical, transfer_canonical)))
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
    trajectories = _generate_paths(manifest, trajectory_texts, reference_model, frame)
    for trajectory in trajectories:
        atlas.observe_path(np.asarray(trajectory["path"], dtype=np.float64))
    occupied = sum(cell.count > 0 for cell in atlas.cells)

    result = {
        "schema_version": 1,
        "experiment": manifest["experiment"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "source_commit": commit,
        "models": {
            "reference_observer": manifest["reference_observer"],
            "transfer_observer": manifest["transfer_observer"],
            "generator": manifest["generator"],
        },
        "corpus_paths": {
            "calibration": cal_paths,
            "heldout": held_paths,
            "trajectory": trajectory_paths,
        },
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
            "This artifact tests Experiment A only. It cannot support MPC/steering claims. "
            "A green execution is not a positive scientific result."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("model_backed_a_v1.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/model_backed_a_v1.json"))
    args = parser.parse_args()
    result = run(args.manifest, args.output)
    print(json.dumps(result["metrics"], indent=2))
    print(f"artifact={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
