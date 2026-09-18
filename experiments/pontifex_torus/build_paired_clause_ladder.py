# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Build paired Pontifex fields for a clause-complexity ladder.

Each text family is sampled once as four independent clauses. The c=1..4 corpora
are nested prefixes of that same family, so text identity and added content are
paired across the ladder. A repeat4 control repeats clause 1 four times while using
the same connector sequence, giving a long, low-compositional-diversity input to
contrast with the equally segmented independent c=4 input.

Every regime is probed at the same number of deterministic relative positions.
This is synthetic pairwise cartography only; these stores are not and must never be
reused as D_assembly, D_student, D_val, or D_test.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from build_field_store import (
    ENCODER_A,
    ENCODER_B,
    OBJECTS,
    SUBJECTS,
    TAILS,
    VERBS,
    cos_distance,
    mask_tokens,
)
from build_long_field_store import CONNECTORS


def _clause(rng: np.random.Generator) -> str:
    return f"{rng.choice(SUBJECTS)} {rng.choice(VERBS)} {rng.choice(OBJECTS)} {rng.choice(TAILS)}."


def _join(clauses: list[str], connectors: list[str]) -> str:
    parts = [clauses[0]]
    for i, clause in enumerate(clauses[1:], start=1):
        parts.append(f"{connectors[i - 1]}, {clause[0].lower()}{clause[1:]}")
    return " ".join(parts)


def make_paired_corpora(n: int, seed: int) -> dict[str, list[str]]:
    rng = np.random.default_rng(seed)
    corpora = {f"c{i}": [] for i in range(1, 5)}
    corpora["repeat4"] = []
    seen = {name: set() for name in corpora}

    while len(corpora["c1"]) < n:
        clauses = [_clause(rng) for _ in range(4)]
        connectors = [str(rng.choice(CONNECTORS)) for _ in range(3)]
        candidates = {
            f"c{i}": _join(clauses[:i], connectors[: i - 1])
            for i in range(1, 5)
        }
        candidates["repeat4"] = _join([clauses[0]] * 4, connectors)

        # Require uniqueness in every regime so family index remains a strict pair.
        if any(text in seen[name] for name, text in candidates.items()):
            continue
        for name, text in candidates.items():
            seen[name].add(text)
            corpora[name].append(text)

    return corpora


def relative_probe_starts(token_count: int, positions: int) -> np.ndarray:
    max_start = max(1, token_count - 1)
    if positions > max_start:
        raise ValueError(
            f"fixed probe budget {positions} exceeds available starts {max_start}; "
            "lower --positions so all regimes have exactly the same budget"
        )
    # Matched quantile grid: same relative acquisition coordinates in every regime.
    starts = np.rint(np.linspace(0, max_start - 1, positions)).astype(int)
    if len(np.unique(starts)) != positions:
        raise ValueError("relative probe grid collapsed to duplicate token starts")
    return starts


def build_regime(
    *,
    corpus: list[str],
    positions: int,
    model_a: SentenceTransformer,
    model_b: SentenceTransformer,
) -> dict[str, np.ndarray]:
    originals_a = model_a.encode(corpus, batch_size=64, convert_to_numpy=True)
    originals_b = model_b.encode(corpus, batch_size=64, convert_to_numpy=True)

    masked: list[str] = []
    meta: list[tuple[int, float, int]] = []
    token_counts: list[int] = []
    for text_id, text in enumerate(corpus):
        toks = text.split()
        token_counts.append(len(toks))
        starts = relative_probe_starts(len(toks), positions)
        denom = max(1, len(toks) - 1)
        for start in starts:
            masked.append(mask_tokens(toks, int(start), 1))
            meta.append((text_id, float(start) / denom, 1))

    masked_a = model_a.encode(masked, batch_size=128, convert_to_numpy=True)
    masked_b = model_b.encode(masked, batch_size=128, convert_to_numpy=True)
    orig_a = np.stack([originals_a[t] for t, _, _ in meta])
    orig_b = np.stack([originals_b[t] for t, _, _ in meta])

    return {
        "text_id": np.asarray([m[0] for m in meta], dtype=np.int32),
        "original_a": originals_a.astype(np.float32),
        "original_b": originals_b.astype(np.float32),
        "pos": np.asarray([m[1] for m in meta], dtype=np.float64),
        "size": np.ones(len(meta), dtype=np.int16),
        "response_a": cos_distance(orig_a, masked_a).astype(np.float64),
        "response_b": cos_distance(orig_b, masked_b).astype(np.float64),
        "token_count": np.asarray(token_counts, dtype=np.int16),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=800)
    ap.add_argument("--positions", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    corpora = make_paired_corpora(args.texts, args.seed)
    model_a = SentenceTransformer(ENCODER_A)
    model_b = SentenceTransformer(ENCODER_B)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "texts_per_regime": args.texts,
        "positions_per_text": args.positions,
        "seed": args.seed,
        "encoders": {"A": ENCODER_A, "B": ENCODER_B},
        "pairing": "c1..c4 are nested prefixes of the same four-clause family; repeat4 repeats c1 content",
        "probe_grid": "same deterministic relative-position quantile grid in every regime",
        "evidence_boundary": "synthetic cartography only; no assembly/student/val/test benchmark data",
        "regimes": {},
    }

    for name in ("c1", "c2", "c3", "c4", "repeat4"):
        arrays = build_regime(
            corpus=corpora[name], positions=args.positions, model_a=model_a, model_b=model_b
        )
        counts = arrays["token_count"].astype(float)
        metadata = {
            "regime": name,
            "texts": args.texts,
            "positions_per_text": args.positions,
            "seed": args.seed,
            "rows": int(len(arrays["text_id"])),
            "token_count_mean": float(np.mean(counts)),
            "token_count_std": float(np.std(counts)),
            "token_count_min": int(np.min(counts)),
            "token_count_max": int(np.max(counts)),
            "paired_family_indices": True,
            "sizes": [1],
        }
        path = args.output_dir / f"field-{name}-n{args.texts}-p{args.positions}-seed{args.seed}.npz"
        np.savez_compressed(path, **arrays, metadata=np.asarray(json.dumps(metadata)))
        manifest["regimes"][name] = {"path": str(path), **metadata}

    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
