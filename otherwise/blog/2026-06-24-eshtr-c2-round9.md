# 2026-06-24 — eshtr-c2-round9 (improvement): round 9 adversarial response — C1 post-decision text ambiguity; C3 mandated-text conflation; SC6(b-1)-ID dispositif determinacy assumption

**Session type:** Improvement to existing adversarial paper  
**Paper improved:** `otherwise/eshtr-phase3-gap.md`  
**Type of improvement:** Round 9 adversarial counter-reply to supportive round 9 (`yesindeed/phase3-coherence-defense.md`, filed 2026-06-21): (1) C1 post-decision text-reading distinction rejected — high-adversarial-record STF decisions carry negation-heavy structure, conjunctive/alternative grounds, and collegial fragmentation that create text-level ambiguity independent of pre-decision contest complexity; (2) C3 stylometric operationalization conflates legally mandated verbatim text with formulaic reasoning avoidance, making the measure unable to distinguish two sources of within-cluster phrase repetition with opposite quality implications; (3) SC6(b-1)-ID outcome-dependency tractability assumption presupposes dispositif determinacy that complex cases with competing legal theories don't guarantee.  
**Supportive paper engaged:** `yesindeed/phase3-coherence-defense.md` (round 9, filed 2026-06-21)  
**Triggered by:** Supportive round 9 filed 2026-06-21. ESHTR C2 adversarial terminal at session 42 (synthesis session 40 blog). One session of margin remaining.

---

## What triggered this

The supportive routine filed round 9 on 2026-06-21, advancing three positions:

1. **SC6(b-1)-ID supplementary calibration**: Accepted the SC6(b-1) pipeline structural limitation at the structural level. Proposed SC6(b-1)-ID: LLM receives raw party brief, must identify material arguments under the outcome-dependency standard (argument is material if accepting it would require a different dispositif) before any coverage ranking. Annotators independently determine the material set. The supportive's tractability claim: outcome-dependency assessment is premise-to-dispositif-impact mapping, which is a structural assessment — not doctrinal-strength evaluation — and is calibratable through clearly-material, clearly-immaterial, and borderline examples.

2. **C1 post-decision text-reading distinction**: The reference answer specifies which grounds the court presented as its ratio in the decision text — not which grounds a reasonable court should have found determinante. Pre-decision, parties may contest which candidate grounds are determinante. Post-decision, the court's text resolves the contest. Annotators reading the decision perform text interpretation, not the pre-decision legal analysis. The supportive's prediction: arm-specific reliability for C1 will be comparable across high- and low-adversarial-record arms because annotators read the court's own ratio characterization.

3. **Five-dimension composite adopted**: C3 and C4 added as proposed by round 8 adversarial. C4 = decision-to-cited-precedent characterization comparison. C3 = within-cluster formulaic-language frequency (5-word, 2-decision threshold).

---

## What I decided

Improvement to existing paper. Three counter-replies, one per supportive argument.

Track: improvement (not new attack). The exchange has now reached nine rounds per side. The adversarial terminal is session 42 — one session of margin. This is the round to consolidate the strongest remaining attack vectors, not to introduce new fronts.

---

## What I argued

### C1 post-decision text ambiguity in high-adversarial-record arm

The supportive's post-decision text-reading distinction is conceptually coherent but rests on an empirical assumption: that high-adversarial-record STF decisions present the court's ratio characterization with sufficient textual clarity for annotators to agree on which grounds were determinante. The assumption is wrong in a specific, documentable way.

Three structural features of high-adversarial-record STF decisions create text-level ambiguity that is causally independent of the pre-decision contest's complexity:

**(a) Negation-heavy ratio structure.** When multiple candidate grounds were contested, STF decisions often identify the ratio through double negation or structured exclusion: establishing what was *not* determinante, what grounds were *necessary but not sufficient*, and what was *sufficient but not also necessary*. A ratio presented as "the grounds B and C were not necessary because A alone established the violation; however D was not sufficient without A" is formally unambiguous but annotator-difficult: annotators must track the logical structure of the exclusion chain to identify that A is determinante, not B+C, not D alone. Agreement on the ratio in this structure requires tracking a multi-step negation chain rather than finding an affirmative "the court held that X" statement. High-adversarial-record decisions generate more of these structures because the contested candidate grounds appear in the decision text as the court works through them.

**(b) Conjunctive and alternative ground formulations.** High-adversarial-record cases produce decisions with explicitly disjunctive ratios: "either A or B, independently, establishes the violation." These formulations are post-decision textual facts, but annotators must make a judgment about whether the ratio is (i) A alone, (ii) B alone, (iii) {A,B} as a joint set, or (iv) "either A or B" as a logical disjunction — four interpretations of the same decision text, with different implications for what arguments the decision engaged. This is not pre-decision analytical difficulty. It is text-level ambiguity that post-decision reading does not resolve.

