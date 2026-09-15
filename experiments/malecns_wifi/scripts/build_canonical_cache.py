"""Build canonical embedding cache using Intel UHD Graphics 630 via OpenVINO.

Precomputes frozen Transformer perception (MiniLM and E5 at scales 8, 32, 128)
and saves canonical .npz and manifest.json for offline reuse across all seeds/runs.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
import numpy as np
import openvino as ov
from sentence_transformers import SentenceTransformer

import smoke_concept_flavour_gpu as base


MODELS = [
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "intfloat/multilingual-e5-small",
]
SCALES = (8, 32, 128)
CACHE_DIR = Path("artifacts/embedding_cache")


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "embeddings.npz"
    manifest_file = CACHE_DIR / "manifest.json"

    core = ov.Core()
    devices = core.available_devices
    gpu_name = core.get_property("GPU", "FULL_DEVICE_NAME") if "GPU" in devices else "None"
    print(f"OpenVINO devices: {devices}")
    print(f"Target GPU: {gpu_name}")

    train_examples = [base.Example(*row) for row in base.TRAIN_EXAMPLES]
    val_examples = [base.Example(*row) for row in base.VAL_EXAMPLES]
    examples = train_examples + val_examples
    for ex in examples:
        ex.mask = base._mask_for(ex)

    all_texts = [ex.text for ex in examples]
    texts_hash = hashlib.sha256("||".join(all_texts).encode("utf-8")).hexdigest()

    t_start = time.perf_counter()
    npz_dict = {}
    models_meta = []

    for model_index, model_name in enumerate(MODELS):
        print(f"\n[OpenVINO GPU] Loading and encoding with {model_name}...")
        t0 = time.perf_counter()
        
        # Load SentenceTransformer with OpenVINO GPU backend
        model = SentenceTransformer(
            model_name,
            backend="openvino",
            model_kwargs={"device": "GPU", "export": True},
        )
        t_load = time.perf_counter() - t0
        print(f"Model loaded in {t_load:.2f}s")

        # 1. Anchors
        t_enc0 = time.perf_counter()
        literal = base._encode_anchor_set(model, model_name, ("recurso",), kind="query")[0]
        positives = base._encode_anchor_set(model, model_name, base.POSITIVE_ANCHORS, kind="query")
        negatives = base._encode_anchor_set(model, model_name, base.NEGATIVE_ANCHORS, kind="query")
        heldout = base._encode_anchor_set(model, model_name, base.HELDOUT_CONCEPTS, kind="query")

        positive_centroid = base._unit_vec_np(positives.mean(axis=0))
        negative_centroid = base._unit_vec_np(negatives.mean(axis=0))
        discriminative = base._unit_vec_np(positive_centroid - negative_centroid)
        literal = base._unit_vec_np(literal)
        heldout_centroid = base._unit_vec_np(heldout.mean(axis=0))

        # Store in dict
        prefix = f"model_{model_index}_"
        npz_dict[prefix + "literal"] = literal
        npz_dict[prefix + "positive_centroid"] = positive_centroid
        npz_dict[prefix + "negative_centroid"] = negative_centroid
        npz_dict[prefix + "discriminative"] = discriminative
        npz_dict[prefix + "heldout_centroid"] = heldout_centroid

        # 2. Fields
        fields = base._encode_fields(model, model_name, examples, SCALES)
        for ex_idx, f_dict in enumerate(fields):
            for sc in SCALES:
                npz_dict[f"{prefix}ex_{ex_idx}_scale_{sc}"] = f_dict[sc]

        t_encode = time.perf_counter() - t_enc0
        print(f"Encoding finished in {t_encode:.2f}s")

        geometry = {
            "literal_to_positive": base._cosine_np(literal, positive_centroid),
            "literal_to_negative": base._cosine_np(literal, negative_centroid),
            "discriminative_to_positive": base._cosine_np(discriminative, positive_centroid),
            "discriminative_to_negative": base._cosine_np(discriminative, negative_centroid),
            "discriminative_to_heldout": base._cosine_np(discriminative, heldout.mean(axis=0)),
        }
        models_meta.append({
            "model_index": model_index,
            "name": model_name,
            "dim": int(literal.shape[0]),
            "geometry": geometry,
            "load_time_s": t_load,
            "encode_time_s": t_encode,
        })
        del model

    total_time = time.perf_counter() - t_start
    print(f"\nSaving cache to {cache_file}...")
    np.savez_compressed(cache_file, **npz_dict)
    file_bytes = cache_file.stat().st_size

    manifest = {
        "schema": "papers/malecns-embedding-cache-v1",
        "description": "Precomputed frozen Transformer embeddings for MaleCNS semantic channels",
        "perception_backend": "OpenVINO (Intel UHD Graphics 630)",
        "device": gpu_name,
        "models": models_meta,
        "scales": list(SCALES),
        "num_examples": len(examples),
        "texts_sha256": texts_hash,
        "total_time_s": total_time,
        "file_bytes": file_bytes,
        "file_name": cache_file.name,
    }
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest written to {manifest_file} ({file_bytes / (1024*1024):.2f} MB)")
    print(json.dumps({"event": "embedding_cache_built", "summary": manifest}, indent=2))


if __name__ == "__main__":
    main()
