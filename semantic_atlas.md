---
type: "Technical Paper"
title: "Semantic Atlas: Shared Coordinate Frames, Model-Specific Dynamics, and Closed-Loop Navigation"
description: "Position paper proposing a model-indexed semantic atlas over a shared operational coordinate frame, with transition dynamics, control cost, reachability, and cross-model transfer as the central empirical objects."
tags: [semantic-atlas, semantic-dynamics, reachability, control, navigation, embeddings, representation-alignment, efficient-inference]
timestamp: 2026-08-26T02:45:00Z
---

# Semantic Atlas: Shared Coordinate Frames, Model-Specific Dynamics, and Closed-Loop Navigation

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme.** This revision deliberately narrows the claim. It does **not** assume that language or embedding models inhabit one observer-independent Euclidean semantic universe, that stronger models see a common map at higher resolution, or that successful representational alignment implies shared behavior. A common coordinate frame is treated as an operational gauge for comparing trajectories. The scientific object of the Atlas is the **model-specific dynamics defined over that gauge**: transitions, control cost, reachability, navigation distance, and uncertainty. Unless a section explicitly reports a completed experiment, all claims are hypotheses and design targets.

## Abstract

Modern representation-alignment work makes it increasingly plausible that embeddings from different models can be placed into interoperable coordinate systems. `vec2vec` can translate between independently trained text-embedding spaces through a learned common latent representation; multi-way alignment can place several observers in one reference space; and calibrated analyses suggest that local neighborhood relations may be more reproducible than one global metric geometry. These developments weaken, rather than strengthen, the need for a Semantic Atlas to claim a new universal semantic coordinate system. **Universal geometry, if it exists, is only the coordinate layer of an Atlas—not the Atlas itself.**

This paper therefore defines a Semantic Atlas as a **family of model-indexed dynamical maps expressed in a chosen common frame**. A trajectory is represented by semantic position and history; repeated trajectories estimate a model-specific transition field \(F_M\), intervention cost \(C_M\), reachable set \(R_M\), directed navigation distance \(d_M^{nav}\), uncertainty \(\Omega_M\), and optional density or competence fields. A shared coordinate \(q\) does not imply shared dynamics:

\[
T_A(E_A(x))\approx T_B(E_B(x))
\quad\not\Rightarrow\quad
F_A(q)=F_B(q),\; C_A(q,u)=C_B(q,u),\; R_A(q,H,B)=R_B(q,H,B).
\]

This distinction produces the paper's main empirical question: **how much model-specific semantic dynamics transfers after static coordinate alignment?** We propose leave-one-model-out experiments in which a common frame and dynamical prior are learned from source models, then evaluated on a held-out target model before and after observing \(k\) target trajectories. A sample-equivalence statistic \(k^*_{Atlas}\) measures how many target trajectories a transferred atlas is worth relative to fitting target dynamics from scratch. Static alignment can succeed while dynamical transfer fails; that negative result would itself establish an important boundary on universal-representation claims.

The downstream engineering programme remains control-theoretic. A route planner searches the learned directed cost landscape, semantic Model Predictive Control tests whether planned routes improve goal attainment, and a Semantic Servo attempts closed-loop hidden-state control after causal calibration. Weight-space compilation remains a later efficiency hypothesis, not a foundation. The Atlas succeeds only if its dynamics improve prediction, planning, or sample efficiency beyond static geometry, nearest-neighbor, prompting, and target-only baselines.

**Keywords:** semantic trajectories, representation alignment, dynamical systems, reachability, optimal control, semantic navigation, model predictive control, transfer learning, efficient inference

---

## 1. The revised question

A language model exposes learned structure through an autoregressive interface. Even when a destination is conceptually simple, reaching it can require many token-level transitions. This motivates a coarse-grained question: can long-range semantic motion be represented, predicted, and controlled at a level above individual lexical choices?

Earlier versions of the Semantic Atlas mixed this question with a second, much stronger idea: that independently trained models might be progressively clearer observers of one common semantic map. Subsequent analysis makes that hierarchy unnecessary and poorly motivated. Modern alignment results already occupy much of the static-geometry territory, while the strongest calibrated convergence evidence is local rather than globally metric. More importantly, even perfect coordinate interoperability would not imply identical transition dynamics.

The revised paper therefore asks:

1. Can generated discourse be represented as a trajectory whose recent semantic history predicts future semantic motion beyond endpoint similarity?
2. Can a chosen common frame make trajectories from different models comparable without claiming that the frame is ontologically privileged?
3. Does each model induce reproducible transition, cost, and reachability structure in that frame?
4. How much of those **dynamics**, rather than merely the coordinates, transfers to a held-out model?
5. Can a planner use the estimated dynamics to improve goal attainment under a budget?
6. Can closed-loop control realize planned motion with lower intervention or rollout cost than open-loop steering?
7. Can useful parts of the dynamics eventually be compiled from weights or sparse measurements rather than rediscovered by exhaustive rollout?

