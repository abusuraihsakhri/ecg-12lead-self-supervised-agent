#!/usr/bin/env python3
"""
Tests for 12-Lead ECG Interpretation Helper.
"""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ecg_interpretation import (
    ALL_LEADS,
    LEAD_INFO,
    STEMI_TERRITORIES,
    BBB_CRITERIA,
    NORMAL_INTERVALS,
    calculate_qtc_bazett,
    calculate_qtc_fridericia,
    calculate_qtc_framingham,
    hr_from_rr,
    rr_from_hr,
    calculate_axis_from_leads,
    classify_axis,
    check_intervals,
    check_st_elevation,
    check_bundle_branch_block,
    interpret_ecg,
    get_lead_info,
    get_all_lead_info,
    get_stemi_territory,
)


# =============================================================================
# Lead Info Tests
# =============================================================================

def test_all_12_leads_defined():
    """All 12 standard leads must be defined."""
    expected = {"I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"}
    assert set(ALL_LEADS) == expected
    assert len(ALL_LEADS) == 12


def test_lead_info_contains_required_fields():
    """Each lead must have type, axis_degrees, views, coronary_territory."""
    for lead in ALL_LEADS:
        info = LEAD_INFO[lead]
        assert "type" in info
        assert "axis_degrees" in info
        assert "views" in info
        assert "coronary_territory" in info


def test_lead_types():
    """Verify lead type classification."""
    assert LEAD_INFO["I"]["type"] == "limb"
    assert LEAD_INFO["II"]["type"] == "limb"
    assert LEAD_INFO["III"]["type"] == "limb"
    assert LEAD_INFO["aVR"]["type"] == "augmented"
    assert LEAD_INFO["aVL"]["type"] == "augmented"
    assert LEAD_INFO["aVF"]["type"] == "augmented"
    assert LEAD_INFO["V1"]["type"] == "precordial"
    assert LEAD_INFO["V6"]["type"] == "precordial"


def test_get_lead_info_valid():
    """get_lead_info returns correct data for valid lead."""
    info = get_lead_info("V1")
    assert info["type"] == "precordial"
    assert "right sternal border" in info["placement"]


def test_get_lead_info_invalid():
    """get_lead_info raises ValueError for unknown lead."""
    try:
        get_lead_info("V7")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_get_all_lead_info():
    """get_all_lead_info returns all 12 leads."""
    info = get_all_lead_info()
    assert len(info) == 12
    assert "I" in info
    assert "V6" in info


# =============================================================================
# Heart Rate / RR Conversion Tests
# =============================================================================

def test_hr_from_rr_normal():
    """RR of 1.0s = 60 bpm."""
    assert hr_from_rr(1.0) == 60.0


def test_hr_from_rr_tachycardia():
    """RR of 0.5s = 120 bpm."""
    assert hr_from_rr(0.5) == 120.0


def test_hr_from_rr_bradycardia():
    """RR of 1.5s = 40 bpm."""
    assert abs(hr_from_rr(1.5) - 40.0) < 0.01


def test_rr_from_hr():
    """75 bpm -> 0.8s RR."""
    assert abs(rr_from_hr(75) - 0.8) < 0.001


def test_hr_rr_roundtrip():
    """hr_from_rr and rr_from_hr are inverse operations."""
    for hr in [50, 60, 75, 100, 120, 150]:
        rr = rr_from_hr(hr)
        assert abs(hr_from_rr(rr) - hr) < 0.01


def test_hr_from_rr_invalid():
    """Zero or negative RR should raise ValueError."""
    try:
        hr_from_rr(0)
        assert False
    except ValueError:
        pass


# =============================================================================
# QTc Calculation Tests
# =============================================================================

def test_qtc_bazett_normal():
    """QT 400ms, RR 1.0s -> QTc 400ms."""
    assert abs(calculate_qtc_bazett(400, 1.0) - 400.0) < 0.1


