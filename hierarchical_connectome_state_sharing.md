---
type: "Scientific Position Paper"
title: "Hierarchical State Sharing for Massive Connectome Ensembles: Barnes-Hut-Inspired Clustering, Low-Rank Dynamics, and Multirate Simulation"
description: "Proposes and falsifies a family of approximation methods for simulating many copies of one biological connectome by sharing computation across similar regional neural states, combining exact sparse batching, hierarchical clustering, representative-plus-residual updates, low-rank ensemble dynamics, hyper-reduction, adaptive timesteps, and spatial field solvers."
tags: [malecns, drosophila, connectome, simulation, barnes-hut, low-rank, model-reduction, clustering, sparse-linear-algebra, swarm]
timestamp: 2026-09-16T12:00:00-04:00
---

# Hierarchical State Sharing for Massive Connectome Ensembles

## Barnes-Hut-inspired clustering, low-rank dynamics, and multirate simulation

**Franklin Baldo**  
Independent Researcher

> **Scientific position paper / research agenda — 16 September 2026.** No benchmark claimed for the methods proposed here has yet been run. The paper distinguishes exact algebraic reorganizations from approximations and treats speedups as hypotheses to be measured. “State similarity” refers to similarity of simulated neural state vectors; it is not a claim about consciousness or subjective mental identity.

## Abstract

A large connectome can be simulated once, but many-copy simulation creates a different computational problem. Suppose a fixed recurrent operator derived from one biological connectome is instantiated for thousands or millions of agents. Each agent has the same graph and update rule but a different neural state and sensory drive. The obvious implementation applies the sparse recurrent operator independently to every agent, with cost proportional to the number of agents. Yet many agents in the same environment may occupy highly similar local neural states. Recomputing nearly the same regional transition for every copy may therefore be redundant.

This paper proposes a falsifiable family of methods for exploiting that redundancy. The motivating analogy is Barnes and Hut's hierarchical N-body method: when many distant particles can be summarized sufficiently well by an aggregate, computation is spent only where additional detail materially changes the answer. The proposed neural analogue does **not** reuse gravitational mathematics. Instead, it builds adaptive hierarchies in neural-state space. Copies whose regional states and incoming drives are sufficiently similar share one representative transition; clusters split when an explicit error criterion is violated. Representative states can be augmented with low-rank residual bases, while ensemble-wide low-rank factorizations can reduce repeated applications of the shared sparse operator. Because the recurrence is nonlinear, low-rank compression alone is insufficient; the paper therefore considers localized hyper-reduction methods such as DEIM as a possible second stage.

The central mathematical observation is simple. For a leaky recurrence

\[
x^+ = (1-\lambda)x + \lambda\tanh(Wx + Bu),
\]

`tanh` is 1-Lipschitz, so two nearby states obey the one-step bound

\[
\|F(x,u)-F(y,v)\|
\le
\bigl((1-\lambda)+\lambda\|W\|\bigr)\|x-y\|
+\lambda\|B\|\|u-v\|.
\]

For a block-partitioned connectome this becomes a regional bound that depends on local state dispersion and incoming boundary dispersion. This supplies a principled analogue of a Barnes-Hut opening criterion: use a shared representative only while the worst-case propagated error remains below a chosen tolerance.

The proposal has a hard limit. If every full neuron-by-agent state must be materialized exactly at every step, merely writing those states costs \(\Omega(NF)\) for \(N\) neurons and \(F\) agents. Sublinear-in-\(F\) simulation therefore requires either approximation, compressed state storage, selective reconstruction, or a weaker output contract. This lower-bound observation is important because it prevents a misleading “one brain update for a million flies” claim.

The paper defines exact baselines, a hierarchical regional state-sharing algorithm, a cluster-plus-low-rank residual variant, an ensemble low-rank formulation, adaptive regional timesteps, and complementary world-level accelerations such as Barnes-Hut and particle-mesh fields. It then specifies experiments designed to answer the key empirical question: **does a large ensemble of MaleCNS-like recurrent systems actually collapse onto far fewer effective regional states than the number of simulated individuals, at tolerances small enough to preserve behavior?**

## 1. Motivation: one graph, many neural trajectories

The recently published MaleCNS resource provides a complete adult male *Drosophila melanogaster* CNS connectome. The Cell paper reports 166,700 neurons in the resource; the proofread graph with superclass annotations contains 25.58 million neuron-to-neuron edges between 166,483 neurons, and a threshold of at least five synapses leaves 6.24 million edges between 165,536 neurons [1]. Those figures describe the biological resource, not any particular reduced simulator.

