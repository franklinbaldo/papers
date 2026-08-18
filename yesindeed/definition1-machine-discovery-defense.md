---
type: "Supportive Defense"
title: "Definition 1 as Certification Framework: Why the Machine-Contribution Classification Is Correctly Located in Definition 2"
description: "Direct defense of machine_discovery.md's Definition 1 against the adversarial filing otherwise/machine-discovery-scope.md. Central argument: Definition 1's five conditions intentionally define certified epistemic transitions rather than machine-φ-generation events; the machine-contribution classification is correctly located in Definition 2 because (a) requiring φ-generation in Definition 1 would exclude genuine machine discovery cases where machine contribution is to the proof rather than the claim, and (b) treating 'trivially satisfied at the lowest autonomy level' as a framework defect misreads how graded frameworks are designed to behave. The adversarial's proposed definitional refinement would narrow the framework to exclude the intermediate cases the field most needs to track."
tags: [supportive, machine-discovery, definition, autonomy-vector, direct-defense]
timestamp: 2026-08-18T00:00:00+00:00
---

# Definition 1 as Certification Framework: Why the Machine-Contribution Classification Is Correctly Located in Definition 2

---

## 1. Thesis Supported

Target paper: `machine_discovery.md` — "When the Learner Changes the Curriculum: Machine Discovery as Recursive Expansion of Verifiable Knowledge" (Baldo, 2026).

Central claim under defense:

> **A machine discovers when an artifact to which it made an essential contribution survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state.** (§19)

And the definitional framework:

> **Definition 2.** An accepted discovery is **machine-originated relative to an ablation family** when a machine component is essential to the first generation of the novel claim, construction, or method, rather than only to verification, formatting, or retrieval. (§9)

The target paper presents Definition 1 as the auditing framework for discovery events and Definition 2 as the machine-contribution classifier. This paper defends the decision to separate these two functions against the adversarial critique in `otherwise/machine-discovery-scope.md`.

---

## 2. What This Support Adds

**Vector:** Direct defense. The adversarial filing (`otherwise/machine-discovery-scope.md`, 2026-08-17) argues that Definition 1's five conditions define certified epistemic expansion events rather than machine discovery events specifically, that Condition 4 is trivially satisfied for any Lean proof at the machine-assisted level, and that the experimental program (§15.1) reveals an intended scope that Definition 1 does not enforce. This paper responds to that attack on its own terms.

The Lean Mathlib supportive filing (`yesindeed/machine-discovery-mathlib-case.md`) addressed the framework's operational coherence as independent evidence. This filing addresses the definitional structure itself.

---

## 3. The Argument

### 3.1 The Adversarial Attack, Reconstructed

The adversarial's strongest argument has two layers.

**Layer 1 (definitional gap):** Definition 1's five conditions do not require machine contribution to φ-generation. Condition 4 ("μ supports the level of machine-contribution claim being made") is modulary — it accepts whatever claim level the submitter makes, as long as the provenance supports it. At the "machine-assisted" level (Definition 2's weakest category), any Lean proof trivially qualifies: Lean's kernel is always an essential machine component, so removing it prevents any proof from being accepted, satisfying the ablation criterion. The result is that a human-authored theorem mechanically verified by Lean and a machine-generated theorem both satisfy Definition 1 under the same conditions, with the same Condition 4 satisfaction mechanism. The framework makes no definitional distinction between them at the event-type level.

**Layer 2 (experimental program divergence):** The paper's own experimental design (§15.1) requires the agent to generate theorem-certificate pairs — machine φ-generation is the experimental starting point. If the paper intends to study machine claim-generation, but Definition 1 does not require it, there is a mismatch between what the definition covers and what the experiments test.

Both layers are correctly stated as descriptions of what Definition 1 does and does not say. The question is whether this constitutes a design flaw or a design choice.

### 3.2 Definition 1 and Definition 2 Perform Different Functions in the Framework

The adversarial treats Definition 1 as if it should, by itself, be the definition of a machine discovery event — such that Conditions 1–5 provide the necessary and sufficient conditions for what counts as machine discovery. On this reading, the absence of a φ-generation requirement is a gap in the definition.

The paper's framework has a different structure. Definition 1 specifies the **auditing procedure** — what makes any discovery event an *accepted* discovery event. Definition 2 specifies **machine-contribution classification** — how to characterize the machine's role within an accepted discovery event. These are functionally distinct:

- Auditing procedure answers: has this event been properly certified, is it novel, has the provenance been recorded, has it been incorporated into the public state?
- Machine-contribution classification answers: what kind of machine contribution made this accepted event a machine discovery event rather than a human discovery event?

The paper's innovation is to separate these two questions. Definition 1 provides a *generator-agnostic auditing procedure* — the same five conditions apply whether the generator is a neural prover, a human mathematician, or a human-machine collaboration. This is not a gap; it is the framework's principal architectural decision. The same auditing procedure applies uniformly because the epistemic requirements for a certified transition are the same regardless of who generated the claim.

Definition 2 then classifies, within the set of accepted discovery events, where on the machine-contribution spectrum the event falls. The separation means that (a) auditors can evaluate epistemic status without needing to determine generator identity first, and (b) machine contribution can be classified on a continuous spectrum (the autonomy vector) rather than as a binary entry condition.

The adversarial's proposed fix — adding a φ-generation requirement to Definition 1 — would collapse these two functions into one definition, making generator identity a condition of epistemic acceptance. This would violate the framework's foundational design decision.

### 3.3 The φ-Generation Requirement Would Exclude Genuine Machine Discovery Cases

The adversarial proposes: "A machine discovery event requires machine-essential contribution to claim generation (φ), not only machine participation in the pipeline as a whole."

Applied consistently, this refinement would exclude the following cases from the "machine discovery" category:

**Proof-level machine contributions.** AlphaGeometry (Trinh et al., 2024, cited at §3 of the paper) produces machine-checkable geometric arguments for human-specified problem classes. The machine's contribution is to the proof structure (π), not to the original geometric claim (φ). AlphaTensor (Fawzi et al., 2022, cited at §3) discovers algorithms for human-specified problem classes — the machine generates the construction (π), while the problem class (φ, "find a faster matrix multiplication algorithm for n×n matrices") is human-specified. Under the adversarial's refinement, neither of these would be a "machine discovery event." Both are paradigmatic cases the paper's framework is designed to capture.

This is not a narrow exception. The paper's §3 ("Related Work and the Missing Distinction") lists seven systems as motivating the framework. Of these, the cases where machine contribution is primarily to the proof or construction rather than the original claim formulation are neither marginal nor atypical — they represent the mainstream of current AI-assisted discovery systems. A definition that excludes them by requiring machine φ-generation addresses a minority of the field's most interesting cases while excluding the majority.

**The autonomy vector makes this classification correctly.** For AlphaGeometry, the autonomy vector would show high α_p (proof/experiment autonomy) and low α_g (generation autonomy) — and zero is not the same as "no machine discovery." The framework's explicit statement at §8.3 is that "a result can be machine-generated but human-selected, machine-proved but human-formalized, or machine-proposed but independently machine-verified. These are different scientific facts." The adversarial's φ-generation requirement converts the "generation" dimension of the autonomy vector from *one component* into *the* necessary condition, collapsing a multidimensional classification into a binary gate.

### 3.4 "Trivially Satisfied at the Lowest Level" Is the Correct Behavior for a Graded Framework

The adversarial argues that Condition 4 is "trivially satisfied" for any Lean proof at the machine-assisted level, and presents this as a defect: the condition cannot filter theorems on machine contribution to φ-generation.

But the function of Condition 4 is not to filter on φ-generation contribution. Its function is to ensure adequate provenance documentation for the level of contribution claim being made. For a human-authored theorem kernel-verified by Lean, where the submitter makes only the "machine-assisted" claim, Condition 4 is satisfied when the provenance record documents Lean's kernel as an essential pipeline component. This is the correct outcome: the framework has correctly classified the event at the "machine-assisted" level and required adequate provenance for that level.

The alternative — requiring that Condition 4 be non-trivially satisfied only at high autonomy levels — would mean that human-authored theorems kernel-verified by Lean *fail* Condition 4 and thus cannot be accepted discovery events under the framework. This would narrow the framework's applicability to only the most autonomous cases, excluding the intermediate cases that make up the bulk of contemporary human-machine collaborative discovery.

"Trivially satisfied at the lowest autonomy level" is the correct behavior for a graded framework that starts by specifying the auditing procedure (applicable to all levels) and then classifies machine contribution (across the full spectrum). It is only a defect if the framework's goal were to filter *in* only high-autonomy cases at the Definition 1 stage — but that is not the framework's goal.