def test_qtc_bazett_tachycardia():
    """QT 350ms, RR 0.6s -> QTc ~452ms."""
    expected = 350.0 / math.sqrt(0.6)
    assert abs(calculate_qtc_bazett(350, 0.6) - expected) < 0.1


def test_qtc_bazett_bradycardia():
    """QT 440ms, RR 1.44s -> QTc ~367ms."""
    expected = 440.0 / math.sqrt(1.44)
    assert abs(calculate_qtc_bazett(440, 1.44) - expected) < 0.1


def test_qtc_fridericia():
    """QT 400ms, RR 1.0s -> QTc 400ms."""
    assert abs(calculate_qtc_fridericia(400, 1.0) - 400.0) < 0.1


def test_qtc_framingham():
    """QT 400ms, RR 1.0s -> QTc 400ms."""
    assert abs(calculate_qtc_framingham(400, 1.0) - 400.0) < 0.1


def test_qtc_bazett_invalid_rr():
    """Zero RR should raise ValueError."""
    try:
        calculate_qtc_bazett(400, 0)
        assert False
    except ValueError:
        pass


# =============================================================================
# Axis Calculation Tests
# =============================================================================

def test_axis_normal():
    """Lead I positive, aVF positive -> normal axis (~37 degrees)."""
    axis = calculate_axis_from_leads(8, 6)
    assert 30 < axis < 45  # approximately 36.9 degrees


def test_axis_left_deviation():
    """Lead I positive, aVF negative -> left axis deviation."""
    axis = calculate_axis_from_leads(8, -6)
    assert -50 < axis < -30


def test_axis_right_deviation():
    """Lead I negative, aVF positive -> right axis deviation."""
    axis = calculate_axis_from_leads(-3, 10)
    assert 100 < axis < 120


def test_axis_extreme():
    """Lead I negative, aVF negative -> extreme axis."""
    axis = calculate_axis_from_leads(-5, -5)
    assert axis < -100 or axis > 150  # northwest


def test_classify_axis_normal():
    result = classify_axis(45)
    assert result["classification"] == "Normal axis"


def test_classify_axis_lad():
    result = classify_axis(-60)
    assert "Left axis deviation" in result["classification"]


def test_classify_axis_rad():
    result = classify_axis(120)
    assert "Right axis deviation" in result["classification"]


def test_classify_axis_extreme():
    result = classify_axis(-135)
    assert "Extreme" in result["classification"]


# =============================================================================
# Interval Checking Tests
# =============================================================================

def test_intervals_all_normal():
    result = check_intervals(pr_ms=160, qrs_ms=90, qt_ms=400, rr_seconds=1.0, sex="male")
    assert len(result["abnormalities"]) == 0


def test_intervals_prolonged_pr():
    result = check_intervals(pr_ms=240)
    assert len(result["abnormalities"]) == 1
    assert "PR" in result["abnormalities"][0]["interval"]
    assert "first-degree" in result["abnormalities"][0]["finding"].lower()


def test_intervals_short_pr():
    result = check_intervals(pr_ms=100)
    assert len(result["abnormalities"]) == 1
    assert "Short" in result["abnormalities"][0]["finding"]


def test_intervals_wide_qrs():
    result = check_intervals(qrs_ms=140)
    assert len(result["abnormalities"]) == 1
    assert "Wide" in result["abnormalities"][0]["finding"]


def test_intervals_prolonged_qt_male():
    result = check_intervals(qt_ms=460, sex="male")
    assert len(result["abnormalities"]) == 1
    assert "QT" in result["abnormalities"][0]["interval"]


def test_intervals_normal_qt_female():
    result = check_intervals(qt_ms=450, sex="female")
    assert len(result["abnormalities"]) == 0


def test_intervals_prolonged_qt_female():
    result = check_intervals(qt_ms=470, sex="female")
    assert len(result["abnormalities"]) == 1


