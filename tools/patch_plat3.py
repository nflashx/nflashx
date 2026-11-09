import io, re

pcss = 'css/platform.css'
pcs = io.open(pcss, encoding='utf-8').read()
old_lc_css = re.search(r'\.plat \.live-chat\{[^}]*\}', pcs)
assert old_lc_css, 'old live-chat css rule not found in platform.css'
pcs = pcs.replace(old_lc_css.group(0), '')  # remove old rule; new block appended below

p = 'platform.html'
s = io.open(p, encoding='utf-8').read()

# ================= 1. CSS: thay toàn bộ khối .live-chat + .lc-* cũ =================
new_lc = r'''.plat .live-chat{position:fixed;bottom:26px;right:26px;z-index:80;display:inline-flex;align-items:center;gap:9px;padding:13px 22px;border-radius:999px;background:#0c1014;color:#fff;font-size:14px;font-weight:600;border:0;cursor:pointer;box-shadow:0 14px 40px rgba(0,0,0,.25)}
.plat .live-chat:hover{transform:translateY(-2px)}
.lc-panel{position:fixed;bottom:26px;right:26px;z-index:120;width:380px;height:520px;background:#fff;border-radius:14px;box-shadow:0 24px 80px rgba(0,0,0,.3);display:none;flex-direction:column;overflow:hidden;border:1px solid #e8ecf0}
.lc-panel.on{display:flex}
.lc-head{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid #e8ecf0;background:#fff}
.lc-head img{width:30px;height:30px;border-radius:50%}
.lc-head b{font-size:15px;color:#14181d;font-weight:600;flex:1}
.lc-head .lc-ic{border:0;background:none;cursor:pointer;color:#5c6975;width:28px;height:28px;border-radius:7px;display:grid;place-items:center}
.lc-head .lc-ic:hover{background:#f0f3f6;color:#14181d}
.lc-body{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;background:#fff}
.lc-panel.min .lc-body,.lc-panel.min .lc-input{display:none}
.lc-row{display:flex;gap:9px;align-items:flex-start}
.lc-row .lc-ava{width:30px;height:30px;border-radius:50%;flex:none;background:#3b5bdb;display:grid;place-items:center}
.lc-row .lc-ava img{width:18px;height:18px}
.lc-bubble{background:#eef4ff;border-radius:4px 14px 14px 14px;padding:12px 14px;font-size:13.5px;line-height:1.55;color:#14181d;max-width:85%}
.lc-row.me{justify-content:flex-end}
.lc-row.me .lc-bubble{background:#eef1f4;border-radius:14px 4px 14px 14px}
.lc-quick{display:flex;flex-direction:column;gap:9px;padding:2px 0 4px 39px}
.lc-quick a{color:#0c6bd6;font-size:13.5px;text-decoration:none}
.lc-quick a::before{content:"· ";font-weight:700}
.lc-quick a:hover{text-decoration:underline}
.lc-hint{text-align:center;color:#a5aeb8;font-size:12.5px;padding:6px 0 2px}
.lc-input{margin:10px;border:1px solid #dfe4ea;border-radius:11px;display:flex;flex-direction:column}
.lc-input input{border:0;outline:0;padding:13px 15px;font-size:13.5px;background:transparent}
.lc-input .lc-sendrow{display:flex;justify-content:flex-end;padding:0 12px 11px}
.lc-send{border:0;background:#c9cfd6;color:#fff;font-size:13px;font-weight:600;padding:8px 20px;border-radius:999px;cursor:pointer;transition:.2s}
.lc-send.on{background:#3b5bdb}
/* key operations icons */
.plat .ops{display:inline-flex;gap:12px;align-items:center}
.plat .ops button{border:0;background:none;cursor:pointer;color:#5c6975;padding:2px;display:grid;place-items:center}
.plat .ops button:hover{color:#14181d}
.plat .ops svg{width:15px;height:15px}
/* mini popup (create / rename key) */
.kp-backdrop{position:fixed;inset:0;z-index:650;background:rgba(20,24,30,.45);display:grid;place-items:center;opacity:0;visibility:hidden;transition:.2s}
.kp-backdrop.on{opacity:1;visibility:visible}
.kp-card{width:min(460px,92vw);background:#fff;border-radius:12px;padding:22px 24px;box-shadow:0 24px 80px rgba(0,0,0,.3)}
.kp-card b{font-size:15.5px}
.kp-card input{width:100%;margin:18px 0 22px;padding:13px 15px;border-radius:9px;border:1px solid #e3e7ec;background:#f6f8fa;font-size:14px;outline:0;box-sizing:border-box}
.kp-card input:focus{background:#fff;border-color:#c9d1d9}
.kp-btns{display:flex;justify-content:flex-end;gap:10px}
.kp-btns .kp-cancel{padding:9px 20px;border-radius:9px;border:1px solid #dfe4ea;background:#fff;font-size:13.5px;cursor:pointer}
.kp-btns .kp-save{padding:9px 22px;border-radius:9px;border:0;background:#0c1014;color:#fff;font-size:13.5px;font-weight:600;cursor:pointer}
.kp-btns .kp-save:disabled{opacity:.45;cursor:default}'''
pcs += new_lc  # append new live-chat styles to platform.css

