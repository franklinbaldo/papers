"""Exploratory multi-epoch whole-brain flavour-learning curve on CUDA.

This is deliberately NOT Stage-B confirmatory evidence.  It asks the engineering
question that follows the real-GPU smoke: when a low-rank flavourizer receives
repeated gradients through the frozen complete MaleCNS recurrence, does the
auxiliary taste objective learn over many epochs, and does the standalone tagger
move differently from an identically initialized tag-only control?

The run uses one labelled document for training and a distinct labelled document
for evaluation, chosen deterministically as the two documents with the most tag
assignments.  That label-dependent choice is acceptable only for this exploratory
mechanism curve and is explicitly disallowed as confirmatory model selection.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from malecns_wifi import load_graph
from malecns_wifi.fly_assisted import (
    FlyAssistSpec,
    make_model,
    score_standalone,
    training_loss,
)
from malecns_wifi.multitag import MultitagSpec, build_flavours
from malecns_wifi.tagger import row_normalise, select_populations


def _torch():
    import torch

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is required for this learning-curve experiment")
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
    """Fixed Achlioptas-style whole-state projection, independent of labels."""
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


def _standalone_score(model, features, masks):
    torch = _torch()
    model.eval()
    with torch.no_grad():
        logits, residual = model.standalone_logits(features)
    score = score_standalone(
        logits.detach().cpu().numpy(), masks.detach().cpu().numpy()
    )
    ratio = (
        torch.linalg.vector_norm(residual, dim=1)
        / torch.linalg.vector_norm(features, dim=1).clamp_min(1e-12)
    ).mean()
    model.train()
    return {**score, "residual_ratio": float(ratio.detach().cpu())}


def _grad_norm(parameter) -> float:
    if parameter.grad is None:
        return 0.0
    return float(parameter.grad.norm().detach().cpu())


def _train_tag_only(*, model, features, masks, epochs: int, lr: float):
    torch = _torch()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    rows = []
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        result = training_loss(
            model, features, masks,
            spec=FlyAssistSpec(),
            assist_lambda=0.0,
        )
        result["loss"].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        rows.append({
            "epoch": epoch,
            "loss": float(result["loss"].detach().cpu()),
            "tag_loss": float(result["tag_loss"].detach().cpu()),
            "residual_ratio": float(result["residual_ratio"].detach().cpu()),
            "up_grad": _grad_norm(model.up.weight),
            "down_grad": _grad_norm(model.down.weight),
        })
        optimizer.step()
    return rows


def _train_assisted(
    *, model, features, masks, epochs: int, lr: float, depth: int,
    operator, input_weights, input_indices, whole_brain, readout_projection,
    flavours, eval_features, eval_masks, progress_path: Path,
):
    torch = _torch()
    spec = FlyAssistSpec(
        rank=32,
        steps_per_chunk=depth,
        leak=0.4,
        gain=4.0,
        target_drive_rms=0.05,
        assist_weight=1.0,
        assist_fraction=1.0,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    curve = []
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        result = training_loss(
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
        result["loss"].backward()
        preclip_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
        row = {
            "epoch": epoch,
            "loss": float(result["loss"].detach().cpu()),
            "tag_loss": float(result["tag_loss"].detach().cpu()),
            "fly_loss": float(result["fly_loss"].detach().cpu()),
            "residual_ratio": float(result["residual_ratio"].detach().cpu()),
            "drive_rms": float(result["drive_rms"].detach().cpu()),
            "up_grad": _grad_norm(model.up.weight),
            "down_grad": _grad_norm(model.down.weight),
            "preclip_grad_norm": preclip_norm,
        }
        optimizer.step()
        held = _standalone_score(model, eval_features, eval_masks)
        row["heldout"] = held
        curve.append(row)
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"depth": depth, **row}, sort_keys=True) + "\n")
        print(json.dumps({"event": "epoch", "depth": depth, **row}), flush=True)
    return curve


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--depths", type=int, nargs="+", default=[4, 16, 64])
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--readout-width", type=int, default=1314)
    args = parser.parse_args()

    torch = _torch()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda")

    stored = np.load(args.features, allow_pickle=False)
    block = np.hstack([stored["absolute"], stored["sensation"]]).astype(np.float32)
    groups = stored["groups"]
    masks_all = stored["tag_masks"].astype(np.float32)

    documents = np.unique(groups)
    ranked = sorted(
        documents,
        key=lambda d: (-float(masks_all[groups == d].sum()), int(d)),
    )
    if len(ranked) < 2:
        raise SystemExit("need at least two documents")
    train_document, eval_document = ranked[:2]
    train_rows = groups == train_document
    eval_rows = groups == eval_document

    features = torch.as_tensor(block[train_rows], dtype=torch.float32, device=device)
    masks = torch.as_tensor(masks_all[train_rows], dtype=torch.float32, device=device)
    eval_features = torch.as_tensor(block[eval_rows], dtype=torch.float32, device=device)
    eval_masks = torch.as_tensor(masks_all[eval_rows], dtype=torch.float32, device=device)

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

    # Train the tag-only comparator once from a deterministic initialization.
    base_spec = FlyAssistSpec(rank=32)
    torch.manual_seed(args.seed + 7000)
    base_model = make_model(
        block.shape[1], masks_all.shape[1], args.readout_width,
        flavours_np.shape[1], base_spec,
    ).to(device)
    initial = deepcopy(base_model.state_dict())

    tag_only = make_model(
        block.shape[1], masks_all.shape[1], args.readout_width,
        flavours_np.shape[1], base_spec,
    ).to(device)
    tag_only.load_state_dict(initial)
    tag_only_curve = _train_tag_only(
        model=tag_only, features=features, masks=masks, epochs=args.epochs, lr=args.lr
    )
    tag_only_heldout = _standalone_score(tag_only, eval_features, eval_masks)

    args.progress.parent.mkdir(parents=True, exist_ok=True)
    args.progress.write_text("", encoding="utf-8")
    depth_results = []
    for depth in args.depths:
        torch.cuda.empty_cache()
        model = make_model(
            block.shape[1], masks_all.shape[1], args.readout_width,
            flavours_np.shape[1], FlyAssistSpec(rank=32, steps_per_chunk=depth),
        ).to(device)
        model.load_state_dict(initial)
        curve = _train_assisted(
            model=model,
            features=features,
            masks=masks,
            epochs=args.epochs,
            lr=args.lr,
            depth=depth,
            operator=operator,
            input_weights=input_weights,
            input_indices=input_indices,
            whole_brain=whole_brain,
            readout_projection=readout_projection,
            flavours=flavours,
            eval_features=eval_features,
            eval_masks=eval_masks,
            progress_path=args.progress,
        )
        depth_results.append({
            "steps_per_chunk": depth,
            "curve": curve,
            "heldout_final": _standalone_score(model, eval_features, eval_masks),
        })
        del model

    payload = {
        "schema": "papers/malecns-wholebrain-flavour-learning-exploratory-v1",
        "claim_status": (
            "exploratory mechanism curve only; document selection is label-dependent; "
            "not Stage A/B confirmatory evidence"
        ),
        "device": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "seed": args.seed,
        "epochs": args.epochs,
        "learning_rate": args.lr,
        "depths_requested": args.depths,
        "train_document": int(train_document),
        "eval_document": int(eval_document),
        "train_chunks": int(train_rows.sum()),
        "eval_chunks": int(eval_rows.sum()),
        "train_positive_tag_assignments": int(masks_all[train_rows].sum()),
        "eval_positive_tag_assignments": int(masks_all[eval_rows].sum()),
        "document_selection": "top two by total tag assignments; exploratory only",
        "neurons": neurons,
        "edges": int(matrix.nnz),
        "sensory_neurons": int(populations.input_indices.size),
        "descending_neurons": int(populations.readout_indices.size),
        "semantic_input_dim": int(block.shape[1]),
        "wholebrain_projection_width": int(args.readout_width),
        "wholebrain_projection_nnz": int(readout_projection._nnz()),
        "tag_only_curve": tag_only_curve,
        "tag_only_heldout_final": tag_only_heldout,
        "assisted": depth_results,
        "max_cuda_memory_allocated": int(torch.cuda.max_memory_allocated()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "complete",
        "output": str(args.output),
        "train_document": int(train_document),
        "eval_document": int(eval_document),
        "tag_only_heldout": tag_only_heldout,
        "assisted_final": [
            {"depth": row["steps_per_chunk"], **row["heldout_final"]}
            for row in depth_results
        ],
        "max_cuda_memory_allocated": payload["max_cuda_memory_allocated"],
    }), flush=True)


if __name__ == "__main__":
    main()
