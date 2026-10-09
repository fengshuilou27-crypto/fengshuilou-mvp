// 專家學習環純函數回歸測試（2026-09-12 P0）
// 鎖死口徑：命中率→因子映射、步幅/夾限/樣本閘、跑輸四分類（個別/系統性/大市/無）、R² 誠實空值。
import { describe, it, expect } from "vitest";
import {
  targetFactorFromHitRate, proposeFactor, classifyUnderperformance, dailyReturns, rSquared,
  FACTOR_MIN, FACTOR_MAX, MAX_WEEKLY_STEP,
} from "@contracts/learner";

describe("targetFactorFromHitRate", () => {
  it("50% 命中 = 中性 1.0", () => expect(targetFactorFromHitRate(50)).toBe(1));
  it("75% → 夾上限 1.5；25% → 夾下限 0.5", () => {
    expect(targetFactorFromHitRate(75)).toBe(FACTOR_MAX);
    expect(targetFactorFromHitRate(25)).toBe(FACTOR_MIN);
  });
  it("極端值唔會出界", () => {
    expect(targetFactorFromHitRate(100)).toBe(FACTOR_MAX);
    expect(targetFactorFromHitRate(0)).toBe(FACTOR_MIN);
  });
});

describe("proposeFactor 閘門", () => {
  it("樣本 <3：完全唔調", () => {
    const p = proposeFactor("choi", 80, 2, 1.2);
    expect(p.next).toBe(1.2);
    expect(p.reason).toContain("樣本不足");
  });
  it("步幅上限 ±0.1/週（滿樣本）", () => {
    // 100% 命中 → 目標 1.5，prev 1.0，最多行 +0.1
    const p = proposeFactor("hong", 100, 15, 1.0);
    expect(p.next).toBe(1.1);
  });
  it("樣本 <10 步幅減半（±0.05）", () => {
    const p = proposeFactor("tam", 100, 5, 1.0);
    expect(p.next).toBe(1.05);
  });
  it("下調對稱：0% 命中 prev 1.2 → -0.1", () => {
    const p = proposeFactor("lam", 0, 12, 1.2);
    expect(p.next).toBe(1.1);
  });
  it("已貼上限唔會再升", () => {
    const p = proposeFactor("timmer", 90, 20, FACTOR_MAX);
    expect(p.next).toBe(FACTOR_MAX);
  });
});

describe("classifyUnderperformance 四分類", () => {
  const base = { excess20dPp: -4.5, marketRSq: 0.5, consensusHitRate: 45, expertHitRates: [] as { expertId: string; hitRate: number | null; decided: number }[] };
  it("未觸線 → none", () => {
    expect(classifyUnderperformance({ ...base, excess20dPp: -1 }).verdict).toBe("none");
  });
  it("R²>0.8 → market（唔郁專家）", () => {
    const r = classifyUnderperformance({ ...base, marketRSq: 0.91, expertHitRates: [] });
    expect(r.verdict).toBe("market");
    expect(r.detail).toContain("大環境");
  });
  it("過半專家+共識都弱 → systemic", () => {
    const r = classifyUnderperformance({
      ...base,
      expertHitRates: [
        { expertId: "a", hitRate: 30, decided: 8 }, { expertId: "b", hitRate: 40, decided: 6 },
        { expertId: "c", hitRate: 35, decided: 5 }, { expertId: "d", hitRate: 70, decided: 9 },
      ],
    });
    expect(r.verdict).toBe("systemic");
  });
  it("只有一位弱 → individual（唔連坐）", () => {
    const r = classifyUnderperformance({
      ...base, consensusHitRate: 62,
      expertHitRates: [
        { expertId: "a", hitRate: 20, decided: 8 }, { expertId: "b", hitRate: 65, decided: 6 },
        { expertId: "c", hitRate: 70, decided: 5 },
      ],
    });
    expect(r.verdict).toBe("individual");
    expect(r.detail).toContain("a 20%");
  });
  it("有效專家 <3 位唔好亂判 systemic", () => {
    const r = classifyUnderperformance({
      ...base, consensusHitRate: 40,
      expertHitRates: [{ expertId: "a", hitRate: 10, decided: 4 }],
    });
    expect(r.verdict).toBe("individual");
  });
});

describe("rSquared", () => {
  it("完全同步序列 → 1", () => {
    const a = new Map(), b = new Map();
    for (let i = 0; i < 40; i++) { const v = Math.sin(i) * 0.01; a.set(`d${i}`, v); b.set(`d${i}`, v); }
    expect(rSquared(a, b)).toBe(1);
  });
  it("共同日 <30 → null（唔出假數字）", () => {
    const a = new Map([["d1", 0.01], ["d2", -0.01]]);
    const b = new Map([["d1", 0.02], ["d2", 0.01]]);
    expect(rSquared(a, b)).toBeNull();
  });
  it("dailyReturns 前收 ≤0 跳過", () => {
    const m = dailyReturns([{ date: "a", close: 100 }, { date: "b", close: 0 }, { date: "c", close: 101 }]);
    expect(m.get("b")).toBe(-1);
    expect(m.has("c")).toBe(false);
  });
});
