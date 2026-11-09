import io

p = 'login.html'
s = io.open(p, encoding='utf-8').read()

# 1. nhân đôi track (seamless loop)
if 'abtr.innerHTML' not in s:
    dup = '''/* nhân đôi track - loop liền mạch */
const abtr = document.querySelector('.ab-track');
if (abtr) abtr.innerHTML += abtr.innerHTML;

'''
    s = s.replace('/* password eye toggles */', dup + '/* password eye toggles */')

io.open(p, 'w', encoding='utf-8').write(s)
print('login.html dup OK')

# ---------- 2. styles.css: bar cao hơn + chữ vừa + khoảng thở ----------
p = 'css/styles.css'
s = io.open(p, encoding='utf-8').read()
s = s.replace('.ab-track .lb-bars{height:150px;gap:7px}', '.ab-track .lb-bars{height:212px;gap:7px}')
s = s.replace('.ab-track .lb-bar .bar{width:16px;height:calc(var(--hp)*0.55);background:linear-gradient(180deg,rgba(160,230,205,.8),rgba(70,160,135,.4) 80%);box-shadow:0 0 16px rgba(80,200,160,.4),inset 0 0 6px rgba(255,255,255,.18)}',
              '.ab-track .lb-bar .bar{width:16px;height:calc(var(--hp)*0.85);background:linear-gradient(180deg,rgba(160,230,205,.8),rgba(70,160,135,.4) 80%);box-shadow:0 0 16px rgba(80,200,160,.4),inset 0 0 6px rgba(255,255,255,.18)}')
s = s.replace('.ab-track .lb-bar .vname{font-size:6px;top:5px}', '.ab-track .lb-bar .vname{font-size:6px;top:6px}')
s = s.replace('.ab-track .lb-sub{font-size:9.5px;margin:2px 0 10px;min-height:0}', '.ab-track .lb-sub{font-size:9.5px;margin:2px 0 18px;min-height:0}')
s = s.replace('.ab-mview{position:relative;z-index:1;width:100%;overflow:hidden;padding:10px 0 64px;', '.ab-mview{position:relative;z-index:1;width:100%;overflow:hidden;padding:6px 0 52px;')
s = s.replace('.ab-foot{position:absolute;bottom:20px;color:#7c8894;font-size:12px}', '.ab-foot{position:absolute;bottom:14px;color:#7c8894;font-size:12px}')
io.open(p, 'w', encoding='utf-8').write(s)
print('styles.css OK')