The motivating engineering prototype is FlyDoom, a browser simulation that derives a compact recurrent operator from MaleCNS and couples simulated sensory populations to a small 3D arena. Its current implementation is useful here not as scientific evidence for state sharing but as a concrete systems target: one fixed sparse neural graph is already reused across multiple simulated flies, while each fly carries its own neural state.

For one agent, the main recurrent cost is approximately a sparse matrix-vector product plus a pointwise nonlinearity. For \(F\) agents with the same recurrent matrix \(W\), let

\[
X_t = [x_t^{(1)},x_t^{(2)},\ldots,x_t^{(F)}]\in\mathbb{R}^{N\times F}
\]

collect all neural states and let

\[
U_t=[u_t^{(1)},\ldots,u_t^{(F)}]
\]

collect the inputs. A common leaky-rate abstraction is

\[
X_{t+1}=(1-\lambda)X_t+
\lambda\,\phi(WX_t+BU_t),
\]

where \(\phi\) acts elementwise.

The naive implementation performs \(F\) sparse matrix-vector products. A better exact baseline performs one sparse-matrix/dense-matrix product (SpMM), loading the shared sparse graph once while processing multiple state columns. This preserves the same \(O(FE)\) arithmetic count for \(E\) recurrent edges but can improve cache use, vectorization, and memory-bandwidth amortization substantially. Any approximate state-sharing method should therefore be compared against a strong batched SpMM implementation, not against an intentionally poor loop over agents.

The deeper question is whether \(X_t\) contains much less information than its raw \(N\times F\) shape suggests.

If many agents experience related environments, share initialization statistics, and evolve under the same strongly structured dynamics, then for some brain region \(R\) the set

\[
\{x_{t,R}^{(1)},\ldots,x_{t,R}^{(F)}\}
\]

may occupy only a small number of neighborhoods or a low-dimensional manifold. If that is true, simulation can potentially scale with the number of **distinct effective regional states** instead of the number of agents.

That is the hypothesis tested here.

## 2. What Barnes-Hut contributes — and what it does not

Barnes and Hut reduced the cost of gravitational N-body force evaluation by recursively partitioning physical space and replacing sufficiently distant groups of particles by aggregate summaries [2]. The key computational idea is not gravity itself. It is **adaptive hierarchical approximation**:

1. build a hierarchy;
2. define a criterion that determines when an aggregate is accurate enough;
3. descend to finer detail only where the aggregate is insufficient.

The proposed neural method borrows that pattern, not the force law.

There is no pairwise inverse-square interaction between simulated flies inside the recurrent update. A fly's brain state is transformed primarily by the shared graph \(W\), not by summing pairwise interactions with other flies. Therefore a literal Barnes-Hut tree over flies' neural states does not automatically reduce the sparse recurrent computation.

A useful analogue requires a different aggregation object. Instead of summarizing **the influence of many particles on one particle**, we summarize **many similar input states to the same transition operator**.

The analogy is:

| N-body simulation | Connectome ensemble |
| --- | --- |
| particle position | regional neural state + incoming drive |
| spatial cell | state-space cluster |
| center of mass / multipole | representative state + residual basis |
| opening criterion | propagated neural-error criterion |
| descend when cell too coarse | split cluster when predicted error too large |
| one aggregate interaction | one representative regional transition |

The Fast Multipole Method (FMM) shows a related principle at higher approximation order: groups can be represented by structured expansions rather than a single monopole summary [3]. In the neural setting, a low-rank residual basis plays an analogous computational role. The analogy remains conceptual, not a mathematical equivalence.

## 3. Exact baselines before approximation

Approximation should only be attempted after extracting exact sharing already present in the problem.

### 3.1 Batched sparse recurrence

Because all flies use the same \(W\), compute

\[
Z=WX
\]

as one sparse-matrix/dense-matrix multiplication. For CPU implementations, the state layout should be tested in both forms:

- agent-major: independent contiguous state vectors;
- neuron-major: states for several agents adjacent in memory, enabling SIMD lanes to process multiple flies while each edge is decoded once.

The second layout is particularly attractive for a compact edge representation because a single weight and column index can feed several agent lanes.

### 3.2 Fixed-width specializations

For small common ensemble widths — 1, 2, 4, 8, 16 — fixed-width kernels can remove inner-loop bounds checks and enable explicit SIMD. A WebAssembly SIMD kernel or native AVX2/AVX-512 implementation is a natural exact baseline.

### 3.3 Sparse sensory drives

