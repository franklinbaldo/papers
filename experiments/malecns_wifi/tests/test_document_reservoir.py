import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

torch = pytest.importorskip("torch")

from malecns_wifi import document_reservoir as dr
from malecns_wifi import multieurlex_cache as mc

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _graph(n=300, density=0.03, seed=3):
    rng = np.random.default_rng(seed)
    matrix = sp.random(n, n, density=density, format="csr", random_state=rng, dtype=np.float32)
    matrix.data = (matrix.data - 0.5).astype(np.float32) * 4
    inputs = np.sort(rng.choice(n, size=40, replace=False))
    return matrix, inputs


def _cache(n_docs=23, dim=24, seed=5):
    rng = np.random.default_rng(seed)
    counts = rng.integers(1, 5, size=n_docs)
    offsets = np.concatenate([[0], np.cumsum(counts)]).astype(np.int64)
    fused = dr.unit_rows(rng.normal(size=(int(offsets[-1]), dim)).astype(np.float32))
    return fused, offsets


def _original_reservoir_batch(reservoir, cube, active):
    """Verbatim arithmetic of FrozenMaleCNSEncoder._reservoir_batch at 27db9c7."""
    cfg = reservoir.config
    batch, steps, _ = cube.shape
    features = torch.as_tensor(cube, dtype=torch.float32)
    active_t = torch.as_tensor(active, dtype=torch.bool)
    state = torch.zeros((reservoir.neurons, batch), dtype=torch.float32)
    for step in range(steps):
        local = features[:, step, :]
        projected = reservoir.input_weights @ local.T
        rms = torch.sqrt(torch.mean(projected.square(), dim=0, keepdim=True)).clamp_min(1e-12)
        projected = projected * (cfg.target_rms / rms)
        drive = torch.zeros_like(state)
        drive.index_copy_(0, reservoir.input_indices, projected)
        pre = torch.sparse.mm(reservoir.operator, state) * cfg.gain + drive
        updated = (1.0 - cfg.leak) * state + cfg.leak * torch.tanh(pre)
        mask = active_t[:, step][None, :]
        state = torch.where(mask, updated, state)
    readout = torch.sparse.mm(reservoir.readout_projection, state).T
    readout = readout / torch.linalg.vector_norm(readout, dim=1, keepdim=True).clamp_min(1e-12)
    return readout.detach().cpu().numpy().astype(np.float32)


def test_canonical_backend_is_bit_exact_with_original_encoder_math():
    matrix, inputs = _graph()
    fused, offsets = _cache()
    config = dr.DocumentReservoirConfig(readout_width=16)
    reservoir = dr.DocumentReservoir(matrix, inputs, semantic_dim=fused.shape[1], config=config, device="cpu")
    docs = np.arange(0, 16)
    cube, active = dr.pack_cube(fused, offsets, docs)
    expected = _original_reservoir_batch(reservoir, cube, active)
    got = reservoir.forward(cube, active)
    assert np.array_equal(expected, got)


def test_fast_backend_matches_canonical_within_gate():
    matrix, inputs = _graph()
    fused, offsets = _cache()
    config = dr.DocumentReservoirConfig(readout_width=16)
    canonical = dr.DocumentReservoir(matrix, inputs, semantic_dim=fused.shape[1], config=config, device="cpu", backend="canonical")
    fast = dr.DocumentReservoir(matrix, inputs, semantic_dim=fused.shape[1], config=config, device="cpu", backend="fast")
    reference = canonical.encode_cached(fused, offsets, batch_size=8, group_by_length=False)
    for batch_size in (1, 4, 64):
        fast.stats = dr.ReservoirStats()
        candidate = fast.encode_cached(fused, offsets, batch_size=batch_size)
        report = dr.equivalence_report(reference, candidate)
        assert dr.passes_gate(report), report
        # grouped batching never wastes a masked column-step; ragged batching does
        assert fast.stats.masked_column_steps == 0
        # first-step SpMM skipped and no padded columns: fewer column-SpMV equivalents
        assert fast.stats.spmm_columns == fused.shape[0] - (len(offsets) - 1)
        assert fast.stats.spmm_columns < canonical.stats.spmm_columns
    assert canonical.stats.masked_column_steps > 0


