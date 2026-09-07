from src.validate import check_exceedance, validate_samples


def make_sample(**overrides):
    base = {"sample_id": "S-00001", "source": "LabA", "station": "Station-North-1",
            "parameter": "pH", "sample_date": "2026-01-05", "value": "7.4"}
    base.update(overrides)
    return base


def test_normal_ph_not_flagged():
    assert check_exceedance(make_sample(value="7.4")) is None


def test_low_ph_flagged():
    reason = check_exceedance(make_sample(value="5.9"))
    assert reason is not None
    assert "Below guideline minimum" in reason


def test_high_ph_flagged():
    reason = check_exceedance(make_sample(value="9.5"))
    assert reason is not None
    assert "Exceeds guideline maximum" in reason


def test_arsenic_exceedance_flagged():
    reason = check_exceedance(make_sample(parameter="Dissolved Arsenic", value="8.2"))
    assert reason is not None
    assert "Exceeds guideline maximum" in reason


def test_arsenic_within_guideline_not_flagged():
    assert check_exceedance(make_sample(parameter="Dissolved Arsenic", value="3.1")) is None


def test_validate_samples_splits_correctly():
    samples = [
        make_sample(sample_id="S-1", value="7.4"),          # ok
        make_sample(sample_id="S-2", value="9.8"),          # exceeds
        make_sample(sample_id="S-3", parameter="Turbidity", value="30"),  # exceeds
        make_sample(sample_id="S-4", parameter="Turbidity", value="10"),  # ok
    ]
    clean, exceedances = validate_samples(samples)
    assert len(clean) == 2
    assert len(exceedances) == 2
    assert all("reason" in e for e in exceedances)
