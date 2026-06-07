# The Endogenous Threshold Problem: Why Technological Cost Reduction May Not Shift the Argumentative Equilibrium

---

## 1. Thesis Attacked

"Custos Argumentativos e Equilíbrio Institucional: Como a Redução do Custo de Produção de Argumentos Jurídicos Racionaliza o Sistema de Precedentes" (Baldo, 2025; `paper1E_custos_argumentativos.md`) defends a game-theoretic prediction about the Brazilian binding-precedent system:

> "Há um ponto — não definível com precisão, mas estruturalmente necessário — em que o custo de reafirmar autoridade sem enfrentar argumentos supera o benefício de não enfrentar. Nesse ponto, o STF tem incentivo para mudar a estratégia: enfrentar os melhores argumentos, distinguir quando a distinção é genuína, revisar quando o argumento revela erro real." (§4.3)

The paper's central prediction is that technological reduction in argument-production costs creates a structural inflection point at which the STF's reputational cost of non-engagement exceeds the cost of engagement, driving the system from its current low-quality equilibrium (β, β) toward the rational-dialogue equilibrium (α, α) the CPC 2015 presupposes. The argument is framed as independent of any specific technology and dependent only on two stable claims: (1) argument-production costs are falling structurally; and (2) the system's incentive structure is stable. This attack targets the equilibrium-shift prediction — the move from cost reduction to the inflection point to (α, α).

---

## 2. Faithful Reconstruction

The paper's argument is strongest when integrated with its game-theoretic premises and its own acknowledged limits.

**On the current equilibrium:** The binding-precedent system is characterized by a Nash equilibrium at (β, β): the STF creates precedents optimized for volume management without ratio robustness; inferior courts apply or ignore mechanically without the reasoned engagement art. 489, §1º requires. This equilibrium is stable because each agent's individual payoff from switching to strategy (α) is negative when the other remains at (β). The diagnosis is correct and well-grounded.

**On the cost-reduction mechanism:** Three components of argument-production cost are each in structural decline: research cost (legal databases, semantic indexing), articulation cost (language models that assist structured argument production), and audit cost (formal verification tools). The aggregate trend is downward.

**On the equilibrium-shift mechanism:** When argument-production costs fall, agents whose individual benefit from quality dialogue exceeds the new lower cost switch to strategy (α). The first movers are those with the highest individual benefit: procuradores and advocates in high-volume repetitive matters, where a single precedent revision generates impact across many cases. As more agents adopt (α), the volume of quality arguments reaching the STF via reclamação increases. This creates two effects: (1) the volume effect — the STF faces more quality arguments that cannot be ignored without reputational cost; (2) the visibility effect — ignored quality arguments become more visible to academia, legal press, and the CNJ, increasing the reputational cost of non-engagement. Beyond a critical threshold, the STF's rational choice shifts from (β) to (α).

**On the differential-reduction premise:** The paper acknowledges (§5.4) that the equilibrium-shift mechanism requires cost reduction to be differentially larger for quality arguments than for poor ones — "a reasonable hypothesis for tools incorporating explicit argument structure, but not guaranteed." The paper's strongest response to this is that tools with explicit structural scaffolding (formal verification systems, structured-reasoning models) reduce the costs of the auditable, precisely-structured argument disproportionately relative to the costs of mere text generation — because the structure is the specific thing these tools provide.

**On the limits:** The paper correctly identifies three limits (§5.4): compressibility (not all argument components are compressible), quality-mean (STF may triage more aggressively), and substitution (equilibrium may move to a new level rather than resolving). These are presented as qualifications that do not defeat the central prediction.

---

## 3. The Attack

### 3.1 The Endogenous Threshold Problem — Threshold Adjustment Is Self-Assessed, Not Externally Constrained

The paper treats the "quality-mean limit" (§5.4) as a marginal qualification: "o STF pode racionalmente optar por triar mais agressivamente — o que pode manter ou até reforçar o equilíbrio (β, β) para argumentos de qualidade média, mesmo que mude para argumentos de qualidade excepcional." This framing — the limit applies to "average-quality" arguments, not to "exceptional-quality" ones — treats threshold adjustment as a second-order effect that doesn't touch the argument's core.

