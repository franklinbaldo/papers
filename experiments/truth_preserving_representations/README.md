---
type: "Companion Note"
title: "Truth-Preserving Representations — Toy Apparatus"
description: "Dependency-free exact checks for transport of structure, finite structural version spaces, and ambiguity under a non-injective decoder."
tags: [structural-identifiability, finite-groups, exact-enumeration, toy-experiment]
timestamp: 2026-08-24T01:35:00Z
---

# Truth-Preserving Representations — Toy Apparatus

This directory accompanies `truth_preserving_representations.md`.

It is deliberately small and exact. It does **not** contain a model-backed result and does not test whether a neural learner acquires structural representations. Its purpose is to verify the mathematical bookkeeping used by the position paper before a larger benchmark is built.

## What is tested

### 1. Full transport under arbitrary labels

`C4` is relabeled using the opaque codes

```text
(37, 12, 83, 51)
```

The operation is transported through the bijection. Every decoded product must equal the original group product.

Expected result:

```text
transport_preserves_all_products: True
```

The resulting encoded Cayley table is:

```text
37 -> 37 12 83 51
12 -> 12 83 51 37
83 -> 83 51 37 12
51 -> 51 37 12 83
```

This is the deliberately non-novel control: an arbitrary code plus exact transport is just an isomorphic copy.

### 2. Sparse local truths versus ambient structure

The frozen toy hypothesis class is

```text
C4, V4, C8, D4
```

where `D4` is the dihedral group of order eight.

The proxy for an “$i$-like” local multiplicative fact is existence of an element of order four.

Exact version spaces:

```text
local i-like fact                  -> C4, C8, D4
+ commutativity                    -> C4, C8
+ carrier order = 4                -> C4
```

The point is not the particular group list. It is that the same local truth becomes identifying or non-identifying depending on the declared background class.

### 3. Non-injective decoder

Let the latent code set be `{0,1,2}` and decode it to `C2` by

```text
0 -> 0
1 -> 0
2 -> 1
```

Every latent binary operation `*` is accepted when

```text
decode(x * y) = decode(x) + decode(y) mod 2
```

for every pair `(x,y)`.

Exact enumeration gives:

| Constraint | Labeled operations | Isomorphism classes |
| --- | ---: | ---: |
| decoded multiplication only | 32 | 16 magmas |
| + associativity | 4 | 2 semigroups |
| + two-sided identity | 2 | 1 monoid |

Thus exact behavior at the decoded interface can coexist with substantial latent structural ambiguity.

## Reproduce

No third-party package is required.

From the repository root:

```bash
python -m unittest discover -s experiments/truth_preserving_representations -p 'test_*.py' -v
python experiments/truth_preserving_representations/run.py
```

## Verified local result before commit

The exact code committed here was executed with Python 3 before being written to the branch:

```text
test_arbitrary_bijective_codes_preserve_c4_exactly ... ok
test_background_restriction_can_make_same_truth_identifying ... ok
test_commutativity_still_leaves_ambiguity ... ok
test_local_i_truth_does_not_identify_ambient_group ... ok
test_noninjective_decoder_allows_many_latent_lifts ... ok

Ran 5 tests in 0.001s
OK
```

Runtime is not a benchmark and may differ by machine.

## Research boundary

A future learned experiment must not count these exact enumeration checks as evidence for the main empirical hypotheses. In particular, it must separately test:

- held-out operation prediction;
- structural-class recovery up to isomorphism;
- calibration to the true structural version space;
- robustness under fresh carrier relabelings;
- and evidence efficiency under different truth-selection policies.

See `protocol.md` for the preregistered next gate.
