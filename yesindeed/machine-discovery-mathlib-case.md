---
type: "Supportive Defense"
title: "Formal Library Growth as Certified Epistemic Expansion: The Lean Mathlib Case"
description: "Independent evidence that the five-condition framework for accepted machine discovery events is operationally instantiated in the Lean Mathlib ecosystem, and that Mathlib's growth has produced measurable improvement in later proof-generating systems."
tags: [supportive, machine-discovery, formal-mathematics, lean, mathlib]
timestamp: 2026-08-14T00:00:00+00:00
---

# Formal Library Growth as Certified Epistemic Expansion: The Lean Mathlib Case

---

## 1. Thesis Supported

Target paper: `machine_discovery.md` — "When the Learner Changes the Curriculum: Machine Discovery as Recursive Expansion of Verifiable Knowledge" (Baldo, 2026).

Central claim:

> **A machine discovers when an artifact to which it made an essential contribution survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state. The discovery becomes recursive when that enlargement measurably changes what later learners can infer, solve, or discover.**

The paper defines an accepted discovery event ($K_t \xrightarrow{a} K_{t+1}$) by five conditions: admissibility, certification, snapshot novelty, provenance sufficiency, and public uptake (Definition 1). It additionally defines recursive productivity for learner family $\mathcal{F}$ in terms of a measurable performance improvement after incorporating $a$ into the curriculum (Definition 3). The paper proposes formal mathematics — specifically a frozen proof-assistant library — as the "cleanest initial test bed" for these definitions (§2, §15.1).

---

## 2. What This Support Adds

**Vector:** Independent evidence. The paper proposes experiments for testing its framework (§15) but does not demonstrate that any existing ecosystem already operationalizes the five-condition framework and exhibits recursive productivity. This paper shows that the Lean Mathlib library governance model independently instantiates Definition 1 in practice, and that the retrieval-augmented theorem-proving literature provides empirical evidence for recursive productivity (Definition 3). The support is additive: it shows the framework captures an already-operating system, not merely a proposed experimental design.

---

## 3. The Argument

### 3.1 The Lean Mathlib Governance Model Implements Definition 1

Lean 4 is a proof assistant grounded in dependent type theory (the Calculus of Constructions extended with inductive types and universe polymorphism). Mathlib4 is its primary community library, containing formalized proofs of results spanning algebra, analysis, combinatorics, and topology. As of mid-2026, Mathlib4 contains hundreds of thousands of individually verified lemma and theorem entries, each accepted through a defined governance process.

Each Mathlib contribution proceeds through the following steps:

1. **A contributor opens a pull request (PR)** containing the formal statement (expressed in Lean's type language) and a proof term or tactic proof.
2. **The Lean elaborator and type checker verify** that the proof term inhabits the claimed type — establishing that the formal certificate is valid relative to Lean's foundational kernel.
3. **The PR undergoes reviewer and `bors` (merge bot) checks**, which include: (a) CI verification that the proof compiles from the kernel up; (b) reviewer inspection for whether the result duplicates existing Mathlib content; (c) style and naming-convention review.
4. **Upon merge**, the result enters the versioned `Mathlib/Mathlib4` main branch, is assigned a stable API name, and is accessible to all future users as a lemma or theorem.

This maps directly onto Definition 1's five conditions:

| Definition 1 Condition | Mathlib Implementation |
|---|---|
| Admissibility | Statement must be well-typed in Lean's dependent type theory; elaborator rejects malformed terms |
| Certification | Lean's kernel verifies the complete proof term; CI enforces kernel acceptance on every PR |
| Snapshot novelty | Reviewers check against existing Mathlib content; tools like `exact?` search for duplicate proofs; explicit policy against re-adding existing results |
| Provenance sufficiency | Git commit history preserves contributor identity, dependency list, and proof structure; PR records human-reviewer approval |
| Public uptake | Merge into main branch with stable versioned API; downstream users reference the specific lemma name |

The operational consequence is that Mathlib is not a candidate ledger but a certified epistemic state in the paper's sense: every accepted entry satisfies all five conditions relative to the prior library state as the frozen snapshot.

### 3.2 Certification Independence: The Small Trusted Kernel

The paper notes (§6.2) that "verification strength is therefore graded" and identifies small-kernel verification as a high-independence level (level 4 in the proposed hierarchy). Lean's kernel is architecturally separated from the elaboration and tactic machinery that generates proof terms. The kernel is a comparatively small, purpose-restricted component (~tens of thousands of lines) that performs only type checking — it does not run tactics, call external tools, or access the network.

The practical consequence is that even if the elaborator or a tactic implementation contains bugs that produce an incorrect proof term, the kernel will reject it: the kernel does not trust the elaboration pipeline, only the final term. This is not perfect independence — the kernel itself could contain soundness bugs, and imported axioms could be inappropriate — but it provides a structurally meaningful separation between the generation process and the certification process. Lean's kernel bugs are tracked separately, are rare, and are treated as critical issues rather than tolerated imperfections.

This design means Lean's certification structure is not self-assertion (level 1) or same-stack checking (level 2) in the paper's hierarchy. It approximates level 4 (small-kernel verification), with residual uncertainty about kernel soundness and axiom appropriateness that the audit graph should record.

The common-mode dependencies that the paper (§6.2) asks to be recorded include: the Lean kernel itself (single point of trust), imported axioms (`Classical`, `propext`, `Quot.sound`), the `Mathlib` import dependency graph, and any external tools used during proof search. Mathlib PRs document import dependencies explicitly.

### 3.3 Recursive Productivity: Evidence from Retrieval-Augmented Theorem Proving

The recursive productivity claim (Definition 3) requires that incorporating an accepted artifact into the curriculum yields a measurable improvement in later learning or discovery performance, after charging retrieval and interpretation costs.

The theorem-proving literature provides direct evidence for this claim at the library level. Yang et al. (2023) introduced LeanDojo, a benchmark environment that permits controlled access to Lean's proof state and Mathlib's theorem database for neural theorem provers. A key experimental finding: provers with retrieval access to a larger set of Mathlib premises substantially outperform provers without retrieval or with access to a smaller premise set, on tasks where the proof requires using library lemmas as building blocks. The performance differential is not a training artifact — the retrieval access condition is varied at inference time, holding the prover model fixed. This directly operationalizes the paper's Reach measure:

$$
G_B(a; \mathcal{T}) = \operatorname{Reach}_B(K_{t+1}, \mathcal{T}) - \operatorname{Reach}_B(K_t, \mathcal{T})
$$

for the specific case where $a$ is a set of Mathlib lemmas and $\mathcal{T}$ is a distribution of theorem-proving tasks. The improvement in Reach when more lemmas are available is positive and substantial enough to be the primary predictor of prover success on lemma-dependent tasks.

This evidence establishes recursive productivity at the library-level aggregate. It does not establish that each individual accepted lemma produces positive $G_B$ — Proposition 4 of the paper predicts that extensional expansion need not imply practical expansion for every artifact, and H3 predicts heavy-tailed distribution of practical gain. The LeanDojo evidence is consistent with both: aggregate library growth produces aggregate Reach improvement, while individual lemmas vary in fertility.

### 3.4 The Curriculum Expansion Loop in Practice

The paper describes the recursive discovery cycle (§12.1):

$$
K_t \xrightarrow{\text{learning and search}} a_t \xrightarrow{\text{audit}} K_{t+1} \xrightarrow{\text{teaching and reuse}} L_{t+1}
$$

The Lean/Mathlib ecosystem closes this loop in an observable way:

- **Learning and search phase**: Proof-searching systems (whether human mathematicians, automated tactics, or neural provers) operate against the current Mathlib state as their available lemma corpus.
- **Audit phase**: The PR and kernel verification process implements the audit boundary — candidates do not enter $K_{t+1}$ without passing all five conditions.
- **Teaching and reuse phase**: Accepted Mathlib results are used as lemmas by subsequent provers; they appear in retrieval datasets for neural systems; and they serve as training data for models that attempt to generate new Mathlib-compatible proofs.

The critical structural property that distinguishes this from the "circular self-training" the paper rejects (§12.3) is the audit boundary. Mathlib's CI enforces that only kernel-verified, novelty-checked, publicly uploaded results enter the canonical epistemic state. A neural prover's unverified output does not enter Mathlib. If a neural prover generates an incorrect proof term, the kernel rejects it. If a neural prover rediscovers a known result, reviewers catch it. Only artifacts that cross the audit boundary — satisfying all five conditions — modify the epistemic state that later learners receive.

This architectural choice makes Mathlib an empirically operating instance of the paper's recursive curriculum, with the audit boundary functioning as the control mechanism §18.5 identifies as necessary for systems that "write the curricula from which later systems learn."

### 3.5 The Provenance Gap: Where Mathlib Falls Short

The support is honest about a gap. The paper (§18.3) recommends that proof libraries distinguish: imported human results; machine formalizations of known results; machine-generated proofs; machine-proposed novel statements; and externally accepted novel discoveries.

Mathlib does not currently track this distinction in its metadata. The contribution type (human-authored proof, human-directed tactic search, machine-suggested lemma, machine-generated proof) is not recorded in a queryable per-theorem field. The autonomy vector $\alpha(a)$ from Definition 2 is not populated for any Mathlib entry.

This is not a failure of the framework; it is a failure of current library practice relative to the framework's recommendations. The gap demonstrates that the paper's framework adds something that existing best practices do not yet capture: the machinery of certified epistemic states is in place in Mathlib, but the provenance decomposition required to make recursive machine discovery claims — as opposed to recursive human-assisted discovery claims — is absent. Implementing §18.3's metadata recommendations would make Mathlib a fully traceable instance of the paper's framework rather than a partially traceable one.

---

## 4. Anticipated Objection

**Objection**: The Mathlib case primarily demonstrates the framework for human-authored results machine-verified by Lean's kernel. The paper's central concern is *machine discovery* — artifacts to which machines made essential contributions. Mathlib shows that the epistemic infrastructure for tracking certified discoveries is operational, but it does not demonstrate that machines are making discoveries in the relevant sense. The autonomy vectors for most Mathlib entries would have near-zero machine-generation components. The Mathlib case is therefore evidence for the infrastructure's coherence, not for the central machine-discovery claim.

**Response**: The objection correctly identifies a scope limitation (see §5 below) but overstates it in two respects.

First, the paper's five-condition framework (Definition 1) applies uniformly regardless of the generator's nature. The admission, certification, novelty, provenance, and uptake conditions make no reference to whether the generator is human or machine. Definition 2 provides the further classification (machine-assisted vs. machine-originated) that captures this difference. The objection concerns Definition 2, not Definition 1. The Mathlib case supports Definition 1's coherence and operationalizability — which is the necessary substrate for any machine-discovery claim. A framework whose five conditions cannot be operationally satisfied does not become more credible by being applied to machine outputs; Mathlib shows the conditions are satisfiable, which is a precondition for the stronger claim.

Second, machine components already appear in Mathlib's discovery pipeline. Neural provers (including systems trained on Mathlib itself) have contributed suggestions accepted into Mathlib. The `aesop` and `decide` tactics automate proof search for specific problem classes. The `polyrith` tactic calls an external algebraic system and produces verified proof terms. These cases are not systematically labeled — the provenance gap identified in §3.5 — but they represent existing machine contributions to the certified epistemic state. The Mathlib case is not purely human-only.

---

## 5. Scope of the Support

This support establishes:

- The five-condition framework (Definition 1) is operationally instantiated in the Lean Mathlib ecosystem. This is a demonstration of operational coherence in at least one domain.
- Lean's small-kernel architecture implements graded certification independence at level 4 in the paper's hierarchy.
- Aggregate library growth produces measurable Reach improvement (positive $G_B$ at the library level), consistent with Definition 3's recursive productivity claim.
- The audit boundary — the structural separation between the candidate state and the accepted epistemic state — is implemented in Mathlib's governance, confirming the paper's distinction between recursive discovery and circular self-training.
- The paper's §18.3 metadata recommendations for distinguishing discovery types represent a genuine gap in current Mathlib practice, which the framework would fill.

This support does not establish:

- Recursive productivity for individual accepted lemmas (the distribution of $G_B(a; \mathcal{T})$ for single artifacts). Proposition 4 predicts this distribution is heavy-tailed; the LeanDojo evidence is consistent with this prediction but does not resolve it at the individual lemma level.
- Recursive productivity outside formal mathematics. The paper explicitly scopes this as a harder domain (§15.6, §15.7).
- That current neural systems make machine-originated discoveries (Definition 2, high autonomy vector) in Mathlib at significant scale. The provenance gap makes this unquantifiable from current metadata.

---

## 6. Conditions Under Which This Support Would Fail

- **Lean kernel soundness failure**: If Lean's trusted kernel were found to contain soundness bugs at a rate high enough to permit invalid proof terms to be accepted, the "certification" condition would be satisfied in form but not in substance. Kernel bugs are tracked and are rare; their existence weakens but does not eliminate the certification claim.

- **Novelty-audit unreliability**: If the Mathlib PR review process systematically accepted results equivalent (under any reasonable $\equiv_t$) to existing Mathlib content, the snapshot-novelty condition would not be operationally implemented. Studies of Mathlib's duplicate rate are not available; this is an empirical question the framework itself recommends studying (§15.2 matched-rediscovery controls).

- **LeanDojo evidence confounded**: If the retrieval-augmented performance improvement documented by Yang et al. (2023) were explained by training-data overlap rather than inference-time curriculum access — i.e., if the neural prover's training data already contained the "retrieved" lemmas, making retrieval redundant rather than additive — the recursive productivity evidence would not support Definition 3. The LeanDojo experimental design controls for this partially but not exhaustively.

- **All Mathlib machine contributions are purely verification-stage**: If machine components in current Mathlib contributions are limited to verification (running tactics, kernel checking) with zero machine-origination (generation of the novel claim or novel proof strategy), then Definition 1's provenance sufficiency condition is satisfied but the machine-originated condition in Definition 2 is never met. The support's scope would then be confined to the infrastructure claim, with no evidence for machine-originated recursive discovery even in the cleanest case.
