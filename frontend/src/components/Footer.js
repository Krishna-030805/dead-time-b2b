'use client';

import styles from './Footer.module.css';
import { ShieldIcon, LockIcon, ActivityIcon } from './Icons';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.left}>
        <div className={styles.brand}>
          <span className={styles.badge}>ENTERPRISE</span>
          <span className={styles.brandName}>Dead Time B2B</span>
          <span className={styles.version}>v4.2.0</span>
        </div>
        <p className={styles.tagline}>
          Continuous Cross-Application Telemetry, Bottleneck Quantification &amp; Closed-Loop Automation Synthesis.
        </p>
      </div>

      <div className={styles.security}>
        <div className={styles.securityBadge}>
          <ShieldIcon size={13} className={styles.securityIcon} />
          <span>SOC-2 Type II Ingestion Standards</span>
        </div>
        <div className={styles.securityBadge}>
          <LockIcon size={13} className={styles.securityIcon} />
          <span>AES-256 Encrypted Stream</span>
        </div>
        <div className={styles.securityBadge}>
          <span className={styles.statusDot} />
          <span>Telemetry Daemon Operational</span>
        </div>
      </div>
    </footer>
  );
}
