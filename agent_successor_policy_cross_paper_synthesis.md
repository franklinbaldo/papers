---
okf_version: "0.2"
title: "Agent Successor Policy — Cross-Paper Synthesis"
description: "Synthesis of architectural and experimental connections between ASP and the existing papers programme."
doc_type: "alignment-paper-note"
status: "draft"
---

# Agent Successor Policy — Cross-Paper Synthesis

Franklin Baldo  
Draft: 2026-08-16

Agent Successor Policy (ASP) did not arise in an empty research programme. Several papers already present in this repository contain mechanisms, distinctions, or experimental controls that sharpen ASP substantially. Conversely, ASP provides a recurring-agent testbed in which claims from those papers can be exercised over long-lived trajectories rather than isolated model calls.

This note records those connections while preserving claim boundaries. It does not collapse the papers into one theory. The objective is to identify reusable mechanisms, shared experiments, and places where one paper supplies a falsifier or constraint for another.

## 1. RL Relay Transducers: semantic recall is not functional choice

The closest pre-existing mechanism is `rl_relay_transducers.md`, especially its reward-conditioned retrieval design and the synthetic experiment under `experiments/reward_conditioned_retrieval/`.

That work explicitly separates:

```text
frozen semantic recall
        ↓
reward-conditioned functional ranking
        ↓
commit/reject action
```

This distinction should be imported into ASP.

The first version of semantic ASP can be written as:

```text
desired behavior vector
        ↓
nearest prompt in embedding space
        ↓
execute
```

but nearest semantic similarity need not imply highest downstream utility. Two prompts can be near paraphrases while differing in operational effect, scope discipline, tool use, or interaction with the current phase of a project.

ASP should therefore adopt a two-stage prompt retrieval architecture:

```text
trajectory tau_t
        ↓
continuous policy pi(tau_t)
        ↓
desired semantic query z*_t
        ↓
frozen semantic top-k from OKF prompt catalog
        ↓
reward-conditioned functional reranker
        ↓
prompt distribution / exploration
        ↓
selected executable prompt
```

For catalog prompt `j`, preserve both a frozen semantic key `e_j` and an optional learned functional key `k_j`:

```text
prompt_j = (text_j, e_j, k_j, provenance_j, utility_j)
```

The frozen key defines stable semantic identity and reproducible broad recall. The learned key captures task- and trajectory-dependent usefulness. This directly addresses the open question of a canonical embedding model: the canonical space need not itself encode perfect behavioral utility. It can remain stable while a learned projection or functional key adapts to outcomes.

The relay paper also supplies a crucial anti-Goodhart rule for ASP:

> Selection alone must not improve a prompt's future rank.

A prompt should move toward future queries only when it receives positive attributed advantage. Otherwise early retrieval noise can become a self-reinforcing popularity loop. ASP should preserve candidate exposure, propensity, attributed reward and frozen-evaluation versions for this reason.

### Shared experiment

Use the existing reward-conditioned retrieval experiment pattern with an ASP prompt catalog: construct semantically close prompt siblings whose actual downstream utility differs, verify high semantic top-k recall, and test whether reward-conditioned reranking outperforms nearest-cosine retrieval. This is a cheap mechanism test before training a trajectory encoder.

## 2. Semantic Atlas: ASP is a control problem in semantic behavior space

`semantic_atlas.md` argues that semantic position alone is not a complete dynamic state. The same point can be approached with different semantic velocities and curvature. Its state therefore includes position and dynamic terms rather than only an embedding.

This maps directly onto the ASP observation that the same current repository state can require different next prompts depending on the sequence of behaviors that produced it.

The correspondence is:

| Semantic Atlas | Agent Successor Policy |
|---|---|
| semantic position `q_t` | current project/behavior representation |
| incoming velocity `v_t` | recent direction through prompt/strategy space |
| route | desired project trajectory |
| desired local displacement | desired behavioral change |
| servo/control action | selected prompt |
| resulting trajectory | successor project states |

A trajectory-conditioned ASP policy should therefore test not only an absolute target

```text
z*_t = pi(tau_t)
```

but a relative or velocity-aware target:

```text
delta z*_t = pi(tau_t, v_t)
z*_t = z_recent + delta z*_t
```

This turns the "destinations or directions?" question from a metaphor into a direct dynamical ablation.

## 3. Inverse Atlas: history-conditioned and route-conditioned prompt retrieval

The open Semantic Atlas inverse-atlas experiment (`papers#277`) is even closer. It distinguishes:

```text
current position
incoming trajectory
independently desired outgoing direction
local retrieval evidence
```

and models retrieval approximately as:

```text
P(item | q_t, incoming_velocity, desired_delta, local evidence)
```

ASP can reuse exactly this factorization:

