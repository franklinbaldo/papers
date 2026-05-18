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

---

## 4. Anticipated Reply and Why It Does Not Suffice

The most direct available reply is that STT is not intended primarily as
a generative system for novel content, but as a **long-context modeling
system for content drawn from the training corpus**. In that setting —
a domain-specific corpus where the training data and the inference-time
inputs draw from the same distribution — the medoid retrieval is accurate
because the codebook was built from the same distribution as the input.
For within-corpus use cases (semantic search over a legal corpus,
summarization of documents from a domain the codebook was built on), the
F2 failure mode is substantially attenuated: the medoids were constructed
from the same distribution as the input, so retrieval of wrong content
is less likely.

This reply should be taken seriously. The synthesis of §3.3's compound
failure is strongest for novel inputs; it weakens as the inference-time
input distribution converges on the training distribution.

The reply does not suffice for two reasons.

First, the paper's claims are not restricted to within-corpus use cases.
§8 presents "bounded hallucination under retrieval-grounded decoding" as
a general design property, not a deployment precondition. The evaluation
protocol (§5.1) uses Wikipedia, BookCorpus, Legal corpus, and Code as
training data, and targets downstream tasks (NarrativeQA, QuALITY, BEIR)
that include test content which may not match the training corpus
distribution. Whether the medoids retrieved during evaluation on those
benchmarks accurately represent the test queries is an empirical question
the protocol does not directly address: neither the n-gram novelty metric
(§5.3) nor the semantic similarity metric (between proto-text and
LLM-normalized output) tests semantic accuracy of the proto-text relative
to the intended target.

Second, if the system's utility is restricted to content in or near the
training corpus distribution, the claimed advantage over standard
retrieval-augmented generation is reduced. A RAG system also grounds
outputs in corpus documents without requiring the expensive offline
codebook construction and Transformer pre-training. STT's value proposition
over RAG depends on the generative modeling capability of the code-sequence
Transformer — which is precisely the component whose outputs are at risk
for F2-type failures when the inference-time target diverges from the
training distribution.

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

The attack is conditional on the generative use case. For within-corpus
generative use cases where training and inference distributions are
well-aligned, the F2 failure mode is attenuated.

---

## 6. Surrender Conditions

The attack would not hold, or would hold only partially, under the
following conditions.

1. **Within-corpus restriction formally acknowledged.** If STT's
   anti-hallucination claim is revised to apply only to generative
   tasks where inference-time content is drawn from the same distribution
   as the training corpus, and the claim is presented as a corpus-relative
   property rather than an architectural guarantee, the F2 failure mode
   is out of scope. This requires explicitly marking "bounded hallucination"
   as a deployment condition, not a design feature.

2. **Out-of-distribution fidelity demonstrated empirically.** If the
   experimental protocol (§5) is extended to evaluate semantic accuracy
   of decoded outputs on content that diverges from the training corpus
   distribution — measuring whether the generated code sequences'
   medoids faithfully represent the intended output rather than
   approximating it with wrong content — and this test shows high
   semantic fidelity (e.g., high ROUGE-L on summarization of held-out
   documents not in the training corpus), the scope of F2 failures
   is empirically bounded.

3. **Validation protocol extended to test proto-text fidelity.** If a
   second validation step is added that tests whether the proto-text
   (medoid concatenation) is semantically accurate to the intended output
   — not only whether the LLM normalizer stayed close to the proto-text —
   the evaluation's blind spot for F2 failures is addressed. Such a test
   could compare the proto-text's embedding to the target embedding,
   measuring whether the medoid retrieval is semantically on-target
   independent of the LLM normalization constraint.

4. **Alignment loss as primary objective with demonstrated downstream
   effect.** If the alignment loss weight is substantially increased and
   it is empirically demonstrated that the model learns to generate code
   sequences whose medoids faithfully represent out-of-distribution target
   content, the training-decoding objective mismatch is empirically closed.

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
