#!/usr/bin/env python3
"""
12-Lead ECG Interpretation Helper

Real clinical calculations for ECG interpretation including:
- Lead placement and axis for all 12 leads
- Normal interval checking (PR, QRS, QT/QTc)
- ST elevation criteria (STEMI)
- STEMI territory localization
- Bundle branch block criteria (RBBB, LBBB)
- Axis calculation from leads I and aVF

References:
- AHA/ACC/HRS Guidelines for ECG Interpretation
- Wagner GS. Marriott's Practical Electrocardiography. 12th ed.
- Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice. 6th ed.

Author: Medical Calculator Project
License: MIT
"""

import math
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# LEAD PLACEMENT AND ANATOMICAL INFORMATION
# =============================================================================

LEAD_INFO = {
    "I": {
        "type": "limb",
        "positive_electrode": "Left arm (LA)",
        "negative_electrode": "Right arm (RA)",
        "axis_degrees": 0,
        "views": "Lateral wall of left ventricle",
        "coronary_territory": "LCx (left circumflex)",
    },
    "II": {
        "type": "limb",
        "positive_electrode": "Left leg (LL)",
        "negative_electrode": "Right arm (RA)",
        "axis_degrees": 60,
        "views": "Inferior wall of left ventricle",
        "coronary_territory": "RCA (right coronary artery)",
    },
    "III": {
        "type": "limb",
        "positive_electrode": "Left leg (LL)",
        "negative_electrode": "Left arm (LA)",
        "axis_degrees": 120,
        "views": "Inferior wall of left ventricle",
        "coronary_territory": "RCA (right coronary artery)",
    },
    "aVR": {
        "type": "augmented",
        "positive_electrode": "Right arm (RA)",
        "negative_electrode": "LA + LL",
        "axis_degrees": -150,
        "views": "Cavity of right ventricle / high lateral",
        "coronary_territory": "N/A (reciprocal)",
    },
    "aVL": {
        "type": "augmented",
        "positive_electrode": "Left arm (LA)",
        "negative_electrode": "RA + LL",
        "axis_degrees": -30,
        "views": "High lateral wall of left ventricle",
        "coronary_territory": "LCx (left circumflex)",
    },
    "aVF": {
        "type": "augmented",
        "positive_electrode": "Left leg (LL)",
        "negative_electrode": "RA + LA",
        "axis_degrees": 90,
        "views": "Inferior wall of left ventricle",
        "coronary_territory": "RCA (right coronary artery)",
    },
    "V1": {
        "type": "precordial",
        "placement": "4th intercostal space, right sternal border",
        "axis_degrees": 110,
        "views": "Right ventricle, interventricular septum",
        "coronary_territory": "RCA (proximal) / LAD (septal branches)",
    },
    "V2": {
        "type": "precordial",
        "placement": "4th intercostal space, left sternal border",
        "axis_degrees": 65,
        "views": "Interventricular septum, anterior wall",
        "coronary_territory": "LAD (left anterior descending)",
    },
    "V3": {
        "type": "precordial",
        "placement": "Midway between V2 and V4",
        "axis_degrees": 45,
        "views": "Anterior wall of left ventricle",
        "coronary_territory": "LAD (left anterior descending)",
    },
    "V4": {
        "type": "precordial",
        "placement": "5th intercostal space, mid-clavicular line",
        "axis_degrees": 30,
        "views": "Anterior-apical wall of left ventricle",
        "coronary_territory": "LAD (left anterior descending)",
    },
    "V5": {
        "type": "precordial",
        "placement": "Anterior axillary line, same level as V4",
        "axis_degrees": -15,
        "views": "Lateral wall of left ventricle",
        "coronary_territory": "LCx (left circumflex)",
    },
    "V6": {
        "type": "precordial",
        "placement": "Mid-axillary line, same level as V4",
        "axis_degrees": -30,
        "views": "Lateral wall of left ventricle",
        "coronary_territory": "LCx (left circumflex)",
    },
}

ALL_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]


def _canonical_lead(lead_name: str) -> str:
    """Return the conventional lead spelling (including aVR/aVL/aVF)."""
    for lead in ALL_LEADS:
        if lead.upper() == str(lead_name).strip().upper():
            return lead
    raise ValueError(f"Unknown ECG lead: {lead_name!r}")



