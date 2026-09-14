---
type: "Paper"
title: "Learning Printable Visual Lures for Fly Agents"
description: "Draft empirical paper: optimize printable visual patterns against populations of fly-like agents in simulation, then test whether attraction transfers to physical Drosophila assays."
tags: [drosophila, vision, sim-to-real, visual-attraction, connectome, safety]
timestamp: 2026-09-14T17:40:00-04:00
status: "pre-registered design; no confirmatory results yet"
---

# Learning Printable Visual Lures for Fly Agents

## Abstract

We ask whether a visual pattern optimized entirely in simulation can become a reliable, printable lure for flies. The proposed system places multiple fly-like agents at different positions and orientations in a virtual arena containing one flat target surface whose image is generated procedurally. A search algorithm modifies the pattern to maximize preregistered attraction behaviours such as orientation, approach, dwell time and landing across the population. The resulting pattern is then tested under domain randomization and against simple visual controls before any physical transfer is attempted.

The scientific question is not whether flies respond to visual patterns; that is established. The question is whether an optimization loop can discover a compact, printable pattern whose **attraction field** survives changes in viewpoint, pose, illumination and scene statistics and then transfers at least partially from a fly/connectome simulation to real insects. A successful result would provide a non-chemical, visually mediated lure and a benchmark for how much behaviourally relevant structure in a simulated visual system transfers to the animal that inspired it.

No sim-to-real claim is made in this draft. The first registered result is virtual only; a physical assay is a later gate contingent on robustness in simulation.

## Motivation

Flies show robust visually guided orientation, fixation, optomotor responses and landing behaviours. Prior work has demonstrated innate preferences for object shape and size in closed-loop virtual reality, fixation on high-contrast objects or stripes, visually guided flight and landing, and spectral preferences that depend on photoreceptor pathways. These findings motivate the search space but do not establish that an optimized printable pattern will transfer across a simulator-to-animal gap.

The proposed contribution is narrower and operational:

> Treat a printable surface as an optimizable sensory stimulus, use a population of fly-like agents as the behavioural objective, and test whether the resulting lure defines a robust spatial field of attraction under controlled perturbations and, later, in a blinded real-world assay.

## Core experiment

A single planar target is shared by many virtual flies in the same scene. Each fly starts from a different position, heading, distance and, where the simulator supports it, velocity. All see the **same drawing**. This is a major efficiency advantage: one candidate pattern can be evaluated from many viewpoints simultaneously instead of requiring one pattern/one trajectory pairs.

The target displays a generated image constrained to be physically printable. Each agent receives only its normal visual input. The generator never receives privileged access to internal labels such as target direction at deployment; its only feedback during search is the population's behaviour.

The first search space is deliberately small: a `32 x 32` binary black/white pattern, upsampled without interpolation to the target surface. This isolates spatial pattern from colour, UV, odour and material effects. Later experiments may add grayscale, colour or spectral reflectance, but those are different axes and may not rescue a failed binary experiment.

For pattern `p` and fly `j`, an episode contribution is built from observable behaviour:

`R_j(p) = w_o * orientation_j + w_a * approach_j + w_d * dwell_j + w_l * landing_j - w_e * avoidance_j`

The pattern reward aggregates across flies, not across isolated episodes:

`R(p) = robust_aggregate_j R_j(p)`.

The default aggregate is the mean together with lower-tail diagnostics. A pattern that attracts only flies starting in one favourable sector is not a robust lure even if its mean is high.

The individual terms and per-fly scores are always reported separately. A positive result cannot be carried by one pathological term, such as agents oscillating near the target without approaching it.

## Attraction field, not a single trajectory

The multi-fly design makes the object of study a spatial response field. For a frozen pattern we estimate attraction as a function of initial state:

`A_p(x, y, heading, distance, ...) -> behavioural response`.

This provides several measurements unavailable in a one-fly design:

- the angular basin from which the pattern captures orientation;
- the distance range over which attraction remains detectable;
- asymmetric blind spots or repulsive sectors;
- variance across agents exposed to exactly the same target and scene;
- robustness of the lure to viewpoint without changing the pattern.

A candidate therefore produces both a scalar optimization score and an **attraction map**. The map is a scientific output in its own right and may reveal whether a pattern is broadly attractive or merely exploits a narrow camera/pose configuration.

Multiple flies in one scene are not treated as fully independent statistical replicates. Scene and pattern are shared, so confirmatory analysis clusters observations by scene/pattern seed and reports both per-fly and per-scene aggregates.

## Optimizer

The first optimizer is population-based rather than a GAN. The simulator itself is already the behavioural critic, so a classical generator/discriminator GAN is not required. A simple evolutionary search over the binary grid gives a transparent first test and makes it easy to preserve an archive of candidate patterns and behavioural traces.

