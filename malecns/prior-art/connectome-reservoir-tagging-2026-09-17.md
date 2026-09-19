---
type: "Audit Report"
title: "MaleCNS legal sequence-tagging prior-art audit — 2026-09-17"
description: "Dated prior-art audit of the MaleCNS frozen-reservoir legal sequence-tagging claim, with a claim-specific GitHub cutoff and explicit temporal classifications."
tags: [malecns, prior-art, reservoir-computing, sequence-tagging, legal-nlp]
timestamp: 2026-09-17T14:00:00-04:00
---

# MaleCNS legal sequence-tagging prior-art audit — 2026-09-17

> **Status:** first reproducible prior-art audit for `malecns_connectome_reservoir_tagging.md`. It narrows the novelty question and does not establish patent novelty, exhaustive literature coverage, or causal dependence between projects.

## 1. Audited claim and temporal cutoff

The narrow claim audited here is not “connectomes can be reservoirs” or “reservoir computing can process text.” It is the specific experimental combination in the paper:

1. MaleCNS v1.0 supplies a fixed recurrent biological topology;
2. UTF-8 bytes are the sequential input unit for Portuguese legal decisions;
3. the task is span/sequence tagging of `resultado` versus `O`;
4. only the text interface/readout are trained while the recurrent operator is frozen;
5. the biological condition is compared against a directed degree-preserving shuffled recurrent null and a non-recurrent byte-only baseline under paired conditions.

