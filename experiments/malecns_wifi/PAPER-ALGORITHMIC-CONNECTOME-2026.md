---
type: "Scientific Position Paper"
title: "The Algorithmic Connectome: Replacing Biological Neural Wiring with Procedural Topologies"
description: "Position paper deriving the Algorithmic Connectome hypothesis: substituting empirical electron-microscopy wiring matrices with compact parameterized developmental rules evaluated across native and reservoir tasks."
tags: [malecns, drosophila, connectome, procedural-generation, stochastic-block-model, small-world, reservoir-computing, inductive-bias]
timestamp: 2026-09-16T09:00:00-04:00
---

# The Algorithmic Connectome: Replacing Biological Neural Wiring with Procedural Topologies

**Franklin Baldo**  
*September 2026*


---

## Abstract

Recent breakthroughs in whole-brain electron microscopy have produced petabyte-scale wiring diagrams of biological nervous systems, epitomized by the *Drosophila melanogaster* MaleCNS connectome (~165,000 neurons, ~10 million synapses). While treated as empirical ground truth, the functional utility of this static wiring graph exhibits a fundamental double dissociation: it strictly outperforms randomized controls in native sensorimotor feedback tasks (FlyDoom evasive steering, 99.4% vs. 88.7%), yet consistently underperforms degree-preserving null models when driven by arbitrary dense semantic embeddings in reservoir computing tasks (macroAP 0.131 vs. 0.257). 

Here, we propose and investigate the **Algorithmic Connectome Hypothesis**: *the computational efficacy and inductive biases of biological nervous systems do not depend on the exact empirical placement of individual synapses, but are the macroscopic manifestation of a compact, parameterized developmental program.* 

Through parametric degree-preserving edge rewiring ($p \in [0.0, 1.0]$) and procedural graph generative models (Hierarchical Stochastic Block Models over neuropils, spatial distance-decay kernels, and duplication-divergence rules), we map the topological landscape connecting the frozen biological connectome to unconstrained random networks. We demonstrate that the biological graph's restrictive bottleneck for arbitrary signals resists minor stochastic rewiring ($p \le 0.10$), indicating deep modular compartmentalization, and we formulate a framework to substitute brute-force connectomic matrices with closed-form procedural generators that preserve both native behavioral performance and domain-specific inductive biases.

---

## 1. Introduction: The Limits of Empirical Connectomics

The culmination of automated transmission electron microscopy (TEM) and volumetric machine learning reconstruction has made full-organism connectomics an empirical reality. Datasets such as the *Drosophila* Hemibrain, FlyWire, and the full male central nervous system (MaleCNS v1.0) provide complete, cell-identified synaptic graphs.

A prevailing assumption in computational neuroscience and neuromorphic engineering is that biological wiring represents an optimized, universal computational substrate. Under this premise, deploying the frozen connectome as a high-dimensional recurrent reservoir (*Echo State Network* / *Reservoir Computing*) should confer inherent advantages over synthetic random operators.

However, rigorous double-blind confirmatory experiments on MaleCNS reveal a striking **double dissociation**:

1. **Native Sensorimotor Domain (FlyDoom):**  
   When inputs enter through native afferent sensory pathways (optic lobe and central brain sensory neurons) and decode through descending motor pathways, the true biological connectome dramatically surpasses degree-matched null models (99.4% vs. 88.7% evasion success, with a 34x reduction in collisions). Here, evolutionarily tuned topology is paramount.

2. **Arbitrary Semantic Domain (Text-Tagger Reservoir):**  
   When dense, multi-channel semantic embeddings are projected into the same sensory populations and read out via descending channels, the exact opposite occurs: the degree-preserving null model (`degree_null`) outperforms MaleCNS with absolute unanimity across all random seeds (macroAP 0.257 vs. 0.131).

### The Law of Topological Coupling
This divergence demonstrates that a biological connectome is not an omnipotent, general-purpose computation engine. Rather:
> **Synaptic wiring constitutes an extreme, domain-specific inductive bias.**  
> Under native sensorimotor couplings, its modular highways channel reflex dynamics efficiently. Under arbitrary semantic drive, these same biological highways act as informational dams, constricting signal dispersion. Randomizing connections while preserving degree sequences systematically dissolves these evolutionary bottlenecks, restoring full-rank reservoir dispersion.

This finding exposes a fundamental question: **Must we store and simulate 10 million empirical synapses, or can the essential computational properties of the connectome be generated from pure procedure?**

---

## 2. The Algorithmic Connectome Hypothesis

Biological brains do not possess a genetic blueprint large enough to encode each individual synapse. The *Drosophila* genome contains ~14,000 genes, which must specify the development of ~165,000 neurons and ~10,000,000 synaptic connections. Development is necessarily algorithmic: genetic programs establish gradients, cell adhesions, temporal birth-order cascades, and local chemical affinities.

