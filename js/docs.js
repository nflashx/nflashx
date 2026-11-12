/* ============================================================
   NFlashX Docs — content router (brand-style docs)
   Sidebar groups collapse; clicking a group reveals its models.
   ============================================================ */
/* Real platform base URL — examples are copy-paste ready */
const API_BASE = "https://nflashx.cc.cd";   // base URL chinh thuc (custom domain)   // base URL chinh thuc (worker proxy)

const MODELS = {
  text: [
    { id: 'nflashx-1.0-flash', name: 'NFlashX 1.0 Flash', kind: 'text',
      lede: 'Fast, cost-efficient model for coding, agent workflows, tool calling, and multimodal understanding.',
      release: 'Generally available to users with NFlashX API access.',
      upgrade: 'Initial release of the NFlashX 1.0 series — no prior migration needed.' },
    { id: 'nflashx-1.0-pro', name: 'NFlashX 1.0 Pro', kind: 'text',
      lede: 'Pro-tier model for advanced coding, scientific reasoning, long-context analysis, and agentic workflows.',
      release: 'Generally available to Pro-tier API keys. Free keys receive HTTP 403 with upgrade instructions.',
      upgrade: 'API-compatible upgrade from the nflashx-1.0-flash model — change one line to move up.' },
  ],
  image: [
    { id: 'nflashx-vision-1.0-flash', name: 'NFlashX Vision 1.0 Flash', kind: 'image',
      lede: 'Fast text-to-image generation and image editing with high aesthetic quality.',
      release: 'Generally available to users with NFlashX API access.',
      upgrade: 'Initial release of the NFlashX Vision series.' },
  ],
  video: [
    { id: 'nflashx-motion-1.0', name: 'NFlashX Motion 1.0', kind: 'video', soon: true,
      lede: 'Cinematic-quality video with synchronized audio, generated at high speed through an asynchronous task API.',
      release: 'Coming soon — the model is not yet publicly available.',
      upgrade: 'Initial release of the NFlashX Motion series.' },
  ],
};