In embodied simulations, only a subset of neurons receives direct sensory drive at each tick. Clearing a full \(N\)-element drive vector for every fly is unnecessary. Maintain a touched-index list, clear only previously written positions, or fuse sensory injection into the affected recurrent rows. This is an exact optimization.

### 3.4 Representation ablations

Compact formats must be benchmarked independently. A packed 4-bit weight code can save memory but adds nibble extraction and lookup overhead. An 8-bit codebook index may be faster while still fitting in cache. Similarly, delta-coded indices reduce bytes but impose a serial dependency

\[
\mathrm{col}_{j}=\mathrm{col}_{j-1}+\Delta_j.
\]

Absolute indices cost more memory but may expose more instruction-level parallelism. The experiment should therefore compare identical graphs under:

- 4-bit packed weights;
- 8-bit codebook indices;
- direct float weights;
- 16-bit deltas;
- block-delta schemes with periodic absolute restart points;
- full absolute indices.

Graph pruning, quantization, and state-sharing must not be changed simultaneously when attributing speedups.

## 4. Regional rather than whole-brain sharing

Whole-brain state clustering is unnecessarily strict. Two flies can have nearly identical visual states while differing in olfactory, integrative, or descending-neuron activity. The natural unit is therefore a partition of the connectome into regions or computational blocks.

Let the neuron set be partitioned into regions \(R_1,\ldots,R_M\). Anatomical neuropils, sensory systems, graph communities, or hardware-motivated blocks are all possible partitions. Write the recurrent matrix in blocks \(W_{RS}\), where \(W_{RS}\) maps source region \(S\) into target region \(R\).

For fly \(f\), the preactivation of region \(R\) is

\[
a_R^{(f)} = \sum_S W_{RS}x_S^{(f)} + B_Ru_R^{(f)}.
\]

The update is

\[
x_R^{(f)+}
=(1-\lambda)x_R^{(f)}
+\lambda\phi(a_R^{(f)}).
\]

A clustering method that uses only \(x_R\) can be wrong even if two local states are identical, because different upstream regions can provide different boundary input. The cluster descriptor must therefore summarize both the local state and the incoming conditions.

One practical descriptor is

\[
d_R^{(f)}=
\left[
P_R x_R^{(f)},
q_R^{(f)},
S_R u_R^{(f)}
\right],
\]

where \(P_R\) is a low-dimensional state sketch and \(q_R\) summarizes incoming boundary activity. The sketches can be random projections, PCA/POD coordinates learned from exact pilot runs, or task-specific projections.

The hierarchy is then built over \(d_R^{(f)}\), independently for each region.

This allows a fly to share its visual update with one group, its olfactory update with another, and its motor-region update with no one.

## 5. An explicit opening criterion from the recurrence

The main reason to prefer an error-controlled hierarchy over ad hoc quantization is that the recurrent map supplies a simple bound.

Let

\[
F(x,u)=(1-\lambda)x+\lambda\tanh(Wx+Bu).
\]

Since \(\tanh\) is 1-Lipschitz componentwise,

\[
\|\tanh(p)-\tanh(q)\|\le\|p-q\|.
\]

Therefore

\[
\begin{aligned}
\|F(x,u)-F(y,v)\|
&\le(1-\lambda)\|x-y\|\\
&\quad+\lambda\|W(x-y)+B(u-v)\|\\
&\le\bigl((1-\lambda)+\lambda\|W\|\bigr)\|x-y\|
+\lambda\|B\|\|u-v\|.
\end{aligned}
\]

This is an algebraic consequence of the chosen recurrence, not an empirical result.

For a regional block \(R\), if \(\delta_S\) bounds the state spread of source region \(S\) inside a candidate cluster and \(\delta_{u,R}\) bounds local-input spread, then

\[
\delta_R^+
\le
(1-\lambda)\delta_R
+
\lambda\left(
\sum_S \|W_{RS}\|\delta_S
+
\|B_R\|\delta_{u,R}
\right).
\]

This suggests a direct opening rule:

\[
\boxed{
\text{share region }R\text{ for cluster }C
\quad\text{only if}\quad
\widehat{\delta}_{R,C}^+\le\varepsilon_R
}
\]

for a chosen regional tolerance \(\varepsilon_R\).

The norm bound may be pessimistic. A local Jacobian can tighten it. Let

\[
D=\operatorname{diag}(1-\tanh^2(a)).
\]

Then locally

\[
J_x=(1-\lambda)I+\lambda DW.
\]

Near saturation, entries of \(D\) become small, so two nearby states may contract much more strongly than the global \(\|W\|\) bound predicts. A practical implementation can estimate a local gain from representative preactivations and use the conservative global bound as a fallback.

