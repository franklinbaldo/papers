---
type: "Audit Report"
title: "Alignment by Affordance Restriction prior-art audit — 2026-09-17"
description: "Claim-specific, temporally grounded audit of the four-property affordance-restriction pattern, including pre-cutoff authorization/shielding antecedents and post-cutoff convergences in consent integrity and runtime authority control."
tags: [affordance-restriction, prior-art, agent-security, least-privilege, authorization, human-in-the-loop, content-addressing, action-space, agent-governance]
timestamp: 2026-09-17T21:01:47-04:00
---

# Alignment by Affordance Restriction prior-art audit — 2026-09-17

> **Status:** first claim-specific reproducible prior-art audit of the paper's four-property pattern. The audit narrows several component-level novelty claims and records later convergences separately. It does **not** establish exhaustive novelty, patent novelty, independent invention, copying, or causal dependence between projects.

## 1. Audited claim and claim-specific cutoff

The current paper, [`affordance_restriction.md`](../../affordance_restriction.md), presents **alignment by affordance restriction** as the conjunction of four structural properties:

1. **affordance enumeration** — an agent may act only by selecting and binding entries from a finite, human-curated catalog of parameterized scenarios; actions outside the catalog cannot reach the world;
2. **doctrine/procedure separation** — the catalog distinguishes value/doctrinal commitments from instrumental/procedural specializations and assigns materially higher review cost to doctrinal expansion;
3. **structured ex-ante commitment** — before acting, the agent emits a structured proposal carrying the selected catalog entry, bindings, descent/path and intended executable action; the approved artifact is also the executor input and durable audit record;
4. **content-addressed canon** — behavioral entries are identified by normalized-content hash, references bind to those hashes, changed content becomes a new identity, and prior approvals remain pinned to the original content.

The paper's strongest candidate originality claim is therefore **not** that finite action schemas, least privilege, human approval, cryptographic hashing, Merkle structures, or version-controlled policies were invented here. It is the use of those pieces as one LLM-agent alignment pattern in which a human-readable, content-addressed scenario canon is simultaneously the allowed action vocabulary, the review surface, and the durable referent for execution.

### 1.1 GitHub reconstruction

The earliest GitHub commit located with the core four-property formulation already present is:

