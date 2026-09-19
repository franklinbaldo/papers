---
type: "Audit Report"
title: "Paper 1C — candidate-ratio and provenance heuristic prior-art audit — 2026-09-19"
description: "Claim-specific temporal audit of Paper 1C's fragmented-majority candidate-ratio procedure and claim-provenance/status machinery, with a publication-safe boundary between descriptive CPC mapping and proposed computational heuristics."
tags: [paper1c, prior-art, ratio-decidendi, plurality, fragmented-majority, provenance, computational-law]
timestamp: 2026-09-19T16:38:00-04:00
---

# Paper 1C — candidate-ratio and provenance heuristic prior-art audit — 2026-09-19

## Status

This audit covers the proposal-bearing parts of `paper1C_categorias_processuais_formalizacao.md`, especially the `quadro de rationes candidatas` introduced after the original descriptive paper and the provenance/status annotations used for computational formalization. It is a bounded temporal search, not an exhaustive novelty, patent, copying, or priority determination.

## 1. Claim boundary and cutoff

The repository history shows that the candidate-ratio extension was introduced by commit `57ac8d76e4540a35f7541353e60bc657cc95fc20`, authored **2026-07-16 10:11:23 UTC**. That commit explicitly adds a procedure for fragmented-majority decisions: identify vote-level grounds, cluster votes by shared grounds, and emit candidate ratios with support/status/scope metadata. The audit therefore uses **2026-07-16 10:11:23 UTC** as the conservative cutoff for that proposal.

The general CPC categories in the paper are descriptive and are not audited as originality claims. The generic idea of attaching provenance metadata to assertions is also treated as occupied infrastructure rather than a novelty claim.

## 2. Claims audited

- **C1 — majority-ground requirement:** a collegiate result does not necessarily yield one binding ratio if the judges forming the result do not share a material legal ground.
- **C2 — fragmented-decision extraction:** when reasoning is fractured, inspect individual opinions/votes and identify shared or nested grounds rather than infer a ratio from the dispositive result alone.
- **C3 — candidate-ratio heuristic:** when no unique majority ground can safely be extracted, retain multiple candidate grounds with explicit supporting votes, scope and epistemic status instead of silently selecting one as binding.
- **C4 — provenance metadata:** formal assertions should preserve source/derivation information and uncertainty/status metadata so later users can distinguish directly sourced, inferred and unresolved assertions.
- **C5 — procedural propagation:** a proposition present in one procedural document can later be expressly adopted as a ground in another document, but that textual derivation does not by itself determine res judicata, preclusion, appeal scope, admission or any other procedural effect.

## 3. Pre-cutoff prior art

### 3.1 Brazilian precedent doctrine already separates majority result from majority reasoning

Luiz Guilherme Marinoni's work on decisions of supreme courts and precedents, published before the cutoff, directly addresses the problem that a resource may be decided by majority even though no legal ground is supported by a majority. Brazilian literature on precedent likewise treats the ratio as dependent on reasons actually shared by the deciding coalition, not merely the numerical result.

A public 2017 discussion of `Precedente, Decisão Majoritária e Pluralidade de Fundamentos` states the problem in substantially these terms: for precedent purposes, the relevant question is how many judges sustain the same ground, not simply how many support the disposition. It also discusses the United States plurality-opinion problem and the `narrowest grounds` approach.

**Classification:** C1 is `prior_art`. C2 is at least `partial_prior_art`.

### 3.2 Marks v. United States (1977) is direct comparative prior art for fractured-decision extraction

In `Marks v. United States`, 430 U.S. 188 (1977), the U.S. Supreme Court stated that when no single rationale explaining a fragmented decision has majority assent, the holding may be viewed as the position taken by those concurring in the judgment on the narrowest grounds. Later U.S. cases and scholarship show that this rule is difficult or indeterminate when opinions lack a logical common denominator.

