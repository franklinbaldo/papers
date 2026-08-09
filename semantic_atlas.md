---
type: "Technical Paper"
title: "Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models"
description: "Position paper proposing a multiscale semantic atlas compiled from language models, artificial quasar reference frames, reachability fields, and closed-loop steering for efficient generation."
tags: [semantic-atlas, embeddings, steering, interpretability, control, efficient-inference]
timestamp: 2026-08-09T00:15:00Z
---

# Semantic Atlas: Quasar Reference Frames, Reachability, and Closed-Loop Navigation for Language Models

**Franklin Baldo**  
Independent Researcher  
franklinbaldo@gmail.com

---

> **Position paper and experimental programme.** This manuscript proposes a mathematical and computational framework and pre-registers a sequence of toy experiments. Unless a section is explicitly marked as reporting a completed experiment, all claims about efficiency, cross-model invariance, controllability, atlas compilation, and token savings are hypotheses or design targets rather than measured results.

## Abstract

Autoregressive language models generate text one token at a time even when the task appears to require movement through a much lower-dimensional sequence of semantic states. This paper asks whether that semantic dynamics can be made explicit, mapped, and controlled independently of the model's native token coordinates. We propose **Semantic Atlas**, a multiscale representation of language-model dynamics built on four ideas. First, a text is represented not only by embeddings but by a trajectory through semantic state space, with position, velocity, curvature, and scale. Second, model-specific coordinates are aligned to an artificial **Semantic Reference Frame (SRF)** whose geometry is defined by mathematically constructed landmarks, called **semantic quasars**, while its semantic orientation is fixed empirically by a shared, row-paired calibration set. The quasars define the external gauge; paired examples determine how each model is placed into that gauge. Third, repeated model trajectories induce an atlas containing density, local competence, transition dynamics, control cost, reachability, and a potential-like quantity informally called **semantic gravity**. Fourth, a planner chooses low-cost routes through this atlas while a **Semantic Servo** converts desired semantic motion into local generation control through rollout selection or hidden-state feedback.

The programme deliberately separates six claims that are easy to conflate: (1) semantic trajectories are geometrically informative; (2) an artificial reference frame can preserve useful structure; (3) an atlas can approximate model dynamics; (4) semantic routes can control generation; (5) such control can reduce token or compute cost; and (6) useful parts of the atlas can be compiled directly from model weights rather than discovered solely by autoregressive exploration. We define falsification criteria for each claim and propose a staged experiment using a small open generator and a related embedding model. The long-term hypothesis is not that the atlas replaces language models everywhere, but that planning can occur at a coarser semantic resolution than lexical generation, with the full model invoked only where linguistic resolution is required.

**Keywords:** semantic trajectories, representation geometry, relative representations, activation steering, semantic navigation, model predictive control, Jacobian, reachability, efficient inference, multiscale representation

---

## 1. Introduction

A language model exposes a peculiar interface to a large body of learned structure: whatever it knows or can compute must ordinarily be reached through an autoregressive path. Even when the final answer is conceptually close to a known solution, the model proceeds through a sequence of token-level state transitions. Long-form reasoning can therefore contain detours, repetitions, abandoned branches, abrupt changes of topic, and verbalized intermediate work that may be unnecessary for the final result.

Dense embeddings suggest a different view. A sentence, paragraph, argument, or conversation can be represented as a point in a high-dimensional semantic space. But a conversation is not merely a collection of such points. It is ordered. The ordering traces a path. Once text is treated as a trajectory, several questions become natural:

1. Can two conversations be compared by the *shape and dynamics* of their paths rather than only by endpoint similarity?
2. Can multiple embedding models be aligned to a common navigational frame without pretending that their native coordinates are universal?
3. Can a corpus of trajectories be compiled into a reusable map of corridors, barriers, attractor-like regions, and reachable destinations?
4. Given a desired semantic route, can a language model be steered to realize it without prescribing the exact words in advance?
5. Can planning in the map skip semantic distance that would otherwise be explored token by token, reducing inference cost?
6. Can part of this map be extracted directly from a model's weights, with dynamic sampling used only for calibration and local refinement?

