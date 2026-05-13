# Frame Stability and the Semantic Proximity Hypothesis: A Cognitive Mechanism for Non-Transitivity in LLM Judges

---

## 1. Thesis Supported

Baldo (2025), "Embedding-Seeded Hierarchical Tournament Ranking" (ESHTR), Section 4, states the **Semantic Proximity Hypothesis**:

> "the incidence of non-transitive preferences in LLM judges is positively correlated with the semantic distance between compared items"

and offers an informal argument grounding this hypothesis in the instability of implicit evaluative frames when compared items are semantically distant.

This paper provides a mechanism vector: an account from the cognitive science of comparative judgment — specifically the literature on contingent weighting and frame-sensitive preference — that independently grounds why the Semantic Proximity Hypothesis should hold. The mechanism is distinct from, and additive to, the bias-amplification account in ESHTR §4 (which focuses on positional and verbosity biases being harder to override when stable criteria are unavailable). The frame-stability account operates at an earlier stage: the evaluative criteria themselves are not stably selected across cross-cluster pairings, so bias-correction applied within any single pairwise comparison cannot prevent cycles arising from criterion inconsistency across three comparisons.

---

## 2. What This Support Adds

**Vector:** Mechanism. The paper proposes a specific causal model — contingent frame construction in comparative judgment — that explains why non-transitivity should be more frequent when compared items are semantically distant. This mechanism is grounded in pre-LLM literature on human preference formation and generates a prediction about the *structure* of the non-transitivity (direction-reversing cycles, not random noise) that goes beyond the general Semantic Proximity Hypothesis and could be tested in the ESHTR experimental setup.

The support does not repeat the ESHTR §4 argument. It offers independent grounding from a different domain.

---

## 3. The Mechanism

### 3.1 Intransitivity from Contingent Criterion Selection

A foundational result in behavioral decision theory is that preference intransitivity arises not from random error but from systematic changes in decision strategy across pairs (Tversky, 1969). If an agent selects evaluation criterion d₁ to adjudicate between A and B, criterion d₂ to adjudicate between B and C, and criterion d₃ to adjudicate between A and C, then A > B > C and C > A can all be locally correct without any single judgment being unreliable. The cycle is a product of criterion switches across pairs, not of noise within any pair.

The key empirical finding in Tversky (1969) is that such criterion switches are *predictable from the structure of the choice set*: different features are salient in different pair contexts, and the feature that is most discriminating in one pair need not be the most discriminating in another.

This is not a failure of rationality; it is a consequence of the well-documented fact that comparative judgment is context-sensitive. Tversky (1977) showed that similarity judgments between two objects are influenced by which features best discriminate that particular pair: shared features and distinctive features contribute asymmetrically depending on what is being compared. The same structural property applies to preference: the implicit weighting of features shifts with the pair.

### 3.2 Frame Construction and Frame Stability

Define a **comparison frame** as the implicit weighting vector w(A, B) that an evaluator applies when comparing items A and B — encoding which features matter and how much. A comparison frame is **stable** across a triple (A, B, C) if w(A, B) ≈ w(B, C) ≈ w(A, C): the same set of features drives all three pairwise judgments. A frame is **unstable** if the weighting shifts substantially across pairs.

Transitivity is guaranteed when the frame is stable: if the same features are used in all three comparisons and item X consistently outperforms Y on those features, the ranking is consistent. Transitivity is at risk when the frame is unstable: switching from features that favor A-over-B to features that favor C-over-A can produce a cycle even when each individual judgment is accurate under its own frame.

**Within a semantic cluster**, items share subject matter, structural conventions, vocabulary, and domain-specific reasoning standards. The features that meaningfully discriminate one item from another within the cluster are drawn from a constrained, shared repertoire. For a set of judicial decisions all concerning administrative disciplinary proceedings, the discriminating features — thoroughness of fact-finding, coherence of sanction proportionality reasoning, adequacy of procedural safeguards — are approximately the same across all pairs. The comparison frame is stable within the cluster.

**Across semantic clusters**, items differ in subject matter, normative framework, vocabulary, and reasoning conventions. The features that best discriminate a criminal sentencing decision from a tax injunction ruling are not the same features that best discriminate a tax injunction ruling from a property rights decision. The comparison frame shifts between pairs. This frame shift creates the structural conditions for direction-reversing cycles: A beats B on Feature₁ (criminal reasoning quality), B beats C on Feature₂ (regulatory analysis depth), and C beats A on Feature₃ (property law precedent handling) — a cycle produced by criterion switching, with each individual judgment locally defensible.

### 3.3 Why LLM Judges Inherit This Mechanism

LLM judges trained on human-generated preference data learn the context-sensitivity that characterizes human comparative judgment. An LLM that has been trained or prompted to evaluate "judicial quality" will have acquired, from legal text and human annotations, that:

- criminal reasoning quality is judged on criteria specific to that domain (evidentiary standards, sentencing proportionality, constitutional rights compliance);
- administrative reasoning quality invokes a different criterion set (abuse of discretion, proportionality of sanction, due process compliance);
- contract law quality invokes yet another (formation analysis, breach materiality, remedy appropriateness).

This domain-specific criterion mapping is *not* a bias to be corrected: within-cluster, it produces more reliable judgments by activating criteria that are actually relevant to the domain being evaluated. It becomes a structural problem precisely when cross-cluster comparisons ask the LLM to compare items from different criterion regimes.

