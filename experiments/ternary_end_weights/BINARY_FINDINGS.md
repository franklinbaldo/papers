---
type: "Findings Record"
title: "Findings — Binary Variable-Precision Alternatives for Quantized LLM Weights"
description: "Execution record for the post-ternary follow-up comparing sparse, per-weight variable-length, bitplane-enumerative, and Huffman binary encodings on the pinned SmolLM2 checkpoint."
tags: [llm, quantization, compression, variable-precision, bitplanes, findings]
timestamp: 2026-08-31T08:25:00-04:00
---

# Findings — binary variable-precision alternatives for quantized LLM weights

## Frozen protocol

This record executes `binary_protocol.md`, a follow-up protocol frozen only after the original ternary experiment had already produced its negative dense-model result. It is not part of the original ternary preregistration.

Model identity: `HuggingFaceTB/SmolLM2-135M`, revision `d6a5589c239236d22370e2126bbe23d4843c47d9`, checkpoint SHA-256 `80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1`, NumPy 2.5.2, group size 128.

The registered run executed in GitHub Actions run `33391383616` against repository commit `3d3f6af44543876613f5e1d7728d7984bf2b13d7`. It covered the same 211 matrix-like tensors and 134,479,872 weights as the original ternary model run, with no supported dtype skipped. The exact aggregate output is committed as `binary_results.json`.

## Result

All values below are exact registered payload accounting for the specified formats. Ratios are relative to ordinary fixed-width sign-magnitude storage.

| representation | INT4 bits/weight | INT4 ratio | INT8 bits/weight | INT8 ratio |
|---|---:|---:|---:|---:|
| fixed | 4.0000 | 1.0000 | 8.0000 | 1.0000 |
| adaptive bitmap + sparse payload | 3.9521 | **0.9880** | 8.0078 | 1.0010 |
| per-weight length, fixed length field | 4.1985 | 1.0496 | 8.9068 | 1.1133 |
| per-weight length, Huffman length stream | 4.1847 | 1.0462 | 8.4765 | 1.0596 |
| bitplane + enumerative subsets | **3.5585** | **0.8896** | **7.5775** | **0.9472** |
| full-value Huffman | **3.2679** | **0.8170** | **7.4180** | **0.9273** |
| empirical Shannon entropy | 3.2382 | 0.8096 | 7.3802 | 0.9225 |

The quantized exact-zero rate is 19.9545% at INT4 and only 1.1251% at INT8. All 15 possible sign-magnitude values appear at INT4 and all 255 possible values appear at INT8.

## Gates

- **B0 — corpus identity: PASS.** Model revision, checkpoint hash, tensor rule, tensor count (211), group size (128), and total weight count (134,479,872) match the original registered execution.
- **B1 — simple random-access binary win: PASS.** Bitplane-enumerative coding reaches 0.8896× fixed INT4 and 0.9472× fixed INT8. Adaptive bitmap+sparse also narrowly wins at INT4 (0.9880×) but not INT8.
- **B2 — direct variable-precision win: FAIL.** Compressing a per-weight bit-length stream still costs 1.0462× fixed INT4 and 1.0596× fixed INT8.
- **B3 — binary entropy win: PASS.** Full-value Huffman reaches 0.8170× INT4 and 0.9273× INT8.
- **B4 — ternary-mechanism recovery: PASS.** At INT4 the best block-local binary ratio, 0.8896, is below the original ternary raw-cell ratio 0.9584. Numerically, the binary block representation removes more payload bits than the ternary scheme removed raw symbols, while avoiding the third alphabet state. This is a coding comparison only, not a transistor-area comparison.

## Interpretation

The experiment separates three hypotheses that had been bundled together in the original intuition.

### 1. Per-weight self-delimiting precision is not the useful mechanism

The most literal binary translation of `{0,1,END}` loses. Even when the per-weight length metadata is Huffman-compressed across the entire model, INT4 requires 4.1847 bits per weight and INT8 requires 8.4765. The metadata plus sign/payload cost is larger than simply keeping the fixed-width word.

So the useful principle is **not** merely “each weight should know where it ends.”

### 2. Collective significance across a block is useful

The strongest inference-local result is the bitplane representation: 3.5585 bits per INT4 weight, an 11.04% reduction, and 7.5775 bits per INT8 weight, a 5.28% reduction.

This result is especially informative at INT8. Exact zeros are only 1.1251% there, so a 5.28% bitplane reduction cannot be explained primarily by zero-weight sparsity. The exploitable structure is broader: individual bitplanes have strongly non-uniform populations within 128-weight quantization blocks, and an exact subset code can describe those populations more cheaply than storing every plane as a raw 128-bit bitmap.

This is close to the conceptual refinement suggested by the original experiment: **use a collective boundary/significance description for a block, rather than an END marker for every individual weight.**

### 3. There is still more ordinary distributional entropy than the block-local format captures

Full-value Huffman reaches 3.2679 bits at INT4 and 7.4180 at INT8, close to the empirical Shannon entropies of 3.2382 and 7.3802 bits respectively. This shows that the quantized value distribution contains additional global compressibility.

But Huffman is not the operational winner for inference by default. A global variable-length value stream disrupts ordinary constant-time indexing and SIMD/GPU-friendly fixed-stride access. The bitplane result is therefore more interesting as a candidate *layout*: it remains block-local and has deterministic block boundaries, even though this experiment has not benchmarked decoding or kernels.

## What changed relative to the ternary result

The original `{0,1,END}` experiment found a 4.16% reduction in raw ternary symbol count at INT4 but a 51.9% increase after neutral `log2(3)` capacity accounting. The binary bitplane follow-up instead reduces the actual binary payload by 11.04% at INT4.

That changes the interpretation of the original idea. The productive abstraction is no longer:

> give every digit a third `END` state.

It is closer to:

> **quantized weights contain collectively compressible significance structure; encode that structure once per block instead of reserving the same number of positions for every weight.**

The third state was a useful way to expose the fixed-width assumption, but it is not needed to exploit the structure measured here.

## Claim boundary

These results support the narrow claim that the registered SmolLM2 group-quantized weights admit a smaller **lossless post-quantization binary representation** under the specified bitplane-enumerative accounting, and that this block-local representation beats both fixed width and the raw-symbol reduction observed in the ternary experiment.

They do **not** establish that the format improves end-to-end model size once every production metadata/alignment requirement is included; that compressed weights can be multiplied without decode/unpack overhead; that inference becomes faster or more energy efficient; that GPU/CPU kernels will benefit; that enumerative subset ranking is the best practical bitplane codec; or that this beats production quantization/compression systems. The next experiment must measure an actual packed encoder/decoder and inference-relevant decode throughput before making a systems claim.