# ================= 2. HTML: thay lc-panel + thêm key popup =================
old_panel = re.search(r'<div class="lc-panel" id="lcPanel">.*?</div>\n\n<script>', s, re.S)
assert old_panel, 'lc panel not found'
new_panel = r'''<div class="lc-panel" id="lcPanel">
  <div class="lc-head">
    <img src="assets/logo.svg" alt="">
    <b>NFlashX Support</b>
    <button class="lc-ic" title="Email support" onclick="location.href='mailto:support@nflashx.com'"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/></svg></button>
    <button class="lc-ic" id="lcMin" title="Minimize"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></button>
    <button class="lc-ic" id="lcClose" title="Close"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
  </div>
  <div class="lc-body" id="lcBody">
    <div class="lc-row">
      <span class="lc-ava"><img src="assets/logo.svg" alt=""></span>
      <div class="lc-bubble">Hi, I'm NFlashX AI support. I can help with product usage, accounts, subscriptions, Credits, and more. How can I help you?</div>
    </div>
    <div class="lc-quick" id="lcQuick">
      <a href="#" data-q="How to get an API Key">How to get an API Key</a>
      <a href="#" data-q="How to connect a model">How to connect a model</a>
      <a href="#" data-q="Model pricing">Model pricing</a>
      <a href="#" data-q="What is Tokenplan? What plans are available?">What is Tokenplan? What plans are available?</a>
      <a href="#" data-q="How to subscribe to Tokenplan">How to subscribe to Tokenplan</a>
      <a href="#" data-q="How to troubleshoot API errors">How to troubleshoot API errors</a>
    </div>
    <div class="lc-hint">Click a quick question to send</div>
  </div>
  <div class="lc-input">
    <input id="lcInput" type="text" placeholder="Enter your question">
    <div class="lc-sendrow"><button class="lc-send" id="lcSend">Send</button></div>
  </div>
</div>

<div class="kp-backdrop" id="kpBackdrop">
  <div class="kp-card">
    <b id="kpTitle">Create new secret key</b>
    <input id="kpInput" type="text" placeholder="Please enter a key name" maxlength="40">
    <div class="kp-btns">
      <button class="kp-cancel" id="kpCancel">Cancel</button>
      <button class="kp-save" id="kpSave" disabled>Save</button>
    </div>
  </div>
</div>

<script>'''
s = s[:old_panel.start()] + new_panel + s[old_panel.end():]

