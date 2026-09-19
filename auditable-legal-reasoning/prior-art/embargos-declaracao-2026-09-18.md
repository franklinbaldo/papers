---
type: "Audit Report"
title: "Paper 1A — embargos de declaração, mérito e efeitos infringentes prior-art audit — 2026-09-18"
description: "Claim-specific temporal audit of Paper 1A's mode-versus-object account of curable defects, infringement as a consequence of integration, drafting implications, and the later unique-determination cognition claim."
tags: [paper1a, prior-art, embargos-de-declaracao, efeitos-infringentes, omissao, merito, cpc, cognicao-integrativa]
timestamp: 2026-09-18T13:01:00-04:00
---

# Paper 1A — embargos de declaração, mérito e efeitos infringentes prior-art audit — 2026-09-18

> **Status:** first claim-specific temporal prior-art audit of [`paper1A_embargos_declaracao.md`](../../paper1A_embargos_declaracao.md). The main finding is material: the paper's central C2 proposition — infringement/modification as a consequence of curing the declaratory defect rather than an autonomous reform request — was already stated in substantially the same form in Brazilian doctrine and case law long before our cutoff. The audit also identifies a likely doctrinal misattribution in current §5.2: publicly verifiable quotations of Nelson Nery Jr. and Rosa Nery support, rather than oppose, the central C2 distinction. This audit does **not** infer copying, plagiarism, bad faith, patent novelty, or causal dependence from chronology alone.

## 1. Claims audited

The current paper is decomposed into the following claims for temporal comparison:

- **C1 — mode, not object:** the curability of a defect by embargos de declaração is defined by the defect's mode — omission, contradiction, obscurity or material error — rather than by whether its subject matter is procedural or merits-based. A genuine omission or internal contradiction can therefore concern the merits.
- **C2 — modification as consequence, not autonomous claim:** when curing a genuine declaratory defect changes the result, the modification is a consequence of integration rather than an autonomous reform claim that has to be granted separately.
- **C3 — drafting consequence:** the formula `subsidiariamente, requer-se a atribuição de efeitos infringentes` is dogmatically misleading; the primary request is to cure the identified defect, with modification following if the cure requires it. A separate/subsidiary infringement claim should not be treated as the juridical source of the modification.
- **C4 — unique-determination cognition boundary:** for the narrower class in which the tribunal's existing commitments uniquely determine the outcome of the omitted argument, integration does not require a new autonomous merits cognition; direction-without-uniqueness and genuinely generative omissions fall outside that defended core.
- **C5 — combined architecture:** broad subject-matter reach of genuine defects + integration-first treatment of modification + a boundary between integrative completion and autonomous merits reconsideration yields the paper's practical account of declaratory motions.
- **C6 — historical-CPC framing:** the current paper suggests that CPC/2015 resolved or materially displaced an older ambiguity in which modification was treated as a special infringent category requiring a distinct request.

## 2. Temporal reconstruction of our claims

The current file timestamp is not the priority date.

### 2.1 C1–C3, C5 and C6: public on 2026-05-10

The earliest repository commit located for `paper1A_embargos_declaracao.md` is:

- [`f4953cd88b135901627a5e647bf6b0401e8a435b`](https://github.com/franklinbaldo/papers/commit/f4953cd88b135901627a5e647bf6b0401e8a435b), committed **2026-05-10 15:01:02 UTC**.

That first public version already states both central propositions in the abstract and introduction: defects are defined by their mode rather than subject matter, and modification is the consequence of curing the defect when the cure implies a different result, not an autonomous subsidiary claim. It also already criticizes the drafting formula requesting infringent effects subsidiarily.

**Cutoff used for C1–C3, C5 and C6:** **2026-05-10 15:01:02 UTC**.

### 2.2 C4: unique-determination narrowing is later

The current `unique determination` boundary did not exist in that exact form in the first version. It was made public in [PR #135](https://github.com/franklinbaldo/papers/pull/135), opened **2026-06-24 10:13:33 UTC**. The PR body expressly says that the defense was narrowed to the class in which the tribunal's existing framework **uniquely determines** the outcome of the omitted argument, with direction-without-uniqueness placed on the generative side of the boundary.

**Cutoff used for C4:** **2026-06-24 10:13:33 UTC**.

This audit does not retroactively assign the May cutoff to the June refinement.

## 3. Search protocol

The search was claim-led rather than title-led. Sources consulted included GitHub history, LexML/STJ case-law records, publicly accessible tribunal decisions, Brazilian procedural scholarship, journal records at UEL/DOAJ, older doctrinal quotations, and current legal-search indexes used only for discovery when a primary or bibliographic source could be identified.

Representative queries preserved from this run include:

- `"pedido" "efeitos infringentes" embargos declaração desnecessário`
- `"efeito infringente" "pedido" embargos declaração consequência`
- `"efeitos modificativos" "pedido" "embargos de declaração" consequência`
- `"Nery" "pedido expresso" "efeitos infringentes" embargos declaração`
- `"Nery" "infringência do julgado" "pedido principal"`
- `"efeito infringente como consequência" embargos declaração`
- `"embargos de declaração" "nova cognição" mérito`
- `"embargos de declaração" "cognição" "terceira instância"`
- `"embargos de declaração" "consequência necessária" "cognição"`
- `"rejeição implícita" argumento embargos declaração omissão STJ`
- exact title, `Franklin Silveira Baldo`, `modo objeto embargos de declaração`, and post-cutoff variants through 2026-09-18.

Negative results below are bounded by these sources and queries. “Not located” is not evidence of nonexistence.

## 4. Pre-cutoff findings

### 4.1 Nery Jr. & Nery: the central C2 distinction is already stated almost verbatim

**Work:** Nelson Nery Jr. & Rosa Maria de Andrade Nery, *Código de Processo Civil Comentado* / later *Comentários ao Código de Processo Civil*.

- underlying cited edition in a publicly verifiable 2006 quotation: **7th ed., 2003**;
- public quotation verified on Migalhas, Carlos Alberto Barbosa de Mattos, **2006-08-10**: <https://www.migalhas.com.br/depeso/26231/embargos-de-declaracao--efeitos-infringentes>;
- the same proposition is reproduced from the 2004 edition in later public decisions and from the CPC/2015 comments in later TRF decisions.

The quoted Nery formulation says that infringement may be a **consequence of granting the declaratory motion**, but cannot be its **main request**, because a direct request to reform the judgment would amount to reconsideration. It further says infringement can occur when it is the **necessary consequence** of curing the defect.

**Compared claims:** C2, C3, C6.

**Classification:** `prior_art` for C2; `partial_prior_art` for C3's more specific drafting prescription; `prior_art` against the historical suggestion in C6 that this integration/consequence structure originates with CPC/2015.

**Material correction:** current Paper 1A §5.2 describes a line “represented by Nery Jr.” as requiring modification to be a separate, express request. The publicly verifiable Nery quotations located in this audit say the opposite on the core point: infringement is not the main request; it is a consequence of the declaratory judgment. The original cited edition should be checked before final publication, but the present attribution should not remain unqualified.

### 4.2 Mattos (2006): publicly accessible restatement before CPC/2015

**Work:** Carlos Alberto Barbosa de Mattos, **“Embargos de declaração: efeitos infringentes?”**, Migalhas, **2006-08-10**.

- URL: <https://www.migalhas.com.br/depeso/26231/embargos-de-declaracao--efeitos-infringentes>.

Mattos, relying expressly on Nery, states that infringement can arise from the defect cure and is not itself the principal request. He treats modification as something that may arise inevitably from correcting omission or contradiction.

**Compared claims:** C2, C3.

**Classification:** `prior_art` for the broad consequence-not-main-request proposition; `partial_prior_art` for Paper 1A's exact replacement drafting formula.

### 4.3 Lima (2007): a dedicated peer-reviewed article already occupied the effects-infringentes problem

**Work:** Thales Fernando Lima, **“Efeitos infringentes dos embargos de declaração.”** *Revista do Direito Público*, 2(2), 115–122.

- publication: **2007-12-15**;
- DOI: <https://doi.org/10.5433/1980-511X.2007v2n2p115>;
- journal record: <https://ojs.uel.br/revistas/uel/index.php/direitopub/article/view/11459/0>.

The journal abstract confirms that the article specifically analyzes doctrinal and case-law treatment of declaratory motions whose grant substantially changes the challenged decision.

**Compared claims:** C2, C3.

**Classification:** `adjacent_prior_work` on the basis of the verified journal record alone. The full article should be read before assigning a stronger claim-level classification; this audit does not infer exact anticipation from title/abstract similarity.

### 4.4 Monteiro Neto (2010): modification as effect of judgment, not an infringent request

**Work:** João Pereira Monteiro Neto, **“Os denominados ‘efeitos modificativos’ em embargos de declaração são mesmo excepcionais?”**, Jus Navigandi, **2010-01-28**.

- URL: <https://jus.com.br/artigos/14260/os-denominados-efeitos-modificativos-em-embargos-de-declaracao-sao-mesmo-excepcionais>.

The article expressly concludes that modificative effects depend on the declaratory ruling; infringement of the earlier judgment is an **effect of the judgment**, not a separate effect generated simply by filing the motion. It also rejects a principal infringent request as the proper conceptual structure. Its notes cite earlier doctrine, including Nery and pre-2000 literature.

The same article also describes declaratory motions as a broad corrective mechanism and gives a merits example in which curing a defect changes the substantive result.

**Compared claims:** C1, C2, C3, C6.

**Classification:** `prior_art` for C2; `partial_prior_art` for C1 and C3; `prior_art` against C6's suggestion that CPC/2015 first supplied the consequence-not-autonomous-request architecture.

### 4.5 STJ line before our cutoff: “consequence necessary” was settled judicial vocabulary

**Representative primary records:**

- STJ, **EDcl no REsp 1.185.201/DF**, 5th Panel, decided **2011-08-18**, DJe **2011-10-03**: <https://www.lexml.gov.br/urn/urn:lex:br:superior.tribunal.justica;turma.5:acordao;resp:2011-08-18;1185201-1135689>;
- STJ, **EDcl no AgRg nos EDcl no AREsp 164.503/SC**, 3rd Panel, decided **2013-03-07**: <https://www.lexml.gov.br/urn/urn:lex:br:superior.tribunal.justica;turma.3:acordao;aresp:2013-03-07;164503-1253498>;
- STJ, **EDcl no AgRg nos EREsp 747.702/PR**, Corte Especial, DJe **2012-09-20**, repeatedly quoted by later STJ decisions.

These decisions use a stable formula: modificative/infringent effects are admissible when, once omission/contradiction/obscurity is cured, alteration of the decision arises as a **necessary consequence**; they are unavailable merely to obtain a new judgment without a qualifying defect.

**Compared claims:** C2, C4, C5.

**Classification:** `prior_art` for the necessary-consequence core of C2; `partial_prior_art` for C4 because the case law supplies the determinacy intuition but not Paper 1A's later explicit cognitive theory of unique determination versus generative cognition.

### 4.6 Talamini (2016): merits modification can be the normal function of embargos

**Work:** Eduardo Talamini, **“Embargos de declaração: efeitos no CPC/15”**, Migalhas, **2016-03-22**.

- URL: <https://www.migalhas.com.br/depeso/236300/embargos-de-declaracao-->.

Talamini's section is expressly titled **“Efeito infringente como consequência do normal emprego dos embargos.”** It explains that curing omission, contradiction, obscurity or material error can substantially alter the challenged decision. Its concrete example is unmistakably merits-based: a court initially grants a payment claim, omitted prescription, and on curing that omission may issue a merits judgment against the previously victorious plaintiff. Talamini emphasizes that this remains the **normal, typical function** of declaratory motions, while distinguishing it from pure merits rediscussion.

**Compared claims:** C1, C2, C5.

**Classification:** `prior_art` for C1's operative legal proposition and for C2's consequence-of-integration proposition; `partial_prior_art` for the combined C5 architecture.

**Material consequence:** Paper 1A can retain “mode, not object” as a useful explanatory slogan, but it should not present the underlying proposition — a genuine declaratory defect may concern the merits and its cure may change the merits result — as a new doctrinal discovery.

### 4.7 Rejection-implicit doctrine predates the C4 narrowing

**Representative source:** TSE, **ED-AgR-AI 10.353**, decided **2010-02-04**, DJe **2010-03-12**: <https://www.lexml.gov.br/urn/urn:lex:br:tribunal.superior.eleitoral;plenario:acordao;ed.agr.ai:2010-02-04;ai-10353>.

The TSE states that omissions capable of supporting declaratory motions concern issues submitted for decision except those already rejected explicitly or implicitly; embargos do not provide a new judgment of the cause.

**Compared claim:** C4.

**Classification:** `partial_prior_art` / `adjacent_prior_work`. It anticipates one of Paper 1A's filters — logically or implicitly rejected arguments are not genuine omissions — but does not supply the paper's exact unique-determination criterion or its recall-versus-generative cognition vocabulary.

## 5. Claim-level classification

| Claim | Cutoff | Result | Reason |
|---|---|---|---|
| C1 — mode, not object | 2026-05-10 15:01:02 UTC | `prior_art` for the operative proposition | Pre-cutoff doctrine, especially Talamini 2016, already treats merits omissions as ordinary curable defects and permits merits-result change when the defect is cured. The exact “mode not object” phrasing is a useful synthesis, not a materially new legal rule located in this audit. |
| C2 — modification as consequence | 2026-05-10 15:01:02 UTC | `prior_art` | Nery, Monteiro Neto, STJ and Talamini all state the consequence/necessary-consequence structure before our cutoff. |
| C3 — drafting consequence/no autonomous infringent request | 2026-05-10 15:01:02 UTC | `partial_prior_art` | Nery and Monteiro Neto already reject infringement as the principal request. The exact critique of the *subsidiary* formula and Paper 1A's replacement drafting clause were not located verbatim. |
| C4 — unique-determination cognitive boundary | 2026-06-24 10:13:33 UTC | `partial_prior_art` | “Necessary consequence” case law and rejection-implicit doctrine supply important pieces, but the exact explicit boundary `unique determination → recognitive/integrative; non-unique → potentially generative` was not located before cutoff. |
| C5 — combined architecture | mixed | `partial_prior_art` | Its main doctrinal components were established; the later cognitive taxonomy is the least-occupied part. |
| C6 — CPC/2015 as origin of the consequence architecture | 2026-05-10 15:01:02 UTC | material historical correction | The consequence-not-main-request architecture is publicly documented under CPC/1973 and in doctrine from at least the 2000s. CPC/2015 may strengthen or codify aspects of the structure, but it did not originate it. |

## 6. Material revision to the paper's present framing

This audit changes more than a novelty score.

### 6.1 §5.2 likely reverses Nery's actual position

Current §5.2 says a line represented by Nery Jr. treats modification as exceptional and **dependent on an express request**. The publicly verifiable quotations located in this run attribute to Nery the opposite proposition on request structure: infringement is not the main request and may only follow as consequence of granting embargos that cure a qualifying defect.

The safest correction is not to turn Nery into a blanket ally on every proposition — he still uses the language of exceptional infringent character — but to separate two questions:

1. **frequency/exceptionality:** Nery can call modificative effects exceptional;
2. **request structure:** the located Nery text says infringement is a consequence, not the principal reform request.

Those propositions can coexist. Paper 1A currently collapses them and should be revised before publication.

### 6.2 §3.2 / §5.4 overstate the break introduced by CPC/2015

Paper 1A is strongest when it says CPC/2015 gives textual support to a clean consequence structure. It is weakest when it suggests that this structure is a new solution to a CPC/1973 ambiguity. The pre-2015 doctrine and STJ line already articulated essentially the same model.

The defensible historical statement is narrower: CPC/2015 **expressly regulates procedural consequences of actual modification** and ties omission to art. 489, §1º, making the older integration logic easier to state from positive text. It did not create the idea that modification follows from curing the defect rather than functioning as an autonomous appeal request.

## 7. What remains plausibly distinctive

After removing occupied ground, the strongest residual is not C2. It is the later **cognitive boundary** developed through the adversarial rounds:

> when the tribunal's already-adopted commitments uniquely determine the omitted argument's outcome, curing the omission can be described as integrative completion without a new autonomous choice; when those commitments leave multiple outcomes open, the act is genuinely generative to that extent.

Pre-cutoff jurisprudence supplies “necessary consequence”, “premises necessarily infirmed” and implicit-rejection doctrines. Those are close enough that C4 is only `partial_prior_art`, not cleanly novel. But this run did **not** locate a prior Brazilian procedural source that turns those materials into the explicit unique-determination versus generative-cognition test used in the current §5.6.

A future empirical test should therefore focus on the distribution of real art. 489, §1º, IV omissions across:

1. logically determined / implicit-rejection cases;
2. uniquely determined but genuinely omitted cases;
3. direction-without-uniqueness cases;
4. fully generative omissions.

If classes 2 and 3 collapse empirically, the residual theory loses much of its value. If class 2 is stable and substantial, it is the paper's most defensible contribution after this audit.

## 8. Post-cutoff search

Searches through **2026-09-18** located many later judgments, explainers and practice materials repeating the longstanding formula that modification may arise as a logical/necessary consequence of curing a real defect. None located in this run materially reproduces the full later C4 cognitive taxonomy.

A page first published **2026-05-15**, five days after C1–C3's cutoff, also describes modification as a consequence of defect cure rather than an autonomous objective, but it cites older doctrine. It is therefore not treated as evidence of later independent convergence with Paper 1A; the underlying proposition was already prior art.

No candidate in this run met the threshold for `later_overlap`, `later_non_citing`, `later_citing`, or `later_derivative` with respect to the paper's residual C4 architecture. Absence of a candidate after these searches is only a bounded negative result.

## 9. Audit conclusion

The principal epistemic revision is straightforward:

- C2 is **not** a viable originality claim; its substance is long-standing Brazilian doctrine and case law.
- C1 is also occupied at the level of substantive legal proposition, though Paper 1A's “mode not object” formulation remains a useful pedagogical compression.
- C3 has a smaller residual in the exact drafting prescription, but the conceptual reason for not treating infringement as the main request predates us.
- C4 is the least occupied portion and should carry any originality discussion, with explicit acknowledgment of the older necessary-consequence and implicit-rejection lines.
- the paper's attribution of an express-request position to Nery should be checked and corrected; accessible sources repeatedly quote him for the opposite request structure.

The appropriate revision is therefore **not** “we discovered that effects infringentes are a consequence.” It is: **the paper systematizes a well-established integration/consequence doctrine, derives a cleaner CPC/2015 drafting practice from it, and proposes a narrower cognitive test for distinguishing integrative completion from genuinely generative merits cognition.**
