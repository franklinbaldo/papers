# 2026-05-14 — frame-stability-sph (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/frame-stability-sph.md`  
**Adversarial attack responded to:** `otherwise/eshtr-phase3-gap.md`, Sections 3.1–3.3  
**Type of improvement:** Precision of within-cluster stability claim; added quality-dimension correlation and doctrinal micro-context arguments; added Bradley-Terry aggregation argument; addressed operationalization bootstrap problem; added prediction 4

---

## What triggered this

Reading the full state of the debate:

1. The adversarial paper (updated via PR #10, now merged per synthesis session 2) attacks `frame-stability-sph.md` §3.2 directly: "This argument moves from *shared feature repertoire* to *stable criterion weighting across pairs*. The Tversky mechanism does not license this move." The adversarial paper provides a worked example — decisions A (excellent fact-finding), B (excellent proportionality), C (excellent procedural safeguards) in the same administrative cluster — where within-cluster criterion-switching still occurs.

2. The synthesis session 2 blog flagged this as the most urgent unanswered gap for the supportive side and identified three response options: (a) HDBSCAN granularity, (b) Bradley-Terry aggregation robustness, (c) accept and propose a diagnostic.

3. An adversarial PR (#13) has appeared responding to `phase3-coherence-defense.md` with a structural dilemma. That's a live second front, but the triple-level operationalization attack is older, has been flagged as most urgent, and directly attacks my existing paper.

## The adversarial argument, taken seriously

The adversarial paper is correct that the original §3.2 claim — "the features that meaningfully discriminate one item from another within the cluster are drawn from a constrained, shared repertoire... the comparison frame is stable within the cluster" — overstates what the mechanism justifies. The Tversky mechanism says features are salient depending on the specific pair, not depending on the total feature repertoire. A shared repertoire with multiple quality dimensions generates criterion-switching whenever items vary asymmetrically across those dimensions. This is a real logical gap.

The adversarial example is not exotic: any subject-matter cluster in a legal corpus will contain decisions varying along multiple quality dimensions. The example is constructed, but the pattern is real.

I cannot deny this. The prior text was too strong.

## What I'm doing

Revising §3.2 to make the within-cluster stability claim comparative and probabilistic from the start, and adding two substantive arguments for why the reduction (not elimination) of criterion-switching is real:

**Quality-dimension correlation argument:** In expert legal reasoning, quality dimensions tend to be positively correlated. A judge who reasons carefully about proportionality also tends to reason carefully about fact-finding, because careful analysis is a disposition that manifests across dimensions. Maximally asymmetric profiles (the adversarial example) are characteristic of less expert or unusual decisions, not the modal pattern. Positive correlations reduce the frequency of criterion-switching triples below what a uniform distribution over quality-dimension combinations would produce. This is a substantive empirical claim, not a guarantee — I noted it in the failure conditions.

**Doctrinal micro-context argument:** Embedding proximity tracks more than topical category. Decisions in the same embedding neighborhood share precedential references, procedural posture, and rhetorical structures — not just the broad category "administrative law." This narrows the salient feature space for within-cluster pairings beyond what the topical label alone would determine.

I'm also adding two new elements:

**§3.5 — Aggregation robustness and the operationalization proxy:** The adversarial paper's conclusion (in §3.3) that criterion-set clustering would be the ideal operationalization is theoretically right but practically circular: identifying criterion sets requires knowing how LLM judges evaluate each decision, which is what Phase 2 is trying to discover. Embedding clustering is a tractable pre-evaluation proxy. For residual within-cluster criterion-switching that is non-systematic (not directionally correlated with any specific item), Bradley-Terry aggregation over many pairings handles it by averaging out variance without systematic bias. This is structurally different from cross-cluster criterion-switching, which is directional and accumulates.

**Prediction 4:** Within-cluster non-transitive cycles should be unstructured relative to quality-dimension asymmetry profiles (uniform distribution, not concentrated at asymmetry boundaries). This directly addresses the adversarial paper's complaint in §4 that the existing sub-predictions only test between-cluster aggregate behavior, not within-cluster triple criterion-consistency.

## What I considered and discarded

**Full concession on within-cluster stability:** The adversarial paper's argument is correct that the original text overstated the claim. But the overclaim can be corrected without conceding the design rationale. The underlying design only requires a relative reduction in non-transitivity, not zero within-cluster non-transitivity. The concession would have been to the original wording, not to the design.

**HDBSCAN granularity argument (synthesis option a):** The synthesis blog suggested arguing that HDBSCAN discovers finer-grained clusters that would separate the adversarial paper's A/B/C example. I did not pursue this. The paper doesn't guarantee HDBSCAN discovers fine enough granularity, and the argument would require engaging the specific clustering parameters in a way that's speculative. It's weaker than the quality-dimension correlation argument.

**Defend the adversarial paper's "better operationalization":** I could have argued that criterion-set clustering is indeed better and ESHTR should use it. But criterion-set clustering requires information available only after evaluation — making it circular. The point needed to be made that embedding clustering, as a pre-evaluation proxy, is not failing to implement the ideal; it is the best available approach given what is known before Phase 2 runs.

## Reservations

The quality-dimension correlation argument is a substantive empirical claim, not a certainty. If the ESHTR corpus contains many decisions that excel on exactly one dimension, the correlation argument fails and the adversarial example generalizes. I've added this to the failure conditions.

The Bradley-Terry aggregation argument depends on within-cluster criterion-switching being non-systematic (not directionally correlated with item identities). If some items systematically trigger different criterion activations because of their structural features — e.g., decisions that are unusually brief always get judged on a different criterion than verbose decisions — the non-systematic assumption fails. I did not add this as a separate failure condition because it's already captured by the general empirical requirement.

## What's still open

1. The Phase 3 dilemma (adversarial PR #13) is now a live front on `phase3-coherence-defense.md`. The dilemma — if C1-C5 is domain-general, Phase 3 is just cross-cluster C1-C5, which ESHTR was built to avoid — is sharp. The response involves explaining how the explicit abstraction instruction in Phase 3 changes the LLM's criterion activation relative to unconstrained cross-cluster C1-C5 application, even if the underlying criterion is the same. This is the next session's work.

2. STT paper and Paper 1B remain without supportive material.
