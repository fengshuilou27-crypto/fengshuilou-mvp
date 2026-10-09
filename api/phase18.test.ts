// Phase 18 測試：批核即記錄嘅純函數層——buildApprovalChanges（建議→changes 過濾）+ resolveMarkWeek（黃點落位）
// 全部純函數測試：唔掂 DB、唔掂檔案、唔寫任何真實調倉記錄（真金白銀數據紅線）。
import { describe, it, expect } from "vitest";
import { buildApprovalChanges } from "./pipeline";
import { resolveMarkWeek } from "../contracts/rebalance";

describe("buildApprovalChanges（批核建議 → 調倉 changes）", () => {
  const ew = { VOO: 12, SMH: 8, GLD: 9, SGOV: 5 };

  it("正常映射：ticker→etf、保留順序", () => {
    const out = buildApprovalChanges([{ ticker: "VOO", to: 14 }, { ticker: "GLD", to: 7 }], ew);
    expect(out).toEqual([{ etf: "VOO", to: 14 }, { etf: "GLD", to: 7 }]);
  });

  it("同現行權重一樣嘅 no-op 建議會被過濾（stale 快照唔阻塞批核）", () => {
    const out = buildApprovalChanges([{ ticker: "VOO", to: 12 }, { ticker: "GLD", to: 10 }], ew);
    expect(out).toEqual([{ etf: "GLD", to: 10 }]);
  });

  it("重複 ticker 首個勝出", () => {
    const out = buildApprovalChanges([{ ticker: "VOO", to: 14 }, { ticker: "VOO", to: 15 }], ew);
    expect(out).toEqual([{ etf: "VOO", to: 14 }]);
  });

  it("全部 no-op → 空數組（上層行 no-suggestions 路徑）", () => {
    expect(buildApprovalChanges([{ ticker: "VOO", to: 12 }], ew)).toEqual([]);
  });

  it("空建議 → 空數組", () => {
    expect(buildApprovalChanges([], ew)).toEqual([]);
  });

  it("建議含 effective 冇嘅 ticker → 照留（後續 validateRebalance 白名單把關拒絕）", () => {
    const out = buildApprovalChanges([{ ticker: "QQQ", to: 3 }], ew);
    expect(out).toEqual([{ etf: "QQQ", to: 3 }]);
  });
});

describe("resolveMarkWeek（黃點落位：記錄日唔一定有淨值點）", () => {
  const weeks = ["09-22", "09-23", "09-24", "09-25"]; // 周一至周五（09-25 周五收市點）

  it("exact 命中直接返", () => {
    expect(resolveMarkWeek("09-24", weeks)).toBe("09-24");
  });

  it("周六記錄 → 落位周五（上一交易日收市點，語義=該收市後生效）", () => {
    expect(resolveMarkWeek("09-26", weeks)).toBe("09-25");
  });

  it("周日記錄 → 落位周五", () => {
    expect(resolveMarkWeek("09-27", weeks)).toBe("09-25");
  });

  it("記錄日晚過最新淨值日（當日未收市）→ 暫落最後一點，收市追加後 exact 命中自動接管", () => {
    expect(resolveMarkWeek("09-28", weeks)).toBe("09-25");
  });

  it("記錄日早過全部淨值日 → 最早嘅晚於日", () => {
    expect(resolveMarkWeek("09-21", weeks)).toBe("09-22");
  });

  it("空淨值序列 → null（唔渲染好過渲染錯位）", () => {
    expect(resolveMarkWeek("09-26", [])).toBe(null);
  });
});