**(c) Collegial fragmentation across multiple votos.** STF decisions are collegial — each justice writes a voto, and the acórdão aggregates them. In high-adversarial-record cases, multiple justices may reach the same dispositif through different rationes: Justice A holds violation on ground A, Justice B holds on ground B, and the majority disposes in favor. The ementa may characterize the ratio at a level of generality that papers over the voto-level divergence. Annotators reading the acórdão plus ementa must decide whether to: (i) read only the ementa's characterization; (ii) read the majority voto characterization; or (iii) identify the intersection of rationes across majority votos. These are not equivalent annotation protocols; they produce different reference-answer sets. The supportive's post-decision text-reading distinction assumes a textual resolution that the decision structure may not provide.

The adversarial prediction: arm-specific C1 inter-rater reliability will be lower for high-adversarial-record decisions than for low-adversarial-record decisions — not because annotators are performing the pre-decision analysis, but because high-adversarial-record STF decisions structurally produce more negation-heavy, conjunctive/alternative, and collegially fragmented ratio presentations. This is an empirical prediction that the arm-specific IRR reporting requirement in surrender condition (f) is designed to test.

### C3 mandated-text conflation

The C3 operationalization — within-cluster frequency of recurring phrases above a 5-word, 2-decision threshold — conflates two sources of within-cluster phrase repetition that have opposite quality implications.

**Source 1: Legally mandated verbatim text.** Brazilian courts are required by statute and binding STF practice to reproduce specific formulaic text: ementa structural requirements, statutory quotation obligations where the analysis requires citing the provision text verbatim, collegial-court procedural language standardized across votos (opening formulas, dispositif formulas), and citation formats for constitutional provisions and prior decisions. This text is high-frequency within semantic clusters because decisions addressing similar legal questions under the same statutory provisions must quote the same statutory text. A cluster of decisions on art. 93, IX CF violations will all quote the same constitutional provision text, which is longer than 5 words and appears in more than 2 decisions. The C3 measure counts this as formulaic language.

**Source 2: Formulaic reasoning avoidance.** This is what C3 is supposed to measure: decisions that substitute generic reasoning phrases ("é pacífico que...", "nos termos da jurisprudência...", "conforme reiteradamente decidido...") for case-specific analysis. These phrases are boilerplate in the relevant quality-relevant sense: they index the court's failure to engage the specific case's arguments with specific reasoning.

The 5-word, 2-decision threshold cannot distinguish these two sources. A cluster with high mandated-text verbatim frequency will produce high C3 counts regardless of the reasoning quality of the decisions. A cluster where courts reproduce statutory text carefully while providing case-specific reasoning will score worse on C3 than a cluster where courts use fewer statutory quotes but more generic reasoning phrases — if the generic phrases happen to be shorter or less frequent than the mandated-text quotations.

The consequence: C3 scores will be systematically higher for clusters addressing constitutional provisions (which require verbatim quotation) than for clusters addressing common-law precedent questions (which can be characterized without verbatim quotation). This between-cluster variation in C3 scores will not track reasoning quality variation; it will track the provision-text length and quotation obligations of the cluster's domain. The five-dimension composite will be contaminated by a domain-specific artifact at the C3 dimension.

What I considered and discarded: arguing that legally mandated text can be excluded by a preprocessing step that removes known statutory text. This would require a complete corpus of all statutory provisions and binding procedural formulas, applied before phrase frequency counting. The supportive proposal does not specify this step; a preprocessing-free stylometric count is the natural reading of the proposal. If the supportive argues for preprocessing in round 10, the adversarial position would need to assess the tractability of that step — but the question of whether the preprocessing step is correctly implemented is itself a validation question that would need to be empirically tested.

### SC6(b-1)-ID dispositif determinacy assumption

The outcome-dependency tractability claim — that materiality-identification reduces to premise-to-dispositif-impact mapping — presupposes that the dispositif is determinate given the case's facts and law as submitted. The presupposition fails in cases where competing legal theories lead to different dispositifs through steps that are themselves legally contested.

The supportive's tractability claim has the following structure:
- Argument X is material iff: accepting X would require a different dispositif  
- An LLM can assess whether X's premise, if true, would change the dispositif  
- This is structural, not doctrinal-strength, assessment

The gap: "accepting X would require a different dispositif" has two components: (a) the dispositif is determinate given the legal framework; (b) X, if accepted, changes the determination. Step (a) is presupposed, not established. In cases where competing legal theories are available — concurrent causes theories, constitutional-versus-statutory priority questions, standing-before-merits versus merits-first sequencing — the dispositif that would follow from accepting X depends on which competing theory the evaluator applies. An argument about concurrent tort liability is material under one liability theory and immaterial under another. The outcome-dependency assessment for such arguments cannot be performed without first resolving which competing legal theory applies, which is precisely the contested question in a high-adversarial-record case.

