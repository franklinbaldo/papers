"""Few-NERD byte-level NER smoke for MaleCNS positional tagging.

Smoke only.  Uses Few-NERD's 66 fine-grained entity types and IO tagging.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fewnerd_ner_core import (
    byte_labels_to_token_labels,
    canonical_byte_axis,
    exact_entity_prf,
    io_entities,
)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--split", default="train")
    p.add_argument("--limit", type=int, default=64)
    a = p.parse_args()

    from datasets import load_dataset

    ds = load_dataset("DFKI-SLT/few-nerd", "supervised", split=a.split)
    if a.limit:
        ds = ds.select(range(min(a.limit, len(ds))))

    feature = ds.features["fine_ner_tags"].feature
    label_names = list(feature.names)
    if label_names[0] != "O" or len(label_names) != 67:
        raise RuntimeError(
            f"unexpected Few-NERD fine ontology: first={label_names[:1]!r} count={len(label_names)}"
        )

    total_tokens = entity_tokens = total_bytes = entity_bytes = unicode_tokens = 0
    total_entities = 0
    gold_sequences: list[list[int]] = []
    roundtrip_sequences: list[tuple[int, ...]] = []

    for sample in ds:
        tokens = [str(x) for x in sample["tokens"]]
        labels = [int(x) for x in sample["fine_ner_tags"]]
        axis = canonical_byte_axis(tokens, labels)
        roundtrip = byte_labels_to_token_labels(axis.byte_labels, axis.token_byte_spans)
        if tuple(labels) != roundtrip:
            raise RuntimeError("gold token -> byte -> token label roundtrip mismatch")

        total_tokens += len(tokens)
        entity_tokens += sum(label != 0 for label in labels)
        total_bytes += len(axis.byte_labels)
        entity_bytes += sum(label != 0 for label in axis.byte_labels)
        unicode_tokens += sum(len(token.encode("utf-8")) != len(token) for token in tokens)
        total_entities += len(io_entities(labels))
        gold_sequences.append(labels)
        roundtrip_sequences.append(roundtrip)

    identity_score = exact_entity_prf(gold_sequences, roundtrip_sequences)
    if identity_score["f1"] != 1.0:
        raise RuntimeError(f"entity scorer/byte roundtrip identity failed: {identity_score}")

    out = {
        "schema": "papers/malecns-fewnerd-ner-byte-smoke-v2",
        "claim_status": "pipeline smoke only; not benchmark evidence",
        "dataset": "DFKI-SLT/few-nerd",
        "config": "supervised",
        "split": a.split,
        "tagging_scheme": "IO",
        "label_column": "fine_ner_tags",
        "entity_types": len(label_names) - 1,
        "samples": len(ds),
        "tokens": total_tokens,
        "entity_tokens": entity_tokens,
        "entities": total_entities,
        "bytes": total_bytes,
        "entity_bytes": entity_bytes,
        "unicode_tokens": unicode_tokens,
        "task": "byte-level internal NER with exact entity-span/type evaluation",
        "canonical_reconstruction": "official tokens joined by one ASCII space; separator bytes are outside label",
        "roundtrip": "all token UTF-8 slices and labels round-tripped exactly",
        "identity_entity_score": identity_score,
        "guardrail": "MaleCNS predictions live on bytes; token/span conversion only at benchmark boundary",
        "preregistration_amendment": "preregistered-fewnerd-ner-byte-amendment-2026-09-15.md",
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "fewnerd_byte_ner_smoke_ready", **out}), flush=True)


if __name__ == "__main__":
    main()