```text
P(prompt | current_behavior_state,
           incoming_prompt_velocity,
           desired_policy_delta,
           prompt_catalog_evidence)
```

Two trajectories can therefore arrive near the same semantic state yet retrieve different prompts because their incoming velocities differ. Similarly, two prompts with similar text may receive different rank because only one aligns with the desired outgoing direction.

The inverse-atlas paper also supplies an important verification discipline: generated/interpolated textual candidates are only proposals. They must be re-embedded and accepted only after measured proximity/support checks. ASP should apply the same rule to prompt generation.

## 4. Manifold-Aware Semantic Atlas: the prompt space may not be Euclidean

The open manifold follow-up (`papers#307`) warns that concepts may occupy curved, locally low-dimensional structures rather than isolated points or globally meaningful directions.

This matters for ASP because the continuous policy may predict a vector between existing prompts. A Euclidean midpoint is not automatically a valid behavior. Interpolating between "falsify aggressively" and "publish conservatively" may fall into a region unsupported by any coherent instruction.

ASP should therefore treat a prompt manifold as an empirical possibility:

```text
global behavior space
    └── implementation manifold
    └── falsification manifold
    └── verification manifold
    └── publication manifold
```

The policy then has two scales:

1. choose or move toward a behavioral region;
2. move within that region to an appropriate local prompt.

A future manifold-aware ASP should compare:

- Euclidean nearest-neighbor retrieval;
- graph/local-neighborhood retrieval;
- manifold/geodesic retrieval;
- global target prediction versus tangent-space displacement prediction.

If manifold-aware retrieval does not improve held-out outcomes at matched complexity, it should be rejected without harming the simpler ASP architecture.

## 5. Alignment by Affordance Restriction: continuous preference, bounded authority

`affordance_restriction.md` supplies the strongest governance interpretation of the OKF prompt catalog.

ASP's policy may operate in a continuous semantic space, but the executable action space can remain a finite, reviewable catalog:

```text
unbounded learned intention
        ↓
bounded catalog projection
        ↓
auditable executable prompt
```

This creates a useful separation:

- **policy learning** decides which admitted behavior appears valuable;
- **affordance governance** decides which behaviors are executable at all.

A prompt generator may identify a catalog gap and propose a new prompt, but the generated prompt should not automatically acquire execution authority. It enters a proposal/review path and becomes selectable only after admission into the catalog.

This also strengthens the meaning of the cycle `start.md`: the selected prompt is a structured ex-ante commitment to a versioned behavioral affordance. The cycle can later be judged against the behavior it explicitly committed to rather than against a reconstructed story of its internal reasoning.

ASP therefore provides a natural extension to affordance restriction: **learned selection over a structurally bounded action vocabulary**. Training-based optimization and structural bounding are complementary rather than alternatives.

## 6. Generative Machine Teaching: prompt trajectories as curricula

`generative_machine_teaching.md` treats a curriculum as an ordered, state-transforming programme rather than an exchangeable dataset. Each lesson changes the learner and therefore changes the conditions under which later lessons are interpreted.

ASP has the same structural property at a higher operational level. A sequence of prompts is not merely a bag of independently useful instructions:

```text
prompt_1 → result_1 → prompt_2 → result_2 → ...
```

Each result changes the repository, the available evidence, the prompt catalog, and the trajectory state presented to later cycles.

ASP can therefore be interpreted as a form of **meta-machine teaching over a general-purpose agent**: the policy learns a curriculum of behavioral instructions that elicits a long-horizon project trajectory. This is an analogy, not an identity. The base LLM need not update its model weights; the "student state" can be the coupled state of repository + context + memory + tools.

A shared research question follows: does optimizing prompt order produce gains beyond choosing individually high-value prompts? The state-only versus trajectory-conditioned ASP experiment is also a curriculum-order experiment.

## 7. Structured Irregularity: delayed reward as retrospective interpretation

`pedagogical_signal_extraction.md` introduces **retrospective interpretation**: evidence that appears opaque at time `t` may become useful after later observations reveal the relevant structure.

ASP's delayed evaluator loop is an operational instance of the same phenomenon. A cycle that looks unimportant immediately may later be recognized as the step that enabled a merge, prevented a regression, or made a later discovery possible. Conversely, apparently impressive work may later be reclassified as churn.

This suggests treating reward maturation as more than score revision. Later cycles can change the *interpretation* of earlier actions.

The training corpus should therefore preserve:

```text
forecast at t
next-cycle retrospective at t+1
later observed consequence at t+k
reason/evidence for reinterpretation
```

A model can then learn not only expected reward but which kinds of early evidence are systematically under- or over-valued by short-horizon critics.

## 8. Informational Time: wall-clock horizon and causal horizon are different

ASP currently uses hour/day/week/month/year critics. `informational_time.md` warns that elapsed physical or wall-clock time and informational causal depth should not be collapsed.

