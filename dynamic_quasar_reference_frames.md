---
type: "Technical Paper"
title: "Dynamic Quasar Reference Frames: Vortical Gauges for the Semantic Atlas"
description: "Follow-up Semantic Atlas position paper proposing frozen dynamic gauges whose primary test is whether they compress, compare, and transfer model dynamics more simply than isolated model-specific transition fields; vortices are one candidate family and Navier--Stokes-inspired scaling is a terminal hypothesis, not a privileged destination."
tags: [semantic-atlas, quasar, dynamic-reference-frame, vector-fields, vortices, dynamical-systems, steering, reachability, control, embeddings, compression, mdl]
timestamp: 2026-09-08T21:28:00-04:00
---

# Dynamic Quasar Reference Frames: Vortical Gauges for the Semantic Atlas

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Follow-up position paper and experimental proposal.** This manuscript does not replace the static Semantic Reference Frame (SRF) proposed in *Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models*. It asks whether a frozen external dynamics can make model-specific semantic dynamics simpler to represent, compare, and transfer. The proposal is a metrological hypothesis, not a claim that language obeys fluid mechanics. Unless explicitly marked otherwise, all performance claims are hypotheses to be tested against matched static, random-field, gradient-field, and learned-field baselines.

## Abstract

The Semantic Atlas programme represents language-model behavior as trajectories in a calibrated semantic state space. Its existing Semantic Reference Frame (SRF) uses artificial semantic quasars to define a fixed external geometry while paired calibration and orthogonal Procrustes determine cross-model semantic orientation. The Atlas then estimates model-specific transition dynamics, reachability, intervention cost, and trajectory structure. This paper asks whether an external reference frame can do for **dynamics** what the SRF already attempts to do for **position**.

We propose **Dynamic Quasar Reference Frames (DQRFs)**: frozen canonical vector fields attached to or constructed from the quasar geometry. The primary claim is not that flow-relative features contain information unavailable in position and velocity. A deterministic coordinate change cannot create information. The claim is instead representational:

> **A frozen external dynamic gauge may allow the transition fields of multiple language models to be represented, compared, and transferred with lower descriptive complexity and better out-of-distribution generalization than estimating each model-specific field in isolation.**

For model \(M\), let \(F_M(q)\) denote its empirical semantic transition field in the calibrated SRF. Given a frozen candidate gauge \(\mathcal V_Q(q)\), we study decompositions

\[
F_M(q)=a_M(q)\mathcal V_Q(q)+r_M(q),
\]

where \(a_M\) belongs to a preregistered low-capacity function class and \(r_M\) is the residual. A useful gauge should not merely increase predictive \(R^2\). It should make \(r_M\) measurably simpler: lower residual energy, lower effective rank, lower sample complexity at fixed prediction error, greater local/OOD stability, and stronger cross-model residual concordance on held-out paired states. We call this the **Dynamic Gauge Compression Test (DGCT)** and make it the foundational experiment of the proposal.

Vortical fields are one candidate family because they provide phase, chirality, radial/tangential decomposition, shear, separatrices, and natural multiscale structure in a compact object. They receive no a priori privilege. Smooth vortices must beat complexity-matched random divergence-free, gradient, generic antisymmetric, and learned local fields. A Navier--Stokes-inspired self-similar hierarchy is tested only as the last and most extravagant nested hypothesis. If an ordinary vortex already compresses dynamics well, the Navier--Stokes construction is unnecessary; if only the Navier--Stokes-inspired family succeeds, that result becomes independently interesting.

The programme preserves a strict epistemic firewall. Gauge geometry and all field hyperparameters must be frozen without access to evaluation-model transition fields. Paired calibration may place observations into the common SRF, but no information from \(F_M\) may influence gauge selection, planes, scales, chirality, or field family on the evaluation split. Downstream reachability, steering-cost, and control experiments are treated as consequences of a successful compression result rather than the primary justification for DQRF.

