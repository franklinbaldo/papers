---
type: "Protocol"
title: "Learned Visual Attractors for Drosophila"
description: "Closed-loop MaleCNS protocol for optimizing dynamic visual stimuli by capture distance, then distilling successful stimuli toward simpler physical forms."
tags: [malecns, drosophila, visual-tracking, courtship, closed-loop, curriculum-learning, evolutionary-search, surrogate-model]
timestamp: 2026-09-14T19:15:00-04:00
---

# Learned Visual Attractors for Drosophila — protocol

Status: **prospective, no result yet**.

This is an independent experiment. It does not modify the semantic-tagging/F2/F3 protocols or use CausaGanha data.

## 1. Primary question

Starting from a biologically plausible moving target, how far can a visual stimulus capture and guide a MaleCNS-controlled fly toward a fixed lure location?

For stimulus `V`:

`D*(V) = max_d { d : P(approach | V, d) >= p0 }`.

For the first distance-curriculum analysis, freeze `p0 = 0.60` before any optimization result at a new distance is inspected. Report the complete response curve as well as `D*`; `D*` alone is not sufficient evidence.

A candidate also has to exceed the best matched negative control in scene-level approach probability by at least `0.10` at that distance. If this margin is not met, that distance is not considered captured even when the raw probability exceeds `p0`.

## 2. Minimal closed loop

The governing loop is:

```text
stimulus parameters + time + fly pose
        -> retinal/visual rendering
        -> identified visual input neurons
        -> frozen MaleCNS recurrent update
        -> descending-neuron readout
        -> planar fly kinematics
        -> new pose
        -> next frame
```

The recurrent graph is frozen. Search changes only the visual stimulus unless a separately registered interface ablation says otherwise.

The first implementation may use a one-dimensional azimuthal eye model because MaleCNS v1.0 provides optic-column assignments for photoreceptors. It must preserve left/right eye identity and the pinned optic-column source. A richer 2-D eye model is a later interface version, not a silent change.

## 3. Visual interface provenance

Canonical recurrent input is the existing MaleCNS `graph.npz` and manifest used by this repository. The visual interface is built separately and aligned by body ID.

The interface builder may use:

- MaleCNS v1.0 neuron annotations;
- `R1-6`, `R7`, and `R8` photoreceptors;
- the pinned MaleCNS optic-column assignment table from `flyconnectome/2025malecns` commit `67767d2233657983993ff6c2be48e836a935863c`;
- left/right eye and column-derived azimuth;
- identified P1/pC1 types only for a frozen courtship-prime drive;
- descending neurons as the raw motor readout population.

Every interface artifact records body IDs, source URLs/commits, SHA-256 values, unmatched counts, and exact mapping policy.

## 4. Courtship state is part of the positive-control assay

A moving visual target is not assumed to be strongly attractive in every internal state. Work on Drosophila pursuit shows that courtship/arousal state gates the gain of visual tracking circuitry. Therefore the first primary gate uses a **fixed courtship-primed condition** held identical across moving target, static target, blank, and randomized motion.

The implementation may realize the prime as a constant low-amplitude external drive to a predeclared set of MaleCNS P1/pC1 neurons resolved from annotations. The exact type set and drive RMS must be written into the run manifest before the first behavioural comparison.

An otherwise identical unprimed run is a secondary diagnostic. It cannot replace the primary primed comparison after results are known.

## 5. Positive control and first run

Do not start from random images.

The first registered stimulus family contains:

1. `moving_target` — small high-contrast fly-sized target with smooth horizontal motion;
2. `static_equivalent` — same target, same mean luminance/contrast, no motion;
3. `blank` — background only;
4. `random_motion` — same target and motion-energy budget, temporally randomized trajectory.

The initial moving-target calibration uses an apparent width of approximately `15°` at the easy reference distance `d0` and a nominal angular speed of `53°/s`, matching the scale/order of classic courtship-like moving-target assays. These numbers define a positive-control starting point, not the final search bounds.

Define `d0` from target physical diameter `s` by:

`d0 = (s/2) / tan(7.5°)`.

Thus increasing world distance naturally reduces angular size.

First-run scene set:

- `32` independent scene/swarm seeds;
- `64` flies per scene;
- common random numbers: every stimulus/control sees the exact same initial poses and nuisance variables within a scene seed;
- initial radial distance `d0` with small registered jitter;
- heading uniform on `[-pi, pi]`;
- no optimizer in Run 1.

If `moving_target` does not beat both `static_equivalent` and `blank` on the preregistered primary metrics, stop optimization and diagnose the interface. Do not rescue the run by searching thousands of stimuli.

If it does, proceed directly to parametric optimization.

## 6. Per-fly trajectory record

Store at every simulation step or a registered decimation:

- time;
- `x`, `y`, heading;
- target bearing and angular size;
- distance to lure;
- radial velocity;
- orientation error;
- raw descending left/right summaries;
- decoded forward and turn commands;
- collision/contact flag;
- visual drive summary;
- courtship-prime drive summary.

Per fly derive at least:

- initial distance;
- final distance;
- minimum distance;
- normalized distance reduction;
- mean radial velocity;
- fraction of time oriented within `±30°` of target;
- number of approach bouts;
- first entry into the near zone;
- time in near zone;
- revisits;
- contact/passage through lure radius;
- avoidance/retreat fraction;
- trajectory length.

