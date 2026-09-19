---
type: "Protocol"
title: "Semantic Atlas — Dynamic Gauge Compression Test v1"
description: "Preregistered model-backed test of whether one external frozen dynamic gauge makes independently calibrated model transition fields simpler and more mutually concordant without learning the gauge from those dynamics."
tags: [semantic-atlas, dqrf, dynamic-gauge, compression, cross-model, preregistration]
timestamp: 2026-09-08T21:32:00-04:00
---

# Semantic Atlas — Dynamic Gauge Compression Test v1

## 1. Question

The foundational DQRF claim is not that a vortical feature bank contains new information. A deterministic coordinate transform cannot do that. The claim under test is instead representational:

> **Can one external, frozen, shared dynamic gauge redistribute model-specific transition complexity into residuals that are simpler and more transferable than the un-gauged dynamics?**

For observer/model \(M\), let \(q\) be the calibrated Semantic Reference Frame state and let \(F_M(q)\) be the observed one-step semantic displacement along generated trajectories. For frozen candidate field \(\mathcal V^{(k)}\), fit only a preregistered low-capacity amplitude and write

\[
F_M(q)=a_M^{(k)}(q)\,\mathcal V^{(k)}(q)+r_M^{(k)}(q).
\]

DGCT asks whether \(r_M^{(k)}\) is easier to describe and predict than \(F_M\), and whether residual structure agrees better across independently calibrated observers.

## 2. Epistemic firewall

The external field is a ruler, not a learned model of the object being measured. Therefore all of the following are frozen in `dynamic_gauge_compression_v1.json` **before model-backed transition fields are generated or inspected**:

- field family;
- field dimension;
- quasar centers (the already-defined regular-simplex SRF quasars);
- random seeds;
- radial scale;
- field strength;
- amplitude model class and ridge;
- trajectory-level train/test split seed and fraction;
- residual-predictor class and ridge;
- sample-complexity fractions and target error.

No plane, chirality, scale, seed, envelope, field normalization, or field family may be selected after looking at \(F_M\) and still count as confirmatory DGCT-v1 evidence. Any such tuning is exploratory and requires a new frozen manifest for confirmation.

## 3. Data and observers

DGCT-v1 inherits the frozen corpus, generator, observer revisions, SRF dimension, generation seeds, chunking and sampling settings from `model_backed_a_v1.json`.

The generator produces each continuation once. The same cumulative text states are then embedded independently by the reference observer and transfer observer. Each observer is calibrated into the common SRF using only the frozen calibration corpus and the existing paired-Procrustes contract.

For a generated trajectory

\[
q_0,q_1,\ldots,q_T,
\]

DGCT samples

\[
(q_t,F_t),\qquad F_t=q_{t+1}-q_t.
\]

The prompt itself is included as \(q_0\), followed by cumulative continuation chunks, so every generated trajectory contributes all successive one-step displacements.

Train/test splitting occurs by **whole trajectory**, not by individual adjacent steps, preventing neighboring states from the same continuation from leaking across the split. The same split keys are applied to both observers.

## 4. Frozen field families

DGCT-v1 tests only the first, deliberately simple hierarchy:

1. **zero** — the un-gauged baseline, \(\mathcal V=0\);
2. **radial_gradient** — smooth non-vortical gradient control;
3. **vortex_smooth** — smooth bounded vortical gauge with a sparse seeded antisymmetric generator;
4. **random_divergence_free** — smooth bounded control with a dense seeded antisymmetric generator.

For antisymmetric \(A\) and radial envelope \(g(\|r\|)\), each component has form

\[
\mathcal V(r)=g(\|r\|)Ar.
\]

Because \(r^TAr=0\) and \(\operatorname{tr}A=0\), its divergence is zero in the canonical Euclidean coordinates. The implemented field is a finite superposition around the fixed artificial quasar centers.

**No multiscale, self-similar, or Navier--Stokes-inspired field is tested in v1.** Those are terminal hypotheses and earn evaluation only if simpler dynamic gauges show evidence-bearing compression.

## 5. Amplitude fit

DGCT-v1 fits one constant scalar amplitude per observer and field:

\[
a_M^{(k)}=
\arg\min_a
\sum_{q\in\text{train}}
\left\|F_M(q)-a\mathcal V^{(k)}(q)\right\|_2^2.
\]

The implementation also supports an affine low-capacity amplitude for future preregistrations, but v1 does not enable it. This avoids letting a flexible \(a(q)\) silently become the real transition model.

Amplitude fitting uses training trajectories only. All primary complexity measurements are reported separately on held-out trajectories.

