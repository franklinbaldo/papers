# Retrieval Fidelity and the Corpus-Relative Scope of STT's Hallucination Bound

---

## 1. Thesis Supported

Baldo (2025), "Semantic Tokenization Transformers" (STT;
`semantic_tokenization_transformers (1).md`), §6.1, states:

> "By constraining outputs to real text chunks, we aim to eliminate the most
> common source of hallucination — generation from the model's interpolation
> of training data."

And §8 (prediction P4):

> "Bounded hallucination under retrieval-grounded decoding, with a
> pre-registered ceiling enforced by the protocol of Section 5.3."

This paper responds to `otherwise/stt-retrieval-hallucination.md`, which
argues that the anti-hallucination design conflates two structurally distinct
failure modes (F1: generation hallucination; F2: retrieval hallucination), and
that the validation protocol detects only F1, leaving the bounded-hallucination
claim unverified for F2.

---

## 2. What This Support Adds

**Vector:** Direct defense. This paper reconstructs the adversarial argument
faithfully — the F1/F2 distinction is correct and the validation gap is real —
then shows that the attack lands on a stronger version of the claim than STT
makes. The defense has three components: (1) the epistemic status of P4 is
that of a corpus-relative prediction, not an architectural guarantee; (2) the
adversarial RAG comparison fails on the primary competitive axis; (3) the
validation gap is a protocol extension problem, not a design flaw.

---

## 3. The Defense

### 3.1 P4 Is a Corpus-Relative Prediction, Not an Architectural Guarantee

The adversarial paper characterizes "bounded hallucination" as a "design
property" and "architectural guarantee" (otherwise §2), then constructs the
F1/F2 distinction to show the design fails to achieve this guarantee. But P4
is listed in STT's §8 under the heading "The design predicts... that STT
should yield," followed by: "Each of these is stated as a prediction with an
explicit `Falsified if:` clause, not as a result." The §6.1 language
reinforces this: "we aim to eliminate," "is designed to," and — crucially —
"Whether this constraint is preserved through LLM normalization is itself a
question we identify in Section 5.3."

P4's falsified-if clause operationalizes bounded hallucination as: hallucinated
n-gram rate ≤ 1% between proto-text and normalized output (§5.3, step 5). That
operationalization tests only whether the LLM normalization step introduces
novel n-grams — F1-type failures at the normalization stage. The adversarial
paper is correct that it does not test whether the proto-text's medoids
faithfully represent the intended content — F2-type failures at the medoid
selection stage.

The adversarial argument proves that P4's operationalization is incomplete,
not that the design fails the test it commits to. If the §5.3 protocol were
executed and the ≤1% n-gram threshold passed, P4 would not be falsified under
STT's own pre-registered criteria. The question of whether P4 should require a
stronger operationalization is scientifically legitimate — the adversarial
paper's most constructive contribution is its surrender condition 3, which
specifies exactly what the missing test should measure. But showing that a
prediction has an inadequate operationalization is different from showing that
the design fails.

The adversarial paper's strongest version of the claim requires that the paper
presents bounded hallucination as an architectural guarantee independent of any
evaluation. The paper does not do this. Position paper status is not merely a
rhetorical hedge: it commits the paper to the claim that each prediction is
tested, not asserted, and that the claim is only as strong as the pre-registered
test that would confirm or falsify it.

### 3.2 F1 Is the Dominant Failure Mode in the Targeted Deployment Context

STT's §6.1 identifies "generation from the model's interpolation of training
data" as "the most common source of hallucination." The adversarial paper
accepts that medoid-based decoding eliminates F1 by construction, then argues
the targeted failure mode is insufficient because F2 exists. Whether this
argument succeeds depends on whether F2 is actually the dominant failure mode
in STT's deployment context.

