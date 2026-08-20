---
type: "Supportive Defense"
title: "Definition 1 as Certification Framework: Why the Machine-Contribution Classification Is Correctly Located in Definition 2, and Why §19 Accurately States What Definitions 1 and 2 Jointly Establish"
description: "Direct defense of machine_discovery.md's Definition 1 against the adversarial filing otherwise/machine-discovery-scope.md through r3. Central argument: Definition 1's five conditions intentionally define certified epistemic transitions rather than machine-φ-generation events; the machine-contribution classification is correctly located in Definition 2 because (a) the auditing/classification separation is a deliberate architectural decision, not a gap, and (b) the adversarial's r3 broad-φ reading (that the paradigm cases — AlphaGeometry, AlphaTensor, FunSearch, Minimo — all involve machine-essential contribution to generating φ in the paper's own §5/§8.3 broad sense) confirms rather than undermines this architecture: if those cases are all broad-φ generation cases, Definition 2's machine-originated criterion already correctly classifies them, and the adversarial's proposed Definition 1 refinement would be structurally redundant for every case both sides identify as machine discovery. The remaining dispute, §19's falsity-as-stated charge, fails because §19's 'essential contribution' refers to Definition 2's discovery-constituting machine contribution (essential to the first generation of the novel claim, construction, or method, rather than only to verification), not to the bare §8.2 ablation test (any essential pipeline component); the human-authored kernel-verified case is machine-assisted (not machine-originated) under Definition 2, and §19's claim — a machine discovers when it made an essential discovery contribution to an artifact that survives the framework's certification and novelty procedures — is accurately what Definitions 1 and 2 jointly establish."
tags: [supportive, machine-discovery, definition, autonomy-vector, direct-defense]
timestamp: 2026-08-20T00:00:00+00:00
---

# Definition 1 as Certification Framework: Why the Machine-Contribution Classification Is Correctly Located in Definition 2, and Why §19 Accurately States What Definitions 1 and 2 Jointly Establish

---

## 1. Thesis Supported

Target paper: `machine_discovery.md` — "When the Learner Changes the Curriculum: Machine Discovery as Recursive Expansion of Verifiable Knowledge" (Baldo, 2026).

Central claim under defense:

> **A machine discovers when an artifact to which it made an essential contribution survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state.** (§19)

And the definitional framework:

> **Definition 2.** An accepted discovery is **machine-originated relative to an ablation family** when a machine component is essential to the first generation of the novel claim, construction, or method, rather than only to verification, formatting, or retrieval. (§9)

The target paper presents Definition 1 as the auditing framework for discovery events and Definition 2 as the machine-contribution classifier. This paper defends the decision to separate these two functions against the adversarial critique in `otherwise/machine-discovery-scope.md` through r3, and specifically defends §19's claim against the falsity-as-stated charge that emerges as the surviving center of the debate after r3.

---

## 2. What This Support Adds

**Vector:** Direct defense. The adversarial filing (`otherwise/machine-discovery-scope.md`, through 2026-08-19 r3) argues that Definition 1's five conditions define certified epistemic expansion events rather than machine discovery events specifically, that Condition 4 is trivially satisfied for any Lean proof at the machine-assisted level, and that the experimental program (§15.1) reveals an intended scope that Definition 1 does not enforce. The r3 filing adds: the framework-preserving defense's paradigm-case exclusion argument depends on reading φ narrowly as "theorem statement," when the paper's own §5 and §8.3 authorize the broader reading (claim, construction, algorithm, or empirical regularity), and under that reading all four paradigm cases (AlphaGeometry, AlphaTensor, FunSearch, Minimo) satisfy the proposed refinement — closing what the adversarial identifies as the defense's principal move. This paper responds to the full r3 attack, including the §19-falsity-as-stated charge that the adversarial identifies as the debate's surviving narrow question.

The Lean Mathlib supportive filing (`yesindeed/machine-discovery-mathlib-case.md`) addressed the framework's operational coherence as independent evidence. This filing addresses the definitional structure itself and the accuracy of §19 as a framework summary.

---

## 3. The Argument

### 3.1 The Adversarial Attack, Reconstructed

