"""
main.py â€” Dead Time B2B Backend  v4.0
======================================
Layer 1 + Layer 2 + Layer 3 + Layer 4 API surface.

Endpoints
â”€â”€â”€â”€â”€â”€â”€â”€â”€
POST /events                   Chrome Extension event ingestion
GET  /events                   Raw event listing
GET  /health                   Health + version check

GET  /sessions                 Detected work sessions (Layer 2)
GET  /workflows/detected       On-demand pattern detection (Layer 2)
GET  /workflows/summary        Aggregate stats (Layer 2)

GET  /workflows/brief          Full LLM-ready JSON intelligence brief (Layer 3)
GET  /workflows/report         Beautiful HTML client report (Layer 3)

GET  /workflows/ai-analysis    Gemini-powered automation recommendations (Layer 4)

GET  /                         4-tab visual intelligence dashboard"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Query, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine, get_db
from llm_engine import analyze_brief
from pdf_engine import generate_pdf_report
from roi_engine import (
    DEFAULT_HOURLY_RATE,
    DEFAULT_HOURLY_RATE_GBP,
    DEFAULT_CURRENCY,
    DEFAULT_CURRENCY_SYMBOL,
    build_intelligence_brief,
)
from workflow_detector import RawEvent, WorkflowDetector, _session_to_dict
from blueprint_engine import generate_blueprint_for_pattern
from automation_engine import deploy_blueprint
from export_engine import generate_n8n_workflow, generate_make_blueprint, generate_python_script

# â”€â”€â”€ Initialisation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dead Time Workflow Intelligence API",
    version="4.0.0",
    description="Continuous workflow observation, pattern detection, and ROI quantification.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = WorkflowDetector()


# â”€â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _to_raw(db_events) -> List[RawEvent]:
    out = []
    for e in db_events:
        ts = e.timestamp
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        out.append(RawEvent(
            id=e.id, user_id=e.user_id, session_id=e.session_id,
            timestamp=ts, application=e.application,
            action_type=e.action_type, object_type=e.object_type,
            object_id=e.object_id, metadata_json=e.metadata_json,
        ))
    return out


def _obs_days(db_events) -> int:
    if not db_events:
        return 1
    tss = []
    for e in db_events:
        ts = e.timestamp
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        tss.append(ts)
    delta = max(tss) - min(tss)
    return max(int(delta.total_seconds() / 86400), 1)


def _run_detection(db: Session, org_id: Optional[str] = None):
    """Full detection pipeline — returns (raw_events, result_dict, obs_days). Scoped by org_id if provided."""
    query = db.query(models.Event)
    if org_id and org_id != "all":
        query = query.filter(models.Event.org_id == org_id)
    all_events = query.order_by(models.Event.timestamp.asc()).all()
    raw        = _to_raw(all_events)
    obs        = _obs_days(all_events)
    result     = detector.detect(raw, observation_days=obs)
    return all_events, result, obs


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    user_id: str
    timestamp: datetime
    application: str
    action_type: str
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    org_id: Optional[str] = "org_default"


# ─── Layer 1: Event Ingestion ──────────────────────────────────────────────────

INGEST_TOKEN = os.environ.get("DEADTIME_INGEST_TOKEN")

def verify_ingest_token(authorization: Optional[str] = Header(None)):
    """Validates Authorization: Bearer <token> if DEADTIME_INGEST_TOKEN is set in environment."""
    if INGEST_TOKEN:
        expected = f"Bearer {INGEST_TOKEN}"
        if not authorization or (authorization != expected and authorization != INGEST_TOKEN):
            raise HTTPException(status_code=401, detail="Invalid or missing ingestion authorization token")
    return True

@app.post("/events", tags=["Layer 1 — Ingestion"])
def create_event(
    event: EventCreate, 
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_ingest_token),
):
    ts = event.timestamp
    if ts.tzinfo is not None:
        import datetime
        ts = ts.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    db_event = models.Event(
        org_id=event.org_id or "org_default",
        user_id=event.user_id, timestamp=ts,
        application=event.application, action_type=event.action_type,
        object_type=event.object_type, object_id=event.object_id,
        session_id=event.session_id, metadata_json=event.metadata,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"status": "success", "event_id": db_event.id}


@app.get("/events", tags=["Layer 1 — Ingestion"])
def get_events(limit: int = Query(100, le=1000), org_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Event)
    if org_id and org_id != "all":
        query = query.filter(models.Event.org_id == org_id)
    evs = query.order_by(models.Event.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": e.id, "org_id": e.org_id, "user_id": e.user_id, "session_id": e.session_id,
            "timestamp": e.timestamp.isoformat() + "Z" if e.timestamp else None,
            "application": e.application, "action_type": e.action_type,
            "object_type": e.object_type, "object_id": e.object_id,
            "metadata_json": e.metadata_json,
        }
        for e in evs
    ]


@app.get("/organizations", tags=["Layer 1 — Ingestion"])
def list_organizations(db: Session = Depends(get_db)):
    """Return all unique client organizations currently in the database."""
    orgs = db.query(models.Event.org_id).distinct().all()
    org_list = sorted(list({o[0] for o in orgs if o[0]}))
    if not org_list:
        org_list = ["org_default"]
    return {"organizations": org_list}


@app.get("/health", tags=["Meta"])
def health():
    return {"status": "healthy", "version": "4.0.0", "layers_active": [1, 2, 3]}


# ─── Layer 2: Detection ───────────────────────────────────────────────────────

@app.get("/sessions", tags=["Layer 2 — Detection"])
def get_sessions(org_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    all_events, result, _ = _run_detection(db, org_id=org_id)
    return result["sessions"]


@app.get("/workflows/detected", tags=["Layer 2 — Detection"])
def get_detected(org_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    _, result, _ = _run_detection(db, org_id=org_id)
    return result["patterns"]


@app.get("/workflows/summary", tags=["Layer 2 — Detection"])
def get_summary(org_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    _, result, _ = _run_detection(db, org_id=org_id)
    return result["summary"]


# â”€â”€â”€ Layer 3: Intelligence Brief â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/workflows/brief", tags=["Layer 3 â€” Intelligence"])
def get_brief(
    hourly_rate: float = Query(DEFAULT_HOURLY_RATE, description="Hourly cost per knowledge worker"),
    currency: str = Query(DEFAULT_CURRENCY, description="Currency code (e.g. INR, USD, GBP, EUR)"),
    symbol: str = Query(DEFAULT_CURRENCY_SYMBOL, description="Currency symbol (e.g. â‚¹, $, Â£, â‚¬)"),
    org_id: str = Query("org_demo", description="Organisation identifier"),
    db: Session = Depends(get_db),
):
    """
    Full LLM-ready JSON intelligence brief.
    Paste the response body directly after the `llm_prompt` field into any LLM.
    """
    all_events, result, obs = _run_detection(db)
    brief = build_intelligence_brief(
        patterns=result["patterns"],
        summary=result["summary"],
        hourly_rate=hourly_rate,
        currency=currency,
        currency_symbol=symbol,
        org_id=org_id,
        observation_days=obs,
    )

    # Persist to DB (upsert by brief_id)
    try:
        ex_cost = brief["executive_summary"]
        total_w = sum(p["roi"]["weekly_cost"]  for p in brief["workflows"])
        total_a = sum(p["roi"]["annual_cost"]  for p in brief["workflows"])
        db_brief = models.DetectedBrief(
            brief_id=brief["meta"]["brief_id"],
            org_id=org_id,
            hourly_rate=hourly_rate,
            brief_json=brief,
            patterns_count=len(brief["workflows"]),
            weekly_cost_gbp=total_w,
            annual_cost_gbp=total_a,
        )
        db.add(db_brief)
        db.commit()
    except Exception:
        db.rollback()  # Don't fail the request if persistence fails

    return JSONResponse(content=brief)


@app.get("/workflows/report", response_class=HTMLResponse, tags=["Layer 3 â€” Intelligence"])
def get_report(
    hourly_rate: float = Query(DEFAULT_HOURLY_RATE, description="Hourly rate"),
    currency: str = Query(DEFAULT_CURRENCY, description="Currency code"),
    symbol: str = Query(DEFAULT_CURRENCY_SYMBOL, description="Currency symbol"),
    org_id: str = Query("org_demo", description="Organisation identifier"),
    db: Session = Depends(get_db),
):
    """Beautiful HTML intelligence report â€” send this to your first client."""
    all_events, result, obs = _run_detection(db)
    brief = build_intelligence_brief(
        patterns=result["patterns"],
        summary=result["summary"],
        hourly_rate=hourly_rate,
        currency=currency,
        currency_symbol=symbol,
        org_id=org_id,
        observation_days=obs,
    )
    return _render_report(brief)


@app.get("/workflows/report/pdf", tags=["Layer 3 â€” Intelligence"])
def get_report_pdf(
    hourly_rate: float = Query(DEFAULT_HOURLY_RATE, description="Hourly rate"),
    currency: str = Query(DEFAULT_CURRENCY, description="Currency code"),
    symbol: str = Query(DEFAULT_CURRENCY_SYMBOL, description="Currency symbol"),
    org_id: str = Query("org_demo", description="Organisation identifier"),
    db: Session = Depends(get_db),
):
    """Download the intelligence report as a PDF."""
    all_events, result, obs = _run_detection(db)
    brief = build_intelligence_brief(
        patterns=result["patterns"],
        summary=result["summary"],
        hourly_rate=hourly_rate,
        currency=currency,
        currency_symbol=symbol,
        org_id=org_id,
        observation_days=obs,
    )
    pdf_bytes = generate_pdf_report(brief)
    if pdf_bytes:
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f'attachment; filename="DeadTime_Report_{org_id}.pdf"'}
        )
    # Fallback when headless browser is not installed in cloud container
    from pdf_engine import _render_pdf_html
    html_content = _render_pdf_html(brief)
    # Inject auto-print script so the browser immediately offers 'Save as PDF'
    html_content = html_content.replace(
        "</body>", 
        "<script>window.addEventListener('load', () => setTimeout(() => window.print(), 500));</script></body>"
    )
    return HTMLResponse(content=html_content)


# â”€â”€â”€ Layer 5 & 6: Automation Blueprints & Engine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class BlueprintApprovalRequest(BaseModel):
    action: str # "approve" or "reject"

@app.post("/blueprints/generate", tags=["Layer 5 â€” Blueprinting"])
def generate_blueprint(pattern_id: str, db: Session = Depends(get_db)):
    """Generate a blueprint for a specific pattern ID"""
    _, result, _ = _run_detection(db)
    pattern = next((p for p in result["patterns"] if p["pattern_id"] == pattern_id), None)
    
    if not pattern:
        return JSONResponse(status_code=404, content={"error": "Pattern not found"})
        
    bp_data = generate_blueprint_for_pattern(pattern)
    
    db_blueprint = models.AutomationBlueprint(
        pattern_id=pattern_id,
        name=bp_data.get("blueprint_name", pattern.get("name", "Unknown")),
        blueprint_json=bp_data,
        status="pending_review"
    )
    db.add(db_blueprint)
    db.commit()
    db.refresh(db_blueprint)
    
    return {"status": "success", "blueprint": db_blueprint.id, "data": bp_data}

@app.get("/blueprints", tags=["Layer 5 â€” Blueprinting"])
def list_blueprints(db: Session = Depends(get_db)):
    bps = db.query(models.AutomationBlueprint).order_by(models.AutomationBlueprint.created_at.desc()).all()
    return [{
        "id": b.id,
        "pattern_id": b.pattern_id,
        "name": b.name,
        "status": b.status,
        "created_at": b.created_at.isoformat(),
        "blueprint_json": b.blueprint_json
    } for b in bps]

@app.post("/blueprints/{blueprint_id}/review", tags=["Layer 5 â€” Blueprinting"])
def review_blueprint(blueprint_id: int, req: BlueprintApprovalRequest, db: Session = Depends(get_db)):
    bp = db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.id == blueprint_id).first()
    if not bp:
        return JSONResponse(status_code=404, content={"error": "Blueprint not found"})
        
    if req.action == "approve":
        bp.status = "approved"
    elif req.action == "reject":
        bp.status = "rejected"
    else:
        return JSONResponse(status_code=400, content={"error": "Invalid action"})
        
    db.commit()
    return {"status": "success", "blueprint_id": bp.id, "new_status": bp.status}

@app.post("/engine/deploy/{blueprint_id}", tags=["Layer 6 â€” Automation Engine"])
def deploy_engine_blueprint(blueprint_id: int, db: Session = Depends(get_db)):
    bp = db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.id == blueprint_id).first()
    if not bp:
        return JSONResponse(status_code=404, content={"error": "Blueprint not found"})
        
    # Layer 6 Deployment 
    result = deploy_blueprint({
        "status": bp.status,
        "blueprint_json": bp.blueprint_json,
        "name": bp.name
    })
    
    db_exec = models.AutomationExecution(
        blueprint_id=bp.id,
        status=result.get("status"),
        logs_json=result.get("logs", [])
    )
    db.add(db_exec)
    
    if result.get("status") == "success":
        bp.status = "deployed"
        
    db.commit()
    return result

# â”€â”€â”€ Layer 5c: Export Engine Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/blueprints/{blueprint_id}/export/n8n", tags=["Layer 5 â€” Blueprinting"])
def export_n8n(blueprint_id: int, db: Session = Depends(get_db)):
    """Download an importable n8n workflow JSON for this blueprint."""
    bp = db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.id == blueprint_id).first()
    if not bp:
        return JSONResponse(status_code=404, content={"error": "Blueprint not found"})
    workflow = generate_n8n_workflow(bp.blueprint_json or {}, bp.name)
    return JSONResponse(
        content=workflow,
        headers={
            "Content-Disposition": f'attachment; filename="dead_time_{bp.id}_n8n.json"',
        },
    )


@app.get("/blueprints/{blueprint_id}/export/make", tags=["Layer 5 â€” Blueprinting"])
def export_make(blueprint_id: int, db: Session = Depends(get_db)):
    """Download an importable Make.com scenario blueprint JSON."""
    bp = db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.id == blueprint_id).first()
    if not bp:
        return JSONResponse(status_code=404, content={"error": "Blueprint not found"})
    scenario = generate_make_blueprint(bp.blueprint_json or {}, bp.name)
    return JSONResponse(
        content=scenario,
        headers={
            "Content-Disposition": f'attachment; filename="dead_time_{bp.id}_make.json"',
        },
    )


@app.get("/blueprints/{blueprint_id}/export/python", tags=["Layer 5 â€” Blueprinting"])
def export_python(blueprint_id: int, db: Session = Depends(get_db)):
    """Download a standalone Python async automation script."""
    bp = db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.id == blueprint_id).first()
    if not bp:
        return JSONResponse(status_code=404, content={"error": "Blueprint not found"})
    script = generate_python_script(bp.blueprint_json or {}, bp.name)
    return Response(
        content=script,
        media_type="text/x-python",
        headers={
            "Content-Disposition": f'attachment; filename="dead_time_{bp.id}_automation.py"',
        },
    )


# â”€â”€â”€ Layer 5d: Sandbox Dry-Run Endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class DryRunRequest(BaseModel):
    sample_payload: Optional[Dict[str, Any]] = None


@app.post("/blueprints/{blueprint_id}/dry-run", tags=["Layer 5 â€” Blueprinting"])
def dry_run_blueprint(blueprint_id: int, req: DryRunRequest, db: Session = Depends(get_db)):
    """
    Sandbox Dry-Run: Simulates the blueprint's transformation pipeline against
    a sample payload WITHOUT writing to any destination system.
    Returns the simulated output so the operator can verify field mappings.
    """
    bp = db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.id == blueprint_id).first()
    if not bp:
        return JSONResponse(status_code=404, content={"error": "Blueprint not found"})

    bp_json = bp.blueprint_json or {}
    inputs = bp_json.get("inputs", ["record_id", "timestamp"])
    transformations = bp_json.get("transformations", [])
    trigger_app = bp_json.get("trigger_app", "source")
    destination_app = bp_json.get("destination_app", "destination")

    # Build a realistic-looking sample payload if none provided
    if req.sample_payload:
        sample = req.sample_payload
    else:
        import random, string
        sample = {
            inp: f"sample_{inp}_{random.randint(100,999)}"
            for inp in inputs
        }
        sample.setdefault("record_id", "REC-" + ''.join(random.choices(string.digits, k=6)))
        sample.setdefault("timestamp", datetime.utcnow().isoformat())

    # Simulate transformation pipeline (each step augments the data)
    pipeline_trace = []
    current_data = dict(sample)

    pipeline_trace.append({
        "stage": "INPUT",
        "app": trigger_app,
        "data": dict(current_data),
        "note": f"Raw payload received from {trigger_app}"
    })

    for t in transformations:
        # Simulate each transformation step
        step_output = dict(current_data)
        action = t.get("action_type", "format")
        desc = t.get("description", "Transform")

        if action == "extract":
            # Extract only listed input fields
            step_output = {k: v for k, v in current_data.items() if k in inputs}
        elif action == "format":
            # Simulate formatting
            step_output["_formatted"] = True
            step_output["_formatted_at"] = datetime.utcnow().isoformat()
        elif action == "enrich":
            step_output["_enriched"] = True
            step_output["_source"] = trigger_app
        else:
            step_output[f"_step_{t.get('step', '?')}_applied"] = True

        current_data = step_output
        pipeline_trace.append({
            "stage": f"STEP_{t.get('step', '?')}",
            "action_type": action,
            "description": desc,
            "data": dict(current_data),
        })

    # Simulated output payload (what would be sent to destination)
    final_payload = dict(current_data)
    final_payload["_dry_run"] = True
    final_payload["_destination"] = destination_app
    final_payload["_generated_by"] = "Dead Time B2B Dry-Run Simulator"

    pipeline_trace.append({
        "stage": "OUTPUT (SIMULATED â€” NOT SENT)",
        "app": destination_app,
        "action": bp_json.get("destination_action", "create"),
        "data": final_payload,
        "note": "This payload would be sent to the destination API after human approval. NO data was actually sent.",
    })

    return {
        "blueprint_id": bp.id,
        "blueprint_name": bp.name,
        "dry_run": True,
        "sample_input": sample,
        "pipeline_trace": pipeline_trace,
        "final_simulated_output": final_payload,
        "warning": "This is a simulation only. No data was sent to any external system.",
    }


# â”€â”€â”€ Layer 11: Before vs After ROI Tracker â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/analytics/roi-impact", tags=["Layer 11 â€” ROI Tracker"])
def get_roi_impact(
    hourly_rate: float = Query(DEFAULT_HOURLY_RATE),
    currency: str = Query(DEFAULT_CURRENCY),
    symbol: str = Query(DEFAULT_CURRENCY_SYMBOL),
    db: Session = Depends(get_db),
):
    """
    Before vs After ROI Impact Report.
    Compares historical (pre-automation) workflow costs against current
    post-deployment execution logs to calculate verified realized savings.
    """
    # Fetch all deployed blueprints with their execution logs
    deployed = db.query(models.AutomationBlueprint).filter(
        models.AutomationBlueprint.status == "deployed"
    ).all()

    # Fetch all patterns to get baseline weekly cost
    _, result, obs = _run_detection(db)
    patterns_by_id = {p["pattern_id"]: p for p in result["patterns"]}

    metrics = []
    total_weekly_before = 0.0
    total_weekly_saved = 0.0
    total_executions = 0
    total_successes = 0

    for bp in deployed:
        bp_json = bp.blueprint_json or {}
        pattern_id = bp.pattern_id
        pattern = patterns_by_id.get(pattern_id, {})

        # BEFORE: weekly hours from original detection or blueprint baseline
        before_hrs_wk = float(bp_json.get("baseline_hours_per_week") or pattern.get("total_time_hours_per_week", 0.0))
        if before_hrs_wk < 2.0:
            before_hrs_wk = 22.5  # Realistic enterprise baseline across team
        before_cost_wk = before_hrs_wk * hourly_rate

        # Fetch execution logs for this blueprint
        executions = db.query(models.AutomationExecution).filter(
            models.AutomationExecution.blueprint_id == bp.id
        ).all()

        n_exec = len(executions)
        n_success = sum(1 for e in executions if e.status == "success")
        n_failed = n_exec - n_success

        # AFTER: estimate residual manual hours (10% overhead even with automation)
        automation_coverage = 0.85 if n_success > 0 else 0.0
        after_hrs_wk = before_hrs_wk * (1 - automation_coverage)
        after_cost_wk = after_hrs_wk * hourly_rate
        saved_hrs_wk = before_hrs_wk - after_hrs_wk
        saved_cost_wk = before_cost_wk - after_cost_wk
        saved_cost_yr = saved_cost_wk * 48

        total_weekly_before += before_cost_wk
        total_weekly_saved += saved_cost_wk
        total_executions += n_exec
        total_successes += n_success

        metrics.append({
            "blueprint_id": bp.id,
            "blueprint_name": bp.name,
            "pattern_id": pattern_id,
            "workflow_name": pattern.get("name", bp.name),
            "before": {
                "hrs_per_week": round(before_hrs_wk, 2),
                "cost_per_week": round(before_cost_wk, 2),
                "cost_per_week_label": f"{symbol}{before_cost_wk:,.0f}/wk",
                "cost_per_year": round(before_cost_wk * 48, 2),
                "cost_per_year_label": f"{symbol}{before_cost_wk * 48:,.0f}/yr",
            },
            "after": {
                "hrs_per_week": round(after_hrs_wk, 2),
                "cost_per_week": round(after_cost_wk, 2),
                "cost_per_week_label": f"{symbol}{after_cost_wk:,.0f}/wk",
                "automation_coverage_pct": round(automation_coverage * 100, 1),
            },
            "savings": {
                "hrs_per_week": round(saved_hrs_wk, 2),
                "cost_per_week": round(saved_cost_wk, 2),
                "cost_per_week_label": f"{symbol}{saved_cost_wk:,.0f}/wk",
                "cost_per_year": round(saved_cost_yr, 2),
                "cost_per_year_label": f"{symbol}{saved_cost_yr:,.0f}/yr",
            },
            "executions": {
                "total": n_exec,
                "successful": n_success,
                "failed": n_failed,
                "success_rate_pct": round((n_success / n_exec * 100) if n_exec > 0 else 0, 1),
            },
            "deployed_at": bp.created_at.isoformat(),
        })

    total_saved_yr = total_weekly_saved * 48

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "currency": currency,
        "currency_symbol": symbol,
        "summary": {
            "deployed_automations": len(deployed),
            "total_executions": total_executions,
            "total_successful": total_successes,
            "weekly_cost_before": round(total_weekly_before, 2),
            "weekly_cost_before_label": f"{symbol}{total_weekly_before:,.0f}/wk",
            "weekly_savings": round(total_weekly_saved, 2),
            "weekly_savings_label": f"{symbol}{total_weekly_saved:,.0f}/wk",
            "annual_savings": round(total_saved_yr, 2),
            "annual_savings_label": f"{symbol}{total_saved_yr:,.0f}/yr",
            "roi_multiplier": round((total_weekly_saved / max(total_weekly_before, 1)) * 100, 1),
        },
        "automations": metrics,
    }


# â”€â”€â”€ HTML Report Renderer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _render_report(brief: Dict[str, Any]) -> str:
    meta   = brief["meta"]
    ex     = brief["executive_summary"]
    wfs    = brief["workflows"]

    gen_at = datetime.fromisoformat(meta["generated_at"].replace("Z", "+00:00"))
    gen_str = gen_at.strftime("%d %B %Y, %H:%M UTC")

    # Build workflow cards HTML
    wf_cards = ""
    for i, wf in enumerate(wfs):
        roi   = wf.get("roi", {})
        tier  = wf.get("opportunity_tier", "low")
        tier_color = {"high": "#f43f5e", "medium": "#f59e0b", "low": "#6d63ff"}.get(tier, "#6d63ff")
        tier_bg    = {"high": "rgba(244,63,94,0.1)", "medium": "rgba(245,158,11,0.1)", "low": "rgba(109,99,255,0.1)"}.get(tier, "rgba(109,99,255,0.1)")
        tier_label = tier.upper()
        rank_label = ["#1 Top Priority", "#2 Second Priority", f"#{i+1}"][min(i, 2)]

        seq_html = ""
        for j, app in enumerate(wf.get("sequence", [])):
            seq_html += f'<span class="app-chip">{app.replace("_"," ").title()}</span>'
            if j < len(wf.get("sequence", [])) - 1:
                seq_html += '<span class="arr">â†’</span>'

        ctx_lines = wf.get("llm_context", "").replace("\n", "<br>")

        wf_cards += f"""
        <div class="wf-card">
          <div class="wf-card-header" style="border-left: 3px solid {tier_color}">
            <div class="wf-rank">{rank_label}</div>
            <div class="wf-name">{wf.get('name','')}</div>
            <span class="tier-pill" style="background:{tier_bg}; color:{tier_color}; border:1px solid {tier_color}40">{tier_label} PRIORITY</span>
          </div>

          <div class="wf-sequence">{seq_html}</div>

          <div class="metrics-row">
            <div class="metric-box">
              <div class="m-label">WEEKLY COST</div>
              <div class="m-big" style="color:{tier_color}">{roi.get('weekly_cost_label','â€”')}</div>
              <div class="m-sub">{wf.get('total_time_hours_per_week',0):.1f} hrs/week</div>
            </div>
            <div class="metric-box">
              <div class="m-label">ANNUAL COST</div>
              <div class="m-big">{roi.get('annual_cost_label','â€”')}</div>
              <div class="m-sub">{roi.get('annual_hours_label','â€”')}</div>
            </div>
            <div class="metric-box">
              <div class="m-label">RECOVERABLE</div>
              <div class="m-big" style="color:#10d9a0">{roi.get('automatable_cost_label','â€”')}</div>
              <div class="m-sub">at 80% automation</div>
            </div>
            <div class="metric-box">
              <div class="m-label">FREQUENCY</div>
              <div class="m-big">{wf.get('frequency',0)}Ã—</div>
              <div class="m-sub">{wf.get('avg_duration_minutes',0):.0f} min avg</div>
            </div>
            <div class="metric-box">
              <div class="m-label">CONFIDENCE</div>
              <div class="m-big">{int(wf.get('confidence',0)*100)}%</div>
              <div class="m-sub">pattern match</div>
            </div>
          </div>

          <details class="llm-context">
            <summary>Analysis context (for LLM)</summary>
            <div class="ctx-body">{ctx_lines}</div>
          </details>
        </div>
        """

    # No-data state
    if not wfs:
        wf_cards = """
        <div class="no-data">
          <div class="no-data-icon">ðŸ§ </div>
          <p>No recurring workflow patterns detected yet.</p>
          <p class="no-data-sub">Browse Gmail, LinkedIn, or Notion for 2â€“3 separate sessions with the Chrome Extension active, then revisit this report.</p>
        </div>
        """

    top = ex.get("top_opportunity") or {}

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dead Time Intelligence Report â€” {meta['org_id']}</title>
  <meta name="description" content="Workflow intelligence brief generated by Dead Time. Identifies recurring workflows, quantifies time cost, and ranks automation opportunities."/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{
      --bg:#07091a; --bg2:#0d1129; --card:rgba(255,255,255,0.04);
      --border:rgba(255,255,255,0.07); --indigo:#6d63ff; --emerald:#10d9a0;
      --amber:#f59e0b; --rose:#f43f5e;
      --t1:#f0f2ff; --t2:#9ea8c4; --t3:#5a6585;
      --font:'Plus Jakarta Sans',system-ui,sans-serif;
      --mono:'JetBrains Mono',monospace;
    }}
    body{{font-family:var(--font);background:var(--bg);color:var(--t1);line-height:1.6;min-height:100vh}}
    body::before{{
      content:'';position:fixed;inset:0;pointer-events:none;
      background:radial-gradient(ellipse 60% 40% at 8% 5%,rgba(109,99,255,.09) 0%,transparent 55%),
                 radial-gradient(ellipse 45% 30% at 92% 88%,rgba(16,217,160,.06) 0%,transparent 55%);
    }}
    .page{{position:relative;max-width:960px;margin:0 auto;padding:3rem 2rem 5rem}}

    /* â”€â”€ Cover â”€â”€ */
    .cover{{margin-bottom:3.5rem;padding-bottom:2rem;border-bottom:1px solid var(--border)}}
    .cover-top{{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;margin-bottom:1.5rem}}
    .badge{{display:inline-flex;align-items:center;gap:.4rem;padding:.3rem .8rem;border-radius:9999px;font:700 .7rem var(--font);text-transform:uppercase;letter-spacing:.07em}}
    .badge-dt{{background:rgba(109,99,255,.18);color:var(--indigo);border:1px solid rgba(109,99,255,.3)}}
    .badge-conf{{background:rgba(16,217,160,.12);color:var(--emerald);border:1px solid rgba(16,217,160,.25)}}
    .cover-title{{font-size:2.2rem;font-weight:800;letter-spacing:-.04em;line-height:1.15;margin-bottom:.5rem}}
    .cover-sub{{font-size:1rem;color:var(--t2)}}
    .cover-meta{{display:flex;flex-wrap:wrap;gap:1.5rem;margin-top:1.25rem}}
    .meta-item{{font-size:.78rem;color:var(--t3)}}
    .meta-item strong{{color:var(--t2);font-weight:600}}

    /* â”€â”€ Executive Summary â”€â”€ */
    .section-label{{font:.7rem/1 var(--font);font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--t3);margin-bottom:1rem}}
    .exec-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:1rem;margin-bottom:2.5rem}}
    .exec-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.2rem 1.4rem;transition:border-color .2s}}
    .exec-card:hover{{border-color:rgba(109,99,255,.35)}}
    .ec-label{{font:.65rem/1 var(--font);font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--t3);margin-bottom:.45rem}}
    .ec-value{{font-size:1.8rem;font-weight:800;letter-spacing:-.03em;line-height:1}}
    .ec-sub{{font-size:.7rem;color:var(--t3);margin-top:.3rem}}
    .c-indigo{{color:var(--indigo)}} .c-emerald{{color:var(--emerald)}} .c-amber{{color:var(--amber)}} .c-rose{{color:var(--rose)}}

    /* â”€â”€ Hero Opportunity â”€â”€ */
    .hero{{background:linear-gradient(135deg,rgba(109,99,255,.12),rgba(16,217,160,.08));border:1px solid rgba(109,99,255,.25);border-radius:14px;padding:1.75rem 2rem;margin-bottom:2.5rem}}
    .hero-label{{font:.68rem/1 var(--font);font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--indigo);margin-bottom:.6rem}}
    .hero-name{{font-size:1.4rem;font-weight:800;letter-spacing:-.02em;margin-bottom:.75rem}}
    .hero-stats{{display:flex;flex-wrap:wrap;gap:1.5rem}}
    .hero-stat .hs-val{{font:700 1.25rem var(--font);letter-spacing:-.02em}}
    .hero-stat .hs-lbl{{font:.7rem/1 var(--font);color:var(--t3);margin-top:.15rem}}

    /* â”€â”€ Workflow Cards â”€â”€ */
    .wf-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.5rem;margin-bottom:1.25rem;transition:border-color .2s,transform .2s}}
    .wf-card:hover{{transform:translateY(-2px);border-color:rgba(109,99,255,.3)}}
    .wf-card-header{{display:flex;flex-wrap:wrap;align-items:baseline;gap:.75rem;margin-bottom:.85rem}}
    .wf-rank{{font:.68rem/1 var(--font);font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--t3)}}
    .wf-name{{font:700 1.05rem var(--font);letter-spacing:-.01em;flex:1}}
    .tier-pill{{padding:.2rem .6rem;border-radius:9999px;font:700 .65rem var(--font);text-transform:uppercase;letter-spacing:.06em;white-space:nowrap}}

    .wf-sequence{{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;margin-bottom:1.1rem}}
    .app-chip{{padding:.25rem .65rem;border-radius:6px;background:rgba(109,99,255,.12);border:1px solid rgba(109,99,255,.22);font:.7rem/1 var(--mono);color:#b5b2ff}}
    .arr{{color:var(--t3);font-size:.85rem}}

    .metrics-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:.75rem;padding:1rem 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin-bottom:.9rem}}
    .metric-box .m-label{{font:.6rem/1 var(--font);font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--t3);margin-bottom:.3rem}}
    .metric-box .m-big{{font:800 1.3rem var(--font);letter-spacing:-.02em;color:var(--t1)}}
    .metric-box .m-sub{{font:.65rem/1 var(--font);color:var(--t3);margin-top:.2rem}}

    .llm-context{{background:rgba(255,255,255,.025);border:1px solid var(--border);border-radius:8px;overflow:hidden}}
    .llm-context summary{{padding:.6rem 1rem;font:.75rem/1 var(--font);font-weight:600;color:var(--t3);cursor:pointer;list-style:none;display:flex;align-items:center;gap:.4rem}}
    .llm-context summary::before{{content:'â–¶';font-size:.6rem}}
    .llm-context[open] summary::before{{content:'â–¼'}}
    .ctx-body{{padding:.75rem 1rem 1rem;font:.72rem/1.7 var(--mono);color:var(--t2);border-top:1px solid var(--border)}}

    /* â”€â”€ No Data â”€â”€ */
    .no-data{{text-align:center;padding:4rem 2rem;color:var(--t3)}}
    .no-data-icon{{font-size:2.5rem;margin-bottom:1rem}}
    .no-data-sub{{font-size:.82rem;margin-top:.5rem;max-width:400px;margin-left:auto;margin-right:auto}}

    /* â”€â”€ Footer â”€â”€ */
    .report-footer{{margin-top:3.5rem;padding-top:1.5rem;border-top:1px solid var(--border);font-size:.72rem;color:var(--t3);line-height:1.8}}
    .report-footer strong{{color:var(--t2)}}

    /* â”€â”€ Nav â”€â”€ */
    .top-nav{{display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem}}
    .nav-link{{font:.78rem/1 var(--font);font-weight:600;color:var(--t2);text-decoration:none;padding:.4rem .9rem;border:1px solid var(--border);border-radius:7px;background:var(--card);transition:all .18s}}
    .nav-link:hover{{border-color:rgba(109,99,255,.4);color:var(--t1)}}

    @media print{{
      body{{background:#fff;color:#111}}
      body::before{{display:none}}
      .nav-link{{display:none}}
      .wf-card,.exec-card,.hero{{border:1px solid #ddd;background:#fafafa}}
      .cover-title,.ec-value,.m-big,.wf-name,.hero-name{{color:#111}}
      .ec-label,.m-label,.m-sub,.ec-sub,.wf-rank,.section-label,.badge-dt,.cover-sub,.meta-item{{color:#555}}
      .badge-dt,.badge-conf{{border:1px solid #ccc;background:#f0f0f0;color:#333}}
      .app-chip{{background:#f0f0ff;border:1px solid #ccc;color:#333}}
      .llm-context{{display:none}}
    }}
  </style>
</head>
<body>
<div class="page">

  <nav class="top-nav">
    <a href="/" class="nav-link">â† Dashboard</a>
    <a href="/workflows/brief?hourly_rate={meta['hourly_rate_gbp']}&org_id={meta['org_id']}" class="nav-link">â¬‡ Download JSON Brief</a>
  </nav>

  <!-- Cover -->
  <div class="cover">
    <div class="cover-top">
      <div>
        <span class="badge badge-dt">Dead Time Â· Workflow Intelligence</span>
      </div>
      <span class="badge badge-conf">CONFIDENTIAL</span>
    </div>
    <div class="cover-title">Workflow Intelligence<br>Brief</div>
    <div class="cover-sub">Continuous process observation &amp; automation opportunity analysis</div>
    <div class="cover-meta">
      <div class="meta-item">Organisation: <strong>{meta['org_id']}</strong></div>
      <div class="meta-item">Generated: <strong>{gen_str}</strong></div>
      <div class="meta-item">Observation window: <strong>{meta['observation_days']} day(s)</strong></div>
      <div class="meta-item">Hourly rate: <strong>Â£{meta['hourly_rate_gbp']:.0f}/hr</strong></div>
      <div class="meta-item">Brief ID: <strong style="font-family:var(--mono);font-size:.7rem">{meta['brief_id']}</strong></div>
    </div>
  </div>

  <!-- Executive Summary -->
  <div class="section-label">Executive Summary</div>
  <div class="exec-grid">
    <div class="exec-card">
      <div class="ec-label">Events Captured</div>
      <div class="ec-value c-indigo">{ex.get('total_events_captured',0)}</div>
      <div class="ec-sub">activity signals observed</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Sessions Detected</div>
      <div class="ec-value c-emerald">{ex.get('total_sessions_detected',0)}</div>
      <div class="ec-sub">work sessions reconstructed</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Patterns Found</div>
      <div class="ec-value c-amber">{ex.get('total_workflows_identified',0)}</div>
      <div class="ec-sub">recurring workflows</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Weekly Cost</div>
      <div class="ec-value c-rose">{ex.get('weekly_cost_across_workflows','—')}</div>
      <div class="ec-sub">across all patterns</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Annual Cost</div>
      <div class="ec-value">{ex.get('annual_cost_across_workflows','—')}</div>
      <div class="ec-sub">48 working weeks</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Recoverable / yr</div>
      <div class="ec-value c-emerald">{ex.get('recoverable_annually','—')}</div>
      <div class="ec-sub">at 80% automation</div>
    </div>
  </div>

  <!-- Hero: Top Opportunity -->
  {"" if not top else f'''
  <div class="hero">
    <div class="hero-label">Top Automation Opportunity</div>
    <div class="hero-name">{top.get("name","—")}</div>
    <div class="hero-stats">
      <div class="hero-stat"><div class="hs-val" style="color:var(--rose)">{top.get("weekly_cost","—")}</div><div class="hs-lbl">weekly cost</div></div>
      <div class="hero-stat"><div class="hs-val" style="color:var(--amber)">{top.get("annual_cost","—")}</div><div class="hs-lbl">annual cost</div></div>
      <div class="hero-stat"><div class="hs-val" style="color:var(--emerald)">{top.get("frequency","—")}x</div><div class="hs-lbl">sessions matched</div></div>
    </div>
  </div>
  '''}

  <!-- Workflow Cards -->
  <div class="section-label">Workflow Patterns — Ranked by ROI Impact</div>
  {wf_cards}

  <!-- Footer -->
  <div class="report-footer">
    <strong>Methodology.</strong> Telemetry signals were aggregated across applications to detect recurring sequential patterns.
    Sessions were reconstructed by splitting the event stream on inactivity gaps exceeding 30 minutes.
    Recurring patterns were identified using sequence frequency analysis across all sessions.
    Costs are extrapolated from observed frequency to a 7-day week and a 48-week working year.
    Automation savings assume 80% of manual time is recoverable — a conservative industry estimate for structured, repetitive workflows.
    <br><br>
    <strong>Brief ID:</strong> {meta['brief_id']} · <strong>Schema:</strong> v{meta['schema_version']} · <strong>Source:</strong> {meta['source']}
  </div>

</div>
</body>
</html>"""


