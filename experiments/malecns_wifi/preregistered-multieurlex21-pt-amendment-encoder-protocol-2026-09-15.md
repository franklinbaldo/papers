---
type: "Protocol"
---

# Amendment — direct MTEB comparison uses a frozen MaleCNS encoder

Date: 2026-09-15

This amendment is recorded before the first MultiEURLEX benchmark run.

The public MTEB results for `MultiEURLEXMultilabelClassification` evaluate an encoder under the MTEB multilabel-classification evaluator. To preserve direct comparability, the primary MaleCNS benchmark arm will therefore be:

- `malecns_frozen_encoder`: deterministic document embeddings produced by frozen MiniLM/E5 semantic inputs passed through the frozen MaleCNS recurrent connectome; no benchmark labels are used inside the encoder.

The official MTEB evaluator remains responsible for its own few-shot training/evaluation procedure and metrics.

The previously planned supervised `malecns_state_uncertainty` arm is retained as a later task-specific extension, but it is **not** directly comparable to public embedding leaderboard rows if it uses benchmark labels to adapt the encoder. Such results must be reported separately.

No benchmark result has been observed before this amendment.
