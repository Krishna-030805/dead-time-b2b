"""
workflow_detector.py
====================
Layer 2 — Deterministic Workflow Reconstruction Engine

Algorithm pipeline:
  1. Ingest raw events (sorted by timestamp)
  2. Split into sessions (gap > SESSION_GAP_MINUTES = new session)
  3. Normalize each session into a clean app-sequence
  4. Mine n-grams (sub-sequences of length MIN_N..MAX_N) across all sessions
  5. Score patterns by frequency x avg_duration → total weekly time cost
  6. Return ranked WorkflowPattern objects

No LLM, no external ML libraries. Pure deterministic Python.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


# ─── Configuration ────────────────────────────────────────────────────────────

SESSION_GAP_MINUTES: int = 30       # inactivity threshold that closes a session
MIN_SESSION_EVENTS: int = 2         # sessions with fewer events are discarded
MIN_PATTERN_FREQUENCY: int = 2      # patterns seen fewer times are discarded
MIN_NGRAM_LENGTH: int = 2           # shortest pattern we care about
MAX_NGRAM_LENGTH: int = 6           # longest pattern we care about
WEEKLY_EXTRAPOLATION_DAYS: int = 5  # window for active business days projection (Mon-Fri)

# Automation opportunity thresholds (total_time_hours_per_week)
OPPORTUNITY_HIGH_HOURS: float = 3.0
OPPORTUNITY_MED_HOURS: float = 1.0


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class RawEvent:
    id: int
    user_id: str
    session_id: str
    timestamp: datetime
    application: str
    action_type: str
    object_type: Optional[str]
    object_id: Optional[str]
    metadata_json: Optional[Dict[str, Any]]


@dataclass
class DetectedSession:
    session_key: str                  # composite: user_id + ordinal
    user_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    event_count: int
    app_sequence: List[str]           # deduplicated ordered app list
    raw_sequence: List[str]           # full app list (one per event)
    apps_used: List[str]              # unique apps (unordered)
    source_session_ids: List[str]     # original extension session IDs

    @property
    def duration_label(self) -> str:
        m = int(self.duration_minutes)
        h, mins = divmod(m, 60)
        return f"{h}h {mins}m" if h else f"{mins}m"


@dataclass
class WorkflowPattern:
    pattern_id: str                   # stable hash of the sequence
    sequence: List[str]               # e.g. ["gmail","linkedin","google_sheets"]
    name: str                         # human-readable label
    frequency: int                    # number of sessions this pattern appeared in
    avg_duration_minutes: float       # average session duration for sessions with this pattern
    total_time_minutes_observed: float
    total_time_hours_per_week: float  # extrapolated weekly cost
    time_cost_label: str              # e.g. "4h 28min/week"
    opportunity_tier: str             # "high" / "medium" / "low"
    confidence: float                 # frequency / total_sessions (0.0–1.0)
    supporting_sessions: List[str]    # session_key list
    apps: List[str]                   # unique apps in pattern

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─── Helper Utilities ─────────────────────────────────────────────────────────

def _stable_id(sequence: List[str]) -> str:
    """Produce a short stable hash for a sequence (used as pattern_id)."""
    raw = "→".join(sequence).encode()
    return "wp_" + hashlib.sha1(raw).hexdigest()[:10]


def _deduplicate_consecutive(seq: List[str]) -> List[str]:
    """Remove consecutive duplicates: [a, a, b, b, b, c] → [a, b, c]."""
    result: List[str] = []
    for item in seq:
        if not result or result[-1] != item:
            result.append(item)
    return result


def _format_time(total_minutes: float) -> str:
    """Convert float minutes to human-readable string."""
    total = int(total_minutes)
    h, m = divmod(total, 60)
    if h > 0:
        return f"{h}h {m}min"
    return f"{m}min"


def _opportunity_tier(hours_per_week: float) -> str:
    if hours_per_week >= OPPORTUNITY_HIGH_HOURS:
        return "high"
    if hours_per_week >= OPPORTUNITY_MED_HOURS:
        return "medium"
    return "low"


# ─── Core Engine ──────────────────────────────────────────────────────────────

class WorkflowDetector:
    """
    Full detection pipeline:
      detect(raw_events) → (sessions, patterns)
    """

    # ── Step 1: Session Splitting ──────────────────────────────────────────────

    def split_into_sessions(self, raw_events: List[RawEvent]) -> List[DetectedSession]:
        """
        Group events by user_id, then split on inactivity gaps.
        Returns sorted list of DetectedSession objects.
        """
        # Group events by user
        by_user: Dict[str, List[RawEvent]] = defaultdict(list)
        for ev in raw_events:
            by_user[ev.user_id].append(ev)

        sessions: List[DetectedSession] = []
        gap = timedelta(minutes=SESSION_GAP_MINUTES)

        for user_id, events in by_user.items():
            # Sort events chronologically
            events.sort(key=lambda e: e.timestamp)

            current_chunk: List[RawEvent] = []

            for ev in events:
                if not current_chunk:
                    current_chunk.append(ev)
                    continue

                delta = ev.timestamp - current_chunk[-1].timestamp
                if delta > gap:
                    # Close current session and start new one
                    sess = self._build_session(user_id, current_chunk, len(sessions))
                    if sess:
                        sessions.append(sess)
                    current_chunk = [ev]
                else:
                    current_chunk.append(ev)

            # Don't forget the last chunk
            if current_chunk:
                sess = self._build_session(user_id, current_chunk, len(sessions))
                if sess:
                    sessions.append(sess)

        return sessions

    def _build_session(
        self, user_id: str, events: List[RawEvent], ordinal: int
    ) -> Optional[DetectedSession]:
        """Convert a raw event chunk into a DetectedSession."""
        if len(events) < MIN_SESSION_EVENTS:
            return None

        start = events[0].timestamp
        end = events[-1].timestamp
        duration_minutes = max((end - start).total_seconds() / 60.0, 0.1)

        raw_seq = [e.application for e in events]
        app_seq = _deduplicate_consecutive(raw_seq)

        # Filter out sessions that are just one app repeated
        if len(app_seq) < 1:
            return None

        return DetectedSession(
            session_key=f"{user_id}_sess_{ordinal:04d}",
            user_id=user_id,
            start_time=start,
            end_time=end,
            duration_minutes=duration_minutes,
            event_count=len(events),
            app_sequence=app_seq,
            raw_sequence=raw_seq,
            apps_used=list(dict.fromkeys(raw_seq)),  # preserve order, deduplicate
            source_session_ids=list({e.session_id for e in events}),
        )

    # ── Step 2: N-gram Mining ──────────────────────────────────────────────────

    def mine_ngrams(
        self, sessions: List[DetectedSession]
    ) -> Tuple[Counter, Dict[str, List[str]]]:
        """
        Extract all sub-sequences (n-grams) from session app sequences.
        Returns:
          - ngram_counts: Counter({tuple: frequency})
          - ngram_to_sessions: {ngram_key: [session_key, ...]}
        """
        ngram_counts: Counter = Counter()
        ngram_to_sessions: Dict[str, List[str]] = defaultdict(list)

        for sess in sessions:
            seq = sess.app_sequence
            seen_in_session: set = set()

            for n in range(MIN_NGRAM_LENGTH, min(MAX_NGRAM_LENGTH + 1, len(seq) + 1)):
                for i in range(len(seq) - n + 1):
                    gram = tuple(seq[i : i + n])
                    key = "→".join(gram)

                    # Count each ngram at most once per session (avoid inflation)
                    if key not in seen_in_session:
                        ngram_counts[gram] += 1
                        ngram_to_sessions[key].append(sess.session_key)
                        seen_in_session.add(key)

        return ngram_counts, ngram_to_sessions

    # ── Step 3: Pattern Building & Scoring ────────────────────────────────────

    def build_patterns(
        self,
        ngram_counts: Counter,
        ngram_to_sessions: Dict[str, List[str]],
        sessions: List[DetectedSession],
        observation_days: int = 1,
    ) -> List[WorkflowPattern]:
        """
        For each n-gram above MIN_PATTERN_FREQUENCY, create a scored WorkflowPattern.
        Patterns are deduplicated: if [A→B→C] exists, sub-grams [A→B] and [B→C]
        that are entirely subsumed by a longer pattern are suppressed.
        """
        session_by_key: Dict[str, DetectedSession] = {
            s.session_key: s for s in sessions
        }
        total_sessions = max(len(sessions), 1)

        # Collect candidate patterns
        candidates: List[WorkflowPattern] = []
        for gram, freq in ngram_counts.items():
            if freq < MIN_PATTERN_FREQUENCY:
                continue

            gram_list = list(gram)
            key = "→".join(gram_list)
            supporting = ngram_to_sessions.get(key, [])

            # Average duration of sessions containing this pattern
            durations = [
                session_by_key[sk].duration_minutes
                for sk in supporting
                if sk in session_by_key
            ]
            avg_dur = sum(durations) / len(durations) if durations else 0.0
            total_observed = avg_dur * freq

            # Extrapolate to weekly (based on observation window)
            weekly_factor = WEEKLY_EXTRAPOLATION_DAYS / max(observation_days, 1)
            weekly_hours = (total_observed * weekly_factor) / 60.0

            pattern = WorkflowPattern(
                pattern_id=_stable_id(gram_list),
                sequence=gram_list,
                name=" → ".join(gram_list).replace("_", " ").title(),
                frequency=freq,
                avg_duration_minutes=round(avg_dur, 1),
                total_time_minutes_observed=round(total_observed, 1),
                total_time_hours_per_week=round(weekly_hours, 2),
                time_cost_label=_format_time(weekly_hours * 60),
                opportunity_tier=_opportunity_tier(weekly_hours),
                confidence=round(freq / total_sessions, 2),
                supporting_sessions=supporting,
                apps=list(dict.fromkeys(gram_list)),
            )
            candidates.append(pattern)

        # Suppress sub-patterns that are fully covered by longer patterns
        candidates = self._suppress_subpatterns(candidates)

        # Sort: high opportunity first, then by frequency desc
        tier_order = {"high": 0, "medium": 1, "low": 2}
        candidates.sort(
            key=lambda p: (tier_order.get(p.opportunity_tier, 9), -p.frequency)
        )

        return candidates

    def _suppress_subpatterns(
        self, patterns: List[WorkflowPattern]
    ) -> List[WorkflowPattern]:
        """
        Remove patterns whose sequence is a subsequence of a longer, more-frequent pattern.
        This prevents noise like [A→B] when [A→B→C→D] already covers it.
        """
        kept: List[WorkflowPattern] = []
        pattern_seqs = [p.sequence for p in patterns]

        for p in patterns:
            subsumed = False
            for longer in pattern_seqs:
                if len(longer) <= len(p.sequence):
                    continue
                # Check if p.sequence is a contiguous sublist of longer
                seq_str = "→".join(longer)
                sub_str = "→".join(p.sequence)
                if sub_str in seq_str:
                    subsumed = True
                    break
            if not subsumed:
                kept.append(p)

        # If suppression removed everything, fall back to unsuppressed list
        return kept if kept else patterns

    # ── Full Pipeline ──────────────────────────────────────────────────────────

    def detect(
        self, raw_events: List[RawEvent], observation_days: int = 1
    ) -> Dict[str, Any]:
        """
        Full detection pipeline.
        Returns dict with 'sessions' and 'patterns'.
        """
        if not raw_events:
            return {"sessions": [], "patterns": [], "summary": _empty_summary()}

        sessions = self.split_into_sessions(raw_events)
        ngram_counts, ngram_to_sessions = self.mine_ngrams(sessions)
        patterns = self.build_patterns(
            ngram_counts, ngram_to_sessions, sessions, observation_days
        )

        # Compute summary stats
        total_events = len(raw_events)
        total_time_mapped = sum(s.duration_minutes for s in sessions)
        apps_seen = set()
        for s in sessions:
            apps_seen.update(s.apps_used)

        summary = {
            "total_events": total_events,
            "total_sessions": len(sessions),
            "total_workflows_detected": len(patterns),
            "apps_seen": sorted(apps_seen),
            "total_time_mapped_minutes": round(total_time_mapped, 1),
            "total_time_mapped_label": _format_time(total_time_mapped),
            "high_opportunity_count": sum(
                1 for p in patterns if p.opportunity_tier == "high"
            ),
            "medium_opportunity_count": sum(
                1 for p in patterns if p.opportunity_tier == "medium"
            ),
        }

        # Pseudonymize employee identities to anonymous seats (e.g. "Seat 1", "Seat 2")
        # to ensure privacy and prevent individual surveillance perception
        unique_users = sorted(list({s.user_id for s in sessions}))
        user_to_seat = {u: f"Seat {i+1}" for i, u in enumerate(unique_users)}
        for s in sessions:
            s.user_id = user_to_seat.get(s.user_id, s.user_id)

        return {
            "sessions": [_session_to_dict(s) for s in sessions],
            "patterns": [p.to_dict() for p in patterns],
            "summary": summary,
        }


# ─── Serialization Helpers ────────────────────────────────────────────────────

def _session_to_dict(s: DetectedSession) -> Dict[str, Any]:
    return {
        "session_key": s.session_key,
        "user_id": s.user_id,
        "start_time": s.start_time.isoformat(),
        "end_time": s.end_time.isoformat(),
        "duration_minutes": round(s.duration_minutes, 1),
        "duration_label": s.duration_label,
        "event_count": s.event_count,
        "app_sequence": s.app_sequence,
        "apps_used": s.apps_used,
        "source_session_ids": s.source_session_ids,
    }


def _empty_summary() -> Dict[str, Any]:
    return {
        "total_events": 0,
        "total_sessions": 0,
        "total_workflows_detected": 0,
        "apps_seen": [],
        "total_time_mapped_minutes": 0,
        "total_time_mapped_label": "0m",
        "high_opportunity_count": 0,
        "medium_opportunity_count": 0,
    }
