"""
NFlashX server — static files + API proxy + REAL auth backend + self-serve SaaS.

Run:  python server.py        (then open http://127.0.0.1:8600)

Auth features:
  • signup with email verification (real 6-digit code via SMTP; dev code printed when mail is not configured)
  • disposable / trash email domains blocked, "+" aliases blocked
  • per-IP signup rate limit (auto IP ban on abuse), account ban flag
  • login with failed-attempt lock, sessions persisted, multiple API keys per user
  • real Google / GitHub OAuth (needs data/oauth_config.json — see AUTH-SETUP.md)
  • password reset + set/change password + account deletion (all real)
  • self-serve registration: POST /v1/auth/register {"email"} -> nfx- key immediately
  • per-key rate limiting + usage log (SQLite) powering the Admin Console
  • tier policy: free/pro caps + persona; Pro model id gated to pro-tier keys

Config files (created on demand under data/):
  data/db.json           users, sessions, pending codes, ip stats, bans, topups
  data/nflashx.db        SQLite: users(api keys, tier, usage) + usage_log
  data/mail_config.json  {"host","port","user","pass","from"}   (SMTP, e.g. Gmail app password)
  data/oauth_config.json {"google":{"client_id","client_secret"},"github":{...}}
"""
import hashlib
import ipaddress
import json
import os
import re
import secrets
import smtplib
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", 8600))
API_KEY = os.environ.get("AGNES_KEY", "")
UPSTREAM = "https://apihub.agnes-ai.com"
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
DB_PATH = os.path.join(DATA, "db.json")
SQLITE_PATH = os.path.join(DATA, "nflashx.db")

ROUTES = {
    "/api/chat": "/v1/chat/completions",
    "/api/images": "/v1/images/generations",
    "/api/videos": "/v1/videos",
}

MODEL_MAP = {
    "n-flashx-1.0-flash": "agnes-2.5-flash",      # developer API naming (spec /v1)
    "nflashx-1.0-pro": "agnes-2.5-flash",         # Pro = CÙNG engine agnes-2.5-flash, full power (TIER_POLICY pro); 3.0 để nguyên, chưa dùng
    "n-flashx-1.0-pro": "agnes-2.5-flash",
    "nflashx-vision-1.0-flash": "agnes-image-2.5-flash",   # flagship image (trùng id trang docs)
    "nflashx-vision-1.5": "agnes-image-2.5-flash",         # legacy alias (prefs cũ trong browser)
    "nflashx-vision-1.1": "agnes-image-2.1-flash",
    "nflashx-vision-1.0": "agnes-image-2.0-flash",
    "nflashx-motion-1.0": "agnes-video-2.5-flash",
    "nflashx-1.0-flash": "agnes-2.5-flash",
}
PRO_MODELS = {"nflashx-1.0-pro", "n-flashx-1.0-pro"}   # chỉ key tier 'pro' được gọi

# ---------------------------------------------------------------- database
def load_db():
    os.makedirs(DATA, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"users": {}, "sessions": {}, "pending": {}, "ip_signups": {},
                       "banned_ips": [], "failed_logins": {}}, f, indent=2)
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
    os.replace(tmp, DB_PATH)

DB = load_db()

def now(): return time.time()

# ------------------------------------------------- self-serve SQLite store
# users(id, email UNIQUE, api_key UNIQUE, tier, total_requests, last_request_time, last_ip, banned)
SQLITE_LOCK = threading.Lock()
SQLITE = None

def init_sqlite():
    global SQLITE
    os.makedirs(DATA, exist_ok=True)
    SQLITE = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    SQLITE.execute("""CREATE TABLE IF NOT EXISTS users(
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        email             TEXT UNIQUE,
        api_key           TEXT UNIQUE,
        tier              TEXT DEFAULT 'free',
        total_requests    INTEGER DEFAULT 0,
        last_request_time REAL DEFAULT 0,
        created           REAL
    )""")
    try:
        SQLITE.execute("ALTER TABLE users ADD COLUMN last_ip TEXT")
    except Exception:
        pass  # cot da ton tai
    try:
        SQLITE.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
    except Exception:
        pass  # cot da ton tai
    SQLITE.execute("""CREATE TABLE IF NOT EXISTS usage_log(
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        email     TEXT,
        api_key   TEXT,
        endpoint  TEXT,
        ip        TEXT,
        ts        REAL
    )""")
    SQLITE.commit()

def sql_user_by_key(key):
    with SQLITE_LOCK:
        row = SQLITE.execute(
            "SELECT id,email,api_key,tier,total_requests,last_request_time,COALESCE(banned,0) FROM users WHERE api_key=?",
            (key,)).fetchone()
    if not row:
        return None
    return {"id": row[0], "email": row[1], "api_key": row[2], "tier": row[3],
            "total_requests": row[4], "last_request_time": row[5], "banned": bool(row[6])}

def sql_user_by_email(email):
    with SQLITE_LOCK:
        row = SQLITE.execute(
            "SELECT id,email,api_key,tier,total_requests,last_request_time FROM users WHERE email=?",
            (email,)).fetchone()
    if not row:
        return None
    return {"id": row[0], "email": row[1], "api_key": row[2], "tier": row[3],
            "total_requests": row[4], "last_request_time": row[5]}

def sql_insert_user(email, api_key, tier="free"):
    with SQLITE_LOCK:
        SQLITE.execute(
            "INSERT INTO users(email,api_key,tier,total_requests,last_request_time,created) VALUES(?,?,?,0,0,?)",
            (email, api_key, tier, now()))
        SQLITE.commit()

def sql_touch_usage(user_id):
    # Update last_request_time AND increment total_requests on every successful request
    with SQLITE_LOCK:
        SQLITE.execute("UPDATE users SET total_requests=total_requests+1, last_request_time=? WHERE id=?",
                       (now(), user_id))
        SQLITE.commit()

def find_account_key_owner(key):
    # Bridge: key sinh ra từ tài khoản platform (db.json) vẫn dùng được — auto-sync sang SQLite
    for email, u in DB["users"].items():
        if u.get("api_key") == key:
            return email
        if any(k.get("key") == key for k in u.get("keys", [])):
            return email
    return None

def key_exists(key):
    """Kiểm tra key đã tồn tại GLOBALLY (mọi account, mọi kho) — chống trùng tuyệt đối."""
    for u in DB["users"].values():
        if u.get("api_key") == key:
            return True
        if any(k.get("key") == key for k in u.get("keys", [])):
            return True
    if SQLITE is not None:
        with SQLITE_LOCK:
            row = SQLITE.execute("SELECT 1 FROM users WHERE api_key=?", (key,)).fetchone()
        if row:
            return True
    return False

def gen_api_key(prefix="sk-nfx-"):
    """Sinh key mới crypto-secure (secrets), kiểm tra trùng toàn hệ thống trước khi trả.
    Mỗi account — mỗi key riêng, không trùng lặp giữa các account."""
    while True:
        k = prefix + secrets.token_hex(20)
        if not key_exists(k):
            return k

# Per-minute rate limiting: strict gap between requests (free = 1 rps = 60/min)
RATE_LIMITS = {"free": 1.0, "pro": 0.1}

def check_api_key(key, endpoint="", ip=""):
    """Verify Bearer key against SQLite, enforce tier rate limit, count usage.
    Raises AuthError(401/403/429). Returns the usage row."""
    if not key:
        raise AuthError(401, "Missing API key. Send header: Authorization: Bearer <your key>.")
    u = sql_user_by_key(key)
    if not u:
        email = find_account_key_owner(key)
        if email:
            owner = DB["users"].get(email) or {}
            sql_insert_user(email, key, "pro" if owner.get("plan") == "Pro" else "free")
            u = sql_user_by_key(key)
    if not u:
        raise AuthError(401, "Invalid API key.")
    if u.get("banned"):
        raise AuthError(403, "This API key has been banned for abuse.")
    owner = DB["users"].get(u["email"])
    if owner and owner.get("banned"):
        raise AuthError(403, "This account has been banned for abuse.")
    t = now()
    gap = RATE_LIMITS.get(u["tier"], 1.0)
    if u["last_request_time"] and (t - u["last_request_time"]) < gap:
        raise AuthError(429, f"Rate limit exceeded ({int(round(60/gap))} requests/minute on the "
                             f"{u['tier']} tier). Slow down or upgrade to Pro.")
    sql_touch_usage(u["id"])
    u["total_requests"] += 1
    # usage log (cho trang Admin: usage hom nay, IP, spam control)
    if SQLITE is not None:
        with SQLITE_LOCK:
            SQLITE.execute("INSERT INTO usage_log(email,api_key,endpoint,ip,ts) VALUES(?,?,?,?,?)",
                           (u["email"], key, endpoint, ip, t))
            if ip:
                SQLITE.execute("UPDATE users SET last_ip=? WHERE id=?", (ip, u["id"]))
            SQLITE.commit()
    return u

# ---------------------------------------------------------------- tier policy
# "Capability envelope": ban Free/Flash chay lite — con duong mo 100% suc manh
# khi ban Pro (chi can UPDATE users SET tier='pro' là unlock).
TIER_POLICY = {
    "free": {
        "max_output_tokens": 4096,  # du cho code + test hoan chinh (tester chu yeu thu code) — van 2x thap hon Pro
        "persona": ("You are NFlashX 1.0 Flash, a fast lightweight assistant. "
                    "Be direct and concise in prose — around 150 words for explanations. "
                    "When writing code, always complete the code fully; "
                    "skip deep multi-step reasoning and long examples."),
    },
    "pro": {
        "max_output_tokens": 8192,  # full power khi mo tier pro
        # persona DINH DANH ONLY — chi de khong lo brand upstream, khong gioi han output
        "persona": ("You are NFlashX 1.0 Pro, an AI model created by NFlashX. "
                    "Never claim, state, or imply that you were made by, belong to, or are "
                    "affiliated with any other company, product, or lab. If asked who you are, "
                    "say you are NFlashX 1.0 Pro by NFlashX. Apart from your identity, behave "
                    "exactly as your full capabilities allow."),
    },
}

def apply_tier_policy(body, tier):
    """Gioi han do manh theo tier: clamp max_tokens + persona lite cho free."""
    pol = TIER_POLICY.get(tier, TIER_POLICY["free"])
    if not isinstance(body, dict):
        return body
    msgs = body.get("messages")
    if pol["persona"] and isinstance(msgs, list):
        if msgs and msgs[0].get("role") == "system":
            msgs[0]["content"] = pol["persona"] + "\n" + str(msgs[0].get("content", ""))
        else:
            msgs.insert(0, {"role": "system", "content": pol["persona"]})
    cap = pol["max_output_tokens"]
    mt = body.get("max_tokens")
    body["max_tokens"] = min(int(mt), cap) if isinstance(mt, int) and mt > 0 else cap
    return body

# ------------------------------------------------- self-serve registration
def signup_cap_reached():
    """Launch window: cap the total number of accounts (0 = unlimited)."""
    cap = int(SETTINGS.get("signup_cap") or 0)
    return cap > 0 and len(DB["users"]) >= cap

def signup_cap_error():
    cap = int(SETTINGS.get("signup_cap") or 0)
    return AuthError(403, f"Launch limit reached: the first {cap} accounts are already taken. "
                          "Sign-up is closed for now — see you in the next wave.")

def do_register(body):
    """POST /v1/auth/register  {"email": "..."} → returns a fresh nfx- key immediately."""
    if signup_cap_reached():
        raise signup_cap_error()
    email = (body.get("email") or "").strip().lower()
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise AuthError(400, "Please provide a valid email address.")
    ok, why = mail_allowed(email)
    if not ok:
        raise AuthError(400, why)
    if sql_user_by_email(email):
        raise AuthError(409, "This email already has an API key. Check your account page.")
    if family_taken(email_family(email)):
        raise AuthError(409, "An account with this email (or a Gmail variant of it) already exists.")
    # Platform account đã tồn tại → dùng lại key sẵn có (không phát sinh key mới)
    owner = DB["users"].get(email)
    if owner:
        ensure_keys(owner)
        save_db(DB)
        if not sql_user_by_key(owner["api_key"]):
            sql_insert_user(email, owner["api_key"], "free")
        return {"ok": True, "email": email, "api_key": owner["api_key"], "tier": "free",
                "note": "existing platform account — same key"}
    api_key = gen_api_key("nfx-")   # secure key via secrets + global uniqueness check
    sql_insert_user(email, api_key, "free")
    return {"ok": True, "email": email, "api_key": api_key, "tier": "free"}

