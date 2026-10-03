"""
export_engine.py
================
Layer 5b — Automation Export Engine

Converts an approved AutomationBlueprint into a real, importable workflow
definition for three popular automation platforms:

  1. n8n         — JSON workflow that can be imported via n8n UI / API
  2. Make.com    — JSON scenario blueprint
  3. Python      — Standalone async Python script with env-var placeholders
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    """Convert a human name to a safe identifier slug."""
    return text.lower().replace(" ", "_").replace("/", "_").replace("-", "_")


def _pascal(text: str) -> str:
    """Convert to PascalCase for class/node names."""
    return "".join(w.capitalize() for w in text.replace("-", " ").replace("_", " ").split())


# ─── n8n Export ───────────────────────────────────────────────────────────────

def generate_n8n_workflow(bp_json: Dict[str, Any], blueprint_name: str) -> Dict[str, Any]:
    """
    Generates an importable n8n workflow JSON.
    The result can be directly pasted into n8n via:
      n8n UI → Workflows → Import from File / Clipboard
    """
    trigger_app = bp_json.get("trigger_app", "webhook")
    trigger_event = bp_json.get("trigger_event", "New Event")
    destination_app = bp_json.get("destination_app", "http")
    destination_action = bp_json.get("destination_action", "Create Record")
    transformations = bp_json.get("transformations", [])
    inputs = bp_json.get("inputs", [])
    setup_time = bp_json.get("estimated_setup_time_mins", 30)

    # Build nodes list
    nodes = []
    node_x = 250
    node_y = 300

    # 1. Trigger Node
    trigger_node_type = "n8n-nodes-base.webhook"
    trigger_params = {
        "httpMethod": "POST",
        "path": f"dead-time/{_slug(blueprint_name)}",
        "responseMode": "onReceived",
    }

    nodes.append({
        "id": str(uuid.uuid4()),
        "name": f"Trigger: {trigger_app.title()}",
        "type": trigger_node_type,
        "typeVersion": 1,
        "position": [node_x, node_y],
        "parameters": trigger_params,
        "notes": f"Triggered when: {trigger_event}\nSource App: {trigger_app}\nInputs captured: {', '.join(inputs)}",
    })
    node_x += 200

    # 2. Transformation Nodes (one Function node per transformation step)
    for t in transformations:
        step_num = t.get("step", 1)
        step_desc = t.get("description", "Transform data")
        action_type = t.get("action_type", "format")

        js_code = f"""// Step {step_num}: {step_desc}