const PAGES = {
  overview: {
    title: 'NFlashX API Overview',
    lede: 'The NFlashX API gives you programmatic access to our full-stack multimodal models — text, image, and video — through OpenAI-compatible endpoints.',
    toc: ['1. NFlashX API Introduction', '2. Core Capabilities', '3. Model Capabilities Overview', '4. API Compatibility', '5. Base URL', '6. Authentication', '7. Security Notice', '8. Quick Start', '9. Applicable Development Scenarios', '10. Documentation Notes'],
    body: `
      <h2>1. NFlashX API Introduction</h2>
      <p>NFlashX provides multiple types of model capabilities, including text models, image models, video models, and multimodal models designed for reasoning, creative generation, and production application scenarios.</p>
      <p>These models help developers quickly integrate a complete AI capability stack, from content understanding and text generation to image generation, image editing, and video generation.</p>
      <h2>4. API Compatibility</h2>
      <p>NFlashX API is compatible with OpenAI-style interfaces. If you have already used an OpenAI-compatible API, you usually only need to modify the following configurations:</p>
      <p><span class="code-inline">Base_URL</span> &nbsp; <span class="code-inline">API_Key</span> &nbsp; <span class="code-inline">Model_Name</span></p>
      <h2>5. Base URL</h2>
      <div class="codeblock"><button class="copy-btn" data-copy="${API_BASE}/v1">⧉</button><pre>${API_BASE}/v1</pre></div>
      <h2>8. Quick Start</h2>
      <p>Send your first request in under a minute — see the Quickstart page in the sidebar.</p>
      <h2>9. Applicable Development Scenarios</h2>
      <p>AI chat applications · AI search and research tools · AI writing and office productivity tools · AI image generation tools · AI video generation tools · Agent automation platforms · Creative content production platforms · Education, entertainment, e-commerce, and marketing tools.</p>
      <h2>10. Documentation Notes</h2>
      <p>This document helps developers quickly understand the basic capabilities, integration methods, and usage guidelines of NFlashX API. For detailed model parameters, request examples, response formats, and error code descriptions, please refer to the corresponding model-specific integration documents.</p>
      <div class="next-link"><a href="#quickstart">Quickstart <span>›</span></a></div>`
  },
  quickstart: {
    title: 'Quickstart',
    lede: 'Get up and running with the NFlashX API in minutes.',
    toc: ['1. Get your API Key', '2. Set up Authentication', '3. Make your First Request', '4. Next Steps'],
    body: `
      <h2>1. Get your API Key</h2>
      <p>Create a secret key from your platform dashboard. 2. Connect to NFlashX omnimodal free models. 3. Start exploring.</p>
      <h2>3. Make your First Request</h2>
      <div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> ${API_BASE}/v1/chat/completions \\
  -H <span class="c-str">"Content-Type: application/json"</span> \\
  -H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\
  -d <span class="c-str">'{
    "model": "nflashx-1.0-flash",
    "messages": [
      { "role": "user", "content": "Hello NFlashX!" }
    ]
  }'</span></pre></div>
      <div class="callout"><span class="ic">💡</span><div>Replace <span class="code-inline red">YOUR_API_KEY</span> with your actual API key before running the request. A successful response will return a chat completion that matches your input.</div></div>
      <h2>4. Next Steps</h2>
      <p>After your first request, explore these next steps to get more out of the NFlashX API:</p>
      <p>• Read the documentation for request parameters, response formats, and error handling for each API endpoint.<br>• Integrate advanced features like streaming responses or tool calling to enhance your application's functionality.</p>
      <div class="next-link"><a href="#m=nflashx-1.0-flash">NFlashX 1.0 Flash <span>›</span></a></div>`
  },
  integration: {
    title: 'OpenClaw Integration Guide',
    lede: 'OpenClaw Model Configuration Guide — configure a custom model provider in OpenClaw.',
    toc: ['1. Overview', '2. Prerequisites', '12. Configuration Example', '13. Verify the Configuration', '14. Troubleshooting', '15. Notes'],
    body: `
      <h2>1. Overview</h2>
      <p>This guide explains how to configure a custom model provider in OpenClaw. After the configuration is complete, OpenClaw can call models through the specified API endpoint and use them for local Agent tasks.</p>
      <h2>2. Prerequisites</h2>
      <div class="callout"><span class="ic">ℹ️</span><div>Before you start, make sure you have the following:<br>1. OpenClaw installed on your device.<br>2. A valid API Key.<br>3. The model name you want to use.<br>4. A network environment that can access the API service normally.</div></div>
      <h2>12. Configuration Example</h2>
      <p>API Key: <span class="code-inline red">YOUR_API_KEY</span> &nbsp; Model: <span class="code-inline red">nflashx-1.0-flash</span></p>
      <h2>13. Verify the Configuration</h2>
      <p>After completing the configuration, you can run an OpenClaw task or start a test session. If the configuration is correct, OpenClaw should be able to send requests to the API service and return model responses normally.</p>
      <h2>14. Troubleshooting</h2>
      <div class="codeblock"><pre>▸ 1. API Request Failed
▸ 2. Model Not Found
▸ 3. Authentication Failed
▸ 4. Network Error</pre></div>
      <h2>15. Notes</h2>
      <div class="callout" style="border-color:rgba(255,180,60,.4);background:rgba(255,150,40,.07)"><span class="ic">⚠️</span><div>For OpenAI-compatible API services, the API Base URL usually ends with <span class="code-inline">/v1</span>.<br><br>Correct example:<div class="codeblock" style="margin-top:10px"><button class="copy-btn" data-copy="${API_BASE}/v1">⧉</button><pre>${API_BASE}/v1</pre></div></div></div>`
  },
  plans: {
    title: 'Billing & Top-up',
    lede: 'Prepaid USD balance — no subscriptions. Top up with PayPal, VietQR (VND), or USDT.',
    toc: ['Prepaid balance', 'Top-up methods', 'Signup credit', 'Pro tier', 'How billing works'],
    body: `
      <h2>Prepaid balance</h2>
      <p>NFlashX is pay-as-you-go. Every account holds a USD balance; each successful API call is charged at the model's list price. There are no monthly plans — your balance is always shown in USD.</p>
      <h2>Top-up methods</h2>
      <div class="dcards">
        <div class="dcard"><b>PayPal</b><p>USD top-up from <b>$5</b> to <b>$10,000</b>. The balance is credited when PayPal captures the order.</p></div>
        <div class="dcard"><b>VietQR / bank transfer</b><p>Transfer VND to the bank account shown at checkout. The amount is converted at the live USD/VND rate. Include the <span class="code-inline">NFX-xxxx</span> memo so the bank webhook can credit your balance automatically.</p></div>
        <div class="dcard"><b>USDT (TRC20)</b><p>Available when the admin has configured a USDT wallet. Send the exact amount with the memo; the top-up is credited after confirmation.</p></div>
      </div>
      <h2>Signup credit</h2>
      <p>New verified accounts receive <b>$1.00</b> in balance. The bonus is capped at <b>$2.00 per IP per day</b> to prevent abuse.</p>
      <h2>Pro tier</h2>
      <p>Pro is a one-time <b>$10</b> top-up — not a recurring subscription. It upgrades your account tier to Pro and unlocks <span class="code-inline red">nflashx-1.0-pro</span>, a larger context window (8,192 tokens), and the lower Pro rate limit. Use the platform's <b>Pro tier</b> page; once the payment is approved the tier is applied automatically.</p>
      <h2>How billing works</h2>
      <div class="codeblock"><pre>Charge = model list price × real usage
Text:  per 1M input / output tokens
Image: per generated image
Video: per generated second</pre></div>
      <p>Only successful requests are charged. Flash text requests are free for the first <b>10,000 requests per month</b> (trial). See <a href="#pricing">Model Pricing</a> for current rates.</p>`
  },
  pricing: {
    title: 'Model Pricing',
    lede: 'List price and current trial offers for all NFlashX models.',
    toc: ['Text models', 'Image models', 'Video models', 'Billing notes'],
    body: `
      <h2>Text models</h2>
      <div class="dcards">
        <div class="dcard"><b><span class="code-inline red">nflashx-1.0-flash</span></b><p>Input <b>$0.10</b>/M · Output <b>$0.15</b>/M — first 10,000 requests/month free (trial).</p></div>
        <div class="dcard"><b><span class="code-inline red">nflashx-1.0-pro</span></b><p>Input <b>$0.40</b>/M · Output <b>$0.70</b>/M — requires the Pro tier.</p></div>
      </div>
      <h2>Image models</h2>
      <p><span class="code-inline red">nflashx-vision-1.0-flash</span> — flat <b>$0.010</b> per generated image. Current trial: free.</p>
      <h2>Video models</h2>
      <p><span class="code-inline red">nflashx-motion-1.0</span> — <b>$0.025</b> per generated second; synchronized audio included. <b>Coming soon</b> — not yet publicly available.</p>
      <h2>Billing notes</h2>
      <p>All prices are in USD and charged against your prepaid balance. Only successful requests are billed. Flash text requests are free for the first 10,000 requests/month.</p>`
  },
  faqs: {
    title: 'FAQs',
    lede: 'API access, billing, and top-ups — everything you asked.',
    toc: ['API access and billing', 'Other frequently asked questions'],
    body: `
      <div class="dcards" style="grid-template-columns:1fr">
        <div class="dcard"><b>1. What is this platform?</b><p>NFlashX is a full-stack multimodal AI platform — text, image, and video models behind one OpenAI-compatible API.</p></div>
        <div class="dcard"><b>2. Is the API free to use?</b><p>New accounts get <b>$1.00</b> in balance, and Flash text requests are free for the first 10,000 requests/month. After that you top up a USD balance and pay only for what you use.</p></div>
        <div class="dcard"><b>3. What are the limitations for free users?</b><p>Free accounts use the standard rate limit; the Pro model and the larger context window require the one-time $10 Pro upgrade.</p></div>
        <div class="dcard"><b>4. How do I get started?</b><p>Create a key, call the endpoint, and try <a href="playground.html" style="color:#8df0c4">Vision Studio</a> for images.</p></div>
        <div class="dcard"><b>5. How can I check my usage?</b><p>Usage dashboard shows tokens, image pics, video seconds and requests with a 7-day trend chart.</p></div>
      </div>
      <div class="next-link"><a href="#">Common Error Codes <span>›</span></a></div>`
  },
  legal: {
    title: 'Privacy Policy',
    lede: 'How NFlashX collects, uses, and protects your information.',
    toc: ['1. Scope of This Policy', '3. Information We Collect', '5. AI Data Usage', '7. Sharing of Information'],
    body: `
      <h2>1. Scope of This Policy</h2>
      <p>This policy explains how NFlashX processes information when you use our websites, APIs, and applications.</p>
      <h2>3. Information We Collect</h2>
      <p><b>• Payment and Billing Details</b> If you subscribe to a paid plan, billing information such as billing address and transaction records may be collected. We do not store full payment card details directly.</p>
      <p><b>• Communications</b> When you contact our support team or participate in surveys, we may collect the content of those communications.</p>
      <p><b>• Content You Submit</b> Any content you submit when using the Service, including prompts, inputs, files (documents, images, audio), and other user-generated content.</p>
      <p><b>○ Free Services</b> For users of our Free Services, including the Free API tier, your interactions with the Service may be used to improve our products and AI models unless you opt out.</p>
      <p><b>○ Enterprise Services and Paid Plans</b> Customer Content is not used to train or improve our AI models by default.</p>
      <h2>7. Sharing of Information</h2>
      <p>We share information with service providers, affiliates, and as required by law. See Terms of Service for more.</p>`
  },
};

