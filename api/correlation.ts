/**
 * 持倉相關性 / 重複曝光分析（2026-09-07 Phase 7 新增）
 *
 * 回答用戶問題：「唔同 ETF 底層資產會唔會重複？相關性有冇考慮到？」
 * 方法（風險管理標準做法，無參數優化）：
 * ① 19 隻持倉 ETF 一年日線 → 逐對共同交易日對齊 → 日收益皮爾遜相關係數；
 * ② 高相關配對清單（|ρ|≥0.6 列出，≥0.75 視為近似重複曝光）；
 * ③ 底層敞口分組加總（與算法層 S9 組合熱度閘門同口徑，上限 30pp），
 *    組內平均相關 >0.75 標警示。
 *
 * 誠實性聲明（必須保留）：
 * - 呢個係**價格行為代理**，唔係持倉穿透（holdings look-through）——我哋冇 ETF
 *   成分股數據；VOO/XLV 呢類「同市場板塊」重疊係由相關性側寫推斷。
 * - 歷史相關性喺市場危機時會趨向 1（correlation breakdown），呢度嘅低相關
 *   唔保證分散效果喺跌市時成立。
 * - 窗口 = 近 1 年日收益，文獻常用窗口，唔做窗口優化。
 *
 * 工程模式複用 quotes.ts / algo.ts：雙引擎行情（fetchCloses）、Promise.allSettled、
 * per-ticker 失敗標記、status ok/partial/unavailable、全部失敗唔寫緩存、6 小時緩存
 * + in-flight 去重。
 */
import { fetchCloses } from "./marketdata";
import { CURRENT_WEIGHTS } from "./pipeline";
import type { CorrelationReport, CorrGroup, CorrPair } from "@contracts/types";

const TICKERS = Object.keys(CURRENT_WEIGHTS); // 19 隻持倉 ETF
const CACHE_TTL = 6 * 60 * 60 * 1000; // 6 小時（日線級數據，毋須更密）

// 底層敞口分組（同 api/algo.ts HEAT_GROUPS 口徑對齊，另補齊 IBIT/債券組令 19 隻全覆蓋）
const EXPOSURE_GROUPS: { name: string; members: string[]; note: string }[] = [
  { name: "美股大盤系", members: ["VOO", "XLV"], note: "標普500 + 醫療板塊，底層同為美股大公司" },
  { name: "半導體韓台鏈", members: ["SMH", "EWY", "EWT"], note: "三星/台積電與費半指數高度聯動" },
  { name: "HALO重資產", members: ["XLE", "XLB", "IFRA"], note: "能源/材料/基建，同受商品周期驅動" },
  { name: "中國系", members: ["ASHR", "MCHI", "EWH"], note: "A股+離岸中資+香港，中國增長敞口三重叠加" },
  { name: "商品系", members: ["GLD", "SLV", "COPX"], note: "金銀銅同屬貴金屬/工業金屬避險-通脹交易" },
  { name: "歐洲系", members: ["VGK"], note: "歐洲股票，單一工具無組內重複" },
  { name: "加密系", members: ["IBIT"], note: "比特幣現貨 ETF，獨立風險因子" },
  { name: "債券現金系", members: ["TLT", "BND", "SGOV"], note: "長債/綜合債/短債，利率久期敞口" },
];

// ---- 統計小工具 ----
function dailyReturnsByDate(rows: { date: string; close: number }[]): Map<string, number> {
  const m = new Map<string, number>();
  for (let i = 1; i < rows.length; i++) {
    const prev = rows[i - 1].close;
    if (prev > 0) m.set(rows[i].date, rows[i].close / prev - 1);
  }
  return m;
}

// 皮爾遜相關：逐對用兩者共同交易日期對齊（美股/港股/A股/加密假期唔同，全局交集會丟太多樣本）
function pearson(x: number[], y: number[]): number | null {
  const n = Math.min(x.length, y.length);
  if (n < 30) return null; // 樣本太少唔出數（誠實原則）
  const xs = x.slice(0, n), ys = y.slice(0, n);
  const mx = xs.reduce((s, v) => s + v, 0) / n, my = ys.reduce((s, v) => s + v, 0) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - mx, dy = ys[i] - my;
    sxy += dx * dy; sxx += dx * dx; syy += dy * dy;
  }
  if (sxx === 0 || syy === 0) return null;
  return Math.round((sxy / Math.sqrt(sxx * syy)) * 1000) / 1000;
}

