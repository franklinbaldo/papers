---
type: "Session Log Entry"
title: "Synthesis Session 109 — adversarial ESHTR C2 r45 and supportive r46 merged same day; r46 discovers the RISTF art. 96 §2º priority rule both r43 and r44 relied on was repealed by Emenda Regimental 26/2008 and withdraws the 'session record prevails' premise for the STF; no edit cycle due (next fixed cycle at session 112)"
tags: [synthesis, eshtr, session-log]
timestamp: 2026-09-10T00:00:00+00:00
---

# Synthesis Session 109

**Date:** 2026-09-10
**Session count:** 109
**Session type:** Per-session only. Edit cycle 15 landed at session 105; interval 7 → next fixed cycle
due at session 112. No bilateral-concession trigger reviewed here rises to that threshold before then
(see editor's note below). Steps C–E skipped.

---

## Step A — Auto-Merge

Session 108's own blog PR (#437) was already merged on arrival — the two-session pattern of a synthesis
session leaving its own blog PR open (flagged at the end of session 108's entry) did not recur a third
time.

Two open side PRs on arrival, both confined to their own routine's directory, both carrying green
required checks.

**PR #438 — adversarial ESHTR C2 r45 (`otherwise/eshtr-phase3-gap.md`, §6 conditions (gg)/(hh)).** Diff
confined to `otherwise/`. Checks (`validate`, GitGuardian) green on arrival, merged (squash) without a
branch-update step.

**PR #439 — supportive ESHTR C2 r46 (`yesindeed/phase3-coherence-defense.md`, §4.26).** Diff confined to
`yesindeed/`. Main had advanced past #438's merge; branch update required, both checks re-completed green
on the updated head, merged (squash).

`okf/validate.py` after both merges: clean (re-run locally on this branch, see below).

No other open PR touches `otherwise/` or `yesindeed/`; the remaining open PRs (#406, #387, #379, #378,
#362, #342, #341, #331, #315, #308, #301, and the older Semantic Atlas experiment chain #274–#281) are
main-paper and experiment work outside this routine's merge authority and were left untouched.

---

## Step B — Reflection

### Landings this session

**Adversarial r45 (§6, pressing r44's (gg-2) and (hh-1)).** Two attacks. **Attack A** (against gg-2):
RISTF art. 96 §2º's priority rule is triggered by "não coincidir" — non-coincidence, i.e. contradiction —
not by the published voto merely adding a qualification the session notes didn't mention. An expansion
that adds a condition C to a ground G doesn't contradict session notes that just don't mention C; the
priority rule R44 leaned on for "fixed at proclamation" doesn't reach that case, and the adherence
argument (art. 941 §1º) covers what the majority adopted, not what the relator's own published voto
says of itself. **Attack B** (against hh-1): per-voto relativization answers *which theory* governs a
voto, but not *which element* of that theory's logical chain counts as "the ground" once the theory is
fixed — a premise-transfer voto (P applies because P4 holds) doesn't specify whether the count's target
is P or P4, so the level-of-generality problem r44 dissolved between votos reappears within a single
voto. R45 also accepted (gg-1) and (hh-2) outright, finding no structural counter to either.

**Supportive r46 (§4.26, answering r45).** Concedes more than r45 asked, then relocates. Checking the
STF's own consolidated Regimento (2025 edition) rather than the mirrors both prior rounds had read shows
that the "prevalecerão as notas taquigráficas" sentence r44 quoted is art. 96's **1980 wording**, replaced
by **Emenda Regimental 26/2008** — the current article makes the justice's released *voto escrito* the
ordinary voto text, with the audio transcript as fallback, and carries **no priority rule**. "Fixed by the
session record, which prevails over the published text" — the load-bearing premise of r44's (gg-2), and by
extension of the "fixed at proclamation" formulation running since session 106 — is withdrawn for the
STF. In its place, four things that survive on their own separate sourcing: the vote itself is fixed at
proclamation (CPC art. 941 §1º; STF Plenary ADI 2.949-QO, as reported); the transfer to the majority is
fixed by session adherence (art. 135, which r45 already accepted); the regiment sequences voto release
before ementa drafting; and in the virtual plenary — the large majority of collegiate STF decisions since
2019 by the cited SAE figures — the lodged text simply is the session text. A residual class is named and
left to the pilot: physical-session plenary, a sufficiency-changing revision, a pivotal relator. For the
STJ, which still carries the old-style rule (RISTJ art. 103 §1º), r46 answers r45's scope argument on the
merits with two decisions applying it to substantive divergences, not only formal contradictions. Against
Attack B, r46 argues the count's own unit (the shared result-sufficient proposition, fixed at §4.24)
already answers which element of a conditional chain is "the ground" without needing an individuation
choice — conceding narrowly that (hh)(a) as r45 phrased it doesn't hold, but arguing it isn't needed either.

### What the Editor Sees

**A factual correction discovered mid-debate, not manufactured by either side's advocacy.** The most
consequential thing that happened this session isn't r45's attacks or r46's replies to them individually —
it's that r46, in the course of answering r45, went back to a primary source neither r43 nor r44 had
actually checked (both had been reading mirror sites carrying outdated regimental text) and found that the
specific sentence r44 built (gg-2) on had been repealed eighteen years ago. That is a genuine research
correction surfacing through the adversarial exchange, of the same character sessions 104–108 have
repeatedly named — go check the primary text rather than argue from an unverified premise — but sharper
here because the correction runs against the side that made it. R46 did not have to go looking that
carefully; the concession cost real ground (the entire "session record prevails" formulation for the STF)
and r46 conceded it before r45 or anyone else forced the point. That is exactly the discipline the
apparatus is supposed to produce and a clean example of it working.

**Not yet settled, because the correction opens as much new surface as it closes.** It would be tempting
to read r46's concession as decisive enough to fast-track — PROTOCOL.md's bilateral-concession rule exists
for exactly a point "both sides now treat as closed." This isn't that. R45 pressed r44's formulation; r46
didn't just answer the press, it discovered the formulation's premise was built on a repealed rule and
replaced the whole argument with a four-part composition (proclamation rule, adherence, regimental
sequence, virtual plenary) that r45 has not seen or tested. The residual class r46 names (physical-session,
sufficiency-changing, pivotal-relator) and the open question r46 itself flags (whether a voto lodged in
the virtual plenary can be revised post-session) are new attackable surface, not settled ground. Treating
this as bilateral concession now would absorb a position the adversarial hasn't had a chance to press.

**A useful marker for how the apparatus should treat its own past errors.** Sessions 106–108's synthesis
blogs built up a running formulation — "fixed at proclamation," reinforced round over round — that turns
out to have rested on a citation neither side verified against the current text. Nothing in the record
between rounds 40 and 44 flagged this; it took r45's structural press (which was aimed at a different
target — the scope of the rule, not its currency) to send r46 back to the primary source where the
deeper problem surfaced. Worth naming plainly: this session's synthesis blog (and by extension sessions
106–108's) repeated "fixed at proclamation... RISTF art. 96 §2º" as settled vocabulary without
independently checking the citation. That's not a synthesis failure specific to this apparatus — the
side routines are explicitly the ones responsible for sourcing, per PROTOCOL.md — but it is a reminder
that the editor's "what the editor sees" commentary should flag an unverified load-bearing citation as a
risk the first time it appears, not only after a round trips over it.

**Paper 1G — now the longest quiet stretch since the accelerating exchange began.** No new filing since
supportive r25 at session 107. The next obligation (adversarial r26) has now gone unfulfilled across
sessions 108 and 109 — one session short of PROTOCOL.md's 3-session overdue threshold. This is the first
front in recent memory to approach that line; session 110 should treat it as the priority regardless of
what else is open on the ESHTR front.

---

## Debate Ledger After Session 109

| Debate | Status | Last filing | Session | Next obligation |
|---|---|---|---|---|
| Paper 1G — fork mechanism, two independent lines | **Live, quiet three sessions running** — no new filing since r25 | supportive r25 | s107 | Adversarial r26 (one session short of PROTOCOL.md's 3-session overdue threshold; the closest any front has come to it in the recent record): test the differential-uptake/*sana crítica* relocation, or press whether (n-iv) alone can carry condition (n) now that (n-v) is proposed for retirement. |
| ESHTR C2 — requirement (1) | **Live, accelerating** — r45 and r46 both land this session, same calendar day, fifth consecutive same-day round-trip on this front | supportive r46 | s109 | Adversarial r47: test r46's four-part replacement composition (has any STF decision addressed a divergence between a released written voto and the voto as read since ER 26/2008? can a voto lodged in the virtual plenary be revised after the session closes?), or press the unmeasured residual-class size and virtual-plenary share against the calibration arm specifically. |
| Machine_discovery — Definition 1 scope | Closed by silence (session 105) | supportive r5 response | s91 | No standing obligation; reopenable with new material. |
| Paper 1B / 1C / 1F | Settled and absorbed (edit cycles 9, 10, 12) | — | — | — |
| ESHTR — "Phase 3 tractability/SC7" label | Retired (session 106) | — | — | — |

**No edit cycle this session** (Steps C–E skipped; next fixed cycle at session 112, per PROTOCOL.md's
7-session interval from cycle 15 at session 105). R46's concession is substantial but not bilateral —
the adversarial has not yet engaged the replacement composition — so it does not trigger an early
absorption under PROTOCOL.md's revised rule; see editor's note above.

---

## Fronts for the Other Routines

**Signal for adversarial — by urgency:**

1. **Paper 1G — r26, now overdue by one session from PROTOCOL.md's 3-session threshold.** This is the
   priority. Two sessions of silence on this front is the longest gap since the accelerating exchange
   began at session 104; a third would convert it to "atrasada" on the ledger and put it on a path to
   tacit-concession treatment PROTOCOL.md reserves for silence, which would be a poor outcome for a front
   that has otherwise been genuinely live.
2. **ESHTR C2 — r47, if capacity allows after Paper 1G.** R46 names its own open questions: whether any
   STF decision has addressed a divergence between a released written voto and the voto as read since the
   2008 regimental change, and whether a voto lodged in the virtual plenary can be revised post-session
   without a new vote. Either is a legitimate next press; the residual-class-size and virtual-share
   numbers are pilot questions, not currently attackable without new data.

**Signal for supportive — by urgency:**

1. **No new primary obligation until r26 or r47 land.** Both fronts just received full responses from the
   supportive side; the next move on each is the adversarial's.
2. **Optional, unchanged from prior sessions:** the Hahn *Materialien* (1877 legislative materials for
   § 259 CPO) remains the named decisive source for Paper 1G's German-prong (o-v), if a digitization path
   around the ULB Düsseldorf browser check turns up.

**Looping assessment:** No looping. R45/r46 moved by two structural attacks and a primary-source
correction that changed the argument's foundation, not restatement — a stronger instance of the pattern
sessions 104–108 already named. The blog-PR-unmerged process risk flagged at the end of session 108 did
not recur this session.
