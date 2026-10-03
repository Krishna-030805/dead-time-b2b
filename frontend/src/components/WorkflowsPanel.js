'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import styles from './WorkflowsPanel.module.css';
import { fetchWorkflows, API_BASE } from '@/lib/api';
import { useToast } from './Toast';
import {
  WorkflowIcon,
  ClockIcon,
  RefreshIcon,
  TrendingUpIcon,
  ArrowRightIcon,
  ZapIcon,
  LayersIcon,
} from './Icons';

function esc(s) {
  return String(s || '');
}

export function WorkflowCard({ workflow, onGenerate, isGenerating }) {
  const tier = (workflow.opportunity_tier || 'low').toLowerCase();
  const conf = Math.round((workflow.confidence || 0) * 100);

  const tierClass =
    tier === 'high'
      ? styles.tierHigh
      : tier === 'medium'
      ? styles.tierMedium
      : styles.tierLow;

  const pillClass =
    tier === 'high'
      ? styles.pillHigh
      : tier === 'medium'
      ? styles.pillMedium
      : styles.pillLow;

  return (
    <div className={`${styles.card} ${tierClass}`}>
      <div className={styles.cardTop}>
        <div className={styles.name}>{esc(workflow.name)}</div>
        <span className={`${styles.pill} ${pillClass}`}>
          {tier.toUpperCase()} PRIORITY
        </span>
      </div>

      <div className={styles.sequence}>
        {(workflow.sequence || []).map((app, j) => (
          <span key={j} className={styles.seqItem}>
            <span className={styles.seqApp}>{app.replace(/_/g, ' ')}</span>
            {j < workflow.sequence.length - 1 && (
              <span className={styles.seqArrow}>
                <ArrowRightIcon size={12} />
              </span>
            )}
          </span>
        ))}
      </div>

      <div className={styles.metrics}>
        <div className={styles.metric}>
          <div className={styles.metricLabel}>
            <ClockIcon size={11} className={styles.metricIcon} />
            <span>Time Drag/Wk</span>
          </div>
          <div className={styles.metricValue} style={{ color: '#fbbf24' }}>
            {esc(workflow.time_cost_label)}
          </div>
          <div className={styles.metricSub}>
            {(workflow.total_time_hours_per_week || 0).toFixed(1)} hrs/wk
          </div>
        </div>

        <div className={styles.metric}>
          <div className={styles.metricLabel}>
            <RefreshIcon size={11} className={styles.metricIcon} />
            <span>Frequency</span>
          </div>
          <div className={styles.metricValue} style={{ color: '#34d399' }}>
            {workflow.frequency}x
          </div>
          <div className={styles.metricSub}>{workflow.avg_duration_minutes}m avg</div>
        </div>

        <div className={styles.metric}>
          <div className={styles.metricLabel}>
            <LayersIcon size={11} className={styles.metricIcon} />
            <span>Avg Session</span>
          </div>
          <div className={styles.metricValue}>{workflow.avg_duration_minutes}m</div>
          <div className={styles.metricSub}>per execution</div>
        </div>

        <div className={styles.metric}>
          <div className={styles.metricLabel}>
            <TrendingUpIcon size={11} className={styles.metricIcon} />
            <span>Pattern Confidence</span>
          </div>
          <div className={styles.metricValue} style={{ color: '#60a5fa' }}>
            {conf}%
          </div>
          <div className={styles.metricSub}>match stability</div>
        </div>
      </div>

      <div className={styles.footer}>
        <span className={styles.patternId}>{esc(workflow.pattern_id)}</span>
        <button
          type="button"
          className={styles.blueprintBtn}
          onClick={() => onGenerate(workflow.pattern_id)}
          disabled={isGenerating}
        >
          <ZapIcon size={13} />
          <span>{isGenerating ? 'Synthesizing...' : 'Generate Blueprint'}</span>
        </button>
      </div>
    </div>
  );
}

export default function WorkflowsPanel({ onCount }) {
  const [workflows, setWorkflows] = useState([]);
  const [generating, setGenerating] = useState(null);
  const { showToast } = useToast();

  const onCountRef = useRef(onCount);
  useEffect(() => {
    onCountRef.current = onCount;
  }, [onCount]);

  const load = useCallback(async () => {
    try {
      const data = await fetchWorkflows();
      setWorkflows(data);
      onCountRef.current?.(data.length);
    } catch {}
  }, []);

  const handleGenerateBlueprint = async (patternId) => {
    try {
      setGenerating(patternId);
      const res = await fetch(`${API_BASE}/blueprints/generate?pattern_id=${patternId}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to generate blueprint');
      showToast(
        'Automation Blueprint synthesized successfully. Review in Automation Blueprints.',
        'success'
      );
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setGenerating(null);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 18000);
    return () => clearInterval(id);
  }, [load]);

  if (!workflows.length) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyIcon}>
          <WorkflowIcon size={32} />
        </div>
        <p>No recurring bottleneck patterns detected yet.</p>
        <span className={styles.emptySub}>
          Telemetry ingestion agent is monitoring active application transitions.
        </span>
      </div>
    );
  }

  return (
    <div>
      <div className={styles.intro}>
        <div className={styles.introContent}>
          <strong>Phase 1 Audit Findings:</strong> Telemetry ingestion models cross-application
          transitions into workflow sequence clusters. Identified patterns below represent quantified
          operational dead time, prioritized by weekly labor expenditure.
        </div>
      </div>

      <div className={styles.sectionHeader}>
        <h2>Identified Bottleneck Patterns</h2>
        <span className={styles.note}>{workflows.length} workflows discovered</span>
      </div>

      <div className={styles.grid}>
        {workflows.map((p, i) => (
          <WorkflowCard
            key={p.pattern_id || i}
            workflow={p}
            onGenerate={handleGenerateBlueprint}
            isGenerating={generating === p.pattern_id}
          />
        ))}
      </div>
    </div>
  );
}
