"""Run preregistered directed peer-gain comparison on two new seeds."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SEEDS = (20260918, 20260919)


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
    parser.add_argument("--peer-lambda", type=float, default=0.50)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    args = parser.parse_args()
    if abs(args.peer_lambda - 0.50) > 1e-9:
        raise SystemExit("directed peer-gain preregistration fixes --peer-lambda=0.50")

    here = Path(__file__).resolve().parent
    runs = {}
    for seed in SEEDS:
        out = args.output.parent / f"directed-peer-seed-{seed}.json"
        cmd = [
            sys.executable,
            str(here / "smoke_directed_peer_gains_one_gpu.py"),
            "--graph", str(args.graph),
            "--output", str(out),
            "--epochs", str(args.epochs),
            "--lr", str(args.lr),
            "--peer-lambda", "0.5",
            "--anchor-lambda", str(args.anchor_lambda),
            "--readout-width", str(args.readout_width),
            "--seed", str(seed),
        ]
        print(json.dumps({"event": "directed_peer_seed_start", "seed": seed, "cmd": cmd}), flush=True)
        subprocess.check_call(cmd)
        runs[str(seed)] = json.loads(out.read_text(encoding="utf-8"))

    comparisons = []
    for seed in SEEDS:
        run = runs[str(seed)]
        independent = _final(run, "independent")["all_direct"]
        scalar = _final(run, "scalar_reliability_0.50")["all_direct"]
        directed = _final(run, "directed_reliability_0.50")["all_direct"]
        comparisons.append({
            "seed": seed,
            "independent_all": independent["all"],
            "independent_unseen": independent["unseen_generalization"],
            "scalar_all": scalar["all"],
            "scalar_unseen": scalar["unseen_generalization"],
            "directed_all": directed["all"],
            "directed_unseen": directed["unseen_generalization"],
            "directed_minus_scalar_unseen": directed["unseen_generalization"] - scalar["unseen_generalization"],
            "directed_minus_scalar_all": directed["all"] - scalar["all"],
            "directed_minus_independent_unseen": directed["unseen_generalization"] - independent["unseen_generalization"],
        })

    mean_unseen_gain = sum(row["directed_minus_scalar_unseen"] for row in comparisons) / len(comparisons)
    mean_all_delta = sum(row["directed_minus_scalar_all"] for row in comparisons) / len(comparisons)
    both_seeds = all(row["directed_minus_scalar_unseen"] > 0 for row in comparisons)
    checks = {
        "both_new_seeds_directed_unseen_gt_scalar": both_seeds,
        "mean_directed_minus_scalar_unseen_gt_0": mean_unseen_gain > 0,
        "mean_directed_minus_scalar_all_ge_minus_0.02": mean_all_delta >= -0.02,
    }
    checks["directed_teaching_supported"] = all(checks.values())

    first = runs[str(SEEDS[0])]
    payload = {
        "schema": "papers/malecns-directed-peer-gains-batch-v1",
        "claim_status": "preregistered directed-teaching curriculum evidence; not Stage A/B",
        "preregistration": "preregistered-directed-peer-gains-2026-09-15.md",
        "seeds": list(SEEDS),
        "lambda": 0.50,
        "flavour_rule": first.get("flavour_rule"),
        "coupling_rule": (
            "training-only cross-channel teaching; scalar reliability versus fixed directed "
            "sender->receiver usefulness matrix; no inference-time attention/router"
        ),
        "translation_rule": first.get("translation_rule"),
        "comparisons": comparisons,
        "mean_directed_minus_scalar_unseen": mean_unseen_gain,
        "mean_directed_minus_scalar_all": mean_all_delta,
        "preregistered_checks": checks,
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "directed_peer_gain_batch_complete",
        "summary": {"comparisons": comparisons, "preregistered_checks": checks},
    }), flush=True)


if __name__ == "__main__":
    main()
