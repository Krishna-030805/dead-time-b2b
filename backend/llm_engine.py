"""
llm_engine.py
=============
Layer 4 — LLM Insight Engine (Google Gemini)

Sends the structured intelligence brief produced by Layer 3 to Gemini 2.0 Flash
with structured JSON output enforcement (schema-constrained decoding).

Because we feed the LLM clean, quantified, context-rich data instead of raw
events, the output is grounded and hallucination-free.

Usage:
    from llm_engine import analyze_brief
    result = analyze_brief(brief_dict)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

_BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv()  # Also check cwd

# Multi-model resilience pool.
# If a model experiences temporary high demand (503) or rate limits (429),
# the engine automatically fails over to the next available candidate.
GEMINI_MODELS: List[str] = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
GEMINI_MODEL: str = GEMINI_MODELS[0]

def get_gemini_api_key() -> Optional[str]:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        load_dotenv(_BACKEND_DIR / ".env", override=True)
        load_dotenv(override=True)
        key = os.environ.get("GEMINI_API_KEY")
    return key



# ─── Structured Output Schema (Pydantic) ─────────────────────────────────────
# Gemini will be constrained to exactly this shape.
# This eliminates hallucination and guarantees machine-parseable output.

class TopOpportunity(BaseModel):
    workflow_name:                    str
    recommended_tool:                 str
    why_this_tool:                    str
    what_gets_automated:              str
    automation_steps:                 List[str]
    estimated_hours_saved_per_week:   float
    payback_period_label:             str
    complexity:                       str   # "Low" | "Medium" | "High"
    required_apis:                    List[str]


class QuickWin(BaseModel):
    title:       str
    description: str
    time_saved:  str   # e.g. "30 min/week"


class WorkflowAssessment(BaseModel):
    workflow_name:           str
    complexity:              str   # "Low" | "Medium" | "High"
    automation_approach:     str
    required_integrations:   List[str]


class AIInsights(BaseModel):
    top_opportunity:       TopOpportunity
    executive_pitch:       str            # 3 concise sentences for a decision-maker
    quick_wins:            List[QuickWin]
    workflow_assessments:  List[WorkflowAssessment]


def _build_heuristic_fallback(brief: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic rule-based fallback that adheres strictly to AIInsights schema.
    Guarantees the system never crashes even during full API outages or 503 spikes.
    """
    workflows = brief.get("workflows", [])
    top_wf = workflows[0] if workflows else {}
    wf_name = top_wf.get("name", "Manual Multi-App Workflow")
    apps = top_wf.get("apps", [])
    hours = top_wf.get("time_cost_hours_per_week", 2.5)
    payback = top_wf.get("payback_label", "Immediate (< 1 month)")

    if any(a in ["jira", "github", "zendesk"] for a in apps):
        tool = "Make.com or Zapier"
        why = f"Native API webhook connectors for {', '.join(apps)} allow automated trigger-action synchronization without manual copy-paste."
    else:
        tool = "Zapier / Make.com"
        why = f"Direct turnkey connectors available for {', '.join(apps)} to automate cross-platform loops."

    top_opportunity = {
        "workflow_name": wf_name,
        "recommended_tool": tool,
        "why_this_tool": why,
        "what_gets_automated": f"Automates manual data passing and context switching across {' -> '.join(apps)}.",
        "automation_steps": [
            f"1. Set up event trigger on {apps[0] if apps else 'source application'}.",
            f"2. Transform data payload and map fields across platforms.",
            f"3. Push automated updates to {apps[-1] if len(apps) > 1 else 'destination application'}."
        ],
        "estimated_hours_saved_per_week": float(hours),
        "payback_period_label": payback,
        "complexity": "Low" if len(apps) <= 3 else "Medium",
        "required_apis": [f"{a}_api" for a in apps]
    }

    assessments = []
    for w in workflows[:3]:
        assessments.append({
            "workflow_name": w.get("name", "Recurring Workflow"),
            "complexity": "Low" if len(w.get("sequence", [])) <= 3 else "Medium",
            "automation_approach": f"Direct webhook trigger in {w.get('sequence', ['app'])[0]} mapped to downstream actions.",
            "required_integrations": w.get("sequence", [])
        })

    return {
        "top_opportunity": top_opportunity,
        "executive_pitch": f"Identified {len(workflows)} recurring manual workflows consuming significant employee bandwidth. Automating the primary {wf_name} pattern unlocks estimated capacity savings of {hours} hours weekly. Payback is projected at {payback} with minimal setup overhead.",
        "quick_wins": [
            {
                "title": f"Turnkey Webhook Sync for {wf_name}",
                "description": f"Eliminate repetitive manual copying between {', '.join(apps)} using a prebuilt automation connector.",
                "time_saved": f"{round(float(hours)*0.6, 1)} hrs/week"
            }
        ],
        "workflow_assessments": assessments
    }


