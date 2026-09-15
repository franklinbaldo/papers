"""Exploratory exact-word curriculum smoke on byte-aligned multiscale channels.

This is deliberately a small curriculum task, not Stage A/B evidence.  The target
word is rewarded byte-by-byte.  Two frozen embedding models create parallel
multiscale vector fields over the same UTF-8 byte axis.  Relations (ratio,
difference, product) are computed only within one encoder space, stay vector-
valued, and are concatenated only after independent row normalisation.

The script reports cheap direct probes for each encoder and the combined channels,
then trains identical tag-only and MaleCNS-assisted standalone taggers from the
same initialization.  The assisted arm uses the complete frozen MaleCNS graph and
a fixed whole-brain projection; food/taste exists only during training.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from malecns_wifi import load_graph
from malecns_wifi.encoder_gate import average_precision, best_f1_threshold
from malecns_wifi.fly_assisted import FlyAssistSpec, make_model, score_standalone, training_loss
from malecns_wifi.multitag import ridge_multioutput
from malecns_wifi.tagger import row_normalise, select_populations
from malecns_wifi.text_axis_channels import byte_aligned_scale, utf8_byte_axis, vector_relations


def _torch():
    import torch
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required")
    return torch


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _first_word_span(text: str, target: str) -> tuple[int, int] | None:
    match = re.search(rf"(?i)(?<!\w){re.escape(target)}(?!\w)", text)
    return None if match is None else (match.start(), match.end())


def _crop(record: dict, target: str, width: int) -> dict | None:
    text = record["text"]
    span = _first_word_span(text, target)
    if span is None:
        return None
    centre = (span[0] + span[1]) // 2
    start = max(0, centre - width // 2)
    end = min(len(text), start + width)
    start = max(0, end - width)
    snippet = text[start:end]
    local = _first_word_span(snippet, target)
    if local is None:
        return None
    return {
        "doc_id": record.get("info", {}).get("doc_id", "?"),
        "text": snippet,
        "source_char_start": start,
    }


def _choose(records: list[dict], target: str, count: int, width: int) -> list[dict]:
    rows = []
    for record in records:
        item = _crop(record, target, width)
        if item is not None:
            rows.append(item)
        if len(rows) >= count:
            break
    if len(rows) < count:
        raise SystemExit(f"target {target!r}: need {count} documents, found {len(rows)}")
    return rows


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


def _byte_spans(text: str, char_spans: list[tuple[int, int]]) -> np.ndarray:
    axis = utf8_byte_axis(text)
    return np.asarray(
        [(int(axis.char_to_byte[a]), int(axis.char_to_byte[b])) for a, b in char_spans],
        dtype=np.int64,
    )


def _target_mask(text: str, target: str) -> np.ndarray:
    axis = utf8_byte_axis(text)
    mask = np.zeros((axis.byte_length, 1), dtype=np.float32)
    for match in re.finditer(rf"(?i)(?<!\w){re.escape(target)}(?!\w)", text):
        a = int(axis.char_to_byte[match.start()])
        b = int(axis.char_to_byte[match.end()])
        mask[a:b, 0] = 1.0
    if not mask.any():
        raise ValueError("crop lost target word")
    return mask


def _unit_rows(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    return values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)


def _encode_model(model_name: str, snippets: list[dict], scales: tuple[int, ...], *, device: str) -> dict:
    from sentence_transformers import SentenceTransformer
    torch = _torch()
    model = SentenceTransformer(model_name, device=device)
    result = {}
    for item in snippets:
        text = item["text"]
        axis = utf8_byte_axis(text)
        scale_fields = {}
        for scale in scales:
            char_spans = _window_spans(text, scale)
            texts = [text[a:b] for a, b in char_spans]
            if "e5" in model_name.lower():
                texts = ["passage: " + value for value in texts]
            embeddings = model.encode(
                texts, batch_size=32, convert_to_numpy=True,
                normalize_embeddings=False, show_progress_bar=False,
            ).astype(np.float32)
            scale_fields[scale] = byte_aligned_scale(
                embeddings, _byte_spans(text, char_spans), byte_length=axis.byte_length
            )

        groups: list[tuple[str, np.ndarray]] = []
        for scale in scales:
            groups.append((f"scale_{scale}", _unit_rows(scale_fields[scale])))
        for small, large in zip(scales[:-1], scales[1:], strict=True):
            relations = vector_relations(scale_fields[small], scale_fields[large], epsilon=1e-3)
            for relation_name, values in relations.items():
                groups.append((f"{relation_name}_{small}_{large}", _unit_rows(values)))
        result[item["doc_id"]] = {
            "matrix": np.concatenate([values for _, values in groups], axis=1).astype(np.float32),
            "channels": [name for name, _ in groups],
            "embedding_dim": int(scale_fields[scales[0]].shape[1]),
            "byte_length": axis.byte_length,
        }
    del model
    torch.cuda.empty_cache()
    return result


def _direct_probe(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray) -> dict:
    weights = ridge_multioutput(train_x, train_y, 1.0)
    scored = np.hstack([test_x, np.ones((len(test_x), 1))]) @ weights
    score = scored[:, 0]
    truth = test_y[:, 0] > 0
    threshold, best_f1 = best_f1_threshold(score, truth)
    return {
        "auprc": float(average_precision(score, truth)),
        "best_f1": float(best_f1),
        "best_threshold": float(threshold),
        "prevalence": float(truth.mean()),
    }


def _csr_to_torch(matrix: sp.csr_matrix, *, device):
    torch = _torch()
    matrix = matrix.tocsr().astype(np.float32)
    return torch.sparse_csr_tensor(
        torch.as_tensor(matrix.indptr, dtype=torch.int64, device=device),
        torch.as_tensor(matrix.indices, dtype=torch.int64, device=device),
        torch.as_tensor(matrix.data, dtype=torch.float32, device=device),
        size=matrix.shape,
        device=device,
    )


def _fixed_sparse_projection(rows: int, cols: int, *, seed: int, device):
    torch = _torch()
    rng = np.random.default_rng(seed)
    per_row = max(1, int(round(np.sqrt(cols))))
    row = np.repeat(np.arange(rows, dtype=np.int64), per_row)
    col = np.concatenate([rng.choice(cols, size=per_row, replace=False) for _ in range(rows)]).astype(np.int64)
    sign = rng.choice([-1.0, 1.0], size=len(row)).astype(np.float32) / np.float32(np.sqrt(per_row))
    indices = torch.as_tensor(np.vstack([row, col]), dtype=torch.int64, device=device)
    values = torch.as_tensor(sign, dtype=torch.float32, device=device)
    return torch.sparse_coo_tensor(indices, values, (rows, cols), device=device).coalesce()


def _heldout(model, xs, ys):
    torch = _torch()
    logits, residuals = [], []
    model.eval()
    with torch.no_grad():
        for x in xs:
            local_logits, residual = model.standalone_logits(x)
            logits.append(local_logits.detach().cpu().numpy())
            residuals.append(float((torch.linalg.vector_norm(residual, dim=1) /
                                    torch.linalg.vector_norm(x, dim=1).clamp_min(1e-12)).mean().cpu()))
    model.train()
    score = score_standalone(np.vstack(logits), np.vstack([y.cpu().numpy() for y in ys]))
    return {**score, "residual_ratio": float(np.mean(residuals))}


def _train_arm(*, assisted: bool, initial: dict, train_x, train_y, test_x, test_y,
               operator, input_weights, input_indices, whole_brain, readout_projection,
               flavour, epochs: int, lr: float, input_dim: int, readout_width: int):
    torch = _torch()
    spec = FlyAssistSpec(rank=16, steps_per_chunk=1, leak=0.4, gain=4.0,
                         target_drive_rms=0.05, assist_weight=1.0, assist_fraction=1.0)
    model = make_model(input_dim, 1, readout_width, flavour.shape[1], spec).to(train_x[0].device)
    model.load_state_dict(initial)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    curve = []
    for epoch in range(epochs):
        losses, fly_losses, drives = [], [], []
        for x, y in zip(train_x, train_y, strict=True):
            optimizer.zero_grad(set_to_none=True)
            kwargs = {}
            if assisted:
                kwargs = dict(
                    operator=operator, input_weights=input_weights, input_indices=input_indices,
                    readout_indices=whole_brain, readout_projection=readout_projection,
                    flavours=flavour,
                )
            result = training_loss(
                model, x, y, spec=spec, assist_lambda=1.0 if assisted else 0.0, **kwargs
            )
            result["loss"].backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            losses.append(float(result["loss"].detach().cpu()))
            fly_losses.append(float(result["fly_loss"].detach().cpu()))
            drives.append(float(result["drive_rms"].detach().cpu()))
        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "fly_loss": float(np.mean(fly_losses)),
            "drive_rms": float(np.mean(drives)),
            "heldout": _heldout(model, test_x, test_y),
        }
        print(json.dumps({"event": "epoch", "arm": "assisted" if assisted else "tag_only", **row}), flush=True)
        curve.append(row)
    return {"curve": curve, "heldout_final": _heldout(model, test_x, test_y)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--val", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target", default="recurso")
    parser.add_argument("--train-docs", type=int, default=3)
    parser.add_argument("--val-docs", type=int, default=2)
    parser.add_argument("--crop-chars", type=int, default=160)
    parser.add_argument("--scales", type=int, nargs="+", default=[8, 32, 128])
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--readout-width", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--models", nargs="+", default=[
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ])
    args = parser.parse_args()

    torch = _torch()
    device = torch.device("cuda")
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    scales = tuple(args.scales)

    train_items = _choose(_load_jsonl(args.train), args.target, args.train_docs, args.crop_chars)
    val_items = _choose(_load_jsonl(args.val), args.target, args.val_docs, args.crop_chars)
    all_items = train_items + val_items

    encoded_by_model = {}
    for model_name in args.models:
        print(json.dumps({"event": "embedding_model_start", "model": model_name}), flush=True)
        encoded_by_model[model_name] = _encode_model(model_name, all_items, scales, device="cuda")
        first = encoded_by_model[model_name][all_items[0]["doc_id"]]
        print(json.dumps({"event": "embedding_model_ready", "model": model_name,
                          "embedding_dim": first["embedding_dim"],
                          "channels": first["channels"]}), flush=True)

    def matrices(items, model_names):
        xs, ys = [], []
        for item in items:
            pieces = [encoded_by_model[name][item["doc_id"]]["matrix"] for name in model_names]
            xs.append(np.concatenate(pieces, axis=1).astype(np.float32))
            ys.append(_target_mask(item["text"], args.target))
        return xs, ys

    direct = {}
    for model_name in args.models:
        train_np, train_y_np = matrices(train_items, [model_name])
        val_np, val_y_np = matrices(val_items, [model_name])
        direct[model_name] = _direct_probe(
            np.vstack(train_np), np.vstack(train_y_np), np.vstack(val_np), np.vstack(val_y_np)
        )
    train_np, train_y_np = matrices(train_items, args.models)
    val_np, val_y_np = matrices(val_items, args.models)
    direct["combined"] = _direct_probe(
        np.vstack(train_np), np.vstack(train_y_np), np.vstack(val_np), np.vstack(val_y_np)
    )
    print(json.dumps({"event": "direct_probes", "results": direct}), flush=True)

    matrix = row_normalise(load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    operator = _csr_to_torch(matrix, device=device)
    neurons = int(matrix.shape[0])
    input_dim = int(train_np[0].shape[1])
    input_weights = torch.as_tensor(
        rng.normal(size=(populations.input_indices.size, input_dim)).astype(np.float32), device=device
    )
    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=device)
    whole_brain = torch.arange(neurons, dtype=torch.int64, device=device)
    readout_projection = _fixed_sparse_projection(
        args.readout_width, neurons, seed=args.seed + 17, device=device
    )
    flavour_np = rng.normal(size=(1, 8)).astype(np.float32)
    flavour_np /= np.linalg.norm(flavour_np, axis=1, keepdims=True)
    flavour = torch.as_tensor(flavour_np, dtype=torch.float32, device=device)

    train_x = [torch.as_tensor(x, dtype=torch.float32, device=device) for x in train_np]
    train_y = [torch.as_tensor(y, dtype=torch.float32, device=device) for y in train_y_np]
    val_x = [torch.as_tensor(x, dtype=torch.float32, device=device) for x in val_np]
    val_y = [torch.as_tensor(y, dtype=torch.float32, device=device) for y in val_y_np]

    base_spec = FlyAssistSpec(rank=16, steps_per_chunk=1)
    torch.manual_seed(args.seed + 9000)
    base = make_model(input_dim, 1, args.readout_width, flavour.shape[1], base_spec).to(device)
    initial = deepcopy(base.state_dict())
    del base

    tag_only = _train_arm(
        assisted=False, initial=initial, train_x=train_x, train_y=train_y,
        test_x=val_x, test_y=val_y, operator=None, input_weights=None,
        input_indices=None, whole_brain=None, readout_projection=None, flavour=flavour,
        epochs=args.epochs, lr=args.lr, input_dim=input_dim, readout_width=args.readout_width,
    )
    assisted = _train_arm(
        assisted=True, initial=initial, train_x=train_x, train_y=train_y,
        test_x=val_x, test_y=val_y, operator=operator, input_weights=input_weights,
        input_indices=input_indices, whole_brain=whole_brain,
        readout_projection=readout_projection, flavour=flavour,
        epochs=args.epochs, lr=args.lr, input_dim=input_dim, readout_width=args.readout_width,
    )

    first_model = args.models[0]
    per_encoder_channels = encoded_by_model[first_model][all_items[0]["doc_id"]]["channels"]
    payload = {
        "schema": "papers/malecns-word-curriculum-smoke-v1",
        "claim_status": "exploratory curriculum smoke only; exact-word task",
        "target": args.target,
        "models": args.models,
        "scales_chars": list(scales),
        "channels_per_encoder": per_encoder_channels,
        "channel_count_total": len(per_encoder_channels) * len(args.models),
        "combined_input_dim": input_dim,
        "train_documents": [item["doc_id"] for item in train_items],
        "val_documents": [item["doc_id"] for item in val_items],
        "train_bytes": int(sum(len(x) for x in train_np)),
        "val_bytes": int(sum(len(x) for x in val_np)),
        "direct_probes": direct,
        "neurons": neurons,
        "edges": int(matrix.nnz),
        "sensory_neurons": int(populations.input_indices.size),
        "wholebrain_projection_width": args.readout_width,
        "tag_only": tag_only,
        "malecns_assisted": assisted,
        "device": torch.cuda.get_device_name(0),
        "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()),
        "next_curriculum": [
            "several exact words with distinct flavours",
            "synonym groups rewarded with one shared flavour",
            "unseen synonyms held out from reward during training",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "complete", "summary": payload}), flush=True)


if __name__ == "__main__":
    main()