/* ---------- shared page fragments ---------- */
const ENDPOINTS_HTML = (chat = true) => `
  <p style="margin-bottom:8px">Chat Completions: <span class="code-inline red">POST</span> <span class="code-inline">/v1/chat/completions</span></p>
  <p style="margin-bottom:8px">Responses: <span class="code-inline red">POST</span> <span class="code-inline">/v1/responses</span></p>
  ${chat ? '<p>Messages: <span class="code-inline red">POST</span> <span class="code-inline">/v1/messages</span></p>' : ''}`;

const PARAM_ROWS = (id) => `
  <tr><td><span class="code-inline">model</span></td><td>string</td><td>Yes</td><td>Model name. Use <span class="code-inline red">${id}</span>.</td></tr>
  <tr><td><span class="code-inline">messages</span></td><td>array</td><td>Yes</td><td>Conversation messages, including <span class="code-inline">system</span>, <span class="code-inline">user</span>, and <span class="code-inline">assistant</span> messages.</td></tr>
  <tr><td><span class="code-inline">messages[].content</span></td><td>string / array</td><td>Yes</td><td>Message content. It can be plain text or an array of content blocks containing <span class="code-inline">text</span> and <span class="code-inline">image_url</span>.</td></tr>
  <tr><td><span class="code-inline">temperature</span></td><td>number</td><td>No</td><td>Controls randomness. Lower values produce more deterministic results.</td></tr>
  <tr><td><span class="code-inline">top_p</span></td><td>number</td><td>No</td><td>Controls nucleus sampling. Lower values make output more focused.</td></tr>
  <tr><td><span class="code-inline">max_tokens</span></td><td>number</td><td>No</td><td>Maximum number of tokens to generate in the response.</td></tr>
  <tr><td><span class="code-inline">stream</span></td><td>boolean</td><td>No</td><td>Whether to enable streaming output.</td></tr>
  <tr><td><span class="code-inline">tools</span></td><td>array</td><td>No</td><td>Tool definitions for tool-calling workflows.</td></tr>
  <tr><td><span class="code-inline">tool_choice</span></td><td>string / object</td><td>No</td><td>Controls whether and how the model uses tools.</td></tr>
  <tr><td><span class="code-inline">thinking</span></td><td>object</td><td>No</td><td>Field for enabling Thinking mode in compatible requests.</td></tr>`;

const CAPS_HTML = `
  <p><b>Chat Completions</b><br>Generate high-quality responses for conversations, applications, and business systems.</p>
  <p><b>Multi-turn Conversations</b><br>Maintain context consistency across continuous interactions.</p>
  <p><b>Image URL Input</b><br>Accept visual content through publicly accessible image URLs.</p>
  <p><b>Image Understanding</b><br>Analyze screenshots, describe images, answer visual questions, and extract visual information.</p>
  <p><b>Tool Calling</b><br>Support function calling and external tool orchestration.</p>
  <p><b>Agent Workflows</b><br>Improved planning, execution, context tracking, and multi-step task completion.</p>
  <p><b>Code-specialized Tasks</b><br>Optimized for code generation, debugging, refactoring, explanation, and patch-style development workflows.</p>
  <p><b>Streaming</b><br>Return responses in real time for a better interactive experience.</p>`;

const USECASES_HTML = `
  <p><b>AI Assistants</b><br>General Q&A, productivity assistants, personal assistants, and in-app copilots.</p>
  <p><b>Autonomous Agents</b><br>Multi-step task execution, planning, tool use, and workflow scheduling.</p>
  <p><b>Coding Assistants</b><br>Code generation, bug fixing, refactoring suggestions, code review, test generation, and code explanation.</p>
  <p><b>Customer Support</b><br>FAQ automation, support chatbots, and service workflow automation.</p>
  <p><b>Search and Q&A</b><br>Retrieval-based answers, summarization, and information extraction.</p>
  <p><b>Image Understanding</b><br>Screenshot analysis, image description, visual Q&A, and structured extraction.</p>`;

const RESPONSE_JSON = (id) => `<div class="codeblock"><button class="copy-btn">⧉</button><pre>{
  <span class="c-key">"id"</span>: <span class="c-str">"chatcmpl_xxx"</span>,
  <span class="c-key">"object"</span>: <span class="c-str">"chat.completion"</span>,
  <span class="c-key">"created"</span>: <span class="c-num">1793901842</span>,
  <span class="c-key">"model"</span>: <span class="c-str">"${id}"</span>,
  <span class="c-key">"choices"</span>: [
    {
      <span class="c-key">"index"</span>: <span class="c-num">0</span>,
      <span class="c-key">"message"</span>: {
        <span class="c-key">"role"</span>: <span class="c-str">"assistant"</span>,
        <span class="c-key">"content"</span>: <span class="c-str">"..."</span>
      },
      <span class="c-key">"finish_reason"</span>: <span class="c-str">"stop"</span>
    }
  ],
  <span class="c-key">"usage"</span>: {
    <span class="c-key">"prompt_tokens"</span>: <span class="c-num">290</span>,
    <span class="c-key">"completion_tokens"</span>: <span class="c-num">20</span>,
    <span class="c-key">"total_tokens"</span>: <span class="c-num">310</span>
  }
}</pre></div>`;

