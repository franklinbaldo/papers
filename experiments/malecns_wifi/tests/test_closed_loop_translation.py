from __future__ import annotations

import pytest


torch = pytest.importorskip("torch")

from malecns_wifi.closed_loop_translation import (  # noqa: E402
    TranslationSpec,
    closed_loop_forward,
    make_direct_low_rank,
    make_translator,
    translation_loss,
)


def _toy_operator(neurons: int = 12):
    # Deterministic recurrent graph with self-memory plus a directed ring.
    rows = []
    cols = []
    values = []
    for i in range(neurons):
        rows.extend([i, i])
        cols.extend([i, (i - 1) % neurons])
        values.extend([0.30, 0.20])
    indices = torch.tensor([rows, cols], dtype=torch.int64)
    values = torch.tensor(values, dtype=torch.float32)
    return torch.sparse_coo_tensor(indices, values, (neurons, neurons)).coalesce()


def _fixture():
    torch.manual_seed(7)
    source_dim = 6
    target_dim = 5
    neurons = 12
    sensory = 4
    readout_dim = 7
    batch = 3
    spec = TranslationSpec(rank=3, steps=4, leak=0.5, gain=0.8, target_drive_rms=0.1)
    model = make_translator(source_dim, target_dim, sensory, readout_dim, spec)
    operator = _toy_operator(neurons)
    input_indices = torch.tensor([0, 2, 5, 9], dtype=torch.int64)
    readout_projection = torch.randn(readout_dim, neurons) / neurons**0.5
    source = torch.randn(batch, source_dim)
    target = torch.randn(batch, target_dim)
    return model, operator, source, target, input_indices, readout_projection, spec


def test_closed_loop_returns_full_quality_trajectory_and_persistent_state():
    model, operator, source, target, inputs, projection, spec = _fixture()
    result = closed_loop_forward(
        model,
        operator,
        source,
        target=target,
        input_indices=inputs,
        readout_projection=projection,
        spec=spec,
        feedback=True,
    )

    assert result["prediction_path"].shape == (source.shape[0], spec.steps + 1, target.shape[1])
    assert result["cosine_path"].shape == (source.shape[0], spec.steps + 1)
    assert result["error_contraction"].shape == (source.shape[0], spec.steps)
    assert result["state_path"].shape == (source.shape[0], spec.steps + 1, operator.shape[0])
    assert torch.isfinite(result["prediction_path"]).all()
    assert torch.isfinite(result["error_contraction"]).all()

    # State is genuinely carried forward; later states are not resets of step zero.
    assert not torch.allclose(result["state_path"][:, 0], result["state_path"][:, 1])


def test_gradients_reach_all_three_adapters_but_not_operator_or_fixed_projection():
    model, operator, source, target, inputs, projection, spec = _fixture()
    result = closed_loop_forward(
        model,
        operator,
        source,
        target=target,
        input_indices=inputs,
        readout_projection=projection,
        spec=spec,
        feedback=True,
    )
    loss = translation_loss(result, target)
    loss.backward()

    for name, parameters in model.parameter_groups().items():
        assert parameters, name
        assert any(p.grad is not None and torch.isfinite(p.grad).all() for p in parameters), name

    assert operator.requires_grad is False
    assert projection.requires_grad is False


def test_feedback_changes_the_next_state_without_changing_model_or_input():
    model, operator, source, target, inputs, projection, spec = _fixture()
    closed = closed_loop_forward(
        model,
        operator,
        source,
        target=target,
        input_indices=inputs,
        readout_projection=projection,
        spec=spec,
        feedback=True,
    )
    opened = closed_loop_forward(
        model,
        operator,
        source,
        target=target,
        input_indices=inputs,
        readout_projection=projection,
        spec=spec,
        feedback=False,
    )

    # The first estimate is identical; only subsequent state updates can see feedback.
    assert torch.allclose(closed["prediction_path"][:, 0], opened["prediction_path"][:, 0])
    assert not torch.allclose(closed["state_path"][:, 1], opened["state_path"][:, 1])
    assert torch.count_nonzero(closed["feedback_norm_path"]) > 0
    assert torch.count_nonzero(opened["feedback_norm_path"]) == 0


def test_direct_low_rank_baseline_has_no_recurrent_dependency():
    torch.manual_seed(3)
    baseline = make_direct_low_rank(6, 5, rank=3)
    output = baseline(torch.randn(4, 6))
    assert output.shape == (4, 5)
    output.square().mean().backward()
    assert all(p.grad is not None for p in baseline.parameters())


def test_teacher_feedback_requires_matching_batch():
    model, operator, source, target, inputs, projection, spec = _fixture()
    with pytest.raises(ValueError, match="batch sizes differ"):
        closed_loop_forward(
            model,
            operator,
            source,
            target=target[:2],
            input_indices=inputs,
            readout_projection=projection,
            spec=spec,
        )
