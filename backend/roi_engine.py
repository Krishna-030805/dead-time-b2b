"""
roi_engine.py
=============
Layer 3 — ROI Quantification & LLM-Ready Brief Generator

Converts raw WorkflowPattern objects (from workflow_detector.py) into:
  1. Business value metrics  (£ cost per week / year)
  2. Natural language context strings (deterministic, no LLM needed)
  3. A fully structured JSON "Intelligence Brief" ready for LLM consumption

The JSON brief is designed so that pasting it verbatim into any LLM
(GPT-4, Claude, Gemini) with a standard prompt yields grounded,
hallucination-free automation recommendations.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ─── Defaults ─────────────────────────────────────────────────────────────────

DEFAULT_HOURLY_RATE:     float = 400.0   # Default labor rate (e.g. ₹400/hr)
DEFAULT_HOURLY_RATE_GBP: float = 50.0    # Legacy alias
DEFAULT_CURRENCY:        str   = "INR"
DEFAULT_CURRENCY_SYMBOL: str   = "₹"
WORKING_WEEKS_PER_YEAR:  int   = 48      # exclude 4 weeks holiday


# ─── App Vocabulary ───────────────────────────────────────────────────────────
# Plain-English description of what each tracked application represents.
# Used to construct deterministic LLM context strings.

APP_DESCRIPTIONS: Dict[str, str] = {
    "gmail":              "reading and sending emails in Gmail",
    "google_sheets":      "updating or reading data in Google Sheets",
    "google_docs":        "reading or writing a document in Google Docs",
    "google_slides":      "editing a presentation in Google Slides",
    "google_drive":       "navigating files in Google Drive",
    "google_calendar":    "scheduling or reviewing calendar events",
    "google_meet":        "attending or preparing for a video call",
    "notion":             "reading or creating pages in Notion",
    "linkedin":           "prospecting or messaging on LinkedIn",
    "slack_web":          "reading or sending messages in Slack (web)",
    "hubspot":            "managing contacts or deals in HubSpot",
    "salesforce":         "updating CRM records in Salesforce",
    "jira":               "creating or updating issues in Jira",
    "confluence":         "reading documentation in Confluence",
    "trello":             "moving cards across Trello boards",
    "asana":              "managing tasks and projects in Asana",
    "clickup":            "managing tasks in ClickUp",
    "monday":             "updating boards in Monday.com",
    "pipedrive":          "updating deal or contact records in Pipedrive",
    "calendly":           "scheduling or reviewing meeting bookings",
    "airtable":           "reading or updating data in Airtable",
    "github":             "reviewing code or issues on GitHub",
    "figma":              "designing or reviewing assets in Figma",
    "zoom":               "attending or scheduling a Zoom call",
    "typeform":           "building or reviewing a form in Typeform",
    "intercom":           "managing customer conversations in Intercom",
    "zendesk":            "handling support tickets in Zendesk",
}


# ─── Transition Intelligence ──────────────────────────────────────────────────
# Maps (app_a, app_b) → a human-readable workflow archetype.
# These are the most commercially meaningful transitions in B2B work.

TRANSITION_ARCHETYPES: Dict[tuple, str] = {
    # Outreach & Sales
    ("linkedin",       "gmail"):           "manual outreach loop — researching prospects on LinkedIn then emailing them individually",
    ("linkedin",       "hubspot"):         "manual CRM entry — finding contacts on LinkedIn then logging them in HubSpot",
    ("linkedin",       "salesforce"):      "manual CRM entry — researching on LinkedIn then recording in Salesforce",
    ("linkedin",       "pipedrive"):       "manual prospecting — moving leads from LinkedIn into Pipedrive manually",
    ("linkedin",       "google_sheets"):   "prospect tracking — researching contacts on LinkedIn then logging them to a spreadsheet",
    ("gmail",          "hubspot"):         "email-to-CRM logging — reading emails then manually updating HubSpot records",
    ("gmail",          "salesforce"):      "email-to-CRM logging — reading emails then manually updating Salesforce",
    ("gmail",          "pipedrive"):       "email-to-deal updates — reading emails then updating Pipedrive deals",
    ("gmail",          "google_sheets"):   "email-to-spreadsheet logging — reading emails and recording data manually",
    ("gmail",          "notion"):          "email-to-notes — reading emails and transcribing notes or action items",
    ("gmail",          "google_docs"):     "email-to-doc workflow — reading emails and drafting or updating documents",
    ("calendly",       "gmail"):           "booking confirmation loop — managing scheduling via Calendly then emailing confirmations",
    ("google_calendar","gmail"):           "calendar-to-email — checking calendar then sending follow-up or reminder emails",

    # Reporting & Data
    ("google_sheets",  "google_docs"):     "data-to-report pipeline — pulling data from Sheets and writing it into a document",
    ("google_sheets",  "google_slides"):   "data-to-presentation — copying data from Sheets into a presentation manually",
    ("google_sheets",  "gmail"):           "report distribution — compiling a spreadsheet then emailing it out",
    ("airtable",       "gmail"):           "database-to-email — reviewing Airtable records then sending manual emails",
    ("airtable",       "google_sheets"):   "duplicate data entry — copying data between Airtable and Google Sheets",
    ("hubspot",        "google_sheets"):   "CRM export workflow — pulling CRM data into a spreadsheet manually",
    ("salesforce",     "google_sheets"):   "CRM export workflow — copying Salesforce data into a spreadsheet",

    # Project Management
    ("gmail",          "jira"):            "email-to-ticket creation — reading emails and manually creating Jira tickets",
    ("gmail",          "trello"):          "email-to-task creation — reading emails and manually adding Trello cards",
    ("gmail",          "asana"):           "email-to-task creation — reading emails and creating Asana tasks",
    ("gmail",          "notion"):          "email-to-notes — reading emails and writing notes in Notion",
    ("jira",           "google_sheets"):   "ticket reporting — exporting Jira data into a spreadsheet manually",
    ("jira",           "slack_web"):       "ticket notification — updating Jira then manually messaging the team on Slack",
    ("notion",         "gmail"):           "brief-to-email — reading a Notion brief then composing related emails",
    ("notion",         "google_docs"):     "notes-to-doc — copying from Notion notes into a formal Google Doc",

    # Support & Customer Success
    ("gmail",          "zendesk"):         "email-to-ticket routing — reading customer emails and manually logging support tickets",
    ("gmail",          "intercom"):        "manual customer responses — reading support emails and replying in Intercom",
    ("zendesk",        "google_sheets"):   "support reporting — exporting ticket data into a spreadsheet",
    ("intercom",       "google_sheets"):   "customer data logging — copying conversation data from Intercom to Sheets",
}


# ─── ROI Calculations ─────────────────────────────────────────────────────────

def calculate_roi(
    pattern: Dict[str, Any],
    hourly_rate: float = DEFAULT_HOURLY_RATE,
    currency: str = DEFAULT_CURRENCY,
    currency_symbol: str = DEFAULT_CURRENCY_SYMBOL,
    hourly_rate_gbp: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Enrich a workflow pattern dict with monetary cost fields in any currency.
    Returns a new dict with all original fields + ROI additions.
    """
    rate = hourly_rate_gbp if hourly_rate_gbp is not None else hourly_rate
    weekly_hours  = pattern.get("total_time_hours_per_week", 0.0)
    weekly_cost   = round(weekly_hours * rate, 2)
    annual_cost   = round(weekly_cost * WORKING_WEEKS_PER_YEAR, 2)
    annual_hours  = round(weekly_hours * WORKING_WEEKS_PER_YEAR, 1)

    return {
        **pattern,
        "roi": {
            "currency":                   currency,
            "currency_symbol":            currency_symbol,
            "hourly_rate":                rate,
            "hourly_rate_gbp":            rate,  # backward compatibility
            "weekly_cost":                weekly_cost,
            "weekly_cost_gbp":            weekly_cost,  # backward compatibility
            "weekly_cost_label":          f"{currency_symbol}{weekly_cost:,.0f}/week",
            "annual_cost":                annual_cost,
            "annual_cost_gbp":            annual_cost,  # backward compatibility
            "annual_cost_label":          f"{currency_symbol}{annual_cost:,.0f}/year",
            "annual_hours":               annual_hours,
            "annual_hours_label":         f"{annual_hours:.0f} hrs/year",
            "automation_savings_pct":     80,  # conservative estimate for knowledge-work automation
            "automatable_hours_per_year":  round(annual_hours * 0.80, 1),
            "automatable_cost_per_year":   round(annual_cost  * 0.80, 2),
            "automatable_cost_label":      f"{currency_symbol}{annual_cost * 0.80:,.0f} recoverable/year",
        },
    }