The central object is no longer one universal atlas \(A\). It is a shared coordinate layer plus a family of model-specific atlases:

\[
\mathfrak A
=
\left(
\mathcal Q,
\{A_M\}_{M\in\mathcal M}
\right),
\]

where \(\mathcal Q\) is a chosen comparison frame and \(A_M\) describes the dynamics of model \(M\) in that frame.

This reframing is load-bearing. **The map is not the coordinate system.** The coordinate system merely lets us write several maps on comparable paper.

---

## 2. Semantic trajectories as dynamical observations

### 2.1 From text to a path

Let a generated sequence be

\[
x_1,x_2,\ldots,x_n.
\]

A semantic observer maps a prefix or contextual unit to a representation. For causal navigation, let

\[
e_t=E(x_{\le t})
\]

or use a registered chunk-level embedding of the text generated up to time \(t\). A frame map \(T_M\) places the representation in a common coordinate system:

\[
q_t=T_M(e_t)\in\mathcal Q.
\]

The sequence

\[
\gamma_M=(q_0,q_1,\ldots,q_T)
\]

is a semantic trajectory of model \(M\) under a registered prompting and decoding protocol.

This is an observational construction. It does not imply that \(q_t\) is the model's internal computational state or that semantic dynamics are literally Euclidean.

### 2.2 Position is not a Markov state by assumption

A point \(q_t\) can be reached with different histories. Define local displacement

\[
v_t=q_t-q_{t-1}
\]

and, where useful, a turning or curvature statistic \(\kappa_t\). A compressed state may be

\[
z_t=(q_t,v_t,\kappa_t,h_t,\sigma_t),
\]

where \(h_t\) is a finite registered history summary and \(\sigma_t\) records scale or uncertainty.

The empirical problem is to find the smallest state summary that predicts future semantic motion adequately. We must compare any proposed compressed state against:

- endpoint-only \(q_t\);
- fixed recent windows of embeddings;
- native hidden-state baselines where accessible;
- simple lexical/context statistics;
- larger black-box sequence predictors.

If trajectory history adds no held-out predictive value, the dynamical Atlas should not be built on curvature language merely because it is geometrically attractive.

### 2.3 Controlled and uncontrolled dynamics

Write the next-state law schematically as

\[
q_{t+1}\sim F_M(\cdot\mid z_t,u_t),
\]

where \(u_t\) is an intervention: prompt modification, candidate selection, activation steering, retrieval insertion, or another registered control.

The uncontrolled dynamics are

\[
q_{t+1}\sim F_M^0(\cdot\mid z_t).
\]

The controlled law is the foundation for reachability and planning. We do not assume it is linear, stationary, or globally smooth.

---

## 3. The coordinate layer is a gauge, not the Atlas

### 3.1 Why a common frame remains useful

Different embedding models use different native dimensions and coordinate systems. A common frame is useful because it lets us compare paths, transition statistics, and goals. But the frame does not need to be the unique or true semantic geometry.

Any frame construction is acceptable if it satisfies the downstream invariance required for navigation. Candidates include:

- paired orthogonal Procrustes;
- Generalized Procrustes Analysis for several models;
- relative representations;
- learned alignment adapters;
- `vec2vec`-style common latent translations;
- the artificial quasar/SRF construction retained from the earlier Atlas.

These are **coordinate-layer alternatives**, not competing ontologies.

### 3.2 Artificial quasars as one gauge-fixing construction

For canonical dimension \(k\), a simple Semantic Reference Frame uses the \(k+1\) vertices of a regular simplex

\[
Q=\{q_1,\ldots,q_{k+1}\},
\]

with

\[
\|q_i\|=1,
\qquad
q_i\cdot q_j=-\frac1k
\quad(i\neq j).
\]

These artificial landmarks define a fixed metrological geometry. They are not natural semantic concepts and do not themselves identify semantic axes.

A model-specific embedding \(x\) is first centered/whitened or otherwise normalized, then aligned to a frozen calibration cloud. For paired Procrustes,

\[
R_M^*
=
\arg\min_{R^TR=I}
\|X_MR-Y\|_F,
\]

and

\[
T_M(x)=W_M(x)R_M^*.
\]

The semantic identification comes from the paired calibration set, not from the simplex.

### 3.3 Static alignment is not the target result

The coordinate layer passes a minimum gate if held-out matched items are comparable after alignment and the transformation preserves navigation-relevant local relations. But a high static alignment score is only infrastructure.

The key logical separation is

\[
\text{coordinate compatibility}
\not\Rightarrow
\text{dynamic compatibility}.
\]

Jha et al. show that text embeddings can be translated across model families through a shared latent representation. Gröger, Wen, and Brbić show that after null calibration, local neighborhood agreement remains more robust than global spectral convergence. Both results motivate treating alignment as a plausible coordinate technology while leaving the dynamics question open.

### 3.4 Alignment baselines are mandatory

Any cross-model Atlas result must be repeated with at least two alignment classes when feasible. Otherwise an apparent dynamic mismatch may be an alignment artifact.

