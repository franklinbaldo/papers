---
type: "OKF Type Spec"
title: "Paper Lifecycle Metadata"
description: "Repository-level OKF extension for marking papers and companion research documents as active, historical, superseded, or deprecated."
tags: [okf, lifecycle, papers]
timestamp: 2026-09-17T16:00:00Z
---

# Paper lifecycle metadata

This repository extends the permissive OKF v0.1 frontmatter model with a small, explicit lifecycle vocabulary for research documents. The extension does **not** modify the vendored upstream specification in [`SPEC.md`](SPEC.md); it is a producer-side schema for `franklinbaldo/papers`.

The goal is to distinguish scientific age from epistemic obsolescence. An old paper, a negative result, or a low-tier hypothesis is not deprecated merely for being old, negative, or speculative. Lifecycle status answers a narrower question: **should a reader treat this document as a current statement/evidence source, a historical record, a superseded formulation, or something that should no longer be relied upon?**

## Schema

The following producer-defined frontmatter keys are recognized:

```yaml
lifecycle_status: active | historical | superseded | deprecated
lifecycle_reason: <non-empty string>
superseded_by:
  - path/to/replacement.md
```

### `lifecycle_status`

Optional enum. If omitted, consumers and repository tooling MUST interpret the document as `active` for backward compatibility.

Allowed values:

- **`active`** — the document still represents a current paper, position, protocol, result, or supporting artifact. This does not imply that its claims are correct, mature, peer reviewed, or high quality.
- **`historical`** — retained because it records a meaningful stage of the programme, but it is no longer part of the current canonical reading path. Historical documents may remain scientifically useful as provenance.
- **`superseded`** — a later document has taken over the document's current role, formulation, or protocol. The older document remains useful for history/provenance but should not be cited as the current version when the successor applies.
- **`deprecated`** — the document should not be relied upon as a current source of evidence, guidance, or programme position. Typical reasons include unsupported claims that survived in an old artifact, invalidated methodology, misleading provenance, or a role that the programme has explicitly abandoned.

### `lifecycle_reason`

A concise explanation of **why** the document has a non-active lifecycle state. It is REQUIRED when `lifecycle_status` is `historical`, `superseded`, or `deprecated`, and optional for `active`.

Good reasons identify the epistemic transition, for example:

- `Raw AI-session prior-art assessment; independent reproducible review remains pending.`
- `Absorbed by sintese_programa.md after the doctrinal series stabilized.`
- `Protocol replaced by empirical_evaluation_v2.md after the preregistration changed.`

Do not use lifecycle reasons as quality scores or as substitutes for scientific criticism.

### `superseded_by`

Optional list of repository-relative `.md` paths naming documents that replace or absorb this document's current role.

Rules:

- REQUIRED when `lifecycle_status: superseded`.
- OPTIONAL for `historical` and `deprecated` when a clear successor exists.
- Normally omitted for `active`.
- Every listed target MUST exist in the repository and MUST NOT point back to the same file.

A document may be superseded by more than one successor when its former role was split across multiple papers.

## Decision rules

Use lifecycle state conservatively:

1. **Do not deprecate negative results.** A valid negative result is still evidence.
2. **Do not deprecate merely for age.** Age alone is not epistemic obsolescence.
3. **Do not deprecate merely for low scientific tier.** Tiering measures comparative maturity/strength; lifecycle measures whether the artifact remains current and usable for its stated role.
4. **Prefer `historical` when the document is still an honest record of a past stage.**
5. **Prefer `superseded` when a specific successor now carries the role.**
6. **Use `deprecated` when continuing to rely on the artifact would materially mislead a reader about evidence, methodology, provenance, or the programme's current position.**
7. Changing lifecycle state is a substantive editorial action. The commit/PR should identify the concrete reason and, for `superseded`, the successor.

## Examples

Current paper (implicit default):

```yaml
---
type: "Scientific Position Paper"
# lifecycle_status omitted => active
---
```

Superseded preregistration:

```yaml
---
type: "Empirical Paper"
lifecycle_status: superseded
lifecycle_reason: "The protocol was replaced after the experimental design changed materially."
superseded_by:
  - empirical_evaluation_v2.md
---
```

Deprecated companion artifact:

```yaml
---
type: "Companion Note"
lifecycle_status: deprecated
lifecycle_reason: "Raw AI-session prior-art assessment; its search is not independently reproducible and should not support originality claims."
superseded_by:
  - pontifex.md
---
```

## Consumer behavior

Repository indexes, the public `/papers` map, agents, and other consumers SHOULD:

- treat omitted `lifecycle_status` as `active`;
- keep historical/superseded/deprecated documents discoverable unless a separate archival policy says otherwise;
- visibly label non-active documents;
- prefer successors over superseded documents in canonical reading paths;
- avoid using deprecated documents as current evidence without explicitly discussing their deprecated status.

Lifecycle metadata is orthogonal to scientific/interest tiers, peer-review status, publication status, and document `type`.