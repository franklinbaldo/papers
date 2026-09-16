# Closed-loop embedding translation through frozen MaleCNS

## Question

Can a frozen MaleCNS recurrent substrate, surrounded by small trainable low-rank interfaces, support iterative translation between two representation spaces?

The first concrete translation is:

```text
MiniLM -> MaleCNS -> E5
```

This branch starts with an **engineering smoke**, not a scientific result.

## Architecture

```text
embedding A
    |
low-rank adapter_in
    |
frozen MaleCNS state h_t
    |
fixed state projection
    |
low-rank adapter_out
    |
B_hat_t
    |
teacher error / quality features
    |
low-rank adapter_feedback
    |
same persistent MaleCNS state
    +-------------------------^
```

MaleCNS connectivity is never an optimizer parameter. Gradients may flow through the recurrent computation into the interfaces.

The modules are called **trainable low-rank adapters**, not LoRA, because this first implementation learns `B(tanh(Ax))` directly rather than a low-rank delta on top of a frozen matrix.

## Phase 1: supervised recurrent correction

During training the target B embedding is available to construct feedback features:

```text
prediction
B_target
B_target - prediction
cosine(prediction, B_target)
||B_target - prediction||
```

Therefore this phase is explicitly **teacher feedback**. It must not be described as autonomous inference.

Autonomous feedback is a separate later experiment in which a learned critic/predictor replaces access to `B_target`.

## First fixed protocol

```text
source: MiniLM
target: E5
rank: 16
T: 4
state: persistent across all correction rounds
MaleCNS: frozen
MiniLM: frozen
E5: frozen
```

The implementation exposes `T + 1` estimates (`B_hat_0 ... B_hat_T`) so the trajectory itself is measurable.

## Required smoke invariants

Before using real cached embeddings, prove on a tiny operator that:

- forward executes;
- backward executes;
- gradients reach `adapter_in`, `adapter_out`, and `adapter_feedback`;
- recurrent operator remains frozen;
- fixed readout projection remains frozen;
- recurrent state persists rather than resetting between rounds;
- closed-loop and open-loop produce the same first estimate;
- feedback changes a later recurrent state;
- cosine/error trajectories are finite;
- direct low-rank baseline trains independently of any recurrent operator.

These checks live in `tests/test_closed_loop_translation.py`.

## First real smoke

Use 100--1000 paired texts already present in the semantic-cache pipeline where possible. Do not re-embed data unnecessarily.

Arms:

1. direct low-rank: `MiniLM -> adapter -> E5`;
2. MaleCNS open-loop: same input/output interfaces, feedback disabled;
3. MaleCNS closed-loop: teacher feedback enabled;
4. degree-preserving-null closed-loop using the existing topology-null infrastructure.

A small MLP and matched random recurrent network are required before any scientific claim, even if they are not needed to validate the first engineering path.

## Metrics

Primary smoke diagnostics:

```text
cosine_t
||error_t||
error_contraction_t = ||e_(t+1)|| / ||e_t||
```

Scientific runs additionally report retrieval@1, retrieval@10, MSE, local-kNN preservation, Spearman distance correlation, and CSLS retrieval where appropriate.

The key closed-loop question is not only final quality but whether `quality(t)` improves iteratively.

## Claim boundary

A positive engineering smoke proves only that the system is trainable and that feedback causally changes later state.

A MaleCNS-specific scientific claim requires the biological graph to beat, under matched data/seeds/budget:

- MaleCNS open-loop;
- degree-preserving/null topology;
- matched random recurrent network;
- direct low-rank baseline;
- small MLP.

If generic recurrent controls match or beat MaleCNS, the result may still support **generic recurrent closed-loop representation translation**, but not a biological-topology-specific claim.

## Stack choice

This branch is based on `experiment/malecns-local-cpu-studies` (#462), because that stack already contains both:

- the differentiable frozen whole-brain recurrence / trainable-interface code inherited from the fly-assisted work;
- `FastSpMV`, which caches the transposed sparse operator for a much cheaper CPU backward pass.

The semantic-cache/provenance infrastructure in #464 is a sibling stack and should be integrated rather than reimplemented when this smoke graduates to real MiniLM/E5 data.