function requestTabs(id) {
  const basic = `curl ${API_BASE}/v1/chat/completions \\\n  -H "Authorization: Bearer YOUR_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "model": "${id}",\n    "messages": [\n      { "role": "system", "content": "You are a helpful AI assistant." },\n      { "role": "user", "content": "Explain how autonomous agents use tools to complete tasks." }\n    ],\n    "temperature": 0.7,\n    "max_tokens": 1024\n  }'`;
  const stream = `curl ${API_BASE}/v1/chat/completions \\\n  -H "Authorization: Bearer YOUR_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "model": "${id}",\n    "messages": [\n      { "role": "user", "content": "Write a short product introduction for an AI assistant app." }\n    ],\n    "stream": true\n  }'`;
  const tools = `curl ${API_BASE}/v1/chat/completions \\\n  -H "Authorization: Bearer YOUR_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "model": "${id}",\n    "messages": [\n      { "role": "user", "content": "What is the weather like in Singapore today?" }\n    ],\n    "tools": [\n      { "type": "function", "function": {\n          "name": "get_weather",\n          "parameters": { "type": "object",\n            "properties": { "city": { "type": "string" } } } } }\n    ]\n  }'`;
  const vision = `curl ${API_BASE}/v1/chat/completions \\\n  -H "Authorization: Bearer YOUR_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "model": "${id}",\n    "messages": [\n      { "role": "user", "content": [\n          { "type": "text", "text": "Describe the content of this image." },\n          { "type": "image_url", "image_url": {\n              "url": "https://example.com/image.jpg" } }\n      ] }\n    ]\n  }'`;
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const panel = (name, code, active) => `
    <div class="rpanel ${active ? 'on' : ''}" data-panel="${name}">
      <div class="codeblock"><button class="copy-btn">⧉</button><pre>${esc(code)}</pre></div>
    </div>`;
  return `
    <div class="rtabs">
      <button class="rtab on" data-tab="basic">Basic Chat</button>
      <button class="rtab" data-tab="streaming">Streaming</button>
      <button class="rtab" data-tab="tools">Tool Calling</button>
      <button class="rtab" data-tab="vision">Image Understanding</button>
    </div>
    ${panel('basic', basic, true)}${panel('streaming', stream, false)}${panel('tools', tools, false)}${panel('vision', vision, false)}`;
}

/* ---------- model pages (brand-style structure) ---------- */
function textModelPage(m) {
  const prev = m.id === 'nflashx-1.0-flash' ? ['NFlashX 0.9 Flash', 'nflashx-0.9-flash'] : ['NFlashX 1.0 Flash', 'nflashx-1.0-flash'];
  return {
    kicker: 'Text',
    title: m.name,
    lede: m.lede,
    copy: true,
    toc: ['Overview', 'Core Capabilities', 'Use Cases', `Upgrade from ${prev[0]}`, 'API Reference', 'Endpoint', 'Headers', 'Request Parameters', 'Image URL Input', 'Request Examples', 'Response Format', 'Response Fields', 'Thinking Mode', 'Limits and Pricing'],
    body: `
      ${m.id === 'nflashx-1.0-pro' ? '<div class="callout" style="border-color:rgba(37,227,154,.4);background:rgba(37,227,154,.07)"><span class="ic">🔑</span><div><b>Pro-tier model.</b> Calling <span class="code-inline red">nflashx-1.0-pro</span> requires a <b>Pro-tier API key</b> — free keys receive HTTP 403. Upgrade via the API Platform.</div></div>' : ''}
      <div class="callout"><span class="ic">ℹ️</span><div>${m.name} is a generally available language model. It keeps the same OpenAI-compatible Chat Completions integration path while improving the experience for coding, agent workflows, tool calling, multi-turn conversations, reasoning, and image understanding.</div></div>
      <div class="dcards">
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3zM12 12l8-4.5M12 12v9M12 12L4 7.5" stroke="currentColor"/></svg></div><b>Model</b><p><span class="code-inline red">${m.id}</span></p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M9 9a3 3 0 105.5 1.6M8 15a5 5 0 108-4" stroke="currentColor"/><circle cx="12" cy="12" r="9" stroke="currentColor"/></svg></div><b>API Endpoints</b><p>${ENDPOINTS_HTML()}</p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M9 3h6M10 3v6L4.5 18a2 2 0 001.8 3h11.4a2 2 0 001.8-3L14 9V3" stroke="currentColor"/></svg></div><b>Release Status</b><p>${m.release}</p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M12 19V5m-6 6l6-6 6 6" stroke="currentColor"/></svg></div><b>Upgrade Path</b><p>${m.upgrade}</p></div>
      </div>
      <h2>Overview</h2>
      <p>${m.name} is designed as the next-step upgrade for developers building on the NFlashX series. In most integrations, you only need to replace the model value with <span class="code-inline">${m.id}</span>; the Base URL, endpoint, headers, message format, streaming format, tool-calling format, and image URL input format remain the same.</p>
      <p>The model focuses on a smoother developer experience, stronger instruction following, more stable multi-turn output, and improved code-specific capability for generation, debugging, refactoring, explanation, and agentic coding workflows.</p>
      <p>Use <span class="code-inline red">${m.id}</span> directly as the model name.</p>
      <h2>Core Capabilities</h2>
      ${CAPS_HTML}
      <h2>Use Cases</h2>
      ${USECASES_HTML}
      <h2>Upgrade from ${prev[0]}</h2>
      <p>If you already call <span class="code-inline red">${prev[1]}</span>, the migration is intentionally small.</p>
      <table class="mtable">
        <tr><th>Item</th><th>${prev[0]}</th><th>${m.name}</th></tr>
        <tr><td>Endpoint</td><td>POST /v1/chat/completions</td><td>POST /v1/chat/completions</td></tr>
        <tr><td>Base URL</td><td>${API_BASE}/v1</td><td>${API_BASE}/v1</td></tr>
        <tr><td>Model name</td><td><span class="code-inline red">${prev[1]}</span></td><td><span class="code-inline red">${m.id}</span></td></tr>
        <tr><td>Message format</td><td>OpenAI-compatible messages</td><td>Same</td></tr>
        <tr><td>Streaming</td><td>stream: true</td><td>Same</td></tr>
        <tr><td>Tool calling</td><td>tools and tool_choice</td><td>Same</td></tr>
        <tr><td>Image URL input</td><td>messages[].content[].image_url</td><td>Same</td></tr>
      </table>
      <p>For existing integrations, migration can usually be handled as a model-name change.</p>
      <h2>API Reference</h2>
      <h3>Endpoint</h3>
      <div class="codeblock"><button class="copy-btn" data-copy="${API_BASE}/v1/chat/completions">⧉</button><pre><span class="c-key">POST</span> ${API_BASE}/v1/chat/completions</pre></div>
      <h3>Headers</h3>
      <div class="codeblock"><button class="copy-btn">⧉</button><pre>-H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span></pre></div>
      <h3>Request Parameters</h3>
      <table class="mtable">
        <tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>
        ${PARAM_ROWS(m.id)}
      </table>
      <h3>Image URL Input</h3>
      <p>${m.name} supports passing text and image URLs in the same messages request.</p>
      <table class="mtable">
        <tr><th>Input Type</th><th>Format</th><th>Description</th></tr>
        <tr><td>Text</td><td><span class="code-inline">text</span></td><td>Plain text instruction or question.</td></tr>
        <tr><td>Image URL</td><td><span class="code-inline">image_url</span></td><td>Pass image content through a publicly accessible image URL.</td></tr>
      </table>
      <div class="codeblock"><button class="copy-btn">⧉</button><pre>{
  <span class="c-key">"role"</span>: <span class="c-str">"user"</span>,
  <span class="c-key">"content"</span>: [
    { <span class="c-key">"type"</span>: <span class="c-str">"text"</span>, <span class="c-str">"text"</span>: <span class="c-str">"Describe the content of this image."</span> },
    { <span class="c-key">"type"</span>: <span class="c-str">"image_url"</span>, <span class="c-str">"image_url"</span>: { <span class="c-str">"url"</span>: <span class="c-str">"https://example.com/image.jpg"</span> } }
  ]
}</pre></div>
      <h3>Request Examples</h3>
      ${requestTabs(m.id)}
      <h3>Response Format</h3>
      ${RESPONSE_JSON(m.id)}
      <h3>Response Fields</h3>
      <table class="mtable">
        <tr><th>Field</th><th>Type</th><th>Description</th></tr>
        <tr><td><span class="code-inline">id</span></td><td>string</td><td>Unique identifier for the completion.</td></tr>
        <tr><td><span class="code-inline">object</span></td><td>string</td><td>Object type, always <span class="code-inline">chat.completion</span>.</td></tr>
        <tr><td><span class="code-inline">model</span></td><td>string</td><td>Model that handled the request.</td></tr>
        <tr><td><span class="code-inline">choices[].message</span></td><td>object</td><td>Assistant response message.</td></tr>
        <tr><td><span class="code-inline">usage</span></td><td>object</td><td>Token accounting for the request.</td></tr>
      </table>
      <h2>Thinking Mode</h2>
      <p>Enable extended reasoning by adding <span class="code-inline">"thinking": { "type": "enabled" }</span> to the request body. The response then carries a <span class="code-inline">reasoning_content</span> field alongside the final answer.</p>
      <h2>Limits and Pricing</h2>
      <p>See the <a href="#pricing" style="color:#8df0c4">Model Pricing</a> page for list prices and current trial offers.</p>`
  };
}

