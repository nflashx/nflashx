# NFlashX 1.0

**One API key. Text · Image · Video.**
A multimodal AI API with a free tier, prepaid billing and an OpenAI-compatible interface — by NowayDev.

[![Live](https://img.shields.io/badge/Live-nflashx.cc.cd-8b5cf6)](https://nflashx.cc.cd)
[![Docs](https://img.shields.io/badge/Docs-API%20Reference-22d3ee)](https://nflashx.cc.cd/docs.html)
[![Platform](https://img.shields.io/badge/Platform-Keys%20%26%20Billing-34d399)](https://nflashx.cc.cd/platform.html)

---

## Live

| | |
|---|---|
| 🌐 Website | **https://nflashx.cc.cd** |
| 📚 Docs & API reference | **https://nflashx.cc.cd/docs.html** |
| 🔑 Platform — keys, balance, usage | **https://nflashx.cc.cd/platform.html** |
| 💬 Chat playground | **https://nflashx.cc.cd/chat.html** |
| 🖼 Vision playground | **https://nflashx.cc.cd/playground.html** |

---

## Why NFlashX

- **One key, three modalities** — chat, image generation and video through the same OpenAI-compatible API
- **Free to start** — 2 requests/min, 4K output tokens, **$1 credit on signup**, no credit card
- **Streaming** — server-sent events, first token in about a second
- **Prepaid, transparent** — USD balance, per-token pricing, no subscriptions
- **Top up your way** — VietQR (VND), USDT (TRC20) or PayPal
- **Sign in your way** — email, Google or GitHub

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

Any OpenAI-compatible SDK works — point `base_url` at `https://nflashx.cc.cd/v1`.

Get a key: [platform.html](https://nflashx.cc.cd/platform.html) → **Create new secret key**.

---

## Models & pricing

| Model | ID | Output | Rate limit | Price (per 1M tokens) |
|---|---|---|---|---|
| NFlashX 1.0 Flash | `nflashx-1.0-flash` | 4K | 2 req/min (free) | $0.10 in / $0.15 out |
| NFlashX 1.0 Pro | `nflashx-1.0-pro` | 8K | 30 req/min | $0.40 in / $0.70 out |
| NFlashX Vision 1.0 Flash | `nflashx-vision-1.0-flash` | image | — | $0.01 / image |
| NFlashX Motion 1.0 | `nflashx-motion-1.0` | video | — | $0.025 / second |

- New accounts receive **$1.00** welcome credit (capped per network, anti-abuse)
- Launch window: the first **100 accounts**

---

## Links

- Website — https://nflashx.cc.cd
- Docs — https://nflashx.cc.cd/docs.html
- Platform — https://nflashx.cc.cd/platform.html

---

## License

© 2026 **NowayDev** — All rights reserved.
NFlashX and the NFlashX logo are trademarks of NowayDev.
