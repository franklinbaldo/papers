# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "sentence-transformers>=3.0",
# ]
# ///
"""Pontifex cyclic seam-rotation equivariance test.

The dynamic double-occlusion experiment imposes modulo motion, but that alone does
not imply that text semantics are invariant to where a circular seam is placed.
This experiment moves the seam *in the raw sequence* by cyclically rotating each
text, then checks whether singleton response fields and pair-interaction fields
rotate equivariantly.

For an original token index t and a left rotation by s tokens, the same physical
token appears at k=(t-s) mod N. A genuinely seam-equivariant response field should
therefore satisfy, approximately,

    R_original(t) ~= R_rotated((t-s) mod N)

and likewise for the simultaneous-pair residual

    I_E(t,t+delta) = R_E(t,t+delta) - R_E(t) - R_E(t+delta).

The aligned comparison is contrasted with an intentionally unaligned control. This
is a mechanistic falsification test on the synthetic cartography corpus; it does
not use any downstream benchmark test set.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from build_field_store import ENCODER_A, ENCODER_B, cos_distance, make_texts


def mask_single(tokens: list[str], i: int) -> str:
    out = list(tokens)
    out[i] = "[MASK]"
    return " ".join(out)


def mask_pair(tokens: list[str], i: int, j: int) -> str:
    if i == j:
        raise ValueError("double occlusion requires distinct centers")
    out = list(tokens)
    out[i] = "[MASK]"
    out[j] = "[MASK]"
    return " ".join(out)


def pearson(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def nrmse(reference, candidate) -> float:
    reference = np.asarray(reference, dtype=float)
    candidate = np.asarray(candidate, dtype=float)
    denom = max(float(np.std(reference)), 1e-12)
    return float(np.sqrt(np.mean((reference - candidate) ** 2)) / denom)


def summarize(values):
    x = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if len(x) == 0:
        return {"mean": float("nan"), "median": float("nan"), "std": float("nan")}
    return {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
    }


def encode_fields(model, tokens: list[str], delta: int):
    n = len(tokens)
    original = model.encode([" ".join(tokens)], convert_to_numpy=True)[0]
    single_texts = [mask_single(tokens, i) for i in range(n)]
    pair_texts = [mask_pair(tokens, i, (i + delta) % n) for i in range(n)]
    single_emb = model.encode(single_texts, batch_size=128, convert_to_numpy=True)
    pair_emb = model.encode(pair_texts, batch_size=128, convert_to_numpy=True)
    original_batch = np.repeat(original[None, :], n, axis=0)
    single = cos_distance(original_batch, single_emb).astype(float)
    pair = cos_distance(original_batch, pair_emb).astype(float)
    interaction = pair - single - np.roll(single, -delta)
    return single, interaction, original


def unique_shifts(n: int, fractions: list[float]) -> list[int]:
    shifts = []
    for frac in fractions:
        s = int(round(frac * n)) % n
        if s == 0:
            s = 1
        if s not in shifts:
            shifts.append(s)
    return shifts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-store", type=Path, required=True)
    ap.add_argument("--texts", type=int, default=120)
    ap.add_argument("--shift-fractions", type=float, nargs="+", default=[0.25, 0.5])
    ap.add_argument("--output", type=Path, default=Path("pontifex-seam-rotation.json"))
    args = ap.parse_args()

    # The field store fixes the exact synthetic corpus seed/size used by the other
    # Torus experiments. We read only text ids here; all rotation responses are
    # freshly encoded so the seam test does not recycle target values.
    store = np.load(args.field_store, allow_pickle=False)
    text_ids = np.unique(store["text_id"].astype(int))[: args.texts]
    corpus = make_texts(len(np.unique(store["text_id"].astype(int))), 17)

    models = {
        "A": SentenceTransformer(ENCODER_A),
        "B": SentenceTransformer(ENCODER_B),
    }
    records = []

    for text_id in text_ids:
        tokens = corpus[int(text_id)].split()
        n = len(tokens)
        if n < 4:
            continue
        delta = max(1, n // 3)
        if delta >= n:
            delta = n - 1
        shifts = unique_shifts(n, args.shift_fractions)

        baseline = {}
        for label, model in models.items():
            baseline[label] = encode_fields(model, tokens, delta)

        for shift in shifts:
            rotated_tokens = tokens[shift:] + tokens[:shift]
            for label, model in models.items():
                base_single, base_interaction, base_original = baseline[label]
                rot_single, rot_interaction, rot_original = encode_fields(
                    model, rotated_tokens, delta
                )

                # left-rotating the sequence by `shift` moves original physical
                # position t to rotated coordinate (t-shift) mod N. np.roll by
                # +shift performs exactly that lookup for each original t.
                aligned_single = np.roll(rot_single, shift)
                aligned_interaction = np.roll(rot_interaction, shift)

                records.append(
                    {
                        "text_id": int(text_id),
                        "encoder": label,
                        "n": int(n),
                        "delta": int(delta),
                        "shift": int(shift),
                        "shift_phase": float(shift / n),
                        "full_text_cosine": float(
                            1.0 - cos_distance(
                                base_original[None, :], rot_original[None, :]
                            )[0]
                        ),
                        "single_aligned_pearson": pearson(
                            base_single, aligned_single
                        ),
                        "single_unaligned_pearson": pearson(
                            base_single, rot_single
                        ),
                        "single_aligned_nrmse": nrmse(
                            base_single, aligned_single
                        ),
                        "interaction_aligned_pearson": pearson(
                            base_interaction, aligned_interaction
                        ),
                        "interaction_unaligned_pearson": pearson(
                            base_interaction, rot_interaction
                        ),
                        "interaction_aligned_nrmse": nrmse(
                            base_interaction, aligned_interaction
                        ),
                    }
                )

    summary = {}
    for label in ("A", "B"):
        rows = [r for r in records if r["encoder"] == label]
        metrics = [
            "full_text_cosine",
            "single_aligned_pearson",
            "single_unaligned_pearson",
            "single_aligned_nrmse",
            "interaction_aligned_pearson",
            "interaction_unaligned_pearson",
            "interaction_aligned_nrmse",
        ]
        summary[label] = {m: summarize([r[m] for r in rows]) for m in metrics}
        summary[label]["single_alignment_gain"] = float(
            summary[label]["single_aligned_pearson"]["mean"]
            - summary[label]["single_unaligned_pearson"]["mean"]
        )
        summary[label]["interaction_alignment_gain"] = float(
            summary[label]["interaction_aligned_pearson"]["mean"]
            - summary[label]["interaction_unaligned_pearson"]["mean"]
        )

    result = {
        "experiment": "Pontifex cyclic seam-rotation equivariance",
        "texts": int(len(text_ids)),
        "shift_fractions": args.shift_fractions,
        "records": records,
        "summary": summary,
        "interpretation_contract": {
            "equivariance": "after cyclically rotating raw text, phase-aligned response fields should remain strongly correlated if moving the seam preserves the semantic field",
            "alignment_control": "aligned Pearson should exceed the intentionally unaligned control if the field rotates with the seam rather than merely changing arbitrarily",
            "full_text_cosine": "reports how much the encoder itself changes under cyclic sequence rotation; low invariance here is evidence against treating raw text semantics as intrinsically circular",
            "scope": "this tests semantic seam-rotation equivariance, not the modulo rule for moving interventions; modulo motion remains a definition even if this test fails",
            "data_boundary": "mechanistic synthetic cartography corpus only; no assembly/student/validation/downstream-test partition is consumed",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