def test_intervals_qtc_high_risk():
    """QTc >500ms should trigger high risk warning."""
    result = check_intervals(qt_ms=500, rr_seconds=0.8, sex="male")
    qtc_abnormalities = [a for a in result["abnormalities"] if a["interval"] == "QTc"]
    assert len(qtc_abnormalities) >= 1
    assert "500" in qtc_abnormalities[0]["finding"] or "HIGH" in qtc_abnormalities[0]["finding"].upper()


def test_intervals_invalid_sex():
    try:
        check_intervals(sex="unknown")
        assert False
    except ValueError:
        pass


# =============================================================================
# STEMI Detection Tests
# =============================================================================

def test_stemi_inferior():
    """ST elevation in II, III, aVF -> inferior STEMI."""
    result = check_st_elevation({"II": 3.0, "III": 2.5, "aVF": 2.0})
    assert result["stemi_detected"] is True
    territory_names = [t["territory"] for t in result["territories"]]
    assert "inferior" in territory_names


def test_stemi_anterior():
    """ST elevation in V1-V4 -> anterior STEMI."""
    result = check_st_elevation({"V1": 3.0, "V2": 4.0, "V3": 3.5, "V4": 2.5})
    assert result["stemi_detected"] is True
    territory_names = [t["territory"] for t in result["territories"]]
    assert "anterior" in territory_names


def test_stemi_lateral():
    """ST elevation in I, aVL, V5, V6 -> lateral STEMI."""
    result = check_st_elevation({"I": 2.0, "aVL": 2.5, "V5": 1.5, "V6": 1.5})
    assert result["stemi_detected"] is True
    territory_names = [t["territory"] for t in result["territories"]]
    assert "lateral" in territory_names


def test_stemi_not_met_single_lead():
    """Single lead ST elevation should not meet STEMI criteria."""
    result = check_st_elevation({"II": 3.0})
    assert result["stemi_detected"] is False


def test_stemi_not_met_below_threshold():
    """ST elevation below threshold should not trigger."""
    result = check_st_elevation({"II": 0.5, "III": 0.5})
    assert result["stemi_detected"] is False


def test_stemi_v1_v3_higher_threshold():
    """V1-V3 require >=2mm for STEMI."""
    result = check_st_elevation({"V1": 1.5, "V2": 1.5})
    assert result["stemi_detected"] is False  # below 2mm threshold

    result2 = check_st_elevation({"V1": 2.5, "V2": 3.0})
    assert result2["stemi_detected"] is True


def test_stemi_cath_lab_action():
    """STEMI detection should recommend cath lab activation."""
    result = check_st_elevation({"II": 3.0, "III": 2.5, "aVF": 2.0})
    assert "cath" in result["clinical_action"].lower() or "PCI" in result["clinical_action"]


def test_stemi_territory_artery():
    """Inferior STEMI should identify RCA."""
    result = check_st_elevation({"II": 3.0, "III": 2.5, "aVF": 2.0})
    inferior = [t for t in result["territories"] if t["territory"] == "inferior"][0]
    assert "coronary" in inferior["artery"].lower()


def test_get_stemi_territory():
    """get_stemi_territory returns correct data."""
    info = get_stemi_territory("inferior")
    assert "II" in info["leads"]
    assert "RCA" in info["artery"]


# =============================================================================
# Bundle Branch Block Tests
# =============================================================================

def test_bbb_normal_qrs():
    """Normal QRS duration should not indicate BBB."""
    result = check_bundle_branch_block(qrs_ms=90)
    assert result["rbbb_criteria_met"] is False
    assert result["lbbb_criteria_met"] is False
    assert "Normal" in result["diagnosis"]


def test_bbb_rbbb():
    """QRS >=120 with RSR' in V1 and wide S in I -> RBBB."""
    result = check_bundle_branch_block(
        qrs_ms=140, lead_v1_pattern="rsr", lead_i_pattern="wideS"
    )
    assert result["rbbb_criteria_met"] is True
    assert "RBBB" in result["diagnosis"]


