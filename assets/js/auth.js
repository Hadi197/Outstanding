// Simple client-side auth + inactivity enforcement (30 minutes)
(function () {
  const TOKEN_KEY = 'auth_token';
  const USER_KEY = 'auth_user';
  const EXP_KEY = 'auth_exp';
  const LAST_ACTIVITY_KEY = 'auth_last_activity';
  const INACTIVITY_MS = 30 * 60 * 1000; // 30 minutes

  function clearSession() {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(EXP_KEY);
      localStorage.removeItem(LAST_ACTIVITY_KEY);
    } catch (e) {}
  }

  function updateActivity() {
    try { localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now())); } catch (e) {}
  }

  function getLastActivity() {
    const t = parseInt(localStorage.getItem(LAST_ACTIVITY_KEY) || '0', 10);
    return isNaN(t) ? 0 : t;
  }

  function isSessionValid() {
    const token = localStorage.getItem(TOKEN_KEY);
    const exp = parseInt(localStorage.getItem(EXP_KEY) || '0', 10);
    if (!token || !exp) return false;
    return Date.now() < exp;
  }

  function isInactiveTooLong() {
    const last = getLastActivity();
    if (!last) return true;
    return (Date.now() - last) > INACTIVITY_MS;
  }

  function loginUrlWithRedirect() {
    const here = window.location.pathname + window.location.search + window.location.hash;
    const url = new URL('login.html', window.location.origin);
    url.searchParams.set('redirect', here);
    return url.toString();
  }

  function logoutAndRedirect() {
    clearSession();
    window.location.replace(loginUrlWithRedirect());
  }

  function attachActivityListeners() {
    const events = ['click','mousemove','keydown','scroll','touchstart','touchmove'];
    events.forEach(ev => window.addEventListener(ev, updateActivity, { passive: true }));
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) updateActivity();
    });
  }

  function startWatcher() {
    updateActivity();
    attachActivityListeners();
    setInterval(() => {
      if (!isSessionValid() || isInactiveTooLong()) {
        logoutAndRedirect();
      }
    }, 60 * 1000); // check every minute
  }

  // Public API
  window.enforceAuth = function enforceAuth() {
    if (!isSessionValid() || isInactiveTooLong()) {
      logoutAndRedirect();
      return;
    }
    startWatcher();
  };
})();
