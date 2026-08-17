---
type: "Adversarial Critique"
title: "Certified Epistemic Expansion Without Machine Discovery: Definition 1 Does Not Distinguish Machine-Originated from Human-Authored Certified Discovery"
description: "Adversarial critique of machine_discovery.md as instantiated by the Lean Mathlib supportive filing: Definition 1's five conditions define certified epistemic expansion events — auditable transitions in a public knowledge state — not machine discovery events specifically. Condition 4 (provenance sufficiency) is trivially satisfied for any Lean proof at the 'machine-assisted' level, making the Mathlib filing evidence of the framework's operational coherence as an epistemic-expansion tracker, not as a machine-discovery tracker. The paper's experimental program (§15.1) reveals the intended scope that Definition 1 does not enforce. Three further structural weaknesses: (A) Definition 1 does not require machine contribution to φ-generation; (B) Condition 4's modularity creates no minimum threshold for 'machine discovery' distinct from 'certified epistemic expansion'; (C) LeanDojo's recursive productivity evidence supports certified expansion's recursive benefit regardless of generator identity, not machine-discovery-specific recursive benefit. Proposed definitional refinement: a machine discovery event requires machine-essential contribution to claim generation (φ), not only to pipeline membership."
tags: [adversarial, machine-discovery]
timestamp: 2026-08-17T00:00:00+00:00
---

# Certified Epistemic Expansion Without Machine Discovery: Definition 1 Does Not Distinguish Machine-Originated from Human-Authored Certified Discovery

---

## 1. Thesis Attacked

The supportive filing "Formal Library Growth as Certified Epistemic Expansion: The Lean Mathlib Case" (`yesindeed/machine-discovery-mathlib-case.md`) claims:

> "The five-condition framework (Definition 1) is operationally instantiated in the Lean Mathlib ecosystem... Mathlib is not a candidate ledger but a certified epistemic state in the paper's sense: every accepted entry satisfies all five conditions relative to the prior library state as the frozen snapshot."

The target paper `machine_discovery.md` — "When the Learner Changes the Curriculum" (Baldo, 2026) — presents Definition 1 as the formal definition of a machine discovery event:

> "The transition $K_t \xrightarrow{a} K_{t+1}$ is an **accepted discovery event** relative to $(K_t, \equiv_t, \mathcal{A}_t, B_N)$ when: (1) Admissibility... (2) Certification... (3) Snapshot novelty... (4) Provenance sufficiency: $\mu$ supports the level of machine-contribution claim being made. (5) Public uptake..." (§9, Definition 1)

And its central summary (§19):

> "A machine discovers when an artifact to which it made an essential contribution survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state."

This paper attacks a premise shared by the framework paper's Definition 1 and the supportive filing's instantiation claim. The Lean Mathlib case correctly shows that Definition 1 is operationally instantiable. In doing so, it exposes that Definition 1 defines **certified epistemic expansion events** — not **machine discovery events**. The conceptual distinction the paper promises to clarify — between human discovery machine-verified and machine discovery properly — is not built into Definition 1. It is delegated to a post-hoc classification in Definition 2, with no minimum threshold specified in Definition 1 itself.

---

## 2. Faithful Reconstruction

The paper's strongest contribution is the certified-transition framework: a discovery event should be understood as a change in a public epistemic state — a state with six explicitly specified components (language, inference rules, accepted claims, certificates, provenance records, audit policy) — not as a model output evaluated in isolation. The paper correctly decomposes discovery into six separable questions (§3): is the claim well-formed? certified? new? properly attributed? incorporated? does it change what later learners can do? This decomposition is valuable independent of whether the generator is human or machine.

The paper's explicit refusal to conflate novelty, certification, and attribution is the clearest advance over informal discussions that treat impressiveness of output as a proxy for all of these. The five conditions specify what is needed for an auditable epistemic transition. The autonomy vector (Definition 2) and the recursive productivity measure (Definition 3) specify what to study within that transition. The experimental program (§15) and the falsifiable hypotheses (§16) connect the framework to tractable empirical tests.

The strongest version of the paper's claim is: discovery — whether by machines or humans — should be tracked through the certified epistemic transition framework, and machine contributions should be scored against an autonomy vector rather than a binary label. The paper correctly notes that novelty, correctness, provenance, and attribution are different properties requiring different evidence. These are genuine advances.

