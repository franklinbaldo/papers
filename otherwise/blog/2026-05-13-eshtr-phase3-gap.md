# 2026-05-13 — First run: attacking ESHTR's design rationale

## What changed

Created `otherwise/` and `otherwise/blog/` (both new — first run of the
adversarial routine). Wrote the first adversarial paper:
`otherwise/eshtr-phase3-gap.md`.

## Target and vector

**Target**: `embedding_seeded_tournament_paper.md` (ESHTR, Baldo 2025).

**Primary vector**: False premise. The paper's Semantic Proximity Hypothesis
assumes that embedding cosine distance is a reliable proxy for evaluative
frame stability in LLM judges. These are different properties, and they come
apart systematically in legal corpora — because legal domains are internally
heterogeneous (a criminal law cluster contains sentencing, habeas corpus, and
evidence decisions that require different evaluative criteria) and because
rigorous reasoning style appears across domains (producing cross-cluster pairs
that share evaluative frames despite large embedding distances).

**Secondary vector**: Criterion substitution in Phase 3. Even granting the
Phase 2 argument, Phase 3 adds "contextual generalizability" as a new
criterion for cross-cluster comparison. This changes the evaluation objective:
Phase 2 champions are selected by C1–C5; Phase 3 ranks them by a different
property. The combined ranking is not a unified quality ordering.

## What triggered this

No prior adversarial work exists. The ESHTR paper was chosen over the STT
paper (also a position paper with falsifiable predictions) and the two legal
doctrinal papers for the following reasons:

- ESHTR makes the most specific falsifiable claims and has the clearest
  internal tension. The Semantic Proximity Hypothesis is the load-bearing
  premise of the entire architecture, and it's introduced as "informal
  argument" with no empirical support.
- The STT paper is also attackable (medoid-based decoding fails for novel
  content; compression-fidelity tradeoff is glossed over), but that attack
  would be less structural — more a list of implementation risks than a
  challenge to the core design rationale.
- The legal papers (1A and 1B) are doctrinal: the best attacks are on
  normative interpretation, where the burden of proof is different. The
  "rational overruling" argument in 1B is vulnerable, but that attack would
  take a different form — empirical data about how Brazilian courts actually
  handle this.

## What was considered and discarded

**Attack on the Semantic Proximity Hypothesis directly**: The paper
explicitly labels the hypothesis as a falsifiable prediction to be tested.
Attacking it as "unproven" is too weak — the paper concedes this. The more
interesting attack is that the hypothesis, even if true in the rough
form, is insufficient to justify the specific design choice (k-means or
HDBSCAN clustering of legal decisions using a general multilingual
embedding model). The paper needs not just the correlation but the
operationalization to track the relevant property.

**Attack on calibration**: The calibration protocol (Section 5.4) uses
20 decisions with known quality signals (cited approvingly vs. criticized on
appeal). This is a small calibration set and the quality signals may not
generalize. But this felt like a secondary concern — a question about the
robustness of the experiment, not a challenge to the method's design logic.

**Attack on computational complexity claims**: The O(n²/k + k²) analysis
is correct. Attacking it would be unproductive.

**Attack on Phase 3 alone without Phase 2**: The Phase 3 argument is
strongest when combined with the Phase 2 argument, because the Phase 3
objection presupposes that Phase 2 has done its work. Framing it as a
compound failure — the foundation is shaky AND the superstructure doesn't
connect to it coherently — is a more complete attack.

## What is left open

1. The STT paper has not been attacked. The decoding pipeline in particular
   is vulnerable: medoid lookup retrieves chunks from the training corpus,
   so for novel content there are no faithful medoids. The LLM normalization
   step is supposed to handle this, but LLM normalization is precisely what
   the method claims to avoid (hallucination risk). This is worth a session.

2. Paper 1B ("cinco saídas") has not been attacked. The "rational overruling
   by inferior courts" argument is the most vulnerable thesis: it conflicts
   with the institutional design of the system (STF as court of final
   interpretation) and the author's own acknowledgment that the same theorists
   invoked in support (Marinoni, Mitidiero) also hold the orthodox position.
   The author tries to escape this by distinguishing "possibility" from
   "ease" — but the distinction doesn't resolve the institutional objection.

3. Paper 1A ("embargos") is the least vulnerable of the four papers: the
   textual argument from art. 1.022 and art. 489, §1º is solid. The main
   vulnerability is in the "automatic consequence" thesis — it assumes courts
   will correctly characterize what modification flows from the cure, which
   may be harder in practice than the paper implies. Not clear this is a
   strong enough attack to warrant a full paper session.

4. The `yesindeed/` routine has not run. If it does and produces supportive
   papers for ESHTR (e.g., a paper confirming that embedding clusters
   produce higher LLM judge agreement), the attack may need to be updated
   or conceded in specific respects.
