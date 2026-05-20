# Phase 3 Is Not a Criterion Substitution: On the Coherence of ESHTR's Global Ranking

---

## 1. Thesis Supported

Baldo (2025), "Embedding-Seeded Hierarchical Tournament Ranking" (ESHTR), Section 3.3, proposes that Phase 3 of the method conducts a cross-cluster championship tournament using the same LLM panel and rubric as Phase 2, with one modification: an additional criterion for **contextual generalizability** — "whether the reasoning quality evident in the decision would transfer to adjacent subject matters."

The implicit claim in the design is that this produces a **unified global quality ranking**: a single ordering of judicial decisions that is coherent with the Phase 2 domain-specific rankings.

This paper responds to the attack in `otherwise/eshtr-phase3-gap.md` (Sections 3.5–3.7 and Section 4), which argues that (a) accepting C1-C5 as domain-general creates a structural dilemma that the defense cannot escape; (b) LLM judges cannot in practice separate domain-specific content from domain-general method; and (c) Phase 3's champion comparators may be artifacts of within-cluster criterion-switching rather than genuine quality peaks.

---

## 2. What This Support Adds

**Vector:** Direct defense. This paper reconstructs the adversarial paper's updated arguments — including the structural dilemma in §3.5, the method/content inseparability claim in §3.6, and the champion-circularity argument in §3.7 — and responds to each on its own terms. The core new move is to show that the dilemma's Horn 1 conclusion rests on a mischaracterization of what ESHTR's hierarchical design was constructed to avoid.

---

## 3. Reconstructing the Updated Attack

### 3.1 The Criterion Substitution Argument

Phase 2 ranks decisions by C1-C5, criteria anchored to domain-specific procedural standards. Phase 3 adds "contextual generalizability" — whether reasoning quality would transfer across domains. The adversarial paper argues that combining these rankings produces a composite of incommensurable criteria, not a unified quality ordering, because a highest-quality Phase 2 decision may score poorly on contextual generalizability if it applies domain-specific statutory formulas.

### 3.2 The Non-Transitivity Recurrence Argument

The adversarial paper argues that contextual generalizability requires cross-contextual judgment that is susceptible to the same criterion-switching mechanism that generates non-transitivity within the ESHTR corpus (§4 of ESHTR). An instruction to "abstract across domains" asks the LLM to bridge precisely the criterion-set differences that produce cross-cluster cycling.

### 3.3 The Structural Dilemma

The adversarial paper (§3.5) presents a dilemma for the prior defense's claim that C1-C5 tests domain-general reasoning method:

- **Horn 1:** If C1-C5 is domain-general, then Phase 3 comparisons under "contextual generalizability" are conceptually equivalent to cross-cluster C1-C5 comparisons. But that, the adversarial paper argues, is "precisely the operation that ESHTR's hierarchical design was constructed to avoid, on the grounds that cross-cluster LLM-panel evaluation produces non-transitive results." Phase 3 then repeats the problem instead of solving it.

- **Horn 2:** If "contextual generalizability" is not simply C1-C5 applied cross-cluster — if it is genuinely different — criterion substitution stands.

The adversarial paper argues the middle position ("C1-C5 at a higher level of abstraction") is unstable: if the instruction changes what is evaluated, it changes the criterion (Horn 2); if it does not, it offers no operational advantage (Horn 1).

### 3.4 Method/Content Inseparability

The adversarial paper (§3.6) argues that LLM judges applying C1-C5 to domain-specific legal texts either:

**(a)** apply domain-specific legal knowledge to identify the ratio, making C1-C5 scores sensitive to domain content in practice, or

**(b)** apply a domain-agnostic template that misses domain-specific load-bearing elements, losing doctrinal precision.

Neither option, the adversarial paper argues, supports the claim that C1-C5 is domain-general in its implementation.

### 3.5 Champion Circularity

The adversarial paper (§3.7) argues that Phase 3 comparators — the Phase 2 cluster champions — may not be genuine quality peaks. If Phase 2 within-cluster rankings are themselves produced by criterion-switching, the champion is whichever decision happened to win the specific pairings the tournament arranged, not necessarily the highest-quality decision under any stable standard. Phase 3's supposed operational advantage (a more homogeneous, quality-selected comparator population) is undermined if Phase 2 cannot be trusted to produce it.

---

## 4. The Defense

### 4.1 C1-C5 as Reasoning Method

