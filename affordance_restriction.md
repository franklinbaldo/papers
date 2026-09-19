---
type: "Alignment Paper"
title: "Alignment by Affordance Restriction: A Pattern for Auditable Bounded Agents"
description: "A position paper on a bounded-agent architecture that composes a human-readable content-addressed action canon, approval/execution integrity, and doctrine/procedure governance asymmetry."
tags: [affordance-restriction, bounded-agents, agent-governance, auditability]
timestamp: 2026-06-13T06:05:18-04:00
authors:
  - ref: /authors/franklin-silveira-baldo.md
    byline: "Franklin Silveira Baldo"
    affiliations:
      - "Independent Researcher"
    corresponding: true
publication:
  status: ready
  targets: [zenodo]
  zenodo:
    publication_type: preprint
    access_right: open
    license: cc-by-nc-4.0
    version: "0.1"
---

# Alignment by Affordance Restriction: A Pattern for Auditable Bounded Agents

**Franklin Silveira Baldo**  
*Procuradoria-Geral do Estado de Rondônia / Universidade Federal de Rondônia*  
*franklin@pge.ro.gov.br*

*Target venue: SafeAI @ AAAI 2027 (workshop, ~8 pages + references).*

> **Position/methodology paper — frozen v0.1.** This version reports a design pattern and a worked historical design/implementation snapshot, not a completed deployment evaluation. A claim-specific prior-art audit is maintained at [`audits/prior-art/affordance-restriction-2026-09-17.md`](audits/prior-art/affordance-restriction-2026-09-17.md). The audit found direct antecedents for deterministic action shielding, least-privilege agent authorization, parameterized action schemas, draft-first/human-reviewed execution, approval-to-execution integrity, and cryptographic capability/provenance binding. Accordingly, this paper does **not** claim those components individually. Its candidate contribution is the narrower composition described below. The PINK provenance used for the worked example is pinned in Section 4.6; this version makes no claim that the historical playbook architecture is the current production interface of PINK.

---

## Abstract

We describe *alignment by affordance restriction*: an architecture for bounded agents in which the executable action space is a curated, human-readable, content-addressed catalog of parameterized scenarios. Prior work already establishes model-external action shielding, least-privilege authorization for LLM agents, parameterized action schemas, human-gated write workflows, approval/execution integrity, and digest-bound capability/provenance mechanisms. Our candidate contribution is therefore not any of those components in isolation. It is their specific composition: a scenario canon that simultaneously acts as the agent's complete action vocabulary and durable approval/execution substrate, while separating doctrine/value commitments from procedure/instrumental specializations with intentionally asymmetric governance cost.

The pattern has four structural properties — affordance enumeration, doctrine/procedure separation, structured ex-ante commitment, and content-addressed canon. We identify three semantic conditions that determine whether the pattern is applicable to a target domain: whether there exists a discrete unit of action, whether there is a record where reflection can persist, and whether durable audit is desirable for the operator. We use a historical PINK playbook design as a worked example, characterize four failure modes, and propose a validation programme against stronger controls derived from the prior-art audit. No pilot-performance or safety-superiority result is reported.

## 1. Introduction

Many alignment techniques act on the model or its outputs: reinforcement learning from human feedback changes a policy using preference-derived reward [Christiano et al. 2017; Ouyang et al. 2022], constitutional approaches train against principle-stated critiques [Bai et al. 2022], and output filters intervene after generation. A different family acts at the execution boundary. Safe-RL shielding, deterministic LLM-agent privilege controls, scoped delegation frameworks, and governed tool gateways already demonstrate that a learned policy can be constrained by machinery outside the model [Alshiekh et al. 2018; South et al. 2025; Shi et al. 2025; Zhu et al. 2026].

This paper studies one narrower composition of that execution-boundary idea. We call it *alignment by affordance restriction*. An agent's executable action space is the projection of a curated, content-addressed catalog of parameterized scenarios written for both domain experts and software. The agent selects and binds entries; the system boundary rejects actions that cannot be represented by an authorized catalog entry. Consequential actions are materialized as structured artifacts before execution, and the same approved artifact constrains what can later execute. The catalog distinguishes doctrine/value-level entries from procedural specializations and deliberately makes doctrine expansion more expensive to approve.

