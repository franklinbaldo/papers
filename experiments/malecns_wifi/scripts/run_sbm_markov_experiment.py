"""Experiment 2: Neuropilar SBM Procedural Graph & Frozen Markov State Codebook.

Protocol:
1. Generate procedural models:
   - Bio: intact MaleCNS (p=0.0)
   - SBM: Neuropilar Block-Constrained Model (M matrix preserved)
   - Rewired p=0.10: 10% degree-preserving rewiring
   - Rewired p=0.50: 50% degree-preserving rewiring
   - Degree Null: 100% degree-preserving rewiring (p=1.0)
2. Drive biological reference on continuous training sensory trajectories.
3. Fit K=32 state vector quantizer (codebook C*_bio) on biological train -> FREEZE codebook.
4. Project held-out trajectories of Bio, SBM, Rewired p=0.10, Rewired p=0.50, and Degree Null
   onto the frozen codebook.
5. Estimate transition matrices T and stationary distributions pi.
6. Evaluate:
   - State Repertoire Size (number of active states)
   - Stationary Entropy H(pi)
   - Markov Operator Divergence: ||T_bio - T_M||_F^2 + D_JS(pi_bio || pi_M)
   - Centered Kernel Alignment (CKA) over continuous trajectories
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.cluster.vq import kmeans2, vq
from scipy.spatial.distance import jensenshannon

from malecns_wifi.characterize import partial_degree_preserving_null
from malecns_wifi.tagger import row_normalise, select_populations


def linear_cka(X: np.ndarray, Y: np.ndarray) -> float:
    """Centered Kernel Alignment (linear CKA) between two trajectory matrices (T x D)."""
    X = X - X.mean(axis=0, keepdims=True)
    Y = Y - Y.mean(axis=0, keepdims=True)
    K = X @ X.T
    L = Y @ Y.T
    hsic_kl = np.sum(K * L)
    hsic_kk = np.sum(K * K)
    hsic_ll = np.sum(L * L)
    denom = np.sqrt(hsic_kk * hsic_ll)
    return float(hsic_kl / max(denom, 1e-12))


def build_sbm_matrix(W_raw: sp.csr_matrix, block_ids: np.ndarray, seed: int = 42) -> sp.csr_matrix:
    """Generate Degree-Corrected SBM with exact block-traffic matrix M."""
    coo = W_raw.tocoo()
    rng = np.random.default_rng(seed)
    new_rows = coo.row.copy()
    target_blocks = block_ids[coo.row]
    B = int(block_ids.max() + 1)
    for b in range(B):
        mask = (target_blocks == b)
        if mask.sum() > 1:
            new_rows[mask] = rng.permutation(new_rows[mask])
    sbm = sp.csr_matrix((coo.data, (new_rows, coo.col)), shape=W_raw.shape, dtype=np.float32)
    sbm.sum_duplicates()
    return sbm


def simulate_trajectories(
    operators: dict[str, sp.csr_matrix],
    inputs: np.ndarray,
    readout: np.ndarray,
    u_seq: np.ndarray,
    *,
    gain: float = 1.2,
    leak: float = 0.4,
    seed: int = 0,
) -> dict[str, np.ndarray]:
    """Drive multiple operators with the exact same input stream and input projection."""
    steps, dim_in = u_seq.shape
    n_inputs = len(inputs)
    rng = np.random.default_rng(seed)
    w_in = rng.normal(0.0, 0.05, size=(n_inputs, dim_in)).astype(np.float32)

    trajectories = {}
    for name, W in operators.items():
        n = W.shape[0]
        state = np.zeros(n, dtype=np.float32)
        traj = np.zeros((steps, len(readout)), dtype=np.float32)
        for t in range(steps):
            ext = np.zeros(n, dtype=np.float32)
            ext[inputs] = w_in @ u_seq[t]
            rec = W @ state
            state = ((1.0 - leak) * state + leak * np.tanh(gain * rec + ext)).astype(np.float32)
            traj[t] = state[readout]
        trajectories[name] = traj
    return trajectories


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=Path("artifacts/runtime-v1/graph.npz"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/runtime-v1/sbm-markov-results.json"))
    parser.add_argument("--k-states", type=int, default=32)
    parser.add_argument("--t-train", type=int, default=1500)
    parser.add_argument("--t-test", type=int, default=1500)
    parser.add_argument("--dim-in", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gain", type=float, default=1.2)
    parser.add_argument("--leak", type=float, default=0.4)
    args = parser.parse_args()

    print(f"Loading graph from {args.graph}...")
    t0 = time.time()
    d = np.load(args.graph)
    shape = tuple(int(x) for x in d["shape"])
    W_raw = sp.csr_matrix((d["data"], d["indices"], d["indptr"]), shape=shape)
    print(f"Graph loaded in {time.time()-t0:.2f}s (N={shape[0]}, NNZ={W_raw.nnz})")

    pops = select_populations(d["superclass"])
    inputs, readout = pops.input_indices, pops.readout_indices
    print(f"Ingress: {len(inputs)} sensory neurons | Egress: {len(readout)} descending neurons")

    # Anatomical blocks
    labels = np.array([f"{s}_{side}" for s, side in zip(d["superclass"], d["soma_side"])])
    unique_labels, block_ids = np.unique(labels, return_inverse=True)
    B = len(unique_labels)
    print(f"Partitioned into B={B} anatomical modules (superclass x soma_side)")

    # Build operators
    print("Synthesizing operators...")
    t_ops = time.time()
    operators_raw = {
        "bio_malecns": W_raw,
        "sbm_neuropil": build_sbm_matrix(W_raw, block_ids, seed=args.seed),
        "rewired_p10": partial_degree_preserving_null(W_raw, p=0.10, seed=args.seed)[0],
        "rewired_p50": partial_degree_preserving_null(W_raw, p=0.50, seed=args.seed)[0],
        "degree_null": partial_degree_preserving_null(W_raw, p=1.00, seed=args.seed)[0],
    }

    print("Row-normalising operators...")
    operators = {k: row_normalise(v) for k, v in operators_raw.items()}
    print(f"Operators ready in {time.time()-t_ops:.2f}s")

    # Generate AR(1) continuous multi-channel sensory streams
    rng_drive = np.random.default_rng(args.seed + 999)
    total_steps = args.t_train + args.t_test
    u_all = np.zeros((total_steps, args.dim_in), dtype=np.float32)
    for t in range(1, total_steps):
        u_all[t] = 0.85 * u_all[t - 1] + 0.15 * rng_drive.normal(0.0, 1.0, size=args.dim_in)

    u_train = u_all[: args.t_train]
    u_test = u_all[args.t_train :]

    print(f"\n[PHASE 1] Simulating biological train trajectory (T={args.t_train})...")
    bio_train_dict = simulate_trajectories(
        {"bio_malecns": operators["bio_malecns"]},
        inputs,
        readout,
        u_train,
        gain=args.gain,
        leak=args.leak,
        seed=args.seed,
    )
    h_bio_train = bio_train_dict["bio_malecns"]

    print(f"[PHASE 2] Fitting frozen state codebook (K={args.k_states}) strictly on biological train...")
    centroids, _ = kmeans2(h_bio_train, args.k_states, minit="points", seed=args.seed)
    print(f"Codebook frozen. Centroid shape: {centroids.shape}")

    print(f"\n[PHASE 3] Simulating held-out test trajectories (T={args.t_test}) across all models...")
    t_sim = time.time()
    test_trajectories = simulate_trajectories(
        operators, inputs, readout, u_test, gain=args.gain, leak=args.leak, seed=args.seed + 1
    )
    print(f"Held-out simulations complete in {time.time()-t_sim:.2f}s")

    print("\n[PHASE 4] Projecting into frozen codebook and estimating Markov transition operators...")
    h_bio_test = test_trajectories["bio_malecns"]
    results = {
        "metadata": {
            "k_states": args.k_states,
            "t_train": args.t_train,
            "t_test": args.t_test,
            "gain": args.gain,
            "leak": args.leak,
            "seed": args.seed,
            "num_blocks": B,
        },
        "models": {},
    }

    # Reference biological transition and stationary distribution
    s_bio, _ = vq(h_bio_test, centroids)
    counts_bio = np.zeros((args.k_states, args.k_states), dtype=np.float64)
    for t in range(len(s_bio) - 1):
        counts_bio[s_bio[t], s_bio[t + 1]] += 1.0
    T_bio = (counts_bio + 1e-6) / (counts_bio + 1e-6).sum(axis=1, keepdims=True)
    pi_bio = np.bincount(s_bio, minlength=args.k_states).astype(np.float64)
    pi_bio /= pi_bio.sum()

    for name, traj in test_trajectories.items():
        s_model, _ = vq(traj, centroids)
        counts = np.zeros((args.k_states, args.k_states), dtype=np.float64)
        for t in range(len(s_model) - 1):
            counts[s_model[t], s_model[t + 1]] += 1.0
        T_model = (counts + 1e-6) / (counts + 1e-6).sum(axis=1, keepdims=True)

        pi_model = np.bincount(s_model, minlength=args.k_states).astype(np.float64)
        pi_model /= pi_model.sum()

        frob_div = float(np.linalg.norm(T_bio - T_model, "fro") ** 2)
        js_div = float(jensenshannon(pi_bio, pi_model))
        total_markov = frob_div + js_div
        cka = linear_cka(h_bio_test, traj)

        active_states = int((pi_model > 0.01).sum())
        entropy_pi = float(-np.sum([p * np.log2(p) for p in pi_model if p > 0]))
        entropy_rate = float(
            -np.sum([pi_model[i] * np.sum([T_model[i, j] * np.log2(T_model[i, j]) for j in range(args.k_states)]) for i in range(args.k_states)])
        )

        results["models"][name] = {
            "frob_div": frob_div,
            "js_div": js_div,
            "total_markov_div": total_markov,
            "cka_alignment": cka,
            "active_states": active_states,
            "entropy_pi": entropy_pi,
            "entropy_rate": entropy_rate,
            "trajectory_l2_norm": float(np.linalg.norm(traj)),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nWrote results to {args.output}")

    print("\n" + "=" * 80)
    print(f"{'Model':<15} | {'Markov Div':<11} | {'Frob ||T-T*||2':<15} | {'JS(pi||pi*)':<12} | {'CKA':<6} | {'Active K':<8} | {'H(pi)':<6}")
    print("-" * 80)
    for name, m in results["models"].items():
        print(
            f"{name:<15} | {m['total_markov_div']:<11.4f} | {m['frob_div']:<15.4f} | {m['js_div']:<12.4f} | {m['cka_alignment']:<6.4f} | {m['active_states']:<8} | {m['entropy_pi']:<6.2f}"
        )
    print("=" * 80)


if __name__ == "__main__":
    main()
