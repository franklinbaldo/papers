"""Real-encoder gate: does the semantic representation localise the span at all?

Runs entirely without the connectome. If no signal here separates the annotated
dispositivo from the rest of the document, the tagger experiment would be asking
the fly to recover information its input never carried, and no amount of GPU
fixes that.

Default model is Qwen3-Embedding-0.6B, which needs roughly 2.4GB resident in
float32. Use --model to substitute a smaller encoder when validating the pipeline
on a machine that cannot hold it.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from malecns_wifi.encoder_gate import (
    build_hierarchy,
    candidate_signals,
    plan_chunks,
    score_signal,
)


class TransformerEncoder:
    """Mean-pooled sentence embeddings from any HuggingFace encoder."""

    def __init__(self, model_name: str, device: str = "cpu", max_length: int = 1024):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device).eval()
        self.device = device
        self.max_length = max_length

    def encode(self, texts):
        vectors = []
        with self.torch.no_grad():
            for start in range(0, len(texts), 8):
                batch = self.tokenizer(
                    list(texts[start : start + 8]),
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                ).to(self.device)
                hidden = self.model(**batch).last_hidden_state
                mask = batch["attention_mask"].unsqueeze(-1).to(hidden.dtype)
                pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                vectors.append(pooled.float().cpu().numpy())
        return np.vstack(vectors)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, nargs="+", required=True)
    parser.add_argument("--model", default="Qwen/Qwen3-Embedding-0.6B")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--tag", default="dispositivo: o resultado do julgamento")
    parser.add_argument("--fine-size", type=int, default=64)
    parser.add_argument("--scales", type=int, nargs="+", default=[256, 1024])
    parser.add_argument("--tau", type=float, default=0.5)
    parser.add_argument("--max-documents", type=int, default=0)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/runtime-v1/encoder-gate.json")
    )
    args = parser.parse_args()

    encoder = TransformerEncoder(args.model, device=args.device)
    tokenizer = encoder.tokenizer

    documents = []
    for path in args.corpus:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                documents.append(json.loads(line))
    if args.max_documents:
        documents = documents[: args.max_documents]

    pooled: dict[str, list[np.ndarray]] = defaultdict(list)
    pooled_labels: list[np.ndarray] = []
    per_document = []

    for record in documents:
        text = record["text"]
        spans = [
            (int(s["start"]), int(s["end"]))
            for s in record.get("label", [])
            if s.get("category") == "resultado"
        ]
        if not spans:
            continue
        encoded = tokenizer(text, return_offsets_mapping=True, add_special_tokens=False)
        offsets = encoded["offset_mapping"]
        plan = plan_chunks(len(offsets), fine_size=args.fine_size, scales=args.scales)

        def text_of(span, offsets=offsets, text=text):
            first, last = span
            if first >= len(offsets) or last <= first:
                return ""
            return text[offsets[first][0] : offsets[min(last, len(offsets)) - 1][1]]

        # A fine chunk is positive when it overlaps an annotated resultado span.
        labels = np.zeros(len(plan.fine_spans), dtype=bool)
        for index, (first, last) in enumerate(plan.fine_spans):
            if first >= len(offsets):
                continue
            chunk_start = offsets[first][0]
            chunk_end = offsets[min(last, len(offsets)) - 1][1]
            labels[index] = any(
                chunk_start < end and start < chunk_end for start, end in spans
            )
        if not labels.any():
            continue

        hierarchy = build_hierarchy(text_of, plan, encoder, args.tag)
        signals = candidate_signals(hierarchy, tau=args.tau)
        per_document.append(
            {
                "doc_id": record.get("info", {}).get("doc_id", "?"),
                "tokens": len(offsets),
                "fine_chunks": len(plan.fine_spans),
                "positive_chunks": int(labels.sum()),
                "scores": {
                    name: score_signal(name, values, labels, fine_size=args.fine_size)
                    for name, values in signals.items()
                },
            }
        )
        for name, values in signals.items():
            pooled[name].append(np.asarray(values, dtype=np.float64))
        pooled_labels.append(labels)
        print(f"  {per_document[-1]['doc_id']}: {len(plan.fine_spans)} chunks, "
              f"{int(labels.sum())} positive", flush=True)

    if not per_document:
        raise SystemExit("no document carried an annotated resultado span")

    labels = np.concatenate(pooled_labels)
    overall = {
        name: score_signal(name, np.concatenate(values), labels, fine_size=args.fine_size)
        for name, values in pooled.items()
    }
    report = {
        "model": args.model,
        "tag": args.tag,
        "fine_size": args.fine_size,
        "scales": args.scales,
        "documents": len(per_document),
        "pooled_chunks": int(labels.size),
        "positive_rate": float(labels.mean()),
        "pooled": overall,
        "per_document": per_document,
        "claim_boundary": (
            "No connectome involved. Measures whether the semantic representation "
            "localises the annotated span at all; a pass here is a precondition for "
            "the tagger experiment, not evidence for it."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")

    baseline = report["positive_rate"]
    print(f"\n{len(per_document)} documents, {labels.size} chunks, "
          f"{baseline:.3f} positive (random AUPRC)")
    print(f"{'signal':<28}{'AUPRC':>8}{'lift':>7}{'r_pb':>8}{'F1':>7}"
          f"{'startErr':>10}{'endErr':>9}")
    for name, row in sorted(overall.items(), key=lambda kv: -(kv[1]["auprc"] or 0)):
        print(
            f"{name:<28}{row['auprc']:>8.3f}{row['auprc']/baseline:>7.1f}"
            f"{row['point_biserial']:>8.3f}{row['best_f1']:>7.3f}"
            f"{row['start_error_tokens']:>10.0f}{row['end_error_tokens']:>9.0f}"
        )
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
