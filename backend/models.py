from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Text
from database import Base
import datetime

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String, index=True, default="org_default")
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    application = Column(String, index=True)
    action_type = Column(String)
    object_type = Column(String, nullable=True)
    object_id = Column(String, nullable=True)
    session_id = Column(String, index=True)
    metadata_json = Column(JSON, nullable=True)

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String, index=True)
    name = Column(String)
    trigger = Column(String)
    sequence = Column(JSON)
    systems = Column(JSON)
    avg_duration = Column(Float)
    frequency = Column(Integer)
    participants = Column(Integer)
    confidence = Column(Float)


class WorkflowSession(Base):
    """A detected work session (group of events separated by inactivity gap)."""
    __tablename__ = "workflow_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_key = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Float)
    event_count = Column(Integer)
    app_sequence = Column(JSON)           # deduplicated ordered list
    apps_used = Column(JSON)              # unique apps unordered
    source_session_ids = Column(JSON)     # extension session IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DetectedBrief(Base):
    """
    Persisted intelligence brief — one row per generated brief.
    Allows history, caching, and downstream LLM retrieval without recomputation.
    """
    __tablename__ = "detected_briefs"

    id           = Column(Integer,  primary_key=True, index=True)
    brief_id     = Column(String,   unique=True, index=True)
    org_id       = Column(String,   index=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    hourly_rate  = Column(Float,    default=50.0)
    brief_json   = Column(JSON)     # full brief payload
    patterns_count   = Column(Integer, default=0)
    weekly_cost_gbp  = Column(Float,   default=0.0)
    annual_cost_gbp  = Column(Float,   default=0.0)

class AutomationBlueprint(Base):
    """
    Phase 2: Generated execution plan for a workflow pattern.
    Requires manual approval (Human-in-the-Loop) before deployment.
    """
    __tablename__ = "automation_blueprints"

    id             = Column(Integer, primary_key=True, index=True)
    org_id         = Column(String, index=True, default="org_default")
    pattern_id     = Column(String, index=True)
    name           = Column(String)
    blueprint_json = Column(JSON)
    status         = Column(String, default="pending_review") # pending_review, approved, rejected, deployed
    created_at     = Column(DateTime, default=datetime.datetime.utcnow)

class AutomationExecution(Base):
    """
    Phase 2: Execution logs for deployed blueprints (simulated for MVP).
    """
    __tablename__ = "automation_executions"

    id             = Column(Integer, primary_key=True, index=True)
    blueprint_id   = Column(Integer, index=True)
    status         = Column(String) # success, failed
    execution_time = Column(DateTime, default=datetime.datetime.utcnow)
    logs_json      = Column(JSON)