Never discard trajectories and retain only a scalar reward.

## 7. Primary behavioural event

For a fly starting at distance `d`, `approach = 1` when it reduces radial distance by at least `50%` before its registered horizon. The near-zone and contact measures remain secondary so a candidate cannot win only because of one arbitrary radius.

The simulation horizon scales with distance using a frozen reference locomotor speed: enough time to traverse `1.5 * d` at the reference speed, plus a fixed acquisition allowance. The exact speed and allowance are frozen in the first run manifest.

## 8. Unit of replication

The independent statistical unit is the **scene/swarm seed**, not the individual fly. Flies within one scene share stimulus, nuisance variables, and simulator instance.

For each scene compute:

- approach rate;
- median normalized distance reduction;
- median orientation fraction;
- median near-zone time;
- lower-quartile fly score;
- attraction field by initial angular sector.

Candidate/control comparisons are paired by scene seed.

## 9. Attraction field

Estimate:

`A_V(x, y, heading) -> P(approach)`

from the swarm starts. At minimum report attraction by radial distance, starting angular sector, and initial heading-to-target error. A high global mean with a dead sector is visible rather than hidden.

## 10. Parametric stimulus family

The first optimizer acts on an interpretable parameter vector, not raw video pixels:

`theta = (shape, size, contrast, path amplitude, path frequency, mean angular velocity, acceleration, jitter, orientation, flicker, phase)`.

The renderer turns `theta` into a time-dependent visual target. Search bounds and mutation scales are frozen in the run manifest.

A richer renderer or neural video generator is a later stage.

## 11. Evolutionary baseline

First optimizer: deterministic-seeded evolutionary search or CMA-ES over `theta`.

For every generation record:

- population seed;
- every candidate parameter vector;
- scene seeds evaluated;
- complete behavioural vector;
- scalar selection score;
- parents/mutations;
- true simulator calls;
- elapsed compute.

The selection score may combine approach, orientation, distance reduction, near-time, and avoidance, but its weights are frozen before the generation is evaluated. The complete component vector remains authoritative for interpretation.

## 12. Distance curriculum

Distances are continuation stages, not independent hyperparameter searches.

Initial schedule: `d0`, `1.5*d0`, `2.25*d0`, `3.375*d0`, ... . A stage may adapt the next multiplier only by a rule frozen before viewing the next-stage result.

At each stage:

1. seed the initial population with the previous distance winner plus registered perturbations;
2. optimize only on train scene seeds at that distance;
3. select by frozen validation scene seeds;
4. evaluate the frozen winner once on held-out test scene seeds;
5. advance only if the capture criterion passes.

Report `D*` separately for each stimulus family and optimizer.

## 13. Learned generator / critic stage

Only after the evolutionary baseline exists.

A learned generator may emit `theta` first; direct video generation comes later. A critic/surrogate approximates simulator reward from stimulus and context.

Absolute rule:

**critic-only reward never counts.**

Every validation/test candidate and every claimed record is rescored by the true closed-loop MaleCNS simulation. Report critic error, rank correlation, simulator-call budget, and best true reward versus simulator calls.

Compare random search, evolutionary search, and surrogate-guided generation at matched true-simulator budgets.

## 14. Distillation

Once a dynamic winner exists, simplify in a registered sequence:

`rich dynamic target -> simplified render -> silhouette -> primitives -> low-parameter animation -> static image -> printable image`.

At every reduction measure the full capture-distance curve. A static image is adopted only if it preserves enough of the dynamic winner's `D*` under a threshold frozen before that reduction.

## 15. Controls

Candidate-level controls:

- positive moving target;
- blank;
- static equivalent;
- random motion with matched energy;
- temporally shuffled winner;
- reversed trajectory;
- random shape with matched size/contrast;
- structure-destroyed stimulus with matched mean luminance and motion energy.

Neural controls after the positive-control gate:

- true MaleCNS;
- degree-preserving recurrent null;
- random recurrent graph matched on gross size/density;
- visual-pathway ablation;
- relevant descending/readout ablation.

A topology-specific claim requires the true graph to beat the registered graph controls under identical interface, seeds, and stimulus search budgets.

## 16. Heavy artefacts and Kaggle

Do not commit large arrays or video to GitHub.

Private Kaggle Dataset target:

`franklinbaldo/malecns-visual-attractor`

Heavy contents may include:

- `graph.npz`;
- graph manifest;
- visual-interface artifact;
- positive-control videos/parameter manifests;
- trajectories;
- candidate videos;
- optimizer states;
- checkpoints.

GitHub receives only code, protocol, seeds, fingerprints, small result tables, and a small summary manifest. Compute success must not depend on downloading a large Kaggle output ZIP.

## 17. First decision table

Run 1 produces exactly one small decision table containing, for all four stimuli:

- paired scene approach rate;
- normalized distance reduction;
- orientation fraction;
- near-zone time;
- avoidance;
- attraction-field sector summary;
- number of scene seeds;
- interface and graph fingerprints.

If the moving target produces a clear signal, optimization starts. If not, the scientific result of Run 1 is an interface/assay failure and only interface diagnosis is authorized.
