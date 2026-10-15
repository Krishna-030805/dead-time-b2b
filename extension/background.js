// background.js — Dead Time B2B · Service Worker
// Receives events from content scripts, enriches with session context, POSTs to API.

const API_URL = "https://dead-time-backend.onrender.com/events";

// ── Session Management ────────────────────────────────────────────────────────
// A session ID is a UUID-like string that persists within the browser session.
// It resets on browser restart or explicit reset.

function makeSessionId() {
  return "s_" + Date.now().toString(36) + "_" + Math.random().toString(36).substr(2, 7);
}

const SESSION_GAP_MS = 30 * 60 * 1000; // 30 minutes — matches backend

// Auto-rotate session if idle too long (persisted in chrome.storage so service worker shutdowns don't reset timer)
async function getActiveSessionId() {
  const now = Date.now();
  try {
    const data = await chrome.storage.local.get(["active_session_id", "last_event_time"]);
    const lastTime = Number(data.last_event_time || 0);
    let currentSession = data.active_session_id;

    // Inactivity threshold: if no event occurred for >30 minutes, rotate session ID
    if (!currentSession || (lastTime > 0 && (now - lastTime > SESSION_GAP_MS))) {
      currentSession = makeSessionId();
      console.log("[Dead Time] Inactivity threshold exceeded (>30m). Rotated session:", currentSession);
    }

    await chrome.storage.local.set({
      active_session_id: currentSession,
      last_event_time: now,
    });
    return currentSession;
  } catch {
    return makeSessionId();
  }
}

// Helper: Get or initialize persistent device/user identifier
async function getUserId() {
  try {
    const res = await chrome.storage.local.get(["user_id"]);
    if (res.user_id && res.user_id.trim()) {
      return res.user_id.trim();
    }
    const autoId = "device_" + Math.random().toString(36).substring(2, 8);
    await chrome.storage.local.set({ user_id: autoId });
    return autoId;
  } catch {
    return "device_main";
  }
}

// Helper: Get or initialize persistent client/organization identifier
async function getOrgId() {
  try {
    const res = await chrome.storage.local.get(["org_id"]);
    if (res.org_id && res.org_id.trim()) {
      return res.org_id.trim();
    }
    return "org_default";
  } catch {
    return "org_default";
  }
}

// Reset on browser startup
chrome.runtime.onStartup.addListener(async () => {
  const newSession = makeSessionId();
  await chrome.storage.local.set({
    active_session_id: newSession,
    last_event_time: Date.now(),
  });
  console.log("[Dead Time] Browser started. Fresh session:", newSession);
});

// ── Event Handling ────────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type !== "WORKFLOW_EVENT") return true;

  chrome.storage.local.get(["telemetry_paused"]).then(async (storage) => {
    if (storage.telemetry_paused) {
      return;
    }

    const activeSession = await getActiveSessionId();

    Promise.all([getUserId(), getOrgId()]).then(([userId, orgId]) => {
      const payload = {
        org_id:      orgId,
        user_id:     userId,
        timestamp:   request.data.timestamp,
        application: request.data.application,
        action_type: request.data.action_type,
        object_type: request.data.object_type  || null,
        object_id:   null, // Stripped for privacy
        session_id:  activeSession,
        metadata: {
          app_token:     request.data.application,
          dwell_seconds: request.data.dwell_seconds || null,
        }
      };

      console.log(`[Dead Time] [${orgId}/${userId}] →`, payload.application, payload.action_type);

      chrome.storage.local.get(["ingest_token"]).then((tok) => {
        const headers = { "Content-Type": "application/json" };
        if (tok.ingest_token) {
          headers["Authorization"] = `Bearer ${tok.ingest_token}`;
        }

        fetch(API_URL, {
          method:  "POST",
          headers: headers,
          body:    JSON.stringify(payload)
        })
          .then(res => res.json())
          .then(data => console.log("[Dead Time] Saved event_id:", data.event_id))
          .catch(err => console.warn("[Dead Time] Failed to send event:", err.message));
      });
    });
  });

  return true; // keep message channel open for async
});
