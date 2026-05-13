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

The strongest form of the argument now includes an independent cognitive
mechanism that grounds the Semantic Proximity Hypothesis — the contingent
frame construction account from behavioral decision theory.

When an LLM judge compares two items A and B, it constructs an implicit
evaluative frame: a weighting of which features are relevant and how much
each matters. Tversky (1969) showed that preference intransitivity arises
not from random error but from systematic criterion switches across pairs:
an agent that applies criterion d₁ to adjudicate A vs. B, d₂ for B vs. C,
and d₃ for A vs. C can generate cycles where each individual judgment is
locally correct. Tversky (1977) further showed that which features are
most salient in a comparison depends on the specific pair, not only on the
feature inventory shared by the items.

Applied to LLM judges: an LLM that has learned domain-specific criterion
mappings from legal corpora will weight evaluative features differently
depending on the pair it is comparing. Within a semantic cluster — say,
administrative disciplinary decisions — items share the same subject matter,
vocabulary, and doctrinal framework, so the features that most discriminate
any given pair are drawn from the same constrained criterion set. The
comparison frame is stable, and cycles are less likely. Across clusters —
comparing a criminal sentencing decision to a tax injunction ruling — the
discriminating features shift between pairs, generating cycles even when
each individual judgment is accurate under its own frame.

This mechanism is additive to, not a replacement for, ESHTR's bias-amplification
account (Section 4): cross-cluster comparisons both destabilize the criterion
frame and amplify positional and verbosity biases that the judge cannot
override when no stable criteria anchor the evaluation.

Under this account, embedding-based clustering is motivated because embedding
proximity tracks the semantic context that determines which criterion set an
LLM judge will activate. Clustering by semantic proximity is clustering by
implicit criterion set, and clusters with stable criterion sets produce
reliable, transitive rankings.

---

## 3. The Attack

The argument depends on an identification that the cognitive mechanism, once
accepted, reveals cannot hold in general: **within-cluster criterion
stability is not derivable from pairwise embedding proximity**, and the
operationalization gap between what embeddings measure and what the mechanism
requires is systematic and has a specific structure.

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

### 3.5 Phase 3 Does Not Solve the Residual Problem; It Replaces the Criterion

Even granting the Phase 2 argument, Phase 3 explicitly compares cluster
champions across semantically distant clusters — the criminal law champion
against the tax law champion, the RPPS pension champion against the
administrative disciplinary champion. This is exactly the cross-domain
comparison that motivated the design of Phase 2.

Section 3.3 of ESHTR addresses this by adding a criterion for Phase 3:
"whether the reasoning quality evident in the decision would transfer to
adjacent subject matters" (contextual generalizability). This does not
solve the cross-cluster problem; it substitutes a different evaluation
objective.

Phase 2 ranks decisions by criteria C1–C5, anchored to domain-specific
procedural standards (art. 489, §1º CPC; art. 927 CPC). These criteria
are domain-sensitive: what counts as "correct application of a binding
precedent" in criminal sentencing differs from what counts in tax law.
Phase 3 ranks cluster champions by contextual generalizability — a property
that C1–C5 does not measure and that is not equivalent to quality under
domain-specific standards.

The global ranking produced by combining Phase 2 cluster rankings with
Phase 3 is therefore not a unified quality ordering. A decision ranked
second in its cluster under C1–C5 (eliminated in Phase 2, absent from
Phase 3) may be globally superior under any unified quality standard the
method could have applied — but it is invisible in the final ranking.

The paper claims (Abstract) that Phase 3 "surfaces globally exceptional
decisions." But "globally exceptional under C1–C5" and "highest-scoring
on contextual generalizability" are categorically different properties.
The champion identified by Phase 3 is the decision that most generalizes
across subject matters — not necessarily the decision of highest quality
under the Brazilian CPC standards that motivate the rubric.

### 3.6 The Added Criterion Is Subject to the Same Non-Transitivity Concern

