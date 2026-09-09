---
type: "Technical Paper"
title: "Dynamic Quasar Reference Frames: Vortical Gauges for the Semantic Atlas"
description: "Follow-up Semantic Atlas position paper proposing dynamic quasar reference frames in which artificial quasars anchor not only positions but canonical multiscale vector fields, enabling trajectory-relative coordinates, flow-aware reachability, and matched tests against the static simplex SRF."
tags: [semantic-atlas, quasar, dynamic-reference-frame, vector-fields, vortices, dynamical-systems, steering, reachability, control, embeddings]
timestamp: 2026-09-08T20:40:00-04:00
---

# Dynamic Quasar Reference Frames: Vortical Gauges for the Semantic Atlas

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Follow-up position paper and experimental proposal.** This manuscript does not replace the static Semantic Reference Frame (SRF) proposed in *Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models*. It asks whether the reference frame itself should contain a canonical dynamics in addition to canonical landmarks. The proposal is deliberately stronger than a visualization metaphor and weaker than a claim that semantic dynamics obey fluid mechanics. Unless explicitly stated otherwise, all performance claims are hypotheses to be tested against the existing static-SRF baseline.

## Abstract

The Semantic Atlas programme represents language-model behavior as trajectories in a calibrated semantic state space. Its current Semantic Reference Frame uses artificial **semantic quasars** arranged as a regular simplex to define an external geometry, while paired calibration data and orthogonal Procrustes determine semantic orientation across models. This cleanly separates artificial metrology from empirical semantics, but leaves one structural asymmetry: the atlas is explicitly dynamic, whereas the reference geometry is static. Position, velocity, curvature, reachability, transition dynamics, and control cost are estimated in a coordinate system whose landmarks provide no preferred local motion.

This paper proposes a **Dynamic Quasar Reference Frame (DQRF)**. Each quasar is augmented by a canonical vector field, and the collection of quasars defines a smooth, externally specified flow over the calibrated semantic space. The first candidate family is vortical: not because language is assumed to satisfy Navier--Stokes, but because vortices provide mathematically controlled notions of radial motion, circulation, phase, chirality, shear, separatrices, scale, and multiscale self-similarity. A semantic trajectory can then be described relative to both landmark position and local reference flow. Instead of asking only *where is the state relative to the quasars?*, the DQRF also asks *how is the observed semantic motion aligned with, opposed to, crossing, or orbiting the reference flow?*

The proposal preserves the original calibration contract. A vortical field cannot determine semantic identity: rotating the entire field leaves its artificial dynamics intact. Paired calibration remains responsible for semantic orientation; the DQRF adds **dynamic metrology**, not semantics by fiat. We define dynamic quasar coordinates, flow-relative navigation cost, corridor and barrier observables, multiscale reference fields, and compatibility with the manifold-aware Semantic Atlas. We distinguish the proposal from Steering Vector Fields and energy-landscape steering: those methods learn or apply state-dependent control policies, whereas the DQRF is a canonical observation and navigation gauge in which learned dynamics and controls can be compared.

The paper pre-registers a sequence of matched experiments comparing the existing simplex SRF against smooth vortical DQRFs at equal canonical dimension and calibration data. The extension survives only if it improves held-out trajectory prediction, reachability prediction, route-cost estimation, cross-model transfer, or steering efficiency beyond complexity-matched static and random-field controls. The strongest version additionally predicts that a Navier--Stokes-inspired self-similar vortical family can provide a useful **multiscale reference flow**, but the proposal does not depend on singularities: smooth truncated vortices are the first scientific baseline.

**Keywords:** semantic atlas, semantic quasars, dynamic reference frames, vector fields, vortices, representation geometry, semantic trajectories, reachability, activation steering, dynamical systems, multiscale representations

---

## 1. Scope: make the gauge dynamic, not the semantics fluid

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

The SRF supplies a calibrated global coordinate system. Artificial quasars define a fixed reference geometry; shared row-paired calibration data determine how each observer is oriented inside that geometry. The Atlas then estimates model-relative density, competence, transition dynamics, reachability, intervention cost, uncertainty, and a potential-like escape quantity called semantic gravity.

