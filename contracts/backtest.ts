// ---- 信號命中率回測：純函數層（前後端共用，2026-09-11 Phase 12）----
// 背景：舊版 signalBacktest 只有單一 15 交易日窗 + 絕對方向判定，有三個方法論缺陷——
//   ① 視野錯配：event/theme/macro 信號壽命唔同（半衰期 7/21/45 日），15 日窗對 macro 信號係噪音級
//   ② 順風車偏差：上升市中睇多信號乜都唔使啱都命中（觀點庫 bull:bear ≈ 38:17）——冇基準調整嘅命中率
//      會系統性高估看多專家
//   ③ 單窗太脆弱：窗口一加長，未夠日子嘅信號全部「待驗證」，張卡變空白
// 由呢度開始：多窗口階梯（5/15/45/90 交易日）+ ACWI 同窗超額命中 + 未到期誠實標記。
//
// 口徑定義（全部百分比單位，2dp；正數 = 升）：
//   retPct    = ETF 由信號日收盤 → 信號日後第 w 個交易日收盤嘅收益 %
//   excessPct = retPct − ACWI 同期收益 %（剔除大市順風，先係專家淨實力）
//   hit       = bull: excess > +0.5pp ｜ bear: excess < −0.5pp ｜ neutral: |excess| ≤ 2pp
//   cell = null 表示該窗口「未到期」（前瞻數據唔夠），誠實留空——唔當命中亦唔當證偽
//
// 聚合口徑：
//   hitRate      = hits / decided（decided = 該窗已到期信號數）
//   avgExcessDir = 方向性信號（bull/bear）嘅簽名超額均值：bull 取 +excess、bear 取 −excess
//                  （neutral 唔計入——佢嘅「期望值」概念上係 band−|excess|，混入會扭曲解讀）
//   insufficient = decided < 10（整體窗）/ < 3（按專家）——樣本太細時命中率僅供參考

export const BT_WINDOWS = [5, 15, 45, 90] as const
export const BT_PRIMARY_WINDOW = 15 // byExpert 聚合用嘅主窗（樣本最多、同舊版口徑最接近）
export const BT_DIR_EDGE_PP = 0.5 // 方向信號超額門檻（pp）
export const BT_NEUTRAL_BAND_PP = 2 // 中性信號超額上限（pp）

export interface BtPricePoint { date: string; close: number }
export interface BtCell { retPct: number; excessPct: number; hit: boolean }
export type BtCells = Record<number, BtCell | null> // key = 窗口交易日數；null = 未到期

export interface BtWindowAgg {
  window: number
  decided: number        // 已到期信號數
  pending: number        // 未到期信號數
  hits: number
  hitRate: number | null // %；decided=0 → null
  avgRetPct: number | null
  avgExcessDirPct: number | null // 方向性信號嘅簽名超額均值（pp）
  insufficient: boolean
}

const r2 = (n: number) => Math.round(n * 100) / 100

/** 方向命中判定（超額口徑） */
export function scoreHit(excessPct: number, direction: string): boolean {
  if (direction === 'bull') return excessPct > BT_DIR_EDGE_PP
  if (direction === 'bear') return excessPct < -BT_DIR_EDGE_PP
  return Math.abs(excessPct) <= BT_NEUTRAL_BAND_PP
}

/** 由日期對齊攞区间收益 %：from/to 用目標序列嘅實際交易日（>= 該日期嘅首個收盤） */
export function windowRetPct(closes: BtPricePoint[], fromDate: string, toDate: string): number | null {
  const a = closes.find(x => x.date >= fromDate)
  const b = closes.find(x => x.date >= toDate)
  if (!a || !b || b.date <= a.date) return null
  return r2((b.close / a.close - 1) * 100)
}

/**
 * 對一條信號逐窗口評分。entryDate = 信號發布日（YYYY-MM-DD）；
 * 入場 = 首個 date >= entryDate 嘅收盤（發布日非交易日則順延）；出場 = 入場後第 w 個交易日。
 * ACWI 用同一對入場/出場日期對齊（美股 ETF 同一交易日曆；個別缺失日以後順延）。
 */
export function evalWindows(closes: BtPricePoint[], acwi: BtPricePoint[], entryDate: string, direction: string): BtCells {
  const out: BtCells = {}
  for (const w of BT_WINDOWS) out[w] = null
  const ei = closes.findIndex(x => x.date >= entryDate)
  if (ei < 0) return out
  const entry = closes[ei]
  for (const w of BT_WINDOWS) {
    const exit = closes[ei + w]
    if (!exit) continue // 未到期：留 null
    const acwiRet = windowRetPct(acwi, entry.date, exit.date)
    if (acwiRet == null) continue // 基準缺數據：該窗誠實留空
    const retPct = r2((exit.close / entry.close - 1) * 100)
    const excessPct = r2(retPct - acwiRet)
    out[w] = { retPct, excessPct, hit: scoreHit(excessPct, direction) }
  }
  return out
}

/** 聚合一個窗口嘅整體統計（cellsList = 全部信號嘅 cells + direction） */
export function aggregateWindow(items: { direction: string; cells: BtCells }[], w: number): BtWindowAgg {
  const mature = items
    .map(x => ({ direction: x.direction, cell: x.cells[w] }))
    .filter((x): x is { direction: string; cell: BtCell } => x.cell != null)
  const decided = mature.length
  const pending = items.length - decided
  const hits = mature.filter(x => x.cell.hit).length
  const dir = mature.filter(x => x.direction !== 'neutral')
  const signedExcess = dir.map(x => (x.direction === 'bear' ? -x.cell.excessPct : x.cell.excessPct))
  return {
    window: w,
    decided,
    pending,
    hits,
    hitRate: decided > 0 ? r2((hits / decided) * 100) : null,
    avgRetPct: decided > 0 ? r2(mature.reduce((s, x) => s + x.cell.retPct, 0) / decided) : null,
    avgExcessDirPct: signedExcess.length > 0 ? r2(signedExcess.reduce((s, v) => s + v, 0) / signedExcess.length) : null,
    insufficient: decided < 10,
  }
}

/** 按專家聚合（主窗 BT_PRIMARY_WINDOW） */
export function aggregateExpert(items: { expert: string; direction: string; cells: BtCells }[], w: number = BT_PRIMARY_WINDOW) {
  const byExp = new Map<string, { direction: string; cell: BtCell }[]>()
  for (const x of items) {
    const cell = x.cells[w]
    if (!cell) continue
    const arr = byExp.get(x.expert) ?? []
    arr.push({ direction: x.direction, cell })
    byExp.set(x.expert, arr)
  }
  return [...byExp.entries()].map(([expert, list]) => {
    const decided = list.length
    const hits = list.filter(x => x.cell.hit).length
    const dir = list.filter(x => x.direction !== 'neutral')
    const signed = dir.map(x => (x.direction === 'bear' ? -x.cell.excessPct : x.cell.excessPct))
    return {
      expert,
      decided,
      hits,
      hitRate: decided > 0 ? r2((hits / decided) * 100) : null,
      avgExcessDirPct: signed.length > 0 ? r2(signed.reduce((s, v) => s + v, 0) / signed.length) : null,
      insufficient: decided < 3,
    }
  }).sort((a, b) => b.decided - a.decided)
}
