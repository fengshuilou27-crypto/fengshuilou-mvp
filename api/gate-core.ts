/**
 * 門禁核心（零 hono 依賴）：token 計算 + 登入牆 HTML
 * gate.ts（hono 中間件，生產模式）與 vite.config.ts（connect 中間件，dev 預覽）共用
 */
import { createHmac, timingSafeEqual } from "node:crypto";
import { readFileSync } from "node:fs";

// 直接從 .env 文件讀取——vite dev server 熱更新時不會重讀 process.env，
// 但會重新執行本模塊；從文件讀保證 ACCESS_CODE 修改即時生效
export function envFromFile(name: string): string {
  try {
    const m = readFileSync(".env", "utf8").match(new RegExp(`^${name}=(.*)$`, "m"));
    if (m) return m[1].trim();
  } catch {}
  return process.env[name] ?? "";
}

const CODE = envFromFile("ACCESS_CODE");
const SECRET = envFromFile("APP_SECRET") || "etf-gate-fallback-secret";

export const COOKIE_NAME = "etf_auth";
export const COOKIE_MAX_AGE = 30 * 24 * 3600; // 30 天
export const gateEnabled = CODE.length > 0;

export function expectedToken(): string {
  return createHmac("sha256", SECRET).update(`etf-gate-v1:${CODE}`).digest("hex");
}

export function safeEq(a: string, b: string): boolean {
  const ba = Buffer.from(a), bb = Buffer.from(b);
  return ba.length === bb.length && timingSafeEqual(ba, bb);
}

export function verifyCode(code: string): boolean {
  return gateEnabled && code.length > 0 && safeEq(code, CODE);
}

export function cookieAuthed(cookieHeader: string | undefined | null): boolean {
  if (!cookieHeader) return false;
  const m = cookieHeader.match(new RegExp(`(?:^|;\\s*)${COOKIE_NAME}=([^;]+)`));
  if (!m) return false;
  try { return safeEq(decodeURIComponent(m[1]), expectedToken()); } catch { return false; } // 畸形 % 序列不得炸掉中間件
}

// 登入限流（進程內滑動窗口）：每 IP 10 分鐘最多 10 次嘗試，防在線暴力破解 ACCESS_CODE
const attempts = new Map<string, number[]>();
export function loginThrottle(ip: string): boolean {
  const now = Date.now(), win = 10 * 60 * 1000, max = 10;
  const arr = (attempts.get(ip) ?? []).filter(t => now - t < win);
  if (arr.length >= max) { attempts.set(ip, arr); return false; }
  arr.push(now); attempts.set(ip, arr);
  if (attempts.size > 1000) attempts.clear(); // 防內存膨脹
  return true;
}

export const LOGIN_HTML = `<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex,nofollow" />
<title>私人訪問 · ETF 組合追蹤</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { min-height: 100vh; background: #0a0f1c; color: #e2e8f0; display: flex; align-items: center; justify-content: center; font-family: -apple-system, "PingFang TC", "Microsoft JhengHei", sans-serif; padding: 24px; }
  .card { width: 100%; max-width: 360px; background: #0f1729; border: 1px solid #1e293b; border-radius: 14px; padding: 28px; }
  h1 { font-size: 17px; font-weight: 700; color: #fff; margin-bottom: 6px; }
  .sub { font-size: 12px; color: #64748b; margin-bottom: 20px; line-height: 1.6; }
  input { width: 100%; padding: 11px 14px; border-radius: 9px; border: 1px solid #334155; background: #0a0f1c; color: #e2e8f0; font-size: 15px; letter-spacing: 1px; outline: none; text-align: center; }
  input:focus { border-color: #38bdf8; }
  button { width: 100%; margin-top: 12px; padding: 11px; border-radius: 9px; border: 1px solid rgba(56,189,248,.4); background: rgba(56,189,248,.15); color: #7dd3fc; font-size: 14px; font-weight: 600; cursor: pointer; }
  button:hover { background: rgba(56,189,248,.25); }
  .err { display: none; margin-top: 10px; font-size: 12px; color: #fb7185; text-align: center; }
  .lock { text-align: center; font-size: 26px; margin-bottom: 12px; }
</style>
</head>
<body>
<div class="card">
  <div class="lock">🔒</div>
  <h1>私人投資組合追蹤</h1>
  <p class="sub">此網站設有訪問門禁。請輸入訪問密碼繼續。<br/>（密碼由網站擁有者保管，30 天內免重輸）</p>
  <input id="code" type="password" placeholder="訪問密碼" autocomplete="off" />
  <button id="go">進入</button>
  <p class="err" id="err">密碼不正確，請重試</p>
</div>
<script>
  async function submit() {
    const code = document.getElementById('code').value.trim();
    if (!code) return;
    const r = await fetch('/api/auth/login', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }), credentials: 'include',
    });
    if (r.ok) { location.reload(); }
    else { document.getElementById('err').style.display = 'block'; }
  }
  document.getElementById('go').onclick = submit;
  document.getElementById('code').addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });
  document.getElementById('code').focus();
</script>
</body>
</html>`;
