import io

p = 'css/platform.css'
s = io.open(p, encoding='utf-8').read()

# 1. content dãn rộng như Agnes
s = s.replace('.plat .plat-main{flex:1;padding:34px clamp(22px,4vw,56px);max-width:1060px}',
              '.plat .plat-main{flex:1;padding:34px clamp(22px,4vw,56px);max-width:none}')
s = s.replace('.plat .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin:18px 0}',
              '.plat .stats{display:grid;grid-template-columns:repeat(5,1fr);gap:18px;margin:18px 0}')
s = s.replace('.plat .plan-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:16px 0}',
              '.plat .plan-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin:16px 0}')

# 2. nút gọn hơn
s = s.replace('.plat .btn-dark{display:inline-flex;align-items:center;gap:7px;padding:11px 22px;border-radius:999px;background:#0c1014;color:#fff;font-size:14px;font-weight:600;border:0;cursor:pointer;text-decoration:none}',
              '.plat .btn-dark{display:inline-flex;align-items:center;gap:7px;padding:9px 20px;border-radius:999px;background:#0c1014;color:#fff;font-size:13.5px;font-weight:600;border:0;cursor:pointer;text-decoration:none}')
s = s.replace('.plat .btn-light{display:inline-flex;align-items:center;gap:7px;padding:11px 22px;border-radius:999px;background:#fff;color:#14181d;font-size:14px;font-weight:600;border:1px solid #dfe4ea;cursor:pointer;text-decoration:none}',
              '.plat .btn-light{display:inline-flex;align-items:center;gap:7px;padding:9px 20px;border-radius:999px;background:#fff;color:#14181d;font-size:13.5px;font-weight:600;border:1px solid #dfe4ea;cursor:pointer;text-decoration:none}')

# 3. pills + QR đẹp hơn
s = s.replace('.plat .side-widgets .pill-row{display:flex;gap:8px;margin-bottom:14px}',
              '.plat .side-widgets .pill-row{display:flex;gap:9px;margin-bottom:16px;justify-content:center}')
s = s.replace('.plat .pill-connect{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:9px 6px;border-radius:999px;background:#f5722a;color:#fff;font-size:12.5px;font-weight:600;border:0;cursor:pointer;text-decoration:none}',
              '.plat .pill-connect{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:10px 8px;border-radius:999px;background:linear-gradient(135deg,#f5722a,#f5822a);color:#fff;font-size:12.5px;font-weight:600;border:0;cursor:pointer;text-decoration:none;white-space:nowrap;box-shadow:0 4px 14px rgba(245,114,42,.35)}')
s = s.replace('.plat .pill-gh{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:9px 6px;border-radius:999px;background:#0c1014;color:#fff;font-size:12.5px;font-weight:600;border:0;cursor:pointer;text-decoration:none}',
              '.plat .pill-gh{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:10px 8px;border-radius:999px;background:#0c1014;color:#fff;font-size:12.5px;font-weight:600;border:0;cursor:pointer;text-decoration:none;white-space:nowrap}')
s = s.replace('.plat .qr-item .qr{width:64px;height:64px;border:1px solid #cfe8cf;border-radius:8px;padding:5px;background:#fff;margin:0 auto 5px}',
              '.plat .qr-item .qr{width:76px;height:76px;border:1px solid #cfe8cf;border-radius:10px;padding:6px;background:#fff;margin:0 auto 6px;display:grid;place-items:center;box-shadow:0 2px 8px rgba(0,0,0,.05)}')
s = s.replace('.plat .qr-item{text-align:center;font-size:11px;color:#5c6975;text-decoration:none}',
              '.plat .qr-item{text-align:center;font-size:11.5px;color:#5c6975;text-decoration:none;font-weight:500}')
s += '''
/* recharge modal */
.rc-backdrop{position:fixed;inset:0;z-index:600;background:rgba(10,14,18,.5);display:grid;place-items:center;opacity:0;visibility:hidden;transition:.25s}
.rc-backdrop.on{opacity:1;visibility:visible}
.rc-modal{width:min(720px,94vw);max-height:90vh;overflow:auto;background:#fff;border-radius:14px;padding:24px 28px;box-shadow:0 30px 90px rgba(0,0,0,.3);transform:translateY(14px);transition:.25s;position:relative}
.rc-backdrop.on .rc-modal{transform:none}
.rc-modal .rc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.rc-modal .rc-head b{font-size:17px}
.rc-modal .rc-close{border:0;background:none;font-size:16px;cursor:pointer;color:#5c6975}
.rc-reminder{background:#f3f7fd;border:1px solid #dce8f7;border-radius:10px;padding:14px 18px;font-size:13px;color:#3c454f;margin-bottom:18px}
.rc-reminder b{display:block;margin-bottom:6px;color:#14181d}
.rc-reminder ol{margin:0;padding-left:18px;display:grid;gap:5px}
.rc-reminder a{color:#0c6bd6}
.rc-modal label.rc-lbl{display:block;font-size:14px;font-weight:600;margin-bottom:8px}
.rc-modal input[type=text]{width:100%;padding:12px 14px;border-radius:9px;border:1px solid #dfe4ea;font-size:14px;outline:0;box-sizing:border-box}
.rc-modal input[type=text]:focus{border-color:#14181d}
.rc-agree{display:flex;align-items:center;gap:8px;font-size:13px;color:#3c454f;margin:14px 0 20px}
.rc-btns{display:flex;justify-content:flex-end;gap:12px}
.rc-btns .rc-cancel{padding:10px 24px;border-radius:999px;border:1px solid #dfe4ea;background:#fff;font-size:14px;cursor:pointer}
.rc-btns .rc-confirm{padding:10px 24px;border-radius:999px;border:0;background:#c9cfd6;color:#fff;font-size:14px;font-weight:600;cursor:default}
.rc-btns .rc-confirm.ok{background:#0c1014}
/* live chat widget */
.lc-panel{position:fixed;bottom:86px;right:26px;z-index:120;width:340px;height:440px;background:#fff;border-radius:16px;box-shadow:0 24px 80px rgba(0,0,0,.28);display:none;flex-direction:column;overflow:hidden}
.lc-panel.on{display:flex}
.lc-head{background:#0c1014;color:#fff;padding:15px 18px;font-weight:600;font-size:14.5px;display:flex;align-items:center;gap:9px}
.lc-head .st{width:8px;height:8px;border-radius:50%;background:#25e39a}
.lc-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;background:#f7f9fa}
.lc-msg{max-width:78%;padding:10px 13px;border-radius:12px;font-size:13.5px;line-height:1.5}
.lc-msg.bot{background:#eceff3;color:#14181d;border-bottom-left-radius:4px;align-self:flex-start}
.lc-msg.me{background:#0c1014;color:#fff;border-bottom-right-radius:4px;align-self:flex-end}
.lc-input{display:flex;border-top:1px solid #e8ecf0}
.lc-input input{flex:1;border:0;outline:0;padding:13px 15px;font-size:13.5px}
.lc-input button{border:0;background:none;padding:0 16px;cursor:pointer;color:#0c1014}
.lc-input button:hover{color:#25e39a}
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('platform.css ok')
