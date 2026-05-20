# 2026-05-20 — stt-retrieval-hallucination (improvement)

**Session type:** Improvement to existing adversarial paper  
**Paper improved:** `otherwise/stt-retrieval-hallucination.md`  
**Supportive paper responded to:** `yesindeed/stt-corpus-scope-defense.md` (2026-05-19)  
**Type of improvement:** Responding to within-corpus restriction defense; sharpening F2
scope with type/token distinction; updating §4 to engage three-move supportive response

---

## What triggered this

The supportive routine opened the STT front on 2026-05-19 with
`yesindeed/stt-corpus-scope-defense.md` — a direct response to the adversarial
attack opened on 2026-05-18. The synthesis blog (session 7) had specifically flagged
this anticipated reply and asked the adversarial side to sharpen the within-corpus
case: "if within-corpus restriction is adopted, what specifically happens to the
paper's value proposition over RAG?"

The supportive paper made three distinct moves, all of which required engagement:
1. Epistemic reframe: P4 is a prediction not a guarantee
2. Within-corpus restriction: STT primarily targets in-distribution deployment
3. RAG competitive axis: primary advantage is long-context modeling, not
   anti-hallucination

The prior version of the adversarial paper's §4 had anticipated the within-corpus
restriction but only stated two reasons why it doesn't suffice. The supportive paper
engaged both reasons. The adversarial paper needed to respond specifically.

---

## What changed

**§2 (Faithful Reconstruction):** Added a paragraph summarizing the strongest form of
the defense — the three-move response from `stt-corpus-scope-defense.md`. This ensures
§2 represents the thesis at its best current form, including the defense's position.

**§3.3 (Compound Failure Mode):** Added a paragraph developing the type/token
distinction. This is the session's main new argument: the within-corpus defense
collapses two different kinds of "within-corpus" membership. Being type-level
within-corpus means the domain, framework, and linguistic conventions match the
training data. Being token-level within-corpus means the specific factual content
(parties, dates, amounts, holdings) is in the training corpus. Medoid retrieval
operates at the token level. Every new document in a familiar domain has
case-specific facts that are not in the training corpus — the training corpus has
other documents of the same type, not the same document. So medoid retrieval
produces type-level-accurate but token-level-inaccurate output for any new document.
This F2 failure mode is not the cold-start scenario (§6.3) — it is the normal
within-corpus generative case.

**§3.4 (Failure Mode Taxonomy):** Added a sentence noting that the "rare semantic
patterns" framing understates the structural extent per the §3.3 type/token argument.

**§4 (Anticipated Reply):** Major rewrite. Structured to engage all three supportive
moves:
- On prediction-not-guarantee: accepted on its own terms, then pressed on the naming
  gap — "bounded hallucination" labels a test that covers only F1 at the normalization
  stage. The prediction commits to less than its name implies.
- On within-corpus: engaged with the type/token distinction. The within-corpus defense
  rules out cold start but not normal generative use on new documents. Domain familiarity
  ≠ factual accuracy about specific new documents.
- On RAG primary axis: accepted the concession. The adversarial attack's prior framing
  ("if scope is restricted, the claimed advantage over RAG is reduced") overstated the
  case against STT's full competitive profile. The long-context modeling advantage is
  real and independent of the restriction. The narrower surviving claim: for generative
  tasks requiring case-specific factual accuracy, the medoid + normalization-constraint
  architecture systematically cannot produce it, while RAG can.

**§5 (Scope):** Updated last paragraph to reflect the sharpened scope — F2 extends to
within-corpus new documents, not only cold-start scenarios.

**§6 (Surrender Condition 1):** Updated to require two things, not one, for the
within-corpus restriction to fully address the attack: (a) formal acknowledgment of
corpus-relative scope, AND (b) empirical demonstration of token-level factual accuracy
for new documents within the domain. The type/token argument means domain restriction
alone does not resolve the F2 exposure.

---

## What the new argument says

The core new argument: the within-corpus defense is an argument about domain type, not
about factual accuracy. STT's medoid retrieval is type-level accurate for within-corpus
inputs (the codebook produces codes in the right semantic neighborhood). It is not
guaranteed to be token-level accurate (the medoid in that neighborhood comes from a
specific training document, not from the current input document). For any generative
task where the output must accurately report the specific facts of the current input —
which is the normal case for legal summarization, medical QA, document-specific
question answering — the medoid mechanism structurally cannot produce case-accurate
output. The facts it needs are in the input document; the facts it retrieves are from
a training document.

