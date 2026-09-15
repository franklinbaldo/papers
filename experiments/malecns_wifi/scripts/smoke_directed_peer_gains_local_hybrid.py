"""Local hybrid directed-peer experiment: CPU MaleCNS + optional DirectML dense modules.

This is a separate operational prototype.  Existing CUDA/Kaggle runners are not
modified.  Frozen semantic encoders, graph sparse recurrence, projections and
translation stay on CPU; only trainable dense modules (flavours, per-channel
adapters and taste head) live on the selected dense backend.

The CPU<->dense copies remain in the autograd graph.  Therefore this script also
acts as a compatibility test for torch-directml: if that backend cannot carry a
gradient across the hybrid boundary it fails explicitly rather than silently
falling back to a different scientific computation.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import torch

import local_dense_backend
import smoke_concept_flavour_gpu as base
import smoke_coupled_flavour_translation_gpu as v1
import smoke_coupled_flavour_translation_gpu_v3 as v3
import smoke_directed_peer_gains_one_gpu as directed
import smoke_peer_reliability_grid_gpu as grid


def _hybrid_local_logits(model, fields, dense_device):
    rows = []
    for index, field_cpu in enumerate(fields):
        field = field_cpu.to(dense_device)
        adapted = model.adapt(index, field)
        rows.append(6.0 * (adapted @ model.flavour(index)))
    return torch.stack(rows, dim=1)


def _hybrid_reservoir_logits(
    model,
    fields,
    operator,
    input_weights,
    input_indices,
    whole_brain,
    readout_projection,
    dense_device,
    *,
    target_rms=0.05,
):
    relation_blocks = []
    for index, field_cpu in enumerate(fields):
        field = field_cpu.to(dense_device)
        adapted = model.adapt(index, field)
        block = v1._relation_block(adapted, model.flavour(index))
        relation_blocks.append(block.to("cpu"))
    features = torch.cat(relation_blocks, dim=1)

    projected = input_weights @ features.T
    rms = torch.sqrt(torch.mean(projected.square())).clamp_min(1e-12)
    projected = projected * (target_rms / rms)
    state = torch.zeros(int(operator.shape[0]), dtype=torch.float32, device="cpu")
    outputs = []
    for step in range(features.shape[0]):
        drive = torch.zeros_like(state).index_add(0, input_indices, projected[:, step])
        pre = torch.sparse.mm(operator, state[:, None]).squeeze(1) * 4.0 + drive
        state = 0.6 * state + 0.4 * torch.tanh(pre)
        outputs.append(torch.sparse.mm(readout_projection, state[whole_brain, None]).squeeze(1))
    states_cpu = torch.stack(outputs)
    logits = model.taste_head(states_cpu.to(dense_device))
    return logits, torch.sqrt(torch.mean(projected.square()))


def _weighted_peer_loss(model, fields, target, pos_weight, weights, dense_device):
    logits = _hybrid_local_logits(model, fields, dense_device)
    probs = torch.sigmoid(logits.detach())
    count = logits.shape[1]
    weight_tensor = weights.to(dense_device)
    losses = []
    for receiver in range(count):
        if count == 1:
            teacher = target[:, 0]
        else:
            keep = torch.tensor(
                [sender for sender in range(count) if sender != receiver],
                dtype=torch.long,
                device=dense_device,
            )
            if weight_tensor.ndim == 1:
                local_weights = weight_tensor[keep]
            else:
                local_weights = weight_tensor[receiver, keep]
            peer = (probs[:, keep] * local_weights[None, :]).sum(dim=1)
            peer = peer / local_weights.sum().clamp_min(1e-12)
            teacher = 0.65 * target[:, 0] + 0.35 * peer
        soft = torch.nn.functional.binary_cross_entropy_with_logits(logits[:, receiver], teacher)
        hard = torch.nn.functional.binary_cross_entropy_with_logits(
            logits[:, receiver:receiver + 1], target, pos_weight=pos_weight
        )
        losses.append(0.5 * soft + 0.5 * hard)
    return torch.stack(losses).mean()


def _score_model(
    model,
    *,
    arm,
    encoders,
    spaces,
    direct_fields,
    translators,
    val_indices,
    examples,
    operator,
    input_weights,
    input_indices,
    whole_brain,
    readout_projection,
    dense_device,
):
    scores, truth, groups = [], [], []
    model.eval()
    with torch.no_grad():
        for example_index in val_indices:
            fields = v1._arm_fields(
                encoders, spaces, direct_fields, translators,
                example_index, arm, torch.device("cpu")
            )
            logits, _ = _hybrid_reservoir_logits(
                model, fields, operator, input_weights, input_indices,
                whole_brain, readout_projection, dense_device,
            )
            scores.append(torch.sigmoid(logits[:, 0]).cpu().numpy())
            truth.append(examples[example_index].mask[:, 0] > 0)
            groups.extend([examples[example_index].group] * len(scores[-1]))
    model.train()
    return base._score_by_group(
        np.concatenate(scores), np.concatenate(truth), np.asarray(groups, dtype=object)
    )


def _train_arm(
    *,
    mode,
    peer_weights,
    initial_state,
    spaces,
    direct_fields,
    train_indices,
    val_indices,
    examples,
    encoders,
    translators,
    operator,
    input_weights,
    input_indices,
    whole_brain,
    readout_projection,
    epochs,
    lr,
    peer_lambda,
    anchor_lambda,
    pos_weight,
    dense_device,
):
    model = v3.PerChannelAdapterFlavourBundle(
        [space["initial"] for space in spaces],
        readout_projection.shape[0],
        device=torch.device("cpu"),
    )
    model.load_state_dict(initial_state)
    model = model.to(dense_device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    pos_weight_t = torch.tensor([pos_weight], dtype=torch.float32, device=dense_device)
    curve = []

    for epoch in range(epochs):
        losses, taste_losses, peer_losses = [], [], []
        for example_index in train_indices:
            optimizer.zero_grad(set_to_none=True)
            fields = direct_fields[example_index]
            logits, _ = _hybrid_reservoir_logits(
                model, fields, operator, input_weights, input_indices,
                whole_brain, readout_projection, dense_device,
            )
            target = torch.as_tensor(
                examples[example_index].mask, dtype=torch.float32, device=dense_device
            )
            taste = torch.nn.functional.binary_cross_entropy_with_logits(
                logits, target, pos_weight=pos_weight_t
            )
            if mode == "independent":
                peers = torch.zeros((), dtype=torch.float32, device=dense_device)
            else:
                peers = _weighted_peer_loss(
                    model, fields, target, pos_weight_t, peer_weights, dense_device
                )
            anchor = torch.stack([delta.square().mean() for delta in model.delta]).mean()
            coupling = 0.0 if mode == "independent" else peer_lambda
            loss = taste + coupling * peers + anchor_lambda * anchor
            loss.backward()
            preclip = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
            taste_losses.append(float(taste.detach().cpu()))
            peer_losses.append(float(peers.detach().cpu()))

        validation = {}
        arms = ["all_direct", "no_128"]
        if len(encoders) >= 2:
            arms += ["no_encoder_0", "no_encoder_1"]
        arms += ["minilm_short_only"]
        for arm in arms:
            validation[arm] = _score_model(
                model,
                arm=arm,
                encoders=encoders,
                spaces=spaces,
                direct_fields=direct_fields,
                translators=translators,
                val_indices=val_indices,
                examples=examples,
                operator=operator,
                input_weights=input_weights,
                input_indices=input_indices,
                whole_brain=whole_brain,
                readout_projection=readout_projection,
                dense_device=dense_device,
            )
        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "taste_bce": float(np.mean(taste_losses)),
            "peer_loss": float(np.mean(peer_losses)),
            "preclip_grad_norm_last": preclip,
            "validation": validation,
            "flavours": v3._adapter_flavour_report(model, spaces),
        }
        print(json.dumps({"event": "hybrid_epoch", "arm": mode, **row}), flush=True)
        curve.append(row)

    return {"curve": curve, "final_flavours": v3._adapter_flavour_report(model, spaces)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dense-device", choices=["cpu", "directml", "auto"], default="auto")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--peer-lambda", type=float, default=0.50)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20260918)
    parser.add_argument("--models", nargs="+", default=[
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ])
    parser.add_argument("--scales", type=int, nargs="+", default=[8, 32, 128])
    args = parser.parse_args()

    if abs(args.peer_lambda - 0.50) > 1e-9:
        raise SystemExit("directed peer-gain protocol fixes --peer-lambda=0.50")
    if tuple(args.scales) != (8, 32, 128):
        raise SystemExit("directed peer-gain protocol fixes scales 8,32,128")

    backend = local_dense_backend.resolve_dense_backend(args.dense_device)
    dense_device = backend.device
    cpu = torch.device("cpu")

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)

    train_examples = [base.Example(*row) for row in base.TRAIN_EXAMPLES]
    val_examples = [base.Example(*row) for row in base.VAL_EXAMPLES]
    examples = train_examples + val_examples
    for example in examples:
        example.mask = base._mask_for(example)
    train_indices = list(range(len(train_examples)))
    val_indices = list(range(len(train_examples), len(examples)))

    # Frozen encoders are intentionally kept on CPU in this first hybrid
    # prototype.  OpenVINO encoder offload can be layered independently later.
    encoders = base._prepare_encoders(args.models, examples, tuple(args.scales), device="cpu")
    spaces = v1._space_bank(encoders, train_indices, [example.mask for example in examples], tuple(args.scales))
    direct_fields = v1._fields_by_space(encoders, spaces, examples, cpu)
    translators = v1._fit_translators(encoders, spaces, train_indices)
    reconstruction = v1._reconstruction_report(encoders, spaces, translators, val_indices)

    matrix = base.row_normalise(base.load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    populations = base.select_populations(archive["superclass"])
    operator = base._csr_to_torch(matrix, device=cpu)
    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=cpu)
    whole_brain = torch.arange(matrix.shape[0], dtype=torch.int64, device=cpu)
    readout_projection = base._fixed_sparse_projection(
        args.readout_width, matrix.shape[0], seed=args.seed + 17, device=cpu
    )
    input_dim = int(sum(3 * space["dim"] for space in spaces))
    input_weights = torch.as_tensor(
        rng.normal(size=(len(populations.input_indices), input_dim)).astype(np.float32), device=cpu
    )

    positives = sum(float(examples[i].mask.sum()) for i in train_indices)
    total = sum(len(examples[i].mask) for i in train_indices)
    pos_weight = (total - positives) / max(positives, 1.0)

    scalar_weights, scalar_report = grid._training_reliability(
        spaces=spaces,
        direct_fields=direct_fields,
        train_indices=train_indices,
        examples=examples,
        pos_weight=pos_weight,
        device=cpu,
    )
    directed_weights, directed_report = directed._training_directed_reliability(
        spaces=spaces,
        direct_fields=direct_fields,
        train_indices=train_indices,
        examples=examples,
        device=cpu,
    )

    torch.manual_seed(args.seed + 9000)
    seed_model = v3.PerChannelAdapterFlavourBundle(
        [space["initial"] for space in spaces], args.readout_width, device=cpu
    )
    initial_state = deepcopy(seed_model.state_dict())

    common = dict(
        initial_state=initial_state,
        spaces=spaces,
        direct_fields=direct_fields,
        train_indices=train_indices,
        val_indices=val_indices,
        examples=examples,
        encoders=encoders,
        translators=translators,
        operator=operator,
        input_weights=input_weights,
        input_indices=input_indices,
        whole_brain=whole_brain,
        readout_projection=readout_projection,
        epochs=args.epochs,
        lr=args.lr,
        peer_lambda=args.peer_lambda,
        anchor_lambda=args.anchor_lambda,
        pos_weight=pos_weight,
        dense_device=dense_device,
    )
    independent = _train_arm(mode="independent", peer_weights=None, **common)
    scalar = _train_arm(mode="scalar_reliability_0.50", peer_weights=scalar_weights, **common)
    directed_run = _train_arm(mode="directed_reliability_0.50", peer_weights=directed_weights, **common)

    payload = {
        "schema": "papers/malecns-directed-peer-gains-local-hybrid-v1",
        "claim_status": "local hybrid backend prototype; establish backend parity before confirmatory use",
        "seed": args.seed,
        "models": args.models,
        "scales": list(args.scales),
        "peer_lambda": args.peer_lambda,
        "reservoir_device": "cpu",
        "encoder_device": "cpu",
        "dense_backend": backend.name,
        "dense_device_name": backend.device_name,
        "hybrid_rule": "CPU sparse MaleCNS; dense flavours/adapters/taste head on selected backend; autograd crosses device copies",
        "translation_reconstruction": reconstruction,
        "scalar_training_reliability": scalar_report,
        "directed_training_matrix": directed_report,
        "independent": independent,
        "coupled": {
            "scalar_reliability_0.50": scalar,
            "directed_reliability_0.50": directed_run,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "local_hybrid_complete", "output": str(args.output)}), flush=True)


if __name__ == "__main__":
    main()
