"""Run scalar-reliability coupling-strength mapping on four fresh seeds."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

SEEDS = (20260926, 20260927, 20260928, 20260929)
LAMBDAS = (0.05, 0.10, 0.25, 0.50)


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
    timings = {}
    for seed in SEEDS:
        out = args.output.parent / f"dose-response-seed-{seed}.json"
        cmd = [
            sys.executable,
            str(here / "smoke_scalar_reliability_dose_response_cached_one_gpu.py"),
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
        print(json.dumps({"event": "dose_response_seed_start", "seed": seed, "cmd": cmd}), flush=True)
        t0 = time.perf_counter()
        subprocess.check_call(cmd)
        timings[str(seed)] = time.perf_counter() - t0
        runs[str(seed)] = json.loads(out.read_text(encoding="utf-8"))

    comparisons = []
    arm_stats = {f"reliability_{x:.2f}": [] for x in LAMBDAS}
    for seed in SEEDS:
        run = runs[str(seed)]
        independent = _final(run, "independent")
        row = {
            "seed": seed,
            "independent_all": independent["all"],
            "independent_unseen": independent["unseen_generalization"],
        }
        for value in LAMBDAS:
            arm = f"reliability_{value:.2f}"
            score = _final(run, arm)
            du = score["unseen_generalization"] - independent["unseen_generalization"]
            da = score["all"] - independent["all"]
            row[f"{arm}_all"] = score["all"]
            row[f"{arm}_unseen"] = score["unseen_generalization"]
            row[f"{arm}_minus_independent_unseen"] = du
            row[f"{arm}_minus_independent_all"] = da
            arm_stats[arm].append((du, da))
        comparisons.append(row)

    summaries = {}
    eligible = []
    for value in LAMBDAS:
        arm = f"reliability_{value:.2f}"
        vals = arm_stats[arm]
        mean_unseen = sum(v[0] for v in vals) / len(vals)
        mean_all = sum(v[1] for v in vals) / len(vals)
        wins = sum(v[0] > 0 for v in vals)
        qualifies = wins >= 3 and mean_unseen >= 0.05 and mean_all >= -0.02
        summaries[arm] = {
            "lambda": value,
            "unseen_wins": wins,
            "mean_unseen_delta": mean_unseen,
            "mean_all_delta": mean_all,
            "eligible_for_fresh_seed_confirmation": qualifies,
        }
        if qualifies:
            eligible.append(arm)

    selected = None
    if eligible:
        selected = sorted(
            eligible,
            key=lambda arm: (-summaries[arm]["mean_unseen_delta"], summaries[arm]["lambda"]),
        )[0]

    first = runs[str(SEEDS[0])]
    payload = {
        "schema": "papers/malecns-scalar-reliability-dose-response-batch-v1",
        "claim_status": "preregistered coupling-strength mapping; not Stage A/B",
        "preregistration": "preregistered-scalar-reliability-dose-response-2026-09-15.md",
        "seeds": list(SEEDS),
        "lambdas": list(LAMBDAS),
        "comparisons": comparisons,
        "arm_summaries": summaries,
        "selected_followup_arm": selected,
        "seed_seconds": timings,
        "total_seed_seconds": sum(timings.values()),
        "embedding_cache": first.get("embedding_cache"),
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "dose_response_batch_complete",
        "summary": {"arm_summaries": summaries, "selected_followup_arm": selected},
    }), flush=True)


if __name__ == "__main__":
    main()
