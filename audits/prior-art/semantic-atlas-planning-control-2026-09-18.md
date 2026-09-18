---
type: "Audit Report"
title: "Semantic Atlas — latent planning, reachability and closed-loop semantic control prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of Semantic Atlas trajectory dynamics, reachability, latent/world-model planning, closed-loop semantic steering, multiscale planning, and efficiency claims."
tags: [semantic-atlas, prior-art, latent-planning, world-models, semantic-control, reachability, model-predictive-control, latent-reasoning]
timestamp: 2026-09-18T11:02:00-04:00
---

# Semantic Atlas — latent planning, reachability and closed-loop semantic control prior-art audit — 2026-09-18

> **Status:** second external prior-art pass over the Semantic Atlas programme, but the first temporal audit centered specifically on the core **atlas → planning → closed-loop control → efficiency** claims in [`semantic_atlas.md`](../../semantic_atlas.md). It extends rather than replaces [`audits/2026-08-09-semantic-atlas-frontier-scan.md`](../2026-08-09-semantic-atlas-frontier-scan.md), whose strongest searches concerned alignment, steering baselines, inverse-atlas retrieval, Jacobian Lens, and termination controls. This audit does **not** establish exhaustive novelty, patent novelty, causal dependence, copying, or priority beyond the bounded public record inspected here.

## 1. Claims audited

The current paper separates several hypotheses; this audit focuses on the five that form its navigational spine and one combination-level claim:

- **C1 — semantic trajectory dynamics:** language/reasoning generation can be treated as a trajectory in a continuous semantic or representation space, and trajectory features such as direction, velocity, curvature, and history can add predictive or control-relevant information beyond the current point alone;
- **C2 — reusable semantic dynamics map:** repeated trajectories can support a reusable reduced model/atlas containing local transition dynamics and uncertainty, with explicit notions such as reachable sets, directed navigation cost, corridors, barriers, or escape/control cost;
- **C3 — route planning plus closed-loop semantic control:** a planner can choose a semantic path or setpoint sequence and an online controller can repeatedly observe model state, compute route/setpoint error, intervene, and replan/track rather than relying only on open-loop prompting or a static steering vector;
- **C4 — multiresolution separation of planning and lexical realization:** long-range reasoning/planning can occur at a coarser latent/semantic resolution while text is generated or decoded only where lexical realization is needed;
- **C5 — efficiency:** the coarse semantic/latent planning layer can reduce tokens, model queries, latency, or total compute at matched task quality, provided all planning/control overhead is counted;
- **C6 — full Semantic Atlas conjunction:** a **frozen externally calibrated semantic frame** + a reusable empirical map learned from model trajectories + explicit transition/reachability/control-cost structure + route planning + closed-loop realization of the route by the original language model + end-to-end efficiency accounting.

This audit intentionally does **not** reopen Procrustes/multi-model alignment, inverse-atlas retrieval, or the Jacobian-Lens distinction already treated in earlier repository audits unless they are needed to delimit C6.

## 2. Temporal reconstruction of our claims

### 2.1 Relevant cutoff: 2026-08-09 00:15:15 UTC

