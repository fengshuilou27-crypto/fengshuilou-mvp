// ---- 專家學習環純函數層（2026-09-12，P0）----
// 目的：系統由「記錄錯誤」升級為「從錯誤學習」——專家權重按滾動命中率自動調整，
// 跑輸大盤時自動分辯「個別專家錯 / 專家全錯 / 大市環境問題」。
//
// 鐵律邊界（Bailey/López de Prado 過擬合閘）：
//   - 學習只調「權重」（expert factor），永不改規則、永不自動執行調倉
//   - 因子永遠夾 [0.5, 1.5]（與 contracts/expertWeights.ts 靜態表同口徑）
//   - 單次調幅 ≤0.1；樣本不足（decided<10）調幅減半 → ≤0.05；decided<3 完全不調
//   - 每次調整留賬（前值/後值/依據/樣本量），可審計、可回滚

export const FACTOR_MIN = 0.5;
export const FACTOR_MAX = 1.5;
export const FACTOR_NEUTRAL = 1.0;
export const MAX_WEEKLY_STEP = 0.1;
export const LEARN_MIN_SAMPLE = 3;    // 少於 3 個已到期信號 → 不調（統計上無意義）
export const LEARN_FULL_SAMPLE = 10;  // 滿 10 個先准全幅調整（同 backtest.ts insufficient 口徑）

export interface FactorProposal {
  expertId: string;
  prev: number;          // 現行因子（靜態表或上一份學習快照）
  next: number;          // 建議因子（已過全部閘門）
  hitRate: number | null; // 主窗（15 交易日）命中率 %
  decided: number;        // 已到期信號數
  reason: string;         // 人話解釋（點解調/點解唔調）
}

const r3 = (n: number) => Math.round(n * 1000) / 1000;

/**
 * 命中率 → 目標因子映射（未過閘門嘅原始值）：
 * 50% 命中 = 中性 1.0；每 ±10pp 命中 = ±0.2 因子（線性，即 target = 2×hitRate 小數）。
 * 例：75% → 1.5（上限）；25% → 0.5（下限）。
 */
export function targetFactorFromHitRate(hitRatePct: number): number {
  return Math.min(FACTOR_MAX, Math.max(FACTOR_MIN, r3(2 * (hitRatePct / 100))));
}

/**
 * 過閘門嘅因子提案：樣本閘 → 步幅閘（±0.1/週）→ 夾限。
 * prev 係現行有效因子（靜態表或上一份學習結果），保證學習路徑平滑唔會單日跳變。
 */
export function proposeFactor(expertId: string, hitRatePct: number | null, decided: number, prev: number): FactorProposal {
  if (hitRatePct == null || decided < LEARN_MIN_SAMPLE) {
    return { expertId, prev, next: prev, hitRate: hitRatePct, decided,
      reason: decided === 0 ? "無已到期信號，維持現行因子" : `僅 ${decided} 個已到期信號（<${LEARN_MIN_SAMPLE}），樣本不足唔調` };
  }
  const target = targetFactorFromHitRate(hitRatePct);
  const stepCap = decided < LEARN_FULL_SAMPLE ? MAX_WEEKLY_STEP / 2 : MAX_WEEKLY_STEP;
  const delta = Math.max(-stepCap, Math.min(stepCap, target - prev));
  const next = r3(Math.min(FACTOR_MAX, Math.max(FACTOR_MIN, prev + delta)));
  const dirTxt = next > prev ? "上調" : next < prev ? "下調" : "維持";
  return { expertId, prev, next, hitRate: hitRatePct, decided,
    reason: `主窗命中率 ${hitRatePct}%（n=${decided}）→ 目標 ${target}；步幅限 ±${stepCap} → ${dirTxt}至 ${next}` };
}

// ---- 跑輸診斷：個別錯 vs 全錯 vs 大市問題 ----

export type UnderperfVerdict = "none" | "individual" | "systemic" | "market";