# ------------------------------------------------- session helpers (hang that)
def session_user(body):
    """Lấy user từ session token trong body. Raise nếu hết hạn/bị ban."""
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u or u.get("banned"):
        raise AuthError(403, "Account unavailable.")
    return u

def require_admin(body):
    u = session_user(body)
    if not u.get("admin"):
        raise AuthError(403, "Admin only.")
    return u

def do_set_password(body):
    u = session_user(body)
    pw = body.get("password") or ""
    if len(pw) < 6:
        raise AuthError(400, "Password must be at least 6 characters.")
    u["pass"] = hash_pass(pw)
    u["provider"] = "email"   # từ giờ login bằng password được
    save_db(DB)
    return {"ok": True}

def do_delete_account(body):
    u = session_user(body)
    if (body.get("confirm") or "").strip().upper() != "DELETE":
        raise AuthError(400, 'Type DELETE to confirm account removal.')
    email = u["email"]
    if u.get("admin") and sum(1 for x in DB["users"].values() if x.get("admin")) <= 1:
        raise AuthError(403, "Cannot delete the last admin account.")
    DB["users"].pop(email, None)
    for t in [t for t, s in DB["sessions"].items() if s["email"] == email]:
        DB["sessions"].pop(t, None)
    if SQLITE is not None:
        with SQLITE_LOCK:
            SQLITE.execute("DELETE FROM users WHERE email=?", (email,))
            SQLITE.commit()
    save_db(DB)
    return {"ok": True}

def do_reset_request(body, handler):
    ip = client_ip(handler)
    if ip_is_banned(DB, ip):
        raise AuthError(403, "This network is banned.")
    email = (body.get("email") or "").strip().lower()
    u = DB["users"].get(email)
    code = f"{secrets.randbelow(1000000):06d}"
    sent = False
    if u:
        sent = send_code_email(email, code)
        if not sent:
            print(f"[MAIL NOT CONFIGURED] password reset code for {email}: {code}")
        DB.setdefault("resets", {})[email] = {"code_hash": hash_pass(code),
                                              "expires": now() + CODE_TTL, "attempts": 0}
        save_db(DB)
    return {"ok": True, "sent": sent, "dev_code": code if (u and not sent) else None}

def do_reset_confirm(body):
    email = (body.get("email") or "").strip().lower()
    code = (body.get("code") or "").strip()
    new = body.get("password") or ""
    r = DB.get("resets", {}).get(email)
    if not r:
        raise AuthError(400, "No reset requested for this email.")
    if now() > r["expires"]:
        del DB["resets"][email]; save_db(DB)
        raise AuthError(400, "Reset code expired. Request a new one.")
    if r["attempts"] >= 6:
        del DB["resets"][email]; save_db(DB)
        raise AuthError(429, "Too many wrong attempts. Request a new code.")
    r["attempts"] += 1
    if not check_pass(code, r["code_hash"]):
        save_db(DB)
        raise AuthError(400, "Wrong code.")
    u = DB["users"].get(email)
    if not u:
        raise AuthError(404, "No such account.")
    if len(new) < 6:
        raise AuthError(400, "Password must be at least 6 characters.")
    u["pass"] = hash_pass(new)
    del DB["resets"][email]
    save_db(DB)
    return {"ok": True}

# Thanh toán: KHÁCH chuyển khoản qua VietQR (mã memo NFX-<id> để đối chiếu),
# admin đối chiếu bank app → Approve ở Admin Console → credit.
# ADMIN tự nạp cho mình vẫn tức thì (không cần tự duyệt chính mình).
# Khi gắn payment gateway thật (Momo/Stripe...) thì thay payment_info() bằng flow của cổng đó.
INSTANT_TOPUP = False

PAYMENT_CFG_PATH = os.path.join(DATA, "payment_config.json")

def load_payment_cfg():
    return load_json_cfg("payment_config.json") or {}

# ------------------------------------------------- admin settings (kiểm soát từ UI)
ADMIN_SETTINGS_PATH = os.path.join(DATA, "admin_settings.json")
SETTINGS = {
    "usd_vnd": 0, "instant_topup": True,
    "signup_credit": 1.0, "ip_credit_daily": 2.0,
    "rate_limit_free": 2.0, "rate_limit_pro": 1.0,
    "flash_cap": 4096, "pro_cap": 8192,
    "flash_in": 0.10, "flash_out": 0.15,
    "pro_in": 0.40, "pro_out": 0.70,
    "vision_price": 0.01, "motion_price": 0.025,
    "persona_flash": "", "persona_pro": "",
    "pro_gate": True, "maintenance": False, "signup_open": True,
    "signup_cap": 100,
}

def load_settings():
    s = load_json_cfg("admin_settings.json") or {}
    for k in SETTINGS:
        if k in s:
            SETTINGS[k] = s[k]
    apply_settings()

def apply_settings():
    TIER_POLICY["free"]["max_output_tokens"] = SETTINGS["flash_cap"]
    TIER_POLICY["pro"]["max_output_tokens"] = SETTINGS["pro_cap"]
    TIER_POLICY["free"]["persona"] = SETTINGS["persona_flash"] or None
    TIER_POLICY["pro"]["persona"] = SETTINGS["persona_pro"] or None
    RATE_LIMITS["free"] = SETTINGS["rate_limit_free"]
    RATE_LIMITS["pro"] = SETTINGS["rate_limit_pro"]
    MODEL_PRICING["nflashx-1.0-flash"].update({"in": SETTINGS["flash_in"], "out": SETTINGS["flash_out"]})
    MODEL_PRICING["nflashx-1.0-pro"].update({"in": SETTINGS["pro_in"], "out": SETTINGS["pro_out"]})
    MODEL_PRICING["nflashx-vision-1.0-flash"]["image"] = SETTINGS["vision_price"]
    MODEL_PRICING["nflashx-motion-1.0"]["second"] = SETTINGS["motion_price"]

def save_settings():
    os.makedirs(DATA, exist_ok=True)
    with open(ADMIN_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(SETTINGS, f, indent=2)

USD_VND = 25600
_RATE_CACHE = {"vnd": None, "ts": 0}

def usd_to_vnd_rate():
    if SETTINGS.get("usd_vnd"):
        return float(SETTINGS["usd_vnd"])
    if _RATE_CACHE["vnd"] and now() - _RATE_CACHE["ts"] < 6 * 3600:
        return _RATE_CACHE["vnd"]
    cfg = load_payment_cfg()
    r = cfg.get("usd_vnd")
    if isinstance(r, (int, float)) and r > 0:
        _RATE_CACHE["vnd"], _RATE_CACHE["ts"] = float(r), now()
        return _RATE_CACHE["vnd"]
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=8) as resp:
            v = json.loads(resp.read())["rates"]["VND"]
        _RATE_CACHE["vnd"], _RATE_CACHE["ts"] = float(v), now()
        return float(v)
    except Exception:
        return float(USD_VND)

MODEL_PRICING = {
    "nflashx-1.0-flash":        {"in": 0.10, "out": 0.15},
    "nflashx-1.0-pro":          {"in": 0.40, "out": 0.70},
    "nflashx-vision-1.0-flash": {"image": 0.010},
    "nflashx-motion-1.0":       {"second": 0.025},
}

def estimate_cost(model, usage, kind="text"):
    p = MODEL_PRICING.get(model) or MODEL_PRICING.get("nflashx-1.0-flash", {})
    if kind == "text":
        u = usage or {}
        return round(float(u.get("prompt_tokens") or 0) / 1e6 * p.get("in", 0)
                     + float(u.get("completion_tokens") or 0) / 1e6 * p.get("out", 0), 6)
    if kind == "image":
        return round(int((usage or {}).get("n") or 1) * p.get("image", 0.01), 4)
    if kind == "video":
        return round(float((usage or {}).get("seconds") or 0) * p.get("second", 0.025), 4)
    return 0.0

def payment_info(rec):
    """VietQR (VND quy đổi từ USD) + PayPal (USD)."""
    cfg = load_payment_cfg()
    memo = "NFX-" + rec["id"]
    rate = usd_to_vnd_rate()
    vnd = int(round(rec["amount"] * rate))
    out = {"memo": memo, "amount": rec["amount"], "vnd": vnd, "rate": round(rate, 2),
           "paypal": bool(load_paypal_cfg().get("client_id")),
           "usdt": (cfg.get("usdt") or "").strip()}
    if cfg.get("bank") and cfg.get("account"):
        url = ("https://img.vietqr.io/image/%s-%s-compact2.png"
               "?amount=%d&addInfo=%s&accountName=%s&style=noLogo"
               % (urllib.parse.quote(cfg["bank"]), urllib.parse.quote(cfg["account"]),
                  vnd, urllib.parse.quote(memo),
                  urllib.parse.quote(cfg.get("name", "NFlashX"))))
        out.update({"bank": cfg["bank"], "account": cfg["account"],
                    "name": cfg.get("name", ""), "vietqr": url})
    if not out.get("vietqr") and not out["paypal"] and not out.get("usdt"):
        return None
    return out

# ------------------------------------------------- PayPal (Orders v2 REST)
PAYPAL_CFG_PATH = os.path.join(DATA, "paypal_config.json")
PAYPAL_API = {"live": "https://api-m.paypal.com", "sandbox": "https://api-m.sandbox.paypal.com"}
_PP_TOKEN_CACHE = {"key": None, "token": None, "expires": 0}

def load_paypal_cfg():
    return load_json_cfg("paypal_config.json") or {}

def paypal_base():
    return PAYPAL_API.get(load_paypal_cfg().get("mode", "live"), PAYPAL_API["live"])

def paypal_token():
    import base64
    cfg = load_paypal_cfg()
    cache_key = (cfg.get("mode", "live"), cfg.get("client_id", ""))
    if (_PP_TOKEN_CACHE["token"] and _PP_TOKEN_CACHE.get("key") == cache_key
            and now() < _PP_TOKEN_CACHE["expires"]):
        return _PP_TOKEN_CACHE["token"]
    auth = base64.b64encode(f"{cfg['client_id']}:{cfg['secret']}".encode()).decode()
    req = urllib.request.Request(paypal_base() + "/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={"Authorization": "Basic " + auth,
                 "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    _PP_TOKEN_CACHE["token"] = d["access_token"]
    _PP_TOKEN_CACHE["key"] = cache_key
    _PP_TOKEN_CACHE["expires"] = now() + int(d.get("expires_in", 32400)) - 120
    return _PP_TOKEN_CACHE["token"]

def paypal_api_call(method, path, payload=None):
    req = urllib.request.Request(paypal_base() + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + paypal_token(),
                 "Content-Type": "application/json"},
        method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def paypal_create_order(rec, base_url):
    amount = "%.2f" % rec["amount"]
    desc = "NFlashX Agent Plan (Pro)" if rec.get("plan") == "pro" else "NFlashX balance topup"
    d = paypal_api_call("POST", "/v2/checkout/orders", {
        "intent": "CAPTURE",
        "purchase_units": [{"reference_id": rec["id"], "custom_id": "NFX-" + rec["id"],
                            "description": desc[:127],
                            "amount": {"currency_code": "USD", "value": amount}}],
        "application_context": {"brand_name": "NFlashX", "user_action": "PAY_NOW",
                                "return_url": base_url + "/api/paypal/return?rid=" + rec["id"],
                                "cancel_url": base_url + "/api/paypal/cancel?rid=" + rec["id"]}})
    approve = next((l["href"] for l in d.get("links", []) if l["rel"] == "approve"), None)
    return d.get("id"), approve

def paypal_capture(order_id):
    return paypal_api_call("POST", f"/v2/checkout/orders/{order_id}/capture", {})

def credit_topup(rec):
    """Cộng tiền + nâng tier (nếu là gói) — dùng chung cho admin duyệt & PayPal capture."""
    rec["status"] = "approved"
    tu = DB["users"].get(rec["email"])
    if tu:
        tu["balance"] = round(tu.get("balance", 0) + rec["amount"], 2)
        if rec.get("plan") == "pro":
            tu["plan"] = "Pro"
    if rec.get("plan") == "pro" and SQLITE is not None:
        with SQLITE_LOCK:
            SQLITE.execute("UPDATE users SET tier='pro' WHERE email=?", (rec["email"],))
            SQLITE.commit()
    save_db(DB)
    notify_user_topup_done(rec, True)

def do_paypal_create(body, handler):
    """Tạo PayPal order cho request nạp → trả về link approve để redirect khách."""
    u = session_user(body)
    cfg = load_paypal_cfg()
    if not cfg.get("client_id") or not cfg.get("secret"):
        raise AuthError(503, "PayPal is not configured yet. Use Bank QR / USDT or ask the admin.")
    try:
        amt = float(body.get("amount"))
    except (TypeError, ValueError):
        raise AuthError(400, "Invalid amount.")
    if not (5 <= amt <= 10000):
        raise AuthError(400, "Amount must be between $5 and $10,000.")
    plan = "pro" if (body.get("plan") or "").lower() == "pro" else None
    rec = {"id": secrets.token_hex(4), "email": u["email"], "amount": round(amt, 2),
           "plan": plan, "ts": now(), "status": "pending", "method": "paypal"}
    host = handler.headers.get("Host") or f"127.0.0.1:{PORT}"
    base_url = f"http://{host}"
    try:
        order_id, approve_url = paypal_create_order(rec, base_url)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:150]
        raise AuthError(502, f"PayPal rejected the request ({e.code}). Check Client ID/Secret in Admin Console. {detail}")
    except Exception as e:
        raise AuthError(502, f"Could not reach PayPal: {e}")
    if not order_id or not approve_url:
        raise AuthError(502, "PayPal did not return an approval link. Try again.")
    rec["paypal_order_id"] = order_id
    DB.setdefault("topups", []).append(rec)
    save_db(DB)
    return {"ok": True, "approve_url": approve_url, "request": rec}

