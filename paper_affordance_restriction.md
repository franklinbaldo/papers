# Alignment by Affordance Restriction: A Pattern for Auditable Bounded Agents

**Franklin Silveira Baldo**
*Procuradoria-Geral do Estado de Rondônia / Universidade Federal de Rondônia*
*franklin@pge.ro.gov.br*

*Target venue: SafeAI @ AAAI 2027 (workshop, ~8 pages + references).*
*Draft status: TDD-for-research. Citations marked `[CITATION NEEDED]` indicate references the author intends to verify and engage in subsequent revision. Real citations to verified works are given inline as `[Author Year]`.*

---

## Abstract

We describe *alignment by affordance restriction*: an alignment pattern in which an agent's action space is constrained by a curated, content-addressed catalog of allowed scenarios rather than by reward modeling, output filtering, or behavioral training. The pattern has four structural properties — affordance enumeration, doctrine/procedure separation, structured ex-ante commitment, and content-addressed canon — and we argue that an instance of the pattern exhibits all four. We identify three semantic conditions that determine the pattern's applicability to a target domain: whether there exists a discrete unit of action, whether there is a record where reflection persists, and whether the operator wishes to be auditable. We instantiate the pattern in PINK, a legal-administrative agent system under development at the Brazilian state attorney's office for the State of Rondônia, with design complete and phased implementation underway. We characterize four failure modes that survive the pattern's application, present a validation roadmap with metrics targeted for the pilot deployment, and situate the pattern against training-based alignment, scalable oversight, mechanistic interpretability, and legal expert systems.

## 1. Introduction

Public discourse on AI alignment is dominated by techniques that act on the model itself: reward modeling and reinforcement learning from human feedback [Ouyang et al. 2022], constitutional methods that train models against principle-stated critiques [Bai et al. 2022], output filtering pipelines, and interpretability research aimed at recovering intent from internal state. These techniques operate by changing what the model is or by filtering what it produces. We describe a complementary pattern that operates earlier: it changes what the model is *allowed to do*, where "allowed" is enforced by syntax rather than by training.

We call this pattern *alignment by affordance restriction*. An agent's action space is the projection of a curated, content-addressed catalog of allowed scenarios written in a human-readable specification language. The agent does not generate actions; it instantiates entries from the catalog by binding parameter slots to values from the case at hand. The catalog grows monotonically; additions are git commits subject to human review. Edits to existing entries are structurally impossible — content change yields a new identity, and prior bindings either resolve to the original entry or fail cleanly. The pattern is old in spirit (expert systems [Ashley 1990], doctrinal codification, behavior-driven development [North 2006]) but newly tractable: a contemporary LLM is competent at selecting from and binding to a catalog without needing to extend it on the fly, which is the operational shift that makes the pattern useful where it was previously only conceptually attractive.

This paper makes three contributions:

1. We name and characterize the affordance-restriction pattern as a class of alignment techniques distinct from training-based and filtering-based approaches, identifying four structural properties that make instances of the pattern recognizable.

2. We identify three semantic conditions on the target domain that determine whether the pattern is applicable: the existence of a discrete unit of action, the existence of a record where reflection persists, and the operator's interest in auditability. We apply these conditions to seven candidate domains.

3. We present PINK, a legal-administrative agent system under development with design complete and phased implementation underway, as a worked example with documented architecture, four named failure modes, and an explicit validation roadmap.

The paper proceeds as follows. Section 2 situates the pattern in the alignment, scalable-oversight, and legal-informatics literatures. Section 3 articulates the four structural properties. Section 4 walks through PINK's instantiation of each. Section 5 develops the three semantic questions and applies them across domains. Sections 6 and 7 enumerate what the pattern is not and the failure modes that survive its application. Section 8 lays out deployment status and validation plans. Section 9 closes.

## 2. Background and Related Work

**Alignment via model modification.** Two dominant techniques act on the model. Reinforcement learning from human feedback fits a reward model from preference comparisons and trains the policy to maximize predicted reward [Christiano et al. 2017; Ouyang et al. 2022]. Constitutional AI replaces direct human feedback with model-generated critiques against a written constitution [Bai et al. 2022]. Both modify the model's distribution over outputs without constraining the space of possible outputs in any verifiable structural sense. Affordance restriction is complementary rather than competing: it changes the syntactic space the model selects within, independently of how the model was trained. RLHF-trained and constitutionally-trained models can sit inside an affordance restriction without contradiction; the techniques compose.

**Scalable oversight.** The bandwidth question — how does a human supervise a system fast enough to keep up — is shared between affordance restriction and the scalable-oversight literature [Christiano, Shlegeris, and Amodei 2018; Bowman et al. 2022; Irving, Christiano, and Amodei 2018]. The strategies diverge sharply. Scalable oversight amplifies the human supervisor (via debate, recursive amplification, weak-to-strong generalization) to keep pace with a more capable learner. Affordance restriction constrains the learner's action space such that human oversight remains feasible at fixed human bandwidth. The two can compose; in domains where the affordance set is bounded and the proposal volume is matched to approval throughput, oversight amplification is not required.

