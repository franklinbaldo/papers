---
type: "Findings Record"
title: "Findings — Packed BPE1 Bitplane Container and Native Decode Benchmark"
description: "Execution record for the systems follow-up that materializes the bitplane-enumerative representation as a real indexed binary container and benchmarks a portable native decoder on the pinned SmolLM2 checkpoint."
tags: [llm, quantization, compression, bitplanes, systems, benchmark, findings]
timestamp: 2026-08-31T09:00:00-04:00
---

# Findings — packed BPE1 bitplane container and native decode benchmark

## Frozen protocol

This record executes `packed_protocol.md`, the systems follow-up frozen after `BINARY_FINDINGS.md` had established that block-local bitplane significance compresses the registered quantized SmolLM2 weights in ideal payload accounting.

Model identity: `HuggingFaceTB/SmolLM2-135M`, revision `d6a5589c239236d22370e2126bbe23d4843c47d9`, checkpoint SHA-256 `80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1`, NumPy 2.5.2, group size 128.

Registered execution: GitHub Actions run `33392861216` against repository commit `a3f90b77cba101e5e2fe0297218c10a85f497f7a`. Runner: x86_64 Linux `6.17.0-1022-azure`, glibc 2.39, GCC 13.3.0. The benchmark used one warm-up pass, five timed sequential passes, 10,000 random block probes, and resident files. Raw outputs are committed as `packed_build.json`, `packed_bench_int4.json`, `packed_bench_int8.json`, and `packed_results.json`.

The execution covered 211 matrix-like tensors, 1,050,624 quantization blocks, and 134,479,872 weights at each registered width.

## Actual container result

The earlier bitplane experiment reported ideal bit-level payload costs of approximately 3.5585 bits/weight for INT4 and 7.5775 bits/weight for INT8. BPE1 turns that representation into an actual byte-addressable file and charges:

- a 25-byte file header;
- a 2-byte header for every block;
- byte padding inside encoded block payloads;
- an explicit 64-bit index entry every 32 blocks.

| width | fixed bytes | BPE1 bytes | actual bits/weight | size ratio | actual saving |
|---|---:|---:|---:|---:|---:|
| INT4 | 67,239,936 | **62,616,026** | **3.72493** | **0.93123** | **6.88%** |
| INT8 | 134,479,872 | **130,194,198** | **7.74505** | **0.96813** | **3.19%** |

The actual files are therefore smaller than fixed width at both widths. INT4 saves 4,623,910 bytes; INT8 saves 4,285,674 bytes.

The engineering overhead is material but does not erase the effect. At INT4, ideal bitplane accounting implied an 11.04% saving; the real container retains 6.88%. At INT8, the ideal 5.28% saving becomes 3.19%.

### Where the overhead went

For INT4:

- unpadded encoded payload: 478,552,782 bits;
- byte-padding overhead: 3,463,994 bits;
- payload bytes after padding: 60,252,097;
- per-block headers: 2,101,248 bytes;
- sparse index: 262,656 bytes;
- file header: 25 bytes.

For INT8:

- unpadded encoded payload: 1,019,027,276 bits;
- byte-padding overhead: 3,614,876 bits;
- payload bytes after padding: 127,830,269;
- per-block headers: 2,101,248 bytes;
- sparse index: 262,656 bytes;
- file header: 25 bytes.

So the compression effect is not an accounting artifact: it survives byte packing, explicit block boundaries, and bounded random-access metadata.

## Exactness

The Python reference decoder reconstructed all 134,479,872 quantized weights at both widths from the serialized BPE1 files. `python_verified` is true for INT4 and INT8.

The native benchmark also computes checksums during sequential and random-block decoding so timed paths cannot obtain speed by skipping reconstruction work.

BPE1 file SHA-256 values:

- INT4: `63ee06f955490fd6058f669be34972174f14109076681bb1b7d836dc059a42b5`;
- INT8: `459c5d33c8afc9a161359161e9b78cdc585c9568d32781073c612f9497796c18`.

## Sequential decode throughput

The portable native decoder was compiled as C11 with `gcc -O3`. It is a reference decoder, not a SIMD implementation and not a fused matrix kernel.

