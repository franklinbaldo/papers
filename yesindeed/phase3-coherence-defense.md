# Phase 3 Is Not a Criterion Substitution: On the Coherence of ESHTR's Global Ranking

---

## 1. Thesis Supported

Baldo (2025), "Embedding-Seeded Hierarchical Tournament Ranking" (ESHTR), Section 3.3, proposes that Phase 3 of the method conducts a cross-cluster championship tournament using the same LLM panel and rubric as Phase 2, with one modification: an additional criterion for **contextual generalizability** — "whether the reasoning quality evident in the decision would transfer to adjacent subject matters."

The implicit claim in the design is that this produces a **unified global quality ranking**: a single ordering of judicial decisions that is coherent with the Phase 2 domain-specific rankings.

This paper responds to the attack in `otherwise/eshtr-phase3-gap.md` (Sections 3.4 and 3.5), which argues that (a) the addition of "contextual generalizability" substitutes a categorically different criterion for C1-C5, making the global ranking incoherent, and (b) contextual generalizability is itself more susceptible to non-transitivity than C1-C5. The defense is that both arguments rest on a mischaracterization of what C1-C5 measures and of the relationship between domain-specific quality indicators and domain-general reasoning quality.

---

## 2. What This Support Adds

**Vector:** Direct defense. The adversarial paper in `otherwise/eshtr-phase3-gap.md` attacks Phase 3 coherence with two independent arguments. This paper reconstructs both arguments charitably and responds to each on its own terms.

---

## 3. Reconstructing the Attack

### 3.1 The Criterion Substitution Argument

The adversarial paper's argument has the following structure:

1. Phase 2 ranks decisions by criteria C1-C5, anchored to domain-specific procedural standards (art. 489, §1º; art. 927; art. 1.022 CPC).
2. Phase 3 adds "contextual generalizability" — whether reasoning quality would transfer across domains — as the tiebreaking criterion for cross-cluster comparison.
3. C1-C5 and contextual generalizability are incommensurable: a decision that is highest-quality in its cluster under C1-C5 may score poorly on contextual generalizability because it applies technical statutory formulas specific to its domain.
4. Therefore, combining Phase 2 cluster rankings with Phase 3 contextual-generalizability rankings produces a composite ranking, not a unified quality ordering.
5. A decision eliminated in Phase 2 may be globally superior under any unified standard, but is invisible in the final ranking.

### 3.2 The Non-Transitivity Recurrence Argument

The adversarial paper further argues that contextual generalizability requires an LLM judge to assess "whether reasoning quality would transfer to adjacent subject matters" — precisely the kind of cross-contextual judgment that Section 4 of ESHTR identifies as susceptible to non-transitivity. The criterion that Phase 3 adds to handle cross-cluster non-transitivity is, on this account, subject to the same mechanism that generates it.

---

## 4. The Defense

### 4.1 C1-C5 Are Indicators of Reasoning Method, Not Domain-Specific Content

The adversarial paper treats C1-C5 as domain-specific criteria. The text of those criteria does not support this reading.

- **C1** (art. 489, §1º, V): does the decision identify the *determining grounds* (*fundamentos determinantes*) of invoked precedents? This is a test of whether the judge correctly isolated the ratio — the holding that generalizes from the specific case — from obiter dicta. Identifying the ratio of a precedent requires abstracting from the case's specific facts to the legal principle the precedent establishes. This is inherently a reasoning operation that applies across criminal law, tax law, and administrative law in the same form.

- **C2** (art. 489, §1º, IV): does the decision address arguments *capable of affecting the outcome*? This is a test of whether the judge engaged with material arguments rather than deflecting them. The criterion does not specify what kinds of arguments count; it tests the cognitive operation of identifying and engaging with the strongest challenge to the holding. That operation has the same form in every domain.

- **C3** (art. 489, §1º, III): does the decision avoid generic boilerplate? Generic formulas — stock phrases that could appear in any decision without modification — are the opposite of contextually sensitive reasoning. A decision that avoids them has, by definition, applied reasoning that is specific to its argument structure, not borrowed from a domain-specific formula bank.

- **C4** (art. 927, §1º): is the binding precedent correctly applied, distinguished, or justified in deviation? Correct application requires understanding why the precedent holds — its underlying principle — not just what it says. That understanding is what enables the judge to apply the precedent when facts differ slightly, to distinguish it when they differ substantially, and to justify deviation when the ratio is wrong. This cognitive operation — principled abstraction from precedent to holding to application — has the same form regardless of subject matter.

