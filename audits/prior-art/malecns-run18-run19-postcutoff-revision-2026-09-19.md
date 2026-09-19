---
type: "Audit Report"
title: "RUN18 prior-art audit revision — RUN19 post-cutoff clock-health evidence — 2026-09-19"
description: "Post-cutoff revision to the RUN18 innovation/covariance audit after RUN19 became public during the audit round, preserving priority and truth-status axes separately."
tags: [malecns, prior-art, later-derivative, falsification, driving, sensor-fusion, innovation, covariance, clock-health, imu, gnss]
timestamp: 2026-09-19T16:08:00Z
---

# RUN18 audit revision — RUN19 post-cutoff clock-health evidence

This revision supplements [`malecns-run18-innovation-covariance-2026-09-19.md`](./malecns-run18-innovation-covariance-2026-09-19.md). It exists because `main` advanced with RUN19 while the RUN18 audit was being prepared. The new evidence is temporally **after** the RUN18 cutoff and must not be folded backward into prior art.

## Temporal relation

RUN18 conservative public cutoff: **2026-09-19 15:08:24 UTC** (PR #667 creation).

RUN19 / PR [#682](https://github.com/franklinbaldo/papers/pull/682) was created at **2026-09-19 16:06:20 UTC** and merged at **16:06:51 UTC**, nearly an hour later. Its manuscript explicitly starts from the statement that **“Run 18 assumes that the reported sensor timestamp corresponds to the physical measurement instant”** and then stress-tests the RUN18 covariance baseline with a phone-IMU clock-health witness.

**Classification:** `later_derivative` with high confidence. The dependency is positive and explicit in the RUN19 artifact; this is not merely temporal similarity.

## What RUN19 adds to RUN18 truth status

RUN19 tests a boundary that RUN18 itself left open: timing metadata can be wrong even when sensor values and arrival latency look ordinary.

With clean OBD and GNSS offset+jitter, RUN19 reports:

- OBD/control MAE: `0.148333`;
- RUN18-style covariance baseline: `0.199772`;
- covariance + phone-IMU clock merit: `0.189464`.

The independent kinematic witness therefore limits damage by about **5.16% relative to the covariance baseline**, but the corrected arm still substantially trails the simple OBD control. Under clean timing, the merit is essentially neutral/slightly beneficial; under drifting/static OBD bias the benefit is smaller and not universal.

### Classification

For RUN18's implicit timestamp-contract premise:

- `boundary_condition`, strength **strong**: innovation/covariance adaptation is not sufficient when the measurement time itself is wrong;
- `contrary_evidence`, strength **moderate** against any broad reading that residual/covariance adaptation alone makes the fusion path robust to asynchronous sensing.

**Target attacked:** mechanism/generalization, not the RUN18 frozen-table arithmetic.

**Required action:** `add_boundary_condition + add_control`. Preserve reported timestamp health as a separate observable channel; compare attenuation against actual clock-offset estimation/interpolation rather than treating clock merit as a substitute for synchronization.

## Epistemic consequence

RUN19 reinforces the RUN18 audit's main correction: residual energy is not self-interpreting. Large disagreement may arise from sensor noise, persistent bias, cross-channel correlation, state dynamics **or timestamp corruption**. A scalar innovation scale cannot identify those causes without extra assumptions or independent witnesses.

It also reinforces the project-level ordering: this is useful diagnostic/remediation machinery, not another reason to delay the first direct MaleCNS driving loop. RUN19 itself calls the IMU signal a guard/decision signal rather than a universal fusion rule. The car programme should keep these mechanisms available as controls when concrete driving failures demand them.

## Priority remains unchanged

RUN19 is later than RUN18 and therefore does **not** alter RUN18's temporal priority relative to external pre-cutoff literature. It changes only the current `truth_status`/boundary analysis.
