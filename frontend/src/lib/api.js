export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

/**
 * Centralised API client for the Dead Time backend.
 * Every function returns a parsed JSON promise.
 */

export async function fetchEvents(limit = 80) {
  const res = await fetch(`${API_BASE}/events?limit=${limit}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Events fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/sessions`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Sessions fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchWorkflows() {
  const res = await fetch(`${API_BASE}/workflows/detected`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Workflows fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchBrief(hourlyRate = 400, currency = 'INR', symbol = '₹') {
  const encSymbol = encodeURIComponent(symbol);
  const res = await fetch(`${API_BASE}/workflows/brief?hourly_rate=${hourlyRate}&currency=${currency}&symbol=${encSymbol}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Brief fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchAIAnalysis(hourlyRate = 400, currency = 'INR', symbol = '₹') {
  const encSymbol = encodeURIComponent(symbol);
  const res = await fetch(`${API_BASE}/workflows/ai-analysis?hourly_rate=${hourlyRate}&currency=${currency}&symbol=${encSymbol}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`AI analysis fetch failed: ${res.status}`);
  return res.json();
}

export function getPDFDownloadURL(hourlyRate = 400, orgId = 'org_demo', currency = 'INR', symbol = '₹') {
  const encSymbol = encodeURIComponent(symbol);
  return `${API_BASE}/workflows/report/pdf?hourly_rate=${hourlyRate}&org_id=${orgId}&currency=${currency}&symbol=${encSymbol}`;
}

export function getReportURL(hourlyRate = 400, currency = 'INR', symbol = '₹', orgId = 'org_demo') {
  const encSymbol = encodeURIComponent(symbol);
  return `${API_BASE}/workflows/report?hourly_rate=${hourlyRate}&org_id=${orgId}&currency=${currency}&symbol=${encSymbol}`;
}

export function getBriefURL(hourlyRate = 400, currency = 'INR', symbol = '₹', orgId = 'org_demo') {
  const encSymbol = encodeURIComponent(symbol);
  return `${API_BASE}/workflows/brief?hourly_rate=${hourlyRate}&org_id=${orgId}&currency=${currency}&symbol=${encSymbol}`;
}
