# NFlashX 1.0

**One API key. Text · Image · Video.**
A multimodal AI API with a free tier, prepaid billing and an OpenAI-compatible interface — built and operated by **NowayDev**.

[![Live](https://img.shields.io/badge/Live-nflashx.cc.cd-8b5cf6)](https://nflashx.cc.cd)
[![Docs](https://img.shields.io/badge/Docs-API%20Reference-22d3ee)](https://nflashx.cc.cd/docs.html)
[![Platform](https://img.shields.io/badge/Platform-Keys%20%26%20Billing-34d399)](https://nflashx.cc.cd/platform.html)
[![API Version](https://img.shields.io/badge/API-v1-a78bfa)](https://nflashx.cc.cd/docs.html)
[![License](https://img.shields.io/badge/License-Proprietary-9ca3b8)](./README.md#license)

---

## Live

| | |
|---|---|
| 🌐 Website | **https://nflashx.cc.cd** |
| 📚 Docs & API reference | **https://nflashx.cc.cd/docs.html** |
| 🔑 Platform — keys, balance, usage | **https://nflashx.cc.cd/platform.html** |
| 🔒 Terms & Privacy | [docs.html?tab=legal](https://nflashx.cc.cd/docs.html?tab=legal) |

---

## Why developers choose NFlashX

- **One key, three modalities** — chat, image generation and video through a single OpenAI-compatible API
- **Drop-in compatible** — works with the official OpenAI SDKs; change `base_url` and keep your code
- **Streaming by default** — server-sent events, first token in about a second
- **Free to start** — 2 requests/min, 4K output, **$1 credit on signup**, no credit card required
- **Clear pricing** — prepaid USD balance, per-token billing, no subscriptions, no surprise fees
- **Your choice of payment** — VietQR (VND), USDT (TRC20) or PayPal
- **Versioned API** — every endpoint lives under `/v1`; breaking changes ship under a new version

---

## Quickstart

1. Create a key in the [Platform](https://nflashx.cc.cd/platform.html) → **Create new secret key**
2. Call the API:

```bash
curl https://nflashx.cc.cd/v1/chat/completions \
  -H "Authorization: Bearer nfx-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nflashx-1.0-flash",
    "messages": [{"role": "user", "content": "Hello NFlashX!"}]
  }'
```

3. Add `"stream": true` to the JSON body to receive server-sent events instead of a single response.

### Image generation

```bash
curl https://nflashx.cc.cd/v1/images/generations \
  -H "Authorization: Bearer nfx-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nflashx-vision-1.0-flash",
    "prompt": "A glass cube on a white studio background, soft shadows, high detail",
    "size": "1024x768"
  }'
```

### Video generation — coming soon

Video generation ships through an asynchronous task API (`POST /v1/videos`, then poll the task). The endpoint is documented ahead of launch in the [docs](https://nflashx.cc.cd/docs.html) and will be enabled for all accounts with API access.

**Python / Node:** the official OpenAI SDK works out of the box — set `base_url="https://nflashx.cc.cd/v1"`.

---

## Models

| Model | ID | Output | Rate limit | Status |
|---|---|---|---|---|
| NFlashX 1.0 Flash | `nflashx-1.0-flash` | 4K | 2 req/min (free) | **Generally available** |
| NFlashX 1.0 Pro | `nflashx-1.0-pro` | 8K | 30 req/min | **Generally available** |
| NFlashX Vision 1.0 Flash | `nflashx-vision-1.0-flash` | image | — | **Generally available** |
| NFlashX Motion 1.0 | `nflashx-motion-1.0` | video | — | **Coming soon** |

---

## Pricing

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| NFlashX 1.0 Flash | $0.10 | $0.15 |
| NFlashX 1.0 Pro | $0.40 | $0.70 |
| NFlashX Vision 1.0 Flash | $0.01 / image | — |
| NFlashX Motion 1.0 | Pricing announced at launch | — |

- New accounts receive **$1.00** welcome credit (capped per network, anti-abuse)
- Launch window: the first **100 accounts**
- Billing is prepaid: your balance is charged per request; current rates are always listed on the [Pricing docs](https://nflashx.cc.cd/docs.html?tab=pricing)

---

## Reliability & security

- **HTTPS only** — all endpoints are served over TLS
- **Key control** — keys can be created and revoked at any time from your [Platform](https://nflashx.cc.cd/platform.html)
- **Isolated rate limits** — per-key limits protect shared capacity; limits are published above and enforced with clear `429` responses
- **Transparent status** — usage, spend and request history are visible in real time on your dashboard
- **Versioned contract** — `/v1` is stable; changes are additive and documented

---

## Support

- 📖 **[Documentation](https://nflashx.cc.cd/docs.html)** — endpoints, parameters, error codes, examples
- ✉️ **Email** — hoanghaiminh2004@gmail.com
- 🔒 **[Terms & Privacy](https://nflashx.cc.cd/docs.html?tab=legal)**

---

## License

© 2026 **NowayDev** — All rights reserved.
NFlashX and the NFlashX logo are trademarks of NowayDev.
