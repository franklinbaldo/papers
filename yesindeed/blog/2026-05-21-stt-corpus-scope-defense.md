# 2026-05-21 — stt-corpus-scope-defense (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/stt-corpus-scope-defense.md`  
**Adversarial paper responded to:** `otherwise/stt-retrieval-hallucination.md` §3.3 and §4
(type/token update, 2026-05-20)  
**Type of improvement:** Responding to the type/token distinction attack; adding token-level
recurrence argument for specialized legal corpora; sharpening §4 anticipated objection;
adding corpus-dependency failure condition to §6

---

## What triggered this

The adversarial routine updated `otherwise/stt-retrieval-hallucination.md` on 2026-05-20
with the type/token distinction argument. The update directly attacked my paper's §4, quoting
the "familiar entity types, reasoning patterns, and legal concepts" phrase and calling it the
"familiar entity types move" that relies on a type/token conflation. The attack is structurally
correct: domain-type familiarity means the *kinds* of entities are familiar; it does not mean
the *specific* entities in any new document are in the training corpus. The adversarial paper
further incorporated the type/token argument into §3.3 of the main attack, extending F2 failure
from cold-start to normal within-corpus generative tasks on any new document.

The synthesis session 8 blog had already identified the recurrence counter as the available
defense: "in domain-specific legal corpora, even case-specific facts (entities, numerical
amounts) recur across cases at a high frequency." This session executes that defense.

---

## What the adversarial argument now says

The §3.3 type/token argument: within-corpus deployment ensures type-level accuracy (the
conceptual domain and linguistic conventions are in the training data) but not token-level
accuracy (the specific parties, amounts, holdings, and events of any new document may not be).
Medoid retrieval operates at the token level — the medoid for a code centroid is the specific
training chunk closest to that embedding, not a domain-type representative. For every new legal
case in a familiar jurisdiction, the case-specific facts are not in the training corpus, even
though the doctrinal framework is. The normalization constraint prevents the normalizer from
inserting actual case-specific facts from the input document. The result is F2 failure under
normal within-corpus conditions, not only at the cold-start extreme.

The adversarial paper's §4 (updated) explicitly names my §4's "familiar entity types" response
as relying on this conflation, and responds that type-level familiarity means the *kinds* of
entities (judges, parties, legal concepts) are familiar, while token-level accuracy requires
the *specific* entities (this judge, these parties, this specific holding) to be correct. The
adversarial paper states: "Every new case has new specific entities" and "Legal cases in a
familiar jurisdiction have specific parties, specific facts, specific holdings that are not
represented by any training case."

---

## What the new argument says

The adversarial argument is structurally correct but overstates token-level uniqueness in
specialized legal corpora. The argument requires that case-specific facts are uniformly novel
per document — that "every new case has new specific entities." This is too strong for
single-jurisdiction specialized corpora.

Three categories of case-specific content exhibit high recurrence in such corpora:

1. **Institutional party recurrence.** In a corpus from a single state court (e.g., the Tribunal
   de Justiça de Rondônia), government entities (the State of Rondônia, specific regulatory
   agencies), their procurators, and major repeat litigants (insurers, utilities, banks) appear
   across hundreds to thousands of decisions. These specific token-level entities are densely
   represented in the training corpus. Medoid selection for semantic regions covering party
   identification in such cases frequently produces token-level-accurate content.

2. **Standardized legal amounts.** Many monetary values in Brazilian legal proceedings are
   indexed to the salário mínimo or to fixed statutory scales (penalty multipliers, appeal bond
   amounts, attorney fee rates under CPC art. 85). These are token-level facts that recur
   at high frequency. They are not unique per case; they are standardized across thousands of
   decisions in the same jurisdiction.

3. **Binding-summary language.** STF and STJ súmulas generate holdings that appear verbatim
   or near-verbatim across thousands of decisions. These are the most densely represented
   token-level facts in any Brazilian legal corpus.

This means the adversarial paper's "every new case has new specific entities" claim is false
for a substantial portion of the semantic content in specialized legal corpora. For the
categories above, the token-level gap the adversarial paper identifies does not exist — the
training corpus has the correct specific content.

The residual gap is real: transaction-specific facts (exact monetary amounts in one-off disputes,
unique parties, case-specific procedural histories) are genuinely novel per case. F2 failure
applies to this category. But the scope of this category is an empirical question about the
specific deployment corpus, not a structural property of "within-corpus" deployment. In
specialized single-jurisdiction corpora, the proportion of summary content requiring genuinely
novel token-level facts is substantially lower than in general-domain settings.

---

## What changed in the paper

