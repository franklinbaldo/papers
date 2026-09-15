"""Few-NERD NER smoke scaffold for MaleCNS positional tagging.

Smoke only: validates dataset/token/span alignment and the positional benchmark
contract before any full evidence run.  Do not report smoke scores as benchmark
results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", default="train")
    parser.add_argument("--limit", type=int, default=64)
    args = parser.parse_args()

    from datasets import load_dataset

    # Public Few-NERD supervised dataset.  Keep the exact token and NER tag
    # columns and derive spans without converting the task to sentence labels.
    ds = load_dataset("DFKI-SLT/few-nerd", "supervised", split=args.split)
    if args.limit:
        ds = ds.select(range(min(args.limit, len(ds))))

    rows = []
    entity_tokens = 0
    total_tokens = 0
    for sample in ds:
        tokens = list(sample["tokens"])
        tags = list(sample["ner_tags"])
        if len(tokens) != len(tags):
            raise RuntimeError("Few-NERD token/tag length mismatch")
        total_tokens += len(tokens)
        entity_tokens += sum(int(tag) != 0 for tag in tags)
        rows.append({
            "token_count": len(tokens),
            "entity_token_count": sum(int(tag) != 0 for tag in tags),
        })

    payload = {
        "schema": "papers/malecns-fewnerd-ner-smoke-v1",
        "claim_status": "pipeline smoke only; not benchmark evidence",
        "dataset": "DFKI-SLT/few-nerd",
        "config": "supervised",
        "split": args.split,
        "samples": len(rows),
        "tokens": total_tokens,
        "entity_tokens": entity_tokens,
        "task": "token/span-level NER",
        "guardrail": "must preserve positional entity predictions; no sentence/document collapse",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"event": "fewnerd_ner_smoke_ready", **payload}), flush=True)


if __name__ == "__main__":
    main()
