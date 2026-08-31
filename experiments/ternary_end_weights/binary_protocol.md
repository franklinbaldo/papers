---
type: "Protocol"
title: "Protocol — Binary Variable-Precision Alternatives for Quantized LLM Weights"
description: "Follow-up protocol testing whether the structure exposed by the negative ternary END experiment is better captured by conventional binary encodings."
tags: [llm, quantization, compression, variable-precision, sparse, bitplanes, protocol]
timestamp: 2026-08-31T08:35:00-04:00
---

# Protocol — binary variable-precision alternatives for quantized LLM weights

## 1. Status and question

This is a **post-result follow-up** to `protocol.md`, frozen only after the original `{0,1,END}` experiment had already rejected its dense-LLM compression hypothesis. It must not be presented as part of the original preregistration.

The follow-up asks a narrower question suggested by that negative result:

> If the useful mechanism is variable precision, sparsity, or collective significance rather than a third physical state, how much of it can conventional binary encodings recover on the exact same quantized SmolLM2 weights?

The experiment keeps the original model, checkpoint, tensor inclusion rule, group size, and groupwise quantizer so the only changed variable is the representation after quantization.

## 2. Registered corpus and quantization

Model: `HuggingFaceTB/SmolLM2-135M`.

Revision: `d6a5589c239236d22370e2126bbe23d4843c47d9`.

Registered `model.safetensors` SHA-256: `80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1`.

NumPy: `2.5.2`.

Include numeric F16/BF16/F32/F64 tensors with `ndim >= 2`; flatten each tensor independently; form consecutive groups of 128; quantize each group symmetrically by its maximum absolute value using round-to-nearest. Tensor boundaries never share a group.

Registered widths are **4 and 8 bits**. INT16 is omitted because the original result showed essentially no post-quantization zeros there and 4/8 are the operationally relevant comparison.

Scale metadata is excluded from every payload cost because all registered representations use the identical groupwise quantization scales.

## 3. Baseline

`fixed`: ordinary fixed-width sign-magnitude payload, exactly `B` bits per weight. This is the same baseline used by the ternary experiment.

No alternative may claim a storage win unless its complete registered payload cost is below this baseline.

## 4. Binary alternatives

### A. Adaptive bitmap + sparse payload

For each quantization group of `N <= 128` weights, emit one mode bit and choose the smaller of:

- fixed mode: `N × B` payload bits;
- sparse mode: an `N`-bit zero bitmap plus `B` bits for each non-zero value.

Registered cost:

`1 + min(NB, N + nonzero_count × B)` bits per block.

This is deliberately simple and random-access-friendly at block granularity.

### B. Per-weight bit length + payload

For every quantized value, define magnitude bit length `L = bit_length(abs(q))`, with `L = 0` for zero. A non-zero payload uses one sign bit plus exactly `L` magnitude bits.

Report two length-stream variants:

1. `length_fixed`: every `L` uses `ceil(log2(B))` bits;
2. `length_huffman`: all `L` values across the model share one canonical Huffman code. Charge a small explicit codebook cost of `B × ceil(log2(B+1))` bits.

This tests the user's core variable-precision intuition without any ternary symbol.

### C. Bitplane significance + exact enumerative subsets

Transpose each sign-magnitude block into `B` binary bitplanes: one sign plane and `B-1` magnitude planes.

Each plane independently uses two mode bits selecting one of four exact representations:

- all zero;
- all one;
- raw `N`-bit bitmap;
- enumerative subset coding.

For a plane containing `k` ones among `N` positions, enumerative mode stores `k` in `ceil(log2(N+1))` bits and then the rank of that exact `k`-subset in `ceil(log2(C(N,k)))` bits. The registered plane cost is therefore:

- `2` bits for all-zero or all-one planes;
- otherwise `2 + min(N, ceil(log2(N+1)) + ceil(log2(C(N,k))))`.

This is an exact combinatorial code, not an entropy estimate. It tests whether collective significance across 128 weights captures more structure than per-weight termination.

### D. Full-value Huffman reference

Build one Huffman code over the complete quantized signed-value distribution for each width. Charge the exact weighted Huffman payload plus `2B` metadata bits for every observed quantized symbol as a compact canonical codebook allowance.

This comparator is **not** treated as an inference-layout recommendation: a global variable-length stream sacrifices ordinary constant-time random access. Its role is to measure how much conventional entropy coding can exploit the same distribution.

### E. Shannon entropy diagnostic

Report empirical Shannon entropy of the quantized signed-value distribution. This is a diagnostic lower bound, not an implemented format and not eligible to win an implementation gate.

## 5. Metrics

For every width report bits per weight and ratio to fixed width for:

- `fixed`;
- `adaptive_bitmap_sparse`;
- `length_fixed`;
- `length_huffman`;
- `bitplane_enumerative`;
- `value_huffman`;
- empirical value entropy.

Also report quantized zero rate and number of distinct observed quantized values.

## 6. Gates

### B0 — corpus identity

**Pass:** checkpoint hash, tensor count/rule, group size, and total weight count match the original registered SmolLM2 execution.

A mismatch invalidates the comparison.

### B1 — simple random-access binary win

**Pass:** either `adaptive_bitmap_sparse_ratio < 1` or `bitplane_enumerative_ratio < 1` at INT4 or INT8.

This asks whether a block-local binary representation can capture the opportunity without a global entropy stream.

### B2 — direct variable-precision win

**Pass:** `length_huffman_ratio < 1` at INT4 or INT8.

Failure means merely making precision self-describing per weight is not enough, even when the length metadata is compressed collectively.

### B3 — binary entropy win

**Pass:** `value_huffman_ratio < 1` at INT4 or INT8.

This does not imply a good inference layout. It establishes only that the quantized symbol distribution itself is compressible by an ordinary binary prefix code.

### B4 — ternary-mechanism recovery

At INT4, compare the best block-local binary ratio with the original ternary raw-cell ratio `0.9584` and ternary capacity ratio `1.5190`.

- If a block-local binary scheme is `< 0.9584`, it recovers more than the ternary raw symbol-count effect while staying binary.
- If it is between `0.9584` and `1`, it still beats fixed width but does not recover the full raw-cell reduction.
- If all block-local schemes are `>= 1`, the original small raw-cell effect is not captured by these simple binary layouts.

This gate is descriptive; it must not compare binary bits directly to physical ternary-cell area.

## 7. Interpretation boundaries

A win for bitmap or bitplanes supports a **block-structured sparsity/significance** explanation.

A win only for length coding supports **variable per-weight precision**, but not necessarily efficient random access.

A win only for full-value Huffman supports ordinary **distributional entropy coding**, not the original termination mechanism and not an inference-friendly layout.

No result may be used to claim faster inference, lower energy, smaller silicon area, or superiority over production sparse kernels, ANS/arithmetic coding, Zstd, GPTQ/AWQ packing, or hardware-native compressed formats without measuring those systems directly.

## 8. Reproduction

```bash
python -m pip install numpy==2.5.2
python -m unittest -v test_binary_alternatives.py
python binary_alternatives.py \
  --safetensors model.safetensors \
  --model-id HuggingFaceTB/SmolLM2-135M \
  --revision d6a5589c239236d22370e2126bbe23d4843c47d9 \
  --expected-sha256 80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1 \
  --bits 4,8 \
  --group-size 128 \
  --output binary_results.json
```
