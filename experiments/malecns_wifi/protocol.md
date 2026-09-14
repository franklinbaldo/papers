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

with `W_hat = W / rho(W)`, so `gain` *is* the spectral radius of the linear part. See "Operating point" below: on this operator that normalisation is measured to be the wrong one, and the task runs row-normalised instead. `rho` is estimated by the growth rate of the power iteration, `||W^k v||^(1/k)`, which converges to `|lambda_max|` even when the dominant eigenvalue is complex; the spread of the final ratios is reported so a non-converged estimate cannot be mistaken for a converged one.

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

## Operating point — measured, not assumed

**The rule.** Each operator picks its own gain from a shared logarithmic grid, `{0.25, 0.5, 0.95, 1.5, 2.5, 4} x (1/rho)`, selected on validation and scored on held-out data. Matching operators on a single scalar of the spectrum is ill-posed when the spectra have different shapes: MaleCNS is rank-2-plus-bulk, the nulls are flat, and there is no "same operating point" between those objects — only the best of each. This is standard ESN practice (one hyperparameter per model) and it asks the right question: topology at its best against null at its best. As robustness, the same contrast is reported at both fixed points, rho-matched (0.95) and bulk-matched (~3.2), so the reader can see how much the answer depends on the criterion. If MaleCNS wins at only one of them, that goes in the paper as it stands.

**Registered prediction.** At gain >= 1.5/rho the two hemisphere-local modes should saturate — tanh clamping v1 and v2 — and the echo state property should break, which would make the bulk-matched point unreachable for MaleCNS without saturating.

**Measured so far, and refined.** MaleCNS *does* reach bulk-matched, and reaches it exactly at the knee where clamping begins: peak |x| is 0.970 at gain 0.95 and 1.000 by gain 4.0, while the saturated fraction stays at 0 until gain 4 (1.4%) and is 11.6% at gain 8. So the prediction's conclusion ("unreachable") is wrong and its mechanism is right: the operator cannot reach bulk-matched *without beginning to clamp*.

That is a refinement, not a partial failure, and it needed the right instrument to close. A global saturated fraction does not test a claim about `v1` and `v2`. The mode-loading sweep projects the state onto the leading eigenvectors, weights saturation by the mass each mode carries, and checks the echo state property. On the row-normalised operator, 400 steps, leak 0.4, dense drive:

| gain | leading-subspace rms | subspace saturation | third-mode rms | ESP | separation |
|---|---|---|---|---|---|
| 0.25 | 0.070 | 0.000 | 0.103 | yes | 0 |
| 0.50 | 0.085 | 0.000 | 0.101 | yes | 0 |
| 0.95 | 0.155 | 0.000 | 0.109 | yes | 9e-08 |
| 1.50 | 0.766 | 0.000 | 0.128 | **no** | 2.49 |
| 2.00 | 1.246 | 0.000 | 0.136 | no | 18.4 |
| 2.50 | 1.464 | 0.013 | 0.095 | no | 46.2 |
| 3.20 | 1.596 | **0.859** | 0.041 | no | 85.4 |

Three measured facts, none of which the global fraction could show:

* **The echo state property breaks between gain 0.95 and 1.50** — separation goes from 9e-08 to 2.49. The usable ESP range is gain <= ~1, far below bulk-matched.
* **Leading-subspace saturation switches on between 2.5 and 3.2**, from 1.3% to 86%, which is exactly the bulk-matched point. At gain 3.2 the global saturated fraction was still near zero; the modes that carry the dynamics were 86% clamped.
* **The third mode is crowded out as the pair clamps**, dropping from ~0.11 to 0.041. The bulk gets quieter precisely as the slow modes pin.

So bulk-matched is reachable only at a gain where the operator has long since stopped being a reservoir: no echo state property, and most of its leading subspace clamped.

Two caveats attach to the numbers. On the row-normalised operator the leading pair is **exactly** degenerate (`lambda_2/lambda_1 = 1.000`, against 0.9848 raw), so `v1` and `v2` individually are an arbitrary basis of one 2-D invariant subspace and only the subspace total is interpretable — per-mode loadings differed 20-fold purely by basis choice. And this sweep drives all 165k neurons at `input_scale` 1.0, much harder than the task's sensory-only input; ESP and saturation thresholds both depend on drive amplitude, so these characterise the operator, not the tagger's operating point.

Document length remains a separate confound: 384-byte tails may be too short for a slow two-mode integrator to charge.

