# Corpus-Groundedness Is Not Semantic Accuracy: The Fidelity Gap in STT's Decoding Guarantee

---

## 1. Thesis Attacked

The paper "Semantic Tokenization Transformers" (Baldo, 2025; STT;
`semantic_tokenization_transformers (1).md`) proposes a decoding mechanism
it describes as "semantically grounded" on the basis that all decoded text
is drawn from real corpus chunks (medoids) rather than generated from model
weights. The paper claims this mechanism achieves "bounded hallucination":

> "By constraining outputs to real text chunks, we aim to eliminate the
> most common source of hallucination — generation from the model's
> interpolation of training data." (§6.1)

And, in §8: "Bounded hallucination under retrieval-grounded decoding, with
a pre-registered ceiling enforced by the protocol of Section 5.3."

The falsifiable prediction (§5.3, step 5) is that the LLM normalization
step introduces a "hallucinated n-gram rate ≤ 1%," operationalized by
measuring the proportion of output n-grams not present in the proto-text
(the medoid concatenation before normalization).

---

## 2. Faithful Reconstruction

The strongest form of the design argument has two components.

**Component 1 — Grounding as hallucination prevention.** Standard LLM
generation hallucination arises from the model interpolating between
training patterns to produce text that was never in the training data.
STT's medoid-based decoding constrains outputs to real corpus chunks,
eliminating this failure mode by construction. Every position in the
decoded sequence corresponds to a real chunk selected from the codebook's
medoid set. The LLM normalization step polishes surface issues — boundary
artifacts, grammar — without generating new factual content, constrained
by explicit prompt instructions ("DO NOT Add new information or facts")
and validated by n-gram recall.

**Component 2 — Teacher-mediated semantic alignment.** The offline codebook
is constructed by embedding training chunks using a powerful teacher model
(e.g., Gemini-Embeddings, E5-Large) and clustering in embedding space via
Residual Vector Quantization. Medoids are the training chunks closest to
each centroid. When the Transformer generates a code sequence at inference
time, the codes correspond to the semantic neighborhoods of the training
data that best match the input context. A code generated for semantic
region X will have medoids that are real corpus examples of content in
region X. The alignment loss (L_ALIGN) reinforces this by training the
Transformer's hidden states to predict the teacher's embedding for the
next chunk, providing gradient signal that steers code generation toward
embedding-space accuracy.

**The validation protocol operationalizes the anti-hallucination claim by:**
measuring n-gram novelty rate between proto-text and normalized output;
measuring semantic similarity between proto-text and final text via cosine
similarity; and setting a pre-registered threshold (≤ 1% novel n-gram
rate). The paper is explicit that the decoding stage is the most uncertain
component and deliberately separates its failure criteria from those of
the encoding stage.

