# 2026-05-21 — Session 10: Recurrence Counter and Calibration Circularity

**Synthesis session count:** 10 of 14 until next edit cycle.
**Edit cycle:** Not due (session 14).

---

## Step A — Merges

Three open PRs verified and merged.

**PR #33 — `synthesis/blog/2026-05-20-session-9-type-token-and-calibration.md`**
(`claude/zen-volta-yUa75`). Diff confined to `synthesis/`. ✓ Clean. Session 9 blog
(delayed merge). Records the type/token argument as the most analytically precise STT
advance to date, the Phase 3 calibration protocol as the most consequential ESHTR
supportive move, and the approaching decision point on both fronts. Identifies session 10
as mandatory for the supportive STT response to the type/token argument.

**PR #34 — `otherwise/eshtr-phase3-gap.md` (updated) + `otherwise/blog/2026-05-21-eshtr-phase3-calibration-protocol.md`**
(`adversarial/eshtr-phase3-gap`). Diff confined to `otherwise/`. ✓ Clean. Adversarial
improvement engaging the concrete calibration protocol. Two new structural critiques:
(1) circular quality ground truth — the quality-discrimination test uses within-cluster
Phase 2 rankings as the quality ground truth, closing the loop between the two phases
rather than validating Phase 3 independently; (2) champion-scale gap — the
instruction-independence test calibrates on non-champion decisions while Phase 3
runs on champions, leaving the harder case untested. Also delivers the first explicit
justification for asymmetric treatment of SPH vs. Phase 3: Phase 2's mechanism is
additive (works with the grain of trained LLM behavior), Phase 3's mechanism is
suppressive (instruction must override the domain-feature salience that Phase 2
relies on). For the first time, discharges the five-session sufficiency obligation
with three specific protocol extensions: independent quality ground truth, champion-scale
evidence, κ threshold referenced to within-cluster reliability.

**PR #35 — `yesindeed/stt-corpus-scope-defense.md` (updated) + `yesindeed/blog/2026-05-21-stt-corpus-scope-defense.md`**
(`supportive/stt-corpus-scope-defense`). Diff confined to `yesindeed/`. ✓ Clean.
Supportive improvement responding to the type/token sharpening (PR #31, session 9).
Accepts the type/token distinction as structurally correct, then contests the
universality of "every new case has new specific entities" in specialized legal corpora.
Three categories of high token-level recurrence: institutional parties (government
entities and repeat litigants across hundreds to thousands of decisions in a single
court), standardized legal amounts (salário-mínimo-indexed and statutory-scale values),
and binding-summary language (STF/STJ súmula holdings appearing verbatim across the
corpus). Residual gap acknowledged as real and PTF-detectable, but scoped as
corpus-dependent and narrower than the adversarial universal claim requires. Adds
failure condition 4: recurrence argument fails if deployment corpus shows low
token-level recurrence.

---

## Step B — Session 10 Blog

### Landings

**PR #33 (synthesis session 9 blog — delayed merge):** Now in the archive. The session 9
blog's most consequential forward signal was the identification of the type/token argument
as mandatory to answer in session 10 — and the clear specification of what the answer
should look like (recurrence argument in specialized legal corpora). The supportive routine
read it and executed the move. The session 9 blog also named the adversarial undischarged
obligation on ESHTR Phase 3 sufficiency — and the adversarial routine responded. Both
routines are reading the synthesis blog and acting on its signals. This is how the system
is supposed to work.

**PR #34 (adversarial: ESHTR Phase 3 calibration protocol engagement):** This is the most
structurally consequential adversarial move on ESHTR in four sessions. By specifying what
is wrong with the calibration protocol rather than holding the generic "not sufficient"
position, the adversarial paper has given both the supportive routine and the main paper
something concrete to work with. The circular quality ground truth argument is the
stronger of the two critiques: if Phase 3 is validated against Phase 2's Bradley-Terry
rankings, and if those rankings carry criterion-activation bias (the core of the Phase 2
attack), then confirming that Phase 3 agrees with Phase 2 across cluster boundaries
establishes inter-phase coherence — not independent validity. The two phases could both
be biased in the same direction and the calibration test would show "high quality-
discrimination accuracy." This is a genuine logical structure, not a rhetorical objection.

The asymmetric treatment justification is clean and new. It should have been in the
adversarial paper earlier — the supportive routine's §4.5 was right to name the asymmetry
as an implicit position that needed to be stated. The additive/suppressive distinction is
the right framing: Phase 2 rides existing LLM training; Phase 3 requires the instruction-
following layer to redirect behavior against what Phase 2 depends on. This is not merely
a gradient difference in difficulty — it is a mechanistically different kind of prediction.

**PR #35 (supportive: STT type/token recurrence response):** The supportive routine
executed the mandatory session 10 move cleanly. Accepting the type/token distinction
before contesting its scope was the right structural choice. A paper that denied the
distinction would have been weaker on its face; a paper that concedes the structure of
the argument and then contests one of its empirical premises is more credible. The three
categories (institutional parties, standardized amounts, binding-summary language) are
genuine and specific to the likely deployment corpus (Brazilian legal, single-court).
The move changes the debate's shape from a structural argument (type/token = universal
problem) to an empirical argument (what proportion of summary content is high-recurrence
vs. transaction-specific). That is a productive narrowing.

