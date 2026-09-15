"""Benchmark OpenVINO CPU vs GPU (Intel UHD 630) vs PyTorch CPU for text scale embeddings."""

from __future__ import annotations

import json
import time
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from malecns_wifi.text_axis_channels import utf8_byte_axis

MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "intfloat/multilingual-e5-small",
]

SCALES = (8, 32, 128)

TEXTS = [
    "A parte interpôs recurso processual contra a decisão.",
    "O agravo foi encaminhado ao relator para julgamento.",
    "Foi admitido o recurso especial apresentado pela defesa.",
    "O recurso extraordinário teve seguimento negado na origem.",
    "A insurgência recursal questiona a condenação imposta.",
    "O recurso judicial foi protocolado dentro do prazo.",
    "A empresa recebeu recurso financeiro para concluir a obra.",
    "O setor de recursos humanos publicou novo comunicado.",
    "A água é um recurso natural essencial à população.",
    "O município reservou recurso orçamentário para a despesa.",
    "O aplicativo é um recurso tecnológico usado na escola.",
    "O professor adotou um recurso pedagógico visual.",
    "A apelação foi interposta contra a sentença condenatória.",
    "O recurso ordinário será examinado pelo tribunal competente.",
    "Foram opostos embargos de declaração por omissão no julgado.",
    "O agravo discute apenas a decisão interlocutória.",
    "O recurso especial aponta divergência jurisprudencial.",
    "O banco liberou recurso financeiro para capital de giro.",
    "A floresta constitui importante recurso natural da região.",
    "A secretaria ampliou o recurso orçamentário disponível.",
]


def _window_spans(text: str, scale: int) -> list[tuple[int, int]]:
    n = len(text)
    if n == 0:
        return [(0, 1)]
    if n <= scale:
        return [(0, n)]
    stride = max(1, scale // 2)
    starts = list(range(0, n - scale + 1, stride))
    last = n - scale
    if starts[-1] != last:
        starts.append(last)
    return [(start, start + scale) for start in starts]


def collect_windows(scale: int, is_e5: bool) -> list[str]:
    all_windows = []
    for text in TEXTS:
        spans = _window_spans(text, scale)
        windows = [text[a:b] for a, b in spans]
        if is_e5:
            windows = ["passage: " + w for w in windows]
        all_windows.extend(windows)
    return all_windows


def benchmark_model(model_name: str):
    is_e5 = "e5" in model_name.lower()
    print(f"\n==========================================")
    print(f"Benchmarking model: {model_name}")
    print(f"==========================================")

    # 1. Load PyTorch CPU
    t0 = time.perf_counter()
    model_torch_cpu = SentenceTransformer(model_name, device="cpu")
    print(f"PyTorch CPU loaded in {time.perf_counter() - t0:.2f}s")

    # 2. Load OpenVINO CPU
    t0 = time.perf_counter()
    model_ov_cpu = SentenceTransformer(
        model_name,
        backend="openvino",
        model_kwargs={"device": "CPU", "export": True},
    )
    print(f"OpenVINO CPU loaded in {time.perf_counter() - t0:.2f}s")

    # 3. Load OpenVINO GPU (Intel UHD 630)
    t0 = time.perf_counter()
    model_ov_gpu = SentenceTransformer(
        model_name,
        backend="openvino",
        model_kwargs={"device": "GPU", "export": True},
    )
    print(f"OpenVINO GPU loaded in {time.perf_counter() - t0:.2f}s")

    # Warmup all backends
    warmup_text = ["passage: teste de aquecimento" if is_e5 else "teste de aquecimento"] * 16
    _ = model_torch_cpu.encode(warmup_text, batch_size=16)
    _ = model_ov_cpu.encode(warmup_text, batch_size=16)
    _ = model_ov_gpu.encode(warmup_text, batch_size=16)

    results = {}
    for scale in SCALES:
        windows = collect_windows(scale, is_e5)
        num_chunks = len(windows)
        print(f"\n--- Scale {scale} bytes: {num_chunks} total chunks across 20 texts ---")

        # PyTorch CPU
        t0 = time.perf_counter()
        emb_torch = model_torch_cpu.encode(windows, batch_size=32, normalize_embeddings=False)
        t_torch = time.perf_counter() - t0
        rate_torch = num_chunks / t_torch

        # OpenVINO CPU
        t0 = time.perf_counter()
        emb_ov_cpu = model_ov_cpu.encode(windows, batch_size=32, normalize_embeddings=False)
        t_ov_cpu = time.perf_counter() - t0
        rate_ov_cpu = num_chunks / t_ov_cpu

        # OpenVINO GPU (UHD 630)
        t0 = time.perf_counter()
        emb_ov_gpu = model_ov_gpu.encode(windows, batch_size=32, normalize_embeddings=False)
        t_ov_gpu = time.perf_counter() - t0
        rate_ov_gpu = num_chunks / t_ov_gpu

        # Numerical fidelity comparison (cosine and max diff)
        u_torch = emb_torch / np.linalg.norm(emb_torch, axis=1, keepdims=True)
        u_ov_cpu = emb_ov_cpu / np.linalg.norm(emb_ov_cpu, axis=1, keepdims=True)
        u_ov_gpu = emb_ov_gpu / np.linalg.norm(emb_ov_gpu, axis=1, keepdims=True)

        cos_torch_vs_ov_cpu = float(np.mean(np.sum(u_torch * u_ov_cpu, axis=1)))
        cos_torch_vs_ov_gpu = float(np.mean(np.sum(u_torch * u_ov_gpu, axis=1)))
        max_diff_ov_gpu = float(np.max(np.abs(emb_torch - emb_ov_gpu)))

        results[str(scale)] = {
            "num_chunks": num_chunks,
            "torch_cpu_time_s": t_torch,
            "torch_cpu_chunks_per_s": rate_torch,
            "ov_cpu_time_s": t_ov_cpu,
            "ov_cpu_chunks_per_s": rate_ov_cpu,
            "ov_gpu_time_s": t_ov_gpu,
            "ov_gpu_chunks_per_s": rate_ov_gpu,
            "gpu_speedup_vs_torch_cpu": rate_ov_gpu / rate_torch,
            "gpu_speedup_vs_ov_cpu": rate_ov_gpu / rate_ov_cpu,
            "cos_sim_torch_vs_ov_gpu": cos_torch_vs_ov_gpu,
            "max_abs_diff_ov_gpu": max_diff_ov_gpu,
        }

        print(f"PyTorch CPU:   {t_torch*1000:.1f}ms ({rate_torch:.1f} chunks/s)")
        print(f"OpenVINO CPU:  {t_ov_cpu*1000:.1f}ms ({rate_ov_cpu:.1f} chunks/s)")
        print(f"OpenVINO GPU:  {t_ov_gpu*1000:.1f}ms ({rate_ov_gpu:.1f} chunks/s) [Speedup vs Torch: {rate_ov_gpu/rate_torch:.2f}x, vs OV CPU: {rate_ov_gpu/rate_ov_cpu:.2f}x]")
        print(f"Fidelity to Torch CPU: Cosine={cos_torch_vs_ov_gpu:.6f}, MaxDiff={max_diff_ov_gpu:.6e}")

    return results


if __name__ == "__main__":
    summary = {}
    for m in MODELS:
        summary[m] = benchmark_model(m)
    print("\n\nFINAL BENCHMARK SUMMARY:")
    print(json.dumps(summary, indent=2))