An hour may pass with no relevant state transition. Conversely, five consequential agent cycles can occur in a short interval. For learning which actions caused which outcomes, ASP should preserve at least two temporal coordinates:

```text
wall_clock_delta
causal_cycle_depth
```

and eventually richer measures of causal work or intervening state changes.

This yields a testable refinement of multi-horizon reward. Compare critics indexed by wall time, cycle depth, and hybrid horizons. If causal-depth critics better predict downstream outcomes, fixed clock horizons should be treated primarily as convenient observation schedules rather than the fundamental temporal variable.

The informational-time paper also supports recursive compression of trajectory memory: a long causal history can be represented by compact expandable summaries without pretending the underlying history never occurred.

## 9. Language as a Higher-Order Agent: bounded readout and compressed trajectory memory

The open Language-Agent paper (`papers#308`) gives ASP a principled answer to an eventual scaling problem. "Use the whole trajectory" cannot mean placing every raw historical token into every future inference indefinitely. Readout is bounded.

The Language-Agent paper distinguishes explicit archive lookup from model-based reconstruction relative to a query family, loss tolerance and readout budget. ASP can adopt the same test for long-term trajectory memory.

Recent cycles can remain explicit while older history is represented through learned prototypes, summaries, successor statistics or reconstructive memories:

```text
recent raw trajectory
        +
compressed long-term trajectory state
        ↓
policy
```

The requirement is functional rather than literal: compression is acceptable only if it preserves the historical distinctions needed for prompt choice under matched readout budgets.

ASP also supplies a small controlled environment for the Language-Agent Hypothesis. A recurring human–LLM–repository–scheduler system maintains a shared external state, incorporates outputs causally into later inputs, compresses history and alters future action selection. This does not establish higher-order agency, but it creates a tractable microcosm in which "independent communicating agents" can be compared against "agents + slower shared latent state" models.

## 10. Machine Discovery: when catalog growth becomes recursive curriculum expansion

`machine_discovery.md` distinguishes an emitted artifact from a certified public epistemic transition. ASP should use the same discipline when discussing self-improvement.

Generating a new prompt is not a discovery. Even successfully using it once is not enough. A new behavioral strategy becomes scientifically interesting when it is:

- provenance-auditable;
- distinct from existing catalog entries under a declared equivalence rule;
- admitted through the catalog's governance process;
- measurably useful to later cycles on held-out or future trajectories.

At that point the agent has changed the curriculum available to later agents. This is a form of recursive capability expansion, though not necessarily an epistemic discovery in the stronger sense of the Machine Discovery paper.

The Machine Discovery framework therefore supplies the vocabulary needed to avoid calling every prompt mutation "self-improvement." ASP supplies a possible behavioral-domain testbed for downstream fertility: did the admitted strategy improve what later agents could accomplish?

## 11. ESHTR and empirical evaluation: critics should themselves be evaluated

`embedding_seeded_tournament.md` and `empirical_evaluation.md` provide two useful warnings for ASP's temporal evaluators.

First, LLM judgments can be inconsistent and non-transitive. Second, semantically heterogeneous objects may be poor direct comparison targets. ASP currently asks role-conditioned temporal critics to assign absolute scores. Those scores should not be treated as ground truth merely because they are structured.

A stronger evaluation layer can compare cycles within semantically similar neighborhoods and use heterogeneous evaluator panels or pairwise tournaments as an external calibration signal. Candidate experiments include:

```text
absolute 0..1 critic scores
vs.
pairwise preference among semantically similar cycles
vs.
heterogeneous panel aggregation
vs.
ESHTR-style local tournament + cross-cluster abstraction
```

The question is not whether ASP should literally rank every cycle in a tournament. It is whether relative, locality-aware evaluation produces more stable reward labels than unconstrained absolute self-grading.

This also creates an evaluator-learning problem: which temporal critic, model family or evaluation protocol best predicts genuinely observed future outcomes?

## 12. Pontifex: one canonical embedding space may not be necessary

`pontifex.md` deliberately avoids mapping heterogeneous embedding spaces into one common coordinate system. Instead it learns over patterns of similarity produced independently by several encoders.

This supplies an alternative to ASP's current assumption that one `embedding_model_id` defines the canonical behavior space. Three architectures should be compared:

1. **single-space ASP** — one frozen canonical embedding model;
2. **SRF-aligned ASP** — several spaces aligned into a common Semantic Atlas reference frame;
3. **multi-space ASP** — predict or retrieve in several unaligned spaces and combine similarity/ranking evidence through a small convergence model.

If multi-space convergence outperforms any single canonical space, the "choose the correct embedding model" question is partly dissolved: semantic neighborhood identity can be an agreement pattern rather than one coordinate system.

