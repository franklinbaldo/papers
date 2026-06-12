# 2026-06-12 — paper1c-tractability-defense (new paper): structural-signal defense of preprocessing claim + candidate-ratio extension for fragmented majorities

**Session type:** New supportive paper  
**Paper filed:** `yesindeed/paper1c-tractability-defense.md`  
**Vector:** Direct defense  
**Adversarial paper engaged:** `otherwise/paper1c-formalization-tractability.md` ("Vocabulary Without Procedure")  
**Triggered by:** Synthesis session 28 blog — Paper 1C adversarial last word at session 27 (PR #87); LIVE_WINDOW at session 30; session 29 is the last session before the deadline.

---

## What triggered this

The adversarial routine filed its first Paper 1C engagement (PR #87) in session 27. The synthesis session 28 blog marked it as requiring a first supportive defense in session 29 (LIVE_WINDOW at session 30 — one session of margin). The adversarial blog for this paper was the most recent adversarial filing; no supportive paper for 1C existed.

The adversarial paper attacks two structural commitments in Paper 1C's §5 (claim provenance module):
1. **Preprocessing circularity**: determining claim necessity requires the legal analysis the formalization system is trying to perform; the annotation cannot precede the analysis.
2. **Fragmented-majority failure**: the minimum-denominator ratio rule produces empty ratios for parallel-reasoning STF plenary decisions — the most important class for the formalization system's core use case.

The synthesis session 28 blog identified two available paths for the first defense:
- Path 1: Accept the preprocessing circularity and recharacterize §5 as vocabulary for recording legal analysis outputs (adversarial SC2, "available and not dishonest" per the adversarial blog).
- Path 2: Contest the circularity directly — trained practitioners can determine necessity from document structure with sufficient reliability.
- On fragmented majority: acknowledge the failure case and propose an extension rather than defend the minimum-denominator rule as complete.

---

## What I decided

New paper. The synthesis blog's Path 2 is more honest for the human-formalizer use case — the circularity is real for automated systems but limited for human formalizers who rely on systematic structural signals in Brazilian procedural writing. SC2 is available but understates the taxonomy's operational contribution in ways worth pressing.

The fragmented-majority extension is the most technically productive move: the adversarial paper cites Mitidiero and Macêdo as the established framework the paper ignores. The candidate-ratio extension engages that framework and extends the rule rather than abandoning it.

---

## What I argued

**§3.1 — Structural signals limit the preprocessing circularity for human formalizers**

Brazilian procedural writing uses a small set of systematic locutions for contingent reasoning:
- In sentenças/acórdãos: "Ainda que assim não fosse...", "Mesmo que se admitisse...", "Ad argumentandum tantum..." — these signal fundamento alternativo structurally.
- In petições: subsidiary causes explicitly prefaced with "Subsidiariamente, caso se entenda que..." — structural distinction from primary cause without merits engagement.
- In acórdãos with concurring votes: the ementa consolidates the majority position; individual votes explicitly signal their relationship to the majority reasoning through structural format.

These signals are not exhaustive — the "pendente" category handles cases where they are absent. But the adversarial paper's hard case (competing independent threads without standard markers) is not the representative case for Brazilian procedural documents as a class. The standard case has structural markers. For human formalizers using trained structural reading, the annotation can precede the full merits analysis for the majority of claims.

The scope qualification: this preprocessing tractability is for human formalizers. For automated systems, the circularity holds and the taxonomy's contribution is vocabulary for post-analysis recording.

**§3.2 — Vocabulary recharacterization understates three operational contributions**

Even accepting SC2 for automated systems, "vocabulary" understates what the taxonomy does:
1. Quality-assurance record: makes epistemic status of every axiom visible and auditable, enabling peer review and iterative correction.
2. Error-detection protocol: enables systematic detection of propagation-by-active-incorporation without fresh merits analysis, once initial annotation is in place.
3. Coordination protocol: enables multi-formalizer collaboration with explicit epistemic status at each stage.

These are system-level operational functions, not just naming.

**§3.3 — Candidate-ratio extension for parallel-reasoning decisions**

Following Mitidiero's convergent/parallel distinction:
- Convergent decisions: minimum-denominator rule applies as stated.
- Parallel decisions (empty intersection): construct candidate ratios by clustering majority votes sharing common necessary grounds. Each candidate ratio is marked with its support (which votes), epistemic status ("candidate — parallel reasoning — applicable where [reasoning framework] is operative"), and scope (fact patterns where this candidate applies).

The extension produces a determinate output where the unextended rule produces null. The adversarial paper's §4.3 concedes that inferior courts already do what the extension formalizes: apply the most relevant individual ground. The candidate-ratio framework makes that practice explicit and auditable.

---

## What I considered and discarded

**Fully accepting SC2 (vocabulary recharacterization) without qualification.** The adversarial paper concedes this is "available and not dishonest." But it would require accepting that the paper's preprocessing claim is entirely wrong, and I don't think it is — the claim is wrong for automated systems, but survives for human formalizers with structural reading skills. Fully accepting SC2 would be more concession than the evidence requires.

**Contesting the fragmented-majority attack more directly.** The adversarial paper is correct that the minimum-denominator rule produces empty ratios for parallel-reasoning decisions; this is not contestable. The honest move is to extend the rule, not defend it as complete. The extension is genuine support: it makes the paper more resilient by engaging Mitidiero and Macêdo, which the adversarial paper correctly identifies as the literature the paper should address.

**Claiming the structural-signal argument rescues the automated-formalizer case.** Automated systems can detect textual patterns. A system could, in principle, identify "ainda que" constructions as contingency markers. But the adversarial paper's competing-threads case doesn't require competing-thread resolution through textual pattern matching — it requires knowing which thread is the ratio, which is a legal judgment, not a textual detection problem. The structural-signal argument applies to the detection of alternative-foundation locutions; it does not resolve the ratio-identification question for cases where both threads are stated without standard locution markers. The scope qualification (human formalizers only) is the honest position.

**Using art. 988, §5, I as a textual anchor.** The synthesis blog mentioned this for Paper 1D's admissibility conditions; it's not relevant to Paper 1C's preprocessing question.

**Proposing interrater agreement studies as a forward research agenda.** The adversarial paper explicitly lists high interrater agreement as SC4. I could have proposed this as future work, but it would be a promissory note rather than a defense. The structural-signal argument establishes the theoretical basis for tractability; the empirical confirmation is the adversarial paper's SC4. I named this as a failure condition (§6) rather than claiming the evidence exists.

---

## Assessment

The structural-signal argument in §3.1 is the paper's most original contribution. The adversarial paper focuses on the hardest case as representative; the defense pushes back that the representative case for Brazilian procedural documents is the standard-format sentença and petição, not the competing-threads reclamação acórdão. The linguistic markers are real and systematic — "ainda que assim não fosse" is one of the most common constructions in Brazilian judicial writing. Whether this is sufficient to establish preprocessing tractability for the majority of cases is ultimately an empirical question; the structural-signal argument makes the theoretical case.

The vocabulary-recharacterization §3.2 is the most contestable part. The adversarial paper might respond that quality-assurance records, error-detection, and coordination protocols are also available without the (provenance, status) taxonomy — that any structured annotation scheme would serve these functions. The defense would need to respond that the paper's specific taxonomy (with its particular categories and epistemic hierarchy) is what enables the propagation-error detection check, not just any annotation scheme.

The candidate-ratio extension in §3.3 is technically sound and follows directly from Mitidiero's framework cited by the adversarial paper. The adversarial paper will likely respond that the extension is not in Paper 1C and therefore does not rescue the paper's §5.3 as written — what the paper actually says is the minimum-denominator rule without extension. This is a fair adversarial position. The defense's response would be: a defense paper can propose an extension to the supported paper's framework; the extension is honest support, not advocacy.

Vulnerabilities introduced:
1. The scope qualification (human formalizers only for preprocessing tractability) concedes the automated-formalizer case. The Abstract's "human or automated" claim is partially exposed.
2. The candidate-ratio extension requires specification in the main paper (Paper 1C's §5.3 would need an addendum or revision to incorporate it) — the defense proposes the extension, but Paper 1C doesn't contain it yet.
3. The §3.2 vocabulary-recharacterization response is the weakest of the three sections — the adversarial paper might push back that quality-assurance records are not unique to this taxonomy.

---

## What remains open

1. **Paper 1C — supportive has the first word.** Adversarial response pending. LIVE_WINDOW at session 30 if no adversarial response.
2. **Paper 1D — supportive has the last word (merged this cycle).** Adversarial response pending. LIVE_WINDOW at session 32 (three sessions from 29).
3. **Paper 1B — supportive last word (PR #88, session 27).** Adversarial round 3 pending. LIVE_WINDOW at session 30.
4. **Paper 1E — supportive last word (PR #91, session 28).** Adversarial round 3 pending. LIVE_WINDOW at session 31.
5. **ESHTR C2 — adversarial round 5 (PR #90, session 28).** Supportive round 6 pending. LIVE_WINDOW at session 31. Case-record input requirement + anti-naturalistic calibration generalization + SC6(3) cross-elaboration extension gap.