At minimum, compare:

1. a rigid/geometry-preserving frame such as Procrustes;
2. a stronger modern alignment or common-latent baseline.

If dynamic-transfer conclusions reverse solely because the alignment class changes, report the dependence rather than claiming a model-intrinsic phenomenon.

---

## 4. The model-indexed Semantic Atlas

For each model \(M\), define a local atlas entry

\[
A_M(z)
=
(\rho_M,K_M,U_M,F_M,C_M,\Omega_M),
\]

where these fields are optional components estimated at a registered state scale.

- \(\rho_M(z)\): empirical density or support of observed trajectories;
- \(K_M(z)\): measured local task competence/calibration where an external task exists;
- \(U_M(z)\): potential-like stability or escape difficulty;
- \(F_M\): transition law;
- \(C_M\): intervention or route cost;
- \(\Omega_M\): uncertainty in the Atlas estimate.

The scientific core is \((F_M,C_M,R_M,d_M^{nav},\Omega_M)\). Density, competence, and potential are auxiliary summaries.

### 4.1 Transition dynamics

A coarse transition field estimates

\[
F_M(z,u)
\approx
\mathbb E[q_{t+1}-q_t\mid z_t=z,u_t=u]
\]

or, preferably when data allow, a conditional distribution over next semantic states.

The field may be local and nonstationary. The Atlas should not force a global vector field when a graph, mixture model, local operator, or conditional density is better calibrated.

### 4.2 Control cost

Let \(u\) denote a registered intervention. Define

\[
C_M(z,u)
\]

as a cost combining compute, intervention magnitude, probability distortion, or another declared resource. Route cost is

\[
C_M(\Gamma)
=
\sum_t C_M(z_t,u_t)
\]

or a continuous analogue.

Different papers or applications may choose different cost functions. Therefore navigation distance is always relative to a declared cost model.

### 4.3 Reachability

Given current state \(z\), horizon \(H\), and budget \(B\), define

\[
R_M(z,H,B)
=
\{y:\exists\Gamma:z\rightarrow y,\;C_M(\Gamma)\le B\}.
\]

A semantic destination can be present in the shared coordinate frame yet operationally unreachable for one model under a budget.

This yields a model-relative concept of capability that is different from static nearest-neighbor geometry.

### 4.4 Directed navigation distance

Define

\[
d_M^{nav}(a,b)
=
\inf_{\Gamma:a\rightarrow b} C_M(\Gamma).
\]

In general,

\[
d_M^{nav}(a,b)\neq d_M^{nav}(b,a).
\]

The same two semantic regions can therefore be geometrically close but dynamically far apart, or vice versa.

This is the central reason a Semantic Atlas is not merely an embedding index.

### 4.5 Semantic gravity as escape cost

The earlier metaphor of **semantic gravity** is retained only as shorthand for a measured dynamical quantity. For region \(B\), define

\[
E_{escape,M}(B)
=
\inf_{\Gamma:B\rightarrow\neg B} C_M(\Gamma),
\]

with an explicit persistence condition preventing immediate return.

A region with high escape cost is an attractor-like region under the declared dynamics and cost, not evidence of a literal potential field or universal semantic basin.

---

## 5. Shared coordinates, different mechanics

The strongest conceptual prediction of the revised Atlas is that coordinate agreement can coexist with dynamical disagreement.

For matched semantic state \(x\), suppose

\[
q=T_A(E_A(x))\approx T_B(E_B(x)).
\]

This establishes static coordinate compatibility around \(x\). It does not imply

\[
F_A(z,u)\approx F_B(z,u),
\]

nor

\[
C_A(z,u)\approx C_B(z,u),
\]

nor

\[
R_A(z,H,B)\approx R_B(z,H,B).
\]

A useful analogy is a common geographic coordinate system used for vehicles with different mechanics. GPS coordinates can be identical while feasible routes differ for cars, boats, pedestrians, or aircraft. The Atlas studies the mechanics, not merely the GPS layer.

### 5.1 Static similarity versus dynamic similarity

For model pair \((A,B)\), report separately:

- static alignment quality \(S_{AB}^{static}\);
- one-step transition agreement \(S_{AB}^{F}\);
- control-response agreement \(S_{AB}^{C}\);
- reachable-set overlap \(S_{AB}^{R}\);
- route-rank or navigation-distance agreement \(S_{AB}^{nav}\).

A high \(S^{static}\) with low dynamic agreement is a scientifically meaningful result. It would show that representational interoperability does not license behavioral interchangeability.

### 5.2 Dynamic agreement may be local

There is no reason to expect one scalar dynamic-similarity score. Two models may transfer well in broad topical motion and poorly near compositional, mathematical, legal, or long-horizon transitions.

Therefore cross-model dynamics should be reported as a profile over states, horizons, controls, and task families.

---

## 6. Cross-model transfer of semantic dynamics

This is the main new experimental axis of the revised paper.

Assume source models

\[
M_1,\ldots,M_{n-1}
\]

and a held-out target

\[
M_*.
\]

