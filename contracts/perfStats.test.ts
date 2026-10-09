import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { computePerfStats } from "@contracts/perfStats";

// ---- Phase 8 回歸：統計必須由淨值序列即時重算，唔准再出現半凍結分裂 ----
// 背景 bug：管道每日只更新 portRet/benchRet，netRet/maxDD/Sharpe 凍結喺 2026-07-23，
// 令頂部 pill（+12.3% 毛）同總覽大數字（+7.97% 淨）差 4.3pp——成本只得 0.12pp，差異其實係陳舊。

const perf = JSON.parse(readFileSync("public/data/performance.json", "utf8")) as {
  dates: string[]; portfolio: number[]; benchmark: number[];
  stats: { turnover: number; costDrag: number };
};

describe("perfStats 單一口徑計算器", () => {
  it("07-23 截斷可 100% 重現原始 REAL_STATS（方法學錨定）", () => {
    const i = perf.dates.indexOf("07-23");
    expect(i).toBeGreaterThan(0);
    const s = computePerfStats({
      dates: perf.dates.slice(0, i + 1),
      portfolio: perf.portfolio.slice(0, i + 1),
      benchmark: perf.benchmark.slice(0, i + 1),
    });
    // 對照 src/data/portfolio.ts REAL_STATS（2026-01-20→07-23 凍結記錄）
    expect(s.portRet).toBeCloseTo(8.09, 2);
    expect(s.benchRet).toBeCloseTo(5.34, 2);
    expect(s.netRet).toBeCloseTo(7.97, 2);
    expect(s.maxDD).toBeCloseTo(-8.17, 2);
    expect(s.benchMaxDD).toBeCloseTo(-6.61, 2);
    expect(s.vol).toBeCloseTo(18.4, 1);
    expect(s.benchVol).toBeCloseTo(10.8, 1);
    expect(s.annRet).toBeCloseTo(16.7, 1);
    expect(s.benchAnnRet).toBeCloseTo(10.9, 1);
    expect(s.sharpe).toBeCloseTo(0.69, 2);
    expect(s.benchSharpe).toBeCloseTo(0.64, 2);
  });

  it("全序列重算：portRet = 末值-100，netRet = portRet − costDrag（不存在半凍結空間）", () => {
    const s = computePerfStats({
      dates: perf.dates, portfolio: perf.portfolio, benchmark: perf.benchmark,
      turnover: perf.stats.turnover, costDrag: perf.stats.costDrag,
    });
    expect(s.portRet).toBeCloseTo(perf.portfolio[perf.portfolio.length - 1] - 100, 2);
    expect(s.benchRet).toBeCloseTo(perf.benchmark[perf.benchmark.length - 1] - 100, 2);
    expect(s.netRet).toBeCloseTo(s.portRet - s.costDrag, 2);
    // 文件 stats（若由新管道寫出）必須同即場重算一致——呢條就係防分裂嘅閘
    const file = JSON.parse(readFileSync("public/data/performance.json", "utf8"));
    expect(file.stats.netRet).toBeCloseTo(s.netRet, 2);
    expect(file.stats.maxDD).toBeCloseTo(s.maxDD, 2);
    expect(file.stats.sharpe).toBeCloseTo(s.sharpe, 2);
  });

  it("maxDD：已知序列 [100,110,90,120] → 90/110−1 = -18.18%", () => {
    const s = computePerfStats({
      dates: ["01-20", "01-21", "01-22", "01-23"],
      portfolio: [100, 110, 90, 120], benchmark: [100, 100, 100, 100],
    });
    expect(s.maxDD).toBeCloseTo(-18.18, 2);
    expect(s.benchMaxDD).toBe(0);
  });

  it("跨年 MM-DD：12-31 → 01-02 日曆日數唔會斷裂", () => {
    const s = computePerfStats({
      dates: ["12-30", "12-31", "01-02"],
      portfolio: [100, 101, 102], benchmark: [100, 100, 100],
      startDate: "2025-12-01",
    });
    expect(s.days).toBe(32); // 12-01 → 01-02
    expect(s.portRet).toBe(2);
  });
});
