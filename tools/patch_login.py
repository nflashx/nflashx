import io, re

p = 'login.html'
s = io.open(p, encoding='utf-8').read()

verify_box = '''
      <div id="verifyBox" style="display:none">
        <p style="text-align:center;font-size:13.5px;color:#4a545f;line-height:1.6;margin-bottom:14px">
          Enter the 6-digit code we sent to<br><b id="vEmail" style="color:#0c1014">—</b>
        </p>
        <div class="auth-err" id="errVerify"></div>
        <input id="vCode" inputmode="numeric" maxlength="6" placeholder="&bull;&bull;&bull;&bull;&bull;&bull;"
               style="width:100%;text-align:center;font-family:'JetBrains Mono',monospace;font-size:22px;letter-spacing:10px;
                      padding:12px;border-radius:10px;border:1px solid #dfe4ea;background:#f3f5f8;outline:0;margin-bottom:12px;box-sizing:border-box">
        <button class="btn-signin" id="btnVerify" type="button">Verify email</button>
        <button class="btn-signin" id="btnResend" type="button" style="background:#fff;color:#4a545f;border:1px solid #dfe4ea;margin-top:10px;font-size:13px" disabled>Resend code (45s)</button>
      </div>
'''

# insert verify box right after the signup pane's "Continue with Github" button
anchor = 'Continue with Github\n        </button>\n      </div>\n    </div>\n  </section>'
# the full pattern only matches the signup pane (last pane before </section>)
idx = s.find(anchor)
assert idx > -1, 'anchor missing'
s = s[:idx + len(anchor)] + verify_box + s[idx + len(anchor):]

# replace the whole inline demo script
m = re.search(r'<script>\n/\* ---------- auth demo logic.*?</script>', s, re.S)
assert m, 'script block not found'

new_script = r'''<script>
/* ---------- NFlashX auth (server-backed) ---------- */
const $ = s => document.querySelector(s);
const api = (path, body) => fetch('/api/auth/' + path, {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {})
}).then(async r => { const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Request failed'); return j; });

if (localStorage.getItem('nfx_session')) location.replace('account.html');

/* rotate brand cards */
setInterval(() => {
  const cards = document.querySelectorAll('#abCards .lb-card');
  const show = [...cards].findIndex(c => c.classList.contains('show'));
  cards[show].classList.remove('show');
  cards[(show + 1) % cards.length].classList.add('show');
}, 6000);

document.querySelectorAll('.pw-toggle').forEach(b => b.onclick = () => {
  const i = document.getElementById(b.dataset.for);
  i.type = i.type === 'password' ? 'text' : 'password';
});

$('#gotoSignup').onclick = e => { e.preventDefault(); $('#paneSignin').style.display = 'none'; $('#paneSignup').style.display = 'block'; };
$('#gotoSignin').onclick = e => { e.preventDefault(); $('#paneSignup').style.display = 'none'; $('#paneSignin').style.display = 'block'; };

const showErr = (id, msg) => { const b = $(id); b.textContent = msg; b.style.display = msg ? 'block' : 'none'; };
const validEmail = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
let pendingEmail = null, resendTimer = null;

function startSession(r) {
  localStorage.setItem('nfx_session', JSON.stringify({ token: r.token, email: r.user.email, name: r.user.name }));
  location.href = 'account.html';
}
function showVerify(email, devCode) {
  pendingEmail = email;
  $('#paneSignup').style.display = 'none';
  $('#verifyBox').style.display = 'block';
  $('#vEmail').textContent = email;
  showErr('#errVerify', devCode ? 'DEV MODE (mail not configured) — your code: ' + devCode : '');
  cooldown();
  $('#vCode').focus();
}
function cooldown() {
  const b = $('#btnResend'); let s = 45; b.disabled = true;
  clearInterval(resendTimer);
  resendTimer = setInterval(() => {
    s--; b.textContent = 'Resend code (' + s + 's)';
    if (s <= 0) { clearInterval(resendTimer); b.disabled = false; b.textContent = 'Resend code'; }
  }, 1000);
}

$('#formSignin').addEventListener('submit', async e => {
  e.preventDefault();
  const email = $('#siEmail').value.trim().toLowerCase(), pass = $('#siPass').value;
  if (!validEmail(email)) return showErr('#errSignin', 'Please enter a valid email address.');
  if (!pass) return showErr('#errSignin', 'Please enter your password.');
  showErr('#errSignin', '');
  const btn = $('#btnSignin'); btn.disabled = true; btn.textContent = 'Signing in…';
  try {
    const r = await api('login', { email, password: pass });
    startSession(r);
  } catch (err) {
    btn.disabled = false; btn.textContent = 'Sign In';
    showErr('#errSignin', err.message);
  }
});

$('#formSignup').addEventListener('submit', async e => {
  e.preventDefault();
  const name = $('#suName').value.trim(), email = $('#suEmail').value.trim().toLowerCase();
  const pass = $('#suPass').value, pass2 = $('#suPass2').value;
  if (!name) return showErr('#errSignup', 'Please enter your full name.');
  if (!validEmail(email)) return showErr('#errSignup', 'Please enter a valid email address.');
  if (pass.length < 6) return showErr('#errSignup', 'Password must be at least 6 characters.');
  if (pass !== pass2) return showErr('#errSignup', 'Passwords do not match.');
  showErr('#errSignup', '');
  const btn = $('#btnSignup'); btn.disabled = true; btn.textContent = 'Creating account…';
  try {
    const r = await api('signup', { name, email, password: pass });
    showVerify(email, r.dev_code);
    btn.disabled = false; btn.textContent = 'Create account';
  } catch (err) {
    btn.disabled = false; btn.textContent = 'Create account';
    showErr('#errSignup', err.message);
  }
});

$('#btnVerify').onclick = async () => {
  const code = $('#vCode').value.trim();
  try {
    const r = await api('verify', { email: pendingEmail, code });
    startSession(r);
  } catch (err) { showErr('#errVerify', err.message); }
};
$('#btnResend').onclick = async () => {
  try {
    const r = await api('resend', { email: pendingEmail });
    showErr('#errVerify', r.dev_code ? 'DEV MODE — code: ' + r.dev_code : 'New code sent. Check your inbox.');
    cooldown();
  } catch (err) { showErr('#errVerify', err.message); }
};

/* oauth: redirect to the real provider (needs data/oauth_config.json) */
document.querySelectorAll('.btn-oauth').forEach(b => b.onclick = async () => {
  const p = b.dataset.provider.toLowerCase();
  try {
    const r = await fetch('/api/auth/oauth/' + p + '/start').then(x => x.json());
    if (r.url) location.href = r.url;
    else showErr('#errSignin', r.error);
  } catch (err) { showErr('#errSignin', 'OAuth is not available right now.'); }
});

$('#linkForgot').onclick = e => {
  e.preventDefault();
  const n = $('#noteForgot');
  n.style.display = 'block';
  clearTimeout(n._t); n._t = setTimeout(() => n.style.display = 'none', 4000);
};
</script>'''
s = s[:m.start()] + new_script + s[m.end():]
io.open(p, 'w', encoding='utf-8').write(s)
print('login.html rewritten OK')
