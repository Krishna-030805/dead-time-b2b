'use client';

import { useState } from 'react';
import styles from './DryRunModal.module.css';
import { API_BASE } from '@/lib/api';
import { useToast } from './Toast';
import { PlayIcon, CloseIcon, ShieldIcon, AlertIcon } from './Icons';

export default function DryRunModal({ blueprint, onClose }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [customPayload, setCustomPayload] = useState('');
  const [useCustom, setUseCustom] = useState(false);
  const [activeTrace, setActiveTrace] = useState(0);
  const { showToast } = useToast();

  const runDryRun = async () => {
    setLoading(true);
    setResult(null);
    try {
      let body = {};
      if (useCustom && customPayload.trim()) {
        body = { sample_payload: JSON.parse(customPayload) };
      }
      const res = await fetch(`${API_BASE}/blueprints/${blueprint.id}/dry-run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error('Simulation execution failed');
      const data = await res.json();
      setResult(data);
      setActiveTrace(0);
      showToast('Sandboxed execution simulation completed successfully.', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div>
            <span className={styles.modalBadge}>Sandboxed Simulation Environment</span>
            <h3>Dry-Run Execution Engine</h3>
            <p className={styles.modalSub}>{blueprint.name}</p>
          </div>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close simulation modal"
          >
            <CloseIcon size={16} />
          </button>
        </div>

        <div className={styles.dryRunConfig}>
          <label className={styles.toggle}>
            <input
              type="checkbox"
              checked={useCustom}
              onChange={(e) => setUseCustom(e.target.checked)}
            />
            <span>Provide custom validation payload</span>
          </label>

          {useCustom && (
            <textarea
              className={styles.payloadInput}
              placeholder={
                '{\n  "record_id": "TICKET-001",\n  "subject": "System Latency Alert",\n  "priority": "high"\n}'
              }
              value={customPayload}
              onChange={(e) => setCustomPayload(e.target.value)}
              rows={5}
            />
          )}

          <button
            type="button"
            className={styles.runBtn}
            onClick={runDryRun}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className={styles.spinnerSm} />
                <span>Executing Pipeline Simulation...</span>
              </>
            ) : (
              <>
                <PlayIcon size={14} />
                <span>Execute Simulation (Deterministic Safe Mode)</span>
              </>
            )}
          </button>

          <div className={styles.safetyNote}>
            <ShieldIcon size={14} className={styles.safetyIcon} />
            <span>
              <strong>Zero-Impact Guarantee:</strong> Execution is evaluated deterministically in memory.
              No external API mutations or third-party write calls are made.
            </span>
          </div>
        </div>

        {result && (
          <div className={styles.traceContainer}>
            <div className={styles.traceHeader}>
              <span>Pipeline Stages ({result.pipeline_trace?.length || 0} evaluated)</span>
              <span className={styles.warningTag}>SIMULATED EXECUTION</span>
            </div>

            <div className={styles.traceTabs}>
              {result.pipeline_trace?.map((stage, i) => (
                <button
                  key={i}
                  type="button"
                  className={`${styles.traceTab} ${activeTrace === i ? styles.traceTabActive : ''}`}
                  onClick={() => setActiveTrace(i)}
                >
                  {stage.stage}
                </button>
              ))}
            </div>

            {result.pipeline_trace?.[activeTrace] && (
              <div className={styles.traceStage}>
                {result.pipeline_trace[activeTrace].note && (
                  <p className={styles.traceNote}>{result.pipeline_trace[activeTrace].note}</p>
                )}
                {result.pipeline_trace[activeTrace].description && (
                  <p className={styles.traceDesc}>
                    <strong>{result.pipeline_trace[activeTrace].action_type?.toUpperCase()}</strong>:
                    {' '}{result.pipeline_trace[activeTrace].description}
                  </p>
                )}
                <pre className={styles.traceJson}>
                  {JSON.stringify(result.pipeline_trace[activeTrace].data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
