# Dead Time B2B — Master Project Documentation & System Reference
*The Complete Technical, Operational, and Commercial Blueprint for Engineers, Operators, and LLMs.*

---

## 📑 Table of Contents
1. [Executive Summary & Core Philosophy](#1-executive-summary--core-philosophy)
2. [The Two-Phase Commercial & Operating Model](#2-the-two-phase-commercial--operating-model)
   - [Phase 1: Workflow Efficiency Audit (Discovery & Quantification)](#phase-1-workflow-efficiency-audit-discovery--quantification)
   - [Phase 2: Automation Implementation & Continuity Retainer](#phase-2-automation-implementation--continuity-retainer)
3. [System Architecture & The 11 Functional Layers](#3-system-architecture--the-11-functional-layers)
4. [Data Models & Mathematical Formulations](#4-data-models--mathematical-formulations)
   - [Session Reconstruction Algorithm](#session-reconstruction-algorithm)
   - [N-Gram Sequence Pattern Mining](#n-gram-sequence-pattern-mining)
   - [Financial & ROI Quantification Formulas](#financial--roi-quantification-formulas)
5. [Complete REST API Specification](#5-complete-rest-api-specification)
6. [Component Deep Dive](#6-component-deep-dive)
   - [Chrome Telemetry Extension (Manifest V3)](#a-chrome-telemetry-extension-manifest-v3)
   - [FastAPI Python Backend & Algorithmic Engines](#b-fastapi-python-backend--algorithmic-engines)
   - [Next.js 14 Executive Intelligence Dashboard](#c-nextjs-14-executive-intelligence-dashboard)
7. [Cloud Deployment & Zero-Cost Infrastructure](#7-cloud-deployment--zero-cost-infrastructure)
8. [Go-To-Market, Sales & Client Onboarding Playbook](#8-go-to-market-sales--client-onboarding-playbook)
9. [Security, Privacy & Compliance Guarantees](#9-security-privacy--compliance-guarantees)
10. [Quick-Start Development Guide](#10-quick-start-development-guide)

---

## 1. Executive Summary & Core Philosophy

### What is Dead Time B2B?
**Dead Time B2B** is an automated enterprise workflow intelligence, telemetry audit, and automation orchestration platform. It continuously observes how knowledge workers interact with web-based SaaS tools (Slack, Jira, Zendesk, Salesforce, Google Sheets, HubSpot, GitHub, Notion, etc.), mathematically reconstructs cross-application work patterns, quantifies the exact financial payroll wasted on repetitive manual actions ("dead time"), generates human-approved automation blueprints (n8n, Make.com, Python), and tracks verified post-deployment realized ROI.

### Core Problem
B2B companies spend millions on payroll. The average knowledge worker loses **15% to 30% of their day (20–40 hours per week across a 10-person team)** copy-pasting data between disconnected browser tabs, manually reconciling tickets, or moving records from form to spreadsheet. 
- Traditional consulting firms charge $50,000+ for manual human interviews that are slow, inaccurate, and biased.
- Monitoring software ("bossware") feels invasive, tracks keystrokes/screenshots, and fails to identify automatable workflows.
- Dead Time bridges this gap: **Zero invasive spyware + 100% mathematical workflow telemetry + instant exportable automation scripts.**

### Core Philosophy
$$\text{Observe Silently} \longrightarrow \text{Quantify in Currency} \longrightarrow \text{Synthesize Blueprints} \longrightarrow \text{Deploy with Human Gate} \longrightarrow \text{Verify Realized ROI}$$

---

## 2. The Two-Phase Commercial & Operating Model

Dead Time operates on a high-converting, low-friction **Two-Phase B2B Engagement Model**:

```
┌────────────────────────────────────────────────────────┐
│  PHASE 1: WORKFLOW EFFICIENCY AUDIT (Discovery)        │
│  - 3 to 14 day telemetry capture via Chrome Extension  │
│  - Pattern reconstruction & N-gram mining              │
│  - Deliverable: Executive ROI Audit (PDF/HTML)         │
│  - Revenue: Free Pilot hook OR Paid Audit ($600/₹49k)  │
└───────────────────────────┬────────────────────────────┘
                            │ Proves Hard Dollar Waste
                            ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 2: AUTOMATION & CONTINUITY RETAINER             │
│  - Implementation of top blueprints (n8n/Make/Python)  │
│  - Sandbox dry-run testing & human sign-off            │
│  - Live deployment & Closed-Loop ROI tracking          │
│  - Revenue: Build Fee ($1.5k–$5k) + Retainer ($199/mo) │
└────────────────────────────────────────────────────────┘
```

### Phase 1: Workflow Efficiency Audit (Discovery & Quantification)
* **Goal:** Land inside the client's operations with zero friction, establish trust, and provide undeniable data proving how much money their current manual processes are wasting.
* **Duration:** 3 to 14 business days.
* **Delivery Mechanism:** Private pilot ZIP file loaded unpacked into Google Chrome (`chrome://extensions`) on 3 to 10 key employee machines.
* **Telemetry Collected:** Non-invasive browser navigation events, active domains, application context, session durations, and sequence flows. (No keystrokes, no passwords, no form inputs, no screenshots).
* **Deliverables:**
  1. **Executive Audit Report (Boardroom PDF & Interactive HTML):** Identifies top 3–5 recurring cross-app loops, frequency, hourly loss, and annual payroll cost.
  2. **AI Executive Insights Brief:** Highlighting the #1 automation priority, payback period (in weeks), recommended tech stack, and zero-code quick wins.
* **Commercial Options:**
  - **Option A (Free Hook):** 100% Free 3-Day Pilot used as a foot-in-the-door strategy for warm leads and agencies.
  - **Option B (Paid Audit):** Flat fee of **$600 / ₹49,000** for a full 14-day comprehensive diagnostic across 5–10 seats (deductible from Phase 2 fees).

### Phase 2: Automation Implementation & Continuity Retainer
* **Goal:** Monetize the high-value findings from Phase 1 by implementing the recommended automations and providing continuous workflow governance.
* **Deliverables:**
  1. **Turnkey Automation Deployment:** Converting the generated Dead Time blueprints into live, production-grade workflows (n8n JSON scenarios, Make.com scenarios, or async Python worker scripts).
  2. **Human-in-the-Loop Governance:** Sandboxed dry-run testing where operators inspect payload transformations before enabling live API writes.
  3. **Continuous ROI Closed-Loop Verification:** Access to the Dead Time dashboard tracking before-vs-after manual hours, automation execution success rates, and verified realized savings.
* **Pricing & Revenue Structure:**
  - **Implementation Setup Fee:** **$1,000 – $3,500 (₹75,000 – ₹2,50,000)** flat fee per automated workflow package (typically 2–4 core cross-app loops).
  - **Continuity SaaS Retainer:** **$199 – $499/month (or $19–$39/seat/month)** for continuous monitoring, drift detection (spotting when workflows break or change), monthly ROI reports, and new bottleneck discovery.

---

## 3. System Architecture & The 11 Functional Layers

The platform is engineered into 11 distinct, decoupled functional layers spanning client browser, cloud API, pattern engines, and the executive UI:

```
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 1] Chrome MV3 Telemetry Extension (Private Pilot ZIP / Web Store)  │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ HTTP POST /events (Batched JSON)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 2] FastAPI Cloud Backend & Session Splitter (30-min Inactivity)   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
┌───────────────────────────────┐               ┌───────────────────────────┐
│ [Layer 3] N-Gram Pattern      │               │ [Layer 4] Financial ROI   │
│ Mining & Subsequence Matcher  │               │ Engine & Currency Matrix  │
└─────────────┬─────────────────┘               └─────────────┬─────────────┘
              └───────────────────────┬───────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 5] Gemini AI Executive Intelligence & Recommendation Engine        │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 6] Blueprint Generator & Multi-Engine Exporter (n8n / Make / Py)   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 7] Human-in-the-Loop Review Gateway & Sandbox Dry-Run Simulator   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 8] Automation Execution Engine & Audit Trail                       │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 9] Report Generator (Boardroom PDF & Standalone HTML)              │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 10] Next.js 14 Multi-Tenant Dashboard (Live Cloud UI on Vercel)    │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ [Layer 11] Closed-Loop Realized ROI Tracker (Before vs After Verification)│
└───────────────────────────────────────────────────────────────────────────┘
```

### Layer Breakdown
* **Layer 1 (Ingestion):** Chrome Extension (Manifest V3) running a background service worker. Buffers tab transitions, window focus changes, and application domain switches.
* **Layer 2 (Sessionization):** Ingests raw telemetry events into SQLite/PostgreSQL. Splits continuous event streams into distinct sessions based on a 30-minute inactivity threshold.
* **Layer 3 (Pattern Recognition):** Algorithmic n-gram extraction (lengths 2 to 5) across reconstructed sessions. Identifies recurring sequential application transitions with confidence scoring.
* **Layer 4 (Financial Quantification):** Extrapolates observed sample frequencies across a standard 7-day week and 48-week working year. Applies configurable worker hourly rates across global currencies (₹ INR, $ USD, £ GBP, € EUR).
* **Layer 5 (AI Intelligence):** Synthesizes workflow briefs into Google Gemini prompts, returning structured analysis: top ROI opportunity, recommended automation tool, quick-hit operational wins, and payback timelines.
* **Layer 6 (Blueprint Generation & Export):** Converts detected abstract patterns into concrete, executable automation templates for **n8n**, **Make.com**, and standalone **Python asyncio** scripts.
* **Layer 7 (Human Governance & Dry-Run):** Enforces an approval state (`pending_review` $\to$ `approved` $\to$ `deployed`). Includes a simulated pipeline dry-run that tests transformations against mock data without writing to third-party APIs.
* **Layer 8 (Execution Engine):** Triggers and manages local or webhook-based execution of approved blueprints, logging output, runtime, and status.
* **Layer 9 (Reporting Engine):** Compiles executive summaries into downloadable, high-fidelity PDFs (via WeasyPrint / Chrome headless) and self-contained HTML briefs with one-click print styling.
* **Layer 10 (Presentation Dashboard):** Modern Next.js 14 web application featuring multi-tenant organization switching, real-time KPI stats, workflow inspection, and interactive controls.
* **Layer 11 (Closed-Loop Realized ROI):** Tracks post-deployment execution records against baseline historical hours, verifying realized hours saved and calculating exact ROI multipliers.

---

## 4. Data Models & Mathematical Formulations

### Session Reconstruction Algorithm
Given a sequence of events $E = \{e_1, e_2, \dots, e_n\}$ ordered chronologically by timestamp $t(e_i)$, a new session $S_k$ is instantiated whenever:
$$t(e_{i}) - t(e_{i-1}) > \Delta t_{\text{threshold}} \quad \text{where } \Delta t_{\text{threshold}} = 30 \text{ minutes (1800 seconds)}$$

### N-Gram Sequence Pattern Mining
For each reconstructed session $S_k = (a_1, a_2, \dots, a_m)$ where $a_j$ represents the application identifier (e.g., `google_sheets` $\to$ `salesforce` $\to$ `slack`):
1. Extract all sub-sequences of length $N \in [2, 5]$.
2. Compute the frequency $F(p)$ of pattern $p$ across all distinct sessions.
3. Filter out patterns appearing in fewer than $K_{\text{min}}$ sessions (default $K_{\text{min}} = 2$).
4. Compute Pattern Confidence:
$$\text{Confidence}(p) = \frac{\text{Sessions containing } p}{\text{Total reconstructed sessions}}$$

### Financial & ROI Quantification Formulas

#### 1. Weekly Extrapolation (5 Active Business Days)
Given observation window $D_{\text{obs}}$ (active business days) and observed occurrences $O(p)$ of candidate pattern $p$:
$$\text{Weekly Frequency } F_{\text{wk}}(p) = O(p) \times \left( \frac{5}{\max(D_{\text{obs}}, 1)} \right)$$
*(Note: Extrapolating against 5 business days rather than 7 calendar days ensures labor estimates reflect actual working workweeks without inflating hours).*

#### 2. Weekly Time Loss
Given average duration per pattern execution $\bar{T}(p)$ (in hours):
$$\text{Weekly Hours } H_{\text{wk}}(p) = F_{\text{wk}}(p) \times \bar{T}(p)$$

#### 3. Weekly & Annual Cost
Given organization-configured hourly cost per worker $R_{\text{hr}}$:
$$\text{Weekly Cost } C_{\text{wk}}(p) = H_{\text{wk}}(p) \times R_{\text{hr}}$$
$$\text{Annual Cost } C_{\text{yr}}(p) = C_{\text{wk}}(p) \times 48 \text{ working weeks}$$

#### 4. Recoverable Automation Savings Range
Rather than assuming a flat percentage, Dead Time reports a conservative-to-optimal bandwidth across candidate workflows:
$$\text{Conservative Annual Recovery (50%)} = C_{\text{yr}}(p) \times 0.50$$
$$\text{Optimal Annual Recovery (80%)} = C_{\text{yr}}(p) \times 0.80$$

#### 5. Realized ROI & Payback Period
$$\text{Payback Period (Weeks)} = \frac{\text{Implementation Cost}}{\text{Conservative Weekly Savings } S_{\text{wk, cons}}}$$
$$\text{Realized Weekly Savings} = (H_{\text{before}} - H_{\text{after}}) \times R_{\text{hr}}$$

---

## 5. Complete REST API Specification

Base URL (Cloud Production): `https://dead-time-backend.onrender.com`  
Local Development: `http://localhost:8002`

| Method | Endpoint | Description | Request Body / Params |
|---|---|---|---|
| `POST` | `/events` | Ingests telemetry event from Chrome extension | `EventCreate` JSON |
| `GET` | `/events` | List raw telemetry events | `limit: int`, `org_id: str` |
| `GET` | `/organizations` | List unique client organizations | None |
| `GET` | `/health` | Health check & active layer status | None |
| `GET` | `/sessions` | View reconstructed worker sessions | `org_id: str` |
| `GET` | `/workflows/detected` | Run pattern detection & list sequences | `org_id: str` |
| `GET` | `/workflows/summary` | Aggregate telemetry KPIs | `org_id: str` |
| `GET` | `/workflows/brief` | Full LLM-ready JSON intelligence brief | `hourly_rate`, `currency`, `symbol`, `org_id` |
| `GET` | `/workflows/report` | Render standalone executive HTML report | `hourly_rate`, `currency`, `symbol`, `org_id` |
| `GET` | `/workflows/report/pdf`| Download executive boardroom PDF report | `hourly_rate`, `currency`, `symbol`, `org_id` |
| `GET` | `/workflows/ai-analysis`| Get Gemini-powered AI recommendations | `hourly_rate`, `currency`, `symbol`, `org_id` |
| `POST` | `/blueprints/generate` | Auto-generate blueprint for pattern ID | `pattern_id: str` |
| `GET` | `/blueprints` | List all automation blueprints | None |
| `POST` | `/blueprints/{id}/review` | Human approval gate (`approve`/`reject`) | `{"action": "approve"}` |
| `POST` | `/blueprints/{id}/dry-run`| Sandbox test against mock payload | `DryRunRequest` |
| `GET` | `/blueprints/{id}/export/n8n` | Download ready-to-import n8n workflow | None |
| `GET` | `/blueprints/{id}/export/make`| Download Make.com scenario JSON | None |
| `GET` | `/blueprints/{id}/export/python`| Download standalone Python async script | None |
| `POST` | `/engine/deploy/{id}` | Execute or trigger live deployment | None |
| `GET` | `/analytics/roi-impact` | Before vs After realized ROI metrics | `hourly_rate`, `currency`, `symbol` |

---

## 6. Component Deep Dive

### A. Chrome Telemetry Extension (Manifest V3)
* **Location:** `/extension`
* **Core Files:**
  - `manifest.json`: Defines permissions (`tabs`, `storage`, `idle`, `<all_urls>`).
  - `background.js`: Service worker capturing `chrome.tabs.onActivated` and `chrome.tabs.onUpdated`. Resolves browser URLs to standard application tokens (`slack`, `jira`, `zendesk`, `notion`, `hubspot`, `google_sheets`, `salesforce`, `github`). Batches events and dispatches HTTP POST payloads to `https://dead-time-backend.onrender.com/events`.
  - `popup.html` & `popup.js`: Displays real-time connection status (Online / Offline), cloud server health, and a direct link to the live Vercel dashboard.

### B. FastAPI Python Backend & Algorithmic Engines
* **Location:** `/backend`
* **Core Engines:**
  - `workflow_detector.py`: Session reconstruction and n-gram pattern mining algorithms.
  - `roi_engine.py`: Currency conversions, labor extrapolation, and structured brief synthesis.
  - `llm_engine.py`: Formats prompts and communicates with Google Gemini API (`gemini-1.5-flash` / `gemini-pro`).
  - `blueprint_engine.py`: Synthesizes trigger apps, input fields, transformations, and destination actions into standardized blueprint schemas.
  - `export_engine.py`: Converts blueprint schemas into native JSON import trees for **n8n** and **Make.com**, or compiles executable **Python asyncio** scripts using `httpx`.
  - `automation_engine.py`: Sandboxed mock execution runner and deployment state manager.
  - `pdf_engine.py`: Generates boardroom-quality PDF exports with fallback print styling.

### C. Next.js 14 Executive Intelligence Dashboard
* **Location:** `/frontend`
* **Live URL:** `https://dead-time-b2b.vercel.app/`
* **Key Features:**
  - **Organization Switcher:** Dynamic dropdown filtering telemetry across client accounts (`org_default`, `org_demo`, `acme_corp`, etc.).
  - **5 Primary Operational Panels:**
    1. `Overview`: High-level summary of observed hours, sessions, and recoverable savings.
    2. `Detected Workflows`: Visual breakdown of sequences, step transitions, frequency, and annual cost.
    3. `Sessions`: Chronological reconstruction of employee work sessions and app switching.
    4. `AI Insights`: Instant Gemini automation recommendations, tool rankings, and quick-win operational advice.
    5. `Automation Blueprints & Exports`: Interactive review card with dry-run modal, one-click export buttons (n8n, Make, Python), and deploy triggers.
    6. `ROI Impact Tracker`: Real-time before-vs-after savings tracker showing verified reclaimed hours and ROI percentages.

---

## 7. Cloud Deployment & Zero-Cost Infrastructure

The entire platform is hosted on a high-availability, zero-maintenance, **100% free production tier**:

| Component | Platform | URL / Configuration | Cost |
|---|---|---|---|
| **Backend API** | Render | `https://dead-time-backend.onrender.com` (Python 3.11, Uvicorn) | **$0.00 / month** (750 free hrs) |
| **Frontend UI** | Vercel | `https://dead-time-b2b.vercel.app/` (Next.js 14 App Router) | **$0.00 / month** (Hobby Plan) |
| **Cold-Start Preventer** | UptimeRobot | Pings `GET /health` every 5 minutes to keep Render container hot | **$0.00 / month** (Free tier) |
| **Extension Client** | Local Browser | Unpacked ZIP for private enterprise pilots (zero Web Store fees) | **$0.00** |

---

## 8. Go-To-Market, Sales & Client Onboarding Playbook

### Ideal Customer Profile (ICP)
* **Company Size:** 5 to 50 employees (bypasses enterprise IT procurement bottlenecks).
* **Target Roles:** Founder / CEO (boutique agencies), Chief Operating Officer (COO), VP of Operations, Head of RevOps.
* **Target Verticals:**
  1. **Digital Marketing & SEO Agencies:** Constant manual reporting between Google Sheets, GA4, Meta Ads, and client dashboards.
  2. **Recruitment & Staffing Agencies:** Repetitive scraping between LinkedIn, email, and applicant tracking systems (ATS).
  3. **E-commerce & Shopify Agencies:** Routine catalog management, inventory sync, and order exception handling.
  4. **B2B Outbound Lead Gen Agencies:** Manual data transfers between Apollo, Clay, CRM, and email sequences.

### Cold Outreach Script (LinkedIn / Email)
> **Subject:** Quick question about [Company Name]’s internal ops / dead time
>
> Hi [First Name],
>
> Saw you’re scaling operations at [Company Name]. Typically, service and ops teams lose 15–25% of their working hours to repetitive "dead time" (copy-pasting between tabs, manual spreadsheet reconciliations, and CRM updates).
>
> We run a **free 3-day workflow efficiency audit**:
> 1. Your team installs our lightweight telemetry extension for 3 business days.
> 2. Our engine detects invisible cross-app bottlenecks without capturing sensitive data.
> 3. We deliver a custom **Executive ROI Audit & Automation Blueprint** showing exactly which workflows you can automate and how much payroll you'll reclaim.
>
> Zero commitment, 100% free. Open to seeing what your team's workflow bottleneck map looks like?
>
> Best,  
> [Your Name]

### The White-Glove Onboarding Call (10 Minutes)
1. **Screen Share:** Guide the client to unzip the extension folder, open `chrome://extensions`, enable *Developer mode*, and click *Load unpacked*.
2. **Verify Badge:** Show the Dead Time extension badge switching to green **"Online"**.
3. **Set the Expectation:** *"Let your team work completely normally for 3 business days. On Friday at 3 PM, we will open your live dashboard together and review your team's automation cost map."*

---

## 9. Security & Privacy Design

Enterprise and agency clients care deeply about privacy and avoiding "bossware" perceptions. Dead Time is engineered with a strict **Privacy-by-Design** posture:
* **In-Browser URL Stripping:** The Chrome extension strips raw URLs and page titles before transmission. The backend receives only standardized application tokens (`slack`, `jira`, `google_sheets`) and duration, never sensitive document names, search queries, or internal customer URLs.
* **Seat Pseudonymization (Anti-Surveillance):** Employee IDs are dynamically mapped to anonymous `"Seat 1"`, `"Seat 2"` identifiers in the dashboard. Management sees team workflow patterns without tracking or penalizing individual workers.
* **Employee Pause Toggle (Private Mode):** The extension popup provides a 1-click **Pause Telemetry** button, allowing workers to pause tracking during personal browsing or sensitive tasks.
* **No Keystroke or Screen Capture:** Zero keystrokes, zero form inputs, zero clipboard inspection, zero screenshots, and zero audio/video recording.
* **Isolated Client Screen Shares:** Client dashboards are isolated by workspace (`?org=client_name`), ensuring no competitor or other client names are ever visible during live calls.
* **Bearer Token Ingest Authorization:** Ingestion endpoint supports `Authorization: Bearer <token>` guarded by `DEADTIME_INGEST_TOKEN`.

---

## 10. Quick-Start Development Guide

### 1. Local Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```
*Health Check:* `http://localhost:8002/health`

### 2. Local Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Dashboard:* `http://localhost:3000`

### 3. Load Extension Locally
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable the **Developer mode** toggle in the top-right corner.
3. Click **Load unpacked** and select the `dead-time-b2b/extension` folder.
4. Telemetry events will stream directly to the configured backend API.
