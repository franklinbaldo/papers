# 2026-05-23 — stt-retrieval-hallucination (improvement)

**Session type:** Improvement to existing adversarial paper  
**Paper improved:** `otherwise/stt-retrieval-hallucination.md`  
**Target:** `semantic_tokenization_transformers (1).md` (STT)  
**Supportive paper engaged:** `yesindeed/stt-corpus-scope-defense.md` (updated 2026-05-21)  
**Type of improvement:** Responding to the recurrence counter; deploying PTF-as-architectural-constraint as a new §3.5; updating §4 within-corpus reply; adding surrender condition 5

---

## What triggered this

The synthesis session 10 blog flagged two things as mandatory adversarial moves on the STT front:

1. **Engage the recurrence counter**: The supportive paper (2026-05-21 update) responded to the type/token argument by accepting the distinction as structurally correct, then contesting its scope in specialized single-jurisdiction legal corpora. Three categories of high-recurrence content: institutional parties, standardized amounts, súmula language. The adversarial paper had not responded to this.

2. **PTF-as-architectural-constraint (three sessions unexecuted)**: The "DO NOT add new information or facts" normalizer instruction prevents the normalizer from correcting F2 errors even when the correct information is available from the input document. The synthesis flagged this as the strongest available undeployed argument. It appeared in §3.3 step 5 nested inside the compound failure scenario for novel inputs, but had never been deployed as a standalone architectural argument independent of the cold-start case.

The ESHTR Phase 3 debate has a new supportive response (merged 2026-05-22) that engaged the calibration critiques. The synthesis said Phase 3 is approaching empirical impasse and the supportive response accepts the surrender condition extensions — so the Phase 3 front is theoretically saturating. The STT front has a clean move available and an unengaged supportive advance. This session goes to STT.

---

## What changed

**§2 (Faithful reconstruction):** Changed "three responses" to "four responses" and added the recurrence counter as the fourth defense. The fourth defense is stated faithfully at its strongest: three specific, genuine high-recurrence categories in single-jurisdiction specialized corpora; residual gap acknowledged as real and PTF-detectable; scope described as corpus-dependent and narrower than the universal formulation.

**§3.5 (new section — The Normalizer Constraint Structurally Forecloses F2 Correction):** This is the main new attack. The argument:
- The "DO NOT add new information or facts" instruction is an architectural decision defining the normalizer's role as surface-polishing, not content-generating
- This instruction structurally forecloses F2 correction: when the proto-text contains a wrong medoid (wrong multiplier, inverted party role, misapplied súmula), the normalizer cannot insert the correct value from D
- The supportive paper's §3.4 says "the blind spot is in the evaluation layer, not in the design layer" — this is wrong on the design-layer half
- PTF testing would detect F2 failures but cannot correct them — detection ≠ correction
- The design choice is internally consistent: permitting D-grounded correction would reintroduce F1 risk at the normalization step
- The argument is independent of cold-start: it applies to any F2 failure, including those in high-recurrence categories

**§4 (within-corpus reply updated):** Added five paragraphs after the existing type/token analysis:
- Accepted the three recurrence categories as genuine (no straw man)
- Pressed the proportion question on operative content: holding, factual findings, remedy
- Argued that súmulas state principles but not case-specific holdings; institutional parties appear as boilerplate but case-specific acts are unique; salary-minimum multipliers establish scales but case-specific calculations are transaction-specific
- Named the applications where anti-hallucination protection is needed as precisely those where operative content (not boilerplate) matters
- Connected the PTF constraint (§3.5) to the within-corpus recurrence case: high-recurrence categories reduce frequency of F2 errors, not their uncorrectability

**§6 (surrender conditions):** Added condition 5 — normalizer redesigned to permit F2 correction from D, with an explicit mechanism distinguishing F1 prevention from F2 correction and empirical evidence that F1 risk is not reintroduced. Under the current instruction, this path is closed by design.

---

## The argument structure

The two new moves work together:

1. **Recurrence counter response** attacks the scope claim: even granting that three categories of content have high recurrence, the operative content of a legal summary (the specific holding, factual findings, remedy) is predominantly transaction-specific within each of those categories. The holding isn't "the súmula applies" — it's "the súmula applies to this party's specific situation, and here is the determination." The remedy isn't "salary-minimum indexed" — it's "8x salary minimum for this employee's 14 months of employment under these specific violations."

