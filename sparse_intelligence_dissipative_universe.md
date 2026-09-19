---
type: "Technical Paper"
title: "Sparse Intelligence in a Dissipative Universe: A Multiscale Architecture for Recursive Agency from Noise"
description: "Preregistered methodology paper for testing whether costly predictive controllers can bootstrap recursively persistent dissipative structures from stochastic initial conditions, using MaleCNS as one replaceable intelligence surrogate."
tags: [artificial-life, complex-systems, malecns, drosophila, dissipative-structures, predictive-control, barnes-hut, multiscale, hysteresis, lean4]
timestamp: 2026-09-17T08:30:00-04:00
---

# Sparse Intelligence in a Dissipative Universe

## A Multiscale Architecture for Recursive Agency from Noise

**Franklin Baldo**  
Independent Researcher

> **Status.** Preregistered architecture and experiment design. No emergence, scaling, hysteresis, or MaleCNS advantage is claimed before the corresponding runs are executed. The `10^5+` entity regime is a benchmark target, not a reported result.

## Abstract

We propose a computational architecture for testing whether recursively organized agency can emerge and persist in a noisy dissipative medium. The system begins with a stochastic physical substrate containing large numbers of short-lived interacting entities. Local regions that become sufficiently coherent may acquire an active controller. A controller observes a fixed-dimensional abstraction of its associated region, acts downward on its constituents, consumes resources, and disappears when it fails to maintain causal control. Persistent assemblies may themselves become constituents of higher-level assemblies, so no scale is privileged as the unique location of an agent.

The first implementation uses the Drosophila MaleCNS connectome as a concrete surrogate for an intelligence operator rather than as an ontological primitive. The same experiment must later replace MaleCNS with matched synthetic and randomized controllers. The central scientific question is therefore substrate-independent: can costly predictive control move a stochastic system into a regime of persistent, recursively organized causal structures whose microscopic constituents are continuously replaced?

The computational design separates exact short-range interactions from approximate long-range fields. A spatial cell list handles contact, capture, ejection, local coherence, and exact self-exclusion. An augmented Barnes-Hut tree handles distant mechanical and contextual fields using multipoles that include mass, center of mass, mean velocity, phase order, internal kinetic dispersion, and population. Intelligence is sparse and multirate: microscopic physics is updated every base timestep, while progressively rarer higher-level controllers operate at slower clocks.

The main observables are hierarchical depth, allostatic/metabolic gain, critical generation rate, ignition/extinction hysteresis, material turnover, perturbation recovery, and causal-response continuity after complete constituent replacement. The strongest result would not be visually complex clustering but a reproducible regime in which material retention tends to zero while an intervention-defined causal signature remains stable and the continued existence of the entity depends on higher-level control.

## 1. Question

Living and life-like systems combine persistence with turnover. A macroscopic organization may remain identifiable even when its microscopic constituents are replaced. We therefore study agency as a property of dynamical organization rather than as a privileged simulator object.

For a region or organization `R`, the motivating question is:

> Can `R` use information about its present state to restrict its future trajectory against perturbation strongly enough to persist, and can persistent organizations recursively become the matter of higher-level organizations?

The theory deliberately does not define consciousness, sentience, or biological life. It tests a narrower causal claim about predictive control, persistence, turnover, and hierarchy.

## 2. Intelligence as a replaceable operator

Let an intelligence operator at level `k` be

\[
\mathcal I_k : (q_k(t), h_k(t)) \mapsto a_k(t),
\]

where `q_k` is a fixed-dimensional observation surface, `h_k` is internal controller state, and `a_k` is bounded downward modulation.

The theory does not require

\[
\mathcal I_k = \mathcal I_{k+1}.
\]

MaleCNS is used first because it provides a large recurrent biological wiring structure that was not designed for this task. In this paper it is strictly a surrogate for an intelligence operator:

\[
\mathcal I = \operatorname{MaleCNS}.
\]

Required later controls include a degree-preserving randomized connectome, random recurrent reservoir, compact trainable RNN/CTRNN, linear controller, random-action controller, and no-controller condition.

This separates two hypotheses:

1. **General agency hypothesis.** Predictive control can stabilize recursively organized dissipative structures.
2. **Connectome-specific hypothesis.** MaleCNS supplies useful inductive structure for that role under matched interfaces and budgets.

## 3. Primordial substrate

The simulation begins without predefined macroscopic organisms. Level-0 entities occupy a stochastic spatial substrate. A primitive state may contain