We formalize the **Algorithmic Connectome Hypothesis**:

$$\mathcal{G}_{\text{bio}} \approx \mathcal{P}(\boldsymbol{\theta})$$

where $\mathcal{P}$ is a generative procedural rule governed by a low-dimensional parameter vector $\boldsymbol{\theta} \in \mathbb{R}^k$ ($k \ll |\mathcal{E}|$), such that an ensemble of synthetic networks $\mathcal{G}_{\text{syn}} \sim \mathcal{P}(\boldsymbol{\theta})$ statistically matches $\mathcal{G}_{\text{bio}}$ in both:
1. Native task fitness ($\mathcal{T}_{\text{sensorimotor}}$), and
2. Inductive bias profile ($\mathcal{T}_{\text{reservoir}}$).

---

## 3. Investigating the Topological Continuum: Degree-Preserving Rewiring Sweep

To understand the boundary between biological specialization and generic reservoir dispersion, we introduce a continuous degree-preserving rewiring operator.

### 3.1 Mathematical Formulation
Let $\mathbf{W} \in \mathbb{R}^{n \times n}$ be the sparse adjacency/weight matrix of MaleCNS. For a rewiring fraction $p \in [0.0, 1.0]$:
- A subset of $k = \lfloor p \cdot |\mathcal{E}| \rfloor$ edges is uniformly sampled without replacement.
- The presynaptic origin $j$, the synaptic weight $w_{ij}$, and presynaptic neurotransmitter sign are strictly preserved.
- The postsynaptic targets $\{i\}$ of this subset are permuted uniformly among themselves.
- Parallel edges resulting from collisions are merged additively:
  $$\mathbf{W}_{p} = \text{RowNormalise}\left(\sum_{\text{merged}} \mathbf{W}_{\text{permuted}}\right)$$

This construction ensures that for all $p \in [0, 1]$:
- In-degree sequence is strictly preserved.
- Out-degree sequence is strictly preserved.
- Outgoing weight mass and sign distribution remain invariant.
- At $p = 0.0$: $\mathbf{W}_{0} \equiv \mathbf{W}_{\text{malecns}}$ (intact biology).
- At $p = 1.0$: $\mathbf{W}_{1} \equiv \mathbf{W}_{\text{degree\_null}}$ (configuration model).

### 3.2 Empirical Trajectory ($p$-Sweep Pilot)
Evaluating on the audited nested cross-validation benchmark (17 documents, 355 chunks, 9 legal semantic tags, 7-point gain grid $\rho \in [0.0, 4.0]$, 3 paired seeds `0, 1, 2`, cached run hash `5aa49652c533ab74336d`, raw results in `artifacts/runtime-v1/rewiring-sweep-pilot.json`), we observe:

| Rewiring Fraction ($p$) | State | Mean macroAP | sd | anyAUPRC | Recurrence Gain ($\Delta_{\text{rec}}$) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$p = 0.00$** | Pure MaleCNS | **0.120** | 0.037 | 0.413 | +0.086 |
| **$p = 0.01$** | 1% Perturbation | **0.123** | 0.017 | 0.392 | +0.089 |
| **$p = 0.05$** | 5% Small-World | **0.122** | 0.024 | 0.347 | +0.087 |
| **$p = 0.10$** | 10% Perturbation | **0.114** | 0.011 | 0.391 | +0.079 |
| **$p = 0.25$** | 25% Perturbation | **0.130** | 0.053 | 0.396 | +0.095 |
| **$p = 0.50$** | 50% Hybrid | **0.187** | 0.038 | 0.476 | +0.153 |
| **$p = 1.00$** | Full Degree Null | **0.227** | 0.060 | 0.529 | **+0.193** |

*Note on degree preservation:* As in the canonical configuration model, `partial_degree_preserving_null` strictly preserves degree multisets and presynaptic signs prior to CSR reconstruction; duplicate parallel edges created by random target assignment are merged additively (`merged_parallel_edges`), conserving outgoing synaptic mass per neuron.

#### Analysis: The Apparent Sigmoidal Transition of Biological Modularity
Unlike idealized theoretical lattice networks where a tiny 5% rewiring fraction triggers an immediate collapse in characteristic path length (the classical Watts-Strogatz small-world transition), **the MaleCNS connectome exhibits functional buffering up to $p = 0.10$**. 

