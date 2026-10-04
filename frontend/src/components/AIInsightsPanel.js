'use client';

import { useState } from 'react';
import styles from './AIInsightsPanel.module.css';
import { fetchAIAnalysis } from '@/lib/api';
import {
  InsightsIcon,
  ZapIcon,
  ClockIcon,
  TrendingUpIcon,
  RefreshIcon,
  AlertIcon,
  CheckCircleIcon,
  LayersIcon,
} from './Icons';

function esc(s) {
  return String(s || '');
}

export function OpportunityHero({ opportunity }) {
  if (!opportunity || !opportunity.workflow_name) return null;
  const cx = opportunity.complexity || 'Medium';

  return (
    <div className={styles.topOppCard}>
      <div className={styles.topOppBanner}>
        <ZapIcon size={13} />
        <span>Highest ROI Strategic Target — Primary Automation Candidate</span>
      </div>
      <div className={styles.topOppBody}>
        <div className={styles.toolBadge}>
          <LayersIcon size={13} />
          <span>Recommended Architecture: {esc(opportunity.recommended_tool)}</span>
        </div>
        <div className={styles.oppName}>{esc(opportunity.workflow_name)}</div>
        <div className={styles.oppWhat}>
          {esc(opportunity.what_gets_automated || opportunity.why_this_tool)}
        </div>

        {opportunity.automation_steps?.length > 0 && (
          <ol className={styles.stepsList}>
            {opportunity.automation_steps.map((s, i) => (
              <li key={i}>{esc(s)}</li>
            ))}
          </ol>
        )}

        <div className={styles.oppMetrics}>
          <div className={styles.metricBox}>
            <div className={styles.metricLabel}>
              <ClockIcon size={11} />
              <span>Hours Recovered/Wk</span>
            </div>
            <div className={styles.metricValue} style={{ color: '#34d399' }}>
              {opportunity.estimated_hours_saved_per_week || 0} hrs/wk
            </div>
          </div>
          <div className={styles.metricBox}>
            <div className={styles.metricLabel}>
              <TrendingUpIcon size={11} />
              <span>Payback Timeline</span>
            </div>
            <div className={styles.metricValue} style={{ color: '#fbbf24' }}>
              {esc(opportunity.payback_period_label || 'Immediate')}
            </div>
          </div>
          <div className={styles.metricBox}>
            <div className={styles.metricLabel}>
              <LayersIcon size={11} />
              <span>Engineering Complexity</span>
            </div>
            <div className={styles.metricValue}>
              <span className={`${styles.complexityBadge} ${styles['cx' + cx]}`}>{cx}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function QuickWinCard({ win }) {
  return (
    <div className={styles.winCard}>
      <div className={styles.winHeader}>
        <CheckCircleIcon size={14} className={styles.winIcon} />
        <div className={styles.winTitle}>{esc(win.title)}</div>
      </div>
      <div className={styles.winDesc}>{esc(win.description)}</div>
      <div className={styles.winTime}>
        <ClockIcon size={11} />
        <span>Target Recovery: {esc(win.time_saved)}</span>
      </div>
    </div>
  );
}

export function AssessmentCard({ assessment }) {
  const cx = assessment.complexity || 'Medium';

  return (
    <div className={styles.assessCard}>
      <div className={styles.assessHeader}>
        <div className={styles.assessName}>{esc(assessment.workflow_name)}</div>
        <span className={`${styles.complexityBadge} ${styles['cx' + cx]}`}>{cx}</span>
      </div>
      <div className={styles.assessApproach}>{esc(assessment.automation_approach)}</div>
      {(assessment.required_integrations || []).length > 0 && (
        <div className={styles.integrations}>
          {assessment.required_integrations.map((int, j) => (
            <span className={styles.intChip} key={j}>
              {esc(int)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function AIInsightsPanel({ hourlyRate = 400, currency, selectedOrg }) {
  const [state, setState] = useState('idle'); // idle | loading | success | error
  const [data, setData] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  async function generate() {
    setState('loading');
    setErrorMsg('');
    try {
      const d = await fetchAIAnalysis(hourlyRate, currency?.code, currency?.symbol, selectedOrg);
      if (d.status === 'error') {
        setState('error');
        setErrorMsg(d.message || 'Strategic synthesis failed. Ensure API credentials are configured.');
        return;
      }
      if (d.status === 'no_patterns') {
        setState('error');
        setErrorMsg(d.message || 'No workflow patterns detected yet.');
        return;
      }
      setData(d);
      setState('success');
    } catch (err) {
      setState('error');
      setErrorMsg('Network error: ' + err.message);
    }
  }

  // Idle state
  if (state === 'idle') {
    return (
      <div className={styles.cta}>
        <div className={styles.ctaIcon}>
          <InsightsIcon size={36} />
        </div>
        <h3>Synthesize Executive Strategic Assessment</h3>
        <p>
          Translates passive telemetry findings into an executive-ready business case:
          ranks top automation opportunities, calculates capital payback periods, and generates
          immediate zero-cost workflow optimizations.
        </p>
        <button type="button" className={styles.generateBtn} onClick={generate}>
          <ZapIcon size={14} />
          <span>Generate Strategic Assessment</span>
        </button>
      </div>
    );
  }

  // Loading
  if (state === 'loading') {
    return (
      <div className={styles.loading}>
        <div className={styles.spinLg} />
        <p>Synthesizing telemetry stream and evaluating automation vectors...</p>
        <span className={styles.loadingSub}>Formulating executive payback model</span>
      </div>
    );
  }

  // Error
  if (state === 'error') {
    return (
      <div>
        <div className={styles.errorBox}>
          <AlertIcon size={16} />
          <span>{errorMsg}</span>
        </div>
        <div className={styles.cta} style={{ paddingTop: '1.5rem' }}>
          <button type="button" className={styles.generateBtn} onClick={generate}>
            <RefreshIcon size={14} />
            <span>Retry Strategic Assessment</span>
          </button>
        </div>
      </div>
    );
  }

  const ins = data?.insights || {};
  const top = ins.top_opportunity || {};

  return (
    <div className={styles.result}>
      {/* Executive Pitch */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>Executive Business Case Summary</div>
        <div className={styles.pitchCard}>
          <p>{ins.executive_pitch || ''}</p>
        </div>
      </section>

      {/* Top Opportunity */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>Primary High-Impact Opportunity</div>
        <OpportunityHero opportunity={top} />
      </section>

      {/* Quick Wins */}
      {ins.quick_wins?.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>
            Zero-Code Operational Optimizations (Implement Immediately)
          </div>
          <div className={styles.winsGrid}>
            {ins.quick_wins.map((w, i) => (
              <QuickWinCard key={i} win={w} />
            ))}
          </div>
        </section>
      )}

      {/* Workflow Assessments */}
      {ins.workflow_assessments?.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>All Evaluated Workflows Matrix</div>
          <div className={styles.assessGrid}>
            {ins.workflow_assessments.map((a, i) => (
              <AssessmentCard key={i} assessment={a} />
            ))}
          </div>
        </section>
      )}

      {/* Meta footer */}
      <div className={styles.metaFooter}>
        <span>Architecture Engine: {esc(data?.model || 'Enterprise Core')}</span>
        <span>
          Evaluated: {data?.generated_at ? new Date(data.generated_at).toLocaleTimeString() : ''}
        </span>
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <button type="button" className={styles.reRunBtn} onClick={generate}>
          <RefreshIcon size={13} />
          <span>Re-Evaluate Telemetry</span>
        </button>
      </div>
    </div>
  );
}