None of the ingredients is treated as an isolated invention. STRIPS and descendants long predate the paper in parameterized action schemas [Fikes and Nilsson 1971]. Runtime shielding predates it in external enforcement of allowable actions [Alshiekh et al. 2018]. Authenticated Delegation, Progent, OpenPort, and SkillScope predate it in scoped or graph-structured agent authorization [South et al. 2025; Shi et al. 2025; Zhu et al. 2026; Wu et al. 2026]. The WYSIWYS security lineage predates it in the integrity goal that the operation a human approves should be the operation authorized [Landrock and Pedersen 1998]. in-toto/SLSA and capability-manifest work predate it in digest-bound provenance and capability identity [Torres-Arias et al. 2019; SLSA 2023; Zhou 2026].

The claim left after that literature is deliberately compositional. Under the search protocol documented in the repository audit, no pre-cutoff source was located that materially anticipated the full conjunction of: (i) a finite human-readable scenario canon as the complete action vocabulary; (ii) doctrine/procedure stratification with asymmetric governance cost; (iii) structured ex-ante commitment pinned to immutable content identity; (iv) the approved proposal serving as executor input and durable audit record; and (v) behavior changes receiving new content identity rather than silently inheriting old authority. That is a bounded negative search result, not an exhaustive firstness claim.

This paper therefore makes three narrower contributions:

1. It specifies the four-property conjunction as a reusable bounded-agent architecture and makes explicit how the properties depend on one another.
2. It proposes three semantic applicability questions — discrete action, persistent record, and desirability of audit — as a domain-selection test for this composition.
3. It develops a PINK playbook design snapshot as a worked example and derives failure modes and discriminating evaluation controls that compare the full composition with simpler authorization and approval architectures.

The paper proceeds as follows. Section 2 maps the closest antecedents. Section 3 specifies the four-property pattern. Section 4 records the PINK worked design and its provenance boundary. Section 5 gives the applicability test. Sections 6 and 7 state non-claims and failure modes. Section 8 freezes a prospective validation roadmap. Section 9 closes.

## 2. Background and Prior-Art Boundary

**Alignment via model modification.** Reinforcement learning from human feedback fits a reward model from preference comparisons and trains a policy to maximize predicted reward [Christiano et al. 2017; Ouyang et al. 2022]. Constitutional AI replaces direct human preference labels with model-generated critiques against a written constitution [Bai et al. 2022]. Affordance restriction operates at a different layer and can compose with either: the model may still be preference-trained while the external system separately limits which actions can have effects.

**Parameterized action vocabularies.** STRIPS represents domains through operators with parameters, applicability conditions, and effects [Fikes and Nilsson 1971]. The general idea that an agent or planner acts through a finite vocabulary of parameterized schemas is therefore established. The contribution claimed here is not schema enumeration itself, but the way schema identity is tied to governance, approval, and durable authorization.

**Execution-layer shielding and least privilege.** Safe Reinforcement Learning via Shielding established model-external enforcement of allowable behavior using a synthesized shield [Alshiekh et al. 2018]. Authenticated Delegation formalizes human-scoped, auditable authority for AI agents [South et al. 2025]. Progent provides deterministic, programmable privilege control for LLM-agent tool calls without changing agent internals [Shi et al. 2025]. SkillScope models fine-grained agent-skill actions and constrains over-privileged behavior using graph structure [Wu et al. 2026]. These are direct antecedents to the generic claim that safety can be improved by constraining what reaches the world rather than relying only on model obedience.

**Human-gated writes and approval/execution integrity.** OpenPort supplies authorization-dependent tool access, draft-first governed writes, human review, preflight binding, and structured audit events [Zhu et al. 2026]. Much older WYSIWYS work establishes the security requirement that the operation represented to a signer should be the operation actually authorized [Landrock and Pedersen 1998]. The present paper therefore does not claim that review-before-write or approval/execution identity is new. Its narrower architectural move is to make the reviewed object an instantiation of the same immutable scenario canon that defines the allowed action vocabulary.