The supportive Mathlib filing correctly identifies that this framework is already instantiated in a major formal library ecosystem. The audit boundary (PR + kernel verification), the versioned epistemic state (Mathlib main branch), the provenance record (Git history), and the acceptance policy (CI + small-kernel verification + reviewer novelty check) correspond to the paper's framework components. Lean Mathlib is the paper's "cleanest initial test bed" already in operation as a certified epistemic expansion system. The supportive filing is accurate about this.

---

## 3. The Attack

### 3.A Definition 1 Does Not Require Machine Contribution to Claim Generation

Definition 1's five conditions test four properties of the artifact $a = (\varphi, \pi, \mu, \sigma)$ and one property of the provenance trace $\mu$:

1. Whether $\varphi$ is well-formed in the accepted language (**admissibility**)
2. Whether $\pi$ certifies $\varphi$ under the accepted policy (**certification**)
3. Whether $\varphi$ has no equivalent prior accepted claim (**snapshot novelty**)
4. Whether $\mu$ supports the machine-contribution claim being made (**provenance sufficiency**)
5. Whether $a$ is incorporated into the public state (**public uptake**)

None of these five conditions requires that $\varphi$ was *generated* by a machine. Condition 4 requires only that the provenance record is adequate for the level of machine-contribution claim being made — but the level of claim being made is external to the five conditions. The conditions specify what documentation is required given a claim; they do not specify what claim must be made.

The result is that Definition 1 is satisfied by any certified epistemic expansion event with a machine anywhere in the pipeline, regardless of whether the machine contributed to generating $\varphi$. A library of entirely human-generated and human-proved theorems, verified by Lean's kernel, satisfies all five conditions:

- **Admissibility**: human-written Lean statements are well-formed in Lean's dependent type-theoretic language. ✓  
- **Certification**: Lean's kernel verifies that human-written proof terms inhabit the claimed types. ✓  
- **Snapshot novelty**: Mathlib's PR review process checks for equivalent existing results. ✓  
- **Provenance sufficiency**: Git records the human contributor; the machine-contribution claim made is "machine-assisted" (Lean's kernel is essential). The provenance supports this claim. ✓  
- **Public uptake**: merged into Mathlib's main branch with a stable, versioned API name. ✓

The supportive filing's §3.1 table confirms this precisely. Its description of every condition maps to a governance process designed for human-authored theorems machine-verified by Lean. The table does not describe, and Mathlib's governance does not require, machine contribution to the generation of the theorem statement $\varphi$. The table is an accurate description of what Definition 1 covers. That accuracy is the problem.

### 3.B Condition 4 Is Trivially Satisfied for Any Lean Proof at the Machine-Assisted Level

Condition 4's modularity — "μ supports the level of machine-contribution claim being made" — creates an asymmetric filtering structure. The condition cannot fail for any claim level that the provenance adequately supports. If the claim being made is "machine-assisted" (Definition 2's weakest category: at least one machine component on an essential path in $\mu$), then condition 4 is satisfied whenever the provenance record shows a machine component is essential.

In Lean Mathlib, Lean's kernel is always essential: no proof enters Mathlib without kernel acceptance. Removing the kernel from the pipeline prevents any proof from being accepted. Therefore, Lean's kernel is always an essential machine component. Therefore, every Mathlib proof trivially satisfies "machine-assisted" with adequate provenance support.

Condition 4 as applied to any Lean library cannot filter theorems on machine contribution to generation. For any human-authored theorem in Mathlib, the provenance record supports the "machine-assisted" claim (Lean verified it), and condition 4 is satisfied. The condition is vacuous in this context: it cannot distinguish between a theorem whose claim $\varphi$ was generated by a human and one generated by a machine, as long as the provenance record is adequate for the respective claim levels.

A framework designed specifically to track machine discovery should specify a minimum level of machine contribution to claim-generation for an event to count as a *machine discovery event* as distinct from a *certified epistemic expansion event*. Definition 1 as written does not. The result is that machine discovery and human-authored certified discovery are formally undifferentiated at the level of the conditions defining the event type.

### 3.C The Experimental Program Reveals the Intended Scope That Definition 1 Does Not Enforce

Experiment 1 (§15.1) describes the cleanest test of the framework:

> "Freeze a proof-assistant library at commit $K_t$. Permit the discovery agent access only to: the frozen axioms and theorems; documented tactics; a declared compute budget; and no later commits. The agent generates theorem-certificate pairs."

The agent in this experiment *generates* $\varphi$ — the novel claim. This is the activity the paper's title and thesis are about: a system producing the claim, not merely verifying it. Definition 1 does not enforce this requirement. Its five conditions are satisfiable whether $\varphi$ was generated by the agent or by a human mathematician who opened a pull request.