# ─── LLM Context Generation ───────────────────────────────────────────────────

def generate_llm_context(pattern: Dict[str, Any]) -> str:
    """
    Produce a rich, deterministic natural-language description of what
    the workflow likely represents, based on app transition patterns.

    This gives an LLM grounded context without hallucination.
    """
    sequence = pattern.get("sequence", [])
    if not sequence:
        return "Unknown workflow pattern."

    lines: List[str] = []

    # Opening sentence
    app_chain = " → ".join(a.replace("_", " ").title() for a in sequence)
    lines.append(f"Workflow sequence: {app_chain}.")

    # Describe individual apps
    app_descs = [
        f"  • {app.replace('_',' ').title()}: {APP_DESCRIPTIONS.get(app, 'a business web application')}"
        for app in sequence
    ]
    lines.append("Apps involved:")
    lines.extend(app_descs)

    # Detect meaningful transitions
    found_archetypes: List[str] = []
    for i in range(len(sequence) - 1):
        pair = (sequence[i], sequence[i + 1])
        archetype = TRANSITION_ARCHETYPES.get(pair)
        if archetype:
            found_archetypes.append(archetype)

    if found_archetypes:
        lines.append("Inferred workflow type(s):")
        for arch in found_archetypes:
            lines.append(f"  • {arch.capitalize()}.")
    else:
        lines.append(
            f"Multi-application workflow involving {len(sequence)} tools "
            "with no precisely matched archetype — likely a custom internal process."
        )

    # Stats
    freq    = pattern.get("frequency", 0)
    dur     = pattern.get("avg_duration_minutes", 0)
    cost_lbl = pattern.get("roi", {}).get("annual_cost_label", "unknown")
    wk_hrs  = pattern.get("total_time_hours_per_week", 0)

    lines.append(
        f"Observed frequency: {freq} sessions matched. "
        f"Average duration per session: {dur} minutes. "
        f"Extrapolated weekly time cost: {wk_hrs:.1f} hours. "
        f"Estimated annual cost (at configured hourly rate): {cost_lbl}."
    )

    tier = pattern.get("opportunity_tier", "low")
    if tier == "high":
        lines.append(
            "Automation priority: HIGH. This workflow is a strong candidate for full automation — "
            "it is repetitive, multi-system, and consumes significant measurable time."
        )
    elif tier == "medium":
        lines.append(
            "Automation priority: MEDIUM. This workflow is a candidate for partial automation "
            "or tooling to accelerate the manual steps."
        )
    else:
        lines.append(
            "Automation priority: LOW. This pattern occurs infrequently or is short enough "
            "that partial optimisation may be more appropriate than full automation."
        )

    return "\n".join(lines)


