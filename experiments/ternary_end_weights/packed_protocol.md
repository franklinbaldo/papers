---
type: "Protocol"
title: "Protocol — Packed Bitplane Codec and Decode Throughput"
description: "Third-round systems protocol testing whether the block-local bitplane-enumerative result survives real byte packing, indexing, exact decoding, and native decode benchmarks."
tags: [llm, quantization, compression, bitplanes, codec, benchmark, protocol]
timestamp: 2026-08-31T08:30:00-04:00
---

# Protocol — packed bitplane codec and decode throughput

## 1. Status and question

This is a **post-result systems follow-up** to `binary_protocol.md`. It is frozen after the binary accounting experiment found that block-local bitplane-enumerative coding used 3.5585 bits/weight at INT4 and 7.5775 bits/weight at INT8 on the registered SmolLM2 checkpoint.

The previous round counted an exact code but did not emit a file, charge byte alignment and seek metadata, or execute a decoder. This round asks:

> Does the bitplane result survive as a real binary format once every container byte is charged, and what decode/seek cost does a straightforward native implementation impose relative to fixed-width packing?

This is a reference-codec experiment, not a claim that the codec is kernel-ready.

## 2. Registered corpus and quantization

Use exactly the same corpus and quantizer as the prior two model-backed rounds:

- model: `HuggingFaceTB/SmolLM2-135M`;
- revision: `d6a5589c239236d22370e2126bbe23d4843c47d9`;
- `model.safetensors` SHA-256: `80521b40281d6ce74e35c9282c22539e75aa0ac8578892b2a59955ef78d55da1`;
- NumPy: `2.5.2`;
- included tensors: numeric F16/BF16/F32/F64 with `ndim >= 2`;
- flatten each tensor independently and never share a quantization group across tensor boundaries;
- group size: 128;
- symmetric max-absolute-value, round-to-nearest sign-magnitude quantization;
- registered widths: INT4 and INT8.

Per-group scales and tensor metadata remain outside the comparison because they are identical requirements for fixed and compressed payloads. Every byte introduced specifically by the compressed container is charged.

## 3. `BPE1` packed format

The registered compressed container is little-endian and block-local.

### File header

The file contains:

- magic `BPE1` (4 bytes);
- bit width (1 byte);
- group size (unsigned 16-bit);
- index stride (unsigned 16-bit), fixed to **32 blocks**;
- block count (unsigned 32-bit);
- weight count (unsigned 64-bit);
- index entry count (unsigned 32-bit);
- one unsigned 64-bit absolute file offset for every 32nd block.

The index is part of the measured file size. It bounds random block lookup to at most 31 skipped block headers after one indexed seek.

### Block header

Each quantization block stores:

- `N-1` in one byte, where `1 <= N <= 128`;
- packed payload byte length in one byte.

The one-byte payload length is valid for the registered `B <= 8`, `N <= 128` format. If an encoder ever produces a payload larger than 255 bytes, that is a format failure.

### Plane payload

A block is transposed into one sign plane followed by `B-1` magnitude bitplanes. A bit writer packs fields continuously; only the **end of the block** is rounded up to the next byte.

Each plane starts with a two-bit mode:

- `00`: all zero;
- `01`: all one;
- `10`: raw `N`-bit bitmap;
- `11`: exact enumerative subset.

For enumerative mode, store:

1. `k`, the number of one positions, in `ceil(log2(N+1))` bits;
2. the combinatorial rank in `ceil(log2(C(N,k)))` bits.

Rank/unrank uses one fixed combinatorial-number-system bijection implemented by both encoder and decoder. Unused rank codepoints are invalid. For a non-constant plane, the encoder chooses raw or enumerative according to the smaller exact bit count before final block-byte padding.

## 4. Fixed-width reference stream

For the same quantized values, emit a raw fixed-width sign-magnitude stream:

- INT4: two 4-bit codes per byte;
- INT8: one 8-bit code per byte.

