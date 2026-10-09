// Phase 13：調倉鏈完整性回歸測試
// 背景：REBALANCES 調倉#1 曾遺漏 TLT 4→3，令 replay 出 TLT=4、Σ=101，
// 與 ETF_PORTFOLIO 當前權重（TLT=3、Σ=100）矛盾。
import { describe, it, expect } from 'vitest'
import { ETF_PORTFOLIO, REBALANCES } from '../data/portfolio'

// 由初始建倉起逐次調倉 replay；每個 change 的 from 必須等於 replay 當前值（鏈條唔准斷）
function replay() {
  const w = new Map<string, number>()
  for (const r of REBALANCES) {
    for (const c of r.changes) {
      const cur = w.get(c.etf) ?? 0
      if (cur !== c.from) throw new Error(`${r.date} ${r.title}：${c.etf} from=${c.from} 但 replay 當前值=${cur}`)
      w.set(c.etf, c.to)
    }
  }
  return w
}

describe('REBALANCES 調倉鏈 replay', () => {
  it('每個 change 的 from 與上一次狀態銜接（鏈條無斷裂）', () => {
    expect(() => replay()).not.toThrow()
  })

  it('replay 初始建倉 + 全部調倉後，每個 ETF 權重 == 當前持倉權重', () => {
    const w = replay()
    for (const e of ETF_PORTFOLIO) {
      expect(w.get(e.ticker), e.ticker).toBe(e.weight)
    }
    // 唔准有 replay 出嚟但持倉表冇嘅 ETF
    for (const k of w.keys()) {
      expect(ETF_PORTFOLIO.some(e => e.ticker === k), k).toBe(true)
    }
  })

  it('最終權重總和 = 100', () => {
    const sum = [...replay().values()].reduce((a, b) => a + b, 0)
    expect(sum).toBe(100)
    expect(ETF_PORTFOLIO.reduce((s, e) => s + e.weight, 0)).toBe(100)
  })
})