The current file date and the later merge are not the priority date. The earliest verified public GitHub record located for the claims above is [PR #271](https://github.com/franklinbaldo/papers/pull/271), **opened 2026-08-09 00:15:15 UTC**.

The PR's initial public diff already contained all of the load-bearing ideas audited here. In particular, the paper asked whether:

- a corpus of semantic trajectories can become a reusable map of corridors, barriers, attractor-like regions, and reachable destinations;
- a desired semantic route can be realized by steering a language model without prescribing the exact words;
- long semantic distance can be planned at a coarser resolution than token-by-token exploration;
- a route planner can choose low-cost paths and a Semantic Servo can convert route error into generation control;
- such navigation can reduce token or compute cost;
- local semantic dynamics may be approximated by reduced operators rather than full lexical simulation.

The PR body likewise already listed `atlas fields and directed reachability`, `semantic MPC and closed-loop Servo`, and `token savings versus end-to-end compute savings` as separate programme claims. This audit therefore uses **2026-08-09 00:15:15 UTC** as the conservative public cutoff for **C1–C6**.

Later corrections to SRF identifiability, causal Jacobian calibration, and controlled dynamics narrowed or repaired the programme but did not create the broad atlas/planning/control claims from scratch. Where a future audit examines a later, more specific implementation claim, that later claim must receive its own cutoff.

## 3. Search protocol

The search was claim-led rather than title-led. It used modern and historical terminology around latent reasoning, control, planning, world models, reachability, continuous semantic state, multiscale planning, and reasoning-trajectory geometry.

Sources consulted included arXiv primary records/full text, publisher/preprint pages, project pages, GitHub-linked code where surfaced, and targeted web discovery. Primary arXiv version history was used whenever later revisions could otherwise create a false date.

Representative queries included:

- `semantic trajectory LLM reasoning latent path planning`
- `language generation trajectory continuous semantic space control`
- `reachability controllability meaning state large language model`
- `closed-loop activation steering semantic setpoint LLM`
- `model predictive control semantic space language model`
- `latent world model chain of thought planning semantic space`
- `reasoning trajectory latent dynamics world model LLM`
- `multi-scale latent planning language model reasoning`
- `continuous latent reasoning fewer tokens planning`
- `global semantic plan continuous space autoregressive language model`
- `hierarchical planning latent world model multiscale compute`
- `semantic step prediction reasoning trajectory multi-step latent forecasting`
- exact-title / `Semantic Atlas` / `Franklin Baldo` post-cutoff overlap searches.

Negative findings are bounded by those sources and queries. “Not located” below is not proof of nonexistence.

## 4. Pre-cutoff findings

### 4.1 Soatto et al. (2023): meaning-space reachability and controllability already exist as explicit LLM objects

**Work:** Stefano Soatto, Paulo Tabuada, Pratik Chaudhari, Tian Yu Liu, **“Taming AI Bots: Controllability of Neural States in Large Language Models.”** arXiv:2305.18449.

- arXiv v1: **2023-05-29 03:58:33 UTC**;
- <https://arxiv.org/abs/2305.18449>;
- status: public arXiv preprint.

The paper defines a space of meanings, studies the subset reachable by an LLM under prompts, introduces a stronger notion of almost-certain reachability, proves controllability results under its assumptions, and discusses avoiding undesirable regions before their boundaries are crossed.

**Compared claims:** C2, C3.

**Classification:** `prior_art` for the broad ideas of **semantic/meaning-space reachability and controllability** in LLMs; `partial_prior_art` for C2 because it does not construct the Semantic Atlas's empirical map with density, local dynamics, uncertainty, directed route costs and control-cost fields.

**Material consequence:** `reachable set` and semantic controllability cannot be treated as Semantic Atlas inventions. The residual question is whether an empirically calibrated atlas provides a useful *operational map and planner* for those notions.

### 4.2 Cheng, Baroni & Amo Alonso (2024): language generation as a continuous semantic trajectory under optimal control

**Work:** Emily Cheng, Marco Baroni, Carmen Amo Alonso, **“Linearly Controlled Language Generation with Performative Guarantees.”** Later revised as **“LiSeCo: Linear Semantic Control for Language Generation.”** arXiv:2405.15454.

- **v1: 2024-05-24 11:30:44 UTC**;
- <https://arxiv.org/abs/2405.15454v1>;
- later revisions in 2025/2026 do not change the relevant temporal classification.

The v1 abstract already states that natural-language generation traces a trajectory in a continuous semantic space realized by hidden activations, then applies a control-theoretic intervention to dynamically steer that trajectory away from undesired meanings and into an allowed semantic region.

**Compared claims:** C1, C3.

**Classification:** `prior_art` for the broad formulations **“language generation is a semantic-space trajectory”** and **“control theory can online-steer that trajectory toward/away from semantic regions.”** It is `partial_prior_art` for C3 because it does not plan and track an independently chosen multi-waypoint route in a reusable atlas.

**Material consequence:** Semantic Atlas must not carry novelty on trajectory-as-control-system or online semantic steering alone. Its control claim must stay at the stricter route-tracking/atlas integration boundary.

### 4.3 Coconut (2024): reasoning outside language space with fewer thinking tokens

**Work:** Shibo Hao et al., **“Training Large Language Models to Reason in a Continuous Latent Space.”** arXiv:2412.06769.

- arXiv v1: **2024-12-09 18:55:56 UTC**;
- <https://arxiv.org/abs/2412.06769>.

Coconut feeds the model's hidden state back as the next input embedding instead of verbalizing each reasoning step. It explicitly argues that language space may be inefficient for reasoning, reports fewer thinking tokens in some tasks, and observes latent states that can retain multiple candidate next steps rather than committing immediately to one textual path.

**Compared claims:** C4, C5.

**Classification:** `prior_art` for the generic proposition that useful reasoning may occur in a non-lexical continuous state with fewer visible reasoning tokens; `partial_prior_art` for the Atlas claim that an external reusable semantic map can plan such motion.

### 4.4 Token Assorted (2025): mixed latent/text resolution already compresses reasoning traces

**Work:** DiJia Su et al., **“Token Assorted: Mixing Latent and Text Tokens for Improved Language Model Reasoning.”** arXiv:2502.03275.

- arXiv v1: **2025-02-05 15:33:00 UTC**;
- <https://arxiv.org/abs/2502.03275>.

The method compresses parts of explicit reasoning into learned latent discrete tokens while retaining text elsewhere, motivated directly by the cost of language tokens that serve coherence rather than core reasoning.

**Compared claims:** C4, C5.

**Classification:** `partial_prior_art` for the multiresolution/efficiency idea. It does not provide a navigational atlas, route planner, reachability field, or closed-loop trajectory controller.

### 4.5 Hu, Robey & Liu (2025): multi-turn dialogue as a semantic dynamical system under feedback safety control

**Work:** Hanjiang Hu, Alexander Robey, Changliu Liu, **“Steering Dialogue Dynamics for Robustness against Multi-turn Jailbreaking Attacks.”** arXiv:2503.00187.

- arXiv v1: **2025-02-28 21:10:03 UTC**;
- <https://arxiv.org/abs/2503.00187>.

The paper models dialogue evolution using a state-space representation and applies safe-control machinery to prevent context drift into unsafe regions over multiple turns.

**Compared claims:** C1, C3.

**Classification:** `partial_prior_art` for treating language interaction as controlled semantic dynamics and for feedback over a trajectory. The objective is safety invariance rather than route planning through a learned semantic atlas.

### 4.6 Feedback/PID activation steering (2025): closed-loop semantic steering is independently occupied

**Work:** Dung V. Nguyen et al., **“Activation Steering with a Feedback Controller.”** arXiv:2510.04309.

- arXiv v1: **2025-10-05 18:05:28 UTC**;
- <https://arxiv.org/abs/2510.04309>.

The work interprets common activation steering as proportional control and introduces PID steering: proportional alignment to semantic directions, accumulated error correction, and derivative damping in a closed-loop controller.

**Compared claims:** C3.

**Classification:** `prior_art` for generic **closed-loop feedback control of LLM activations toward semantic directions**; `partial_prior_art` for C3 because it does not track a sequence of externally planned atlas waypoints.

### 4.7 iCLP (2025): compact latent plans guide language-space reasoning

**Work:** Sijia Chen, Di Niu, **“iCLP: Large Language Model Reasoning with Implicit Cognition Latent Planning.”** arXiv:2512.24014.

- arXiv v1: **2025-12-30 06:19:04 UTC**;
- <https://arxiv.org/abs/2512.24014>.

The system distills explicit plans into compact vector-quantized latent plans and then trains the LLM to plan in latent space while reasoning in language space, reporting accuracy and efficiency gains.

**Compared claims:** C4, C5.

**Classification:** `partial_prior_art` for separation between a compact planning representation and lexical reasoning/realization, and for the efficiency claim.

### 4.8 PLaT (2026): latent planning states separated from textual realization

**Work:** Jiecong Wang, Hao Peng, Chunyang Liu, **“Latent Chain-of-Thought as Planning: Decoupling Reasoning from Verbalization.”** arXiv:2601.21358.

- arXiv v1: **2026-01-29 07:38:18 UTC**;
- <https://arxiv.org/abs/2601.21358>.

PLaT explicitly models reasoning as a trajectory of latent planning states with a separate decoder that grounds those thoughts into text when needed. Its stated objective is to decouple reasoning from verbalization and avoid the cost/path constraints of discrete token space.

**Compared claims:** C1, C4, C5.

**Classification:** `prior_art` for the broad C4 proposition that planning may occur in latent states while textual realization is a separate operation; `partial_prior_art` for C1/C5 and for the full Atlas conjunction.

### 4.9 ATP-Latent (2026): active planning over latent-token representations with token savings

**Work:** Zhi Zheng, Wee Sun Lee, **“Beyond Imitation: Reinforcement Learning for Active Latent Planning.”** arXiv:2601.21598.

- arXiv v1: **2026-01-29 12:07:16 UTC**;
- <https://arxiv.org/abs/2601.21598>.

The work is explicit that latent reasoning should be an **active planning** problem over the representation space of latent tokens. It uses RL over a smoother latent space and reports both accuracy gains and token reduction.

**Compared claims:** C4, C5.

**Classification:** `prior_art` for generic active latent planning as a means to improve token efficiency; `partial_prior_art` for the external-map / route-planning architecture.

### 4.10 STAR-LDM (2026): global semantic planning before committing to discrete text

**Work:** Justin Lovelace et al., **“Stop-Think-AutoRegress: Language Modeling with Latent Diffusion Planning.”** arXiv:2602.20528.

- arXiv v1: **2026-02-24 04:09:31 UTC**;
- <https://arxiv.org/abs/2602.20528>.

STAR-LDM inserts a latent-diffusion “thinking” phase into autoregressive generation. The model refines a semantic plan in continuous space before continuing token generation, expressly allowing global planning before commitment to discrete tokens.

**Compared claims:** C4, C5.

**Classification:** `prior_art` for the broad “semantic/continuous planning first, lexical commitment later” claim; `partial_prior_art` for C5 and C6 because it lacks the reusable trajectory atlas and explicit reachability/control-cost map.

### 4.11 Hierarchical latent world-model planning (2026): multiscale latent dynamics + long-horizon planning + compute reduction already exist outside language

**Work:** Wancong Zhang et al., **“Hierarchical Planning with Latent World Models.”** arXiv:2604.03208.

- arXiv v1: **2026-04-03 17:32:36 UTC**;
- <https://arxiv.org/abs/2604.03208>;
- domain: embodied/robotic control.

The system learns latent world models at multiple temporal scales and performs hierarchical planning across them, explicitly to handle long horizons while reducing inference-time planning complexity; it reports up to 4× less planning compute in tested environments.

**Compared claims:** C2, C4, C5.

**Classification:** `adjacent_prior_work` for the language-specific claims, but `prior_art` for the general control idea “multiscale latent dynamics + hierarchical long-horizon planning can reduce planning complexity.”

**Material consequence:** the multiresolution Atlas rationale should be framed as a language-model instantiation/test of a broader world-model planning strategy, not as a new general control principle.

### 4.12 Grounded World Model (2026): MPC already plans in a vision-language-aligned latent semantic space

**Work:** Quanyi Li et al., **“Grounded World Model for Semantically Generalizable Planning.”** arXiv:2604.11751.

- arXiv v1: **2026-04-13 17:25:41 UTC**;
- <https://arxiv.org/abs/2604.11751>;
- domain: visuomotor control.

The method learns a world model in a vision-language-aligned latent space and uses MPC to score future action outcomes by embedding similarity to a natural-language task instruction.

**Compared claims:** C2, C3.

**Classification:** `adjacent_prior_work` for Semantic Atlas, but an important pre-cutoff precedent for **semantic latent-space world-model + MPC** as a control architecture.

### 4.13 Semantic Step Prediction (2026): multi-step forecasting of LLM reasoning trajectories is already an explicit empirical target

**Work:** Yidi Yuan, **“Semantic Step Prediction: Multi-Step Latent Forecasting in LLM Reasoning Trajectories via Step Sampling.”** arXiv:2604.18464.

- arXiv v1: **2026-04-20 16:19:02 UTC**;
- <https://arxiv.org/abs/2604.18464>.

The paper regularizes hidden-state reasoning trajectories and directly measures multi-step latent prediction. It reports that step-boundary models yield much more predictable multi-step trajectories than frozen baselines and studies the curvature/smoothness of the resulting latent manifold.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for the generic claim that **multi-step future semantic/latent motion of reasoning trajectories is a measurable prediction problem**; `partial_prior_art` for an Atlas of reusable local operators.

### 4.14 A-LQR (2026): locally linear LLM dynamics + Jacobians + closed-loop optimal control to semantic setpoints

**Work:** Julian Skifstad, Xinyue Annie Yang, Glen Chou, **“Local Linearity of LLMs Enables Activation Steering via Model-Based Linear Optimal Control.”** arXiv:2604.19018.

- arXiv v1: **2026-04-21 03:09:46 UTC**;
- <https://arxiv.org/abs/2604.19018>.

This is a particularly close collision with the local-control side of the Servo. The authors model LLM inference as a linear time-varying dynamical system, estimate layer-wise local dynamics/Jacobians, and use an LQR feedback controller to track semantic setpoints in closed loop with low overhead.

**Compared claims:** C2, C3.

**Classification:** `prior_art` for local linear semantic dynamics used for **closed-loop setpoint tracking**; `partial_prior_art` for the Atlas Servo because the Semantic Atlas proposes externally planned multi-step semantic routes in a calibrated state space rather than one behavior/setpoint controller across layers.

**Material consequence:** “future semantic head + Jacobian + feedback control” cannot carry broad novelty. The defensible comparison must be route-following against strong LQR/PID/local-field controllers under matched objectives and intervention budget.

### 4.15 Thoughts-as-Planning (2026): the closest pre-cutoff collision with the Atlas planning spine

**Work:** Dong Liu, Yanxuan Yu, Ying Nian Wu, **“Thoughts-as-Planning: Latent World Models for Chain-of-Thoughts Optimization via Reinforcement Planning.”** arXiv:2605.28842.

- arXiv v1: **2026-04-27 08:18:12 UTC**;
- <https://arxiv.org/abs/2605.28842>;
- status: public arXiv preprint.

This is the strongest newly located collision relative to the 2026-08-09 frontier scan. The paper:

1. formalizes reasoning-chain optimization as sequential decision-making over a **latent semantic space**;
2. learns an explicit **latent world model** for reasoning-chain dynamics;
3. encodes reasoning-chain/response dynamics in a proximity-preserving embedding space;
4. plans over that model via model-based rollouts / RL;
5. supports **multi-scale** actions at token, step, and structural levels;
6. explicitly asks whether the learned world model can reduce LLM queries;
7. reports structured, reusable/transferable planning trajectories.

Its formal method includes a latent transition model \(\hat T(z,a)\), a utility predictor, and H-step model-based rollouts used to choose actions.

**Compared claims:** C2, C3, C4, C5, C6.

**Classification:** `prior_art` for the broad combination **“latent semantic dynamics/world model + multi-step planning over those dynamics + multiscale reasoning actions + efficiency objective”**; `partial_prior_art` for C6.

**Why it does not collapse the full Semantic Atlas claim:** Thoughts-as-Planning optimizes/edit reasoning chains in a task-conditioned latent world model. It does not, on the inspected record, build the same frozen cross-model calibrated SRF; define a reusable atlas with density, explicit directed reachability, escape/control-cost fields, and route geometry; or ask an online language generator to track an externally planned sequence of semantic waypoints with the same full end-to-end accounting.

**Material consequence:** the Semantic Atlas cannot safely claim novelty merely for learning semantic dynamics and planning through them. The paper now needs to be read as a stricter hypothesis about a **persistent navigational map and route-following interface**, not the invention of latent semantic planning.

## 5. Post-cutoff convergence

### 5.1 LeFlow (2026-08-25): reusable latent trajectory priors as amortized planning

**Work:** Hsiang-Wei Huang et al., **“LeFlow: Generative Latent Flow Planning for World Models.”** arXiv:2608.24855.

- arXiv v1: **2026-08-25 17:42:30 UTC**, after our 2026-08-09 cutoff;
- <https://arxiv.org/abs/2608.24855>;
- domain: goal-conditioned pixel control.

LeFlow learns a reusable prior over latent trajectories, generates a latent path from current state to goal, decodes transitions into actions, and uses the frozen world model for verification, reducing planning time by roughly an order of magnitude in reported tasks.

**Compared claims:** C2, C3, C5.

**Classification:** `later_independent` / domain-adjacent. Its visible lineage is the latent-world-model planning literature; no `Semantic Atlas` or `Baldo` reference was located in the inspected full text. This is not evidence of causal independence in the strong sense, only the best classification supported by the record.

### 5.2 A*-Thought-V2 (2026-09-07): later convergence on geometric reasoning trajectories and efficiency

**Work:** Xiaoang Xu et al., **“A*-Thought-V2: Efficient Latent Reasoning via Geometric Dynamics of LLM.”** arXiv:2609.07821.

- arXiv v1: **2026-09-07 17:56:20 UTC**, after our cutoff;
- <https://arxiv.org/abs/2609.07821>.

The paper models chain-of-thought as a hidden-state trajectory, uses local transition directions relative to the global question-to-solution direction, identifies exploration/convergence/refinement stages, and uses that geometry to decide which reasoning spans should remain explicit and which should be compressed into latent tokens. It reports shorter responses and improved accuracy-per-computation-unit.

Full-text searches in this run found no occurrence of `Semantic Atlas`, `Baldo`, or `Franklin`. The paper's visible lineage is A*-Thought plus established latent-reasoning/compression work.

**Compared claims:** C1, C4, C5.

**Classification:** `later_independent`, not `later_non_citing`. The chronological and conceptual overlap is real, but the work does not reproduce the Atlas/world-model/route-control conjunction, and the inspected citation lineage provides a straightforward independent route to its mechanism. Absence of a located citation is recorded only as a fact, not as evidence of derivation or appropriation.

## 6. Classification summary

| Claim | Status after this audit | Main temporal reason |
| --- | --- | --- |
| C1 semantic trajectory dynamics | `prior_art` at broad level | LiSeCo 2024; dialogue dynamics 2025; SSP 2026 |
| C2 semantic reachability / reusable dynamics | `partial_prior_art` | Soatto 2023 covers reachability; world-model/latent-dynamics literature covers reduced dynamics; full persistent Atlas object remains narrower |
| C3 route planning + closed-loop semantic control | `partial_prior_art` | feedback/PID, A-LQR, LiSeCo and semantic MPC precede cutoff; externally planned multi-waypoint Atlas route remains narrower |
| C4 coarse/latent planning separated from lexical realization | `prior_art` at broad level | Coconut 2024; iCLP/PLaT/ATP-Latent/STAR-LDM 2025–26 |
| C5 efficiency from latent/coarse planning | `prior_art` at broad level | Coconut, Token Assorted, ATP-Latent, latent world-model planning all predate cutoff |
| C6 full Semantic Atlas conjunction | `partial_prior_art`; no full pre-cutoff anticipation located in this run | Thoughts-as-Planning is the closest joint collision but lacks the same calibrated persistent map + reachability/cost fields + route-tracking interface |

The strongest epistemic update is therefore not that the Semantic Atlas is “already done,” nor that its components are untouched. It is that **most broad component claims are already occupied, including a surprisingly close pre-cutoff latent-world-model planning paper**. The scientific question must be pushed to the integrated map-and-controller layer.

## 7. Bounded negative result: what was not located

After the searches above, this run did **not** locate a pre-2026-08-09 work that combines all of the following in one LLM-generation system:

1. a frozen **externally calibrated** semantic coordinate frame intended to make the navigation state reproducible across specified observers;
2. a persistent empirical **map of free-generation trajectories** rather than only a task-specific latent policy/world model;
3. local transition prediction together with explicit **directed reachability / navigation cost / escape or control-cost** observables;
4. a planner that computes an ordered semantic route through that map;
5. a closed-loop generator that repeatedly observes its realised semantic state and tracks those **externally planned waypoints** while preserving lexical freedom;
6. an adaptive multiresolution boundary that decides when coarse semantic prediction is sufficient and when lexical/full-model resolution must be invoked;
7. an end-to-end comparison that charges all mapping, planning, discarded rollout, intervention, and lexical-generation compute.

This is a **bounded negative search result**, not a claim that no such work exists or that the conjunction is legally/scientifically novel in an exhaustive sense.

## 8. Experimental consequences

The old baseline ladder is no longer strong enough. A decisive Semantic Atlas experiment should compare against mechanisms that now occupy neighboring space:

1. ordinary autoregressive generation / prompting;
2. static and state-dependent activation steering;
3. **LiSeCo-like semantic-region control**;
4. **PID or A-LQR closed-loop semantic setpoint tracking**;
5. latent-planning baselines such as **PLaT / ATP-Latent / STAR-LDM** where a faithful implementation is feasible;
6. a **Thoughts-as-Planning-style learned latent world model** with matched transition-model capacity and planning horizon;
7. only then, the full Atlas condition with persistent route map, directed reachability/cost structure, external route planning, and Servo tracking.

For C5, token savings alone are insufficient because multiple prior systems already reduce visible reasoning length. Report at least:

- task success/quality at matched token budget;
- total model forward passes / LLM queries;
- planning-model FLOPs or measured latency;
- cost of building/amortizing the atlas;
- discarded rollouts;
- controller overhead;
- lexical generation cost.

A particularly clean falsifier is: **if a task-conditioned latent world model (Thoughts-as-Planning-like) or local closed-loop controller (A-LQR/PID-like) matches the full Atlas at equal total compute, then the persistent global map / route machinery has not demonstrated causal value.**

Conversely, the integrated claim gains support only if the persistent Atlas improves transfer to new goals/routes or reduces repeated planning cost **after** these stronger baselines and amortization costs are included.

## 9. Revision note relative to the 2026-08-09 frontier scan

The earlier frontier scan remains historically useful and should not be overwritten. This audit changes the epistemic state in four material ways:

1. it adds **Soatto et al. 2023** as direct antecedent for semantic reachability/controllability;
2. it adds **LiSeCo v1 2024** as direct antecedent for semantic trajectories under control;
3. it adds the 2024–2026 latent-planning line (Coconut, PLaT, ATP-Latent, STAR-LDM) as antecedent to coarse planning / lexical-realization separation and token-efficiency claims;
4. most importantly, it adds **Thoughts-as-Planning (2026-04-27)** as a pre-cutoff collision with the joint `latent semantic dynamics + learned world model + multi-scale planning + efficiency` spine.

Accordingly, future prose should avoid using “semantic planning,” “latent world model,” “trajectory control,” “reachability,” or “coarse planning before text” as standalone novelty hooks. The strongest remaining research bet is the **persistent calibrated atlas + explicit route/reachability/cost geometry + closed-loop waypoint tracking + amortized end-to-end efficiency** conjunction.

## 10. Sources and verification notes

Primary records used for temporal classification:

- Soatto et al. 2023 — <https://arxiv.org/abs/2305.18449>
- Cheng, Baroni & Amo Alonso 2024 v1 — <https://arxiv.org/abs/2405.15454v1>
- Hao et al. 2024 (Coconut) — <https://arxiv.org/abs/2412.06769>
- Su et al. 2025 (Token Assorted) — <https://arxiv.org/abs/2502.03275>
- Hu, Robey & Liu 2025 — <https://arxiv.org/abs/2503.00187>
- Nguyen et al. 2025 — <https://arxiv.org/abs/2510.04309>
- Chen & Niu 2025 (iCLP) — <https://arxiv.org/abs/2512.24014>
- Wang, Peng & Liu 2026 (PLaT) — <https://arxiv.org/abs/2601.21358>
- Zheng & Lee 2026 (ATP-Latent) — <https://arxiv.org/abs/2601.21598>
- Lovelace et al. 2026 (STAR-LDM) — <https://arxiv.org/abs/2602.20528>
- Zhang et al. 2026 (hierarchical latent world models) — <https://arxiv.org/abs/2604.03208>
- Li et al. 2026 (Grounded World Model) — <https://arxiv.org/abs/2604.11751>
- Yuan 2026 (Semantic Step Prediction) — <https://arxiv.org/abs/2604.18464>
- Skifstad, Yang & Chou 2026 (A-LQR) — <https://arxiv.org/abs/2604.19018>
- Liu, Yu & Wu 2026 (Thoughts-as-Planning) — <https://arxiv.org/abs/2605.28842>
- Huang et al. 2026 (LeFlow; post-cutoff) — <https://arxiv.org/abs/2608.24855>
- Xu et al. 2026 (A*-Thought-V2; post-cutoff) — <https://arxiv.org/abs/2609.07821>

The audit preserves exact v1 dates where they matter. Later revisions or publication dates were not allowed to move a pre-cutoff work into the post-cutoff category or vice versa.
