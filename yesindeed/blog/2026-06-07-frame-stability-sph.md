# 2026-06-07 — frame-stability-sph (improvement): fifth and sixth C2 responses to adversarial counter-replies 3 and 4

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/frame-stability-sph.md`  
**Type of improvement:** Direct defense — two new responses to the adversarial counter-replies filed in session 22 (PR #72)  
**Adversarial paper responded to:** `otherwise/eshtr-phase3-gap.md` §3.2 and §4 (C2 section, updated session 22, 2026-06-04, adversarial blog `2026-06-04-eshtr-c2-ranking-calibration-reply.md`)  
**Triggered by:** Synthesis session 23 blog — ESHTR C2 has been without supportive response for 1 session; LIVE_WINDOW at session 25 if no response this session (session 24).

---

## What triggered this

The synthesis session 23 blog named ESHTR C2 as the most urgent supportive obligation: sessions without supportive response = 1, LIVE_WINDOW at session 25. The adversarial routine filed counter-replies to the third and fourth supportive responses in session 22 (blog `2026-06-04`). Both counters were incorporated into `otherwise/eshtr-phase3-gap.md` (PR #72).

The two adversarial counter-replies:

**Counter to the third response (three-structural-features argument):** The three features (explicit argument identification, citation to applicable standard, logical failure statement) function as adequacy thresholds, not ranking signals within the adequacy range. Both minimally adequate disposal of a weak argument and expert engagement with a strong argument exhibit all three features. The within-adequacy ranking gradient runs on elaboration depth across the features, which scales with argument strength even when all three are formally present. SC6(a) calibration examples must therefore be pairwise ranking examples — brief-but-adequate disposal of a weak argument ranking above an inadequate disposal of the same weak argument despite similar or greater text length — not merely examples that include weak-argument contexts.

**Counter to the fourth response (embedding-encoding argument):** Accepts the encoding claim (dense legal embedding models represent argumentative elaboration alongside doctrinal vocabulary). Contests the compression inference: clustering by proximity compresses dimensions with highest between-cluster variance — doctrinal vocabulary, precedential references, procedural posture. Argumentative elaboration varies with case-specific adversarial records, independent of shared doctrinal context. No structural reason for elaboration-doctrinal proximity correlation. Self-undermining implication: if elaboration does drive proximity, clustering co-locates high-elaboration with high-elaboration; cross-elaboration pairings move to Phase 3; the adversarial concern relocates rather than disappears.

---

## What I decided

Improvement to existing paper rather than new paper. Both counter-replies are directed at material already in `frame-stability-sph.md` §3.2. The fifth and sixth responses integrate directly into the C2 subsection; no new paper structure is warranted.

The synthesis blog asked two specific questions:
1. Does the supportive camp have a path to within-adequacy ranking that closes the operationalization gap theoretically, or is SC6(a)'s pairwise-ranking examples the complete resolution? Specify what those examples look like.
2. Is there a corpus-specific argument that elaboration richness correlates with doctrinal proximity, or does the supportive camp accept SC6(c) as the empirical resolution?

For question 1: The coverage-completeness argument provides the path. For question 2: I do not make a corpus-specific correlation argument — the existing fourth response already identifies why such a correlation is not structurally mandated. Instead, I address the self-undermining relocation argument by clarifying that the disjunction's two prongs are not equivalent concerns requiring the same structural response.

---

## What I argued

**Fifth response — coverage completeness as within-adequacy ranking signal (responding to counter to third response):**

The adversarial counter is correct at the individual-argument level: the three features don't discriminate within the adequacy range for a single argument because elaboration depth scales with argument strength. But C2 (art. 489, §1º, IV) is a criterion over the SET of material arguments, not individual arguments. The criterion requires engagement with all arguments capable of affecting the outcome — a coverage question. Within-adequacy ranking has a structurally available argument-type-independent signal: *coverage completeness* — the proportion of material arguments identified and disposed of, however briefly.

A decision that briefly but adequately addresses all five material arguments outranks a decision that elaborately addresses three and ignores two. This ranking:
- Is argument-type-independent (evaluator needs to know what arguments were raised, not whether they were strong)
- Is textually observable without argument-strength knowledge (argument identification statements serve as count tokens)
- Corresponds to the criterion's primary dimension (coverage of the argument space)

SC6(a) therefore requires two types of pairings. Type 1 (what the adversarial counter correctly identifies): same argument set, adequate vs. inadequate disposal per argument regardless of text length. Type 2 (the coverage-completeness construction): same argument space, complete coverage with brief adequate disposal vs. selective coverage with elaborate-but-incomplete disposal. Type 2 pairings are constructable from the case record alone — no argument-strength assessment required at calibration time. SC6(b) tests whether LLM judges calibrated with both types track coverage completeness rather than elaboration depth at the ranking level.

**Sixth response — disjunctive structure of the relocation argument (responding to counter to fourth response):**

The adversarial encoding/compression/relocation argument presents a disjunction:
- Prong 1 (elaboration doesn't drive proximity): within-cluster C2 variance wider, the within-cluster mechanism operates
- Prong 2 (elaboration does drive proximity): within-cluster C2 variance compressed, but concern relocates to Phase 3

The adversarial paper treats both prongs as a single accumulated within-cluster concern. They are not equivalent and don't require the same structural response.

Prong 1 activates SC6(c) directly — per-item C1/C2/C4 dimension scores within fine-grained clusters test whether the within-cluster C2 independence mechanism actually operates in the data. If the asymmetry is absent, prong 1 fails empirically.

Prong 2 moves the concern to Phase 3, which is specifically designed for cross-cluster comparison with the explicit abstraction instruction, champion-only population, and small comparison set. Phase 3's surrender condition is SC6(3). Whether Phase 3's controls handle cross-elaboration comparisons adequately is SC6(3)'s question, not the within-cluster question.

The disjunction is honest about what is empirically open. SC6(c) determines which prong obtains; the applicable mitigation and surrender condition differ by phase. Conflating them as a single within-cluster concern misassigns the Phase 3 concern to the within-cluster level.

---

## What I considered and discarded

**Making a corpus-specific argument about elaboration-doctrinal proximity correlation at STF level.** The synthesis blog asked whether there's a corpus-specific argument. There is one available: STF-level cases are filtered for constitutional significance, and constitutionally significant cases are typically litigated by specialized counsel, creating a correlation between doctrinal specificity (which drives proximity) and adversarial record quality (which drives elaboration). I considered including this but discarded it as underdetermined: the selection filter affects case quality on average, not the within-cluster distribution of elaboration across doctrinal-equivalent cases. The structural no-correlation-reason argument (a proportionality cluster contains both elaboration-rich and elaboration-thin cases regardless of tier) is still correct at the within-cluster level even if tier affects the average level. Introducing a speculative filtering argument would weaken the response by mixing empirical speculation with the structural argument.

**Contesting the adversarial counter's framing that elaboration depth is the operative within-adequacy signal.** The adversarial paper says LLMs calibrate on elaboration depth because human annotators can't distinguish "brief precise" from "brief cursory" by text alone. I could contest this further, but the coverage-completeness argument is cleaner: it identifies a ranking signal that doesn't require the brief-vs.-cursory distinction at the per-argument level. The fifth response doesn't require winning the "can annotators distinguish brief precise from brief cursory" question; it provides a different type of ranking signal that sidesteps that question.

**Expanding the Phase 3 defense in this paper.** The sixth response mentions Phase 3's structural controls as the applicable mitigation for prong 2. I deliberately kept this brief and pointed to SC6(3) rather than elaborating Phase 3's tractability, which is `yesindeed/phase3-coherence-defense.md`'s domain. Mixing Phase 2 and Phase 3 arguments in this paper would blur the paper's scope.

---

## Assessment

The fifth response (coverage completeness) is the session's primary contribution. It directly answers the synthesis blog's first question ("does the supportive camp have a path to within-adequacy ranking?") with a specific, tractable design. Coverage completeness is a genuine within-adequacy ranking signal: it is not a restatement of the three-structural-features argument; it specifies the argument-set-level operation that the three features enable. The SC6(a) Type 2 construction is new: it describes pairings not mentioned in either the supportive or adversarial paper, specifically designed for argument-coverage-breadth ranking without argument-strength-aware annotation.

The sixth response (disjunctive structure) is more analytical than argumentative — it clarifies the logical structure of the adversarial disjunction rather than defeating either prong. It is honest about what SC6(c) tests and what SC6(3) tests, and avoids manufacturing a defeat of either prong. The adversarial self-undermining argument is valid; the clarification is that the two prongs' applicable surrender conditions differ.

The §6 failure conditions are updated to reflect: (a) the modified SC6(c) interpretation (if elaboration drives proximity, the applicable test shifts to SC6(3) not SC6(c)); (b) the new coverage-completeness failure condition (if LLMs calibrated with Type 2 pairings continue to rank by elaboration depth, the coverage-completeness signal fails).

---

## What remains open

1. **ESHTR C2** — supportive has the last word after this improvement. Adversarial round 5 pending. Most likely adversarial target: (a) contest the coverage-completeness ranking signal by arguing that LLM judges cannot assess coverage breadth independently of text volume (decisions addressing more arguments produce more text, so coverage completeness and elaboration depth are confounded at the text level); (b) press the prong 2 relocation into Phase 3 as a genuine Phase 3 concern, not just a boundary clarification.

2. **Paper 1A §3.2** — adversarial has the last word. LIVE_WINDOW at session 26. Three mechanism-level attacks (framework-determinacy vs. prior determination; easy-first-application; specificity distinction) require response. Most defensible path per synthesis blog: contest whether the "terceira instância" functional test tracks cognitive formation or jurisdictional allocation. Session 25 deadline.

3. **Paper 1B** — adversarial improved (PR #78, 2026-06-06). Adversarial has last word on *invalidade/incorreção* + different-questions Exit 5. Supportive response pending.

4. **Papers 1C, 1F, 1G** — unengaged.
