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
judges are reliably coherent, and the non-transitivity problem can be
managed by confining dangerous cross-domain comparisons to Phase 3, where
a modified criterion handles them.

---

## 2. Faithful Reconstruction

The strongest form of the argument is as follows.

LLM judges are unstable when comparing semantically distant items because
they must construct incompatible implicit evaluative frames. The criteria
that make one decision better than another depend on the domain, the
procedural context, and the substantive standards applicable. When two
compared decisions share semantic context — same subject matter, same
procedural stage — the judge can draw on a stable set of criteria: it
knows what "good reasoning" looks like in this domain. When the decisions
are semantically distant (a criminal ruling vs. a tax ruling), the judge
must reconcile evaluative criteria that differ not in degree but in kind,
generating the positional bias and preference inconsistency that produce
non-transitive cycles.

Embedding-based clustering captures exactly this semantic context: decisions
embedded nearby in vector space share topic, vocabulary, procedural stage,
and substantive domain. By restricting Phase 2 comparisons to within-cluster
pairs, ESHTR ensures that the implicit evaluative frame remains stable across
comparisons, reducing non-transitivity.

The Semantic Proximity Hypothesis thus has a principled theoretical basis
even before empirical validation: it follows, on this account, from the
structure of how LLM judges construct in-context evaluative criteria.

---

## 3. The Attack

The argument depends on an identification that does not hold in general:
**semantic distance as measured by text embeddings is not the same as
evaluative frame distance as experienced by an LLM judge**. The method
conflates two distinct notions of proximity, and the conflation is
systematic rather than incidental.

### 3.1 What Embeddings Measure

Dense text embeddings — multilingual-e5-large-instruct, the model proposed
in Section 5.2 — are trained to place semantically similar texts nearby in
vector space, where "semantically similar" is operationalized through
contrastive or next-sentence objectives on natural language. These models
cluster documents by topical similarity: two criminal sentencing decisions
will be embedded nearby because they share vocabulary, cited statutes, and
argumentation patterns. Two tax law rulings will also cluster. The embedding
distance between these two clusters is large.

Embedding similarity is a reliable proxy for topical similarity. It is not,
without further argument, a reliable proxy for the stability of an LLM
judge's evaluative frame when comparing two documents within a topic.

### 3.2 Why Evaluative Frame Stability Is a Different Property

Within a semantically coherent embedding cluster — say, a criminal law
cluster — a judicial corpus contains decisions that differ along dimensions
that matter for LLM judge evaluative stability:

- **Procedural stage**: First-instance sentencing, appellate revision,
  post-conviction relief, and habeas corpus all appear in "criminal law"
  clusters. The evaluative standards for first-instance sentencing
  (proportionality of the custodial measure, weighing of aggravating and
  mitigating factors) differ substantially from those for appellate habeas
  review (existence of a constrangimento ilegal, preservation of rights
  during arrest). An LLM judge comparing a first-instance sentencing
  decision to a habeas ruling is evaluating across different doctrinal
  frameworks — even though both decisions land in the same cluster.

- **Quality-level distance**: A cluster champion may be a decision that
  applies a detailed proportionality analysis across twelve mitigating
  factors. Its intra-cluster adversary may be a two-paragraph dispositif
  citing a generic formula. The evaluative criteria needed to distinguish
  them (criterion C2: enfrentamento de argumentos; criterion C3: ausência de
  motivos genéricos) are straightforward. But comparing a top-10 decision
  in criminal sentencing to a top-10 decision in criminal evidence admission
  may require reconciling doctrinal frameworks that share vocabulary
  ("fundamentação", "ratio decidendi") while applying incommensurable
  substantive standards.

- **Domain-internal heterogeneity vs. domain-external homogeneity**:
  Rigorous statutory interpretation — careful textual analysis, systematic
  engagement with legislative history, coherent precedent application —
  appears across criminal law, tax law, administrative law, and
  constitutional law. Two decisions that exemplify identical interpretive
  methodologies may cluster in different embedding domains but require the
  same evaluative frame. Conversely, two decisions that cluster together
  (both "labor law") may require different evaluative frameworks depending
  on whether they address collective bargaining procedures or individual
  termination rights.