Fit the coordinate layer and all meta-level modeling choices without using target trajectory outcomes. Source trajectories define a transfer prior or meta-model

\[
\widehat A_{- *}.
\]

The target model may expose embeddings or aligned semantic coordinates, but its trajectory outcomes remain held out for the zero-shot condition.

### 6.1 Zero-shot dynamic transfer

Use \(\widehat A_{-*}\) to predict target quantities such as

\[
q_{t+H},
\qquad
\Pr[g\in R_{M_*}(z,H,B)],
\qquad
C_{M_*}(\Gamma),
\qquad
\operatorname{rank}_{M_*}(\Gamma_1,\Gamma_2).
\]

The transfer model may condition on target-side **static** descriptors available without rollout labels: aligned coordinate geometry, model metadata when allowed, or frozen representation statistics. It may not use target trajectory results in the zero-shot condition.

### 6.2 Few-shot calibration curve

Then reveal \(k\) target trajectories and update the transferred Atlas. Let

\[
E_{transfer}(k)
\]

be held-out target error after transfer plus \(k\) target trajectories, and

\[
E_{scratch}(k)
\]

be the error of an otherwise matched target-only Atlas trained from those \(k\) trajectories without source-model transfer.

Report the full sample-efficiency curves, not one cherry-picked \(k\).

### 6.3 The Atlas-equivalent trajectory count

Define

\[
k^*_{Atlas}
=
\min\{k:E_{scratch}(k)\le E_{transfer}(0)\}.
\]

This measures how many target trajectories a zero-shot transferred Atlas is worth relative to learning target dynamics from scratch.

If no \(k\) in the registered range matches the transferred model, report a lower bound. If the scratch model wins with the first few samples, \(k^*_{Atlas}\) is correspondingly small.

A complementary statistic compares sample complexity at a fixed target error \(\epsilon\):

\[
\Delta k(\epsilon)
=
 k_{scratch}(\epsilon)-k_{transfer}(\epsilon).
\]

These quantities make transfer value operational rather than metaphorical.

### 6.4 Negative results are informative

Three outcomes matter:

1. **Static and dynamic transfer both succeed.** Shared coordinates capture part of reusable mechanics.
2. **Static succeeds, dynamic transfer fails.** Universal/interoperable geometry does not imply universal dynamics.
3. **Both fail.** The chosen frame is not useful for this target population.

The second outcome is especially important because it draws a sharp boundary around what representational-alignment results permit us to infer.

---

## 7. Multiresolution is computational, not an observer hierarchy

The Atlas remains multiresolution, but the meaning changes. Resolution is a property of the **map representation and planner**, not a ranking of models as clearer or blurrier observers.

Let

\[
\mathcal A_{M,0},\mathcal A_{M,1},\ldots,\mathcal A_{M,L}
\]

be progressively finer dynamic summaries.

A coarse cell may store transition probabilities and route costs among broad regions. A fine chart may store local state distributions, control responses, or lexical realization information.

The Borges constraint remains:

> a map at 1:1 scale has stopped being useful as a map.

Refinement should therefore be driven by predictive or control uncertainty. For example, refine a cell when

\[
\Omega_M(z,H)>\tau
\]

or when a coarse policy cannot distinguish candidate routes with sufficient confidence.

The central compression question is:

\[
\text{How coarse can the Atlas remain while preserving useful prediction and control?}
\]

---

## 8. Navigation as optimal control

Suppose the current state is \(z_0\) and the task defines goal set \(G\). A planner chooses route/control sequence

\[
\Gamma^*
=
\arg\min_{\Gamma} J_M(\Gamma)
\]

subject to reachability, budget, and task constraints.

A generic objective is

\[
J_M(\Gamma)
=
\alpha C_M(\Gamma)
+\beta U_M(\Gamma)
+\gamma O_M(\Gamma)
+\delta T_M(\Gamma),
\]

where \(U_M\) is predictive uncertainty, \(O_M\) penalizes unsupported/off-manifold motion, and \(T_M\) is expected token or compute cost.

The shortest route in coordinate distance is only a baseline. The Atlas planner is supposed to exploit the **model-specific directed cost landscape**.

### 8.1 Corridors and bridges

If a direct transition \(A\rightarrow B\) has low success probability or high cost, but

\[
A\rightarrow G_1\rightarrow G_2\rightarrow B
\]

is reliable, the intermediate states form a useful dynamic bridge.

This gives a falsifiable version of the intuition that decomposition helps: the Atlas predicts in advance which intermediate route has higher success at matched budget.

### 8.2 Perquire as a planner implementation

A search system such as Perquire can be viewed as an implementation layer over the Atlas:

\[
\text{Atlas}=\text{estimated dynamics/cost/reachability},
\]

\[
\text{Perquire}=\text{planner/search over those estimates}.
\]

This relation is architectural, not evidentiary. Perquire's success would not prove the Atlas formalism unless gains are attributable to the registered dynamic quantities rather than generic search.

---

## 9. From route to generation: Semantic Model Predictive Control