**Corrigibility and human-in-the-loop control.** Hadfield-Menell et al. [2017] formalize corrigibility as a game-theoretic property under which an agent voluntarily defers to human control. The structured commitment property in our pattern (Section 3) is a concrete shape of this: every action is the projection of a human-approved instance of a human-curated scenario, with the approval recorded as a state transition on a structured artifact. Russell [2019] argues for value uncertainty as the foundation of safe agency; our pattern is silent on value learning but provides a substrate within which value commitments — encoded as the doctrinal layer of the catalog — are explicit, finite, and version-controlled.

**Plans as accountability.** Suchman's distinction between *plans-as-cognition* and *plans-as-accountability* [Suchman 1987] is central to interpreting our pattern. The proposal artifact in our instantiation (Section 4) is not a record of the agent's decision process; it is the structured commitment by which the decision will be judged. Mechanistic interpretability seeks to recover intent from internal state; our pattern instead requires the agent to externalize its intent as a parseable artifact before any action is taken. The two strategies answer different questions about a system; neither replaces the other.

**Content-addressed software artifacts.** The structural use of content-addressing in our canon borrows from supply-chain security work. Merkle trees [Merkle 1987] supply the cryptographic foundation; in-toto attestations [Torres-Arias et al. 2019] and the SLSA framework [CITATION NEEDED: SLSA v1.0 specification, slsa.dev, 2023] establish per-artifact provenance for software build pipelines. We extend the technique from build artifacts to behavioral specifications: the agent's allowed action vocabulary becomes itself a content-addressed directed acyclic graph, with the same audit properties applied to a different artifact class.

**Behavior-driven development.** Gherkin, the specification language used in our instantiation, originates in BDD [North 2006; Wynne and Hellesøy 2012]. BDD designed Gherkin for human-readable test specifications of human-built systems; we appropriate it for human-curated action specifications of LLM-driven agents. The grammar fits because it was originally designed for a similar audience: domain experts who must agree, in prose, with engineers, on what a system should do. The semantics shifts — the same syntax that specifies test scenarios in BDD specifies allowed actions in our pattern — but the grammar's human-readability properties carry over.

**Legal expert systems.** The deep prehistory of our worked example is the legal-expert-systems literature: HYPO [Rissland and Ashley 1987] and CATO [CITATION NEEDED: Aleven and Ashley, CATO system, 1990s] modeled legal argument via case-based reasoning; rule-based systems for tax law [McCarty 1977] integrated structured legal rules with case retrieval; later hybrid systems combined both [Branting 2000]. These systems aimed to *replace* legal reasoning with formal machinery; the present work aims instead to *bound* it. The agent reasons under a catalog curated by lawyers; the lawyers retain authority; the catalog records what reasoning is legitimate, not what conclusions are correct on a given case.

**The alignment-as-values literature.** Gabriel [2020] argues that AI alignment is best understood as a problem of value identification rather than capability constraint. Our pattern is consistent with this framing: the doctrinal layer of the catalog (Section 3) explicitly encodes value commitments distinct from the procedural layer, and extending doctrine requires a heavier review gesture than extending procedure. We do not propose a method for *discovering* values; we propose a structural separation between values and instrumental policies in agent action spaces, leaving value-discovery to the human curators of the catalog.

## 3. The Pattern: Alignment by Affordance Restriction

We characterize alignment by affordance restriction via four structural properties. An instance of the pattern exhibits all four; absence of any indicates a related but distinct technique.

### 3.1 Property 1: Affordance Enumeration

The agent's allowed actions are the entries in a finite catalog. The catalog is human-curated; additions require human approval; the agent does not act outside it. Each entry is a parameterized scenario: a pattern of preconditions, an action sequence, and metadata identifying its role in the catalog graph. Operating on a case means selecting an entry whose preconditions describe the case and instantiating it by binding parameters to concrete values.

Affordance enumeration distinguishes the pattern from prompt-based restriction ("you must only do X, Y, Z") and from output filtering ("if the output looks like W, refuse"). Prompt-based restriction is not enforceable; the model can be jailbroken, can misunderstand instructions, or can simply not follow them under sufficient context pressure. Output filtering reacts after the fact and cannot prevent novel attack surfaces; its blacklist grows monotonically by design. Affordance enumeration is enforced at the system boundary, not at the model boundary: actions not parseable as catalog instantiations cannot reach the world, regardless of what the model produces internally.

### 3.2 Property 2: Doctrine/Procedure Separation

The catalog stratifies. A doctrinal layer (which we call *Tier 1* in our instantiation) declares what counts as a legitimate outcome in a class of situations; the action clauses in this layer are *assertions* about state, not instructions. Procedural layers (*Tier 2+*) declare concrete action sequences that, if executed, produce the doctrinal outcomes. The procedural layers concretize the doctrinal layer through structural references — in our content-addressed instantiation, by carrying a tag that points at the doctrinal scenario's content hash.

