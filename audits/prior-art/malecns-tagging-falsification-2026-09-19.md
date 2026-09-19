---
type: "Audit Report"
title: "MaleCNS legal tagging adversarial validity audit — 2026-09-19"
description: "Claim-level prior-art and falsification audit for the MaleCNS frozen-reservoir legal sequence-tagging hypothesis, separating temporal priority from current truth status."
tags: [malecns, prior-art, falsification, contrary-evidence, reservoir-computing, sequence-tagging, legal-nlp]
timestamp: 2026-09-19T00:57:00-04:00
---

# MaleCNS legal tagging adversarial validity audit — 2026-09-19

> **Status:** adversarial follow-up to `audits/prior-art/malecns-connectome-reservoir-tagging-2026-09-17.md`. This round adds an explicit falsification axis, corrects one missed pre-cutoff MaleCNS-language predecessor, and separates **priority** from **truth status**. It does not infer copying, plagiarism, bad faith, or causal dependence from chronology or technical similarity.

## 1. Scope and claim-specific cutoff

The paper under audit is `malecns_connectome_reservoir_tagging.md`. The central empirical question is:

> Given the same text interface, trainable adapter/readout, data windows and optimisation, does a frozen recurrent reservoir constrained by MaleCNS wiring improve byte-level legal sequence tagging relative to topology-destroying or simpler controls?

