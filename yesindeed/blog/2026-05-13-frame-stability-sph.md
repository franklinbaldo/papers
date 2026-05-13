# 2026-05-13 — frame-stability-sph

**Session type:** New supportive paper  
**Target thesis:** ESHTR Semantic Proximity Hypothesis (§4)  
**Vector:** Mechanism  
**Paper created:** `yesindeed/frame-stability-sph.md`

---

## What triggered this

First run of the supportive researcher routine on this repo. No `otherwise/` directory exists yet (no adversarial papers). No prior `yesindeed/` material. I needed to choose a first target.

**Inventory of the author's papers:**
- ESHTR: Embedding-Seeded Hierarchical Tournament Ranking. Central unfalsified claim: the Semantic Proximity Hypothesis. Well-structured position paper; theoretical motivation in §4 is informal and would benefit from independent grounding.
- STT: Semantic Tokenization Transformers. Architecture proposal with falsifiable predictions; weakest point is the decoding pipeline uncertainty (acknowledged in the paper).
- Paper 1A (Embargos de Declaração): Brazilian procedural law. Thesis on scope of embargos and infringement effects.
- Paper 1B (Cinco Saídas): Brazilian precedent law. Taxonomy of five legitimate responses to binding precedents.

**Why ESHTR Semantic Proximity Hypothesis, not other targets:**
- The hypothesis is the core theoretical claim the entire method rests on. If it fails, the rationale for ESHTR's stratification dissolves.
- It has no independent support at all — the paper itself says it's a falsifiable prediction not yet tested.
- The informal argument in §4 ("the evaluative frame is less stable when items are semantically distant") is plausible but not grounded in any literature.
- A mechanism vector from cognitive science can provide independent grounding without just restating the paper's argument.

STT's main weakness (decoding pipeline) is acknowledged uncertainly by the paper itself, and a support paper restating that the mechanism *might* work would be sycophantic. The Brazilian law papers are sound but narrower; supporting their theses requires deep engagement with domestic jurisprudence that I can contribute to later.

## What I considered and discarded

**Formalization vector for SPH:** I considered writing a more formal characterization of the hypothesis (defining semantic distance and non-transitivity probability precisely). This is possible but would require introducing notation that adds complexity without adding evidence — the paper already has Fleiss' κ as the test statistic. A formalization without empirical grounding is just a different language for the same uncertainty.

**Extension vector for ESHTR:** Could extend the method to scientific paper review or policy evaluation. This is useful but not the most urgent — the core hypothesis needs grounding before extension is valuable.

**Support for STT P1 (compression ratio):** The ≥5x compression target is theoretically estimable from the chunking parameters. But this would be a numerical exercise deriving from the paper's own design, not independent evidence. It would be restatement in more precise voice.

## What the paper actually contributes

The Tversky (1969) intransitivity paper is the canonical source showing that preference cycles arise from systematic criterion switching across pairs — not random error. This is the mechanism I needed: the SPH predicts more criterion switching when items are semantically distant, which is exactly the structure of frame-instability non-transitivity.

The key addition over ESHTR §4's informal argument:
1. Names the mechanism precisely (contingent frame construction / contingent weighting)
2. Shows it's documented in behavioral decision theory as a source of intransitivity, not just an intuition
3. Distinguishes it from the bias-amplification account already in ESHTR — these are additive, not alternatives
4. Derives three more specific sub-predictions (structured cycles, directional predictability, asymmetric cluster-pair gradient) that can be assessed in the same experimental setup

The Tversky (1977) Features of Similarity paper provides the additional point that similarity judgments are context-sensitive in exactly the way needed: the features that drive discrimination between a pair depend on which pair is being considered. This is the bridge from the intransitivity literature to the semantic structure argument.

## Reservations

The main risk in this paper is that LLMs might not actually exhibit contingent frame construction in the way human judges do. The mechanism relies on LLMs having learned domain-specific criterion mappings from training data. If large frontier LLMs have "compressed" these into a unified quality function, the mechanism doesn't apply. I put this in the Anticipated Objection section and was careful not to claim this is proven — the paper explicitly limits itself to "plausibility, not proof."

The Xu et al. (2025) finding that LLM non-transitivity correlates with positional bias is consistent with the mechanism (frame instability → bias-susceptibility), but doesn't confirm the frame-instability account directly. I noted this as supporting but not conclusive.

## PR opened

Branch: `supportive/frame-stability-sph`  
PR description links: target paper (ESHTR), no adversarial paper responded to (none exist), vector = mechanism, new paper.
