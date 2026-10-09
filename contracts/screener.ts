/**
 * 候選 ETF 篩選器 — 純函數層（2026-09-11 Phase 11 新增）
 *
 * 背景：用戶問「covered call ETF 同其他 ETF 相關性係咪都好高？總回報會唔會打贏？
 * 應唔應該喺站內做篩選？」——實測答案：相關性的確高（0.68–0.95），但牛市總回報
 * 全部跑輸本尊 8–28pp（upside 被賣走）。所以呢個篩選器唔係「高分就加」，
 * 而係對候選 ETF 俾出**誠實判語**：重疊度、回報、風險、成本一次過攤開。
 *
 * 設計分工（同 perfStats.ts 同一模式）：
 * - 呢個檔案 = 零副作用純函數 + 類型（前端後端共用，單測鎖死口徑）
 * - api/screener.ts = 數據抓取（fetchCloses / get_stock_info）+ 緩存，調用呢度嘅函數
 *
 * 判語規則係寫死嘅白名單規則（唔經 LLM，唔會編造）：
 *   ρ(候選, 組合) ≥ 0.8 且回報 < VOO → avoid（高重疊兼跑輸——唔建議加入）
 *   ρ(候選, 組合) ≥ 0.8 且回報 ≥ VOO → substitute（高重疊但有動能——只宜替代式持有）
 *   ρ(候選, 組合) < 0.5 → diversifier（真分散價值）
 *   其餘（0.5–0.8）→ limited（有限分散價值）
 *
 * 誠實性聲明（UI 必須保留）：相關性係歷史價格行為代理，唔係成分股穿透；
 * 危機時風險資產相關性趨向 1；歷史回報唔代表將來。
 */

export interface DayCloseLike { date: string; close: number }

export interface ScreenStats {
  ret: number;  // 區間總回報（小數，0.18 = +18%）
  vol: number;  // 年化波動率（小數，日收益樣本標準差 × √252）
  mdd: number;  // 最大回撤（負小數，−0.089 = −8.9%）
}

export interface ScreenMetrics {
  ticker: string;
  name: string | null;
  fundFamily: string | null;
  aumUsd: number | null;          // 資產規模（美元）
  yieldPct: number | null;        // 分派率（%，Yahoo ETF yield 欄；冇就 null 顯示「—」）
  expenseRatioPct: number | null; // 開支比率（%，Yahoo 缺則 null——誠實顯示，唔估）
  stats1y: ScreenStats;
  corrToPortfolio: number | null;    // 同現有組合（凍結權重合成）日收益相關
  avgCorrToHoldings: number | null;  // 同持倉逐對相關嘅權重加權平均
  maxPair: { holding: string; corr: number } | null; // |ρ| 最高嘅單一持倉
  corrToVOO: number | null;
  corrToACWI: number | null;
}

export interface ScreenBench {
  vooRet1y: number | null;
  vooVol1y: number | null;
  acwiRet1y: number | null;
}

export type ScreenTier = "avoid" | "substitute" | "limited" | "diversifier";

export interface ScreenVerdict {
  tier: ScreenTier;
  headline: string;
  points: string[];
}

export interface ScreenResult extends ScreenMetrics {
  bench: ScreenBench;
  verdict: ScreenVerdict;
  asOf: string;
  asOfDate: string | null; // 行情序列最新共同日期
  failed: string[];        // 行情缺失嘅持倉（partial 時誠實列出）
  honest: string;          // 誠實聲明（固定文案，UI 展示）
}

export type ScreenResponse = { ok: true; result: ScreenResult } | { ok: false; error: string };

export const SCREEN_HONEST =
  "誠實聲明：相關性係歷史價格行為代理（近 1 年日收益，共同交易日對齊，每對最少 30 個樣本），唔係成分股穿透——本站冇 ETF 持倉明細數據；跌市時風險資產相關性會趨向 1，低相關唔保證跌市時分散；歷史回報唔代表將來。分派率高的策略（covered call/高息）分派多數係期權金或含本金返還，香港投資者另畀 30% 股息預扣稅——比較時睇總回報，唔好齋睇息率。";

// ---- 統計小工具（同 api/correlation.ts 口徑一致：逐對共同交易日對齊、≥30 樣本先出數）----
export function dailyReturnsByDate(rows: DayCloseLike[]): Map<string, number> {
  const m = new Map<string, number>();
  for (let i = 1; i < rows.length; i++) {
    const prev = rows[i - 1].close;
    if (prev > 0) m.set(rows[i].date, rows[i].close / prev - 1);
  }
  return m;
}