- [`a27909ecf381bfbb6d1ca8d30bce7081a1e4d0be`](https://github.com/franklinbaldo/papers/commit/a27909ecf381bfbb6d1ca8d30bce7081a1e4d0be), **2026-05-14 20:36:24 UTC**, message `Add affordance restriction alignment paper draft`.

The commit adds `paper_affordance_restriction.md`; its initial patch already states the four properties in the abstract and describes the finite catalog, parameter binding, human-reviewed monotonic growth, content-derived identity, and structurally bound proposal/execution design.

The corresponding public pull request:

- [`#16`](https://github.com/franklinbaldo/papers/pull/16), **created 2026-05-14 20:36:40 UTC**, merged **2026-05-14 20:54:27 UTC**.

Because GitHub exposes the public commit URL and timestamp, the earliest directly verifiable repository timestamp is 20:36:24 UTC. To avoid overclaiming the exact instant at which a branch commit became discoverable to third parties, this audit uses the PR creation time as the conservative public cutoff.

**Conservative cutoff for the four-property conjunction: 2026-05-14 20:36:40 UTC.**

A public companion blog post, [“The Agent That Doesn't Invent Verbs”](https://franklinbaldo.github.io/blog/the-agent-that-doesnt-invent-verbs/), is dated **2026-05-14** and independently exposes the core catalog-as-vocabulary idea, but its page does not provide a more precise time than GitHub and is therefore corroborating evidence rather than the cutoff source.

## 2. Claim decomposition

For temporal classification, the audit separates five subclaims rather than treating similarity to the paper title as sufficient:

- **C1 — external action-boundary enforcement:** safety comes from preventing unapproved actions from reaching the world, independently of model weights or prompt obedience;
- **C2 — curated parameterized action vocabulary:** the agent chooses/binds from a finite human-readable catalog rather than inventing action types;
- **C3 — approval-bound execution:** a structured pre-execution artifact is reviewed and its approved content is cryptographically or structurally bound to what can execute;
- **C4 — content-addressed behavioral canon:** authority refers to immutable content identity, so behavioral changes do not silently inherit old approvals;
- **C5 — four-property conjunction:** C1–C4 plus an explicit doctrine/procedure split with asymmetric governance cost, all applied as one bounded-agent architecture.

This decomposition matters because C1, much of C3, and much of C4 have strong antecedents. The novelty question that survives is narrower than the paper's original contrast with training and filtering.

## 3. Search protocol

Searches were run over GitHub history and PR metadata, arXiv, AAAI proceedings, MIT/Stanford research pages, SLSA/in-toto documentation, older planning literature, and targeted web/full-text queries. Primary sources were preferred for dates and technical claims.

Representative queries:

- `LLM agent least privilege deterministic tool call policy`
- `LLM agent authorization auditable delegation permission scope`
- `LLM agent human review draft write execution binding`
- `agent action space external enforcement shield temporal logic`
- `agent skills graph fine grained action nodes privilege`
- `AI agent capability manifest hash audit ledger`
- `What You See Is What You Sign approval exact transaction execution`
- `structured action proposal human approval exact action execution LLM agent`
- `finite action schema preconditions effects planner STRIPS`
- `content-addressed policy authorization immutable audit`
- `policy as code version controlled authorization enforcement`
- `doctrine procedure hierarchy agent policy value instrumental`
- exact-title and author searches for `Alignment by Affordance Restriction`, `Franklin Baldo`, `PINK`, and later candidate papers.

Negative searches are recorded as scoped search results, not proof of absence.

## 4. Findings before our cutoff

### 4.1 STRIPS already provides finite parameterized action schemas with preconditions and effects

**Work:** Richard E. Fikes & Nils J. Nilsson, **“STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving.”**

- First public technical-report lineage located: SRI/DTIC report, **1970-10-01**.
- Journal publication: *Artificial Intelligence* 2(3–4), **1971**, DOI [`10.1016/0004-3702(71)90010-5`](https://doi.org/10.1016/0004-3702(71)90010-5).
- DTIC record: <https://dtic.minsky.ai/index/ADA459687>

**Compared claim:** C2.

**Classification:** `partial_prior_art`.

STRIPS predates the paper by more than five decades in representing a problem domain through a set of operators/actions whose applicability depends on represented world state and whose execution transforms that state. The broader planning tradition therefore already supplies the core idea of a **bounded action vocabulary made of parameterized schemas with preconditions and effects**.

**Difference:** STRIPS is a planning formalism, not an alignment/governance architecture. It does not require human review of catalog expansion, content-address entries, distinguish doctrine from procedure, or bind human approval to the exact executed proposal. Thus it anticipates an important substrate of C2 but not the paper's governance conjunction.

### 4.2 Runtime shielding already established model-external enforcement of allowable actions

**Work:** Mohammed Alshiekh et al., **“Safe Reinforcement Learning via Shielding.”**

- AAAI 2018, publisher publication date **2018-04-29**.
- DOI: <https://doi.org/10.1609/aaai.v32i1.11797>
- Publisher: <https://ojs.aaai.org/index.php/AAAI/article/view/11797>

**Compared claim:** C1.

**Classification:** `prior_art` for the generic component “safety by externally enforcing an allowable action boundary”; `partial_prior_art` for affordance restriction as a whole.

The shield is synthesized from a temporal-logic safety specification, monitors learner actions, and corrects actions that would violate the specification. This directly predates the proposition that reliable safety can be imposed **outside the learned policy**, at execution time, rather than solely through training or after-the-fact textual filtering.

**Difference:** shielding generally derives safe choices from state and a safety property. It is not a human-readable catalog of institutional scenarios, and it does not supply C3–C5.

### 4.3 Authenticated Delegation already formalized human-scoped, auditable authority for AI agents

**Work:** Tobin South et al., **“Authenticated Delegation and Authorized AI Agents.”**

- arXiv v1: **2025-01-16 17:11:21 UTC**.
- <https://arxiv.org/abs/2501.09674>
- Stanford Digital Economy Lab record dated **2025-01-16**: <https://digitaleconomy.stanford.edu/publication/authenticated-delegation-and-authorized-ai-agents/>

**Compared claims:** C1, auditability aspect of C3.

**Classification:** `partial_prior_art`.

The framework explicitly lets users delegate and **restrict permissions and scope** of AI agents while maintaining auditable chains of accountability, and proposes translating flexible natural-language permissions into auditable access-control configurations. It therefore predates any broad claim that explicit, human-defined authority scopes plus auditability are distinctive to affordance restriction.

**Difference:** it is an identity/delegation/access-control framework, not a scenario canon. It does not make one human-readable scenario artifact simultaneously the planner vocabulary, approval object, executor input and content-addressed behavioral identity.

### 4.4 Progent is direct prior art for deterministic privilege control at the agent/tool boundary

**Work:** Tianneng Shi et al., **“Progent: Programmable Privilege Control for LLM Agents.”**

- arXiv v1: **2025-04-16 01:58:40 UTC**.
- <https://arxiv.org/abs/2504.11703>

**Compared claim:** C1, part of C2.

**Classification:** `prior_art` for deterministic, model-external action restriction in tool-using LLM agents; `partial_prior_art` for C2 and the full paper.

Progent explicitly motivates least privilege as **allowing only essential actions while blocking unnecessary ones**, supplies a DSL for fine-grained tool-call policies, decides when calls are permissible, and enforces the policies deterministically during execution without altering agent internals. This is materially closer than generic safe-RL shielding and substantially narrows the paper's initial “distinct from training and filtering” framing.

The generic component “change what the model is allowed to do by deterministic execution-layer policy” was therefore already public more than a year before our cutoff.

**Difference:** Progent policies constrain calls; they are not a finite, content-addressed, lawyer-readable scenario vocabulary that the agent must instantiate. Its automated policy-writing path is also conceptually different from a canon whose expansion requires human review.

### 4.5 OpenPort predates draft-first governed writes, human review, preflight binding and deterministic audit

**Work:** Genliang Zhu et al., **“OpenPort Protocol: A Security Governance Specification for AI Agent Tool Access.”**

- arXiv v1: **2026-02-22 05:16:40 UTC**.
- <https://arxiv.org/abs/2602.20196>

**Compared claims:** C1 and C3; adjacent to C4.

**Classification:** strong `partial_prior_art`; `prior_art` for generic draft-first/human-reviewed governed writes and pre-execution binding controls.

OpenPort defines authorization-dependent tool discovery, scoped permissions and policy constraints. Crucially for C3, write operations default to **draft creation and human review**; higher-risk flows include a preflight impact hash binding the tool, payload and impact summary, and an optional state witness revalidates execution-time preconditions to prevent approval/execution drift. It also requires structured audit events.

This means neither “agent writes should become reviewable drafts before execution” nor the generic objective “bind reviewed intent/action data to what later executes” can be treated as original components of our pattern.

**Difference:** OpenPort governs tools and write requests through a gateway. It does not appear to use a content-addressed scenario canon as the agent's complete behavioral vocabulary; nor does it provide our doctrine/procedure tier split.

### 4.6 Governing Dynamic Capabilities already binds agent authority to cryptographic capability identity

**Work:** Ziling Zhou, **“Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use.”**

- arXiv v1: **2026-03-15 11:46:57 UTC**.
- <https://arxiv.org/abs/2603.14332>

**Compared claim:** C4.

**Classification:** strong `partial_prior_art`.

The paper identifies a capability-identity gap and proposes capability-bound agent certificates containing a **skills-manifest hash**, such that a tool change invalidates the certificate, plus a signed hash-linked interaction ledger. This is direct pre-cutoff evidence that cryptographically binding agent authority to a digest of its capability surface, and invalidating authority after capability change, was already an explicit agent-governance technique.

**Difference:** the hash binds a capability/skills manifest rather than giving each human-readable behavioral scenario a permanent content-derived identity within a Merkle-style canon. The antecedent is therefore highly relevant to C4 but does not reproduce the same data model.

### 4.7 SkillScope predates graph-structured fine-grained action constraints for agent Skills

**Work:** Jiangrong Wu et al., **“SkillScope: Toward Fine-Grained Least-Privilege Enforcement for Agent Skills.”**

- arXiv v1: **2026-05-07 08:34:14 UTC**, seven days before our cutoff.
- <https://arxiv.org/abs/2605.05868>

**Compared claims:** C1/C2, graph aspect of C4.

**Classification:** `partial_prior_art`.

SkillScope models instruction-level procedures and code-level operations as **fine-grained action nodes**, analyzes them as a graph, and constrains over-privileged actions through control-flow privilege constraining. This is a particularly close temporal antecedent to graph-structured, externally constrained agent capabilities.

**Difference:** the graph is recovered/analyzed from Skills for least-privilege enforcement; it is not a deliberately curated institutional canon whose graph itself defines the only legal actions and whose node identity is content-addressed.

### 4.8 WYSIWYS is much older prior art for the generic approval/execution integrity property

**Work/family:** **What You See Is What You Sign (WYSIWYS)** in digital-signature and transaction-authorization systems.

- Landrock & Pedersen, **“WYSIWYS? — What You See Is What You Sign?”**, *Information Security Technical Report* 3(2), **1998**.
- Longstanding transaction-signing systems show the human a human-readable operation before the cryptographic approval is produced.
- A current explanatory record: <https://www.ledger.com/academy/topics/ledgersolutions/what-is-clear-signing>

**Compared claim:** the generic core of C3.

**Classification:** `prior_art` for the generic integrity goal “the operation reviewed/approved by a human must be the operation cryptographically authorized”; `adjacent_prior_work` for the LLM-agent architecture.

The paper's particular artifact shape remains distinctive, but approval-to-execution identity is not new as a security property. The right novelty question is how that property is embedded into an LLM agent's scenario-selection workflow, not whether the property itself exists.

### 4.9 in-toto/SLSA and immutable provenance precede content-addressed approval referents

**Work/family:** in-toto and SLSA provenance.

- in-toto publication: Torres-Arias et al., USENIX Security 2019 (already cited in the manuscript).
- SLSA v1.0 provenance/distribution specifications require artifact digests and recommend immutable attestations: <https://slsa.dev/spec/v1.0/distributing-provenance>.

**Compared claim:** C4.

**Classification:** `adjacent_prior_work`, rising to `partial_prior_art` for the generic “immutable digest-bound artifact + auditable provenance” component.

These systems make exact artifact identity and provenance verifiable with cryptographic digests and immutable attestations. Our behavioral-canon use is a different artifact class, but the security mechanism itself is established.

## 5. What remains after the pre-cutoff search

The audit materially narrows the paper's novelty boundary.

The following should **not** be presented as independently novel:

- model-external enforcement of safe/allowed actions (shielding, Progent);
- least-privilege tool authorization for LLM agents (Progent; Authenticated Delegation; OpenPort);
- graph-structured action/capability analysis (SkillScope);
- draft-first/human-reviewed agent writes and approval/execution drift controls (OpenPort);
- approval integrity as “what the user approved is what is authorized/executed” (WYSIWYS family);
- cryptographic digest binding of agent capability identity (Governing Dynamic Capabilities);
- immutable digest-bound provenance artifacts (in-toto/SLSA);
- parameterized action schemas as a planning substrate (STRIPS and descendants).

### 5.1 Narrow combination not located before cutoff

After the searches above, **no pre-cutoff source was located that materially anticipates the full conjunction**:

> a finite, human-curated, human-readable set of parameterized scenarios is the LLM agent's complete action vocabulary; the catalog is split into doctrine/value versus procedure/instrument with asymmetric human governance; every consequential action is first materialized as a structured proposal pinned to immutable content identity; the human-approved proposal is also the executor input and durable audit record; and behavioral edits create new content identities rather than silently inheriting prior authority.

That is a **negative search result under this protocol**, not a claim that no such antecedent exists.

The least-supported individual element is currently the **doctrine/procedure semantic split with intentionally asymmetric review cost inside the same bounded action canon**. Searches over policy hierarchy, value/instrument distinction, policy-as-code, access control and agent governance did not locate a pre-cutoff agent architecture with this exact division. However, the distinction has obvious conceptual ancestry in legal/public-administration practice and policy hierarchies, so absence from this technical search should not be converted into an “invented here” statement.

### 5.2 Revised novelty statement

A defensible current formulation is:

> Prior work already provides deterministic action shielding, least-privilege agent authorization, parameterized action schemas, human-gated write workflows, approval-to-execution integrity, and cryptographic capability/provenance binding. The candidate contribution of affordance restriction is the **specific composition** in which a human-readable, content-addressed scenario canon is both the complete action vocabulary and the durable approval/execution substrate, with a governance-significant doctrine/procedure stratification. No material antecedent to that full conjunction was located in this audit.

## 6. Work published after our cutoff

Later work cannot be prior art against a claim public by 2026-05-14. It is recorded separately for convergence and overlap.

### 6.1 AIRGuard — close post-cutoff convergence on execution-layer authority

**Work:** Suliu Qin et al., **“AIRGuard: Guarding Agent Actions with Runtime Authority Control.”**

- arXiv v1: **2026-05-27 17:48:14 UTC**, thirteen days after our cutoff.
- <https://arxiv.org/abs/2605.28914>

**Classification:** `later_overlap`.

AIRGuard argues that prompt-only policy is weaker than a dedicated runtime authority layer and enforces action-time authorization before side effects. This strongly converges with C1 but uses task-derived step authority, trust tracking and side-effect simulation rather than a finite human-curated canon.

Because the publication is post-cutoff, it cannot be prior art against our C1 formulation. The evidence reviewed here is insufficient to establish causal independence or dependence; therefore `later_overlap` is more appropriate than a causal label.

### 6.2 “What You Approve Is What Executes” — later non-citing overlap with structured ex-ante commitment

**Work:** Xiaoqi Weng, **“What You Approve Is What Executes: Consent Integrity for Black-Box LLM Agents.”**

- arXiv v1: **2026-06-01 11:08:17 UTC**.
- <https://arxiv.org/abs/2606.02668>

**Classification:** `later_non_citing` for the C3 approval/execution-integrity subclaim; not a claim of derivation.

This work explicitly names **Consent Integrity**: the action displayed to the human must be rendered by a trusted mediator from the real boundary action and bound to the exact action that executes. It imports WYSIWYS and trusted-path reasoning into black-box LLM-agent approvals and implements an analyzer/renderer/bind-to-execution prototype.

The overlap with our C3 is material: both require the human review object to be structurally tied to the action that can actually execute, rather than trusting an agent-authored narrative after the fact. The systems differ substantially: Weng starts from the low-level boundary action and derives a trusted display, while affordance restriction starts from a curated scenario identity and structured proposal that constrains execution.

Targeted searches of the searchable arXiv/web records for `Baldo`, `Alignment by Affordance Restriction`, `affordance`, and `PINK` did **not locate a citation to our work**. This justifies the factual `later_non_citing` label under the repository taxonomy. It does **not** imply copying, awareness, derivation, plagiarism, or bad faith.

### 6.3 EBTE — later non-citing convergence on claim-carrying action mediation

**Work:** Genliang Zhu & Chu Wang, **“Explanation-Bound Tool Execution for AI Agents: Server-Verified Action Claims Without Trusting Model Rationales.”**

- arXiv v1: **2026-07-28 07:16:12 UTC**.
- <https://arxiv.org/abs/2607.25364>

**Classification:** `later_non_citing` for the structured claim-before-execution overlap; dependency unknown.

EBTE converts decision-relevant rationale content into typed action claims and checks them against server-held intent, policy, payload, tool, risk, provenance and freshness facts before the action remains eligible for governed execution. Conflicts deny and incomplete/uncertain cases go to review. It also uses a versioned reference profile and minimized audit packets.

That is a material later convergence on C3's core idea that a consequential agent action should be represented as structured, externally checkable content **before execution** and should not rely on trusting the model's prose rationale. It is not the same architecture: EBTE verifies claims about tool calls rather than selecting from a content-addressed scenario canon.

Exact-title/author searches performed in this audit did not locate a citation to `Alignment by Affordance Restriction` or Franklin Baldo in the accessible records. Again, the `later_non_citing` category records only the located absence of citation plus temporal/material overlap.

### 6.4 ClosureBound — later independent convergence on version-bound capability identity

**Work:** Genliang Zhu & Chu Wang, **“Versioned Transitive Dependency-Closure Binding and Operation-Time Effect Governance for Agent Skills: ClosureBound.”**

- arXiv record located with submission **2026-09-10**.
- <https://arxiv.org/abs/2609.05920>

**Classification:** `later_independent` / `later_overlap` with C4 at the mechanism level; no causal claim.

ClosureBound prevents authorization from transferring across material changes to an Agent Skill's heterogeneous dependency closure. Grants bind an exact closure root, effect ceiling, purpose/provenance, validity and epochs; at operation time the closure is re-resolved before durable effects are admitted. This is a much more developed later treatment of “authority must not silently survive capability identity changes.”

Its object is transitive Skill dependency closure, not a curated legal scenario canon. It therefore strengthens the surrounding literature without erasing our earlier claim-specific cutoff.

## 7. Classification summary

| Candidate | Earliest verified public date used | Compared claim | Classification | Why |
|---|---:|---|---|---|
| STRIPS | 1970 report / 1971 journal | C2 | `partial_prior_art` | finite parameterized action/operator schemas, not agent governance |
| Safe RL via Shielding | 2018-04-29 | C1 | `prior_art` component | externally enforced allowed/safe action boundary |
| Authenticated Delegation | 2025-01-16 | C1/C3-audit | `partial_prior_art` | human-scoped agent authority + auditable delegation |
| Progent | 2025-04-16 | C1/C2 | `prior_art` for deterministic agent privilege control; `partial_prior_art` full pattern | deterministic tool-call authorization outside agent internals |
| OpenPort | 2026-02-22 | C1/C3 | strong `partial_prior_art`; component `prior_art` | draft-first writes, human review, preflight binding, audit |
| Governing Dynamic Capabilities | 2026-03-15 | C4 | strong `partial_prior_art` | manifest hash binds capability identity; hash-linked ledger |
| SkillScope | 2026-05-07 | C1/C2/C4-graph | `partial_prior_art` | graph action nodes + fine-grained privilege constraining |
| WYSIWYS family | 1998 and earlier signature lineage | C3 | `prior_art` generic property | human approval must bind to exact authorized operation |
| in-toto/SLSA | 2019 / 2023 | C4 | `adjacent_prior_work` / component `partial_prior_art` | immutable digest-bound artifacts and provenance |
| AIRGuard | 2026-05-27 | C1 | `later_overlap` | runtime authority before effects, post-cutoff |
| What You Approve Is What Executes | 2026-06-01 | C3 | `later_non_citing` | exact approve/execute binding for LLM agents; no citation located |
| EBTE | 2026-07-28 | C3 | `later_non_citing` | typed pre-execution action claims; no citation located |
| ClosureBound | 2026-09-10 | C4 | `later_independent` / `later_overlap` | exact version/dependency-closure binding of agent authority |

## 8. Epistemic revision relative to the manuscript

The manuscript is already unusually cautious in saying the pattern is “old in spirit” and citing expert systems, BDD, Merkle trees, in-toto and SLSA. The material revision from this audit is more specific:

1. **C1 is not merely old in spirit.** Deterministic, external action restriction for learning/LLM agents has direct technical antecedents in shielding and Progent.
2. **C3 has direct pre-cutoff LLM-agent antecedents.** OpenPort already combines draft-first writes, human review and preflight binding; WYSIWYS supplies the older generic integrity property.
3. **C4 has an especially close pre-cutoff agent-governance antecedent.** Governing Dynamic Capabilities uses a skills-manifest hash so capability changes invalidate authorization.
4. **A near-cutoff antecedent exists for graph-structured constrained actions.** SkillScope appeared seven days before the conservative cutoff.
5. The **full four-property conjunction remains unresolved**, not established as first. The remaining research contribution should be expressed compositionally and tested against these stronger baselines rather than against training/filtering alone.

## 9. Recommended scientific consequences

The paper's future evaluation should compare the PINK pattern against controls that isolate the claimed composition:

- **policy-only runtime gate** (Progent-like): same tools and model, deterministic allow/deny rules, no scenario canon;
- **draft/review gateway** (OpenPort-like): structured write draft + approval + preflight binding, but no content-addressed scenario vocabulary;
- **manifest-hash capability binding** (Zhou-like): capability identity pinned by digest, but no doctrine/procedure canon;
- **scenario canon without content addressing**: tests whether immutable identity contributes beyond Git/version history;
- **scenario canon without doctrine/procedure asymmetry**: tests the governance value of the semantic tier split;
- **full affordance restriction**: all four properties.

Useful outcome metrics are not only task success: unauthorized side-effect rate, approval/execution drift, reviewer time, silent behavioral-change inheritance, replay/audit reconstruction success, and catalog-maintenance cost are closer to the paper's actual safety claims.

## 10. Search limits and negative evidence

This audit did not establish exhaustive coverage of patents, non-English proceedings, private industrial deployments, or unpublished internal systems. Google Scholar access was not treated as a completeness oracle. Search terminology in this area is unstable (`guardrails`, `authorization`, `capabilities`, `tool governance`, `policy as code`, `least privilege`, `approval binding`, `consent integrity`, `action schemas`, `shields`), so future runs should revisit the claim when new vocabulary or citation chains emerge.

In particular:

- no pre-cutoff paper was located that combines **all four** properties with the same artifact semantics;
- no pre-cutoff agent paper was located with the same explicit **doctrine-versus-procedure review-cost asymmetry**;
- no evidence of causal dependence was located for any later work;
- the absence of located citations in the two `later_non_citing` cases is a bounded factual observation from the searches above, not evidence of misconduct.

## 11. Primary references

- Fikes, R. E.; Nilsson, N. J. “STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving.” *Artificial Intelligence* 2(3–4), 1971. <https://doi.org/10.1016/0004-3702(71)90010-5>
- Alshiekh, M. et al. “Safe Reinforcement Learning via Shielding.” AAAI 2018. <https://doi.org/10.1609/aaai.v32i1.11797>
- South, T. et al. “Authenticated Delegation and Authorized AI Agents.” arXiv:2501.09674, 2025. <https://arxiv.org/abs/2501.09674>
- Shi, T. et al. “Progent: Programmable Privilege Control for LLM Agents.” arXiv:2504.11703, 2025. <https://arxiv.org/abs/2504.11703>
- Zhu, G. et al. “OpenPort Protocol: A Security Governance Specification for AI Agent Tool Access.” arXiv:2602.20196, 2026. <https://arxiv.org/abs/2602.20196>
- Zhou, Z. “Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use.” arXiv:2603.14332, 2026. <https://arxiv.org/abs/2603.14332>
- Wu, J. et al. “SkillScope: Toward Fine-Grained Least-Privilege Enforcement for Agent Skills.” arXiv:2605.05868, 2026. <https://arxiv.org/abs/2605.05868>
- Qin, S. et al. “AIRGuard: Guarding Agent Actions with Runtime Authority Control.” arXiv:2605.28914, 2026. <https://arxiv.org/abs/2605.28914>
- Weng, X. “What You Approve Is What Executes: Consent Integrity for Black-Box LLM Agents.” arXiv:2606.02668, 2026. <https://arxiv.org/abs/2606.02668>
- Zhu, G.; Wang, C. “Explanation-Bound Tool Execution for AI Agents: Server-Verified Action Claims Without Trusting Model Rationales.” arXiv:2607.25364, 2026. <https://arxiv.org/abs/2607.25364>
- Zhu, G.; Wang, C. “Versioned Transitive Dependency-Closure Binding and Operation-Time Effect Governance for Agent Skills: ClosureBound.” arXiv:2609.05920, 2026. <https://arxiv.org/abs/2609.05920>
- SLSA v1.0, “Distributing provenance.” <https://slsa.dev/spec/v1.0/distributing-provenance>
