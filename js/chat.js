// ============================================================
// NFlashX — Chat API Integration (js/chat.js)
// Gọi chính server platform (server.py, port 8600):
//   POST /v1/chat/completions   (Bearer key + rate limit theo tier)
// Lưu ý: KHÔNG đụng js/app.js (landing slider)
// ============================================================

// Cùng origin khi chạy qua server NFlashX; mở file trực tiếp thì fallback về 8600
const API_URL = (location.protocol.startsWith('http') ? '' : 'http://127.0.0.1:8600')
              + '/v1/chat/completions';
const MODEL   = 'n-flashx-1.0-flash';
const KEY_STORAGE = 'nfx_chat_api_key';

function getApiKey() {
  // Lấy key từ ô input do người dùng nhập, không hardcode
  const keyEl = document.getElementById('api-key');
  return keyEl ? keyEl.value.trim() : '';
}

function setStatus(el, text, cls) {
  el.className = 'chat-status' + (cls ? ' ' + cls : '');
  el.textContent = text;
}

function addBubble(el, text, who) {
  const b = document.createElement('div');
  b.className = 'chat-bubble ' + who; // 'user' | 'ai' | 'error'
  b.textContent = text;
  el.appendChild(b);
  el.scrollTop = el.scrollHeight;
  return b;
}

async function sendMessage() {
  const inputEl  = document.getElementById('user-input');
  const outputEl = document.getElementById('chat-output');
  const keyEl    = document.getElementById('api-key');
  const sendBtn  = document.getElementById('send-btn');

  const userText = inputEl.value.trim();
  if (!userText && !PENDING_IMAGE) return;

  const apiKey = getApiKey();
  if (!apiKey) {
    addBubble(outputEl, '⚠️ Chưa nhập API Key — điền key vào ô "API Key" phía trên rồi gửi lại.', 'error');
    keyEl.focus();
    return;
  }

  // --- Loading state ---
  inputEl.disabled = true;
  sendBtn.disabled = true;
  addBubble(outputEl, userText + (PENDING_IMAGE ? '  🖼 [ảnh đính kèm]' : ''), 'user');
  inputEl.value = '';
  const loading = addBubble(outputEl, 'Loading...', 'ai loading');

  // Content: text thường HOẶC text + image (multimodal — upstream đã test với data URL)
  let content;
  if (PENDING_IMAGE) {
    content = [{ type: 'text', text: userText || 'Describe this image.' },
               { type: 'image_url', image_url: { url: PENDING_IMAGE } }];
    clearPendingImage();
  } else {
    content = userText;
  }

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + apiKey
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [{ role: 'user', content }],
        max_tokens: 4000          // ảnh tốn token — nới trần phía client, server vẫn clamp theo tier
      })
    });

    // Bắt lỗi HTTP (401, 429, 500...) trước khi parse JSON
    if (!response.ok) {
      const errText = await response.text();
      throw new Error('API trả về lỗi ' + response.status + ': ' + errText);
    }

    const data = await response.json();
    loading.textContent = data.choices[0].message.content;
    loading.classList.remove('loading');

  } catch (error) {
    // Lỗi mạng / CORS / key sai / JSON lỗi — hiển thị sạch, thay bubble Loading
    loading.textContent = '❌ Lỗi: ' + error.message;
    loading.classList.remove('loading');
    loading.classList.add('error');

  } finally {
    inputEl.disabled = false;
    sendBtn.disabled = false;
    inputEl.focus();
    outputEl.scrollTop = outputEl.scrollHeight;
  }
}

/* ---------- đính kèm ảnh: downscale về ≤1024px rồi chuyển data URL ---------- */
let PENDING_IMAGE = null;

function clearPendingImage() {
  PENDING_IMAGE = null;
  document.getElementById('img-preview').style.display = 'none';
  document.getElementById('img-file').value = '';
}

function initImageAttach() {
  const btn = document.getElementById('img-btn');
  const file = document.getElementById('img-file');
  btn.onclick = () => file.click();
  document.getElementById('img-clear').onclick = clearPendingImage;
  file.onchange = () => {
    const f = file.files && file.files[0];
    if (!f) return;
    if (f.size > 8 * 1024 * 1024) { alert('Ảnh quá lớn (tối đa 8MB).'); return; }
    const img = new Image();
    const rd = new FileReader();
    rd.onload = () => { img.src = rd.result; };
    img.onload = () => {
      const MAX = 1024;
      const sc = Math.min(1, MAX / Math.max(img.width, img.height));
      const cv = document.createElement('canvas');
      cv.width = Math.round(img.width * sc);
      cv.height = Math.round(img.height * sc);
      cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
      PENDING_IMAGE = cv.toDataURL('image/png');
      document.getElementById('img-thumb').src = PENDING_IMAGE;
      document.getElementById('img-name').textContent = f.name + ' → ' + cv.width + '×' + cv.height;
      document.getElementById('img-preview').style.display = 'flex';
    };
    img.onerror = () => alert('Không đọc được file ảnh này.');
    rd.readAsDataURL(f);
  };
}

// --- Khởi tạo: gắn sự kiện + auto key từ session đăng nhập ---
document.addEventListener('DOMContentLoaded', () => {
  const sendBtn = document.getElementById('send-btn');
  const inputEl = document.getElementById('user-input');
  const keyEl   = document.getElementById('api-key');

  // 1) Key đã dùng lần trước (localStorage)
  const savedKey = localStorage.getItem(KEY_STORAGE);
  if (savedKey) keyEl.value = savedKey;

  // 2) Đã đăng nhập nền tảng → tự điền key của tài khoản (nfx_session)
  let sess = null;
  try { sess = JSON.parse(localStorage.getItem('nfx_session') || 'null'); } catch (_) {}
  if (sess && sess.token) {
    fetch('/api/auth/me', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: sess.token })
    }).then(r => r.json()).then(j => {
      if (j.ok && j.user && j.user.api_key) {
        keyEl.value = j.user.api_key;
        localStorage.setItem(KEY_STORAGE, j.user.api_key);
      }
    }).catch(() => {});
  }

  // Lưu key mỗi lần người dùng tự sửa
  keyEl.addEventListener('change', () => {
    const k = keyEl.value.trim();
    if (k) localStorage.setItem(KEY_STORAGE, k);
  });

  sendBtn.addEventListener('click', sendMessage);
  initImageAttach();
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});
