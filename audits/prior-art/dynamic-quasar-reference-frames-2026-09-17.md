---
type: "Audit Report"
title: "Dynamic Quasar Reference Frames prior-art audit — 2026-09-17"
description: "Claim-specific prior-art audit of the DQRF dynamic-gauge compression hypothesis, with a GitHub-derived cutoff and explicit separation of antecedents from later work."
tags: [semantic-atlas, dqrf, prior-art, dynamical-systems, shared-dynamics, semantic-reference-frame, compression]
timestamp: 2026-09-17T14:59:00-04:00
---

# Dynamic Quasar Reference Frames prior-art audit — 2026-09-17

> **Status:** first reproducible prior-art audit for the current central claim of `dynamic_quasar_reference_frames.md`. It narrows the novelty boundary; it does not establish patent novelty, exhaustive literature coverage, or causal dependence between projects.

## 1. Audited claim and claim-specific cutoff

The current central DQRF claim is narrower than the paper's original proposal to attach canonical vector fields to semantic quasars. The claim audited here is:

> A frozen external dynamic gauge, selected without access to evaluation-model transition fields, may make multiple models' transition fields cheaper to describe, compare, and transfer by fitting only a preregistered low-capacity amplitude and measuring the complexity of the remaining model-specific residual.

Operationally, the paper writes

\[
F_M(q)=a_M(q)\mathcal V_Q(q)+r_M(q)
\]

and makes the **Dynamic Gauge Compression Test (DGCT)** foundational: a candidate gauge must reduce a preregistered vector of held-out residual-complexity quantities such as residual energy, effective rank, sample complexity, OOD stability and cross-model residual concordance, while the gauge family and geometry remain frozen before evaluation.

