import numpy as np
import pytest

from malecns_wifi.semantic_memory import (
    SemanticMemory,
    admissible_memory_mask,
    complete_channel,
    completion_ledger,
    retrieve,
)


def _memory() -> SemanticMemory:
    keys = np.asarray(
        [
            [1.0, 0.0],
            [0.9, 0.1],
            [0.0, 1.0],
            [-1.0, 0.0],
        ],
        dtype=np.float32,
    )
    # Deliberately a different dimensionality from the key space.
    values = np.asarray(
        [
            [10.0, 0.0, 0.0],
            [8.0, 2.0, 0.0],
            [0.0, 10.0, 0.0],
            [0.0, 0.0, 10.0],
        ],
        dtype=np.float32,
    )
    return SemanticMemory(
        keys=keys,
        values=values,
        document_ids=np.asarray([0, 1, 2, 3]),
        positions=np.asarray([4, 7, 3, 9]),
        key_schema="tiny16-local-v1",
        value_schema="jina256-absolute-v1",
    )


def test_cross_space_key_value_retrieval_is_allowed() -> None:
    """64d->1024d is conceptually fine: retrieval is association, not subtraction."""
    memory = _memory()
    found = retrieve(np.asarray([1.0, 0.0]), memory, k=1, mode="top1")
    assert found.value.shape == (3,)
    assert np.allclose(found.value, [10.0, 0.0, 0.0])
    assert found.confidence == pytest.approx(1.0)


def test_topk_barycenter_uses_similar_values_not_a_plain_centroid() -> None:
    memory = _memory()
    found = retrieve(
        np.asarray([1.0, 0.0]), memory, k=2, temperature=0.2, mode="topk_barycenter"
    )
    assert set(found.indices.tolist()) == {0, 1}
    assert found.value[0] > found.value[1] > 0
    assert found.value[2] == pytest.approx(0.0)
    assert found.weights.sum() == pytest.approx(1.0)


def test_confirmatory_lodo_memory_excludes_the_held_out_document_completely() -> None:
    memory = _memory()
    mask = admissible_memory_mask(memory, query_document=0, query_position=100)
    assert not mask[0]
    assert mask[1:].all()

    found = retrieve(np.asarray([1.0, 0.0]), memory, k=1, allowed=mask, mode="top1")
    # The exact nearest row belonged to the held-out document, so the next best
    # training-document memory must be used instead.
    assert found.indices.tolist() == [1]


def test_same_document_prefix_mode_never_exposes_future_rows() -> None:
    memory = SemanticMemory(
        keys=np.eye(3, dtype=np.float32),
        values=np.eye(3, dtype=np.float32),
        document_ids=np.asarray([7, 7, 8]),
        positions=np.asarray([2, 12, 1]),
        key_schema="cheap",
        value_schema="coarse",
    )
    mask = admissible_memory_mask(
        memory,
        query_document=7,
        query_position=10,
        allow_same_document_prefix=True,
    )
    assert mask.tolist() == [True, False, True]


def test_low_confidence_retrieval_falls_back_to_real_channel() -> None:
    memory = _memory()
    completion = complete_channel(
        np.asarray([0.7, 0.7]),
        memory,
        query_document=99,
        query_position=0,
        threshold=0.99,
        real_value=np.asarray([3.0, 4.0, 5.0]),
        k=2,
    )
    assert completion.source == "real_fallback"
    assert np.allclose(completion.value, [3.0, 4.0, 5.0])
    assert completion.retrieval is not None


def test_high_confidence_retrieval_avoids_the_expensive_channel() -> None:
    memory = _memory()
    completion = complete_channel(
        np.asarray([1.0, 0.0]),
        memory,
        query_document=99,
        query_position=0,
        threshold=0.95,
        real_value=np.asarray([99.0, 99.0, 99.0]),
        k=1,
        mode="top1",
    )
    assert completion.source == "retrieved"
    assert np.allclose(completion.value, [10.0, 0.0, 0.0])


def test_low_confidence_without_a_real_fallback_is_explicit_failure() -> None:
    with pytest.raises(ValueError, match="no real fallback"):
        complete_channel(
            np.asarray([0.7, 0.7]),
            _memory(),
            query_document=99,
            query_position=0,
            threshold=0.99,
            real_value=None,
        )


def test_ledger_separates_retrieval_from_real_fallbacks() -> None:
    memory = _memory()
    retrieved = complete_channel(
        np.asarray([1.0, 0.0]),
        memory,
        query_document=99,
        query_position=0,
        threshold=0.95,
        real_value=np.asarray([1.0, 1.0, 1.0]),
        k=1,
        mode="top1",
    )
    fallback = complete_channel(
        np.asarray([0.7, 0.7]),
        memory,
        query_document=99,
        query_position=0,
        threshold=0.99,
        real_value=np.asarray([1.0, 1.0, 1.0]),
        k=2,
    )
    ledger = completion_ledger([retrieved, fallback])
    assert ledger["retrieved"] == 1
    assert ledger["real_fallbacks"] == 1
    assert ledger["encoder_calls_avoided"] == 1
    assert ledger["retrieval_fraction"] == pytest.approx(0.5)