def test_int32_indices_match_int64():
    matrix, inputs = _graph()
    fused, offsets = _cache()
    config = dr.DocumentReservoirConfig(readout_width=16)
    a = dr.DocumentReservoir(matrix, inputs, semantic_dim=fused.shape[1], config=config, device="cpu", backend="fast", index_dtype="int64")
    b = dr.DocumentReservoir(matrix, inputs, semantic_dim=fused.shape[1], config=config, device="cpu", backend="fast", index_dtype="int32")
    report = dr.equivalence_report(
        a.encode_cached(fused, offsets, batch_size=8), b.encode_cached(fused, offsets, batch_size=8)
    )
    assert dr.passes_gate(report), report


def test_sample_windows_policy():
    assert dr.sample_windows("", max_chunks=4, chunk_chars=10) == [" "]
    assert dr.sample_windows("short", max_chunks=4, chunk_chars=10) == ["short"]
    text = "".join(chr(97 + (i % 26)) for i in range(100))
    windows = dr.sample_windows(text, max_chunks=4, chunk_chars=30)
    assert len(windows) == 4
    assert windows[0] == text[:30] and windows[-1] == text[70:100]
    assert len(dr.sample_windows(text, max_chunks=4, chunk_chars=60)) == 2


def test_controls_are_label_free_and_shaped():
    matrix, inputs = _graph()
    fused, offsets = _cache()
    config = dr.DocumentReservoirConfig(readout_width=16)
    reservoir = dr.DocumentReservoir(matrix, inputs, semantic_dim=fused.shape[1], config=config, device="cpu", backend="fast")
    n = len(offsets) - 1
    mean = dr.control_embeddings("fused-mean", fused, offsets, config=config)
    proj = dr.control_embeddings("fused-mean-proj", fused, offsets, config=config)
    sensory = dr.control_embeddings("sensory-only", fused, offsets, config=config, reservoir=reservoir)
    assert mean.shape == (n, fused.shape[1]) and proj.shape == (n, 16) and sensory.shape == (n, 16)
    for value in (mean, proj, sensory):
        assert np.allclose(np.linalg.norm(value, axis=1), 1.0, atol=1e-5)
    # sensory-only is exactly the pipeline at gain 0 (recurrence removed)
    again = reservoir.encode_cached(fused, offsets, batch_size=8, gain=0.0)
    assert np.array_equal(sensory, again)
    with pytest.raises(ValueError):
        dr.control_embeddings("nope", fused, offsets, config=config)


def test_fixed_projection_arrays_are_seeded():
    a = dr.fixed_sparse_projection_arrays(4, 100, seed=1)
    b = dr.fixed_sparse_projection_arrays(4, 100, seed=1)
    c = dr.fixed_sparse_projection_arrays(4, 100, seed=2)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    assert not np.array_equal(a[1], c[1])
    per_row = int(round(math.sqrt(100)))
    assert len(a[0]) == 4 * per_row


class _FakeSentenceTransformer:
    """Deterministic stand-in: embeds text by hashed character histogram."""

    dim = 8
    max_seq_length = 128

    def __init__(self, name, device=None):
        self.name = name
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append(list(texts))
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for ch in text:
                out[i, ord(ch) % self.dim] += 1.0
        return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-12)

    def __getitem__(self, item):
        raise IndexError

    def get_sentence_embedding_dimension(self):
        return self.dim


