'use client';

import { useState } from 'react';
import styles from './AuditTrailPanel.module.css';
import EventsPanel from './EventsPanel';
import SessionsPanel from './SessionsPanel';
import { ActivityIcon, FolderIcon } from './Icons';

export default function AuditTrailPanel({ onEventsCount, onSessionsCount }) {
  const [activeSubTab, setActiveSubTab] = useState('events');

  return (
    <div className={styles.wrap}>
      <div className={styles.header}>
        <div>
          <h2>Enterprise Audit Trail &amp; Telemetry Feed</h2>
          <p className={styles.subtitle}>
            Deterministic, tamper-evident record of captured application window focus events, system signals,
            and clustered work sessions utilized for dead-time quantification.
          </p>
        </div>
        <div className={styles.toggleGroup} role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeSubTab === 'events'}
            className={`${styles.toggleBtn} ${activeSubTab === 'events' ? styles.toggleActive : ''}`}
            onClick={() => setActiveSubTab('events')}
          >
            <ActivityIcon size={13} />
            <span>Ingestion Signal Feed</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeSubTab === 'sessions'}
            className={`${styles.toggleBtn} ${activeSubTab === 'sessions' ? styles.toggleActive : ''}`}
            onClick={() => setActiveSubTab('sessions')}
          >
            <FolderIcon size={13} />
            <span>Clustered Work Sessions</span>
          </button>
        </div>
      </div>

      <div className={styles.content}>
        {activeSubTab === 'events' ? (
          <EventsPanel onCount={onEventsCount} />
        ) : (
          <SessionsPanel onCount={onSessionsCount} />
        )}
      </div>
    </div>
  );
}