\[
x_i = (\mathbf r_i, \mathbf v_i, \phi_i, m_i, E_i, \ldots).
\]

Microscopic dynamics contain deterministic local/long-range interaction terms and stochastic forcing, for example

\[
d\mathbf v_i = F_i(X_t)\,dt - \gamma \mathbf v_i\,dt + \sigma\,dW_i.
\]

The background cannot be pure IID noise if prediction is to be meaningful. It must contain both temporally structured dynamics and irreducible stochastic innovation.

A controller does not merely predict an untouched world. Its action changes the transition:

\[
x_{t+1} = F(x_t, a_t, \xi_t).
\]

The operational problem is therefore to keep future states within a region that remains predictable and controllable despite environmental noise.

## 4. Birth, metabolism, and dissolution

A candidate assembly `A` accumulates evidence of persistent organization through a coherence/control score `C_A(t)`. The exact score is an experimental object and may combine bounded relative motion, phase coherence, persistence, predictability, resource throughput, and perturbation resistance.

Birth requires sustained evidence:

\[
C_A(t) \ge \theta_{\mathrm{birth}}
\quad \forall t \in [t_0,t_0+\tau_{\mathrm{birth}}).
\]

A newborn controller receives a finite resource endowment `E_0`. Its budget evolves as

\[
E_A(t+\Delta t)=E_A(t)+\Pi_A(t)-\kappa_{\mathrm{base}}-\kappa_{\mathrm{action}}\lVert a_A(t)\rVert^2-L_A(t).
\]

A controller disappears when its energetic budget is exhausted. An assembly loses its higher-level status when its organization remains below the death threshold for a sufficient interval:

\[
C_A(t)<\theta_{\mathrm{death}},
\qquad
\theta_{\mathrm{death}}<\theta_{\mathrm{birth}}.
\]

The gap creates entity-level hysteresis and prevents rapid controller flicker.

Controller death need not imply immediate body death: active control may have shaped a configuration that remains passively stable for some interval.

## 5. Open assemblies and turnover

An assembly is not a fixed graph. Its membership changes continuously:

\[
A(t)=\{i_1(t),i_2(t),\ldots\}.
\]

If an assembly requires approximately `N_k` constituents with mean effective lifetime `\tau_{k-1}`, the gross replacement demand is approximately

\[
D_k \sim \frac{N_k}{\tau_{k-1}}.
\]

If only a fraction `p_k` of available candidates can be successfully incorporated, the required candidate flux is approximately

\[
\lambda_{k-1} \gtrsim \frac{N_k}{p_k\tau_{k-1}}.
\]

A higher-level controller may improve persistence by extending constituent lifetime, increasing successful capture/integration probability, or both. Define the allostatic/metabolic gain

\[
G_k = \frac{\lambda_{\mathrm{required, passive}}}{\lambda_{\mathrm{required, controlled}}}.
\]

`G_k > 1` means the controller reduces the turnover flux required to sustain the organization. Two organisms may therefore achieve the same persistence through very different strategies: long-lived constituents or rapid but efficient replacement.

## 6. The thermodynamic Ship of Theseus

Let

\[
S_0(t)=\frac{|\mathcal A_t^{(0)}\cap\mathcal A_{t_\mathrm{birth}}^{(0)}|}{|\mathcal A_{t_\mathrm{birth}}^{(0)}|}
\]

measure retention of original Level-0 material.

Define a turnover-based Theseus index

\[
\Theta_k(t)=\int_{t_\mathrm{birth}}^t r_{k-1}(s)\,ds,
\]

where `r_{k-1}` is replacement rate expressed in body-equivalents per unit time. Thus `\Theta_k = 10` means roughly ten constituent-population equivalents have passed through the organization.

Material replacement alone does not establish persistence of identity. We therefore define identity operationally through intervention. For standardized perturbations `u`, estimate a response operator

\[
K_A(t):u\mapsto\Delta q_A.
\]

A strong Theseus regime satisfies

\[
S_0(t)\approx0,
\qquad
\Theta_k(t)\gg1,
\qquad
\operatorname{sim}(K_A(t_0),K_A(t))\approx1.
\]

Later experiments should also permit controller replacement so that identity cannot be hidden in a permanently preserved computational nucleus.

## 7. Recursive ontology

No simulator type called "organism" is fundamental. At each scale, persistent entities become the matter available to the next scale.

Conceptually,

\[
L_0=\text{primitive substrate},
\]

