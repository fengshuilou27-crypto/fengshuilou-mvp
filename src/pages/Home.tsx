import { useState, useEffect, useMemo, useRef } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceDot, PieChart, Pie, Cell, Legend,
} from 'recharts'
import { REBALANCES, REBALANCE_MARKS, EXPERT_NAMES } from '../data/portfolio'
import { EXPERTS, REVIEWS, FIT_CHECKS } from '../data/experts'
import { trpc } from '@/providers/trpc'
import { usePerformance, useFileSnapshot, useQuotes, useAlgo, useEffectivePortfolio, liveDayChange } from '../hooks/useLiveData'
import { rebalanceMark, resolveMarkWeek } from '@contracts/rebalance'
import { computeConsensus, THEME_ACTIONS, type LiveSignalView } from '../lib/consensus'
import { ALGO_RULES_META } from '@contracts/algoRules'
import type { AlgoRuleState } from '@contracts/types'

const SNAPSHOT = '2026-07-24'
const HALF_LIFE = 21
const EXPERT_COLS = ['hong', 'choi', 'timmer', 'tam', 'lam', 'lamy', 'chong', 'hui']
const STALE_DAYS = Math.floor((Date.now() - new Date(SNAPSHOT).getTime()) / 86400000)

// 衰减对「今天」计算（旧版按固定快照日冻结，会导致过期信号看起来仍然新鲜）
function decay(dateStr: string) {
  const days = Math.max(0, (Date.now() - new Date(dateStr).getTime()) / 86400000)
  if (days > 90) return 0
  return Math.pow(0.5, days / HALF_LIFE)
}
const pct = (n: number, d = 1) => `${n >= 0 ? '+' : ''}${n.toFixed(d)}%`

