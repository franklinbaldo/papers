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

**On the equilibrium-shift mechanism:** When argument-production cost falls, agents whose individual benefit from quality dialogue exceeds the new lower cost switch to strategy (α). The first movers are those with the highest individual benefit: procuradores and advocates in high-volume repetitive matters, where a single precedent revision generates impact across many cases. As more agents adopt (α), the volume of quality arguments reaching the STF via reclamação increases. This creates two effects: (1) the volume effect — the STF faces more quality arguments that cannot be ignored without reputational cost; (2) the visibility effect — ignored quality arguments become more visible to academia, legal press, and the CNJ, increasing the reputational cost of non-engagement. Beyond a critical threshold, the STF's rational choice shifts from (β) to (α).

**On the differential-reduction premise:** The paper acknowledges (§5.4) that the equilibrium-shift mechanism requires cost reduction to be differentially larger for quality arguments than for poor ones — "a reasonable hypothesis for tools incorporating explicit argument structure, but not guaranteed." The paper's strongest response to this is that tools with explicit structural scaffolding (formal verification systems, structured-reasoning models) reduce the costs of the auditable, precisely-structured argument disproportionately relative to the costs of mere text generation — because the structure is the specific thing these tools provide.

**On the limits:** The paper correctly identifies three limits (§5.4): compressibility (not all argument components are compressible), quality-mean (STF may triage more aggressively), and substitution (equilibrium may move to a new level rather than resolving). These are presented as qualifications that do not defeat the central prediction.

---

## 3. The Attack

### 3.1 The Endogenous Threshold Problem: The Quality-Mean Limit Is the Primary Dynamic, Not a Qualification

The paper treats the "quality-mean limit" (§5.4) as a marginal qualification: "o STF pode racionalmente optar por triar mais agressivamente — o que pode manter ou até reforçar o equilíbrio (β, β) para argumentos de qualidade média, mesmo que mude para argumentos de qualidade excepcional." This framing — the limit applies to "average-quality" arguments, not to "exceptional-quality" ones — treats threshold adjustment as a second-order effect that doesn't touch the argument's core.

The framing is mistaken. Threshold adjustment is not a second-order qualification but the primary rational response of any resource-constrained institution facing volume increase. Consider the structure of the problem.

The STF currently engages a certain fraction *f* of arguments that reach it above the current engagement threshold *τ*. When argument-production costs fall, more arguments are produced, some of which cross *τ*. The STF now faces a higher volume of threshold-crossing arguments. Its options are: (a) engage all of them (increasing total engagement cost proportionally to volume); or (b) raise *τ* to maintain roughly constant engagement cost. The paper's inflection-point argument requires option (a) to be forced on the STF — that the volume of crossing arguments eventually makes the reputational cost of non-engagement exceed the cost of engagement. But option (b) is available to the STF as long as it has discretion over its own engagement threshold, which it currently exercises through the plenário virtual mechanism.

Under option (b), the STF's response to rising argument volume is to raise *τ* in proportion to volume increase, maintaining approximately constant engagement across quality levels. The critical mass of arguments that would trigger the inflection point is never reached, because each increment of volume is absorbed by threshold adjustment. The equilibrium does not shift to (α, α); it shifts to a new (β', β') where (β') is defined by a higher absolute level of argument production meeting a proportionally higher engagement threshold. This is the substitution limit the paper itself names in §5.4 — but described there as "moving the equilibrium to another level," which understates the problem. Moving to (β', β') is not progress; it is maintaining the same systemic dysfunction at higher resource expenditure.

The crucial question the paper does not address is: why would the STF choose option (a) rather than option (b)? The paper implicitly assumes the STF's engagement threshold is fixed — that above a certain quality level, arguments cannot be ignored without reputational cost regardless of volume. But the threshold is not exogenous to the system; it is a choice variable for the STF. A court with plenário virtual can set the engagement bar where it finds the best balance of engagement cost and reputational cost, and can adjust that bar as conditions change.

The only mechanism that would prevent threshold adjustment is a monitoring system that imposes costs specifically when above-threshold arguments are not engaged — a system that can distinguish between "the argument crossed the old threshold but the STF raised the bar to avoid it" and "the argument genuinely didn't warrant engagement." No such system is described in the paper, and there is no institutional actor with both the capability and incentives to perform this discrimination. This is the structural gap in the inflection-point prediction.

### 3.2 The Reputational Cost Mechanism Is Contradicted by the Evidence the Paper Itself Relies On

The "visibility effect" (§4.2) requires the following causal chain: quality arguments that the STF ignores → visible to academia, legal press, CNJ → reputational cost imposed on STF → STF shifts strategy. The paper's central prediction depends on this chain being operative.

