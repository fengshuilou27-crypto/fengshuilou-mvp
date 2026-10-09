/**
 * 訪問門禁 hono 層（生產模式）：登入端點 + 全域中間件。
 * 核心邏輯（token/HTML）在 gate-core.ts，與 vite.config.ts 的 dev 中間件共用。
 * - ACCESS_CODE 留空 = 門禁關閉（向後兼容）
 * - 無狀態 HMAC cookie，無需 DB；密碼只在服務端 .env，不下發前端 bundle
 */
import type { Context, Next } from "hono";
import { getCookie, setCookie } from "hono/cookie";
import {
  COOKIE_MAX_AGE, COOKIE_NAME, LOGIN_HTML,
  cookieAuthed, expectedToken, gateEnabled, loginThrottle, safeEq, verifyCode,
} from "./gate-core";

export { gateEnabled };

type RouteHandler = (c: Context) => unknown;

/** 登入/登出端點（必須開放，在 gateMiddleware 之前註冊） */
export function mountAuthRoutes(app: { post: (p: string, h: RouteHandler) => unknown; get: (p: string, h: RouteHandler) => unknown }) {
  app.post("/api/auth/login", async (c) => {
    if (!gateEnabled) return c.json({ ok: true, gate: "disabled" });
    const ip = c.req.header("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
    if (!loginThrottle(ip)) return c.json({ ok: false, error: "嘗試過於頻繁，請 10 分鐘後再試" }, 429);
    let code = "";
    try { code = String((await c.req.json())?.code ?? ""); } catch {}
    if (verifyCode(code)) {
      // Phase 13.3 修復：預覽係 iframe 嵌入（跨站上下文），SameSite=Lax 嘅 cookie
      // 會被瀏覽器當第三方 cookie 擋埋——登入成功但 cookie 存唔到 → 永遠彈返密碼頁。
      // https 環境必須 SameSite=None + Secure（Chrome 硬性要求兩者成對）；
      // 本地 http 開發就用返 Lax 唔加 Secure（否則 http 下 cookie 一樣存唔到）。
      const isHttps = c.req.header("x-forwarded-proto") === "https";
      setCookie(c, COOKIE_NAME, expectedToken(), {
        httpOnly: true, sameSite: isHttps ? "None" : "Lax", path: "/", maxAge: COOKIE_MAX_AGE,
        secure: isHttps,
      });
      return c.json({ ok: true });
    }
    return c.json({ ok: false }, 401);
  });
  app.get("/api/auth/logout", (c) => {
    const isHttps = c.req.header("x-forwarded-proto") === "https";
    setCookie(c, COOKIE_NAME, "", { httpOnly: true, sameSite: isHttps ? "None" : "Lax", path: "/", maxAge: 0, secure: isHttps });
    return c.json({ ok: true });
  });
}

/** 全域門禁中間件：未登入 → 頁面請求回登入牆 HTML，API/數據/資產請求回 401 */
export async function gateMiddleware(c: Context, next: Next) {
  if (!gateEnabled) return next();
  if (c.req.path.startsWith("/api/auth/")) return next();
  if (safeEq(getCookie(c, COOKIE_NAME) ?? "", expectedToken())) return next();
  const accept = c.req.header("accept") ?? "";
  const isPage = (!c.req.path.startsWith("/api/") && !c.req.path.includes(".")) || accept.includes("text/html");
  if (isPage && c.req.method === "GET") return c.html(LOGIN_HTML);
  return c.json({ error: "access required" }, 401);
}
