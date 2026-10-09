import { describe, it, expect } from "vitest";
import {
  applyRebalances, validateRebalance, weightsForDate, rebalanceMark, nextRebalanceTitle,
  type RuntimeRebalance, type WeightsTimelineEntry,
} from "@contracts/rebalance";

// ---- Phase 15 調倉閉環純函數回歸 ----
// 背景 bug（用戶實測發現）：批核＋調倉後 chart 無黃點——因為圖表標記係人手維護嘅第二份
// 寫死數組，而且系統根本冇「記錄調倉」呢個動作。呢組測試鎖死閉環核心邏輯。

const BASE = { VOO: 12, SMH: 10, ASHR: 8, GLD: 5, CASH: 65 } as Record<string, number>;
const TICKERS = Object.keys(BASE);
const NOW = new Date("2026-09-25T04:00:00Z"); // HKT 2026-09-25 12:00

const rec = (over: Partial<RuntimeRebalance>): RuntimeRebalance => ({
  date: "2026-09-01", title: "调仓 #4", trigger: "", note: "", recordedAt: "2026-09-01T10:00:00.000Z",
  changes: [{ etf: "VOO", from: 12, to: 13 }],
  ...over,
});

describe("applyRebalances — 生效權重 replay", () => {
  it("冇記錄時原樣返回 base（且唔會改到原對象）", () => {
    const w = applyRebalances(BASE, []);
    expect(w).toEqual(BASE);
    expect(w).not.toBe(BASE);
  });
  it("按日期順序套用 to 值；同 ticker 後記錄冚前記錄", () => {
    const w = applyRebalances(BASE, [
      rec({ date: "2026-09-10", changes: [{ etf: "VOO", from: 13, to: 14 }] }),
      rec({ date: "2026-09-01", changes: [{ etf: "VOO", from: 12, to: 13 }, { etf: "GLD", from: 5, to: 4 }] }),
    ]);
    expect(w.VOO).toBe(14);
    expect(w.GLD).toBe(4);
    expect(w.SMH).toBe(10);
  });
  it("輸入順序唔影響結果（函數內部自行排序）", () => {
    const a = applyRebalances(BASE, [rec({ date: "2026-09-01" }), rec({ date: "2026-08-20", changes: [{ etf: "SMH", from: 10, to: 11 }] })]);
    const b = applyRebalances(BASE, [rec({ date: "2026-08-20", changes: [{ etf: "SMH", from: 10, to: 11 }] }), rec({ date: "2026-09-01" })]);
    expect(a).toEqual(b);
  });
});

describe("weightsForDate — 淨值分段（收市執行，下一交易日起生效）", () => {
  const W2 = { ...BASE, VOO: 13, GLD: 4 };
  const timeline: WeightsTimelineEntry[] = [
    { from: "2026-07-20", w: BASE },
    { from: "2026-09-01", w: W2 },
  ];
  it("調倉日之前用基準權重", () => {
    expect(weightsForDate(timeline, "2026-08-31")).toEqual(BASE);
  });
  it("調倉當日仍用舊權重（收市先執行）", () => {
    expect(weightsForDate(timeline, "2026-09-01")).toEqual(BASE);
  });
  it("調倉翌日起用新權重", () => {
    expect(weightsForDate(timeline, "2026-09-02")).toEqual(W2);
    expect(weightsForDate(timeline, "2026-12-31")).toEqual(W2);
  });
  it("空 timeline 返回空對象（調用方兜底 CURRENT_WEIGHTS）", () => {
    expect(weightsForDate([], "2026-09-02")).toEqual({});
  });
});

describe("validateRebalance — 記錄前校驗", () => {
  const ok = { date: "2026-09-25", changes: [{ etf: "VOO", to: 13 }, { etf: "GLD", to: 4 }] };
  it("合法輸入通過", () => {
    expect(validateRebalance(BASE, TICKERS, [], ok, NOW)).toBeNull();
  });
  it("日期格式錯 → 拒絕", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, date: "25/09/2026" }, NOW)).toMatch("YYYY-MM-DD");
  });
  it("唔存在嘅日子（02-31）→ 拒絕（JS Date 進位漏洞回歸）", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, date: "2026-02-31" }, NOW)).toMatch("有效日子");
  });
  it("未來日期 → 拒絕（只記已執行嘅真實調倉）", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, date: "2026-09-26" }, NOW)).toMatch("未來");
  });
  it("同一日已有記錄 → 拒絕", () => {
    expect(validateRebalance(BASE, TICKERS, [rec({ date: "2026-09-25" })], ok, NOW)).toMatch("同一日");
  });
  it("未知 ticker → 拒絕", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "TSLA", to: 5 }, { etf: "VOO", to: 7 }] }, NOW)).toMatch("未知 ETF");
  });
  it("同一 changes 入面 ticker 重複 → 拒絕", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "VOO", to: 13 }, { etf: "VOO", to: 14 }] }, NOW)).toMatch("重複");
  });
  it("目標權重越界（>40 / 負數 / NaN）→ 拒絕", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "VOO", to: 41 }] }, NOW)).toMatch("0-40");
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "VOO", to: -1 }] }, NOW)).toMatch("0-40");
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "VOO", to: NaN }] }, NOW)).toMatch("0-40");
  });
  it("目標 = 現行權重（冇變動）→ 拒絕", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "VOO", to: 12 }] }, NOW)).toMatch("冇變動");
  });
  it("調後 Σ≠100 → 拒絕（真金白銀唔准憑空消失/增生）", () => {
    expect(validateRebalance(BASE, TICKERS, [], { ...ok, changes: [{ etf: "VOO", to: 13 }] }, NOW)).toMatch("必須等於 100");
  });
  it("基於「已 replay 嘅生效權重」校驗——第二記錄嘅 from 係第一記錄嘅結果", () => {
    const eff = applyRebalances(BASE, [rec({ date: "2026-09-01" })]); // VOO 已變 13
    expect(eff.VOO).toBe(13);
    expect(validateRebalance(eff, TICKERS, [rec({ date: "2026-09-01" })], { date: "2026-09-25", changes: [{ etf: "VOO", to: 13 }] }, NOW)).toMatch("冇變動");
  });
});

describe("rebalanceMark / nextRebalanceTitle — 圖表標記衍生", () => {
  it("week = MM-DD（對齊淨值圖 x 軸），label 抽 #N", () => {
    expect(rebalanceMark(rec({ date: "2026-09-25", title: "调仓 #4" }))).toEqual({ week: "09-25", label: "调仓#4" });
  });
  it("title 無 #N 時用 title 頭 8 字", () => {
    expect(rebalanceMark(rec({ title: "緊急減倉" })).label).toBe("緊急減倉");
  });
  it("標題自動編號：靜態 3 次 + runtime n 次 → 下一條係 #(4+n)", () => {
    expect(nextRebalanceTitle(3, 0)).toBe("调仓 #4");
    expect(nextRebalanceTitle(3, 2)).toBe("调仓 #6");
  });
});
