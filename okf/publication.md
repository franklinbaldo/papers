---
type: "Protocol"
title: "Publication State"
description: "Repository-local OKF extension for tracking manuscript publication readiness and external publication records without conflating Git history with venue publication."
tags: [okf, publication, arxiv, provenance]
timestamp: 2026-09-18T14:00:00-04:00
---

# Publication State

This repository uses an optional `publication` frontmatter object on paper
concepts. It is a producer-defined OKF extension: OKF v0.1 explicitly permits
additional frontmatter keys.

The field has two jobs that must stay separate:

1. `publication.status` describes the publication workflow state of the
   **current working version** of the manuscript.
2. `publication.records` preserves external submission/publication events
   already attained by earlier or current versions.

That distinction matters for revisions. A paper may have an announced arXiv
`v1` in `records` while the current manuscript has returned to `draft` or
`ready` for a future `v2`.

## Minimal form

```yaml
publication:
  status: draft
```

## States

The closed state vocabulary is:

- `draft` — manuscript is still being edited and is not approved as a frozen
  external-submission candidate.
- `ready` — the current version is approved/frozen enough to prepare or submit
  to one or more external publication targets.
- `submitted` — the current version has been sent to at least one external
  service, but that submission has not yet reached the repository's
  `announced` condition.
- `announced` — the current version has a public external record suitable for
  citation and temporal-priority evidence.

These states are workflow states, not quality judgments. In particular,
`ready` does not mean peer reviewed, and `announced` does not mean accepted
by a journal or conference.

## Targets

A paper MAY name intended destinations before submission:

```yaml
publication:
  status: ready
  targets: [arxiv, zenodo]
```

`targets` is advisory and intentionally open-ended. The validator only
requires it to be a list of non-empty strings.

## Public Zenodo rights policy

For a public Zenodo deposit under the repository's current authorial policy,
the content remains publicly accessible while economic/commercial reuse is the
restricted category. The current Zenodo metadata representation is therefore:

```yaml
publication:
  status: ready
  targets: [zenodo]
  zenodo:
    access_right: open
    license: cc-by-nc-4.0
```

The license MUST still be explicit in each Zenodo-ready paper. This repository
policy removes the need to re-open the same rights choice paper by paper, but
it does not make a draft manuscript `ready` and does not resolve scientific,
editorial, doctrinal, versioning, or archival-scope decisions.

This policy records the present grant only. It does not encode an automatic
relicensing date or a future ten-year change rule. Any later time-triggered
additional grant must be recorded separately and explicitly rather than being
inferred from `cc-by-nc-4.0`.

## External records

External events are recorded under `records`:

```yaml
publication:
  status: announced
  targets: [arxiv, zenodo]
  records:
    - venue: arxiv
      status: announced
      identifier: "2609.01234"
      version: "v1"
      submitted_at: "2026-09-18T18:00:00Z"
      announced_at: "2026-09-19T00:00:00Z"
      url: "https://arxiv.org/abs/2609.01234"
      source_commit: "0123456789abcdef0123456789abcdef01234567"
      bundle_sha256: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
```

Each record MUST have:

- `venue` — non-empty external service name, e.g. `arxiv`, `zenodo`,
  `ssrn`;
- `status` — `submitted` or `announced`.

An `announced` record SHOULD additionally carry a stable public
`identifier`, canonical `url`, and `announced_at`.

The following provenance fields are strongly recommended whenever known:

- `source_commit` — exact 40-character Git commit whose manuscript state was
  packaged for the external submission;
- `bundle_sha256` — SHA-256 of the exact submission bundle;
- `version` — external version label such as arXiv `v1`.

Records SHOULD be append-only. Correct factual mistakes by editing the affected
record with an explanatory commit, not by silently deleting publication
history.

## Relationship to priority claims

Git history and external publication are distinct evidence streams.

A Git commit/PR may remain the earliest public evidence of a claim. An arXiv,
Zenodo, SSRN, proceedings, DOI, or other external record may later provide
additional independently timestamped evidence. Prior-art audits MUST continue
to reconstruct the earliest public date of each specific claim rather than
blindly substituting `publication.records[*].announced_at` for claim history.

## Validation

`okf/validate.py` validates this extension when the `publication` key is
present. Existing documents without the key remain conformant so publication
metadata can be adopted incrementally.