The adversarial paper's compound failure scenario (§3.3) is strongest for
inputs whose semantic content is novel relative to the training corpus — where
the model's medoid pool contains no close representative of the intended output.
STT's §6.3 explicitly acknowledges this as the cold start problem: "The model
cannot easily generate text about topics entirely absent from the corpus." That
acknowledgment marks out-of-distribution content generation as a known
limitation, not a design target.

The deployment contexts STT's design most directly serves — legal summarization
from a legal corpus, biomedical QA from a biomedical corpus, long-document
processing within a domain-specific corpus — are within-corpus use cases where
training and inference distributions substantially overlap. The adversarial
paper's §4 concedes this explicitly: "the synthesis of §3.3's compound failure
is strongest for novel inputs; it weakens as the inference-time input
distribution converges on the training distribution." For within-corpus inputs,
the medoid pool was built from the same distribution: the nearest code centroid
for an in-distribution chunk is likely to have a medoid that represents the
correct semantic neighborhood, because both the input and the medoids inhabit
the same trained embedding space.

The adversarial paper's §3.4 criticizes the §5.5 failure mode taxonomy as
framing F2 too narrowly ("rare semantic patterns"). That criticism is accurate —
the F2 problem is broader than representational sparsity. But the paper's §5.5
framing, while incomplete, is consistent with the within-corpus use case: sparse
codes (few training examples per centroid) are the primary source of medoid
selection error in the within-corpus setting where distribution overlap is
assumed. The adversarial paper's generalization (F2 applies to any input that
diverges from the training distribution) is correct; the question is whether the
primary evaluation targets are within-corpus or out-of-distribution generative
tasks. The STT paper's evaluation design (legal corpus, Wikipedia, BookCorpus as
training data; downstream benchmarks using documents from the same or adjacent
corpora) is consistent with a within-corpus experimental scope.

The adversarial paper's §3.3 (updated) sharpens the within-corpus argument by
introducing the type/token distinction. *Type-level* within-corpus membership
means a document's domain, conceptual framework, and linguistic conventions
match the training data. *Token-level* within-corpus membership means the
document's specific factual content — particular parties, amounts, holdings, and
events — is represented in the training corpus. Medoid retrieval, as the
adversarial paper correctly observes, operates at the token level: each code
position's medoid is the specific training chunk closest to that centroid's
embedding. Domain-type accuracy in the embedding space is compatible with
token-level inaccuracy when the nearest medoid comes from a different specific
document.

The adversarial paper's formulation — that in any new legal case in a familiar
jurisdiction, the case-specific facts "are not in the training corpus, even
though the doctrinal framework is" — asserts that token-level facts are uniformly
novel per document. This assertion overstates token-level uniqueness in
specialized legal corpora with narrow jurisdictional scope. Several categories
of case-specific content exhibit high recurrence across documents in such corpora:
institutional parties (government entities, regulatory agencies, and
repeat-litigant corporations that appear across hundreds to thousands of decisions
from a single court), standardized legal amounts (monetary values indexed to the
salário mínimo or fixed statutory penalty scales that recur across thousands of
decisions in the same jurisdiction), and binding-summary language (STF and STJ
súmula holdings whose specific formulations appear verbatim across the corpus).
For code positions whose semantic regions correspond to these recurrent facts,
medoid selection frequently produces token-level-accurate content because the
relevant tokens are densely represented in training data.

The residual token-level gap is real: transaction-specific facts that are
genuinely unique per case — exact monetary amounts in single-occurrence disputes,
parties and events with no prior training-corpus representation — will not be
well-covered by the medoid pool, and F2 failure in the adversarial sense applies
to this category. The scope question is what proportion of the semantic content
in typical specialized legal summaries consists of genuinely novel token-level
facts versus recurrent institutional and doctrinal content. In single-jurisdiction
specialized corpora, this proportion is substantially lower than in general-domain
settings, and substantially lower than the adversarial argument's universal
formulation implies. The deployment context's specific corpus characteristics
determine the practical extent of F2 failure under normal within-corpus
conditions.

