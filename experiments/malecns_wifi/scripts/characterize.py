from __future__ import annotations

import argparse
from pathlib import Path

from malecns_wifi import CharacterizeSpec, DriveSpec, characterize, summary_table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Spectral radius and Jaeger memory capacity for the connectome operator "
        "and its two nulls."
    )
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/runtime-v1/characterization.json")
    )
    parser.add_argument("--gains", type=float, nargs="+", default=[0.8, 1.0, 1.2])
    parser.add_argument("--leaks", type=float, nargs="+", default=[1.0])
    parser.add_argument("--input-seeds", type=int, nargs="+", default=[0])
    parser.add_argument("--null-seed", type=int, default=20260914)
    parser.add_argument("--washout", type=int, default=200)
    parser.add_argument("--train-steps", type=int, default=2500)
    parser.add_argument("--test-steps", type=int, default=1000)
    parser.add_argument("--max-lag", type=int, default=100)
    parser.add_argument("--readout-size", type=int, default=512)
    parser.add_argument("--input-scale", type=float, default=0.1)
    args = parser.parse_args()

    spec = CharacterizeSpec(
        gains=tuple(args.gains),
        leaks=tuple(args.leaks),
        input_seeds=tuple(args.input_seeds),
        null_seed=args.null_seed,
        drive=DriveSpec(
            washout=args.washout,
            train_steps=args.train_steps,
            test_steps=args.test_steps,
            max_lag=args.max_lag,
            readout_size=args.readout_size,
            input_scale=args.input_scale,
        ),
    )
    report = characterize(args.graph, args.output, spec)
    print(summary_table(report))
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
