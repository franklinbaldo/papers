"""Exploratory coupled concept-flavour + channel-translation smoke.

Each (encoder, context-scale) owns its own concept flavour in that space's native
dimensionality.  No vector is compared across incompatible embedding spaces.
Channels communicate only through evidence: a leave-one-channel-out consensus is
used as a detached teacher for each local flavour.  Thus when another channel says
"yes", the local flavour moves toward the *local embedding of the same byte*.

The same aligned training bytes also fit cheap ridge translators between spaces.
At validation we deliberately remove expensive channels and reconstruct them from
short-context channels, then ask whether the complete frozen MaleCNS taste decoder
retains concept localisation.

This is exploratory curriculum evidence only, not Stage A/B confirmatory evidence.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import torch

import smoke_concept_flavour_gpu as base


class FlavourBundle(torch.nn.Module):
    def __init__(self, initial_flavours: list[np.ndarray], readout_width: int, *, device):
        super().__init__()
        self.delta = torch.nn.ParameterList()
        self._initial_names: list[str] = []
        for index, value in enumerate(initial_flavours):
            name = f"initial_{index}"
            self.register_buffer(name, torch.as_tensor(value, dtype=torch.float32, device=device))
            self._initial_names.append(name)
            self.delta.append(torch.nn.Parameter(torch.zeros(len(value), dtype=torch.float32, device=device)))
        self.taste_head = torch.nn.Linear(readout_width, 1)

    def flavour(self, index: int):
        value = getattr(self, self._initial_names[index]) + self.delta[index]
        return value / torch.linalg.vector_norm(value).clamp_min(1e-12)


def _space_bank(encoders, train_indices, masks, scales):
    spaces = []
    for encoder_index, encoder in enumerate(encoders):
        for scale in scales:
            positive, negative = [], []
            for example_index in train_indices:
                field = encoder["fields"][example_index][scale]
                mask = masks[example_index][:, 0] > 0
                if mask.any():
                    positive.append(field[mask])
                    negative.append(field[~mask])
                else:
                    negative.append(field)
            pos = np.vstack(positive).mean(axis=0)
            neg = np.vstack(negative).mean(axis=0)
            initial = base._unit_vec_np(pos - neg)
            spaces.append({
                "encoder_index": encoder_index,
                "encoder": encoder["name"],
                "scale": int(scale),
                "dim": int(initial.shape[0]),
                "initial": initial,
            })
    return spaces


def _fields_by_space(encoders, spaces, examples, device):
    result = []
    for example_index in range(len(examples)):
        local = []
        for space in spaces:
            value = encoders[space["encoder_index"]]["fields"][example_index][space["scale"]]
            local.append(torch.as_tensor(value, dtype=torch.float32, device=device))
        result.append(local)
    return result


def _relation_block(field, flavour):
    field = field / torch.linalg.vector_norm(field, dim=1, keepdim=True).clamp_min(1e-12)
    flavour = flavour / torch.linalg.vector_norm(flavour).clamp_min(1e-12)
    sign = torch.where(flavour < 0, -torch.ones_like(flavour), torch.ones_like(flavour))
    safe = torch.where(flavour.abs() < 1e-3, sign * 1e-3, flavour)
    pieces = [field - flavour[None, :], field * flavour[None, :], field / safe[None, :]]
    return torch.cat([
        value / torch.linalg.vector_norm(value, dim=1, keepdim=True).clamp_min(1e-12)
        for value in pieces
    ], dim=1)


def _local_logits(model, fields):
    rows = []
    for index, field in enumerate(fields):
        unit = field / torch.linalg.vector_norm(field, dim=1, keepdim=True).clamp_min(1e-12)
        rows.append(6.0 * (unit @ model.flavour(index)))
    return torch.stack(rows, dim=1)


def _peer_loss(model, fields, target, pos_weight):
    logits = _local_logits(model, fields)
    probs = torch.sigmoid(logits.detach())
    count = logits.shape[1]
    losses = []
    for index in range(count):
        if count == 1:
            teacher = target[:, 0]
        else:
            keep = [j for j in range(count) if j != index]
            peer = probs[:, keep].mean(dim=1)
            # Ground truth/reward remains the anchor; peer consensus supplies the
            # cross-space evidence rather than replacing supervision.
            teacher = 0.65 * target[:, 0] + 0.35 * peer
        # soft BCE plus explicit positive weighting from the actual reward mask.
        soft = torch.nn.functional.binary_cross_entropy_with_logits(logits[:, index], teacher)
        hard = torch.nn.functional.binary_cross_entropy_with_logits(
            logits[:, index:index+1], target, pos_weight=pos_weight
        )
        losses.append(0.5 * soft + 0.5 * hard)
    return torch.stack(losses).mean()


from malecns_wifi.fast_spmv import fast_sparse_mm as _fast_sparse_mm, csr_to_fast_operator


def _reservoir_logits(model, fields, operator, input_weights, input_indices,
                      whole_brain, readout_projection, *, target_rms=0.05):
    features = torch.cat([
        _relation_block(field, model.flavour(index))
        for index, field in enumerate(fields)
    ], dim=1)
    projected = input_weights @ features.T
    rms = torch.sqrt(torch.mean(projected.square())).clamp_min(1e-12)
    projected = projected * (target_rms / rms)
    state = torch.zeros(int(operator.shape[0]), dtype=torch.float32, device=features.device)
    outputs = []
    for step in range(features.shape[0]):
        drive = torch.zeros_like(state).index_add(0, input_indices, projected[:, step])
        pre = _fast_sparse_mm(operator, state[:, None]).squeeze(1) * 4.0 + drive
        state = 0.6 * state + 0.4 * torch.tanh(pre)
        outputs.append(torch.sparse.mm(readout_projection, state[whole_brain, None]).squeeze(1))
    states = torch.stack(outputs)
    return model.taste_head(states), torch.sqrt(torch.mean(projected.square()))


def _ridge_map(source: np.ndarray, target: np.ndarray, penalty: float = 1e-2) -> np.ndarray:
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    design = np.hstack([source, np.ones((len(source), 1), dtype=np.float64)])
    gram = design @ design.T
    scale = penalty * max(float(np.trace(gram)) / max(len(gram), 1), 1e-12)
    return (design.T @ np.linalg.solve(gram + scale * np.eye(len(gram)), target)).astype(np.float32)


def _apply_map(source: np.ndarray, weights: np.ndarray) -> np.ndarray:
    design = np.hstack([source, np.ones((len(source), 1), dtype=np.float32)])
    return (design @ weights).astype(np.float32)


def _stack_source(encoders, example_index: int, encoder_indices, scales):
    parts = []
    for encoder_index in encoder_indices:
        for scale in scales:
            parts.append(base._unit_rows_np(encoders[encoder_index]["fields"][example_index][scale]))
    return np.concatenate(parts, axis=1).astype(np.float32)


def _fit_translators(encoders, spaces, train_indices):
    maps = {}
    # Same-encoder short context -> its long 128-ish context.
    short_scales = (8, 32)
    for target_index, space in enumerate(spaces):
        if space["scale"] != 128:
            continue
        xs, ys = [], []
        for example_index in train_indices:
            xs.append(_stack_source(encoders, example_index, [space["encoder_index"]], short_scales))
            ys.append(base._unit_rows_np(encoders[space["encoder_index"]]["fields"][example_index][space["scale"]]))
        maps[("no_128", target_index)] = _ridge_map(np.vstack(xs), np.vstack(ys))

    # One encoder's short channels -> every space of the other encoder.  This
    # handles different dimensionalities because the map is rectangular.
    if len(encoders) >= 2:
        for missing_encoder in range(len(encoders)):
            source_encoders = [index for index in range(len(encoders)) if index != missing_encoder]
            for target_index, space in enumerate(spaces):
                if space["encoder_index"] != missing_encoder:
                    continue
                xs, ys = [], []
                for example_index in train_indices:
                    xs.append(_stack_source(encoders, example_index, source_encoders, short_scales))
                    ys.append(base._unit_rows_np(encoders[missing_encoder]["fields"][example_index][space["scale"]]))
                maps[(f"no_encoder_{missing_encoder}", target_index)] = _ridge_map(np.vstack(xs), np.vstack(ys))

    # Extreme cheap path: MiniLM (encoder 0) scales 8+32 reconstructs every
    # other/missing space including its own long context.
    for target_index, space in enumerate(spaces):
        if space["encoder_index"] == 0 and space["scale"] in short_scales:
            continue
        xs, ys = [], []
        for example_index in train_indices:
            xs.append(_stack_source(encoders, example_index, [0], short_scales))
            ys.append(base._unit_rows_np(encoders[space["encoder_index"]]["fields"][example_index][space["scale"]]))
        maps[("minilm_short_only", target_index)] = _ridge_map(np.vstack(xs), np.vstack(ys))
    return maps


def _arm_fields(encoders, spaces, direct_fields, translators, example_index, arm, device):
    if arm == "all_direct":
        return direct_fields[example_index]
    result = []
    source_cache = {}
    for target_index, space in enumerate(spaces):
        use_direct = True
        key = None
        if arm == "no_128" and space["scale"] == 128:
            use_direct = False
            key = ("no_128", target_index)
            source_key = ("same", space["encoder_index"])
            if source_key not in source_cache:
                source_cache[source_key] = _stack_source(encoders, example_index, [space["encoder_index"]], (8, 32))
        elif arm.startswith("no_encoder_") and space["encoder_index"] == int(arm.rsplit("_", 1)[1]):
            use_direct = False
            key = (arm, target_index)
            missing = space["encoder_index"]
            source_key = ("other", missing)
            if source_key not in source_cache:
                src = [i for i in range(len(encoders)) if i != missing]
                source_cache[source_key] = _stack_source(encoders, example_index, src, (8, 32))
        elif arm == "minilm_short_only" and not (space["encoder_index"] == 0 and space["scale"] in (8, 32)):
            use_direct = False
            key = (arm, target_index)
            source_key = ("minilm", 0)
            if source_key not in source_cache:
                source_cache[source_key] = _stack_source(encoders, example_index, [0], (8, 32))
        if use_direct:
            result.append(direct_fields[example_index][target_index])
        else:
            if arm == "no_128":
                source = source_cache[("same", space["encoder_index"])]
            elif arm.startswith("no_encoder_"):
                source = source_cache[("other", space["encoder_index"])]
            else:
                source = source_cache[("minilm", 0)]
            predicted = _apply_map(source, translators[key])
            result.append(torch.as_tensor(predicted, dtype=torch.float32, device=device))
    return result


def _reconstruction_report(encoders, spaces, translators, val_indices):
    report = {}
    arms = ["no_128"]
    if len(encoders) >= 2:
        arms += ["no_encoder_0", "no_encoder_1"]
    arms += ["minilm_short_only"]
    for arm in arms:
        values = []
        for example_index in val_indices:
            for target_index, space in enumerate(spaces):
                key = (arm, target_index)
                if key not in translators:
                    continue
                if arm == "no_128":
                    source = _stack_source(encoders, example_index, [space["encoder_index"]], (8, 32))
                elif arm.startswith("no_encoder_"):
                    missing = int(arm.rsplit("_", 1)[1])
                    source = _stack_source(encoders, example_index, [i for i in range(len(encoders)) if i != missing], (8, 32))
                else:
                    source = _stack_source(encoders, example_index, [0], (8, 32))
                predicted = base._unit_rows_np(_apply_map(source, translators[key]))
                truth = base._unit_rows_np(encoders[space["encoder_index"]]["fields"][example_index][space["scale"]])
                values.extend(np.sum(predicted * truth, axis=1).tolist())
        report[arm] = {
            "mean_cosine": float(np.mean(values)) if values else float("nan"),
            "p10_cosine": float(np.quantile(values, 0.1)) if values else float("nan"),
            "n": len(values),
        }
    return report


def _score_model(model, *, arm, encoders, spaces, direct_fields, translators,
                 val_indices, examples, operator, input_weights, input_indices,
                 whole_brain, readout_projection, device):
    scores, truth, groups = [], [], []
    model.eval()
    with torch.no_grad():
        for example_index in val_indices:
            fields = _arm_fields(encoders, spaces, direct_fields, translators, example_index, arm, device)
            logits, _ = _reservoir_logits(
                model, fields, operator, input_weights, input_indices, whole_brain, readout_projection
            )
            scores.append(torch.sigmoid(logits[:, 0]).cpu().numpy())
            truth.append(examples[example_index].mask[:, 0] > 0)
            groups.extend([examples[example_index].group] * len(scores[-1]))
    model.train()
    return base._score_by_group(
        np.concatenate(scores), np.concatenate(truth), np.asarray(groups, dtype=object)
    )


def _flavour_report(model, spaces):
    return [
        {
            "encoder": space["encoder"],
            "scale": space["scale"],
            "delta_norm": float(model.delta[index].detach().norm().cpu()),
            "cosine_to_initial": base._cosine_np(
                model.flavour(index).detach().cpu().numpy(), space["initial"]
            ),
        }
        for index, space in enumerate(spaces)
    ]


def _train(*, peer_lambda, initial_state, spaces, direct_fields, train_indices,
           val_indices, examples, encoders, translators, operator, input_weights,
           input_indices, whole_brain, readout_projection, epochs, lr,
           anchor_lambda, pos_weight, device):
    model = FlavourBundle([space["initial"] for space in spaces], readout_projection.shape[0], device=device)
    model.load_state_dict(initial_state)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    pos_weight_t = torch.tensor([pos_weight], dtype=torch.float32, device=device)
    curve = []
    for epoch in range(epochs):
        losses, taste_losses, peer_losses = [], [], []
        for example_index in train_indices:
            optimizer.zero_grad(set_to_none=True)
            fields = direct_fields[example_index]
            logits, drive = _reservoir_logits(
                model, fields, operator, input_weights, input_indices, whole_brain, readout_projection
            )
            target = torch.as_tensor(examples[example_index].mask, dtype=torch.float32, device=device)
            taste = torch.nn.functional.binary_cross_entropy_with_logits(logits, target, pos_weight=pos_weight_t)
            peers = _peer_loss(model, fields, target, pos_weight_t)
            anchor = torch.stack([delta.square().mean() for delta in model.delta]).mean()
            loss = taste + peer_lambda * peers + anchor_lambda * anchor
            loss.backward()
            preclip = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
            taste_losses.append(float(taste.detach().cpu()))
            peer_losses.append(float(peers.detach().cpu()))
        validation = {}
        for arm in ["all_direct", "no_128"] + (["no_encoder_0", "no_encoder_1"] if len(encoders) >= 2 else []) + ["minilm_short_only"]:
            validation[arm] = _score_model(
                model, arm=arm, encoders=encoders, spaces=spaces,
                direct_fields=direct_fields, translators=translators,
                val_indices=val_indices, examples=examples, operator=operator,
                input_weights=input_weights, input_indices=input_indices,
                whole_brain=whole_brain, readout_projection=readout_projection,
                device=device,
            )
        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "taste_bce": float(np.mean(taste_losses)),
            "peer_loss": float(np.mean(peer_losses)),
            "preclip_grad_norm_last": preclip,
            "validation": validation,
            "flavours": _flavour_report(model, spaces),
        }
        print(json.dumps({"event": "epoch", "arm": "coupled" if peer_lambda else "independent", **row}), flush=True)
        curve.append(row)
    return {"curve": curve, "final_flavours": _flavour_report(model, spaces)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--peer-lambda", type=float, default=0.5)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--models", nargs="+", default=[
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ])
    parser.add_argument("--scales", type=int, nargs="+", default=[8, 32, 128])
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    scales = tuple(args.scales)
    if tuple(scales) != (8, 32, 128):
        raise SystemExit("this first translation smoke is preregistered for scales 8,32,128")

    train_examples = [base.Example(*row) for row in base.TRAIN_EXAMPLES]
    val_examples = [base.Example(*row) for row in base.VAL_EXAMPLES]
    examples = train_examples + val_examples
    for example in examples:
        example.mask = base._mask_for(example)
    train_indices = list(range(len(train_examples)))
    val_indices = list(range(len(train_examples), len(examples)))

    encoders = base._prepare_encoders(args.models, examples, scales, device=str(device))
    spaces = _space_bank(encoders, train_indices, [example.mask for example in examples], scales)
    direct_fields = _fields_by_space(encoders, spaces, examples, device)
    translators = _fit_translators(encoders, spaces, train_indices)
    reconstruction = _reconstruction_report(encoders, spaces, translators, val_indices)
    print(json.dumps({"event": "translation_reconstruction", "results": reconstruction}), flush=True)

    matrix = base.row_normalise(base.load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    populations = base.select_populations(archive["superclass"])
    operator = csr_to_fast_operator(matrix, device=device)
    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=device)
    whole_brain = torch.arange(matrix.shape[0], dtype=torch.int64, device=device)
    readout_projection = base._fixed_sparse_projection(
        args.readout_width, matrix.shape[0], seed=args.seed + 17, device=device
    )
    input_dim = int(sum(3 * space["dim"] for space in spaces))
    input_weights = torch.as_tensor(
        rng.normal(size=(len(populations.input_indices), input_dim)).astype(np.float32), device=device
    )

    positives = sum(float(examples[i].mask.sum()) for i in train_indices)
    total = sum(len(examples[i].mask) for i in train_indices)
    negatives = total - positives
    pos_weight = negatives / max(positives, 1.0)

    torch.manual_seed(args.seed + 9000)
    seed_model = FlavourBundle([space["initial"] for space in spaces], args.readout_width, device=device)
    initial_state = deepcopy(seed_model.state_dict())
    del seed_model

    independent = _train(
        peer_lambda=0.0, initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices, val_indices=val_indices,
        examples=examples, encoders=encoders, translators=translators,
        operator=operator, input_weights=input_weights, input_indices=input_indices,
        whole_brain=whole_brain, readout_projection=readout_projection,
        epochs=args.epochs, lr=args.lr, anchor_lambda=args.anchor_lambda,
        pos_weight=pos_weight, device=device,
    )
    coupled = _train(
        peer_lambda=args.peer_lambda, initial_state=initial_state, spaces=spaces,
        direct_fields=direct_fields, train_indices=train_indices, val_indices=val_indices,
        examples=examples, encoders=encoders, translators=translators,
        operator=operator, input_weights=input_weights, input_indices=input_indices,
        whole_brain=whole_brain, readout_projection=readout_projection,
        epochs=args.epochs, lr=args.lr, anchor_lambda=args.anchor_lambda,
        pos_weight=pos_weight, device=device,
    )

    payload = {
        "schema": "papers/malecns-coupled-flavour-translation-smoke-v1",
        "claim_status": "exploratory curriculum smoke only; not Stage A/B evidence",
        "models": args.models,
        "scales": list(scales),
        "spaces": [{k: v for k, v in space.items() if k != "initial"} for space in spaces],
        "flavour_rule": "one flavour per (encoder, scale) native space",
        "coupling_rule": "leave-one-channel-out evidence teacher; no cross-space vector arithmetic",
        "translation_rule": "ridge maps fitted on aligned training bytes only",
        "translation_reconstruction": reconstruction,
        "dropout_arms": ["all_direct", "no_128", "no_encoder_0", "no_encoder_1", "minilm_short_only"],
        "pos_weight": float(pos_weight),
        "independent": independent,
        "coupled": coupled,
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "complete", "summary": payload}), flush=True)


if __name__ == "__main__":
    main()
