---
type: "Companion Note"
title: "MultiEURLEX-21 PT — staged pipeline, semantic cache dataset and fast MaleCNS reservoir"
description: "Engineering note for the frozen-MaleCNS MultiEURLEX-21 PT benchmark: three-stage pipeline (semantic cache as a published dataset, reservoir/controls, official evaluator), canonical-vs-fast equivalence gates, label-free controls, and the local CPU throughput milestone."
tags: [malecns, multieurlex, mteb, semantic-cache, throughput, reproducibility]
timestamp: 2026-09-15T18:00:00+00:00
---

# MultiEURLEX-21 PT — staged pipeline and throughput work

Date: 2026-09-15. Infrastructure only: the scientific protocol of
`preregistered-multieurlex21-pt-2026-09-15.md` and its encoder amendment are
unchanged. Nothing here reads benchmark labels, touches the dataset revision or
the official splits, or selects hyperparameters on test.

## Why

The first official run (`run 35001017472`, ref `27db9c7`) pays MiniLM + E5 for
every document each time the MaleCNS reservoir is evaluated, and runs the
reservoir at batch 16 with ragged batches. The MTEB evaluator itself only ever
encodes the unique undersampled train documents (≤ `n_experiments ×
samples_per_label × 21` ≈ 1.7k) plus the test split, so the real cost is per
document, and it was being paid in the wrong place.

## Stages

| stage | script | input → output |
|---|---|---|
| A | `scripts/build_multieurlex_semantic_cache.py` | official MTEB task data → one parquet table per encoder + `manifest.json` (unit chunk vectors, `id`/`split`/`chunk_index`, `text_sha256`, provenance columns, per-encoder fingerprints) |
| B | `scripts/encode_multieurlex_documents.py` | semantic cache (directory or `hf:<repo>`) → `documents.npz` (`doc_key`, 256-d embeddings) for one variant, with engineering metrics and an optional equivalence gate against a reference file |
| C | `scripts/run_multieurlex21_pt_mteb.py --document-embeddings documents.npz` | unchanged official evaluator, served by text hash |

The semantic cache is a first-class dataset, not a scratch file: encoders are
computed independently (`--models` one at a time, possibly on different
machines) and joined on `(id, split, chunk_index)`; the join refuses tables
whose rows, dataset revision or chunking version differ. `--push-to-hub`
publishes the full cache as `franklinbaldo/multieurlex21-pt-semantic-cache`
with a dataset card; partial caches are refused for publication. Fusion order
is part of the representation and is fixed to MiniLM ‖ E5 (`encoder_order` in
the manifest), exactly as in the first official run — a cross-check against
npz-era canonical embeddings caught an alphabetical ordering bug before it
shipped.

The live path (`run_multieurlex21_pt_mteb.py --graph …`) still exists and is
what the first official run used. `FrozenMaleCNSEncoder` now delegates to
`malecns_wifi.document_reservoir.DocumentReservoir`; the `canonical` backend is
tested bit-exact against the verbatim arithmetic of ref `27db9c7`.

Per-encoder fingerprint covers: dataset path + revision + subset + splits +
per-split cap, encoder name + HF revision + E5 prefix, chunking policy,
`max_chunks`, `chunk_chars`. A cache built with a different spec is refused.

## Backends

`canonical` is the original step. `fast` keeps the same floating-point
operations in the same order and only removes work that is identically zero:

1. the recurrent SpMM at step 0 is skipped (`W @ 0 == 0`, `0 * gain + d == d`);
2. the sensory drive is added in place on the recurrent term (`x + 0 == x` on
   non-sensory rows) instead of materialising a dense `[neurons, batch]` drive;
3. batches are grouped by window count, so no masked column-steps are computed.

Because the reservoir columns are independent documents, grouping changes which
documents share a batch but not any document's arithmetic. CSR index dtype
(`int64`/`int32`) is a separate switch.

Equivalence gate (checked by stage B `--reference` and by the benchmark):
`max_abs_error ≤ 1e-5` and per-document cosine `≥ 0.999999` against the
canonical batch-16 embeddings. Bit-exactness is reported but not required.

