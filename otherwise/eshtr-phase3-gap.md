# Embedding Proximity Is Not Evaluative Frame Stability: A Challenge to ESHTR's Core Design Rationale

---

## 1. Thesis Attacked

The paper "Embedding-Seeded Hierarchical Tournament Ranking" (Baldo, 2025;
`embedding_seeded_tournament_paper.md`) proposes that dense-embedding
clustering of judicial decisions before LLM-panel ranking reduces
non-transitivity by ensuring early-stage comparisons occur between
semantically similar decisions — "where we expect LLM judges to be more
reliable" (Abstract). The theoretical foundation is the **Semantic
Proximity Hypothesis**: that "the incidence of non-transitive preferences
in LLM judges is positively correlated with the semantic distance between
compared items" (Section 4).

The method's practical justification rests on this hypothesis. If semantic
proximity — as measured by embedding cosine similarity — predicts LLM judge
reliability, then clustering by embeddings produces groups within which
judges are reliably coherent, and the non-transitivity problem can be managed
by confining dangerous cross-domain comparisons to Phase 3.

---

## 2. Faithful Reconstruction

The strongest form of the argument now includes two independent theoretical
supports for the Semantic Proximity Hypothesis and a coherent account of
Phase 3's global ranking.

**Support 1 — Cognitive mechanism.** When an LLM judge compares two items A
and B, it constructs an implicit evaluative frame: a weighting of which
features are relevant and how much each matters. Tversky (1969) showed that
preference intransitivity arises not from random error but from systematic
criterion switches across pairs: an agent that applies criterion d₁ to
adjudicate A vs. B, d₂ for B vs. C, and d₃ for A vs. C can generate cycles
where each individual judgment is locally correct. Applied to LLM judges:
an LLM that has learned domain-specific criterion mappings from legal corpora
will weight evaluative features differently depending on the pair it is
comparing. Within a semantic cluster, items share the same subject matter,
vocabulary, and doctrinal framework, so the features that most discriminate
any given pair are drawn from the same constrained criterion set. Across
clusters, the discriminating features shift between pairs, generating cycles
even when each individual judgment is accurate under its own frame.

**Support 2 — Phase 3 coherence through method-level unity.** The defense
in `yesindeed/phase3-coherence-defense.md` argues that C1-C5 tests reasoning
*method*, not domain-specific *content*. Identifying a precedent's ratio
(C1), engaging material arguments (C2), avoiding generic boilerplate (C3),
applying precedents with genuine principled understanding (C4), producing a
coherent dispositif (C5) — these are domain-general cognitive operations,
tested through domain-specific instantiations. A judge who reasons correctly
in criminal law in the C1-C5 sense is a judge who would reason correctly in
administrative law, because the method is the same. "Contextual
generalizability" in Phase 3 is therefore not a substitute criterion; it is
the same reasoning-method quality criterion applied at a higher level of
abstraction. Phase 3 asks: among the cluster champions who each demonstrated
domain-quality reasoning, whose method is most visible as quality across
domain boundaries? Both phases answer to the same underlying property.

Under this account, the global ranking is coherent: every decision in the
combined ranking is ordered by the same property (quality of reasoning
method), at different levels of aggregation.

---

## 3. The Attack

### 3.1 What the Mechanism Actually Requires

The contingent frame construction account (Tversky 1969, 1977; as developed
in the supportive paper `yesindeed/frame-stability-sph.md`) identifies a
precise structural unit for non-transitivity risk: the **triple** {A, B, C}.
A cycle arises in a triple when the pair (A, B) is most discriminated on
criterion set S₁, the pair (B, C) on S₂, and the pair (A, C) on S₃, with
S₁, S₂, S₃ not all equal. The mechanism is triple-level, not pair-level.

ESHTR's Phase 1 clustering controls pairwise semantic distance. The resulting
clusters group items that are similar to each other in embedding space. But
grouping by pairwise similarity does not guarantee triple criterion-consistency.
A set of three items {A, B, C} can all fall within a single high-density
cluster — mutually similar in embedding space — while still forming a
criterion-switching triple if A and B are most differentiated on one quality
dimension, B and C on a second, and A and C on a third.

The mechanism-operationalization gap is therefore not merely that embeddings
track topic proximity rather than evaluative frame stability (the point of
the original attack). It is more specific: *even if embedding proximity
perfectly predicted pairwise frame affinity, that would not prevent
criterion-switching cycles arising from within-cluster variation across
quality dimensions*. The mechanism demands triple-level criterion homogeneity,
and pairwise clustering cannot deliver it.