The proposal in this paper changes only one interface:

```text
static artificial landmarks
            ↓
canonical landmarks + canonical reference flow
```

The replacement is intentionally conservative. The DQRF does **not** assert that:

1. language-model activations are a physical fluid;
2. semantic density is mass density;
3. semantic gravity is gravitational potential;
4. semantic trajectories satisfy Navier--Stokes;
5. a finite-time fluid singularity has a semantic analogue;
6. vortices are intrinsically better than every other vector-field family.

It proposes a narrower hypothesis:

> **A canonical dynamic field may be a better metrological object for semantic trajectories than canonical points alone.**

The scientific question is therefore comparative. If a DQRF provides no held-out advantage over the existing static SRF after matching dimension, calibration information, parameter count, and downstream model capacity, it should be rejected without weakening the broader Semantic Atlas programme.

## 2. The static-frame asymmetry

### 2.1 The Atlas already treats semantic state as dynamic

The original paper explicitly argues that position is not a complete state. A minimal dynamic state has the schematic form

\[
z_t=(q_t,v_t,\kappa_t,\sigma_t),
\]

where \(q_t\) is canonical position, \(v_t\) semantic velocity, \(\kappa_t\) curvature or turning information, and \(\sigma_t\) scale and uncertainty. Reachability is likewise dynamical:

\[
R_M(q,H,B)=\{y:\exists\Gamma:q\rightarrow y,\ C_M(\Gamma)\le B\}.
\]

The navigation distance

\[
d_M^{nav}(a,b)=\min_{\Gamma:a\rightarrow b} C_M(\Gamma)
\]

is generally directed and model-relative. Corridors and barriers are defined through trajectories and costs, not Euclidean proximity alone.

Yet the quasars against which those dynamics are expressed are static points. For a canonical semantic state \(q\), the basic quasar observation is a family of similarities or distances to landmarks. That is sufficient to locate the state but says nothing about preferred local motion.

### 2.2 Equal distance need not mean equal dynamic relation

Suppose two semantic states \(q_a\) and \(q_b\) are at the same distance from a quasar \(Q_i\):

\[
\|q_a-Q_i\|=\|q_b-Q_i\|.
\]

Under a static radial description, they can be equivalent up to angle. But two trajectories crossing those points may have very different dynamic relations:

- one moves toward the quasar;
- one moves away;
- one circles clockwise;
- one circles counterclockwise;
- one follows a local corridor;
- one crosses the corridor transversely;
- one enters a high-shear transition zone;
- one remains on a slowly varying streamline.

These differences can be estimated from empirical trajectory history. The DQRF asks whether they become easier to express, compare, and transfer if the reference system itself contains a canonical field.

### 2.3 Why not simply learn the field from data?

The Atlas already estimates model-specific transition dynamics \(F_M(q)\). A natural objection is therefore: why introduce an artificial vector field at all?

For the same reason the original paper introduced artificial quasars instead of treating one model's native coordinates as universal. A **reference field** and an **empirical field** serve different roles.

Let

\[
\mathcal V_Q(q)
\]

be the canonical reference field and

\[
F_M(q)
\]

be the model's measured transition field. Then quantities such as

\[
\langle F_M(q),\mathcal V_Q(q)\rangle
\]

become model observations expressed against a fixed external gauge. Multiple models can be compared by asking how their measured flows relate to the same reference dynamics, just as their positions are compared in the same calibrated SRF.

The artificial field must therefore remain frozen when evaluating observers. Learning \(\mathcal V_Q\) separately for each model would collapse the distinction between ruler and object being measured.

## 3. Dynamic quasars

### 3.1 From a landmark to a landmark-plus-field

A static quasar is a canonical point

\[
Q_i=q_i.
\]

A dynamic quasar is instead

\[
Q_i=(q_i,\mathcal V_i,\Theta_i),
\]

where:

- \(q_i\in\mathbb R^k\) is the canonical landmark;
- \(\mathcal V_i:\mathbb R^k\rightarrow\mathbb R^k\) is a smooth reference vector field associated with it;
- \(\Theta_i\) contains frozen field parameters such as orientation plane, chirality, radial scale, decay, and multiscale schedule.

