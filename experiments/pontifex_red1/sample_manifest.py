# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a deterministic, encoder-independent sample of MS MARCO v1 passage IDs.

The manifest is intentionally defined without RNG state so every encoder extracts
exactly the same PIDs. We use a full-cycle modular walk because STEP is coprime
with the corpus size; therefore no PID repeats before exhausting the corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CORPUS_SIZE = 8_841_823
START = 4_271_903
STEP = 1_888_861  # gcd(STEP, CORPUS_SIZE) == 1
SPEC_VERSION = "msmarco-v1-passage-sample-v1"


def sample_pids(n: int) -> list[int]:
    if not 1 <= n <= CORPUS_SIZE:
        raise ValueError(f"n must be in [1, {CORPUS_SIZE}]")
    pids = [(START + i * STEP) % CORPUS_SIZE for i in range(n)]
    if len(set(pids)) != n:
        raise AssertionError("sampling walk repeated a PID")
    return pids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=10_000)
    ap.add_argument("--output", type=Path, default=Path("msmarco-sample-10k.json"))
    args = ap.parse_args()

    pids = sample_pids(args.size)
    encoded = "\n".join(map(str, pids)).encode()
    result = {
        "type": "msmarco_pid_sample_manifest",
        "spec_version": SPEC_VERSION,
        "corpus": "MS MARCO Passage v1",
        "corpus_size": CORPUS_SIZE,
        "sample_size": len(pids),
        "sampling": {
            "method": "full-cycle modular walk",
            "start": START,
            "step": STEP,
            "formula": "pid_i = (start + i * step) mod corpus_size",
        },
        "pid_sequence_sha256": hashlib.sha256(encoded).hexdigest(),
        "pids": [str(x) for x in pids],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"sample={len(pids)} first={pids[:5]} last={pids[-5:]} "
        f"sha256={result['pid_sequence_sha256']}"
    )


if __name__ == "__main__":
    main()
