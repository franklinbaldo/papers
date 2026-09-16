import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

torch = pytest.importorskip("torch")

from malecns_wifi import token_reservoir as tr
from malecns_wifi import token_probe as tp
from malecns_wifi import fewnerd_cache as fc
from malecns_wifi import text_axis_channels as tac

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _graph(n=250, density=0.03, seed=7):
    rng = np.random.default_rng(seed)
    matrix = sp.random(n, n, density=density, format="csr", random_state=rng, dtype=np.float32)
    matrix.data = (matrix.data - 0.5).astype(np.float32) * 4
    inputs = np.sort(rng.choice(n, size=32, replace=False))
    return matrix, inputs


# -- byte-axis primitives (the established channel convention) --------------

def test_window_spans_covers_short_and_long_text():
    assert tr is not None  # module import sanity (reservoir depends on nothing byte-specific)
    assert tac.window_spans("hi", 8) == [(0, 2)]
    spans = tac.window_spans("a" * 20, 8)
    assert spans[0] == (0, 8) and spans[-1] == (12, 20)
    assert all(b - a == 8 for a, b in spans)


def test_char_spans_to_byte_spans_matches_utf8_lengths():
    text = "café"  # 'é' is 2 UTF-8 bytes
    spans = tac.char_spans_to_byte_spans(text, [(0, 4)])
    assert spans[0][1] == len(text.encode("utf-8"))


# -- byte-label reconstruction ------------------------------------------------

def test_reconstruct_text_and_byte_labels_broadcast_word_spans():
    words = ["Ann", "met", "Bob"]
    fine = [51, 0, 51]
    coarse = [7, 0, 7]
    text, byte_fine, byte_coarse = fc.byte_labels(words, fine, coarse)
    assert text == "Ann met Bob"
    # "Ann" occupies bytes 0-3, the space is O (0), "Bob" occupies bytes 8-11
    assert list(byte_fine[0:3]) == [51, 51, 51]
    assert byte_fine[3] == 0  # space between words
    assert list(byte_fine[8:11]) == [51, 51, 51]
    assert byte_coarse[0] == 7 and byte_coarse[3] == 0


def test_byte_labels_handles_multibyte_words():
    words = ["café", "ok"]
    text, byte_fine, _ = fc.byte_labels(words, [21, 0], [4, 0])
    assert text == "café ok"
    café_bytes = len("café".encode("utf-8"))
    assert list(byte_fine[:café_bytes]) == [21] * café_bytes
    assert byte_fine[café_bytes] == 0  # the space


# -- positional reservoir (unit-agnostic: works over whatever axis it's fed) --

def test_positional_reservoir_emits_one_readout_per_step():
    matrix, inputs = _graph()
    rng = np.random.default_rng(3)
    dim = 20
    config = tr.TokenReservoirConfig(readout_width=12)
    reservoir = tr.PositionalReservoir(matrix, inputs, semantic_dim=dim, config=config, device="cpu")

    batch, steps = 5, 6
    cube = rng.normal(size=(batch, steps, dim)).astype(np.float32)
    active = np.ones((batch, steps), dtype=np.bool_)
    active[0, 4:] = False  # shorter sentence padded

    out = reservoir.forward(cube, active)
    assert out.shape == (batch, steps, 12)
    norms = np.linalg.norm(out, axis=2)
    assert np.allclose(norms[active], 1.0, atol=1e-5)
    # step 0's readout never touches the recurrent operator (state is exactly zero
    # before it); every later step makes exactly one SpMM call.
    assert reservoir.stats.spmm_calls == steps - 1


def test_positional_reservoir_descending_neuron_readout_matches_state_verbatim():
    matrix, inputs = _graph()
    rng = np.random.default_rng(5)
    dim = 10
    readout_indices = np.array([3, 17, 42, 100])
    config = tr.TokenReservoirConfig(readout_mode="descending_neuron")
    reservoir = tr.PositionalReservoir(matrix, inputs, semantic_dim=dim, config=config, device="cpu",
                                       readout_indices=readout_indices)
    assert reservoir.readout_width == 4 and reservoir.readout_projection is None

    cube = rng.normal(size=(3, 4, dim)).astype(np.float32)
    active = np.ones((3, 4), dtype=np.bool_)
    out = reservoir.forward(cube, active)
    assert out.shape == (3, 4, 4)
    assert np.allclose(np.linalg.norm(out, axis=2), 1.0, atol=1e-5)


def test_config_readout_width_is_not_the_actual_width_in_descending_mode():
    """Regression: encode_fewnerd_tokens.py once allocated its output array with
    ``config.readout_width`` (the default 256) even in descending-neuron mode,
    where the real width is set by ``readout_indices`` -- crashed on the very
    first non-empty batch with a shape mismatch. Any code consuming a
    reservoir's output width MUST read ``reservoir.readout_width``, never
    ``config.readout_width``, once ``readout_mode="descending_neuron"``.
    """
    matrix, inputs = _graph()
    readout_indices = np.array([1, 2, 3, 4])
    config = tr.TokenReservoirConfig(readout_width=256, readout_mode="descending_neuron")
    reservoir = tr.PositionalReservoir(matrix, inputs, semantic_dim=8, config=config, device="cpu",
                                       readout_indices=readout_indices)
    assert reservoir.readout_width != config.readout_width
    assert reservoir.readout_width == len(readout_indices)
    out = reservoir.forward(np.zeros((1, 1, 8), dtype=np.float32), np.ones((1, 1), dtype=np.bool_))
    assert out.shape[-1] == reservoir.readout_width  # not config.readout_width


