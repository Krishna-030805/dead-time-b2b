"""
automation_engine.py
====================
Layer 6 — Automation Execution Engine

Responsible for taking an approved blueprint and deploying it.
Enforces the Human-in-the-Loop constraint: no blueprint can be deployed
unless its status is explicitly "approved".
"""

from typing import Dict, Any
from datetime import datetime, timezone
import random
import time

def deploy_blueprint(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the deployment of a blueprint to an automation platform (e.g. Zapier).
    Returns execution logs and the result status.
    """
    # ── Guard: Human in the loop ──────────────────────────────────────────────
    if blueprint.get("status") != "approved":
        return {
            "status": "failed",
            "error": "Human-in-the-Loop Gateway blocked execution. Blueprint is not 'approved'.",
            "logs": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "level": "ERROR", "message": "Deployment blocked. Status is pending_review or rejected."}
            ]
        }
    
    # ── Simulate Deployment ───────────────────────────────────────────────────
    logs = []
    def _log(msg: str, level: str = "INFO"):
        logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": msg
        })

    bp_json = blueprint.get("blueprint_json", {})
    name = bp_json.get("blueprint_name", blueprint.get("name", "Unknown Blueprint"))
    src = bp_json.get("trigger_app", "Source")
    dst = bp_json.get("destination_app", "Destination")
    
    _log(f"Initiating deployment for: {name}")
    _log("Human approval verified. Proceeding with execution configuration.")
    _log(f"Connecting to trigger source: {src}")
    
    # Simulate some work
    success = random.random() > 0.05 # 95% success rate for simulation
    
    if success:
        _log(f"Successfully subscribed to webhooks on {src}")
        for t in bp_json.get("transformations", []):
            _log(f"Configuring transformation step {t.get('step', '?')}: {t.get('action_type', 'process')}")
        _log(f"Testing connection to destination: {dst}")
        _log("Connection verified. Sending test payload.")
        _log("Test payload accepted. Automation is now LIVE.")
        
        return {
            "status": "success",
            "logs": logs
        }
    else:
        _log(f"Failed to authenticate with destination API: {dst}", "ERROR")
        _log("Deployment rolled back.", "ERROR")
        return {
            "status": "failed",
            "error": "Destination API authentication failure.",
            "logs": logs
        }