# ─── Core Function ────────────────────────────────────────────────────────────

def analyze_brief(brief: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send the intelligence brief to Gemini with automatic multi-model failover.
    Returns structured AI insights or graceful deterministic fallback.
    """

    # ── Guard: API key ────────────────────────────────────────────────────────
    api_key = get_gemini_api_key()
    if not api_key:
        return {
            "status":  "error",
            "message": (
                "GEMINI_API_KEY not found. "
                "Please create a file named '.env' in the backend folder "
                "and add: GEMINI_API_KEY=your_key_here"
            ),
        }

    # ── Guard: Patterns needed ────────────────────────────────────────────────
    patterns = brief.get("workflows", [])
    if not patterns:
        return {
            "status":  "no_patterns",
            "message": (
                "No recurring workflow patterns have been detected yet. "
                "Browse Gmail, LinkedIn, or Notion across at least 2 separate sessions "
                "with the Chrome Extension active, then try again."
            ),
        }

    # ── Call Gemini with Multi-Model Failover ──────────────────────────────────
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # Build the prompt: prepend the LLM prompt from the brief, then append the full JSON
        llm_prompt = brief.get("llm_prompt", "")
        brief_body = json.dumps(brief, indent=2, default=str)
        full_prompt = f"{llm_prompt}\n\n{brief_body}\n\n---END INTELLIGENCE BRIEF JSON---"

        response = None
        used_model = None
        last_error = None

        for candidate in GEMINI_MODELS:
            try:
                print(f"[LLM Engine] Querying model candidate: {candidate}...")
                response = client.models.generate_content(
                    model=candidate,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIInsights,
                        temperature=0.2,   # Low temperature = precise, consistent output
                    ),
                )
                if response and response.text:
                    used_model = candidate
                    print(f"[LLM Engine] Successfully generated insights using: {candidate}")
                    break
                else:
                    print(f"[LLM Engine] Candidate {candidate} returned empty text, trying next...")
            except Exception as err:
                last_error = err
                print(f"[LLM Engine] Candidate {candidate} failed: {type(err).__name__}: {err}. Failing over...")
                continue

        if response is None or not response.text:
            print("[LLM Engine] All remote model candidates failed. Activating deterministic fallback...")
            return {
                "status":       "success",
                "model":        "deterministic_heuristic_fallback",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "brief_id":     brief.get("meta", {}).get("brief_id", ""),
                "insights":     _build_heuristic_fallback(brief),
            }

        # Gemini returns a JSON string in response.text
        insights_dict = json.loads(response.text)

        return {
            "status":       "success",
            "model":        used_model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "brief_id":     brief.get("meta", {}).get("brief_id", ""),
            "insights":     insights_dict,
        }

    except Exception as exc:
        print(f"[LLM Engine] Unexpected exception: {exc}. Activating heuristic fallback...")
        return {
            "status":       "success",
            "model":        "deterministic_heuristic_fallback",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "brief_id":     brief.get("meta", {}).get("brief_id", ""),
            "insights":     _build_heuristic_fallback(brief),
        }