## 6. Complexity vector

There is deliberately no tunable weighted scalar called “complexity.” For both raw dynamics and residual dynamics, DGCT reports the following vector.

### 6.1 Residual energy

\[
E(X)=\mathbb E\|X\|_2^2.
\]

Primary ratio:

\[
C_E=\frac{E(r_M)}{E(F_M)}.
\]

Lower is better. This is necessary but not sufficient: a field could remove magnitude without making the remainder structurally simple.

### 6.2 Entropy effective rank

For centered sample matrix \(X\) with squared singular-value probabilities \(p_i\),

\[
r_{eff}(X)=\exp\left(-\sum_i p_i\log p_i\right).
\]

Primary ratio:

\[
C_R=\frac{r_{eff}(r_M)}{r_{eff}(F_M)}.
\]

Lower values indicate that residual variation occupies fewer effective directions.

### 6.3 Predictive sample complexity

A fixed affine ridge predictor maps \(q\) to either raw dynamics or residual dynamics. Using nested deterministic fractions of the training set, DGCT measures held-out relative MSE and records the smallest sample count reaching the frozen target relative MSE.

A useful gauge should not merely lower target magnitude; it should make a low-capacity predictor learn the remainder with fewer samples and/or lower held-out relative error.

### 6.4 Local sensitivity

On observed support, DGCT reports the median nearest-neighbor ratio

\[
S(X)=\operatorname{median}_i
\frac{\|X_i-X_{n(i)}\|}{\|q_i-q_{n(i)}\|}.
\]

Lower residual sensitivity is evidence that the gauge has factored out rapidly varying structure. This is a local observed-support proxy, not a claim of global Lipschitz regularity.

### 6.5 Cross-model residual concordance

Because both observers are already in the common SRF, DGCT compares paired held-out raw dynamics and paired held-out residuals using:

- mean row cosine;
- normalized RMSE;
- correlation of pairwise residual distances.

The strongest outcome is not merely \(C_E<1\) inside each model. It is that **the same frozen gauge makes independently calibrated observers leave behind residuals that are simultaneously simpler and more mutually concordant**.

## 7. Foundational comparison

For every frozen field \(k\) and observer \(M\), report

\[
\mathcal C_M^{(k)}=
\left(
C_E,
C_R,
N_\epsilon,
S,
\text{held-out prediction curve}
\right).
\]

For each field also report cross-observer concordance of \(r_A^{(k)}\) and \(r_B^{(k)}\), alongside the raw \(F_A,F_B\) concordance.

The scientific result is a **Pareto-style vector comparison**, not a post-hoc weighted score. No field earns a claim merely by winning one metric while materially worsening the others.

## 8. Interpretation ladder

Results must be interpreted at the narrowest surviving level:

```text
dynamic gauge
    ⊃ vortical gauge
        ⊃ self-similar vortical gauge
            ⊃ Navier–Stokes-inspired gauge
```

- If all nonzero fields fail to simplify residuals beyond the zero baseline, the dynamic-gauge claim fails.
- If several unrelated frozen fields simplify equally, generic feature/gauge structure may matter but vortex specificity is unsupported.
- If `vortex_smooth` beats non-vortical and random divergence-free controls under matched complexity, a vortex-specific follow-up is justified.
- Self-similar and Navier–Stokes-inspired gauges are **not tested here**.

## 9. Falsifiers

DGCT-v1 counts against the proposal when any of the following occurs:

1. residual energy is not materially lower on held-out trajectories;
2. effective rank does not decrease or worsens;
3. residual predictive sample complexity does not improve;
4. local residual sensitivity does not improve;
5. cross-model residual concordance does not improve over raw dynamics;
6. any apparent advantage vanishes against the frozen radial or random divergence-free controls;
7. the result depends on tuning field parameters after transition data are visible;
8. improvement appears only in training trajectories;
9. one observer compresses while the other becomes substantially more complex;
10. a result is described as evidence for Navier--Stokes structure despite v1 not testing such a field.

Partial rejection is expected and scientifically useful.

## 10. Execution and artifact

Cheap CI tests only deterministic field, decomposition and metric primitives. The registered model-backed run is intentionally manual because it downloads pinned models and generates continuations.

Expected command:

```bash
pip install -e '.[models]'
python scripts/run_dynamic_gauge_compression.py
```

Expected artifact:

```text
artifacts/dynamic_gauge_compression_v1.json
```

A successful process exit means only that the preregistered measurement ran. It is **not** a positive scientific result.