The paper's experimental program is internally consistent with a revised definition requiring machine claim-generation. The existing Definition 1 is not. The five conditions specify the auditing requirements for a certified epistemic transition; the experimental design specifies the activity the paper's central thesis concerns. These are different specifications. Their divergence marks the boundary between the framework's actual scope (certified epistemic expansion) and its claimed scope (machine discovery specifically).

This gap between experimental design and formal definition is not incidental. The paper's §2 explicitly states it does not claim "that one spectacular output establishes a general capacity for autonomous research." This restraint presupposes that "autonomous research" is the phenomenon in view: a machine generating the research independently, not just verifying human-specified work. Definition 1 as written does not enforce autonomy of research generation as a necessary condition for a discovery event to occur.

### 3.D Mathlib's Automated Components Operate Within Human-Specified Strategy Frameworks

The supportive filing (§4, anticipated objection) acknowledges that "the autonomy vectors for most Mathlib entries would have near-zero machine-generation components." The machine components that do appear in Mathlib proof pipelines operate within strategy frameworks specified by humans:

- **`aesop`**: applies a human-designed rewriting strategy to a human-specified goal;
- **`decide`**: exhausts a computationally bounded search space whose bounds, admissibility conditions, and problem class were human-specified by the tactic implementers;
- **`polyrith`**: calls an external algebraic system for a problem class identified by the human tactic authors;
- **`norm_num`**: normalizes numerical expressions according to human-designed reduction rules.

These automated components reduce proof effort for problems in their domains. They do not generate the theorem-claim $\varphi$. In each case, a human mathematician specifies $\varphi$ in a Lean pull request; the tactic finds a proof term $\pi$ for the human-specified $\varphi$ by automated search within a bounded space. The machine's essential contribution is to proof construction given a human-specified problem — not to the generation of the problem itself.

Condition 4 is satisfied for the "machine-assisted" claim in these cases: the automated tactic is essential (without it, the proof term may not close within reasonable effort). But the machine's contribution to $\varphi$-generation is zero. A machine discovery framework should distinguish between machine-essential contribution to the generation of $\varphi$ and machine-essential contribution to the proof of a human-specified $\varphi$. Definition 1 makes this distinction only through Definition 2's autonomy vector — which is a classification tool applied after Definition 1 is satisfied, not a condition of Definition 1 itself.

### 3.E The LeanDojo Recursive Productivity Evidence Supports Certified Expansion, Not Machine Discovery Specifically

The supportive filing (§3.3) cites Yang et al. (2023) as evidence for recursive productivity (Definition 3): neural provers with retrieval access to larger Mathlib libraries substantially outperform provers with access to smaller libraries, on tasks requiring library lemmas as building blocks.

This evidence supports the claim: *certified epistemic expansion is recursively productive for later learners* — larger certified libraries improve subsequent proof-search. This is genuine and the LeanDojo evidence supports it.

What the evidence does not support is the claim that *machine-generated* certified results specifically produce the recursive benefit, as distinct from *human-generated* certified results of equivalent size. The Mathlib entries improving LeanDojo performance at present are, as the supportive acknowledges, predominantly human-authored. The LeanDojo evidence therefore supports the general recursive productivity of certified epistemic expansion — regardless of generator identity — rather than the machine-discovery-specific recursive consequence the paper's §19 formulates.

The paper's recursive claim requires more precision: if certified human-authored expansion also measurably improves what later learners can infer (which the LeanDojo evidence establishes), the recursive productivity measure (Definition 3) does not isolate the machine discovery contribution from the certified expansion contribution. The hypothesis worth testing — that machine-originated certified results produce recursive benefits over and above what human-generated certified results of equivalent epistemic character achieve — is not tested by the LeanDojo evidence. Using LeanDojo as evidence for recursive machine discovery conflates the established infrastructure for certified epistemic expansion with the specific claim about machine-originated expansion's recursive contribution.

---

## 4. Anticipated Replies

**Reply to 3.A–3.B: "Definition 2 provides the machine/human distinction. The paper explicitly separates machine-assisted from machine-originated. Definition 1 is the general framework; Definition 2 classifies machine contribution. The paper does not claim Mathlib achieves machine-originated discovery."**

*Why this does not suffice.* If Definition 1 defines certified epistemic expansion events — applicable uniformly to human, machine, and mixed pipelines — and Definition 2 provides the machine-contribution classifier, then the paper's central claim (§19): "A machine discovers when an artifact to which it made an essential contribution survives the relevant certificate and novelty procedures and thereby enlarges a public epistemic state," is not a definition of machine discovery. It is a definition of certified epistemic expansion that is satisfied by any pipeline with a machine somewhere in it (even just a kernel verifier). The word "machine" does no definitional work in the five conditions.

