/**
 * 雙引擎行情提供器（修復「回報不更新 / fetch failed」的根因）
 *
 * ROOT CAUSE：運行環境的出口防火牆只放行 Kimi 系域名——
 *   query1.finance.yahoo.com / googleapis / api.search.brave.com 全部 TCP 連接失敗（curl 返回碼 000），
 *   而 agent-gw.kimi.com 與 api.moonshot.cn 可達。
 * 因此所有行情請求改為雙引擎：
 *   引擎 1（直連 Yahoo v8）——開放網絡環境下最快，6 秒超時快速失敗；
 *   引擎 2（agent-gw 網關代理 yahoo_finance 數據源）——受限環境下的可用路徑，90 秒超時。
 * 調用方無需感知環境差異：fetchQuote / fetchCloses 自動直連優先、網關兜底。
 */
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

async function tf(url: string, opts: RequestInit = {}, ms = 6000): Promise<Response> {
  return fetch(url, { ...opts, signal: AbortSignal.timeout(ms) });
}

// ---- agent-gw 配置：env 優先，否則讀 ~/.kimi/agent-gw.json（與 Python SDK 同一套憑證）----
interface GwCfg { apiKey: string; baseUrl: string }
let gwCfg: GwCfg | null | undefined;
function getGwCfg(): GwCfg | null {
  if (gwCfg !== undefined) return gwCfg;
  try {
    if (process.env.AGENT_GW_API_KEY) {
      gwCfg = { apiKey: process.env.AGENT_GW_API_KEY, baseUrl: process.env.AGENT_GW_BASE_URL ?? "https://agent-gw.kimi.com/coding" };
    } else {
      const j = JSON.parse(readFileSync(join(homedir(), ".kimi", "agent-gw.json"), "utf8"));
      gwCfg = j?.api_key ? { apiKey: j.api_key, baseUrl: j.base_url ?? "https://agent-gw.kimi.com/coding" } : null;
    }
  } catch { gwCfg = null; }
  return gwCfg;
}

// 21 只並發打網關會偶發限流（實測 ASHR/XLB/XLV 間歇失敗、重試即好）——失敗自動重試 2 次，指數退避
async function gwCall(apiName: string, params: Record<string, unknown>, attempt = 0): Promise<string | null> {
  const cfg = getGwCfg();
  if (!cfg) return null;
  try {
    // 並發抖動：錯開 0-2 秒，避免 21 隻同瞬間打到網關
    if (attempt === 0) await new Promise(r => setTimeout(r, Math.random() * 2000));
    const r = await tf(`${cfg.baseUrl}/v1/tools`, {
      method: "POST",
      headers: { Authorization: `Bearer ${cfg.apiKey}`, "Content-Type": "application/json" },
      body: JSON.stringify({ method: "call_data_source_tool", params: { data_source_name: "yahoo_finance", api_name: apiName, params } }),
    }, 90000);
    const j: any = await r.json();
    if (!j?.is_success) throw new Error("datasource returned failure");
    const files: any[] = j.files ?? [];
    return files[0]?.content ?? null;
  } catch {
    if (attempt < 2) {
      await new Promise(r => setTimeout(r, 2000 * (attempt + 1)));
      return gwCall(apiName, params, attempt + 1);
    }
    return null;
  }
}

// 正規 CSV 解析（狀態機）：get_stock_info 的 longBusinessSummary 等字段含引號內逗號/換行，
// naive split 會列錯位（實測 VOO 價格被移成 15.42）——必須處理 RFC4180 引號規則
function parseCsvRows(text: string): string[][] {
  const rows: string[][] = [];
  let cur: string[] = [], field = "", inQ = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQ) {
      if (ch === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; } else inQ = false;
      } else field += ch;
    } else if (ch === '"') inQ = true;
    else if (ch === ",") { cur.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      cur.push(field); field = "";
      if (cur.length > 1 || cur[0] !== "") rows.push(cur);
      cur = [];
    } else field += ch;
  }
  if (field !== "" || cur.length) { cur.push(field); rows.push(cur); }
  return rows;
}

function parseClosesCsv(csv: string): { date: string; close: number; volume?: number }[] {
  const rows = parseCsvRows(csv);
  if (rows.length < 2) return [];
  const hdr = rows[0];
  const di = hdr.indexOf("Date"), ci = hdr.indexOf("Close"), vi = hdr.indexOf("Volume");
  if (di < 0 || ci < 0) return [];
  const out: { date: string; close: number; volume?: number }[] = [];
  for (const cols of rows.slice(1)) {
    const close = parseFloat(cols[ci]);
    const volume = vi >= 0 ? parseFloat(cols[vi]) : NaN;
    if (cols[di] && isFinite(close)) out.push({ date: cols[di].slice(0, 10), close, ...(isFinite(volume) ? { volume } : {}) });
  }
  return out;
}

function parseInfoCsv(csv: string): Record<string, string> {
  const rows = parseCsvRows(csv);
  if (rows.length < 2) return {};
  const out: Record<string, string> = {};
  rows[0].forEach((h, i) => { out[h] = rows[1][i] ?? ""; });
  return out;
}