The Semantic Proximity Hypothesis predicts that embedding-proximate
comparisons exhibit lower non-transitivity. The mismatch identified here
suggests the hypothesis may hold as a rough correlation (topical similarity
is a noisy proxy for evaluative stability) while being insufficient as a
*design principle* for clustering. The noise is systematic rather than
random: the cases where embedding proximity and evaluative stability come
apart are not exceptional edge cases but structural features of legal
corpora.

### 3.3 The Hypothesis Is Introduced Without the Evidence It Needs

Section 4 of the paper offers an "informal argument" that evaluative frame
instability is the mechanism connecting semantic distance to non-transitivity.
This argument is plausible but circular in the context of ESHTR's design. The
paper first defines evaluative frame instability as the mechanism (an LLM
constructing different implicit criteria for semantically distant items), then
uses embedding-based clustering as the operationalization of "same semantic
context," then cites the mechanism as the justification for the
operationalization.

The circularity matters because it conceals a gap: the informal argument does
not establish that the embedding models used (multilingual-e5-large-instruct
or its fine-tuned variants) track the distinctions relevant for LLM judge
stability. The paper states that "embeddings capture semantic similarity
across topical clusters... procedural stages... and subject matter" (Section
3.1). But the claim that they also track evaluative frame stability — the
property that actually matters for the Semantic Proximity Hypothesis — is
asserted, not argued.

The falsifiability condition stated in Section 4 is *κ_intracluster >
κ_crosscorpus*. This test, if run, would reveal whether embedding-based
clusters produce higher judge agreement. But it would not, even if
confirmed, establish that the mechanism is evaluative frame stability rather
than a trivially confounded variable (e.g., clusters tend to contain
decisions of similar length, and verbosity bias interacts with length).

### 3.4 Phase 3 Does Not Solve the Residual Problem; It Replaces the Criterion

Even granting the Phase 2 argument, Phase 3 explicitly compares cluster
champions across semantically distant clusters — the criminal law champion
against the tax law champion, the RPPS pension champion against the
administrative disciplinary champion. This is exactly the cross-domain
comparison that motivated the design of Phase 2.

Section 3.3 addresses this by adding an evaluation criterion for Phase 3:
"whether the reasoning quality evident in the decision would transfer to
adjacent subject matters" (contextual generalizability). This addition does
not solve the cross-cluster problem; it substitutes a different evaluation
objective.

Phase 2 ranks decisions by criteria C1–C5, anchored to domain-specific
standards. These criteria measure whether a decision correctly applies the
ratio of a binding precedent to the case at hand (C1, C4), addresses
material arguments (C2), avoids generic boilerplate (C3), and produces a
complete dispositif (C5). These are domain-sensitive: what counts as a
"determining ground" in criminal sentencing differs from what counts as one
in tax law.

Phase 3 ranks cluster champions by "contextual generalizability" — a
property that C1–C5 does not measure and that is not equivalent to quality
under domain-specific standards. A criminal sentencing decision that is the
highest-quality decision in its cluster under C1–C5 may score poorly on
"contextual generalizability" because criminal sentencing employs technical
statutory formulas specific to the Código Penal that do not transfer to
adjacent domains. A moderately-ranked decision in a tax law cluster may
score highly on "contextual generalizability" because it applies a
domain-agnostic interpretive method whose logical structure is transparent.

The global ranking produced by combining Phase 2 cluster rankings with Phase 3
rankings is therefore not a single unified quality ordering. It is a composite
of two incommensurable rankings: Phase 2 ranks on C1–C5, Phase 3 ranks on
contextual generalizability. A decision ranked second in its cluster under
C1–C5 (eliminated in Phase 2, absent from Phase 3) may be globally
superior under any unified standard that the method could have applied —
but it is invisible in the final ranking.

The paper claims (Abstract) that Phase 3 "surfaces globally exceptional
decisions." But "globally exceptional under C1–C5" and "highest-scoring on
contextual generalizability" are categorically different properties. The
champion identified by Phase 3 is the decision that most generalizes across
subject matters — not necessarily the decision of highest quality in the
Brazilian CPC sense that motivates the rubric.

### 3.5 The Added Criterion Is Subject to the Same Non-Transitivity Concern

Section 3.3 asks LLM judges to assess "whether the reasoning quality
evident in the decision would transfer to adjacent subject matters." This
cross-domain evaluation is exactly the kind of judgment the paper argues
LLM judges perform poorly: one that requires bridging different contextual
frames and applying criteria that are not anchored to a specific domain.
The mechanism invoked in Section 4 to explain non-transitivity
("bridging different contextual frames, introducing instability") applies
directly to contextual generalizability assessments.

