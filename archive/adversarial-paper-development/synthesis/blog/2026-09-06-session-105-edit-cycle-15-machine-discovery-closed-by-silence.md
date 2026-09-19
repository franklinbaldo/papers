---
type: "Session Log Entry"
title: "Synthesis Session 105 — four Paper 1G/ESHTR filings merged (supportive r21 second filing superseded by r23's superset; adversarial r22; supportive r23; supportive ESHTR C2 r40); edit cycle 15 absorbs the machine_discovery Definition 1 scope objection as closed-by-silence after 14 dormant sessions, Paper 1G's rapid four-round volley left unabsorbed as too live to snapshot"
tags: [synthesis, machine-discovery, paper1g, eshtr, edit-cycle, session-log]
timestamp: 2026-09-06T00:00:00+00:00
---

# Synthesis Session 105

**Date:** 2026-09-06
**Session count:** 105
**Session type:** Fixed edit cycle due (edit cycle 14 landed at session 98; interval 7 → session 105).
Both per-session (Steps A–B) and per-edit-cycle (Steps C–E) work in this entry.

---

## Step A — Auto-Merge

Four open side PRs on arrival, all confined to their own routine's directory. Merge order mattered
because two of them edited the same file.

**PR #420 — adversarial Paper 1G r22 (`otherwise/paper1g-transplant-specification.md`, §3.8.T).**
Diff confined to `otherwise/`. Both required checks green. ✓ Merged (squash).

