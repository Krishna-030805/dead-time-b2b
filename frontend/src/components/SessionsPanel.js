'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import styles from './SessionsPanel.module.css';
import { fetchSessions } from '@/lib/api';
import { FolderIcon, ActivityIcon, LayersIcon, ArrowRightIcon, ClockIcon } from './Icons';

function esc(s) {
  return String(s || '');
}

export function SessionCard({ session }) {
  const chain = session.app_sequence || [];
  const t1 = new Date(session.start_time).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
  const t2 = new Date(session.end_time).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={styles.card}>
      <div className={styles.cardTop}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
          <span className={styles.sessionKey}>{esc(session.session_key)}</span>
          {session.user_id && (
            <span className={styles.userBadge}>{esc(session.user_id)}</span>
          )}
        </div>
        <span className={styles.duration}>{esc(session.duration_label)}</span>
      </div>

      <div className={styles.time}>
        <ClockIcon size={12} className={styles.timeIcon} />
        <span>{t1} → {t2}</span>
      </div>

      <div className={styles.chain}>
        {chain.map((app, j) => (
          <span key={j} className={styles.chainItem}>
            <span className={styles.appNode}>{app.replace(/_/g, ' ')}</span>
            {j < chain.length - 1 && (
              <span className={styles.arrow}>
                <ArrowRightIcon size={11} />
              </span>
            )}
          </span>
        ))}
      </div>

      <div className={styles.meta}>
        <span className={styles.metaItem}>
          <ActivityIcon size={11} />
          <span>{session.event_count} signals</span>
        </span>
        <span className={styles.metaItem}>
          <LayersIcon size={11} />
          <span>{(session.apps_used || []).length} applications</span>
        </span>
      </div>
    </div>
  );
}

export default function SessionsPanel({ onCount }) {
  const [sessions, setSessions] = useState([]);

  const onCountRef = useRef(onCount);
  useEffect(() => {
    onCountRef.current = onCount;
  }, [onCount]);

  const load = useCallback(async () => {
    try {
      const data = await fetchSessions();
      setSessions(data);
      onCountRef.current?.(data.length);
    } catch {}
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 12000);
    return () => clearInterval(id);
  }, [load]);

  if (!sessions.length) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyIcon}>
          <FolderIcon size={32} />
        </div>
        <p>No clustered work sessions detected yet.</p>
        <span className={styles.emptySub}>
          Sessions are automatically constructed when sequential telemetry signals occur within the clustering threshold.
        </span>
      </div>
    );
  }

  return (
    <div>
      <div className={styles.sectionHeader}>
        <div>
          <h2>Clustered Work Sessions</h2>
          <span className={styles.note}>Threshold: 30-minute inactivity boundary creates a new session</span>
        </div>
        <span className={styles.countBadge}>{sessions.length} sessions</span>
      </div>
      <div className={styles.grid}>
        {sessions.map((s, i) => (
          <SessionCard key={s.session_key || i} session={s} />
        ))}
      </div>
    </div>
  );
}
