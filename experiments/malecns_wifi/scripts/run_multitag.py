"""Run 1: multi-tag frozen-state decoding, on CPU, from cached encoder features.

Three paired sensations (absolute, relations, both), each read directly and
through the frozen operator, plus the topology nulls on the representation chosen
in validation, plus semantic against random flavours.

Nothing here claims the fly learned. It asks whether MaleCNS's state carries a
representation the direct control does not.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from malecns_wifi import load_graph
from malecns_wifi.multitag import (
    MultitagSpec,
    build_flavours,
    evaluate,
    reservoir_states,
)
from malecns_wifi.tagger import iter_operators, select_populations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument("--gain", type=float, default=0.95)
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--readout-size", type=int, default=0, help="0 = all descending neurons")
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/runtime-v1/multitag-run1.json")
    )
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    if "tag_masks" not in stored:
        raise SystemExit("this feature cache has no tag_masks; re-run the gate with --tags")

    tag_names = [str(name) for name in stored["tag_names"]]
    tag_masks = stored["tag_masks"]
    groups = stored["groups"]
    blocks = {
        "absolute": stored["absolute"],
        "relations": stored["sensation"],
        "absolute_plus_relations": np.hstack([stored["absolute"], stored["sensation"]]),
    }
    spec = MultitagSpec(
        seeds=tuple(args.seeds),
        steps_per_chunk=args.steps_per_chunk,
        gain=args.gain,
        leak=args.leak,
    )

    print(f"{len(np.unique(groups))} documents, {len(tag_masks)} chunks, "
          f"{len(tag_names)} tags: {', '.join(tag_names)}")
    coverage = tag_masks.sum(axis=0)
    print("chunks per tag: " + ", ".join(
        f"{name}={int(count)}" for name, count in zip(tag_names, coverage, strict=True)
    ))

    results = []

    def record(row: dict) -> None:
        results.append(row)
        print(
            f"{row['reservoir']:<14}{row['representation']:<24}{row['flavour']:<16}"
            f"{row['inside_auprc']:>8.3f}{row['inside_auprc']/row['random_auprc']:>7.1f}"
            f"{row['tag_accuracy_on_true_spans']:>9.3f}",
            flush=True,
        )

    print(f"\n{'reservoir':<14}{'representation':<24}{'flavour':<16}"
          f"{'AUPRC':>8}{'lift':>7}{'tagAcc':>9}  (tag chance "
          f"{1 / len(tag_names):.3f})")

    # --- direct probes ------------------------------------------------------
    for name, block in blocks.items():
        for flavour_source in spec.flavour_sources:
            scores = [
                evaluate(
                    block,
                    tag_masks,
                    build_flavours(
                        stored["tag_embeddings"], spec, seed=seed, source=flavour_source
                    ),
                    groups,
                    penalties=spec.ridge_penalties,
                )
                for seed in spec.seeds
            ]
            record({
                "reservoir": "direct",
                "representation": name,
                "flavour": flavour_source,
                "inside_auprc": float(np.mean([s["inside_auprc"] for s in scores])),
                "tag_accuracy_on_true_spans": float(
                    np.mean([s["tag_accuracy_on_true_spans"] for s in scores])
                ),
                "random_auprc": scores[0]["random_auprc"],
                "per_seed": scores,
            })

    # --- through the operators ----------------------------------------------
    matrix = load_graph(args.graph)
    archive = np.load(args.graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    readout = populations.readout_indices
    if args.readout_size:
        readout = readout[: args.readout_size]

    for operator_name, operator, _ in iter_operators(matrix, seed=spec.seeds[0]):
        for name, block in blocks.items():
            if operator_name != "malecns" and name != "absolute_plus_relations":
                continue  # nulls run on the full representation only
            for flavour_source in spec.flavour_sources:
                scores = []
                for seed in spec.seeds:
                    rng = np.random.default_rng(seed)
                    input_weights = (
                        rng.normal(size=(populations.input_indices.size, block.shape[1]))
                        * spec.input_scale
                        / np.sqrt(block.shape[1])
                    ).astype(np.float32)
                    states = np.vstack([
                        reservoir_states(
                            operator,
                            block[groups == document],
                            input_weights=input_weights,
                            readout_indices=readout,
                            input_indices=populations.input_indices,
                            spec=spec,
                        )
                        for document in np.unique(groups)
                    ])
                    scores.append(
                        evaluate(
                            states,
                            tag_masks,
                            build_flavours(
                                stored["tag_embeddings"], spec, seed=seed, source=flavour_source
                            ),
                            groups,
                            penalties=spec.ridge_penalties,
                        )
                    )
                record({
                    "reservoir": operator_name,
                    "representation": name,
                    "flavour": flavour_source,
                    "inside_auprc": float(np.mean([s["inside_auprc"] for s in scores])),
                    "tag_accuracy_on_true_spans": float(
                        np.mean([s["tag_accuracy_on_true_spans"] for s in scores])
                    ),
                    "random_auprc": scores[0]["random_auprc"],
                    "per_seed": scores,
                })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "tags": tag_names,
                "documents": int(len(np.unique(groups))),
                "chunks": int(len(tag_masks)),
                "readout_neurons": int(readout.size),
                "spec": {
                    "gain": spec.gain,
                    "leak": spec.leak,
                    "steps_per_chunk": spec.steps_per_chunk,
                    "seeds": list(spec.seeds),
                },
                "results": results,
                "claim_boundary": (
                    "Run 1, frozen-state decoding. The recurrent weights never move and "
                    "the association lives in the ridge readout, so this cannot show that "
                    "the fly learned anything. It shows whether the state MaleCNS produces "
                    "carries a representation the direct control does not."
                ),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
