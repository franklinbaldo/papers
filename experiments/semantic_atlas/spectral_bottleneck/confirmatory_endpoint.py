#!/usr/bin/env python3
"""Fresh confirmatory smoke for causal-endpoint spectral bottlenecks.

This protocol was frozen after the original mean-pooling result was negative and
a post-hoc observer comparison found a promising causal-endpoint signal. It uses
new contexts and paraphrases, a pinned checkpoint, a preregistered middle-layer
causal-endpoint observer, label-blind connectivity-adaptive k selection, and an
explicit token-length nuisance baseline.

A negative scientific result exits normally. Runtime/protocol failures still
raise and fail CI.
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
from scipy.sparse.csgraph import connected_components
from transformers import AutoTokenizer

from observer_comparison import REVISION, extract_mid_observers
from real_model_experiment import (
    AxisSpec,
    Example,
    evaluate_one,
    knn_graph_with_sigma,
    parse_int_list,
)

MODEL = "HuggingFaceTB/SmolLM2-135M"

CONFIRM_AXES: tuple[AxisSpec, ...] = (
    AxisSpec(
        name="stance_confirm",
        template="{actor} {predicate} {obj} after an independent review.",
        contexts=(
            ("The licensing board", "the variance request"),
            ("The research council", "the grant application"),
            ("The procurement panel", "the supplier proposal"),
            ("The appellate committee", "the recommended interpretation"),
            ("The product committee", "the release plan"),
            ("The standards group", "the draft specification"),
            ("The trustees", "the investment policy"),
            ("The accreditation team", "the program revision"),
            ("The safety board", "the mitigation package"),
            ("The editorial committee", "the special issue proposal"),
            ("The planning commission", "the redevelopment plan"),
            ("The oversight group", "the corrective-action proposal"),
        ),
        negative=(
            "recommended turning down",
            "found no basis to endorse",
            "gave its opposition to",
            "advised against adopting",
            "declined to give backing to",
            "judged unacceptable",
        ),
        bridge=(
            "reserved judgment on",
            "saw substantial arguments on both sides of",
            "supported some parts but questioned others in",
            "postponed a final position on",
            "remained evenly divided over",
            "made its support conditional on changes to",
        ),
        positive=(
            "recommended moving ahead with",
            "found sufficient basis to endorse",
            "gave its backing to",
            "advised adopting",
            "gave unqualified support to",
            "judged acceptable",
        ),
    ),
    AxisSpec(
        name="confidence_confirm",
        template="{actor} said that {obj} was {predicate} after a fresh review of the evidence.",
        contexts=(
            ("The laboratory team", "the proposed mechanism"),
            ("The field researcher", "the species identification"),
            ("The forecasting unit", "the demand projection"),
            ("The forensic analyst", "the reconstruction"),
            ("The review scientist", "the measured association"),
            ("The quality engineer", "the root-cause diagnosis"),
            ("The archivist", "the document attribution"),
            ("The risk analyst", "the loss estimate"),
            ("The survey team", "the population estimate"),
            ("The geologist", "the dating conclusion"),
            ("The epidemiologist", "the transmission hypothesis"),
            ("The evaluator", "the reported causal link"),
        ),
        negative=(
            "still too uncertain to establish",
            "supported only weakly",
            "unlikely to be settled",
            "not demonstrated with confidence",
            "best treated as speculative",
            "far from resolved",
        ),
        bridge=(
            "credible but not settled",
            "compatible with competing explanations",
            "supported to an intermediate degree",
            "open to meaningful revision",
            "balanced between confirmation and doubt",
            "provisionally supported but unresolved",
        ),
        positive=(
            "established with high confidence",
            "supported very strongly",
            "settled beyond substantial doubt",
            "demonstrated with high confidence",
            "best treated as established",
            "very likely to be correct",
        ),
    ),
    AxisSpec(
        name="permission_confirm",
        template="{actor} determined that {obj} was {predicate} under the applicable rules.",
        contexts=(
            ("The compliance officer", "the proposed transfer"),
            ("The site administrator", "the requested access"),
            ("The permit authority", "the planned construction"),
            ("The tournament official", "the equipment change"),
            ("The data steward", "the requested disclosure"),
            ("The registrar", "the late filing"),
            ("The platform moderator", "the account action"),
            ("The facilities manager", "the after-hours entry"),
            ("The customs officer", "the declared shipment"),
            ("The research administrator", "the protocol deviation"),
            ("The event organizer", "the schedule alteration"),
            ("The records officer", "the proposed release"),
        ),
        negative=(
            "expressly prohibited",
            "not authorized",
            "disallowed without exception",
            "outside the permitted scope",
            "forbidden under the rule",
            "not permitted to proceed",
        ),
        bridge=(
            "permitted only if conditions were met",
            "subject to case-by-case authorization",
            "neither clearly allowed nor clearly forbidden",
            "allowed only on a provisional basis",
            "conditional on further approval",
            "left unresolved by the rule",
        ),
        positive=(
            "expressly permitted",
            "fully authorized",
            "allowed without restriction",
            "within the permitted scope",
            "allowed under the rule",
            "permitted to proceed",
        ),
    ),
)


def build_confirm_corpus() -> list[Example]:
    rows: list[Example] = []
    for spec in CONFIRM_AXES:
        groups = ((-1, spec.negative), (0, spec.bridge), (1, spec.positive))
        for split, context_slice, phrase_slice in (
            ("train", range(0, 8), range(0, 4)),
            ("test", range(8, 12), range(4, 6)),
        ):
            for context_index in context_slice:
                actor, obj = spec.contexts[context_index]
                for label, phrases in groups:
                    for phrase_index in phrase_slice:
                        rows.append(
                            Example(
                                axis=spec.name,
                                split=split,
                                context_id=f"{spec.name}-c{context_index}",
                                phrase_id=f"{spec.name}-l{label}-p{phrase_index}",
                                label=label,
                                text=spec.template.format(
                                    actor=actor,
                                    predicate=phrases[phrase_index],
                                    obj=obj,
                                ),
                            )
                        )
    return rows


def axis_indices(corpus: list[Example], axis: str, split: str) -> np.ndarray:
    return np.asarray(
        [i for i, row in enumerate(corpus) if row.axis == axis and row.split == split],
        dtype=int,
    )


def choose_connected_k(
    embeddings: np.ndarray,
    corpus: list[Example],
    axis: str,
    candidates: list[int],
) -> tuple[int, list[dict[str, int]]]:
    """Select the smallest registered k yielding one connected training graph."""
    train_idx = axis_indices(corpus, axis, "train")
    train = embeddings[train_idx]
    trace: list[dict[str, int]] = []
    for k in candidates:
        graph, _ = knn_graph_with_sigma(train, k)
        components = int(connected_components(graph, directed=False, return_labels=False))
        trace.append({"k": k, "components": components})
        if components == 1:
            return k, trace
    raise RuntimeError(f"no connected graph for {axis} in k candidates {candidates}")


def token_counts(
    texts: list[str], model_name: str, revision: str, max_length: int
) -> np.ndarray:
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    encoded = tokenizer(
        texts,
        add_special_tokens=True,
        truncation=True,
        max_length=max_length,
        padding=False,
    )
    return np.asarray([len(ids) for ids in encoded["input_ids"]], dtype=float)


def token_length_accuracy(
    counts: np.ndarray,
    corpus: list[Example],
    axis: str,
) -> float:
    train_idx = axis_indices(corpus, axis, "train")
    test_idx = axis_indices(corpus, axis, "test")
    train_y = np.asarray([corpus[i].label for i in train_idx], dtype=float)
    test_y = np.asarray([corpus[i].label for i in test_idx], dtype=int)
    train_x = counts[train_idx]
    test_x = counts[test_idx]
    mean = float(train_x.mean())
    scale = float(train_x.std()) or 1.0
    z_train = (train_x - mean) / scale
    z_test = (test_x - mean) / scale
    design = np.column_stack([np.ones(len(z_train)), z_train])
    ridge = np.diag([0.0, 1e-2])
    beta = np.linalg.solve(design.T @ design + ridge, design.T @ train_y)
    score = np.column_stack([np.ones(len(z_test)), z_test]) @ beta
    pole = test_y != 0
    prediction = np.where(score[pole] >= 0.0, 1, -1)
    return float(np.mean(prediction == test_y[pole]))


def axis_gate(record: dict[str, object], length_accuracy: float) -> dict[str, bool]:
    return {
        "train_alignment": float(record["train_pole_accuracy"]) >= 0.80,
        "heldout_alignment": float(record["heldout_pole_accuracy"]) >= 0.80,
        "bridge_boundary": float(record["heldout_bridge_abs_score_ratio"]) <= 0.85,
        "beats_token_length": float(record["heldout_pole_accuracy"])
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

    lines = [
        "# Confirmatory causal-endpoint spectral smoke",
        "",
        f"**All-axis confirmation:** `{result['confirmed']}`",
        "",
        result["claim_boundary"],
        "",
        "## Axis results",
        "",
    ]
    for axis, item in result["axes"].items():
        r = item["record"]
        lines.extend(
            [
                f"### {axis}",
                "",
                f"- label-blind selected k: `{item['selected_k']}`",
                f"- train pole accuracy: `{r['train_pole_accuracy']:.4f}`",
                f"- held-out pole accuracy: `{r['heldout_pole_accuracy']:.4f}`",
                f"- bridge ratio: `{r['heldout_bridge_abs_score_ratio']:.4f}`",
                f"- token-length held-out accuracy: `{item['token_length_accuracy']:.4f}`",
                f"- supervised centroid held-out accuracy: `{r['centroid_heldout_accuracy']:.4f}`",
                f"- shuffled-label accuracy: `{r['shuffled_label_accuracy']:.4f}`",
                f"- scrambled-representation accuracy: `{r['scrambled_representation_accuracy']:.4f}`",
                f"- conductance: `{r['conductance']:.6f}`",
                f"- lambda2: `{r['lambda2']:.6f}`",
                f"- axis gates pass: `{item['passed']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim boundary",
            "",
            "This is a controlled-corpus confirmation in one pinned small model. Even a positive result would establish neither natural-corpus topology nor a causal relation between spectral bottlenecks and steering/navigation cost. Those require separate experiments.",
            "",
        ]
    )
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--revision", default=REVISION)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=64)
    parser.add_argument("--k-candidates", default="6,8,10,12,14,16,20")
    parser.add_argument("--output", default="results-confirm")
    args = parser.parse_args()

    corpus = build_confirm_corpus()
    observers, model_metadata = extract_mid_observers(
        [row.text for row in corpus],
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    endpoint = observers["causal_endpoint"]
    ks = parse_int_list(args.k_candidates)
    lengths = token_counts(
        [row.text for row in corpus], args.model, args.revision, args.max_length
    )

    axis_results: dict[str, object] = {}
    for spec in CONFIRM_AXES:
        selected_k, connectivity_trace = choose_connected_k(
            endpoint, corpus, spec.name, ks
        )
        record = evaluate_one(
            endpoint, corpus, spec.name, "causal_endpoint_confirm", selected_k
        )
        length_accuracy = token_length_accuracy(lengths, corpus, spec.name)
        gates = axis_gate(record, length_accuracy)
        axis_results[spec.name] = {
            "selected_k": selected_k,
            "connectivity_trace": connectivity_trace,
            "token_length_accuracy": length_accuracy,
            "record": record,
            "gates": gates,
            "passed": all(gates.values()),
        }

    result: dict[str, object] = {
        "claim_boundary": (
            "Fresh confirmatory controlled-corpus smoke. Endpoint observer, checkpoint, "
            "k-selection rule, axes, split, controls, and thresholds were frozen before "
            "inspection of this run."
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
            "observer": "middle-layer causal endpoint",
            "checkpoint_revision": args.revision,
            "k_candidates": ks,
            "k_rule": "smallest candidate producing one connected training graph",
            "train_contexts_per_axis": 8,
            "heldout_contexts_per_axis": 4,
            "train_paraphrases_per_class": 4,
            "heldout_paraphrases_per_class": 2,
            "axis_pass_rule": "all six preregistered gates",
            "experiment_pass_rule": "all three axes pass",
        },
        "axes": axis_results,
        "confirmed": all(bool(item["passed"]) for item in axis_results.values()),
        "corpus": [asdict(row) for row in corpus],
    }
    write_outputs(Path(args.output), result)
    print(
        json.dumps(
            {
                "model": result["model"],
                "axes": result["axes"],
                "confirmed": result["confirmed"],
            },
            indent=2,
        )
    )
    # Scientific negative exits 0 by design.


if __name__ == "__main__":
    main()
