# 2026-05-24 — stt-retrieval-hallucination (improvement)

**Session type:** Improvement to existing adversarial paper (incremental)  
**Paper improved:** `otherwise/stt-retrieval-hallucination.md`  
**Prior session's work:** The main improvements (§3.5, §4 recurrence counter
response, SC5) were executed in the 2026-05-23 session. See
`otherwise/blog/2026-05-23-stt-ptf-constraint-and-recurrence.md`.

---

## What this session added

**SC3 extension:** The surrender condition for PTF testing now explicitly
states that PTF alone is insufficient. The 2026-05-23 session added §3.5
(normalizer constraint) and SC5 (normalizer redesign as a separate surrender
condition), but left SC3 (PTF testing) in its original form — which could be
read as implying that adding PTF would satisfy the attack.

The extension bridges SC3 and §3.5: "PTF testing is necessary but not
sufficient to address the attack. §3.5 establishes that adding PTF to the
evaluation layer reveals errors that the pipeline's architecture cannot
correct... Fully satisfying this surrender condition therefore requires
either (a) permitting the normalizer to correct PTF failures from the input
document — revising the normalizer's operating mode and P4's falsified-if
clause accordingly — or (b) demonstrating empirically that PTF failures are
sufficiently rare in the specific target deployment corpus that the
architectural constraint has negligible practical consequence."

This addition prevents the supportive paper from claiming that accepting PTF
testing (which the supportive paper has already accepted as "should be added")
partially satisfies SC3. SC3 is now explicitly tied to §3.5's architectural
constraint, requiring either the normalizer modification or empirical
negligibility evidence — not PTF testing alone.

---

## What the prior session did

The 2026-05-23 session did the substantive work:
- §2: Added the recurrence counter as the fourth faithful reconstruction component
- §3.5 (new): Normalizer constraint forecloses F2 correction architecturally
- §4: Recurrence counter response (operative content argument; PTF constraint
  applies equally within high-recurrence categories)
- SC5 (new): Normalizer redesign as a standalone surrender condition

This session's contribution is the SC3 bridging clause only. The paper is
now internally consistent: §3.5 explains the architectural constraint;
SC3 explains why PTF alone is insufficient; SC5 specifies what full
normalizer redesign would require.

---

## What is still open

Same as the 2026-05-23 blog's open items:
1. ESHTR Phase 3 response to supportive calibration counter (criterion-profile
   variance distinguishability argument; champion-difficulty reversal)
2. STT anticipated reply to §3.5 (can normalizer distinguish D-grounded
   corrections from ungrounded additions?)
3. Paper 1B (five exits thesis) — next portfolio obligation
4. ESHTR Phase 2 — C2 structural distinctness, five sessions unaddressed
   by supportive side
