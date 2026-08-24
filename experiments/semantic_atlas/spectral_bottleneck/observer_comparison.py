#!/usr/bin/env python3
"""Observer-sensitivity follow-up for the real-model spectral smoke.

The first frozen run used mean pooling and was negative. This follow-up keeps the
same corpus, split, model, graph construction, k values, labels and thresholds,
but compares that observer with the final non-padding token state at the same
registered middle layer. The endpoint observer is exploratory/post-hoc and
cannot retroactively rescue the preregistered mean-pooling result.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from real_model_experiment import (
    AXES,
    build_corpus,
    configure_padding,
    evaluate_one,
    parse_int_list,
)

MODEL = "HuggingFaceTB/SmolLM2-135M"
REVISION = "93efa2f097d58c2a74874c7e644dbc9b0cee75a2"


def normalize_rows(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.clip(norms, 1e-12, None)


def extract_mid_observers(
    texts: list[str],
    *,
    model_name: str,
    revision: str,
    batch_size: int,
    max_length: int,
) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    torch.manual_seed(0)
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision)
    padding_strategy = configure_padding(tokenizer, model)
    tokenizer.padding_side = "right"
    model.eval().to("cpu")

    layer_count = int(model.config.num_hidden_layers)
    mid_index = max(1, int(round(layer_count * 0.50)))
    mean_parts: list[np.ndarray] = []
    endpoint_parts: list[np.ndarray] = []

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
            hidden = outputs.hidden_states[mid_index].to(torch.float32)
            attention = encoded["attention_mask"]
            mask = attention.unsqueeze(-1).to(torch.float32)
            mean_state = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1.0)
            last_position = attention.sum(dim=1).to(torch.long) - 1
            endpoint_state = hidden[
                torch.arange(hidden.shape[0], dtype=torch.long), last_position
            ]
            mean_parts.append(mean_state.cpu().numpy())
            endpoint_parts.append(endpoint_state.cpu().numpy())

    observers = {
        "mean": normalize_rows(np.concatenate(mean_parts, axis=0)),
        "causal_endpoint": normalize_rows(np.concatenate(endpoint_parts, axis=0)),
    }
    metadata = {
        "model": model_name,
        "requested_revision": revision,
        "resolved_revision": getattr(model.config, "_commit_hash", None),
        "hidden_size": int(model.config.hidden_size),
        "num_hidden_layers": layer_count,
        "mid_hidden_state_index": mid_index,
        "padding_strategy": padding_strategy,
        "padding_side": tokenizer.padding_side,
        "observers": {
            "mean": "attention-mask weighted mean of middle-layer token states",
            "causal_endpoint": "middle-layer hidden state at final non-padding input token",
        },
    }
    return observers, metadata


def median(records: list[dict[str, object]], key: str) -> float:
    return float(np.median([float(record[key]) for record in records]))


def summarize_observer(records: list[dict[str, object]]) -> dict[str, object]:
    axes = sorted({str(record["axis"]) for record in records})
    axis_accuracy = {
        axis: median(
            [record for record in records if record["axis"] == axis],
            "heldout_pole_accuracy",
        )
        for axis in axes
    }
    robust_flags = [
        float(record["heldout_pole_accuracy"]) >= 0.65
        and float(record["heldout_bridge_abs_score_ratio"]) <= 0.95
        and float(record["scrambled_representation_accuracy"]) <= 0.70
        for record in records
    ]
    aggregate = {
        "median_heldout_pole_accuracy": median(records, "heldout_pole_accuracy"),
        "median_bridge_abs_score_ratio": median(
            records, "heldout_bridge_abs_score_ratio"
        ),
        "median_centroid_heldout_accuracy": median(
            records, "centroid_heldout_accuracy"
        ),
        "median_shuffled_label_accuracy": median(records, "shuffled_label_accuracy"),
        "median_scrambled_representation_accuracy": median(
            records, "scrambled_representation_accuracy"
        ),
        "median_conductance": median(records, "conductance"),
        "median_lambda2": median(records, "lambda2"),
        "robust_axis_k_fraction": float(np.mean(robust_flags)),
        "axis_median_heldout_accuracy": axis_accuracy,
    }
    gates = {
        "heldout_semantic_partition": aggregate["median_heldout_pole_accuracy"] >= 0.70,
        "bridges_near_spectral_boundary": aggregate[
            "median_bridge_abs_score_ratio"
        ]
        <= 0.85,
        "shuffled_labels_near_chance": aggregate["median_shuffled_label_accuracy"]
        <= 0.58,
        "scrambled_geometry_near_chance": aggregate[
            "median_scrambled_representation_accuracy"
        ]
        <= 0.65,
        "not_driven_by_one_axis": min(axis_accuracy.values()) >= 0.60,
        "robust_across_axis_and_k": aggregate["robust_axis_k_fraction"] >= 0.60,
    }
    return {
        "aggregate": aggregate,
        "gates": gates,
        "passes_same_thresholds": all(gates.values()),
    }


def write_outputs(
    output: Path,
    result: dict[str, object],
    observers: dict[str, np.ndarray],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    np.savez_compressed(output / "mid-observers.npz", **observers)

    mean = result["observers"]["mean"]
    endpoint = result["observers"]["causal_endpoint"]
    lines = [
        "# Semantic spectral observer comparison",
        "",
        "The original mean-pooling result remains the preregistered result. The causal-endpoint observer is a post-hoc sensitivity analysis.",
        "",
        "## Mean observer (frozen replication)",
        "",
        f"- held-out pole accuracy: `{mean['aggregate']['median_heldout_pole_accuracy']:.4f}`",
        f"- bridge ratio: `{mean['aggregate']['median_bridge_abs_score_ratio']:.4f}`",
        f"- same thresholds pass: `{mean['passes_same_thresholds']}`",
        "",
        "## Causal-endpoint observer (exploratory)",
        "",
        f"- held-out pole accuracy: `{endpoint['aggregate']['median_heldout_pole_accuracy']:.4f}`",
        f"- bridge ratio: `{endpoint['aggregate']['median_bridge_abs_score_ratio']:.4f}`",
        f"- supervised centroid held-out accuracy: `{endpoint['aggregate']['median_centroid_heldout_accuracy']:.4f}`",
        f"- shuffled-label accuracy: `{endpoint['aggregate']['median_shuffled_label_accuracy']:.4f}`",
        f"- scrambled-representation accuracy: `{endpoint['aggregate']['median_scrambled_representation_accuracy']:.4f}`",
        f"- robust axis×k fraction: `{endpoint['aggregate']['robust_axis_k_fraction']:.4f}`",
        f"- same thresholds pass: `{endpoint['passes_same_thresholds']}`",
        "",
        "### Endpoint per-axis held-out accuracy",
        "",
    ]
    for axis, value in endpoint["aggregate"]["axis_median_heldout_accuracy"].items():
        lines.append(f"- {axis}: `{value:.4f}`")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "Observer sensitivity can diagnose why the first smoke failed, but a post-hoc observer cannot convert that negative preregistered result into confirmation. Any promising endpoint result requires a newly frozen confirmatory corpus/split.",
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
    parser.add_argument("--k-values", default="6,10,14")
    parser.add_argument("--output", default="results-observers")
    args = parser.parse_args()

    corpus = build_corpus()
    observers, model_metadata = extract_mid_observers(
        [row.text for row in corpus],
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    ks = parse_int_list(args.k_values)
    observer_results: dict[str, object] = {}
    all_records: dict[str, list[dict[str, object]]] = {}
    for observer_name, embeddings in observers.items():
        records = [
            evaluate_one(embeddings, corpus, axis.name, observer_name, k)
            for axis in AXES
            for k in ks
        ]
        all_records[observer_name] = records
        observer_results[observer_name] = summarize_observer(records)

    result: dict[str, object] = {
        "claim_boundary": (
            "Post-hoc observer-sensitivity analysis. Mean pooling is the frozen first "
            "result; causal endpoint is exploratory and needs independent confirmation."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        },
        "model": model_metadata,
        "design": {
            "corpus_and_split": "identical to first real-model smoke",
            "k_values": ks,
            "registered_first_result_observer": "mean",
            "exploratory_observer": "causal_endpoint",
            "all_other_graph_metrics_and_thresholds": "unchanged",
        },
        "observers": observer_results,
        "records": all_records,
    }
    write_outputs(Path(args.output), result, observers)
    print(
        json.dumps(
            {
                "model": result["model"],
                "observers": result["observers"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
