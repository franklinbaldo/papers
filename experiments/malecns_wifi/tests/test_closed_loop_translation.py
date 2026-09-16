"""Tests for the closed-loop translation substrate and its metrics.

The properties worth testing here are the ones a result would be wrong without:
the substrate never receives gradient, the state carries across rounds, and the
feedback channel really is as narrow as its name says.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp

from malecns_wifi.closed_loop_translation import (
    FeedbackMode,
    TranslationSpec,
    build_substrate,
    feedback_features,
    make_low_rank_adapter,
    make_translator,
    protocol_dict,
    round_loss,
    run_loop,
    select_ports,
)
from malecns_wifi.translation_metrics import (
    error_norms,
    knn_preservation,
    retrieval,
    score_trajectory,
)

torch = pytest.importorskip("torch")


def toy_operator(neurons: int = 64, seed: int = 0) -> sp.csr_matrix:
    rng = np.random.default_rng(seed)
    dense = rng.normal(size=(neurons, neurons)).astype(np.float32)
    dense[np.abs(dense) < 1.6] = 0.0
    matrix = sp.csr_matrix(dense)
    row_sum = np.asarray(np.abs(matrix).sum(axis=1)).ravel()
    matrix.data /= np.repeat(np.maximum(row_sum, 1.0), np.diff(matrix.indptr)).astype(np.float32)
    return matrix


def toy_substrate(spec: TranslationSpec, neurons: int = 64):
    matrix = toy_operator(neurons)
    return build_substrate(
        matrix,
        name="toy",
        spec=spec,
        input_indices=np.arange(0, 8),
        feedback_indices=np.arange(8, 16),
        seed=1,
        device=torch.device("cpu"),
    )


def toy_batch(source_dim: int = 12, target_dim: int = 20, batch: int = 5):
    generator = torch.Generator().manual_seed(3)
    source = torch.randn(batch, source_dim, generator=generator)
    target = torch.randn(batch, target_dim, generator=generator)
    return source, target


def test_feedback_modes_expose_exactly_what_they_advertise() -> None:
    target_dim = 20
    b_hat = torch.randn(4, target_dim)
    b_target = torch.randn(4, target_dim)
    for mode in (FeedbackMode.SCALAR, FeedbackMode.RESIDUAL, FeedbackMode.FULL):
        features = feedback_features(b_hat, b_target, 0, 4, mode)
        assert features.shape[1] == mode.feature_dim(target_dim)
    scalar = feedback_features(b_hat, b_target, 1, 4, FeedbackMode.SCALAR)
    assert scalar.shape[1] == 3, "the scalar channel must stay too narrow to carry a target"
    assert not FeedbackMode.SCALAR.can_reconstruct_target
    assert FeedbackMode.RESIDUAL.can_reconstruct_target
    assert FeedbackMode.FULL.can_reconstruct_target


def test_scalar_feedback_is_invariant_to_target_rotation() -> None:
    """The narrow channel must carry error magnitude only, not target identity."""
    generator = torch.Generator().manual_seed(11)
    b_hat = torch.randn(3, 8, generator=generator)
    b_target = torch.randn(3, 8, generator=generator)
    rotation, _ = torch.linalg.qr(torch.randn(8, 8, generator=generator))
    first = feedback_features(b_hat, b_target, 0, 4, FeedbackMode.SCALAR)
    rotated = feedback_features(b_hat @ rotation, b_target @ rotation, 0, 4, FeedbackMode.SCALAR)
    assert torch.allclose(first, rotated, atol=1e-5)


def test_gradient_reaches_every_adapter_and_never_the_substrate() -> None:
    spec = TranslationSpec(rank=4, rounds=3, inner_steps=1, drive_dim=8, readout_width=16)
    substrate = toy_substrate(spec)
    source, target = toy_batch()
    model = make_translator(source.shape[1], target.shape[1], spec, device=torch.device("cpu"))

    predictions, _ = run_loop(model, substrate, source, target, spec)
    loss, _ = round_loss(predictions, target, spec)
    loss.backward()

    reached = {name.split(".")[0] for name, parameter in model.named_parameters()
               if parameter.grad is not None and float(parameter.grad.norm()) > 0.0}
    assert {"adapter_in", "adapter_out", "adapter_feedback"} <= reached

    for tensor in (substrate.operator, substrate.operator_t, substrate.input_weights,
                   substrate.feedback_weights, substrate.readout_projection):
        assert not tensor.requires_grad
        assert getattr(tensor, "grad", None) is None


def test_frozen_spmm_backward_matches_dense_autograd() -> None:
    """The hand-written backward must be the real Jacobian, not an approximation."""
    from malecns_wifi.closed_loop_translation import FrozenSpMM, csr_to_torch

    matrix = toy_operator(32, seed=5)
    operator = csr_to_torch(matrix, device=torch.device("cpu"))
    operator_t = csr_to_torch(sp.csr_matrix(matrix.T), device=torch.device("cpu"))
    dense = torch.as_tensor(matrix.toarray(), dtype=torch.float32)

    x = torch.randn(32, 3, requires_grad=True)
    FrozenSpMM.apply(x, operator, operator_t).square().sum().backward()
    custom = x.grad.clone()

    y = x.detach().clone().requires_grad_(True)
    (dense @ y).square().sum().backward()
    assert torch.allclose(custom, y.grad, atol=1e-4)


def test_state_persists_across_rounds_and_feedback_changes_the_trajectory() -> None:
    spec = TranslationSpec(rank=4, rounds=4, inner_steps=1, drive_dim=8, readout_width=16,
                           feedback_mode=FeedbackMode.FULL)
    substrate = toy_substrate(spec)
    source, target = toy_batch()
    model = make_translator(source.shape[1], target.shape[1], spec, device=torch.device("cpu"))
    # A zero-initialised LoRA residual would make every round identical through
    # adapter_out; perturb it so the test measures the loop, not the init.
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.add_(torch.randn_like(parameter) * 0.2)

    with torch.no_grad():
        closed, diagnostics = run_loop(model, substrate, source, target, spec)
        open_spec = TranslationSpec(
            **{**{key: getattr(spec, key) for key in spec.__dataclass_fields__},
               "feedback_mode": FeedbackMode.NONE}
        )
        opened, _ = run_loop(model, substrate, source, target, open_spec)

    state_rms = [item["state_rms"] for item in diagnostics]
    assert len(set(np.round(state_rms, 9))) > 1, "state must evolve across rounds"
    assert torch.allclose(closed[0], opened[0], atol=1e-6), "round 0 precedes any feedback"
    assert max(float((c - o).norm()) for c, o in zip(closed[1:], opened[1:], strict=True)) > 1e-6


def test_open_loop_spec_has_no_feedback_adapter() -> None:
    spec = TranslationSpec(rank=4, rounds=2, inner_steps=1, drive_dim=8, readout_width=16,
                           feedback_mode=FeedbackMode.NONE)
    model = make_translator(12, 20, spec, device=torch.device("cpu"))
    assert model.adapter_feedback is None
    assert model.describe()["feedback_can_reconstruct_target"] is False


def test_ports_must_be_disjoint() -> None:
    spec = TranslationSpec(rank=4, rounds=2, inner_steps=1, drive_dim=8, readout_width=16)
    with pytest.raises(ValueError, match="disjoint"):
        build_substrate(
            toy_operator(), name="toy", spec=spec,
            input_indices=np.arange(0, 8), feedback_indices=np.arange(4, 12),
            seed=1, device=torch.device("cpu"),
        )


def test_select_ports_marks_the_feedback_port_as_synthetic() -> None:
    superclass = np.asarray(["cb_sensory"] * 10 + ["intrinsic"] * 40)
    inputs, feedback, report = select_ports(superclass, neurons=50, seed=0)
    assert inputs.size == 10
    assert np.intersect1d(inputs, feedback).size == 0
    assert "synthetic" in report["feedback_port_kind"]


def test_low_rank_adapter_is_only_called_lora_when_it_has_a_frozen_base() -> None:
    plain = make_low_rank_adapter(6, 8, rank=2)
    assert plain.describe()["kind"] == "trainable_low_rank_adapter"
    base = torch.randn(8, 6)
    lora = make_low_rank_adapter(6, 8, rank=2, base=base)
    assert lora.describe()["kind"] == "lora"
    values = torch.randn(3, 6)
    # A zero-initialised residual means the module starts as exactly the base map.
    assert torch.allclose(lora(values), values @ base.T, atol=1e-6)


def test_round_weights_sum_to_one_and_linear_leans_late() -> None:
    spec = TranslationSpec(rounds=4)
    weights = spec.round_weights()
    assert np.isclose(weights.sum(), 1.0)
    assert weights[-1] > weights[0]
    assert np.isclose(TranslationSpec(rounds=3, round_loss_weighting="final").round_weights()[-1], 1.0)


def test_retrieval_reports_chance_and_is_perfect_on_identity() -> None:
    values = np.random.default_rng(0).normal(size=(30, 12)).astype(np.float32)
    result = retrieval(values, values)
    assert result["retrieval@1"] == 1.0
    assert np.isclose(result["chance_retrieval@1"], 1.0 / 30)
    assert knn_preservation(values, values, k=5) == 1.0


def test_score_trajectory_flags_an_idle_loop() -> None:
    rng = np.random.default_rng(1)
    target = rng.normal(size=(20, 8)).astype(np.float32)
    constant = rng.normal(size=(20, 8)).astype(np.float32)
    idle = score_trajectory([constant, constant.copy()], target)
    assert idle["trajectory_gain"]["loop_is_idle"] is True

    improving = score_trajectory([constant, 0.5 * constant + 0.5 * target], target)
    assert improving["trajectory_gain"]["loop_is_idle"] is False
    assert improving["error_contraction"][0]["mean_ratio"] < 1.0


def test_error_contraction_ratio_direction() -> None:
    target = np.eye(4, dtype=np.float32)
    worse = np.roll(np.eye(4, dtype=np.float32), 1, axis=1)
    assert float(np.mean(error_norms(target, target))) < float(np.mean(error_norms(worse, target)))


def test_protocol_dict_names_the_claim_boundary_and_the_weights_distinction() -> None:
    payload = protocol_dict(TranslationSpec())
    assert "autonomous inference" in payload["claim_boundary"]
    assert "not trained artificial-neural-network weights" in payload["weights_disambiguation"]
    assert payload["trainable"] == ["adapter_in", "adapter_out residual", "adapter_feedback"]
    assert payload["recurrent_depth"] == payload["spec"]["rounds"] * payload["spec"]["inner_steps"]


def test_infonce_is_the_default_and_punishes_centroid_collapse() -> None:
    """The whole point of the contrastive objective, as a test rather than a comment."""
    spec = TranslationSpec(rounds=1)
    assert spec.objective == "infonce"
    generator = torch.Generator().manual_seed(7)
    target = torch.nn.functional.normalize(torch.randn(16, 32, generator=generator), dim=-1)
    # An anisotropic space: every target leans toward a shared direction.
    bias = torch.nn.functional.normalize(torch.randn(1, 32, generator=generator), dim=-1)
    target = torch.nn.functional.normalize(target + 2.0 * bias, dim=-1)
    collapsed = bias.expand_as(target).contiguous()
    perfect = target.clone()

    cosine_spec = TranslationSpec(rounds=1, objective="cosine")
    collapsed_cosine, _ = round_loss([collapsed], target, cosine_spec)
    perfect_cosine, _ = round_loss([perfect], target, cosine_spec)
    collapsed_nce, _ = round_loss([collapsed], target, spec)
    perfect_nce, _ = round_loss([perfect], target, spec)

    # Cosine barely separates a constant prediction from a perfect one here...
    assert float(collapsed_cosine) < 0.35
    # ...while InfoNCE puts the collapse at chance and the perfect map near zero.
    assert float(collapsed_nce) > float(perfect_nce) + 1.0
    assert float(perfect_nce) < float(collapsed_nce)
    assert float(perfect_cosine) < float(collapsed_cosine)


def test_centroid_baseline_beats_nothing_on_retrieval() -> None:
    from malecns_wifi.translation_metrics import centroid_baseline

    rng = np.random.default_rng(4)
    bias = rng.normal(size=(1, 24))
    target = rng.normal(size=(60, 24)) + 3.0 * bias
    result = centroid_baseline(target)
    assert result["mean_cosine"] > 0.8, "a constant prediction can score high cosine"
    assert result["retrieval@1"] <= 2.0 / 60, "and still retrieve at chance"
    assert result["mean_pairwise_cosine_in_target_space"] > 0.5


def test_split_indices_are_group_disjoint() -> None:
    from malecns_wifi.translation_pairs import split_indices

    groups = np.repeat(np.arange(100), 2)
    train, val, test = split_indices(len(groups), seed=0, groups=groups)
    assert len(set(train) | set(val) | set(test)) == len(groups)
    for left, right in ((train, val), (train, test), (val, test)):
        assert not set(left) & set(right)
        assert not set(groups[left]) & set(groups[right]), "a group must not straddle a split"


def test_matched_bulk_gain_puts_different_operators_at_the_same_operating_point() -> None:
    from malecns_wifi.closed_loop_translation import bulk_gain

    spec = TranslationSpec(rank=4, rounds=2, inner_steps=1, drive_dim=8, readout_width=16)
    strong = toy_operator(64, seed=0)
    weak = strong.copy()
    weak.data = weak.data * np.float32(0.1)
    assert bulk_gain(weak) < bulk_gain(strong)

    built = [
        build_substrate(
            matrix, name="m", spec=spec, input_indices=np.arange(0, 8),
            feedback_indices=np.arange(8, 16), seed=1, device=torch.device("cpu"),
            gain_mode="matched_bulk", bulk_target=0.9,
        )
        for matrix in (strong, weak)
    ]
    points = [item.gain_report["realised_bulk_operating_point"] for item in built]
    assert all(abs(point - 0.9) < 1e-3 for point in points)
    assert built[0].gain != pytest.approx(built[1].gain), "the rescaling must actually differ"
