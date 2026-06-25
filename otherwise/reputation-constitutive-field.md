# The Constitutive Field Problem: Why Cheaper Verification May Not Devalue Legal Reputational Capital

---

## 1. Thesis Attacked

"Reputação como Mecanismo de Coordenação no Sistema Jurídico" (Baldo, 2025; `paper1F_reputacao_sistema_juridico.md`) defends a two-part prediction about the Brazilian legal system:

> "A redução tecnológica do custo de verificação da qualidade argumentativa recalibra esse sistema em dois sentidos: desvaloriza proxies institucionais quando qualidade é verificável diretamente, e abre novo canal de construção de reputação para agentes antes excluídos do sistema."

The prediction has two components. First, when argumentative quality becomes directly verifiable at lower cost, institutional proxies (affiliation, win history, credentials, network) lose relative value as reputation-formation inputs. Second, agents previously excluded from the reputation network can build reputation through verified quality alone, democratizing access to the system. This attack targets the causal mechanism linking cheaper verification to proxy devaluation to democratization.

---

## 2. Faithful Reconstruction

The paper's argument is strongest when understood through its three-stage structure.

**Stage 1 (Informational diagnosis):** Argumentative quality in law is a credence good — expensive or impossible to verify even after consumption. A judge receiving a petition cannot cheaply verify whether it correctly identifies the *ratio decidendi* of the relevant precedent, whether a proposed distinction is genuine, or whether an omission weakens the fundamentação. This creates information asymmetry of the type Akerlof analyzed: buyers (decision-makers) who cannot distinguish quality from non-quality pay for expected quality; sellers (practitioners) of genuine quality cannot extract a premium; quality production incentives collapse.

**Stage 2 (Proxy mechanism):** The legal system avoids quality collapse by operating a distributed reputation network. Observable proxies — institutional affiliation, win history, credentials, professional network — function as screening devices: they correlate with quality without directly measuring it. Reputation, in the paper's framework, is "the decentralized price of argumentative quality — the mechanism through which information about quality propagates through the network without direct verification." The analysis correctly notes that proxies are imperfect and that agents with accumulated reputational capital have a structural interest in maintaining the informational opacity that makes proxies necessary.

**Stage 3 (Technology prediction):** When verification technology reduces the cost of direct quality assessment, the screening function of proxies diminishes. The argument follows the structure of information disclosure: when quality becomes visible, signals that substitute for quality visibility lose informational value. The paper integrates Kreps's repeated-game analysis by noting that reputation serves as a credible commitment device — but the paper's prediction is that cheaper verification reduces the need for the commitment device by making direct assessment possible, lowering the value of the proxy through which the commitment was built.

The paper's strongest version is its own: it does not claim proxies disappear but that their "peso relativo na formação de reputação diminui quando verificação direta se torna mais barata" — a partial, differential claim that is more defensible than a strong devaluation claim.

---

## 3. The Attack

The paper's mechanism contains a suppressed premise that neither its Akerlof framing nor its Bourdieu framing supports: that "argumentative quality" is an objective standard existing independently of the field's capital structure and accessible to verification technology.

### 3.1 The Constitutive Capital Problem

The paper draws on Bourdieu's concepts of symbolic capital and the legal field. In Bourdieu's framework, the legal field is not simply a market where quality is produced exogenously and then signaled. The field constitutes the standards through which quality is recognized: what counts as a sound argument, as genuine precedent distinction, as adequate *ratio* engagement, is determined in part by agents recognized as competent judges of these things — and recognition of competence is itself a function of capital distribution within the field. This is not circular in a vicious sense; it is how any knowledge field reproduces its standards. But it is structurally important.

The implication: verification technology trained on legal production would encode existing quality standards. The systems the paper's program proposes — formal verification pipelines, structured argument auditing — are calibrated against legal argumentation as it is produced and recognized in the current field. "Verified quality" would be "quality as recognized by the current field," which is quality structured by existing capital relations.