The first controller should remain black-box and expensive on purpose. At semantic state \(z_t\), sample candidate short continuations \(c_1,\ldots,c_N\). Embed their resulting prefixes and score them using the route objective:

\[
S(c_i)
=
-\widehat J_M(\Gamma_i)
+\lambda\log P_M(c_i).
\]

Execute only a short prefix of the best candidate, observe the new semantic state, and replan.

This is semantic Model Predictive Control (MPC).

MPC may consume **more** compute than ordinary generation because discarded rollouts are evaluated. The first question is controllability:

> Does a model-specific Atlas select continuations that reach registered semantic goals more reliably at matched rollout budget than static geometry or direct prompting?

Only after that result may the programme claim efficiency.

### 9.1 Required baselines

Compare at least:

1. base generation;
2. explicit goal prompting;
3. nearest-goal or cosine-progress reranking;
4. local Q/value predictor without an Atlas;
5. Atlas MPC using learned dynamics/cost;
6. oracle dynamics where available in synthetic tasks.

If Atlas MPC does not beat static geometric reranking, the dynamic machinery has not paid for itself.

---

## 10. Semantic Servo and causal local control

MPC establishes whether semantic routes can guide generation, but it wastes rollouts. A later controller can attempt direct hidden-state corrections.

Let \(h_{\ell,t}\) be a model hidden state. Train a future-state head

\[
G_H(h_{\ell,t})
\approx
q_{t+H}-q_t.
\]

For desired displacement \(\Delta q^*\), define

\[
e
=
\Delta q^*-G_H(h_{\ell,t}).
\]

A local sensitivity is

\[
\widehat J^{sem}_{\ell,H}
=
\frac{\partial G_H}{\partial h_{\ell,t}}.
\]

A regularized correction may solve

\[
\widehat J^{sem}_{\ell,H}\delta h\approx e.
\]

One minimum-norm form is

\[
\delta h
=
(\widehat J^{sem})^\top
\left(
\widehat J^{sem}(\widehat J^{sem})^\top+\lambda I
\right)^{-1}e.
\]

But the derivative of a fitted head is not automatically a causal derivative of the generated trajectory. Before using it for control, inject registered small perturbations and verify that

\[
\widehat J^{sem}\delta h
\]

predicts the **measured** change in future aligned semantic state.

The Servo passes only if closed-loop correction reduces route error at acceptable language-quality and intervention cost compared with static steering and matched random directions.

---

## 11. Can dynamics be compiled from weights?

Weight-space compilation is retained as a later hypothesis and is explicitly downstream of the observational Atlas.

### 11.1 Static reduced coordinates

For final logit map

\[
\ell=W_Uh,
\]

a truncated decomposition

\[
W_U\approx U_k\Sigma_kV_k^\top
\]

defines reduced coordinate

\[
z=V_k^\top h.
\]

This may expose useful static lexical structure. It does not establish semantic transition dynamics.

### 11.2 Local dynamic operators

Within a registered region \(c\), fit a local approximation

\[
q_{t+1}
\approx
A_{M,c}q_t+B_{M,c}u_t+b_{M,c}.
\]

The value of such an operator is empirical. It must predict multiple held-out steps better than dimension-matched simple baselines and remain useful long enough for planning.

### 11.3 Transferable operators

A stronger question follows naturally from the revised paper: after placing two models in the same frame, are any local operators reusable?

For aligned regions, compare

\[
A_{A,c}
\quad\text{and}\quad
A_{B,c}
\]

only after controlling for estimation noise and alignment choice. If operator transfer works, it could reduce the number of target trajectories needed to initialize a new Atlas. If not, weight compilation remains model-specific.

---

## 12. Experimental programme

The programme is staged so that later claims depend on earlier gates.

### 12.1 Model population

A single same-family pair is insufficient for cross-model dynamics. The initial population should contain several open models spanning at least two architecture/training families where compatible embedding/trajectory measurements can be constructed.

A same-family pair such as Qwen3-0.6B plus Qwen3-Embedding-0.6B remains useful for an initial mechanics test, but the transfer experiment requires leave-one-model-out evaluation over a broader population.

### 12.2 Dataset and trajectory protocol

Freeze before fitting:

- prompt/task families;
- decoding settings;
- semantic chunking rule;
- trajectory horizons;
- coordinate-alignment train/test split;
- source-model/target-model folds;
- intervention classes;
- route-cost definition.

Target-model trajectory outcomes used for final testing must not leak into frame fitting, hyperparameter selection, or zero-shot transfer features.

### 12.3 Experiment A — coordinate interoperability gate

Fit at least two alignment methods. On held-out paired semantic items measure:

- coordinate/cosine agreement;
- local-neighborhood agreement;
- trajectory-shape preservation for already observed matched paths;
- shuffled-correspondence nulls;
- dimension- and scale-matched native-space baselines.

This experiment establishes only whether a common comparison frame is usable.

### 12.4 Experiment B — within-model dynamic identification