def do_paypal_return(rid):
    """Khách quay lại từ PayPal → capture order → credit tự động."""
    rec = next((t for t in DB.get("topups", []) if t.get("id") == rid), None)
    if not rec:
        return "error"
    if rec["status"] == "approved":
        return "ok"
    try:
        d = paypal_capture(rec.get("paypal_order_id"))
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        # đã capture trước đó (user refresh) → coi như xong nếu capture status COMPLETED
        return "ok" if '"status": "COMPLETED"' in body or "ORDER_ALREADY_CAPTURED" in body else "error"
    if d.get("status") == "COMPLETED":
        credit_topup(rec)
        return "ok"
    return "error"

def do_paypal_sdk_create(body, handler):
    """PayPal JS SDK: tạo order, trả {id} để SDK mở popup thanh toán tại chỗ."""
    u = session_user(body)
    cfg = load_paypal_cfg()
    if not cfg.get("client_id") or not cfg.get("secret"):
        raise AuthError(503, "PayPal is not configured.")
    try:
        amt = float(body.get("amount"))
    except (TypeError, ValueError):
        raise AuthError(400, "Invalid amount.")
    if not (5 <= amt <= 10000):
        raise AuthError(400, "Amount must be between $5 and $10,000.")
    plan = "pro" if (body.get("plan") or "").lower() == "pro" else None
    rec = {"id": secrets.token_hex(4), "email": u["email"], "amount": round(amt, 2),
           "plan": plan, "ts": now(), "status": "pending", "method": "paypal-sdk"}
    d = paypal_api_call("POST", "/v2/checkout/orders", {
        "intent": "CAPTURE",
        "purchase_units": [{"reference_id": rec["id"], "custom_id": "NFX-" + rec["id"],
                            "description": ("NFlashX Agent Plan (Pro)" if plan == "pro"
                                            else "NFlashX balance topup")[:127],
                            "amount": {"currency_code": "USD", "value": "%.2f" % rec["amount"]}}],
        "application_context": {"brand_name": "NFlashX", "user_action": "PAY_NOW",
                                "shipping_preference": "NO_SHIPPING"}})
    rec["paypal_order_id"] = d["id"]
    DB.setdefault("topups", []).append(rec)
    save_db(DB)
    return {"ok": True, "id": d["id"], "request_id": rec["id"]}

def do_paypal_sdk_capture(body):
    """SDK onApprove → capture order → cộng balance ngay tại chỗ."""
    u = session_user(body)
    order_id = body.get("orderID") or ""
    rid = body.get("request_id") or ""
    if not order_id:
        raise AuthError(400, "Missing orderID.")
    rec = next((t for t in DB.get("topups", []) if t.get("id") == rid), None)
    if not rec:
        raise AuthError(404, "Top-up request not found.")
    if rec["email"] != u["email"]:
        raise AuthError(403, "This request belongs to another account.")
    if rec["status"] == "approved":
        return {"ok": True, "already": True, "amount": rec["amount"], "balance": u.get("balance", 0)}
    try:
        d = paypal_capture(order_id)
    except urllib.error.HTTPError as e:
        raise AuthError(502, "PayPal capture failed: " + e.read().decode()[:150])
    if d.get("status") != "COMPLETED":
        raise AuthError(402, "Payment not completed (status " + str(d.get("status")) + ").")
    credit_topup(rec)
    return {"ok": True, "amount": rec["amount"], "balance": DB["users"][u["email"]].get("balance", 0)}

def do_paypal_client(body):
    """Trả client_id + currency cho JS SDK (public info, không phải secret)."""
    cfg = load_paypal_cfg()
    return {"ok": True, "client_id": cfg.get("client_id", ""),
            "currency": "USD", "enabled": bool(cfg.get("client_id") and cfg.get("secret"))}

def do_api_pricing(body):
    """Bảng giá công khai để khách biết bị trừ bao nhiêu."""
    return {"ok": True, "pricing": MODEL_PRICING,
            "note": "Prices in USD. Text: per 1M tokens (input/output). Image: per image. Video: per second.",
            "free_trial": "Flash: first 10,000 requests/month not deducted (trial)."}

def do_my_billing(body):
    """Khách xem mình đã bị trừ bn, còn bao nhiêu."""
    u = session_user(body)
    hist = u.get("charged_history", [])[-50:]
    return {"ok": True, "balance": round(u.get("balance", 0), 6),
            "charged_total": round(u.get("charged_total", 0), 6),
            "history": hist}

def do_admin_webhook_sim(body, handler):
    """Webhook nhận thông báo chuyển khoản (Casso/Sepay/ngân hàng).
    Format chuẩn: {"data":[{"description":"NFX-xxxx","amount":256000,...}]}
    Tự khớp memo → tự credit + nâng tier nếu là gói. An toàn: cần secret key."""
    sec = (body.get("secure_token") or handler.headers.get("Secure-Token") or "")
    expected = load_payment_cfg().get("webhook_token") or ""
    if not expected or sec != expected:
        raise AuthError(403, "Invalid webhook token.")
    rows = body.get("data") or ([body] if body.get("description") else [])
    done, skipped = [], []
    for row in rows:
        desc = str(row.get("description") or row.get("content") or "")
        m = re.search(r"NFX-([0-9a-f]{8})", desc, re.I)
        if not m:
            skipped.append({"reason": "no NFX memo", "desc": desc[:60]}); continue
        rid = m.group(1)
        rec = next((t for t in DB.get("topups", []) if t.get("id") == rid), None)
        if not rec:
            skipped.append({"reason": "request not found", "id": rid}); continue
        if rec["status"] != "pending":
            skipped.append({"reason": "already " + rec["status"], "id": rid}); continue
        amt = float(row.get("amount") or 0)
        rate = usd_to_vnd_rate()
        expect_vnd = rec["amount"] * rate
        # chấp nhận sai số 2% (phí ngân hàng) hoặc khớp tuyệt đối
        if amt and abs(amt - expect_vnd) > expect_vnd * 0.02:
            skipped.append({"reason": "amount mismatch", "expect": int(expect_vnd), "got": int(amt), "id": rid})
            continue
        rec["paid_vnd"] = amt
        rec["paid_via"] = "bank-webhook"
        credit_topup(rec)
        done.append({"id": rid, "email": rec["email"], "amount": rec["amount"]})
    return {"ok": True, "credited": done, "skipped": skipped}

def do_topup_txid(body):
    u = session_user(body)
    tid, txid = body.get("id") or "", (body.get("txid") or "").strip()
    if not tid or not txid:
        raise AuthError(400, "Missing request id or TXID.")
    if not re.match(r"^[0-9a-fA-F]{20,120}$", txid):
        raise AuthError(400, "TXID is not valid (it is the transaction hash from your wallet/exchange).")
    for t in DB.get("topups", []):
        if t.get("id") == tid:
            if t["email"] != u["email"]:
                raise AuthError(403, "This request belongs to another account.")
            if t["status"] != "pending":
                raise AuthError(400, "This request is already " + t["status"] + ".")
            t["txid"] = txid
            save_db(DB)
            return {"ok": True, "txid": txid}
    raise AuthError(404, "No such top-up request.")

def do_recharge_request(body):
    u = session_user(body)
    try:
        amt = float(body.get("amount"))
    except (TypeError, ValueError):
        raise AuthError(400, "Invalid amount.")
    if not (5 <= amt <= 10000):
        raise AuthError(400, "Amount must be between $5 and $10,000.")
    rec = {"id": secrets.token_hex(4), "email": u["email"], "amount": round(amt, 2),
           "plan": "pro" if (body.get("plan") or "").lower() == "pro" else None,
           "ts": now(), "status": "pending"}
    if SETTINGS["instant_topup"] or u.get("admin"):
        rec["status"] = "approved"
        u["balance"] = round(u.get("balance", 0) + rec["amount"], 2)
        if rec["plan"] == "pro":
            u["plan"] = "Pro"
        DB.setdefault("topups", []).append(rec)
        if SQLITE is not None and rec["plan"] == "pro":
            with SQLITE_LOCK:
                SQLITE.execute("UPDATE users SET tier='pro' WHERE email=?", (u["email"],))
                SQLITE.commit()
        save_db(DB)
        return {"ok": True, "request": rec, "instant": True}
    DB.setdefault("topups", []).append(rec)
    save_db(DB)
    resp = {"ok": True, "request": rec}
    info = payment_info(rec)          # QR + bank info cho khách chuyển khoản
    if info:
        resp["payment"] = info
    else:
        resp["payment_missing"] = True
    notify_admins_new_topup(rec)      # báo GMAIL admin kèm memo (khi đã cấu hình mail)
    return resp

def do_recharge_status(body):
    u = session_user(body)
    mine = [t for t in DB.get("topups", []) if t["email"] == u["email"]]
    return {"ok": True, "balance": round(u.get("balance", 0), 2),
            "pending": len([t for t in mine if t["status"] == "pending"]),
            "history": [{"amount": t["amount"], "status": t["status"],
                         "ts": t["ts"]} for t in reversed(mine[-20:])]}

def do_usage(body):
    u = session_user(body)
    today0 = time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d"))
    out = {"ok": True, "lifetime_requests": 0, "today_requests": 0,
           "today_by_endpoint": {}, "lifetime_by_endpoint": {}, "daily": {},
           "balance": round(u.get("balance", 0), 2)}
    if SQLITE is not None:
        with SQLITE_LOCK:
            out["lifetime_requests"] = SQLITE.execute(
                "SELECT COALESCE(SUM(total_requests),0) FROM users WHERE email=?", (u["email"],)).fetchone()[0]
            out["today_requests"] = SQLITE.execute(
                "SELECT COUNT(*) FROM usage_log WHERE email=? AND ts>=?", (u["email"], today0)).fetchone()[0]
            for ep, n in SQLITE.execute(
                "SELECT endpoint, COUNT(*) FROM usage_log WHERE email=? AND ts>=? GROUP BY endpoint",
                    (u["email"], today0)).fetchall():
                out["today_by_endpoint"][ep or "unknown"] = n
            for ep, n in SQLITE.execute(
                "SELECT endpoint, COUNT(*) FROM usage_log WHERE email=? GROUP BY endpoint",
                    (u["email"],)).fetchall():
                out["lifetime_by_endpoint"][ep or "unknown"] = n
            for day, n in SQLITE.execute(
                "SELECT date(ts,'unixepoch','localtime'), COUNT(*) FROM usage_log WHERE email=? "
                "AND ts>=? GROUP BY 1", (u["email"], now() - 365 * 86400)).fetchall():
                out["daily"][day] = n
    return out

