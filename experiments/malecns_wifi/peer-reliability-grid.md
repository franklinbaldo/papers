# Peer-reliability grid — exploratory preregistration

Status: exploratory follow-up, registered before reading the grid result.

## Question

Does reliability-weighted cross-channel teaching improve the per-(encoder, scale)
adapter system without destroying held-out synonym generalization or robustness to
missing expensive channels?

## Frozen architecture

- two embedding models: MiniLM and multilingual E5;
- scales: 8, 32, 128;
- one independent trainable residual adapter per `(encoder, scale)` channel;
- one independent flavour/reference vector per `(encoder, scale)` channel;
- no vector arithmetic across incompatible embedding spaces;
- full frozen MaleCNS recurrence and the same fixed sensory/readout projections as
  the successful v3 adapter smoke;
- channel translators fitted on aligned training bytes only;
- validation includes `all_direct`, `no_128`, `no_encoder_0`, `no_encoder_1`, and
  `minilm_short_only`.

## Peer reliability

Before any adapter/flavour learning, each channel is scored on training bytes only
using its initial flavour and balanced BCE.  Its fixed reliability is
`exp(-balanced_bce)`, normalized so the six channel weights have mean 1.

During peer teaching, channel `c` never votes for itself.  The teacher for `c` is
formed from the reliability-weighted mean probability of the other channels.  The
hard reward remains primary: `teacher = 0.65 * target + 0.35 * peer`.

Reliability is fixed for the entire run.  Validation bytes never influence the
weights.

## Grid

Run the same initialization and cached inputs with:

- independent control: `peer_lambda = 0`;
- reliability-weighted `peer_lambda = 0.05`;
- reliability-weighted `peer_lambda = 0.10`;
- reliability-weighted `peer_lambda = 0.25`;
- reliability-weighted `peer_lambda = 0.50`.

All arms use the same epochs, learning rate, adapter rank, residual scale, graph,
projections, examples, translators and seed.

## Primary readout

Primary descriptive comparison: final `all_direct / unseen_generalization` AUPRC.
A weighted peer arm is considered promising for the next follow-up if it exceeds
the independent control on that quantity without reducing `all_direct / all`
AUPRC by more than 0.02.

## Robustness readout

Among promising arms, inspect retention under `minilm_short_only` and `no_128`.
A useful coupling rule should not rely on a channel that disappears at inference.
No topology or general semantic claim follows from this smoke alone.

## Interpretation guardrails

- This is a tiny synthetic curriculum smoke, not Stage A/B confirmatory evidence.
- The lambda grid is exploratory hyperparameter screening.
- No post-result change to the grid, reliability formula or primary descriptive
  comparison belongs to this run.
- Any subsequent confidence scheme learned online, per-example, or from validation
  requires a separate follow-up.
