from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import sys
import time
from pathlib import Path


def _default_output() -> Path:
    if Path("/kaggle/working").is_dir():
        return Path("/kaggle/working/semantic_atlas_gpu_smoke.json")
    if Path("/content").is_dir():
        return Path("/content/semantic_atlas_gpu_smoke.json")
    return Path("semantic_atlas_gpu_smoke.json")


def _bytes_to_gib(value: int) -> float:
    return round(value / (1024**3), 3)


def _sync(torch) -> None:
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantic Atlas free-GPU smoke run")
    parser.add_argument("--output", type=Path, default=_default_output())
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--generator", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--generator-revision", default=os.environ.get("QWEN_GENERATOR_REVISION", "main"))
    parser.add_argument("--embedder", default="Qwen/Qwen3-Embedding-0.6B")
    parser.add_argument("--embedder-revision", default=os.environ.get("QWEN_EMBEDDER_REVISION", "main"))
    args = parser.parse_args()

    try:
        import torch
        import transformers
        from sentence_transformers import SentenceTransformer
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        print(
            "Missing model dependencies. Install: torch transformers sentence-transformers accelerate",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    if not torch.cuda.is_available():
        raise SystemExit("CUDA GPU is required for this smoke run")

    device = torch.device("cuda:0")
    properties = torch.cuda.get_device_properties(device)
    result: dict[str, object] = {
        "schema_version": 1,
        "provider_hints": {
            "colab": bool(os.environ.get("COLAB_RELEASE_TAG") or Path("/content").is_dir()),
            "kaggle": bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE") or Path("/kaggle/working").is_dir()),
        },
        "system": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "cuda_runtime": torch.version.cuda,
            "gpu": properties.name,
            "gpu_total_gib": _bytes_to_gib(properties.total_memory),
            "bf16_supported": bool(torch.cuda.is_bf16_supported()),
        },
        "generator": {"model": args.generator, "requested_revision": args.generator_revision},
        "embedder": {"model": args.embedder, "requested_revision": args.embedder_revision},
    }

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    prompt = (
        "Explain in two concise sentences why a useful map can be smaller than the territory "
        "it represents."
    )

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)

    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(args.generator, revision=args.generator_revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.generator,
        revision=args.generator_revision,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    ).to(device)
    model.eval()
    _sync(torch)
    result["generator"]["load_seconds"] = round(time.perf_counter() - t0, 3)
    result["generator"]["resolved_revision"] = getattr(model.config, "_commit_hash", None)
    result["generator"]["dtype"] = str(dtype).replace("torch.", "")
    result["generator"]["allocated_after_load_gib"] = _bytes_to_gib(torch.cuda.memory_allocated(device))

    encoded = tokenizer(prompt, return_tensors="pt").to(device)
    _sync(torch)
    t0 = time.perf_counter()
    with torch.inference_mode():
        output_ids = model.generate(
            **encoded,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            use_cache=True,
        )
    _sync(torch)
    generation_seconds = time.perf_counter() - t0
    continuation_ids = output_ids[0, encoded["input_ids"].shape[1] :]
    continuation = tokenizer.decode(continuation_ids, skip_special_tokens=True)
    result["generator"].update(
        {
            "prompt_tokens": int(encoded["input_ids"].shape[1]),
            "generated_tokens": int(continuation_ids.shape[0]),
            "generation_seconds": round(generation_seconds, 3),
            "generated_tokens_per_second": round(
                continuation_ids.shape[0] / max(generation_seconds, 1e-9), 3
            ),
            "continuation": continuation,
            "allocated_after_generate_gib": _bytes_to_gib(torch.cuda.memory_allocated(device)),
            "peak_gib": _bytes_to_gib(torch.cuda.max_memory_allocated(device)),
        }
    )

    _sync(torch)
    t0 = time.perf_counter()
    embedder = SentenceTransformer(
        args.embedder,
        revision=args.embedder_revision,
        device="cuda",
        model_kwargs={"torch_dtype": dtype},
    )
    _sync(torch)
    result["embedder"]["load_seconds"] = round(time.perf_counter() - t0, 3)
    first_module = embedder._first_module()
    auto_model = getattr(first_module, "auto_model", None)
    config = getattr(auto_model, "config", None)
    result["embedder"]["resolved_revision"] = getattr(config, "_commit_hash", None)
    result["embedder"]["allocated_with_both_models_gib"] = _bytes_to_gib(
        torch.cuda.memory_allocated(device)
    )

    _sync(torch)
    t0 = time.perf_counter()
    vectors = embedder.encode(
        [prompt, continuation],
        convert_to_numpy=True,
        normalize_embeddings=True,
        truncate_dim=64,
    )
    _sync(torch)
    embedding_seconds = time.perf_counter() - t0
    cosine = float((vectors[0] * vectors[1]).sum())
    result["embedder"].update(
        {
            "batch_size": 2,
            "embedding_dim": int(vectors.shape[1]),
            "embedding_seconds": round(embedding_seconds, 3),
            "prompt_continuation_cosine": round(cosine, 6),
            "allocated_after_embed_gib": _bytes_to_gib(torch.cuda.memory_allocated(device)),
            "combined_peak_gib": _bytes_to_gib(torch.cuda.max_memory_allocated(device)),
        }
    )

    del embedder, model, tokenizer, encoded, output_ids
    gc.collect()
    torch.cuda.empty_cache()
    result["system"]["allocated_after_cleanup_gib"] = _bytes_to_gib(
        torch.cuda.memory_allocated(device)
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nartifact={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
