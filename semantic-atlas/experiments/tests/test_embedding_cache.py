from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from semantic_atlas.embedding_cache import load_embedding_cache, write_embedding_cache


def _fixture():
    paths = {
        "calibration": ["a.md", "b.md"],
        "heldout": ["c.md"],
    }
    texts = {
        "calibration": ["alpha", "beta"],
        "heldout": ["gamma"],
    }
    raw = {
        "calibration": np.array([[3.0, 4.0], [0.0, 2.0]], dtype=np.float64),
        "heldout": np.array([[5.0, 12.0]], dtype=np.float64),
    }
    normalized = {
        split: values / np.linalg.norm(values, axis=1, keepdims=True)
        for split, values in raw.items()
    }
    return paths, texts, raw, normalized


def test_cache_is_content_addressed_and_round_trips(tmp_path: Path) -> None:
    paths, texts, raw, normalized = _fixture()
    kwargs = dict(
        directory=tmp_path,
        observer={"model": "observer/example", "revision": "abc123"},
        source_commit="deadbeef",
        paths_by_split=paths,
        texts_by_split=texts,
        raw_by_split=raw,
        normalized_by_split=normalized,
    )

    first = write_embedding_cache(**kwargs)
    second = write_embedding_cache(**kwargs)

    assert first.data_sha256 == second.data_sha256
    assert first.data_path.name == f"embeddings-{first.data_sha256}.npz"
    assert first.manifest_path.name == f"embeddings-{first.data_sha256}.json"

    manifest, arrays = load_embedding_cache(first.manifest_path)
    assert manifest["source_commit"] == "deadbeef"
    assert manifest["corpus_sha256"] == first.corpus_sha256
    assert np.array_equal(arrays["raw_calibration"], raw["calibration"])
    assert np.array_equal(arrays["normalized_heldout"], normalized["heldout"])


def test_cache_records_text_hashes_not_text_or_credentials(tmp_path: Path) -> None:
    paths, texts, raw, normalized = _fixture()
    ref = write_embedding_cache(
        tmp_path,
        observer={"provider": "example", "model": "embed-v1"},
        source_commit="deadbeef",
        paths_by_split=paths,
        texts_by_split=texts,
        raw_by_split=raw,
        normalized_by_split=normalized,
    )
    manifest_text = ref.manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)

    assert "alpha" not in manifest_text
    assert "beta" not in manifest_text
    assert "gamma" not in manifest_text
    assert all(len(item["text_sha256"]) == 64 for items in manifest["corpus"].values() for item in items)

    with pytest.raises(ValueError, match="secret-bearing key"):
        write_embedding_cache(
            tmp_path / "bad",
            observer={"model": "embed-v1", "api_key": "do-not-store"},
            source_commit="deadbeef",
            paths_by_split=paths,
            texts_by_split=texts,
            raw_by_split=raw,
            normalized_by_split=normalized,
        )


def test_cache_rejects_cross_split_overlap(tmp_path: Path) -> None:
    paths, texts, raw, normalized = _fixture()
    paths["heldout"] = ["a.md"]

    with pytest.raises(ValueError, match="disjoint"):
        write_embedding_cache(
            tmp_path,
            observer={"model": "observer/example", "revision": "abc123"},
            source_commit="deadbeef",
            paths_by_split=paths,
            texts_by_split=texts,
            raw_by_split=raw,
            normalized_by_split=normalized,
        )


def test_cache_detects_numeric_tampering(tmp_path: Path) -> None:
    paths, texts, raw, normalized = _fixture()
    ref = write_embedding_cache(
        tmp_path,
        observer={"model": "observer/example", "revision": "abc123"},
        source_commit="deadbeef",
        paths_by_split=paths,
        texts_by_split=texts,
        raw_by_split=raw,
        normalized_by_split=normalized,
    )
    data = bytearray(ref.data_path.read_bytes())
    data[-1] ^= 1
    ref.data_path.write_bytes(bytes(data))

    with pytest.raises(ValueError, match="hash mismatch"):
        load_embedding_cache(ref.manifest_path)
