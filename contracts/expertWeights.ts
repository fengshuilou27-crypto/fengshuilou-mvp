// M4 專家信號 IC 加權（Grinold 主動管理基本定律：IR = IC × √breadth）
// 前端 src/data/experts.ts 的 weightInPortfolio 已含命中率貝葉斯收縮（w×(0.7+0.6×hitRate)）；
// 本表把它折算成後端 expert_score 的乘數因子：factor = weightInPortfolio ÷ 在線專家均值，並夾在 [0.5, 1.5]，
// 避免單一專家（如蔡金強 25%）把融合分推出校準區間。
// 媒體級來源（news/scan/manual/主題掃描）不屬於專家背書，因子恒 1.0。
// 更新規則：experts.ts 調整 weightInPortfolio 後同步本表；expertId 以管道為準（lambl=林本利）。
const MEAN_ACTIVE_WEIGHT = 12.375; // 8 位在線專家 weightInPortfolio 均值（2026-07-24 快照）

export const EXPERT_FACTOR: Record<string, number> = {
  hong: 14 / MEAN_ACTIVE_WEIGHT,    // 洪灝 1.13
  choi: 25 / MEAN_ACTIVE_WEIGHT,    // 蔡金強 2.02 → 夾 1.5
  timmer: 15 / MEAN_ACTIVE_WEIGHT,  // Jurrien Timmer 1.21
  tam: 12 / MEAN_ACTIVE_WEIGHT,     // 譚新強 0.97
  lam: 14 / MEAN_ACTIVE_WEIGHT,     // 林本利 1.13
  lambl: 14 / MEAN_ACTIVE_WEIGHT,   // 管道 expertId 別名（林本利）
  lamy: 8 / MEAN_ACTIVE_WEIGHT,     // 林一鳴 0.65
  chong: 8 / MEAN_ACTIVE_WEIGHT,    // 莊太量 0.65
  hui: 3 / MEAN_ACTIVE_WEIGHT,      // 許佳龍 0.24 → 夾 0.5
  calvin: 1.0,                      // 蔡嘉民：算法層本身即其方法論，觀點不加權
};

export function expertFactor(expertId: string): number {
  const f = EXPERT_FACTOR[expertId];
  if (f == null) return 1.0; // news / scan / manual / 未知
  return Math.min(1.5, Math.max(0.5, Math.round(f * 100) / 100));
}
