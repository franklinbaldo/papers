---
type: "Adversarial Critique"
title: "Embedding Proximity Is Not Evaluative Frame Stability: A Challenge to ESHTR's Core Design Rationale"
description: "Critica adversarial ao campeonato inter-cluster da Fase 3 do ESHTR e ao debate C2: round 36 (§4.21, this filing) pressiona as condições de falha (s)–(u) nomeadas pela resposta adversarial r34 (§4.20) e respondidas pela resposta supportive r35 (§4.20 do lado supportive). Contra (s/v) — o critério de separabilidade estrutural de R35 conflate localização de premissas com expressibilidade da cadeia de raciocínio: a cadeia de raciocínio do veredito também é construída sobre premissas em documentos anteriores, mas o art. 93, IX CF ainda a alcança; o critério correto é se a cadeia de raciocínio das premissas à conclusão é expressível de forma independente, e a cadeia de designação-ratio ('G2 porque J4–J5 fundam G2 de forma autônoma') é assim expressível. Contra (t/w) — R35 responde a uma alegação que R34 nunca fez: R34 argumentou que o censo É a base justificatória da determinação jurídica, não que a operatividade jurídica converte a forma; o fundamento determinante vem a existir por meio da designação, portanto a base da designação É a base justificatória da determinação juridicamente operativa; a afirmação de R35 'os efeitos vinculantes provêm da operação dos arts. 926–927' descreve igualmente o caso do veredito, mas a disposição ainda alcança o raciocínio do veredito. Contra (u/x) — a identidade comparação ementa-votos suprime a etapa de aplicação do critério: votos individuais não afirmam 'J4 e J5 juntos constituem apoio coletivo autônomo suficiente para G2'; aplicar o critério limiar ao registro deliberativo produz conteúdo que não está no voto de J4, no voto de J5 nem na própria designação — exatamente o conteúdo de documento intermediário que a própria condição de falha (u) de R35 nomeia. Novas condições de falha: (v) separabilidade estrutural operacionalizada como expressibilidade da cadeia de raciocínio; (w) distinção de forma justificatória não alcança o argumento de R34 de que a designação produz a determinação jurídica; (x) argumento estrutural estabelece que cada voto individual expressa separadamente o conteúdo do critério limiar de apoio coletivo autônomo. Requisito (1) permanece aberto após round 36."
tags: [adversarial, eshtr]
timestamp: 2026-09-01T00:00:00+00:00
---

# Embedding Proximity Is Not Evaluative Frame Stability: A Challenge to ESHTR's Core Design Rationale

---

## 1. Thesis Attacked

The paper "Embedding-Seeded Hierarchical Tournament Ranking" (Baldo, 2025;
`embedding_seeded_tournament.md`) proposes that dense-embedding
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

The strongest form of the argument now includes three independent theoretical
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

**Support 2 — Within-cluster comparative stability and its structural supports.**
The supportive account (`yesindeed/frame-stability-sph.md`) does not claim
categorical within-cluster frame stability. It makes a comparative,
probabilistic claim: within-cluster triples exhibit *lower* criterion-switching
rates than cross-cluster triples, not zero criterion-switching. Two structural
properties jointly support this reduction. First, quality dimensions in expert
legal reasoning tend to be positively correlated within a subject-matter
context: a judge who reasons carefully about proportionality tends also to
reason carefully about fact-finding, because careful analysis is a disposition
that manifests across dimensions. Maximally asymmetric quality-dimension
profiles occur but are not the modal pattern in a corpus of decisions from
the same procedural area. Second, embedding proximity captures more than a
broad topical category: decisions in the same embedding neighborhood share
precedential references, procedural posture, and rhetorical conventions. This
doctrinal micro-context constrains the most salient criterion set for
within-cluster pairings beyond what the topical label alone determines.

Additionally, the Bradley-Terry model aggregates over many pairings within
each cluster. If any residual within-cluster criterion-switching is
non-systematic — not directionally correlated with item identities — it
contributes variance to individual pairings without introducing systematic
bias into the aggregate score. The design standard for Phase 1 is relative
reduction in non-transitivity incidence, not elimination; Bradley-Terry
provides practical robustness for non-directional residual variance.

The ideal operationalization — clustering items by criterion-set homogeneity
within triples — would require knowing, before Phase 2, which quality
dimensions are most discriminating for which pairs. This information is
generated by Phase 2 itself. Embedding clustering is therefore the best
tractable pre-evaluation proxy given the information available before
evaluation runs. Whether the proxy is adequate can be tested by measuring
whether within-cluster non-transitive cycles are unstructured relative to
quality-dimension asymmetry profiles (Prediction 4, from
`yesindeed/frame-stability-sph.md`, §3.4).

The supportive paper has since responded directly to the §§3.2–3.3 attacks
(`yesindeed/frame-stability-sph.md`, updated 2026-05-16). Against the
rubric-independence objection: C1-C5's logical independence establishes
completeness of coverage, not statistical independence of scores; instruments
with logically distinct subscales exhibit positive intercorrelations in expert
populations due to an underlying analytical-care disposition. Against case-driven
quality-dimension variation: criteria like C3 and C5 are properties of writing
disposition rather than responses to party arguments; case-specific demands
determine which dimensions receive the most elaborate treatment, not which
dimensions score low. Against routinization: uniform C3 failure compresses C3
variance toward a floor, making C3 the least discriminating feature in pairings
between similarly formulaic items; the mechanism is a "localized effect" on the
exceptional item that deviates from the pattern, not a cluster-wide mechanism.
Against item-level persistent criterion activation: the Tversky (1977) account
identifies the most discriminating feature as pair-specific — determined jointly
by both items. Decision A's fact-finding excellence activates fact-finding as the
most salient criterion in a pairing with B only when A's advantage on fact-finding
exceeds B's counter-advantage on every other dimension; in a pairing with C who
matches A on fact-finding, the most discriminating feature shifts. Persistent
activation across all of A's pairings is an extreme condition requiring A to be a
clear outlier on one dimension relative to the entire cluster, not the modal
configuration in clusters with graded quality variation across multiple dimensions.

