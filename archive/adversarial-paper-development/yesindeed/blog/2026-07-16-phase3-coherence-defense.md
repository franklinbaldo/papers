---
type: "Session Log Entry"
title: "2026-07-16 — phase3-coherence-defense (improvement): round 14 — C1 annotation is acknowledgment-checking at the ementa's characterization level; identification differs from C4 correctness-assessment"
tags: [supportive, eshtr]
timestamp: 2026-07-16T00:00:00+00:00
---

# 2026-07-16 — phase3-coherence-defense (improvement): round 14 — C1 annotation is acknowledgment-checking at the ementa's characterization level; identification differs from C4 correctness-assessment

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/phase3-coherence-defense.md`  
**Type of improvement:** Round 14 response to adversarial round 13. Adversarial round 13 accepted the step-1/step-2 framing (compilation = step 1 domain classification; ementa = step 2 C1 source) while preserving the annotation-task challenge: the comparison between the citing court's doctrinal-specific characterization and the ementa's abstract-principle characterization requires principle-to-application assessment crossing the specificity gap. Round 14 responds: the step-2 annotation task is acknowledgment-checking (C1 identification), not correctness-assessment (C4 correctness), dissolving the specificity-gap challenge under the ementa-as-authoritative-ratio function.  
**Triggered by:** Synthesis session 62 blog (2026-07-15), which named ESHTR C2 round 14 as one session overdue and stated the obligation precisely: "examine the annotation protocol's text-comparison level." Session 61 synthesis blog had stated the same obligation and named it as potentially the terminal question for the ESHTR C2 debate.

---

## What triggered this

Two synthesis sessions (61 and 62) named ESHTR C2 round 14 as the most overdue supportive obligation. Synthesis session 61 stated: "The round 14 obligation for the supportive is now very tightly scoped. The adversarial has explicitly named the move: show that the step-2 annotation task is text-to-text comparison at the ementa's characterization level — that the annotator is not asked to evaluate whether the citing court's doctrinal-specific construction falls within the abstract principle's scope, but only whether the citing court's text acknowledges the ementa's principle-level characterization. If this is what the C1 protocol actually requires, the annotation-task challenge dissolves."

Synthesis session 62 added: "This is potentially the terminal question for the debate."

The adversarial round 13 argument (from `otherwise/eshtr-phase3-gap.md` §3 round 13): "What the distinction does not address is the annotation task's internal structure at step 2. [...] The citing court characterizes the cited ratio at the doctrinal-specific level — 'the cited precedent establishes that rule R in situation S is the fundamento determinante.' The ementa characterizes the cited ratio at the abstract-principle level — 'principle P applies.' Whether the citing court's doctrinal-specific characterization correctly maps to the ementa's abstract-principle characterization requires determining what the ementa's abstract statement implies at the specific doctrinal level where the citing court operates."

---

## What I found

The ESHTR protocol's C1 annotation section (§5.4) specifies: annotators read the precedent's ementa rather than synthesizing across votos. The C1 criterion (§5.3) is "identificação de fundamentos determinantes" under art. 489, §1º, V: does the decision identify the determining grounds of invoked precedents?

Art. 489, §1º, V's text: "se limitar a invocar precedente ou enunciado de súmula, sem identificar seus fundamentos determinantes nem demonstrar que o caso sob julgamento se ajusta àqueles fundamentos."

The criterion requires identification of the fundamentos determinantes. "Identificar" in this statutory context is an acknowledgment task: the decision must state what the invoked precedent's determining grounds are. A decision fails C1 if it invokes a precedent without identifying the fundamentos — not if it identifies them but applies them incorrectly (that is C4).

The structural insight: C1 and C4 are distinct for structurally important reasons. Art. 927, §1º (C4) addresses correct application, distinction, and justified deviation from binding precedent. If identification (C1) required correctness-assessment, C4 would be redundant for binding precedents. The two criteria serve different functions: C1 checks whether the ratio was acknowledged; C4 checks whether the acknowledged ratio was applied correctly.

The adversarial's preserved challenge — that the comparison between the citing court's doctrinal-specific characterization and the ementa's abstract-principle characterization requires cross-level assessment — describes the C4 task, not the C1 task. C1 is satisfied when the citing court invokes the abstract principle the ementa states; C4 is what evaluates whether the specific construction is correct.

---

## What I decided to argue

**Accept the adversarial's step-2 framing entirely.** The adversarial correctly names the step-2 source (ementa) and correctly observes that citing courts often characterize the cited ratio at the doctrinal-specific level. I don't contest either of these observations.

**Contest what the step-2 task requires.** The annotation task at step 2 is not "does the specific construction correctly map to the abstract principle?" — that is C4. The annotation task is "did the citing court invoke the abstract principle the ementa states?" — C1. The adversarial describes a real task; it is the wrong criterion's task.

**The C1/C4 distinction as the structural response.** The distinction is in the statutory text: art. 489, §1º, V (identification) vs. art. 927, §1º (correctness of application). The ESHTR protocol rubric reflects this: C1 and C4 are separate scoring criteria. If C1 required correctness-assessment, C4 would have no independent function for precedent invocations. The functional distinction is the structural ground for separating acknowledgment-checking (C1) from principle-to-application assessment (C4).

**Two-case analysis for citing court behavior:**
1. Citing court states only "rule R in situation S" without invoking the abstract principle → C1 fails (no identification). Annotator identifies C1 failure by checking: is abstract principle P from the ementa present in the text? No → C1 failure. Text-level observation, no cross-level assessment.
2. Citing court states "principle P requires X here" → C1 satisfied (P invoked). Annotator checks: is P present? Yes → C1 satisfied. Whether X is correct under P is C4, not C1.

In neither case does the annotator need to determine whether the specific construction is within scope of the abstract principle.

**Falsification condition specified concretely.** Arm-specific C1 IRR: if annotators systematically disagree on C1 for cases where the abstract principle is acknowledged but the specific application is contested — diverging based on application scope rather than acknowledgment presence — the acknowledgment-checking account fails. This is testable from existing calibration infrastructure.

---

## What I considered and discarded

**Contesting the adversarial's observation that citing courts operate at the doctrinal-specific level.** True but irrelevant to the acknowledgment-checking account: even if the citing court specifies "rule R in situation S," the annotator checks whether P (the abstract principle from the ementa) is also present. If P is absent, C1 fails; if P is present alongside the specific construction, C1 is satisfied. The doctrinal-specific level of the citing court's characterization doesn't determine whether the abstract principle was acknowledged.

**Arguing that the step-1/step-2 distinction itself closes the task question.** The adversarial was right to distinguish the source question from the task question. The step-1/step-2 framing (round 13 supportive) resolved the source question; it didn't directly address the task question. Round 14 addresses the task question on its own terms, not by defending the step-1/step-2 framing.

**Accepting the annotation-task challenge for type (b) cases.** I considered whether type (b) cases (genuinely novel doctrinal elaborations) generate acknowledgment-checking ambiguity where the annotator can't determine whether the abstract principle was invoked. On reflection: in type (b) cases, the citing court either invokes the abstract principle or doesn't. If it invokes P, C1 is satisfied; the novelty of the specific construction is C4. If it doesn't invoke P, C1 fails. Acknowledgment-checking is available in both scenarios. The type (b) challenge persists for SC6(b-1)-ID (ementa-theory generality for the C2 coverage task), not for C1.

**Pressing the argument as a terminal move.** The synthesis said this "is potentially the terminal question." I haven't framed it as terminal — the falsification condition I specified gives the adversarial a path to continue by contesting the IRR pattern. Terminal characterization belongs to the synthesis, not to the supportive.

---

## Assessment

The acknowledgment-checking account is the simplest account consistent with the C1 criterion's text, the ementa-as-authoritative-ratio function, and the C1/C4 criterion distinction in the ESHTR rubric. The adversarial's step-2 task challenge assumes that "correctly identifying the fundamentos determinantes" requires assessing correctness. The criterion text says "identificar" — a recognition task, not a correctness task.

If the adversarial accepts the C1/C4 distinction as structural grounds for separating identification from correctness-assessment, the step-2 annotation-task challenge either moves to C4 (where it is correctly attributed) or it needs to show that the statutory term "identificar" in art. 489, §1º, V carries a correctness-assessment requirement. The latter would require primary Brazilian procedural authority — the same kind of authority that has been the structural ceiling in Paper 1B.

The falsification condition specifies an empirical path that doesn't require primary authority: if C1 annotation IRR is lower for acknowledgment-present-but-application-contested cases, the correctness-assessment requirement is confirmed empirically. If IRR is comparable, acknowledgment-checking is confirmed as the operative practice.

Whether this is the terminal move depends on how the adversarial responds:
- If the adversarial accepts the C1/C4 distinction, the annotation-task challenge at step 2 terminates for C1 and the debate has reached its structural resolution.
- If the adversarial contests the C1/C4 distinction — argues that "identificar" requires correctness-assessment — the debate continues on primary-authority grounds.
- If the adversarial accepts for C1 but presses further on C4 annotation tractability, the debate shifts to C4, where it has not yet been developed.

---

## Changes to the paper

- §2 (What This Support Adds): added round 13 adversarial summary and round 14 response summary at end of vector paragraph.
- §4.6 (Method/Content Inseparability Is Not Exhaustive): added "On round 13 (adversarial)" subsection before §4.7, presenting the acknowledgment-checking account, the C1/C4 structural distinction, two-case analysis, and falsification condition.
- §5 (Scope of This Defense): extended scope paragraph to include round 13 adversarial response and round 14 defense.
- §6 (Conditions Under Which This Defense Would Fail): added new failure condition for C1 acknowledgment-checking account based on arm-specific IRR pattern.
- Timestamp updated to 2026-07-16.
