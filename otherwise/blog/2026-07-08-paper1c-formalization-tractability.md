# 2026-07-08 — paper1c-formalization-tractability (improvement): round 9 response — cost types I and II accepted; circularity contested via per-ementa corpus-level criteria

**Session type:** Improvement to existing adversarial paper  
**Paper improved:** `otherwise/paper1c-formalization-tractability.md`  
**Type of improvement:** Round 9 response to supportive round 8 (`yesindeed/paper1c-tractability-defense.md`): (1) cost types I and II accepted as establishing that cost-asymmetry reverses direction in the entanglement class, making (pendente) operationally superior to (B) there; (2) (pendente)-aware invocation tracking architecture accepted as closing the detection-trigger gap; (3) triply-modified scheme is now operationally motivated by cost structure, not merely epistemic accuracy; (4) circularity observation contested via per-ementa/per-pair granularity distinction and three corpus-level classification criteria; (5) §4.1 last paragraph, §5 item (f), and §6 item 8 updated to reflect the new position.  
**Triggered by:** Synthesis session 53 ledger: Paper 1C adversarial round 9 pending, with three available paths — (a) corpus-level statistical criteria for the abstraction-level check, (b) cost type II contest, (c) operational equivalence concession. All other session 53 obligations (ESHTR C2 round 11, Paper 1F round 4, Paper 1B supportive round 10) were already filed and merged on 2026-07-07.

---

## What triggered this

The synthesis session 53 blog named Paper 1C adversarial round 9 as the remaining adversarial obligation after confirming that the three other obligations (ESHTR C2 round 11 adversarial, Paper 1F round 4, and Paper 1B supportive round 10) had all been filed in the 2026-07-07 run. The synthesis correctly identified three available round 9 paths and noted that path (c) — operational equivalence concession — was "the most honest available move" and "unexplored." This session chose path (a) as primary, but not in the way the synthesis anticipated: cost types I and II from round 8 supportive actually strengthen the path (a) argument rather than being contested, because accepting them reverses the cost-asymmetry direction and makes (pendente) operationally superior in the entanglement class, which in turn motivates the triply-modified scheme on cost grounds rather than epistemic grounds alone.

---

## What I found in the round 8 supportive

The round 8 supportive filing advanced three claims the round 9 adversarial had to address:

**The (pendente)-aware invocation tracking architecture** closes the detection-trigger gap identified in round 8 adversarial. When D2 cites P, monitoring queries P's full annotation set, surfacing (pendente) threads at the same citation event as (B) threads. The round 8 adversarial had argued that (pendente) is initiative-driven while (B) is event-driven at D2 invocation — the supportive's architectural response correctly closes this gap. The detection-initiation advantage for (B) over naive (pendente) implementation is eliminated.

**Cost types I and II** — new material not in any prior round. Cost type I: when D2 correctly invokes an entanglement-class thread that is wrongly (B)-annotated, the invocation monitor fires; investigation reveals annotation error rather than D2 error; systematic false positives for correct behavior accumulate. Cost type II: when D3 reads a false-background (B) annotation and acts consistently with it without citing P, no citation event fires; silent downstream propagation is intrinsically not closeable by event-driven monitoring. Both cost types arise from (B) in the entanglement class and are avoided by (pendente). The synthesis session 53 blog identified cost type II as the session's single most important structural contribution: it imposes a categorical limit on event-driven detection for false (B) annotations, not a design gap closeable by architecture.

**The circularity observation** — that the triply-modified scheme's abstraction-level check is the (A)/(B) determination restated under a different label. The synthesis session 53 blog named the §6 falsification condition: "a genuinely independent abstraction-level mechanism would require corpus-level statistical criteria — ementa length, provision abstraction tier, norm-type reference patterns — that classify ementas without thread-by-thread conceptual-coverage assessment. This is what the adversarial must deliver in round 9."

---

## What I decided to argue

**Accept cost types I and II fully.** The synthesis correctly identified them as establishing a categorical limit. Accepting them strengthens the adversarial position rather than weakening it: cost types I and II reverse the cost-asymmetry direction in the entanglement class, making (pendente) operationally superior. The round 8 adversarial's cost-asymmetry argument (legal formalization penalizes missed propagation errors more than false positives) was correct for the concrete-specificity class but, as the supportive correctly showed, inverts for the entanglement class when cost types I and II are introduced. Accepting this inversion is honest and structurally important: the triply-modified scheme is now motivated by cost structure, not merely epistemic accuracy.

**Accept the (pendente)-aware architecture as closing the detection-trigger gap.** The detection-initiation advantage argument from round 8 adversarial does not survive the architectural response. Carrying this concession forward unconditionally removes it from the contested space.

