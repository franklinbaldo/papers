# OKF adoption for this repository

This directory documents how `franklinbaldo/papers` applies the Open
Knowledge Format (OKF) to its own documents: every non-reserved `.md`
file in this repository carries OKF frontmatter, this repository
defines a closed set of `type` values, and CI checks conformance on
every pull request.

# Specification

* [SPEC.md](SPEC.md) - vendored copy of OKF v0.1, the version this repository targets.
* [publication.md](publication.md) - repository-local `publication` frontmatter state machine and external-publication provenance records.

# Canonical concepts

* [Schmidhuber Meter](schmidhuber-meter.md) - claim-level Citation Debt Index based only on public temporal priority, substantive overlap, historical discoverability, observed credit, and separately measured impact.

# Types

* [Dogmatic Paper](types/dogmatic-paper.md) - CPC 2015 doctrinal thesis papers (the 1A-1G series plus the umbrella paper).
* [Technical Paper](types/technical-paper.md) - English methodology/tooling papers (pipeline, provenance, ESHTR, STT).
* [Scientific Position Paper](types/scientific-position-paper.md) - research-grounded natural-science hypotheses, syntheses, and falsifiable research agendas.
* [Empirical Paper](types/empirical-paper.md) - pre-registered empirical evaluation design.
* [Synthesis Paper](types/synthesis-paper.md) - capstone paper summarizing programme coherence.
* [Alignment Paper](types/alignment-paper.md) - general AI alignment position paper.
* [Interpretability Paper](types/interpretability-paper.md) - general interpretability position paper.
* [Companion Note](types/companion-note.md) - subordinate supporting document for a paper.
* [Adversarial Critique](types/adversarial-critique.md) - living attack thread against a paper's thesis.
* [Adversarial Blog](types/adversarial-blog.md) - dated long-form record of one substantive adversarial round.
* [Supportive Defense](types/supportive-defense.md) - living defense thread for a paper's thesis.
* [Supportive Blog](types/supportive-blog.md) - dated supportive-session record that preserves a complete round-specific defense and its assessment.
* [Session Log Entry](types/session-log-entry.md) - dated changelog entry for one debate-apparatus session.
* [Protocol](types/protocol.md) - canonical rules document for a repeatable process.
* [Audit Report](types/audit-report.md) - dated external review with findings and execution status.
* [Citation Debt Assessment](types/citation-debt-assessment.md) - claim-by-claim auditable record used to compute the Schmidhuber Meter without inferring private intent or causal derivation.
* [Session Log](types/session-log.md) - superseded precursor to Session Log Entry.
* [Index](types/catalog-index.md) - human-facing catalog and reading guide (this repository's `README.md`).
* [Reference](types/reference.md) - vendored external material, mirrored into this repository so its OKF adoption does not depend on that material staying reachable (`okf/SPEC.md`).
* [Author](types/author.md) - canonical reusable identity record for paper authors and future coauthors.
* [OKF Type Spec](types/okf-type-spec.md) - a document that specifies how one type should be used (this list's own entries).

# Tooling

* [validate.py](validate.py) - conformance checker; also runs in CI on every pull request.