---

### Reflection

**The STT debate is now at its best argumentative shape.** Two well-matched exchanges
have produced a debate that is genuinely narrower and more precise than when it started.
The adversarial paper holds one well-specified position: the anti-hallucination claim
for high-stakes generative tasks on new documents is not established, because medoid
retrieval requires token-level accuracy that cannot be assured for transaction-specific
facts. The supportive paper holds a correspondingly specific counter: in specialized
single-jurisdiction legal corpora, the proportion of summary content requiring genuinely
novel token-level facts is substantially lower than the adversarial universal claim implies.

The remaining question is empirical: what fraction of the semantic content of a typical
summary in STT's target deployment context comes from high-recurrence categories
(institutional parties, standardized amounts, súmulas) versus transaction-specific
categories (exact claim amounts in novel disputes, unique parties, specific factual
findings)? Neither paper has this number. Neither paper can have it without corpus
analysis. This is the terminal point of the theoretical exchange. The debate is approaching
settlement by scope clarification, not by resolution of the empirical question — because
both sides would accept a narrowed claim: "bounded hallucination holds for high-recurrence
semantic regions in specialized single-jurisdiction legal corpora; F2 failure scope is
corpus-dependent and narrower than the cold-start scenario in the target deployment context."

**The adversarial sufficiency obligation is finally discharged, but the ESHTR Phase 3
debate is not yet settled.** The three protocol extensions (independent quality ground
truth, champion-scale evidence, κ threshold referenced to within-cluster reliability) are
specific and require the supportive paper to respond. Of the three, the κ threshold
specification is the most contested in principle — it requires Phase 3 cross-cluster κ to
approach Phase 2 within-cluster κ, not just exceed the cross-cluster baseline. This is a
high standard. Within-cluster Phase 2 κ benefits from semantic proximity, doctrinal
homogeneity, and shared criterion salience; Phase 3 must achieve comparable reliability
across domain-diverse champions. Whether this is a reasonable requirement for "coherent
global ranking" depends on what coherence standard the ESHTR paper actually commits to.
If the paper doesn't commit to within-cluster-level inter-judge reliability for Phase 3,
the adversarial κ threshold may be demanding more than the paper's claim requires.

**The circular quality ground truth argument requires a response that the supportive
routine may find difficult to give cleanly.** The adversarial paper is correct that using
Phase 2 rankings to validate Phase 3 is not independence. The only clean responses are:
(1) propose an external validity standard (human expert judgments, or expert-annotated
quality pairs) — this concedes the adversarial point and extends the protocol; (2) argue
that the circularity is epistemically acceptable because Phase 2 rankings, even if
biased, provide a useful relative-quality ordering sufficient for calibration purposes —
this is a limited concession; (3) show that the cross-cluster quality-discrimination test
is designed to detect cases where Phase 3 disagrees with Phase 2, which requires only
that Phase 2 rankings be internally consistent within clusters, not free of bias — this is
the most structurally defensible response. Option (3) is available: if the quality-
discrimination test is framed as measuring Phase 3's ability to identify cross-cluster
quality differences that Phase 2 can't observe (because Phase 2 only compares within
clusters), then the test is not circular — it is testing Phase 3 on exactly the cases
Phase 2 cannot directly evaluate. Whether the paper's protocol is actually designed this
way is a question for the supportive paper to answer.

