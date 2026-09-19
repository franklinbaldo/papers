---
type: "Protocol"
title: "Frozen rule: when a GPU state cache may be imported into the clean confirmatory"
description: "Pre-result import protocol freezing the admissibility gates and procedure for importing GPU-computed MaleCNS states into the clean confirmatory run."
tags: [malecns, protocol, gpu-cache, confirmatory]
timestamp: 2026-09-15T00:32:00Z
---

# Frozen rule: when a GPU state cache may be imported into the clean confirmatory

Registered 2026-09-15T00:32Z, while Kaggle run `34912592209` (kernel v5) was still
`in_progress` and no parity number existed. The point of writing it now is that
every branch below is decided before the result is visible, so nothing in the
import path can be chosen to suit an outcome.

## Standing facts this rule is written against

    runner commit       437083ae30f24f6f424ce405182d90b275b62621
    config hash         fef3c98965d20f43153e
    features hash       ab494d7e0b615c9633e7
    graph hash          214106d04307618db054cb977a691d48d431b771
    cache schema        2
    corpus              17 documents, 355 chunks, 9 tags
    gain grid           {0.0, 0.25, 0.5, 0.95, 1.5, 2.5, 4.0}
    seeds               0..9
    clean run           PID 17448, started 2026-09-14 20:29:03 local
    clean paths         artifacts/confirmatory-clean-20260914T202623/{states,result}

## Gates, all of which must pass

    input fingerprints    features and graph hashes exactly equal to the above
    state max_abs         <= 2e-3
    state relative RMSE   <= 2e-3
    |delta macroAP|       <= 1e-4
    |delta anyAUPRC|      <= 1e-4

Any single failure is a FAIL. There is no partial credit and no re-tuning of a
threshold after seeing a number.

## FAIL

Nothing happens. The clean CPU run is not touched, not stopped, not fed. It
finishes on its own and is the confirmatory reference. The GPU cache is discarded
for this purpose.

## PASS

In this order, and only in this order:

1. Confirm the current clean checkpoint is valid — it parses, and its
   `config_hash` is `fef3c98965d20f43153e`.
2. Snapshot the checkpoint and `states/` before anything is added.
3. Stop the single CPU run in a controlled way, children before parents.
4. Copy from the GPU cache **only files that are absent**. A state the clean CPU
   run already computed is never overwritten. The CPU result wins every
   collision, because it is the reference and the GPU is the accelerator.
5. Verify every imported filename is a schema-2 key built from the frozen
   fingerprints. A key that does not reconstruct from
   (schema=2, features=ab494d7e…, graph=214106d0…b771, inputs, readout,
   projection, calibration, normalisation) is not imported.
6. Relaunch the identical command, at commit `437083a`, and confirm the
   checkpoint still reports config hash `fef3c98965d20f43153e`.

The runner then performs nested `(gain, ridge)` selection and F2/F3 adjudication
exactly as it would have. Importing states changes which machine multiplied the
matrices and nothing else: no metric, no selection, no null, no comparator.

## What this rule deliberately does not allow

- Copying anything while the CPU run is live.
- Overwriting a CPU-computed state with a GPU one.
- Importing states whose key does not match the frozen fingerprints.
- Editing the runner, the grid, the seeds or the thresholds after the start.
- Treating a 429/503 from Kaggle as a scientific result in either direction.

## Note on the runner SHA

This document is committed on top of `437083a`, so `HEAD` will no longer equal
that SHA. The runner itself is unchanged: verification at relaunch is that
`git hash-object` of `scripts/run_confirmatory.py`, `src/malecns_wifi/multitag.py`
and `src/malecns_wifi/tagger.py` still equals their blobs in `437083a`, not that
`HEAD` equals it.
