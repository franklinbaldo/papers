---
type: "Audit Report"
title: "Structured Irregularity / Pedagogical Signal Extraction prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of learner-relative pedagogy, progressive decodability, retrospective interpretation, structured irregularity, predictive invariants, and noisy pedagogical channels."
tags: [machine-teaching, prior-art, curriculum-learning, retrospective-revaluation, predictive-information, pedagogy, noisy-channels]
timestamp: 2026-09-18T04:10:00-04:00
---

# Structured Irregularity / Pedagogical Signal Extraction prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal audit of the novelty boundary in [`pedagogical_signal_extraction.md`](../../pedagogical_signal_extraction.md), _Structured Irregularity: Learning as Signal Extraction in Noisy Pedagogical Channels_. The paper is explicitly a position paper and reports no empirical results. This audit separates established machine-teaching, curriculum-learning, predictive-representation, and retrospective-revaluation machinery from a narrower unresolved conjunction around learner-relative opacity and retrospective held-out gain. It does **not** establish exhaustive novelty, patent novelty, independent invention, copying, plagiarism, or causal dependence.

## 1. Claims audited

The paper's contribution is best decomposed into claims rather than assessed by title similarity:

- **C1 — learner-relative optimal pedagogy:** an optimal teaching message is relative to a specified learner; teacher policy, learner model, communication budget, and target competence jointly determine the useful curriculum;
- **C2 — progressive decodability:** a staged curriculum may be locally difficult or irregular but should expose reusable structure over time, with stagewise future predictive/task gain for the specified learner;
- **C3 — retrospective interpretation / temporary opacity:** an earlier observation that was initially uninformative may become useful after later structure is learned; the paper operationalizes this by ablating the earlier observation from the completed history and measuring held-out loss (`R_{i,t}`);
- **C4 — structured irregularity:** pedagogically useful data may combine high local diversity/surprise with a low-complexity, stable higher-order grammar or teaching policy; optimal curricula should discriminate among live hypotheses without making the interpretive meta-structure gratuitously complex;
- **C5 — learner as predictive-invariant extractor:** the preferred learner is not the one with maximal retrospective fit, but one that extracts a compact representation that survives new data, perturbation/intervention and supports prediction, task execution, and transfer;
- **C6 — learner-relative taxonomy of apparent irregularity:** exogenous channel noise, endogenous opacity, accidental finite-sample pattern, and concealment should be distinguished operationally rather than by surface appearance;
- **C7 — primitive-interface criterion:** in the strict binary benchmark, next-bit prediction remains the external scoring interface while tokens/segments/higher-order symbols are revisable internal instruments rather than canonical targets.

The paper is careful to state these as hypotheses/framework proposals. The audit therefore asks which **components and combinations** were already public before the relevant GitHub cutoff.

## 2. Temporal reconstruction of our claims

### 2.1 Earliest claim-bearing commit