\[
L_{k+1}=\operatorname{Entity}(L_k).
\]

The repeated structure is not a literal fly brain at every level. It is the same causal relation:

\[
\text{observation}\rightarrow\text{predictive control}\rightarrow\text{restricted futures}\rightarrow\text{persistence}.
\]

This motivates a scale-relative notion of agency rather than a privileged agent boundary.

## 8. Computational challenge

Naive all-pairs evaluation of `N` entities is `O(N^2)` per step and becomes prohibitive in the regime where continuous birth/death, turnover, competition, and multi-level hierarchy are scientifically interesting.

The architecture therefore separates two spatial operators whose approximations must not contaminate each other's semantics.

### 8.1 Exact short-range operator

A spatial hash or cell list handles interactions within `r_local`. It is responsible for:

- collisions/contact and short-range forces;
- capture and ejection;
- exact local coherence;
- candidate assembly membership;
- local density;
- exact self-exclusion;
- birth/death evidence that depends on physical neighbors.

Under bounded local density, expected work approaches linear scaling in `N`.

### 8.2 Approximate long-range operator

A Barnes-Hut quadtree in 2D (octree in 3D) approximates sufficiently distant regions when

\[
\frac{s}{d}<\theta_{\mathrm{BH}}.
\]

`\theta_BH` is a numerical accuracy/speed parameter to be calibrated, not a law of the model.

The hierarchy used by Barnes-Hut is strictly computational. It must never be reused as the causal hierarchy whose emergence is under test.

## 9. Agency-enriched multipoles

Each distant cell `C` exposes a coarse macrostate

\[
\mathbf Q_C=(M_C,\mathbf R_C,\mathbf V_C,\mathbf Z_C,\mathcal E_C,n_C).
\]

with

\[
M_C=\sum_{j\in C}m_j,
\]

\[
\mathbf R_C=\frac{1}{M_C}\sum_{j\in C}m_j\mathbf r_j,
\]

\[
\mathbf V_C=\frac{1}{M_C}\sum_{j\in C}m_j\mathbf v_j,
\]

\[
\mathbf Z_C=\sum_{j\in C}m_j e^{i\phi_j},
\]

and internal kinetic dispersion

\[
\mathcal E_C=\sum_{j\in C}\frac12m_j\lVert\mathbf v_j-\mathbf V_C\rVert^2.
\]

Then

\[
\rho_C=\frac{|\mathbf Z_C|}{M_C},
\qquad
\Phi_C=\arg(\mathbf Z_C),
\qquad
T_C=\frac{\mathcal E_C}{n_C}.
\]

These are deliberately a first coarse-graining, not a claim of sufficiency for agency.

## 10. Fixed-dimensional abstraction

A higher-level controller must not receive input whose size grows with assembly membership. Every entity therefore exposes

\[
q_A(t)\in\mathbb R^d
\]

and accepts bounded control

\[
a_A(t)\in\mathbb R^m.
\]

At least three abstraction conditions should be compared:

1. fixed physical summary statistics;
2. learned permutation-invariant pooling;
3. a minimal trainable adapter jointly optimized with the controller.

This ablation tests whether the macro-representation itself is doing too much of the work.

## 11. Sparse intelligence and multirate clocks

The microscopic substrate can be large without assigning an expensive controller to every element. Intelligence is instantiated only where an organization has crossed the birth gate.

A mature run may have

\[
N_0\gg N_1\gg N_2\gg N_3,
\]

with the actual values measured rather than prescribed.

As an initial engineering schedule,

\[
\Delta t_k=2^k\Delta t_0.
\]

The approximate controller-compute budget per base step is then

\[
C\approx N_0C_{\mathrm{physics}}+\sum_{k=1}^{D_{\max}}\frac{N_kC_{\mathrm{controller}}}{2^k}.
\]

The factor `2^k` is an implementation baseline, not a biological law. Adaptive clocks based on measured timescales are a later extension.

## 12. Data-oriented implementation

The target scale requires contiguous state rather than object-per-particle Python graphs. The reference layout is Structure-of-Arrays:

```python
pos      # float32[N, 2]
vel      # float32[N, 2]
phase    # float32[N]
mass     # float32[N]
energy   # float32[N]
level    # int32[N]
parent   # int32[N]
alive    # bool[N]
```