This paper proposes a framework for asking these questions separately. The central object is a **Semantic Atlas**: a compressed, multiresolution, model-relative map expressed in an externally fixed and empirically calibrated reference frame. The frame is not model-independent by construction: cross-model correspondence is a hypothesis that must be earned on held-out paired examples. The atlas is not assumed to be an exact copy of the model. Indeed, if it preserved every possible lexical distinction at every point, it would collapse into the problem made famous by Borges's *On Exactitude in Science*: a map at 1:1 scale has ceased to be useful as a map. The intended atlas is instead coarse almost everywhere and locally detailed only where the navigation or decoding task requires it.

The proposed architecture separates five layers:

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

The key research hypothesis is that the semantic dynamics relevant to planning are substantially lower-dimensional and smoother than the raw combinatorics of token sequences. If this is false, the atlas will either lose too much predictive information or grow until it reproduces the original model. If it is true, a model may be able to plan and traverse long conceptual distances using a small number of semantic transitions while delegating local lexical realization to the original generator.

## 2. From contextual meaning to semantic trajectories

### 2.1 Tokens are positions, not semantic atoms

A tokenizer supplies a discrete sequence

\[
x_1,x_2,\ldots,x_n,
\]

but a token's meaning is contextual. We therefore distinguish the token position from the semantic state associated with that position. Let

\[
S(i,r)\in\mathbb R^d
\]

denote a representation of position \(i\) when interpreted with contextual radius \(r\). The radius may denote a symmetric window in retrospective text analysis. For causal generation we use an explicitly left-context form,

\[
S^-(i,l)=S(i,l,0),
\]

so no future token is allowed to influence the navigation state.

For a fixed scale \(r\), the sequence

\[
\gamma_r(i)=S(i,r)
\]

is a discrete semantic trajectory. Varying \(r\) yields a family of trajectories, or equivalently a multiscale surface indexed by textual position and contextual scale.

This distinction matters because a word can move substantially in representation space as context accumulates. A phrase that initially appears financial may later become metaphorical; a sentence in a mystery novel may acquire a different interpretation after a later reveal. The retrospective displacement

\[
D_i=d(S^-(i,l),S(i,l,r_{future}))
\]

is itself a measurable property, but it must not be used by a causal controller.

### 2.2 Position is not a complete dynamic state

Given one trajectory \(\gamma(t)\), define the local displacement

\[
v_t=\gamma(t+1)-\gamma(t),
\]

a discrete acceleration

\[
a_t=v_{t+1}-v_t,
\]

and a turning angle

\[
\theta_t=\cos^{-1}\frac{v_{t-1}\cdot v_t}{\|v_{t-1}\|\|v_t\|}.
\]

The same semantic position can be approached from different directions. Therefore an embedding alone is not a full state description for navigation. A minimal dynamic state may have the form

\[
z_t=(q_t,v_t,\kappa_t,\sigma_t),
\]

where \(q_t\) is a location in a canonical reference frame, \(v_t\) is semantic velocity, \(\kappa_t\) summarizes curvature, and \(\sigma_t\) records scale and uncertainty.

The empirical question is how much of future semantic motion can be predicted from such a compressed state compared with the full transformer state.

## 3. Semantic quasars and a reference frame

### 3.1 Why native embedding coordinates are insufficient

Embedding spaces are useful because relative geometry can be stable while absolute coordinates are not. Two independently trained models can encode similar relations in spaces that differ by rotations, reflections, rescalings, anisotropy, or more complex transformations. Relative representations address part of this problem by expressing a point through its similarity to a set of anchors rather than by its raw coordinates [Moschella et al., 2022].

The present proposal introduces a stricter separation between **reference geometry** and **semantic calibration**. Instead of requiring the reference landmarks themselves to correspond to natural concepts, we define the quasar geometry mathematically. That does **not** identify semantic axes: a regular simplex is symmetric under orthogonal transformations. Semantic orientation enters through a shared calibration set whose rows denote the same texts or states across observers.

### 3.2 Artificial quasars

Let the effective canonical dimension be \(k\). The simplest SRF uses the \(k+1\) vertices of a regular simplex,

\[
Q=\{q_1,\ldots,q_{k+1}\},
\]

with

\[
\|q_i\|=1,\qquad q_i\cdot q_j=-\frac1k\quad(i\neq j).
\]

These points are the first **semantic quasars**. They need not be realizable as natural-language embeddings. Their role is metrological: they define a fixed external geometry. Their labels do not carry semantic identity. Calling one vertex `Q17` does not make the corresponding native direction in two independently trained models the same direction.

For a normalized semantic state \(y\), define its quasar coordinates by

