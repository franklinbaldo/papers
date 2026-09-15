"""Non-confirmatory real-input smoke for whole-brain semantic readouts.

This deliberately runs only one document/seed.  It exists to prove that the
whole-brain readout paths, matched-width projection and deeper recurrent rollout
execute on the canonical MaleCNS inputs before any Stage-A/Stage-B confirmatory
run is allowed to start.  Results from this script are engineering evidence only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from malecns_wifi import load_graph
from malecns_wifi.multitag import (
    MultitagSpec,
    build_readout,
    calibrate_drive,
    reservoir_states,
)
from malecns_wifi.tagger import row_normalise, select_populations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    block = np.hstack([stored["absolute"], stored["sensation"]]).astype(np.float32)
    groups = stored["groups"]
    document = np.unique(groups)[0]
    document_block = block[groups == document]

    matrix = load_graph(args.graph)
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    operator = row_normalise(matrix)
    neurons = operator.shape[0]
    descending = populations.readout_indices

    rng = np.random.default_rng(args.seed)
    input_weights = rng.normal(
        size=(populations.input_indices.size, block.shape[1])
    ).astype(np.float32)
    calibration = calibrate_drive(input_weights, block, groups, target_rms=0.05)

    cases = [
        ("descending_1314", "descending", 4, descending.size),
        ("wholebrain_projected_1314", "projected", 4, descending.size),
        ("wholebrain_full", "full", 4, None),
        # The deeper path is intentionally exercised only through the matched-budget
        # projection here; this is a runtime smoke, not a scientific comparison.
        ("wholebrain_projected_1314_depth16", "projected", 16, descending.size),
    ]

    rows: list[dict] = []
    for label, kind, steps, width in cases:
        indices, readout_projection = build_readout(
            kind,
            descending,
            neurons,
            seed=args.seed,
            width=width,
        )
        spec = MultitagSpec(
            seeds=(args.seed,),
            steps_per_chunk=steps,
            gain=4.0,
            leak=0.4,
            input_scale=0.05,
        )
        states, drive_rms = reservoir_states(
            operator,
            document_block,
            input_weights=input_weights,
            readout_indices=indices,
            input_indices=populations.input_indices,
            spec=spec,
            scale=calibration["mean"],
            readout_projection=readout_projection,
        )
        if not np.isfinite(states).all():
            raise SystemExit(f"{label}: non-finite recurrent state")
        if states.shape[0] != len(document_block):
            raise SystemExit(
                f"{label}: expected {len(document_block)} chunks, got {states.shape[0]}"
            )
        rows.append(
            {
                "case": label,
                "steps_per_chunk": steps,
                "shape": list(states.shape),
                "drive_rms": float(drive_rms),
                "state_rms": float(np.sqrt(np.mean(states.astype(np.float64) ** 2))),
                "state_std": float(np.std(states.astype(np.float64))),
                "finite": True,
            }
        )

    # A single matched-budget recurrence-off check proves the recurrent matrix has
    # an observable effect without turning this one-document smoke into an F3 rerun.
    indices, readout_projection = build_readout(
        "projected", descending, neurons, seed=args.seed, width=descending.size
    )
    off = MultitagSpec(
        seeds=(args.seed,), steps_per_chunk=4, gain=0.0, leak=0.4, input_scale=0.05
    )
    off_states, _ = reservoir_states(
        operator,
        document_block,
        input_weights=input_weights,
        readout_indices=indices,
        input_indices=populations.input_indices,
        spec=off,
        scale=calibration["mean"],
        readout_projection=readout_projection,
    )
    on_row = next(row for row in rows if row["case"] == "wholebrain_projected_1314")
    on_rms = on_row["state_rms"]
    off_rms = float(np.sqrt(np.mean(off_states.astype(np.float64) ** 2)))

    payload = {
        "schema": "papers/malecns-wholebrain-smoke-v1",
        "claim_status": "engineering smoke only; not Stage A/B confirmatory evidence",
        "seed": args.seed,
        "document": int(document),
        "chunks": int(len(document_block)),
        "neurons": int(neurons),
        "sensory_neurons": int(populations.input_indices.size),
        "descending_neurons": int(descending.size),
        "semantic_input_dim": int(block.shape[1]),
        "calibration": calibration,
        "cases": rows,
        "matched_projected_gain0_state_rms": off_rms,
        "matched_projected_gain4_state_rms": on_rms,
        "gain4_minus_gain0_state_rms": on_rms - off_rms,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
