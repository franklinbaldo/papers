from __future__ import annotations

import hashlib
import json

import numpy as np

from semantic_atlas.scale_embeddings import (
    l2_normalize,
    load_matrix,
    shard_bounds,
    write_shard,
)


def test_shard_bounds_partition_without_overlap():
    bounds = [shard_bounds(10, index, 3) for index in range(3)]
    assert bounds == [(0, 3), (3, 6), (6, 10)]


def test_l2_normalize_has_unit_rows():
    matrix = np.asarray([[3.0, 4.0], [1.0, -1.0]], dtype=np.float32)
    normalized = l2_normalize(matrix)
    assert np.allclose(np.linalg.norm(normalized, axis=1), 1.0)


def test_shards_round_trip_in_global_order(tmp_path):
    spec = {"model": "test", "revision": "abc", "dimension": 2}
    rows = [
        {
            "arxiv_id": str(index),
            "abstract": f"abstract {index}",
            "abstract_sha256": hashlib.sha256(f"abstract {index}".encode()).hexdigest(),
            "minilm_wordpieces_including_special": 4,
        }
        for index in range(4)
    ]
    first = np.asarray([[1.0, 0.0], [0.0, 2.0]], dtype=np.float32)
    second = np.asarray([[3.0, 0.0], [0.0, 4.0]], dtype=np.float32)
    write_shard(
        output_dir=tmp_path,
        observer_key="qwen",
        spec=spec,
        rows=rows[:2],
        global_start=0,
        global_end=2,
        shard_index=0,
        shard_count=2,
        raw=first,
        token_lengths=[4, 4],
    )
    write_shard(
        output_dir=tmp_path,
        observer_key="qwen",
        spec=spec,
        rows=rows[2:],
        global_start=2,
        global_end=4,
        shard_index=1,
        shard_count=2,
        raw=second,
        token_lengths=[4, 4],
    )
    assert np.array_equal(load_matrix(tmp_path, "qwen", "raw"), np.vstack([first, second]))
    assert all(json.loads(path.read_text())["rows"] == 2 for path in tmp_path.glob("*.json"))
