import urllib.request, json, sys

BASE = "http://127.0.0.1:8002"

def get(path):
    r = urllib.request.urlopen(BASE + path)
    return r.status, r.read()

print("=== Layer 3 Endpoint Verification ===\n")

# Health
s, b = get("/health")
h = json.loads(b)
print("HEALTH:", h)
assert h["version"] == "4.0.0", f"version mismatch: {h['version']}"
assert h["layers_active"] == [1, 2, 3]

# Root
s, b = get("/")
print(f"ROOT HTML: {s}, {len(b)} bytes")
assert s == 200

# Events
s, b = get("/events")
evs = json.loads(b)
print(f"EVENTS: {len(evs)} total")

# Sessions
s, b = get("/sessions")
sess = json.loads(b)
print(f"SESSIONS: {len(sess)} detected")

# Patterns
s, b = get("/workflows/detected")
wf = json.loads(b)
print(f"PATTERNS: {len(wf)} detected")

# Brief
s, b = get("/workflows/brief?hourly_rate=50&org_id=org_demo")
brief = json.loads(b)
print("\n=== INTELLIGENCE BRIEF ===")
print("brief_id:", brief["meta"]["brief_id"])
print("schema_version:", brief["meta"]["schema_version"])
ex = brief["executive_summary"]
print("events:", ex["total_events_captured"])
print("sessions:", ex["total_sessions_detected"])
print("patterns:", ex["total_workflows_identified"])
print("weekly_cost:", ex["weekly_cost_across_workflows"])
print("annual_cost:", ex["annual_cost_across_workflows"])
print("recoverable:", ex["recoverable_annually"])
print("top_opportunity:", str(ex["top_opportunity"]).encode('ascii', 'replace').decode('ascii'))
assert "llm_prompt" in brief, "llm_prompt missing from brief"
print("\nLLM prompt (first 200 chars):")
print(brief["llm_prompt"][:200])

print("\nWorkflows in brief:")
for p in brief["workflows"][:5]:
    roi = p.get("roi", {})
    tier = p.get("opportunity_tier","?").upper()
    name = p.get("name","?")
    freq = p.get("frequency","?")
    avg  = p.get("avg_duration_minutes","?")
    wc   = roi.get("weekly_cost_label","?")
    ac   = roi.get("annual_cost_label","?")
    rec  = roi.get("automatable_cost_label","?")
    ctx  = p.get("llm_context","")[:80]
    print(f"  [{tier}] {name}")
    print(f"    freq={freq}  avg={avg}m  weekly={wc}  annual={ac}  recover={rec}")
    print(f"    context: {ctx}")
    assert "roi" in p, "roi missing from pattern"
    assert "llm_context" in p, "llm_context missing"

# Report HTML
s, b = get("/workflows/report?hourly_rate=50")
print(f"\nREPORT HTML: {s}, {len(b)} bytes")
assert s == 200
assert b"Intelligence Brief" in b or b"Dead Time" in b

print("\n=== ALL CHECKS PASSED ===")
