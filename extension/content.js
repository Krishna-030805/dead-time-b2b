// content.js — Dead Time B2B · Enriched Activity Tracker
// Tracks: page loads, clicks, dwell time, tab visibility changes
// Privacy: No passwords, no form content, no keystrokes. URL + title + element label only.

console.log("[Dead Time] Recorder active →", window.location.hostname);

// ── App Detection ──────────────────────────────────────────────────────────────

function getApplicationName(url) {
  try {
    const h = new URL(url).hostname;
    if (h.includes("mail.google.com"))              return "gmail";
    if (h.includes("docs.google.com/spreadsheets")) return "google_sheets";
    if (h.includes("docs.google.com/document"))     return "google_docs";
    if (h.includes("docs.google.com/presentation")) return "google_slides";
    if (h.includes("drive.google.com"))             return "google_drive";
    if (h.includes("calendar.google.com"))          return "google_calendar";
    if (h.includes("meet.google.com"))              return "google_meet";
    if (h.includes("linkedin.com"))                 return "linkedin";
    if (h.includes("notion.so"))                    return "notion";
    if (h.includes("slack.com"))                    return "slack_web";
    if (h.includes("app.hubspot.com"))              return "hubspot";
    if (h.includes("salesforce.com"))               return "salesforce";
    if (h.includes("jira") || h.includes("atlassian.net")) return "jira";
    if (h.includes("trello.com"))                   return "trello";
    if (h.includes("asana.com"))                    return "asana";
    if (h.includes("pipedrive.com"))                return "pipedrive";
    if (h.includes("calendly.com"))                 return "calendly";
    if (h.includes("airtable.com"))                 return "airtable";
    if (h.includes("clickup.com"))                  return "clickup";
    if (h.includes("monday.com"))                   return "monday";
    if (h.includes("github.com"))                   return "github";
    if (h.includes("figma.com"))                    return "figma";
    if (h.includes("zoom.us"))                      return "zoom";
    if (h.includes("typeform.com"))                 return "typeform";
    if (h.includes("intercom.com"))                 return "intercom";
    if (h.includes("zendesk.com"))                  return "zendesk";
    if (h.includes("sheets.google") || h.includes("spreadsheet")) return "google_sheets";
    // Generic fallback: use cleaned hostname
    return h.replace(/^www\./, "").replace(/\.(com|io|net|org|co)$/, "").replace(/\./g, "_");
  } catch (e) {
    return "unknown";
  }
}

// ── Event Sender ──────────────────────────────────────────────────────────────

function sendEvent(action_type, object_type, object_id, extra = {}) {
  const url = window.location.href;
  chrome.runtime.sendMessage({
    type: "WORKFLOW_EVENT",
    data: {
      timestamp:    new Date().toISOString(),
      application:  getApplicationName(url),
      action_type,
      object_type,
      object_id:    String(object_id || "").substring(0, 60),
      url,
      title:        document.title,
      ...extra
    }
  });
}

// ── Page Load ─────────────────────────────────────────────────────────────────

sendEvent("open", "page", document.title.substring(0, 60));

// ── Dwell Time Tracking ───────────────────────────────────────────────────────
// When the user leaves this page, record how long they stayed.

let pageEntryTime = Date.now();

function recordDwell() {
  const dwell_seconds = Math.round((Date.now() - pageEntryTime) / 1000);
  if (dwell_seconds < 3) return; // Ignore bounces under 3 seconds
  sendEvent("dwell", "page", document.title.substring(0, 60), { dwell_seconds });
}

// Fires when tab loses focus or user navigates away
window.addEventListener("beforeunload", recordDwell);
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    recordDwell();
  } else {
    // User returned to this tab — reset timer
    pageEntryTime = Date.now();
  }
});

// ── Click Tracking ────────────────────────────────────────────────────────────

document.addEventListener("click", (e) => {
  const target = e.target;

  // Only track meaningful interactive elements
  const el = target.closest("button, a, [role='button'], [role='tab'], [role='menuitem'], [role='link']");
  if (!el) return;

  // Extract a clean, non-sensitive label
  let label = (
    el.getAttribute("aria-label") ||
    el.getAttribute("title")       ||
    el.innerText                   ||
    el.value                       ||
    el.id                          ||
    "button"
  ).trim().replace(/\s+/g, " ").substring(0, 50);

  // Skip empty or purely numeric labels (usually icons/IDs)
  if (!label || /^\d+$/.test(label)) return;

  // Never capture password fields, search inputs with actual text, or sensitive patterns
  const sensitivePatterns = /password|passwd|secret|token|api.key|credit.card|ssn/i;
  if (sensitivePatterns.test(label)) return;

  sendEvent("click", "ui_element", label);
}, true);

// ── Copy Detection (detect data extraction workflows) ─────────────────────────

document.addEventListener("copy", () => {
  sendEvent("copy", "clipboard", "text_copied");
});

// ── SPA Navigation Tracking (For sites like YouTube, Notion) ──────────────────

let lastUrl = window.location.href;
setInterval(() => {
  if (window.location.href !== lastUrl) {
    // URL changed without full page reload
    recordDwell(); // End dwell for previous page
    lastUrl = window.location.href;
    pageEntryTime = Date.now(); // Reset timer for new page
    sendEvent("open", "page", document.title.substring(0, 60));
  }
}, 1000);
