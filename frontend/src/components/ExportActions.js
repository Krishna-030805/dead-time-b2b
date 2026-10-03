'use client';

import { useState } from 'react';
import styles from './ExportActions.module.css';
import { API_BASE } from '@/lib/api';
import { useToast } from './Toast';
import { DownloadIcon, ZapIcon, LayersIcon, CodeIcon } from './Icons';

const EXPORT_FORMATS = [
  { type: 'n8n', label: 'n8n Workflow', Icon: ZapIcon },
  { type: 'make', label: 'Make.com', Icon: LayersIcon },
  { type: 'python', label: 'Python Script', Icon: CodeIcon },
];

export default function ExportActions({ blueprint }) {
  const [exporting, setExporting] = useState(null);
  const { showToast } = useToast();

  const handleExport = async (type) => {
    setExporting(type);
    try {
      const url = `${API_BASE}/blueprints/${blueprint.id}/export/${type}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Export to ${type} failed.`);

      const blob = await res.blob();
      const ext = type === 'python' ? 'py' : 'json';
      const filename = `dead_time_${blueprint.id}_${type}.${ext}`;

      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      showToast(`Exported ${blueprint.name} as ${type.toUpperCase()}`, 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className={styles.exportGroup}>
      <span className={styles.exportLabel}>Export:</span>
      {EXPORT_FORMATS.map(({ type, label, Icon: IconComponent }) => (
        <button
          key={type}
          type="button"
          className={styles.exportBtn}
          onClick={() => handleExport(type)}
          disabled={exporting === type}
          title={`Download ${label}`}
        >
          {exporting === type ? (
            <span className={styles.spinnerSm} />
          ) : (
            <IconComponent size={12} />
          )}
          <span>{label}</span>
        </button>
      ))}
    </div>
  );
}