**Content-addressed identity and provenance.** Merkle trees provide the cryptographic basis for content-derived identity [Merkle 1987]. in-toto and SLSA use digests and immutable attestations for software-supply-chain provenance [Torres-Arias et al. 2019; SLSA 2023]. Governing Dynamic Capabilities binds AI-agent authorization to a skills-manifest hash so that capability changes invalidate prior authority [Zhou 2026]. These works occupy the generic mechanism of digest-bound provenance/capability identity. The question here is what changes when that mechanism is applied to human-readable behavioral scenarios that are also the approval and execution referents.

**Scalable oversight.** The bandwidth question — how a human supervises a system fast enough to keep up — is shared with scalable-oversight work [Christiano, Shlegeris, and Amodei 2018; Bowman et al. 2022; Irving, Christiano, and Amodei 2018]. Affordance restriction does not solve scalable oversight generally. In bounded domains it attempts to lower review entropy by forcing consequential actions into a finite, structured vocabulary. Whether this actually reduces reviewer burden without introducing unacceptable catalog-maintenance costs is an empirical question for Section 8.

**Corrigibility and human-in-the-loop control.** Hadfield-Menell et al. [2017] formalize corrigibility as a game-theoretic property under which an agent defers to human control. Russell [2019] argues for value uncertainty as a foundation for safe agency. The present pattern is silent on value learning; it instead makes a narrower engineering choice in which value-like/doctrinal commitments and instrumental procedures are separated in the external action canon and governed with different review costs.

**Plans as accountability.** Suchman's distinction between *plans-as-cognition* and *plans-as-accountability* [Suchman 1987] is useful here. The proposal artifact is not claimed to reveal the model's internal decision process. It is the structured commitment by which the action is reviewed and later judged. Mechanistic interpretability and ex-ante commitment therefore answer different questions.

**Behavior-driven development.** Gherkin originates in behavior-driven development [North 2006; Wynne and Hellesøy 2012]. We reuse its human-readable scenario grammar as one possible syntax for an action canon. The syntax is not the contribution; another parseable domain language could instantiate the same architecture.

**Legal expert systems.** Legal AI has a long lineage in case-based and rule-based reasoning, including HYPO-related work, TAXMAN, and later hybrid approaches [Rissland and Ashley 1987; Ashley 1990; McCarty 1977; Branting 2000]. The present architecture does not claim to replace legal reasoning with a formal expert system. The worked example instead uses a curated external canon to delimit which procedural effects an LLM-driven agent may cause.

**The alignment-as-values literature.** Gabriel [2020] argues that alignment involves value identification rather than only capability constraint. This paper does not solve value identification. Doctrine/procedure stratification assumes that humans can identify a set of higher-cost commitments whose modification deserves stronger governance.

### 2.1 Revised novelty statement

The claim-specific audit supports the following bounded formulation:

> Prior work already provides deterministic action shielding, least-privilege agent authorization, parameterized action schemas, human-gated write workflows, approval-to-execution integrity, and cryptographic capability/provenance binding. The candidate contribution of affordance restriction is the **specific composition** in which a human-readable, content-addressed scenario canon is both the complete action vocabulary and the durable approval/execution substrate, with a governance-significant doctrine/procedure stratification. No material antecedent to that full conjunction was located under the documented pre-cutoff search protocol.

This statement is a search result, not a patent-style novelty opinion and not evidence that every component was independently invented here.

## 3. The Pattern: Alignment by Affordance Restriction

We characterize alignment by affordance restriction via four structural properties. An instance of the pattern exhibits all four; absence of any indicates a related but distinct technique.

### 3.1 Property 1: Affordance Enumeration

The agent's allowed actions are the entries in a finite catalog. The catalog is human-curated; additions require human approval; the agent does not act outside it. Each entry is a parameterized scenario: a pattern of preconditions, an action sequence, and metadata identifying its role in the catalog graph. Operating on a case means selecting an entry whose preconditions describe the case and instantiating it by binding parameters to concrete values.