**Keywords:** semantic atlas, semantic quasars, dynamic reference frames, vector fields, representation compression, semantic trajectories, reachability, activation steering, vortices, minimum description length, cross-model transfer

---

## 1. Scope and central claim

The original Semantic Atlas separates five layers:

```text
language model / embedding model
            ↓
   Semantic Reference Frame
            ↓
       Semantic Atlas
            ↓
        route planner
            ↓
       Semantic Servo
            ↓
       lexical generation
```

The SRF supplies a calibrated global coordinate system. Artificial quasars define external geometry; shared row-paired calibration data determine how each observer is placed in that geometry. The Atlas then estimates model-relative density, competence, transition dynamics, reachability, intervention cost, uncertainty, and semantic gravity.

The DQRF changes only the metrological interface:

```text
static artificial landmarks
            ↓
canonical landmarks + frozen reference dynamics
```

It does **not** assert that:

1. language-model activations are a physical fluid;
2. semantic density is mass density;
3. semantic gravity is gravitational potential;
4. semantic trajectories satisfy Navier--Stokes;
5. a fluid singularity has a semantic analogue;
6. vortices are intrinsically superior to other vector fields;
7. a coordinate transform creates new information.

The central claim is deliberately colder:

> **A field of reference that is external, frozen, and shared across observers can be scientifically useful if it redistributes dynamical complexity: model-specific transition fields should become simpler residuals in the common gauge, and those residuals should generalize or transfer better than the un-gauged dynamics.**

This is analogous to using polar rather than Cartesian coordinates for rotationally structured motion. The information is equivalent in principle, but one representation can expose regularity that is expensive to describe in another.

Let \(\Phi_Q\) denote the deterministic transformation induced by a DQRF. The scientific target is therefore not

\[
I(\Phi_Q(q,v);Y)>I((q,v);Y),
\]

which would be impossible for a deterministic lossless transformation without additional information. Instead we ask whether, under matched model classes and finite data,

\[
\mathcal C(F_M\mid \Phi_Q) < \mathcal C(F_M),
\]

for operational measures \(\mathcal C\) defined before evaluation.

### 1.1 Why this matters for the Semantic Atlas

The broader Semantic Atlas already depends on a compression hypothesis: semantic dynamics useful for planning should admit a lower-resolution description than complete token-level or hidden-state dynamics. If no such compression exists, an atlas eventually approaches a map at 1:1 scale.

DQRF therefore becomes a direct test of that programme-level assumption. A successful gauge would demonstrate that at least part of model dynamics can be factored into

\[
\text{shared reference structure} + \text{simpler model-specific residual}.
\]

The most important positive result would be stronger than a small improvement in next-step prediction. It would be evidence that

\[
F_A(q)=a_A(q)\mathcal V_Q(q)+r_A(q),
\]

\[
F_B(q)=a_B(q)\mathcal V_Q(q)+r_B(q),
\]

\[
F_C(q)=a_C(q)\mathcal V_Q(q)+r_C(q),
\]

with residuals that are both simpler than the original fields and structurally more alike across independently calibrated models.

### 1.2 Coordinate utility without information creation

A coordinate system can be useful even when it is invertible and therefore information-neutral. The right question is whether relevant regularities become cheaper to describe or learn.

A DQRF earns scientific value only if at least one of the following improves under strictly matched conditions:

- description length;
- effective dimensionality;
- number of samples required to achieve a fixed prediction error;
- stability under perturbation or distribution shift;
- cross-model transfer;
- planner or controller complexity needed for a fixed outcome.

Raw predictive accuracy remains useful, but it is downstream evidence rather than the core claim.

## 2. Static-frame asymmetry and the gauge distinction

### 2.1 Semantic state is already dynamic

The original paper argues that position alone is not a complete state. A minimal semantic state can be written schematically as

\[
z_t=(q_t,v_t,\kappa_t,\sigma_t),
\]

where \(q_t\) is canonical position, \(v_t\) semantic velocity, \(\kappa_t\) curvature, and \(\sigma_t\) scale and uncertainty.

