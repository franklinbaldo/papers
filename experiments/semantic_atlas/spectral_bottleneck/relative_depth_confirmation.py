#!/usr/bin/env python3
"""Fresh cross-model confirmation of the ~0.56-depth confidence mode.

Exploratory all-layer scans found the confidence transfer signal near the same
relative depth in SmolLM2-135M and SmolLM2-360M. This follow-up freezes that
mechanistic prediction *before* seeing a new corpus:

    target layer = round(0.56 * num_hidden_layers)

No layer scan or layer selection is permitted in this run. The explicit training
sentences and implicit held-out evidence descriptions are entirely new relative
to the earlier confirmation/transfer corpora. k=8 and the inherited transfer
thresholds remain unchanged. Each model must also pass a fresh training-alignment
gate. The cross-model hypothesis passes only if both pinned checkpoints pass.
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
from transformers import AutoModelForCausalLM, AutoTokenizer

from confidence_transfer import FORBIDDEN_EXPLICIT_TERMS, REGISTERED_K, transfer_gates
from confirmatory_endpoint import token_counts, token_length_accuracy
from real_model_experiment import (
    Example,
    configure_padding,
    evaluate_one,
    normalize_rows,
)

RELATIVE_DEPTH = 0.56
AXIS = "confidence_relative_depth_confirm"

TRAIN_CONTEXTS = (
    ("The validation team", "the reported treatment effect"),
    ("The remote-sensing group", "the vegetation estimate"),
    ("The materials laboratory", "the fatigue mechanism"),
    ("The replication consortium", "the behavioral effect"),
    ("The hydrology team", "the runoff estimate"),
    ("The benchmark committee", "the measured performance gain"),
    ("The field observatory", "the detected periodic signal"),
    ("The calibration group", "the instrument-bias estimate"),
)

NEGATIVE_EXPLICIT = (
    "assigned very low confidence to",
    "treated as seriously uncertain",
    "regarded as too weakly established",
    "considered far from settled",
)
BRIDGE_EXPLICIT = (
    "assigned moderate confidence to",
    "treated as plausible but uncertain",
    "regarded as provisionally supported",
    "considered credible but not settled",
)
POSITIVE_EXPLICIT = (
    "assigned very high confidence to",
    "treated as highly certain",
    "regarded as firmly established",
    "considered effectively settled",
)

IMPLICIT_CLAIMS = (
    "the new catalyst reduces energy use",
    "the diagnostic marker predicts recurrence",
    "the revised routing policy reduces congestion",
    "the habitat intervention increases juvenile survival",
    "the compiler change lowers execution latency",
    "the irrigation method improves soil retention",
    "the imaging method detects the target lesion",
    "the revised battery chemistry slows capacity loss",
)

NEGATIVE_IMPLICIT = (
    "the original pattern vanished in four larger replications performed by separate teams",
    "follow-up measurements changed sign across sites and the initial signal disappeared under blinded reanalysis",
    "the apparent gain was traced to one faulty sensor and was absent after recalibration",
    "two independent repeats produced null effects while a third produced the opposite direction",
    "the benchmark advantage disappeared on every held-out workload and under a second implementation",
    "repeated field seasons produced inconsistent effects with no stable direction",
    "independent readers and a second imaging platform failed to recover the original pattern",
    "larger cycling tests produced no repeat of the initial advantage and exposed an instrumentation artifact",
)
BRIDGE_IMPLICIT = (
    "two independent replications recovered the pattern while two comparable replications returned near-baseline results",
    "one site reproduced the association and another site produced a smaller effect in the opposite direction",
    "the primary sensor showed the gain while a second calibrated sensor showed little change",
    "some field seasons reproduced the effect while others remained close to baseline",
    "the held-out workloads split evenly between measurable gains and no meaningful difference",
    "one soil type showed the effect clearly while a matched site showed almost no change",
    "one reader group reproduced the pattern while another group produced mixed classifications",
    "one cycling protocol reproduced the advantage while a second protocol showed almost no difference",
)
POSITIVE_IMPLICIT = (
    "four independent preregistered replications recovered the same effect with closely matching estimates",
    "separate sites and analysis teams recovered the same association with narrow error ranges",
    "three calibrated sensors and an external audit all recovered the same directional gain",
    "independent field seasons and a second research group reproduced the effect with similar magnitude",
    "every held-out workload and an independent implementation reproduced the same performance gain",
    "multiple sites and measurement methods recovered the same improvement across repeated seasons",
    "independent readers and a second imaging platform recovered closely matching detection gains",
    "two laboratories and three cycling protocols reproduced nearly the same reduction in capacity loss",
)


def build_fresh_corpus() -> list[Example]:
    rows: list[Example] = []
    groups = ((-1, NEGATIVE_EXPLICIT), (0, BRIDGE_EXPLICIT), (1, POSITIVE_EXPLICIT))
    for context_index, (actor, obj) in enumerate(TRAIN_CONTEXTS):
        for label, phrases in groups:
            for phrase_index, phrase in enumerate(phrases):
                rows.append(
                    Example(
                        axis=AXIS,
                        split="train",
                        context_id=f"fresh-explicit-c{context_index}",
                        phrase_id=f"fresh-explicit-l{label}-p{phrase_index}",
                        label=label,
                        text=f"{actor} {phrase} {obj} after reviewing the complete analysis.",
                    )
                )

    implicit_groups = (
        (-1, NEGATIVE_IMPLICIT),
        (0, BRIDGE_IMPLICIT),
        (1, POSITIVE_IMPLICIT),
    )
    for context_index, claim in enumerate(IMPLICIT_CLAIMS):
        for label, scenarios in implicit_groups:
            rows.append(
                Example(
                    axis=AXIS,
                    split="test",
                    context_id=f"fresh-implicit-c{context_index}",
                    phrase_id=f"fresh-implicit-l{label}-p{context_index}",
                    label=label,
                    text=f"For the claim that {claim}, {scenarios[context_index]}.",
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


def extract_target_endpoint(
    texts: list[str],
    *,
    model_name: str,
    revision: str,
    batch_size: int,
    max_length: int,
) -> tuple[np.ndarray, dict[str, object]]:
    torch.manual_seed(0)
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision)
    padding_strategy = configure_padding(tokenizer, model)
    tokenizer.padding_side = "right"
    model.eval().to("cpu")

    layer_count = int(model.config.num_hidden_layers)
    target_layer = max(1, min(layer_count, int(round(RELATIVE_DEPTH * layer_count))))
    parts: list[np.ndarray] = []
    with torch.inference_mode():
        for start in range(0, len(texts), batch_size):
            encoded = tokenizer(
                texts[start : start + batch_size],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
            )
            outputs = model(
                **encoded,
                output_hidden_states=True,
                use_cache=False,
                return_dict=True,
            )
            attention = encoded["attention_mask"]
            last_position = attention.sum(dim=1).to(torch.long) - 1
            batch_index = torch.arange(attention.shape[0], dtype=torch.long)
            hidden = outputs.hidden_states[target_layer].to(torch.float32)
            endpoint = hidden[batch_index, last_position]
            parts.append(endpoint.cpu().numpy())
            del outputs

    embeddings = normalize_rows(np.concatenate(parts, axis=0))
    metadata = {
        "model": model_name,
        "requested_revision": revision,
        "resolved_revision": getattr(model.config, "_commit_hash", None),
        "hidden_size": int(model.config.hidden_size),
        "num_hidden_layers": layer_count,
        "relative_depth_rule": RELATIVE_DEPTH,
        "target_layer": target_layer,
        "actual_relative_depth": target_layer / layer_count,
        "observer": "causal endpoint at preregistered relative-depth layer",
        "padding_strategy": padding_strategy,
    }
    return embeddings, metadata


def gates_with_fresh_train(record: dict[str, object], length_accuracy: float) -> dict[str, bool]:
    gates = {"fresh_train_alignment": float(record["train_pole_accuracy"]) >= 0.80}
    gates.update(transfer_gates(record, length_accuracy))
    return gates


def write_outputs(output: Path, result: dict[str, object]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "corpus.json").write_text(
        json.dumps(result["corpus"], indent=2) + "\n", encoding="utf-8"
    )
    r = result["record"]
    m = result["model"]
    lines = [
        "# Relative-depth confidence confirmation",
        "",
        f"**Model passes all frozen gates:** `{result['supported']}`",
        "",
        f"- model: `{m['model']}`",
        f"- revision: `{m['resolved_revision']}`",
        f"- frozen depth rule: `{RELATIVE_DEPTH}`",
        f"- selected layer: `{m['target_layer']}/{m['num_hidden_layers']}` = `{m['actual_relative_depth']:.4f}`",
        f"- registered k: `{REGISTERED_K}`",
        f"- train pole accuracy: `{r['train_pole_accuracy']:.4f}`",
        f"- fresh implicit held-out accuracy: `{r['heldout_pole_accuracy']:.4f}`",
        f"- bridge ratio: `{r['heldout_bridge_abs_score_ratio']:.4f}`",
        f"- token-length accuracy: `{result['token_length_accuracy']:.4f}`",
        f"- supervised centroid accuracy: `{r['centroid_heldout_accuracy']:.4f}`",
        f"- shuffled-label accuracy: `{r['shuffled_label_accuracy']:.4f}`",
        f"- scrambled-representation accuracy: `{r['scrambled_representation_accuracy']:.4f}`",
        f"- forbidden explicit-term hits in implicit test: `{len(result['explicit_term_hits'])}`",
        "",
        "## Gates",
        "",
    ]
    lines.extend(
        f"- {'PASS' if passed else 'FAIL'} — `{name}`"
        for name, passed in result["gates"].items()
    )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "This confirms or falsifies one preregistered relative-depth prediction on a fresh controlled corpus for one pinned model. Cross-model confirmation requires both matrix jobs to pass independently. It does not establish natural-corpus topology or causal steering effects.",
            "",
        ]
    )
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=96)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    corpus = build_fresh_corpus()
    hits = explicit_term_hits(corpus)
    if hits:
        raise RuntimeError(f"fresh implicit corpus leaked explicit confidence terms: {hits}")
    texts = [row.text for row in corpus]
    embeddings, model_metadata = extract_target_endpoint(
        texts,
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    record = evaluate_one(
        embeddings,
        corpus,
        AXIS,
        "relative_depth_confirm",
        REGISTERED_K,
    )
    lengths = token_counts(texts, args.model, args.revision, args.max_length)
    length_accuracy = token_length_accuracy(lengths, corpus, AXIS)
    gates = gates_with_fresh_train(record, length_accuracy)
    result: dict[str, object] = {
        "claim_boundary": (
            "Fresh preregistered cross-model relative-depth test after exploratory depth "
            "scans. No layer selection or corpus reuse is allowed in this run."
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
            "relative_depth_rule": RELATIVE_DEPTH,
            "registered_k": REGISTERED_K,
            "train_examples": 96,
            "implicit_test_examples": 24,
            "fresh_corpus": True,
            "cross_model_pass_rule": "both pinned model jobs must independently pass all six gates",
        },
        "record": record,
        "token_length_accuracy": length_accuracy,
        "explicit_term_hits": hits,
        "gates": gates,
        "supported": all(gates.values()),
        "corpus": [asdict(row) for row in corpus],
    }
    write_outputs(Path(args.output), result)
    print(
        json.dumps(
            {
                "model": result["model"],
                "record": record,
                "token_length_accuracy": length_accuracy,
                "gates": gates,
                "supported": result["supported"],
            },
            indent=2,
        )
    )
    # Scientific negative exits 0 by design.


if __name__ == "__main__":
    main()