- **C5** (art. 1.022): is the dispositif free of obscurity, contradiction, and omission? This is a completeness and logical coherence criterion. It is entirely domain-agnostic.

The pattern is consistent. C1-C5 test whether a judge applied the legal reasoning *method* correctly: isolating ratio, engaging material arguments, avoiding formulaic shortcuts, abstracting the right principle from precedent, producing a coherent device. These are domain-general cognitive operations, tested through domain-specific instantiations.

A decision that scores highly on C1-C5 is one that demonstrates reasoning quality in its domain by applying a reasoning method that would, by its nature, produce quality reasoning in adjacent domains. A judge who correctly identifies the ratio of a criminal sentencing precedent (C1) and applies it with genuine proportionality analysis (C4), avoiding stock sentencing formulas (C3), is demonstrating a reasoning method — principled abstraction, criterion-sensitive application, engagement with material arguments — that is the same method that produces quality reasoning in tax, administrative, or contract law.

### 4.2 The Adversarial Paper's Key Counterexample Is Refuted

The adversarial paper writes: "A criminal sentencing decision that is the highest-quality decision in its cluster under C1–C5 may score poorly on 'contextual generalizability' because criminal sentencing employs technical statutory formulas specific to the Código Penal that do not transfer to adjacent domains."

This example conflates two different claims:

- **Claim A (content-transferability):** The specific statutory rules in the decision (art. 59, art. 68 CP, the doctrine of *bis in idem* applied to aggravating factors) transfer to other domains. This is false; criminal sentencing doctrine is domain-specific.

- **Claim B (reasoning-quality-transferability):** The *method of reasoning* demonstrated in the decision — the way the judge applies the proportionality framework, isolates the relevant ratio from prior cases, engages with the defendant's arguments rather than dismissing them with formulas — would be recognizable as reasoning quality in other domains. This is what ESHTR's Phase 3 criterion actually tests.

The ESHTR paper's criterion asks whether "the reasoning quality evident in the decision would transfer to adjacent subject matters" (§3.3, emphasis added). This is not a question about whether criminal law rules apply in tax law. It is a question about whether the *quality of reasoning* — the method, the rigor, the engagement — would produce a high-quality decision in another domain. A judge who reasons correctly in criminal law, in the C1-C5 sense, is a judge who would reason correctly in administrative law.

The counterexample therefore fails: the domain-specific content of a high-C1-C5 criminal sentencing decision does not transfer, but the reasoning quality that generated the high score does.

### 4.3 Contextual Generalizability Is Not an Additional Criterion; It Is an Operationalization of C1-C5 Quality at Scale

Sections 4.1 and 4.2 together establish that a decision scoring highly on C1-C5 is one whose reasoning quality is, by the nature of what C1-C5 measures, domain-generalizable. The "contextual generalizability" criterion in Phase 3 is therefore not a substitute for C1-C5; it is the natural question to ask when comparing champions across domains: which of these high-C1-C5 decisions demonstrates reasoning quality in a form most transferable across the different domains being compared?

This is not an incommensurable criterion. It is the same criterion (reasoning method quality) applied at a higher level of abstraction. Phase 2 asks: is this the best reasoning in domain D? Phase 3 asks: among the best reasoners from each domain, which demonstrates reasoning quality that is most visible as such across domain boundaries? Both questions are answered by reference to the same underlying property: quality of reasoning method.

The adversarial paper's surrender condition #2 (§6) states: "If the author can demonstrate that 'contextual generalizability' is a component of quality already measured by C1–C5 — specifically, that a decision scoring highly on C1–C5 is necessarily one whose reasoning generalizes — the Phase 3 criterion substitution does not change the evaluation objective." The argument in §§4.1–4.2 above is that demonstration.

### 4.4 The Non-Transitivity Recurrence Argument Does Not Apply

The adversarial paper argues that "contextual generalizability" assessments require bridging different contextual frames and are therefore susceptible to the same non-transitivity mechanism identified in ESHTR §4. This argument applies to arbitrary cross-domain pairings. It does not apply to Phase 3's specific population with the same force.