The Atlas also defines model-relative reachability and navigation cost:

\[
R_M(q,H,B)=\{y:\exists\Gamma:q\rightarrow y,\ C_M(\Gamma)\le B\},
\]

\[
d_M^{nav}(a,b)=\min_{\Gamma:a\rightarrow b} C_M(\Gamma).
\]

The atlas is therefore dynamic even when its reference landmarks are not.

### 2.2 Why not simply learn \(F_M\)?

Because an empirical transition field and a reference field answer different questions.

Let

\[
F_M(q)
\]

be measured from model \(M\), while

\[
\mathcal V_Q(q)
\]

is fixed independently of the evaluation-model dynamics. The empirical field describes the object; the canonical field supplies a ruler for motion.

The decomposition

\[
F_M(q)=a_M(q)\mathcal V_Q(q)+r_M(q)
\]

is interesting only if the frozen ruler exposes common structure. If a separate \(\mathcal V_M\) is learned for every model, then the central shared-gauge hypothesis has disappeared. Learned fields remain important baselines, but they test a different proposition: whether local dynamics are useful, not whether a common external dynamics is useful.

## 3. Dynamic quasars

A static quasar is a point

\[
Q_i=q_i.
\]

A dynamic quasar is

\[
Q_i=(q_i,\mathcal V_i,\Theta_i),
\]

where \(\mathcal V_i\) is a smooth field and \(\Theta_i\) contains fully frozen construction parameters.

The global field can be a smooth superposition

\[
\mathcal V_Q(q)=\sum_i w_i(q)\mathcal V_i(q)
\]

or another deterministic construction tied to the quasar geometry.

### 3.1 Simple vortical baseline

In a two-dimensional canonical plane associated with quasar \(i\), define \(r=q-q_i\), an antisymmetric generator \(J_i\), and smooth radial envelope \(g_i\). A minimal vortex is

\[
\mathcal V_i(q)=\omega_i g_i(\|r\|)J_i r,
\]

with, for example,

\[
g_i(r)=\exp(-r^2/2s_i^2).
\]

This yields phase, chirality, tangential direction, radial/tangential decomposition, and a local circulation scale without singular behavior.

### 3.2 Higher-dimensional fields

For canonical dimension \(k>2\), use frozen two-planes or antisymmetric generators

\[
J_{i,1},\ldots,J_{i,m},
\]

and

\[
\mathcal V_i(q)=\sum_{a=1}^m \omega_{i,a}g_{i,a}(\|P_{i,a}r\|)J_{i,a}P_{i,a}r.
\]

The plane assignments, scales, signs, envelopes, and combination rule must be derived deterministically from public preregistered seeds and quasar geometry. They must never be tuned against evaluation-model trajectory data.

## 4. Dynamic coordinates

Given canonical position \(q_t\) and semantic displacement \(v_t=q_{t+1}-q_t\), a dynamic quasar coordinate block may include

\[
C_i(q_t,v_t)=
[d_i,c_i,v_t\cdot\hat r_i,v_t\cdot\hat f_i,\|v_t\|,\alpha_i,s_i,\chi_i],
\]

where \(d_i\) is distance, \(c_i\) static similarity, \(\hat r_i\) radial direction, \(\hat f_i\) normalized reference-flow direction, \(\alpha_i\) phase, \(s_i\) scale, and \(\chi_i\) chirality-sensitive alignment.

Candidate derived observables include cross-flow ratio,

\[
X(q_t,v_t)=
\frac{\|v_t-(v_t\cdot\hat f_i)\hat f_i\|}{\|v_t\|+\epsilon},
\]

reference strain,

\[
S_Q(q)=\frac12(\nabla\mathcal V_Q+\nabla\mathcal V_Q^T),
\]

and antisymmetric rotation,

\[
W_Q(q)=\frac12(\nabla\mathcal V_Q-\nabla\mathcal V_Q^T).
\]

These are properties of the measuring field. They are not claims of literal fluid shear or vorticity in the model.