The earliest public GitHub object located that already contains this question, the completed five-seed null result, and the paired control design is commit [`f4a3eca169b75c38c968702bbc51aa9120ae5039`](https://github.com/franklinbaldo/papers/commit/f4a3eca169b75c38c968702bbc51aa9120ae5039), timestamped **2026-09-13 17:06:01 UTC**. PR #442 was opened later with that commit as its head.

**Claim-specific cutoff: 2026-09-13 17:06:01 UTC.**

Anything first made public after this instant is not prior art against the claim. Post-cutoff work remains relevant to truth status, convergence and later overlap.

## 2. Claim decomposition and explicit falsifiers

### H1 — Higher-order MaleCNS topology adds task-relevant signal

Operational claim: after matching trainable interface, data and optimisation, the biological topology should outperform a directed degree-preserving shuffled recurrent null by a practically meaningful margin on untouched data.

**Would falsify or materially weaken H1:**

- no stable held-out improvement over degree-preserving shuffled wiring across paired seeds;
- an equal-capacity simpler recurrent/non-recurrent model matches or exceeds the biological condition;
- any apparent gain disappears under reasonable choices of recurrent dynamics;
- the same apparent gain is reproduced by low-order statistics preserved in the null.

### H2 — Recurrent context itself helps byte-level legal tagging

Operational claim: recurrent state should improve held-out tagging over byte-only and a cheap conventional sequential baseline.

**Would falsify or materially weaken H2:** no practically meaningful held-out improvement over byte-only and parameter/compute-matched GRU, temporal CNN, or comparable sequential baseline.

### H3 — The v1 null may be substantially explained by undertraining

Operational claim: the three-epoch endpoint may have stopped before the adapter/readout reached their useful regime.

**Would falsify or materially weaken H3:** after the predeclared longer-training/model-selection diagnostic, best checkpoints still show no consistent paired MaleCNS advantage, or the shuffled/simple baselines improve equally or more.

The falling training loss in one v1 seed is evidence that optimisation had not stopped, but it is **not evidence that additional optimisation selectively benefits biological topology**.

### H4 — Scaling the biological reservoir is scientifically justified by topology, not merely capacity

**Would falsify or materially weaken H4:** improvements with reservoir size that also appear under shuffled topology; improvements attributable to larger trainable interfaces; or external evidence showing that biological-topology effects are strongly regime-specific and absent under nearby dynamics.

## 3. Search protocol

This round deliberately used adversarial as well as overlap queries. Representative searches included:

- `Drosophila connectome reservoir rewired null no advantage`
- `fruit fly connectome reservoir memory rewired p 0.11`
- `MaleCNS language direct input control no advantage`
- `connectome reservoir spectral radius underperform random`
- `biological topology reservoir no benefit random baseline`
- `connectome reservoir failure negative null result`
- `random reservoirs rule biological connectivity Drosophila`
- `MaleCNS language degree matched shuffled wiring`
- `MaleCNS reservoir TinyStories shuffled control`
- `connectome reservoir robustness rather than accuracy`
- post-cutoff variants for `MaleCNS`, `language`, `reservoir`, `tagging`, `shuffled`, and `degree-matched`.

Sources checked included Nature Communications, bioRxiv, MDPI/Preprints.org, PubMed, Zenodo, Hugging Face model cards, GitHub repository history, institutional publication pages, and current web search. Primary sources were preferred for dates and results.

## 4. Novelty / overlap findings

### 4.1 nanoFLY was already public before our cutoff

**Work:** Igor Kuzmin, `igorktech/nanoFLY`.

**First verified relevant public object:** parentless commit [`179a148ce8530b6d2f3538069027d6de2a565900`](https://github.com/igorktech/nanoFLY/commit/179a148ce8530b6d2f3538069027d6de2a565900), **2026-09-12 20:54:35 UTC**, about 20 hours before our cutoff.

**Classification:** `partial_prior_art`.

The initial public README already described a language model whose recurrent layer is measured **MaleCNS v1.0** wiring and stated that conclusions require controls using the same graph with wiring shuffled at matched degrees plus a dense equal-capacity baseline. That materially anticipates the broad experimental logic **MaleCNS + language + frozen measured recurrent graph + degree-matched wiring control**.

It does **not** anticipate the exact package in our paper: UTF-8 byte-level Portuguese legal span tagging, `resultado` extraction, the exact directed weight-multiset-preserving null, paired five-seed protocol, and byte-only local baseline.

**Revision to the 2026-09-17 audit:** the exact narrow package remains unlocated before the cutoff, but the matched-degree-control idea in a MaleCNS language system was closer and earlier than that audit recorded. The relevant novelty boundary is narrower than “MaleCNS language with a degree-preserving control.”

### 4.2 Previously established components remain prior art

The previous audit remains valid that connectome reservoirs, Drosophila reservoirs, rewired/randomized controls, reservoir NLP sequence labeling, and MaleCNS language reservoirs all predate our cutoff. This round does not reclassify those components; it strengthens the nearest-neighbour record through nanoFLY's pre-cutoff history.

## 5. Contrary evidence, nulls and boundary conditions

### 5.1 Our own v1 result is a direct null for H1

**Classification:** `failed_replication_or_null` for H1 under the frozen v1 regime.

**Strength:** `moderate`.

The five paired seeds reported:

- MaleCNS validation F1: `0.2753 ± 0.0682`;
- degree-preserving shuffle: `0.2782 ± 0.0610`;
- MaleCNS minus shuffle: `-0.00292 ± 0.02840`;
- byte-only: `0.2727 ± 0.0562`.

This is a direct test of the topology claim and does not show an advantage. Strength is not rated `strong` because the legal dataset is tiny, validation has only nine windows, training stops at three epochs, and the current validation split is developmental rather than terminal.

**Target attacked:** topology advantage in this task/regime.

**Required change:** `downgrade_confidence` in H1; `no_change` to the paper's current v0.1 conclusion because it already reports the null honestly.

### 5.2 conn2res: the fruit-fly connectome did not beat rewired nulls on peak memory capacity

**Work:** Suárez et al., *Connectome-based reservoir computing with the conn2res toolbox*, Nature Communications (2024).

**Classification:** `failed_replication_or_null` for the broader proposition that fruit-fly empirical topology should generically outperform degree-preserving rewired topology.

**Strength:** `moderate-to-strong`.

The cross-species experiment compares each empirical connectome with **500 rewired null networks**. At peak memory capacity, mouse, rat and macaque reservoirs significantly outperform rewired nulls, but the **fruit fly does not** (`p = 0.11`, reported at `alpha_peak = 0.9`).

This is a stronger topology-null design than an anecdotal failure, but it is not the same MaleCNS release, task, resolution or dynamics as our legal tagger.

**Target attacked:** generalization of a fly-topology advantage; not the exact byte-level legal claim.

**Required change:** `add_boundary_condition`; `downgrade_confidence` in generic expectations that fruit-fly topology should win merely because it is biological.

Primary source: <https://www.nature.com/articles/s41467-024-44900-4>

### 5.3 Flies Are All You Need: MaleCNS participates in language modeling but a simpler control is better

**Work:** Codex & Alex Wormuth, *Flies Are All You Need*, first published **2026-09-11**, before our cutoff.

**Classification:** `contrary_evidence` for a broad MaleCNS-language architectural-advantage hypothesis; `partial_prior_art` for MaleCNS + language + frozen reservoir + trained readout.

**Strength:** `strong` for the experiment's own architecture; `moderate` when transferred to our exact legal tagging hypothesis.

On 32 newly held-out conversations, the fly readout improves negative log-likelihood over a frozen language backbone, but a **parameter-matched direct-input readout is better in all three fitted seeds**. Reported fly-minus-direct-input NLL is `+0.000488` nats/token, with a descriptive paired bootstrap interval `+0.00000502` to `+0.00104`; lower is better. The authors explicitly conclude that graph participation is demonstrated but fly-specific architectural advantage is not.

The same work proves that its chosen recurrence contracts dependence on initial state by at most `0.6^t`, demonstrating that adding more anatomical nodes does not automatically create long-lived context under a strongly contracting numerical recurrence.

**Target attacked:** the mechanism-level intuition that routing language through MaleCNS should itself yield a useful inductive bias; also the assumption that reservoir size implies long memory.

**Required change:** `add_boundary_condition`, `add_control`, and `downgrade_confidence`. In particular, the v2 “undertraining” explanation must remain one hypothesis among several, not the privileged default explanation for our null.

Primary source: <https://artificialscientific.com/papers/flies-are-all-you-need>

### 5.4 Costi et al.: connectome advantage reverses with dynamical regime

**Work:** Costi et al., *The Drosophila Connectome as a Computational Reservoir for Time-Series Prediction* (preprint 2025-04-15; Biomimetics 2025).

**Classification:** `boundary_condition`.

**Strength:** `strong` for the proposition that connectome advantage is dynamics-dependent.

At spectral radius `0.99`, the biomimetic reservoirs outperform classical controls in the tested setup. At lower spectral radii the conditions can become equivalent or reverse; at spectral radius `0.25`, the classical ESN is reported to perform consistently better with few exceptions.

This means a null or positive result at one recurrent gain/spectral regime cannot safely be generalized to “the connectome topology works/does not work.” Dynamics are part of the estimand.

**Target attacked:** generalization and mechanism, not the existence of our v1 result.

**Required change:** `add_boundary_condition`. For a future confirmatory topology claim, add a predeclared small dynamics-sensitivity control rather than interpreting one engineered recurrence as a property of MaleCNS itself.

Primary source: <https://www.mdpi.com/2313-7673/10/5/341>

### 5.5 McAllister et al.: biological wiring may buy robustness rather than raw accuracy

**Work:** McAllister, Houghton, Wade & O'Donnell, *Non-random brain connectome wiring enables robust and efficient neural network function under high sparsity*, bioRxiv, posted **2026-04-01**.

**Classification:** `boundary_condition` and alternative mechanism.

**Strength:** `moderate` for our hypothesis because the tasks and connectome implementation differ.

Across eight cognitive tasks, Drosophila-connectome ESNs are reported as especially robust to neuron loss and hyperparameter variation compared with sparsity-matched random wiring; the authors identify excess self-recurrency as sufficient to explain enhanced robustness. The result suggests a plausible alternative to “better mean task score”: biological wiring may primarily improve robustness, efficiency or stability.

**Target attacked:** our choice of raw F1 advantage as the only interesting biological endpoint.

**Required change:** `add_control` only if a future paper broadens its biological-inductive-bias claim. The current v0.1 legal-tagging paper need not be rewritten around robustness because it asks a narrower performance question.

Primary source: <https://www.biorxiv.org/content/10.64898/2026.03.30.715411v1>

### 5.6 Earlier poster evidence also warned that simple/random reservoirs can match biology

**Work:** McAllister et al., *Random and biological network connectivity for reservoir computing: Random Reservoirs Rule! (at Remembering)*, UK Neural Computation 2024.

**Classification:** `adjacent_prior_work` / `boundary_condition`.

**Strength:** `weak-to-moderate` in this audit because the accessible abstract, not a full numeric paper, is the primary evidence reviewed here.

The authors explicitly frame the comparison around biological connectomes versus varying degrees of randomization and state that simpler topologies often perform equally well as more complex networks on prediction tasks.

**Required change:** no independent change beyond the stronger sources above.

Zenodo: <https://zenodo.org/records/13303677>

## 6. Post-cutoff convergence and conflicting evidence

### 6.1 nanoFLY later reports a positive real-wiring result — but the project itself predates us

The nanoFLY code/design was already public before our cutoff, so its existence is `partial_prior_art`. Its **published English checkpoint/result** appeared after our cutoff and is therefore not prior art for the result itself.

**Classification of the later result:** `later_independent` plus `boundary_condition` for truth status.

The current `nanofly-decoder-en` model card reports a held-out TinyStories comparison with identical data, recipe, seed and budget in which only recurrent wiring differs:

- degree-matched shuffled wiring: validation loss `1.979`;
- real MaleCNS connectome: validation loss `1.933`;
- real connectome with trainable synapse strengths: `1.913`.

The model card says the degree-matched shuffle preserves each neuron's in/out degree, transmitter signs and Dale's law while randomizing pairings; the real-wiring margin (`0.046` nats) is reported across all ten intermediate evaluations. However, it is **one seed per condition** and all runs were still improving, so the author explicitly labels the margins indicative rather than significant.

This later positive result conflicts with the null direction of our small legal-tagging baseline and with the simpler-control result in *Flies Are All You Need*, but the conflict is scientifically useful rather than paradoxical: tasks, graph subsets, trainable dynamics, input mappings, objectives and capacity differ substantially.

Because nanoFLY's public project predates our paper, there is affirmative temporal evidence for independent development. This round therefore does **not** label the result `later_non_citing` even though no citation to our paper was located in the model card. `later_independent` is the better classification.

Primary model card: <https://huggingface.co/igorktech/nanofly-decoder-en>

### 6.2 No other material post-cutoff exact overlap located

No other work first made public after our cutoff was located that reproduces the exact **byte-level Portuguese legal span tagging + MaleCNS + paired degree-preserving shuffle + byte-only baseline** package. Absence from these searches is not evidence of nonexistence.

## 7. Priority status versus truth status

### Priority

The 2026-09-17 audit's narrow conclusion needs one refinement: nanoFLY shows that, before our cutoff, a public MaleCNS language-model project had already specified the need for **degree-matched shuffled wiring and dense controls**. The defensible unresolved combination is therefore narrower:

- byte-level input;
- Portuguese legal span tagging rather than next-token generation;
- the exact directed degree-preserving, recurrent-weight-multiset-preserving null;
- the non-recurrent byte-only baseline;
- paired five-seed data/initialization/optimization;
- the archived negative result and provenance package.

No source in this round was located before the cutoff with that entire combination. This is a bounded negative search result, not a priority claim.

### Truth status

The truth-status evidence is more sobering than the novelty status:

1. our own exact v1 test is null;
2. conn2res reports no significant fruit-fly peak-memory advantage over rewired nulls;
3. *Flies Are All You Need* finds a simpler parameter-matched direct-input control slightly better than the MaleCNS route;
4. Costi et al. show connectome advantage can reverse when recurrent dynamics change;
5. McAllister et al. suggest the biological benefit may manifest more in robustness/stability than mean score;
6. nanoFLY later reports the opposite direction on TinyStories with a much larger reservoir and trainable per-neuron dynamics, but only one seed per condition.

The combined evidence does **not** justify `abandon_hypothesis`: there is genuine conflicting evidence across regimes. It does justify **lower prior confidence in a generic topology advantage** and requires a stronger test before scaling or biological interpretation.

## 8. Required scientific action

For the current archived v0.1 paper:

- baseline result: `no_change` — it already reports the null honestly;
- topology-advantage hypothesis: `downgrade_confidence`;
- interpretation of undertraining: `narrow_claim` — longer training is one diagnostic, not the default causal explanation;
- future confirmatory design: `add_control` and `add_boundary_condition`.

A defensible confirmatory stopping rule is:

> Freeze the selected training regime, evaluate on untouched `test.jsonl`, and require MaleCNS to beat both the degree-preserving shuffle and a conventional sequential baseline by a predeclared practically meaningful margin across paired seeds. If it does not, retire the MaleCNS-topology-advantage claim for this task/version rather than escalating reservoir size as the next explanation.

Because Costi et al. demonstrate regime reversal, a subsequent topology-confirmatory run should also include a small predeclared dynamics-sensitivity check (for example, recurrent gain/leak regimes) or explicitly limit the claim to the frozen v1 dynamics.

## 9. Search negatives and uncertainty

This round did **not** locate:

- a pre-cutoff replication of our exact legal byte-span task;
- a pre-cutoff MaleCNS legal-NLP result;
- a multi-seed nanoFLY degree-matched result;
- a post-cutoff independent reproduction of the exact legal-tagging package;
- positive evidence of causal dependence by any later project on our paper.

“Not located” is a search outcome, not proof that no such source exists.

## 10. Revision record

This audit preserves rather than overwrites the 2026-09-17 prior-art audit. The material epistemic revision is twofold:

1. **priority refinement:** nanoFLY's first public commit predates our claim and already states the MaleCNS-language plus degree-matched-control logic;
2. **validity refinement:** adversarial evidence makes a generic biological-topology advantage a lower-confidence hypothesis than the earlier novelty-only audit conveyed, while later nanoFLY evidence shows that the correct boundary is regime/task dependent rather than a universal null.