\[
C_Q(y)=[y\cdot q_1,\ldots,y\cdot q_m].
\]

A redundant frame or spherical code can replace the simplex when robustness is more important than minimal coordinates.

### 3.3 Calibration

A model-specific embedding \(x\) is mapped to the SRF through a calibration function

\[
T_M:x\mapsto q.
\]

The v0 calibration uses **shared correspondences**. Let \(c_1,\ldots,c_n\) be calibration items observed by every model. A designated reference observer is centered and whitened to dimension \(k\); its resulting coordinates on those frozen items become a canonical target matrix \(Y\in\mathbb R^{n\times k}\). For another model \(M\), let \(X_M\) be its independently whitened coordinates for the same row-paired items. We then fit

\[
R_M^*=\arg\min_{R^TR=I}\|X_MR-Y\|_F,
\]

using orthogonal Procrustes, and define \(T_M(x)=W_M(x)R_M^*\), where \(W_M\) is that model's fitted centering/whitening transform. The artificial quasars are then evaluated in this shared coordinate system.

This calibration resolves the rotational gauge only to the extent that the paired calibration examples span the retained dimension and generalize to unseen items. A second SVD of an already whitened cloud cannot provide this identification: after whitening, equalized variance leaves orthogonal orientation unconstrained. Sign fixing resolves only a \(\pm\) ambiguity and is not a substitute for cross-model anchoring.

A learned adapter is a later baseline, not the starting assumption.

### 3.4 What would count as success?

An SRF is useful if it preserves the relationships needed for navigation and, when cross-model alignment is claimed, if independently fitted observers produce the **same held-out coordinates** for corresponding items. Relevant tests include:

- held-out canonical-coordinate RMSE and cosine agreement across observers;
- nearest-quasar agreement on held-out items;
- degradation under deliberately shuffled calibration correspondences;
- neighborhood, local distance, angle, and trajectory-shape preservation;
- synthetic recovery from unknown rotations/reflections and anisotropic scalings;
- graceful degradation as canonical dimension decreases.

Distance preservation alone cannot validate the shared-frame claim because distances and angles are already invariant under global orthogonal rotations. Cross-model universality is stronger still: success on two observers would establish calibrated interoperability for that pair, not a universal semantic sky.

## 4. The Semantic Atlas

### 4.1 The atlas is not the model

Let \(M\) denote a language model and \(A_M\) an atlas compiled or estimated from it. The intended relationship is

\[
M\longrightarrow A_M,
\]

where \(A_M\) deliberately discards most microscopic lexical state while preserving information useful for navigation.

A local atlas entry at semantic state \(q\) may contain

\[
A_M(q)=(\rho,K,U,F,C,\Omega),
\]

where:

- \(\rho(q)\): density of observed trajectories;
- \(K_M(q)\): local measured competence/calibration on tasks associated with the region;
- \(U_M(q)\): potential-like stability or escape difficulty;
- \(F_M(q)\): estimated distribution of natural semantic transitions;
- \(C_M(q,u)\): cost of applying control \(u\);
- \(\Omega(q)\): atlas uncertainty.

These quantities must remain distinct. A region may be frequently visited yet factually unreliable; it may contain accurate knowledge but be dynamically difficult to enter; a deep attractor can encode a repetitive failure mode rather than useful expertise.

### 4.2 Semantic gravity

The term **semantic gravity** is an intuition for resistance to leaving a region, not a claim that the space obeys Newtonian mechanics. For a region \(B\), define an escape cost

\[
E_{escape}(B)=\min_{\Gamma:B\rightarrow\neg B} C(\Gamma),
\]

where \(C(\Gamma)\) is the intervention cost of a path that leaves the region and does not immediately return.

A practical version can be estimated experimentally by increasing steering magnitude until a chosen proportion of continuations leave a cluster and remain outside it for a fixed horizon. This yields quantities such as \(E_{escape}^{50}\) and \(E_{escape}^{90}\).

Recent work on activation energy and context-dependent steering provides neighboring operational tools: energy-based controllers can assign low energy to desired activation states and steer along local gradients, while Steering Vector Fields replaces one static direction with a position-dependent field [Jiang et al., 2026; Li et al., 2026]. The Semantic Atlas differs by treating such dynamics as properties of a global navigational chart rather than a single behavior objective.

### 4.3 Reachability

Given model \(M\), state \(q\), horizon \(H\), and budget \(B\), define a reachable set