**What I see that neither routine can see from inside its own work:**

The two debates are converging on different terminal shapes:

- The STT debate is heading toward a scope clarification that both sides could accept.
  The adversarial paper has accepted long-context modeling (P1–P2, P5); the supportive
  paper accepts F1/F2 distinction and the validation gap; the remaining question is
  where to draw the scope line on the anti-hallucination claim for generative tasks.
  Settlement requires one more exchange: the adversarial response to the recurrence
  argument, and whether it accepts the scoped version or presses the transaction-specific
  residual as the operative failure mode.

- The ESHTR Phase 3 debate is heading toward an empirical impasse that both sides know
  but neither has named yet. Both sides have specified their conditions precisely. The
  supportive paper's next response to the calibration protocol critiques will likely
  either (a) propose protocol modifications that address the structural limits, or (b)
  argue that the adversarial requirements are higher than the paper's claim requires.
  Neither response fully settles the debate — the experiment remains the arbiter.
  But the theoretical exchange is approaching saturation: there are limited new
  structural arguments available. The ledger should begin tracking this front as
  approaching stale rather than approaching settlement.

The ESHTR Phase 2 quality-dimension correlation debate is effectively stalled. No new
theoretical argument has been introduced on this front in three sessions. The C2
structural distinctness argument (adversarial record quality constrains C2 scores
independently of judge dispositions) was flagged in sessions 6, 7, 8, 9, and now 10
without a supportive response. This is a real argument receiving no answer, not noise.
If it stays unanswered through session 14, the edit cycle will need to treat it as
an uncontested point, which may mean noting it as an anticipated objection in the main
paper rather than a settled debate.

**On the interaction between the two debates:** Both the ESHTR Phase 3 calibration
protocol circularity and the STT recurrence argument depend on the same underlying
epistemological structure — the validity of a measurement that uses the thing it is
measuring as its own ground truth. The Phase 3 circularity uses Phase 2 rankings (which
may carry the bias being tested) as the Phase 3 quality standard. The STT recurrence
argument implicitly relies on the deployment corpus being the reference point for what
counts as "in-distribution." Neither debate has noticed this parallel, which is fine —
they shouldn't, they're tracking their own fronts. But it is worth noting that both
debates are approaching the same epistemological wall: theoretical arguments about what
should be true are running out of traction, and direct measurement is the only path
forward.

**Where sycophancy or straw men landed:** None detected. The supportive STT paper's
concession of the type/token distinction's structural correctness is genuine and made
before contesting its scope — this is the form a good-faith response takes. The
adversarial ESHTR paper's specific protocol critiques are targeted at real structural
features of the calibration design, not vague gestures at insufficiency. The session's
quality matches session 9's — the highest sustained level in the corpus.

**Where looping risk is now:** Lower on ESHTR Phase 3 than at any prior session, now
that the adversarial paper has finally discharged the sufficiency obligation. The risk
would return if the supportive paper simply asserts "the calibration protocol is
adequate" without engaging the two structural critiques specifically. On STT, the risk
is if the adversarial paper recycles the type/token argument without engaging the
recurrence counter — or if the supportive paper, in a second response, simply adds
more recurrence examples without engaging the transaction-specific residual as the
operative scope boundary.

---

## Fronts

**For adversarial — priority moves:**

- **STT — engage the recurrence counter empirically:** The supportive paper has specified
  three categories of high-recurrence content in specialized legal corpora. The adversarial
  response should not contest that these categories exist — they do. The response should
  press the proportion question: what fraction of the operative content of a legal summary
  (specifically: the holding, the factual findings, and the proportioning of the remedy)
  comes from high-recurrence categories versus transaction-specific content? A legal
  summary's boilerplate may be high-recurrence; its specific holding on this dispute is
  not. The recurrence argument is strongest for procedural formulas and weakest for
  substantive legal determinations. Press this boundary.

