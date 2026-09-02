# ECG 12lead Self Supervised Agent

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

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

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_qtc_bazett()`**: Calculate QTc using Bazett's formula.

QTc = QT / sqrt(RR)

Args:
    qt_ms: QT interval in milliseconds
    rr_seconds: RR interval in seconds

Returns:
    QTc in milliseconds
- **`calculate_qtc_fridericia()`**: Calculate QTc using Fridericia's formula (more accurate at extreme HRs).

QTc = QT / (RR)^(1/3)

Args:
    qt_ms: QT interval in milliseconds
    rr_seconds: RR interval in seconds

Returns:
    QTc in milliseconds
- **`calculate_qtc_framingham()`**: Calculate QTc using Framingham (Sagie) formula.

QTc = QT + 154 * (1 - RR)

Args:
    qt_ms: QT interval in milliseconds
    rr_seconds: RR interval in seconds

Returns:
    QTc in milliseconds
- **`hr_from_rr()`**: Convert RR interval in seconds to heart rate in bpm.
- **`rr_from_hr()`**: Convert heart rate in bpm to RR interval in seconds.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate QTc using Bazett's formula.
  Calculate QTc using Fridericia's formula (more accurate at extreme HRs).
  Calculate QTc using Framingham (Sagie) formula.
  Calculate the frontal plane QRS axis using leads I and aVF.
  qtc_bazett = calculate_qtc_bazett(qt_ms, rr_seconds)
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --rr <value> --hr <value> --json <value> --pr <value>
```

### Parameter Reference
- `--rr`: Specifies input measurement or parameter value.
- `--hr`: Specifies input measurement or parameter value.
- `--json`: Specifies input measurement or parameter value.
- `--pr`: Specifies input measurement or parameter value.
- `--qrs`: Specifies input measurement or parameter value.
- `--qt`: Specifies input measurement or parameter value.
- `--sex`: Specifies input measurement or parameter value.
- `--lead-i`: Specifies input measurement or parameter value.
- `--lead-avf`: Specifies input measurement or parameter value.
- `--st-elevations`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Parameter / observation metric | Required |
| `secondary_metric` | Parameter / observation metric | Required |
| `is_critical_flag` | Parameter / observation metric | Required |
| `status_descriptor` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t ecg-12lead-self-supervised-agent .
docker run -p 8000:8000 ecg-12lead-self-supervised-agent
```