### 3.3 The RAG Comparison Does Not Weaken Under Corpus Restriction

The adversarial paper argues (§4) that if STT's anti-hallucination claim is
restricted to within-corpus use cases, "the claimed advantage over standard RAG
is reduced," because RAG also grounds outputs in corpus documents without the
expensive offline codebook construction and Transformer pre-training.

This argument misidentifies STT's primary competitive axis. STT's §6.2 is
explicit: "We do not claim this is strictly better than RAG for all use cases."
The primary competitive claim over RAG is not superior anti-hallucination for
generative tasks, but the internalization of retrieval into the training process,
enabling the code-sequence Transformer to learn long-range sequential structure
over thousands of semantic positions. A RAG system retrieves relevant chunks at
inference time and computes attention over those chunks; it does not encode, in
its learned weights, globally learned code transition patterns from the training
corpus. STT's autoregressive code-sequence Transformer does — and this is the
mechanism behind prediction P5 (long-document QA performance) and the
compression advantages in P1-P4.

Restricting the anti-hallucination claim to within-corpus use cases reduces one
component of the STT-vs-RAG comparison: the claim that STT can generate
hallucination-free content about topics not in a fixed retrieval datastore. It
does not touch the compression and long-context modeling advantages, which are
independent of where the inference-time inputs fall relative to the training
distribution. The adversarial §4.2 conflates the full competitive profile with
the anti-hallucination component, and infers that a limitation on one component
undermines the comparison with RAG as a whole. This inference fails.

### 3.4 The Normalizer Constraint Is an Explicit Design Tradeoff

The adversarial paper's surrender condition 3 specifies the missing test:
a second validation step that measures whether the proto-text (medoid
concatenation) is semantically accurate to the intended output — independently
of whether the LLM normalizer stayed close to the proto-text.

This is a correct characterization of the blind spot, and the test should be
added. The metric would compare the proto-text's embedding to a reference
output's embedding (e.g., the target summary, the original document being
compressed), measuring whether medoid selection produced semantically accurate
proto-text before normalization. Call this proto-text fidelity (PTF).

PTF is implementable within the existing evaluation framework: it requires a
reference output for each evaluated example (already implicit in benchmark
evaluation on NarrativeQA, QuALITY) and an embedding similarity computation
using the teacher model already present in the pipeline. It does not require
redesigning the decoding architecture or the training objective. PTF resolves
the detection gap: it identifies F2 failures before they propagate to output.

The normalizer constraint, however, is not only an evaluation-layer concern.
The "DO NOT Add new information or facts" instruction is a design decision with
a structural consequence: F2 failures are detectable by adding PTF but not
correctable under the current instruction. The adversarial paper is correct on
this point — "the blind spot is in the evaluation layer, not in the design
layer" was incomplete. When the proto-text contains a wrong medoid, inserting
the correct value from D is adding new information not present in the
proto-text, which the instruction blocks regardless of whether D contains the
correct value.

The tradeoff is explicit, not hidden. The same instruction that prevents F1
generation hallucination at the normalization stage forecloses F2 correction at
that same stage. This is internally consistent: a normalizer permitted to insert
facts from D would reintroduce F1 risk at the normalization step — the risk the
instruction is designed to eliminate. The design prioritizes F1 elimination (the
dominant failure mode in the targeted deployment context, per §6.1) at the cost
of F2 uncorrectability within the current instruction.

The remediation is named. Surrender condition 5 specifies the V2 design: a
revised normalizer instruction that permits D-grounded corrections while blocking
ungrounded additions. The current instruction is binary — it cannot distinguish
"insert 8x from D to correct the proto-text's 10x" (D-grounded, correction) from
"generate additional content not in either proto-text or D" (ungrounded,
generation). SC5 requires demonstrating that this distinction can be operationalized
without reintroducing F1 risk. Until that demonstration, the V1 tradeoff stands.

