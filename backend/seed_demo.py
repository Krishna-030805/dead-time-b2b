"""
seed_demo.py
============
Enterprise Demonstration Dataset Seeder for Dead Time B2B.

Populates realistic cross-app telemetry, mines workflow patterns,
and configures Phase 2 blueprints across all lifecycle states:
  • 1 Blueprint in 'pending_review' (Human-in-the-Loop demo)
  • 1 Blueprint in 'approved' (Deployment demo)
  • 1 Blueprint in 'deployed' (Realized ROI savings demo)
"""

import datetime
from database import SessionLocal, engine, Base
import models
from workflow_detector import WorkflowDetector, RawEvent

def seed_enterprise_demo():
    db = SessionLocal()
    try:
        print("[Demo Seed] Initializing database tables...")
        Base.metadata.create_all(bind=engine)

        # Clear existing records
        db.query(models.AutomationExecution).delete()
        db.query(models.AutomationBlueprint).delete()
        db.query(models.WorkflowSession).delete()
        db.query(models.Event).delete()
        db.commit()

        print("[Demo Seed] Generating realistic cross-tool telemetry...")
        now = datetime.datetime.utcnow()
        events = []

        def add_seq(session_id, user_id, start_offset_mins, seq_list):
            base_time = now - datetime.timedelta(minutes=start_offset_mins)
            t = base_time
            for app, action, obj_type, obj_id, meta in seq_list:
                t += datetime.timedelta(seconds=20)
                events.append(models.Event(
                    org_id="org_enterprise_demo",
                    user_id=user_id,
                    timestamp=t,
                    application=app,
                    action_type=action,
                    object_type=obj_type,
                    object_id=obj_id,
                    session_id=session_id,
                    metadata_json=meta
                ))

        # Workflow 1: Customer Support Escalation (Slack -> Zendesk -> Jira -> GitHub)
        # Repeated across 4 sessions
        for i in range(4):
            sess_id = f"demo_sess_support_{i+1}"
            offset = 1440 * (4 - i) + 120
            add_seq(sess_id, "agent_sarah@company.com", offset, [
                ("slack", "open", "channel", "#support-urgent", {"channel": "#support-urgent"}),
                ("slack", "click", "message", "MSG-9921", {"snippet": "URGENT: Production API returning 500"}),
                ("zendesk", "open", "ticket", f"TICKET-10{i+1}", {"priority": "urgent", "subject": "API 500 error"}),
                ("zendesk", "edit", "ticket_field", "status", {"new_status": "in_progress"}),
                ("jira", "open", "issue_creator", "PROJ-BUG", {"project": "INFRA"}),
                ("jira", "submit", "issue", f"INFRA-34{i+1}", {"issue_type": "Bug", "severity": "P0"}),
                ("github", "open", "repo", "backend-core", {"repo": "enterprise/backend-core"}),
                ("github", "click", "commit_history", "main", {"branch": "main"}),
                ("slack", "send", "channel", "#support-urgent", {"text": f"Created Jira INFRA-34{i+1} for TICKET-10{i+1}"})
            ])

        # Workflow 2: Financial Accounts Payable (Gmail -> Xero -> Google Drive -> Slack)
        # Repeated across 4 sessions
        for i in range(4):
            sess_id = f"demo_sess_finance_{i+1}"
            offset = 1440 * (4 - i) + 240
            add_seq(sess_id, "finance_david@company.com", offset, [
                ("gmail", "open", "email", f"INV-2026-0{i+1}", {"sender": "billing@vendor-saas.com"}),
                ("gmail", "click", "attachment", f"invoice_march_0{i+1}.pdf", {"type": "application/pdf"}),
                ("xero", "open", "bills", "new_bill", {"contact": "Vendor SaaS Inc"}),
                ("xero", "submit", "bill_entry", f"BILL-99{i+1}", {"amount": 4200.0, "currency": "USD"}),
                ("google_drive", "open", "folder", "/Finance/2026/Invoices", {"folder": "Invoices"}),
                ("google_drive", "upload", "file", f"vendor_invoice_0{i+1}.pdf", {"status": "saved"}),
                ("slack", "send", "channel", "#finance-ops", {"text": f"Logged bill BILL-99{i+1} in Xero & uploaded PDF"})
            ])

        # Workflow 3: Inbound Sales Lead Sync (Salesforce -> LinkedIn -> HubSpot -> Slack)
        # Repeated across 3 sessions
        for i in range(3):
            sess_id = f"demo_sess_sales_{i+1}"
            offset = 1440 * (3 - i) + 360
            add_seq(sess_id, "sales_marcus@company.com", offset, [
                ("salesforce", "open", "lead", f"LEAD-44{i+1}", {"company": "Acme Global", "industry": "Fintech"}),
                ("salesforce", "copy", "lead_details", "email,company", {"fields": ["name", "email", "title"]}),
                ("hubspot", "open", "deal_pipeline", "Enterprise Deals", {"pipeline": "Q1 2026"}),
                ("hubspot", "create", "contact", f"contact_{i+1}@acme.com", {"lifecycle_stage": "opportunity"}),
                ("slack", "send", "channel", "#sales-wins", {"text": f"Enriched Acme Global lead and synced to HubSpot"})
            ])

        db.add_all(events)
        db.commit()
        print(f"[Demo Seed] Ingested {len(events)} activity events.")

        # Reconstruct sessions and mine patterns
        print("[Demo Seed] Reconstructing work sessions...")
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

        # Seed 3 Commercial-Grade Blueprints across all lifecycle states
        print("[Demo Seed] Configuring Phase 2 Blueprints & Closed-Loop Engine...")

        # Blueprint 1: Pending Human Review (Demo Human-in-the-Loop Gateway)
        bp_pending = models.AutomationBlueprint(
            org_id="org_enterprise_demo",
            pattern_id="wp_support_escalation",
            name="Customer Support Incident Sync (Slack → Zendesk → Jira)",
            status="pending_review",
            blueprint_json={
                "blueprint_name": "Customer Support Incident Sync",
                "trigger_app": "Slack",
                "trigger_event": "New Urgent Message in #support-urgent",
                "inputs": ["slack_message_content", "slack_user_id", "channel_id"],
                "transformations": [
                    {
                        "step": 1,
                        "description": "Parse incident priority and extract error codes using LLM classifier",
                        "action_type": "ai_classification"
                    },
                    {
                        "step": 2,
                        "description": "Create Zendesk urgent support ticket and assign to tier-2 on-call",
                        "action_type": "create_ticket"
                    },
                    {
                        "step": 3,
                        "description": "Create Jira P0 Bug ticket linking Zendesk Ticket ID in custom fields",
                        "action_type": "create_issue"
                    }
                ],
                "destination_app": "Jira & Slack",
                "destination_action": "Create Bug & Post Confirmation to Slack",
                "human_in_the_loop_required": True,
                "estimated_setup_time_mins": 35
            }
        )
        db.add(bp_pending)

        # Blueprint 2: Approved (Demo Deploy Button)
        bp_approved = models.AutomationBlueprint(
            org_id="org_enterprise_demo",
            pattern_id="wp_sales_intake",
            name="Inbound Sales Lead Enrichment (Salesforce → HubSpot)",
            status="approved",
            blueprint_json={
                "blueprint_name": "Inbound Sales Lead Enrichment",
                "trigger_app": "Salesforce",
                "trigger_event": "New Lead Created (Status: MQL)",
                "inputs": ["company_name", "contact_email", "lead_source"],
                "transformations": [
                    {
                        "step": 1,
                        "description": "Enrich company metadata via Clearbit API",
                        "action_type": "data_enrichment"
                    },
                    {
                        "step": 2,
                        "description": "Upsert Contact and Deal record in HubSpot Enterprise Pipeline",
                        "action_type": "sync_crm"
                    }
                ],
                "destination_app": "HubSpot",
                "destination_action": "Upsert Deal & Notify Account Exec on Slack",
                "human_in_the_loop_required": True,
                "estimated_setup_time_mins": 25
            }
        )
        db.add(bp_approved)

        # Blueprint 3: Deployed (Demo Realized ROI Impact Tracker)
        bp_deployed = models.AutomationBlueprint(
            org_id="org_enterprise_demo",
            pattern_id="wp_finance_payable",
            name="Accounts Payable Invoice Processing (Gmail → Xero → Drive)",
            status="deployed",
            blueprint_json={
                "blueprint_name": "Accounts Payable Invoice Processing",
                "trigger_app": "Gmail",
                "trigger_event": "New Email with PDF Attachment from Known Vendors",
                "inputs": ["email_sender", "email_subject", "attachment_pdf"],
                "transformations": [
                    {
                        "step": 1,
                        "description": "Extract vendor, invoice number, due date, line items, and tax via OCR",
                        "action_type": "ocr_extraction"
                    },
                    {
                        "step": 2,
                        "description": "Create Draft Bill in Xero Accounting awaiting approval",
                        "action_type": "create_bill"
                    },
                    {
                        "step": 3,
                        "description": "Archive PDF invoice to Google Drive /Finance/2026/Invoices with naming schema",
                        "action_type": "archive_file"
                    }
                ],
                "destination_app": "Xero & Google Drive",
                "destination_action": "Draft Bill Created & File Archived",
                "human_in_the_loop_required": True,
                "estimated_setup_time_mins": 45
            }
        )
        db.add(bp_deployed)
        db.commit()

        # Add simulated execution history for deployed blueprint
        exec_logs = [
            {"timestamp": (now - datetime.timedelta(hours=48)).isoformat(), "level": "INFO", "message": "Triggered by invoice from Datadog Inc ($3,400.00). Bill BILL-8821 created in Xero. Archived to Drive."},
            {"timestamp": (now - datetime.timedelta(hours=36)).isoformat(), "level": "INFO", "message": "Triggered by invoice from AWS Cloud ($14,250.00). Bill BILL-8822 created in Xero. Archived to Drive."},
            {"timestamp": (now - datetime.timedelta(hours=24)).isoformat(), "level": "INFO", "message": "Triggered by invoice from Figma ($980.00). Bill BILL-8823 created in Xero. Archived to Drive."},
            {"timestamp": (now - datetime.timedelta(hours=12)).isoformat(), "level": "INFO", "message": "Triggered by invoice from Google Workspace ($1,850.00). Bill BILL-8824 created in Xero. Archived to Drive."},
            {"timestamp": (now - datetime.timedelta(hours=2)).isoformat(),  "level": "INFO", "message": "Triggered by invoice from Zoom Inc ($450.00). Bill BILL-8825 created in Xero. Archived to Drive."}
        ]

        for log in exec_logs:
            db.add(models.AutomationExecution(
                blueprint_id=bp_deployed.id,
                status="success",
                execution_time=datetime.datetime.fromisoformat(log["timestamp"]),
                logs_json=[log]
            ))
        db.commit()

        print(f"[Demo Seed] SUCCESS: Enterprise demonstration data seeded cleanly! ({len(events)} events, {len(detected_sessions)} sessions, 3 blueprints, {len(exec_logs)} executions)")
        return {
            "status": "success",
            "events_seeded": len(events),
            "sessions_detected": len(detected_sessions),
            "blueprints": 3,
            "executions": len(exec_logs)
        }
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise_demo()