This is the closest analogue in the proposal to Barnes-Hut's geometric opening parameter \(\theta\): a cluster remains aggregated only while its predicted effect on the next state is below tolerance.

## 6. Hierarchical Regional State Sharing (HRSS)

The first proposed algorithm is intentionally simple.

### 6.1 Per-region hierarchy

At each neural step and for each region:

1. compute or update a compact descriptor for every fly;
2. insert descriptors into a hierarchical tree or recursive k-means structure;
3. estimate cluster dispersion and predicted one-step error;
4. accept clusters whose error bound is below \(\varepsilon_R\);
5. split the others;
6. compute the exact regional transition only for each accepted cluster representative;
7. assign the representative result to cluster members, optionally with residual correction.

The simplest version copies the representative result. This is deliberately aggressive and is useful as an upper bound on attainable sharing, not necessarily as the final method.

### 6.2 Effective state count

Let \(K_R(t,\varepsilon)\) be the number of accepted clusters for region \(R\) at time \(t\). The central empirical quantity is the compression ratio

\[
\rho_R(t,\varepsilon)=\frac{F}{K_R(t,\varepsilon)}.
\]

A second measure captures uneven cluster sizes. If \(p_c=|C_c|/F\), define

\[
K_{\mathrm{eff},R}
=
\exp\left(-\sum_c p_c\log p_c\right).
\]

This entropy-based effective number of states equals the number of clusters when all clusters are equally populated and falls when most flies occupy a few dominant states.

The primary hypothesis is not merely that clustering is possible, but that for behavior-preserving tolerances

\[
K_{\mathrm{eff},R}\ll F
\]

for at least some high-cost regions over substantial fractions of time.

## 7. Representative plus residual: where the speedup really comes from

A representative-only cluster discards individual differences. A natural refinement is

\[
x^{(f)}=\mu_C+r^{(f)},
\]

where \(\mu_C\) is the cluster representative and \(r^{(f)}\) is a residual.

The linear part satisfies

\[
Wx^{(f)}=W\mu_C+Wr^{(f)}.
\]

Computing \(W\mu_C\) once is useful, but computing \(Wr^{(f)}\) exactly for every fly restores the original \(O(FE)\) cost. Therefore “representative + exact residual” is **not** by itself a scaling solution.

A speedup requires the residuals to have additional structure.

### 7.1 Low-rank residual basis within a cluster

Suppose residuals in cluster \(C\) satisfy

\[
R_C=[r^{(1)},\ldots,r^{(|C|)}]
\approx U_C A_C,
\]

with rank \(r_C\ll|C|\). Then

\[
WR_C\approx (WU_C)A_C.
\]

The sparse operator is applied only to the \(r_C\) residual basis vectors rather than every fly. This gives a more faithful neural analogue of replacing a particle group by a higher-order expansion.

The computationally relevant quantity becomes

\[
1+r_C
\]

operator applications per cluster rather than \(|C|\).

### 7.2 First-order residual dynamics

For small residuals,

\[
F(\mu+r,u+\eta)
\approx
F(\mu,u)+J_xr+J_u\eta.
\]

If residuals are represented in a basis, the Jacobian can act on the basis rather than on each individual residual. This remains an approximation because the elementwise nonlinearity varies across agents.

The method should monitor residual growth. A cluster is split or its basis rank increased whenever reconstruction or motor-output error exceeds tolerance.

## 8. Ensemble-wide low-rank dynamics

Instead of many local clusters, consider the entire ensemble matrix

\[
X\in\mathbb{R}^{N\times F}.
\]

If its numerical rank is \(r\ll\min(N,F)\), write

\[
X\approx UC,
\]

with \(U\in\mathbb{R}^{N\times r}\) and \(C\in\mathbb{R}^{r\times F}\). Then

\[
WX\approx(WU)C.
\]

The expensive sparse operator is applied to only \(r\) basis states.

This connects the proposal to dynamical low-rank approximation, which evolves low-rank representations of time-dependent matrices instead of repeatedly recomputing a full factorization [4]. However, the connectome recurrence has a significant complication:

\[
\phi(WUC+BU)
\]

is generally not low rank even when \(UC\) is. An elementwise nonlinearity can rapidly increase numerical rank.

That limitation is central, not incidental. Low-rank state compression will only work if the post-nonlinearity ensemble remains compressible at tolerable rank or if the nonlinearity itself is hyper-reduced.

### 8.1 Hyper-reducing the nonlinearity

