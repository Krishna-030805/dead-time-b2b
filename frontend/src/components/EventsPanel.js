'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import styles from './EventsPanel.module.css';
import { fetchEvents } from '@/lib/api';
import { ActivityIcon, RefreshIcon } from './Icons';

function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export default function EventsPanel({ onCount, selectedOrg }) {
  const [events, setEvents] = useState([]);
  const [lastRefresh, setLastRefresh] = useState('');
  const [selectedUser, setSelectedUser] = useState('');

  const onCountRef = useRef(onCount);
  useEffect(() => {
    onCountRef.current = onCount;
  }, [onCount]);

  const load = useCallback(async () => {
    try {
      const data = await fetchEvents(80, selectedOrg);
      setEvents(data);
      onCountRef.current?.(data.length);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch {}
  }, [selectedOrg]);

  useEffect(() => {
    load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, [load]);

  const uniqueUsers = Array.from(new Set(events.map(e => e.user_id).filter(Boolean)));
  const displayEvents = selectedUser ? events.filter(e => e.user_id === selectedUser) : events;

  if (!events.length) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyIcon}>
          <ActivityIcon size={32} />
        </div>
        <p>Awaiting telemetry signals from ingestion collector.</p>
        <span className={styles.emptySub}>
          Window focus changes and application switch events will stream here live.
        </span>
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.tableHeader}>
        <div>
          <h2>Real-Time Telemetry Stream</h2>
          <span className={styles.tableSub}>Verified cross-application activity signals</span>
        </div>
        <div className={styles.headerRight}>
          {uniqueUsers.length > 1 && (
            <select
              className={styles.userFilter}
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
              title="Filter by Computer / Employee"
            >
              <option value="">All Devices ({events.length})</option>
              {uniqueUsers.map(u => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          )}
          <span className={styles.liveIndicator}>
            <span className={styles.liveDot} />
            Auto-refresh 3s
          </span>
          <span className={styles.note}>Last sync: {lastRefresh || 'Just now'}</span>
        </div>
      </div>
      <div className={styles.tableScroll}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Device / User</th>
              <th>Application</th>
              <th>Signal Type</th>
              <th>Target Object</th>
              <th>Session ID</th>
              <th>Payload Metadata</th>
            </tr>
          </thead>
          <tbody>
            {displayEvents.map((e, i) => {
              const t = e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : '—';
              const sid = e.session_id ? e.session_id.substring(0, 12) + '…' : '—';
              const meta = e.metadata_json ? JSON.stringify(e.metadata_json) : '—';
              const actionClass = e.action_type === 'open' ? styles.chipOpen : styles.chipAction;

              return (
                <tr key={e.id || i}>
                  <td className={styles.mono}>{t}</td>
                  <td>
                    <span className={styles.chipUser}>
                      {esc(e.user_id || 'default')}
                    </span>
                  </td>
                  <td>
                    <span className={`${styles.chip} ${styles.chipApp}`}>
                      {esc(e.application || 'web')}
                    </span>
                  </td>
                  <td>
                    <span className={`${styles.chip} ${actionClass}`}>
                      {esc(e.action_type)}
                    </span>
                  </td>
                  <td className={styles.mono} style={{ fontSize: '0.72rem' }}>
                    {esc(e.object_type || '')}
                    {e.object_id && (
                      <span style={{ color: 'var(--t3)' }}>
                        {' '}· {esc(e.object_id.substring(0, 24))}
                      </span>
                    )}
                  </td>
                  <td className={styles.mono}>{sid}</td>
                  <td className={styles.metaCell} title={meta}>
                    {meta}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