function imageModelPage(m) {
  return {
    kicker: 'Image',
    title: m.name,
    lede: `${m.name} is a high-performance NFlashX image generation and editing model. It supports text-to-image, image-to-image, and multi-image composition workflows for creative design, marketing visuals, e-commerce product images, and social content production.`,
    copy: true,
    toc: ['Overview', 'Core Capabilities', 'Use Cases', 'API Reference', 'Endpoint', 'Headers', 'Request Parameters', 'Important Notes', 'Request Examples', 'Response Format', 'Response Fields', 'Limits and Pricing'],
    body: `
      <div class="callout"><span class="ic">ℹ️</span><div>${m.name} is a high-performance image generation and editing model. It supports text-to-image, image-to-image, and multi-image composition workflows for creative design, marketing visuals, e-commerce product images, and social content production.</div></div>
      <div class="dcards">
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" stroke="currentColor"/></svg></div><b>Model</b><p><span class="code-inline red">${m.id}</span></p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M9 9a3 3 0 105.5 1.6M8 15a5 5 0 108-4" stroke="currentColor"/><circle cx="12" cy="12" r="9" stroke="currentColor"/></svg></div><b>API Endpoint</b><div class="ep"><div class="ep-line"><span class="method post">POST</span><span class="path">/v1/images/generations</span></div></div></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M4 17l4.5-4.5 3 3L17 11l3.5 3.5" stroke="currentColor"/><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor"/></svg></div><b>Supported Workflows</b><p>Text-to-image, image-to-image, and multi-image composition.</p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M12 2v20M2 12h20" stroke="currentColor"/><circle cx="12" cy="12" r="9" stroke="currentColor"/></svg></div><b>Trial price</b><p>All supported output-resolution tiers and input reference images are currently <b>free</b>.</p></div>
      </div>
      <h2>Overview</h2>
      <p>${m.name} is optimized for fast, high-quality, and cost-effective image production workflows. The model has appeared on the Artificial Analysis image editing leaderboard with an Elo score of <b>1,091</b>, ranking just outside the Top 20 and demonstrating strong image editing capability for a first release.</p>
      <h2>Core Capabilities</h2>
      <p><b>Text-to-image</b><br>Generate images from text prompts.</p>
      <p><b>Image-to-image</b><br>Edit, transform, or enhance existing images.</p>
      <p><b>Multi-image Input</b><br>Use multiple reference images to create a new image.</p>
      <p><b>Image Editing</b><br>Modify composition, style, objects, backgrounds, and scenes.</p>
      <p><b>Style Control</b><br>Control artistic style, lighting, layout, and visual direction.</p>
      <p><b>Fast Generation</b><br>Designed for frequent, fast, production-grade creative workflows.</p>
      <h2>Use Cases</h2>
      <p><b>Creative Design</b><br>Posters, concept art, and social media visuals.</p>
      <p><b>Marketing Content</b><br>Product ads, campaign creatives, and banners.</p>
      <p><b>Image Editing</b><br>Object replacement, background replacement, style transfer, and local edits.</p>
      <p><b>Character Composition</b><br>Combine multiple characters or reference images into one scene.</p>
      <p><b>E-commerce</b><br>Product image enhancement, product staging, and marketing hero images.</p>
      <p><b>Social Content</b><br>Memes, avatars, thumbnails, and lifestyle visual assets.</p>
      <h2>API Reference</h2>
      <h3>Endpoint</h3>
      <div class="codeblock"><button class="copy-btn" data-copy="${API_BASE}/v1/images/generations">⧉</button><pre><span class="c-key">POST</span> ${API_BASE}/v1/images/generations</pre></div>
      <h3>Headers</h3>
      <div class="codeblock"><button class="copy-btn">⧉</button><pre>-H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span></pre></div>
      <h3>Request Parameters</h3>
      <table class="mtable">
        <tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>
        <tr><td><span class="code-inline">model</span></td><td>string</td><td>Yes</td><td>Model name. Use <span class="code-inline red">${m.id}</span>.</td></tr>
        <tr><td><span class="code-inline">prompt</span></td><td>string</td><td>Yes</td><td>Text prompt describing the target image or editing instruction.</td></tr>
        <tr><td><span class="code-inline">size</span></td><td>string</td><td>Yes</td><td>Output image size, such as <span class="code-inline">1024x768</span>, <span class="code-inline">1024x1024</span>, or <span class="code-inline">768x1024</span>.</td></tr>
        <tr><td><span class="code-inline">image</span></td><td>string[]</td><td>Required for image-to-image</td><td>Input image array. Supports public URLs or Data URI Base64.</td></tr>
        <tr><td><span class="code-inline">return_base64</span></td><td>boolean</td><td>No</td><td>Use this when text-to-image output should be returned as Base64.</td></tr>
        <tr><td><span class="code-inline">extra_body.response_format</span></td><td>string</td><td>No</td><td>Output format. Common values are <span class="code-inline">url</span> and <span class="code-inline">b64_json</span>.</td></tr>
      </table>
      <div class="callout" style="border-color:rgba(255,180,60,.4);background:rgba(255,150,40,.07)"><span class="ic">⚠️</span><div><b>Important Notes</b><br>• Do not place <span class="code-inline">response_format</span> at the top level of the request body. For URL or Base64 output, place it inside <span class="code-inline">extra_body</span>.<br>• <b>Text-to-image:</b> only <span class="code-inline">model</span>, <span class="code-inline">prompt</span>, and <span class="code-inline">size</span> are required. Do not pass <span class="code-inline">image</span>.<br>• <b>Image-to-image:</b> pass image URLs or Data URI Base64 values through <span class="code-inline">extra_body.image</span>.<br>• Image-to-image requests do not require <span class="code-inline">tags: ["img2img"]</span>.<br>• Use <span class="code-inline">YOUR_API_KEY</span> in public documentation. Do not expose real API keys.</div></div>
      <h3>Request Examples</h3>
      <div class="rtabs">
        <button class="rtab on" data-tab="t2i-url">Text-to-image: URL Output</button>
        <button class="rtab" data-tab="t2i-b64">Text-to-image: Base64 Output</button>
        <button class="rtab" data-tab="i2i-url">Image-to-image: URL Input + URL Output</button>
        <button class="rtab" data-tab="multi">Multi-image Composition</button>
      </div>
      <div class="rpanel on" data-panel="t2i-url"><div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> ${API_BASE}/v1/images/generations \\\n  -H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span> \\\n  -d <span class="c-str">'{
    "model": "${m.id}",
    "prompt": "A clean product photo of a glass cube on a white studio background, soft shadows, high detail",
    "size": "1024x768",
    "extra_body": { "response_format": "url" }
  }'</span></pre></div></div>
      <div class="rpanel" data-panel="t2i-b64"><div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> ${API_BASE}/v1/images/generations \\\n  -H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span> \\\n  -d <span class="c-str">'{
    "model": "${m.id}",
    "prompt": "A clean product photo of a glass cube on a white studio background, soft shadows, high detail",
    "size": "1024x768",
    "return_base64": true
  }'</span></pre></div></div>
      <div class="rpanel" data-panel="i2i-url"><div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> ${API_BASE}/v1/images/generations \\\n  -H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span> \\\n  -d <span class="c-str">'{
    "model": "${m.id}",
    "prompt": "Transform this image into a cinematic cyberpunk style while preserving the main subject and composition",
    "size": "1024x768",
    "extra_body": {
      "image": [ "https://example.com/input-image.png" ],
      "response_format": "url"
    }
  }'</span></pre></div></div>
      <div class="rpanel" data-panel="multi"><div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> ${API_BASE}/v1/images/generations \\\n  -H <span class="c-str">"Authorization: Bearer YOUR_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span> \\\n  -d <span class="c-str">'{
    "model": "${m.id}",
    "prompt": "Combine the two characters into an intense fantasy battle scene, dynamic lighting, detailed background, cinematic composition",
    "size": "1024x768",
    "extra_body": {
      "image": [
        "https://example.com/character-1.png",
        "https://example.com/character-2.png"
      ],
      "response_format": "url"
    }
  }'</span></pre></div></div>
      <h3>Response Format</h3>
      <div class="rtabs">
        <button class="rtab on" data-tab="rf-url">URL Output</button>
        <button class="rtab" data-tab="rf-b64">Base64 Output</button>
      </div>
      <div class="rpanel on" data-panel="rf-url"><div class="codeblock"><button class="copy-btn">⧉</button><pre>{
  <span class="c-key">"created"</span>: <span class="c-num">1793901842</span>,
  <span class="c-key">"data"</span>: [
    { <span class="c-key">"url"</span>: <span class="c-str">"https://cdn.nflashx.com/images/xxx.png"</span>,
      <span class="c-key">"b64_json"</span>: <span class="c-key">null</span>,
      <span class="c-key">"revised_prompt"</span>: <span class="c-key">null</span> }
  ]
}</pre></div></div>
      <div class="rpanel" data-panel="rf-b64"><div class="codeblock"><button class="copy-btn">⧉</button><pre>{
  <span class="c-key">"created"</span>: <span class="c-num">1793901842</span>,
  <span class="c-key">"data"</span>: [
    { <span class="c-key">"url"</span>: <span class="c-key">null</span>,
      <span class="c-key">"b64_json"</span>: <span class="c-str">"iVBORw0KGgoAAAANSUhEUgAA..."</span>,
      <span class="c-key">"revised_prompt"</span>: <span class="c-key">null</span> }
  ]
}</pre></div></div>
      <h3>Response Fields</h3>
      <table class="mtable">
        <tr><th>Field</th><th>Type</th><th>Description</th></tr>
        <tr><td><span class="code-inline">created</span></td><td>integer</td><td>Request creation timestamp.</td></tr>
        <tr><td><span class="code-inline">data</span></td><td>array</td><td>List of generated image results.</td></tr>
        <tr><td><span class="code-inline">data[].url</span></td><td>string / null</td><td>Generated image URL when <span class="code-inline">response_format</span> is <span class="code-inline">url</span>.</td></tr>
        <tr><td><span class="code-inline">data[].b64_json</span></td><td>string / null</td><td>Base64-encoded image when <span class="code-inline">response_format</span> is <span class="code-inline">b64_json</span>.</td></tr>
      </table>
      <h2>Limits and Pricing</h2>
      <p>See the <a href="#pricing" style="color:#8df0c4">Model Pricing</a> page for resolution tiers and current trial offers.</p>`
  };
}

