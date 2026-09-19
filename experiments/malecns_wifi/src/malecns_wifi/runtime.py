from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp


def load_graph(path: Path) -> sp.csr_matrix:
    archive = np.load(path, allow_pickle=False)
    shape = tuple(int(x) for x in archive["shape"])
    return sp.csr_matrix((archive["data"], archive["indices"], archive["indptr"]), shape=shape)


def smoke_reservoir(graph_path: Path, output_path: Path, *, seed: int = 0, steps: int = 12) -> dict:
    matrix = load_graph(graph_path)
    n = matrix.shape[0]
    rng = np.random.default_rng(seed)
    state = np.zeros(n, dtype=np.float32)
    input_neurons = rng.choice(n, size=min(256, n), replace=False)
    max_abs_row_sum = float(np.asarray(np.abs(matrix).sum(axis=1)).max())
    scale = max(max_abs_row_sum, 1.0)
    trace = []

    for step in range(steps):
        external = np.zeros(n, dtype=np.float32)
        if step < 3:
            external[input_neurons] = rng.normal(0.0, 0.5, size=input_neurons.size).astype(np.float32)
        recurrent = matrix @ state
        state = (0.8 * state + 0.2 * np.tanh(recurrent / scale + external)).astype(np.float32)
        trace.append({
            "step": step,
            "l2": float(np.linalg.norm(state)),
            "active_gt_1e-6": int(np.count_nonzero(np.abs(state) > 1e-6)),
            "finite": bool(np.isfinite(state).all()),
        })

    result = {
        "seed": seed,
        "steps": steps,
        "neurons": n,
        "edges": int(matrix.nnz),
        "normalization": {"max_abs_row_sum": scale},
        "trace": trace,
        "final_finite": bool(np.isfinite(state).all()),
        "activity_spread": int(max(item["active_gt_1e-6"] for item in trace)),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result