Discrete Empirical Interpolation (DEIM) was developed precisely because classical low-rank/POD reduction can leave the cost of nonlinear term evaluation tied to the full system dimension [5]. A DEIM-like method evaluates the nonlinear term at selected coordinates and reconstructs it in a reduced basis. State-space error bounds for POD-DEIM systems have also been developed [6]. Localized DEIM replaces one global nonlinear basis with several local bases specialized to different regions of state space [7], making it especially relevant to the cluster-based proposal here.

A connectome implementation could therefore test:

\[
\text{regional clustering}
+\text{low-rank residuals}
+\text{localized nonlinear hyper-reduction}.
\]

This is a substantially more ambitious method than simple state caching and should not be implemented first.

## 9. A lower bound: exact full-state simulation cannot become free

There is a basic systems constraint that any claim of massive speedup must respect.

If the simulator promises to materialize an independent exact \(N\)-neuron state vector for every one of \(F\) flies after every step, then it must at least write \(NF\) state values. That alone is \(\Omega(NF)\) memory traffic.

Therefore no hierarchical trick can produce truly sublinear-in-\(F\) end-to-end cost while preserving that exact output contract.

A meaningful asymptotic improvement requires one or more of the following:

- approximate state sharing;
- compressed storage such as representative + residual coordinates;
- low-rank ensemble storage;
- reconstruction only for selected neurons or selected agents;
- lower-frequency materialization of full states;
- a behavioral-output contract in which only sensory, descending-neuron, motor, or diagnostic subsets are reconstructed every tick.

This changes the architectural question. The target is not merely a faster matrix multiply; it is a **compressed simulator state representation**.

## 10. Adaptive regional timesteps

State sharing exploits similarity across agents. A separate axis exploits slow change over time.

Not every brain region of every fly needs the same update cadence. A region receiving rapidly changing sensory input may require fine timesteps, while a slowly varying region can be updated less frequently. The simulator can maintain per-region clocks and predict whether skipping an update keeps the local error below tolerance.

A simple policy is:

- update at the fastest cadence after strong sensory or boundary-input change;
- lengthen the interval while state derivatives and local gains remain small;
- force a refresh when the error predictor crosses threshold;
- interpolate or hold the region's outgoing summary between updates.

This resembles multirate integration in spirit, but the discrete recurrent model used in a connectome simulator may not represent a continuous-time physical system. Therefore multirate stepping changes the model semantics unless the recurrence is explicitly interpreted as an integration scheme. It must be treated as an approximation and validated behaviorally.

The interesting interaction is that temporal and ensemble redundancy can reinforce one another. A large quiescent cluster can share both a representative state **and** a slower clock.

## 11. World-level acceleration is complementary

The neural-state proposal addresses repeated brain computation. Large swarms also create external-world costs.

If every fly interacts directly with every other fly, pairwise world interactions cost \(O(F^2)\). That is where literal Barnes-Hut or FMM methods can apply: long-range attraction, repulsion, social fields, or other approximately aggregatable pairwise effects can be evaluated hierarchically [2, 3].

Odor and other environmental fields may be better handled by a particle-mesh or grid method:

1. sources deposit concentration into a spatial grid;
2. diffusion/advection is evolved once for the world;
3. each fly samples the field at antenna positions.

The total architecture therefore has two distinct hierarchies:

- **physical-space hierarchy:** accelerates interactions among agents and environmental fields;
- **neural-state hierarchy:** accelerates repeated transitions through the shared connectome.

They should be benchmarked independently before being combined.

## 12. Proposed implementation ladder

The methods should be attempted in increasing order of conceptual risk.

### Stage A — exact engineering baseline

1. identical graph and recurrence across all variants;
2. batched SpMM instead of independent SpMV loops;
3. neuron-major SIMD layout across flies;
4. sparse sensory-drive clearing;
5. fixed-width kernels for 1/2/4/8/16 flies;
6. 4-bit versus 8-bit versus direct-weight representation ablation;
7. delta-coded versus absolute-index ablation;
8. WebAssembly/native kernels where appropriate.

This stage establishes how much performance is available without approximation.

### Stage B — measurement before optimization

Run exact ensembles and record snapshots. For every candidate region measure:

- pairwise or sampled state distances;
- singular-value spectrum of the regional ensemble matrix;
- effective rank;
- cluster count versus tolerance;
- temporal persistence of clusters;
- correlation between neural distance and motor-output distance.

If the ensemble is not compressible, the project should stop before implementing a complicated approximation.

### Stage C — representative-only regional sharing

Implement HRSS with a conservative error criterion. This is the simplest approximate method and provides the first speed/accuracy frontier.

### Stage D — low-rank residual clusters