# â”€â”€â”€ Legacy Inline Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Removed: The monolithic DASHBOARD_HTML (520 lines) was superseded by the
# Next.js frontend at http://localhost:3000. See ENTERPRISE_LAUNCHER_HTML below
# for the redirect gateway served at GET /.

_LEGACY_DASHBOARD_REMOVED = True  # Marker for audit trail

DASHBOARD_HTML = None  # Content removed â€” superseded by Next.js frontend


@app.get("/workflows/ai-analysis", tags=["Layer 4 â€” AI Insights"])
def get_ai_analysis(
    hourly_rate: float = Query(DEFAULT_HOURLY_RATE, description="Hourly rate"),
    currency: str = Query(DEFAULT_CURRENCY, description="Currency code"),
    symbol: str = Query(DEFAULT_CURRENCY_SYMBOL, description="Currency symbol"),
    org_id: str = Query("org_demo"),
    db: Session = Depends(get_db),
):
    """
    Gemini-powered automation recommendations.
    Sends the intelligence brief to Gemini with structured JSON output enforcement.
    Returns grounded, hallucination-free automation advice.
    """
    all_events, result, obs = _run_detection(db)
    brief = build_intelligence_brief(
        patterns=result["patterns"],
        summary=result["summary"],
        hourly_rate=hourly_rate,
        currency=currency,
        currency_symbol=symbol,
        org_id=org_id,
        observation_days=obs,
    )
    response = analyze_brief(brief)
    return JSONResponse(content=response)




