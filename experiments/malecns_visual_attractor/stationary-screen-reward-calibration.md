---
type: "Protocol"
title: "MaleCNS Stationary-Screen Reward-Loop Calibration"
description: "Engineering calibration for a stationary visual display generated from a MaleCNS body latent and reinforced by receiver neural excitation."
tags: [malecns, drosophila, visual, reward, calibration, kaggle]
timestamp: 2026-09-14T21:10:00-04:00
---

# Stationary-screen reward-loop calibration

Status: **engineering calibration after failed Run 1; not Run 2**.

The screen is stationary at the world origin. Only receiver flies move. The generator is a frozen full MaleCNS used as a dynamic substrate; it does not represent a second physical fly.

## Generator loop

1. generator MaleCNS recurrent state produces a six-channel body latent from DNa02, DNg100 and broad left/right descending activity;
2. a small `6 x 6` screen transducer maps that latent to pattern x/y offset, apparent-size scale, orientation, contrast and lobe separation;
3. the stationary screen renders a three-lobe body-like pattern onto **all mapped receiver visual receptors**;
4. the receiver full MaleCNS evolves and moves;
5. receiver descending excitation is reduced to a scalar reward;
6. the reward returns one step later through an explicitly synthetic reward projection into the generator descending pool;
7. one-plus-lambda ES selects the screen transducer with the highest integrated receiver descending excitation.

The synthetic reward projection is an engineering boundary, not a claim about identified dopaminergic neurons. Later work may replace it with an anatomically motivated neuromodulatory pathway.

## Direct-gaze calibration

Receivers start facing the stationary screen. Initial apparent screen width is approximately `30°`. No courtship/P1/pC1 prime is applied. The first objective is to establish a live visual-to-descending channel before testing capture distance.

Selection reward is mean absolute receiver descending activity integrated through time. Approach, final distance and minimum distance are recorded but are not the calibration selection target.

## Telemetry

Every registered checkpoint logs:

- current leading transducer candidate;
- instantaneous and cumulative reward;
- generator body latent;
- screen parameters;
- top activated visual receptor body IDs;
- a compact 64-column raster containing **one character per mapped visual receptor** using ` .:-=+*#%@` as the intensity scale.

The raster preserves every receptor. Optic-column-resolved receptors are ordered by eye/retinal coordinates; unresolved receptors remain present in deterministic order. It is telemetry, not a claim that the rectangular raster is the native retinal geometry.

Small public outputs include `screen-reward-summary.json`, `progress.jsonl`, `winner-retina.txt`, `winner-top-receptors.json`, the screen geometry manifest, interface manifest and provenance. Heavy arrays remain in Kaggle output.
