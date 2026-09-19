---
type: Experiment Report
title: "Pontifex CMB: multi-remote locality control"
date: 2026-09-19
status: experimental
---

# Pontifex CMB: multi-remote locality control

## Question

The preceding matched remote-ring control falsified the simplest locality interpretation: a single ring translated by half a period predicted observation width about as well as the lesion-adjacent ring. However, one remote location is an arbitrary control and can itself be unusually informative.

This experiment asks the stricter question: **is the lesion-adjacent descriptor exceptional relative to a predeclared ensemble of matched remote locations?**

The discriminant was fixed before held-out outcomes were generated:

- LOCAL: roughness in the lesion-adjacent context ring;
- REMOTE-0/1/2: the identical roughness statistic at periodic shifts `+0.25`, `+0.50`, and `+0.75`;
- REMOTE-ENSEMBLE: the median log-roughness across those three remote rings;
- FIXED: the already frozen `w = 0.5 × lesion radius` baseline.

All adaptive rules use the same three-bin model class and are fitted only on development skies.

## Geometry gate

The geometry filter is outcome-free. A theta is retained only when:

1. every remote context ring has at least four pixels;
2. every remote context ring is disjoint from the local lesion support;
3. the three remote context rings are pairwise disjoint.

Of 60 balanced theta samples, **45 passed** this gate. No outcome was inspected when making these exclusions.

The experiment then used:

- 12 independent development base skies;
- 24 independent held-out base skies;
- metric spectra `k0 = {4, 8, 16}` nested within each base sky;
- candidate widths `{0.125, 0.25, 0.5, 1.0}`;
- independent base-sky seed as the inferential unit.

This produced 1,620 development rows and 3,240 held-out rows.

## Development result

The development fit itself is informative.

LOCAL selected:

`[0.5, 0.5, 0.5]`

so the local adaptive controller **collapsed exactly to the fixed baseline** on this new cohort.

The three single-remote controllers each selected:

`[0.5, 0.5, 0.25]`

and the REMOTE-ENSEMBLE controller also selected:

`[0.5, 0.5, 0.25]`.

This is already a warning against treating the earlier `[0.5, 0.5, 0.25]` LOCAL rule as a stable property of the harness. The current geometry-matched cohort and new sky/theta seed did not recover it locally.

## Held-out results

### Primary locality discriminant

LOCAL minus the median of the three independently fitted single-REMOTE controllers:

- mean difference: **+0.0022145**;
- median difference: **+0.0010446**;
- 16 positive skies, 8 negative, 0 ties;
- exact two-sided sign test: **p = 0.15159**;
- Holm-adjusted: **p = 0.45477**.

Therefore the predeclared positive-locality criterion was **not met**.

Although LOCAL ranked first among the four single-location controllers in 12/24 held-out skies, that descriptive asymmetry is insufficient to establish locality under the predeclared inferential test.

### Remote-ensemble control

LOCAL minus REMOTE-ENSEMBLE:

- mean difference: **+0.0010995**;
- median difference: **+0.0000033**;
- 12 positive, 10 negative, 2 ties;
- exact sign test: **p = 0.83181**;
- Holm-adjusted: **p = 1.0**.

REMOTE-ENSEMBLE minus FIXED is the exact opposite in this run:

- mean difference: **-0.0010995**;
- median difference: **-0.0000033**;
- 10 positive, 12 negative, 2 ties;
- exact sign test: **p = 0.83181**;
- Holm-adjusted: **p = 1.0**.

So the stronger alternative explanation — that a spatially broad roughness estimate reliably improves scale selection — is **also not confirmed** here.

### Descriptor geography

The LOCAL descriptor is correlated with the median remote descriptor, but much less strongly than in the previous single-remote experiment:

- Pearson `r(local, remote-ensemble) = 0.75138`.

At row level, the LOCAL descriptor's rank among LOCAL + three REMOTE descriptors was nearly uniform:

- rank 1: 829 / 3,240;
- rank 2: 806 / 3,240;
- rank 3: 829 / 3,240;
- rank 4: 776 / 3,240.

The median `log(local roughness) - median(log(remote roughness))` was only **+0.00242**. The local neighborhood is therefore not descriptively exceptional in roughness magnitude across this matched cohort.

## Scientific interpretation

This is a useful **negative replication**.

The earlier experiments established that pre-intervention roughness can correlate with useful observation width, and a single remote ring showed that the information need not be lesion-local. The present stricter experiment does not reproduce a reliable adaptive advantage for either the local descriptor or the median of three remote descriptors.

What the current evidence supports is narrower:

1. the fixed intermediate scale `w = 0.5` remains a robust synthetic baseline;
2. locality is not established by the current roughness statistic;
3. the previously observed adaptive gain is **cohort-sensitive** under changes in theta panel, sky seed, and the stricter multi-remote geometry gate;
4. neither a lesion-local nor a spatially broad scalar roughness controller has yet earned status as a stable control law.

A tempting post-hoc explanation is that the strict multi-remote geometry gate preferentially removes large lesions and changes the roughness/scale relationship. That is a **hypothesis**, not an explanation established by this run. We do not retune bins, shifts, theta radius range, or controller class after seeing the held-out result.

## Evidence boundary

This experiment is evidence only about calibration and scale selection inside the current **synthetic Pontifex CMB harness**.

It does **not** establish:

- a physical CMB scale;
- a Planck or ACT beam law;
- a real-sky anomaly;
- physical nonlocality;
- Torus causality;
- that roughness is the relevant latent variable in real data.

The development/held-out split here is internal to this synthetic calibration experiment. It is not a substitute for any downstream learning boundary.

The downstream separation remains strict and untouched:

`D_assembly ⟂ D_student ⟂ D_val ⟂ D_test`.

No assembly, student-training, validation, or test data are used in this experiment.

## Next discriminant

The next experiment should separate **cohort shift** from **descriptor failure** without post-hoc retuning: take the exact accepted-theta mask from this multi-remote geometry gate and evaluate, on common skies, both the previous single-remote protocol and the new multi-remote protocol. If the adaptive gain disappears solely when the theta cohort is restricted, geometry selection is the likely source; if it survives the cohort restriction but disappears only under remote ensembling, the descriptor/control construction is the more likely source.
