"""
seed_agency.py
==============
Digital Marketing & Performance Agency Demo Dataset for Dead Time B2B.

Populates realistic cross-app telemetry tailored for:
  • Digital Marketing Agencies (PPC, SEO, Social)
  • Performance Marketing Strategists (Google Ads, Meta Ads, Sheets, Analytics)

Creates 3 high-impact marketing workflows and Phase 2 blueprints:
  1. Multi-Platform PPC Client Reporting (Google Ads -> Meta Ads -> Sheets -> Gmail)
  2. SEO Rank & Keyword Export Sync (SEMrush -> Sheets -> Looker Studio)
  3. Creative Asset Handoff & Launch (Drive -> Meta Ads -> Slack)
"""

import datetime
from database import SessionLocal, engine, Base
import models
from workflow_detector import WorkflowDetector, RawEvent

def seed_agency_demo():
    db = SessionLocal()
    try:
        print("[Agency Demo Seed] Initializing tables...")
        Base.metadata.create_all(bind=engine)

        # Remove existing agency demo records only
        db.query(models.AutomationBlueprint).filter(models.AutomationBlueprint.org_id == "org_agency_demo").delete()
        db.query(models.Event).filter(models.Event.org_id == "org_agency_demo").delete()
        db.commit()

        print("[Agency Demo Seed] Generating realistic agency marketing telemetry...")
        now = datetime.datetime.utcnow()
        events = []

        def add_seq(session_id, user_id, start_offset_mins, seq_list):
            base_time = now - datetime.timedelta(minutes=start_offset_mins)
            t = base_time
            for app, action, obj_type, obj_id, meta in seq_list:
                t += datetime.timedelta(seconds=25)
                events.append(models.Event(
                    org_id="org_agency_demo",
                    user_id=user_id,
                    timestamp=t,
                    application=app,
                    action_type=action,
                    object_type=obj_type,
                    object_id=obj_id,
                    session_id=session_id,
                    metadata_json=meta
                ))

        # Workflow 1: Multi-Platform PPC Reporting (Monday Routine)
        # Google Ads -> Meta Ads -> Google Sheets -> Gmail
        for i in range(5):
            sess_id = f"agency_sess_ppc_{i+1}"
            offset = 1440 * (5 - i) + 180
            add_seq(sess_id, "analyst_rohit@agency.com", offset, [
                ("google_ads", "open", "campaign_dashboard", "Client_Alpha_Search", {"spend": 45000, "roas": 3.8}),
                ("google_ads", "export", "performance_table", "q1_search_metrics.csv", {"metrics": ["clicks", "cpc", "conversions"]}),
                ("facebook_ads", "open", "ads_manager", "Client_Alpha_Meta", {"ad_sets": 6, "status": "active"}),
                ("facebook_ads", "copy", "roas_table", "weekly_roas", {"spend": 62000, "roas": 4.1}),
                ("google_sheets", "open", "client_master_deck", "Client_Alpha_Weekly_PPC", {"sheet": "Consolidated_Metrics"}),
                ("google_sheets", "edit", "cells", "Range_B12_F24", {"formula": "=SUM(B2:B11)"}),
                ("gmail", "open", "compose", "draft_report", {"to": "client_cmo@clientbrand.com"}),
                ("gmail", "send", "weekly_deck", "Email_Sent", {"subject": "Weekly Performance Dashboard: Client Alpha"})
            ])

        # Workflow 2: SEO Keyword Audit & Client Deck Sync
        # SEMrush -> Google Sheets -> Looker Studio
        for i in range(4):
            sess_id = f"agency_sess_seo_{i+1}"
            offset = 1440 * (4 - i) + 300
            add_seq(sess_id, "seo_priya@agency.com", offset, [
                ("semrush", "open", "position_tracking", "client_alpha_domain", {"ranked_keywords": 420}),
                ("semrush", "export", "csv", "keyword_delta_weekly.csv", {"format": "csv"}),
                ("google_sheets", "open", "seo_tracker", "SEO_Master_Tracking_2026", {"tab": "Weekly_Deltas"}),
                ("google_sheets", "paste", "data", "A1:G150", {"rows_imported": 150}),
                ("looker_studio", "refresh", "data_source", "SEO_Executive_Dashboard", {"status": "recalculated"})
            ])

        # Workflow 3: Creative Handoff & Ad Set Launch
        # Google Drive -> Meta Ads Manager -> Slack
        for i in range(4):
            sess_id = f"agency_sess_creative_{i+1}"
            offset = 1440 * (4 - i) + 420
            add_seq(sess_id, "buyer_arjun@agency.com", offset, [
                ("google_drive", "open", "folder", "/Clients/Alpha/Creatives_Q1", {"files_count": 8}),
                ("google_drive", "download", "video_ad", "Reel_Hook_03_Final.mp4", {"size_mb": 24.5}),
                ("facebook_ads", "open", "creative_library", "Upload_New_Creative", {"ad_format": "9:16 Reel"}),
                ("facebook_ads", "submit", "publish_campaign", "Camp_Retargeting_V3", {"budget_daily": 5000}),
                ("slack", "send", "channel", "#client-alpha-ops", {"text": "Published new Reel creative into Camp_Retargeting_V3"})
            ])

        db.add_all(events)
        db.commit()
        print(f"[Agency Demo Seed] Ingested {len(events)} events.")

        # Reconstruct sessions and detect patterns
        print("[Agency Demo Seed] Running session detection...")
        detector = WorkflowDetector()
        raw_events = [
            RawEvent(
                id=e.id, user_id=e.user_id, session_id=e.session_id,
                timestamp=e.timestamp, application=e.application,
                action_type=e.action_type, object_type=e.object_type,
                object_id=e.object_id, metadata_json=e.metadata_json
            )
            for e in events
        ]
        detected_sessions = detector.split_into_sessions(raw_events)
        for s in detected_sessions:
            db.add(models.WorkflowSession(
                session_key=s.session_key,
                user_id=s.user_id,
                start_time=s.start_time,
                end_time=s.end_time,
                duration_minutes=s.duration_minutes,
                event_count=s.event_count,
                app_sequence=s.app_sequence,
                apps_used=s.apps_used,
                source_session_ids=s.source_session_ids,
            ))
        db.commit()

        # Seed 3 Commercial-Grade Blueprints specifically for Marketing Agencies
        print("[Agency Demo Seed] Creating Agency Automation Blueprints...")

        # 1. Pending Review: Multi-Platform PPC Consolidator
        bp_ppc = models.AutomationBlueprint(
            org_id="org_agency_demo",
            pattern_id="wp_ppc_reporting",
            name="Multi-Platform PPC Consolidator (Google Ads + Meta → Sheets → Client Email)",
            status="pending_review",
            blueprint_json={
                "blueprint_name": "Multi-Platform PPC Consolidator",
                "trigger_app": "Google Ads & Meta Ads API",
                "trigger_event": "Scheduled Monday 06:00 AM Cron",
                "inputs": ["google_ads_account_id", "meta_ads_account_id", "date_range_last_7_days"],
                "transformations": [
                    {
                        "step": 1,
                        "description": "Fetch spend, impressions, CTR, CPC, and conversion values from Google Ads REST API",
                        "action_type": "api_fetch"
                    },
                    {
                        "step": 2,
                        "description": "Fetch ad-set spend, reach, ROAS, and purchases from Meta Graph API",
                        "action_type": "api_fetch"
                    },
                    {
                        "step": 3,
                        "description": "Calculate blended ROAS, CPA, and variance vs target KPI inside Google Sheets template",
                        "action_type": "sheets_upsert"
                    },
                    {
                        "step": 4,
                        "description": "Draft client summary email in Gmail with PDF executive attachment ready for Account Manager 1-click send",
                        "action_type": "email_draft"
                    }
                ],
                "destination_app": "Google Sheets & Gmail",
                "destination_action": "Consolidated Report Created & Draft Staged",
                "human_in_the_loop_required": True,
                "estimated_setup_time_mins": 45
            }
        )
        db.add(bp_ppc)

        # 2. Approved: Weekly SEO Rank Movement Sync
        bp_seo = models.AutomationBlueprint(
            org_id="org_agency_demo",
            pattern_id="wp_seo_sync",
            name="SEO Rank & Keyword Movement Sync (SEMrush → Looker Studio)",
            status="approved",
            blueprint_json={
                "blueprint_name": "SEO Rank & Keyword Movement Sync",
                "trigger_app": "SEMrush API",
                "trigger_event": "Weekly Position Tracking Delta Export",
                "inputs": ["project_id", "top_100_keywords", "competitor_benchmarks"],
                "transformations": [
                    {
                        "step": 1,
                        "description": "Pull keyword rankings delta (+/- positions) via SEMrush API",
                        "action_type": "api_fetch"
                    },
                    {
                        "step": 2,
                        "description": "Filter high-intent commercial keywords that dropped out of Top 3",
                        "action_type": "data_filter"
                    },
                    {
                        "step": 3,
                        "description": "Refresh Looker Studio data source and trigger agency Slack alert on critical rank drops",
                        "action_type": "webhook_notify"
                    }
                ],
                "destination_app": "Looker Studio & Slack",
                "destination_action": "Dashboard Refreshed & Alert Dispatched",
                "human_in_the_loop_required": True,
                "estimated_setup_time_mins": 30
            }
        )
        db.add(bp_seo)

        # 3. Deployed: Ad Creative Handoff & Launch
        bp_creative = models.AutomationBlueprint(
            org_id="org_agency_demo",
            pattern_id="wp_creative_launch",
            name="Creative Asset Ingestion & Meta Ads Drafter (Drive → Meta Ads → Slack)",
            status="deployed",
            blueprint_json={
                "blueprint_name": "Creative Asset Ingestion & Meta Ads Drafter",
                "trigger_app": "Google Drive",
                "trigger_event": "New Asset Uploaded to /Approved_Creatives",
                "inputs": ["asset_url", "ad_copy_doc", "target_campaign_id"],
                "transformations": [
                    {
                        "step": 1,
                        "description": "Upload video/image to Meta Ad Creative Library via Graph API",
                        "action_type": "media_upload"
                    },
                    {
                        "step": 2,
                        "description": "Create Draft Ad inside target campaign with standard UTM tracking parameters",
                        "action_type": "ad_creation"
                    },
                    {
                        "step": 3,
                        "description": "Notify Media Buyer in Slack #media-buying with 1-click preview link for review",
                        "action_type": "slack_notify"
                    }
                ],
                "destination_app": "Meta Ads Manager & Slack",
                "destination_action": "Draft Ad Created in Meta & Slack Alert Dispatched",
                "human_in_the_loop_required": True,
                "estimated_setup_time_mins": 35
            }
        )
        db.add(bp_creative)
        db.commit()

        # Seed execution logs for deployed blueprint
        exec_logs = [
            {"timestamp": (now - datetime.timedelta(hours=44)).isoformat(), "level": "INFO", "message": "Uploaded 2 Reel creatives for Client Alpha. Draft Ads staged in Meta Ads Manager. Notified #media-buying."},
            {"timestamp": (now - datetime.timedelta(hours=32)).isoformat(), "level": "INFO", "message": "Uploaded 3 Static Carousels for Client Beta. Draft Ads staged in Meta Ads Manager. Notified #media-buying."},
            {"timestamp": (now - datetime.timedelta(hours=18)).isoformat(), "level": "INFO", "message": "Uploaded 1 Hero Video for Client Gamma. Draft Ads staged in Meta Ads Manager. Notified #media-buying."},
            {"timestamp": (now - datetime.timedelta(hours=6)).isoformat(),  "level": "INFO", "message": "Uploaded 4 Retargeting Creatives for Client Delta. Draft Ads staged in Meta Ads Manager. Notified #media-buying."}
        ]

        for log in exec_logs:
            db.add(models.AutomationExecution(
                blueprint_id=bp_creative.id,
                status="success",
                execution_time=datetime.datetime.fromisoformat(log["timestamp"]),
                logs_json=[log]
            ))
        db.commit()

        print(f"[Agency Demo Seed] SUCCESS! Seeded {len(events)} events, {len(detected_sessions)} sessions, 3 blueprints, {len(exec_logs)} executions for org_agency_demo.")
        return {
            "status": "success",
            "org_id": "org_agency_demo",
            "events_seeded": len(events),
            "sessions": len(detected_sessions),
            "blueprints": 3
        }
    finally:
        db.close()

if __name__ == "__main__":
    seed_agency_demo()
