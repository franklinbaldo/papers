#!/usr/bin/env python3
"""Exploratory all-layer scan of the confidence spectral transfer signal.

This is intentionally *not* a confirmation protocol. It follows a successful
135M middle-layer result and a failed 360M middle-layer replication. The goal is
to report the full depth profile, without selecting a favorable layer and
calling it confirmatory.

Corpus, k=8 graph rule, explicit->implicit realization shift, and metric
thresholds are inherited unchanged from confidence_transfer.py. Every causal
endpoint hidden-state layer is evaluated and written to the artifact.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
from pathlib import Path

import numpy as np
import scipy
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from confidence_transfer import (
    AXIS,
    REGISTERED_K,
    build_transfer_corpus,
    explicit_term_hits,
    transfer_gates,
)
from confirmatory_endpoint import token_counts, token_length_accuracy
from real_model_experiment import configure_padding, evaluate_one, normalize_rows


def extract_endpoint_layers(
    texts: list[str],
    *,
    model_name: str,
    revision: str,
    batch_size: int,
    max_length: int,
) -> tuple[dict[int, np.ndarray], dict[str, object]]:
    torch.manual_seed(0)
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision)
    padding_strategy = configure_padding(tokenizer, model)
    tokenizer.padding_side = "right"
    model.eval().to("cpu")

    layer_count = int(model.config.num_hidden_layers)
    storage: dict[int, list[np.ndarray]] = {
        index: [] for index in range(1, layer_count + 1)
    }

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
            for index in range(1, layer_count + 1):
                hidden = outputs.hidden_states[index].to(torch.float32)
                endpoint = hidden[batch_index, last_position]
                storage[index].append(endpoint.cpu().numpy())
            del outputs

    arrays = {
        index: normalize_rows(np.concatenate(parts, axis=0))
        for index, parts in storage.items()
    }
    metadata = {
        "model": model_name,
        "requested_revision": revision,
        "resolved_revision": getattr(model.config, "_commit_hash", None),
        "hidden_size": int(model.config.hidden_size),
        "num_hidden_layers": layer_count,
        "observer": "causal endpoint at every hidden-state layer, excluding embedding index 0",
        "padding_strategy": padding_strategy,
    }
    return arrays, metadata


def contiguous_windows(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []
    ordered = sorted(indices)
    windows = [[ordered[0]]]
    for index in ordered[1:]:
        if index == windows[-1][-1] + 1:
            windows[-1].append(index)
        else:
            windows.append([index])
    return windows


def write_outputs(output: Path, result: dict[str, object]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    records = result["records"]
    with (output / "depth_profile.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "layer_index",
            "normalized_depth",
            "train_pole_accuracy",
            "heldout_pole_accuracy",
            "heldout_bridge_abs_score_ratio",
            "centroid_heldout_accuracy",
            "shuffled_label_accuracy",
            "scrambled_representation_accuracy",
            "conductance",
            "lambda2",
            "passes_transfer_gates",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record[key] for key in fieldnames})

    best_heldout = max(records, key=lambda row: row["heldout_pole_accuracy"])
    best_train = max(records, key=lambda row: row["train_pole_accuracy"])
    lines = [
        "# Confidence spectral depth scan",
        "",
        "**Exploratory only. Favorable layers found here require a new frozen corpus for confirmation.**",
        "",
        f"- model: `{result['model']['model']}`",
        f"- revision: `{result['model']['resolved_revision']}`",
        f"- hidden layers scanned: `{result['model']['num_hidden_layers']}`",
        f"- registered graph k: `{REGISTERED_K}`",
        f"- token-length held-out accuracy: `{result['token_length_accuracy']:.4f}`",
        f"- layers passing all inherited transfer gates: `{result['passing_layers']}`",
        f"- contiguous passing windows: `{result['passing_windows']}`",
        "",
        "## Best descriptive layers",
        "",
        f"- best held-out layer: `{best_heldout['layer_index']}` ({best_heldout['normalized_depth']:.3f} depth), held-out `{best_heldout['heldout_pole_accuracy']:.4f}`, train `{best_heldout['train_pole_accuracy']:.4f}`, bridge `{best_heldout['heldout_bridge_abs_score_ratio']:.4f}`",
        f"- best train-alignment layer: `{best_train['layer_index']}` ({best_train['normalized_depth']:.3f} depth), train `{best_train['train_pole_accuracy']:.4f}`, held-out `{best_train['heldout_pole_accuracy']:.4f}`",
        "",
        "## Full profile",
        "",
        "| layer | depth | train | implicit test | bridge ratio | conductance | lambda2 | gates |",
        "|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in records:
        lines.append(
            f"| {row['layer_index']} | {row['normalized_depth']:.3f} | "
            f"{row['train_pole_accuracy']:.3f} | {row['heldout_pole_accuracy']:.3f} | "
            f"{row['heldout_bridge_abs_score_ratio']:.3f} | {row['conductance']:.4f} | "
            f"{row['lambda2']:.4f} | {'PASS' if row['passes_transfer_gates'] else '—'} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The scan is a mechanism diagnostic after observing the outcomes at the preregistered middle layers. It can distinguish disappearance from depth displacement, but it cannot establish a newly discovered layer as confirmatory evidence because layer choice is now post-hoc.",
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

    corpus = build_transfer_corpus()
    hits = explicit_term_hits(corpus)
    if hits:
        raise RuntimeError(f"implicit test contains registered explicit terms: {hits}")

    texts = [row.text for row in corpus]
    layers, model_metadata = extract_endpoint_layers(
        texts,
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    lengths = token_counts(texts, args.model, args.revision, args.max_length)
    length_accuracy = token_length_accuracy(lengths, corpus, AXIS)

    records: list[dict[str, object]] = []
    layer_count = int(model_metadata["num_hidden_layers"])
    for index in range(1, layer_count + 1):
        record = evaluate_one(
            layers[index], corpus, AXIS, f"endpoint_layer_{index}", REGISTERED_K
        )
        gates = transfer_gates(record, length_accuracy)
        records.append(
            {
                "layer_index": index,
                "normalized_depth": index / layer_count,
                **record,
                "passes_transfer_gates": all(gates.values()),
                "gates": gates,
            }
        )

    passing_layers = [
        int(row["layer_index"]) for row in records if row["passes_transfer_gates"]
    ]
    result: dict[str, object] = {
        "claim_boundary": (
            "Post-outcome exploratory depth scan. Full profile is reported; no layer "
            "identified here counts as a new confirmation without a fresh frozen corpus."
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
            "corpus": "unchanged explicit-confidence train -> implicit-evidence test",
            "registered_k": REGISTERED_K,
            "layer_scan": "all causal endpoint hidden states 1..N",
            "thresholds": "unchanged transfer_gates",
            "selection": "none; full depth profile reported",
        },
        "token_length_accuracy": length_accuracy,
        "passing_layers": passing_layers,
        "passing_windows": contiguous_windows(passing_layers),
        "records": records,
    }
    write_outputs(Path(args.output), result)
    print(
        json.dumps(
            {
                "model": result["model"],
                "token_length_accuracy": length_accuracy,
                "passing_layers": passing_layers,
                "passing_windows": result["passing_windows"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