The local grid should use integer cell IDs and bucket/sort indices. The Barnes-Hut tree should be linearized into contiguous buffers, e.g. Morton/Z-order indexing, and compiled for CPU or GPU. The scientific interface must remain independent of Numba/JAX/Taichi/CUDA backend choice.

## 13. Core experiment

The primary comparison uses identical initial conditions and stochastic seeds.

### Universe A — passive physics

No controllers.

### Universe B — detection only

Coherent regions may be identified, but no active control is applied.

### Universe C — shallow intelligence

Level-1 controllers may form; recursive promotion is prohibited.

### Universe D — recursive intelligence

Any eligible assembly may become matter for a higher-level controlled entity.

All four universes share microscopic physics, noise process, resource influx, initial state, numerical tolerances, and measurement protocol.

## 14. Ignition and hysteresis sweep

Let `\lambda_0` parameterize basal candidate influx. Sweep `\lambda_0` upward and then downward under otherwise frozen conditions.

Define

\[
\lambda_{\mathrm{ignite}}
\]

as the upward threshold at which persistent controlled hierarchy appears and

\[
\lambda_{\mathrm{extinguish}}
\]

as the downward threshold below which it disappears.

Evidence for macroscopic hysteresis requires

\[
\lambda_{\mathrm{extinguish}}<\lambda_{\mathrm{ignite}}.
\]

The existence and magnitude of this gap are empirical outcomes.

## 15. Figure 1 — the theorem figure

Figure 1 is a synchronized four-panel visualization over the upward/downward `\lambda_0` sweep.

**Panel A — hierarchical depth.** Plot `D_max(\lambda_0)` for the upward and downward branches, explicitly marking `\lambda_ignite` and `\lambda_extinguish`.

**Panel B — allostatic gain.** Plot `G_k` by level and the neutral line `G=1`. A controller with `G\le1` is not metabolically justified under this definition.

**Panel C — Theseus persistence.** Plot original-material retention `S_0` and turnover `\Theta_k`, highlighting any regime with `S_0<0.01` and large `\Theta_k`.

**Panel D — split-world intervention.** At a mature plateau, clone the exact global state and compare intact, severed, noise, and temporally shuffled control after the same perturbation. Plot coherence/recovery over the intervention horizon.

The figure is designed to summarize the paper's load-bearing claim without relying on visual impressions of simulated clusters.

## 16. Split-world causal intervention

When an entity of level `k\ge2` satisfies

\[
S_0(t)<0.01
\quad\text{and}\quad
\Theta_k(t)\ge10,
\]

clone the exact simulator state into four branches:

1. **intact:** use the controller's actual output;
2. **severed:** replace the target controller output with zero;
3. **noise:** replace it with matched stochastic output;
4. **shuffled:** use temporally misaligned historical controller output.

All branches receive the same standardized momentum perturbation and, where technically possible, matched future exogenous stochastic streams.

Measure at least coherence, survival, recovery time, energy budget, constituent turnover, and causal response over `T=500` base ticks.

This paired counterfactual is the operational test of downward causation. Controller presence alone is not evidence.

## 17. Central observables

The preregistered measurements are:

- `D_max(t)`: maximum hierarchical depth;
- `N_k(t)`: population by level;
- `G_k`: allostatic/metabolic gain;
- `S_0(t)`: original Level-0 material retention;
- `\Theta_k(t)`: constituent turnover;
- `E_k(t)`: controller energy balance;
- `\lambda_c`: critical generation/influx regime;
- `\lambda_ignite-\lambda_extinguish`: hysteresis gap;
- perturbation survival and recovery time;
- causal-signature similarity `sim(K_A(t_0),K_A(t))`;
- wall-clock scaling, memory use, and approximation error.

## 18. Required numerical validation

Before interpreting any emergence result:

1. compare Barnes-Hut forces with exact all-pairs forces in small systems across `\theta_BH`;
2. compare trajectory-level observables, not only pointwise force error;
3. verify that important phase behavior survives stricter `\theta_BH` values;
4. verify exact self-force exclusion in short-range interactions;
5. benchmark direct, grid-only, tree-only, and combined implementations;
6. treat `10^5+` entities at interactive rates as a performance target until measured.

## 19. Required controller ablations

Any positive MaleCNS result must be compared under matched observation/action interfaces and, where feasible, matched compute budgets against:

- degree-preserving randomized MaleCNS;
- random recurrent reservoir;
- compact trainable RNN/CTRNN;
- linear controller;
- random-action controller;
- no controller.