export function pearson(x: number[], y: number[]): number | null {
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

export function pairCorr(a: Map<string, number>, b: Map<string, number>): number | null {
  const xs: number[] = [], ys: number[] = [];
  for (const [d, r] of a) { const rb = b.get(d); if (rb != null) { xs.push(r); ys.push(rb); } }
  return pearson(xs, ys);
}

/** 單條收盤序列嘅總回報 / 年化波動 / 最大回撤 */
export function retStats(closes: DayCloseLike[]): ScreenStats {
  const n = closes.length;
  if (n < 2) return { ret: 0, vol: 0, mdd: 0 };
  const ret = closes[n - 1].close / closes[0].close - 1;
  const rets: number[] = [];
  let peak = closes[0].close, mdd = 0;
  for (let i = 1; i < n; i++) {
    const prev = closes[i - 1].close;
    if (prev > 0) rets.push(closes[i].close / prev - 1);
    peak = Math.max(peak, closes[i].close);
    if (peak > 0) mdd = Math.min(mdd, closes[i].close / peak - 1);
  }
  let vol = 0;
  if (rets.length >= 2) {
    const mean = rets.reduce((s, v) => s + v, 0) / rets.length;
    const variance = rets.reduce((s, v) => s + (v - mean) * (v - mean), 0) / (rets.length - 1);
    vol = Math.sqrt(variance * 252);
  }
  const r3 = (v: number) => Math.round(v * 1000) / 1000;
  return { ret: r3(ret), vol: r3(vol), mdd: r3(mdd) };
}

/**
 * 現有組合（凍結權重）嘅合成日收益序列：
 * 取所有可用持倉嘅共同交易日，權重按可用持倉歸一化（缺失持倉按比例攤分，failed 會喺結果列出）。
 */
export function weightedPortfolioReturns(
  retsBy: Record<string, Map<string, number>>,
  weights: Record<string, number>,
): Map<string, number> {
  const tickers = Object.keys(retsBy).filter(t => (weights[t] ?? 0) > 0 && retsBy[t].size > 0);
  if (!tickers.length) return new Map();
  let common: Set<string> = new Set(retsBy[tickers[0]].keys());
  for (const t of tickers.slice(1)) {
    const keys = new Set(retsBy[t].keys());
    common = new Set([...common].filter(d => keys.has(d)));
  }
  const wTotal = tickers.reduce((s, t) => s + weights[t], 0);
  const out = new Map<string, number>();
  if (wTotal <= 0) return out;
  for (const d of common) {
    let r = 0;
    for (const t of tickers) r += (weights[t] / wTotal) * (retsBy[t].get(d) ?? 0);
    out.set(d, r);
  }
  return out;
}

const pct1 = (v: number) => (v * 100).toFixed(1);

/** 誠實判語（白名單規則，唔經 LLM） */
export function screenVerdict(m: ScreenMetrics, bench: ScreenBench): ScreenVerdict {
  const corr = m.corrToPortfolio;
  const beats = bench.vooRet1y != null && m.stats1y.ret >= bench.vooRet1y;
  const cTxt = corr != null ? corr.toFixed(2) : "—";

  let tier: ScreenTier;
  let headline: string;
  if (corr != null && corr >= 0.8 && !beats) {
    tier = "avoid";
    headline = `同組合高度重疊（ρ=${cTxt}）兼回報唔及 VOO——唔建議加入：冇分散價值兼拖低回報。`;
  } else if (corr != null && corr >= 0.8 && beats) {
    tier = "substitute";
    headline = `同組合高度重疊（ρ=${cTxt}）但動能唔輸 VOO——只宜「替代式」持有（例如換走部分同系持倉），疊加會推高集中度。`;
  } else if (corr != null && corr < 0.5) {
    tier = "diversifier";
    headline = `同組合低相關（ρ=${cTxt}）——具真實分散價值；如信號面配合，可按 K7 首倉 ≤2pp 小注配置。`;
  } else {
    tier = "limited";
    headline = `同組合中等相關（ρ=${cTxt}）——有限分散價值；留意同最高相關持倉嘅重疊。`;
  }

  const points: string[] = [];
  if (m.maxPair && Math.abs(m.maxPair.corr) >= 0.75) {
    points.push(`同 ${m.maxPair.holding} ρ=${m.maxPair.corr.toFixed(2)}——近似重複曝光，買佢 ≈ 變相加注 ${m.maxPair.holding}。`);
  }
  if (m.yieldPct != null && m.yieldPct >= 6) {
    points.push(`分派率 ${m.yieldPct.toFixed(1)}% 屬高水平——covered call/高息類分派多數係期權金或含本金返還（ROC），香港投資者另畀 30% 股息預扣稅；比較時睇總回報，唔好齋睇息率。`);
  }
  if (bench.vooRet1y != null) {
    const diff = m.stats1y.ret - bench.vooRet1y;
    points.push(`近 1 年總回報 ${diff >= 0 ? "跑贏" : "跑輸"} VOO ${pct1(Math.abs(diff))}pp（${pct1(m.stats1y.ret)}% vs ${pct1(bench.vooRet1y)}%）。`);
  }
  if (bench.vooVol1y != null && m.stats1y.vol > 0 && m.stats1y.vol <= bench.vooVol1y * 0.75) {
    points.push(`波動 ${pct1(m.stats1y.vol)}% 明顯低過 VOO ${pct1(bench.vooVol1y)}%——防守性較強，如需降波動可作「替代式」選項。`);
  }
  if (m.expenseRatioPct != null && m.expenseRatioPct > 0.6) {
    points.push(`開支比率 ${m.expenseRatioPct.toFixed(2)}% 偏貴（VOO 約 0.03%）——長揸成本會持續侵蝕回報。`);
  }
  if (m.aumUsd != null && m.aumUsd < 500_000_000) {
    points.push(`資產規模較細——留意買賣差價同流動性。`);
  }
  return { tier, headline, points };
}