// Action type: {action_type}
const inputData = $input.all();
const transformed = inputData.map(item => {{
  const data = item.json;
  // TODO: Map your specific fields here
  // Example: data.jira_summary = data.email_subject;
  return {{ json: data }};
}});
return transformed;"""

        nodes.append({
            "id": str(uuid.uuid4()),
            "name": f"Step {step_num}: {step_desc[:40]}",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [node_x, node_y],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": js_code,
            },
        })
        node_x += 200

    # 3. Human Approval Checkpoint (Wait node)
    nodes.append({
        "id": str(uuid.uuid4()),
        "name": "⚠️ Human Approval Gate",
        "type": "n8n-nodes-base.wait",
        "typeVersion": 1,
        "position": [node_x, node_y],
        "parameters": {
            "resume": "webhook",
            "options": {},
        },
        "notes": "MANDATORY: A human must approve before data is sent to the destination.\nConfigure: Send a Slack/Email notification with the approval webhook URL.",
    })
    node_x += 200

    # 4. Destination Node
    nodes.append({
        "id": str(uuid.uuid4()),
        "name": f"Output: {destination_app.title()} — {destination_action}",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [node_x, node_y],
        "parameters": {
            "method": "POST",
            "url": f"={{ $env.{_slug(destination_app).upper()}_API_URL }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "bodyParameters": {
                "parameters": [
                    {"name": field, "value": f"={{ $json.{field} }}"}
                    for field in inputs[:3]
                ]
            },
        },
        "notes": f"Destination: {destination_app}\nAction: {destination_action}\nSet env var: {_slug(destination_app).upper()}_API_URL",
    })

    # Build connections (linear chain)
    connections: Dict[str, Any] = {}
    for i in range(len(nodes) - 1):
        src_name = nodes[i]["name"]
        dst_name = nodes[i + 1]["name"]
        connections[src_name] = {
            "main": [[{"node": dst_name, "type": "main", "index": 0}]]
        }

    return {
        "name": blueprint_name,
        "nodes": nodes,
        "connections": connections,
        "active": False,
        "settings": {
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner",
            "errorWorkflow": "",
        },
        "id": str(uuid.uuid4()),
        "meta": {
            "instanceId": "dead-time-b2b",
            "templateCredsSetupCompleted": False,
        },
        "tags": ["dead-time", "auto-generated"],
        "notes": (
            f"Generated by Dead Time B2B on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.\n"
            f"Estimated setup time: {setup_time} minutes.\n"
            "IMPORTANT: Review all field mappings and configure API credentials before activating."
        ),
        "versionId": str(uuid.uuid4()),
    }


# ─── Make.com Export ──────────────────────────────────────────────────────────

def generate_make_blueprint(bp_json: Dict[str, Any], blueprint_name: str) -> Dict[str, Any]:
    """
    Generates an importable Make.com (formerly Integromat) scenario blueprint.
    Import via: Make.com → Scenarios → Create a new scenario → Import Blueprint
    """
    trigger_app = bp_json.get("trigger_app", "webhook")
    trigger_event = bp_json.get("trigger_event", "New Event")
    destination_app = bp_json.get("destination_app", "http")
    destination_action = bp_json.get("destination_action", "Create Record")
    transformations = bp_json.get("transformations", [])
    inputs = bp_json.get("inputs", [])

    module_id = 1
    modules = []

    # 1. Webhook Trigger
    modules.append({
        "id": module_id,
        "module": "gateway:CustomWebHook",
        "version": 1,
        "parameters": {},
        "mapper": {},
        "metadata": {
            "designer": {
                "x": 0,
                "y": 0,
                "name": f"Trigger: {trigger_app.title()} — {trigger_event}",
            },
            "restore": {},
        },
    })
    module_id += 1

    # 2. Transformation modules (JSON Parse / Set Variables)
    for t in transformations:
        variables_list = [
            {
                "name": f"step_{t.get('step', module_id)}_{inp}_result",
                "value": f"{{{{1.{inp}}}}}" if inputs else "{{1.value}}",
            }
            for inp in inputs[:2]
        ]
        if not variables_list:
            variables_list = [{"name": f"step_{t.get('step', module_id)}_result", "value": "{{1.value}}"}]
            
        modules.append({
            "id": module_id,
            "module": "util:SetVariables",
            "version": 1,
            "parameters": {},
            "mapper": {
                "variables": variables_list
            },
            "metadata": {
                "designer": {
                    "x": (module_id - 1) * 300,
                    "y": 0,
                    "name": f"Step {t.get('step','?')}: {t.get('description', 'Transform')[:40]}",
                },
            },
        })
        module_id += 1

    # 3. HTTP Module for Destination
    modules.append({
        "id": module_id,
        "module": "http:ActionSendData",
        "version": 3,
        "parameters": {"handleErrors": False, "useNewZLibDeCompression": True},
        "mapper": {
            "url": f"https://api.example.com/REPLACE_WITH_{_slug(destination_app).upper()}_API_URL",
            "method": "post",
            "headers": [
                {"name": "Content-Type", "value": "application/json"},
                {"name": "Authorization", "value": f"Bearer {{{{$env.{_slug(destination_app).upper()}_TOKEN}}}}"},
            ],
            "bodyType": "raw",
            "contentType": "json",
            "data": json.dumps({field: f"{{{{{field}}}}}" for field in inputs}),
        },
        "metadata": {
            "designer": {
                "x": (module_id - 1) * 300,
                "y": 0,
                "name": f"Output: {destination_app.title()} — {destination_action}",
            },
        },
    })

    return {
        "name": blueprint_name,
        "flow": modules,
        "scheduling": {
            "type": "indefinitely",
            "interval": 15,
            "unit": "minutes",
        },
        "metadata": {
            "instant": True,
            "designer": {"orphans": []},
            "version": 1,
            "scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": True,
                "autoCommitTriggerLast": True,
                "sequential": False,
                "slots": None,
                "confidential": False,
                "dataloss": False,
                "dlq": False,
                "freshVariables": False,
            },
            "generated_by": "dead-time-b2b",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "notes": (
                f"Blueprint: {blueprint_name}\n"
                "Human approval checkpoint: Add a 'Send Slack notification + wait for approval' "
                "module before the final output module.\n"
                "Required: Set all API credentials in Make.com Connections before activating."
            ),
        },
    }


# ─── Python Export ────────────────────────────────────────────────────────────

def generate_python_script(bp_json: Dict[str, Any], blueprint_name: str) -> str:
    """
    Generates a standalone async Python automation script.
    Uses environment variables for API keys and httpx for HTTP calls.
    """
    trigger_app = bp_json.get("trigger_app", "webhook")
    trigger_event = bp_json.get("trigger_event", "New Event")
    destination_app = bp_json.get("destination_app", "http")
    destination_action = bp_json.get("destination_action", "Create Record")
    transformations = bp_json.get("transformations", [])
    inputs = bp_json.get("inputs", ["record_id", "timestamp"])
    setup_time = bp_json.get("estimated_setup_time_mins", 30)

    trigger_env = f"{_slug(trigger_app).upper()}_API_KEY"
    dest_env = f"{_slug(destination_app).upper()}_API_KEY"
    dest_url_env = f"{_slug(destination_app).upper()}_API_URL"

    transform_funcs = ""
    for t in transformations:
        fn_name = _slug(t.get("description", f"step_{t.get('step', 1)}"))[:30]
        transform_funcs += f'''
async def {fn_name}(data: dict) -> dict:
    """
    Step {t.get("step", "?")}: {t.get("description", "Transform")}
    Action: {t.get("action_type", "process")}
    """
    # TODO: Implement {t.get("action_type", "process")} logic here
    # Example: map field from {trigger_app} schema to {destination_app} schema
    transformed = {{**data}}
    return transformed
'''

    input_assignments = "\n".join(
        f'    {inp} = payload.get("{inp}", "")  # Required field from {trigger_app}'
        for inp in inputs
    )

    pipeline_calls_parts = []
    for t in transformations:
        _desc = t.get("description", f"step_{t.get('step', 1)}")
        _fn = _slug(_desc)[:30]
        _sn = t.get("step", "?")
        pipeline_calls_parts.append(f'    data = await {_fn}(data)  # Step {_sn}')
    pipeline_calls = "\n".join(pipeline_calls_parts)

    return f'''#!/usr/bin/env python3
"""
{blueprint_name}
{'=' * len(blueprint_name)}
Generated by Dead Time B2B — Automation Export Engine
Generated at: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
Estimated setup time: {setup_time} minutes

