import json
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

torch = pytest.importorskip("torch")

from malecns_wifi import token_reservoir as tr
from malecns_wifi import token_probe as tp
from malecns_wifi import fewnerd_cache as fc

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _graph(n=250, density=0.03, seed=7):
    rng = np.random.default_rng(seed)
    matrix = sp.random(n, n, density=density, format="csr", random_state=rng, dtype=np.float32)
    matrix.data = (matrix.data - 0.5).astype(np.float32) * 4
    inputs = np.sort(rng.choice(n, size=32, replace=False))
    return matrix, inputs


def test_word_pool_hidden_states_means_over_subwords():
    hidden = np.array([[1.0, 0.0], [3.0, 0.0], [0.0, 2.0], [10.0, 10.0]], dtype=np.float32)
    word_ids = [0, 0, 1, None]  # word 0 spans two subwords, word 1 one, special token dropped
    pooled = tr.word_pool_hidden_states(hidden, word_ids, num_words=2)
    assert np.allclose(pooled[0], [2.0, 0.0])
    assert np.allclose(pooled[1], [0.0, 2.0])


def test_word_pool_handles_word_with_no_subwords():
    hidden = np.array([[1.0, 1.0]], dtype=np.float32)
    pooled = tr.word_pool_hidden_states(hidden, [0], num_words=2)
    assert np.allclose(pooled[0], [1.0, 1.0])
    assert np.allclose(pooled[1], [0.0, 0.0])  # never fabricated, exact zero


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
    # step 0's readout never touches the recurrent operator (state is exactly zero before it);
    # every later step makes exactly one SpMM call.
    assert reservoir.stats.spmm_calls == steps - 1


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
    # a padded position repeats the last real embedding for that sentence (state frozen, readout deterministic in state)
    assert np.allclose(out[1, 2], out[1, 3])
    assert np.allclose(out[1, 3], out[1, 4])


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


class _FakeTokenizerOutput(dict):
    def to(self, device):
        return self

    def word_ids(self, batch_index):
        return self["_word_ids"][batch_index]


class _FakeTokenizer:
    def __call__(self, batch, **kwargs):
        max_len = max(len(s) for s in batch) + 1  # +1 for a leading [CLS]-like special token
        word_ids = [[None] + list(range(len(s))) + [None] * (max_len - len(s) - 1) for s in batch]
        input_ids = torch.zeros((len(batch), max_len), dtype=torch.long)
        return _FakeTokenizerOutput(input_ids=input_ids, _word_ids=word_ids)


class _FakeConfig:
    hidden_size = 6
    _commit_hash = "deadbeef"


class _FakeModel:
    def __init__(self):
        self.config = _FakeConfig()

    def to(self, device):
        return self

    def eval(self):
        return self

    def __call__(self, **kwargs):
        input_ids = kwargs["input_ids"]
        batch, seq = input_ids.shape
        rng = np.random.default_rng(0)
        hidden = torch.as_tensor(rng.normal(size=(batch, seq, 6)).astype(np.float32))

        class Output:
            last_hidden_state = hidden

        return Output()


def test_encode_model_word_pools_and_normalises(monkeypatch):
    import transformers

    monkeypatch.setattr(transformers, "AutoTokenizer", type("T", (), {"from_pretrained": staticmethod(lambda name: _FakeTokenizer())}))
    monkeypatch.setattr(transformers, "AutoModel", type("M", (), {"from_pretrained": staticmethod(lambda name: _FakeModel())}))

    sentences = [["hello", "world"], ["a", "b", "c"]]
    embeddings, info = fc.encode_model("fake/model", sentences, device="cpu", batch_size=2, max_tokens=16)
    assert embeddings.shape == (5, 6)
    assert np.allclose(np.linalg.norm(embeddings, axis=1), 1.0, atol=1e-5)
    assert info["dim"] == 6 and info["revision"] == "deadbeef"


def test_fewnerd_cache_manifest_fields(tmp_path):
    documents = {
        "train": [{"id": "0", "tokens": ["Ann", "met", "Bob"], "fine": [51, 0, 51], "coarse": [7, 0, 7]}],
        "validation": [{"id": "1", "tokens": ["Paris"], "fine": [21], "coarse": [4]}],
        "test": [{"id": "2", "tokens": ["ok"], "fine": [0], "coarse": [0]}],
    }
    fine_names = ["O"] * 67
    fine_names[51] = "person-other"
    fine_names[21] = "location-GPE"
    loaded = {"documents": documents, "fine_names": fine_names, "coarse_names": ["O"] * 9}
    spec = fc.TokenCacheSpec(models=("fake/minilm",), limit_per_split=None, max_tokens=16)
    table = fc.TokenTable.from_documents(spec, documents)
    assert len(table) == 3 + 1 + 1
    assert table.sentence_tokens == [["Ann", "met", "Bob"], ["Paris"], ["ok"]]
    assert fc.sentence_key(["Ann", "met", "Bob"]) == fc.sentence_key(["Ann", "met", "Bob"])
    assert fc.sentence_key(["Ann", "met", "Bob"]) != fc.sentence_key(["Paris"])
