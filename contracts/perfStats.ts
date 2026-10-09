// ---- 組合表現統計：單一口徑計算器（前端 × 管道共用，2026-09-07 Phase 8）----
// 背景：管道每日追加淨值時舊版只更新 portRet/benchRet，netRet/maxDD/vol/Sharpe
// 永遠凍結喺 2026-07-23——造成「頂部 +12.3% vs 總覽 +7.97%」嘅結構性分裂。
// 由呢度開始：任何展示統計必須由淨值序列即時重算，唔准再用凍結值。
//
// 方法學（已用 2026-01-20→07-23 數據反向驗證，100% 重現 REAL_STATS）：
//   portRet  = 最後淨值 − 100
//   netRet   = portRet − costDrag（交易成本拖累 = 單邊10bps × 總換手）
//   maxDD    = min( 淨值 / 歷史峰值 − 1 )
//   vol      = 日收益樣本標準差 × √252
//   annRet   = 日曆日 CAGR：(末/初)^(365/日數) − 1
//   sharpe   = (annRet − rf) / vol，rf = 4%（美元無風險利率假設）

export interface PerfStatsInput {
  dates: string[]        // MM-DD 展示格式（跨年：由 startDate 年份推斷）
  portfolio: number[]    // 組合淨值序列（起點 = 100）
  benchmark: number[]    // 基準淨值序列（起點 = 100）
  startDate?: string     // 完整日期 YYYY-MM-DD，預設 '2026-01-20'
  rf?: number            // 無風險利率 %，預設 4
  turnover?: number      // 總換手 %，預設 125
  costDrag?: number      // 成本拖累 pp，預設 0.12
}

export interface PerfStats {
  portRet: number; netRet: number; benchRet: number
  maxDD: number; benchMaxDD: number
  annRet: number; benchAnnRet: number
  vol: number; benchVol: number
  sharpe: number; benchSharpe: number
  turnover: number; costDrag: number; days: number
}

const r2 = (x: number) => +x.toFixed(2)
const r1 = (x: number) => +x.toFixed(1)

function maxDrawdown(xs: number[]): number {
  let peak = xs[0], m = 0
  for (const x of xs) { if (x > peak) peak = x; const dd = x / peak - 1; if (dd < m) m = dd }
  return m * 100
}

function dailyReturns(xs: number[]): number[] {
  const out: number[] = []
  for (let i = 1; i < xs.length; i++) out.push(xs[i] / xs[i - 1] - 1)
  return out
}

function sampleStd(xs: number[]): number {
  const n = xs.length
  if (n < 2) return 0
  const mean = xs.reduce((a, b) => a + b, 0) / n
  const v = xs.reduce((a, b) => a + (b - mean) * (b - mean), 0) / (n - 1)
  return Math.sqrt(v)
}

// MM-DD → 完整日期的年份推斷（同 api/pipeline.ts 跨年邏輯一致）：MM-DD >= 起點 → 起始年，否則 +1
function fullDate(mmdd: string, startYear: number, startMmdd: string): Date {
  const y = mmdd >= startMmdd ? startYear : startYear + 1
  return new Date(Date.UTC(y, Number(mmdd.slice(0, 2)) - 1, Number(mmdd.slice(3, 5))))
}

export function computePerfStats(inp: PerfStatsInput): PerfStats {
  const { dates, portfolio, benchmark } = inp
  const startDate = inp.startDate ?? '2026-01-20'
  const rf = inp.rf ?? 4
  const turnover = inp.turnover ?? 125
  const costDrag = inp.costDrag ?? 0.12
  const startY = Number(startDate.slice(0, 4))
  const startMmdd = startDate.slice(5, 10)
  const t0 = new Date(Date.UTC(startY, Number(startMmdd.slice(0, 2)) - 1, Number(startMmdd.slice(3, 5)))).getTime()
  const t1 = fullDate(dates[dates.length - 1], startY, startMmdd).getTime()
  const days = Math.max(1, Math.round((t1 - t0) / 86400000))

  const leg = (xs: number[]) => {
    const ret = r2(xs[xs.length - 1] - 100)
    const mdd = r2(maxDrawdown(xs))
    const vol = r1(sampleStd(dailyReturns(xs)) * Math.sqrt(252) * 100)
    const ann = r1((Math.pow(xs[xs.length - 1] / xs[0], 365 / days) - 1) * 100)
    const sharpe = vol > 0 ? r2((ann - rf) / vol) : 0
    return { ret, mdd, vol, ann, sharpe }
  }
  const p = leg(portfolio), b = leg(benchmark)
  return {
    portRet: p.ret, netRet: r2(p.ret - costDrag), benchRet: b.ret,
    maxDD: p.mdd, benchMaxDD: b.mdd,
    annRet: p.ann, benchAnnRet: b.ann,
    vol: p.vol, benchVol: b.vol,
    sharpe: p.sharpe, benchSharpe: b.sharpe,
    turnover, costDrag, days,
  }
}