| width | fixed unpack | BPE1 decode | BPE1 / fixed | slowdown |
|---|---:|---:|---:|---:|
| INT4 | 240.39 M weights/s | **37.63 M weights/s** | **0.1565×** | **6.39×** |
| INT8 | 458.46 M weights/s | **18.18 M weights/s** | **0.0397×** | **25.21×** |

This is the strongest negative systems result of the third round. The representation compresses, but the straightforward combinatorial decoder is substantially slower than ordinary fixed-width unpacking.

The aggregate registered gate `P3_practical_sequential_reference_decode` is **PASS** because its frozen threshold was `>= 0.10×` fixed throughput at at least one registered width. INT4 passes that threshold at 0.1565×. INT8 does **not** pass it individually: 0.0397× is far below the threshold. The aggregate PASS must not be read as evidence that both widths have practical decode throughput.

## Random block access

BPE1 stores an index entry every 32 blocks. Reaching an arbitrary block therefore requires jumping to the nearest indexed block and scanning at most 31 block headers before decoding the target.

| width | fixed random access | BPE1 random access | latency ratio |
|---|---:|---:|---:|
| INT4 | 0.691 µs/block | **3.670 µs/block** | **5.31×** |
| INT8 | 0.396 µs/block | **7.648 µs/block** | **19.33×** |

The bounded-access design works as specified, but bounded does not mean cheap. The same complexity that hurts sequential decode also appears in block seek/decode latency, especially at INT8.

## Gates

- **P0 — corpus identity: PASS.** Checkpoint, tensor count, weight count, and group size match the previous registered runs.
- **P1 — exact packed round-trip: PASS.** Both serialized files reconstruct every quantized weight exactly in the independent Python verifier.
- **P2 — real container size win: PASS.** Actual BPE1 files are 0.9312× fixed INT4 and 0.9681× fixed INT8.
- **P3 — practical sequential reference decode: PASS, via INT4 only.** INT4 reaches 0.1565× fixed throughput; INT8 reaches only 0.0397×.
- **P4 — bounded random access: PASS.** Index stride is 32 blocks, so seek work is structurally bounded. Measured latency is nevertheless 5.31× fixed at INT4 and 19.33× at INT8.
- **P5 — systems claim boundary: PASS.** No end-to-end inference-speed, energy, or kernel-efficiency claim follows from this benchmark.

## Interpretation

The third experiment resolves the main uncertainty left by `BINARY_FINDINGS.md`.

### 1. The compression is real

The 11.04% / 5.28% ideal bitplane savings were not merely a fractional-bit accounting effect. Once the representation is converted to an ordinary byte stream with explicit headers, padding, and an access index, it still saves **6.88% at INT4** and **3.19% at INT8**.

This supports treating collective bitplane significance as a genuine post-quantization compression mechanism for this model and quantizer.

### 2. The current decoder is not inference-competitive

A portable scalar `-O3` implementation pays too much for combinatorial subset reconstruction. INT4 decode is about 6.4 times slower than fixed unpack; INT8 is about 25 times slower. Random block access shows the same qualitative problem.

Therefore the present result supports **storage compression**, not a claim that BPE1 should directly replace a fixed INT4/INT8 inference layout.

### 3. The next question is no longer codec correctness

The representation, container, exact decoder, size advantage, and bounded indexing are all demonstrated. The remaining systems question is whether decoding can be moved off the critical path or fused with useful computation.

The next defensible experiment should therefore compare at least one of:

1. a vectorized/SIMD bitplane decoder against the scalar reference;
2. decode directly into dot-product/GEMV accumulation instead of materializing all integer weights;
3. a fused BPE1-to-GEMM/GEMV kernel where reduced memory traffic can potentially compensate for decode work;
4. alternative block codecs chosen for cheaper decoding, using BPE1's measured 6.88% INT4 saving as the compression target to beat.

A fourth experiment should be considered successful only if it improves an inference-relevant time or bandwidth metric, not merely if it preserves the compressed byte count.

## Claim boundary

These results support the claim that the registered SmolLM2 quantized weights admit an **actual, exact, indexed binary container** smaller than fixed sign-magnitude INT4/INT8 under the BPE1 format.

They do **not** support the claim that BPE1 currently makes inference faster, that its reference decoder is competitive with fixed unpacking, that its random access is cheap, that the observed storage saving survives scale metadata and every production layout requirement, that it is superior to production quantization formats, or that combinatorial bitplane coding is the final codec design.
