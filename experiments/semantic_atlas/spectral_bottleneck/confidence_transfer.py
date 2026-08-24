#!/usr/bin/env python3
"""Cross-realization transfer test for the confirmed confidence spectral mode.

The fresh endpoint confirmation found that epistemic confidence, but not stance
or permission, aligned with the first connected Fiedler mode. This follow-up
asks a harder question: does that coordinate transfer from explicit confidence
language to new sentences in which confidence is implied only by the pattern of
replication, measurement consistency, and conflicting observations?

The explicit training corpus is reused exactly from the frozen confirmation.
All test sentences are new and avoid the registered explicit certainty lexemes.
"""

from __future__ import annotations

import argparse
import json
import platform
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy
import torch
import transformers

from confirmatory_endpoint import (
    MODEL,
    REVISION,
    build_confirm_corpus,
    token_length_accuracy,
    token_counts,
)
from observer_comparison import extract_mid_observers
from real_model_experiment import Example, evaluate_one

AXIS = "confidence_transfer"
REGISTERED_K = 8

FORBIDDEN_EXPLICIT_TERMS = {
    "uncertain",
    "certainty",
    "certain",
    "established",
    "speculative",
    "resolved",
    "confidence",
    "confident",
    "settled",
    "demonstrated",
    "doubt",
    "likely",
    "unlikely",
}

CLAIMS = (
    "the medication shortens recovery time",
    "the alloy tolerates repeated heating",
    "the migration occurred before the recorded drought",
    "the sensor fails under humid conditions",
    "the intervention lowers peak demand",
    "the enzyme accelerates the reaction",
    "the habitat change reduced nesting density",
    "the software patch eliminates the memory leak",
)

NEGATIVE_SCENARIOS = (
    "the claim rests on one noisy observation that disappeared when the measurement was repeated",
    "three replications produced mutually inconsistent outcomes and none matched the original",
    "the signal appeared only after an unplanned exclusion and vanished under the preregistered analysis",
    "different instruments gave opposing readings and calibration checks revealed instability",
    "the pattern changed direction across samples and could not be reproduced outside the original dataset",
    "the result depended on a single outlier and disappeared when that point was removed",
    "the original effect was absent in two larger follow-up samples using the same procedure",
    "repeated measurements alternated in sign while the control measurements remained stable",
)

BRIDGE_SCENARIOS = (
    "two studies found the pattern while two comparable studies did not",
    "the main measurement favored the claim while a replication returned a weaker opposing pattern",
    "some instruments reproduced the effect while others showed no measurable change",
    "the aggregate estimate leaned one way although intervals were broad and datasets disagreed",
    "one laboratory reproduced the effect and another obtained a near-zero result",
    "the larger sample showed the pattern but a second method yielded a mixed result",
    "the effect appeared in one population and was absent in another population of similar size",
    "several runs pointed in the same direction while several others remained near baseline",
)

POSITIVE_SCENARIOS = (
    "three independent teams reproduced the same result using preregistered procedures",
    "the finding appeared in repeated measurements across four instruments and two sites",
    "the prediction succeeded in every held-out trial and survived an external replication",
    "multiple independent datasets produced the same pattern with narrow error margins",
    "the result remained unchanged across methods samples and independent laboratories",
    "every attempted replication returned the same effect under blinded analysis",
    "two larger follow-up studies reproduced the original effect with nearly identical estimates",
    "independent instruments and analysis teams all recovered the same directional effect",
)


def build_transfer_corpus() -> list[Example]:
    confirmation = build_confirm_corpus()
    explicit_train = [
        row
        for row in confirmation
        if row.axis == "confidence_confirm" and row.split == "train"
    ]
    rows = [
        Example(
            axis=AXIS,
            split="train",
            context_id=f"explicit-{row.context_id}",
            phrase_id=f"explicit-{row.phrase_id}",
            label=row.label,
            text=row.text,
        )
        for row in explicit_train
    ]
    groups = ((-1, NEGATIVE_SCENARIOS), (0, BRIDGE_SCENARIOS), (1, POSITIVE_SCENARIOS))
    for context_index, claim in enumerate(CLAIMS):
        for label, scenarios in groups:
            scenario = scenarios[context_index]
            rows.append(
                Example(
                    axis=AXIS,
                    split="test",
                    context_id=f"implicit-c{context_index}",
                    phrase_id=f"implicit-l{label}-p{context_index}",
                    label=label,
                    text=f"Regarding the claim that {claim}, {scenario}.",
                )
            )
    return rows