# ------------------------------------------------- admin console (hang that)
def do_admin_settings(body, handler):
    require_admin(body)
    keys_num = ("usd_vnd", "signup_credit", "ip_credit_daily", "rate_limit_free", "rate_limit_pro",
                "flash_in", "flash_out", "pro_in", "pro_out", "vision_price", "motion_price")
    keys_int = ("flash_cap", "pro_cap", "signup_cap")
    keys_bool = ("instant_topup", "pro_gate", "maintenance", "signup_open")
    keys_str = ("persona_flash", "persona_pro")
    if any(k in body for k in list(keys_num) + list(keys_int) + list(keys_bool) + list(keys_str)):
        for k in list(keys_num) + list(keys_int):
            if k in body:
                try:
                    SETTINGS[k] = int(body[k]) if k in keys_int else float(body[k])
                except (TypeError, ValueError):
                    raise AuthError(400, "Invalid value for " + k)
        for k in keys_bool:
            if k in body:
                SETTINGS[k] = bool(body[k])
        for k in keys_str:
            if k in body:
                SETTINGS[k] = str(body[k] or "")
        save_settings(); apply_settings()
    return {"ok": True, "settings": SETTINGS}

def do_admin_agnes_keys(body, handler):
    """Quản lý pool key Agnes: {"add": "key"} để thêm, {"keys": [...]} để thay toàn bộ."""
    require_admin(body)
    changed = False
    if body.get("add"):
        raw = body.get("add")
        if isinstance(raw, str):
            lines = [x for x in raw.replace(chr(13), "").split(chr(10)) if x.strip()]
        else:
            lines = list(raw)
        cur = load_json_cfg("agnes_keys.json") or []
        cur = [str(x).strip() for x in cur if str(x).strip()]
        for k in lines:
            k = str(k).strip()
            if k and k not in cur and k != (API_KEY or ""):
                cur.append(k)
                changed = True
        if changed:
            save_json_cfg("agnes_keys.json", cur)
            reload_agnes_keys()
    if body.get("keys") is not None:
        raw = body.get("keys")
        lines = raw.splitlines() if isinstance(raw, str) else list(raw or [])
        clean = []
        for k in lines:
            k = str(k).strip()
            if k and k not in clean and k != (API_KEY or ""):
                clean.append(k)
        save_json_cfg("agnes_keys.json", clean)
        reload_agnes_keys()
        changed = True
    usage = [_AGNES_USAGE.get(k, 0) for k in AGNES_KEYS]
    return {"ok": True, "count": len(AGNES_KEYS), "changed": changed,
            "masked": [mask_key(k) for k in AGNES_KEYS],
            "usage": usage,
            "usage_str": "/".join(str(x) for x in usage),
            "total_req": sum(usage)}

def do_admin_announce(body, handler):
    require_admin(body)
    if body.get("title") or body.get("body"):
        rec = {"id": secrets.token_hex(4), "title": (body.get("title") or "").strip()[:120],
               "body": (body.get("body") or "").strip()[:2000], "ts": now()}
        DB.setdefault("announcements", []).insert(0, rec)
        del DB["announcements"][30:]
        save_db(DB)
        return {"ok": True, "announcement": rec}
    if body.get("delete_id"):
        DB["announcements"] = [a for a in DB.get("announcements", []) if a["id"] != body["delete_id"]]
        save_db(DB)
        return {"ok": True}
    return {"ok": True, "announcements": DB.get("announcements", [])}

def do_admin_ipbans(body, handler):
    require_admin(body)
    if body.get("action") == "unban" and body.get("ip"):
        DB["banned_ips"] = [b for b in DB.get("banned_ips", []) if b["ip"] != body["ip"]]
        save_db(DB)
        return {"ok": True, "banned_ips": DB.get("banned_ips", [])}
    if body.get("action") == "ban" and body.get("ip"):
        ip = str(body["ip"]).strip()
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise AuthError(400, "Invalid IP address.")
        DB.setdefault("banned_ips", []).append({"ip": ip, "until": 0,
                                                "reason": body.get("reason") or "banned by admin"})
        save_db(DB)
        return {"ok": True, "banned_ips": DB.get("banned_ips", [])}
    return {"ok": True, "banned_ips": DB.get("banned_ips", [])}

def do_admin_user_detail(body, handler):
    require_admin(body)
    email = (body.get("email") or "").lower()
    u = DB["users"].get(email)
    if not u:
        raise AuthError(404, "No such user.")
    row = None
    if SQLITE is not None:
        with SQLITE_LOCK:
            row = SQLITE.execute(
                "SELECT tier,total_requests,last_ip,COALESCE(banned,0) FROM users WHERE email=?",
                (email,)).fetchone()
    return {"ok": True, "email": email, "user": public_user(u),
            "keys": u.get("keys", []), "charged_history": u.get("charged_history", [])[-100:],
            "charged_total": round(u.get("charged_total", 0), 6),
            "balance": round(u.get("balance", 0), 2),
            "tier": row[0] if row else None, "total_requests": row[1] if row else 0,
            "last_ip": row[2] if row else None,
            "sessions": sum(1 for s2 in DB["sessions"].values() if s2["email"] == email),
            "topups": [t for t in DB.get("topups", []) if t["email"] == email][-20:]}

def do_admin_server_restart(body, handler):
    require_admin(body)
    import subprocess, sys
    subprocess.Popen([sys.executable, "-I", "server.py"], cwd=ROOT,
                     creationflags=0x00000008 | 0x00000200)
    threading.Timer(1.5, lambda: os._exit(0)).start()
    return {"ok": True, "restarting": True}

def do_admin_clear(body, handler):
    """Dọn dữ liệu test: topups / usage_log / announcements."""
    require_admin(body)
    target = body.get("target")
    if target == "topups":
        DB["topups"] = []
        save_db(DB)
        return {"ok": True, "cleared": "topups"}
    if target == "usage":
        if SQLITE is not None:
            with SQLITE_LOCK:
                SQLITE.execute("DELETE FROM usage_log")
                SQLITE.commit()
        return {"ok": True, "cleared": "usage"}
    if target == "announcements":
        DB["announcements"] = []
        save_db(DB)
        return {"ok": True, "cleared": "announcements"}
    if target == "test_accounts":
        keep = {e for e, u in DB["users"].items() if u.get("admin")}
        for e in list(DB["users"]):
            if e not in keep:
                DB["users"].pop(e)
        DB["sessions"] = {t: s2 for t, s2 in DB["sessions"].items() if s2["email"] in keep}
        if SQLITE is not None:
            with SQLITE_LOCK:
                for (e,) in SQLITE.execute("SELECT email FROM users").fetchall():
                    if e not in keep:
                        SQLITE.execute("DELETE FROM users WHERE email=?", (e,))
                SQLITE.commit()
        save_db(DB)
        return {"ok": True, "cleared": "test_accounts", "kept": list(keep)}
    raise AuthError(400, "Unknown clear target.")

def do_admin_users(body, handler):
    require_admin(body)
    today0 = time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d"))
    per_today, lifetime, last_ips = {}, {}, {}
    if SQLITE is not None:
        with SQLITE_LOCK:
            per_today = {r[0]: r[1] for r in SQLITE.execute(
                "SELECT email, COUNT(*) FROM usage_log WHERE ts>=? GROUP BY email", (today0,)).fetchall()}
            lifetime = {r[0]: r[1] for r in SQLITE.execute(
                "SELECT email, MAX(total_requests) FROM users GROUP BY email").fetchall()}
            last_ips = {r[0]: r[1] for r in SQLITE.execute(
                "SELECT email, MAX(last_ip) FROM users WHERE last_ip IS NOT NULL GROUP BY email").fetchall()}
    rows = []
    for email, u in DB["users"].items():
        keys = [k["key"] for k in u.get("keys", [])] or ([u["api_key"]] if u.get("api_key") else [])
        rows.append({
            "email": email, "name": u.get("name", ""), "provider": u.get("provider", "email"),
            "admin": bool(u.get("admin")), "banned": bool(u.get("banned")),
            "plan": u.get("plan", "Free"), "created": u.get("created"),
            "keys": len(keys), "key_list": [k[:10] + "…" + k[-4:] for k in keys],
            "total_requests": lifetime.get(email, 0), "today_requests": per_today.get(email, 0),
            "last_ip": last_ips.get(email, ""), "balance": round(u.get("balance", 0), 2),
        })
    if SQLITE is not None:
        with SQLITE_LOCK:
            for r in SQLITE.execute(
                    "SELECT email, api_key, tier, total_requests, last_ip, COALESCE(banned,0) FROM users").fetchall():
                if r[0] in DB["users"]:
                    continue
                rows.append({"email": r[0], "name": "(self-serve)", "provider": "api",
                             "admin": False, "banned": bool(r[5]), "plan": r[2], "created": None,
                             "keys": 1, "key_list": [r[1][:10] + "…" + r[1][-4:]],
                             "total_requests": r[3], "today_requests": per_today.get(r[0], 0),
                             "last_ip": r[4] or "", "balance": 0})
    rows.sort(key=lambda x: -x["today_requests"])
    return {"ok": True, "users": rows}

def do_admin_stats(body, handler):
    require_admin(body)
    today0 = time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d"))
    out = {"ok": True, "today_total": 0, "today_users": 0, "per_endpoint": {}, "recent": [],
           "pending_topups": len([t for t in DB.get("topups", []) if t["status"] == "pending"])}
    if SQLITE is not None:
        with SQLITE_LOCK:
            out["today_total"] = SQLITE.execute(
                "SELECT COUNT(*) FROM usage_log WHERE ts>=?", (today0,)).fetchone()[0]
            out["today_users"] = SQLITE.execute(
                "SELECT COUNT(DISTINCT email) FROM usage_log WHERE ts>=?", (today0,)).fetchone()[0]
            out["per_endpoint"] = dict(SQLITE.execute(
                "SELECT COALESCE(endpoint,'unknown'), COUNT(*) FROM usage_log WHERE ts>=? GROUP BY 1",
                (today0,)).fetchall())
            for r in SQLITE.execute(
                    "SELECT email,api_key,endpoint,ip,ts FROM usage_log ORDER BY id DESC LIMIT 50").fetchall():
                out["recent"].append({"email": r[0], "api_key": (r[1] or "")[:10] + "…" + (r[1] or "")[-4:],
                                      "endpoint": r[2], "ip": r[3], "ts": r[4]})
    return out

def do_admin_topups(body, handler):
    require_admin(body)
    return {"ok": True, "topups": DB.get("topups", [])[-100:]}

