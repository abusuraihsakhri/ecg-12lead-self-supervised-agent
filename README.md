# ECG 12-Lead Reference & Audit Tools

### [Open the Live Application →](https://abusuraihsakhri.github.io/ecg-12lead-self-supervised-agent/)

A small browser-based ECG reference calculator, Python ECG measurement utilities, and a separate **demonstration** audit API. Despite the historical repository name, **this code does not implement or train a self-supervised 12-lead waveform model**, produce embeddings, or classify rhythm from raw ECG recordings.

> **Educational and research use only.** This software is not validated for clinical diagnosis, emergency triage, treatment decisions, or patient monitoring. The ST-elevation and bundle-branch-block rules are deliberately simplified and must not be treated as a complete guideline implementation.

## Features

- **Browser, without a server:** QTc by Bazett, Fridericia, and Framingham; heart rate from RR; approximate frontal QRS axis from leads I and aVF. Runs locally in JavaScript without installing Python or transmitting measurement values.
- **Python ECG utilities:** interval screening; lead descriptions; simplified ST-elevation threshold/territory screen; QRS-axis and bundle-branch-block morphology checks; JSON-capable command-line interface.
- **Optional FastAPI demonstration audit:** synthetic task IDs, two arbitrary numeric metrics, a descriptor and a critical flag, evaluated against fixed **non-clinical** thresholds. JSON metrics and HMAC-chained in-memory audit log.
- **Batch CLI:** evaluate a CSV of demonstration audit tasks and export the results.
- **Docker and CI:** Python unit tests, API smoke tests, browser-script syntax checking, container build, and HTTP smoke tests.

The [GitHub Pages application](https://abusuraihsakhri.github.io/ecg-12lead-self-supervised-agent/) supports **only the client-side reference calculators**; its backend-audit form is disabled on static hosting. The same page enables that form when served by the running FastAPI application.

## Usage

Open the live application above for QTc and QRS-axis calculations. No upload is required.

For Python (3.10–3.12 tested):

```bash
git clone https://github.com/abusuraihsakhri/ecg-12lead-self-supervised-agent.git
cd ecg-12lead-self-supervised-agent
python -m pip install -e .

python cli.py qtc --qt 400 --rr 0.8
python cli.py axis --lead-i 8 --lead-avf 6
python cli.py intervals --pr 160 --qrs 90 --qt 400 --rr 1.0
python cli.py stemi --st-elevations II:2 aVF:2
python ecg_foundation_app.py batch -i sample.csv -o results.csv
```

The ST-elevation command is a limited rule-based **screen**, not a diagnostic STEMI classifier. It does not account for all sex/age-specific ST thresholds, reciprocal changes, symptoms, or serial recordings. Its displayed actions must not substitute for clinical judgment.

## Run the API

The operational API and the static reference page can be served together:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ECG_ENV=production
uvicorn agents.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the interface. Available endpoints:

| Route | Purpose |
| --- | --- |
| `GET /` | ECG reference page and optional backend audit |
| `GET /health` | API health JSON |
| `GET /metrics` | In-memory operational counts (JSON, not Prometheus text) |
| `POST /api/audit` | Evaluate a synthetic demonstration task |
| `POST /api/chat` | Deterministic **mock** response; no external language model |
| `GET /api/audit/logs` | In-memory audit entries and HMAC verification |

An additional legacy coordinator CLI is available through `ecg_foundation_app.py`; its fixed-threshold logic is not waveform self-supervision.

For a containerized service, set `AUDIT_SECRET_KEY` as above, then run `docker compose up --build`. Docker requires the key and runs the app as an unprivileged user. The service is not configured for public multi-user hosting or authenticated access.

## Privacy and limitations

The static calculator processes values in your browser, without external fonts, services, tracking, or data uploads. The API is **not** a patient-data system. Submit synthetic/de-identified test inputs only. Its identifier guard detects certain patterns but cannot establish HIPAA compliance, guarantee PHI removal, or detect all identifiers. An audit secret is required in production, and signature verification detects changes to recorded fields, but the audit trail is **in memory only**, lost on restart, and not a durable forensic log. The backend has no user authentication.

## Tests

```bash
python -m pip install -e . pytest httpx2
pytest -q
```

GitHub Actions runs Python 3.10, 3.11, and 3.12, checks browser JavaScript syntax, and smoke-tests the Docker service. The browser UI uses modern JavaScript and is intended for current Chrome, Firefox, Safari, and Edge; full cross-browser testing has not been performed.

## License

MIT. See [LICENSE](LICENSE).
