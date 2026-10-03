'use client';

import { useState, useEffect, useCallback } from 'react';
import styles from './ROITrackerPanel.module.css';
import { API_BASE } from '@/lib/api';
import {
  RoiIcon,
  RefreshIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  AlertIcon,
  TrendingUpIcon,
} from './Icons';

export function RoiStatCard({ label, value, sub, colorClass }) {
  return (
    <div className={styles.roiStat}>
      <div className={styles.roiStatLabel}>{label}</div>
      <div className={`${styles.roiStatValue} ${styles[colorClass] || ''}`}>{value}</div>
      <div className={styles.roiStatSub}>{sub}</div>
    </div>
  );
}

export function RoiAutomationCard({ automation }) {
  return (
    <div className={styles.roiCard}>
      <div className={styles.roiCardHeader}>
        <div className={styles.roiCardTitle}>
          {automation.workflow_name || automation.blueprint_name}
        </div>
        <span className={styles.roiCardBadge}>Blueprint #{automation.blueprint_id}</span>
      </div>

      {/* Before ↔ After visualization */}
      <div className={styles.roiBeforeAfter}>
        <div className={styles.roiBeforeAfterCol}>
          <div className={styles.baLabel}>Pre-Automation Baseline</div>
          <div className={`${styles.baHrs} ${styles.colorRose}`}>
            {automation.before.hrs_per_week} hrs/wk
          </div>
          <div className={styles.baCost}>{automation.before.cost_per_week_label}</div>
        </div>

        <div className={styles.roiArrow}>
          <ArrowRightIcon size={18} />
        </div>

        <div className={styles.roiBeforeAfterCol}>
          <div className={styles.baLabel}>Post-Automation Measured</div>
          <div className={`${styles.baHrs} ${styles.colorGreen}`}>
            {automation.after.hrs_per_week} hrs/wk
          </div>
          <div className={styles.baCost}>
            {automation.after.cost_per_week_label} · {automation.after.automation_coverage_pct}% automated
          </div>
        </div>
      </div>

      {/* Verified Realized Savings Banner */}
      <div className={styles.roiSavingsBanner}>
        <div>
          <div className={styles.savingsLabel}>Verified Realized Savings</div>
          <div className={styles.savingsValue}>
            {automation.savings.cost_per_week_label} · {automation.savings.cost_per_year_label}
          </div>
        </div>
        <div className={styles.execStats}>
          <div>
            <strong>{automation.executions.total}</strong> runs
          </div>
          <div>
            <strong>{automation.executions.successful}</strong> successes
          </div>
          <div>
            <strong>{automation.executions.success_rate_pct}%</strong> rate
          </div>
          <div>
            <strong>{automation.savings.hrs_per_week} hrs</strong> saved/wk
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ROITrackerPanel({
  hourlyRate = 400,
  currency = 'INR',
  symbol = '₹',
}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchROI = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const enc = encodeURIComponent(symbol);
      const res = await fetch(
        `${API_BASE}/analytics/roi-impact?hourly_rate=${hourlyRate}&currency=${currency}&symbol=${enc}`
      );
      if (!res.ok) throw new Error('Failed to load ROI telemetry data');
      setData(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [hourlyRate, currency, symbol]);

  useEffect(() => {
    fetchROI();
  }, [fetchROI]);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <p>Calculating verified ROI telemetry...</p>
      </div>
    );
  }

  const summary = data?.summary || {};
  const automations = data?.automations || [];

  return (
    <div className={styles.roiContainer}>
      {/* Header */}
      <div className={styles.roiHeader}>
        <div className={styles.headerContent}>
          <h2>Verified ROI Impact &amp; Cost Recovery</h2>
          <p>
            Compares pre-automation labor baselines against production telemetry to mathematically
            verify exact time and monetary savings recovered by active automations.
          </p>
        </div>
        <button
          type="button"
          className={styles.refreshBtn}
          onClick={fetchROI}
        >
          <RefreshIcon size={13} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className={styles.errorBox}>
          <AlertIcon size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Summary Grid */}
      <div className={styles.roiSummaryGrid}>
        <RoiStatCard
          label="Deployed Automations"
          value={summary.deployed_automations ?? 0}
          colorClass="colorIndigo"
          sub="active production pipelines"
        />
        <RoiStatCard
          label="Weekly Cost Recovery"
          value={summary.weekly_savings_label || `${symbol}0`}
          colorClass="colorGreen"
          sub="recurring weekly benefit"
        />
        <RoiStatCard
          label="Annual Realized Recovery"
          value={summary.annual_savings_label || `${symbol}0`}
          colorClass="colorGreen"
          sub="verified annualized ROI"
        />
        <RoiStatCard
          label="Execution Volume"
          value={summary.total_executions ?? 0}
          colorClass="colorAmber"
          sub={`${summary.total_successful ?? 0} successful runs`}
        />
        <RoiStatCard
          label="Operational Coverage"
          value={`${summary.roi_multiplier ?? 0}%`}
          colorClass="colorGreen"
          sub="manual drag eliminated"
        />
      </div>

      {/* Per-automation cards */}
      {automations.length === 0 ? (
        <div className={styles.roiEmptyState}>
          <div className={styles.roiEmptyIcon}>
            <RoiIcon size={32} />
          </div>
          <div className={styles.roiEmptyTitle}>No active production automations yet</div>
          <p className={styles.roiEmptySub}>
            Authorize and deploy an automation blueprint from the <strong>Automation Blueprints</strong> gateway.
            Once running in production, this panel tracks before-and-after baseline metrics with live telemetry verification.
          </p>
        </div>
      ) : (
        automations.map((a) => (
          <RoiAutomationCard key={a.blueprint_id} automation={a} />
        ))
      )}

      {data?.generated_at && (
        <div className={styles.metaRow}>
          <span>Last calibrated: {new Date(data.generated_at).toLocaleTimeString()}</span>
        </div>
      )}
    </div>
  );
}