\[
R_M(q,H,B)=\{y:\exists\Gamma:q\rightarrow y,\ C_M(\Gamma)\le B\}.
\]

This reframes model capability. A target can exist in the external semantic map while remaining unreachable by a given model under a resource budget.

The induced navigation distance

\[
d_M^{nav}(a,b)=\min_{\Gamma:a\rightarrow b} C_M(\Gamma)
\]

need not be symmetric. Generalization from an example to a principle can have a different cost from constructing an example from a principle. The resulting geometry is therefore better thought of as a directed cost landscape than a Euclidean map.

### 4.4 Corridors, barriers, and bridges

A high-density low-cost set of transitions forms a semantic corridor. A region with high escape cost or low transition probability forms a barrier. A narrow sequence of low-cost intermediate states can connect two otherwise distant basins.

Such bridges are interesting because they provide a testable explanation for why decomposition helps smaller models. A model may fail at a direct transition \(A\rightarrow B\) while succeeding at

\[
A\rightarrow G_1\rightarrow G_2\rightarrow B.
\]

The atlas turns decomposition into route planning rather than a manually supplied chain of thought.

## 5. Multiresolution and the Borges constraint

A globally exact atlas would be uselessly large. The intended representation is therefore hierarchical. Let

\[
\mathcal A_0,\mathcal A_1,\ldots,\mathcal A_L
\]

be progressively finer partitions or local charts. At coarse levels, cells summarize broad regions and expected transitions. At fine levels, they encode local state distributions and lexical realization.

The atlas should refine where uncertainty matters. If \(X\) is the next lexical block and \(C_r\) is the current semantic cell at resolution \(r\), one possible zoom criterion is

\[
H(X\mid C_r)>\tau.
\]

When predictive entropy is high, refine the local chart or invoke the full model. When it is low, a lightweight decoder may suffice.

This creates an explicit boundary between map and territory:

- **zoom out** to plan long semantic travel;
- **zoom in** to select a local concept or phrase;
- invoke the full LLM when local ambiguity exceeds the atlas's calibrated resolution.

The atlas is useful only while the information discarded globally is larger than the information reconstructed locally.

## 6. Navigation as optimal control

### 6.1 Route planning

Suppose the current state is \(q_0\) and the task defines one or more goals \(G=\{g_1,\ldots,g_m\}\). A route planner chooses

\[
\Gamma^*=\arg\min_{\Gamma} J(\Gamma)
\]

subject to required waypoints or precedence constraints. A generic cost is

\[
J(\Gamma)=
\alpha L(\Gamma)+
\beta K(\Gamma)+
\gamma O(\Gamma)+
\delta U(\Gamma)+
\epsilon T(\Gamma),
\]

where:

- \(L\) is path length;
- \(K\) penalizes abrupt curvature or jerk;
- \(O\) penalizes off-manifold travel;
- \(U\) accounts for uncertainty or potential barriers;
- \(T\) is expected token/compute cost.

The shortest geometric route need not be the best route. The planner seeks a low-cost *admissible* path.

### 6.2 Multiobjective routes

Language tasks often contain multiple destinations rather than one. The planner can decide an order subject to dependencies. If a proof requires lemmas \(g_1\) and \(g_2\) before conclusion \(g_3\), then the route problem includes

\[
g_1\prec g_3,\qquad g_2\prec g_3.
\]

The atlas can then prefer an ordering that minimizes semantic detour and avoids abrupt topic transitions.

### 6.3 Novelty is not temperature

A route can be novel even when every token on it is individually ordinary. Let \(\rho(\Gamma)\) denote historical trajectory density. A controlled novelty term can reward low-density but still supported corridors. This differs from increasing decoding temperature, which makes locally unlikely tokens more probable without explicitly seeking a globally new conceptual path.

## 7. From route to tokens: the Semantic Servo

The planner operates in a continuous or graph-based semantic space; the language model emits discrete tokens. The missing bridge is an inverse dynamics controller.

### 7.1 Baseline: semantic model predictive control

The least invasive implementation requires no hidden-state modification. At state \(q_t\), sample short candidate continuations \(c_1,\ldots,c_N\). Embed each continuation and score the resulting semantic path by

\[
R(c_i)=
\lambda_1\,\text{progress}(c_i,g)
-\lambda_2\,\text{curvature}(c_i)
-\lambda_3\,\text{offmanifold}(c_i)
+\lambda_4\,\log P_M(c_i).
\]