The global reference field may be a weighted superposition

\[
\mathcal V_Q(q)=\sum_i w_i(q)\mathcal V_i(q)
\]

with smooth partition weights \(w_i(q)\), or a separately constructed field constrained by the quasar geometry.

The first implementation should avoid singularities and discontinuous patch boundaries. Smoothness is a property of the measuring instrument, not a metaphysical claim about semantics.

### 3.2 A simple vortical baseline

In a two-dimensional canonical plane associated with quasar \(i\), let

\[
r=q-q_i.
\]

Choose an antisymmetric generator \(J_i\) on that plane and a smooth radial envelope \(g_i(\|r\|)\). A minimal vortical field is

\[
\mathcal V_i(q)=\omega_i g_i(\|r\|)J_i r.
\]

For example,

\[
g_i(r)=\exp(-r^2/2s_i^2)
\]

gives a smooth localized swirl. The sign of \(\omega_i\) determines chirality and \(s_i\) the characteristic scale.

This field already adds information unavailable from the landmark alone:

- orbital phase;
- clockwise/counterclockwise orientation;
- tangent direction;
- local circulation scale;
- radial versus tangential decomposition of observed motion.

It is also deliberately boring. If a simple smooth vortex cannot improve any measured Atlas objective, there is little reason to begin with a complicated Navier--Stokes construction.

### 3.3 Higher-dimensional construction

A canonical dimension \(k>2\) does not admit one unique notion of rotation. We therefore define a frozen set of orthogonal two-planes or antisymmetric generators

\[
J_{i,1},\ldots,J_{i,m},
\]

and compose them:

\[
\mathcal V_i(q)=\sum_{a=1}^m \omega_{i,a}g_{i,a}(\|P_{i,a}r\|)J_{i,a}P_{i,a}r,
\]

where \(P_{i,a}\) projects into the chosen plane.

The plane assignments are part of the external gauge. They must be deterministic from the quasar configuration or frozen once from the reference observer; they must not be refit to maximize each evaluation model's score.

A redundant quasar code can provide more planes than a minimal simplex. This yields a family of dynamic reference channels while preserving the original idea that the external geometry is known exactly.

## 4. Dynamic quasar coordinates

Let \(q_t\) be canonical position and \(v_t=q_{t+1}-q_t\) observed semantic displacement. For quasar \(i\), define the local radial unit direction

\[
\hat r_i=\frac{q_t-q_i}{\|q_t-q_i\|},
\]

and, where defined, the normalized reference-flow direction

\[
\hat f_i=\frac{\mathcal V_i(q_t)}{\|\mathcal V_i(q_t)\|}.
\]

A dynamic coordinate block can contain

\[
C_i(q_t,v_t)=
\left[
 d_i,
 c_i,
 v_t\cdot\hat r_i,
 v_t\cdot\hat f_i,
 \|v_t\|,
 \alpha_i,
 s_i,
 \chi_i
\right],
\]

where:

- \(d_i=\|q_t-q_i\|\) is distance;
- \(c_i\) is the original static quasar similarity;
- \(v_t\cdot\hat r_i\) is radial semantic velocity;
- \(v_t\cdot\hat f_i\) is flow alignment;
- \(\alpha_i\) is a local phase or angle in the active vortex plane;
- \(s_i\) records the reference scale with strongest response;
- \(\chi_i\) records chirality-sensitive alignment.

Additional candidate observables include:

\[
\text{cross-flow ratio}
=
\frac{\|v_t-(v_t\cdot\hat f_i)\hat f_i\|}{\|v_t\|+\epsilon},
\]

local reference shear

\[
S_Q(q)=\frac12\left(\nabla\mathcal V_Q+\nabla\mathcal V_Q^T\right),
\]

and vorticity-like antisymmetric part

\[
W_Q(q)=\frac12\left(\nabla\mathcal V_Q-\nabla\mathcal V_Q^T\right).
\]

These are features of the artificial field, not measurements of literal fluid shear or vorticity in the model.

## 5. Flow-aware reachability and semantic navigation