For each model independently, estimate future semantic displacement, transition probabilities, reachability, and route cost.

Compare:

1. static coordinate only;
2. static local neighborhood features;
3. short trajectory history;
4. Atlas state \(z_t\);
5. stronger sequence baseline.

The Atlas needs to demonstrate that its compact state has predictive value at useful horizons.

### 12.5 Experiment C — static alignment versus dynamic agreement

For every model pair, compare static alignment quality with held-out dynamic agreement.

Primary analysis:

\[
S_{AB}^{static}
\quad\text{vs.}\quad
S_{AB}^{F},S_{AB}^{R},S_{AB}^{nav}.
\]

The point is not to force a positive correlation. A weak relation is a valid result and would delimit universal-geometry claims.

### 12.6 Experiment D — leave-one-model-out dynamic transfer

Hold model \(M_*\) out. Fit the common frame and transfer prior using the source population, without target trajectory labels.

Evaluate:

- zero-shot target future-state prediction;
- zero-shot reachability prediction;
- zero-shot route ranking;
- target-only baseline at \(k=0\) where defined;
- few-shot transfer for registered \(k\) values;
- target-only-from-scratch curves at the same \(k\).

Report

\[
E_{transfer}(k),
\qquad
E_{scratch}(k),
\qquad
k^*_{Atlas},
\qquad
\Delta k(\epsilon).
\]

Repeat over every model as the held-out target.

### 12.7 Experiment E — MPC navigation

For origin/goal pairs and multi-waypoint tasks compare base generation, direct prompting, static semantic reranking, and Atlas MPC.

Primary endpoint:

\[
\text{success@budget}
\]

with compute including discarded rollouts. Secondary endpoints include path cost, revisits, semantic route error, output likelihood, correctness, and naturalness.

### 12.8 Experiment F — Semantic Servo

After the MPC gate, fit and causally calibrate local future-state sensitivities. Compare Semantic Servo with static activation steering and matched random controls.

A Servo result is about efficient route execution, not about the existence of universal semantic coordinates.

### 12.9 Experiment G — compiled dynamics

Compare empirical Atlas dynamics with operators or reduced maps derived from weights. Random subspaces and dimension-matched low-rank controls are mandatory.

---

## 13. Metrics

### 13.1 Future-state prediction

For horizon \(H\), report calibrated error

\[
E_F(H)
=
\mathbb E[d(\widehat q_{t+H},q_{t+H})]
\]

plus rank/neighborhood versions where raw metric distances are not comparable.

### 13.2 Reachability calibration

For registered target regions \(g\), evaluate

\[
\widehat p_M(g\in R_M(z,H,B))
\]

using proper scoring rules and calibration curves.

### 13.3 Route-ranking agreement

Given candidate routes \(\Gamma_i\), compare predicted and empirical cost/success orderings. This can be more robust than requiring exact transition prediction.

### 13.4 Dynamic transfer gain

At each \(k\), define

\[
\Delta E(k)
=
E_{scratch}(k)-E_{transfer}(k).
\]

Positive \(\Delta E\) means the source population reduces target error at the same number of target trajectories.

### 13.5 Atlas-equivalent trajectory count

Report \(k^*_{Atlas}\) and \(\Delta k(\epsilon)\) as defined above. These are the primary sample-efficiency metrics for cross-model Atlas transfer.

### 13.6 Navigation efficiency

If \(J_M^*\) is the best estimated admissible route cost and \(J_M\) the realized cost, define

\[
NPE
=
\frac{J_M^*}{J_M}
\]

only within a declared Atlas/cost definition.

Token count, FLOPs, latency, and API/model calls must be reported separately. Token savings do not imply compute savings.

---

## 14. Falsification criteria

### H1 — trajectory-state value

**Claim.** A compact trajectory state predicts future semantic motion better than static endpoint geometry at registered horizons.

**Fails if.** History/trajectory features add no reproducible held-out value over static or simple sequence baselines.

### H2 — coordinate interoperability

**Claim.** At least one chosen frame makes cross-model semantic coordinates sufficiently comparable for downstream dynamic tests.

**Fails if.** Held-out alignment is no better than shuffled or matched nulls, or conclusions are unstable to reasonable alignment choices.

### H3 — model-specific dynamics

**Claim.** Transition, reachability, and navigation quantities are reproducible within a model and not reducible to static distance alone.

**Fails if.** Dynamics are too noisy to predict or static geometry explains equivalent held-out behavior.

### H4 — cross-model dynamic transfer

**Claim.** Source-model dynamics provide useful prior information about a held-out target model after static alignment.

**Fails if.** Across held-out targets,

\[
\Delta E(k)\le0
\]

at the preregistered sample sizes or \(k^*_{Atlas}\) is operationally negligible.

A failure of H4 does **not** invalidate H1-H3; it establishes that the Atlas is model-specific rather than transferable.

### H5 — static alignment does not determine dynamics

This is deliberately two-sided.

**Question.** How strongly does \(S^{static}\) predict dynamic agreement?