### 3.5 The Experimental Program Is Scoped to the Most Unambiguous Cases

The adversarial identifies a real observation: Experiment 1 (§15.1) tests machine claim-generation while Definition 1 does not require it. This mismatch between experimental focus and definitional scope is described as a design gap.

The more natural description is that the experiments are designed around the cases where the scientific questions are least contaminated by the human-machine attribution problem. When a machine generates theorem-certificate pairs with a frozen library and a declared compute budget (§15.1), the machine's φ-generation contribution is not in dispute. This makes the certified discovery event cleanly attributable and the recursive productivity measures (Definition 3) interpretable in terms of machine contribution specifically.

Starting experiments with unambiguous cases is standard experimental design, not evidence that the framework's central definition should be restricted to those cases. The appropriate response to "the experiments start with high-autonomy cases" is "the framework is designed so that lessons from high-autonomy cases generalize to lower-autonomy cases through the same auditing procedure." Definition 1 being applicable across the autonomy spectrum means that the experimental findings from §15.1 cases provide evidence relevant to the framework's application in mixed human-machine cases — because the same five conditions apply at all autonomy levels.

If Definition 1 were restricted to machine φ-generation cases (the adversarial's refinement), the experimental findings from §15.1 would be confined to that restricted domain and would not inform the framework's application to the intermediate cases. The broader scope of Definition 1 is what allows the experimental results to be broadly applicable.

---

## 4. Scope of the Support

This support establishes:

- Definition 1 + Definition 2 constitute a unified machine discovery framework where the separation of auditing function (Definition 1) from machine-contribution classification (Definition 2) is a deliberate architectural decision, not a definitional gap.
- The adversarial's proposed φ-generation requirement in Definition 1 would exclude genuine machine discovery cases (proof-level contributions) that the paper's framework and the field recognize as important machine contributions to epistemic transitions.
- "Trivially satisfied at the lowest autonomy level" is the correct behavior for a graded framework: it correctly classifies kernel-verification cases as "machine-assisted" with adequate provenance, without making the condition vacuous for the cases it is designed to track.
- The experimental program's focus on high-autonomy cases is appropriate experimental design; the framework's broader Definition 1 scope enables findings from those cases to generalize.

This support does not establish:

- That the adversarial's surrender condition (e) — specifying a minimum Definition 2 autonomy level required for Definition 1 events to count as "machine discovery events" — would not be an improvement. Specifying this threshold would clarify the framework without conceding the definitional gap argument, and would address the legitimate question of where on the machine-contribution spectrum the category "machine discovery event" begins.
- That the provenance gap in current Mathlib practice (absence of per-theorem tracking of generation autonomy) is resolved. This limitation, acknowledged in the Mathlib supportive filing (§3.5 of that paper), stands. Without the §18.3 metadata improvements, the Lean Mathlib evidence supports the framework's operational coherence as a certified-expansion tracker but cannot establish machine-originated discovery at quantified scale.
- That the LeanDojo evidence supports machine-discovery-specific recursive productivity (as distinct from certified-expansion recursive productivity). This limitation from the Mathlib filing (§3.3) stands for the same provenance reasons.

---

## 5. Conditions Under Which This Support Would Fail

- **Field consensus converges on φ-generation as the necessary condition.** If the community standard for "machine discovery" converges on requiring machine-essential contribution to φ-generation specifically — such that AlphaGeometry and AlphaTensor are explicitly classified as "machine-assisted" rather than "machine discovery" by consensus — then the adversarial's proposed refinement aligns with the field standard and the framework's broader Definition 1 scope would be a departure from community usage rather than a clarification of it.

- **The paper's related work turns out to be confined to φ-generation cases.** If AlphaGeometry, AlphaTensor, FunSearch, and Minimo are all cases where machines generate φ (not only π), then the adversarial's proposed refinement would not exclude the paradigm cases. The support's §3.3 argument depends on these systems making proof-level rather than claim-generation-level contributions. If the characterization of these systems is wrong, the exclusion argument fails.

- **Definition 1's broader scope creates misuse patterns.** If describing human-authored kernel-verified theorems as satisfying "the machine discovery framework" (even at the machine-assisted level) leads to systematic overcounting of machine discovery events in empirical studies that use Definition 1 as their entry criterion, the adversarial's proposed restriction would be practically warranted even if theoretically narrower than ideal. The burden of evidence here falls on showing that the broader scope causes misclassification in practice, not merely in principle.
