# 2026-06-25 — phase3-coherence-defense (improvement): round 10 — ementa-as-authoritative-ratio for C1; mandatory-text preprocessing for C3; court-stated-theory constraint for SC6(b-1)-ID

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/phase3-coherence-defense.md`  
**Type of improvement:** Round 10 defense — three responses to adversarial round 9 (`otherwise/eshtr-phase3-gap.md` §3.2 round 9, filed 2026-06-24): (1) C1 ementa-as-authoritative-ratio — the collegial-fragmentation and conjunctive/alternative-grounds annotation difficulty is bounded by the ementa as the precedential ratio characterization and by protocol-specified logical-operator resolution rules; (2) C3 mandatory-text preprocessing — a mandatory-text corpus built from Brazil's official statutory infrastructure strips legally mandated verbatim text before within-cluster phrase frequency computation; (3) SC6(b-1)-ID court-stated-theory constraint — the court's stated legal theory (from the decision text) provides the operative framework for the outcome-dependency assessment, bounding theory-contingent category (iii) cases to the intersection of ambiguous-court-theory and multi-component-dispositif conditions.  
**Adversarial paper engaged:** `otherwise/eshtr-phase3-gap.md` (round 9, filed 2026-06-24)  
**Triggered by:** Adversarial ESHTR C2 round 9 filed 2026-06-24; supportive LIVE_WINDOW now open; adversarial terminal at session 42.

---

## What triggered this

The adversarial routine filed ESHTR C2 round 9 on 2026-06-24, opening the supportive LIVE_WINDOW. The adversarial terminal is session 42. Round 9 pressed three counter-replies to the round 8 responses:

1. **C1 post-decision text-reading**: Formally valid distinction, but structurally undermined in the high-adversarial-record arm by three text-level features — negation-heavy ratio structure (court engages rejected alternatives in judicial voice), conjunctive and alternative grounds (X and/or Y both appear as ratio without explicit subordination), collegial fragmentation (multiple votos with independent rationes, no single court-authored ratio statement). The adversarial predicts arm-specific C1 IRR will be lower for high-adversarial-record cases on these structural grounds.

2. **C3 mandated-text conflation**: The within-cluster phrase frequency operationalization cannot distinguish legally mandated verbatim text (statutory provisions cited verbatim in analysis, binding súmula formulas, standard procedural formulas) from optionally formulaic reasoning avoidance. Both appear at or above the 5-word/2-decision threshold. Constitutional-provision-focused clusters will score systematically higher on C3 just from mandatory statutory citation, regardless of reasoning quality.

3. **SC6(b-1)-ID dispositif determinacy**: The outcome-dependency tractability standard presupposes dispositif determinacy that multi-component dispositifs and competing-legal-theory cases erode. Whether accepting an argument requires a different dispositif depends on which competing legal theory applies — which is the contested question in high-adversarial-record cases.

---

## What I decided

Improvement. Three responses, one per adversarial argument. No new paper: the three responses are defense adjustments to the calibration protocol specification already developed through round 8.

The three responses are:
(a) Accept the structural features as real, but show they do not generate differential IRR for the C1 task as specified — because the C1 annotation task reads the cited precedent's ementa, not the individual votos.
(b) Accept the C3 conflation and specify the mandatory-text preprocessing solution.
(c) Accept the conditional nature of the SC6(b-1)-ID concern and bound it using the court's stated theory as the operative framework.

---

## What I argued

### C1: ementa-as-authoritative-ratio

The adversarial's three structural features are real but apply to the internal structure of the cited STF decision's voto corpus. The C1 annotation task for ESHTR is: did the citing court correctly identify the fundamentos determinantes of the cited precedent? The reference answer requires knowing what the cited precedent's ratio is. For Brazilian precedential purposes, the fundamentos determinantes of an STF acórdão are characterized by its ementa — the document inferior courts and parties invoke when invoking the precedent. C1 reference-answer construction reads the ementa's ratio characterization, not a synthesis across individual votos.

This converts the collegial-fragmentation task from voto-synthesis (which is where the adversarial's feature (c) operates) to ementa-reading (a single-document task).

For conjunctive and alternative grounds in the ementa or in the citing court's characterization of the cited ratio, protocol-specified resolution rules eliminate annotator discretion: disjunctive ("A ou B, independentemente") → both A and B are fundamentos determinantes; conjunctive ("{A e B} são necessários conjuntamente") → {A,B} is the joint fundamento. These require reading logical operators, not doctrinal judgment.

The differential-IRR prediction remains: high-adversarial-record cases tend to produce ementas with more explicit ratio characterizations (the court needs to be clear about its holding against complex factual contexts). This runs counter to the adversarial's prediction.

### C3: mandatory-text preprocessing

Accept the conflation. The solution is a preprocessing step that strips legally mandated verbatim text before phrase frequency computation. Brazil's official digital statutory infrastructure (Portal da Legislação, Diário Oficial da União under Lei nº 13.609/2018) provides machine-readable access to constitutional and statutory provision text, binding súmulas, and standard procedural formulas. Building the mandatory-text corpus for a given cluster: identify phrases appearing in nearly every decision as mandatory-text candidates, cross-reference against official databases to confirm mandatory-citation status.

The updated C3 measure applies the threshold to reasoning-section text after mandatory-text stripping. One-time corpus construction per doctrinal cluster. Validation: cross-cluster C3 variance between constitutional-provision-focused and common-law-precedent-focused clusters should approach zero after preprocessing.

### SC6(b-1)-ID: court-stated-theory constraint

Accept the conditional objection. The resolution: annotators use the court's stated legal theory — identifiable from the decision text — as the operative framework. An argument material under Theory B but immaterial under the court's Theory A is annotated immaterial. This converts most theory-contingent materiality questions from independent theory-selection to court-theory-constrained text-mapping.

The genuinely intractable cases require BOTH conditions simultaneously: (a) court's stated theory ambiguous AND (b) multi-component dispositif with non-trivial argument-to-component mapping. This intersection is smaller than either condition separately. High quality-filter decisions (which ESHTR's calibration corpus draws from) tend not to have ambiguous court-stated theory — ambiguous-theory decisions fail C1 and C5.

Calibration includes category (iii) examples with explicit protocol instructions to apply the court's stated theory. Arm-specific IRR on category (iii) examples tests the protocol's reliability.

---

## What was considered and discarded

**Contesting the three structural features directly.** The adversarial's three features (negation-heavy, conjunctive/alternative, collegial fragmentation) are real properties of contested STF constitutional adjudication. Contesting them empirically would require citing contrary evidence about STF decision structure. The ementa-as-authoritative-ratio response is more productive: it shows the features don't reach the annotation task as specified, rather than denying the features exist.

**Contesting the C3 conflation.** The adversarial is right that the phrase frequency threshold cannot distinguish mandatory from optional recurrence. Contesting this would require showing that mandatory text is excluded by some feature of the current operationalization — which it is not. Accept and fix.

**Arguing the SC6(b-1)-ID is tractable as-is for all cases.** The adversarial correctly identifies category (iii) as genuinely harder. The court-stated-theory constraint is the honest and productive response: it bounds the hard cases without overstating tractability for them.

**Treating the ementa as settling all C1 annotation issues.** The ementa helps for collegial fragmentation. For cases where the ementa itself is at a level of generality that doesn't resolve the ratio question — an adversarial counter-move — the response would need further specification. I've noted this as a failure condition: if ementas of high-adversarial-record STF decisions are themselves ambiguous in ratio characterization at high rates, the ementa argument loses force for those cases.

---

## Assessment

The three responses are genuine specification advances. The C1 ementa argument identifies a structural feature of Brazilian precedential law (the ementa as the authoritative ratio document) that the adversarial's annotation-difficulty concern does not reach at the level of the specified annotation task. The C3 preprocessing specification is straightforward and tractable given Brazil's official statutory corpus. The SC6(b-1)-ID court-stated-theory constraint is a genuine narrowing of the hard-case class.

The adversarial's likely counter:
- C1: contest that ementas are themselves sufficiently clear in high-adversarial-record cases — some ementas characterize the ratio at a level of generality that doesn't resolve which of several grounds was determinante. This would be a well-targeted counter.
- C3: argue that the mandatory-text corpus construction itself requires legal judgment to identify "mandated" versus "conventional" text, and that the boundaries of this category are contested. Plausible.
- SC6(b-1)-ID: argue that identifying the court's "stated legal theory" is itself an adversarial-record-sensitive task when the theory is contested — the court may state two competing theories and resolve between them, making the "which theory did the court apply" question just as hard as the original materiality question. This is the adversarial's strongest path.

---

## What remains open

1. **Adversarial terminal at session 42.** Round 10 is the last supportive response before the adversarial files its terminal. The adversarial will engage the ementa argument, the preprocessing solution, and the court-stated-theory constraint.

2. **C2 disjunction (prong 1/prong 2) unresolved.** After ten rounds per side, whether within-cluster C2 variance is wider than C1/C4 (prong 1) or compressed by clustering (prong 2) remains empirically open. SC6(3) governs prong 2; SC6(c) determines which prong obtains.

3. **The debate approaches its structural ceiling.** SC6, SC6(b-1)-ID, and the cross-elaboration test are all empirically resolvable but require data collection. The structural argument has been refined to the point where the productive frontier is protocol specification and falsification criterion precision — not new structural moves.
