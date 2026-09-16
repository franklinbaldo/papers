"""Cheap kill-test for the gustation front: do four taste channels already tag?

Runs before any operator. If a learned four-channel compositional code already
recovers the nine tags on held-out documents, then the gustatory interface is
doing the work and MaleCNS, the nulls and the ESN would be decorating a solved
problem -- and there is no reason to spend hours finding that out.

Reports the ceiling as well as the learned code. ``oracle_flavour`` is the true
taste, so its score is what *any* four-channel code could achieve: with k = 4 and
nine tags the codebook is deliberately ambiguous, and if even the oracle cannot
separate the tags instantaneously, that is the opening for a recurrent operator
to contribute something using trajectory rather than instantaneous value.

Nothing here is tuned after seeing a result: k, codebook, regularisation and
representation are fixed by the registered gustation design.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from malecns_wifi.gustation import (
    FlavourSpec,
    delayed_stack,
    effective_delay_window,
    flavour_codebook,
    fit_flavourizer,
    target_flavour,
)
from malecns_wifi.multitag import build_flavours, evaluate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--channels", type=int, default=4)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    parser.add_argument("--leak", type=float, default=0.4)
    parser.add_argument("--steps-per-chunk", type=int, default=4)
    parser.add_argument("--representation", default="absolute_plus_relations")
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/runtime-v1/gustation-gate.json")
    )
    args = parser.parse_args()

    stored = np.load(args.features, allow_pickle=False)
    tag_masks, groups = stored["tag_masks"], stored["groups"]
    embeddings = stored["tag_embeddings"]
    blocks = {
        "absolute": stored["absolute"],
        "relations": stored["sensation"],
        "absolute_plus_relations": np.hstack([stored["absolute"], stored["sensation"]]),
    }
    semantics = blocks[args.representation]
    tags = tag_masks.shape[1]
    prevalence = float(np.mean([(tag_masks[:, i] > 0).mean() for i in range(tags)]))
    horizon = effective_delay_window(args.leak, args.steps_per_chunk)

    print(f"{len(np.unique(groups))} documents, {len(tag_masks)} chunks, {tags} tags")
    print(f"macro prevalence {prevalence:.4f}, tag chance {1/tags:.3f}, "
          f"k = {args.channels}, delay horizon {horizon} chunks\n")
    print(f"{'condition':<26}{'seed':>5}{'macroAP':>9}{'anyAUPRC':>10}{'tagAcc':>9}")

    rows = []
    for seed in args.seeds:
        spec = FlavourSpec(channels=args.channels, seed=seed)
        codebook, diagnostics = flavour_codebook(embeddings, spec, source="semantic")
        oracle = target_flavour(tag_masks, codebook)
        learned = fit_flavourizer(semantics, oracle, groups, spec)

        # The decoding codebook for scoring is the same taste geometry, so
        # magnitude answers "is there a tag" and direction "which one".
        conditions = {
            "oracle_flavour": oracle,
            "learned_flavour": learned,
            "learned_flavour_delay": delayed_stack(learned, groups, horizon),
            f"direct_{args.representation}": semantics,
        }
        for name, features in conditions.items():
            scored = evaluate(features, tag_masks, codebook, groups,
                              penalties=(0.01, 0.1, 1.0, 10.0, 100.0))
            rows.append({
                "condition": name,
                "seed": seed,
                "channels": args.channels,
                "codebook_mean_abs_cosine": diagnostics["mean_abs_cosine"],
                **scored,
            })
            print(f"{name:<26}{seed:>5}{scored['macro_tag_auprc']:>9.3f}"
                  f"{scored['inside_auprc']:>10.3f}"
                  f"{scored['tag_accuracy_on_true_spans']:>9.3f}", flush=True)

    # --- summary, per condition and per document ----------------------------
    names = list(dict.fromkeys(row["condition"] for row in rows))
    summary = {}
    for name in names:
        subset = [row for row in rows if row["condition"] == name]
        summary[name] = {
            "macro_tag_auprc_mean": float(np.mean([r["macro_tag_auprc"] for r in subset])),
            "macro_tag_auprc_stdev": float(np.std([r["macro_tag_auprc"] for r in subset], ddof=1)),
            "inside_auprc_mean": float(np.mean([r["inside_auprc"] for r in subset])),
            "tag_accuracy_mean": float(
                np.mean([r["tag_accuracy_on_true_spans"] for r in subset])
            ),
            "per_seed_macro_ap": [r["macro_tag_auprc"] for r in subset],
        }

    direct = f"direct_{args.representation}"
    deltas = {}
    for name in names:
        if name == direct:
            continue
        paired = []
        for seed in args.seeds:
            a = next(r for r in rows if r["condition"] == name and r["seed"] == seed)
            b = next(r for r in rows if r["condition"] == direct and r["seed"] == seed)
            paired.append(a["macro_tag_auprc"] - b["macro_tag_auprc"])
        deltas[f"{name}_minus_{direct}"] = {
            "per_seed": paired, "mean": float(np.mean(paired)),
            "wins": int(sum(1 for d in paired if d > 0)), "seeds": len(paired),
        }

    per_document = {}
    for name in names:
        subset = [r for r in rows if r["condition"] == name]
        documents = sorted(subset[0].get("per_document", {}), key=int)
        per_document[name] = {
            document: float(np.mean([r["per_document"][document]["macro_tag_auprc"]
                                     for r in subset]))
            for document in documents
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "representation": args.representation,
        "channels": args.channels,
        "tags": tags,
        "macro_prevalence": prevalence,
        "tag_chance": 1.0 / tags,
        "delay_horizon_chunks": horizon,
        "summary": summary,
        "paired_vs_direct": deltas,
        "per_document_macro_ap": per_document,
        "results": rows,
        "claim_boundary": (
            "No operator involved. Asks whether four taste channels already recover "
            "the tags; a strong result here means the gustatory interface is doing the "
            "work and an operator would be decorating a solved problem."
        ),
    }, indent=2) + "\n")

    print(f"\n{'condition':<26}{'macroAP':>9}{'sd':>7}{'anyAUPRC':>10}{'tagAcc':>9}")
    for name, row in summary.items():
        print(f"{name:<26}{row['macro_tag_auprc_mean']:>9.3f}"
              f"{row['macro_tag_auprc_stdev']:>7.3f}{row['inside_auprc_mean']:>10.3f}"
              f"{row['tag_accuracy_mean']:>9.3f}")
    print(f"\n{'paired contrast':<44}{'mean':>9}{'wins':>8}")
    for name, row in deltas.items():
        print(f"{name:<44}{row['mean']:>+9.3f}{row['wins']:>5}/{row['seeds']}")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