### 3.2 The Within-Cluster Stability Claim Is Asserted, Not Derived

The supportive paper (`yesindeed/frame-stability-sph.md`, Section 3.2)
argues:

> "Within a semantic cluster, items share subject matter, structural
> conventions, vocabulary, and domain-specific reasoning standards. The
> features that meaningfully discriminate one item from another within the
> cluster are drawn from a constrained, shared repertoire... the comparison
> frame is stable within the cluster."

This argument moves from *shared feature repertoire* to *stable criterion
weighting across pairs*. The Tversky mechanism does not license this move.
Tversky's finding is that which features from the shared repertoire are most
*salient* — most discriminating — depends on the specific pair, not on the
repertoire. A shared repertoire with multiple quality dimensions is a
necessary condition for within-cluster stability, not a sufficient one.

Consider a cluster of administrative disciplinary decisions. Items in this
cluster share subject matter (administrative sanctions), vocabulary, and
doctrinal standards. Their shared feature repertoire includes:
thoroughness of fact-finding, coherence of proportionality reasoning,
and adequacy of procedural safeguard analysis. Decision A is excellent on
fact-finding but adequate on proportionality; decision B is adequate on
fact-finding but excellent on proportionality; decision C is adequate on
fact-finding but excellent on procedural safeguards.

The triple {A, B, C} generates criterion-switching under the Tversky
mechanism: A vs. B is discriminated primarily on fact-finding (A wins);
B vs. C is discriminated primarily on procedural safeguards (B or C);
A vs. C is discriminated on a combination where C's procedural strength
may dominate. The criterion frame shifts across the three pairings even
though all three decisions are in the same embedding cluster. ESHTR's
Phase 2 Bradley-Terry ranking is designed precisely to resolve exactly
this kind of within-cluster comparison — but if the Bradley-Terry scores
are themselves determined by criterion-switching, the scores reflect which
criterion is most activated by the cluster's distribution of pairings,
not a stable underlying quality ordering.

This is not an exotic edge case. Legal corpora within any subject-matter
cluster are heterogeneous along multiple quality dimensions simultaneously.
The distribution of decisions along each dimension does not covary perfectly
with embedding distance. The supportive paper's stability claim would need
empirical support from the same ESHTR experimental protocol it is meant to
support — making the argument circular in the same way as the original.

### 3.3 The Mechanism Identifies a Better Operationalization

The Tversky mechanism, if accepted as the correct explanation for SPH,
implies that the relevant clustering unit is *criterion-set homogeneity
within triples*, not pairwise embedding proximity. An operationalization
aligned with the mechanism would cluster items such that any triple within
a cluster activates approximately the same criterion set across all three
pairings. This is a stronger property than pairwise embedding similarity,
and it requires knowing (or estimating) which quality dimensions are most
discriminating for which pairs — information not available from the
embedding model alone.

The supportive paper's contribution is to identify the mechanism clearly.
But a mechanism, once identified, also identifies what the operationalization
must track. Embedding proximity is a noisy proxy for pairwise semantic
context; pairwise semantic context is a noisy proxy for the pair's most
discriminating criterion set; and criterion-set consistency within pairs
is a necessary but not sufficient condition for criterion-set stability
across triples. The mechanism paper's grounding, accepted in full, reveals
that ESHTR's clustering addresses the first link in this chain while the
non-transitivity risk lives at the third link.

### 3.4 The Hypothesis Is Introduced Without the Evidence It Needs

Section 4 of ESHTR offers an "informal argument" and the mechanism paper
provides independent grounding. But neither establishes the critical
empirical claim: that the embedding clusters produced by
multilingual-e5-large-instruct (or fine-tuned variants) are sufficiently
criterion-homogeneous within triples to materially reduce non-transitivity.

The mechanism paper explicitly acknowledges that it provides plausibility,
not proof. The mechanism could be correct — criterion switching is the
source of non-transitivity — while the embedding-clustering operationalization
fails to control it adequately at the triple level. Whether the proxy is
good enough is an empirical question, and it requires tests beyond the
aggregate κ comparison specified in Section 5.5 of ESHTR. Specifically:
the ESHTR experiment would need to measure non-transitivity incidence *within
clusters*, not only compare within-cluster κ to cross-corpus κ, to reveal
whether residual within-cluster cycles are systematic.

### 3.5 Phase 3 Is Not Rescued by the Method/Content Distinction

