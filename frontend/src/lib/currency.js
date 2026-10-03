// currency.js — Multi-Currency & Location-Aware Engine for Dead Time B2B

export const CURRENCIES = {
  INR: {
    code: 'INR',
    symbol: '₹',
    name: 'INR (₹)',
    defaultRate: 400,
    presets: [200, 400, 750, 1200],
    locale: 'en-IN',
  },
  USD: {
    code: 'USD',
    symbol: '$',
    name: 'USD ($)',
    defaultRate: 65,
    presets: [35, 65, 100, 150],
    locale: 'en-US',
  },
  GBP: {
    code: 'GBP',
    symbol: '£',
    name: 'GBP (£)',
    defaultRate: 50,
    presets: [25, 50, 100, 150],
    locale: 'en-GB',
  },
  EUR: {
    code: 'EUR',
    symbol: '€',
    name: 'EUR (€)',
    defaultRate: 55,
    presets: [30, 55, 90, 140],
    locale: 'de-DE',
  },
};

/**
 * Detect user currency based on stored preference, browser timezone, and locale.
 */
export function detectUserCurrency() {
  if (typeof window === 'undefined') return CURRENCIES.INR;

  try {
    // 1. Check local storage preference
    const saved = localStorage.getItem('dt_currency');
    if (saved && CURRENCIES[saved]) {
      return CURRENCIES[saved];
    }

    // 2. Inspect device timezone
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    if (
      tz.includes('Kolkata') ||
      tz.includes('Calcutta') ||
      tz.startsWith('Asia/Colombo') ||
      tz.startsWith('Asia/Kathmandu')
    ) {
      return CURRENCIES.INR;
    }
    if (tz === 'Europe/London') return CURRENCIES.GBP;
    if (tz.startsWith('Europe/')) return CURRENCIES.EUR;
    if (tz.startsWith('America/') || tz.startsWith('US/')) return CURRENCIES.USD;

    // 3. Inspect browser language
    const lang = navigator.language || '';
    if (lang.includes('IN') || lang.startsWith('hi')) return CURRENCIES.INR;
    if (lang.includes('GB')) return CURRENCIES.GBP;
    if (lang.includes('US')) return CURRENCIES.USD;

    // Default to INR
    return CURRENCIES.INR;
  } catch {
    return CURRENCIES.INR;
  }
}

/**
 * Format a number into currency string with symbol.
 */
export function formatCurrency(amount, currency = CURRENCIES.INR) {
  if (amount === undefined || amount === null) return '—';
  const num = Number(amount);
  if (isNaN(num)) return String(amount);
  return `${currency.symbol}${num.toLocaleString(currency.locale, { maximumFractionDigits: 0 })}`;
}