## 13. Semantic Tokenization Transformers: the prompt catalog as a semantic codebook

`semantic_tokenization_transformers.md` treats a semantic codebook as a coarser alphabet over which long-range dynamics may be easier to model. The ASP prompt catalog is not the same object, but the analogy is useful.

As the catalog grows, behavioral prompts may admit hierarchical quantization:

```text
behavior family
→ strategy region
→ specific executable prompt
```

A learned policy could plan over coarse behavioral codes and retrieve a concrete prompt only at execution time. This is another route toward separating long-horizon planning from high-resolution textual realization.

The hypothesis should be tested against the simpler flat catalog; hierarchical codebooks earn their complexity only if they improve data efficiency, retrieval or transfer.

## 14. Repository prompt governance and the synthesis routine

Open PR `papers#301` moves scheduled research-routine instructions into versioned repository prompts because external scheduler copies had diverged from the canonical protocol. This is direct operational evidence for ASP's repository-bound prompt catalog design.

A scheduler should ideally hold only a stable pointer to versioned policy/catalog state. Behavioral instructions belong in auditable repository artifacts where they can be diffed, reviewed, related to outcomes and selected by a policy.

The synthesis/adversarial/supportive research process, now with dozens of logged sessions and explicit protocol state, is also a promising second ASP testbed after O Vigia. It has:

- repeated cycles;
- durable reports;
- explicit behavioral roles;
- observable failures such as loops, overdue fronts and missed absorption triggers;
- outcomes such as bilateral settlement, absorption and paper revision.

Unlike the young O Vigia ASP corpus, this history may support retrospective experiments on state compression, trajectory-conditioned strategy choice and evaluator calibration. It should not be retroactively relabeled as randomized RL data when historical propensities are unknown, but it can support representation and observational analyses.

## 15. Revised ASP architecture after cross-paper synthesis

The resulting architecture is richer but also cleaner:

```text
append-only OKF trajectory
        ↓
recent explicit history + bounded-readout long-term memory
        ↓
trajectory/dynamics representation
(position + incoming semantic velocity + causal depth)
        ↓
continuous desired behavior target / desired delta
        ↓
frozen semantic top-k from affordance-restricted OKF prompt catalog
        ↓
reward-conditioned functional reranking + exploration
        ↓
versioned prompt selected as ex-ante commitment
        ↓
agent action
        ↓
successor state + evidence
        ↓
multi-horizon forecasts / retrospectives / observed delayed outcomes
        ↺
```

Generated prompts do not bypass the catalog. They are proposals for catalog expansion. Semantic proximity supplies recall; downstream reward supplies functional preference; governance supplies authority.

## 16. Cross-paper experimental matrix

Several experiments can now test multiple papers without conflating their claims:

| Experiment | ASP | Other paper contribution |
|---|---|---|
| semantic top-k vs reward reranker | prompt selection | RL Relay Transducers |
| state-only vs full trajectory | trajectory policy | Machine Teaching / LAH |
| absolute target vs desired delta | semantic dynamics | Semantic Atlas |
| history/route-conditioned retrieval | functional retrieval | Inverse Atlas |
| Euclidean vs manifold-aware prompt search | prompt geometry | Manifold Atlas |
| raw history vs reconstructive memory | bounded readout | Language-Agent |
| wall-clock vs causal-depth critics | delayed value | Informational Time |
| retrospective reward reinterpretation | reward maturation | Structured Irregularity |
| generated prompt admission + later fertility | catalog evolution | Machine Discovery / Affordance Restriction |
| single vs multi-space retrieval | embedding robustness | Pontifex / Semantic Atlas |
| absolute critic vs panel/pairwise critic | reward reliability | ESHTR |
| O Vigia vs synthesis-routine transfer | cross-domain policy | programme-level generalization |

This matrix suggests that ASP should be developed as a testbed that shares evidence with neighboring theories rather than as an isolated architecture. The same trajectory can support distinct claims provided each paper states its own observable, null model and falsifier.

## 17. Claim boundary

The cross-paper fit should not be mistaken for confirmation. The fact that several papers share embeddings, trajectories, retrieval, compression or reward does not imply that they are one theory or that success in one validates another.

The strongest discipline is reuse with independent falsification:

- ASP may reuse reward-conditioned retrieval even if interstitial-agency claims fail;
- ASP may use Semantic Atlas dynamics even if manifolds add no value;
- bounded-readout memory may help ASP even if Language-Agent higher-order agency is rejected;
- an affordance-restricted prompt catalog can remain useful even if learned prompt selection fails to beat a fixed scheduler;
- machine-discovery vocabulary can constrain self-improvement claims even if no generated ASP prompt ever qualifies as a discovery.

The research programme gains strength when mechanisms are shared but claims remain separately defeasible.
