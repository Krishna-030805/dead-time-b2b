# Dead Time B2B — Master Project Documentation & Technical Specification

> **Continuous Workflow Intelligence, Deterministic Pattern Mining, and Closed-Loop Automation Engine**

---

## 1. Executive Summary & Value Proposition

### What is Dead Time?
**Dead Time B2B** is an enterprise process intelligence and workflow automation platform. It quietly observes knowledge-worker activity across web applications, deterministically detects repetitive cross-app routines (without recording sensitive keystrokes or passwords), quantifies the annual payroll cost of those workflows, and generates ready-to-run automation blueprints (n8n, Make.com, Python scripts).

### The Business Problem
In knowledge-work companies (agencies, B2B sales teams, customer ops, recruitment firms, e-commerce ops), knowledge workers spend **15% to 30% of their day on repetitive "dead time"**:
- Copy-pasting data between CRM, email, and spreadsheets.
- Manually looking up records across multiple browser tabs.
- Updating databases, tracking spreadsheets, or status dashboards.

Business leaders know automation saves money, but they do not know:
1. *Which* workflows are happening repeatedly across their team.
2. *How many hours* are truly wasted per week.
3. *What the ROI* and payback period would be if automated.

### The Solution: Zero-Friction Closed Loop
1. **Observe:** Lightweight Chrome Extension captures privacy-safe telemetry events.
2. **Reconstruct:** Backend groups events into sessions using a 30-minute inactivity threshold.
3. **Mine:** An n-gram pattern mining algorithm discovers recurring cross-app sequences.
4. **Quantify:** An ROI engine calculates exact weekly and annual financial waste based on hourly wages.
5. **Advise:** LLM (Google Gemini Flash with multi-model fallback) produces grounded automation recommendations.
6. **Execute & Export:** Human-in-the-loop review approves blueprints, simulates payloads via Sandbox Dry-Run, and exports turnkey workflows to n8n, Make.com, or standalone async Python.
7. **Verify:** A Before vs. After ROI tracker verifies real-world realized savings.

---

## 2. System Architecture & Layers

Dead Time B2B is engineered as an 8-layer modular pipeline:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LAYER 1: TELEMETRY INGESTION                    │
│   Chrome Extension (Manifest v3) -> Background Worker -> POST /events  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  LAYER 2: DETERMINISTIC PATTERN MINER                  │
│    Session Reconstruction (30m gap) -> N-gram Mining (2..6) -> Ranking │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: ROI QUANTIFICATION ENGINE                  │
│  Hourly Rate Extrapolation -> 48-Wk Annual Cost -> 80% Recovery Model  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      LAYER 4: LLM INSIGHT ENGINE                       │
│    Gemini Multi-Model Fallback Pool -> Strict Pydantic JSON Schema     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER 5: BLUEPRINTING & EXPORT ENGINE                │
│    Human-in-the-Loop Gateway -> Sandbox Dry-Run -> n8n / Make / Python │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER 6: CLOSED-LOOP EXECUTION LOGS                  │
│         Execution Dispatcher -> Success/Failure Telemetry Logs         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER 7: BEFORE VS AFTER ROI TRACKER                 │
│      Baseline Hours vs Deployed Savings -> Realized Annual Payroll     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     LAYER 8: NEXT.JS SAAS DASHBOARD                    │
│   5-Tab Executive UI -> Multi-Currency Switcher -> Multi-Tenant Orgs   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Deep Dive

### 3.1 Telemetry Collection (`/extension`)
- **Technology:** Chrome Extension (Manifest V3), Vanilla JavaScript.
- **Privacy Architecture:**
  - **Zero Form Extraction:** Password inputs, form inputs, and keystrokes are strictly ignored.
  - **Sanitized Metadata:** Captures only high-level signals: `application` (e.g., `gmail`, `hubspot`, `google_sheets`, `linkedin`), `action_type` (`open`, `dwell`, `click`), `object_type` (`page`, `button`), and sanitised element labels.
  - **Dwell Time:** Tracks active engagement duration; bounces under 3 seconds are discarded.
  - **Session Management:** Client generates a session ID that automatically rolls over when an inactivity gap of >30 minutes occurs.
  - **Multi-Tenancy:** Supports `org_id` and `user_id` storage so multiple client organizations can be partitioned on the same backend.