# =============================================================================
# NORMAL INTERVAL RANGES
# =============================================================================

NORMAL_INTERVALS = {
    "pr_interval": {
        "min_ms": 120,
        "max_ms": 200,
        "description": "PR interval (P wave onset to QRS onset)",
        "short_label": "PR",
        "short_description": "<120ms: pre-excitation (WPW) or junctional rhythm",
        "prolonged_description": ">200ms: first-degree AV block",
    },
    "qrs_duration": {
        "min_ms": 80,
        "max_ms": 120,
        "description": "QRS duration (ventricular depolarization)",
        "short_label": "QRS",
        "short_description": "<80ms: consider normal variant",
        "prolonged_description": ">=120ms: bundle branch block or ventricular rhythm",
    },
    "qt_interval": {
        "max_male_ms": 440,
        "max_female_ms": 460,
        "description": "QT interval (ventricular depolarization + repolarization)",
        "short_label": "QT",
        "prolonged_description_male": ">440ms (male): prolonged QT, risk of TdP",
        "prolonged_description_female": ">460ms (female): prolonged QT, risk of TdP",
    },
    "qtc_interval": {
        "max_male_ms": 450,
        "max_female_ms": 460,
        "description": "QTc (Bazett-corrected QT)",
        "short_label": "QTc",
        "prolonged_description_male": ">450ms (male): prolonged QTc",
        "prolonged_description_female": ">460ms (female): prolonged QTc",
        "danger_description": ">500ms: high risk of Torsades de Pointes",
    },
    "hr": {
        "min_bpm": 60,
        "max_bpm": 100,
        "description": "Heart rate",
        "short_label": "HR",
    },
}


# =============================================================================
# STEMI TERRITORY DEFINITIONS
# =============================================================================

STEMI_TERRITORIES = {
    "inferior": {
        "leads": ["II", "III", "aVF"],
        "artery": "RCA (right coronary artery)",
        "artery_full": "Right coronary artery (85%) or dominant LCx (15%)",
        "description": "Inferior STEMI",
        "contiguous_pairs": [("II", "III"), ("II", "aVF"), ("III", "aVF")],
        "associated_findings": [
            "Check right-sided leads (V4R) for RV involvement",
            "Reciprocal ST depression in I, aVL",
            "Risk of bradycardia (SA/AV node from RCA)",
        ],
    },
    "anterior": {
        "leads": ["V1", "V2", "V3", "V4"],
        "artery": "LAD (left anterior descending)",
        "artery_full": "Left anterior descending artery (proximal to mid)",
        "description": "Anterior STEMI",
        "contiguous_pairs": [
            ("V1", "V2"), ("V1", "V3"), ("V1", "V4"),
            ("V2", "V3"), ("V2", "V4"), ("V3", "V4"),
        ],
        "associated_findings": [
            "Reciprocal ST depression in inferior leads (II, III, aVF)",
            "Risk of LV systolic dysfunction and cardiogenic shock",
            "Check for Wellens syndrome if pain resolved",
        ],
    },
    "lateral": {
        "leads": ["I", "aVL", "V5", "V6"],
        "artery": "LCx (left circumflex)",
        "artery_full": "Left circumflex artery or diagonal branch of LAD",
        "description": "Lateral STEMI",
        "contiguous_pairs": [
            ("I", "aVL"), ("I", "V5"), ("I", "V6"),
            ("aVL", "V5"), ("aVL", "V6"), ("V5", "V6"),
        ],
        "associated_findings": [
            "May be subtle; compare with prior ECGs",
            "Reciprocal changes in III, aVF",
            "High lateral: I, aVL; Low lateral: V5, V6",
        ],
    },
    "right_ventricular": {
        "leads": ["V1", "V2", "V3", "V4"],
        "artery": "RCA (proximal)",
        "artery_full": "Proximal right coronary artery (before RV marginal branches)",
        "description": "Right Ventricular STEMI (with inferior STEMI)",
        "contiguous_pairs": [("V1", "V2"), ("V1", "V3"), ("V1", "V4")],
        "associated_findings": [
            "Usually accompanies inferior STEMI",
            "ST elevation V4R >1mm is diagnostic",
            "Avoid nitrates and diuretics (preload dependent)",
            "Kussmaul sign, hypotension, clear lungs",
        ],
    },
    "posterior": {
        "leads": ["V1", "V2"],
        "artery": "RCA or LCx",
        "artery_full": "Right coronary artery or left circumflex artery",
        "description": "Posterior STEMI (mirror image in V1-V2)",
        "contiguous_pairs": [("V1", "V2")],
        "associated_findings": [
            "ST depression in V1-V3 (reciprocal/mirror image)",
            "Tall R waves in V1-V2 (posterior Q waves)",
            "Confirm with posterior leads V7-V9",
            "Often accompanies inferior STEMI",
        ],
    },
}


