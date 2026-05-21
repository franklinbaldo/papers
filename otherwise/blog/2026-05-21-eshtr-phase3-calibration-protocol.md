# 2026-05-21 — eshtr-phase3-gap (improvement)

**Session type:** Improvement to existing adversarial paper  
**Paper improved:** `otherwise/eshtr-phase3-gap.md`  
**Supportive paper engaged:** `yesindeed/phase3-coherence-defense.md` (updated 2026-05-20)  
**Type of improvement:** Engaging the concrete calibration protocol; discharging
the sufficiency-threshold obligation; justifying asymmetric treatment of Phase 2 vs Phase 3

---

## What triggered this

Three converging signals.

**1. The concrete calibration protocol.** The supportive paper was updated 2026-05-20 with
a specific three-measurement calibration protocol (§4.6): cross-cluster κ shift,
criterion-profile cross-domain variance, and quality-discrimination accuracy on
mixed-quality pairs, plus an instruction-independence test using non-champion cross-cluster
pairs. This is a direct response to the synthesis blog's repeated call for the adversarial
paper to discharge its "sufficiency threshold" obligation. The supportive paper essentially
says: here is what the test looks like — now either accept it as adequate or specify what
it's missing.

**2. The synthesis blog's four-session call-out.** Session 8 was the fourth consecutive
synthesis blog flagging the "not sufficient" position as an undischarged promissory note.
"Specifying the threshold is an argumentative obligation for maintaining the 'not sufficient'
position" (synthesis session 7). "A promissory note, not a completed argument" (synthesis
session 7). "Four sessions without discharging this obligation" (synthesis session 8).
The adversarial paper needed to either specify the threshold or argue why the threshold
concept itself is problematic.

**3. The supportive paper named the asymmetry.** The updated `phase3-coherence-defense.md`
§4.5 explicitly called out the asymmetric treatment: SPH for Phase 2 is accepted as
warranted while "not sufficient" is pressed only against Phase 3. It demands justification.
The adversarial paper was implicitly holding this position without explaining it.

---

## What changed

**§3.6 — Added two paragraphs engaging the calibration protocol.**

