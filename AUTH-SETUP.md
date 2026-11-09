# NFlashX Auth — Setup Guide (email verification + real Google/GitHub login)

Server auth is fully implemented in `server.py`. Two integrations need your own
credentials (nobody can create these for you — they are tied to your accounts).

---

## 1. Real verification emails (SMTP)

Sign-up sends a real 6-digit code by email. Configure any SMTP inbox —
**Gmail with an App Password is the easiest**:

1. Enable 2-Step Verification on your Google account:
   https://myaccount.google.com/security
2. Create an App Password: https://myaccount.google.com/apppasswords
   (select "Mail" → copy the 16-character password)
3. Create `nflashx/data/mail_config.json`:

```json
{
  "enabled": true,
  "host": "smtp.gmail.com",
  "port": 465,
  "user": "yourgmail@gmail.com",
  "pass": "your-16-char-app-password",
  "from": "NFlashX <yourgmail@gmail.com>"
}
```

Restart `python server.py`. Test sign-up → the code arrives in the real inbox.

> Any other SMTP provider works too (Outlook, Zoho, Brevo, Mailgun SMTP…).
> While mail is NOT configured, the server falls back to DEV MODE: the code is
> printed in the server console and shown in the UI, clearly marked.

---

## 2. Real Google login (OAuth)

1. Open https://console.cloud.google.com/apis/credentials → **Create credentials → OAuth client ID**
2. Application type: **Web application**
3. Authorized redirect URIs — add exactly:
   ```
   http://127.0.0.1:8600/api/auth/oauth/google/callback
   ```
4. Copy the **Client ID** and **Client secret**.
5. Create `nflashx/data/oauth_config.json`:

```json
{
  "google":  { "client_id": "XXXX.apps.googleusercontent.com", "client_secret": "GOCSPX-..." },
  "github":  { "client_id": "", "client_secret": "" }
}
```

Restart the server. "Continue with Google" now redirects to the real Google
login page and returns a real account.

---

## 3. Real GitHub login (OAuth)

1. Open https://github.com/settings/developers → **New OAuth App**
2. Homepage URL: `http://127.0.0.1:8600`
3. Authorization callback URL — add exactly:
   ```
   http://127.0.0.1:8600/api/auth/oauth/github/callback
   ```
4. Copy **Client ID** → generate a **Client secret**.
5. Fill them into the same `data/oauth_config.json` (github section above).

---

## 4. Anti-abuse (already active, no config needed)

| Rule | Value |
|---|---|
| Disposable / temp email domains | blocked (built-in list + pattern check in `server.py`) |
| `+` alias addresses (user+spam@) | blocked at sign-up |
| Sign-ups per IP | 3 / hour, 6 / day |
| IP abuse | automatic 24 h ban (mass sign-up) |
| Failed logins per account | 8 → 15 min lock |
| Account ban | set `"banned": true` in `data/db.json`, or: |
| Admin ban API | `POST /api/auth/admin/ban` with `{"email":"...","admin_key":"..."}` and header `X-Admin-Key` is not used — put the key in the body; default admin key: `change-me-admin` (change via env `NFLASHX_ADMIN_KEY`) |

All state lives in `nflashx/data/db.json` — accounts survive restarts.

---

## 5. Endpoints (for reference)

| Endpoint | Body | Purpose |
|---|---|---|
| POST `/api/auth/signup` | name, email, password | create pending account, email code |
| POST `/api/auth/verify` | email, code | verify code → account + session token |
| POST `/api/auth/resend` | email | new code (45 s cooldown) |
| POST `/api/auth/login` | email, password | session token |
| POST `/api/auth/me` | token | user + api_key |
| POST `/api/auth/newkey` | token | regenerate api_key |
| POST `/api/auth/logout` | token | destroy session |
| GET `/api/auth/oauth/google/start` | — | real Google redirect |
| GET `/api/auth/oauth/github/start` | — | real GitHub redirect |
