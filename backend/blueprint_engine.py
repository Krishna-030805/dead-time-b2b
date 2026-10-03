"""
blueprint_engine.py
===================
Layer 5 — Automation Blueprint Engine

Transforms a detected workflow pattern (opportunity) into a concrete, 
machine-readable automation blueprint (JSON format). Uses Gemini with strict
schema decoding to ensure executable outputs.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from llm_engine import get_gemini_api_key, GEMINI_MODELS

# ─── Structured Output Schema (Pydantic) ─────────────────────────────────────
# This schema defines the structure of the execution blueprint.

class BlueprintTransformation(BaseModel):
    step: int
    description: str
    action_type: str # e.g., "extract", "format", "enrich"

class AutomationBlueprintSchema(BaseModel):
    blueprint_name: str
    trigger_app: str
    trigger_event: str
    inputs: List[str]
    transformations: List[BlueprintTransformation]
    destination_app: str
    destination_action: str
    human_in_the_loop_required: bool
    estimated_setup_time_mins: int


def _build_heuristic_fallback_blueprint(pattern: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic fallback for blueprint generation if API fails.
    """
    seq = pattern.get("sequence", ["app_a", "app_b"])
    apps = [app for app in seq if isinstance(app, str)]
    if not apps:
        apps = ["source_app", "dest_app"]
        
    src = apps[0]
    dst = apps[-1] if len(apps) > 1 else apps[0]

    return {
        "blueprint_name": f"Automated Sync: {src.title()} to {dst.title()}",
        "trigger_app": src,
        "trigger_event": "New record or activity created",
        "inputs": ["record_id", "timestamp", "metadata"],
        "transformations": [
            {
                "step": 1,
                "description": f"Extract fields from {src}",
                "action_type": "extract"
            },
            {
                "step": 2,
                "description": "Map to standard JSON format",
                "action_type": "format"
            }
        ],
        "destination_app": dst,
        "destination_action": "Create or update record",
        "human_in_the_loop_required": True,
        "estimated_setup_time_mins": 30
    }

def generate_blueprint_for_pattern(pattern: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an executable automation blueprint for a given workflow pattern.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        print("[Blueprint Engine] Missing API Key. Using fallback.")
        return _build_heuristic_fallback_blueprint(pattern)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = f"""
        You are an expert Automation Architect. 
        Analyze the following recurring manual workflow pattern and generate a structured execution blueprint.
        The blueprint will be used to configure an automation engine (e.g. Zapier/Make).
        
        CRITICAL RULES:
        1. Ensure 'human_in_the_loop_required' is ALWAYS True. No autonomous deployments.
        2. Identify the likely trigger app and the final destination app.
        3. Define clear transformation steps.
        
        PATTERN DATA:
        {json.dumps(pattern, indent=2)}
        """

        response = None
        for candidate in GEMINI_MODELS:
            try:
                print(f"[Blueprint Engine] Querying model candidate: {candidate}...")
                response = client.models.generate_content(
                    model=candidate,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AutomationBlueprintSchema,
                        temperature=0.1,
                    ),
                )
                if response and response.text:
                    print(f"[Blueprint Engine] Successfully generated blueprint using: {candidate}")
                    break
            except Exception as err:
                print(f"[Blueprint Engine] Candidate {candidate} failed: {err}. Failing over...")
                continue

        if response is None or not response.text:
             print("[Blueprint Engine] All models failed. Using fallback.")
             return _build_heuristic_fallback_blueprint(pattern)

        blueprint_dict = json.loads(response.text)
        # Enforce Human-in-the-Loop rule just in case the LLM ignored it
        blueprint_dict["human_in_the_loop_required"] = True
        return blueprint_dict

    except Exception as exc:
        print(f"[Blueprint Engine] Unexpected exception: {exc}. Using fallback.")
        return _build_heuristic_fallback_blueprint(pattern)
