# ECG 12-Lead Self-Supervised Agent

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics
> **Reference Guidelines & Standards:** AHA/ACC Practice Guidelines & ESC Clinical Standards

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

A comprehensive 12-Lead ECG Interpretation Helper with enterprise-grade security features:

- **ECG Interval Analysis**: PR, QRS, QT/QTc interval checking against normal ranges
- **Axis Calculation**: Frontal plane QRS axis from leads I and aVF
- **STEMI Detection**: ST elevation criteria with territory localization
- **Bundle Branch Block**: RBBB and LBBB criteria evaluation
- **Lead Placement Info**: Anatomical and placement data for all 12 leads
- **Zero-PHI Guard**: AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **HMAC-SHA256 Audit Trail**: Cryptographic tamper-evident logging
- **Multi-Agent Architecture**: Distributed component coordination with specialized workers

References:
- AHA/ACC/HRS Guidelines for ECG Interpretation
- Wagner GS. Marriott's Practical Electrocardiography. 12th ed.
- Surawicz B, Knilans TK. Chou's Electrocardiography in Clinical Practice. 6th ed.

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 ECG Interpretation Functions

- **`calculate_qtc_bazett(qt_ms, rr_seconds)`**: QTc using Bazett's formula: QTc = QT / sqrt(RR)
- **`calculate_qtc_fridericia(qt_ms, rr_seconds)`**: QTc using Fridericia's formula: QTc = QT / (RR)^(1/3)
- **`calculate_qtc_framingham(qt_ms, rr_seconds)`**: QTc using Framingham formula: QTc = QT + 154 * (1 - RR)
- **`hr_from_rr(rr_seconds)`**: Convert RR interval to heart rate
- **`rr_from_hr(hr_bpm)`**: Convert heart rate to RR interval
- **`calculate_axis_from_leads(lead_i, lead_avf)`**: Calculate frontal plane QRS axis
- **`classify_axis(axis_degrees)`**: Classify axis as normal, LAD, RAD, or extreme
- **`check_intervals(...)`**: Comprehensive interval analysis
- **`check_st_elevation(elevations)`**: STEMI criteria evaluation
- **`check_bundle_branch_block(...)`**: BBB pattern recognition
- **`interpret_ecg(...)`**: Comprehensive ECG interpretation

### 🔐 Security & Enterprise Features

- **Zero-PHI Outbound Interceptor**: Blocks SSNs, MRNs, phone numbers, emails, DOBs, and patient names
- **HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs
- **Multi-Agent Workers**: InvariantQC, SafetyEscalation, ProtocolConformance workers
- **FastAPI REST API**: OpenAPI 3.1 endpoints with Prometheus metrics

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/ecg-12lead-self-supervised-agent.git
cd ecg-12lead-self-supervised-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set audit secret key (recommended for production)
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

---

## 🖥️ CLI Usage

### ECG Interpretation CLI

```bash
# Show all 12-lead placement info
python cli.py leads

# Check ECG intervals
python cli.py intervals --pr 160 --qrs 90 --qt 400 --rr 1.0 --sex male

# Calculate QRS axis
python cli.py axis --lead-i 8 --lead-avf 6

# Check for STEMI
python cli.py stemi --st-elevations II:3 III:2.5 aVF:2

# Evaluate bundle branch block
python cli.py bbb --qrs 140 --v1-pattern rsr --i-pattern wideS

# Calculate QTc
python cli.py qtc --qt 420 --hr 75

# Comprehensive interpretation
python cli.py interpret --pr 160 --qrs 90 --qt 390 --rr 0.8 --sex male

# Output JSON (add --json to any command)
python cli.py intervals --pr 240 --json
```

### Agent System CLI

```bash
# Run task audit
python ecg_foundation_app.py audit --task-id TASK-001

# Query supervisory chat
python ecg_foundation_app.py chat "What is the system status?"

# Verify audit trail integrity
python ecg_foundation_app.py verify-audit

# Batch process CSV
python ecg_foundation_app.py batch -i sample.csv -o results.csv

# Launch REST server
python ecg_foundation_app.py serve --host 0.0.0.0 --port 8000
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run specific test modules
pytest tests/test_ecg_interpretation.py -v
pytest tests/test_ecg_foundation.py -v
pytest tests/test_ecg_12lead_self_supervised_agent.py -v
pytest tests/test_enrichment.py -v
```

**Test Coverage:**
- 69 tests covering ECG calculations, axis classification, STEMI detection, BBB evaluation
- Security tests for PHI guard enforcement
- Audit trail integrity verification
- CLI command validation
- Enrichment suite execution

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
AUDIT_SECRET_KEY="your-secure-key" docker-compose up --build

# Or build manually
docker build -t ecg-12lead-self-supervised-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secure-key" ecg-12lead-self-supervised-agent
```

---

## 🔌 REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and system status |
| `/metrics` | GET | Prometheus operational metrics |
| `/api/audit` | POST | Dispatch task for multi-worker evaluation |
| `/api/chat` | POST | Air-gapped supervisory chat |
| `/api/audit/logs` | GET | Retrieve and verify HMAC audit trail |

---

## 🛡️ Security Considerations

1. **Set AUDIT_SECRET_KEY**: Always set a strong, random `AUDIT_SECRET_KEY` environment variable in production
2. **PHI Guard**: The system actively blocks outbound PHI (SSNs, MRNs, phone numbers, emails, patient names)
3. **Audit Trail**: All operations are logged with HMAC-SHA256 chained signatures
4. **No External Dependencies**: Core ECG calculations use only Python standard library

---

## 📁 Project Structure

```
ecg-12lead-self-supervised-agent/
├── agents/                  # Multi-agent system (supervisor, workers, security)
│   ├── base.py             # PHI Guard, Audit Trail, Security
│   ├── models.py           # Pydantic schemas
│   ├── workers.py          # Specialized domain workers
│   ├── supervisor.py       # Master coordinator
│   ├── api.py              # FastAPI server
│   └── ...
├── ecg_foundation/         # ECG foundation engine
│   ├── models.py           # Data models
│   ├── engine.py           # Core algorithms
│   ├── agents.py           # Sub-agents
│   ├── cli.py              # CLI interface
│   └── server.py           # REST server
├── tests/                  # Test suite
├── ecg_interpretation.py   # Core ECG calculations
├── cli.py                  # Main CLI entry point
├── enrichment.py           # Enrichment features
├── simulator.py            # Load testing simulator
├── web/index.html          # Operations console UI
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