The framing is mistaken. Threshold adjustment is not a second-order qualification but the primary rational response of any resource-constrained institution facing volume increase. Consider the structure of the problem.

The STF currently engages a certain fraction *f* of arguments that reach it above the current engagement threshold *τ*. When argument-production costs fall, more arguments are produced, some of which cross *τ*. The STF now faces a higher volume of threshold-crossing arguments. Its options are: (a) engage all of them (increasing total engagement cost proportionally to volume); or (b) raise *τ* to maintain roughly constant engagement cost. The paper's inflection-point argument requires option (a) to be forced on the STF — that the volume of crossing arguments eventually makes the reputational cost of non-engagement exceed the cost of engagement. But option (b) is available to the STF as long as it has discretion over its own engagement threshold, which it currently exercises through the plenário virtual mechanism.

Under option (b), the STF's response to rising argument volume is to raise *τ* in proportion to volume increase, maintaining approximately constant engagement across quality levels. The critical mass of arguments that would trigger the inflection point is never reached, because each increment of volume is absorbed by threshold adjustment. The equilibrium does not shift to (α, α); it shifts to a new (β', β') where (β') is defined by a higher absolute level of argument production meeting a proportionally higher engagement threshold. This is the substitution limit the paper itself names in §5.4 — but described there as "moving the equilibrium to another level," which understates the problem. Moving to (β', β') is not progress; it is maintaining the same systemic dysfunction at higher resource expenditure.

The crucial question the paper does not address is: why would the STF choose option (a) rather than option (b)? The paper implicitly assumes the STF's engagement threshold is fixed — that above a certain quality level, arguments cannot be ignored without reputational cost regardless of volume. But the threshold is not exogenous to the system; it is a choice variable for the STF. A court with plenário virtual can set the engagement bar where it finds the best balance of engagement cost and reputational cost, and can adjust that bar as conditions change.

The only mechanism that would prevent threshold adjustment is a monitoring system that imposes costs specifically when above-threshold arguments are not engaged — a system that can distinguish between "the argument crossed the old threshold but the STF raised the bar to avoid it" and "the argument genuinely didn't warrant engagement." No such system is described in the paper, and there is no institutional actor with both the capability and incentives to perform this discrimination. This is the structural gap in the inflection-point prediction.

The strongest current response to this argument holds that threshold adjustment is not cost-free because the CPC 2015's procedural architecture imposes reasoning requirements that scale with argument quality. A reclamação arguing with formal structure and explicit ratio identification generates, on this view, a dismissal obligation that must proportionally engage the argument's structure to satisfy art. 93, IX CF; any dismissal that does not acknowledge the structured argument's ratio-identification component is vulnerable to embargos de declaração for omissão under art. 1022, II CPC. This argument correctly identifies that formal procedural architecture exists and that reasoning adequacy requirements are real.

The argument fails to identify an external enforcement mechanism. The STF is Brazil's final court; no superior tribunal reviews the STF's own embargos de declaração responses for reasoning adequacy. When the STF determines that a prior reclamação dismissal contained "no omissão, contradição ou obscuridade" — the standard embargos response — this determination is authoritative and unreviewable. The institution with concentrated incentive to minimize engagement cost is the same institution that determines whether its prior engagement was adequate. This is the structural condition under which self-assessed constraints are least reliable as external checks on institutional behavior.

The established pattern in reclamação proceedings confirms that this structural condition produces the expected outcome. The same scholars who document non-engagement with departure reasoning — Mitidiero, Marinoni — document that the embargos route in this context produces systematically brief, deferential responses from the STF. The procedural architecture's reasoning requirements are applied deferentially by the STF to its own prior decisions. For the procedural-cost argument to hold, the STF would need to self-assess its own embargos responses as inadequate — an outcome structurally unavailable to the institution as currently constituted. The constitutional reasoning requirement is real; its enforcement against the STF's own decisions depends on the STF.

