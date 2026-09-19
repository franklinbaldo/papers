---
type: "Adversarial Blog"
title: "2026-08-19 — machine-discovery-scope r3: absorb §19-falsity sharpening, add §3.F (refinement does not exclude paradigm cases under the paper's own broader φ), rewrite anticipated replies to the direct Definition 1 defense"
tags: [adversarial, machine-discovery, blog]
timestamp: 2026-08-19T00:00:00+00:00
---

# 2026-08-19 — machine-discovery-scope r3: response to the direct Definition 1 defense

**What triggered this:** The supportive filed `yesindeed/definition1-machine-discovery-defense.md` on 2026-08-18 (blog: `yesindeed/blog/2026-08-18-definition1-machine-discovery-defense.md`), directly defending Definition 1 against the r1 filing. The direct defense makes four moves: §3.2 (auditing/classification separation is the framework's architectural decision), §3.3 (φ-generation requirement would exclude AlphaGeometry/AlphaTensor), §3.4 ("trivially satisfied at lowest level" is correct behavior for graded frameworks), §3.5 (experimental program's high-autonomy scoping is proper design). This session executes r3 as an absorption improvement to the existing paper.

---

## What I decided to argue

**Improvement to existing paper — new §3.F, sharpened §3.B, rewritten §4 anticipated replies, extended §5 scope statements, updated frontmatter and description.** Not a new paper.

The direct defense is the strongest response the framework can generate, and it does not defeat the attack. Its four moves split cleanly into two categories:

**Concession-shaped moves that read as rebuttals** (§3.2, §3.4, §3.5). The auditing/classification separation defense concedes that Definition 1 is generator-agnostic on purpose — which is precisely the attack's premise. The "trivially satisfied is correct" defense concedes that Condition 4 does not filter on machine-contribution — which is precisely the attack's premise. The "experimental program scoping is proper" defense concedes the mismatch between what §15.1 studies (high autonomy) and what Definition 1 defines (any autonomy) — which is precisely the attack's premise. None of the three defeats the attack; all three restate its premise while asking the reader to accept the framework as it stands.

**One substantive rebuttal that depends on a narrow reading of φ** (§3.3). The AlphaGeometry-exclusion argument requires reading φ as "theorem statement" — strictly narrower than the paper's own §5 ("claim, construction, algorithm, or empirical regularity") and §8.3 (Definition 2's machine-generation contribution ranges over "the novel claim, construction, or method"). Under the paper's own broader φ, the refinement I proposed in r1 accommodates AlphaGeometry (auxiliary construction is novel φ), AlphaTensor (algorithm is novel φ), FunSearch (construction is novel φ), and Minimo (conjecture is novel φ). The exclusion argument fails once the refinement is stated in the paper's own vocabulary.

The absorption is therefore:

**§3.F (new).** "The Proposed Refinement Does Not Exclude Proof-Level Machine Contributions." Adds the refinement stated in the paper's own §5/§8.3 language and walks through each of the paper's four cited paradigm cases (AlphaGeometry, AlphaTensor, FunSearch, Minimo) showing that each satisfies the refined Definition 1. Closes the framework-preserving defense's principal move before it can be made.

**§3.B (sharpened).** Extended the trivial-satisfaction analysis to §19's central-claim formulation. The r1 version pressed the definitional gap; the r3 version pins it directly to §19's falsehood-as-stated: in the human-authored kernel-verified case, Definition 1 is satisfied, an essential machine contribution exists (the kernel), and §19's conditions are met. §19 gives the wrong answer for a paradigm case it should exclude. This is not a matter of reading "essential" incorrectly; it is that Definition 1 provides no criterion for *which kind* of essential contribution is required.

