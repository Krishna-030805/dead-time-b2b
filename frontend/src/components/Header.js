'use client';

import { useState } from 'react';
import styles from './Header.module.css';
import { getReportURL, getPDFDownloadURL } from '@/lib/api';
import { CURRENCIES } from '@/lib/currency';
import { SettingsIcon, FileTextIcon, DownloadIcon, CheckCircleIcon } from './Icons';

export default function Header({
  hourlyRate,
  setHourlyRate,
  currency = CURRENCIES.INR,
  onCurrencyChange,
  realizedSavings,
  selectedOrg = 'org_default',
  onOrgChange,
  organizations = ['org_default'],
}) {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const presets = currency?.presets || [200, 400, 750, 1200];

  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <div className={styles.logo}>
          <span className={styles.logoText}>DT</span>
        </div>
        <div className={styles.brandText}>
          <div className={styles.brandTitleRow}>
            <h1>Dead Time</h1>
            <span className={styles.versionPill}>Enterprise</span>
          </div>
          <p>Workflow Intelligence &amp; Automation Platform</p>
        </div>
      </div>

      <div className={styles.right}>
        {/* Client Organization Selector */}
        <div className={styles.clientSelectorWrap} title="Active Client Organization Filter">
          <span className={styles.clientIcon}>🏢</span>
          <select
            className={styles.clientSelect}
            value={selectedOrg}
            onChange={(e) => onOrgChange?.(e.target.value)}
          >
            <option value="all">All Clients (Consolidated)</option>
            {organizations.map((org) => (
              <option key={org} value={org}>
                {org === 'org_default' ? 'Default Client' : org.replace(/^org_/, '').replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Realized savings badge — shown only when automations are deployed */}
        {realizedSavings && (
          <div className={styles.savingsBadge} title="Verified annual savings from deployed automations">
            <div className={styles.savingsIconWrap}>
              <CheckCircleIcon size={14} />
            </div>
            <div className={styles.savingsContent}>
              <span className={styles.savingsLabel}>Realized Savings</span>
              <span className={styles.savingsValue}>
                {realizedSavings.endsWith('/yr') ? realizedSavings : `${realizedSavings}/yr`}
              </span>
            </div>
          </div>
        )}

        <div className={styles.livePill} title="Telemetry Ingestion Agent Active">
          <span className={styles.dot} />
          <span>LIVE TELEMETRY</span>
        </div>

        {/* Generate Report */}
        <a
          href={getReportURL(hourlyRate, currency?.code, currency?.symbol, selectedOrg)}
          target="_blank"
          rel="noopener"
          className={`${styles.btn} ${styles.btnSecondary}`}
        >
          <FileTextIcon size={14} />
          <span>Audit Report</span>
        </a>

        {/* Export PDF */}
        <a
          href={getPDFDownloadURL(hourlyRate, selectedOrg, currency?.code, currency?.symbol)}
          target="_blank"
          rel="noopener"
          className={`${styles.btn} ${styles.btnPrimary}`}
        >
          <DownloadIcon size={14} />
          <span>Export PDF</span>
        </a>

        {/* Engagement Settings — internal audit config */}
        <button
          type="button"
          className={`${styles.settingsBtn} ${settingsOpen ? styles.settingsBtnActive : ''}`}
          onClick={() => setSettingsOpen((v) => !v)}
          title="Engagement Configuration"
          aria-label="Engagement Configuration"
        >
          <SettingsIcon size={16} />
        </button>

        {settingsOpen && (
          <div className={styles.settingsDropdown}>
            <div className={styles.settingsTitle}>Engagement Parameters</div>
            <p className={styles.settingsSub}>
              Configures client organization labor costs to calibrate all ROI calculations and executive audit figures.
            </p>

            <div className={styles.formGroup}>
              <label className={styles.settingsLabel}>Client Reporting Currency</label>
              <select
                className={styles.settingsSelect}
                value={currency?.code || 'INR'}
                onChange={(e) => {
                  const next = CURRENCIES[e.target.value] || CURRENCIES.INR;
                  onCurrencyChange?.(next);
                }}
              >
                {Object.values(CURRENCIES).map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.symbol} {c.code} ({c.name})
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.settingsLabel}>Fully-Loaded Labor Rate</label>
              <select
                className={styles.settingsSelect}
                value={hourlyRate}
                onChange={(e) => setHourlyRate(Number(e.target.value))}
              >
                {presets.map((rate) => (
                  <option key={rate} value={rate}>
                    {currency.symbol}{rate} / hour
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              className={styles.settingsClose}
              onClick={() => setSettingsOpen(false)}
            >
              Apply &amp; Close
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
