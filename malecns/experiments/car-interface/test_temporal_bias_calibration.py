from temporal_bias_calibration import PersistentBiasCalibrator


def test_requires_persistent_evidence_before_correction():
    calibrator = PersistentBiasCalibrator()
    for _ in range(3):
        calibrator.observe(1.5, 0.0)
        assert not calibrator.active
    calibrator.observe(1.5, 0.0)
    assert calibrator.active
    assert calibrator.correction > 0.0


def test_zero_mean_small_residuals_do_not_activate():
    calibrator = PersistentBiasCalibrator()
    for residual in (0.2, -0.3, 0.1, -0.2, 0.25, -0.1) * 4:
        calibrator.observe(residual, 0.0)
    assert not calibrator.active
    assert calibrator.correction == 0.0


def test_apply_subtracts_evidenced_reference_bias():
    calibrator = PersistentBiasCalibrator(alpha=0.5)
    for _ in range(6):
        calibrator.observe(2.0, 0.0)
    corrected = calibrator.apply(12.0)
    assert corrected < 12.0
    assert corrected > 10.0


def test_opposite_signed_evidence_decays_persistence():
    calibrator = PersistentBiasCalibrator()
    for _ in range(6):
        calibrator.observe(1.5, 0.0)
    assert calibrator.active
    for _ in range(3):
        calibrator.observe(-1.5, 0.0)
    assert not calibrator.active