### 5.1 Separate drift from intervention

Suppose observed semantic dynamics under a controller can be approximated locally as

\[
\dot q=F_M(q)+G_M(q)u.
\]

The static Atlas measures the cost of choosing \(u\) to reach a target. The DQRF introduces a reference decomposition

\[
F_M(q)=a_M(q)\mathcal V_Q(q)+r_M(q),
\]

where \(a_M(q)\) is local alignment and \(r_M(q)\) the residual relative to the reference flow.

This permits questions such as:

- does successful generation preferentially follow the reference flow?
- are low-cost routes more aligned with it than failed routes?
- does the residual \(r_M\) transfer better across models than raw native velocity?
- do high-cost transitions coincide with strong cross-flow motion?

The field is useful only if these questions predict held-out behavior better than matched static or random-field features.

### 5.2 Corridors, barriers, and separatrices

The existing Atlas uses corridor and barrier language operationally. A DQRF gives those concepts additional dynamic observables.

A **flow-aligned corridor candidate** is a region \(B\) where observed successful trajectories satisfy

\[
\mathbb E[\cos(v_t,\mathcal V_Q(q_t))\mid q_t\in B]\gg0.
\]

A **cross-flow barrier candidate** is a boundary across which successful transitions require unusually large residual motion or intervention.

A **separatrix candidate** is a surface of the reference field whose sides predict different empirical destination basins.

None of these definitions is accepted merely because the field has the corresponding mathematical structure. The reference separatrix matters only if it aligns with reproducible differences in the model's measured dynamics.

### 5.3 Navigation distance in a moving frame

A flow-relative cost can be written schematically as

\[
C_Q(\Gamma)=
\int_\Gamma
\left[
\lambda_\parallel c_\parallel(q,\dot q)
+
\lambda_\perp c_\perp(q,\dot q)
+
\lambda_u\|u\|^2
\right]dt,
\]

where the first two terms distinguish movement along and across the canonical field.

The important scientific test is not whether this cost looks physically elegant. It is whether

\[
d_{M,Q}^{nav}(a,b)=\min_\Gamma C_Q(\Gamma)
\]

better predicts empirical intervention cost, latency, rollout count, or task success than the original cost model.

## 6. Why vortices are an interesting reference family

A generic vector field would satisfy the formal proposal. Vortices are interesting because they contribute several structures at once.

### 6.1 Chirality

A static simplex has no intrinsic clockwise/counterclockwise distinction. A vortex does. Chirality can break otherwise equivalent directional descriptions without assigning semantic labels to axes.

### 6.2 Phase

Two states at equal radius can have different orbital phase. Phase offers a compact coordinate for cyclic or recurrent semantic dynamics.

### 6.3 Radial/tangential decomposition

Observed motion can be decomposed into attraction/escape and circulation. This may be useful for distinguishing transitions that approach a conceptual basin from transitions that elaborate within it.

### 6.4 Shear and local deformation

A non-uniform vortex contains regions in which neighboring reference trajectories separate or rotate at different rates. These regions provide fixed probes for asking whether empirical semantic trajectories also display predictable changes in curvature, branching, or control cost.

### 6.5 Natural multiscale families

Vortices admit radial scale parameters and self-similar rescalings. This makes them natural candidates for the multiresolution constraint already present in the Atlas.

These are reasons to test vortices, not reasons to privilege them in advance. Gradient fields, Hamiltonian flows, learned normal forms, and random divergence-free fields are required comparison families.

## 7. Navier--Stokes as inspiration, not ontology

### 7.1 What the 2026 blow-up result contributes

The September 2026 OpenAI construction of finite-time Navier--Stokes blow-up provides a newly explicit family of anisotropic, multiscale vortical dynamics with characteristic shrinking spatial scales and increasing local velocity/gradient scales. The accompanying Lean repository formalizes the existence claims for forced three-dimensional Navier--Stokes and unforced Euler.

The Semantic Atlas proposal does **not** require the full singular construction. Its relevance is methodological: it demonstrates that a compactly specified vortical architecture can organize motion across a hierarchy of scales in a mathematically exact way.

A DQRF can borrow a truncated self-similar schedule such as

