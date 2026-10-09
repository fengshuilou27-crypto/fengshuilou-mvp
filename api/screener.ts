/**
 * 候選 ETF 篩選器 — 數據抓取層（2026-09-11 Phase 11 新增）
 *
 * 職責：攞候選 ETF 嘅一年日線 + 基本資料（get_stock_info），同埋 19 隻持倉 + ACWI
 * 嘅一年日線，交俾 contracts/screener.ts 嘅純函數計指標同判語。
 *
 * 工程模式複用 correlation.ts / quotes.ts：
 * - 持倉行情 bundle 6 小時緩存 + in-flight 去重（篩多隻候選唔使逐次重拉 20 隻）
 * - 候選結果按 ticker 6 小時緩存
 * - 全部失敗唔寫緩存；部分缺失喺 failed 誠實列出
 */
import { fetchCloses, gwDatasourceCall, csvToRecords, type DayClose } from "./marketdata";
import { CURRENT_WEIGHTS } from "@contracts/rebalance"; // 葉子模組直取，避免 pipeline↔screener 循環依賴
import {
  dailyReturnsByDate, pairCorr, retStats, weightedPortfolioReturns, screenVerdict,
  SCREEN_HONEST, type ScreenMetrics, type ScreenResult, type ScreenResponse,
} from "@contracts/screener";

const HOLDINGS = Object.keys(CURRENT_WEIGHTS); // 19 隻持倉
const CACHE_TTL = 6 * 60 * 60 * 1000; // 6 小時（日線級數據，同 correlation.ts 口徑）

// ---- 持倉行情 bundle（6h 緩存 + in-flight 去重）----
interface Bundle {
  closesBy: Record<string, DayClose[]>;
  retsBy: Record<string, Map<string, number>>;
  failed: string[];
  asOfDate: string | null;
}
let bundleCache: { at: number; data: Bundle } | null = null;
let bundleInflight: Promise<Bundle> | null = null;

function getBundle(): Promise<Bundle> {
  if (bundleCache && Date.now() - bundleCache.at < CACHE_TTL) return Promise.resolve(bundleCache.data);
  if (bundleInflight) return bundleInflight;
  bundleInflight = computeBundle().finally(() => { bundleInflight = null; });
  return bundleInflight;
}

async function computeBundle(): Promise<Bundle> {
  const want = [...HOLDINGS, "ACWI"];
  const settled = await Promise.allSettled(want.map(t => fetchCloses(t, "1y")));
  const closesBy: Record<string, DayClose[]> = {};
  const retsBy: Record<string, Map<string, number>> = {};
  const failed: string[] = [];
  let asOfDate: string | null = null;
  settled.forEach((r, i) => {
    const rows = r.status === "fulfilled" ? r.value : null;
    if (rows && rows.length >= 60) {
      closesBy[want[i]] = rows;
      retsBy[want[i]] = dailyReturnsByDate(rows);
      const last = rows[rows.length - 1].date;
      if (!asOfDate || last < asOfDate) asOfDate = last;
    } else failed.push(want[i]);
  });
  const data: Bundle = { closesBy, retsBy, failed, asOfDate };
  // 只要唔係全軍覆沒都緩存（partial 會喺結果標明）；全失敗留俾下次重試
  if (Object.keys(retsBy).length > 0) bundleCache = { at: Date.now(), data };
  return data;
}

// ---- 候選基本資料（Yahoo get_stock_info，經雙引擎行情檔嘅閘道；失敗 → 全部 null，誠實顯示「—」）----
interface InfoFields { name: string | null; fundFamily: string | null; aumUsd: number | null; yieldPct: number | null; expenseRatioPct: number | null }
async function fetchInfo(ticker: string): Promise<InfoFields> {
  const out: InfoFields = { name: null, fundFamily: null, aumUsd: null, yieldPct: null, expenseRatioPct: null };
  const csv = await gwDatasourceCall("yahoo_finance", "get_stock_info", { ticker, file_path: `/tmp/screen_${ticker}.csv` });
  if (!csv) return out;
  const rec = csvToRecords(csv)[0];
  if (!rec) return out;
  out.name = rec.longName?.trim() || rec.shortName?.trim() || null;
  out.fundFamily = rec.fundFamily?.trim() || null;
  const aum = parseFloat(rec.totalAssets ?? "");
  if (isFinite(aum) && aum > 0) out.aumUsd = aum;
  // Yahoo ETF 嘅 yield 欄係小數（0.0797 = 7.97%）；dividendYield 對 ETF 有時已係百分數——兩個形態都接住
  const y1 = parseFloat(rec.yield ?? "");
  const y2 = parseFloat(rec.dividendYield ?? "");
  const toPct = (v: number) => (v > 0 && v < 1 ? v * 100 : v);
  if (isFinite(y1) && y1 > 0) out.yieldPct = Math.round(toPct(y1) * 100) / 100;
  else if (isFinite(y2) && y2 > 0) out.yieldPct = Math.round(toPct(y2) * 100) / 100;
  // 開支比率：呢個數據源嘅 annualReportExpenseRatio 係百分制（0.35 = 0.35%，唔係小數——
  // 實測 JEPI 返回 0.35；yield 欄先係小數制）。合理區間 0.01–5%，超界視為缺數（唔估）。
  const er = parseFloat(rec.annualReportExpenseRatio ?? rec.netExpenseRatio ?? "");
  if (isFinite(er) && er >= 0.01 && er <= 5) out.expenseRatioPct = Math.round(er * 100) / 100;
  return out;
}

