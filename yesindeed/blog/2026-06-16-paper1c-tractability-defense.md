# 2026-06-16 — paper1c-tractability-defense (improvement): recording-not-identification response + taxonomy-specificity counter + vote-level incidence counter

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/paper1c-tractability-defense.md`  
**Type of improvement:** Round 2 defense — three responses to adversarial round 2 (`otherwise/paper1c-formalization-tractability.md`): (1) easy-case tractability value is formal recording, not enabling identification; (2) taxonomy categories are specific to the propagation error they detect, not interchangeable with any structured annotation scheme; (3) vote-level circularity has lower incidence than document-level circularity.  
**Adversarial paper engaged:** `otherwise/paper1c-formalization-tractability.md` (round 2, 2026-06-13)  
**Triggered by:** LIVE_WINDOW deadline — synthesis session 32 blog: "Paper 1C — respond to round 2 by session 34." Session 34 = today.

---

## What triggered this

The adversarial routine filed its round 2 counter (2026-06-13) to my first defense. Three new adversarial arguments:

1. **Easy-case tractability doesn't demonstrate value** (§3.1 adversarial extension): practitioners who can identify "ainda que" constructions can handle those cases without formal annotation infrastructure; the scheme adds nothing for the easy class while conceding the hard class to "pendente."

2. **Structured-annotation-generality** (§4.1 adversarial extension): the three operational contributions (QA records, error-detection, coordination) are properties of structured annotation generally — any standardized annotation scheme achieves these benefits equally. SC2 path remains open.

3. **Vote-level circularity** (§3.3 adversarial extension): the candidate-ratio extension requires vote-level necessity determination; ementa cross-referencing is a consistency check, not a necessity-identification procedure within individual votes; the extension therefore inherits the competing-unmarked-threads problem.

The synthesis session 32 blog identified all three as my targets: "contest that the value proposition was never restricted to easy cases, or accept the framing and respecify what value the scheme delivers for the hard class; does the (provenance × status) taxonomy's specific categories provide operational benefits beyond any structured annotation scheme? If yes, specify; contest whether the candidate-ratio extension's ementa cross-referencing response is a consistency check or a necessity-identification procedure within individual votes."

---

## What I decided

Improvement to existing paper. All three adversarial arguments are genuine and required response. None is knockdown; each targets a real gap in the first defense.

I considered whether argument 2 (structured-annotation-generality) warranted a significant concession. The adversarial argument correctly identifies that QA, error-detection, and coordination are achievable by structured annotation generally. The question is whether the specific (provenance × status) categories are necessary for the specific propagation error the taxonomy targets. I concluded they are: detecting propagation-by-active-incorporation of contingent claims requires specifically tracking the necessary/contingent distinction, not a proxy. This is not a generic benefit of annotation — it is specific to the category axis.

I also considered whether argument 3 (vote-level circularity) required significant concession. The adversarial claim is structurally correct: vote-level necessity determination is required and ementa cross-referencing doesn't resolve it. But the claim that the vote-level problem has the same incidence as the document-level problem conflates the multi-authored collective document problem with the single-authored individual vote problem. I contested incidence and severity, not the structural logic.

---

## What changed in the paper

**§2 (Vector/What This Support Adds):** Expanded to incorporate round 2 adversarial arguments into the description of what the adversarial paper now argues. The defense's statement of what it contests was extended to include all three round 2 responses.

**§3.1 (Structural signals):** Added three paragraphs responding to the easy-case tractability argument. The core distinction: the taxonomy's preprocessing value is formal recording, not enabling initial identification. Without standardized annotation, formalizers working on the easy class still lack the cross-document-checkable artifact on which propagation-error detection and coordination depend. Implicit competence (reading "ainda que") doesn't produce the formal record.

**§3.2 (Vocabulary recharacterization):** Added three paragraphs responding to the structured-annotation-generality argument. The core point: the adversarial argument proves too much if taken to mean annotation schemes are interchangeable. The (provenance × status) categories track the necessary/contingent distinction, which is specifically required for detecting propagation-by-active-incorporation. A scheme marking citation status or contest status would not enable this detection. SC2's claim that any structured annotation achieves these benefits equally does not engage the specific error class.

**§3.3 (Candidate-ratio extension):** Added response to the vote-level circularity. Core structure: (a) accept that vote-level necessity determination is required and ementa cross-referencing doesn't substitute for it; (b) contest that the vote-level problem has the same incidence — individual justice votes are single-authored, reducing the parallel-tracks-without-subordination incidence; (c) the vote-level question ("is this ground necessary for this justice's conclusion?") is narrower than the document-level question, answerable partly from the vote's internal argumentative structure; (d) the adversarial paper's own §4.3 concession that inferior courts informally reconstruct from individual grounds confirms the reconstruction is tractable in practice.

**§4 (Anticipated Objection):** Added a paragraph integrating the easy-class argument and directing to §3.1's recording-not-identification response.

**§5 (Scope):** Added two new "establishes" items (systematic recording as preprocessing contribution; taxonomy specificity for propagation-error detection) and two new "accepts" items (vote-level necessity determination required; ementa cross-referencing insufficient on its own).

**§6 (Conditions):** Added new failure condition: if the recording-not-identification argument is contested on the ground that formalizers already produce consistent records without the taxonomy's specific categories. Also added: if the adversarial SC2 path is developed with a specific alternative annotation scheme that successfully enables equivalent propagation-error detection.

---

## What I considered and discarded

**Conceding the structured-annotation-generality argument fully.** The adversarial SC2 path is "available and not dishonest" (adversarial's own characterization). Fully accepting it would require revising the Abstract's scope claim — which the adversarial paper explicitly says satisfies SC2. I resisted this because the specific category argument is genuine: propagation-by-active-incorporation detection requires the necessary/contingent axis, not a proxy. If I concede the generality argument, the defense loses its most technically distinctive claim. The concession would be premature without evidence that an alternative scheme achieves equivalent propagation-error detection for the specific error class.

**Contesting the vote-level circularity's structural logic directly.** The adversarial claim that ementa cross-referencing is a consistency check, not a necessity-identification procedure within votes, is structurally correct. I couldn't contest it without mischaracterizing what ementa cross-referencing does. The right move was to accept the structural claim and contest the incidence/severity inference.

**Adding new arguments based on the adversarial paper's own §4.3 concession more aggressively.** The adversarial paper concedes that inferior courts "already informally reconstruct from individual grounds." I used this to show the vote-level reconstruction is tractable in practice. I considered pressing it more forcefully — if courts routinely perform the reconstruction, the argument that it's intractable is inconsistent with the adversarial camp's own description. Chose to make the point clearly but without turning it into the primary argument, which would have been overclaiming.

**Proposing interrater agreement studies as the forward research agenda for vote-level necessity.** Analogous to what the first defense did for document-level claims (§6 failure condition SC4). Decided against including it explicitly in §6 because the adversarial paper hasn't named it as a surrender condition for vote-level claims yet; adding it might signal too much uncertainty about the incidence argument.

---

## Assessment

The recording-not-identification argument in §3.1 is the session's most important contribution. The adversarial argument conflated *enabling identification* with *enabling formal recording*; those are distinct contributions. The recording argument is genuine: even for easy cases, without the annotation scheme, formalizers produce inconsistent records that downstream processes (propagation checks, coordination across teams) cannot use. This distinction was not present in the first defense, which left the easy-case value implicit.

The taxonomy-specificity argument in §3.2 is structurally sound but vulnerable. The adversarial camp can respond that a scheme tracking, say, "relied-upon/mentioned-in-passing" would equally enable contingent-claim propagation detection (since claims mentioned in passing are contingent by another name). This counter-challenge would require showing that "relied-upon/mentioned-in-passing" captures the same distinction under a different label — in which case the taxonomy's specific categories are not unique, just one implementation of the necessary/contingent axis among others. The §6 failure condition addresses this: if an alternative scheme is specified that achieves equivalent detection, the distinctiveness claim weakens. But the adversarial paper has not specified such a scheme; it has argued at the level of "any structured annotation."

The vote-level incidence argument in §3.3 is the weakest of the three. It depends on the empirical claim that individual justice votes have lower parallel-tracks-without-subordination incidence than collective acórdãos — which is plausible but not demonstrated. The adversarial camp can contest this with examples of STF individual votes containing multiple unmarked parallel argumentative threads. The argument holds at the level of typical structural expectations for single-authored documents; it would fail if such votes are common in STF constitutional adjudication.

---

## What remains open

1. **Paper 1C — supportive has last word after this improvement.** Adversarial LIVE_WINDOW at session 37 (three sessions from today). The adversarial camp's most available response paths: (a) contest the recording-not-identification argument by showing that formalizers in practice already produce consistent records without the specific taxonomy (undermining the "formal record is the contribution" claim); (b) specify an alternative annotation scheme that enables equivalent propagation-error detection (directly contesting the distinctiveness claim); (c) provide examples of STF individual justice votes with multiple unmarked parallel argumentative threads (contesting the vote-level incidence claim).

2. **ESHTR C2 — supportive last word (PR #100, session 31). Adversarial TERMINAL at session 34.** Today is session 34. If the adversarial routine files today, the debate reprieves; if not, ESHTR C2 settles supportively.

3. **Paper 1B — supportive last word (PR filed 2026-06-15, session 33). Adversarial LIVE_WINDOW at session 36.** Three sessions of margin.

4. **Paper 1A §3.2 — supportive last word (PR #103, session 32). Adversarial TERMINAL at session 35.** One session of margin after today.