def test_semantic_cache_parquet_join_and_cached_encoder(tmp_path, monkeypatch):
    import sentence_transformers

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", _FakeSentenceTransformer)
    docs = {
        "train": [{"id": "A", "text": "alpha " * 50}, {"id": "B", "text": "beta"}],
        "test": [{"id": "C", "text": "gamma " * 400}, {"id": "D", "text": ""}],
    }
    out = tmp_path / "cache"
    # encoders built independently (as on different machines), merged by manifest
    spec_a = mc.CacheSpec(models=("fake/minilm",), max_chunks=4, chunk_chars=100, splits=("train", "test"), limit_per_split=2)
    spec_b = mc.CacheSpec(models=("fake/e5-small",), max_chunks=4, chunk_chars=100, splits=("train", "test"), limit_per_split=2)
    mc.build_cache(spec_a, output_dir=out, device="cpu", batch_size=4, documents=docs)
    manifest = mc.build_cache(spec_b, output_dir=out, device="cpu", batch_size=4, documents=docs)
    assert manifest["documents"] == 4 and manifest["chunks"] == 3 + 1 + 4 + 1
    assert {e["name"] for e in manifest["encoders"]} == {"fake/minilm", "fake/e5-small"}
    assert next(e for e in manifest["encoders"] if "e5" in e["name"])["prefix"] == "passage: "
    assert manifest["dataset"]["partial"] is True
    assert sorted(p.name for p in out.glob("*.parquet")) == ["e5-small.parquet", "minilm.parquet"]

    # unknown encoders fall back to alphabetical order; the real defaults keep MiniLM then E5
    assert manifest["encoder_order"] == ["fake/e5-small", "fake/minilm"]
    assert mc.canonical_model_order(reversed(mc.DEFAULT_MODELS)) == list(mc.DEFAULT_MODELS)
    assert mc.load_cache(out).models == ["fake/e5-small", "fake/minilm"]
    spec = mc.CacheSpec(models=("fake/minilm", "fake/e5-small"), max_chunks=4, chunk_chars=100, splits=("train", "test"), limit_per_split=2)
    loaded = mc.load_cache(out, spec=spec)
    assert loaded.fused.shape == (9, 16)
    assert loaded.doc_id.tolist() == ["A", "B", "C", "D"]
    assert loaded.doc_split.tolist() == ["train", "train", "test", "test"]
    assert loaded.offsets.tolist() == [0, 3, 4, 8, 9]
    assert loaded.doc_key[0] == mc.text_key(docs["train"][0]["text"])
    # column order follows the requested model order, not file order
    swapped = mc.load_cache(out, models=("fake/e5-small", "fake/minilm"))
    assert np.array_equal(swapped.fused[:, :8], loaded.fused[:, 8:])
    # a split subset keeps only those documents
    only_test = mc.load_cache(out, splits=("test",))
    assert only_test.doc_id.tolist() == ["C", "D"]
    with pytest.raises(RuntimeError):
        mc.load_cache(out, spec=mc.CacheSpec(models=spec.models, max_chunks=3, chunk_chars=100, splits=("train", "test"), limit_per_split=2))
    assert "text_sha256" in mc.dataset_card(manifest)

    # stage B -> stage C lookup
    from malecns_mteb_encoder import CachedDocumentEncoder

    embeddings = dr.control_embeddings("fused-mean", loaded.fused, loaded.offsets, config=dr.DocumentReservoirConfig())
    stage_b = tmp_path / "docs.npz"
    np.savez(stage_b, doc_key=loaded.doc_key, embeddings=embeddings)
    stage_b.with_suffix(".manifest.json").write_text(json.dumps({"variant": "fused-mean"}), encoding="utf-8")
    encoder = CachedDocumentEncoder(stage_b)
    batches = [{"text": [docs["test"][0]["text"], docs["train"][1]["text"]]}]
    out_rows = encoder.encode(batches, task_metadata=None, hf_split="test", hf_subset="pt")
    assert np.array_equal(out_rows[0], embeddings[2]) and np.array_equal(out_rows[1], embeddings[1])
    with pytest.raises(KeyError):
        encoder.encode([{"text": ["unseen document"]}], task_metadata=None, hf_split="test", hf_subset="pt")
