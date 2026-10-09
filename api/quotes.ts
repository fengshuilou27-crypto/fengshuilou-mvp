/**
 * 实时行情层：每次打开网页时拉取整个 ETF 组合的最新价格。
 * - Yahoo v8 chart API（v7 quote 需要 cookie/crumb，v8 更稳）
 * - 服务端 60 秒缓存，避免每次页面打开都打 21 次 Yahoo
 * - 单 ticker 失败不拖垮整体：per-ticker 标记，quotesStatus = ok | partial | unavailable
 */
import type { Quote, QuotesResponse } from "../contracts/types";
import { fetchQuote } from "./marketdata";

const TICKERS = [
  "VOO", "SMH", "ASHR", "MCHI", "EWH", "GLD", "SLV", "COPX", "XLE", "XLB",
  "IFRA", "EWY", "EWT", "XLV", "VGK", "IBIT", "TLT", "BND", "SGOV",
  "ACWI", "AGG", // 基准
];

async function fetchOne(ticker: string): Promise<Quote | null> {
  // 雙引擎（直連 Yahoo → agent-gw 網關兜底），修復受限網絡下全部失敗的問題
  const qx = await fetchQuote(ticker);
  if (!qx) return null;
  const changePct = qx.prevClose > 0 ? ((qx.price - qx.prevClose) / qx.prevClose) * 100 : 0;
  return {
    ticker,
    price: Math.round(qx.price * 100) / 100,
    prevClose: Math.round(qx.prevClose * 100) / 100,
    changePct: Math.round(changePct * 100) / 100,
    currency: qx.currency,
    asOf: new Date().toISOString(),
  };
}

// ---- 60 秒服务端缓存 + in-flight 去重 ----
let cache: { at: number; data: QuotesResponse } | null = null;
const CACHE_TTL = 60 * 1000;
// 冷啟動全量抓取 21 只需 1-2 分鐘（網關限流退避）；並發請求共享同一個 in-flight Promise，
// 避免多個用戶同時打開頁面時各自觸發一輪全量抓取、互相加重限流
let inflight: Promise<QuotesResponse> | null = null;

export async function getQuotes(): Promise<QuotesResponse> {
  if (cache && Date.now() - cache.at < CACHE_TTL) return cache.data;
  if (inflight) return inflight;
  inflight = fetchAll().finally(() => { inflight = null; });
  return inflight;
}

async function fetchAll(): Promise<QuotesResponse> {
  const results = await Promise.allSettled(TICKERS.map(fetchOne));
  const quotes: Record<string, Quote> = {};
  const failed: string[] = [];
  results.forEach((r, i) => {
    const q = r.status === "fulfilled" ? r.value : null;
    if (q) quotes[q.ticker] = q;
    else failed.push(TICKERS[i]);
  });

  const status: QuotesResponse["status"] =
    failed.length === 0 ? "ok" : Object.keys(quotes).length === 0 ? "unavailable" : "partial";
  const data: QuotesResponse = { asOf: new Date().toISOString(), status, quotes, failed };
  // 全部失败时不写缓存（下次请求立刻重试），部分/全部成功才缓存
  if (status !== "unavailable") cache = { at: Date.now(), data };
  return data;
}
