'use client';

import { useEffect, useState, useCallback } from 'react';
import styles from './StatsStrip.module.css';
import { fetchBrief, API_BASE } from '@/lib/api';
import {
  ActivityIcon,
  FolderIcon,
  WorkflowIcon,
  TrendingUpIcon,
  CheckCircleIcon,
} from './Icons';

export function StatCard({ label, value, sub, variant = 'neutral', icon: IconComponent }) {
  const variantClass = styles[`variant_${variant}`] || styles.variant_neutral;

  return (
    <div className={`${styles.card} ${variantClass}`}>
      <div className={styles.cardHeader}>
        <span className={styles.label}>{label}</span>
        {IconComponent && (
          <span className={styles.cardIcon}>
            <IconComponent size={14} />
          </span>
        )}
      </div>
      <div className={styles.value}>{value}</div>
      <div className={styles.sub}>{sub}</div>
    </div>
  );
}

export default function StatsStrip({
  hourlyRate = 400,
  currency = { symbol: '₹', code: 'INR' },
  onRealizedSavings,
}) {
  const [stats, setStats] = useState(null);

  const load = useCallback(async () => {
    try {
      const d = await fetchBrief(hourlyRate, currency.code, currency.symbol);
      const ex = d.executive_summary || {};

      let realizedLabel = `${currency.symbol}0/yr`;
      try {
        const enc = encodeURIComponent(currency.symbol);
        const roiRes = await fetch(
          `${API_BASE}/analytics/roi-impact?hourly_rate=${hourlyRate}&currency=${currency.code}&symbol=${enc}`
        );
        if (roiRes.ok) {
          const roi = await roiRes.json();
          const annual = roi?.summary?.annual_savings_label;
          if (annual && annual !== `${currency.symbol}0`) {
            realizedLabel = annual;
          }
        }
      } catch {}

      setStats({
        events: ex.total_events_captured ?? 0,
        sessions: ex.total_sessions_detected ?? 0,
        patterns: ex.total_workflows_identified ?? 0,
        weeklyCost: ex.weekly_cost_across_workflows || `${currency.symbol}0`,
        recoverable: ex.recoverable_annually || `${currency.symbol}0`,
        realized: realizedLabel,
      });

      if (onRealizedSavings && realizedLabel && realizedLabel !== `${currency.symbol}0/yr`) {
        onRealizedSavings(realizedLabel);
      }
    } catch {}
  }, [hourlyRate, currency, onRealizedSavings]);

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, [load]);

  const cards = [
    {
      key: 'events',
      label: 'Telemetry Events',
      value: stats?.events != null ? stats.events.toLocaleString() : '—',
      variant: 'blue',
      sub: 'Signals ingested',
      icon: ActivityIcon,
    },
    {
      key: 'sessions',
      label: 'Clustered Sessions',
      value: stats?.sessions != null ? stats.sessions.toLocaleString() : '—',
      variant: 'neutral',
      sub: 'Work sessions detected',
      icon: FolderIcon,
    },
    {
      key: 'patterns',
      label: 'Bottleneck Patterns',
      value: stats?.patterns != null ? stats.patterns.toLocaleString() : '—',
      variant: 'amber',
      sub: 'Recurring manual workflows',
      icon: WorkflowIcon,
    },
    {
      key: 'weeklyCost',
      label: 'Manual Process Drag',
      value: stats?.weeklyCost ?? '—',
      variant: 'rose',
      sub: 'Weekly labor hemorrhage',
      icon: TrendingUpIcon,
    },
    {
      key: 'recoverable',
      label: 'Recoverable Annually',
      value: stats?.recoverable ?? '—',
      variant: 'emerald',
      sub: 'At target 80% automation',
      icon: CheckCircleIcon,
    },
    {
      key: 'realized',
      label: 'Realized Savings',
      value: stats?.realized ?? '—',
      variant: 'emeraldHighlight',
      sub: 'Verified live cost recovery',
      icon: CheckCircleIcon,
    },
  ];

  return (
    <div className={styles.grid}>
      {cards.map((c) => (
        <StatCard
          key={c.key}
          label={c.label}
          value={c.value}
          variant={c.variant}
          sub={c.sub}
          icon={c.icon}
        />
      ))}
    </div>
  );
}