Choose the best candidate, execute only a short prefix, observe the new state, and replan. This is semantic Model Predictive Control (MPC).

MPC is expected to cost *more* compute than ordinary generation because discarded rollouts are evaluated. Its purpose is to establish **controllability** before making efficiency claims.

### 7.2 Future semantic head

Let \(h_{\ell,t}\) be a hidden state at layer \(\ell\). Train a lightweight predictor

\[
F_H(h_{\ell,t})\approx q_{t+H}-q_t.
\]

This tests whether the model's current activation contains enough information to predict semantic displacement over horizon \(H\).

For desired displacement \(\Delta q^*\), the control error is

\[
e=\Delta q^*-F_H(h_{\ell,t}).
\]

### 7.3 Semantic Jacobian

The local sensitivity

\[
J^{sem}_{\ell,H}=\frac{\partial F_H}{\partial h_{\ell,t}}
\]

answers a precise control question: how does a small change in the current hidden state change predicted semantic motion over horizon \(H\)? A regularized local intervention can solve

\[
J^{sem}\delta h\approx e.
\]

One minimum-norm form is

\[
\delta h=(J^{sem})^\top(J^{sem}(J^{sem})^\top+\lambda I)^{-1}e.
\]

The intervention is then

\[
h'_{\ell,t}=h_{\ell,t}+\alpha\delta h.
\]

This is a control-theoretic use of a Jacobian; it does **not** imply that the LLM internally computes Jacobians.

### 7.4 Relation to the Jacobian Lens

Gurnee et al. (2026) introduced the Jacobian Lens and identified a J-space of verbalizable internal representations that participates in reasoning, report, and future planning. Their experiments show that interventions on future-oriented representations can alter earlier lexical choices used to realize a later target. This is closely related to the control problem here: a semantic destination may constrain intermediate generation without specifying each token.

The proposed Semantic Jacobian differs in its output space. The Jacobian Lens asks, approximately, which verbalizable content an internal state is disposed to produce. We ask how current hidden state perturbations change a *future position in an external semantic reference frame*. The experiments will test whether the two spaces are practically alignable or merely conceptually adjacent.

### 7.5 Closed-loop control

A stable controller should intervene minimally. One cost is

\[
\mathcal L=
\|q_{t+H}-q^*_{t+H}\|^2
+\beta D_{KL}(P_{steered}\|P_{base})
+\gamma\|\delta h\|^2
+\eta D(\Gamma,\Gamma^*).
\]

When the model is already following the desired route, the optimal control should approach zero. The system therefore behaves as a servo: observe, compute route error, apply a small correction, generate, and observe again.

## 8. Can the atlas be compiled from weights?

### 8.1 Static structure from the output head

The atlas need not be learned solely by walking every possible token sequence. Consider the final linear map

\[
\ell=W_Uh
\]

from final hidden state to logits. A truncated singular value decomposition

\[
W_U\approx U_k\Sigma_kV_k^\top
\]

defines a reduced coordinate

\[
z=V_k^\top h
\]

and approximate logits

\[
\ell\approx U_k\Sigma_k z.
\]

If the reduced subspace preserves top-k lexical structure, it forms a direct algebraic bridge from compact latent coordinates to token preferences. This does not by itself recover context-dependent transformer dynamics, but it is a concrete test of how much lexical geometry is exposed by the weights before autoregressive exploration.

The same idea can be extended cautiously to MLP and attention matrices, whose singular directions may expose functionally coherent subspaces. The hypothesis is not that one SVD reveals the whole semantic atlas, but that a useful **static base map** can be extracted from weights and corrected by relatively sparse dynamic measurements.

### 8.2 Local dynamic operators

Within a sufficiently small semantic cell \(c\), approximate the dynamics by

\[
q_{t+1}\approx A_cq_t+B_cu_t+b_c.
\]

If this approximation remains valid over multiple steps, then coarse planning can use operator composition rather than lexical simulation:

\[
q_{t+n}\approx A_c^nq_t+\sum_{j=0}^{n-1}A_c^jb_c.
\]

This is the strongest efficiency hypothesis in the programme. It would allow the planner to jump across semantic time at coarse resolution and invoke token-level generation only when required. It is also the easiest hypothesis to falsify if local linear models rapidly lose predictive accuracy.

