import io, re

# ---------- 1. styles.css: marquee seamless + footer margin + platform refinements ----------
p = 'css/styles.css'
s = io.open(p, encoding='utf-8').read()
s = s.replace('.ab-track{display:flex;gap:22px;width:max-content;animation:abmarq 60s linear infinite}',
              '.ab-track{display:flex;width:max-content;animation:abmarq 60s linear infinite}')
s = s.replace('.ab-track .lb-card{width:300px;flex:none;margin:0;padding:14px 14px 10px;',
              '.ab-track .lb-card{width:300px;flex:none;margin:0 22px 0 0;padding:14px 14px 10px;')
s = s.replace('.ab-foot{position:absolute;bottom:26px;color:#5c6975;font-size:12px}',
              '.ab-foot{position:absolute;bottom:22px;color:#5c6975;font-size:12px}')
if '.plat .btn-dark.sm' not in s:
    s += '''
/* platform refinements */
.plat .btn-dark.sm{padding:9px 18px;font-size:13.5px}
.plat .btn-light.sm{padding:9px 18px;font-size:13.5px}
.plat table.apitable{width:100%;border-collapse:collapse;font-size:13.5px;margin:14px 0 8px}
.plat table.apitable th{text-align:left;font-weight:600;color:#3c454f;padding:12px 14px;background:#f7f9fa}
.plat table.apitable td{padding:18px 14px;color:#3c454f;border-bottom:1px solid #eef1f4}
.plat table.apitable .mono{font-family:var(--font-mono);font-size:12.5px;color:#5c6975}
.plat .no-data{padding:38px;text-align:center;color:#b6bfc9;background:#fbfcfd}
.plat .heat-wrap{border:1px solid #e8ecf0;border-radius:14px;padding:20px;margin:16px 0}
.plat .heat-head{display:flex;justify-content:space-between;align-items:center;font-size:14px;font-weight:600}
.plat .heat-legend{display:flex;align-items:center;gap:5px;font-size:11.5px;color:#8a949f}
.plat .heat-legend i{width:10px;height:10px;border-radius:2px;display:inline-block;background:#eef1f4}
.plat .heat-legend i.on{background:#25c93f}
.plat .heat-grid{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,11px);gap:3px;margin:14px 0 6px;overflow-x:auto}
.plat .heat-cell{width:11px;height:11px;border-radius:2.5px;background:#eef1f4}
.plat .heat-months{display:flex;justify-content:space-between;font-size:10.5px;color:#8a949f;padding-left:34px}
.plat .seg{display:inline-flex;background:#f3f5f8;border-radius:9px;padding:3px;gap:2px}
.plat .seg button{border:0;background:none;padding:7px 13px;border-radius:7px;font-size:12.5px;color:#3c454f;cursor:pointer}
.plat .seg button.on{background:#fff;box-shadow:0 1px 5px rgba(0,0,0,.14);font-weight:600}
.plat .bal-big{font-size:40px;font-weight:700;margin:4px 0 20px}
.plat .bal-box{display:inline-flex;background:#f3f5f8;border-radius:12px;padding:6px;margin-bottom:8px}
.plat .bal-box .b{padding:10px 30px;text-align:center}
.plat .bal-box .b+.b{border-left:1px solid #e3e7ec}
.plat .bal-box b{display:block;font-size:13.5px;font-weight:600}
.plat .bal-box span{font-size:13px;color:#5c6975}
.plat .date-range{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:#8a949f;border:1px solid #e3e7ec;border-radius:9px;padding:8px 14px}
.plat .doc-ic{margin:30px auto 8px;width:70px;height:70px;border-radius:12px;background:#eef1f4;display:grid;place-items:center;color:#b6bfc9}
.plat .doc-ic svg{width:34px;height:34px}
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('styles.css ok')

# ---------- 2. login.html: duplicate track ----------
p = 'login.html'
s = io.open(p, encoding='utf-8').read()
if 'duplicate marquee track' not in s:
    dup = ('/* duplicate marquee track for a seamless -50% loop */\n'
           'const tr = document.querySelector(\'.ab-track\');\n'
           "if (tr) tr.innerHTML += tr.innerHTML;\n\n")
    s = s.replace('/* password eye toggles */', dup + '/* password eye toggles */')
    io.open(p, 'w', encoding='utf-8').write(s)
print('login.html ok')

# ---------- 3. platform.html: rewrite pages ----------
p = 'platform.html'
s = io.open(p, encoding='utf-8').read()

s = s.replace('<a class="btn-dark" href="#api-keys">Get Your Key</a>',
              '<a class="btn-dark sm" href="#api-keys">Get Your Key</a>')

old_api = re.search(r"    'api-keys': \{\n      title: 'API Keys',\n      render\(u\) \{.*?\n    \},", s, re.S)
assert old_api, 'api-keys page not found'
new_api = r'''    'api-keys': {
    title: 'API Keys',
    render(u) {
      const masked = u.api_key ? u.api_key.slice(0,8) + '\u2022'.repeat(8) + u.api_key.slice(-4) : '\u2014';
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
      const draw = () => cell.textContent = show ? sess.apiKey : sess.apiKey.slice(0,8) + '\u2022'.repeat(8) + sess.apiKey.slice(-4);
      cell.onclick = () => { show = !show; draw(); };
      cell.style.cursor = 'pointer';
      $('#delKey').onclick = () => alert('Key deletion is disabled in this demo.');
      $('#createKey').onclick = () => alert('A project already has a default key. Delete it first to create a new one \u2014 demo mode.');
    }
  },'''
s = s[:old_api.start()] + new_api + s[old_api.end():]

old_u = re.search(r"    usage: \{\n      title: 'Usage',\n      render\(u\) \{.*?\n    \},", s, re.S)
assert old_u, 'usage page not found'
heat_cells = '\u0037'.join([''])
cells_js = "Array.from({length: 53*7}, (_,i) => '<div class=\"heat-cell\"></div>').join('')"
months_js = "['Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov'].map(m=>'<span>'+m+'</span>').join('')"
dots_js = "[60,168,276,384,492,600,690].map(x=>'<circle cx=\"'+x+'\" cy=\"180\" r=\"3.5\"/>').join('')"
new_u = ("    usage: {\n    title: 'Usage',\n    render(u) {\n      const cells = " + cells_js + ";\n"
         "      const months = " + months_js + ";\n      return `\n"
         "      <h1>Usage <span style=\"color:#b6bfc9;font-size:14px\">\u24d8</span></h1>\n"
         "      <div class=\"stats\">\n"
         "        <div class=\"stat\"><div class=\"n\">0 <span style=\"font-size:14px;font-weight:600\">Token</span></div><div class=\"l\">Total Tokens</div></div>\n"
         "        <div class=\"stat\"><div class=\"n\">0</div><div class=\"l\">Total Images</div></div>\n"
         "        <div class=\"stat\"><div class=\"n\">0</div><div class=\"l\">Total Video Seconds</div></div>\n"
         "        <div class=\"stat\"><div class=\"n\">0</div><div class=\"l\">Requests</div></div>\n"
         "        <div class=\"stat\"><div class=\"n\">0</div><div class=\"l\">Active Days</div></div>\n"
         "      </div>\n"
         "      <div class=\"heat-wrap\">\n"
         "        <div class=\"heat-head\"><span>Activity</span><span style=\"font-weight:400;color:#8a949f;font-size:12px\">2025-11-07 - 2026-11-06</span></div>\n"
         "        <div style=\"display:flex;align-items:center;gap:10px;margin-top:12px\">\n"
         "          <span style=\"font-size:13px;font-weight:600\">Past 1 Year</span>\n"
         "          <span class=\"heat-legend\">Less <i></i><i class=\"on\"></i><i class=\"on\"></i><i class=\"on\"></i><i class=\"on\"></i> More</span>\n"
         "        </div>\n"
         "        <p class=\"desc\" style=\"margin-top:6px\">0 active days</p>\n"
         "        <div class=\"heat-months\">${months}</div>\n"
         "        <div class=\"heat-grid\">${cells}</div>\n"
         "      </div>\n"
         "      <div class=\"heat-wrap\">\n"
         "        <div class=\"heat-head\"><span>Usage Trend</span></div>\n"
         "        <div style=\"display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin:14px 0\">\n"
         "          <span class=\"seg\"><button>Today</button><button class=\"on\">Last 7 Days</button><button>Last 30 Days</button><button>This Month</button><button>Custom</button></span>\n"
         "          <span class=\"seg\"><button class=\"on\">Requests</button><button>Token Usage</button><button>Image Pics</button><button>Video Seconds</button></span>\n"
         "        </div>\n"
         "        <div class=\"date-range\">Start date <span>\u2192</span> End date \ud83d\udcc5</div>\n"
         "        <svg viewBox=\"0 0 700 190\" style=\"width:100%;height:200px;margin-top:10px\">\n"
         "          <g stroke=\"#eef1f4\"><line x1=\"40\" y1=\"20\" x2=\"690\" y2=\"20\"/><line x1=\"40\" y1=\"60\" x2=\"690\" y2=\"60\"/><line x1=\"40\" y1=\"100\" x2=\"690\" y2=\"100\"/><line x1=\"40\" y1=\"140\" x2=\"690\" y2=\"140\"/><line x1=\"40\" y1=\"180\" x2=\"690\" y2=\"180\"/></g>\n"
         "          <g fill=\"#8a949f\" font-size=\"10\"><text x=\"10\" y=\"24\">1.2</text><text x=\"10\" y=\"64\">0.9</text><text x=\"10\" y=\"104\">0.6</text><text x=\"10\" y=\"144\">0.3</text><text x=\"16\" y=\"184\">0</text></g>\n"
         "          <polyline points=\"60,180 168,180 276,180 384,180 492,180 600,180 690,180\" fill=\"none\" stroke=\"#14181d\" stroke-width=\"1.5\"/>\n"
         "          <g fill=\"#fff\" stroke=\"#14181d\">${dots}</g>\n"
         "          <g fill=\"#8a949f\" font-size=\"10\"><text x=\"45\" y=\"188\">10-31</text><text x=\"153\" y=\"188\">11-1</text><text x=\"261\" y=\"188\">11-2</text><text x=\"369\" y=\"188\">11-3</text><text x=\"477\" y=\"188\">11-4</text><text x=\"585\" y=\"188\">11-5</text></g>\n"
         "        </svg>\n"
         "      </div>`;\n"
         "    },\n"
         "    after() {\n"
         "      document.querySelectorAll('.seg').forEach(seg => seg.querySelectorAll('button').forEach(b => b.onclick = () => { seg.querySelectorAll('button').forEach(x => x.classList.remove('on')); b.classList.add('on'); }));\n"
         "    }\n"
         "  },")
s = s[:old_u.start()] + new_u + s[old_u.end():]

old_b = re.search(r"    balance: \{\n      title: 'Balance',\n      render\(u\) \{.*?\n    \},", s, re.S)
assert old_b, 'balance page not found'
new_b = r'''    balance: {
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
s = s[:old_b.start()] + new_b + s[old_b.end():]

old_ap = re.search(r"    'agent-plan': \{\n      title: 'Agent Plan',\n      render\(\) \{.*?\n    \},", s, re.S)
assert old_ap, 'agent-plan not found'
new_ap = r'''    'agent-plan': {
    title: 'Agent Plan',
    render() {
      return `
      <h1>Agent Plan</h1>
      <p class="desc">Shared quota across text, image, and video — for teams and heavy agent workflows.</p>
      <div class="empty">Agent Plan is coming soon. Pricing will be announced at launch.</div>`;
    }
  },'''
s = s[:old_ap.start()] + new_ap + s[old_ap.end():]

io.open(p, 'w', encoding='utf-8').write(s)
print('platform.html pages rewritten OK')