Phase 3 comparators are cluster champions: decisions that have demonstrated, through the Phase 2 tournament, that their reasoning quality under C1-C5 is the highest in their domain. This population is dramatically less heterogeneous than the full cross-domain corpus. All Phase 3 comparators share the property of exemplifying domain-specific reasoning quality. The evaluative frame for "which champion has more transferable reasoning quality" has a stable reference point — C1-C5 quality — that arbitrary cross-domain comparisons lack.

The frame-stability mechanism (documented in `yesindeed/frame-stability-sph.md` via the Tversky contingent-weighting literature) predicts that evaluative instability arises when compared items activate incompatible criterion sets. For Phase 3 champion-vs-champion comparison, the criterion set is constrained: the LLM judge is specifically instructed to abstract from domain-specific vocabulary to underlying reasoning quality. The comparison frame is thus explicitly anchored, not left implicit as in the unconstrained cross-domain comparisons that generate non-transitivity.

Additionally, k (the number of Phase 3 comparators) is small (5-20 in the protocol described). The scope for non-transitive cycles scales with the number of comparators; with k = 10, the number of triples is C(10,3) = 120, manageable for a tournament that explicitly randomizes ordering and uses a multi-model panel. Non-transitivity remains possible but is structurally less severe than in the full corpus.

None of this eliminates non-transitivity from Phase 3. The adversarial paper is correct that the mechanism can still operate. The defense is that Phase 3's design (constrained criterion instruction + champion-only population + small k) substantially attenuates the mechanism compared to arbitrary cross-domain comparison, and that the attenuation is principled rather than ad hoc.

---

## 5. Scope of This Defense

This paper defends the coherence of ESHTR's global ranking against the criterion-substitution and non-transitivity-recurrence attacks in `otherwise/eshtr-phase3-gap.md` Sections 3.4 and 3.5.

This paper does **not** address:

- The Phase 2 embedding-proximity attack (Sections 3.1-3.3 of the adversarial paper), which is addressed separately in `yesindeed/frame-stability-sph.md`.
- The empirical question of whether Phase 3 contextual-generalizability rankings actually correlate with C1-C5 quality rankings from Phase 2. The conceptual argument in §4.1-4.3 establishes that they should, but this is a prediction, not a measured outcome. If experiments show Phase 3 champions systematically diverging from Phase 2 quality (e.g., moderate C1-C5 scorers beating cluster champions under contextual generalizability), the conceptual argument requires revision.
- The global ranking's completeness: a decision eliminated in Phase 2 is absent from Phase 3. The defense above argues the global ranking is *coherent* — Phase 3 uses the same quality criterion as Phase 2 — but does not argue it is complete. The adversarial paper is correct that a Phase 2 second-place decision may be globally superior in some respects; this is a structural consequence of any hierarchical tournament, not specific to ESHTR.

---

## 6. Conditions Under Which This Defense Would Fail

- If empirical experiments show that Phase 3 rankings and Phase 2 quality rankings are poorly correlated — i.e., that the champion identified by "contextual generalizability" is systematically a decision with middling C1-C5 scores, not the domain's highest-quality decision — the conceptual argument fails. The test is whether Phase 3 winners are also near the top of Phase 2 rankings when evaluated on C1-C5 within their own clusters.
- If the practical implementation of "contextual generalizability" in the LLM judge prompt fails to separate content-transferability from reasoning-quality-transferability — if judges systematically penalize domain-specific content rather than assessing reasoning method — the conceptual argument is sound but the implementation does not capture it. This is a prompt engineering concern, addressable by explicit instruction ("evaluate the method of reasoning, not the domain-specific rules applied").
- If the Phase 3 non-transitivity rate empirically exceeds Phase 2 non-transitivity rates (controlling for k), the attenuation argument in §4.4 fails, and the adversarial paper's recurrence concern is confirmed.

---

## References

- Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking. `embedding_seeded_tournament_paper.md` (this repository).
- `otherwise/eshtr-phase3-gap.md` — "Embedding Proximity Is Not Evaluative Frame Stability: A Challenge to ESHTR's Core Design Rationale" (adversarial paper, this repository).
- `yesindeed/frame-stability-sph.md` — "Frame Stability and the Semantic Proximity Hypothesis: A Cognitive Mechanism for Non-Transitivity in LLM Judges" (this repository).
- Tversky, A. (1969). Intransitivity of preferences. *Psychological Review*, 76(1), 31–48.