The same paper that predicts this chain produces empirical evidence against it. Paper 1D in this repository (`paper1D_vinculacao_racional_dialogo_institucional.md`) — which Paper 1E's §1 presupposes as the descriptive background for "o ciclo de diálogo racional que o CPC 2015 pressupõe raramente se materializa" — documents years of STF plenário virtual practice in reclamação proceedings producing brief, non-engaging judgments. This practice has been the object of sustained Brazilian academic criticism, including by Mitidiero, Marinoni, and Mendes — precisely the academia the visibility-effect mechanism invokes. The practice has not changed.

The visibility effect therefore has a tracked record. Quality departure arguments that the STF ignores have been visible to academia and criticized as legally inadequate for years. This criticism has not moved the STF toward engagement. The paper offers no account of why a higher volume of similarly-quality arguments, made visible by the same mechanisms, would generate different outcomes than the sustained academic criticism of the practice already has not generated.

The paper might respond that academic criticism of the *practice* is different from individual quality arguments crossing the *threshold* — that the visibility mechanism operates at the level of specific arguments rather than systemic practices. But this distinction weakens rather than strengthens the paper's position. If academic criticism of the systemic practice has been ineffective, the visibility mechanism for individual arguments is less likely to work, not more — it requires case-specific monitoring of the STF's engagement decisions by actors (the legal press, CNJ) who lack both the incentive and analytical capacity to evaluate whether specific arguments deserved engagement.

The CNJ's oversight extends to procedural compliance, not to the quality of legal reasoning. Article 103-B, §4º, CF grants the CNJ authority over administrative, financial, and disciplinary control of the judiciary — not over the substantive reasoning quality of decisions. The CNJ cannot impose costs on the STF for failing to engage quality arguments; the STF is not subject to CNJ oversight by operation of art. 103-B, §4º, III CF (the CNJ's jurisdiction covers judiciaries subject to its control, not the STF itself). The paper names the CNJ as a visibility mechanism without noting this structural limit.

### 3.3 The Differential Cost-Reduction Premise Lacks Support and Has Structural Reasons to Fail

The equilibrium-shift argument requires not merely that argument-production costs fall but that the reduction is differentially larger for quality arguments. The paper acknowledges this in §5.4 and calls it "reasonable for tools incorporating explicit argument structure, but not guaranteed." This acknowledgment understates the problem.

The distinction between quality-argument production and poor-argument production maps onto a distinction between *substantive analytical work* and *textual production work*. Quality in legal reasoning is primarily substantive: correctly identifying the ratio of a precedent, marshaling facts that genuinely track the ratio's normatively significant features, and constructing the logical structure that connects those facts to the distinction or supersession conclusion. These are analytical tasks that depend on the reasoner's understanding of the law, not on the reasoner's text-production speed.

The technological tools the paper invokes — language models, formal verification systems — reduce *text-production costs* substantially. They reduce *analytical costs* to a lesser and less certain degree. A language model can generate a structured argument at low cost regardless of whether the argument is analytically correct; the structure is a feature of the output, not an indicator of the reasoning's validity. "Auditable argument" (the paper's term for the quality-argument output of formal verification tools) means the argument's structure can be machine-checked for internal consistency — not that the argument's premises are correct or that the legal analysis is sound.

This creates an important asymmetry in the direction opposite to what the paper requires. The cost of producing a *formally structured argument with wrong premises or incorrect legal analysis* falls substantially — because structure is what tools provide. The cost of producing a *formally structured argument with correct analysis* falls less — because analytical correctness depends on a cognitive contribution that tools assist but do not replace. If this asymmetry holds, cost reduction improves the production of formally structured but substantively unreliable arguments disproportionately, increasing the STF's noise problem without proportionally improving signal quality.

The paper's hypothesis — that tools incorporating explicit argument structure reduce quality costs differentially — holds only for the narrow class of arguments where the argument's correctness is fully computable from the existing legal materials. For arguments that require original judgment about ratio identification, fact-feature mapping, and scope of prior decisions, the analytical contribution is not computable and tools provide limited reduction in analytical cost.

This is not merely a "limit" in the sense of a marginal exception; it is likely the description of the majority of arguments in the reclamação context, where the contested questions are precisely the scope and correct application of precedents — substantive questions that require legal judgment, not formal computation.

### 3.4 The Game Model Treats the STF as a Unitary Rational Actor That It Is Not

