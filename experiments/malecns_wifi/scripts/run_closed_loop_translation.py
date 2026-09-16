"""Closed-loop embedding translation through a frozen MaleCNS operator.

Runs the arms that decide the question, under one shared set of frozen
embeddings, one shared split and one shared interface budget:

* ``direct_lowrank``   -- A -> low-rank adapter -> B. No substrate at all.
* ``mlp``              -- A -> small MLP -> B. Parameter-matched-ish comparator.
* ``malecns_open``     -- adapter_in -> MaleCNS -> adapter_out, feedback disabled.
* ``malecns_closed``   -- the same, with the error fed back into the same state.
* ``degree_null_closed``  -- closed loop on a directed configuration model.
* ``random_esn_closed``   -- closed loop on a random operator, matched density
  and weight multiset.

Every substrate arm shares byte-identical ports, readout and hyperparameters, so
an arm difference is a topology difference. The only variable is the operator.

Usage::

    python scripts/run_closed_loop_translation.py \\
        --graph artifacts/runtime-v1/graph.npz \\
        --cache artifacts/translation/minilm-e5.npz \\
        --output artifacts/closed-loop-translation.json
"""

from __future__ import annotations

import argparse
import json
import time
from copy import deepcopy
from pathlib import Path

import numpy as np
import torch

from malecns_wifi.characterize import degree_preserving_null, random_esn
from malecns_wifi.closed_loop_translation import (
    FeedbackMode,
    TranslationSpec,
    build_substrate,
    make_low_rank_adapter,
    make_mlp,
    protocol_dict,
    round_loss,
    run_loop,
    select_ports,
    unit_rows,
)
from malecns_wifi.runtime import load_graph
from malecns_wifi.tagger import row_normalise
from malecns_wifi.translation_metrics import (
    centroid_baseline,
    score_prediction,
    score_trajectory,
)
from malecns_wifi.translation_pairs import load_cache, split_indices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--inner-steps", type=int, default=2)
    parser.add_argument("--drive-dim", type=int, default=128)
    parser.add_argument("--readout-width", type=int, default=512)
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--gain", type=float, default=0.95,
                        help="only used when --gain-mode fixed")
    parser.add_argument("--gain-mode", default="matched_bulk",
                        choices=["matched_bulk", "fixed"],
                        help="matched_bulk puts every operator at the same bulk operating "
                             "point, so an arm difference is topology and not dynamic range")
    parser.add_argument("--bulk-target", type=float, default=0.9)
    parser.add_argument("--drive-rms", type=float, default=0.5)
    parser.add_argument("--mlp-hidden", type=int, default=64)
    parser.add_argument("--objective", default="infonce", choices=["infonce", "cosine"],
                        help="infonce is the default because plain cosine collapses onto "
                             "the target centroid in an anisotropic embedding space")
    parser.add_argument("--temperature", type=float, default=0.05)
    parser.add_argument(
        "--feedback-modes", nargs="+", default=["scalar", "full"],
        help="closed-loop feedback channels to run; scalar cannot carry the target",
    )
    parser.add_argument(
        "--arms", nargs="+",
        default=[
            "direct_lowrank", "mlp", "malecns_open", "malecns_closed",
            "degree_null_closed", "random_esn_closed",
        ],
    )
    parser.add_argument("--device", default="cpu")
    return parser.parse_args()


def make_spec(args: argparse.Namespace, mode: FeedbackMode) -> TranslationSpec:
    return TranslationSpec(
        rank=args.rank,
        rounds=args.rounds,
        inner_steps=args.inner_steps,
        drive_dim=args.drive_dim,
        readout_width=args.readout_width,
        leak=args.leak,
        gain=args.gain,
        target_drive_rms=args.drive_rms,
        feedback_drive_rms=args.drive_rms,
        feedback_mode=mode,
        objective=args.objective,
        temperature=args.temperature,
    )