Its performance remains stable at $\approx 0.114 - 0.123$ with recurrence gain $\approx +0.08$. The observed trajectory is consistent with a **sigmoidal transition**:
- At $p \le 0.10$: The biological mesoscale compartments (neuropils) appear to buffer and extinguish random shortcut dispersion, maintaining the domain-specific bottleneck.
- At $p = 0.25$: Initial percolation becomes detectable ($\text{macroAP} = 0.130$).
- At $p = 0.50$: A substantial gain in dispersion emerges ($\text{macroAP} = 0.187$, recovering ~70% of recurrence capacity).
- At $p = 1.00$: Unconstrained null dispersion is reached ($\text{macroAP} = 0.227$, $\Delta_{\text{rec}} = +0.193$).

*Epistemic boundary:* While consistent with mesoscale compartmentalization, this pilot sweep identifies functional decoupling rather than direct anatomical causality. Confirmatory 10-seed expansion and targeted neuropil ablation remain necessary to isolate the specific anatomical tracts responsible for this buffering.



---

## 4. Families of Procedural Connectome Generators

Because blind random rewiring fails to capture the structured behavior of the fly until almost all biological information is destroyed, we define four structured procedural generative models to replace empirical EM matrices:

```
                         [DEVELOPMENTAL RULES]
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
   MODEL 1: SBM              MODEL 2: DISTANCE         MODEL 3: HIERARCHICAL
   Neuropilar Block          Exponential Decay         Duplication-Divergence
   Affinity Matrix           $P(u,v) \sim e^{-d/\lambda}$  (Symmetric Hemispheres)
```

### 4.1 Model 1: Neuropilar Stochastic Block Model (SBM)
The brain of *Drosophila* is partitioned into 78 anatomically defined neuropils (e.g., Antennal Lobe, Mushroom Body Calyx, Central Complex, Optic Glomeruli).
- Let $\mathbf{M} \in \mathbb{R}^{78 \times 78}$ be the coarse-grained neuropilar traffic matrix, where $M_{AB}$ is the probability of a synapse from a neuron in neuropil $A$ to neuropil $B$.
- A synthetic connectome is generated by:
  $$P(\text{edge } u \to v) = M_{\text{neuropil}(u), \text{neuropil}(v)} \cdot \frac{k_u^{\text{out}} k_v^{\text{in}}}{\sum_w k_w}$$
- **Compression Accounting:**
  - *Inter-Neuropil Routing Matrix:* Replaces $10^7$ empirical synaptic connections with the coarse $78 \times 78 = 6,084$ block-affinity matrix, achieving a **~1,640x matrix parameter compression**.
  - *Full Generative Specification:* Conditioning on explicit empirical in/out marginal degree sequences for $N = 165,000$ neurons requires an additional $2N \approx 3.3 \times 10^5$ integer values, representing an overall **~30x total state description compression**. If nodal degrees are instead sampled from neuropil-specific parametric distributions (e.g., log-normal or truncated Pareto models with 2 parameters per neuropil, totaling $\approx 312$ floats), the entire generator compresses to under $6,400$ scalars (>1,500x total parametric reduction).

### 4.2 Model 2: Geometric Distance-Decay Kernel (Peters' Rule)
Axons and dendrites arborize in 3D Euclidean space. The probability of axo-dendritic overlap drops with spatial distance:
$$P_{ij} = C \cdot k_i^{\text{out}} k_j^{\text{in}} \cdot \exp\left(-\frac{\|\mathbf{x}_i - \mathbf{x}_j\|_2}{\lambda}\right)$$
where $\mathbf{x}_i \in \mathbb{R}^3$ represents the somatic or neuropilar centroid coordinate, and $\lambda$ is the characteristic axonal projection length.

### 4.3 Model 3: Symmetrical Duplication and Divergence
To reproduce the distinct near-degenerate leading spectral modes observed in MaleCNS (eigenvalues $\lambda_1 = 3776.27, \lambda_2 = 3718.80$ representing left/right hemisphere symmetric and antisymmetric dynamics):
- Generate a left hemisphere seed network via SBM.
- Duplicate symmetrically across the sagittal midline with probability $p_{\text{mirror}}$.
- Introduce commissural bridging fibers across the central complex with probability $p_{\text{chiasm}}$.

---

## 5. The Topological Turing Test: Dual-Benchmark Protocol

To validate whether a procedural model $\mathcal{P}(\boldsymbol{\theta})$ successfully replaces the empirical connectome, it must pass a **Topological Turing Test** across both poles of the double dissociation:

```
                           [PROCEDURAL GRAPH G_syn]
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
         BENCHMARK 1: FlyDoom                      BENCHMARK 2: Text-Tagger
      Sensorimotor Steering                     Reservoir Signal Dispersion
                 │                                         │
        MUST OUTPERFORM NULL                      MUST EXHIBIT BOTTLENECK
         (Evasion Rate > 95%)                      (macroAP ≈ 0.12 - 0.14)
```