Section 3.3 of ESHTR asks LLM judges to assess "whether the reasoning
quality evident in the decision would transfer to adjacent subject matters."
Under the mechanism account, this cross-domain evaluation is exactly the
kind of judgment most susceptible to criterion-switching: the LLM must
bridge the criterion sets of different domains to evaluate transferability,
which is precisely the operation the mechanism attributes as the source of
cross-cluster non-transitivity.

Phase 3 therefore introduces a criterion that, under the mechanism paper's
own account, is likely to exhibit the very non-transitivity it was introduced
to manage. The method has not eliminated the cross-domain evaluation problem;
it has deferred it to a criterion that is structurally more, not less,
susceptible to frame instability.

---

## 4. Anticipated Reply and Why It Does Not Suffice

The most direct reply now available to the author is: the mechanism paper's
sub-predictions (structured cycles, directional predictability, asymmetric
cluster-pair gradient) provide a more demanding test than the aggregate κ
comparison. If the ESHTR experiment shows that non-transitive cycles are
concentrated in triples with maximal pairwise semantic distance asymmetry,
and that the asymmetric gradient holds across cluster pairs, this would
confirm that the operationalization is tracking the mechanism's relevant
property — even if imperfectly.

This reply does not suffice for three reasons.

First, the sub-predictions distinguish between within-cluster and
cross-cluster non-transitivity at the aggregate level, but they cannot
distinguish between *within-cluster criterion-switching* and *genuine
within-cluster frame stability*. If within-cluster κ is higher than
cross-corpus κ, this is consistent with (a) within-cluster items sharing
a single dominant criterion (the proxy is working) and (b) within-cluster
items generating moderate criterion-switching while cross-cluster items
generate severe switching (the proxy reduces the problem without solving it).
The experiment does not separately measure within-cluster triple cycle
incidence, which is the quantity the mechanism attack targets.

Second, the asymmetric gradient prediction (closer cluster pairs show smaller
κ degradation) addresses whether embedding distance is a good proxy for
*cross-cluster* non-transitivity. It does not address whether within-cluster
pairwise similarity prevents *triple-level* criterion inconsistency. These
are separate tests.

Third, even if the aggregate experimental results support the SPH in its
rough form, the Phase 3 attack stands independently. The experiment is
designed to test within-cluster vs. cross-corpus κ comparison (Section 5.5);
it is not designed to test whether Phase 3's contextual generalizability
criterion is more stable than C1–C5 in cross-cluster comparison, or whether
the global ranking it produces is coherent under any unified quality standard.

---

## 5. Scope of the Attack

This attack targets ESHTR's stated ambition to produce a *global quality
ranking* of judicial decisions and the use of embedding similarity as a
design principle for evaluative stability. The attack has been sharpened,
relative to its initial form, by accepting the contingent frame construction
mechanism as the best available account of why the SPH should hold. The
mechanism reveals that the operationalization gap is more specific than
a general mismatch between topical proximity and frame stability: it
concerns the triple-level criterion-consistency requirement that pairwise
clustering cannot guarantee.

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

3. **Criterion consistency across phases**: If the author can demonstrate
   that contextual generalizability is a component of quality already
   measured by C1–C5 — specifically, that high-C1–C5 decisions necessarily
   have reasoning that generalizes — the Phase 3 criterion substitution
   does not change the evaluation objective. This requires a normative
   argument connecting CPC procedural criteria to domain-agnostic
   reasoning quality.

4. **Restricted scope claim**: If ESHTR is reinterpreted as producing only
   within-cluster quality rankings (not a global ranking), the Phase 3
   attack is moot. This requires retracting or qualifying the Abstract's
   claim that Phase 3 "surfaces globally exceptional decisions."

---

## References

Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking:
A Scalable Method for Evaluating Judicial Decision Quality with LLM Panels.
`embedding_seeded_tournament_paper.md` (this repository).

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