**Why the grid, in numbers.** Scaling by `0.95 / rho` was the original plan and is measurably wrong for this operator.

    rho (ARPACK)                 3776.27
    typical ||Wv|| / ||v||        149.86
    spectral concentration         24.79      (= 1 for an i.i.d. random matrix)

The spectral radius is set by one structured mode roughly 25x above the bulk, so
`0.95 / rho` leaves the typical gain at **0.038** and the recurrent drive at 0.9%
of the input drive: the topology is not in the loop at all. Raising the gain until
the bulk is live puts the dominant mode at ~24, far outside the echo state
property. For this operator a live bulk and gain-by-spectral-radius are mutually
exclusive.

Per-row normalisation by postsynaptic in-strength — each row divided by its own
in-strength, which is *not* the single max-row-sum scalar rejected above — drops
the concentration from 24.8 to 3.4 (`rho` = 1.000, typical 0.295). That is the
operating point the task uses, and it is what the 512-node v1/v2 tagger used when
it produced a working reservoir.

The two leading eigenvalues are near-degenerate (3776.27 and 3718.80) because they
are the symmetric and antisymmetric combination of two hemisphere-local modes:
`v1 + v2` carries 94.4% of its energy on the left soma side and `v1 - v2` 94.4% on
the right. The 1.5% splitting is the cross-hemisphere coupling strength. This is
why power iteration converges slowly here (as `(lambda_2/lambda_1)^k`), and it
means that under `rho` normalisation the two slowest modes are "which hemisphere
is ringing" rather than anything computational.

### Fourth condition: deflation (an ablation, not a null)

`W` with its two leading hemisphere-local modes projected out, applied matrix-free
since `W` minus a dense 165k-square update is not representable. This is not a null
model and is not scored against the decision rule — it is a question the nulls
cannot answer, because no degree-preserving rewiring reproduces that geometry:
**what does the bulk do on its own?** It separates "slow global integrator" from
"reservoir".

Only real modes are deflated. A complex pair spans a two-dimensional real invariant
subspace; removing its real part alone is not a projector and can make the spectral
radius grow rather than shrink. Skipped modes are counted in the report.

## Semantic tagging: food as a change in hierarchical relation

The food signal is not a supervised pulse over an annotated span. It comes from
the encoder itself. The **primary formulation** differences the multiscale
relations rather than the raw embeddings:

    R_i      = [alignment, residual] of chunk i against each containing parent
    F_i      = R_i(text + tag) - R_i(text)

`F_i` is *in what way the presence of this tag changes how this chunk sits inside
its local and global context* — not merely whether the passage resembles the tag.
A passage can resemble the tag while playing the role it always played, and a
passage can keep its wording while its role in the surrounding argument changes
completely. Only the second is what a tag boundary is.

The tag is appended at every scale, child and parents alike, so both sides of the
relation are read in the tag's presence and the difference isolates the change in
relation rather than a change in what was embedded.

The flat version below is kept as the reference and the fallback:

    E_t     = f(text up to t)
    E_t^tag = f(text up to t + tag)
    F_t     = E_t^tag - E_t

`F_t` is what the presence of this tag changes about the interpretation at this
point. The whole vector, not a scalar, is projected onto the gustatory population,
so different semantic directions produce different patterns across the food
neurons — distinct tastes rather than only more or less food. Intensity controls
how much; the direction of `F_t` controls which flavour.

The fly then reads two synchronised trajectories: the motion of meaning `dE_t`,
and the tag-relevance signal `F_t`. **START and END are not declared.** They are
where the signal rises and falls, which is the property that makes this
formulation better than feeding on a hand-marked span.

### Intensity: polarity is measured, never assumed

Three definitions are available and **two of them are probably inverted**. If the
text is already about the tag, appending the tag is redundant and moves the
embedding very little, so `||F_t||` and `<F_t, tag>` are expected to be *largest
where the text is least related*. Feeding on either would starve the fly exactly
over the region being looked for.

| definition | expression | expected polarity |
|---|---|---|
| `redundancy` | `exp(-||F_t||/tau)` | intended — **the default** |
| `norm` | `||F_t||` | inverted |
| `alignment` | `<F_t, tag_hat>` | inverted |
| `similarity` | `<E_t_hat, tag_hat>` | trivial control, no tag conditioning |