Under this reading, proxies would not devalue upon the introduction of verification technology. They would be embedded in the quality standard the technology verifies. An argument from a practitioner at a high-capital institution would receive a high quality score not because of institutional rent, but because the quality rubric was constructed from material that high-capital institutions produce and that the field's competent judges (themselves high-capital agents) recognize as quality. The technology would provide a cheaper window onto field-relative quality, not an independent window onto quality as such.

The force of this objection depends on whether the paper's verification mechanism is calibrated against an *exogenous* quality standard or a *field-relative* one. The paper describes verification in terms of "auditability" of "argumentative quality" and references the Lean 4 pipeline (Paper 2 of this series), which tests arguments for procedural validity under CPC 2015. A procedural-validity standard has more independence from capital relations than a peer-assessment standard — CPC 2015 is law, not field consensus. But even procedural validity is interpreted through field practice: what counts as adequate engagement with art. 489, §1º, VI is determined by existing jurisprudence, produced by high-capital tribunals, through interpretive moves that are themselves contested within the field.

The paper could respond by identifying an exogenous standard — a mathematical notion of argumentative validity, a statutory text read literally, a formal proof system — that would provide independent leverage against existing capital relations. But the paper does not make this claim. It describes verification technology as revealing quality that already exists in arguments, not as imposing an external standard. The Bourdieusian analysis the paper invokes implies that "quality that already exists in arguments" is not field-neutral.

### 3.2 The Signaling Persistence Problem

The paper cites Spence (1973) on job market signaling. The Spencean framework presents a structural difficulty the paper does not engage.

In a separating equilibrium under Spence's model, high-quality agents invest in costly signals to distinguish themselves from low-quality agents. The signal's value comes from two sources: (a) its correlation with quality, which provides information; and (b) its cost, which provides screening — it is more costly for low-quality agents to mimic the signal than for high-quality agents to produce it. The equilibrium can persist even when quality is partially observable, because the signal carries commitment value beyond its informational content.

In the legal context, institutional credentials and professional affiliations function as costly signals with both components. The informational component (proxy-as-quality-correlation) is what the paper's mechanism targets: cheaper verification substitutes for this component, reducing proxy value. But the commitment component survives cheaper verification.

The paper itself establishes, through Kreps, that legal reputation functions as a credible commitment in repeated games: the practitioner who built reputation through investment in institutional credentials has committed to the profession, to long-term relationship maintenance, and to reputational accountability — signals that cheap quality verification on a single argument cannot substitute. Direct verification of output quality reveals nothing about the investment the agent has made in the network of professional relationships and institutional accountability that makes future performance predictable. A new entrant with one verified high-quality argument has not demonstrated the commitment that decades of institutional investment signal.

This is not an objection to the existence of the information-substitution effect the paper predicts. It is an objection to the paper's implicit assumption that this effect dominates the equilibrium. In Kreps's framework, the value of commitment signals in repeated games is independent of whether the underlying quality is observable — it depends on whether the history of investment is observable, which it is (institutional affiliation, career trajectory, professional relationships are the investment record). Cheaper single-interaction quality verification does not substitute for this investment record.

A related consequence: when verification costs fall, practitioners may shift from observable proxies to other forms of costly commitment signals rather than abandoning costly signaling altogether. The equilibrium changes form without dissolving.

### 3.3 The Network Diffusion Problem

The paper's democratization prediction requires that verified quality signals propagate through the reputation network to agents with reputational authority (judges, senior lawyers, academic reviewers) without being filtered or amplified by existing capital holders. This requires three conditions the paper does not establish:

**(a) Legibility and access.** Verified quality scores must be accessible to decision-makers in formats they consult and trust. If quality verification tools are primarily used by practitioners and academics, but judges form reputational assessments through the channels described in the paper (petitions received, adversaries assessed, colleagues evaluated), then verified quality scores would reach judges only through the intermediation of practitioners — who are themselves differentially positioned in the reputation network.

**(b) Cross-interaction propagation.** Reputation in repeated games (Kreps) accumulates across interactions with many counter-parties. A single high-quality verified argument builds reputation with the specific judge who received it; propagating this to the broader network requires that other agents learn about the quality interaction. The paper describes the existing reputation network as operating through professional relationships and institutional channels. Verified quality signals would propagate through these same channels — channels that existing capital holders dominate, both as transmitters and as filters.