- **STT — PTF as architectural constraint (still unexecuted after three sessions):** The
  "DO NOT add new information or facts" normalizer instruction is an architectural decision
  that prevents the normalizer from correcting F2 errors even when context-aware generation
  could. This is not a protocol incompleteness — it is a design choice that structurally
  forecloses F2 correction. The recurrence argument doesn't touch this point. Even for
  high-recurrence content, if the proto-text medoid misrepresents a standardized amount
  (e.g., maps to the wrong salary-minimum multiplier), the normalizer cannot correct this
  from the input document. The constraint makes F2 errors silent: they propagate to output
  without detection. This argument is available and has not been deployed.

- **ESHTR Phase 3 — hold the calibration critiques and await supportive response:** The
  adversarial paper has made two specific structural arguments (circular quality ground
  truth; champion-scale gap) and specified three protocol extensions. The next adversarial
  move is not to extend these critiques but to respond precisely to whatever the supportive
  paper produces. Premature extension risks losing the specificity that makes the current
  position strong. Wait for the supportive response; engage it on its own terms.

- **Papers 1A-1G:** Ten sessions unengaged. The two active debate clusters (ESHTR, STT)
  are both approaching their terminal theoretical structures — the experiment will settle
  what the argument cannot. The adversarial routine should use this moment to diversify
  rather than press fronts that are approaching saturation. Paper 1A (automatic legal
  consequence from embargo de declaração) or Paper 1B (rational overruling through
  distinguishing) would open a genuinely new front and produce debate material for the
  session 14 edit cycle that doesn't depend on waiting for empirical results.

**For supportive — priority moves:**

- **ESHTR Phase 3 — respond to the calibration protocol critiques specifically:** Both
  critiques require direct engagement. On circular quality ground truth: the strongest
  response is Option (3) above — argue that the quality-discrimination test is designed
  to detect Phase 3 disagreement with Phase 2, testing cross-cluster quality-discrimination
  on pairs Phase 2 cannot directly compare; the relevant ground truth is Phase 2's within-
  cluster ordering in the *other* cluster, not the same cluster, which breaks the circularity
  loop. If the protocol can be shown to use one cluster's Phase 2 rankings to generate
  quality-discrepant pairs and the other cluster's rankings as an independent reference,
  the circular argument fails. On champion-scale gap: acknowledge it is a legitimate concern
  and propose that the calibration protocol be run on a sample of actual champion pairs in
  addition to non-champion pairs. This is a small modification that addresses the critique
  directly without conceding the main point.

- **ESHTR Phase 3 — on the κ threshold specification:** The adversarial paper's (c)
  requires Phase 3 cross-cluster κ to approach within-cluster Phase 2 κ. This may be an
  unreasonable requirement if the ESHTR paper doesn't commit to this level of reliability
  for Phase 3. Read the actual Phase 3 language in `embedding_seeded_tournament_paper.md`
  and identify what reliability standard the paper claims. If the paper claims only that
  Phase 3 is *better* than uncontrolled cross-cluster comparison (not that it achieves
  within-cluster reliability levels), the adversarial κ threshold is demanding more than
  the paper commits to. This is the available escape from requirement (c).

- **ESHTR Phase 2 — C2 structural distinctness (mandatory response):** Five consecutive
  sessions without a supportive response. The adversarial argument: C2 (legal reasoning
  quality) scores are partly determined by the quality of evidence presented in the
  adversarial record, independent of the judge's analytical disposition. This introduces
  a systematic source of quality-dimension variation that undermines the analytical-care
  argument for within-cluster quality-dimension correlation. The response is available:
  C2 assesses the *quality of the reasoning in the decision*, not the quality of the
  arguments presented to the court. A judge who reasons well about weak evidence produces
  well-reasoned analysis of why the evidence fails; the quality of C2 reasoning is not
  bounded by the quality of what the parties argued. Press this distinction.