The text of C1-C5 does not support the reading that they test domain-specific content.

- **C1** (art. 489, §1º, V): isolating the *determining grounds* (*fundamentos determinantes*) of invoked precedents — the ratio that generalizes from the specific case — is a reasoning operation that applies across domains in the same form.
- **C2** (art. 489, §1º, IV): engaging arguments capable of affecting the outcome tests whether the judge identified and addressed material challenges to the holding. The criterion does not specify what kinds of arguments count; it tests the cognitive operation of engagement.
- **C3** (art. 489, §1º, III): avoiding generic boilerplate tests whether reasoning is specific to the argument structure at hand, not borrowed from a domain-specific formula bank.
- **C4** (art. 927, §1º): correctly applying, distinguishing, or justifying deviation from binding precedent requires understanding why the precedent holds — its underlying principle — so that its scope can be assessed when facts differ. This operation has the same form regardless of subject matter.
- **C5** (art. 1.022): logical completeness and non-contradiction of the dispositif is domain-agnostic.

C1-C5 test whether reasoning *method* was applied correctly: isolating ratio, engaging material arguments, avoiding formulaic shortcuts, abstracting the right principle from precedent, producing a coherent device.

### 4.2 Content vs. Reasoning-Quality Transferability

The adversarial paper's exemplar counterexample — "a criminal sentencing decision may score poorly on contextual generalizability because criminal sentencing employs technical statutory formulas specific to the Código Penal that do not transfer" — conflates:

- **Content-transferability:** whether the specific statutory rules (art. 59, art. 68 CP, *bis in idem* doctrine) apply in other domains. False; they do not.
- **Reasoning-quality-transferability:** whether the method of reasoning demonstrated — the way the judge applies proportionality, isolates ratio, engages arguments, avoids formulaic shortcuts — would produce quality reasoning in other domains.

ESHTR's Phase 3 criterion asks whether "the reasoning quality evident in the decision would transfer to adjacent subject matters" (§3.3, emphasis added). This is a question about the second property, not the first. A decision that scores highly on C1-C5 demonstrates method quality that is, by the nature of what those criteria test, applicable across domains.

### 4.3 Dissolving the Dilemma

The structural dilemma (§3.3 above) rests on a mischaracterization of what ESHTR's hierarchical design was constructed to avoid.

The adversarial paper states (§3.5) that cross-cluster C1-C5 comparison is "precisely the operation that ESHTR's hierarchical design was constructed to avoid." But ESHTR §3.1 frames the problem as unreliable rankings from *uncontrolled* direct cross-corpus comparison and provides the hierarchical structure as a solution that *confines* cross-cluster comparison to Phase 3 — not that eliminates it. The paper explicitly describes Phase 3 as "a cross-cluster championship tournament" (§3.3). Phase 3 IS the controlled cross-cluster comparison that ESHTR's design enables; it is not a repetition of the problem.

Horn 1's implied conclusion therefore does not follow. Under Horn 1:

- The criterion is the same in Phase 2 and Phase 3 (reasoning method quality). Accepted.
- Phase 3 applies this criterion cross-cluster. Accepted — this is by design.
- This "defeats ESHTR's design rationale." **Not accepted.** ESHTR's design rationale is to make cross-cluster comparison tractable by confining it to Phase 3, where it occurs in a constrained setting (champion-only population; explicit abstraction instruction; small k). Horn 1 describes Phase 3 accurately and is consistent with ESHTR.

The dilemma collapses because "Phase 3 = cross-cluster C1-C5 comparison" is the design's intended output, not a problem the design was meant to avoid. What ESHTR was constructed to avoid is uncontrolled, arbitrary cross-corpus pairings during the main ranking phase — which Phase 2 prevents by confining the bulk of comparison to within-cluster settings.

The remaining question — which the adversarial paper correctly identifies as empirical — is whether Phase 3's structured operationalization of cross-cluster C1-C5 comparison is materially more tractable (lower non-transitivity rate) than uncontrolled cross-cluster C1-C5 application. This is addressed in §4.5.

### 4.4 The Redundancy Objection Does Not Hold

The adversarial paper (§4) argues that if C1-C5 is necessarily domain-general, "the method can simply select the highest-aggregate-C1-C5 decision across all clusters" — making Phase 3 redundant.

