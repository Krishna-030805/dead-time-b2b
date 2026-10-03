'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import styles from './Toast.module.css';
import { CheckCircleIcon, AlertIcon, InsightsIcon, CloseIcon } from './Icons';

const ToastContext = createContext({
  showToast: () => {},
});

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message, type = 'info', durationMs = 4000) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    if (durationMs > 0) {
      setTimeout(() => {
        removeToast(id);
      }, durationMs);
    }
  }, [removeToast]);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className={styles.toastContainer} aria-live="polite">
        {toasts.map((toast) => {
          let typeClass = styles.toastInfo;
          let IconComp = InsightsIcon;
          if (toast.type === 'success') {
            typeClass = styles.toastSuccess;
            IconComp = CheckCircleIcon;
          } else if (toast.type === 'error') {
            typeClass = styles.toastError;
            IconComp = AlertIcon;
          }

          return (
            <div key={toast.id} className={`${styles.toast} ${typeClass}`}>
              <div className={styles.iconWrap}>
                <IconComp size={18} />
              </div>
              <div className={styles.message}>{toast.message}</div>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={() => removeToast(toast.id)}
                aria-label="Dismiss notification"
              >
                <CloseIcon size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