// ---- 候選結果緩存（按 ticker，6h）----
const resultCache = new Map<string, { at: number; data: ScreenResponse }>();
const resultInflight = new Map<string, Promise<ScreenResponse>>();

export function screenCandidateEtf(raw: string): Promise<ScreenResponse> {
  const ticker = raw.trim().toUpperCase();
  if (!/^[A-Z][A-Z0-9.\-]{0,11}$/.test(ticker)) {
    return Promise.resolve({ ok: false, error: "代碼格式唔啱——請輸入美股/ETF ticker（例如 JEPI、SCHD、FDEV）" });
  }
  if (HOLDINGS.includes(ticker)) {
    return Promise.resolve({ ok: false, error: `${ticker} 已經係現有持倉——佢嘅重疊情況睇上面嘅分組敞口同高相關配對就得` });
  }
  const hit = resultCache.get(ticker);
  if (hit && Date.now() - hit.at < CACHE_TTL) return Promise.resolve(hit.data);
  const flying = resultInflight.get(ticker);
  if (flying) return flying;
  const p = computeScreen(ticker)
    .then(data => { if (data.ok) resultCache.set(ticker, { at: Date.now(), data }); return data; })
    .finally(() => { resultInflight.delete(ticker); });
  resultInflight.set(ticker, p);
  return p;
}

async function computeScreen(ticker: string): Promise<ScreenResponse> {
  const [candCloses, info, bundle] = await Promise.all([fetchCloses(ticker, "1y"), fetchInfo(ticker), getBundle()]);
  if (!candCloses || candCloses.length < 60) {
    return { ok: false, error: `揾唔到 ${ticker} 嘅一年日線行情——請確認係美國上市代碼（或行情源暫時不可用，稍後再試）` };
  }
  const holdingsAvail = HOLDINGS.filter(t => bundle.retsBy[t]);
  if (holdingsAvail.length < 10) {
    return { ok: false, error: "持倉行情源暫時大部份不可用，無法計算重疊度——稍後再試" };
  }

  const candRets = dailyReturnsByDate(candCloses);
  const portRets = weightedPortfolioReturns(bundle.retsBy, CURRENT_WEIGHTS);
  const corrToPortfolio = pairCorr(candRets, portRets);

  // 逐持倉相關 → 權重加權平均 + |ρ| 最高配對
  let wSum = 0, cSum = 0, cN = 0;
  let maxPair: { holding: string; corr: number } | null = null;
  for (const h of holdingsAvail) {
    const c = pairCorr(candRets, bundle.retsBy[h]);
    if (c == null) continue;
    const w = CURRENT_WEIGHTS[h] ?? 0;
    wSum += w; cSum += w * c; cN++;
    if (!maxPair || Math.abs(c) > Math.abs(maxPair.corr)) maxPair = { holding: h, corr: c };
  }
  const avgCorrToHoldings = cN && wSum > 0 ? Math.round((cSum / wSum) * 1000) / 1000 : null;

  const metrics: ScreenMetrics = {
    ticker,
    name: info.name,
    fundFamily: info.fundFamily,
    aumUsd: info.aumUsd,
    yieldPct: info.yieldPct,
    expenseRatioPct: info.expenseRatioPct,
    stats1y: retStats(candCloses),
    corrToPortfolio,
    avgCorrToHoldings,
    maxPair,
    corrToVOO: bundle.retsBy.VOO ? pairCorr(candRets, bundle.retsBy.VOO) : null,
    corrToACWI: bundle.retsBy.ACWI ? pairCorr(candRets, bundle.retsBy.ACWI) : null,
  };
  const bench = {
    vooRet1y: bundle.closesBy.VOO ? retStats(bundle.closesBy.VOO).ret : null,
    vooVol1y: bundle.closesBy.VOO ? retStats(bundle.closesBy.VOO).vol : null,
    acwiRet1y: bundle.closesBy.ACWI ? retStats(bundle.closesBy.ACWI).ret : null,
  };
  const result: ScreenResult = {
    ...metrics,
    bench,
    verdict: screenVerdict(metrics, bench),
    asOf: new Date().toISOString(),
    asOfDate: bundle.asOfDate,
    failed: bundle.failed,
    honest: SCREEN_HONEST,
  };
  return { ok: true, result };
}
