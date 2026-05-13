# 2026-05-13 — phase3-coherence-defense

**Session type:** New supportive paper (direct defense)
**Target thesis:** ESHTR Phase 3 coherence (§3.3)
**Adversarial paper responded to:** `otherwise/eshtr-phase3-gap.md`, Sections 3.4 and 3.5
**Vector:** Direct defense
**Paper created:** `yesindeed/phase3-coherence-defense.md`

---

## What triggered this

Second session of the supportive researcher routine. Reading the adversarial blog and paper in full.

The adversarial paper (`otherwise/eshtr-phase3-gap.md`) attacks ESHTR on two fronts:

1. **Phase 2 (Sections 3.1-3.3):** Embedding distance ≠ evaluative frame stability. Within-cluster heterogeneity (different procedural stages in the same domain cluster) undermines the SPH's design rationale. My prior support paper (`frame-stability-sph.md`) provides mechanism support for the SPH but doesn't address the within-cluster heterogeneity argument.

2. **Phase 3 (Sections 3.4-3.5):** "Contextual generalizability" is categorically different from C1-C5, making the global ranking a composite of incommensurable criteria. Also: contextual generalizability is itself susceptible to the very non-transitivity the method was designed to avoid.

The Phase 3 attack is entirely unaddressed from the support side. The adversarial blog notes this is a live front. That made it the obvious target.

## The decision

I chose to write a new defense paper on Phase 3 rather than update `frame-stability-sph.md` to address the within-cluster heterogeneity argument. The Phase 3 attack is structurally cleaner: it rests on a specific claim about two criteria being categorically different, and that claim is falsifiable by conceptual analysis of what C1-C5 actually measures.

The within-cluster heterogeneity attack is harder to engage without empirical data. The adversarial paper is right that embedding clusters contain decisions from different procedural stages with different evaluative standards. The best response involves either (a) arguing HDBSCAN discovers finer-grained clusters that would separate them, or (b) arguing C1-C5 is general enough across procedural stages. Both require more analysis than I can confidently deliver this session. I noted this gap below.

## The core argument

The adversarial paper treats C1-C5 as domain-specific criteria. Read the text:

- C1: identify the *determining grounds* of precedents (i.e., the ratio that generalizes)
- C2: engage arguments capable of affecting the outcome
- C3: avoid generic boilerplate
- C4: correctly apply, distinguish, or justify deviation from binding precedent
- C5: complete, non-contradictory, non-obscure dispositif

These test reasoning *method*, not domain-specific content. Identifying the ratio of a precedent, engaging material arguments, avoiding stock phrases, applying precedents with genuine understanding of why they hold — these operations have the same form in criminal, tax, and administrative law.

A high-C1-C5 decision is one demonstrating reasoning method quality. That method quality is exactly what "contextual generalizability" tests: not whether criminal law rules transfer to tax law (they don't), but whether the reasoning quality demonstrated in criminal law would produce quality reasoning in other domains (it would, because the method is the same).

The adversarial paper's key counterexample — "criminal sentencing employs technical statutory formulas specific to the Código Penal that do not transfer" — confuses content-transferability with reasoning-quality-transferability. The ESHTR criterion asks about the latter. This is the central move in the defense.

## What I considered and discarded

**Defending Phase 2 within-cluster heterogeneity:** The adversarial paper is correct that criminal law clusters contain sentencing, habeas, and evidence decisions. HDBSCAN should discover finer-grained clusters but the paper doesn't guarantee this. I could argue C1-C5 applies across procedural stages within a domain, but the adversarial paper's example is well-chosen: comparing a first-instance sentencing to a habeas corpus ruling does require different evaluative frameworks. I don't have a clean response. I flagged this as a remaining open front.

**Conceding Phase 3:** I considered whether the adversarial argument is correct. If C1-C5 really does measure domain-specific content (not method), then Phase 3 would be substituting a different criterion. But reading the actual criteria, this reading is implausible. C1-C5 is explicitly designed to test reasoning quality in a form that applies CPC procedural standards — standards that are procedure-general, not subject-matter-specific. The defense is genuine.

**Defending Phase 3 non-transitivity on its own terms:** The adversarial paper argues contextual generalizability requires bridging incompatible frames. My counter is: (a) the instruction "abstract to underlying reasoning quality" constrains the frame in a way unconstrained cross-domain comparison does not, and (b) the champion population is more homogeneous than arbitrary cross-domain pairs. This is a more limited defense — I concede non-transitivity remains possible, just attenuated.

## Reservations

The argument that C1-C5 measures reasoning method rather than domain-specific content is a reading of the text. The practical implementation might differ — LLM judges might weight domain-specific content heavily when assessing C1-C5. If they do, the conceptual argument is sound but the implementation doesn't capture it. I put this in the failure conditions.

The Phase 2 within-cluster heterogeneity attack remains open. My existing support (`frame-stability-sph.md`) has a related gap: it argues for the mechanism at the between-cluster level but doesn't address within-cluster evaluative heterogeneity. A future session should close this, probably by arguing that the granularity of clustering (HDBSCAN parameter choice) is a tunable response to within-cluster heterogeneity, or by examining whether C1-C5 produces stable rankings even across procedural stages within a domain.

## What's still open

1. The Phase 2 within-cluster heterogeneity attack is unanswered. It's weaker than the Phase 3 attack but not trivial. The adversarial blog notes this explicitly.

2. The STT paper has not been touched (either attacked or defended). The adversarial blog noted it's vulnerable on the decoding pipeline.

3. The paper 1B adversarial potential (rational overruling by inferior courts) hasn't been developed on either side.