def batches(indices: np.ndarray, size: int, rng: np.random.Generator):
    order = rng.permutation(indices)
    for start in range(0, len(order), size):
        chunk = order[start:start + size]
        if len(chunk):
            yield chunk


def evaluate_direct(model, source, target, indices, *, seed: int) -> dict:
    with torch.no_grad():
        predicted = unit_rows(model(unit_rows(source[indices]))).cpu().numpy()
    return score_prediction(predicted, target[indices].cpu().numpy(), seed=seed)


def train_direct(
    model, *, source, target, train_idx, val_idx, args, rng, label: str
) -> dict:
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    curve = []
    started = time.perf_counter()
    for epoch in range(args.epochs):
        losses = []
        for chunk in batches(train_idx, args.batch_size, rng):
            optimizer.zero_grad(set_to_none=True)
            predicted = unit_rows(model(unit_rows(source[chunk])))
            chunk_target = unit_rows(target[chunk])
            if args.objective == "cosine":
                loss = (1.0 - (predicted * chunk_target).sum(dim=-1)).mean()
            else:
                logits = (predicted @ chunk_target.T) / args.temperature
                loss = torch.nn.functional.cross_entropy(
                    logits, torch.arange(logits.shape[0], device=logits.device)
                )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
        row = {
            "epoch": epoch,
            "train_loss": float(np.mean(losses)),
            "val": evaluate_direct(model, source, target, val_idx, seed=args.seed),
        }
        print(json.dumps({"event": "epoch", "arm": label, **row}), flush=True)
        curve.append(row)
    return {"curve": curve, "seconds": time.perf_counter() - started}


def evaluate_loop(model, substrate, spec, source, target, indices, *, seed: int,
                  batch_size: int) -> dict:
    model.eval()
    collected: list[list[np.ndarray]] = [[] for _ in range(spec.rounds)]
    diagnostics = None
    with torch.no_grad():
        for start in range(0, len(indices), batch_size):
            chunk = indices[start:start + batch_size]
            predictions, diagnostics = run_loop(
                model, substrate, source[chunk], target[chunk], spec
            )
            for index, prediction in enumerate(predictions):
                collected[index].append(prediction.cpu().numpy())
    model.train()
    stacked = [np.concatenate(rows, axis=0) for rows in collected]
    result = score_trajectory(stacked, target[indices].cpu().numpy(), seed=seed)
    result["last_batch_diagnostics"] = diagnostics
    return result


def train_loop_arm(
    model, substrate, spec, *, source, target, train_idx, val_idx, args, rng, label: str
) -> dict:
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    curve = []
    started = time.perf_counter()
    for epoch in range(args.epochs):
        losses, round_losses, grad_norms = [], [], []
        for chunk in batches(train_idx, args.batch_size, rng):
            optimizer.zero_grad(set_to_none=True)
            predictions, _ = run_loop(model, substrate, source[chunk], target[chunk], spec)
            loss, per_round = round_loss(predictions, target[chunk], spec)
            loss.backward()
            grad_norms.append(
                float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).detach().cpu())
            )
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
            round_losses.append([float(item.detach().cpu()) for item in per_round])
        validation = evaluate_loop(
            model, substrate, spec, source, target, val_idx,
            seed=args.seed, batch_size=args.batch_size,
        )
        row = {
            "epoch": epoch,
            "train_loss": float(np.mean(losses)),
            "train_round_loss": np.mean(np.asarray(round_losses), axis=0).tolist(),
            "preclip_grad_norm_mean": float(np.mean(grad_norms)),
            "val_cosine_by_round": [item["mean_cosine"] for item in validation["rounds"]],
            "val_retrieval@1_final": validation["final"]["retrieval@1"],
        }
        print(json.dumps({"event": "epoch", "arm": label, **row}), flush=True)
        curve.append(row)
    return {"curve": curve, "seconds": time.perf_counter() - started}