The game model (§2.1) posits two players: "o STF" with strategies (α) and (β), and "os órgãos inferiores" with strategies (α) and (β). This 2×2 structure is analytically tractable. It does not accurately represent the STF's decision-making structure.

The STF is a plural court with eleven justices, a rapporteur system for case assignment, and a plenário virtual procedure that operates with limited inter-justice deliberation on high-volume cases. Crucially, the decision to engage or not engage an inferior court's departure reasoning in a reclamação judgment is made by the rapporteur, not by the full court. The rapporteur determines whether the matter warrants monocratic or virtual plenário processing; if virtual plenário, whether to produce an engagement-type opinion; and, in practice, what the opinion's substantive scope is. The eleven justices are agents with heterogeneous preferences, caseloads, and institutional positions.

The game model's prediction — that "the STF" will have incentive to shift strategies when reputational costs exceed engagement costs — requires reputational costs to be borne in a concentrated way by the institution. But reputational costs from non-engagement with inferior-court departure reasoning are diffuse across eleven justices and concentrated in none. No individual justice bears the full institutional reputational cost of the rapporteur's decision to process a reclamação without engaging departure reasons. The incentive structure that the game model predicts operates at the institutional level; the decision-making authority that determines engagement operates at the individual-justice level. This gap between where costs are felt and where decisions are made is not a minor modelling detail; it is a structural feature of Brazil's reclamação system that prevents the reputational-cost mechanism from operating at the relevant decision node.

---

## 4. Anticipated Reply and Why It Does Not Suffice

### 4.1 The "Structural Tendency" Reply

The paper might respond that the attack conflates the absence of certainty about the inflection point with the absence of the structural tendency. Even if the threshold adjusts and the reputational mechanism is imperfect, the structural forces described — lower costs, more quality arguments, higher visibility — pull the equilibrium in the right direction. The prediction is probabilistic, not deterministic (§4.4).

This reply does not resolve the attack. The attack's core is that the endogenous threshold adjustment converts the directional pressure into a null effect: higher volume → higher threshold → constant fraction engaged. If the threshold adjusts proportionally, the equilibrium remains stable at (β, β) even as absolute argument production increases. A structural tendency that is exactly offset by a countervailing structural tendency — threshold adjustment — does not produce the directional change the paper predicts. The paper needs to show why threshold adjustment would not offset volume increase, and it does not.

### 4.2 The "Exceptional Arguments" Reply

The paper's §5.4 suggests the quality-mean limit may not apply to "exceptional quality" arguments — those above the new elevated threshold. Perhaps cost reduction, even if it doesn't shift average-quality engagement, makes it possible for more agents to produce the exceptional-quality arguments that would survive threshold adjustment.

This reply concedes the main prediction. The paper's claim (§4.3) is not that exceptional-quality arguments will occasionally reach the STF's attention; it is that an inflection point exists at which the STF's rational strategy shifts to (α) across cases. A narrowed claim — "more exceptional arguments will be produced and some will succeed" — does not generate the systemic equilibrium shift the paper predicts. It predicts occasional victories for high-investment litigants, which is compatible with the system remaining in (β, β) for average cases. The paper's §5.3 explicitly argues for democratization of access — the mechanism is supposed to operate for the broader population of litigants, not only for those who can still produce exceptional arguments at the new elevated cost.

### 4.3 The "Long-Run Dynamics" Reply

The STF's reputational-cost resistance may be a short-run institutional inertia that cost reduction will overcome in the long run. As the volume of quality arguments rises over years, the pattern of non-engagement becomes increasingly untenable.

This reply relies on a mechanism the paper has not established. Long-run institutional change through accumulation of reputational costs requires that each non-engagement event compounds into a reputational stock that eventually forces strategic change. But if each non-engagement event generates minimal individual reputational cost (because monitoring is diffuse) and the STF has threshold-adjustment capacity, there is no clear compounding mechanism. The long-run forecast requires more than the assertion that "eventually the pattern will become untenable" — it requires identifying what institutional actor, with what incentives and capacities, would impose the costs that force the change.

---

## 5. Scope of the Attack

This attack targets:

- **The equilibrium-shift prediction** (§4.2–4.3): that technological cost reduction will create an inflection point driving the system from (β, β) toward (α, α). The endogenous threshold problem (§3.1), the reputational mechanism's empirical track record (§3.2), and the differential cost-reduction premise (§3.3) together undermine this prediction.

This attack does not contest:

- **The diagnosis of the current equilibrium** (§2.1–2.3): The paper's characterization of the (β, β) Nash equilibrium as the current state, its description of the incentive structure that maintains it, and the observation that temas repetitivos amplify the dysfunction are all well-founded. The diagnosis is accurate; the prediction from that diagnosis is contested.
- **The cost-reduction trend** (§4.1): Argument-production costs are falling. The directional claim is not in dispute; only the claim that this reduction creates the specific systemic effect the paper predicts.
- **The distinction between súmula vinculante and temas repetitivos** (§3.1–3.3): The observation that temas repetitivos were designed for volume management rather than ratio robustness, and that this creates higher distinguishing costs, is well-grounded in the CPC 2015's design logic.
- **The access-to-justice observation** (§5.3): The distributive consequence of cost reduction — that lower production costs reduce barriers for less-resourced litigants — is correct independent of whether the equilibrium-shift prediction holds. Democratized access to quality argument production is a real benefit even if it doesn't produce the systemic equilibrium shift the paper predicts.

---

## 6. Surrender Conditions

The attack would not hold under the following conditions.

1. **Empirical evidence that the engagement fraction is stable or increasing despite argument volume growth.** If data from the STF's reclamação docket shows that as quality-argument volume increases, the proportion of substantively engaged responses does not fall (i.e., the threshold is not adjusting proportionally), the endogenous threshold problem would not be operative in the relevant domain. The paper makes a prediction susceptible to empirical test; if the test shows the predicted effect, the adversarial argument is answered by evidence.

2. **A mechanism constraining threshold adjustment is identified.** If a constitutional, statutory, or institutional mechanism prevents the STF from raising its engagement threshold proportionally to volume increase — for example, a procedural rule requiring substantive engagement with all departure reasons meeting a specified formal quality bar — the endogenous threshold problem would be blocked by the mechanism's operation. The paper does not identify such a mechanism; one might exist.

3. **The reputational-cost mechanism is grounded in an actor with the capacity and incentive to impose it.** If an institutional actor with oversight authority over the STF's reasoning quality (not just procedural compliance) is identified — with the capacity to evaluate whether specific arguments warranted engagement and the incentive to impose costs when they didn't — the reputational mechanism could operate. This would require identifying an actor that the paper's current invocation (academia, legal press, CNJ) does not supply.

4. **Evidence that LLMs or formal verification tools differentially reduce analytical costs.** If tools are shown to reduce the cost of substantively correct legal analysis — ratio identification, fact-feature mapping, scope determination — more than they reduce the cost of formally structured but analytically incorrect argument production, the differential cost-reduction premise would gain empirical support. This is a tractable empirical question about the tools' actual performance in legal reasoning contexts.

5. **The game model is specified for the rapporteur-system structure.** If the paper's game model is extended to account for the rapporteur system — with the engagement decision modeled as a choice by individual justices rather than by a unitary STF — the aggregation problem may be resolvable. A reformulated model showing that individual justices have sufficient incentive to increase engagement even without full institutional coordination would address the pluralactor objection.

---

## References

Baldo, F. S. (2025). Custos Argumentativos e Equilíbrio Institucional: Como a Redução do Custo de Produção de Argumentos Jurídicos Racionaliza o Sistema de Precedentes. `paper1E_custos_argumentativos.md` (this repository).

Baldo, F. S. (2025). Vinculação Racional e Diálogo Institucional: o Dever de Fundamentação como Limite Simétrico no Sistema Brasileiro de Precedentes. `paper1D_vinculacao_racional_dialogo_institucional.md` (this repository).

BRASIL. Constituição da República Federativa do Brasil, 1988. Arts. 102, *caput*; 103-A, §2º; 103-B, §4º.

BRASIL. Lei nº 13.105, de 16 de março de 2015 (Código de Processo Civil). Arts. 489, §1º, IV e VI; 927; 988–993.

AXELROD, Robert. *The evolution of cooperation*. New York: Basic Books, 1984.

HARDIN, Garrett. The tragedy of the commons. *Science*, v. 162, n. 3859, p. 1243–1248, 1968.

MARINONI, Luiz Guilherme. *Precedentes obrigatórios*. 5. ed. São Paulo: Revista dos Tribunais, 2016.

MITIDIERO, Daniel. *Cortes superiores e cortes supremas: do controle à interpretação, da jurisprudência ao precedente*. 3. ed. São Paulo: Revista dos Tribunais, 2017.

OLSON, Mancur. *The logic of collective action: public goods and the theory of groups*. Cambridge: Harvard University Press, 1965.

OSTROM, Elinor. *Governing the commons: the evolution of institutions for collective action*. Cambridge: Cambridge University Press, 1990.

SCHELLING, Thomas C. *The strategy of conflict*. Cambridge: Harvard University Press, 1960.
