"""Trained Few-NERD NER smoke through the full MaleCNS recurrent graph.

This is infrastructure evidence only. It consumes label-free contextual token
caches, derives MiniLM/E5 × scales 1/2/4/8 channels, applies an independent v3
rank-16 adapter to every channel, broadcasts adapted token evidence onto the
UTF-8 byte axis, runs the established full row-normalised MaleCNS recurrence,
and trains a 67-way positional decoder using official-token cross entropy.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from datasets import load_dataset
from malecns_wifi import load_graph
from malecns_wifi.tagger import row_normalise, select_populations

import smoke_concept_flavour_gpu as base
from fewnerd_ner_core import canonical_byte_axis, exact_entity_prf
from fewnerd_semantic_cache import multiscale_token_fields
from smoke_coupled_flavour_translation_gpu_v3 import ChannelAdapter

SCALES = (1, 2, 4, 8)
N_CLASSES = 67


def _load_cache(path: Path) -> tuple[dict, dict[str, np.ndarray]]:
    manifest_path = path.with_suffix(".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "papers/malecns-fewnerd-contextual-token-cache-v1":
        raise RuntimeError(f"unexpected cache schema: {manifest.get('schema')}")
    arrays: dict[str, np.ndarray] = {}
    with np.load(path, allow_pickle=False) as archive:
        for name in archive.files:
            arrays[name] = archive[name]
    if len(manifest.get("models", [])) != 2:
        raise RuntimeError("first NER smoke requires exactly MiniLM + E5 caches")
    return manifest, arrays


def _load_examples(split: str, limit: int, arrays: dict[str, np.ndarray]) -> list[dict]:
    ds = load_dataset("DFKI-SLT/few-nerd", "supervised", split=split)
    if limit:
        ds = ds.select(range(min(limit, len(ds))))
    cached_ids = [str(x) for x in arrays["sentence_ids"].tolist()]
    dataset_ids = [str(row["id"]) for row in ds]
    if cached_ids != dataset_ids:
        raise RuntimeError(f"cache/dataset id mismatch for {split}")
    examples = []
    for sentence_index, row in enumerate(ds):
        tokens = [str(x) for x in row["tokens"]]
        labels = [int(x) for x in row["fine_ner_tags"]]
        if any(label < 0 or label >= N_CLASSES for label in labels):
            raise RuntimeError("fine label outside 0..66")
        axis = canonical_byte_axis(tokens, labels)
        examples.append({
            "id": str(row["id"]),
            "tokens": tokens,
            "labels": labels,
            "axis": axis,
            "sentence_index": sentence_index,
        })
    return examples


def _cache_sentence_channels(
    arrays: dict[str, np.ndarray], manifest: dict, sentence_index: int, axis
) -> list[np.ndarray]:
    offsets = arrays["token_offsets"]
    start, end = int(offsets[sentence_index]), int(offsets[sentence_index + 1])
    token_count = end - start
    if token_count != len(axis.token_byte_spans):
        raise RuntimeError("cache token count does not match canonical byte axis")

    channels: list[np.ndarray] = []
    byte_len = len(axis.byte_labels)
    for model_index, model_meta in enumerate(manifest["models"]):
        token_vectors = arrays[f"model_{model_index}_tokens"][start:end].astype(np.float32)
        if token_vectors.shape[1] != int(model_meta["hidden_size"]):
            raise RuntimeError("semantic cache hidden size mismatch")
        fields = multiscale_token_fields(token_vectors, SCALES)
        for scale in SCALES:
            byte_field = np.zeros((byte_len, token_vectors.shape[1]), dtype=np.float32)
            for token_index, (a, b) in enumerate(axis.token_byte_spans):
                byte_field[a:b] = fields[scale][token_index]
            channels.append(byte_field)
    return channels


class FewNERDWholeBrain(torch.nn.Module):
    def __init__(self, channel_dims: list[int], readout_width: int, *, device):
        super().__init__()
        self.adapters = torch.nn.ModuleList([
            ChannelAdapter(dim, rank=16, residual_scale=0.1, device=device)
            for dim in channel_dims
        ])
        self.head = torch.nn.Linear(readout_width, N_CLASSES, device=device)

    def adapt(self, fields: list[torch.Tensor]) -> torch.Tensor:
        if len(fields) != len(self.adapters):
            raise RuntimeError("field/adapter count mismatch")
        return torch.cat(
            [adapter(field) for adapter, field in zip(self.adapters, fields, strict=True)],
            dim=1,
        )


def _reservoir_byte_logits(
    model: FewNERDWholeBrain,
    fields: list[torch.Tensor],
    *,
    operator,
    input_weights,
    input_indices,
    whole_brain,
    readout_projection,
    gain: float = 4.0,
    leak: float = 0.4,
    target_rms: float = 0.05,
) -> tuple[torch.Tensor, torch.Tensor]:
    features = model.adapt(fields)
    projected = input_weights @ features.T
    rms = torch.sqrt(torch.mean(projected.square())).clamp_min(1e-12)
    projected = projected * (target_rms / rms)

    state = torch.zeros(int(operator.shape[0]), dtype=torch.float32, device=features.device)
    rows = []
    for step in range(features.shape[0]):
        drive = torch.zeros_like(state).index_add(0, input_indices, projected[:, step])
        pre = torch.sparse.mm(operator, state[:, None]).squeeze(1) * gain + drive
        state = (1.0 - leak) * state + leak * torch.tanh(pre)
        probed = state[whole_brain]
        rows.append(torch.sparse.mm(readout_projection, probed[:, None]).squeeze(1))
    readout = torch.stack(rows, dim=0)
    return model.head(readout), torch.sqrt(torch.mean(projected.square()))


def _token_logits(byte_logits: torch.Tensor, token_byte_spans) -> torch.Tensor:
    return torch.stack([byte_logits[a:b].mean(dim=0) for a, b in token_byte_spans], dim=0)


def _predict_examples(
    model,
    examples,
    arrays,
    manifest,
    *,
    operator,
    input_weights,
    input_indices,
    whole_brain,
    readout_projection,
    device,
) -> tuple[list[list[int]], list[list[int]]]:
    gold, pred = [], []
    model.eval()
    with torch.no_grad():
        for example in examples:
            fields_np = _cache_sentence_channels(
                arrays, manifest, example["sentence_index"], example["axis"]
            )
            fields = [torch.as_tensor(x, dtype=torch.float32, device=device) for x in fields_np]
            byte_logits, _ = _reservoir_byte_logits(
                model, fields, operator=operator, input_weights=input_weights,
                input_indices=input_indices, whole_brain=whole_brain,
                readout_projection=readout_projection,
            )
            token_logits = _token_logits(byte_logits, example["axis"].token_byte_spans)
            pred.append(token_logits.argmax(dim=1).cpu().tolist())
            gold.append(list(example["labels"]))
    model.train()
    return gold, pred


def _adapter_report(model: FewNERDWholeBrain) -> list[dict]:
    rows = []
    index = 0
    for encoder in ("MiniLM", "E5"):
        for scale in SCALES:
            adapter = model.adapters[index]
            rows.append({
                "encoder": encoder,
                "scale_tokens": scale,
                "up_norm": float(adapter.up.weight.detach().norm().cpu()),
                "down_norm": float(adapter.down.weight.detach().norm().cpu()),
            })
            index += 1
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graph", type=Path, required=True)
    p.add_argument("--train-cache", type=Path, required=True)
    p.add_argument("--dev-cache", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--train-limit", type=int, default=8)
    p.add_argument("--dev-limit", type=int, default=8)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--lr", type=float, default=5e-4)
    p.add_argument("--readout-width", type=int, default=128)
    p.add_argument("--seed", type=int, default=20260915)
    args = p.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required for the full-whole-brain NER smoke")
    device = torch.device("cuda")
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()

    train_manifest, train_arrays = _load_cache(args.train_cache)
    dev_manifest, dev_arrays = _load_cache(args.dev_cache)
    train_examples = _load_examples("train", args.train_limit, train_arrays)
    dev_examples = _load_examples("validation", args.dev_limit, dev_arrays)

    matrix = row_normalise(load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    operator = base._csr_to_torch(matrix, device=device)
    neurons = int(matrix.shape[0])
    whole_brain = torch.arange(neurons, dtype=torch.int64, device=device)
    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=device)

    channel_dims = []
    for meta in train_manifest["models"]:
        channel_dims.extend([int(meta["hidden_size"])] * len(SCALES))
    if channel_dims != [384] * 8:
        raise RuntimeError(f"unexpected first-smoke channel dims: {channel_dims}")
    combined_dim = sum(channel_dims)
    input_weights = torch.as_tensor(
        rng.normal(size=(populations.input_indices.size, combined_dim)).astype(np.float32)
        / np.float32(np.sqrt(combined_dim)),
        dtype=torch.float32,
        device=device,
    )
    readout_projection = base._fixed_sparse_projection(
        args.readout_width, neurons, seed=args.seed + 17, device=device
    )

    model = FewNERDWholeBrain(channel_dims, args.readout_width, device=device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    curves = []

    for epoch in range(args.epochs):
        epoch_started = time.perf_counter()
        losses, drive_rms = [], []
        for example in train_examples:
            optimizer.zero_grad(set_to_none=True)
            fields_np = _cache_sentence_channels(
                train_arrays, train_manifest, example["sentence_index"], example["axis"]
            )
            fields = [torch.as_tensor(x, dtype=torch.float32, device=device) for x in fields_np]
            byte_logits, drive = _reservoir_byte_logits(
                model, fields, operator=operator, input_weights=input_weights,
                input_indices=input_indices, whole_brain=whole_brain,
                readout_projection=readout_projection,
            )
            logits = _token_logits(byte_logits, example["axis"].token_byte_spans)
            target = torch.as_tensor(example["labels"], dtype=torch.long, device=device)
            loss = torch.nn.functional.cross_entropy(logits, target)
            loss.backward()
            grad_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
            drive_rms.append(float(drive.detach().cpu()))

        gold, pred = _predict_examples(
            model, dev_examples, dev_arrays, dev_manifest,
            operator=operator, input_weights=input_weights, input_indices=input_indices,
            whole_brain=whole_brain, readout_projection=readout_projection, device=device,
        )
        score = exact_entity_prf(gold, pred)
        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "drive_rms": float(np.mean(drive_rms)),
            "grad_norm_last": grad_norm,
            "dev_exact_entity": score,
            "seconds": time.perf_counter() - epoch_started,
            "adapters": _adapter_report(model),
        }
        curves.append(row)
        print(json.dumps({"event": "fewnerd_ner_epoch", **row}), flush=True)

    payload = {
        "schema": "papers/malecns-fewnerd-wholebrain-ner-smoke-v1",
        "claim_status": "trained infrastructure smoke on train/dev only; not benchmark evidence",
        "preregistration": [
            "preregistered-fewnerd-ner-2026-09-15.md",
            "preregistered-fewnerd-ner-byte-amendment-2026-09-15.md",
            "preregistered-fewnerd-ner-contextual-token-cache-amendment-2026-09-15.md",
            "preregistered-fewnerd-ner-decoder-amendment-2026-09-15.md",
        ],
        "dataset": "DFKI-SLT/few-nerd",
        "config": "supervised",
        "train_examples": len(train_examples),
        "dev_examples": len(dev_examples),
        "test_loaded": False,
        "tagging_scheme": "IO",
        "fine_entity_types": 66,
        "decoder_classes": N_CLASSES,
        "semantic_channels": [
            f"{encoder}-scale-{scale}"
            for encoder in ("MiniLM", "E5") for scale in SCALES
        ],
        "adapter": "independent rank-16 v3 residual per semantic channel",
        "byte_to_token": "mean real-valued byte logits over official token bytes, then argmax",
        "loss": "unweighted 67-way token cross entropy after byte-logit aggregation",
        "neurons": neurons,
        "edges": int(matrix.nnz),
        "sensory_neurons": int(populations.input_indices.size),
        "wholebrain_projection_width": args.readout_width,
        "gain": 4.0,
        "leak": 0.4,
        "target_rms": 0.05,
        "train_cache_fingerprint": train_manifest["fingerprint"],
        "dev_cache_fingerprint": dev_manifest["fingerprint"],
        "epochs": args.epochs,
        "curve": curves,
        "device": torch.cuda.get_device_name(0),
        "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()),
        "wall_seconds": time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "fewnerd_wholebrain_ner_smoke_complete", "summary": payload}), flush=True)


if __name__ == "__main__":
    main()
