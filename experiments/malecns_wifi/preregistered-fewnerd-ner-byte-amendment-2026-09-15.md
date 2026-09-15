# Preregistration amendment — Few-NERD byte-level axis

Date: 2026-09-15

This amendment is recorded before the first Kaggle runner for the Few-NERD front.

## Byte-level representation

The internal sequence axis of the MaleCNS NER method is UTF-8 bytes, not Few-NERD tokens and not subword tokens from MiniLM/E5.

Few-NERD is distributed as token sequences. For this benchmark, reconstruct each sentence canonically by joining the official token strings with exactly one ASCII space (`U+0020`). This deterministic reconstruction defines the byte axis used by the method.

For token `i`, record the half-open UTF-8 byte interval `[byte_start_i, byte_end_i)` in that reconstructed sentence. The official `ner_tags[i]` is projected to every byte inside that token interval. Separator-space bytes are assigned the outside/non-entity label and are never treated as entity evidence.

Predictions are produced on the byte axis. Benchmark evaluation converts byte predictions back to the official token/entity spans using the frozen token↔byte interval map. Exact span + entity type scoring remains the primary metric.

## Why

Byte-level operation is part of the method under test. It avoids making a particular tokenizer/subword segmentation the unit of prediction and provides a common positional axis across semantic encoders. MiniLM/E5 may tokenize internally to generate semantic channels, but their tokenization does not define the output grid.

## Guardrails

- The canonical reconstruction rule is frozen before training.
- No test-set inspection may alter token→byte reconstruction or byte→token decoding.
- Unicode is measured after UTF-8 encoding, never Python character count.
- Round-trip token text recovered from each byte interval must equal the original Few-NERD token bytes exactly.
- Smoke results remain non-evidentiary.
