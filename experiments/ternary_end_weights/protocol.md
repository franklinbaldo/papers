---
type: "Protocol"
title: "Protocol — 0/1/END Ternary Delimiting for Quantized Weights"
description: "Pre-registered protocol for testing whether an in-band third ternary state can make fixed-width quantized LLM weights cheaper to represent without changing the quantized values."
tags: [ternary-computation, llm, quantization, compression, protocol]
timestamp: 2026-08-31T08:00:00-04:00
---

# Protocol — 0/1/END ternary delimiting for quantized weights

## 1. Question

For a weight tensor already quantized to a fixed-width signed integer representation, does replacing the fixed boundary with a ternary alphabet `{0, 1, END}` reduce representation cost enough to remain advantageous after fair accounting for ternary information capacity and conventional binary alternatives?

The protocol intentionally does **not** ask whether ternary hardware is practical, whether a three-level transistor has the same area/energy/error cost as a binary transistor, or whether a model should be trained with ternary weights. Those are different questions.

## 2. Encoding under test

For a `B`-bit sign-magnitude quantized integer:

1. one binary digit denotes sign;
2. `B - 1` binary digits denote magnitude;
3. zero is encoded as `[END]`;
4. for a non-zero value, remove trailing zeroes from the fixed-width magnitude and emit `sign`, the remaining magnitude prefix, then `END`;
5. decoding pads the missing magnitude suffix with zeroes.

Because only trailing zeroes are removed, decoding must recover the **identical quantized integer**. Any mismatch is a correctness failure, not a rate/distortion tradeoff.

## 3. Quantization before encoding

The encoding is evaluated after symmetric group quantization. For total width `B`, the magnitude range is `0 .. 2^(B-1)-1`. Each group uses its maximum absolute value as scale and round-to-nearest quantization. Registered widths are 4, 8, and 16 bits.

The model-backed run uses group size 128. Per-group scale metadata is omitted from all reported payload costs because both the fixed-width reference and the proposed encoding need the same scales.

The fixed-width reference is deliberately sign-magnitude rather than two's complement so that the transformation being measured is exact and the sign semantics are shared. This costs one duplicate-zero code relative to the most efficient fixed signed integer codebook; therefore any marginal win should be treated conservatively rather than generalized to all INT4/INT8 formats.

## 4. Cost measures

For each distribution/model and bit width report:

- `fixed_bits`: `B` bits per weight;
- `avg_trits`: average number of `{0,1,END}` symbols per weight;
- `capacity_equivalent_bits`: `avg_trits × log2(3)`;
- `packed_2bit_bits`: `avg_trits × 2`, representing naive storage of a trit on a binary machine;
- `binary_length_prefix_bits`: a simple binary competitor that stores a fixed-width field for the retained magnitude-prefix length, followed by sign and retained prefix for non-zero values;
- zero rate after quantization;
- ratios of each cost to `B`.

`capacity_equivalent_bits` is a normalization by alphabet capacity, not a claim about transistor area or energy. `packed_2bit_bits` is a software-storage baseline, not an optimized ternary packer. The binary length-prefix comparator is intentionally simple and must not be described as an optimal entropy code.

## 5. Synthetic controls

Use Python's deterministic `random.Random` generator with seed `20260831`, 50,000 values per distribution, and the following controls:

- uniform `[-1,1]` — negative control with little central concentration;
- Gaussian `N(0, 0.18)` clipped to `[-1,1]`;
- Laplace scale `0.12` clipped to `[-1,1]`;
- centered mixture — 90% `N(0,0.08)`, 10% `N(0,0.35)`, clipped;
- sparse uniform — 50% exact zero, otherwise uniform `[-1,1]`.

The synthetic layer exists to test the mechanism and identify the sparsity regime. It is not evidence about LLM weights.

## 6. Registered real-model replication

Model: `HuggingFaceTB/SmolLM2-135M`.

Revision: `d6a5589c239236d22370e2126bbe23d4843c47d9`.

Registered `model.safetensors` SHA-256: `80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1`.

NumPy: `2.5.2`.

Include numeric F16/BF16/F32/F64 tensors with `ndim >= 2`; exclude one-dimensional normalization/bias-like tensors. Flatten each included tensor independently and form consecutive groups of 128. Tensor boundaries must not share a quantization group.

The model file hash must match before results are accepted.

## 7. Gates

### G0 — exactness

**Pass:** exhaustive round-trip over the complete 4-bit sign-magnitude integer range succeeds, and stream concatenation including zero weights reproduces the original integer sequence.

Failure kills the encoding implementation.

### G1 — negative-control sanity

**Pass:** the uniform synthetic control must not be reported as an information-capacity win merely because trits were counted like bits. At 8 bits, `capacity_ratio` must be greater than 1.

This gate catches the easiest accounting error.

### G2 — real-model capacity win

**Pass:** the aggregate SmolLM2 model-backed run has `capacity_ratio < 1` at at least one of 4 or 8 bits.

If it fails at both widths, the experiment does not support the hypothesis that this encoding is storage-efficient for ordinary quantized LLM weights under alphabet-capacity normalization.

### G3 — binary-software win

**Pass:** `packed_2bit_ratio < 1` at at least one of 4 or 8 bits on the real model.

Failure means the scheme offers no raw-storage advantage when implemented naively on conventional binary memory, even if a hypothetical ternary cell-count result is interesting.

### G4 — simple binary variable-length competitor

**Pass:** at a width where the proposed scheme beats fixed width by `capacity_equivalent_bits`, it must also use fewer capacity-equivalent bits than the registered `binary_length_prefix_bits` comparator.

Failure means the observed gain is attributable to variable-length/trailing-zero suppression in general, not evidence that a third physical state is the better way to obtain it.

### G5 — native ternary boundary

This is a claim-boundary gate rather than a numeric win condition. Results must state that a native `{-1,0,+1}` weight alphabet can be represented directly by one trit and is not the target beaten by this experiment. Any conclusion that presents `0/1/END` as superior to direct ternary-weight representation fails this gate.

## 8. Interpretation and kill conditions

The proposal remains interesting as an LLM-weight storage hypothesis only if G0 and G1 pass and the real-model layer provides a non-trivial win under G2 or G3. A cell-count reduction alone is insufficient.

If G2 fails at both 4 and 8 bits **and** the simple binary comparator is no worse wherever variable-length coding helps, the storage-compression version of the hypothesis should be treated as negative absent new hardware evidence. It may still be useful as a self-delimiting protocol primitive, but that is a different claim.

Even if G2 passes, no hardware-efficiency claim follows without measured area, energy, latency, noise margin, and read/write cost for an actual ternary device. Conversely, a hardware implementation could change the relevant cost model; this experiment is designed to expose exactly which assumption would need to change.

## 9. Reproduction

Synthetic:

```bash
python -m unittest -v test_experiment.py
python experiment.py --output synthetic_results.json
```

Pinned model:

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