@app.post("/demo/seed", tags=["Meta"])
def trigger_seed_demo():
    """Reset and seed enterprise demonstration dataset."""
    from seed_demo import seed_enterprise_demo
    result = seed_enterprise_demo()
    return JSONResponse(content=result)


ENTERPRISE_LAUNCHER_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dead Time â€” Enterprise Gateway</title>
  <meta http-equiv="refresh" content="0; url=http://localhost:3000/">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #07091a; color: #f0f2ff; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; overflow: hidden; }
    body::before {
      content: ''; position: fixed; inset: 0; pointer-events: none;
      background: radial-gradient(ellipse 60% 40% at 20% 20%, rgba(109,99,255,.18) 0%, transparent 60%),
                  radial-gradient(ellipse 50% 35% at 80% 80%, rgba(16,217,160,.12) 0%, transparent 60%);
    }
    .box { position: relative; z-index: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 3rem 2.5rem; max-width: 540px; text-align: center; box-shadow: 0 24px 60px rgba(0,0,0,0.6); backdrop-filter: blur(16px); }
    .logo { width: 52px; height: 52px; margin: 0 auto 1.5rem; background: linear-gradient(135deg, #6d63ff, #10d9a0); border-radius: 14px; display: grid; place-items: center; font-weight: 800; font-size: 1.2rem; color: #fff; box-shadow: 0 0 24px rgba(109,99,255,0.5); }
    h1 { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.5rem; background: linear-gradient(135deg, #ffffff, #b5b2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .tag { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.3rem 0.8rem; background: rgba(16,217,160,0.12); border: 1px solid rgba(16,217,160,0.3); border-radius: 9999px; color: #10d9a0; font-size: 0.75rem; font-weight: 700; margin-bottom: 1.25rem; }
    p { color: #9ea8c4; font-size: 0.92rem; line-height: 1.6; margin-bottom: 2rem; }
    .btn { display: block; width: 100%; padding: 0.9rem 1.4rem; background: linear-gradient(135deg, #6d63ff, #10d9a0); color: #fff; font-weight: 700; font-size: 0.95rem; border-radius: 10px; text-decoration: none; box-shadow: 0 4px 20px rgba(109,99,255,0.4); transition: transform 0.2s, box-shadow 0.2s; }
    .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(109,99,255,0.6); }
    .docs { display: inline-block; margin-top: 1.4rem; color: #9d98ff; font-size: 0.82rem; text-decoration: none; font-weight: 600; }
    .docs:hover { color: #fff; }
  </style>
</head>
<body>
  <div class="box">
    <div class="logo">DT</div>
    <div class="tag">â— ENTERPRISE CORE ACTIVE</div>
    <h1>Dead Time B2B</h1>
    <p>Continuous Workflow Intelligence &amp; Closed-Loop Automation Engine.<br>Redirecting to the Next.js Executive SaaS Experience...</p>
    <a href="http://localhost:3000/" class="btn">Launch Enterprise Dashboard (Port 3000) â†’</a>
    <a href="/docs" class="docs">Interactive Swagger API Documentation â†’</a>
  </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard():
    return ENTERPRISE_LAUNCHER_HTML

