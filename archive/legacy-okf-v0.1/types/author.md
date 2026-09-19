---
type: "OKF Type Spec"
title: "Author"
description: "Canonical identity concept for a person who authors or coauthors papers in this repository."
tags: [okf-type-spec, authorship]
timestamp: 2026-09-18T13:20:00-04:00
---

# Author

**`type` value:** `"Author"`  
**Applies to:** files under `authors/`, one concept per person.

## Purpose

An `Author` is a reusable canonical identity record. Papers SHOULD refer to
author concepts instead of duplicating identity metadata independently in every
manuscript. This allows coauthorship, author-order changes, ORCID/Lattes
reconciliation, and affiliation changes without conflating the person with one
paper.

The concept represents the person. Paper-specific authorship facts such as
author order, byline spelling, corresponding-author status, and affiliation used
for a particular submission belong on the paper.

## Required fields (beyond OKF baseline)

- `title` — canonical human-readable name.

## Recommended fields

- `publication_name` — default byline form used when a paper does not override it.
- `identifiers` — list of external identity records, each with `scheme`, `value`,
  and optionally `url`; examples: `orcid`, `lattes`, `github`.
- `aliases` — other published/name variants.
- `affiliations` — known/default affiliations; these are identity context, not a
  substitute for the affiliation recorded for a specific submission.
- `timestamp` — last meaningful change to the author record.

No particular identifier is required because future coauthors may not have
ORCID, Lattes, GitHub, or any other specific registry.

## Paper authorship convention

Papers that adopt structured authorship SHOULD use an ordered `authors` list in
frontmatter. Each entry references an Author concept:

```yaml
authors:
  - ref: /authors/franklin-silveira-baldo.md
    byline: "Franklin Baldo"
    affiliations:
      - "Independent Researcher"
    corresponding: true
```

The list order is the author order for that manuscript. `byline`,
`affiliations`, and `corresponding` are paper-specific overrides and are
optional.

Future coauthors get their own `authors/<slug>.md` concept and another entry in
the paper's ordered list. Do not embed one author inside another author's record.

## Notes

The Author concept is deliberately independent of publication venue. arXiv,
Zenodo, journals, conference proceedings, SSRN, and other targets can all consume
the same identity record while preserving venue-specific metadata elsewhere.
