"""
pdf_engine.py
=============
Layer 3B — Executive PDF Report Generator

Converts an intelligence brief (from roi_engine.build_intelligence_brief) into
a beautiful, branded, downloadable PDF report.

Uses WeasyPrint to render HTML/CSS → PDF.  The HTML template mirrors the
existing _render_report() aesthetic but is optimised for print:
  • Light background for low ink usage
  • Proper page-break hints
  • Page numbers in footer margins
  • Cover page with org name, date, "CONFIDENTIAL" badge
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


# ─── Public API ──────────────────────────────────────────────────────────────

def generate_pdf_report(brief: Dict[str, Any]) -> bytes:
    """
    Render the intelligence brief as a PDF.
    Returns raw PDF bytes ready for streaming to the client.
    """
    from playwright.sync_api import sync_playwright

    html = _render_pdf_html(brief)
    
    with sync_playwright() as p:
        try:
            # Standard headless Chromium (works on Linux/Render/Docker)
            browser = p.chromium.launch(headless=True)
        except Exception:
            # Fallback to local system Edge browser (Windows development)
            browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "2cm", "bottom": "2cm", "left": "1.8cm", "right": "1.8cm"}
        )
        browser.close()
        
    return pdf_bytes


# ─── HTML Template ───────────────────────────────────────────────────────────

def _render_pdf_html(brief: Dict[str, Any]) -> str:
    meta = brief["meta"]
    ex   = brief["executive_summary"]
    wfs  = brief["workflows"]

    gen_at  = datetime.fromisoformat(meta["generated_at"].replace("Z", "+00:00"))
    gen_str = gen_at.strftime("%d %B %Y, %H:%M UTC")

    # ── Build workflow cards HTML ─────────────────────────────────────────
    wf_cards = ""
    for i, wf in enumerate(wfs):
        roi  = wf.get("roi", {})
        tier = wf.get("opportunity_tier", "low")
        tier_color = {"high": "#e11d48", "medium": "#d97706", "low": "#6d63ff"}.get(tier, "#6d63ff")
        tier_bg    = {"high": "#fef2f2", "medium": "#fffbeb", "low": "#eef2ff"}.get(tier, "#eef2ff")
        tier_label = tier.upper()
        rank_label = ["#1 Top Priority", "#2 Second Priority", f"#{i+1}"][min(i, 2)]

        seq_html = ""
        for j, app in enumerate(wf.get("sequence", [])):
            seq_html += f'<span class="app-chip">{app.replace("_"," ").title()}</span>'
            if j < len(wf.get("sequence", [])) - 1:
                seq_html += '<span class="arr">→</span>'

        wf_cards += f"""
        <div class="wf-card" style="border-left:3px solid {tier_color};page-break-inside:avoid">
          <div class="wf-header">
            <div class="wf-rank">{rank_label}</div>
            <div class="wf-name">{wf.get('name','')}</div>
            <span class="tier-pill" style="background:{tier_bg};color:{tier_color};border:1px solid {tier_color}40">{tier_label}</span>
          </div>
          <div class="wf-seq">{seq_html}</div>
          <div class="metrics-row">
            <div class="m">
              <div class="ml">WEEKLY COST</div>
              <div class="mv" style="color:{tier_color}">{roi.get('weekly_cost_label','—')}</div>
              <div class="ms">{wf.get('total_time_hours_per_week',0):.1f} hrs/week</div>
            </div>
            <div class="m">
              <div class="ml">ANNUAL COST</div>
              <div class="mv">{roi.get('annual_cost_label','—')}</div>
              <div class="ms">{roi.get('annual_hours_label','—')}</div>
            </div>
            <div class="m">
              <div class="ml">RECOVERABLE</div>
              <div class="mv" style="color:#059669">{roi.get('automatable_cost_label','—')}</div>
              <div class="ms">at 80% automation</div>
            </div>
            <div class="m">
              <div class="ml">FREQUENCY</div>
              <div class="mv">{wf.get('frequency',0)}×</div>
              <div class="ms">{wf.get('avg_duration_minutes',0):.0f} min avg</div>
            </div>
            <div class="m">
              <div class="ml">CONFIDENCE</div>
              <div class="mv">{int(wf.get('confidence',0)*100)}%</div>
              <div class="ms">pattern match</div>
            </div>
          </div>
        </div>
        """

    if not wfs:
        wf_cards = """
        <div class="no-data">
          <p>No recurring workflow patterns detected yet.</p>
          <p class="sub">Browse with the Chrome Extension active across 2–3 sessions, then regenerate.</p>
        </div>
        """

    top = ex.get("top_opportunity") or {}

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Dead Time Workflow Intelligence Report — {meta['org_id']}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    @page {{
      size: A4;
      margin: 2cm 1.8cm;
      @bottom-center {{
        content: "Dead Time · Workflow Intelligence Report · Page " counter(page) " of " counter(pages);
        font: 400 8pt 'Plus Jakarta Sans', sans-serif;
        color: #94a3b8;
      }}
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      background: #fff;
      color: #1e293b;
      font-size: 10pt;
      line-height: 1.6;
    }}

    /* ── Cover ── */
    .cover {{
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 2px solid #e2e8f0;
    }}
    .cover-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1rem;
    }}
    .badge {{
      display: inline-block;
      padding: 0.25rem 0.7rem;
      border-radius: 9999px;
      font-weight: 700;
      font-size: 7pt;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }}
    .badge-dt {{
      background: #eef2ff;
      color: #6d63ff;
      border: 1px solid #c7d2fe;
    }}
    .badge-conf {{
      background: #fef2f2;
      color: #e11d48;
      border: 1px solid #fecaca;
    }}
    .cover-title {{
      font-size: 22pt;
      font-weight: 800;
      letter-spacing: -0.04em;
      line-height: 1.15;
      color: #0f172a;
      margin-bottom: 0.4rem;
    }}
    .cover-sub {{
      font-size: 10pt;
      color: #64748b;
    }}
    .cover-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 1.2rem;
      margin-top: 1rem;
    }}
    .meta-item {{
      font-size: 8pt;
      color: #94a3b8;
    }}
    .meta-item strong {{
      color: #475569;
      font-weight: 600;
    }}

    /* ── Section labels ── */
    .section-label {{
      font-size: 7pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #94a3b8;
      margin-bottom: 0.8rem;
      margin-top: 1.5rem;
    }}

    /* ── Executive Summary Grid ── */
    .exec-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1.8rem;
    }}
    .exec-card {{
      flex: 1 1 130px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 0.8rem 1rem;
    }}
    .ec-label {{
      font-size: 6.5pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: #94a3b8;
      margin-bottom: 0.3rem;
    }}
    .ec-value {{
      font-size: 18pt;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1;
    }}
    .ec-sub {{
      font-size: 7pt;
      color: #94a3b8;
      margin-top: 0.2rem;
    }}
    .c-indigo {{ color: #6d63ff; }}
    .c-emerald {{ color: #059669; }}
    .c-amber {{ color: #d97706; }}
    .c-rose {{ color: #e11d48; }}

    /* ── Hero ── */
    .hero {{
      background: linear-gradient(135deg, #eef2ff, #f0fdf4);
      border: 1px solid #c7d2fe;
      border-radius: 10px;
      padding: 1.2rem 1.5rem;
      margin-bottom: 1.8rem;
      page-break-inside: avoid;
    }}
    .hero-label {{
      font-size: 7pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #6d63ff;
      margin-bottom: 0.4rem;
    }}
    .hero-name {{
      font-size: 14pt;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
      color: #0f172a;
    }}
    .hero-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 1.2rem;
    }}
    .hero-stat .hs-val {{
      font-weight: 700;
      font-size: 12pt;
      letter-spacing: -0.02em;
    }}
    .hero-stat .hs-lbl {{
      font-size: 7pt;
      color: #94a3b8;
      margin-top: 0.1rem;
    }}

    /* ── Workflow Cards ── */
    .wf-card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 1.1rem;
      margin-bottom: 0.9rem;
    }}
    .wf-header {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 0.5rem;
      margin-bottom: 0.6rem;
    }}
    .wf-rank {{
      font-size: 7pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: #94a3b8;
    }}
    .wf-name {{
      font-weight: 700;
      font-size: 10pt;
      flex: 1;
    }}
    .tier-pill {{
      padding: 0.15rem 0.5rem;
      border-radius: 9999px;
      font-weight: 700;
      font-size: 6.5pt;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .wf-seq {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.25rem;
      margin-bottom: 0.8rem;
    }}
    .app-chip {{
      padding: 0.2rem 0.5rem;
      border-radius: 5px;
      background: #eef2ff;
      border: 1px solid #c7d2fe;
      font-size: 7.5pt;
      color: #4338ca;
    }}
    .arr {{ color: #94a3b8; font-size: 9pt; }}

    .metrics-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
      padding-top: 0.7rem;
      border-top: 1px solid #e2e8f0;
    }}
    .m {{ flex: 1 1 90px; }}
    .ml {{
      font-size: 6pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: #94a3b8;
      margin-bottom: 0.2rem;
    }}
    .mv {{
      font-weight: 800;
      font-size: 12pt;
      letter-spacing: -0.02em;
      color: #1e293b;
    }}
    .ms {{
      font-size: 6.5pt;
      color: #94a3b8;
      margin-top: 0.1rem;
    }}

    /* ── No Data ── */
    .no-data {{
      text-align: center;
      padding: 3rem 1rem;
      color: #94a3b8;
    }}
    .no-data .sub {{
      font-size: 9pt;
      margin-top: 0.4rem;
    }}

    /* ── Footer ── */
    .report-footer {{
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid #e2e8f0;
      font-size: 7.5pt;
      color: #94a3b8;
      line-height: 1.8;
    }}
    .report-footer strong {{
      color: #475569;
    }}
  </style>
</head>
<body>

  <!-- Cover -->
  <div class="cover">
    <div class="cover-top">
      <span class="badge badge-dt">Dead Time · Workflow Intelligence</span>
      <span class="badge badge-conf">CONFIDENTIAL</span>
    </div>
    <div class="cover-title">Workflow Intelligence<br>Brief</div>
    <div class="cover-sub">Continuous process observation &amp; automation opportunity analysis</div>
    <div class="cover-meta">
      <div class="meta-item">Organisation: <strong>{meta['org_id']}</strong></div>
      <div class="meta-item">Generated: <strong>{gen_str}</strong></div>
      <div class="meta-item">Observation: <strong>{meta['observation_days']} day(s)</strong></div>
      <div class="meta-item">Hourly rate: <strong>{meta.get('currency_symbol', '₹')}{meta.get('hourly_rate', meta.get('hourly_rate_gbp', 400)):.0f}/hr</strong></div>
      <div class="meta-item">Brief ID: <strong>{meta['brief_id']}</strong></div>
    </div>
  </div>

  <!-- Executive Summary -->
  <div class="section-label">Executive Summary</div>
  <div class="exec-grid">
    <div class="exec-card">
      <div class="ec-label">Events Captured</div>
      <div class="ec-value c-indigo">{ex.get('total_events_captured',0)}</div>
      <div class="ec-sub">activity signals</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Sessions Detected</div>
      <div class="ec-value c-emerald">{ex.get('total_sessions_detected',0)}</div>
      <div class="ec-sub">work sessions</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Patterns Found</div>
      <div class="ec-value c-amber">{ex.get('total_workflows_identified',0)}</div>
      <div class="ec-sub">recurring workflows</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Weekly Cost</div>
      <div class="ec-value c-rose">{ex.get('weekly_cost_across_workflows','£0')}</div>
      <div class="ec-sub">across all patterns</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Annual Cost</div>
      <div class="ec-value">{ex.get('annual_cost_across_workflows','£0')}</div>
      <div class="ec-sub">48 working weeks</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Recoverable / yr</div>
      <div class="ec-value c-emerald">{ex.get('recoverable_annually','£0')}</div>
      <div class="ec-sub">at 80% automation</div>
    </div>
  </div>

  <!-- Hero: Top Opportunity -->
  {"" if not top else f'''
  <div class="hero">
    <div class="hero-label">Top Automation Opportunity</div>
    <div class="hero-name">{top.get("name","—")}</div>
    <div class="hero-stats">
      <div class="hero-stat"><div class="hs-val" style="color:#e11d48">{top.get("weekly_cost","—")}</div><div class="hs-lbl">weekly cost</div></div>
      <div class="hero-stat"><div class="hs-val" style="color:#d97706">{top.get("annual_cost","—")}</div><div class="hs-lbl">annual cost</div></div>
      <div class="hero-stat"><div class="hs-val" style="color:#059669">{top.get("frequency","—")}×</div><div class="hs-lbl">sessions matched</div></div>
    </div>
  </div>
  '''}

  <!-- Workflow Cards -->
  <div class="section-label">Workflow Patterns — Ranked by ROI Impact</div>
  {wf_cards}

  <!-- Footer -->
  <div class="report-footer">
    <strong>Methodology.</strong> Events were collected via the Dead Time Chrome Extension. Sessions were
    reconstructed by splitting the event stream on 30-minute inactivity gaps. Recurring patterns were
    identified using n-gram frequency analysis. Costs are extrapolated to a 7-day week and a 48-week
    working year. Automation savings assume 80% of manual time is recoverable.
    <br><br>
    <strong>Brief ID:</strong> {meta['brief_id']} ·
    <strong>Schema:</strong> v{meta['schema_version']} ·
    <strong>Source:</strong> {meta['source']}
  </div>

</body>
</html>"""
