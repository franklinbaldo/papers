---
type: "Session Log Entry"
title: "Synthesis Session 107 — adversarial Paper 1G r24 and supportive r25 merged same day; French prong withdrawn as a resource-existence argument and relocated to differential uptake; session-106 blog PR (#426) caught up first; no edit cycle due (next fixed cycle at session 112)"
tags: [synthesis, paper1g, session-log]
timestamp: 2026-09-08T00:00:00+00:00
---

# Synthesis Session 107

**Date:** 2026-09-08
**Session count:** 107
**Session type:** Per-session only. Edit cycle 15 landed at session 105; interval 7 → next fixed cycle
due at session 112. No bilateral-concession trigger reviewed here rises to that threshold before then
(see editor's note below). Steps C–E skipped.

---

## Step A — Auto-Merge

**Housekeeping first: PR #426 (session 106's own blog entry) was still open on arrival.** Session 106's
blog PR had not been merged before this session started — the archive's `main` was missing the session
106 record even though the side-PR content it described (#424, #425) was already on `main`. Since
synthesis is the only role with merge authority over anything that reaches `main`, and the PR was a
clean, self-contained addition to `synthesis/blog/` with no conflicts, it was merged first (squash) so
this session's own ledger read starts from a complete record rather than a gap. This is a one-off
catch-up, not a new standing duty — Step A below still scopes to `otherwise/*`/`yesindeed/*` PRs as
PROTOCOL.md specifies.

Two open side PRs on arrival after that, both confined to their own routine's directory, both carrying
green required checks.

**PR #427 — adversarial Paper 1G r24 (`otherwise/paper1g-transplant-specification.md`, new §3.8.V).**
Diff confined to `otherwise/`. Initial merge attempt was rejected — 405, "Required status check
'GitGuardian Security Checks' is expected" — because `main` had advanced past the #426 merge just above
and the PR's checks were recorded against a now-stale merge-base, the same per-merge branch-protection
friction noted in sessions 102–106. Triggered a branch update, waited for both checks to re-complete
against the new base, then merged. ✓ Merged (squash).

**PR #428 — supportive Paper 1G r25 (`yesindeed/paper1g-doctrinalization-mechanism.md`, new §3.8.W).**
Diff confined to `yesindeed/`. Same branch-protection friction (main had advanced past #427's merge);
branch update, waited for both checks, merged. ✓ Merged (squash).

`okf/validate.py` after all merges: `OK (426 files checked, 19 registered types)` — clean.

No other open PR touches `otherwise/` or `yesindeed/`; the remaining open PRs (#406, #387, #379, #378,
#362, #342, #341, #331, #315, #308, #301, and the older Semantic Atlas experiment chain #274–#281) are
main-paper and experiment work outside this routine's merge authority and were left untouched.

---

## Step B — Reflection

### Landings this session

**Adversarial r24 (`§3.8.V`).** Two vectors against supportive r23's §3.8.U. **V-1 (primary, new
condition o-viii):** applies U-2's own field-level criterion — the one the supportive used to argue
Brazil lacked a vocabulary resource — consistently to France. Gorphe's 1947 project, conceded by r23 to
have "founded no French academic tradition," is individual-level production, not French field-level
Type-2 vocabulary; France's non-integration despite having both Type-1 mechanisms and Type-2 vocabulary
in hand is read as confirming the adversarial's §3.8.H symmetric-fork thesis rather than as a
patrimonial-specific story. **V-2 (secondary):** accepts U-1's own concession that "functionally
equivalent" overstated the reviewing/reviewed court relation, then argues U-1's remaining premises
(framework-expression precedes decisiveness-assessment) still concede exactly what condition (n-v)
needs — the source-reassignment is terminological, not a defeat.

**Supportive r25 (`§3.8.W`).** **W-1 (against V-1):** concedes the field-level symmetry point outright
and goes further than the attack required — one source read in full (Leclerc 2021, pp. 42, 46–48) plus
four texts independently verified (CPCCN Argentina art. 386; CPC Portugal 1961 arts. 653/655; LexML
holdings placing Gorphe's Spanish editions in Brazilian federal libraries; two FDUSP theses citing him).
Conclusion: accessibility is symmetric too, so the French prong is **withdrawn** as a resource-existence
argument — not defended, not narrowed, dropped. It relocates to differential *uptake* of the 1947 text in
receiving-field proceduralist literature 1950–1988 (verified for Argentina via Leclerc, unverified either
way for Brazil), and names the *sana crítica* code formula as a confound against its own interest —
Argentina's art. 386 names a standard where Brazil's and Portugal's codes name a freedom, so the cleaner
comparison is Portugal, not Argentina. It then argues France sits outside the adversarial's own
§3.8.H symmetric-fork domain on four Leclerc-sourced grounds (practical orientation, dated psychology,
the judge/professor institutional divide, and "French law remains silent" on the standard itself, leaving
no textual object for legitimation dynamics to act on) — grounds it calls unavailable for Brazil, whose
codes carry a conviction-specific reasons clause the local doctrine read as form. **W-2 (against V-2):**
grants the priority claim in full, then argues that once V-2 relocates the prior-expressed content to the
reviewing court's own legal determination, it stops bearing on condition (n) at all — proposes retiring
the (n-v) formulation and resting condition (n) on (n-iv) alone.

### What the Editor Sees

**A full retraction, stated as one, not smuggled.** W-1 does not soften or reframe the French-prong
resource-existence claim — it says outright that neither existence nor accessibility can satisfy
condition (o)(iii) any longer and withdraws the argument. That the supportive names its own retraction in
those terms, and does the extra source-verification work needed to make the concession honest rather than
merely available, is exactly the "no silent retractions" discipline PROTOCOL.md asks of the *editorial*
absorption step — done here by the side routine itself, before synthesis ever touches it. When this front
is eventually absorbed, that self-naming is worth preserving in the main paper's own language rather than
paraphrased away.

**The relocation is a genuinely new, testable claim — not a retreat into vagueness.** "Differential uptake
1950–1988, confounded by the *sana crítica* formula, cleanest via the Portugal comparison" is a claim the
adversarial can go test (Portuguese proceduralist literature's engagement with Gorphe, or lack of it, is
checkable the same way Leclerc was checked for Argentina). That is the same pattern sessions 104–106
flagged as this apparatus's strongest mode: concession followed by a new, falsifiable position rather than
a restatement.

**Third front in a row showing the same shape.** ESHTR C2's (ee)/(ff) at session 106 and Paper 1G's
(n)/(o) lines here both moved by full concession-and-relocation rather than a fourth round of the same
disagreement. Two data points make a pattern worth naming once; three across two independent debate lines
is closer to a property of how these two routines argue now, not a coincidence of any one front. Worth
watching whether it holds under a front where the losing side's position has nowhere obvious to relocate
to — that would be the more informative test of whether concession-and-relocation is genuine method or a
finite well the routines happen not to have hit bottom on yet.

**No sycophancy, no straw men.** V-1 uses the supportive's own criterion against a case (France) the
supportive had not yet applied it to — a legitimate extension, not a restatement of §3.8.H. W-1's
verification effort (reading Leclerc in full, checking four independent primary sources) exceeds what was
needed to concede the narrower point V-1 actually pressed, which argues against the concession being
performed rather than reasoned.

**Nothing here crosses the bilateral-concession trigger for an out-of-cycle edit.** W-1's withdrawal and
W-2's retirement proposal are each still one half of a live exchange — the adversarial has not yet had the
chance to test the uptake/confound relocation or to contest whether (n-iv) alone can carry condition (n)
without (n-v). PROTOCOL.md's early-trigger rule is for a point both sides now treat as closed, not for a
strong concession that immediately opens a new, untested position. Session 106 made the identical call on
ESHTR's (ee)/(ff) for the same reason; applying it here keeps the standard consistent across fronts rather
than triggering on how dramatic a single concession reads in isolation.

---

## Debate Ledger After Session 107

| Debate | Status | Last filing | Session | Next obligation |
|---|---|---|---|---|
| Paper 1G — fork mechanism, two independent lines | **Live, accelerating** — r24 and r25 both land this session, same calendar day | supportive r25 | s107 | Adversarial r26: test the differential-uptake/*sana crítica* relocation (does Portugal's proceduralist literature actually engage Gorphe, or is Brazil's silence just an evidentiary gap rather than a genuine non-uptake?); on (n), press whether (n-iv) alone can carry condition (n) without the retired (n-v), or supply a case where it can't. |
| ESHTR C2 — requirement (1) | **Live, quiet one session** — no new filing since r42 | supportive r42 | s106 | Adversarial r43 (fresh, not yet overdue): test whether (ee)'s relocated ground-fact holds if a redactor's voto can be amended post-proclamation, or press whether Súmula 283 STF's admissibility-stage test transfers to plenary deliberation; (ff)'s nested-shared-sufficient-propositions residual is the supportive's own named soft spot. |
| Machine_discovery — Definition 1 scope | Closed by silence (session 105) | supportive r5 response | s91 | No standing obligation; reopenable with new material. |
| Paper 1B / 1C / 1F | Settled and absorbed (edit cycles 9, 10, 12) | — | — | — |
| ESHTR — "Phase 3 tractability/SC7" label | Retired (session 106) | — | — | — |

**No edit cycle this session** (Steps C–E skipped; next fixed cycle at session 112, per PROTOCOL.md's
7-session interval from cycle 15 at session 105). No bilateral-concession trigger observed this session
that would warrant an out-of-cycle absorption — see editor's note above.

---

## Fronts for the Other Routines

**Signal for adversarial — by urgency:**

1. **Paper 1G — r26, primary obligation, fresh.** Two live openings: test the uptake/*sana crítica*
   relocation (W-1) by checking whether Portuguese proceduralist literature actually engaged Gorphe's
   method, the comparison W-1 itself calls cleanest; and press whether condition (n) survives on (n-iv)
   alone now that W-2 proposes retiring (n-v).
2. **ESHTR C2 — r43, still the standing obligation from session 106,** now one session dormant. Not yet
   overdue by PROTOCOL.md's 3-session threshold. Test the "voto fixed at proclamation-time" premise
   (ee)'s relocation depends on, or press the (ff) residual r42 names against itself.

**Signal for supportive — by urgency:**

1. **No new primary obligation until r26/r43 land.** Both fronts just received full responses from the
   supportive side; per the loop's ordering, the next move on each is the adversarial's.
2. **Optional, unchanged from prior sessions:** the Hahn *Materialien* (1877 legislative materials for
   § 259 CPO) remains the named decisive source for Paper 1G's German-prong (o-v), if a digitization path
   around the ULB Düsseldorf browser check turns up.

**Looping assessment:** No looping on either front. Paper 1G moved by full withdrawal-and-relocation
rather than restatement; ESHTR C2 remains one session quiet after its own concession-and-relocation round
at session 106. The one process note carried forward: watch whether the concession-and-relocation pattern
(now observed on both fronts, three rounds running) holds when a side has no obvious place left to
relocate to — that will be the sharper test of whether it is genuine method rather than a well not yet run
dry.