Selecting the highest-aggregate-C1-C5 decision across all clusters is not a trivially available operation. It requires cross-cluster comparison of C1-C5 scores — exactly the operation that generates non-transitivity and for which ESHTR's hierarchical structure exists. There is no procedure that produces a global C1-C5 ranking without cross-cluster comparison; Phase 3 is that procedure, structured to reduce the non-transitivity it cannot eliminate. The necessary-implication claim (high C1-C5 → generalizable reasoning method) does not make Phase 3 redundant; it supplies the theoretical grounding for what Phase 3 is trying to identify. Phase 3 remains structurally necessary for the same reason that motivated the hierarchical design.

### 4.5 Why Phase 3's Operationalization Is More Tractable: The Mechanism

The adversarial paper correctly requires empirical evidence that Phase 3 comparisons under the explicit abstraction instruction exhibit lower non-transitivity than unconstrained cross-cluster C1-C5 comparison. A mechanism-level argument establishes the prior.

The Tversky (1977) feature-salience account, accepted by both the adversarial paper and `yesindeed/frame-stability-sph.md` as the correct mechanism for frame-instability-based non-transitivity, identifies what feature salience depends on: the comparison frame. In unconstrained cross-cluster C1-C5 evaluation, the comparison frame is implicit — set by the items themselves. The most salient discriminating features between a criminal sentencing decision and a tax injunction ruling are the domain-specific content features, because those differ most between the items, and they are highly present in the text LLM judges read.

The explicit abstraction instruction in Phase 3 ("abstract from subject-specific vocabulary to underlying argumentation quality," §3.3 ESHTR) functions as a frame-setting mechanism: it names the discrimination axis. Under Tversky's (1977) feature-salience account, this should reduce the salience of domain-specific content features by directing attention to the structural features the instruction specifies — reasoning coherence, argument engagement, non-formulaic application of principles. These are the domain-general features that C1-C5 is designed to target.

