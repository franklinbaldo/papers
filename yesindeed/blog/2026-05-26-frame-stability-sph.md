# 2026-05-26 — frame-stability-sph (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/frame-stability-sph.md`  
**Target:** `embedding_seeded_tournament_paper.md` (ESHTR), Phase 2 quality-dimension correlation claim  
**Adversarial section engaged:** `otherwise/eshtr-phase3-gap.md`, §3.2 — "The quality-dimension correlation argument conflicts with the rubric's architecture and with the structure of appellate corpus generation," specifically the C2 structural distinctness sub-argument (lines 204–230 of the adversarial paper)  
**Type of improvement:** Closing the C2 gap in the case-driven quality-dimension variation response

---

## What triggered this

The synthesis blog has flagged the ESHTR Phase 2 C2 structural distinctness argument as unanswered for five consecutive sessions (sessions 7–11), with session 11 explicitly marking the C2 response as "mandatory (session 12 or 13)." The synthesis notes that if the response doesn't land before the session 14 edit cycle, the adversarial C2 argument enters the edit cycle as an uncontested point, requiring the main paper to absorb it as an acknowledged limitation.

The adversarial paper identified a specific gap in `frame-stability-sph.md`'s §3.2 response to the case-driven quality-dimension variation objection. The existing response exempted C3 and C5 as writing-disposition properties that track the judge's analytical care regardless of what the case required — and the adversarial paper immediately responded that this exemption does not hold for C2: C2 performance is constrained by the adversarial record quality, not only by writing disposition. This is the C2 structural distinctness sub-argument, and the supportive paper had no answer to it.

Session priority: Paper 1A now has two supportive papers (ed-nonautonomy-defense.md, ed-recall-range-defense.md), both landing since session 11. The STT adversarial response (PTF-as-architectural-constraint) has landed and will need a supportive reply, but the synthesis said to await it before returning to STT, and the Paper 1A defensive papers addressed the highest-urgency live attack first. The C2 gap is the oldest unanswered specific argument in the corpus — older than the STT PTF-constraint argument, older than the paper1A attack — and its approach to session 14 makes it time-sensitive.

---

## What the C2 structural distinctness argument says

