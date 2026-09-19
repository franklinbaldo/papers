---
type: "Audit Report"
title: "MaleCNS legal tagging adversarial validity audit — 2026-09-19"
description: "Claim-level prior-art and falsification audit for the MaleCNS frozen-reservoir legal sequence-tagging hypothesis, separating temporal priority from current truth status."
tags: [malecns, prior-art, falsification, contrary-evidence, reservoir-computing, sequence-tagging, legal-nlp]
timestamp: 2026-09-19T00:57:00-04:00
---

# MaleCNS legal tagging adversarial validity audit — 2026-09-19

> **Status:** adversarial follow-up to `audits/prior-art/malecns-connectome-reservoir-tagging-2026-09-17.md`. This round adds an explicit falsification axis, corrects one missed pre-cutoff MaleCNS-language predecessor, and separates **priority** from **truth status**. Chronology and similarity alone are not evidence of copying, derivation, plagiarism or bad faith.

## 1. Claim-specific cutoff

The paper under audit is `malecns_connectome_reservoir_tagging.md`. Its central empirical question is whether, after matching the text interface, trainable adapter/readout, data windows and optimisation, a frozen recurrent reservoir constrained by MaleCNS wiring improves byte-level legal sequence tagging relative to topology-destroying or simpler controls.

The earliest public GitHub object located that already contains this question, the completed five-seed null result and the paired control design is commit [`f4a3eca169b75c38c968702bbc51aa9120ae5039`](https://github.com/franklinbaldo/papers/commit/f4a3eca169b75c38c968702bbc51aa9120ae5039), timestamped **2026-09-13 17:06:01 UTC**. PR #442 was opened later with that commit as its head.

**Claim-specific cutoff: 2026-09-13 17:06:01 UTC.** Anything first made public after this instant is not prior art against the claim. Later work remains relevant to truth status and convergence.

## 2. Claims and explicit falsifiers

### H1 — Higher-order MaleCNS topology adds task-relevant signal

The biological topology should outperform a directed degree-preserving shuffled recurrent null by a practically meaningful margin on untouched data.

**Would falsify/materially weaken H1:** no stable held-out improvement over shuffled wiring across paired seeds; a simpler equal-capacity model matches or exceeds it; the effect disappears under reasonable recurrent dynamics; or the same gain is reproduced by low-order graph statistics preserved in the null.

### H2 — Recurrent context itself helps byte-level legal tagging

**Would falsify/materially weaken H2:** no practically meaningful held-out improvement over byte-only and a parameter/compute-matched conventional sequential baseline such as GRU or temporal CNN.

### H3 — The v1 null may be substantially explained by undertraining

**Would falsify/materially weaken H3:** the preregistered longer-training/best-checkpoint diagnostic still shows no consistent paired MaleCNS gain, or shuffled/simple controls improve equally or more. Falling training loss shows optimisation had not stopped; it does **not** show that additional optimisation selectively benefits biological topology.

### H4 — Scaling the biological reservoir is justified by topology rather than capacity

**Would falsify/materially weaken H4:** scale gains also appear under shuffled topology, are explained by a larger trainable interface, or disappear/invert under nearby dynamical regimes.

## 3. Search protocol

Representative adversarial and overlap queries:

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

Sources checked included Nature Communications, bioRxiv, MDPI/Biomimetics, PubMed, Zenodo, Hugging Face model cards, GitHub history, institutional publication pages, and current web search. Primary sources were preferred for dates and results.

## 4. Novelty / overlap findings

### 4.1 nanoFLY predates our cutoff

**Work:** Igor Kuzmin, [`igorktech/nanoFLY`](https://github.com/igorktech/nanoFLY).

**First verified relevant public object:** parentless commit [`179a148ce8530b6d2f3538069027d6de2a565900`](https://github.com/igorktech/nanoFLY/commit/179a148ce8530b6d2f3538069027d6de2a565900), **2026-09-12 20:54:35 UTC**, about 20 hours before our cutoff.

**Classification:** `partial_prior_art`.

The initial public README already described a language model whose recurrent layer follows measured **MaleCNS v1.0** wiring and explicitly stated that a topology claim requires controls using the same graph with shuffled wiring at matched degrees plus a dense equal-capacity baseline. This materially anticipates the broad experimental logic **MaleCNS + language + measured recurrent graph + degree-matched wiring control**.

It does **not** anticipate our exact package: UTF-8 byte-level Portuguese legal span tagging, `resultado` extraction, the exact directed recurrent-weight-multiset-preserving null, paired five-seed protocol, and byte-only local baseline.

**Revision to the 2026-09-17 audit:** the exact narrow package remains unlocated before the cutoff, but MaleCNS-language plus a degree-matched shuffled-wiring control was closer and earlier than that audit recorded.

## 5. Contrary evidence, nulls and boundary conditions

### 5.1 Our v1 result is a direct null for H1

**Classification:** `failed_replication_or_null`.  
**Strength:** `moderate`.

Reported validation results:

- MaleCNS F1: `0.2753 ± 0.0682`;
- degree-preserving shuffle: `0.2782 ± 0.0610`;
- MaleCNS minus shuffle: `-0.00292 ± 0.02840`;
- byte-only: `0.2727 ± 0.0562`.

This direct test does not show a topology advantage. It is not `strong` falsification because the corpus is small, validation has only nine windows, training stops at three epochs, and validation is developmental rather than terminal.

**Target attacked:** topology advantage in this task/regime.  
**Required change:** `downgrade_confidence`; `no_change` to the archived v0.1 result because it already reports the null honestly.

### 5.2 conn2res: fruit-fly topology does not significantly beat rewired nulls at peak memory

**Work:** Suárez et al., *Connectome-based reservoir computing with the conn2res toolbox*, Nature Communications (2024).  
**Classification:** `failed_replication_or_null` for the broader proposition that fruit-fly empirical topology generically beats degree-preserving rewired topology.  
**Strength:** `moderate-to-strong`.

Their cross-species experiment compares each empirical connectome with **500 rewired null networks**. Mouse, rat and macaque significantly outperform rewired nulls at peak memory capacity; the **fruit fly does not** (`p = 0.11`, reported at `alpha_peak = 0.9`). The task, graph resolution and dynamics differ from ours, so this is a boundary on generalization rather than a direct falsification of legal tagging.

**Required change:** `add_boundary_condition`; `downgrade_confidence` in generic fly-topology expectations.

Primary source: <https://www.nature.com/articles/s41467-024-44900-4>

### 5.3 Flies Are All You Need: a simpler parameter-matched control is better

**Work:** Codex & Alex Wormuth, *Flies Are All You Need*, first published **2026-09-11**, before our cutoff.  
**Classification:** `contrary_evidence` for a broad MaleCNS-language architectural-advantage hypothesis; `partial_prior_art` for MaleCNS + language + frozen reservoir + trained readout.  
**Strength:** `strong` for its own architecture; `moderate` transferred to our exact legal-tagging hypothesis.

On 32 newly held-out conversations, the fly readout improves NLL over a frozen language backbone, but a **parameter-matched direct-input readout is better in all three fitted seeds**. Reported fly-minus-direct-input NLL is `+0.000488` nats/token with descriptive paired-bootstrap interval `+0.00000502` to `+0.00104`; lower is better. The authors conclude that graph participation is demonstrated but fly-specific architectural advantage is not.

The same work proves that its chosen recurrence contracts dependence on initial state by at most `0.6^t`, showing that adding anatomical nodes does not automatically create long-lived context under strongly contracting numerical dynamics.

**Target attacked:** mechanism-level expectation that routing language through MaleCNS itself supplies a useful inductive bias; assumption that reservoir size implies long memory.  
**Required change:** `add_boundary_condition`, `add_control`, `downgrade_confidence`. The v2 undertraining explanation must remain one hypothesis among several, not the privileged default explanation for our null.

Primary source: <https://artificialscientific.com/papers/flies-are-all-you-need>

### 5.4 Costi et al.: connectome advantage reverses with dynamical regime

**Work:** Costi et al., *The Drosophila Connectome as a Computational Reservoir for Time-Series Prediction* (preprint 2025-04-15; Biomimetics 2025).  
**Classification:** `boundary_condition`.  
**Strength:** `strong` for dynamics dependence.

At spectral radius `0.99`, biomimetic reservoirs outperform classical controls in the tested setup. At lower spectral radii the conditions can become equivalent or reverse; at `0.25`, the classical ESN is reported to perform consistently better with few exceptions.

**Target attacked:** generalization and mechanism.  
**Required change:** `add_boundary_condition`. A future topology-confirmatory claim should include a small predeclared dynamics-sensitivity control or explicitly scope itself to the frozen recurrence.

Primary source: <https://www.mdpi.com/2313-7673/10/5/341>

### 5.5 McAllister et al.: biological wiring may buy robustness rather than raw accuracy

**Work:** McAllister, Houghton, Wade & O'Donnell, *Non-random brain connectome wiring enables robust and efficient neural network function under high sparsity*, bioRxiv, posted **2026-04-01**.  
**Classification:** `boundary_condition` and alternative mechanism.  
**Strength:** `moderate` for our hypothesis.

Across eight cognitive tasks, Drosophila-connectome ESNs are reported as especially robust to neuron loss and hyperparameter variation compared with sparsity-matched random wiring; excess self-recurrency is identified as sufficient to explain enhanced robustness. This suggests a plausible alternative to “better mean task score”: biological wiring may primarily improve robustness, efficiency or stability.

**Target attacked:** raw F1 advantage as the only biologically interesting endpoint.  
**Required change:** `add_control` only if a future paper broadens its biological-inductive-bias claim.

Primary source: <https://www.biorxiv.org/content/10.64898/2026.03.30.715411v1>

### 5.6 Earlier poster evidence also warns that simple/random reservoirs can match biology

**Work:** McAllister et al., *Random and biological network connectivity for reservoir computing: Random Reservoirs Rule! (at Remembering)*, UK Neural Computation 2024.  
**Classification:** `adjacent_prior_work` / `boundary_condition`.  
**Strength:** `weak-to-moderate` because this audit reviewed the accessible abstract rather than a full numeric article.

The authors explicitly compare biological connectomes against varying randomization and state that simpler topologies often perform equally well as more complex networks on prediction tasks.

Zenodo: <https://zenodo.org/records/13303677>

## 6. Post-cutoff convergence and conflicting evidence

### 6.1 nanoFLY later reports a positive real-wiring result

The nanoFLY project/design is pre-cutoff `partial_prior_art`; its later English checkpoint/result is therefore not prior art for our result.

**Classification of later result:** `later_independent` plus `boundary_condition` for truth status.

The current `nanofly-decoder-en` model card reports held-out TinyStories comparisons with identical data, recipe, seed and budget, changing only recurrent wiring:

- degree-matched shuffled wiring: validation loss `1.979`;
- real MaleCNS connectome: `1.933`;
- real connectome with trainable synapse strengths: `1.913`.

The shuffle preserves each neuron's in/out degree, transmitter signs and Dale's law while randomizing pairings. The real-wiring margin (`0.046` nats) appears at all ten intermediate evaluations. However, there is **one seed per condition**, all runs were still improving, and the author labels the margins indicative rather than significant.

This conflicts in direction with our small legal-tagging baseline and with the simpler-control result in *Flies Are All You Need*. The most conservative interpretation is task/dynamics/regime dependence.

Because nanoFLY's public project predates our paper, there is affirmative temporal evidence for independent development. This audit therefore does **not** label the later result `later_non_citing` even though no citation to our paper was located in the model card.

Primary model card: <https://huggingface.co/igorktech/nanofly-decoder-en>

### 6.2 No other exact post-cutoff overlap located

No other work first made public after our cutoff was located that reproduces the exact byte-level Portuguese legal span-tagging + MaleCNS + paired degree-preserving shuffle + byte-only baseline package. This is a negative search result, not evidence of nonexistence.

## 7. Priority versus truth status

### Priority

The 2026-09-17 audit needs one refinement: nanoFLY shows that, before our cutoff, a public MaleCNS language-model project had already specified the need for **degree-matched shuffled wiring and dense controls**. The unresolved combination is narrower:

- byte-level input;
- Portuguese legal span tagging rather than next-token generation;
- exact directed degree-preserving, recurrent-weight-multiset-preserving null;
- non-recurrent byte-only baseline;
- paired five-seed data/initialization/optimization;
- archived negative-result/provenance package.

No source in this round was located before the cutoff with that entire combination. This is a bounded negative search result, not a claim of primacy.

### Truth status

The truth-status evidence is mixed but materially lowers confidence in a generic topology advantage:

1. our exact v1 test is null;
2. conn2res finds no significant fruit-fly peak-memory advantage over rewired nulls;
3. *Flies Are All You Need* finds a simpler parameter-matched direct-input control slightly better than the MaleCNS route;
4. Costi et al. show connectome advantage can reverse when recurrence changes;
5. McAllister et al. suggest a biological benefit may appear in robustness/stability rather than mean score;
6. nanoFLY later reports the opposite direction on TinyStories with a larger reservoir and trainable per-neuron dynamics, but only one seed per condition.

This does **not** justify `abandon_hypothesis`; it does justify lower prior confidence and a stronger discriminating test before scaling or biological interpretation.

## 8. Required scientific action

For the archived v0.1 paper:

- baseline result: `no_change`;
- topology-advantage hypothesis: `downgrade_confidence`;
- undertraining explanation: `narrow_claim` — longer training is one diagnostic, not the default causal explanation;
- future confirmatory design: `add_control` and `add_boundary_condition`.

A defensible confirmatory stopping rule is:

> Freeze the selected training regime, evaluate on untouched `test.jsonl`, and require MaleCNS to beat both the degree-preserving shuffle and a conventional sequential baseline by a predeclared practically meaningful margin across paired seeds. If it does not, retire the MaleCNS-topology-advantage claim for this task/version rather than escalating reservoir size as the next explanation.

Because Costi et al. demonstrate regime reversal, a subsequent topology-confirmatory run should also include a small predeclared dynamics-sensitivity check (for example recurrent gain/leak regimes) or explicitly limit the claim to the frozen v1 dynamics.

## 9. Search negatives and uncertainty

This round did **not** locate:

- a pre-cutoff replication of the exact legal byte-span task;
- a pre-cutoff MaleCNS legal-NLP result matching our whole control package;
- a multi-seed nanoFLY degree-matched result;
- a post-cutoff independent reproduction of the exact legal-tagging package;
- positive evidence of causal dependence by any later project on our paper.

“Not located” is a search result, not proof of nonexistence.

## 10. Revision record

This audit preserves rather than overwrites the 2026-09-17 prior-art audit. The material revisions are:

1. **priority refinement:** nanoFLY's first public commit predates our claim and already states the MaleCNS-language plus degree-matched-control logic;
2. **validity refinement:** adversarial evidence makes a generic biological-topology advantage lower-confidence than a novelty-only audit suggests, while later nanoFLY evidence shows the boundary is regime/task dependent rather than a universal null.