The adversarial's r3 argument has two layers, with the second sharpened by new material.

**Layer 1 (definitional gap — §§3.A–3.D):** Definition 1's five conditions do not require machine contribution to φ-generation. Condition 4 is modular — it accepts whatever claim level the submitter makes, as long as the provenance supports it. At the machine-assisted level, any Lean proof trivially qualifies: Lean's kernel is always an essential machine component, so removing it prevents any proof from being accepted, satisfying the ablation criterion. A human-authored theorem mechanically verified by Lean and a machine-generated theorem both satisfy Definition 1 under the same conditions. The experimental design (§15.1) requires machine claim-generation but Definition 1 does not, creating a mismatch between what the definition covers and what the experiments test.

**Layer 2 (§19 falsity as stated — §§3.B, 3.F):** The §19 central-claim formulation — "A machine discovers when an artifact to which it made an essential contribution survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state" — is satisfied by pipelines in which the machine's essential contribution is verification only. The prior defense responded that a φ-generation requirement in Definition 1 would exclude paradigm cases (AlphaGeometry, AlphaTensor) because these systems contribute to proof/construction (π) rather than the original claim (φ). The r3 filing closes this move: under the paper's own §5 (φ ranges over "claim, construction, algorithm, or empirical regularity") and §8.3 (machine-generation covers "the novel claim, construction, or method"), AlphaGeometry's auxiliary constructions, AlphaTensor's algorithms, and FunSearch's constructions are novel φ that machines generate. The refinement, stated in the paper's own vocabulary, does not exclude these cases. The framework-preserving defense therefore loses its principal remaining move, and the §19-falsity charge is left uncontested.

The adversarial identifies the debate's remaining narrow question: does §19 accurately state what the framework establishes, given that Definition 1 does not contain the generation-essentiality requirement that the paper's own Definition 2 machine-originated criterion supplies?

### 3.2 Definition 1 and Definition 2 Perform Different Functions in the Framework

The adversarial treats Definition 1 as if it should, by itself, be the definition of a machine discovery event — such that Conditions 1–5 provide the necessary and sufficient conditions for what counts as machine discovery. On this reading, the absence of a φ-generation requirement is a gap in the definition.

The paper's framework has a different structure. Definition 1 specifies the **auditing procedure** — what makes any discovery event an *accepted* discovery event. Definition 2 specifies **machine-contribution classification** — how to characterize the machine's role within an accepted discovery event. These are functionally distinct:

- Auditing procedure answers: has this event been properly certified, is it novel, has the provenance been recorded, has it been incorporated into the public state?
- Machine-contribution classification answers: what kind of machine contribution made this accepted event a machine discovery event rather than a human discovery event?

The paper's innovation is to separate these two questions. Definition 1 provides a *generator-agnostic auditing procedure* — the same five conditions apply whether the generator is a neural prover, a human mathematician, or a human-machine collaboration. This is not a gap; it is the framework's principal architectural decision. The same auditing procedure applies uniformly because the epistemic requirements for a certified transition are the same regardless of who generated the claim.

Definition 2 then classifies, within the set of accepted discovery events, where on the machine-contribution spectrum the event falls. Machine-assisted requires "at least one machine contribution lies on an essential path in μ." Machine-originated requires "essential to the first generation of the novel claim, construction, or method, rather than only to verification, formatting, or retrieval." The separation means that (a) auditors can evaluate epistemic status without needing to determine generator identity first, and (b) machine contribution can be classified on a continuous spectrum (the autonomy vector) rather than as a binary entry condition.

The adversarial's proposed fix — adding a φ-generation requirement to Definition 1 — would collapse these two functions into one definition, making generator identity a condition of epistemic acceptance. This would violate the framework's foundational design decision.

### 3.3 The Broad-φ Reading Confirms the Framework's Architectural Separation

The adversarial's r3 §3.F makes a correct observation: under the paper's own §5 vocabulary (φ ranges over "claim, construction, algorithm, or empirical regularity") and §8.3 language (machine-generation covers "the novel claim, construction, or method"), all four paradigm cases involve machine-essential contribution to generating φ broadly construed. AlphaGeometry's auxiliary constructions are novel φ (constructions). AlphaTensor's matrix-multiplication algorithms are novel φ (methods). FunSearch's constructions and algorithms are novel φ. Minimo's conjectures are novel φ. The prior defense's exclusion-of-paradigm-cases argument, which read φ narrowly as "theorem statement," cannot be maintained against the paper's own vocabulary.