GitHub history identifies commit [`d31fcfc19406c63f2dddfc55a6e3f96c585d0a3c`](https://github.com/franklinbaldo/papers/commit/d31fcfc19406c63f2dddfc55a6e3f96c585d0a3c), **“paper: add pedagogical signal extraction position paper,”** at:

**2026-07-31 14:20:42 UTC.**

This was not a title-only placeholder. The initial 432-line file already contained the material versions of C1–C6: the teacher–channel–learner model; learner-relative noise/opacity; progressive decodability; retrospective interpretation; structured irregularity; and the predictive-invariant learner criterion.

### 2.2 Earliest unambiguous public claim statement

Pull request [`#241`](https://github.com/franklinbaldo/papers/pull/241), **“paper: model learning as signal extraction in noisy pedagogical channels,”** was opened at:

**2026-07-31 14:21:45 UTC.**

Its public body explicitly enumerated the main hypotheses:

1. progressive decodability, including retrospective reinterpretation of earlier evidence;
2. structured irregularity, defined as high local diversity/entropy under stable low-complexity higher-order structure;
3. learner as invariant extractor, judged by persistence under future data, perturbation and intervention rather than retrospective fit;
4. teacher–learner co-definition / learner-relative optimal messages.

It also stated the noise/opacity/accidental-pattern/concealment distinctions and the primitive next-bit clarification. PR #241 was merged only on 2026-08-01, so the merge date is **not** used as the priority date.

### 2.3 Cutoff used

For C1–C7 this audit therefore uses the conservative public cutoff:

**2026-07-31 14:21:45 UTC.**

The claim-bearing commit is 63 seconds earlier and corroborates the same content. Only work publicly available before this cutoff is eligible for `prior_art`, `partial_prior_art`, or `adjacent_prior_work`. Later work is classified separately.

## 3. Search protocol

The search intentionally decomposed the paper's terminology, because older work does not use “structured irregularity,” “progressive decodability,” or “temporary opacity.” Sources included AAAI, IJCAI, ICML/ACM records, PMLR, arXiv, PubMed/journal primary pages, cognitive-science literature, information-theoretic predictive inference, and targeted post-cutoff searches.

Representative queries included:

- `machine teaching optimal training set learner model target model`
- `pedagogical sampling learner teacher examples rational model`
- `curriculum learning meaningful order gradually more concepts`
- `teacher curriculum maximize learning progress unknown student`
- `sequential machine teaching learner model teacher intent`
- `POMDP teaching learner uncertainty optimal pedagogical actions`
- `machine teaching imperfect noisy teacher knowledge`
- `retrospective revaluation later information earlier cue statistical learning`
- `backward blocking statistical learning retrospective revaluation`
- `predictive information minimal sufficient representation past future`
- `information bottleneck most compact model desired predictive power`
- `minimal predictive representation causal states`
- `simple examples pedagogical sampling motifs alternative interpretations`
- `progressive decodability learning pedagogy`
- `structured irregularity machine learning teaching`
- `retrospective gain earlier observation later decoding`
- `temporary opacity learning signal`
- `noise learner-relative pedagogy`
- post-cutoff exact-title, distinctive-phrase and combination searches through 2026-09-18.

Negative searches are bounded search results only. “Not located” does not imply nonexistence.

## 4. Pre-cutoff findings

### 4.1 Learner-relative optimal teaching is established machine-teaching machinery

**Work:** Xiaojin Zhu, **“Machine Teaching: An Inverse Problem to Machine Learning and an Approach Toward Optimal Education.”** AAAI 2015.

- public proceedings date: **2015-03-04**;
- primary record: <https://ojs.aaai.org/index.php/AAAI/article/view/9761>;
- DOI: <https://doi.org/10.1609/aaai.v29i1.9761>.

Zhu defines machine teaching as finding an **optimal training set given a machine-learning algorithm and target model**. That directly establishes the generic learner-relative inverse problem underlying C1.

**Work:** Patrick Shafto, Noah D. Goodman, Thomas L. Griffiths, **“A rational account of pedagogical reasoning: teaching by, and learning from, examples.”** _Cognitive Psychology_ 71 (2014).

- online publication: **2014-03-07**;
- DOI: <https://doi.org/10.1016/j.cogpsych.2013.12.004>;
- PubMed: <https://pubmed.ncbi.nlm.nih.gov/24607849/>.

Shafto et al. model the reciprocal coupling explicitly: a knowledgeable teacher selects examples to help a learner infer a concept, while a learner interprets examples under the assumption that they were pedagogically selected.

**Work:** Xiaojin Zhu, Ji Liu, Manuel Lopes, **“No Learner Left Behind: On the Complexity of Teaching Multiple Learners Simultaneously.”** IJCAI 2017.

- proceedings: **2017**;
- primary record: <https://www.ijcai.org/proceedings/2017/502>;
- DOI: <https://doi.org/10.24963/ijcai.2017/502>.

This work makes learner heterogeneity explicit: the same training set has different teaching cost across learners, and partitioning a class changes teaching complexity.

**Compared claims:** C1 and the generic teacher–learner co-definition part of C2/C4.

**Classification:** `prior_art` for the generic claim that the best teaching message/training set depends on the learner model and target; `partial_prior_art` for the full noisy-channel framework.

**Revision:** the present paper should not carry novelty on “optimal messages are learner-relative.” Its distinctive question, if any, lies in what happens when the representation/channel itself is initially undecodable and later evidence changes the utility of earlier events.

### 4.2 Sequential teaching and curriculum optimization already depend on learner state and learning progress

**Work:** Yoshua Bengio, Jérôme Louradour, Ronan Collobert, Jason Weston, **“Curriculum Learning.”** ICML 2009.

- proceedings: **2009**;
- DOI: <https://doi.org/10.1145/1553374.1553380>.

The paper formalizes training curricula in which examples are selected and ordered so that concepts are encountered progressively, and reports effects on generalization and optimization.

**Work:** Anna N. Rafferty, Emma Brunskill, Thomas L. Griffiths, Patrick Shafto, **“Faster Teaching via POMDP Planning.”** _Cognitive Science_ 2016 (online **2015-09-24**).

- DOI: <https://doi.org/10.1111/cogs.12290>.

The teacher maintains uncertainty over learner knowledge, chooses a sequence of pedagogical actions, and optimizes immediate and long-term teaching value. The paper directly shows that assumed learner models change the optimal teaching policy.

**Work:** Tomi Peltola, Mustafa Mert Çelikok, Pedram Daee, Samuel Kaski, **“Machine Teaching of Active Sequential Learners.”** arXiv v1 **2018-09-08**.

- arXiv: <https://arxiv.org/abs/1809.02869>.

This is particularly relevant to the reciprocal side of C2: it models a sequential teacher that plans, and a learner that improves by **recognizing teaching intent** through a model of the teacher.

**Work:** Rémy Portelas, Cédric Colas, Katja Hofmann, Pierre-Yves Oudeyer, **“Teacher algorithms for curriculum learning of Deep RL in continuously parameterized environments.”** CoRL / PMLR 100 (2020), public preprint in 2019.

- PMLR: <https://proceedings.mlr.press/v100/portelas20a.html>.

The teacher does not initially know the student's capabilities. It learns which environments are easy, difficult, or unlearnable and sequentially samples curricula to maximize **absolute learning progress**.

**Work:** Bo Yang et al., **“ZPD Detector: Data Selection via Capability-Difficulty Alignment for Large Language Models.”** arXiv v1 **2026-01-16**.

- arXiv: <https://arxiv.org/abs/2601.10986>.

It explicitly models evolving model capability and dynamically selects the most informative samples at each stage.

**Compared claim:** C2.

**Classification:** `prior_art` for staged/sequential curriculum selection and learner-state-relative progress objectives; `partial_prior_art` for “progressive decodability” as defined here.

None of these located works supplied the exact C3 mechanism in which later-acquired representational structure retrospectively converts a specific earlier event from near-useless to held-out-useful. Therefore, stagewise learning progress cannot itself be used as the novelty boundary; retrospective unlock is the narrower unresolved part.

### 4.3 Noisy or imperfect teaching is established, but “opacity” is not equivalent to ordinary noise

**Work:** Rati Devidze, Farnam Mansouri, Luis Haug, Yuxin Chen, Adish Singla, **“Understanding the Power and Limitations of Teaching with Imperfect Knowledge.”** IJCAI 2020.

- primary proceedings record: <https://www.ijcai.org/proceedings/2020/367>;
- DOI: <https://doi.org/10.24963/ijcai.2020/367>.

The work studies machine teaching when the teacher has limited/noisy knowledge of the target representation and learning dynamics, asking when imperfect knowledge permits or prevents effective teaching.

Rafferty et al. likewise formulate teaching under uncertainty about learner state through a POMDP. These literatures already block any broad claim that pedagogical interaction under uncertainty/noise is new.

**Compared claims:** C2 and C6.

**Classification:** `prior_art` for teaching with uncertainty/imperfect knowledge; `adjacent_prior_work` for C6's exact distinction between **exogenous noise** and **endogenous opacity whose decoding rule becomes available later**.

The distinction matters: ordinary channel/teacher uncertainty need not contain recoverable information. In C6 the learner can initially fail to decode a component even though it is lawful and later demonstrably useful. The search did not locate a pre-cutoff machine-teaching paper that used this exact operational four-way taxonomy.

### 4.4 Retrospective revaluation is real prior art for the broad “later evidence changes earlier evidence” idea

**Work:** M. E. Le Pelley and I. P. L. McLaren, **“Retrospective Revaluation in Humans: Learning or Memory?”** _Quarterly Journal of Experimental Psychology_ 54B (2001).

- first published: **2001-11**;
- DOI: <https://doi.org/10.1080/713932762>.

Retrospective revaluation changes the effective relation/strength assigned to a cue on later trials in which that cue is absent; the paper evaluates whether the effect reflects new learning or changed retrievability in memory.

**Work:** Jan De Houwer and Tom Beckers, **“Higher-Order Retrospective Revaluation in Human Causal Learning.”** _Quarterly Journal of Experimental Psychology_ 55B (2002).

- first published: **2002-04**;
- DOI: <https://doi.org/10.1080/02724990143000216>.

Participants retrospectively adjust the assessed relation of a target cue to an outcome after receiving later information about the causal status of a competing cue, including second- and third-order effects.

**Work:** İrem Nazlı, Andrea Ferrari, Christoph Huber-Huber, Floris P. de Lange, **“Forward and backward blocking in statistical learning.”** _PLOS ONE_ 19(8), 2024.

- publication year: **2024**;
- DOI: <https://doi.org/10.1371/journal.pone.0306797>.

The study reports backward blocking in visual statistical learning and explicitly interprets it as evidence for retrospective revaluation.

**Compared claim:** C3.

**Classification:** `prior_art` for the broad phenomenon that **later observations can change the learned/retrievable significance of earlier cues**; `partial_prior_art` for the paper's learner-relative temporary-opacity claim.

**What remains different:** the paper does not merely ask whether a judgment about `z_i` changes. It proposes the operational score

`R_{i,t} = L_future(M_t^{-z_i}) - L_future(M_t)`

after later decoding structure is available. The causal question is whether the earlier datum now contributes to **held-out future prediction/task performance** when removed from the same completed history. This exact post-unlock ablation criterion was not located in the pre-cutoff literature searched.

This materially narrows C3: “later evidence can make earlier evidence matter differently” is not new; the candidate contribution is the **pedagogical, predictive, ablation-based operationalization** of a specific earlier event's newly usable information.

### 4.5 “Learner as predictive-invariant extractor” has deep predictive-representation prior art

**Work:** Cosma Rohilla Shalizi and James P. Crutchfield, **“Computational Mechanics: Pattern and Prediction, Structure and Simplicity.”** arXiv v1 **1999-07-13**.

- arXiv: <https://arxiv.org/abs/cond-mat/9907176>.

The causal-state representation is shown to be a **minimal representation consistent with accurate prediction**, with optimality and uniqueness properties.

**Work:** William Bialek, Ilya Nemenman, Naftali Tishby, **“Predictability, complexity and learning.”** arXiv v1 **2000-07-20**; journal version 2001.

- arXiv: <https://arxiv.org/abs/physics/0007070>.

It defines predictive information as mutual information between past and future and connects predictability, learning and complexity.

**Work:** Susanne Still, **“Information Bottleneck Approach to Predictive Inference.”** _Entropy_ 16(2), 2014.

- published: **2014-02-17**;
- DOI: <https://doi.org/10.3390/e16020968>.

The framework compresses past experience into a summary that retains information useful for predicting future experience; it explicitly describes the objective as finding the **most compact model with a desired predictive power**, discarding nonpredictive information.

**Compared claims:** C5 and the predictive part of C7.

**Classification:** `prior_art` for the core principle “prefer compact representations that preserve future-predictive information over arbitrary retrospective fit”; `partial_prior_art` for the paper's compound quality functional adding task execution, transfer, perturbation/intervention stability and representational cost.

Thus the novelty boundary cannot be “smallest stable representation sufficient for prediction.” The contribution, if validated, would be its use as the **acceptance test for emergent symbols inside a pedagogical interaction** and the coupling to C3/C6, not predictive sufficiency itself.

### 4.6 Structured irregularity decomposes into established discriminative teaching plus a narrower composition

C4 makes two separable moves:

1. examples should efficiently discriminate among live hypotheses / resolve important ambiguity;
2. locally diverse or surprising examples can still be easy to learn if governed by a stable low-complexity higher-order rule.

The first move is central to machine teaching and pedagogical sampling: optimal examples depend on how they alter the learner's hypothesis distribution rather than on surface regularity. Shafto et al. and Zhu already supply that foundation.

A more direct recent pedagogical result is:

**Work:** Avery Ham, Olivia Zhao, Thomas L. Griffiths, Caren M. Vélez, **“Teaching Recombinable Motifs Through Simple Examples.”** _Cognitive Science_ (2025).

- DOI: <https://doi.org/10.1111/cogs.70103>.

The authors find that human teachers favor simple examples when conveying recombinable motifs; a pedagogical-sampling model explains the behavior better than simplicity as a standalone heuristic, and learners recover motifs better from such examples.

**Compared claim:** C4.

**Classification:** `prior_art` for learner-aware example selection/discrimination and for simplicity as a pedagogical property; `partial_prior_art` for the exact **high-local-irregularity + low-complexity meta-grammar** conjunction.

The search did not locate a pre-cutoff work that states the same tradeoff in the paper's form: maximize useful local discrimination/diversity while minimizing the complexity of the reusable interpretive grammar, then test that grammar by future prediction and transfer. That conjunction is a plausible hypothesis to test, but it should not be presented as if pedagogical discriminativeness or simple explanatory examples were themselves new.

### 4.7 The noise/opacity/concealment taxonomy is best treated as a synthesis, not four new primitives

The ingredients of C6 have mature homes in different literatures:

- exogenous noise — communication/statistical learning;
- latent or initially unavailable interpretation — latent-variable/sequential inference and retrospective revaluation;
- accidental pattern — generalization/overfitting and predictive validation;
- concealment — coding/cryptographic communication where the intended recipient has a decoding channel that another observer lacks.

What the present paper adds is a **single learner-relative decision problem**: do not classify an unexplained event from appearance; wait for evidence from held-out prediction, intervention/permutation, or a finite decoding horizon.

**Classification:** `adjacent_prior_work` / `partial_prior_art` for the taxonomy as a package. No pre-cutoff source located in this run materially anticipated the exact four-way operational taxonomy in a machine-teaching channel.

This is a useful organizing distinction, but the audit does not find evidence sufficient to claim priority for inventing the constituent categories.

## 5. Post-cutoff search

Targeted searches from the cutoff **2026-07-31 14:21:45 UTC** through **2026-09-18** used the exact title, `progressive decodability`, `structured irregularity`, `retrospective gain`, `temporary opacity`, learner-relative noise, and combinations of `machine teaching + retrospective + prediction + later decoding`.

No post-cutoff candidate located in this run materially reproduces the full conjunction C2+C3+C4+C6. Therefore this audit does **not** assign `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` to any work.

A few later papers use words such as “retrospective,” “progressive decoding,” or adaptive curriculum in unrelated senses. They were excluded rather than upgraded on lexical similarity. This is a bounded negative result, not evidence that no later overlapping work exists.

## 6. Claim-by-claim classification after the audit

| Claim | Classification | Reason |
|---|---|---|
| C1 learner-relative optimal teaching | `prior_art` | machine teaching and pedagogical sampling already optimize examples conditional on learner/target models |
| C2 staged curriculum / learning-progress optimization | `prior_art` generically; `partial_prior_art` for progressive decodability | curriculum learning, POMDP teaching, sequential teaching and learning-progress teachers predate cutoff |
| C3 later evidence changes earlier evidence | `prior_art` as broad phenomenon; `partial_prior_art` for the operational claim | retrospective revaluation/backward blocking predate cutoff; exact held-out post-unlock ablation not located |
| C4 structured irregularity | `partial_prior_art` | discriminative pedagogical sampling and simple-example teaching are established; exact local-diversity / low-complexity-meta-grammar tradeoff not located |
| C5 compact predictive invariant | `prior_art` | causal states, predictive information and predictive information bottleneck already optimize compact future-predictive representations |
| C6 noise / opacity / accident / concealment taxonomy | `adjacent_prior_work` / `partial_prior_art` | constituent ideas exist; exact learner-relative operational package not located |
| C7 primitive next-bit score with noncanonical internal symbols | `partial_prior_art` | external predictive objectives with latent/minimal representations are established; coupling to self-constructed pedagogical symbols is the narrower specialization |

## 7. Revised novelty boundary

After this audit, the paper should **not** rely on the following as standalone novelty claims:

- teaching is learner-relative;
- curricula should be staged or adapt to learning progress;
- teachers should choose informative/discriminative examples;
- later information can retrospectively change the significance of earlier cues;
- compact representations should preserve information about the future;
- teaching under noisy/imperfect knowledge is possible and nontrivial.

The narrower unresolved combination is:

> a noisy pedagogical interaction in which apparent irregularities are classified relative to the learner and decoding horizon; curricula are evaluated for progressive decodability; and an earlier event counts as temporarily opaque rather than noise only when later-acquired structure makes that **same earlier event causally useful for held-out prediction or task behavior under post-hoc ablation**, while the teacher is simultaneously optimized for high discriminative information under a reusable low-complexity meta-grammar.

This run **did not locate a material pre-cutoff antecedent for that full conjunction** after searches across machine teaching, curriculum learning, pedagogical reasoning, predictive representations, and retrospective revaluation. This is a bounded search statement, not “we are first.”

## 8. Experimental consequences

The audit changes what would count as a discriminating experiment. A future implementation should not compare only against random curricula. At minimum it should include:

1. **standard curriculum baseline** — fixed easy-to-hard order;
2. **learner-state/POMDP or learning-progress teacher** — captures C1/C2 prior art;
3. **pedagogical-sampling / information-gain teacher** — captures discriminative example selection;
4. **predictive-bottleneck / compact predictive-state learner** — captures C5 prior art;
5. **retrospective-revaluation-compatible learner without explicit post-unlock ablation objective** — isolates C3;
6. **full structured-irregularity curriculum** — high local diversity under controlled meta-grammar complexity;
7. **ablation of the earlier opaque event only after the decoding structure is learned** — the decisive `R_{i,t}` test.

The key falsifier is strong: if later “reinterpretation” survives removal of the supposedly unlocked earlier event, then the event was not shown to have gained retrospective predictive value. Conversely, if any ordinary sequential curriculum or predictive-state baseline produces the same `R_{i,t}` pattern under equal budget, the proposed mechanism does not require the new framework.

A second useful axis should independently manipulate **local surprise/diversity** and **meta-grammar complexity**. That prevents a positive result from collapsing into the classical claim that informative examples or simpler examples are easier to teach.

## 9. Epistemic change introduced by this audit

This audit narrows the paper in three substantive ways:

1. **learner-relative optimal pedagogy moves from candidate novelty to established prior art**;
2. **retrospective reinterpretation moves from a broad candidate novelty to a specific operational claim**, because retrospective revaluation predates the paper by decades;
3. **predictive invariance/minimality moves to background machinery**, leaving the scientifically sharper question of whether later representational acquisition makes specific earlier observations newly useful under held-out causal ablation.

The result is a smaller but more falsifiable research claim. The paper's strongest path is not a new theory of curricula in general; it is a bridge between machine teaching and retrospective revaluation with a concrete predictive-ablation criterion for distinguishing temporary opacity from noise.

## 10. Search ledger / primary records

Primary or near-primary records used for classification:

- ours, PR #241: <https://github.com/franklinbaldo/papers/pull/241>
- ours, initial claim-bearing commit: <https://github.com/franklinbaldo/papers/commit/d31fcfc19406c63f2dddfc55a6e3f96c585d0a3c>
- Zhu 2015, AAAI: <https://ojs.aaai.org/index.php/AAAI/article/view/9761>
- Shafto, Goodman & Griffiths 2014: <https://doi.org/10.1016/j.cogpsych.2013.12.004>
- Bengio et al. 2009: <https://doi.org/10.1145/1553374.1553380>
- Zhu, Liu & Lopes 2017, IJCAI: <https://www.ijcai.org/proceedings/2017/502>
- Peltola et al. 2018: <https://arxiv.org/abs/1809.02869>
- Portelas et al. 2020: <https://proceedings.mlr.press/v100/portelas20a.html>
- Rafferty et al. 2016: <https://doi.org/10.1111/cogs.12290>
- Devidze et al. 2020, IJCAI: <https://www.ijcai.org/proceedings/2020/367>
- Yang et al. 2026, ZPD Detector: <https://arxiv.org/abs/2601.10986>
- Le Pelley & McLaren 2001: <https://doi.org/10.1080/713932762>
- De Houwer & Beckers 2002: <https://doi.org/10.1080/02724990143000216>
- Nazlı et al. 2024: <https://doi.org/10.1371/journal.pone.0306797>
- Shalizi & Crutchfield 1999: <https://arxiv.org/abs/cond-mat/9907176>
- Bialek, Nemenman & Tishby 2000/2001: <https://arxiv.org/abs/physics/0007070>
- Still 2014: <https://doi.org/10.3390/e16020968>
- Ham et al. 2025: <https://doi.org/10.1111/cogs.70103>

## 11. Open search questions

The following remain worth revisiting in later runs rather than repeating the same generic queries:

- machine-teaching work that explicitly distinguishes **recoverable code not yet learned** from stochastic corruption;
- Bayesian/latent-program learning with a formal analogue of `R_{i,t}` where later rule induction increases the counterfactual held-out value of an earlier datum;
- information-theoretic curricula optimizing both **example surprise** and **description length of the teacher policy**;
- work after 2026-07-31 that combines retrospective credit assignment with pedagogical decoding rather than merely using “retrospective” for self-reflection or hindsight replay.

Until such a source is located, the full conjunction remains **unresolved by this search**, not established as globally novel.