A strong relation supports reusable mechanics; a weak relation establishes an important separation between geometry and dynamics. The paper must report whichever occurs rather than treating only one direction as success.

### H6 — navigation

**Claim.** Atlas-aware planning improves goal attainment at matched rollout/compute budget beyond static semantic reranking and prompting.

**Fails if.** Dynamic planning adds no benefit or gains require unacceptable language-quality degradation.

### H7 — Semantic Servo

**Claim.** Causally calibrated local control follows Atlas routes with fewer discarded rollouts or lower intervention cost than MPC/static steering.

**Fails if.** The fitted Jacobian does not predict measured intervention effects or closed-loop gains disappear against matched controls.

### H8 — weight compilation

**Claim.** A useful fraction of dynamic structure can be predicted from weights or sparse measurements.

**Fails if.** compiled operators do not beat random/dimension-matched baselines or do not reduce trajectory sample requirements.

---

## 15. Prior art and novelty boundary

The revised Atlas deliberately concedes the static-coordinate territory.

### 15.1 Representation convergence and universal geometry

Huh et al. formulate the Platonic Representation Hypothesis. Jha et al. demonstrate unpaired translation of text embeddings through a learned universal latent representation. Achara et al. provide multi-way representation alignment. Gröger, Wen, and Brbić show that scale confounds inflate common similarity metrics and that calibrated local neighborhood similarity survives more robustly than global spectral convergence.

**Not claimed here:** discovery of a universal embedding geometry, first cross-model alignment, or first common latent representation.

The Atlas uses these results as motivation for treating a common coordinate layer as available infrastructure worth testing.

### 15.2 Relative representations and Procrustes

Relative representations and Procrustes alignment already provide coordinate-invariant or interoperable views across latent spaces.

**Not claimed here:** a new solution to the basic gauge problem.

Artificial quasars remain one metrological implementation whose value is downstream navigational utility, not coordinate novelty.

### 15.3 Reduced-order and predictive-state modeling

Dynamical-systems and control literatures have long studied compact predictive states, local linearizations, reachability, model predictive control, and system identification.

**Not claimed here:** invention of those mathematical objects.

The Atlas question is domain-specific: whether autoregressive language-model behavior admits a useful **semantic** reduced-order dynamics in an external comparison frame, and whether that dynamics transfers across aligned models.

### 15.4 Activation steering and context-dependent control

Static activation steering, Steering Vector Fields, energy-based steering, and Jacobian-based interpretability/control already show that internal interventions can alter model behavior.

**Not claimed here:** first hidden-state controller.

The Servo's narrower question is whether control signals derived from an explicit learned route/reachability model outperform static directions or rollout-only planning.

### 15.5 Candidate contribution

The surviving contribution is the combination of:

1. a strict separation between **coordinate layer** and **model-specific semantic dynamics**;
2. a model-indexed Atlas \(\mathfrak A=(\mathcal Q,\{A_M\})\);
3. explicit measurement of transition, control cost, reachability, and directed navigation distance in that frame;
4. a leave-one-model-out test of **dynamic transfer after static alignment**;
5. sample-equivalence quantities \(k^*_{Atlas}\) and \(\Delta k(\epsilon)\);
6. downstream planning/control tests that must beat static-geometry baselines.

The originality claim should be rejected if prior work is found that already performs this same cross-model transfer-of-dynamics experiment over aligned language-model semantic trajectories.

---

## 16. Limitations

### 16.1 The coordinate frame can still distort dynamics

Even excellent static alignment may warp directions or scales relevant to transition estimation. Dynamic conclusions must be checked across multiple reasonable frames.

### 16.2 Semantic embeddings may omit computational state

An external embedding can smooth over distinctions that are essential to reasoning. Failure of the Atlas may reflect an inadequate observer rather than absence of reduced dynamics.

### 16.3 Trajectories depend on prompting and decoding

\(F_M\) is conditional on the registered generation protocol. Temperature, system prompt, retrieval context, tool use, and decoding rules can change the dynamics. The Atlas must declare these conditions rather than treating dynamics as an unconditional property of a model checkpoint.

### 16.4 Transfer can be ancestry rather than universality

Closely related model families may share dynamics because of common training data, architecture, distillation, or fine-tuning. Leave-family-out analysis is therefore stronger than random leave-one-model-out when enough models are available.

### 16.5 Reachability is cost-relative

Changing the allowed control set or budget changes \(R_M\). No reachable-set result is meaningful without the control class and cost definition.

### 16.6 Atlas construction can be expensive

Offline rollout cost must be amortized by repeated use, transfer, or compilation. A beautiful map that costs more to construct than the tasks it accelerates is not an efficiency result.

### 16.7 Hidden-state steering can leave the training manifold

Servo interventions may damage correctness, calibration, or safety. Minimum-intervention and output-quality constraints are mandatory.

---

## 17. Discussion: one coordinate system, many engines

The revised Semantic Atlas assigns different jobs to different layers.

The **language model** is the microscopic engine that produces lexical behavior.