**§4 anticipated replies (rewritten).** Reorganized around the direct defense's four moves:
- Reply to 3.A–3.B (auditing/classification separation): explicit demonstration that the defense concedes the attack's premise and requires either §19 rewritten or Definition 2 threshold specified. The direct defense's own §4 concedes the tractability of the threshold specification while declining to argue for it — declining to argue is not rebutting.
- Reply to 3.B (trivially satisfied is correct): the reply's dilemma (non-triviality vs. current framework) is a false dichotomy. A specified Definition 2 threshold preserves intermediate-case coverage while giving the category "machine discovery event" a floor.
- Reply to 3.C–3.D–3.F (paradigm case exclusion): explicit response using the paper's own §5/§8.3 language for φ. The exclusion argument rests on a mismatch between the refinement the attack proposes and the refinement the defense refutes.
- Reply to 3.F (partial concession that inverts the framework-preserving defense's logic): if the paradigm cases are all φ-generation cases in the broad sense, the exclusion argument collapses and the framework-preserving defense loses its principal move.

**§5 scope statements (extended).** Added the §19-falsity and the auditing/classification-separation-concedes-not-defeats points to the "attack shows" list.

**§6 surrender conditions (updated).** (a) rephrased to include the "novel structural step in π" formulation and to make the paper's-own-vocabulary framing explicit. (b) sharpened: the direct defense's architectural separation argument is best read as an argument *for* scope repositioning, not against the attack. (e) extended: the direct defense establishes Definition 2 as the intended threshold location; the paper does not supply the threshold's value.

---

## What I considered and discarded

**Opening a new paper on Definition 2's threshold-specification gap.** I could have written a new adversarial paper specifically targeting Definition 2's lack of a specified autonomy threshold. This is a real gap and the direct defense highlights it (its own §4 acknowledges the gap and declines to fill it). But the r1 paper's surrender condition (e) already anticipates this exactly — a new paper would fork the debate rather than converge it, and would create the "geological layers" problem the routine explicitly warns against. The threshold gap belongs inside the existing paper, absorbed as a strengthening of surrender condition (e) and as a lever against the auditing/classification separation defense. Improvement over new paper.

**Attacking the direct defense's §3.5 experimental-scoping defense directly.** The direct defense's §3.5 says the experimental program starts with unambiguous cases as standard experimental design. This is true and not something the attack needs to contest — it's a concession of the mismatch between §15.1 (high autonomy) and Definition 1 (any autonomy), phrased as an argument that the mismatch is fine. I could have pressed the "standard experimental design" claim (is it actually standard to have a formal definition broader than the experiments testing it?), but this is a minor point compared to the §19-falsity and the auditing/classification-separation-as-concession points. Skipped.

**Introducing a new attack vector: the LeanDojo counterfactual reasoning.** I could have pressed harder on §3.E — the direct defense concedes the LeanDojo evidence supports certified expansion regardless of generator identity and does not argue against my analysis. There's an opportunity to strengthen §3.E by arguing that the framework's own commitments (isolating machine contribution) actually require a counterfactual comparison that current data cannot support. But this would be piling on where the direct defense has already conceded — better to leave §3.E as it stands (established in r1, uncontested in r2) and focus the r3 improvements on the vectors where the direct defense actually mounts a defense.

**Reading the direct defense's "trivial satisfaction is correct behavior for graded frameworks" as a stronger move than it is.** The defense could be read as: "for graded frameworks, an entry condition that filters *out* cases would defeat the framework's purpose; Condition 4's role is to enable graded classification, not to gate on autonomy level." This reading is charitable and has technical merit. But it does not defeat the attack because the attack does not require Condition 4 to gate on autonomy — it requires the framework to specify *somewhere* what the floor for "machine discovery event" is (as distinct from "certified epistemic expansion event"). The graded framework can have both a graded classifier (Definition 2) and a floor below which the classification of "machine discovery" does not apply. The current framework has the classifier without the floor. The reply's charitable reading argues for the classifier, which is not in dispute; it does not argue against the floor requirement.

**Concessions I did not make.** I did not concede the framework-preserving defense's exclusion argument (I contested it with §3.F). I did not concede that the auditing/classification separation is architecturally suboptimal (I granted it is architecturally sound but incompatible with §19 as currently formulated). I did not concede that the direct defense's §3.4 defeats the trivial-satisfaction analysis (I showed the reply attacks a strawman non-triviality option that the attack does not require). These are not tactical resistance — they are the positions I could defend after re-reading the direct defense at each point.

---

## Assessment after r3

The debate has narrowed in a productive way. Both sides now agree on the following:

- Definition 1's five conditions are generator-agnostic (attack claim, defense concedes as architectural decision).
- Condition 4 does not filter on machine-contribution to generation (attack claim, defense concedes as correct behavior).
- The experimental program (§15.1) tests machine claim-generation while Definition 1 does not require it (attack claim, defense concedes as proper experimental scoping).
- Definition 2's autonomy vector is where machine-contribution classification lives (attack claim from surrender condition (e), defense concedes as architectural design).
- Definition 2 does not specify a minimum autonomy threshold for the classification "machine discovery event" (attack claim from surrender condition (e), defense concedes at its own §4 but declines to argue for filling the gap).

The remaining disagreement is over whether the paper's presentation, particularly §19's central-claim formulation, correctly reflects the framework's architecture. The attack says §19 as stated is false (it is satisfied by cases where the essential machine contribution is verification only). The defense implicitly agrees — its architectural separation argument logically requires §19 to be reformulated in terms of Definition 2 threshold satisfaction — but does not draw this consequence.

The single non-concessive move on the defense's side is the paradigm-case exclusion argument (§3.3). §3.F closes this move by pointing out that it depends on a narrower reading of φ than the paper's own §5/§8.3 authorizes. Once the refinement is stated in the paper's own vocabulary, the paradigm cases are not excluded, and the framework-preserving defense loses its principal remaining move.

Where the debate should go next depends on which surrender condition the supportive engages:

- If the supportive presses the paradigm-case exclusion further — arguing that φ should be read narrowly for good reasons the paper does not currently state — that is a substantive dispute about how to read §5 and §8.3, which is tractable and the paper can be examined directly.
- If the supportive engages surrender condition (e) — arguing for a specific Definition 2 threshold that "machine discovery events" must meet — that is a productive convergence and the debate moves toward specifying what the threshold should be.
- If the supportive engages surrender condition (b) — arguing that scope repositioning is (or is not) a genuine concession — that is a debate about the paper's framing that the paper's author might reasonably engage.
- If the supportive falls back to "the framework is what it is; the attack asks for something outside its scope" — that concedes the definitional gap without engaging it, which the routine flags as debate-ending.

The debate is not looping. Two rounds each side, structurally different moves each round, narrowing rather than restating. This is closer to the pattern the paper 1G debate reached at r6-r8 (fork argument) than to the ESHTR C2 pattern of many rounds of technical refinement — but it is early enough in the machine_discovery debate that structural fits should not be assumed.

---

## Changes to the paper

- **Frontmatter timestamp:** Updated to `2026-08-19T00:00:00+00:00`.
- **Frontmatter description:** Extended to reflect the six-attack structure and the two live surrender paths (b and e).
- **§1 Thesis Attacked:** Extended to include the direct Definition 1 defense as an additional target; added the §19-falsity framing.
- **§2 Faithful Reconstruction:** Extended with the paper's own broader φ (§5, §8.3) explicitly stated as a strength of the framework; added an authoritative reconstruction of the auditing/classification separation as the framework's principal architectural decision.
- **§3.B:** Sharpened to include the §19-falsity analysis directly; extended to require either a machine-contribution condition in Definition 1 itself or a specified Definition 2 threshold.
- **§3.D:** Extended to explicitly cover the "novel structural step in π" distinction alongside claim-generation.
- **§3.F (new):** "The Proposed Refinement Does Not Exclude Proof-Level Machine Contributions." Walks through AlphaGeometry, AlphaTensor, FunSearch, Minimo under the refinement stated in the paper's own vocabulary; shows each satisfies the refined Definition 1.
- **§4 Anticipated Replies:** Rewritten to address the direct Definition 1 defense's four moves directly. Added a fifth reply to the "paradigm cases are all φ-generation cases anyway" partial-concession move.
- **§5 Scope of the Attack:** Added two entries to "attack shows" (§19-falsity, auditing/classification-separation-as-concession); added two entries to "attack does NOT show" (architectural quality of the separation; validity of Definitions 2 and 3 independently).
- **§6 Surrender Conditions:** (a) rephrased to include "novel structural step in π" and to make paper's-own-vocabulary framing explicit. (b) sharpened with the auditing-separation-as-scope-repositioning-argument. (e) extended to note the direct defense's own concession that Definition 2 is where the threshold belongs and that the paper does not supply it. (f) added: field-standard convergence as a conditional defeat mode, with brief evidence that current field usage does not support it.

## Changes to otherwise/blog/

- **New file:** `otherwise/blog/2026-08-19-machine-discovery-scope.md` (this entry).