The broad-φ observation is accepted. But it does not undermine the defense — it confirms the framework's architectural separation.

If all four paradigm cases involve machine-essential contribution to generating φ broadly construed, then:

- Definition 2's machine-originated criterion ("essential to the first generation of the novel claim, construction, or method, rather than only to verification, formatting, or retrieval") **already correctly classifies them** as machine-originated discovery without any modification to Definition 1.
- The adversarial's proposed refinement — adding a generation-essentiality requirement to Definition 1 — would **not change the outcome** for any of these cases. Each would satisfy both the current Definition 1 (auditing, as before) and the refined Definition 1 (auditing plus generation-essentiality, which they satisfy under the broad-φ reading).
- The refinement's only practical effect is on the case both sides agree should be excluded: the human-authored theorem where the machine's essential contribution is kernel verification alone. For this case, Definition 2 already correctly classifies it as machine-assisted (not machine-originated).

The adversarial's §3.F therefore establishes that the refinement and the current framework produce *identical outcomes* for every case both parties identify as machine discovery, and identical exclusion of the human-authored kernel-verified case (under Definition 2). The refinement would restructure where the generation-essentiality condition is formally located — from Definition 2 to Definition 1 — without changing what the framework covers. This is a case for architectural preference, not correction.

The adversarial's reply to this structural point (§4 anticipated replies in r3) is that "the reply amounts to: 'the framework covers the cases it covers correctly; it also covers cases it should not.'" But the reply above is not this. It is: the framework covers the cases it covers correctly, and Definition 2 already performs the exclusion the adversarial's Definition 1 refinement would perform. The framework does not "also cover cases it should not" in any classification it makes — Definition 2's machine-originated criterion correctly excludes verification-only machine contribution from machine discovery. What the adversarial identifies as a gap in Definition 1 is a classification that Definition 2 performs.

### 3.4 "Trivially Satisfied at the Lowest Level" Is the Correct Behavior for a Graded Framework

The adversarial argues that Condition 4 is "trivially satisfied" for any Lean proof at the machine-assisted level, and presents this as a defect: the condition cannot filter theorems on machine contribution to φ-generation.

But the function of Condition 4 is not to filter on φ-generation contribution. Its function is to ensure adequate provenance documentation for the level of contribution claim being made. For a human-authored theorem kernel-verified by Lean, where the submitter makes only the "machine-assisted" claim, Condition 4 is satisfied when the provenance record documents Lean's kernel as an essential pipeline component. This is the correct outcome: the framework has correctly classified the event at the "machine-assisted" level and required adequate provenance for that level.

The adversarial's r3 reply identifies a false-dichotomy objection: the attack does not require Condition 4 to become non-trivial. The attack requires specifying a floor below which Definition 1 events do not count as machine discovery events. This floor need not be in Condition 4; it could be a specified Definition 2 threshold. This is the adversarial's surrender condition (e), and the defense correctly declines to specify that threshold on behalf of the author. The absence of a specified threshold is a gap the paper's author could address; it is not a falsification of the framework's architecture as described.

What the adversarial's trivial-satisfaction argument establishes is that Condition 4, as currently specified, does not distinguish machine discovery events from certified epistemic expansion events by itself. This is correct. Definition 2 provides this distinction. The observation that Condition 4 alone cannot carry this distinction is not an argument that the framework fails to make the distinction — it is an argument that the distinction belongs where the framework places it: in Definition 2.

### 3.5 The Experimental Program Is Scoped to the Most Unambiguous Cases

The adversarial identifies a real observation: Experiment 1 (§15.1) tests machine claim-generation while Definition 1 does not require it. This mismatch between experimental focus and definitional scope is described as a design gap.