def explicit_term_hits(corpus: list[Example]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for row in corpus:
        if row.split != "test":
            continue
        words = {
            token.strip(".,;:!?()[]{}\"'").lower()
            for token in row.text.split()
        }
        overlap = sorted(words & FORBIDDEN_EXPLICIT_TERMS)
        if overlap:
            hits[row.phrase_id] = overlap
    return hits


def transfer_gates(record: dict[str, object], length_accuracy: float) -> dict[str, bool]:
    return {
        "heldout_implicit_alignment": float(record["heldout_pole_accuracy"]) >= 0.75,
        "implicit_bridges_near_boundary": float(
            record["heldout_bridge_abs_score_ratio"]
        )
        <= 1.00,
        "beats_token_length_by_margin": float(record["heldout_pole_accuracy"])
        >= length_accuracy + 0.15,
        "shuffled_label_control": float(record["shuffled_label_accuracy"]) <= 0.58,
        "scrambled_geometry_control": float(record["scrambled_representation_accuracy"])
        <= 0.65,
    }


def write_outputs(output: Path, result: dict[str, object]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "corpus.json").write_text(
        json.dumps(result["corpus"], indent=2) + "\n", encoding="utf-8"
    )
    r = result["record"]
    lines = [
        "# Implicit confidence spectral transfer",
        "",
        f"**Transfer supported:** `{result['supported']}`",
        "",
        f"- registered k: `{REGISTERED_K}`",
        f"- train pole accuracy: `{r['train_pole_accuracy']:.4f}`",
        f"- implicit held-out pole accuracy: `{r['heldout_pole_accuracy']:.4f}`",
        f"- implicit bridge ratio: `{r['heldout_bridge_abs_score_ratio']:.4f}`",
        f"- token-length held-out accuracy: `{result['token_length_accuracy']:.4f}`",
        f"- supervised centroid held-out accuracy: `{r['centroid_heldout_accuracy']:.4f}`",
        f"- shuffled-label accuracy: `{r['shuffled_label_accuracy']:.4f}`",
        f"- scrambled-representation accuracy: `{r['scrambled_representation_accuracy']:.4f}`",
        f"- explicit forbidden-term hits in implicit test: `{len(result['explicit_term_hits'])}`",
        "",
        "## Claim boundary",
        "",
        "A positive transfer would show that the previously confirmed confidence Fiedler coordinate generalizes beyond direct certainty vocabulary in this controlled small-model setting. It would still not establish natural-corpus topology or causal steering cost.",
        "",
    ]
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--revision", default=REVISION)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=96)
    parser.add_argument("--output", default="results-confidence-transfer")
    args = parser.parse_args()

    corpus = build_transfer_corpus()
    hits = explicit_term_hits(corpus)
    if hits:
        raise RuntimeError(f"implicit test contains registered explicit terms: {hits}")

    observers, model_metadata = extract_mid_observers(
        [row.text for row in corpus],
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    endpoint = observers["causal_endpoint"]
    record = evaluate_one(endpoint, corpus, AXIS, "causal_endpoint_transfer", REGISTERED_K)
    lengths = token_counts(
        [row.text for row in corpus], args.model, args.revision, args.max_length
    )
    length_accuracy = token_length_accuracy(lengths, corpus, AXIS)
    gates = transfer_gates(record, length_accuracy)

    result: dict[str, object] = {
        "claim_boundary": (
            "Fresh cross-realization transfer test frozen after confidence-specific "
            "confirmation. Explicit confidence language is used only in training; test "
            "confidence is implied by replication and measurement patterns."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        },
        "model": model_metadata,
        "protocol": {
            "registered_k": REGISTERED_K,
            "observer": "middle-layer causal endpoint",
            "explicit_train_examples": 96,
            "implicit_test_examples": 24,
            "test_examples_per_class": 8,
            "forbidden_explicit_terms": sorted(FORBIDDEN_EXPLICIT_TERMS),
        },
        "record": record,
        "token_length_accuracy": length_accuracy,
        "explicit_term_hits": hits,
        "gates": gates,
        "supported": all(gates.values()),
        "corpus": [asdict(row) for row in corpus],
    }
    write_outputs(Path(args.output), result)
    print(json.dumps({k: result[k] for k in ["model", "record", "token_length_accuracy", "gates", "supported"]}, indent=2))
    # Scientific negative exits 0 by design.


if __name__ == "__main__":
    main()
