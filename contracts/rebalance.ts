// 調倉閉環純函數層（前後端共用、可單測）——Phase 15
// 數據流：用戶喺券商真實執行調倉 → 網站「記錄調倉」→ runtime 記錄落 public/data/rebalances.json
// → 生效權重 = 靜態基準（2026-07-20 調倉#3）+ runtime 記錄按日期順序 replay
// → 淨值追蹤按 weightsTimeline 分段計算（調倉日收市執行，下一交易日起用新權重）
// → 圖表黃點由記錄自動衍生（唔再靠人手同步第二份寫死嘅 marks 數組——呢個就係「chart 冇同步」嘅根因）

// 靜態基準權重（2026-07-20 調倉#3）——由 api/pipeline.ts 移入呢個葉子模組，
// 斬斷 pipeline ↔ screener 循環依賴（screener 攞持倉清單唔再要 import pipeline）。
export const CURRENT_WEIGHTS: Record<string, number> = {
  VOO: 12, SMH: 10, ASHR: 8, MCHI: 5, EWH: 6, GLD: 9, SLV: 3, COPX: 3,
  XLE: 6, XLB: 4, IFRA: 5, EWY: 4, EWT: 5, XLV: 4, VGK: 3, IBIT: 2,
  TLT: 3, BND: 4, SGOV: 4,
};
export const LAST_REBALANCE_DATE = "2026-07-20";

export interface RebalanceChange { etf: string; from: number; to: number }

export interface RuntimeRebalance {
  date: string                      // YYYY-MM-DD（執行日；新權重由下一交易日起生效）
  title: string                     // 例：「调仓 #4」
  trigger: string                   // 觸發原因（可空字串）
  changes: RebalanceChange[]
  note: string
  recordedAt: string                // ISO 時間戳（記錄動作發生時間，審計用）
}

// 生效權重 replay：base（靜態基準）依次套用每條記錄嘅 to 值；同 ticker 後記錄冚前記錄
export function applyRebalances(base: Record<string, number>, records: RuntimeRebalance[]): Record<string, number> {
  const w = { ...base };
  const sorted = [...records].sort((a, b) => a.date === b.date ? a.recordedAt.localeCompare(b.recordedAt) : a.date.localeCompare(b.date));
  for (const r of sorted) for (const c of r.changes) w[c.etf] = c.to;
  return w;
}

export interface WeightsTimelineEntry { from: string; w: Record<string, number> }

// 淨值追蹤分段權重：entry.from = 調倉執行日，該日仍以舊權重計（收市執行），新權重對「嚴格晚於 from」嘅日期生效。
// 基準 entry from=2026-07-20 → 07-21 起用基準權重，與原有凍結口徑一致。
export function weightsForDate(timeline: WeightsTimelineEntry[], ymd: string): Record<string, number> {
  let cur = timeline[0]?.w ?? {};
  for (const e of timeline) {
    if (e.from < ymd) cur = e.w; else break;
  }
  return cur;
}

export interface RebalanceInput {
  date: string;
  changes: { etf: string; to: number }[];
}

// 校驗一條新記錄（喺現行生效權重基礎上）：回傳 error 字串或 null（通過）。
// 純函數，唔掂日期「今日」以外嘅副作用；now 由調用方注入方便測試。
export function validateRebalance(
  effective: Record<string, number>,
  allowedTickers: readonly string[],
  existing: RuntimeRebalance[],
  input: RebalanceInput,
  now: Date,
): string | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.date)) return "日期格式必須係 YYYY-MM-DD";
  // 嚴格日子校驗：JS Date 會將 02-31 之類「進位」成正規日期，必須 round-trip 對返先算有效
  const [yy, mm, dd] = input.date.split("-").map(Number);
  const dt = new Date(Date.UTC(yy, mm - 1, dd));
  if (dt.getUTCFullYear() !== yy || dt.getUTCMonth() !== mm - 1 || dt.getUTCDate() !== dd) return "日期唔係有效日子";
  // 「今日」以香港時間計（用戶 HKT；券商執行日都係按本地日記）
  const today = new Date(now.getTime() + 8 * 3600_000).toISOString().slice(0, 10);
  if (input.date > today) return `調倉日期 ${input.date} 喺未來——只可以記錄已執行嘅真實調倉`;
  if (existing.some(r => r.date === input.date)) return `${input.date} 已有調倉記錄——同一日唔可以記兩次（如記錯請聯絡管理員修正）`;
  if (!input.changes.length) return "至少要有一項權重變動";
  const seen = new Set<string>();
  const next = { ...effective };
  for (const c of input.changes) {
    if (!allowedTickers.includes(c.etf)) return `未知 ETF：${c.etf}（只接受現行 19 隻持倉工具）`;
    if (seen.has(c.etf)) return `${c.etf} 重複出現`;
    seen.add(c.etf);
    if (!Number.isFinite(c.to) || c.to < 0 || c.to > 40) return `${c.etf} 目標權重 ${c.to} 超出合理範圍（0-40%）`;
    if (c.to === effective[c.etf]) return `${c.etf} 目標權重同現行一樣（${c.to}%），冇變動唔使記錄`;
    next[c.etf] = c.to;
  }
  const sum = Object.values(next).reduce((s, v) => s + v, 0);
  if (Math.abs(sum - 100) > 1e-9) return `調整後總權重 = ${sum.toFixed(2)}%，必須等於 100%（加倉嘅 pp 要由邊度嚟講清楚）`;
  return null;
}

// 由記錄生成圖表標記（week = MM-DD，對齊淨值圖 x 軸；label 統一「调仓#N」格式）
export function rebalanceMark(r: RuntimeRebalance): { week: string; label: string } {
  const m = r.title.match(/#\s*(\d+)/);
  return { week: r.date.slice(5, 10), label: m ? `调仓#${m[1]}` : (r.title || "调仓").slice(0, 8) };
}

// Phase 18：黃點落位——記錄日唔一定有淨值點（周末/美股休市/當日未收市），舊版 find 唔到就靜默丟咗個點
// （「批核咗但 chart 冇標記」嘅其中一個成因）。落位規則：① exact 命中；② 否則最近嘅不晚於日
// （休市日批核 → 標喺上一交易日收市點，語義 =「呢個收市之後生效」）；③ 再否則最早嘅晚於日。
// weeks 必須係升序 MM-DD 數組（同一年度內字典序=時序；跨年邊界喺淨值序列層已處理，呢度從簡）。
export function resolveMarkWeek(week: string, weeks: string[]): string | null {
  if (!weeks.length) return null;
  if (weeks.includes(week)) return week;
  const le = weeks.filter(w => w <= week);
  if (le.length) return le[le.length - 1];
  return weeks.find(w => w >= week) ?? null;
}

// 調倉記錄標題自動編號：靜態歷史有 3 次調倉（#1-#3），runtime 由 #4 起
export function nextRebalanceTitle(staticCount: number, runtimeCount: number): string {
  return `调仓 #${staticCount + runtimeCount + 1}`;
}
