---
type: "Audit Report"
title: "Argumentative costs and precedent equilibrium prior-art audit — 2026-09-18"
description: "Claim-specific, temporally grounded audit of Paper 1E's law-and-economics and AI-cost mechanism, separating pre-cutoff antecedents from later convergences."
tags: [paper1e, prior-art, precedents, law-and-economics, litigation-costs, generative-ai, judicial-hierarchy, brazil]
timestamp: 2026-09-18T00:00:00-04:00
---

# Argumentative costs and precedent equilibrium prior-art audit — 2026-09-18

> **Status:** first claim-specific reproducible prior-art audit of [`paper1E_custos_argumentativos.md`](../../paper1E_custos_argumentativos.md). This audit materially narrows the paper's generic novelty claims. It does **not** establish exhaustive novelty, patent novelty, independent invention, copying, plagiarism, or causal dependence. A negative search result means only that no material antecedent was located in the searched sources and terminology during this run.

## 1. Claims audited and temporal cutoff

Paper 1E contains several claims that must be separated rather than inheriting novelty from the paper as a whole:

- **C1 — private/social incentive divergence:** producing a high-quality legal argument capable of moving precedent imposes a concentrated cost on the producing actor while much of the benefit of better precedent is distributed across the legal system; this can sustain underinvestment in argument quality.
- **C2 — strategic judicial-hierarchy equilibrium:** higher and lower courts interact strategically, and a stable low-effort equilibrium can arise when unilateral investment in higher-quality reasoning is privately costly and the other side is not expected to reciprocate.
- **C3 — technological comparative static:** reducing the cost of legal research, argument construction, drafting, and litigation changes legal actors' behavior and can change the rate or direction of legal evolution.
- **C4 — generative-AI productivity channel:** modern AI can reduce the time/cost of legal work and, with sufficiently capable systems, can sometimes raise measured quality as well as productivity, increasing the feasible volume of legal activity.
- **C5 — Brazil/STF/reclamação feedback loop:** in the Brazilian binding-precedent system, sufficiently cheaper *auditable, high-quality* arguments reaching the STF through reclamação can raise the institutional or reputational cost of non-engagement and thereby move the system away from a `(β,β)` low-effort equilibrium toward reasoned dialogue.
- **C6 — doctrinal coupling:** the mechanism is tied to Brazil's CPC 2015 argumentative duties, distinguishing/superação architecture, and the institutional differences between súmula vinculante and mass-precedent mechanisms.

The paper's broad statements about costs, strategic legal behavior, AI productivity, and legal evolution therefore cannot be treated as a single indivisible contribution. The strongest residual candidate is C5+C6: the *Brazil-specific closed loop* from cheaper auditable argument production, through reclamação and engagement pressure, to a change in precedent practice.

### 1.1 GitHub reconstruction

The current file timestamp is not used as the priority date. The earliest repository commit located for the file is:

- [`3de41c63f429ab2f4f9a1844825be2e9bd78dbf4`](https://github.com/franklinbaldo/papers/commit/3de41c63f429ab2f4f9a1844825be2e9bd78dbf4), **2026-05-13 03:20:27 UTC**, message `Import dogmatic series (paper1, 1C–1G), methodological papers (2, 3), empirical (5), synthesis (6); rewrite README as program index`.

The historical file at that commit already states the core mechanism in both the Portuguese and English abstracts: the existing low-quality equilibrium is maintained by incentive structure; the individual cost of producing sufficiently strong legal argument exceeds the producing actor's expected benefit although the collective benefit is larger; technological reduction in the cost of quality/auditable legal argument changes the game's parameters; more such arguments reach the STF through reclamação; non-engagement becomes institutionally costlier; and the equilibrium is predicted to move toward rational dialogue.

The corresponding public pull request is:

- [`#9`](https://github.com/franklinbaldo/papers/pull/9), created **2026-05-13 03:20:45 UTC**, merged **2026-05-13 03:22:27 UTC**. Its opening description explicitly lists `paper1E_custos_argumentativos.md` among the imported papers.

Because the branch commit precedes the PR by only eighteen seconds and the exact instant at which that branch commit became discoverable to arbitrary third parties is harder to prove than PR creation, this audit uses the conservative public cutoff:

**Cutoff for C1–C6: 2026-05-13 03:20:45 UTC.**

Later June and July edits narrowed the equilibrium-shift prediction, added endogenous-threshold and pattern-formation limits, and acknowledged that AI may reduce textual costs more than analytical costs. Those later qualifications do not move the priority date of the original broad claims; they are revisions of claims that were already public on May 13.

## 2. Search protocol

The search deliberately decomposed the paper rather than searching only its title. Sources consulted included arXiv, NBER, primary journal/publisher pages, SSRN records or public quotations of preprints, Brazilian legal journals, court/institutional materials, and GitHub history.

Representative queries included:

- `"custos argumentativos" precedentes STF teoria dos jogos`
- `"ônus argumentativo" precedentes "teoria dos jogos"`
- `"precedentes vinculantes" "análise econômica" custos litigância Brasil`
- `higher court lower court game theory precedent compliance strategic review`
- `private social incentive litigation costs precedent law economics`
- `litigation cost legal change precedent evolution technology`
- `generative AI litigation cost legal evolution precedent`
- `"AI and the law" litigation cost precedent evolution`
- `generative AI lawyer productivity randomized legal tasks`
- `generative AI litigation volume court burden`
- `AI pro se filings court burden 2026`
- `Brazil AI lawyers more lawsuits courts 2025`
- exact-title, author-name, `Custos Argumentativos`, `Franklin Baldo`, and related-title searches against later candidates.

Historical and modern terminology were both used: `repeat player`, `selection of legal rules`, `private/social incentive to sue`, `principal-agent judiciary`, `strategic defiance`, `cost of litigation`, `legal services productivity`, `access to justice`, `AI-generated filings`, `precedent evolution`, and `institutional dialogue`.

## 3. Pre-cutoff findings

### 3.1 Galanter: resource asymmetry and repeat-player investment in legal rules

**Work:** Marc Galanter, **“Why the ‘Haves’ Come Out Ahead: Speculations on the Limits of Legal Change”**, *Law & Society Review* 9(1), 1974. DOI: `10.2307/3053023`.

Primary record: <https://doi.org/10.2307/3053023>

**First public date used:** 1974 publication lineage (the paper also notes an earlier working-paper version and a 1973 conference version).

**Compared claims:** C1, adjacent to C3.

**Classification:** `prior_art` for the generic proposition that differential resources and repeat-player capacity shape strategic use of litigation and rule development; `partial_prior_art` for Paper 1E's specific private-cost/social-benefit mechanism.

Galanter's structural account long predates Paper 1E's premise that legal-system outcomes depend on actors' capacity to invest repeatedly in litigation and rule formation. It does not model STF/reclamação, LLM-driven cost reduction, or a bilateral low-effort equilibrium.

### 3.2 Landes & Posner: precedent as costly capital formation

**Work:** William M. Landes & Richard A. Posner, **“Legal Precedent: A Theoretical and Empirical Analysis”**, NBER Working Paper 0146, August 1976; *Journal of Law and Economics* 19(2), 1976. DOI: `10.3386/w0146` / `10.1086/466868`.

Primary record: <https://www.nber.org/papers/w0146>

**First public date used:** August 1976 NBER issue date.

**Compared claims:** C1, C3.

**Classification:** `partial_prior_art`.

Landes and Posner explicitly model the stock of legal precedent as capital yielding information services and describe new/replacement precedent as being created by investment in the production of precedents. This occupies a substantial part of the generic idea that improving/changing precedent requires costly investment and that legal rules respond to the economics of producing precedent.

### 3.3 Rubin and Priest: litigation incentives can drive legal-rule evolution

**Works:**

- Paul H. Rubin, **“Why Is the Common Law Efficient?”**, *Journal of Legal Studies* 6(1), **1977-01-01**, DOI `10.1086/467562`.
- George L. Priest, **“The Common Law Process and the Selection of Efficient Rules”**, *Journal of Legal Studies* 6(1), 1977, DOI `10.1086/467563`.

Primary record for Rubin: <https://www.journals.uchicago.edu/doi/abs/10.1086/467562>

**Compared claims:** C1, C3.

**Classification:** `partial_prior_art`; the generic proposition that incentives to litigate affect which rules persist is established prior work.

This evolutionary-law literature analyzes how differential incentives to litigate legal rules can change the stock of law. Paper 1E's direction of change and institutional mechanism are different, but its broad claim that altered litigation incentives can alter legal evolution does not begin in 2026.

### 3.4 Shavell: private and social incentives to litigate diverge in a costly legal system

**Work:** Steven Shavell, **“The Social versus the Private Incentive to Bring Suit in a Costly Legal System”**, NBER Working Paper 0741, **September 1981**; *Journal of Legal Studies* 11(2), 1982.

Primary record: <https://www.nber.org/papers/w0741>

**Compared claim:** C1.

**Classification:** `prior_art` for the generic private-versus-social incentive divergence created by litigation costs; `partial_prior_art` for Paper 1E's narrower claim about investment in *argument quality* and precedent improvement.

Shavell directly asks how a private party's incentive to bring suit relates to the socially appropriate level when legal-system costs and social gains are not internalized. Paper 1E's collective-action skeleton therefore has a clear law-and-economics antecedent even though its object is high-quality argument rather than the binary filing decision.

### 3.5 Strategic judicial hierarchy was already a mature game-theoretic literature

**Works:**

- Charles M. Cameron, Jeffrey A. Segal & Donald Songer, **“Strategic Auditing in a Political Hierarchy: An Informational Model of the Supreme Court's Certiorari Decisions”**, *American Political Science Review*, published online **2000-03-01**: <https://www.cambridge.org/core/journals/american-political-science-review/article/abs/strategic-auditing-in-a-political-hierarchy-an-informational-model-of-the-supreme-courts-certiorari-decisions/5FDA958BDA087A276B4DC9DC08C0D189>.
- Chad Westerland, Jeffrey A. Segal, Lee Epstein, Charles M. Cameron & Scott Comparato, **“Strategic Defiance and Compliance in the U.S. Courts of Appeals”**, *American Journal of Political Science* 54(4), first published **2010-07-21**, DOI `10.1111/j.1540-5907.2010.00465.x`.

**Compared claim:** C2.

**Classification:** `prior_art` for modeling higher/lower courts as strategic actors under hierarchical control; `partial_prior_art` for Paper 1E's particular two-strategy argumentative-effort game.

Cameron–Segal–Songer explicitly use a game-theoretic model in which a higher court reviews signals and a lower court strategically exploits ambiguity. Westerland et al. use a principal-agent framework and a large empirical sample of subsequent treatments of Supreme Court precedent. Paper 1E may use a different payoff structure and normative object, but the generic move “model higher and lower courts strategically and study equilibrium compliance/defiance” is prior art.

### 3.6 Brazilian law-and-economics literature already linked binding precedent, litigation costs, and filing incentives

**Work:** João Máximo Rodrigues Neto, **“A Relevância dos Precedentes na Análise Econômica da Litigância — Um Estudo de Law and Finance”**, *Revista Direito em Debate* 26(48), **2017-12-28**, DOI `10.21527/2176-6622.2017.48.63-83`.

Primary record: <https://www.revistas.unijui.edu.br/revistadireitoemdebate/pt_BR/article/view/5781>

**Compared claims:** C1, C3, C6.

**Classification:** `prior_art` for applying cost-benefit/litigation incentives to Brazilian binding precedents; `partial_prior_art` for Paper 1E.

The article explicitly treats litigants as economic agents deciding whether to sue from litigation cost/benefit and analyzes how binding precedents can reduce costs and discourage litigation. The predicted direction differs from Paper 1E's AI channel, but Brazilian binding-precedent + litigation-cost economics is not an unoccupied combination.

### 3.7 LLM assistance was already known to reduce time on legal tasks

**Works:**

- Jonathan H. Choi, Amy B. Monahan & Daniel Schwarcz, **“Lawyering in the Age of Artificial Intelligence”**, research paper publicly reported **2023-11-09**, later *Minnesota Law Review* 109 (2024): <https://scholarship.law.umn.edu/minnlrev/vol109/iss1/3/>.
- Aileen Nielsen, Stavroula Skylaki, Milda Norkute & Alexander Stremitzer, **“Building a better lawyer: Experimental evidence that artificial intelligence can increase legal work efficiency”**, *Journal of Empirical Legal Studies*, first published **2024-11-17**, DOI `10.1111/jels.12396`.
- Colleen V. Chien & Miriam Kim, **“Generative AI and Legal Aid: Results from a Field Study and 100 Use Cases to Bridge the Access to Justice Gap”**, preliminary draft publicly reported **2024-03-14**, later *Loyola of Los Angeles Law Review* 57.

**Compared claim:** C4.

**Classification:** `prior_art`.

The RCT lineage already showed large, consistent speed gains on realistic lawyering tasks, while later work showed a 30% time reduction without measured quality loss for one form of AI assistance. The legal-aid field study reported productivity gains among practitioners. Thus the generic “AI reduces the cost/time of legal work” proposition cannot bear Paper 1E's novelty.

### 3.8 Thompson 2024 is the closest generic antecedent to Paper 1E's stated central contribution

**Work:** Henry A. Thompson, **“AI and the law”**, arXiv v1 **2024-12-06 14:48:02 UTC**, arXiv:2412.05090; later *Kyklos*, first published online 2025-09-14.

Primary preprint: <https://arxiv.org/abs/2412.05090>

**Compared claims:** C3 and C4; materially adjacent to C1.

**Classification:** `prior_art` for the generic comparative-static claim that generative AI reduces litigation/legal-work costs, increases demand for courts, and changes the speed of legal evolution; `partial_prior_art` for the complete Brazil/STF mechanism.

This is the audit's most consequential finding. Thompson explicitly treats generative AI as labor-augmenting technology that reduces litigation cost; states that attorneys produce information about law, precedents, sound legal arguments and procedural rules; identifies legal search, argument creation, and legal writing as core inputs; argues that AI makes trial attorneys more productive in preparing arguments, motions and briefs and therefore lowers the marginal cost of legal services; and concludes that cheaper litigation changes demand for courts and can accelerate legal change by increasing challenges to inefficient rules.

Accordingly, Paper 1E's original formulation that its “central contribution” is to show that technological reduction in the cost of producing legal arguments changes the game's parameters and legal equilibrium is too broad as a novelty claim. Thompson was publicly available about seventeen months before Paper 1E's cutoff and connects GenAI → lower legal/litigation cost → more court use → faster legal evolution directly.

The residual distinction is substantive: Thompson models common-law evolution through litigation and settlement incentives, not Brazilian CPC argumentative duties, reclamação, reason-giving pressure on the STF, or a higher/lower-court `(β,β) → (α,α)` engagement transition.

### 3.9 Pre-cutoff experiments had already moved from speed to quality + productivity

**Work:** Daniel Schwarcz et al., **“AI-Powered Lawyering: AI Reasoning Models, Retrieval Augmented Generation, and the Future of Legal Practice”**, first published online **2026-04-09**, *Journal of Law & Empirical Analysis*, DOI `10.1177/2755323X261427048`.

Primary record: <https://journals.sagepub.com/doi/full/10.1177/2755323X261427048>

**Compared claim:** C4, especially Paper 1E's post-objection narrowing toward practitioners able to produce higher-quality analytical work.

**Classification:** `prior_art` for the generic proposition that then-current legal AI could increase both measured quality and productivity on at least some complex legal tasks.

The randomized trial reports statistically significant productivity gains of roughly 50–130% in five of six tasks and improved legal-work quality with RAG/reasoning systems. This directly weakens any novelty boundary based merely on distinguishing textual speed from analytical quality.

### 3.10 A pre-cutoff U.S. draft already documented the volume-and-burden channel

**Work:** Anand V. Shah & Joshua Y. Levy, **“Access to Justice in the Age of AI: Evidence from U.S. Federal Courts.”**

The temporal record requires care. The eventual SSRN page was posted after our cutoff (May 21, 2026), so that posting cannot be used as pre-cutoff priority. However, a public Volokh/Reason article on **2026-04-28** quoted and identified the work as a draft, providing independently verifiable public disclosure before Paper 1E's May 13 cutoff: <https://reason.com/volokh/2026/04/28/apparent-surge-in-self-represented-litigation-using-ai/>.

**Compared claims:** C3, C4.

**Classification:** `partial_prior_art` based on the April 28 public disclosure, not on the later SSRN posting.

The publicly quoted draft analyzed more than 4.5 million federal civil cases and reported a rise in pro se filing share, increased docket activity/burden, and growing AI-generated text. It therefore anticipates the empirical channel “lower AI-enabled production barriers → more legal filings → more institutional burden” before our cutoff. It does not test high-quality precedent-changing arguments or the STF engagement mechanism.

### 3.11 Brazil already had public evidence of an AI-driven litigation-volume feedback loop

**Work/report:** Pedro Nakamura, **“AI is helping judges to quickly close cases, and lawyers to quickly open them”**, *Rest of World*, **2025-09-25**: <https://restofworld.org/2025/brazil-ai-courts-lawsuits/>.

**Compared claims:** C3, C4, contextual to C5.

**Classification:** `partial_prior_art` / jurisdiction-specific public antecedent, not a causal academic demonstration.

The report documents a Brazilian judiciary simultaneously using AI to close cases faster while lawyers use generative AI and file at record levels, and quotes a CNJ councilor observing that AI appears to be increasing litigation. It also reports that legal drafting that previously took minutes could be completed in seconds in some workflows. This is highly relevant because it places the cost/volume feedback in Brazil before Paper 1E, but it does **not** establish the paper's stronger quality-and-engagement chain: more *auditable* arguments, STF reason-giving pressure, and precedent-equilibrium change.

## 4. Classification change produced by this audit

The audit materially narrows the novelty boundary.

| Claim | Classification after audit | Reason |
|---|---|---|
| C1 private/social incentive divergence | `prior_art` at generic level; `partial_prior_art` for argument-quality version | Shavell and the repeat-player/evolution literature already model private/social cost divergence and costly investment in legal change. |
| C2 strategic higher/lower-court equilibrium | `prior_art` at generic level | Game-theoretic and principal-agent judicial-hierarchy models long predate Paper 1E. |
| C3 lower technology/litigation cost changes legal evolution | `prior_art` | Thompson 2024 states the GenAI comparative static directly; older evolutionary-law work supplies the litigation-selection mechanism. |
| C4 GenAI raises legal-work productivity and may raise quality | `prior_art` | Choi/Monahan/Schwarcz, Nielsen et al., Chien/Kim, and Schwarcz et al. predate the cutoff. |
| C5 STF/reclamação engagement-pressure feedback | **unresolved combination** | No pre-cutoff work located in this run models the specific chain from cheaper auditable arguments through reclamação to higher non-engagement cost and changed STF precedent practice. |
| C6 CPC-2015 doctrinal coupling | components are prior doctrinal background; combination with C5 unresolved | Argumentative burdens and institutional dialogue are established Brazilian doctrine; their coupling to the AI comparative static was not located before cutoff. |

The strongest correction is therefore:

> The paper should not rely on the generic proposition “technology/GenAI lowers the cost of legal argument or litigation and therefore changes legal-system behavior/evolution” as its central novelty. That mechanism has substantial prior art, most directly Thompson (2024). The defensible research question is the narrower Brazilian feedback mechanism: whether cheaper *auditable and substantively strong* argument changes the behavior of a precedent-setting court by changing the cost of reasoned engagement versus non-engagement.

This is a novelty-boundary correction, not a claim that the paper lacks scientific value. The Brazil-specific institutional mechanism is more precise and more falsifiable than the broader claim.

## 5. Work after our cutoff

### 5.1 The New Pro Se — later non-citing overlap on the volume/burden subclaim

**Work:** Or Cohen-Sasson, **“The New Pro Se: Generative AI and the Surge in Federal Civil Self-Representation”**, arXiv v1 **2026-05-28 07:19:09 UTC**, arXiv:2605.29493: <https://arxiv.org/abs/2605.29493>.

**Temporal relation:** 15 days after our May 13 cutoff.

**Compared claim:** C4 and the lower-barrier → more-filings → court-burden portion of C3.

**Classification:** `later_non_citing` for this subclaim only.

The paper analyzes roughly 2.8 million U.S. federal filings, reports a rise in pro se plaintiffs from 11.33% to 16.94%, identifies AI-consistent complaint drafting, and finds no improvement in win rates while raising court-screening-burden concerns. In the searchable full text inspected during this audit, no occurrence of `Baldo`, `Custos Argumentativos`, or `Rondônia` was located.

That fact supports only the narrow label: later publication, material overlap on the access/volume/burden subclaim, and no citation located. It does **not** establish derivation, copying, plagiarism, awareness, or bad faith. The work is U.S.-federal and does not reproduce the STF/reclamação/argument-quality mechanism.

### 5.2 Later evidence can cut against Paper 1E's optimistic quality channel

Later 2026 reporting on AI-related filing errors and sanctions strengthens a competing mechanism: lower production cost may increase volume while lowering average reliability or increasing screening cost. This does not alter priority; it matters to maturity and experimental design. Paper 1E's strongest surviving proposition therefore cannot be tested using filing volume alone. It must separately measure *quality/auditability* and *institutional engagement*.

## 6. Negative search result and residual boundary

After searches across law-and-economics, judicial-politics, Brazilian precedent doctrine, legal-AI productivity, access-to-justice, AI-filing-volume, and exact-title/author terminology, this run did **not** locate a pre-`2026-05-13 03:20:45 UTC` source that contains the full following conjunction:

1. Brazilian CPC-2015 precedent/argumentative-duty architecture;
2. a strategic low-effort equilibrium between STF and lower courts framed around quality of reasons rather than only outcomes/compliance;
3. generative-AI or related technology reducing the cost of producing **auditable and substantively strong** precedent-challenging arguments;
4. those arguments reaching the STF specifically through reclamação or a functionally equivalent review channel;
5. the increased argument supply raising the institutional/reputational cost of *not engaging the argument's reasons* rather than merely raising court workload;
6. that pressure changing the stable precedent equilibrium toward more reasoned institutional dialogue.

This is **limited negative-search evidence**, not proof that no antecedent exists. The search also found strong reasons to decompose the mechanism: cheaper drafting can increase filings without improving legal efficacy; courts can endogenously raise screening/engagement thresholds; and the marginal cost reduction may be larger for textual production than for ratio identification and doctrinal analysis.

## 7. Experimental consequence

The prior-art review makes the next empirical test clearer. A meaningful Paper 1E experiment should distinguish four stages that prior work often collapses:

1. **production cost:** time/money needed to prepare a precedent challenge;
2. **argument quality:** correctness of ratio identification, factual mapping, distinguishing/superação logic, citation accuracy, and auditability;
3. **institutional engagement:** whether the STF actually answers the argument's decisive reasons, not merely whether it disposes of the case;
4. **precedent effect:** distinction, narrowing, revision, clarification, or durable change in lower-court treatment.

A useful design would compare matched reclamações or precedent challenges across a documented technology/adoption shock, with blinded doctrinal scoring of argument quality and engagement quality. It should pre-register controls for:

- endogenous increases in the court's engagement threshold as volume rises;
- AI-assisted low-quality/noisy filings;
- rapporteur-level rather than court-unitary incentives;
- case selection and stakes;
- repeat-player status and legal-resource differences;
- professional-press/publicity channels;
- whether any measured effect is on outcome, reasoning quality, or both.

The decisive result is **not** “AI produced more filings.” That channel was already anticipated and, before our cutoff, publicly observed. The distinctive test is whether lower production cost for *verified high-quality argument* changes the probability and depth of reasoned engagement and, eventually, precedent behavior.

## 8. Source/date ledger

| Candidate | Earliest public date used | Claim | Classification |
|---|---:|---|---|
| Galanter, *Why the Haves Come Out Ahead* | 1974 (earlier 1973 conference lineage noted) | C1 | `prior_art` generic / `partial_prior_art` specific |
| Landes & Posner, *Legal Precedent* | 1976-08 | C1/C3 | `partial_prior_art` |
| Rubin, *Why Is the Common Law Efficient?* | 1977-01-01 | C1/C3 | `partial_prior_art` |
| Shavell, *Social versus Private Incentive to Bring Suit* | 1981-09 | C1 | `prior_art` generic / `partial_prior_art` specific |
| Cameron, Segal & Songer, *Strategic Auditing* | 2000-03-01 online | C2 | `prior_art` generic |
| Westerland et al., *Strategic Defiance and Compliance* | 2010-07-21 online | C2 | `prior_art` generic |
| Rodrigues Neto, *Precedentes na Análise Econômica da Litigância* | 2017-12-28 | C1/C3/C6 | `partial_prior_art` |
| Choi, Monahan & Schwarcz, *Lawyering in the Age of AI* | public study report 2023-11-09 | C4 | `prior_art` |
| Nielsen et al., *Building a better lawyer* | 2024-11-17 | C4 | `prior_art` |
| Thompson, *AI and the law* | **2024-12-06 14:48:02 UTC** | **C3/C4** | **`prior_art` generic; strong `partial_prior_art` full claim** |
| Rest of World, Brazil AI court/lawyer feedback | 2025-09-25 | C3/C4 contextual C5 | `partial_prior_art` |
| Schwarcz et al., *AI-Powered Lawyering* | 2026-04-09 | C4 | `prior_art` |
| Shah & Levy draft, public quotation | **2026-04-28** | C3/C4 | `partial_prior_art` (SSRN posting itself is later) |
| **Our Paper 1E public PR cutoff** | **2026-05-13 03:20:45 UTC** | C1–C6 | — |
| Cohen-Sasson, *The New Pro Se* | 2026-05-28 07:19:09 UTC | C3/C4 subclaim | `later_non_citing` |

## 9. Epistemic revision note

This audit is an additive revision to the repository's epistemic record. It does not erase the adversarial/supportive debate that later narrowed Paper 1E's prediction. It adds an orthogonal conclusion that the debate had not established: **several propositions treated rhetorically as part of the paper's central contribution were already occupied by older law-and-economics, judicial-politics, and legal-AI work.**

The residual research contribution, if it survives empirical testing, is narrower and more jurisdictionally specific: an STF/reclamação reason-engagement feedback mechanism in which technological cost reduction matters only insofar as it expands the supply of genuinely auditable, precedent-relevant argument rather than merely text or filings.