This is not a Brazilian rule and should not be imported mechanically. It does establish decades-old prior art for the computational/legal problem `fractured result → inspect reasoning relationships → attempt a common/narrow ground → admit indeterminacy when no suitable relation exists`.

**Classification:** C2 is `prior_art` at the generic problem/solution-family level. C3 remains a narrower implementation choice.

Primary comparative source: <https://supreme.justia.com/cases/federal/us/430/188/>.

### 3.3 Provenance as structured metadata is established infrastructure

The W3C PROV family became a Recommendation in 2013. PROV supplies a general model for representing entities, activities, agents, derivations and provenance relationships and explicitly supports assessments of quality, reliability and trustworthiness. This predates Paper 1C by more than a decade.

Legal AI also has a long line of argument-graph and judicial-interpretation representation work. Examples include formal models of legal argumentation/case reasoning and JudO, an OWL ontology library for representing judicial interpretations and reasoning in precedents.

**Classification:** C4's generic `claim + source/derivation/status metadata` architecture is `prior_art` / established infrastructure. Paper 1C may specify a domain-specific annotation profile but should not claim the underlying provenance concept as new.

W3C source: <https://www.w3.org/TR/2013/REC-prov-o-20130430/>.

### 3.4 Textual adoption is not automatic procedural effect

The CPC itself supplies decisive constraints. Article 503 gives force of law to the principal issue expressly decided and extends this to prejudicial issues only under the conditions of §1. Article 504 expressly excludes reasons—even important ones—and the truth of facts used as grounds from res judicata. Article 507 separately addresses preclusion of issues already decided in the process. Article 1.013 separately structures the devolutive scope of appeal.

Therefore a provenance edge such as `later-document derives-from earlier-claim` cannot itself entail `res judicata`, `accepted`, `precluded`, `within appellate scope`, or `binding ratio`.

**Classification:** any strong version of C5 that assigns those legal effects from provenance alone is unsupported and must be removed. The defensible residual is a computational traceability rule: preserve the derivation and then evaluate the relevant legal effect under its independent legal conditions.

Primary source: <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm>.

## 4. Residual contribution that survives the audit

The publication-safe contribution is not a new doctrine of precedent or a new theory of provenance. It is a **formalizer-facing heuristic/profile** that combines established constraints:

1. identify vote-level grounds and their support;
2. if a genuinely shared majority ground exists, record that shared ground with its supporting coalition;
3. if no unique shared majority ground can be established, emit a **set of candidate grounds** rather than fabricate a single ratio;
4. attach support, scope, source and epistemic-status metadata to every candidate;
5. mark the output `pending/non-binding inference` unless an independent legal analysis establishes controlling status;
6. never choose the candidate “closest” to the new case merely because it is computationally convenient;
7. keep provenance/derivation distinct from legal consequences such as res judicata, preclusion, admission, congruence or devolutive scope.

No exhaustive-firstness claim is made for this exact conjunction. Its value is operational discipline for formalization, not priority over the established plurality-opinion, precedent, argument-graph or provenance literatures.

## 5. Required manuscript correction

For Zenodo readiness, Paper 1C should:

- call `quadro de rationes candidatas` a **proposed computational/interpretive heuristic**, not a descriptive rule of Brazilian law;
- remove any statement that the heuristic is a “complete procedure” that determines a binding ratio in all fragmented cases;
- remove the instruction to apply whichever candidate is most similar to the later case;
- use `pending` when a shared majority ground cannot be established;
- state that `necessary/contingent/pending` are annotation statuses for the formalization, not synonyms for ratio/obiter, res judicata or preclusion;
- replace automatic propagation consequences with source-bounded CPC rules.

## 6. Search limits

This audit did not exhaust monographs, non-digitized Brazilian commentary, all plurality-opinion scholarship, or all AI-and-law argumentation literature. No exact pre-cutoff source was located in the bounded searches that uses Paper 1C's exact label `quadro de rationes candidatas` together with the same three metadata fields. That negative result does not establish firstness. The component problem and most of the machinery are clearly anteceded.