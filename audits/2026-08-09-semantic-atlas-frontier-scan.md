---
type: "Audit Report"
title: "Semantic Atlas Frontier Scan — 2026-08-09"
description: "Claim-aware external frontier scan across the live Semantic Atlas PR overlay, recording primary-source collisions, negative evidence, stack drift, and concrete experiment changes."
tags: [semantic-atlas, frontier-scan, prior-art, audit, experiments]
timestamp: 2026-08-09T14:24:00Z
---

# Semantic Atlas Frontier Scan — 2026-08-09

## Status

First dogfood run of the `research-frontier` method proposed in `franklinbaldo/skills#74/#75`.

This is an **external research audit**, not a manuscript and not a claim that the search is exhaustive. Discovery/ranking systems were used only to prioritize reading. Every material consequence below is grounded in the cited primary preprint record rather than a ranking score or generated summary.

Literature cutoff: **2026-08-09**.

## 1. Effective research state

The Semantic Atlas programme cannot currently be represented by one branch head. The live state is an **overlay** of the PRs that own the latest version of each manuscript/protocol surface.

| Surface | Live owner | Head observed in this scan | Research obligation |
| --- | --- | --- | --- |
| manuscript | #271 | `1cf111d9dca4f5de2e6e54dbcd7d7dca7bb48644` | six separated Atlas claims and prior-art boundaries |
| Experiment A | #272 | `ef9cafe7b4298213e3d57dbbc5301ff9292aeb6f` | paired cross-model SRF calibration and held-out identifiability |
| Experiment B | #273 | `326426ce762f0736f0815808210056396ccaa866` | route-following semantic MPC |
| Experiment C | #274 | `830ef45da4bc847dfc025dc58e55f3a29a81d32d` | future semantic head + closed-loop Servo |
| Experiment D | #275 | `ef5769b5143e7535935c8efc6ebd55775a3aa1bb` | frozen-weight semantic Jacobian vs empirical dynamics |
| Experiment E | #277 | `78bba93be004cfde88875098d1447a563febed26` | empirical inverse atlas / route-conditioned lexical retrieval |
| GPU smoke | #279 | `bb12f2ba518e9f0b38c7bf6f3b9215b414c6fb9e` | first cheap model-backed execution artifact |
| Experiment F | #281 | `c42546361bc6c20bafad01c76f48314cf38dba72` | termination geometry / semantic head-tail |

### Finding S1 — the leaf PR is stale as a research snapshot

During this scan, `experiments/semantic_atlas/protocol.md` on the current #272 head was compared with the same path visible from the #281 branch. The #272 version contains the later correction that the regular simplex fixes **geometry only**, semantic orientation comes from row-paired calibration + orthogonal Procrustes, and cross-model success is tested on held-out canonical/quasar coordinates with a shuffled-correspondence negative control. The descendant copy still contained the older deterministic-orientation / rotation-invariance formulation.

The same class of drift became visible again after this scan strengthened #274: #275 is now behind the updated #274 base and cannot be treated as a materialized snapshot of the current stack without reconciliation.

**Consequence:** frontier scans of stacked research must use the current owner head of each live surface and detect ancestor/descendant drift. `HEAD(#281)` is not synonymous with "the Semantic Atlas as currently proposed."

This finding was fed back into `research-frontier/references/frontier-scan.md` in `skills#75` as a general overlay rule.

## 2. Live obligations frozen before literature comparison

| ID | Live claim / experiment | Current status | Load-bearing boundary |
| --- | --- | --- | --- |
| A | artificial quasar geometry + empirically anchored SRF | preregistered | paired held-out cross-model coordinates, not distance invariance |
| B | semantic MPC can follow an explicit route | preregistered | navigability/control, not compute efficiency |
| C | hidden-state future head + bounded feedback can track semantic routes | preregistered | actual generated trajectory must move; head-error reduction is insufficient |
| D | useful local semantic dynamics can be compiled from frozen weights | preregistered | zero-trajectory weight-derived operator must predict held-out discrete motion |
| E | empirical inference memory can act as an inverse Atlas for a planned route | preregistered | route/direction must add value beyond position-only retrieval |
| F | termination may exhibit stable semantic basins/surfaces before EOS | preregistered | length/lexical effects must not explain the geometry; singularity requires stronger degeneracy evidence |

No empirical success is inferred from these preregistrations.

## 3. Primary-source collision ledger

