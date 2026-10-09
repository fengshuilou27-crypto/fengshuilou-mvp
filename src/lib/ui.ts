// 共用 UI 工具：百分比格式 + 觀點時間衰減（半衰期 21 天，與共識引擎一致）
export const HALF_LIFE = 21

// 衰减对「今天」计算（旧版按固定快照日冻结，会导致过期信号看起来仍然新鲜）
export function decay(dateStr: string) {
  const days = Math.max(0, (Date.now() - new Date(dateStr).getTime()) / 86400000)
  if (days > 90) return 0
  return Math.pow(0.5, days / HALF_LIFE)
}

export const pct = (n: number, d = 1) => `${n >= 0 ? '+' : ''}${n.toFixed(d)}%`