Procedural addition is cheap: a new specialization passes a linter, receives review, and lands. Doctrinal addition is structurally expensive: the proposal carries an explicit doctrinal-alert flag, sits in a separate review queue, requires a confirmation gesture that names the proposal individually, and never enters batch operations. The asymmetry encodes a value commitment: extending procedure is recognized as common and acceptable; extending doctrine is rare and reflective. This maps the philosophical distinction between instrumental policies and value commitments [Russell 2019] onto a concrete review workflow with different gating costs.

### 3.3 Property 3: Structured Ex-ante Commitment

Before acting, the agent emits a proposal — a structured artifact carrying (a) the catalog entry it instantiates, identified by content hash; (b) the bindings of placeholders to case values; (c) a record of the path traversed through the catalog graph to reach the selected entry; (d) a narrative justification; and (e) the instantiated scenario in executable form. The same artifact is the input to human approval, the input to the executor on approval, and the durable audit record after execution. There is no translation step between approval-time content and execution-time content; the executor parses the same string the reviewer read.

The interpretability claim is structural rather than computational. The agent's intent is not recovered from internal state via probing or attribution; it is *required to be externalized* as a parseable commitment before any action takes effect. A reviewer reads the proposal and sees: which catalog entry, with which bindings, justified by which descent through the catalog, with which expected effects. The opacity of the underlying model is bracketed; what the model committed to is on disk.

This is interpretability via *what the model said it would do*, not via *what we can recover about how the model decided*. The two notions are not substitutes (Section 6), but the former is operationally tractable in ways the latter currently is not.

### 3.4 Property 4: Content-addressed Canon

