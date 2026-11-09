import io, re

p = 'platform.html'
s = io.open(p, encoding='utf-8').read()

# ---------- 1. sidebar: bỏ Token Plan khỏi menu ----------
s = s.replace('        <li><a href="#token-plan">Token Plan</a></li>\n', '')

# ---------- 2. profile: Recharge mở popup ----------
s = s.replace('<a class="btn-light" href="#balance">Recharge</a>',
              '<a class="btn-light" href="#" data-recharge>Recharge</a>')

# ---------- 3. balance: Recharge mở popup ----------
s = s.replace('<button class="btn-dark sm">Recharge</button>',
              '<button class="btn-dark sm" data-recharge>Recharge</button>')

# ---------- 4. token plan: xoá nội dung, để trống tạm ----------
old_tp = re.search(r"  'token-plan': \{\n    title: 'Token Plan',\n    render\(\w*\) \{.*?\n    \},", s, re.S)
assert old_tp, 'token-plan not found'
new_tp = '''  'token-plan': {
    title: 'Token Plan',
    render() {
      return `
      <h1>Token Plan</h1>
      <p class="desc">Starter quotas included with every account.</p>
      <div class="empty">Token Plan details are coming soon.</div>`;
    }
  },'''
s = s[:old_tp.start()] + new_tp + s[old_tp.end():]

# ---------- 5. QR generator + recharge modal + live chat JS ----------
s = s.replace('</body>', '''<div class="rc-backdrop" id="rcBackdrop">
  <div class="rc-modal">
    <div class="rc-head"><b>Recharge</b><button class="rc-close" aria-label="Close">✕</button></div>
    <div class="rc-reminder">
      <b>Reminder:</b>
      <ol>
        <li>Please ensure that your account has sufficient funds for the transaction.</li>
        <li>If you encounter transaction issues during the recharge process, please check with the relevant third-party payment platform for confirmation.</li>
        <li>After completing the recharge, you can go to the <a href="#billing">Payment History</a> to view your transaction records and account balance.</li>
        <li>If you want to top up using bank transfer, please refer to the <a href="#">Bank Transfer Guide</a>.</li>
        <li>Please note that sales tax may be applied to the charge based on your location.</li>
      </ol>
    </div>
    <label class="rc-lbl">Recharge Amount</label>
    <input type="text" id="rcAmount" placeholder="Single recharge amount ranges from $10 to $9999">
    <label class="rc-agree"><input type="checkbox" id="rcAgree"> I have read and agree to the <a href="#">Privacy Policy</a> and <a href="#">Terms and Conditions</a>.</label>
    <div class="rc-btns">
      <button class="rc-cancel" id="rcCancel">Cancel</button>
      <button class="rc-confirm" id="rcConfirm" disabled>Confirm</button>
    </div>
  </div>
</div>

<div class="lc-panel" id="lcPanel">
  <div class="lc-head"><span class="st"></span> NFlashX Live Chat</div>
  <div class="lc-msgs" id="lcMsgs">
    <div class="lc-msg bot">👋 Hi there! How can we help you today?</div>
  </div>
  <div class="lc-input">
    <input id="lcInput" type="text" placeholder="Type a message…">
    <button id="lcSend" aria-label="Send"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg></button>
  </div>
</div>

<script>
/* ---------- QR placeholders (fake QR look, deterministic) ---------- */
(function () {
  document.querySelectorAll('.qr-item .qr').forEach((box, qi) => {
    const n = 17, cell = 4, size = n * cell;
    let rects = '';
    const finder = (x, y) => {
      rects += '<rect x="' + x + '" y="' + y + '" width="' + 7*cell + '" height="' + 7*cell + '" fill="none" stroke="CUR" stroke-width="' + cell + '"/>';
      rects += '<rect x="' + (x+2*cell) + '" y="' + (y+2*cell) + '" width="' + 3*cell + '" height="' + 3*cell + '" fill="CUR"/>';
    };
    let seed = 7 + qi * 13;
    const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
      const inFinder = (x < 8 && y < 8) || (x >= n-8 && y < 8) || (x < 8 && y >= n-8);
      if (inFinder) continue;
      if (rnd() > 0.52) rects += '<rect x="' + x*cell + '" y="' + y*cell + '" width="' + cell + '" height="' + cell + '" fill="CUR"/>';
    }
    const color = box.closest('.qr-item').classList.contains('discord') ? '#5865f2' : '#2aae67';
    rects = rects.replace(/CUR/g, color);
    finder(0, 0); finder(size - 7*cell, 0); finder(0, size - 7*cell);
    box.innerHTML = '<svg viewBox="0 0 ' + size + ' ' + size + '" width="100%" height="100%">' + rects + '</svg>';
  });
})();

/* ---------- recharge modal ---------- */
(function () {
  const bd = document.getElementById('rcBackdrop');
  document.querySelectorAll('[data-recharge]').forEach(b => b.addEventListener('click', e => {
    e.preventDefault();
    bd.classList.add('on');
  }));
  bd.querySelector('.rc-close').onclick = () => bd.classList.remove('on');
  document.getElementById('rcCancel').onclick = () => bd.classList.remove('on');
  bd.addEventListener('click', e => { if (e.target === bd) bd.classList.remove('on'); });
  const amt = document.getElementById('rcAmount'), agree = document.getElementById('rcAgree'), ok = document.getElementById('rcConfirm');
  function check() {
    const v = parseFloat(amt.value);
    ok.classList.toggle('ok', agree.checked && v >= 10 && v <= 9999);
  }
  amt.addEventListener('input', check);
  agree.addEventListener('change', check);
  ok.onclick = () => {
    if (!ok.classList.contains('ok')) return;
    bd.classList.remove('on');
    alert('Recharge of $' + amt.value + ' — demo mode. Integrate your payment provider here.');
  };
})();

/* ---------- live chat widget ---------- */
(function () {
  const btn = document.querySelector('.live-chat'), panel = document.getElementById('lcPanel');
  btn.onclick = () => panel.classList.toggle('on');
  const msgs = document.getElementById('lcMsgs'), input = document.getElementById('lcInput');
  function send() {
    const t = input.value.trim(); if (!t) return;
    const me = document.createElement('div');
    me.className = 'lc-msg me'; me.textContent = t;
    msgs.appendChild(me); input.value = '';
    msgs.scrollTop = msgs.scrollHeight;
    setTimeout(() => {
      const b = document.createElement('div');
      b.className = 'lc-msg bot';
      b.textContent = 'Thanks for reaching out! Our team will reply shortly — meanwhile, check the Developer Docs for quick answers.';
      msgs.appendChild(b); msgs.scrollTop = msgs.scrollHeight;
    }, 900);
  }
  document.getElementById('lcSend').onclick = send;
  input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
})();
</script>
</body>''')

io.open(p, 'w', encoding='utf-8').write(s)
print('platform.html widgets + token-plan removed OK')