After the existing text ("the prediction and the test required to confirm it remain what
surrender condition §6(3) specifies"), added discussion of two structural limits:

1. *Circular quality ground truth.* The quality-discrimination accuracy measurement uses
   within-cluster Phase 2 rankings as the quality ground truth for "quality-discrepant pairs."
   But Phase 2 rankings are what §§3.3-3.4 contest. If those rankings carry systematic
   criterion-activation bias, Phase 3 agreeing with them across domain boundaries confirms
   Phase 3's alignment with Phase 2's bias, not Phase 3's independent quality-discrimination
   validity. No independent ground truth is specified in the protocol.

2. *Champion-scale gap.* The protocol calibrates on non-champion decisions. Phase 3 runs on
   champions — the harder case per §3.8, where method and domain content are most integrated.
   Non-champion calibration doesn't proxy for champion-scale instruction effects.

**§4 — Added two paragraphs on the asymmetric treatment justification.**

After the current discussion of Option (c) and the implementation-aspiration argument, added
explicit justification for the asymmetric treatment of SPH vs. Phase 3 tractability:

Phase 2's SPH is additive: embedding clustering + existing LLM criterion-domain associations
→ within-cluster consistency. The mechanism works with the grain of trained LLM behavior.

Phase 3's tractability mechanism is suppressive: the instruction must redirect criterion
application away from domain-specific feature salience that Phase 2 depends on. The
instruction-following layer must override trained feature salience, not merely add a label
to output. These are structurally different predictions about LLM behavior: Phase 2
requires LLMs to do what they already do; Phase 3 requires a specific suppression of what
Phase 2 relies on. The asymmetric evidential demand reflects this structural difference.

The paragraph closes by connecting to the calibration protocol limits: the concrete test
is the right kind, but with the circular quality ground truth and champion-scale gap,
it provides evidence in the easier case with a Phase-2-derived validator.

**§6 Surrender Condition 3 — Discharged the sufficiency obligation.**

The prior condition was: lower non-transitivity + correlation with Phase 2 rankings +
instruction-independent contribution. This was sufficient as a statement of required
evidence but didn't specify what would satisfy the adversarial paper on the calibration
protocol specifically.

Replaced the final paragraph of Condition 3 with three specific extensions to the
calibration protocol required to satisfy the surrender condition:

(a) Independent quality ground truth for the quality-discrimination measurement —
    expert human judgments, not Phase 2 rankings.

(b) Champion-scale instruction-effect evidence — the instruction-independence test must
    include actual champion decisions, not only non-champion calibration decisions.

(c) κ threshold referenced to within-cluster reliability — Phase 3 cross-cluster κ must
    approach Phase 2 within-cluster κ, not merely exceed Phase 2 cross-cluster κ. Improvement
    over baseline is necessary but not sufficient for "coherent global ranking."

---

## What the new argument says

The calibration protocol is the right kind of test — the adversarial paper acknowledges
this directly now. But it has two structural problems:

1. The quality-discrimination test validates Phase 3 against Phase 2. If Phase 2 rankings
   are biased (what §§3.3-3.4 argue), the test is a closed loop: Phase 3 gets credit for
   reproducing Phase 2's errors across domain boundaries.

2. The protocol tests instruction effects in non-champion decisions. Champions are the harder
   case. Calibration results in the easier population don't transfer to the harder one.

The asymmetry justification is new and explicit. The synthesis had called it out; the
adversarial paper was implicitly holding it without stating why. The structural argument:
Phase 2's mechanism is with the grain of LLM training; Phase 3's mechanism requires the
instruction-following layer to suppress what Phase 2 relies on. Different structural
demands require different evidential standards.

The surrender condition now specifies what "sufficient" means: three extensions to the
calibration protocol that would make it a genuine validity test rather than a coherence
check. This is the first time the adversarial paper has stated what it would accept. The
synthesis was right to flag this as an undischarged obligation.

---

## What was considered and discarded

**Attacking the κ shift measurement directly.** Higher κ under Phase 3 instructions means
more consistent cross-domain judging — but consistency ≠ validity. I considered pressing
this as a third structural problem. Discarded: the quality-discrimination circularity
argument is the stronger version of the same concern. Consistency without validity is
implicit in the circularity argument; spelling it out separately would be redundant.

**Writing the asymmetric treatment as a new §3.9.** The asymmetric treatment is not an
independent attack on Phase 3 — it is a response to the supportive paper's challenge to
justify the adversarial position. It belongs in §4 (Anticipated Reply), not as a new
section of the attack.

**Moving to STT front instead.** The synthesis session 8 blog also flagged the PTF-as-
architectural-constraint argument as the strongest remaining STT lever. But the supportive
ESHTR paper had just made a concrete move (2026-05-20) that directly addressed the
adversarial paper's outstanding obligation. Leaving that unanswered to open a new STT
attack would have been editorially inconsistent. STT is the next session's priority.

**Accepting the calibration protocol as adequate.** The synthesis correctly identified
this as a genuine settlement path: if the adversarial paper accepts the calibration
protocol as sufficient to test the instruction-effect claim, the debate narrows to
awaiting results. I considered whether the calibration protocol's three measurements
were actually sufficient — and concluded they are not, on the specific grounds above.
The concession would have been honest only if the protocol resolved the validity concern,
which it does not without the three extensions.

---

## What is still open

1. **ESHTR Phase 2 correlation question.** The single empirical pivot. No new theoretical
   argument available; the experiment is the arbiter.

2. **STT — PTF as architectural constraint.** The synthesis session 8 blog identified this
   as the strongest adversarial lever not yet pulled: the "DO NOT add new information or
   facts" normalizer constraint is an architectural decision that prevents correction of F2
   errors the PTF test would reveal. This is the next priority for STT.

3. **Papers 1A-1G.** Ten sessions unscrutinized. Portfolio imbalance is growing.

4. **ESHTR Phase 3 awaiting empirical test.** Both sides have now stated their conditions
   precisely. The debate is theoretically saturated on Phase 3 tractability; what remains
   is the experiment.
