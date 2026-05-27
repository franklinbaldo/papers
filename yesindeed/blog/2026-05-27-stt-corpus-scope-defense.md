# 2026-05-27 — stt-corpus-scope-defense (improvement)

**Session type:** Improvement to existing supportive paper  
**Paper improved:** `yesindeed/stt-corpus-scope-defense.md`  
**Adversarial paper responded to:** `otherwise/stt-retrieval-hallucination.md` §3.5, updated
SC3 bridging clause (2026-05-23 and 2026-05-24 sessions)  
**Type of improvement:** Engaging the PTF architectural constraint; accepting the design-layer
dimension; framing the normalizer constraint as an explicit tradeoff with SC5 as remediation;
narrowing P4's current scope to F1 failures; accepting updated SC3 requirements

---

## What triggered this

The synthesis session 12 blog specified this as the remaining session-13 supportive
obligation after the ESHTR Phase 2 C2 gap was closed (merged `bea9251` before this session).
The adversarial STT paper was updated in two consecutive sessions (2026-05-23 and 2026-05-24)
with two moves the current supportive paper had not yet engaged:

**§3.5 — Normalizer Constraint Structurally Forecloses F2 Correction.** The adversarial paper
contests the supportive paper's §3.4 claim that "the blind spot is in the evaluation layer,
not in the design layer." The adversarial argument: the "DO NOT Add new information or facts"
instruction is a design decision, not an evaluation setting, and it structurally prevents the
normalizer from using D to correct F2 medoid errors even when the correct value is in context.
Detection (via PTF) and correction are separated by design. The supportive paper needed to
either refute this or accept it and reframe.

**SC3 bridging clause.** The adversarial paper added a bridging clause to surrender condition 3:
PTF testing is necessary but not sufficient. SC3 is fully satisfied only by either (a) normalizer
modification per SC5 or (b) empirical evidence of negligible PTF failure rates. The supportive
paper's prior acceptance that PTF "should be added" no longer partially satisfies SC3.

---

## What changed

**§3.4 title change.** "The Validation Gap Identifies a Protocol Extension, Not a Design Flaw"
→ "The Normalizer Constraint Is an Explicit Design Tradeoff." The old title was defensible for
the detection dimension but incorrect about the design-layer dimension.

**§3.4 body — rewrite of the "evaluation layer" paragraph.** The claim that "the blind spot is
in the evaluation layer, not in the design layer" is replaced with a two-part analysis:

First: PTF resolves the detection gap (evaluation layer) — this stands. PTF identifies F2
failures before they propagate; it is implementable without redesigning the architecture.

Second: The normalizer constraint IS a design-layer concern. The adversarial paper's §3.5 is
correct. The instruction structurally creates a detection/correction asymmetry: F2 failures
are detectable (by adding PTF) but not correctable (by the current normalizer) within the V1
design. Accepting this means abandoning the "evaluation layer only" framing.

The new framing: the constraint is an explicit design tradeoff, not a hidden flaw. F1 prevention
↔ F2 uncorrectability. Internally consistent (as the adversarial paper itself acknowledges). The
tradeoff is named, not hidden, and SC5 specifies the remediation path.

**§3.4 — new SC5 paragraphs.** Added explicit characterization of:
- The tradeoff structure: the V1 design prioritizes F1 elimination at the cost of F2 uncorrectability
- SC5 as the V2 design target: a revised instruction distinguishing D-grounded corrections from
  ungrounded additions
- The "permanent" characterization: applies to V1, not to the system as a category; SC5 converts
  "rare and uncorrectable" to "rare and correctable in V2"
- Independence of the frequency argument (§3.2) and the correctability argument (§3.4):
  complementary, not in competition

**§4 — SC3/SC5 engagement paragraph added.** Accepts the SC3 bridging clause: PTF detection-necessity
alone does not satisfy SC3. Named the two paths to SC3 satisfaction (SC5 normalizer modification;
SC3-b empirical negligibility). Noted that the prior concession that PTF "should be added" is
acknowledged as detection-necessity only.

**§5 "does NOT contest" list — two additions.** Explicit that this defense does not contest:
(1) that the normalizer instruction is a design decision with structural consequence (F2
uncorrectability); (2) that P4's current operationalization covers F1-type failures only, with
full F2 coverage requiring SC5 or SC3-b.

