import { describe, it, expect } from "vitest";
import { HEAT_GROUPS, groupOf, windowDD, computePodStatus, POD_TRIP_LINE, POD_RECOVER_LINE } from "../podBreaker";

describe("podBreaker 分組定義", () => {
  it("19 隻持倉中的高相關組成員歸屬正確", () => {
    expect(groupOf("SMH")).toBe("半導體韓台鏈");
    expect(groupOf("VOO")).toBe("美股大盤系");
    expect(groupOf("XLE")).toBe("HALO重資產");
    expect(groupOf("ASHR")).toBe("中國系");
    expect(groupOf("SLV")).toBe("商品系");
    expect(groupOf("IBIT")).toBeNull(); // 不屬於任何 pod → 不受 M1 約束
    expect(groupOf("SGOV")).toBeNull();
  });
  it("熔斷線與解除線常數鎖定（Millennium 報道值適配）", () => {
    expect(POD_TRIP_LINE).toBe(-0.10);
    expect(POD_RECOVER_LINE).toBe(-0.06);
    expect(HEAT_GROUPS.map(g => g.name)).toEqual(["美股大盤系", "半導體韓台鏈", "HALO重資產", "中國系", "商品系", "歐洲系"]);
  });
});

describe("windowDD（60 日窗口回撤）", () => {
  it("峰值後下跌 → 負回撤", () => {
    const closes = [100, 120, 90]; // 峰值 120，現價 90 → -25%
    expect(windowDD(closes)).toBeCloseTo(-0.25, 6);
  });
  it("現價即峰值 → 0", () => {
    expect(windowDD([100, 110, 120])).toBeCloseTo(0, 6);
  });
  it("窗口只取最後 60 日：早期更深的跌不計", () => {
    const early = [200, 50]; // 早期暴跌 -75%
    const recent = Array.from({ length: 60 }, (_, i) => 100 + i * 0.1); // 近期單邊上行
    expect(windowDD([...early, ...recent], 60)).toBeCloseTo(0, 6);
  });
  it("數據不足 → null", () => {
    expect(windowDD([])).toBeNull();
    expect(windowDD([100])).toBeNull();
  });
});

describe("computePodStatus（M1 加權熔斷）", () => {
  const weights = { GLD: 10, SLV: 5, COPX: 3, VOO: 30, SMH: 8 };

  it("加權回撤按持倉權重計算", () => {
    // 商品系：GLD -15%×10 + SLV -39%×5 + COPX 0%×3 → (-150-195)/18 ≈ -19.17%
    const { podDD, tripped } = computePodStatus(weights, { GLD: -0.15, SLV: -0.39, COPX: 0, VOO: 0.02, SMH: -0.05 });
    expect(podDD["商品系"]).toBeCloseTo((-0.15 * 10 + -0.39 * 5) / 18, 6);
    expect(tripped.has("商品系")).toBe(true);
    expect(tripped.has("美股大盤系")).toBe(false);
    expect(tripped.has("半導體韓台鏈")).toBe(false);
    expect(tripped.has("中國系")).toBe(false); // 無持倉 → null → 不觸發
  });

  it("整組加權回撤 -9.9% 不觸發、-10.1% 觸發（邊界鎖定）", () => {
    const mk = (dd: number) => computePodStatus({ GLD: 10 }, { GLD: dd });
    expect(mk(-0.099).tripped.size).toBe(0);
    expect(mk(-0.101).tripped.has("商品系")).toBe(true);
  });

  it("單隻失敗從加權剔除，不影響其餘成員判定", () => {
    // SLV 失敗(null) → 商品系只剩 GLD -15%×10 + COPX 0%×3 → -11.5% 仍觸發
    const { podDD, tripped } = computePodStatus(weights, { GLD: -0.15, SLV: null, COPX: 0 });
    expect(podDD["商品系"]).toBeCloseTo(-1.5 / 13, 6);
    expect(tripped.has("商品系")).toBe(true);
  });

  it("整組無數據 → null 且保守放行（不誤鎖）", () => {
    const { podDD, tripped } = computePodStatus(weights, { GLD: null, SLV: null, COPX: null });
    expect(podDD["商品系"]).toBeNull();
    expect(tripped.size).toBe(0);
  });

  it("零權重標的不計入加權（非持倉不影響 pod）", () => {
    const w = { GLD: 10, SLV: 0 }; // SLV 零持倉
    const { podDD } = computePodStatus(w, { GLD: -0.05, SLV: -0.50 });
    expect(podDD["商品系"]).toBeCloseTo(-0.05, 6);
  });
});
