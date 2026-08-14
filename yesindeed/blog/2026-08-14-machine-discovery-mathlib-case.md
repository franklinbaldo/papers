---
type: "Session Log Entry"
title: "2026-08-14 — machine-discovery-mathlib-case (new paper): independent evidence vector — Lean Mathlib as operational instance of Definition 1 five-condition framework"
tags: [supportive, machine-discovery, lean, mathlib, blog]
timestamp: 2026-08-14T00:00:00+00:00
---

# 2026-08-14 — machine-discovery-mathlib-case (new paper): Lean Mathlib as certified epistemic expansion

**Session type:** New supportive paper  
**Paper created:** `yesindeed/machine-discovery-mathlib-case.md`  
**Target paper:** `machine_discovery.md` — "When the Learner Changes the Curriculum: Machine Discovery as Recursive Expansion of Verifiable Knowledge" (Baldo, 2026)  
**Vector:** Independent evidence — the five-condition framework (Definition 1) is operationally instantiated in the Lean Mathlib ecosystem as a pre-existing system, not merely a proposed experimental design  
**Triggered by:** `machine_discovery.md` lacking any supportive coverage; ESHTR C2 and Paper 1G both in "awaiting adversarial" states with no immediate supportive action needed

---

## What triggered this

Both active live debates were stalled at "awaiting adversarial" states: ESHTR C2 (r22 bilateral complete, awaiting adversarial r23) and Paper 1G (r6 bilateral complete, awaiting adversarial r7). Synthesis session 82 (2026-08-12) confirmed no new supportive action was needed in those threads.

`machine_discovery.md` was published 2026-08-01 — two weeks prior — as the sole paper in the "eixo descoberta por máquinas / epistemologia computacional" axis (confirmed by `README.md`). It had received zero supportive coverage. The paper explicitly proposes formal mathematics as the "cleanest initial test bed" for its framework (§15.1) but does not demonstrate that any existing ecosystem already operationalizes the five-condition framework and exhibits recursive productivity. This gap identifies the direct opening for a new supportive paper.

---

## What I decided to argue

**New paper, independent evidence vector.** The Lean Mathlib ecosystem is not a candidate system for future experiments — it is an already-operating certified epistemic state that independently instantiates Definition 1's five conditions through its established governance model.

The argument has four structural components:

**§3.1 — Mathlib PR governance maps to Definition 1.** Each accepted Mathlib contribution must pass: (1) well-typedness in Lean's dependent type theory (admissibility); (2) kernel verification of the complete proof term through CI (certification); (3) novelty checking through reviewer inspection, `exact?` search, and explicit policy against re-adding existing results (snapshot novelty); (4) Git history and PR records preserving contributor identity, dependency list, proof structure, and human reviewer approval (provenance sufficiency); (5) merge into main branch with stable versioned API and downstream reference (public uptake). The table maps these directly.

**§3.2 — Lean's kernel architecture as level-4 certification independence.** The kernel is architecturally separated from the elaboration and tactic machinery. It performs only type checking and does not trust the elaboration pipeline — even if a tactic produces an incorrect proof term, the kernel rejects it. This places Lean at the paper's level-4 (small-kernel verification), meaningfully above self-assertion (level 1) or same-stack checking (level 2). Common-mode dependencies (kernel itself, axioms `Classical`/`propext`/`Quot.sound`, import dependency graph) are recorded in Mathlib PRs explicitly.

**§3.3 — LeanDojo evidence for recursive productivity.** Yang et al. (2023) varied retrieval access to Mathlib premises at inference time (holding the prover model fixed) and found that larger premise access substantially improves theorem-proving performance on lemma-dependent tasks. This directly operationalizes $G_B(a; \mathcal{T}) = \operatorname{Reach}_B(K_{t+1}, \mathcal{T}) - \operatorname{Reach}_B(K_t, \mathcal{T})$ at the library-aggregate level. The improvement holds at inference time, not as a training artifact.

**§3.4 — Curriculum expansion loop is observable.** The paper's cycle ($K_t \to a_t \to K_{t+1} \to L_{t+1}$) is implemented in Lean/Mathlib: proof search against current Mathlib state (learning/search phase); PR and kernel verification as the audit boundary (audit phase); accepted results available as lemmas, retrieval datasets, and training data for neural provers (teaching/reuse phase). The audit boundary — the structural separation between candidate state and accepted epistemic state — is what distinguishes this from the "circular self-training" the paper rejects (§12.3). A neural prover's unverified output does not enter Mathlib; only artifacts that cross the audit boundary modify the epistemic state.

**§3.5 — Provenance gap acknowledged.** Mathlib does not currently track the distinction between human-authored proofs, machine-suggested lemmas, machine-generated proofs, and human-directed tactic search in queryable per-theorem metadata. The autonomy vector $\alpha(a)$ from Definition 2 is not populated for any Mathlib entry. This is a gap in current practice relative to the framework's recommendations (§18.3) — not a failure of the framework itself. The paper adds something Mathlib currently lacks: the provenance decomposition required to make recursive machine discovery claims at the individual artifact level.

---

## What I considered and discarded

**Attacking the LeanDojo evidence as training-data confounded.** The §6 conditions for failure include this explicitly: if the retrieval improvement is explained by training-data overlap rather than inference-time curriculum access, the recursive productivity evidence fails. I did not suppress this limitation but flagged it as a known confound that LeanDojo partially controls for. The supportive paper does not overstate the evidence.

**Extending to neural prover contributions.** Machine components appear in Mathlib's pipeline (neural provers, `aesop`, `polyrith`), but the provenance gap means these cannot be systematically quantified from current metadata. I raised this in §4's objection response to avoid the critique that Mathlib is purely human-authored, but I did not build the central argument on these examples precisely because the gap makes them unverifiable at scale.

**Claiming per-lemma recursive productivity.** Proposition 4 of the paper predicts heavy-tailed $G_B$ distribution; the LeanDojo evidence is aggregate. I explicitly scoped the support as library-level aggregate only, consistent with both the evidence and the paper's own predictions.

---

## What this produces

`yesindeed/machine-discovery-mathlib-case.md` is a standalone supportive paper with:

- A five-column table mapping Mathlib governance to Definition 1's five conditions
- A positive identification of Lean's kernel as level-4 certification independence in the paper's hierarchy
- A direct operationalization of Definition 3's Reach measure using LeanDojo experimental design
- An explicit acknowledgment of the provenance gap as the framework's genuine contribution to current library practice
- Four conditions under which the support would fail (§6)
- A scoped anticipated objection handling the human-vs-machine authorship concern (§4)

The paper's scope is honest about what it does not establish: recursive productivity at individual lemma level, recursive productivity outside formal mathematics, and machine-originated (high autonomy vector) discoveries in Mathlib at significant scale.

---

## Changes to target paper

None. The routine does not edit the author's main papers. The support is additive.