The Phase 3 defense in `yesindeed/phase3-coherence-defense.md` concedes the
criterion-substitution framing but contests the premise: C1-C5 is not
domain-specific; it tests reasoning method, which is inherently
domain-general. Contextual generalizability is therefore not a substitute
criterion but an application of the same criterion at a higher level of
abstraction.

This argument is accepted in its conceptual form. C1-C5, read carefully, does
target domain-general operations: isolating the ratio from obiter dicta (C1),
engaging material arguments (C2), avoiding formulaic shortcuts (C3), applying
precedents through genuine principled understanding (C4), producing a coherent
dispositif (C5). These operations have a domain-general form.

Accepting this, however, reveals a structural problem that the defense does
not resolve: **the method/content unity argument is self-undermining as a
rationale for Phase 3's design**.

If C1-C5 is already measuring a domain-general property — reasoning method
quality, equally applicable in criminal, tax, and administrative law — then
Phase 3 comparisons are, by the defense's own account, comparisons of items
along the same underlying quality dimension that Phase 2 used. A cross-cluster
comparison of criminal and tax law champions under C1-C5 is not crossing
into incommensurable criteria; it is applying the same domain-general criterion
to items from different clusters. But then the Phase 3 comparison is a
*cross-cluster C1-C5 comparison* — precisely the operation that ESHTR's
hierarchical design was constructed to avoid, on the grounds that cross-cluster
LLM-panel evaluation produces non-transitive results (Section 4 of ESHTR).

The defense is therefore caught in a dilemma:

- **Horn 1:** If C1-C5 is domain-general (as the defense argues), then Phase 3
  comparisons under "contextual generalizability" are conceptually equivalent
  to cross-cluster C1-C5 comparisons. The design rationale for the hierarchical
  structure collapses: if comparing cluster champions on domain-general
  reasoning quality is the same operation as applying C1-C5 cross-cluster, the
  two-phase architecture provides no protection against the non-transitivity
  it was designed to prevent. Phase 3 is not a coherent next step; it repeats
  the problem Phase 2 was supposed to solve.

- **Horn 2:** If "contextual generalizability" is not simply C1-C5 applied
  cross-cluster — if it asks something additional, something that makes
  Phase 3 comparisons genuinely different from and more tractable than
  direct cross-cluster C1-C5 comparison — then the criterion is not the same
  as C1-C5. The criterion substitution stands.

The defense attempts to occupy a middle position: contextual generalizability
is C1-C5 "at a higher level of abstraction," distinct enough to anchor the
frame more stably than unconstrained cross-cluster comparison, but still the
same criterion. This middle position is unstable. What additional analytical
work does "at a higher level of abstraction" do? If it changes what the LLM
judge evaluates, the criterion is different; if it does not change what the
judge evaluates, the design offers no advantage over direct cross-cluster
application.

### 3.6 Method/Content Inseparability in LLM Implementation

The defense rests on a conceptual analysis of what C1-C5 should measure. The
question of what LLM judges *actually* track when instructed to apply C1-C5
to domain-specific legal documents is distinct.

Legal reasoning method is expressed through domain-specific doctrinal
categories. Identifying the *fundamentos determinantes* (ratio) of a criminal
sentencing precedent (C1) requires recognizing that, in criminal law, the
determining grounds of a sentencing ratio include the constitutional
proportionality framework, the application of mitigating and aggravating
factor categories, and the doctrinal structure distinguishing *pena-base* from
adjustments. These are not incidental to identifying the ratio; they are how
the ratio is constituted in this domain. An LLM judge that applies C1 "at the
level of reasoning method" either:

(a) applies domain-specific legal knowledge to identify the ratio through its
domain-specific doctrinal structure — in which case the C1 score is sensitive
to domain content in precisely the way the defense denies, or

