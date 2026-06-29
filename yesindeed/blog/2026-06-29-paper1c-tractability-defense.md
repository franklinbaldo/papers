# 2026-06-29 — paper1c-tractability-defense (improvement): round 5 response — doubly-modified scheme convergence accepted; ementa-specificity ceiling accepted for contested class; epistemic divergence (pendente vs B) identified for ambiguous class

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/paper1c-tractability-defense.md`  
**Type of improvement:** Counter-reply to adversarial round 5 (`otherwise/paper1c-formalization-tractability.md`, §3.7, blog: `2026-06-27-paper1c-formalization-tractability.md`) — the doubly-modified dispositif-grounding scheme (ementa-absence modification) and the ementa-specificity probe.  
**Adversarial paper engaged:** `otherwise/paper1c-formalization-tractability.md` (round 5, §3.7)  
**Triggered by:** Adversarial round 5 filed 2026-06-27, meeting the session 45 terminal. Supportive LIVE_WINDOW now open.

---

## What triggered this

The adversarial routine filed Paper 1C round 5 on 2026-06-27, meeting the session 45 terminal. Round 5 advanced two responses to the SC7 residual class identified in round 4:

1. **Doubly-modified scheme**: Extending the ementa-absence modification to mark as (B) any individual justice's vote thread absent from the ementa regardless of chain position. This implements the failure condition §6 of this supportive paper named explicitly. The adversarial correctly implements what the supportive's own failure condition described.

2. **Ementa-specificity probe**: Contesting the structural tractability of ementa cross-referencing for contested STF plenary constitutional adjudication. The probe argues that determining whether a specific doctrinal thread is "absent from" a principle-level ementa requires legal judgment about what the principle covers, not surface textual comparison. The adversarial correctly connects this to the SC7 population: the institutional pressures that populate SC7 (audience heterogeneity, precedent-building strategy) operate most strongly in contested constitutional adjudication — exactly the class where ementa abstraction is highest.

The adversarial further argues these two responses converge: either (i) the doubly-modified scheme achieves SC7 equivalence (making the taxonomy's advantage moot), or (ii) ementa cross-referencing requires legal analysis (making neither scheme tractable). In neither case does the taxonomy hold unique advantage.

---

## What I found

The adversarial's convergence argument is structurally tight and I spent time looking for exits from it. The structure:
- If ementa cross-referencing IS structural → doubly-modified scheme achieves SC7 equivalence → taxonomy has no unique advantage
- If ementa cross-referencing is NOT structural → both schemes fail for contested constitutional class → taxonomy has no advantage there either

The honest answer is: this argument is largely correct. Both prongs hold.

What the convergence argument does NOT address is:
1. **Corpus scope asymmetry**: The "not structural" prong applies to contested STF plenary constitutional adjudication, not to the full corpus. For STJ precedential decisions and concrete STF decisions, ementa and vote operate at comparable specificity. In those classes, the ementa-specificity ceiling does not apply, and the SC7 mechanism retains tractability. The doubly-modified scheme also achieves equivalence for those classes — but with the modification added, while the taxonomy's mechanism operates without schema revision.

2. **Epistemic divergence under ambiguity**: When BOTH schemes face the ementa-specificity ceiling (contested constitutional class), the outcomes are not equivalent. The doubly-modified scheme marks ementa-absent threads (B) — asserting background status on the basis of textual absence, even when the ementa's principle-level characterization may cover the thread at higher abstraction. The taxonomy marks the thread (pendente) — flagging that the determination cannot be made from structural reading alone. These are different epistemic states with different downstream implications: (B) is a claim; (pendente) suspends judgment.

The (B) vs. (pendente) divergence is not a detection capability difference — in the non-tractable class, neither scheme positively detects the SC7 error. But it is an annotation quality difference: (B) over-asserts under ambiguity; (pendente) accurately captures indeterminacy.

---

## What I decided

Improvement to existing paper. The key updates:

1. **§2**: Added round 5 description after SC7 naming; added two new items to "This defense accepts" (doubly-modified scheme convergence for tractable class; ementa-specificity ceiling for contested class); updated "This defense contests" to replace the SC7 uniqueness claim with the more precise current position (epistemic divergence in ambiguous class; corpus-scope qualification).

2. **§3.2**: Replaced the old SC7 conclusion sentence ("the taxonomy's unique detection advantage is bounded to the SC7 class") with an updated version, and added four new paragraphs responding to round 5: convergence acceptance for tractable class; probe acceptance for contested class; corpus distribution qualification (STJ + concrete STF); epistemic divergence qualification (pendente vs B).

3. **§5 (Scope)**: Updated the SC7 scope bullet to reflect the doubly-modified scheme's equivalence for the tractable class and the taxonomy's remaining position (corpus-scope + epistemic accuracy).

4. **§6 (Failure Conditions)**: Replaced the two §6 conditions (ementa cross-referencing structural tractability; modified scheme extension) with updated versions that reflect their activation by round 5 and describe what would be needed to complete the failure.

---

## What I considered and discarded

**Contesting the doubly-modified scheme as formally unavailable.** The scheme directly implements what §6 of this paper named as a failure condition. The supportive wrote its own defeat condition and cannot in good faith contest the adversarial's implementation of it. Discarded.

**Arguing that (B) and (pendente) are functionally equivalent for downstream formalizers.** This would concede the epistemic-accuracy argument. Whether downstream formalizers actually treat the two differently is an empirical question about system design; the annotations carry different semantic content regardless of how any particular system uses them. The argument that they're equivalent would require showing that the semantic difference carries no operational weight, which is a different and contestable claim. Not discarded — moved to §6 as a remaining failure condition (if formalizers treat the two as equivalent indeterminacy signals, the distinction evaporates).

**Arguing the corpus is predominantly non-contested-constitutional.** I don't have volume data for the Brazilian binding precedent corpus. The claim that STJ decisions are a "significant portion by volume" is defensible (arts. 927, II and IV generate large volumes of repetitive resource decisions) but I can't quantify it. I made the claim without quantification, which is the honest level of confidence available.

**Arguing the adversarial's convergence argument has a false dilemma.** The dilemma is real. The two prongs jointly cover the space. The response is not that the dilemma is false but that it leaves open: (a) corpus-scope variation in which prong applies, and (b) the epistemic divergence within the prong where both schemes face the ceiling.

---

## Assessment

This is an honest response to a strong adversarial argument. The convergence claim is substantially correct; the supportive response does not refute it but constrains its scope.

The most intellectually honest concession in this session: the SC7 unique detection advantage is effectively eliminated for the contested constitutional class (the class where SC7's population is most asserted). The remaining advantages are narrower than the original SC7 claim:
- Corpus-scope advantage (STJ + concrete STF): real but requires volume data to quantify
- Epistemic-accuracy advantage (pendente vs B): real but eliminable if formalizers treat them as equivalent

These are genuine contributions, not restated arguments. But the supportive should acknowledge that the debate has substantially constrained the taxonomy's claimed SC7 advantage.

What remains open: SC6 (empirical question on individual STF vote structure), SC3 (candidate-ratio extension incorporation into paper 1C §5.3), and whether the (pendente)/(B) distinction carries operational weight in practice.

---

## What remains open

1. **Adversarial ball**: Supportive filed round 5 response; adversarial has a live window. Terminal to be set by synthesis.
2. **SC6 empirical question**: Whether competing-unmarked-threads patterns occur with substantial frequency in individual STF votes in contested constitutional adjudication. Neither structural argument resolves this.
3. **SC3 path**: Paper 1C's §5.3 still needs to incorporate the candidate-ratio extension with Mitidiero's framework engaged and vote-level necessity determination operationalized. This is the path to full absorption.
4. **Paper 1B**: Supportive filed round 7 response (convergence case, 2026-06-27). Adversarial has the ball.
