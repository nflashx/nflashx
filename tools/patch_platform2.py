import io

p = 'platform.html'
s = io.open(p, encoding='utf-8').read()

def replace_entry(s, marker, new_text):
    i = s.find(marker)
    assert i > -1, marker + ' not found'
    j = s.find('\n  },', i)
    assert j > -1, 'end marker not found for ' + marker
    return s[:i] + new_text + s[j + len('\n  },') + 1:]

# ---- api-keys (Agnes style: description + create + table + enterprise) ----
new_api = '''  'api-keys': {
    title: 'API Keys',
    render(u) {
      const masked = u.api_key ? u.api_key.slice(0,8) + '\\u2022'.repeat(8) + u.api_key.slice(-4) : '\\u2014';
      const created = new Date((u.created || Date.now()/1000)*1000).toISOString().slice(0,10);
      return `
      <h1>API Keys</h1>
      <p class="desc">Do not share your API key with others, or expose it in the browser or other client-side code.</p>
      <p class="desc">1. Create a secret key; 2. Connect to NFlashX omnimodal free models; 3. Start exploring.</p>
      <div class="btn-row" style="justify-content:space-between;align-items:center;margin-bottom:0">
        <button class="btn-dark sm" id="createKey">Create new secret key</button>
        <a class="linklike" href="docs.html#quickstart" style="text-decoration:none">Connect Coding Tools &#8599;</a>
      </div>
      <table class="apitable">
        <thead><tr><th style="width:18%">Name</th><th style="width:24%">Secret Key</th><th style="width:22%">Created time(UTC)</th><th style="width:22%">Last used(UTC)</th><th>Operations</th></tr></thead>
        <tbody id="keyRows">
          <tr>
            <td><b style="font-weight:600;color:#14181d">Default key</b></td>
            <td class="mono" id="maskCell">${masked}</td>
            <td>${created} UTC</td>
            <td>Never</td>
            <td><span class="linklike" id="delKey" style="font-size:13px">Delete</span></td>
          </tr>
        </tbody>
      </table>
      <h2>Enterprise Keys</h2>
      <p class="desc">Do not share your API key with others, or expose it in the browser or other client-side code.</p>
      <p class="desc">After completing Enterprise Verification, you can create enterprise API keys. Enterprise API keys have 2&times; the RPM limit of free personal user keys.</p>
      <button class="btn-dark sm">Create new secret key</button>
      <table class="apitable">
        <thead><tr><th style="width:18%">Name</th><th style="width:24%">Secret Key</th><th style="width:22%">Created time(UTC)</th><th style="width:22%">Last used(UTC)</th><th>Operations</th></tr></thead>
        <tbody><tr><td colspan="5"><div class="no-data">No data</div></td></tr></tbody>
      </table>`;
    },
    after() {
      let show = false;
      const cell = $('#maskCell');
      const draw = () => cell.textContent = show ? sess.apiKey : sess.apiKey.slice(0,8) + '\\u2022'.repeat(8) + sess.apiKey.slice(-4);
      cell.onclick = () => { show = !show; draw(); };
      cell.style.cursor = 'pointer';
      $('#delKey').onclick = () => alert('Key deletion is disabled in this demo.');
      $('#createKey').onclick = () => alert('A project already has a default key. Delete it first to create a new one. Demo mode.');
    }
  },'''
s = replace_entry(s, "  'api-keys': {", new_api)

