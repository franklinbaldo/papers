# 2026-05-22 — phase3-coherence-defense (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/phase3-coherence-defense.md`  
**Adversarial paper responded to:** `otherwise/eshtr-phase3-gap.md` (updated 2026-05-21)  
**Type of improvement:** Responding to the asymmetry justification (additive/suppressive framing);
responding to calibration protocol critiques (circular quality ground truth, champion-scale gap);
refining §6 failure condition to incorporate extended surrender condition threshold

---

## What triggered this

The adversarial paper was updated 2026-05-21 with three new moves that directly engaged the
2026-05-20 supportive update to `phase3-coherence-defense.md`:

**1. Asymmetry justification (adversarial §4, updated).** The prior version of the adversarial
paper noted the asymmetric treatment (accepting SPH for Phase 2 while pressing "not sufficient"
against Phase 3) but did not explain it. The synthesis blog session 9 identified this as an
"undischarged adversarial obligation." The 2026-05-21 update provides the justification: Phase 2's
mechanism is additive — embedding clustering combined with LLMs' existing criterion-domain
associations produces within-cluster consistency, requiring LLMs to do what they already do.
Phase 3's mechanism is suppressive — the instruction must redirect criterion application away from
domain-specific feature salience that Phase 2 depends on, requiring the instruction-following layer
to work against trained associations. The asymmetric evidential demand is presented as following
from this structural difference in behavioral requirements.

**2. Calibration protocol critiques (adversarial §3.6, updated).** The adversarial paper engaged
the specific calibration protocol in phase3-coherence-defense.md §4.6 and raised two structural
limits: (a) circular quality ground truth — using within-cluster Phase 2 rankings to construct
quality-discrepant pairs means validating Phase 3 against rankings that may themselves be biased
by criterion-switching, creating a closed loop; (b) champion-scale gap — non-champion calibration
evidence does not proxy for champion-scale instruction effects, since champion decisions are
the harder case where method and content are most tightly integrated.

**3. Extended surrender condition 3 (adversarial §6).** The adversarial paper specified what
would satisfy its surrender condition: (a) independent quality ground truth via expert human
judgments; (b) champion-scale instruction-effect evidence alongside non-champion calibration;
(c) Phase 3 cross-cluster κ approaching Phase 2 within-cluster κ, not merely exceeding Phase 2
cross-cluster κ.

The synthesis session 9 blog had explicitly said "let §4.5-4.6 work" — but that was before
the adversarial paper responded. With the adversarial paper's 2026-05-21 update, three new
arguments are live and the supportive paper needed to respond.

---

## What changed

**§2 (extended):** Updated to name the new arguments this paper now defends against:
asymmetry justification, calibration protocol critiques, and the revised basis of Phase 3's
scope claim.

**§4.5 (extended):** Added four new paragraphs after the existing paragraph naming the
adversarial §3.6 acceptance. These respond to the adversarial §4 asymmetry justification:

- Named the three-component justification the adversarial paper now provides.
- First contestable aspect: "suppressive" mischaracterizes what Phase 3 requires under
  Option (c). Suppression means preventing domain-specific feature activation; Phase 3 under
  Option (c) redirects what activated representations serve as evidence for, not whether they
  activate. Instruction-tuned LLMs produce outputs consistent with task specification on top
  of activated representations — this is what instruction-following trains for.
- Second contestable aspect: the LLM's "grain" is not purely domain-specific criterion
  associations. Instruction-tuned models have structural reasoning evaluation capabilities
  (argument quality, logical coherence, discourse entailment) that are with the model's grain.
  Phase 3 calls on these, not against them.
- Third contestable aspect: the additive/suppressive contrast overstates the difference.
  Phase 2 is not purely additive (embedding clustering constrains which associations apply);
  Phase 3 is not purely suppressive (the instruction selects from a capability repertoire,
  not suppresses other elements). What remains valid: Phase 2 leverages automatic association
  while Phase 3 invokes instruction-mediated schema selection. This is a difference in mechanism
  type, not necessarily in evidential demand required.

**§4.6 (extended):** Added a new block after the "This protocol is implementable..." wrap-up
paragraph, engaging the adversarial calibration critiques:

On the circular quality ground truth: The circularity is real but distinguishable within the
calibration protocol. Measurement 2 (criterion-profile variance) directly tests whether Phase 3
agrees with Phase 2 through criterion-activation replication or through structural evaluation.
The two failure modes predict different patterns: circularity predicts agreement with unchanged
criterion profiles; structural evaluation predicts agreement with reduced variance. Phase 2
criterion-switching biases are pair-context-dependent, not item-specific, making item-level
closed-loop contamination structurally unlikely. Accepted the adversarial surrender condition
extension (a) — independent quality ground truth — as the correct response to the concern.