The paper itself first became public in commit [`438c118817ce6cf5dd276b98a514d2e837b2b6d9`](https://github.com/franklinbaldo/papers/commit/438c118817ce6cf5dd276b98a514d2e837b2b6d9) at **2026-09-09 00:53:22 UTC**. That version proposed dynamic/vortical semantic reference fields, but did not yet make residual-complexity redistribution the primary claim.

The present central claim was introduced in the next public commit, [`70b382726b11ef4eced8ce1fa6b31bf734e63fdc`](https://github.com/franklinbaldo/papers/commit/70b382726b11ef4eced8ce1fa6b31bf734e63fdc), **2026-09-09 01:26:01 UTC**, whose commit message is `research: make dynamic gauge compression the primary DQRF claim`. Its diff introduces the frozen-gauge decomposition, the residual-complexity framing and DGCT as the foundational experiment.

**Claim-specific cutoff: 2026-09-09 01:26:01 UTC.** Material first made public after that instant is not prior art against this audited claim.

## 2. Search protocol

This round searched the exact composition and its components under older terminology. Representative queries included:

- `"semantic reference frame" language model dynamics`
- `semantic trajectories reference frame language model`
- `shared dynamics multiple systems common coordinate system`
- `shared latent dynamics cross system transfer`
- `vector field shared component subject specific deviation`
- `mixed effect ODE shared vector field subject deviation`
- `coordinate system simplify dynamics sparsity basis`
- `dynamical systems residual shared component individual component`
- `Koopman multiple systems shared representation transfer`
- `cross-session shared latent dynamical system alignment`
- `minimum description length dynamical system reconstruction`
- `frozen reference vector field residual complexity`
- `dynamic gauge embeddings language models`

Sources checked included arXiv, PNAS, Nature/Communications Physics, bioRxiv, Physical Review E and public GitHub/repository search. Candidate dates were checked against primary preprint or publisher records where available. Searches also decomposed the claim so that older work need not use the words “gauge”, “quasar” or “Semantic Atlas”.

## 3. Findings before our cutoff

### 3.1 Choosing coordinates/bases to make dynamics simpler is established prior art

**Classification:** `prior_art` for the generic simplification-by-representation principle; not prior art for the full DQRF composition.

Brunton, Proctor & Kutz, **“Discovering governing equations from data by sparse identification of nonlinear dynamical systems”** (SINDy), was published online by PNAS on **2016-03-28**. SINDy explicitly depends on finding measurement coordinates and a function basis in which dynamics become sparse, and treats sparsity/accuracy as diagnostic evidence about the representation. It therefore directly precedes the generic proposition that dynamical complexity can be redistributed by a useful representation without creating new information.

- <https://doi.org/10.1073/pnas.1517384113>

Earlier normal-form and coordinate-transform traditions are broader historical antecedents to the same generic principle. DQRF should not frame “a representation can expose simpler dynamics” itself as novel.

**Difference from DQRF:** SINDy searches for a sparse governing representation of the observed system. It does not supply an externally frozen vector field shared across independently calibrated language-model observers, nor the DGCT freeze boundary and residual-complexity comparison.

### 3.2 Shared latent dynamics between different systems predates DQRF

**Classification:** `partial_prior_art`.

Kim, Xie & van de Panne, **“Learning to Correspond Dynamical Systems”**, arXiv:1912.03015, first posted **2019-12-06**, learns a shared latent state space and a shared latent dynamics model for pairs of distinct dynamical systems, together with system-specific encoders/decoders. The learned correspondence supports simulation of one system through the counterpart and shared latent dynamics.

- <https://arxiv.org/abs/1912.03015>

This anticipates an important component of DQRF: different systems can become more directly comparable and transferable after placement in a common dynamical representation.

**Difference from DQRF:** the common representation and latent dynamics are learned jointly from the systems being related; they are not an evaluation-independent external gauge, and the scientific endpoint is correspondence/bisimulation rather than whether a frozen ruler reduces model-specific residual complexity.

### 3.3 Multi-system Koopman modeling already exploited shared structure for sample-efficient transfer

**Classification:** strong `partial_prior_art` for shared representation, system-specific dynamics and transfer.

Elul et al., **“Data-driven modeling of interrelated dynamical systems”**, *Communications Physics* 7, 141, published **2024-05-01**, learns a common transformation into a joint coordinate system while retaining individual linear dynamics operators. Its MIDST construction ties shared components across systems and demonstrates adaptation to a new system with substantially fewer new samples; the paper also evaluates effective rank of the learned dynamics.

- <https://doi.org/10.1038/s42005-024-01626-5>

This is close to DQRF's programme-level motivation that related systems may share a representation in which system-specific dynamics become cheaper to learn and transfer.

**Difference from DQRF:** MIDST learns the shared representation and shared operator factors from the systems themselves. DQRF's distinctive methodological constraint is that the candidate reference field is selected and frozen without evaluation-model transition fields, after which only a low-capacity amplitude may be fitted before residual complexity is measured.

### 3.4 Cross-subject neural work established preserved shared latent dynamics

**Classification:** `adjacent_prior_work` / `partial_prior_art` for aligned shared dynamics and held-out transfer.

Safaie et al., **“Preserved neural population dynamics across animals performing similar behaviour”**, bioRxiv `2022.09.26.509498`, first posted **2022-09-26**, reported behaviorally relevant latent neural dynamics preserved across animals and cross-individual decoding after alignment.

- <https://www.biorxiv.org/content/10.1101/2022.09.26.509498v1>

A later methodological development, **CANDY — “Extracting task-relevant preserved dynamics from contrastive aligned neural recordings”**, bioRxiv `2025.11.11.686428`, first posted in **2025-11**, aligns recordings from different sessions/subjects into a shared latent embedding and fits a shared linear dynamical system. It reports generalization of the learned dynamics to held-out sessions/subjects.

- <https://www.biorxiv.org/content/10.1101/2025.11.11.686428v1>

These works make clear that “aligned observers can expose preserved dynamics and enable transfer” was already an active empirical programme before the DQRF cutoff.

**Difference from DQRF:** the shared dynamics are inferred from the observations and, in CANDY, trained jointly with the alignment. They do not use an externally specified reference flow as a frozen metrological object.

### 3.5 A shared vector field plus subject-specific deviations predates DQRF very closely

**Classification:** strong `partial_prior_art`.

Martinelli et al., **“Bayesian Nonparametric Mixed-Effect ODEs with Gaussian Processes” (MEGPODE)**, arXiv:2605.13088, first posted **2026-05-13 06:57:01 UTC**, models related continuous-time systems by decomposing each subject's vector field into a **shared population component plus a subject-specific deviation**, with Gaussian-process priors on both.

- <https://arxiv.org/abs/2605.13088>

This is the closest structural antecedent located for the algebraic shape of DQRF's

\[
F_M = \text{shared/reference component} + \text{model-specific residual}.
\]

It materially narrows any novelty claim based simply on factoring a family of vector fields into common structure and individual residuals.

**Difference from DQRF:** MEGPODE learns the population component from the subjects jointly. DQRF instead asks whether a field fixed independently of evaluation-model dynamics can function as a ruler, with a low-capacity amplitude and preregistered residual-complexity tests. The external-freeze requirement remains a substantive distinction.

### 3.6 A semantic reference frame with trajectories and compressibility was public before DQRF

**Classification:** strong `partial_prior_art`, and the closest domain-specific antecedent located in this round.

Gu, Aleti, Chen & Zhang, **“SemRF: A Semantic Reference Frame for Residual-Stream Dynamics in Language Models”**, arXiv:2606.32022, first posted **2026-06-30 17:52:22 UTC**, predates the DQRF cutoff by more than two months. SemRF fixes semantic anchors, measures residual-stream states against them, turns depthwise computation into a semantic trajectory, defines a canonical minimum-action trace, and explicitly relates low curvature to piecewise-linear **compressibility** / lower trajectory complexity.

- <https://arxiv.org/abs/2606.32022>

This means that several domain-specific ingredients were already public before DQRF:

1. a named **semantic reference frame** built from fixed anchors;
2. semantic trajectories measured inside that frame;
3. trajectory/action/curvature quantities;
4. an explicit connection between the chosen frame/trajectory representation and compressibility/complexity.

No reference to SemRF or arXiv:2606.32022 was located in the current `franklinbaldo/papers` tree during this audit.

**Difference from DQRF:** SemRF's frame is static and tied to residual-stream depth within a model. It does not attach an externally frozen **dynamic vector field** to the anchors, does not decompose multiple models as `a_M V_Q + r_M`, and does not use the DGCT cross-model residual-complexity battery. It is therefore not an anticipation of the exact DQRF mechanism, but it is too close to omit from future Related Work.

### 3.7 MDL-based dynamical reconstruction is older adjacent work

**Classification:** `adjacent_prior_work`.

Molkov et al., **“Using the minimum description length principle for global reconstruction of dynamic systems from noisy time series”**, *Physical Review E* 80, 046207, published **2009-10-15**, uses minimum description length to choose model size and embedding dimension for dynamical-system reconstruction.

- <https://doi.org/10.1103/PhysRevE.80.046207>

This does not anticipate DQRF's shared gauge, but it prevents treating description-length or complexity-based selection of dynamical representations as a new ingredient.

## 4. Novelty boundary after this round

The broad components of DQRF are substantially less novel than the paper name can initially suggest:

- representation/coordinate choices that simplify dynamics are established (`prior_art`);
- shared latent dynamics across systems are established (`partial_prior_art`);
- shared representations/components can improve transfer and sample efficiency across systems (`partial_prior_art`);
- shared vector field + unit-specific deviation is established (`partial_prior_art`);
- semantic reference frames, semantic trajectories and trajectory compressibility existed in language-model work before our cutoff (`partial_prior_art`).

This round **did not locate** a pre-2026-09-09 01:26:01 UTC source combining all of the following:

1. a semantic/common state frame for multiple model observers;
2. a **dynamic vector field chosen and frozen independently of evaluation-model transition fields**;
3. only a preregistered low-capacity per-model amplitude fitted against that field;
4. model-specific residuals evaluated for complexity rather than merely prediction accuracy;
5. a matched battery including residual energy/effective rank/sample complexity/OOD stability/cross-model residual concordance;
6. complexity-matched alternative field families used to test whether the chosen external gauge is genuinely useful.

That exact composition remains **unresolved by this search**, not established as novel. A negative search is not proof that no antecedent exists.

The most defensible scientific framing after this audit is therefore that DQRF proposes a stringent **external-freeze metrology experiment** combining established ideas, rather than that it invents shared dynamics, semantic reference frames, residual decomposition, or dynamical compression individually.

## 5. Work after our cutoff

Targeted searches for material made public after **2026-09-09 01:26:01 UTC** used `semantic reference frame`, `shared dynamics language models`, `dynamic gauge embeddings` and `frozen vector field semantics`, including recent-result searches through 2026-09-17.

No post-cutoff work located in this round was close enough to the exact DQRF composition to justify `later_independent`, `later_overlap`, `later_non_citing`, `later_citing` or `later_derivative` classification.

This is only a negative search result. If a later source appears, chronology and citation status should be recorded separately from any claim about causal dependence.

## 6. Consequence for the paper's Related Work and novelty language

A future paper revision should explicitly position DQRF against at least four distinct antecedent families instead of only steering/vector-field analogies:

1. **sparsifying coordinates / system identification** — SINDy and normal-form traditions;
2. **shared multi-system dynamics** — learned correspondence and MIDST-style shared representations;
3. **mixed-effect vector fields** — MEGPODE's shared population field plus subject-specific deviation;
4. **semantic reference frames** — SemRF's fixed anchors, semantic trajectories and compressibility.

A cautious summary sentence supported by this audit would be:

> Coordinate choices that simplify dynamics, shared latent dynamics across related systems, common-plus-individual vector-field decompositions, and semantic reference frames for language-model trajectories all predate DQRF. The narrower hypothesis tested here is whether an **externally frozen dynamic gauge**, chosen without evaluation-model transition data, can lower preregistered held-out residual-complexity measures across independently calibrated model observers better than matched alternative fields.

## 7. Next search frontier

The highest-value next searches are now narrower than generic dynamical-systems literature:

1. gauge-equivariant / moving-frame methods that use a **fixed external vector field** rather than learned shared dynamics;
2. Koopman and transfer-learning papers that explicitly decompose operators/fields into common + task-specific residuals under a frozen shared component;
3. language-model interpretability work using cross-model common semantic coordinates **and** temporal/depth dynamics;
4. MDL/minimum-action work comparing candidate reference dynamics by held-out residual description length;
5. repositories/preprints between June and September 2026 that may use “semantic frame”, “semantic flow”, “latent flow”, “dynamics prior”, or “common flow field” without DQRF terminology.
