"""Batch runner for preregistered state-conditioned coupling experiment."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SEEDS = (20261004, 20261005, 20261006, 20261007)
ARMS = ("static_0.50", "state_uncertainty", "state_reward_error")


def _final(run, arm: str):
    if arm == "independent":
        curve = run["independent"]["curve"]
    else:
        curve = run["coupled"][arm]["curve"]
    return curve[-1]["validation"]["all_direct"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--embedding-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--anchor-lambda", type=float, default=0.05)
    parser.add_argument("--readout-width", type=int, default=128)
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    runs = {}
    for seed in SEEDS:
        out = args.output.parent / f"state-seed-{seed}.json"
        cmd = [
            sys.executable,
            str(here / "smoke_state_conditioned_coupling_one_gpu.py"),
            "--graph", str(args.graph),
            "--embedding-cache", str(args.embedding_cache),
            "--output", str(out),
            "--epochs", str(args.epochs),
            "--lr", str(args.lr),
            "--peer-lambda", "0.5",
            "--anchor-lambda", str(args.anchor_lambda),
            "--readout-width", str(args.readout_width),
            "--seed", str(seed),
        ]
        print(json.dumps({"event": "state_seed_start", "seed": seed, "cmd": cmd}), flush=True)
        subprocess.check_call(cmd)
        runs[str(seed)] = json.loads(out.read_text(encoding="utf-8"))

    comparisons = []
    for seed in SEEDS:
        run = runs[str(seed)]
        independent = _final(run, "independent")
        static = _final(run, "static_0.50")
        row = {
            "seed": seed,
            "independent_all": independent["all"],
            "independent_unseen": independent["unseen_generalization"],
            "static_all": static["all"],
            "static_unseen": static["unseen_generalization"],
        }
        for arm in ("state_uncertainty", "state_reward_error"):
            value = _final(run, arm)
            row[f"{arm}_all"] = value["all"]
            row[f"{arm}_unseen"] = value["unseen_generalization"]
            row[f"{arm}_minus_static_unseen"] = value["unseen_generalization"] - static["unseen_generalization"]
            row[f"{arm}_minus_independent_unseen"] = value["unseen_generalization"] - independent["unseen_generalization"]
            row[f"{arm}_minus_independent_all"] = value["all"] - independent["all"]
        comparisons.append(row)

    checks = {}
    summaries = {}
    for arm in ("state_uncertainty", "state_reward_error"):
        wins_vs_static = sum(row[f"{arm}_minus_static_unseen"] > 0 for row in comparisons)
        mean_vs_static = sum(row[f"{arm}_minus_static_unseen"] for row in comparisons) / len(comparisons)
        mean_vs_ind_unseen = sum(row[f"{arm}_minus_independent_unseen"] for row in comparisons) / len(comparisons)
        mean_vs_ind_all = sum(row[f"{arm}_minus_independent_all"] for row in comparisons) / len(comparisons)
        promoted = (
            wins_vs_static >= 3
            and mean_vs_static > 0
            and mean_vs_ind_unseen >= 0.03
            and mean_vs_ind_all >= -0.02
        )
        summaries[arm] = {
            "wins_vs_static": wins_vs_static,
            "mean_minus_static_unseen": mean_vs_static,
            "mean_minus_independent_unseen": mean_vs_ind_unseen,
            "mean_minus_independent_all": mean_vs_ind_all,
        }
        checks[arm] = promoted

    first = runs[str(SEEDS[0])]
    payload = {
        "schema": "papers/malecns-state-conditioned-coupling-batch-v1",
        "claim_status": "preregistered exploratory state-conditioned coupling; not Stage A/B",
        "preregistration": "preregistered-state-conditioned-coupling-2026-09-15.md",
        "seeds": list(SEEDS),
        "arms": ["independent", "static_0.50", "state_uncertainty", "state_reward_error"],
        "comparisons": comparisons,
        "summaries": summaries,
        "promotion_checks": checks,
        "embedding_cache": first.get("embedding_cache"),
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "state_conditioned_batch_complete", "summaries": summaries, "promotion_checks": checks}), flush=True)


if __name__ == "__main__":
    main()