This property should not be confused with the claim that finite action schemas are new. The established antecedents above already provide bounded action vocabularies and execution-layer restrictions. Here, enumeration matters because the same vocabulary is also the unit of versioned authority, review, and provenance.

### 3.2 Property 2: Doctrine/Procedure Separation

The catalog stratifies. A doctrinal layer (called *Tier 1* in the worked design) declares what counts as a legitimate outcome in a class of situations; its action clauses are assertions about state rather than executable instructions. Procedural layers (*Tier 2+*) declare concrete action sequences that realize those outcomes. Procedural entries structurally reference the doctrinal entries they concretize.

Procedural addition is designed to be comparatively cheap. Doctrinal addition is intentionally more expensive: it enters a separate review path and cannot be batch-approved in the worked design. The asymmetry encodes a governance choice: changes to value-like commitments receive more friction than changes to implementation procedure. This distinction has obvious ancestry in law, public administration, and policy hierarchies; the paper claims only its role inside this particular bounded-agent composition.

### 3.3 Property 3: Structured Ex-ante Commitment

Before acting, the agent emits a proposal — a structured artifact carrying (a) the catalog entry it instantiates, identified by content identity; (b) bindings of placeholders to case values; (c) the path traversed through the catalog graph; (d) a narrative justification; and (e) the instantiated scenario in executable form. The intended invariant is that the same approved artifact is the executor input and durable audit record.

The interpretability claim is structural rather than computational. The artifact does not prove why an internal model selected the action. It records what action the system committed to, under which declared bindings and justification, before effects occur. WYSIWYS and OpenPort establish related approval-integrity goals; the distinctive role here is that the proposal is pinned to the same content-addressed behavioral vocabulary that defines authorization.

### 3.4 Property 4: Content-addressed Canon

Catalog entries are identified by normalized content identity. Edges in the catalog graph point at immutable identities rather than mutable semantic names. Changing behavior therefore creates a new identity and requires explicit reauthorization rather than silently inheriting authority from an earlier version.

Content addressing and digest-bound authority are established mechanisms [Torres-Arias et al. 2019; SLSA 2023; Zhou 2026]. Their role in this pattern is to bind Properties 1 and 3 together: an approval refers to the exact behavioral object from the finite action vocabulary.

The four properties are coupled. Property 4 strengthens Property 3 because commitment is to immutable content rather than a mutable reference. Property 2 presupposes an enumerated vocabulary. Property 3 makes that vocabulary the human review surface. The candidate contribution is this conjunction, not the isolated mechanisms.

## 4. PINK as a Worked Design Snapshot

PINK is an agent-first interface to the Kanoê/Caipora legal case system used in the State of Rondônia. The historical design explored in this paper introduced a five-stage case workflow and a Gherkin playbook canon. The worked example is useful because it supplied the concrete artifact semantics from which the four-property pattern was abstracted.

The archival boundary matters. PINK's current repository documentation at head `cb20378754cf7182f94761ae8931dac7bf94b678` describes the product as a typed FastMCP capability surface over Kanoê/Caipora and does not present the playbook framework as the current product documentation. Consequently, this paper freezes the playbook material as a **historical design/implementation snapshot**, not as a claim about PINK's present production architecture or deployment status.

### 4.1 Pipeline

The playbook design used a five-stage pipeline: *Discover* (read case data into agent context), *Fetch* (materialize referenced documents), *Propose* (descend the canon, bind parameters, write a proposal artifact), *Review* (human approve/reject/edit), and *Apply* (execute an approved scenario through the gated write subsystem).

```mermaid
graph LR
  D[Discover<br/><i>read</i>] --> F[Fetch<br/><i>read</i>]
  F --> P[Propose<br/><i>local artifact</i>]
  P --> R[Review<br/><i>human gate</i>]
  R --> A[Apply<br/><i>gated write</i>]
```