### A1 — Procrustes alignment is prior art, not the SRF contribution

**Source:** Maystre et al. (2025), *When Embedding Models Meet: Procrustes Bounds and Applications*, arXiv:2510.13406.

**Primary-source result inspected:** the paper studies when separately trained embedding spaces can be aligned by an orthogonal transformation, provides bounds linking approximate pairwise-inner-product preservation to a close isometry, and uses Procrustes post-processing for interoperable embedding models.

**Relation:** `challenges` the novelty of cross-model orthogonal alignment; `supports` the plausibility of the chosen calibration primitive.

**Collision:** Experiment A already uses paired Procrustes after the #272 identifiability correction. Procrustes itself therefore cannot be a contribution claim.

**Action:** no protocol mutation required in this cycle because #272 already makes the simplex metrological rather than intrinsically semantic and treats calibration empirically. Manuscript related work should eventually make the Procrustes prior-art boundary explicit when the paper absorbs experiment results.

### A2 — a shared multi-model reference already exists as a research target

**Source:** Achara et al. (2026), *Multi-Way Representation Alignment*, arXiv:2602.06205.

**Primary-source result inspected:** the paper adapts Generalized Procrustes Analysis to align `M >= 3` representation spaces into a shared orthogonal universe and introduces Geometry-Corrected Procrustes Alignment for any-to-any retrieval while retaining a shared reference.

**Relation:** `challenges` any future claim that constructing a shared global latent reference by Procrustes is novel; `enables_experiment` for a later three-plus-observer baseline.

**Collision:** current Experiment A is deliberately narrower — one reference observer and one independent transfer observer, with artificial quasar geometry and held-out coordinate identifiability. That remains a useful test, but "global shared representation universe" is occupied prior-art territory.

**Action:** preserve the current two-observer primary experiment. If the programme escalates to three or more observers, add GPA/GCPA as a mandatory alignment baseline rather than treating multi-way calibration as an Atlas invention.

### B1 — text-native curvature is close, but not the same state/control object

**Source:** Grover et al. (2026), *Text Has Curvature*, arXiv:2602.13418.

**Primary-source result inspected:** the paper defines a text-native word-level discrete curvature signal, `Texture`, from left/right contextual beliefs through a Schrödinger-bridge construction and applies it to compression and routing.

**Relation:** `orthogonal` to the primary causal trajectory claim; potentially `enables_experiment` as a later geometry comparator.

**Collision:** Semantic Atlas turning/trajectory curvature is measured in a causal projected state trajectory, while Texture is designed as a text-native curvature observable using bilateral context. The current manuscript already recognizes this neighboring work. Treating Texture as if it directly falsified causal SRF curvature would conflate distinct observables.

**Action:** no immediate protocol change. A later retrospective geometry study may compare the signals, but the causal controller must not use future/right-context information unavailable at generation time.

### C1 — context-dependent steering fields are already established prior art

**Source:** Li, Li & Huang (2026), *Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models*, arXiv:2602.01654.

**Primary-source result inspected:** SVF replaces a fixed global steering vector with a differentiable concept scoring function whose local gradient defines a context-dependent steering direction, including long-form and multi-attribute settings.

**Relation:** `challenges` a broad "local/context-dependent semantic control" novelty claim and `enables_experiment` as a stronger baseline.

**Action applied:** #274 `protocol_servo.md` now requires a state-dependent local-field baseline. The Servo novelty boundary is narrowed to **closed-loop tracking of an independently planned multistep SRF route**, not the existence of local vector fields.

### C2 — curved, token-varying activation flows are also prior art

**Source:** Jin et al. (2026), *Beyond Steering Vector: Flow-based Activation Steering for Inference-Time Intervention*, arXiv:2605.05892.

**Primary-source result inspected:** FLAS learns a concept-conditioned velocity field over activations and reports curved, multi-step, token-varying trajectories, explicitly rejecting fixed single-step position-invariant steering assumptions.

**Relation:** `challenges` any claim that curved/token-varying activation motion is distinctive to Semantic Servo; `enables_experiment` as a frontier comparator.

**Action applied:** #274 now includes a FLAS-like flow condition when feasible (or a preregistered faithful secondary baseline) and requires matched intervention/model-forward accounting. Beating static activation addition is explicitly insufficient.

### D1 — Jacobian Lens/J-space is close in terminology but a different operator

**Source:** Gurnee et al. (2026), *Verbalizable Representations Form a Global Workspace in Language Models*, arXiv:2607.15495.