def do_admin_action(body, handler):
    """Ban/unban, set-tier, topup approve/reject — qua admin_key HOẶC session admin."""
    admin_ok = (body.get("admin_key") or "") == ADMIN_KEY
    if not admin_ok:
        require_admin(body)   # raise 401/403 nếu không phải admin
    action, email = body.get("action"), (body.get("email") or "").lower()
    if action == "topup":
        tid, decision = body.get("id"), body.get("decision")
        for t in DB.get("topups", []):
            if t.get("id") == tid:
                if decision == "approve":
                    credit_topup(t)   # cộng tiền + nâng tier (nếu gói) + email khách
                else:
                    t["status"] = "rejected"
                    notify_user_topup_done(t, False)
                save_db(DB)
                return {"ok": True, "topup": t}
        raise AuthError(404, "No such top-up request.")
    if action == "payment-cfg":
        # Lấy/cấu hình tài khoản nhận tiền (VietQR + USDT TRC20 + PayPal) — chỉ admin
        if body.get("bank") and body.get("account"):
            cfg = {"bank": str(body["bank"]).strip(), "account": str(body["account"]).strip(),
                   "name": str(body.get("name") or "NFlashX").strip()}
            old = load_payment_cfg()
            if str(body.get("usdt") or "").strip():
                cfg["usdt"] = str(body["usdt"]).strip()
            elif old.get("usdt"):
                cfg["usdt"] = old["usdt"]   # giữ usdt cũ nếu không nhập mới
            os.makedirs(DATA, exist_ok=True)
            with open(PAYMENT_CFG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            return {"ok": True, "config": cfg}
        return {"ok": True, "config": load_payment_cfg()}
    if action == "paypal-cfg":
        # Lưu/thay PayPal REST credentials (client_id + secret từ developer.paypal.com)
        old = load_paypal_cfg()
        cid = str(body.get("client_id") or "").strip() or old.get("client_id", "")
        sec = str(body.get("secret") or "").strip() or old.get("secret", "")
        mode = str(body.get("mode") or "").strip() or old.get("mode", "live")
        if body.get("client_id") is not None or body.get("secret") is not None or body.get("mode") is not None:
            cfg = {"client_id": cid, "secret": sec, "mode": mode if mode in PAYPAL_API else "live"}
            os.makedirs(DATA, exist_ok=True)
            with open(PAYPAL_CFG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            _PP_TOKEN_CACHE["token"] = None   # reset token cache khi đổi credentials
            return {"ok": True, "configured": bool(cid and sec), "mode": cfg["mode"]}
        return {"ok": True, "configured": bool(old.get("client_id")), "mode": old.get("mode", "live"),
                "client_id": old.get("client_id", "")}
    u = DB["users"].get(email)
    if action == "set-tier":
        tier = (body.get("tier") or "").lower()
        if tier not in TIER_POLICY:
            raise AuthError(400, "Tier must be 'free' or 'pro'.")
        found = False
        if SQLITE is not None:
            with SQLITE_LOCK:
                cur = SQLITE.execute("UPDATE users SET tier=? WHERE email=?", (tier, email))
                SQLITE.commit()
            found = cur.rowcount > 0
        if u is not None:
            u["plan"] = "Pro" if tier == "pro" else "Free"
            save_db(DB)
            found = True
        if not found:
            raise AuthError(404, "No such user.")
        return {"ok": True, "email": email, "tier": tier}
    # Guard admin: account admin luôn nằm trong db.json
    if u and u.get("admin") and action in ("ban", "delete"):
        raise AuthError(403, "Admin accounts cannot be banned or deleted from the console.")
    if action in ("ban", "unban", "delete"):
        found = False
        if action == "delete":
            # Xóa vĩnh viễn ở CẢ HAI kho: db.json + sessions + SQLite (kể cả user self-serve)
            if u:
                DB["users"].pop(email, None)
                for t in [t for t, s in DB["sessions"].items() if s["email"] == email]:
                    DB["sessions"].pop(t, None)
                save_db(DB)
                found = True
            if SQLITE is not None:
                with SQLITE_LOCK:
                    cur = SQLITE.execute("DELETE FROM users WHERE email=?", (email,))
                    SQLITE.commit()
                found = found or cur.rowcount > 0
            if not found:
                raise AuthError(404, "No such user.")
            return {"ok": True, "email": email, "deleted": True}
        # ban / unban — đặt cờ ở cả db.json lẫn SQLite (user self-serve chỉ có SQLite)
        if u:
            u["banned"] = (action == "ban")
            found = True
        if SQLITE is not None:
            with SQLITE_LOCK:
                cur = SQLITE.execute("UPDATE users SET banned=? WHERE email=?",
                                     (1 if action == "ban" else 0, email))
                SQLITE.commit()
            found = found or cur.rowcount > 0
        if not found:
            raise AuthError(404, "No such user.")
        if u:
            save_db(DB)
        return {"ok": True, "email": email, "banned": action == "ban"}
    raise AuthError(400, "Unknown action.")

# ------------------------------------------------- vision studio limits
VISION_TRIES = 3   # 3 lan moi login + 3 lan moi IP moi ngay

def vision_allow(handler, body):
    ip = client_ip(handler)
    day = time.strftime("%Y-%m-%d")
    v = DB.setdefault("vision_ip", {})
    rec = v.get(ip) if v.get(ip, {}).get("day") == day else {"day": day, "n": 0}
    if rec["n"] >= VISION_TRIES:
        raise AuthError(429, "Free trial used up: %d images per network per day. Sign in for your own 3 tries, or come back tomorrow." % VISION_TRIES)
    token = (body or {}).get("token") or ""
    if token:
        trials = DB.setdefault("vision_trials", {})
        if trials.get(token, 0) >= VISION_TRIES:
            raise AuthError(429, "You used all %d free tries for this login. Create API keys in the API Platform for more." % VISION_TRIES)
    rec["n"] += 1
    v[ip] = rec
    if token:
        trials = DB.setdefault("vision_trials", {})
        trials[token] = trials.get(token, 0) + 1
    save_db(DB)

def video_defaults(body):
    """Upstream /v1/videos bat buoc mode/seconds/size/aspect_ratio — dien mac dinh."""
    if isinstance(body, dict):
        body.setdefault("mode", "text")
        body.setdefault("seconds", "5")
        body.setdefault("size", "720P")
        body.setdefault("aspect_ratio", "16:9")
    return body

# ---------------------------------------------------------------- passwords
def hash_pass(password, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${h}"

def check_pass(password, stored):
    try:
        salt, h = stored.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_pass(password, salt).split("$")[1], h)

# ---------------------------------------------------------------- disposable mail blocker
DISPOSABLE_DOMAINS = {
    "mailinator.com","10minutemail.com","10minutemail.net","guerrillamail.com","guerrillamail.net",
    "guerrillamail.org","sharklasers.com","grr.la","yopmail.com","yopmail.net","trashmail.com",
    "trashmail.net","trash-mail.com","tempmail.com","temp-mail.org","tempmailo.com","tempmail.dev",
    "getnada.com","nada.email","dispostable.com","fakeinbox.com","throwawaymail.com","maildrop.cc",
    "mintemail.com","mytemp.email","spam4.me","mailnesia.com","tempinbox.com","tmpmail.org",
    "throwam.com","moakt.com","mohmal.com","emailondeck.com","email-fake.com","fakemailgenerator.com",
    "fake-mail.net","mailtemp.net","tempr.email","discard.email","spamgourmet.com","burnermail.io",
    "anonaddy.me","33mail.com","mailcatch.com","inboxbear.com","tempmailaddress.com","mailsac.com",
    "inboxkitten.com","harakirimail.com","mailde.de","mailde.info","luxusmail.org","cs.email",
    "edumail.edu.pl","1secmail.com","1secmail.net","1secmail.org","esiix.com","wwjmp.com","xojxe.com",
    "yoggm.com","vjuum.com","laafd.com","txcct.com","kzccv.com","qiott.com","wuuvo.com","icznn.com",
    "ezztt.com","crymail.com","tempmail.plus","internxt.com","altmails.com","temprmail.com",
    "getairmail.com","airmail.cc","10minutemail.pl","binkmail.com","bobmail.info","chammy.info",
    "devnullmail.com","letthemeatspam.com","mailin8r.com","mailinater.com","notmailinator.com",
    "reallymymail.com","sogetthis.com","spambog.com","spamhole.com","thisisnotmyrealemail.com",
    "trbvm.com","uggsrock.com","wegwerfmail.de","zoemail.net","sneakemail.com","jetable.org",
    "mail-temporaire.fr","moncourrier.fr.nf","monmail.fr.nf","discardmail.com","spambog.de",
}
DISPOSABLE_PATTERNS = re.compile(
    r"^(temp|trash|fake|throwaway|disposable|10minute|burner|junk|spam|onetime|one-time)[\w.-]*", re.I)

def mail_allowed(email):
    domain = email.rsplit("@", 1)[1].lower()
    if domain in DISPOSABLE_DOMAINS:
        return False, "Disposable / temporary email domains are not allowed. Use a real mailbox."
    if DISPOSABLE_PATTERNS.match(domain.split(".")[0]):
        return False, "This looks like a throwaway email domain. Use a real mailbox."
    return True, ""

# ---------------------------------------------------------------- mail sending
def load_json_cfg(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def save_json_cfg(name, obj):
    p = os.path.join(DATA, name)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)

# ---------------------------------------------------------- Agnes key pool
# Nhiều key xoay vòng: 1 acc Agnes kéo quá nhiều user sẽ bị rate-limit/die.
AGNES_KEYS = []
_AGNES_STATE = {}          # key -> thời điểm hết cooldown
_AGNES_USAGE = {}          # key -> số request đã gửi qua key này (xoay liên tục)          # key -> thời điểm hết cooldown
_AGNES_RR = {"i": 0}
_AGNES_LOCK = threading.Lock()

def reload_agnes_keys():
    global AGNES_KEYS
    raw = load_json_cfg("agnes_keys.json") or []
    keys = []
    if isinstance(raw, list):
        for k in raw:
            k = str(k).strip()
            if k and k not in keys:
                keys.append(k)
    env = (API_KEY or "").strip()
    if env and env not in keys:
        keys.insert(0, env)
    AGNES_KEYS = keys
    return keys

def mask_key(k):
    return (k[:6] + "..." + k[-4:]) if len(k) > 12 else ("..." if k else "")

def agnes_key_order():
    """Xoay vòng key; key vừa bị 401/402/429 bị tạm nghỉ."""
    with _AGNES_LOCK:
        ks = list(AGNES_KEYS) or reload_agnes_keys()
        if not ks:
            return []
        t = now()
        start = _AGNES_RR["i"] % len(ks)
        _AGNES_RR["i"] = (start + 1) % len(ks)
    order = ks[start:] + ks[:start]
    alive = [k for k in order if _AGNES_STATE.get(k, 0) <= t]
    return alive or order

def agnes_key_penalize(k, status):
    secs = 3600 if status == 401 else (600 if status == 402 else 120)
    _AGNES_STATE[k] = now() + secs

def send_mail(to, subject, html_body, text_body=""):
    """Gửi email qua SMTP khi đã cấu hình mail_config.json; không thì in ra console (dev)."""
    cfg = load_json_cfg("mail_config.json")
    if not cfg or not cfg.get("enabled"):
        print(f"[MAIL NOT CONFIGURED] to={to} | {subject} | {text_body or html_body[:120]}")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg.get("from", cfg["user"])
    msg["To"] = to
    msg.attach(MIMEText(text_body or html_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    port = int(cfg.get("port", 465))
    if port == 465:
        smtp = smtplib.SMTP_SSL(cfg["host"], port, timeout=20)
    else:
        smtp = smtplib.SMTP(cfg["host"], port, timeout=20)
        smtp.starttls()
    try:
        smtp.login(cfg["user"], cfg["pass"])
        smtp.send_message(msg)
    finally:
        smtp.quit()
    return True

def send_code_email(to, code):
    cfg = load_json_cfg("mail_config.json")
    if not cfg or not cfg.get("enabled"):
        print(f"[MAIL NOT CONFIGURED] verification code for {to}: {code}")
        return False
    html = f"""<div style="background:#04060a;padding:32px;font-family:Segoe UI,Arial,sans-serif">
      <div style="max-width:460px;margin:0 auto;background:#0c1016;border:1px solid #1f2a36;border-radius:16px;padding:32px;text-align:center">
        <h2 style="color:#fff;margin:0 0 6px">NFlashX</h2>
        <p style="color:#8fa0b0;font-size:13px;margin:0 0 24px">Your verification code (expires in 10 minutes)</p>
        <div style="font-size:34px;letter-spacing:10px;font-weight:700;color:#25e39a">{code}</div>
        <p style="color:#5c6975;font-size:12px;margin-top:24px">If you didn't request this, ignore this email.</p>
      </div></div>"""
    return send_mail(to, f"NFlashX — your verification code: {code}", html,
                     f"Your NFlashX verification code: {code} (expires in 10 minutes)")

def admin_emails():
    return [e for e, u in DB["users"].items() if u.get("admin")]

def notify_admins_new_topup(rec):
    """Khách tạo yêu cầu nạp → báo GMAIL admin kèm mã memo để đối chiếu."""
    if rec.get("status") != "pending":
        return
    link = f"http://127.0.0.1:{PORT}/admin.html"
    for e in admin_emails():
        send_mail(e, f"NFlashX — new recharge request ${rec['amount']} (memo NFX-{rec['id']})",
                  f"""<div style="background:#04060a;padding:32px;font-family:Segoe UI,Arial,sans-serif">
                  <div style="max-width:460px;margin:0 auto;background:#0c1016;border:1px solid #1f2a36;border-radius:16px;padding:28px;color:#f2f6f9">
                  <h2 style="margin:0 0 10px;color:#fff">New recharge request</h2>
                  <p style="color:#8fa0b0;font-size:14px;line-height:1.7;margin:0">
                  User: <b>{rec['email']}</b><br>Amount: <b style="color:#25e39a">${rec['amount']}</b><br>
                  Memo: <b style="font-family:monospace">NFX-{rec['id']}</b><br>Plan: {rec.get('plan') or '— (balance only)'}</p>
                  <p style="margin-top:16px"><a href="{link}" style="color:#25e39a">Open Admin Console to approve →</a></p>
                  </div></div>""",
                  f"New recharge ${rec['amount']} from {rec['email']} — memo NFX-{rec['id']} — approve in Admin Console ({link}).")

def notify_user_topup_done(rec, approved):
    status = "approved" if approved else "rejected"
    bal = ""
    if approved:
        tu = DB["users"].get(rec["email"])
        if tu:
            bal = f" Current balance: <b>${tu.get('balance', 0)}</b>."
    color = "#25e39a" if approved else "#ff6b6b"
    send_mail(rec["email"], f"NFlashX — your recharge ${rec['amount']} was {status}",
              f"""<div style="background:#04060a;padding:32px;font-family:Segoe UI,Arial,sans-serif">
              <div style="max-width:460px;margin:0 auto;background:#0c1016;border:1px solid #1f2a36;border-radius:16px;padding:28px;color:#f2f6f9">
              <h2 style="margin:0 0 10px;color:#fff">Recharge {status}</h2>
              <p style="color:#8fa0b0;font-size:14px;line-height:1.7;margin:0">
              Request <b style="font-family:monospace">NFX-{rec['id']}</b> for <b style="color:{color}">${rec['amount']}</b> was <b>{status}</b>.{bal}</p>
              </div></div>""",
              f"Your recharge NFX-{rec['id']} (${rec['amount']}) was {status}.{bal}")

# ---------------------------------------------------------------- helpers
def json_bytes(obj):
    return json.dumps(obj).encode()

class AuthError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message

def client_ip(handler):
    return handler.client_address[0]

def require_email_verified(email):
    u = DB["users"].get(email)
    return bool(u and u.get("verified"))

def public_user(u):
    return {"email": u["email"], "name": u.get("name", ""), "plan": u.get("plan", "Free"),
            "api_key": u.get("api_key"), "created": u.get("created"), "banned": u.get("banned", False),
            "admin": bool(u.get("admin")), "balance": round(u.get("balance", 0), 2),
            "welcome_credit": u.get("welcome_credit")}

# ---------------------------------------------------------------- auth ops
SIGNUP_WINDOW = 3600          # 1 hour
SIGNUP_LIMIT = 3              # accounts per IP per hour
SIGNUP_DAILY = 6              # accounts per IP per day → IP ban beyond
IP_BAN_SECONDS = 86400        # 24 h
FAILED_LIMIT = 8
LOCK_SECONDS = 900            # 15 min
CODE_TTL = 600                # 10 min
SESSION_TTL = 30 * 86400      # 30 days

def prune_ip(db, ip):
    hits = [t for t in db["ip_signups"].get(ip, []) if now() - t < 86400]
    db["ip_signups"][ip] = hits
    return hits

def ip_is_banned(db, ip):
    for b in db["banned_ips"]:
        if b["ip"] == ip and (b.get("until") == 0 or now() < b["until"]):
            return True
    return False

# ------------------------------------------------- signup abuse: mail ảo + Gmail variant + credit
FAKE_MAIL_LIMIT = 3          # lần gửi email ảo trước khi bị cấm nhận code
FAKE_MAIL_BASE = 600         # 10 phút, x2 mỗi lần vi phạm tiếp
FAKE_MAIL_MAX = 86400        # tối đa 24h
SIGNUP_CREDIT = 1.0          # tặng $1 khi tạo account (một lần)
IP_CREDIT_DAILY = 2.0        # trần credit miễn phí mỗi IP mỗi ngày

def email_family(email):
    """Chuẩn hóa: Gmail bỏ dấu chấm + đuôi +alias, googlemail == gmail."""
    e = (email or "").strip().lower()
    local, _, domain = e.partition("@")
    if domain in ("gmail.com", "googlemail.com"):
        domain = "gmail.com"
        local = local.split("+")[0].replace(".", "")
    return local + "@" + domain

def family_taken(fam):
    for e in DB["users"]:
        if email_family(e) == fam:
            return True
    if SQLITE is not None:
        with SQLITE_LOCK:
            for (e,) in SQLITE.execute("SELECT email FROM users"):
                if e and email_family(e) == fam:
                    return True
    return False

def fake_mail_check(handler):
    """Đang bị cấm gửi code vì spam mail ảo? → raise 429."""
    ip = client_ip(handler)
    st = DB.get("fake_mail", {}).get(ip)
    if st and now() < st.get("blocked_until", 0):
        mins = int((st["blocked_until"] - now()) // 60) + 1
        raise AuthError(429, f"Mạng của bạn bị tạm chặn NHẬN MÃ XÁC THỰC do đăng ký lặp lại bằng email ảo. Thử lại sau {mins} phút.")
    return ip

def fake_mail_hit(handler):
    """Ghi nhận 1 lần đăng ký bằng email ảo — vượt ngưỡng thì cấm gửi code (tăng dần)."""
    ip = client_ip(handler)
    st = DB.setdefault("fake_mail", {}).setdefault(ip, {"count": 0, "blocked_until": 0})
    st["count"] = st.get("count", 0) + 1
    if st["count"] >= FAKE_MAIL_LIMIT:
        penalty = min(FAKE_MAIL_BASE * (2 ** (st["count"] - FAKE_MAIL_LIMIT)), FAKE_MAIL_MAX)
        st["blocked_until"] = now() + penalty
        save_db(DB)
        mins = int(penalty // 60)
        raise AuthError(429, f"Phát hiện {st['count']} lần đăng ký bằng email ảo. "
                             f"Mạng của bạn bị CHẶN GỬI MÃ XÁC THỰC trong {mins} phút.")
    save_db(DB)

def grant_signup_credit(u, ip):
    """Tặng $1 credit khi tạo account — trần $2/IP/ngày chống farm."""
    if u.get("admin") or not ip:
        return
    credit = float(SETTINGS.get("signup_credit", 1.0))
    daily = float(SETTINGS.get("ip_credit_daily", 2.0))
    if credit <= 0:
        u["trial_note"] = "Trial credit is disabled by the admin."
        return
    day = time.strftime("%Y-%m-%d")
    cap = DB.setdefault("ip_credit", {}).get(ip)
    if not cap or cap.get("day") != day:
        cap = {"day": day, "total": 0.0}
    if cap["total"] + credit > daily:
        u["trial_note"] = "Free trial credit for this network is used up for today."
        return
    cap["total"] = round(cap["total"] + credit, 2)
    DB.setdefault("ip_credit", {})[ip] = cap
    u["balance"] = round(u.get("balance", 0) + credit, 2)
    u["welcome_credit"] = credit

def do_signup(handler, body):
    if not SETTINGS.get("signup_open", True):
        raise AuthError(503, "Đăng ký tạm đóng — admin đang bảo trì hệ thống.")
    if signup_cap_reached():
        raise signup_cap_error()
    ip = fake_mail_check(handler)   # đang bị cấm gửi code (spam mail ảo)?
    if ip_is_banned(DB, ip):
        raise AuthError(403, "This network is banned from creating accounts (abuse).")
    email = (body.get("email") or "").strip().lower()
    name = (body.get("name") or "").strip()
    password = body.get("password") or ""
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise AuthError(400, "Please enter a valid email address.")
    if "+" in email.split("@")[0]:
        raise AuthError(400, "Plus-addressing is not allowed. Use your base email.")
    if len(name) < 2:
        raise AuthError(400, "Please enter your full name.")
    if len(password) < 6:
        raise AuthError(400, "Password must be at least 6 characters.")
    ok, why = mail_allowed(email)
    if not ok:
        fake_mail_hit(handler)   # đếm lần gửi email ảo — vượt ngưỡng thì CẤM gửi code
        raise AuthError(400, why)

    hits = prune_ip(DB, ip)
    per_hour = sum(1 for t in hits if now() - t < SIGNUP_WINDOW)
    if per_hour >= SIGNUP_LIMIT:
        if per_hour >= SIGNUP_DAILY:
            DB["banned_ips"].append({"ip": ip, "until": now() + IP_BAN_SECONDS,
                                     "reason": "mass signup abuse"})
            save_db(DB)
            raise AuthError(403, "Too many accounts from this network. IP banned for 24 hours.")
        raise AuthError(429, "Too many accounts created from this network. Try again later.")
    if email in DB["users"]:
        raise AuthError(409, "An account with this email already exists. Sign in instead.")
    if family_taken(email_family(email)):
        raise AuthError(409, "An account with this email (or a Gmail variant of it) already exists. Sign in instead.")

    code = f"{secrets.randbelow(1000000):06d}"
    sent = send_code_email(email, code)
    if not sent:
        # dev fallback: surface the code only when mail is not configured
        print(f"[MAIL NOT CONFIGURED] verification code for {email}: {code}")
    DB["pending"][email] = {
        "code_hash": hash_pass(code), "name": name,
        "pass": hash_pass(password), "expires": now() + CODE_TTL,
        "attempts": 0, "ip": ip, "sent": sent, "ts": now(),
    }
    hits.append(now())
    DB["ip_signups"][ip] = hits
    save_db(DB)
    return {"ok": True, "email": email, "sent": sent,
            "dev_code": code if not sent else None}

def do_verify(body):
    email = (body.get("email") or "").strip().lower()
    code = (body.get("code") or "").strip()
    p = DB["pending"].get(email)
    if not p:
        raise AuthError(400, "No pending verification for this email. Sign up again.")
    if now() > p["expires"]:
        del DB["pending"][email]; save_db(DB)
        raise AuthError(400, "Code expired. Sign up again to get a new one.")
    if p["attempts"] >= 6:
        del DB["pending"][email]; save_db(DB)
        raise AuthError(429, "Too many wrong attempts. Sign up again for a new code.")
    p["attempts"] += 1
    if not check_pass(code, p["code_hash"]):
        save_db(DB)
        raise AuthError(400, "Wrong code. Check your email and try again.")
    if signup_cap_reached():
        del DB["pending"][email]
        save_db(DB)
        raise signup_cap_error()
    del DB["pending"][email]
    email_clean = email
    # KHÔNG tự sinh api_key khi verify — khách tạo key bằng nút "Create new secret key"
    DB["users"][email_clean] = {
        "email": email_clean, "name": p["name"], "pass": p["pass"],
        "verified": True, "created": now(), "plan": "Free",
        "banned": False, "provider": "email",
    }
    grant_signup_credit(DB["users"][email_clean], p.get("ip") or "")
    token = secrets.token_urlsafe(32)
    DB["sessions"][token] = {"email": email_clean, "expires": now() + SESSION_TTL}
    save_db(DB)
    return {"ok": True, "token": token, "user": public_user(DB["users"][email_clean])}

def do_resend(body):
    email = (body.get("email") or "").strip().lower()
    p = DB["pending"].get(email)
    if not p:
        raise AuthError(400, "No pending verification for this email.")
    if now() - p.get("last_sent", 0) < 45:
        raise AuthError(429, "Please wait before requesting another code.")
    code = f"{secrets.randbelow(1000000):06d}"
    sent = send_code_email(email, code)
    if not sent:
        print(f"[MAIL NOT CONFIGURED] verification code for {email}: {code}")
    p.update({"code_hash": hash_pass(code), "expires": now() + CODE_TTL,
              "attempts": 0, "sent": sent, "last_sent": now()})
    save_db(DB)
    return {"ok": True, "sent": sent, "dev_code": code if not sent else None}

def do_login(handler, body):
    ip = client_ip(handler)
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    fl = DB["failed_logins"].get(email, {"count": 0, "lock_until": 0})
    if now() < fl.get("lock_until", 0):
        raise AuthError(429, "Too many failed attempts. Try again in a few minutes.")
    u = DB["users"].get(email)
    if not u or not check_pass(password, u["pass"]):
        fl["count"] = fl.get("count", 0) + 1
        if fl["count"] >= FAILED_LIMIT:
            fl["lock_until"] = now() + LOCK_SECONDS
            fl["count"] = 0
        DB["failed_logins"][email] = fl
        save_db(DB)
        raise AuthError(401, "Invalid email or password.")
    if u.get("banned"):
        raise AuthError(403, "This account has been banned for abuse.")
    if not u.get("verified"):
        raise AuthError(403, "Email not verified. Sign up again to receive a new code.")
    DB["failed_logins"].pop(email, None)
    token = secrets.token_urlsafe(32)
    DB["sessions"][token] = {"email": email, "expires": now() + SESSION_TTL}
    save_db(DB)
    return {"ok": True, "token": token, "user": public_user(u)}

def do_me(body):
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u or u.get("banned"):
        raise AuthError(403, "Account unavailable.")
    ensure_keys(u)
    return {"ok": True, "user": public_user(u), "keys": u["keys"]}


def do_newkey(body):
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u or u.get("banned"):
        raise AuthError(403, "Account unavailable.")
    u["api_key"] = gen_api_key()
    save_db(DB)
    return {"ok": True, "api_key": u["api_key"]}

def ensure_keys(u):
    # KHÔNG tự sinh key cho account mới — key chỉ được tạo khi khách bấm
    # "Create new secret key" (do_keycreate) hoặc tự đăng ký qua /v1/auth/register.
    # Legacy: account cũ có api_key nhưng chưa có list keys → bọc lại cho đồng bộ.
    if "keys" not in u:
        created = time.strftime("%Y-%m-%d", time.gmtime(u.get("created", now())))
        u["keys"] = ([{"name": "Default key", "key": u["api_key"],
                       "created": created, "last_used": "Never"}]
                      if u.get("api_key") else [])

def do_keys(body):
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u or u.get("banned"):
        raise AuthError(403, "Account unavailable.")
    ensure_keys(u)
    save_db(DB)
    return {"ok": True, "keys": u["keys"]}

def do_keycreate(body):
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u or u.get("banned"):
        raise AuthError(403, "Account unavailable.")
    ensure_keys(u)
    name = (body.get("name") or "").strip()
    if not name:
        raise AuthError(400, "Please enter a key name.")
    if len(u["keys"]) >= 10:
        raise AuthError(400, "Key limit reached (10). Delete a key first.")
    # prefix theo gói: key của account Pro nhận nhãn sk-nfx-pro-, free là sk-nfx-free-
    prefix = "sk-nfx-pro-" if u.get("plan") == "Pro" else "sk-nfx-free-"
    u["keys"].append({"name": name, "key": gen_api_key(prefix),
                      "created": time.strftime("%Y-%m-%d", time.gmtime()), "last_used": "Never"})
    if not u.get("api_key"):
        u["api_key"] = u["keys"][-1]["key"]
    save_db(DB)
    return {"ok": True, "keys": u["keys"]}

def do_keyrename(body):
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u:
        raise AuthError(403, "Account unavailable.")
    for k in u.get("keys", []):
        if k["key"] == body.get("key"):
            k["name"] = (body.get("name") or "").strip() or k["name"]
            save_db(DB)
            return {"ok": True, "keys": u["keys"]}
    raise AuthError(404, "Key not found.")

def do_keydelete(body):
    token = body.get("token") or ""
    s = DB["sessions"].get(token)
    if not s or now() > s["expires"]:
        raise AuthError(401, "Session expired. Please sign in again.")
    u = DB["users"].get(s["email"])
    if not u:
        raise AuthError(403, "Account unavailable.")
    before = len(u.get("keys", []))
    u["keys"] = [k for k in u.get("keys", []) if k["key"] != body.get("key")]
    save_db(DB)
    return {"ok": True, "deleted": before - len(u["keys"])}

def do_logout(body):
    DB["sessions"].pop(body.get("token") or "", None)
    save_db(DB)
    return {"ok": True}

def do_admin(body, handler):
    return do_admin_action(body, handler)

# ---------------------------------------------------------------- oauth
OAUTH_STATE = {}

def oauth_cfg(provider):
    cfg = load_json_cfg("oauth_config.json") or {}
    c = cfg.get(provider)
    if not c or not c.get("client_id") or not c.get("client_secret"):
        return None
    return c

def oauth_start(provider, base):
    c = oauth_cfg(provider)
    if not c:
        raise AuthError(503, f"{provider.capitalize()} OAuth is not configured yet. Use email sign-up or ask the admin to add data/oauth_config.json.")
    state = secrets.token_urlsafe(16)
    OAUTH_STATE[state] = {"provider": provider, "expires": now() + 600}
    if provider == "google":
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
            "client_id": c["client_id"], "redirect_uri": f"{base}/api/auth/oauth/google/callback",
            "response_type": "code", "scope": "openid email profile",
            "state": state, "prompt": "select_account"})
    else:
        url = "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode({
            "client_id": c["client_id"], "redirect_uri": f"{base}/api/auth/oauth/github/callback",
            "scope": "read:user user:email", "state": state})
    return {"ok": True, "url": url}

def http_post_json(url, data, headers=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def oauth_callback(provider, qs, base, ip=""):
    st = OAUTH_STATE.pop(qs.get("state", [""])[0], None)
    if not st or st["provider"] != provider or now() > st["expires"]:
        raise AuthError(400, "OAuth state invalid or expired. Try again.")
    c = oauth_cfg(provider)
    if not c:
        raise AuthError(503, f"{provider} OAuth is not configured.")
    code = qs.get("code", [""])[0]
    if provider == "google":
        tok = http_post_json("https://oauth2.googleapis.com/token", {
            "code": code, "client_id": c["client_id"], "client_secret": c["client_secret"],
            "redirect_uri": f"{base}/api/auth/oauth/google/callback", "grant_type": "authorization_code"})
        info = http_post_json("https://openidconnect.googleapis.com/v1/userinfo", {},
                              {"Authorization": "Bearer " + tok["access_token"]})
        email, name = info.get("email"), info.get("name") or info.get("email")
    else:
        tok = http_post_json("https://github.com/login/oauth/access_token", {
            "code": code, "client_id": c["client_id"], "client_secret": c["client_secret"],
            "redirect_uri": f"{base}/api/auth/oauth/github/callback"})
        at = tok.get("access_token")
        req = urllib.request.Request("https://api.github.com/user",
                                     headers={"Authorization": "Bearer " + at, "User-Agent": "NFlashX"})
        with urllib.request.urlopen(req, timeout=30) as r:
            info = json.loads(r.read())
        req = urllib.request.Request("https://api.github.com/user/emails",
                                     headers={"Authorization": "Bearer " + at, "User-Agent": "NFlashX"})
        with urllib.request.urlopen(req, timeout=30) as r:
            emails = json.loads(r.read())
        email = next((e["email"] for e in emails if e.get("primary")), emails[0]["email"] if emails else None)
        name = info.get("name") or info.get("login")
    if not email:
        raise AuthError(400, "Could not read your email from the provider.")
    email = email.lower()
    u = DB["users"].get(email)
    if not u:
        if signup_cap_reached():
            raise signup_cap_error()
        u = {"email": email, "name": name or email.split("@")[0], "provider": provider,
             "verified": True, "created": now(), "plan": "Free",
             "banned": False,
             "pass": hash_pass(secrets.token_urlsafe(24))}
        DB["users"][email] = u
        grant_signup_credit(u, ip)   # $1 credit cho user OAuth mới (trần theo IP)
    if u.get("banned"):
        raise AuthError(403, "This account has been banned for abuse.")
    token = secrets.token_urlsafe(32)
    DB["sessions"][token] = {"email": email, "expires": now() + SESSION_TTL}
    save_db(DB)
    return token

# ---------------------------------------------------------------- handler
def scrub_sse_line(line):
    """Loc reasoning_content/provider fields khoi tung dong SSE truoc khi forward."""
    if not line.startswith(b"data:"):
        return line
    raw = line[5:].strip()
    if not raw or raw == b"[DONE]":
        return line
    try:
        d = json.loads(raw)
    except Exception:
        return line
    ch = d.get("choices")
    if isinstance(ch, list):
        for c in ch:
            if not isinstance(c, dict):
                continue
            delta = c.get("delta")
            if isinstance(delta, dict):
                for k in ("reasoning_content", "reasoning", "provider_specific_fields"):
                    delta.pop(k, None)
            c.pop("provider_specific_fields", None)
    return b"data: " + json.dumps(d, ensure_ascii=False).encode() + b"\n\n"

def scrub_upstream(payload):
    """Giữ response sạch: bỏ reasoning_content + provider_specific_fields
    (chain-of-thought tiếng Anh của upstream lộ ra là fingerprint rõ nhất)."""
    try:
        d = json.loads(payload)
    except Exception:
        return payload
    if not isinstance(d, dict):
        return payload
    changed = False
    choices = d.get("choices")
    if isinstance(choices, list):
        for c in choices:
            if not isinstance(c, dict):
                continue
            msg = c.get("message")
            if isinstance(msg, dict):
                for k in ("reasoning_content", "reasoning", "provider_specific_fields"):
                    if k in msg:
                        del msg[k]
                        changed = True
            if "provider_specific_fields" in c:
                del c["provider_specific_fields"]
                changed = True
    return json.dumps(d, ensure_ascii=False).encode() if changed else payload

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def _json(self, obj, status=200):
        payload = json_bytes(obj)
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _redirect(self, to):
        self.send_response(302)
        self._cors()
        self.send_header("Location", to)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _charge_usage(self, usage_user, model, resp_payload, kind="text"):
        """Trừ balance theo usage thật trả về từ upstream (chỉ khi thành công)."""
        try:
            d = json.loads(resp_payload) if resp_payload else {}
            usage = d.get("usage") or {}
            cost = estimate_cost(model or "nflashx-1.0-flash", usage, kind)
            if cost <= 0 or not usage_user:
                return
            email = usage_user.get("email")
            u = DB["users"].get(email)
            if u is None:                      # user self-serve chỉ có SQLite
                u = {"email": email, "balance": 0}
                DB["users"][email] = u
            u["balance"] = round(u.get("balance", 0) - cost, 6)
            u["charged_total"] = round(u.get("charged_total", 0) + cost, 6)
            u.setdefault("charged_history", []).append(
                {"ts": now(), "model": model, "cost": round(cost, 6),
                 "in": usage.get("prompt_tokens"), "out": usage.get("completion_tokens")})
            del u["charged_history"][:-200]     # giữ 200 bản ghi gần nhất
            save_db(DB)
        except Exception as e:
            print("[charge] error:", e)

    def _proxy(self, upstream_path, body=None, method="POST", usage_user=None, model=None, kind="text"):
        is_stream = False
        if body:
            try:
                is_stream = bool(json.loads(body).get("stream"))
            except Exception:
                is_stream = b'"stream":true' in body.replace(b" ", b"").lower()
        attempt_keys = agnes_key_order() or [API_KEY]
        payload, status, ctype = b"{}", 502, "application/json"
        for idx, key in enumerate(attempt_keys):
            headers = {"Authorization": f"Bearer {key}",
                       "Content-Type": "application/json", "Accept": "application/json"}
            req = urllib.request.Request(UPSTREAM + upstream_path, data=body,
                                         headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    ctype_u = r.headers.get("Content-Type", "application/json")
                    if r.status == 200 and is_stream and "event-stream" in (ctype_u or ""):
                        # ---- streaming passthrough: day tung dong SSE ve client ngay ----
                        self.send_response(200)
                        self._cors()
                        self.send_header("Content-Type", "text/event-stream")
                        self.send_header("Cache-Control", "no-cache")
                        self.send_header("X-Accel-Buffering", "no")
                        self.end_headers()
                        try:
                            buf = b""
                            while True:
                                chunk = r.read1(4096)
                                if not chunk:
                                    break
                                buf += chunk
                                while b"\n" in buf:
                                    line, buf = buf.split(b"\n", 1)
                                    self.wfile.write(scrub_sse_line(line) + b"\n")
                                self.wfile.flush()
                            if buf:
                                self.wfile.write(scrub_sse_line(buf))
                                self.wfile.flush()
                        except Exception:
                            pass
                        _AGNES_USAGE[key] = _AGNES_USAGE.get(key, 0) + 1
                        return
                    payload, status, ctype = r.read(), r.status, ctype_u
            except urllib.error.HTTPError as e:
                payload, status, ctype = e.read(), e.code, "application/json"
            except Exception as e:
                payload = json.dumps({"error": str(e)}).encode()
                status, ctype = 502, "application/json"
            _AGNES_USAGE[key] = _AGNES_USAGE.get(key, 0) + 1
            if status in (401, 402, 429) and idx < len(attempt_keys) - 1:
                agnes_key_penalize(key, status)   # key chết/limit -> thử key kế
                continue
            break
        if 200 <= status < 300:
            payload = scrub_upstream(payload)
        if 200 <= status < 300 and usage_user:
            self._charge_usage(usage_user, model, payload, kind)
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _canonical_redirect(self):
        """URL instabox dai -> tu nhay sang base URL chinh thuc (GET/HEAD only;
        POST giu nguyen de API client va panel khong bi doi method)."""
        fwd = (self.headers.get("X-Forwarded-Host") or "").lower()
        via_proxy = self.headers.get("X-NFX-Proxy") == "1"
        if "instabox.tech" in fwd and not via_proxy and self.command in ("GET", "HEAD"):
            self.send_response(302)
            self.send_header("Location", "https://api.nflashx.workers.dev" + self.path)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        return False

    def public_base(self):
        """Base URL cong khai: uu tien host goc ma browser dung (worker forward qua X-Original-Host)."""
        orig = (self.headers.get("X-Original-Host") or "").split(",")[0].strip()
        xfh = (self.headers.get("X-Forwarded-Host") or "").split(",")[0].strip()
        host = orig or xfh or (self.headers.get("Host") or "").strip()
        if not host or host.startswith("127.0.0.1") or host.startswith("localhost"):
            return f"http://127.0.0.1:{PORT}"
        return "https://" + host

    def do_GET(self):
        if self._canonical_redirect():
            return
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)

        if u.path.startswith("/api/auth/oauth/") and u.path.endswith("/callback"):
            provider = u.path.split("/")[-2]
            try:
                token = oauth_callback(provider, q, self.public_base(), client_ip(self))
                self._redirect(f"/auth-callback.html?token={token}")
            except AuthError as e:
                self._redirect(f"/auth-callback.html?error={urllib.parse.quote(e.message)}")
            return

        if u.path == "/api/auth/oauth/google/start":
            try:
                self._json(oauth_start("google", self.public_base()))
            except AuthError as e:
                self._json({"error": e.message}, e.status)
            return
        if u.path == "/api/auth/oauth/github/start":
            try:
                self._json(oauth_start("github", self.public_base()))
            except AuthError as e:
                self._json({"error": e.message}, e.status)
            return

        if u.path.startswith("/api/paypal/return"):
            rid = q.get("rid", [""])[0]
            result = do_paypal_return(rid)
            self._redirect(f"/platform.html?pay={result}#balance")
            return
        if u.path.startswith("/api/paypal/cancel"):
            self._redirect("/platform.html?pay=cancel#balance")
            return
        if u.path.startswith("/api/video-status/"):
            vid = u.path.rsplit("/", 1)[1]
            self._proxy(f"/agnesapi?video_id={vid}&model_name=agnes-video-2.5-flash", method="GET")
            return
        super().do_GET()

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        body = self._read_body()

        # maintenance mode: chặn mọi API trừ admin (admin console vẫn điều khiển được)
        if SETTINGS.get("maintenance") and not (u.path.startswith("/api/admin") or u.path.startswith("/api/auth/admin")):
            self._json({"error": "Hệ thống đang bảo trì. Vui lòng thử lại sau ít phút."}, 503)
            return

        auth_routes = {
            "/api/auth/signup": lambda: do_signup(self, body),
            "/api/auth/verify": lambda: do_verify(body),
            "/api/auth/resend": lambda: do_resend(body),
            "/api/auth/login": lambda: do_login(self, body),
            "/api/auth/me": lambda: do_me(body),
            "/api/auth/logout": lambda: do_logout(body),
            "/api/auth/newkey": lambda: do_newkey(body),
            "/api/auth/keys": lambda: do_keys(body),
            "/api/auth/keys/create": lambda: do_keycreate(body),
            "/api/auth/keys/rename": lambda: do_keyrename(body),
            "/api/auth/keys/delete": lambda: do_keydelete(body),
            "/api/auth/admin/ban": lambda: do_admin(body, self),
            "/api/auth/set-password": lambda: do_set_password(body),
            "/api/auth/delete-account": lambda: do_delete_account(body),
            "/api/auth/reset-request": lambda: do_reset_request(body, self),
            "/api/auth/reset-confirm": lambda: do_reset_confirm(body),
            "/api/auth/recharge-request": lambda: do_recharge_request(body),
            "/api/auth/recharge-status": lambda: do_recharge_status(body),
            "/api/auth/topup-txid": lambda: do_topup_txid(body),
            "/api/auth/paypal-create": lambda: do_paypal_create(body, self),
            "/api/auth/paypal-client": lambda: do_paypal_client(body),
            "/api/auth/paypal-sdk-create": lambda: do_paypal_sdk_create(body, self),
            "/api/auth/paypal-sdk-capture": lambda: do_paypal_sdk_capture(body),
            "/api/auth/pricing": lambda: do_api_pricing(body),
            "/api/auth/my-billing": lambda: do_my_billing(body),
            "/api/auth/usage": lambda: do_usage(body),
            "/api/auth/announcements": lambda: {"ok": True, "announcements": DB.get("announcements", [])[:10]},
            "/api/admin/users": lambda: do_admin_users(body, self),
            "/api/admin/stats": lambda: do_admin_stats(body, self),
            "/api/admin/topups": lambda: do_admin_topups(body, self),
            "/api/admin/payment-cfg": lambda: do_admin_action(dict(body, action="payment-cfg"), self),
            "/api/admin/paypal-cfg": lambda: do_admin_action(dict(body, action="paypal-cfg"), self),
            "/api/admin/settings": lambda: do_admin_settings(body, self),
            "/api/admin/agnes-keys": lambda: do_admin_agnes_keys(body, self),
            "/api/admin/announce": lambda: do_admin_announce(body, self),
            "/api/admin/ipbans": lambda: do_admin_ipbans(body, self),
            "/api/admin/user-detail": lambda: do_admin_user_detail(body, self),
            "/api/admin/server-restart": lambda: do_admin_server_restart(body, self),
            "/api/admin/clear": lambda: do_admin_clear(body, self),
        }
        if u.path in auth_routes:
            try:
                self._json(auth_routes[u.path]())
            except AuthError as e:
                self._json({"error": e.message}, e.status)
            except Exception as e:
                self._json({"error": f"Server error: {e}"}, 500)
            return

        # ---------------- webhook ngân hàng (Casso/Sepay) → tự credit ----------------
        if u.path in ("/api/webhook/bank", "/webhook/bank"):
            try:
                self._json(do_admin_webhook_sim(body, self))
            except AuthError as e:
                self._json({"error": e.message}, e.status)
            except Exception as e:
                self._json({"error": f"Server error: {e}"}, 500)
            return

        # ---------------- self-serve registration (no login needed) ----------------
        if u.path == "/v1/auth/register":
            try:
                self._json(do_register(body))
            except AuthError as e:
                self._json({"error": e.message}, e.status)
            except Exception as e:
                self._json({"error": f"Server error: {e}"}, 500)
            return

        # ---------------- developer API: Bearer key + per-key rate limit ----------------
        if u.path in ("/v1/chat/completions", "/v1/images/generations"):
            auth = self.headers.get("Authorization") or ""
            key = auth[7:].strip() if auth.startswith("Bearer ") else ""
            try:
                usage = check_api_key(key, endpoint=u.path, ip=client_ip(self))
            except AuthError as e:
                self._json({"error": e.message}, e.status)
                return
            except Exception as e:
                self._json({"error": f"Server error: {e}"}, 500)
                return
            req_model = body.get("model") if isinstance(body, dict) else None
            if req_model in PRO_MODELS and usage.get("tier", "free") != "pro" and SETTINGS.get("pro_gate", True):
                self._json({"error": "Model nflashx-1.0-pro requires a Pro-tier API key (free keys get HTTP 403). "
                                    "Upgrade your account tier in the API Platform to call it."}, 403)
                return
            upstream = "/v1/chat/completions" if u.path.endswith("/chat/completions") else "/v1/images/generations"
            if upstream == "/v1/chat/completions":
                # PRO model hiện CHẠY Y HỆT FLASH: cùng cap 4096 + cùng persona.
                # (chưa bung full power — khi bán mạnh sẽ đổi lại theo tier:
                #  body = apply_tier_policy(body, usage.get("tier", "free")))
                body = apply_tier_policy(body, "free")
            try:
                obj = body
                mapped = MODEL_MAP.get(obj.get("model"))
                if mapped:
                    obj["model"] = mapped
            except Exception:
                pass
            if not isinstance(body, (bytes, bytearray)):
                body = json.dumps(body if isinstance(body, dict) else {}).encode()
            _m = None
            try:
                _m = json.loads(body).get("model")
            except Exception:
                pass
            _kind = "image" if upstream.endswith("generations") else "text"
            # model goc (ten thuong hieu) de tra gia
            _orig = req_model or _m or "nflashx-1.0-flash"
            if _orig.startswith("n-flashx"):
                _orig = "nflashx" + _orig[len("n-flashx"):]
            self._proxy(upstream, body, usage_user=usage, model=_orig, kind=_kind)
            return

        for local, upstream in ROUTES.items():
            if self.path.startswith(local):
                try:
                    if local == "/api/chat" and isinstance(body, dict):
                        if body.get("model") in PRO_MODELS:
                            self._json({"error": "Model nflashx-1.0-pro requires a Pro-tier API key."}, 403)
                            return
                        body = apply_tier_policy(body, "free")   # browser route: chinh sach free
                    if local == "/api/images":
                        vision_allow(self, body)                 # 3 lan/login + 3 lan/IP/ngay
                    if local == "/api/videos" and isinstance(body, dict):
                        body = video_defaults(body)              # dien mode/seconds/size mac dinh
                except AuthError as e:
                    self._json({"error": e.message}, e.status)
                    return
                try:
                    obj = body
                    mapped = MODEL_MAP.get(obj.get("model"))
                    if mapped:
                        obj["model"] = mapped
                        body = json.dumps(obj).encode()
                except Exception:
                    pass
                self._proxy(upstream, body)
                return
        self.send_error(404, "unknown api route")


if __name__ == "__main__":
    init_sqlite()
    load_settings()
    reload_agnes_keys()
    if not API_KEY:
        print("[!] AGNES_KEY is not set — upstream API calls will fail with 401. "
              "Set the AGNES_KEY environment variable before starting the server.")
    if not ADMIN_KEY:
        print("[!] ADMIN_KEY is not set — Admin Console login will fail. "
              "Set the ADMIN_KEY environment variable before starting the server.")
    print(f"NFlashX server -> http://127.0.0.1:{PORT}  (static + API proxy + auth)")
    print(f"  db: {DB_PATH}")
    print(f"  sqlite (self-serve + usage): {SQLITE_PATH}")
    print(f"  mail: {'configured' if load_json_cfg('mail_config.json') else 'NOT configured (dev codes printed to console)'}")
    print(f"  oauth: {'configured' if load_json_cfg('oauth_config.json') else 'NOT configured'}")
    BIND = os.environ.get("BIND", "127.0.0.1")   # serv00/VPS: BIND=0.0.0.0
ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
