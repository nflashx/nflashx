/* ============================================================
   NFlashX auth modal — real server-backed auth.
   Endpoints (server.py): /api/auth/signup|verify|resend|login|me|logout
   Included on every page; intercepts .btn-login / .btn-doclogin.
   ============================================================ */
(function () {
  const LS_SESSION = 'nfx_session';
  let sess = null;
  try { sess = JSON.parse(localStorage.getItem(LS_SESSION) || 'null'); } catch (_) {}

  const saveSession = s => { sess = s; localStorage.setItem(LS_SESSION, JSON.stringify(s)); };
  const clearSession = () => { sess = null; localStorage.removeItem(LS_SESSION); };
  const api = (path, body) => fetch('/api/auth/' + path, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  }).then(async r => {
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || 'Request failed');
    return j;
  });

  function refreshButtons() {
    document.querySelectorAll('.btn-login, .btn-doclogin').forEach(el => {
      el.textContent = sess ? sess.name : 'Login';
      el.href = '#';
      el.title = sess ? 'Account & API key' : 'Sign in';
    });
  }

  /* ---------- modal markup ---------- */
  const OAUTH_G = '<svg viewBox="0 0 24 24" width="16" height="16"><path fill="#4285F4" d="M23.5 12.3c0-.9-.1-1.5-.3-2.2H12v4.1h6.5c-.1 1.1-.8 2.7-2.4 3.8l3.7 2.9c2.3-2.1 3.7-5.1 3.7-8.6z"/><path fill="#34A853" d="M12 24c3.2 0 5.9-1.1 7.9-2.9l-3.7-2.9c-1 .7-2.4 1.2-4.2 1.2-3.2 0-5.9-2.1-6.9-5.1L1.3 17.2C3.3 21.2 7.3 24 12 24z"/><path fill="#FBBC05" d="M5.1 14.3c-.2-.7-.4-1.5-.4-2.3s.1-1.6.4-2.3L1.3 6.8C.5 8.4 0 10.1 0 12s.5 3.6 1.3 5.2l3.8-2.9z"/><path fill="#EA4335" d="M12 4.7c1.8 0 3 .8 3.7 1.4l3.3-3.2C17.9 1.1 15.2 0 12 0 7.3 0 3.3 2.8 1.3 6.8l3.8 2.9c1-3 3.7-5 6.9-5z"/></svg>';
  const OAUTH_GH = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 .3a12 12 0 00-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2 0 1.9 1.2 1.9 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 016 0C17.3 4.6 18.3 5 18.3 5c.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0012 .3z"/></svg>';

  function build() {
    if (document.getElementById('amBackdrop')) return;
    const wrap = document.createElement('div');
    wrap.id = 'amBackdrop';
    wrap.className = 'am-backdrop';
    wrap.innerHTML = `
      <div class="am-card" role="dialog" aria-modal="true">
        <button class="am-close" aria-label="Close">✕</button>
        <div class="am-brand"><img src="assets/logo.svg" alt=""> NFlashX <span>API Platform</span></div>

        <div class="am-view" data-v="guest">
          <div class="am-tabs">
            <button class="am-tab on" data-t="in">Sign In</button>
            <button class="am-tab" data-t="up">Sign Up</button>
          </div>
          <div class="am-err"></div>

          <form id="amForm" novalidate>
            <div class="am-field am-onlyup" style="display:none"><label>Full name</label><input type="text" id="amName" placeholder="Your name" autocomplete="name"></div>
            <div class="am-field"><label>Email</label><input type="email" id="amEmail" placeholder="Email" autocomplete="email"></div>
            <div class="am-field"><label>Password</label><input type="password" id="amPass" placeholder="At least 6 characters" autocomplete="current-password"></div>
            <div class="am-field am-onlyup" style="display:none"><label>Confirm password</label><input type="password" id="amPass2" placeholder="Re-enter your password"></div>
            <button class="am-submit" type="submit">Sign In</button>
          </form>

          <div class="am-verify" style="display:none">
            <p class="am-vtext">Enter the 6-digit code we sent to<br><b class="am-vmail">—</b></p>
            <input class="am-code" id="amCode" inputmode="numeric" maxlength="6" placeholder="••••••" autocomplete="one-time-code">
            <div class="am-err am-verr"></div>
            <button class="am-submit" id="amVerifyBtn">Verify email</button>
            <button class="am-ghost am-resend" id="amResend" disabled>Resend code (45s)</button>
          </div>

          <div class="am-or">OR</div>
          <button class="am-oauth" data-p="google">${OAUTH_G} Continue with Google</button>
          <button class="am-oauth" data-p="github">${OAUTH_GH} Continue with Github</button>
        </div>

        <div class="am-view" data-v="user" style="display:none">
          <div class="am-user">
            <div class="am-avatar">N</div>
            <div><b class="am-uname">—</b><span class="am-umail">—</span></div>
          </div>
          <div class="am-key">
            <span class="am-key-label">API key</span>
            <div class="am-key-row">
              <span class="am-key-val" id="amKeyValue">sk-nfx-••••••••••••</span>
              <button class="am-key-btn" data-act="showkey" type="button">Show</button>
              <button class="am-key-btn" data-act="copykey" type="button">Copy</button>
            </div>
          </div>
          <button class="am-submit" data-act="account">Open account page</button>
          <button class="am-submit ghost" data-act="logout">Log out</button>
        </div>
      </div>`;
    document.body.appendChild(wrap);
    wire(wrap);
  }

  let pendingEmail = null, resendTimer = null, keyShown = false;

  function maskKey(k) { return k.slice(0, 10) + '••••••••••••••' + k.slice(-4); }

  function wire(wrap) {
    wrap.addEventListener('click', e => { if (e.target === wrap) close(); });
    wrap.querySelector('.am-close').onclick = close;
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

    wrap.querySelectorAll('.am-tab').forEach(t => t.onclick = () => {
      wrap.querySelectorAll('.am-tab').forEach(x => x.classList.remove('on'));
      t.classList.add('on');
      const up = t.dataset.t === 'up';
      wrap.querySelectorAll('.am-onlyup').forEach(f => f.style.display = up ? 'block' : 'none');
      wrap.querySelector('.am-submit').textContent = up ? 'Create account' : 'Sign In';
      hideErr();
    });

    wrap.querySelector('#amForm').onsubmit = async e => {
      e.preventDefault();
      const btn = wrap.querySelector('.am-submit');
      const up = wrap.querySelector('.am-tab.on').dataset.t === 'up';
      const email = wrap.querySelector('#amEmail').value.trim().toLowerCase();
      const pass = wrap.querySelector('#amPass').value;
      try {
        if (up) {
          const name = wrap.querySelector('#amName').value.trim();
          const pass2 = wrap.querySelector('#amPass2').value;
          const r = await api('signup', { name, email, password: pass, confirm: pass2 });
          pendingEmail = email;
          showVerify(email, r.dev_code);
        } else {
          const r = await api('login', { email, password: pass });
          saveSession({ token: r.token, email: r.user.email, name: r.user.name, apiKey: r.user.api_key, hasKey: !!r.user.api_key });
          refreshButtons(); showUser(); close(); toast('Signed in as ' + r.user.name);
        }
      } catch (err) { showErr(err.message); }
    };

    wrap.querySelector('#amVerifyBtn').onclick = async () => {
      const code = wrap.querySelector('#amCode').value.trim();
      try {
        const r = await api('verify', { email: pendingEmail, code });
        saveSession({ token: r.token, email: r.user.email, name: r.user.name, apiKey: r.user.api_key, hasKey: !!r.user.api_key });
        refreshButtons(); showUser(); close(); toast('Email verified — welcome, ' + r.user.name);
      } catch (err) { showVerifyErr(err.message); }
    };

    wrap.querySelector('#amResend').onclick = async () => {
      try {
        const r = await api('resend', { email: pendingEmail });
        showVerifyErr(r.dev_code ? 'DEV MODE — code: ' + r.dev_code : 'New code sent. Check your inbox.');
        cooldown();
      } catch (err) { showVerifyErr(err.message); }
    };

    wrap.querySelectorAll('.am-oauth').forEach(b => b.onclick = async () => {
      const p = b.dataset.p;
      try {
        const r = await fetch(`/api/auth/oauth/${p}/start`).then(x => x.json());
        if (r.url) location.href = r.url;
        else showErr(r.error || 'OAuth is not available.');
      } catch (err) { showErr('OAuth is not available right now.'); }
    });

    wrap.querySelector('[data-act="showkey"]').onclick = () => { keyShown = !keyShown; renderUser(); };
    wrap.querySelector('[data-act="copykey"]').onclick = async () => {
      if (!sess || !sess.apiKey) return;
      try { await navigator.clipboard.writeText(sess.apiKey); }
      catch (_) {
        const ta = document.createElement('textarea');
        ta.value = sess.apiKey; document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); ta.remove();
      }
      toast('API key copied to clipboard');
    };
    wrap.querySelector('[data-act="account"]').onclick = () => { close(); location.href = 'platform.html'; };
    wrap.querySelector('[data-act="logout"]').onclick = async () => {
      try { await api('logout', { token: sess && sess.token }); } catch (_) {}
      clearSession(); refreshButtons(); renderUser(); close(); toast('Logged out');
    };
  }

  function showVerify(email, devCode) {
    const wrap = document.getElementById('amBackdrop');
    wrap.querySelector('#amForm').style.display = 'none';
    wrap.querySelector('.am-or').style.display = 'none';
    wrap.querySelectorAll('.am-oauth').forEach(o => o.style.display = 'none');
    hideErr();
    const v = wrap.querySelector('.am-verify');
    v.style.display = 'block';
    v.querySelector('.am-vmail').textContent = email;
    const codeInput = v.querySelector('.am-code');
    codeInput.value = '';
    if (devCode) showVerifyErr('DEV MODE (mail not configured) — your code: ' + devCode);
    else showVerifyErr('');
    cooldown();
    setTimeout(() => codeInput.focus(), 100);
  }
  function cooldown() {
    const b = document.getElementById('amResend');
    let s = 45; b.disabled = true;
    clearInterval(resendTimer);
    resendTimer = setInterval(() => {
      s--; b.textContent = `Resend code (${s}s)`;
      if (s <= 0) { clearInterval(resendTimer); b.disabled = false; b.textContent = 'Resend code'; }
    }, 1000);
  }

  function showErr(m) {
    const e = document.querySelector('#amBackdrop .am-err');
    e.textContent = m; e.style.display = m ? 'block' : 'none';
  }
  function showVerifyErr(m) {
    const e = document.querySelector('#amBackdrop .am-verr');
    e.textContent = m; e.style.display = m ? 'block' : 'none';
  }
  function hideErr() { showErr(''); }

  function renderUser() {
    const v = document.querySelector('.am-view[data-v="user"]');
    if (!v || !sess) return;
    v.querySelector('.am-uname').textContent = sess.name;
    v.querySelector('.am-umail').textContent = sess.email;
    v.querySelector('.am-avatar').textContent = (sess.name[0] || 'N').toUpperCase();
    const kv = v.querySelector('#amKeyValue');
    const showBtn = v.querySelector('[data-act="showkey"]');
    if (sess.apiKey) {
      kv.textContent = keyShown ? sess.apiKey : maskKey(sess.apiKey);
      showBtn.textContent = keyShown ? 'Hide' : 'Show';
      showBtn.style.display = '';
    } else if (sess.hasKey === false) {
      kv.textContent = 'No key yet — create one on the API Platform';
      showBtn.style.display = 'none';
    } else {
      kv.textContent = 'Loading key…';
      showBtn.style.display = 'none';
    }
  }

  function showUser() {
    const wrap = document.getElementById('amBackdrop');
    wrap.querySelector('#amForm').style.display = 'none';
    wrap.querySelector('.am-verify').style.display = 'none';
    wrap.querySelector('.am-or').style.display = 'none';
    wrap.querySelectorAll('.am-oauth').forEach(o => o.style.display = 'none');
    wrap.querySelector('.am-view[data-v="user"]').style.display = 'block';
    renderUser();
  }

  function open() {
    build();
    const wrap = document.getElementById('amBackdrop');
    wrap.querySelector('.am-view[data-v="guest"]').style.display = sess ? 'none' : 'block';
    wrap.querySelector('.am-view[data-v="user"]').style.display = sess ? 'block' : 'none';
    if (sess) {
      keyShown = false;
      renderUser();
      // luôn refresh key mới nhất từ server (kể cả khi vừa tạo key mới ở account page)
      api('me', { token: sess.token }).then(r => {
        saveSession({ token: sess.token, email: r.user.email, name: r.user.name, apiKey: r.user.api_key, hasKey: !!r.user.api_key });
        renderUser();
      }).catch(() => {});
    }
    wrap.classList.add('on');
  }
  function close() { const b = document.getElementById('amBackdrop'); if (b) b.classList.remove('on'); }

  function toast(msg) {
    const t = document.createElement('div');
    t.className = 'am-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add('on'), 20);
    setTimeout(() => { t.classList.remove('on'); setTimeout(() => t.remove(), 400); }, 2600);
  }

  /* intercept login buttons */
  document.addEventListener('click', e => {
    const b = e.target.closest('.btn-login, .btn-doclogin');
    if (!b) return;
    e.preventDefault();
    open();
  });

  refreshButtons();
  window.NFXAuth = { open, close };
})();