### 3.2 Backend API & Core Engines (`/backend`)
- **Framework:** FastAPI (Python 3.10+), SQLAlchemy, SQLite (`deadtime_b2b.db`) / PostgreSQL compatible.
- **Deployment:** Render (`https://dead-time-backend.onrender.com`).
- **Core Modules:**
  1. `models.py`: Database entities:
     - `Event`: Raw telemetry events with timestamps, application, action, and JSON metadata.
     - `WorkflowSession`: Reconstructed work sessions bounded by inactivity gaps.
     - `DetectedBrief`: Persisted intelligence reports with financial totals.
     - `AutomationBlueprint`: Generated execution plans with lifecycle states (`pending_review`, `approved`, `rejected`, `deployed`).
     - `AutomationExecution`: Real execution runtime logs for deployed automations.
  2. `workflow_detector.py`: Pure deterministic Python algorithm.
     - Sorts events chronologically.
     - Splits into sessions on gaps $> 30$ minutes.
     - Normalizes sessions into sequential app transitions (e.g. `["gmail", "linkedin", "google_sheets"]`).
     - Extracts all sub-sequences (n-grams of length 2 to 6).
     - Ranks patterns by frequency and time cost: $\text{Weekly Cost} = \text{Frequency} \times \text{Avg Duration} \times \text{Extrapolation Factor}$.
  3. `roi_engine.py`:
     - Multi-currency mathematical model (INR `₹`, USD `$`, GBP `£`, EUR `€`).
     - Calculates annual costs assuming a 48-week working year.
     - Assumes a conservative 80% automatable time recovery benchmark.
     - Ranks opportunities into High ($\ge 3$ hrs/wk), Medium ($\ge 1$ hr/wk), and Low tiers.
  4. `llm_engine.py`:
     - Connects to Google Gemini via API.
     - Features an automatic resilient fallback model pool (`gemini-3.1-flash-lite`, `gemini-3.5-flash-lite`, `gemini-3.5-flash`, `gemini-3.6-flash`, `gemini-3.8-flash`).
     - Enforces strict Pydantic JSON decoding (`TopOpportunity`, `QuickWin`, `WorkflowAssessment`).
     - Includes a zero-crash heuristic rule engine fallback if API keys or network fail.
  5. `export_engine.py`:
     - **n8n Exporter:** Generates valid, importable n8n JSON nodes and connection trees.
     - **Make.com Exporter:** Generates valid Make scenario blueprints.
     - **Python Exporter:** Generates standalone executable async Python scripts with environment variables.
  6. `pdf_engine.py`:
     - Generates pixel-perfect executive PDF audit reports using headless printing or browser print fallback.

### 3.3 Executive Dashboard (`/frontend`)
- **Technology:** Next.js (App Router), Vanilla CSS Design System, Responsive layout.
- **Deployment:** Vercel (`https://dead-time-b2b.vercel.app/`).
- **Features & Tabs:**
  - **Header & Stats Strip:** Global currency selector (INR, USD, GBP, EUR), editable hourly wage, real-time realized savings ticker, and multi-tenant organization selector (`org_id`).
  - **Workflows Panel:** Ranked cards of discovered routines, sequence flow chips, confidence scores, and one-click "Generate Blueprint".
  - **AI Insights Panel:** Gemini-generated executive pitch, top automation target with step-by-step implementation, quick wins, and risk assessments.
  - **Blueprint Review Panel:** Human-in-the-Loop approval gateway (Approve, Reject, Deploy), interactive **Sandbox Dry-Run Modal** (simulating payload transformations without calling production APIs), and instant exports (n8n JSON, Make JSON, Python Script).
  - **ROI Impact Tracker:** Before vs. After analytics comparing pre-automation baseline hours against active deployment logs.
  - **Audit Trail Panel:** Granular inspection of reconstructed user sessions and raw telemetry event streams.

---

## 4. Complete API Specification

