// 共識矩陣「即時觀點併入」回歸測試——2026-09-06 修復：矩陣曾只讀靜態檔案，
// 管道新鮮信號（如洪灝 9/4 黃金看多、蔡金強長債看淡）從不反映，「即時計算」名不副實。
import { describe, it, expect } from 'vitest'
import { computeConsensus, themeOf, type LiveSignalView } from './consensus'

const NOW = new Date('2026-09-06T00:00:00Z')

const live: LiveSignalView[] = [
  {
    expertName: '洪灝',
    date: '2026-09-04',
    signals: [
      { asset: '黄金', direction: 'bull', strength: 4 },
      { asset: '铜', direction: 'bull', strength: 4 },
      { asset: '能源', direction: 'bull', strength: 3 },
      { asset: '美股', direction: 'neutral', strength: 3 },
    ],
  },
  {
    expertName: '蔡金強',
    date: '2026-09-02',
    signals: [
      { asset: '长债', direction: 'bear', strength: 4 },
      { asset: '比特币', direction: 'bull', strength: 4 },
    ],
  },
  { expertName: '某訪談訪客', date: '2026-09-01', signals: [{ asset: '黄金', direction: 'bear', strength: 5 }] },
]

describe('computeConsensus 併入管道即時觀點', () => {
  const rows = computeConsensus(NOW, live)
  const byTheme = Object.fromEntries(rows.map(r => [r.theme, r]))

  it('即時看多信號進入對應主題的專家單元格（洪灝 → 黃金）', () => {
    expect(byTheme['黄金 / 贵金属'].cells['hong']).toBe('bull')
  })

  it('「铜」歸入黃金/貴金屬主題（組合內 COPX 與 GLD/SLV 同組）', () => {
    expect(themeOf('铜')).toBe('黄金 / 贵金属')
  })

  it('「中国」歸入中國A股主題', () => {
    expect(themeOf('中国')).toBe('中国A股')
  })

  it('即時看淡信號進入債券主題（蔡金強 長債 bear）', () => {
    expect(byTheme['债券'].cells['choi']).toBe('bear')
  })

  it('比特幣主題反映即時看多（蔡金強 IBIT bull）', () => {
    expect(byTheme['比特币'].cells['choi']).toBe('bull')
  })

  it('對不上專家檔案的訪客觀點不入矩陣', () => {
    // 訪客 bear-5 黃金若誤入會拉低淨分；此處斷言淨分不被訪客影響（無該專家欄）
    expect(Object.keys(byTheme['黄金 / 贵金属'].cells)).not.toContain('某訪談訪客')
  })

  it('不傳即時觀點時行為與舊版一致（向後兼容）', () => {
    const base = computeConsensus(NOW)
    expect(base.length).toBe(rows.length)
  })

  it('超過 90 天的即時觀點權重為 0，不產生單元格', () => {
    const stale: LiveSignalView[] = [
      { expertName: '洪灝', date: '2026-01-01', signals: [{ asset: '比特币', direction: 'bull', strength: 5 }] },
    ]
    const r = computeConsensus(NOW, stale)
    const btc = r.find(x => x.theme === '比特币')!
    expect(btc.cells['hong'] ?? null).toBe(
      computeConsensus(NOW).find(x => x.theme === '比特币')!.cells['hong'] ?? null,
    )
  })
})