The answer to the inversion is not to fall back on a plain text-tag cosine. That
discards the tag-conditioning that makes the construction interesting and reduces
it to similarity search. If the encoder confirms the redundancy effect, then
**food is semantic redundancy**: a passage tastes of the tag precisely when the
tag adds nothing to it. `exp(-||F_t||/tau)` scores +0.87 against the annotated
region where `||F_t||` scores -0.89, essentially matching plain similarity (+0.89)
while still depending on what the tag does to the text. The direction of `F_t`
remains the flavour in every case; `similarity` stays as a control.

On a synthetic corpus built with the redundancy effect, the point-biserial
correlation with the annotated region is −0.89 for `norm`, −0.94 for `alignment`
and +0.89 for `similarity`.

**The relational formulation removes this problem.** Because the tag perturbs
child and parent together, the redundancy inversion does not carry over. On a
synthetic hierarchy that places a topic-similar region and a role-changing region
at different positions, so that no signal can be credited for both:

| intensity | vs role change | vs topic similarity |
|---|---|---|
| `norm` (relational) | **+0.74** | −0.37 |
| `alignment_shift` | **+0.80** | −0.25 |
| `similarity` (flat) | −0.06 | **+0.75** |

`norm` on the relation is positively correlated with role change, where `norm` on
the flat contrast was inverted. `similarity` is blind to role change and tracks
topic, which is the other question and is why it stays as a reference rather than
the signal.

Both constructions assume the effect they demonstrate, so they establish that the
mechanisms are real and separable, not that a given encoder shows them. The
definition is chosen by running `intensity_polarity` against gold spans with the
actual encoder, before any training.

Contrast magnitude is also reported **per context scale**: a boundary visible only
against the 4096-token parent is a different claim from one visible against the
256-token parent, and averaging the scales hides exactly that.

### Chunk against parent: `A_i^s = D(p_i^s) - D(c_i)`

With `D(x) = ||f(x + tag) - f(x)||`, a small `D` means the tag is redundant there.
`A_i^s > 0` therefore means the fine chunk makes the tag more redundant than its
containing context does: *this passage explains the tag better than the broad
region around it*. That is sharper than either term alone, because a whole section
about the tag gives every chunk inside it a small `D` and absolute redundancy
cannot say where within the section the answer sits.

Two limits, both measured rather than assumed:

* **The sign is encoder-dependent.** `A` is positive only if a longer chunk's
  embedding does not concentrate the shared topic more than its constituents do.
  Where parents behave like averages of their children, the averaging cancels
  per-chunk noise, the parent is the purer of the two, and `A` is negative
  throughout — about −0.26 in the answer on the synthetic corpus.
* **`A` is a within-context discriminator, not a global marker.** Outside a
  relevant section both child and parent are equally unrelated to the tag, their
  contrasts cancel, and `A` sits near zero — *above* its value inside the section.
  It must be read against the section it belongs to, or gated by absolute
  redundancy. On the synthetic corpus it separates the answer from the rest of its
  own section by 0.151 against absolute redundancy's 0.095.

### Four signals, each against every control

| signal | question |
|---|---|
| `similarity(text, tag)` | trivial baseline |
| `||F||` or its inversion | absolute contrast |
| relational `F_i^s` across scales | the multiscale hypothesis |
| `A_i^s` | does this chunk out-explain its context |

Each is run against MaleCNS, both nulls, and the direct control.

### Mandatory control

A classifier receiving `[R_t, F_t, dR_t]` with no fly — the relational states,
the relational contrast, and the motion, which is everything the fly is given. If that already delimits
the region cleanly, the encoder solved the tagging and the connectome is
decoration. The claim worth making is the connectome improving continuity, edge
placement, or the temporal decision over a noisy signal — and it is only available
once this control has been run and lost.

## Gate 2 — document-level task on the whole brain

After Gates 0 and 1, all conditions receive the **same frozen byte stream**, the same split, and the same fixed random input projection.

**Corpus scope: first-instance merits judgments that have a dispositivo.** Appellate decisions in the current corpus are ementa and header only — 90% of them carry no dispositivo and are dropped by the filter rather than silently mislabelled — so the scale collection filters for first-instance merits judgments at source. This is stated in the first line of the data section, not buried in a limitations paragraph.

Primary task: predict the dispositivo of a judicial decision from its report and reasoning alone (`favourable` / `unfavourable` / `partial`). The reservoir reads the truncated decision byte by byte; the readout pools the descending-neuron state (final step and temporal mean).