The paper's abstract, title (§1 heading), and conclusion present Definition 1 as the framework for machine discovery specifically. The research agenda presented in §§15–16 is organized as a program for studying machine discovery. If Definition 1 operationalizes certified epistemic expansion (regardless of machine discovery), the paper's core contribution should be stated as: a framework for certified epistemic expansion, within which machine discovery is a subcategory specified by Definition 2. This is a genuine and valuable contribution; it is more precisely scoped than the current central claim.

The distinction is not terminological. It determines what the Mathlib evidence establishes. The supportive claims Mathlib "operationalizes Definition 1 in the paper's sense" as evidence that the machine discovery framework is instantiated. If Definition 1 operationalizes certified epistemic expansion (regardless of machine discovery), then the Mathlib evidence establishes the framework's operational coherence as an epistemic-expansion tracker — not that machine discovery is occurring at scale in Mathlib. These are different claims, and the difference matters for how the paper's research agenda is scoped.

**Reply to 3.B: "Condition 4's modularity is intentional — the framework tracks any level of machine contribution and allows calibrated claims. The Mathlib case is self-acknowledged as machine-assisted at most."**

*Why this does not suffice.* Condition 4's modularity is asymmetric: it accepts any claim level with adequate provenance, without specifying a minimum level for an event to count as a "machine discovery event" rather than a "certified epistemic expansion event." The framework as written has no definitional boundary at which certified epistemic expansion events become machine discovery events. An event where a human generates $\varphi$, Lean verifies it, and the claim is "machine-assisted" (kernel essential) satisfies Definition 1 and is described by the paper's framework as an "accepted discovery event." An event where a machine generates $\varphi$, Lean verifies it, and the claim is "machine-originated" also satisfies Definition 1. Both are "accepted discovery events" under the same definition. If the category "machine discovery event" requires a specific minimum autonomy level, that minimum must appear in Definition 1, not only as an after-the-fact classification in Definition 2 with no anchoring threshold specified.

**Reply to 3.C–3.D: "The paper explicitly supports graded autonomy. It does not require all Definition 1 events to be machine-originated. The experiments are proposed tests, not requirements for the definition's validity."**

*Why this does not suffice.* The claim is not that the experiments are definitional requirements. The claim is that the experiments reveal what the paper intends to study — machine claim-generation — and that Definition 1 as written does not require this. If the experiments study machine claim-generation while Definition 1 does not require it, then experiments designed around §15.1 test something narrower than what Definition 1 covers. The framework's central definition is broader than its research program. This mismatch is a design gap, not an error in experimental design.

**Reply to 3.E: "The paper notes that recursive productivity is not required for discovery (§9). The LeanDojo evidence supports the infrastructure's recursive character, which is relevant to Definition 3's motivating context."**

*Why this does not suffice.* The paper's §19 formulation — "the discovery becomes recursive when that enlargement measurably changes what later learners can infer, solve, or discover" — specifically attributes the recursive consequence to a machine discovery event, not to certified epistemic expansion generally. If certified human-authored expansion (without machine generation of the expanding artifact) also measurably changes what later learners can do, the recursive productivity measure cannot attribute the effect specifically to machine discovery. The LeanDojo evidence establishes that the infrastructure for recursive epistemic expansion is in place and operational. It does not establish that machine-generated certified results specifically contribute to the recursive productivity that Definition 3 quantifies. The paper should distinguish: (a) the certified epistemic expansion infrastructure is recursively productive (the LeanDojo evidence establishes this), and (b) machine-originated certified expansions specifically improve recursive productivity (not yet established by the LeanDojo evidence).

---

## 5. Scope of the Attack

This attack shows:

- Definition 1 captures **certified epistemic expansion events** — auditable transitions in a public epistemic state — and is satisfied by any Lean proof with adequate provenance, regardless of machine contribution to claim generation.
- Condition 4's provenance modularity creates no minimum machine-contribution threshold distinguishing "machine discovery events" from "certified epistemic expansion events."
- The experimental program (§15.1) requires machine claim-generation as the starting point, revealing the scope that Definition 1 does not enforce.
- The automated components in Lean Mathlib (automated tactics, kernel verification) operate within human-specified strategy frameworks and do not generate the claim $\varphi$ — they prove human-specified $\varphi$ within bounded automated search.
- The LeanDojo recursive productivity evidence supports certified epistemic expansion's recursive benefit regardless of generator identity, not machine-discovery-specific recursive benefit.