export interface UnderperfInput {
  excess20dPp: number | null;     // 組合 20 日相對 ACWI 超額（pp，負=跑輸）
  marketRSq: number | null;       // 組合日收益對 ACWI 日收益回歸嘅 R²（60 日窗）
  expertHitRates: { expertId: string; hitRate: number | null; decided: number }[];
  consensusHitRate: number | null; // 全體信號主窗命中率（%）
}

export const UNDERPERF_TRIGGER_PP = -3;  // 滾動 20 日跑輸 >3pp 先觸發診斷（避免噪音級波動誤報）
export const MARKET_RSQ_LINE = 0.8;      // R²>0.8 = 回撤幾乎全由市場解釋

/** 跑輸診斷分類器（純函數，全部口徑鎖死單測） */
export function classifyUnderperformance(inp: UnderperfInput): { verdict: UnderperfVerdict; detail: string } {
  const { excess20dPp, marketRSq, expertHitRates, consensusHitRate } = inp;
  if (excess20dPp == null || excess20dPp > UNDERPERF_TRIGGER_PP) {
    return { verdict: "none", detail: "未觸發診斷線（20 日超額 > -3pp）" };
  }
  // 大市主導：R² 高 = 組合回撤跟足大市，專家觀點唔係主因 → 唔郁專家權重，由 S3 狀態機收敞口
  if (marketRSq != null && marketRSq > MARKET_RSQ_LINE) {
    return { verdict: "market", detail: `跑輸 ${excess20dPp.toFixed(1)}pp，但市場因子解釋力 R²=${marketRSq.toFixed(2)}（>0.8）——係大環境回撤，唔係專家判斷錯；唔調專家因子` };
  }
  // 系統性：過半專家主窗命中率 <50% 且共識命中率都 <50% → 專家群體判斷失效（regime change）
  const valid = expertHitRates.filter(e => e.hitRate != null && e.decided >= LEARN_MIN_SAMPLE);
  const negShare = valid.length ? valid.filter(e => (e.hitRate ?? 0) < 50).length / valid.length : 0;
  if (valid.length >= 3 && negShare > 0.5 && consensusHitRate != null && consensusHitRate < 50) {
    return { verdict: "systemic", detail: `跑輸 ${excess20dPp.toFixed(1)}pp；${valid.filter(e => (e.hitRate ?? 0) < 50).length}/${valid.length} 位專家命中率 <50%、共識命中率 ${consensusHitRate}%——屬系統性失效（可能係市場風格切換），共識信號整體降權` };
  }
  // 個別：得少數專家拖累
  const worst = [...valid].sort((a, b) => (a.hitRate ?? 0) - (b.hitRate ?? 0))[0];
  return { verdict: "individual", detail: `跑輸 ${excess20dPp.toFixed(1)}pp；集中喺個別專家（最弱：${worst ? `${worst.expertId} ${worst.hitRate}%（n=${worst.decided}）` : "—"}）——逐位下調因子，唔好連坐` };
}

// ---- 統計小工具（R² 用）----
export function dailyReturns(closes: { date: string; close: number }[]): Map<string, number> {
  const m = new Map<string, number>();
  for (let i = 1; i < closes.length; i++) {
    if (closes[i - 1].close > 0) m.set(closes[i].date, closes[i].close / closes[i - 1].close - 1);
  }
  return m;
}

/** 兩條日收益序列（日期對齊交集）嘅決定系數 R²；共同日 <30 → null（誠實原則，同 screener.ts pearson 口徑） */
export function rSquared(a: Map<string, number>, b: Map<string, number>): number | null {
  const xs: number[] = [], ys: number[] = [];
  for (const [d, v] of a) { const w = b.get(d); if (w != null) { xs.push(v); ys.push(w); } }
  const n = xs.length;
  if (n < 30) return null;
  const mx = xs.reduce((s, x) => s + x, 0) / n, my = ys.reduce((s, y) => s + y, 0) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; syy += (ys[i] - my) ** 2; }
  if (sxx === 0 || syy === 0) return null;
  const r = sxy / Math.sqrt(sxx * syy);
  return r3(r * r);
}