### 3.2 The Reputational Cost Mechanism — Individual Monitoring Does Not Solve the Pattern Formation Problem

The "visibility effect" (§4.2) requires the following causal chain: quality arguments that the STF ignores → visible to academia, legal press, CNJ → reputational cost imposed on STF → STF shifts strategy. The paper's central prediction depends on this chain being operative.

The same paper that predicts this chain produces empirical evidence against it. Paper 1D in this repository (`paper1D_vinculacao_racional_dialogo_institucional.md`) — which Paper 1E's §1 presupposes as the descriptive background for "o ciclo de diálogo racional que o CPC 2015 pressupõe raramente se materializa" — documents years of STF plenário virtual practice in reclamação proceedings producing brief, non-engaging judgments. This practice has been the object of sustained Brazilian academic criticism, including by Mitidiero, Marinoni, and Mendes — precisely the academia the visibility-effect mechanism invokes. The practice has not changed.

The paper might respond that academic criticism of the *practice* is different from individual quality arguments crossing the *threshold* — that the visibility mechanism operates at the level of specific arguments rather than systemic practices. This distinction is structurally accurate. The party whose formally structured quality argument was dismissed in a specific reclamação proceeding has concentrated incentive to document and publicize that non-engagement; counsel has professional standing to articulate why the STF's response was inadequate; academic supporters have specific material to analyze. The individual party is a more capable monitor of their specific case than diffuse academic observers of the system.

The distinction relocates rather than resolves the adversarial problem, however. The equilibrium-shift prediction (§4.3) requires not that individual parties document their own non-engagement events, but that visible patterns of non-engagement across cases impose institutional reputational costs large enough to shift the STF's strategy. The production of visible patterns from individual cases requires actors who compile, analyze, and publicize non-engagement across many parties — a function distinct from single-case documentation. The actors best positioned to perform pattern compilation are academics and the legal press — the same actors correctly characterized as lacking the concentrated per-case incentive and specific analytical access that party monitors possess. Party-level monitors produce the individual data points; diffuse monitors perform the aggregation into visible patterns. Neither class can perform both functions.

This division reflects the same collective action structure the paper identifies in §2.2 for inferior courts. Each party has strong individual incentive to document their own non-engagement event; no party has incentive to compile other parties' non-engagement events into a publicly visible pattern. The incentive to compile is concentrated in diffuse actors who lack case-specific access and per-case motivation. The result is a structural gap between individual documentation (tractable by party monitors) and pattern formation (not tractable by any identified actor) that the individual-monitoring distinction does not resolve.

The historical evidence supports this reading. The academic criticism that has been documented and sustained — by scholars who track reclamação jurisprudence systematically — represents exactly the pattern-formation function the mechanism requires: individual cases compiled into a visible pattern of non-engagement. This is not the diffuse "practice criticism" the party-monitoring distinction is designed to distinguish from. It is the targeted, specific, expert analysis of individual decisions aggregated into a pattern. That this targeted pattern-based criticism has not produced behavioral change is the best available evidence that the mechanism's cost-imposition chain does not operate at the intensity the equilibrium-shift prediction requires.

The CNJ's oversight extends to procedural compliance, not to the quality of legal reasoning. Article 103-B, §4º, CF grants the CNJ authority over administrative, financial, and disciplinary control of the judiciary — not over the substantive reasoning quality of decisions. The CNJ cannot impose costs on the STF for failing to engage quality arguments; the STF is not subject to CNJ oversight by operation of art. 103-B, §4º, III CF (the CNJ's jurisdiction covers judiciaries subject to its control, not the STF itself). The paper names the CNJ as a visibility mechanism without noting this structural limit.

### 3.3 The Differential Cost-Reduction Premise — The Narrowed Mechanism Is Insufficient for the Systemic Prediction

The equilibrium-shift argument requires not merely that argument-production costs fall but that the reduction is differentially larger for quality arguments. The paper acknowledges this in §5.4 and calls it "reasonable for tools incorporating explicit argument structure, but not guaranteed."

