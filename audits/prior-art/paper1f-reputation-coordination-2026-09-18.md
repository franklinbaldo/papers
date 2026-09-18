---
type: "Audit Report"
title: "Paper 1F — reputação, verificabilidade e recalibração prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of reputation as a substitute for costly verification in legal services, prestige/proxy effects, incumbent opacity incentives, technology-driven recalibration, and the later local court-practitioner channel."
tags: [paper1f, prior-art, reputation, legal-services, information-asymmetry, transparency, lawyer-quality, access-to-justice]
timestamp: 2026-09-18T10:01:00-04:00
---

# Paper 1F — reputação, verificabilidade e recalibração prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal prior-art audit of [`paper1F_reputacao_sistema_juridico.md`](../../paper1F_reputacao_sistema_juridico.md). The audit reconstructs the public date of the original mechanism separately from the later local-channel narrowing. It distinguishes the novelty of individual components from the novelty of their combination and does **not** infer copying, plagiarism, bad faith, patent novelty, or causal dependence from chronology alone.

## 1. Claims audited

For temporal and substantive comparison, the current paper is decomposed into six claims:

- **C1 — reputation as costly-verification substitute:** legal services and legal argument quality are difficult/expensive to assess directly, so reputation, certification, affiliation and related signals substitute for direct quality verification;
- **C2 — proxies and self-reinforcing advantage:** legal reputation often tracks institutional affiliation, prestige, credentials, network and outcome history imperfectly; these signals can influence selection and adjudicative treatment and can reinforce incumbent advantage independently of underlying argumentative quality;
- **C3 — opacity-rent / resistance mechanism:** agents and institutions holding accumulated reputational capital have a structural interest in preserving informational opacity because cheaper direct verification reduces the relative value of reputation-based proxies;
- **C4 — technological recalibration:** cheaper direct or data-driven verification of quality reduces reliance on prestige/reputation proxies and can open a quality-based path for actors who lack incumbent institutional capital;
- **C5 — local court-practitioner channel:** after the later adversarial/supportive narrowing, verified output can at most establish a first-stage local reputation channel through repeated direct observation by courts that actually see a practitioner's filings; wide network propagation is a separate and unresolved mechanism;
- **C6 — full Paper 1F synthesis:** costly verification → proxy-based legal reputation → incumbent advantage/opacification incentives → technological verification shock → partial devaluation/recalibration of proxies + bounded local quality-based reputation-building, subject to the paper's later institutional-scope and enforcement qualifications.

The paper's empirical claims about high-volume/low-review dockets, triage, institutional practitioners and Brazilian sortition/rotation/assessor mediation are treated primarily as scope and falsification conditions, not as free-standing novelty claims.

## 2. Temporal reconstruction of our claims

### 2.1 Original mechanism: cutoff 2026-05-13 03:20:45 UTC