\[
\ell_r(\tau)\propto \tau^{1/2},
\qquad
\ell_z(\tau)\propto \tau^{1/2-h},
\]

while stopping at a finite minimum scale

\[
\tau\ge \tau_{min}>0.
\]

No semantic coordinate is allowed to diverge. The singular endpoint is neither needed nor desirable as a reference instrument.

### 7.2 A scale-indexed reference flow

Let \(s\in\{s_0,\ldots,s_L\}\) index reference scales. Define

\[
\mathcal V_Q(q;s)
\]

as a family of geometrically related fields. A trajectory can then be represented by the scale at which its local displacement is most coherent with the reference dynamics:

\[
s^*(q_t,v_t)=
\arg\max_s
\cos\left(v_t,\mathcal V_Q(q_t;s)\right).
\]

This supplies a dynamic analogue of the Atlas's multiresolution charts. The question becomes not merely *where is the state?* but *at what scale does its motion admit the simplest local description?*

### 7.3 The stronger hypothesis

The strongest DQRF claim is:

> A self-similar vortical reference family yields a compact scale coordinate that improves semantic trajectory prediction and cross-model transfer beyond independently parameterized multiscale static features.

This is highly falsifiable. If a bank of ordinary radial basis functions, random smooth fields, or learned local PCA directions performs equally well with the same degrees of freedom, the Navier--Stokes-inspired structure adds no evidence-bearing value.

## 8. Relation to Steering Vector Fields and energy-landscape steering

Recent steering work makes the distinction between **static direction** and **state-dependent field** empirically important.

Li, Li, and Huang (2026) propose **Steering Vector Fields (SVF)**. A differentiable concept-scoring function produces a local gradient, so the steering direction depends on the current activation rather than applying one global vector everywhere. Their results support the proposition that context-dependent local directions can outperform fixed vectors.

Jiang et al. (2026) propose **Energy Landscape Steering (ELS)**. An external energy-based model assigns high energy to undesirable activation states and low energy to desired states; inference-time gradients steer the hidden state toward lower-energy regions.

These are neighboring but distinct objects from the DQRF:

| Object | Learned from behavior? | Primary role | Model-specific? |
|---|---:|---|---:|
| Static quasar SRF | calibration only | position metrology | calibration map yes, geometry no |
| DQRF | calibration only for placement | dynamic metrology / navigation gauge | calibration map yes, field no |
| SVF | yes | state-dependent control direction | yes |
| ELS | yes | objective landscape + control gradient | yes |
| Atlas transition field \(F_M\) | yes | empirical model dynamics | yes |

The DQRF should therefore be tested as a **common coordinate system for comparing** SVF, ELS, natural model dynamics, and Semantic Servo interventions. A positive result would not show that the DQRF controls the model by itself. It would show that flow-relative coordinates make those controls easier to predict, compare, or transfer.

## 9. Compatibility with concept manifolds

The manifold-aware Semantic Atlas argues that local semantic objects may be low-dimensional manifolds rather than points. The DQRF is compatible with that extension.

Let \(\mathcal M_g\) be a local concept manifold with tangent space \(T_q\mathcal M_g\). Project the canonical field into the tangent space:

\[
\mathcal V_{Q,g}(q)=P_{T_q\mathcal M_g}\mathcal V_Q(q).
\]

This yields two new observables:

1. **tangent alignment** -- whether a reference flow follows locally supported semantic variation;
2. **normal pressure** -- the size of the component that points away from the manifold.

Define

\[
A_{tan}(q)=
\frac{\|P_T\mathcal V_Q(q)\|}{\|\mathcal V_Q(q)\|+\epsilon},
\]

and

\[
A_{norm}(q)=
\frac{\|(I-P_T)\mathcal V_Q(q)\|}{\|\mathcal V_Q(q)\|+\epsilon}.
\]

If low-cost semantic trajectories preferentially occur where the canonical field is tangent to recovered concept manifolds, DQRF structure may be useful for route planning. If tangent alignment is no better than random-field controls, the apparent geometric correspondence is decorative.