def test_bbb_lbbb():
    """QRS >=120 with broad notched R in I, no Q in I/V5-V6 -> LBBB."""
    result = check_bundle_branch_block(
        qrs_ms=150, lead_i_pattern="broadNotchedR",
        has_q_in_v5_v6=False, has_q_in_i=False,
    )
    assert result["lbbb_criteria_met"] is True
    assert "LBBB" in result["diagnosis"]


def test_bbb_incomplete_rbbb():
    """QRS 100-120 with RSR' in V1 -> incomplete RBBB."""
    result = check_bundle_branch_block(qrs_ms=110, lead_v1_pattern="rsr")
    assert "Incomplete" in result["diagnosis"]
    assert "Right" in result["diagnosis"]


def test_bbb_lbbb_no_q_waves():
    """LBBB with Q waves in V5-V6 should have fewer criteria met."""
    result_with_q = check_bundle_branch_block(
        qrs_ms=140, lead_i_pattern="broadNotchedR",
        has_q_in_v5_v6=True, has_q_in_i=False,
    )
    result_without_q = check_bundle_branch_block(
        qrs_ms=140, lead_i_pattern="broadNotchedR",
        has_q_in_v5_v6=False, has_q_in_i=False,
    )
    # Without Q waves, more LBBB criteria are met
    assert len(result_without_q["criteria_details"]) >= len(result_with_q["criteria_details"])


def test_bbb_qrs_threshold():
    """QRS exactly at 120ms should be considered for BBB."""
    result = check_bundle_branch_block(qrs_ms=120, lead_v1_pattern="rsr", lead_i_pattern="wideS")
    assert result["qrs_widened"] is True
    assert result["rbbb_criteria_met"] is True


# =============================================================================
# Comprehensive Interpretation Tests
# =============================================================================

def test_interpret_normal():
    """Normal ECG should have no significant findings."""
    result = interpret_ecg(
        lead_i_amplitude=5, lead_avf_amplitude=8,
        pr_ms=160, qrs_ms=90, qt_ms=380, rr_seconds=0.85, sex="male",
    )
    assert "analysis" in result
    assert "findings" in result
    assert len(result["warnings"]) == 0


def test_interpret_with_stemi():
    """STEMI should generate warnings."""
    result = interpret_ecg(
        st_elevations={"II": 3.0, "III": 2.5, "aVF": 2.0},
        qrs_ms=90,
    )
    assert len(result["warnings"]) > 0
    assert any("STEMI" in w for w in result["warnings"])


def test_interpret_with_bbb():
    """BBB should appear in findings."""
    result = interpret_ecg(
        qrs_ms=140, lead_v1_pattern="rsr", lead_i_pattern="wideS",
    )
    assert any("RBBB" in f for f in result["findings"])


def test_interpret_summary():
    """Summary should be a non-empty string."""
    result = interpret_ecg(pr_ms=160, qrs_ms=90)
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


# =============================================================================
# CLI Tests
# =============================================================================

def test_cli_intervals():
    from cli import main
    rc = main(["intervals", "--pr", "160", "--qrs", "90", "--qt", "400", "--rr", "1.0", "--sex", "male"])
    assert rc == 0


def test_cli_axis():
    from cli import main
    rc = main(["axis", "--lead-i", "8", "--lead-avf", "6"])
    assert rc == 0


def test_cli_stemi():
    from cli import main
    rc = main(["stemi", "--st-elevations", "II:3", "III:2.5", "aVF:2"])
    assert rc == 0


def test_cli_bbb():
    from cli import main
    rc = main(["bbb", "--qrs", "140", "--v1-pattern", "rsr", "--i-pattern", "wideS"])
    assert rc == 0


def test_cli_qtc():
    from cli import main
    rc = main(["qtc", "--qt", "420", "--hr", "75"])
    assert rc == 0


def test_cli_leads():
    from cli import main
    rc = main(["leads"])
    assert rc == 0


def test_cli_interpret():
    from cli import main
    rc = main(["interpret", "--pr", "160", "--qrs", "90", "--qt", "390", "--rr", "0.8", "--sex", "male"])
    assert rc == 0