(b) applies a domain-agnostic template ("which elements of the judgment are
the ones that logically necessitate the outcome?") that may miss
domain-specific elements that are, in fact, load-bearing for the ratio's
correct identification.

Option (a) means C1-C5 scores are domain-sensitive in practice, even if the
criteria are domain-general in formulation. Option (b) means C1-C5 scores
track a generic logical-coherence dimension that loses the doctrinal precision
that makes the criteria useful as legal quality assessors in the first place.
Neither option supports the defense's claim that C1-C5 is domain-general in
its implementation without loss of validity.

The defense acknowledges this in its failure conditions: "If the practical
implementation of 'contextual generalizability' in the LLM judge prompt fails
to separate content-transferability from reasoning-quality-transferability...
the conceptual argument is sound but the implementation does not capture it."
This framing treats the implementation gap as a peripheral prompt-engineering
concern. It is not peripheral; it is the central empirical question for both
Phase 2 and Phase 3 coherence.

### 3.7 The Champion Population Argument Does Not Stabilize Phase 3

The defense argues that Phase 3 comparators — cluster champions — are a more
homogeneous population than arbitrary cross-domain pairs, because all
champions share the property of domain-reasoning-quality excellence. This
reduces the frame-instability mechanism's operation.

Two problems.

First, whether a decision is a "cluster champion" depends on Phase 2's
tournament ranking, which the attack in Sections 3.1-3.2 argues may itself
be driven by within-cluster criterion-switching. A tournament ordered by
criterion-switching cycles does not reliably identify the highest-quality
decision in each cluster; it identifies the decision that wins the specific
pairings the tournament arranges. The champion may not be the highest-quality
decision under any stable quality standard. The champion population's supposed
homogeneity (all are domain-quality exemplars) cannot be guaranteed by a
process that may itself be non-transitive.

Second, even granting that champions genuinely represent domain-quality peaks,
the question "whose reasoning quality transfers most across domains?" requires
the LLM judge to bridge criterion sets across the compared champions' domains.
A criminal law champion and a tax law champion both demonstrate domain
excellence. Determining which champion's *method* is "more transferable" asks
the judge to compare the generalizability of two different high-quality
reasoning styles — precisely the kind of cross-domain bridging that the
contingent frame-construction mechanism identifies as the source of
non-transitivity. The champion population's shared excellence does not
eliminate the criterion-switching problem; it concentrates it among the most
sophisticated and domain-integrated examples of legal reasoning, where
domain-general and domain-specific method are most tightly intertwined and
therefore hardest to separate.

---

## 4. Anticipated Reply and Why It Does Not Suffice

The Phase 3 defense explicitly invokes my surrender condition §6(3):
"If the author can demonstrate that 'contextual generalizability' is a
component of quality already measured by C1–C5 — specifically, that a
decision scoring highly on C1–C5 is necessarily one whose reasoning
generalizes — the Phase 3 criterion substitution does not change the
evaluation objective." The defense claims to meet this condition through
the conceptual analysis of C1-C5 as a method criterion (§4.1-4.3 of the
defense paper).

**Why this does not meet the surrender condition.** My condition requires a
*necessary* implication: a high-C1-C5 score necessarily implies
generalizability. The defense provides a conceptual argument for why the
implication should hold by the nature of what the criteria measure. But the
necessary implication, if it held, would make Phase 3 redundant: if every
high-C1-C5 decision is necessarily generalizable, and the goal is to identify
the most generalizable champion, the method can simply select the
highest-aggregate-C1-C5 decision across all clusters. That it cannot do this
(without introducing cross-cluster non-transitivity) is the entire design
rationale for the hierarchical structure. Surrender condition §6(3) cannot
be met by a conceptual argument that, if valid, makes Phase 3 unnecessary.

The condition can only be met by resolving the dilemma identified in Section
3.5: demonstrating either that cross-cluster C1-C5 comparison does *not*
exhibit the non-transitivity that motivated the hierarchical design (in which
case Phase 3's problem disappears, along with Phase 2's rationale), or that
"contextual generalizability" provides a genuinely different evaluation frame
from C1-C5 that is more tractable for cross-cluster comparison — in which
case the criterion is different, not identical. The defense does not address
this dilemma.

The most direct remaining reply available to the Phase 3 defense is to
argue that "contextual generalizability" functions as a simplified, more
tractable *implementation* of C1-C5 cross-cluster — not conceptually
different, but operationally more stable because the explicit abstraction
instruction reduces the salience of domain-specific content features that
drive non-transitivity. This version of the argument requires empirical
support: measurements showing that Phase 3 pairwise comparisons under the
contextual-generalizability instruction exhibit lower non-transitivity rates
than Phase 2 cross-cluster comparisons would under C1-C5. Without this
evidence, the claim that the instruction stabilizes the frame is the same
kind of informal argument the ESHTR paper makes for SPH itself — a
plausible conjecture, not an established result.

Separately, for the Phase 2 sections (3.1-3.4): the mechanism paper's
sub-predictions (structured cycles, directional predictability, asymmetric
cluster-pair gradient) provide more diagnostic sharpness than aggregate κ.
But these predictions address between-cluster non-transitivity patterns. They
do not separately measure within-cluster triple cycle incidence, which is the
quantity the Phase 2 attack targets. The experiment as designed does not
generate the data needed to test the within-cluster component of this attack.

---

## 5. Scope of the Attack

This attack targets ESHTR's stated ambition to produce a *global quality
ranking* of judicial decisions and the use of embedding similarity as a
design principle for evaluative stability. The attack has been sharpened,
relative to its initial form, by accepting the contingent frame construction
mechanism as the best available account of why the SPH should hold, and by
accepting the defense's conceptual claim that C1-C5 tests domain-general
reasoning method — while showing that this acceptance generates a structural
dilemma for Phase 3's design rationale rather than resolving it.

This attack does not challenge:

- The value of Phase 2 intra-cluster ranking as a domain-specific quality
  assessment tool, even if residual within-cluster non-transitivity remains.
- The structured rubric design (C1–C5) or the LLM panel methodology
  (following Verga et al., 2024), which are independently motivated.
- The calibration protocol (Section 5.4).
- The paper's intellectual honesty in presenting ESHTR as a position paper
  with falsifiable predictions.
- The mechanism account of non-transitivity itself. The Tversky (1969, 1977)
  grounding is accepted as the best available explanation. The attack is
  on the operationalization, not the mechanism.
- The conceptual claim that C1-C5 targets domain-general reasoning method.
  This is accepted. The attack is that the acceptance generates a dilemma
  for Phase 3 rather than resolving it.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the following
conditions.

1. **Triple-level within-cluster homogeneity confirmed**: If experiments show
   that within-cluster triples produce cycle incidence statistically
   indistinguishable from that expected under a single stable criterion,
   the within-cluster attack falls. This requires measuring not only
   aggregate κ but the distribution of non-transitive triples and testing
   whether cycles are concentrated at within-cluster quality-dimension
   boundaries (as the attack predicts) or uniformly distributed (as
   stability would predict).

2. **The mechanism paper's sub-predictions confirmed with structure**: If
   the experiment shows (a) structured cycles concentrated in triples with
   maximal inter-pair semantic distance, (b) directionally predictable
   cycles across cluster pairs, and (c) an asymmetric gradient across
   cluster-pair semantic distances — and if these patterns hold with
   within-cluster residual non-transitivity controlled — the proxy is
   functioning with sufficient precision for the design goal.

3. **The Phase 3 dilemma resolved by empirical evidence**: The criterion-
   substitution attack holds unless evidence shows that Phase 3 comparisons
   under the contextual-generalizability instruction exhibit substantially
   lower non-transitivity rates than Phase 2 cross-cluster comparisons
   under C1-C5, while correlating with Phase 2 quality rankings within each
   cluster. If Phase 3 rankings correlate highly with Phase 2 cluster-quality
   rankings and exhibit lower non-transitivity than cross-cluster C1-C5
   application, this would support the interpretation that contextual
   generalizability functions as a tractable implementation of cross-cluster
   method-quality comparison. The conceptual analysis alone cannot settle this.

4. **Restricted scope claim**: If ESHTR is reinterpreted as producing only
   within-cluster quality rankings (not a global ranking), the Phase 3
   attack is moot. This requires retracting or qualifying the Abstract's
   claim that Phase 3 "surfaces globally exceptional decisions."

---

## References

Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking:
A Scalable Method for Evaluating Judicial Decision Quality with LLM Panels.
`embedding_seeded_tournament_paper.md` (this repository).

Phase 3 Is Not a Criterion Substitution: On the Coherence of ESHTR's Global
Ranking. `yesindeed/phase3-coherence-defense.md` (this repository).

Frame Stability and the Semantic Proximity Hypothesis: A Cognitive Mechanism
for Non-Transitivity in LLM Judges. `yesindeed/frame-stability-sph.md`
(this repository).

Tversky, A. (1969). Intransitivity of preferences. *Psychological Review*,
76(1), 31–48.

Tversky, A. (1977). Features of similarity. *Psychological Review*, 84(4),
327–352.

Verga, P. et al. (2024). Replacing Judges with Juries: Evaluating LLM
Generations with a Panel of Diverse Models. *NAACL 2024*.

Xu, Y., Ruis, L., Rocktäschel, T., and Kirk, R. (2025). Investigating
Non-Transitivity in LLM-as-a-Judge. *ICML 2025* (Spotlight).
arXiv:2502.14074.
