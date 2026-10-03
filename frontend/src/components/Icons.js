export function IconBase({ children, size = 16, className = '', ...props }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export function WorkflowIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <path d="M10 6.5h4" />
      <path d="M6.5 10v4" />
      <path d="M17.5 10v4" />
    </IconBase>
  );
}

export function InsightsIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
      <circle cx="12" cy="12" r="3" />
    </IconBase>
  );
}

export function BlueprintIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="M10 4v16" />
      <path d="M2 10h8" />
      <path d="M2 16h8" />
      <path d="M14 8h4" />
      <path d="M14 12h4" />
      <path d="M14 16h2" />
    </IconBase>
  );
}

export function RoiIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M3 3v18h18" />
      <path d="M18 9l-5 5-4-4-5 5" />
      <path d="M14 9h4v4" />
    </IconBase>
  );
}

export function AuditIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="m9 12 2 2 4-4" />
    </IconBase>
  );
}

export function ActivityIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </IconBase>
  );
}

export function ClockIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </IconBase>
  );
}

export function CheckIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polyline points="20 6 9 17 4 12" />
    </IconBase>
  );
}

export function CheckCircleIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <circle cx="12" cy="12" r="10" />
      <path d="m9 12 2 2 4-4" />
    </IconBase>
  );
}

export function AlertIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </IconBase>
  );
}

export function CloseIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </IconBase>
  );
}

export function SettingsIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </IconBase>
  );
}

export function RefreshIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </IconBase>
  );
}

export function DownloadIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </IconBase>
  );
}

export function FileTextIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </IconBase>
  );
}

export function PlayIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polygon points="5 3 19 12 5 21 5 3" />
    </IconBase>
  );
}

export function ZapIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </IconBase>
  );
}

export function ShieldIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </IconBase>
  );
}

export function FolderIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </IconBase>
  );
}

export function ArrowRightIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </IconBase>
  );
}

export function TrendingUpIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </IconBase>
  );
}

export function CodeIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polyline points="16 18 22 12 16 6" />
      <polyline points="8 6 2 12 8 18" />
    </IconBase>
  );
}

export function LockIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </IconBase>
  );
}

export function LayersIcon({ size = 16, className = '', ...props }) {
  return (
    <IconBase size={size} className={className} {...props}>
      <polygon points="12 2 2 7 12 12 22 7 12 2" />
      <polyline points="2 17 12 22 22 17" />
      <polyline points="2 12 12 17 22 12" />
    </IconBase>
  );
}