1. **Criterion 1 (Competence Preservation):**
   When evaluated in closed-loop FlyDoom under optical-flow sensory drive, $\mathcal{G}_{\text{syn}}$ must achieve an evasion rate comparable to the biological connectome ($> 95\%$) and significantly higher than the unstructured null ($88.7\%$).
   
2. **Criterion 2 (Inductive Bias Fidelity):**
   When evaluated in open-loop reservoir decoding with dense text embeddings, $\mathcal{G}_{\text{syn}}$ must reproduce the specific restrictive bottleneck observed in MaleCNS ($\text{macroAP} \in [0.12, 0.14]$), failing to attain the unconstrained null dispersion ($\text{macroAP} \ge 0.25$).

3. **Criterion 3 (Spectral Geometry):**
   The eigenspectrum of $\mathcal{G}_{\text{syn}}$ must exhibit the characteristic spectral concentration ratio ($\rho / (\sigma / \sqrt{n}) \approx 24.8$ unnormalised, compressible to $\approx 3.4$ via row-normalisation) and isolate the dominant hemispheric pair.

---

## 6. Discussion: Implication for Neuromorphic AI and Evolutionary Robotics

### 6.1 Task-Specific Small-World Rewiring and Development Pruning
Our findings suggest a unified design methodology for brain-inspired computing:
1. **Bootstrap with Algorithmic Scaffold:** Instantiate an ultra-sparse procedural graph governed by an SBM traffic prior.
2. **Task Adaptation via Targeted Rewiring:** Introduce a small budget of directed shortcut bridges ($p \sim 0.05$) specifically targeting bottlenecks between input and output projections.
3. **Activity-Dependent Synaptic Pruning:** Following task exposure, prune inactive or redundant pathways, leaving an ultra-compact, high-efficiency task-specific circuit.

### 6.2 Beyond Empirical Brute-Force Connectomics
While high-resolution electron microscopy is indispensable for establishing initial anatomical baselines, running and scaling neuromorphic architectures on raw synaptic point-clouds is computationally intractable and conceptually limited. By identifying the procedural laws that generate functional neural topologies, we transition from *descriptive anatomy* to *generative neuro-engineering*.

### 6.3 Cross-Scale Procedural Conservation: Testing Common Topological Grammars
A profound implication of the algorithmic connectome is investigating whether topological principles are conserved across phylogenetic lineages and developmental scales:

1. **The Organism Library Across Scales:**
   Modern automated electron microscopy and volumetric reconstructions now span distinct phylogenetic lineages across orders of magnitude in neuron count:
   - *Caenorhabditis elegans* (~302 neurons, ~7,000 synapses): The canonical compact reflex circuit.
   - *Drosophila melanogaster* larva (~3,016 neurons, ~548,000 synapses): Larval sensory-motor coordination.
   - *Drosophila melanogaster* adult (MaleCNS v1.0 & FlyWire, ~139,000–165,000 neurons, ~10M synapses): The full adult central nervous system featuring rich-club organization, recurring motifs, and modular neuropilar highways.
   - Mouse visual cortex (MICrONS, >200,000 reconstructed cells, ~500M synapses): Mammalian laminar neocortex bridging structural connectivity and functional response properties.

2. **The Cross-Scale Procedural Conservation Hypothesis:**
   We avoid claiming an untestable "universal law" and instead formulate a rigorous, falsifiable hypothesis:
   > **Cross-scale procedural conservation hypothesis:** after coarse-graining each nervous system into its native mesoscopic compartments, a low-dimensional family of generative rules predicts held-out topological and dynamical observables across species better than matched null models, without organism-specific refitting of the rule family.

3. **From Connectome Compression to a Generative Neural Language:**
   Under this formulation, the *Algorithmic Connectome* transcends the narrow task of "compressing the fly connectome." It defines a **compact generative language capable of describing families of nervous systems across scales**. This reframing motivates the autopoietic question of Section 7: *can an in silico nervous system infer and synthesize its own minimal description within this shared generative language?*

---

## 7. Autopoietic Neural Morphogenesis: In Silico Connectome Self-Compilation

The ultimate instantiation of this paradigm is an **autopoietic self-replacement loop**:  
*Can a computational model of the MaleCNS connectome actively parameterize and control the procedural engine that synthesizes its own replacement, transferring its functional identity without behavioral loss?*

Critically, **the primary continuous supervisor of this synthesis is not an external environment (FlyDoom), but the brain model's own intrinsic neural activity manifold.** Simulation in an external behavioral simulator is computationally expensive and captures only low-dimensional outputs (steering, collisions). Instead, the synthetic connectome is continuously optimized to reproduce the **high-dimensional latent dynamics and stochastic transition operators** of the in silico biological model, with behavioral tasks evaluated only as sparse, downstream verification gates.