**Figure 1.** *Historical five-stage playbook design. The figure is an architectural proposal/snapshot, not evidence of current production deployment.*

### 4.2 Catalog Structure

The design represented catalog entries as Brazilian-Portuguese Gherkin `.feature` files organized by tier. Content-addressing work defined normalized content identity and filenames carrying an abbreviated UUIDv5-derived identity. `@concretiza:` edges linked higher-tier procedural specializations to lower-tier outcomes. A strict lower-tier rule made the concretization graph acyclic by construction in that design.

Leaves were the directly bindable objects. Adding a deeper specialization could retire a parent from direct binding for that branch, forcing later proposals to descend to the more specific node.

### 4.3 Traversal, Not Matching

The design deliberately moved semantic selection out of the infrastructure. The infrastructure exposed structural navigation (`tree`, `show`, `children`, `is-leaf`, `ancestors`); the LLM performed the semantic judgment about which child fit the case. The traversal path was intended to be recorded in the proposal artifact so a later reviewer could reconstruct the declared descent through the canon without claiming access to the model's internal reasoning.

### 4.4 The Proposal Artifact

A proposal was specified as a markdown artifact with YAML frontmatter (catalog reference, traversal, bindings, status, and agent-reported confidence), a narrative justification, and an embedded Gherkin scenario. The proposal design required edits after approval to reset review state, and the embedded scenario — not a newly regenerated action — was the intended unit executed after approval.

### 4.5 Two Artifacts, Two Readers, Same Reflection

The design also required substantive reasoning to be written back into the case record when the procedural outcome depended on interpretation. The local proposal served the technical audit trail; the case-system comment served the legal audit trail. Closure-recognizing outcomes were introduced specifically to avoid a structural bias toward visible procedural action when the appropriate result was acknowledgment or no further act.

### 4.6 Provenance and implementation boundary

The worked example is pinned to repository history rather than presented as a current-product assertion. Material milestones include:

- `f0c8cd95fe3f7800d467c91161cfe6db4da635b3` (2026-05-14): five-stage journey and tiered playbook framework design;
- `82a3d20736c53a355ca03107dd6e66e8bcbf7e48` (2026-05-14): content-addressed playbook identity and stricter tier-edge semantics;
- `50569aef349615af9fd41d149f2aca2b062f99ff` (2026-05-14): review-integrity and apply-contract refinements;
- `eeecb4c78a526d1defaa0d42742a036430d8f151` (2026-05-14): implemented content-addressing primitives and `pink playbooks normalize/resolve`;
- `96946547bb0a513385cccb94c82433f436ec9e9e` (2026-05-15): implemented read-only `pink playbooks list/tree/show` discovery layer;
- current PINK head inspected for this archival freeze: `cb20378754cf7182f94761ae8931dac7bf94b678` (2026-09-17).

The current repository is private and is not vendored into this Zenodo candidate. Therefore these SHAs provide author-side provenance, not independent public reproducibility of the implementation. This paper makes no claim that the later phases of the historical plan were completed, deployed, or empirically validated. The four-property architecture should be evaluated as a position/methodology proposal until a public, frozen implementation/evaluation artifact exists.

## 5. Three Semantic Questions of Applicability

The four structural properties require three antecedent conditions to hold of the target domain. We state them as design questions rather than empirical laws.

**Q1: Is there a discrete unit of action?** The pattern requires that consequential effects be decomposable into named operations whose execution can be represented by parameterized clauses. Ticket workflows, case management, transactional systems, and many control loops are plausible candidates; open conversation and creative composition are weaker fits.

**Q2: Is there a record where reflection belongs?** The pattern benefits from a persistent context where the agent's declared reasoning can be inscribed for later readers. Case records, ticket systems, electronic health records, lab notebooks, and operator logs are examples of such surfaces. Where no durable record belongs, the audit artifact may become detached from the practitioners' actual workflow.

**Q3: Does the operator want to be auditable?** The pattern intentionally produces durable structured records. In settings where durable traceability itself creates unacceptable risk — for example, some confidential-source or repressive-environment contexts — that property can be harmful rather than protective.