function videoModelPage(m) {
  return {
    kicker: 'Video',
    title: m.name,
    titleExtra: '<span class="soon-pill"><span class="dot"></span>Coming Soon</span>',
    lede: `Integrate ${m.name} through an OpenAI Videos-compatible API for text-to-video, keyframe control, and image-reference generation.`,
    copy: true,
    toc: ['Model ID', 'Create Task', 'Retrieve Task', 'Release Status', 'Differences from the standard Motion API', 'Quickstart', '1. Set Environment Variables', '2. Create a Video Task', '3. Retrieve the Result'],
    body: `
      <div class="callout" style="border-color:rgba(120,150,255,.4);background:rgba(120,150,255,.07)"><span class="ic">🚧</span><div><b>Coming soon.</b> ${m.name} is not yet publicly available. This page previews the upcoming API ahead of launch. Access, pricing, and the live endpoint will be enabled when the model is officially released.</div></div>
      <div class="dcards">
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" stroke="currentColor"/></svg></div><b>Model ID</b><p><span class="code-inline red">${m.id}</span></p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor"/><path d="M10 9l5 3-5 3V9z" stroke="currentColor"/></svg></div><b>Create Task</b><p><span class="code-inline red">POST</span> <span class="code-inline">/v1/videos</span></p></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><circle cx="12" cy="12" r="9" stroke="currentColor"/><path d="M12 7v5l3 3" stroke="currentColor"/></svg></div><b>Retrieve Task</b><div class="ep"><div class="ep-line"><span class="method get">GET</span><span class="path">/nflashxapi?video_id=&lt;VIDEO_ID&gt;<br>&amp;model_name=${m.id}</span></div></div></div>
        <div class="dcard"><div class="dic"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.6"><path d="M9 3h6M10 3v6L4.5 18a2 2 0 001.8 3h11.4a2 2 0 001.8-3L14 9V3" stroke="currentColor"/></svg></div><b>Release Status</b><p><span class="status-pill"><span class="dot"></span>Coming soon</span></p><p>Not yet publicly available. Launch pricing: list <b>$0.025 / second</b>, trial <b>$0 / second</b>.</p></div>
      </div>
      <h2>Differences from the standard Motion API</h2>
      <table class="mtable">
        <tr><th>Validation</th><th>Flash rule</th><th>Failure response</th></tr>
        <tr><td>size</td><td>Only the string <span class="code-inline">"720P"</span> is supported</td><td>HTTP 400: size must be 720P</td></tr>
        <tr><td>seconds</td><td>Only the string <span class="code-inline">"4"</span>–<span class="code-inline">"12"</span> is supported</td><td>HTTP 400: seconds must be 4–12</td></tr>
        <tr><td>Reference image count</td><td><span class="code-inline">images</span> supports at most 5 items</td><td>HTTP 400: images length must not exceed 5</td></tr>
        <tr><td>Reference audio count</td><td><span class="code-inline">audios</span> supports at most 3 items</td><td>HTTP 400: audios length must not exceed 3</td></tr>
        <tr><td>Reference video input</td><td>Non-empty <span class="code-inline">videos</span> content is not supported</td><td>HTTP 400: videos is not supported</td></tr>
      </table>
      <p>Flash-specific validation runs before task creation, queueing, billing, and inference. Invalid requests do not create a video task and are not billed.</p>
      <h2>Quickstart</h2>
      <h3>1. Set Environment Variables</h3>
      <div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">export</span> NFLASHX_API_KEY = <span class="c-str">"YOUR_API_KEY"</span>\n<span class="c-key">export</span> NFLASHX_BASE_URL = <span class="c-str">"${API_BASE}/v1"</span></pre></div>
      <h3>2. Create a Video Task</h3>
      <div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> -sS -X POST <span class="c-str">"$NFLASHX_BASE_URL/videos"</span> \\\n  -H <span class="c-str">"Authorization: Bearer $NFLASHX_API_KEY"</span> \\\n  -H <span class="c-str">"Content-Type: application/json"</span> \\\n  -d <span class="c-str">'{
    "model": "${m.id}",
    "prompt": "A silver sports car moves slowly through a rain-soaked futuristic city street, neon reflections, cinematic camera motion, natural ambience",
    "seconds": "5",
    "mode": "text",
    "size": "720P",
    "aspect_ratio": "16:9"
  }'</span></pre></div>
      <p>Save <span class="code-inline">video_id</span> from the create response. <span class="code-inline">id</span> and <span class="code-inline">task_id</span> identify the asynchronous task, while <span class="code-inline">video_id</span> is used for retrieval.</p>
      <h3>3. Retrieve the Result</h3>
      <div class="rtabs">
        <button class="rtab on" data-tab="ret-name">By video_id + model_name (Recommended)</button>
        <button class="rtab" data-tab="ret-id">By video_id (text mode only)</button>
      </div>
      <div class="rpanel on" data-panel="ret-name"><div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> -sS <span class="c-str">"${API_BASE}/api/video-status/VIDEO_ID"</span> \\\n  -H <span class="c-str">"Authorization: Bearer $NFLASHX_API_KEY"</span></pre></div>
      <p>This form works for <span class="code-inline">text</span>, <span class="code-inline">keyframe</span>, and <span class="code-inline">reference</span> modes and is the recommended polling method for ${m.name}.</p></div>
      <div class="rpanel" data-panel="ret-id"><div class="codeblock"><button class="copy-btn">⧉</button><pre><span class="c-key">curl</span> -sS <span class="c-str">"${API_BASE}/api/video-status/VIDEO_ID"</span> \\\n  -H <span class="c-str">"Authorization: Bearer $NFLASHX_API_KEY"</span></pre></div>
      <p>This form is valid only for tasks created with <span class="code-inline">mode: "text"</span>. Queries for keyframe and reference tasks must include <span class="code-inline">model_name=${m.id}</span>.</p></div>
      <p>Poll every 1–2 seconds until <span class="code-inline">status</span> becomes <span class="code-inline">completed</span> or <span class="code-inline">failed</span>. When status is <span class="code-inline">completed</span>, read the video address from the top-level <span class="code-inline">url</span> field to play or download it.</p>`
  };
}