```
                  ┌───────────────────────────────────────────────────────────┐
                  │        In Silico MaleCNS v1.0 Model / Substrate           │
                  │             Spontaneous & Evoked Neural Trajectories      │
                  └─────────────┬─────────────────────────────┬───────────────┘
                                │                             │
             Latent Manifold    │                             │ Output Control
             Signature:         ▼                             ▼ θ_t = R(h_t)
            H_bio = {x_t} ──► [ DENSE CONTINUOUS ] ◄── H_syn  │
                              [ MARKOV & MANIFOLD]            │
                              [     ARBITER      ]            ▼
                                      │              ┌────────────────────────┐
                             Divergence Loss         │ Procedural Generator   │
                             ∇_θ L_intrinsic ──────► │ P(θ): SBM + Dist + Rew │
                                                     └───────────┬────────────┘
                                                                 │ Produces G*
                                                                 ▼
                                                     ┌────────────────────────┐
                                                     │ Synthetic Brain G*     │
                                                     └───────────┬────────────┘
                                                                 │
                                                    Sparse Check │ (Every K cycles)
                                                                 ▼
                                                     ┌────────────────────────┐
                                                     │ Sparse Behavior Gate:  │
                                                     │ FlyDoom Evasion > 98%  │
                                                     └────────────────────────┘
```

### 7.1 The Dense Intrinsic Arbiter: Neural Manifold Alignment & Markov State Operators
Instead of relying on sparse, high-latency behavioral simulations, the primary loss function is computed directly over the **state-space trajectories and stochastic transition dynamics** of the network:
$$\mathcal{L}_{\text{intrinsic}}(\mathcal{G}^*, \mathcal{G}_{\text{bio}}) = \mathcal{D}_{\text{Markov}}\left(\mathbf{T}_{\text{bio}}, \mathbf{T}_{\text{syn}}\right) + \mathcal{D}_{\text{manifold}}\left(\mathbf{X}_{\text{bio}}, \mathbf{X}_{\text{syn}}\right) + \alpha \cdot \text{KL}\left(P_{\text{spectrum}}(\mathcal{G}^*) \,\|\, P_{\text{spectrum}}(\mathcal{G}_{\text{bio}})\right)$$

Where the comparison is executed at two distinct levels:

#### A. The Markov Transition Operator ($\mathcal{D}_{\text{Markov}}$)
A neural circuit operating in noisy regime induces a continuous-time Markov jump process or a discrete transition matrix $\mathbf{T} \in \mathbb{R}^{K \times K}$ over discretized neural population states (metastable microstates / attractors).

- **Frozen Biological Codebook Protocol:**
  To guarantee that operator divergence $\|\mathbf{T}_{\text{bio}} - \mathbf{T}_{\text{syn}}\|_F^2$ is mathematically well-defined, the $K$ discrete microstates must share identical identities and geometric boundaries across both biological and synthetic trajectories. Independent clustering assigns arbitrary permutation labels to clusters, rendering direct matrix subtraction meaningless.
  
  To eliminate arbitrary degrees of freedom and ensure strict pre-registration, we establish a frozen projection protocol:
  $$\text{fit } \mathcal{C}^*_{\text{bio}} \text{ on biological train} \longrightarrow \text{freeze } \mathcal{C}^*_{\text{bio}} \longrightarrow \text{encode } (\text{bio}, \text{syn}, \text{null}) \longrightarrow \text{estimate } \mathbf{T}, \boldsymbol{\pi} \longrightarrow \text{compare held-out transitions}$$
  
  Specifically, we train a vector quantizer $\mathcal{C}^*_{\text{bio}}$ strictly on latent trajectories from the biological reference model under training sensory drive:
  $$\mathcal{C}^*_{\text{bio}} = \arg\min_{\mathcal{C}} \sum_{\mathbf{x} \in \mathbf{X}_{\text{bio}}^{\text{train}}} \min_{c_k \in \mathcal{C}} \|\mathbf{x} - c_k\|_2^2$$
  The codebook $\mathcal{C}^*_{\text{bio}}$ is then **frozen**. Both held-out biological trajectories and synthetic surrogate trajectories are projected into these fixed microstate boundaries, yielding aligned state sequences $\mathbf{s}_t^{\text{bio}}, \mathbf{s}_t^{\text{syn}} \in \{1, \dots, K\}$:
  $$T_{ij} = P(\mathbf{s}_{t+1} = j \mid \mathbf{s}_t = i)$$