### 5.1 Candidate Domains

Table 1 illustrates how the questions can be used. It is a design analysis, not evidence that the full four-property architecture is already deployed in the listed domains.

| Domain | Q1: Discrete action? | Q2: Persistent record? | Q3: Audit desirable? | Candidate fit |
|---|---|---|---|---|
| Legal-administrative agency | Strong | Strong | Strong | High |
| High-frequency trading | Strong | Strong | Strong, but latency changes review placement | Conditional |
| Industrial process control | Strong | Strong | Strong | Plausible analogy |
| Clinical decision support | Strong for orders/prescriptions | Strong | Strong | Conditional |
| Software ops / SRE | Strong | Strong | Strong | High |
| Regulatory compliance attestation | Strong | Strong | Strong | High |
| Investigative journalism with confidential sources | Mixed | Mixed | Often weak/negative | Poor |

**Table 1.** *Analytical candidate assessment under the three semantic questions; not a survey of existing deployments.*

The review mechanism need not be identical in every domain. Very low-latency systems cannot support per-action human approval, so any attempted adaptation would require a different realization of governance and should not be called equivalent without testing. Industrial process control shares surface features such as structured commands, alarms, and operator records, but this paper does **not** claim that existing process-control systems instantiate the four-property conjunction.

A pattern's applicability is not the same as its desirability. Even where the three questions are favorable, affordance restriction competes with alternatives: simpler runtime policies, ordinary access control, draft/review gateways, manual workflows, or hybrid architectures. That competition motivates the controls in Section 8.

## 6. What This Is Not

**Affordance restriction is not a replacement for RLHF, CAI, or output filtering.** It operates at a different system layer and can compose with them. Nor is execution-layer restriction itself new: shielding, Progent, OpenPort and related authorization work already occupy that component. The paper's claim is only about the full composition.

**Affordance restriction is not mechanistic interpretability.** It does not recover beliefs, circuits, representations, or causal internal state. It records an externally checkable commitment. A proposal can be perfectly auditable while the internal decision process remains opaque.

**Affordance restriction is not alignment for open-ended agents.** Enumeration trades generality for governance. Where a finite or curatable action vocabulary is not meaningful, the architecture loses its defining property.

**Affordance restriction is not empirically validated by this paper.** The PINK material establishes a design and partial implementation lineage, not a measured safety benefit. Claims about reduced unauthorized effects, reviewer burden, audit quality, or maintenance cost remain hypotheses for controlled evaluation.

## 7. Limitations and Failure Modes

We document four failure modes the pattern does not eliminate.

### 7.1 Wrong-but-Valid Leaf Selection

The pattern constrains *what* the agent can do; it does not guarantee that the agent selects the appropriate allowed action. An agent can choose a wrong-but-valid leaf whose preconditions appear compatible with the case. The structured artifact makes such errors inspectable but does not prevent them.

### 7.2 Unverified Tier Realization

A structural edge can state that a procedural entry concretizes a doctrinal outcome without proving semantic realization. Lint can check identity, tier constraints, and required structural elements; semantic implication remains a human/domain-review problem unless a stronger formal semantics is added.

### 7.3 Cascading State Drift Between Executed Steps

Multi-step execution over a non-transactional external system can partially succeed and thereby invalidate later assumptions. Per-step revalidation can reduce this risk but cannot generally retrofit transactional semantics onto a legacy write surface.

### 7.4 Self-Reported Confidence Without Calibration

An agent-reported confidence field is not a calibrated probability merely because it is structured. Any archival or deployment artifact should distinguish self-report from empirically calibrated reliability.

### 7.5 Prior-art and composition limitation

The strongest novelty statement here is a negative-search result for a conjunction. Future work may locate a closer pre-cutoff antecedent, in which case the contribution boundary should narrow again. The value of the architecture does not depend on exhaustive firstness; it can be evaluated as a composition even if every component and eventually the conjunction prove to have antecedents.

## 8. Validation Roadmap