## 5. Dynamic Gauge Compression Test

The **Dynamic Gauge Compression Test (DGCT)** is the foundational experiment. Downstream steering and reachability experiments are secondary until a gauge shows evidence of compression.

### 5.1 Candidate fields

Let the preregistered candidate set be

\[
\mathfrak V=
\{0,\mathcal V_{rand-div},\mathcal V_{grad},\mathcal V_{anti},\mathcal V_{vortex},\mathcal V_{multi},\mathcal V_{NS}\}.
\]

Here \(0\) is the no-field baseline; the other members denote random divergence-free, gradient, generic antisymmetric, smooth vortex, generic multiscale vortex, and finally truncated Navier--Stokes-inspired fields.

A learned local field \(\widehat F_M\) is included as a non-canonical upper baseline, but it is not eligible to establish the shared-gauge claim because it is model-specific.

### 5.2 Fit only a low-capacity amplitude

For each model \(M\) and frozen field \(\mathcal V^{(k)}\), fit

\[
a_M^{(k)}=\arg\min_{a\in\mathcal A}
\mathbb E_{q\sim D_{train}}
\|F_M(q)-a(q)\mathcal V^{(k)}(q)\|^2,
\]

where \(\mathcal A\) is a preregistered low-capacity function family shared across all candidate fields. The first experiment should use a scalar constant and a small linear/RBF alternative as separate preregistered conditions, not an unrestricted neural network.

Define

\[
r_M^{(k)}(q)=F_M(q)-a_M^{(k)}(q)\mathcal V^{(k)}(q).
\]

The gauge itself remains frozen. Only the amplitude function \(a_M^{(k)}\) is fitted to model data.

### 5.3 Complexity is a vector, not a convenient scalar

There is no unique representation-independent scalar called "complexity." The primary DGCT therefore reports a preregistered vector of operational quantities rather than collapsing them into a tunable weighted score.

#### Residual energy

\[
E_r^{(k)}=
\frac{\mathbb E\|r_M^{(k)}(q)\|^2}
{\mathbb E\|F_M(q)\|^2}.
\]

Lower is better. The reciprocal

\[
G_E^{(k)}=1/E_r^{(k)}
\]

is an energy-compression factor, but it is not by itself sufficient evidence.

#### Effective residual rank

Let \(\lambda_j\) be eigenvalues of the held-out residual covariance and

\[
p_j=\frac{\lambda_j}{\sum_l\lambda_l}.
\]

Define entropy effective rank

\[
r_{eff}=\exp\left(-\sum_j p_j\log p_j\right).
\]

A useful gauge should reduce \(r_{eff}\) relative to the no-field and matched random-field baselines.

#### Predictive sample complexity

For a frozen predictor family \(\mathcal H\), define

\[
N_\varepsilon(r)=
\min\{n:\mathbb E[L(\hat r_n(q),r(q))]\le\varepsilon\},
\]

estimated from preregistered learning curves. Lower \(N_\varepsilon\) means the residual is easier to learn at a fixed target error.

#### Local and OOD stability

For perturbations \(\delta\) drawn from preregistered in-support and OOD perturbation distributions, estimate

\[
S_\delta(r)=
\mathbb E
\frac{\|r(q+\delta)-r(q)\|^2}{\|\delta\|^2+\epsilon}.
\]

This is an operational local-sensitivity measure, not a proof of a Lipschitz constant. A useful gauge should reduce sensitivity or improve held-out prediction under controlled distribution shifts.

#### Cross-model residual concordance

For independently calibrated models \(A\) and \(B\), fit residual Procrustes only on a training correspondence set and evaluate held-out paired states. Report residual cosine agreement, Procrustes RMSE, neighborhood preservation, and optionally linear CKA.

The strongest result is not merely small \(r_M\), but

\[
r_A^{(k)}\approx r_B^{(k)}\approx r_C^{(k)}
\]

on held-out correspondences under a fixed gauge.

### 5.4 Optional MDL summary