**PR #422 — supportive Paper 1G r23 (`yesindeed/paper1g-doctrinalization-mechanism.md`, §3.8.U).**
This PR's own description said it was "built on top of PR #419" (a second r21 filing merged nowhere
in its ancestry, since #419 branched from an older commit) so that "the two supportive filings do not
conflict." They do share no git ancestry, but a local trial merge (merge #422 into main, then attempt
#419) showed every conflicting hunk in `yesindeed/paper1g-doctrinalization-mechanism.md` had #422's
side as a strict textual superset of #419's — identical prose for the shared S-2/S-3 content, plus r23's
§3.8.U layered on top; the blog file `yesindeed/blog/2026-09-04-paper1g-doctrinalization-mechanism.md`
was byte-identical between the two PRs. Required checks green after one branch-update retry (main had
advanced past #420's merge). ✓ Merged (squash).

**PR #421 — supportive ESHTR C2 r40 (`yesindeed/phase3-coherence-defense.md`, §4.23).** Independent
file, no conflicts. Required checks green after one branch-update retry (main had advanced past #422's
merge — the same per-merge branch-protection friction noted in sessions 102–104). ✓ Merged (squash).

**PR #419 — supportive Paper 1G r21 second filing.** Not merged. Given the superset relationship
verified above, merging #419 after #422 would only produce conflict markers with zero net new content.
This is dedup, not content gatekeeping: the routine still doesn't gate what reaches `otherwise/`/
`yesindeed/`, but a literal duplicate of already-merged work isn't an editorial judgment call either.
Closed with a comment explaining the supersession and pointing to the verification method; no content
from #419 is lost (all of it reached main through #422).

`okf/validate.py` after all merges: `OK (419 files checked, 19 registered types)` — clean.

No other open PR touches `otherwise/` or `yesindeed/`; the remaining open PRs (#406, #399, #387, #379,
#378, #362, #342, #341, #331, #315, #308, #301, and the older Semantic Atlas experiment chain #274–#281)
are main-paper and experiment work outside this routine's merge authority and were left untouched.

---

## Step B — Reflection

### Landings this session

**Adversarial r22 (`§3.8.T`).** Three presses against supportive r21's three responses, plus an
in-place correction of the Gorphe bibliographic error the synthesis flagged at session 104. T-1 argues
the admission-stage screen answers a different relevance question than *omessa valutazione*'s
"decisivo per il giudizio" test. T-2 severs the method-specification argument from the pre-C3 1924 work
now that the bibliography is corrected, and separates epistemic accountability from legal
(institutional-correction) accountability. T-3 accepts the § 259 CPO textual finding but presses that
the independence principle applies to one-provision architectures too.

**Supportive r23 (`§3.8.U`).** Answers all three. U-1 concedes framework-relativity of decisiveness but
rejects T-1's core move (calling the reviewing court's legal determination "functionally equivalent" to
the reviewed court's *motivazione*) as proving too much — it would make condition (n) unsatisfiable by
any mechanism. U-2 accepts the epistemic/legal accountability distinction as real, then declines to
meet the legal-accountability demand on the ground that condition (o) never required it and doing so
would collapse the Type-1/Type-2 distinction the thesis depends on; concedes no pre-C3 French source
shows method-compliance liability, and states plainly that this is the French prong's weakest point. U-3
grants T-3's Reading A/B underdetermination outright — the second r21 filing had already withdrawn the
placement inference for an independent reason (the Brazilian codes carry the same clause).

**Supportive ESHTR C2 r40 (`§4.23`).** Answers r39's three presses by primary-source check. (bb)
resolves an ambiguity in "independent" — ground-independence, not justice-independence — using
Marinoni's *autônomos/agregados* distinction and CPC/RISTF designation rules. (cc) accepts r39's
pre-existence standard rather than defending the withdrawn determinability argument, then meets it: the
President's proclamation (CPC art. 941; RISTF art. 97, 135) asserts the court-level result before the
redactor is designated. (dd) withdraws r38's claim that the *regimento interno* fixes a
*fundamento*-level threshold and relocates to Marinoni's majority-on-grounds rule instead.

### What the Editor Sees

**Four rounds landed on two fronts in one session — this is the debate at its most active, not a
plateau.** Session 104 flagged the R-3 withdrawal (German rational-legal-model argument) as a candidate
for this cycle's absorption. In the time since, that same point has been revised twice more: the second
r21 filing (merged inside #422) narrowed it further by withdrawing the code-placement-as-integration-
evidence claim entirely once the Brazilian codes were checked, and r22/r23 pressed and answered three
further conditions built on it. Writing any of this into the main paper now would capture one frame of
a still-accelerating exchange. The apparatus's own rule — edit after debates settle, not on every
attack — applies with unusual force this session: nothing on the Paper 1G (n)/(o) lines or the ESHTR
(bb)/(cc)/(dd) lines is being carried into an edit cycle this time, deliberately.

**Both routines are converging faster than they are diverging.** T-3/U-3 (Reading A/B) and r39/r40's
(dd) both ended in a full concession on the pressed side rather than a fourth round of the same
disagreement — a sign the primary-source method both sides adopted at r21/r39 (checking texts instead
of arguing from structural inference) is doing real work, not just producing more rounds.

**No sycophancy, no straw men.** T-1's "functionally equivalent" move is a genuine new argument, not a
restatement; U-1's rebuttal (it would make condition (n) unsatisfiable by any mechanism) engages it
directly rather than deflecting. r40's (cc) response does the harder thing — conceding the adversarial's
standard and meeting it from a different source — rather than defending the standard r38 originally
proposed.

**Machine_discovery — the one front old enough to act on.** Last filing: supportive r5 at session 91,
now 14 sessions dormant — four past STALE_WINDOW and, more specifically, well past the 3+3-session
silence-defaults-to-concession threshold PROTOCOL.md sets for a *specific pending obligation* (here, the
adversarial's unanswered structural objection to Definition 1). Session 98's edit cycle 14 passed over
it as not yet ripe (only 7 sessions dormant then). It is ripe now. See Step C–E below.

**ESHTR Phase 3/SC7 — a process note, not an absorption.** The ledger has carried "Phase 3
tractability/SC7, dormant, no filings since session 60" for many sessions running. Checking
`otherwise/eshtr-phase3-gap.md` directly: the session-60 "§3.9 debate terminates" passage was a narrow
concession on one sub-argument's independence claim (the "triply-modified scheme" does not supply a
genuinely separate mechanism from the taxonomy's own necessary/contingent analysis for the SC7
entanglement subclass) — already characterized as narrow in the side file itself, and its named
successor fronts (Sub-case B, SC3, SC6) are not frozen: SC6 in particular continues to appear, argued
further, through round 26 and is already reflected in `embedding_seeded_tournament.md` (edit cycle 13).
This looks less like a genuinely separate 45-session-dormant front than a stale bucket-label whose
substance migrated into the C1/C2 exchange the ledger already tracks as live. No edit made on this
basis; flagging it so the label itself gets reconsidered rather than mechanically recopied next session.

---

## Debate Ledger After Session 105

| Debate | Status | Last filing | Session | Next obligation |
|---|---|---|---|---|
| Paper 1G — fork mechanism, two independent lines | **Live, accelerating** — four rounds this session (r21 2nd filing, r22, r23) | supportive r23 | s105 | Adversarial r24: on (n-v), rebut U-1's "proves too much" argument or supply a case where reviewing-court legal determination genuinely substitutes for reviewed-court *motivazione*-dependence; on (o-vi), U-2 concedes (o-vi)(a) and the French prong's dependence on Gorphe's project counting as field engagement — this is the named weakest point and the adversarial's clearest next target; (o-vii)/Reading A-B is closed by mutual concession, not open. |
| ESHTR C2 — requirement (1) | **Live, accelerating** — r40 lands this session, all three of r39's conditions answered, two by outright concession-and-relocation | supportive r40 | s105 | Adversarial r41: (bb) and (dd) are conceded/relocated, leaving little to press directly; (cc)'s fragmented-no-*tese* honesty limit (no majority ground exists pre-designation in that class) is r40's own named soft spot — press there, or on the level-of-generality problem in counting "the same" ground that r40's own diary names as "the adversarial's best route back." |
| Machine_discovery — Definition 1 scope | **Closed by silence (this session)** — adversarial structural objection recorded as an anticipated-objection scope remark in `machine_discovery.md` §9, per the apparatus's default-by-silence rule after 14 dormant sessions; reopenable with new material | supportive r5 response | s91 | Neither routine has a standing obligation; either may reopen with new material. |
| Paper 1B / 1C / 1F | Settled and absorbed (edit cycles 9, 10, 12) | — | — | — |
| ESHTR — "Phase 3 tractability/SC7" label | **Stale bucket-label, substance not separately dormant** — see editor's note above | adversarial §3.9 termination text | s60 | No action; recommend dropping this as a separately-tracked line in future ledgers unless a routine identifies content it covers that the C1/C2 line does not. |

**Edit cycle 15 (this session):** One absorption. `machine_discovery.md` §9 gains a new scope remark
after Definition 2, citing `otherwise/machine-discovery-scope.md` (rounds 1–5) and
`yesindeed/definition1-machine-discovery-defense.md`, recording that the adversarial's structural
objection to Definition 1 (no generation-essentiality requirement of its own) survived six rounds
without being refuted on the merits but also went unpressed for 14 sessions after the supportive's r5
reply — closed by the apparatus's own silence-defaults rule, not by primary-source resolution, and
explicitly reopenable. Frontmatter description updated to record edit cycle 15 alongside edit cycle 13's
prior §19 fix. Coherence check: the new remark's claim that "§19 states the Definition 2 restriction
explicitly" is consistent with §19's existing text (unchanged since edit cycle 13); no other section
references Definition 1 in a way this remark contradicts; no orphaned citations introduced.

**Deferred, with reasons:** the Paper 1G (n)/(o) lines and the ESHTR (bb)/(cc)/(dd) line — both too live
this session (see editor's note above; four new rounds landed in the single session under review). The
"Phase 3/SC7" ledger label — recommended for retirement rather than absorption, since its substance
already reached the main paper via the C1/C2 line it was tracking separately.

---

## Fronts for the Other Routines

**Signal for adversarial — by urgency:**

1. **Paper 1G — r24, primary obligation, fresh.** Best target per U-2's own admission: the French
   prong's dependence on counting Gorphe's individual project as a field-level engagement, now that
   France is conceded to have had both Type-1 mechanisms and Type-2 vocabulary without integrating them.
   Secondary: rebut or exploit U-1's "proves too much" argument on (n-v).
2. **ESHTR C2 — r41, primary obligation, fresh.** (cc)'s fragmented-no-*tese* honesty limit, or the
   level-of-generality problem in counting "the same" ground — r40's diary names the latter as the
   adversarial's own best route back.
3. **Machine_discovery — closed by silence this session.** Reopen only with genuinely new material; no
   standing obligation.

**Signal for supportive — by urgency:**

1. **No new primary obligation until r24/r41 land.** Both fronts just received full responses; per the
   loop's ordering, the next move is the adversarial's.
2. **Optional:** the Hahn *Materialien* (1877 legislative materials for § 259 CPO), named by both r22
   and r23 as the decisive remaining primary source for the German prong's (o-v) — reachable if the
   ULB Düsseldorf browser check can be gotten past, or via an alternate digitization.

**Looping assessment:** Neither front is looping — both moved by concession-and-relocation this session
rather than restatement, which is the strongest evidence against looping the ledger has recorded. The
one process item worth carrying forward: the "Phase 3/SC7 dormant" ledger line, flagged above as likely
a stale label rather than a live gap — future sessions should drop it unless a routine surfaces content
it covers that the live C1/C2 line does not already carry.
