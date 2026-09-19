---
type: "Audit Report"
title: "Semantic Tokenization Transformers grounding / hallucination falsification audit — 2026-09-19"
description: "Claim-specific adversarial validity audit of STT's retrieval-grounded decoding, F1/F2 taxonomy, n-gram hallucination metric, and embedding-based proto-text fidelity test."
tags: [stt, falsification, contrary-evidence, hallucination, groundedness, retrieval, factuality, semantic-similarity]
timestamp: 2026-09-19T02:00:58-04:00
---

# Semantic Tokenization Transformers grounding / hallucination falsification audit — 2026-09-19

> **Status:** adversarial truth-status audit complementing the novelty-focused [`semantic-tokenization-transformers-2026-09-18.md`](semantic-tokenization-transformers-2026-09-18.md). The two axes are kept separate: older work may limit the plausibility of STT without anticipating its architecture, and later work may contradict a hypothesis without becoming prior art. This audit does not infer copying, plagiarism, bad faith, or causal dependence.

## 1. Target and temporal reconstruction

The audited object is [`semantic_tokenization_transformers.md`](../../semantic_tokenization_transformers.md), especially its current claims around retrieval-grounded decoding and the F1/F2 failure-mode split.

There are two relevant public cutoffs because the claim changed materially over time.

### 1.1 Broad anti-hallucination claim