The LLM faces the same contingent weighting problem as a human domain expert asked to compare work across their specialty and adjacent domains: the evaluative frame that makes sense for items in domain A is not the same as the frame that makes sense for items in domain B, and the frame chosen for the A-vs-B comparison may differ from the frame chosen if the same items appeared in an A-vs-C comparison.

Xu et al. (2025) document that LLM non-transitivity is correlated with positional bias — a result consistent with the frame-instability account. When the comparison frame is unstable, the LLM has no stable criterion set to apply, and surface-level heuristics (position, length) fill the gap. The frame-instability mechanism thus precedes and explains the bias-susceptibility documented by Xu et al.: instability creates the conditions under which biases become decisive.

### 3.4 A More Specific Prediction

The frame-stability account generates a prediction more specific than the general Semantic Proximity Hypothesis. If non-transitivity arises from criterion switching, then:

1. Cross-cluster non-transitivity should be **structured**: cycles should not be uniformly distributed across all possible item triples but should cluster around triples where the pairwise semantic distances are maximally unequal (one within-cluster pair, two cross-cluster pairs).

2. The direction of cycles should be **predictable from the semantic structure**: if cluster C_i emphasizes Feature₁ and cluster C_j emphasizes Feature₂, then items from C_i should systematically beat items from C_j when the framing activates Feature₁ and lose when Feature₂ is activated — producing a predictable direction for cycles involving items from C_i and C_j.

3. Cross-cluster κ degradation should be **asymmetric across cluster pairs**: cluster pairs that are semantically closer (e.g., two civil law clusters vs. a civil law and a criminal law cluster) should show smaller κ degradation. This is a testable gradient, not a binary within/cross split.

Predictions 1–3 can be assessed in the ESHTR experimental setup (§5.5, §6) with moderate additional analysis: tracking not just whether κ is lower cross-cluster but whether the distribution of non-transitive triples matches the structured pattern the mechanism predicts.

---

## 4. Anticipated Objection

The mechanism assumes that LLM judges construct locally varying comparison frames that shift with the semantic context of the pair. An alternative model holds that LLMs encode a single high-dimensional quality embedding space in which any two items can be compared by a fixed function of their embeddings, producing preferences that are stable across permutations of the comparison context. On this model, non-transitivity would arise from noise in the quality embedding rather than from criterion switching, and would not be systematically correlated with semantic distance.

The embedded-quality model is consistent with some recent findings showing that larger LLMs produce more consistent pairwise judgments overall. If consistency gains from scale eliminate the criterion-switching mechanism, cross-cluster non-transitivity would not exceed within-cluster non-transitivity, and the Semantic Proximity Hypothesis would be disconfirmed.

This objection underscores that the cognitive science grounding provides *plausibility*, not proof. The mechanism is the best available account given what is known about how LLMs process comparative prompts, but it is not derivable from first principles about LLM internals. The ESHTR experimental protocol (Section 5.5) is the necessary test.

---

## 5. Scope of This Support

This paper strengthens the theoretical plausibility of the Semantic Proximity Hypothesis through a mechanism independent of the ESHTR paper's own account. It adds:

- a named mechanism (contingent frame construction, grounded in the Tversky intransitivity literature);
- a structural distinction between two sources of non-transitivity (frame instability vs. bias amplification), showing they are additive rather than alternative;
- three more specific experimental predictions derivable from the mechanism (structured cycles, directional predictability, asymmetric cluster-pair gradient) that can be assessed in the same experimental setup as the general hypothesis.

This paper does **not** provide empirical evidence for the Semantic Proximity Hypothesis. It does not test LLM judges. The ESHTR experimental protocol remains the required validation. The mechanism argument increases the prior probability that the hypothesis will be confirmed, and its specific sub-predictions give the experiment additional diagnostic power.

---

## 6. Conditions Under Which This Support Would Fail

- If the ESHTR experiment shows cross-cluster κ ≤ within-cluster κ (the general hypothesis is disconfirmed), this mechanism paper falls with it.
- If cross-cluster non-transitivity is uniformly distributed rather than structured (cycles are not concentrated around triples with maximal pairwise semantic distance asymmetry), prediction 1 fails, and the criterion-switching account is not supported even if the general hypothesis holds.
- If the distribution of non-transitive cycles shows no predictable directional bias across cluster pairs (prediction 2), the mechanism fails even with the general hypothesis confirmed — pointing to noise-based rather than frame-based non-transitivity.
- If scale eliminates the criterion-switching mechanism (large enough LLMs show no semantic-distance gradient in non-transitivity), the cognitive science grounding does not transfer to frontier models of the kind used in ESHTR's panel.

---

## References

- Baldo, F. S. (2025). Embedding-Seeded Hierarchical Tournament Ranking: A Scalable Method for Evaluating Judicial Decision Quality with LLM Panels. *Position paper*. (`embedding_seeded_tournament_paper.md`, this repository.)
- Tversky, A. (1969). Intransitivity of preferences. *Psychological Review*, 76(1), 31–48.
- Tversky, A. (1977). Features of similarity. *Psychological Review*, 84(4), 327–352.
- Xu, Y., Ruis, L., Rocktäschel, T., and Kirk, R. (2025). Investigating Non-Transitivity in LLM-as-a-Judge. *ICML 2025 Spotlight*. arXiv:2502.14074.
- Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*.