## 9. Experimental programme

The experiments are intentionally staged so that failure at one level does not contaminate conclusions at another.

### 9.1 Models

The initial toy pair is:

- **Qwen3-0.6B** as an open-weight generator;
- **Qwen3-Embedding-0.6B** as the semantic observer.

The embedding model is built on the same Qwen3 family, has 0.6B parameters, 28 layers, and supports user-selected output dimensionality from 32 to 1024 [Zhang et al., 2025]. The first canonical SRF dimension is \(k=64\).

A same-family pair is a convenience for the toy study, not evidence of generality.

### 9.2 Experiment A: reference frame and observational atlas

Construct a deterministic 64-dimensional simplex SRF with 65 quasars. Freeze a row-paired calibration set across a reference observer and at least one independent transfer observer. Derive canonical calibration targets once from the reference observer, fit each transfer observer by paired Procrustes, and reserve separate held-out texts for the identifiability test. Then embed the frozen trajectory corpus, segment trajectories at multiple horizons, and build a graph of semantic cells and transitions.

Primary questions:

- Do independently fitted observers agree on held-out canonical vectors and quasar coordinates?
- Does that agreement collapse when calibration correspondences are shuffled?
- Does the frame preserve useful local geometry?
- Are trajectory measures stable across reasonable chunk sizes?
- Do repeated prompts expose consistent corridors and basin-like regions?

### 9.3 Experiment B: MPC navigation

For origin/goal pairs and multi-waypoint tasks, compare:

1. base generation;
2. explicit goal prompting;
3. nearest-neighbor semantic reranking;
4. semantic MPC;
5. MPC without curvature penalty;
6. MPC without off-manifold penalty.

The main endpoint is `success@budget`, accompanied by path length, curvature, revisits, language-model likelihood, and total compute including discarded rollouts.

A result in which MPC reaches goals more reliably but consumes substantially more compute supports controllability but **not** efficiency.

### 9.4 Experiment C: Semantic Servo

Collect hidden states and future SRF displacements, train \(F_H\), and test whether closed-loop Jacobian steering can follow the same routes with fewer discarded generations.

Compare against static activation addition and random control vectors with matched norm. Measure semantic route error, KL drift, control energy, output quality, token count, and total runtime.

### 9.5 Experiment D: compiled atlas

Decompose the output head at multiple ranks and measure:

- top-k logit overlap;
- KL between full and low-rank output distributions;
- neighborhood preservation in lexical space;
- correlation between compiled and empirical atlas transitions.

Then add a sparse set of local Jacobians/activations and measure the marginal improvement. Random low-rank bases are required controls.

### 9.6 Reasoning benchmark

A later toy benchmark uses tasks with known decomposable intermediate objectives. An oracle route may be supplied **only** to test route execution. The discovery of the route and the execution of the route are separate problems.

Conditions include:

- base model;
- natural-language plan;
- semantic route without textual subgoals;
- semantic servo.

Evaluate correctness under progressively smaller token budgets. A result where semantic routing preserves accuracy at lower token budgets would support efficiency in *token use*. FLOP or latency savings require separate measurement.

## 10. Metrics

### 10.1 Semantic Path Efficiency

Let \(L^*\) be the estimated minimum admissible route length and \(L\) the realized path length. Define

\[
SPE=\frac{L^*}{L}.
\]

The value is meaningful only relative to a declared atlas and path-cost definition; it is not a universal measure of intelligence.

### 10.2 Tokens per useful semantic progress

If \(\Delta^+_t\) is semantic displacement projected onto locally useful route progress, define

\[
TPSP=\frac{N_{tokens}}{\sum_t \Delta^+_t}.
\]

This is intended to detect verbose motion that consumes tokens without approaching required waypoints.

### 10.3 Reachable volume

For fixed horizon and budget, estimate the volume or graph coverage of \(R_M(q,H,B)\). Comparing reachable sets with and without steering tests whether the controller expands practical capability or merely changes style.

### 10.4 Naturalness and safety constraints

Route success must be reported alongside:

- perplexity or base-model log-likelihood;
- KL drift;
- semantic discontinuity/curvature;
- grammaticality or independent quality evaluation;
- factual correctness where applicable;
- off-manifold diagnostics;
- intervention norm.

A controller that reaches a target by destroying language quality has failed.

## 11. Falsification criteria

The programme is useful only if its claims can fail independently.