No pilot result is frozen into v0.1. Evaluation should isolate the value, if any, of the composition rather than compare only against unconstrained agents.

The prior-art audit motivates at least the following controls:

1. **Policy-only runtime gate:** deterministic allow/deny control with the same model and tools, but no scenario canon.
2. **Draft/review gateway:** structured draft + approval + execution binding, but no content-addressed scenario vocabulary.
3. **Manifest-hash capability binding:** digest-bound capability identity, but no doctrine/procedure canon.
4. **Scenario canon without content addressing:** tests whether immutable behavioral identity contributes beyond ordinary version control.
5. **Scenario canon without doctrine/procedure asymmetry:** tests whether the semantic governance split changes review quality or maintenance burden.
6. **Full affordance restriction:** all four properties.

Outcome metrics should track the actual safety/governance claims rather than generic task accuracy alone: unauthorized side-effect rate, approval/execution drift, reviewer time, wrong-but-valid action rate, silent inheritance after behavioral change, audit-reconstruction accuracy, partial-apply rate, and catalog-maintenance cost.

Any later deployment study should freeze decision rules and thresholds prospectively. This v0.1 does not precommit numerical thresholds because it contains no calibration data from the target deployment.

**Replication boundary.** The PINK development repository inspected for this version is private, and the legal canon is not part of this paper bundle. The paper therefore does not claim public reproduction of the worked PINK implementation. What is reproducible from the manuscript is the architecture and the proposed control structure; a future empirical paper should archive the executable evaluation substrate or an equivalent public fixture set before making implementation-performance claims.

## 9. Discussion

Affordance restriction occupies one corner of the agent-governance design space. Its central hypothesis is compositional: a human-readable scenario canon may become more useful as a safety and audit boundary when the same immutable objects serve simultaneously as executable vocabulary, review surface, authorization referent, and provenance anchor, with higher-cost governance for doctrine-like changes.

The prior-art correction strengthens rather than weakens the experimental question. We do not need to compare the full pattern only against an unconstrained model. Existing shielding, least-privilege, approval-binding, and capability-hash systems supply meaningful ablations. If a simpler runtime gate performs equally well on unauthorized-effect rate, reviewer effort, audit reconstruction, and maintenance cost, the extra canon machinery is not justified by the evidence. If doctrine/procedure asymmetry or immutable scenario identity provides measurable benefits under matched controls, those benefits can be attributed more narrowly.

The paper also keeps a limited notion of interpretability. The proposal artifact is an accountability surface: it records what the system was permitted and committed to do. It does not reveal internal cognition. That narrower property may still matter in regulated bounded workflows, but its practical value must be measured rather than assumed.

The remaining research questions are therefore empirical and formal: whether procedural entries can be checked against doctrinal outcomes more strongly than by human review; whether confidence can be calibrated from outcomes; how concurrent canon extension should preserve authority identity; and which audit metrics best distinguish a useful structural commitment from mere paperwork.

The contribution claimed by v0.1 is thus a bounded architectural synthesis and a testable evaluation programme. It does not claim general alignment, novel execution-layer authorization, or demonstrated deployment superiority.

## References

Alshiekh, M.; Bloem, R.; Ehlers, R.; Könighofer, B.; Niekum, S.; and Topcu, U. 2018. Safe Reinforcement Learning via Shielding. *Proceedings of the AAAI Conference on Artificial Intelligence* 32(1). https://doi.org/10.1609/aaai.v32i1.11797.

Ashley, K. D. 1990. *Modeling Legal Argument: Reasoning with Cases and Hypotheticals.* Cambridge, MA: MIT Press.

Bai, Y.; Kadavath, S.; Kundu, S.; Askell, A.; Kernion, J.; Jones, A.; Chen, A.; et al. 2022. Constitutional AI: Harmlessness from AI Feedback. arXiv:2212.08073.

Bowman, S. R.; Hyun, J.; Perez, E.; Chen, E.; Pettit, C.; Heiner, S.; Lukošiūtė, K.; et al. 2022. Measuring Progress on Scalable Oversight for Large Language Models. arXiv:2211.03540.

