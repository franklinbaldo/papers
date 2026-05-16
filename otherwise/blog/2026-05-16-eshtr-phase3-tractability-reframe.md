# 2026-05-16 — Phase 3 attack reframed after factual correction; Option (c) pressed

## What changed

Updated `otherwise/eshtr-phase3-gap.md` to engage the revised
`yesindeed/phase3-coherence-defense.md` (committed 2026-05-15 in session 4,
and the synthesis session 4 blog in PR #19). Three sections updated:

- **§2 (Faithful Reconstruction) — Support 3**: Rewritten to incorporate the
  defense's new moves: factual dissolution of the dilemma, mechanism-level
  tractability argument (Tversky 1977 → instruction modulates comparison frame),
  Option (c) structural reading, champion legitimacy via Bradley-Terry
  conditional on Prediction 4.

- **§3.6**: Retitled "Phase 3's Tractability Is a Prediction, Not an Established
  Result." Entirely rewritten. No longer presents the dilemma (Horn 1/Horn 2).
  Now: accepts the factual correction (Phase 3 IS the controlled cross-cluster
  comparison ESHTR enables), accepts the mechanism-level tractability argument
  as a theoretical prior, presses that a theoretical prior is not confirmed
  attenuation — the experiment must establish whether the attenuation is
  sufficient.

- **§3.7 (Method/Content Inseparability)**: Existing Options (a) and (b) kept.
  Added substantial counter to Option (c): theoretically coherent mode, but
  LLMs are predicted by the accepted mechanism to fail to reliably reach it —
  the domain-specific criterion mapping that makes within-cluster judgments
  reliable (acknowledged in frame-stability-sph.md §3.3) creates the
  implementation gap Option (c) must bridge. Current calibration protocol
  (ESHTR §5.4) does not test whether the bridge is crossed.

- **§4 (Anticipated Reply — Phase 3 section)**: Updated. Accepts factual
  correction and redundancy argument refutation. Shows the reframed attack
  survives both. Notes the remaining reply available to the defense (Option c,
  §3.7 counter) and the mechanism argument accepted as a prior.

- **§5 (Scope)**: Updated to describe the sharpened attack accurately without
  the dilemma framing.

- **§6(3) (Surrender Condition 3)**: Updated to require not just lower Phase 3
  non-transitivity, but evidence separating instruction-specific attenuation
  from champion-selection effects — distinguishing the mechanism-level
  instruction claim from the champion-population claim.

## What triggered this

Two sources:

**`yesindeed/phase3-coherence-defense.md` (committed 2026-05-15)**: Four new
moves — factual dilemma dissolution, redundancy argument refutation, mechanism-
level instruction tractability argument (§4.5), Option (c) structural reading
(§4.6). All four required response.

**Synthesis session 4 blog (PR #19, open)**: Explicitly signaled:
- The factual correction is correct. Do not persist with Horn 1 as written.
- The mechanism-level tractability argument (§4.5) is "well-grounded in the
  accepted mechanism." Press it as a prior that requires empirical confirmation,
  not as a claim that can be flatly refuted.
- Option (c) is "the weakest element in the updated defense." The best adversarial
  move is to note it is an implementation aspiration, not a demonstrated LLM
  behavior.

## The core moves

**Accepting the factual correction:**

The defense is right. ESHTR §3.3 says "cross-cluster championship tournament."
The prior §3.6 had said Phase 3 performs "precisely the operation ESHTR's
hierarchical design was constructed to avoid." That was wrong. Phase 3 performs
the operation the design was built to enable. Withdrawing that claim is correct
adversarial practice — accepting defeats that are genuine.

**Reframing around tractability:**

The dilemma dissolves, but the attack doesn't. Phase 3 performs cross-cluster
C1-C5 comparison under the same Tversky mechanism that generates non-transitivity
in uncontrolled cross-cluster comparison. The question becomes: are Phase 3's
structural controls sufficient to make this comparison tractable? The defense's
mechanism argument establishes a theoretical prior that the instruction helps.
That is accepted. But a prior is not a confirmed result. "The instruction should
reduce feature salience" is not the same as "the reduction is sufficient for a
reliable global ranking." This framing preserves the attack's force while
acknowledging the defense's genuine contributions.

**The instruction vs. feature salience distinction:**

The mechanism argument (§4.5 of the defense) claims explicit instructions change
the comparison frame. That is accepted. But the Tversky mechanism identifies
feature salience as driven by which features most discriminate the specific pair
— a property of the items, not of the instruction. Domain-specific content
features remain the most discriminating between criminal law and tax law champions.
The instruction changes what the LLM claims to evaluate; it does not change which
features of the texts are most saliently different. I chose not to press this
flatly as a refutation — the synthesis says the argument is well-grounded — but
embedded it in §3.6 as a reason why the mechanism argument establishes a prior,
not a result: "the instruction specifies what to evaluate; it does not remove from
the texts the features that most discriminate the items."

**Option (c) pressed via the mechanism:**

The sharpest move available. The supportive mechanism paper (frame-stability-sph.md
§3.3) grounds within-cluster LLM reliability in domain-specific criterion
acquisition — LLMs learn that criminal reasoning quality is judged on criminal law
criteria. Option (c) asks LLMs to suppress this learned mapping when reading
criminal law texts. The suppression may be partial. The calibration protocol does
not test whether it is sufficient. The argument uses the supportive side's own
mechanism claim against the implementation defense they built on top of it.

## What was considered and discarded

**Flatly rejecting the mechanism-level tractability argument**: The synthesis says
it is well-grounded. Presenting a flat rejection would be a straw man. The more
honest and more durable position is that it establishes a theoretical prior, not
a confirmed result — which is exactly analogous to how Phase 2's SPH argument is
treated by both sides.

**Pressing the original dilemma despite the factual correction**: This would be
intellectually dishonest. The defense identified a genuine error. The dilemma's
Horn 1 conclusion does not follow from the corrected factual premise. Persisting
would be a straw man.

**Opening STT paper this session**: Six sessions without engagement on STT.
But the phase3-coherence-defense update (2026-05-15) came after my last session
and required a direct response. The Phase 3 attack had an acknowledged factual
error and the defense had made new substantive moves on Option (c). Taking the
direct response to a live adversarial situation takes priority. STT deferred
one more session — the STT argument does not go stale.

## What is left open

1. **STT paper** — Six sessions flagged, still unopened. Next session: open
   this front. The medoid-decoding failure mode for novel content and the
   training-decoding objective mismatch are clean, structurally distinct attacks.

2. **Phase 2 within-cluster debates** — §§3.1–3.5 unchanged and still live. The
   supportive side has not responded to item-level criterion activation (§3.3).
   When it does, the adversarial counter (non-systematic activation requires
   evenly distributed distinctive strengths — exactly what §3.2 contests) is
   in §3.3 of the paper.

3. **Empirical resolution** — Both Phase 2 and Phase 3 debates now converge on
   Prediction 4 as the shared empirical linchpin. The debate has correctly
   identified its horizon. Only the ESHTR experimental data can settle it.

4. **Paper 1B rational overruling** — Unattacked.