The adversarial paper's "rare but permanently wrong" characterization correctly
describes the V1 design's failure mode: F2 failures that escape PTF detection
(absent PTF) or are detected but uncorrectable (with PTF but without SC5) propagate
to output silently. With SC5 implemented, the risk profile converts from "rare
and uncorrectable" to "rare and correctable." The two arguments are independent
and complementary: §3.2 addresses how often F2 failures occur in high-recurrence
legal corpora; §3.4 addresses what happens when they do and what is required to
enable correction.

The adversarial paper's §3.2 training-decoding objective mismatch provides the
theoretical mechanism for why PTF might fail independently: the alignment loss
(λ=0.1) may be insufficient to close the gap between code transition probability
and downstream text fidelity, especially under distribution shift. This is a
legitimate design concern about the sufficiency of the alignment loss weight.
Whether it is actually insufficient — whether PTF would fail even for within-corpus
inputs — is an empirical question the adversarial paper does not resolve by
theoretical argument alone. The statement that 0.1 is "too weak" requires a claim
about the interaction dynamics between L_AR and L_ALIGN under the specific training
setup, which the adversarial paper approximates via distribution-shift intuition
rather than derivation. Adding PTF to the evaluation protocol would directly answer
whether the mismatch produces actual failures in practice.

---

## 4. Anticipated Objection