# =============================================================================
# BUNDLE BRANCH BLOCK CRITERIA
# =============================================================================

BBB_CRITERIA = {
    "RBBB": {
        "name": "Right Bundle Branch Block",
        "qrs_threshold_ms": 120,
        "criteria": [
            "QRS duration >= 120 ms",
            "RSR' (rabbit ear) pattern in V1-V2 (M-shaped QRS)",
            "Wide, slurred S wave in leads I and V6",
            "Secondary ST-T wave changes in V1-V3 (discordant)",
        ],
        "incomplete_qrs_ms": (100, 120),
        "leads_positive": ["V1", "V2"],
        "leads_negative": ["I", "V6"],
        "clinical_significance": [
            "Can be normal variant in young healthy patients",
            "May indicate right ventricular overload/strain",
            "Consider PE, RVH, ASD if new",
            "Does not prevent STEMI diagnosis in V1-V3",
        ],
    },
    "LBBB": {
        "name": "Left Bundle Branch Block",
        "qrs_threshold_ms": 120,
        "criteria": [
            "QRS duration >= 120 ms",
            "Broad, notched or plateau-shaped R wave in I, aVL, V5, V6",
            "Absence of Q waves in leads I, V5, V6",
            "Rabbit ear RSR' in V5-V6 (not V1)",
            "Secondary ST-T wave changes (discordant to QRS)",
            "Delayed intrinsicoid deflection in V5-V6 (>0.07s)",
        ],
        "incomplete_qrs_ms": (110, 120),
        "leads_positive": ["I", "aVL", "V5", "V6"],
        "leads_negative": ["V1", "V2"],
        "clinical_significance": [
            "New LBBB is pathological until proven otherwise",
            "Consider ischemia, cardiomyopathy, aortic stenosis",
            "Sgarbossa criteria needed for STEMI diagnosis in LBBB",
            "Concordant ST changes: ST elevation in positive QRS leads",
            "Discordant ST elevation >25% of preceding S wave depth",
        ],
    },
}

# Sgarbossa criteria for STEMI in LBBB
SGARBOSSA_CRITERIA = {
    "concordant_st_elevation": {
        "points": 5,
        "description": "Concordant ST elevation >=1mm in any lead with positive QRS",
    },
    "concordant_st_depression": {
        "points": 1,
        "description": "Concordant ST depression >=1mm in V1, V2, or V3",
    },
    "discordant_st_elevation": {
        "points": 5,
        "description": "Discordant ST elevation >=5mm (or >=25% of S wave depth per modified Sgarbossa/Smith criteria)",
    },
}


# =============================================================================
# CORE CALCULATION FUNCTIONS
# =============================================================================

def calculate_qtc_bazett(qt_ms: float, rr_seconds: float) -> float:
    """
    Calculate QTc using Bazett's formula.
    
    QTc = QT / sqrt(RR)
    
    Args:
        qt_ms: QT interval in milliseconds
        rr_seconds: RR interval in seconds
    
    Returns:
        QTc in milliseconds
    """
    if not math.isfinite(rr_seconds) or rr_seconds <= 0:
        raise ValueError("RR interval must be finite and positive")
    if not math.isfinite(qt_ms) or qt_ms <= 0:
        raise ValueError("QT interval must be finite and positive")
    return qt_ms / math.sqrt(rr_seconds)