The instruction does not eliminate domain-specific feature salience (the decisions' texts still contain it), but it changes the comparison frame from implicit (dominated by the most content-distinctive features) to explicit (directed toward method-quality features). This is the mechanism by which "at a higher level of abstraction" does additional work: it specifies the suppression of domain-specific feature salience as the operationalization strategy, grounded in the same mechanism both sides have accepted. An explicit instruction and an implicit frame do not produce the same comparison, even when the underlying criterion is identical.

The adversarial paper's claim that the middle position is unstable — "if it changes what the LLM judge evaluates, the criterion is different; if it does not change what the judge evaluates, the design offers no advantage" — conflates criterion with operationalization. An instruction can change which features are most salient in the evaluation (the operationalization) without changing what is ultimately being evaluated (the criterion: reasoning method quality). This is a difference between what is assessed and how it is accessed. Instructions that change operationalization without changing criterion are standard in evaluation design.

Whether this theoretical prior is confirmed requires the empirical test the adversarial paper specifies: Phase 3 non-transitivity rates compared to Phase 2 cross-cluster non-transitivity rates under C1-C5, while checking that Phase 3 rankings correlate with Phase 2 cluster-quality rankings within each cluster. The mechanism argument supports the prediction; the test would confirm or disconfirm it.

The adversarial paper (§3.6) has accepted the mechanism argument as providing a "theoretical prior" for Phase 3 tractability, characterizing the prediction as "a mechanism-grounded conjecture that generates a falsifiable prediction... of the same logical type as the Semantic Proximity Hypothesis for Phase 2." This acceptance is significant: the adversarial paper is no longer arguing that Phase 3 tractability is improperly asserted without theoretical grounds, or that the position paper presents it as an architectural guarantee. The adversarial paper's remaining claim is that the mechanism argument does not establish "sufficiency." In the position paper context, no mechanism-grounded conjecture establishes sufficiency before the experiment — that is what experiments are for. Phase 2's Semantic Proximity Hypothesis is in the same position: the mechanism argues it should hold; the experiment confirms or disconfirms it. If the adversarial paper accepts SPH as a warranted prediction at the mechanism-grounded level while pressing the "not sufficient" objection specifically against Phase 3, the asymmetric treatment requires justification. That justification must show Phase 3's mechanism claim depends on an LLM behavior (instruction-modulated structural reading) that is structurally less warranted than Phase 2's mechanism claim (domain-specific criterion mapping from training). The adversarial §§3.7-3.8 attempt this. Whether the attempt succeeds depends on whether the representation/output distinction this defense establishes in §4.6 is adequate — and the calibration protocol in §4.6 specifies the test that would confirm or disconfirm this distinction's practical efficacy.

### 4.6 Method/Content Inseparability Is Not Exhaustive

The adversarial paper's Options (a) and (b) for how LLM judges implement C1-C5 are not exhaustive. A third option:

**(c)** LLM judges evaluate the **structure** of reasoning using domain-specific material as evidence, without evaluating the domain-specific content itself as a criterion component. Identifying whether a passage constitutes load-bearing grounds for a decision (C1) requires recognizing logical dependency relationships, not mastery of the specific doctrine. A reader without Brazilian criminal sentencing expertise can assess whether a passage logically necessitates the conclusion or constitutes elaboration. The domain vocabulary is text to be read for structural properties, not a domain knowledge base to be evaluated against.

This is the mode in which comparative law scholars evaluate foreign decisions: they identify ratio structure, coherence of argument engagement, and departure from formula without evaluating whether the specific doctrine is correct. The Phase 3 instruction explicitly positions LLM judges in this mode: abstract from domain vocabulary to argumentation quality.

Option (c) is neither a domain-agnostic template (it reads domain-specific text carefully) nor domain-sensitive evaluation (it does not assess doctrinal correctness). The adversarial paper's dichotomy between these two options misses the third, which is what a careful implementation of Phase 3's rubric aims to produce.

The adversarial paper's failure condition — "If the practical implementation of 'contextual generalizability' in the LLM judge prompt fails to separate content-transferability from reasoning-quality-transferability... the conceptual argument is sound but the implementation does not capture it" — is correctly identified as a prompt-engineering concern. It is a concern, but not a demonstration that the separation is impossible. It is addressable by explicit instruction: evaluate the method of reasoning, not the domain-specific rules applied. This is a tractable calibration problem, not a structural impossibility.

The adversarial paper (§3.7, updated) grounds a further counter in the accepted mechanism. The domain-specific criterion acquisition that produces within-cluster LLM reliability — described in `yesindeed/frame-stability-sph.md` §3.3 as the mechanism by which LLMs evaluate criminal law decisions on criminal law criteria — creates the implementation gap Option (c) must bridge. The Phase 3 instruction to "abstract from subject-specific vocabulary" changes what the LLM claims to evaluate; it does not sever, in the LLM's weights, the associations between domain-specific textual features and the quality criteria those features activate. The mechanism that produces within-cluster reliability and the mechanism that Option (c) must override are, on this account, one and the same.

This counter identifies a genuine implementation challenge. What it does not establish is that representation-level feature activation necessarily flows through to output-level criterion application. These are separated in instruction-tuned LLMs by the instruction-following mechanism that is the defining property of such models. An instruction-following model may activate domain-specific representations when reading criminal sentencing text — recognizing sentencing framework vocabulary, proportionality doctrine, precedential structure — while producing output that reports on the structural properties the instruction specifies, because the instruction modulates the mapping from activated representations to generated output. Instruction-tuning optimizes precisely this mapping: producing outputs consistent with explicit task specification on top of whatever representations are activated by the input. The adversarial argument conflates representation-level feature activation with output-level criterion application as though no instruction-following layer intervenes.

Additionally, Option (c) does not require suppression of domain-specific feature activation. Under Option (c), domain-specific textual features are read as evidence for structural properties — ratio identification, argument engagement quality, precedent application rigour — not as evaluation targets in themselves. The domain-specific vocabulary is the material through which structural properties are assessed, not an obstacle to their assessment. Readers in structural-reading mode activate domain-specific representations to identify the logical dependencies and argument structures that constitute the structural evidence. This is not suppression; it is redirection of what the activated representations serve as evidence for. The adversarial paper treats domain-specific activation and structural-reading mode as incompatible; they are complementary under Option (c).

The calibration gap is real: the current ESHTR calibration protocol (§5.4) does not include a Phase 3-specific test for whether LLM outputs under the abstraction instruction reflect structural rather than domain-specific criterion application. The test is implementable within the existing framework and can be made concrete.

Using decisions from the within-cluster calibration block (§5.4 of ESHTR), which establishes known quality rankings within each cluster, construct a set of **cross-cluster calibration pairs**: decisions from different domain clusters, matched approximately on quality level (both high-quality or both lower-quality, as established by their within-cluster calibration rankings). For each cross-cluster pair, run two evaluation conditions with the same LLM panel:

*Phase 2 condition:* Standard Phase 2 domain-specific rubric (C1-C5, no cross-domain abstraction instruction). Collect per-criterion scores for both decisions and pairwise preference judgments.

*Phase 3 condition:* Phase 3 abstraction instruction ("abstract from subject-specific vocabulary to underlying argumentation quality") applied to the same pair. Collect per-criterion scores and pairwise preference judgments.

Three measurements distinguish structural-reading mode from domain-criterion activation with leakage:

**(1) Cross-cluster κ shift.** Compare inter-judge agreement (Fleiss' κ) across the LLM panel for cross-cluster pairs under Phase 3 versus Phase 2 conditions. If the instruction redirects evaluation toward structural method properties that generate more consistent cross-judge assessments when made explicit, κ should be higher under Phase 3 conditions. *Falsified if:* κ_Phase3\_cross ≤ κ_Phase2\_cross across the calibration set.

**(2) Criterion-profile cross-domain variance.** For each cross-cluster pair, compare the variance of per-criterion score profiles across the two domain decisions under Phase 2 versus Phase 3 conditions. Domain-specific criterion activation (the adversarial claim) drives larger score gaps between decisions from different domains because domain-appropriate criteria differ across domains and penalize the out-of-domain decision. If Phase 3 instructions suppress this effect, per-criterion score variance across the two decisions should decrease under Phase 3 conditions relative to Phase 2 conditions, as both decisions are assessed on the same structural-method dimension. *Falsified if:* criterion-profile variance across domain decisions is not reduced under Phase 3 conditions.

**(3) Quality-discrimination accuracy on mixed-quality pairs.** Construct cross-cluster pairs where one decision ranks higher within its cluster than the other (quality-discrepant pairs). Under Phase 3 instructions, the higher-quality decision should win more often than under Phase 2 instructions, because Phase 3 instructions calibrate the comparison to structural-method quality rather than domain-specific performance — enabling the cross-domain quality distinction that Phase 2 instructions cannot reliably produce. *Falsified if:* winner-accuracy for quality-discrepant cross-cluster pairs is not higher under Phase 3 instructions than Phase 2 instructions applied to the same pairs.

The third measurement directly addresses the adversarial paper's "not sufficient" concern: quality-discrimination accuracy across domains is a direct measure of whether the structural-reading mode produces reliable cross-domain quality distinctions, not only improved inter-judge agreement. If Phase 3 instructions produce higher accuracy on quality-discrepant cross-cluster pairs, the instruction demonstrates the behavioral effect that the adversarial paper characterizes as an aspiration.

To satisfy the adversarial paper's surrender condition §6(3) — which requires evidence that non-transitivity reduction in Phase 3 is attributable in part to the instruction's frame-setting function, not entirely to champion selection — the calibration set should include **non-champion cross-cluster pairs** (decisions that competed but did not win within their clusters) alongside champion pairs. If Phase 3 instructions improve cross-cluster κ on non-champion pairs, the instruction's independent contribution is demonstrated independently of champion-selection effects. *Falsified if:* Phase 3 instruction conditions show no κ improvement over Phase 2 instruction conditions on non-champion cross-cluster pairs, which would indicate that whatever Phase 3 advantage exists is attributable entirely to the champion population's properties rather than the instruction's frame-setting function.

This protocol is implementable within the existing ESHTR evaluation framework: it reuses existing calibration decisions (augmented with cross-cluster pairings), the existing LLM panel infrastructure, and existing metrics (Fleiss' κ, per-criterion scores). The within-cluster quality rankings required to construct matched cross-cluster pairs are produced by the Phase 2 calibration block already in the protocol. The cross-cluster calibration component is an extension of the existing Phase 2 calibration block, applied to cross-domain pairs with an additional instruction condition — no new infrastructure is required.

### 4.7 Champion Legitimacy Is Supported by Aggregation Robustness

The adversarial paper's champion-circularity concern (§3.7) depends on within-cluster criterion-switching being systematic and directional — consistently advantaging specific items over others in criterion activation. If within-cluster criterion-switching is non-systematic, Bradley-Terry aggregation over the full distribution of pairings produces a valid quality signal even with some criterion-switching in individual pairings.

As analyzed in `yesindeed/frame-stability-sph.md` (§3.5): within-cluster criterion-switching that is non-systematic contributes variance to individual pairings without introducing directional bias against any specific item into the aggregate score. The champion is the decision that wins most pairings across the distribution of criteria activated within the cluster — a signal that averages across criterion activation rather than being determined by which criterion any single pairing happens to activate. This is the structural advantage of Bradley-Terry aggregation over individual pairings.

The circularity concern holds only if within-cluster criterion-switching is systematically correlated with specific item identities — some items consistently trigger the "losing" criterion in their pairings. Prediction 4 from `yesindeed/frame-stability-sph.md` (§3.4) addresses this: within-cluster non-transitive cycles should be unstructured relative to quality-dimension asymmetry profiles if switching is non-systematic; if cycles concentrate at asymmetry boundaries (items with extreme profiles generating cycles more frequently), switching is systematic. Until that structural test indicates directional within-cluster switching, the circularity concern is a possibility rather than an established failure mode, and Bradley-Terry champions are a reasonable quality signal.

The adversarial paper (§3.8) presents a second argument concerning the champion population, distinct from the circularity concern. Even granting that Phase 2 champions are genuine quality peaks, the structural controls do not stabilize Phase 3 because sophisticated domain-integrated reasoning has domain-general and domain-specific method most tightly intertwined. Among champion decisions — selected precisely for the excellence with which they integrate method and content — the method/content separation that Phase 3's structural-reading mode requires is most difficult to achieve. Determining which champion's method is "more transferable," the adversarial paper argues, requires cross-domain bridging that generates non-transitivity precisely among the most sophisticated and domain-integrated examples of legal reasoning.

The argument's premise is correct: in high-quality champion decisions, domain-general reasoning method is expressed through domain-specific doctrinal material in a fully realized way. The implied conclusion — that this intertwining makes structural evaluation harder — does not follow.

Tight integration of method and content makes structural properties more legible in the decision's text, not less. A champion decision that integrates proportionality analysis, ratio isolation, and precedential reasoning at a high level produces a text in which the logical dependencies between claims, the thoroughness of argument engagement, and the rigour of precedent application are extensively exhibited across multiple paragraphs. Structural properties are most visible in decisions where those properties are most fully exercised. By contrast, structural deficiencies are harder to identify in formulaic decisions, because formulaic language conceals whether genuine reasoning occurred. In champion decisions with tight method/content integration, the structural operations that Phase 3 evaluates are demonstrated through the richness of the domain-specific material — providing more, not less, evidence for Option (c)'s structural-reading evaluation.

The "cross-domain bridging that generates non-transitivity" claim also requires examination. What Phase 3 compares is the structural quality of reasoning operations — ratio isolation, argument engagement quality, precedent application — expressed through different domain-specific vocabularies. These operations are domain-general in form (§4.1). The comparison does not ask which champion's domain-specific doctrinal reasoning is superior; it asks which champion's structural reasoning operations are of higher quality as evidenced by domain-specific text. Under the Tversky (1977) feature-salience account, criterion switches in cross-cluster comparisons arise when domain-specific features are the most discriminating dimensions between the compared items, activating different criterion sets across pairings. When the Phase 3 instruction successfully redirects comparison to structural quality — the mechanism-level argument in §4.5 — the most discriminating features between champion decisions are properties of the structural operations they demonstrate, not their domain vocabularies. Criterion-switching at the structural-quality level requires that champions differ more on structural operational quality than on domain-specific content features, which is a less severe cross-cluster switching problem than the unconstrained version. Whether the instruction successfully effects this redirection is, again, the empirical question surrender condition §6(3) addresses.

### 4.8 Non-Transitivity Recurrence Is Attenuated

Phase 3's champion-only population, explicit abstraction instruction, and small k jointly attenuate the criterion-switching mechanism relative to arbitrary cross-cluster comparison. The adversarial paper concedes this is attenuation, not elimination. The mechanism-level argument in §4.5 adds: the attenuation is not ad hoc — it operates through a specific causal pathway (instruction-modulated feature salience, per the Tversky 1977 account) that both sides have accepted as the mechanism for frame-instability-based non-transitivity.

Whether the attenuation is sufficient is the empirical question. The adversarial paper's updated surrender condition §6(3) — evidence that Phase 3 non-transitivity rates are substantially lower than Phase 2 cross-cluster non-transitivity rates while Phase 3 rankings correlate with Phase 2 quality rankings — is the right test. The defense does not claim to provide that evidence; it provides the theoretical basis for why the prediction should be confirmed, and identifies the test that would confirm or disconfirm it.

---

## 5. Scope of This Defense

This paper defends the coherence of ESHTR's global ranking against the criterion-substitution attack, the non-transitivity-recurrence attack, the structural dilemma, the method/content-inseparability argument (including the mechanism-based counter to Option c in §3.7 of the adversarial paper), the champion-circularity argument, and the champion-intertwining argument (§3.8, second argument) from the current version of `otherwise/eshtr-phase3-gap.md`.

This paper does **not** address:

- The Phase 2 operationalization attack (Sections 3.1–3.4 of the adversarial paper) — addressed in `yesindeed/frame-stability-sph.md`.
- The empirical question of whether Phase 3 non-transitivity rates are in fact lower than Phase 2 cross-cluster non-transitivity rates. The defense provides theoretical grounds for why they should be and a calibration protocol (§4.6) that would provide preliminary evidence on whether the instruction-following mechanism achieves the postulated behavioral effect; the full ESHTR experimental protocol remains the required validation test.
- The global ranking's completeness: decisions eliminated in Phase 2 are absent from Phase 3. The defense argues the ranking is *coherent* (Phase 3 applies the same underlying criterion as Phase 2), not *complete*.

---

## 6. Conditions Under Which This Defense Would Fail

- If empirical measurements show Phase 3 non-transitivity rates ≥ Phase 2 cross-cluster non-transitivity rates under C1-C5 (the adversarial paper's updated surrender condition §6(3)), the attenuation argument and the operationalization-tractability claim both fail.
- If Phase 3 rankings are poorly correlated with Phase 2 quality rankings within each cluster — i.e., moderate C1-C5 scorers systematically beat cluster champions under contextual generalizability — the claim that both phases measure the same underlying property is empirically disconfirmed.
- If Prediction 4 from `yesindeed/frame-stability-sph.md` (§3.4) confirms systematic, directional within-cluster criterion-switching, the champion-legitimacy argument fails: Phase 2 champions may not be valid quality proxies, and the champion-population advantage of Phase 3 dissolves.
- If the practical implementation of Phase 3's rubric fails to separate reasoning-structure evaluation from domain-content evaluation — if LLM judges under the abstraction instruction consistently penalize domain-specific vocabulary rather than abstracting to structural quality — Option (c) in §4.6 is not realized, and the method/content inseparability concern becomes a binding implementation failure.
- If the Phase 3-specific calibration protocol in §4.6 shows that per-criterion score profiles under the abstraction instruction do not shift relative to Phase 2 domain-specific profiles — the same criterion emphasis patterns appear regardless of the instruction — the representation/output-mapping distinction in §4.6 fails to hold for the LLM panel used, and the instruction-following defense of Option (c) is empirically disconfirmed. Specifically: if (a) cross-cluster κ under Phase 3 instructions does not exceed cross-cluster κ under Phase 2 instructions, (b) criterion-profile variance across domain decisions does not decrease under Phase 3 instructions, and (c) winner-accuracy for quality-discrepant cross-cluster pairs is not higher under Phase 3 instructions — all three conditions met — Option (c) is not the LLM's achieved behavior under the Phase 3 rubric.
- If the calibration protocol shows no instruction-independent κ improvement on non-champion cross-cluster pairs (i.e., any Phase 3 advantage is attributable entirely to champion-selection, not to the instruction's frame-setting function), the mechanism-level argument for the instruction's contribution in §4.5 is empirically disconfirmed, though the champion-population argument for Phase 3 may still hold partially.

---

## References

- Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking. `embedding_seeded_tournament_paper.md` (this repository).
- `otherwise/eshtr-phase3-gap.md` — "Embedding Proximity Is Not Evaluative Frame Stability: A Challenge to ESHTR's Core Design Rationale" (adversarial paper, this repository).
- `yesindeed/frame-stability-sph.md` — "Frame Stability and the Semantic Proximity Hypothesis: A Cognitive Mechanism for Non-Transitivity in LLM Judges" (this repository).
- Tversky, A. (1969). Intransitivity of preferences. *Psychological Review*, 76(1), 31–48.
- Tversky, A. (1977). Features of similarity. *Psychological Review*, 84(4), 327–352.
- Verga, P. et al. (2024). Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models. *NAACL 2024*.
- Xu, Y., Ruis, L., Rocktäschel, T., and Kirk, R. (2025). Investigating Non-Transitivity in LLM-as-a-Judge. *ICML 2025 Spotlight*. arXiv:2502.14074.