/* ---------- top rail (thay sidebar 3-cot kieu cu) ---------- */
const rail = document.getElementById('drail');
const main = document.getElementById('docMain');

const RAIL = [
  ['overview', 'Overview'],
  ['quickstart', 'Quickstart'],
  ['m=nflashx-1.0-flash', '1.0 Flash'],
  ['m=nflashx-1.0-pro', '1.0 Pro'],
  ['m=nflashx-vision-1.0-flash', 'Vision 1.0'],
  ['m=nflashx-motion-1.0', 'Motion 1.0'],
  ['integration', 'Integration'],
  ['plans', 'Billing'],
  ['pricing', 'Pricing'],
  ['faqs', 'FAQs'],
  ['legal', 'Legal'],
];

function renderRail(activeKey) {
  rail.innerHTML = RAIL.map(([k, label]) => {
    const on = activeKey === k ? ' on' : '';
    const soon = k === 'm=nflashx-motion-1.0' ? ' <span class="badge-soon">Soon</span>' : '';
    return `<a href="#${k}" class="rail-chip${on}">${label}${soon}</a>`;
  }).join('');
}

/* ---------- page render ---------- */
function renderPage(key) {
  renderRail(key);
  if (key === 'overview') {
    renderDashboard();
    return;
  }
  let p;
  if (key.startsWith('m=')) {
    const all = [...MODELS.text, ...MODELS.image, ...MODELS.video];
    const m = all.find(x => x.id === key.slice(2)) || all[0];
    p = m.kind === 'text' ? textModelPage(m) : m.kind === 'image' ? imageModelPage(m) : videoModelPage(m);
  } else {
    p = PAGES[key] || PAGES.overview;
    p = { ...p, kicker: '', copy: true };
  }
  const chips = (p.toc || []).map(t => `<span class="toc-chip">${t}</span>`).join('');
  main.innerHTML = `
    ${p.kicker ? `<div class="kicker">${p.kicker}</div>` : ''}
    <div class="doc-head">
      <h1>${p.title}${p.titleExtra || ''}</h1>
      ${p.copy ? '<button class="copy-page" id="copyPage">⧉ Copy page</button>' : ''}
    </div>
    <p class="lede">${p.lede}</p>
    ${chips ? `<div class="toc-chips"><span class="toc-lbl">ON THIS PAGE</span>${chips}</div>` : ''}
    ${p.body}`;
  bindPage();
  scrollTo(0, 0);
}