WORKFLOW:
  Trigger: {trigger_app} — {trigger_event}
  Destination: {destination_app} — {destination_action}

SETUP:
  1. Install dependencies: pip install httpx fastapi uvicorn python-dotenv
  2. Create a .env file with the required API keys (see ENV VARIABLES below)
  3. Run: python {_slug(blueprint_name)}.py
  4. POST a test payload to http://localhost:8888/webhook to verify

⚠️  HUMAN-IN-THE-LOOP: This script will send a Slack/email notification before
    executing any write operations. A human must approve by visiting the
    approval URL provided in the notification. DO NOT disable this safeguard.

ENV VARIABLES REQUIRED:
  {trigger_env}          API key for {trigger_app}
  {dest_env}             API key for {destination_app}
  {dest_url_env}         Base API URL for {destination_app}
  APPROVAL_NOTIFY_URL    Slack webhook URL for approval notifications
"""

import asyncio
import hashlib
import os
import uuid
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
{trigger_env.upper()} = os.getenv("{trigger_env}", "")
{dest_env.upper()} = os.getenv("{dest_env}", "")
DESTINATION_API_URL = os.getenv("{dest_url_env}", "https://api.example.com/records")
APPROVAL_NOTIFY_URL = os.getenv("APPROVAL_NOTIFY_URL", "")

# In-memory approval store (use Redis/DB in production)
_pending_approvals: dict[str, dict] = {{}}

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="{blueprint_name}")


# ── Transformation Steps ──────────────────────────────────────────────────────
{transform_funcs}


# ── Human Approval Gate ────────────────────────────────────────────────────────
async def request_human_approval(data: dict, context: str) -> str:
    """
    Sends a Slack notification with an approval link.
    Returns a unique approval_id. Execution blocks until approved.
    """
    approval_id = str(uuid.uuid4())[:8]
    approve_url = f"http://localhost:8888/approve/{{approval_id}}"
    reject_url = f"http://localhost:8888/reject/{{approval_id}}"

    _pending_approvals[approval_id] = {{"status": "pending", "data": data}}

    if APPROVAL_NOTIFY_URL:
        msg = {{
            "text": f"⚠️ *Dead Time Automation — Human Approval Required*\\n"
                    f"Workflow: *{blueprint_name}*\\n"
                    f"Context: {{context}}\\n"
                    f"✅ Approve: {{approve_url}}\\n"
                    f"❌ Reject: {{reject_url}}",
        }}
        async with httpx.AsyncClient() as client:
            await client.post(APPROVAL_NOTIFY_URL, json=msg, timeout=5)
    else:
        print(f"\\n[APPROVAL REQUIRED] Visit: {{approve_url}} or {{reject_url}}")

    return approval_id


async def wait_for_approval(approval_id: str, timeout_seconds: int = 3600) -> bool:
    """Poll for human approval. Times out after `timeout_seconds`."""
    for _ in range(timeout_seconds):
        await asyncio.sleep(1)
        status = _pending_approvals.get(approval_id, {{}}).get("status")
        if status == "approved":
            return True
        if status == "rejected":
            return False
    return False  # Timed out → treat as rejected


@app.get("/approve/{{approval_id}}")
async def approve_action(approval_id: str):
    if approval_id not in _pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")
    _pending_approvals[approval_id]["status"] = "approved"
    return {{"status": "approved", "message": "Automation approved. Execution will proceed."}}


@app.get("/reject/{{approval_id}}")
async def reject_action(approval_id: str):
    if approval_id not in _pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")
    _pending_approvals[approval_id]["status"] = "rejected"
    return {{"status": "rejected", "message": "Automation rejected. No data was sent."}}


# ── Destination Write ─────────────────────────────────────────────────────────
async def write_to_destination(data: dict) -> dict:
    """Send approved data to {destination_app} — {destination_action}."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            DESTINATION_API_URL,
            json=data,
            headers={{
                "Authorization": f"Bearer {{{{{dest_env.upper()}}}}}",
                "Content-Type": "application/json",
            }},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


