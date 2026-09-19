from adaptive_soft_trust import age_normalized_huber_weight, soften_probe_huber
from colony import SpecialistReport


def _report(identifier, value, *, modality, confidence=0.9, age_ms=20.0):
    return SpecialistReport(
        identifier,
        "dynamic-scalar",
        value,
        confidence,
        age_ms=age_ms,
        modality=modality,
    )


def test_age_normalization_reduces_stale_probe_influence():
    camera = [_report("c0", 0.0, modality="camera"), _report("c1", 0.03, modality="camera")]
    imu = [_report("i0", 0.0, modality="imu"), _report("i1", -0.02, modality="imu")]
    fresh = _report("c2", 0.18, modality="camera", age_ms=20.0)
    stale = _report("c3", 0.18, modality="camera", age_ms=600.0)

    fresh_weight = age_normalized_huber_weight(camera, fresh, imu)
    stale_weight = age_normalized_huber_weight(camera, stale, imu)

    assert 0.0 <= stale_weight < fresh_weight <= 1.0


def test_huber_softening_retains_but_bounds_outlier():
    camera = [_report("c0", 0.0, modality="camera"), _report("c1", 0.02, modality="camera")]
    imu = [_report("i0", -0.01, modality="imu"), _report("i1", 0.01, modality="imu")]
    candidate = _report("c2", 1.5, modality="camera", confidence=0.95)

    softened = soften_probe_huber(camera, candidate, imu)

    assert softened.specialist_id == candidate.specialist_id
    assert softened.modality == candidate.modality
    assert softened.value != candidate.value
    assert abs(softened.value) < abs(candidate.value)
    assert 0.0 < softened.confidence < candidate.confidence


def test_age_power_zero_is_less_strict_for_old_reports():
    camera = [_report("c0", 0.0, modality="camera"), _report("c1", 0.03, modality="camera")]
    imu = [_report("i0", 0.0, modality="imu"), _report("i1", -0.02, modality="imu")]
    stale = _report("c2", 0.30, modality="camera", age_ms=450.0)

    fixed_radius = age_normalized_huber_weight(camera, stale, imu, age_power=0.0)
    age_scaled = age_normalized_huber_weight(camera, stale, imu, age_power=1.0)

    assert age_scaled < fixed_radius


def test_adaptive_soft_trust_rejects_cross_modal_identity_error():
    camera = [_report("c0", 0.0, modality="camera")]
    imu = [_report("i0", 0.0, modality="imu")]
    candidate = _report("i1", 0.1, modality="imu")

    try:
        age_normalized_huber_weight(camera, candidate, imu)
    except ValueError as exc:
        assert "candidate modality" in str(exc)
    else:
        raise AssertionError("candidate from another modality should be rejected")
