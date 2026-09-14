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

A transparent evolutionary search is the first optimizer. A second generator arm places another frozen MaleCNS on the opposite side of the visual channel: MaleCNS A receives observable state from receiver B through a trainable input adapter, evolves its own recurrent state, and a trainable output adapter turns A's descending activity into a time-varying visual control sequence shown to B. This creates a connectome-to-connectome closed loop while keeping both recurrent graphs frozen. The connectomic generator is compared against direct parametric search, a parameter-matched MLP generator, a random recurrent generator, and a degree-preserving MaleCNS emitter null under identical receiver seeds and true-simulator budgets.

A later learned generator may propose stimulus parameters or video while a critic predicts expensive simulator reward, but every claimed improvement is rescored by the true MaleCNS loop. Fooling the critic never counts. Heavy graph, trajectory, video, checkpoint, and optimizer-state artefacts live in a versioned private Kaggle Dataset; GitHub stores code, protocol, hashes, seeds, manifests, and small summaries.

## Scientific question

For a stimulus family `V_theta`, define the capture range

`D*(V) = max_d { d : P(approach | V, d) >= p0 }`,

where `p0` is frozen before the corresponding analysis. The central question is whether optimization can increase `D*` beyond a biologically plausible moving-target control, and how much stimulus complexity can subsequently be removed without losing that gain.

## Why movement is the first positive control

Male Drosophila courtship relies strongly on visual tracking of small moving objects. LC10/LC10a visual projection neurons are implicated in detecting fly-sized moving targets and in directed pursuit, with their effective gain modulated by courtship arousal. The first virtual assay therefore uses a moving high-contrast target under a fixed courtship-primed condition rather than treating a static photograph as the strongest control.

The priming manipulation is part of the assay and is held constant across candidate and controls. An unprimed condition is retained as a diagnostic, not as a substitute for the primary gate.

## Experimental stages

1. **Interface gate.** Build the minimal visual-to-MaleCNS-to-motion loop and compare moving positive control, static equivalent, blank, and randomized motion on matched swarms.
2. **Parametric search.** Evolve interpretable stimulus parameters such as angular size, contrast, path, speed, acceleration, jitter, orientation, and flicker.
3. **Distance curriculum.** Increase initial distance only after the current distance passes the frozen capture criterion; initialize each harder search from the previous winner.
4. **Connectome generator.** Place a second frozen MaleCNS on the emitter side and train only its input/output adapters so that its recurrent activity invents the visual dynamics presented to the receiver.
5. **Generator controls.** Compare the connectomic emitter against direct parametric search, a parameter-matched MLP, a frozen random recurrent emitter, and a degree-preserving MaleCNS emitter null at matched true-simulator budgets.
6. **Learned proposal model.** Compare random search, evolutionary search, connectomic generation, and a surrogate-guided neural generator at matched true-simulator budgets.
7. **Distillation.** Remove temporal, spatial, and representational complexity while measuring the loss in capture range. For a connectome-generated winner, first compare adaptive closed-loop generation with prerecorded replay of the exact emitted waveform.
8. **Sim-to-real.** Only after virtual robustness, test frozen positive control, best synthetic attractor, temporally shuffled attractor, and blank on a physical display; printable/static transfer is a later compression question.

## Connectome-to-connectome generator

The connectome-generator arm asks whether a biological wiring prior is useful not only as a receiver but also as a **signal generator**.

```text
receiver B pose / radial motion
        -> input adapter
        -> frozen MaleCNS A
        -> output adapter
        -> bearing / size / contrast / temporal gate
        -> visual renderer
        -> frozen MaleCNS B
        -> movement
        -> updated receiver state
        -> ...
```

A does not see B's neural state. Its primary adaptive context is limited to receiver variables that could be measured externally: distance, bearing, heading and radial motion. Both recurrent connectomes remain frozen. Only the boundary adapters of A are trainable in the first arm.

The first emitted signal is deliberately low-dimensional rather than raw video. At every timestep A controls target bearing offset, apparent size, contrast and an intensity gate. This gives the recurrent emitter room to invent temporally structured signals while keeping the search interpretable. Direct video generation is a later extension.

The key comparison is not whether this architecture can be trained at all. The key questions are:

- does a true MaleCNS emitter increase `D*` or robustness over an MLP/direct generator at equal receiver-evaluation budget?;
- does it beat a frozen random recurrent emitter?;
- does it beat a degree-preserving MaleCNS emitter null with identical adapters?;
- does the resulting waveform still work when prerecorded and replayed, or is closed-loop adaptation itself necessary?

Only the last two topology controls can support a claim that the higher-order emitter wiring matters. A connectome generator that merely matches a generic controller is still a functioning two-connectome system, but not evidence for a special biological topology.

If a frozen emitted waveform replays successfully across receivers, the result suggests a reusable synthetic visual signal. If only adaptive generation succeeds, the result instead points to an interactive control policy. Neither outcome is described as natural fly communication without a separate biological experiment.

The governing arm protocol is `experiments/malecns_visual_attractor/connectome-generator-arm.md`.

## Claim boundary

A virtual winner establishes only a property of the registered MaleCNS simulation and interface. A topology-specific claim requires matched graph controls and pathway ablations. A real-world lure claim requires a separately registered physical assay. No result in the tagging line can rescue this experiment, and no result here retroactively changes the tagging papers.

The governing protocol and executable scaffold live under `experiments/malecns_visual_attractor/`.