The **coordinate frame** is a gauge. It gives comparable labels to locations but need not be the true geometry of meaning.

The **model-specific Atlas** records the mechanics of motion in that gauge: transition tendencies, barriers, reachable regions, and control costs.

The **planner** searches those mechanics for an admissible route.

The **Semantic Servo** executes route corrections in closed loop.

This changes the main analogy. The Atlas no longer needs multiple models to be telescopes of different resolution looking at the same object. A better analogy is several vehicles using the same coordinate system with different transition laws.

Two models can agree that they are at \(q\) and disagree about what happens next. One may reach target \(g\) directly; another may require intermediate states. One may be easily steered out of a basin; another may have high escape cost. Static geometry tells us where we are writing the coordinates. The Atlas tells us what motion is possible.

This separation also gives a clean interpretation of universal-geometry work:

\[
\boxed{
\text{Universal geometry, if it exists, is the coordinate layer—not the Atlas.}
}
\]

And it gives a sharper research question:

\[
\boxed{
\text{Does geometric alignment transfer any useful semantic dynamics?}
}
\]

That question is meaningful whether the answer is yes, no, or only locally.

---

## 18. Conclusion

The Semantic Atlas should not compete with modern representation alignment by claiming another universal semantic coordinate system. Its defensible scientific target is downstream of alignment.

Choose a frame. Represent generated discourse as trajectories. For each model, estimate the transition law, control cost, uncertainty, reachable sets, and directed navigation distances. Then ask whether those mechanics are compressible enough for planning and whether any of them transfer to a held-out model once static coordinates have been aligned.

The strongest positive result would be a transferred Atlas that predicts target dynamics before substantial target rollout and reduces the number of trajectories required for useful planning. The cleanest negative result would be equally informative: high static alignment with little or no dynamic transfer. That would demonstrate that interoperable semantic coordinates do not make language models dynamically interchangeable.

Only after dynamics prediction and route planning survive strong baselines should the programme pursue Semantic Servo control, weight-space compilation, or compute savings.

The intended end state is therefore not a universal semantic map. It is a **common chart carrying several empirically learned systems of motion**—coarse enough to be useful, model-specific enough to be honest, and predictive enough to tell a planner not merely where a destination lies, but whether this model can get there and at what cost.

---

## References

- Achara, A., Gaintseva, T., Mahaut, M., et al. (2026). **Multi-Way Representation Alignment.** ICML 2026. arXiv:2602.06205. https://arxiv.org/abs/2602.06205
- Gröger, F., Wen, S., & Brbić, M. (2026). **Revisiting the Platonic Representation Hypothesis: An Aristotelian View.** ICML 2026. arXiv:2602.14486. https://arxiv.org/abs/2602.14486
- Grover, K., Zeng, H., Xia, Y., Faloutsos, C., & Gordon, G. J. (2026). **Text Has Curvature.** arXiv:2602.13418. https://arxiv.org/abs/2602.13418
- Gurnee, W., Sofroniew, N., Pearce, A., et al. (2026). **Verbalizable Representations Form a Global Workspace in Language Models.** arXiv:2607.15495. https://arxiv.org/abs/2607.15495
- Huh, M., Cheung, B., Wang, T., & Isola, P. (2024). **Position: The Platonic Representation Hypothesis.** ICML 2024, PMLR 235:20617–20642. https://proceedings.mlr.press/v235/huh24a.html
- Jha, R., Zhang, C., Shmatikov, V., & Morris, J. X. (2025). **Harnessing the Universal Geometry of Embeddings.** NeurIPS 2025. arXiv:2505.12540. https://arxiv.org/abs/2505.12540
- Jiang, E. H., Ou, W., Liu, R., et al. (2026). **Mitigating Over-Refusal in Aligned Large Language Models via Inference-Time Activation Energy.** ACL 2026. https://aclanthology.org/2026.acl-long.1759/
- Li, J., Li, Y., & Huang, K.-H. (2026). **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models.** arXiv:2602.01654. https://arxiv.org/abs/2602.01654
- Maystre, L., Ortega Gonzalez, A., Park, C., et al. (2025). **When Embedding Models Meet: Procrustes Bounds and Applications.** arXiv:2510.13406. https://arxiv.org/abs/2510.13406
- Moschella, L., Maiorca, V., Fumero, M., Norelli, A., Locatello, F., & Rodolà, E. (2022). **Relative Representations Enable Zero-Shot Latent Space Communication.** arXiv:2209.15430. https://arxiv.org/abs/2209.15430
- Zhang, Y., Li, M., Long, D., et al. (2025). **Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models.** arXiv:2506.05176. https://arxiv.org/abs/2506.05176

## Issue map

This paper remains developed under #260. Existing prior-art, trajectory, SRF, reachability, Servo, observational-atlas, MPC, Jacobian, compilation, and integration issues (#261–#270) remain useful, but the revised synthesis changes their priority: coordinate/SRF work is an enabling layer; **within-model dynamics and cross-model dynamic transfer now precede efficiency and compilation claims**.