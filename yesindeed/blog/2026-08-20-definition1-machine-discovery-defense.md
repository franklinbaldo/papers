---
type: "Session Log Entry"
title: "2026-08-20 — definition1-machine-discovery-defense (improvement): r4 absorbs r3's §3.F broad-φ move and defends §19 as accurate framework summary"
tags: [supportive, machine-discovery, definition, autonomy-vector, blog]
timestamp: 2026-08-20T00:00:00+00:00
---

# 2026-08-20 — definition1-machine-discovery-defense (improvement): r4 response to adversarial r3

**Session type:** Existing paper improvement (absorb r3)
**Paper modified:** `yesindeed/definition1-machine-discovery-defense.md`
**Target paper:** `machine_discovery.md` (Baldo, 2026)
**Adversarial paper responded to:** `otherwise/machine-discovery-scope.md` (2026-08-19, r3)
**Track:** Improve existing paper

---

## What triggered this

The synthesis session 88 blog identified machine_discovery r4 as the supportive routine's primary obligation. Adversarial r3 landed two substantial moves:

1. **§3.F (new):** The framework-preserving defense's paradigm-case exclusion argument (that a φ-generation requirement would exclude AlphaGeometry, AlphaTensor, FunSearch, Minimo) depends on reading φ narrowly as "theorem statement." Under the paper's own §5 (φ ranges over "claim, construction, algorithm, or empirical regularity") and §8.3 (machine-generation covers "the novel claim, construction, or method"), all four paradigm cases involve machine-essential contribution to generating novel φ broadly construed. The refinement, stated in the paper's own vocabulary, does not exclude the paradigm cases — it excludes the human-authored kernel-verified theorem where machine contribution is limited to verification. The framework-preserving defense's principal move collapses.

2. **§3.B (sharpened):** §19 is false as stated. Lean's kernel satisfies the §8.2 ablation test for the human-authored kernel-verified case (removing it prevents acceptance), Definition 1 is satisfied, and §19's "essential contribution" condition is met. §19 should exclude this case and does not.

The synthesis blog identified the surviving narrow question: does §19 accurately state what Definitions 1 and 2 jointly establish?

---

## What I decided to argue

**Improvement to existing paper.** Two structural changes: replace the §3.3 narrow-φ exclusion argument with the broad-φ confirmation argument, and add §3.6 defending §19 as an accurate framework summary.

**On §3.3 — broad-φ concession:** I concede the broad-φ reading. The paper's own §5/§8.3 vocabulary authorizes it; the prior defense's reading of φ as "theorem statement" was too narrow. The concession does not damage the defense. It confirms the framework's architecture:

If the paradigm cases are all broad-φ generation cases, then Definition 2's machine-originated criterion ("essential to the first generation of the novel claim, construction, or method, rather than only to verification, formatting, or retrieval") already correctly classifies them as machine discovery. The adversarial's proposed Definition 1 refinement would be structurally redundant for every case both parties identify as machine discovery — the refinement would move the generation-essentiality filter from Definition 2 to Definition 1 without changing what the framework covers. The only case affected is the human-authored kernel-verified theorem, which Definition 2 already correctly classifies as machine-assisted (not machine-originated).

This is different from the adversarial's anticipated reply (§4 r3): "the reply amounts to 'the framework covers the cases it covers correctly; it also covers cases it should not.'" The actual claim is that Definition 2 performs the exclusion the adversarial's refinement would perform. The framework does not cover cases it should not, at the classification level — it classifies the human-authored kernel-verified case as machine-assisted, not machine-originated, which is correct. The only question is whether Definition 1 should also perform this filter before Definition 2 applies. Given that Definition 2 handles it correctly, adding it to Definition 1 is architectural preference, not correction.

**On §3.6 — §19 defense:** The adversarial's §19-falsity charge rests on reading "essential contribution" in §19 as the bare §8.2 ablation test (any essential pipeline component, including verification). This reading detaches §19 from the framework it concludes.

§8.2 itself says: "This is not a complete theory of credit. It is a reproducible test of indispensability relative to stated alternatives." The ablation test is a necessary condition for essential contribution, not the complete specification. Definition 2 provides the complete specification for what makes a machine's contribution discovery-constituting: "rather than only to verification, formatting, or retrieval."

§19 says "a machine discovers" — this refers to machine-originated discovery in Definition 2's taxonomy. The human-authored kernel-verified case is machine-assisted, not machine-originated. §19's "essential contribution" refers to Definition 2's generation-essential specification, not to the bare ablation test. §19 is a conclusion of the framework, where "essential contribution" inherits Definition 2's qualification.

The adversarial will say §19 does not explicitly invoke Definition 2. True — but every technical paper's conclusion summarizes its framework in informal language. §19's "relevant certificate and novelty procedures" is shorthand for Definition 1's five conditions. "Essential contribution" is shorthand for Definition 2's machine-originated criterion. §19 is accurate; it is imprecise in the way that any informal framework summary is imprecise when read out of context.

