"""Regression checks for ECG calculations, audit integrity, and batch input."""
import csv
import math

import pytest

from agents.base import AuditTrail
from ecg_foundation.cli import main, parse_bool
from ecg_interpretation import (
    calculate_axis_from_leads,
    calculate_qtc_bazett,
    check_bundle_branch_block,
    check_intervals,
    check_st_elevation,
    get_lead_info,
    interpret_ecg,
)


def test_augmented_leads_are_recognized():
    assert get_lead_info("aVF")["type"] == "augmented"
    assert get_lead_info("AVR")["type"] == "augmented"
    assert get_lead_info(" avl ")["type"] == "augmented"
    result = check_st_elevation({"II": 2.0, "aVF": 2.0})
    assert result["stemi_detected"] is True
    assert any(t["territory"] == "inferior" for t in result["territories"])


def test_no_lbbb_diagnosis_without_specific_morphology():
    assert check_bundle_branch_block(140)["lbbb_criteria_met"] is False
    assert check_bundle_branch_block(110)["diagnosis"] != "Incomplete Left Bundle Branch Block"


def test_heart_rate_does_not_establish_sinus_rhythm():
    result = interpret_ecg(rr_seconds=0.5)
    assert any("Tachycardia" in value for value in result["findings"])
    assert not any("Sinus" in value for value in result["findings"])


@pytest.mark.parametrize("rr", [0, -1, math.nan, math.inf, -math.inf])
def test_invalid_rr_rejected(rr):
    with pytest.raises(ValueError):
        calculate_qtc_bazett(400, rr)
    with pytest.raises(ValueError):
        check_intervals(qt_ms=400, rr_seconds=rr)


def test_zero_qrs_vector_has_undefined_axis():
    with pytest.raises(ValueError):
        calculate_axis_from_leads(0, 0)


def test_hmac_verifies_signature_not_only_chain_links():
    trail = AuditTrail(secret_key="a-test-key")
    trail.log("worker", "tier", "event", {"status": "ok"})
    trail.log("worker", "tier", "event", {"status": "ok"})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "tampered"
    assert trail.verify_integrity(), "Callers must not mutate internal audit entries"
    trail.logs[0]["actor"] = "tampered"
    assert not trail.verify_integrity(), "Signature mismatch must be detected"


def test_bool_parser():
    assert parse_bool("False") is False
    assert parse_bool("true") is True
    assert parse_bool("0") is False
    with pytest.raises(ValueError):
        parse_bool("sometimes")


def test_batch_false_flag_is_not_critical(tmp_path):
    source = tmp_path / "in.csv"
    output = tmp_path / "out.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "A,KEY-1,10,1,False,NOMINAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(source), "-o", str(output)]) == 0
    with output.open(newline="", encoding="utf-8") as f:
        row = list(csv.DictReader(f))[0]
    assert row["critical_count"] == "0"
    assert row["overall_status"] == "NOMINAL_OPTIMAL"


def test_batch_rejects_ambiguous_boolean(tmp_path):
    source = tmp_path / "in.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "A,KEY-1,10,1,nope,NOMINAL\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="row 2"):
        main(["batch", "-i", str(source), "-o", str(tmp_path / "out.csv")])


def test_prod_requires_audit_secret(monkeypatch):
    monkeypatch.setenv("ECG_ENV", "production")
    monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
        AuditTrail()


def test_nonadjacent_anterior_leads_do_not_meet_screen():
    result = check_st_elevation({"V1": 3.0, "V4": 3.0})
    assert result["stemi_detected"] is False


def test_no_posterior_or_rv_diagnosis_from_v1_v2_elevation():
    result = check_st_elevation({"V1": 3.0, "V2": 3.0})
    labels = {territory["territory"] for territory in result["territories"]}
    assert labels == {"anterior"}
