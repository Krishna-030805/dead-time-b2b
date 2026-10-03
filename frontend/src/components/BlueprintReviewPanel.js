'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import styles from './BlueprintReviewPanel.module.css';
import { API_BASE } from '@/lib/api';
import DryRunModal from './DryRunModal';
import ExportActions from './ExportActions';
import { useToast } from './Toast';
import {
  BlueprintIcon,
  RefreshIcon,
  CheckIcon,
  CloseIcon,
  PlayIcon,
  ZapIcon,
  ArrowRightIcon,
  ClockIcon,
  CheckCircleIcon,
  AlertIcon,
} from './Icons';

export function BlueprintCard({
  blueprint,
  onReview,
  onDeploy,
  onSimulate,
  actionLoading,
}) {
  const data = blueprint.blueprint_json || {};
  const status = blueprint.status || 'pending_review';

  return (
    <div className={`${styles.card} ${styles[status] || ''}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>
          <h3>{blueprint.name}</h3>
          <span className={`${styles.badge} ${styles['badge-' + status] || ''}`}>
            {status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
        <div className={styles.cardMeta}>
          ID: {blueprint.id} · Pattern: {blueprint.pattern_id}
        </div>
      </div>

      {/* Flow Diagram */}
      <div className={styles.flowDiagram}>
        <div className={styles.flowNode}>
          <span className={styles.nodeLabel}>TRIGGER SOURCE</span>
          <span className={styles.nodeApp}>{data.trigger_app || 'Unknown'}</span>
          <span className={styles.nodeEvent}>{data.trigger_event || 'On Activity'}</span>
        </div>

        <div className={styles.flowArr}>
          <ArrowRightIcon size={16} />
        </div>

        <div className={styles.flowNode}>
          <span className={styles.nodeLabel}>TRANSFORMATION</span>
          <span className={styles.nodeApp}>
            {(data.transformations || []).length} Stage Pipeline
          </span>
          <span className={styles.nodeEvent}>
            {data.inputs?.slice(0, 2).join(', ') || 'In-memory normalization'}
          </span>
        </div>

        <div className={styles.flowArr}>
          <ArrowRightIcon size={16} />
        </div>

        <div className={styles.flowNode}>
          <span className={styles.nodeLabel}>DESTINATION SINK</span>
          <span className={styles.nodeApp}>{data.destination_app || 'Unknown'}</span>
          <span className={styles.nodeEvent}>{data.destination_action || 'Execute Action'}</span>
        </div>

        {data.estimated_setup_time_mins && (
          <div className={styles.setupTime}>
            <ClockIcon size={11} />
            <span>~{data.estimated_setup_time_mins}m configuration</span>
          </div>
        )}
      </div>

      {/* Transformation pipeline steps */}
      {data.transformations?.length > 0 && (
        <div className={styles.transformList}>
          {data.transformations.map((t) => (
            <div key={t.step} className={styles.transformStep}>
              <span className={styles.stepNum}>Stage {t.step}</span>
              <span className={styles.stepAction}>{t.action_type}</span>
              <span className={styles.stepDesc}>{t.description}</span>
            </div>
          ))}
        </div>
      )}

      {/* Action Bar */}
      <div className={styles.actions}>
        {/* Human approval buttons */}
        {status === 'pending_review' && (
          <div className={styles.approvalGroup}>
            <button
              type="button"
              className={`${styles.btn} ${styles.btnApprove}`}
              onClick={() => onReview(blueprint.id, 'approve')}
              disabled={actionLoading === blueprint.id}
            >
              <CheckIcon size={14} />
              <span>{actionLoading === blueprint.id ? 'Processing...' : 'Authorize Blueprint'}</span>
            </button>
            <button
              type="button"
              className={`${styles.btn} ${styles.btnReject}`}
              onClick={() => onReview(blueprint.id, 'reject')}
              disabled={actionLoading === blueprint.id}
            >
              <CloseIcon size={14} />
              <span>{actionLoading === blueprint.id ? 'Processing...' : 'Deny'}</span>
            </button>
          </div>
        )}

        {/* Sandboxed Simulation button */}
        <button
          type="button"
          className={styles.dryRunBtn}
          onClick={() => onSimulate(blueprint)}
        >
          <PlayIcon size={13} />
          <span>Simulation Sandbox</span>
        </button>

        {/* Deploy button for approved */}
        {status === 'approved' && (
          <button
            type="button"
            className={`${styles.btn} ${styles.btnDeploy}`}
            onClick={() => onDeploy(blueprint.id)}
            disabled={actionLoading === blueprint.id}
          >
            <ZapIcon size={14} />
            <span>{actionLoading === blueprint.id ? 'Deploying...' : 'Deploy to Production'}</span>
          </button>
        )}

        {/* Export buttons for approved/deployed */}
        {(status === 'approved' || status === 'deployed') && (
          <ExportActions blueprint={blueprint} />
        )}

        {/* Status indicator badges */}
        {status === 'deployed' && (
          <div className={styles.deployedMsg}>
            <CheckCircleIcon size={14} className={styles.deployedIcon} />
            <span>Active in Production</span>
          </div>
        )}
        {status === 'rejected' && (
          <div className={styles.rejectedMsg}>
            <AlertIcon size={14} />
            <span>Blocked by Administrator</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function BlueprintReviewPanel({ onCount }) {
  const [blueprints, setBlueprints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(null);
  const [dryRunBp, setDryRunBp] = useState(null);
  const { showToast } = useToast();

  const onCountRef = useRef(onCount);
  useEffect(() => {
    onCountRef.current = onCount;
  }, [onCount]);

  const fetchBlueprints = useCallback(async (isInitial = false) => {
    try {
      if (isInitial) setLoading(true);
      setError('');
      const res = await fetch(`${API_BASE}/blueprints`);
      if (!res.ok) throw new Error('Failed to fetch blueprints');
      const data = await res.json();
      setBlueprints(data);
      onCountRef.current?.(data.length);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBlueprints(true);
  }, [fetchBlueprints]);

  const handleReview = async (id, action) => {
    try {
      setActionLoading(id);
      const res = await fetch(`${API_BASE}/blueprints/${id}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      if (!res.ok) throw new Error(`Review action '${action}' failed`);
      showToast(
        `Blueprint ${action === 'approve' ? 'authorized' : 'rejected'} successfully.`,
        'success'
      );
      await fetchBlueprints();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeploy = async (id) => {
    try {
      setActionLoading(id);
      const res = await fetch(`${API_BASE}/engine/deploy/${id}`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data.status === 'failed') {
        throw new Error(data.error || 'Deployment failed');
      }
      showToast('Blueprint deployed to production engine successfully.', 'success');
      await fetchBlueprints();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <p>Loading automation blueprints...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {dryRunBp && (
        <DryRunModal blueprint={dryRunBp} onClose={() => setDryRunBp(null)} />
      )}

      <div className={styles.container}>
        <div className={styles.header}>
          <div>
            <h2>Automation Blueprints (Human-in-the-Loop Gateway)</h2>
            <p>
              Audited workflow automation specifications. Authorize execution, run safe sandboxed simulations,
              or export production-ready code directly to n8n, Make.com, or Python.
            </p>
          </div>
          <button
            type="button"
            className={styles.refreshBtn}
            onClick={() => fetchBlueprints(false)}
          >
            <RefreshIcon size={13} />
            <span>Refresh</span>
          </button>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.grid}>
          {blueprints.length === 0 ? (
            <div className={styles.empty}>
              <div className={styles.emptyIcon}>
                <BlueprintIcon size={32} />
              </div>
              <p>No automation blueprints generated yet.</p>
              <p className={styles.emptySub}>
                Synthesize a blueprint from the Workflow Intelligence panel to begin delivery.
              </p>
            </div>
          ) : (
            blueprints.map((bp) => (
              <BlueprintCard
                key={bp.id}
                blueprint={bp}
                onReview={handleReview}
                onDeploy={handleDeploy}
                onSimulate={setDryRunBp}
                actionLoading={actionLoading}
              />
            ))
          )}
        </div>
      </div>
    </>
  );
}
