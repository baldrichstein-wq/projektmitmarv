let csrfToken = null;

export function setCsrfToken(token) {
  if (token) csrfToken = token;
}

async function fetchCsrfToken(url) {
  const base = url.replace(/\/api\/.*$/, '');
  const res = await fetch(`${base}/api/csrf-token`, { credentials: 'include' });
  const data = await res.json();
  csrfToken = data.csrf_token;
  return csrfToken;
}

// Drop-in Ersatz für fetch(): sendet Session-Cookies immer mit (credentials: 'include') und
// haengt bei veraendernden Requests (POST/PUT/DELETE/PATCH) automatisch das CSRF-Token als
// Header an. Das Token wird beim ersten Bedarf einmalig von /api/csrf-token geholt und danach
// aus dem Speicher wiederverwendet; nach Login/Logout liefert das Backend ein neues Token
// mit, das ueber setCsrfToken() aktualisiert wird.
export async function apiFetch(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const opts = { ...options, credentials: 'include' };

  if (method !== 'GET' && method !== 'HEAD') {
    if (!csrfToken) {
      await fetchCsrfToken(url);
    }
    opts.headers = { ...(options.headers || {}), 'X-CSRF-Token': csrfToken };
  }

  return fetch(url, opts);
}

export function checkPasswordStrength(password) {
  if (password.length < 8) return 'Mindestens 8 Zeichen.';
  if (!/[A-Z]/.test(password)) return 'Mindestens ein Großbuchstabe.';
  if (!/[a-z]/.test(password)) return 'Mindestens ein Kleinbuchstabe.';
  if (!/\d/.test(password)) return 'Mindestens eine Ziffer.';
  return null;
}
