import pytest

from calculator.greenwave_calc import compute_greenwave_offset


def test_matches_the_readme_worked_example():
    # 500m at 50 km/h, 60s base cycle - the exact example used throughout
    # the README and as firmware/main.py's own default configuration.
    result = compute_greenwave_offset(distance_m=500, speed_kmh=50, base_cycle_s=60)
    assert result["practical_offset_s"] == 36


def test_offset_wraps_within_the_base_cycle():
    # A long distance at a slow speed produces a raw travel time far
    # longer than one cycle - the practical offset must still land
    # inside [0, base_cycle_s).
    result = compute_greenwave_offset(distance_m=5000, speed_kmh=20, base_cycle_s=60)
    assert 0 <= result["practical_offset_s"] < 60


def test_zero_base_cycle_raises_instead_of_crashing():
    """
    Regression test for a real bug: base_cycle_s=0 used to reach a bare
    `% base_cycle_s` with no validation, raising an uncaught
    ZeroDivisionError all the way out of the CLI. Now raises a clear
    ValueError instead.
    """
    with pytest.raises(ValueError, match="Base cycle time"):
        compute_greenwave_offset(distance_m=500, speed_kmh=50, base_cycle_s=0)


def test_zero_speed_raises_a_clear_error():
    with pytest.raises(ValueError, match="Speed"):
        compute_greenwave_offset(distance_m=500, speed_kmh=0, base_cycle_s=60)


def test_negative_distance_raises_a_clear_error():
    with pytest.raises(ValueError, match="Distance"):
        compute_greenwave_offset(distance_m=-10, speed_kmh=50, base_cycle_s=60)
