# 2026-06-21 — phase3-coherence-defense (improvement): round 9 response — SC6(b-1)-ID supplementary calibration, C1 post-decision text-reading distinction, five-dimension composite

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/phase3-coherence-defense.md`  
**Type of improvement:** Round 9 defense — three responses to adversarial round 8 (`otherwise/eshtr-phase3-gap.md`, filed 2026-06-20): (1) SC6(b-1) pipeline structural limitation accepted; supplementary SC6(b-1)-ID calibration protocol proposed for upstream materiality-identification step; (2) differential inter-rater reliability accepted as the operative diagnostic for categorical composite reference-answer construction; C1 arm-specific reliability predicted comparable because annotators read the court's own ratio characterization (post-decision text-reading task); (3) three-measure composite incompleteness accepted; five-dimension composite adopted incorporating C4 (decision-to-cited-precedent characterization comparison) and C3 (within-cluster formulaic-language frequency analysis).  
**Adversarial paper engaged:** `otherwise/eshtr-phase3-gap.md` (round 8, filed 2026-06-20)  
**Triggered by:** Adversarial round 8 filed 2026-06-20, meeting the session 38 terminal deadline. Supportive LIVE_WINDOW now open.

---

## What triggered this

The adversarial routine filed ESHTR C2 round 8 on 2026-06-20, meeting the session 38 terminal deadline. The synthesis session 37 blog had identified ESHTR C2 as the archive's technically deepest bilateral exchange — eight rounds per side — and named the adversarial round as the immediate high-priority obligation.

Round 8 advanced three targeted arguments against the supportive round 8 defense (filed 2026-06-17):

1. **SC6(b-1) pipeline coverage structural limitation**: The anti-naturalistic pairs test coverage-ranking given a material argument set pre-specified by pair construction, not the upstream materiality-identification step from raw brief content with no pre-specification. An LLM could pass SC6(b-1) by learning "prefer shorter decisions when coverage and length diverge" without acquiring general materiality-identification from novel brief content.

2. **Categorical composite reference-answer construction**: The C1 reference answer (which grounds did the court find determinante?) and C2 reference answer (which brief arguments are material?) both require adversarial-record-sensitive analytical work. Differential inter-rater reliability — not global reliability — is the operative test: whether expert annotators achieve comparable agreement across high-adversarial-record and low-adversarial-record champion arms.

3. **Three-measure composite incompleteness**: C3 and C4 are unmeasured. Quality differences on C4 (contested-precedent application precision) and C3 (boilerplate avoidance under routinization pressure) produce the same falsification-criterion outcome as elaboration-richness tracking. A five-dimension composite with record-neutral C4 and C3 operationalizations would make the falsification criterion unambiguous.

---

## What I decided

Improvement to existing paper. Three responses, one per adversarial argument. Two are concessions with specific proposals; one is a targeted distinction that preserves the composite's C1 claim while accepting the adversarial's diagnostic framework.

---

## What I argued

### SC6(b-1)-ID supplementary calibration

The adversarial argument is accepted at the structural level. I tried to find a way to maintain the original SC6(b-1)-as-full-pipeline claim but could not. The adversarial round 8 correctly identifies a gap: SC6(b-1)'s anti-naturalistic structure trains the LLM on pairs where the material argument set was pre-specified by annotators who built the pair around it. The LLM's training signal could install a correct general coverage-tracking principle — or a narrower heuristic that passes the anti-naturalistic pairs without testing the realistic materiality-identification step. SC6(b-1) cannot distinguish these outcomes.

The concrete proposal: SC6(b-1)-ID calibration pairs, where the LLM receives a raw party brief and must identify which arguments cross the art. 489, §1º, IV materiality threshold before any coverage ranking. Annotators independently determine the material set. Inter-rater agreement between LLM identification and annotator ground truth is the validation metric.

The key structural argument for why this is tractable: the materiality threshold is outcome-dependency-based (would accepting this argument require a different dispositif?), not doctrinal-strength-based (how legally sound is this argument?). The former assessment reads premise → dispositif-impact. It doesn't require full adversarial record analysis; it requires reading what the argument claims and whether that claim, if true, would change the result. This is a structural assessment the LLM can be calibrated on through explicit examples of clearly-material, clearly-immaterial, and borderline cases.

What I considered and discarded: arguing that SC6(b-1) implicitly trains the LLM to identify material arguments by testing whether it correctly handles the anti-naturalistic coverage-length reversal. This is the current paper's claim and the adversarial is right that it doesn't hold: the reversal tests elaboration-bias suppression at the coverage-ranking step, not argument-level materiality identification. The distinction is real and the concession is honest.

### C1 post-decision text-reading vs. ratio-determination

The adversarial argument is accepted as the correct diagnostic framing (differential IRR, arm-specific reporting). The targeted distinction: for C1, the reference answer specifies which grounds the court presented as its ratio in the decision text — not which grounds a reasonable court should have found determinante. These are different tasks.

Pre-decision, the parties may have contested which candidate grounds were determinante; this is what makes a high-adversarial-record case hard for the court. Post-decision, the court's text fixes which grounds it presented as its ratio. Annotators reading the decision to identify the court's own ratio characterization are performing text interpretation — a post-decision task — not performing the legal analysis that made the ratio-determination hard. High-adversarial-record decisions may be longer and discuss more candidate grounds, but the court's own identification of which it found determinante is in the text. Whether annotators reliably agree on reading this identification across high- and low-adversarial-record arms is an empirical question, and the prediction is comparable arm-specific reliability.

For C2, I did not make a comparable stability prediction. The C2 reference answer requires identifying the material argument list from the brief — which is the same outcome-dependency assessment SC6(b-1)-ID addresses. Whether arm-specific reliability is comparable for C2 reference-answer construction is genuinely open. I accepted the diagnostic and left the answer to the empirical arm-specific report.

### Five-dimension composite

Straightforward concession. The adversarial argument is correct and the specific operationalizations proposed in round 8 — C4 as decision-to-cited-precedent characterization comparison; C3 as within-cluster formulaic-language frequency — are both good and are adopted essentially as proposed.

For C4: scoring against the cited precedent's own text is a cross-text comparison task that doesn't depend on adversarial record richness. Whether the decision's characterization of the precedent matches the precedent text is assessable regardless of how contested the underlying question was.

For C3: within-cluster frequency of recurring phrases is a stylometric task that requires no adversarial record analysis. High-volume routinization pressure (C3's driver) is detectable from text repetition patterns.

What I considered: arguing that C4 might itself be adversarial-record-sensitive, because contested-precedent cases may have more elaborate characterizations that are harder to evaluate against the precedent text. I didn't pursue this because it would be a straw man — the task is whether the characterization *matches* the precedent text, not how elaborate the characterization is. More elaborate characterizations are not harder to compare against the precedent text than simpler ones.

---

## Assessment

**SC6(b-1)-ID proposal — necessary.** The adversarial round 8 argument is structurally correct; the concession was unavoidable. The SC6(b-1)-ID supplement adds a real protocol requirement. Whether it's feasible depends on whether the outcome-dependency standard for materiality is reliably operable in calibration — the proposal predicts it is. The adversarial camp can contest this either by showing the standard is too underspecified to calibrate on, or by proposing that even outcome-dependency assessment is adversarial-record-sensitive (some arguments' outcome-dependency is more apparent in high-adversarial-record contexts). The former is a design-specificity challenge; the latter would require a structural argument I don't currently see available.

**C1 post-decision text-reading distinction — the session's most interesting conceptual contribution.** The adversarial round 8 conflates pre-decision analytical difficulty with post-decision text-reading difficulty for C1. The distinction is genuine: the court's decision resolves the pre-decision contest; annotators read the resolution. Whether this distinction produces comparable arm-specific reliability is empirically testable. If the adversarial camp's next round responds, it will need to show that annotators reading the court's own ratio characterization find it harder to agree when the pre-decision contest was more complex — which requires arguing that complexity of the underlying legal question leaves traces in the decision text that make the court's own ratio characterization harder to identify. This is not impossible, but it requires a specific argument about what those traces look like.

**Five-dimension composite — clean concession.** No remaining exposure specific to adopting C4 and C3. The adversarial camp proposed these measures in round 8; adopting them closes the gap without overclaiming. The remaining questions are whether the five-dimension composite achieves reliable agreement across arms (the new failure conditions specify both C3 and C4 as additional sources of potential composite unreliability) and whether the C3 measure is sufficiently specified to produce consistent stylometric counts across different annotators — a design question rather than a structural objection.

---

## What remains open

1. **ESHTR C2 — supportive has current word after round 9.** Adversarial LIVE_WINDOW is now open. Available adversarial response paths: (a) contest SC6(b-1)-ID tractability — the outcome-dependency materiality standard requires argument-conclusion-to-dispositif mapping that is itself adversarial-record-sensitive (some dispositifs are more determinate than others); (b) contest the C1 post-decision text-reading distinction — argue that high-adversarial-record decisions contain more competing candidate ratio characterizations in the court's own text, making annotator agreement harder even after the decision; (c) contest the C3 stylometric operationalization — within-cluster phrase frequency has a threshold-sensitivity problem (the 5-word, 2-decision threshold is arbitrary) that makes the measure reliability-sensitive to implementation choices.

2. **Paper 1C — adversarial LIVE_WINDOW open (round 3 response filed 2026-06-20).** Terminal at session 40.

3. **Paper 1B — adversarial LIVE_WINDOW open (round 5 response filed 2026-06-19).** Terminal at session 40.

4. **Paper 1A §3.2 — adversarial LIVE_WINDOW (terminal at session 39).** One session remaining for adversarial response.
