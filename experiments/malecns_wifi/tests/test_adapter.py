"""Tests for the trainable adapter.

These run on CPU at toy scale. The claims they check are the ones that silently
fail otherwise: that the gradient really reaches the input embedding *through*
the frozen recurrence, that truncation actually truncates, that the frozen
operator stays frozen, and that the direct control cannot see the fly at all.
"""

import numpy as np
import pytest
import scipy.sparse as sp

torch = pytest.importorskip("torch")

from malecns_wifi.adapter import (  # noqa: E402
    AdapterSpec,
    TrainSpec,
    make_models,
    parameter_count,
    reservoir_forward,
    to_sparse,
    train_condition,
)
from malecns_wifi.tagger import CLASSES, Document, Populations  # noqa: E402

NEURONS = 40


def _populations() -> Populations:
    return Populations(
        input_indices=np.arange(0, 12),
        readout_indices=np.arange(12, 20),
        input_selector=("cb_sensory",),
        readout_selector=("descending_neuron",),
    )


def _operator(seed: int = 0):
    rng = np.random.default_rng(seed)
    dense = rng.normal(size=(NEURONS, NEURONS)).astype(np.float32)
    dense[rng.random((NEURONS, NEURONS)) > 0.3] = 0.0
    matrix = sp.csr_matrix(dense)
    matrix.data /= max(float(np.abs(matrix).sum(axis=1).max()), 1.0)
    return matrix


def _batch(count: int = 3, width: int = 12):
    rng = np.random.default_rng(1)
    bytes_batch = torch.from_numpy(rng.integers(1, 255, size=(count, width)).astype(np.int64))
    lengths = torch.from_numpy(np.full(count, width, dtype=np.int64))
    return bytes_batch, lengths


def _spec(**overrides) -> AdapterSpec:
    base = {"embedding_dim": 8, "input_neurons": 0, "window": 4, "batch_size": 2}
    return AdapterSpec(**{**base, **overrides})


def test_gradient_reaches_the_embedding_through_the_frozen_recurrence() -> None:
    """The whole point: the input side learns via the fly, not around it."""
    spec = _spec()
    model, _, _ = make_models(_populations(), spec)
    operator = to_sparse(_operator())
    bytes_batch, lengths = _batch()

    logits = reservoir_forward(model, operator, bytes_batch, lengths, spec)
    logits.sum().backward()

    assert model.embedding.weight.grad is not None
    assert torch.isfinite(model.embedding.weight.grad).all()
    assert model.embedding.weight.grad.abs().sum() > 0
    assert model.project.weight.grad.abs().sum() > 0


def test_recurrence_is_load_bearing_for_the_input_gradient() -> None:
    """With the operator zeroed the readout sees only the last window's drive.

    A non-trivial gradient with a live operator and a smaller one without it is
    what distinguishes "the fly is in the loop" from "the adapter is talking to
    itself".
    """
    spec = _spec(window=64)  # one window, so nothing is truncated away
    bytes_batch, lengths = _batch(width=12)

    grads = {}
    for label, matrix in (("live", _operator()), ("zero", sp.csr_matrix((NEURONS, NEURONS)))):
        torch.manual_seed(0)
        model, _, _ = make_models(_populations(), spec)
        logits = reservoir_forward(model, to_sparse(matrix.astype(np.float32)), bytes_batch,
                                   lengths, spec)
        logits.sum().backward()
        grads[label] = float(model.embedding.weight.grad.abs().sum())

    assert grads["live"] != pytest.approx(grads["zero"], rel=1e-3)


def test_truncation_cuts_the_gradient_between_windows() -> None:
    """A short window must not accumulate gradient from the whole document."""
    bytes_batch, lengths = _batch(width=16)
    grads = {}
    for window in (2, 16):
        spec = _spec(window=window)
        torch.manual_seed(0)
        model, _, _ = make_models(_populations(), spec)
        logits = reservoir_forward(model, to_sparse(_operator()), bytes_batch, lengths, spec)
        logits.sum().backward()
        grads[window] = float(model.embedding.weight.grad.abs().sum())

    assert grads[2] != pytest.approx(grads[16], rel=1e-6), "window length changed nothing"


def test_frozen_operator_never_becomes_a_parameter() -> None:
    spec = _spec()
    model, control, _ = make_models(_populations(), spec)
    names = {name for name, _ in model.named_parameters()}
    assert names == {"embedding.weight", "project.weight", "readout.weight", "readout.bias"}
    assert "inputs" in dict(model.named_buffers())
    # The control has no path to the connectome at all.
    assert not any("operator" in name or "inputs" in name for name, _ in control.named_buffers())


def test_direct_control_runs_without_any_operator() -> None:
    spec = _spec()
    _, control, _ = make_models(_populations(), spec)
    bytes_batch, lengths = _batch()
    logits = control(bytes_batch, lengths)
    assert logits.shape == (bytes_batch.shape[0], len(CLASSES))
    logits.sum().backward()
    assert control.embedding.weight.grad.abs().sum() > 0


def test_direct_control_is_matched_in_parameters() -> None:
    """Within a few percent: the control must not be handicapped or advantaged."""
    spec = _spec()
    model, control, _ = make_models(_populations(), spec)
    fly, direct = parameter_count(model), parameter_count(control)
    assert abs(fly - direct) / fly < 0.05, f"{fly} vs {direct}"


def test_padding_does_not_change_a_shorter_document() -> None:
    """A document padded in a batch must score as it does alone."""
    spec = _spec(window=64)
    torch.manual_seed(0)
    model, _, _ = make_models(_populations(), spec)
    operator = to_sparse(_operator())
    rng = np.random.default_rng(3)
    short = rng.integers(1, 255, size=6).astype(np.int64)

    alone = reservoir_forward(
        model,
        operator,
        torch.from_numpy(short[None, :]),
        torch.tensor([6]),
        spec,
    )
    padded_bytes = np.zeros((2, 11), dtype=np.int64)
    padded_bytes[0, :6] = short
    padded_bytes[1, :] = rng.integers(1, 255, size=11)
    together = reservoir_forward(
        model, operator, torch.from_numpy(padded_bytes), torch.tensor([6, 11]), spec
    )
    assert torch.allclose(alone[0], together[0], atol=1e-5)


def test_training_selects_a_checkpoint_on_validation() -> None:
    spec = TrainSpec(
        max_epochs=3, min_epochs=1, patience=1, seeds=(0,), adapter=_spec(batch_size=2)
    )
    model, _, _ = make_models(_populations(), spec.adapter)
    operator = to_sparse(_operator())
    train = [Document(f"t{i}", "texto de treino " * 2, gold=CLASSES[i % 3], weak=None)
             for i in range(6)]
    validate = [Document(f"v{i}", "texto de validacao " * 2, gold=CLASSES[i % 3], weak=None)
                for i in range(3)]

    result = train_condition("malecns", model, operator, train, validate, spec, device="cpu")
    assert 1 <= result["best_epoch"] <= 3
    assert len(result["history"]) >= 1
    assert result["parameters"] == parameter_count(model)
    assert 0.0 <= result["validation_macro_f1"] <= 1.0