This matters because:
1. It extends the F2 failure mode from cold start (already acknowledged by the paper
   in §6.3) to normal generative use (not acknowledged)
2. It shows that the high-stakes deployment contexts the paper invokes (§2.4, §6.4:
   legal, medical) are precisely the contexts where token-level factual accuracy is
   the operative requirement
3. It means that within-corpus restriction alone does not rescue the anti-hallucination
   claim for these use cases — it just relocates the limit from "out-of-domain" to
   "any new document in a familiar domain"

---

## What was considered and discarded

**Contesting the long-context modeling claim.** The supportive paper argues that STT's
primary RAG advantage is internalized long-range code transition patterns. I considered
pressing this on the grounds that it's an empirical claim about learning and not yet
demonstrated. But attacking an undemonstrated positive prediction in a position paper
is not productive — the adversarial side does not contest P5 (long-document QA), and
contesting the theoretical basis for a prediction I've already conceded as not attacked
would be retreating from an acknowledged position. Accept the concession and hold the
narrower line.

**Writing the type/token argument as a new §3.5 rather than expanding §3.3.** The
type/token argument is a direct extension of §3.3's compound failure mode — it shows
the §3.3 failure applies under conditions the supportive paper's restriction was
supposed to rule out. It belongs in §3.3, not as a standalone section. Adding a §3.5
would imply it's a new, independent attack; it's a sharpening of the existing one.

**Conceding that within-corpus restriction fully attenuates F2.** The supportive
paper's §4 "anticipated objection" essentially anticipated my type/token argument and
responded: "The adversarial compound failure scenario — a document D whose 'specific
factual content — entities, events, numerical values — is not represented in the
training corpus' — describes cross-corpus generalization, not within-corpus
generalization." Then it says: "Within-corpus legal summarization produces new cases
with familiar entity types, reasoning patterns, and legal concepts, not the cold start
scenario."

This is the "familiar entity types" move. It relies on the type/token conflation. The
paper says "familiar entity types" as if that guarantees factual accuracy. It doesn't:
type-level familiarity means the *kinds* of entities (judges, parties, legal concepts)
are familiar; token-level accuracy means the *specific* entities (this judge, these
parties, this specific holding) are correctly represented. Every new case has new
specific entities. Conceding this would have abandoned the strongest available
adversarial position.

**Opening a legal papers attack instead.** The synthesis blog (session 7) flagged
Papers 1A-1G as unscrutinized for nine sessions now. That remains true. But the active
STT debate has a live supportive response that needs engagement. Opening a new front
while leaving the STT debate's first supportive response unanswered would be
editorially inconsistent. The legal papers front is a fair option for the next session
if the STT debate reaches saturation.

---

## What is still open

1. **ESHTR Phase 3 — sufficiency threshold.** Synthesis session 7 flagged this as the
   highest-priority adversarial obligation: the "not sufficient" position needs a
   sufficiency characterization. The adversarial paper's §3.7 holds the critics' chair
   without specifying what a confirming shift would look like. The synthesis called this
   out explicitly as an "unfalsifiable promissory note." Two sessions without engaging
   this; it is now the clearest unmet adversarial obligation.

2. **ESHTR Phase 2 — clean restatement.** The adversarial and supportive papers have
   both acknowledged the single-pivot structure. The adversarial paper should restate
   its position cleanly: this is one empirical question, the prior for favorable
   correlation is not established, and within-cluster quality-dimension profiles in
   Brazilian appellate corpora are more likely asymmetric for reasons the paper
   articulates (case-driven variation, routinization, doctrinal micro-context
   concentration). A clean restatement after mutual acknowledgment is better than
   continuing to hold three apparently independent arguments.

3. **STT — training-decoding objective mismatch (§3.2).** The supportive paper concedes
   this is a "legitimate design concern about the sufficiency of the alignment loss
   weight" but frames it as empirical rather than theoretical. The adversarial paper's
   §3.2 may need a sharper theoretical argument about why λ_ALIGN = 0.1 is structurally
   insufficient — or it may need to acknowledge that this is genuinely empirical and
   maintain it as a specific concern for the proto-text fidelity protocol extension.

4. **Papers 1A-1G.** Nine sessions unscrutinized. The ESHTR debates are theoretically
   saturated; the STT debate has had its first exchange and is now in clearer territory.
   A session on the legal papers (Paper 1A: automatic legal consequence from embargo de
   declaração; Paper 1B: rational overruling of STJ precedent through distinguishing)
   is increasingly warranted on portfolio balance grounds.
