---
type: "Technical Paper"
title: "Learned Visual Attractors for Drosophila: From Courtship Stimuli to Long-Range Synthetic Lures"
description: "Living experimental paper on optimizing dynamic visual stimuli in a closed-loop MaleCNS simulation, extending capture distance before distilling successful stimuli toward simpler physical forms."
tags: [malecns, drosophila, connectome, vision, courtship, closed-loop, optimisation, sim-to-real]
timestamp: 2026-09-14T19:15:00-04:00
---

# Learned Visual Attractors for Drosophila

## From courtship stimuli to long-range synthetic lures

**Franklin Baldo**  
Independent Researcher

> **Status.** New independent experimental line. No positive virtual or physical result is claimed. The first decision is whether a biologically plausible moving target produces measurable orientation and approach in a closed-loop MaleCNS arena under a frozen courtship-primed condition. The experiment is independent of the semantic-tagging, F2/F3, flavour-pyramid, and legal-text work.

## Abstract

Rather than beginning with an arbitrary printable image, we ask a broader optimization question: **which visual stimulus captures and guides a male Drosophila-like agent from the greatest initial distance?** The stimulus is evaluated in closed loop: a fly pose determines the retinal view, visual drive enters a MaleCNS-derived recurrent network, descending activity is decoded into movement, and the new pose changes the next frame. A candidate is therefore judged by behaviour, not by an image classifier or a surrogate alone.

The search begins in a region already known to support male pursuit: a small, high-contrast moving target resembling the visual component of a female. The first gate compares a moving target with its static equivalent, blank, and random-motion controls across paired swarms. If the positive control produces measurable tracking, optimization begins immediately. The primary optimization target is the **maximum capture distance** at a pre-registered approach-probability threshold. Search proceeds as a continuation problem: optimize at an easy distance, initialize the next population from the winner, increase distance, and repeat.

Successful stimuli are then distilled rather than assumed printable. The planned sequence is rich dynamic target -> simplified render -> silhouette -> geometric primitives -> low-parameter animation -> static image -> optionally printed paper. A video that survives while every static reduction fails is a scientific result, not a failed paper-lure project.

A transparent evolutionary search is the first optimizer. A later learned generator may propose stimulus parameters or video while a critic predicts expensive simulator reward, but every claimed improvement is rescored by the true MaleCNS loop. Fooling the critic never counts. Heavy graph, trajectory, video, checkpoint, and optimizer-state artefacts live in a versioned private Kaggle Dataset; GitHub stores code, protocol, hashes, seeds, manifests, and small summaries.

## Scientific question

For a stimulus family `V_theta`, define the capture range

`D*(V) = max_d { d : P(approach | V, d) >= p0 }`,

where `p0` is frozen before the corresponding analysis. The central question is whether optimization can increase `D*` beyond a biologically plausible moving-target control, and how much stimulus complexity can subsequently be removed without losing that gain.

## Why movement is the first positive control

Male Drosophila courtship relies strongly on visual tracking of small moving objects. Ribeiro et al. identified LC10 visual projection neurons as a major pathway for directed courtship: silencing disrupted orientation and maintenance of proximity, and LC10 neurons preferentially responded to small moving objects. Hindmarsh Sten et al. then showed that P1-mediated sexual arousal increases LC10a gain and supports high-fidelity tracking of a virtual female. Earlier, Kohatsu and Yamamoto showed that after appropriate state priming, artificial moving light targets can sustain courtship-like following pursuit.

The first virtual assay therefore uses a moving high-contrast target under a fixed courtship-primed condition rather than treating a static photograph as the strongest control. The priming manipulation is part of the assay and is held constant across candidate and controls. An unprimed condition is retained as a diagnostic, not as a substitute for the primary gate.

## Experimental stages

1. **Interface gate.** Build the minimal visual-to-MaleCNS-to-motion loop and compare moving positive control, static equivalent, blank, and randomized motion on matched swarms.
2. **Parametric search.** Evolve interpretable stimulus parameters such as angular size, contrast, path, speed, acceleration, jitter, orientation, and flicker.
3. **Distance curriculum.** Increase initial distance only after the current distance passes the frozen capture criterion; initialize each harder search from the previous winner.
4. **Learned proposal model.** Compare random search, evolutionary search, and a surrogate-guided generator at matched true-simulator budgets.
5. **Distillation.** Remove temporal, spatial, and representational complexity while measuring the loss in capture range.
6. **Sim-to-real.** Only after virtual robustness, test frozen positive control, best synthetic attractor, temporally shuffled attractor, and blank on a physical display; printable/static transfer is a later compression question.

## Claim boundary

A virtual winner establishes only a property of the registered MaleCNS simulation and interface. A topology-specific claim requires matched graph controls and pathway ablations. A real-world lure claim requires a separately registered physical assay. No result in the tagging line can rescue this experiment, and no result here retroactively changes the tagging papers.

The governing protocol, frozen Run 1 operating point, and executable scaffold live under `experiments/malecns_visual_attractor/`.

## References

- Ribeiro, I. M. A., Drews, M., Bahl, A., Machacek, C., Borst, A. & Dickson, B. J. **Visual Projection Neurons Mediating Directed Courtship in Drosophila.** *Cell* 174, 607–621.e18 (2018). DOI: `10.1016/j.cell.2018.06.020`.
- Hindmarsh Sten, T., Li, R., Otopalik, A. et al. **Sexual arousal gates visual processing during Drosophila courtship.** *Nature* 595, 549–553 (2021). DOI: `10.1038/s41586-021-03714-w`.
- Kohatsu, S. & Yamamoto, D. **Visually induced initiation of Drosophila innate courtship-like following pursuit is mediated by central excitatory state.** *Nature Communications* 6, 6457 (2015). DOI: `10.1038/ncomms7457`.