def test_positional_reservoir_descending_neuron_needs_indices():
    matrix, inputs = _graph()
    config = tr.TokenReservoirConfig(readout_mode="descending_neuron")
    with pytest.raises(ValueError):
        tr.PositionalReservoir(matrix, inputs, semantic_dim=10, config=config, device="cpu")


def test_positional_reservoir_padding_freezes_state():
    matrix, inputs = _graph()
    rng = np.random.default_rng(11)
    dim = 16
    config = tr.TokenReservoirConfig(readout_width=8)
    reservoir = tr.PositionalReservoir(matrix, inputs, semantic_dim=dim, config=config, device="cpu")
    cube = rng.normal(size=(2, 5, dim)).astype(np.float32)
    active = np.ones((2, 5), dtype=np.bool_)
    active[1, 2:] = False
    out = reservoir.forward(cube, active)
    assert np.allclose(out[1, 2], out[1, 3])
    assert np.allclose(out[1, 3], out[1, 4])


# -- span metrics -------------------------------------------------------------

def test_fit_probe_recovers_minority_class_on_imbalanced_labels():
    """Regression test: plain-accuracy selection collapses to majority-only.

    With an 80/20-ish class split and enough separable signal, a probe
    selected by validation accuracy alone can legitimately settle on
    predicting only the majority class (highest accuracy, zero minority
    recall) -- this is exactly the failure observed empirically on Few-NERD
    (span F1 stayed at 0.0 even with 4,000 training sentences). Selecting by
    macro-F1 with class_weight='balanced' must recover the minority class
    here, where it is linearly separable and plentiful enough to learn.
    """
    rng = np.random.default_rng(0)
    n_majority, n_minority = 400, 100
    majority = rng.normal(loc=0.0, scale=0.3, size=(n_majority, 2))
    minority = rng.normal(loc=4.0, scale=0.3, size=(n_minority, 2))
    x = np.concatenate([majority, minority])
    y = np.concatenate([np.zeros(n_majority, dtype=np.int64), np.ones(n_minority, dtype=np.int64)])
    order = rng.permutation(len(x))
    x, y = x[order], y[order]
    split = len(x) // 2
    model, c, val_acc = tp.fit_probe(x[:split], y[:split], x[split:], y[split:])
    pred = model.predict(x[split:])
    assert 1 in set(pred.tolist()), "macro-F1 selection must not collapse to majority-only prediction"


def test_bio_conversion_and_span_metrics_perfect_match():
    names = ["O", "person", "location"]
    true = [np.array([0, 1, 1, 0, 2]), np.array([2, 2, 0])]
    pred = [np.array([0, 1, 1, 0, 2]), np.array([2, 2, 0])]
    metrics = tp.span_metrics(true, pred, names)
    assert metrics["micro_f1"] == pytest.approx(1.0)
    assert metrics["macro_f1"] == pytest.approx(1.0)


def test_bio_conversion_splits_adjacent_different_entities():
    names = ["O", "person", "location"]
    tags = tp.bio_tags(np.array([1, 1, 2, 2, 0]), names)
    assert tags == ["B-person", "I-person", "B-location", "I-location", "O"]


def test_bio_conversion_false_positive_lowers_precision_not_recall():
    names = ["O", "person"]
    true = [np.array([0, 0, 0])]
    pred = [np.array([0, 1, 0])]
    metrics = tp.span_metrics(true, pred, names)
    assert metrics["micro_precision"] == 0.0
    assert metrics["micro_recall"] == 0.0  # no true entities to recall


# -- fake-encoder round trip through the byte-channel pipeline ---------------

class _FakeSentenceTransformer:
    """Deterministic stand-in: embeds text as a hashed character histogram."""

    dim = 6

    def __init__(self, name, device=None):
        self.name = name

    def encode(self, texts, **kwargs):
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for ch in text:
                out[i, ord(ch) % self.dim] += 1.0
        return out

    def get_sentence_embedding_dimension(self):
        return self.dim


def test_default_scale_ladder_is_power_of_two_sweep():
    assert fc.DEFAULT_SCALES == (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048)


def test_window_key_is_stable_and_content_addressed():
    assert fc.window_key("ab") == fc.window_key("ab")
    assert fc.window_key("ab") != fc.window_key("ba")
    assert len(fc.window_key("x")) == 16  # KEY_DIGEST_SIZE


def test_collect_unique_windows_dedups_across_sentences_and_scales():
    texts = ["aaaa", "aaab"]
    unique = fc.collect_unique_windows(texts, scales=(1, 2))
    # scale=1 windows are single characters: only 'a' and 'b' exist across both sentences
    single_char_values = {v for v in unique.values() if len(v) == 1}
    assert single_char_values == {"a", "b"}
    assert unique[fc.window_key("a")] == "a"