The adversarial paper's §3.2 accepts the supportive paper's claim that C3 and C5 track writing disposition (a judge's propensity for careful, non-formulaic analysis that applies regardless of case demands). It contests the quality-dimension correlation argument by identifying C2 as the exception:

- C2 (art. 489, §1º, IV) measures whether the decision addresses arguments capable of affecting the outcome
- C2 performance is constrained by what material arguments were available to engage
- A case where the opposing party's strongest argument was unmeritorious will produce thin C2 even in a careful judge — not from a writing-disposition deficit, but because there was no strong argument to engage
- This makes C2 variation within a cluster a compound of judge-level engagement skill AND case-level adversarial record quality — a compound writing disposition cannot smooth

The concern: within a fine-grained doctrinal cluster, cases arrived at the appellate level for different reasons, with different argument quality. Some cases had strong adversarial arguments forcing elaborate C2 engagement; others didn't. If C3 and C5 are uniformly high for careful judges while C2 varies with adversarial record quality, this creates asymmetric profiles across cluster members — exactly the configuration that generates criterion-switching triples.

---

## What the improvement adds

The improvement extends the case-driven variation response in §3.2 with two arguments that directly engage the C2 structural distinctness claim.

**Argument 1: C2 evaluates analytical conduct toward arguments, not the arguments' intrinsic strength.**

C2 is satisfied by the quality of engagement, not by the volume or elaboration proportional to argument strength. A carefully reasoned explanation of why a raised argument does not clear the "capable of affecting the outcome" threshold demonstrates the same analytical care as elaborate analysis of a stronger argument: identifying the applicable legal standard, characterizing the argument's limits, applying the standard to show the shortfall. A calibrated LLM judge assessing C2 from the decision's text is evaluating whether the court reasoned correctly about the arguments raised — not whether the arguments provided opportunity for extensive elaboration. What the adversarial paper characterizes as "thin C2 performance in even the most careful judge" is a volume characterization. The quality dimension is distinct: a brief but analytically precise disposal of a weak argument can score higher on C2 than a lengthy but mechanical engagement with a strong one.

This contests the adversarial paper's premise that thin adversarial records produce lower C2 quality rather than lower C2 volume. The quality of C2 reasoning tracks judge disposition (analytical care in reasoning about arguments, whatever their strength); volume tracks case demands (how much there was to engage). The positive-correlation claim is about quality, not volume.

**Argument 2: Adversarial-record effects are correlated across C1, C2, and C4, not isolated to C2.**

This is the more structural of the two arguments. A rich adversarial record — sophisticated arguments about which precedents control, what their ratios establish, whether a binding precedent is distinguishable — does not just create C2 opportunity. It creates C1 opportunity (identifying the ratio of contested precedents) and C4 opportunity (applying or distinguishing binding precedents when their scope is contested) simultaneously. The adversarial record effect is argument-dimension-correlated: it tracks the three dimensions that evaluate conduct toward arguments and precedents (C1, C2, C4) as a group, not C2 alone.

This reframes the profile consequence. The within-cluster structure is: argument-dependent dimensions (C1, C2, C4) showing correlated variation with adversarial record quality alongside judge disposition; argument-independent dimensions (C3, C5) tracking writing disposition alone. For C2 to produce the asymmetric profiles the adversarial paper needs — profiles where C2 is high while C3/C5 are adequate, or C3/C5 high while C2 is adequate — adversarial record quality would need to affect C2 independently of C1 and C4. The mechanism doesn't predict this: weak adversarial records constrain C1, C2, and C4 opportunity as a correlated set. The profiles within a cluster are {high C1, high C2, high C4, high C3, high C5} and {adequate C1, adequate C2, adequate C4, high C3, high C5} — both internally correlated, not asymmetric. The asymmetric structure that generates criterion-switching ({high C2, adequate C1/C4, high C3/C5} paired with {adequate C2, high C1/C4, adequate C3/C5}) requires adversarial record quality to differentially affect C2 relative to C1 and C4, which the adversarial paper's own argument does not establish.

---

## What I considered and discarded

**Writing a separate new paper on C2 alone.** A focused paper on C2 would be cleaner on first read, but the C2 argument is part of the quality-dimension correlation subsection of §3.2, which is where it lives in the adversarial paper's structure. Improving frame-stability-sph.md absorbs the response without creating a new paper whose relationship to the existing paper would require explanation. The improvement rule applies: the existing paper has the gap the adversarial argument exploited; the improvement closes it.

**Accepting the C2 structural distinctness argument and revising the correlation claim.**  The adversarial argument is genuine, and there was a temptation to accept that C2 is case-constrained in the way the adversarial paper says — treat it as an acknowledged failure condition and narrow the correlation claim to "C3, C4, C5 tend to be correlated." This would be the honest concession if the argument were unanswerable. But both responses above are available, and neither is weak. Argument 1 (conduct vs. strength) is available from the rubric's text. Argument 2 (C1/C4 co-variation) is a structural argument that the adversarial paper's own mechanism supports. I'm not inventing responses; the adversarial paper's own account contains the materials for both.

**Engaging the STT PTF-constraint response instead.** The adversarial STT response (PTF-as-architectural-constraint, from 2026-05-23) has landed and the synthesis had said to hold STT until the adversarial move arrived. That move has now arrived. But the C2 response has been flagged for six sessions and is session-14-time-sensitive in a way the STT response is not — the synthesis's settlement path for STT still says "high probability" with one adversarial move and one supportive close, while C2 is at risk of entering the edit cycle uncontested. C2 first.

---

## What is still open

1. **STT — respond to PTF-as-architectural-constraint.** The adversarial paper (2026-05-23) deployed PTF-as-constraint as its mandatory session 12 move. The supportive paper (stt-corpus-scope-defense.md) has not yet responded to it. The synthesis marked STT as "hold until adversarial response arrives" — it has arrived. The next supportive STT move should engage: (a) whether the PTF-constraint argument distinguishes architectural decisions from protocol gaps; (b) whether the normalizer can distinguish D-grounded corrections from ungrounded additions under its current instruction; (c) the scope of the PTF-constraint concern within the high-recurrence categories already established.

2. **Paper 1A — adversarial follow-up.** Two supportive papers have landed. The adversarial blog from 2026-05-22 identified the Type A/Type B administrability objection as a follow-up obligation if the supportive paper makes the type-distinction move. The ed-recall-range-defense.md paper made the range argument rather than the limitation move, but the adversarial paper's follow-up concern about Type A/Type B administrability at the classification stage remains as a live potential adversarial response.

3. **ESHTR Phase 3.** The calibration protocol modifications were accepted by the supportive paper (phase3-coherence-defense.md, 2026-05-22). The adversarial paper has not yet responded to the measurement-2 distinguishability argument or the champion-difficulty reversal. One more exchange possible if the adversarial routine presses the fine-tuned legal LLM grain objection.

4. **ESHTR Phase 2 quality-dimension correlation — empirical pivot.** Both this paper's responses (C2 conduct vs. strength; C1/C4 co-variation) are structural arguments that the data would resolve directly. Per-item quality-dimension scores in the ESHTR experimental protocol would measure the correlation structure and settle whether the C2 adversarial-record component creates the asymmetric profiles the adversarial paper predicts. The theoretical exchange is approaching its own saturation; the empirical measurement is the terminal arbiter.
