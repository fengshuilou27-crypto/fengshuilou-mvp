import { useMemo } from 'react'
import { trpc } from '../providers/trpc'
import { WEEKS, PORTFOLIO, BENCHMARK, REAL_STATS, ETF_PORTFOLIO, REBALANCES, type EtfHolding } from '../data/portfolio'
import { computePerfStats, type PerfStats } from '@contracts/perfStats'

// 实时数据层：數據源以 DB（tRPC pipeline.*）為準，BUNDLED 打包靜態快照係離線/build-time 兜底。
// 統計口徑（Phase 8）：stats 永遠由淨值序列即時重算，唔信文件入面嘅 stats 欄位——
// 舊版管道只更新 portRet/benchRet，netRet 等凍結喺 07-23，造成全站數字分裂。
export interface PerfData {
  asOf: string; source: string; frozenSince: string
  dates: string[]; portfolio: number[]; benchmark: number[]
  stats: PerfStats
  weightsTimeline?: WeightsTimelineEntry[] // 淨值分段權重（有就透傳，唔影響舊用法）
}

const BUNDLED: PerfData = {
  asOf: '2026-07-23', source: REAL_STATS.source, frozenSince: '2026-07-20',
  dates: WEEKS, portfolio: PORTFOLIO, benchmark: BENCHMARK,
  stats: computePerfStats({ dates: WEEKS, portfolio: PORTFOLIO, benchmark: BENCHMARK }),
}

// Phase 13+：react-query 嘅 refetchOnWindowFocus 已覆蓋「返回分頁即重拉」，唔再手動掛 listener
const FRESH = { refetchOnWindowFocus: true, staleTime: 30_000, retry: 1 } as const

export function usePerformance(): PerfData {
  const q = trpc.pipeline.performance.useQuery(undefined, FRESH)
  return useMemo(() => {
    const j: any = q.data
    // 嚴格校驗：三數組等長且淨值全為數字才採用，防止半截數據 / 錯誤格式污染圖表；唔過回 BUNDLED
    const ok = Array.isArray(j?.dates) && j.dates.length > 0
      && j.dates.length === j.portfolio?.length && j.dates.length === j.benchmark?.length
      && j.portfolio.every((v: unknown) => typeof v === 'number' && isFinite(v))
      && j.benchmark.every((v: unknown) => typeof v === 'number' && isFinite(v))
    if (!ok) return BUNDLED
    // 序列先係真相：stats 即場重算（turnover/costDrag 沿用源數據值，缺咗用預設）；weightsTimeline 等額外欄位透傳
    return {
      ...j,
      stats: computePerfStats({
        dates: j.dates, portfolio: j.portfolio, benchmark: j.benchmark,
        turnover: j.stats?.turnover, costDrag: j.stats?.costDrag,
      }),
    }
  }, [q.data])
}

import type { Snapshot } from '@contracts/types'
export type FileSnapshot = Snapshot

export function useFileSnapshot(): FileSnapshot | null {
  const q = trpc.pipeline.snapshot.useQuery(undefined, FRESH)
  const j: any = q.data
  const ok = j?.date && Array.isArray(j.views) && Array.isArray(j.suggested)
    && typeof j.generatedAt === 'string'
  return ok ? j : null
}

// ---- 实时行情（tRPC → Yahoo，60 秒轮询；后端不可用时静默回退 null） ----
import type { QuotesResponse } from '@contracts/types'

export function useQuotes(): { data: QuotesResponse | null; backendDown: boolean } {
  const q = trpc.quotes.live.useQuery(undefined, {
    refetchInterval: 60_000,
    retry: 1,
    staleTime: 30_000,
    refetchOnWindowFocus: true, // Phase 13：返回分頁即刷新行情
  })
  return { data: q.data ?? null, backendDown: q.isError }
}

// ---- 融合算法引擎（tRPC → api/algo.ts，30 分钟 staleTime；后端不可用时静默回退 null） ----
import type { AlgoAnalysis } from '@contracts/types'

export function useAlgo(): { data: AlgoAnalysis | null; backendDown: boolean } {
  const q = trpc.algo.analyze.useQuery(undefined, {
    staleTime: 30 * 60_000,
    retry: 1,
    refetchOnWindowFocus: true, // Phase 13：返回分頁即刷新引擎讀數
  })
  return { data: q.data ?? null, backendDown: q.isError }
}

// ---- Phase 15：runtime 調倉記錄（tRPC pipeline.rebalances，DB 優先；用戶記低真實執行嘅調倉） ----
import { applyRebalances, type RuntimeRebalance, type WeightsTimelineEntry } from '@contracts/rebalance'

export function useRebalances(): { records: RuntimeRebalance[]; reload: () => void } {
  const q = trpc.pipeline.rebalances.useQuery(undefined, FRESH)
  // tRPC 回 bare array；逐條格式校驗，壞記錄直接丟
  const records = useMemo(
    () => (Array.isArray(q.data) ? q.data : [])
      .filter((r: any) => typeof r?.date === 'string' && Array.isArray(r?.changes)),
    [q.data],
  )
  return { records, reload: q.refetch }
}

// 生效持倉：靜態基準（ETF_PORTFOLIO = 2026-07-20 調倉#3）+ runtime 記錄按日期 replay。
// delta 顯示「最新一次記錄」嘅變動；冇 runtime 記錄時沿用靜態 delta（即 #3 嘅變動）。
const STATIC_LAST_REBALANCE = REBALANCES[REBALANCES.length - 1]?.date ?? '2026-07-20'
export function useEffectivePortfolio(): { holdings: EtfHolding[]; records: RuntimeRebalance[]; reload: () => void; lastRebalanceDate: string } {
  const { records, reload } = useRebalances()
  const sorted = useMemo(
    () => [...records].sort((a, b) => a.date.localeCompare(b.date) || a.recordedAt.localeCompare(b.recordedAt)),
    [records],
  )
  const holdings = useMemo(() => {
    if (!sorted.length) return ETF_PORTFOLIO
    const base = Object.fromEntries(ETF_PORTFOLIO.map(h => [h.ticker, h.weight]))
    const eff = applyRebalances(base, sorted)
    const chg = new Map(sorted[sorted.length - 1].changes.map(c => [c.etf, c.to - c.from]))
    return ETF_PORTFOLIO.map(h => ({
      ...h,
      weight: eff[h.ticker] ?? h.weight,
      delta: chg.has(h.ticker) ? (chg.get(h.ticker) as number) : 0,
    }))
  }, [sorted])
  const lastRebalanceDate = sorted.length ? sorted[sorted.length - 1].date : STATIC_LAST_REBALANCE
  return { holdings, records: sorted, reload, lastRebalanceDate }
}

// 组合今日实时估算：Σ(权重 × 当日涨跌) —— 基于生效权重，非精确 NAV
export function liveDayChange(
  quotes: Record<string, { changePct: number }>,
  weights: ReadonlyArray<{ ticker: string; weight: number }>,
): { pct: number; covered: number } {
  let sum = 0, covered = 0
  for (const w of weights) {
    const q = quotes[w.ticker]
    if (q) { sum += w.weight * q.changePct; covered += w.weight }
  }
  return { pct: covered > 0 ? sum / 100 : 0, covered }
}