Phase 3 therefore introduces a criterion that is likely to exhibit the very
non-transitivity it was introduced to manage. The method has not eliminated
the cross-domain evaluation problem; it has deferred it to a criterion that
is less, not more, stable than C1–C5.

---

## 4. Anticipated Reply and Why It Does Not Suffice

The anticipated reply is: the Phase 3 "contextual generalizability" criterion
is appropriate precisely because direct application of C1–C5 is unreliable
at the cross-cluster stage. The Phase 2 champions have already been validated
on C1–C5; Phase 3 asks which of those champions has reasoning that rises above
domain-specific content. This is consistent with identifying globally
exceptional decisions.

This reply does not suffice for two reasons.

First, it confirms that Phase 3 operates on a different criterion — which
accepts that the global ranking combines incommensurable local rankings. If
"globally exceptional" is defined by contextual generalizability rather than
by C1–C5, then the method should say so explicitly. The paper's stated goal
is quality evaluation of judicial decisions under Brazilian CPC standards;
contextual generalizability is at best a correlate of quality, not a measure
of it.

Second, the reply does not address the specific mechanism by which Phase 3's
criterion is expected to be more stable than C1–C5 under cross-cluster
comparison. Given that the paper's own Section 4 attributes non-transitivity
to the need to bridge incompatible contextual frames, a criterion that
explicitly requires bridging ("would transfer to adjacent subject matters")
should be *more* susceptible to the instability, not less. The reply would
need to explain why this expectation is wrong.

---

## 5. Scope of the Attack

This attack targets ESHTR's stated ambition to produce a *global quality
ranking* of judicial decisions and the use of embedding similarity as a
design principle for evaluative stability. It does not challenge:

- The value of Phase 2 intra-cluster ranking, which may be a useful tool
  for domain-specific quality assessment even if the Semantic Proximity
  Hypothesis is a rough approximation.
- The structured rubric design (C1–C5) or the LLM panel methodology
  (following Verga et al., 2024), which are independently motivated
  contributions.
- The calibration protocol (Section 5.4), which addresses a distinct concern.
- The paper's intellectual honesty in presenting ESHTR as a position paper
  with falsifiable predictions, not a system with reported results.

The attack is specifically directed at (a) the assumption that embedding
distance tracks evaluative frame stability in a way sufficient to ground
the clustering step and (b) the coherence of combining Phase 2 and Phase 3
into a single unified global ranking when Phase 3 substitutes a different
evaluation criterion.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the following
conditions:

1. **Empirical confirmation of the clustering effect, with within-cluster
   heterogeneity controls**: If experiments show that embedding-based
   clustering produces significantly higher LLM judge agreement (Fleiss' κ)
   and that this effect persists when controlling for within-cluster
   procedural-stage heterogeneity and quality-level variance, the attack on
   Phase 2's design rationale is substantially weakened. The paper's own
   falsifiability condition (Section 4) is the appropriate test, but the
   controls matter.

2. **Criterion consistency across phases**: If the author can demonstrate
   that "contextual generalizability" is a component of quality already
   measured by C1–C5 — specifically, that a decision scoring highly on C1–C5
   is necessarily one whose reasoning generalizes — the Phase 3 criterion
   substitution does not change the evaluation objective, and the global
   ranking is more coherent than the attack suggests. This requires a
   normative argument connecting CPC procedural criteria to domain-agnostic
   reasoning quality.

3. **Restricted scope claim**: If ESHTR is reinterpreted as producing only
   within-cluster quality rankings (not a unified global ranking), the Phase
   3 attack is moot. The method would be valuable for domain-specific quality
   assessment. This requires retracting or substantially qualifying the claim
   that Phase 3 "surfaces globally exceptional decisions," which appears in
   the Abstract and Section 3.3.

---

## References

Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking:
A Scalable Method for Evaluating Judicial Decision Quality with LLM Panels.
`embedding_seeded_tournament_paper.md` (this repository).

Verga, P. et al. (2024). Replacing Judges with Juries: Evaluating LLM
Generations with a Panel of Diverse Models. *NAACL 2024*.

Xu, Y., Ruis, L., Rocktäschel, T., and Kirk, R. (2025). Investigating
Non-Transitivity in LLM-as-a-Judge. *ICML 2025* (Spotlight).
arXiv:2502.14074.
