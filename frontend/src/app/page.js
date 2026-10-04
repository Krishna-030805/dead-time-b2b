'use client';

import { useState, useCallback, useEffect } from 'react';
import Header from '@/components/Header';
import StatsStrip from '@/components/StatsStrip';
import TabBar from '@/components/TabBar';
import WorkflowsPanel from '@/components/WorkflowsPanel';
import AIInsightsPanel from '@/components/AIInsightsPanel';
import BlueprintReviewPanel from '@/components/BlueprintReviewPanel';
import ROITrackerPanel from '@/components/ROITrackerPanel';
import AuditTrailPanel from '@/components/AuditTrailPanel';
import Footer from '@/components/Footer';
import { ToastProvider } from '@/components/Toast';
import { CURRENCIES, detectUserCurrency } from '@/lib/currency';
import { API_BASE } from '@/lib/api';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('workflows');
  const [counts, setCounts] = useState({});
  const [currency, setCurrency] = useState(CURRENCIES.INR);
  const [hourlyRate, setHourlyRate] = useState(CURRENCIES.INR.defaultRate);
  const [realizedSavings, setRealizedSavings] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState('all');
  const [organizations, setOrganizations] = useState(['org_default']);

  // Read ?org= or ?org_id= from URL to isolate client workspace on screen-share
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const orgParam = params.get('org') || params.get('org_id');
      if (orgParam) {
        setSelectedOrg(orgParam);
      }
    }
  }, []);

  // Fetch client organizations
  useEffect(() => {
    fetch(`${API_BASE}/organizations`)
      .then((r) => r.json())
      .then((d) => {
        if (d.organizations && d.organizations.length > 0) {
          setOrganizations(d.organizations);
        }
      })
      .catch(() => {});
  }, []);

  // Auto-detect on client mount & fetch initial badge counts
  useEffect(() => {
    const detected = detectUserCurrency();
    setCurrency(detected);
    setHourlyRate(detected.defaultRate);

    // Initial load of badge counts across tabs
    fetch(`${API_BASE}/blueprints`)
      .then((r) => r.json())
      .then((bps) => setCounts((prev) => ({ ...prev, blueprints: bps.length })))
      .catch(() => {});

    fetch(`${API_BASE}/workflows/detected`)
      .then((r) => r.json())
      .then((wfs) => setCounts((prev) => ({ ...prev, workflows: wfs.length })))
      .catch(() => {});

    fetch(`${API_BASE}/sessions`)
      .then((r) => r.json())
      .then((sess) => setCounts((prev) => ({ ...prev, sessions: sess.length })))
      .catch(() => {});

    fetch(`${API_BASE}/events?limit=1`)
      .then((r) => r.json())
      .then((evts) => setCounts((prev) => ({ ...prev, events: evts.length })))
      .catch(() => {});
  }, []);

  const handleCurrencyChange = useCallback((newCurrency) => {
    setCurrency(newCurrency);
    setHourlyRate(newCurrency.defaultRate);
    try {
      localStorage.setItem('dt_currency', newCurrency.code);
    } catch {}
  }, []);

  const updateCount = useCallback((key, count) => {
    setCounts((prev) => {
      if (prev[key] === count) return prev;
      return { ...prev, [key]: count };
    });
  }, []);

  const handleEventsCount = useCallback((count) => updateCount('events', count), [updateCount]);
  const handleSessionsCount = useCallback((count) => updateCount('sessions', count), [updateCount]);
  const handleWorkflowsCount = useCallback((count) => updateCount('workflows', count), [updateCount]);
  const handleBlueprintsCount = useCallback((count) => updateCount('blueprints', count), [updateCount]);

  const tabCounts = {
    ...counts,
    audit: counts.events || counts.sessions || undefined,
  };

  return (
    <ToastProvider>
      <div className="app">
        <Header
          hourlyRate={hourlyRate}
          setHourlyRate={setHourlyRate}
          currency={currency}
          onCurrencyChange={handleCurrencyChange}
          realizedSavings={realizedSavings}
          selectedOrg={selectedOrg}
          onOrgChange={setSelectedOrg}
          organizations={organizations}
        />

        <StatsStrip
          hourlyRate={hourlyRate}
          currency={currency}
          onRealizedSavings={setRealizedSavings}
          selectedOrg={selectedOrg}
        />

        <TabBar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          counts={tabCounts}
        />

        {activeTab === 'workflows' && (
          <div className="panel" role="tabpanel">
            <WorkflowsPanel onCount={handleWorkflowsCount} selectedOrg={selectedOrg} />
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="panel" role="tabpanel">
            <AIInsightsPanel hourlyRate={hourlyRate} currency={currency} selectedOrg={selectedOrg} />
          </div>
        )}

        {activeTab === 'blueprints' && (
          <div className="panel" role="tabpanel">
            <BlueprintReviewPanel onCount={handleBlueprintsCount} />
          </div>
        )}

        {activeTab === 'roi' && (
          <div className="panel" role="tabpanel">
            <ROITrackerPanel
              hourlyRate={hourlyRate}
              currency={currency.code}
              symbol={currency.symbol}
              selectedOrg={selectedOrg}
            />
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="panel" role="tabpanel">
            <AuditTrailPanel
              onEventsCount={handleEventsCount}
              onSessionsCount={handleSessionsCount}
              selectedOrg={selectedOrg}
            />
          </div>
        )}

        <Footer />
      </div>
    </ToastProvider>
  );
}