// 來源鏈接正規化：youtu.be 短鏈 / shorts 鏈統一顯示為 canonical watch?v=ID；抓唔到 videoId 就原樣返回
function canonicalYtUrl(u: string): string {
  const m = u.match(/(?:youtube\.com\/(?:watch\?.*v=|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/)
  return m ? `https://www.youtube.com/watch?v=${m[1]}` : u
}

// 錯誤訊息美化：iPhone Safari 等平台代理逾時回非 JSON，fetch 層只會拋通用 parse/網絡錯——翻譯做人話
function friendlyNetworkError(msg: string): string {
  if (/did not match the expected pattern|Unexpected token|Failed to fetch|Load failed/i.test(msg))
    return '網絡或伺服器回應異常（多數係逾時）——內容已保留喺下面，請 30 秒後再撳一次'
  return msg
}

// 合併管道即時觀點的共識引擎入口：tRPC 優先，無後端時回退隨站快照文件。
// 修復 2026-09-06 發現的假「即時計算」——舊版只讀靜態檔案，新鮮觀點從不進矩陣。
function useMergedConsensus() {
  const snapQ = trpc.pipeline.snapshot.useQuery(undefined, { retry: false, refetchInterval: 5 * 60000 })
  const fileSnap = useFileSnapshot()
  const liveSnap = snapQ.data ?? (snapQ.isError ? fileSnap : null)
  return useMemo(() => {
    const live: LiveSignalView[] = (liveSnap?.views ?? []).map(v => ({
      expertName: v.expertName,
      date: v.date,
      signals: v.signals.map(s => ({ asset: s.asset, direction: s.direction, strength: s.strength })),
      // Phase 13：後端正加緊 decayWeight 欄——有就透傳畀共識引擎直接用，冇就由引擎 fallback 自行折算
      decayWeight: (v as { decayWeight?: number }).decayWeight,
    }))
    return { rows: computeConsensus(new Date(), live), liveCount: live.length, snapDate: liveSnap?.date ?? null }
  }, [liveSnap])
}

const SECTIONS = ['总览', '组合配置', '信号共识矩阵', '量化算法', '每日更新', '调仓记录', '专家观点库', '复盘验证', '方法论']
const PIE_COLORS = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f472b6', '#a78bfa', '#22d3ee', '#fb923c', '#94a3b8', '#4ade80', '#e879f9', '#facc15', '#64748b', '#f87171', '#2dd4bf', '#c084fc', '#fcd34d', '#7dd3fc', '#bef264']

export default function Home() {
  const [tab, setTab] = useState('总览')
  const perf = usePerformance()
  // 全站调仓提醒：tRPC 优先，失败时回退 /data/snapshot.json（无后端静态部署时横幅依然有效）
  const snapQuery = trpc.pipeline.snapshot.useQuery(undefined, { retry: false, refetchInterval: 5 * 60000 })
  const fileSnap = useFileSnapshot()
  const liveSnap = snapQuery.data ?? (snapQuery.isError ? fileSnap : null)
  const pending = liveSnap && !liveSnap.acknowledged && liveSnap.suggested.length > 0 ? liveSnap : null

  return (
    <div className="min-h-screen bg-[#0a0f1c] text-slate-200">
      <header className="border-b border-slate-800 bg-[#0d1424]/90 sticky top-0 z-20 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3 justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">专家观点 ETF 组合追踪</h1>
            <p className="text-xs text-slate-400">8位专家 · 全网视频/专栏观点 · 时间衰减引擎 · 信号共识驱动</p>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2 py-1 rounded bg-sky-500/15 text-sky-300 border border-sky-500/30" title={liveSnap ? `管道最新快照 ${liveSnap.date} · 觀點 ${liveSnap.views.length} 條 · 生成於 ${new Date(liveSnap.generatedAt).toLocaleString('zh-HK')}` : '靜態檔案基準日（後端未連接）'}>快照 {liveSnap?.date ?? SNAPSHOT}{liveSnap ? ` · ${liveSnap.views.length}觀點` : ''}</span>
            <span className="px-2 py-1 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" title={`與總覽「回報」同一個數：淨值序列即時重算嘅含成本淨回報（${perf.asOf} 更新）`}>真实行情回测 {pct(perf.stats.netRet ?? perf.stats.portRet)}</span>
          </div>
        </div>
        {/* Phase 13：補齊 ARIA tablist 語義 */}
        <nav role="tablist" aria-label="頁面分區" className="max-w-7xl mx-auto px-4 flex gap-1 overflow-x-auto pb-2">
          {SECTIONS.map(s => (
            <button key={s} role="tab" aria-selected={tab === s} aria-controls={`panel-${s}`} id={`tab-${s}`}
              onClick={() => setTab(s)}
              className={`px-3 py-1.5 rounded-md text-sm whitespace-nowrap transition ${tab === s ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40' : 'text-slate-400 hover:text-slate-200'}`}>
              {s}
            </button>
          ))}
        </nav>
      </header>

      {STALE_DAYS > 3 && (
        <div className="bg-sky-500/10 border-b border-sky-500/30">
          <div className="max-w-7xl mx-auto px-4 py-2 text-xs text-sky-300">
            ℹ 「专家观点库」下方的旧版静态档案基准日为 {SNAPSHOT}（{STALE_DAYS} 天前），仅作历史对照；新鲜观点以各卡顶部绿框的「管道即時觀點」及「每日更新」页为准。
          </div>
        </div>
      )}
      {pending && (
        <div className="bg-amber-500/15 border-b border-amber-500/40">
          <div className="max-w-7xl mx-auto px-4 py-2.5 flex flex-wrap items-center gap-3">
            <span className="text-amber-300 text-sm font-medium">⚠ {pending.date} 快照有 {pending.suggested.length} 项待复核调仓建议</span>
            <span className="text-xs text-amber-200/70">{pending.suggested.slice(0, 3).map(c => `${c.ticker} ${c.from}%→${c.to}%`).join(' · ')}{pending.suggested.length > 3 ? ' …' : ''}</span>
            <button onClick={() => {
                setTab('每日更新')
                // 等 React 渲染完「每日更新」頁先滾動；已喺該頁時 setTab 係 no-op，呢個滾動先係實際回應
                setTimeout(() => document.getElementById('pending-review')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
              }} className="ml-auto text-xs px-3 py-1 rounded bg-amber-500/25 text-amber-200 border border-amber-500/50 hover:bg-amber-500/35 active:bg-amber-500/45">
              立即复核 →
            </button>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`} className="space-y-6">
        {tab === '总览' && <Overview />}
        {tab === '组合配置' && <Allocation />}
        {tab === '信号共识矩阵' && <Consensus />}
        {tab === '量化算法' && <AlgoEngine />}
        {tab === '每日更新' && <DailyUpdate />}
        {tab === '调仓记录' && <RebalanceLog />}
        {tab === '专家观点库' && <Experts />}
        {tab === '复盘验证' && <Review />}
        {tab === '方法论' && <Methodology />}
        </div>
        <Disclaimer />
      </main>
    </div>
  )
}

function Card({ title, children, sub, id }: { title: string; children: React.ReactNode; sub?: string; id?: string }) {
  return (
    <section id={id} className="rounded-xl border border-slate-800 bg-[#0f1729] p-5 scroll-mt-32">
      <h2 className="text-base font-semibold text-white mb-1">{title}</h2>
      {sub && <p className="text-xs text-slate-400 mb-3">{sub}</p>}
      {children}
    </section>
  )
}

// 今日实时条：打开页面即拉取整个组合的最新价，估算组合当日涨跌；后端不可用时优雅隐藏
function LiveStrip() {
  const { data, backendDown } = useQuotes()
  // Hook 必須在任何 early return 之前調用（React Hooks 規則）——此前在條件返回後調用
  // usePerformance 導致數據到達時 hook 數量變化，整個頁面崩潰白屏
  const perf = usePerformance()
  const { holdings } = useEffectivePortfolio()
  if (backendDown) return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-500">
      实时行情：后端未连接（静态预览模式）——部署后此处显示整个 ETF 组合的实时价格与当日估算涨跌，60 秒自动刷新。
    </div>
  )
  if (!data) return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-400 animate-pulse">
      实时行情加载中…
    </div>
  )
  if (data.status === 'unavailable') return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-500">
      实时行情：行情源暂时不可用（已显式标记，下一分钟自动重试）——下方仍展示最新收盘净值数据。
    </div>
  )
  const day = liveDayChange(data.quotes, holdings)
  const acwi = data.quotes['ACWI'], agg = data.quotes['AGG']
  const benchDay = acwi && agg ? (acwi.changePct * 0.6 + agg.changePct * 0.4) : null
  const lastNav = perf.portfolio[perf.portfolio.length - 1] ?? 100
  const est = isFinite(day.pct) ? lastNav * (1 + day.pct / 100) : null
  return (
    <div className={`rounded-xl border px-4 py-3 ${data.status === 'partial' ? 'border-amber-500/30 bg-amber-500/5' : 'border-sky-500/30 bg-sky-500/5'}`}>
      <div className="flex flex-wrap items-center gap-x-6 gap-y-1">
        <span className="text-xs text-slate-400">⚡ 今日实时（{new Date(data.asOf).toLocaleTimeString('zh-HK', { hour: '2-digit', minute: '2-digit' })} 更新，60 秒自动刷新）</span>
        <span className={`text-sm font-bold tabular-nums ${day.pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
          组合今日估算 {pct(day.pct, 2)}
        </span>
        {est && <span className={`text-sm font-bold tabular-nums ${est >= 100 ? 'text-emerald-400' : 'text-rose-400'}`}>累计净值估算 {est.toFixed(2)}</span>}
        {benchDay !== null && (
          <span className={`text-xs tabular-nums ${benchDay >= 0 ? 'text-emerald-500/80' : 'text-rose-500/80'}`}>基准今日 {pct(benchDay, 2)}</span>
        )}
        <span className="text-[10px] text-slate-500">覆盖 {day.covered.toFixed(0)}% 仓位</span>
      </div>
      {data.status === 'partial' && <p className="text-[10px] text-amber-400/80 mt-1">部分行情获取失败（{data.failed.join('、')}），估算仅基于成功部分。</p>}
    </div>
  )
}

// ---- Excel 導出（CSV，UTF-8 BOM，Excel 直接打開）----
function ExportButton() {
  const perf = usePerformance()
  const snap = useFileSnapshot()
  const { holdings, lastRebalanceDate } = useEffectivePortfolio()
  function download() {
    const q = (s: unknown) => `"${String(s ?? '').replace(/"/g, '""')}"`
    const L: string[] = []
    L.push(`【持倉權重（截至 ${lastRebalanceDate} 調倉後生效）】`, 'ETF,名稱,主題,權重%,半年收益%')
    for (const e of holdings) L.push([e.ticker, e.name, e.theme, e.weight, e.halfRet].map(q).join(','))
    L.push('', '【當前調倉建議（待人工複核）】', 'ETF,從%,到%,理由')
    for (const c of snap?.suggested ?? []) L.push([c.ticker, c.from, c.to, c.reason].map(q).join(','))
    if (!(snap?.suggested?.length)) L.push(q('（無）'))
    L.push('', '【前向實盤淨值（2026-01-20=100）】', '日期,組合,基準60/40')
    perf.dates.forEach((d, i) => L.push([d, perf.portfolio[i], perf.benchmark[i]].map(q).join(',')))
    L.push('', '【統計】', '指標,組合,基準')
    L.push(['回報%（含交易成本淨）', perf.stats.netRet ?? perf.stats.portRet, perf.stats.benchRet].map(q).join(','))
    L.push(['最大回撤%', perf.stats.maxDD, perf.stats.benchMaxDD].map(q).join(','))
    L.push(['Sharpe', perf.stats.sharpe, perf.stats.benchSharpe].map(q).join(','))
    L.push(['年化波動%', perf.stats.vol, perf.stats.benchVol].map(q).join(','))
    const blob = new Blob([String.fromCharCode(0xFEFF) + L.join('\r\n')], { type: 'text/csv;charset=utf-8' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `etf-portfolio-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(a.href)
  }
  return (
    <button onClick={download}
      className="rounded-md border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 px-3 py-1.5 text-xs font-semibold hover:bg-emerald-500/20">
      📊 導出 Excel（持倉+建議+淨值）
    </button>
  )
}

function Overview() {
  const perf = usePerformance()
  const { holdings, records, lastRebalanceDate } = useEffectivePortfolio()
  const S = perf.stats
  const chartData = perf.dates.map((w, i) => ({ week: w, 组合: perf.portfolio[i], 基准: perf.benchmark[i] }))
  // Phase 15：黃點唔再靠寫死嘅 REBALANCE_MARKS——runtime 記錄（用戶記低嘅真實調倉）自動衍生
  const marks = [...REBALANCE_MARKS, ...records.map(rebalanceMark)]
  const chartWeeks = chartData.map(d => d.week)
  const allVals = [...perf.portfolio, ...perf.benchmark]
  const yMin = Math.floor(Math.min(...allVals) - 1), yMax = Math.ceil(Math.max(...allVals) + 1)
  return (
    <>
      <div className="flex justify-end mb-1"><ExportButton /></div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: '回报（含交易成本净）', value: pct(S.netRet ?? S.portRet, 2), cls: 'text-emerald-400' },
          { label: '基准 60/40（ACWI+AGG）', value: pct(S.benchRet, 2), cls: 'text-slate-300' },
          { label: 'Sharpe（组合 vs 基准）', value: `${S.sharpe} / ${S.benchSharpe}`, cls: 'text-sky-400' },
          { label: '年化波动率（组合 vs 基准）', value: `${S.vol}% / ${S.benchVol}%`, cls: 'text-rose-400' },
        ].map(s => (
          <div key={s.label} className="rounded-xl border border-slate-800 bg-[#0f1729] p-4">
            <p className="text-xs text-slate-400">{s.label}</p>
            <p className={`text-xl font-bold mt-1 ${s.cls}`}>{s.value}</p>
          </div>
        ))}
      </div>
      {/* Phase 18：淨值新鮮度明示——周末/美股休市數字不變屬正常，唔使再估「係咪冇更新」 */}
      <p className="text-[11px] text-slate-500 -mt-4">
        淨值截至 {perf.asOf}（美股收盤價）· 每 30 分鐘自動檢查追加，美股收市後先會有新點 · 周末/休市日數字不變屬正常 · 數據 DB 持久化，容器重啟唔會蒸發
      </p>

      <LiveStrip />

      <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
        <p className="text-sm text-amber-300 font-medium mb-1">⚠ 批判性解读（跟投前必读）</p>
        <p className="text-xs text-slate-300">组合跑赢基准 {(S.portRet - S.benchRet).toFixed(2)}pp，但 <b>Sharpe 仅 {S.sharpe} vs {S.benchSharpe}</b>——超额回报大部分来自更高的风险预算（股票+商品 86% vs 基准 60%），而非纯粹的信号质量。这是回测<b>规则重放（in-sample）</b>：权重由已知观点事后设定，不能证明未来表现（学术上专家/基金经理超额收益持续性很弱）。真正的检验是<b>前向实盘追踪</b>——本站自 2026-07-20 起冻结权重规则，此后表现即真实样本外验证。最大回撤 {S.maxDD}%（基准 {S.benchMaxDD}%）意味着 100 万本金中途最大浮亏约 {Math.round(Math.abs(S.maxDD))} 万，请确认可承受。</p>
      </div>

      <Card title={`组合表现 vs 基准（真实行情，2026-01-20 = 100，已追踪至 ${perf.asOf}）`}
        sub={`数据源：${perf.source}；权重自 ${perf.frozenSince} 冻结，此后为样本外前向追踪。黄点为调仓日期（含「调仓记录」页即时记录的真实调仓，自动同步至此）。净值线为毛口径；上方「回报」卡 = 毛 − 交易成本（单边10bps × 总换手${S.turnover}% = 拖累${S.costDrag}%），全站所有回报数字同一口径、同一序列即時重算。`}>
        <div className="h-80">
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
              <XAxis dataKey="week" tick={{ fill: '#64748b', fontSize: 11 }} interval={10} />
              <YAxis domain={[yMin, yMax]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f1729', border: '1px solid #1e293b', borderRadius: 8, fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="组合" stroke="#38bdf8" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="基准" stroke="#64748b" strokeWidth={1.5} strokeDasharray="5 4" dot={false} />
              {marks.map(m => {
                // Phase 18：記錄日逢周末/美股休市/當日未收市時冇 exact 淨值點——resolveMarkWeek 落位到最近交易日，黃點唔再靜默消失
                const wk = resolveMarkWeek(m.week, chartWeeks)
                const y = wk ? chartData.find(d => d.week === wk) : undefined
                return y ? <ReferenceDot key={`${m.week}-${m.label}`} x={wk ?? undefined} y={y.组合} r={6} fill="#fbbf24" stroke="#0a0f1c" strokeWidth={2} label={{ value: m.label, fill: '#fbbf24', fontSize: 11, position: 'top' }} /> : null
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="当前配置（占组合 %）" sub={`截至 ${lastRebalanceDate} 调仓后生效 · 日股 0%（三专家一致看淡）`}>
          <div className="h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={holdings} dataKey="weight" nameKey="ticker" innerRadius={55} outerRadius={90} paddingAngle={2}>
                  {holdings.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f1729', border: '1px solid #1e293b', borderRadius: 8, fontSize: 12 }} formatter={(v: number) => `${v}%`} />
                <Legend wrapperStyle={{ fontSize: 11 }} layout="vertical" align="right" verticalAlign="middle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="当前最强共识信号 TOP 5" sub="由观点库 + 管道即時觀點 + 时间衰减即时计算（非手工维护）">
          <TopConsensus />
        </Card>
      </div>
    </>
  )
}

function TopConsensus() {
  const { rows } = useMergedConsensus()
  return (
    <div className="space-y-2.5">
      {rows.sort((a, b) => b.net - a.net).slice(0, 5).map(c => (
              <div key={c.theme} className="rounded-lg bg-slate-800/40 px-3 py-2.5">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-100 font-medium">{c.theme}</span>
                  <span className={`text-xs font-bold ${c.net >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>{c.net >= 0 ? `+${c.net}` : c.net}</span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{THEME_ACTIONS[c.theme]}</p>
                <div className="mt-1.5 h-1.5 rounded bg-slate-700/60 overflow-hidden">
                  <div className={`h-full ${c.net >= 0 ? 'bg-emerald-400/80' : 'bg-rose-400/80'}`} style={{ width: `${Math.abs(c.net)}%` }} />
                </div>
              </div>
            ))}
    </div>
  )
}

function Allocation() {
  const { data: quotes } = useQuotes()
  // Phase 13：半年回報係凍結快照值（淨值序列最後日期），唔係「最新」——標籤動態對齊 perf.asOf
  const perf = usePerformance()
  const { holdings, lastRebalanceDate } = useEffectivePortfolio()
  return (
    <>
    <Card title="ETF 组合配置详情" sub={quotes ? `「最新调整」= ${lastRebalanceDate} 调仓变动；实时价 = ${new Date(quotes.asOf).toLocaleTimeString('zh-HK', { hour: '2-digit', minute: '2-digit' })} Yahoo 行情（60秒刷新）；半年回报 = 真实复权价 2026-01-20 → 截至 ${perf.asOf}（净值序列最新日期，此后冻结）` : `「最新调整」= ${lastRebalanceDate} 调仓变动；半年回报 = Yahoo Finance 真实复权价 2026-01-20 → 截至 ${perf.asOf}（静态模式无实时价，数值冻结于此）`}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-400 border-b border-slate-800">
              <th className="py-2 pr-3">ETF</th><th className="pr-3">主题</th>
              <th className="pr-3 text-right">当前配置</th><th className="pr-3 text-right">最新调整</th>
              {quotes && <th className="pr-3 text-right">实时价</th>}
              {quotes && <th className="pr-3 text-right">今日涨跌</th>}
              <th className="pr-3 text-right">半年回报</th><th className="pr-3">观点依据（含视频内容要点）</th><th>追踪</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map(e => (
              <tr key={e.ticker} className="border-b border-slate-800/60 align-top hover:bg-slate-800/20">
                <td className="py-2.5 pr-3"><span className="font-bold text-sky-300">{e.ticker}</span><span className="block text-[10px] text-slate-500">{e.name}</span></td>
                <td className="pr-3 text-slate-400 whitespace-nowrap text-xs">{e.theme}</td>
                <td className="pr-3 text-right font-semibold text-sky-300 tabular-nums">{e.weight.toFixed(2)}%</td>
                <td className={`pr-3 text-right font-semibold tabular-nums ${e.delta > 0 ? 'text-emerald-400' : e.delta < 0 ? 'text-rose-400' : 'text-slate-500'}`}>
                  {e.delta > 0 ? `+${e.delta.toFixed(2)}pp` : e.delta < 0 ? `${e.delta.toFixed(2)}pp` : '—'}
                </td>
                {quotes && (
                  <td className="pr-3 text-right tabular-nums text-slate-200">
                    {quotes.quotes[e.ticker] ? `$${quotes.quotes[e.ticker].price.toFixed(2)}` : <span className="text-slate-600">—</span>}
                  </td>
                )}
                {quotes && (
                  <td className={`pr-3 text-right tabular-nums font-semibold ${(quotes.quotes[e.ticker]?.changePct ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {quotes.quotes[e.ticker] ? pct(quotes.quotes[e.ticker].changePct, 2) : <span className="text-slate-600">—</span>}
                  </td>
                )}
                {/* Phase 13：靜態 halfRet 保留，但標明凍結口徑，避免誤當實時值 */}
                <td className={`pr-3 text-right tabular-nums ${e.halfRet >= 0 ? 'text-emerald-400' : 'text-rose-400'}`} title={`截至 ${perf.asOf}（淨值序列最新日期）`}>{pct(e.halfRet)}</td>
                <td className="pr-3 text-xs text-slate-400 max-w-md">{e.signal}<span className="block text-slate-500 mt-0.5">专家：{e.experts}</span></td>
                <td className="whitespace-nowrap"><a className="text-sky-400 hover:underline text-xs" href={e.tv} target="_blank" rel="noreferrer">TradingView ↗</a></td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="text-sm font-semibold text-slate-200">
              <td className="py-2" colSpan={2}>合计（日股 0%）</td>
              <td className="text-right text-sky-300">{holdings.reduce((s, e) => s + e.weight, 0).toFixed(2)}%</td>
              {/* Phase 13 修復：表 9 欄（有實時價）/ 7 欄（無）——舊 colSpan 令 tfoot 少一格 */}
              <td colSpan={quotes ? 6 : 4}></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <p className="text-xs text-slate-500 mt-3">「组合配置」与「调仓记录」共用同一权重数据源，两处数字必然一致。所有 ETF 均为交易所挂牌，TradingView 链接即真实价格追踪页。</p>

      <h3 className="text-sm font-semibold text-white mt-6 mb-2">观点 → ETF 适配度校验</h3>
      <p className="text-xs text-slate-400 mb-3">每条信号执行前必须通过适配度检查：工具的资产属性、市值风格、地区纯度必须与信号一致（杜绝「看好小盘股却加仓标普500」式错配）</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs text-slate-400 border-b border-slate-800">
            <th className="py-2 pr-3">专家信号</th><th className="pr-3">专家</th><th className="pr-3">执行工具</th><th className="pr-3">适配度</th><th>校验说明</th>
          </tr></thead>
          <tbody>
            {FIT_CHECKS.map((f, i) => (
              <tr key={i} className="border-b border-slate-800/60 align-top">
                <td className="py-2.5 pr-3 text-slate-200 text-xs">{f.signal}</td>
                <td className="pr-3 text-slate-400 whitespace-nowrap text-xs">{f.expert}</td>
                <td className="pr-3 text-slate-300 whitespace-nowrap text-xs">{f.etf}</td>
                <td className="pr-3 w-32">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded bg-slate-700/60 overflow-hidden">
                      <div className={`h-full ${f.fit >= 80 ? 'bg-emerald-400' : f.fit >= 60 ? 'bg-amber-400' : 'bg-rose-400'}`} style={{ width: `${f.fit}%` }} />
                    </div>
                    <span className="text-xs tabular-nums text-slate-300">{f.fit}</span>
                  </div>
                </td>
                <td className="text-xs text-slate-400 max-w-sm">{f.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
    <CorrelationCard />
    </>
  )
}

// ---- 底層資產重複曝光 & 相關性檢查（Phase 7，數據：api/correlation.ts 近1年日收益皮爾遜相關）----
function CorrelationCard() {
  const q = trpc.correlation.report.useQuery(undefined, { retry: 1, staleTime: 30 * 60000 })
  const d = q.data
  const corrCls = (c: number) => Math.abs(c) >= 0.75 ? 'text-rose-300' : Math.abs(c) >= 0.6 ? 'text-amber-300' : 'text-slate-300'
  return (
    <Card title="底層資產重複曝光 & 相關性檢查"
      sub="唔同 ETF 嘅底層資產會重疊（例如 ASHR/MCHI/EWH 都係中國敞口、VOO/XLV 都係美股大公司）——重複持倉=隱形超配。呢度用近 1 年真實日收益計算皮爾遜相關：ρ≥0.75 視為近似重複曝光；分組權重合計與量化引擎嘅 S9 熱度閘門同一口徑（上限 30pp，超標組會被算法否決加倉）">
      {q.isError ? (
        <div className="rounded-lg border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-500">
          後端未連接（靜態預覽模式）——部署後此處顯示 19 隻持倉 ETF 嘅實測相關配對同埋分組敞口合計。
        </div>
      ) : !d ? (
        <div className="rounded-lg border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-400 animate-pulse">
          相關性計算中（首次需拉取 19 隻 ETF 一年日線，約 10 秒）…
        </div>
      ) : d.status === 'unavailable' ? (
        <div className="rounded-lg border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-500">行情源暫時不可用，下一小時自動重試。</div>
      ) : (
        <>
          {/* 分組敞口：同 S9 閘門口徑 */}
          <h3 className="text-xs font-semibold text-slate-300 mb-2">底層敞口分組（S9 熱度閘門口徑，上限 30pp）</h3>
          <div className="grid md:grid-cols-2 gap-2 mb-4">
            {d.groups.map(g => (
              <div key={g.name} className={`rounded-lg border px-3 py-2 ${g.over ? 'border-rose-500/40 bg-rose-500/5' : (g.intraCorr ?? 0) >= 0.75 ? 'border-amber-500/40 bg-amber-500/5' : 'border-slate-800 bg-slate-800/30'}`}>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-200 font-medium">{g.name}</span>
                  <span className="text-slate-500">{g.members.join(' + ')}</span>
                  <span className={`ml-auto tabular-nums font-bold ${g.over ? 'text-rose-300' : 'text-sky-300'}`}>{g.weight}%</span>
                </div>
                <div className="w-full h-1.5 rounded bg-slate-700/60 overflow-hidden mt-1.5">
                  <div className={`h-full ${g.over ? 'bg-rose-400' : g.weight >= 24 ? 'bg-amber-400' : 'bg-emerald-400'}`} style={{ width: `${Math.min(100, g.weight / 30 * 100)}%` }} />
                </div>
                <p className="text-[10px] text-slate-500 mt-1">
                  {g.intraCorr != null ? <>組內平均相關 <span className={corrCls(g.intraCorr)}>{g.intraCorr.toFixed(2)}</span>{g.intraCorr >= 0.75 ? '（近似重複曝光）' : ''} · </> : ''}{g.note}{g.over ? ' · ⚠ 超過 30pp，S9 閘門會否決該組任何加倉' : ''}
                </p>
              </div>
            ))}
          </div>
          {/* 高相關配對 */}
          <h3 className="text-xs font-semibold text-slate-300 mb-2">高相關配對（|ρ|≥0.6，近 1 年日收益實測）</h3>
          {d.pairs.length === 0 ? (
            <p className="text-xs text-emerald-300 mb-2">✓ 無 |ρ|≥0.6 嘅配對——持倉之間重複曝光低。</p>
          ) : (
            <div className="flex flex-wrap gap-1.5 mb-3">
              {d.pairs.map(p => (
                <span key={`${p.a}-${p.b}`} className={`text-[11px] px-2 py-0.5 rounded border tabular-nums ${p.corr >= 0.75 ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : 'bg-amber-500/10 text-amber-300 border-amber-500/30'}`}>
                  {p.a}×{p.b} ρ={p.corr.toFixed(2)}{p.corr >= 0.75 ? ' 近似重複' : ''}
                </span>
              ))}
            </div>
          )}
          <p className="text-[11px] text-slate-500 leading-relaxed border-t border-slate-800 pt-2">
            誠實聲明：相關性係歷史價格行為代理（數據截至 {d.asOfDate ?? '—'}，每對最少 30 個共同交易日），唔係成分股穿透分析——本站冇 ETF 持倉明細數據；而且跌市時風險資產相關性會趨向 1，低相關唔等於跌市時一定分散。{d.status === 'partial' ? `⚠ 部分行情缺失（${d.failed.join('、')}），相關配對可能少報。` : ''} 應對方法：① 同一分組權重合計唔超 30pp（算法 S9 閘門已強制執行）；② 加倉前睇呢度——如果候選 ETF 同現有重倉 ρ≥0.75，等於變相加注同一敞口；③ 債券現金系（TLT/BND/SGOV）係組合入面主要嘅低相關對沖腿。
          </p>
        </>
      )}
      {/* 候選 ETF 篩選器（Phase 11）——同相關性卡同一數據口徑，獨立運作 */}
      <ScreenerSection />
    </Card>
  )
}

// ---- 候選 ETF 篩選器（Phase 11，數據：api/screener.ts）----
// 源起：用戶問「covered call ETF 同其他 ETF 相關性係咪好高？總回報會唔會打贏？應唔應該做篩選？」
// 實測答案：相關性的確高（0.68–0.95），但牛市總回報全部跑輸本尊——所以篩選器俾嘅係
// 誠實判語（重疊度/回報/風險/成本攤開 + 寫死嘅白名單規則），唔係「高分就加」。
function ScreenerSection() {
  const [input, setInput] = useState('')
  const m = trpc.correlation.screen.useMutation()
  const go = (t: string) => { const tt = t.trim().toUpperCase(); if (tt && !m.isPending) m.mutate({ ticker: tt }) }
  const tierBox: Record<string, string> = {
    avoid: 'border-rose-500/40 bg-rose-500/10',
    substitute: 'border-amber-500/40 bg-amber-500/10',
    limited: 'border-sky-500/40 bg-sky-500/10',
    diversifier: 'border-emerald-500/40 bg-emerald-500/10',
  }
  const tierText: Record<string, string> = { avoid: 'text-rose-200', substitute: 'text-amber-200', limited: 'text-sky-200', diversifier: 'text-emerald-200' }
  const tierLabel: Record<string, string> = { avoid: '⛔ 唔建議加入', substitute: '🔁 只宜替代式持有', limited: '◐ 有限分散價值', diversifier: '✓ 具分散價值' }
  const r = m.data && m.data.ok ? m.data.result : null
  const fmtAum = (v: number) => v >= 1e9 ? `${(v / 1e9).toFixed(1)}B` : `${(v / 1e6).toFixed(0)}M`
  const chip = (txt: string, cls = 'border-slate-700 bg-slate-800/40 text-slate-300') => (
    <span key={txt} className={`text-[11px] px-2 py-0.5 rounded border tabular-nums ${cls}`}>{txt}</span>
  )
  const corrCls = (c: number | null) => c == null ? 'border-slate-700 bg-slate-800/40 text-slate-500'
    : Math.abs(c) >= 0.75 ? 'border-rose-500/30 bg-rose-500/10 text-rose-300'
    : Math.abs(c) >= 0.6 ? 'border-amber-500/30 bg-amber-500/10 text-amber-300'
    : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  return (
    <div className="mt-4 border-t border-slate-800 pt-3">
      <h3 className="text-xs font-semibold text-slate-300 mb-1">候選 ETF 篩選器（買新嘢前必過呢關）</h3>
      <p className="text-[11px] text-slate-500 mb-2 leading-relaxed">
        輸入任何美股 ETF ticker——系統會計佢同現有組合嘅重疊度、近 1 年回報/波動/回撤、息率同費率，然後俾明確判語（規則寫死，唔經 LLM，唔會編造）。結論永遠只係建議，落唔落單人工決定。
      </p>
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') go(input) }}
          placeholder="輸入 ticker，例如 JEPI" maxLength={12}
          className="w-40 rounded-md border border-slate-700 bg-slate-900/60 px-2.5 py-1.5 text-xs text-slate-200 placeholder:text-slate-600 focus:border-sky-500/60 focus:outline-none uppercase" />
        <button onClick={() => go(input)} disabled={m.isPending || !input.trim()}
          className="rounded-md bg-sky-500/20 border border-sky-500/40 px-3 py-1.5 text-xs text-sky-200 hover:bg-sky-500/30 active:bg-sky-500/45 disabled:opacity-40">
          {m.isPending ? '篩選中…' : '篩選'}
        </button>
        <span className="text-[10px] text-slate-600">試下：</span>
        {['JEPI', 'JEPQ', 'QYLD', 'XYLD'].map(t => (
          <button key={t} onClick={() => { setInput(t); go(t) }} disabled={m.isPending}
            className="rounded-md border border-slate-700 bg-slate-800/40 px-2 py-1.5 text-[11px] text-slate-400 hover:text-slate-200 hover:border-slate-600 active:bg-slate-700/60 disabled:opacity-40">{t}</button>
        ))}
      </div>
      {m.isPending && (
        <div className="rounded-lg border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-400 animate-pulse">
          篩選計算中（首次需拉取約 20 隻 ETF 一年日線，10–30 秒）…
        </div>
      )}
      {m.isError && (
        <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-xs text-rose-300">篩選失敗：{m.error?.message ?? '未知錯誤'}</div>
      )}
      {m.data && !m.data.ok && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-xs text-amber-300">{m.data.error}</div>
      )}
      {r && (
        <div className="rounded-lg border border-slate-800 bg-slate-800/30 px-4 py-3">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 mb-2">
            <span className="text-sm font-bold text-slate-100">{r.ticker}</span>
            <span className="text-xs text-slate-400">{r.name ?? '—'}{r.fundFamily ? ` · ${r.fundFamily}` : ''}{r.aumUsd != null ? ` · 規模 ${fmtAum(r.aumUsd)}` : ''}</span>
            <span className="text-[10px] text-slate-600 ml-auto">數據截至 {r.asOfDate ?? '—'}</span>
          </div>
          <div className="flex flex-wrap gap-1.5 mb-2">
            {chip(`1y 回報 ${(r.stats1y.ret * 100).toFixed(1)}%`, r.bench.vooRet1y != null && r.stats1y.ret >= r.bench.vooRet1y ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' : r.stats1y.ret < 0 ? 'border-rose-500/30 bg-rose-500/10 text-rose-300' : undefined)}
            {chip(`波動 ${(r.stats1y.vol * 100).toFixed(1)}%`)}
            {chip(`最大回撤 ${(r.stats1y.mdd * 100).toFixed(1)}%`)}
            {chip(`息率 ${r.yieldPct != null ? r.yieldPct.toFixed(1) + '%' : '—'}`, (r.yieldPct ?? 0) >= 6 ? 'border-amber-500/30 bg-amber-500/10 text-amber-300' : undefined)}
            {chip(`費率 ${r.expenseRatioPct != null ? r.expenseRatioPct.toFixed(2) + '%' : '—'}`)}
            {chip(`同期 VOO ${r.bench.vooRet1y != null ? (r.bench.vooRet1y * 100).toFixed(1) + '%' : '—'}`)}
          </div>
          <div className="flex flex-wrap gap-1.5 mb-2">
            {chip(`同組合 ρ=${r.corrToPortfolio?.toFixed(2) ?? '—'}`, corrCls(r.corrToPortfolio))}
            {chip(`持倉加權平均 ρ=${r.avgCorrToHoldings?.toFixed(2) ?? '—'}`, corrCls(r.avgCorrToHoldings))}
            {chip(`vs VOO ρ=${r.corrToVOO?.toFixed(2) ?? '—'}`, corrCls(r.corrToVOO))}
            {chip(`vs ACWI ρ=${r.corrToACWI?.toFixed(2) ?? '—'}`, corrCls(r.corrToACWI))}
            {r.maxPair ? chip(`最高重疊：${r.maxPair.holding} ρ=${r.maxPair.corr.toFixed(2)}`, corrCls(r.maxPair.corr)) : null}
          </div>
          <div className={`rounded-lg border px-3 py-2 mb-2 ${tierBox[r.verdict.tier]}`}>
            <div className={`text-xs font-bold mb-1 ${tierText[r.verdict.tier]}`}>{tierLabel[r.verdict.tier]}</div>
            <p className={`text-xs leading-relaxed ${tierText[r.verdict.tier]}`}>{r.verdict.headline}</p>
            <ul className="text-[11px] leading-relaxed mt-1 space-y-0.5 text-slate-400">
              {r.verdict.points.map((p, i) => <li key={i}>· {p}</li>)}
            </ul>
          </div>
          {r.failed.length > 0 && <p className="text-[10px] text-amber-400/80 mb-1">⚠ 部分持倉行情缺失（{r.failed.join('、')}），相關計算以可用持倉為準。</p>}
          <p className="text-[10px] text-slate-600 leading-relaxed">{r.honest}</p>
        </div>
      )}
    </div>
  )
}

function Consensus() {
  const { rows, liveCount, snapDate } = useMergedConsensus()
  const cellCls = (v: string | null) =>
    v === 'bull' ? 'bg-emerald-500/25 text-emerald-300' :
    v === 'bear' ? 'bg-rose-500/25 text-rose-300' :
    v === 'neutral' ? 'bg-slate-600/30 text-slate-400' : 'text-slate-700'
  // Phase 13 降級態：冇新鮮即時觀點，或全部觀點已過 90 日衰減歸零（矩陣全空）時要明確提示
  const hasAnyCell = rows.some(r => Object.values(r.cells).some(c => c !== null))
  return (
    <Card title="信号共识矩阵" sub="由专家观点库 + 管道即時觀點 + 时间衰减【即时计算】生成。行=资产主题，列=专家；净分 -100 ~ +100；即時信號按強度（1-5）歸一化加權">
      {liveCount > 0 && (
        <p className="text-xs text-emerald-300/90 mb-3">✅ 已併入 {snapDate} 快照的 {liveCount} 條管道即時觀點（字幕級證據）——矩陣反映最新專家信號</p>
      )}
      {liveCount === 0 && hasAnyCell && (
        <p className="text-xs text-amber-300/90 mb-3">⚠ 暫無新鮮觀點（冷卻期外）——矩陣僅反映舊版靜態檔案，共識僅供參考；最新信號請睇「每日更新」頁。</p>
      )}
      {!hasAnyCell && (
        <p className="text-xs text-amber-300/90 mb-3">⚠ 暫無新鮮觀點（冷卻期外）——全部觀點已超 90 日衰減歸零，共識僅供參考；請到「每日更新」頁運行管道或手動錄入。</p>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-slate-400 border-b border-slate-800">
              <th className="py-2 pr-2 text-left">资产主题</th>
              {EXPERT_COLS.map(id => <th key={id} className="px-1 text-center whitespace-nowrap">{EXPERT_NAMES[id]}</th>)}
              <th className="px-2 text-center">净共识</th>
              <th className="pl-2 text-left">组合动作</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.theme} className="border-b border-slate-800/60">
                <td className="py-2 pr-2 text-slate-100 font-medium whitespace-nowrap">{r.theme}</td>
                {EXPERT_COLS.map(id => {
                  const v = r.cells[id]
                  return <td key={id} className="px-1 py-1 text-center">
                    <span className={`inline-block w-6 h-6 leading-6 rounded ${cellCls(v)}`}>
                      {v === 'bull' ? '▲' : v === 'bear' ? '▼' : v === 'neutral' ? '●' : '·'}
                    </span>
                  </td>
                })}
                <td className="px-2 text-center">
                  <span className={`font-bold tabular-nums ${r.net >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>{r.net >= 0 ? `+${r.net}` : r.net}</span>
                </td>
                <td className="pl-2 text-slate-300">{THEME_ACTIONS[r.theme]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-500 mt-3">▲ 看好　▼ 看淡　● 中性　· 无相关观点（含超90天已失效观点）。单元格 = 该专家全部相关观点按衰减权重加权的净方向（|分|&gt;0.15 才算有方向）；净共识按专家动态权重加权。多空并读规则：对冲信号取净值并降低仓位变动幅度。</p>
    </Card>
  )
}

// 網絡能力自檢卡：一鍵探測當前部署環境能走通哪些渠道
function NetCheckCard() {
  const q = trpc.pipeline.netCheck.useQuery(undefined, { retry: false, staleTime: 0 })
  const d = q.data
  const Pill = ({ ok, label }: { ok: boolean | undefined; label: string }) => (
    <span className={`px-2 py-1 rounded text-xs border ${ok == null ? 'bg-slate-600/20 text-slate-500 border-slate-600/40' : ok ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : 'bg-rose-500/10 text-rose-300 border-rose-500/30'}`}>
      {ok == null ? '…' : ok ? '✓' : '✗'} {label}
    </span>
  )
  const ytOk = d ? d.googleapis && d.youtube : undefined
  return (
    <Card title="網絡能力自檢" sub="探測當前部署環境的出口能力——決定專家字幕管道能否自動運行">
      <div className="flex flex-wrap gap-2 mb-3">
        <Pill ok={ytOk} label="YouTube 直連" />
        <Pill ok={d?.kome} label="字幕代理" />
        <Pill ok={d?.brave} label="Brave 新聞" />
        <Pill ok={d?.moonshot} label="Kimi API" />
        <Pill ok={d?.agentGw} label="行情+新聞網關" />
      </div>
      {d && !d.kome && d.komeDetail && (
        <p className="text-xs text-rose-300 mb-2">✗ 字幕代理（kome.ai）：{d.komeDetail}——「自動抓字幕」會如實報錯並話你知點做；請用方法二（YouTube「顯示文字記錄」複製）或方法三（截圖 OCR）。</p>
      )}
      {d && !d.moonshot && d.moonshotDetail && (
        <p className="text-xs text-rose-300 mb-2">✗ Kimi API：{d.moonshotDetail}——LLM 結構化/OCR/新聞搜索暫停，但字幕抓取與行情、建議引擎不受影響；可用「手動錄入」或 Agent 結構化通道入庫。</p>
      )}
      {d && !d.moonshot && (
        <p className="text-xs text-slate-400 mb-2 leading-relaxed">ℹ 點解你係 Kimi Allegro 會員都冇 API 額度？因為 <b className="text-slate-200">Allegro 會員（kimi.com 消費者訂閱）同 Moonshot 開放平台 API（platform.moonshot.cn 按量計費）係兩套獨立帳務</b>——會員身份唔會為 API key 充值。不過本站每日 HKT 09:00 嘅 Agent 掃描入庫通道用的正正係你嘅 Kimi 會員側能力（唔經 API key），所以專家觀點每日照舊自動更新；要恢復嘅只係 OCR 截圖轉錄、Kimi 新聞搜索同服務端全自動結構化（充值或更換 API key 即恢復）。</p>
      )}
      {d && (
        ytOk
          ? <p className="text-xs text-emerald-300">✅ 當前環境可直連 YouTube——專家字幕管道每日 HKT 08:00 自動運行，無需任何手動操作。</p>
          : d.kome
            ? <p className="text-xs text-emerald-300 leading-relaxed">✅ 雖然 YouTube 直連被封，但<b>字幕代理通道可用</b>——在下方「手動錄入」貼上 YouTube 鏈接即可自動抓完整字幕（約 5 秒/條）；Wind 專家新聞通道每日自動掃描 8 位專家的媒體報道。開放網絡部署（Dockerfile 已備好）則全頻道自動化。</p>
            : <p className="text-xs text-amber-300 leading-relaxed">⚠ 當前環境無法直連 YouTube，字幕代理也不可用。專家觀點兩條路：① 下方「手動錄入」——截圖 OCR 或複製字幕貼上來（字幕級證據，與自動管道同一引擎）；② 把網站部署到自己的服務器/電腦（Dockerfile 已備好），開放網絡下字幕管道全自動恢復，代碼零改動。</p>
      )}
    </Card>
  )
}

// 手動錄入專家觀點：YouTube「顯示文字記錄」複製字幕 → 粘貼 → 同一套結構化引擎入庫
const MANUAL_EXPERTS = ['蔡金強', '譚新強', '洪灝', '林本利', '林一鳴', '莊太量', 'Jurrien Timmer', '蔡嘉民 Calvin']
function ManualViewForm({ onAdded }: { onAdded: () => void }) {
  const [expert, setExpert] = useState(MANUAL_EXPERTS[0])
  const [customExpert, setCustomExpert] = useState('')
  const [title, setTitle] = useState('')
  const [url, setUrl] = useState('')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [content, setContent] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  // async job 模式：submit 即時返回 jobId（校驗層錯誤同步返回），真正結構化喺後台跑，
  // 前端輪詢 manualViewJob 攞結果——避免平台代理逾時令 Safari 拋「did not match the expected pattern」
  const [jobId, setJobId] = useState<string | null>(null)
  // Phase 19 卡死修復：輪詢 query 本身報錯時 q.state.data 係 undefined，舊版 refetchInterval 繼續 3000
  // → 無限「Kimi 結構化中…」零反饋。加 pollIssue（可查詢錯/超時，撳「重新查詢」復活）+ submitAt（計時/超時）。
  const [pollIssue, setPollIssue] = useState<string | null>(null)
  const [submitAt, setSubmitAt] = useState<number | null>(null)
  const POLL_TIMEOUT_MS = 8 * 60 * 1000
  const submit = trpc.pipeline.submitManualView.useMutation({
    onSuccess: (r) => {
      if (r.ok) { setJobId(r.jobId); setSubmitAt(Date.now()); setPollIssue(null) } // 開始輪詢
      else setMsg(`❌ ${r.error}`) // 校驗層錯誤即刻見
    },
    onError: (e) => setMsg(`❌ 提交失敗：${friendlyNetworkError(e.message)}`),
  })
  const job = trpc.pipeline.manualViewJob.useQuery(
    { jobId: jobId ?? '' },
    {
      enabled: !!jobId,
      retry: 1,
      // done/failed/unknown 都係終態，停止輪詢；pollIssue / query 級錯誤 / 超時都停（唔好無限零反饋輪詢）
      refetchInterval: (q) => {
        if (pollIssue) return false
        if (q.state.error) return false
        const s = q.state.data?.status
        if (s === 'done' || s === 'failed' || s === 'unknown') return false
        if (submitAt && Date.now() - submitAt > POLL_TIMEOUT_MS) return false
        return 3000
      },
    },
  )
  // 輪詢 query 級網絡錯誤（代理 reset 等）——後台 job 可能仲行緊，俾用戶「重新查詢」繼續跟進
  useEffect(() => {
    if (jobId && job.error && !pollIssue) {
      setPollIssue(`❌ 查詢結果時網絡出錯：${friendlyNetworkError(job.error.message)}——後台工作可能仍在進行，撳「🔄 重新查詢」繼續跟進，內容已保留`)
    }
  }, [job.error, jobId, pollIssue])
  // 輪詢超時兜底：一次性 timer（唔使每 3 秒 poll 先有機會觸發——poll 停咗之後冇重渲染）
  useEffect(() => {
    if (!jobId || !submitAt) return
    const remain = POLL_TIMEOUT_MS - (Date.now() - submitAt)
    const fire = () => {
      const s = job.data?.status
      if (s !== 'done' && s !== 'failed' && s !== 'unknown') {
        setPollIssue('❌ 等待超時（8 分鐘）——後台工作可能仍在進行，撳「🔄 重新查詢」繼續跟進，內容已保留')
      }
    }
    if (remain <= 0) { fire(); return }
    const t = setTimeout(fire, remain)
    return () => clearTimeout(t)
  }, [jobId, submitAt, job.data?.status]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const d = job.data
    if (!d || !jobId) return
    if (d.status === 'done') {
      const r = d.result
      if (r?.ok) {
        setMsg(`✅ 已入庫：提取到 ${r.signalCount ?? 0} 個信號${(r.signalCount ?? 0) === 0 ? '（內容無明確資產方向，誠實留空）' : ''}；建議引擎已重算。`)
        setTitle(''); setUrl(''); setContent('')
        onAdded()
      } else {
        // 失敗絕對唔清 content/title/url——用戶可能貼咗幾千字，一錯就冇晒會嬲爆
        setMsg(`❌ ${friendlyNetworkError(r?.error ?? '入庫失敗')}`)
      }
      setJobId(null); setSubmitAt(null); setPollIssue(null)
    } else if (d.status === 'failed' || d.status === 'unknown') {
      setMsg(`❌ ${friendlyNetworkError(d.error ?? d.result?.error ?? '工作失蹤，請重試——內容已保留')}`)
      setJobId(null); setSubmitAt(null); setPollIssue(null)
    }
  }, [job.data, jobId]) // eslint-disable-line react-hooks/exhaustive-deps
  const finalExpert = expert === '__custom__' ? customExpert.trim() : expert
  const canSubmit = finalExpert.length > 0 && title.trim().length > 0 && content.trim().length >= 100 && !submit.isPending && !jobId

  // 貼鏈接抓字幕：字幕代理通道（受限網絡可達）——最快路徑，5 秒拿回完整字幕
  // Phase 19 智能串聯：後端就算字幕失敗都會經 noembed 攞 title/author——
  // 自動填標題 + 按頻道映射自動揀專家（映射唔中唔亂揀）；字幕失敗時照樣用 meta，error 本身已含方法二/三指引。
  const fetchSubs = trpc.pipeline.fetchVideoTranscript.useMutation({
    onSuccess: (r) => {
      const notes: string[] = []
      const meta = r.meta
      if (meta?.title && !title.trim()) { setTitle(meta.title); notes.push('已自動填入標題') }
      if (meta?.author) {
        const a = meta.author.toLowerCase()
        const mapped = a.includes('octalk') ? '蔡金強'
          : (a.includes('hket') || a.includes('sunchannel')) ? '譚新強'
          : a.includes('etnet') ? '洪灝'
          : (meta.author.includes('大师说') || meta.author.includes('大師說')) ? '洪灝'
          : null
        if (mapped && MANUAL_EXPERTS.includes(mapped)) { setExpert(mapped); notes.push(`已按頻道自動揀咗 ${mapped}，可手動改`) }
      }
      if (r.ok && r.text) {
        setContent(r.text)
        setMsg(`✅ 字幕抓取成功（${r.chars} 字）——已填入下方文本框${notes.length ? `；${notes.join('；')}` : ''}，核對後按「結構化並入庫」`)
      } else setMsg(`❌ ${r.error}${notes.length ? `（${notes.join('；')}）` : ''}`)
    },
    onError: (e) => setMsg(`❌ 抓取失敗：${e.message}`),
  })

  // 截圖 OCR：手機上「文字記錄」常無法複製——截圖上傳，vision 模型轉錄後回填文本框
  const fileRef = useRef<HTMLInputElement>(null)
  const [ocrCount, setOcrCount] = useState(0)
  const ocr = trpc.pipeline.ocrTranscript.useMutation({
    onSuccess: (r) => {
      if (r.ok && r.text) {
        setContent(prev => (prev.trim() ? prev.trim() + '\n' : '') + r.text!)
        setMsg(`✅ 截圖識別完成（${r.chars} 字）——已填入下方文本框，請快速核對後按「結構化並入庫」`)
      } else setMsg(`❌ ${r.error}`)
    },
    onError: (e) => setMsg(`❌ OCR 失敗：${e.message}`),
  })
  async function compressImage(file: File): Promise<string> {
    const bmp = await createImageBitmap(file)
    const scale = Math.min(1, 1400 / Math.max(bmp.width, bmp.height))
    const c = document.createElement('canvas')
    c.width = Math.round(bmp.width * scale); c.height = Math.round(bmp.height * scale)
    c.getContext('2d')!.drawImage(bmp, 0, 0, c.width, c.height)
    return c.toDataURL('image/jpeg', 0.85)
  }
  async function onPickImages(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []).slice(0, 8)
    e.target.value = ''
    if (!files.length) return
    setOcrCount(files.length)
    try {
      const urls = await Promise.all(files.map(compressImage))
      ocr.mutate({ images: urls })
    } catch { setMsg('❌ 圖片讀取失敗，請重試') }
  }

  // 批量導入：一次貼多條 YouTube 鏈接（每行一條，≤10），後端批量抓字幕→結構化→單次快照合併
  // Phase 19：改 async job 模式（submitBatchImport + manualViewJob 輪詢）——舊同步 mutation 動輒幾分鐘，
  // 必然超過平台代理逾時（Safari 拋非 JSON 錯誤）。與單條錄入共用同一套 pollIssue/submitAt pattern。
  const [batchUrls, setBatchUrls] = useState('')
  const [showBatch, setShowBatch] = useState(false)
  const [batchJobId, setBatchJobId] = useState<string | null>(null)
  const [batchPollIssue, setBatchPollIssue] = useState<string | null>(null)
  const [batchSubmitAt, setBatchSubmitAt] = useState<number | null>(null)
  const BATCH_POLL_TIMEOUT_MS = 11 * 60 * 1000 // 後端 watchdog 10 分鐘，前端畀多少少等終態返嚟
  const batchSubmit = trpc.pipeline.submitBatchImport.useMutation({
    onSuccess: (r) => {
      if (r.ok) { setBatchJobId(r.jobId); setBatchSubmitAt(Date.now()); setBatchPollIssue(null) }
      else setMsg(`❌ ${r.error}`)
    },
    onError: (e) => setMsg(`❌ 批量導入提交失敗：${friendlyNetworkError(e.message)}`),
  })
  const batchJob = trpc.pipeline.manualViewJob.useQuery(
    { jobId: batchJobId ?? '' },
    {
      enabled: !!batchJobId,
      retry: 1,
      refetchInterval: (q) => {
        if (batchPollIssue) return false
        if (q.state.error) return false
        const s = q.state.data?.status
        if (s === 'done' || s === 'failed' || s === 'unknown') return false
        if (batchSubmitAt && Date.now() - batchSubmitAt > BATCH_POLL_TIMEOUT_MS) return false
        return 3000
      },
    },
  )
  useEffect(() => {
    if (batchJobId && batchJob.error && !batchPollIssue) {
      setBatchPollIssue(`❌ 查詢批量進度時網絡出錯：${friendlyNetworkError(batchJob.error.message)}——後台工作可能仍在進行，撳「🔄 重新查詢」繼續跟進`)
    }
  }, [batchJob.error, batchJobId, batchPollIssue])
  useEffect(() => {
    if (!batchJobId || !batchSubmitAt) return
    const remain = BATCH_POLL_TIMEOUT_MS - (Date.now() - batchSubmitAt)
    const fire = () => {
      const s = batchJob.data?.status
      if (s !== 'done' && s !== 'failed' && s !== 'unknown') {
        setBatchPollIssue('❌ 等待超時（11 分鐘）——後台批量導入可能仍在進行，撳「🔄 重新查詢」繼續跟進')
      }
    }
    if (remain <= 0) { fire(); return }
    const t = setTimeout(fire, remain)
    return () => clearTimeout(t)
  }, [batchJobId, batchSubmitAt, batchJob.data?.status]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const d = batchJob.data
    if (!d || !batchJobId) return
    if (d.status === 'done') {
      const r = d.result
      if (r?.ok) {
        const fails = r.failedList ?? []
        const failNote = fails.length ? `；${fails.length} 條失敗（${fails.map(f => `${f.url}：${f.error}`).slice(0, 2).join('；')}）` : ''
        setMsg(`✅ 批量導入完成：${r.imported ?? 0} 條入庫、共 ${r.signalCount ?? 0} 個信號${failNote}`)
        if ((r.imported ?? 0) > 0) { setBatchUrls(''); onAdded() }
      } else setMsg(`❌ ${friendlyNetworkError(r?.error ?? '批量導入失敗')}`)
      setBatchJobId(null); setBatchSubmitAt(null); setBatchPollIssue(null)
    } else if (d.status === 'failed' || d.status === 'unknown') {
      setMsg(`❌ ${friendlyNetworkError(d.error ?? d.result?.error ?? '批量導入工作失蹤，請重試')}`)
      setBatchJobId(null); setBatchSubmitAt(null); setBatchPollIssue(null)
    }
  }, [batchJob.data, batchJobId]) // eslint-disable-line react-hooks/exhaustive-deps
  const batchList = batchUrls.split('\n').map(s => s.trim()).filter(Boolean)

  return (
    <Card title="手動錄入專家觀點（字幕級證據）" sub="受限網絡下抓取專家 YouTube 觀點的正式通道——證據等級與自動字幕管道完全相同">
      <div className="rounded-lg bg-sky-500/5 border border-sky-500/20 p-3 mb-4 text-xs text-sky-300 leading-relaxed">
        <b>方法一（最快）：</b>貼 YouTube 鏈接 → 按「🔗 自動抓字幕」——成功約 5 秒；若字幕服務失效會如實話你知，自動改行方法二/三（標題同專家會照樣自動填）。<br/>
        <b>方法二（最穩陣）：</b>YouTube App/網頁「顯示文字記錄」全選複製貼落嚟。<br/>
        <b>方法三：</b>截圖 OCR——把「文字記錄」逐屏截圖（邊拉邊截，3–8 張）→ 點「📷 上傳截圖」——vision 模型自動轉錄。三條路徑證據等級完全相同。<br/>
        <b>批量模式：</b>點下方「📦 批量導入」一次貼多條鏈接（每行一條，最多 10 條）——背景運行，可隨時離開，呢頁會自動更新結果。
      </div>
      <div className="mb-4">
        <button type="button" onClick={() => setShowBatch(v => !v)}
          className="text-xs rounded-md border border-violet-500/30 bg-violet-500/10 text-violet-300 px-3 py-1.5 hover:bg-violet-500/20">
          {showBatch ? '收起批量導入 ▲' : '📦 批量導入（多條鏈接一次入庫）▼'}
        </button>
        {showBatch && (
          <div className="mt-2 rounded-lg border border-violet-500/20 bg-violet-500/5 p-3">
            <textarea value={batchUrls} onChange={e => setBatchUrls(e.target.value)} rows={5}
              placeholder={'每行一條 YouTube 鏈接，例如：\nhttps://www.youtube.com/watch?v=xxxxxxxxxxx\nhttps://youtu.be/yyyyyyyyyyy'}
              className="w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500" />
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              <button type="button"
                onClick={() => batchSubmit.mutate({ urls: batchList.slice(0, 10), expertName: finalExpert || undefined })}
                disabled={!batchList.length || batchSubmit.isPending || !!batchJobId}
                className="rounded-md border border-violet-500/40 bg-violet-500/15 text-violet-200 px-4 py-2 text-sm font-semibold disabled:opacity-40">
                {batchSubmit.isPending || batchJobId
                  ? `批量導入中${batchJob.data?.stage ? `｜${batchJob.data.stage}` : ''}…（背景運行，可隨時離開）`
                  : `開始批量導入（${Math.min(batchList.length, 10)} 條）`}
              </button>
              <span className="text-[10px] text-slate-500">以「{finalExpert || 'YouTube 頻道'}」名義入庫 · 已入庫的視頻自動跳過 · 只寫一次快照</span>
            </div>
            {batchPollIssue && (
              <div className="mt-2 flex items-center gap-2 flex-wrap rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-2">
                <p className="text-xs text-amber-200 flex-1 min-w-48">{batchPollIssue}</p>
                <button type="button"
                  onClick={() => { setBatchPollIssue(null); setBatchSubmitAt(Date.now()); batchJob.refetch() }}
                  className="shrink-0 rounded-md border border-amber-500/50 bg-amber-500/20 text-amber-100 px-3 py-1 text-xs font-semibold hover:bg-amber-500/30">
                  🔄 重新查詢
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="text-xs text-slate-400">專家
          <select value={expert} onChange={e => setExpert(e.target.value)}
            className="mt-1 w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200">
            {MANUAL_EXPERTS.map(n => <option key={n} value={n}>{n}</option>)}
            <option value="__custom__">其他（自訂）…</option>
          </select>
        </label>
        {expert === '__custom__' && (
          <label className="text-xs text-slate-400">專家名
            <input value={customExpert} onChange={e => setCustomExpert(e.target.value)} placeholder="例如：但斌"
              className="mt-1 w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200" />
          </label>
        )}
        <label className="text-xs text-slate-400">標題
          <input value={title} onChange={e => setTitle(e.target.value)} placeholder="視頻/文章標題"
            className="mt-1 w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200" />
        </label>
        <label className="text-xs text-slate-400">發布日期
          <input type="date" value={date} onChange={e => setDate(e.target.value)}
            className="mt-1 w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200" />
        </label>
        <label className="text-xs text-slate-400 sm:col-span-2">來源鏈接（貼上 YouTube 鏈接 → 按右側按鈕自動抓字幕）
          <div className="mt-1 flex gap-2">
            <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://www.youtube.com/watch?v=…"
              onBlur={() => setUrl(u => canonicalYtUrl(u.trim()))}
              className="flex-1 rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200" />
            <button type="button" onClick={() => { const u = canonicalYtUrl(url.trim()); if (!u) return; setUrl(u); fetchSubs.mutate({ url: u }) }}
              disabled={!url.trim() || fetchSubs.isPending}
              className="shrink-0 rounded-md bg-emerald-600/80 hover:bg-emerald-600 disabled:opacity-40 px-4 py-2 text-sm text-white transition-colors">
              {fetchSubs.isPending ? '抓取中…' : '🔗 自動抓字幕'}
            </button>
          </div>
        </label>
      </div>
      <div className="mt-3 rounded-lg border border-dashed border-slate-600 bg-slate-800/30 p-3 flex items-center justify-between gap-3 flex-wrap">
        <div className="text-xs text-slate-400 leading-relaxed">
          <b className="text-slate-300">📷 截圖直接識別</b>（可多選，≤8 張）——vision 模型轉錄字幕，自動填入下方文本框
        </div>
        <button onClick={() => fileRef.current?.click()} disabled={ocr.isPending}
          className="rounded-md bg-sky-600/80 hover:bg-sky-600 disabled:opacity-40 px-4 py-2 text-sm text-white transition-colors">
          {ocr.isPending ? `識別中（${ocrCount} 張）…` : '上傳文字記錄截圖'}
        </button>
        <input ref={fileRef} type="file" accept="image/*" multiple hidden onChange={onPickImages} />
      </div>
      <label className="block text-xs text-slate-400 mt-3">字幕 / 正文全文（<span className={content.trim().length >= 100 ? 'text-emerald-400' : 'text-amber-400'}>{content.trim().length} 字</span>，需 ≥100 字——字幕級證據門檻）
        <textarea value={content} onChange={e => setContent(e.target.value)} rows={6}
          placeholder="在此粘貼 YouTube 文字記錄或文章全文……"
          className="mt-1 w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-2 text-sm text-slate-200 font-mono" />
      </label>
      <div className="flex items-center gap-3 mt-3 flex-wrap">
        <button onClick={() => submit.mutate({ expertName: finalExpert, title: title.trim(), url: url.trim() || undefined, date, content: content.trim() })}
          disabled={!canSubmit}
          className="px-4 py-2 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-sm hover:bg-emerald-500/30 disabled:opacity-50">
          {submit.isPending || jobId
            ? `Kimi 結構化中…（已用 ${submitAt ? Math.round((Date.now() - submitAt) / 1000) : 0} 秒${job.data?.stage ? `｜${job.data.stage}` : ''}，可隨時離開）`
            : '結構化並入庫'}
        </button>
        {msg && <p className="text-xs text-slate-300">{msg}</p>}
      </div>
      {pollIssue && (
        <div className="mt-2 flex items-center gap-2 flex-wrap rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-2">
          <p className="text-xs text-amber-200 flex-1 min-w-48">{pollIssue}</p>
          <button type="button"
            onClick={() => { setPollIssue(null); setSubmitAt(Date.now()); job.refetch() }}
            className="shrink-0 rounded-md border border-amber-500/50 bg-amber-500/20 text-amber-100 px-3 py-1 text-xs font-semibold hover:bg-amber-500/30">
            🔄 重新查詢
          </button>
        </div>
      )}
    </Card>
  )
}

function DailyUpdate() {
  const [justStarted, setJustStarted] = useState(false)
  // 非阻塞运行：启动后每 5 秒轮询状态，running → success/failed 时停止并刷新快照
  const status = trpc.pipeline.status.useQuery(undefined, { retry: false, refetchInterval: justStarted ? 5000 : 60000 })
  const snapshot = trpc.pipeline.snapshot.useQuery(undefined, { retry: false })
  const runNow = trpc.pipeline.runNow.useMutation({ onSuccess: () => { setJustStarted(true); status.refetch() } })
  useEffect(() => {
    if (justStarted && status.data?.lastStatus && status.data.lastStatus !== 'running') {
      setJustStarted(false)
      snapshot.refetch()
    }
  }, [justStarted, status.data?.lastStatus])
  // 批核後引導：「僅知悉」唔會改持倉/加圖表黃點——要提示用戶去「記錄調倉」
  const [ackedHint, setAckedHint] = useState(false)
  const ack = trpc.pipeline.acknowledge.useMutation({
    onSuccess: () => {
      snapshot.refetch()
      // 無建議可記（suggested 為空）時唔使彈引導
      if ((snapshot.data?.suggested?.length ?? 0) > 0) setAckedHint(true)
    },
  })
  // Phase 18：批核即自動記錄——按批核時所見建議權重一次過記低，調倉記錄/黃點/生效權重/淨值分段即時聯動
  const [approveMsg, setApproveMsg] = useState<{ kind: 'ok' | 'err' | 'info'; text: string } | null>(null)
  // Phase 18.1：建議唔零和時嘅資金來源/去向選擇（正數=要由某 ETF 扣咁多 pp；負數=要加落某 ETF）
  const [funding, setFunding] = useState<number | null>(null)
  const [fundEtf, setFundEtf] = useState('')
  const { holdings: effHoldings, reload: reloadRebalances } = useEffectivePortfolio()
  const approveRec = trpc.pipeline.approveAndRecord.useMutation({
    onSuccess: (r) => {
      if (r.ok && r.recorded && r.record) {
        setAckedHint(false); setFunding(null); setFundEtf('')
        setApproveMsg({ kind: 'ok', text: `✅ 已批核並自動記錄 ${r.record.title} @ ${r.record.date}：${r.record.changes.map(c => `${c.etf} ${c.from}%→${c.to}%`).join('，')}——調倉記錄、總覽圖黃點、生效權重、淨值分段已即時聯動。⚠ 系統只係記錄，永遠唔會幫你落單——請確保你已喺券商按此權重真實執行。` })
        snapshot.refetch()
        reloadRebalances()
      } else if (r.ok) {
        setFunding(null)
        setApproveMsg({ kind: 'info', text: r.reason === 'duplicate-date'
          ? 'ℹ 今日已經有一條調倉記錄——唔會重複記；快照已標記知悉。如需修正請聯絡管理員。'
          : 'ℹ 本輪冇新建議可記（或建議已全部反映喺現行權重）——已標記知悉。' })
        snapshot.refetch()
      } else if (r.reason === 'needs-funding') {
        // 建議唔零和：唔直接報錯，彈資金來源/去向選擇——用戶指明後先真正記錄
        setApproveMsg(null)
        setFunding(r.residualPp ?? 0)
      } else {
        setApproveMsg({ kind: 'err', text: `❌ 自動記錄失敗：${r.error ?? '未知原因'}——快照未標記知悉，橫幅會保留；可以改用下面「记录调仓」手動記低。` })
      }
    },
    onError: (e) => setApproveMsg({ kind: 'err', text: `❌ ${friendlyNetworkError(e.message)}` }),
  })
  const fileSnap = useFileSnapshot()
  const backendDown = status.isError || snapshot.isError
  const snap = snapshot.data ?? (backendDown ? fileSnap : null)
  const brake = snap?.brakeStatus

  return (
    <>
      {backendDown && (
        <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-3 text-xs text-slate-400">
          后端引擎未连接（静态模式）——正在展示随站附带的最新快照文件；「立即运行」与「复核」按钮在后端部署后可用。
        </div>
      )}
      {brake === 'unavailable' && (
        <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-300">
          ⚠ 价格风险刹车层本次未能运行（行情接口不可用）——本轮建议未经价格验证，请勿直接执行。这正是黄金-25%教训要防的静默失效场景，已改为显性警告。
        </div>
      )}
      {brake === 'partial' && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-300">
          ⚠ 价格风险刹车层部分标的校验失败——建议可信度降级，执行前请人工核对持仓回撤。
        </div>
      )}
      {!backendDown && (<>
      <NetCheckCard />
      <ManualViewForm onAdded={() => snapshot.refetch()} />
      <Card title="数据引擎状态" sub="每日 HKT 08:00 自动运行：字幕源可達時抓频道新视频(含完整字幕)；新闻面经 Kimi 联网搜索主题扫描 → LLM结构化 → 分级衰减 → 建议+风险刹车 → 追加前向净值">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <span className="text-slate-300">上次运行：<b className="text-white">{status.data?.lastRunAt ? new Date(status.data.lastRunAt).toLocaleString('zh-HK') : '尚未运行'}</b></span>
          <span className={`px-2 py-0.5 rounded text-xs border ${status.data?.lastStatus === 'success' ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' : 'bg-slate-600/30 text-slate-400 border-slate-600'}`}>{status.data?.lastStatus ?? '—'}</span>
          <button onClick={() => runNow.mutate()} disabled={runNow.isPending || justStarted || status.data?.lastStatus === 'running'}
            className="px-3 py-1.5 rounded-md bg-sky-500/20 text-sky-300 border border-sky-500/40 text-sm hover:bg-sky-500/30 disabled:opacity-50">
            {justStarted || status.data?.lastStatus === 'running' ? '管道后台运行中…（最长12分钟硬超时保护）' : '立即运行更新管道'}
          </button>
        </div>
        {status.data?.lastLog && <pre className="mt-3 text-xs text-slate-400 bg-slate-800/40 rounded-lg p-3 whitespace-pre-wrap max-h-40 overflow-y-auto">{status.data.lastLog}</pre>}
      </Card>
      </>)}

      {snap && (
        <>
          <Card title={`最新自动快照 · ${snap.date}`} sub={`生效组合仍基于 ${snap.lastRebalanceDate} 人工确认的调仓；以下为管道新抓取的观点`}>
            {snap.views.length === 0 ? <p className="text-sm text-slate-400">本轮未发现追踪频道的新视频。</p> : (
              <div className="space-y-3">
                {snap.views.map((v, i) => (
                  <div key={i} className="rounded-lg bg-slate-800/40 p-3">
                    <div className="flex flex-wrap items-center gap-2 text-xs mb-1">
                      <span className="text-sky-300 font-medium">{v.expertName}</span>
                      <span className="text-slate-400">{v.date}</span>
                      <span className="px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">{v.channel}</span>
                      <span className="text-amber-300 ml-auto">衰减权重 {(v.decayWeight * 100).toFixed(0)}%</span>
                      {v.url && <a href={v.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">來源 ↗</a>}
                    </div>
                    <p className="text-sm text-slate-100 font-medium">{v.title}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{v.summary}</p>
                    {v.signals.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {v.signals.map((s, j) => (
                          <span key={j} title={s.note} className={`text-xs px-2 py-0.5 rounded-full border ${s.direction === 'bull' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : s.direction === 'bear' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : 'bg-slate-600/20 text-slate-400 border-slate-600/40'}`}>
                            {s.asset} · {s.direction === 'bull' ? '看好' : s.direction === 'bear' ? '看淡' : '中性'} · 强度{s.strength}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
          <Card id="pending-review" title={snap.acknowledged ? '建议调仓（已复核 ✓）' : '建议调仓（待人工复核，不会自动生效）'} sub={snap.suggestedNote + ' 触发时机：每日香港时间 08:00 自动运行 + 本页手动运行；有建议时全站顶部会出现横幅，配置了 Webhook 还会推送到你的手机。「批核並記錄調倉」會按你批核時所見嘅建議權重自動生成調倉記錄（即時聯動調倉記錄頁/圖表黃點/生效權重/淨值分段）——只係簿記，系統永遠唔會喺券商落單；「僅標記知悉」則唔會記錄。'}>
            {/* Phase 18：有建議就常駐「批核並記錄」——已知悉但未記錄嘅舊建議（acknowledged=true）都可以一撳補記 */}
            {!backendDown && (snap.suggested.length > 0 || !snap.acknowledged) && (
              <div className="mb-3 flex flex-wrap items-center gap-2">
                {snap.suggested.length > 0 && (
                  <button onClick={() => { setApproveMsg(null); approveRec.mutate({}) }} disabled={approveRec.isPending || ack.isPending}
                    className="px-4 py-2 rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-sm font-semibold hover:bg-emerald-500/30 disabled:opacity-50">
                    {approveRec.isPending ? '記錄中…' : `✓ 批核並記錄調倉（按以上 ${snap.suggested.length} 項建議自動記低）`}
                  </button>
                )}
                {!snap.acknowledged && (
                  <button onClick={() => ack.mutate()} disabled={ack.isPending || approveRec.isPending}
                    className="px-3 py-2 rounded-md bg-slate-600/20 text-slate-400 border border-slate-600/50 text-xs hover:bg-slate-600/30 disabled:opacity-50">
                    {ack.isPending ? '標記中…' : snap.suggested.length > 0 ? '僅標記知悉（唔記錄）' : '✓ 我已复核（横幅提醒将关闭）'}
                  </button>
                )}
              </div>
            )}
            {approveMsg && (
              <div className={`mb-3 rounded-lg border px-4 py-3 text-xs leading-relaxed ${approveMsg.kind === 'ok' ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' : approveMsg.kind === 'err' ? 'border-rose-500/40 bg-rose-500/10 text-rose-300' : 'border-sky-500/40 bg-sky-500/10 text-sky-200'}`}>
                {approveMsg.text}
              </div>
            )}
            {/* Phase 18.1：資金來源/去向選擇——建議唔零和時先彈；記錄內容 = 建議 + 呢個安排，全部寫入記錄備註 */}
            {funding !== null && snap.suggested.length > 0 && (
              <div className="mb-3 rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-xs text-amber-200 leading-relaxed">
                <p className="font-semibold mb-1.5">⚠ 呢輪建議淨{funding > 0 ? '加' : '減'}倉 {Math.abs(funding)}pp——引擎建議係方向性 nudge、唔係零和；資金{funding > 0 ? '來源（由邊隻扣）' : '去向（加落邊隻）'}必須你指明，系統唔會替你揀：</p>
                <div className="flex flex-wrap items-center gap-2">
                  <select value={fundEtf} onChange={e => setFundEtf(e.target.value)}
                    className="rounded-md bg-slate-800/60 border border-slate-700 px-2 py-1.5 text-xs text-slate-200">
                    <option value="">選擇 ETF…</option>
                    {effHoldings.filter(h => !snap.suggested.some(c => c.ticker === h.ticker)).map(h => (
                      <option key={h.ticker} value={h.ticker}>{h.ticker}（現 {h.weight}%）</option>
                    ))}
                  </select>
                  {fundEtf && (() => {
                    const cur = effHoldings.find(h => h.ticker === fundEtf)?.weight ?? 0
                    const to = +(cur - funding).toFixed(2) // funding>0 → 扣；funding<0 → 加
                    const valid = to >= 0 && to <= 40
                    return (
                      <>
                        <span className={`tabular-nums ${valid ? 'text-amber-100' : 'text-rose-300'}`}>
                          → 新權重 {to}%{!valid ? '（超出 0-40% 範圍，請揀另一隻）' : ''}
                        </span>
                        <button type="button" disabled={!valid || approveRec.isPending}
                          onClick={() => { setApproveMsg(null); approveRec.mutate({ fundFrom: { etf: fundEtf, to } }) }}
                          className="px-3 py-1.5 rounded bg-amber-500/25 text-amber-100 border border-amber-500/50 hover:bg-amber-500/35 disabled:opacity-40 font-semibold">
                          {approveRec.isPending ? '記錄中…' : '確認資金安排並記錄'}
                        </button>
                      </>
                    )
                  })()}
                  <button type="button" onClick={() => { setFunding(null); setFundEtf('') }}
                    className="px-2.5 py-1.5 rounded bg-slate-600/20 text-slate-400 border border-slate-600/50 hover:bg-slate-600/30">取消</button>
                </div>
                <p className="mt-1.5 text-[10px] text-amber-200/60">記錄內容 = 建議 {snap.suggested.length} 項 + 你呢個資金安排，全部寫進調倉記錄備註，可隨時喺「调仓记录」頁核對。想完全自訂權重，可以用下面「记录调仓」表格。</p>
              </div>
            )}
            {snap.acknowledged && snap.acknowledgedAt && (
              <p className="mb-3 text-xs text-emerald-400">已于 {new Date(snap.acknowledgedAt).toLocaleString('zh-HK')} 复核。</p>
            )}
            {/* 批核後引導：講明批核 ≠ 執行，指引用戶去「記錄調倉」先會令 chart 加黃點 */}
            {ackedHint && (
              <div className="mb-3 rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-xs text-amber-200 leading-relaxed">
                ✅ 已批核（表示你知悉咗建議）。<b>批核唔會改持倉、chart 亦唔會加點</b>——系統永遠唔會幫你落單。你去券商執行之後，撳下面「📝 去記錄調倉」記低實際權重，組合圖表先會加黃點標記、持倉同淨值先會按新權重更新。
                <button type="button"
                  onClick={() => document.getElementById('record-rebalance')?.scrollIntoView({ behavior: 'smooth' })}
                  className="ml-2 px-3 py-1 rounded bg-amber-500/25 text-amber-100 border border-amber-500/50 hover:bg-amber-500/35 active:bg-amber-500/45 whitespace-nowrap">
                  📝 去記錄調倉
                </button>
              </div>
            )}
            {snap.suggested.length === 0 ? <p className="text-sm text-slate-400">本轮无建议变动。</p> : (
              <div className="grid sm:grid-cols-2 gap-2">
                {snap.suggested.map((c, i) => (
                  <div key={i} className="rounded-lg bg-slate-800/40 px-3 py-2.5">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-sky-300">{c.ticker}</span>
                      <span className="tabular-nums text-sm">
                        <span className="text-slate-500">{c.from}%</span><span className="text-slate-500 mx-1">→</span>
                        <span className={c.to > c.from ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>{c.to}%</span>
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{c.reason}</p>
                  </div>
                ))}
              </div>
            )}
            {/* Phase 13：講明「from」嘅基準口径 + 建議屬性 */}
            <p className="text-[10px] text-slate-500 mt-2">基準權重（「由 X%」）= 當前生效持倉（截至 {snap.lastRebalanceDate} 已記錄調倉）；以上僅為建議，需人工复核，不會自動執行。</p>
          </Card>
          {/* 新主題瞭望（2026-10-09）：專家講到組合冇覆蓋嘅主題 → 候選 ETF 篩選 → 試倉提案 */}
          {(snap.watchlist?.length ?? 0) > 0 && (
            <Card title="新主題瞭望（開放視野）" sub="專家觀點涉及組合未覆蓋嘅主題時，系統自動聚合淨分、配對策展候選 ETF（真實代碼，唔准 LLM 發明）、經篩選器驗證分散價值，先至出試倉提案。睇淡主題只觀望（長倉系統唔做空）；全部提案須人工覆核。">
              <div className="space-y-3">
                {snap.watchlist!.map((w, i) => (
                  <div key={i} className="rounded-lg border border-slate-800 bg-slate-800/30 p-3.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-semibold text-slate-100">{w.theme}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full border ${w.direction === 'bull' ? 'text-emerald-300 border-emerald-500/40 bg-emerald-500/10' : w.direction === 'bear' ? 'text-rose-300 border-rose-500/40 bg-rose-500/10' : 'text-slate-400 border-slate-600 bg-slate-700/30'}`}>
                        {w.direction === 'bull' ? '看多' : w.direction === 'bear' ? '看淡' : '分歧'}
                      </span>
                      <span className="text-[10px] text-slate-500">淨分 {w.netScore >= 0 ? '+' : ''}{w.netScore} · {w.signalCount} 條信號 · 最新 {w.latestDate}</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1.5">{w.supporters.join('；')}</p>
                    {w.candidates.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {w.candidates.map(c => (
                          <p key={c.ticker} className="text-xs text-slate-400">
                            <b className="text-sky-300">{c.ticker}</b>
                            <span className={`ml-1.5 text-[10px] ${c.tier === 'diversifier' ? 'text-emerald-400' : c.tier === 'substitute' ? 'text-sky-300' : c.tier === 'avoid' ? 'text-rose-400' : 'text-slate-500'}`}>
                              [{c.tier === 'diversifier' ? '分散器' : c.tier === 'substitute' ? '替代式' : c.tier === 'avoid' ? '唔建議' : c.tier === 'limited' ? '有限價值' : c.tier}]
                            </span>
                            <span className="ml-1.5">{c.headline}</span>
                          </p>
                        ))}
                      </div>
                    )}
                    {w.candidates.length === 0 && w.direction === 'bull' && (
                      <p className="text-[11px] text-slate-600 mt-1.5">暫無策展候選工具——如需研究，請去「組合配置」頁下方嘅候選篩選器手動輸入代碼。</p>
                    )}
                    {w.proposal && (
                      <p className="text-xs text-teal-300 mt-2 border-t border-slate-700/60 pt-2">💡 {w.proposal}</p>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}
          {/* 批核後引導 banner 嘅滾動目標（RebalanceLog 頁嗰份唔加 id，避免重複） */}
          <div id="record-rebalance" className="scroll-mt-20">
            <RecordRebalance suggested={snap.suggested} onRecorded={() => snapshot.refetch()} />
          </div>
        </>
      )}
      {!snap && !snapshot.isLoading && <p className="text-sm text-slate-400">数据库中还没有快照，点击「立即运行更新管道」生成第一份。</p>}
    </>
  )
}

function RebalanceLog() {
  const { records } = useEffectivePortfolio()
  // Phase 15：靜態歷史（打包時）+ runtime 記錄（用戶真實執行後記低）合併，按日期倒序
  const all = [
    ...REBALANCES.map(r => ({ ...r, live: false as const, recordedAt: null as string | null })),
    ...records.map(r => ({ date: r.date, title: r.title, trigger: r.trigger, changes: r.changes, note: r.note, live: true as const, recordedAt: r.recordedAt })),
  ].sort((a, b) => b.date.localeCompare(a.date))
  return (
    <div className="space-y-4">
      <RecordRebalance />
      {all.map((r, i) => (
        <Card key={`${r.date}-${r.title}`} title={`${r.date} · ${r.title}${r.live ? ' · 即時記錄 ✓' : ''}`} sub={r.trigger}>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2 mb-3">
            {r.changes.map(c => (
              <div key={c.etf} className="flex items-center justify-between rounded-lg bg-slate-800/40 px-3 py-2 text-sm">
                <span className="text-slate-300 font-medium">{c.etf}</span>
                <span className="tabular-nums">
                  <span className="text-slate-500">{c.from}%</span>
                  <span className="text-slate-500 mx-1">→</span>
                  <span className={c.to > c.from ? 'text-emerald-400 font-semibold' : c.to < c.from ? 'text-rose-400 font-semibold' : 'text-slate-300'}>{c.to}%</span>
                </span>
              </div>
            ))}
          </div>
          <p className="text-xs text-amber-300/90">{r.note}</p>
          {r.live && r.recordedAt && <p className="text-[10px] text-slate-500 mt-1">記錄於 {new Date(r.recordedAt).toLocaleString('zh-HK')}</p>}
          {i === 0 && <p className="text-xs text-slate-500 mt-1">{r.live
            ? '此調倉已即時反映於「组合配置」生效權重、總覽表現圖黃點，及淨值序列分段計算（調倉日收市執行，下一交易日起用新權重）。'
            : `此调仓已直接反映于「组合配置」当前权重，并在表现图以${(r.title.match(/#\s*(\d+)/) ? `调仓#${r.title.match(/#\s*(\d+)/)![1]}` : r.title.slice(0, 8))}标记。`}</p>}
        </Card>
      ))}
    </div>
  )
}

// ---- Phase 15：記錄調倉表單 ----
// 用戶喺券商真實執行調倉之後，喺度記低 → 服務端校驗（Σ=100、ticker 白名單、唔准未來/重複日期）
// → 寫入 public/data/rebalances.json → 圖表黃點、生效權重、淨值分段、建議引擎全部即時聯動。
// 鐵律：呢個動作只係「記錄」，系統永遠唔會幫用戶落單。
function RecordRebalance({ suggested, onRecorded }: { suggested?: { ticker: string; from: number; to: number }[]; onRecorded?: () => void }) {
  const { holdings, reload } = useEffectivePortfolio()
  const statusQ = trpc.pipeline.status.useQuery(undefined, { retry: false })
  const backendDown = statusQ.isError
  const today = new Date().toLocaleDateString('sv-SE') // YYYY-MM-DD（本地時區）
  const [date, setDate] = useState(today)
  const [rows, setRows] = useState<{ etf: string; to: string }[]>([{ etf: '', to: '' }])
  const [note, setNote] = useState('')
  const [done, setDone] = useState<string | null>(null)
  const mut = trpc.pipeline.recordRebalance.useMutation({
    onSuccess: r => {
      if (r.ok) {
        setDone(`✓ 已記錄 ${r.record?.date} ${r.record?.title}——圖表黃點、生效權重、淨值分段已即時聯動。`)
        setRows([{ etf: '', to: '' }]); setNote('')
        reload(); onRecorded?.()
      }
    },
  })
  const curW = (t: string) => holdings.find(h => h.ticker === t)?.weight ?? 0
  // 即時預覽：調後總和必須 = 100（同服務端校驗同一規則）
  const filled = rows.filter(r => r.etf && r.to.trim() !== '' && isFinite(parseFloat(r.to)))
  const afterSum = useMemo(() => {
    const w = Object.fromEntries(holdings.map(h => [h.ticker, h.weight]))
    for (const r of filled) w[r.etf] = parseFloat(r.to)
    return Object.values(w).reduce((s, v) => s + v, 0)
  }, [holdings, rows])
  const sumOk = Math.abs(afterSum - 100) < 1e-9
  const serverErr = mut.data && !mut.data.ok ? mut.data.error : (mut.isError ? '伺服器錯誤，請稍後再試' : null)
  const canSubmit = !backendDown && !mut.isPending && filled.length > 0 && sumOk && /^\d{4}-\d{2}-\d{2}$/.test(date)

  return (
    <Card title="记录调仓（执行后即时同步全站）"
      sub="喺券商真實執行調倉之後喺度記低：總覽表現圖會即刻出現黃點標記、「组合配置」權重即時更新、淨值由下一交易日起按新權重分段計算、建議引擎按新權重重算。⚠ 此動作只係記錄——系統永遠唔會幫你落單。">
      {backendDown && (
        <p className="text-xs text-slate-500 mb-3">后端引擎未连接（静态模式）——記錄功能喺後端部署後可用；而家可以睇到表單預覽。</p>
      )}
      <div className="space-y-2.5">
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <label className="text-xs text-slate-400">執行日期（收市價生效，下一交易日起用新權重）</label>
          <input type="date" value={date} max={today} onChange={e => setDate(e.target.value)}
            className="rounded-md bg-slate-800/60 border border-slate-700 px-2 py-1 text-sm text-slate-200" />
          {suggested && suggested.length > 0 && (
            <button type="button" onClick={() => setRows(suggested.map(c => ({ etf: c.ticker, to: String(c.to) })))}
              className="text-xs px-2.5 py-1 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-500/25">
              用待复核建议预填（{suggested.length} 项）
            </button>
          )}
        </div>
        {rows.map((r, i) => (
          <div key={i} className="flex flex-wrap items-center gap-2">
            <select value={r.etf} onChange={e => setRows(rows.map((x, j) => j === i ? { ...x, etf: e.target.value } : x))}
              className="rounded-md bg-slate-800/60 border border-slate-700 px-2 py-1 text-sm text-slate-200 w-36">
              <option value="">選擇 ETF…</option>
              {holdings.map(h => <option key={h.ticker} value={h.ticker}>{h.ticker}（現 {h.weight}%）</option>)}
            </select>
            <span className="text-xs text-slate-500 tabular-nums">{r.etf ? `${curW(r.etf)}% →` : '—'}</span>
            <input type="number" min={0} max={40} step={0.5} placeholder="新權重 %" value={r.to}
              onChange={e => setRows(rows.map((x, j) => j === i ? { ...x, to: e.target.value } : x))}
              className="rounded-md bg-slate-800/60 border border-slate-700 px-2 py-1 text-sm text-slate-200 w-24 tabular-nums" />
            <span className="text-xs text-slate-500">%</span>
            {r.etf && r.to.trim() !== '' && isFinite(parseFloat(r.to)) && (
              <span className={`text-xs tabular-nums ${parseFloat(r.to) > curW(r.etf) ? 'text-emerald-400' : parseFloat(r.to) < curW(r.etf) ? 'text-rose-400' : 'text-slate-500'}`}>
                {parseFloat(r.to) > curW(r.etf) ? `+${(parseFloat(r.to) - curW(r.etf)).toFixed(2)}pp` : parseFloat(r.to) < curW(r.etf) ? `${(parseFloat(r.to) - curW(r.etf)).toFixed(2)}pp` : '無變動'}
              </span>
            )}
            {rows.length > 1 && (
              <button type="button" onClick={() => setRows(rows.filter((_, j) => j !== i))}
                className="text-xs text-slate-500 hover:text-rose-400 px-1">✕</button>
            )}
          </div>
        ))}
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" onClick={() => setRows([...rows, { etf: '', to: '' }])}
            className="text-xs px-2.5 py-1 rounded bg-slate-700/40 text-slate-300 border border-slate-600 hover:bg-slate-700/60">+ 加一行</button>
          <span className={`text-xs font-semibold tabular-nums ${sumOk ? 'text-emerald-400' : 'text-rose-400'}`}>
            調後總和 {afterSum.toFixed(2)}% {sumOk ? '✓ =100' : '（必須 =100）'}
          </span>
        </div>
        <input type="text" value={note} onChange={e => setNote(e.target.value)} maxLength={500}
          placeholder="備註（可選）：例如券商成交編號、執行理由…"
          className="w-full rounded-md bg-slate-800/60 border border-slate-700 px-3 py-1.5 text-sm text-slate-200" />
        {serverErr && <p className="text-xs text-rose-400">✕ {serverErr}</p>}
        {done && <p className="text-xs text-emerald-400">{done}</p>}
        <button type="button" disabled={!canSubmit}
          onClick={() => { setDone(null); mut.mutate({ date, note: note || undefined, changes: filled.map(r => ({ etf: r.etf, to: parseFloat(r.to) })) }) }}
          className="px-4 py-2 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 text-sm font-semibold hover:bg-amber-500/30 disabled:opacity-40 disabled:cursor-not-allowed">
          {mut.isPending ? '記錄中…' : '📝 記錄此調倉（唔會落單）'}
        </button>
      </div>
    </Card>
  )
}

function Experts() {
  // 即時管道觀點：snapshot.views 是每日更新的真實抓取（字幕級證據），按專家名合併到對應卡片頂部
  const snapQ = trpc.pipeline.snapshot.useQuery(undefined, { retry: false, refetchInterval: 5 * 60000 })
  // Phase 13 降級態：後端未連接時回退隨站快照文件；兩者都冇 → 顯性「暫無數據」
  const fileSnap = useFileSnapshot()
  const liveViews: any[] = ((snapQ.data as any) ?? (snapQ.isError ? fileSnap : null))?.views ?? []
  const matchLive = (name: string) => liveViews.filter(v => {
    const n = v.expertName || ''
    return n.includes(name) || name.includes(n)
  }).sort((a, b) => (b.date || '').localeCompare(a.date || ''))
  const liveTotal = liveViews.length
  const liveLatest = liveViews.reduce((m, v) => (v.date > m ? v.date : m), '')
  return (
    <div className="space-y-4">
      <div className={`rounded-xl border p-4 ${liveTotal ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-slate-800 bg-[#0f1729]'}`}>
        <p className="text-sm text-slate-200">
          {liveTotal
            ? <>✅ 管道即時觀點庫：<b className="text-emerald-300">{liveTotal} 條</b>字幕級證據觀點已入庫（最新 {liveLatest}），按專家合併顯示於下方各卡頂部（綠框）。下方舊版靜態檔案保留作歷史對照。</>
            : snapQ.isLoading ? '正在讀取管道快照…'
            // Phase 13：區分「後端離線但文件快照有數據（空庫）」同「兩者皆無」兩種降級
            : snapQ.isError && !fileSnap ? '⚠ 暫無數據，等待下次掃描——後端未連接且無隨站快照文件；部署後管道每日 HKT 09:00 自動掃描。'
            : '⚠ 管道快照暫無數據，等待下次掃描——請到「每日更新」頁運行管道或手動錄入。'}
        </p>
      </div>
    <div className="grid lg:grid-cols-2 gap-4">
      {EXPERTS.map(e => { const live = matchLive(e.name); return (
        <section key={e.id} className={`rounded-xl border p-5 ${e.active ? 'border-slate-800 bg-[#0f1729]' : 'border-slate-800/60 bg-[#0f1729]/50 opacity-80'}`}>
          <div className="flex items-start justify-between gap-3 mb-3">
            <div>
              <h3 className="text-white font-semibold">{e.name}</h3>
              <p className="text-xs text-slate-400">{e.role}</p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className={`text-xs px-2 py-1 rounded border whitespace-nowrap ${e.active ? 'bg-sky-500/10 text-sky-300 border-sky-500/30' : 'bg-slate-700/30 text-slate-400 border-slate-700'}`}>
                动态权重 {e.weightInPortfolio}%
              </span>
              {/* Phase 13：靜態 hitRate 係人工復盤口径（2026-05~06，樣本≤8），同「復盤驗證」頁動態回測命中率唔同口径，必須標明避免混淆 */}
              <span title="人工復盤口径（2026-05~06）· 樣本極小（≤8 條），僅供參考；動態回測命中率見「復盤驗證」頁"
                className={`text-[10px] px-1.5 py-0.5 rounded ${e.hitRate == null ? 'text-slate-500' : e.hitRate >= 0.8 ? 'text-emerald-400' : e.hitRate >= 0.5 ? 'text-amber-300' : 'text-rose-400'}`}>
                {e.hitRate == null ? '样本不足' : `命中率 ${(e.hitRate * 100).toFixed(0)}%`}
                <span className="block text-[9px] text-slate-500">人工復盤 · 樣本≤8</span>
              </span>
            </div>
          </div>
          {!e.active && <p className="text-xs text-amber-300/80 mb-2">{e.inactiveNote}</p>}
          <div className="space-y-3">
            {live.map((v: any, i: number) => (
              <div key={`live-${i}`} className="rounded-lg bg-emerald-500/5 border border-emerald-500/30 p-3">
                <div className="flex flex-wrap items-center gap-2 text-xs mb-1.5">
                  <span className="text-emerald-300 font-medium">{v.date}</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">{v.channel || '管道'}</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-200 text-[10px]">即時入庫</span>
                  {v.url && <a href={v.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline ml-auto">来源 ↗</a>}
                </div>
                <p className="text-sm text-slate-100 font-medium">{v.title}</p>
                <p className="text-xs text-slate-400 mt-1">{v.summary}</p>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {(v.signals || []).map((s: any, j: number) => (
                    <span key={j} title={s.note} className={`text-xs px-2 py-0.5 rounded-full border ${s.direction === 'bull' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : s.direction === 'bear' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : 'bg-slate-600/20 text-slate-400 border-slate-600/40'}`}>
                      {s.asset} · {s.direction === 'bull' ? '看好' : s.direction === 'bear' ? '看淡' : '中性'} {s.strength ? `· 强度${s.strength}` : ''}
                    </span>
                  ))}
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-[10px] text-slate-500">时间衰减权重</span>
                  <div className="flex-1 h-1.5 rounded bg-slate-700/60 overflow-hidden">
                    <div className="h-full bg-emerald-400/80" style={{ width: `${Math.round((v.decayWeight ?? 0) * 100)}%` }} />
                  </div>
                  <span className="text-[10px] text-emerald-300 tabular-nums">{((v.decayWeight ?? 0) * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
            {e.views.map((v, i) => {
              const w = decay(v.date)
              return (
                <div key={i} className="rounded-lg bg-slate-800/40 p-3">
                  <div className="flex flex-wrap items-center gap-2 text-xs mb-1.5">
                    <span className="text-slate-300 font-medium">{v.date}</span>
                    <span className="px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">{v.channel}</span>
                    <a href={v.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline ml-auto">来源 ↗</a>
                  </div>
                  <p className="text-sm text-slate-100 font-medium">{v.title}</p>
                  <p className="text-xs text-slate-400 mt-1">{v.summary}</p>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {v.stance.map((s, j) => (
                      <span key={j} title={s.note} className={`text-xs px-2 py-0.5 rounded-full border ${s.dir === 'bull' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : s.dir === 'bear' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : 'bg-slate-600/20 text-slate-400 border-slate-600/40'}`}>
                        {s.asset} · {s.dir === 'bull' ? '看好' : s.dir === 'bear' ? '看淡' : '中性'}
                      </span>
                    ))}
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[10px] text-slate-500">时间衰减权重</span>
                    <div className="flex-1 h-1.5 rounded bg-slate-700/60 overflow-hidden">
                      <div className="h-full bg-amber-400/80" style={{ width: `${Math.round(w * 100)}%` }} />
                    </div>
                    <span className="text-[10px] text-amber-300 tabular-nums">{(w * 100).toFixed(0)}%</span>
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      ); })}
    </div>
    </div>
  )
}

function Review() {
  const cls = { 命中: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40', 部分命中: 'bg-amber-500/15 text-amber-300 border-amber-500/40', 未兑现: 'bg-rose-500/15 text-rose-300 border-rose-500/40', 观察中: 'bg-sky-500/15 text-sky-300 border-sky-500/40' } as const
  // Phase 13：總復盤數字改用淨值序列即時重算（與總覽同口径），唔再寫死
  const perf = usePerformance()
  const S = perf.stats
  const fmtOr = (v: number | null | undefined, d = 2) => v == null || !isFinite(v) ? '—' : pct(v, d)
  return (
    <div className="space-y-4">
    <SignalBacktestCard />
    <LearningCard />
    {/* Phase 13 誠實文案：後端冇「按命中率自動降權」機制——復盤係人工校準動態權重；真實機制係冷卻期避免重複計算 */}
    <Card title="观点复盘：是否仍匹配当前市场" sub="对照市场快照逐条人工验证；复盘结论用于人工校准各专家动态权重（见方法论，非自动）；量化引擎另设 S10 冷却机制，共识信号设冷却期，避免重复计算同一观点">
      <div className="space-y-3">
        {REVIEWS.map((r, i) => (
          <div key={i} className="rounded-lg bg-slate-800/40 p-4">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-white font-medium text-sm">{r.expert}</span>
              <span className="text-xs text-slate-500">{r.date}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full border ${cls[r.verdict]}`}>{r.verdict}</span>
            </div>
            <div className="grid md:grid-cols-2 gap-3 text-xs">
              <div><p className="text-slate-500 mb-0.5">当时观点</p><p className="text-slate-300">{r.view}</p></div>
              <div><p className="text-slate-500 mb-0.5">市场实际</p><p className="text-slate-300">{r.reality}</p></div>
            </div>
            <p className="text-xs text-amber-300/90 mt-2">对组合影响：{r.impact}</p>
          </div>
        ))}
        <div className="rounded-lg border border-sky-500/30 bg-sky-500/5 p-4">
          {/* Phase 13：回报/回撤改為 usePerformance 動態值（淨值序列即時重算），唔再寫死 +8.09/+5.34/-8.17 */}
          <p className="text-sm text-sky-300 font-medium mb-1">★ 真实行情总复盘（Yahoo Finance 复权价，2026-01-20 → {perf.asOf}）</p>
          <p className="text-xs text-slate-300">组合 <b className="text-emerald-400">{fmtOr(S.portRet)}</b> vs 基准 <b>{fmtOr(S.benchRet)}</b>；最大回撤 {fmtOr(S.maxDD)} vs {fmtOr(S.benchMaxDD)}。<b className="text-emerald-400">赚在哪里</b>：蔡金強韩台（EWY +56.7%、EWT +50.0%）+ HALO能源（XLE +26.5%）+ Timmer半导体（SMH +48.6%）。<b className="text-rose-400">亏在哪里</b>：洪灝黄金长牛（GLD -15%、SLV -39%）是最大拖累（约-3pp），比特币（IBIT -27.8%）小仓位试错（-0.4pp），MCHI离岸中国（-12.9%）。<b className="text-amber-300">结论</b>：信号引擎在股票类观点上命中率高，在单边商品叙事上曾缺乏刹车——<b className="text-white">「价格风险刹车层」现已上线</b>：持仓自60日峰值回撤超15%且30天无新看多信号 → 强制降权建议；配合信号冷却期避免重复计算同一观点。刹车失效时会显性警告（见「每日更新」页）；所有调仓建议仍需人工复核，不会自动执行。</p>
          <p className="text-[10px] text-slate-500 mt-1.5">以上回报/回撤截至净值序列最新日期（{perf.asOf}），此后因实时行情未更新而冻结。</p>
        </div>
      </div>
    </Card>
    </div>
  )
}

function Methodology() {
  return (
    <div className="space-y-4">
      <Card title="信号合成流程（观点 → 组合）v2 · 对标顶级量化实践">
        <ol className="text-sm text-slate-300 space-y-2 list-decimal list-inside">
          <li><b className="text-white">多渠道采集 + 视频内容阅读</b>：YouTube 视频以完整字幕/官方转录为输入（例：Timmer 7/6 一集按字幕拆出8条独立信号），辅以官方简介、报章专栏原文；每条观点记录日期、渠道、链接。</li>
          <li><b className="text-white">时间性核验</b>：交叉核对内容内时间锚点（曾成功纠错：洪灝「形势严峻」片实为2025年3月而非近期）。超过90天权重=0。</li>
          <li><b className="text-white">分级信息半衰期</b>（对标 Alpha Architect 信息衰减研究：宏观/价值信号衰减慢、动量/事件信号衰减快）：宏观/年度级 45天 · 行业/主题级 21天 · 事件/短线级 7天，w = 0.5^（天数/半衰期）。</li>
          <li><b className="text-white">信号标准化 + 适配度校验</b>：拆解为「资产×方向×强度」；工具必须能精确表达信号才执行（杜绝「看好小盘股却加仓标普500」式错配）。</li>
          <li><b className="text-white">共识矩阵 + 冲突对冲</b>：跨专家汇总净共识分；多空并读取净值并降低变动幅度。</li>
          <li><b className="text-white">专家动态权重（TipRanks 式命中率加权 + 贝叶斯收缩）</b>：按复盘命中率调整（蔡金強 100%→25%、洪灝 0%→14%）；因样本仅半年，权重向均值收缩（w×(0.7+0.6×命中率)）防止小样本过拟合——学术研究表明专家超额收益持续性弱，命中率仅供参考不设为零。</li>
          <li><b className="text-white">价格验证层 · 风险刹车</b>：观点必须与价格交叉验证——持仓自60日峰值回撤超15%且30天无新看多信号 → 强制降权建议（源自真实教训：金价自峰值-25%、白银-50%期间无刹车，拖累组合约3pp）。</li>
          {/* Phase 13 口径統一：與「回测口径」卡一致——淨值計及 ETF 費率，交易成本係另列嘅估算口径 */}
          <li><b className="text-white">成本意识</b>：净值序列基于真实复权价（已内含各 ETF 自身费率，包括 IBIT 较高费率）；交易佣金/滑点未计入净值，另以估算口径单列（单边10bps×换手125%=拖累0.12%，即总览「含交易成本净」回报）；调仓频率刻意压低（半年仅4次），因信号属月度级视野，高频调仓只会被成本吞噬。</li>
        </ol>
      </Card>
      <Card title="回测的诚实边界（学界最佳实践对照）">
        <ul className="text-sm text-slate-300 space-y-2 list-disc list-inside">
          <li><b className="text-white">样本内局限</b>：当前回测是「规则重放」——权重由已知观点事后设定，存在后见之明；学术研究（Alpha Architect 等）反复证明：无论是基金经理还是专家观点，历史超额收益对未来的预测力都很弱。</li>
          <li><b className="text-white">样本外承诺</b>：自 2026-07-20 起权重规则冻结，之后的表现才是真正的实时验证（walk-forward）；每日更新面板将持续记录。</li>
          <li><b className="text-white">风险对等原则</b>：组合 Sharpe 0.69 vs 基准 0.64（截至 2026-07-23 回测口径；最新数值以「总览」实时重算为准）——评估信号质量应看风险调整后收益而非毛回报；若想要与基准同等波动，可将组合整体仓位按 10.8/18.4 ≈ 59% 缩放，其余放 SGOV。</li>
          <li><b className="text-white">策略退役条件</b>：若前向追踪出现 ①滚动3个月跑输基准超5pp ②实际回撤超回测最大回撤1.5倍（≈-12%）③信号引擎连续2次调仓后均被证伪——任一触发即应停用本策略并全面复盘。</li>
        </ul>
      </Card>
      <Card title="自动化管线（后端 cron 已上线）">
        {/* Phase 13 誠實文案：後端已有 cron pipeline，唔再係「需後端服務」嘅未來式 */}
        <p className="text-sm text-slate-300">后端已内置 cron pipeline：<b className="text-white">每日 HKT 09:00 自动扫描</b>——字幕源可达时经 YouTube Data API 拉取 @octalk999（蔡金強）、@SunChannelHK（譚新強世界ZOOM）、etnet、新城财经台、Fidelity 频道新视频 → 抓取字幕转录 → <b className="text-white">LLM（Kimi API）</b> 结构化为信号并做时间性核验 → <b className="text-white">News API + Brave Search</b> 补全网来源 → 衰减引擎 + 共识矩阵 → 生成调仓建议（仅建议，需人工复核）、写入表现追踪。<b className="text-white">运行失败会记录日志</b>并于「每日更新」页显性显示上次状态；亦可于该页手动触发。密钥只存服务端环境变量，绝不写入网页代码。</p>
      </Card>
      <Card title="回测口径（真实数据）">
        {/* Phase 13 口径統一：舊版「未計入交易費用」同方法論「回測含交易成本」矛盾——統一為：淨值計及 ETF 自身費率，未計交易佣金/滑點（交易成本另以淨回報口径列示） */}
        <p className="text-sm text-slate-300">回测区间 2026-01-20 至 2026-07-23，<b className="text-white">全部为 Yahoo Finance 真实复权日线价格</b>（19只持仓ETF + ACWI/AGG基准），逐日按四次调仓权重路径滚动计算组合净值。基准 = 60% ACWI + 40% AGG。净值序列基于真实复权价，<b className="text-white">已计及各 ETF 自身费率</b>（含 IBIT 较高费率，复权价已内含）；<b className="text-white">未计交易佣金、买卖滑点</b>、港元/美元汇率、股息税——交易成本另以估算口径单列（单边10bps × 总换手125% ≈ 拖累0.12%，见总览「回报（含交易成本净）」）。真实跟投时收益会略低于回测值，且滑点在SMH/EWY等高波动品种上更明显。</p>
      </Card>
    </div>
  )
}

// ---- 信號命中率回測：多窗口階梯（5/15/45/90 交易日）× ACWI 超額命中（2026-09-11 Phase 12 升級）----
// Phase 13：Wilson score interval 下界——小樣本命中率會嚴重高估，對標 TipRanks 嘅誠實披露
function wilsonLower(hits: number, n: number, z = 1.96): number {
  if (n <= 0) return 0
  const p = hits / n
  const den = 1 + z * z / n
  const centre = p + z * z / (2 * n)
  const margin = z * Math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
  return Math.max(0, ((centre - margin) / den) * 100)
}
// ---- 專家學習環卡（P0，2026-09-12）：滾動命中率 → 因子自動調整提案 + 跑輸診斷 ----
// 邊界（與後端 contracts/learner.ts 同口徑）：只調權重、夾 [0.5,1.5]、週步幅 ≤0.1、樣本不足減半、永不自動執行調倉
function LearningCard() {
  const lr = trpc.learning.report.useQuery(undefined, { staleTime: 3600_000, retry: 1 })
  const d = lr.data
  if (lr.isLoading) return <Card title="專家學習環（自動權重校準 + 跑輸診斷）" sub="計算中——正在聚合滾動命中率與組合歸因…"><p className="text-xs text-slate-500">載入中…</p></Card>
  if (!d) return null
  const verdictMeta: Record<string, { label: string; cls: string }> = {
    none: { label: '未觸發（未跑輸逾 3pp）', cls: 'text-slate-400 border-slate-700 bg-slate-800/40' },
    individual: { label: '個別專家問題', cls: 'text-amber-300 border-amber-500/40 bg-amber-500/10' },
    systemic: { label: '系統性失效（專家群體）', cls: 'text-rose-300 border-rose-500/40 bg-rose-500/10' },
    market: { label: '大市環境主導（非專家錯）', cls: 'text-sky-300 border-sky-500/40 bg-sky-500/10' },
  }
  const vm = verdictMeta[d.diagnosis.verdict] ?? verdictMeta.none
  const changed = d.proposals.filter(p => p.next !== p.prev)
  return (
    <Card title="專家學習環（P0）：滾動命中率 → 因子自動校準 + 跑輸診斷"
      sub="信號回測（15 日窗）驅動專家因子每週微調——夾 [0.5,1.5]、單次 ±0.1、樣本 &lt;10 減半；跑輸大盤 &gt;3pp 時自動分辯「個別專家錯 / 專家全錯 / 大市環境」。因子即時生效於 M4 加權；調倉建議仍需人工覆核，學習永不自動落單。">
      {/* 診斷行 */}
      <div className="flex flex-wrap items-center gap-2 mb-3 text-xs">
        <span className={`px-2.5 py-1 rounded border ${vm.cls}`}>診斷：{vm.label}</span>
        <span className="text-slate-500">20 日超額：<b className={d.diagnosis.excess20dPp != null && d.diagnosis.excess20dPp < 0 ? 'text-rose-400' : 'text-emerald-400'}>{d.diagnosis.excess20dPp != null ? `${d.diagnosis.excess20dPp >= 0 ? '+' : ''}${d.diagnosis.excess20dPp}pp` : '—'}</b></span>
        <span className="text-slate-500">市場解釋力 R²：<b className="text-slate-300">{d.diagnosis.marketRSq != null ? d.diagnosis.marketRSq : '—'}</b></span>
        <span className="text-slate-600 ml-auto">因子來源：{d.factorsSource === 'learning' ? '學習環（動態）' : d.factorsSource === 'static' ? '靜態表' : '無'}</span>
      </div>
      <p className="text-xs text-slate-400 mb-3">{d.diagnosis.detail}</p>
      {/* 因子提案表 */}
      {d.proposals.length === 0 ? (
        <p className="text-xs text-slate-500">暫無已到期信號可學習——前向數據累積中（45/90 日窗約 10-11 月先有意義）。</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead><tr className="text-left text-slate-500 border-b border-slate-800">
              <th className="py-1.5 pr-3">專家</th><th className="pr-3 text-right">主窗命中率</th><th className="pr-3 text-right">樣本</th>
              <th className="pr-3 text-right">因子</th><th className="text-left">依據</th>
            </tr></thead>
            <tbody>
              {d.proposals.map(p => (
                <tr key={p.expertId} className="border-b border-slate-800/50">
                  <td className="py-1.5 pr-3 font-medium text-slate-200">{p.expertId}</td>
                  <td className="pr-3 text-right tabular-nums">{p.hitRate != null ? `${p.hitRate}%` : '—'}</td>
                  <td className="pr-3 text-right tabular-nums text-slate-500">{p.decided}</td>
                  <td className={`pr-3 text-right tabular-nums font-bold ${p.next > p.prev ? 'text-emerald-400' : p.next < p.prev ? 'text-rose-400' : 'text-slate-400'}`}>
                    {p.prev} → {p.next}
                  </td>
                  <td className="text-slate-500">{p.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="text-[10px] text-slate-600 mt-3">{d.note}</p>
      {changed.length > 0 && <p className="text-[10px] text-teal-400/80 mt-1">本輪有 {changed.length} 位因子調整已寫入學習快照（append-only 留賬，可審計）。</p>}
    </Card>
  )
}

function SignalBacktestCard() {
  const bt = trpc.pipeline.signalBacktest.useQuery(undefined, { staleTime: 3600_000, retry: 1 })
  const d = bt.data
  if (bt.isLoading) return <Card title="信號命中率回測（真實價格驗證 · 多窗口）" sub="計算中——正在對每條信號拉取四個前瞻窗口嘅行情…"><p className="text-xs text-slate-500">載入中…</p></Card>
  if (!d) return null
  // Phase 13：後端同步加緊嘅 acwiMissing 欄——用可選讀取，唔假設一定存在
  const acwiMissing = (d as unknown as Record<string, unknown>).acwiMissing === true
  const dirCount = { bull: 0, bear: 0, neutral: 0 }
  for (const r of d.rows) if (r.direction in dirCount) dirCount[r.direction as keyof typeof dirCount]++
  const rateCls = (r: number | null) => r == null ? 'text-slate-500' : r >= 55 ? 'text-emerald-400' : r >= 45 ? 'text-amber-300' : 'text-rose-400'
  const xsCls = (x: number | null) => x == null ? 'text-slate-600' : x > 0 ? 'text-emerald-400' : x < 0 ? 'text-rose-400' : 'text-slate-400'
  return (
    <Card title="信號命中率回測（真實價格驗證 · 多窗口階梯）"
      sub="每條信號由發布日起，喺 5/15/45/90 個交易日四個窗口逐格驗證；命中以「超額收益」判定——ETF 窗口收益 − 同期 ACWI 收益：看多 >+0.5pp / 看空 <−0.5pp / 中性 |超額|≤2pp（剔除大市順風，先係專家淨實力）。未到期嘅窗口標「—」，唔當命中亦唔當證偽。前向、樣本外檢驗，非回測重放。">
      {acwiMissing && (
        <p className="text-xs text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2 mb-3">
          ⚠ 基準 ACWI 數據缺失，本期無法計算超額收益——命中率暫以 ETF 自身收益方向判定，解讀請留意。
        </p>
      )}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
        {d.byWindow.map(w => (
          <div key={w.window} className="rounded-lg border border-slate-800 bg-slate-800/40 p-3">
            <div className="flex items-baseline justify-between">
              <span className="text-xs text-slate-400">{w.window} 交易日</span>
              <span className="text-[10px] text-slate-600">{w.pending > 0 ? `${w.pending} 條未到期` : '全部到期'}</span>
            </div>
            {w.decided === 0 ? (
              <p className="text-xs text-slate-500 mt-1.5">未到期——觀點庫最舊信號仲未夠 {w.window} 個交易日</p>
            ) : (
              <>
                <div className={`text-xl font-bold tabular-nums mt-1 ${rateCls(w.hitRate)}`}>
                  {w.hitRate == null ? '—' : `${w.hitRate}%`}
                  <span className="text-[10px] font-normal text-slate-500 ml-1">（{w.hits}/{w.decided}）</span>
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5">
                  方向信號平均簽名超額：<b className={xsCls(w.avgExcessDirPct)}>{w.avgExcessDirPct == null ? '—' : `${w.avgExcessDirPct >= 0 ? '+' : ''}${w.avgExcessDirPct}pp`}</b>
                </div>
                {w.insufficient && <div className="text-[10px] text-amber-400/80 mt-0.5">樣本 &lt;10，僅供參考</div>}
              </>
            )}
          </div>
        ))}
      </div>
      <p className="text-[10px] text-slate-500 mb-3">
        點樣讀：短窗（5日）噪音重，長窗（45/90日）先見真章——如果專家真係有 edge，命中率應該隨窗口拉長而企穩；如果只係 5 日窗好彩，長窗會打回原形。方向信號（看多/看空）嘅平均簽名超額先係核心指標：長期 &gt;0 先代表觀點庫有淨價值。截至 {d.asOf}。
      </p>
      {d.byExpert.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-1">
          {d.byExpert.map(e => (
            <span key={e.expert} title={e.avgExcessDirPct == null ? undefined : `平均簽名超額 ${e.avgExcessDirPct >= 0 ? '+' : ''}${e.avgExcessDirPct}pp（15 交易日窗）`}
              className="text-xs rounded-full border border-slate-700 bg-slate-800/60 px-2.5 py-1 text-slate-300">
              {/* Phase 13：n<10 唔顯示命中率數字（小樣本誤導）；n≥10 先顯示，並附 Wilson 95% 下界 */}
              {e.expert}：{e.decided < 10 ? <span className="text-slate-500">樣本不足 (n={e.decided})</span>
                : <b className={rateCls(e.hitRate)}>{e.hitRate}%（{e.hits}/{e.decided}）
                    <span className="font-normal text-slate-500"> · 下界 {wilsonLower(e.hits, e.decided).toFixed(0)}%</span>
                  </b>}
            </span>
          ))}
        </div>
      )}
      <p className="text-[10px] text-slate-600 mb-3">按專家以 15 交易日主窗計 · 「下界」= Wilson 95% 置信區間下界（小樣本懲罰後嘅保守命中率）· hover 睇平均簽名超額</p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr className="text-left text-slate-500 border-b border-slate-800">
            <th className="py-1.5 pr-3">日期</th><th className="pr-3">專家</th><th className="pr-3">信號</th><th className="pr-3">工具</th>
            {d.windows.map(w => <th key={w} className="pr-3 text-right">{w}日</th>)}
          </tr></thead>
          <tbody>
            {d.rows.slice(0, 20).map((r, i) => (
              <tr key={i} className="border-b border-slate-800/50 text-slate-300">
                <td className="py-1.5 pr-3 whitespace-nowrap text-slate-400">{r.date}</td>
                <td className="pr-3">{r.expert}</td>
                <td className="pr-3">{r.asset} {r.direction === 'bull' ? '看多' : r.direction === 'bear' ? '看空' : '中性'}</td>
                <td className="pr-3 text-sky-300">{r.ticker}</td>
                {d.windows.map(w => {
                  const c = r.cells?.[w]
                  return (
                    <td key={w} className="pr-3 text-right tabular-nums whitespace-nowrap"
                      title={c ? `超額 ${c.excessPct >= 0 ? '+' : ''}${c.excessPct}pp vs ACWI` : '未到期'}>
                      {c == null ? <span className="text-slate-700">—</span>
                        : <span className={c.hit ? 'text-emerald-400' : 'text-rose-400'}>{c.retPct >= 0 ? '+' : ''}{c.retPct}% {c.hit ? '✓' : '✗'}</span>}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Phase 13：方向分佈披露——專家觀點天然偏多，命中率解讀必須計入呢個偏差 */}
      <p className="text-[10px] text-slate-500 mt-3">
        信號方向分佈：Bull:{dirCount.bull} Bear:{dirCount.bear} Neutral:{dirCount.neutral} ｜ 專家觀點天然偏多（sell-side 平均 74% 買入），命中率解讀請留意。
      </p>
      <p className="text-[10px] text-slate-600 mt-1 border-t border-slate-800/60 pt-2">
        誠實邊界：格仔內嘅 % 係 ETF 自身窗口收益，紅綠 ✓✗ 按「對 ACWI 嘅超額」判定（hover 顯示超額數值）；而家可判定樣本得 ~35 條（15 日窗），95% 置信區間闊約 ±16pp——呢塊鏡係攞嚟睇趨勢（邊類信號邊個窗口開始有邊際），唔係專家排名定案；45/90 日窗要觀點庫再成熟兩三個月先開到。
      </p>
    </Card>
  )
}

// ---- 量化算法：Calvin × 孫子兵法 融合算法引擎（規格 research/algo-spec.md §5）----
const LAMP_CLS: Record<AlgoRuleState['lamp'], { label: string; cls: string }> = {
  pass: { label: '通過', cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' },
  warn: { label: '警告', cls: 'bg-amber-500/15 text-amber-300 border-amber-500/40' },
  fail: { label: '否決', cls: 'bg-rose-500/15 text-rose-300 border-rose-500/40' },
  na: { label: '無讀數', cls: 'bg-slate-600/30 text-slate-500 border-slate-700' },
}
const CONF_CLS: Record<string, string> = {
  證實: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  推斷: 'bg-sky-500/10 text-sky-300 border-sky-500/30',
  缺口: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
}
const ACTION_META: Record<string, { label: string; cls: string }> = {
  add: { label: '加倉', cls: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' },
  reduce: { label: '減倉', cls: 'bg-rose-500/15 text-rose-300 border-rose-500/40' },
  trim: { label: '止盈', cls: 'bg-amber-500/15 text-amber-300 border-amber-500/40' },
  hold: { label: '持有', cls: 'bg-slate-600/30 text-slate-400 border-slate-600' },
}

function AlgoRuleCard({ r }: { r: AlgoRuleState }) {
  const lamp = LAMP_CLS[r.lamp]
  return (
    <div className={`rounded-lg border p-3.5 ${r.id === 'X1' ? 'border-rose-500/50 bg-rose-500/5' : 'border-slate-800 bg-slate-800/40'}`}>
      <div className="flex flex-wrap items-center gap-2 mb-1.5">
        <span className={`text-xs font-bold ${r.origin === 'calvin' ? 'text-indigo-300' : r.origin === 'quant' ? 'text-teal-300' : 'text-amber-300'}`}>{r.id}</span>
        <span className="text-sm text-slate-100 font-medium">{r.name}</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-700/50 text-slate-400">{r.level} 級</span>
        <span className={`text-[10px] px-1.5 py-0.5 rounded border ${CONF_CLS[r.confidence]}`}>{r.confidence}</span>
        <span className={`ml-auto text-[10px] px-2 py-0.5 rounded-full border ${lamp.cls}`}>
          {r.lamp === 'na' ? '● 後端未連接/無讀數' : `● ${lamp.label}`}
        </span>
      </div>
      <p className="text-xs text-slate-300 leading-relaxed">{r.quote}</p>
      <p className="text-[10px] text-slate-500 mt-1">{r.source}</p>
      <p className={`text-xs mt-2 ${r.lamp === 'na' ? 'text-slate-600' : r.lamp === 'fail' ? 'text-rose-300' : r.lamp === 'warn' ? 'text-amber-300' : 'text-emerald-300/90'}`}>
        讀數：{r.reading}
      </p>
    </div>
  )
}

function AlgoEngine() {
  const { data, backendDown } = useAlgo()
  // 規則卡永遠渲染（元數據在 contracts/algoRules.ts 共享）；後端未連接時讀數與燈號灰化
  const rules: AlgoRuleState[] = ALGO_RULES_META.map(m => {
    const live = data?.rules.find(x => x.id === m.id)
    if (live) return live
    return { id: m.id, name: m.name, origin: m.origin, level: m.level, confidence: m.confidence, quote: m.quote, source: m.source, reading: backendDown ? '後端未連接（靜態預覽模式）' : '讀數載入中…', lamp: 'na' as const }
  })
  const calvinRules = rules.filter(r => r.origin === 'calvin')
  const suntzuRules = rules.filter(r => r.origin === 'suntzu' && r.id !== 'X1')
  const quantRules = rules.filter(r => r.origin === 'quant')
  const rejected = rules.find(r => r.id === 'X1')
  const mktDown = backendDown || !data || data.status === 'unavailable'

  return (
    <div className="space-y-6">
      {/* 卡 1：三層架構流 */}
      <Card title="融合算法引擎：四層架構" sub="Calvin 戰術層（K1-K10）× 孫子戰略層（S1-S11）× 機構量化層（M1-M5）× 專家信號管道；全部規則標注來源置信度與可驗證級別">
        <div className="flex flex-col lg:flex-row items-stretch gap-2 text-center">
          {[
            { t: '① 專家信號層', d: 'YouTube字幕+全網新聞 → LLM結構化 → 時間衰減 → 主題共識', o: 'expert_score(ticker) ∈ [-1, +1]', cls: 'border-sky-500/40 bg-sky-500/5 text-sky-300' },
            { t: '② Calvin 戰術層', d: 'K1 趨勢定方向 · K3 MDD倉位上限 · K4 Equity開關 · K6 波動率regime', o: 'trend_score ∈ [-1, +1] + 倉位上限 + 全局閘門', cls: 'border-indigo-500/40 bg-indigo-500/5 text-indigo-300' },
            { t: '③ 孫子戰略層', d: 'S1 廟算門檻 · S6 避銳擊惰 · S9 組合熱度 · S10 冷卻機制', o: 'gates：通過 / 否決 + 原因', cls: 'border-amber-500/40 bg-amber-500/5 text-amber-300' },
            { t: '④ 建議輸出', d: 'fused = 50 + 50 × (0.5·expert + 0.5·trend) × regime × equity_gate', o: 'per-ETF：fused 0-100 · 動作 · 目標調整 pp', cls: 'border-emerald-500/40 bg-emerald-500/5 text-emerald-300' },
          ].map((s, i) => (
            <div key={s.t} className="flex-1 flex items-center gap-2">
              <div className={`flex-1 rounded-lg border p-3 ${s.cls}`}>
                <p className="text-sm font-semibold">{s.t}</p>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{s.d}</p>
                <p className="text-[11px] mt-1.5 font-mono">{s.o}</p>
              </div>
              {i < 3 && <span className="hidden lg:block text-slate-600 text-lg">→</span>}
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 mt-3 text-xs">
          <span className={`px-2 py-1 rounded border ${data ? (data.regime === 'highVol' ? 'bg-amber-500/15 text-amber-300 border-amber-500/40' : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40') : 'bg-slate-600/30 text-slate-500 border-slate-700'}`}>
            regime：{data ? (data.regime === 'highVol' ? '高波動（趨勢權重 0.7）' : '正常') : '—'}
          </span>
          <span className={`px-2 py-1 rounded border ${data ? (data.equityGateOn ? 'bg-rose-500/15 text-rose-300 border-rose-500/40' : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40') : 'bg-slate-600/30 text-slate-500 border-slate-700'}`}>
            K4 equity gate：{data ? (data.equityGateOn ? '觸發（否決加倉）' : '未觸發') : '—'}
          </span>
          <span className={`px-2 py-1 rounded border ${data?.portfolioDD != null ? (data.portfolioDD <= -8 ? 'bg-rose-500/15 text-rose-300 border-rose-500/40' : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40') : 'bg-slate-600/30 text-slate-500 border-slate-700'}`}>
            組合回撤：{data?.portfolioDD != null ? `${data.portfolioDD}%` : '—'}
          </span>
          {data && <span className="px-2 py-1 rounded border bg-slate-700/40 text-slate-400 border-slate-700">數據 {new Date(data.asOf).toLocaleString('zh-HK')} · 1 小時緩存</span>}
        </div>
      </Card>

      {/* 卡 2：融合信號表 */}
      <Card title="融合信號表（19 隻持倉 ETF）" sub={mktDown ? '後端未連接或行情不可用——規則卡照常展示（見下方），讀數灰化' : `expert=專家層加權淨分 · trend=0.5×sign(price−SMA200)+0.5×sign(mom126) · fused=融合分（≥60可議加/≤40可議減）· 閘門=通過數/總數${data?.status === 'partial' ? ' · ⚠ 部分行情缺失' : ''}`}>
        {mktDown ? (
          <div className="rounded-lg border border-slate-700/60 bg-slate-800/20 px-4 py-3 text-xs text-slate-500">
            {backendDown ? '後端未連接（靜態預覽模式）——部署後此處顯示每隻 ETF 的 expert/trend/fused 分數、動作徽章與閘門明細。' : data ? `行情源不可用：${data.summary}` : '引擎計算中（首次需拉取 19 隻 ETF 一年日線，約 10 秒）…'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-slate-400 border-b border-slate-800">
                  <th className="py-2 pr-3">ETF</th><th className="pr-3 text-right">現價</th>
                  <th className="pr-3 text-right">expert</th><th className="pr-3 text-right">trend</th>
                  <th className="pr-3 text-right">z 乖離</th><th className="pr-3 text-right">MDD(1y)</th>
                  <th className="pr-3 text-right">fused</th><th className="pr-3 text-center">動作</th>
                  <th className="pr-3 text-center">閘門</th><th className="text-right">建議調整</th>
                </tr>
              </thead>
              <tbody>
                {[...data.tickers].sort((a, b) => b.fusedScore - a.fusedScore).map(r => {
                  const am = ACTION_META[r.action]
                  const passed = r.gates.filter(g => g.passed).length
                  return (
                    <tr key={r.ticker} className="border-b border-slate-800/60 hover:bg-slate-800/20">
                      <td className="py-2 pr-3 font-bold text-sky-300">{r.ticker}</td>
                      <td className="pr-3 text-right tabular-nums text-slate-300">${r.price.toFixed(2)}</td>
                      <td className={`pr-3 text-right tabular-nums ${r.expertScore > 0 ? 'text-emerald-400' : r.expertScore < 0 ? 'text-rose-400' : 'text-slate-500'}`}>{r.expertScore >= 0 ? '+' : ''}{r.expertScore.toFixed(2)}</td>
                      <td className={`pr-3 text-right tabular-nums ${r.trendScore > 0 ? 'text-emerald-400' : r.trendScore < 0 ? 'text-rose-400' : 'text-slate-500'}`}>{r.trendScore >= 0 ? '+' : ''}{r.trendScore.toFixed(1)}</td>
                      <td className={`pr-3 text-right tabular-nums ${(r.zscore ?? 0) > 2 || (r.zscore ?? 0) < -2 ? 'text-amber-300 font-semibold' : 'text-slate-400'}`}>{r.zscore != null ? `${r.zscore >= 0 ? '+' : ''}${r.zscore.toFixed(2)}` : '—'}</td>
                      <td className="pr-3 text-right tabular-nums text-slate-400">{r.mdd1y != null ? `${(r.mdd1y * 100).toFixed(0)}%` : '—'}</td>
                      <td className={`pr-3 text-right tabular-nums font-bold ${r.fusedScore >= 60 ? 'text-emerald-400' : r.fusedScore <= 40 ? 'text-rose-400' : 'text-slate-300'}`}>{r.fusedScore}</td>
                      <td className="pr-3 text-center"><span className={`px-2 py-0.5 rounded-full border text-[10px] ${am.cls}`}>{am.label}</span></td>
                      <td className="pr-3 text-center tabular-nums text-slate-400" title={r.gates.map(g => `${g.rule}${g.passed ? '✓' : '✗'} ${g.note}`).join('\n')}>{passed}/{r.gates.length}</td>
                      <td className="text-right tabular-nums">
                        {r.targetDeltaPp !== 0 ? (
                          <span className={r.targetDeltaPp > 0 ? 'text-emerald-400 font-semibold' : r.action === 'trim' ? 'text-amber-300 font-semibold' : 'text-rose-400 font-semibold'}>
                            {r.targetDeltaPp > 0 ? '+' : ''}{r.targetDeltaPp}pp
                            {r.action === 'add' && <span className="block text-[9px] text-slate-500">首筆試倉</span>}
                            {r.action === 'trim' && <span className="block text-[9px] text-slate-500">減現倉 1/4</span>}
                          </span>
                        ) : <span className="text-slate-600">—</span>}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        {data && !mktDown && <p className="text-xs text-slate-500 mt-3">{data.summary}</p>}
      </Card>

      {/* 卡 3：Calvin 規則庫 K1-K10 */}
      <Card title="Calvin 規則庫（K1-K10）" sub="語錄為訪談/專欄 verbatim；[證實]=原文直引 · [推斷]=方法論適配 ETF · [缺口]=實盤參數保密、以學術標準參數替代；A 級=可回測機制 · B 級=流程規則 · C 級=哲學命名（不作交易條件）">
        <div className="grid md:grid-cols-2 gap-3">
          {calvinRules.map(r => <AlgoRuleCard key={r.id} r={r} />)}
        </div>
      </Card>

      {/* 卡 4：孫子兵法矩陣 S1-S11 + 剔除卡 */}
      <Card title="孫子兵法矩陣（S1-S11）" sub="原文引自十三篇對照表；量化規則為本站推斷適配（級別 A=可回測 / B=流程）。「投之亡地」明確剔除——與風控公理衝突時捨棄兵法。">
        <div className="grid md:grid-cols-2 gap-3">
          {suntzuRules.map(r => <AlgoRuleCard key={r.id} r={r} />)}
        </div>
        {rejected && (
          <div className="mt-3">
            <p className="text-xs text-rose-300 font-medium mb-2">▼ 剔除卡（不作為引擎規則，僅作誠實性記錄）</p>
            <AlgoRuleCard r={rejected} />
          </div>
        )}
      </Card>

      {/* 卡 4.5：機構量化層 M1-M5 */}
      <Card title="機構量化層（M1-M5）" sub="綜合 Renaissance / Citadel / Jane Street / Millennium 公開可考證方法論，適配低中頻 ETF 場景（規格 research/quant-model-synthesis.md）。誠實標注：四家實盤模型全部保密，本層只採用公開書籍/論文/訪談方法，confidence 一律 [推斷]——不採用任何無法考證的「內部參數」。">
        <div className="grid md:grid-cols-2 gap-3">
          {quantRules.map(r => <AlgoRuleCard key={r.id} r={r} />)}
        </div>
      </Card>

      {/* 卡 5：誠實聲明卡（琥珀色） */}
      <section className="rounded-xl border border-amber-500/40 bg-amber-500/5 p-5">
        <h2 className="text-base font-semibold text-amber-300 mb-2">⚠ 誠實聲明（跟據本引擎操作前必讀）</h2>
        <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside leading-relaxed">
          <li><b className="text-white">逆向工程局限</b>：Calvin 實盤參數明言保密——「最賺錢的策略、現在用的策略參數……比較敏感，吃飯的方法不能講」。本引擎所有指標參數（SMA200、6 個月動量、20 日波動率、z=±2σ、9 日淨值均線、6% 虧損預算、80 分位 regime）均為<b className="text-white">文獻標準參數</b>，不是他的實盤參數。</li>
          <li><b className="text-white">級別定義</b>：A 級=可回測機制（K1/K3/K4/K5/K6/K8、S1/S3/S4/S5/S6/S7/S9/S10）；B 級=流程/審計規則（K7/K9、S2/S8/S11）；C 級=哲學命名（K10），<b className="text-white">C 級禁止作為交易條件</b>。</li>
          <li><b className="text-white">過擬合控制</b>：Bailey / López de Prado 警告——5 年日數據最多隻能試約 45 個變體，超出即大概率過擬合。本站<b className="text-white">零參數搜索</b>：全部參數取自公開文獻（TSMOM、Faber 200DMA、海龜、vol targeting），不做 heat map 優化。</li>
          <li><b className="text-white">反面證據</b>：TSMOM 在 2010 年代後擁擠化、實盤 Sharpe 明顯衰減；趨勢過濾在震盪市會反覆挨打（whipsaw）；專家觀點超額收益的持續性在學術上很弱。本引擎是<b className="text-white">方法論演示</b>，不是收益承諾。</li>
          <li><b className="text-white">剔除原則</b>：「投之亡地然後存」（破釜沉舟）與風控公理衝突——凡衝突，捨棄兵法、保留風控。本站永遠不會建議孤注一擲。</li>
        </ul>
      </section>
    </div>
  )
}

function Disclaimer() {
  return (
    <p className="text-xs text-slate-500 border-t border-slate-800 pt-4 pb-8">
      免责声明：本工具仅为信息整理与方法论演示，不构成投资建议。专家观点均引自公开渠道并附来源与发表日期；回测为指数代理近似模拟。ETF 价格请以其 TradingView 页面及券商报价为准。投资涉及风险，过去表现不代表将来。
    </p>
  )
}