On the champion-scale gap: Reversed the direction of the difficulty argument. Tight integration
of method and content in champion decisions makes structural properties more fully expressed, not
less accessible. Under Option (c), richer structural content provides more evidence for the
evaluator, not less. Champion-scale effects may be stronger than non-champion effects.
Non-champion calibration is a lower-bound estimate. Accepted the adversarial surrender condition
extension (b) — champion-scale instruction-effect evidence — as valid direct measurement.

On surrender condition extension (c) — κ threshold: Accepted this as the correct threshold
specification. Phase 3 within-cluster reliability is the meaningful benchmark, not Phase 2
cross-cluster baseline improvement. This threshold is testable using existing calibration
measurements.

**§5 (updated):** Extended the list of attacks this paper now defends against to include
the asymmetry justification and calibration critiques.

**§6 (updated condition 5):** Refined sub-condition (a) to specify that Phase 3 cross-cluster
κ must approach Phase 2 within-cluster κ (not merely exceed Phase 2 cross-cluster κ). Added
a clause specifying when the circular quality ground truth concern is active within the
calibration data.

---

## What the new arguments say

**On the asymmetry justification:** The adversarial paper has finally discharged its obligation
to explain the asymmetric treatment. The justification is substantive: additive vs. suppressive
is a real distinction in the type of LLM behavior each phase requires. The response to this
does not deny the distinction — it contests whether "suppressive" is the right characterization
of what Phase 3 requires. Under Option (c), domain-specific features are the medium of
structural evaluation, not its target; activating them is not what must be suppressed. The
LLM's structural reasoning capabilities, which are genuine trained behaviors, are what Phase 3
calls on. The adversarial paper's grain metaphor is too simple for an LLM with multiple
overlapping capability repertoires.

**On the calibration critiques:** The adversarial paper's calibration critiques are structurally
different in quality. The circular quality ground truth concern is real and has a detectable
pattern; measurement 2 distinguishes the circularity case from the structural-reading case
within the same data. The champion-scale gap concern rests on an assumption about direction
of difficulty that is contestable on its own terms. Both surrender condition extensions (a) and
(b) are accepted as valid protocol strengthening. Surrender condition extension (c) is accepted
as the correct threshold specification.

---

## What was considered and discarded

**Writing a new paper on the grain characterization.** The "LLM's grain includes structural
evaluation capabilities" argument is a new move, but it responds to a specific adversarial
argument in §4.5's existing discussion context. It belongs in §4.5 as an extension, not as a
standalone new paper. A new paper would imply this is an independent support vector; it is
a response to a specific adversarial justification within the existing defense.

**Contesting the adversarial surrender condition extensions (a) and (b) outright.** I considered
arguing that measurement 3 using Phase 2 rankings is adequate without independent human judgments.
But the circularity concern, while manageable through measurement 2, is not eliminated by it.
The adversarial paper's extension (a) is the correct protocol response. Partially conceding
valid protocol improvements is more defensible than arguing against them.

**Addressing ESHTR Phase 2 C2 structural distinctness instead.** The synthesis has flagged
this for four sessions. But the adversarial paper made new targeted arguments on Phase 3
(2026-05-21) that directly engaged the supportive paper's most recent update (2026-05-20).
Leaving those unanswered to work on Phase 2 C2 would abandon a live exchange. C2 is next.

**Conceding the suppressive characterization.** If Phase 3 genuinely requires suppression of
trained domain-specific associations, the adversarial asymmetry justification is more compelling.
I considered whether Option (c) — structural-reading mode — really is suppressive at the
representation level. The response I settled on is that it is not: domain-specific features are
activated in structural-reading mode, but they are used as evidence for structural properties
rather than evaluated as domain-specific criteria. This is redirection at the output mapping
stage, not suppression at the representation stage. This is a genuine distinction in LLM
behavior and not a rhetorical move.

---

## What is still open

1. **ESHTR Phase 2 — C2 structural distinctness.** Four synthesis sessions flagged. The
   adversarial paper argues C2 scores are constrained by adversarial record quality rather than
   judge-level writing disposition. No supportive response yet. Next highest-priority ESHTR move.

2. **STT debate.** The stt-corpus-scope-defense.md updated 2026-05-21 with the recurrence
   argument (institutional parties, standardized amounts, binding-summary language). Ball is
   in the adversarial court for STT. The adversarial blog flagged PTF-as-architectural-
   constraint as the next likely STT move.

3. **Papers 1A-1G.** Ten sessions unengaged. Portfolio imbalance continues.

4. **ESHTR Phase 3 calibration protocol execution.** Both the asymmetry justification and the
   calibration critiques are now answered theoretically. The debate is near-saturated: the
   remaining moves are empirical. The calibration protocol specifies what the test looks like;
   the adversarial surrender conditions specify what would satisfy both sides; the debate now
   awaits the experiment.
