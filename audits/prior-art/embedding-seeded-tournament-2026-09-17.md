---
type: "Audit Report"
title: "Embedding-Seeded Hierarchical Tournament Ranking prior-art audit — 2026-09-17"
description: "Claim-specific, temporally grounded prior-art audit of ESHTR and the Semantic Proximity Hypothesis, including divide-and-conquer paired ranking, representation-informed pre-ordering, LLM pairwise judging, context-dependent intransitivity, and Brazilian legal multi-judge evaluation."
tags: [eshtr, prior-art, llm-as-judge, pairwise-ranking, clustering, semantic-proximity, judicial-evaluation, legal-ai]
timestamp: 2026-09-17T22:00:00-04:00
---

# Embedding-Seeded Hierarchical Tournament Ranking prior-art audit — 2026-09-17

> **Status:** first claim-specific, reproducible prior-art audit of ESHTR and its Semantic Proximity Hypothesis. The audit materially narrows several component-level novelty claims. It does **not** establish exhaustive novelty, patent novelty, independent invention, copying, or causal dependence between projects. Negative search results below mean only that no material antecedent was located under the recorded search protocol.

## 1. Audited claims and claim-specific cutoff

The current paper, [`embedding_seeded_tournament.md`](../../embedding_seeded_tournament.md), proposes **Embedding-Seeded Hierarchical Tournament Ranking (ESHTR)** for judicial-decision quality evaluation. For this audit the paper is decomposed into six claims:

- **C1 — pairwise LLM ranking:** use LLM evaluators to compare items pairwise and aggregate those comparisons into a ranking;
- **C2 — hierarchical / divide-and-conquer pairwise ranking:** avoid exhaustive global comparison by ranking within groups and comparing a much smaller set of representatives across groups;
- **C3 — representation-informed seeding:** use an external semantic representation or embedding-derived structure before pairwise ranking so that early comparisons are made among more locally comparable items;
- **C4 — Semantic Proximity Hypothesis (SPH):** for LLM judges, the incidence of preference non-transitivity is predicted to increase with semantic distance between compared items, because semantically distant comparisons destabilize the evaluative frame; therefore semantic-locality seeding should improve consistency;
- **C5 — Brazilian judicial evaluation with a heterogeneous LLM panel:** evaluate legal/judicial writing with explicit legal rubrics using several independent LLM judges;
- **C6 — full ESHTR conjunction:** dense semantic clustering of judicial decisions → within-cluster heterogeneous-LLM pairwise ranking → cross-cluster championship among local winners, motivated specifically by C4.

### 1.1 GitHub reconstruction

The paper first appears in repository history as `embedding_seeded_tournament_paper.md` in commit:

- [`872de345e9a67a6631966b33a0b69461aff6d433`](https://github.com/franklinbaldo/papers/commit/872de345e9a67a6631966b33a0b69461aff6d433), **2026-05-10 14:37:39 UTC**, message `Add files via upload`.

The parent commit does not contain the file. The introducing patch already contains all material elements relevant to this audit: dense semantic grouping, within-cluster LLM-panel pairwise tournaments, cross-cluster championship among winners, the SPH-style claim that semantically distant comparisons increase preference inconsistency/non-transitivity, and a Brazilian-CPC-anchored heterogeneous judge panel. The later rename to `embedding_seeded_tournament.md` does not affect priority.

**Cutoff for C1–C6: 2026-05-10 14:37:39 UTC.**

This is the earliest public GitHub state located for the claims, not the present file timestamp and not the repository creation date.

## 2. Search protocol

The audit searched GitHub history plus literature sources including arXiv, ACL Anthology, PMLR/ICML, IJCAI proceedings, DBLP-style bibliographic records, and primary project/publisher pages where available. Search terms were expanded beyond the paper's name to cover historical terminology and decomposed mechanisms.

Representative queries included:

- `divide and conquer paired comparisons ranking groups pivots Bradley Terry`
- `hierarchical pairwise ranking clustering representatives tournament`
- `embedding pre-ordering pairwise ranking semantic prior`
- `CLIP hierarchical pre-ordering pairwise ranking reliability`
- `simultaneous clustering ranking pairwise comparisons`
- `LLM pairwise ranking prompting sorting tournament`
- `LLM judge non-transitivity round robin tournament`
- `context dependent salient features pairwise intransitivity`
- `semantic distance LLM judge non-transitivity`
- `LLM judge pairwise semantic context coherence`
- `Brazilian legal benchmark multi LLM judges rubric magistrate judicial`
- `cluster aware LLM-as-a-judge ranking`
- exact-title, `ESHTR`, `Embedding-Seeded Hierarchical Tournament Ranking`, and `Franklin Baldo` searches for later overlap.

A later-work pass separately searched post-cutoff 2026 literature for combinations of semantic clustering/embedding seeding, pairwise LLM judging, tournaments and legal evaluation. Superficial uses of the word “cluster” (for example, cluster-robust statistical inference rather than semantic comparison grouping) were not treated as overlap.

## 3. Findings before our cutoff

### 3.1 Pairwise Ranking Prompting already established LLMs as pairwise text rankers

**Work:** Zhen Qin et al., **“Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting.”**

- First public version located: arXiv v1, **2023-06-30 11:32:25 UTC**.
- Later venue: Findings of NAACL 2024.
- Primary source: <https://arxiv.org/abs/2306.17563>
- Publisher: <https://aclanthology.org/2024.findings-naacl.97/>

**Compared claim:** C1.

**Classification:** `prior_art` for off-the-shelf LLM pairwise ranking; `partial_prior_art` for ESHTR as a whole.

Qin et al. explicitly reformulate ranking as pairwise LLM comparisons and propose multiple aggregation/scheduling variants, including sorting-based schemes with subquadratic complexity. Thus neither “LLM as pairwise ranker” nor “use a sorting schedule rather than all pairs” is an ESHTR novelty.

**Difference:** the task is information retrieval rather than quality evaluation; there is no semantic clustering of the candidate set, no heterogeneous LLM jury, no local-champion cross-cluster stage and no SPH.

### 3.2 CrowDC is direct prior art for the divide-group / local-rank / cross-group-representative architecture

**Work:** Ming-Hung Wang, Chia-Yuan Zhang, Jia-Ru Song, **“CrowDC: A Divide-and-Conquer Approach for Paired Comparisons in Crowdsourcing.”**

- arXiv v1: **2023-02-23 00:59:35 UTC**.
- Primary source: <https://arxiv.org/abs/2302.11722>

**Compared claims:** C2 and structural part of C6.

**Classification:** `prior_art` for divide-and-conquer paired-comparison ranking with local groups plus cross-group representatives; strong `partial_prior_art` for C6.

CrowDC divides items into subsets, obtains within-group Bradley–Terry scores, chooses multiple pivots from each group, compares the pooled pivots across groups, and then aligns/merges the local scores into a global ranking. Its objective is exactly the same generic scalability problem that motivates ESHTR: avoid quadratic all-pairs cost while retaining useful global ranking information.

This is materially closer than a generic citation to Swiss tournaments. ESHTR’s “rank locally, then compare a reduced cross-group set” architecture therefore has a clear pre-cutoff antecedent.

**Difference:** CrowDC’s grouping is not semantic-embedding seeding designed to stabilize an LLM judge; evaluators are crowdsourcing subjects rather than LLM panels; pivots span each local score range rather than only promoting winners; and there is no judicial domain or SPH.

### 3.3 SCARPA already joins clustering structure and pairwise preference ranking

**Work:** Jiyi Li, Yukino Baba, Hisashi Kashima, **“Simultaneous Clustering and Ranking from Pairwise Comparisons.”**

- Venue: IJCAI 2018, pp. 1554–1560.
- DOI: <https://doi.org/10.24963/ijcai.2018/215>
- Primary proceedings page: <https://www.ijcai.org/Proceedings/2018/215>

**Compared claims:** conceptual bridge behind C3.

**Classification:** `partial_prior_art`.

SCARPA explicitly asks whether similarity comparisons used for clustering can improve ranking and vice versa, and jointly estimates embeddings and a preference direction from pairwise similarity/preference observations. It establishes well before ESHTR that item similarity structure and pairwise preference ranking can be coupled rather than treated as unrelated tasks.

**Difference:** SCARPA learns clustering/ranking jointly from pairwise observations. ESHTR instead imports an independently computed dense semantic geometry as a scheduling/seeding mechanism for a downstream judge. The hierarchical local-winner championship and SPH are absent.

### 3.4 EZ-Sort is strong prior art for representation-informed pre-ordering before pairwise ranking

**Work:** Yujin Park, Haejun Chung, Ikbeom Jang, **“EZ-Sort: Efficient Pairwise Comparison via Zero-Shot CLIP-Based Pre-Ordering and Human-in-the-Loop Sorting.”**

- arXiv v1: **2025-08-29 12:06:49 UTC**.
- Accepted at CIKM 2025.
- Primary source: <https://arxiv.org/abs/2508.21550>
- DOI: <https://doi.org/10.1145/3746252.3760848>

**Compared claims:** C3 and scalability motivation of C6.

**Classification:** `prior_art` for using pretrained representation similarity as a pre-ranking/seeding prior before pairwise comparisons; strong `partial_prior_art` for ESHTR.

EZ-Sort first uses CLIP to produce a zero-shot hierarchical pre-ordering, then initializes bucket-aware Elo scores and runs uncertainty-guided human-in-the-loop MergeSort. Its own abstract frames the benefit as combining a semantic/VLM prior with selective pairwise comparison to improve efficiency while maintaining or improving inter-rater reliability.

This materially narrows any generic ESHTR claim of novelty based merely on “embedding/semantic representation first, pairwise ranking second.”

**Difference:** EZ-Sort’s hierarchy is prompt-defined coarse ordering for visual criteria, not unsupervised semantic clustering of heterogeneous legal documents; it does not posit that semantic distance causes LLM-judge non-transitivity; the pairwise evaluator is human rather than an LLM jury; and it does not use local cluster winners followed by a cross-cluster championship.

### 3.5 Dodgersort strengthens the same antecedent with reliability and probabilistic ranking

**Work:** Yujin Park, Haejun Chung, Ikbeom Jang, **“Dodgersort: Uncertainty-Aware VLM-Guided Human-in-the-Loop Pairwise Ranking.”**

- arXiv v1: **2026-03-21 14:55:49 UTC**.
- PAKDD 2026.
- Primary source: <https://arxiv.org/abs/2603.20839>

**Compared claims:** C3 and reliability/scalability rationale around C6.

**Classification:** strong `partial_prior_art`.

Dodgersort combines CLIP-based hierarchical pre-ordering, a learned ranking head, Elo/BTL/GP aggregation and uncertainty-aware pair selection. It reports improved inter-rater reliability while reducing comparisons, and its method explicitly uses a representation-derived coarse structure to reserve difficult local comparisons for richer treatment.

The work is particularly important because it was public **50 days before** the ESHTR cutoff and already links representation-informed pre-ordering to more reliable pairwise ranking. The component-level space is therefore substantially occupied before our claim.

**Difference:** the evaluator remains human; the representation prior is aligned to a known visual ranking criterion rather than used to cluster heterogeneous documents by semantic type; there is no LLM-judge non-transitivity hypothesis and no local-winner cross-cluster tournament.

### 3.6 LLM-judge non-transitivity and tournament mitigation were already explicit

**Work:** Yi Xu, Laura Ruis, Tim Rocktäschel, Robert Kirk, **“Investigating Non-Transitivity in LLM-as-a-Judge.”**

- arXiv v1: **2025-02-19 19:59:16 UTC**.
- ICML 2025.
- Primary source: <https://arxiv.org/abs/2502.14074>
- PMLR: <https://proceedings.mlr.press/v267/xu25w.html>

**Compared claims:** C1, motivation for C2/C4.

**Classification:** `prior_art` for identifying LLM-judge non-transitivity and using round-robin / Bradley–Terry tournament methods to mitigate ranking instability; `partial_prior_art` for ESHTR.

Xu et al. directly show non-transitive preferences in LLM judges and that rankings can depend on the chosen baseline. They propose round-robin plus Bradley–Terry and SWIM, a dynamic matchmaking approximation, to recover more reliable rankings at lower cost.

**Difference:** the paper does not use semantic distance as a scheduling variable. Its analyses implicate position bias and model/performance relationships rather than establishing C4.

### 3.7 Context-dependent salient features are a pre-LLM mechanism for pair-dependent intransitivity

**Work:** Amanda Bower, Laura Balzano, **“Preference Modeling with Context-Dependent Salient Features.”**

- arXiv v1: **2020-02-22 04:05:16 UTC**.
- ICML 2020, PMLR 119:1067–1077.
- Primary source: <https://arxiv.org/abs/2002.09615>
- PMLR: <https://proceedings.mlr.press/v119/bower20a.html>

**Compared claim:** mechanism proposed for C4.

**Classification:** `partial_prior_art` for the evaluative-frame mechanism; not prior art for the directional SPH itself.

Bower and Balzano model pairwise choice in which only a context-dependent subset of item features becomes salient. They show that this can explain systematic intransitivity. That is a close theoretical antecedent to ESHTR’s informal argument that different pairs can activate different evaluative criteria and thereby create cycles.

**Difference:** the paper neither uses LLM judges nor claims that semantic distance monotonically increases non-transitivity. It therefore narrows the originality of the explanatory mechanism while leaving C4’s specific directional hypothesis open.

### 3.8 Semantic Needles provides near-cutoff evidence that semantic context changes LLM pairwise scoring

**Work:** Sinan G. Aksoy, Alexandra A. Sabrio, Erik VonKaenel, Lee Burke, **“Semantic Needles in Document Haystacks: Sensitivity Testing of LLM-as-a-Judge Similarity Scoring.”**

- arXiv v1: **2026-04-20 20:59:25 UTC**, about 20 days before the ESHTR cutoff.
- Primary source: <https://arxiv.org/abs/2604.18835>

**Compared claim:** C4 mechanism.

**Classification:** strong `partial_prior_art` for semantic/contextual framing effects in LLM pairwise evaluation; not prior art for the SPH’s distance→non-transitivity relation.

The study varies perturbations, document context and position over tens of thousands of pairwise document judgments. Topically unrelated surrounding context systematically shifts similarity scores and produces strongly polarized scoring; the authors interpret the result through an “interpretive frame” account. This is unusually close to ESHTR’s mechanism-level story that semantic context changes how a judge frames a comparison.

**Difference:** the outcome is similarity scoring, not preference-cycle incidence or quality ranking. It does not establish that larger embedding distance increases non-transitivity.

### 3.9 Diverse LLM juries predate ESHTR

**Work:** Pat Verga et al., **“Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models.”**

- arXiv v1: **2024-04-29 15:33:23 UTC**.
- Primary source: <https://arxiv.org/abs/2404.18796>

**Compared claim:** heterogeneous-panel part of C5.

**Classification:** `prior_art`.

The paper proposes a panel of diverse LLM evaluators and reports lower bias / better evaluation than relying on one large judge. ESHTR already cites this line correctly; the audit records that a heterogeneous synthetic jury is an inherited component, not an originality-bearing part of C6.

### 3.10 Magis-Bench predates ESHTR by less than two days in the Brazilian judicial-evaluation niche

**Work:** Ramon Pires et al., **“Magis-Bench: Evaluating LLMs on Magistrate-Level Legal Tasks.”**

- arXiv v1: **2026-05-08 20:00:14 UTC**.
- ICAIL 2026 short paper.
- Primary source: <https://arxiv.org/abs/2605.08437>
- Repository: <https://github.com/maritaca-ai/magis-bench>

**Compared claim:** C5 and domain-specific part of C6.

**Classification:** `prior_art` for Brazilian magistrate-level legal evaluation with explicit rubrics and multiple independent frontier LLM judges; strong `partial_prior_art` for C6.

Magis-Bench evaluates 23 LLMs on 74 tasks derived from Brazilian judicial-selection examinations, including complete civil and criminal judgment drafting. Its original paper evaluation uses **four independent frontier models as judges** and reports inter-judge agreement. The benchmark uses official examination rubrics.

The date is important: the primary arXiv submission history is **8 May 2026 20:00:14 UTC**, whereas ESHTR first appears in GitHub on **10 May 2026 14:37:39 UTC** — about 42.6 hours later. Some secondary indexes display later May dates; those must not be used to invert the temporal order.

**Difference:** Magis-Bench scores model outputs on magistrate-level tasks; it does not rank a heterogeneous corpus of real judicial decisions through semantic clustering, pairwise local tournaments and a championship stage. It also does not propose C4.

### 3.11 Anchor-selection work shows that comparison scheduling itself affects LLM-judge reliability

**Work:** Shachar Don-Yehiya, Asaf Yehudai, Leshem Choshen, Omri Abend, **“Mediocrity is the key for LLM as a Judge Anchor Selection.”**

- arXiv v1: **2026-03-17 17:54:08 UTC**.
- ACL 2026.
- Primary source: <https://arxiv.org/abs/2603.16848>

**Compared claim:** scheduling/reliability rationale underlying C2/C4.

**Classification:** `adjacent_prior_work`.

The work shows that which anchor is chosen in pairwise LLM evaluation substantially changes reliability and that extreme anchors can be poor choices. This reinforces the general pre-cutoff proposition that pair selection is not neutral in LLM-as-a-judge pipelines.

**Difference:** anchor quality is about relative model strength, not semantic proximity between evaluated texts, so it does not anticipate C4.

## 4. Claim-level assessment after the pre-cutoff search

| Claim | Assessment | Reason |
| --- | --- | --- |
| C1 — pairwise LLM ranking | `prior_art` | PRP and later LLM-as-judge work clearly predate ESHTR. |
| C2 — hierarchical/divide-and-conquer paired ranking | `prior_art` | CrowDC already ranks within groups and uses cross-group representatives; Xu et al. also establish tournament/matchmaking mitigation for LLM judging. |
| C3 — representation-informed seeding before pairwise ranking | `prior_art` at the generic mechanism level; `partial_prior_art` for ESHTR’s semantic-cluster form | EZ-Sort/Dodgersort use pretrained representation structure to pre-order pairwise ranking and improve efficiency/reliability; SCARPA couples clustering and ranking. |
| C4 — SPH: semantic distance increases LLM-judge non-transitivity | **not located as an antecedent in this audit** | Context-dependent salience and semantic framing effects predate us, but no inspected source states or tests the specific monotonic semantic-distance→non-transitivity hypothesis. |
| C5 — Brazilian legal evaluation with heterogeneous LLM panel | `prior_art` | Verga et al. predate the panel component; Magis-Bench predates the Brazilian magistrate/rubric/multi-judge instantiation by ~42.6 hours. |
| C6 — full ESHTR conjunction | no complete antecedent located | The parts are heavily occupied, but no inspected pre-cutoff work combines semantic clustering of judicial decisions, within-cluster heterogeneous-LLM pairwise ranking, cross-cluster winner championship, and SPH as the reason for clustering. |

The scientific novelty boundary is therefore substantially narrower than “embedding seeding + hierarchical tournament ranking” in the abstract. That phrase by itself now overlaps too strongly with EZ-Sort/Dodgersort plus CrowDC. The potentially distinctive scientific contribution is the **specific conjunction and its falsifiable mechanism**: dense semantic *type* clustering used to alter the comparison graph of an LLM jury because semantic distance is hypothesized to increase cycle inconsistency, followed by a cross-type championship in the judicial domain.

## 5. Status of the Semantic Proximity Hypothesis

This audit did **not** locate a pre-cutoff paper that tests the directional statement:

> holding judge, rubric and comparison budget fixed, LLM-judge non-transitivity increases as semantic distance between evaluated items increases.

However, the search also does not permit treating the hypothesis as established or presumptively true. The prior literature creates a more demanding baseline:

- Bower & Balzano show that pair-dependent salient features can cause systematic intransitivity, supporting the possibility of comparison-frame drift without establishing a semantic-distance gradient;
- Semantic Needles shows that topical/context coherence materially changes LLM pairwise scoring, supporting the plausibility of semantic framing effects without measuring preference cycles;
- Xu et al. show that LLM judges are non-transitive and that scheduling/aggregation matter, but their identified factors are not the ESHTR semantic-distance variable;
- anchor-selection results likewise show that the comparison graph can affect reliability for reasons unrelated to semantic distance.

Accordingly, C4 should remain a **falsifiable empirical hypothesis**, not a literature-established premise. A decisive experiment needs matched pairs/triples in which semantic distance varies while judge, legal rubric, item quality gap, text length, procedural stage and position order are controlled.

## 6. Post-cutoff search and later work

A separate search covered material published after **2026-05-10 14:37:39 UTC** using combinations of `semantic cluster`, `embedding`, `pairwise ranking`, `LLM-as-a-judge`, `tournament`, `hierarchical ranking`, `legal evaluation`, the exact ESHTR title/acronym and the author name.

### 6.1 Later cluster-aware / semantic-selection work did not reproduce the ESHTR conjunction

Post-cutoff papers were found that use “cluster-aware” statistics in LLM-as-a-judge evaluation or semantic-diversity selection under query budgets. The inspected examples address statistical dependence, benchmark construction, active query selection or judge extraction, not semantic-locality tournament seeding for quality ranking.

Examples include:

- **“A Fixed-Budget, Cluster-Aware Standard for LLM-as-a-Judge Evaluation: A Multi-Hop RAG Stress Test”**, arXiv v1 **2026-05-27** — “cluster-aware” refers primarily to statistical inference over clustered benchmark data, not local semantic tournament brackets;
- **“JudgeStealer: Extracting LLM Judging Capabilities across Evaluation Protocols”**, arXiv v1 **2026-08-27** — uses semantic diversity, predictive uncertainty and bias signals for query-efficient extraction of judge behavior, not ESHTR-style judicial ranking.

**Classification:** `later_independent` only at the broad level of semantic/query-structure-aware evaluation; not material enough to classify as `later_non_citing` against C6.

### 6.2 No material post-cutoff non-citing duplicate located

Exact-title/acronym/author searches and decomposed searches did **not** locate, in this run, a post-cutoff work that materially reproduces C6 closely enough to justify `later_non_citing` or `later_overlap` for the full claim. This is a scoped negative search result, not evidence that no such work exists.

No causal claim about copying, derivation or independent invention is made for any later work.

## 7. Revision relative to the current paper

The current paper’s narrow sentence — “the specific combination of embedding-based seeding and hierarchical tournament ranking for judicial decision quality evaluation has not been proposed” — is not directly falsified by the sources inspected, because no earlier work was found with the **full judicial ESHTR conjunction**.

But the literature boundary around that sentence is now much tighter:

1. **hierarchical/grouped paired ranking is not new** (CrowDC);
2. **representation-informed pre-ordering before pairwise ranking is not new** (EZ-Sort/Dodgersort);
3. **clustering and pairwise ranking have long been jointly modeled** (SCARPA);
4. **pairwise LLM ranking and tournament mitigation of non-transitivity are not new** (Qin et al.; Xu et al.);
5. **heterogeneous LLM juries are not new** (Verga et al.);
6. **Brazilian magistrate-level rubric-based multi-LLM judging was publicly disclosed before ESHTR** (Magis-Bench);
7. **pair-dependent evaluative salience and semantic/context framing effects predate the SPH mechanism** (Bower & Balzano; Semantic Needles).

The audit therefore recommends describing the candidate novelty, if retained, as the **full comparison-graph design plus the semantic-distance non-transitivity hypothesis**, rather than novelty in any individual component.

## 8. Experimental consequence

The prior-art search yields a sharper validation ladder. A convincing ESHTR experiment should compare, under matched judge/rubric/budget conditions:

1. all-pairs or round-robin + Bradley–Terry;
2. random-group divide-and-conquer ranking in the style of CrowDC;
3. sorting/tournament scheduling without semantic information;
4. representation-informed pre-ordering without explicit clusters (EZ-Sort/Dodgersort-like control);
5. semantic clustering with random cross-cluster representatives;
6. semantic clustering with ESHTR local-winner championship;
7. the same designs with one judge versus a heterogeneous panel.

Separately, the SPH should be tested directly by estimating cycle incidence as a function of embedding distance after matching or conditioning on objective/consensus quality gap, text length, legal subject, procedural stage, order randomization and judge identity. If semantic distance has no independent effect after these controls, the main theoretical motivation for ESHTR weakens even if the scheduling method remains computationally useful.

## 9. Audit conclusion

After reconstructing the claim cutoff from GitHub and searching the decomposed claims, the strongest revision is:

- **C1, C2, generic C3 and C5 have substantial pre-cutoff prior art.**
- **C4 remains an unverified claim for which no direct pre-cutoff anticipation was located in this run, although its mechanism has important antecedents.**
- **No complete pre-cutoff anticipation of C6 was located**, but C6 is a combination of heavily occupied components and should be presented and tested accordingly.

The most consequential newly surfaced sources are **CrowDC**, **EZ-Sort/Dodgersort**, and **Magis-Bench**. Magis-Bench is especially sensitive temporally: its primary arXiv v1 predates the ESHTR GitHub cutoff by only about 42.6 hours, so using a later secondary-index date would incorrectly reverse priority.