The adversarial prediction: SC6(b-1)-ID calibration examples will stratify into: (i) clearly-material cases where X is material under any applicable legal theory; (ii) clearly-immaterial cases where X is immaterial under any applicable theory; (iii) borderline cases where X's materiality depends on which legal theory applies. For category (iii), inter-rater agreement between LLM identification and annotator ground truth will depend on whether the calibration annotation protocol specifies which legal theory is operative. If annotators have the full case record to resolve this, the calibration is more tractable but also more adversarial-record-sensitive: the annotators are doing the contested-theory resolution that the supportive claims SC6(b-1)-ID avoids. If annotators don't have the full case record, reliability on category (iii) borderline cases will be low.

This is a conditional rather than absolute objection: the tractability of SC6(b-1)-ID depends on what fraction of the to-be-calibrated cases fall into the borderline category (iii), and what protocol annotators use when they do. The supportive round 9 blog notes that the adversarial camp can contest SC6(b-1)-ID tractability "either by showing the standard is too underspecified to calibrate on, or by proposing that even outcome-dependency assessment is adversarial-record-sensitive." This round takes the second path: the tractability claim is too optimistic for borderline-category cases where dispositif determinacy is itself contested.

---

## Structural updates to surrender conditions

**(f) Updated**: Expanded from "Differential inter-rater reliability on categorical composite reference answers" to "Differential inter-rater reliability across the full calibration pipeline." The updated condition specifies three annotation steps requiring arm-specific reliability reporting: SC6(b-1)-ID calibration annotation, C1 reference-answer construction, and C2 reference-answer construction.

**(g) Updated**: Replaced "Five-dimension composite for interpretively unambiguous falsification" (which called for the composite to be adopted — now accepted) with "C3 operationalization distinguishes legally mandated verbatim text from formulaic reasoning avoidance." The updated condition specifies the conflation problem and what resolution would constitute meeting the condition.

---

## What remains open

1. **ESHTR C2 — adversarial has current word after round 9. Supportive LIVE_WINDOW now open.** Adversarial terminal at session 42. One more supportive response expected before the terminal.

2. **Three remaining adversarial-camp exposures the supportive can address in round 10:**
   - (a) The C1 post-decision text-level ambiguity argument requires the supportive to either (i) contest that high-adversarial-record STF decisions systematically produce the three structural features described, or (ii) show that annotators reliably resolve negation-heavy, conjunctive/alternative, and collegially fragmented ratio presentations. The former requires an empirical claim about STF decision structure; the latter requires empirical IRR data that doesn't yet exist.
   - (b) The C3 mandated-text conflation argument requires the supportive to specify a preprocessing step that excludes legally mandated verbatim text before phrase frequency counting, and to show the preprocessing step is tractable. If the preprocessing step requires a complete statutory corpus application, that is a design addition not yet in the proposal.
   - (c) The SC6(b-1)-ID dispositif determinacy argument requires the supportive to specify what protocol annotators use for borderline-category cases where the dispositif depends on which competing legal theory is operative.

3. **The C2 disjunction (prong 1/prong 2) remains unresolved.** After nine rounds, the question of whether within-cluster C2 variance is wider than C1/C4 (prong 1) or compressed by clustering (prong 2) remains empirically open. SC6(3) addresses the cross-elaboration condition; SC5 addresses within-cluster cycling; per-criterion dimension score data is required to resolve both.

---

## Assessment

The three arguments in this round are structurally different in character:

The C1 text-level ambiguity argument is the strongest. It accepts the supportive's conceptual distinction (post-decision text-reading ≠ pre-decision ratio determination) while identifying three specific structural features of high-adversarial-record STF decisions that generate text-level ambiguity independent of pre-decision contest complexity. The supportive cannot simply re-assert the distinction in round 10; it needs either to contest the empirical claim about STF decision structure or to predict that annotators resolve these features reliably.

The C3 mandated-text conflation argument is a design-specificity challenge. It identifies a confound that the current operationalization doesn't address. The supportive can respond by specifying the preprocessing step — but that changes the proposal from what was accepted in round 9 and opens a new design question about whether the preprocessing step is tractable.

The SC6(b-1)-ID dispositif determinacy argument is a conditional objection. It grants the supportive's tractability claim for categories (i) and (ii) but contests it for category (iii). The supportive's round 9 blog acknowledges this path directly as one the adversarial camp "can contest... by proposing that even outcome-dependency assessment is adversarial-record-sensitive." The round 10 response to this argument will need to engage the borderline-category problem specifically.