**Primary-source result inspected:** the Jacobian Lens identifies representations that a model is poised to verbalize, defining a J-space used to study reportable/deliberative internal content.

**Relation:** `orthogonal` / close prior art to Experiment D's dynamic operator rather than a direct supersession.

**Collision:** the Experiment D object is a Jacobian of a differentiable **frozen-weight semantic transition** and is evaluated by prediction of held-out discrete semantic motion. The Jacobian Lens is used to expose verbalizable representational content. The manuscript already says the semantic Jacobian is related to, but not equated with, Jacobian Lens/J-space.

**Action:** no protocol change in this cycle. Preserve the explicit operator distinction. If an implementation later projects through J-space, that should be registered as a new comparator rather than silently identifying the two Jacobians.

### E1 — dense semantic retrieval for speculative drafts is prior art

**Source:** Gritta, Xue & Lampouras (2025), *DReSD: Dense Retrieval for Speculative Decoding*, arXiv:2502.15572.

**Primary-source result inspected:** DReSD uses approximate nearest-neighbor search over contextualized token embeddings to retrieve semantically relevant token sequences for speculative decoding with target-model verification.

**Relation:** `challenges` generic novelty claims around dense semantic retrieval/drafting; `enables_experiment` as a stronger non-Atlas baseline.

**Action applied:** #277 `protocol_inverse.md` now includes a DReSD-style dense contextual retrieval/speculative-drafting condition. The surviving frontier claim is narrower: calibrated SRF position **plus incoming trajectory plus externally planned desired displacement** must improve held-out lexical guidance beyond strong context-only dense retrieval.

### F1 — remaining output length is linearly decodable from hidden state

**Source:** Merzouk et al. (2026), *How Much is Left? LLMs Linearly Encode Their Remaining Output Length*, arXiv:2607.05316.

**Primary-source result inspected:** minimal linear probes on frozen hidden states across multiple open-weight models decode total response length before output and approximate remaining generation length during generation; the authors explicitly distinguish decodability from demonstrated causal use.

**Relation:** `challenges` a false-green route for terminal basins/tails and `enables_experiment` as a load-bearing control.

**Collision:** an apparent contraction toward EOS in SRF space may simply recover an already encoded remaining-length variable. Token index and normalized length do not control for that internal predictive signal.

**Action applied:** #281 `protocol_termination.md` now requires a preregistered hidden-state remaining-length probe and measures the **incremental** value of `q`, velocity and history after conditioning on predicted remaining length.

### F2 — progressive hidden-state/entropy prediction strengthens the length control

**Source:** Xie et al. (2026), *Predicting LLM Output Length via Entropy-Guided Representations*, arXiv:2602.11812.

**Primary-source result inspected:** the paper reuses model hidden states and token entropy for static and progressive remaining-length prediction and introduces a benchmark for long-sequence/CoT/RL length prediction.

**Relation:** `enables_experiment`.

**Action applied:** #281 registers a progressive hidden-state + entropy predictor as a stronger secondary baseline when feasible and requires basin/horizon analyses to survive matching or residualization by learned remaining length.

## 4. Negative evidence

### N1 — no inspected source supersedes the route-conditioned inverse-Atlas claim

Within the retrieval/memory sources inspected in this cycle, no material collision was found with the **joint** claim:

`P(token/block | calibrated SRF state, incoming semantic trajectory, independently planned desired displacement, local lexical evidence)`

DReSD occupies dense semantic retrieval/speculative drafting, and ordinary kNN-LM/inference-memory work occupies non-parametric context-to-token retrieval. The inspected source did not itself supply the Atlas combination of calibrated cross-model position, incoming direction, and an external route objective.

This is a **bounded search result through 2026-08-09, not proof of global novelty**. It becomes less meaningful if future citation-trail or full-text search finds a semantically equivalent route-conditioned memory method under different terminology.

### N2 — no inspected source collapses the Experiment D operator into Jacobian Lens

The July 2026 Jacobian Lens work is important and very close linguistically, but on the inspected primary record it does not establish the same frozen-weight next-semantic-transition operator or the same held-out dynamic prediction gate. No manuscript retraction is justified from that source alone.

## 5. Research actions produced by this scan

