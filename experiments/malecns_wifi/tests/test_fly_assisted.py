"""Toy-scale invariants for fly-assisted standalone tagging."""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from malecns_wifi.fly_assisted import (  # noqa: E402
    FlyAssistSpec,
    make_model,
    semantic_reservoir_states,
    training_loss,
)


def _operator(neurons: int = 18):
    indices = torch.arange(neurons)
    rows = torch.cat([indices, indices])
    cols = torch.cat([indices, torch.roll(indices, 1)])
    values = torch.cat([
        torch.full((neurons,), 0.35),
        torch.full((neurons,), 0.15),
    ])
    return torch.sparse_coo_tensor(
        torch.stack([rows, cols]), values, (neurons, neurons)
    ).coalesce()


def _case():
    torch.manual_seed(0)
    spec = FlyAssistSpec(rank=3, steps_per_chunk=2, target_drive_rms=0.05)
    chunks, input_dim, tags, flavour_dim = 5, 7, 3, 4
    readout = torch.tensor([8, 9, 10, 11])
    inputs = torch.tensor([0, 1, 2, 3, 4, 5])
    model = make_model(input_dim, tags, len(readout), flavour_dim, spec)
    # Make the residual path live on the first backward pass. Production starts
    # from identity (zero up-projection); this is only to isolate the auxiliary
    # gradient in a one-step unit test.
    with torch.no_grad():
        model.up.weight.normal_(0, 0.05)
    features = torch.randn(chunks, input_dim)
    masks = torch.tensor(
        [[1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]],
        dtype=torch.float32,
    )
    flavours = torch.randn(tags, flavour_dim)
    flavours = flavours / torch.linalg.vector_norm(flavours, dim=1, keepdim=True)
    projection = torch.randn(len(inputs), input_dim)
    return spec, model, features, masks, flavours, projection, inputs, readout


def test_assistance_anneals_to_exactly_zero() -> None:
    spec = FlyAssistSpec(assist_weight=1.0, assist_fraction=0.7)
    values = [spec.assist_lambda(epoch, 10) for epoch in range(10)]
    assert values[0] == pytest.approx(1.0)
    assert values[6] == pytest.approx(0.0)
    assert all(value == 0.0 for value in values[6:])


def test_zero_assistance_needs_no_fly_and_is_deployment_path() -> None:
    spec, model, features, masks, _, _, _, _ = _case()
    result = training_loss(model, features, masks, spec=spec, assist_lambda=0.0)
    direct_logits, _ = model.standalone_logits(features)

    assert torch.allclose(result["logits"], direct_logits)
    assert result["fly_loss"].item() == 0.0
    assert result["drive_rms"].item() == 0.0


def test_auxiliary_gradient_reaches_the_flavourizer_through_frozen_recurrence() -> None:
    spec, model, features, masks, flavours, projection, inputs, readout = _case()
    result = training_loss(
        model,
        features,
        masks,
        spec=spec,
        assist_lambda=1.0,
        operator=_operator(),
        input_weights=projection,
        input_indices=inputs,
        readout_indices=readout,
        flavours=flavours,
    )
    result["fly_loss"].backward()

    assert model.up.weight.grad is not None
    assert model.up.weight.grad.abs().sum() > 0
    assert model.down.weight.grad is not None
    assert model.down.weight.grad.abs().sum() > 0


def test_drive_energy_cannot_be_increased_by_scaling_the_semantics() -> None:
    spec, model, features, _, _, projection, inputs, readout = _case()
    transformed, _ = model.transform(features)
    _, first = semantic_reservoir_states(
        _operator(),
        transformed,
        input_weights=projection,
        input_indices=inputs,
        readout_indices=readout,
        spec=spec,
    )
    _, second = semantic_reservoir_states(
        _operator(),
        transformed * 100.0,
        input_weights=projection,
        input_indices=inputs,
        readout_indices=readout,
        spec=spec,
    )

    assert first.item() == pytest.approx(0.05, rel=1e-5)
    assert second.item() == pytest.approx(0.05, rel=1e-5)


def test_taste_head_is_disposable_at_inference() -> None:
    spec, model, features, _, _, _, _, _ = _case()
    before, _ = model.standalone_logits(features)
    with torch.no_grad():
        model.taste_head.weight.normal_(100, 10)
        model.taste_head.bias.normal_(100, 10)
    after, _ = model.standalone_logits(features)
    assert torch.allclose(before, after)
