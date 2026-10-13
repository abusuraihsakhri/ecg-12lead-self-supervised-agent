"""
FastAPI REST API Server for Ecg 12Lead Self Supervised Agent.
"""
from typing import Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ecg 12Lead Self Supervised Agent API",
    description="Demonstration threshold audit and ECG reference console; no waveform self-supervision or clinical decision engine",
    version="3.0.0-ENTERPRISE",
)


@app.exception_handler(SecurityException)
def blocked_phi(request: Request, exc: SecurityException):
    return JSONResponse(status_code=422, content={"detail": "Input contains a potentially sensitive identifier; use synthetic or de-identified data."})


@app.get("/", include_in_schema=False)
def interface():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "ecg-12lead-self-supervised-agent", "domain": "Cardiology & Intensive Care Systems", "standard": "Demonstration rules only", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "AVAILABLE" if AuditLogger.verify_integrity() else "AUDIT_INTEGRITY_FAILURE"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid query")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