For clusters with persistent internal variation, maintain \(r_C\)-dimensional residual bases and increase or decrease rank adaptively.

### Stage E — nonlinear hyper-reduction

Only if the low-rank representation is promising but nonlinear evaluation remains dominant, test DEIM or localized DEIM.

### Stage F — adaptive regional clocks

Add multirate updates only after the spatial/state approximations are understood.

### Stage G — physical-space swarm acceleration

Add Barnes-Hut/FMM or particle-mesh world solvers when fly-fly or field computation becomes a measurable bottleneck.

## 13. Experimental design

### 13.1 Research questions

**RQ1.** At fixed recurrence and sensory workload, how much faster is a strong exact batched implementation than independent per-fly updates?

**RQ2.** Does the number of effective regional states grow substantially more slowly than the number of flies under shared or correlated environments?

**RQ3.** At what neural-error tolerance does hierarchical state sharing produce meaningful speedup, and does that tolerance preserve downstream behavior?

**RQ4.** Do residual matrices inside accepted clusters have low enough rank to justify representative-plus-low-rank updates?

**RQ5.** Does ensemble low rank survive the recurrent nonlinearity, or does rank immediately expand to the point that compression is useless?

**RQ6.** Can localized nonlinear hyper-reduction preserve behavior while reducing the cost of the pointwise nonlinearity and full-state reconstruction?

**RQ7.** Does adaptive regional timing add speedup beyond state sharing without producing unstable or qualitatively altered trajectories?

### 13.2 Ensemble sizes

Use a geometric scale sequence, for example

\[
F\in\{1,2,4,8,16,32,64,128,256,512,1024,2048,\ldots\}
\]

until memory or runtime limits are reached. Browser experiments can stop earlier; a native CPU/GPU runner should continue the scaling study.

### 13.3 Input regimes

At least four regimes are required because redundancy depends strongly on correlation among agents:

1. **synchronized:** identical initial states and identical sensory streams — positive control for maximal sharing;
2. **shared world:** different positions in one arena with correlated sensory statistics;
3. **perturbed:** common trajectory plus controlled input and initial-state noise;
4. **decorrelated/adversarial:** independent sensory streams designed to destroy state similarity — negative control.

A method that only wins in the synchronized positive control has limited practical value.

### 13.4 Neural accuracy metrics

For approximate variants, compare against an exact batched trajectory from the same initial state and input stream:

- mean and maximum regional \(L_2\) error;
- cosine similarity;
- error in descending-neuron activity;
- error in sensory and motor populations;
- divergence time until a specified threshold;
- singular-value and effective-rank drift.

Because recurrent systems can amplify small local differences, one-step error alone is insufficient.

### 13.5 Behavioral metrics

In an embodied arena measure:

- target/prize captures;
- collision rate;
- path efficiency;
- survival or task completion where applicable;
- distribution of steering and thrust outputs;
- pairwise trajectory diversity;
- fraction of flies whose behavioral outcome differs from exact simulation.

A numerically small hidden-state error that changes task outcomes is not acceptable merely because RMSE is low.

### 13.6 Performance metrics

Report separately:

- neural steps per second;
- visual/render FPS;
- p50 and p95 neural-step latency;
- recurrent edges processed per second;
- bytes moved per neural step where measurable;
- peak and resident memory;
- cluster-build cost;
- basis-update cost;
- fraction of total time in sparse recurrence, nonlinearity, clustering, reconstruction, sensing, physics, and rendering.

On native CPU benchmarks, hardware counters for last-level-cache loads/misses, branch misses, and memory bandwidth should be collected where available. Claims that a representation “lives in L3” should be supported by those measurements rather than inferred solely from nominal object size.

### 13.7 Multiple seeds and confidence intervals

Cluster trees, randomized projections, initial states, sensory perturbations, and environment placement can all affect results. Performance and behavior should be reported over multiple seeds with uncertainty intervals. A single attractive run is not evidence for general compression.

## 14. A proposed benchmark matrix

The minimum useful ablation is:

| Variant | Exact recurrence? | Shared graph reads? | State clustering? | Low-rank state? | Hyper-reduced nonlinearity? | Adaptive time? |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| independent SpMV | yes | no | no | no | no | no |
| batched SpMM | yes | yes | no | no | no | no |
| HRSS representative | no | yes | yes | no | no | no |
| HRSS + residual basis | approximate | yes | yes | local | no | no |
| global DLR | approximate | yes | implicit | yes | no | no |
| DLR + DEIM/LDEIM | approximate | yes | implicit/local | yes | yes | no |
| best state-sharing + multirate | approximate | yes | yes | optional | optional | yes |