**Support 3 — Phase 3 coherence through method-level unity.** The defense
in `yesindeed/phase3-coherence-defense.md` now offers a multi-layered defense of
Phase 3's coherence. The core factual move (§4.3): ESHTR §3.3 explicitly describes
Phase 3 as "a cross-cluster championship tournament." The hierarchical design
*confines* uncontrolled cross-cluster comparison to an eliminated baseline; Phase 3
IS the controlled cross-cluster comparison the design enables. The prior adversarial
framing — that cross-cluster C1-C5 comparison is "precisely what ESHTR was
constructed to avoid" — is corrected by the defense as a mischaracterization. Horn 1
of the original dilemma (Phase 3 = cross-cluster C1-C5 application) is accepted as
accurate, but its implied conclusion (this defeats ESHTR's design rationale) does not
follow: the design rationale was precisely to make controlled cross-cluster comparison
tractable in Phase 3.

Additionally, a mechanism-level argument for Phase 3's tractability (§4.5): the
explicit instruction "abstract from subject-specific vocabulary to underlying
argumentation quality" functions, under the Tversky (1977) feature-salience account,
as a frame-setting mechanism. It changes the comparison frame from implicit
(domain-content-dominated) to explicit (method-quality-directed), reducing salience
of domain-specific content features via the same mechanism both sides have accepted
as governing criterion activation in comparative judgment. An explicit frame specification
changes the operationalization without changing the underlying criterion.

A third implementation option for method/content application (§4.6, Option c): LLM
judges can evaluate the structure of reasoning using domain-specific material as
evidence, without evaluating domain-specific content correctness — assessing logical
dependency relationships and argument engagement quality. This is the mode in which
comparative law scholars assess foreign decisions across jurisdictions.

Under this account, Phase 3's global ranking is coherent: Phase 2 and Phase 3 measure
the same underlying property (reasoning method quality) at different aggregation levels,
with Phase 3's structural controls (champion population, explicit instruction, small k)
making cross-cluster comparison tractable in ways that uncontrolled cross-cluster
comparison is not.

In round 6 of the C2 debate, the supportive camp additionally accepts the input-protocol
gap for coverage completeness tracking — characterizing providing the party brief as a
minor input-specification change under Brazilian processo eletrônico (Lei nº 11.419/2006),
not an architectural redesign — and specifies SC6(b-2) as a concrete naturalistic
validation test with an explicit falsification criterion, and proposes a cross-elaboration
calibration pair methodology for SC6(3): champions matched on doctrinal area but
differentiated by cluster-level adversarial record richness, with independent expert
assessment of reasoning-operation quality establishing quality-discrepant pairs.

---

## 3. The Attack

### 3.1 What the Mechanism Actually Requires

The contingent frame construction account (Tversky 1969, 1977; as developed
in `yesindeed/frame-stability-sph.md`) identifies a precise structural unit
for non-transitivity risk: the **triple** {A, B, C}. A cycle arises in a
triple when the pair (A, B) is most discriminated on criterion set S₁, the
pair (B, C) on S₂, and the pair (A, C) on S₃, with S₁, S₂, S₃ not all
equal. The mechanism is triple-level, not pair-level.

ESHTR's Phase 1 clustering controls pairwise semantic distance. The resulting
clusters group items that are similar to each other in embedding space. But
grouping by pairwise similarity does not guarantee triple criterion-consistency.
A set of three items {A, B, C} can all fall within a single high-density
cluster — mutually similar in embedding space — while still forming a
criterion-switching triple if A and B are most differentiated on one quality
dimension, B and C on a second, and A and C on a third.

The supportive paper (`yesindeed/frame-stability-sph.md`, §3.2) now
acknowledges this directly: "Pairwise embedding proximity does not guarantee
triple-level criterion-consistency. A cluster of three items can all be
mutually similar in embedding space while still activating different criterion
sets across pairings, if items vary asymmetrically across quality dimensions
within the cluster." The gap between the mechanism and the operationalization
is established on both sides of this debate. The live questions are: (a) does
the comparative stability claim hold — do within-cluster triples exhibit
materially lower criterion-switching rates than cross-cluster triples? and (b)
is whatever residual switching remains handled adequately by Bradley-Terry
aggregation?

### 3.2 The Comparative Stability Claim Cannot Sustain the Design Goal

**The quality-dimension correlation argument conflicts with the rubric's
architecture and with the structure of appellate corpus generation.**

The supportive paper argues that quality dimensions in expert legal reasoning
tend to be positively correlated within a subject-matter context: a judge who
reasons carefully about proportionality tends also to reason carefully about
fact-finding, because careful analysis is a disposition that manifests across
dimensions. Positive correlations reduce the frequency of maximally asymmetric
quality-dimension profiles — the profiles that generate criterion-switching
triples.

The supportive paper correctly distinguishes logical independence from statistical
independence: defining C1-C5 as five separable failure conditions in CPC art. 489,
§1º establishes completeness of coverage, not a prediction about the joint
distribution of dimension scores in the target corpus. This distinction is accepted.
The adversarial argument does not rest on inferring statistical independence from
logical structure. It is grounded in the legislative purpose: the CPC framework
enumerated five independent failure conditions because Brazilian appellate decisions
were observed to fail on specific dimensions while performing adequately on others —
the criteria were designed to address independently occurring failures. A decision
can correctly identify a ratio (C1) while addressing arguments with generic
boilerplate (C3 failure); it can engage material arguments carefully (C2) while
applying the resulting precedent without principled understanding of its scope (C4
failure). The legislature's recognition that these failure modes occur separately
in Brazilian appellate practice is evidence that cross-dimension divergence is
present in the target population. Whether the specific corpus targeted by ESHTR
exhibits sufficient divergence to generate criterion-switching triples is empirically
open, but the legislative history establishes cross-dimension divergence as the
expected prior for this corpus, not a theoretical assumption derived from logical
structure.

Beyond rubric design, appellate decisions have quality-dimension profiles
shaped by what each case required, not only by the judge's overall analytical
care. C2 performance depends partly on whether the parties raised arguments
capable of affecting the outcome: a case where the most powerful argument for
the losing party was raised but genuinely unmeritorious will produce a thin
C2 record in even the most careful decision, not because the judge lacks
engagement skill but because the case offered no strong material argument
to engage. A complex precedent-identification question forces sustained C1
work; a case where the applicable precedent is settled forces sustained C4
work on application and distinction; a case where boilerplate dismissal is
tempting (high-volume procedural motions) makes C3 the load-bearing dimension.
Within a cluster of decisions on the same doctrinal question, the cases that
reach the appellate level arrived there for different reasons — different
dimensions of the shared question were contested in different cases — producing
systematically different quality-dimension profiles across cluster members
even among decisions authored by careful judges. The supportive paper argues
that a judge's writing disposition maintains adequate scores on under-exercised
dimensions: C3 and C5, as properties of analytical writing care, are applied
regardless of case demands. This holds for C3 and C5. It does not hold for C2 —
the requirement to engage arguments capable of affecting the outcome — because C2
performance at the scoring level is constrained by what material arguments were
available. A case where the opposing party's most powerful argument was genuinely
unmeritorious produces thin C2 performance in even the most careful judge, not
from a writing-disposition deficit but because there was no strong material argument
to engage. C2 variation within a doctrinal cluster reflects both judge-level
engagement skill and the case-level quality of the adversarial record — a compound
that judge-level writing disposition cannot smooth into cross-case uniformity.

At the criterion operationalization level, the practical C2 scoring behavior of
LLM judges does not preserve the theoretical distinction between analytical conduct
quality and engagement volume. A decision that correctly dismisses a weak argument
produces thinner analysis in the decision text than a decision that engages a strong
argument — not from the judge's writing disposition but from the character of the
argument engaged. LLM judges trained on human preference data calibrate their C2
signal partly from this textual thickness, because human annotators comparing
decisions from specialized legal domains cannot verify analytical precision for
specific arguments independently from the decision text itself. Where annotators
cannot distinguish "brief but analytically precise disposal of a weak argument" from
"brief cursory analysis of any argument" by reading the text, the training gradient
favors richer engagement as the more reliable C2 quality indicator. The practical
C2 score is therefore adversarial-record-sensitive even when the criterion is
theoretically defined as a conduct measure. This operationalization gap is not
addressed by the criterion's definition; it requires a calibration protocol
extension — calibration examples demonstrating correct C2 assessment of
weak-argument cases with explicit conditional calibration on argument character.
Without such an extension, the conduct/quality distinction holds at the definitional
level but not at the scoring level where LLM judges actually operationalize it.

The most targeted response to this operationalization argument identifies three
structural features present in Brazilian appellate decisions regardless of argument
strength: explicit identification of what the argument claims, citation to the
applicable legal standard as the operative criterion, and a logical statement of
why the argument fails under that standard. An annotator or calibrated LLM judge can
detect these features' presence without independent knowledge of argument character;
the gap is therefore a protocol design insufficiency closable by including weak-argument
calibration examples, not a structural opacity that infects C2 measurement regardless
of calibration design. This response reframes the contested claim usefully: the
operative question is not whether such features are absent in weak-argument contexts
(they are present in any adequately-reasoned decision) but whether their presence closes
the *ranking* calibration problem.

It does not. The three features function as adequacy thresholds — distinguishing
conclusory dismissal from reasoned disposal — not as ranking signals within the
adequacy range. For a pairwise *ranking* task, which is what ESHTR's tournament
requires, both a minimally adequate disposal of a weak argument and an expert engagement
with a strong argument exhibit the three features; the features establish that both
decisions cleared the adequacy floor but cannot discriminate between them. The
calibration gradient operative for tournament ranking runs on within-adequacy
discrimination, and here elaboration depth — how extensively each feature is developed,
how many standards are cited, how complex the logical chain — scales with argument
strength even when all three features are formally present. A strong argument that
raises multiple contested sub-claims requires identification of several claims, citation
to competing authorities, and a multi-step logical chain; the same features appear in
both the weak-argument and strong-argument contexts, but their elaborateness is
argument-strength-sensitive. LLM judges calibrated on human preference annotations over
complete decision texts acquire their within-adequacy ranking signal from this
elaboration depth, not from feature presence alone. Calibration examples for SC6(a)
must therefore be constructed as *pairwise ranking* examples — where a
brief-but-adequate disposal of a weak argument ranks above an inadequate disposal of
the same weak argument, despite potentially similar or greater text length in the
inadequate version — training judgment of conduct quality within the adequacy range.
Calibration examples that merely include weak-argument contexts satisfy the structural
move but not the design specificity that closes the within-adequacy gap.

Within fine-grained doctrinal clusters, C1 and C4 score variance is compressed by
shared precedential context in ways that C2 variance is not. In a cluster of
decisions applying the same leading precedents and doctrinal framework, C1 (ratio
identification) and C4 (precedent application) draw on a settled shared landscape:
within-cluster variation is about precise formulation of a ratio already established
and application of a framework already shared — a compressed range relative to
cross-cluster C1/C4 variation. C2 varies with what arguments the opposing party
raised in each specific case, which is independent of the shared doctrinal context.
Within the cluster, cases with similar C1/C4 profiles (same framework) may have
substantially different C2 profiles (different adversarial records) — a case with a
sophisticated factual challenge and a case with only settled-precedent arguments may
be embedding-proximate (same doctrinal vocabulary, same precedential references)
while occupying opposite ends of the within-cluster C2 distribution. The
between-case co-movement of C1, C2, and C4 with adversarial record intensity does
not generate within-cluster co-movement when within-cluster C1/C4 variance is
already compressed toward a common doctrinal profile. Within the cluster's
compressed C1/C4 space, C2 variation is relatively wider and more independent —
producing the profile asymmetry between cluster members that generates C2-specific
criterion activation in within-cluster pairings.

The most direct response to the within-cluster compression argument challenges the
selectivity assumption at its source: dense embedding models trained on legal text
encode both doctrinal vocabulary and argumentative discourse structure in the same
representational space. Decisions with richer C2 engagement differ textually in
argument-specific reasoning vocabulary, counter-reasoning structure, and elaboration
discourse markers — features the embedding model represents alongside precedential
references and procedural posture. If elaboration richness is represented in the same
embedding space, clustering by embedding proximity groups items by elaboration
alongside doctrinal context, compressing within-cluster C2 variance together with
C1/C4 variance. The selectivity the adversarial compression mechanism requires —
doctrinal dimensions compressed, argumentative elaboration dimensions not — has not
been demonstrated for multilingual-e5-large-instruct in Brazilian legal corpora.

The encoding claim is accepted; the compression inference does not follow from it.
Encoding and clustering-compression are distinct operations. The embedding model's
representational space contains dimensions corresponding to many textual features.
Clustering by proximity selects items that are close in this high-dimensional space,
but closeness is driven by the dimensions with highest between-cluster variance —
in fine-grained doctrinal clusters, these are the doctrinal vocabulary, precedential
reference, and procedural-posture dimensions. Within the cluster, these dimensions are
compressed by selection: items are close on the features that drove cluster membership.
Argumentative elaboration varies with case-specific adversarial records, determined by
counsel's choices in each specific case — a source of variation independent of the
shared doctrinal context. For clustering to compress elaboration variance significantly,
elaboration richness would need to correlate strongly with doctrinal proximity in the
target corpus. There is no structural reason for this correlation: a cluster of
proportionality-of-sanction cases contains both cases where counsel raised sophisticated
factual challenges (high elaboration) and cases where counsel raised only
settled-precedent arguments (low elaboration), both equally embedding-proximate on the
doctrinal dimensions that define the cluster's neighborhood.

The response's implicit prediction also has a self-contained testable consequence.
If elaboration richness drives embedding proximity significantly enough to produce
meaningful within-cluster compression, the clustering step co-locates high-elaboration
decisions with high-elaboration ones and low-elaboration with low-elaboration ones;
within-cluster pairings are then between decisions with similar elaboration levels;
the elaboration-asymmetric pairings where C2 criterion activation is sharpest are
sorted into cross-cluster events rather than within-cluster ones. Under this outcome
the adversarial concern does not vanish — it relocates to Phase 3, where cross-cluster
comparisons include the cross-elaboration pairings clustering moved there. SC6(c)'s
measurement of per-item C1/C2/C4 dimension scores within fine-grained clusters tests
both predictions simultaneously: if within-cluster C2 variance is not wider than
C1/C4 variance, either the compression is co-extensive (the fourth response's
prediction) or adversarial records happen to be homogeneous within clusters — in
either case the within-cluster adversarial mechanism does not operate; if C2 variance
is systematically wider, the compression asymmetry is confirmed regardless of what
the embedding model encodes in principle.

A fifth supportive response shifts the within-adequacy ranking analysis from
the per-argument level to the argument-set level. The adversarial counter to
the three-features response — that those features function as adequacy
thresholds rather than ranking signals within the adequacy range — is accepted
at the individual-argument level. The fifth response contests it at the
argument-set level. Art. 489, §1º, IV is a coverage criterion over the set
of material arguments: the primary within-adequacy ranking dimension is not
per-argument elaboration depth but coverage completeness — the proportion of
material arguments identified and explicitly disposed of. A decision that
applies the three structural features briefly to all five material arguments
outranks a decision that applies them elaborately to three and ignores two.
Coverage completeness is argument-type-independent in that counting
argument-identification statements against the case record of arguments raised
is sufficient to determine coverage without argument-strength knowledge.
SC6(a) accordingly requires two types of calibration pairings: Type 1 (correct
C2 ranking for a single argument within the adequacy range) and Type 2 (coverage
completeness across the argument space, constructable from the case record alone).

The coverage-completeness argument is accepted as identifying a valid ranking
dimension under art. 489, §1º, IV. The adversarial concern it generates is
structural: coverage completeness is observable only with access to both the
decision text and the case record. Determining the proportion of material
arguments covered requires knowing what arguments counsel raised — information
residing in the party submissions, not in the decision itself. ESHTR's protocol
(§5.4) specifies decision texts as the input provided to the LLM evaluation
panel; party submissions are not described as part of the evaluator's input.
Without the case record, an LLM judge cannot determine coverage completeness
independently of textual proxies available from the decision alone: total token
count (more covered arguments produce more text), argument-identification
statement density (more coverage generates more identification tokens), and the
reversal relationship between coverage breadth and per-argument elaboration
depth. In a complete-but-thin decision covering five arguments briefly and a
selective-but-elaborate decision covering three arguments extensively, the
complete-but-thin decision may be shorter in total text, but the LLM judge
receiving only the decision text cannot determine whether the shorter decision
covered fewer arguments or covered more arguments more briefly — the source of
the length difference is not recoverable from the decision alone. The fifth
response therefore requires a protocol extension — providing the case record
as LLM judge input at evaluation time — to make coverage tracking
argument-type-independent in the way it claims. This extension is distinct from
the SC6(a) calibration requirement: it changes what information the evaluator
receives, not only how it is trained. Type 2 calibration pairings annotated
against the case record during calibration design can establish coverage as the
relevant ranking dimension; they do not validate that LLM judges track coverage
when evaluating naturalistic decisions without case record input at evaluation time.

A further constraint follows from the calibration pairing structure. Type 2
pairings are deliberately anti-naturalistic: the complete-but-thin decision is
shorter than the selective-but-elaborate one, reversing the naturalistic positive
co-variation between coverage breadth and total text length. In a naturalistic
decision corpus, longer decisions tend to cover more arguments and also elaborate
each argument more fully; coverage breadth, total text length, and per-argument
elaboration depth all co-vary positively under natural conditions. Type 2
calibration trains the LLM judge to suppress the coverage-volume correlation
in reversed-relationship pairs. SC6(b) asks whether trained judges track
coverage completeness rather than elaboration depth at the ranking level. The
implicit generalization requirement — that performance on anti-naturalistic
pairs transfers to naturalistic decisions where the standard coverage-volume
co-variation is present — is an additional empirical question the Type 2 design
does not itself answer. SC6(b) must therefore include a test of LLM judges'
coverage-completeness tracking under naturalistic pairings where coverage and
volume co-vary in the standard direction, not only in the artificially reversed
pairs the calibration design constructs.

The sixth supportive response addresses the disjunctive structure of the fourth
adversarial response's self-undermining implication. Under prong 1 of the C2
adversarial disjunction (elaboration richness does not significantly drive
embedding proximity, so within-cluster C2 variance is systematically wider than
C1/C4 variance), the within-cluster C2 independence mechanism operates and
SC6(c) tests it directly. Under prong 2 (elaboration richness does drive
proximity, so cross-elaboration pairings sort to Phase 3), the sixth response
holds that the relocated concern falls under SC6(3). The structural
clarification is accepted: prong 1 and prong 2 correspond to different
operational levels, and SC6(c) determines which prong obtains.

What the sixth response does not resolve: SC6(3) was specified for the
cross-domain non-transitivity concern — whether Phase 3's abstraction
instruction ("abstract from subject-specific vocabulary to underlying
argumentation quality") successfully redirects LLM evaluation from
domain-specific feature activation toward reasoning-method assessment across
doctrinal domains. The cross-elaboration concern that prong 2 relocates to
Phase 3 has a different structure. Under prong 2, clustering co-locates
high-elaboration decisions; each cluster's champion tends to be the
highest-elaboration decision within its cluster. Phase 3 compares
high-elaboration champions from different clusters. The between-champion
differences include both domain-specific vocabulary differences (which the
abstraction instruction targets) and elaboration richness differences arising
from cluster-level adversarial record heterogeneity (which the instruction does
not specifically address). A champion from a high-adversarial-record cluster
has elaborate reasoning because demanding arguments were available; a champion
from a low-adversarial-record cluster has elaborate reasoning because the judge
applied analytical care against undemanding arguments. Whether LLM judges
applying the Phase 3 instruction assign rankings independent of these
between-champion elaboration richness differences — rather than tracking them
as components of "argumentation quality" — is not addressed by SC6(3)'s current
specification, which was designed for the domain-vocabulary non-transitivity
concern. SC6(3) extended to govern prong 2 requires a cross-elaboration-specific
test alongside its cross-domain test: whether Phase 3 judges rank champions
independently of elaboration richness differences arising from cluster-level
adversarial record variation, not only from domain-vocabulary differences.

**Seventh adversarial response — round 7: input-protocol extension introduces
a materiality-identification step; SC6(b-2) accepted as specified; the
cross-elaboration test's expert-assessment protocol is question-begging.**

The supportive round 6 paper addresses all three adversarial requirements from
round 5. Three adversarial responses follow.

*Input-protocol extension: the materiality-identification gap.* The supportive
camp accepts the input-protocol gap and characterizes the required extension as
architecturally minor: Brazilian processo eletrônico (Lei nº 11.419/2006) makes
appellate party briefs publicly accessible as digitized case-record components;
for appellate decisions the relevant brief is typically one document; providing
it alongside the decision text changes the evaluator's input package without
altering panel architecture, calibration rubric, or Bradley-Terry aggregation.

The adversarial position is that this framing understates a new processing
requirement the extension introduces. Coverage completeness under art. 489,
§1º, IV requires identifying which arguments in the brief are material —
capable, in principle, of affecting the outcome ("capazes de, em tese, infirmar
a conclusão") — so that coverage is assessable as a proportion of material
arguments addressed. The party brief contains all arguments counsel chose to
raise: meritorious arguments, marginal arguments, and arguments that are
legally foreclosed on settled doctrine. Determining which arguments cross the
materiality threshold requires assessing argument strength: does this argument,
if accepted, require a different dispositif? This assessment is C2-adjacent.
It requires engagement with argument substance — what the argument claims, what
the applicable standard is, whether accepting the argument's premise would
require the court to decide differently — precisely the analytical step the
C2 debate has established is not straightforwardly separable from elaboration
richness in the text.

Brief arguments that are long and well-developed are more likely to have been
identified by counsel as strong and to satisfy the materiality condition; brief
arguments stated in a few lines are more likely to be marginal. The
elaboration-quality correlation that infects C2 scoring in the decision text
is present in the party brief in the same structural form: more elaborate
arguments correlate with higher likelihood of materiality under art. 489, §1º,
IV. The input extension therefore shifts the processing challenge rather than
resolving it. Instead of asking the LLM judge to infer coverage from the
decision text, it asks the LLM judge to identify material arguments from the
brief and then assess coverage. Both tasks involve assessments that correlate
with elaboration richness.

SC6(a) Type 2 calibration examples constructed with (decision text + party
brief) input must include a demonstration that the LLM correctly identifies
the set of material arguments from the raw brief — not only that it correctly
ranks coverage completeness once the material argument set is given. In the
realistic evaluation condition, the LLM receives (decision text + party brief)
and must perform argument materiality identification before coverage ranking.
Calibration that tests the conditional task (rank coverage given the material
argument set) but not the identification task (identify which brief arguments
are material) leaves the realistic evaluation task incompletely validated.
Without a separate demonstration of correct materiality identification from raw
brief material, the coverage-completeness ranking signal is validated only for
a task structure that does not match the evaluation condition.

*SC6(b-2): accepted as appropriately specified.* The supportive camp specifies
SC6(b-2) as a naturalistic test with an explicit falsification criterion:
judges trained on anti-naturalistic SC6(b-1) pairs (where the complete decision
is shorter) must correctly rank the complete-and-elaborate decision as higher
in naturalistic SC6(b-2) pairs (where the complete decision is also longer).
This specification addresses the naturalistic generalization requirement the
adversarial paper introduced. SC6(b-2) as specified tests what it claims to
test. This requirement is accepted as appropriately operationalized.

*SC6(3) cross-elaboration test: the expert-assessment protocol is
question-begging.* The supportive camp proposes a specific cross-elaboration
methodology: two champions matched on doctrinal area, differentiated by
cluster-level adversarial record richness, with independent expert assessment
of reasoning-operation quality used to construct quality-discrepant pairs. The
falsification criterion: if higher-elaboration champions consistently win at
rates substantially above chance independent of expert-assessed
reasoning-operation quality, the abstraction instruction has not separated
argumentation quality from adversarial-record-driven elaboration.

The adversarial position is that the expert-assessment protocol is
question-begging. The test requires independent experts to assess
"reasoning-operation quality" in a way that is "in principle separable from
elaboration level generated by adversarial record richness." But this
separability is what the cross-elaboration test is designed to investigate;
specifying it as a condition on the expert assessment presupposes rather than
establishes it.

The problem appears in operationalizing the expert-assessment protocol for
ratio isolation (C1). In a high-adversarial-record case, the parties have
contested which precedential grounds are fundamentos determinantes; ratio
isolation requires distinguishing competing candidate rationes and identifying
which grounds are load-bearing for the holding. In a low-adversarial-record
case, the applicable ratio is more nearly settled; the isolation requires
identifying and articulating a ratio that is not seriously contested. Both are
instances of ratio isolation. An expert asked to assess which champion
demonstrates "higher reasoning-operation quality" on ratio isolation faces a
choice between two assessment standards.

Under a complexity-relative standard, the expert calibrates quality against
what the operation must accomplish — quality is assessed relative to how
difficult the isolation is. Under this standard, the expert's quality judgment
is adversarial-record-relative: what each champion had to accomplish is
factored in. The comparison across champions then tracks the adversarial record
that generated their respective difficulties, not a record-independent quality
level. The quality judgment is not independent of elaboration in the relevant
sense — it is calibrated to the elaboration that the case demanded.

Under a universal scale, the expert applies a single quality dimension
regardless of adversarial record context. Under this standard, a champion from
a high-adversarial-record cluster will systematically produce a more elaborately
structured ratio isolation — because the contested candidate rationes required
sustained discrimination — and expert judges applying the same universal scale
will identify that more elaborately structured isolation as higher quality. The
test would then confirm what the adversarial mechanism predicts: elaboration
richness arising from adversarial record differences systematically tracks what
independent experts identify as higher reasoning-operation quality.

The cross-elaboration test's validity requires the expert assessment to apply
the complexity-relative standard to produce quality judgments genuinely
independent of elaboration. But the complexity-relative standard requires
calibration: what is the appropriate quality level for ratio isolation given a
case of a specific adversarial record complexity? This calibration is not
operationalized in the proposed methodology. Inter-rater reliability on a
complexity-relative quality standard has not been established, and there is no
basis for expecting independent experts to agree on what "quality given record
difficulty" looks like when the record difficulties differ across clusters.
Without this operationalization, the expert-assessment protocol lacks the
specification needed to distinguish complexity-relative quality judgments from
complexity-insensitive elaboration-tracking. The falsification criterion — "if
higher-elaboration champions consistently win at rates substantially above
chance independent of expert-assessed reasoning-operation quality" — is
testable only if the expert assessments are genuinely independent of
elaboration. If experts implicitly apply a universal quality scale, their
assessments will correlate with elaboration, and the test will confirm that LLM
judges agree with experts — not that LLM judges are tracking something other
than elaboration-correlated quality. The expert-assessment protocol must
operationalize the complexity-relative standard and establish inter-rater
reliability on it as a prior empirical requirement of the cross-elaboration
test. That operationalization is not a feature of the current proposal.

**Eighth adversarial response — round 8: SC6(b-1) tests coverage-by-length
calibration, not general materiality identification; categorical composite
presupposes record-relative reference answers; three-measure composite omits
C3 and C4.**

The supportive round 8 paper addresses all three adversarial requirements from
round 7 with three responses: (1) SC6(b-1) anti-naturalistic pairs already
constitute the full-pipeline materiality-identification test, because an
elaborate-biased brief reader fails them; (2) SC6(b-2) acceptance is
acknowledged as a convergence point; (3) the cross-elaboration question-begging
is resolved by three categorical/ordinal measures — ratio identification
precision (ordinal 0/1/2, targeting C1), material argument engagement
completeness (proportion, targeting C2), and logical entailment validity of
dispositif (binary, targeting C5) — whose reference answers are established
"from the decision text and brief independently of adversarial record richness."
Three adversarial responses follow.

*SC6(b-1) pipeline coverage: anti-naturalistic pairs test one form of
elaboration-length bias, not the general materiality-identification task.*
SC6(b-1) calibration pairs are constructed with a pre-specified coverage
structure: annotators design one decision to cover all material arguments
briefly and another to cover some elaborately. An LLM trained on these pairs
learns to rank coverage over length when the naturalistic length-coverage
correlation is reversed. The pipeline claim is that passing this test
demonstrates the LLM correctly identifies material arguments from the brief
before assessing coverage.

The pipeline claim conflates the calibration setup with the realistic evaluation
condition. In calibration, the material argument set is embedded in the pair's
construction logic — annotators who know which arguments are material build the
pair around that pre-specified set. In realistic evaluation, the LLM receives a
(decision text + party brief) pair and must identify the material set from raw
brief content before coverage ranking. SC6(b-1) validates the downstream step
(coverage ranking when the material set is effectively given by pair
construction) but not the upstream step (materiality identification from novel
brief material with no pre-specification).

An LLM that learns "prefer shorter decisions on coverage when length and
coverage diverge" passes SC6(b-1) without having acquired correct
materiality-identification behavior from novel brief content. It could
simultaneously apply elaboration-biased materiality thresholds — treating
elaborately stated brief arguments as material regardless of legal foreclosure,
and briefly stated arguments as immaterial regardless of substantive strength —
while passing the anti-naturalistic pairs, because those pairs' pre-specified
material sets were established by annotators rather than constructed by the LLM
from the raw brief. The pipeline test the round 7 argument specified —
calibration pairs that directly test argument-level materiality judgment from
raw brief content, where the LLM receives a brief with no pre-specified material
set and must identify which arguments cross the art. 489, §1º, IV threshold
before coverage ranking — is not what SC6(b-1)'s anti-naturalistic structure
provides.

*Categorical composite reference answers presuppose adversarial-record-sensitive
construction.* The C1 measure's reference answer specifies the cited precedent's
fundamentos determinantes. In a high-adversarial-record case, the parties
contested which candidate grounds were determinantes; the court resolved that
contest. Establishing the reference answer requires identifying which candidate
ratio the court actually relied upon as determinante for the dispositif — a
determination whose analytical difficulty correlates with the number of contested
candidate rationes and the complexity of their resolution. For a
low-adversarial-record case where the applicable ratio is settled, the reference
answer requires identifying an uncontested ratio; for a high-adversarial-record
case, it requires resolving an interpretive question about the court's reasoning
structure. The 0/1/2 scoring scale is formally record-neutral; the reference
answer the scale is applied to is not.

The C2 measure's reference answer specifies the material argument list — which
brief arguments satisfy the art. 489, §1º, IV materiality threshold. This
requires exactly the materiality-identification assessment the round 7 argument
identified as C2-adjacent: whether a given argument, if accepted, would require
a different dispositif under the applicable legal standard. The categorical
composite relocates the complexity-relative problem from the scoring step to the
reference-answer construction step. The binary/ordinal scales provide
record-neutral output given the reference answers; they presuppose that the
reference answers themselves were constructed without adversarial-record-sensitive
analysis.

The operative diagnostic is differential inter-rater reliability: whether expert
annotators achieve comparable agreement on reference-answer construction for
matched high-adversarial-record and low-adversarial-record champions.
Uniform reliability across adversarial record contexts confirms the composite is
record-neutral at the construction level. Systematically lower reliability for
high-adversarial-record champions would confirm that reference-answer
construction is record-sensitive — that the complexity-relative problem has been
relocated rather than resolved. The supportive camp's failure condition refers to
"low inter-rater reliability" without specifying the diagnostic form: whether the
failure applies globally (agreement fails across the full sample) or
differentially (agreement is specifically lower for high-adversarial-record
cases). Differential reliability — not global reliability — is the operative
failure test for the specific claim that reference-answer construction is
adversarial-record-independent.

*Three-measure composite incompleteness: falsification criterion is ambiguous
for unmeasured dimensions.* The composite covers C1, C2, and C5 but not C3 or
C4. A champion from a high-adversarial-record cluster may be indistinguishable
from a matched low-adversarial-record champion on the three measured dimensions
while having genuinely higher C4 quality — contested-precedent cases required
more precise argumentation about which precedent applies and how its scope limits
the present case — or lower C3 quality — high-volume processing creates
routinization pressure on boilerplate avoidance independently of C1/C4
precision. Quality-discrepant cross-elaboration pairs constructed from the
three-measure composite may be quality-equivalent on the measured dimensions
while having real C4 or C3 differences undetected by the composite. LLM
rankings that partly reflect these unmeasured dimension differences produce the
same observable outcome as rankings driven by elaboration-richness from
adversarial record differences: the higher-elaboration champion consistently
wins at rates above chance independent of the three measured quality scores. The
falsification criterion cannot distinguish between these two interpretations.
A five-dimension composite, covering C4 through a record-neutral measure —
whether the decision correctly quotes or paraphrases the determinante in applying
the cited precedent — and C3 through a formulaic-language marker count
independent of case demands, would make the falsification criterion
interpretively unambiguous.

**Ninth adversarial response — round 9: C1 post-decision text-reading distinction
fails structurally in the high-adversarial-record arm through three text-level
features; C3 stylometric operationalization conflates legally mandated verbatim
text with formulaic reasoning avoidance; SC6(b-1)-ID presupposes dispositif
determinacy that complex cases do not guarantee.**

The supportive round 9 paper addresses all three adversarial requirements from
round 8 with three responses. Three adversarial responses follow.

*C1 post-decision text-reading: formally valid distinction, structurally undermined
in the cases that determine the differential inter-rater reliability test.* The
formal distinction between pre-decision analytical difficulty and post-decision
text-reading difficulty is accepted: annotators reading the court's text are not
performing the legal analysis that made the ratio hard to determine before the
decision was issued. The question is whether the decision text presents an
unambiguous ratio for annotators to read, specifically in the high-adversarial-record
arm where arm-specific differential reliability is the operative diagnostic.

Three structural features of high-adversarial-record cases produce text-level
ambiguity in the court's own ratio presentation that low-adversarial-record cases
do not exhibit.

First, negation-heavy reasoning structure. Courts in complex cases engage extensively
with the competing ratio characterizations that the parties contested — explaining
at length why each alternative interpretation fails before settling on the accepted
one. The decision text in high-adversarial-record cases therefore contains substantial
treatment of rejected characterizations, in the court's first-person judicial voice,
using the same rhetorical register as the court's affirmative ratio. Annotators must
distinguish passages where the court (i) states its accepted ratio from passages where
the court (ii) characterizes and then rejects the alternative argued by the losing
party. Both appear in the text as judicial reasoning; the structural signals
distinguishing them — rejection markers such as "não é correto afirmar que...",
"ao contrário...", "equivoca-se a parte quando..." — are often subtle and may be
parsed differently by different annotators. Low-adversarial-record decisions contain
no extended engagement with alternative characterizations: the court states its ratio
without sustained treatment of rejected alternatives. The ratio identification task
in low-adversarial-record text is correspondingly simpler.

Second, conjunctive and alternative grounds. Courts in high-adversarial-record cases
frequently provide multiple grounds for the same holding, without explicitly
designating which is the fundamento determinante for C1 purposes. Conditional
alternative formulations ("Mesmo que X não bastasse para sustentar a conclusão, o
resultado segue independentemente de Y") and conjunctive formulations ("A conclusão
decorre da conjunção de X e Y, sendo insuficiente qualquer um isoladamente") both
present X and Y as the court's reasoning. Whether X is the fundamento determinante
(Y being obiter), Y is (X being obiter), both are (conjunctive grounds), or neither
independently suffices (alternative grounds, neither alone being determinante) is not
resolved by the presence of both in the text. The decision text presents the court's
reasoning through both X and Y; annotators must determine which — if any — is the
fundamento determinante. This ambiguity is structurally more prevalent in
high-adversarial-record cases, where contested questions generate multi-ground
responses, than in low-adversarial-record cases with single-issue holdings where
the court's ratio characterization occupies a single paragraph.

Third, collegial fragmentation in multi-justice courts. In STF plenary decisions on
contested constitutional questions — the class of cases that ESHTR's cross-cluster
Phase 3 is specifically designed to rank, given the corpus focus on superior court
constitutional adjudication — the decision consists of multiple individual votes
(votos), each justice characterizing the ratio differently, emphasizing different
grounds, and reaching the same holding through different analytical paths. There is
no single text that presents "the court's own ratio characterization"; the court's
collective ratio must be synthesized from multiple concurrent characterizations. The
acórdão's ementa, which summarizes the holding, is produced by the court's
secretariat through interpretive work after the votes are registered; it is not the
justices' direct ratio characterization in the text of their opinions. For
high-adversarial-record STF plenary decisions — the cases most likely to appear in
clusters of constitutionally contested decisions — annotators constructing C1
reference answers must synthesize across fragmented collegial opinions rather than
reading a single court-authored ratio statement. This fragmentation is
adversarial-record-correlated: contested constitutional questions are precisely the
cases that reach the STF in plenary on divided votes, generating multi-opinion
decisions where synthesis difficulty is highest.

These three features are structural consequences of high adversarial record complexity:
more contested proceedings generate more extended judicial treatment of rejected
alternatives (Feature 1), more multi-ground holdings (Feature 2), and in the Brazilian
superior court context, more fragmented collegial opinions on the contested questions
that reach STF plenary (Feature 3). The supportive prediction of "comparable arm-
specific reliability" for C1 faces a structural counter-prediction: the post-decision
text in the high-adversarial-record arm is more ambiguous for annotators to read —
not from what the court had to determine before deciding, but from the textual
characteristics of how courts produce decisions when the pre-decision contest was
more complex. Pre-decision difficulty leaves post-decision textual traces that
generate arm-specific annotation difficulty for C1 reference-answer construction.

*C3 stylometric operationalization: within-cluster frequency thresholds cannot
distinguish legally mandated verbatim text from formulaic reasoning avoidance.* The
five-dimension composite's C3 operationalization — recurring phrases of five or more
consecutive words appearing in the reasoning sections of two or more cluster
decisions — adopts the adversarial camp's round 8 requirement for a
record-neutral C3 measure. The specific operationalization introduces a confound
that no frequency threshold can resolve: legally mandated verbatim text is
structurally indistinguishable from genuinely formulaic reasoning under within-cluster
frequency analysis.

Within ESHTR's fine-grained doctrinal clusters, decisions that correctly engage their
doctrinal question necessarily share mandatory verbatim text: statutory provisions
are quoted verbatim in reasoning sections as part of the analytical demonstration;
holding formulations of the leading precedents on the clustered question are quoted
verbatim as the authoritative statement of the applicable rule; procedural formulas
required by Brazilian appellate practice appear verbatim in every qualifying decision
of that type. In a fine-grained cluster of proportionality-of-sanction cases, every
decision that correctly engages the proportionality framework quotes the operative
statutory text and the leading STJ or STF holding on sanction proportionality.
Under the 5-word/2-decision threshold, this universally present mandatory text
generates cross-decision recurring phrases in the reasoning section of every cluster
decision — scoring every decision at the most severe (0) level on the stylometric
measure by structural necessity, regardless of whether the reasoning in which those
mandatory quotations are embedded is formulaic or case-specific.

CPC art. 489, §1º, III targets a different phenomenon: formulaic invocation of
authority without substantive engagement with the specific case — "se limitar a
invocar precedente ou enunciado de súmula, sem identificar seus fundamentos
determinantes nem demonstrar que o caso sob julgamento se amolda àqueles
fundamentos." The criterion is about reasoning engagement, not text novelty. A
decision that quotes the operative statute and leading precedent verbatim while
providing highly specific, case-tailored proportionality reasoning would score as
severe boilerplate under the stylometric measure but as high-quality under the
criterion. A decision that quotes the same authority verbatim while providing entirely
formulaic proportionality reasoning would score identically. The measure cannot
distinguish these cases because both use the same mandatory quotations — the
mandatory quotations generate the same cross-decision recurring phrases in both.

The adversarial camp's round 8 requirement was for a "formulaic-language marker
count independent of case demands." The adopted within-cluster phrase frequency is
independent of case demands in one sense (frequency is measured across the cluster
without case-specific analysis) but fails to count formulaic language in the relevant
sense: it counts text recurrence regardless of whether that recurrence reflects
mandatory citation practice or optional formulaic reasoning. Separating these two
sources of cross-decision text recurrence requires identifying which phrases are
legally mandated versus optionally formulaic — a categorization that requires
substantive legal content analysis, which the stylometric approach is designed to
avoid. The problem is categorical, not scalar: no frequency threshold distinguishes
mandatory from optional repetition because mandatory repetition appears in every
cluster decision and optional formulaic repetition appears in some — both generating
frequencies at or above the threshold in fine-grained clusters where mandatory
citation concentrates.

*SC6(b-1)-ID tractability: the outcome-dependency materiality standard presupposes
dispositif determinacy that adversarial record complexity erodes.* The supportive
characterizes the SC6(b-1)-ID materiality-identification task as tractable through
a structural assessment: an argument is material if accepting its conclusion would
require a different dispositif — a determination that requires reading what the
argument claims and what the court decided, without full adversarial record analysis.

In cases with determinate single-component dispositifs, this assessment is tractable.
In cases where the dispositif has multiple components — partial grants and partial
denials, holdings on multiple issues, rulings on sequenced sub-findings — the
outcome-dependency assessment requires a prior mapping: which component of the
dispositif does this argument address, and is that component independently supported
by other grounds? An argument that, if accepted, would affect one component of a
holding independently supported by additional grounds that remain unchallenged is
non-material under outcome-dependency — the conclusion would not change even if the
argument were accepted, because the remaining grounds sustain it. An argument that
attacks one of two disjunctive alternative grounds for the same holding is similarly
non-material under strict outcome-dependency if the other alternative independently
suffices.

The difficulty of this mapping — ground independence, conjunctive/disjunctive
structure, which components of the dispositif each argument addresses — scales
directly with adversarial record complexity. High-adversarial-record cases produce
complex dispositifs for the same reason they produce negation-heavy texts and
multi-ground holdings: the parties contested multiple issues simultaneously, generating
multiple decisional components and multiple independent grounds. The tractability that
the outcome-dependency standard provides in simple cases — read the argument,
read the holding, check if they conflict — gives way in complex cases to a dispositif-
parsing step whose difficulty tracks adversarial record complexity.

"Clearly-material, clearly-immaterial, and borderline cases" in calibration examples
operationalize the outcome-dependency standard for calibration-visible cases. They do
not establish that the trained LLM achieves comparable materiality-identification
reliability across arms when encountering novel high-adversarial-record brief-
dispositif pairs where dispositif complexity makes the argument-to-component mapping
non-trivial. The differential inter-rater reliability concern the round 8 adversarial
response identified for reference-answer construction at the scoring step applies at
the SC6(b-1)-ID calibration annotation step itself: whether annotators establishing
the material argument set for high-adversarial-record brief-dispositif pairs achieve
agreement levels comparable to annotators working on low-adversarial-record pairs is
an empirical question the tractability claim assumes but the calibration design must
separately establish.

**Tenth adversarial response — round 10: C3 official-database preprocessing accepted
with residual institutional-convention gap; C1 ementa-reading source reduction accepted
with two annotation-task limits — implicit-structure ementas and principle-level
abstraction; SC6(b-1)-ID quality-filter narrowing accepted with ementa-theory
generality as residual.**

The supportive round 10 paper makes three genuine advances: (1) ementa-as-authoritative-
ratio — the C1 annotation task reads the cited precedent's ementa rather than synthesizing
across votos, converting collegial fragmentation from a multi-document synthesis problem to
a single-document reading task, with protocol-specified logical-operator resolution rules
for ementas containing explicit conjunctive/alternative connectives; (2) mandatory-text
preprocessing — an official-database corpus (Portal da Legislação, Diário Oficial, STF/STJ
súmulas) strips legally-mandated verbatim text from reasoning sections before within-cluster
phrase frequency computation, with validation through cross-cluster C3 variance convergence;
(3) court-stated-theory constraint — annotators identify the court's stated legal theory
from the decision text and assess argument materiality under that framework, reducing the
genuinely intractable cases to the intersection of ambiguous-court-theory and
multi-component-dispositif, with the quality-filter further shrinking the hard-case class
within the calibration corpus. All three are accepted as substantive advances. The residual
concerns follow.

*C3 preprocessing: official-database coverage with two residual gaps.* The preprocessing
design is accepted as the correct approach and as addressing legally-mandated text
conflation for the categories covered by official databases: constitutional and statutory
provision text, formally enacted STF/STJ súmulas, and standard statutory formulas
expressly prescribed by procedural legislation. For these categories, official-database
matching provides tractable preprocessing independent of legal content analysis.

Two residual source categories fall outside official-database coverage. First, mandatory
text from court-specific procedural rules: Regimento Interno provisions of the STF and
STJ generate mandatory procedural formulas — standard admissibility disposition language,
session-record formulas, and required characterization language for specific procedural
determinations — that appear verbatim across decisions of the relevant procedural types
but are not in Portal da Legislação or Diário Oficial. Second, institutionally conventional
formulas: standard dispositif language, opening and closing structures for votos and
acórdãos, citation-style templates, and institutional phrases that have become uniform
through appellate practice without statutory or Regimento mandate. Both categories
generate within-cluster phrase frequencies at or above the 5-word/2-decision threshold
in fine-grained doctrinal clusters without tracking reasoning quality, and neither is
identified or removed by official-database preprocessing.

After official-database stripping, the residual phrase frequency in reasoning sections
reflects a mixture of genuine boilerplate reasoning avoidance (what C3 targets),
court-specific Regimento Interno formulas, and institutionally conventional language.
Whether these residual categories materially contaminate the C3 signal in the
calibration corpus is an empirical question the current specification does not address.
A cross-cluster-convention stripping step — identifying phrases appearing universally
across multiple doctrinal clusters regardless of subject matter as institutional-convention
candidates, and removing them before within-cluster frequency computation — would address
both residual categories. This step is not specified in the round 10 proposal. Surrender
condition (g) is updated to reflect that official-database preprocessing satisfies the
condition for legally-mandated text in the covered categories; the cross-cluster-convention
stripping step is required for the two residual categories.

*C1 ementa-as-authoritative-ratio: source reduction accepted; two annotation-task limits
remaining.* The source-reduction benefit is fully accepted: reading the ementa is simpler
than synthesizing across votos, and collegial fragmentation at the annotation-source
level is addressed. Protocol-specified logical-operator resolution rules eliminate
annotator discretion for ementas containing explicit conjunctive or disjunctive
connectives.

Two annotation-task limits remain.

First, implicit-structure ementas. Constitutional decisions on contested multi-issue
holdings often produce ementas listing grounds without explicit logical operators:
"Fundamentos: (i) violação ao art. X; (ii) ofensa ao princípio Y; (iii) contrariedade ao
precedente Z." Whether each listed ground is independently sufficient, conjunctive-
necessary, or hierarchically subordinated is not stated in such ementas. The protocol
resolution rules apply when the logical structure is explicit; they do not determine the
annotation for ementas with implicit or unlabeled multi-item ground structures, which
require reading the underlying votos to establish the logical relationship among grounds.
This class is not the majority case, but it is disproportionately represented in contested
constitutional adjudication, where multi-issue holdings generate multi-item ementas
without explicit inter-item connectives.

Second, principle-level abstraction. Ementas of contested STF constitutional decisions
characterize the ratio at the level of the governing constitutional principle, not at the
level of the specific doctrinal construction that was the fundamento determinante. This
abstraction is a structural property of constitutional precedential documentation: inferior
courts and parties invoking the precedent must be able to apply it across a range of
specific factual configurations, so the ementa characterizes the ratio at a level of
generality sufficient for downstream application. The C1 task for ESHTR requires
determining whether the citing court correctly identified the fundamentos determinantes
at the level where the citing court's analysis operates — the doctrinal-specific level.
The ementa's principle-level characterization is consistent with multiple specific
doctrinal constructions of the ratio; the annotator must determine which construction the
cited precedent resolved and whether the citing court's identification maps to the correct
one. This determination requires legal judgment about what the ementa's principle-level
statement implies at the specific doctrinal level where the cited case was decided. For
contested STF constitutional precedents — the high-adversarial-record class — the
underlying decision resolved which of multiple competing specific constructions was the
fundamento determinante; the ementa documents that resolution at the principle level
without specifying which construction.

The surviving arm-specific differential IRR concern for C1: not voto-synthesis difficulty
(addressed by ementa reading), but ementa-interpretation difficulty for decisions where
the ementa's principle-level characterization does not directly resolve which specific
doctrinal construction was the fundamento determinante. This class is concentrated in
contested STF constitutional decisions — the high-adversarial-record arm.

*SC6(b-1)-ID court-stated-theory constraint: narrowing accepted; ementa-theory generality
as residual.* The court-stated-theory constraint is accepted as a genuine narrowing. The
quality-filter argument — that high-quality calibration decisions tend not to have
ambiguous court-stated theories — is accepted as reducing the hard-case class within the
calibration corpus. Two residual considerations follow.

First, calibration-scope representativeness. If ESHTR's evaluation target extends beyond
quality-filter exemplars to the broader appellate corpus, the calibration's reliability
on clearly-stated-theory cases does not establish comparable SC6(b-1)-ID reliability for
evaluation cases with less clearly expressed court theories. The calibration scope needs
to specify how the quality-filter boundary maps onto the evaluation target's distribution.

Second, ementa-theory generality. The court's stated theory, for contested STF
constitutional decisions, is characterized in the ementa at the same principle-level
abstraction that generates the C1 annotation-task limit described above. Using the
ementa's theory characterization as the operative outcome-dependency framework —
assessing whether accepting a brief argument would require a different dispositif under
the principle-level theory — encounters the same interpretation problem: the
principle-level characterization is consistent with multiple specific legal constructions,
and determining whether a particular brief argument would affect the dispositif under the
court's specific construction requires the doctrinal judgment the court-stated-theory
constraint is intended to avoid. This residual is concentrated in the same
contested-constitutional class as the C1 annotation-task limit.

*Note on cross-front ementa positions.* Round 9 of this paper accepted the
ementa-as-authoritative-ratio reconceptualization for its source-reduction benefit. The
adversarial paper on Paper 1C (`otherwise/paper1c-formalization-tractability.md`, §3.7)
argues that STF constitutional ementas generalize to principle-level language, making SC7
ementa cross-referencing require legal judgment rather than structural comparison. These
positions address different annotation demands and are compatible. The ESHTR C2 concession
addressed annotation source reduction — reading one authoritative document rather than
synthesizing across multiple votos. The Paper 1C argument addresses annotation task demands
at the doctrinal-specificity level required for thread-contingency determination. The
ementa simplifies the source; its principle-level generality limits operations requiring
doctrinal-specific identification in both contexts. Both positions are consistently
maintained.

**Eleventh adversarial response — round 11: C1 relocation accepted at annotation-source
level; annotation-task challenge preserved through citing-court characterization mismatch
at the principle-to-application gap; type (a)/(b) demarcation presupposes established-
application-area knowledge; implicit-structure flagging rate is a resource-constraint at
champion scale in the contested-constitutional arm; C3 cross-cluster-convention stripping
leaves procedural-type-specific institutional formulas unaddressed.**

The supportive round 11 makes four advances: C1 principle-level abstraction relocated
from C1 to SC6(b-1)-ID ementa-theory generality, with C1 annotation recast as textual
comparison of the citing court's characterization against the ementa at the ementa's level;
supplementary C3 cross-cluster-convention stripping identifying institutional-convention
candidates through cross-corpus phrase frequency across three or more unrelated doctrinal
clusters; mandatory C1 implicit-structure flagging routing ementas with unlabeled multi-item
grounds to expert review; and SC6(b-1)-ID type (a)/(b) narrowing into established
application areas (text-mapping tractable) and novel conceptual extensions (bounded hard
core requiring expert calibration). Four adversarial responses follow.

*C1 relocation: annotation-source benefit fully accepted; annotation-task challenge
preserved through citing-court characterization mismatch.* The relocation is accepted as
correctly identifying the annotation source: annotators read the cited precedent's ementa
rather than synthesizing across votos. The source-reduction benefit — ementa reading is
simpler than voto synthesis, collegial fragmentation is addressed at the source level —
is accepted unconditionally. The concession from round 9 that accepted the ementa-as-
authoritative-ratio source-reduction benefit is fully incorporated and not revisited.

What the relocation does not establish is that C1 annotation is tractable at the
annotation-task level. The annotation task is not ementa-reading alone; it is comparison
of the citing court's ratio characterization against the ementa. The mismatch: the citing
court characterizes the cited precedent's fundamentos determinantes at the specific
doctrinal level at which it is applying the precedent — "the cited precedent establishes
that rule R holds in situation S." The ementa characterizes the cited ratio at the abstract
constitutional-principle level — "constitutional principle P applies." Whether rule R in
situation S is a fundamento determinante of the cited precedent — rather than an obiter
elaboration of principle P that the citing court incorrectly elevated to load-bearing
status — requires determining what the ementa's principle-level characterization implies
at the specific doctrinal level of the citing court's application. This is not ementa-
reading at the ementa's level of characterization; it is principle-to-application-level
gap-filling.

For cases where the specific application is settled and uncontested, this gap is closed
by precedential record: the annotator recognizes rule R in situation S as a well-
established application of principle P. This is the type (a) class. For cases where the
specific application is contested — where parties dispute whether rule R in situation S is
within the established scope of the precedent's fundamentos determinantes or an overreading
of the abstract principle — the ementa-level comparison does not resolve the annotation
task. The ementa states principle P without specifying which competing specific
constructions of P are fundamentos determinantes at the doctrinal level. This is the
type (b) class, where the annotation-task challenge survives the source-reduction move.

The relocation converts the annotation task from multi-voto synthesis (what is the
precedent's ratio?) to principle-to-application mapping (is the citing court's specific
characterization within the ementa's established scope?). The annotation-source
simplification is genuine; the annotation-task challenge for the type (b) class is
unchanged in kind, only re-described in terms consistent with the ementa-reading model.

*Type (a)/(b) demarcation presupposes established-application-area knowledge.* The type
(a)/(b) distinction is accepted as correctly identifying two categories. The operative
question is whether the demarcation step is tractable without the doctrinal expertise the
classification aims to avoid.

Identifying which specific doctrinal constructions fall within the established application
areas of a given abstract constitutional principle requires knowledge of the accumulated
doctrinal record: how courts and parties have treated specific applications of the abstract
principle across the precedential history. For routine constitutional applications — where
the specific construction has been repeatedly applied and its fundamento determinante status
is uncontested across the precedential record — type (a) classification is tractable. For
contested constitutional applications — where parties in the citing case dispute whether
the specific construction is within the established scope of the abstract principle's
fundamentos determinantes — the type (a)/(b) demarcation is not determinable from the
ementa alone. The ementa's abstract-principle characterization is consistent with both
the established-application and the novel-extension classification for the same specific
construction.

The structural point: in the high-adversarial-record arm, "established application area"
for the contested constitutional principle is itself the object of the dispute. A citing
court invokes the precedent for the specific proposition that rule R applies in situation
S; the challenging party argues this construction is a novel extension. Whether R in S is
type (a) or type (b) is precisely what the annotation must determine. The demarcation step
therefore imports the doctrinal-expertise requirement into the classification that precedes
annotation: placing a citing court's characterization in type (a) or type (b) requires
knowing the history of established applications of the abstract principle at the doctrinal
level — the same knowledge annotators are not expected to possess for the ementa-reading
step that the relocation makes tractable. This is not a claim that the type (a)/(b)
distinction fails conceptually; it is a claim that the type (b) hard core is concentrated
in the contested-constitutional cases precisely where the demarcation requires the
doctrinal judgment the expert-review escalation is meant to catch.

*Implicit-structure flagging: accepted as annotation-source solution; class-size concern
in the contested-constitutional arm.* The mandatory-flagging step for ementas listing
grounds without explicit logical connectives is accepted as addressing the annotation-
source ambiguity for that class. The operative concern is the class-size distribution
across arms.

Contested constitutional adjudication at the STF plenary level — the source of the
high-quality champions Phase 3 requires — produces multi-issue decisions whose ementas
list grounds without explicit connectives at systematically higher rates than routine
constitutional applications. Two structural factors drive this: complex constitutional
cases resolve multiple contested issues simultaneously, generating multi-item ground
listings; and secretariat-authored ementas serving as cross-court citation resources favor
listing formats — allowing other courts to identify the relevant ground for their case —
over logical-structure specifications that would require parsing the full deliberation. If
the flagging rate for the contested-constitutional arm substantially exceeds the rate for
routine constitutional applications, the mandatory-flagging solution converts the
annotation tractability problem into an operational-capacity constraint at champion scale:
expert review becomes the dominant annotation pathway for exactly the decisions Phase 3
requires. The solution is architecturally valid; its operational tractability depends on
the flagging-rate distribution across arms, which the round 11 proposal does not specify.
Surrender condition (f) is updated to require arm-specific implicit-structure flagging
rates alongside the arm-specific IRR data the prior rounds established.

*C3 cross-cluster-convention stripping: frequency criterion addresses cross-doctrinal-
subject universals; procedural-type-specific institutional formulas survive.* The cross-
cluster-convention stripping step is accepted as a genuine advance for the categories it
covers. Phrases appearing across three or more unrelated doctrinal clusters are correctly
identified as institutional-convention candidates without requiring legal-content analysis;
the surrender condition (g) is partially met for universally-conventional institutional
formulas, and this advance is accepted unconditionally.

The remaining gap concerns procedural-type-specific institutional formulas. Brazilian
appellate decisions cluster by both doctrinal subject matter and procedural posture:
habeas corpus petitions, recursos especiais, mandados de segurança, and recursos
extraordinários each generate procedurally conventional language — standard admissibility
characterizations, petition-opening and closing structures, reasoning-section transitions
— that is universal within the procedural type but not distributed across doctrinal-
subject clusters. A mandatory admissibility characterization formula for habeas corpus
appears in all habeas corpus decisions regardless of underlying criminal-law question, but
does not appear in tax-law recurso especial clusters or administrative-law mandado de
segurança clusters. The three-cluster frequency criterion — applied across doctrinal-
subject clusters — does not identify procedural-type-specific conventional language because
its distribution is concentrated within procedural-posture clusters rather than spread
across doctrinal-subject clusters.

After both preprocessing steps, within-cluster phrase frequency analysis in procedural-
posture clusters captures mandatory procedural formulas and optional formulaic reasoning
equally: both appear universally within habeas corpus clusters, for instance, generating
within-cluster recurrence at or above the threshold. The cross-cluster criterion removes
the habeas corpus formula from doctrinal-subject clusters where it does not appear; it
does not remove it from within the habeas corpus procedural cluster where it appears
universally. The C3 conflation problem for this category survives both preprocessing
steps — mandatory and optional formulaic recurrence remain indistinguishable by within-
cluster frequency analysis after stripping, for the same categorical reason the original
round 9 argument established.

Surrender condition (g) is updated: official-database preprocessing satisfies the
condition for universally-mandated text categories; cross-cluster-convention stripping
satisfies it for court-universally-conventional institutional formulas; procedural-type-
specific institutional formulas constitute a third residual category. A posture-type
stripping step — identifying phrases appearing across instances of the same procedural
type regardless of doctrinal subject matter — analogous to the cross-cluster step but
applied within procedural-posture groupings, is required to close the residual.

**Twelfth adversarial response — round 12: posture-type stripping accepted; type (b) shared-infrastructure accepted; Jurisprudência Temática/Teses granularity does not reach doctrinal-specific fundamento determinante identification; currency limitation in the contested-boundary subclass of the high-adversarial-record arm; secretariat authorship convention claim lacks documentary basis.**

The supportive round 12 makes four advances: (1) posture-type stripping — a third C3 preprocessing layer stripping phrases appearing in more than 90% of decisions of each procedural type across all doctrinal clusters before within-cluster frequency computation, with within-posture-type cross-cluster C3 variance as the validation check; (2) type (a)/(b) demarcation operationalized via the STF's Jurisprudência Temática and the STJ's Jurisprudência em Teses as a database-lookup task parallel in structure to C3's official-database preprocessing; (3) implicit-structure flagging rate contested as a structural inference that overlooks STF secretariat conventions favoring explicit logical structure for high-profile constitutional ementas, with the rate to be determined empirically by pre-calibration pilot; (4) type (b) gap-filling via the same expert-review infrastructure already required for implicit-structure ementa C1 annotation, with combined class-size determined by the same pilot. Four adversarial responses follow.

*Posture-type stripping: accepted.* The three-layer combined preprocessing sequence — official-database, cross-cluster-convention, posture-type — addresses all three C3 residual categories the adversarial identified across rounds 9–11: universally-mandated text, court-universally-conventional institutional formulas, and procedural-type-specific institutional formulas. The validation criterion (within-posture-type cross-cluster C3 variance approaching zero after all three preprocessing layers) is correctly specified and makes the adequacy claim falsifiable. Accept unconditionally. Surrender condition (g) is updated to reflect that the posture-type stripping layer closes the procedural-type residual; full satisfaction requires implementation of all three preprocessing layers with convergent within-posture-type cross-cluster C3 variance confirmed at the validation step.

*Type (b) shared-infrastructure gap-filling: accepted.* The shared expert-review infrastructure for type (b) SC6(b-1)-ID annotation and implicit-structure ementa C1 annotation is accepted as a valid cost-reduction argument. Both annotation classes use the same expert substrate; the pre-calibration pilot measures the combined class size from both. If the combined class size is manageable, the shared infrastructure is a genuine cost-reduction; if large, both classes compound a single bottleneck. Accept the shared-infrastructure framing. The empirical constraint — the arm-specific combined class size from the pilot — is the only remaining question on the calibration design's operational feasibility.

*Jurisprudência Temática/Teses granularity: the structural parallel to C3 preprocessing does not extend to doctrinal-specific fundamento determinante identification.* The structural parallel to C3 official-database preprocessing is accepted in principle: both tasks involve querying an authoritative document set to classify a citing court's action against an established reference without requiring independent legal-content analysis at the annotation step. The analogy identifies a genuine structural similarity. What the analogy does not show is that the query is granular enough for the C1 annotation task.

C3 official-database preprocessing matches text verbatim: the reasoning section contains "Art. 5°, caput, da Constituição Federal" and the official database contains that provision's verbatim text. The match is mechanical and unambiguous. The Jurisprudência Temática/Teses database-lookup classifies a citing court's doctrinal characterization against the compilation's named-entry thematic categories. The STF's Jurisprudência Temática and the STJ's Jurisprudência em Teses enumerate established applications of constitutional and statutory principles at the thematic level: "proporcionalidade nas sanções administrativas," "contraditório e ampla defesa em procedimentos administrativos," "tutela cautelar em matéria tributária." These entries confirm that the abstract constitutional principle has established applications in the thematic domain. They do not enumerate which specific doctrinal constructions of the principle — which particular formulations of the principle's requirements at the operative level where citing courts apply it — have been established as fundamentos determinantes.

A citing court that characterizes the cited precedent as establishing "proportionality requires individualized enumeration of each aggravating factor in the sanctioning decision as a fundamento determinante" matches the thematic entry for administrative-sanctions proportionality. The database returns type (a). The C1 annotation task requires determining whether individualized factor enumeration specifically — as distinguished from proportionality's application to the sanction outcome generally — is a fundamento determinante of the cited precedent or a doctrinal construction the citing court incorrectly elevates from the abstract principle. The thematic-level entry does not resolve this: it establishes that proportionality applies to administrative sanctions; it does not specify which doctrinal constructions of proportionality's requirements in that domain are fundamentos determinantes at the level where the citing court's analysis operates.

This granularity gap is structurally parallel to the gap that survived the ementa-as-authoritative-ratio source-reduction move in round 10. Round 10's concession accepted that reading the cited precedent's ementa is simpler than synthesizing across votos. The annotation-task challenge preserved was the principle-to-application-level mismatch: the ementa characterizes the ratio at the abstract-principle level while the citing court characterizes the fundamento determinante at the doctrinal-specific level. The Jurisprudência Temática operationalization addresses the same granularity level as the ementa: it enumerates established thematic applications of the abstract principle. Neither the ementa nor the compilation specifies which particular doctrinal constructions within the thematic domain are fundamentos determinantes. The database-lookup provides the same structural confirmation the ementa provides — that the abstract principle has established application to the thematic domain — and inherits the same annotation-task challenge the ementa leaves unresolved at the doctrinal-specific level.

*Currency limitation in the contested-boundary subclass.* A second structural constraint limits the database-lookup operationalization in the high-adversarial-record arm. The high-adversarial-record arm consists disproportionately of cases where parties contest the scope of an established constitutional doctrine — specifically, whether the doctrinal construction the citing court characterizes as the fundamento determinante is within the established application or a novel extension. These are precisely the cases where the Jurisprudência Temática/Teses compilations have not yet produced an authoritative classification of the contested construction: the compilations document settled doctrine; contested-boundary interpretive developments appear in the compilation only after they are resolved through the adjudicative process that generates the high-adversarial-record cases in the calibration corpus. The calibration corpus's high-adversarial-record cases are drawn from contested interpretive contexts by construction: adversarial record richness indexes contested interpretive boundaries. For the database-lookup to classify a case as type (a), the compilation must contain an entry identifying the specific doctrinal construction as an established application at the time of corpus assembly. In the contested-boundary subclass of the high-adversarial-record arm, the compilation is silent on precisely the question the annotation must determine — because the litigation is the mechanism by which that classification is eventually established. The database-lookup defaults the unclassified case to type (b): not-type-(a). This is also what the adversarial predicts: the type (b) hard core is concentrated in contested-boundary cases where both the granularity and currency limitations operate simultaneously. The currency limitation does not defeat the database-lookup operationalization for paradigm type (a) cases; it confirms that the type (b) hard core remains in the contested-constitutional class.

*Secretariat authorship convention: asserted mechanism, not documented practice.* The supportive round 12 contests the adversarial's implicit-structure flagging rate prediction on the grounds that STF secretariat authorship conventions for high-profile constitutional ementas favor explicit logical structure for precedential clarity. This counter-inference is presented without documentary basis. The round 12 filing does not identify a STF secretariat authorship guideline, ementa drafting convention document, administrative directive, or empirical comparison of ementa logical-structure rates against multi-issue holding characteristics establishing that high-profile constitutional ementas systematically favor explicit logical connectives over listing formats.

The adversarial's flagging-rate prediction rests on two independently stated structural drivers: (i) contested constitutional cases resolve multiple issues simultaneously, generating multi-item ground listings by structural necessity; (ii) ementas serving as cross-court citation resources favor listing formats that allow each downstream court to identify the relevant ground for its specific case without parsing logical dependencies among all grounds. Both drivers follow from the institutional function of ementas and the structural characteristics of contested constitutional adjudication. The supportive's counter-inference requires a convention that overrides both drivers simultaneously — a drafting practice mandating explicit logical connectives in ementa multi-item ground listings for high-profile constitutional decisions in spite of the cross-court applicability function that favors listing formats. Whether such a convention exists and dominates the two structural drivers is a factual question about STF secretariat drafting behavior that the round 12 filing neither documents nor cites. The pre-calibration pilot measurement is the correct resolution; the adversarial does not contest this. What the adversarial presses: an asserted convention that overrides two independently grounded structural pressures requires documentary support before it can constitute a structural rebuttal to the adversarial's rate prediction. Until the pilot data is available, both sides' rate projections are structurally inferred; the adversarial's projection has two stated structural drivers, and the supportive's has one mechanism claim that presupposes an undocumented convention.

**Thirteenth adversarial response — round 13: step-1/step-2 distinction correctly identifies the compilation's step-1 role and the ementa's step-2 role; it does not address the annotation task at step 2, where the citing court's doctrinal-specific characterization must be compared against the ementa's abstract-principle characterization; currency limitation accepted; secretariat convention withdrawal accepted.**

The supportive round 13 makes four moves: (1) reconfirms posture-type stripping and type (b) shared-infrastructure acceptances from round 12; (2) responds to the granularity challenge with a step-1/step-2 structural distinction — the compilation (Jurisprudência Temática/Teses) performs step 1 (domain classification for type (a)/(b) demarcation), the ementa performs step 2 (fundamento determinante characterization for C1 annotation), and C1 requires step 2 which the ementa supplies at principle level; (3) accepts the currency limitation as correctly describing the type (b) default rule's operation; (4) withdraws the secretariat authorship convention claim and names the pre-calibration pilot as the sole resolution for the implicit-structure flagging rate. Three adversarial responses follow.

*Step-1/step-2 distinction: analytically correct as a description of document functions; does not address the annotation task at step 2.* The structural distinction is accepted as accurate. The compilation performs step 1: it classifies the cited precedent's established application to a thematic domain, enabling the type (a)/(b) demarcation that routes annotation to text-mapping or expert review. The ementa performs step 2: it supplies the authoritative characterization of the cited precedent's fundamentos determinantes at the abstract-principle level. C1 annotation uses the ementa as its step-2 source document — this was the round 10 ementa-as-authoritative-ratio concession, not re-contested here. The step-1/step-2 framing accurately describes which document serves which protocol function.

What the distinction does not address is the annotation task's internal structure at step 2. The step-2 document-level function is: the ementa supplies the principle-level characterization. The step-2 annotation task is: the annotator compares the citing court's characterization of the cited ratio against the ementa's characterization. These are not the same operation. The citing court characterizes the cited ratio at the doctrinal-specific level — "the cited precedent establishes that rule R in situation S is the fundamento determinante." The ementa characterizes the cited ratio at the abstract-principle level — "principle P applies." Whether the citing court's doctrinal-specific characterization (rule R in situation S) correctly maps to the ementa's abstract-principle characterization (principle P) requires determining what the ementa's abstract statement implies at the specific doctrinal level where the citing court operates. This is not ementa-reading at the ementa's characterization level; it is principle-to-application-level assessment — the same gap the round 11 argument established as the surviving annotation-task challenge after the source-reduction move. The step-1/step-2 distinction resolves a source-selection question that round 10 already resolved; it does not alter the structure of the task the annotator performs once the ementa is selected as the step-2 source.

The supportive's formulation — "C1 annotation requires step 2, which the ementa supplies at principle level" — is correct about the document the annotation reads but incomplete about the task the annotation performs. The ementa supplies one side of the comparison (the abstract-principle characterization of the cited ratio); the citing court's text supplies the other side (the doctrinal-specific characterization of what the citing court claims the cited ratio establishes at the operative level). The two sides are at different levels of specificity. The comparison across levels is the annotation task, and this comparison requires principle-to-application assessment. The step-1/step-2 distinction correctly identifies which document performs which protocol function; it establishes the ementa as the step-2 source, which round 10 already established; it does not establish that the comparison the annotator performs at step 2 is tractable within the ementa's characterization level.

The round 12 granularity challenge was not about which document is the step-2 source. It was about whether the C1 annotation task can be performed tractably at the granularity the ementa supplies (principle level) when the citing court's characterization operates at the doctrinal-specific level. The step-1/step-2 distinction responds to a question the adversarial did not ask — which document is the step-2 source — rather than the question the adversarial did ask — whether the step-2 task is tractable across the specificity gap. Naming the compilation as step 1 and the ementa as step 2 correctly describes the demarcation-to-annotation protocol structure; it does not address whether the annotation at step 2 can be performed without crossing the specificity gap from principle level to doctrinal-specific level.

*Currency limitation: accepted.* The supportive's acceptance of the currency limitation as the correct operational description is accepted without further contest. Conservative routing of compilation-absent arguments to type (b) expert review is the operationally appropriate response to the lag-window effect. The lag-window class size in the contested-boundary subclass of the high-adversarial-record arm is the empirical question determined by the pre-calibration pilot. The currency limitation compounds with the granularity gap in the contested-boundary subclass: both limitations operate simultaneously on the cases where the annotation task is hardest, concentrating type (b) routing where the step-2 annotation task is structurally most complex. The pilot's operational significance is therefore not only the class size but the class composition: cases simultaneously requiring type (b) routing and step-2 gap-crossing are the maximum annotation-cost class.

*Secretariat convention withdrawal: accepted.* The withdrawal is accepted as the epistemically honest response. The pre-calibration pilot is the correct arbiter. The adversarial's two structural drivers for its implicit-structure flagging rate prediction are stated structural inferences, not documented rates; the supportive's convention claim was a structural inference in the same epistemic category. Neither side has documented the flagging rate; both have stated structural arguments for their projections. The pilot resolves which projection is empirically borne out.

**Fourteenth adversarial response — round 15: C1/C4 structural distinction accepted as formally valid; purely designative reading of *identificar* contested — *identificar fundamentos determinantes* is a conceptual-coverage judgment that requires the annotator to determine whether what the citing court identifies as a fundamento determinante IS one, not only whether any principle from the ementa was named.**

The supportive round 14 advances an acknowledgment-checking account grounded in the C1/C4 structural distinction. Four positions follow.

*C1/C4 structural distinction: accepted as formally valid.* Art. 489, §1º, V (*identificar*) and Art. 927, §1º (correct application, distinction, justified deviation) are structurally distinct functions that are not redundant: if C1 required correctness-assessment, C4's independent function for binding precedent invocations would be eliminated. The adversarial accepts this structural observation. C1 and C4 operate at different analytical points in the rubric, and the two-provision structure establishes their distinctness from the enacted text.

*Purely designative reading of *identificar*: contested.* The acknowledgment-checking account derives annotation-task tractability from characterizing *identificar* as purely designative — the citing court need only name the abstract principle the ementa states; no determination of whether the specific construction is within the principle's scope is required. This reading is textually contestable on two grounds from the statute's own language.

First, the possessive *seus* in Art. 489, §1º, V — "sem identificar *seus* fundamentos determinantes" — refers to the cited precedent's actual fundamentos determinantes. The provision's failure condition is "without identifying ITS fundamentos determinantes," not "without naming any principle that appeared in the ementa." This formulation implies that the fundamentos determinantes are an objective feature of the cited precedent that the citing court must correctly recognize. A purely designative reading that accepts any named principle from the ementa as satisfying the identification requirement does not test whether what was named is in fact one of the cited precedent's fundamentos determinantes.

Second, Art. 489, §1º, VI's parallel formulation is non-designative: "sem identificar os fundamentos determinantes do precedente *que justifiquem a aplicação ao caso sob julgamento*." The *que justifiquem* clause specifies that the identified grounds must be grounds that actually justify the case-specific application — the identified grounds must have the property of being justifying, not merely of having been named. VI's *identificar* carries substantive identification content. Provisions V and VI are independent failure conditions within the same legal sentence, not sequential steps; V's *identificar* must carry its own content independent of VI's *que justifiquem* clause. If V's *identificar* were purely designative (name any principle), then V's failure condition would be exhausted by the mere absence of any principle name — a thin requirement that would not distinguish a decision that nominates the wrong grounds from one that names no grounds at all. VI's structure confirms that *identificar* in the binding-precedent context refers to identifying grounds that have a substantive relationship to the cited precedent, not merely naming them.

*Third case the purely designative reading misses.* The supportive's two-case analysis covers: (a) no principle named → C1 fails; (b) abstract principle P named → C1 satisfied, correctness handled by C4. A third case falls outside this analysis: a citing court names principle P from the ementa but identifies a specific proposition as the fundamento determinante that was in fact obiter in the cited precedent — P was genuinely present in the cited decision, but the specific construction the citing court nominates as P's fundamento determinante was not determinative for the holding; it was an incidental observation the deciding court did not rely upon. Under the purely designative reading, case (c) satisfies C1 (P was named). Under the statute's failure condition — invoking a precedent without identifying its fundamentos determinantes — case (c) is precisely the failure the provision targets. A citing court that elevates an obiter dictum to fundamento determinante status has not identified the cited precedent's fundamentos determinantes; it has nominated the wrong ground. The purely designative reading does not catch this. The conceptual coverage reading does: the annotator must determine whether what the citing court identifies as a fundamento determinante IS one — whether the specific proposition the citing court nominates was actually load-bearing for the cited precedent's holding.

*C1/C4 non-redundancy preserved on the conceptual coverage reading.* The acknowledgment-checking account's central structural move — C4's independent function shows C1 cannot require correctness-assessment — is accepted. The conceptual coverage reading does not make C1 and C4 redundant. C1 (conceptual coverage) checks whether the identification was of something that IS a fundamento determinante of the cited precedent — a question about the cited precedent's structure. C4 checks whether the correctly-identified fundamento determinante was correctly applied to the present case — a question about the citing court's analysis of its case in light of the ratio. These remain distinct: a court can fail C1 (nominate obiter as determinante) while performing correct C4 analysis on the misidentified ground; a court can pass C1 (correctly identify the ratio) while misapplying it to the present case (fail C4). The C1/C4 distinction holds on both the designative and the conceptual-coverage reading.

*Annotation-task implication.* On the conceptual coverage reading, the step-2 annotation task requires more than designative ementa-reading. The annotator must determine whether the specific ground the citing court nominates was actually a fundamento determinante of the cited precedent — which grounds were load-bearing for the holding, as opposed to obiter. The ementa's abstract-principle characterization does not enumerate which specific doctrinal constructions of the abstract principle were determinative versus obiter in the cited precedent's particular procedural context. This determination requires engaging the cited precedent at the doctrinal-specific level — the same level the round 11 annotation-task challenge identified as the step-2 gap-crossing requirement. The conceptual coverage reading therefore preserves the annotation-task challenge: the step-2 task cannot be performed tractably at the ementa's characterization level when the question is whether a specific construction was determinative, not merely whether an abstract principle was named.

*Relationship to the falsification condition.* The supportive's falsification condition — arm-specific C1 IRR lower for acknowledgment-present-but-application-contested cases — is accepted as the correct discriminating test between the two readings of *identificar*. The conceptual coverage reading predicts exactly this IRR pattern: in cases where the citing court names principle P but nominates a specific construction as the fundamento determinante, and where the cited precedent's ementa does not specify which constructions of P were determinative versus obiter, annotators applying the conceptual coverage task will disagree on C1 precisely in those acknowledgment-present-but-application-contested cases — because the acknowledgment of P alone does not settle whether the specifically-nominated construction was determinative. The purely designative reading predicts agreement in those cases (P was named → C1 satisfied regardless of which construction was determinative). The IRR pattern the supportive named as its falsification condition is the pattern the conceptual coverage reading structurally predicts. The pre-calibration pilot data should report arm-specific C1 IRR separately for acknowledgment-present-but-application-contested calibration pairs to discriminate between the two readings empirically.

**Fifteenth adversarial response — round 16: V/VI textual economy inference accepted unconditionally; ementa-anchored account contested at the constitutive-authority level — the ementa is evidential, not constitutive, of the cited precedent's fundamentos determinantes; a fourth case demonstrates that the ementa-anchored designative reading licenses the paradigm Art. 489, §1º, V failure when the ementa contains an elevation error.**

The supportive round 15 responds to all three adversarial positions from round 15 with three moves: (1) the objective reference set that *seus* denotes is constituted by the cited precedent's ementa — the authoritative published statement of what the court found to be its fundamentos determinantes for precedential purposes; the designative check is accordingly text-to-text comparison at the ementa's characterization level: does the citing court's text invoke the grounds the ementa identifies? the possessive *seus* correctly identifies that an objective set exists; the ementa is that set; (2) the V/VI textual difference inverts the adversarial's structural analogy — *que justifiquem* in VI and its absence in V marks an intentional legislative distinction; if bare *identificar* in V already carried application-justification content, *que justifiquem* in VI would add nothing; non-redundancy requires V's *identificar* to be purely designative, and VI's *que justifiquem* to be the additional application-justification layer; (3) the obiter-nomination third case is caught by the ementa-anchored reading: a citing court that nominates as the fundamento a proposition the ementa does not characterize as the ratio has not invoked what the ementa identifies, and C1 fails. Three adversarial responses follow.

*V/VI textual economy inference: accepted unconditionally.* The non-redundancy premise is jointly accepted. The supportive's inversion of the adversarial's structural analogy is correct: if V's bare *identificar* already carried the application-justification content that VI's *que justifiquem* clause adds, VI's clause would be vacuous — a genuine redundancy. Non-redundancy requires that V and VI impose different requirements: V's *identificar* is purely designative (was a fundamento determinante named at all?), and VI's *que justifiquem* adds the application-justification layer (do the identified grounds actually justify this case's application?). This inference is accepted without qualification and resolves the designative/conceptual-coverage question for *identificar* in V's favor. The adversarial's round 15 *que justifiquem* argument, offered as evidence that V's *identificar* carries non-designative content by structural analogy, is withdrawn: the supportive's reading of the textual difference is the correct one. V's *identificar* is purely designative.

*Ementa constitutive authority: the ementa is evidential, not constitutive, of the cited precedent's fundamentos determinantes.* Accepting V's purely designative reading shifts the surviving question to what *seus* refers to. The ementa-anchored account requires more than the annotation-source benefit established in round 10. Round 10 accepted that reading the cited precedent's ementa is simpler than synthesizing across votos — a source-reduction move. The ementa-anchored account now requires that the ementa not only simplifies the annotation source but constitutively determines what the cited precedent's fundamentos determinantes are for art. 489, §1º, V compliance purposes: *seus fundamentos determinantes* refers to the ementa-characterized fundamentos determinantes, such that what the ementa calls the ratio IS the ratio for C1 assessment, regardless of what the underlying deliberation's actual load-bearing grounds were.

This constitutive claim exceeds what the statute's text or the ementa's institutional function establishes. Art. 489, §1º, V's "sem identificar *seus* fundamentos determinantes" refers grammatically to the cited precedent's fundamentos determinantes — the grounds that were actually load-bearing for its holding. The possessive *seus* refers back to the cited precedent as an act of deliberation, not to the ementa as its published summary. The ementa is produced by the court's secretariat, not authored by the justices in their capacity as deliberating court; it is a summary for citation reference, not a definitive characterization binding for compliance-assessment purposes. Art. 927 — which establishes the binding precedential effect that art. 489, §1º, V enforces — binds courts to the decisions listed in its items, which are the underlying acts of deliberation, not to their ementas.

The distinction between evidential and constitutive is practically significant. An evidential ementa is a presumptively accurate characterization of the cited precedent's ratio, rebuttable in principle by careful reading of the underlying deliberation. Under this reading, the ementa-anchored designative check functions as a practical approximation — generally reliable, covering most cases correctly, but not immune to ementa inaccuracy. A constitutive ementa IS the cited precedent's fundamentos determinantes for compliance purposes, such that no gap can exist between ementa-characterized and actually-load-bearing grounds: the ementa determines the latter for §1º, V compliance by institutional design.

The adversarial does not contest the practical utility of anchoring the designative check to the ementa. What is contested is whether the ementa's characterization is immune to the objection that it may mischaracterize what the cited precedent's deliberation actually found to be determinative — an objection that the constitutive account forecloses by design rather than by establishing its accuracy.

*Fourth case: ementa elevation error defeats the ementa-anchored account's claim to handle all paradigm Art. 489, §1º, V failures.* The supportive's round 15 filing establishes that the ementa-anchored designative check catches the third case: a citing court that nominates a proposition the ementa does not characterize as a fundamento determinante has not invoked what the ementa identifies, and C1 fails. This is accepted: the third case is caught, on the ementa-anchored account, precisely because the ementa serves as the reference for what counts as a fundamento determinante.

The fourth case is the complement of the third, and it is not caught by the ementa-anchored account. The ementa mischaracterizes an obiter proposition P' as a fundamento determinante — an elevation error. The citing court invokes P', following the ementa's characterization. Under the ementa-anchored designative check: P' is what the ementa characterizes as a fundamento determinante; the citing court has invoked what the ementa identifies; C1 is satisfied. But P' was actually obiter in the underlying deliberation — the cited precedent's actual load-bearing grounds were different, and the secretariat's ementa erroneously attributed determinative status to an incidental observation. The citing court has not identified the cited precedent's actual fundamentos determinantes; it has invoked the wrong ground because the ementa got it wrong. Art. 489, §1º, V targets exactly this failure: a court that invokes a precedent without identifying the grounds that actually determined its holding. The ementa-anchored designative reading licenses C1 satisfaction in this case.

The fourth case is not exotic or pathological in the corpus ESHTR targets. Elevation errors — the ementa mischaracterizing an obiter observation as a fundamento determinante — are structurally concentrated in the contested-constitutional high-adversarial-record class that ESHTR's Phase 3 is designed to rank. Two structural drivers produce this concentration.

First, secretariat synthesis under fragmented collegial deliberation. In STF plenary decisions on contested constitutional questions, the deliberation produces multiple justices' individual votes (*votos*), each characterizing the ratio differently, emphasizing different grounds, and sometimes reaching the same dispositif through independent rationes. The secretariat synthesizes these fragmented characterizations into a single ementa statement of fundamentos determinantes. Synthesis across competing characterizations under institutional time pressure generates elevation errors: a ground mentioned prominently in a concurring justice's voto but not relied upon as the load-bearing foundation in the majority's analytical path can be listed in the ementa alongside genuinely determinative grounds. The more contested and fragmented the plenary deliberation, the more synthesis choices the secretariat must make — and the more elevation errors become structurally predictable.

Second, breadth incentive in the ementa's cross-court citation function. The ementa serves as a citation reference that citing courts across the judicial hierarchy consult to identify which grounds of the cited precedent are fundamentos determinantes for their specific cases. An ementa that comprehensively lists multiple candidate grounds (including borderline and obiter ones) provides more applicability surface for a broader range of future citing cases; an ementa that precisely identifies only the minimally load-bearing grounds limits the precedent's downstream usability. This creates an institutional incentive toward over-inclusion — characterizing borderline and near-ratio grounds as fundamentos determinantes — that is absent from the deliberation itself and independent of annotation quality. Breadth incentives structurally favor elevation of obiter or borderline grounds in the ementa regardless of whether the deliberating justices' votes support that characterization.

Both structural drivers are concentrated in the contested-constitutional plenary decisions Phase 3 is designed to rank. For ESHTR's annotation task, this means the ementa-anchored designative check encounters its fourth case most frequently precisely where annotation reliability matters most: in the high-adversarial-record arm whose champion decisions constitute Phase 3's comparator population.

*Relationship to the IRR falsification condition.* The IRR falsification condition — arm-specific C1 IRR lower for acknowledgment-present-but-application-contested cases — is accepted as the correct discriminating test for which reading of *identificar* annotators operationalize. If annotators anchor uniformly to the ementa's characterization, the ementa-anchored designative reading predicts high IRR in acknowledgment-present cases: invoking the ementa-named principle satisfies C1 regardless of construction contestation, producing cross-annotator agreement. The conceptual-coverage reading predicts lower IRR in the same cases: annotators must determine whether the invoked construction was actually determinative, generating disagreement where that determination is contested. The IRR pilot data discriminates which reading annotators operationalize.

What the IRR test does not discriminate is whether the ementa-anchored reference set is accurate about which grounds were actually load-bearing. If annotators achieve high IRR by uniformly anchoring to the ementa, this confirms that the annotation task is tractable and produces cross-annotator agreement under the ementa-anchored designative reading — not that the ementa-anchored reading catches all paradigm §1º, V failures. When the ementa contains an elevation error (fourth case), annotators achieving uniform agreement on the ementa's characterization produce high IRR while generating a systematic annotation error: they uniformly assign C1 satisfaction to a citing court that has not identified the cited precedent's actual fundamentos determinantes. High IRR and systematic annotation error are compatible outcomes; the IRR falsification condition tests the former, not the latter. The pilot arm-specific C1 IRR data is the correct empirical discriminant between the two readings of *identificar*; it is a separate and open empirical question whether the ementa-anchored reference set is accurate about which grounds were actually determinative in the cases where annotators anchor to it.

The adversarial's round 16 position is therefore: accept the V/VI textual economy inference unconditionally and without reservation — V's *identificar* is purely designative, the designative/conceptual-coverage question is resolved; accept the ementa as the practical annotation-source and reference document for the designative check; contest that the ementa constitutively defines *seus fundamentos determinantes* for art. 489, §1º, V compliance purposes in the sense of being immune to the objection that it may mischaracterize what the cited precedent's deliberation actually found to be load-bearing. The fourth case (ementa elevation error) demonstrates that the ementa-anchored designative reading — on its constitutive interpretation — licenses the paradigm §1º, V failure in a class structurally concentrated in the high-adversarial-record arm. Whether the ementa is to be treated as constitutive or evidential for art. 489 compliance assessment is a question about the statute's intent that the ementa-anchored account presupposes but has not established from the enacted text or from authoritative institutional characterization of the ementa's compliance-assessment function.

**Sixteenth adversarial response — round 17: compliance-assessment framing accepted as useful reframing that does not resolve the constitutive/evidential question; institutional-allocation argument contested as circular under the constitutive account it claims to support; restricted evidential trigger proposed for the compliance-determinacy concern.**

The supportive round 16 advances three structural arguments for the ementa's constitutive authority: (1) art. 489, §1º, V is a compliance-assessment standard, not an accuracy standard, and the ementa is constitutive by institutional design at the citation compliance level; (2) three institutional considerations — systemic structure (fragmented constitutional deliberation makes the evidential reading intractable for high-volume courts), compliance determinacy (the evidential reading produces an indeterminate standard because no trigger specifies when to look behind the ementa), and institutional allocation (the accuracy obligation runs to the cited court's self-documentation, not to citing courts' compliance standard); (3) structural drivers for elevation errors are plausible mechanisms whose frequency and concentration are unestablished, to be determined by the pilot. Three responses follow.

*Compliance-assessment framing: accepted as useful reframing that does not resolve the constitutive/evidential question.* The distinction between a compliance-assessment standard and an accuracy standard is accepted. Art. 489, §1º, V disciplines what the citing court must do; it does not audit whether the cited court's ementa accurately reflects its own deliberation. This is correct. But the compliance-assessment character of art. 489, §1º, V does not determine what the compliance-assessment standard's operative reference is. A compliance-assessment standard can assess compliance against either: (a) what the ementa characterizes as ratio (constitutive), or (b) the actual load-bearing grounds, using the ementa as presumptive evidence of those grounds (evidential). Both options remain available once the compliance-assessment character of the provision is accepted. The supportive's round 16 framing clarifies what kind of obligation art. 489, §1º, V imposes — a citing court conduct standard — but does not answer what the standard's operative reference consists in. The compliance-assessment/accuracy-standard distinction reframes the question without resolving it.

*The institutional-allocation argument's circular structure.* The supportive argues: "The accuracy obligation runs to the cited court's self-documentation, not to every citing court's compliance standard." This argument requires a structural distinction between: (a) the cited court's obligation — to accurately characterize in its ementa what was actually load-bearing — and (b) the citing court's obligation — to satisfy art. 489, §1º, V by engaging the relevant fundamentos determinantes. The adversarial accepts that art. 489, §1º, V disciplines obligation (b). What the adversarial contests is the structural presupposition of the institutional-allocation argument.

Under the constitutive account, distinction (a)/(b) does not exist at the compliance level. There is no "cited court's self-documentation accuracy obligation" that is separable from the ementa's constitutive function: if the ementa characterizes Y as ratio, Y is ratio for §1º, V purposes by institutional design. The cited court's ementa cannot "get wrong" what was ratio under the constitutive account, because what the ementa says IS the ratio for compliance purposes — definitionally. A self-documentation accuracy obligation for the cited court presupposes that there is a fact of the matter about what was actually determinative that the ementa might mischaracterize — which is precisely the evidential account's characterization of the system. Under the constitutive account, no such presupposition exists: the ementa constitutes the fact of the matter.

The institutional-allocation argument therefore invokes a distinction — cited court self-documentation obligation versus citing court compliance obligation — that only exists under the evidential account's institutional-responsibility structure. Under the evidential account, the cited court has an obligation to accurately characterize its holdings in the ementa (self-documentation), and the citing court has an obligation to engage the actual fundamentos determinantes, with the ementa as rebuttable evidence. Under the constitutive account, only obligation (b) exists, because what the ementa says defines what "the fundamentos determinantes" are — no accuracy check is available or needed. Using the evidential account's structural distinction to argue that the citing court's compliance obligation is accuracy-independent — and therefore that the constitutive account is correct — is circular: it imports the evidential account's institutional-responsibility structure as a premise for the constitutive conclusion.

*Compliance-determinacy: a restricted evidential trigger addresses the indeterminacy concern without general behind-the-ementa reading.* The supportive argues the evidential reading creates an indeterminate compliance standard because no trigger specifies when citing courts must look behind the ementa. A general read-behind-the-ementa requirement is indeed indeterminate; this concern is conceded. But the evidential reading does not require a general behind-the-ementa obligation. A restricted evidential trigger is determinable and publicly available: the existence of a subsequent authoritative determination — a superior court decision, a formal STJ/STF *tese vinculante*, or an *entendimento cancelado* resolution — that expressly revises, negates, or substitutes the cited precedent's ementa characterization of its fundamentos determinantes. When such an authoritative revision exists, it is published in official law reporters and accessible through the same case-law databases citing courts consult for precedent identification. The restricted trigger is: (a) determinate — either a revision exists in the public record or it does not; (b) observable without reconstructing the original fragmented deliberation — the citing court checks the case-law record for authoritative revisions, not the plenary votos; (c) narrow — covering only ementas whose characterization has been authoritatively contested and revised.

The systemic-structure concern does not apply to the restricted trigger class. High-volume citing courts are not asked to reconstruct plenary deliberation from fragmented votes; they are asked to check whether an authoritative subsequent characterization exists — the same lookup that identifies whether a precedent has been overruled, distinguished, or refined in subsequent superior court decisions. This is a standard element of Brazilian precedential practice, not an additional burden specific to the evidential reading.

Under the restricted evidential reading, the fourth case generates a C1 failure only when the ementa's elevation has been authoritatively revised — a narrower class than all elevation errors, but tractably identifiable. The compliance-determinacy concern does not defeat the evidential reading categorically; it defeats only readings that impose a general obligation to look behind ementas whose characterizations have not been authoritatively challenged.

Whether art. 489, §1º, V adopts the constitutive or the restricted evidential reading is a question about the statute's intent and institutional purpose that neither side has established from primary Brazilian procedural authority. The adversarial maintains that the restricted evidential reading is available, is textually grounded in *seus fundamentos determinantes* (the cited precedent's actual load-bearing grounds), and addresses the compliance-determinacy concern without the systemic-structure burden of reconstructing fragmented deliberations.

**Seventeenth adversarial response — round 18: statutory grounding required for the cited court's ementa-accuracy obligation; restricted trigger absorption denies the correction-triggering mechanism.**

The supportive round 17 advances two principal responses: (1) the institutional-allocation (a)/(b) distinction is non-circular under the constitutive account because "constitutive for §1º, V compliance purposes" is not equivalent to "incapable of mischaracterizing the underlying deliberation" — the constitutive account itself acknowledges the gap, as evidenced by the elevation-error fourth case being a "defect in the cited court's self-documentation" rather than a citing court compliance failure; and (2) the restricted evidential trigger is absorbed into the constitutive account because authoritative revisions (tese vinculante, entendimento cancelado, superior court ratio-revision holdings) function as new constitutive references superseding the original ementa's characterization, with checking which constitutive reference controls as a standard citation-verification step rather than evidential inquiry into the original ementa's deliberation-level accuracy. Two responses follow.

*The non-circularity response requires independent statutory grounding for the cited court's ementa-accuracy obligation.* The supportive r17's core claim is that the constitutive account "maintains a genuine gap between ementa accuracy and compliance reference" because the cited court has a "separate institutional obligation" for ementa accuracy ((a)) that is distinct from the citing court's §1º, V compliance obligation ((b)). The elevation-error fourth case is a defect in (a) — not a citing court compliance failure — precisely because this separate obligation exists. This is the proposed path out of the circularity charge: (a) is available under the constitutive account, so (a)/(b) does not presuppose the evidential account.

But the non-circularity response generates a structural requirement: obligation (a) must have statutory grounding independent of §1º, V and independent of the evidential reading. Without this grounding, the accuracy standard that constitutes the elevation error as a "defect" must come from somewhere — and the only available source is §1º, V on the evidential reading, which presupposes exactly what the constitutive account claims to deny. The supportive's claim that the constitutive account "maintains a genuine gap" and admits a "defect" in self-documentation is not a structural derivation from within the constitutive account; it is a borrowing of the evidential account's accuracy criterion to characterize what the constitutive account cannot itself characterize as defective.

The CPC's provisions governing the cited court's ementa authorship do not supply the required independent grounding. Art. 926 (*caput*) requires courts to maintain jurisprudence that is "stable, integral, and coherent" — a coherence obligation over time, not an accuracy obligation for individual ementa characterizations relative to the underlying deliberation. Art. 926, §2º requires súmulas to "adhere to the factual circumstances of the precedents that motivated their creation" — a provision targeted at súmulas, not ordinary case ementas. Art. 927, §4 requires "adequate and specific justification" for modifying a precedent tese, considering the principles of legal certainty, legitimate expectations, and equality — a justification standard for prospective modification, not a retroactive accuracy standard for original ementa characterizations. Art. 93, IX CF imposes a fundamentação requirement on decisions — applicable to the deliberating body's decision, not to the secretariat's ementa as a post-deliberation summary characterization.

The elevation-error fourth case makes the structural problem concrete. The supportive r17 concedes the elevation error is a "defect in the cited court's self-documentation." But under the constitutive account consistently applied, an elevation error cannot be called a defect: if what the ementa says IS the ratio for §1º, V compliance purposes by institutional design, then a secretariat that characterizes an obiter proposition as a fundamento determinante has exercised the constitutive authority the ementa possesses — it has defined what counts as ratio for compliance purposes. The ementa cannot fail to accurately characterize the ratio under the constitutive account, because the ementa's characterization defines what the ratio IS. Calling the elevation error a "defect in self-documentation" presupposes that there is a fact of the matter about what was actually load-bearing that the ementa mischaracterized — which is precisely the evidential account's characterization of what the ementa does. The concession that the elevation error is a defect is the constitutive account's own import of the evidential account's accuracy standard as the content of obligation (a). This confirms rather than defeats the circularity charge.

The supportive's path to non-circularity requires identifying the specific CPC provision — or combination of provisions — that independently establishes the cited court's obligation to accurately characterize its actual fundamentos determinantes in its ementa. If such a provision exists and establishes accuracy as the governing standard for ementa authorship independently of §1º, V, the (a)/(b) distinction survives without circularity. If no such provision exists, the accuracy standard must be derived from §1º, V on the evidential reading, confirming the round 17 circularity charge.

*The restricted trigger absorption denies its own triggering mechanism for correction revisions.* The supportive r17 absorbs the restricted evidential trigger by framing all authoritative revisions as new constitutive references superseding the original ementa's characterization. On this framing, checking which constitutive reference currently controls is a standard citation-verification step — equivalent to checking whether a precedent has been overruled — not inquiry into whether the original ementa was evidentially accurate.

Brazilian revision proceedings divide into two structurally distinct classes, however, and the constitutive absorption is stable for one class but not the other.

*Changed circumstances.* Revision because normative or factual circumstances have evolved since the original determination — new legislation, constitutional amendment, or changed social facts that alter the applicable legal standard. Art. 927, §4 expressly addresses this class: modification is warranted when the underlying circumstances that grounded the original tese have changed. In this class, the original ementa was accurate when issued; the revision produces a new constitutive reference because circumstances warrant a new determination, not because the original characterization was wrong. The constitutive absorption is stable here: no inaccuracy of the original is implied.

*Correction revisions.* Revision because the original ementa or tese incorrectly characterized what the court actually found to be the load-bearing grounds — the secretariat-synthesized characterization diverged from what the deliberating justices actually reasoned as determinative. This class is not merely theoretical: Brazilian superior courts have issued entendimento cancelado resolutions and tese revision requests specifically on the ground that the original formulation mischaracterized the ratio. In this class, the triggering mechanism is that the original characterization was evidentially inaccurate.

The constitutive absorption applied to correction revisions suppresses the triggering condition. If the original ementa constitutively defined the ratio by institutional design, then: (i) no ementa characterization can be "wrong" for compliance purposes — any secretariat characterization, however divergent from the underlying deliberation, defines the ratio for compliance; (ii) correction revisions cannot be distinguished from change revisions by their triggering mechanism — both are new constitutive references, and the triggering condition of correction revisions (that the original was inaccurate) has no status under the constitutive account; (iii) the revision record's engagement with the accuracy-of-original-characterization question — explaining why the original was wrong — becomes unintelligible: there is nothing to explain about why the original was wrong if the original's characterization constitutively defined the ratio.

Brazilian revision practice resists this absorption. Correction revision proceedings, as distinguished from change revision proceedings, engage the accuracy-of-original-characterization question — they explain why the original characterization was wrong, not merely that a new determination supersedes it. This is evidence that Brazilian practice presupposes the evidential account's accuracy standard for the correction class, even when the formal effect of both classes of revision is a new constitutive reference.

The constitutive account can absorb the formal effect of all authoritative revisions (new reference governs). It cannot absorb the material reason that distinguishes correction revisions from change revisions without suppressing the evidential character of the correction-triggering mechanism. Whether this suppression is available under Brazilian procedural doctrine — whether Brazilian law recognizes only supersession without the accuracy presupposition for correction revisions — is the question round 18 poses for the restricted trigger's constitutive absorption.

**Eighteenth adversarial response — round 19: art. 93, IX CF's fundamentação requirement mandates presence and expression of reasoning, not accuracy of ementa characterization; obligation (a) lacks statutory grounding at the characterization level.**

The supportive round 18 contests the premise of the round 18 adversarial's art. 93, IX CF dismissal. Under CPC art. 943, the acórdão is lavrado pelo relator and the ementa is a formal component authored by the deliberating court through its relator; the secretariat's role is publication and indexing, not authorship. Accepted: the ementa is relator-authored and forms part of the acórdão. Art. 93, IX CF's fundamentação requirement accordingly applies to the acórdão in its entirety, including the ementa. The round 18 adversarial dismissal of art. 93, IX CF on secretariat-summary grounds is withdrawn.

What survives is a scope question about what art. 93, IX CF requires of the relator-authored ementa. Accepting art. 943 and art. 93, IX CF's application to the acórdão-including-ementa does not settle whether the fundamentação obligation requires: (i) *presence and expression* of reasoning in the decision — the grounds are stated and the decision is not arbitrary; or (ii) *accuracy of characterization* — the ementa correctly identifies which element of the expressed reasoning was the ratio. The statutory grounding argument does not fail because art. 93, IX CF is inapplicable to the ementa; it fails — if it fails — because the fundamentação requirement operates at level (i), not level (ii).

Art. 93, IX CF requires that "todas as decisões [sejam] fundamentadas, sob pena de nulidade." A decision satisfies this requirement when it states its reasoning — when it is not arbitrary, when the judge explains the grounds for the holding. The fundamentação resides in the votos: the expressed reasoning that justifies the dispositif. A decision whose votos express the court's reasoning fully, and whose dispositif follows from that reasoning, is "fundamentada" under art. 93, IX CF even if the ementa's compact heading characterizes the expressed reasoning imperfectly. The votos supply the fundamentação; the ementa supplies a condensed abstract of it for citation and indexing purposes. If the abstract is inaccurate — if the ementa says "P' was our ratio" when the votos establish P as the actual load-bearing ground — the votos' fundamentação is intact. The decision has not become "sem fundamentação." An elevation error is a headnote accuracy problem, not a fundamentação deficit.

For the elevation error to constitute a fundamentação defect under art. 93, IX CF, the provision would need to require not only that reasoning be present and expressed, but also that the ementa's characterization accurately identify which portion of the expressed reasoning was load-bearing. No such accuracy requirement appears in the provision's text. The sanction clause confirms the scope: nullity attaches to decisions "sem fundamentação" — decisions that give no reasoning. A decision with a defective ementa heading but full reasoning in its votos is not "sem fundamentação." If headnote accuracy were within the fundamentação obligation, elevation errors would trigger nullity of the acórdão — a consequence Brazilian procedural doctrine has not derived from the provision and whose breadth would be inconsistent with the provision's established function as a check against arbitrary, unreasoned decision-making rather than a check against inaccurate self-description.

The structural consequence for the (a)/(b) distinction is direct. If art. 93, IX CF's fundamentação requirement operates at the reasoning-presence level (i), the cited court's obligation under art. 93, IX CF is to ensure the votos express the court's reasoning — an obligation satisfied by the votos regardless of how the ementa characterizes them. The ementa's characterization of which element of that reasoning was the ratio lies outside this scope. Obligation (a) — the cited court's obligation to accurately characterize its actual fundamentos determinantes in the ementa — does not find statutory grounding in art. 93, IX CF even under the accepted relator-authorship framing. The statutory-grounding requirement from round 18 is reformulated, not withdrawn: the adversarial requires the supportive to identify a provision that grounds an accuracy obligation specifically at the *ementa-characterization* level — distinct from the reasoning-presence obligation art. 93, IX CF supplies.

*The correction-revision class under the revised art. 93, IX CF scope.* The supportive round 18 assigned the correction-revision triggering condition to obligation (a): the cited court exercises obligation (a) by recognizing that the ementa mischaracterizes the ratio and issuing a correction revision; for §1º, V purposes, both correction and change revisions produce new constitutive references, and the compliance framework under obligation (b) is indifferent to the triggering mechanism.

Under the fundamentação scope narrowing, the assignment to obligation (a) is unavailable. Art. 93, IX CF requires reasoning to be present and expressed in the votos — an obligation satisfied by the votos even when the ementa mislabels the reasoning the votos correctly express. A correction revision triggered by ementa mischaracterization is not explained by the cited court's art. 93, IX CF obligation at the reasoning-presence level: that obligation is satisfied despite the elevation error, because the votos express the court's reasoning correctly. No art. 93, IX CF basis prompts the correction revision in the elevation-error case; the correction revision's triggering condition operates at the characterization-accuracy level that art. 93, IX CF does not reach.

The correction revision's triggering condition — accuracy recognition that the original characterization mischaracterized the ratio — remains a presupposition of the evidential account that the constitutive account cannot account for within the revised statutory framework. The round 18 adversarial argument is preserved: the (a)/(b) reassignment is unavailable when obligation (a) has no art. 93, IX CF basis at the ementa-characterization level. Whether Brazilian procedural doctrine provides an alternative statutory basis for a characterization-accuracy obligation — or whether the correction-revision triggering mechanism is a practice-level presupposition without statutory grounding — is the open question round 19 poses.

**Nineteenth adversarial response — round 20: functional differentiation within the acórdão explains asymmetric art. 93, IX CF scope; the relatório counterexample shows formal component status does not determine fundamentação scope.**

The supportive round 19 response makes three structural moves against the scope-narrowing argument: (1) the adversarial's "heading/body" vocabulary is in tension with the art. 943 acceptance — if the ementa is a formal acórdão component, not a heading external to the decision, the inconsistency between ementa and votos is an internal inconsistency between formal components, not a heading-to-body inaccuracy; (2) art. 93, IX CF's "decisões" covers the acórdão as a whole, so the scope limitation requires a positive argument for asymmetric application to formal acórdão components that round 19 does not supply; (3) art. 93, IX CF's accountability function extends to the ementa as the official published ratio statement under arts. 926-927, because accountability for precedent-producing courts operates through the ementa for citation compliance.

Round 20 concedes the vocabulary point and supplies the missing positive argument.

*On the vocabulary concession.* The "heading/body" framing is withdrawn. Using "heading" implies the ementa is external to the acórdão — which art. 943 forecloses. The correct description: the ementa is a relator-authored formal acórdão component whose function is citation summarization. Withdrawing this vocabulary terminates the vocabulary objection; it does not affect the scope argument. The scope question is not whether the ementa is inside or outside the acórdão; it is whether "fundamentadas" requires every relator-authored formal acórdão component to satisfy the same constitutional obligation, or whether the scope of "fundamentadas" is tracked by which component serves the reasoning-expression function.

*The positive argument: functional differentiation within the acórdão.* Art. 943 identifies three main relator-authored formal acórdão components: the relatório, the votos, and the ementa. These serve distinct constitutional functions. The votos serve the reasoning-expression function: they state the court's grounds for the dispositif, making the decision non-arbitrary and reviewable. The relatório serves the factual-summary function: it records the proceedings and parties' claims. The ementa serves the citation-indexing function: it summarizes the ratio for precedential reference under arts. 926-927.

The relatório counterexample establishes the scope principle conclusively. Brazilian doctrine does not hold that art. 93, IX CF requires the relatório to be "fundamentada" in the constitutional sense applicable to the votos. The relatório is a relator-authored formal acórdão component under art. 943; if the supportive's argument were correct — that all relator-authored formal acórdão components are covered by "fundamentadas" in the same constitutional sense — it would follow that the relatório must satisfy the fundamentação requirement. That implication is not maintained in Brazilian doctrine. Scope is therefore tracked by the reasoning-expression function, not by formal component membership. The ementa and the relatório are both relator-authored formal acórdão components under art. 943 that are not bearers of the reasoning-expression function. The asymmetric application the supportive identifies as missing a positive argument is supplied by functional differentiation implicit in the settled treatment of the relatório.

*On the accountability argument.* The supportive invokes art. 93, IX CF's accountability function: courts must give reviewable reasons; accountability for precedent-producing courts operates through the ementa under arts. 926-927; therefore the fundamentação requirement extends to ementa-characterization accuracy. This conflates two distinct accountability mechanisms governed by distinct statutory schemes. Art. 93, IX CF's accountability function is reasoning-presence reviewability — parties, appellate courts, and public scrutiny can assess whether the court expressed reasoning for the dispositif or issued an arbitrary decision. This function is served by the votos. The ementa's function in the arts. 926-927 accountability structure — systemic coherence of precedent citation — is a different objective governed by different provisions. The constitutive account itself presupposes this separation: obligation (a) is the cited court's self-documentation obligation, governed independently of §1º, V's compliance requirement on citing courts, while obligation (b) is the citing court's compliance obligation. Grounding obligation (a) in art. 93, IX CF collapses the (a)/(b) structural separation the constitutive account requires: both obligations would then be governed by the same provision, and the two-obligation structure is eliminated. The accountability argument does not establish that art. 93, IX CF — rather than arts. 926-927 — is the provision governing ementa-characterization accuracy; it establishes that some accuracy obligation exists from some source, which the adversarial does not deny. Which statutory provision governs the obligation is the open question.

**Courts operating at high volume compound this pattern.** Brazilian appellate
courts at the tribunal level process large volumes of decisions in recurring
case types. High-volume processing creates institutional pressures to routinize
recurring elements of reasoning. C3 — the requirement to avoid generic
boilerplate — is precisely the dimension most susceptible to this pressure:
formulaic language satisfies the form of the criterion while failing its
substance, and the failure is efficient at high volume. A court that has
developed a reliable standing formula for a particular proportionality finding
may produce decisions that are carefully crafted on C1 (ratio identification)
and C4 (precedent application) — because these require case-specific analysis —
while remaining systematically formulaic on C3 for the standard proportionality
announcement. The positive-correlation argument holds at the level of
judge-level analytical disposition; it is undermined by the institutional
dynamics that produce systematic formulaic patterns on some dimensions
independently of the judge's care on others.

**Fine-grained doctrinal clustering concentrates, rather than reduces,
quality-dimension asymmetry.**

The supportive paper further argues that embedding proximity captures fine-grained
doctrinal micro-context — precedential references, procedural posture, rhetorical
conventions — that constrains the salient criterion repertoire for within-cluster
pairings beyond what the broad topical label determines.

Consider a fine-grained cluster of proportionality-of-sanction appeals in
administrative law: decisions that are embedding-proximate because they invoke
the same leading proportionality precedents, apply the same evidentiary
standards for misconduct, and share procedural posture. Within this narrow
doctrinal neighborhood, the decisions that are proximate in embedding space
are those that engage the same doctrinal problem — but from different angles
determined by the contested issue in each individual case. Some push the
proportionality framework in novel factual applications (high C4, variable C2
depending on whether the parties contested the framework's applicability). Some
engage primarily with the evidentiary inference from misconduct to sanction
quantum (high C2 on evidence arguments, adequate C4 on applying settled
proportionality doctrine). Some address primarily the completeness and internal
consistency of the proportionality holding (high C5, variable C1 for identifying
the ratio's precise formulation). Doctrinal specificity constrains the framework
and vocabulary the decisions invoke; it does not constrain which aspects of that
framework were contested in each specific case. A fine-grained cluster of
proportionality decisions selects for decisions that engage the same doctrinal
problem from different contested angles — exactly the configuration that produces
asymmetric quality-dimension profiles across cluster members.

### 3.3 Item-Level Criterion Activation Defeats the Aggregation Defense

The Bradley-Terry aggregation defense requires a crucial assumption: within-cluster
criterion-switching is non-systematic — not directionally correlated with item
identities. Only under this assumption does residual criterion-switching
contribute variance without systematic bias, and only then does Bradley-Terry
aggregation converge on an accurate quality signal despite individual pair
variation.

The supportive paper draws a structural contrast: cross-cluster switching is
directional (a criminal law item consistently activates domain-specific criteria
against tax law items, producing bias that accumulates across pairings);
within-cluster switching is non-directional (criterion activation varies across
pairings without item-level correlation, so Bradley-Terry averages it out).
This contrast is asserted as a structural property of within-cluster vs.
cross-cluster comparison. It is not derived from the mechanism, and it is
not obviously true.

The supportive paper's pair-specificity response is accepted on its own terms:
the most discriminating feature of a pairing is determined jointly by both items,
not by one item's absolute profile. Decision A's fact-finding excellence is the
most salient criterion in a pairing with B only when A's fact-finding advantage
over B exceeds B's counter-advantage over A on every other quality dimension. In
a pairing with opponent C who closely matches A on fact-finding but is distinctly
weaker on proportionality, the most discriminating feature shifts to proportionality.
The prior claim that distinctive strength activates a criterion in *every* pairing
was too strong; it is withdrawn.

The narrowed claim: criterion activation is systematic in **cross-strength
pairings** — pairings where one item is stronger on a quality dimension and its
opponent is not. When A is among the cluster's strongest on fact-finding and faces
an opponent who is weaker on that dimension, A's fact-finding advantage is by
definition the feature that most distinguishes the two items. The Tversky mechanism
then predicts fact-finding activates as the primary evaluative dimension for that
comparison. In a cluster where most items are not strong fact-finders, the majority
of A's pairings are of this cross-strength type, making fact-finding the
most-discriminating feature in the majority of A's pairings — not from persistent
activation regardless of pairing, but from the cluster composition generating
predominantly cross-strength pairings for an item that specializes in a scarce
dimension.

**The structural dependency on quality-dimension correlation.** The pair-specificity
response rescues the aggregation defense only under strong positive correlation
among quality dimensions. Under positive correlation, opponents who are weaker than A
on fact-finding are also weaker on proportionality — so their counter-advantage on
proportionality is small, and A's fact-finding advantage is the most discriminating
feature in most of A's pairings regardless. Bradley-Terry then aggregates A's overall
quality advantage across its pairings, converging on a valid quality signal.

Under weak or zero correlation — where opponents weaker on fact-finding may be
strong on proportionality — the counter-advantage on proportionality can exceed A's
fact-finding advantage in specific pairings, shifting criterion activation to
proportionality in those pairings. Whether fact-finding or proportionality is most
discriminating then varies by opponent, generating a criterion-activation distribution
across A's pairings that depends on the specific quality-dimension profiles of the
cluster members A faces. The aggregate Bradley-Terry score reflects this composition
of pairing types — not a stable quality standard.

The pair-specificity response thus succeeds under strong positive correlation and
fails under weak correlation. The §3.2 arguments establish structural reasons to
expect weak correlation in Brazilian appellate corpora: case-driven quality-dimension
variation (especially C2 constrained by adversarial record quality), high-volume
routinization of C3 independently of C1/C4, and fine-grained doctrinal clustering
concentrating within-cluster dimensional asymmetry. The aggregation defense and the
pair-specificity response share a single load-bearing premise with §3.2's attack:
whether Brazilian appellate corpora exhibit sufficiently strong quality-dimension
correlation. Under strong correlation, the defense wins both §3.2 and §3.3. Under
weak correlation, the defense loses both. These are not independent structural
arguments that can hold separately.

**The cluster-composition dynamic.** Systematic criterion-activation patterns arise
from the cluster's quality-dimension composition even in the moderate case, without
invoking extreme outlier items. In a cluster where some items are stronger on
fact-finding (and adequate on proportionality) and others are stronger on
proportionality (and adequate on fact-finding), pairings between two fact-finding-
strong items activate proportionality as the most discriminating dimension — they are
matched on fact-finding, so their largest gap lies on proportionality. Pairings between
two proportionality-strong items activate fact-finding for the same reason. Cross-group
pairings activate whichever dimension produces the larger gap between the specific items.

A fact-finding-strong item whose pairing schedule includes more proportionality-strong
opponents — because the cluster's composition favors proportionality specialists —
activates its fact-finding advantage more frequently and accumulates wins under the
fact-finding criterion more readily than a comparably-quality item in a cluster with
the reversed composition. In a round-robin tournament, the criterion-activation
frequencies across any item's pairings are determined by the cluster's composition —
a fixed structural property, not a stochastic process. Bradley-Terry aggregates this
composition effect into the final score. The score reflects how often the item's strong
dimension is the most discriminating feature in its pairings, which depends on the
cluster's quality-dimension population, not only on the item's own quality profile.

**The routinization concession and the mechanism's scope.** The supportive paper
explicitly acknowledges that C3-exceptional items — those deviating from the cluster's
formulaic pattern — exhibit systematic C3 criterion activation in their pairings with
formulaic opponents: "its C3 distinctiveness becomes the most discriminating feature in
pairings where its C3 advantage exceeds the opponent's counter-advantages on other
dimensions." This is described as "a localized effect on C3-exceptional items, not a
cluster-wide mechanism." Both characterizations are accurate: the effect is concentrated
in pairings involving the exceptional item; it does not operate uniformly across all
cluster pairings. What neither characterization establishes is that the systematic
character of the effect — predictable from the item's position and the pairing
composition — makes it negligible in the aggregate Bradley-Terry score for that item.

The supportive paper has no principled basis for limiting this concession to C3. The
mechanism applies to any dimension where one item is distinctively stronger than most
cluster members. C3 exceptionalism is one structural route to this configuration; the
case-driven C2 variation and fine-grained doctrinal clustering described in §3.2 are
others. The "localized" characterization describes the scope (concentrated in the
exceptional item's pairings), not the systematic quality of the criterion activation
within that scope. The aggregation defense requires that effects of this type are
either absent or sufficiently uncorrelated across the pairing distribution to average
out — a requirement that neither the "localized" characterization nor the quality-
dimension correlation argument establishes for the target corpus.

### 3.4 The Operationalization: Best Available Does Not Mean Sufficient

The supportive paper (`yesindeed/frame-stability-sph.md`, §3.5) acknowledges
that the ideal operationalization — clustering items by criterion-set homogeneity
within triples — would require knowing, before Phase 2, which quality dimensions
are most discriminating for which pairs. This information is generated by Phase 2
itself. Embedding clustering is therefore the best tractable pre-evaluation proxy.

This concession is accepted: there is no non-circular pre-evaluation
operationalization that fully aligns with what the mechanism requires. The
question shifts to whether the best available proxy is sufficient for the
design goal.

Prediction 4 (`yesindeed/frame-stability-sph.md`, §3.4) is offered as the
empirical test: within-cluster non-transitive cycles should be unstructured
relative to quality-dimension asymmetry profiles — uniformly distributed, not
concentrated at triples where items have maximally asymmetric profiles. This
is accepted as the correct test.

However, the Tversky mechanism that the supportive paper invokes should predict
the opposite pattern if within-cluster quality-dimension profiles are asymmetric.
By the mechanism, the most discriminating feature of each specific pair
determines criterion salience. If Decision A is structurally distinctive for
its thorough fact-finding and Decision C is structurally distinctive for its
procedural-safeguard analysis, the triple {A, B, C} — where B is adequate on
both — will produce criterion switches across its three pairings in a
predictable pattern: the A-vs-B pairing activates fact-finding (where A wins),
the B-vs-C pairing activates procedural safeguards (where C wins), and the
A-vs-C pairing activates whichever dimension is most discriminating between
A's fact-finding strength and C's procedural strength. The cycle involving A
and C concentrates at exactly the quality-dimension boundary between A's
distinctive strength and C's distinctive strength. This is the structured
pattern Prediction 4 denies.

Whether within-cluster quality-dimension profiles are sufficiently correlated
to suppress this structure, or sufficiently asymmetric to produce it, is the
central empirical question. The arguments in §§3.2–3.3 give reasons to expect
asymmetric profiles are not rare in appellate legal corpora: case-driven
quality-dimension variation, high-volume routinization effects, and the
concentration of quality-dimension asymmetry within fine-grained doctrinal
clusters all work against the positive-correlation assumption.

The mechanism, accepted in full, generates two competing predictions depending
on the empirical distribution of quality-dimension profiles in the corpus: if
profiles are correlated (the supportive prediction), cycling is non-systematic
and Prediction 4 holds; if profiles are asymmetric (the prediction following
from §§3.2–3.3), cycling is structured and Prediction 4 fails. The experiment
is the arbiter — but the current theoretical balance of arguments does not favor
the supportive prediction.

### 3.5 The Hypothesis Is Introduced Without the Evidence It Needs

Section 4 of ESHTR offers an "informal argument" and the mechanism paper
provides independent grounding. But neither establishes the critical empirical
claim: that the embedding clusters produced by multilingual-e5-large-instruct
(or fine-tuned variants) are sufficiently criterion-homogeneous within triples
to materially reduce non-transitivity in the specific experimental protocol
ESHTR describes.

The mechanism paper explicitly acknowledges that it provides plausibility,
not proof. The mechanism could be correct — criterion switching is the source
of non-transitivity — while the embedding-clustering operationalization fails
to control it adequately at the triple level, or while the Bradley-Terry
aggregation fails to handle the within-cluster cycling that remains. Whether
the proxy is good enough is an empirical question, and it requires tests beyond
the aggregate κ comparison specified in Section 5.5 of ESHTR. Specifically:
the ESHTR experiment would need to measure within-cluster cycle incidence
relative to quality-dimension asymmetry profiles — the test Prediction 4
identifies — not only compare aggregate within-cluster κ to cross-corpus κ.
Without this additional measurement, whether within-cluster cycling is
systematic or non-systematic cannot be determined from the experimental output
the current protocol design produces.

### 3.6 Phase 3's Tractability Is a Prediction, Not an Established Result

The defense has corrected a factual error in the prior version of this attack.
ESHTR §3.3 explicitly describes Phase 3 as "a cross-cluster championship
tournament": the hierarchical design was built to confine uncontrolled cross-cluster
comparison to a rejected baseline while enabling controlled cross-cluster comparison
in Phase 3. Phase 3 performs the cross-cluster comparison the design was built to
produce, not what it was built to prevent. The prior characterization — "precisely
the operation that ESHTR's hierarchical design was constructed to avoid" — was
inaccurate and is withdrawn.

The question that survives the correction is more specific and more empirically
demanding. Phase 3 performs the cross-cluster comparison that motivated the
hierarchical design. The accepted Tversky mechanism predicts that cross-cluster
C1-C5 comparison produces non-transitive cycles through criterion switching at the
feature-salience level. Phase 3's structural controls (champion-only population,
explicit abstraction instruction, small k) are intended to make this cross-cluster
comparison more tractable than the uncontrolled baseline. The defense now provides
a mechanism-level argument for why the instruction should help: under Tversky (1977)
feature-salience, an explicit instruction changes the comparison frame from implicit
(domain-content-dominated) to explicit (method-quality-directed), reducing salience
of domain-specific content features that drive cross-cluster cycling.

This mechanism-level argument is accepted as providing a theoretical prior. If the
instruction successfully modulates feature salience in the Tversky sense, Phase 3
should exhibit lower non-transitivity rates than uncontrolled cross-cluster comparison.
The argument is of the same logical type as the Semantic Proximity Hypothesis for
Phase 2: a mechanism-grounded conjecture that generates a falsifiable prediction. As
with Phase 2's SPH, the mechanism establishes the prior; the experiment determines
whether the prior is confirmed and whether the attenuation is sufficient.

What the mechanism argument does not establish is that the attenuation is sufficient.
Between "the instruction should help" and "Phase 3's non-transitivity is low enough
to support a coherent global ranking" lies the central empirical question. The Tversky
mechanism identifies feature salience as a function of which features most discriminate
the specific pair being compared — a property of the items. A criminal law champion
and a tax law champion are distinguished most saliently by their domain-specific content
features in the texts the LLM reads: legal frameworks, doctrinal vocabulary, and
reasoning conventions that differ maximally across domains. The instruction specifies
what to evaluate (reasoning method); it does not remove from the texts the features
that most discriminate the items. Whether residual domain-specific feature influence
leaves non-transitivity above or below the threshold needed for a reliable global
ranking is not resolved by the mechanism argument — it is the question the experiment
must answer.

The three structural controls — champions, instruction, small k — were present in
ESHTR's original design. The mechanism argument grounds why they should help; it does
not add new empirical content to the prediction. The prediction and the test required
to confirm it remain what surrender condition §6(3) specifies.

The concrete calibration protocol in `phase3-coherence-defense.md` §4.6 advances the
debate: it specifies three falsifiable measurements and an instruction-independence
test using non-champion cross-cluster pairs. Two structural limits constrain what the
protocol can establish.

**Circular quality ground truth.** The quality-discrimination accuracy measurement
constructs "quality-discrepant pairs" using within-cluster Phase 2 calibration
rankings — one decision ranks higher within its cluster. Phase 3 instructions are
tested for winner-accuracy: whether the Phase 3 judgment identifies the higher-ranked
decision. For this to validate Phase 3's quality-discrimination reliability,
within-cluster Phase 2 rankings must be valid quality ground truths. But
within-cluster rankings are produced by the Bradley-Terry aggregation that §§3.3-3.4
contest: if systematic criterion-switching produces item-level biases in Bradley-Terry
scores, quality-discrepant pairs may not be discrepant in quality — they are discrepant
in which criteria dominated their within-cluster pairings. Phase 3 agreeing with Phase 2's
quality ordering across domain boundaries confirms Phase 3's alignment with Phase 2's
criterion-activation pattern, not independent cross-domain quality-discrimination validity.
An independent quality ground truth — expert human judgments on cross-cluster
quality-discrepant pairs, not derived from Phase 2 rankings — is not specified in the
protocol. Without it, the quality-discrimination measurement is a closed loop between
Phase 2 and Phase 3 calibration.

**Champion-scale gap.** The protocol calibrates instruction effects on non-champion
cross-cluster decisions. Phase 3's actual comparators are domain champions — decisions
where method and domain content are most tightly integrated (§3.8). Non-champion
calibration evidence does not proxy for champion-scale instruction effects. §3.8
identifies champion decisions as the harder case, not an approximation: reasoning
method in champion decisions is expressed through, not separately from, domain-specific
doctrinal structure in a fully realized way. The instruction-independence test provides
evidence on the easier case and leaves the harder case untested.

**Variance-source confound in measurement 2.** Measurement 2 compares per-criterion
score variance across two cross-domain decisions under Phase 2 versus Phase 3
conditions. Its diagnostic logic: domain-specific criterion mapping drives larger
within-pair criterion-profile differences under Phase 2 (domain-appropriate criteria
favor the in-domain decision); structural-reading mode suppresses this and reduces
criterion-profile variance; circularity produces no reduction. The falsification
criterion is explicit: criterion-profile variance not reduced under Phase 3 conditions
would disconfirm structural-reading mode; variance reduced under Phase 3 would
disconfirm circularity.

The logic requires that within-pair criterion-profile variance under Phase 2 cross-
cluster conditions is primarily driven by domain-specific criterion mapping. But the
accepted adversarial mechanism predicts that criterion activation in any pairing is
determined jointly by both items' quality-dimension profiles — pair-specifically, not
by domain label alone. For a cross-cluster pair, within-pair criterion-profile
differences under Phase 2 arise from two sources: (i) domain-specific criterion
mapping that differentially weights domain-appropriate quality dimensions, and (ii)
pair-specific quality-dimension-profile differences between the two specific decisions,
which activate different dominant criteria even within a single domain. Both sources
produce within-pair criterion-score asymmetry; measurement 2 measures their sum.

Source (ii) is not eliminated by the Phase 3 instruction. When structural-reading mode
suppresses source (i), source (ii) becomes relatively more prominent — quality-dimension-
profile differences between two high-quality champions from different structural
specializations remain, and in the absence of domain-specific mapping, they become the
dominant driver of within-pair criterion variation. The net effect on total within-pair
criterion-profile variance under Phase 3 depends on the relative magnitudes of sources
(i) and (ii) in the specific calibration pairs used. If source (ii) is comparable in
magnitude to source (i) — which the adversarial mechanism's own pair-specificity account
makes plausible for high-quality champion comparisons — Phase 3 instructions may reduce
total criterion-profile variance only moderately even when structural-reading mode is
fully functioning.

The interpretive gap concerns the intermediate outcome. Large variance reduction
confirms structural-reading mode; zero reduction is consistent with circularity.
Moderate reduction — which the adversarial mechanism predicts is the likely outcome
when source (ii) partially replaces the suppressed source (i) — is consistent with
both effective structural-reading mode and partial circularity. The stated falsification
criterion ("variance not reduced") provides confirmatory power when reduction is large
but fails to arbitrate the intermediate case that the accepted mechanism predicts.

Measurements 1 and 3 add independent evidence but do not resolve the variance-source
confound. An LLM panel that achieves improved cross-cluster κ (measurement 1) and
better quality-discrimination accuracy (measurement 3) under Phase 3 conditions could
be converging on quality-dimension-profile-driven criteria rather than structural-method
criteria — agreement for reasons consistent with the mechanism's source-(ii) prediction
that measurements 1 and 3 cannot distinguish from genuine structural-reading mode
without variance-source decomposition. The supportive paper notes that the combination
of all three measurements is "more diagnostic" than any single one; but the expected
pattern of results across the three measurements under each hypothesis — structural-
reading, circularity, and source-(ii) dominance — is not specified in the protocol.
Specifying those patterns in advance is what converts three measurements from a
descriptively richer observation into a discriminating test.

### 3.7 Method/Content Inseparability in LLM Implementation

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
the ones that logically necessitate the outcome?") that may miss domain-specific
elements that are, in fact, load-bearing for the ratio's correct identification.

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

The defense adds a third option (§4.6 of the defense, Option c): LLM judges
evaluate the **structure** of reasoning using domain-specific material as evidence,
without evaluating domain-specific content itself — assessing logical dependency
relationships and argument engagement coherence. The proposed analogy is comparative
law scholars who assess ratio structure and argument coherence across jurisdictions
without evaluating whether the specific doctrine is correct.

Option (c) describes a theoretically coherent evaluative mode. The question is
whether frontier LLMs under the Phase 3 abstraction instruction reliably realize it.

There is structural reason, grounded in the accepted mechanism, to doubt that they
do. The supportive mechanism paper (`yesindeed/frame-stability-sph.md`, §3.3)
explicitly grounds LLM reliability in domain-specific criterion acquisition: "LLM
judges trained on human-generated preference data learn the context-sensitivity that
characterizes human comparative judgment... criminal reasoning quality is judged on
criteria specific to that domain (evidentiary standards, sentencing proportionality,
constitutional rights compliance)." This domain-specific criterion mapping is what
makes within-cluster LLM judgments reliable: LLMs evaluate criminal law decisions
using criminal law criteria because their training encoded those criterion-domain
associations. The Phase 3 instruction asks LLMs to suppress precisely this activation
when reading domain-specific legal texts.

The mechanism that produces within-cluster reliability (domain-specific criterion
activation from domain-specific text) is the same activation the instruction attempts
to override. LLMs trained on domain-specific legal corpora carry in their weights the
associations between legal domains and quality criteria. When those LLMs read domain-
specific texts — criminal law champion decisions, tax law champion decisions — the
domain-specific features that differ most between compared items will tend to activate
their associated criterion mappings. The instruction to "abstract from subject-specific
vocabulary" changes the LLM's explicit evaluative label; it does not sever the
association between domain-specific textual features and the quality criteria those
features activate.

Option (c)'s theoretical availability does not establish that it is what frontier LLMs
achieve in practice under the Phase 3 instruction. The calibration protocol (ESHTR
§5.4) is designed for Phase 2 panel calibration and does not include a Phase 3-specific
test for whether LLM judges operate in the structural-reading mode rather than in a
domain-criterion-suppression mode where domain-specific feature activation persists
despite the instruction. Without such a test, Option (c) remains an implementation
aspiration rather than a demonstrated behavior.

### 3.8 The Champion Population Argument Does Not Stabilize Phase 3

The defense argues that Phase 3 comparators — cluster champions — are a more
homogeneous population than arbitrary cross-domain pairs, because all champions
share the property of domain-reasoning-quality excellence. This reduces the
frame-instability mechanism's operation.

Two problems.

First, whether a decision is a "cluster champion" depends on Phase 2's
tournament ranking, which Sections 3.1–3.4 argue may itself be driven by
within-cluster criterion-switching. A tournament that Bradley-Terry aggregates
over asymmetric quality-dimension profiles — where each item persistently
activates the criterion associated with its most distinctive structural feature —
does not reliably identify the highest-quality decision in each cluster. It
identifies the decision that accumulates the most wins under the distribution
of criteria the cluster's pairing structure activates. The champion population's
supposed homogeneity (all are domain-quality exemplars) cannot be guaranteed
by a process that may select for "wins most pairings under the criterion-activation
distribution" rather than "highest quality under any stable standard."

Second, even granting that champions genuinely represent domain-quality peaks,
the question "whose reasoning quality transfers most across domains?" requires
the LLM judge to bridge criterion sets across the compared champions' domains.
A criminal law champion and a tax law champion both demonstrate domain excellence.
Determining which champion's *method* is "more transferable" asks the judge to
compare the generalizability of two different high-quality reasoning styles —
precisely the kind of cross-domain bridging that the contingent frame-construction
mechanism identifies as the source of non-transitivity. The champion population's
shared excellence does not eliminate the criterion-switching problem; it
concentrates it among the most sophisticated and domain-integrated examples of
legal reasoning, where domain-general and domain-specific method are most
tightly intertwined and therefore hardest to separate.

---

## 4. Anticipated Reply and Why It Does Not Suffice

**On the Phase 2 within-cluster attack (§§3.1–3.4):**

The most direct reply available is the cluster-granularity argument: HDBSCAN's
parameter choices can produce fine-grained enough clusters that all decisions
within a cluster share similar quality-dimension profiles, making the
non-systematic assumption hold in practice. Under this argument, within a
sufficiently narrow doctrinal cluster, no individual decision has structural
features distinctively prominent enough to activate a specific criterion in
every pairing — all decisions are similarly positioned across quality dimensions.

This reply faces a dilemma of its own: clusters fine-grained enough to produce
quality-dimension homogeneity contain few enough items that the within-cluster
tournament is trivially simple (one or two pairings determine the ranking) and
the hierarchical design adds no value over direct comparison. The Phase 2
parameters described in ESHTR — clusters of approximately 10–20 decisions — are
large enough to require a multi-round tournament, which implies enough quality
variation across items to make the tournament informative. But enough quality
variation across items means some items are distinctively stronger on some
dimensions, which is precisely the structural condition for item-level persistent
criterion activation. The cluster size needed to make Phase 2 informative is
incompatible with the cluster homogeneity needed to make the non-systematic
assumption hold.

Even if granularity arguments could be made to work, the doctrinal
micro-context argument shows that fine-grained clusters may concentrate
quality-dimension asymmetry rather than suppress it (§3.2). Finer granularity
reduces the criterion repertoire that can be activated within a cluster; it
does not eliminate item-level persistent structural features that activate
specific criteria within whatever repertoire remains.

The pair-specificity reply — that persistent activation across all of A's
pairings requires A to be a clear outlier on one dimension relative to the entire
cluster, an extreme condition not the modal case — is a genuine correction accepted
in §3.3. The reply narrows but does not defeat the §3.3 attack. Two reasons.
First, the narrowed claim (systematic criterion activation in cross-strength
pairings) survives: A need not activate a criterion in every pairing; it suffices
that A's cross-strength pairings — which constitute the majority of A's schedule
in a cluster where A's focal dimension is scarce — systematically activate the
focal dimension, producing a criterion-activation distribution that is not stochastic.
Second, the reply is structurally dependent on the quality-dimension correlation
claim (§3.2): it succeeds under strong correlation (where opponents weaker on A's
focal dimension are also weaker on other dimensions, reducing the counter-advantage
that could displace the focal dimension as most discriminating) and fails under weak
correlation (where opponents' dimensional profiles vary independently). The pair-
specificity response and the aggregation defense share a single load-bearing premise
with §3.2's attack: the quality-dimension correlation claim. Whether the defense wins
the §3.2 correlation debate determines whether it wins §3.3 as well.

**On the full C2 exchange (eighteen supportive responses, eighteen adversarial counter-replies).**
The C2 debate has passed through nine exchanges. The supportive camp argues (1) that
C2 evaluates analytical conduct quality rather than engagement volume; (2) that
adversarial record quality affects C1, C2, and C4 as a correlated set; (3) that three
argument-type-independent textual markers — explicit identification of the argument,
citation to the applicable standard, logical failure statement — allow calibrated
judges to assess conduct quality regardless of argument strength, making the calibration
gap a protocol design insufficiency not a structural impossibility; (4) that dense
embedding models encode argumentative elaboration alongside doctrinal vocabulary in
the same representational space, so clustering by proximity compresses both, and
within-cluster C2 variance is not necessarily wider than C1/C4 variance; (5) that
coverage completeness at the argument-set level is the within-adequacy ranking signal,
observable from the case record without argument-strength knowledge, and requiring
SC6(a) Type 2 calibration pairings; (6) that the C2 adversarial disjunction resolves
structurally — prong 1 activates SC6(c) directly; prong 2 relocates to Phase 3 and
activates SC6(3); (7) that the input-protocol gap for coverage completeness is a
minor input-specification change under Brazilian processo eletrônico, SC6(b-2) provides
a concrete naturalistic test, and a cross-elaboration calibration pair methodology with
independent expert assessment addresses SC6(3) under prong 2; (8) that the
materiality-identification gap is addressed because SC6(b-1) anti-naturalistic pairs
already constitute the full pipeline test, the SC6(b-2) convergence is acknowledged,
and the question-begging in the cross-elaboration expert assessment is resolved by
three categorical/ordinal measures whose reference answers are established from the
decision text and brief independently of adversarial record richness; and (9) that the
SC6(b-1) pipeline structural limitation is accepted and supplemented by SC6(b-1)-ID
calibration pairs that test materiality identification from raw brief content under the
outcome-dependency standard — an argument is material if accepting its conclusion
would require a different dispositif, a determination requiring argument-conclusion-
to-dispositif mapping rather than doctrinal-strength assessment; the C1 post-decision
text-reading distinction is the session's key concession-with-response, accepting the
formal validity of pre-decision/post-decision separation while predicting comparable
arm-specific inter-rater reliability for C1 because annotators read the court's own
ratio characterization in the decision text rather than independently determining what
the ratio should have been; and the five-dimension composite is adopted, incorporating
C4 through decision-to-cited-precedent characterization comparison and C3 through
within-cluster formulaic-language frequency analysis; and (10) that the C1 annotation
task is bounded to ementa-reading with protocol-specified logical-operator resolution
rules for explicit conjunctive/alternative connectives, addressing collegial fragmentation
as a source-reduction benefit; that C3 mandatory-text conflation is addressed by
official-database preprocessing (Portal da Legislação, Diário Oficial, STF/STJ súmulas)
stripping legally-mandated verbatim text from reasoning sections before phrase frequency
computation; and that SC6(b-1)-ID tractability is bounded by the court's stated legal
theory from the decision text, reducing genuinely intractable cases to the intersection
of ambiguous-court-theory and multi-component-dispositif, with the quality-filter
narrowing this class in the calibration corpus.

The §3.2 analyses address all ten. On (1): the conduct/quality distinction holds at
the criterion level; it does not survive the calibration step, where LLM judges
trained on human preference data acquire a C2 signal correlated with elaboration
richness in the text, because annotators assessing conduct quality for legal arguments
cannot verify argument-specific analytical precision from decision text independently
of that text's own elaboration level. On (2): the C1/C4 co-variation argument
establishes between-case dynamics; within a fine-grained doctrinal cluster, C1/C4
variance is compressed by shared precedential context while C2 varies with
case-specific adversarial records, independent of the shared doctrinal framework.
On (3): the three structural features function as adequacy thresholds — distinguishing
conclusory from reasoned disposal — not as ranking signals within the adequacy range;
both minimally adequate and excellent C2 decisions exhibit the features; elaboration
depth across the features scales with argument strength even when all three are
formally present; the within-adequacy ranking problem is not closed by feature
presence. SC6(a) must be constructed as pairwise ranking examples, not only as
weak-argument context inclusions. On (4): the encoding claim is accepted; the
compression inference does not follow; clustering compresses the dimensions that drove
proximity — doctrinal vocabulary, precedential references, procedural posture —
while argumentative elaboration varies with case-specific adversarial records
independent of doctrinal context; whether elaboration is also compressed depends on
a corpus-specific correlation that is not structurally mandated. On (5): coverage
completeness is a valid ranking dimension under art. 489, §1º, IV; but tracking it
independently of text-volume proxies requires the case record as LLM judge input at
evaluation time — an input-protocol extension ESHTR's design does not currently
specify; additionally, Type 2 calibration on anti-naturalistic pairs (where the
complete-but-thin decision is shorter) must demonstrate generalization to naturalistic
pairs where coverage and text volume co-vary in the standard positive direction.
On (6): the disjunctive structure clarification is accepted; SC6(3) as currently
specified addresses the cross-domain criterion-switching concern; it does not address
the cross-elaboration concern prong 2 relocates to Phase 3, where champions may differ
in elaboration richness arising from cluster-level adversarial record heterogeneity
rather than domain-vocabulary differences — a distinction the abstraction instruction
does not explicitly target. On (7): the input extension introduces a materiality-
identification step that the minor-specification-change framing does not address —
identifying which brief arguments are material under art. 489, §1º, IV requires
C2-adjacent argument-strength assessment, and the elaboration-quality correlation that
infects C2 scoring in the decision text is present in the party brief in the same
structural form; SC6(b-2) is accepted as appropriately specified; the cross-elaboration
test's expert-assessment protocol is question-begging — the two candidate standards for
assessing "reasoning-operation quality independently of elaboration level" (complexity-
relative and universal-scale) both reintroduce the adversarial record as a determinant,
the former as the comparison frame and the latter as the quality signal, and neither is
operationalized in the proposed methodology with inter-rater reliability established.
On (8): SC6(b-1) anti-naturalistic pairs test coverage ranking when the material set
is implicitly pre-specified by pair construction — they do not test the upstream
materiality-identification step where the LLM must identify which brief arguments
satisfy art. 489, §1º, IV from raw brief content with no pre-specification; the
categorical composite relocates rather than resolves the complexity-relative problem —
reference-answer construction for ratio identification precision and material argument
engagement completeness requires record-sensitive analytical work whose difficulty
correlates with adversarial record complexity; and the three-measure composite omits
C3 and C4, leaving the falsification criterion ambiguous for quality differences on
the unmeasured dimensions.
On (9): the formal pre-decision/post-decision C1 distinction is accepted; the
structural counter-prediction is that post-decision texts in high-adversarial-record
cases are harder for annotators to read for three reasons internal to the text —
negation-heavy reasoning structure (courts explaining why rejected characterizations
fail, in the same judicial voice as the accepted characterization, producing text where
both are present for annotators to disentangle); conjunctive/alternative grounds
(multi-ground holdings where the text presents both X and Y as the court's reasoning
without explicitly designating which is the fundamento determinante); and collegial
fragmentation in STF plenary decisions (multiple individual votes each characterizing
the ratio differently, with no single court-authored synthesis, requiring annotators
to aggregate across fragmented opinions) — each feature is adversarial-record-correlated
and produces annotation difficulty in the high-adversarial-record arm independent of
the pre-decision difficulty the supportive's distinction correctly rules out; the C3
stylometric operationalization conflates legally mandated verbatim text with formulaic
reasoning avoidance — within fine-grained doctrinal clusters, every correctly-citing
decision quotes the same statutory provisions and leading precedent holdings verbatim
in its reasoning section, generating cross-decision recurring phrases at or above the
5-word/2-decision threshold regardless of whether the reasoning embedding those
quotations is formulaic or case-specific, and no frequency threshold can resolve this
categorical distinction between mandatory citation practice and optional formulaic
reasoning because both produce recurrence that the threshold flags equally; and
SC6(b-1)-ID presupposes dispositif determinacy — the outcome-dependency materiality
standard requires mapping brief arguments to dispositif components and assessing
ground independence in multi-component holdings, and the difficulty of this mapping
scales with adversarial record complexity for the same structural reason that produces
negation-heavy C1 texts and multi-ground holdings, so the arm-specific differential
inter-rater reliability concern the round 8 adversarial response identified for
reference-answer construction at the composite scoring step applies equally at the
SC6(b-1)-ID calibration annotation step, where annotators must establish the material
argument set for brief-dispositif pairs whose complexity varies by adversarial record.
Through rounds 1–9, the cumulative adversarial position was: within-cluster C2-specific
criterion activation cannot be ruled out under the current protocol design; coverage
completeness as a within-adequacy ranking signal requires the case-record input
extension, calibration generalization validation via SC6(b-2), and separate validation
of the materiality-identification step from raw brief material via calibration pairs
that test argument-level materiality judgment with no pre-specified material set;
SC6(c) determines which prong of the C2 disjunction applies; under prong 2, SC6(3)
requires a cross-elaboration test whose categorical composite must (a) satisfy a
differential inter-rater reliability condition — agreement on reference-answer
construction for high-adversarial-record champions must be comparable to agreement for
matched low-adversarial-record champions — and (b) be extended to cover all five C1-C5
dimensions to make the falsification criterion interpretively unambiguous; additionally,
the SC6(b-1)-ID calibration annotation step itself must satisfy arm-specific
differential inter-rater reliability — annotators identifying the material argument set
for high-adversarial-record brief-dispositif pairs (where dispositif complexity is
greater and ground independence assessment is harder) must achieve agreement levels
comparable to annotators working on matched low-adversarial-record pairs; and the C1
post-decision text-reading distinction must be validated empirically rather than
assumed — whether annotators reading the court's own ratio characterization achieve
comparable arm-specific reliability across high- and low-adversarial-record cases
depends on whether the three text-level features (negation-heavy structure, multi-
ground holdings, collegial fragmentation) produce measurably higher annotation
variance in the high-adversarial-record arm; these three text-level features remain the
primary basis for the surviving arm-specific differential IRR prediction for the C1
annotation task, now re-scoped to ementa-interpretation difficulty after the ementa-as-
authoritative-ratio source reduction (round 10) addresses the voto-synthesis dimension.
On (10): official-database preprocessing is accepted as addressing legally-mandated text
conflation for the categories covered (constitutional provisions, federal statutes,
STF/STJ súmulas); residual gaps exist for court-specific Regimento Interno formulas and
institutionally conventional language — both generating phrase frequencies that
official-database stripping does not remove — and a cross-cluster-convention stripping
step is required to close them (SC6(g) updated accordingly); the ementa-as-authoritative-
ratio source-reduction benefit is accepted, with collegial fragmentation addressed at the
annotation-source level; two annotation-task limits remain — implicit-structure ementas
with unlabeled multi-item ground structures (requiring limited voto engagement for
specific cases) and principle-level abstraction (ementas of contested STF constitutional
decisions characterize the ratio at constitutional-principle level rather than
doctrinal-specific level, generating ementa-interpretation difficulty in the
high-adversarial-record arm that the source-reduction move does not close); the
court-stated-theory constraint is accepted as a genuine narrowing for quality-filter
decisions; ementa-theory generality remains as a residual for contested constitutional
decisions where the principle-level theory characterization does not adjudicate argument
materiality at the doctrinal-specific level, and calibration-scope representativeness
remains as a second residual if the evaluation target extends beyond quality-filter
exemplars. On (11): the C1 relocation's annotation-source benefit (ementa reading
over voto synthesis) is accepted unconditionally; the annotation-task challenge is
preserved through the citing-court characterization mismatch — the citing court
operates at the specific doctrinal level ("rule R in situation S is a fundamento
determinante") while the ementa characterizes the ratio at the abstract-principle level
("principle P applies"), and closing this gap requires principle-to-application-level
mapping that goes beyond ementa-reading at the ementa's level; the type (a)/(b)
demarcation presupposes established-application-area knowledge — determining whether
a specific construction falls within type (a) (established) or type (b) (novel)
requires knowing the accumulated doctrinal record of how the abstract principle has
been applied at the specific level, which is itself contested in the high-adversarial-
record arm; implicit-structure flagging is accepted as a solution for its class with a
class-size concern — the flagging rate in the contested-constitutional arm (where
multi-item ementas without explicit connectives are structurally concentrated) may be
high enough to convert the annotation tractability problem into an operational-capacity
constraint at champion scale, requiring arm-specific flagging rates in the empirical
reporting; and the C3 cross-cluster-convention stripping advance is accepted for
universally-conventional institutional formulas while a procedural-type-specific
residual survives — phrases that are conventional within procedural-posture clusters
(habeas corpus admission formulas, recurso especial admissibility templates) but not
cross-doctrinal-subject in distribution are not captured by the three-cluster frequency
criterion, requiring a posture-type stripping step to close. On (12): posture-type stripping is
accepted unconditionally — the three-layer preprocessing sequence closes all three C3
residual categories and surrender condition (g) is updated accordingly; type (b) shared-
infrastructure gap-filling is accepted, with arm-specific combined type (b) plus implicit-
structure class size from the pre-calibration pilot as the single remaining operational
constraint; the Jurisprudência Temática/Teses database-lookup operationalization is
accepted as structurally parallel to C3 preprocessing and as correctly handling paradigm
type (a) cases, but the granularity gap survives — thematic-level compilation entries
confirm the abstract principle's established application to the thematic domain without
specifying which particular doctrinal constructions within the domain are fundamentos
determinantes, and this is the same resolution level as the ementa-as-authoritative-ratio
source-reduction, which itself left the principle-to-doctrinal-application annotation-task
challenge unresolved; the currency limitation compounds the granularity gap in the
contested-boundary subclass — compilation coverage of settled doctrine does not extend to
contested interpretive developments that constitute the high-adversarial-record arm's hard
core, defaulting those cases to type (b) by the negative-identification test; and the
secretariat authorship convention claim for the implicit-structure flagging rate is
insufficiently attested — the claim requires documentary support for a convention that
overrides two independently stated structural drivers (multi-issue simultaneous resolution;
cross-court citation listing function), and until the pilot data is available both sides'
rate projections are structurally inferred, with the adversarial's projection having two
stated structural drivers and the supportive's having one undocumented mechanism claim.
On (13): the step-1/step-2 distinction is accepted as accurately describing the compilation's step-1 function (domain classification for type (a)/(b) demarcation) and the ementa's step-2 function (C1 source document supplying the fundamento determinante characterization at principle level); the distinction correctly identifies the ementa as the step-2 source, which round 10 established, and does not re-contest this; the granularity challenge survives under the new framing — the step-1/step-2 distinction resolves the step-2 SOURCE question but not the step-2 TASK question: the annotation task at step 2 requires comparing the citing court's doctrinal-specific characterization against the ementa's abstract-principle characterization, a comparison that crosses the specificity gap and requires principle-to-application assessment; the distinction responds to a source question (which document?) that round 10 already resolved rather than the task question (is the comparison tractable across the specificity gap?) that the round 11 and 12 adversarial arguments raised; the currency limitation acceptance is accepted as correctly describing the default rule's conservative routing — lag-window class size and class composition determined by the pilot; the secretariat convention withdrawal is accepted as epistemically appropriate — the pilot resolves both sides' structural inferences about the flagging rate.
On (14): the C1/C4 structural distinction is accepted as formally valid — C1 identifies fundamentos determinantes (Art. 489, §1º, V) while C4 checks correct application, distinction, and justified deviation (Art. 927, §1º); the two criteria are non-redundant on both the designative and the conceptual-coverage reading of *identificar*; the purely designative reading of *identificar* is contested through two statutory grounds — the possessive *seus* in Art. 489, §1º, V (implying the cited precedent has actual fundamentos determinantes that must be correctly recognized, not merely any named principle) and Art. 489, §1º, VI's parallel *que justifiquem* formulation (which embeds a substantive justification requirement in VI's own *identificar*, establishing that the parallel V-provision's *identificar* is non-designative by structural analogy); the third case (citing court names the abstract principle P but nominates an obiter proposition as the fundamento determinante) satisfies C1 on the purely designative reading while failing to identify the cited precedent's actual fundamentos determinantes — which is the paradigm C1 failure Art. 489, §1º, V targets; on the conceptual coverage reading, the step-2 annotation task requires determining whether the nominated specific construction was actually determinative in the cited precedent, a question the ementa's abstract-principle characterization does not resolve; and the falsification condition the supportive specified — arm-specific C1 IRR lower for acknowledgment-present-but-application-contested cases — is accepted as the correct discriminating test, with the conceptual coverage reading predicting exactly that IRR pattern while the purely designative reading predicts cross-arm agreement.
On (15): the V/VI textual economy inference is accepted unconditionally — V's *identificar* is purely designative and the designative/conceptual-coverage question is closed in the designative reading's favor; the ementa-anchored designative account's response to *seus* and the third case (obiter-nomination) is accepted as internally coherent; the surviving contest is at the constitutive-authority level — whether the ementa IS (constitutively) the cited precedent's fundamentos determinantes for art. 489, §1º, V compliance purposes, or is evidential (presumptively accurate but rebuttable); a fourth case (elevation error: ementa mischaracterizes an obiter proposition P' as a fundamento determinante; citing court invokes P'; ementa-anchored designative check licenses C1 satisfaction; but the citing court has not identified the cited precedent's actual fundamentos determinantes — the paradigm §1º, V failure) defeats the ementa-anchored account's completeness claim; two structural drivers concentrate elevation errors in the high-adversarial-record class ESHTR targets — secretariat synthesis under fragmented collegial deliberation and breadth incentive in the ementa's cross-court citation function; the IRR pilot discriminates which reading of *identificar* annotators operationalize but does not test whether the ementa-anchored reference set is accurate about which grounds were actually load-bearing; high IRR under the ementa-anchored designative reading and systematic annotation error (uniform C1 satisfaction for elevation-error cases) are compatible outcomes, leaving the constitutive-versus-evidential question open at the structural level.
On (16): the compliance-assessment/accuracy-standard distinction is accepted as correctly characterizing art. 489, §1º, V as a provision governing the citing court's conduct rather than auditing the cited court's ementa accuracy — but the distinction reframes rather than resolves the constitutive/evidential question: a compliance-assessment standard can assess compliance against either what the ementa characterizes as ratio (constitutive) or the actual load-bearing grounds with the ementa as presumptive evidence (restricted evidential), and the compliance-assessment character of art. 489, §1º, V does not determine which operative reference applies; the institutional-allocation argument (accuracy obligation runs to the cited court's self-documentation, not to the citing court's compliance) is contested as circular under the constitutive account it claims to support: the separation between cited court self-documentation obligation and citing court compliance obligation is only coherent under the evidential account's institutional-responsibility structure, which distinguishes between ementa characterization and actual load-bearing grounds — under the constitutive account no such separation exists, because the ementa's characterization IS the fundamentos determinantes, leaving no "self-documentation accuracy" category that could be assigned to the cited court; importing the evidential account's structural distinction as a premise for the constitutive conclusion is circular; the compliance-determinacy concern is addressed by a restricted evidential trigger — a subsequent authoritative determination (superior court decision, *tese vinculante*, or *entendimento cancelado* resolution) expressly revising the cited precedent's ementa characterization of its fundamentos determinantes — which is determinate (either an authoritative revision exists or it does not), publicly available through the same case-law databases citing courts consult for precedent identification, and narrow (covering only ementas whose characterization has been authoritatively revised); the systemic-structure concern does not apply to the restricted trigger class because the citing court checks the public case-law record for authoritative revisions, not the plenary votos; structural-driver frequency remains pilot-determined; the surviving question is whether primary Brazilian procedural authority resolves the constitutive/evidential question — specifically, whether art. 489, §1º, V's enacted text and institutional purpose establish the ementa's characterization as constitutive by design or accommodate the restricted evidential reading for authoritatively-revised ementas.
On (17): the non-circularity response generates a statutory grounding requirement — the constitutive account's admission that the elevation error is a "defect in cited court self-documentation" presupposes an accuracy standard for ementa authorship that only the evidential reading supplies; no CPC provision independently establishes the cited court's obligation to accurately characterize its actual fundamentos determinantes in its ementa outside §1º, V on the evidential reading: art. 926's coherence obligation is a stability requirement over time rather than an accuracy standard for individual ementa characterizations relative to the underlying deliberation; art. 926, §2º applies to súmulas not ordinary ementas; art. 927, §4 provides a prospective modification standard not a retroactive accuracy standard; art. 93, IX CF's fundamentação requirement applies to the decision, not the secretariat's ementa; without an independent statutory source, the accuracy standard that constitutes the elevation error as a "defect" must be derived from §1º, V on the evidential reading — confirming rather than defeating the round 17 circularity charge; the restricted trigger absorption is contested for the correction-revision class — Brazilian revision proceedings divide structurally into changed-circumstances revisions (the original was accurate when issued; circumstances warrant a new determination; constitutive absorption stable; no inaccuracy implied) and correction revisions (the original characterization was recognized as evidentially inaccurate; the triggering mechanism is inaccuracy); for correction revisions, the constitutive absorption suppresses the triggering condition: all revisions become new constitutive references, making correction and change revisions formally indistinguishable by their triggering mechanism; correction revision proceedings in Brazilian practice engage the accuracy-of-original-characterization question — they explain why the original was wrong, not merely that a new determination supersedes it — which is unintelligible under the constitutive account where no ementa characterization can be wrong for compliance purposes; the surviving question for the correction class is whether Brazilian procedural doctrine recognizes the constitutive absorption of correction revisions or presupposes the evidential account's accuracy standard as the triggering condition.
The practical implication across all seventeen exchanges: within-cluster C2-specific criterion
activation cannot be ruled out under the current protocol design; the round 10 advances
substantially address C3 conflation for officially-mandated text categories,
collegial-fragmentation at the annotation-source level, and SC6(b-1)-ID tractability for
quality-filter calibration decisions; round 11's C1 relocation advances annotation-source
tractability unconditionally while the annotation-task challenge relocates from
principle-level voto-synthesis to principle-to-application-level gap-filling at the type
(b) hard core; round 12 closes the procedural-type C3 residual via posture-type stripping
and closes the type (b) gap-filling cost question via shared infrastructure, while the
Jurisprudência Temática/Teses operationalization inherits the granularity gap that the
ementa-as-authoritative-ratio move left unresolved — thematic-level classification does
not identify doctrinal-specific fundamentos determinantes — and the currency limitation
compounds the granularity gap in the contested-boundary subclass; round 13 accepts the
step-1/step-2 distinction as correctly identifying the ementa as the step-2 source
document while establishing that the step-2 annotation task — comparing the citing court's
doctrinal-specific characterization against the ementa's abstract-principle characterization
— requires principle-to-application assessment that the source-identification distinction
does not address; round 14 accepts the C1/C4 structural distinction as formally valid —
C1 (*identificar fundamentos determinantes*) and C4 (correct application, distinction,
justified deviation) are non-redundant on both readings of *identificar* — while contesting
the purely designative reading of *identificar*: the possessive *seus* in Art. 489, §1º, V
implies a correct set of fundamentos determinantes to recognize (not merely any named
principle), and Art. 489, §1º, VI's parallel *identificar* carries a *que justifiquem*
requirement that is non-designative — establishing that *identificar* in V carries
conceptual-coverage content requiring the annotator to determine whether the nominated
construction was actually a fundamento determinante of the cited precedent; the third
case (citing court names the abstract principle but nominates an obiter proposition as
the fundamento determinante) is the paradigm C1 failure Art. 489, §1º, V targets and
is missed by the purely designative reading; on the conceptual coverage reading, the
step-2 annotation task requires determining whether the nominated specific construction
was actually determinative in the cited precedent — a question the ementa's abstract-
principle characterization does not resolve; and the IRR falsification condition is
accepted as the correct discriminating test, with the conceptual coverage reading
predicting exactly the acknowledgment-present-but-application-contested IRR divergence
the supportive named; the surviving arm-specific differential IRR concerns are: (a) for C1,
ementa-interpretation difficulty at the principle-to-doctrinal-application gap, now
reformulated as the step-2 task tractability challenge — whether the comparison between
the citing court's doctrinal-specific characterization and the ementa's abstract
characterization is tractable without crossing the specificity gap (relocated from
voto-synthesis but not eliminated); (b) for SC6(b-1)-ID, the type (b) hard core
concentrated where granularity and currency limitations simultaneously operate in the
contested-boundary subclass of the high-adversarial-record arm, with pilot data
determining both class size and class composition; coverage completeness as a
within-adequacy ranking signal continues to require the case-record input extension and
materiality-identification calibration; SC6(c) determines which prong of the C2
disjunction applies; under prong 2, SC6(3) requires the cross-elaboration test with
cross-cluster-convention and cross-elaboration extensions; round 15 closes the
designative/conceptual-coverage question — the V/VI textual economy inference (non-redundancy
requires V's *identificar* to be purely designative, with VI's *que justifiquem* adding the
application-justification layer V lacks) is accepted unconditionally, resolving the reading
of *identificar* in the designative reading's favor, while the ementa-anchored account's
response to *seus* (the ementa constitutes the objective reference set) and to the third
case (obiter-nomination caught by ementa non-match) is accepted as internally coherent; round 16
presses the surviving contest at the constitutive-authority level — the ementa is evidential
rather than constitutive of the cited precedent's fundamentos determinantes: the fourth case
(ementa elevation error: secretariat mischaracterizes an obiter proposition as a fundamento
determinante, citing court invokes it, ementa-anchored check licenses C1 satisfaction, but
the paradigm §1º, V failure is present) demonstrates that the ementa-anchored designative
reading does not catch all paradigm failures; two structural drivers concentrate elevation
errors in the high-adversarial-record class — secretariat synthesis under fragmented
collegial deliberation and breadth incentive in the ementa's cross-court citation function;
the IRR pilot discriminates which reading of *identificar* annotators operationalize but does
not test ementa accuracy, leaving the constitutive-versus-evidential question as the surviving
open issue requiring authoritative resolution; round 17 accepts the compliance-assessment/accuracy-standard distinction as correctly characterizing art. 489, §1º, V without resolving the constitutive/evidential question — both accounts remain compliance-assessment standards that differ in what the operative reference of compliance is; contests the institutional-allocation argument as circular under the constitutive account it claims to support — the separation between cited court self-documentation obligation and citing court compliance obligation is only available under the evidential account's institutional-responsibility structure, which presupposes exactly what the constitutive account denies; and identifies a restricted evidential trigger (subsequent authoritative revision of the cited precedent's ementa characterization) that addresses the compliance-determinacy concern without requiring general behind-the-ementa reading, applying only to the narrow class of ementas whose characterization has been authoritatively revised in subsequent superior court decisions or formalized *tese* proceedings; the restricted trigger is determinate and publicly available through standard case-law databases, without imposing the systemic-structure burden of reconstructing fragmented deliberations that the high-volume appellate environment makes intractable; the surviving terminal question is whether primary Brazilian procedural authority — text, legislative history, or authoritative doctrinal treatment — establishes the ementa's characterization as constitutive by institutional design or accommodates the restricted evidential reading for authoritatively-revised ementas; round 18 presses the non-circularity response for independent statutory grounding — the constitutive account's (a)/(b) distinction requires a CPC provision that independently establishes the cited court's ementa-accuracy obligation, and no such provision exists; the "defect" concession imports the evidential account's accuracy standard as the content of obligation (a), confirming the circularity charge; and contests the restricted trigger absorption for correction revisions — the constitutive account cannot explain why correction revision proceedings engage the accuracy-of-original-characterization question if no ementa characterization can be wrong for compliance purposes, suggesting that Brazilian practice presupposes the evidential account's accuracy standard as the triggering condition for this class even when the revision's formal effect is constitutively a new reference; round 18 support response contests the secretariat-summary premise — under CPC art. 943, the ementa is a formal component of the acórdão lavrado pelo relator, not a secretariat-produced summary; art. 93, IX CF therefore applies to the ementa-component, and an elevation error constitutes a fundamentação defect (internal inconsistency within the relator-authored acórdão between the ementa's characterization and what the votos establish as the ratio); the correction-revision class is assigned to obligation (a) under art. 93, IX CF — the cited court's recognition of ementa mischaracterization triggers a correction revision as an exercise of its obligation to maintain fundamentação consistency within the acórdão — while for obligation (b) purposes both revision types produce new constitutive references indifferently; round 19 accepts the art. 943 characterization and art. 93, IX CF's application to the ementa-component while contesting the scope of the fundamentação requirement — art. 93, IX CF mandates presence and expression of reasoning in the votos (the decision must not be arbitrary; the grounds for the holding must be stated), not accuracy of the ementa's characterization of which element of the expressed reasoning was the ratio; an elevation error leaves the votos' expressed reasoning intact and the decision fundamentada; the headnote-to-body inaccuracy does not make the decision "sem fundamentação" because the reasoning is present and expressed in the votos; obligation (a) accordingly lacks art. 93, IX CF grounding at the ementa-characterization-accuracy level even under relator authorship; and the correction-revision triggering condition cannot be assigned to obligation (a) without the characterization-accuracy scope that art. 93, IX CF does not supply, preserving the round 18 adversarial argument that the correction-revision class presupposes the evidential account's accuracy standard without available statutory grounding within the constitutive framework; round 19 support response contests the scope-narrowing on three grounds — the "heading/body" vocabulary is in tension with the art. 943 acceptance (the ementa is a formal acórdão component, not a heading external to the acórdão; describing the inconsistency as a "heading-to-body" inaccuracy encodes the conclusion the art. 943 acceptance forecloses), art. 93, IX CF's "decisões" covers the acórdão as a whole so the scope limitation requires a positive argument for asymmetric application to formal acórdão components not supplied in round 19, and art. 93, IX CF's accountability function operates through the ementa as the official published ratio statement under arts. 926-927 and therefore extends to ementa-characterization accuracy; round 20 concedes the "heading/body" vocabulary (withdrawn as inconsistent with art. 943 acceptance; the ementa is a relator-authored formal acórdão component whose function is citation summarization), supplies the missing positive argument through functional differentiation within the acórdão — art. 943 identifies three relator-authored formal acórdão components (relatório, votos, ementa) serving distinct constitutional functions; the relatório counterexample establishes that formal component status under art. 943 does not determine art. 93, IX CF scope (Brazilian doctrine does not require the relatório to be fundamentada in the same constitutional sense as the votos; if all relator-authored formal acórdão components were covered by "fundamentadas" in the same constitutional sense it would follow that the relatório must satisfy the fundamentação requirement, an implication not maintained in doctrine; scope tracks the reasoning-expression function, not formal component membership; the ementa's citation-indexing function, like the relatório's factual-summary function, does not make it a bearer of the reasoning-expression obligation that "fundamentadas" targets) — and rejects the accountability conflation (art. 93, IX CF's accountability mechanism is reasoning-presence reviewability served by the votos; the ementa's accountability mechanism is citation-coherence under arts. 926-927, governed by different statutory provisions; the constitutive account's own (a)/(b) structural separation requires obligation (a) and obligation (b) to be governed by different statutory schemes; grounding obligation (a) in art. 93, IX CF collapses this separation and eliminates the two-obligation structure; the accountability argument establishes that some accuracy obligation exists from some source, which the adversarial does not deny, but does not establish that art. 93, IX CF rather than arts. 926-927 is the provision that governs it).

**On the Phase 3 attack (§§3.6–3.8):**

The defense's factual correction is accepted and incorporated into the reframed §3.6:
Phase 3 IS the controlled cross-cluster comparison ESHTR's design enables. The prior
characterization ("precisely the operation ESHTR's hierarchical design was constructed
to avoid") was inaccurate. The reframed attack survives this correction: Phase 3
performs cross-cluster C1-C5 comparison subject to the same Tversky criterion-switching
mechanism; its tractability claim requires empirical confirmation that the structural
controls (champions, instruction, small k) provide sufficient attenuation.

The defense's mechanism-level argument for the instruction's effect (§4.5) is accepted
as a theoretical prior: the explicit instruction should reduce domain-specific feature
salience under the Tversky feature-salience account. Changing the comparison frame from
implicit to explicit is distinct from eliminating domain-specific feature influence. The
adversarial position is that "should reduce" is not "has been confirmed to reduce
sufficiently" — the mechanism argument establishes the prior; the empirical test
establishes whether the attenuation is sufficient. The defense acknowledges the test is
required; surrender condition §6(3) specifies it.

The redundancy argument (§4.4 of the defense) is cleanly refuted and accepted. Selecting
the highest-aggregate-C1-C5 decision across all clusters IS a cross-cluster comparison
problem; there is no bypass around Phase 3 for any global ranking. The adversarial
inference from "necessary implication holds" to "Phase 3 is unnecessary" was incorrect.
Phase 3 is structurally required; the question is whether it produces a reliable result.

The defense's most direct remaining reply is Option (c): structural reading of
domain-specific text allows LLMs to assess reasoning structure without evaluating
doctrinal content. §3.7 establishes why this is an implementation aspiration rather
than a confirmed LLM behavior: the same domain-specific criterion activation that
makes within-cluster judgments reliable (acknowledged in `yesindeed/frame-stability-sph.md` §3.3) creates the implementation gap Option (c) must bridge. Whether the
Phase 3 instruction bridges it is the empirical question neither the mechanism argument
nor the current calibration protocol answers.

The supportive paper (§4.5) correctly identifies an asymmetry in this adversarial
position: SPH for Phase 2 is accepted as a warranted mechanism-grounded conjecture
while "not sufficient" is pressed specifically against Phase 3. The asymmetry requires
justification, and here it is.

Phase 2's SPH mechanism predicts that existing LLM criterion-activation patterns
operate more consistently within semantic proximity clusters than across them. This
is additive: embedding-based clustering + LLM's existing criterion-domain associations
(acquired in training) → within-cluster consistency. No new LLM behavior is required.
The prediction is that LLMs will do what they already do, in a pairing context where
the training-encoded criterion-domain associations are more uniformly relevant. The
mechanism is with the grain of trained LLM behavior.

Phase 3's tractability mechanism predicts that the explicit abstraction instruction
will actively redirect criterion application away from domain-specific feature salience
toward structural method properties. This is not additive to the Phase 2 mechanism —
it requires the instruction-following layer to suppress the domain-specific feature
salience that Phase 2's mechanism depends on. A model instruction that changes the
explicit label attached to the output ("I am evaluating reasoning structure") without
altering which features activate that output satisfies the surface requirement without
achieving the representational override. Whether instruction-tuning reliably achieves
the override at the level of feature salience — not only at the level of output
labeling — is a structural question about the depth of the instruction-following
mechanism's reach into the representation-to-output mapping. Phase 3's prediction
requires the mechanism to work against the grain of domain-specific training, not
with it.

This structural difference justifies asymmetric evidential demands. The mechanism
argument for Phase 3 tractability is of the same logical form as SPH — a mechanism-
grounded conjecture with a falsifiable prediction — but the prediction requires a
specific LLM behavior (instruction-modulated suppression of trained feature salience)
that Phase 2's prediction does not. The "not sufficient" concern is not about logical
form; it is about the depth of behavioral evidence needed to confirm that the required
suppression actually occurs in practice, specifically in the domain-integrated texts of
champion decisions where trained feature salience is strongest.

The concrete calibration protocol is the right kind of test, but the three structural
limits identified in §3.6 (circular quality ground truth; champion-scale gap;
variance-source confound in measurement 2) mean it provides behavioral evidence for
the instruction effect in a non-champion population with a Phase-2-derived quality
validator and a variance diagnostic whose intermediate results the accepted mechanism
renders ambiguous — not evidence sufficient to establish that the override works in
the harder champion case against an independent quality standard under an unconfounded
diagnostic. The expected pattern of results across measurements 1, 2, and 3 under
each competing hypothesis — structural-reading mode, circularity, and pair-specific
quality-dimension-profile dominance (source ii active after domain-mapping suppression)
— is not pre-specified in the protocol, which is what would convert three measurements
from a descriptively richer result into a discriminating test.

Separately, for the Phase 2 sections (§§3.1–3.5): the mechanism paper's
sub-predictions provide more diagnostic sharpness than aggregate κ, but address
between-cluster non-transitivity patterns. They do not separately measure
within-cluster cycle incidence relative to quality-dimension asymmetry profiles,
which is the quantity Sections 3.3–3.4 target. The experiment as designed does
not generate the data needed to test the within-cluster component of this attack.

---

## 5. Scope of the Attack

This attack targets ESHTR's stated ambition to produce a *global quality
ranking* of judicial decisions and the use of embedding similarity as a
design principle for evaluative stability. The attack has been sharpened by:
accepting the contingent frame construction mechanism as the best available
account of why SPH should hold; accepting the defense's factual correction that
Phase 3 performs intentional controlled cross-cluster comparison (not a repetition
of what Phase 2 was designed to avoid); accepting the mechanism-level argument
that the explicit instruction provides a theoretical prior for non-transitivity
attenuation — while pressing that a theoretical prior requires empirical
confirmation of sufficiency; and arguing that Option (c) structural reading, while
theoretically coherent, is not established as the implementation mode frontier LLMs
reliably reach under the Phase 3 abstraction instruction, given that the same
domain-specific criterion acquisition identified in the accepted mechanism as the
source of within-cluster reliability creates the implementation gap Option (c) must
bridge. On the Phase 2 front, the mechanism's own logic produces item-level
criterion-activation patterns inconsistent with the non-systematic assumption the
Bradley-Terry aggregation defense requires; and accepting the pair-specificity
correction to §3.3 — that persistent activation across all pairings was too strong
a claim — while pressing the narrowed claim: systematic criterion activation in
cross-strength pairings and the cluster-composition dynamic both produce structured
Bradley-Terry scoring artifacts, and the pair-specificity response's success depends
on the quality-dimension correlation claim that §3.2 contests. On the C2 annotation-task
front: round 13 accepts the step-1/step-2 distinction as accurately describing the
ementa's document-level function as the step-2 source while pressing that the annotation
task at step 2 requires comparing the citing court's doctrinal-specific characterization
against the ementa's abstract-principle characterization — a cross-specificity comparison
the source-identification distinction does not address; round 14 accepts the C1/C4
structural distinction as formally valid while contesting the purely designative reading
of *identificar* — the conceptual-coverage reading is textually grounded in the possessive
*seus* (Art. 489, §1º, V) and the parallel *que justifiquem* formulation (Art. 489, §1º,
VI), establishing that *identificar* requires the annotator to determine whether the
nominated construction IS a fundamento determinante, not merely whether an abstract
principle was named; the step-2 annotation-task challenge survives on the conceptual
coverage reading; the IRR falsification condition the supportive named is accepted as the
correct discriminating test, with the conceptual coverage reading predicting the
acknowledgment-present-but-application-contested IRR divergence pattern; accepting the
currency limitation as the correct operational description of conservative type (b)
routing with lag-window class size and class composition determined by the pilot; and
accepting the secretariat convention withdrawal with the pilot as the sole resolution for
the implicit-structure flagging rate; round 15 closes the designative/conceptual-coverage
question by accepting the V/VI textual economy inference unconditionally — V's *identificar*
is purely designative — while accepting the ementa-anchored designative account as
internally coherent in its handling of *seus* and the third case (obiter-nomination); round
16 shifts the surviving contest to the ementa's constitutive-versus-evidential status —
contesting that the ementa constitutively defines the cited precedent's fundamentos
determinantes for art. 489, §1º, V compliance purposes by introducing the fourth case
(ementa elevation error), identifying two structural drivers for elevation errors concentrated
in the high-adversarial-record class (secretariat synthesis under fragmented plenary
deliberation; breadth incentive in the ementa's cross-court citation function), and
distinguishing the IRR pilot's discriminatory scope (which reading of *identificar*
annotators operationalize) from the open question (whether the ementa-anchored reference
set is accurate about which grounds were actually load-bearing in the cases where
annotators anchor to it); round 17 accepts the compliance-assessment framing while contesting the institutional-allocation argument as circular under the constitutive account it claims to support — the self-documentation/compliance-obligation separation is only coherent under the evidential account's institutional-responsibility structure, and importing that structure as a premise for the constitutive conclusion is circular — and identifies a restricted evidential trigger (authoritative subsequent revision of the cited precedent's ementa characterization, available in the public case-law record) that addresses the compliance-determinacy concern without requiring general behind-the-ementa reading, preserving the fourth case's coverage for the narrow class of authoritatively-contested ementa characterizations; round 18 presses the non-circularity response for independent statutory grounding — no CPC provision independently establishes the cited court's ementa-accuracy obligation outside §1º, V on the evidential reading; the elevation-error "defect" concession imports the evidential account's accuracy standard as the content of obligation (a), confirming rather than defeating the round 17 circularity charge; and contests the restricted trigger absorption for the correction-revision class, showing that correction revision proceedings presuppose the evidential account's accuracy standard as their triggering mechanism — a presupposition the constitutive absorption suppresses by treating all revisions as mere supersession; round 18 support response contests the secretariat-summary premise — under CPC art. 943, the ementa is a formal component of the acórdão lavrado pelo relator; art. 93, IX CF therefore applies to the ementa-component and an elevation error is a fundamentação defect; the correction-revision class is assigned to obligation (a) under art. 93, IX CF, with obligation (b) indifferent to triggering mechanism across both revision types; round 19 accepts art. 943 and art. 93, IX CF's application to the ementa while contesting the fundamentação requirement's scope — the provision mandates presence and expression of reasoning in the votos, not accuracy of the ementa's characterization of which element of the expressed reasoning was the ratio; the elevation error is a headnote accuracy problem that leaves the votos' expressed reasoning intact; obligation (a) lacks art. 93, IX CF grounding at the ementa-characterization-accuracy level; and the correction-revision triggering condition cannot be assigned to obligation (a) without the characterization-accuracy scope art. 93, IX CF does not supply; round 19 support response contests the scope-narrowing through three arguments — the "heading/body" vocabulary is in tension with the art. 943 acceptance (the ementa is a formal acórdão component, not a heading external to the acórdão), art. 93, IX CF's "decisões" covers the acórdão as a whole requiring a positive argument for asymmetric scope that round 19 does not supply, and art. 93, IX CF's accountability function extends to the ementa as the official ratio statement under arts. 926-927; round 20 concedes the vocabulary (the "heading/body" framing is withdrawn; the ementa is a relator-authored formal acórdão component whose function is citation summarization), supplies the functional-differentiation argument as the missing positive argument — the relatório counterexample establishes the scope principle (Brazilian doctrine does not hold that art. 93, IX CF requires the relatório, a relator-authored formal acórdão component under art. 943, to be fundamentada in the same constitutional sense as the votos; if formal component status determined scope the relatório would also be covered, an implication not maintained in doctrine; scope tracks the reasoning-expression function, not formal component membership; the ementa's citation-indexing function does not make it a bearer of the reasoning-expression obligation) — and rejects the accountability conflation (art. 93, IX CF's accountability function is reasoning-presence reviewability served by the votos; the ementa's accountability function is arts. 926-927 citation-coherence; these are distinct mechanisms governed by distinct provisions; the constitutive account's (a)/(b) structure requires obligation (a) and obligation (b) to be governed by different statutory schemes, so grounding obligation (a) in art. 93, IX CF collapses the structural separation the constitutive account requires); round 20 support response introduces the ratio-constitutive function criterion to distinguish the ementa from the *relatório* within the accepted functional-differentiation framework: scope tracks function; the *relatório* is excluded because its factual-summary function bears no authoritative relationship to the court's *ratio* determination; the ementa's ratio-constitutive function — its role as the court's authoritative *ratio* characterization for arts. 926–927 citation compliance purposes — specifically brings it within art. 93, IX CF's scope; the correct scope criterion is not "reasoning-expression" (which applies to the votos alone) but "bearing an authoritative relationship to the court's *ratio* determination for the precedent system," which the ementa satisfies and the *relatório* does not; and the (a)/(b) structural separation is maintained as a two-actor, two-provision structure with art. 93, IX CF governing the cited court's obligation (a) and arts. 926–927 governing the citing court's obligation (b); round 21 adversarial response presses that the ratio-constitutive function criterion, correctly applied within the functional-differentiation framework, places the ementa's accuracy obligation within arts. 926–927's domain rather than art. 93, IX CF's domain, on three structural grounds: (1) criterion misapplication — the functional-differentiation framework places components inside the provision that governs their function; the ementa's ratio-constitutive function is by definition a precedent-coherence function governed by arts. 926–927 (that is what makes it ratio-constitutive); applying the functional criterion consistently places the ementa inside arts. 926–927's scope, which the constitutive account has always asserted, but does not additionally place it inside art. 93, IX CF's scope, because art. 93, IX CF governs reasoning-expression rather than precedent-coherence, and the ratio-constitutive function is not a reasoning-expression function; (2) redundancy challenge — art. 926 caput (*'Os tribunais devem uniformizar sua jurisprudência e mantê-la estável, íntegra e coerente'*) independently grounds the cited court's obligation to produce accurate ementas as part of the coherence and integrity requirement; an individual ementa that mischaracterizes the *ratio* of its decision introduces incoherence into the court's published jurisprudential output at the level of the specific publication event, directly violating art. 926 caput; with art. 926 caput grounding obligation (a) and arts. 926–927's compliance framework grounding obligation (b), the two-provision structure is satisfied and art. 93, IX CF is dispensable for obligation (a); (3) normative double-counting — the supportive r20 grounds the ementa's ratio-constitutive obligation simultaneously in art. 93, IX CF (obligation a grounding) and arts. 926–927 (obligation b grounding), but these provisions have different constitutional authority (art. 93, IX CF as a fundamental rights guarantee under CF Title IV; arts. 926–927 as CPC statutory provisions), different enforcement mechanisms (art. 93, IX CF's nullity sanction; arts. 926–927's compliance and recalibration framework), and different scope; the constitutive account has not provided a theory of how the same ratio-constitutive function grounds obligations under both provisions simultaneously or how their different authority and enforcement mechanisms interact; this is normative double-counting rather than a resolved statutory grounding; round 21 support response (§4.12) introduces the per-decision/cross-decision two-dimension analysis as the structural basis for art. 93, IX CF inclusion: the ementa's ratio-constitutive function has two analytically separable dimensions — the per-decision dimension (the act of designating which element of the expressed reasoning was decisive for this decision, which the supportive characterizes as a reasoning-expression act grounding obligation (a) in art. 93, IX CF's per-decision reasoning-expression obligation) and the cross-decision dimension (making that designation available for citation compliance under arts. 926–927, grounding obligation (b)); the *relatório* lacks both dimensions — its factual-summary function bears no authoritative relationship to the *ratio* determination at either level; the accountability function invoked for art. 93, IX CF is therefore not conflated with arts. 926–927 (they govern different analytical domains: per-decision reasoning adequacy versus cross-decision citation coherence), and there is no double-counting because each obligation is grounded in the provision appropriate to its analytical domain; art. 926 caput's integrity obligation operates systemically (maintaining coherent jurisprudência across cases over time) rather than per-ementa, and art. 926 §4's prospective-modification enforcement confirms the systemic rather than per-decision scope; round 22 adversarial response presses two structural challenges to the two-dimension analysis: (ii-a) designation versus expression — the per-decision dimension of the ementa's ratio-constitutive function is an act of designation (identifying and indexing which element of the already-expressed reasoning was decisive for this decision), not an act of reasoning-expression (producing the reasoning record that art. 93, IX CF's accountability mechanism reviews); the votos express reasoning and supply the reasoning-presence accountability function the provision targets; the ementa designates which expressed element was the *ratio*, a post-expression indexing act that does not make the ementa a bearer of the reasoning-expression obligation art. 93, IX CF imposes; the elevation error case — misidentifying the *ratio* — does not impair art. 93, IX CF accountability because the votos' expressed reasoning remains accessible and reviewable through the primary record; the *relatório* analogy confirms the principle: per-decision formal acórdão components bearing authoritative relationships to specific judicial outputs do not automatically fall within art. 93, IX CF's scope merely because they bear such relationships; the relator's formal characterization-duty is satisfied when the votos express reasoning, not when the ementa correctly designates which expressed element was the *ratio*; (ii-b) art. 926 caput per-event integrity scope — the "mantê-la íntegra" obligation in art. 926 caput requires courts to maintain their jurisprudência integral, and systemic integrity presupposes and entails per-ementa accuracy as its structural prerequisite: a court cannot maintain integral jurisprudência across cases if individual ementas systematically mischaracterize the *ratio* of the decisions they accompany; art. 926 §4's prospective-modification enforcement mechanism addresses the systemic-departure dimension of the integrity obligation and does not define or exhaust art. 926 caput's substantive scope; art. 926 caput's per-event integrity requirement therefore independently grounds obligation (a) — the cited court's ementa-accuracy obligation — without requiring art. 93, IX CF; the (a)/(b) two-actor structure is preserved under the adversarial's formulation: obligation (a) grounded in art. 926 caput (cited court's per-ementa accuracy as prerequisite to integral jurisprudência); obligation (b) governed by arts. 926–927's compliance framework (citing court's citation compliance obligation). Round 22 supportive response (§4.13): accepts the per-decision/cross-decision two-dimension analysis and contests both (ii-a) and (ii-b). Against (ii-a): the designation/expression dichotomy fails for collegial courts with individual voto authorship — in the STF, justices reach the same dispositif through independent rationes; the relator must determine from potentially divergent voto rationes which element constitutes the court's unified *fundamento determinante*; this is second-order reasoning about deliberative structure, not indexing a pre-given labeled item; the determination's accuracy dimension is demonstrated by the elevation-error mechanism — an act that can misfire when voto reasoning points in different directions has a genuine accuracy dimension that pure indexing of clearly-labeled pre-given items does not; voto accessibility does not satisfy art. 93, IX CF's accountability function at the normative-output level, because accountability requires the court's official characterization of what it determined as operative to be reliable, not merely access to the discursive reasoning the votos contain; the *relatório* parallel confirms the distinction: the *relatório* narrates external procedural history without constituting the court's normative output as a determinate *ratio* — there is no fact of the matter (the court's collectively-determined *ratio*) against which the *relatório*'s narration can be accurate or inaccurate in the relevant sense, while the ementa's designation constitutes that normative output and can be accurate or inaccurate against what the votos' collective deliberation established as the *fundamento determinante*. Against (ii-b): accepting arguendo art. 926 caput's per-event integrity scope, art. 93, IX CF remains non-redundant on three grounds — (1) constitutional normative level: art. 93, IX CF is a constitutional provision with constitutional-level obligation and nullity sanction, not displaceable by statutory amendment, while arts. 926–927 are CPC statutory provisions; (2) enforcement character: art. 93, IX CF's consequence is nullity of the *fundamentação*-defective decision — a per-decision, backward-looking sanction — while art. 926 §4's mechanism is prospective-modification justification, systemic and forward-looking; the simplified (a)/(b) structure without art. 93, IX CF does not supply nullity for obligation (a); (3) per-decision unconditional scope: art. 93, IX CF applies to every decision regardless of systemic effect; art. 926 caput's per-event integrity obligation, derived from the systemic-coherence requirement, may not reach isolated elevation errors in decisions otherwise consistent with established *jurisprudência*. Round 23 adversarial response presses three structural challenges to §4.13. (iii-a) Second-order reasoning does not relocate a function: the §4.13 collegial argument correctly establishes that the relator's STF determination is constitutive rather than merely retrieval-based — it involves second-order reasoning about deliberative structure and is not pure indexing. This does not establish that the determination falls within art. 93, IX CF's functional domain. Under the functional-differentiation framework accepted at round 20, provision scope tracks the function an act serves, not the cognitive character of the act. The relator's collegial determination, however constitutive and however cognitively demanding, produces the court's officially published *ratio* for arts. 926–927 citation compliance — this is its function. Second-order reasoning about which voto-expressed element constitutes the collective *fundamento determinante* serves the citation-coherence function regardless of the deliberative complexity involved. The argument traverses from "not pure indexing" to "therefore art. 93, IX CF governs" through "second-order reasoning about deliberative structure" — but this traversal requires showing that the determination belongs to art. 93, IX CF's functional domain rather than arts. 926–927's; it does not: determining the court's collectively decisive *ratio* for citation-compliance purposes is a precedent-coherence function however cognitively demanding its execution is in the collegial context. (iii-b) The accuracy-dimension argument imports the evidential account's structure: §4.13 distinguishes the ementa from the *relatório* on the ground that there is a fact of the matter — which element the votos' collective deliberation established as *fundamento determinante* — against which the ementa's designation can be accurate or inaccurate; the *relatório* lacks this accuracy dimension because it narrates external procedural events without constituting the court's normative output. This accuracy structure presupposes a prior ratio established by the votos independently of the ementa's designation — precisely the evidential account's structure. Under the constitutive account this support has defended across rounds 16–22 for §1º, V compliance purposes, the ementa constitutes the ratio for compliance purposes; there is no prior votos-established fact against which the ementa's designation is accurate or inaccurate in the compliance-assessment sense. The §4.13 collegial argument invokes the evidential account's accuracy structure (votos establish the ratio independently; ementa can accurately or inaccurately characterize it) to argue for art. 93, IX CF coverage of the per-decision dimension — while simultaneously defending the constitutive account for §1º, V compliance purposes. The accuracy dimension §4.13 identifies presupposes the evidential account and is in structural tension with the constitutive account being maintained elsewhere in the same defense. (iii-c) The nullity sanction does not attach to ementa-designation accuracy: §4.13's three-ground non-redundancy response against (ii-b) depends on art. 93, IX CF supplying a constitutional-level nullity sanction for obligation (a) that art. 926 caput alone cannot supply. This requires that ementa-designation inaccuracy triggers the art. 93, IX CF nullity sanction. Brazilian constitutional doctrine attaches the nullity sanction to *fundamentação* failure — decisions whose reasoning is absent, insufficient, or unreviewable in the votos. An elevation error — ementa designates Q as *ratio* while votos establish P as collectively decisive — does not impair the votos' expressed reasoning: the reasoning remains present, identifiable, and reviewable. A decision is not *nula* under art. 93, IX CF because its ementa misidentifies the *ratio* while the votos' reasoning is complete and accessible. If the nullity sanction does not attach to ementa-designation inaccuracy independently of voto reasoning-adequacy, the first non-redundancy ground fails: art. 93, IX CF does not supply a nullity for obligation (a)'s specific conduct — ementa-designation accuracy — that art. 926 caput's per-event integrity scope cannot also supply. The enforcement-character and scope-conditionality grounds (§4.13 grounds 2 and 3) are structurally dependent on the first: if the nullity sanction does not attach to ementa-designation accuracy, grounds 2 and 3 describe provisions governing structurally distinct obligations — art. 93, IX CF governing voto reasoning-expression; art. 926 caput governing per-event ementa accuracy as a structural prerequisite to integral *jurisprudência* — rather than alternative groundings of the same obligation at different normative levels. This confirms rather than defeats the adversarial's position: art. 93, IX CF does not govern ementa-designation accuracy; art. 926 caput does; the simplified (a)/(b) structure without art. 93, IX CF is available. Round 24 supportive response (§4.14) responds to round 23's three attacks on three fronts: against (iii-a), the act-character criterion — the ementa is embedded in the *fundamentação*-authorship process under art. 943 and art. 93, IX CF follows act-character not output-use, with a reductio showing the output-use criterion would govern votos under arts. 926–927; against (iii-b), actor-level separation — the constitutive account for obligation (b) (citing court) and the accuracy structure for obligation (a) (cited court) operate at structurally distinct actor levels, demonstrated by the elevation-error fourth case where court B satisfies §1º, V by correctly invoking court A's ementa even while court A's ementa inaccurately characterizes the underlying votos; against (iii-c), acórdão internal consistency — art. 93, IX CF's "decisões... serão fundamentadas" covers the acórdão as a decision-document; ementa-voto internal inconsistency constitutes a *fundamentação* defect regardless of individual voto adequacy. Round 25 adversarial response accepts (iv-b): the actor-level separation substantially resolves the (iii-b) tension; the accuracy dimension at obligation (a)'s level does not infect the constitutive framing at obligation (b)'s level; the elevation-error demonstration is correct; (iii-b) is withdrawn as a live structural charge. Round 25 presses (iv-a) and (iv-c). (iv-a) Against act-character (location-in-process ≠ function-type): the act-character criterion confirms that coverage tracks the character of the authorship act, not the downstream use of its output — but this does not establish that the ementa-authorship act's character places it within art. 93, IX CF's functional domain rather than arts. 926–927's; the *relatório* parallel, settled from round 20 and never withdrawn, forecloses the location-in-process inference: the *relatório* is authored by the relator as a formal acórdão component under art. 943, embedded in the same authorship process, yet art. 93, IX CF does not govern it; if location-in-process within the art. 943 authorship process were sufficient for art. 93, IX CF coverage the *relatório* would be covered; it is not; therefore location-in-process is insufficient for functional-domain assignment; the functional-differentiation framework (round 20) requires a function-type argument distinguishing the ementa-authorship act from the *relatório*-authorship act on grounds internal to functional-domain assignment — the r24 reductio establishes act-character as the correct criterion but does not supply the function-type argument showing the ementa-authorship function falls within art. 93, IX CF's reasoning-expression domain. (iv-c) Against acórdão internal-consistency nullity: the r24 claim requires doctrinal grounding not supplied — STF precedent or authoritative Brazilian procedural doctrine establishing that art. 93, IX CF nullity attaches to ementa-voto inconsistency as a distinct defect category, separable from and not reducible to voto reasoning-expression failure; an elevation error — ementa designates Q as *ratio* while votos establish P with complete and reviewable reasoning — does not impair the votos' expressed reasoning; the textual observation that "decisões... serão fundamentadas" reaches the acórdão as a unit is correct but does not supply the substantive scope claim that the nullity sanction reaches ementa-voto inconsistency independently of voto reasoning-expression adequacy; absent this doctrinal grounding, art. 93, IX CF's traditional scope — nullity for reasoning-expression failure in the votos — governs, and the simplified (a)/(b) structure without art. 93, IX CF for obligation (a) remains available. Round 25 support response (§4.15): against (iv-a), argues the function-type argument was established across §§4.11–4.14 — the ementa is distinguished from the *relatório* by function-type (case narration vs. per-decision normative output expression), not by location-in-process; the *relatório*'s function-type is narration of external procedural and factual history with no accuracy dimension relative to the court's normative deliberative product; the ementa's per-decision function-type is normative output expression — the court's official characterization of what its deliberation established as the *fundamento determinante* — and characterization accuracy at this level is internal to *fundamentação*'s accountability function; the *relatório* parallel confirms rather than defeats the distinction under the functional-differentiation framework because the accepted criterion is function-type, not location, and the *relatório* is the model case of a relator-authored art. 943 component whose function-type (case narration) places it outside art. 93, IX CF's scope; against (iv-c), accepts the doctrinal grounding gap — neither side has produced primary authority establishing ementa-voto inconsistency as an independent art. 93, IX CF nullity category — while preserving the (a)/(b) two-actor structure through art. 926 caput grounding obligation (a), as the adversarial's own round 22 structure proposed; the residual open question is not whether obligation (a) exists but whether art. 93, IX CF's nullity sanction additionally reaches ementa-designation accuracy beyond art. 926 caput's statutory grounding. Round 26 adversarial response: accepts §4.15's function-type argument as substantially meeting requirement (2) — the case narration / per-decision normative output expression distinction is internal to functional-domain assignment under the accepted functional-differentiation framework, and the *relatório* parallel confirms rather than defeats the distinction; the (iv-a) function-type gap charge is withdrawn. Accepts (iv-c)'s evidentiary wall: neither side has produced primary authority for art. 93, IX CF nullity reaching ementa-voto inconsistency as a distinct defect category. Accepts art. 926 caput as obligation (a)'s statutory grounding, preserving the (a)/(b) structure without requiring art. 93, IX CF for obligation (a). One requirement (1) argument survives: §4.15 characterizes the ementa's per-decision function as "normative output expression" and claims this constitutes "reasoning-expression in art. 93, IX CF's sense" because "characterization accuracy at this level is internal to *fundamentação*'s accountability function." §4.13 established that the ementa-authorship act involves genuine second-order deliberative reasoning — the relator determines from potentially divergent voto rationes which element constitutes the unified *fundamento determinante*, an act with a genuine accuracy dimension that pure indexing does not have; this is accepted. But what is *expressed* in the ementa is the conclusion of that second-order reasoning (the designation: which element was decisive for this decision), not the reasoning process by which that conclusion was reached (why that element rather than another, given the potentially divergent votos). Art. 93, IX CF's "decisões... serão fundamentadas" requires grounds to be articulated and reviewable — its accountability function is served by expression of the reasoning process, not only by statement of the reasoning's output. If the ementa's per-decision act falls within art. 93, IX CF's scope as a reasoning-expression act (§4.15's position), then art. 93, IX CF's expression requirement reaches it: the ementa must express the second-order reasoning, not only state its conclusion. A *fundamentação* act that states a conclusion without articulating the grounds behind it is precisely what art. 93, IX CF's "fundamentadas" requirement prohibits. The question §4.15 leaves open: does "normative output expression" — expressing the conclusion of second-order reasoning — satisfy art. 93, IX CF's expression requirement when the second-order reasoning itself (the deliberative process by which the relator selected the *ratio* from divergent voto rationes) is not expressed in the ementa? If yes, the expression requirement is satisfied by conclusion-expression, which reads "fundamentadas" as satisfied by stated conclusions rather than articulated reasoning — in tension with the provision's accountability purpose. If no, "normative output expression" is not "reasoning-expression" in art. 93, IX CF's sense when what is expressed is a reasoning's conclusion rather than the reasoning process that generated it, and requirement (1) is not met by §4.15's function-type argument alone. Round 27 support response (§4.16) argues in two components. Component 1 (template inapplicability): art. 93, IX CF's conclusion/reasoning distinction operates on a template requiring (i) a stated conclusion and (ii) a separately-expressible reasoning-object that exists but is omitted; the second element is absent at the per-decision ementa level because the second-order collegial deliberation does not produce a discursive text separable from the *fundamento determinante* designation — the designation is both the determination's conclusion and its complete expression at the level available to the per-decision ementa function, so the template does not apply and the conclusion-vs-reasoning-expression distinction cannot be drawn. Component 2 (accountability function): even setting Component 1 aside, art. 93, IX CF's accountability function at this dimension is exhausted by two reviews — (a) was a *fundamento determinante* designated? (b) is the designated element supported by what the votos establish? — both enabled by the designation plus the ementa-votos comparison; requiring the ementa to additionally express the inter-voto deliberative reasoning would produce no additional reviewability, and would generate a redundancy obligation because that reasoning "is already present in the votos and the acórdão taken as a whole." Round 28 adversarial response presses four structural challenges to §4.16 while accepting the framing move — that the requirement (1) question turns on whether a separately-expressible second-order reasoning-object exists at the per-decision ementa level. (v-a) Component 1 self-refutes against §4.13's accepted accuracy dimension: §4.13's characterization of the second-order deliberation as "a genuine reasoning act ... not an indexing operation over pre-labeled items" is accepted since round 22 and load-bearing for §4.15's function-type distinction (which round 26 accepted at requirement (2)); §4.13 grounds that characterization in a genuine accuracy dimension attaching to the relator's determination — the determination can produce elevation errors, mischaracterizing what the votos collectively established as *fundamento determinante*. The presence of an accuracy dimension entails that the reasoning-process (inputs: the divergent voto rationes; assessment: which element is decisive given each voto's grounds; conclusion: the designation) is at least conceptually separable from its output; otherwise there is no fact of the matter against which the designation can be inaccurate. Component 1's claim that the reasoning IS the designation — with no separately-expressible reasoning-object — leaves the elevation-error mechanism without content: the "inaccuracy" becomes an equivocation on the designation itself rather than a mismatch between reasoning-object and designation. Component 1 and the accepted accuracy dimension are mutually exclusive; giving up either takes down a foundation §4.16 needs (giving up Component 1 concedes the template; giving up the accuracy dimension takes down §4.13, and with it §4.15's function-type argument at requirement (2)). (v-b) The redundancy defense concedes the template. Component 1's escape from the redundancy problem is that requiring ementa-level expression of the second-order reasoning "would require the ementa to reproduce, in summary, the inter-voto analysis — which is already present in the votos and the acórdão taken as a whole." Two exhaustive readings, both fatal. First reading: the inter-voto reasoning is present in the votos. Each voto expresses that judge's own reasoning to that judge's own conclusion; the inter-voto reasoning is the relator's second-order determination of which voto element constitutes the collective *fundamento determinante*, an act whose inputs are the votos and whose output is the designation. That determination is exactly what the votos do not express: each voto is the object of the inter-voto reasoning, not its expression. The inter-voto reasoning is not "already present" in the votos; it is present nowhere in the acórdão in elevation-error cases, and that absence is the very defect requirement (1) names. Second reading: accept arguendo that the inter-voto reasoning is somewhere expressed in the acórdão taken as a whole. Then the second-order reasoning-object exists as a separately-expressible discursive text distinct from its conclusion (the designation in the ementa) — which is exactly the paradigm conclusion/reasoning template Component 1 argues is inapplicable; the template applies precisely because the reasoning-object exists and is expressible. Whether art. 93, IX CF then requires the ementa-component to independently carry that expression (as the surrender condition §4.16 flags in (g) frames it) or accepts distributed expression across the acórdão is a further question, but Component 1's template-inapplicability claim fails on either reading of its own redundancy defense. (v-c) Component 1's "the designation IS the complete expression" move generalizes to a defense of conclusory reasoning per se. The move's structure — the conclusion of a reasoning process is asserted to be the expression of that reasoning at the level available to the paradigmatic act — would, applied to the voto-paradigm failure, produce: "the voto's holding is the expression of the voto's reasoning at the level available to the paradigmatic voto function." Art. 93, IX CF's *fundamentadas* requirement forecloses that reading at the paradigmatic voto level; nothing in §4.15's function-type distinction supplies a differentia that would license the move at the ementa level while blocking it at the voto level. If §4.15 successfully brings the per-decision ementa dimension within art. 93, IX CF's scope as a reasoning-expression act (round 26's acceptance), the same *fundamentadas* standard reaches it. Component 1 is not a template-inapplicability claim specific to the ementa's per-decision function; it is a general reformulation of the conclusion/reasoning distinction that would collapse the distinction wherever applied. (v-d) Component 2's reviewability list is under-inclusive. §4.16 enumerates the reviewable questions at this dimension as (a) was a *fundamento determinante* designated? and (b) is the designated element supported by what the votos collectively establish as the ratio? — and concludes that accurate designation enables both without remainder. This omits a third question the acórdão-as-decision-document must answer under a *fundamentadas* standard: was the relator's determination that element X (rather than element Y from a competing voto) is the *fundamento determinante* itself reasoned? Even in the paradigm voto case, reviewability under art. 93, IX CF is not confined to "was a conclusion stated" and "do the premises support it" — it extends to whether the inferential move from premises to conclusion is defensible; a voto whose stated premises admit both a proposition and its negation, absent expressed reasoning selecting one, is *fundamentação*-defective regardless of which of the two conclusions was announced or whether that conclusion is supportable. The second-order determination has this same premises→inference→conclusion structure: divergent voto rationes are the premises; the assessment of which is the collective operative ratio is the inferential move; the designation is the conclusion. Reviewability of the inferential move — the actual second-order reasoning — is exactly what accurate designation plus ementa-votos comparison does not supply: a designation that happens to correspond to an element the votos support does not thereby express the reasoning by which that element was selected over competing candidates. Component 2's exhausted-by-designation account is *fundamentadas*-inadequate on the same criterion §4.13 used to distinguish the ementa from the *relatório* (the second-order determination is a reasoning act with premises, inferences, and a conclusion; that structure is exactly what the *fundamentadas* standard demands be expressed rather than merely concluded). Round 29 supportive response (§4.17) responds to (v-a)–(v-d) with four distinctions. Against (v-a): distinguishes *epistemic separability* (a deliberative fact exists about which voto element the collective deliberation established as *fundamento determinante*, against which the designation can be accurate or inaccurate) from *expressive separability* (a separately-expressible document distinct from the designation exists and is withheld); §4.13's accuracy dimension requires only the former; Component 1 denies only the latter; the two are compatible because a deliberative fact constituted by the votos collectively does not require a separately-expressible text to function as an accuracy ground, and (v-a) conflates the two forms. Against (v-b): both readings of the redundancy defense require the equation "present in the acórdão" = "present as a separately-expressible document distinct from the designation," which Component 1 denies outright; "present" refers to the voto materials as inputs to the relator's determination, not to a withheld second-order reasoning document; neither reading survives once that equation is denied. Against (v-c): the "level available" differential tracks what each act's production process generates — voto-production generates first-order deliberative reasoning available for expression; the ementa's per-decision production process generates only the designation because the second-order determination does not produce a further document; the function-type distinction (§4.15) identifies the differentia in what the production process produces, not only in what is conventionally expressed. Against (v-d): at the per-decision ementa level, "is the designation voto-supported" and "was the inferential move adequate" are co-extensive — the ementa-votos comparison IS the review of the inferential move, because assessing whether the designated element is what the votos collectively establish as *fundamento determinante* is assessing whether the relator's inferential identification was adequate; no class of cases exists at this structural level where the designation is voto-supported but the inferential move was independently defective, because "inferential move was adequate" and "designated element is voto-supported" are the same question at this level. New failure conditions: (h) if the deliberative fact grounding elevation errors cannot function as an accuracy standard without a discursive reasoning act whose product is separately expressible, the epistemic/expressive distinction does not hold in the ementa context; (i) if the relator's second-order determination generates intermediate reasoning structurally available for expression, the production-process differential does not hold; (j) if a class of decisions exists where the designation is voto-supported in the narrow sense while the inferential move was defective, co-extensiveness fails. Round 30 adversarial response (this filing) presses all three failure conditions. Against (h): for the accuracy dimension to be operative — for elevation errors to be genuine errors reviewable by a supervising court — some evaluator must be able to determine what the correct designation should have been; the only path to this determination is through reading and reasoning about the votos, a discursive act whose output — a claim of the form "voto materials collectively establish P as *fundamento determinante*" — is a separately-expressible text; if that discursive product is not produced, the deliberative fact has no operational content as an accuracy standard and the elevation-error mechanism loses its analytical grip; the epistemic/expressive distinction is coherent in contexts where facts exist independently of discursive access, but in the ementa context the deliberative fact is accessible only via the votos-reading act whose intermediate product Component 1 says is not produced; §4.17 owes an account of how a deliberative fact functions as an accuracy standard without any expressive act capable of accessing it, or the distinction is not doing the work assigned to it. Against (i): the "level available" response derives a production-structure claim from the function-type distinction (§4.15) without bridging the gap between them; function-type (what the act accomplishes as its final output) and production-process structure (what intermediate products the act generates in reaching that output) are distinct; §4.15 establishes that the ementa's per-decision act produces normative output expression as its final output, not that the production process generates no intermediate reasoning; the relator's determination necessarily involves deliberative steps — identifying each voto's operative rationale, assessing convergence at the right level of specificity, selecting the collectively operative element — steps structurally available for expression whether or not ementas conventionally include them; conventional omission is not structural incapacity, and the function-type argument cannot supply the production-structure claim without a further premise that §4.17 does not establish. Against (j): the co-extensiveness claim is either empirical or conceptual; if empirical, the case class exists — in fragmented decisions, multiple voto elements are each supported by some subset of votos, so the ementa-votos comparison (is the designated element voto-supported?) is satisfiable by any element appearing as decisive in some votos; the relator who designates the minority-supported element produces a "voto-supported" designation in the narrow sense while the inferential move was defective (the collectively operative element is different); if conceptual, the claim builds inferential-adequacy requirements into the definition of "voto-supported," making co-extensiveness definitionally guaranteed rather than contingently absent of counterexamples; in neither reading does the simple ementa-votos comparison constitute reviewability of the inferential move. Requirement (1) remains open after round 30; requirement (2)'s function-type placement (round-26 accepted) makes the *fundamentadas* standard's application at this dimension unavoidable rather than dispensable, so the burden of showing that conclusion-alone suffices remains on the supportive. Round 31 supportive response (§4.18) responds to r30's three attacks with three responses. Against (h): distinguishes the relator's ementa-production act from the evaluator's retrospective accuracy-assessment act — different agents, timing, and materials (votos as primary source, not a missing ementa-produced intermediate document) — the evaluator's claim is produced from votos-reading in the context of accuracy review, not a document the relator's production process was supposed to have generated; votos-reading accessibility supports epistemic separability without establishing expressive separability; the (h) attack requires equating the evaluator's accuracy-assessment claim with the ementa's omitted production-process output, an equation the two-acts distinction defeats. Against (i): distinguishes between steps occurring and the content those steps generate as their product — for first-order deliberation, the steps generate legal reasoning content distinct from the holding; for second-order identification, the steps are epistemic prerequisites of an identification act whose output is the identification result; the designation expresses this identification; the epistemic process of arriving at the identification does not generate *fundamentação*-bearing content of the type art. 93, IX CF covers, distinct from the designation; the claim is not about conventional omission but about what type of content the production process generates. Against (j): Component 2 was never committed to thin-presence; the collective-support check tests whether the designated element is what the votos collectively establish as *fundamento determinante*, not merely whether it appears in any voto; in the fragmented-voto case (G1: three justices, G2: two, G3: one), G2 designation fails the collective-support check because the votos collectively support G1 as the operative ratio; collective-support is independently evaluable — the evaluator reads the votos and assesses which element the largest group treated as operative — without any intermediate reasoning document the ementa was supposed to produce. New failure conditions: (k) a structural argument establishing the evaluator's act IS structurally equivalent to the ementa's omitted production-process output — that the retrospective reconstruction and the relator's supposed intermediate document are the same type of expressive product; (l) a structural argument establishing the relator's steps generate deliberative products — legal reasoning content distinct from the designation and structurally available for expression independently of the votos — whose expression art. 93, IX CF would require; (m) a case class where the designated element satisfies the collective-support standard AND the relator's inferential move was independently defective — establishing that co-extensiveness fails at the collective-support level rather than only at the thin-presence level. Round 32 adversarial response (this filing) presses all three failure conditions. Against (k) — the two-acts distinction does not defeat structural equivalence at the act-type level: r31 concedes that the evaluator performing the accuracy-assessment act produces a claim of the form "the votos collectively establish P as *fundamento determinante*" — an expressible text; this concession establishes that the act-type of second-order identification from voto materials generates expressible output beyond mere designation; the relator performs the same act-type during ementa production — identifying from potentially divergent voto rationes which element constitutes the unified *fundamento determinante*; if the evaluator's performance of this act-type generates an expressible claim, the relator's performance of the same act-type also generates an expressible claim; the two-acts distinction identifies non-structural differences — timing (production vs. review), agent (relator vs. evaluator), institutional purpose (authorship vs. accuracy assessment) — none of which determines whether an act of a given type generates expressible output; the structural equivalence is at the level of act-type: both relator and evaluator perform second-order identification from voto materials, and acts of the same type generate outputs of the same type; r31's concession that the evaluator's performance generates an expressible text is self-refuting for Component 1 — if the act-type generates expressible output in the evaluator's performance, the relator's performance of the same act-type also generates expressible output, which is precisely what Component 1's "the designation IS the complete expression" claim denies. Against (l) — the type-of-content claim is stipulative, not established: r31's distinction between "epistemic prerequisites of an identification act" (steps of reading, comparing, selecting) and "*fundamentação*-bearing deliberative products of the type art. 93, IX CF covers" asserts without argument that the former do not generate the latter; when a collegial court's justices disagree on the operative rationale — one invoking proportionality, another procedural due process — the relator's determination that proportionality (rather than due process) is the collectively operative element has propositional content distinct from the designation: "proportionality rather than due process constitutes the *fundamento determinante* because [the convergence pattern of the majority's deliberative commitments shows X]"; this propositional content is the basis for the designation — the "why proportionality and not due process" — not the designation itself; "fundamentadas" in art. 93, IX CF requires the basis for legally operative acts to be expressed, not only the acts themselves; the type-of-content claim suppresses this by asserting that second-order identification generates no basis-content distinct from the identification, but this is a restatement of Component 1's thesis, not an argument that such basis-content does not exist. Against (m) — the conditionality case class satisfies collective-support while the inferential move is defective: the collective-support check assesses which element the votos collectively support as *fundamento determinante* by asking which element the most justices treat as their operative ratio; this check fails in cases where the majority-supported element is conditionally deployed — suppose G1 (proportionality) is invoked by three justices, all of whom explicitly condition their proportionality finding on G2 (constitutional right) being established ("given that G2 is present, proportionality requires X"), while G2 is independently grounded by two justices; collective-support check: G1 is the element most votos invoke as their operative ratio, so G1 designation passes the check; inferential-move adequacy: the court's *fundamento determinante* is not G1 alone, because G1's supporters treat G2 as G1's necessary premise — the element the decision is establishing as the autonomous rule is G2 (or G2 + conditional G1), and a G1 designation captures the majority invocation while missing the conditionality structure that determines what the court's actual holding establishes; the inferential move is defective despite passing the collective-support check; this case class satisfies condition (m): the designated element passes collective-support (G1 is in the most votos as an explicitly operative element) while the inferential move is independently defective (the conditionality structure makes G2 the autonomous *fundamento determinante*, and G1-alone designation fails to identify it); conditional majority reasoning — where justices condition their independently-stated rationale on a prior finding by another justice — is a structural feature of multi-author collegial decisions, not an empirical claim about specific STF cases, and the case class is constructable from the internal logic of the deliberation alone. R33 (supportive §4.19): three responses against r32’s three attacks — against (k/p), act-type identity is individuated by normative function (constitutive designation vs. epistemic reconstruction), not input-output schema alone; R31’s evaluator-output concession is evidence about the epistemic act-type, not the constitutive one R32 needs it to cover; against (l/q), identification-basis content has the structure of a deliberative census (who invoked which ground; plurality count), not a normative chain from legal premises to conclusions; art. 93, IX CF’s *fundamentadas* requirement targets the latter; the individual votos already supply the normative chains the provision reaches; against (m/r), two independent responses: the autonomous-support reading (conditional G1 invocations do not establish G1 as autonomous *fundamento determinante*; G2 with two-justice autonomous support is the correct designation) and the within-voto-expressed-conditionality argument (Brazilian STF practice produces explicit conditionality within individual votos, making Marks-rule and *Anschlusskontrolle* analogies inapt for their implicit-conditionality settings); new failure conditions (p), (q), (r). R34 (adversarial §4.20, this filing): three responses against r33’s three responses — against (p), the normative-function criterion assumes its conclusion; art. 93, IX CF’s *fundamentadas* requirement targets the epistemic product of reasoning acts (the basis-reasoning grounding why this determination rather than another was reached), not the normative product alone; the verdict analogy confirms: judges’ verdicts are paradigmatically constitutive acts yet art. 93, IX CF reaches their reasoning basis; against (q), a deliberative census identifying the *fundamento determinante* is legally operative content with binding precedential force under arts. 926—927 CPC; its basis-content — the plurality pattern grounding the operative identification — is legal-justification content the provision covers because it determines what future courts are bound to apply; against (r), both responses require cross-voto synthesis: detecting G1’s conditionality is within-voto, but identifying G2 as the autonomous *fundamento determinante* requires reading across two justices’ separate G2-grounding votos; the within-voto-expressed-conditionality argument eliminates inter-voto synthesis about conditionality itself but does not eliminate the cross-voto step needed to establish G2’s autonomous collective support; new failure conditions (s), (t), (u). R35 (supportive §4.20) responds to all three — against (p/s): structural separability correctly locates art. 93, IX CF's reach at acts whose epistemic products are structurally separable from the normative output; the verdict's reasoning is structurally separable (logically independent of the finding); the ratio-designation's "epistemic product" — the collective-support fact grounding why G2 rather than G1 — is in the votos, not in a generated document between the votos and the designation; the identification process reads the votos and outputs the designation without generating a third document; the verdict analogy confirms the provision reaches separable content, not that it reaches any epistemic process of any constitutive act; against (q/t): legal operativity converts downstream effects, not internal justificatory form — the census's content type is deliberative-accounting (which element received autonomous collective support); the binding effects are supplied by arts. 926–927's operation applied to the designation result, not by the census's inherent normative status; against (r/u): the ementa-votos comparison constitutively IS multi-voto reading — reading J4's and J5's G2-grounding votos to confirm their independence and unconditionality is the collective-support check for the conditionality case class, not a step beyond it; no intermediate document is generated between the multi-voto reading and the designation; R35 explicitly names the live residual (u): whether confirming G2's autonomous support requires content beyond what the individual votos supply; new failure conditions (v)–(x) named. R36 adversarial response (§4.21, this filing) presses all three — against (s/v): R35's structural-separability criterion conflates premise localization with reasoning-chain expressibility; the verdict's reasoning chain is also built on premises expressed in prior trial documents yet art. 93, IX CF still reaches it; the correct criterion tracks whether the reasoning chain from premises to conclusion is independently expressible, not whether the content is confined to prior documents; the ratio-designation's chain — "G2 rather than G1 is the *fundamento determinante* because J4 and J5 independently and unconditionally grounded G2 making it the autonomous ratio" — is independently expressible from both its premises (individual votos) and its conclusion (the designation); R35's own "Falsified if:" condition confirms the criterion: R36 argues that chain exists and is expressible; against (t/w): R35 addresses a claim R34 never made; R34 never argued "legal operativity converts justificatory form" — R34 argued the census IS the justificatory basis of the legal determination itself; the *fundamento determinante* does not exist before the designation — it comes into existence through the designation act, so the designation's basis IS the legal determination's justificatory basis; R35's claim that "the binding effects come from arts. 926–927's operation applied to the census result" equally describes the verdict case yet the provision still reaches verdict reasoning; the justificatory-form/effects distinction, applied consistently, would exempt verdict reasoning from the provision's reach; against (u/x): the ementa-votos comparison identity suppresses the criterion-application step; individual votos do not assert "J4 and J5 together constitute sufficient autonomous collective support for G2"; applying the threshold criterion — what counts as sufficient autonomous collective support — to the deliberative record produces content that is not in J4's voto, not in J5's voto, and not in the designation, precisely the intermediate-document content R35's own failure condition (u) named; R35 identified (u) as the residual; R36 argues condition (u) is satisfied; new failure conditions (v), (w), (x) named. Requirement (1) remains open after round 36; requirement (2)'s function-type placement (round-26 accepted) makes the *fundamentadas* standard's application at this dimension unavoidable rather than dispensable, so the burden of showing that conclusion-alone suffices remains on the supportive.

This attack does not challenge:

- The value of Phase 2 intra-cluster ranking as a domain-specific quality
  assessment tool, even if residual within-cluster non-transitivity remains.
- The structured rubric design (C1–C5) or the LLM panel methodology
  (following Verga et al., 2024), which are independently motivated.
- The calibration protocol (Section 5.4).
- The paper's intellectual honesty in presenting ESHTR as a position paper
  with falsifiable predictions.
- The mechanism account of non-transitivity itself. The Tversky (1969, 1977)
  grounding is accepted as the best available explanation. The attack is on the
  operationalization and aggregation design, not on the mechanism.
- The conceptual claim that C1-C5 targets domain-general reasoning method.
  This is accepted. The attack is that the acceptance generates a dilemma for
  Phase 3, and that the mechanism's implications for within-cluster
  criterion-activation are inconsistent with the Bradley-Terry aggregation
  defense's requirements.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the following
conditions.

1. **Triple-level within-cluster homogeneity confirmed**: If experiments show
   that within-cluster triples produce cycle incidence statistically
   indistinguishable from that expected under a single stable criterion, the
   within-cluster attack falls. This requires measuring the distribution of
   non-transitive triples and testing whether cycles are concentrated at
   within-cluster quality-dimension boundaries or uniformly distributed.

2. **Mechanism sub-predictions confirmed with structure**: If the experiment
   shows (a) structured cycles concentrated in triples with maximal inter-pair
   semantic distance, (b) directionally predictable cycles across cluster pairs,
   and (c) an asymmetric gradient across cluster-pair semantic distances — and
   if these patterns hold with within-cluster residual non-transitivity controlled
   — the proxy is functioning with sufficient precision for the design goal.

3. **Phase 3 tractability confirmed by empirical evidence**: The Phase 3 attack
   holds unless evidence shows that Phase 3 comparisons under the contextual-
   generalizability instruction exhibit substantially lower non-transitivity rates
   than uncontrolled cross-cluster C1-C5 comparisons, while correlating with Phase 2
   quality rankings within each cluster. Additionally, to confirm the mechanism-level
   instruction argument (§4.5 of the defense), the evidence should distinguish
   instruction-specific attenuation from champion-selection effects: Phase 3
   non-transitivity should be lower than what champion-population homogeneity alone
   would predict, indicating that the explicit abstraction instruction contributes
   independently to non-transitivity reduction.

   The calibration protocol in `phase3-coherence-defense.md` §4.6 is the right
   framework for this test. For the evidence to satisfy this surrender condition,
   the calibration protocol requires three specific extensions beyond its current
   design:

   **(a) Independent quality ground truth for the quality-discrimination measurement.**
   The mixed-quality pairs used in the quality-discrimination accuracy test must be
   quality-discrepant on the basis of an independent criterion — expert human
   quality judgments on cross-cluster decisions, not within-cluster Phase 2
   Bradley-Terry rankings — to break the closed loop between Phase 2 and Phase 3
   calibration. If Phase 2 rankings serve as the ground truth for the Phase 3
   calibration test, confirming that Phase 3 agrees with Phase 2 across domain
   boundaries establishes coherence between the two phases, not Phase 3's independent
   quality-discrimination validity.

   **(b) Champion-scale instruction-effect evidence.** The instruction-independence
   test should include actual Phase 3 champion decisions, not only non-champion
   cross-cluster calibration decisions. If Phase 3 instructions produce higher κ on
   non-champion cross-cluster pairs but show no improvement on champion cross-cluster
   pairs, the instruction effect does not transfer to Phase 3's actual comparator
   population, and the mechanism-level argument for instruction-modulated structural
   reading at champion scale is not confirmed.

   **(c) κ threshold referenced to within-cluster reliability.** Cross-cluster κ
   under Phase 3 instructions must approach within-cluster Phase 2 κ levels —
   not merely exceed cross-cluster Phase 2 κ — for the global ranking claim to
   meet a reliability standard comparable to Phase 2's within-domain reliability.
   The claim is that Phase 3 produces a coherent global ranking; a ranking whose
   inter-judge reliability substantially falls below Phase 2's within-domain
   reliability level does not meet the standard that "coherent global ranking"
   implies. Evidence of improvement over the Phase 2 cross-domain baseline is
   necessary but not sufficient.

   **(d) Variance-source decomposition for measurement 2.** The criterion-profile
   variance reduction test requires controlling for pair-specific quality-dimension-
   profile effects to cleanly attribute variance reduction to domain-specific criterion
   suppression rather than to quality-dimension-profile rearrangement under Phase 3
   conditions. Two methods are available. First, construct cross-cluster calibration
   pairs that are quality-dimension-profile-matched: pairs where the two domain
   decisions have been assessed (via Phase 2 per-criterion scores or expert judgment)
   to have similar overall quality-dimension profiles, so that within-pair criterion-
   profile differences under Phase 2 conditions are primarily attributable to domain-
   specific mapping rather than to quality-dimension-profile differences. For such
   pairs, the variance reduction signal from Phase 3 instructions is cleaner: any
   remaining within-pair criterion-profile variance after profile-matching is more
   confidently attributable to domain-specific effects. Second, specify the expected
   pattern of results across measurements 1, 2, and 3 jointly for each competing
   hypothesis — structural-reading mode, circularity, and pair-specific quality-
   dimension-profile dominance after domain-mapping suppression — prior to data
   collection. Without this pre-specification, moderate variance reduction combined
   with improved κ and quality-discrimination accuracy is consistent with multiple
   hypotheses and the protocol cannot adjudicate among them.

   **(e) Cross-elaboration extension under prong 2 of the C2 disjunction.** If
   SC6(c) yields prong 2 — within-cluster C2 variance is not systematically
   wider than C1/C4 variance because elaboration richness is co-compressed by
   clustering — the within-cluster cross-elaboration concern relocates to Phase 3.
   Under this outcome, between-champion elaboration richness differences in Phase 3
   arise from cluster-level adversarial record heterogeneity rather than from
   domain-vocabulary differences. The Phase 3 abstraction instruction specifies
   what to evaluate (reasoning method quality) but does not specify whether
   reasoning method quality is assessed independently of elaboration richness
   generated by adversarial record differences. A champion from a cluster dominated
   by high-adversarial-record cases has elaborate reasoning because demanding
   arguments were available; a champion from a low-adversarial-record cluster has
   elaborate reasoning because the judge applied analytical care against undemanding
   arguments. The Phase 3 instruction does not distinguish these two sources of
   elaboration richness. To satisfy SC6(3) under prong 2, the Phase 3 calibration
   evidence must include a cross-elaboration test — whether LLM judges applying
   the abstraction instruction assign rankings independent of between-champion
   elaboration richness differences arising from cluster-level adversarial record
   variation, not only from domain-vocabulary differences. This cross-elaboration
   test is a distinct empirical requirement from the cross-domain κ measurement
   SC6(3) currently specifies; both are required if SC6(c) yields prong 2.

   The proposed cross-elaboration methodology (supportive round 6) requires
   independent expert assessment of reasoning-operation quality that is "in principle
   separable from elaboration level generated by adversarial record richness." As
   argued in §3.2 (seventh adversarial response), this condition is not
   operationalized in the proposed methodology. For the cross-elaboration test to
   satisfy SC6(3)(e), the expert-assessment protocol must specify a
   complexity-relative quality standard — quality assessed relative to what the
   reasoning operation must accomplish given the case's adversarial record difficulty
   — and must establish inter-rater reliability on that standard across matched-domain
   champions from different adversarial record contexts. Without this
   operationalization, the test cannot distinguish between LLM judges tracking quality
   that experts assessed as higher under a genuine complexity-relative standard and
   LLM judges tracking elaboration that experts assessed as higher under an implicit
   universal scale where more elaborately structured reasoning operations score better
   regardless of what the case demanded. Both outcomes would produce the same pattern
   of LLM agreement with expert rankings; only the operationalized complexity-relative
   standard with established inter-rater reliability can distinguish them.

   **(f) Differential inter-rater reliability across the full calibration pipeline.**
   The supportive round 9 response proposes three distinct annotation steps that
   introduce adversarial-record sensitivity: (1) SC6(b-1)-ID calibration annotation,
   where annotators identify the material argument set from raw brief content for cases
   with dispositifs of varying determinacy; (2) C1 reference-answer construction; (3) C2
   reference-answer construction. Round 10's ementa-as-authoritative-ratio move addresses
   annotation source complexity for step (2): annotators read the cited precedent's ementa
   rather than synthesizing across votos, removing collegial fragmentation as the primary
   source of inter-rater disagreement for C1. The court-stated-theory constraint reduces
   the hard-case class for step (1). These are genuine advances. For this surrender
   condition to be met, two residual concerns require resolution. First, arm-specific
   inter-rater reliability for C1 reference-answer construction must be reported separately
   for high-adversarial-record and low-adversarial-record cases after the ementa-as-ratio
   source reduction — specifically to determine whether ementa-interpretation ambiguity
   (principle-level abstraction in contested constitutional decisions) generates arm-specific
   disagreement on which specific doctrinal construction was the fundamento determinante,
   replacing but not eliminating the voto-synthesis disagreement the ementa-as-ratio move
   addresses. Second, arm-specific inter-rater reliability for SC6(b-1)-ID calibration
   annotation must be reported separately across arms — the court-stated-theory constraint
   narrows the hard-case class for quality-filter decisions but leaves ementa-theory
   generality as a residual for the contested constitutional class. Pooled reliability
   across both steps can obscure arm-specific deficits that the round 10 advances reduce
   but do not eliminate. Third, arm-specific implicit-structure flagging rates must be
   reported: if ementas listing grounds without explicit logical connectives are
   concentrated in the contested-constitutional arm at substantially higher rates than
   in the routine arm, the mandatory-flagging solution converts annotation tractability
   into an operational-capacity dependency at champion scale, and the arm-specific
   flagging rate is the empirical quantity that determines whether the solution is
   tractable in the evaluation target's distribution. Fourth, arm-specific combined
   type (b) case rate and implicit-structure flagging rate must be reported jointly
   from a pre-calibration pilot. Round 12 accepts the type (b) shared-infrastructure
   framing and the posture-type stripping step, but whether the contested-constitutional
   arm concentrates cases with both type (b) complexity and implicit-structure flags at
   operationally significant rates is an open empirical question. Cases simultaneously
   requiring expert-calibrated type (b) annotation and implicit-structure unpacking
   represent the maximum annotation-cost class; if this joint class is concentrated in
   the arm where annotation tractability is most disputed, the cumulative burden may
   exceed what reference-answer construction can address without substantially expanded
   expert infrastructure. The pre-calibration pilot data should report this joint class
   size directly.

   Fifth, the annotation task at step 2 must be confirmed as tractable at the ementa's
   characterization level without requiring the annotator to cross the specificity gap
   to the doctrinal-specific level. Round 13's step-1/step-2 distinction correctly
   identifies the ementa as the step-2 source document for C1 annotation. It does not
   address whether the annotation task — comparing the citing court's doctrinal-specific
   characterization against the ementa's abstract-principle characterization — can be
   performed tractably within the ementa's characterization level, or requires
   determining what the ementa's abstract statement implies at the specific doctrinal
   level where the citing court operates. The latter requires principle-to-application
   assessment whose difficulty is concentrated in the high-adversarial-record arm where
   doctrinal-specific characterizations are most contested. Arm-specific IRR for C1
   annotation must report whether annotator disagreements concentrate at the
   cross-specificity comparison step — specifically in cases where the citing court's
   construction is neither obviously within nor obviously outside the abstract principle's
   established scope — and whether this concentration is systematically higher in the
   high-adversarial-record arm than in the routine arm. Uniform cross-arm agreement on
   C1 annotation after the ementa-as-ratio source reduction would confirm that the
   step-2 task is tractable at the ementa's characterization level; arm-specifically
   lower agreement in the high-adversarial-record arm would confirm that the step-2
   task requires principle-to-application assessment that the source-reduction move
   does not eliminate.

   **(g) C3 operationalization distinguishes legally mandated verbatim text from
   formulaic reasoning avoidance.** Round 10's mandatory-text preprocessing proposal
   (official-database corpus stripping legally-mandated text before phrase frequency
   computation) advances toward this condition. The condition is satisfied for the
   categories covered by official databases: constitutional and statutory provision text,
   formally enacted STF/STJ súmulas, and standard statutory formulas from Portal da
   Legislação and Diário Oficial. For these categories, the preprocessing provides a
   tractable solution that does not require legal content analysis.
   
   For this surrender condition to be fully met, the preprocessing must additionally
   address residual categories that official databases do not cover. Round 10 identified
   two such categories: (i) court-specific procedural formulas from the STF and STJ
   Regimento Interno (mandatory within those courts' procedural practice but not in
   Portal da Legislação or Diário Oficial), and (ii) institutionally conventional
   formulas that have become uniform through appellate practice without statutory or
   Regimento mandate (standard dispositif language, voto opening/closing structures,
   citation-style templates). Round 11's cross-cluster-convention stripping step —
   identifying phrases appearing across three or more unrelated doctrinal clusters as
   institutional-convention candidates — addresses both categories and is accepted as
   satisfying the surrender condition for them. The condition is now met for three
   categories: universally-mandated text (official-database preprocessing), and
   court-universally-conventional and Regimento Interno formulas (cross-cluster-
   convention stripping).

   Round 12's posture-type stripping step — identifying phrases appearing in greater
   than ninety percent of decisions of each procedural type across doctrinal clusters
   — addresses this residual category directly. The step's scope criterion
   (procedural-type-specific universality across doctrinal subjects) matches the
   structural description of the residual: phrases that are universal within a
   procedural posture but not cross-cluster. This surrender condition is now met for
   four categories: universally-mandated text (official-database preprocessing),
   court-universally-conventional and Regimento Interno formulas (cross-cluster-
   convention stripping), and procedural-type-specific institutional formulas
   (posture-type stripping). Full satisfaction is subject to implementation validation
   confirming that the ninety-percent threshold correctly separates institutional-
   procedural formulas from doctrinal reasoning in practice — whether the threshold
   calibration is robust across different procedural types and doctrinal domains in
   the STF corpus remains an empirical question for the ESHTR experimental protocol.

4. **Restricted scope claim**: If ESHTR is reinterpreted as producing only
   within-cluster quality rankings (not a global ranking), the Phase 3 attack is
   moot. This requires retracting or qualifying the Abstract's claim that Phase 3
   "surfaces globally exceptional decisions."

5. **Within-cluster cycles confirmed to be unstructured**: If the ESHTR
   experiment implements Prediction 4 — measuring within-cluster cycle incidence
   as a function of quality-dimension asymmetry profiles across items — and shows
   that cycles are uniformly distributed rather than concentrated at quality-dimension
   asymmetry boundaries, the item-level criterion activation argument falls. This
   finding would support the non-systematic assumption and validate the Bradley-Terry
   aggregation defense. The test requires measuring per-item quality-dimension scores
   alongside cycle incidence in the experimental protocol — a specific addition to
   the ESHTR protocol's current design (§5.5, §6) that it does not currently output.

6. **C2 operationalization validated against adversarial record confound.** If the ESHTR
   §5.4 calibration protocol is extended to include: (a) two types of calibration
   examples for C2 ranking — Type 1: pairwise examples where a brief-but-adequate
   disposal of a weak argument ranks above an inadequate disposal of the same weak
   argument despite similar or greater text length in the inadequate version, training
   LLM judges to discriminate conduct quality within the adequacy range for individual
   arguments; and Type 2: pairings where a decision covering all material arguments
   briefly (complete-but-thin) outranks a decision covering some arguments elaborately
   while ignoring others (selective-but-elaborate), constructed from the case record of
   arguments raised by counsel, evaluated with the case record provided as part of the
   LLM judge's input alongside the decision text; (b) empirical evidence showing that
   LLM judges calibrated under this extended protocol (i) assign C2 scores independent
   of adversarial record elaboration richness across a range of argument strength levels,
   *at the ranking level*, and (ii) track coverage completeness independently of text
   volume or per-argument elaboration depth when evaluating naturalistic decisions where
   coverage breadth and total text length co-vary in the standard positive direction —
   not only in the artificially reversed Type 2 calibration pairs where the
   complete-but-thin decision is shorter; and
   (c) per-item C1, C2, and C4 dimension scores within fine-grained semantic clusters,
   showing that within-cluster C2 variance is not systematically wider than C1/C4
   variance; and
   (d) SC6(a) Type 2 calibration examples constructed with (decision text + party brief)
   input demonstrating that LLM judges correctly identify the set of material arguments
   from the raw party brief — not only correctly rank coverage completeness once the
   material argument set is pre-specified in the calibration pair. In the realistic
   evaluation condition, the LLM receives (decision text + party brief) and must perform
   argument materiality identification under art. 489, §1º, IV's "capable of affecting
   the outcome" standard before coverage ranking. Calibration examples that pre-specify
   which brief arguments are material test the coverage ranking task but not the
   identification task. Both must be validated to confirm that coverage-completeness
   tracking under the proposed input-extension protocol functions reliably at evaluation
   time; and
   (e) SC6(b-1) anti-naturalistic calibration pairs must be extended to include
   argument-level materiality-identification tests from raw brief content: pairs where
   the LLM receives a party brief with no pre-specified material set and must identify
   which arguments satisfy the art. 489, §1º, IV materiality threshold before coverage
   ranking. SC6(b-1)'s current anti-naturalistic structure tests the downstream coverage-
   ranking step given an implicit pre-specification embedded in pair construction; it
   does not validate that the LLM correctly performs the upstream materiality-
   identification step in the realistic evaluation condition where no pre-specification
   is provided —
   then the C2 operationalization concern and the within-cluster C2 independence claim
   are both addressable from a single data collection. Evidence of within-cluster
   C1/C2/C4 co-variation at levels comparable to between-cluster co-variation would
   undermine the adversarial C2-specific mechanism and simultaneously confirm that
   embedding proximity compresses elaboration variance alongside doctrinal variance —
   the fourth supportive response's implicit prediction. Evidence of within-cluster C2
   variation independent of C1/C4 would confirm the adversarial mechanism and
   disconfirm the fourth response. Both hypotheses are tested by the same data
   collection; neither requires a new experimental design beyond what SC5 already
   specifies with the addition of per-criterion dimension scores. This surrender
   condition is partially overlapping with SC5: both require per-item dimension score
   data collected alongside Bradley-Terry rankings; the difference is that SC5 tests
   for non-systematic within-cluster cycling overall, while SC6 tests for C2-specific
   profile dynamics that generate systematic within-cluster criterion activation.

7. **Ementa confirmed as constitutive authority for art. 489, §1º, V compliance assessment, without an available restricted evidential trigger.**
   The V/VI textual economy inference (round 15) settles the designative/conceptual-coverage
   question: V's *identificar* is purely designative, and the annotation task is text-to-text
   comparison at the ementa's characterization level — does the citing court's statement
   invoke what the ementa identifies as the cited precedent's fundamentos determinantes?
   The surviving issue is whether the ementa's characterization is constitutive or evidential
   for this comparison. The attack at the C1 annotation front falls in whole if: (a) primary
   Brazilian procedural authority — a superior court decision or authoritative doctrinal
   treatment — establishes that *seus fundamentos determinantes* in Art. 489, §1º, V refers
   to the ementa-characterized fundamentos determinantes as the operative reference for
   compliance purposes, such that a citing court that invokes what the ementa identifies as
   ratio has satisfied C1 regardless of whether the ementa's characterization accurately
   reflects the underlying deliberation's actual load-bearing grounds; OR (b) the institutional-
   allocation argument is shown to be non-circular — that the distinction between cited court
   self-documentation obligation and citing court compliance obligation is derivable from the
   constitutive account's own structure rather than presupposing the evidential account's
   institutional-responsibility characterization. Meeting path (b) now requires addressing
   the round 18 statutory-grounding challenge and the round 19 scope-narrowing counter-argument
   together. Round 18 support response identified CPC art. 943 and art. 93, IX CF as the
   independent statutory basis for obligation (a): the ementa is authored by the relator as a
   formal acórdão component, and art. 93, IX CF applies to the ementa accordingly; an elevation
   error is an internal fundamentação inconsistency within the acórdão. Round 19 accepts art. 943
   and art. 93, IX CF's application while contesting the scope of the fundamentação requirement:
   the provision mandates presence and expression of reasoning in the votos (the decision must
   not be arbitrary; the grounds must be stated), not accuracy of the ementa's characterization
   of which element of the expressed reasoning was the ratio. Under this scope reading, the votos'
   expressed reasoning remains intact in an elevation-error case, the decision is fundamentada,
   and the ementa error is a headnote accuracy problem outside art. 93, IX CF's scope. Round 20
   concedes the "heading/body" vocabulary and supplies the functional-differentiation argument as
   the positive argument for asymmetric art. 93, IX CF scope. The core move is the relatório
   counterexample: Brazilian doctrine does not hold that art. 93, IX CF requires the relatório —
   a relator-authored formal acórdão component under art. 943 — to be fundamentada in the same
   constitutional sense as the votos. Art. 943 identifies three main relator-authored formal
   acórdão components (relatório, votos, ementa) serving distinct constitutional functions:
   the votos bear the reasoning-expression function; the relatório serves factual summarization;
   the ementa serves citation indexing. If the supportive's argument were correct that all
   relator-authored formal acórdão components are covered by "fundamentadas" in the same
   constitutional sense, the relatório would be subject to the same fundamentação requirement —
   an implication not maintained in doctrine. Scope tracks the reasoning-expression function,
   not formal component membership. Round 20 also rejects the accountability conflation:
   art. 93, IX CF's accountability function (reasoning-presence reviewability through the votos)
   and the ementa's accountability function (arts. 926-927 citation-coherence) are distinct
   mechanisms governed by distinct provisions; the constitutive account's (a)/(b) structure
   requires these to be governed by different statutory schemes, so grounding obligation (a) in
   art. 93, IX CF collapses the structural separation the constitutive account requires. Path (b)
   therefore now requires the supportive to show either: (i) that the ementa's citation-indexing
   function specifically makes it a bearer of the reasoning-expression obligation in a way the
   relatório's factual-summary function does not — a functional differentiation within art. 943
   components that favors the ementa specifically over the relatório — such that art. 93, IX CF's
   "fundamentadas" reaches ementa-characterization accuracy while leaving the relatório's
   factual accuracy outside the same scope; or (ii) that a different provision independently
   grounds ementa-characterization accuracy without passing through art. 93, IX CF's scope
   question. Round 20 support response took path (i) with the ratio-constitutive function
   criterion: the ementa's ratio-constitutive function — its role as the court's authoritative
   *ratio* characterization for arts. 926–927 citation compliance purposes — distinguishes it
   from the *relatório* by bearing an authoritative relationship to the court's *ratio*
   determination that the *relatório*'s factual-summary function does not bear; and the (a)/(b)
   structure is maintained as a two-actor, two-provision arrangement. Round 21 adversarial
   response contests the ratio-constitutive function criterion on three grounds. (i-a) Criterion
   misapplication: the functional-differentiation framework places components inside the provision
   that governs their function; the ratio-constitutive function is by definition a precedent-
   coherence function governed by arts. 926–927 — that is what makes it ratio-constitutive;
   correctly applying the criterion places the ementa inside arts. 926–927's scope (which the
   constitutive account has always asserted), but leaves open why this same function also triggers
   art. 93, IX CF, which governs reasoning-expression, not precedent-coherence. (i-b) Redundancy
   challenge: art. 926 caput (*'Os tribunais devem uniformizar sua jurisprudência e mantê-la
   estável, íntegra e coerente'*) independently grounds the cited court's obligation to produce
   accurate ementas as a coherence and integrity requirement; an individual ementa that
   mischaracterizes the *ratio* of its decision introduces incoherence into the court's published
   jurisprudential output at the level of the specific publication event, directly violating
   art. 926 caput; with art. 926 caput grounding obligation (a) and arts. 926–927's compliance
   framework grounding obligation (b), the two-provision structure is satisfied and art. 93, IX CF
   is structurally dispensable for obligation (a). (i-c) Normative double-counting: the supportive
   r20 grounds the ementa's ratio-constitutive obligation simultaneously in art. 93, IX CF
   (obligation a) and arts. 926–927 (obligation b); these provisions have different constitutional
   authority (art. 93, IX CF as a CF Title IV fundamental rights guarantee; arts. 926–927 as CPC
   statutory provisions), different enforcement mechanisms (art. 93, IX CF's nullity sanction;
   arts. 926–927's compliance and recalibration framework), and different scope; double-grounding
   the ratio-constitutive obligation in both provisions creates normative incoherence without a
   theory of how they interact. Round 21 supportive response (§4.12): the ementa's ratio-
   constitutive function has two analytically distinct dimensions — per-decision (the court's
   official characterization of what its reasoning determined as *ratio*, asserted to constitute a
   reasoning-expression act under art. 93, IX CF: accurately characterizing the reasoning's
   normative output is internal to *fundamentação*'s accountability function because a court whose
   ementa mischaracterizes what its votos determined as *fundamento determinante* has produced a
   *fundamentação* defect in the art. 93, IX CF sense) and cross-decision (the citation reference
   function governed by arts. 926–927); the functional-differentiation framework tracks both
   dimensions separately without requiring mutual exclusivity; art. 926 caput's scope is systemic
   (the *jurisprudência* as a corpus across decisions over time, with prospective-modification
   enforcement under art. 926 §4) rather than per-decision ementa characterization accuracy,
   and even if art. 926 caput reaches individual ementas it does so through the systemic-
   coherence dimension rather than the per-decision reasoning-adequacy dimension art. 93, IX CF
   governs; no normative double-counting because art. 93, IX CF governs one actor (cited court)
   for the per-decision dimension while arts. 926–927 govern a different actor (citing court) for
   the cross-decision dimension — different actors, different analytical domains, different
   enforcement mechanisms; the (a)/(b) two-actor, two-provision structure is itself the theory of
   articulation, with each provision governing non-overlapping actor-obligation pairs. Round 22
   adversarial response: the per-decision/cross-decision two-dimension analysis does not establish
   art. 93, IX CF as the governing provision for the per-decision dimension. (ii-a) Designation
   versus expression: the per-decision dimension — stating which element of expressed reasoning was
   the *fundamento determinante* — is a designation act, not a reasoning-expression act; the votos
   express the reasoning; the ementa designates which already-expressed element was decisive;
   art. 93, IX CF governs expression (decisions must be *fundamentadas*: reasoning must be present,
   stated, and reviewable), not designation; an elevation error — ementa designates Q as *ratio*
   while votos established P — does not impair the accountability function art. 93, IX CF serves,
   because the expressed reasoning remains fully accessible through the votos; the elevation error
   is a ratio-coherence failure within arts. 926–927's domain, not a reasoning-expression failure
   within art. 93, IX CF's domain; the functional-differentiation criterion (scope tracks function)
   places designation within arts. 926–927's precedent-coherence scope regardless of whether the
   designation operates at the per-decision or cross-decision analytical level — both dimensions of
   the ratio-constitutive function are precedent-coherence functions; the *relatório*'s settled
   non-*fundamentação*-bearing treatment confirms that per-decision characterization does not
   automatically generate art. 93, IX CF coverage — the *relatório*'s narration of which facts are
   procedurally relevant is also a per-decision characterization act and is not *fundamentação*-
   bearing, which shows that analytical level (per-decision) does not determine provision scope.
   (ii-b) Art. 926 caput per-event integrity scope: 'Mantê-la íntegra' (maintain it integral) in
   art. 926 caput reaches per-ementa accuracy; the *íntegra* requirement targets internal
   consistency — an ementa inconsistent with the votos of its own decision is an integrity failure
   at the individual decision level; the systemic-integrity obligation presupposes and entails per-
   decision accuracy as a structural prerequisite, because a court cannot maintain an *íntegra
   jurisprudência* while publishing ementas that mischaracterize its decisions' rationes; the
   prospective-modification enforcement mechanism (art. 926 §4) addresses the systemic-departure
   dimension and does not define or exhaust art. 926 caput's substantive scope; art. 926 caput's
   per-event integrity requirement independently grounds obligation (a) within arts. 926–927's
   framework, and the (a)/(b) two-actor structure is preserved without art. 93, IX CF — obligation
   (a): cited court's ementa-accuracy obligation, grounded in art. 926 caput; obligation (b):
   citing court's citation compliance, governed by arts. 926–927's compliance framework. Round 24
   supportive response (§4.14) responds to round 23's three attacks: the act-character criterion
   against (iii-a); actor-level separation against (iii-b); and acórdão internal-consistency
   nullity against (iii-c). Round 25 adversarial response accepts the actor-level separation
   (iv-b) and presses (iv-a) against act-character and (iv-c) against the internal-consistency
   nullity. Round 25 adversarial response accepted (iv-b) and pressed (iv-a) on the function-type
   gap and (iv-c) on the internal-consistency nullity. Round 26 adversarial response (this filing)
   accepts §4.15's function-type argument as meeting requirement (2) and accepts (iv-c)'s
   evidentiary wall with art. 926 caput as obligation (a)'s statutory grounding. Path (b) now
   additionally requires the supportive to show all of the following:
   (1) that the per-decision dimension of the ratio-constitutive function constitutes reasoning-
   expression in art. 93, IX CF's sense — specifically, that the ementa's per-decision normative
   output (§4.15's accepted function-type) expresses the second-order deliberative reasoning rather
   than merely stating its conclusion. Round 27 support response (§4.16) offers two components.
   Component 1 (template inapplicability): art. 93, IX CF's conclusion/reasoning distinction
   operates on a template requiring (i) a stated conclusion and (ii) a separately-expressible
   reasoning-object omitted alongside it; the second element is absent at the per-decision ementa
   level because the second-order collegial deliberation does not produce a discursive text
   separable from the *fundamento determinante* designation — the designation is both the
   determination's conclusion and its complete expression at the level available to this function.
   Component 2 (accountability function): the reviewability art. 93, IX CF requires at this
   dimension is exhausted by (a) was a *fundamento determinante* designated? and (b) is the
   designated element supported by what the votos collectively establish? — both enabled by
   accurate designation plus ementa-votos comparison; requiring additional inter-voto
   deliberative-reasoning expression would add no reviewability and would generate a redundancy
   obligation because the reasoning is "already present in the votos and the acórdão taken as a
   whole." Round 28 adversarial response contests both. Against Component 1: §4.13's accepted
   accuracy dimension — invoked by both sides and load-bearing for §4.15's function-type
   distinction that round 26 accepted at requirement (2) — presupposes the very separability
   Component 1 denies. The elevation-error mechanism that §4.13 uses to distinguish the ementa
   from the *relatório* requires the second-order reasoning-process (inputs: divergent voto
   rationes; assessment: which is decisive; output: the designation) to be conceptually distinct
   from its designation-output, or there is nothing for the designation to be inaccurate about.
   Component 1's redundancy defense either denies its own premise (if the inter-voto reasoning is
   in fact not present in the votos, because each voto expresses its own reasoning to its own
   conclusion and the second-order determination is nowhere expressed in the acórdão) or concedes
   the template's applicability (if the reasoning is somewhere expressed as a separately-expressible
   discursive text distinct from the designation, that is the paradigm conclusion/reasoning
   template — the template applies precisely because a reasoning-object exists and is expressible).
   Component 1's "the designation IS the complete expression" move, generalized, defeats
   voto-paradigm failure by the same structure ("the voto's holding is the expression of its
   reasoning at the level available"), which art. 93, IX CF's *fundamentadas* forecloses; §4.15's
   function-type distinction supplies no differentia that blocks the move at the voto level while
   licensing it at the ementa level. Against Component 2: reviewability under art. 93, IX CF is
   not confined to (a) "was a conclusion stated" and (b) "do the premises support it" — it extends
   to the inferential move from premises to conclusion; the second-order determination has that
   same premises→inference→conclusion structure (divergent voto rationes → assessment → designation),
   and reviewability of the inferential move is exactly what accurate designation plus ementa-votos
   comparison does not supply. Component 2's exhausted-by-designation account is
   *fundamentadas*-inadequate on the same criterion §4.13 used to distinguish the ementa from the
   *relatório* — the second-order determination is a reasoning act with premises, inferences, and
   a conclusion, and that structure is exactly what the *fundamentadas* standard demands be
   expressed rather than merely concluded. Requirement (1) remains the live remaining requirement
   after round 34. Round 31 supportive (§4.18) responded to r30's three attacks — (h), (i), (j) —
   with three responses (the two-acts distinction, the type-of-content claim, and the collective-
   support reading) and named new failure conditions (k)–(m). Round 32 adversarial (§4.19, this
   filing) presses all three: (k) the two-acts distinction identifies non-structural differences
   (timing, agent, institutional purpose) that do not determine whether an act-type generates
   expressible output; both the relator and the evaluator perform second-order identification from
   voto materials, and r31's own concession that the evaluator's performance generates an expressible
   claim establishes that the act-type generates expressible output — refuting Component 1's "the
   designation IS the complete expression" thesis at the level of act-type equivalence; (l) the
   type-of-content claim is stipulative — when votos diverge on the operative rationale, the
   relator's selection of one rationale over another has propositional basis-content distinct from
   the designation (the "why X and not Y" content that constitutes the basis for the designation),
   which is of the type art. 93, IX CF's *fundamentadas* requirement demands be expressed rather
   than only stated as conclusion; (m) the conditionality case class — where the majority-supported
   element G1 is invoked only conditionally (given G2), with G2 independently grounded by a
   minority — passes the collective-support check (G1 is in the most votos as an explicitly
   operative element) while the inferential move is defective (G2 is the autonomous *fundamento
   determinante* that G1-alone designation fails to identify); this case class satisfies condition
   (m) at the collective-support level, not only at the thin-presence level that r30's earlier
   fragmented-voto attack pressed; Round 33 supportive response (§4.19) responds to r32’s three attacks. Against (k): act-type identity is individuated by normative function, not input-output schema — the relator’s designation act is constitutive (it creates the authoritative ratio) while the evaluator’s reconstruction act is epistemic (it assesses whether the created ratio tracks the votos); their outputs differ in normative kind even when they share input materials and output format; institutional role is constitutive of act-type identity in the normative practice, not merely contextual; R32 stripped out institutional role and retained only the input-output schema, but this yields the wrong individuating criterion for Component 1’s expressive-separability analysis; R31’s concession that the evaluator produces an expressible claim establishes that an epistemic-reconstruction act generates such output, not that a constitutive-designation act generates an analogous intermediate document; new failure condition (p): a structural argument establishing that act-type identity is correctly individuated by input-material structure and output format alone, with institutional role merely contextual. Against (l): identification-basis content has the structure of a deliberative census — who invoked which ground and in what plurality — not a normative chain from legal premises to legal conclusions; art. 93, IX CF’s *fundamentadas* requirement covers the second type, not the first; a deliberative census describes the procedural record rather than articulating a legal argument; the individual justices’ votos already supply the normative chains the provision reaches; new failure condition (q): a structural argument establishing that deliberative-accounting content (who said what, plurality result) constitutes legal-justification content of the type the provision covers. Against (m): two independent responses, each sufficient — (first) the collective-support reading tracks which element the votos collectively establish as the AUTONOMOUS *fundamento determinante*; conditional G1 invocations do not establish G1 as an autonomous ratio: the three G1 justices treat G2 as G1’s necessary premise; G1 has no autonomous invocations; the element with autonomous deliberative support (G2, independently grounded by two justices without conditionality) is what the collective-support check designates; (second) Brazilian STF practice generates within-voto-expressed conditionality: each G1-invoking justice explicitly states the conditionality within their own voto, making the conditional structure detectable from within-voto reading without inter-voto synthesis; the Marks rule and *Anschlusskontrolle* analogies apply to settings where conditionality is implicit because justices do not write individual votos with explicitly stated reasoning — Brazilian STF practice is institutionally different; new failure condition (r): a structural argument establishing that the collective-support reading correctly counts conditional invocations as full deliberative support AND that Brazilian STF practice generates implicit (within-voto unexpressed) conditionality at a frequency making within-voto reading insufficient to identify the autonomous *fundamento determinante*. Round 34 adversarial response (§4.20, this filing) presses all three failure conditions. Against (k/p): R33’s normative-function criterion assumes its conclusion. The criterion correctly identifies that constitutive acts and epistemic acts have normative products that differ in kind — the designation constitutes the ratio; the accuracy claim does not. But art. 93, IX CF’s *fundamentadas* requirement is not about the normative product of an act; it targets the epistemic product of reasoning acts — the basis-reasoning grounding why this determination rather than another was reached — regardless of what normative function the act serves. Both act-types have both a normative product and an epistemic product. The constitutive act’s normative product is the designation (which constitutes the ratio); its epistemic product is the basis-reasoning grounding why G1 rather than G2 was designated. Art. 93, IX CF’s accountability function reaches the epistemic product. R33 imports the conclusion by defining the constitutive act as one whose output IS only the normative product (the designation), which is precisely Component 1’s claim that is at issue — it cannot serve as the criterion that resolves whether Component 1 is correct. The verdict-analogy R33 offers confirms the adversarial’s position: judges’ verdicts are paradigmatically constitutive acts (they create the legal finding), yet art. 93, IX CF’s *fundamentadas* requirement reaches the reasoning basis behind them; the constitutive character of the verdict’s normative product does not exempt its epistemic product from the *fundamentadas* standard. Against (l/q): the deliberative census is legally operative content under the Brazilian precedential system, not mere procedural aggregation. The fact that "the plurality of the court invoked G1 as the operative premise" is a legal finding with binding precedential force under arts. 926–927 — it is the determination that arts. 926–927’s compliance framework enforces against citing courts. The deliberative census is the evidentiary basis for the legal determination "X is the court’s *fundamento determinante*." That determination is legally operative; its basis must be expressed for it to be *fundamentada*. R33’s distinction between the deliberative census (outside the provision’s scope) and normative chains (within scope) presupposes that the census is a sociological observation rather than the legal-justification basis for the precedentially operative determination. But the *fundamento determinante* identification IS the legally operative act of the court’s deliberation — what creates the binding precedent; the deliberative census that grounds it is the basis-content the provision requires to be expressed for the determination to satisfy *fundamentadas*. Against (m/r): both of R33’s responses require inter-voto synthesis, defeating Component 2’s claim that the accountability function is satisfied without it. Against the autonomous-support reading: to identify G2 as the autonomous *fundamento determinante* from the conditionality case class, the ementa-votos comparison must connect J1–J3’s within-voto-expressed condition ("given G2...") to J4–J5’s within-voto-expressed autonomous G2 grounding — specifically, it must determine that G2’s autonomous grounding by J4–J5 completes G1’s conditional structure and thereby makes G2 the autonomous ratio. Detecting J1–J3’s conditionality is within-voto readable (R33 is correct on this point). But the completion determination — connecting J1’s "given G2" to J4’s "G2 is established" — is a cross-voto synthesis step not within-voto readable from any individual justice’s voto. The autonomous-support reading enriches Component 2 with a condition not present in its original formulation AND self-defeats by requiring the cross-voto synthesis it claimed to eliminate. Against the within-voto-expressed-conditionality response: the within-voto response defeats the document-production failure implicit in the Marks/*Anschlusskontrolle* analogy (those analogies apply to implicit conditionality; Brazilian STF practice expresses conditionality explicitly within individual votos). But this defeats only the premise that conditionality detection requires a separate inter-voto document — it does not defeat the autonomous ratio identification requirement. Even with explicit within-voto conditionality, identifying WHICH element is the autonomous *fundamento determinante* requires a cross-voto step: after reading each G1-invoking justice’s explicit conditionality, the ementa-votos comparison must still determine that G2’s independent grounding by J4–J5 renders G2 the autonomous ratio — a determination not within-voto completable from any individual justice’s voto but requiring synthesis across votos. The within-voto response eliminates the document-production failure but not the synthesis requirement. New failure conditions: (s) a structural argument establishing that the normative-function criterion correctly determines what art. 93, IX CF’s *fundamentadas* requirement reaches — specifically, that the provision’s accountability function is directed at normative products rather than at epistemic products (basis-reasoning) of reasoning acts, such that a constitutive act’s epistemic basis-reasoning falls outside the provision’s scope — would defeat (p); (t) a structural argument establishing that the deliberative census constituting the relator’s identification basis is not legal-justification content of the type the provision covers even when it is the evidentiary basis for a legally operative determination with binding precedential force under arts. 926–927 — would defeat (q); (u) a structural argument establishing that the autonomous ratio identification from within-voto-expressed conditionality (connecting conditional invocations in some votos with autonomous groundings in other votos to identify which element has autonomous support) does not require cross-voto synthesis, or that this synthesis step is itself within-voto completable without reading across different justices’ votos — would defeat (r). R35 (supportive §4.20) responds to all three: against (p/s), structural separability correctly captures that art. 93, IX CF reaches epistemic products structurally independent of the normative output — the verdict's reasoning is structurally independent of the finding; the ratio-designation's "epistemic product" is the collective-support fact in the votos, not in a generated intermediate document; the identification process does not produce a third document between the votos and the designation; against (q/t), legal operativity converts downstream effects, not internal justificatory form — the census's content type is deliberative-accounting and the binding effects are supplied by arts. 926–927's operation applied to the result; against (r/u), the ementa-votos comparison constitutively IS multi-voto reading — confirming J4's and J5's independence and unconditionality is the collective-support check for the conditionality case class, not a step beyond it; R35 names the live residual (u): whether confirming G2's autonomous support requires content beyond the individual votos. R36 adversarial response (§4.21, this filing) presses all three: against (s/v), R35's structural-separability criterion conflates premise localization with reasoning-chain expressibility; verdicts' reasoning chains are built on premises in prior documents yet the provision reaches them; the correct criterion is whether the reasoning chain from premises to conclusion is independently expressible; the ratio-designation's chain ("G2 because J4–J5 independently and unconditionally ground G2 making it the autonomous *fundamento determinante*") is independently expressible from both its premises and its conclusion; against (t/w), R35 addresses a claim R34 never made — R34 argued the census IS the justificatory basis of the legal determination itself, not that operativity converts form; the *fundamento determinante* comes into existence through the designation act, so the designation's basis IS the legal determination's justificatory basis; R35's "arts. 926–927's operation explains the binding force" equally describes verdicts yet the provision still reaches verdict reasoning; the justificatory-form/effects distinction, applied consistently, would exempt verdict reasoning; against (u/x), the ementa-votos comparison identity suppresses the criterion-application step — individual votos do not assert "J4 and J5 together constitute sufficient autonomous collective support for G2"; applying the threshold criterion to the deliberative record produces content not in J4's voto, not in J5's voto, and not in the designation — precisely the intermediate content R35's own failure condition (u) named; new failure conditions: (v) a structural argument establishing that structural separability is correctly operationalized as "generates a reasoning chain from premises to conclusion independently expressible from both the premises and the conclusion" — under this criterion the ratio-designation's chain is independently expressible and the verdict analogy applies at the structural-separability level — would defeat (s); (w) a structural argument establishing that the designation act's basis IS the normative grounding of the *fundamento determinante* determination — because the *fundamento determinante* comes into existence through the designation, its basis-reasoning is necessarily the normative basis of the legally operative determination — such that R35's justificatory-form/effects distinction does not hold at this act-type level — would defeat (t); (x) a structural argument establishing that the threshold criterion "two independent unconditional invocations constitute sufficient autonomous collective support" is content expressed in each individual voto separately — specifically, that a justice's assertion of unconditional G2 support is ipso facto an assertion that autonomous collective support is satisfied, so that each voto individually carries the collective-sufficiency claim and no criterion-application step generates intermediate content distinct from the individual votos — would defeat (u). (2) a function-type argument —
   not merely a location-in-process argument — showing that the ementa-authorship act's function
   falls within art. 93, IX CF's reasoning-expression domain rather than arts. 926–927's citation-
   coherence domain, accounting for the *relatório* parallel; this requirement is substantially met
   by round-26-accepted §4.15: the ementa performs per-decision normative output expression; the
   *relatório* performs case narration of external procedural and factual history; the distinction
   is internal to functional-domain assignment under the round-20 accepted functional-
   differentiation framework; (3) that the accuracy structure's implicit evidential presuppositions
   are coherent with the constitutive account maintained for §1º, V compliance purposes, or that
   the two accounts operate at structurally distinct levels — this requirement is met by the
   round-25-and-26-accepted actor-level separation (obligation (a) at the cited court level,
   obligation (b) at the citing court level, no contamination); and (4) doctrinal grounding for
   acórdão-level internal-consistency nullity — this requirement faces an evidentiary wall
   acknowledged by both sides as of round 26: neither side can supply STF precedent or
   authoritative doctrine establishing art. 93, IX CF nullity for ementa-voto inconsistency as
   a category distinct from voto reasoning-expression failure; round-26-accepted fallback:
   obligation (a) is grounded in art. 926 caput's per-event integrity requirement (statutory
   level) rather than art. 93, IX CF's constitutional nullity sanction; this narrows obligation
   (a)'s force (statutory rather than constitutional basis) while preserving the (a)/(b) two-
   actor structure; the simplified structure — obligation (a) in art. 926 caput, obligation (b)
   in arts. 926–927 — without art. 93, IX CF is the adversarial's accepted fallback for the
   constitutional-scope arm, and requirement (1) is the remaining live question. Under
   either path (a) or (b) fully met, the fourth case (ementa elevation error)
   does not generate a C1 annotation failure, and the surviving arm-specific IRR concern
   collapses to ementa-interpretation ambiguity alone (implicit-structure flagging;
   principle-level abstraction in contested constitutional decisions), a narrower and more
   tractable residual. The attack also falls in part if primary authority or institutional
   practice establishes that the restricted evidential trigger (authoritative subsequent
   revision of the cited precedent's ementa characterization) is not available in Brazilian
   precedential practice — i.e., that Brazilian procedural doctrine does not recognize
   subsequent *tese vinculante* revision, *entendimento cancelado* resolution, or superior
   court decisions as triggering a citing court's obligation to engage the revised
   characterization rather than the original ementa. If no such trigger class exists in
   practice, the restricted evidential reading has no practical purchase, and the
   constitutive account covers the entire compliance-assessment domain without exception.
   The attack also falls in part for the correction-revision class if Brazilian procedural
   doctrine treats correction revisions as pure supersession — i.e., if Brazilian practice
   does not distinguish between changed-circumstances revisions and correction revisions in
   terms of what the triggering condition implies about the original ementa's accuracy, such
   that all authoritative revisions are correctly characterized as new constitutive references
   without any presupposition of evidential inaccuracy in the original.
   Absent these paths, the constitutive-versus-evidential question remains open; the fourth
   case licenses the paradigm §1º, V failure under the ementa-anchored designative reading,
   and the annotation task's accuracy profile in the high-adversarial-record arm turns on
   which account is operative.

---

## References

Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking:
A Scalable Method for Evaluating Judicial Decision Quality with LLM Panels.
`embedding_seeded_tournament.md` (this repository).

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