# ─── Brief Builder ────────────────────────────────────────────────────────────

def build_intelligence_brief(
    patterns:         List[Dict[str, Any]],
    summary:          Dict[str, Any],
    hourly_rate:      float  = DEFAULT_HOURLY_RATE,
    currency:         str    = DEFAULT_CURRENCY,
    currency_symbol:  str    = DEFAULT_CURRENCY_SYMBOL,
    org_id:           str    = "org_demo",
    observation_days: int    = 7,
    hourly_rate_gbp:  Optional[float] = None,
) -> Dict[str, Any]:
    """
    Assemble the complete LLM-ready intelligence brief.
    Supports dynamic currency and hourly rate.
    """

    rate = hourly_rate_gbp if hourly_rate_gbp is not None else hourly_rate
    now    = datetime.now(timezone.utc)
    brief_id = "brief_" + hashlib.sha1(
        f"{org_id}{now.isoformat()}".encode()
    ).hexdigest()[:10]

    # ── Enrich all patterns with ROI ──────────────────────────────────────────
    enriched: List[Dict[str, Any]] = []
    for p in patterns:
        p_with_roi = calculate_roi(
            p,
            hourly_rate=rate,
            currency=currency,
            currency_symbol=currency_symbol,
        )
        p_with_roi["llm_context"] = generate_llm_context(p_with_roi)
        enriched.append(p_with_roi)

    # ── Aggregate financials ──────────────────────────────────────────────────
    total_weekly_cost  = sum(p["roi"]["weekly_cost"]  for p in enriched)
    total_annual_cost  = sum(p["roi"]["annual_cost"]  for p in enriched)
    total_recover_yr   = sum(p["roi"]["automatable_cost_per_year"] for p in enriched)
    total_weekly_hrs   = summary.get("total_time_mapped_minutes", 0) / 60
    high_opps          = [p for p in enriched if p.get("opportunity_tier") == "high"]
    top_pattern        = enriched[0] if enriched else None

    # ── Build brief ───────────────────────────────────────────────────────────
    brief: Dict[str, Any] = {
        "meta": {
            "brief_id":           brief_id,
            "org_id":             org_id,
            "generated_at":       now.isoformat(),
            "observation_days":   observation_days,
            "hourly_rate":        rate,
            "hourly_rate_gbp":    rate,
            "currency":           currency,
            "currency_symbol":    currency_symbol,
            "schema_version":     "4.0",
            "source":             "Dead Time Workflow Intelligence Engine",
        },

        "executive_summary": {
            "total_events_captured":         summary.get("total_events", 0),
            "total_sessions_detected":        summary.get("total_sessions", 0),
            "total_workflows_identified":     len(enriched),
            "apps_observed":                  summary.get("apps_seen", []),
            "total_time_mapped_label":        summary.get("total_time_mapped_label", "0m"),
            "total_time_mapped_hours":        round(total_weekly_hrs, 1),
            "currency":                       currency,
            "currency_symbol":                currency_symbol,
            "weekly_cost_across_workflows":   f"{currency_symbol}{total_weekly_cost:,.0f}",
            "annual_cost_across_workflows":   f"{currency_symbol}{total_annual_cost:,.0f}",
            "recoverable_annually":           f"{currency_symbol}{total_recover_yr:,.0f}",
            "high_priority_opportunities":    len(high_opps),
            "top_opportunity": {
                "name":           top_pattern["name"]                     if top_pattern else None,
                "sequence":       top_pattern["sequence"]                 if top_pattern else [],
                "weekly_cost":    top_pattern["roi"]["weekly_cost_label"] if top_pattern else None,
                "annual_cost":    top_pattern["roi"]["annual_cost_label"] if top_pattern else None,
                "frequency":      top_pattern["frequency"]                if top_pattern else 0,
            } if top_pattern else None,
        },

        "workflows": enriched,

        "llm_prompt": _build_llm_prompt(enriched, total_annual_cost, org_id, currency_symbol),
    }

    return brief


