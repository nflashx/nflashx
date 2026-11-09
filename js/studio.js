/* ============================================================
   NFlashX Vision Studio — generation logic
   Engines map to the platform image API through the local
   proxy (/api/images). "Cloud Free" falls back to Pollinations.
   ============================================================ */
const ENGINES = {
  'nflashx-vision-1.0-flash': { label: 'NFlashX Vision 1.0 Flash', model: 'nflashx-vision-1.0-flash', free: true,
                          suffix: ', ultra detailed, high quality' },
  'nflashx-vision-1.1': { label: 'NFlashX Vision 1.0 Fast', model: 'nflashx-vision-1.1', free: true,
                          suffix: '' },
  'nflashx-vision-1.0': { label: 'NFlashX Vision 1.0 Classic', model: 'nflashx-vision-1.0', free: true,
                          suffix: '' },
  'nflashx-cloud':      { label: 'NFlashX Cloud · Free', model: '@pollinations/sana', free: true,
                          suffix: '' },
};

const TEMPLATES = {
  'logo-minimal':  { pre: 'minimal vector logo of', post: ', flat design, simple shapes, high contrast, white background, professional branding', ratio: '1024x1024' },
  'logo-badge':    { pre: 'circular emblem badge logo of', post: ', vintage crest style, clean lines, centered, solid background', ratio: '1024x1024' },
  'logo-letter':   { pre: 'lettermark logo with the capital letter N, featuring', post: ', bold geometric typography, gradient indigo to green, dark background', ratio: '1024x1024' },
  'logo-neon':     { pre: 'neon sign logo of', post: ', glowing tubes on dark wall, night vibe, photorealistic', ratio: '1024x1024' },
  'frame-poster':  { pre: 'cinematic movie poster of', post: ', dramatic lighting, title space at bottom, professional composition', ratio: '864x1152' },
  'frame-polaroid':{ pre: 'vintage polaroid photo of', post: ', soft flash light, nostalgic 90s film look, white border', ratio: '864x1152' },
  'frame-gold':    { pre: 'ornate baroque golden picture frame surrounding', post: ', museum lighting, luxurious', ratio: '864x1152' },
  'none':          { pre: '', post: '' },
};

const $ = id => document.getElementById(id);
const promptEl = $('prompt'), engineEl = $('engine'), ratioEl = $('ratio'),
      frameEl = $('frame'), captionEl = $('caption'), seedEl = $('seed'),
      batchEl = $('batch'), stage = $('stage'), shimmer = $('shimmer'),
      shimSub = $('shimSub'), errBox = $('errBox'), hist = $('history');
const tools = ['dlBtn', 'openBtn', 'reBtn', 'upBtn'].map($);

let currentURL = '', history_ = [], busy = false;

/* ---------- chips ---------- */
$('templates').addEventListener('click', e => {
  const b = e.target.closest('.chip'); if (!b) return;
  $('templates').querySelectorAll('.chip').forEach(c => c.classList.remove('sel'));
  b.classList.add('sel');
  const t = TEMPLATES[b.dataset.t];
  if (t && t.ratio) ratioEl.value = t.ratio;
  if (b.dataset.t === 'frame-polaroid') frameEl.value = 'f-polaroid';
  if (b.dataset.t === 'frame-gold') frameEl.value = 'f-gold';
});
$('styles').addEventListener('click', e => {
  const b = e.target.closest('.chip'); if (!b) return;
  $('styles').querySelectorAll('.chip').forEach(c => c.classList.remove('sel'));
  b.classList.add('sel');
});

/* ---------- prompt composition ---------- */
function composePrompt(q) {
  const eng = ENGINES[engineEl.value];
  const tplKey = document.querySelector('#templates .chip.sel')?.dataset.t || 'none';
  const tpl = TEMPLATES[tplKey] || TEMPLATES.none;
  const style = document.querySelector('#styles .chip.sel')?.dataset.s || '';
  return [tpl.pre, q.trim(), tpl.post, style + eng.suffix].filter(Boolean).join(' ');
}

/* ---------- API calls ---------- */
async function apiImage(model, prompt, w, h, seed) {
  let token = '';
  try { token = (JSON.parse(localStorage.getItem('nfx_session') || 'null') || {}).token || ''; } catch (_) {}
  const r = await fetch('/api/images', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, prompt, size: `${w}x${h}`, n: 1, seed: seed || undefined, token }),
  });
  const j = await r.json();
  const url = j?.data?.[0]?.url;
  if (!url) throw new Error(j?.error?.message || j?.error || j?.message || 'no url in response');
  return url;
}
function pollinationsImage(prompt, w, h, seed) {
  return 'https://image.pollinations.ai/prompt/' + encodeURIComponent(prompt) +
         `?width=${w}&height=${h}&seed=${seed}&nologo=true&model=sana`;
}

