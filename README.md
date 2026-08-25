# 12-Lead ECG Interpretation Helper

> **Cardiology - ECG Analysis**  
> Reference Standards: AHA/ACC/HRS Guidelines, Marriott's Practical Electrocardiography

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)

---

## Overview

A real, functional 12-Lead ECG interpretation helper implementing clinical calculations for:

- **Lead placement and axis** for all 12 leads (I, II, III, aVR, aVL, aVF, V1-V6)
- **Interval analysis**: PR (120-200ms), QRS (<120ms), QT/QTc with sex-specific cutoffs
- **STEMI detection**: ST elevation criteria with territory localization (Inferior, Anterior, Lateral, RV, Posterior)
- **Bundle branch block**: RBBB and LBBB criteria with Sgarbossa scoring reference
- **Axis calculation**: Frontal plane axis from leads I and aVF with classification

**No external dependencies** - uses only Python standard library.

---

## Quick Start

```bash
# Check ECG intervals
python cli.py intervals --pr 180 --qrs 90 --qt 400 --rr 0.8 --sex male

# Calculate frontal plane axis
python cli.py axis --lead-i 8 --lead-avf 6

# Check for STEMI
python cli.py stemi --st-elevations II:3 III:2.5 aVF:2

# Evaluate bundle branch block
python cli.py bbb --qrs 140 --v1-pattern rsr --i-pattern wideS

# Calculate QTc
python cli.py qtc --qt 420 --hr 75

# Show all lead placement info
python cli.py leads

# Comprehensive interpretation
python cli.py interpret --pr 160 --qrs 88 --qt 390 --rr 0.75 --lead-i 5 --lead-avf 8 --sex male
```

---

## Python API

```python
from ecg_interpretation import (
    calculate_axis_from_leads,
    classify_axis,
    check_intervals,
    check_st_elevation,
    check_bundle_branch_block,
    calculate_qtc_bazett,
    interpret_ecg,
)

# Axis calculation
axis = calculate_axis_from_leads(lead_i_amplitude=8, lead_avf_amplitude=6)
classification = classify_axis(axis)
# -> {'axis_degrees': 36.9, 'classification': 'Normal axis', ...}

# Interval checking
result = check_intervals(pr_ms=220, qrs_ms=90, qt_ms=400, rr_seconds=0.8, sex="male")
# -> {'abnormalities': [{'interval': 'PR', 'finding': 'Prolonged PR interval', ...}], ...}

# STEMI detection
stemi = check_st_elevation({"II": 3.0, "III": 2.5, "aVF": 2.0})
# -> {'stemi_detected': True, 'territories': [{'territory': 'inferior', 'artery': 'RCA', ...}], ...}

# QTc calculation
qtc = calculate_qtc_bazett(qt_ms=420, rr_seconds=0.8)
# -> 470.2 ms

# Comprehensive interpretation
result = interpret_ecg(
    lead_i_amplitude=5, lead_avf_amplitude=8,
    pr_ms=160, qrs_ms=88, qt_ms=390, rr_seconds=0.75, sex="male"
)
```

---

## Clinical Reference

### Normal Intervals
| Parameter | Normal Range | Significance if Abnormal |
|-----------|-------------|-------------------------|
| PR | 120-200 ms | Short: WPW; Long: 1st degree AV block |
| QRS | 80-120 ms | Wide: BBB, ventricular rhythm |
| QT (male) | <440 ms | Prolonged: TdP risk |
| QT (female) | <460 ms | Prolonged: TdP risk |
| QTc (male) | <450 ms | >500: high TdP risk |
| QTc (female) | <460 ms | >500: high TdP risk |

### STEMI Territory Localization
| Territory | Leads | Artery |
|-----------|-------|--------|
| Inferior | II, III, aVF | RCA |
| Anterior | V1-V4 | LAD |
| Lateral | I, aVL, V5-V6 | LCx |
| RV | V1-V4 + V4R | Proximal RCA |
| Posterior | V7-V9 (mirror V1-V2) | RCA or LCx |

### Axis Classification
| Range | Classification |
|-------|---------------|
| -30 to +90 | Normal |
| -30 to -90 | Left axis deviation |
| +90 to +180 | Right axis deviation |
| -90 to -180 | Extreme (northwest) axis |

---

## Disclaimer

This tool is for **educational and clinical decision support purposes only**. It does not replace professional medical judgment. Always correlate with clinical context and obtain expert consultation for patient care decisions.

## License

MIT License. See [LICENSE](LICENSE) for details.