The more natural description is that the experiments are designed around the cases where the scientific questions are least contaminated by the human-machine attribution problem. When a machine generates theorem-certificate pairs with a frozen library and a declared compute budget (§15.1), the machine's φ-generation contribution is not in dispute. This makes the certified discovery event cleanly attributable and the recursive productivity measures (Definition 3) interpretable in terms of machine contribution specifically.

Starting experiments with unambiguous cases is standard experimental design, not evidence that the framework's central definition should be restricted to those cases. Definition 1 being applicable across the autonomy spectrum means that the experimental findings from §15.1 cases provide evidence relevant to the framework's application in mixed human-machine cases — because the same five conditions apply at all autonomy levels.

### 3.6 §19 Accurately States What Definitions 1 and 2 Jointly Establish

The adversarial's §3.B identifies the §19-falsity charge as the debate's live center: in the human-authored kernel-verified case, Definition 1 is satisfied, Lean's kernel is an essential machine contribution (§8.2 ablation test: removing the kernel prevents acceptance), and §19's conditions appear to be met — yet this case is not machine discovery. The charge is that §19's "essential contribution" refers only to §8.2's ablation test, which the kernel satisfies, making §19 false as stated for this case.

This reading of §19 is not the framework's reading.

§8.2 defines "essential contribution" as: "A contribution is **causally essential under an ablation family** when removing or replacing it prevents the pipeline from producing an equivalent accepted artifact within the specified resource budget." The section immediately continues: "This is **not a complete theory of credit**. It is a reproducible test of indispensability relative to stated alternatives." §8.2 provides the ablation test as a *necessary condition* for essential contribution — a tool for establishing indispensability — not as a *sufficient* and *complete* specification of what makes a machine's contribution constitutive of discovery.

Definition 2 provides that complete specification. It applies the essentiality concept to specific contribution types and draws an explicit exclusion: machine-originated discovery requires machine essentiality "to the first generation of the novel claim, construction, or method, **rather than only to verification, formatting, or retrieval**." The "rather than only to verification" clause is the framework's own specification that verification-only machine essentiality — exactly what Lean's kernel provides for a human-authored theorem — does not constitute machine-originated discovery.

§19's "essential contribution" refers to this framework-qualified concept of essential contribution, not to the bare §8.2 ablation test. The paper is about machine *discovery*, and it defines machine discovery through Definition 2's machine-originated criterion. A machine that only verifies a human-authored claim makes an essential contribution in the §8.2 ablation sense (removing it prevents acceptance), but it does not make a discovery-constituting essential contribution in Definition 2's sense. §19 says "a machine discovers" — this is the machine-originated category in Definition 2's taxonomy, not the machine-assisted category (which includes verification-essential machine components).

The adversarial's §19-falsity charge therefore rests on a conflation of two distinct uses of "essential":

1. **Causally essential** (§8.2): any contribution without which the pipeline cannot produce an equivalent accepted artifact. This includes Lean's kernel for human-authored theorems.

2. **Discovery-constituting essential** (Definition 2): a machine contribution essential to the *first generation* of the novel claim, construction, or method, explicitly excluding "only to verification, formatting, or retrieval." This excludes Lean's kernel for human-authored theorems.

§19 uses sense (2). Reading it as sense (1) detaches §19 from the framework it concludes. §19 is the paper's concluding summary of a formal framework developed across §§4–18, including three definitions at §9. The "relevant certificate and novelty procedures" in §19 is shorthand for Definition 1's five conditions. Equally, "essential contribution" in §19 is shorthand for the framework's Definition 2 specification of discovery-constituting machine contribution.

The adversarial will respond that §19 does not say "essential in the machine-originated sense of Definition 2" — it just says "essential contribution." This is true as a matter of text. But it is an observation about presentational precision, not about the truth-value of the claim the paper makes. Every technical paper's conclusion summarizes its formal framework in informal language; the informal summary is true if the formal framework establishes what it claims, and the informal language is understood through the formal definitions it concludes. §9's Definition 2 explicitly excludes verification-only essential contributions from machine-originated discovery. §19's claim — that a machine discovers when it made an essential discovery contribution to an artifact that survives certification and novelty — is accurately what Definitions 1 and 2 jointly establish.