def calculate_qtc_fridericia(qt_ms: float, rr_seconds: float) -> float:
    """
    Calculate QTc using Fridericia's formula (more accurate at extreme HRs).
    
    QTc = QT / (RR)^(1/3)
    
    Args:
        qt_ms: QT interval in milliseconds
        rr_seconds: RR interval in seconds
    
    Returns:
        QTc in milliseconds
    """
    if not math.isfinite(rr_seconds) or rr_seconds <= 0:
        raise ValueError("RR interval must be finite and positive")
    if not math.isfinite(qt_ms) or qt_ms <= 0:
        raise ValueError("QT interval must be finite and positive")
    return qt_ms / (rr_seconds ** (1.0 / 3.0))


def calculate_qtc_framingham(qt_ms: float, rr_seconds: float) -> float:
    """
    Calculate QTc using Framingham (Sagie) formula.
    
    QTc = QT + 154 * (1 - RR)
    
    Args:
        qt_ms: QT interval in milliseconds
        rr_seconds: RR interval in seconds
    
    Returns:
        QTc in milliseconds
    """
    if not math.isfinite(rr_seconds) or rr_seconds <= 0 or not math.isfinite(qt_ms) or qt_ms <= 0:
        raise ValueError("QT and RR intervals must be finite and positive")
    return qt_ms + 154.0 * (1.0 - rr_seconds)


def hr_from_rr(rr_seconds: float) -> float:
    """Convert RR interval in seconds to heart rate in bpm."""
    if not math.isfinite(rr_seconds) or rr_seconds <= 0:
        raise ValueError("RR interval must be finite and positive")
    return 60.0 / rr_seconds


def rr_from_hr(hr_bpm: float) -> float:
    """Convert heart rate in bpm to RR interval in seconds."""
    if not math.isfinite(hr_bpm) or hr_bpm <= 0:
        raise ValueError("Heart rate must be finite and positive")
    return 60.0 / hr_bpm


def calculate_axis_from_leads(lead_i_amplitude: float, lead_avf_amplitude: float) -> float:
    """
    Calculate the frontal plane QRS axis using leads I and aVF.
    
    Uses the arctangent method:
        axis_degrees = atan2(aVF, I) * (180/pi)
    
    Args:
        lead_i_amplitude: Net QRS amplitude in lead I (positive - negative deflection, in mm or mV)
        lead_avf_amplitude: Net QRS amplitude in lead aVF
    
    Returns:
        Frontal plane axis in degrees (-180 to +180)
    """
    if not all(math.isfinite(v) for v in (lead_i_amplitude, lead_avf_amplitude)):
        raise ValueError("Lead amplitudes must be finite")
    if lead_i_amplitude == 0 and lead_avf_amplitude == 0:
        raise ValueError("QRS axis is undefined when both amplitudes are zero")
    axis_rad = math.atan2(lead_avf_amplitude, lead_i_amplitude)
    axis_deg = math.degrees(axis_rad)
    return round(axis_deg, 1)


def classify_axis(axis_degrees: float) -> Dict[str, Any]:
    """
    Classify the frontal plane QRS axis.
    
    Normal: -30 to +90 degrees
    Left axis deviation (LAD): -30 to -90 degrees
    Right axis deviation (RAD): +90 to +180 degrees
    Extreme axis deviation: -90 to -180 degrees (northwest axis)
    
    Args:
        axis_degrees: Frontal plane axis in degrees
    
    Returns:
        Dictionary with axis classification and clinical significance
    """
    if not math.isfinite(axis_degrees):
        raise ValueError("Axis must be finite")
    # Normalize in constant time for arbitrarily large angles.
    axis_degrees = (axis_degrees + 180) % 360 - 180

    if -30 <= axis_degrees <= 90:
        classification = "Normal axis"
        significance = "Normal ventricular depolarization"
    elif -90 < axis_degrees < -30:
        classification = "Left axis deviation (LAD)"
        significance = (
            "Consider: left anterior fascicular block, LVH, inferior MI, "
            "WPW (right-sided accessory pathway), first-degree AV block"
        )
    elif 90 < axis_degrees <= 180:
        classification = "Right axis deviation (RAD)"
        significance = (
            "Consider: right ventricular hypertrophy, PE, COPD, "
            "lateral MI, left posterior fascicular block, ASD"
        )
    else:  # -180 to -90
        classification = "Extreme axis deviation (northwest axis)"
        significance = (
            "Consider: severe RVH, ventricular tachycardia, "
            "WPW (left-sided accessory pathway), artifactual lead reversal"
        )

    return {
        "axis_degrees": round(axis_degrees, 1),
        "classification": classification,
        "clinical_significance": significance,
    }