The distinction between quality-argument production and poor-argument production maps onto a distinction between *substantive analytical work* and *textual production work*. Quality in legal reasoning is primarily substantive: correctly identifying the ratio of a precedent, marshaling facts that genuinely track the ratio's normatively significant features, and constructing the logical structure that connects those facts to the distinction or supersession conclusion. These are analytical tasks that depend on the reasoner's understanding of the law, not on the reasoner's text-production speed.

The technological tools the paper invokes — language models, formal verification systems — reduce *text-production costs* substantially. They reduce *analytical costs* to a lesser and less certain degree. A language model can generate a structured argument at low cost regardless of whether the argument is analytically correct; the structure is a feature of the output, not an indicator of the reasoning's validity. "Auditable argument" (the paper's term for the quality-argument output of formal verification tools) means the argument's structure can be machine-checked for internal consistency — not that the argument's premises are correct or that the legal analysis is sound.

The strongest response to this argument identifies a real narrowing: the mechanism operates primarily for a specific class of practitioners — those who have the analytical capacity to correctly identify the ratio but previously lacked resources for the structural elaboration that makes the argument formally assessable. For this marginal class, tools reduce the elaboration cost component without substituting for analytical capacity. The analytical work — ratio identification, fact-feature mapping, scope determination — remains a practitioner contribution; the structural elaboration that produces the auditable format is what tools assist. Cost reduction for this class is differentially larger for quality arguments because the analytical component is already present.

This narrowing identifies a real class, but it creates a proportionality problem for Paper 1E's systemic prediction. Paper 1E predicts an institutional strategy change at the STF level — a change in how the STF processes reclamações across the board, including the systemic democratization of access described in §5.3. For institutional strategy change to occur under the narrowed mechanism, the marginal class of capable-but-resource-constrained practitioners must generate a volume of quality arguments large enough to impose inflection-point costs on the STF — and the quality-argument volume from this class must outpace the noise from formally structured but analytically incorrect arguments that the same cost reduction enables. Both conditions remain empirically unresolved. The narrowing names necessary conditions for the prediction without establishing them.

The asymmetry in the wrong direction is not eliminated by the narrowing; it is relocated to the question of class size. If the majority of the additional argument volume generated by cost reduction comes from practitioners who lack the analytical capacity to correctly identify the ratio — and who use the same structural tools to produce formally convincing but substantively incorrect arguments — the noise problem dominates. Whether the capable-but-resource-constrained class is large enough to generate sufficient quality-argument volume to reach the inflection point before the noise floor rises proportionally is a quantitative empirical question that the current theoretical framework cannot resolve.

### 3.4 The Game Model Misspecifies the STF — Attribution Timing and Panel-Level Diffusion

The game model (§2.1) posits two players: "o STF" with strategies (α) and (β), and "os órgãos inferiores" with strategies (α) and (β). This 2×2 structure is analytically tractable. It does not accurately represent the STF's decision-making structure.

The STF is a plural court with eleven justices, a rapporteur system for case assignment, and a plenário virtual procedure that operates with limited inter-justice deliberation on high-volume cases. Crucially, the decision to engage or not engage an inferior court's departure reasoning in a reclamação judgment is made by the rapporteur, not by the full court. The rapporteur determines whether the matter warrants monocratic or virtual plenário processing; if virtual plenário, whether to produce an engagement-type opinion; and, in practice, what the opinion's substantive scope is. The eleven justices are agents with heterogeneous preferences, caseloads, and institutional positions.

The game model's prediction — that "the STF" will have incentive to shift strategies when reputational costs exceed engagement costs — requires reputational costs to be borne in a concentrated way by the institution. But reputational costs from non-engagement with inferior-court departure reasoning are diffuse across eleven justices and concentrated in none. No individual justice bears the full institutional reputational cost of the rapporteur's decision to process a reclamação without engaging departure reasons. The incentive structure that the game model predicts operates at the institutional level; the decision-making authority that determines engagement operates at the individual-justice level. This gap between where costs are felt and where decisions are made is not a minor modelling detail; it is a structural feature of Brazil's reclamação system that prevents the reputational-cost mechanism from operating at the relevant decision node.

