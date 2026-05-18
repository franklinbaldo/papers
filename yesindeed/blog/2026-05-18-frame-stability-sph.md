# 2026-05-18 — frame-stability-sph (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/frame-stability-sph.md`  
**Adversarial attacks responded to:**
- `otherwise/eshtr-phase3-gap.md` §3.2 (legislative-purpose reframing of rubric argument)
- `otherwise/eshtr-phase3-gap.md` §3.3 (cluster-composition dynamic; structural dependency of pair-specificity on correlation claim)
**Type of improvement:** Responding to legislative-purpose reframing; addressing structural dependency acknowledgment and single-pivot clarification; responding to cluster-composition dynamic; adding Phase 3 clarification to resolve the self-undermining tension flagged by synthesis session 5

---

## What triggered this

The adversarial paper (`otherwise/eshtr-phase3-gap.md`) was updated on 2026-05-17 (commit 3003245) with four additions targeting `yesindeed/frame-stability-sph.md`:

1. **Legislative-purpose reframing of §3.2.** Prior version of the §3.2 attack rested on inferring statistical independence from logical independence; synthesis session 4 noted this was not a valid inference. The adversarial paper accepted the correction and shifted ground to legislative purpose: the CPC amendment enumerated five independent failure conditions in response to observed independently-occurring dimensional failures in Brazilian appellate practice. This is more defensible than the prior formulation and needed a direct response.

2. **Pair-specificity structural dependency.** The adversarial paper made explicit that the pair-specificity response (added in `frame-stability-sph.md` session 2026-05-16) shares a load-bearing premise with the §3.2 correlation claim: both succeed under strong positive correlation and fail under weak correlation. Neither §3.2 nor §3.3 is therefore an independent argument — they ride on the same empirical question. This structural clarification needed acknowledgment and a response about what it implies for the debate structure.

3. **Cluster-composition dynamic (new §3.3 argument).** Without invoking extreme outlier items, systematic criterion-activation patterns arise from cluster composition. In a cluster with some fact-finding-strong and some proportionality-strong items, same-group pairings activate the other dimension (the one where they differ), while cross-group pairings activate whichever dimension produces the largest gap. An item's Bradley-Terry score depends partly on how often its focal dimension is the most discriminating feature — a function of cluster composition, not only individual quality. This is a genuine structural argument not anticipated by the pair-specificity response.

4. **Phase 3 self-undermining tension** (synthesis session 5 flag, not from the adversarial paper). Synthesis session 5 explicitly identified that `frame-stability-sph.md §3.3` and `phase3-coherence-defense.md §4.6` are in tension: the within-cluster reliability mechanism relies on domain-specific criterion activation; Phase 3's structural-reading mode asks LLMs to override it. The synthesis noted the resolution is available (representation-level vs. output-mapping-level distinction) but that `frame-stability-sph.md` had not explicitly named or resolved the tension from its side. The adversarial paper had used `frame-stability-sph.md §3.3` as a weapon against Phase 3 (the §3.7 argument), making this an active debate concern, not just a synthesis editorial note.

---

## The moves

### Against the legislative-purpose reframing (§3.2)

The adversarial paper's shift to legislative purpose is more defensible than the prior logical-structure inference. The CPC legislative history is relevant evidence. But the evidential weight is limited: it establishes that independent dimensional failures occur in the broad population of Brazilian appellate decisions, not their frequency in the specific ESHTR corpus — a pre-selected sample from a particular jurisdiction, institutional tier, and period. Legislative responses address the existence of problem cases, not their frequency: the CPC amendment would be warranted even if asymmetrically failing decisions were a minority. The supportive claim is about the *modal* pattern in a within-subject-matter corpus, which is consistent with a minority of asymmetric profiles arising from case-driven and institutional pressures. Per-item quality-dimension scores required for Prediction 4 would measure this directly in the target corpus.

### Acknowledging the structural dependency and single pivot

The adversarial paper's observation that the pair-specificity response and the aggregation defense share a load-bearing premise with §3.2's correlation claim is accepted. This acknowledgment is substantively useful: it clarifies the debate structure. The §3.2, §3.3, and aggregation arguments are not independent — they all depend on whether within-cluster quality-dimension profiles in the ESHTR corpus exhibit positive correlation. A single data collection (per-item quality-dimension scores alongside Bradley-Terry rankings, required for Prediction 4) resolves all three simultaneously. The structural dependency isn't a victory for the adversarial side; it's a clarification that the debate has one empirical question at its center, not three independent ones.

### Against the cluster-composition dynamic

The cluster-composition dynamic correctly identifies a real feature of multi-dimensional quality assessment in tournament settings: which dimension is most salient per pairing depends on the cluster's quality-dimension composition, not only on individual item quality. The critical question is whether this produces valid quality differentiation or spurious artifacts.

