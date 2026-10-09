// 新主題瞭望純函數回歸測試（2026-10-09）
// 鎖死口徑：未覆蓋信號聚合、主題歸一、方向分檔、bear 唔出提案、候選表唔准發明、排序截斷。
import { describe, it, expect } from "vitest";
import { aggregateWatchlist, watchProposal, THEME_CANDIDATES, type WatchTheme, type WatchSignalInput } from "@contracts/watchlist";

const MAPPED = ["SMH", "GLD"]; // 假裝組合只有 SMH/GLD 兩個映射
const isMapped = (a: string) => /半导体|半導體|黄金|黃金/.test(a);

const view = (asset: string, direction: string, over: Partial<WatchSignalInput> = {}): WatchSignalInput => ({
  expertName: "蔡金強", date: "2026-10-03", decayWeight: 1,
  signals: [{ asset, direction, strength: 5 }], ...over,
});

describe("aggregateWatchlist", () => {
  it("已覆蓋主題唔入瞭望（交返俾建議引擎）", () => {
    const r = aggregateWatchlist([view("半导体", "bull")], isMapped);
    expect(r.length).toBe(0);
  });
  it("未覆蓋主題歸一 + 淨分聚合", () => {
    const r = aggregateWatchlist([
      view("农业", "bull"), view("農產品", "bull", { expertName: "洪灝", date: "2026-10-05" }),
    ], isMapped);
    expect(r.length).toBe(1);
    expect(r[0].theme).toBe("農業");
    expect(r[0].direction).toBe("bull");
    expect(r[0].netScore).toBe(2);
    expect(r[0].supporters.length).toBe(2);
  });
  it("多空對沖 → mixed", () => {
    const r = aggregateWatchlist([view("农业", "bull"), view("農業", "bear")], isMapped);
    expect(r[0].direction).toBe("mixed");
  });
  it("無候選表主題歸「其他：原詞」", () => {
    const r = aggregateWatchlist([view("秘鲁铜矿罷工概念股", "bull")], isMapped);
    expect(r[0].theme.startsWith("其他：")).toBe(true);
  });
  it("候選表全部係真實 ETF 代碼格式（1-5 大階字母）", () => {
    for (const c of THEME_CANDIDATES) for (const t of c.tickers) expect(t).toMatch(/^[A-Z]{1,5}$/);
  });
  it("最多列 5 個主題，按 |淨分| 降序", () => {
    const views = ["农业", "铀", "稀土", "印度", "越南", "日本", "水资源"].map(a => view(a, "bull"));
    const r = aggregateWatchlist(views, isMapped);
    expect(r.length).toBeLessThanOrEqual(5);
    expect(Math.abs(r[0].netScore)).toBeGreaterThanOrEqual(Math.abs(r[r.length - 1].netScore));
  });
});

describe("watchProposal 閘門", () => {
  const bull: WatchTheme = { theme: "農業", direction: "bull", netScore: 0.8, supporters: [], signalCount: 2, latestDate: "2026-10-05" };
  it("bull + 淨分過閘 + diversifier → 出試倉提案", () => {
    expect(watchProposal(bull, "diversifier")).toContain("+1pp");
  });
  it("bull + 候選 avoid → 唔出提案", () => {
    expect(watchProposal(bull, "avoid")).toBeNull();
  });
  it("bear 主題永遠唔出提案（長倉系統）", () => {
    expect(watchProposal({ ...bull, direction: "bear", netScore: -1.2 }, "diversifier")).toBeNull();
  });
  it("淨分未過 0.5 閘 → 唔出提案", () => {
    expect(watchProposal({ ...bull, netScore: 0.4 }, "diversifier")).toBeNull();
  });
});