def gradient_audit(model, substrate, spec, source, target) -> dict:
    """Confirm the gradient reaches every adapter and touches nothing frozen.

    This is the engineering smoke the protocol asks for, run inside the
    experiment rather than asserted in prose: if ``adapter_in`` had no gradient
    the loop would still train, silently, on ``adapter_out`` alone.
    """
    model.zero_grad(set_to_none=True)
    predictions, _ = run_loop(model, substrate, source[:4], target[:4], spec)
    loss, _ = round_loss(predictions, target[:4], spec)
    loss.backward()
    report = {}
    for name, parameter in model.named_parameters():
        gradient = parameter.grad
        report[name] = {
            "requires_grad": bool(parameter.requires_grad),
            "grad_norm": None if gradient is None else float(gradient.norm().cpu()),
            "finite": None if gradient is None else bool(torch.isfinite(gradient).all()),
        }
    frozen = {
        "operator_requires_grad": bool(substrate.operator.requires_grad),
        "operator_t_requires_grad": bool(substrate.operator_t.requires_grad),
        "input_weights_requires_grad": bool(substrate.input_weights.requires_grad),
        "feedback_weights_requires_grad": bool(substrate.feedback_weights.requires_grad),
        "readout_requires_grad": bool(substrate.readout_projection.requires_grad),
    }
    model.zero_grad(set_to_none=True)
    reached = [name for name, item in report.items() if (item["grad_norm"] or 0.0) > 0.0]
    return {
        "parameters": report,
        "frozen_tensors": frozen,
        "adapters_reached_by_gradient": sorted({name.split(".")[0] for name in reached}),
        "all_gradients_finite": all(
            item["finite"] is not False for item in report.values()
        ),
        "any_frozen_tensor_trainable": any(frozen.values()),
    }


def state_persistence_audit(model, substrate, spec, source, target) -> dict:
    """Show that round t+1 depends on round t, and that feedback changes it.

    Two facts have to hold for the word "closed loop" to be earned: the state is
    not reset between rounds, and the feedback actually perturbs the trajectory.
    The second is checked by re-running with the feedback code scaled to zero and
    confirming the later rounds move.
    """
    with torch.no_grad():
        predictions, diagnostics = run_loop(model, substrate, source[:8], target[:8], spec)
        open_spec = TranslationSpec(
            **{**{key: getattr(spec, key) for key in spec.__dataclass_fields__},
               "feedback_mode": FeedbackMode.NONE}
        )
        open_predictions, _ = run_loop(model, substrate, source[:8], target[:8], open_spec)
    deltas = [
        float((closed - opened).norm().cpu())
        for closed, opened in zip(predictions, open_predictions, strict=True)
    ]
    return {
        "state_rms_by_round": [item["state_rms"] for item in diagnostics],
        "state_changes_between_rounds": bool(
            len({round(item["state_rms"], 9) for item in diagnostics}) > 1
        ),
        "closed_minus_open_prediction_norm_by_round": deltas,
        "feedback_alters_later_rounds": bool(len(deltas) > 1 and max(deltas[1:]) > 1e-6),
        "round_0_identical_without_feedback": bool(deltas[0] < 1e-6),
    }


