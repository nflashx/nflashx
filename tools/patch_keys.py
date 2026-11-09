import io, re

p = 'platform.html'
s = io.open(p, encoding='utf-8').read()

# ---------- 1. thay PAGES 'api-keys' bằng bản server-backed ----------
marker = "  'api-keys': {"
i = s.find(marker)
assert i > -1, 'api-keys entry not found'
j = s.find('\n  },', i)
new_api = '''  'api-keys': {
    title: 'API Keys',
    render(u) {
      return `
      <h1>API Keys</h1>
      <p class="desc">Do not share your API key with others, or expose it in the browser or other client-side code.</p>
      <p class="desc">1. Create a secret key; 2. Connect to NFlashX omnimodal free models; 3. Start exploring.</p>
      <div class="btn-row" style="justify-content:space-between;align-items:center;margin-bottom:0">
        <button class="btn-dark sm" id="createKey">Create new secret key</button>
        <a class="linklike" href="docs.html#quickstart" style="text-decoration:none">Connect Coding Tools ↗</a>
      </div>
      <table class="apitable">
        <thead><tr><th style="width:22%">Name</th><th style="width:26%">Secret Key</th><th style="width:22%">Created time(UTC)</th><th style="width:16%">Last used(UTC)</th><th>Operations</th></tr></thead>
        <tbody id="keyRows"><tr><td colspan="5"><div class="no-data">Loading…</div></td></tr></tbody>
      </table>
      <h2>Enterprise Keys</h2>
      <p class="desc">After completing Enterprise Verification, you can create enterprise API keys. Enterprise API keys have 2× the RPM limit of free personal user keys.</p>
      <div class="empty">Enterprise Verification is required before creating enterprise keys.</div>`;
    },
    after() { loadKeys(); }
  },'''
s = s[:i] + new_api + s[j + len('\n  },') + 1:]

# ---------- 2. thay IIFE key management cũ bằng bản server-backed ----------
old_iife = re.search(r'/\* ---------- API keys: create / rename / delete / copy \(Agnes style\) ---------- \*/\s*\(function \(\) \{.*?\}\)\(\);', s, re.S)
assert old_iife, 'old keys iife not found'
new_iife = r'''/* ---------- API keys: server-backed create / rename / delete / copy ---------- */
let KEYS = [];
async function loadKeys() {
  try {
    const r = await api('keys', { token: sess.token });
    KEYS = r.keys;
    sess.apiKey = KEYS.length ? KEYS[0].key : sess.apiKey;
    renderKeyRows();
  } catch (e) { console.warn(e.message); }
}
function renderKeyRows() {
  const tb = document.getElementById('keyRows');
  if (!tb) return;
  if (!KEYS.length) {
    tb.innerHTML = '<tr><td colspan="5"><div class="no-data">No data</div></td></tr>';
    return;
  }
  const ICONS = {
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 012-2h10"/></svg>',
    edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 3a2.8 2.8 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>',
    del: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M8 6V4a1 1 0 011-1h6a1 1 0 011 1v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/></svg>'
  };
  tb.innerHTML = KEYS.map((k, i) => `
    <tr>
      <td style="color:#14181d;font-weight:500">${k.name.replace(/</g, '&lt;')}</td>
      <td class="mono">${k.key.slice(0, 8)}...${k.key.slice(-6)}</td>
      <td>${k.created} UTC</td>
      <td>${k.last_used}</td>
      <td><span class="ops">
        <button title="Copy key" data-op="copy" data-i="${i}">${ICONS.copy}</button>
        <button title="Rename" data-op="rename" data-i="${i}">${ICONS.edit}</button>
        <button title="Delete" data-op="del" data-i="${i}">${ICONS.del}</button>
      </span></td>
    </tr>`).join('');
}
document.addEventListener('click', e => {
  const b = e.target.closest('.ops button'); if (!b) return;
  const i = +b.dataset.i, op = b.dataset.op, k = KEYS[i];
  if (op === 'copy') { navigator.clipboard.writeText(k.key).catch(() => {}); b.style.color = '#25c93f'; setTimeout(() => b.style.color = '', 1000); }
  if (op === 'rename') openKeyPopup('Rename the key', k.name, async name => {
    await api('keys/rename', { token: sess.token, key: k.key, name });
    loadKeys();
  });
  if (op === 'del') {
    if (!confirm('Delete the key "' + k.name + '"? Apps using it will stop working.')) return;
    api('keys/delete', { token: sess.token, key: k.key }).then(loadKeys).catch(err => alert(err.message));
  }
});

/* mini popup dùng chung cho create + rename */
const kpBackdrop = document.getElementById('kpBackdrop');
let kpSaveCb = null;
function openKeyPopup(title, preset, onSave) {
  document.getElementById('kpTitle').textContent = title;
  const inp = document.getElementById('kpInput');
  inp.value = preset || '';
  document.getElementById('kpSave').disabled = !preset;
  kpSaveCb = onSave;
  kpBackdrop.classList.add('on');
  setTimeout(() => inp.focus(), 80);
}
document.getElementById('kpInput').addEventListener('input', e => {
  document.getElementById('kpSave').disabled = !e.target.value.trim();
});
document.getElementById('kpCancel').onclick = () => kpBackdrop.classList.remove('on');
kpBackdrop.addEventListener('click', e => { if (e.target === kpBackdrop) kpBackdrop.classList.remove('on'); });
document.getElementById('kpSave').onclick = async () => {
  const name = document.getElementById('kpInput').value.trim();
  if (!name || !kpSaveCb) return;
  kpBackdrop.classList.remove('on');
  await kpSaveCb(name);
};'''
s = s[:old_iife.start()] + new_iife + s[old_iife.end():]

# ---------- 3. nút createKey mở popup ----------
s = s.replace("document.querySelectorAll('#createKey').forEach(b => b.onclick = () => {\n    mode = 'create'; editIdx = -1; openPopup('Create new secret key', '');\n  });",
              "document.querySelectorAll('#createKey').forEach(b => b.onclick = () => openKeyPopup('Create new secret key', '', async name => {\n    const r = await api('keys/create', { token: sess.token, name });\n    KEYS = r.keys; renderKeyRows();\n  }));")

io.open(p, 'w', encoding='utf-8').write(s)
print('platform.html server-backed keys OK')