A two-part minimum-description-length score may be reported only after fixing the coder and model class before looking at results:

\[
L_k = L(a_M^{(k)}) + L(r_M^{(k)}\mid \mathcal H).
\]

Because MDL values depend on coding choices, this is a secondary synthesis measure. It must not replace the primary complexity vector or be tuned post hoc.

### 5.5 Decision rule

A candidate dynamic gauge earns support only if it beats the no-field/static-derivative baseline and complexity-matched artificial-field controls on preregistered primary metrics across multiple models.

A vortex-specific claim requires

\[
\mathcal V_{vortex}
\]

to outperform random divergence-free and generic antisymmetric fields.

A Navier--Stokes-specific claim requires

\[
\mathcal V_{NS}
\]

to outperform ordinary smooth and generic multiscale vortices. Otherwise the Navier--Stokes structure has no evidence-bearing role.

## 6. Auditably frozen gauge construction

The shared-gauge claim is invalid if evaluation-model dynamics leak into gauge construction. The protocol should therefore be intentionally strict.

### 6.1 Freeze order

The complete `FrozenFieldSpec` must be committed or content-addressed **before** evaluation trajectories are exposed to the experiment that tests that field.

It includes:

- field family;
- canonical dimension;
- quasar configuration;
- plane assignments;
- chirality/sign choices;
- scale bank;
- radial envelopes;
- random seeds;
- superposition weights;
- truncation parameters;
- normalization rules.

### 6.2 Allowed and forbidden information

Allowed before freeze:

- canonical dimension chosen by the parent Semantic Atlas protocol;
- quasar geometry;
- public deterministic seeds;
- synthetic sanity-check data generated independently of evaluation models;
- calibration *procedure*.

Forbidden before or during gauge selection:

- evaluation-model \(F_M\);
- evaluation trajectory directions;
- held-out reachability or steering outcomes;
- model-specific local PCA planes chosen to improve gauge alignment;
- scale or chirality choices optimized against evaluation performance.

Paired semantic calibration is performed after the gauge is frozen to place each observer into the shared SRF. Calibration rows can orient the observer in the gauge; they cannot redesign the gauge.

### 6.3 Artifact requirement

Every DGCT result must preserve:

```text
field_spec_hash
field_family
all field parameters
seed
calibration split ids
trajectory train/validation/test ids
amplitude-model specification
residual-predictor specification
metric definitions
```

A result without a reproducible frozen field specification does not count as evidence for the shared-gauge claim.

## 7. Why test vortices?

A generic dynamic field is sufficient for the general DQRF hypothesis. Vortices are merely an economical candidate basis.

They provide:

- chirality;
- phase;
- radial/tangential decomposition;
- circulation;
- shear and local deformation;
- separatrix-like structure;
- natural scale parameters.

These properties could make some semantic dynamics easier to describe. They could also be decorative. Gradient fields, Hamiltonian-like or antisymmetric fields, radial bases, and random divergence-free fields are mandatory controls.

The hierarchy of claims is therefore

\[
\boxed{
\text{dynamic gauge}
\supset
\text{vortical gauge}
\supset
\text{self-similar vortical gauge}
\supset
\text{Navier--Stokes-inspired gauge}
}.
\]

Failure of a stronger member does not falsify weaker members. Success of a weaker member does not license claims about stronger members.

## 8. Navier--Stokes as terminal hypothesis

The September 2026 OpenAI finite-time Navier--Stokes construction supplies one mathematically explicit anisotropic, multiscale vortical hierarchy. That is enough to make it a candidate field family. It does not make it a privileged one.

A truncated candidate may borrow scale laws such as

\[
\ell_r(\tau)\propto\tau^{1/2},
\qquad
\ell_z(\tau)\propto\tau^{1/2-h},
\]

with

\[
\tau\ge\tau_{min}>0.
\]

No semantic coordinate diverges; no singular endpoint is required.

The test order is intentionally hostile to narrative seduction:

1. no field / static derivatives;
2. random and generic smooth fields;
3. smooth vortex;
4. generic multiscale vortex;
5. only then Navier--Stokes-inspired truncated scaling.

If the smooth vortex already achieves the same compression, the Navier--Stokes construction is historically interesting but scientifically unnecessary here. If only the Navier--Stokes-inspired field produces a robust, cross-model compression advantage, then its specific hierarchy becomes evidence-bearing and merits deeper investigation.

## 9. Reachability and navigation as downstream consequences

Only after a candidate field passes a meaningful DGCT should it be promoted into route planning.

Suppose controlled dynamics are approximated as

\[
\dot q=F_M(q)+G_M(q)u.
\]

A flow-aware route cost can distinguish along-flow, cross-flow, and intervention components:

\[
C_Q(\Gamma)=
\int_\Gamma
[\lambda_\parallel c_\parallel+
\lambda_\perp c_\perp+
\lambda_u\|u\|^2]dt.
\]

The empirical question is whether this predicts measured intervention cost, rollout count, latency, task success, or token count better than static and empirical-graph baselines.

Corridors, barriers, and separatrices remain operational concepts. A reference-field separatrix matters only when its sides predict reproducible differences in empirical destination or control cost.

## 10. Relation to Steering Vector Fields and energy-landscape steering

Recent work already supports state-dependent control.

Li, Li, and Huang (2026) propose **Steering Vector Fields (SVF)**, where local steering direction depends on current activation. Jiang et al. (2026) propose **Energy Landscape Steering (ELS)**, in which inference-time gradients move activations through a learned energy landscape.

The distinction is:

| Object | Learned from model behavior? | Primary role | Shared across models? |
|---|---:|---|---:|
| Static SRF | calibration only | position metrology | geometry yes |
| DQRF | no, after preregistered construction | dynamic metrology / compression gauge | field yes |
| SVF | yes | state-dependent control | generally no |
| ELS | yes | learned objective + control gradient | generally no |
| \(F_M\) | yes | empirical model dynamics | no |

DQRF should therefore be judged primarily by whether it makes those model-specific objects easier to describe or transfer, not by pretending to replace them.

## 11. Compatibility with concept manifolds

Let \(\mathcal M_g\) be a recovered local concept manifold with tangent space \(T_q\mathcal M_g\). Project the field:

\[
\mathcal V_{Q,g}(q)=P_{T_q\mathcal M_g}\mathcal V_Q(q).
\]

Define tangent and normal fractions

\[
A_{tan}(q)=
\frac{\|P_T\mathcal V_Q(q)\|}{\|\mathcal V_Q(q)\|+\epsilon},
\]

\[
A_{norm}(q)=
\frac{\|(I-P_T)\mathcal V_Q(q)\|}{\|\mathcal V_Q(q)\|+\epsilon}.
\]

A useful gauge may make residual dynamics simpler particularly where the field lies near the semantic support. This must be tested against random-field tangent alignment. Visual correspondence alone is not evidence.

## 12. Experimental programme

### 12.1 DQRF-0A: synthetic calibration sanity check

Generate trajectories from known fields, apply unknown rotations/reflections and anisotropic observation transforms, calibrate observers into the SRF, and verify recovery of flow-relative observables on held-out synthetic states.

This is an implementation test, not evidence about language models.

### 12.2 DQRF-0B: Dynamic Gauge Compression Test

This is the first model-backed scientific experiment.

For each observer model and each frozen field family:

1. estimate \(F_M\) using the same trajectory estimator;
2. fit the same low-capacity amplitude family \(a_M^{(k)}\);
3. compute held-out residuals \(r_M^{(k)}\);
4. report residual energy, effective rank, learning curves, OOD sensitivity, and cross-model concordance;
5. compare against no-field, static-derivative, random-field, gradient, generic antisymmetric, and learned-field baselines.

The primary question is:

\[
\boxed{
\text{Does one frozen shared gauge make multiple }F_M
\text{ materially simpler and more mutually comparable?}
}
\]

### 12.3 DQRF-1: observational prediction