# ================= 3. JS: live chat mới + key management =================
old_js = re.search(r'/\* live chat \*/\s*\(function \(\) \{.*?\}\)\(\);', s, re.S)
assert old_js, 'old live chat js not found'
new_js = r'''/* ---------- live chat (Agnes Support style) ---------- */
(function () {
  const btn = document.querySelector('.live-chat'), panel = document.getElementById('lcPanel');
  btn.onclick = () => { panel.classList.add('on'); panel.classList.remove('min'); };
  document.getElementById('lcClose').onclick = () => panel.classList.remove('on');
  document.getElementById('lcMin').onclick = () => panel.classList.toggle('min');

  const body = document.getElementById('lcBody'), input = document.getElementById('lcInput');
  const send = document.getElementById('lcSend');
  const ANSWERS = {
    'How to get an API Key': 'Sign in, open Settings → API Keys and click "Create new secret key". Your key starts with sk-nfx-… and has full access on the Free plan.',
    'How to connect a model': 'Use the OpenAI-compatible base URL https://apihub.nflashx.com/v1 with your key, then set "model" to nflashx-1.0-flash or nflashx-1.0-pro.',
    'Model pricing': 'Text (Flash): $0.10/M input, $0.15/M output — free in trial. Images: from $0.010/image. Video: $0.025/second at 720P.',
    'What is Tokenplan? What plans are available?': 'Token Plan gives starter quotas per model (requests, images, video seconds). Agent Plan adds shared Credits across all modalities — Lite, Plus, Pro and Max tiers.',
    'How to subscribe to Tokenplan': 'Open Subscribe → Token Plan in the sidebar and pick a tier. On Agent Plan, credits refresh every 5 hours.',
    'How to troubleshoot API errors': 'First check your API key and the Base URL (must end with /v1). Then read the error code: 401 wrong key, 429 rate limit, 400 invalid parameters.'
  };
  const GENERIC = 'Thanks for your question! Our team will follow up by email. Meanwhile, tap one of the quick questions above for instant answers.';

  function bubble(text, me) {
    const row = document.createElement('div');
    row.className = 'lc-row' + (me ? ' me' : '');
    if (!me) row.innerHTML = '<span class="lc-ava"><img src="assets/logo.svg" alt=""></span>';
    const b = document.createElement('div');
    b.className = 'lc-bubble'; b.textContent = text;
    row.appendChild(b);
    body.appendChild(row);
    body.scrollTop = body.scrollHeight;
    const hint = body.querySelector('.lc-hint');
    if (hint && !me) return;
    if (me) { const q = body.querySelector('.lc-quick'); if (q) q.style.display = 'none'; const h = body.querySelector('.lc-hint'); if (h) h.style.display = 'none'; }
  }
  function ask(q) {
    bubble(q, true);
    setTimeout(() => bubble(ANSWERS[q] || GENERIC, false), 500);
  }
  document.getElementById('lcQuick').addEventListener('click', e => {
    const a = e.target.closest('a'); if (!a) return;
    e.preventDefault(); ask(a.dataset.q);
  });
  function sendMsg() {
    const t = input.value.trim(); if (!t) return;
    input.value = ''; ask(t);
    send.classList.remove('on');
  }
  send.onclick = sendMsg;
  input.addEventListener('input', () => send.classList.toggle('on', input.value.trim().length > 0));
  input.addEventListener('keydown', e => { if (e.key === 'Enter') sendMsg(); });
})();

/* ---------- API keys: create / rename / delete / copy (Agnes style) ---------- */
(function () {
  const KP = 'nfx_keys';
  let keys = [];
  try { keys = JSON.parse(localStorage.getItem(KP) || 'null'); } catch (_) {}
  if (!Array.isArray(keys) || !keys.length) {
    keys = [{ name: 'Default key', key: (sess && sess.apiKey) || ('sk-nfx-' + [...crypto.getRandomValues(new Uint8Array(20))].map(b => b.toString(16).padStart(2, '0')).join('')), created: new Date().toISOString().slice(0, 10) + ' UTC', last: '---' }];
  }
  const save = () => localStorage.setItem(KP, JSON.stringify(keys));

  const mask = k => k.slice(0, 8) + '...' + k.slice(-6);
  const ICONS = {
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 012-2h10"/></svg>',
    edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 3a2.8 2.8 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>',
    del: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M8 6V4a1 1 0 011-1h6a1 1 0 011 1v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/></svg>'
  };

  function renderTable() {
    const tbody = document.getElementById('keyRows');
    if (!tbody) return;
    if (!keys.length) {
      tbody.innerHTML = '<tr><td colspan="5"><div class="no-data">No data</div></td></tr>';
      return;
    }
    tbody.innerHTML = keys.map((k, i) => `
      <tr>
        <td style="color:#14181d;font-weight:500">${k.name}</td>
        <td class="mono">${mask(k.key)}</td>
        <td>${k.created}</td>
        <td>${k.last}</td>
        <td><span class="ops">
          <button title="Copy key" data-op="copy" data-i="${i}">${ICONS.copy}</button>
          <button title="Rename" data-op="rename" data-i="${i}">${ICONS.edit}</button>
          <button title="Delete" data-op="del" data-i="${i}">${ICONS.del}</button>
        </span></td>
      </tr>`).join('');
  }
  renderTable();

  /* mini popup (create / rename) */
  const kp = document.getElementById('kpBackdrop');
  let mode = 'create', editIdx = -1;
  function openPopup(title, preset) {
    document.getElementById('kpTitle').textContent = title;
    const inp = document.getElementById('kpInput');
    inp.value = preset || '';
    document.getElementById('kpSave').disabled = !preset;
    kp.classList.add('on');
    setTimeout(() => inp.focus(), 80);
  }
  document.getElementById('kpInput').addEventListener('input', e => {
    document.getElementById('kpSave').disabled = !e.target.value.trim();
  });
  document.getElementById('kpCancel').onclick = () => kp.classList.remove('on');
  kp.addEventListener('click', e => { if (e.target === kp) kp.classList.remove('on'); });
  document.getElementById('kpSave').onclick = () => {
    const name = document.getElementById('kpInput').value.trim();
    if (!name) return;
    if (mode === 'create') {
      const key = 'sk-nfx-' + [...crypto.getRandomValues(new Uint8Array(20))].map(b => b.toString(16).padStart(2, '0')).join('');
      keys.push({ name, key, created: new Date().toISOString().slice(0, 10) + ' UTC', last: '---' });
    } else if (editIdx > -1) {
      keys[editIdx].name = name;
    }
    save(); renderTable(); kp.classList.remove('on');
  };

  document.addEventListener('click', e => {
    const b = e.target.closest('.ops button'); if (!b) return;
    const i = +b.dataset.i, op = b.dataset.op, k = keys[i];
    if (op === 'copy') { navigator.clipboard.writeText(k.key).catch(() => {}); b.style.color = '#25c93f'; setTimeout(() => b.style.color = '', 1000); }
    if (op === 'rename') { mode = 'rename'; editIdx = i; openPopup('Rename the key', k.name); }
    if (op === 'del') {
      if (!confirm('Delete the key "' + k.name + '"? Apps using it will stop working.')) return;
      keys.splice(i, 1); save(); renderTable();
    }
  });

  /* Create new secret key → popup */
  document.querySelectorAll('#createKey').forEach(b => b.onclick = () => {
    mode = 'create'; editIdx = -1; openPopup('Create new secret key', '');
  });
})();'''
s = s[:old_js.start()] + new_js + s[old_js.end():]

io.open(p, 'w', encoding='utf-8').write(s)
pcs += new_lc  # new live-chat styles appended at end (overrides old)
io.open(pcss, 'w', encoding='utf-8').write(pcs)
print('platform.html live chat + keys rewritten OK; platform.css updated')