Zero always uses sign 0. The fixed reference needs no seek index because weight offset maps directly to a bit/byte offset. Its measured size is the actual emitted byte count.

## 5. Correctness

The Python reference encoder must provide an exact decoder. The native decoder must independently decode the same `BPE1` file.

Both decoders must reproduce every registered quantized integer. Equality is checked by a deterministic 64-bit checksum over the complete decoded signed-integer stream and by unit tests over exhaustive/small synthetic cases.

Combinatorial rank/unrank is tested as a bijection on exhaustive small subset spaces before the model-backed result is accepted.

## 6. Benchmarks

GitHub Actions `ubuntu-latest` is the registered execution environment. Native code is compiled with the runner's default GCC using `-O3 -std=c11` without architecture-specific `-march=native`, so the result remains portable across hosted runner generations.

All benchmark files are generated once before timing and then read into memory. Timed decode therefore measures **resident decode cost**, not network or filesystem throughput.

Report separately for INT4 and INT8:

- actual compressed bytes and bits/weight;
- actual fixed bytes and bits/weight;
- compressed/fixed size ratio;
- native sequential fixed-width decode throughput in million weights/s;
- native sequential `BPE1` decode throughput in million weights/s;
- throughput ratio compressed/fixed;
- random block decode latency for `BPE1` over 10,000 deterministic pseudo-random block IDs, in microseconds/block;
- fixed-width random block decode latency over the identical block IDs;
- random latency ratio compressed/fixed.

Sequential benchmark reports the median of five timed passes after one warm-up. Random benchmark also performs one warm-up sequence before timing.

The benchmark checksum must remain identical across every timed pass; a faster incorrect pass is a failure.

## 7. Gates

### P0 — corpus identity

**Pass:** model revision/hash, tensor rule, tensor count, group size, and weight count match the previous registered SmolLM2 rounds.

### P1 — exact packed round-trip

**Pass:** Python and native decoders reproduce the exact quantized stream for both INT4 and INT8, including tensor-tail blocks.

Failure invalidates all size and timing results.

### P2 — real-container size win

**Pass:** after charging the complete header, periodic index, every block header, and byte padding, `BPE1` is smaller than the emitted fixed-width stream at INT4 or INT8.

This is the principal test of whether the prior bit-count win survives implementation.

### P3 — practical sequential reference decode

Report rather than reinterpret the throughput. For an explicit prototype threshold, **pass** if native `BPE1` sequential decode reaches at least 10% of the native fixed-width decoder's million-weights/s throughput at either width.

Failure does not refute compressibility; it means this straightforward enumerative decoder is not yet a practical inference layout without a substantially better decoder/kernel.

### P4 — bounded random access

**Pass:** every requested block is reachable from the periodic index by scanning at most 31 intervening block headers and decodes correctly. Report latency ratio to fixed width; there is no speed-win requirement because fixed width has direct addressing by construction.

### P5 — systems claim boundary

No result may claim faster LLM inference, lower end-to-end latency, lower energy, or production readiness. The codec benchmark decodes integers but does not perform matrix multiplication. A storage win plus acceptable decoder throughput only justifies a subsequent fused-kernel experiment.

## 8. Kill/continue rule

- If P1 fails, stop: the format is incorrect.
- If P2 fails at both widths, stop treating the current byte-packed representation as a storage improvement; the theoretical bitplane result did not survive container overhead.
- If P2 passes but P3 fails, preserve the format as a compression result but do **not** advance to inference claims; the next work must target a faster decoder or a different block code.
- If P1, P2, and P3 pass, the next justified experiment is a fused unpack + dot-product/matmul microkernel against the same quantized blocks.

## 9. Reproduction

The GitHub Actions workflow pins the checkpoint and dependency versions, builds the codec files, runs exactness tests, compiles the native benchmark, executes five-pass sequential and 10,000-block random-access measurements, and uploads the JSON result plus packed-size metadata as artifacts.
