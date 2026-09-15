"""Run the preregistered peer-reliability replication on two new seeds."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SEEDS = (20260916, 20260917)


def _final(run, arm: str):
    if arm == "independent":
        curve = run["independent"]["curve"]
    else:
        curve = run["coupled"][arm]["curve"]
    return curve[-1]["validation"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    runs = {}
    for seed in SEEDS:
        out = args.output.parent / f"replication-seed-{seed}.json"
        cmd = [
            sys.executable,
            str(here / "smoke_peer_reliability_replicate_one_gpu.py"),
            "--graph", str(args.graph),
            "--output", str(out),
            "--epochs", str(args.epochs),
            "--lr", str(args.lr),
            "--peer-lambda", "0.5",
            "--anchor-lambda", str(args.anchor_lambda),
            "--readout-width", str(args.readout_width),
            "--seed", str(seed),
        ]
        print(json.dumps({"event": "replication_seed_start", "seed": seed, "cmd": cmd}), flush=True)
        subprocess.check_call(cmd)
        runs[str(seed)] = json.loads(out.read_text(encoding="utf-8"))

    comparisons = []
    for seed in SEEDS:
        run = runs[str(seed)]
        independent = _final(run, "independent")["all_direct"]
        unweighted = _final(run, "unweighted_0.50")["all_direct"]
        weighted = _final(run, "reliability_0.50")["all_direct"]
        comparisons.append({
            "seed": seed,
            "independent_all": independent["all"],
            "independent_unseen": independent["unseen_generalization"],
            "unweighted_all": unweighted["all"],
            "unweighted_unseen": unweighted["unseen_generalization"],
            "weighted_all": weighted["all"],
            "weighted_unseen": weighted["unseen_generalization"],
            "weighted_minus_independent_unseen": weighted["unseen_generalization"] - independent["unseen_generalization"],
            "weighted_minus_independent_all": weighted["all"] - independent["all"],
            "weighted_minus_unweighted_unseen": weighted["unseen_generalization"] - unweighted["unseen_generalization"],
        })

    mean_unseen_gain = sum(row["weighted_minus_independent_unseen"] for row in comparisons) / len(comparisons)
    mean_all_delta = sum(row["weighted_minus_independent_all"] for row in comparisons) / len(comparisons)
    mean_vs_unweighted = sum(row["weighted_minus_unweighted_unseen"] for row in comparisons) / len(comparisons)
    both_seeds_improve = all(row["weighted_minus_independent_unseen"] > 0 for row in comparisons)
    passes = {
        "both_new_seeds_weighted_unseen_gt_independent": both_seeds_improve,
        "mean_unseen_gain_ge_0.10": mean_unseen_gain >= 0.10,
        "mean_all_delta_ge_minus_0.02": mean_all_delta >= -0.02,
        "mean_weighted_unseen_gt_unweighted": mean_vs_unweighted > 0,
    }
    passes["replication_supports_reliability_hypothesis"] = all(passes.values())

    first = runs[str(SEEDS[0])]
    payload = {
        "schema": "papers/malecns-peer-reliability-replication-batch-v1",
        "claim_status": "preregistered new-seed replication curriculum evidence; not Stage A/B",
        "preregistration": "preregistered-peer-reliability-replication-2026-09-15.md",
        "flavour_rule": first.get("flavour_rule", "one flavour per (encoder, scale) native space with one trainable adapter per channel"),
        "coupling_rule": "compare equal-weight leave-one-out peer evidence against fixed training-reliability-weighted leave-one-out evidence at lambda 0.50",
        "translation_rule": first.get("translation_rule", "ridge maps fitted on aligned training bytes only"),
        "models": first.get("models"),
        "scales": first.get("scales"),
        "spaces": first.get("spaces"),
        "translation_reconstruction": first.get("translation_reconstruction"),
        "seeds": list(SEEDS),
        "lambda": 0.50,
        "comparisons": comparisons,
        "mean_weighted_minus_independent_unseen": mean_unseen_gain,
        "mean_weighted_minus_independent_all": mean_all_delta,
        "mean_weighted_minus_unweighted_unseen": mean_vs_unweighted,
        "preregistered_checks": passes,
        "max_cuda_memory_allocated": max(int(run.get("max_cuda_memory_allocated", 0)) for run in runs.values()),
        "device": first.get("device"),
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "replication_batch_complete", "summary": {
        "comparisons": comparisons,
        "preregistered_checks": passes,
    }}), flush=True)


if __name__ == "__main__":
    main()
