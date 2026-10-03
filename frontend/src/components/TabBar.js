'use client';

import styles from './TabBar.module.css';
import {
  WorkflowIcon,
  InsightsIcon,
  BlueprintIcon,
  RoiIcon,
  AuditIcon,
} from './Icons';

const TABS = [
  { id: 'workflows', Icon: WorkflowIcon, label: 'Workflow Intelligence' },
  { id: 'ai', Icon: InsightsIcon, label: 'Executive Insights' },
  { id: 'blueprints', Icon: BlueprintIcon, label: 'Automation Blueprints' },
  { id: 'roi', Icon: RoiIcon, label: 'ROI Impact Tracker' },
  { id: 'audit', Icon: AuditIcon, label: 'Audit & Telemetry' },
];

export default function TabBar({ activeTab, onTabChange, counts = {} }) {
  return (
    <nav className={styles.tabs} aria-label="Main Navigation">
      {TABS.map((tab) => {
        const IconComponent = tab.Icon;
        const isActive = activeTab === tab.id;
        const count = counts[tab.id];

        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={`${styles.tab} ${isActive ? styles.active : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className={styles.iconWrap}>
              <IconComponent size={15} />
            </span>
            <span className={styles.label}>{tab.label}</span>
            {count !== undefined && count > 0 && (
              <span className={styles.badge}>{count}</span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
