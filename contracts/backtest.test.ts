// Phase 12 多窗口信號回測純函數測試（contracts/backtest.ts）
import { describe, it, expect } from "vitest";
import {
  BT_WINDOWS, scoreHit, windowRetPct, evalWindows, aggregateWindow, aggregateExpert,
  type BtPricePoint, type BtCells,
} from "@contracts/backtest";

// 生成 n 個工作日收盤（跳過週末），由 start 起每日 +step
function mk(start: string, n: number, step: number, from = 100): BtPricePoint[] {
  const out: BtPricePoint[] = [];
  const d = new Date(start + "T00:00:00Z");
  while (out.length < n) {
    const wd = d.getUTCDay();
    if (wd !== 0 && wd !== 6) out.push({ date: d.toISOString().slice(0, 10), close: from + out.length * step });
    d.setUTCDate(d.getUTCDate() + 1);
  }
  return out;
}

describe("scoreHit 超額命中邊界", () => {
  it("bull：+0.5pp 唔算命中，+0.51pp 命中", () => {
    expect(scoreHit(0.5, "bull")).toBe(false);
    expect(scoreHit(0.51, "bull")).toBe(true);
  });
  // Phase 13 P2-11：±0.5 嚴格邊界（浮點級）
  it("bull 嚴格邊界：excess=+0.5 → MISS，+0.5001 → HIT", () => {
    expect(scoreHit(0.5, "bull")).toBe(false);
    expect(scoreHit(0.5001, "bull")).toBe(true);
  });
  it("bear 嚴格邊界：excess=−0.5 → MISS，−0.5001 → HIT", () => {
    expect(scoreHit(-0.5, "bear")).toBe(false);
    expect(scoreHit(-0.5001, "bear")).toBe(true);
  });
  it("neutral 嚴格邊界：|excess|=2 → HIT（含端點）", () => {
    expect(scoreHit(2, "neutral")).toBe(true);
    expect(scoreHit(-2, "neutral")).toBe(true);
  });
  it("bear：−0.5pp 唔算命中，−0.51pp 命中", () => {
    expect(scoreHit(-0.5, "bear")).toBe(false);
    expect(scoreHit(-0.51, "bear")).toBe(true);
  });
  it("neutral：|excess|≤2pp 命中，2.01pp 唔中", () => {
    expect(scoreHit(2, "neutral")).toBe(true);
    expect(scoreHit(-2, "neutral")).toBe(true);
    expect(scoreHit(2.01, "neutral")).toBe(false);
  });
});

describe("windowRetPct", () => {
  const closes = mk("2026-07-15", 10, 1); // 100,101,...,109
  it("基本區間收益", () => {
    expect(windowRetPct(closes, "2026-07-15", "2026-07-17")).toBe(2); // 100→102
  });
  it("fromDate 非交易日 → 下一交易日；超出範圍 → null", () => {
    expect(windowRetPct(closes, "2026-07-18", "2026-07-21")).not.toBeNull(); // 週六→週一
    expect(windowRetPct(closes, "2026-08-01", "2026-08-05")).toBeNull();
  });
  it("toDate 唔晚於 fromDate → null", () => {
    expect(windowRetPct(closes, "2026-07-20", "2026-07-15")).toBeNull();
  });
});