The strongest response accepts this modeling gap and contests the inference to fully diffuse reputational costs. Brazilian STF justices are individually attributed in academic scholarship and bar-community assessment; processual monographs track individual justices' handling of specific doctrinal questions; the processual-law community is small enough for individual-level tracking to be feasible. This is accurate. Individual attribution in the academic literature is not contested.

Two considerations prevent individual attribution from closing the adversarial argument.

The first is the attribution timing gap. Academic processual scholarship operates on publication timescales that substantially postdate the engagement decisions they assess. Monographs, doctrinal articles, and law review pieces analyzing individual justices' reclamação jurisprudence appear months to years after the decisions they examine. For anticipated reputational costs to change engagement decisions within the plenário virtual cycle — where individual cases are processed on timescales of days to weeks — a rapporteur would need to anticipate prospectively that a specific case will attract scholarly attention, that the scholarship will produce adverse attribution, and that the adverse attribution will generate career costs sufficient to outweigh the engagement cost for that case. This prospective cost chain is attenuated by three factors: the low prior probability that any specific reclamação case attracts subsequent scholarly attention; temporal discounting over the months-to-years publication lag; and the diffusion of adverse attribution across the many cases each justice processes annually in high-volume plenário virtual proceedings. Retrospective scholarly attribution of the kind documented in the academic literature does not function as prospective engagement incentive at the decision node.

The second consideration is panel-attribution scope within the plenário virtual. Rapporteurs produce the reasoned opinion; the remaining justices register agreement or disagreement, typically without independent reasoning. Even if the rapporteur is individually attributed for the analytical quality of the opinion, the panel members who tacitly concurred in plenário virtual proceedings are attributed at a coarser level — to the outcome, not to the specific reasoning quality. Brazilian processual scholarship that tracks individual justices' doctrinal positions focuses disproportionately on authored opinions and explicit analytical positions; tacit concurrences in high-volume processing receive less individual analytical scrutiny. The individual attribution pressure is concentrated on the rapporteur, attenuated for concurring panel members, and absent for justices whose only visible act is a vote.

---

## 4. The Supportive Defense and Why It Does Not Suffice

### 4.1 The Procedural-Cost Reply

The defense argues that threshold adjustment is not cost-free because the CPC 2015's procedural architecture requires dismissal reasoning to scale with argument quality. Arts. 93, IX CF and 1022, II CPC create formal adequacy requirements — a formally structured reclamação cannot be dismissed without reasoning sufficient to survive an embargos de declaração challenge on omissão grounds; as argument quality rises, the minimum adequate dismissal must proportionally engage the argument's structure.

This reply correctly identifies the procedural architecture; it identifies the wrong enforcement mechanism. There is no external actor who reviews the STF's own embargos de declaração responses for adequacy. The STF self-assesses whether its prior reclamação dismissals were complete; this self-assessment is the determination that "não há omissão." A procedural constraint self-assessed by the constrained institution — the institution with concentrated incentive to minimize engagement cost — is not an external check. The established pattern in reclamação proceedings confirms this: the STF consistently applies a deferential standard to its own prior decisions' reasoning adequacy through brief embargos responses, documented in the same academic literature the defense invokes. The procedural-cost reply names a formal constraint without identifying the external enforcement mechanism that would make the constraint binding against the STF's own engagement interests.

### 4.2 The Party-Monitoring Reply

The defense correctly identifies the party whose quality argument was dismissed as a monitor with concentrated incentive and specific analytical access. This is an accurate and important distinction from diffuse academic observers.

The reply addresses individual-case monitoring; the equilibrium-shift prediction requires pattern-level monitoring. The inflection point described in §4.3 is reached when visible patterns of non-engagement across cases impose institutional reputational costs large enough to change the STF's strategy — not when individual documented cases generate per-case reputational costs. Visible patterns require actors who aggregate individual cases into publicly attributable records. The actors with aggregation capacity are academics and press who, by the defense's own analysis, lack the per-case incentive and specific access of party monitors. The party-monitoring point resolves the single-case documentation problem while leaving the pattern-formation collective action problem structurally intact. The most capable pattern-formers — scholars who track reclamação jurisprudence systematically — have produced exactly the kind of pattern documentation the mechanism requires; it has not produced behavioral change.