The adversarial paper may respond that the position-paper framing and corpus
restriction do not rescue the anti-hallucination claim if STT's value for
high-stakes domains (§6.1: "particularly important for high-stakes domains where
factual accuracy is paramount") requires more than within-corpus reliability.
High-stakes legal or medical applications encounter novel documents, new entities,
and new factual configurations that are not in the training corpus; restricting
the anti-hallucination guarantee to within-corpus scenarios may exclude the cases
that most need it.

This objection is partly correct: within-corpus reliability is necessary but not
sufficient for high-stakes deployment if the relevant documents diverge from the
training distribution. The response is not that STT is guaranteed to handle such
cases — §6.3 acknowledges it cannot. The response is that the cold start problem
is a correctly framed engineering constraint: the system requires a training
corpus representative of the deployment domain. For legal corpora, building a
domain-specific codebook from existing case law and applying it to new cases in
the same jurisdiction and subject matter area is a within-distribution use case
for the medoid pool, even though each new case is a new document.

The adversarial paper's §3.3 (updated) sharpens this objection by introducing
the type/token distinction: domain familiarity ensures type-level accuracy (the
conceptual framework and linguistic conventions are in the training data) but not
token-level accuracy (the specific parties, amounts, and holdings of any new
document may not be represented). This distinction is correct. The response is
not to deny the distinction but to contest its scope in specialized legal corpora.
The adversarial paper's formulation — that case-specific facts "are not in the
training corpus, even though the doctrinal framework is" — treats token-level
uniqueness as a universal property of new documents in a domain, which overstates
uniqueness in single-jurisdiction specialized corpora. Institutional parties,
standardized legal amounts, and binding-summary language recur at high frequency
in such corpora; for these categories, medoid selection produces token-level-
accurate content (§3.2). The residual case for which F2 failure applies in the
adversarial sense — genuinely transaction-specific facts without close training-
corpus representatives — is real and would be identified by PTF testing; but its
scope is narrower than the adversarial paper's universal formulation requires,
and is corpus-specific rather than structurally guaranteed for any new document.

The adversarial paper's updated SC3 requires more than PTF testing: PTF detection
of F2 failures is necessary but not sufficient to satisfy the attack. Fully
addressing SC3 requires either (a) normalizer modification per SC5 — revising the
instruction to permit D-grounded corrections and demonstrating that F1 risk is not
reintroduced — or (b) empirical evidence that PTF failure rates in the specific
deployment corpus are sufficiently low that the architectural constraint has
negligible practical consequence. Both paths are accepted as valid. The current
paper's prior concession that PTF "should be added" acknowledges detection-necessity;
it does not satisfy either (a) or (b) without the additional step each requires.

---

## 5. Scope of This Support

This defense strengthens the bounded hallucination claim within:
- Within-corpus generative and summarization use cases where training and
  inference distributions substantially overlap.
- The epistemic status of P4 as a corpus-relative prediction requiring
  empirical confirmation, not an architectural guarantee.
- The competitive profile of STT vs. RAG, showing the primary advantage
  (long-context modeling) is not diminished by within-corpus restriction.

This defense does NOT contest:
- The F1/F2 structural distinction — it is correct and a genuine contribution.
- The validation gap (missing proto-text fidelity test) — it should be added.
- The adversarial §3.2 concern about alignment loss weight — this is a
  legitimate design question to be resolved empirically.
- The adversarial §3.3 compound failure mode for out-of-distribution inputs —
  these are cold-start scenarios STT's §6.3 already acknowledges as a
  limitation.
- That the "high-stakes domains" framing creates demand for stronger
  guarantees that the current protocol does not provide.
- That the normalizer instruction is a design decision with a structural
  consequence (F2 uncorrectability under V1) — the adversarial paper's §3.5
  is correct on this point.
- That P4's current operationalization tests F1-type failures at the
  normalization stage only; full F2 coverage requires either SC5 implementation
  or empirical negligibility evidence per SC3-b.

---

## 6. Conditions Under Which This Support Would Itself Fail

1. **Out-of-distribution deployment scope established.** If the STT paper's
   primary intended deployment context is shown to include out-of-distribution
   content generation — if the high-stakes applications it targets are not
   within-corpus use cases — the scope argument fails.

2. **Within-corpus PTF failure demonstrated at non-negligible rate.** If proto-text
   fidelity testing shows that even for in-distribution inputs, medoid retrieval
   frequently fails semantically (high PTF error rate), the attenuation argument
   fails. The §3.2 training-decoding mismatch would then produce within-corpus F2
   failures, not only out-of-distribution ones. Under this condition, SC3-b
   (empirical negligibility) would not be satisfied, making SC5 (normalizer
   redesign) necessary for P4's F2 coverage. The adversarial paper's "rare but
   permanently wrong" risk profile would apply at non-negligible frequency, which
   cannot be adequately characterized by the frequency argument alone.

3. **RAG competitive parity on long-context benchmarks.** If RAG with
   sufficiently large retrieval windows performs equivalently to STT on the
   P5-P6 benchmarks (QuALITY, NarrativeQA, BEIR), the competitive advantage
   argument supporting §3.3 weakens: the long-context modeling claim is
   empirically unsupported, and within-corpus restriction then leaves STT
   without a decisive advantage over RAG on any dimension.

4. **Token-level recurrence shown to be low in the specific deployment corpus.**
   The §3.2 argument that F2 failure has narrower scope in specialized legal
   corpora depends on high recurrence rates for institutional parties, standardized
   legal amounts, and binding-summary language. If empirical analysis of the
   deployment corpus shows that a substantial proportion of the semantic content
   required for accurate legal summaries consists of genuinely novel token-level
   facts — parties, amounts, holdings unique to each case with no close training-
   corpus representative — the recurrence argument fails for that corpus, and the
   adversarial type/token analysis applies at the scope the adversarial paper
   claims. The recurrence argument is corpus-dependent and its force varies with
   the jurisdictional and topical narrowness of the specific deployment corpus;
   it does not generalize to multi-jurisdiction or general-domain legal corpora.

---

## References

Baldo, F. S. (2025). Semantic Tokenization Transformers: Pre-training on
High-Level Vector Codes with Semantically Grounded Decoding.
`semantic_tokenization_transformers (1).md` (this repository).

Adversarial paper: `otherwise/stt-retrieval-hallucination.md` (this
repository).

Lewis, P., et al. (2020). Retrieval-augmented generation for
knowledge-intensive NLP tasks. *Advances in Neural Information Processing
Systems*, 33, 9459–9474.
