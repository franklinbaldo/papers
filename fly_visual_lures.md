---
type: "Paper"
title: "Learning Printable Visual Lures for Fly Agents"
description: "Draft empirical paper: optimize printable visual patterns against fly-like visual agents in simulation, then test whether attraction transfers to physical Drosophila assays."
tags: [drosophila, vision, sim-to-real, visual-attraction, connectome, safety]
timestamp: 2026-09-14T17:40:00-04:00
status: "pre-registered design; no confirmatory results yet"
---

# Learning Printable Visual Lures for Fly Agents

## Abstract

We ask whether a visual pattern optimized entirely in simulation can become a reliable, printable lure for flies. The proposed system places a fly-like agent in a virtual arena containing a flat target surface whose image is generated procedurally. A search algorithm modifies the pattern to maximize preregistered attraction behaviours such as orientation, approach, dwell time and landing. The resulting pattern is then tested under domain randomization and against simple visual controls before any physical transfer is attempted.

The scientific question is not whether flies respond to visual patterns; that is established. The question is whether an optimization loop can discover a compact, printable pattern whose attraction survives changes in pose, illumination and scene statistics and then transfers at least partially from a fly/connectome simulation to real insects. A successful result would provide a non-chemical, visually mediated lure and a benchmark for how much behaviourally relevant structure in a simulated visual system transfers to the animal that inspired it.

No sim-to-real claim is made in this draft. The first registered result is virtual only; a physical assay is a later gate contingent on robustness in simulation.

## Motivation

Flies show robust visually guided orientation, fixation, optomotor responses and landing behaviours. Prior work has demonstrated innate preferences for object shape and size in closed-loop virtual reality, fixation on high-contrast objects or stripes, visually guided flight and landing, and spectral preferences that depend on photoreceptor pathways. These findings motivate the search space but do not establish that an optimized printable pattern will transfer across a simulator-to-animal gap.

The proposed contribution is narrower and operational:

> Treat a printable surface as an optimizable sensory stimulus, use a fly-like agent as the behavioural objective, and test whether the resulting lure remains attractive under controlled perturbations and, later, in a blinded real-world assay.

## Core experiment

A virtual fly starts from randomized poses in an arena containing a planar target. The target displays a generated image constrained to be physically printable. The agent receives only its normal visual input. The generator never receives privileged access to internal labels such as target direction at deployment; its only feedback during search is the fly's behaviour.

The first search space is deliberately small: a `32 x 32` binary black/white pattern, upsampled without interpolation to the target surface. This isolates spatial pattern from colour, UV, odour and material effects. Later experiments may add grayscale, colour or spectral reflectance, but those are different axes and may not rescue a failed binary experiment.

For a pattern `p`, an episode score is built from observable behaviour:

`R(p) = w_o * orientation + w_a * approach + w_d * dwell + w_l * landing - w_e * avoidance`

The individual terms are always reported separately. A positive result cannot be carried by one pathological term, such as the agent oscillating near the target without approaching it.

## Optimizer

The first optimizer is population-based rather than a GAN. The simulator itself is already the behavioural critic, so a classical generator/discriminator GAN is not required. A simple evolutionary search over the binary grid gives a transparent first test and makes it easy to preserve an archive of candidate patterns and behavioural traces.

A learned generator is a later extension only if direct search establishes a real signal. At that stage a generator may map latent codes to printable images while a learned surrogate predicts behavioural reward to reduce simulation cost. The fly/connectome simulation remains the final evaluator.

## Controls

Every candidate family is compared against fixed controls under identical arena randomization:

- blank white target;
- blank black target;
- random binary patterns matched for black-pixel fraction;
- checkerboard;
- vertical stripe;
- concentric target;
- the best pattern from an optimizer whose reward labels are shuffled.

If the simulator exposes relevant neural populations, mechanism ablations are diagnostic rather than decision-bearing: silence candidate object/looming pathways, perturb the compound-eye model, and compare the intact connectome with topology controls. These tests ask why a lure works; they do not substitute for behavioural attraction.

## Domain randomization

A pattern that exploits one renderer configuration is not a lure. During optimization and held-out testing, randomize at least:

- target yaw/pitch and distance;
- initial fly pose and velocity;
- global illumination/intensity;
- background texture and contrast;
- camera/compound-eye sampling noise;
- target physical size within a declared range.

A held-out randomization distribution is frozen before optimization. Final virtual evaluation uses only unseen seeds and scene draws.

## Registered virtual gates

The first experiment is successful only if the selected pattern:

1. beats the strongest fixed visual control on a preregistered composite attraction score;
2. improves both approach probability and dwell/landing behaviour, not merely one reward component;
3. remains positive over held-out scene randomizations rather than a small number of lucky seeds;
4. beats random-pattern controls drawn after optimization;
5. does not collapse under modest changes in target pose, brightness or background.

The exact effect-size threshold is frozen when the chosen simulator exposes the natural scale of the behavioural metrics, before the optimizer is run on the decision set.

## Sim-to-real gate

A physical assay is authorized only after the virtual robustness gate passes. The printed pattern, blank controls and matched random controls are presented in randomized positions in a contained arena. Analysis is blinded to target identity until trajectories are frozen.

Primary physical outcomes should mirror the virtual ones where possible: first orientation, approach probability, visits/landings and dwell time. Odour, food and chemical attractants are absent from the primary assay so the transfer claim remains visual.

A physical negative is not rescued by tuning the printed pattern against the same flies. Any redesign after seeing the physical result is a new sim-to-real round.

## Safety framing

The intended use is benign attraction and redirection of flies using a passive visual surface, potentially useful for monitoring or non-chemical trapping. The first phases are fully virtual. Physical work, if reached, should use contained standard husbandry and avoid release, environmental spread or claims of species-general attraction without direct tests.

## Prior-art boundary

This paper does not claim novelty for visual attraction, object fixation, stripe preference, phototaxis, or virtual-reality assays in flies. Relevant literature already shows innate shape/size preferences in walking *Drosophila*, visual fixation on stripes/objects, visually controlled landing and obstacle avoidance, and wavelength preferences mediated by different photoreceptor classes.

The research bet is the conjunction: **closed-loop optimization of a constrained printable pattern against a fly-like agent + held-out robustness + explicit simulator-hack controls + a later blinded sim-to-real transfer test.**

## References / starting points

- van Breugel & Dickinson, "The visual control of landing and obstacle avoidance in the fruit fly Drosophila melanogaster", *Journal of Experimental Biology* (2012), DOI `10.1242/jeb.066498`.
- Weir, Schnell & Dickinson, "Drosophila fly straight by fixating objects in the face of expanding optic flow", *Journal of Experimental Biology* (2010), PMID `20435828`.
- "Innate visual preferences and behavioral flexibility in Drosophila" (2018), PMID `30322983`.
- Yamaguchi et al., "Contribution of photoreceptor subtypes to spectral wavelength preference in Drosophila" (2010), PMID `20212139`.
- Wolf & Heisenberg, "Visual control of straight flight in Drosophila melanogaster" (1990), PMID `2120434`.

## Claim boundary

A virtual positive means only that the selected simulator/agent admits robust printable visual attractors under the registered perturbations. A physical positive means the frozen optimized pattern attracts the tested fly population more than the registered controls in that assay. Neither result establishes universal attraction, ecological superiority, or that the same neural mechanism caused both the virtual and physical effects.