def main() -> None:
    args = parse_args()
    device = torch.device(args.device)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)

    source_np, target_np, texts, groups_np, cache_manifest = load_cache(args.cache)
    if args.limit and args.limit < len(texts):
        keep = np.sort(np.random.default_rng(args.seed).choice(
            len(texts), size=args.limit, replace=False
        ))
        source_np, target_np = source_np[keep], target_np[keep]
        groups_np = groups_np[keep]
        texts = [texts[index] for index in keep]
    train_idx, val_idx, test_idx = split_indices(
        len(texts), seed=args.seed, groups=groups_np
    )
    source = torch.as_tensor(source_np, dtype=torch.float32, device=device)
    target = torch.as_tensor(target_np, dtype=torch.float32, device=device)
    source_dim, target_dim = source.shape[1], target.shape[1]

    matrix = row_normalise(load_graph(args.graph))
    archive = np.load(args.graph, allow_pickle=False)
    neurons = int(matrix.shape[0])
    input_indices, feedback_indices, port_report = select_ports(
        archive["superclass"], neurons=neurons, seed=args.seed + 101
    )

    operators = {"malecns": (matrix, {"kind": "MaleCNS v1.0 compiled operator"})}
    if "degree_null_closed" in args.arms:
        null, stats = degree_preserving_null(matrix, seed=args.seed + 7)
        operators["degree_null"] = (null, stats)
    if "random_esn_closed" in args.arms:
        esn, stats = random_esn(matrix, seed=args.seed + 13)
        operators["random_esn"] = (esn, stats)

    # Reference points that cost nothing and without which the numbers below are
    # not interpretable: what the target centroid scores, and what an ordinary
    # closed-form linear map scores on the same split.
    references = {}
    for split_name, split_idx in (("val", val_idx), ("test", test_idx)):
        references.setdefault("centroid", {})[split_name] = centroid_baseline(
            target_np[split_idx], seed=args.seed
        )
    fitted, *_ = np.linalg.lstsq(
        source_np[train_idx] / np.maximum(
            np.linalg.norm(source_np[train_idx], axis=1, keepdims=True), 1e-12),
        target_np[train_idx], rcond=None,
    )
    for split_name, split_idx in (("val", val_idx), ("test", test_idx)):
        unit_source = source_np[split_idx] / np.maximum(
            np.linalg.norm(source_np[split_idx], axis=1, keepdims=True), 1e-12)
        references.setdefault("least_squares_linear", {})[split_name] = score_prediction(
            unit_source @ fitted, target_np[split_idx], seed=args.seed
        )
    print(json.dumps({"event": "references", **{
        key: {"test_mean_cosine": value["test"]["mean_cosine"],
              "test_retrieval@1": value["test"]["retrieval@1"]}
        for key, value in references.items()}}), flush=True)

    results: dict = {}
    audits: dict = {}
    substrate_reports: dict = {}

    # Baselines without any substrate. Same loss, same split, same optimiser.
    if "direct_lowrank" in args.arms:
        torch.manual_seed(args.seed + 1)
        model = make_low_rank_adapter(
            source_dim, target_dim, rank=args.rank, nonlinearity="tanh"
        ).to(device)
        history = train_direct(
            model, source=source, target=target, train_idx=train_idx,
            val_idx=val_idx, args=args, rng=rng, label="direct_lowrank",
        )
        results["direct_lowrank"] = {
            "model": model.describe(),
            "history": history,
            "val": evaluate_direct(model, source, target, val_idx, seed=args.seed),
            "test": evaluate_direct(model, source, target, test_idx, seed=args.seed),
        }

    if "mlp" in args.arms:
        torch.manual_seed(args.seed + 2)
        model = make_mlp(source_dim, target_dim, hidden=args.mlp_hidden).to(device)
        history = train_direct(
            model, source=source, target=target, train_idx=train_idx,
            val_idx=val_idx, args=args, rng=rng, label="mlp",
        )
        results["mlp"] = {
            "model": model.describe(),
            "history": history,
            "val": evaluate_direct(model, source, target, val_idx, seed=args.seed),
            "test": evaluate_direct(model, source, target, test_idx, seed=args.seed),
        }

    substrate_arms = [
        ("malecns_open", "malecns", FeedbackMode.NONE),
        ("malecns_closed", "malecns", None),
        ("degree_null_closed", "degree_null", None),
        ("random_esn_closed", "random_esn", None),
    ]
    modes = [FeedbackMode(value) for value in args.feedback_modes]

    for arm, operator_key, fixed_mode in substrate_arms:
        if arm not in args.arms:
            continue
        operator_matrix, operator_stats = operators[operator_key]
        arm_modes = [fixed_mode] if fixed_mode is not None else modes
        for mode in arm_modes:
            spec = make_spec(args, mode)
            label = arm if fixed_mode is not None else f"{arm}[{mode.value}]"
            substrate = build_substrate(
                operator_matrix, name=operator_key, spec=spec,
                input_indices=input_indices, feedback_indices=feedback_indices,
                seed=args.seed + 101, device=device, stats=operator_stats,
                gain_mode=args.gain_mode, bulk_target=args.bulk_target,
            )
            substrate_reports[operator_key] = substrate.describe()

            torch.manual_seed(args.seed + 3)
            from malecns_wifi.closed_loop_translation import make_translator

            model = make_translator(source_dim, target_dim, spec, device=device)
            audits[label] = {
                "gradient": gradient_audit(model, substrate, spec, source, target),
                "state": state_persistence_audit(model, substrate, spec, source, target),
            }
            print(json.dumps({"event": "audit", "arm": label, **audits[label]}), flush=True)

            history = train_loop_arm(
                model, substrate, spec, source=source, target=target,
                train_idx=train_idx, val_idx=val_idx, args=args, rng=rng, label=label,
            )
            results[label] = {
                "model": model.describe(),
                "substrate": substrate.describe(),
                "protocol": protocol_dict(spec),
                "history": history,
                "val": evaluate_loop(
                    model, substrate, spec, source, target, val_idx,
                    seed=args.seed, batch_size=args.batch_size,
                ),
                "test": evaluate_loop(
                    model, substrate, spec, source, target, test_idx,
                    seed=args.seed, batch_size=args.batch_size,
                ),
            }
            del substrate, model

    def final_cosine(entry: dict) -> float:
        payload = entry["test"]
        return payload["final"]["mean_cosine"] if "final" in payload else payload["mean_cosine"]

    def final_retrieval(entry: dict) -> float:
        payload = entry["test"]
        return payload["final"]["retrieval@1"] if "final" in payload else payload["retrieval@1"]

    centroid_cosine = references["centroid"]["test"]["mean_cosine"]
    summary = {
        arm: {
            "test_retrieval@1": final_retrieval(entry),
            "test_mean_cosine": final_cosine(entry),
            "cosine_minus_centroid_baseline": final_cosine(entry) - centroid_cosine,
        }
        for arm, entry in results.items()
    }
    summary["_references"] = {
        "centroid_test_retrieval@1": references["centroid"]["test"]["retrieval@1"],
        "centroid_test_mean_cosine": centroid_cosine,
        "least_squares_linear_test_retrieval@1":
            references["least_squares_linear"]["test"]["retrieval@1"],
        "primary_metric": "retrieval@1",
        "why": (
            "The target space is anisotropic, so a constant centroid prediction scores a "
            "high mean cosine at chance retrieval. Cosine is reported only as a delta "
            "against that baseline; retrieval decides."
        ),
    }

    payload = {
        "schema": "papers/malecns-closed-loop-embedding-translation-v1",
        "claim_status": (
            "engineering smoke plus first controlled comparison; exploratory, single seed, "
            "small pool. Not a confirmatory result."
        ),
        "preregistration": "preregistered-closed-loop-embedding-translation-2026-09-16.md",
        "seed": args.seed,
        "device": str(device),
        "embedding_cache": {
            "fingerprint": cache_manifest["fingerprint"],
            "text_sha256": cache_manifest["text_sha256"],
            "corpus": cache_manifest["corpus"],
            "source": cache_manifest["source"],
            "target": cache_manifest["target"],
        },
        "split": {
            "train": int(len(train_idx)),
            "val": int(len(val_idx)),
            "test": int(len(test_idx)),
            "pool_note": "retrieval pool is the split itself; chance@1 is reported with it",
            "group_disjoint": True,
            "groups_total": int(np.unique(groups_np).size),
        },
        "ports": port_report,
        "references": references,
        "operator_stats": {key: stats for key, (_, stats) in operators.items()},
        "substrates": substrate_reports,
        "audits": audits,
        "arms": results,
        "summary": summary,
        "args": {key: (str(value) if isinstance(value, Path) else value)
                 for key, value in vars(args).items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "summary", **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
