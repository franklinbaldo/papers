---
type: "Companion Note"
title: "0/1/END Ternary Delimiting for Quantized LLM Weights"
description: "Experimental companion testing whether a third ternary state used as an in-band terminator can reduce the representation cost of fixed-width quantized weights."
tags: [ternary-computation, llm, quantization, compression, experiment]
timestamp: 2026-08-31T08:00:00-04:00
---

# 0/1/END ternary delimiting for quantized LLM weights

**Editorial note.** This directory is an experimental companion, not evidence of a novel ternary computer architecture and not a claim that ternary hardware is currently cheaper than binary hardware. It isolates one narrow encoding idea so that it can fail quantitatively.

The proposal uses a ternary alphabet with the semantic states `{0, 1, END}`. Two states carry ordinary binary digits; the third terminates the current quantized weight. For a fixed-width sign-magnitude integer, trailing zero magnitude bits can then be omitted: the decoder stops at `END` and restores the omitted suffix as zero.

For example, with a 4-bit reference (`sign + 3 magnitude bits`), the quantized value `+4` is `0 | 100`. The ternary stream is `0, 1, END`; the decoder pads the missing two magnitude positions with zero and recovers exactly `0 | 100`. Zero itself is just `END`.

This is therefore **lossless with respect to the already-quantized integer**. The experiment does not buy storage by silently reducing precision.

## Why this is interesting — and why symbol count is not enough

If a ternary cell had the same physical cost as a binary cell, fewer ternary cells could be attractive. But a trit has information capacity `log2(3) ≈ 1.585` bits, and an ordinary binary machine normally needs two bits to store one of three states. The benchmark consequently reports all of these views instead of treating one trit as one bit:

- average ternary cells per weight;
- capacity-normalized cost: `trits × log2(3)`;
- naive present-day binary packing: `trits × 2` bits;
- the original fixed-width quantized representation;
- a deliberately simple binary variable-length competitor that stores the retained prefix length in a fixed-width field.

A result is interesting only if it survives the relevant comparator.

## Important distinction from native ternary weights

This is **not** the same representation as a model whose weight alphabet is directly `{-1, 0, +1}`. A native ternary weight can be represented by one trit. Under the proposal here, zero takes one `END` trit while either non-zero ternary weight needs sign/data plus `END`; therefore the proposal should not be presented as an improvement over direct ternary-weight encoding.

The question here is narrower: can a ternary delimiter make a binary quantized payload self-delimiting enough to beat fixed-width storage for realistic weight distributions?

## Run the synthetic layer

The synthetic layer has no third-party dependencies:

```bash
cd experiments/ternary_end_weights
python -m unittest -v test_experiment.py
python experiment.py --output synthetic_results.json
```

It evaluates uniform, centered Gaussian, Laplace, centered-mixture, and 50%-sparse controls at 4, 8, and 16 fixed bits.

## Run a real safetensors checkpoint

The model-backed path needs NumPy because it processes the checkpoint in vectorized groups. The registered replication uses NumPy 2.5.2, group size 128, and `HuggingFaceTB/SmolLM2-135M` at revision `d6a5589c239236d22370e2126bbe23d4843c47d9`.

```bash
python -m pip install numpy==2.5.2
python experiment.py \
  --safetensors model.safetensors \
  --model-id HuggingFaceTB/SmolLM2-135M \
  --revision d6a5589c239236d22370e2126bbe23d4843c47d9 \
  --expected-sha256 80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1 \
  --group-size 128 \
  --output model_results.json
```

The reader handles F16, BF16, F32, and F64 safetensors directly and includes numeric tensors with at least two dimensions. Scale metadata is excluded from the storage comparison because the same per-group scale is required by both the fixed-width and `0/1/END` representations.

See `protocol.md` for the frozen gates and `FINDINGS.md` for executed results. The GitHub Actions workflow runs the synthetic checks and the pinned model-backed replication separately so that a failed or unavailable model download cannot be confused with a synthetic result.
