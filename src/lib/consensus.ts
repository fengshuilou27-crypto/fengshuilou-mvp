// 共识矩阵计算引擎：由专家观点库 + 时间衰减即时计算（废除手工维护的静态矩阵，防止数据漂移）
import { EXPERTS } from '../data/experts'

// Phase 13：新增「医疗 / 医药」主题（XLV 此前無主題條目，信號無處歸類）
export const THEMES = ['半导体 / AI上游', '黄金 / 贵金属', '中国A股', 'HALO 重资产(能材基)', '韩台股市', '美股大盘', '欧洲股票', '港股', '比特币', '债券', '日股', '医疗 / 医药'] as const

// 观点 stance.asset 关键词 → 主题（与管道 ASSET_MAP 同源逻辑）
const THEME_MAP: [RegExp, string][] = [
  [/半导体|芯片|晶片|算力|AI上游|AI板块|AI$|记忆体/i, '半导体 / AI上游'],
  [/黄金|金价|白银|贵金属|金银铜|铜价|铜/i, '黄金 / 贵金属'],
  [/A股|中国资产|人民币|在岸|中国增长股|中国|沪深/i, '中国A股'],
  [/重资产|能源|材料|基建|油/i, 'HALO 重资产(能材基)'],
  [/韩国|韩股|韩台|台韩|台湾|台股|台积电|晶片链/i, '韩台股市'],
  [/欧洲|欧元区/i, '欧洲股票'],
  [/港股|恒指|中特估|本地蓝筹|中港|香港/i, '港股'],
  [/比特币|加密/i, '比特币'],
  [/日股|日圆|日本/i, '日股'],
  // Phase 13 修復：舊版 /息/ 太濫——任何含「息」嘅資產（高息股、派息、股息）都誤歸債券主題；
  // 收窄為明確嘅利率/債券詞，逐個詞精確匹配
  [/债券|长债|国债|债息|减息|降息|加息|利率/i, '债券'],
  // Phase 13 修復：剔除「非美」——「非美資產」係看淡美元/轉投非美市場，唔係美股信號，舊版誤歸美股大盘
  [/美股|标普|环球股票|美元资产/i, '美股大盘'],
  // Phase 13：醫療主題（XLV）——醫藥政策青睞 + 防禦性敞口
  [/医疗|医药|创新药|health/i, '医疗 / 医药'],
]

export function themeOf(asset: string): string | null {
  for (const [re, t] of THEME_MAP) if (re.test(asset)) return t
  return null
}

export function decayWeight(dateStr: string, now = new Date()) {
  const days = Math.max(0, (now.getTime() - new Date(dateStr).getTime()) / 86400000)
  if (days > 90) return 0 // 规则：超过90天权重=0
  return Math.pow(0.5, days / 21)
}

export interface ComputedRow {
  theme: string
  cells: Record<string, 'bull' | 'bear' | 'neutral' | null>
  net: number
}

// 管道即時觀點（快照 views）——結構與 SnapshotView 對齊，強度 1-5
export interface LiveSignalView {
  expertName: string
  date: string
  signals: { asset: string; direction: 'bull' | 'bear' | 'neutral'; strength?: number }[]
  // Phase 13：後端正為 view 加緊 decayWeight 欄（管道按分級半衰期 7/21/45 日折算）。
  // 有就直接用；冇先 fallback 用自己嘅固定 21 日半衰期折算（臨時口径，見 computeConsensus 註釋）。
  decayWeight?: number
}

// 即時觀點的專家名 → 靜態檔案專家（雙向包含匹配，與 Home「即時入庫」卡同一規則）
function matchExpert(name: string) {
  const n = name.trim()
  return EXPERTS.find(e => e.name.includes(n) || n.includes(e.name)) ?? null
}

