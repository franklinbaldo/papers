"""Topology vs Weight Ablation Study: Does MaleCNS need continuous synaptic magnitudes?

Evaluates 5 graph representation arms on the CausaGanha legal concept categorization task:
1. continuous_fp32: Full continuous synaptic weights (canonical control).
2. binary_unweighted: Naked wiring (+1/-1 signed unit weights, row-normalised).
   Answers: "Does the reservoir only need the topological connectivity?"
3. shuffled_weights: True weights randomly permuted across the fixed topological edges.
   Answers: "Do weight magnitudes carry specific biological placement information,
   or is it just the degree distribution?"
4. log_16_categories: 4-bit logarithmic codebook (16 discrete categories).
5. log_32_categories: 5-bit logarithmic codebook (32 discrete categories).

Each arm trains the exact same channel adapters + flavours + whole-brain MaleCNS reservoir
for 3 epochs, evaluated on held-out unseen generalization AUPRC.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import torch

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import smoke_coupled_flavour_translation_gpu_v3 as v3
import smoke_coupled_flavour_translation_gpu as v1
import smoke_concept_flavour_gpu as base
from malecns_wifi.fast_spmv import csr_to_fast_operator


DEFAULT_SEEDS = (20261001, 20261002, 20261003, 20261004, 20261005, 20261006)
ARMS = (
    "continuous_fp32",
    "binary_unweighted",
    "shuffled_weights",
    "log_16_categories",
    "log_32_categories",
)


def categorize_weights_log(weights: np.ndarray, n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    """Bin weights into logarithmically spaced bins, matching biological scaling."""
    signs = np.sign(weights)
    abs_w = np.abs(weights)
    min_val = max(float(abs_w.min()), 1.0)
    max_val = float(abs_w.max())
    log_edges = np.geomspace(min_val, max_val, n_bins + 1)
    bin_ids = np.clip(np.digitize(abs_w, log_edges[1:-1]), 0, n_bins - 1)
    centroids = np.zeros(n_bins, dtype=np.float32)
    for b in range(n_bins):
        mask = (bin_ids == b)
        if mask.any():
            centroids[b] = float(np.mean(abs_w[mask]))
        else:
            centroids[b] = float(np.sqrt(log_edges[b] * log_edges[b + 1]))
    reconstructed = signs * centroids[bin_ids]
    return reconstructed, centroids


def build_variant_matrix(raw_mat: sp.csr_matrix, arm: str, *, seed: int) -> sp.csr_matrix:
    """Construct the sparse matrix variant for the given arm and row-normalise."""
    mat = raw_mat.copy().astype(np.float32)
    if arm == "continuous_fp32":
        pass
    elif arm == "binary_unweighted":
        mat.data = np.sign(mat.data).astype(np.float32)
    elif arm == "shuffled_weights":
        rng = np.random.default_rng(seed + 999)
        mat.data = rng.permutation(mat.data).astype(np.float32)
    elif arm == "log_16_categories":
        cat_data, _ = categorize_weights_log(mat.data, 16)
        mat.data = cat_data.astype(np.float32)
    elif arm == "log_32_categories":
        cat_data, _ = categorize_weights_log(mat.data, 32)
        mat.data = cat_data.astype(np.float32)
    else:
        raise ValueError(f"Unknown arm: {arm}")

    # Row normalisation: D^-1 * W
    in_strength = np.asarray(np.abs(mat).sum(axis=1)).ravel()
    scale = (1.0 / np.maximum(in_strength, 1.0)).astype(np.float32)
    mat.data *= np.repeat(scale, np.diff(mat.indptr))
    return mat


def _train_arm(
    *,
    arm_name: str,
    operator,
    initial_state,
    spaces,
    direct_fields,
    train_indices,
    val_indices,
    examples,
    encoders,
    translators,
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
    model = v1.FlavourBundle([space["initial"] for space in spaces], readout_projection.shape[0], device=device)
    model.load_state_dict(copy.deepcopy(initial_state))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    pos_weight_t = torch.tensor([pos_weight], dtype=torch.float32, device=device)

    curve = []
    for epoch in range(epochs):
        losses = []
        model.train()
        for example_index in train_indices:
            fields = [direct_fields[example_index][c] for c in range(len(spaces))]
            target = torch.as_tensor(examples[example_index].mask[:, 0:1], dtype=torch.float32, device=device)

            logits, rms = v1._reservoir_logits(
                model, fields, operator, input_weights, input_indices, whole_brain, readout_projection
            )
            taste_loss = torch.nn.functional.binary_cross_entropy_with_logits(
                logits[:, 0:1], target, pos_weight=pos_weight_t
            )
            anchor = torch.stack([delta.square().mean() for delta in model.delta]).mean()
            loss = taste_loss + anchor_lambda * anchor
            losses.append(float(loss.detach().cpu()))

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

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

        curve.append({
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "validation": val_metrics,
        })
        print(
            json.dumps({
                "event": "ablation_epoch_complete",
                "arm": arm_name,
                "epoch": epoch,
                "unseen_generalization": val_metrics["all_direct"]["unseen_generalization"],
                "all": val_metrics["all_direct"]["all"],
            }),
            flush=True,
        )

    return {
        "arm": arm_name,
        "curve": curve,
        "final_validation": curve[-1]["validation"],
    }


def run_seed_ablation(
    *,
    seed: int,
    graph_path: Path,
    output_path: Path,
    epochs: int = 3,
    lr: float = 5e-4,
    anchor_lambda: float = 0.05,
    readout_width: int = 128,
    scales: tuple[int, ...] = (8, 32, 128),
    models: list[str] = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-small",
    ),
) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_examples = [base.Example(*row) for row in base.TRAIN_EXAMPLES]
    val_examples = [base.Example(*row) for row in base.VAL_EXAMPLES]
    examples = train_examples + val_examples
    for ex in examples:
        ex.mask = base._mask_for(ex)
    train_indices = list(range(len(train_examples)))
    val_indices = list(range(len(train_examples), len(examples)))

    encoders = base._prepare_encoders(list(models), examples, scales, device=str(device))
    spaces = v1._space_bank(encoders, train_indices, [ex.mask for ex in examples], scales)
    direct_fields = v1._fields_by_space(encoders, spaces, examples, device)
    translators = v1._fit_translators(encoders, spaces, train_indices)

    raw_mat = base.load_graph(graph_path)
    archive = np.load(graph_path, allow_pickle=False)
    populations = base.select_populations(archive["superclass"])

    input_indices = torch.as_tensor(populations.input_indices, dtype=torch.int64, device=device)
    whole_brain = torch.arange(raw_mat.shape[0], dtype=torch.int64, device=device)
    readout_projection = base._fixed_sparse_projection(
        readout_width, raw_mat.shape[0], seed=seed + 17, device=device
    )
    input_dim = int(sum(3 * space["dim"] for space in spaces))
    input_weights = torch.as_tensor(
        rng.normal(size=(len(populations.input_indices), input_dim)).astype(np.float32), device=device
    )

    pos = sum(float(ex.mask[:, 0].sum()) for ex in train_examples)
    total = sum(float(len(ex.mask)) for ex in train_examples)
    pos_weight = (total - pos) / max(pos, 1.0)

    # Identical initial state across arms
    flavour_bundle = v1.FlavourBundle([space["initial"] for space in spaces], readout_projection.shape[0], device=device)
    initial_state = copy.deepcopy(flavour_bundle.state_dict())

    print(json.dumps({"event": "ablation_seed_start", "seed": seed, "arms": list(ARMS)}), flush=True)

    arm_results = {}
    for arm_name in ARMS:
        print(json.dumps({"event": "ablation_arm_start", "seed": seed, "arm": arm_name}), flush=True)
        variant_mat = build_variant_matrix(raw_mat, arm_name, seed=seed)
        operator = csr_to_fast_operator(variant_mat, device=device)

        res = _train_arm(
            arm_name=arm_name,
            operator=operator,
            initial_state=initial_state,
            spaces=spaces,
            direct_fields=direct_fields,
            train_indices=train_indices,
            val_indices=val_indices,
            examples=examples,
            encoders=encoders,
            translators=translators,
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
        arm_results[arm_name] = res

    # Summary comparisons against continuous_fp32 control
    control_unseen = arm_results["continuous_fp32"]["final_validation"]["all_direct"]["unseen_generalization"]
    control_all = arm_results["continuous_fp32"]["final_validation"]["all_direct"]["all"]

    comparisons = {}
    for arm_name in ARMS:
        u = arm_results[arm_name]["final_validation"]["all_direct"]["unseen_generalization"]
        a = arm_results[arm_name]["final_validation"]["all_direct"]["all"]
        comparisons[arm_name] = {
            "unseen_generalization": u,
            "all": a,
            "delta_unseen_vs_control": u - control_unseen,
            "delta_all_vs_control": a - control_all,
        }

    payload = {
        "schema": "papers/malecns-topology-weight-ablation-single-v1",
        "seed": seed,
        "device": str(device),
        "epochs": epochs,
        "lr": lr,
        "anchor_lambda": anchor_lambda,
        "readout_width": readout_width,
        "arms": list(ARMS),
        "comparisons": comparisons,
        "runs": arm_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "ablation_seed_complete", "seed": seed, "comparisons": comparisons}), flush=True)
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=Path("artifacts/inputs/graph.npz"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/topology-weight-ablation"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    parser.add_argument("--threads", type=int, default=3, help="Max threads to allow parallel run with task-700")
    args = parser.parse_args()

    torch.set_num_threads(args.threads)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for seed in args.seeds:
        seed_out = args.output_dir / f"seed-{seed}.json"
        res = run_seed_ablation(
            seed=seed,
            graph_path=args.graph,
            output_path=seed_out,
            epochs=args.epochs,
            lr=args.lr,
            anchor_lambda=args.anchor_lambda,
            readout_width=args.readout_width,
        )
        results.append(res)

    # Consolidated across seeds
    summary_by_arm = {}
    for arm_name in ARMS:
        unseens = [r["comparisons"][arm_name]["unseen_generalization"] for r in results]
        alls = [r["comparisons"][arm_name]["all"] for r in results]
        deltas_u = [r["comparisons"][arm_name]["delta_unseen_vs_control"] for r in results]
        deltas_a = [r["comparisons"][arm_name]["delta_all_vs_control"] for r in results]
        summary_by_arm[arm_name] = {
            "mean_unseen": float(np.mean(unseens)),
            "std_unseen": float(np.std(unseens)),
            "mean_all": float(np.mean(alls)),
            "std_all": float(np.std(alls)),
            "mean_delta_unseen_vs_control": float(np.mean(deltas_u)),
            "mean_delta_all_vs_control": float(np.mean(deltas_a)),
        }

    summary = {
        "schema": "papers/malecns-topology-weight-ablation-batch-v1",
        "claim_status": "empirical topology vs weight ablation on CausaGanha task",
        "seeds": args.seeds,
        "n_seeds": len(args.seeds),
        "arms": list(ARMS),
        "summary_by_arm": summary_by_arm,
    }
    summary_file = args.output_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "ablation_batch_complete", "summary_by_arm": summary_by_arm}), flush=True)


if __name__ == "__main__":
    main()