- **Transition Operator Divergence:**
  We evaluate operator divergence over the shared, frozen state space via:
  $$\mathcal{D}_{\text{Markov}} = \|\mathbf{T}_{\text{bio}} - \mathbf{T}_{\text{syn}}\|_F^2 + D_{\text{JS}}(\boldsymbol{\pi}_{\text{bio}} \,\|\, \boldsymbol{\pi}_{\text{syn}})$$
  where $\boldsymbol{\pi}$ is the empirical stationary distribution over the frozen microstate codebook, and $D_{\text{JS}}$ is the symmetric Jensen-Shannon divergence.
- **Why Markov Operators are Superior to Video Games (FlyDoom):**
  - Completely analytical, deterministic, and computable in milliseconds via matrix operations.
  - Captures the exact probabilistic grammar of state switching, refractory periods, and attractor hopping without needing a 3D graphics or physics simulator in the loop.

#### B. The Geometric Manifold Alignment ($\mathcal{D}_{\text{manifold}}$)
1. **Centered Kernel Alignment (CKA) / Representational Similarity Analysis (RSA):** Preserving the relative geometry of neural population responses across sensory states.
2. **Wasserstein-2 Distance between Trajectory Attractors:** Ensuring the synthetic reservoir shares the same fixed points, limit cycles, and chaos boundaries.
3. **Spectral Density Invariance:** Enforcing the dominant hemispheric mode split ($\lambda_1 \approx \lambda_2 \approx 3.7 \times 10^3$) without needing to inspect individual synapses.

### 7.2 The Sparse Behavioral Gate (FlyDoom as Sanity Check)
Because the Markov transition operator and manifold alignment preserve the microscopic state-switching probabilities and geometry, the embodied closed-loop simulation (FlyDoom) is required only as a **sparse assertion gate** (e.g., evaluated once upon convergence of $\mathcal{D}_{\text{Markov}}$):
$$\text{Gate}(\mathcal{G}^*) = \mathbb{I}\left[\text{EvasionRate}_{\text{FlyDoom}}(\mathcal{G}^*) \ge 0.95 \;\land\; \text{Collisions} \le 2\right]$$

This decouples the optimization from simulation engine overhead:
- **Optimization Loop:** 100% analytical Markov Chain and spectral divergence matching.
- **Verification Gate:** Rare, sanity-check deployment in the sensorimotor world.

### 7.3 Epistemic Assessment: Self-Parameterized Procedural Surrogates
By using the neural activity manifold and shared Markov transition operators as arbiters, we evaluate the viability of procedural surrogate compilation:
- Rather than asserting metaphysical substrate independence, this framework demonstrates **functional equivalence across synthetic surrogates under pre-registered dynamical and behavioral observables**.
- The computational MaleCNS model acts as an **autopoietic compiler**: it compresses its own 10-million-synapse anatomy into a low-dimensional generative code $\boldsymbol{\theta}$, proves that its internal dynamics are preserved, and confirms survival in the external world.


---

## 8. Experimental Roadmap: Four Concrete Designs

To empirically validate and falsify the claims of this position paper, we establish four targeted experimental designs:

```
  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
  │  EXPERIMENT 1   │       │  EXPERIMENT 2   │       │  EXPERIMENT 3   │       │  EXPERIMENT 4   │
  │ Massive-Scale   ├──────►│ SBM Neuropil    ├──────►│ Markov Chain    ├──────►│ Autopoietic     │
  │ MultiEURLEX 62k │       │ Procedural Graph│       │ Analytical Loss │       │ Closed Loop     │
  │ (MTEB Benchmark)│       │ (1,600x Compress│       │ (T_bio vs T_syn)│       │ (Self-Compiler) │
  └─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

### 8.1 Experiment 1: The Massive-Scale MultiEURLEX-21 Benchmark
- **Objective:** Eliminate sample-size and corpus-formulaicity caveats by testing the biological bottleneck on a standardized international benchmark.
- **Corpus & Scale:** MultiEURLEX Portuguese legal subset (`mteb/eurlex-multilingual`, cached at `franklinbaldo/multieurlex21-pt-semantic-cache`), comprising **62,370 documents**, **120,590 chunks**, and 21 EuroVoc labels. Precomputed 768-dimensional dual embeddings (MiniLM-L12-v2 + e5-small).
- **Protocol:** Evaluate a frozen sample of 1,000 test chunks across `direct_raw`, `malecns`, `degree_null`, and intermediate rewiring points ($p \in \{0.10, 0.50\}$).
- **Falsification Criterion:** If the performance gap between `degree_null` and `malecns` evaporates at scale ($\Delta \to 0$), the bottleneck was a sample-size artifact. If `degree_null` maintains its $\approx 2\times$ superiority across 62,000 documents and diverse EuroVoc topics, it firmly rules out small-corpus and drafting-formulaicity artifacts, establishing that domain-specific inductive bottlenecking is an inherent property of the biological connectome when driven by dense semantic embeddings.

### 8.2 Experiment 2: The Neuropilar SBM Procedural Graph & Frozen Markov State Codebook
- **Objective:** Determine if a coarse $78 \times 78$ block-affinity traffic matrix between anatomical neuropils can replace 10 million individual empirical synapses, evaluated directly via analytical Markov Chain operator divergence against a frozen biological state codebook without simulator overhead.
- **Protocol:**
  1. Compute the empirical inter-neuropil transition probability matrix $\mathbf{M} \in [0, 1]^{78 \times 78}$ from `graph.npz`.
  2. Sample synthetic adjacency graphs $\mathcal{G}_{\text{SBM}}$ conditioned on $\mathbf{M}$ and marginal in/out-degree sequences. We distinguish between *connectivity matrix compression* (~1,640× reduction, $78 \times 78 = 6,084$ inter-neuropil weights vs. $10^7$ edges) and *total generative state description* (~30× reduction if preserving explicit per-neuron degree sequences; >1,000× if nodal degrees are drawn from neuropil-specific parametric distributions).
  3. **Markov Discretization and Freezing Pipeline:**
     $$\text{fit shared codebook on bio train} \longrightarrow \text{freeze} \longrightarrow \text{encode bio/SBM/null} \longrightarrow \text{estimate } \mathbf{T}, \boldsymbol{\pi} \longrightarrow \text{compare held-out transitions}$$
     - *Fit Biological Codebook:* Discretize continuous latent trajectories into $K = 64$ metastable attractors by training a vector quantizer $\mathcal{C}^*_{\text{bio}}$ strictly on biological training runs under continuous sensory regimes.
     - *Freeze & Encode:* Freeze $\mathcal{C}^*_{\text{bio}}$ and project held-out trajectories of the empirical connectome model, $\mathcal{G}_{\text{SBM}}$, and degree-null baselines into the exact same microstate boundaries, guaranteeing identical state identities across all models without post-hoc alignment heuristics.
     - *Estimate Transitions:* Compute empirical transition matrices ($\mathbf{T}_{\text{bio}}, \mathbf{T}_{\text{SBM}}, \mathbf{T}_{\text{null}}$) and stationary distributions ($\boldsymbol{\pi}_{\text{bio}}, \boldsymbol{\pi}_{\text{SBM}}, \boldsymbol{\pi}_{\text{null}}$) on held-out evaluation sets.
  4. Evaluate $\mathcal{G}_{\text{SBM}}$ across the dual criteria:
     - **Dynamic Syntax Fidelity ($\mathcal{D}_{\text{Markov}}$):** $\mathcal{G}_{\text{SBM}}$ must closely match the empirical state-transition operator over the frozen codebook ($\|\mathbf{T}_{\text{bio}} - \mathbf{T}_{\text{SBM}}\|_F \to 0$ and $D_{\text{JS}}(\boldsymbol{\pi}_{\text{bio}} \,\|\, \boldsymbol{\pi}_{\text{SBM}}) \approx 0$), whereas unstructured random nulls (`degree_null`) produce isotropic, divergent transitions.
     - **Semantic Bottleneck Replication (Text-Tagger):** $\mathcal{G}_{\text{SBM}}$ must preserve the domain-specific inductive bottleneck ($\text{macroAP} \in [0.11, 0.14]$).
- **Significance:** Establishes a rigorous, pre-registrable Markov ruler without free parameters: macroscopic neuropilar routing alone accounts for both the temporal syntax of brain state switching and the semantic information bottleneck.

### 8.3 Experiment 3: Testing Cross-Scale Procedural Conservation Across Species
- **Objective:** Subject the *Cross-Scale Procedural Conservation Hypothesis* to strict empirical falsification by testing whether a low-dimensional generative grammar extracted from one nervous system predicts held-out topological and dynamical invariants in another without species-specific refitting.
- **Experimental Protocol in Three Levels:**
  1. **Level 1: Native Biologically Grounded Mesoscopic Partitioning:**
     To avoid inventing artificial anatomical homologies (e.g. equating insect neuropils with mammalian cortical layers), each nervous system is partitioned strictly according to its native biological mesoscale:
     - *C. elegans* (~302 neurons): functional ganglia and circuit modules.
     - *Drosophila* larva (~3,016 neurons): larval neuropils, brain lobes, and VNC segments.
     - *Drosophila* adult (MaleCNS & FlyWire, ~139k–165k neurons): 78 canonical neuropils.
     - Mouse visual cortex (MICrONS, >200,000 cells): 6 cortical layers $\times$ retinotopic visual areas / columnar subvolumes.
     *The formal generative grammar transfers across species; anatomical homologies do not.*

  2. **Level 2: Dimensionless Scale-Invariant Representations & Power-Law Scaling:**
     Transform each mesoscopic traffic matrix into a dimensionless row-stochastic routing operator:
     $$\widehat{\mathbf{M}} = \mathbf{D}_{\text{out}}^{-1} \mathbf{M}, \quad \text{where } D_{\text{out}, ii} = \sum_j M_{ij}$$
     We compare scale-invariant topological observables across three orders of magnitude in $N$:
     - Spectral gap $\Delta \lambda = 1 - |\lambda_2|$, mixing time $\tau_{\text{mix}}$, and leading spectral density profile.
     - Graph modularity $Q$, transition entropy rate $H(\mathbf{T})$, and effective embedding dimensionality.
     - *Scaling Hypothesis Formulation:* Rather than imposing an ad-hoc normalizer such as $\log N$, we explicitly formulate and test scaling hypotheses as power laws $q(N) \propto N^\alpha$, evaluating curve collapse across pre-registered alternative normalizations.

  3. **Level 3: Predictive Cross-Scale Transfer Without Refitting:**
     We execute directional out-of-distribution transfer:
     $$\mathcal{P}_{\text{larva}}(\boldsymbol{\theta}) \xrightarrow{\text{scale } N} \mathcal{G}_{\text{adult}}^{\text{pred}}$$
     and evaluate whether the un-refitted predicted graph $\mathcal{G}_{\text{adult}}^{\text{pred}}$ matches empirical adult MaleCNS/FlyWire properties.
     - *Strict Matched Null Controls:* Baselines include not only Erdős–Rényi graphs, but strictly constrained null models preserving degree sequences, density, block partitions, and spatial distance-decay kernels.
     - *Falsification Criterion:* If the procedural grammar $\mathcal{P}_{\text{larva}}$ transferred to adult scale fails to predict held-out adult observables (spectral gap, modularity, and Markov stationary entropy $\boldsymbol{\pi}$) significantly better than the matched null controls, the Cross-Scale Procedural Conservation Hypothesis is rejected.

- **Secondary Exploratory Ablation (Cortical Laminar Loop Insertion):**
  - Treated as an independent architectural ablation rather than evidence of phylogenetic transfer: graft mammalian cortical laminar microcircuit motifs (MICrONS-derived feedback loops) into the fly reservoir.
  - Test whether columnar/laminar feedback can break the dense semantic bottleneck without destabilizing baseline sensorimotor evasion dynamics.

### 8.4 Experiment 4: Closed-Loop Autopoietic Neural Morphogenesis
- **Objective:** Operational demonstration of a computational MaleCNS connectome model acting as the self-compiler of its own procedural surrogate.
- **Protocol:**
  1. Wire the 1,314 descending motor neurons of MaleCNS through a linear readout layer to parameterize the procedural compiler: $\boldsymbol{\theta}_t = \sigma(\mathbf{W}_{\text{readout}} \cdot \mathbf{h}_{\text{descending}})$.
  2. $\boldsymbol{\theta}_t$ directly modulates the SBM matrix $\mathbf{M}$, spatial projection scale $\lambda$, and shortcut density $p$.
  3. Optimize $\mathbf{W}_{\text{readout}}$ via evolution strategy (CMA-ES) to minimize:
     $$\mathcal{L} = \mathcal{D}_{\text{Markov}}(\mathbf{T}_{\text{bio}}, \mathbf{T}^*(\boldsymbol{\theta})) + \beta \cdot \text{Cost}(\mathcal{G}^*)$$
  4. Deploy the converged synthetic network $\mathcal{G}^*$ to the sparse behavioral verification gate (FlyDoom evasion $\ge 95\%$).
- **Significance:** Demonstrates a self-parameterized procedural surrogate preserving pre-registered dynamical and behavioral observables: the neural model compiles a compact generative rule that retains its own dynamical identity.



## References

1. Schlegel, P., et al. (2024). Whole-brain connectome of *Drosophila melanogaster*. *Nature*, 634, 139–152.
2. Dorkenwald, S., et al. (2024). Neuronal wiring diagram of an adult brain. *Nature*, 634, 124–138.
3. Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. *Nature*, 393(6684), 440–442.
4. Jaeger, H. (2001). The "echo state" approach to analysing and training recurrent neural networks. *GMD Report 148*.
5. Baldo, F. (2026). MaleCNS Reservoir — Compile, Control and Document-Task Protocol v1. *Papers / Experiments / MaleCNS*.
6. Franke, K., et al. (2024). Universal principles of axonal wiring and developmental economy across insect central complexes. *Current Biology*.
7. The MICrONS Consortium (2021). Functional connectomics spanning multiple areas of mouse visual cortex. *bioRxiv / Nature*.