export function computeConsensus(now = new Date(), live: LiveSignalView[] = []): ComputedRow[] {
  const expertWeight: Record<string, number> = {}
  for (const e of EXPERTS) expertWeight[e.id] = e.active ? e.weightInPortfolio : 0

  // 即時觀點按專家分組（只保留能對上專家檔案的；訪客觀點無權重欄位，不入矩陣）
  const liveByExpert = new Map<string, LiveSignalView[]>()
  for (const v of live) {
    const e = matchExpert(v.expertName)
    if (!e) continue
    const arr = liveByExpert.get(e.id) ?? []
    arr.push(v)
    liveByExpert.set(e.id, arr)
  }

  return THEMES.map(theme => {
    const cells: ComputedRow['cells'] = {}
    let num = 0, den = 0
    for (const e of EXPERTS) {
      let score = 0
      for (const v of e.views) {
        const w = decayWeight(v.date, now)
        if (w === 0) continue
        for (const s of v.stance) {
          if (themeOf(s.asset) !== theme) continue
          const dir = s.dir === 'bull' ? 1 : s.dir === 'bear' ? -1 : 0
          score += dir * w
        }
      }
      // 併入管道即時觀點：同一衰減規則
      for (const v of liveByExpert.get(e.id) ?? []) {
        // Phase 13：view 自帶 decayWeight（管道分級半衰期口径）就直接用；
        // 冇先 fallback 固定 21 日半衰期自己折算——臨時口径，待後端欄位全面鋪開後可移除 fallback
        const w = v.decayWeight ?? decayWeight(v.date, now)
        if (w === 0) continue
        for (const s of v.signals) {
          if (themeOf(s.asset) !== theme) continue
          const dir = s.direction === 'bull' ? 1 : s.direction === 'bear' ? -1 : 0
          // Phase 13 修復：強度量表同管道/algo 统一為 1-5，歸一化應除以 5（舊版 /3 令強信號權重虛高 67%）
          score += dir * w * ((s.strength ?? 3) / 5)
        }
      }
      const has = score !== 0
        || e.views.some(v => decayWeight(v.date, now) > 0 && v.stance.some(s => themeOf(s.asset) === theme))
        || (liveByExpert.get(e.id) ?? []).some(v => (v.decayWeight ?? decayWeight(v.date, now)) > 0 && v.signals.some(s => themeOf(s.asset) === theme))
      cells[e.id] = !has ? null : score > 0.15 ? 'bull' : score < -0.15 ? 'bear' : 'neutral'
      const cellDir = cells[e.id] === 'bull' ? 1 : cells[e.id] === 'bear' ? -1 : 0
      if (cells[e.id] !== null) { num += cellDir * (expertWeight[e.id] || 0); den += expertWeight[e.id] || 0 }
    }
    const net = den === 0 ? 0 : Math.round((num / den) * 100)
    return { theme, cells, net }
  })
}

// 主题 → 组合动作（配置规则说明，随矩阵一起展示）
export const THEME_ACTIONS: Record<string, string> = {
  '半导体 / AI上游': 'SMH 10%（共识强但受隐形债务/广度警示封顶）',
  '黄金 / 贵金属': 'GLD+SLV+COPX 15%（已自高位兑现部分）',
  '中国A股': 'ASHR+MCHI 13%（以在岸 ASHR 为主）',
  'HALO 重资产(能材基)': 'XLE+XLB+IFRA 15%',
  '韩台股市': 'EWY+EWT 9%',
  '美股大盘': 'VOO 12%（多空对冲后温和超配）',
  '欧洲股票': 'VGK 3%（银行对冲逻辑，适配度中等）',
  '港股': 'EWH 6%（观点分歧大→低配）',
  '比特币': 'IBIT 2% 试探仓',
  '债券': 'TLT+BND 7% 基础缓冲',
  '日股': '0% 不配（三专家一致看淡）',
  // Phase 13：補 XLV（醫療）條目——此前矩陣無醫療主題，XLV 信號無處展示
  '医疗 / 医药': 'XLV 4%（醫藥政策青睞 + 防禦性敞口）',
}