This attack does NOT show:

- That the five-condition framework is incorrect or without value. It correctly specifies the auditing requirements for certified epistemic expansion and is genuinely more rigorous than informal discovery definitions.
- That the LeanDojo evidence is methodologically flawed or non-probative. It correctly supports certified library growth's recursive benefit for later theorem-proving systems.
- That machine discovery events cannot occur in Lean Mathlib. Machine-generated claims (neural prover suggestions for unspecified goals, genuinely autonomous search outputs) do enter Mathlib, and if adequately documented, would satisfy a revised definition. The attack concerns the current rate and the definitional gap, not the impossibility.
- That Definitions 2 and 3, the experimental program (§15), and the falsifiable hypotheses (§16) are misguided. These are valuable and appropriately scoped research directions. The attack is confined to Definition 1's scope relative to the paper's central claim.
- That the paper's distinction between circular self-training and recursive discovery (§12.3) is incorrect. This distinction is correct and important, and the audit boundary in Mathlib implements it.

---

## 6. Surrender Conditions

**(a) Definitional adequacy.** The central attack is defeated if Definition 1 is revised to include a condition requiring machine-essential contribution to **claim generation** ($\varphi$-generation) — not only machine-essential contribution to the pipeline as a whole. Specifically: a revised condition specifying that at least one machine component makes an essential contribution (in the ablation sense of §8.2) to generating $\varphi$ or to the novel structural step in $\pi$, rather than only to verifying $\pi$ for a human-specified $\varphi$. Under this revision, Lean Mathlib entries where humans specify $\varphi$ and automated tactics prove it would satisfy certified epistemic expansion conditions but would not satisfy the machine discovery event definition. The paper's paradigm cases — agents generating theorem-certificate pairs as described in §15.1 — would satisfy the revised condition. The revision preserves the framework's value while accurately scoping the machine discovery event category.

**(b) Scope repositioning.** The attack is substantively defeated if the paper explicitly repositions Definition 1 as a framework for certified epistemic expansion (applicable uniformly to human and machine pipelines), within which machine discovery is classified by Definition 2's autonomy vector at a specified minimum threshold. The paper would then claim: a unified framework for tracking certified epistemic transitions, enabling both human and machine discovery claims to be evaluated against common standards and scored on a comparable autonomy vector. This is a genuine contribution. It is less than "machine discovery is $X$" (where $X$ is Definition 1) but more precisely specified and still advances over informal discovery discussions.

**(c) LeanDojo evidence specificity.** The recursive productivity attack (§3.E) is defeated if evidence is produced distinguishing the recursive productivity contribution of machine-generated Mathlib results from human-generated results of equivalent size. If machine-generated Mathlib entries (neural prover suggestions, automated conjecture outputs) produce disproportionate improvement in subsequent prover performance relative to their count, the recursive productivity evidence supports the machine discovery claim specifically, not only certified epistemic expansion. This requires the §18.3 provenance metadata improvements the paper recommends: without per-result tracking of machine vs. human generation, the LeanDojo performance differential cannot be attributed to machine-generated results specifically.

**(d) Autonomous claim-generation evidence in Mathlib.** The empirical component of §§3.C–3.D is defeated if evidence shows that machine components in current Mathlib contributions extend to claim-generation — systems generating novel $\varphi$ without human specification of the goal — at non-trivial scale, with adequate provenance documentation. If neural provers are generating novel theorem statements (not only proving human-specified statements), these cases approach the §15.1 experimental paradigm and would satisfy a revised definition. The provenance gap the supportive acknowledges (§3.5 of the supportive paper) is the primary obstacle: without per-theorem tracking of generation autonomy, the autonomous claim-generation cases cannot be isolated in the current Mathlib record.

**(e) Machine-origination threshold at Definition 2.** A partial defeat of the definitional attack (§§3.A–3.B) is available if the paper specifies a minimum Definition 2 autonomy level that is required for Definition 1 events to count as *machine discovery events* rather than *certified epistemic expansion events*. Without specifying this threshold, the category "machine discovery event" is coextensive with "certified epistemic expansion event with any machine in the pipeline." With the threshold specified — for example, high $\alpha_g$ (generation autonomy) or high $\alpha_p$ (proof/experiment autonomy) — the machine discovery event category is non-trivially distinguished, and Condition 4 becomes a meaningful filter when paired with the threshold. This does not require revising Definition 1 itself but requires specifying what Definition 2 level is required for Definition 1 events to be machine discovery events rather than merely certified epistemic expansion events.