def test_encode_unique_windows_and_assemble_channel_round_trip(monkeypatch, tmp_path):
    import sentence_transformers

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", _FakeSentenceTransformer)
    texts = ["Ann met Bob", "ok"]
    unique = fc.collect_unique_windows(texts, scales=(4, 8))
    embeddings, sorted_keys, info = fc.encode_unique_windows("fake/minilm", unique, device="cpu", batch_size=8)
    assert info["unique_windows"] == len(sorted_keys) == len(unique)
    assert embeddings.shape == (len(unique), 6)
    model_dir = tmp_path / "fake-minilm"
    fc.write_dedup_table(model_dir, embeddings, sorted_keys)

    keys = np.load(model_dir / "keys.npy")
    mm = np.memmap(model_dir / "embeddings.f32", dtype=np.float32, mode="r", shape=(len(keys), 6))
    encoder = fc.DedupEncoder(name="fake/minilm", base_dim=6, sorted_keys=keys, embeddings=mm)

    cache = fc.FewnerdCache(manifest={"labels": {}}, directory=tmp_path, sentences=None,
                            encoders={"fake/minilm": encoder}, scales=(4, 8))
    for text in texts:
        channel = cache.assemble_channel(("fake/minilm",), text)
        n_bytes = len(text.encode("utf-8"))
        assert channel.shape == (n_bytes, 6 * 2)
        assert np.allclose(np.linalg.norm(channel[:, :6], axis=1), 1.0, atol=1e-5)
        assert np.allclose(np.linalg.norm(channel[:, 6:], axis=1), 1.0, atol=1e-5)

    with pytest.raises(KeyError):
        encoder.lookup_many(["never seen this text before"])


def test_assemble_channel_is_piecewise_constant_not_interpolated(monkeypatch, tmp_path):
    """Adjacent chunks must jump, not blend -- this is a mosaic, not interpolation."""
    import sentence_transformers

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", _FakeSentenceTransformer)
    text = "aaaabbbb"  # scale=4 tiles this into exactly two distinct chunks: "aaaa", "bbbb"
    unique = fc.collect_unique_windows([text], scales=(4,))
    embeddings, sorted_keys, _ = fc.encode_unique_windows("fake/minilm", unique, device="cpu", batch_size=8)
    model_dir = tmp_path / "fake-minilm"
    fc.write_dedup_table(model_dir, embeddings, sorted_keys)
    keys = np.load(model_dir / "keys.npy")
    mm = np.memmap(model_dir / "embeddings.f32", dtype=np.float32, mode="r", shape=(len(keys), 6))
    encoder = fc.DedupEncoder(name="fake/minilm", base_dim=6, sorted_keys=keys, embeddings=mm)
    cache = fc.FewnerdCache(manifest={"labels": {}}, directory=tmp_path, sentences=None,
                            encoders={"fake/minilm": encoder}, scales=(4,))

    channel = cache.assemble_channel(("fake/minilm",), text)
    assert channel.shape == (8, 6)
    # within each chunk, every byte is identical (constant, not interpolated)
    assert np.array_equal(channel[0], channel[1]) and np.array_equal(channel[2], channel[3])
    assert np.array_equal(channel[4], channel[5]) and np.array_equal(channel[6], channel[7])
    # the two chunks ("aaaa" vs "bbbb") must differ -- no smoothing across the boundary
    assert not np.allclose(channel[3], channel[4])


def test_fixed_chunks_tiles_without_overlap_or_gaps():
    text = "Ann met Bob"  # 11 chars
    spans = tac.fixed_chunks(text, 4)
    assert spans == [(0, 4), (4, 8), (8, 11)]
    covered = "".join(text[a:b] for a, b in spans)
    assert covered == text  # every byte covered exactly once, in order


def test_build_sentence_records_and_write_sentences(tmp_path):
    documents = {
        "train": [{"id": "0", "tokens": ["Ann", "met", "Bob"], "fine": [51, 0, 51], "coarse": [7, 0, 7]}],
        "validation": [{"id": "1", "tokens": ["café"], "fine": [21], "coarse": [4]}],
        "test": [{"id": "2", "tokens": ["ok"], "fine": [0], "coarse": [0]}],
    }
    spec = fc.TokenCacheSpec(models=("fake/minilm",), max_tokens=16)
    records = fc.build_sentence_records(spec, documents)
    assert [r.text for r in records] == ["Ann met Bob", "café", "ok"]
    assert len(records[0].byte_fine) == len("Ann met Bob".encode("utf-8"))
    assert fc.sentence_key(["Ann", "met", "Bob"]) == fc.sentence_key(["Ann", "met", "Bob"])
    assert fc.sentence_key(["Ann", "met", "Bob"]) != fc.sentence_key(["café"])

    path = fc.write_sentences(records, output_dir=tmp_path)
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    assert table.column("id").to_pylist() == ["0", "1", "2"]
    assert table.column("fine_label").to_pylist()[0][:3] == [51, 51, 51]  # "Ann" broadcast onto its bytes