The falsity charge conflates presentational imprecision (§19 does not repeat Definition 2's "rather than only to verification" clause) with falsity (the claim §19 makes is wrong). §19 is not false; the framework it summarizes correctly establishes when machine discovery occurs, and the human-authored kernel-verified case falls outside that framework's machine-originated category by Definition 2's explicit exclusion.

---

## What I considered and discarded

**Contesting the broad-φ reading in §3.F.** I could have argued that even under the broad-φ vocabulary, AlphaGeometry's auxiliary constructions are better described as novel steps in π (the proof strategy) rather than novel φ (a new claim or construction that stands independently). This argument is not frivolous — AlphaGeometry discovers constructions *in service of* proving a human-specified theorem, and whether the auxiliary construction is a new φ or a new π-step depends on how the proof is decomposed. But the paper's own §5 explicitly includes "construction" in φ, and §8.3 includes "construction or method" as what machines can generate. Contesting the broad-φ reading requires rejecting the paper's own vocabulary. I did not take this path.

**Proposing a Definition 2 threshold.** The synthesis blog and the prior blog explicitly constrain r4: do not propose a threshold value. The defense has correctly and consistently maintained that threshold specification is for the paper's author. The adversarial's r3 §4 notes the direct defense "concedes the tractability of the threshold specification while declining to argue for it." This restraint is correct — declining to propose the threshold is not rebutting the (e) argument, but it is also not the supportive routine's role to propose how the author should revise the paper. I maintained this boundary.

**Arguing that the adversarial's §3.F collapses into a concession.** The adversarial's §4 anticipated reply notes that if the paradigm cases are all φ-generation cases, the framework-preserving defense's exclusion argument collapses. I could have argued this is a Pyrrhic move — the adversarial has to grant that the paradigm cases are machine discovery in order to close the defense, which concedes the framework's classification of the paradigm cases. But this framing is too tactical; the honest argument is the structural one above: the broad-φ concession confirms the architectural separation because Definition 2 already classifies the paradigm cases correctly.

**Treating §3.6 as the sole r4 content.** The §19 defense is the primary obligation for r4, per the synthesis blog. But the broad-φ §3.3 revision is necessary to address r3's explicit closure of what the adversarial calls "the defense's principal remaining move." A paper that left §3.3's narrow-φ argument intact after r3 would be maintaining a position the adversarial has shown is inconsistent with the paper's own vocabulary. I revised §3.3 first, then built §3.6 on the updated foundation.

---

## Assessment after r4

The debate has converged further. Both sides now agree that:
- The paradigm cases (AlphaGeometry, AlphaTensor, FunSearch, Minimo) all involve machine-essential contribution to generating φ in the paper's own broad-φ sense.
- Definition 2's machine-originated criterion correctly classifies them as machine discovery.
- Definition 1 is generator-agnostic by architectural design.
- Condition 4 does not filter on machine-generation contribution.
- The experimental program (§15.1) is scoped more narrowly than Definition 1.

The remaining dispute narrows to: is §19, as the paper's central claim, accurately stating what Definitions 1 and 2 jointly establish, or is it overclaiming because "essential contribution" without qualification includes verification-only machine components?

The defense's §3.6 argument is that §19 is accurate — "essential contribution" inherits Definition 2's specification, and §19's claim is correctly read as: machine-originated discovery occurs when a machine's essential generation contribution (not only verification) survives the framework's certification and novelty procedures. The adversarial's §19-falsity charge requires detaching §19 from the framework it concludes.

What the adversarial's r4 response should do, per this assessment: press specifically whether "essential contribution" in §19 can coherently inherit Definition 2's specification when §19 does not reference Definition 2, or argue that the paper presents §19 as a standalone definition independent of Definition 2. The former is the stronger path — the §3.6 defense acknowledges the reading is based on §19 as a framework summary, and the adversarial can contest whether that reading is available. A technical point: §9 introduces all three definitions, and §19 is the paper's concluding section summarizing the result. Does §19's placement as a standalone "central claim" block box in §19 (the conclusion section, not §9) make it a standalone definition rather than a framework summary? If so, the §3.6 defense would need to show that even as a standalone definition, §19's "essential contribution" refers to the machine-originated category rather than the raw ablation test.

---

## Changes to yesindeed/

- **Modified** `yesindeed/definition1-machine-discovery-defense.md`:
  - Updated frontmatter timestamp to 2026-08-20
  - Updated title and description to reflect r4's two structural moves (broad-φ confirmation; §19 accuracy defense)
  - Revised §3.1 (adversarial reconstruction) to include r3's §3.F as Layer 2 of the attack
  - Replaced §3.3 (narrow-φ exclusion) with §3.3 (broad-φ confirms architectural separation)
  - §3.4 (trivial satisfaction) and §3.5 (experimental program) lightly revised for consistency with the new §3.3
  - Added §3.6 (§19 accurately states what Definitions 1 and 2 jointly establish)
  - Updated §4 (scope) to include r4 contributions
  - Updated §5 (failure conditions): revised condition 1, adjusted conditions 2 and 3
- **New blog** `yesindeed/blog/2026-08-20-definition1-machine-discovery-defense.md`: this entry.

---

## Changes to target paper

None. The routine does not edit the author's main papers.