A learned generator is a later extension only if direct search establishes a real signal. At that stage a generator may map latent codes to printable images while a learned surrogate predicts behavioural reward to reduce simulation cost. The fly/connectome simulation remains the final evaluator.

## Controls

Every candidate family is compared against fixed controls under identical arena randomization and the **same initial swarm states**:

- blank white target;
- blank black target;
- random binary patterns matched for black-pixel fraction;
- checkerboard;
- vertical stripe;
- concentric target;
- the best pattern from an optimizer whose reward labels are shuffled.

Using paired swarm starts is load-bearing: if candidate and control see different initial fly configurations, spatial sampling noise can masquerade as attraction.

If the simulator exposes relevant neural populations, mechanism ablations are diagnostic rather than decision-bearing: silence candidate object/looming pathways, perturb the compound-eye model, and compare the intact connectome with topology controls. These tests ask why a lure works; they do not substitute for behavioural attraction.

## Domain randomization

A pattern that exploits one renderer configuration is not a lure. During optimization and held-out testing, randomize at least:

- target yaw/pitch and distance;
- initial fly positions, headings and velocities;
- spatial distribution of the swarm around the target;
- global illumination/intensity;
- background texture and contrast;
- camera/compound-eye sampling noise;
- target physical size within a declared range.

A held-out randomization distribution is frozen before optimization. Final virtual evaluation uses only unseen scene/swarm seeds and scene draws.

## Registered virtual gates

The first experiment is successful only if the selected pattern:

1. beats the strongest fixed visual control on a preregistered population attraction score;
2. improves both approach probability and dwell/landing behaviour, not merely one reward component;
3. has a positive paired effect across a strong majority of held-out **scene/swarm seeds**;
4. retains attraction across multiple initial spatial sectors and distances rather than one narrow basin;
5. beats random-pattern controls drawn after optimization;
6. does not collapse under modest changes in target pose, brightness or background.

The exact effect-size threshold is frozen when the chosen simulator exposes the natural scale of the behavioural metrics, before the optimizer is run on the decision set.

## Sim-to-real gate

A physical assay is authorized only after the virtual robustness gate passes. The printed pattern, blank controls and matched random controls are presented in randomized positions in a contained arena. Multiple flies are tracked simultaneously when feasible, mirroring the virtual swarm design. Analysis is blinded to target identity until trajectories are frozen.

Primary physical outcomes should mirror the virtual ones where possible: first orientation, approach probability, visits/landings, dwell time and spatial attraction maps. Odour, food and chemical attractants are absent from the primary assay so the transfer claim remains visual.

A physical negative is not rescued by tuning the printed pattern against the same flies. Any redesign after seeing the physical result is a new sim-to-real round.

## Safety framing

The intended use is benign attraction and redirection of flies using a passive visual surface, potentially useful for monitoring or non-chemical trapping. The first phases are fully virtual. Physical work, if reached, should use contained standard husbandry and avoid release, environmental spread or claims of species-general attraction without direct tests.

## Prior-art boundary

This paper does not claim novelty for visual attraction, object fixation, stripe preference, phototaxis, or virtual-reality assays in flies. Relevant literature already shows innate shape/size preferences in walking *Drosophila*, visual fixation on stripes/objects, visually controlled landing and obstacle avoidance, and wavelength preferences mediated by different photoreceptor classes.

The research bet is the conjunction: **closed-loop optimization of a constrained printable pattern against a population of fly-like agents + an explicit attraction-field measurement + held-out robustness + simulator-hack controls + a later blinded sim-to-real transfer test.**

## References / starting points

- van Breugel & Dickinson, "The visual control of landing and obstacle avoidance in the fruit fly Drosophila melanogaster", *Journal of Experimental Biology* (2012), DOI `10.1242/jeb.066498`.
- Weir, Schnell & Dickinson, "Drosophila fly straight by fixating objects in the face of expanding optic flow", *Journal of Experimental Biology* (2010), PMID `20435828`.
- "Innate visual preferences and behavioral flexibility in Drosophila" (2018), PMID `30322983`.
- Yamaguchi et al., "Contribution of photoreceptor subtypes to spectral wavelength preference in Drosophila" (2010), PMID `20212139`.
- Wolf & Heisenberg, "Visual control of straight flight in Drosophila melanogaster" (1990), PMID `2120434`.

## Claim boundary

A virtual positive means only that the selected simulator/agent admits robust printable visual attractors under the registered perturbations. A physical positive means the frozen optimized pattern attracts the tested fly population more than the registered controls in that assay. Neither result establishes universal attraction, ecological superiority, or that the same neural mechanism caused both the virtual and physical effects.