Only after DQRF-0B, compare matched predictors using:

- **S0:** static SRF;
- **S1:** S0 + velocity/curvature;
- **D0:** S1 + best preregistered general dynamic gauge;
- **V0:** S1 + smooth vortex;
- **V1:** S1 + generic multiscale vortex;
- **NS0:** S1 + truncated NS-inspired field;
- **R0/G0:** complexity-matched random/gradient controls.

Evaluate next displacement, turning angle, destination region, and trajectory continuation error. Prediction is secondary to compression: a larger predictor must not be allowed to masquerade as a better gauge.

### 12.4 DQRF-2: cross-model transfer

Freeze the gauge globally and fit semantic calibration maps independently. Ask whether a residual predictor or route description trained on one observer requires less adaptation on another when expressed in the DQRF than in static coordinates.

Report zero-shot and few-shot transfer curves, not only within-model accuracy.

### 12.5 DQRF-3: reachability

Estimate empirical reachability for source-target pairs under a frozen intervention family and compare whether DQRF residual/cost observables improve AUROC/AUPRC, calibration, and rank correlation with measured minimal intervention cost.

### 12.6 DQRF-4: steering cost

Compare Euclidean/SRF, empirical-graph, DQRF, random-field, and learned-field planners under matched intervention and route-search budgets. Measure success, intervention norm, rollouts, tokens, off-support distance, and path length.

## 13. Falsifiers

The proposal is structured as nested hypotheses rather than one all-or-nothing claim.

### F1 -- no compression

No frozen dynamic gauge materially reduces residual energy, effective rank, sample complexity, OOD sensitivity, or description length relative to static derivatives.

**Consequence:** reject the general DQRF claim.

### F2 -- random-field equivalence

Random smooth fields of matched dimension and spectral complexity compress just as well.

**Consequence:** a generic feature-map effect may exist, but there is no evidence for the proposed field structure.

### F3 -- capacity explanation

Advantages disappear after matching amplitude-model, predictor, feature count, hyperparameter budget, and training data.

**Consequence:** reject the claimed representational gain.

### F4 -- gauge leakage

Performance depends on choosing field planes, scales, chirality, or seeds after inspecting evaluation-model dynamics.

**Consequence:** result does not count as evidence for an external gauge.

### F5 -- no cross-model simplification

Residuals become smaller within each observer but are not more concordant or transferable across observers.

**Consequence:** at most a within-model coordinate convenience is supported, not a shared dynamic reference frame.

### F6 -- learned field dominates without regularization/transfer benefit

A small model-specific learned field achieves substantially better compression and generalization, while the frozen gauge has no transfer or sample-efficiency advantage.

**Consequence:** prefer empirical local dynamics.

### F7 -- vortex specificity fails

Gradient, random divergence-free, or generic antisymmetric fields match the vortex.

**Consequence:** the general dynamic-gauge hypothesis may survive; the vortex hypothesis does not.

### F8 -- multiscale specificity fails

A generic multiscale bank matches the self-similar vortex.

**Consequence:** no evidence for self-similar structure.

### F9 -- Navier--Stokes specificity fails

The NS-inspired schedule matches but does not exceed ordinary smooth or generic multiscale vortices.

**Consequence:** NS is a historical inspiration only.

### F10 -- downstream mismatch

Compression improves but reachability, transfer, or steering cost do not.

**Consequence:** DQRF may remain a descriptive representation, but navigation claims must be narrowed.

### F11 -- manifold incompatibility

Tangent/normal DQRF observables do not predict natural transitions or residual simplification better than random controls.

**Consequence:** do not integrate DQRF with manifold routing.

## 14. Implementation sketch

Preserve the existing `QuasarFrame` baseline and add a sibling object:

```python
@dataclass(frozen=True)
class DynamicQuasarFrame:
    static: QuasarFrame
    field_spec: FrozenFieldSpec

    def canonical_vectors(self, embeddings): ...
    def field(self, canonical_vectors, scale=None): ...
    def dynamic_coordinates(self, embeddings_t, embeddings_t1): ...
    def decompose(self, q, empirical_velocity, amplitude_model): ...
```

