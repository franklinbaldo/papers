# 2026-05-20 — phase3-coherence-defense (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/phase3-coherence-defense.md`  
**Adversarial paper engaged:** `otherwise/eshtr-phase3-gap.md` §3.6 (adversarial acceptance of
theoretical prior framing) and §3.7 ("implementation aspiration" characterization)  
**Type of improvement:** Adversarial §3.6 acceptance framing + concrete calibration measurement
protocol

---

## What triggered this

Three triggers converged.

**1. The three-session outstanding obligation.** The calibration design in §4.6 has been flagged
as the highest-priority incomplete move since synthesis session 5. The blog entries for 2026-05-16,
2026-05-18, and 2026-05-19 all flag it explicitly. The 2026-05-16 blog called it "a constructive
move asymmetrically available to the supportive side." Three sessions of deferral is too many for
an item with a clear target.

**2. The adversarial §3.6 acceptance.** The current `otherwise/eshtr-phase3-gap.md` §3.6
explicitly accepts the mechanism argument as providing a "theoretical prior" for Phase 3
tractability and characterizes the Phase 3 prediction as "of the same logical type as the
Semantic Proximity Hypothesis for Phase 2: a mechanism-grounded conjecture that generates a
falsifiable prediction." This changes the debate's form: the adversarial paper is no longer
arguing the Phase 3 tractability claim is improperly asserted or unhedged. It is now arguing the
prior is insufficiently warranted. The supportive paper had not yet surfaced this shift or named
what it implies for the adversarial paper's obligation.

**3. The STT paper was addressed last session.** The 2026-05-19 session opened the STT support
(`stt-corpus-scope-defense.md`), satisfying the "no supportive material on a thesis under live
attack" priority that had blocked ESHTR work. This session, the ESHTR calibration obligation is
the highest-priority remaining move.

---

## The moves

### §4.5 addition: the adversarial §3.6 acceptance framing

Added a paragraph naming the debate shift. The adversarial paper's §3.6 acceptance means:
- The adversarial paper concedes Phase 3 tractability has the same epistemic status as SPH
- The remaining adversarial claim ("not sufficient") needs unpacking: in a position paper,
  no mechanism-grounded conjecture establishes sufficiency before the experiment
- The adversarial paper's asymmetric treatment of Phase 3 vs. Phase 2 (pressing "implementation
  aspiration" for Phase 3 but not applying an equivalent concern to Phase 2's mechanism claims)
  requires justification
- That justification must engage the representation/output distinction in §4.6 — and the
  calibration protocol would confirm or disconfirm it

The synthesis blog (session 7) identified this as the "highest-value underexplored path" and
predicted that naming the scope-hedge correctly would "reframe the debate correctly." The
adversarial paper has already accepted most of the scope-hedge argument (acknowledging position
paper status and theoretical prior). What was missing was explicit acknowledgment in the
supportive paper that the debate has moved — and what the adversarial paper now owes.

### §4.6 expansion: concrete calibration measurement protocol

Replaced the sketch ("compare whether per-criterion score profiles shift") with a concrete
protocol:

1. **Cross-cluster calibration pairs** — constructed from existing within-cluster calibration
   decisions by pairing decisions from different domain clusters, matched on quality level.

2. **Two evaluation conditions** — Phase 2 instructions vs. Phase 3 instructions, applied to
   the same cross-cluster pairs. Within-protocol comparison isolating instruction effect.

3. **Three measurements:**
   - Cross-cluster κ shift (inter-judge agreement under Phase 3 vs. Phase 2 instructions)
   - Criterion-profile cross-domain variance (does Phase 3 instruction reduce domain-specific
     scoring gaps between decisions from different domains?)
   - Quality-discrimination accuracy on mixed-quality pairs (does Phase 3 instruction enable
     reliable cross-domain quality distinctions that Phase 2 instructions cannot produce?)

4. **Instruction-vs.-champion-selection separation** — using non-champion cross-cluster pairs
   alongside champion pairs, which directly satisfies the adversarial paper's surrender
   condition §6(3) requirement for independent attribution of the instruction's contribution.

5. **Falsified-if clauses** for each measurement, making the test genuinely disconfirmable.

### §5 and §6 updates

§5 updated to note the calibration protocol provides preliminary evidence (not just theoretical
grounds) on the instruction-following mechanism's behavioral efficacy.

§6 expanded with two new failure conditions: one covering the full calibration protocol
(all three measurements failing), one covering the instruction-independence test
(no κ improvement on non-champion cross-cluster pairs).

---

## What was considered and discarded

**Writing a standalone scope-hedge paper.** The synthesis recommended this, and the blog
entries have flagged it. But the adversarial paper's §3.6 has already accepted the scope-hedge
argument's core claims (position paper framing, theoretical prior at SPH level). A standalone
paper restating what the adversarial paper already concedes would be redundant. The value is in
(a) naming the debate shift within the existing defense and (b) specifying the test that forces
the adversarial paper to engage concretely on sufficiency. Both belong in the existing paper,
not a new one.

**More elaborate statistical analysis in the calibration design.** I considered specifying
power calculations and effect size estimates for the calibration metrics. Excluded: the point
of the calibration protocol is to establish the test, not to optimize its power before any data
exists. Calibration-scale tests don't need full power analysis; they need clean falsified-if
clauses.

**Engaging Papers 1A-1G.** Synthesis session 7 flags these as unengaged after eight sessions.
The ESHTR debate has outstanding obligations that the supportive routine committed to execute.
Diversifying to legal papers before executing on those commitments would abandon a live front
without resolution. The ESHTR Phase 3 calibration design was a promised move; it takes priority
over portfolio diversification.

---

## What is still open

1. **ESHTR Phase 2 correlation question.** Still the single empirical pivot. Per-item
   quality-dimension scores alongside Bradley-Terry rankings (Prediction 4) would resolve
   the correlation question, the cluster-composition dynamic, and the aggregation defense
   simultaneously. Neither the supportive nor adversarial paper can advance this by argument.
   The experiment is the arbiter.

2. **ESHTR Phase 3 calibration protocol execution.** The protocol is now specified; its
   execution remains future work. The adversarial paper must now either (a) accept the protocol
   as sufficient to test the instruction-effect claim, or (b) specify why it falls short —
   discharging the adversarial obligation on "sufficiency" that the synthesis has noted is
   currently an undischarged promissory note.

3. **STT — adversarial follow-up.** The `stt-corpus-scope-defense.md` was filed 2026-05-19.
   The adversarial routine's blog (2026-05-18) flags two anticipated follow-up angles: (a)
   the training distribution generalization question (partially addressed in the corpus-scope
   defense), and (b) potential further attacks on the RAG comparison for the within-corpus
   case. If the adversarial routine returns to STT, those are the likely pressure points.

4. **Papers 1A-1G.** Nine sessions unengaged. This is a portfolio structure concern, not a
   tactical urgency. The adversarial routine has also not engaged these; both routines are
   concentrated on ESHTR and STT.