function pairCorr(a: Map<string, number>, b: Map<string, number>): number | null {
  const xs: number[] = [], ys: number[] = [];
  for (const [d, r] of a) { const rb = b.get(d); if (rb != null) { xs.push(r); ys.push(rb); } }
  return pearson(xs, ys);
}

// ---- 主流程（6 小時緩存 + in-flight 去重）----
let cache: { at: number; data: CorrelationReport } | null = null;
let inflight: Promise<CorrelationReport> | null = null;

export function getCorrelationReport(): Promise<CorrelationReport> {
  if (cache && Date.now() - cache.at < CACHE_TTL) return Promise.resolve(cache.data);
  if (inflight) return inflight;
  inflight = computeCorrelationReport().finally(() => { inflight = null; });
  return inflight;
}

async function computeCorrelationReport(): Promise<CorrelationReport> {
  const settled = await Promise.allSettled(TICKERS.map(t => fetchCloses(t, "1y")));
  const retsBy: Record<string, Map<string, number>> = {};
  const failed: string[] = [];
  let commonLatest: string | null = null;
  settled.forEach((r, i) => {
    const rows = r.status === "fulfilled" ? r.value : null;
    if (rows && rows.length >= 60) {
      retsBy[TICKERS[i]] = dailyReturnsByDate(rows);
      const last = rows[rows.length - 1].date;
      if (!commonLatest || last < commonLatest) commonLatest = last;
    } else failed.push(TICKERS[i]);
  });
  const ok = Object.keys(retsBy);
  const status: CorrelationReport["status"] =
    failed.length === 0 ? "ok" : ok.length === 0 ? "unavailable" : "partial";

  // 全部配對相關（171 對），只保留 |ρ|≥0.6 嘅有意義高相關配對
  const pairs: CorrPair[] = [];
  for (let i = 0; i < ok.length; i++) {
    for (let j = i + 1; j < ok.length; j++) {
      const c = pairCorr(retsBy[ok[i]], retsBy[ok[j]]);
      if (c != null && Math.abs(c) >= 0.6) pairs.push({ a: ok[i], b: ok[j], corr: c });
    }
  }
  pairs.sort((x, y) => Math.abs(y.corr) - Math.abs(x.corr));

  // 分組敞口：權重合計 + 組內平均相關
  const groups: CorrGroup[] = EXPOSURE_GROUPS.map(g => {
    const weight = g.members.reduce((s, t) => s + (CURRENT_WEIGHTS[t] ?? 0), 0);
    const intra: number[] = [];
    for (let i = 0; i < g.members.length; i++) {
      for (let j = i + 1; j < g.members.length; j++) {
        const [a, b] = [g.members[i], g.members[j]];
        if (retsBy[a] && retsBy[b]) { const c = pairCorr(retsBy[a], retsBy[b]); if (c != null) intra.push(c); }
      }
    }
    const intraCorr = intra.length ? Math.round((intra.reduce((s, v) => s + v, 0) / intra.length) * 1000) / 1000 : null;
    return { name: g.name, members: g.members, note: g.note, weight, intraCorr, over: weight > 30 };
  });

  const dup = pairs.filter(p => p.corr >= 0.75);
  const days = ok.length ? Math.min(...ok.map(t => retsBy[t].size)) : 0;
  const summary = status === "unavailable"
    ? "行情源全部不可用，相關性分析無法計算；下一小時自動重試。"
    : `${status === "partial" ? `部分行情缺失（${failed.join("、")}）。` : ""}近 1 年日收益（每對最少 30 個共同交易日）：${dup.length} 對高度相關（ρ≥0.75，近似重複曝光），${pairs.length - dup.length} 對中度相關（0.6≤ρ<0.75）。分組敞口與算法 S9 熱度閘門同口徑（上限 30pp）。注意：相關性係歷史價格行為代理，唔係成分股穿透；危機時風險資產相關性會趨向 1。`;

  const data: CorrelationReport = { asOf: new Date().toISOString(), asOfDate: commonLatest, status, days, pairs, groups, failed, summary };
  if (status !== "unavailable") cache = { at: Date.now(), data };
  return data;
}
