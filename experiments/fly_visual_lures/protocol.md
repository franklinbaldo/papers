---
type: "Protocol"
title: "Printable Visual Lure Search in a Virtual Fly Arena"
description: "Pre-registered multi-agent virtual experiment for discovering printable 2D patterns that robustly attract fly-like agents before any physical transfer test."
tags: [drosophila, vision, optimisation, sim-to-real, printable-pattern, multi-agent]
timestamp: 2026-09-14T17:45:00-04:00
---

# Printable Visual Lure Search in a Virtual Fly Arena

Status: **new independent experiment; no results yet**. This experiment does not modify or rescue any semantic-tagging, flavour-pyramid or MaleCNS reservoir result.

## Question

Can a constrained, printable 2D visual pattern be discovered in simulation that attracts a population of fly-like agents more strongly and more robustly than simple visual controls?

The first gate is entirely virtual. Sim-to-real transfer is a later experiment and cannot be inferred from a virtual win.

## Primary multi-fly design

One target pattern is rendered once in an arena. A swarm of virtual flies is initialized around it at different positions, headings, distances and, where supported, velocities. Every fly sees the same pattern.

This is not only a throughput optimization. It changes the measured object from a single trajectory to an **attraction field** over initial state. One candidate can therefore be evaluated from many viewpoints in one scene while preserving a paired comparison against controls.

For each candidate/control pair, reuse the same frozen swarm starts and scene nuisance variables. Per-fly observations are not treated as fully independent because pattern and scene are shared; confirmatory statistics aggregate/cluster by scene/swarm seed.

## Target object

The optimizable object is one planar square target with a `32 x 32` binary pattern. Pixels are black or white. Rendering uses nearest-neighbour enlargement so the genotype is exactly the printed image at the chosen physical scale.

No colour, UV, odour, food cue, texture, gloss or chemical attractant is present in Gate 1. Adding those after a negative is a new experiment.

## Behavioural outputs

For fly `j` and pattern `p`, record separately:

- orientation response toward the target;
- approach probability / normalized distance reduction;
- dwell time in a fixed target-near zone;
- landing/contact if supported;
- avoidance response;
- time to first acquisition/approach.

The optimization score is a frozen robust aggregate across flies and components. The default summary reports the mean, median and lower-tail quantile across the swarm. A pattern that attracts only a narrow starting sector cannot pass solely on a high mean.

## Attraction-field map

For the frozen pattern estimate response as a function of initial state:

`A_p(x, y, heading, distance, ...) -> response`.

Report at least:

- attraction by angular sector;
- attraction by initial distance;
- capture/orientation basin size;
- repulsive or blind sectors;
- per-scene variability.

The attraction map is a primary scientific output, not merely a visualization.

## Search algorithm

Primary optimizer: simple population-based evolutionary search over binary patterns. A GAN is not required for Gate 1 because the behavioural simulator already supplies the objective. A learned generator/surrogate is a later efficiency extension only after a direct-search signal exists.

Optimizer population, mutation/crossover rules, elite count and total simulator budget are frozen before held-out scene/swarm seeds are opened.

## Controls

Each candidate is paired against the same swarm starts for:

1. all-white target;
2. all-black target;
3. random Bernoulli pattern with matched black-pixel fraction;
4. checkerboard;
5. single vertical stripe;
6. concentric bullseye;
7. shuffled/phase-scrambled version of the candidate where feasible;
8. best pattern from an optimizer using shuffled behavioural rewards.

The strongest control on validation is the decision comparator.

## Scene splits and domain randomization

Freeze search/train, validation and held-out test scene/swarm seeds before optimization.

Randomize at least:

- fly initial positions/headings/velocities;
- target distance, orientation and apparent size;
- swarm spatial distribution;
- background luminance/texture;
- global brightness/contrast;
- compound-eye/render sampling noise.

The candidate and its controls receive the exact same nuisance draw and initial swarm for paired evaluation.

## Gate 0 — visual sensitivity sanity

Before optimization, the agent must show a measurable behavioural difference between at least two established visual controls. A simulator with no visually guided response cannot test lure discovery.

## Gate 1 — virtual lure discovery

Freeze the selected pattern on validation and evaluate once on held-out scene/swarm seeds.

Success requires all of:

- composite attraction above the strongest fixed control by a predeclared effect threshold;
- better approach probability;
- better dwell or landing/contact;
- positive paired effect across a strong majority of held-out scene/swarm seeds;
- attraction across multiple initial angular sectors and distances;
- superiority to fresh random-pattern controls drawn after the candidate is frozen;
- no catastrophic collapse under any registered modest perturbation axis.

The numerical threshold is fixed from control variability before the candidate test set is opened.

## Gate 2 — simulator-hack audit

Probe the frozen winner under transformations that should preserve the useful cue while breaking renderer quirks: modest translation/rotation, blur, print-resolution changes, contrast compression, new backgrounds and alternate eye/render seeds or implementations where available.

If the effect disappears under tiny nuisance changes, report simulator exploitation, not a robust lure.

## Gate 3 — mechanism diagnostics

Only after Gate 1 passes. If neural populations are exposed, lesion/perturb candidate visual pathways and compare intact versus matched topology controls. Mechanistic diagnostics cannot rescue a failed behavioural gate.

## Gate 4 — physical transfer

Authorized only after virtual robustness. Print the frozen winner and controls and preregister a contained assay with randomized target positions and blinded trajectory analysis. Multiple flies may be tracked simultaneously, mirroring the virtual swarm design.

No odour/food cue in the primary visual-transfer assay. A physical negative closes that transfer round; redesign after observing it is a new round.

## Records

Store for every candidate:

- exact bitmap and hash;
- optimizer generation/parentage;
- simulator/version hash;
- scene/swarm seeds;
- every per-fly behavioural component;
- per-scene aggregate and attraction-field summary;
- whether any physical result was visible when the candidate was created.

## First implementation milestone

1. simulator-neutral `FlyArena` interface;
2. deterministic binary pattern generator/mutator;
3. deterministic swarm-start generator;
4. per-fly attraction metrics and scene-level aggregation;
5. fixed visual controls;
6. toy/mock agent to verify optimizer and pairing plumbing;
7. connect the chosen fly simulator;
8. freeze simulator version, scene splits, score weights and effect threshold;
9. run Gate 0, then the first search.