The earliest verified public GitHub version is commit [`7e8cbf1f4ab079d9a3f1299c066f4f7f1094dcfb`](https://github.com/franklinbaldo/papers/commit/7e8cbf1f4ab079d9a3f1299c066f4f7f1094dcfb), **2025-11-11 13:31:25 UTC**. The original file already stated that medoid-based retrieval plus disciplined LLM normalization would preserve factual content "without hallucination" and described "strong guarantees against hallucination." Those empirical-looking statements were later correctly withdrawn/reframed.

### 1.2 Current narrow F1/F2 formulation

The current claim is materially narrower and should not inherit the 2025 cutoff automatically. Commit [`e795c8e3649edab3e35f8c37a1ae6afc4d832d33`](https://github.com/franklinbaldo/papers/commit/e795c8e3649edab3e35f8c37a1ae6afc4d832d33) introduced the explicit distinction between:

- **F1:** normalizer-generated content absent from the proto-text; and
- **F2:** an upstream wrong-medoid / retrieval-fidelity error.

The conservative public cutoff for that formulation is the creation of PR [#50](https://github.com/franklinbaldo/papers/pull/50), **2026-05-27 10:15:31 UTC**. The PR states that the `DO NOT Add new information` instruction prevents F1, while F2 is detectable by proto-text fidelity (PTF) and not correctable in V1.

All literature used as `prior_art`, `contrary_evidence`, or `boundary_condition` against the current F1/F2 formulation below was public before **2026-05-27 10:15:31 UTC**, unless explicitly labeled later evidence.

## 2. Claims and falsifiers

### H1 — Instruction-constrained normalization can bound F1

**Current proposition:** given a retrieved proto-text, a disciplined normalizer instructed not to add information should improve fluency while keeping F1-type unsupported additions below a preregistered ceiling.

**Would be wrong or materially too strong if:** systems given relevant/accurate source evidence and grounding instructions still generate unsupported or contradictory propositions at material rates; or the proposed instruction does not outperform a matched ordinary grounding prompt on claim-level unsupported-content rate.

### H2 — N-gram novelty is an adequate F1 metric

**Current operationalization:** hallucination rate is principally the percentage of generated n-grams not in proto-text, with a target ceiling such as 1%.

**Would be wrong or materially too narrow if:** outputs can retain source n-grams while changing entity bindings, numbers, negation, relations, entailment, or attribution; or lexical-overlap metrics correlate poorly with human factuality/faithfulness.

### H3 — Embedding-similarity PTF resolves the F2 detection gap

**Current supportive formulation:** compare proto-text embedding with a reference/source embedding using the teacher model; this is said to identify F2 before normalization.

**Would be wrong or materially too strong if:** semantically plausible but factually wrong texts remain close in embedding space; embeddings fail important negation/antonym/entity distinctions; or embedding-based hallucination detection has an unacceptably high error rate on realistic benchmarks.

### H4 — Retrieval grounding is a risk reducer, not a correctness guarantee

This is the narrower hypothesis that survives if H1-H3 are qualified.

**Would be wrong if:** matched controlled studies show no systematic reduction in unsupported claims relative to an ungrounded baseline under the intended deployment regime.

## 3. Search protocol

Primary-source searches covered ACL Anthology and arXiv, with targeted discovery queries for summarization factuality, RAG hallucination, source faithfulness, conformal correctness guarantees, embedding semantic alignment, and post-cutoff mechanisms. Representative queries:

- `retrieval augmented generation hallucination unsupported contradictory retrieved contents`
- `grounded generation hallucination accurate sufficient context`
- `RAG correctness guarantee conformal prediction`
- `abstractive summarization factuality faithfulness entailment ROUGE hallucination`
- `hallucination metric n-gram overlap factuality correlation`
- `sentence embeddings negation antonym semantic similarity limitations`
- `embedding based hallucination detection RAG false positive`
- `retrieved context accurate sufficient hallucination parametric knowledge`
- `grounding instruction does not prevent hallucination`
- `claim level factual consistency source document metric`

Negative searches included exact-title / author queries for later papers citing STT and searches for direct replications of STT's exact medoid+Viterbi+LCS+normalizer pipeline. No such replication was located in this run; that is a bounded search result, not evidence of nonexistence.

## 4. Pre-cutoff contrary evidence and boundary conditions

### 4.1 Maynez et al. 2020 — source-conditioned generation still hallucinates, and lexical metrics are not enough

**Work:** Joshua Maynez, Shashi Narayan, Bernd Bohnet, Ryan McDonald, *On Faithfulness and Factuality in Abstractive Summarization*.

- public proceedings: ACL 2020, July 2020;
- primary source: https://aclanthology.org/2020.acl-main.173/
- DOI: 10.18653/v1/2020.acl-main.173.

Large-scale human evaluation found substantial hallucinated content across abstractive summarizers conditioned on source documents. The paper also reports that textual-entailment measures correlate better with faithfulness than standard summarization metrics.

**Targets:** H1, H2.

**Classification:** `contrary_evidence`.

**Strength:** **strong for H2**, **moderate for H1 transfer to STT**. It directly undermines the assumption that source-conditioned generation plus surface similarity is enough to establish faithfulness, although the exact STT normalizer prompt was not tested.

**Required change:** `add_control` + `revise_mechanism`. Keep lexical novelty as a surface-copy statistic, not as the factuality certificate; add entailment/claim-level checks.

### 4.2 TRAQ 2023 — retrieval augmentation does not itself provide correctness guarantees

**Work:** Shuo Li, Sangdon Park, Insup Lee, Osbert Bastani, *TRAQ: Trustworthy Retrieval Augmented Question Answering via Conformal Prediction*.

- arXiv v1: **2023-07-07 02:42:06 UTC**;
- primary source: https://arxiv.org/abs/2307.04642
- NAACL 2024: https://aclanthology.org/2024.naacl-long.210/

TRAQ starts from the explicit limitation that RAG is promising for hallucination reduction but **does not provide correctness guarantees**, and adds conformal prediction to obtain a statistical guarantee.

**Targets:** H1, H4; especially any use of the words `guarantee` or `bounded` as an architectural property rather than an empirically estimated rate.

**Classification:** `boundary_condition`.

**Strength:** **strong**.

**Required change:** `narrow_claim` + `downgrade_confidence`. A preregistered empirical ceiling is a test target; it is not a guarantee before calibration/validation. If STT wants a guarantee, it needs a statistical coverage construction or comparably explicit guarantee mechanism.

### 4.3 RAGTruth 2023/2024 — retrieved evidence does not prevent unsupported or contradictory claims

**Work:** Cheng Niu et al., *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models*.

- arXiv v1: **2023-12-31 04:43:45 UTC**;
- primary source: https://arxiv.org/abs/2401.00396
- ACL 2024: https://aclanthology.org/2024.acl-long.585/

RAGTruth contains nearly 18,000 naturally generated RAG responses with manual hallucination annotation. The central empirical observation is directly relevant: even with retrieved evidence, LLMs produce unsupported or contradictory claims relative to that evidence.

**Targets:** H1 and H4.

**Classification:** `contrary_evidence`.

**Strength:** **strong against architectural prevention**, **moderate against the narrower ≤1% STT empirical target** because STT's exact prompt and proto-text construction are different.

**Required change:** `narrow_claim` + `add_control`. Treat the STT F1 ceiling as an empirical hypothesis requiring a matched RAG/source-grounded baseline, not a consequence of the instruction.

### 4.4 Stolfo 2024 — ungrounded sentences remain common in retrieval-augmented long-form generation

**Work:** Alessandro Stolfo, *Groundedness in Retrieval-augmented Long-form Generation: An Empirical Study*.

- arXiv v1: **2024-04-10 14:50:10 UTC**;
- primary source: https://arxiv.org/abs/2404.07060

Across three datasets and four model families, a significant fraction of generated sentences remains ungrounded despite retrieval. Larger models improve grounding but do not remove the issue.

**Targets:** H1, H4/generalization.

**Classification:** `contrary_evidence`.

**Strength:** **moderate-to-strong**.

**Required change:** `add_boundary_condition` + `add_control`.

### 4.5 Dong, Wieting & Verga 2022 — faithfulness-to-source and factuality-in-world are different constructs

**Work:** *Faithful to the Document or to the World? Mitigating Hallucinations via Entity-Linked Knowledge in Abstractive Summarization*.

- Findings of EMNLP 2022, December 2022;
- primary source: https://aclanthology.org/2022.findings-emnlp.76/

The paper shows that output may be unfaithful to the source while still factually true by virtue of external knowledge. The inverse distinction also matters for STT: a string may be highly source-like while asserting the wrong relationship for the intended document.

**Targets:** H2; construct validity of the word `hallucination`.

**Classification:** `boundary_condition`.

**Strength:** **strong conceptual boundary**.

**Required change:** `narrow_claim`. Report at least two constructs separately: source/proto-text faithfulness and world/document factual correctness.

### 4.6 HaRiM+ 2022 and prior factuality work — factual consistency requires a dedicated signal

**Work:** Seonil Son et al., *HaRiM+: Evaluating Summary Quality with Hallucination Risk*.

- arXiv v1: **2022-11-22 09:36:41 UTC**;
- primary source: https://arxiv.org/abs/2211.12118
- AACL 2022: https://aclanthology.org/2022.aacl-main.66/

HaRiM+ exists precisely because factual inconsistency is difficult to capture with ordinary summary-quality measures; it evaluates against human factuality annotations on FRANK, QAGS and SummEval.

**Targets:** H2.

**Classification:** `adjacent_prior_work` + `boundary_condition`.

**Strength:** **moderate** by itself, reinforcing Maynez et al.

**Required change:** `add_control`.

### 4.7 ALIGN-SIM 2024 — embedding cosine is not a semantic/factual oracle

**Work:** Yash Mahajan, Naman Bansal, Eduardo Blanco, Santu Karmaker, *ALIGN-SIM: A Task-Free Test Bed for Evaluating and Interpreting Sentence Embeddings through Semantic Similarity Alignment*.

- public proceedings: Findings of EMNLP 2024, November 2024;
- primary source: https://aclanthology.org/2024.findings-emnlp.436/

Thirteen sentence encoders were tested on semantic distinction, synonym replacement, antonym replacement, paraphrase without negation, and sentence jumbling. None aligned with all five criteria, despite strong standard benchmark performance.

**Targets:** H3.

**Classification:** `boundary_condition`.

**Strength:** **moderate**. It does not directly test STT PTF, but it directly attacks the assumption that teacher-embedding cosine alone can reliably distinguish all semantically important errors.

**Required change:** `add_control`. PTF embedding similarity may remain a screening feature, but F2 evaluation should include claim/entity/number/negation/entailment checks and human adjudication on a sample.

### 4.8 Sinha 2025 — direct evidence against embedding-only hallucination detection

**Work:** Debu Sinha, *The Semantic Illusion: Certified Limits of Embedding-Based Hallucination Detection in RAG Systems*.

- arXiv v1: **2025-12-17 04:22:28 UTC**;
- primary source: https://arxiv.org/abs/2512.15068

This preprint evaluates embedding-based detection on realistic hallucination benchmarks. It reports very high false-positive rates for embedding/cross-encoder methods on HaluEval, RAGTruth and WikiBio, while a reasoning-based LLM judge performs substantially better. The proposed explanation is directly relevant to STT PTF: factually wrong text can remain semantically plausible and therefore close in embedding space.

**Temporal relation:** after the broad 2025-11-11 STT architecture cutoff but **before the 2026-05-27 public F1/F2/PTF formulation**.

**Targets:** H3.

**Classification:** `contrary_evidence` for the current PTF formulation; temporally it is not prior art against the original 2025 architecture.

**Strength:** **strong** for treating embedding similarity as a detector by itself.

**Required change:** `revise_mechanism` + `add_control`. PTF must not be described as resolving F2 detection solely through teacher-embedding similarity.

## 5. Later contrary evidence — truth status only, not prior art

### 5.1 CoDA 2026 — hallucination can persist even when retrieved context is accurate and sufficient

**Work:** JinWei Shi et al., *CoDA: Restoring Contextual Dominance via Copy-Encouraged Attention Intervention for Mitigating RAG Hallucinations*.

- Findings of ACL 2026, July 2026;
- primary source: https://aclanthology.org/2026.findings-acl.576/

CoDA explicitly studies hallucinations that occur **despite accurate and sufficient retrieved context**. Its mechanistic account is that parametric knowledge can overwhelm evidence during generation as context-selective information routing weakens.

**Temporal relation:** posterior to the **2026-05-27 10:15:31 UTC** cutoff. It is therefore **not prior art** against the current STT claim.

**Truth-status classification:** `contrary_evidence` (later evidence).

**Strength:** **strong as a mechanism-level boundary**, moderate in direct transfer because STT uses a special normalizer prompt and proto-text rather than ordinary RAG.

**Required change:** `add_boundary_condition` + `add_control`. A correct proto-text in context does not itself guarantee that the final LLM normalization will privilege that evidence over parametric knowledge.

No positive evidence of CoDA depending on, citing, or deriving from STT was located. No `later_derivative` inference is warranted.

## 6. Synthesis: what changes

### 6.1 Priority

This run does **not** materially change the architectural priority conclusions of the 2026-09-18 STT audit. The new literature is mostly about truth status, evaluation, and guarantee strength rather than the exact STT architecture.

The temporal result that matters is instead epistemic: most of the strongest warnings about grounded-generation hallucination, source faithfulness, and correctness guarantees were public **before the 2026-05-27 F1/F2 formulation**.

### 6.2 Validity / plausibility

The current strongest defensible formulation is:

> Retrieval grounding and a restrictive normalizer prompt are plausible **risk-reduction mechanisms** for F1, but they do not establish an architectural hallucination guarantee. The proposed ≤1% F1 ceiling is an empirical target that must be measured at claim/fact level. F2 detection cannot be considered resolved by embedding cosine alone.

The literature does **not** establish that STT necessarily fails its ≤1% target. No direct replication of the exact STT decoder was located. Therefore `retract_claim` or `abandon_hypothesis` would overstate the evidence.

### 6.3 Required actions by claim

| Claim | Evidence strength | Required action |
|---|---|---|
| H1 instruction prevents/bounds F1 | strong boundary + strong contrary evidence against architectural prevention | `narrow_claim`, `downgrade_confidence`, `add_control` |
| H2 n-gram novelty operationalizes hallucination | strong contrary evidence to construct sufficiency | `revise_mechanism`, `add_control` |
| H3 embedding-cosine PTF resolves F2 | strong direct/near-direct contrary evidence | `revise_mechanism`, `add_control` |
| H4 grounding can reduce risk | not falsified by this literature | `no_change`, but quantify against matched baseline |

## 7. Discriminating experiment / protocol change required

Before publication or any claim of bounded hallucination, run a frozen decoder evaluation with the same normalizer model and prompt across at least:

1. **STT medoid proto-text → normalizer**;
2. **matched retrieved source text → same normalizer** (RAG-like grounding control);
3. **proto-text copied without LLM normalization**;
4. optionally, an unconstrained normalizer control.

For each output, score separately:

- lexical novelty / copy distance (retain the current n-gram statistic, but do not call it factuality);
- claim-level support/entailment against proto-text;
- claim-level correctness against source document `D`;
- entity consistency;
- number/date consistency;
- negation and relation consistency;
- a blinded human factuality sample.

For F2/PTF, compare at minimum:

- teacher-embedding cosine alone;
- an NLI/entailment or fact-level verifier;
- a reasoning-based judge with a prespecified rubric;
- human adjudication on an error-enriched sample.

**Discriminating rule:** if STT does not reduce unsupported-claim rate relative to the matched retrieved-source control, the special medoid+normalizer anti-hallucination advantage should be withdrawn for V1. If embedding-cosine PTF misses materially more F2 errors than a claim/fact-level verifier, it must be retained only as a cheap screening feature, not the detection criterion.

## 8. Revision record

This audit reopens one part of an earlier internal settlement. The 2026-05-27 debate correctly distinguished F1 from F2, but both sides treated the restrictive normalizer instruction as if it prevented F1 and treated embedding-similarity PTF as sufficient to close the F2 detection gap. External empirical literature available before that settlement makes both propositions too strong.

The historical debate artifacts are preserved unchanged. The revision is recorded here rather than silently rewriting their past conclusions.

## 9. Conclusion

The F1/F2 taxonomy remains useful. What changes is the confidence assigned to its proposed controls:

- **retrieval grounding is not a correctness guarantee;**
- **an instruction is not a proof of source faithfulness;**
- **n-gram novelty is not a sufficient factuality metric;**
- **embedding similarity is not a sufficient F2 detector.**

The STT hypothesis remains testable. Its anti-hallucination contribution now needs to be stated as an empirical, comparator-relative claim and evaluated with fact/claim-level metrics rather than treated as a property that follows from the architecture.