from __future__ import annotations

import argparse
import json
from pathlib import Path

from malecns_wifi.tagger import ReservoirSpec, TaggerSpec, label_noise, load_corpus, run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Document-level outcome classification with the whole MaleCNS brain as a "
        "frozen reservoir, against a degree-preserving null and a matched random ESN."
    )
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--train", type=Path, required=True, help="training split JSONL")
    parser.add_argument("--eval", type=Path, required=True, help="held-out split JSONL")
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/tagger-v3.json"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--target-radius", type=float, default=0.95)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--input-scale", type=float, default=1.0)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--ridge", type=float, default=1e-3)
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=0,
        help="truncate each document to its last N bytes (0 = whole document)",
    )
    parser.add_argument(
        "--keep-resultado",
        action="store_true",
        help="do not truncate at the dispositivo. The ruling and its cost/sucumbencia clauses "
        "are then in the text and every model reads the answer off the page: use only as a "
        "plumbing check, never as a result.",
    )
    args = parser.parse_args()

    truncate = not args.keep_resultado
    train = load_corpus(args.train, truncate=truncate)
    evaluate = load_corpus(args.eval, truncate=truncate)

    spec = TaggerSpec(
        seeds=tuple(args.seeds),
        ridge=args.ridge,
        target_radius=args.target_radius,
        reservoir=ReservoirSpec(
            leak=args.leak,
            embedding_dim=args.embedding_dim,
            input_scale=args.input_scale,
            batch_size=args.batch_size,
            max_bytes=args.max_bytes,
        ),
    )
    report = run_experiment(args.graph, train, evaluate, spec)
    report["truncated_at_dispositivo"] = truncate
    report["label_noise"] = {
        "train": label_noise(train),
        "eval": label_noise(evaluate),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"truncated at dispositivo: {truncate}   (untruncated runs are plumbing checks)")
    print(f"documents kept: train {len(train)}, eval {len(evaluate)}")
    print(f"{'operator':<16}{'macro-F1':>10}{'stdev':>9}{'rec/in':>9}")
    for name, stats in report["summary"].items():
        if not name.startswith("malecns_minus_"):
            ratio = next(
                run["diagnostics"]["eval"]["recurrent_to_input_ratio"]
                for run in report["runs"]
                if run["operator"] == name
            )
            print(
                f"{name:<16}{stats['macro_f1_mean']:>10.4f}{stats['macro_f1_stdev']:>9.4f}"
                f"{ratio:>9.3f}"
            )
    print(f"{'char-ngram':<16}{report['char_ngram_baseline']['macro_f1']:>10.4f}")
    for null in ("degree_null", "random_esn"):
        key = f"malecns_minus_{null}"
        if key in report["summary"]:
            paired = report["summary"][key]
            print(
                f"paired vs {null:<14} mean {paired['mean']:+.4f}  stdev {paired['stdev']:.4f}  "
                f"wins {paired['malecns_wins']}/{paired['seeds']}"
            )
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
