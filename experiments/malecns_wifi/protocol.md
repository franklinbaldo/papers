---
type: "Protocol"
title: "MaleCNS Reservoir — Compile, Control and Document-Task Protocol v1"
description: "Preregistered protocol for compiling MaleCNS v1.0 into a fixed sparse reservoir and testing it on a document-level task against a degree-preserving null and a matched random ESN."
tags: [malecns, drosophila, connectome, reservoir-computing, memory-capacity, ridge-readout, causaganha]
timestamp: 2026-09-14T15:40:00+00:00
---

# MaleCNS Reservoir — Compile, Control and Document-Task Protocol v1

## Question

Can the released MaleCNS v1.0 connectome serve as a useful fixed recurrent reservoir, with only an input adapter and readout trained for the task?

The experiment does **not** assume a biological advantage. The MaleCNS topology must beat or complement simpler matched baselines before any such claim is made.

## Relation to concurrent community work

Several public projects run the full MaleCNS as a recurrent operator. None has published a controlled topology result — positive or cleanly negative — so the contribution here is the control, not the scale. Two policy differences are recorded rather than reconciled: FLM retains ~25.6M connections with no synapse threshold and no sign, whereas this operator retains 10.2M (at least 3 synapses, neuromodulators zeroed). If a result turns out to depend on the sign convention, the unsigned variant is run as an ablation rather than substituted.

**Change in v1.** v0 went straight from the compile gate to a task on a 512-node subgraph. v1 runs the task on the whole compiled brain, keeps both nulls, and adds a task-free operator characterisation — spectral radius, memory capacity, echo state property — as a **background measurement, not a gate**. The single characterisation number the task needs is the spectral radius, which sets the gain; the rest is an appendix that explains a result rather than licensing one.

The reason the characterisation exists at all is the byte-tagger result on the 512-node subgraph, where the reservoir and a byte-only baseline were indistinguishable and the outcome had several live alternative explanations. The reason it is not a gate is that boldness here means skipping prerequisites, never skipping controls: the two nulls in this protocol are not optional, and no result leaves the repository without them.

## Gate 0 — reproducible connectome artifact

Source: the public MaleCNS v1.0 flat-connectome release from Janelia. The workflow may use a byte-identical mirror (for example Internet Archive) when a mirror base URL is supplied, but records the actual URLs, byte sizes, and SHA-256 hashes in `manifest.json`.

Node policy:

- retain `status == Traced`;
- exclude explicit glia;
- preserve stable body IDs in the artifact;
- carry `superclass` and `class` per neuron, so input and readout populations can later be selected by cell type rather than by degree.

Edge policy for this first runtime:

- retain directed neuron-to-neuron pairs with at least 3 reconstructed synapses;
- use synapse count as connection magnitude;
- presynaptic acetylcholine is positive;
- GABA, glutamate, and histamine are negative;
- dopamine, octopamine, serotonin, unclear, and unknown are zero in the fast recurrent operator rather than being assigned a fictitious excitatory/inhibitory sign;
- store the operator as `W[post, pre]` in CSR form.

The manifest records the full edge funnel — raw pairs, pairs above the synapse threshold, pairs whose endpoints both survive the node policy, and pairs dropped because the presynaptic transmitter maps to zero — so that no step of the reduction is inferred from a difference of two totals.

This policy is intentionally aligned with an independently published MaleCNS build path so the first compile has an external sanity target. The expected order of magnitude is about 165k retained neurons and about 10M signed recurrent edges. A mismatch is a debugging result, not something to tune away.

## Gate 1 — runtime smoke

Before attaching any task, a deterministic seeded perturbation is injected into a small input population. The recurrent state must:

1. remain finite for all smoke steps;
2. spread beyond the directly stimulated population;
3. be reproducible from the same compiled graph and random seed.

The smoke dynamics are a bounded computational reservoir, not a claim of biophysical membrane simulation.

## Background measurement — operator characterisation (task-free, not a gate)

Gate 1 only shows the operator does not explode. This measurement asks a question that explains task results rather than blocking them: **how many steps of input history does this operator hold, and does it hold more than a null that preserves its degrees?** It runs in the background and its output is an appendix. Only one number from it is on the critical path: the spectral radius, which sets the operating gain.

### Update rule

    x <- (1 - leak) * x + leak * tanh(gain * W_hat x + w_in u)

with `W_hat = W / rho(W)`, so `gain` *is* the spectral radius of the linear part. `rho` is estimated by the growth rate of the power iteration, `||W^k v||^(1/k)`, which converges to `|lambda_max|` even when the dominant eigenvalue is complex; the spread of the final ratios is reported so a non-converged estimate cannot be mistaken for a converged one.

Normalising by the largest absolute row sum — the Gershgorin bound used by the Gate 1 smoke — is rejected here: it guarantees contraction but scales the whole operator by its single worst hub.

### Controls

Two nulls, both matched to the real operator and both required:

1. **Degree-preserving null.** Directed configuration model: each edge keeps its presynaptic neuron, its weight and therefore its sign, and is handed a postsynaptic target drawn from the multiset of real postsynaptic endpoints. In-degree and out-degree are preserved exactly per neuron; reciprocity, motifs and modularity are destroyed. Self-loops and merged parallel edges are reported, not resampled away.
2. **Random ESN.** Uniformly random sparse operator with the same density and the same weight multiset. Strictly weaker than the first null — it also destroys the degree distribution — and therefore answers a different question: would any sparse recurrent operator do?

### Measurements

Per operator: spectral radius, Frobenius bulk scale `||W||_F / sqrt(n)`, and their ratio (spectral concentration — how far the operator is from an i.i.d. random matrix of the same energy).

Per operator and gain: Jaeger memory capacity `MC = sum_k r2(u[t-k], y_k[t])` on i.i.d. uniform input, with the linear readout fitted by ridge on a training segment and **every reported `r2` scored on a held-out segment**; the per-lag curve; the effective horizon (largest lag with `r2 >= 0.1`); the noise floor; the echo state property (does a perturbed replica re-converge); the saturated state fraction; and the ratio of recurrent drive to input drive.

The last three are confound checks, not decorations. A memory result is not interpretable if the states are saturating (the tanh is clipped, not computing), if the echo state property fails (the trajectory is not a function of the input history), or if the recurrent drive is negligible against the input drive (the "reservoir" is a memoryless nonlinearity and the topology is not in the loop at all).

### How it is read

This measurement is task-free and makes **no** claim about downstream accuracy:

- The measured effective horizon, in steps, is the upper bound on the temporal structure a downstream task can be relying on. A task whose discriminating evidence lies further back than that horizon has not been shown to test the topology, and the characterisation is how that is noticed.
- If the recurrent-to-input drive ratio is negligible at every gain the echo state property permits, the operator is not functioning as a reservoir under this normalisation, and the normalisation — not the topology — is what a later round must address.

A clean negative here is an acceptable and publishable outcome. A negative with several live alternative explanations is not, which is why the confound checks above run on every cell of the grid.

## Gate 2 — document-level task on the whole brain

After Gates 0 and 1, all conditions receive the **same frozen byte stream**, the same split, and the same fixed random input projection.

Primary task: document-level outcome classification of judicial decisions (`procedente` / `improcedente` / `parcial`, collapsed to binary if the weak label will not support three classes). The reservoir reads the whole decision byte by byte; the readout pools the descending-neuron state (final step and temporal mean).

Input and readout are anchored by cell type rather than by degree: bytes enter through `cb_sensory` and `ol_sensory`, and the readout is the 1,314 descending neurons. A second readout over a random 5k-neuron sample is reported as a comparison only if the descending readout is degenerate.

Conditions to compare:

1. char-n-gram (3–5) plus logistic regression on the raw text — the honest text baseline;
2. random ESN of matched density;
3. degree-preserving rewired MaleCNS control;
4. true frozen MaleCNS reservoir.

Only the readout is fitted, by ridge regression. The input projection is fixed and random (seeded); recurrent weights are frozen in every reservoir condition. No epochs, no checkpoint selection, no early stopping — there is nothing to select on, which is the point.

### Preregistered decision rule

Fixed before the first full run:

- **Topology advantage** is claimed only if MaleCNS beats **both** nulls on held-out data. Beating the random ESN alone shows recurrence helps, not that this wiring does.
- **Seeds:** at least 10. Seeds vary only the input projection and the null draws; the ridge readout is deterministic, so seeds are cheap and there is no excuse for fewer.
- **Test:** paired per-seed differences against each null, reported with the per-seed values, not only the means. A bimodal per-seed distribution is reported as instability, not averaged into a headline.
- **Minimum effect:** a paired mean macro-F1 gain over the degree-preserving null of at least 0.03, with at least 8 of 10 seeds in the same direction. Below that the result is reported as null.
- **If the char-n-gram baseline matches every reservoir condition**, the task did not need recurrence and that is the result.

## Evaluation rules

- Split by period or by court, never by randomly mixing documents.
- The segmenter `test.jsonl` stays untouched; all selection happens on validation.
- Weak regex labels are measured against the 17 hand-annotated gold documents, and the measured label noise is reported alongside every accuracy number.
- Report macro-F1 plus the per-class confusion, parameter counts and wall-clock inference cost for each condition.
- Do not call a result a MaleCNS advantage unless the true topology beats both nulls on held-out data.

## Determinism

Sparse matrix products on GPU are not bit-deterministic. Any confirmatory round whose claim includes reproducibility of the numbers must run on CPU with fixed ordering; otherwise determinism is claimed only over the compiled artifact (`graph.npz` plus its manifest hashes), and the runtime numbers are reported with their seeds and tolerances instead.

## Workflow output

The workflow produces:

- `graph.npz` — compiled sparse recurrent operator, plus body IDs, transmitter signs, `superclass` and `class`;
- `manifest.json` — source provenance, hashes, policy, and the full edge funnel;
- `smoke.json` — deterministic runtime trace (Gate 1);
- `characterization.json` — spectral radius, memory capacity sweep and confound diagnostics for the real operator and both nulls (background measurement).

No task performance claim is made by this workflow.