def check_intervals(
    pr_ms: Optional[float] = None,
    qrs_ms: Optional[float] = None,
    qt_ms: Optional[float] = None,
    rr_seconds: Optional[float] = None,
    sex: str = "male",
) -> Dict[str, Any]:
    """
    Check ECG intervals against normal ranges.
    
    Args:
        pr_ms: PR interval in milliseconds
        qrs_ms: QRS duration in milliseconds
        qt_ms: QT interval in milliseconds
        rr_seconds: RR interval in seconds (needed for QTc calculation)
        sex: "male" or "female" for sex-specific QT/QTc cutoffs
    
    Returns:
        Dictionary with interval analysis results
    """
    sex = sex.lower()
    if sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")

    for name, value in (("PR", pr_ms), ("QRS", qrs_ms), ("QT", qt_ms), ("RR", rr_seconds)):
        if value is not None and (not math.isfinite(value) or value <= 0):
            raise ValueError(f"{name} interval must be finite and positive")

    results = {"abnormalities": [], "intervals": {}}

    # PR interval
    if pr_ms is not None:
        pr_info = {"value_ms": pr_ms, "normal_range": "120-200 ms"}
        if pr_ms < 120:
            pr_info["status"] = "SHORT"
            results["abnormalities"].append({
                "interval": "PR",
                "finding": "Short PR interval",
                "value": f"{pr_ms:.0f} ms",
                "significance": "Consider pre-excitation (WPW syndrome) or junctional rhythm",
            })
        elif pr_ms > 200:
            pr_info["status"] = "PROLONGED"
            results["abnormalities"].append({
                "interval": "PR",
                "finding": "Prolonged PR interval (first-degree AV block)",
                "value": f"{pr_ms:.0f} ms",
                "significance": "Consider AV nodal disease, medications (beta-blockers, CCB, digoxin), vagal tone",
            })
        else:
            pr_info["status"] = "NORMAL"
        results["intervals"]["pr"] = pr_info

    # QRS duration
    if qrs_ms is not None:
        qrs_info = {"value_ms": qrs_ms, "normal_range": "80-120 ms"}
        if qrs_ms < 80:
            qrs_info["status"] = "NORMAL_NARROW"
        elif qrs_ms >= 120:
            qrs_info["status"] = "WIDENED"
            results["abnormalities"].append({
                "interval": "QRS",
                "finding": "Wide QRS complex",
                "value": f"{qrs_ms:.0f} ms",
                "significance": "Consider bundle branch block, ventricular rhythm, hyperkalemia, or paced rhythm",
            })
        else:
            qrs_info["status"] = "NORMAL"
        results["intervals"]["qrs"] = qrs_info

    # QT and QTc
    if qt_ms is not None:
        max_qt = 440 if sex == "male" else 460
        qt_info = {"value_ms": qt_ms, "normal_max_ms": max_qt}
        if qt_ms > max_qt:
            qt_info["status"] = "PROLONGED"
            results["abnormalities"].append({
                "interval": "QT",
                "finding": f"Prolonged QT interval ({sex})",
                "value": f"{qt_ms:.0f} ms (max normal: {max_qt} ms)",
                "significance": "Risk of Torsades de Pointes; check medications, electrolytes (K+, Mg2+, Ca2+)",
            })
        else:
            qt_info["status"] = "NORMAL"
        results["intervals"]["qt"] = qt_info

        # QTc if RR available
        if rr_seconds is not None:
            qtc_bazett = calculate_qtc_bazett(qt_ms, rr_seconds)
            max_qtc = 450 if sex == "male" else 460
            qtc_info = {
                "value_ms": round(qtc_bazett, 1),
                "formula": "Bazett",
                "normal_max_ms": max_qtc,
            }
            if qtc_bazett > 500:
                qtc_info["status"] = "HIGH_RISK"
                results["abnormalities"].append({
                    "interval": "QTc",
                    "finding": "QTc >500 ms - high risk of Torsades de Pointes",
                    "value": f"{qtc_bazett:.1f} ms",
                    "significance": "Urgent: discontinue QT-prolonging drugs, correct electrolytes, consider Mg2+",
                })
            elif qtc_bazett > max_qtc:
                qtc_info["status"] = "PROLONGED"
                results["abnormalities"].append({
                    "interval": "QTc",
                    "finding": f"Prolonged QTc ({sex})",
                    "value": f"{qtc_bazett:.1f} ms (max normal: {max_qtc} ms)",
                    "significance": "Monitor; review QT-prolonging medications and electrolytes",
                })
            else:
                qtc_info["status"] = "NORMAL"
            results["intervals"]["qtc"] = qtc_info

    return results


