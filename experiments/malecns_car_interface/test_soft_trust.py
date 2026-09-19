from colony import SpecialistReport
from soft_trust import soften_probe, soft_probe_weight


def _report(identifier, value, *, modality, confidence=0.9, age_ms=20.0):
    return SpecialistReport(
        identifier,
        "dynamic-scalar",
        value,
        confidence,
        age_ms=age_ms,
        modality=modality,
    )


def test_soft_weight_falls_with_residual_and_age():
    camera = [_report("c0", 0.0, modality="camera"), _report("c1", 0.05, modality="camera")]
    imu = [_report("i0", 0.0, modality="imu"), _report("i1", -0.03, modality="imu")]

    near = _report("c2", 0.08, modality="camera", age_ms=20.0)
    far = _report("c3", 1.2, modality="camera", age_ms=20.0)
    stale = _report("c4", 0.08, modality="camera", age_ms=600.0)

    assert 0.0 <= soft_probe_weight(camera, far, imu) <= 1.0
    assert soft_probe_weight(camera, near, imu) > soft_probe_weight(camera, far, imu)
    assert soft_probe_weight(camera, near, imu) > soft_probe_weight(camera, stale, imu)


def test_soften_probe_bounds_candidate_influence_without_rejecting_it():
    camera = [_report("c0", 0.0, modality="camera"), _report("c1", 0.02, modality="camera")]
    imu = [_report("i0", -0.01, modality="imu"), _report("i1", 0.01, modality="imu")]
    candidate = _report("c2", 1.5, modality="camera", confidence=0.95)

    softened = soften_probe(camera, candidate, imu, residual_scale=0.75)

    assert softened.specialist_id == candidate.specialist_id
    assert softened.modality == candidate.modality
    assert softened.value != candidate.value
    assert abs(softened.value) < abs(candidate.value)
    assert 0.0 < softened.confidence < candidate.confidence


def test_soft_trust_rejects_cross_channel_leakage():
    camera = [_report("c0", 0.0, modality="camera")]
    imu = [_report("i0", 0.0, modality="imu")]
    candidate = SpecialistReport(
        "c1",
        "another-channel",
        0.1,
        0.9,
        age_ms=20.0,
        modality="camera",
    )

    try:
        soft_probe_weight(camera, candidate, imu)
    except ValueError as exc:
        assert "shared semantic channel" in str(exc)
    else:
        raise AssertionError("channel mismatch should be rejected")
