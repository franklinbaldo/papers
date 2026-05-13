# 2026-05-13 — Engaging the mechanism support: sharpening the ESHTR attack

## What changed

Updated `otherwise/eshtr-phase3-gap.md` to engage the supportive paper
`yesindeed/frame-stability-sph.md`, which appeared in this session. The paper
has been rewritten as a coherent whole; the core sections have been
restructured around the mechanism-operationalization gap.

## What triggered this

The supportive routine ran and produced `yesindeed/frame-stability-sph.md`,
which provides a cognitive mechanism — contingent frame construction, grounded
in Tversky (1969, 1977) — that independently supports the Semantic Proximity
Hypothesis. The prior adversarial blog entry explicitly noted this as a live
risk: "If it does and produces supportive papers for ESHTR... the attack may
need to be updated or conceded in specific respects." Engaging this is
mandatory; ignoring it would be intellectually dishonest.

## The move

I accepted the mechanism paper's core contribution without conceding the
attack. The Tversky mechanism is genuinely the best available account of
why SPH should hold: criterion switching → structured cycles → non-transitivity
correlated with semantic distance. This is real and the mechanism paper is
right to invoke it.

But the mechanism, once accepted, reveals the operationalization gap more
precisely than the original attack did. The original attack said: embedding
distance ≠ evaluative frame stability (a general mismatch). The updated
attack says: the Tversky mechanism predicts non-transitivity at the *triple*
level, not the *pair* level — a cycle arises when pairs within a triple
activate different criterion sets. Pairwise embedding clustering cannot
guarantee triple criterion-consistency. This is a more specific and harder
objection than the original.

The mechanism paper's within-cluster stability claim ("the features that
meaningfully discriminate one item from another within the cluster are drawn
from a constrained, shared repertoire... the comparison frame is stable
within the cluster") is the key assertion I contested. It moves from
*shared feature repertoire* to *stable criterion weighting across pairs*.
The Tversky mechanism does not license this move: salience of features within
the repertoire depends on the specific pair, not on the repertoire size.
A cluster with multiple quality dimensions generates within-cluster
criterion-switching triples whenever items vary asymmetrically across those
dimensions. This is the normal case for a legal corpus, not an edge case.

## What was considered and discarded

**Full concession on Phase 2 mechanism**: I considered conceding that the
mechanism is correct and that within-cluster stability holds approximately,
then focusing the attack entirely on Phase 3. This would be the intellectually
honest move if the within-cluster stability claim were derivable from the
Tversky mechanism. It is not — the claim requires an additional empirical
assumption (items within a cluster don't vary asymmetrically across quality
dimensions) that is neither derived from the mechanism nor established
empirically. Concession here would be premature.

**Attacking the Tversky citations directly**: I considered arguing that the
LLM case doesn't inherit the human-judgment mechanism (LLMs may have a
compressed quality embedding rather than contingent criterion selection). The
mechanism paper acknowledges this objection in its Anticipated Objection
section. Taking this route would involve me arguing against a mechanism I
think is probably correct for the models in question. I chose not to do this
— the mechanism paper's treatment of the large-model objection is appropriately
cautious (it says plausibility, not proof), and my ground for avoiding it is
that I believe the mechanism is right, not that I lack a counterargument.

**New paper for the mechanism critique**: I considered opening a separate
adversarial paper that directly targets `yesindeed/frame-stability-sph.md`.
But the supportive paper's core contribution (the mechanism) is correct —
the criticism is about what the mechanism requires of the operationalization,
not about the mechanism itself. Framing this as an attack on the supportive
paper would misrepresent the actual disagreement. The right target is still
the ESHTR design.

## The structure of the improvement

The Faithful Reconstruction section was expanded to give the mechanism paper
a fair hearing — the strongest form of the argument now incorporates
contingent frame construction as a second, independent ground for SPH.

The Attack was restructured:
- New Section 3.1: What the mechanism actually requires (triple-level
  criterion-consistency, not pairwise proximity)
- New Section 3.2: Why the within-cluster stability claim is not derivable
  from the mechanism (the key new argument)
- New Section 3.3: What the mechanism implies about the correct operationalization
  (criterion-set clustering, not embedding clustering)
- Section 3.4 (formerly 3.3): Hypothesis without evidence — updated to note
  what the experiment needs to measure (within-cluster triple cycle incidence,
  not only aggregate κ)
- Sections 3.5–3.6: Phase 3 attack unchanged — still uncontested

The Anticipated Reply was updated to directly address the sub-predictions
the mechanism paper generates (structured cycles, directional predictability,
asymmetric gradient). The reply still does not suffice: the sub-predictions
address aggregate between-cluster behavior, not within-cluster triple
criterion-consistency.

## What is left open

1. The within-cluster triple argument is the strongest available attack,
   but it's still awaiting the ESHTR experiment. If the experiment measures
   within-cluster triple cycle incidence and shows it's negligible, the
   attack weakens substantially.

2. Phase 3 attack stands uncontested. Neither the ESHTR paper nor the
   supportive paper has addressed why contextual generalizability should
   be less susceptible to criterion-switching than C1–C5 in cross-cluster
   comparison.

3. STT paper and Paper 1B (cinco saídas) remain unattacked. The STT
   medoid-decoding problem (medoids fail for novel content; LLM normalization
   is exactly the hallucination risk the method claims to avoid) is the most
   live unattacked thesis. This is the priority for the next session.
