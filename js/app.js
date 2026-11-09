/* ============================================================
   NFlashX 1.0 — shared behaviors
   ============================================================ */

/* ---------- starfield ---------- */
(function () {
  const cv = document.getElementById('stars');
  if (!cv) return;
  const ctx = cv.getContext('2d');
  let stars = [], W, H;
  function resize() {
    W = cv.width = innerWidth; H = cv.height = innerHeight;
    stars = Array.from({ length: Math.min(220, W / 6) }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.4 + .2, p: Math.random() * Math.PI * 2,
      s: .4 + Math.random() * 1.2, vy: -(Math.random() * .06 + .01)
    }));
  }
  function tick(t) {
    ctx.clearRect(0, 0, W, H);
    for (const st of stars) {
      st.y += st.vy; if (st.y < -4) st.y = H + 4;
      const a = .25 + .75 * Math.abs(Math.sin(t / 900 * st.s + st.p));
      ctx.globalAlpha = a * .8;
      ctx.fillStyle = st.r > 1 ? '#cfe6ff' : '#9fb4d8';
      ctx.beginPath(); ctx.arc(st.x, st.y, st.r, 0, 7); ctx.fill();
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(tick);
  }
  addEventListener('resize', resize);
  resize(); requestAnimationFrame(tick);
})();

/* ---------- navbar scroll ---------- */
const nav = document.getElementById('nav');
if (nav) addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 24), { passive: true });

/* ---------- dropdowns ---------- */
(function () {
  const items = document.querySelectorAll('.menu > li[data-drop]');
  const drops = {};
  document.querySelectorAll('.drop').forEach(d => drops[d.id.replace('drop-', '')] = d);
  let openKey = null, closeTimer;

  function place(key, li) {
    const d = drops[key]; if (!d || !li) return;
    const r = li.getBoundingClientRect();
    if (d.classList.contains('models')) {
      d.style.left = Math.max(12, r.left - 250) + 'px';
    } else {
      d.style.left = Math.max(12, r.left - 30) + 'px';
    }
  }
  function open(key, li) {
    clearTimeout(closeTimer);
    Object.values(drops).forEach(d => d.classList.remove('open'));
    const d = drops[key]; if (!d) return;
    place(key, li);
    d.classList.add('open');
    openKey = key;
  }
  function closeSoon() {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      Object.values(drops).forEach(d => d.classList.remove('open'));
      openKey = null;
    }, 180);
  }
  items.forEach(li => {
    li.addEventListener('mouseenter', () => open(li.dataset.drop, li));
    li.addEventListener('mouseleave', closeSoon);
  });
  Object.entries(drops).forEach(([k, d]) => {
    d.addEventListener('mouseenter', () => clearTimeout(closeTimer));
    d.addEventListener('mouseleave', closeSoon);
  });
  addEventListener('scroll', () => { if (openKey) Object.values(drops).forEach(d => d.classList.remove('open')); }, { passive: true });
})();

/* ---------- hero slider ---------- */
(function () {
  const hero = document.getElementById('hero');
  if (!hero) return;
  const slides = [...hero.querySelectorAll('.slide')];
  const dotsWrap = document.getElementById('dots');
  let cur = 0, timer;

  slides.forEach((_, i) => {
    const b = document.createElement('button');
    b.setAttribute('aria-label', 'slide ' + (i + 1));
    if (i === 0) b.classList.add('on');
    b.onclick = () => go(i);
    dotsWrap.appendChild(b);
  });
  const dots = [...dotsWrap.children];

  function go(i) {
    cur = (i + slides.length) % slides.length;
    slides.forEach((s, k) => s.classList.toggle('on', k === cur));
    dots.forEach((d, k) => d.classList.toggle('on', k === cur));
    restart();
  }
  function restart() { clearInterval(timer); timer = setInterval(() => go(cur + 1), 6500); }

  document.getElementById('prev').onclick = () => go(cur - 1);
  document.getElementById('next').onclick = () => go(cur + 1);
  addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') go(cur - 1);
    if (e.key === 'ArrowRight') go(cur + 1);
  });

  /* touch swipe */
  let x0 = null;
  hero.addEventListener('touchstart', e => x0 = e.touches[0].clientX, { passive: true });
  hero.addEventListener('touchend', e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 46) go(cur + (dx < 0 ? 1 : -1));
    x0 = null;
  }, { passive: true });

  restart();
})();

/* ---------- slide 4 : gallery thumbs ---------- */
(function () {
  const thumbs = document.getElementById('thumbs');
  const main = document.getElementById('galMain');
  if (!thumbs || !main) return;
  thumbs.addEventListener('click', e => {
    const btn = e.target.closest('button'); if (!btn) return;
    thumbs.querySelectorAll('button').forEach(b => b.classList.remove('sel'));
    btn.classList.add('sel');
    main.style.opacity = '0';
    setTimeout(() => {
      main.src = btn.dataset.src;
      main.onload = () => main.style.opacity = '1';
    }, 160);
  });
  main.style.transition = 'opacity .4s';
})();

/* ---------- slide 4 : hero prompt -> studio ---------- */
(function () {
  const form = document.getElementById('heroPromptForm');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const q = document.getElementById('heroPrompt').value.trim();
    try { sessionStorage.setItem('nfx_prompt', q); } catch (_) {}
    location.href = 'playground.html' + (q ? '?q=' + encodeURIComponent(q) : '');
  });
})();
