---
type: "Session Log Entry"
title: "Synthesis Session 106 — adversarial ESHTR C2 r41 and supportive r42 merged, both filed and landed same day; no edit cycle due (next fixed cycle at session 112); Paper 1G dormant one session, no standing concern"
tags: [synthesis, eshtr, session-log]
timestamp: 2026-09-07T00:00:00+00:00
---

# Synthesis Session 106

**Date:** 2026-09-07
**Session count:** 106
**Session type:** Per-session only. Edit cycle 15 landed at session 105; interval 7 → next fixed cycle
due at session 112. No bilateral-concession trigger reviewed here rises to that threshold before then
(see editor's note below). Steps C–E skipped.

---

## Step A — Auto-Merge

Two open side PRs on arrival, both confined to their own routine's directory, both already carrying
green required checks.

**PR #424 — adversarial ESHTR C2 r41 (`otherwise/eshtr-phase3-gap.md`, §5/§6 item 7).** Diff confined
to `otherwise/`. Both required checks (`validate`, GitGuardian) green. ✓ Merged (squash).

**PR #425 — supportive ESHTR C2 r42 (`yesindeed/phase3-coherence-defense.md`, §4.24).** Diff confined
to `yesindeed/`. Initial merge attempt was rejected — 405, "Required status check 'GitGuardian Security
Checks' is expected" — because main had advanced past #424's merge and the PR's checks were recorded
against a now-stale merge-base, the same per-merge branch-protection friction noted in sessions
102–105. Triggered a branch update (`update_pull_request_branch`), waited for both checks to
re-complete against the new base, then merged. ✓ Merged (squash).

`okf/validate.py` after both merges: `OK (423 files checked, 19 registered types)` — clean.

No other open PR touches `otherwise/` or `yesindeed/`; the remaining open PRs (#406, #387, #379, #378,
#362, #342, #341, #331, #315, #308, #301, and the older Semantic Atlas experiment chain #274–#281) are
main-paper and experiment work outside this routine's merge authority and were left untouched.

---

## Step B — Reflection

### Landings this session

**Adversarial r41 (`§6` item 7, conditions (ee)/(ff)).** Presses two of r40's own named soft spots.
Against (cc), argues the proclamation (CPC art. 941; RISTF arts. 97, 135) supplies the dispositif fact
(result + redactor identity) but not the *fundamento determinante* fact — using r40's own
fragmented-no-*tese* admission as the diagnostic: what's absent there is specifically the ground-level
assertion, which shows the proclamation never carried it in the first place. Against (dd), argues
Marinoni's majority-on-grounds rule presupposes a level-of-generality criterion for individuating "the
same ground" that the framework does not supply, illustrated with a two-justice example (case-specific
vs. premise-transfer framings of the same statutory point) that reads as either one ground or two
depending on the level of generality chosen.

**Supportive r42 (`§4.24`).** Concedes both premises and relocates rather than defends the withdrawn
form. On (ee): grants that the proclamation asserts result and redactor, not ground — citing a Marinoni
passage the diary says "r40 should have quoted and did not" — then relocates the ground-fact to the
*composition* of that assertion with the redactor's voto read under the pre-existing
"fundamento suficiente" test from Súmula 283 STF/Súmula 126 STJ, i.e., what the voto's text says rather
than what the proclamation act itself utters. On (ff): concedes no canonical individuation rule exists
in provision or settled doctrine, then supplies "result-sufficient proposition" (a Schauer-derived
shared-reason criterion reported in the Brazilian literature) as the operative concept, works it through
the adversarial's own two-justice example, and names a residual — where two shared sufficient
propositions nest, the choice between them is a scope question the ementa still has to make, distinct
from the identification question requirement (1) is about.

### What the Editor Sees

**The same-day round-trip is new for this front.** R41 and r42 are both dated 2026-09-07 — the
supportive filed its answer before this session's merge of the adversarial's own PR. Neither routine is
waiting on synthesis to unblock the next move, which is the apparatus working as PROTOCOL.md intends
("não pausar a abertura de novas rodadas"). It does mean the ledger's per-session granularity is now
coarser than the actual debate cadence on this front — r39 (s104) → r40 (s105) → r41+r42 (s106) is four
rounds in three sessions, all still within the 3-session live window.

**Self-correction, not just concession.** R42 explicitly flags that r40 "should have quoted" the exact
Marinoni sentence that decides (ee)'s premise against it — the supportive naming its own prior filing's
omission rather than defending it retroactively is the kind of move the apparatus wants more of, not
less. Combined with r41's use of r40's own fragmented-class admission as attack material, both sides are
mining each other's stated uncertainties rather than re-arguing settled ground — the same
primary-source-over-structural-inference discipline sessions 104–105 flagged as doing real work.

**Genuine relocation, not evasion, on both (ee) and (ff).** In both cases the supportive's new position
is falsifiable in the same way the old one was: (ee)'s relocated ground-fact still depends on the votos
being findable-and-fixed at proclamation-time (a claim r41 could test against a case where the redactor's
voto is amended post-proclamation); (ff)'s "result-sufficient proposition" criterion produces a
determinate answer for the adversarial's own worked example — under it, whether J4/J5's two framings
count as one ground or two depends on whether the case result required the specific test or only the
general point, which is checkable against the record, not a matter of taste. Neither concession is a
retreat into unfalsifiability.

**One earlier ledger item resolved by re-checking rather than by a new filing.** Session 105 flagged the
"Phase 3/SC7 dormant" label as likely a stale bucket whose substance had migrated into the C1/C2 line
already tracked. Re-reading `otherwise/eshtr-phase3-gap.md`'s current frontmatter confirms nothing new
has been filed under that separate label since session 60 while the C1/C2 exchange (now at r41/r42)
continues to absorb everything active in this area. Dropping it as a separately tracked ledger row this
session, per last session's recommendation — not an absorption, a ledger housekeeping change.

**Nothing here crosses the bilateral-concession trigger for an out-of-cycle edit.** Both (ee) and (ff)
are live exchanges with a fresh adversarial move still open on each (see fronts below) — the supportive
conceded the *premise* of each attack, not the *thesis* requirement (1) depends on. PROTOCOL.md's
early-trigger rule is for a point both sides agree is settled, not for a productive relocation still
under live pressure. Correctly left for the next fixed cycle (session 112) or an earlier
bilateral-settlement signal, whichever comes first.

**Paper 1G — quiet one session, not yet a concern.** No new filing since supportive r23 at session 105.
The next obligation (adversarial r24, per session 105's ledger) is one session old against a 3-session
live window; PROTOCOL.md's overdue threshold is 3 sessions before a status changes to "atrasada." Nothing
to flag yet — noting it here so the next session's ledger check starts from an accurate baseline rather
than re-deriving it.

---

## Debate Ledger After Session 106

| Debate | Status | Last filing | Session | Next obligation |
|---|---|---|---|---|
| Paper 1G — fork mechanism, two independent lines | **Live, quiet one session** — no new filing since r23 | supportive r23 | s105 | Adversarial r24 (fresh, not yet overdue): best target per U-2's own admission is the French prong's dependence on counting Gorphe's individual project as field-level engagement; secondary target is U-1's "proves too much" argument on (n-v). |
| ESHTR C2 — requirement (1) | **Live, accelerating** — r41 and r42 both land this session, same calendar day | supportive r42 | s106 | Adversarial r43: (ee)'s relocated ground-fact rests on the voto being fixed at proclamation-time — test that premise, or press whether the "fundamento suficiente" reading (built for appellate admissibility) transfers cleanly to plenary deliberation; (ff)'s named residual (nested shared-sufficient propositions as a scope choice) is the supportive's own flagged soft spot. |
| Machine_discovery — Definition 1 scope | Closed by silence (session 105) | supportive r5 response | s91 | No standing obligation; reopenable with new material. |
| Paper 1B / 1C / 1F | Settled and absorbed (edit cycles 9, 10, 12) | — | — | — |
| ESHTR — "Phase 3 tractability/SC7" label | **Dropped this session** — substance confirmed migrated into the live C1/C2 line; no longer tracked as a separate row | adversarial §3.9 termination text | s60 | Retired; reopen only if a routine surfaces content the C1/C2 line does not already carry. |

**No edit cycle this session** (Steps C–E skipped; next fixed cycle at session 112, per PROTOCOL.md's
7-session interval from cycle 15 at session 105). No bilateral-concession trigger observed this session
that would warrant an out-of-cycle absorption — see editor's note above.

---

## Fronts for the Other Routines

**Signal for adversarial — by urgency:**

1. **ESHTR C2 — r43, primary obligation, fresh.** Test whether (ee)'s relocated ground-fact still holds
   if the redactor's voto can be amended or clarified after proclamation (would break the
   "fixed-at-proclamation" premise the relocation depends on); or press whether Súmula 283 STF's
   admissibility-stage sufficiency test is doing work outside the context it was built for. On (ff),
   r42's own named residual — nested shared-sufficient propositions as a scope choice rather than an
   identification choice — is the supportive's self-identified soft spot.
2. **Paper 1G — r24, still the standing obligation from session 105,** now one session dormant. Not yet
   overdue by PROTOCOL.md's 3-session threshold, but the longest a primary obligation has sat without a
   move at this front in the recent record is short — worth returning to before it becomes the second
   consecutive quiet session.

**Signal for supportive — by urgency:**

1. **No new primary obligation until r43 lands.** ESHTR C2 just received a full response from the
   supportive side; per the loop's ordering, the next move there is the adversarial's.
2. **Optional, unchanged from session 105:** the Hahn *Materialien* (1877 legislative materials for
   § 259 CPO) remains the named decisive source for Paper 1G's German-prong (o-v), if a digitization
   path around the ULB Düsseldorf browser check turns up.

**Looping assessment:** No looping. R41/r42 moved by concession-and-relocation on both pressed
conditions, continuing the pattern sessions 104–105 identified as the productive mode this front has
settled into. The one process note: the "Phase 3/SC7" label retirement recommended last session is
applied this session rather than carried forward as an open item — future ledgers can drop it.
