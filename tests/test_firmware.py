"""
Exercises the real firmware/main.py logic against a mocked `machine`
module (see conftest.py) - not a reimplementation of the logic, the
actual functions the ESP32 runs.
"""
from firmware.main import calculate_light_state, parse_gprmc

# date field is DDMMYY - the firmware assumes a 2000s year (2000 + YY),
# so this uses "170926" (17 Sep 2026) rather than the classic textbook
# NMEA example date (which is from 1994 and would wrongly parse as 2094
# under that assumption - not a bug in the firmware, just picking a test
# date consistent with the year window the code is actually built for).
VALID_GPRMC = (
    "$GPRMC,123519.00,A,4807.038,N,01131.000,E,022.4,084.4,170926,003.1,W*6A"
)
INVALID_FIX_GPRMC = (
    "$GPRMC,123519.00,V,4807.038,N,01131.000,E,022.4,084.4,170926,003.1,W*6A"
)


def test_parse_gprmc_extracts_utc_datetime_from_a_valid_fix():
    result = parse_gprmc(VALID_GPRMC)
    assert result == (2026, 9, 17, 12, 35, 19)


def test_parse_gprmc_returns_none_for_an_invalid_fix():
    assert parse_gprmc(INVALID_FIX_GPRMC) is None


def test_parse_gprmc_returns_none_for_unrelated_sentences():
    assert parse_gprmc("$GPGGA,123519,4807.038,N*47") is None


def test_parse_gprmc_returns_none_for_truncated_sentences():
    assert parse_gprmc("$GPRMC,123519.00,A") is None


def test_light_state_is_green_at_the_start_of_the_shifted_cycle():
    # offset=36, base_cycle=60, green=30: shifted_time_s == 0 at hh=0,mm=1,ss=36
    assert calculate_light_state(0, 1, 36, 36, 60, 30, 3) == 'GREEN'


def test_light_state_is_yellow_just_after_green_ends():
    # shifted_time_s == 30 (green ends at 30, yellow runs 30-33)
    assert calculate_light_state(0, 2, 6, 36, 60, 30, 3) == 'YELLOW'


def test_light_state_is_red_for_the_remainder_of_the_cycle():
    # shifted_time_s == 40
    assert calculate_light_state(0, 2, 16, 36, 60, 30, 3) == 'RED'


def test_light_state_stays_continuous_across_an_hour_boundary():
    """
    Regression test for a real bug: an earlier version of this firmware
    computed absolute time as (minutes * 60 + seconds) only, which reset
    to 0 at the top of every hour. For a base_cycle_s that doesn't evenly
    divide 3600 (very plausible - e.g. 70s), that reset caused the
    computed cycle position to jump discontinuously once every hour,
    which would show up as a visibly glitching traffic light on real
    hardware. Using seconds-since-midnight (hh included) fixes it for the
    hour boundary; this test locks that in with a cycle length (70) that
    does not evenly divide 3600.
    """
    offset, base_cycle, green, yellow = 36, 70, 30, 3

    # Independently recompute the correct (seconds-since-midnight) cycle
    # positions one second apart across the hour boundary.
    before_shifted = ((10 * 3600 + 59 * 60 + 59) - offset) % base_cycle
    after_shifted = ((11 * 3600 + 0 * 60 + 0) - offset) % base_cycle
    assert after_shifted == (before_shifted + 1) % base_cycle

    def expected_color(shifted):
        if shifted < green:
            return 'GREEN'
        if shifted < green + yellow:
            return 'YELLOW'
        return 'RED'

    # The function under test must agree with that reference at both instants,
    # i.e. it really advances one second across the hour boundary instead of
    # jumping. (This actually exercises calculate_light_state; the arithmetic
    # above alone would pass even if the function were broken.)
    before = calculate_light_state(10, 59, 59, offset, base_cycle, green, yellow)
    after = calculate_light_state(11, 0, 0, offset, base_cycle, green, yellow)
    assert before == expected_color(before_shifted)
    assert after == expected_color(after_shifted)

    # Confirm this input really is sensitive to the bug: the OLD buggy time
    # base (minutes*60+seconds, which resets every hour) would NOT keep the
    # two positions one second apart here.
    buggy_before = ((59 * 60 + 59) - offset) % base_cycle
    buggy_after = ((0 * 60 + 0) - offset) % base_cycle
    assert buggy_after != (buggy_before + 1) % base_cycle