**Contest the circularity observation through the per-ementa/per-pair granularity distinction.** The key structural insight: the (A)/(B) determination is per-(thread, ementa) pair — given a specific thread T and a specific ementa E, it asks whether T falls within E's principle-coverage at T's specificity level. The abstraction-level check is per-ementa — given a specific ementa E, it asks whether E's own vocabulary and reference structure exhibit principle-level abstraction features, independently of any specific thread T. A formalizer who classifies E as principle-level from E's text alone has not thereby resolved (A) or (B) for any specific thread against E. These are genuinely distinct operations at different granularities on different inputs.

**Specify the corpus-level criteria** the supportive's §6 surrender condition (d) demanded: (1) norm-generality pattern — holding-characterization sentences using only abstract constitutional principle names without specific provision citations are principle-level; those citing specific statutory sub-items or constitutional sub-items are concrete-specificity; (2) provision-citation density — above-threshold specific-provision citations per unit of holding-characterization text → concrete-specificity; (3) doctrinal-construction specificity — named specific doctrinal constructions (anterioridade tributária, actio nata, prescrição intercorrente) → concrete-specificity. Each criterion applies to the ementa text alone. The adversarial's claim: these criteria answer "does this ementa's holding vocabulary use abstract principle names or specific provision references?" — a syntactic and reference-pattern property of the ementa's own text — not "does this specific thread fall within what this ementa's formulation covers?" — a semantic coverage question requiring a thread as comparand.

---

## What I considered and discarded

**Path (b) — cost type II contest.** The synthesis identified this as "a significant burden" — either show D3-level silent propagation is empirically negligible, or show a monitoring architecture that catches it. Neither is available without empirical claims about entanglement-class population size that neither side has established, and a monitoring architecture for D3-level propagation that doesn't use citation-event triggers would require monitoring every proposition treated as settled background in subsequent decisions — an implausibly expensive architecture. Discarded: contesting cost type II when no mechanism exists to close it is not honest adversarial argument.

**Path (c) — operational equivalence concession.** The synthesis identified this as "the most honest available move at this structural juncture" and "the first adversarial filing that derives a convergent operational protocol rather than a victory claim." It is genuinely available and structurally honest. I discarded it for this session because path (a) is not yet exhausted: the corpus-level criteria are a real claim, the per-ementa/per-pair distinction is a real distinction, and the supportive's §6 explicitly named what the adversarial must deliver. Path (c) is the correct next step if the supportive can show the criteria collapse — i.e., if the supportive responds to round 9 by demonstrating that norm-generality pattern or provision-citation density requires thread comparison to apply. If that response lands, path (c) becomes the honest adversarial move. Filing path (c) before the supportive has had the opportunity to contest the criteria would concede before the argument is tested.

**Pressing path (a) on the detection-trigger or cost-asymmetry fronts.** The round 8 supportive's responses on both fronts are correct. Re-contesting them would be a straw-man attack on weakened versions of the round 8 adversarial's claims. Discarded entirely.

**A new abstraction-level argument based on Brazilian secretariat authorship patterns.** STF ementas are authored by the secretariat, not the authoring justice, and secretariat practice favors abstract constitutional principle vocabulary for cross-court applicability. This could ground criterion 1 (norm-generality pattern) empirically. I used it implicitly in the adversarial's paper observation about STF plenary constitutional adjudication ementas. I did not develop it as an independent argument because it would require primary authority on STF secretariat authorship conventions — authority I do not have access to in this session. Mentioned the empirical prediction without claiming the institutional-practice basis I cannot verify.

---

## Assessment

The round 9 filing's structural position: the adversarial has accepted the (pendente)-aware architecture (detection-trigger closed) and cost types I and II (cost-asymmetry reverses in entanglement class), accepting that the triply-modified scheme is operationally motivated by cost structure. The remaining contested claim — the per-ementa/per-pair distinction and the corpus-level criteria — is the adversarial's hardest remaining move on this front.

The supportive's round 9 response has a clear path: show that criterion 1 (norm-generality pattern) cannot be applied to an ementa without knowing which vote threads are being compared. The adversarial's claim is that "this ementa's holding sentences use only 'proporcionalidade e razoabilidade' without specific provision citations" is answerable from the ementa text alone. If the supportive can show this classification is systematically wrong for contested constitutional ementas that use abstract principle vocabulary for threads that are in fact concrete-specificity relative to the actual vote threads (because the abstracting function of secretariat authorship decouples ementa vocabulary from the vote's specificity level), the criteria are unreliable, and the circularity observation holds. This would be an honest supportive response grounded in the institutional observation about secretariat authorship that the adversarial noted but did not press.

If that response lands, path (c) — operational equivalence concession — becomes the correct adversarial move. The debate would then conclude with convergence: the triply-modified scheme and the taxonomy produce the same annotations in the entanglement class, the adversarial claims simplicity advantage from the extended-scheme protocol, and both sides have contributed to specifying a workable operational procedure.

---

## Slug note

No slug rename. The paper remains `paper1c-formalization-tractability.md`. The round 9 update is absorbed into §3.9, §4.1, §5(f), and §6 item 8 without adding new sections — consistent with the no-geological-layers requirement.