### H1 — Trajectory geometry

**Claim:** trajectory features add predictive information beyond endpoint similarity.

**Fails if:** curvature/history features do not improve future-state prediction or conversation classification over matched embedding baselines.

### H2 — Artificial reference frame

**Claim:** fixed quasar geometry plus paired empirical calibration can resolve enough cross-model gauge freedom to preserve navigation-relevant structure.

**Fails if:** independently fitted observers disagree materially on held-out canonical coordinates, if shuffled correspondences perform similarly to correct correspondences, or if the transformation introduces material distortion relative to dimensionality-matched native-space baselines.

### H3 — Atlas approximation

**Claim:** local dynamics can be compressed into reusable cells/operators.

**Fails if:** atlas prediction errors grow too quickly for route planning, or the atlas must approach 1:1 lexical resolution almost everywhere.

### H4 — Navigability

**Claim:** planned routes improve semantic goal attainment while preserving naturalness.

**Fails if:** gains disappear against equivalent prompting/reranking or depend on unnatural output.

### H5 — Efficiency

**Claim:** atlas-based control can reduce resource use for equal or better outcomes.

**Fails if:** token reductions are offset by greater total FLOPs/latency, or quality declines at matched compute.

### H6 — Weight compilation

**Claim:** a useful fraction of atlas structure can be extracted from weights before exhaustive exploration.

**Fails if:** low-rank or weight-space structure does not predict empirical transitions better than random baselines after controlling for dimension.

## 12. Related work and boundaries

The proposal sits at the intersection of several established research lines and should not be interpreted as claiming invention of their components.

**Relative representations.** Moschella et al. (2022) showed that representing samples by similarity to fixed anchors can create invariance to latent-space transformations and enable communication across latent spaces. The SRF adopts the relative-coordinate motivation but separates artificial landmark geometry from semantic anchoring: paired calibration examples align each observer to one frozen target cloud, after which artificial quasars provide a shared metrological basis.

**Text geometry.** Grover et al. (2026) propose a text-native curvature signal derived from left/right contextual beliefs and show practical uses in compression and routing. Semantic Atlas instead treats an entire generated discourse as a trajectory and asks whether trajectory geometry is useful for planning and control.

**Activation steering.** Static steering vectors, context-dependent Steering Vector Fields [Li et al., 2026], and Energy Landscape Steering [Jiang et al., 2026] demonstrate that hidden-state interventions can alter model behavior. Semantic Atlas makes the desired control signal a route in an external map rather than a single attribute direction.

**Jacobian Lens / J-space.** Gurnee et al. (2026) use Jacobian-based interpretability to expose verbalizable internal representations participating in reasoning and future planning. The present Semantic Jacobian proposal uses local sensitivities to convert route error into a hidden-state intervention; whether that controller aligns with J-space is an empirical question.

**Semantic tokenization.** The companion paper *Semantic Tokenization Transformers* in this repository proposes replacing BPE-scale modeling with quantized semantic chunks. Semantic Atlas does not require retraining a transformer on semantic codes. Instead it asks whether an existing model's behavior can be represented and navigated at multiple semantic scales while preserving the original model as a lexical engine.

**Reduced-order and predictive-state models.** The atlas shares the broad ambition of representing complex dynamics using compact state variables sufficient for prediction and control. Its distinctive empirical question is whether autoregressive language-model behavior admits such a reduced semantic dynamics at useful horizons.

## 13. Limitations

The proposal has several failure modes that must be taken seriously.

First, embedding geometry may be a poor proxy for reasoning state. A semantic observer can smooth away distinctions that are computationally essential.

Second, trajectories may be highly observer-dependent. A useful atlas for one embedding model may not transfer to another despite calibration.

Third, high-dimensional spaces can make density and distance estimates unstable. Apparent basins or corridors may be artifacts of projection or sampling.

Fourth, lexical generation contains syntactic and pragmatic constraints that a coarse semantic route does not represent. A route can be semantically plausible yet linguistically unrealizable from the current context.

Fifth, the atlas itself may be expensive to construct. Offline cost is justified only if amortized over sufficient queries or if weight-space compilation substantially reduces sampling.

Sixth, steering can push hidden states away from the model's trained manifold, increasing hallucination or degrading safety behavior. The minimum-intervention constraint is therefore not optional.

Seventh, efficiency must be measured end-to-end. Reducing visible reasoning tokens while adding heavy hidden-state optimization does not constitute computational savings.