describe("evalWindows 多窗口階梯", () => {
  it("收益/超額/命中數學：ETF 100→105@5d、ACWI 100→102 → ret 5、excess 3、bull 命中", () => {
    const etf = mk("2026-07-15", 96, 1);   // 每日 +1
    const acwi = mk("2026-07-15", 96, 0.4); // 每日 +0.4
    const cells = evalWindows(etf, acwi, "2026-07-15", "bull");
    const c5 = cells[5]!;
    expect(c5.retPct).toBe(5);
    expect(c5.excessPct).toBe(3); // 5 − (0.4*5=2)
    expect(c5.hit).toBe(true);
    for (const w of BT_WINDOWS) expect(cells[w]).not.toBeNull();
  });
  it("成熟度階梯：得 6 日數據 → 5 日窗有值，15/45/90 全 null", () => {
    const cells = evalWindows(mk("2026-07-15", 6, 1), mk("2026-07-15", 6, 0.4), "2026-07-15", "bull");
    expect(cells[5]).not.toBeNull();
    expect(cells[15]).toBeNull();
    expect(cells[45]).toBeNull();
    expect(cells[90]).toBeNull();
  });
  it("發布日係週六 → 用週一收盤做入場", () => {
    const cells = evalWindows(mk("2026-07-15", 20, 1), mk("2026-07-15", 20, 0), "2026-07-18", "bull");
    const c5 = cells[5]!;
    expect(c5.retPct).toBe(4.85); // 週一 07-20 close=103 → 第5個交易日 07-27 close=108
  });
  it("發布日晚過最新收盤 → 全窗 null", () => {
    const cells = evalWindows(mk("2026-07-15", 5, 1), mk("2026-07-15", 5, 0), "2026-08-01", "bull");
    for (const w of BT_WINDOWS) expect(cells[w]).toBeNull();
  });
  it("ACWI 缺對應退出日 → 用下一交易日；ACWI 太短 → 該窗 null", () => {
    const etf = mk("2026-07-15", 96, 1);
    const acwiShort = mk("2026-07-15", 6, 0.4);
    const cells = evalWindows(etf, acwiShort, "2026-07-15", "bull");
    expect(cells[5]).not.toBeNull();
    expect(cells[15]).toBeNull();
  });
  it("bear 信號：跑輸 ACWI 先算命中", () => {
    const etf = mk("2026-07-15", 20, 0);    // 原地踏步
    const acwi = mk("2026-07-15", 20, 1);   // ACWI 升
    const cells = evalWindows(etf, acwi, "2026-07-15", "bear");
    expect(cells[5]!.excessPct).toBe(-5);
    expect(cells[5]!.hit).toBe(true);
  });
});

describe("aggregateWindow / aggregateExpert", () => {
  const cell = (excessPct: number, hit: boolean) => ({ retPct: excessPct, excessPct, hit });
  const cellsWith = (w: number, c: ReturnType<typeof cell> | null): BtCells =>
    ({ 5: null, 15: null, 45: null, 90: null, [w]: c });

  it("pending / hitRate / insufficient（decided<10）", () => {
    const items = [
      { direction: "bull", cells: cellsWith(15, cell(3, true)) },
      { direction: "bull", cells: cellsWith(15, cell(-3, false)) },
      { direction: "bull", cells: cellsWith(15, null) }, // 未到期
    ];
    const agg = aggregateWindow(items, 15);
    expect(agg.decided).toBe(2);
    expect(agg.pending).toBe(1);
    expect(agg.hits).toBe(1);
    expect(agg.hitRate).toBe(50);
    expect(agg.insufficient).toBe(true);
  });
  it("bear 簽名超額取反；neutral 唔計入 avgExcessDirPct", () => {
    const items = [
      { direction: "bear", cells: cellsWith(15, cell(-3, true)) },  // 簽名 +3
      { direction: "bull", cells: cellsWith(15, cell(1, true)) },   // 簽名 +1
      { direction: "neutral", cells: cellsWith(15, cell(0.5, true)) }, // 排除
    ];
    const agg = aggregateWindow(items, 15);
    expect(agg.avgExcessDirPct).toBe(2); // (3+1)/2
  });
  it("aggregateExpert：分組、decided<3 → insufficient、按 decided 降序", () => {
    const items = [
      { expert: "A", direction: "bull", cells: cellsWith(15, cell(3, true)) },
      { expert: "A", direction: "bull", cells: cellsWith(15, cell(2, true)) },
      { expert: "A", direction: "bull", cells: cellsWith(15, cell(-1, false)) },
      { expert: "B", direction: "bull", cells: cellsWith(15, cell(3, true)) },
      { expert: "B", direction: "bull", cells: cellsWith(15, null) }, // 未到期唔計
    ];
    const agg = aggregateExpert(items);
    expect(agg[0].expert).toBe("A"); // decided 3 > B 嘅 1
    expect(agg[0].decided).toBe(3);
    expect(agg[0].hitRate).toBe(66.67);
    expect(agg[0].insufficient).toBe(false);
    expect(agg[1].expert).toBe("B");
    expect(agg[1].insufficient).toBe(true); // decided 1 < 3
  });
});
