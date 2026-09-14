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
    leave_one_document_out_auprc,
    plan_chunks,
    relative_position,
    score_signal,
    sensation_features,
)


class TransformerEncoder:
    """Mean-pooled sentence embeddings from any HuggingFace encoder."""

    def __init__(self, model_name: str, device: str = "cpu", max_length: int | None = None):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device).eval()
        self.device = device
        self.context_limit = int(
            getattr(self.model.config, "max_position_embeddings", 0)
            or getattr(self.tokenizer, "model_max_length", 0)
            or 512
        )
        self.max_length = min(max_length or self.context_limit, self.context_limit)

    def check_scales(self, scales) -> None:
        """A parent longer than the model's context is not a parent.

        Silently truncating it would leave a "containing" chunk that does not
        contain its children, and every relation built on it would be measuring
        the wrong thing. Better to refuse than to report a corrupted hierarchy.
        """
        too_long = [scale for scale in scales if scale > self.context_limit]
        if too_long:
            raise SystemExit(
                f"parent scales {too_long} exceed this model's {self.context_limit}-token "
                f"context; a truncated parent no longer contains its children. "
                f"Use --scales within {self.context_limit}, or a longer-context encoder."
            )

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
    parser.add_argument(
        "--tags",
        nargs="+",
        default=None,
        help="span categories to cache masks and flavour embeddings for (multi-tag run)",
    )
    parser.add_argument("--fine-size", type=int, default=64)
    parser.add_argument("--scales", type=int, nargs="+", default=[256, 1024])
    parser.add_argument("--tau", type=float, default=0.5)
    parser.add_argument("--max-documents", type=int, default=0)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/runtime-v1/encoder-gate.json")
    )
    args = parser.parse_args()

    encoder = TransformerEncoder(args.model, device=args.device)
    encoder.check_scales(args.scales)
    tokenizer = encoder.tokenizer
    print(f"{args.model}: {encoder.context_limit}-token context, scales {args.scales}")

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
    sensation: list[np.ndarray] = []
    positions: list[np.ndarray] = []
    absolute: list[np.ndarray] = []
    groups: list[np.ndarray] = []
    tag_masks: list[np.ndarray] = []

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

        # Multi-tag masks share this document's chunk plan exactly, so the fly sees
        # one sensation stream and every tag is expressed on the same time axis.
        if args.tags:
            per_tag = np.zeros((len(plan.fine_spans), len(args.tags)), dtype=np.float32)
            for column, category in enumerate(args.tags):
                category_spans = [
                    (int(s["start"]), int(s["end"]))
                    for s in record.get("label", [])
                    if s.get("category") == category
                ]
                for index, (first, last) in enumerate(plan.fine_spans):
                    if first >= len(offsets):
                        continue
                    chunk_start = offsets[first][0]
                    chunk_end = offsets[min(last, len(offsets)) - 1][1]
                    per_tag[index, column] = float(
                        any(chunk_start < end and start < chunk_end
                            for start, end in category_spans)
                    )
            tag_masks.append(per_tag)

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
        sensation.append(
            sensation_features(hierarchy["child_plain"], hierarchy["parents_plain"])
        )
        positions.append(relative_position(len(plan.fine_spans)))
        absolute.append(hierarchy["child_plain"])
        groups.append(np.full(len(plan.fine_spans), len(per_document) - 1))
        print(f"  {per_document[-1]['doc_id']}: {len(plan.fine_spans)} chunks, "
              f"{int(labels.sum())} positive", flush=True)

    if not per_document:
        raise SystemExit("no document carried an annotated resultado span")

    labels = np.concatenate(pooled_labels)
    overall = {}
    for name, values in pooled.items():
        # Ranking metrics pool: they are order statistics over all chunks.
        scored = score_signal(name, np.concatenate(values), labels, fine_size=args.fine_size)
        # Edge errors do NOT pool. Concatenating documents makes the "longest run
        # above threshold" cross document boundaries, producing distances larger
        # than any document is long. They are per-document quantities, summarised
        # across documents.
        per_doc = [
            document["scores"][name] for document in per_document
        ]
        for edge in ("start_error_tokens", "end_error_tokens"):
            finite = [d[edge] for d in per_doc if np.isfinite(d[edge])]
            scored[edge] = float(np.median(finite)) if finite else float("nan")
            scored[f"{edge}_mean"] = float(np.mean(finite)) if finite else float("nan")
        scored["best_f1_per_document_median"] = float(
            np.median([d["best_f1"] for d in per_doc])
        )
        overall[name] = scored
    # Sensation gate: can a probe on the TAG-FREE relational features find the span
    # on a document it has not seen? This is the precondition for inference, where
    # no tag-conditioned channel exists at all.
    group_index = np.concatenate(groups)
    position_block = np.concatenate(positions)[:, None]
    sensation_block = np.vstack(sensation)
    absolute_block = np.vstack(absolute)
    ablations = {
        "position_only": position_block,
        "absolute_embedding": absolute_block,
        "sensation_relations": sensation_block,
        "sensation_plus_position": np.hstack([sensation_block, position_block]),
        "absolute_plus_position": np.hstack([absolute_block, position_block]),
    }
    # Sweep the ridge penalty per ablation and keep the best. The blocks differ by
    # an order of magnitude in width -- relations carry 2*(1+dim) per scale plus
    # deltas, absolute embeddings just dim -- and one fixed penalty would compare
    # regularisation strength as much as representation.
    penalties = (0.01, 0.1, 1.0, 10.0, 100.0)
    sensation_scores = {}
    for name, block in ablations.items():
        scored = [
            (leave_one_document_out_auprc(block, labels, group_index, penalty=penalty), penalty)
            for penalty in penalties
        ]
        best, penalty = max(scored, key=lambda item: item[0] if np.isfinite(item[0]) else -1.0)
        sensation_scores[name] = {
            "auprc": float(best),
            "penalty": penalty,
            "dimensions": int(block.shape[1]),
            "by_penalty": {str(p): float(v) for v, p in scored},
        }

    report = {
        "sensation_gate": {
            "ablations": sensation_scores,
            "random_auprc": float(labels.mean()),
            "protocol": "ridge probe, leave-one-document-out, AUPRC on held-out documents",
            "note": (
                "The inference channel carries no tag. position_only is the control that "
                "matters: a dispositivo sits at the end of a decision, so any relational "
                "feature must beat position to have contributed anything."
            ),
        },
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

    # Cache the feature blocks. Encoding is the only expensive step here; the
    # probes are seconds of numpy. Re-encoding the corpus to re-run a ridge sweep
    # is what exhausted memory on this machine three times over, and it makes the
    # probe design impossible to iterate on where the GPU is not.
    np.savez_compressed(
        args.output.with_suffix(".features.npz"),
        labels=labels,
        groups=group_index,
        position=position_block,
        sensation=sensation_block,
        absolute=absolute_block,
        signal_names=np.asarray(list(pooled.keys())),
        signal_values=np.vstack([np.concatenate(values) for values in pooled.values()]),
        **(
            {
                "tag_names": np.asarray(args.tags),
                "tag_masks": np.vstack(tag_masks),
                # One embedding per tag, from the category name read as a phrase.
                # Constant in time by construction, so it can colour food but
                # never say where the food is.
                "tag_embeddings": encoder.encode(
                    [category.replace("_", " ") for category in args.tags]
                ),
            }
            if args.tags
            else {}
        ),
    )

    baseline = report["positive_rate"]
    print(f"\n{len(per_document)} documents, {labels.size} chunks, "
          f"{baseline:.3f} positive (random AUPRC)")
    print(f"{'signal':<28}{'AUPRC':>8}{'lift':>7}{'r_pb':>8}{'F1':>7}{'F1/doc':>8}"
          f"{'startErr':>10}{'endErr':>9}   (edge errors: median over documents)")
    for name, row in sorted(overall.items(), key=lambda kv: -(kv[1]["auprc"] or 0)):
        print(
            f"{name:<28}{row['auprc']:>8.3f}{row['auprc']/baseline:>7.1f}"
            f"{row['point_biserial']:>8.3f}{row['best_f1']:>7.3f}"
            f"{row['best_f1_per_document_median']:>8.3f}"
            f"{row['start_error_tokens']:>10.0f}{row['end_error_tokens']:>9.0f}"
        )
    print("\n--- sensation gate (tag-free, ridge probe, leave-one-document-out) ---")
    print(f"{'features':<26}{'dims':>6}{'AUPRC':>8}{'lift':>7}{'penalty':>9}")
    for name, row in sorted(sensation_scores.items(), key=lambda kv: -kv[1]["auprc"]):
        print(
            f"{name:<26}{row['dimensions']:>6}{row['auprc']:>8.3f}"
            f"{row['auprc'] / baseline:>7.1f}{row['penalty']:>9g}"
        )

    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