def check_st_elevation(
    st_elevations: Dict[str, float],
    threshold_standard_mm: float = 1.0,
    threshold_v1_v3_mm: float = 2.0,
) -> Dict[str, Any]:
    """
    Check for ST elevation meeting STEMI criteria.
    
    STEMI Criteria (AHA/ACC):
    - >= 1 mm ST elevation in 2 or more contiguous limb leads
    - >= 2 mm ST elevation in 2 or more contiguous precordial leads (V1-V3)
    - >= 1 mm ST elevation in V4-V6
    
    Args:
        st_elevations: Dictionary mapping lead names to ST elevation in mm
        threshold_standard_mm: Standard threshold (default 1.0 mm)
        threshold_v1_v3_mm: Precordial V1-V3 threshold (default 2.0 mm)
    
    Returns:
        Dictionary with STEMI analysis
    """
    elevated_leads = []
    if not all(math.isfinite(x) and x > 0 for x in (threshold_standard_mm, threshold_v1_v3_mm)):
        raise ValueError("ST elevation thresholds must be finite and positive")
    for lead, elevation in st_elevations.items():
        lead_upper = _canonical_lead(lead)
        if not math.isfinite(elevation):
            raise ValueError(f"ST elevation for {lead} must be finite")
        # Determine threshold
        if lead_upper in ("V1", "V2", "V3"):
            threshold = threshold_v1_v3_mm
        else:
            threshold = threshold_standard_mm
        if elevation >= threshold:
            elevated_leads.append({
                "lead": lead_upper,
                "elevation_mm": elevation,
                "threshold_mm": threshold,
            })

    # Check for contiguous leads
    contiguous_pairs_found = []
    elevated_lead_names = {el["lead"] for el in elevated_leads}

    for territory_name, territory in STEMI_TERRITORIES.items():
        for pair in territory["contiguous_pairs"]:
            if pair[0] in elevated_lead_names and pair[1] in elevated_lead_names:
                contiguous_pairs_found.append({
                    "territory": territory_name,
                    "leads": pair,
                    "artery": territory["artery"],
                    "description": territory["description"],
                })

    # Determine if STEMI criteria met
    stemi_detected = len(contiguous_pairs_found) > 0

    # Identify territories
    territories_involved = []
    seen_territories = set()
    for cp in contiguous_pairs_found:
        t = cp["territory"]
        if t not in seen_territories:
            seen_territories.add(t)
            territories_involved.append({
                "territory": t,
                "description": STEMI_TERRITORIES[t]["description"],
                "artery": STEMI_TERRITORIES[t]["artery_full"],
                "elevated_leads": [l for l in STEMI_TERRITORIES[t]["leads"] if l in elevated_lead_names],
                "associated_findings": STEMI_TERRITORIES[t]["associated_findings"],
            })

    return {
        "stemi_detected": stemi_detected,
        "elevated_leads": elevated_leads,
        "contiguous_pairs": contiguous_pairs_found,
        "territories": territories_involved,
        "num_elevated_leads": len(elevated_leads),
        "clinical_action": (
            "Possible STEMI pattern: urgent clinical assessment; activate cath lab / PCI per local protocol if confirmed"
            if stemi_detected
            else "ST elevation does not meet STEMI criteria by standard thresholds"
        ),
    }


