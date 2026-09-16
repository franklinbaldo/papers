"""GPU engineering smoke for whole-brain semantic flavour feedback.

This is deliberately non-confirmatory. It proves on the canonical MaleCNS graph
and feature cache that a fixed whole-brain projection can feed the disposable
taste head and that the auxiliary gradient reaches the flavourizer through the
frozen recurrent operator on CUDA. It must not be reported as Stage A/B evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from malecns_wifi import load_graph
from malecns_wifi.fly_assisted import FlyAssistSpec, make_model, training_loss
from malecns_wifi.multitag import MultitagSpec, build_flavours
from malecns_wifi.tagger import row_normalise, select_populations


def _torch():
    import torch

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required for this GPU smoke")
    return torch


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
    """Achlioptas-style fixed whole-state projection with ~1/sqrt(n) density."""
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


def _run_depth(*, depth, operator, features, masks, flavours, input_weights,
               input_indices, whole_brain, readout_projection, seed):
    torch = _torch()
    spec = FlyAssistSpec(
        rank=32,
        steps_per_chunk=depth,
        leak=0.4,
        gain=4.0,
        target_drive_rms=0.05,
        assist_weight=1.0,
    )
    model = make_model(
        features.shape[1], masks.shape[1], readout_projection.shape[0],
        flavours.shape[1], spec,
    ).to(features.device)

    # Production begins exactly at identity. The first auxiliary backward can
    # move the zero up-projection; after that one explicit update, a second
    # backward must reach the down-projection too. This proves the complete path
    # without pretending this two-step smoke is training.
    first = training_loss(
        model,
        features,
        masks,
        spec=spec,
        assist_lambda=1.0,
        operator=operator,
        input_weights=input_weights,
        input_indices=input_indices,
        readout_indices=whole_brain,
        readout_projection=readout_projection,
        flavours=flavours,
    )
    first["fly_loss"].backward()
    up_grad_1 = float(model.up.weight.grad.norm().detach().cpu())
    with torch.no_grad():
        model.up.weight -= 1e-2 * model.up.weight.grad
    model.zero_grad(set_to_none=True)

    second = training_loss(
        model,
        features,
        masks,
        spec=spec,
        assist_lambda=1.0,
        operator=operator,
        input_weights=input_weights,
        input_indices=input_indices,
        readout_indices=whole_brain,
        readout_projection=readout_projection,
        flavours=flavours,
    )
    second["fly_loss"].backward()
    up_grad_2 = float(model.up.weight.grad.norm().detach().cpu())
    down_grad_2 = float(model.down.weight.grad.norm().detach().cpu())

    for name, value in {
        "up_grad_first": up_grad_1,
        "up_grad_second": up_grad_2,
        "down_grad_second": down_grad_2,
    }.items():
        if not np.isfinite(value) or value <= 0:
            raise SystemExit(f"depth {depth}: invalid {name}={value}")

    return {
        "steps_per_chunk": depth,
        "fly_loss_first": float(first["fly_loss"].detach().cpu()),
        "fly_loss_second": float(second["fly_loss"].detach().cpu()),
        "drive_rms_first": float(first["drive_rms"].detach().cpu()),
        "drive_rms_second": float(second["drive_rms"].detach().cpu()),
        "up_grad_first": up_grad_1,
        "up_grad_second": up_grad_2,
        "down_grad_second": down_grad_2,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--depths", type=int, nargs="+", default=[4, 16])
    parser.add_argument("--readout-width", type=int, default=1314)
    args = parser.parse_args()

    torch = _torch()
    device = torch.device("cuda")
    stored = np.load(args.features, allow_pickle=False)
    block = np.hstack([stored["absolute"], stored["sensation"]]).astype(np.float32)
    groups = stored["groups"]
    masks_all = stored["tag_masks"].astype(np.float32)

    # Pick the real document with the most labelled chunks so the auxiliary target
    # is non-trivial while keeping this an engineering smoke over one document.
    documents = np.unique(groups)
    document = max(
        documents,
        key=lambda d: float(masks_all[groups == d].sum()),
    )
    rows = groups == document
    features = torch.as_tensor(block[rows], dtype=torch.float32, device=device)
    masks = torch.as_tensor(masks_all[rows], dtype=torch.float32, device=device)

    matrix = row_normalise(load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    operator = _csr_to_torch(matrix, device=device)
    neurons = int(matrix.shape[0])

    rng = np.random.default_rng(args.seed)
    input_weights = torch.as_tensor(
        rng.normal(size=(populations.input_indices.size, block.shape[1])).astype(np.float32),
        device=device,
    )
    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=device)
    whole_brain = torch.arange(neurons, dtype=torch.int64, device=device)
    readout_projection = _fixed_sparse_projection(
        args.readout_width, neurons, seed=args.seed + 4242, device=device
    )

    flavours_np = build_flavours(
        stored["tag_embeddings"],
        MultitagSpec(flavour_dimension=32, seeds=(args.seed,)),
        seed=args.seed,
        source="semantic",
    )
    flavours = torch.as_tensor(flavours_np, dtype=torch.float32, device=device)

    depth_rows = []
    for depth in args.depths:
        torch.cuda.empty_cache()
        depth_rows.append(_run_depth(
            depth=depth,
            operator=operator,
            features=features,
            masks=masks,
            flavours=flavours,
            input_weights=input_weights,
            input_indices=input_indices,
            whole_brain=whole_brain,
            readout_projection=readout_projection,
            seed=args.seed,
        ))

    payload = {
        "schema": "papers/malecns-wholebrain-gpu-smoke-v1",
        "claim_status": "engineering smoke only; not Stage A/B confirmatory evidence",
        "device": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "seed": args.seed,
        "document": int(document),
        "chunks": int(rows.sum()),
        "positive_tag_assignments": int(masks_all[rows].sum()),
        "neurons": neurons,
        "edges": int(matrix.nnz),
        "sensory_neurons": int(populations.input_indices.size),
        "descending_neurons": int(populations.readout_indices.size),
        "semantic_input_dim": int(block.shape[1]),
        "wholebrain_projection_width": int(args.readout_width),
        "wholebrain_projection_nnz": int(readout_projection._nnz()),
        "depths": depth_rows,
        "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