Branting, L. K. 2000. *Reasoning with Rules and Precedents: A Computational Model of Legal Analysis.* Dordrecht: Kluwer Academic Publishers.

Christiano, P.; Leike, J.; Brown, T.; Martic, M.; Legg, S.; and Amodei, D. 2017. Deep Reinforcement Learning from Human Preferences. In *Advances in Neural Information Processing Systems 30 (NeurIPS 2017).*

Christiano, P.; Shlegeris, B.; and Amodei, D. 2018. Supervising Strong Learners by Amplifying Weak Experts. arXiv:1810.08575.

Fikes, R. E.; and Nilsson, N. J. 1971. STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving. *Artificial Intelligence* 2(3–4): 189–208. https://doi.org/10.1016/0004-3702(71)90010-5.

Gabriel, I. 2020. Artificial Intelligence, Values, and Alignment. *Minds and Machines* 30(3): 411–437.

Hadfield-Menell, D.; Dragan, A.; Abbeel, P.; and Russell, S. 2017. The Off-Switch Game. In *Proceedings of the 26th International Joint Conference on Artificial Intelligence (IJCAI '17)*, 220–227.

Irving, G.; Christiano, P.; and Amodei, D. 2018. AI Safety via Debate. arXiv:1805.00899.

Landrock, P.; and Pedersen, T. 1998. WYSIWYS? — What You See Is What You Sign? *Information Security Technical Report* 3(2).

McCarty, L. T. 1977. Reflections on TAXMAN: An Experiment in Artificial Intelligence and Legal Reasoning. *Harvard Law Review* 90(5): 837–893.

Merkle, R. C. 1987. A Digital Signature Based on a Conventional Encryption Function. In *Advances in Cryptology — CRYPTO '87*, LNCS 293, 369–378. Berlin: Springer.

North, D. 2006. Introducing BDD. *Better Software Magazine*, March 2006.

Ouyang, L.; Wu, J.; Jiang, X.; Almeida, D.; Wainwright, C. L.; Mishkin, P.; Zhang, C.; et al. 2022. Training Language Models to Follow Instructions with Human Feedback. In *Advances in Neural Information Processing Systems 35 (NeurIPS 2022).*

Rissland, E. L.; and Ashley, K. D. 1987. A Case-Based System for Trade Secrets Law. In *Proceedings of the 1st International Conference on Artificial Intelligence and Law (ICAIL '87)*, 60–66.

Russell, S. 2019. *Human Compatible: Artificial Intelligence and the Problem of Control.* New York: Viking.

Shi, T.; et al. 2025. Progent: Programmable Privilege Control for LLM Agents. arXiv:2504.11703.

SLSA. 2023. Supply-chain Levels for Software Artifacts, Specification v1.0. https://slsa.dev/spec/v1.0/.

South, T.; et al. 2025. Authenticated Delegation and Authorized AI Agents. arXiv:2501.09674.

Suchman, L. A. 1987. *Plans and Situated Actions: The Problem of Human-Machine Communication.* Cambridge: Cambridge University Press.

Torres-Arias, S.; Afzali, H.; Kuppusamy, T. K.; Curtmola, R.; and Cappos, J. 2019. in-toto: Providing Farm-to-Table Guarantees for Bits and Bytes. In *Proceedings of the 28th USENIX Security Symposium*, 1393–1410.

Wu, J.; et al. 2026. SkillScope: Toward Fine-Grained Least-Privilege Enforcement for Agent Skills. arXiv:2605.05868.

Wynne, M.; and Hellesøy, A. 2012. *The Cucumber Book: Behaviour-Driven Development for Testers and Developers.* Raleigh, NC: Pragmatic Bookshelf.

Zhou, Z. 2026. Governing Dynamic Capabilities: Cryptographic Binding and Reproducibility Verification for AI Agent Tool Use. arXiv:2603.14332.

Zhu, G.; et al. 2026. OpenPort Protocol: A Security Governance Specification for AI Agent Tool Access. arXiv:2602.20196.
