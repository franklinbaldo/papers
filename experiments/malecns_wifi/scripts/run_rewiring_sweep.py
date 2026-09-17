"""Degree-preserving rewiring sweep: measuring how rewiring fraction p impacts multitag decoding.

Tests the Topological Coupling / Inductive Bias Hypothesis:
Does partial degree-preserving rewiring (p in [0.0, 1.0]) monotonically restore
reservoir capacity by breaking biological bottlenecks, or is there a critical transition?

Reuses the exact audited nested cross-validation and caching protocol from run_confirmatory.py.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from malecns_wifi import load_graph
from malecns_wifi.characterize import partial_degree_preserving_null
from malecns_wifi.gustation import delayed_stack, effective_delay_window
from malecns_wifi.multitag import (
    CACHE_SCHEMA,
    MultitagSpec,
    array_fingerprint,
    build_flavours,
    calibrate_drive,
    evaluate,
    evaluate_nested,
    reservoir_states,
    run_fingerprint,
    unit_rows,
)
from malecns_wifi.tagger import row_normalise, select_populations


def build_rewired_operator(matrix, p: float, seed: int):
    """Rewire a fraction p of edges, preserving degrees exact, then row-normalise."""
    if p == 0.0:
        return row_normalise(matrix)
    null, _ = partial_degree_preserving_null(matrix, p=p, seed=seed + 101)
    return row_normalise(null)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("artifacts/runtime-v1/multitag-features.features.npz"))
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument(
        "--p-grid",
        type=float,
        nargs="+",
        default=[0.0, 0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.0],
        help="rewiring fractions to evaluate",
    )
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument(
        "--gains",
        type=float,
        nargs="+",
        default=[0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0],
        help="0.0 measures recurrence gain (score(gain*) - score(0))",
    )
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-drive-rms", type=float, default=0.05)
    parser.add_argument("--representation", default="absolute_plus_relations")
    parser.add_argument("--flavour", default="semantic", choices=["semantic", "random_codebook"])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/runtime-v1/rewiring-sweep.json"),
    )
    parser.add_argument("--state-cache", type=Path, default=Path("artifacts/runtime-v1/state-cache"))
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
        seeds=tuple(args.seeds),
        steps_per_chunk=args.steps_per_chunk,
        leak=args.leak,
        input_scale=args.target_drive_rms,
        gain_grid=tuple(args.gains),
    )
    documents = np.unique(groups)
    delay_horizon = effective_delay_window(spec.leak, spec.steps_per_chunk)
    prevalence = float(
        np.mean([(tag_masks[:, i] > 0).mean() for i in range(tag_masks.shape[1])])
    )

    config_hash = run_fingerprint(
        schema=CACHE_SCHEMA,
        sweep="rewiring_fraction",
        p_grid=list(args.p_grid),
        gains=list(spec.gain_grid),
        leak=spec.leak,
        steps=spec.steps_per_chunk,
        drive=spec.input_scale,
        seeds=list(spec.seeds),
        graph=str(args.graph),
        representation=args.representation,
        flavour=args.flavour,
        features=array_fingerprint(block),
        tag_masks=array_fingerprint(tag_masks),
        tag_embeddings=array_fingerprint(embeddings),
        groups=array_fingerprint(groups.astype(np.float32)),
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
            f"{row['condition']:<22}{row['seed']:>5}"
            f"{('-' if gain is None else f'{gain:.2f}'):>7}"
            f"{row['macro_tag_auprc']:>10.3f}{row['inside_auprc']:>10.3f}",
            flush=True,
        )

    print(f"{len(documents)} documents, {len(tag_masks)} chunks, "
          f"macro prevalence {prevalence:.3f}, {len(spec.seeds)} seeds")
    print(f"\n{'condition':<22}{'seed':>5}{'gain':>7}{'macroAP':>10}{'anyAUPRC':>10}")

    matrix = load_graph(args.graph)
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    readout = populations.readout_indices

    graph_hash = array_fingerprint(matrix.data) + array_fingerprint(
        matrix.indices.astype(np.float32)
    )
    inputs_hash = array_fingerprint(populations.input_indices.astype(np.float32))
    readout_hash = array_fingerprint(readout.astype(np.float32))

    # Baselines: direct controls
    for seed in spec.seeds:
        rng = np.random.default_rng(seed)
        flavours = build_flavours(embeddings, spec, seed=seed, source=args.flavour)
        projection = rng.normal(
            size=(populations.input_indices.size, block.shape[1])
        ).astype(np.float32)
        calibration = calibrate_drive(projection, block, groups, target_rms=spec.input_scale)
        projected = (unit_rows(block) @ projection.T) * np.float32(calibration["mean"])

        for name, features in (
            ("direct_raw", block),
            ("projected_direct", projected),
            ("projected_direct_delay", delayed_stack(projected, groups, delay_horizon)),
        ):
            if (name, seed) in done:
                continue
            record({"condition": name, "seed": seed,
                    **evaluate(features, tag_masks, flavours, groups,
                               penalties=spec.ridge_penalties)})

    # Sweep across p values
    for p in args.p_grid:
        cond_name = f"rewire_p{p:.2f}"
        for seed in spec.seeds:
            if (cond_name, seed) in done:
                continue

            operator = build_rewired_operator(matrix, p, seed)
            rng = np.random.default_rng(seed)
            flavours = build_flavours(embeddings, spec, seed=seed, source=args.flavour)
            projection = rng.normal(
                size=(populations.input_indices.size, block.shape[1])
            ).astype(np.float32)
            calibration = calibrate_drive(projection, block, groups, target_rms=spec.input_scale)

            states_by_gain = {}
            for gain in spec.gain_grid:
                key = None
                if cache:
                    key = cache / (run_fingerprint(
                        schema=CACHE_SCHEMA,
                        operator=cond_name,
                        p=float(p),
                        representation=args.representation,
                        seed=seed,
                        gain=gain,
                        leak=spec.leak,
                        steps=spec.steps_per_chunk,
                        drive=spec.input_scale,
                        features=array_fingerprint(block),
                        graph=graph_hash,
                        inputs=inputs_hash,
                        readout=readout_hash,
                        projection=array_fingerprint(projection),
                        groups=array_fingerprint(groups.astype(np.float32)),
                        calibration=round(float(calibration["mean"]), 12),
                        normalisation="unit_rows+row_normalise",
                    ) + ".npy")
                    if key.exists():
                        states_by_gain[gain] = np.load(key)
                        continue

                gain_spec = MultitagSpec(
                    seeds=spec.seeds,
                    steps_per_chunk=spec.steps_per_chunk,
                    gain=gain,
                    leak=spec.leak,
                    input_scale=spec.input_scale,
                )
                states = np.vstack([
                    reservoir_states(
                        operator,
                        block[groups == document],
                        input_weights=projection,
                        readout_indices=readout,
                        input_indices=populations.input_indices,
                        spec=gain_spec,
                        scale=calibration["mean"],
                    )[0]
                    for document in documents
                ])
                states_by_gain[gain] = states
                if key is not None:
                    np.save(key, states)

            chosen = evaluate_nested(
                states_by_gain, tag_masks, flavours, groups, penalties=spec.ridge_penalties
            )
            recurrence_delta = float("nan")
            if 0.0 in states_by_gain:
                without = evaluate(
                    states_by_gain[0.0], tag_masks, flavours, groups, penalties=spec.ridge_penalties
                )
                recurrence_delta = chosen["macro_tag_auprc"] - without["macro_tag_auprc"]
                record({"condition": f"{cond_name}_gain0", "seed": seed, "p": float(p), **without})

            record({
                "condition": cond_name,
                "p": float(p),
                "seed": seed,
                "recurrence_delta": recurrence_delta,
                "gain_grid": list(spec.gain_grid),
                "per_gain_macro_ap": {
                    str(g): float(
                        evaluate(s, tag_masks, flavours, groups, penalties=spec.ridge_penalties)[
                            "macro_tag_auprc"
                        ]
                    )
                    for g, s in sorted(states_by_gain.items())
                },
                **chosen,
            })

    # Summary table by p
    summary_by_p: dict[str, dict] = {}
    for p in args.p_grid:
        cond_name = f"rewire_p{p:.2f}"
        scores = [r["macro_tag_auprc"] for r in results if r["condition"] == cond_name]
        deltas = [r["recurrence_delta"] for r in results if r["condition"] == cond_name and "recurrence_delta" in r]
        if scores:
            summary_by_p[f"{p:.2f}"] = {
                "p": float(p),
                "n": len(scores),
                "macro_tag_auprc_mean": float(np.mean(scores)),
                "macro_tag_auprc_sd": float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0,
                "recurrence_delta_mean": float(np.mean(deltas)) if deltas else 0.0,
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "config_hash": config_hash,
                "representation": args.representation,
                "flavour": args.flavour,
                "p_grid": list(args.p_grid),
                "seeds": list(args.seeds),
                "summary_by_p": summary_by_p,
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )

    print(f"\n{'p (rewire)':<12}{'n':>4}{'macroAP mean':>14}{'sd':>8}{'Delta_rec':>12}")
    for p_str, row in summary_by_p.items():
        print(f"{p_str:<12}{row['n']:>4}{row['macro_tag_auprc_mean']:>14.3f}{row['macro_tag_auprc_sd']:>8.3f}{row['recurrence_delta_mean']:>12.3f}")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
