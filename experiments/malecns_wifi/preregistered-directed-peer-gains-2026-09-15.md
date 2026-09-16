# Preregistered follow-up — directed peer teaching gains

Date: 2026-09-15

## Question

Does a directed training-only teaching matrix `r_{j→i}` improve cross-channel learning over the already tested scalar per-channel reliability `r_j`, without adding an inference-time attention router?

## Frozen architecture

- one trainable embedding adapter per `(embedding model, chunk scale)` channel;
- one native flavour/reference state per channel;
- MaleCNS remains the multimodal integrator at inference;
- no attention budget and no explicit inference-time channel router;
- cross-channel coupling is used only as a training signal;
- `peer_lambda = 0.50` is frozen from the previous exploratory grid;
- no equal-vote arm is tested here.

## Directed gain estimator

For training bytes only, before learning, compute each channel's initial local probability `p_c(t)` against its native flavour and the binary target `y(t)`.

For receiver `i` and sender `j != i`:

- receiver need: `n_i(t) = |y(t) - p_i(t)|`;
- sender competence: `q_j(t) = 1 - |y(t) - p_j(t)|`;
- raw directed usefulness: `u_{j→i} = mean_t[n_i(t) * q_j(t)]`.

Each receiver row is normalized over `j != i` to mean 1. The diagonal is zero. This makes a sender influential for receiver `i` when it tends to be correct specifically on bytes where `i` needs help.

No validation bytes are used to estimate this matrix.

## Arms

Two new seeds: `20260918`, `20260919`.

Within each seed, identical initialization and cached semantic inputs:

1. `independent`: `peer_lambda = 0`;
2. `scalar_reliability_0.50`: existing training-only scalar reliability `r_j`;
3. `directed_reliability_0.50`: directed matrix `r_{j→i}` defined above.

## Primary metric

Final `all_direct / unseen_generalization` AUPRC.

## Preregistered interpretation

The directed mechanism is supported for this curriculum if:

1. directed unseen-generalization AUPRC exceeds scalar reliability on both new seeds;
2. mean directed-minus-scalar unseen-generalization gain is positive;
3. mean directed-minus-scalar `all_direct / all` AUPRC is no worse than `-0.02`.

Secondary descriptive readouts:

- dropout arms (`no_128`, `no_encoder_0`, `no_encoder_1`, `minilm_short_only`);
- full `6×6` directed gain matrix;
- which sender→receiver relations dominate;
- adapter movement and flavour-anchor cosine.

This is still exploratory curriculum evidence, not Stage A/B confirmatory evidence. A failure does not justify retuning the matrix on the same validation set; the next step would be a new estimator or broader concept/text diversity.