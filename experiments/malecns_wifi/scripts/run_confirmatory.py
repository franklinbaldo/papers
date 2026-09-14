"""Confirmatory F2/F3: multi-tag decoding with the registered protocol.

Four defects separated this from the fixed-gain screening that preceded it, each
found by audit rather than by a test:

* **the null topology is redrawn per seed.** Drawing it once and varying only the
  input projection makes "10 seeds" ten readouts of ONE random graph, when the
  quantity a topology null must vary is the rewiring itself.
* **each operator selects its own gain on validation** from the declared grid.
  ``rho = 1`` does not put MaleCNS and a random ESN in the same dynamical regime
  -- the first has typical gain ~0.295 at unit radius, the second a far flatter
  spectrum -- so a fixed 0.95 compares operating points rather than wirings.
* **the ridge is selected on macro per-tag AUPRC**, the metric the decision rule
  is written in, instead of on any-tag AUPRC.
* **a baseline ladder** separates what the interface destroys from what the
  operator destroys. ``direct_raw`` is an information ceiling, not an
  architecturally matched control: if the score already falls at unit-norm plus
  projection, the operator cannot be charged for that part.

Cache identity covers gain, leak, steps, populations, drive and feature content,
so a gain sweep cannot silently reload another gain's states.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from malecns_wifi import load_graph
from malecns_wifi.characterize import degree_preserving_null, random_esn
from malecns_wifi.multitag import (
    MultitagSpec,
    array_fingerprint,
    build_flavours,
    calibrate_drive,
    evaluate,
    reservoir_states,
    run_fingerprint,
    unit_rows,
)
from malecns_wifi.gustation import delayed_stack, effective_delay_window
from malecns_wifi.tagger import row_normalise, select_populations


def build_operator(kind: str, matrix, seed: int):
    """One operator, with the null topology drawn from *this* seed."""
    if kind == "malecns":
        return row_normalise(matrix)
    if kind == "degree_null":
        null, _ = degree_preserving_null(matrix, seed=seed + 101)
        return row_normalise(null)
    if kind == "random_esn":
        esn, _ = random_esn(matrix, seed=seed + 202)
        return row_normalise(esn)
    raise ValueError(f"unknown operator {kind!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument(
        "--gains", type=float, nargs="+",
        default=[0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0],
        help="0.0 is a reported condition, not a debug aside: score(gain*) - score(0) "
        "is how much each operator's recurrent matrix contributes, and operators may "
        "differ in how much benefit they extract from recurrence at all.",
    )
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-drive-rms", type=float, default=0.05)
    parser.add_argument("--representation", default="absolute_plus_relations")
    parser.add_argument("--operators", nargs="+",
                        default=["malecns", "degree_null", "random_esn"])
    parser.add_argument("--flavour", default="semantic",
                        choices=["semantic", "random_codebook"])
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/runtime-v1/multitag-confirmatory.json"))
    parser.add_argument("--state-cache", type=Path, default=None)
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    tag_masks, groups = stored["tag_masks"], stored["groups"]
    embeddings = stored["tag_embeddings"]
    blocks = {
        "absolute": stored["absolute"],
        "relations": stored["sensation"],
        "absolute_plus_relations": np.hstack([stored["absolute"], stored["sensation"]]),
    }
    block = blocks[args.representation]
    spec = MultitagSpec(
        seeds=tuple(args.seeds), steps_per_chunk=args.steps_per_chunk, leak=args.leak,
        input_scale=args.target_drive_rms, gain_grid=tuple(args.gains),
    )
    documents = np.unique(groups)
    # Matched to the leak's reach so the operator has no free memory advantage.
    delay_horizon = effective_delay_window(spec.leak, spec.steps_per_chunk)
    prevalence = float(
        np.mean([(tag_masks[:, i] > 0).mean() for i in range(tag_masks.shape[1])])
    )

    config_hash = run_fingerprint(
        gains=list(spec.gain_grid), leak=spec.leak, steps=spec.steps_per_chunk,
        drive=spec.input_scale, seeds=list(spec.seeds), graph=str(args.graph),
        representation=args.representation, flavour=args.flavour,
        features=array_fingerprint(block),
    )
    checkpoint = args.output.with_suffix(".partial.json")
    results: list[dict] = []
    if checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous.get("config_hash") != config_hash:
            raise SystemExit(
                f"{checkpoint} was written under configuration "
                f"{previous.get('config_hash')}, not {config_hash}. Resuming would mix "
                "runs; delete it to start fresh."
            )
        results = previous["results"]
        print(f"resuming with {len(results)} cells done")
    done = {(row["condition"], row["seed"]) for row in results}

    cache = args.state_cache
    if cache:
        cache.mkdir(parents=True, exist_ok=True)

    def record(row: dict) -> None:
        results.append(row)
        checkpoint.write_text(
            json.dumps({"config_hash": config_hash, "results": results}, indent=2) + "\n"
        )
        gain = row.get("selected_gain")
        print(
            f"{row['condition']:<20}{row['seed']:>5}"
            f"{('-' if gain is None else f'{gain:.2f}'):>7}"
            f"{row['macro_tag_auprc']:>10.3f}{row['inside_auprc']:>10.3f}",
            flush=True,
        )

    print(f"{len(documents)} documents, {len(tag_masks)} chunks, "
          f"macro prevalence {prevalence:.3f}, {len(spec.seeds)} seeds")
    print(f"\n{'condition':<20}{'seed':>5}{'gain':>7}{'macroAP':>10}{'anyAUPRC':>10}")

    matrix = load_graph(args.graph)
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    readout = populations.readout_indices

    for seed in spec.seeds:
        rng = np.random.default_rng(seed)
        flavours = build_flavours(embeddings, spec, seed=seed, source=args.flavour)
        projection = rng.normal(
            size=(populations.input_indices.size, block.shape[1])
        ).astype(np.float32)
        calibration = calibrate_drive(projection, block, groups,
                                      target_rms=spec.input_scale)
        projected = (unit_rows(block) @ projection.T) * np.float32(calibration["mean"])

        for name, features in (
            ("direct_raw", block),
            ("direct_unit_norm", unit_rows(block)),
            ("projected_direct", projected),
            ("projected_direct_delay", delayed_stack(projected, groups, delay_horizon)),
        ):
            if (name, seed) in done:
                continue
            record({"condition": name, "seed": seed,
                    **evaluate(features, tag_masks, flavours, groups,
                               penalties=spec.ridge_penalties)})

    for kind in args.operators:
        for seed in spec.seeds:
            if (kind, seed) in done:
                continue
            operator = build_operator(kind, matrix, seed)
            rng = np.random.default_rng(seed)
            flavours = build_flavours(embeddings, spec, seed=seed, source=args.flavour)
            projection = rng.normal(
                size=(populations.input_indices.size, block.shape[1])
            ).astype(np.float32)
            calibration = calibrate_drive(projection, block, groups,
                                          target_rms=spec.input_scale)

            states_by_gain = {}
            for gain in spec.gain_grid:
                key = None
                if cache:
                    key = cache / (run_fingerprint(
                        operator=kind, representation=args.representation, seed=seed,
                        gain=gain, leak=spec.leak, steps=spec.steps_per_chunk,
                        drive=spec.input_scale, features=array_fingerprint(block),
                        graph=str(args.graph), readout=int(readout.size),
                    ) + ".npy")
                    if key.exists():
                        states_by_gain[gain] = np.load(key)
                        continue
                gain_spec = MultitagSpec(
                    seeds=spec.seeds, steps_per_chunk=spec.steps_per_chunk, gain=gain,
                    leak=spec.leak, input_scale=spec.input_scale,
                )
                states = np.vstack([
                    reservoir_states(
                        operator, block[groups == document], input_weights=projection,
                        readout_indices=readout,
                        input_indices=populations.input_indices,
                        spec=gain_spec, scale=calibration["mean"],
                    )[0]
                    for document in documents
                ])
                states_by_gain[gain] = states
                if key is not None:
                    np.save(key, states)

            # Gain chosen on a split of the TRAINING documents, never the held-out
            # one, and on macro per-tag AUPRC.
            validation = documents[: max(1, len(documents) // 5)]
            held_in = ~np.isin(groups, validation)
            selectable = [g for g in spec.gain_grid if g > 0]
            best_gain, best_score = selectable[0], -np.inf
            for gain in selectable:
                states = states_by_gain[gain]
                score = evaluate(states[held_in], tag_masks[held_in], flavours,
                                 groups[held_in],
                                 penalties=spec.ridge_penalties)["macro_tag_auprc"]
                if np.isfinite(score) and score > best_score:
                    best_gain, best_score = gain, score

            chosen = evaluate(states_by_gain[best_gain], tag_masks, flavours, groups,
                              penalties=spec.ridge_penalties)
            recurrence_delta = float("nan")
            if 0.0 in states_by_gain:
                without = evaluate(states_by_gain[0.0], tag_masks, flavours, groups,
                                   penalties=spec.ridge_penalties)
                recurrence_delta = chosen["macro_tag_auprc"] - without["macro_tag_auprc"]
                record({"condition": f"{kind}_gain0", "seed": seed, **without})
            record({
                "condition": kind, "seed": seed, "selected_gain": best_gain,
                "validation_macro_ap": float(best_score),
                "recurrence_delta": recurrence_delta,
                "gain_grid": list(spec.gain_grid),
                "per_gain_macro_ap": {
                    str(g): float(evaluate(s, tag_masks, flavours, groups,
                                           penalties=spec.ridge_penalties)["macro_tag_auprc"])
                    for g, s in sorted(states_by_gain.items())
                },
                **chosen,
            })

    by_condition: dict[str, dict[int, float]] = {}
    for row in results:
        by_condition.setdefault(row["condition"], {})[row["seed"]] = row["macro_tag_auprc"]

    summary = {}
    for control in ("projected_direct", "degree_null", "random_esn"):
        if "malecns" in by_condition and control in by_condition:
            seeds = sorted(set(by_condition["malecns"]) & set(by_condition[control]))
            deltas = [by_condition["malecns"][s] - by_condition[control][s] for s in seeds]
            summary[f"malecns_minus_{control}"] = {
                "per_seed": deltas,
                "mean": float(np.mean(deltas)) if deltas else float("nan"),
                "wins": int(sum(1 for d in deltas if d > 0)),
                "seeds": len(deltas),
            }

    args.output.write_text(json.dumps({
        "config_hash": config_hash,
        "representation": args.representation,
        "flavour": args.flavour,
        "macro_prevalence": prevalence,
        "results": results,
        "paired": summary,
        "decision_rule": (
            "F3 requires MaleCNS to beat the direct control, the degree-preserving "
            "null and the matched random ESN on held-out macro per-tag AUPRC, mean "
            "paired effect >= 0.03, same sign in >= 8 of 10 seeds."
        ),
    }, indent=2) + "\n")

    print(f"\n{'paired contrast':<34}{'mean':>9}{'wins':>9}")
    for name, row in summary.items():
        print(f"{name:<34}{row['mean']:>+9.3f}{row['wins']:>6}/{row['seeds']}")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