A more ambitious future formulation could treat the DQRF as a vector field defined on the atlas manifold itself rather than in the ambient SRF. That requires reliable manifold recovery first and is therefore not part of the initial experiment.

## 10. Experimental programme

### 10.1 Experiment DQRF-0: synthetic sanity check

Construct synthetic trajectories in known vector fields and pass them through unknown orthogonal transformations and anisotropic observation maps. Compare:

1. raw coordinates;
2. static simplex SRF;
3. DQRF after the same paired calibration.

Success requires recovery of held-out flow-relative observables after calibration. This is primarily an implementation test.

### 10.2 Experiment DQRF-1: observational prediction

Reuse the frozen corpora and observer models from Semantic Atlas Experiment A where possible.

For each trajectory step, build features under:

- **S0:** existing static SRF coordinates;
- **S1:** S0 + finite differences \((v,\kappa)\);
- **V0:** S1 + one smooth vortical DQRF;
- **V1:** S1 + multiscale vortical DQRF;
- **R0:** S1 + complexity-matched random smooth divergence-free fields;
- **G0:** S1 + complexity-matched gradient fields.

Fit the same downstream predictor class and evaluate held-out:

- next canonical displacement;
- turning angle;
- destination cell/manifold;
- transition probability;
- trajectory continuation error.

The primary result is not raw performance but **incremental predictive value** of V0/V1 over S1, R0, and G0.

### 10.3 Experiment DQRF-2: reachability prediction

Sample source-target pairs \((a,b)\), horizon \(H\), and steering budget \(B\). Empirically estimate whether \(b\) is reachable from \(a\) under a frozen intervention family.

Compare models predicting reachability from:

- static atlas observables;
- static + empirical local velocity;
- static + DQRF observables;
- static + random-field observables.

Primary metrics:

- AUROC / AUPRC for reachability;
- calibration error;
- rank correlation with measured minimal intervention cost;
- cross-model transfer degradation.

### 10.4 Experiment DQRF-3: steering cost

Use rollout selection or activation steering to reach predefined semantic targets. Do not let the DQRF controller have more intervention budget than baselines.

Compare planners using:

- Euclidean/SRF shortest routes;
- empirical graph shortest routes;
- flow-relative DQRF routes;
- random-field routes;
- learned local field routes.

Measure:

\[
\text{success},\quad
\text{intervention norm},\quad
\text{rollouts},\quad
\text{tokens},\quad
\text{off-support distance},\quad
\text{semantic path length}.
\]

A DQRF win must survive normalization for planner complexity and route-search compute.

### 10.5 Experiment DQRF-4: cross-model dynamic transfer

Fit all semantic calibration maps independently using the same paired calibration rows, as in the existing SRF contract. Freeze the DQRF itself globally.

Ask whether a route description expressed in flow-relative coordinates transfers better across observers than a route expressed only in static canonical positions.

For models \(M_1,M_2\), compare the disagreement of corresponding held-out trajectories in:

\[
(q_t,v_t)
\]

versus

\[
C_Q(q_t,v_t).
\]

A positive result requires improvement on held-out paired items and trajectories, not just training correspondences.

## 11. Negative controls and falsifiers

The DQRF proposal should be considered unsupported if any of the following survive adequate statistical power.

### F1 -- static sufficiency

Static SRF + ordinary velocity/curvature features matches or beats DQRF on all held-out dynamic tasks.

### F2 -- random-field equivalence

Random smooth fields of matched dimension and spectral complexity perform as well as the vortical field.

### F3 -- parameter-count explanation

Any advantage disappears after matching downstream feature count, predictor capacity, and hyperparameter search budget.

### F4 -- calibration leakage

The advantage appears only on calibration items and collapses on held-out paired states.

### F5 -- no transfer

DQRF coordinates improve one observer but do not preserve corresponding dynamics across independently calibrated models.

### F6 -- learned field dominates trivially

A small learned local vector field strongly outperforms the frozen DQRF with no transfer or regularization advantage for the latter. In that case the correct Atlas primitive may simply be empirical local dynamics.

### F7 -- vortex specificity fails