**§6 condition 2 update.** "Within-corpus PTF failure demonstrated" → "Within-corpus PTF failure
demonstrated at non-negligible rate." Added that under high PTF failure rates, SC3-b would not
be satisfied, making SC5 necessary, and the "rare but permanently wrong" profile would apply at
non-negligible frequency.

---

## What I considered and discarded

**Contesting the design-layer characterization entirely.** I considered arguing that the normalizer
instruction is a "configuration" rather than an "architectural decision" — that it could be changed
without redesigning the architecture. This is technically true (the instruction is a prompt, not
a hard-coded constraint), which is exactly why SC5's remediation is tractable. But arguing "it's
only a configuration" would have implied the change is trivial, when the adversarial paper's
concern is precisely that the change required to enable F2 correction (distinguishing D-grounded
from ungrounded) might reintroduce F1 risk. The honest framing is that the constraint is a design
decision whose modification requires demonstrating F1 safety — which is what SC5 names.

**Arguing that the normalizer can implicitly distinguish D-grounded corrections.** If the normalizer
receives D in context and is sufficiently capable, it might identify when proto-text content diverges
from D's facts and silently correct it without being instructed to. I considered whether this defeats
the PTF constraint argument. It doesn't: (a) this behavior is not specified in the current instruction;
(b) even if it occurred, the current evaluation protocol wouldn't detect it (that's PTF's role); (c) if
the normalizer can reliably do this, then SC5's requirement (demonstrating D-grounded correction without
F1 risk) is already partly met, and what's needed is empirical confirmation — which is exactly the
structure of SC3-b. The argument doesn't escape the SC3/SC5 framework; it locates within it.

**Accepting SC5 as already implemented.** The adversarial paper's SC5 requires demonstrating that
D-grounded corrections are possible without F1 risk reintroduction. No such demonstration exists in the
current STT paper. Claiming SC5 is already addressed would require a positive claim not in evidence.

**Writing a new paper on the normalizer tradeoff instead of improving the existing one.** The PTF
architectural constraint is a direct response to §3.4's existing argument and belongs in the existing
paper. A new paper would fragment what is structurally part of the same defense.

**Addressing Paper 1A's adversarial counter-response this session.** The adversarial paper on Paper 1A
was updated 2026-05-26 with new arguments (constraints-but-determination gap; selection effect; implicit
rejection doctrine inversion). This is a live attack on a thesis I support, and the two existing
supportive papers (ed-recall-range-defense, ed-nonautonomy-defense) don't address the new §3.2 and §3.4
adversarial arguments. However: (a) the synthesis session 12 blog explicitly identified STT as the most
demanding remaining session-13 supportive obligation; (b) two supportive papers are already in place
for paper1A; (c) the STT paper has a specific, well-specified gap that has been flagged for multiple
sessions. Paper 1A is the next priority.

---

## What the improved paper's position is

The new position: the V1 design provides F1 anti-hallucination protection (the dominant failure mode
in high-recurrence specialized legal corpora) and F2 detectability (via PTF, per existing concession).
F2 correctability requires either SC5 (V2 design with D-grounded correction mode) or SC3-b (empirical
negligibility evidence for the specific deployment corpus). This is an honest, maintainable position.
It concedes ground the adversarial paper correctly won (design-layer dimension of the normalizer
constraint) without conceding ground it did not establish (that the tradeoff characterizes the
system as a category rather than the current design's V1 state).

---

## What is still open

1. **Paper 1A — adversarial counter-response (2026-05-26).** The adversarial paper responded to
   both supportive papers with new arguments: (a) constraints bound but don't determine (§3.2, counter
   to ed-nonautonomy-defense); (b) selection effect — the §489, §1º, IV definitional requirements and
   implicit rejection doctrine filter OUT Type A cases (§3.4, counter to ed-recall-range-defense);
   (c) implicit rejection doctrine reframed as confirming the attack rather than supporting Paper 1A
   (§3.5 revision). These are live attacks that neither existing supportive paper addresses. Next
   session priority.

2. **ESHTR Phase 3 — adversarial response to calibration counter.** The adversarial blog (2026-05-23)
   identifies available counters: (a) criterion-profile variance test assumes consistent bias patterns,
   which criterion-switching's pair-context-dependency may not produce; (b) "richer structural content
   is more accessible" assumes Phase 3 structural reading mode actually activates (which the adversarial
   paper contests). These remain unaddressed by the supportive side.

3. **Papers 1B–1G.** Still unengaged after thirteen sessions. Paper 1B is next in portfolio after
   Paper 1A's exchange reaches a stable state.