| HTTP Method | Route | Description | Layer |
|---|---|---|---|
| `POST` | `/events` | Ingests telemetry event from Chrome Extension | Layer 1 |
| `GET` | `/events` | Lists raw events (filtered by `org_id` and `limit`) | Layer 1 |
| `GET` | `/organizations` | Returns all unique active organization identifiers | Layer 1 |
| `GET` | `/health` | System health check (used by UptimeRobot) | Meta |
| `GET` | `/sessions` | Lists reconstructed work sessions | Layer 2 |
| `GET` | `/workflows/detected` | Lists deterministic recurring workflow patterns | Layer 2 |
| `GET` | `/workflows/summary` | Summary metrics of detected patterns | Layer 2 |
| `GET` | `/workflows/brief` | Returns complete LLM-ready JSON intelligence brief | Layer 3 |
| `GET` | `/workflows/report` | Renders a styled standalone HTML intelligence report | Layer 3 |
| `GET` | `/workflows/report/pdf` | Downloads or prints the executive PDF report | Layer 3 |
| `GET` | `/workflows/ai-analysis` | Returns Gemini structured recommendations | Layer 4 |
| `POST` | `/blueprints/generate` | Generates an automation plan for a pattern ID | Layer 5 |
| `GET` | `/blueprints` | Lists all generated blueprints and their approval status | Layer 5 |
| `POST` | `/blueprints/{id}/review` | Approves or rejects a blueprint (`action: approve/reject`) | Layer 5 |
| `POST` | `/blueprints/{id}/dry-run` | Simulates data payload transformations in sandbox | Layer 5 |
| `GET` | `/blueprints/{id}/export/n8n` | Downloads ready-to-import n8n workflow JSON | Layer 5 |
| `GET` | `/blueprints/{id}/export/make` | Downloads ready-to-import Make.com scenario JSON | Layer 5 |
| `GET` | `/blueprints/{id}/export/python` | Downloads standalone async Python script | Layer 5 |
| `POST` | `/engine/deploy/{id}` | Deploys an approved blueprint into production | Layer 6 |
| `GET` | `/analytics/roi-impact` | Before vs. After realized financial savings report | Layer 7 |
| `POST` | `/demo/seed` | Seeds rich enterprise demonstration dataset | Meta |

---

## 5. Deployment & Production Setup

### Live Production Endpoints
- **Frontend Dashboard:** `https://dead-time-b2b.vercel.app/`
- **Backend API:** `https://dead-time-backend.onrender.com`
- **Interactive Swagger Docs:** `https://dead-time-backend.onrender.com/docs`
- **Health Check Monitor:** `https://dead-time-backend.onrender.com/health` (monitored by UptimeRobot every 5 mins to prevent free-tier spin-down).

### Running Locally
Run `start.bat` on Windows or:
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:3000
```

### Installing the Chrome Extension
1. Open Google Chrome and navigate to `chrome://extensions`.
2. Toggle on **Developer mode** (top right switch).
3. Click **Load unpacked** and select the `dead-time-b2b/extension` folder.
4. Click the Dead Time puzzle icon to verify the status indicator displays **Online**.

---

## 6. Commercial Go-to-Market (GTM) Strategy

### Target Market (Ideal Customer Profile)
- **Company Size:** 5 to 50 employees (fast decision cycles without corporate IT hurdles).
- **Target Roles:** Founder, CEO, COO, VP of Operations, Head of RevOps.
- **Top Converting Sectors:**
  1. Digital Marketing & SEO Agencies (reporting, keyword research, sheet syncing).
  2. Recruiting & Staffing Firms (LinkedIn sourcing to ATS/CRM data entry).
  3. E-commerce & Amazon/Shopify Agencies (order tracking, SKU updates, catalog sync).
  4. B2B Lead Gen & Sales Development Agencies (lead enrichment and list building).

### Sales Playbook: "The 3-Day Efficiency Audit"
1. **The Hook:** Don't sell software or employee tracking. Offer a **Free 3-Day Workflow Efficiency Audit**.
2. **The Pilot:** Client's team loads the extension ZIP for 3 business days.
3. **The Presentation:** Open the live dashboard or export the PDF report showing the exact dollar amount lost per year to repetitive routines.
4. **Monetization:**
   - **Service / Retainer:** Charge $1,000–$3,000 to build the Make/n8n/Python automations generated by Dead Time.
   - **Continuous SaaS:** Charge $99–$299/month for perpetual team monitoring and optimization discovery.