Gradient, Hamiltonian, radial-basis, or random divergence-free fields match vortical DQRF performance. Then the general dynamic-gauge hypothesis may survive while the vortex hypothesis fails.

### F8 -- self-similar scale adds nothing

The Navier--Stokes-inspired multiscale schedule does not outperform an independently tuned scale bank.

### F9 -- control metric mismatch

Flow-relative route cost does not correlate with measured intervention cost or success.

### F10 -- manifold incompatibility

On recovered concept manifolds, DQRF tangent/normal observables do not predict natural transitions, steering quality, or off-support risk.

The strongest scientific outcome may therefore be a partial rejection: for example, dynamic fields may help but vortices may not; vortices may help but self-similar scaling may not; or the entire DQRF may reduce to redundant features already captured by the Atlas.

## 12. Implementation sketch

The current experimental code contains a `QuasarFrame` with:

- `quasars` -- regular-simplex landmarks;
- `WhiteningTransform`;
- orthogonal calibration rotation;
- canonical-vector and quasar-coordinate methods.

A minimal extension should preserve that class and add a sibling object rather than mutate the existing baseline:

```python
@dataclass(frozen=True)
class DynamicQuasarFrame:
    static: QuasarFrame
    field_spec: FrozenFieldSpec

    def canonical_vectors(self, embeddings): ...
    def field(self, canonical_vectors, scale=None): ...
    def dynamic_coordinates(self, embeddings_t, embeddings_t1): ...
```

`FrozenFieldSpec` should contain only deterministic or pre-registered artificial parameters. It must serialize into experiment artifacts so that every reported trajectory can be reproduced against exactly the same field.

The first implementation should include four field families:

```text
vortex_smooth
random_divergence_free
radial_gradient
generic_antisymmetric
```

and only later add:

```text
vortex_self_similar_truncated
```

This ordering prevents the 2026 Navier--Stokes result from becoming an aesthetic commitment before the simpler dynamic-gauge claim is tested.

## 13. What would a successful result mean?

A positive DQRF result would **not** mean that language has been shown to be fluid-like. It would establish something more modest and potentially more useful:

1. a fixed artificial dynamic gauge contains reusable information for describing model trajectories;
2. flow-relative coordinates compress or predict semantic motion better than static coordinates alone;
3. some dynamic observables transfer across independently calibrated models;
4. route cost measured relative to that gauge predicts intervention cost or reachability;
5. a vortical or multiscale structure is a useful engineering basis for this metrology.

The conceptual payoff would be that the semantic quasar becomes more than a star-like landmark. It becomes a **dynamic beacon**: a reference object with a known local flow against which an unknown model's motion can be measured.

The original SRF asks:

\[
\boxed{\text{Where is the semantic state?}}
\]

The DQRF adds:

\[
\boxed{\text{How is it moving relative to a common dynamical gauge?}}
\]

The Atlas can then keep its model-specific empirical dynamics while gaining a canonical language for comparing those dynamics.

## 14. Conclusion

The Semantic Atlas already treats text generation as navigation through a dynamic semantic state space. Its current quasars solve a metrological problem for position: artificial landmarks define an external geometry and paired calibration determines semantic orientation. This paper proposes extending the same philosophy from **points to flows**.

A Dynamic Quasar Reference Frame augments canonical landmarks with frozen vector fields. Vortices are the first candidate because they supply phase, chirality, radial/tangential decomposition, shear, separatrices, and multiscale structure in one compact mathematical object. The recent Navier--Stokes blow-up construction motivates a stronger self-similar multiscale family, but the experimental programme begins with smooth bounded vortices and does not require singular behavior.

The proposal preserves the most important epistemic boundary of the Semantic Atlas: artificial geometry does not create semantic identity. Calibration still performs semantic anchoring. The field provides a ruler for motion, not a theory of meaning.

The central falsifiable question is therefore simple:

\[
\boxed{
\text{Does a frozen dynamic quasar gauge improve our ability to predict,}\
\text{compare, navigate, or control semantic trajectories?}
}
\]

If not, the static SRF remains the cleaner design. If yes, semantic quasars should no longer be treated merely as fixed stars in an artificial sky. They can become the sources of a common navigational flow.

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