2. **PTF constraint** attacks the corrective architecture: even if the recurrence argument were fully correct (F2 failures are rare for these categories), when F2 failures occur they are uncorrectable by design. The normalizer instruction that prevents generation hallucination also prevents using the input document to fix medoid errors. This converts "rare F2 failures" into "rare but permanent F2 failures." For high-stakes applications, permanent uncorrectable errors are more dangerous than detectable-and-correctable errors.

The two arguments are independent — you could accept one and reject the other — but together they close both the frequency and the corrective response objections to the F2 attack.

---

## What I considered and discarded

**Accepting the scoped version of the claim.** The synthesis identified "Likelihood: moderate-high" for settlement if the adversarial paper accepts the scoped version — "bounded hallucination holds for high-recurrence semantic regions in specialized single-jurisdiction legal corpora; F2 failure scope is corpus-dependent." I considered accepting this, which would settle the STT debate. But the PTF constraint argument shows the scoped version still has a structural problem: even within high-recurrence regions, F2 failures are uncorrectable. Accepting the scope would let a genuine design-level flaw pass without examination. The honest position is to accept the frequency scope (F2 is less common in high-recurrence categories) while pressing the uncorrectability structural argument (when F2 occurs, the architecture cannot correct it).

**Attacking the normalizer's access to D.** The anticipated reply to §3.5 would be: "The normalizer receives D in context; it can distinguish between adding new information (F1 risk) and correcting proto-text errors with D-grounded facts." I considered whether this reply defeats the PTF constraint argument. It doesn't, because: (a) if the normalizer uses D to insert "8x" where the proto-text has "10x," it IS adding new information to the proto-text — the very action the instruction blocks; (b) permitting this would require the instruction to distinguish "D-grounded corrections" from "ungrounded additions," which the current instruction doesn't do; (c) adding this distinction to the instruction would require redesigning the normalizer's behavior, which is surrender condition 5. I addressed this in §4's anticipated reply section (already present as the "prediction-not-guarantee reframe" component) without adding a new section — the existing §4 structure accommodates it.

**Moving to ESHTR Phase 3 response instead.** The supportive Phase 3 paper (2026-05-22) engaged the calibration critiques by: (a) arguing circularity is distinguishable via measurement 2 (criterion-profile variance predicts a different pattern for circularity vs. structural evaluation); (b) reversing the champion-scale difficulty argument (richer structural content is more accessible to structural evaluation, not less). These are interesting responses. But the synthesis says Phase 3 is approaching empirical impasse — both sides have stated their positions, the calibration protocol extensions are accepted, the debate awaits the experiment. The STT move is more productive this session.

**Attacking Paper 1B.** Paper 1B is next after 1A in the portfolio obligation. But Paper 1A was just opened (2026-05-22) and Paper 1B would require fresh analysis of the "five exits" framework. The STT move is more urgent (flagged for three sessions) and more tractable (the argument is clear).

---

## What is still open

1. **ESHTR Phase 3 response to supportive calibration counter.** The supportive paper's measurement-2 distinguishability argument (circularity predicts unchanged criterion profiles; structural evaluation predicts reduced variance) and the champion-difficulty reversal (richer content → more accessible, not less) are live and unaddressed. The synthesis says to respond "precisely to whatever the supportive paper produces." This is the next ESHTR Phase 3 move. Available counter on the circularity distinguishability: the criterion-profile variance test assumes that criterion-switching bias produces *consistent* criterion-profile patterns (the same bias in the same direction for the same pair types) — if criterion-switching is pair-context-dependent and variable (as the Phase 2 attack claims), then variance patterns may be noisy, making the "distinguishable prediction" harder to operationalize. Available counter on champion difficulty: the argument that richer structural content is more accessible assumes Phase 3's structural reading mode actually activates — but this is exactly what the adversarial paper contests (method/content inseparability for champion decisions).

2. **STT — anticipated reply to §3.5 (normalizer access to D).** If the supportive paper argues the normalizer can distinguish D-grounded corrections from ungrounded additions, and can insert "8x" from D without general F1 risk, the PTF constraint argument weakens. My response: the distinction requires redesigning the normalizer instruction (surrender condition 5), which is a design change, not a reinterpretation of the current instruction. The current instruction is absolute; the distinction the reply needs is not present.

3. **Paper 1B (five exits thesis).** Next portfolio obligation. Still unengaged after eleven sessions.

4. **ESHTR Phase 2 — C2 structural distinctness.** The synthesis has flagged this for five consecutive sessions without a supportive response. If the edit cycle arrives (session 14) without a supportive response, this becomes an uncontested point and should be absorbed into the main paper as an acknowledged limitation.