Catalog entries are identified by hash of normalized content. Filenames embed the hash prefix as a structural element, not as a separate identifier. Edges in the catalog graph — the structural references between entries — point at hashes, not at filesystem paths. Edits to an entry are not possible in place: changing content yields a new hash, which yields a new file. Past references to the original entry remain valid (the file with the original hash either exists or doesn't); new references must point at the new hash explicitly.

Two properties follow. First, the catalog is a Merkle directed acyclic graph; acyclicity is guaranteed by construction when tier-difference rules force edges from higher tiers to strictly lower tiers, and the linter rule for acyclicity reduces to a single comparison per edge. Second, audit reconstruction is deterministic: a proposal pinned to a hash either resolves to a specific normalized content or fails to resolve, with no third option. Silent edits — a class of failure that complicates audit in append-only-with-versioning systems — are eliminated structurally rather than detected procedurally.

The four properties are not independent. Property 4 enables Property 3 to make a stronger claim (commitment is to a specific content, not to a mutable reference); Property 2 requires Property 1 (stratification presupposes enumeration); Property 3 requires Property 4 (durable commitment requires durable referents). The pattern's coherence comes from the conjunction.

## 4. PINK as Worked Example

PINK is an agent system under active development at the Procuradoria-Geral do Estado de Rondônia (PGE-RO), the state attorney's office for the State of Rondônia, Brazil. The system of record, Kanoê, holds case data for the attorney office's docket; PINK operates read-only against Kanoê via a Metabase data layer and writes back only via a separately-gated subsystem invoked under explicit human approval. The first deployment target is the docket of approximately 8,000 active cases in pension litigation (RPPS — *Regime Próprio de Previdência Social*), a domain characterized by recurring procedural patterns, statutory complexity, and high audit sensitivity arising from the constitutional and quasi-judicial nature of state pension adjudication.

### 4.1 Pipeline

PINK structures agent operation as a five-stage pipeline: *Discover* (read case data densely into agent context), *Fetch* (download referenced documents to local storage), *Propose* (descend the catalog, bind parameters, write the proposal artifact), *Review* (human triages and approves, rejects, or edits), *Apply* (execute approved scenario against Kanoê via the gated write subsystem).

```mermaid
graph LR
  D[Discover<br/><i>read</i>] --> F[Fetch<br/><i>read</i>]
  F --> P[Propose<br/><i>local fs write</i>]
  P --> R[Review<br/><i>human gate</i>]
  R --> A[Apply<br/><i>Kanoê write + comment</i>]
```

**Figure 1.** *The five-stage pipeline. Stages 1–3 are read-only against the system of record; stage 4 is human gating; stage 5 is the only stage that mutates case state, and only by dispatching to an explicit, narrow write API.*

### 4.2 Catalog Structure

Catalog entries are Gherkin `.feature` files in Brazilian-Portuguese keyword variant (`Funcionalidade`, `Cenário`, `Dado`, `Quando`, `Então`, `E`), organized under directory paths `playbooks/tier1/`, `tier2/`, etc. Each entry's filename embeds the 8-hex-character prefix of a UUIDv5 computed over the entry's normalized content (line-ending normalization, keyword case-folding, sorted tags, sorted parameter block, trailing whitespace stripped, final newline). Tags within each file declare its tier and, for Tier 2+, the content hashes of the entries it concretizes — for example, `@concretiza:a1b2c3d4`. Aciclicity is enforced by a single linter rule: every concretization edge points to an entry whose tier number is strictly lower than the source's.

Figure 2 illustrates a small canon: one Tier 1 outcome (registering a procedural deadline), two Tier 2 concretizations of it (electronic citation in defense procedure; mere-acknowledgment for non-deadline communications), and one Tier 3 leaf specializing one of the Tier 2 cases for the situation where no work-box has been assigned to the case file. Leaves — nodes with no children — are the only entries the agent may bind directly. Non-leaves are *abstract*: adding a deeper specialization that concretizes them automatically retires them from direct binding for that branch.

**Figure 2.** *Tier hierarchy in the canon. Tier 1 declares outcome; Tier 2 concretizes Tier 1 via `@concretiza:` edges pointing at content hashes; Tier 3 adds situational specialization. The graph is a DAG by construction (edges flow only from higher tiers to strictly lower tiers).*

### 4.3 Traversal, Not Matching

The agent loads the upper canon (Tier 1 and Tier 2) into its working context — a small, slow-changing, human-curated subset. For a case stimulus (typically an *expediente* — a procedural communication from the court), the agent identifies a candidate Tier 2 entry whose preconditions match the case, then queries `pink playbooks children` against the candidate's hash. An empty result indicates a leaf (no deeper specialization exists for this branch); a non-empty result requires the agent to read each child and recurse, selecting the child whose preconditions match the case at the current level of specificity. The descent terminates at a leaf; the leaf is bound. If at any descent step no child of the current node fits the case, the agent proposes a new specialization under the current node, with the appropriate concretization edge.

PINK itself performs no matching, ranking, or fuzzy comparison. It exposes the canon as a graph and serves structural queries (`children`, `is-leaf`, `ancestors`). All inference — which Tier 2 fits the case, which child fits at each level of descent — happens in the LLM. The system is, by design, ignorant of its own content: it answers structural questions deterministically and lets the agent perform the semantic work.

The descent path itself is recorded in the proposal's `traversal` field, with the hash of each visited entry. A reviewer asking *why did the agent descend this far, and through which alternatives* can reconstruct the chain step by step from the artifact, without inspecting the agent's internal state.

### 4.4 The Proposal Artifact

A proposal is a markdown file under `.pink/<case>/proposals/<expediente_id>.md` with YAML frontmatter (catalog reference, traversal, bindings, status, agent self-reported confidence), a narrative reasoning section, and an embedded Gherkin block representing the instantiated scenario. The same artifact is parsed by `pink propose apply` after human approval; the embedded Gherkin's `Então` clauses dispatch to the corresponding write primitives in the gated Kanoê subsystem.

The frontmatter is the machine contract; the embedded Gherkin is the executable; the narrative is the human-readable justification. All three carry the same substantive content in different registers. Lint enforces that the last entry of `traversal` matches the catalog reference, that bindings are complete and well-typed, and that the structure of the embedded Gherkin matches the bound entry's structure modulo placeholder substitution.

### 4.5 Two Artifacts, Two Readers, Same Reflection

When apply executes against the case, the proposal's substantive reasoning is also posted as a comment on the corresponding case record in Kanoê. The technical audit trail — the proposal markdown, content-addressed, git-trackable — and the legal audit trail — the comment in the case record, durable in the case file and readable by any lawyer accessing the case in the future — carry the same substantive content. The technical reviewer reconstructs what the system did; the legal reviewer reads what was reasoned, in the place a lawyer would already be looking. Neither audit requires access to the other.

This property is not incidental. The seed canon for the pilot deployment includes explicit closure-recognizing Tier 1 outcomes: scenarios whose doctrinal claim is that acknowledgment without procedural action is a legitimate result, *provided* the substantive reason for non-action is recorded as a comment on the case record. The pattern requires that the agent's reflection on cases that warrant no procedural action be captured as a durable artifact in the system of record, not merely as an entry in a local-filesystem audit trail. Otherwise the agent is structurally biased toward proposing action whenever action is bindable, and the audit trail of acknowledgment is invisible to the legal reviewer who actually opens the case.

### 4.6 Implementation Status

Design is complete and merged. Phase 0 (audit of pre-existing CLI test specifications for consistency with the design) is complete; 17 existing feature files have been amended or marked deprecated, and 11 new test feature files have been enumerated for the implementation phases. Phases 1 and 2 (read-side affordances and catalog plumbing) are in flight: the content-addressing infrastructure (UUIDv5 namespace, content normalization function, filename parser, UUID-to-path resolver, `pink playbooks normalize` for opt-in rewriting, `pink playbooks lint` for read-only verification) is being built as a prerequisite to all canon-aware commands. Phase 3 (seed canon) is scheduled for Q3 2026 with curation by the legal team at PGE-RO. Phases 4 and 5 (proposal pipeline and apply) follow, targeting first production binding-and-apply against a pilot docket by end of Q3 2026.

## 5. Three Semantic Questions of Applicability

The four structural properties (Section 3) require three antecedent conditions to hold of the target domain. We state them as questions to be answered before considering the pattern.

**Q1: Is there a discrete unit of action?** The pattern requires that what the agent does be decomposable into named steps whose execution against the world can be specified by parameterized clauses. Free creative writing fails this test: a condolence letter is not three executable steps in any meaningful sense, and forcing it into that shape destroys what makes the letter what it is. Domains with strong action discreteness include ticket-based workflows, case management, transactional systems, and control loops. Domains with weak discreteness include open conversation, exploratory analysis, and creative composition.

**Q2: Is there a record where reflection belongs?** The pattern requires a persistent context where the agent's reasoning can be inscribed for future readers — readers who consult the record because that is where one looks for the history of the case, ticket, account, or system. Without such a record, the technical audit trail (Property 3) is isolated from the working context of the domain's practitioners, and the two-artifact property (Section 4.5) degrades to a single technical archive that practitioners do not consult. Case records, ticket systems, electronic health records, lab notebooks, and operator logs are positive examples. Real-time conversation, private deliberation, and most creative work are negative examples.

**Q3: Does the operator want to be auditable?** The pattern produces durable, structured records of agent activity. In domains where the operator's professional or legal posture *requires* that activity not be durably structured — confidential investigative journalism, internal litigation strategy under professional privilege, dissent under repressive regimes — the pattern is a trap rather than a tool. The artifacts that make the pattern interpretable in benign contexts become instruments of surveillance, discovery, or persecution in adversarial ones. We treat this as a structural condition, not a preference: where audit cannot exist without harming the operator, the pattern is inappropriate regardless of design refinement.

### 5.1 Applicability Across Domains

Table 1 applies the three questions to seven candidate domains.

| Domain | Q1: Discrete action? | Q2: Record? | Q3: Wants audit? | Pattern fits? |
|---|---|---|---|---|
| Legal-administrative agency (PINK) | Yes (procedural acts on case) | Yes (case record) | Yes (constitutional requirement) | **Yes** |
| High-frequency trading | Yes (trade orders) | Yes (regulatory logs) | Yes (regulatory mandate) | Yes (with sampling-based approval) |
| Industrial process control | Yes (setpoints, alarms) | Yes (operator log) | Yes (safety regulation) | Yes (pattern already implicit) |
| Clinical decision support | Yes (orders, prescriptions) | Yes (EHR) | Yes (clinical liability) | Yes |
| Software ops / SRE | Yes (commands, runbooks) | Yes (ticket system) | Yes (incident review) | Yes |
| Regulatory compliance attestation | Yes (filings, attestations) | Yes (case management) | Yes (statutory) | Yes |
| Investigative journalism (confidential sources) | Qualified (research operations) | Sometimes (story notes) | **No** | **No** |

**Table 1.** *Applicability of the affordance-restriction pattern across candidate domains. Cells answer the three semantic questions; the final column gives an overall verdict.*

The first six rows have all three answers as yes; the pattern applies cleanly, with the placement of human approval varying with the throughput requirements of the domain. In high-frequency trading, ex-ante per-trade approval is infeasible at the latencies involved; the human approval property is realized instead through a combination of automated boundary checks, post-hoc sampling, and complete structured records that enable forensic reconstruction of every decision. The pattern's interpretability claim remains intact even where ex-ante approval is replaced by structured post-hoc review — the artifacts are still parseable commitments, just inspected after the fact rather than before. Industrial process control is the pattern with different vocabulary already in place: the playbook is the controller, the proposal is the setpoint or alarm acknowledgment, the case record is the operator log; supervisor approval is implicit in boundary conditions and explicit only at alarm escalation [CITATION NEEDED: representative reference on operator-log auditability in process industries]. Legal-administrative agency, where PINK operates, sits at the low-throughput end of the spectrum: ex-ante human approval per proposal is feasible, the case record is the natural location of reflection, and the audit interest is constitutional.

The seventh row fails the third question structurally. Affordance restriction here would produce audit artifacts whose subpoena value would compromise sources; the pattern is inappropriate. We note this not as a peripheral case but as the boundary that defines the pattern's scope: when an operator must remain unauditable to be effective, no design refinement rescues the technique. The pattern carries an embedded assumption — that audit is desirable for the operator — that does not survive transplantation to adversarial-information settings.

A pattern's applicability is not the same as its desirability. Even where all three answers are yes, the pattern competes with alternatives: less-structured agents with more capable post-hoc review, fully manual workflows for low-volume cases, or hybrid approaches that use affordance restriction for the procedural majority and human-only handling for the doctrinally novel minority. We claim only that the three questions are *necessary*: where any answer is no, the pattern does not apply, and design refinement cannot fix this.

## 6. What This Is Not

We anticipate three over-readings of the pattern that its framing may invite.

**Affordance restriction is not a replacement for RLHF, CAI, or output filtering.** It operates at a different system layer. A model whose distribution over outputs is shaped by reward modeling can sit inside an affordance restriction without contradiction; the two techniques are composable and address different failure modes. RLHF reduces the likelihood that the model produces harmful or unhelpful outputs; affordance restriction guarantees that whatever the model produces, only parseable instantiations of catalog entries can reach the world. A safety-relevant deployment might use both: RLHF to align the model's preferences, affordance restriction to constrain its possible actions, and human approval to gate execution. The pattern's claim is that for domains satisfying the three questions, additional constraint at the affordance layer offers structural properties (auditability, monotonic doctrine growth, durable commitment) that training-based techniques do not provide on their own, however well-trained the model.

**Affordance restriction is not mechanistic interpretability.** It does not recover the model's internal state, attribute outputs to circuits, or expose representations. It answers a different question: not *what does the model believe* but *what did the model commit to, on this case, under what justification, with what expected effect*. The two are not substitutes. Mechanistic interpretability asks about the system in the abstract or about its general dispositions; affordance restriction asks about the system on a particular act. For deployment review, post-hoc audit, and regulatory compliance, the latter question is often the operationally relevant one — what did the system do on case X, and why, and was it appropriate — and the former is currently intractable for systems at the scale of contemporary LLMs.

**Affordance restriction is not alignment for open-ended agents.** The three semantic questions delimit where the pattern applies. An open-ended creative assistant, a general-purpose chat interface, or an exploratory research agent operating without ticket structure each fail at least one of the questions. The pattern offers nothing for these settings beyond the trivial observation that explicit action vocabularies are clearer than implicit ones. We do not propose that alignment in general can be solved by enumeration; we propose that in *bounded domains where enumeration is possible*, the pattern offers structural properties that are otherwise difficult to obtain.

## 7. Limitations and Failure Modes

We document four failure modes the pattern does not eliminate.

### 7.1 Wrong-but-Valid Leaf Selection

The pattern constrains *what* the agent can do; it does not guarantee *that the agent picks the right action* within the constrained space. A misaligned matcher can consistently bind the wrong-but-valid leaf for a case — for example, treating an informative communication as deadline-bearing because no closure-recognizing leaf was present in the upper canon, or selecting a procedural concretization whose preconditions are technically satisfied but whose substantive fit to the case is poor. Mitigation depends on canon design: every Tier 1 must have closure-recognizing concretizations (the closure pattern is not optional — see Section 4.5), and the seed canon must cover the space of legitimate outcomes without leaving inadvertent gaps that channel the agent toward the wrong tier.

The structural pattern itself *enables the failure to be detected* — the proposal records exactly what was bound, against which leaf, with what bindings and traversal — but does not prevent it. Post-hoc detection requires sampling and human review of bound leaves against ground-truth case outcomes. We treat this as the primary validation target for the pilot deployment (Section 8).

### 7.2 Unverified Tier Realization

The pattern's structural rules require that every concrete (Tier 2+) entry concretize a doctrinal (Tier 1) entry by hash reference; the linter verifies the reference exists and points to a strictly lower tier. The linter does *not* verify that the concrete `Então` clauses *semantically realize* the doctrinal outcomes. A concretization can carry the correct tag while encoding actions that drift from the parent's intent. This is the soft seam of the pattern: realization checking is the domain expert's job at review time, and lint cannot replace it.

Formal-methods extensions — proving realization via step-level annotations, or via partial-order reasoning over outcome predicates — are a research direction we identify but do not address in v1. The current state of the pattern accepts this as an unverified property and relies on human review at canon-entry time, periodic audit of the canon against the cases it has been applied to, and the structural separation of doctrine/procedure as the mechanism by which doctrine drift becomes visible.

### 7.3 Cascading State Drift Between Executed Steps

Apply is best-effort, not transactional. When a proposal has *N* action clauses and the first *k* succeed while step *k+1* fails, the world has changed in ways the original proposal-time precondition validation did not account for. The retry mechanism handles re-attempting failed steps but does not handle the case where executing the first *k* actions invalidated preconditions of step *k+2*. We mitigate by per-step revalidation declarations — preconditions marked as volatile are re-checked at apply time against fresh data — but we do not eliminate the failure mode. Transactional semantics over a non-transactional write subsystem cannot be retrofitted at the proposal layer; either the underlying write subsystem provides transactional guarantees (which is rare in legacy case-management systems and not the case for Kanoê), or the pattern accepts best-effort with documented partial-apply semantics.

### 7.4 Self-Reported Confidence Without Calibration

Proposals carry an agent-reported confidence field. In v1 this field is uncalibrated: no feedback loop ties past apply outcomes to per-playbook confidence statistics. Readers of the proposal who interpret the field as a probability are misled. We currently mitigate by documentation; structural calibration via tracking apply outcomes per playbook is identified as future work but is not part of the pattern in its current statement. Until calibration exists, the field is best read as an indicator of the agent's working uncertainty, not as a probability.

We expect deployment to surface additional failure modes that the present statement of the pattern does not anticipate; the validation roadmap (Section 8) includes structured surfaces for capturing them and revising the pattern accordingly.

## 8. Deployment Plan and Validation Roadmap

PINK is in active development. We summarize current status and the validation milestones over the next six months.

**Phase status.** Phase 0 (audit of pre-existing CLI test specifications against the design) is complete: 17 existing feature files have been amended or marked deprecated, and 11 new test feature files have been enumerated. Phases 1–2 (read-side affordances and catalog plumbing) are partially implemented; the content-addressing infrastructure is the present focus. Phase 3 (seed canon) is scheduled to begin once Phases 1–2 stabilize; the seed canon will be curated by the legal team at PGE-RO, with the closure-recognizing Tier 1s as required content. Phases 4 and 5 (proposal pipeline and apply) follow, with first production binding-and-apply against a pilot docket of approximately 200 cases targeted for end of Q3 2026.

**Validation metrics.** We commit to instrumenting and reporting the following during the pilot:

- *Proposal volume and disposition.* Number of proposals emitted; distribution across approve, reject, edit-then-approve, and let-expire. Establishes baseline throughput and intervention rate.
- *Edit-before-approve rate.* Fraction of approved proposals that the human modifies during review. High rates indicate either matcher errors (the agent is selecting wrong-but-valid leaves; Section 7.1) or scenario design issues (the canon's leaves are insufficiently specific).
- *Canon extension frequency.* New leaf additions per unit time; new Tier 1 elevations per unit time. Rapid Tier 1 elevation indicates either an underdeveloped seed canon or active domain reconceptualization. Slow Tier 2+ growth indicates the catalog has reached coverage stability.
- *Stale rate after canon evolution.* Fraction of approved-but-unapplied proposals that become stale (their bound leaf gains a child between approval and apply, retiring it from direct binding) before apply. High rates indicate timing mismatches between agent activity and curator activity.
- *Apply success and partial-apply rate.* Fraction of approved proposals that reach `applied`; fraction that reach `partial`; distribution of step-level failures across volatile-precondition stale, write-API error, and unhandled exception. Measures the cost of best-effort apply (Section 7.3).
- *Audit reconstruction by third-party reviewer.* A blinded reviewer — neither the operating lawyer nor the system author — reconstructs the agent's action and justification on a random sample of cases from artifacts alone, without consulting the agent or the operating lawyer. Reconstruction accuracy is our central interpretability metric: a value below threshold indicates the pattern's structural commitment is not, in practice, sufficient for downstream audit, and the pattern's interpretability claim fails empirically.

We do not pre-commit to thresholds for these metrics, because no prior reference exists against which to calibrate them for this specific class of system. A follow-up paper will report the pilot's quantitative results and propose tentative norms; the present paper's contribution is the pattern, the applicability criterion, and the design that supports such measurement.

**Replication.** PINK's implementation is open-source [CITATION NEEDED: PINK repository URL]; the legal canon is curated content owned by PGE-RO and is not redistributed, but the canon's structure, lint rules, and content-addressing infrastructure are general and reusable. We document the canon structure in detail in the project's `PLAYBOOKS.md` to enable replication of the pattern in other domains.

## 9. Discussion

Three implications close the paper.

First, the pattern situates one corner of the alignment design space. Affordance restriction is not a general solution to alignment; it is a class of techniques that buys structural properties — auditability, controllability, durable commitment, monotonic canon growth — at the cost of generality. The three semantic questions are the price tag, and they delimit the pattern's scope honestly. We do not claim what the pattern cannot deliver: alignment for open-ended agents, generality across creative or conversational domains, or interpretability of model internals.

Second, the pattern offers a workable notion of interpretability for bounded systems. Rather than recovering intent from weights via probing or attribution, the system requires the agent to commit intent to a parseable artifact ex ante. The technique scales with the domain expert's capacity to read structured artifacts, not with the analyst's capacity to interpret model internals. For many production deployments — legal, regulatory, clinical, operational — this is the more tractable form of the interpretability question, and the form that downstream audit actually needs.

Third, the pattern raises questions adjacent to but outside its scope. We list four:
- *Formal-methods extensions for tier realization verification.* Can the lint verify, not merely assert, that a Tier 2+ entry's `Então` clauses realize the Tier 1 outcomes they claim to concretize?
- *Confidence calibration from apply outcomes.* Can the self-reported confidence field be replaced or augmented by an empirical confidence statistic learned from past apply outcomes per playbook?
- *Multi-agent canon extension.* When multiple agents propose new concretizations against a shared canon simultaneously, how should proposal conflicts be mediated, and what hash-stability properties survive the resulting merge?
- *Quantitative interpretability metrics for structural commitment.* Beyond third-party reconstruction accuracy, what other empirical handles measure the interpretability that the pattern claims to provide?

We identify these as research directions without addressing them in this paper.

The pattern is older than alignment as a research field. Its newer claim is that the substrate has caught up: LLMs are competent at selecting from and binding to a curated vocabulary, which makes the pattern operationally feasible in domains where it was previously only conceptually attractive. In those domains, alignment by affordance restriction offers what training-based techniques and post-hoc filtering cannot: structural guarantees about the action space, durable commitment to specific actions on specific cases, and interpretability via what was committed rather than via what can be recovered. The cost is generality; the question is whether the bounded domains in which the pattern applies are economically and societally significant enough to be worth the design effort. We believe they are, and PINK is one such case.

## References

Ashley, K. D. 1990. *Modeling Legal Argument: Reasoning with Cases and Hypotheticals.* Cambridge, MA: MIT Press.

Bai, Y.; Kadavath, S.; Kundu, S.; Askell, A.; Kernion, J.; Jones, A.; Chen, A.; et al. 2022. Constitutional AI: Harmlessness from AI Feedback. arXiv:2212.08073.

Bowman, S. R.; Hyun, J.; Perez, E.; Chen, E.; Pettit, C.; Heiner, S.; Lukošiūtė, K.; et al. 2022. Measuring Progress on Scalable Oversight for Large Language Models. arXiv:2211.03540.

Branting, L. K. 2000. *Reasoning with Rules and Precedents: A Computational Model of Legal Analysis.* Dordrecht: Kluwer Academic Publishers.

Christiano, P.; Leike, J.; Brown, T.; Martic, M.; Legg, S.; and Amodei, D. 2017. Deep Reinforcement Learning from Human Preferences. In *Advances in Neural Information Processing Systems 30 (NeurIPS 2017).*

Christiano, P.; Shlegeris, B.; and Amodei, D. 2018. Supervising Strong Learners by Amplifying Weak Experts. arXiv:1810.08575.

Gabriel, I. 2020. Artificial Intelligence, Values, and Alignment. *Minds and Machines* 30(3): 411–437.

Hadfield-Menell, D.; Dragan, A.; Abbeel, P.; and Russell, S. 2017. The Off-Switch Game. In *Proceedings of the 26th International Joint Conference on Artificial Intelligence (IJCAI '17),* 220–227.

Irving, G.; Christiano, P.; and Amodei, D. 2018. AI Safety via Debate. arXiv:1805.00899.

McCarty, L. T. 1977. Reflections on TAXMAN: An Experiment in Artificial Intelligence and Legal Reasoning. *Harvard Law Review* 90(5): 837–893.

Merkle, R. C. 1987. A Digital Signature Based on a Conventional Encryption Function. In *Advances in Cryptology — CRYPTO '87,* LNCS 293, 369–378. Berlin: Springer.

North, D. 2006. Introducing BDD. *Better Software Magazine,* March 2006.

Ouyang, L.; Wu, J.; Jiang, X.; Almeida, D.; Wainwright, C. L.; Mishkin, P.; Zhang, C.; et al. 2022. Training Language Models to Follow Instructions with Human Feedback. In *Advances in Neural Information Processing Systems 35 (NeurIPS 2022).*

Rissland, E. L.; and Ashley, K. D. 1987. A Case-Based System for Trade Secrets Law. In *Proceedings of the 1st International Conference on Artificial Intelligence and Law (ICAIL '87),* 60–66.

Russell, S. 2019. *Human Compatible: Artificial Intelligence and the Problem of Control.* New York: Viking.

Suchman, L. A. 1987. *Plans and Situated Actions: The Problem of Human-Machine Communication.* Cambridge: Cambridge University Press.

Torres-Arias, S.; Afzali, H.; Kuppusamy, T. K.; Curtmola, R.; and Cappos, J. 2019. in-toto: Providing Farm-to-Table Guarantees for Bits and Bytes. In *Proceedings of the 28th USENIX Security Symposium,* 1393–1410.

Wynne, M.; and Hellesøy, A. 2012. *The Cucumber Book: Behaviour-Driven Development for Testers and Developers.* Raleigh, NC: Pragmatic Bookshelf.

[CITATION NEEDED: SLSA framework v1.0 specification, slsa.dev]

[CITATION NEEDED: Aleven and Ashley, CATO system, mid-1990s ICAIL or AI-and-Law journal references]

[CITATION NEEDED: representative reference on operator-log auditability and structured logs in process industries — possibly IEEE Trans. Industrial Informatics or similar]

[CITATION NEEDED: PINK repository URL — to be added on submission]