The current file timestamp is not the priority date. The first repository commit containing `paper1F_reputacao_sistema_juridico.md` is [`3de41c63f429ab2f4f9a1844825be2e9bd78dbf4`](https://github.com/franklinbaldo/papers/commit/3de41c63f429ab2f4f9a1844825be2e9bd78dbf4), dated **2026-05-13 03:20:27 UTC**.

That first version already states, in the abstract and introduction, the core chain audited here: legal reputation substitutes for expensive direct verification; reputation tracks institutional and relational proxies rather than quality directly; opacity makes those proxies valuable; accumulated reputational-capital holders have a structural interest in opacity; and technological reduction in verification cost can devalue proxies and open a new quality-based reputation channel.

The corresponding public [PR #9](https://github.com/franklinbaldo/papers/pull/9) opened at **2026-05-13 03:20:45 UTC**. This audit conservatively uses the PR-opening time as the public cutoff for **C1–C4 and C6**.

### 2.2 Local-channel narrowing: cutoff 2026-07-01 09:12:11 UTC

The current main paper is materially narrower than the May version. The explicit first-stage/second-stage distinction — a **local bilateral court-practitioner reputation channel** without claiming broad network propagation — was first made publicly in the Paper 1F supportive branch in [PR #152](https://github.com/franklinbaldo/papers/pull/152), opened **2026-07-01 09:12:11 UTC**. The PR says that courts directly observe practitioner filings over repeated cases and that this can support stage (a), while stage (b), wide network propagation, remains constrained by the attribution gap.

This is the relevant earliest public cutoff for **C5**, even though the narrowing was absorbed into the main paper later. Later July edits further constrained the mechanism by high-volume/low-review scope, random distribution, judicial mobility, assessor mediation, practitioner incentives and the triage-outcome condition; those changes are treated as epistemic narrowing rather than as moving C1–C4's original priority date forward.

A candidate is classified as `prior_art` only when its earliest verified public date precedes the cutoff of the claim being compared.

## 3. Search protocol

The search was claim-led and used historical as well as modern terminology. Sources consulted included journal/DOI pages, arXiv, NBER, RePEc/EconPapers, working-paper repositories, law-review archives, primary case-law pages and targeted GitHub/web searches. Primary or publisher records were preferred for dates and substantive confirmation.

Representative queries included:

- `market for lawyers quality certification reputational concerns judges information quality legal services`
- `law firm reputational economies of scale quality signal information asymmetry`
- `law firm reputational bonds insufficient information quality legal services`
- `self-regulation legal profession individual collective reputation information asymmetry`
- `lawyer advertising information asymmetry entry barriers established attorneys Bates`
- `data-driven law firm rankings reputation litigation outcomes information asymmetry`
- `law firm prestige rankings feedback loop outcomes quality`
- `information lawyer quality field experiment labor court machine learning lawyer selection`
- `technology transparency legal services reputation quality verification`
- `lawyer reputation transparency AI quality rankings 2026`
- exact-title, `Franklin Baldo`, `Franklin Silveira Baldo`, `argumentative transparency`, `reputational capital` and related post-cutoff overlap/citation searches.

Negative search results below are bounded by these queries and sources. They are not evidence of nonexistence.

## 4. Pre-cutoff findings

### 4.1 Daniels (1992): law-firm reputation as a quality signal under client information deficits

**Work:** Ronald J. Daniels, **“The Law Firm as an Efficient Community.”** *McGill Law Journal* 37(3), September 1992.

- public journal archive: <https://lawjournal.mcgill.ca/article/law-firm-as-an-efficient-community-the/>;
- venue/status: peer-reviewed/edited law-journal article.

Daniels's survey of law-firm organization explicitly describes **reputational bonding**: where clients have insufficient information about the quality of legal services, lawyers invest in a brand/reputation to signal commitment to quality. The article predates Paper 1F by more than three decades.

**Compared claims:** C1, C2.

**Classification:** `prior_art` for the generic mechanism that legal-service reputation/brand substitutes for unavailable direct quality information; `partial_prior_art` for Paper 1F's distributed internal network account.

**Material consequence:** C1 cannot be presented as novel merely because it moves Akerlof/Kreps into the legal market. The law-firm literature had already made the legal-services information-deficit → reputation-as-quality-signal move explicitly.

### 4.2 Iossa & Jullien (2007 working paper; 2012/2013 journal): certified lawyer quality affects both matching and judicial decisions

**Work:** Elisabetta Iossa; Bruno Jullien, **“The Market for Lawyers: The Value of Information on the Quality of Legal Services”** / final **“The market for lawyers and quality layers in legal services.”**

- earliest verified working-paper version: **IDEI Working Paper 485, November 2007**;
- working-paper record: <https://www.tse-fr.eu/articles/market-lawyers-value-information-quality-legal-services>;
- final: *RAND Journal of Economics* 43(4), 2012, pp. 677–704; DOI <https://doi.org/10.1111/1756-2171.12004>.

The model expressly considers litigants, lawyers and judges, lawyer-quality certification, information over legal-service quality and judges with reputational concerns. It finds that reputation/certification information can improve matching while also producing **decision bias in favor of certified lawyers** and lawyer misallocation.

**Compared claims:** C1, C2, C6.

**Classification:** `prior_art` for C1 and for the generic proposition in C2 that legal-quality signals/certification can shape adjudicative treatment rather than merely describe true quality; `partial_prior_art` for C6.

**Material consequence:** Paper 1F's judge-facing reputation mechanism must be distinguished from an already formalized literature in which information about lawyer quality affects judges and equilibrium allocation.

### 4.3 Iacobucci (2012): law firms possess reputational economies of scale

**Work:** Edward M. Iacobucci, **“Reputational Economies of Scale, with Application to Law Firms.”** *American Law and Economics Review* 14(1), 302–329.

- published **2012-01-31**;
- publisher: <https://academic.oup.com/aler/article-abstract/14/1/302/162182>;
- DOI: <https://doi.org/10.1093/aler/ahr023>.

Iacobucci models circumstances in which firm scale creates reputational advantages because more future business is placed at risk by low-quality performance. The paper applies that logic expressly to law firms.

**Compared claims:** C2, C6.

**Classification:** `prior_art` for the generic proposition that organizational affiliation/scale can itself create a reputational advantage in legal services; `adjacent_prior_work` for the specific Brazilian proxy-devaluation mechanism.

### 4.4 Chaserant & Harnay (public online 2013; journal 2015): individual and collective legal-profession reputation sustains quality and rents

**Work:** Camille Chaserant; Sophie Harnay, **“Self-regulation of the legal profession and quality in the market for legal services: an economic analysis of lawyers’ reputation.”** *European Journal of Law and Economics* 39(2), 431–449.

- published online **2013-10-22**; journal issue 2015;
- DOI: <https://doi.org/10.1007/s10657-013-9420-1>;
- RePEc record: <https://ideas.repec.org/a/kap/ejlwec/v39y2015i2p431-449.html>.

The paper starts from strong information asymmetry in legal services, combines individual and collective reputation, and models the profession's incentive to preserve a good collective reputation because it raises clients' willingness to pay and therefore the rent accruing to lawyers collectively.

**Compared claims:** C1, C3, C6.

**Classification:** `prior_art` for C1; `partial_prior_art` for C3 because it explicitly connects legal-profession reputation to rents/incentives but does not derive Paper 1F's stronger proposition that incumbents structurally prefer *argumentative opacity itself* because opacity preserves proxy value.

### 4.5 *Bates v. State Bar of Arizona* (1977): information restrictions can entrench established lawyers

**Work:** *Bates v. State Bar of Arizona*, 433 U.S. 350 (U.S. Supreme Court, decided **1977-06-27**).

- primary-opinion reproduction: <https://supreme.justia.com/cases/federal/us/433/350/>;
- alternative primary-text reproduction: <https://www.law.cornell.edu/supremecourt/text/433/350>.

The Court rejected a blanket lawyer-advertising ban and reasoned that lack of information impedes consumer search and competition. Most relevant to C3, it observed that, absent advertising, an attorney must rely on community contacts accumulated over time and that the ban therefore **perpetuates the market position of established attorneys**.

**Compared claims:** C2, C3, C4.

**Classification:** `prior_art` for the narrower mechanism “information restriction can entrench established lawyers and burden new entry”; `partial_prior_art` for C3's opacity-capital mechanism; `adjacent_prior_work` for C4 because advertising is information disclosure, not direct automated quality verification.

**Material consequence:** the claim that informational opacity can protect incumbent legal-market position has a strong pre-existing legal analogue. Paper 1F's residual novelty, if any, must be in the **argument-quality verification shock and reputational-capital comparative static**, not the generic entrenchment effect of restricted information.

### 4.6 Sadka, Seira & Woodruff (2018 working paper; 2024 journal): providing court-generated outcome information changes legal behavior and lawyer selection

**Work:** Joyce Sadka; Enrique Seira; Christopher Woodruff, **“Information and Bargaining through Agents: Experimental Evidence from Mexico’s Labor Courts.”** NBER Working Paper 25137.

- first public NBER working paper: **October 2018**;
- <https://www.nber.org/papers/w25137>;
- final: *Review of Economic Studies* 91(6), 2024.

The field experiment provides litigants with personalized statistical predictions from court data. It reduces information asymmetry, changes settlement behavior and, in related results from the same experimental program, increases the quality of lawyer hired by first-time court users by reducing reliance on low-quality intermediated counsel.

**Compared claims:** C1, C4.

**Classification:** `partial_prior_art` for C4. The experiment shows that low-cost quantitative information can change legal-market selection and reduce an information disadvantage, but it does not test argumentative-quality verification or the devaluation of professional reputation itself.

### 4.7 Caplin, Gomberg & Sadka (2024): cheap information-indexing improves adjudicative quality

**Work:** Andrew Caplin; Andrei Gomberg; Joyce Sadka, **“Judging the Judges: Indexing of Complex Information Reduces Injustice.”** NBER Working Paper 32587.

- issue date **June 2024**;
- <https://www.nber.org/papers/w32587>.

In a Mexican labor-court field study, merely indexing case-file pages to reduce judges' information-processing cost sharply reduced successful appeals in complex cases and produced shorter, more on-point opinions.

**Compared claims:** C4, C6.

**Classification:** `adjacent_prior_work` for C4. It supplies empirical evidence for the broader premise that lowering legal information-verification/access costs can change adjudicative performance, but does not concern reputation or prestige proxies.

### 4.8 Mojon, Mahari & Lera (arXiv 2024): empirical law-firm quality measures outperform prestige rankings and explicitly aim to level the playing field

**Work:** Alexandre Mojon; Robert Mahari; Sandro Claudio Lera, **“Addressing Information Asymmetry in Legal Disputes through Data-Driven Law Firm Rankings.”** arXiv:2408.16863; later published as **“Data-driven law firm rankings to reduce information asymmetry in legal disputes”** in *Nature Computational Science* (2025).

- arXiv v1: **2024-08-29 19:04:45 UTC**;
- <https://arxiv.org/abs/2408.16863>;
- final publisher page: <https://doi.org/10.1038/s43588-025-00899-2>.

This is the closest located pre-cutoff work to the recalibration half of Paper 1F. It finds that widely used law-firm rankings are reputation/prestige based and correlate poorly with actual litigation outcomes; an outcome-based ranking predicts future performance better. The paper also describes a feedback loop in which highly ranked firms attract more clients and thereby reinforce prestige, and explicitly frames empirical rankings as a way to make quality assessment more equitable and **level the playing field** between litigants.

**Compared claims:** C2, C4, C6.

**Classification:** `prior_art` for the generic C2 proposition that prestige/reputation rankings can be poor proxies for legal performance and self-reinforcing; `prior_art` for the generic selection-side version of C4 (“objective/data-driven quality signal can displace prestige proxies and democratize access to quality information”); `partial_prior_art` for C6 and for Paper 1F's argument-verification/court-facing version.

**Material consequence:** Paper 1F cannot safely claim novelty for the broad comparative static **“better empirical quality information → less dependence on prestige/reputation → more equal access to quality signals.”** That comparative static was public by August 2024. The defensible residual is narrower: direct verification of *argumentative compliance/quality* as a shock to reputational capital inside ongoing legal interactions, plus the bounded local repeated-observation channel.

### 4.9 Lera et al. (2026-05-07): litigation prediction already uses law-firm and judge information immediately before our cutoff

**Work:** Sandro Claudio Lera; Shahrokh Firouzi; Jonathan Habshush; Robert Mahari, **“Predicting civil litigation outcomes and the evolution of case complexity and settlement dynamics.”** arXiv:2605.06151.

- arXiv v1: **2026-05-07 12:43:31 UTC**, six days before our original cutoff;
- <https://arxiv.org/abs/2605.06151>.

The paper models 835,190 litigation filings over time using structured legal features, text embeddings and information about judges and law firms to estimate outcome probabilities throughout a case. It is not a reputation-recalibration paper, but it is evidence that quantitative systems were already turning judge/law-firm identities and litigation records into directly usable predictive information before Paper 1F's public cutoff.

**Compared claims:** C2, C4.

**Classification:** `adjacent_prior_work`.

## 5. Claim-by-claim classification after this round

| Claim | Classification | Why |
|---|---|---|
| C1 — reputation as costly-verification substitute | `prior_art` | legal-services reputation/reputational bonding, certification and collective/individual reputation under information asymmetry were already explicit in Daniels, Iossa–Jullien and Chaserant–Harnay |
| C2 — imperfect prestige/proxy signals and self-reinforcing advantage | `prior_art` at generic level | Iossa–Jullien model certification-driven adjudicative bias; Bates identifies incumbent entrenchment from information restrictions; Iacobucci models law-firm reputational advantages; Mojon et al. show prestige rankings poorly predict outcomes and can reinforce themselves |
| C3 — reputational-capital holders structurally prefer opacity because it preserves proxy value | `partial_prior_art` | pre-cutoff sources establish reputation rents and information restrictions that entrench incumbents, but no located source derives the full opacity → proxy-value → incumbent resistance mechanism in Paper 1F's argumentative-verification setting |
| C4 — cheaper direct/data-driven verification recalibrates reputation and opens access | `prior_art` for generic legal-market selection; `partial_prior_art` for Paper 1F's internal argumentative mechanism | Mojon et al. directly replace prestige-based rankings with empirical performance measures and frame this as leveling the playing field; the specific argumentative-compliance verification shock remains narrower |
| C5 — bounded local bilateral court-practitioner reputation channel | `adjacent_prior_work` / no material anticipation located | repeated-game/reputation theory is old, but no pre-2026-07-01 source located in this search combines direct observation of verified legal filings with the explicit local-stage / network-propagation distinction |
| C6 — full synthesis | `partial_prior_art` | most components pre-exist; the exact combination, especially the direct argumentative-verification shock + opacity-rent comparative static + local-channel narrowing, was not located as one pre-cutoff mechanism |

## 6. Post-cutoff search

Targeted searches covered **2026-05-13 through 2026-09-18** for papers, preprints, projects and reports combining lawyer/law-firm reputation, objective quality measurement, AI or automated verification, transparency, incumbent prestige, and legal-market access. For C5, the temporal search used the later **2026-07-01** cutoff.

Several later works and current projects discuss AI-driven legal-service discovery, lawyer matching, transparent attorney scoring, litigation prediction, AI-assisted self-representation or reputation mechanisms in non-legal AI-agent markets. In this round, however, none met the threshold for material overlap with the **full Paper 1F mechanism** or with C5's local bilateral channel.

Accordingly, this audit records **no `later_non_citing`, `later_overlap`, `later_citing` or `later_derivative` finding**. That negative result is bounded by the queries and sources above. It does not establish absence of later overlap.

A noteworthy near-cutoff development is the public discussion of AI-assisted pro se litigation in May 2026, but it concerns lowered production/access costs rather than reputation recalibration and is therefore not classified as a materially overlapping later work.

## 7. What changes epistemically

The strongest broad claims in the original May paper are more occupied than the paper's current framing suggests:

1. **Reputation as a response to legal-service information asymmetry is established prior art.** It is not merely an application of Akerlof/Kreps invented here; legal-market scholarship had already made the move explicitly.
2. **Institutional/legal reputation affecting adjudicative treatment is established prior art.** Iossa–Jullien is particularly close because it models judges, lawyers, quality information and certification-induced decision bias together.
3. **Informational restrictions protecting incumbent lawyers are established prior art.** *Bates* gives a canonical legal example; Paper 1F's opacity-rent mechanism is a more specific theoretical extension, not the first entrenchment story.
4. **Data-driven quality assessment displacing prestige rankings and leveling the playing field is established prior art at the law-firm-selection level.** Mojon–Mahari–Lera is the crucial missing comparator.
5. The residual worth defending is therefore **not** “reputation matters in law” or “transparency/data can democratize legal markets.” It is the narrower mechanism in which **argument-level verifiability** changes the relative value of accumulated proxy capital inside legal interactions, together with the paper's deliberately bounded local reputation channel and its failure conditions.

## 8. Consequences for experiment/design

A convincing empirical test should no longer compare “reputation” with “no reputation.” It should separate at least four information regimes under controlled case quality:

1. **prestige/proxy only** — affiliation, credentials, historical rankings;
2. **outcome-based quality signal** — a Mojon-style empirical performance measure;
3. **argument-level verification signal** — direct audit of stated legal compliance/reasoning properties;
4. **combined signal** — prestige + outcome history + argument verification.

The core Paper 1F prediction survives only if condition (3), relative to (2), causes decision-makers or clients to reduce the weight placed on prestige proxies and improves access for low-prestige/high-verified-quality actors. That isolates the paper-specific mechanism from already demonstrated selection effects of better outcome information.

For C5, the clean test is longitudinal and local: hold practitioner identity constant, randomize or phase in verifiable quality information to the same adjudicative units, and ask whether court-side expectations update from verified output history after controlling for institutional affiliation and prior outcomes. Random distribution, judicial turnover and assessor mediation should be measured as moderators rather than treated as background noise.

A falsifier is straightforward: if objective outcome-based rankings already absorb the apparent prestige discount, or if argument-level verification adds no incremental weight shift away from affiliation/credentials after outcome quality is observed, then Paper 1F's distinctive argumentative-recalibration mechanism has not been demonstrated.

## 9. Audit conclusion

After reconstructing the actual GitHub cutoffs and reading the closest legal-market sources, the novelty frontier is materially narrower than the original paper's architecture implies.

No claim is made that the remaining combination is unprecedented. The bounded conclusion is:

> **After the searches recorded above, no pre-cutoff work was located that jointly derives the exact Paper 1F chain of argumentative-quality verification becoming cheaper, accumulated legal proxy capital losing relative informational value, incumbents therefore facing an opacity-rent comparative static, and previously low-capital practitioners building a deliberately local reputation through repeatedly observed verified filings while broad network propagation remains unclaimed.**

The individual ingredients around that chain are heavily populated by prior work, especially legal-services information economics and data-driven law-firm quality measurement. Future revisions should cite that literature explicitly and frame any contribution at the level of the narrower combination and its testable comparative statics, not at the level of reputation, information asymmetry or transparency in legal services generally.