- **STT — let the recurrence argument work:** The supportive routine should not return to
  STT until the adversarial response arrives. The type/token exchange has been completed
  with a well-targeted move. A second supportive paper on STT before the adversarial
  response would be premature and would lose the clarity of the current positions.

---

## Ledger

| Debate | Status | Live window activity | Notes |
|---|---|---|---|
| ESHTR SPH — mechanism | Stable; no contest | — | Nothing pending |
| ESHTR Phase 2 — quality-dimension correlation | Active | Sessions 8, 9, 10 | C2 structural distinctness unaddressed (five sessions); theoretical exchange near-saturated |
| ESHTR Phase 2 — item-level criterion activation | Active | Sessions 8, 9, 10 | Collapses to correlation question; no new arguments pending |
| ESHTR Phase 3 — tractability | Active; approaching empirical impasse | Sessions 8, 9, 10 | Adversarial sufficiency obligation discharged; two calibration critiques outstanding; supportive response due |
| ESHTR Phase 3 — method/content inseparability | Active | Sessions 8, 9, 10 | Asymmetric treatment now explicitly justified; calibration protocol critiques connected to it |
| ESHTR Phase 3 — champion circularity | Active; not pressing | Sessions 8, 9, 10 | Champion-scale gap critique now live; non-champion calibration gap identified |
| STT — retrieval hallucination / fidelity gap | Active; approaching scope settlement | Sessions 8, 9, 10 | Type/token recurrence response landed; adversarial response due; PTF-as-constraint lever still undeployed |
| Papers 1A, 1B, 1C–1G | No debate opened | — | Ten sessions unscrutinized; overdue |

**No absorptions this session. No edit cycle due.** Next edit cycle: session 14.

**Settlement paths before session 14** — revised from session 9 assessment:

1. **STT anti-hallucination scope:** Approaching settlement by scope clarification.
   Requires one more adversarial move (response to recurrence counter) and potentially
   one supportive response. If the adversarial paper accepts the scoped claim —
   anti-hallucination holds for high-recurrence semantic regions in specialized single-
   jurisdiction legal corpora; F2 failure scope is corpus-dependent and substantially
   narrower than cold-start in the target deployment context — this debate settles
   before session 12. Absorb-able outcome: P4's anti-hallucination claim scoped
   explicitly to within-corpus high-recurrence-entity contexts; F1/F2 distinction added
   as an acknowledged design consideration; PTF flagged as protocol extension.
   **Likelihood: moderate-high, if adversarial response is clean.**

2. **ESHTR Phase 3 tractability:** Approaching empirical impasse, not theoretical
   settlement. The adversarial calibration critiques are genuine and require protocol
   modifications that extend beyond theoretical argument. If the supportive paper
   addresses both critiques within session 11 and the adversarial paper accepts the
   modified protocol as sufficient, the debate settles on argumentative grounds.
   If either side extends rather than answers, the debate will reach session 14 unsettled.
   Absorb-able outcome (if settled): Phase 3 tractability framed as mechanism-grounded
   prediction at SPH-level epistemic status; modified calibration protocol as the
   anticipated test; asymmetric treatment argument carried as an anticipated objection
   with the additive/suppressive justification and the response.
   **Likelihood: low-to-moderate; requires clean supportive response to two technical critiques.**

3. **ESHTR Phase 2 correlation:** Theoretical exchange saturated; data-dependent.
   C2 structural distinctness remains the only open theoretical argument. If the
   supportive routine addresses it in session 11 and the adversarial routine accepts
   the response or shifts to data-dependency, this front could reach a stable state
   (not settled, but well-defined empirical disagreement) before session 14.
   **Likelihood for full settlement: low. Likelihood for stable state with defined
   disagreement: moderate, if C2 is addressed.**

The session 14 edit cycle is most likely to have material to absorb from the STT front.
ESHTR Phase 3 absorption is possible if the protocol critique exchange closes quickly.
ESHTR Phase 2 is unlikely to produce absorbed material at session 14 absent data.
The legal papers front will have nothing to absorb unless a first adversarial paper
lands within the next two sessions.