## Label-free controls (same semantic inputs)

| variant | what it is | answers |
|---|---|---|
| `fused-mean` | unit mean of the fused MiniLM+E5 chunk vectors (768-d) | the frozen encoders alone |
| `fused-mean-proj` | the same mean through a fixed seeded Gaussian projection to 256-d | width-matched frozen encoders |
| `sensory-only` | the exact MaleCNS pipeline with `gain = 0` (sensory projection → leaky tanh → sparse readout, no recurrence) | the projection scaffolding without the graph |
| `malecns` | full frozen reservoir | the graph's contribution |

Random-graph, shuffled-weights and binary-topology arms come after these and use
the same cache; they are not part of this infrastructure PR.

## Engineering metrics recorded per run

docs/s, chunks/s, MiniLM seconds, E5 seconds, reservoir forward seconds, SpMM
call count and column-SpMV equivalents, mean SpMM time, masked column-steps,
peak RSS, peak VRAM (CUDA), cache size, equivalence report.

## First official run, for scale

`run 35001017472` (T4, ref `27db9c7`, live path): 5,956 documents encoded
(956 unique undersampled train + 5,000 test), 12,469 semantic chunks, 367 s of
evaluation, 1.39 GB peak VRAM, accuracy 0.02978 / LRAP 0.4185 / F1 0.2658 /
hamming 0.3316. Roughly 16 docs/s end to end, dominated by MiniLM + E5.

## Local CPU milestone (i5-1145G7, 4 cores, torch 2.14 CPU, no CUDA)

Deterministic 64-document prefix of `train` and `test` (partial cache, 128
docs, 246 chunks, histogram {1: 65, 2: 31, 3: 9, 4: 23}).

```text
semantic cache:
  128 docs, 246 chunks, 1.1 MB (two parquet tables)
  MiniLM time: 21–114 s   (CPU, batch 16)
  E5 time:     67–312 s   (CPU, batch 16; 512-token windows dominate)

MaleCNS canonical (batch 16, ragged, int64):
  63–67 docs/s, 1.9–2.0 s total, 32 SpMM calls (36–38 ms each), 266 masked column-steps

MaleCNS fast (grouped batches, step-0 SpMM skipped, in-place drive):
  int64 b16   194 docs/s   2.9x   max_abs_error 9.7e-08   min cosine 0.99999988   gate PASS
  int32 b16   236 docs/s   3.5x   max_abs_error 9.7e-08   min cosine 0.99999988   gate PASS
  int32 b64   203 docs/s   3.1x   (CPU SpMM cost grows ~linearly with batch; GPU is the
                                    place where wider batches should pay off)

no-MaleCNS controls (same fused inputs):
  fused-mean        63,000 docs/s
  fused-mean-proj   11,000 docs/s    mean cosine to MaleCNS 0.008 (different projection, expected)
  sensory-only         180 docs/s    mean cosine to MaleCNS 0.950
```

End-to-end check: the official evaluator run in `--smoke` mode (64/64 caps)
gives identical scores from the live encoder (48 s, of which 45.7 s are
MiniLM/E5 and 1.9 s the reservoir) and from stage-B cached embeddings (0.2 s):
accuracy 0.03125, LRAP 0.333247, F1 0.129946, hamming 0.201451.

Reading: on this benchmark the reservoir is a few percent of the cost; caching
the semantic stage removes ~95 % of the work of every subsequent MaleCNS
variant. The fast path is equivalent within 1e-7 and not bit-exact only because
grouped batches change which columns share an SpMM. The `sensory-only` cosine
of 0.95 says the recurrent graph moves the final embedding modestly relative to
the projection scaffolding; whether that movement carries signal is what the
official evaluator on the controls will tell, and it is not read here.

GPU numbers (T4) come from the Colab executor workflow
`MaleCNS MultiEURLEX-21 stages Colab` in `franklinbaldo/franklinbaldo.github.io`,
which also publishes the full semantic cache and runs stage C on every variant.