### 4.3 The Marginal-Class Reply

The defense accepts the adversarial paper's differential-cost-reduction argument as its structurally strongest point, with a narrowing: the mechanism operates for practitioners with analytical capacity but resource-constrained elaboration. For this class, tools reduce elaboration costs without substituting for analytical capacity.

The narrowing is accepted as identifying a real class. The systemic equilibrium-shift prediction requires this class to be large enough to generate quality-argument volume sufficient to impose inflection-point costs on the STF — and for quality-argument volume from this class to outpace the noise from formally structured but analytically incorrect arguments that the same cost reduction enables for a different class of practitioners. Both conditions remain empirically unresolved by either paper. The marginal-class narrowing names necessary conditions for the prediction without establishing them; it does not rescue the equilibrium-shift claim.

### 4.4 The Individual-Attribution Reply

The defense correctly notes that Brazilian STF justices are individually attributed in academic scholarship and that the processual-law community is small enough for individual-level tracking. This partially addresses the original characterization of reputational costs as fully diffuse.

The attributions are retrospective rather than prospective; the mechanism requires prospective anticipated costs at the decision node. Retrospective scholarly attribution, attenuated by publication lag, selective scholarly attention to individual cases, and temporal discounting over multi-year horizons, does not function as contemporaneous engagement incentive at the plenário virtual decision point. Additionally, the attribution pressure is concentrated on rapporteurs and attenuated for panel members who concur through the plenário virtual mechanism without producing independent authored reasoning. Establishing that the scholarly community attributes individual justices' positions does not establish that this attribution operates at the decision-relevant timescale.

### 4.5 On the "Structural Tendency" Response

The paper (§4.4) frames the prediction as probabilistic — the structural forces described pull the equilibrium in the right direction even if timing and mechanism are uncertain. This framing would survive if the four mechanisms above were individually weak but jointly directional. The adversarial attack is not that (β, β) is certainly permanent; it is that the specific causal chain Paper 1E identifies does not reliably produce the inflection point. A structural tendency that relies on a procedural constraint self-assessed by the constrained institution, an individual-monitoring mechanism that cannot solve the pattern-formation problem, an empirically unresolved class-size condition, and a reputational attribution mechanism temporally mismatched to the decision node, is a weaker claim than the paper makes in §4.3. The inflection point is described as "estruturalmente necessário" — structurally required. The adversarial attack targets that structural necessity claim, not the probabilistic tendency.

---

## 5. Scope of the Attack

This attack targets:

- **The equilibrium-shift prediction** (§4.2–4.3): that technological cost reduction will create an inflection point driving the system from (β, β) toward (α, α). The endogenous threshold problem (§3.1), the pattern-formation gap in the reputational mechanism (§3.2), the narrowed-but-insufficient differential cost-reduction premise (§3.3), and the attribution timing gap in the rapporteur-structure problem (§3.4) together undermine this prediction.

This attack does not contest:

- **The diagnosis of the current equilibrium** (§2.1–2.3): The paper's characterization of the (β, β) Nash equilibrium as the current state, its description of the incentive structure that maintains it, and the observation that temas repetitivos amplify the dysfunction are all well-founded. The diagnosis is accurate; the prediction from that diagnosis is contested.
- **The cost-reduction trend** (§4.1): Argument-production costs are falling. The directional claim is not in dispute; only the claim that this reduction creates the specific systemic effect the paper predicts.
- **The distinction between súmula vinculante and temas repetitivos** (§3.1–3.3): The observation that temas repetitivos were designed for volume management rather than ratio robustness, and that this creates higher distinguishing costs, is well-grounded in the CPC 2015's design logic.
- **The access-to-justice observation** (§5.3): The distributive consequence of cost reduction — that lower production costs reduce barriers for less-resourced litigants — is correct independent of whether the equilibrium-shift prediction holds. Democratized access to quality argument production is a real benefit even if it doesn't produce the systemic equilibrium shift the paper predicts.