def check_bundle_branch_block(
    qrs_ms: float,
    lead_v1_pattern: Optional[str] = None,
    lead_i_pattern: Optional[str] = None,
    lead_v5_v6_pattern: Optional[str] = None,
    has_q_in_v5_v6: bool = False,
    has_q_in_i: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate for bundle branch block.
    
    Args:
        qrs_ms: QRS duration in milliseconds
        lead_v1_pattern: QRS morphology in V1 ("rsr", "rsR", "broadR", "qS", "other")
        lead_i_pattern: QRS morphology in I ("wideS", "broadNotchedR", "other")
        lead_v5_v6_pattern: QRS morphology in V5/V6 ("wideS", "broadNotchedR", "rsr", "other")
        has_q_in_v5_v6: Whether Q waves present in V5/V6
        has_q_in_i: Whether Q waves present in I
    
    Returns:
        Dictionary with BBB analysis
    """
    if not math.isfinite(qrs_ms) or qrs_ms <= 0:
        raise ValueError("QRS duration must be finite and positive")
    result = {
        "qrs_ms": qrs_ms,
        "qrs_widened": qrs_ms >= 120,
        "incomplete_bbb": 100 <= qrs_ms < 120,
        "rbbb_criteria_met": False,
        "lbbb_criteria_met": False,
        "diagnosis": "Normal QRS conduction",
        "criteria_details": [],
    }

    if qrs_ms < 100:
        result["diagnosis"] = "Normal QRS duration"
        return result

    # RBBB criteria
    rbbb_score = 0
    rbbb_details = []
    if qrs_ms >= 120:
        rbbb_score += 1
        rbbb_details.append("QRS >= 120 ms")
    if lead_v1_pattern in ("rsr", "rsR"):
        rbbb_score += 1
        rbbb_details.append("RSR' pattern in V1-V2")
    if lead_i_pattern == "wideS" or lead_v5_v6_pattern == "wideS":
        rbbb_score += 1
        rbbb_details.append("Wide S wave in I/V6")

    # LBBB criteria
    lbbb_score = 0
    lbbb_details = []
    if qrs_ms >= 120:
        lbbb_score += 1
        lbbb_details.append("QRS >= 120 ms")
    if lead_i_pattern == "broadNotchedR" or lead_v5_v6_pattern == "broadNotchedR":
        lbbb_score += 1
        lbbb_details.append("Broad notched R in I/aVL/V5-V6")
    if not has_q_in_i and not has_q_in_v5_v6:
        lbbb_score += 1
        lbbb_details.append("No Q waves in I/V5-V6")

    if qrs_ms >= 120:
        if rbbb_score >= 2 and lead_v1_pattern in ("rsr", "rsR") and rbbb_score >= lbbb_score:
            result["rbbb_criteria_met"] = True
            result["criteria_details"] = rbbb_details
            result["diagnosis"] = "Right Bundle Branch Block (RBBB)"
            result["clinical_significance"] = BBB_CRITERIA["RBBB"]["clinical_significance"]
        elif lbbb_score >= 2 and (lead_i_pattern == "broadNotchedR" or lead_v5_v6_pattern == "broadNotchedR"):
            result["lbbb_criteria_met"] = True
            result["criteria_details"] = lbbb_details
            result["diagnosis"] = "Left Bundle Branch Block (LBBB)"
            result["clinical_significance"] = BBB_CRITERIA["LBBB"]["clinical_significance"]
        else:
            result["diagnosis"] = "Wide QRS - indeterminate pattern"
            result["criteria_details"] = rbbb_details + lbbb_details
    elif result["incomplete_bbb"]:
        if rbbb_score >= 1:
            result["diagnosis"] = "Incomplete Right Bundle Branch Block"
            result["criteria_details"] = rbbb_details
        elif lead_i_pattern == "broadNotchedR" or lead_v5_v6_pattern == "broadNotchedR":
            result["diagnosis"] = "Incomplete Left Bundle Branch Block"
            result["criteria_details"] = lbbb_details

    return result


def interpret_ecg(
    lead_i_amplitude: Optional[float] = None,
    lead_avf_amplitude: Optional[float] = None,
    pr_ms: Optional[float] = None,
    qrs_ms: Optional[float] = None,
    qt_ms: Optional[float] = None,
    rr_seconds: Optional[float] = None,
    sex: str = "male",
    st_elevations: Optional[Dict[str, float]] = None,
    lead_v1_pattern: Optional[str] = None,
    lead_i_pattern: Optional[str] = None,
    lead_v5_v6_pattern: Optional[str] = None,
    has_q_in_v5_v6: bool = False,
    has_q_in_i: bool = False,
) -> Dict[str, Any]:
    """
    Comprehensive ECG interpretation combining all analysis modules.
    
    Args:
        lead_i_amplitude: Net QRS amplitude in lead I (mm)
        lead_avf_amplitude: Net QRS amplitude in lead aVF (mm)
        pr_ms: PR interval in ms
        qrs_ms: QRS duration in ms
        qt_ms: QT interval in ms
        rr_seconds: RR interval in seconds
        sex: "male" or "female"
        st_elevations: Dict of lead -> ST elevation in mm
        lead_v1_pattern: V1 QRS morphology
        lead_i_pattern: Lead I QRS morphology
        lead_v5_v6_pattern: V5/V6 QRS morphology
        has_q_in_v5_v6: Q waves in V5/V6
        has_q_in_i: Q waves in I
    
    Returns:
        Comprehensive interpretation dictionary
    """
    interpretation = {"findings": [], "warnings": [], "analysis": {}}

    # Heart rate from RR
    if rr_seconds is not None and rr_seconds > 0:
        hr = hr_from_rr(rr_seconds)
        interpretation["analysis"]["heart_rate"] = round(hr, 1)
        interpretation["analysis"]["rr_seconds"] = rr_seconds
        if hr > 100:
            interpretation["findings"].append(f"Tachycardia by RR interval (HR {hr:.0f} bpm; rhythm not established)")
        elif hr < 60:
            interpretation["findings"].append(f"Bradycardia by RR interval (HR {hr:.0f} bpm; rhythm not established)")

    # Axis analysis
    if lead_i_amplitude is not None and lead_avf_amplitude is not None:
        axis_result = classify_axis(calculate_axis_from_leads(lead_i_amplitude, lead_avf_amplitude))
        interpretation["analysis"]["axis"] = axis_result
        if "Normal" not in axis_result["classification"]:
            interpretation["findings"].append(axis_result["classification"])

    # Interval analysis
    interval_result = check_intervals(pr_ms, qrs_ms, qt_ms, rr_seconds, sex)
    interpretation["analysis"]["intervals"] = interval_result["intervals"]
    for abn in interval_result["abnormalities"]:
        interpretation["findings"].append(f"{abn['finding']}: {abn['value']}")
        if "HIGH_RISK" in abn.get("finding", "") or "Urgent" in abn.get("significance", ""):
            interpretation["warnings"].append(abn["significance"])

    # ST elevation / STEMI analysis
    if st_elevations:
        stemi_result = check_st_elevation(st_elevations)
        interpretation["analysis"]["st_elevation"] = stemi_result
        if stemi_result["stemi_detected"]:
            for t in stemi_result["territories"]:
                interpretation["warnings"].append(
                    f"STEMI: {t['description']} - {t['artery']} - leads {', '.join(t['elevated_leads'])}"
                )
            interpretation["findings"].append(stemi_result["clinical_action"])

    # BBB analysis
    if qrs_ms is not None:
        bbb_result = check_bundle_branch_block(
            qrs_ms, lead_v1_pattern, lead_i_pattern, lead_v5_v6_pattern,
            has_q_in_v5_v6, has_q_in_i,
        )
        interpretation["analysis"]["bbb"] = bbb_result
        if bbb_result["diagnosis"] != "Normal QRS conduction" and bbb_result["diagnosis"] != "Normal QRS duration":
            interpretation["findings"].append(bbb_result["diagnosis"])

    interpretation["summary"] = (
        "; ".join(interpretation["findings"]) if interpretation["findings"]
        else "No significant abnormalities detected"
    )

    return interpretation


def get_lead_info(lead_name: str) -> Dict[str, Any]:
    """Get placement and anatomical information for a specific lead."""
    return LEAD_INFO[_canonical_lead(lead_name)]


def get_all_lead_info() -> Dict[str, Dict[str, Any]]:
    """Get placement and anatomical information for all 12 leads."""
    return dict(LEAD_INFO)


def get_stemi_territory(territory_name: str) -> Dict[str, Any]:
    """Get STEMI territory information."""
    key = territory_name.lower().replace(" ", "_")
    if key not in STEMI_TERRITORIES:
        raise ValueError(f"Unknown territory: {territory_name}. Valid: {', '.join(STEMI_TERRITORIES.keys())}")
    return STEMI_TERRITORIES[key]