**Truncation, not masking.** Each document is cut at its last dispositivo marker ("Ante o exposto", "Diante do exposto", "Isso posto", "Pelo exposto", ...) and only the text before the cut is fed to any model, the character n-gram baseline included. Masking just the outcome phrase is not enough: the whole neighbourhood leaks — `art. 487, I` against `art. 485`, "condeno a parte autora nas custas" against "condeno o réu", "sucumbência recíproca" for a split outcome — and a character n-gram reads that as easily as it reads the phrase. The *last* marker is used because a decision quotes the ruling under appeal long before it opens its own dispositivo. What survives in the reasoning is legitimate signal, not leakage, and predicting the dispositivo from it is the long-range task the recurrence is supposed to be for.

**Labelling from the isolated dispositivo.** The label is read from the extracted dispositivo alone, never from the whole document. Labelling whole documents is what produced outcomes like "parcialmente procedente" for an order that merely declined to schedule a hearing: any outcome word anywhere — in the report of the parties' claims, in a quoted precedent — could decide the label. A document with no dispositivo marker is *dropped, not labelled*: a text with no dispositivo is not a decision with a hidden outcome, it is a procedural act. On the 17 hand-annotated documents this labeller reproduces the human label 17/17.

Input and readout are anchored by cell type rather than by degree: bytes enter through `cb_sensory` and `ol_sensory`, and the readout is the 1,314 descending neurons. A second readout over a random 5k-neuron sample is reported as a comparison only if the descending readout is degenerate.

Conditions to compare:

1. char-n-gram (3–5) plus logistic regression on the raw text — the honest text baseline;
2. random ESN of matched density;
3. degree-preserving rewired MaleCNS control;
4. true frozen MaleCNS reservoir.

Two training regimes run on the same split, in the same run, and are reported side by side.

**Ridge.** Only the readout is fitted. The input projection is fixed and random (seeded); recurrent weights are frozen. No epochs, no checkpoint selection, no early stopping — there is nothing to select on. Runs on CPU and finishes first.

**Trainable adapter.** A learned interface on both sides of the frozen operator, in the FLM design: a 64-dimensional byte embedding and a linear projection into the sensory populations on the way in, a linear readout over descending-neuron pooling on the way out, about 300k parameters. `W` never moves. Gradients reach the embedding through the frozen sparse recurrence, but not across the whole document: backpropagating through a 10M-edge product for thousands of bytes does not fit in memory, so the graph is cut at each 256–512 byte window while the state carries across detached. The state sees the document; the gradient sees a window. Epochs return — up to 30, checkpoint on best validation macro-F1, early stopping — because the validation split is now tens of documents rather than three. Needs a GPU.

**The control that makes the adapter interpretable.** An adapter of the same size wired straight from input to output with no fly in between — FLM's direct-input control. If it matches the reservoir conditions, the adapter did the task and the topology is decoration. Each null gets its own adapter too.

Also reported: adapter against ridge, per operator. If the adapter gains a lot only on MaleCNS, the signal is in the interface; if it gains equally everywhere, it is capacity.

### Preregistered decision rule

Fixed before the first full run:

- **Topology advantage** is claimed only if MaleCNS beats **both** nulls *and* the direct-input control, in the same training regime, on held-out data. Beating the random ESN alone shows recurrence helps, not that this wiring does; beating the nulls but not the direct control shows the adapter did the work.
- **Gain** is selected per operator on validation from the declared grid, never on held-out data.
- **Seeds:** at least 10. Seeds vary only the input projection and the null draws; the ridge readout is deterministic, so seeds are cheap and there is no excuse for fewer.
- **Test:** paired per-seed differences against each null, reported with the per-seed values, not only the means. A bimodal per-seed distribution is reported as instability, not averaged into a headline.
- **Minimum effect:** a paired mean macro-F1 gain over the degree-preserving null of at least 0.03, with at least 8 of 10 seeds in the same direction. Below that the result is reported as null.
- **If the char-n-gram baseline matches every reservoir condition**, the task did not need recurrence and that is the result.

## Evaluation rules

- Split by period or by court, never by randomly mixing documents.
- The segmenter `test.jsonl` stays untouched; all selection happens on validation.
- Weak regex labels are measured against the hand-annotated gold documents, and the measured label noise is reported alongside every accuracy number. The regex reading the isolated dispositivo reproduces the hand annotation 17/17, so no LLM enters the labelling pipeline — one fewer noise source to account for. A stratified sample is checked by hand as verification, not as a tie-break.
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