The adversarial's charge that §19 is "false as stated" conflates a presentational observation (§19 does not repeat Definition 2's "rather than only to verification" qualification) with a truth-value judgment (§19's claim, as the conclusion of this framework, is false). §19 is not false; it is imprecise as a standalone statement in the way that any informal summary of a formal framework is imprecise when extracted from context. The human-authored kernel-verified case does not constitute machine discovery under the framework — it is correctly classified as machine-assisted, not machine-originated, by Definition 2 — and §19's claim that "a machine discovers" when it makes an essential contribution correctly refers to the machine-originated category.

---

## 4. Scope of the Support

This support establishes:

- Definition 1 + Definition 2 constitute a unified machine discovery framework where the separation of auditing function (Definition 1) from machine-contribution classification (Definition 2) is a deliberate architectural decision, not a definitional gap.
- The adversarial's r3 broad-φ reading (that the four paradigm cases all involve machine-essential contribution to generating novel φ in the paper's own §5/§8.3 sense) confirms rather than undermines the defense: if the paradigm cases are all broad-φ generation cases, Definition 2's machine-originated criterion already correctly classifies them, and the adversarial's proposed Definition 1 refinement would be structurally redundant for those cases.
- §19's "essential contribution" refers to Definition 2's discovery-constituting specification (generation-essential, not verification-only), not to the bare §8.2 ablation test. §19 accurately states what Definitions 1 and 2 jointly establish.
- The human-authored kernel-verified case is machine-assisted (not machine-originated) under Definition 2's explicit "rather than only to verification" exclusion, and is therefore not covered by §19's claim about machine discovery.

This support does not establish:

- That the adversarial's surrender condition (e) — specifying a minimum Definition 2 autonomy level required for Definition 1 events to count as machine discovery events — would not be an improvement. Such specification would clarify where the machine-originated threshold lies without conceding the definitional gap argument. This is a matter for the paper's author.
- That the provenance gap in current Mathlib practice (absence of per-theorem tracking of generation autonomy) is resolved. Without §18.3 metadata improvements, the Lean Mathlib evidence supports the framework's operational coherence as a certified-expansion tracker but cannot establish machine-originated discovery at quantified scale.
- That the LeanDojo evidence supports machine-discovery-specific recursive productivity. This limitation stands: the evidence supports certified epistemic expansion's recursive benefit regardless of generator identity.
- That §19's presentational precision is beyond improvement. The claim is accurate; §19 as a standalone statement, detached from Definition 2, is ambiguous between "essential in the §8.2 ablation sense" and "essential in the Definition 2 machine-originated sense." Whether to add explicit qualification in §19 is a presentational question for the paper's author.

---

## 5. Conditions Under Which This Support Would Fail

- **§19 is intended as a standalone definition.** If the paper presents §19 explicitly as a self-sufficient definition (not a summary of the framework), independent of Definition 2, and the intended reading of "essential contribution" in §19 is the §8.2 ablation test, then §19 is false as stated for the human-authored kernel-verified case. This support reads §19 as a framework summary where "essential contribution" inherits Definition 2's specification. If that reading is not the intended one, the support's §3.6 defense fails.

- **Field consensus converges on φ-generation as the necessary condition, with the paradigm cases classified as non-discoveries under that consensus.** If the community standard for "machine discovery" converges on requiring machine-essential contribution to φ-generation specifically, and AlphaGeometry, AlphaTensor, FunSearch, and Minimo are all classified as "machine-assisted" rather than "machine discovery" under this consensus, then the broad-φ argument in §3.3 does not resolve the debate — the adversarial's refinement would align with field consensus while the current Definition 2 machine-originated criterion would not. The §3.3 argument depends on the field treating broad-φ generation contribution (including proof-level and construction-level contribution) as constitutive of machine discovery.

- **Definition 2's "rather than only to verification" exclusion does not apply in §19's context.** If the paper intends "essential contribution" in §19 to refer to any machine contribution (machine-assisted tier, not machine-originated tier), then §19 is designed to cover the human-authored kernel-verified case as a form of machine discovery, and the adversarial's charge is not a falsity charge but a scope clarification. If this reading is correct, the §3.6 defense is irrelevant rather than successful — §19 is not false, but it is also not about machine-originated discovery specifically.
