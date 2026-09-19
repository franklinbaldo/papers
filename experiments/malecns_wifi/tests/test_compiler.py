from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather

from malecns_wifi.compiler import CompilePolicy, SourceSpec, compile_connectome
from malecns_wifi.runtime import load_graph, smoke_reservoir


def test_compile_and_smoke_tiny_connectome(tmp_path: Path) -> None:
    raw = tmp_path / "raw-source"
    raw.mkdir()
    annotations = pa.table({
        "bodyId": [10, 20, 30, 40],
        "status": ["Traced", "Traced", "Traced", "Traced"],
        "statusLabel": ["Neuron", "Neuron", "Neuron", "Glia"],
    })
    neurotransmitters = pa.table({
        "body": [10, 20, 30, 40],
        "consensus_nt": ["acetylcholine", "gaba", "acetylcholine", "acetylcholine"],
    })
    weights = pa.table({
        "body_pre": [10, 20, 30, 40, 10],
        "body_post": [20, 30, 10, 10, 30],
        "weight": [5, 4, 3, 9, 1],
    })
    feather.write_feather(annotations, raw / "body-annotations-male-cns-v1.0-minconf-0.5.feather")
    feather.write_feather(neurotransmitters, raw / "body-neurotransmitters-male-cns-v1.0.feather")
    feather.write_feather(weights, raw / "connectome-weights-male-cns-v1.0-minconf-0.5.feather")

    source = SourceSpec(
        weights_url=(raw / "connectome-weights-male-cns-v1.0-minconf-0.5.feather").as_uri(),
        annotations_url=(raw / "body-annotations-male-cns-v1.0-minconf-0.5.feather").as_uri(),
        neurotransmitters_url=(raw / "body-neurotransmitters-male-cns-v1.0.feather").as_uri(),
    )
    out = tmp_path / "out"
    manifest = compile_connectome(
        output_dir=out,
        cache_dir=tmp_path / "cache",
        source=source,
        policy=CompilePolicy(min_synapses=3),
    )
    graph = load_graph(out / "graph.npz")
    assert manifest["runtime"]["neurons"] == 3
    assert graph.shape == (3, 3)
    assert graph.nnz == 3
    assert graph[1, 0] == 5
    assert graph[2, 1] == -4
    assert graph[0, 2] == 3

    result = smoke_reservoir(out / "graph.npz", out / "smoke.json", seed=1, steps=4)
    assert result["final_finite"]
    assert np.isfinite(result["trace"][-1]["l2"])
