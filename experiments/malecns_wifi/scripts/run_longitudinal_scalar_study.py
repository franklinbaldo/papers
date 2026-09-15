"""Longitudinal study of channel dynamics: Independent vs Scalar Reliability.

Evaluates 6-12 seeds under two arms:
1. independent (peer_lambda = 0.0)
2. scalar_reliability (peer_lambda = 0.50, training-only scalar reliability r_j)

Logs longitudinal per-channel dynamics at every epoch (and pre-training baseline):
- Adapter norms (up, down) and flavour drift (delta norm, cosine to initial).
- Per-channel predictions p_c(t), receiver need n_c(t), sender competence q_c(t).
- Instantaneous empirical usefulness matrix U_{j->i}(t) and competence correlations.
- Per-channel validation AUPRC (unseen generalization, seen transfer, all).
- Whole-brain MaleCNS reservoir validation across arms.

No directed teaching arm is executed, preserving empirical neutrality until
longitudinal relationships are established.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import torch

# Ensure local scripts directory is importable
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import smoke_coupled_flavour_translation_gpu_v3 as v3  # installs per-channel adapter bundle
import smoke_coupled_flavour_translation_gpu as v1
import smoke_concept_flavour_gpu as base
import smoke_peer_reliability_grid_gpu as grid
from malecns_wifi.fast_spmv import csr_to_fast_operator


DEFAULT_SEEDS = (20261001, 20261002, 20261003, 20261004, 20261005, 20261006)


def _compute_channel_predictions(model, spaces, direct_fields, example_indices, examples, device):
    """Compute local channel probability p_c(t) and targets y(t) over given examples."""
    targets = []
    channel_probs = [[] for _ in spaces]
    was_training = model.training
    model.eval()

    with torch.no_grad():
        for example_index in example_indices:
            target = torch.as_tensor(
                examples[example_index].mask[:, 0], dtype=torch.float32, device=device
            )
            targets.append(target)
            for channel_index, space in enumerate(spaces):
                raw_field = direct_fields[example_index][channel_index]
                if hasattr(model, "adapt"):
                    field = model.adapt(channel_index, raw_field)
                else:
                    field = raw_field
                unit = field / torch.linalg.vector_norm(field, dim=1, keepdim=True).clamp_min(1e-12)
                flavour = model.flavour(channel_index)
                flavour = flavour / torch.linalg.vector_norm(flavour).clamp_min(1e-12)
                prob = torch.sigmoid(6.0 * (unit @ flavour))
                channel_probs[channel_index].append(prob)

    if was_training:
        model.train()

    y = torch.cat(targets).cpu().numpy()
    probs = np.stack([torch.cat(p).cpu().numpy() for p in channel_probs], axis=1)  # [T, C]
    return probs, y


def _channel_direct_auprc(probs, y, groups):
    """Compute AUPRC for each individual channel directly across group splits."""
    channel_scores = {}
    for c in range(probs.shape[1]):
        scores = probs[:, c]
        truth = y > 0
        perf = base._score_by_group(scores, truth, np.asarray(groups, dtype=object))
        channel_scores[c] = perf
    return channel_scores


def _record_longitudinal_snapshot(
    model, spaces, direct_fields, train_indices, val_indices, examples, device, pos_weight
) -> dict:
    """Record comprehensive state and empirical cross-channel statistics."""
    # 1. Parameter and drift metrics
    channels_info = []
    for index, space in enumerate(spaces):
        info = {
            "channel_index": index,
            "encoder": space["encoder"],
            "scale": int(space["scale"]),
            "delta_norm": float(model.delta[index].detach().norm().cpu()),
            "cosine_to_initial": float(
                base._cosine_np(model.flavour(index).detach().cpu().numpy(), space["initial"])
            ),
        }
        if hasattr(model, "channel_adapters"):
            adapter = model.channel_adapters[index]
            info["adapter_up_norm"] = float(adapter.up.weight.detach().norm().cpu())
            info["adapter_down_norm"] = float(adapter.down.weight.detach().norm().cpu())
            info["adapter_residual_scale"] = float(adapter.residual_scale)
        channels_info.append(info)

    # 2. Training bytes predictions & competence
    train_probs, train_y = _compute_channel_predictions(
        model, spaces, direct_fields, train_indices, examples, device
    )
    # Competence q = 1 - |y - p|, need n = |y - p|
    error = np.abs(train_y[:, None] - train_probs)  # [T, C]
    need = error
    competence = 1.0 - error

    # Channel-wise summary on training bytes
    for index in range(len(spaces)):
        p = train_probs[:, index]
        bce = -(train_y * np.log(np.clip(p, 1e-7, 1.0)) * pos_weight + (1.0 - train_y) * np.log(np.clip(1.0 - p, 1e-7, 1.0))).mean()
        acc = float(((p >= 0.5) == (train_y >= 0.5)).mean())
        channels_info[index]["train_mean_need"] = float(need[:, index].mean())
        channels_info[index]["train_mean_competence"] = float(competence[:, index].mean())
        channels_info[index]["train_bce"] = float(bce)
        channels_info[index]["train_acc"] = acc

    # 3. Empirical cross-channel usefulness matrix: U_{j -> i} = mean_t [ n_i(t) * q_j(t) ]
    count = len(spaces)
    raw_usefulness = np.zeros((count, count), dtype=np.float32)
    for i in range(count):
        for j in range(count):
            if i != j:
                raw_usefulness[i, j] = float(np.mean(need[:, i] * competence[:, j]))

    # Row-normalized usefulness (mean 1 over j != i)
    normalized_usefulness = np.zeros_like(raw_usefulness)
    for i in range(count):
        others = [j for j in range(count) if j != i]
        mean_row = raw_usefulness[i, others].mean()
        if mean_row > 1e-12:
            normalized_usefulness[i, others] = raw_usefulness[i, others] / mean_row

    # Channel competence correlation matrix
    competence_corr = np.corrcoef(competence.T)
    if np.isnan(competence_corr).any():
        competence_corr = np.nan_to_num(competence_corr, nan=0.0)

    # 4. Validation performance for individual direct channels
    val_groups = [examples[idx].group for idx in val_indices for _ in range(len(examples[idx].mask))]
    val_probs, val_y = _compute_channel_predictions(
        model, spaces, direct_fields, val_indices, examples, device
    )
    val_channel_auprc = _channel_direct_auprc(val_probs, val_y, val_groups)
    for index in range(len(spaces)):
        channels_info[index]["validation_direct"] = val_channel_auprc[index]

    return {
        "channels": channels_info,
        "empirical_usefulness_raw": raw_usefulness.tolist(),
        "empirical_usefulness_normalized": normalized_usefulness.tolist(),
        "competence_correlation": competence_corr.tolist(),
    }


def _run_single_arm(
    *,
    arm_name: str,
    peer_lambda: float,
    peer_loss_fn,
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
    epochs: int,
    lr: float,
    anchor_lambda: float,
    pos_weight: float,
    device: torch.device,
) -> dict:
    """Execute training for a single arm with step-by-step longitudinal tracking."""
    model = v1.FlavourBundle([space["initial"] for space in spaces], readout_projection.shape[0], device=device)
    model.load_state_dict(copy.deepcopy(initial_state))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    pos_weight_t = torch.tensor([pos_weight], dtype=torch.float32, device=device)

    # Baseline snapshot before any training (epoch -1)
    baseline_snapshot = _record_longitudinal_snapshot(
        model, spaces, direct_fields, train_indices, val_indices, examples, device, pos_weight
    )

    history = []
    for epoch in range(epochs):
        losses, taste_losses, peer_losses = [], [], []
        model.train()
        for example_index in train_indices:
            fields = [direct_fields[example_index][channel_index] for channel_index in range(len(spaces))]
            target = torch.as_tensor(examples[example_index].mask[:, 0:1], dtype=torch.float32, device=device)

            logits, rms = v1._reservoir_logits(
                model, fields, operator, input_weights, input_indices, whole_brain, readout_projection
            )
            taste_loss = torch.nn.functional.binary_cross_entropy_with_logits(
                logits[:, 0:1], target, pos_weight=pos_weight_t
            )
            anchor = torch.stack([delta.square().mean() for delta in model.delta]).mean()
            anchor_loss = anchor_lambda * anchor

            if peer_lambda > 0.0:
                p_loss = peer_loss_fn(model, fields, target, pos_weight_t)
                loss = taste_loss + peer_lambda * p_loss + anchor_loss
                peer_losses.append(float(p_loss.detach().cpu()))
            else:
                loss = taste_loss + anchor_loss
                peer_losses.append(0.0)

            losses.append(float(loss.detach().cpu()))
            taste_losses.append(float(taste_loss.detach().cpu()))

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        # Validation of whole-brain MaleCNS reservoir
        val_metrics = {}
        for eval_arm in ["all_direct", "no_128", "no_encoder_0", "no_encoder_1", "minilm_short_only"]:
            val_metrics[eval_arm] = v1._score_model(
                model,
                arm=eval_arm,
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
                device=device,
            )

        # Longitudinal snapshot at this epoch
        longitudinal_snapshot = _record_longitudinal_snapshot(
            model, spaces, direct_fields, train_indices, val_indices, examples, device, pos_weight
        )

        epoch_record = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "taste_bce": float(np.mean(taste_losses)),
            "peer_loss": float(np.mean(peer_losses)),
            "validation": val_metrics,
            "channel_dynamics": longitudinal_snapshot,
        }
        history.append(epoch_record)
        print(
            json.dumps({
                "event": "epoch_complete",
                "arm": arm_name,
                "epoch": epoch,
                "loss": epoch_record["loss"],
                "unseen_generalization": val_metrics["all_direct"]["unseen_generalization"],
                "all": val_metrics["all_direct"]["all"],
            }),
            flush=True,
        )

    return {
        "arm": arm_name,
        "peer_lambda": peer_lambda,
        "baseline": baseline_snapshot,
        "curve": history,
        "final_validation": history[-1]["validation"],
    }


def run_single_seed(
    *,
    seed: int,
    graph_path: Path,
    output_path: Path,
    epochs: int = 3,
    lr: float = 5e-4,
    peer_lambda: float = 0.50,
    anchor_lambda: float = 0.05,
    readout_width: int = 128,
    scales: tuple[int, ...] = (8, 32, 128),
    models: list[str] = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ),
) -> dict:
    """Run independent vs scalar reliability for one seed and save results."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_examples = [base.Example(*row) for row in base.TRAIN_EXAMPLES]
    val_examples = [base.Example(*row) for row in base.VAL_EXAMPLES]
    examples = train_examples + val_examples
    for example in examples:
        example.mask = base._mask_for(example)
    train_indices = list(range(len(train_examples)))
    val_indices = list(range(len(train_examples), len(examples)))

    # Fast cached encoders
    encoders = base._prepare_encoders(list(models), examples, scales, device=str(device))
    spaces = v1._space_bank(encoders, train_indices, [example.mask for example in examples], scales)
    direct_fields = v1._fields_by_space(encoders, spaces, examples, device)
    translators = v1._fit_translators(encoders, spaces, train_indices)

    # Fast sparse operator with cached transpose
    matrix = base.row_normalise(base.load_graph(graph_path))
    archive = np.load(graph_path, allow_pickle=False)
    populations = base.select_populations(archive["superclass"])
    operator = csr_to_fast_operator(matrix, device=device)

    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=device)
    whole_brain = torch.arange(matrix.shape[0], dtype=torch.int64, device=device)
    readout_projection = base._fixed_sparse_projection(
        readout_width, matrix.shape[0], seed=seed + 17, device=device
    )
    input_dim = int(sum(3 * space["dim"] for space in spaces))
    input_weights = torch.as_tensor(
        rng.normal(size=(len(populations.input_indices), input_dim)).astype(np.float32), device=device
    )

    pos = sum(float(example.mask[:, 0].sum()) for example in train_examples)
    total = sum(float(len(example.mask)) for example in train_examples)
    pos_weight = (total - pos) / max(pos, 1.0)

    # Shared initial state across arms
    flavour_bundle = v1.FlavourBundle([space["initial"] for space in spaces], readout_projection.shape[0], device=device)
    initial_state = copy.deepcopy(flavour_bundle.state_dict())

    # Pre-training scalar reliability weights
    scalar_weights, reliability_report = grid._training_reliability(
        spaces=spaces, direct_fields=direct_fields, train_indices=train_indices,
        examples=examples, pos_weight=pos_weight, device=device
    )

    def scalar_peer_loss_fn(m, f, tgt, pw):
        grid._PEER_WEIGHTS = scalar_weights
        return grid._weighted_peer_loss(m, f, tgt, pw)

    print(json.dumps({"event": "seed_start", "seed": seed, "device": str(device)}), flush=True)

    # Arm 1: Independent (peer_lambda = 0.0)
    independent_run = _run_single_arm(
        arm_name="independent",
        peer_lambda=0.0,
        peer_loss_fn=None,
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
        epochs=epochs,
        lr=lr,
        anchor_lambda=anchor_lambda,
        pos_weight=pos_weight,
        device=device,
    )

    # Arm 2: Scalar Reliability (peer_lambda = 0.50)
    scalar_run = _run_single_arm(
        arm_name="scalar_reliability",
        peer_lambda=peer_lambda,
        peer_loss_fn=scalar_peer_loss_fn,
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
        epochs=epochs,
        lr=lr,
        anchor_lambda=anchor_lambda,
        pos_weight=pos_weight,
        device=device,
    )

    ind_unseen = independent_run["final_validation"]["all_direct"]["unseen_generalization"]
    ind_all = independent_run["final_validation"]["all_direct"]["all"]
    sca_unseen = scalar_run["final_validation"]["all_direct"]["unseen_generalization"]
    sca_all = scalar_run["final_validation"]["all_direct"]["all"]

    payload = {
        "schema": "papers/malecns-longitudinal-scalar-single-v1",
        "seed": seed,
        "device": str(device),
        "epochs": epochs,
        "lr": lr,
        "peer_lambda": peer_lambda,
        "anchor_lambda": anchor_lambda,
        "readout_width": readout_width,
        "fixed_training_reliability": reliability_report,
        "comparison": {
            "independent_all": ind_all,
            "independent_unseen": ind_unseen,
            "scalar_all": sca_all,
            "scalar_unseen": sca_unseen,
            "scalar_minus_independent_unseen": sca_unseen - ind_unseen,
            "scalar_minus_independent_all": sca_all - ind_all,
        },
        "independent": independent_run,
        "scalar_reliability": scalar_run,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "seed_complete", "seed": seed, "comparison": payload["comparison"]}), flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=Path("artifacts/inputs/graph.npz"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/longitudinal-scalar-study"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--peer-lambda", type=float, default=0.50)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in args.seeds:
        seed_out = args.output_dir / f"seed-{seed}.json"
        res = run_single_seed(
            seed=seed,
            graph_path=args.graph,
            output_path=seed_out,
            epochs=args.epochs,
            lr=args.lr,
            peer_lambda=args.peer_lambda,
            anchor_lambda=args.anchor_lambda,
            readout_width=args.readout_width,
        )
        results.append(res)

    # Consolidated summary
    comparisons = [r["comparison"] for r in results]
    mean_scalar_gain_unseen = float(np.mean([c["scalar_minus_independent_unseen"] for c in comparisons]))
    mean_scalar_gain_all = float(np.mean([c["scalar_minus_independent_all"] for c in comparisons]))

    summary = {
        "schema": "papers/malecns-longitudinal-scalar-batch-v1",
        "claim_status": "longitudinal empirical channel dynamics and scalar reliability comparison",
        "seeds": args.seeds,
        "n_seeds": len(args.seeds),
        "peer_lambda": args.peer_lambda,
        "comparisons": comparisons,
        "mean_scalar_minus_independent_unseen": mean_scalar_gain_unseen,
        "mean_scalar_minus_independent_all": mean_scalar_gain_all,
    }

    summary_file = args.output_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "longitudinal_scalar_study_complete", "summary": summary}), flush=True)


if __name__ == "__main__":
    main()
