// 前后端共享类型：每日快照结构
export interface SnapshotSignal {
  asset: string
  direction: 'bull' | 'bear' | 'neutral'
  strength: number // 1-5
  note: string
}

export interface SnapshotView {
  expertId: string
  expertName: string
  date: string
  channel: string
  title: string
  summary: string
  url: string
  videoId?: string
  signals: SnapshotSignal[]
  decayWeight: number // 0-1，按 horizon 分級半衰期（macro 45 / theme 21 / event 7 天）
  horizon?: 'macro' | 'theme' | 'event' // Phase 13 P0-3：carry 時保留原視野計衰減（舊數據無此欄 → 默認 theme）
  carried?: boolean // Phase 13 P0-3：由上一快照併入嘅觀點標記（統計/顯示可區分本輪新增）
  signalCarried?: boolean // 2026-10-09：本輪重抓結構化失敗，信號沿用上一快照同 key 觀點（preserveCarriedSignals）
}

export interface SuggestedChange {
  ticker: string
  from: number
  to: number
  reason: string
}

export interface Snapshot {
  date: string
  generatedAt: string
  views: SnapshotView[]           // 本轮新增/更新的观点
  suggested: SuggestedChange[]    // 建议调仓（待人工复核，不自动生效）
  suggestedNote: string
  lastRebalanceDate: string       // 当前生效权重对应的调仓日
  acknowledged?: boolean          // 用户已复核（横幅提醒消失）
  acknowledgedAt?: string
  brakeStatus?: 'ok' | 'partial' | 'unavailable'  // 价格刹车层运行状态（unavailable 时前端须警告）
  watchlist?: WatchlistItem[]     // 新主題瞭望（2026-10-09）：組合未覆蓋嘅專家觀點 → 候選 ETF 篩選 → 試倉提案
}

// ---- 新主題瞭望（contracts/watchlist.ts 純函數聚合；候選 ETF 策展表唔准 LLM 發明）----
export interface WatchlistItem {
  theme: string
  direction: 'bull' | 'bear' | 'mixed'
  netScore: number
  supporters: string[]
  signalCount: number
  latestDate: string
  candidates: { ticker: string; tier: string; headline: string }[]  // 篩選器判語（avoid/substitute/diversifier/limited）
  proposal: string | null           // 試倉提案（bull + 淨分過閘 + 篩選通過先有）
}

export interface PipelineStatus {
  lastRunAt: string | null
  lastStatus: string | null
  lastLog: string | null
  snapshotDate: string | null
}

// ---- 实时行情 ----
export interface Quote {
  ticker: string
  price: number
  prevClose: number
  changePct: number   // 当日涨跌幅 %
  currency: string
  marketState?: string
  asOf: string
}

export interface QuotesResponse {
  asOf: string
  status: 'ok' | 'partial' | 'unavailable'
  quotes: Record<string, Quote>
  failed: string[]
}

// ---- 融合算法引擎（Calvin × 孫子兵法 × 專家信號管道），見 research/algo-spec.md §4 ----
export interface AlgoTickerReading { ticker: string; price: number; sma200: number|null; mom126: number|null; vol20: number|null; mdd1y: number|null; zscore: number|null; trendScore: number; expertScore: number; fusedScore: number; action: 'add'|'reduce'|'hold'|'trim'; targetDeltaPp: number; gates: { rule: string; passed: boolean; note: string }[] }
export interface AlgoRuleState { id: string; name: string; origin: 'calvin'|'suntzu'|'quant'; level: 'A'|'B'|'C'; confidence: '證實'|'推斷'|'缺口'; quote: string; source: string; reading: string; lamp: 'pass'|'warn'|'fail'|'na' }
export interface AlgoAnalysis { asOf: string; status: 'ok'|'partial'|'unavailable'; regime: 'normal'|'highVol'; equityGateOn: boolean; portfolioDD: number|null; tickers: AlgoTickerReading[]; rules: AlgoRuleState[]; summary: string }

// ---- 持倉相關性 / 重複曝光分析（api/correlation.ts，2026-09-07 Phase 7）----
export interface CorrPair { a: string; b: string; corr: number } // 皮爾遜 ρ（近1年日收益，共同交易日對齊）
export interface CorrGroup { name: string; members: string[]; note: string; weight: number; intraCorr: number|null; over: boolean } // over=權重合計>30pp（S9 口徑）
export interface CorrelationReport { asOf: string; asOfDate: string|null; status: 'ok'|'partial'|'unavailable'; days: number; pairs: CorrPair[]; groups: CorrGroup[]; failed: string[]; summary: string }