function renderDashboard() {
  const models = [...MODELS.text, ...MODELS.image, ...MODELS.video];
  const cards = [
    { k: 'quickstart', t: 'Quickstart', d: PAGES.quickstart.lede, tag: 'START HERE' },
    ...models.map(m => ({ k: 'm=' + m.id, t: m.name, d: m.lede,
      tag: (m.kind || '').toUpperCase() + (m.soon ? ' · SOON' : '') })),
    { k: 'integration', t: 'Integration', d: (PAGES.integration || {}).lede || 'Connect NFlashX to your stack.', tag: 'GUIDE' },
    { k: 'plans', t: 'Billing & Top-up', d: (PAGES.plans || {}).lede || '', tag: 'BILLING' },
    { k: 'pricing', t: 'Model Pricing', d: (PAGES.pricing || {}).lede || '', tag: 'BILLING' },
    { k: 'faqs', t: 'FAQs', d: (PAGES.faqs || {}).lede || '', tag: 'HELP' },
    { k: 'legal', t: 'Legal', d: (PAGES.legal || {}).lede || '', tag: 'LEGAL' },
  ];
  main.innerHTML = `
    <div class="kicker">Developer Guides</div>
    <div class="doc-head"><h1>NFlashX Docs</h1></div>
    <p class="lede">The whole API in one place — pick a page to get started.</p>
    <div class="nx-doc-grid">${cards.map(c => `
      <a class="nx-doc-card" href="#${c.k}">
        <span class="dd-tag">${c.tag}</span>
        <b>${c.t}</b>
        <p>${c.d}</p>
        <span class="dd-go">Read →</span>
      </a>`).join('')}</div>`;
  bindPage();
  scrollTo(0, 0);
}

function doSearch(q) {
  q = (q || '').trim().toLowerCase().replace(/[<>&"]/g, '');
  if (!q) { route(); return; }
  renderRail('');
  const idx = [
    { k: 'overview', t: 'Overview', d: PAGES.overview.lede },
    { k: 'quickstart', t: 'Quickstart', d: PAGES.quickstart.lede },
    ...[...MODELS.text, ...MODELS.image, ...MODELS.video].map(m => ({ k: 'm=' + m.id, t: m.name, d: m.lede })),
    { k: 'integration', t: 'Integration', d: (PAGES.integration || {}).lede || '' },
    { k: 'plans', t: 'Billing & Top-up', d: (PAGES.plans || {}).lede || '' },
    { k: 'pricing', t: 'Model Pricing', d: (PAGES.pricing || {}).lede || '' },
    { k: 'faqs', t: 'FAQs', d: (PAGES.faqs || {}).lede || '' },
    { k: 'legal', t: 'Legal', d: (PAGES.legal || {}).lede || '' },
  ];
  const hits = idx.filter(x => (x.t + ' ' + x.d).toLowerCase().includes(q));
  main.innerHTML = `
    <div class="kicker">Search</div>
    <div class="doc-head"><h1>Results for "${q}"</h1></div>
    <p class="lede">${hits.length} trang khớp.</p>
    <div class="nx-doc-grid">${hits.map(c => `
      <a class="nx-doc-card" href="#${c.k}">
        <span class="dd-tag">DOC</span>
        <b>${c.t}</b>
        <p>${c.d}</p>
        <span class="dd-go">Đọc →</span>
      </a>`).join('') || '<p class="lede">No pages found — try another keyword.</p>'}</div>`;
  scrollTo(0, 0);
}

function bindPage() {
  document.querySelectorAll('.copy-btn').forEach(b => {
    b.onclick = () => {
      const txt = b.dataset.copy || b.parentElement.querySelector('pre').innerText;
      navigator.clipboard.writeText(txt).catch(() => {});
      b.textContent = '✓'; setTimeout(() => b.textContent = '⧉', 1200);
    };
  });
  const cp = document.getElementById('copyPage');
  if (cp) cp.onclick = () => {
    navigator.clipboard.writeText(main.innerText).catch(() => {});
    cp.textContent = '✓ Copied'; setTimeout(() => cp.textContent = '⧉ Copy page', 1400);
  };
  document.querySelectorAll('.rtab').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.rtab').forEach(x => x.classList.remove('on'));
      document.querySelectorAll('.rpanel').forEach(x => x.classList.remove('on'));
      b.classList.add('on');
      const panel = document.querySelector(`.rpanel[data-panel="${b.dataset.tab}"]`);
      if (panel) panel.classList.add('on');
    };
  });
}

/* ---------- tabs / routing ---------- */
document.getElementById('tabs').addEventListener('click', e => {
  const a = e.target.closest('a[data-tab]'); if (!a) return;
  e.preventDefault();
  document.querySelectorAll('#tabs a').forEach(x => x.classList.remove('on'));
  a.classList.add('on');
  location.hash = a.dataset.tab;
});

function route() {
  const q = new URLSearchParams(location.search).get('tab');
  const h = location.hash.replace('#', '') || q || 'overview';
  const tabMap = { integration: 'integration', plans: 'plans', pricing: 'pricing', faqs: 'faqs', legal: 'legal' };
  const tab = tabMap[h] || (h.startsWith('m=') || h === 'quickstart' || h === 'overview' ? 'guides' : 'guides');
  document.querySelectorAll('#tabs a').forEach(x => x.classList.toggle('on', x.dataset.tab === tab));
  renderPage(tabMap[h] || h);
}
addEventListener('hashchange', route);

addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault(); document.getElementById('docSearch').focus();
  }
});

document.getElementById('docSearch').addEventListener('input', e => doSearch(e.target.value));

route();
