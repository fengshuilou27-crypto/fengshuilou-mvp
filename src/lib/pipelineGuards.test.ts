// Phase 13 P2-11：管道守衛純函數測試（api/pipeline.ts 守衛 + api/algo.ts S6 純函數）
// 未來日期 clamp、horizon 白名單、繁體 mapping、S6 負 raw 唔放大、專家名匹配
import { describe, it, expect } from "vitest";
import { mapAsset, clampFutureDate, normalizeHorizon, matchExpertName } from "../../api/pipeline";
import { applyS6Boost } from "../../api/algo";

describe("clampFutureDate 未來日期守衛（P1-4）", () => {
  const now = new Date("2026-09-13T08:00:00Z").getTime();
  it("未來日期（>今日+1日）→ 夾返今日並觸發警告", () => {
    const warns: string[] = [];
    expect(clampFutureDate("2026-09-20", now, m => warns.push(m))).toBe("2026-09-13");
    expect(warns.length).toBe(1);
  });
  it("今日/聽日（+1日內）→ 原樣保留，唔誤殺時區邊界", () => {
    expect(clampFutureDate("2026-09-13", now, () => { throw new Error("唔應該警告"); })).toBe("2026-09-13");
    expect(clampFutureDate("2026-09-14", now, () => { throw new Error("唔應該警告"); })).toBe("2026-09-14");
  });
  it("過去日期 → 原樣保留", () => {
    expect(clampFutureDate("2026-07-20", now, () => { throw new Error("唔應該警告"); })).toBe("2026-07-20");
  });
  it("格式唔啱 → 原樣返回（交由上游格式校驗處理）", () => {
    expect(clampFutureDate("not-a-date", now, () => { throw new Error("唔應該警告"); })).toBe("not-a-date");
  });
});

describe("normalizeHorizon 白名單（P1-4）", () => {
  it("合法值原樣通過", () => {
    expect(normalizeHorizon("macro")).toBe("macro");
    expect(normalizeHorizon("theme")).toBe("theme");
    expect(normalizeHorizon("event")).toBe("event");
  });
  it("非法/缺失值一律歸 theme", () => {
    expect(normalizeHorizon("weekly")).toBe("theme");
    expect(normalizeHorizon("")).toBe("theme");
    expect(normalizeHorizon(undefined)).toBe("theme");
    expect(normalizeHorizon(null)).toBe("theme");
    expect(normalizeHorizon("MACRO")).toBe("theme"); // 大小寫唔自動寬容，歸默認
  });
});

describe("mapAsset 繁體變體（P1-7）", () => {
  const cases: [string, string[]][] = [
    ["半導體", ["SMH"]],
    ["台積電", ["EWT"]],
    ["標普500", ["VOO"]],
    ["納指", ["VOO"]],
    ["國債", ["TLT"]],
    ["美債", ["TLT"]],
    ["美债", ["TLT"]],
    ["白銀", ["SLV"]],
    ["銅價", ["COPX"]],
    ["歐洲股票", ["VGK"]],
    ["人民幣", ["ASHR"]],
    ["中國資產", ["ASHR"]],
    ["加密貨幣", ["IBIT"]],
    ["比特幣", ["IBIT"]],
    ["黃金", ["GLD"]],
    ["金銀銅", ["GLD", "SLV", "COPX"]],
    ["韓國股市", ["EWY"]],
    ["醫療保健", ["XLV"]],
    ["債券", ["BND"]],
  ];
  for (const [input, expected] of cases) {
    it(`「${input}」→ ${expected.join("+")}`, () => {
      expect(mapAsset(input)).toEqual(expected);
    });
  }
  it("無法映射 → 空數組（寧缺毋濫）", () => {
    expect(mapAsset("日圆")).toEqual([]); // prompt 例子已移除日圆——ASSET_MAP 無對應持倉工具
    expect(mapAsset("虛無縹緲")).toEqual([]);
  });
});

describe("matchExpertName 專家匹配（P1-9）", () => {
  const roster = ["蔡金強", "譚新強", "洪灝", "林本利", "林一鳴"];
  it("exact match 優先", () => {
    expect(matchExpertName("林本利", roster)).toBe("林本利");
  });
  it("雙向 includes", () => {
    expect(matchExpertName("洪灝專訪", roster)).toBe("洪灝");
    expect(matchExpertName("譚新強", roster)).toBe("譚新強");
  });
  it("複合名切開逐段試：「洪灝/林本利等(etnet专访)」標題提到林本利 → 落林本利", () => {
    const parts = "洪灝/林本利等(etnet专访)".split(/[/、,，]/).map(s => s.replace(/[（(].*$/, "").replace(/等$/, "").trim()).filter(s => s.length >= 2);
    expect(parts).toEqual(["洪灝", "林本利"]);
    expect(matchExpertName("林本利：港股下半年展望", parts)).toBe("林本利");
  });
  it("全部唔中 → null（caller 決定 fallback）", () => {
    expect(matchExpertName("素未謀面", roster)).toBeNull();
    expect(matchExpertName("", roster)).toBeNull();
  });
});

describe("applyS6Boost S6 擊其惰歸（P1-8）", () => {
  it("z<−2 且 trend≥0 且 raw>0 → ×1.2", () => {
    expect(applyS6Boost(0.4, -2.5, 0.5)).toBeCloseTo(0.48);
  });
  it("負 raw 唔准放大（否則睇淡信號邏輯反轉）", () => {
    expect(applyS6Boost(-0.4, -2.5, 0.5)).toBe(-0.4);
    expect(applyS6Boost(0, -2.5, 1)).toBe(0);
  });
  it("未觸線（z≥−2 或 trend<0）→ 原樣", () => {
    expect(applyS6Boost(0.4, -1.9, 0.5)).toBe(0.4);
    expect(applyS6Boost(0.4, -2.5, -0.5)).toBe(0.4);
    expect(applyS6Boost(0.4, null, 0.5)).toBe(0.4);
  });
});