| Action | Destination | Status |
| --- | --- | --- |
| require state-dependent steering baseline; narrow Servo novelty | #274 | applied in `830ef45...` |
| add DReSD-style dense retrieval/speculative baseline; narrow inverse-atlas novelty | #277 | applied in `78bba93...` |
| add learned remaining-length controls and conditional/residual tests | #281 | applied in `c425463...` |
| treat stacked effective state as a live-head overlay | skills#75 | applied in `267f238...` |
| make Procrustes/GPA prior-art boundary explicit in eventual manuscript absorption | #271 / #270 | deferred until synthesis/experiment evidence |
| consider GPA/GCPA only when Experiment A expands to `M >= 3` observers | future A extension | deferred |
| preserve Jacobian Lens vs dynamic-transition-Jacobian distinction | #271/#275 | no change required |

The useful signal is not that eight papers were cited. The useful signal is that **three preregistered experiments became harder to pass and one research-state invariant changed**.

## 6. Discovery-method finding: embedding similarity alone is not a sufficient frontier radar

**Source:** Yoo (2026), *Topic Is Not Agenda: A Citation-Community Audit of Text Embeddings*, arXiv:2605.07158.

The primary record reports that several modern text embedding models retrieve same-subfield neighbors substantially better than same-research-agenda neighbors, and that simple citation-aware reranking recovers useful agenda signal missed by cosine retrieval.

**Consequence for future `research-frontier` cycles:** do not build the radar as `embed our claim -> nearest arXiv papers -> done`. The next benchmark should compare at least:

1. semantic/expanded lexical search;
2. citation-neighbor expansion from strong seed papers;
3. category/venue/time filters;
4. embedding similarity;
5. hybrid reranking;
6. adversarial terminology changes where the same mechanism is named differently.

This is a benchmark-design consequence, not evidence about Semantic Atlas itself.

## 7. Limitations

- This first cycle prioritized high-salience collisions around A/C/D/E/F; it is not an exhaustive systematic review of every Atlas field.
- Primary arXiv records were inspected for the material claims recorded here. Full reproduction and implementation-level comparison remain separate work.
- Search/discovery coverage is necessarily bounded; negative results are phrased accordingly.
- The active stack contains ancestor/descendant drift, so any future scan must reconstruct the overlay again rather than reuse this table blindly.
- No model-backed Semantic Atlas result was produced by this literature scan. Experiment outcomes remain unmeasured until the registered runs execute.

## 8. Next frontier

The next cycle should be capable of finding sources this one would miss. The highest-value improvement is **citation-aware, claim-seeded discovery** plus an adversarial alternate-terminology pass, evaluated against the current search approach.

For Semantic Atlas specifically, the next deep scans should focus on:

- causal representation alignment and gauge/identifiability beyond orthogonal Procrustes;
- route planning/control versus context-dependent steering under matched objectives;
- reduced-order transformer dynamics and local linearization beyond output Jacobians;
- route-conditioned memory/speculative decoding under non-Atlas terminology;
- causal tests that distinguish learned length planning from genuinely independent termination geometry.

A future cycle should record not just what it finds, but whether the added citation/terminology frontier finds a material collision that this 2026-08-09 scan missed.

## Primary sources inspected

1. Maystre et al. (2025). *When Embedding Models Meet: Procrustes Bounds and Applications.* arXiv:2510.13406.
2. Achara et al. (2026). *Multi-Way Representation Alignment.* arXiv:2602.06205.
3. Grover et al. (2026). *Text Has Curvature.* arXiv:2602.13418.
4. Li, Li & Huang (2026). *Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models.* arXiv:2602.01654.
5. Jin et al. (2026). *Beyond Steering Vector: Flow-based Activation Steering for Inference-Time Intervention.* arXiv:2605.05892.
6. Gurnee et al. (2026). *Verbalizable Representations Form a Global Workspace in Language Models.* arXiv:2607.15495.
7. Gritta, Xue & Lampouras (2025). *DReSD: Dense Retrieval for Speculative Decoding.* arXiv:2502.15572.
8. Merzouk et al. (2026). *How Much is Left? LLMs Linearly Encode Their Remaining Output Length.* arXiv:2607.05316.
9. Xie et al. (2026). *Predicting LLM Output Length via Entropy-Guided Representations.* arXiv:2602.11812.
10. Yoo (2026). *Topic Is Not Agenda: A Citation-Community Audit of Text Embeddings.* arXiv:2605.07158.

## Issue

Implements the first frontier cycle for #282. No Semantic Atlas PR is merged by this audit.
