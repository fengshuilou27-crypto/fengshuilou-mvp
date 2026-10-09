// 信號保留守衛回歸測試（2026-10-09）
// 事故原型：2026-08-01 快照有 16 條帶信號觀點；Moonshot 停擺後每日重抓產生空信號同名觀點，
// 去重「新版優先」令 08-04 快照全部歸零。守衛規則：新版空信號 + 舊版同 key 有信號 → 沿用舊信號。
import { describe, it, expect } from "vitest";
import { preserveCarriedSignals } from "../pipeline";
import type { SnapshotView } from "@contracts/types";

const mkView = (over: Partial<SnapshotView>): SnapshotView => ({
  expertId: "choi", expertName: "蔡金強", date: "2026-07-23", channel: "YouTube",
  title: "AI大泡沫？", summary: "s", url: "https://x", signals: [], decayWeight: 1, ...over,
});
const SIG = [{ asset: "半导体", direction: "bull" as const, strength: 4, note: "" }];

describe("preserveCarriedSignals", () => {
  it("新版空信號 + 舊版同 key 有信號 → 沿用舊信號並標記", () => {
    const prev = [mkView({ signals: SIG })];
    const { merged, rescued } = preserveCarriedSignals([mkView({})], prev);
    expect(rescued).toBe(1);
    expect(merged[0].signals).toEqual(SIG);
    expect(merged[0].signalCarried).toBe(true);
  });
  it("新版有信號 → 唔郁（新證據優先）", () => {
    const NEWSIG = [{ asset: "能源", direction: "bear" as const, strength: 3, note: "" }];
    const { merged, rescued } = preserveCarriedSignals([mkView({ signals: NEWSIG })], [mkView({ signals: SIG })]);
    expect(rescued).toBe(0);
    expect(merged[0].signals).toEqual(NEWSIG);
  });
  it("舊版都冇信號 → 唔救（唔編造）", () => {
    const { merged, rescued } = preserveCarriedSignals([mkView({})], [mkView({})]);
    expect(rescued).toBe(0);
    expect(merged[0].signals).toEqual([]);
  });
  it("key 唔同（日期/標題唔同）→ 唔救", () => {
    const prev = [mkView({ signals: SIG, date: "2026-07-22" })];
    const { rescued } = preserveCarriedSignals([mkView({ date: "2026-07-23" })], prev);
    expect(rescued).toBe(0);
  });
  it("舊版 horizon 保留（新版冇 horizon 時）", () => {
    const prev = [mkView({ signals: SIG, horizon: "macro" })];
    const { merged } = preserveCarriedSignals([mkView({})], prev);
    expect(merged[0].horizon).toBe("macro");
  });
});