function loadImageEl(url) {
  return new Promise((res, rej) => {
    const img = new Image();
    const to = setTimeout(() => rej(new Error('timeout')), 180000);
    img.onload = () => { clearTimeout(to); res(url); };
    img.onerror = () => { clearTimeout(to); rej(new Error('image fetch failed')); };
    img.src = url;
  });
}

/* ---------- generate (sequential to respect API limits) ---------- */
async function generate(customSeed) {
  if (busy) return;
  const q = promptEl.value.trim();
  if (!q) { showErr('Nhập prompt đã bạn ơi — describe your idea first.'); promptEl.focus(); return; }
  hideErr(); busy = true;
  $('genBtn').disabled = true;
  const eng = ENGINES[engineEl.value];
  shimSub.textContent = eng.label + ' · painting your idea…';
  shimmer.style.display = 'grid';
  tools.forEach(t => t.disabled = true);

  const n = +batchEl.value;
  const [w, h] = ratioEl.value.split('x');
  const prompt = composePrompt(q);
  const results = [];

  for (let i = 0; i < n; i++) {
    const s = customSeed != null ? customSeed + i : (seedEl.value ? +seedEl.value + i : Math.floor(Math.random() * 999999));
    shimSub.textContent = `${eng.label} · rendering ${i + 1}/${n} (seed ${s})`;
    try {
      let url;
      if (eng.model.startsWith('@pollinations')) {
        url = pollinationsImage(prompt, w, h, s);
      } else {
        url = await apiImage(eng.model, prompt, w, h, s);
      }
      await loadImageEl(url);
      const item = { url, seed: s, prompt };
      results.push(item);
      history_.unshift(item);
      renderHistory();
      show(item);                      // show as soon as ready
    } catch (e) {
      if (!results.length) showErr('Lỗi: ' + e.message + ' — thử lại hoặc đổi Engine bên dưới nhé.');
    }
  }

  shimmer.style.display = 'none';
  busy = false; $('genBtn').disabled = false;
  if (!results.length) tools.forEach(t => t.disabled = true);
}

/* ---------- stage ---------- */
function show(item) {
  currentURL = item.url;
  stage.querySelectorAll('.result-wrap').forEach(n => n.remove());
  $('placeholder').style.display = 'none';
  const wrap = document.createElement('div');
  wrap.className = 'result-wrap';
  const fw = document.createElement('div');
  fw.className = 'frame-wrap ' + (frameEl.value !== 'none' ? frameEl.value : '');
  const img = document.createElement('img');
  img.className = 'result'; img.src = item.url; img.alt = 'NFlashX generated';
  fw.appendChild(img);
  if (frameEl.value === 'f-polaroid') {
    const cap = document.createElement('div');
    cap.className = 'cap'; cap.textContent = captionEl.value || 'NFlashX ✦';
    fw.appendChild(cap);
  }
  wrap.appendChild(fw);
  stage.appendChild(wrap);
  tools.forEach(t => t.disabled = false);
  [...hist.children].forEach((h, i) => h.classList.toggle('sel', history_[i] === item));
}

function renderHistory() {
  hist.innerHTML = '';
  history_.slice(0, 14).forEach(item => {
    const b = document.createElement('button');
    b.className = 'h-item';
    const img = document.createElement('img');
    img.src = item.url; img.loading = 'lazy';
    b.appendChild(img);
    b.onclick = () => show(item);
    hist.appendChild(b);
  });
}

/* ---------- tools ---------- */
$('dlBtn').onclick = async () => {
  if (!currentURL) return;
  try {
    const r = await fetch(currentURL); const b = await r.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b);
    a.download = 'nflashx-' + Date.now() + '.jpg';
    a.click(); URL.revokeObjectURL(a.href);
  } catch (_) { window.open(currentURL, '_blank'); }
};
$('openBtn').onclick = () => currentURL && window.open(currentURL, '_blank');
$('reBtn').onclick = () => generate(Math.floor(Math.random() * 999999));
$('upBtn').onclick = () => {
  if (!currentURL || busy) return;
  currentURL = currentURL.replace(/(\d+)x(\d+)/, (m, a, b) => `${Math.min(+a * 2, 4096)}x${Math.min(+b * 2, 4096)}`);
  busy = true; shimmer.style.display = 'grid';
  shimSub.textContent = 'Upscaling ×2…';
  loadImageEl(currentURL).then(() => {
    shimmer.style.display = 'none'; busy = false;
    show({ url: currentURL });
  }).catch(() => { shimmer.style.display = 'none'; busy = false; showErr('Upscale lỗi, thử lại nhé.'); });
};

/* ---------- errors ---------- */
function showErr(m) { errBox.textContent = m; errBox.style.display = 'block'; }
function hideErr() { errBox.style.display = 'none'; }

/* ---------- boot ---------- */
$('genBtn').onclick = () => generate();
promptEl.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') generate();
});
(function boot() {
  const qs = new URLSearchParams(location.search);
  const q = qs.get('q') || (() => { try { return sessionStorage.getItem('nfx_prompt'); } catch (_) { return null; } })();
  if (q) { promptEl.value = q; generate(); }
})();
