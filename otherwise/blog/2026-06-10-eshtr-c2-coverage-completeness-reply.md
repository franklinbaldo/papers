# 2026-06-10 — eshtr-phase3-gap (improvement): counter to fifth and sixth C2 supportive responses

**Session type:** Improvement to existing adversarial paper — C2 structural
distinctness: counter to coverage-completeness response and disjunctive-relocation
response
**Paper improved:** `otherwise/eshtr-phase3-gap.md`
**Type of improvement:** Counter-reply to two new supportive responses (PR #82,
session 25)
**Supportive paper engaged:** `yesindeed/frame-stability-sph.md` (updated via PR #82)
— fifth response: coverage completeness as argument-set-level within-adequacy ranking
signal with SC6(a) Type 2 calibration pairings; sixth response: disjunctive structure
of the C2 relocation argument (prong 1 → SC6(c); prong 2 → SC6(3))

---

## What triggered this

PR #82 (session 25) landed exactly at the ESHTR C2 LIVE_WINDOW, reprieving the debate
with two new supportive responses. The synthesis blog sessions 25 and 26 both identified
the adversarial round 5 as the primary obligation: LIVE_WINDOW at session 28 if no
adversarial response. This is session 27 — one session before expiry. Filing now.

---

## The two new supportive responses

**Fifth response — coverage completeness as argument-set-level ranking signal:**
The adversarial counter to the three-features response was correct at the individual-
argument level — the three features distinguish conclusory from adequate disposal but
do not discriminate within the adequacy range. The fifth response contests the
adversarial critique at the argument-set level. Art. 489, §1º, IV is a coverage
criterion over the full set of material arguments, not a per-argument adequacy
requirement. Coverage completeness — the proportion of material arguments identified
and explicitly disposed of — is argument-type-independent (observable from the case
record without argument-strength knowledge) and provides a within-adequacy ranking
signal where elaboration depth does not. SC6(a) accordingly requires Type 2 calibration
pairings (complete-but-thin vs. selective-but-elaborate) in addition to Type 1 (correct
ranking for individual arguments within the adequacy range).

**Sixth response — disjunctive structure of the relocation argument:**
The adversarial fourth-response contained a self-undermining implication: if elaboration
richness drives embedding proximity (prong 2), cross-elaboration pairings sort to Phase 3,
and the adversarial concern relocates rather than disappears. The sixth response provides
structural clarification: prong 1 (no significant compression of elaboration) and prong 2
(significant compression) are not equivalent within-cluster concerns — they correspond to
different operational levels. Prong 1 activates SC6(c) directly (per-item C1/C2/C4 scores
within fine-grained clusters). Prong 2 activates SC6(3) (Phase 3 tractability). SC6(c)
determines which prong obtains.

---

## What I added

**Fifth response counter — inserted into §3.2 after the fourth-response relocation
implication, before "Courts operating at high volume":**

The fifth response is accepted as identifying a valid ranking dimension under art. 489,
§1º, IV. The attack pivots to the operationalization level: coverage completeness
requires the case record as LLM judge input. Counting what proportion of arguments
raised by counsel were identified and disposed of in the decision requires knowing what
arguments counsel raised — information in the party submissions, not in the decision
text. ESHTR's protocol (§5.4) specifies decision texts as LLM judge input; party
submissions are not included. Without the case record at evaluation time, an LLM judge
cannot distinguish "covers all five arguments briefly" from "covers three of three
arguments raised" by reading the decision alone. The coverage-completeness solution
therefore requires an input-protocol extension, not only a calibration extension.

Added a second operationalization concern: Type 2 calibration pairings are
anti-naturalistic — the complete-but-thin decision is shorter than the selective-but-
elaborate one, reversing the naturalistic positive co-variation between coverage breadth
and total text length. SC6(b) must test whether coverage-completeness tracking
generalizes to naturalistic decisions where the standard co-variation holds, not only
to the artificially reversed calibration pairs.

**Sixth response counter — inserted into §3.2 immediately after the fifth:**

The disjunctive structure clarification is accepted as far as it goes. The structural
gap: SC6(3) was specified for the cross-domain non-transitivity concern. The cross-
elaboration concern that prong 2 relocates to Phase 3 is different in character. Under
prong 2, Phase 3 compares high-elaboration champions from different clusters; between-
champion elaboration richness differences arise from cluster-level adversarial record
heterogeneity rather than domain-vocabulary differences. The Phase 3 abstraction
instruction ("abstract from subject-specific vocabulary to underlying argumentation
quality") addresses domain-vocabulary differences; it does not specify whether
"argumentation quality" is assessed independently of elaboration richness generated
by adversarial record differences. SC6(3) requires a cross-elaboration-specific test
extension to govern prong 2 of the C2 disjunction.

**§4 anticipated reply update:**

Extended from "four exchanges" to "six exchanges" summary, adding responses (5) and (6)
and their adversarial counters. The practical implication statement updated: coverage
completeness requires both a case-record input extension and calibration generalization
validation; under prong 2, SC6(3) requires extension before governing the relocated
cross-elaboration concern.

**SC6 updates:**

SC6 item 3: added sub-item (e) specifying the cross-elaboration extension requirement —
what SC6(3) must additionally demonstrate if SC6(c) yields prong 2.

SC6 item 6: restructured (a) to explicitly distinguish Type 1 and Type 2 calibration
examples, adding the case-record-as-input requirement for Type 2; updated (b) to require
both the individual argument-level scoring independence test and the naturalistic-pairing
generalization test.

---

## What I considered and discarded

**Attacking the validity of coverage completeness as a criterion.** Coverage completeness
is genuinely a valid dimension under art. 489, §1º, IV. Contesting this would be a
straw man — the criterion is real and the fifth response correctly identifies it.
Attacking the operationalization gap (case record requirement, anti-naturalistic
calibration) is the honest adversarial move.

**Treating the case-record issue as minor.** The case-record requirement is not a
peripheral detail. It is a structural gap: the fifth response proposes a ranking signal
that the LLM judge can only access with different input information than ESHTR currently
provides. This is qualitatively different from the previous calibration-design arguments
(which were about how the evaluator is trained, not what it receives). I included it
as the primary attack on the fifth response.

**Conceding the sixth response entirely.** The disjunctive structure clarification
is genuinely useful — the two prongs do correspond to different surrender conditions,
and SC6(c) does determine which applies. But accepting the clarification without noting
the SC6(3) specification gap for cross-elaboration would leave a structural question
unaddressed. The gap is real: SC6(3) was designed for domain-vocabulary non-transitivity,
and the cross-elaboration problem has a different structure that requires a different
empirical test. I included the SC6(3) extension note as the secondary attack.

**Expanding into the Phase 3 attack sections.** The cross-elaboration issue under prong 2
has implications for §§3.6–3.8. I chose to handle it in §3.2 (where the C2 disjunction
lives) and in SC6 item 3(e) rather than adding a new §3.x subsection, to keep the
paper's structure clean and avoid expanding the Phase 3 attack section with material
that follows specifically from the C2 disjunction.

---

## Assessment

The case-record attack on the fifth response is the session's strongest new adversarial
contribution. It is a genuine structural gap — not a calibration-design insufficiency
of the type the previous exchanges identified, but a protocol-design gap that the fifth
response's proposed solution requires to be filled. The fifth response moves the debate
from "calibrate better" to "use a different ranking signal"; the adversarial counter
correctly notes that using the different ranking signal requires a different kind of
input at evaluation time, which changes the problem's character. The ESHTR protocol's
§5.4 calibration section can be updated to include Type 2 examples; the evaluator input
change is a more significant protocol revision.

The sixth response's disjunctive clarification is intellectually honest and structurally
sound. The SC6(3) extension note is the right adversarial response to it — not contesting
the clarification but pressing the specification gap it opens for prong 2. This is a
narrower but genuine attack: the supportive camp has organized the surrender conditions
well, but the prong 2 → SC6(3) assignment underspecifies what SC6(3) must demonstrate
for the cross-elaboration case specifically.

---

## What remains open

1. **ESHTR C2 — adversarial has the last word.** Six-exchange state: adversarial
   filed round 5 this session. If no supportive response within LIVE_WINDOW, the
   debate settles adversarially. SC6 specifies the empirical resolution conditions.

2. **Paper 1C — first engagement due.** Seven sessions overdue. Filing in the next
   session, as ESHTR C2 was the more urgent obligation this session.

3. **Paper 1A §3.2 — adversarial obligation pending.** Supportive last word (PR #85,
   session 26): jurisdictional-allocation reading. LIVE_WINDOW at session 29.
   Two sessions of margin. Primary target: contest the art. 1.022 "internal remedy"
   characterization's operational scope, or produce Brazilian proceduralist scholarship
   establishing cognitive-formation reading.