The earliest public GitHub object located that contains this exact paper-level claim is commit [`f4a3eca169b75c38c968702bbc51aa9120ae5039`](https://github.com/franklinbaldo/papers/commit/f4a3eca169b75c38c968702bbc51aa9120ae5039), **2026-09-13 17:06:01 UTC**, which introduced the living MaleCNS tagging study. PR #442 was opened about a minute later, so the commit timestamp is the earlier verified public event.

An older PR (#441) was already public at 16:46 UTC, but its first commit was a MaleCNS Wi-Fi reservoir gate. Its semantic/legal-tagging scope was added later; therefore the PR creation time is not used to backdate this specific claim.

**Claim-specific cutoff: 2026-09-13 17:06:01 UTC.** Material first made public after this instant is not prior art against this claim in this audit.

## 2. Search protocol

This round searched both the exact combination and decompositions under older terminology. Representative queries:

- `connectome reservoir text classification`
- `connectome reservoir NLP`
- `connectome sequence tagging reservoir`
- `fruit fly connectome classification reservoir`
- `Drosophila reservoir classification connectome`
- `reservoir computing sequence tagging NLP`
- `echo state network named entity recognition`
- `echo state network part-of-speech tagging`
- `reservoir computing text sequence labeling`
- `echo state network sequence labeling text`
- `connectome-based reservoir language`
- `connectome-informed reservoir NLP`
- `connectome reservoir speech recognition`
- `connectome reservoir text`
- `connectome named entity recognition reservoir`
- `MaleCNS language reservoir connectome`
- `MaleCNS NLP reservoir GitHub`
- `fly-hf MaleCNS TinyStories`

Sources checked included arXiv, Nature/Nature Communications, Scientific Reports, MDPI/PMC/PubMed, public project pages, GitHub and Hugging Face. The search was also run against project/repository terminology rather than assuming earlier work would say “legal sequence tagging.”

## 3. Findings before our cutoff

### 3.1 Generic connectome-as-reservoir computation is established prior art

**Classification:** `prior_art` for the generic mechanism; not anticipation of the narrow legal-tagging combination.

Suárez et al., **“Connectome-based reservoir computing with the conn2res toolbox”**, appeared as posted content in 2023 (DOI `10.1101/2023.05.31.543092`) and was published in *Nature Communications* on 2024-01-22. `conn2res` explicitly treats a biological connectivity matrix as reservoir architecture, accepts supervised task datasets, retrieves reservoir states and trains a linear readout. It also supports connectivity rewiring/manipulation to study the role of topology.

- <https://doi.org/10.1101/2023.05.31.543092>
- <https://www.nature.com/articles/s41467-024-44900-4>

**Effect on our claim:** neither a frozen biological graph with a trained readout nor null-network comparisons are novel by September 2026.

### 3.2 Drosophila connectomes had already been transplanted into reservoirs

**Classification:** `partial_prior_art`.

Morra, Flynn, Amann & Daley, **“Multifunctionality in a Connectome-Based Reservoir Computer”**, arXiv:2306.01885, first posted **2023-06-02**, transplanted the fruit-fly lateral-horn connectome into a reservoir computer and compared it with an Erdős–Rényi reservoir on the “seeing double” benchmark.

- <https://arxiv.org/abs/2306.01885>

Costi et al., **“The Drosophila Connectome as a Computational Reservoir for Time-Series Prediction”**, was publicly available as a preprint by **2025-04-15** and published 2025-05-21. It uses Drosophila connectome topology and synaptic-weight information in an echo-state network, selects high-degree neurons, compares against conventional reservoirs, and includes hybrid controls that separately randomize topology and weights.

- <https://doi.org/10.20944/preprints202504.1215.v1>
- <https://doi.org/10.3390/biomimetics10050341>

This is the immediate precedent already cited by our paper, but the audit makes its scope explicit: the biological-topology-versus-randomized-control logic itself predates our experiment.

### 3.3 Reservoir computing for NLP sequence labeling predates our experiment

**Classification:** `partial_prior_art` for the task family.

Huang, Wang & Safarzadeh, **“Incorporating echo state network and sand cat swarm optimization algorithm based on quantum for named entity recognition”**, published in *Scientific Reports* on **2025-05-29**, applies an echo-state network to CoNLL-2003 named-entity recognition together with embeddings and a CRF layer.

- <https://www.nature.com/articles/s41598-025-02275-6>

The architecture differs substantially from ours, but it eliminates any broad novelty claim of applying reservoir computing to NLP sequence labeling.

### 3.4 Controlled connectome-reservoir benchmarking continued before the cutoff

**Classification:** `adjacent_prior_work` / `partial_prior_art` for controls over biological topology and weights.

Guragain, Kakalis & Godino-Llorente, **“The Whale That Outswam Evolution: Swarm Intelligence Maximises Memory in Connectome Reservoirs”**, arXiv:2606.09902, first posted **2026-06-05**, evaluates connectome-based echo-state networks from several species, including Drosophila, across multiple reservoir benchmarks and compares biological versus random weight initialisation on the same topology.

- <https://arxiv.org/abs/2606.09902>

It does not anticipate our task or MaleCNS-specific implementation, but it reinforces that topology/weight ablation is established experimental practice rather than a novel contribution of our study.

### 3.5 MaleCNS v1.0 had already been used as a language reservoir before our cutoff

**Classification:** strong `partial_prior_art`.

The closest finding of this round is Codex & Alex Wormuth, **“Flies Are All You Need”**, published as a preprint on **2026-09-11**, two days before our claim-specific cutoff. It couples **MaleCNS v1.0** to a frozen 1.17B-parameter language backbone; all 166,700 retained nodes and 25,582,938 directed edges participate in a token-driven reservoir, with a small readout trained on top. Crucially, it also includes a parameter-matched direct-input control and concludes that routing through the fly graph does not establish a wiring-specific advantage.

- <https://artificialscientific.com/papers/flies-are-all-you-need>
- code: <https://github.com/nftechie/flm>

This materially narrows what our paper can regard as distinctive. By 2026-09-11, the combination **MaleCNS v1.0 + language input + frozen anatomical reservoir + trained readout + direct no-graph control** was already public.

The same preprint points to an earlier public `ngxson/fly-llm-hf` prototype using a 49,393-cell MaleCNS central-brain subset as a fixed reservoir trained on TinyStories. The current Hugging Face model card confirms the architecture and reports a shuffled-wiring control, but this round did not independently establish the prototype's first-public timestamp. It is therefore retained as a high-value lead rather than assigned a stronger temporal classification here.

- <https://huggingface.co/ngxson/fly-llm-hf>

### 3.6 A public fixed-fly-connectome classifier was also visible before our cutoff

**Classification:** `partial_prior_art` for a fixed Drosophila connectome used on an arbitrary supervised ML task.

The public GitHub project `Roxx0x/wetware` describes the complete larval Drosophila connectome as a frozen reservoir with only a linear readout trained, including handwritten-digit classification and time-series prediction. GitHub history contains public commits on **2026-09-12**, before our cutoff.

- <https://github.com/Roxx0x/wetware>

This is not MaleCNS and not text, but it further removes novelty from the generic proposition that an untrained fly connectome can serve as a task-agnostic fixed reservoir for conventional ML inputs.

## 4. What remains unresolved rather than established as novel

**Classification:** unresolved combination; absence from this search is not proof of priority.

This round did **not** locate a pre-2026-09-13 17:06:01 UTC source combining all of the following:

1. MaleCNS v1.0 as the fixed recurrent substrate;
2. **byte-level** text input;
3. **span/sequence tagging** rather than next-token generation or document-level classification;
4. **Portuguese legal decisions** as the domain;
5. a topology-specific control that preserves directed in/out degree and the recurrent weight multiset while destroying higher-order wiring;
6. a non-recurrent byte-only baseline under paired seeds/data/optimisation.

That exact experimental package is therefore **not anticipated by any source located in this round**, but this is a negative search result, not a “we were first” conclusion. The scientifically important contribution may ultimately be experimental design/provenance rather than a new learning primitive.

The current negative/indeterminate experiment also constrains interpretation: our five-seed result does not show a MaleCNS topology advantage. Priority over an experimental combination is different from evidence that the biological topology is useful.

## 5. Later work and non-citation

No external post-cutoff publication located in this round was sufficiently close to merit `later_non_citing`, `later_citing` or `later_derivative` classification for the exact byte-level legal-tagging claim. Several MaleCNS demos and benchmarks appeared around the same week, but similarity in timing or use of the same newly released connectome is not evidence of causal dependence.

If a later project reproduces the narrow sequence-tagging/control design without citation, the audit should record only the verifiable chronology, technical overlap and whether a citation was located. It should not infer copying or bad faith without positive evidence.

## 6. Consequence for the paper's novelty framing

The current paper is already appropriately cautious about its negative topology result, but its related-work paragraph is now incomplete if read as a map of the nearest antecedents. A defensible framing is:

> Connectome-based reservoir computing, Drosophila connectome reservoirs, randomized topology/weight controls, and reservoir-based NLP sequence labeling all predate this study. Moreover, MaleCNS v1.0 had already been publicly coupled to language-model inputs as a frozen reservoir before this paper's first public commit. The narrower question tested here is whether a MaleCNS-derived frozen recurrent operator contributes useful signal to byte-level legal span tagging under paired topology-destroying and non-recurrent controls.

This is a stronger claim because it says exactly what the experiment adds without assigning novelty to ingredients that have clear antecedents.

## 7. Next search frontier

The highest-value next searches are narrower than the generic reservoir literature:

1. pre-2026-09-13 repositories or theses using MaleCNS for token/character/byte classification or tagging;
2. `fly-hf` model/repository history to establish its first-public timestamp independently;
3. biological-connectome reservoirs with degree-preserving directed rewiring rather than Erdős–Rényi/random-weight controls;
4. reservoir computing for legal NLP, especially span extraction and outcome/dispositivo segmentation;
5. non-English repository search for connectome-based text tagging that may not use “reservoir” terminology.