---

## 6. Surrender Conditions

The attack would not hold under the following conditions.

1. **Empirical evidence that the engagement fraction is stable or increasing despite argument volume growth.** If data from the STF's reclamação docket shows that as quality-argument volume increases, the proportion of substantively engaged responses does not fall, the endogenous threshold problem would not be operative in the relevant domain. The paper makes a prediction susceptible to empirical test; if the test shows the predicted effect, the adversarial argument is answered by evidence.

2. **A mechanism constraining threshold adjustment is identified that is externally enforced.** If a constitutional, statutory, or institutional mechanism prevents the STF from raising its engagement threshold proportionally to volume increase — and this mechanism is enforced by an external actor with authority over STF engagement adequacy — the endogenous threshold problem would be blocked. The procedural-cost argument identifies a real formal constraint but not an external enforcer; an external enforcement mechanism has not been identified.

3. **An actor with the capacity and incentive to impose reputational costs is identified at the pattern-formation level.** The party whose quality argument was dismissed has been identified as a capable monitor at the individual-case level. This is progress. But the inflection-point mechanism requires visible patterns across many cases to impose institutional costs — a function that requires pattern formation, not only single-case documentation. An actor who aggregates individual documentation into patterns with both the capacity and concentrated incentive to do so systematically has not yet been identified.

4. **Evidence that LLMs or formal verification tools differentially reduce analytical costs for the marginal class at sufficient scale.** The narrowing accepted in §3.3 identifies the relevant class — practitioners with analytical capacity but resource-constrained elaboration. Whether this class is large enough to generate the quality-argument volume the inflection point requires, and whether noise from the broader class of formally-structured-but-analytically-incorrect arguments remains below the threshold, are both tractable empirical questions.

5. **The game model is specified for the rapporteur-system structure with a contemporaneous attribution mechanism.** If the paper's game model is extended to account for the rapporteur system — with engagement decisions modeled at the individual-justice level — and if an attribution mechanism is identified that operates on the decision-relevant timescale (days to weeks) rather than the scholarly-publication timescale (months to years), the aggregation and timing problems may be resolvable.

---

## References

Baldo, F. S. (2025). Custos Argumentativos e Equilíbrio Institucional: Como a Redução do Custo de Produção de Argumentos Jurídicos Racionaliza o Sistema de Precedentes. `paper1E_custos_argumentativos.md` (this repository).

Baldo, F. S. (2025). Vinculação Racional e Diálogo Institucional: o Dever de Fundamentação como Limite Simétrico no Sistema Brasileiro de Precedentes. `paper1D_vinculacao_racional_dialogo_institucional.md` (this repository).

BRASIL. Constituição da República Federativa do Brasil, 1988. Arts. 102, *caput*; 103-A, §2º; 103-B, §4º.

BRASIL. Lei nº 13.105, de 16 de março de 2015 (Código de Processo Civil). Arts. 489, §1º, IV e VI; 927; 988–993; 1022, II.

AXELROD, Robert. *The evolution of cooperation*. New York: Basic Books, 1984.

HARDIN, Garrett. The tragedy of the commons. *Science*, v. 162, n. 3859, p. 1243–1248, 1968.

MARINONI, Luiz Guilherme. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.

MITIDIERO, Daniel. *Cortes superiores e cortes supremas: do controle à interpretação, da jurisprudência ao precedente*. 3. ed. São Paulo: Revista dos Tribunais, 2017.

MENDES, Conrado Hübner. *Constitutional courts and deliberative democracy*. Oxford: Oxford University Press, 2013.

OLSON, Mancur. *The logic of collective action: public goods and the theory of groups*. Cambridge: Harvard University Press, 1965.

OSTROM, Elinor. *Governing the commons: the evolution of institutions for collective action*. Cambridge: Cambridge University Press, 1990.

SCHELLING, Thomas C. *The strategy of conflict*. Cambridge: Harvard University Press, 1960.