Finally, a successful toy experiment on a same-family 0.6B model pair would establish feasibility only. Claims about frontier systems, universal semantic coordinates, or substantial production savings require independent replication.

## 14. Discussion: maps, engines, and semantic computation

The Semantic Atlas framework deliberately assigns different jobs to different representations.

The language model is the **microscopic engine**: it contains the detailed conditional machinery required to produce grammatical, context-sensitive language.

The SRF is the **geodetic system**: artificial quasars define the external geometry, while shared calibration correspondences determine how each model is oriented within it. The sky can be invented; making two telescopes agree about where that sky is remains an empirical calibration problem.

The atlas is the **macroscopic map**: it summarizes which regions exist, how they connect, what costs are associated with movement, and where the map is uncertain.

The planner is the **navigator**: it chooses a route among multiple semantic goals.

The Semantic Servo is the **control loop**: it converts route error into the smallest practical intervention on generation.

This separation suggests a potentially useful computational pattern. Long-range planning may not need lexical resolution. If a coarse atlas can predict that a reasoning process should move from region \(A\) through \(B\) and \(C\) to \(D\), then the full transformer need not necessarily spend tokens exploring every alternative path. It can instead be asked to materialize the locally appropriate segment of a route already planned at a coarser scale.

The strongest version of the hypothesis is therefore not that semantic embeddings are a better tokenizer. It is that **semantic planning and lexical realization may operate efficiently at different resolutions**.

## 15. Conclusion

This paper proposes a research programme for turning language-model semantics into a navigable dynamical object. Artificial quasars provide a fixed external geometry and paired calibration supplies its semantic orientation; multiscale trajectories provide the moving object; the Semantic Atlas records density, potential, transition, control cost, and reachability; route planning chooses admissible low-cost paths; and the Semantic Servo attempts to realize those paths through local generation control.

The framework is intentionally more ambitious than the evidence currently supports. Its value therefore depends on disciplined decomposition. A useful SRF can exist even if weight compilation fails. Semantic MPC can demonstrate controllability even if it is computationally inefficient. A Semantic Servo can reduce wasted rollouts without proving that hidden reasoning is universally lower-dimensional. A compiled output-head map can preserve lexical geometry without reproducing transformer dynamics.

The next step is a small, reproducible experiment designed to kill weak versions of the idea quickly. If the atlas cannot preserve local trajectory geometry, the programme should stop. If it can, the next question is whether route planning changes generation in a predictable way. Only after those two results should the programme test whether planning can save tokens or compute.

The intended end state is therefore not a map the size of Borges's empire. It is a map that remains coarse enough to be cheap, becomes detailed enough to act only where needed, and tells a language model not what words to say, but where to go.

---

## References

- Gurnee, W., Sofroniew, N., Pearce, A., et al. (2026). **Verbalizable Representations Form a Global Workspace in Language Models.** Transformer Circuits Thread / arXiv:2607.15495. https://transformer-circuits.pub/2026/workspace/index.html
- Grover, K., Zeng, H., Xia, Y., Faloutsos, C., & Gordon, G. J. (2026). **Text Has Curvature.** arXiv:2602.13418. https://arxiv.org/abs/2602.13418
- Jiang, E. H., Ou, W., Liu, R., et al. (2026). **Mitigating Over-Refusal in Aligned Large Language Models via Inference-Time Activation Energy.** ACL 2026. https://aclanthology.org/2026.acl-long.1759/
- Li, J., Li, Y., & Huang, K.-H. (2026). **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models.** arXiv:2602.01654. https://arxiv.org/abs/2602.01654
- Moschella, L., Maiorca, V., Fumero, M., Norelli, A., Locatello, F., & Rodolà, E. (2022). **Relative representations enable zero-shot latent space communication.** arXiv:2209.15430. https://arxiv.org/abs/2209.15430
- Zhang, Y., Li, M., Long, D., et al. (2025). **Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models.** arXiv:2506.05176. https://arxiv.org/abs/2506.05176

## Issue map

This paper is developed under #260. Prior-art delimitation is #261; multiscale trajectory formalization is #262; quasar/SRF design is #263; atlas/gravity/reachability is #264; Semantic Servo is #265; the observational atlas implementation is #266; MPC navigation is #267; Jacobian/servo efficiency is #268; weight-space compilation is #269; and final empirical integration is #270.