# ─── LLM Prompt Builder ───────────────────────────────────────────────────────

def _build_llm_prompt(
    enriched: List[Dict[str, Any]],
    total_annual_cost: float,
    org_id: str,
    currency_symbol: str = "₹",
) -> str:
    """
    Returns a complete, copy-paste-ready system+user prompt for LLM analysis.
    The JSON brief can be appended directly after this prompt.
    """
    workflow_count = len(enriched)
    high_count     = sum(1 for p in enriched if p.get("opportunity_tier") == "high")

    return f"""You are a senior workflow automation consultant specialising in B2B knowledge-worker productivity.

You have been provided with a structured intelligence brief generated by Dead Time, a continuous workflow-observation platform.
The brief was produced using deterministic signal processing — no AI was used in its generation. All figures are based on observed behaviour.

The organisation (ID: {org_id}) has {workflow_count} recurring workflow patterns identified across their observed browser activity.
{high_count} of these are classified HIGH priority based on frequency × time cost. Estimated total annual cost: {currency_symbol}{total_annual_cost:,.0f}.

Your task is to analyse the JSON brief below and provide:

1. HIGHEST-ROI AUTOMATION OPPORTUNITY
   - Which single workflow should be automated first, and why
   - Name the specific tool(s) recommended (Zapier, Make, n8n, Python script, dedicated SaaS)
   - Step-by-step: what exactly would be automated
   - Conservative estimate of hours saved per week post-automation
   - Estimated payback period (automation setup cost vs annual savings)

2. AUTOMATION COMPLEXITY ASSESSMENT (for each HIGH/MEDIUM pattern)
   - Complexity: Low / Medium / High
   - Reason: what makes it easy or hard to automate
   - Required integrations: which app APIs are needed

3. EXECUTIVE PITCH (3 sentences)
   - A compelling pitch to a non-technical decision-maker explaining the value of automating the top opportunity

4. QUICK WINS (3 items)
   - Three changes the user could make manually TODAY (no automation needed) that would immediately reduce time waste

Format your response as structured JSON so it can be consumed by a downstream report renderer.

---BEGIN INTELLIGENCE BRIEF JSON---"""