# ── Main Webhook Handler ───────────────────────────────────────────────────────
@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Main entry point. Receives events from {trigger_app} and processes them
    through the transformation pipeline → human approval → destination write.
    """
    payload = await request.json()
    print(f"[{{datetime.now(timezone.utc).isoformat()}}] Received event from {trigger_app}")

    # Extract required fields
    data = {{}}
{input_assignments}
    data = {{"inputs": {{{", ".join(f'"{i}": {i}' for i in inputs)}}}, "source": "{trigger_app}", "timestamp": datetime.now(timezone.utc).isoformat()}}

    # Run transformation pipeline
{pipeline_calls if pipeline_calls else "    # No transformations defined"}

    # Human-in-the-Loop Gate — MANDATORY
    approval_id = await request_human_approval(data, f"Event from {trigger_app}")
    approved = await wait_for_approval(approval_id, timeout_seconds=3600)

    if not approved:
        return JSONResponse(
            status_code=200,
            content={{"status": "rejected", "message": "Human operator rejected this automation run."}}
        )

    # Write to destination
    try:
        result = await write_to_destination(data)
        print(f"[SUCCESS] Data written to {destination_app}: {{result}}")
        return {{"status": "success", "destination_response": result}}
    except httpx.HTTPError as exc:
        print(f"[ERROR] Failed to write to {destination_app}: {{exc}}")
        raise HTTPException(status_code=502, detail=f"Destination API error: {{exc}}")


@app.get("/health")
async def health():
    return {{"status": "running", "blueprint": "{blueprint_name}", "pending_approvals": len(_pending_approvals)}}


if __name__ == "__main__":
    print(f"Starting {blueprint_name} automation server on port 8888...")
    print("Send POST requests to http://localhost:8888/webhook to trigger the workflow.")
    uvicorn.run(app, host="0.0.0.0", port=8888)
'''