The first implementation should support:

```text
zero
vortex_smooth
random_divergence_free
radial_gradient
generic_antisymmetric
vortex_multiscale_generic
```

Only after those results are frozen should it add:

```text
vortex_self_similar_ns_truncated
```

`FrozenFieldSpec` must serialize all parameters and expose a content hash included in every experiment artifact.

## 15. What would count as success?

A positive result would **not** show that semantic dynamics are fluid dynamics. It would show that a frozen artificial dynamic gauge exposes reusable regularity.

The strongest evidence would have the following shape:

\[
\mathcal C(F_M) > \mathcal C(r_M\mid\mathcal V_Q)
\]

for several operational complexity measures and multiple independently calibrated models, while simultaneously

\[
r_A\approx r_B\approx r_C
\]

on held-out paired states more strongly than the corresponding raw transition fields.

In that case the quasar is no longer useful merely as a fixed landmark. It becomes a **dynamic beacon**: a known external flow against which unknown model dynamics become simpler to describe.

The original SRF asks

\[
\boxed{\text{Where is the semantic state?}}
\]

The DQRF adds

\[
\boxed{\text{In what common dynamic gauge is its motion simplest?}}
\]

That is the scientific claim this paper asks the experiments to earn.

## 16. Conclusion

The Semantic Atlas assumes that useful semantic dynamics admit a compressed navigational description. Dynamic Quasar Reference Frames turn that assumption into a direct metrological test.

The proposal does not need vortices, self-similarity, or Navier--Stokes to survive. It needs one thing: a field frozen independently of evaluation-model dynamics that makes several model-specific transition fields cheaper to describe, easier to learn, more stable out of distribution, or more transferable across observers than the appropriate matched baselines.

Vortices are one compact family worth testing. Navier--Stokes-inspired self-similarity is the final nested hypothesis and receives no aesthetic exemption from comparison.

The central falsifiable question is therefore:

\[
\boxed{
\text{Can a shared frozen dynamic gauge turn complex model-specific semantic}\
\text{dynamics into simpler, transferable residuals?}
}
\]

If not, the static SRF remains the cleaner design. If yes, the DQRF would provide something the Semantic Atlas currently lacks: not new semantic information, but a common coordinate system in which the dynamics already present become compressible.

---

## References

Achara, S., et al. (2026). Work on shared multi-model representation spaces using Generalized Procrustes Analysis. Cited and scoped in the original *Semantic Atlas* literature review.

Jiang, E. H., Ou, W., Liu, R., Pang, S., Wan, G., Duan, R., Dong, W., Chang, K.-W., Wang, X., Wu, Y. N., & Li, X. (2026). **Mitigating Over-Refusal in Aligned Large Language Models via Inference-Time Activation Energy.** *Proceedings of ACL 2026*, 37930--37950. DOI: 10.18653/v1/2026.acl-long.1759. https://aclanthology.org/2026.acl-long.1759/

Li, J., Li, Y., & Huang, K.-H. (2026). **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models.** arXiv:2602.01654. https://arxiv.org/abs/2602.01654

Maystre, L., et al. (2025). Work on orthogonal Procrustes alignment for embedding interoperability. Cited and scoped in the original *Semantic Atlas* literature review.

OpenAI (2026). **Finite time blowup for Navier--Stokes.** Research announcement and accompanying manuscript, September 8, 2026. https://openai.com/index/navier-stokes-solution/

OpenAI (2026). **NavierStokesAndEuler: Lean certificates accompanying Navier--Stokes and Euler results.** https://github.com/openai/NavierStokesAndEuler

Baldo, F. (2026). **Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models.** `semantic_atlas.md`, this repository.

Baldo, F. (2026). **From Semantic Points to Concept Manifolds: A Manifold-Aware Extension of the Semantic Atlas.** `semantic_atlas_manifolds.md`, this repository.
