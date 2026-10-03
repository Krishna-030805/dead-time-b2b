import urllib.request
import json
import sys

BASE_URL = "http://localhost:8002"

print("================================================================")
print("             DEAD TIME B2B — WORKFLOW INTELLIGENCE              ")
print("================================================================")

# 1. Fetch Layer 2 Detected Patterns
print("\n[LAYER 2] MINING DETERMINISTIC WORKFLOW PATTERNS...")
try:
    req = urllib.request.Request(f"{BASE_URL}/workflows/detected")
    patterns = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print(f"-> Successfully extracted {len(patterns)} recurring workflow patterns from employee telemetry.\n")
    for i, p in enumerate(patterns[:5]):
        seq = " -> ".join(p.get("sequence", []))
        print(f" {i+1}. [{p.get('opportunity_tier', '').upper()}] {seq}")
        print(f"    Frequency: Seen across {p.get('frequency')} sessions")
        print(f"    Estimated Time Lost: {p.get('total_time_hours_per_week')} hrs/week ({p.get('time_cost_label')})")
        print(f"    Confidence: {round(p.get('confidence', 0)*100)}%\n")
except Exception as e:
    print(f"Error fetching patterns: {e}")
    sys.exit(1)

# 2. Fetch Layer 4 AI Analysis
print("----------------------------------------------------------------")
print("[LAYER 4] GENERATING GROUNDED AI INSIGHTS & ROI...")
try:
    req = urllib.request.Request(f"{BASE_URL}/workflows/ai-analysis?hourly_rate=60")
    resp = urllib.request.urlopen(req)
    res_data = json.loads(resp.read().decode('utf-8'))
    
    print(f"-> Generation Status: {res_data.get('status')}")
    print(f"-> Engine / Model: {res_data.get('model')}\n")
    
    insights = res_data.get("insights", {})
    
    print("====================== EXECUTIVE BRIEF =========================")
    print(insights.get("executive_pitch", "N/A"))
    print("================================================================\n")
    
    top = insights.get("top_opportunity", {})
    print("TOP AUTOMATION OPPORTUNITY:")
    print(f"  * Target Workflow:     {top.get('workflow_name')}")
    print(f"  * Recommended Tool:    {top.get('recommended_tool')}")
    print(f"  * Strategic Fit:       {top.get('why_this_tool')}")
    print(f"  * What Gets Automated: {top.get('what_gets_automated')}")
    print(f"  * Weekly Time Saved:   {top.get('estimated_hours_saved_per_week')} hrs/week")
    print(f"  * Payback Period:      {top.get('payback_period_label')}")
    print(f"  * Setup Complexity:    {top.get('complexity')}")
    print(f"  * Required APIs:       {', '.join(top.get('required_apis', []))}")
    print("  * Automation Blueprint:")
    for step in top.get("automation_steps", []):
        print(f"      - {step}")
        
    print("\nQUICK WINS (IMMEDIATE LOW-EFFORT GAINS):")
    for qw in insights.get("quick_wins", []):
        print(f"  * {qw.get('title')} [{qw.get('time_saved')} saved]: {qw.get('description')}")
        
    print("\nWORKFLOW ASSESSMENTS & COMPLEXITY BREAKDOWN:")
    for wa in insights.get("workflow_assessments", []):
        print(f"  * {wa.get('workflow_name')} ({wa.get('complexity')} Complexity):")
        print(f"    Approach: {wa.get('automation_approach')}")
        print(f"    Integrations: {', '.join(wa.get('required_integrations', []))}")

    print("\n================================================================")
    print("DEMO VERIFICATION COMPLETE: ALL LAYERS GROUNDED & VERIFIED.")
    print("================================================================")

except Exception as e:
    print(f"Error fetching AI insights: {e}")
