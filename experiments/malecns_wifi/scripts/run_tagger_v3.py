from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from malecns_wifi.tagger import (
    FIXED_POINTS,
    ReservoirSpec,
    TaggerSpec,
    label_noise,
    load_corpus,
    run_experiment,
    select_gain,
    summarise,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Document-level outcome classification with the whole MaleCNS brain as a "
        "frozen reservoir, against a degree-preserving null and a matched random ESN."
    )
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--train", type=Path, required=True, help="training split JSONL")
    parser.add_argument(
        "--validation",
        type=Path,
        required=True,
        help="validation split used only to select gain/checkpoints; never reported as held-out",
    )
    parser.add_argument("--eval", type=Path, required=True, help="held-out split JSONL")
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/tagger-v3.json"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--gains", type=float, nargs="+", default=[0.25, 0.5, 0.95, 1.5, 2.5, 4.0])
    parser.add_argument(
        "--operators",
        nargs="+",
        default=None,
        help="restrict to these operators (diagnostic sweeps); default runs all operators.",
    )
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--input-scale", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--ridge", type=float, default=1e-3)
    parser.add_argument(
        "--no-row-normalise",
        action="store_true",
        help="scale by the spectral radius alone. Use only as a robustness reproduction.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=0,
        help="truncate each document to its last N bytes (0 = whole document)",
    )
    parser.add_argument(
        "--keep-resultado",
        action="store_true",
        help="do not truncate at the dispositivo. Plumbing check only; never a result.",
    )
    args = parser.parse_args()

    truncate = not args.keep_resultado
    train = load_corpus(args.train, truncate=truncate)
    validation = load_corpus(args.validation, truncate=truncate)
    evaluate = load_corpus(args.eval, truncate=truncate)

    spec = TaggerSpec(
        seeds=tuple(args.seeds),
        ridge=args.ridge,
        gains=tuple(args.gains),
        normalise_rows=not args.no_row_normalise,
        reservoir=ReservoirSpec(
            leak=args.leak,
            embedding_dim=args.embedding_dim,
            input_scale=args.input_scale,
            batch_size=args.batch_size,
            max_bytes=args.max_bytes,
        ),
    )

    # Preregistered selection rule: every operator gets its best gain on validation.
    # The held-out split is not touched until this dict is frozen.
    validation_report = run_experiment(
        args.graph, train, validation, spec, operators=args.operators
    )
    operator_names = sorted({run["operator"] for run in validation_report["runs"]})
    selection = {
        name: select_gain(validation_report["runs"], name)
        for name in operator_names
    }

    # Held-out gets only the frozen selected gains plus the two fixed robustness
    # points. A common union is used because run_experiment intentionally takes one
    # gain grid for all operators; summarise below ignores cross-operator extras.
    heldout_gains = set(selection.values())
    heldout_gains.update(FIXED_POINTS.values())
    heldout_spec = replace(spec, gains=tuple(sorted(heldout_gains)))
    report = run_experiment(
        args.graph, train, evaluate, heldout_spec, operators=args.operators
    )
    report["summary"] = summarise(report["runs"], selection=selection)
    report["gain_selection"] = {
        "source": "validation",
        "grid": list(spec.gains),
        "selected_by_operator": selection,
        "fixed_robustness_points": FIXED_POINTS,
        "validation_documents": len(validation),
    }
    report["truncated_at_dispositivo"] = truncate
    report["label_noise"] = {
        "train": label_noise(train),
        "validation": label_noise(validation),
        "eval": label_noise(evaluate),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"truncated at dispositivo: {truncate}   (untruncated runs are plumbing checks)")
    print(
        f"documents kept: train {len(train)}, validation {len(validation)}, "
        f"held-out {len(evaluate)}"
    )
    print("gain selected on validation:")
    for name, gain in selection.items():
        print(f"  {name:<14} {gain:.2f}")
    print(
        f"{'operator':<14}{'gain':>6}{'typ':>7}{'macro-F1':>10}"
        f"{'rec/in':>9}{'sat':>7}{'|x|':>8}"
    )
    for run in sorted(report["runs"], key=lambda r: (r["operator"], r["gain"], r["seed"])):
        # Print only selected and fixed-point held-out cells.
        if run["gain"] != selection[run["operator"]] and run["gain"] not in FIXED_POINTS.values():
            continue
        diag = run["diagnostics"]["eval"]
        print(
            f"{run['operator']:<14}{run['gain']:>6.2f}{run['typical_gain']:>7.3f}"
            f"{run['macro_f1']:>10.4f}{diag['recurrent_to_input_ratio']:>9.3f}"
            f"{diag['saturated_fraction']:>7.3f}{diag['state_rms']:>8.4f}"
        )
    print(f"{'char-ngram':<16}{report['char_ngram_baseline']['macro_f1']:>10.4f}")
    for null in ("degree_null", "random_esn"):
        key = f"malecns_minus_{null}"
        if key in report["summary"]:
            paired = report["summary"][key]
            print(
                f"paired vs {null:<14} mean {paired['mean']:+.4f}  "
                f"stdev {paired['stdev']:.4f}  "
                f"wins {paired['malecns_wins']}/{paired['seeds']}"
            )
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