The graph, weights, recurrence, and sensory streams must remain fixed across rows. Quantization and pruning belong in separate orthogonal ablations.

## 15. Concrete FlyDoom-oriented improvements

The motivating browser implementation exposes several immediate engineering experiments that should precede the more speculative hierarchy.

First, the neural tick and the renderer must be reported separately. A renderer can run at display refresh rate while the neural system advances at a lower biological cadence; isolated kernel throughput is a third number. “FPS” should therefore never stand in for all three.

Second, initialization should avoid unnecessary buffer copies where the platform permits transferables or shared memory. FlatBuffers-style random access to an `ArrayBuffer` does not imply end-to-end zero-copy if the implementation explicitly slices arrays and structured-clones them into a worker.

Third, batched fly state should be laid out for the intended SIMD axis. If one edge is decoded once and applied to multiple flies, neuron-major interleaving can outperform separate fly arrays, especially in WebAssembly SIMD.

Fourth, full sensory-drive clearing should be replaced with sparse touched-index clearing.

Fifth, packed 4-bit weights should be treated as a size optimization whose speed must be measured. An 8-bit lookup representation may trade less than a megabyte of additional edge storage for a cheaper hot loop in a million-edge compact graph; whether that is a win is empirical.

Sixth, graph reordering should be tested. Partitioning or reordering neurons to improve locality of state gathers can reduce the true bottleneck even when the edge array itself fits in cache.

These are exact or representation-level improvements. They provide the correct baseline against which HRSS must earn its complexity.

## 16. Falsifiers

The proposal should be abandoned or narrowed if any of the following holds.

### F1 — effective state count scales linearly

For tolerances small enough to preserve behavior,

\[
K_{\mathrm{eff},R}\approx cF
\]

for most expensive regions. Then there is little cross-agent redundancy to exploit.

### F2 — clusters are too short-lived

If flies constantly change clusters, tree maintenance and basis updates may cost more than the shared transitions save.

### F3 — residual rank is high

If each cluster requires \(r_C\approx|C|\), the multipole-like residual idea collapses back to the exact cost.

### F4 — nonlinearity destroys low rank

If the rank of \(\phi(WX+BU)\) rapidly approaches the ensemble size even when \(X\) is low rank, global dynamical low rank will not scale without aggressive hyper-reduction.

### F5 — behavior is sensitive to tiny state errors

If small numerical errors cause large systematic changes in motor decisions or task outcomes, state sharing may be unsuitable even when hidden-state RMSE looks excellent.

### F6 — exact batching already dominates

If a well-optimized SpMM/SIMD kernel makes recurrent compute a small fraction of total simulation time, approximate neural methods may not be worth their complexity. The bottleneck may instead be world physics, sensory raycasting, rendering, or data movement.

### F7 — regional decomposition does not decouple

If inter-region coupling is so strong that local similarity cannot be assessed without effectively comparing the whole brain, regional sharing loses its advantage.

## 17. Expected qualitative regimes

The strongest compression is expected when many flies share a world, similar morphology, and similar sensor statistics. Visual and olfactory peripheries may then form large clusters even while higher-order or motor states remain diverse.

The weakest compression should occur under intentionally independent input streams and strongly divergent histories. This is useful rather than embarrassing: it identifies the actual boundary of the method.

The most interesting outcome would be heterogeneous compressibility, for example:

\[
K_{\mathrm{visual}}\ll
K_{\mathrm{olfactory}}\ll
K_{\mathrm{central}}\approx F.
\]

Such a result would imply that the right simulator is neither “one state per fly” nor “one state for the swarm,” but a mosaic in which some biological subsystems are shared heavily and others remain individual.

## 18. Scientific interpretation

If strong regional state compression is observed, the first conclusion should remain computational:

> under the tested dynamics and environments, an ensemble of connectome-driven agents occupies a much smaller set of effective regional neural states than the raw number of agents.

It would **not** by itself show that biological flies have only a small number of mental states, nor that the reduced recurrence is a faithful model of *Drosophila* electrophysiology. The simulator inherits topology from the connectome but uses engineered dynamics, state variables, gains, and sensory mappings.

Nevertheless, the result could motivate a broader empirical question. Repeated copies of the same high-dimensional dynamical system under related inputs may concentrate onto low-dimensional attractors or a small family of local state manifolds. Measuring where this happens in a connectome-constrained recurrent system is scientifically interesting independently of whether the method ultimately becomes the fastest implementation.

## 19. Relation to the existing MaleCNS tagging work

