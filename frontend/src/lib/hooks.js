'use client';

import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for polling data from the API.
 * @param {Function} fetcher - async function that returns data
 * @param {number} intervalMs - polling interval in ms (0 = no polling)
 * @param {boolean} immediate - fetch immediately on mount
 */
export function usePolling(fetcher, intervalMs = 0, immediate = true) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const result = await fetcher();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    if (immediate) refresh();
    if (intervalMs > 0) {
      const id = setInterval(refresh, intervalMs);
      return () => clearInterval(id);
    }
  }, [refresh, intervalMs, immediate]);

  return { data, loading, error, refresh };
}
