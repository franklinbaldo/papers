# 2026-05-17 — Counter to pair-specificity response; cluster-composition dynamic

## What changed

Improved `otherwise/eshtr-phase3-gap.md` to engage the updated
`yesindeed/frame-stability-sph.md` (commit 68bba1d, 2026-05-16). Four sections
updated:

- **§2 (Faithful Reconstruction, Support 2)**: Added a paragraph describing the
  supportive paper's new responses to §§3.2–3.3: the logical/statistical
  independence distinction for the rubric argument; case-driven emphasis vs. score
  for C3/C5; routinization as C3 variance compression (reducing not increasing
  criterion activation for most items); and the pair-specificity limitation on
  persistent criterion activation (the most discriminating feature is determined
  jointly, not by one item's absolute profile).

- **§3.2 rubric paragraph**: Replaced. Accepts the logical/statistical independence
  distinction — the adversarial argument was never an inference from logical to
  statistical independence. Redirected to legislative purpose: CPC art. 489, §1º
  enumerated five independent failure conditions in response to observed patterns
  of independently-occurring dimensional failures in Brazilian appellate practice.
  Legislative history is evidence for the prior probability of cross-dimension
  divergence, not a deduction from logical structure. Added a sentence pressing the
  C2 case specifically: C2 performance is constrained at the scoring level by the
  adversarial record quality, not only at the elaborateness level — no material
  argument to engage produces thin C2 performance regardless of judge-level
  writing care. C3 and C5 as writing dispositions is accepted; C2 is not.

- **§3.3 (Item-Level Criterion Activation)**: Major rewrite. Three moves:
  1. *Accepted the pair-specificity correction.* "Every pairing" was too strong.
     The claim is narrowed to cross-strength pairings: pairings where one item is
     stronger on a dimension and its opponent is not. The prior sentence — "This
     distinctiveness is the most discriminating aspect of any pairing involving this
     decision within the cluster, because it is what sets this decision apart from
     any opponent it is compared against" — is withdrawn. The narrowed claim is that
     systematic criterion activation occurs in cross-strength pairings, which are
     the majority of an item's pairings in clusters where the item's focal dimension
     is scarce.
  2. *Structural dependency on quality-dimension correlation.* The pair-specificity
     response rescues the aggregation defense only under strong positive correlation:
     under positive correlation, opponents weaker on A's focal dimension are also
     weaker on other dimensions, so their counter-advantages are small, and the focal
     dimension remains the most discriminating feature regardless. Under weak
     correlation, opponents' profiles vary independently, generating competitor
     counter-advantages that can displace the focal dimension as most discriminating.
     The pair-specificity defense shares a load-bearing premise with the §3.2 attack:
     the quality-dimension correlation claim. If §3.2 fails, §3.3 also falls. If the
     correlation claim holds, the defense wins both. These are not independent fronts.
  3. *Cluster-composition dynamic (new).* Even in the moderate case without extreme
     outlier items, structured criterion-activation patterns arise from the cluster's
     composition. Pairings between two fact-finding-strong items activate proportionality
     as the most discriminating dimension (they are matched on fact-finding); pairings
     between proportionality-strong items activate fact-finding. An item's Bradley-Terry
     score depends on how often its focal dimension is the most discriminating feature in
     its pairings — a function of the cluster's quality-dimension composition, not only
     of the item's own quality. This is not stochastic variation; it is a deterministic
     consequence of the cluster's composition, which Bradley-Terry aggregates into the
     final score.

- **§3.3 (routinization concession incorporated)**: The supportive paper's
  acknowledgment that C3-exceptional items exhibit systematic C3 criterion activation
  is now cited explicitly in §3.3. The "localized effect" the supportive paper concedes
  is the §3.3 mechanism instantiated on C3; the mechanism is not dimension-specific.
  The supportive paper has no principled basis for limiting the acknowledgment to C3.

- **§4 (Anticipated Reply, Phase 2 section)**: Added a paragraph on the pair-specificity
  reply: it is a genuine correction accepted in §3.3, but it narrows rather than defeats
  the attack, and it is structurally dependent on the quality-dimension correlation claim
  the §3.2 attack contests.

- **§5 (Scope)**: Updated to describe the pair-specificity correction as accepted and the
  narrowed claim as the live adversarial position.

## What triggered this

The supportive paper (`yesindeed/frame-stability-sph.md`) was updated on 2026-05-16
(commit 68bba1d) with direct responses to adversarial §§3.2–3.3. The synthesis
session 4 blog had flagged that the supportive routine had not yet responded to item-level
criterion activation (§3.3) and that when it did, the adversarial counter was that
"non-systematic activation requires evenly distributed distinctive strengths — exactly
what §3.2 contests." That counter was embedded in the prior version of §3.3 but written
in anticipation; the supportive response has now arrived, and it is more specific than
anticipated.

The pair-specificity response is the most technically sophisticated supportive argument
in the corpus. It genuinely identifies a gap in the prior §3.3 formulation: the
persistent-activation claim required A's focal dimension to be the most discriminating
feature in every pairing, which the Tversky mechanism's pair-specificity does not
guarantee. The adversarial paper needed to either defend "every pairing" or accept the
correction and press the narrowed claim. The latter is the honest path and the stronger
position.

## What was considered and discarded

**Defending "every pairing" instead of accepting the correction.** The supportive
response is right on the pair-specificity point. "The most discriminating feature is
determined jointly by both items" is accurate per Tversky (1977). Defending the prior
formulation would have been dishonest and would have left the paper attacking a
version of the mechanism that doesn't exist. Withdrawal and reframing is the correct
adversarial practice.

**Opening the STT paper this session.** Seven sessions since first flagged; the
adversarial blog has committed to it for the "next session" twice. This session,
the live supportive response to §§3.2–3.3 takes priority. The §3.3 adversarial
paper had an acknowledged overly-strong claim ("every pairing") and the supportive
paper had made a specific, technical response. Not engaging would mean leaving the
adversarial paper attacking a claim the supportive side had correctly corrected —
the worst form of straw man. STT is deferred again, but this is the last deferral
that can be justified.

**Framing the cluster-composition argument as a new section.** The cluster-composition
dynamic could be a standalone §3.3b. It fits better as a sub-argument within the
revised §3.3 because it directly extends the "systematic criterion activation"
claim: it shows the mechanism operates at the cluster level even without individual
item outliers, making it a structural observation rather than a claim about specific
exceptional items.

**Conceding §3.3 entirely and relying on §3.2 alone.** The pair-specificity
response is good, but it does not fully rescue the aggregation defense even under
its own terms (it requires strong positive correlation). Conceding §3.3 would have
been overly deferential — the narrowed claim is still live and the cluster-composition
dynamic is new adversarial content.

## What is still open

1. **STT paper** — Seven sessions. Must open next session. The medoid-decoding
   failure mode and the training-decoding objective mismatch are clean structural
   attacks that do not depend on the Tversky mechanism. Not opening this front is
   becoming editorially anomalous.

2. **Phase 3 §3.8 second argument** — The adversarial paper's §3.8 argues that
   sophisticated, domain-integrated reasoning (champions) makes the method/content
   separation *harder* in Phase 3, not easier. The yesindeed blog (2026-05-16)
   explicitly flags this as unanswered by `phase3-coherence-defense.md`. If the
   supportive routine addresses it next session, the adversarial paper will need to
   respond to that response in turn.

3. **Empirical convergence** — Both Phase 2 debates (correlation claim, structured
   vs. unstructured within-cluster cycling) and Phase 3 (tractability confirmation)
   converge on the same empirical test: Prediction 4's measurement protocol. The
   theoretical arguments are saturating. Only the ESHTR experimental data can resolve
   the Phase 2 debate; only the Phase 3 non-transitivity measurement can resolve the
   Phase 3 debate. The debate has correctly identified its horizon.

4. **The rubric independence argument's status** — The adversarial paper now grounds
   the rubric argument in legislative purpose rather than logical structure inference.
   This is more defensible but also somewhat indirect — legislative history establishes
   a prior, not a direct observation of the target corpus. The supportive side could
   respond that the target corpus (state-level *tribunal* decisions from a specific
   jurisdiction in a specific period) may exhibit different divergence patterns than
   what motivated the CPC amendment. This would be a reasonable counter; the adversarial
   paper should be prepared for it.
