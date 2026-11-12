# NFlashX 1.0

**One API key for Text · Image · Video.**
An OpenAI-compatible multimodal AI API, built by [NowayDev](https://nflashx.cc.cd).

[![Live](https://img.shields.io/badge/Live-nflashx.cc.cd-8b5cf6)](https://nflashx.cc.cd)
[![Docs](https://img.shields.io/badge/Docs-API%20Reference-22d3ee)](https://nflashx.cc.cd/docs.html)
[![Platform](https://img.shields.io/badge/Platform-API%20Keys%20%26%20Billing-34d399)](https://nflashx.cc.cd/platform.html)

---

## What is NFlashX?

NFlashX 1.0 is a self-hosted, OpenAI-compatible API that serves **chat, image generation and video** through a single key — with a free tier, prepaid billing and an upstream key pool that rotates automatically.

| | |
|---|---|
| 🌐 Live site | **https://nflashx.cc.cd** |
| 📚 Docs & API reference | **https://nflashx.cc.cd/docs.html** |
| 🔑 Platform (keys, balance, usage) | **https://nflashx.cc.cd/platform.html** |
| 💬 Chat playground | **https://nflashx.cc.cd/chat.html** |
| 🖼 Vision playground | **https://nflashx.cc.cd/playground.html** |

---

## Features

- **OpenAI-compatible endpoints** — `/v1/chat/completions`, `/v1/images/generations`, `/v1/videos` (task API)
- **Free tier** — 2 requests/min, 4K output tokens, **$1 credit on signup** (first 100 accounts)
- **Pro tier** — 30 requests/min, 8K output, pay-as-you-go at $0.40 / $0.70 per 1M tokens
- **Upstream key pool** — round-robin rotation on every request, automatic cooldown + failover on 401 / 402 / 429
- **True streaming** — SSE passthrough, first token in ~1s; upstream reasoning traces are filtered out
- **Billing built in** — USD balance, usage metering, VietQR / USDT (TRC20) / PayPal top-ups, manual review
- **Auth** — email + verification code, Google OAuth, GitHub OAuth, persistent sessions
- **Zero dependencies** — one Python file (`server.py`), stdlib only

---

## Quickstart

```bash
curl https://nflashx.cc.cd/v1/chat/completions \
  -H "Authorization: Bearer nfx-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nflashx-1.0-flash",
    "messages": [{"role": "user", "content": "Hello NFlashX!"}]
  }'
```

Streaming:

```bash
curl -N https://nflashx.cc.cd/v1/chat/completions \
  -H "Authorization: Bearer nfx-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nflashx-1.0-flash",
    "stream": true,
    "messages": [{"role": "user", "content": "Explain SSE in one sentence."}]
  }'
```

Get a key: [platform.html](https://nflashx.cc.cd/platform.html) → **Create new secret key**.

---

## Models & pricing

| Model | ID | Output | Rate limit | Price (per 1M tokens) |
|---|---|---|---|---|
| NFlashX 1.0 Flash | `nflashx-1.0-flash` | 4K | 2 req/min (free) | $0.10 in / $0.15 out |
| NFlashX 1.0 Pro | `nflashx-1.0-pro` | 8K | 30 req/min | $0.40 in / $0.70 out |
| NFlashX Vision 1.0 Flash | `nflashx-vision-1.0-flash` | image | — | $0.01 / image |
| NFlashX Motion 1.0 | `nflashx-motion-1.0` | video | — | $0.025 / second |

- New accounts: **$1.00** welcome credit (capped at $2/day per IP, anti-abuse)
- Launch window: the first **100 accounts**

---

## Architecture

```text
Browser / SDK
      │  HTTPS
      ▼
Cloudflare Worker  (custom domain: nflashx.cc.cd, TLS, 302 for legacy hosts)
      │  fetch with X-Original-Host / X-NFX-Proxy
      ▼
InstaBox microVM   (nflashx.cc.cd origin, 4 vCPU / 8 GB)
      │
      ├── server.py — static site + auth + billing + API proxy
      │      │  key pool (round-robin, cooldown, failover)
      │      ▼
      └── Upstream AI API (agnes-2.5-flash engine)
```

- **Keep-alive**: a Cloudflare Worker cron recycles the free-tier VM before its max-run limit (`suspend → resume`, no cooldown).
- **Key pool**: every request picks the next key; failing keys get a cooldown (401 → 1h, 402 → 10m, 429 → 2m) and the request retries on the next key.

---

## Repository layout

```text
nflashx/
├── server.py               # entire backend (stdlib only)
├── index.html              # landing (5-slide deck)
├── docs.html + js/docs.js  # API documentation
├── platform.html           # dashboard: keys, balance, usage, top-ups
├── chat.html               # chat playground
├── playground.html         # vision playground
├── login.html              # signup / login (email, Google, GitHub)
├── css/                    # styles.css + landing.css + docs-override.css
├── js/                     # app.js, docs.js, auth-modal.js
├── assets/                 # logo, artwork, galleries
├── robots.txt / sitemap.xml
└──     # legacy tray control app
```

---

## Self-hosting

1. Create `secrets.env` (gitignored):

```bat
set AGNES_KEY=sk-...
set ADMIN_KEY=nfx-admin-...
```

2. Run:

```bash
python server.py            # serves http://127.0.0.1:8600
```

Optional: `data/` holds runtime state (created automatically):

| File | Purpose |
|---|---|
| `data/db.json` | users, sessions, top-ups, IP stats |
| `data/nflashx.db` | SQLite: API keys + usage log |
| `data/admin_settings.json` | runtime settings (rate limits, caps, personas) |
| `data/agnes_keys.json` | upstream key pool |
| `data/payment_config.json` / `paypal_config.json` | payout accounts (set via dashboard) |
| `data/mail_config.json` | SMTP for notifications |

---

## License

© 2026 **NowayDev** — All rights reserved.
NFlashX and the NFlashX logo are trademarks of NowayDev.
