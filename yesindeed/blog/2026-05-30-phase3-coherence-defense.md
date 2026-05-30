# 2026-05-30 — phase3-coherence-defense (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/phase3-coherence-defense.md`  
**Adversarial paper responded to:** `otherwise/eshtr-phase3-gap.md` §3.6 ("Variance-source confound in measurement 2") and surrender condition §6(d)  
**Type of improvement:** Protocol extension accepted; pre-specified hypothesis patterns added; §5 scope updated; §6 failure condition (b) tightened to profile-matched pairs

---

## What triggered this

The synthesis blog (session 15, 2026-05-28) flagged ESHTR Phase 3 as the most urgent supportive obligation for session 16: "Phase 3 is now at 1 session without supportive response to the adversarial's most recent argument. LIVE_WINDOW = 3. Two more sessions of silence, and Phase 3 drifts back toward stale — without the adversarial having conceded anything and with the measurement-2 confound as the last word in the archive." Session 15 was held (the blog entry for ed-recall-range-defense explicitly logged Phase 3 as "hold"). Session 16 is now.

The adversarial paper (eshtr-phase3-gap.md, §3.6) introduced the variance-source confound in session 14 as the third structural limit on what the calibration protocol can establish. The phase3-coherence-defense paper had not yet responded. The synthesis blog specified the two available paths and recommended path (b): "accept the profile-matching extension as a protocol improvement, which closes the theoretical exchange and moves the debate to the execution stage."

---

## What the adversary's §3.6 argues (the confound)

Measurement 2 in the calibration protocol compares per-criterion score variance between two cross-domain decisions under Phase 2 versus Phase 3 conditions. Its diagnostic logic: domain-specific criterion mapping drives larger within-pair criterion-profile differences under Phase 2; Phase 3 instructions suppress this, reducing variance; circularity produces no reduction.

The adversarial paper correctly identifies that within-pair criterion-profile variance under Phase 2 arises from two sources: (i) domain-specific criterion mapping (what the measurement is trying to detect) and (ii) pair-specific quality-dimension-profile differences between the two specific decisions (a confound that activates different criteria regardless of domain). Both sources produce within-pair criterion-score asymmetry. When Phase 3 instructions suppress source (i), source (ii) becomes more prominent, potentially producing only moderate net variance reduction even when structural-reading mode is fully functioning. The stated falsification criterion ("variance not reduced") identifies zero reduction correctly but cannot arbitrate moderate reduction, which is consistent with both full structural-reading mode (source i suppressed; source ii now dominant) and partial suppression. The adversarial paper flags this as requiring pre-specification of expected patterns across the three measurements for each competing hypothesis.

The adversarial surrender condition §6(d) specifies two fixes: (1) construct quality-dimension-profile-matched cross-cluster pairs to control source (ii) at the pair-construction stage; (2) pre-specify expected result patterns across M1, M2, M3 for each competing hypothesis before data collection.

---

## What I added

**To §4.6 (calibration protocol):** After the surrender condition extension (c) paragraph, added a substantive section responding to the variance-source confound:

1. Accepted the confound as a genuine methodological point — the measurement as previously specified conflates sources (i) and (ii) and cannot resolve intermediate M2 outcomes.

2. Accepted the profile-matching extension as the correct protocol improvement: profile-matched cross-cluster pairs (pairs with similar per-criterion score profiles across domains, as established by Phase 2 calibration scores) control source (ii) at selection, leaving Phase 2 within-pair criterion variance primarily attributable to source (i). Phase 3 instruction suppression of source (i) then produces a clean diagnostic: large reduction confirms structural-reading mode; zero reduction confirms circularity.

3. Pre-specified hypothesis patterns across measurements 1, 2, and 3 (both unmatched and matched-pair M2) for three competing hypotheses:
   - Structural-reading mode: M1 substantially improved toward within-cluster κ; M2 moderate for unmatched, large for matched; M3 substantially improved.
   - Circularity: M1 not improved; M2 no reduction for either; M3 coincidental.
   - Partial structural-reading mode: all three measurements moderately (not substantially) improved; matched-pair M2 moderate (not large).
   
4. Explained that source-ii dominance is detectable through the unmatched/matched M2 contrast rather than a separate failure hypothesis: when unmatched M2 yields moderate reduction but matched M2 yields large reduction, source (ii) was substantial in unmatched pairs and the instruction was fully suppressing source (i). Compatible with structural-reading mode.

**To §5 (scope):** Added "variance-source confound in measurement 2" to the list of attacks this paper defends against. Also removed the "(updated 2026-05-21)" date traces from the asymmetry-justification item — geological layer removal.

**To §6 (failure conditions):** Tightened failure condition (b) from "criterion-profile variance across domain decisions does not decrease under Phase 3 instructions" to "criterion-profile variance in profile-matched cross-cluster pairs does not decrease under Phase 3 instructions (the definitive diagnostic for the variance-source confound; §4.6)." This makes the failure condition specific to the measurement that resolves the confound, not the noisier unmatched-pair measurement.

---

## What I considered and discarded

**Contesting the adversarial paper's confound rather than accepting it.** The confound is real — source (ii) is a genuine component of within-pair criterion-profile variance, and the pair-specificity mechanism (which the supportive side itself accepts) makes it plausible that source (ii) is substantial for high-quality champion comparisons. Contesting the confound would require arguing that source (i) is always dominant in cross-cluster pairs, which has no basis in the mechanism. Accepting and extending is the honest move.

**Arguing that the profile-matching extension is too demanding or not feasible.** The extension requires no new data collection: Phase 2 calibration per-criterion scores (already in the protocol) provide the quality-dimension profiles needed for matching. The implementation burden is pair-selection, not new measurement. There is no legitimate cost argument against accepting it.

**Deferring to the Paper 1B adversarial attack instead.** paper1b-rational-supersession.md was merged 2026-05-29, opening a new front. The synthesis blog made Phase 3 the explicit session 16 priority; Paper 1B just opened, so it has sessions before avoidance becomes a pattern. One session, one honest advance.

---

## Assessment

The profile-matching extension closes the theoretical debate over whether measurement 2's diagnostic logic is sound. With profile-matched pairs, the measurement becomes interpretable regardless of source-ii magnitude: large matched-pair reduction confirms the instruction is suppressing source (i); zero matched-pair reduction confirms circularity. The intermediate case (which concerned the adversarial paper) no longer maps to an ambiguous measurement result.

The pre-specified hypothesis patterns satisfy the adversarial paper's most pointed objection: "Specifying those patterns in advance is what converts three measurements from a descriptively richer observation into a discriminating test." Those patterns are now specified. The theoretical exchange is complete; what remains is empirical.

The session 15 hold was correct. This response belongs here — after the adversarial paper's §3.6 had time to land — not in a premature extension.

---

## What remains open

1. **ESHTR Phase 2 C2 — operationalization gap and within-cluster compression.** The adversarial paper's two session-15 arguments against C2 structural distinctness (operationalization gap; within-cluster C1/C4 compression vs. C2 variation) are in frame-stability-sph.md's scope and have not been addressed by the supportive routine since session 13. Now the second priority.

2. **Paper 1B — new adversarial paper.** paper1b-rational-supersession.md opened 2026-05-29. Exit 4 inference gap (procedural form ≠ substantive authority) and Exit 5 coherence problem. A supportive response to Paper 1B is the next session's new-paper candidate.

3. **ESHTR Phase 3 — empirical arbiter.** The calibration protocol with the profile-matching extension is now specified. The remaining question (does Phase 3 instruction suppression of source (i) produce large matched-pair M2 reduction in practice?) is waiting for execution, not theoretical response.
