---
type: "Index"
title: "papers"
description: "Research workspace organized by active research line, with OKF-native concepts and preserved historical experiments."
okf_version: "0.2"
---

# papers

Research workspace for Franklin Silveira Baldo.

The repository is organized by **research line at the root**. Papers,
experiments, formalizations and line-specific prior-art work stay together.
Cross-cutting repository information lives in `about/`; concluded or
superseded research apparatus lives in `archive/`.

Start with [the bundle index](index.md) or the
[research map](about/research-map.md).

## Main active lines

- [Pontifex](pontifex/)
- [MaleCNS](malecns/)
- [Semantic Atlas](semantic-atlas/)
- [Auditable Legal Reasoning](auditable-legal-reasoning/)
- [Machine Discovery](machine-discovery/)
- [Machine Teaching](machine-teaching/)
- [Informational Time](informational-time/)
- [Relay Systems](relay-systems/)
- [Structural Identification](structural-identification/)
- [Schmidhuber Meter](schmidhuber-meter/)

Focused lines remain first-class root directories rather than being hidden in
a miscellaneous bucket.

## Repository-wide infrastructure

- [About](about/) — authorship, publication policy and research map.
- [Archive](archive/) — concluded/superseded experiments with historical vocabulary preserved.
- [Scripts](scripts/) — repository automation.
- [Audits](audits/) — genuinely cross-cutting/publication audits.
- [OKF contracts](.okf/) — bundle-local type specifications.

## Naming rule

Active canonical paths are semantic, lower-case and kebab-case. Historical
sequence labels such as `paper1g`, `phase3`, session and round numbers are
kept only where they are intrinsic to preserved experimental history.

## OKF

The repository targets OKF v0.2 and is validated by
`franklinbaldo/okf-parser`. The former vendored v0.1 specification and custom
validator are preserved under `archive/legacy-okf-v0.1/`.
