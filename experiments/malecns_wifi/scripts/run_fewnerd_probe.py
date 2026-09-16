"""Stage C: fit a linear probe on frozen MaleCNS readouts, score span-level F1.

Reads stage-B per-token embeddings (already split-labelled), fits a
multinomial logistic-regression probe on ``train`` (regularisation strength
selected on ``validation``), and reports token accuracy and entity-level
micro/macro F1 (seqeval, IO->BIO conversion) on ``test``. Test labels never
touch the probe or its model selection.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from malecns_wifi.telemetry import Telemetry
from malecns_wifi.token_probe import fit_probe, span_metrics, token_accuracy


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document-embeddings", type=Path, required=True, help="stage-B npz")
    parser.add_argument("--fine-names", type=Path, required=True, help="JSON list of fine label names")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", default="malecns")
    args = parser.parse_args()

    data = np.load(args.document_embeddings, allow_pickle=False)
    label_names = json.loads(args.fine_names.read_text(encoding="utf-8"))
    embeddings, labels, split = data["embeddings"], data["fine_label"], data["doc_split"]
    offsets = data["offsets"]

    telemetry = Telemetry(f"stage-c-fewnerd-{args.variant}", config={"variant": args.variant})
    masks = {s: split == s for s in ("train", "validation", "test")}
    started = time.perf_counter()
    model, best_c, val_acc = fit_probe(
        embeddings[masks["train"]], labels[masks["train"]], embeddings[masks["validation"]], labels[masks["validation"]]
    )
    fit_seconds = time.perf_counter() - started

    test_pred = model.predict(embeddings[masks["test"]])
    test_true = labels[masks["test"]]
    token_acc = token_accuracy(test_true, test_pred)

    # regroup test predictions/labels back into per-sentence sequences for span scoring
    sentence_count = int(len(offsets) - 1)
    doc_split = data["doc_split"]
    true_seqs, pred_seqs = [], []
    cursor = 0
    for sentence in range(sentence_count):
        start, stop = int(offsets[sentence]), int(offsets[sentence + 1])
        if doc_split[start] != "test":
            continue
        n = stop - start
        true_seqs.append(test_true[cursor:cursor + n])
        pred_seqs.append(test_pred[cursor:cursor + n])
        cursor += n

    metrics = span_metrics(true_seqs, pred_seqs, label_names)
    payload = {
        "schema": "papers/malecns-fewnerd-probe-v1",
        "variant": args.variant,
        "probe": {"C": best_c, "val_accuracy": val_acc, "fit_seconds": fit_seconds},
        "test_token_accuracy": token_acc,
        "test_span_metrics": _jsonable(metrics),
        "test_sentences": len(true_seqs),
        "tokens": {s: int(masks[s].sum()) for s in masks},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    telemetry.summary({"val_accuracy": val_acc, "test_token_accuracy": token_acc,
                       "test_micro_f1": metrics["micro_f1"], "test_macro_f1": metrics["macro_f1"]})
    telemetry.finish()
    print(json.dumps({"event": "fewnerd_probe_complete", "variant": args.variant,
                      "test_token_accuracy": token_acc, "test_micro_f1": metrics["micro_f1"],
                      "test_macro_f1": metrics["macro_f1"]}), flush=True)


if __name__ == "__main__":
    main()
