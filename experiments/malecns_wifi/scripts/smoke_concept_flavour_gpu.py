"""Exploratory concept-flavour curriculum on byte-aligned semantic channels.

The concept is pre-calibrated *before* MaleCNS from positive and negative anchor
phrases in each frozen embedding space. The text is represented at several
character scales, interpolated to the UTF-8 byte axis, and related to the concept
flavour with full vector operations (difference, product, stabilised ratio).

This smoke asks four separate questions:

1. Does a literal one-word flavour localise the concept?
2. Does a positive synonym/example bank improve localisation?
3. Does subtracting homonymous negative contexts improve it further?
4. After that offline calibration, does allowing the flavour vector itself to
   move under MaleCNS reward improve held-out synonym localisation compared with
   an identical arm whose flavour is frozen?

Held-out concept expressions are excluded from both the offline positive bank and
the online reward. This is exploratory curriculum evidence only, not Stage A/B.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from malecns_wifi import load_graph
from malecns_wifi.encoder_gate import average_precision
from malecns_wifi.multitag import ridge_multioutput
from malecns_wifi.tagger import row_normalise, select_populations
from malecns_wifi.text_axis_channels import byte_aligned_scale, utf8_byte_axis


POSITIVE_ANCHORS = (
    "recurso processual",
    "recurso judicial",
    "agravo",
    "recurso especial",
    "recurso extraordinário",
    "insurgência recursal",
    "meio de impugnação de decisão judicial",
)
NEGATIVE_ANCHORS = (
    "recurso financeiro",
    "recursos humanos",
    "recurso natural",
    "recurso orçamentário",
    "recurso tecnológico",
    "recurso pedagógico",
)
HELDOUT_CONCEPTS = (
    "apelação",
    "recurso ordinário",
    "embargos de declaração",
)

TRAIN_EXAMPLES = (
    ("A parte interpôs recurso processual contra a decisão.", "recurso processual", True, "seen_positive"),
    ("O agravo foi encaminhado ao relator para julgamento.", "agravo", True, "seen_positive"),
    ("Foi admitido o recurso especial apresentado pela defesa.", "recurso especial", True, "seen_positive"),
    ("O recurso extraordinário teve seguimento negado na origem.", "recurso extraordinário", True, "seen_positive"),
    ("A insurgência recursal questiona a condenação imposta.", "insurgência recursal", True, "seen_positive"),
    ("O recurso judicial foi protocolado dentro do prazo.", "recurso judicial", True, "seen_positive"),
    ("A empresa recebeu recurso financeiro para concluir a obra.", "recurso financeiro", False, "negative_homonym"),
    ("O setor de recursos humanos publicou novo comunicado.", "recursos humanos", False, "negative_homonym"),
    ("A água é um recurso natural essencial à população.", "recurso natural", False, "negative_homonym"),
    ("O município reservou recurso orçamentário para a despesa.", "recurso orçamentário", False, "negative_homonym"),
    ("O aplicativo é um recurso tecnológico usado na escola.", "recurso tecnológico", False, "negative_homonym"),
    ("O professor adotou um recurso pedagógico visual.", "recurso pedagógico", False, "negative_homonym"),
)

VAL_EXAMPLES = (
    ("A apelação foi interposta contra a sentença condenatória.", "apelação", True, "unseen_positive"),
    ("O recurso ordinário será examinado pelo tribunal competente.", "recurso ordinário", True, "unseen_positive"),
    ("Foram opostos embargos de declaração por omissão no julgado.", "embargos de declaração", True, "unseen_positive"),
    ("O agravo discute apenas a decisão interlocutória.", "agravo", True, "seen_positive"),
    ("O recurso especial aponta divergência jurisprudencial.", "recurso especial", True, "seen_positive"),
    ("O banco liberou recurso financeiro para capital de giro.", "recurso financeiro", False, "negative_homonym"),
    ("A floresta constitui importante recurso natural da região.", "recurso natural", False, "negative_homonym"),
    ("A secretaria ampliou o recurso orçamentário disponível.", "recurso orçamentário", False, "negative_homonym"),
)


def _torch():
    import torch
    return torch


@dataclass
class Example:
    text: str
    phrase: str
    positive: bool
    group: str
    mask: np.ndarray | None = None


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


def _mask_for(example: Example) -> np.ndarray:
    axis = utf8_byte_axis(example.text)
    mask = np.zeros((axis.byte_length, 1), dtype=np.float32)
    if not example.positive:
        return mask
    start = example.text.lower().find(example.phrase.lower())
    if start < 0:
        raise ValueError(f"positive phrase {example.phrase!r} missing from {example.text!r}")
    end = start + len(example.phrase)
    a = int(axis.char_to_byte[start])
    b = int(axis.char_to_byte[end])
    mask[a:b, 0] = 1.0
    return mask


def _unit_rows_np(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    return values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)


def _unit_vec_np(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float32)
    return value / max(float(np.linalg.norm(value)), 1e-12)


def _unit_rows_torch(values):
    torch = _torch()
    return values / torch.linalg.vector_norm(values, dim=1, keepdim=True).clamp_min(1e-12)


def _unit_vec_torch(value):
    torch = _torch()
    return value / torch.linalg.vector_norm(value).clamp_min(1e-12)


def _cosine_np(a: np.ndarray, b: np.ndarray) -> float:
    return float(_unit_vec_np(a) @ _unit_vec_np(b))


def _encode_anchor_set(model, model_name: str, texts: tuple[str, ...], *, kind: str) -> np.ndarray:
    if "e5" in model_name.lower():
        prefix = "query: " if kind == "query" else "passage: "
        texts = tuple(prefix + text for text in texts)
    values = model.encode(
        list(texts),
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(values, dtype=np.float32)


def _encode_fields(model, model_name: str, examples: list[Example], scales: tuple[int, ...]) -> list[dict[int, np.ndarray]]:
    fields = []
    for example in examples:
        text = example.text
        axis = utf8_byte_axis(text)
        local = {}
        for scale in scales:
            spans = _window_spans(text, scale)
            windows = [text[a:b] for a, b in spans]
            if "e5" in model_name.lower():
                windows = ["passage: " + value for value in windows]
            embeddings = model.encode(
                windows,
                batch_size=32,
                convert_to_numpy=True,
                normalize_embeddings=False,
                show_progress_bar=False,
            ).astype(np.float32)
            local[scale] = byte_aligned_scale(
                embeddings,
                _byte_spans(text, spans),
                byte_length=axis.byte_length,
            )
        fields.append(local)
    return fields


def _prepare_encoders(model_names: list[str], examples: list[Example], scales: tuple[int, ...], device: str):
    cache_path = Path("artifacts/embedding_cache/embeddings.npz")
    if cache_path.exists():
        try:
            cached = np.load(cache_path, allow_pickle=False)
            result = []
            for model_index, model_name in enumerate(model_names):
                prefix = f"model_{model_index}_"
                literal = cached[prefix + "literal"]
                positive_centroid = cached[prefix + "positive_centroid"]
                negative_centroid = cached[prefix + "negative_centroid"]
                discriminative = cached[prefix + "discriminative"]
                heldout_centroid = cached[prefix + "heldout_centroid"]
                fields = []
                for ex_idx in range(len(examples)):
                    local = {}
                    for sc in scales:
                        local[sc] = cached[f"{prefix}ex_{ex_idx}_scale_{sc}"]
                    fields.append(local)
                geom = {
                    "literal_to_positive": _cosine_np(literal, positive_centroid),
                    "literal_to_negative": _cosine_np(literal, negative_centroid),
                    "discriminative_to_positive": _cosine_np(discriminative, positive_centroid),
                    "discriminative_to_negative": _cosine_np(discriminative, negative_centroid),
                    "discriminative_to_heldout": float(_unit_vec_np(discriminative) @ _unit_vec_np(heldout_centroid)),
                }
                result.append({
                    "name": model_name,
                    "dim": int(literal.shape[0]),
                    "literal": literal,
                    "positive_centroid": positive_centroid,
                    "negative_centroid": negative_centroid,
                    "discriminative": discriminative,
                    "heldout_centroid": heldout_centroid,
                    "fields": fields,
                    "geometry": geom,
                })
                print(json.dumps({
                    "event": "embedding_model_cached",
                    "model": model_name,
                    "embedding_dim": int(literal.shape[0]),
                    "geometry": geom,
                }), flush=True)
            return result
        except Exception as e:
            print(f"Notice: could not load from cache ({e}), falling back to live encoding", flush=True)

    from sentence_transformers import SentenceTransformer

    torch = _torch()
    result = []
    for model_name in model_names:
        print(json.dumps({"event": "embedding_model_start", "model": model_name}), flush=True)
        model = SentenceTransformer(model_name, device=device)
        literal = _encode_anchor_set(model, model_name, ("recurso",), kind="query")[0]
        positives = _encode_anchor_set(model, model_name, POSITIVE_ANCHORS, kind="query")
        negatives = _encode_anchor_set(model, model_name, NEGATIVE_ANCHORS, kind="query")
        heldout = _encode_anchor_set(model, model_name, HELDOUT_CONCEPTS, kind="query")

        positive_centroid = _unit_vec_np(positives.mean(axis=0))
        negative_centroid = _unit_vec_np(negatives.mean(axis=0))
        discriminative = _unit_vec_np(positive_centroid - negative_centroid)
        literal = _unit_vec_np(literal)

        fields = _encode_fields(model, model_name, examples, scales)
        result.append({
            "name": model_name,
            "dim": int(literal.shape[0]),
            "literal": literal,
            "positive_centroid": positive_centroid,
            "negative_centroid": negative_centroid,
            "discriminative": discriminative,
            "heldout_centroid": _unit_vec_np(heldout.mean(axis=0)),
            "fields": fields,
            "geometry": {
                "literal_to_positive": _cosine_np(literal, positive_centroid),
                "literal_to_negative": _cosine_np(literal, negative_centroid),
                "discriminative_to_positive": _cosine_np(discriminative, positive_centroid),
                "discriminative_to_negative": _cosine_np(discriminative, negative_centroid),
                "discriminative_to_heldout": _cosine_np(discriminative, heldout.mean(axis=0)),
            },
        })
        print(json.dumps({
            "event": "embedding_model_ready",
            "model": model_name,
            "embedding_dim": int(literal.shape[0]),
            "geometry": result[-1]["geometry"],
        }), flush=True)
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return result


def _relation_channels_np(fields: dict[int, np.ndarray], flavour: np.ndarray, scales: tuple[int, ...]) -> np.ndarray:
    pieces = []
    flavour = np.asarray(flavour, dtype=np.float32)
    safe = np.where(
        np.abs(flavour) < 1e-3,
        np.where(flavour < 0, -1e-3, 1e-3),
        flavour,
    ).astype(np.float32)
    for scale in scales:
        values = np.asarray(fields[scale], dtype=np.float32)
        pieces.extend([
            _unit_rows_np(values - flavour[None, :]),
            _unit_rows_np(values * flavour[None, :]),
            _unit_rows_np(values / safe[None, :]),
        ])
    return np.concatenate(pieces, axis=1).astype(np.float32)


def _build_features(encoders, example_indices, scales, variant: str) -> list[np.ndarray]:
    xs = []
    for index in example_indices:
        parts = []
        for encoder in encoders:
            parts.append(_relation_channels_np(encoder["fields"][index], encoder[variant], scales))
        xs.append(np.concatenate(parts, axis=1).astype(np.float32))
    return xs


def _direct_probe(train_x, train_y, val_x, val_y) -> dict:
    train_matrix = np.vstack(train_x)
    train_mask = np.vstack(train_y)
    val_matrix = np.vstack(val_x)
    val_mask = np.vstack(val_y)
    weights = ridge_multioutput(train_matrix, train_mask, 1.0)
    scores = (np.hstack([val_matrix, np.ones((len(val_matrix), 1))]) @ weights)[:, 0]
    truth = val_mask[:, 0] > 0
    return {
        "auprc": float(average_precision(scores, truth)),
        "prevalence": float(truth.mean()),
    }


def _simple_cosine_scores(encoders, indices, scales, variant: str, examples):
    scores, masks, groups = [], [], []
    for index in indices:
        per_encoder = []
        for encoder in encoders:
            flavour = _unit_vec_np(encoder[variant])
            scale_scores = []
            for scale in scales:
                values = _unit_rows_np(encoder["fields"][index][scale])
                scale_scores.append(values @ flavour)
            per_encoder.append(np.max(np.stack(scale_scores, axis=1), axis=1))
        scores.append(np.mean(np.stack(per_encoder, axis=1), axis=1))
        masks.append(examples[index].mask[:, 0] > 0)
        groups.extend([examples[index].group] * len(scores[-1]))
    return np.concatenate(scores), np.concatenate(masks), np.asarray(groups, dtype=object)


def _score_vector(scores: np.ndarray, truth: np.ndarray) -> float:
    if not truth.any() or truth.all():
        return float("nan")
    return float(average_precision(scores, truth))


def _score_by_group(scores, truth, groups) -> dict:
    result = {"all": _score_vector(scores, truth)}
    unseen = np.isin(groups, ["unseen_positive", "negative_homonym"])
    seen = np.isin(groups, ["seen_positive", "negative_homonym"])
    result["unseen_generalization"] = _score_vector(scores[unseen], truth[unseen])
    result["seen_transfer"] = _score_vector(scores[seen], truth[seen])
    return result


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
    col = np.concatenate([
        rng.choice(cols, size=per_row, replace=False).astype(np.int64)
        for _ in range(rows)
    ])
    sign = rng.choice([-1.0, 1.0], size=len(row)).astype(np.float32)
    value = sign / np.float32(np.sqrt(per_row))
    indices = torch.as_tensor(np.vstack([row, col]), dtype=torch.int64, device=device)
    values = torch.as_tensor(value, dtype=torch.float32, device=device)
    return torch.sparse_coo_tensor(indices, values, (rows, cols), device=device).coalesce()


class ConceptTasteModel:
    @staticmethod
    def build(initial_flavours: list[np.ndarray], readout_width: int, *, train_flavour: bool, device):
        torch = _torch()
        nn = torch.nn

        class Model(nn.Module):
            def __init__(self):
                super().__init__()
                self.delta = nn.ParameterList([
                    nn.Parameter(
                        torch.zeros(len(value), dtype=torch.float32, device=device),
                        requires_grad=train_flavour,
                    )
                    for value in initial_flavours
                ])
                self.register_buffer(
                    "initial",
                    torch.stack([
                        torch.as_tensor(value, dtype=torch.float32, device=device)
                        for value in initial_flavours
                    ]),
                )
                self.taste_head = nn.Linear(readout_width, 1)

            def flavour(self, index: int):
                return _unit_vec_torch(self.initial[index] + self.delta[index])

        return Model().to(device)


def _relation_channels_torch(fields: dict[int, object], flavour, scales):
    torch = _torch()
    pieces = []
    sign = torch.where(flavour < 0, -torch.ones_like(flavour), torch.ones_like(flavour))
    safe = torch.where(flavour.abs() < 1e-3, sign * 1e-3, flavour)
    for scale in scales:
        values = fields[scale]
        pieces.extend([
            _unit_rows_torch(values - flavour[None, :]),
            _unit_rows_torch(values * flavour[None, :]),
            _unit_rows_torch(values / safe[None, :]),
        ])
    return torch.cat(pieces, dim=1)


def _reservoir_logits(*, model, encoder_fields, example_index, scales, operator,
                      input_weights, input_indices, whole_brain, readout_projection,
                      gain: float, leak: float, target_rms: float):
    torch = _torch()
    pieces = []
    for encoder_index, fields_by_example in enumerate(encoder_fields):
        pieces.append(_relation_channels_torch(
            fields_by_example[example_index],
            model.flavour(encoder_index),
            scales,
        ))
    features = torch.cat(pieces, dim=1)
    projected = input_weights @ features.T
    rms = torch.sqrt(torch.mean(projected.square())).clamp_min(1e-12)
    projected = projected * (target_rms / rms)

    neurons = int(operator.shape[0])
    state = torch.zeros(neurons, dtype=torch.float32, device=features.device)
    outputs = []
    for step in range(features.shape[0]):
        drive = torch.zeros_like(state).index_add(0, input_indices, projected[:, step])
        pre = torch.sparse.mm(operator, state[:, None]).squeeze(1) * gain + drive
        state = (1.0 - leak) * state + leak * torch.tanh(pre)
        probed = state[whole_brain]
        outputs.append(torch.sparse.mm(readout_projection, probed[:, None]).squeeze(1))
    states = torch.stack(outputs, dim=0)
    return model.taste_head(states), torch.sqrt(torch.mean(projected.square()))


def _heldout_score(*, model, indices, masks_t, groups_by_example, encoder_fields, scales,
                   operator, input_weights, input_indices, whole_brain, readout_projection):
    torch = _torch()
    scores, truth, groups = [], [], []
    model.eval()
    with torch.no_grad():
        for index in indices:
            logits, _ = _reservoir_logits(
                model=model,
                encoder_fields=encoder_fields,
                example_index=index,
                scales=scales,
                operator=operator,
                input_weights=input_weights,
                input_indices=input_indices,
                whole_brain=whole_brain,
                readout_projection=readout_projection,
                gain=4.0,
                leak=0.4,
                target_rms=0.05,
            )
            scores.append(torch.sigmoid(logits[:, 0]).cpu().numpy())
            truth.append(masks_t[index][:, 0].cpu().numpy() > 0)
            groups.extend([groups_by_example[index]] * logits.shape[0])
    model.train()
    scores = np.concatenate(scores)
    truth = np.concatenate(truth)
    groups = np.asarray(groups, dtype=object)
    return _score_by_group(scores, truth, groups)


def _flavour_diagnostics(model, encoders) -> list[dict]:
    rows = []
    for index, encoder in enumerate(encoders):
        current = model.flavour(index).detach().cpu().numpy()
        rows.append({
            "model": encoder["name"],
            "cosine_to_initial": _cosine_np(current, encoder["discriminative"]),
            "cosine_to_positive": _cosine_np(current, encoder["positive_centroid"]),
            "cosine_to_negative": _cosine_np(current, encoder["negative_centroid"]),
            "cosine_to_heldout": _cosine_np(current, encoder["heldout_centroid"]),
            "delta_norm": float(model.delta[index].detach().norm().cpu()),
        })
    return rows


def _train_arm(*, train_flavour: bool, initial_state: dict, encoders, encoder_fields,
               train_indices, val_indices, masks_t, groups_by_example, scales,
               operator, input_weights, input_indices, whole_brain, readout_projection,
               epochs: int, lr: float, anchor_lambda: float, pos_weight: float, device):
    torch = _torch()
    model = ConceptTasteModel.build(
        [encoder["discriminative"] for encoder in encoders],
        readout_projection.shape[0],
        train_flavour=train_flavour,
        device=device,
    )
    model.load_state_dict(initial_state, strict=False)
    for delta in model.delta:
        delta.requires_grad_(train_flavour)

    optimizer = torch.optim.AdamW(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=lr,
    )
    pos_weight_tensor = torch.tensor([pos_weight], dtype=torch.float32, device=device)
    curve = []

    for epoch in range(epochs):
        losses, bces, anchors, drives = [], [], [], []
        preclip = 0.0
        for index in train_indices:
            optimizer.zero_grad(set_to_none=True)
            logits, drive_rms = _reservoir_logits(
                model=model,
                encoder_fields=encoder_fields,
                example_index=index,
                scales=scales,
                operator=operator,
                input_weights=input_weights,
                input_indices=input_indices,
                whole_brain=whole_brain,
                readout_projection=readout_projection,
                gain=4.0,
                leak=0.4,
                target_rms=0.05,
            )
            target = masks_t[index]
            bce = torch.nn.functional.binary_cross_entropy_with_logits(
                logits,
                target,
                pos_weight=pos_weight_tensor,
            )
            anchor = torch.stack([delta.square().mean() for delta in model.delta]).mean()
            loss = bce + anchor_lambda * anchor
            loss.backward()
            preclip = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
            optimizer.step()

            losses.append(float(loss.detach().cpu()))
            bces.append(float(bce.detach().cpu()))
            anchors.append(float(anchor.detach().cpu()))
            drives.append(float(drive_rms.detach().cpu()))

        heldout = _heldout_score(
            model=model,
            indices=val_indices,
            masks_t=masks_t,
            groups_by_example=groups_by_example,
            encoder_fields=encoder_fields,
            scales=scales,
            operator=operator,
            input_weights=input_weights,
            input_indices=input_indices,
            whole_brain=whole_brain,
            readout_projection=readout_projection,
        )
        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "balanced_bce": float(np.mean(bces)),
            "anchor_penalty": float(np.mean(anchors)),
            "drive_rms": float(np.mean(drives)),
            "heldout": heldout,
            "flavours": _flavour_diagnostics(model, encoders),
            "preclip_grad_norm_last": preclip,
        }
        print(json.dumps({
            "event": "epoch",
            "arm": "online_flavour" if train_flavour else "frozen_flavour",
            **row,
        }), flush=True)
        curve.append(row)

    return {
        "curve": curve,
        "heldout_final": _heldout_score(
            model=model,
            indices=val_indices,
            masks_t=masks_t,
            groups_by_example=groups_by_example,
            encoder_fields=encoder_fields,
            scales=scales,
            operator=operator,
            input_weights=input_weights,
            input_indices=input_indices,
            whole_brain=whole_brain,
            readout_projection=readout_projection,
        ),
        "flavours_final": _flavour_diagnostics(model, encoders),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scales", type=int, nargs="+", default=[8, 32, 128])
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--models", nargs="+", default=[
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ])
    args = parser.parse_args()

    torch = _torch()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    scales = tuple(args.scales)

    train_examples = [Example(*row) for row in TRAIN_EXAMPLES]
    val_examples = [Example(*row) for row in VAL_EXAMPLES]
    examples = train_examples + val_examples
    for example in examples:
        example.mask = _mask_for(example)

    train_indices = list(range(len(train_examples)))
    val_indices = list(range(len(train_examples), len(examples)))
    train_y = [examples[index].mask for index in train_indices]
    val_y = [examples[index].mask for index in val_indices]

    encoders = _prepare_encoders(args.models, examples, scales, device=str(device))

    direct_probes = {}
    cosine_probes = {}
    for variant in ("literal", "positive_centroid", "discriminative"):
        train_x = _build_features(encoders, train_indices, scales, variant)
        val_x = _build_features(encoders, val_indices, scales, variant)
        direct_probes[variant] = _direct_probe(train_x, train_y, val_x, val_y)

        cosine_scores, cosine_truth, cosine_groups = _simple_cosine_scores(
            encoders, val_indices, scales, variant, examples
        )
        cosine_probes[variant] = _score_by_group(
            cosine_scores, cosine_truth, cosine_groups
        )

    print(json.dumps({
        "event": "offline_calibration",
        "direct_probes": direct_probes,
        "cosine_probes": cosine_probes,
    }), flush=True)

    encoder_fields = []
    for encoder in encoders:
        encoder_fields.append([
            {
                scale: torch.as_tensor(values, dtype=torch.float32, device=device)
                for scale, values in per_example.items()
            }
            for per_example in encoder["fields"]
        ])

    masks_t = [
        torch.as_tensor(example.mask, dtype=torch.float32, device=device)
        for example in examples
    ]
    groups_by_example = [example.group for example in examples]

    matrix = row_normalise(load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    operator = _csr_to_torch(matrix, device=device)
    neurons = int(matrix.shape[0])

    channel_dim = sum(encoder["dim"] * len(scales) * 3 for encoder in encoders)
    input_weights = torch.as_tensor(
        rng.normal(size=(populations.input_indices.size, channel_dim)).astype(np.float32)
        / np.float32(np.sqrt(channel_dim)),
        dtype=torch.float32,
        device=device,
    )
    input_indices = torch.as_tensor(
        populations.input_indices, dtype=torch.int64, device=device
    )
    whole_brain = torch.arange(neurons, dtype=torch.int64, device=device)
    readout_projection = _fixed_sparse_projection(
        args.readout_width,
        neurons,
        seed=args.seed + 17,
        device=device,
    )

    positive_bytes = int(sum(example.mask.sum() for example in train_examples))
    total_bytes = int(sum(len(example.mask) for example in train_examples))
    negative_bytes = total_bytes - positive_bytes
    pos_weight = float(min(negative_bytes / max(positive_bytes, 1), 30.0))

    torch.manual_seed(args.seed + 9000)
    base = ConceptTasteModel.build(
        [encoder["discriminative"] for encoder in encoders],
        args.readout_width,
        train_flavour=True,
        device=device,
    )
    initial_state = deepcopy(base.state_dict())
    del base

    frozen = _train_arm(
        train_flavour=False,
        initial_state=initial_state,
        encoders=encoders,
        encoder_fields=encoder_fields,
        train_indices=train_indices,
        val_indices=val_indices,
        masks_t=masks_t,
        groups_by_example=groups_by_example,
        scales=scales,
        operator=operator,
        input_weights=input_weights,
        input_indices=input_indices,
        whole_brain=whole_brain,
        readout_projection=readout_projection,
        epochs=args.epochs,
        lr=args.lr,
        anchor_lambda=args.anchor_lambda,
        pos_weight=pos_weight,
        device=device,
    )
    online = _train_arm(
        train_flavour=True,
        initial_state=initial_state,
        encoders=encoders,
        encoder_fields=encoder_fields,
        train_indices=train_indices,
        val_indices=val_indices,
        masks_t=masks_t,
        groups_by_example=groups_by_example,
        scales=scales,
        operator=operator,
        input_weights=input_weights,
        input_indices=input_indices,
        whole_brain=whole_brain,
        readout_projection=readout_projection,
        epochs=args.epochs,
        lr=args.lr,
        anchor_lambda=args.anchor_lambda,
        pos_weight=pos_weight,
        device=device,
    )

    payload = {
        "schema": "papers/malecns-concept-flavour-smoke-v1",
        "claim_status": (
            "exploratory curriculum smoke only; synthetic controlled text; "
            "held-out concept expressions excluded from calibration and reward"
        ),
        "positive_anchors": POSITIVE_ANCHORS,
        "negative_anchors": NEGATIVE_ANCHORS,
        "heldout_concepts": HELDOUT_CONCEPTS,
        "models": args.models,
        "scales_chars": list(scales),
        "conditioned_channels_per_scale": ["difference", "product", "ratio"],
        "channel_count_total": len(args.models) * len(scales) * 3,
        "combined_input_dim": int(channel_dim),
        "offline_geometry": {
            encoder["name"]: encoder["geometry"] for encoder in encoders
        },
        "offline_direct_probes": direct_probes,
        "offline_cosine_probes": cosine_probes,
        "train_positive_bytes": positive_bytes,
        "train_total_bytes": total_bytes,
        "balanced_bce_pos_weight": pos_weight,
        "neurons": neurons,
        "edges": int(matrix.nnz),
        "sensory_neurons": int(populations.input_indices.size),
        "wholebrain_projection_width": args.readout_width,
        "frozen_flavour": frozen,
        "online_flavour": online,
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0,
        "interpretation_guardrails": [
            "direct probes test whether the conditioned embedding field already contains the signal",
            "frozen-vs-online isolates whether reward-driven flavour movement helps beyond offline calibration",
            "unseen_generalization contains only held-out positive expressions plus negative homonyms",
            "no topology-specific claim without null-connectome controls",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "complete", "summary": payload}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
