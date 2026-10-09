// ---- 新主題瞭望（Open-Minded Watchlist）純函數層（2026-10-09）----
// 背景：專家講到組合冇覆蓋嘅主題（例：看好農業），舊系統會靜默丟棄（mapAsset 冇映射）。
// 呢層將呢啲信號聚合成「主題瞭望」：歸一淨分 → 配對候選 ETF（策展表，唔准 LLM 發明 ticker）
// → 交俾 screener 篩 → 得出「試倉提案」（K7 ≤2pp、人工覆核、永不自動執行）。
//
// 誠實邊界：
//   - 候選表係人工策展嘅真實 ETF（DBA/MOO/URA 等），絕唔准憑空編造代碼
//   - 睇淡（bear）主題唔出提案（本系統長倉 only），只作觀望記錄
//   - 提案唔經 LLM，係白名單規則（同 screener 判語一致）

export interface WatchTheme {
  theme: string;            // 歸一主題名（如「農業」）；冇候選表覆蓋時為「其他：原詞」
  direction: "bull" | "bear" | "mixed";
  netScore: number;         // 衰減加權淨分（同 buildSuggestions 口徑）
  supporters: string[];     // 「蔡金強(10-03)看好」式人話（最多 4 條）
  signalCount: number;
  latestDate: string;
}

// 主題 → 候選 ETF 策展表（全部真實存在、美股市場、流動性可驗證嘅 ETF；每主題最多 3 隻，按代表度排序）
export const THEME_CANDIDATES: { re: RegExp; theme: string; tickers: string[] }[] = [
  { re: /农业|農業|农产品|農產品|粮食|糧食|化肥|种业|種業/i, theme: "農業", tickers: ["DBA", "MOO", "VEGI"] },
  { re: /铀|鈾|核电|核電|核能/i, theme: "鈾/核能", tickers: ["URA", "NLR"] },
  { re: /稀土/i, theme: "稀土", tickers: ["REMX"] },
  { re: /锂|鋰|电池材料|電池材料/i, theme: "鋰/電池材料", tickers: ["LIT"] },
  { re: /天然气|天然氣/i, theme: "天然氣", tickers: ["FCG", "UNG"] },
  { re: /水资源|水資源|水务|水務/i, theme: "水資源", tickers: ["PHO", "FIW"] },
  { re: /网络安全|網絡安全|网安|信息安全|資訊安全/i, theme: "網絡安全", tickers: ["HACK", "CIBR"] },
  { re: /机器人|機器人|自动化|自動化/i, theme: "機器人/自動化", tickers: ["BOTZ", "ROBO"] },
  { re: /生物科技|生物医药|生物醫藥|创新药|創新藥/i, theme: "生物科技", tickers: ["XBI", "IBB"] },
  { re: /印度/i, theme: "印度", tickers: ["INDA", "SMIN"] },
  { re: /越南/i, theme: "越南", tickers: ["VNM"] },
  { re: /日本|日股|日经|日經/i, theme: "日本", tickers: ["EWJ", "DXJ"] },
  { re: /日圓|日元|日圆|yen/i, theme: "日圓", tickers: ["FXY"] },
  { re: /房地产|地產|REIT/i, theme: "REITs", tickers: ["VNQ", "XLRE"] },
  { re: /太空|航天|卫星|衛星/i, theme: "太空/衛星", tickers: ["UFO"] },
  { re: /碳|碳排放|碳权|碳權/i, theme: "碳權", tickers: ["KRBN"] },
  { re: /商品综合|商品綜合|大宗商品|大宗/i, theme: "商品綜合", tickers: ["PDBC", "DBC"] },
  { re: /美元/i, theme: "美元", tickers: ["UUP"] },
  { re: /通胀保值|通脹保值|TIPS/i, theme: "TIPS", tickers: ["TIP", "SCHP"] },
  // 波動率產品（UVXY/VXX 等）結構性衰減，刻意唔入表——專家講「買 VIX」都只會入觀望，唔會有候選
];

export interface WatchSignalInput {
  expertName: string; date: string; decayWeight: number;
  signals: { asset: string; direction: string; strength: number }[];
}

const r2 = (n: number) => Math.round(n * 100) / 100;

/**
 * 聚合「組合冇覆蓋」嘅信號成主題瞭望。
 * isMapped = (asset) => boolean（通常係 mapAsset(asset).length > 0）。
 * 規則：netScore = Σ dir × decayWeight × strength/5；|net| ≥0.2 先分 bull/bear，否則 mixed；
 * 唔候選表嘅主題照列（candidates 空陣列，誠實標「暫無策展工具」）。
 */
export function aggregateWatchlist(
  views: WatchSignalInput[],
  isMapped: (asset: string) => boolean,
): WatchTheme[] {
  const acc = new Map<string, WatchTheme & { _score: number }>();
  for (const v of views) {
    for (const s of v.signals ?? []) {
      if (isMapped(s.asset)) continue; // 已覆蓋主題由建議引擎處理
      const c = THEME_CANDIDATES.find(t => t.re.test(s.asset));
      const key = c ? c.theme : `其他：${s.asset.slice(0, 20)}`;
      const dir = s.direction === "bull" ? 1 : s.direction === "bear" ? -1 : 0;
      const w = (v.decayWeight ?? 0) * ((s.strength ?? 3) / 5);
      const cur = acc.get(key) ?? {
        theme: key, direction: "mixed" as const, netScore: 0, supporters: [], signalCount: 0, latestDate: v.date, _score: 0,
      };
      cur._score += dir * w;
      cur.signalCount++;
      if (v.date > cur.latestDate) cur.latestDate = v.date;
      const txt = `${v.expertName}(${v.date.slice(5)})${dir > 0 ? "看好" : dir < 0 ? "看淡" : "中性"}${s.asset}`;
      if (cur.supporters.length < 4 && !cur.supporters.includes(txt)) cur.supporters.push(txt);
      acc.set(key, cur);
    }
  }
  return [...acc.values()]
    .map(({ _score, ...t }) => ({
      ...t,
      netScore: r2(_score),
      direction: (_score >= 0.2 ? "bull" : _score <= -0.2 ? "bear" : "mixed") as WatchTheme["direction"],
    }))
    .sort((a, b) => Math.abs(b.netScore) - Math.abs(a.netScore))
    .slice(0, 5);
}

export const WATCH_PROPOSE_LINE = 0.5; // 同建議引擎 ±0.5 淨分閘一致

/**
 * 試倉提案（純規則，唔經 LLM）：
 * bull 主題 + 淨分 ≥0.5 + 篩選器畀 diversifier/substitute → 「建議試倉 +1pp」；其餘唔出提案。
 * bear/mixed 永遠唔出提案（長倉系統）；候選全部 avoid/limited → 觀望。
 */
export function watchProposal(theme: WatchTheme, bestTier: string | null): string | null {
  if (theme.direction !== "bull" || theme.netScore < WATCH_PROPOSE_LINE) return null;
  if (bestTier === "diversifier" || bestTier === "substitute") {
    return `建議試倉 +1pp（K7 小額漸進，候選經篩選器判「${bestTier === "diversifier" ? "分散器" : "替代式"}」）——須人工覆核，永不自動執行`;
  }
  return null;
}
