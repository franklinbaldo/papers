"""Re-run the gate's probes from cached features, without loading an encoder.

The encoder pass is the expensive part and the probes are seconds of numpy.
Separating them means a probe design can be iterated on any machine, and a
question about regularisation does not cost another full encode.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from malecns_wifi.encoder_gate import average_precision, leave_one_document_out_auprc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument(
        "--penalties", type=float, nargs="+", default=[0.01, 0.1, 1.0, 10.0, 100.0]
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    labels = stored["labels"].astype(bool)
    groups = stored["groups"]
    blocks = {
        "position_only": stored["position"],
        "absolute_embedding": stored["absolute"],
        "sensation_relations": stored["sensation"],
        "sensation_plus_position": np.hstack([stored["sensation"], stored["position"]]),
        "absolute_plus_position": np.hstack([stored["absolute"], stored["position"]]),
    }
    baseline = float(labels.mean())

    results = {}
    for name, block in blocks.items():
        scored = {
            penalty: leave_one_document_out_auprc(block, labels, groups, penalty=penalty)
            for penalty in args.penalties
        }
        finite = {p: v for p, v in scored.items() if np.isfinite(v)}
        best_penalty = max(finite, key=finite.get) if finite else float("nan")
        results[name] = {
            "dimensions": int(block.shape[1]),
            "auprc": float(finite[best_penalty]) if finite else float("nan"),
            "penalty": best_penalty,
            "by_penalty": {str(p): float(v) for p, v in scored.items()},
        }

    print(f"random AUPRC {baseline:.3f}   ({labels.size} chunks, {int(labels.sum())} positive, "
          f"{len(np.unique(groups))} documents)")
    print(f"{'features':<26}{'dims':>6}{'AUPRC':>8}{'lift':>7}{'penalty':>9}   by penalty")
    for name, row in sorted(results.items(), key=lambda kv: -kv[1]["auprc"]):
        trail = "  ".join(f"{p}={v:.3f}" for p, v in row["by_penalty"].items())
        print(
            f"{name:<26}{row['dimensions']:>6}{row['auprc']:>8.3f}"
            f"{row['auprc'] / baseline:>7.1f}{row['penalty']:>9g}   {trail}"
        )

    # Zero-shot signals, for comparison on the same chunks.
    names = [str(n) for n in stored["signal_names"]]
    print(f"\n{'zero-shot signal':<26}{'AUPRC':>8}{'lift':>7}")
    zero_shot = {}
    for name, values in zip(names, stored["signal_values"], strict=True):
        score = average_precision(values, labels)
        zero_shot[name] = float(score)
        print(f"{name:<26}{score:>8.3f}{score / baseline:>7.1f}")

    if args.output:
        args.output.write_text(
            json.dumps(
                {"random_auprc": baseline, "probes": results, "zero_shot": zero_shot},
                indent=2,
            )
            + "\n"
        )
        print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