A defense of the anti-hallucination claim advances four responses
(`yesindeed/stt-corpus-scope-defense.md`). First, P4 is a prediction
with a falsified-if clause, not an architectural guarantee: §6.1's
language ("we aim to eliminate," "designed to," "if the pipeline
behaves as designed") and §8's explicit position-paper status establish
that the paper commits to a test, not a guarantee; the adversarial
argument proves the operationalization incomplete, not that the design
fails the test it commits to. Second, STT's primary deployment target
is within-corpus use cases where training and inference distributions
substantially overlap; §6.3's cold start acknowledgment marks
out-of-distribution content generation as a known limitation, not a
design target; for within-corpus inputs, the codebook was built from
the same distribution, so medoid retrieval accuracy is substantially
higher. Third, STT's primary competitive advantage over RAG is the
internalization of retrieval into training — autoregressive
code-sequence modeling of long-range transition patterns across
thousands of semantic positions — which is independent of where
inference-time inputs fall relative to training distribution; the
anti-hallucination comparison with RAG is one component, not the
primary competitive axis. Fourth, the type/token argument overstates
token-level uniqueness in specialized single-jurisdiction legal corpora.
Three categories of case-specific content exhibit high recurrence across
decisions in such corpora: institutional parties (government entities,
regulatory agencies, and repeat-litigant corporations appearing across
hundreds to thousands of decisions from a single court), standardized
legal amounts (monetary values indexed to the *salário mínimo* or fixed
statutory penalty scales recurring across thousands of decisions in the
same jurisdiction), and binding-summary language (STF and STJ súmula
holdings appearing verbatim across the corpus). For code positions
corresponding to these semantic regions, medoid selection frequently
produces token-level-accurate content. The residual token-level gap —
genuinely transaction-specific facts unique to each case — is real and
PTF-detectable, but its scope is corpus-dependent and narrower than the
adversarial universal formulation requires.

---

## 3. The Attack

### 3.1 The Anti-Hallucination Claim Conflates Two Distinct Failure Modes

Hallucination in language model output refers to two structurally different
failure modes that require different remedies:

**(F1) Generation hallucination:** The model generates text — facts,
entities, quotations — that did not appear in the training data, arising
from interpolation between training patterns. An LLM that produces a
non-existent citation is the canonical example.

**(F2) Retrieval hallucination:** The retrieved content is real (it appears
in the corpus) but is semantically incorrect for the intended referent. A
retrieval system returning a biography of the wrong "John Smith" is the
canonical example. The output contains no generated text, yet it
misrepresents the intended content.

STT's medoid-based decoding eliminates F1 by construction: medoids are
real corpus text. The anti-hallucination claim is accurate for F1.

The claim does not extend to F2. A sequence of medoids that are each real
corpus text can collectively misrepresent the intended content if the
selected medoids are drawn from the wrong semantic regions of the corpus.
The medoid for a code centroid is the training corpus chunk closest to
that centroid's embedding — a fixed artifact of the offline codebook
construction. If the input requires expressing semantic content that is
approximated, but not closely represented, in the training corpus, the
medoid for the nearest code centroid may be factually or semantically
incorrect for the intended content.

The validation protocol detects only F1. The n-gram novelty check
(§3.3.4, §5.3) compares the LLM-normalized output to the proto-text
(medoid concatenation). It flags cases where the LLM normalizer added
novel n-grams — F1-type failures at the normalization step. It does not
and cannot detect cases where the proto-text itself contains semantically
incorrect content from wrong medoid retrieval — F2-type failures at the
medoid selection step. An output that is 100% grounded in the medoid
proto-text (zero novel n-grams) is a "clean" output by the proposed
validation, regardless of whether those medoids correctly represent the
intended content.

### 3.2 The Training-Decoding Objective Mismatch

The Transformer is trained by the combined objective:

L = λ_AR · L_AR + λ_MASK · L_MASK + λ_ALIGN · L_ALIGN + λ_COMMIT · L_COMMIT

The dominant term is the autoregressive code prediction loss (L_AR, λ = 0.6):
the model maximizes the probability of the next code given prior codes,
estimated from the training corpus code sequences. The model does not
receive gradient signal from the quality of the text produced by medoid
selection for the predicted codes. The downstream decoding quality —
whether the selected medoids accurately represent the intended content —
is not in the loss. The model learns the conditional distribution
P(code_t | code_{<t}) over the training corpus, not a distribution that
maximizes downstream text fidelity.

The alignment loss (L_ALIGN, λ = 0.1) provides a partial bridge: the
model's hidden state at position t is trained to predict the teacher
embedding e_t for the next chunk. If the hidden state accurately predicts
the next embedding, and if the predicted code is the code whose centroid
is closest to that embedding, the model implicitly learns to predict
semantically appropriate codes.

The argument does not close the gap for three reasons.

First, the alignment loss is weighted at 0.1, making it an auxiliary
regularizer rather than a primary training objective. The model is
primarily optimized for code transition probability, not embedding
prediction accuracy. Under distribution shift — inputs that differ from
the training corpus distribution — the code transition priors learned
under L_AR may dominate the alignment signal, producing codes that are
likely under the training distribution but semantically displaced from
the intended content.

Second, even a model with a hidden state that accurately predicts the
teacher embedding for the next chunk cannot guarantee that the predicted
code's medoid faithfully represents that embedding in natural language.
The centroid is the mean of a cluster of training embeddings; the medoid
is the training chunk closest to the centroid. For a novel embedding that
falls near, but not at, a training centroid, the nearest code centroid may
have a medoid that is the best available training-corpus approximation —
but "best available approximation" is not "semantically accurate to the
novel embedding." The alignment loss trains the hidden state to predict
the embedding; the decoding step then quantizes to the nearest code and
retrieves a medoid. These are two separate approximations, and the second
is unconstrained by the training objective.

Third, the alignment loss does not constrain whether the predicted code's
medoid accurately represents the predicted embedding in natural language.
The code is selected as argmin_k ||predicted_embedding − centroid_k||₂.
The centroid is close to the predicted embedding in embedding space. Its
medoid — the real corpus chunk nearest the centroid — covers that embedding
space region with a specific text that happens to be the training corpus's
closest representative. That representative may have the correct structural
form but incorrect specific content for the intended referent.

### 3.3 The Compound Failure Mode for Novel Inputs

The failure modes in §§3.1 and 3.2 compound for inputs whose semantic
content is novel relative to the training corpus. The paper acknowledges
a "cold start problem" (§6.3): "The model cannot easily generate text
about topics entirely absent from the corpus." This acknowledgment is
accurate but understates the structural problem.

Consider a generative task: produce a summary of a document D whose
specific factual content — entities, events, numerical values — is not
represented in the training corpus. The STT pipeline for this task:

1. The input document D is encoded into code sequences. The codes
   represent the document's semantic regions in the training corpus's
   embedding space — the nearest training-corpus semantic neighborhoods
   for each chunk.

2. The Transformer generates code sequences for the summary S. These
   codes are drawn from the training corpus code distribution, optimized
   by L_AR to follow the code transitions typical of the training data.

3. Medoid selection: each summary code retrieves its training corpus
   medoids. These medoids are real corpus text from the semantic
   neighborhood of each code centroid, not from the specific content of D.

4. The Viterbi path selection optimizes coherence among selected medoids,
   producing a proto-text that is internally coherent but grounded in
   training corpus exemplars, not in the novel content of D.

5. The LLM normalizer is constrained: "DO NOT Add new information or
   facts." The normalizer receives a proto-text that is semantically
   adjacent to, but factually displaced from, the intended summary of D.
   The constraint prevents the normalizer from inserting correct facts
   from D into the output.

The result is an output that contains no novel n-grams relative to the
proto-text (passes the validation check), is grounded entirely in real
corpus text (satisfies the anti-hallucination claim as operationalized),
and is semantically incorrect for the specific content of D (F2-type
retrieval hallucination). The validation protocol certifies this output
as hallucination-free while it misrepresents the intended content.

This is not a pathological edge case. For any generative task whose target
content is not closely represented in the training corpus — new entities,
new events, new numerical data processed at inference time — this is the
structural behavior of the system.

The within-corpus defense collapses type-level and token-level
in-distribution membership. A document is type-level within-corpus if it
belongs to the same domain, invokes the same conceptual framework, and
uses the same linguistic conventions as the training corpus. It is
token-level within-corpus only if its specific factual content — the
particular parties, amounts, holdings, events, and numerical values — is
represented in the training data. Medoid retrieval operates at the token
level: the medoid for a code centroid is the specific training corpus
chunk closest to that centroid's embedding, not a domain-type
representative. For every new legal case in a familiar jurisdiction, the
case-specific facts — which parties, what transaction, what precise
holding, what proportionality ratio — are not in the training corpus,
even though the doctrinal framework is. The nearest code centroid's
medoid is a text fragment from a training case that shares the domain and
framework but not the specific facts. The normalization constraint
prevents inserting the actual case-specific facts from the current input.
The decoded output represents the correct domain type while reproducing
the wrong document's specific facts — F2 failure under entirely
within-corpus conditions. Cold start is the extreme case where even
domain-type accuracy fails; the normal within-corpus generative task on
any new document is the case where type-level accuracy is preserved but
token-level factual accuracy is structurally absent.

### 3.4 The Paper's Failure Mode Taxonomy Is Incomplete

The paper's §5.5 lists failure modes including: domain-specific jargon,
numerical precision, code boundary artifacts, and "Rare semantic patterns:
Codes with very few training examples may not be well-represented in the
medoid set." This last item is the closest the paper comes to
acknowledging F2-type retrieval hallucination.

But the framing obscures the structural extent of the problem. "Rare
semantic patterns" characterizes the failure as one of *representational
sparsity* — codes at the periphery of the codebook with few assigned
training chunks. The structural failure is broader: for any semantic
content that is novel relative to the training corpus, the nearest code
centroid's medoid is a training corpus exemplar that approximates but
does not instantiate the novel content. Sparse codes are one route to
this failure; displacement from the training corpus distribution is the
general condition.

The proposed mitigation — "Active learning to add diverse medoids for
rare codes" — addresses sparse codebook coverage but not semantic accuracy.
A denser medoid set for a code centroid provides more candidate texts for
that semantic neighborhood; it does not guarantee that any candidate
accurately represents novel content that falls in that neighborhood.
The type/token argument in §3.3 further establishes that the framing of
"rare semantic patterns" understates the structural extent: the failure
is not confined to the codebook periphery but applies to any new
document's case-specific facts, which are absent from the training corpus
even for well-populated code regions that correctly capture the domain
type.

### 3.5 The Normalizer Constraint Structurally Forecloses F2 Correction

The decoding pipeline's anti-generation-hallucination guarantee is
enforced at the normalization step by an explicit instruction: "DO NOT
Add new information or facts" (§3.3.3). This instruction defines the
normalizer's role as surface-polishing — resolving boundary artifacts,
smoothing grammar — rather than content-generating. It is the
architectural mechanism by which F1-type generation failures are blocked
at the normalization stage.

This same instruction structurally forecloses F2 correction. When the
proto-text contains a medoid that is factually wrong for the intended
content — a salary-minimum multiplier of 10x where the input document D
specifies 8x, a party name drawn from a different institutional litigant
in the training corpus, a súmula formulation whose applicability
conditions do not match the specific case's facts — the normalizer cannot
insert the correct value from D. Inserting "8x" where the proto-text has
"10x" is adding new information not present in the proto-text. The
instruction blocks this regardless of whether the correct value is
available in the normalizer's context.

The supportive defense (`yesindeed/stt-corpus-scope-defense.md`, §3.4)
characterizes the validation gap as a protocol extension problem: "the
blind spot is in the evaluation layer, not in the design layer." This
characterization is incorrect on the design-layer half. The normalizer
instruction is a design decision — not an evaluation setting — and it
creates a structural asymmetry: F2 failures can be detected (by adding
PTF to the evaluation protocol) but cannot be corrected (because the
architecture prevents the normalizer from using D to fix proto-text
errors). Adding PTF to the evaluation would change the epistemic status
of F2 failures from undetected to detected; it would not change their
uncorrectability.

The design choice is internally consistent: a normalizer permitted to
insert facts from D would reintroduce F1 risk at the normalization step —
the risk the instruction is designed to eliminate. The constraint achieves
F1 prevention at the cost of permanent F2 uncorrectability. Once a medoid
is selected incorrectly, the pipeline has no mechanism to detect this
before output (absent PTF) and no mechanism to correct it after detection
(due to the normalizer constraint). F2 errors propagate to output silently
and without a correction pathway within the current design.

This argument is independent of where the input falls relative to the
training distribution. It applies to cold-start inputs (where F2 failure
is near-certain) and to within-corpus inputs with high-recurrence content
(where F2 failure is case-specific but structurally uncorrectable when it
occurs). The recurrence argument reduces the frequency of F2 failures for
particular semantic categories; it does not provide a correction mechanism
for those that occur.

---

## 4. Anticipated Reply and Why It Does Not Suffice

The most developed reply has three components.

**The prediction-not-guarantee reframe.** P4 is a prediction with a
falsified-if clause, not an architectural guarantee; §6.1 and §8 use
conditional language throughout ("we aim to eliminate," "designed to,"
"if the pipeline behaves as designed"). The adversarial argument proves
the operationalization is incomplete, not that the design fails the test
it commits to.

The reframe is accepted on its own terms: the adversarial argument does
not require P4 to be an architectural guarantee. The argument is that a
prediction is only as epistemically specific as its operationalization. P4
is named "bounded hallucination under retrieval-grounded decoding."
Retrieval-grounded decoding includes two stages: medoid selection and LLM
normalization. The §5.3 falsified-if clause — n-gram novelty rate ≤ 1%
between proto-text and normalized output — measures only whether the LLM
normalization stage introduces novel text. It does not and cannot detect
whether the medoid selection stage retrieved semantically incorrect
content. P4's operationalization is not "bounded hallucination" but
"bounded F1-type hallucination at the normalization stage." Under the
current protocol, P4 passes if medoid selection returns semantically wrong
content in every generated chunk, provided the LLM normalizer stays close
to that wrong content. The concession that proto-text fidelity testing
"should be added" identifies the correct extension. Until it is added,
the prediction commits to less than its name implies.

**The within-corpus restriction.** STT's primary deployment target is
within-corpus use cases (legal summarization, biomedical QA) where
training and inference distributions substantially overlap. §6.3's cold
start acknowledgment marks out-of-distribution content generation as a
known limitation, not a design target. For within-corpus inputs, the
codebook was built from the same distribution, so medoid retrieval
accuracy is substantially higher.

The §3.3 type/token analysis establishes why this restriction does not
attenuate F2 failures for normal within-corpus generative tasks. "Within-
corpus" as a deployment condition ensures domain-type accuracy — that the
training distribution covers the conceptual domain, legal framework, and
linguistic conventions of the input. It does not ensure that the specific
token-level factual content of new documents is in the training corpus.
Legal cases in a familiar jurisdiction have specific parties, specific
facts, specific holdings that are not represented by any training case,
even one from the same jurisdiction on the same doctrine. For any
generative summarization or factual QA task on a new document, the output
must reproduce case-specific facts. Medoid retrieval for each code
produces a training corpus fragment from the right domain type but from
a different document's specific content. The normalization constraint
prevents the normalizer from inserting the actual case-specific facts.
F2 failure is structurally present in normal within-corpus deployment —
not only at the cold-start extreme.

The high-stakes application context the paper invokes — §2.4 and §6.4
identify legal and medical domains as primary targets "where factual
accuracy is paramount" — is precisely the context where token-level
factual accuracy about specific new documents is the operative
requirement. For a medical QA system answering questions about new patient
records, or a legal summarization system processing new cases, domain
familiarity does not provide the case-specific factual accuracy that the
anti-hallucination claim implies.

The recurrence counter (`yesindeed/stt-corpus-scope-defense.md`, §3.2)
contests the universality of the type/token argument by identifying three
categories of high-recurrence content in specialized single-jurisdiction
legal corpora: institutional parties, standardized legal amounts, and
binding-summary language. The existence of these categories is accepted —
they are genuine in narrow-jurisdiction corpora and do provide some
token-level coverage. The question is what proportion of the *operative
content* of a legal summary — the content a reader must accurately extract
to act on the decision — comes from high-recurrence categories versus
transaction-specific determinations.

A legal summary's operative content consists of three components that are
predominantly transaction-specific. First, the specific holding on this
dispute: which party prevailed, on what grounds, under which legal
framework as applied to the specific facts of this case. Súmulas state
legal principles and their applicability conditions; they do not specify
the holding on any individual dispute. Second, the factual findings: what
conduct was established, what amounts are at issue, what events the court
found proven. Institutional party names appear as boilerplate; the
specific acts and claims involving those parties are unique to each case.
Third, the remedy: what relief was granted, at what specific amounts and
rates applicable to this plaintiff's situation. Salary-minimum multipliers
establish scales; the specific calculation applied to this employee's
employment period and violations is transaction-specific.

The high-stakes applications that require anti-hallucination protection
are those where operative content matters — not the procedural boilerplate.
A legal practitioner relying on STT's output needs to know who prevailed
and on what grounds, what was awarded, and what conduct the court found
established. Each of these is either transaction-specific or requires
case-specific application of standardized categories that the medoid pool
cannot supply from the input document. The recurrence argument is
strongest for the procedural and doctrinal scaffolding of a summary; it
is weakest for the substantive determinations that give the summary its
value.

The normalizer constraint (§3.5) applies equally to the residual failures
within high-recurrence categories. A medoid that retrieves the correct
institutional party but assigns it the wrong procedural role
(plaintiff/defendant inverted), or retrieves the correct salary-minimum
scale but the wrong multiplier from a different case, is a token-level
inaccuracy that the normalizer cannot correct from D. High-recurrence
categories reduce the frequency of F2 failures; they do not reduce their
uncorrectability.

**The RAG competitive axis.** STT's primary competitive advantage over RAG
is the autoregressive code-sequence Transformer's internalized long-range
modeling — transition patterns across thousands of semantic positions
learned into weights — which is independent of the within-corpus
restriction. Restricting anti-hallucination to within-corpus use cases
does not eliminate the long-context modeling advantage. The earlier framing
of this attack — "if scope is restricted, the claimed advantage over RAG
is reduced" — overstated the case against STT's full competitive profile.

The narrower adversarial position survives: for specifically generative
tasks requiring accurate reproduction of case-specific facts from new
input documents, STT's medoid-based decoding cannot produce case-accurate
outputs for any new document regardless of domain familiarity, while a
RAG system with sufficient context can place the actual input in context
and generate from it. The long-context modeling advantage applies to
structural tasks (sequential coherence, topic flow, argument ordering)
where training-distribution patterns transfer to new documents in the
same domain — not to tasks requiring accurate token-level facts from
specific new documents. The anti-hallucination value proposition for
high-stakes generative applications is diminished by the within-corpus
restriction even if the overall competitive profile is not.

---

## 5. Scope of the Attack

This attack targets the "bounded hallucination" and "semantic fidelity"
claims in STT's generative decoding component (§3.3, §5.3, §6.1, §8).
It does not contest:

- The sequence compression advantage (P1-P2): the compression ratio
  follows from the chunk size and RVQ levels, independent of decoding
  quality, and is genuine.
- The training efficiency advantage (P4): shorter code sequences reduce
  training compute, which is correct given the compression.
- The use of semantic codes as discrete retrieval units (P6): for
  retrieval rather than generation, the F2 failure mode is substantially
  attenuated because the system retrieves known corpus documents, not
  generated content.
- The alignment loss as a theoretically reasonable auxiliary objective.
  The critique is about its weight and the limits of its scope, not its
  presence in the training objective.
- The research direction: combining offline codebook construction,
  code-sequence modeling, and retrieval-based decoding is a legitimate
  proposal. The attack is directed at the anti-hallucination claim
  specifically, not at the approach as a whole.

The attack is conditional on the generative use case. The §3.3 type/token
analysis extends the attack's reach: the F2 failure mode applies not
only to out-of-corpus cold-start inputs but to any within-corpus
generative task requiring accurate reproduction of case-specific facts
from new documents. For retrieval tasks (P6), where the system returns
known corpus documents rather than generating new text, the F2 failure
mode is substantially attenuated by the corpus-relative grounding. The
long-context modeling advantages (P1-P2, P5) are not contested.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the
following conditions.

1. **Within-corpus restriction formally acknowledged, with token-level
   accuracy demonstrated.** If STT's anti-hallucination claim is revised
   to apply only to generative tasks where inference-time content is drawn
   from the same distribution as the training corpus, and the claim is
   presented as a corpus-relative property rather than an architectural
   guarantee, the cold-start component of the F2 failure is out of scope.
   This requires explicitly marking "bounded hallucination" as a deployment
   condition, not a design feature. The full attack is addressed only if
   the within-corpus restriction is additionally accompanied by empirical
   evidence that medoid retrieval produces accurate token-level facts for
   new documents within the target domain — not only type-level domain
   accuracy. The type/token distinction (§3.3) establishes that within-
   corpus domain membership does not guarantee token-level factual
   accuracy for any new document's case-specific content.

2. **Out-of-distribution fidelity demonstrated empirically.** If the
   experimental protocol (§5) is extended to evaluate semantic accuracy
   of decoded outputs on content that diverges from the training corpus
   distribution — measuring whether the generated code sequences'
   medoids faithfully represent the intended output rather than
   approximating it with wrong content — and this test shows high
   semantic fidelity (e.g., high ROUGE-L on summarization of held-out
   documents not in the training corpus), the scope of F2 failures
   is empirically bounded.

3. **Validation protocol extended to test proto-text fidelity, with
   accompanying normalizer modification.** If a second validation step
   is added that tests whether the proto-text (medoid concatenation) is
   semantically accurate to the intended output — not only whether the
   LLM normalizer stayed close to the proto-text — the evaluation's blind
   spot for F2 failures is addressed. Such a test could compare the
   proto-text's embedding to the target embedding, measuring whether the
   medoid retrieval is semantically on-target independent of the LLM
   normalization constraint.

   PTF testing is necessary but not sufficient to address the attack.
   §3.5 establishes that adding PTF to the evaluation layer reveals
   errors that the pipeline's architecture cannot correct: when the
   proto-text's medoids misrepresent the intended content, the
   normalizer's constraint ("DO NOT Add new information or facts")
   prevents correction from the input document even when the accurate
   content is in context. Fully satisfying this surrender condition
   therefore requires either (a) permitting the normalizer to correct
   PTF failures from the input document — revising the normalizer's
   operating mode and P4's falsified-if clause accordingly — or
   (b) demonstrating empirically that PTF failures are sufficiently rare
   in the specific target deployment corpus that the architectural
   constraint has negligible practical consequence. PTF measurement
   alone, without one of these additions, reveals the failure category
   while leaving the output unchanged.

4. **Alignment loss as primary objective with demonstrated downstream
   effect.** If the alignment loss weight is substantially increased and
   it is empirically demonstrated that the model learns to generate code
   sequences whose medoids faithfully represent out-of-distribution target
   content, the training-decoding objective mismatch is empirically closed.

5. **Normalizer redesigned to permit F2 correction from input document.**
   If the normalizer instruction were modified to allow the LLM to correct
   factual errors in the proto-text using information from the input
   document D — with an explicit mechanism distinguishing F1 prevention
   (blocking generation of content ungrounded in any source) from F2
   correction (fixing proto-text errors using D as evidence) — and if
   empirical testing showed that this modification does not reintroduce
   F1-type generation failures at the normalization step, the
   architectural silencer argument would be answered. Such a redesign
   would need to demonstrate that the normalizer can identify proto-text
   factual errors and correct them from D without generating novel content
   ungrounded in D. Under the current normalizer instruction, this
   correction path is closed by design.

---

## References

Baldo, F. S. (2025). Semantic Tokenization Transformers: Pre-training
on High-Level Vector Codes with Semantically Grounded Decoding.
`semantic_tokenization_transformers (1).md` (this repository).

Défossez, A., et al. (2022). High fidelity neural audio compression.
arXiv:2210.13438.

van den Oord, A., Vinyals, O., & Kavukcuoglu, K. (2017). Neural discrete
representation learning. *Advances in Neural Information Processing
Systems*, 30.

Lewis, P., et al. (2020). Retrieval-augmented generation for
knowledge-intensive NLP tasks. *Advances in Neural Information Processing
Systems*, 33, 9459–9474.

Zeghidour, N., et al. (2021). SoundStream: An end-to-end neural audio
codec. *IEEE/ACM Transactions on Audio, Speech, and Language Processing*,
30, 495–507.
