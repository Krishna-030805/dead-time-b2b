// background.js — Dead Time B2B · Service Worker
// Receives events from content scripts, enriches with session context, POSTs to API.

const API_URL = "http://127.0.0.1:8002/events";

// ── Session Management ────────────────────────────────────────────────────────
// A session ID is a UUID-like string that persists within the browser session.
// It resets on browser restart or explicit reset.

function makeSessionId() {
  return "s_" + Date.now().toString(36) + "_" + Math.random().toString(36).substr(2, 7);
}

let sessionId = makeSessionId();
let lastEventTime = Date.now();
const SESSION_GAP_MS = 30 * 60 * 1000; // 30 minutes — must match backend

// Auto-rotate session if idle too long (browser doesn't restart between uses)
function getActiveSessionId() {
  const now = Date.now();
  if (now - lastEventTime > SESSION_GAP_MS) {
    sessionId = makeSessionId();
    console.log("[Dead Time] New session started:", sessionId);
  }
  lastEventTime = now;
  return sessionId;
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
chrome.runtime.onStartup.addListener(() => {
  sessionId = makeSessionId();
  lastEventTime = Date.now();
  console.log("[Dead Time] Browser started. Session:", sessionId);
});

// ── Event Handling ────────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type !== "WORKFLOW_EVENT") return true;

  const activeSession = getActiveSessionId();

  Promise.all([getUserId(), getOrgId()]).then(([userId, orgId]) => {
    const payload = {
      org_id:      orgId,
      user_id:     userId,
      timestamp:   request.data.timestamp,
      application: request.data.application,
      action_type: request.data.action_type,
      object_type: request.data.object_type  || null,
      object_id:   request.data.object_id   || null,
      session_id:  activeSession,
      metadata: {
        url:           request.data.url,
        title:         request.data.title,
        dwell_seconds: request.data.dwell_seconds || null,
      }
    };

    console.log(`[Dead Time] [${orgId}/${userId}] →`, payload.application, payload.action_type, payload.object_id);

    fetch(API_URL, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => console.log("[Dead Time] Saved event_id:", data.event_id))
      .catch(err => console.warn("[Dead Time] Failed to send event:", err.message));
  });

  return true; // keep message channel open for async
});