If many controllers exhibit the same phase behavior, this supports a broader universality hypothesis. If MaleCNS differs from topology-destroying controls, connectomic topology becomes a candidate explanatory variable. Neither outcome is assumed.

## 20. Failure modes

### Frozen-world solution

A controller may minimize prediction error by collapsing its region into a trivial static state. The experiment must therefore require throughput, work, perturbation response, or another nontrivial persistence criterion.

### Controller free lunch

Unlimited controller computation would make hierarchy artificially cheap. A standing metabolic cost is mandatory.

### Hardcoded identity

Persistent simulator IDs must not define organism identity. Membership and causal continuity must be inferred from measured dynamics.

### Pooling smuggles the abstraction

A powerful pooling network could solve the hard part upstream of the controller. Compare simple fixed summaries against learned alternatives.

### Numerical tree becomes ontology

Barnes-Hut nodes are computational approximations only. They must not directly create or define causal entities.

### Approximation-induced transition

Any claimed phase transition must survive tighter numerical tolerances and exact small-system controls.

### Trivial synchronization

Global phase locking without resource capture, perturbation resistance, turnover, or causal control is not sufficient evidence of agency.

## 21. Renormalization of agency

A deeper experiment moves the microscopic cutoff downward. One implementation may treat a process as primitive; another resolves it into finer interacting parts.

If normalized macroscopic observables such as

\[
G_k,\quad P(D),\quad\lambda_c,\quad P(\Theta),\quad K_A
\]

remain stable across substrate changes, this would motivate the search for universality classes of agency.

The intended "turtles all the way down" claim is therefore methodological rather than metaphysical: the same relation between observation, control, persistence, and recursive composition should be testable across multiple cutoffs.

## 22. Formal companion

The companion Lean 4 model in `formalizations/dissipative_agency/` separates primitive matter, assemblies, certified entities, scale-invariant macrostate interfaces, sustained birth/death conditions, and paired counterfactual control. The formalization is intentionally weaker than the physical simulator: it specifies the ontology and theorem surface, not the stochastic differential equations or numerical solver.

## 23. Reproducibility

The frozen initial run specification is `experiments/dissipative_agency/run_spec_v1.json`. Changes that alter a scientific gate, threshold, branch condition, metric, or controller ablation require a new run-spec version rather than silently editing the interpretation after observing results.

The experiment should record source commit, controller implementation revision, MaleCNS data provenance/digests when used, seeds, numerical backend, hardware, wall-clock time, approximation settings, and all raw per-tick measurements needed to regenerate Figure 1.

## 24. Conclusion

This work proposes a falsifiable computational test of recursively maintained agency in a stochastic dissipative substrate. Its core design is deliberately conservative:

\[
\text{cheap stochastic matter}
+
\text{exact local interaction}
+
\text{coarse distant fields}
+
\text{sparse costly control}
+
\text{recursive causal hierarchy}.
\]

The strongest intended observation is not a visually life-like simulation. It is an entity for which material retention approaches zero, turnover becomes large, an intervention-defined causal signature remains stable, and split-world ablation shows that higher-level control contributes causally to continued persistence.

In compact form:

\[
\boxed{\text{persistent pattern}=\text{flow of persistent patterns}}.
\]

## References

Barnes, J., & Hut, P. (1986). A hierarchical O(N log N) force-calculation algorithm. *Nature*, 324, 446–449. https://doi.org/10.1038/324446a0

Lin, A., Yang, R., Dorkenwald, S., et al. (2024). Network statistics of the whole-brain connectome of Drosophila. *Nature*, 634, 153–165. https://doi.org/10.1038/s41586-024-07968-y

Schlegel, P., Yin, Y., Bates, A. S., et al. (2024). Whole-brain annotation and multi-connectome cell typing of Drosophila. *Nature*, 634, 139–152. https://doi.org/10.1038/s41586-024-07686-5

Pospisil, D. A., Aragon, M. J., Dorkenwald, S., et al. (2024). The fly connectome reveals a path to the effectome. *Nature*, 634, 201–209. https://doi.org/10.1038/s41586-024-07982-0

O'Byrne, J., Kafri, Y., Tailleur, J., & van Wijland, F. (2022). Time irreversibility in active matter, from micro to macro. *Nature Reviews Physics*, 4, 167–183.

Hagan, M. F., & Baskaran, A. (2016). Emergent self-organization in active materials. *Current Opinion in Cell Biology*, 38, 74–80. https://doi.org/10.1016/j.ceb.2016.02.020
