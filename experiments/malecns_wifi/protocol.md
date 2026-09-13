---
type: "Protocol"
title: "MaleCNS Wi-Fi Reservoir — Compile and Sensing Protocol v0"
description: "Preregistered first gate for compiling MaleCNS v1.0 into a fixed sparse reservoir, validating its runtime dynamics, and preparing a fair CSI movement-sensing comparison."
tags: [malecns, drosophila, connectome, reservoir-computing, wifi, csi]
timestamp: 2026-09-13T12:16:00-04:00
---

# MaleCNS Wi-Fi Reservoir — Compile and Sensing Protocol v0

## Question

Can the released MaleCNS v1.0 connectome serve as a useful fixed recurrent reservoir for Wi-Fi Channel State Information (CSI) sensing, with only an input adapter and readout trained for the task?

The experiment does **not** assume a biological advantage. The MaleCNS topology must beat or complement simpler matched baselines before any such claim is made.

## Gate 0 — reproducible connectome artifact

Source: the public MaleCNS v1.0 flat-connectome release from Janelia. The workflow may use a byte-identical mirror (for example Internet Archive) when a mirror base URL is supplied, but records the actual URLs, byte sizes, and SHA-256 hashes in `manifest.json`.

Node policy:

- retain `status == Traced`;
- exclude explicit glia;
- preserve stable body IDs in the artifact.

Edge policy for this first runtime:

- retain directed neuron-to-neuron pairs with at least 3 reconstructed synapses;
- use synapse count as connection magnitude;
- presynaptic acetylcholine is positive;
- GABA, glutamate, and histamine are negative;
- dopamine, octopamine, serotonin, unclear, and unknown are zero in the fast recurrent operator rather than being assigned a fictitious excitatory/inhibitory sign;
- store the operator as `W[post, pre]` in CSR form.

This policy is intentionally aligned with an independently published MaleCNS build path so the first compile has an external sanity target. The expected order of magnitude is about 165k retained neurons and about 10M signed recurrent edges. A mismatch is a debugging result, not something to tune away.

## Gate 1 — runtime smoke

Before attaching Wi-Fi data, a deterministic seeded perturbation is injected into a small input population. The recurrent state must:

1. remain finite for all smoke steps;
2. spread beyond the directly stimulated population;
3. be reproducible from the same compiled graph and random seed.

The smoke dynamics are a bounded computational reservoir, not a claim of biophysical membrane simulation.

## Gate 2 — Wi-Fi CSI experiment

After Gates 0 and 1 pass, all models receive the **same frozen CSI feature stream** and the same train/validation/test split.

Primary task: `movement / no movement`.

Secondary tasks, only after the primary task works:

- room/zone classification;
- direction of movement;
- persistent occupancy after movement stops.

Models to compare:

1. linear/logistic readout directly on CSI features;
2. small MLP or similarly cheap nonlinear baseline;
3. conventional random reservoir;
4. degree/weight-matched rewired MaleCNS control;
5. true frozen MaleCNS reservoir.

For reservoir conditions, only the input projection and readout may be trained in the first comparison. Recurrent MaleCNS weights remain frozen.

## Evaluation rules

- Split by recording session/time block, never by randomly mixing adjacent CSI windows across train and test.
- Report macro-F1 for movement classification plus false-positive rate and decision latency.
- Report parameter counts and wall-clock inference cost for each baseline.
- Use multiple fixed seeds for trainable adapters/readouts.
- Do not call a result a MaleCNS advantage unless the true topology beats both the conventional reservoir and the matched rewired control on held-out recordings.

## Immediate workflow output

The current workflow produces:

- `graph.npz` — compiled sparse recurrent operator;
- `manifest.json` — source provenance, hashes, policy, and graph counts;
- `smoke.json` — deterministic runtime trace.

No CSI performance claim is made by this workflow yet.
