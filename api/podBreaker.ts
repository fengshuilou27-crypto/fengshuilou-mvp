/**
 * M1 Pod 熔斷（Millennium 原型，規格 research/quant-model-synthesis.md §2）
 * 共享模組：algo.ts（分析層）與 pipeline.ts（快照層=唯一可執行出口）共用同一套
 * 分組、加權回撤計算與熔斷線，避免兩層各自實作漂移。
 *
 * 機制：高相關組（pod）內持倉按權重加權的 60 日回撤 < -10% → 該組整體停止加倉；
 * 回撤回到 -6% 內解除（algo 層讀數有標注；快照層每日無狀態重算，自然滿足滯後解除）。
 * 數據缺失處理：單隻失敗從加權中剔除；整組無數據 → 保守放行（不誤鎖），與 K4 的保守邏輯一致。
 */

// S9 組合熱度分組（規格 §3）：高相關組合併計算，單組 ≤30pp；M1 沿用同一分組。
// 2026-09 重組（與 algo.ts 對齊，本模組為唯一口徑來源）：舊版「美股系」把
// VOO+XLV+XLB+SMH+EWY+EWT+VGK=42pp 全綁一組，導致該組永久超標、所有加倉被否決——按真實相關性拆組。
export const HEAT_GROUPS: { name: string; members: string[] }[] = [
  { name: "美股大盤系", members: ["VOO", "XLV"] },
  { name: "半導體韓台鏈", members: ["SMH", "EWY", "EWT"] },
  { name: "HALO重資產", members: ["XLE", "XLB", "IFRA"] },
  { name: "中國系", members: ["ASHR", "MCHI", "EWH"] },
  { name: "商品系", members: ["GLD", "SLV", "COPX"] },
  { name: "歐洲系", members: ["VGK"] },
];
export const groupOf = (t: string) => HEAT_GROUPS.find(g => g.members.includes(t))?.name ?? null;

export const POD_TRIP_LINE = -0.10; // 熔斷線：60 日加權回撤 < -10%
export const POD_RECOVER_LINE = -0.06; // 解除線：回到 -6% 內（僅供讀數標注）

// 60 日窗口回撤（小數）：最後收盤 / 窗口峰值 - 1
export function windowDD(closes: number[], win = 60): number | null {
  if (closes.length < 2) return null;
  const w = closes.slice(-win);
  const peak = Math.max(...w);
  return peak > 0 ? w[w.length - 1] / peak - 1 : null;
}

export interface PodStatus {
  podDD: Record<string, number | null>; // 各組加權回撤（小數）；整組無數據 = null
  tripped: Set<string>; // 已熔斷的組名
}

/**
 * 由各標的 60 日回撤（小數）+ 當前權重計算 pod 狀態。
 * 純函數，供單測鎖定；ddByTicker 缺值的標的從加權中剔除。
 */
export function computePodStatus(
  weights: Record<string, number>,
  ddByTicker: Record<string, number | null>,
): PodStatus {
  const podDD: Record<string, number | null> = {};
  for (const g of HEAT_GROUPS) {
    let num = 0, den = 0;
    for (const t of g.members) {
      const dd = ddByTicker[t], w = weights[t] ?? 0;
      if (dd == null || w <= 0) continue;
      num += w * dd; den += w;
    }
    podDD[g.name] = den > 0 ? num / den : null;
  }
  const tripped = new Set(HEAT_GROUPS.filter(g => (podDD[g.name] ?? 0) < POD_TRIP_LINE).map(g => g.name));
  return { podDD, tripped };
}