This repository already contains a separate empirical line using a frozen MaleCNS-derived reservoir for byte-level legal sequence tagging. That work asks whether biological topology provides useful predictive structure relative to shuffled and byte-only controls. The present paper asks a different question: **given many copies of the same recurrent operator, can their simulation be compressed across copies?**

The two lines can share infrastructure — graph loading, sparse recurrence, controls, GPU/CPU runners — but their claims must remain separate. Better ensemble compression would not imply better task performance from biological topology, and better tagging performance would not imply state-sharing compressibility.

## 20. Minimal first experiment

The first experiment should be intentionally smaller than the full proposal.

1. Use one fixed recurrent graph and one fixed recurrence; do not change pruning or quantization.
2. Generate exact trajectories for \(F\in\{16,64,256,1024\}\) under synchronized, shared-world, perturbed, and decorrelated inputs.
3. Partition neurons into a small number of regions using an existing anatomical label when available, otherwise a fixed graph partition.
4. For each region and each step, compute a 32- or 64-dimensional sketch of every fly state.
5. Cluster the sketches at a sweep of tolerances.
6. Measure \(K_R/F\), cluster lifetime, regional singular spectra, and motor-output dispersion.
7. **Do not approximate the recurrence yet.** This first run only asks whether exploitable redundancy exists.
8. If the answer is positive, implement representative-only HRSS and compare against exact batched SpMM.

This experiment is cheap enough to falsify the central premise before substantial engineering is invested.

## 21. Conclusion

The computational opportunity in a million simulated flies is not that a million brains become one brain. It is that a million copies of the **same transition operator** may repeatedly receive states that occupy far fewer distinct regions of state space than the number of copies suggests.

Barnes-Hut provides the right design instinct: aggregate aggressively where an error criterion says detail is unnecessary, and refine only where local structure matters. In connectome simulation, the natural hierarchy is not physical distance but regional neural-state similarity plus incoming drive. A representative can be enriched by low-rank residual modes; a whole ensemble can sometimes be factorized; nonlinear model-reduction techniques can reduce the remaining full-dimensional work; and adaptive regional clocks can exploit temporal redundancy as well.

The proposal is attractive precisely because it is easy to falsify. If effective state count grows linearly with swarm size, if residual rank stays high, if nonlinearities destroy low rank, or if small state errors alter behavior, then the hierarchy should be rejected. If instead large regions repeatedly collapse into a few persistent state families, the scaling law of many-connectome simulation changes: cost can begin to track **effective neural diversity** rather than raw agent count.

That is the experiment worth running.

## References

1. Jefferis, G. S. X. E. et al. “Sexual dimorphism in the complete Drosophila male central nervous system connectome.” *Cell* 189 (2026), 5504–5526.e15. DOI: https://doi.org/10.1016/j.cell.2026.08.015 . MaleCNS project: https://male-cns.janelia.org/ .
2. Barnes, J., and Hut, P. “A hierarchical O(N log N) force-calculation algorithm.” *Nature* 324 (1986), 446–449. DOI: https://doi.org/10.1038/324446a0 .
3. Greengard, L., and Rokhlin, V. “A fast algorithm for particle simulations.” *Journal of Computational Physics* 73(2) (1987), 325–348. DOI: https://doi.org/10.1016/0021-9991(87)90140-9 .
4. Koch, O., and Lubich, C. “Dynamical Low-Rank Approximation.” *SIAM Journal on Matrix Analysis and Applications* 29(2) (2007), 434–454. DOI: https://doi.org/10.1137/050639703 .
5. Chaturantabut, S., and Sorensen, D. C. “Nonlinear Model Reduction via Discrete Empirical Interpolation.” *SIAM Journal on Scientific Computing* 32(5) (2010), 2737–2764. DOI: https://doi.org/10.1137/090766498 .
6. Chaturantabut, S., and Sorensen, D. C. “A State Space Error Estimate for POD-DEIM Nonlinear Model Reduction.” *SIAM Journal on Numerical Analysis* 50(1) (2012), 46–63. DOI: https://doi.org/10.1137/110822724 .
7. Peherstorfer, B., Butnaru, D., Willcox, K., and Bungartz, H.-J. “Localized Discrete Empirical Interpolation Method.” *SIAM Journal on Scientific Computing* 36(1) (2014). DOI: https://doi.org/10.1137/130924408 .

## Reproducibility note

This document is a research agenda, not a results paper. Future benchmark commits should record the exact connectome artifact hash, recurrent dynamics, region partition, ensemble seeds, sensory traces, hardware, compiler/runtime versions, benchmark harness, and raw per-run results. Approximate methods must always be evaluated against an exact batched baseline using the same graph and inputs.