# ---- usage (Agnes style: 5 stat cards + Activity heatmap + Usage Trend) ----
new_usage = '''  usage: {
    title: 'Usage',
    render(u) {
      const cells = Array.from({length: 53*7}, (_,i) => '<div class="heat-cell"></div>').join('');
      const months = ['Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov'].map(m=>'<span>'+m+'</span>').join('');
      const dots = [60,168,276,384,492,600,690].map(x=>'<circle cx="'+x+'" cy="180" r="3.5"/>').join('');
      return `
      <h1>Usage <span style="color:#b6bfc9;font-size:14px">ⓘ</span></h1>
      <div class="stats">
        <div class="stat"><div class="n">0 <span style="font-size:14px;font-weight:600">Token</span></div><div class="l">Total Tokens</div></div>
        <div class="stat"><div class="n">0</div><div class="l">Total Images</div></div>
        <div class="stat"><div class="n">0</div><div class="l">Total Video Seconds</div></div>
        <div class="stat"><div class="n">0</div><div class="l">Requests</div></div>
        <div class="stat"><div class="n">0</div><div class="l">Active Days</div></div>
      </div>
      <div class="heat-wrap">
        <div class="heat-head"><span>Activity</span><span style="font-weight:400;color:#8a949f;font-size:12px">2025-11-07 - 2026-11-06</span></div>
        <div style="display:flex;align-items:center;gap:10px;margin-top:12px">
          <span style="font-size:13px;font-weight:600">Past 1 Year</span>
          <span class="heat-legend">Less <i></i><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i> More</span>
        </div>
        <p class="desc" style="margin-top:6px">0 active days</p>
        <div class="heat-months">${months}</div>
        <div class="heat-grid">${cells}</div>
      </div>
      <div class="heat-wrap">
        <div class="heat-head"><span>Usage Trend</span></div>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin:14px 0">
          <span class="seg"><button>Today</button><button class="on">Last 7 Days</button><button>Last 30 Days</button><button>This Month</button><button>Custom</button></span>
          <span class="seg"><button class="on">Requests</button><button>Token Usage</button><button>Image Pics</button><button>Video Seconds</button></span>
        </div>
        <div class="date-range">Start date <span>→</span> End date 📅</div>
        <svg viewBox="0 0 700 190" style="width:100%;height:200px;margin-top:10px">
          <g stroke="#eef1f4"><line x1="40" y1="20" x2="690" y2="20"/><line x1="40" y1="60" x2="690" y2="60"/><line x1="40" y1="100" x2="690" y2="100"/><line x1="40" y1="140" x2="690" y2="140"/><line x1="40" y1="180" x2="690" y2="180"/></g>
          <g fill="#8a949f" font-size="10"><text x="10" y="24">1.2</text><text x="10" y="64">0.9</text><text x="10" y="104">0.6</text><text x="10" y="144">0.3</text><text x="16" y="184">0</text></g>
          <polyline points="60,180 168,180 276,180 384,180 492,180 600,180 690,180" fill="none" stroke="#14181d" stroke-width="1.5"/>
          <g fill="#fff" stroke="#14181d">${dots}</g>
          <g fill="#8a949f" font-size="10"><text x="45" y="188">10-31</text><text x="153" y="188">11-1</text><text x="261" y="188">11-2</text><text x="369" y="188">11-3</text><text x="477" y="188">11-4</text><text x="585" y="188">11-5</text></g>
        </svg>
      </div>`;
    },
    after() {
      document.querySelectorAll('.seg').forEach(seg => seg.querySelectorAll('button').forEach(b => b.onclick = () => { seg.querySelectorAll('button').forEach(x => x.classList.remove('on')); b.classList.add('on'); }));
    }
  },'''
s = replace_entry(s, '  usage: {', new_usage)

# ---- balance (Agnes style) ----
new_balance = '''  balance: {
    title: 'Balance',
    render(u) {
      return `
      <h1>Balance <span style="color:#b6bfc9;font-size:14px">ⓘ</span></h1>
      <p class="desc" style="margin-top:14px">Effective balance</p>
      <div class="bal-big">$ 0.000000</div>
      <div class="bal-box">
        <div class="b"><b>Current balance</b><span>$0.000000</span></div>
        <div class="b"><b>Voucher balance</b><span>$0.000000</span></div>
      </div>
      <div class="btn-row">
        <button class="btn-dark sm">Recharge</button>
        <button class="btn-light sm">Support Bank Transfer</button>
        <button class="btn-light sm">View Invoices</button>
      </div>
      <div class="sec">
        <h2 style="margin-top:0">Payment History</h2>
        <div class="date-range" style="float:right;margin-top:-46px">Start date <span>→</span> End date 📅</div>
        <div class="doc-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><path d="M14 2v6h6M12 18v-6M9 15h6"/></svg></div>
        <div class="no-data">No records available</div>
      </div>`;
    }
  },'''
s = replace_entry(s, '  balance: {', new_balance)

# ---- agent plan (empty for now) ----
new_ap = '''  'agent-plan': {
    title: 'Agent Plan',
    render() {
      return `
      <h1>Agent Plan</h1>
      <p class="desc">Shared quota across text, image, and video — for teams and heavy agent workflows.</p>
      <div class="empty">Agent Plan is coming soon. Pricing will be announced at launch.</div>`;
    }
  },'''
s = replace_entry(s, "  'agent-plan': {", new_ap)

io.open(p, 'w', encoding='utf-8').write(s)
print('platform.html pages rewritten OK')
