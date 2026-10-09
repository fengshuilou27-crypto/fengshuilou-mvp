// 候選 ETF 篩選器純函數回歸測試（2026-09-11 Phase 11）
// 鎖死口徑：判語四檔規則、收益/波動/回撤計算、組合合成收益、判語附加旗標。
import { describe, it, expect } from "vitest";
import {
  pearson, retStats, weightedPortfolioReturns, dailyReturnsByDate, screenVerdict,
  type ScreenMetrics,
} from "@contracts/screener";

const mk = (over: Partial<ScreenMetrics> = {}): ScreenMetrics => ({
  ticker: "TEST",
  name: null, fundFamily: null, aumUsd: null, yieldPct: null, expenseRatioPct: null,
  stats1y: { ret: 0.1, vol: 0.12, mdd: -0.08 },
  corrToPortfolio: 0.9, avgCorrToHoldings: 0.85, maxPair: null, corrToVOO: 0.9, corrToACWI: 0.88,
  ...over,
});

describe("pearson", () => {
  it("完全相同序列 → 1", () => {
    const a = Array.from({ length: 50 }, (_, i) => Math.sin(i) * 0.02 + 0.001);
    expect(pearson(a, a)).toBe(1);
  });
  it("完全反向序列 → −1", () => {
    const a = Array.from({ length: 50 }, (_, i) => Math.sin(i) * 0.02 + 0.001);
    expect(pearson(a, a.map(v => -v))).toBe(-1);
  });
  it("樣本 <30 → null（誠實原則）", () => {
    expect(pearson([1, 2, 3], [1, 2, 3])).toBeNull();
  });
});

describe("retStats", () => {
  it("已知序列：總回報 / 最大回撤 / 波動區間", () => {
    const s = retStats([
      { date: "2026-01-01", close: 100 },
      { date: "2026-01-02", close: 105 },
      { date: "2026-01-03", close: 100 },
      { date: "2026-01-04", close: 110 },
    ]);
    expect(s.ret).toBe(0.1);
    expect(s.mdd).toBe(-0.048); // 100/105−1 = −4.762%
    expect(s.vol).toBeGreaterThan(1.0);
    expect(s.vol).toBeLessThan(1.4);
  });
  it("單點序列唔會炸", () => {
    expect(retStats([{ date: "2026-01-01", close: 100 }])).toEqual({ ret: 0, vol: 0, mdd: 0 });
  });
});

describe("weightedPortfolioReturns", () => {
  it("共同交易日交集 + 權重歸一", () => {
    const retsBy = {
      AAA: new Map([["d1", 0.02], ["d2", -0.01]]),
      BBB: new Map([["d1", 0.04], ["d2", 0.01], ["d3", 0.5]]),
    };
    const port = weightedPortfolioReturns(retsBy as never, { AAA: 50, BBB: 50 });
    expect(port.size).toBe(2); // d3 唔係共同日，剔除
    expect(port.get("d1")).toBeCloseTo(0.03, 10);
    expect(port.get("d2")).toBeCloseTo(0, 10);
  });
});

describe("screenVerdict 四檔規則", () => {
  const bench = { vooRet1y: 0.18, vooVol1y: 0.128, acwiRet1y: 0.196 };
  it("高重疊 + 跑輸 VOO → avoid", () => {
    const v = screenVerdict(mk({ corrToPortfolio: 0.9, stats1y: { ret: 0.1, vol: 0.12, mdd: -0.08 } }), bench);
    expect(v.tier).toBe("avoid");
    expect(v.headline).toContain("唔建議加入");
  });
  it("高重疊 + 跑贏 VOO → substitute", () => {
    const v = screenVerdict(mk({ corrToPortfolio: 0.9, stats1y: { ret: 0.2, vol: 0.12, mdd: -0.08 } }), bench);
    expect(v.tier).toBe("substitute");
    expect(v.headline).toContain("替代式");
  });
  it("低相關 → diversifier", () => {
    const v = screenVerdict(mk({ corrToPortfolio: 0.3 }), bench);
    expect(v.tier).toBe("diversifier");
  });
  it("中相關 → limited；相關缺失都係 limited（唔出假判語）", () => {
    expect(screenVerdict(mk({ corrToPortfolio: 0.65 }), bench).tier).toBe("limited");
    expect(screenVerdict(mk({ corrToPortfolio: null }), bench).tier).toBe("limited");
  });
});

describe("screenVerdict 附加旗標", () => {
  const bench = { vooRet1y: 0.18, vooVol1y: 0.128, acwiRet1y: 0.196 };
  it("高息旗標（≥6% 提預扣稅 + ROC）", () => {
    const v = screenVerdict(mk({ yieldPct: 9.4 }), bench);
    expect(v.points.some(p => p.includes("預扣稅"))).toBe(true);
  });
  it("近似重複曝光旗標（|ρ|≥0.75 單一持倉）", () => {
    const v = screenVerdict(mk({ maxPair: { holding: "VOO", corr: 0.91 } }), bench);
    expect(v.points.some(p => p.includes("變相加注 VOO"))).toBe(true);
  });
  it("貴費旗標（ER>0.6%）+ 細規模旗標", () => {
    const v = screenVerdict(mk({ expenseRatioPct: 0.9, aumUsd: 300_000_000 }), bench);
    expect(v.points.some(p => p.includes("偏貴"))).toBe(true);
    expect(v.points.some(p => p.includes("資產規模較細"))).toBe(true);
  });
  it("低波動旗標（≤ VOO 波動 75%）+ 跑輸 pp 陳述", () => {
    const v = screenVerdict(mk({ stats1y: { ret: 0.07, vol: 0.08, mdd: -0.05 } }), bench);
    expect(v.points.some(p => p.includes("防守性較強"))).toBe(true);
    expect(v.points.some(p => p.includes("跑輸 VOO"))).toBe(true);
  });
});

describe("dailyReturnsByDate", () => {
  it("相鄰兩日計收益，前收 ≤0 嘅嗰格先跳過", () => {
    const m = dailyReturnsByDate([
      { date: "d0", close: 100 }, { date: "d1", close: 102 }, { date: "d2", close: 0 }, { date: "d3", close: 103 },
    ]);
    expect(m.get("d1")).toBeCloseTo(0.02, 10);
    expect(m.get("d2")).toBe(-1); // 前收 102 有效 → 跌到 0 = −100%，如實記錄
    expect(m.has("d3")).toBe(false); // 前收 = 0 唔會做分母，跳過
  });
});