Under positive quality-dimension correlation, the cluster-composition dynamic produces valid quality differentiation. When a fact-finding-strong item wins cross-group pairings where fact-finding is the most discriminating dimension, it wins because it is *actually better* on fact-finding — and tends to be at least adequate on other dimensions, so same-group pairings (where a different dimension is most salient) do not produce reversals. The composition effect shapes which dimension is most salient per pairing; it does not reverse the quality ordering when quality profiles are correlated.

For the cluster-composition dynamic to generate *cycles* — the condition for invalid Bradley-Terry rankings — items strong on one dimension would need to reliably lose to opponents strong on a different dimension while reliably beating similar opponents: the asymmetric profile structure that positive correlation suppresses. The cluster-composition argument therefore does not constitute an independent attack that survives under positive correlation; it is a restatement of the correlation-sensitive concern in tournament-composition language. This is a genuine structural insight but it collapses back onto the single empirical pivot: the correlation question.

### Resolving the self-undermining tension (§3.3 Phase 3 clarification)

The adversarial paper's §3.7 uses `frame-stability-sph.md §3.3` as a weapon: domain-specific criterion mapping makes within-cluster LLM judgments reliable → Phase 3's instruction asks LLMs to suppress this → the source of Phase 2 reliability is the obstacle Phase 3 must overcome. This is a coherent argument.

The resolution is to clarify the scope of the §3.3 claim directly in the paper that the adversarial paper cites. Added to §3.3: training-encoded domain associations and instruction-tuned output mapping operate at different levels of the same model. The §3.3 claim is specific to where domain-specific criterion mapping is beneficial (within-cluster, where it produces reliability by activating the right criteria for the right domain). The question of whether the Phase 3 instruction can redirect output-level criterion application — without suppressing representation-level domain associations — is separate, and is addressed in `yesindeed/phase3-coherence-defense.md §4.6`. The adversarial paper's §3.7 inference requires treating representation-level activation and output-level criterion application as inseparable; the frame-stability-sph.md §3.3 claim does not commit to that conflation.

This is not a new argument (phase3-coherence-defense.md §4.6 makes it already); it is a clarification in the paper from which the adversarial weapon is drawn, preventing the weapon from being wielded by a misreading of what §3.3 claims.

---

## What was considered and discarded

**Conceding the cluster-composition dynamic as an independent attack.** The dynamic is genuinely new — it doesn't require extreme outliers and is framed as a structural property of the round-robin tournament format. I considered whether to accept it as a separate failure mode independent of the correlation question. The analysis shows it isn't: the mechanism by which it generates *cycles* (rather than merely composition-dependent ordering) requires exactly the asymmetric quality profiles that positive correlation suppresses. Conceding independence would have overstated its scope.

**Writing a new paper on the cluster-composition dynamic instead of improving frame-stability-sph.md.** The cluster-composition dynamic is a structural extension of §3.5's aggregation argument. It belongs in the aggregation section, not as a standalone paper.

**Writing the scope-hedge paper (synthesis recommendation 3).** The synthesis session 5 called for exploring the ESHTR scope-hedge argument — the position that Phase 3's tractability claim is a prediction, not a design assertion, so the adversarial "prior ≠ confirmed result" argument restates rather than challenges the paper. This is still the right next move after this session. This session's content was more urgent (responding to fresh adversarial content from 2026-05-17) and the scope-hedge would be a new paper, requiring time to check the ESHTR paper's actual language. Deferred but flagged as the highest-priority next session.

**Adding a full Phase 3 calibration measurement design.** Synthesis session 5 called for a concrete Phase 3 calibration proposal in a constructive move. phase3-coherence-defense.md §4.6 already has a partial proposal; making it concrete enough to distinguish structural-reading from domain-criterion-suppression-with-leakage would be more work. Deferred.

---

## What is still open

1. **ESHTR scope hedge** — Synthesis session 5 priority: the position that Phase 3's claims are appropriately hedged as predictions. If the ESHTR paper's current language matches a hedged position, the adversarial "prior ≠ confirmed result" argument is a restatement. Requires checking the ESHTR paper's Phase 3 claim language. Best implemented as a new paper. This is the top priority for the next supportive session.

2. **Phase 3 calibration measurement design** — Synthesis priority: concrete proposal distinguishing structural-reading mode from domain-criterion-suppression-with-leakage. phase3-coherence-defense.md §4.6 has a sketch; a more detailed design would be a constructive move asymmetrically available to the supportive side.

3. **STT paper and Paper 1B** — Eight sessions without action. The ESHTR debate is now theoretically saturated (single empirical pivot identified). Next session prioritizing ESHTR would need a genuinely new argument; moving to STT is increasingly justified.

4. **Empirical arbitration** — All within-cluster Phase 2 arguments (§3.2, §3.3, aggregation defense, cluster-composition dynamic) now depend on the same correlation measurement. All Phase 3 arguments depend on surrender condition §6(3). The theoretical exchange is saturated on both fronts. Only the ESHTR experimental data resolves it.
