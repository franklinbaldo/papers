---
type: "Audit Report"
title: "ESHTR falsification and ranking-identifiability audit — 2026-09-19"
description: "Adversarial claim-level audit of ESHTR focused on Semantic Proximity, global-ranking identifiability, comparison complexity, pairwise-judge robustness, and legal-domain external validity."
tags: [eshtr, prior-art, falsification, llm-as-a-judge, legal-ai, ranking, semantic-proximity]
timestamp: 2026-09-19T10:59:00Z
---

# ESHTR falsification and ranking-identifiability audit — 2026-09-19

This is an adversarial addendum to `embedding-seeded-tournament-2026-09-17.md`. The earlier audit remains the novelty ledger. This round asks a different question: which substantive ESHTR claims are false as written, which are still open, and which controls are required before the proposed mechanism is credible.

## 1. Temporal reconstruction

The relevant claim families were already public in commit [`872de345e9a67a6631966b33a0b69461aff6d433`](https://github.com/franklinbaldo/papers/commit/872de345e9a67a6631966b33a0b69461aff6d433), timestamped **2026-05-10 14:37:39 UTC**. The parent does not contain the file. The introducing version already states:

- semantic clustering before pairwise judging;
- the claim that semantically similar decisions are a regime in which LLM judges are expected to be more reliable;
- the Semantic Proximity mechanism linking semantic distance to non-transitivity;
- local cluster rankings followed by a championship among cluster winners;
- the claim that local rankings plus the championship ordering reconstruct a full-corpus ranking;
- the `n=1000, k=20` comparison-count example.

Accordingly, **2026-05-10 14:37:39 UTC** is the cutoff used for all claims below. Work public before it may be prior/adjacent work or pre-existing contrary evidence. Work after it is kept on the later-work/truth-status axis.

## 2. Claims and explicit falsifiers

### C1 — Semantic Proximity Hypothesis (SPH)

**Claim.** Holding the judging setup fixed, greater semantic distance between compared decisions increases preference instability/non-transitivity; semantic-locality seeding should therefore improve reliability.

**Would falsify or materially narrow it.** After controlling for decision-quality margin/uncertainty, procedural class, length/style, position, judge identity and repeated-call variance, semantic distance has a null or reversed association with cycle incidence / human-validity error; or within-cluster comparisons have equal or higher cycle/error rates than matched cross-cluster comparisons.

### C2 — full-ranking reconstruction

**Claim.** Within-cluster rankings plus a tournament among cluster winners are sufficient to reconstruct a full total ordering over all decisions.

**Would falsify it.** Two or more incompatible global total orders remain consistent with every observed pairwise result produced by the protocol.

### C3 — computational-saving claim

**Claim.** The all-pairs-within-cluster design illustrated at `n=1000, k=20` needs about 1,250 Phase-2 comparisons and reduces comparisons by about 99.7% relative to global all-pairs.

**Would falsify it.** Direct counting under the paper's own Phase-2 specification gives materially different totals.

### C4 — heterogeneous jury as bias control

**Claim.** A 3–5 model-family panel improves reliability by reducing model-family-specific systematic bias.

**Would falsify or narrow it.** Shared biases persist across model families; the panel is no better than the best single judge against human ground truth; or adversarially irrelevant style changes flip panel rankings.

### C5 — legal validity from LLM-panel agreement/calibration

**Claim.** The proposed panel plus CPC-anchored rubric can serve as a scalable proxy for expert judicial-quality ranking once internally calibrated.

**Would falsify or narrow it.** High inter-LLM agreement coexists with low agreement against legal-expert ground truth, or the same decision receives materially different quality orderings under legally irrelevant presentation changes.

### C6 — ESHTR's incremental advantage

**Claim.** Semantic clustering adds reliability beyond strong non-semantic scheduling/ranking baselines at matched comparison budget.

**Would falsify it as an advantage claim.** SWIM/round-robin subsampling, CrowDC-style bridge comparisons, or an absolute/reference-based protocol reaches equal or better expert-rank correlation and cycle/error rate at matched cost.

## 3. Strong formal counterexample: Phase 3 does not identify a full ranking

C2 is false as written.

Take two clusters whose observed local rankings are:

- cluster A: `A1 > A2`;
- cluster B: `B1 > B2`.

Suppose Phase 3 compares only the winners and observes `A1 > B1`.

These observations do **not** determine where `A2` belongs relative to `B1` or `B2`. Both of the following global orders are compatible with the observations:

- `A1 > A2 > B1 > B2`;
- `A1 > B1 > B2 > A2`.

Many additional linear extensions are possible. Local total orders plus an ordering of cluster winners therefore identify a **partial hierarchy**, not a global total order. A valid full-corpus ranking needs additional cross-cluster bridge comparisons or a separately justified model tying score scales across clusters. CrowDC is relevant prior art precisely because it uses multiple pivots from each group to align local score systems rather than inferring a global order from winners alone.

**Classification:** `contrary_evidence` — **strong**.

**Target attacked:** mathematical identifiability of the claimed output, not merely performance magnitude.

**Required paper action:** `retract_claim` as stated; replace it with champion/local-ranking semantics, and require cross-cluster bridges for any future total-order claim.

## 4. Strong arithmetic correction: the 99.7% example is inconsistent with the stated algorithm

For `n = 1000`, `k = 20`, average cluster size `c = 50`:

- one cluster all-pairs: `50 × 49 / 2 = 1,225`;
- all 20 clusters: `20 × 1,225 = 24,500`;
- champion all-pairs: `20 × 19 / 2 = 190`;
- ESHTR total under the stated all-pairs/BT design: **24,690**;
- global all-pairs: `1000 × 999 / 2 = 499,500`;
- reduction: `1 - 24,690 / 499,500 ≈ 95.06%`.

The current `~1,250` number counts approximately one cluster, not all clusters. `99.7%` is therefore not the reduction delivered by the stated all-pairs-within-cluster protocol.

There is also a schedule/guarantee distinction. A strict knockout can select a local winner in linear comparisons but cannot provide the paper's stated "all pairwise outcomes" for Bradley–Terry estimation or a defensible full local ranking. Sorting-like schedules can be subquadratic only under assumptions about comparator consistency that are exactly what the non-transitivity section places in doubt.

**Classification:** `contrary_evidence` — **strong**.

**Target attacked:** quantitative complexity/result claim.

**Required paper action:** `retract_claim` for the example and replace it with the correct 24,690 / ~95.1% calculation; keep reduced-budget schedules as separately evaluated variants with explicit output guarantees.

## 5. Pre-cutoff evidence that SPH is confounded by comparison difficulty

### Xu et al. — *Investigating Non-Transitivity in LLM-as-a-Judge*

- First public date: arXiv v1, **2025-02-19**.
- Venue: ICML 2025.
- Primary: https://arxiv.org/abs/2502.14074
- PMLR: https://proceedings.mlr.press/v267/xu25w.html
- Compared claims: C1/C6.
- Priority classification: `prior_art` for LLM-judge non-transitivity and tournament mitigation (already recorded in the 2026-09-17 audit); `adjacent_prior_work` for the SPH-specific causal question.
- Truth-status relation: `boundary_condition`, **moderate**.

Xu et al. show that non-transitivity is substantial and that ranking is baseline-sensitive; their stratified analyses also report stronger non-transitivity when compared systems are close in performance. That creates an alternative mechanism directly relevant to ESHTR: semantic clustering may put decisions into more locally comparable **and more closely matched-quality** groups. If comparison difficulty/quality margin drives cycles, raw `κ_intra > κ_cross` does not identify a semantic-distance effect.

**Required action:** `narrow_claim + add_control + downgrade_confidence`. SPH should be treated as the conditional claim that semantic distance adds explanatory power *after* quality margin/uncertainty and other confounds are controlled.

## 6. Pre-cutoff counter-pressure on pairwise judging

### Tripathi et al. — *Pairwise or Pointwise? Evaluating Feedback Protocols for Bias in LLM-Based Evaluation*

- First public date: arXiv v1, **2025-04-20**.
- Primary: https://arxiv.org/abs/2504.14716
- Compared claims: C4/C6 and ESHTR's use of pairwise comparison as the default primitive.
- Classification: `boundary_condition`, **strong** for the pairwise primitive; transfer to judicial decisions remains to be tested.

The study finds pairwise LLM evaluation materially more vulnerable to irrelevant distractor features than absolute scoring; on MT-Bench, distractor-induced preference flips occur at roughly 35% under pairwise evaluation versus about 9% for absolute scores. Thus pairwise comparison is not automatically the more reliable protocol merely because it avoids absolute scale calibration.

**Required action:** `add_control + narrow_claim`. ESHTR should be benchmarked against pointwise/reference-based rubric scoring under style/rhetoric perturbations, not only against other pairwise schedules.

## 7. Cross-family panels help in some settings but do not cancel shared bias

### Verga et al. — *Replacing Judges with Juries*

- First public date: **2024-04-29**.
- Primary: https://arxiv.org/abs/2404.18796
- Relation: supporting evidence for C4 / `prior_art` for diverse LLM panels.

Across six datasets, PoLL outperforms a single large judge in the studied settings and reduces intra-model bias. This remains legitimate support for ESHTR's choice of a heterogeneous panel.

### Soumik — *Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines*

- First public date: arXiv v1, **2026-04-25**, still before the ESHTR cutoff.
- Primary: https://arxiv.org/abs/2604.23178
- Compared claim: C4.
- Classification: `boundary_condition`, **strong**.

Across five judges from four provider families, the paper reports style bias as the dominant shared bias, with bias scores 0.76–0.92, while mitigation effectiveness remains model-dependent. The evidence does not negate PoLL; it shows that provider/model diversity is not a certificate that shared presentation biases cancel.

**Required action:** `narrow_claim + add_control`: state that diversity targets family-specific errors, while cross-family shared biases require explicit style normalization, adversarial perturbation and human-grounded validation.

## 8. Legal-domain contrary evidence: inter-LLM agreement is not legal ground truth

### Karp et al. — *LLM-as-a-Judge is Bad, Based on AI Attempting the Exam Qualifying for the Member of the Polish National Board of Appeal*

- First public date: arXiv v1, **2025-11-06**.
- Primary: https://arxiv.org/abs/2511.04205
- Compared claims: C5/C6.
- Classification: `contrary_evidence`, **strong** against substituting LLM consensus for expert legal validity; **moderate** when transferred to ESHTR's different ranking task.

On an official high-stakes legal qualification exam that includes a written judgment, LLM-as-a-judge evaluations often diverge from the official examining committee; the study also documents hallucination, legal-citation and logical-reasoning failures. This does not show that ESHTR cannot rank decisions, but it attacks the validation shortcut in which agreement among LLM judges is treated as the main evidence that the ordering is legally valid.

**Required action:** `add_control + narrow_claim`. Expert-human pairwise/rank anchors must be a primary validation endpoint, not merely internal Fleiss κ or synthetic calibration.

### MultEval — collaborative criteria are themselves an empirical object

- First public date: arXiv v1, **2026-04-29**, before cutoff.
- Primary: https://arxiv.org/abs/2604.26679
- Compared claim: C5.
- Classification: `boundary_condition`, **moderate**.

MultEval documents that LLM-judge criteria encode stakeholder assumptions and that domain experts can disagree over how criteria should be operationalized. CPC anchoring improves auditability but does not by itself establish measurement invariance across criminal, tax, pension, procurement and other judicial domains.

**Required action:** `add_control`: expert co-design and stratum-specific measurement-invariance/reliability checks.

## 9. Revised truth status

| Claim | Priority status | Truth status after this run | Required action |
|---|---|---|---|
| C1 SPH | specific directional hypothesis remains not materially anticipated in the earlier audit | plausible but confounded; no empirical support yet | `narrow_claim`, `add_control`, `downgrade_confidence` |
| C2 full-ranking reconstruction | generic hierarchical ranking has extensive prior art | **false as stated** by direct counterexample | `retract_claim` / `revise_mechanism` |
| C3 99.7% example | not a novelty question | **false as stated** by direct count | `retract_claim` and correct numbers |
| C4 diverse jury reduces bias | panel methods are prior art | supported in some benchmarks, but shared bias survives diversity | `add_boundary_condition`, `add_control` |
| C5 LLM panel proxies legal quality | legal LLM judging is prior/adjacent territory | external validity remains unestablished; legal counter-evidence is material | `add_control`, `downgrade_confidence` |
| C6 ESHTR advantage | full conjunction remains narrower than components | untested against strong matched-cost baselines | `add_control` |

## 10. Discriminating experiment now required

A credible SPH/ESHTR validation should cross semantic distance against comparison difficulty instead of using only `κ_intra` versus `κ_cross`.

Freeze the following design before observing results:

1. Build an expert-annotated anchor subset spanning procedural/subject strata, with pairwise quality judgments and criterion scores.
2. Construct pairs/triples crossing **semantic distance × expert quality margin**, rather than allowing semantic proximity and difficulty to co-vary.
3. Randomize order and create legally irrelevant style/rhetoric variants of the same decisions.
4. Compare at matched judge-call budget: current ESHTR, round-robin subsampling/BT, SWIM-like matchmaking, a bridge/pivot hierarchical method, and pointwise/reference-based rubric scoring.
5. Primary validity endpoint: agreement/rank correlation with expert ground truth. Secondary endpoints: cycle rate, calibration, style/position sensitivity, bootstrap rank uncertainty and cost.
6. For any full global ranking, require a connected cross-cluster comparison graph or explicit score-linking model; test recovery on held-out expert rankings.

**SPH survives as mechanism only if** semantic distance predicts error/cycle incidence after conditioning on quality margin and the other preregistered covariates. If the coefficient is null/reversed, or clustering fails to improve expert-valid ranking at matched budget, downgrade the semantic-distance mechanism even if ESHTR remains a useful engineering heuristic.

## 11. Search protocol and negative results

Sources/bases consulted in this round: GitHub history, arXiv, PMLR/ICML primary record, and targeted web discovery around LLM judging, legal evaluation and evaluation-criteria design.

Representative queries:

- `Investigating Non-Transitivity LLM judge performance similarity`
- `pairwise pointwise LLM judge distracted evaluation bias`
- `LLM judge style bias different provider families`
- `legal LLM as judge human expert official committee`
- `LLM judge criteria stakeholder disagreement`
- `semantic distance non-transitivity LLM judge`
- `semantic clustering LLM-as-a-judge ranking 2026`
- `hierarchical tournament LLM judge ranking 2026`
- exact title and `Embedding-Seeded Hierarchical Tournament Ranking`

A post-cutoff pass did **not** locate a materially overlapping work first disclosed after 2026-05-10 that reproduces the full ESHTR conjunction closely enough to justify `later_non_citing`, `later_overlap`, `later_citing` or `later_derivative`. This is a bounded negative search, not evidence that no such work exists.

## 12. Audit conclusion

The material update is not a priority reversal. The 2026-09-17 audit's central novelty picture largely stands. The important change is on the **truth/status and method axis**: two claims are formally wrong as written (full global-ranking reconstruction and the 99.7% comparison example), SPH has a major comparison-difficulty confound that the current κ-only design does not isolate, pairwise evaluation has a documented distractor failure mode, and heterogeneous LLM juries require expert-human legal validity checks because cross-family shared biases remain possible.

These findings justify immediate correction of the two formal claims and a stricter preregistered experiment before treating semantic proximity as a causal explanation for improved judicial-ranking reliability.