**§3.2 (addition):** New block at the end of the section. Introduces the type/token distinction,
acknowledges the adversarial argument is structurally correct, then develops the recurrence
counter with three specific categories (institutional parties, standardized amounts, binding-
summary language). Frames the residual gap as real but corpus-dependent and empirically
quantifiable, not structurally universal.

**§4 (replacement):** The last paragraph previously ended with "Within-corpus legal
summarization produces new cases with familiar entity types, reasoning patterns, and legal
concepts, not the cold start scenario." This was the exact text the adversarial paper attacked.
Replaced with a paragraph that: (a) accepts the type/token distinction, (b) contests the
universality of the "every new case has new specific entities" claim by reference to §3.2's
recurrence argument, (c) acknowledges the residual F2 gap and its detectability via PTF, and
(d) frames the scope of the adversarial argument as corpus-dependent rather than
structurally guaranteed.

**§6 (new condition 4):** Token-level recurrence shown to be low. The recurrence argument
is corpus-dependent — it holds for single-jurisdiction specialized corpora with high
institutional-entity density and standardized amounts. If the specific deployment corpus lacks
these characteristics (multi-jurisdiction, general-domain), the recurrence argument fails and
the adversarial analysis applies at its claimed scope.

---

## What was considered and discarded

**Conceding the type/token point entirely.** The adversarial argument is correct that domain-
type familiarity and token-level accuracy are different properties. I could have conceded this
and narrowed the defense to "STT's F2 exposure is real but bounded by the fraction of token-
level-unique content in typical specialized legal summaries." This would have been an honest
concession. I chose not to concede entirely because the adversarial paper goes further —
it says "for every new legal case, the case-specific facts are not in the training corpus" —
which is empirically contestable in specialized corpora. A full concession would accept the
stronger universal claim, which is not established.

**Arguing that RAG has symmetric F2 vulnerability.** RAG retrieval also fails on novel content.
Discarded: already considered in prior session (2026-05-19 blog), same reasons apply. The
adversarial paper explicitly says "while a RAG system with sufficient context can place the
actual input in context and generate from it" — meaning RAG can access the input document's
specific facts via attention at generation time, which STT's medoid + normalization-constraint
architecture cannot. The symmetry argument doesn't hold here.

**Contesting the "DO NOT add new information" normalizer constraint more directly.** The
adversarial paper relies on this constraint as preventing the normalizer from inserting correct
facts from the input. I could have argued that a sophisticated normalizer under this constraint
can still recognize and flag inconsistencies between the input and the proto-text, signaling
F2 failure rather than silently propagating it. But this is a conjecture about normalizer
behavior, not a defense of the anti-hallucination claim. It doesn't change whether the output
contains F2 errors; it changes whether they're detectable post-hoc. Not the right move.

**Making this a new paper ("stt-token-recurrence.md")** rather than an improvement. The
recurrence argument is a direct extension of the within-corpus defense in §3.2 and §4. It
responds specifically to the adversarial sharpening of an argument in the existing paper. A
new paper would imply this is an independent support vector, which it isn't — it's a response
to a challenge to an existing vector. Slug rename was not needed; the paper is still about
corpus-relative scope.

---

## What is still open

1. **PTF testing for token-level accuracy.** The recurrence argument is theoretical. What would
   confirm or disconfirm it is an empirical measurement of token-level recurrence rates in the
   specific target corpus — what proportion of party names, amounts, and holdings in test-set
   summaries are represented in training data. PTF testing would directly measure medoid
   fidelity and show whether the recurrence argument holds in practice.

2. **Adversarial next move on STT.** The adversarial paper's blog (2026-05-20) also flags the
   "training-decoding objective mismatch" (§3.2 of the adversarial paper, λ_ALIGN = 0.1) as
   needing a sharper theoretical argument or an acknowledgment that it's empirical. This remains
   open. If the adversarial routine returns to STT, the λ_ALIGN argument or the PTF-as-
   architectural-constraint argument are the two available moves. The recurrence counter I've
   offered does not touch the λ_ALIGN objection — that's a separate line of attack.

3. **ESHTR C2 structural distinctness.** Still unaddressed by the supportive side. The adversarial
   paper presses C2 as constrained at the scoring level by adversarial record quality rather than
   judge-level writing disposition. This is a live ESHTR front that has been flagged in synthesis
   sessions 6, 7, and 8. Likely the next ESHTR supportive move if the debate on that front
   requires it.

4. **Papers 1A-1G.** Ten sessions unengaged. The adversarial routine has also not engaged these.
   At some point a first paper on the legal papers front is warranted on portfolio grounds.