**(c) Absence of counter-signal investment.** High-capital agents facing verified quality competition from new entrants would have incentive to invest in counter-signals that reinforce their position: advocacy before verification bodies about what quality standards should measure, institutional affiliations that lend credibility to quality certifications, academic publications that frame quality criteria. The paper documents that high-capital agents resist recalibration through normative, cultural, and institutional channels. The same resistance mechanisms would shape what "verified quality" means, reducing the new entrant's ability to build reputation through a verification metric that existing capital holders influence.

---

## 4. Anticipated Reply

The most natural response to the constitutive capital argument is that it proves too much: if quality standards were entirely constituted by field capital, legal fields could never change, which contradicts historical evidence of legal field transformation (including the CPC 2015 itself, which the paper's series argues represented a genuine recalibration of what counts as adequate fundamentação). This response has force, and the constitutive capital objection should not be read as claiming quality is entirely field-constituted.

The narrower claim stands: the paper's specific mechanism (cheaper verification → proxy devaluation) requires verification technology to operate against an exogenous quality standard that provides independent traction against existing capital distributions. Field-transforming episodes in legal history have typically involved an external normative shock — legislation, constitutional amendment, international treaty — that imposed standards that existing capital holders could not unilaterally define. Technology that audits compliance with existing legal norms does not, by itself, constitute such a shock. It verifies quality-as-currently-understood, which is quality-as-currently-structured.

On signaling persistence: the anticipated reply would distinguish commitment signals (investment records) from quality signals (argument output), conceding that the former survive cheaper verification while arguing that the latter dominate reputation formation in the paper's model. The paper's own evidence, however, documents both dimensions: institutional affiliation functions partly as an investment record (commitment signal) and partly as a quality proxy (informational signal). Cheaper verification of output quality disrupts the informational component while leaving the commitment component intact. The relative weight of these components in legal reputation formation is an empirical question the paper does not resolve.

---

## 5. Scope of the Attack

This attack does not claim that technology has no effect on reputational capital in legal systems, that excluded agents cannot benefit from quality verification tools, or that the paper's general direction is wrong. The claim is bounded: the specific causal mechanism (cheaper verification → proxy devaluation → democratization) is underdetermined by the theoretical frameworks the paper invokes. The constitutive capital problem shows that verification technology trained on field production would encode existing capital relations into the quality standard it verifies. The signaling persistence problem shows that commitment-value proxies — which Kreps's analysis, which the paper invokes, implies are present in legal reputation — survive cheaper output verification. Together, they suggest the paper's mechanism operates less strongly, and less reliably in the democratizing direction, than predicted.

The attack is not a defense of the status quo. Opacity is costly; verification tools may produce genuine benefits. The objection is that the paper underestimates the structural stickiness of capital distribution in legal fields and does not identify the mechanism by which verified quality would propagate to reputational authority through channels that existing capital holders do not influence.

---

## 6. Surrender Conditions

The paper's thesis would survive this attack under the following conditions:

**(a) Exogenous quality standard.** The paper identifies a quality standard that is not constituted by existing field capital — for example, formal derivability under CPC 2015 interpreted textually, or logical validity under an explicit formal system — and shows that Brazilian legal verification technology would measure against this standard rather than against field-relative quality norms. The standard would need to be resistant to reinterpretation by existing capital holders.

**(b) Commitment signal separability.** The paper shows that Brazilian legal reputation proxies function primarily as informational signals (Akerlof) rather than commitment devices (Kreps-Spence), or that the commitment-value component of proxies is either empirically negligible or substitutable by verified quality accumulated across multiple interactions.

**(c) Independent diffusion mechanism.** The paper identifies a network diffusion mechanism through which verified quality signals reach reputational authority agents without being filtered by existing capital holders — for example, through institutionally independent publication channels, systematically collected outcome databases, or anonymized quality ratings by standardized rubrics that practitioners cannot influence.

If (a), (b), and (c) hold, the proxy-devaluation mechanism becomes substantially more plausible. In their absence, technology may improve the quality of legal argument production without disrupting the capital structure that determines whose arguments reach the reputational network's authoritative nodes.
