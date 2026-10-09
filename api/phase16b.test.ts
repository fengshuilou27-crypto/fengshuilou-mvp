// Phase 17 測試：DB 真相源化嘅純函數——pickSnapshotFromRows（B1）/ parseRebalanceAuditRows（B2）
// 全部係純函數測試：唔掂 DB、唔掂檔案、唔寫任何真實調倉記錄。
import { describe, it, expect } from "vitest";
import { pickSnapshotFromRows, parseRebalanceAuditRows } from "./pipeline";

describe("pickSnapshotFromRows（B1：latestSnapshot kind 過濾 + payload 驗證）", () => {
  const goodSnap = JSON.stringify({ date: "2026-09-20", generatedAt: "2026-09-20T00:00:00Z", views: [], suggested: [] });

  it("空 rows → null", () => {
    expect(pickSnapshotFromRows([])).toBe(null);
  });

  it("第一行係合法快照 → 直接回", () => {
    const s = pickSnapshotFromRows([{ payload: goodSnap }]);
    expect(s?.date).toBe("2026-09-20");
    expect(Array.isArray(s?.views)).toBe(true);
  });

  it("審計行格式 {record,effective}（無 views array）→ skip 落下一行", () => {
    // 潛伏 bug 情境：舊版 kind='rebalance' 審計行成為最新行時，唔准當 Snapshot 返
    const audit = JSON.stringify({ record: { date: "2026-09-01", changes: [] }, effective: { VOO: 12 } });
    const s = pickSnapshotFromRows([{ payload: audit }, { payload: goodSnap }]);
    expect(s?.date).toBe("2026-09-20");
  });

  it("payload 唔係 JSON → skip 落下一行", () => {
    const s = pickSnapshotFromRows([{ payload: "not-json{{{" }, { payload: goodSnap }]);
    expect(s?.date).toBe("2026-09-20");
  });

  it("views 唔係 array（object/字串/缺失）→ skip", () => {
    expect(pickSnapshotFromRows([{ payload: JSON.stringify({ views: "bad" }) }])).toBe(null);
    expect(pickSnapshotFromRows([{ payload: JSON.stringify({ views: { 0: {} } }) }])).toBe(null);
    expect(pickSnapshotFromRows([{ payload: JSON.stringify({ date: "2026-09-20" }) }])).toBe(null);
  });

  it("全部行都甩格式 → null", () => {
    expect(pickSnapshotFromRows([{ payload: "x" }, { payload: "{}" }])).toBe(null);
  });

  it("有序：新→舊，首個合格者勝出（唔會攞舊嘅覆蓋新嘅）", () => {
    const newer = JSON.stringify({ date: "2026-09-20", views: [{ title: "new" }] });
    const older = JSON.stringify({ date: "2026-09-19", views: [{ title: "old" }] });
    expect(pickSnapshotFromRows([{ payload: newer }, { payload: older }])?.date).toBe("2026-09-20");
  });
});

describe("parseRebalanceAuditRows（B2：rebalance_audit rows → RuntimeRebalance[]）", () => {
  const rec = (date: string) => ({
    date, title: "測試調倉", trigger: "", note: "", recordedAt: "2026-09-01T00:00:00Z",
    changes: [{ etf: "GLD", from: 9, to: 10 }],
  });
  const wrap = (r: unknown) => ({ payload: JSON.stringify({ record: r, effective: { GLD: 10 } }) });

  it("空 rows → []", () => {
    expect(parseRebalanceAuditRows([])).toEqual([]);
  });

  it("合法行 → map 出 record（保留 asc 順序）", () => {
    const out = parseRebalanceAuditRows([wrap(rec("2026-08-01")), wrap(rec("2026-09-01"))]);
    expect(out.map(r => r.date)).toEqual(["2026-08-01", "2026-09-01"]);
    expect(out[0].changes[0]).toEqual({ etf: "GLD", from: 9, to: 10 });
  });

  it("date 唔係 YYYY-MM-DD → 該行 skip", () => {
    const bad = wrap({ ...rec("2026/09/01") });
    expect(parseRebalanceAuditRows([bad, wrap(rec("2026-09-01"))]).map(r => r.date)).toEqual(["2026-09-01"]);
  });

  it("changes 唔係 array → 該行 skip", () => {
    const bad = wrap({ ...rec("2026-09-01"), changes: "GLD" });
    expect(parseRebalanceAuditRows([bad])).toEqual([]);
  });

  it("payload 唔係 JSON / 冇 record 欄 → skip，唔 throw", () => {
    expect(parseRebalanceAuditRows([{ payload: "broken{{" }])).toEqual([]);
    expect(parseRebalanceAuditRows([{ payload: JSON.stringify({ effective: {} }) }])).toEqual([]);
    expect(parseRebalanceAuditRows([{ payload: JSON.stringify({ record: null }) }])).toEqual([]);
  });

  it("完整觀點快照行（kind='rebalance' 舊格式，冇 record 欄）唔會誤當調倉記錄", () => {
    const snapshotLike = { payload: JSON.stringify({ date: "2026-09-01", views: [], suggested: [] }) };
    expect(parseRebalanceAuditRows([snapshotLike])).toEqual([]);
  });
});