// ---- 通用數據源調用（給 pipeline 等新通道用）----
// 專家新聞搜索等任意 agent-gw 數據源；回傳 files[0].content（通常是 CSV 文本），失敗回 null
export async function gwDatasourceCall(dataSource: string, apiName: string, params: Record<string, unknown>, attempt = 0): Promise<string | null> {
  const cfg = getGwCfg();
  if (!cfg) return null;
  try {
    if (attempt === 0) await new Promise(r => setTimeout(r, Math.random() * 1500));
    const r = await tf(`${cfg.baseUrl}/v1/tools`, {
      method: "POST",
      headers: { Authorization: `Bearer ${cfg.apiKey}`, "Content-Type": "application/json" },
      body: JSON.stringify({ method: "call_data_source_tool", params: { data_source_name: dataSource, api_name: apiName, params } }),
    }, 90000);
    const j: any = await r.json();
    if (!j?.is_success) throw new Error("datasource returned failure");
    const files: any[] = j.files ?? [];
    return files[0]?.content ?? null;
  } catch {
    if (attempt < 2) {
      await new Promise(r => setTimeout(r, 2000 * (attempt + 1)));
      return gwDatasourceCall(dataSource, apiName, params, attempt + 1);
    }
    return null;
  }
}

// 通用 CSV → 記錄數組（復用 RFC4180 狀態機解析器）
export function csvToRecords(csv: string): Record<string, string>[] {
  const rows = parseCsvRows(csv);
  if (rows.length < 2) return [];
  const hdr = rows[0];
  return rows.slice(1).filter(cols => cols.some(c => c !== ""))
    .map(cols => Object.fromEntries(hdr.map((h, i) => [h, cols[i] ?? ""])));
}

export interface DayClose { date: string; close: number; volume?: number }
export interface QuotePx { price: number; prevClose: number; currency: string }

// ---- 日線收盤價序列 ----
export async function fetchCloses(ticker: string, range: "3mo" | "6mo" | "1y" | "2y" = "1y"): Promise<DayClose[] | null> {
  // 引擎 1：直連 Yahoo v8
  try {
    const r = await tf(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=${range}&interval=1d`, { headers: { "User-Agent": "Mozilla/5.0" } });
    if (r.ok) {
      const j: any = await r.json();
      const res = j?.chart?.result?.[0];
      const ts: number[] = res?.timestamp ?? [];
      const q0 = res?.indicators?.quote?.[0];
      const closes: (number | null)[] = q0?.close ?? [];
      const vols: (number | null)[] = q0?.volume ?? [];
      const out: DayClose[] = [];
      ts.forEach((t, i) => { const c = closes[i]; if (c != null && isFinite(c)) out.push({ date: new Date(t * 1000).toISOString().slice(0, 10), close: c, ...(vols[i] != null && isFinite(vols[i]!) ? { volume: vols[i]! } : {}) }); });
      if (out.length) return out;
    }
  } catch { /* 直連失敗，落網關 */ }
  // 引擎 2：agent-gw 網關
  const csv = await gwCall("get_historical_stock_prices", { ticker, file_path: `/tmp/md_${ticker}.csv`, period: range, interval: "1d" });
  if (!csv) return null;
  const out = parseClosesCsv(csv);
  return out.length ? out : null;
}

// ---- 最新報價（實時價 + 前收） ----
export async function fetchQuote(ticker: string): Promise<QuotePx | null> {
  // 引擎 1：直連 Yahoo v8 meta
  try {
    const r = await tf(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?interval=1d&range=5d`, { headers: { "User-Agent": "Mozilla/5.0" } });
    if (r.ok) {
      const j: any = await r.json();
      const meta = j?.chart?.result?.[0]?.meta;
      if (meta?.regularMarketPrice) {
        // chartPreviousClose 是 5d 區間「之前」的收盤價 → 會把 5 日漲跌當成日漲跌；
        // 真正的前收 = 5d 序列倒數第二個有效收盤
        const closes: (number | null)[] = j?.chart?.result?.[0]?.indicators?.quote?.[0]?.close ?? [];
        const valid = closes.filter((c): c is number => c != null && isFinite(c));
        const prev = valid.length >= 2 ? valid[valid.length - 2] : (meta.previousClose ?? meta.chartPreviousClose ?? meta.regularMarketPrice);
        return { price: meta.regularMarketPrice, prevClose: prev, currency: meta.currency ?? "USD" };
      }
    }
  } catch { /* 落網關 */ }
  // 引擎 2：agent-gw get_stock_info
  const csv = await gwCall("get_stock_info", { ticker, file_path: `/tmp/md_info_${ticker}.csv` });
  if (!csv) return null;
  const kv = parseInfoCsv(csv);
  const price = parseFloat(kv.regularMarketPrice ?? kv.navPrice ?? "");
  const prevClose = parseFloat(kv.previousClose ?? kv.regularMarketPreviousClose ?? "");
  if (!isFinite(price) || price <= 0) return null;
  return { price, prevClose: isFinite(prevClose) && prevClose > 0 ? prevClose : price, currency: kv.currency || "USD" };
}
