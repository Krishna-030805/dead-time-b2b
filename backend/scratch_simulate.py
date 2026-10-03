import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import urllib.request
import json
import time
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8002/events"
USER_ID = "simulated_employee_001"

def send_event(app, action, obj_type=None, session_id="sess_sim_1", ts_offset_minutes=0):
    ts = (datetime.now() - timedelta(minutes=ts_offset_minutes)).isoformat()
    data = {
        "user_id": USER_ID,
        "timestamp": ts,
        "application": app,
        "action_type": action,
        "object_type": obj_type,
        "session_id": session_id,
        "metadata": {}
    }
    
    req = urllib.request.Request(BASE_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Error sending event: {e}")

# We will simulate 3 days of work
offset = 3 * 24 * 60 # start 3 days ago

def simulate_noise(session_id, offset):
    apps = ["slack", "gmail", "github", "notion", "google_calendar"]
    for _ in range(random.randint(2, 5)):
        app = random.choice(apps)
        send_event(app, "read", "page", session_id, offset)
        offset -= random.randint(1, 5)
    return offset

# Pattern 1: Customer Support Triage (Zendesk -> Jira -> Slack -> Zendesk)
# Happens ~8 times a day
def simulate_support_workflow(session_id, offset):
    send_event("zendesk", "read", "ticket", session_id, offset)
    offset -= 2
    send_event("jira", "create", "issue", session_id, offset)
    offset -= 3
    send_event("slack", "send", "message", session_id, offset)
    offset -= 1
    send_event("zendesk", "reply", "ticket", session_id, offset)
    offset -= 2
    return offset

# Pattern 2: Invoice Processing (Gmail -> Xero -> Google Drive)
# Happens ~5 times a day
def simulate_invoice_workflow(session_id, offset):
    send_event("gmail", "download", "attachment", session_id, offset)
    offset -= 2
    send_event("xero", "create", "invoice", session_id, offset)
    offset -= 4
    send_event("google_drive", "upload", "file", session_id, offset)
    offset -= 1
    return offset

print("Generating synthetic workflows...")

for day in range(3):
    session_id = f"sess_day_{day}"
    offset = (3 - day) * 24 * 60
    
    # Morning block
    offset = simulate_noise(session_id, offset)
    for _ in range(4): # 4 support tickets morning
        offset = simulate_support_workflow(session_id, offset)
        offset = simulate_noise(session_id, offset)
        
    for _ in range(2): # 2 invoices morning
        offset = simulate_invoice_workflow(session_id, offset)
        offset = simulate_noise(session_id, offset)
        
    # Break gap to split session? Actually, workflow detector splits by 30 mins gap automatically.
    # Let's force a gap
    offset -= 60 
    session_id = f"sess_day_{day}_afternoon"
    
    # Afternoon block
    offset = simulate_noise(session_id, offset)
    for _ in range(4): # 4 support tickets afternoon
        offset = simulate_support_workflow(session_id, offset)
        offset = simulate_noise(session_id, offset)
        
    for _ in range(3): # 3 invoices afternoon
        offset = simulate_invoice_workflow(session_id, offset)
        offset = simulate_noise(session_id, offset)

print("Synthetic data injected.")

# First, inspect the deterministic Layer 2 detected patterns
print("\nFetching Layer 2 Detected Patterns...")
try:
    req_det = urllib.request.Request("http://localhost:8002/workflows/detected")
    patterns = json.loads(urllib.request.urlopen(req_det).read().decode('utf-8'))
    print(f"Found {len(patterns)} recurring workflow pattern(s):")
    for p in patterns:
        seq_str = " -> ".join(p.get("sequence", []))
        print(f"  * [{p.get('opportunity_tier', '').upper()}] {seq_str}")
        print(f"    Seen in {p.get('frequency')} sessions, {p.get('total_time_hours_per_week')} hrs/week estimated ({p.get('time_cost_label')})")
except Exception as e:
    print(f"Error fetching detected patterns: {e}")

# Now let's fetch the AI insights from Gemini
print("\nRequesting Layer 4 AI Insights (calling Gemini)...")
req = urllib.request.Request("http://localhost:8002/workflows/ai-analysis?hourly_rate=60")
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    print("\n=================== AI INSIGHTS ===================")
    print(f"Generated via: {data.get('model')}")
    insights = data.get("insights", {})
    
    print("\n[Executive Pitch]:")
    print(insights.get("executive_pitch", ""))
    
    print("\n[Top Opportunity]:")
    top = insights.get("top_opportunity", {})
    print(f"Workflow: {top.get('workflow_name')}")
    print(f"Recommended Tool: {top.get('recommended_tool')}")
    print(f"Why this tool: {top.get('why_this_tool')}")
    print(f"What gets automated: {top.get('what_gets_automated')}")
    print("Implementation Steps:")
    for i, step in enumerate(top.get("automation_steps", [])):
        print(f"  {i+1}. {step}")
    print(f"Estimated Time Saved: {top.get('estimated_hours_saved_per_week')} hrs/week")
    print(f"Payback Period: {top.get('payback_period_label')}")
    print(f"Complexity: {top.get('complexity')}")
    print(f"Required APIs: {', '.join(top.get('required_apis', []))}")
    
    print("\n[Quick Wins]:")
    for qw in insights.get("quick_wins", []):
        print(f"  * {qw.get('title')} ({qw.get('time_saved')}): {qw.get('description')}")
        
    print("\n[Workflow Assessments]:")
    for wa in insights.get("workflow_assessments", []):
        print(f"  * {wa.get('workflow_name')} [Complexity: {wa.get('complexity')}]:")
        print(f"    Approach: {wa.get('automation_approach')}")
        print(f"    Required Integrations: {', '.join(wa.get('required_integrations', []))}")
        
except Exception as e:
    print(f"Failed to fetch insights: {e}")

