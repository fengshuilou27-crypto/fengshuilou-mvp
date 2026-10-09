/**
 * 融合算法引擎：Calvin 戰術層（K1-K10）× 孫子戰略層（S1-S11）× 機構量化層（M1-M5）× 專家信號管道（expert_score）
 * 規格：research/algo-spec.md §1-§4 + research/quant-model-synthesis.md（M 系列）
 * M 系列來源誠實標注：Renaissance/Citadel/Jane Street/Millennium 實盤模型全部保密，
 * 只採用公開書籍/論文/訪談可考證的方法論，並適配到「低中頻 ETF 組合」場景。
 *
 * 誠實性原則（§0，必須保留在代碼註釋）：
 * - Calvin 實盤參數明言保密（「吃飯的方法不能講」）——所有指標參數（SMA200、mom126、σ20、9日淨值均線、
 *   z=±2σ、6% 虧損預算、80 分位 regime）均為文獻標準參數，不做參數優化。
 * - Bailey/López de Prado 警告：5 年日數據最多試 ~45 個變體；本站零參數搜索，以此控制過擬合。
 * - 九地篇「投之亡地然後存」明確剔除：破釜沉舟=破產路徑，與風控公理衝突時捨棄兵法。
 *
 * 數據：Yahoo v8 chart（range=1y&interval=1d）19 持倉 ETF 日線 + public/data/performance.json 組合淨值
 * 緩存/容錯模式複用 quotes.ts：tfetch 10s、Promise.allSettled、per-ticker 失敗標記、
 * status ok/partial/unavailable、全部失敗=unavailable 不寫緩存、1 小時緩存。
 */
import { readFileSync } from "node:fs";
import { fetchCloses } from "./marketdata";
import { getDb } from "./queries/connection";
import { snapshots } from "@db/schema";
import { desc } from "drizzle-orm";
import { CURRENT_WEIGHTS, mapAsset } from "./pipeline";
import { HEAT_GROUPS, groupOf, computePodStatus, windowDD } from "./podBreaker";
import { expertFactor } from "@contracts/expertWeights";
import { ALGO_RULES_META } from "@contracts/algoRules";
import type { AlgoAnalysis, AlgoRuleState, AlgoTickerReading, Snapshot } from "@contracts/types";

const TICKERS = Object.keys(CURRENT_WEIGHTS); // 19 隻持倉 ETF
const CACHE_TTL = 60 * 60 * 1000; // 1 小時

// ---- 統計小工具 ----
const mean = (a: number[]) => a.reduce((s, x) => s + x, 0) / a.length;
const pstdev = (a: number[]) => { const m = mean(a); return Math.sqrt(mean(a.map(x => (x - m) ** 2))) };
function percentile(sortedAsc: number[], p: number): number {
  const i = (sortedAsc.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i);
  return sortedAsc[lo] + (sortedAsc[hi] - sortedAsc[lo]) * (i - lo);
}
function dailyReturns(closes: number[]): number[] {
  const r: number[] = [];
  for (let i = 1; i < closes.length; i++) if (closes[i - 1] > 0) r.push(closes[i] / closes[i - 1] - 1);
  return r;
}

// ---- 日線（雙引擎：直連 Yahoo → agent-gw 網關兜底）----
// M3（流動性閘門）需要成交量：返回收盤序列 + 20 日平均成交額（美元）
async function fetchDailyCloses(ticker: string): Promise<{ closes: number[]; adtv: number | null } | null> {
  const rows = await fetchCloses(ticker, "1y");
  if (!rows) return null;
  const clean = rows.map(r => r.close).filter(x => x > 0);
  if (clean.length < 30) return null;
  const volRows = rows.filter(r => r.close > 0 && r.volume != null && r.volume > 0).slice(-20);
  const adtv = volRows.length >= 10
    ? volRows.reduce((s, r) => s + r.close * (r.volume ?? 0), 0) / volRows.length
    : null;
  return { closes: clean, adtv };
}

interface TickerMetrics {
  price: number; sma200: number | null; mom126: number | null;
  vol20: number | null; mdd1y: number | null; zscore: number | null; trendScore: number;
}

function computeMetrics(closes: number[]): TickerMetrics {
  const n = closes.length;
  const price = closes[n - 1];
  const sma200 = n >= 200 ? mean(closes.slice(-200)) : null;
  const mom126 = n >= 127 ? price / closes[n - 127] - 1 : null;
  const rets = dailyReturns(closes);
  const vol20 = rets.length >= 20 ? pstdev(rets.slice(-20)) * Math.sqrt(252) : null;
  // MDD(1y)：整段序列峰值到谷底的最大回撤（負值小數）
  let peak = closes[0], mdd = 0;
  for (const c of closes) { if (c > peak) peak = c; const dd = c / peak - 1; if (dd < mdd) mdd = dd; }
  // 乖離 z = (price − SMA20) / σ(20日收盤價)
  let zscore: number | null = null;
  if (n >= 20) {
    const last20 = closes.slice(-20), sd = pstdev(last20);
    if (sd > 0) zscore = (price - mean(last20)) / sd;
  }
  // K1/S5：trend = 0.5×sign(price−SMA200) + 0.5×sign(mom126)；數據不足的腿記 0
  const trendScore = 0.5 * (sma200 != null ? Math.sign(price - sma200) : 0) + 0.5 * (mom126 != null ? Math.sign(mom126) : 0);
  const r2 = (x: number | null, d = 4) => (x == null ? null : Math.round(x * 10 ** d) / 10 ** d);
  return { price: Math.round(price * 100) / 100, sma200: r2(sma200, 2), mom126: r2(mom126), vol20: r2(vol20), mdd1y: r2(mdd), zscore: r2(zscore, 2), trendScore };
}

// K6：VOO 20 日已實現波動率 > 其 1 年 80 分位 → 高波動 regime
function vooRegime(closes: number[]): { regime: "normal" | "highVol"; cur: number; p80: number } | null {
  const rets = dailyReturns(closes);
  if (rets.length < 60) return null;
  const rolling: number[] = [];
  for (let i = 20; i <= rets.length; i++) rolling.push(pstdev(rets.slice(i - 20, i)) * Math.sqrt(252));
  const cur = rolling[rolling.length - 1];
  const p80 = percentile([...rolling].sort((a, b) => a - b), 0.8);
  return { regime: cur > p80 ? "highVol" : "normal", cur, p80 };
}

// ---- 組合淨值（K4 equity curve 開關 + S3 回撤狀態機）----
function readPortfolioEquity(): { nav: number; ma9: number; dd: number } | null {
  for (const p of ["public/data/performance.json", "dist/public/data/performance.json"]) {
    try {
      const j = JSON.parse(readFileSync(p, "utf8"));
      const s: number[] = j?.portfolio ?? [];
      if (s.length >= 9) {
        const nav = s[s.length - 1];
        return { nav, ma9: mean(s.slice(-9)), dd: nav / Math.max(...s) - 1 };
      }
    } catch {}
  }
  return null;
}

// ---- 專家信號層（expert_score）+ S10 冷卻（近 5 份快照建議過減倉的標的）----
async function loadExpertLayer(): Promise<{ scores: Record<string, number>; cooledDown: Set<string>; dbOk: boolean; signalCount: number }> {
  try {
    const db = getDb();
    const query = db.select().from(snapshots).orderBy(desc(snapshots.id)).limit(5);
    const rows = await Promise.race([
      query,
      new Promise<never>((_, rej) => setTimeout(() => rej(new Error("DB 查詢超時")), 5000)),
    ]);
    const scores: Record<string, number> = {};
    const cooledDown = new Set<string>();
    let signalCount = 0;
    rows.forEach((row, idx) => {
      try {
        const s = JSON.parse(row.payload) as Snapshot;
        // expert_score 只用最新一份快照的 views（decayWeight 已在管道內計算）
        if (idx === 0) {
          for (const v of s.views ?? []) {
            // M4（Grinold IC 加權）：按專家命中率收縮權重調整信號貢獻；媒體級來源因子 1.0
            const ef = expertFactor(v.expertId);
            for (const sig of v.signals ?? []) {
              const dir = sig.direction === "bull" ? 1 : sig.direction === "bear" ? -1 : 0;
              const w = (v.decayWeight ?? 0) * ((sig.strength ?? 3) / 5) * ef;
              for (const t of mapAsset(sig.asset)) { scores[t] = (scores[t] ?? 0) + dir * w; signalCount++; }
            }
          }
        }
        // S10 冷卻：近 5 份快照建議過減倉（to < from）的標的（複用 pipeline recentSuggestions 概念）
        for (const c of s.suggested ?? []) if (c.to < c.from) cooledDown.add(c.ticker);
      } catch {}
    });
    for (const t of Object.keys(scores)) scores[t] = Math.max(-1, Math.min(1, Math.round(scores[t] * 1000) / 1000));
    return { scores, cooledDown, dbOk: true, signalCount };
  } catch {
    return { scores: {}, cooledDown: new Set(), dbOk: false, signalCount: 0 };
  }
}

// S9 組合熱度分組與 M1 pod 熔斷共用定義在 ./podBreaker（2026-09 已按真實相關性重組為 6 組，
// 快照層與分析層共用同一套，避免兩層漂移）

// Phase 13 P1-8：S6 擊其惰歸加分抽出純函數（可單測）——z<−2 且 trend≥0 觸發；
// 只有正 raw（看多方向）先准 ×1.2，負 raw 放大會變成加強睇淡信號，邏輯反轉
export function applyS6Boost(raw: number, zscore: number | null, trendScore: number): number {
  const boost = zscore != null && zscore < -2 && trendScore >= 0;
  return boost && raw > 0 ? raw * 1.2 : raw;
}

// ---- 主流程（1 小時緩存 + in-flight 去重：緩存過期瞬間的並發請求共享同一次計算）----
let cache: { at: number; data: AlgoAnalysis } | null = null;
let inflight: Promise<AlgoAnalysis> | null = null;

export function getAlgoAnalysis(): Promise<AlgoAnalysis> {
  if (cache && Date.now() - cache.at < CACHE_TTL) return Promise.resolve(cache.data);
  if (inflight) return inflight;
  inflight = computeAlgoAnalysis().finally(() => { inflight = null; });
  return inflight;
}

async function computeAlgoAnalysis(): Promise<AlgoAnalysis> {
  const [settled, expert, equity] = await Promise.all([
    Promise.allSettled(TICKERS.map(fetchDailyCloses)),
    loadExpertLayer(),
    Promise.resolve(readPortfolioEquity()),
  ]);

  const closesBy: Record<string, number[]> = {};
  const adtvBy: Record<string, number | null> = {};
  const failed: string[] = [];
  settled.forEach((r, i) => {
    const v = r.status === "fulfilled" ? r.value : null;
    if (v) { closesBy[TICKERS[i]] = v.closes; adtvBy[TICKERS[i]] = v.adtv; }
    else failed.push(TICKERS[i]);
  });
  const status: AlgoAnalysis["status"] =
    failed.length === 0 ? "ok" : Object.keys(closesBy).length === 0 ? "unavailable" : "partial";
  const marketOk = status !== "unavailable";

  // 全部標的先算一次指標：M2 波動率定倉需要全組合中位波動率
  const metricsBy: Record<string, TickerMetrics> = {};
  for (const t of Object.keys(closesBy)) metricsBy[t] = computeMetrics(closesBy[t]);
  const volsAll = Object.values(metricsBy).map(x => x.vol20).filter((x): x is number => x != null).sort((a, b) => a - b);
  const medVol = volsAll.length ? percentile(volsAll, 0.5) : null;

  // M1（Millennium pod 熔斷）：各高相關組的 60 日加權回撤；< -10% → 該組整體停止加倉
  const ddByTicker: Record<string, number | null> = {};
  for (const t of Object.keys(closesBy)) ddByTicker[t] = windowDD(closesBy[t], 60);
  const { podDD, tripped: podTripped } = computePodStatus(CURRENT_WEIGHTS, ddByTicker);

  // regime（K6）：VOO 缺失時保守視為 normal 並標注
  const voo = closesBy["VOO"] ? vooRegime(closesBy["VOO"]) : null;
  const regime: AlgoAnalysis["regime"] = voo?.regime ?? "normal";

  // K4：組合淨值 < 9 日均線 → equity_gate=0.5 且否決所有加倉
  const equityGateOn = equity ? equity.nav < equity.ma9 : false;
  const portfolioDD = equity ? Math.round(equity.dd * 1000) / 10 : null; // % 單位

  // S9 熱度基準（現倉 + 本輪已承諾加倉）
  const groupHeat: Record<string, number> = {};
  for (const g of HEAT_GROUPS) groupHeat[g.name] = g.members.reduce((s, t) => s + (CURRENT_WEIGHTS[t] ?? 0), 0);

  const trendW = regime === "highVol" ? 0.7 : 0.5; // K6：高波動 regime 時 trend 權重 0.7
  const s10Vetoes: string[] = [];
  const k5Trims: string[] = [];
  const s6Hot: string[] = [];
  const caps: Record<string, number> = {};
  const m3Blocked: string[] = [];
  let m2Scaled = 0;

  const tickers: AlgoTickerReading[] = [];
  for (const t of TICKERS) {
    const closes = closesBy[t];
    if (!closes) continue;
    const m = metricsBy[t];
    const cur = CURRENT_WEIGHTS[t] ?? 0;
    const expertScore = expert.scores[t] ?? 0;
    // K3：cap_i = min(15, round(6% ÷ max(MDD_i(1y),5%) × 100 / 1.25)) pp
    const cap = m.mdd1y != null ? Math.min(15, Math.round((6 / Math.max(Math.abs(m.mdd1y) * 100, 5)) * 100 / 1.25)) : 15; // mdd1y 為負值，必須取絕對值否則 cap 恆為 15
    caps[t] = cap;

    // §1 融合公式：fused_raw = (1−trendW)×expert + trendW×trend
    let raw = (1 - trendW) * expertScore + trendW * m.trendScore;
    const gates: AlgoTickerReading["gates"] = [];
    // S6 擊其惰歸：z < −2 且 trend≥0 → 加倉加分 ×1.2 後重算 action
    const s6boost = m.zscore != null && m.zscore < -2 && m.trendScore >= 0;
    raw = applyS6Boost(raw, m.zscore, m.trendScore); // Phase 13 P1-8：負 raw 唔放大（見 applyS6Boost）
    if (equityGateOn) raw *= 0.5; // K4 全局降檔
    const fused = Math.max(0, Math.min(100, Math.round(50 + 50 * raw)));

    let action: AlgoTickerReading["action"] = "hold";
    let delta = 0;

    // K5 頂部退出（價格軌+信號軌 ETF 簡化）：浮盈（mom126 代理，無成本 basis 追蹤）≥25% 且 z≥1.5 → 止盈減 1/4
    const k5hit = m.mom126 != null && m.mom126 >= 0.25 && m.zscore != null && m.zscore >= 1.5 && cur > 0;
    if (k5hit) {
      action = "trim";
      delta = -Math.round((cur / 4) * 10) / 10;
      if (delta === 0) { action = "hold"; }
      else k5Trims.push(t);
      gates.push({ rule: "K5", passed: false, note: `浮盈代理 mom126=${((m.mom126 ?? 0) * 100).toFixed(1)}% ≥25% 且 z=${m.zscore} ≥1.5 → 止盈，減現倉 1/4` });
    } else {
      gates.push({ rule: "K5", passed: true, note: "未觸及止盈（浮盈≥25% 且 z≥1.5）" });
    }

    // S1 廟算：≥60 加倉 / ≤40 減倉 / 中間持有
    if (action === "hold") {
      if (fused >= 60) {
        let ok = true;
        // K4：equity gate 否決所有加倉
        if (equityGateOn) { ok = false; gates.push({ rule: "K4", passed: false, note: "組合淨值低於 9 日均線 → 否決所有加倉" }); }
        else gates.push({ rule: "K4", passed: true, note: "equity gate 未觸發" });
        // S6 避其銳氣：z > +2 禁追價
        if (m.zscore != null && m.zscore > 2) { ok = false; s6Hot.push(t); gates.push({ rule: "S6", passed: false, note: `z=+${m.zscore} > +2σ → 禁止追價加倉（等回踩）` }); }
        else gates.push({ rule: "S6", passed: true, note: s6boost ? `z=${m.zscore} < −2σ 且趨勢≥0 → 加分 ×1.2 已生效` : `z=${m.zscore ?? "—"}，未觸線` });
        // S9 熱度：所屬組合計 >30pp 否決
        const g = groupOf(t);
        if (g) {
          const heat = groupHeat[g];
          if (heat >= 30) { ok = false; gates.push({ rule: "S9", passed: false, note: `${g}合計 ${heat.toFixed(0)}pp > 30pp → 否決該組加倉` }); }
          else gates.push({ rule: "S9", passed: true, note: `${g}合計 ${heat.toFixed(0)}pp ≤30pp` });
          // M1 pod 熔斷：所屬組 60 日加權回撤 < -10% → 整組停止加倉
          if (podTripped.has(g)) { ok = false; gates.push({ rule: "M1", passed: false, note: `${g} pod 60日加權回撤 ${((podDD[g] ?? 0) * 100).toFixed(1)}% 跌穿 -10% → pod 熔斷，整組停止加倉` }); }
          else gates.push({ rule: "M1", passed: true, note: podDD[g] != null ? `${g} pod 60日回撤 ${(podDD[g]! * 100).toFixed(1)}%，未觸及 -10% 熔斷線` : `${g} 無持倉數據` });
        }
        // M3 流動性閘門：20 日平均成交額 < 300 萬美元 → 否決加倉
        const adtv = adtvBy[t];
        if (adtv != null && adtv < 3_000_000) { ok = false; m3Blocked.push(t); gates.push({ rule: "M3", passed: false, note: `20日平均成交額 $${(adtv / 1e6).toFixed(1)}M < $3M → 流動性不足，執行成本過高，否決加倉` }); }
        else gates.push({ rule: "M3", passed: true, note: adtv != null ? `20日平均成交額 $${(adtv / 1e6).toFixed(0)}M ≥ $3M` : "成交量數據缺失，閘門跳過（保守放行）" });
        // S10 冷卻：近 5 份快照建議過減倉的標的不得加倉
        if (expert.cooledDown.has(t)) { ok = false; s10Vetoes.push(t); gates.push({ rule: "S10", passed: false, note: "近 5 份快照曾建議減倉 → 冷卻中，禁止反向加倉" }); }
        else gates.push({ rule: "S10", passed: true, note: "無冷卻記錄" });
        // K3 倉位上限
        const room = Math.round((cap - cur) * 10) / 10;
        if (room <= 0) { ok = false; gates.push({ rule: "K3", passed: false, note: `現倉 ${cur}pp 已達 MDD 上限 ${cap}pp` }); }
        else gates.push({ rule: "K3", passed: true, note: `MDD(1y)=${m.mdd1y != null ? (m.mdd1y * 100).toFixed(1) + "%" : "—"} → 上限 ${cap}pp，餘量 ${room}pp` });
        if (ok) {
          // K7 小額漸進：首筆試倉 ≤2pp，且受 K3 餘量限制
          action = "add";
          delta = Math.min(2, room);
          // M2 波動率定倉：高波動標的試倉自動縮小（clamp 0.5~1.5，仍不超過 K3 餘量）
          const vf = medVol != null && m.vol20 != null && m.vol20 > 0 ? Math.min(1.5, Math.max(0.5, medVol / m.vol20)) : 1;
          const scaled = Math.min(room, Math.round(delta * vf * 10) / 10);
          if (scaled <= 0) {
            action = "hold"; delta = 0; ok = false;
            gates.push({ rule: "M2", passed: false, note: `波動率定倉後試倉歸零（個券 σ=${m.vol20 != null ? (m.vol20 * 100).toFixed(1) + "%" : "—"} vs 中位 ${medVol != null ? (medVol * 100).toFixed(1) + "%" : "—"}）→ 不輸出` });
          } else {
            if (scaled !== delta) { m2Scaled++; gates.push({ rule: "M2", passed: true, note: `波動率定倉：試倉 ${delta}pp × ${vf.toFixed(2)}（σ 反向縮放）= +${scaled}pp` }); }
            else gates.push({ rule: "M2", passed: true, note: `波動率接近中位水平，試倉維持 +${delta}pp` });
            delta = scaled;
            gates.push({ rule: "K7", passed: true, note: `首筆試倉 +${delta}pp（≤2pp），2 週確認後補齊` });
            if (g) groupHeat[g] += delta;
          }
        }
        gates.unshift({ rule: "S1", passed: ok, note: `廟算 fused=${fused} ≥60${ok ? " → 允許加倉" : " → 加倉被閘門否決"}` });
      } else if (fused <= 40 && cur > 0) {
        action = "reduce";
        delta = -Math.min(2, cur);
        gates.unshift({ rule: "S1", passed: true, note: `廟算 fused=${fused} ≤40 → 允許減倉` });
      } else {
        gates.unshift({ rule: "S1", passed: true, note: `廟算 fused=${fused}（40~60 之間）→ 持有（S7 不動如山）` });
      }
    } else {
      gates.unshift({ rule: "S1", passed: true, note: `廟算 fused=${fused}（止盈優先於加減倉判定）` });
    }

    tickers.push({
      ticker: t, price: m.price, sma200: m.sma200, mom126: m.mom126, vol20: m.vol20,
      mdd1y: m.mdd1y, zscore: m.zscore, trendScore: m.trendScore, expertScore,
      fusedScore: fused, action, targetDeltaPp: delta, gates,
    });
  }

  // K8 成本與容量自覺：預期收益 < 3×成本(10bps)=0.3pp 的加/減倉不輸出（止盈屬風控動作，不適用成本門檻）
  let k8Dropped = 0;
  for (const r of tickers) {
    if (r.action === "add" || r.action === "reduce") {
      const edgePp = (Math.abs(r.fusedScore - 50) / 50) * Math.abs(r.targetDeltaPp); // 預期邊際收益代理（pp）：離中性 50 越遠、幅度越大，預期收益越高
      if (edgePp < 0.3) {
        r.gates.push({ rule: "K8", passed: false, note: `預期收益代理 ${edgePp.toFixed(2)}pp < 0.3pp（3×成本）→ 不輸出` });
        r.action = "hold"; r.targetDeltaPp = 0; k8Dropped++;
      }
    }
  }
  // K8 容量：全部建議 |delta| 合計 ≤15pp，超出要截斷
  let turnover = tickers.reduce((s, r) => s + Math.abs(r.targetDeltaPp), 0);
  if (turnover > 15) {
    // Phase 13 P1-8：protect reduce——減倉/止盈屬風控動作，永遠先保留；
    // 截斷順序改為「先截多餘嘅 add（按 fusedScore 降序保留強信號）」，舊版齋按 fusedScore 排序會先犧牲 reduce（減倉 fused ≤40 排尾）
    const acts = [
      ...tickers.filter(r => r.action === "reduce" || r.action === "trim"),
      ...tickers.filter(r => r.action === "add").sort((a, b) => b.fusedScore - a.fusedScore),
    ];
    let used = 0;
    for (const r of acts) {
      const d = Math.abs(r.targetDeltaPp);
      if (used + d > 15) {
        r.gates.push({ rule: "K8", passed: false, note: `容量截斷：本輪換手已達 15pp 上限` });
        r.action = "hold"; r.targetDeltaPp = 0; k8Dropped++;
      } else used += d;
    }
    turnover = used;
  }

  const adds = tickers.filter(r => r.action === "add");
  const reduces = tickers.filter(r => r.action === "reduce");
  const trims = tickers.filter(r => r.action === "trim");
  const trendUp = tickers.filter(r => r.trendScore > 0).length;
  const na = "行情不可用，無法計算讀數";

  // ---- 每條規則的當前讀數與燈號（§4）----
  const minCapT = Object.entries(caps).sort((a, b) => a[1] - b[1])[0];
  const overCap = tickers.filter(r => caps[r.ticker] != null && (CURRENT_WEIGHTS[r.ticker] ?? 0) > caps[r.ticker]);
  const maxZ = tickers.reduce<(typeof tickers)[0] | null>((a, r) => (r.zscore != null && (a == null || (a.zscore ?? -99) < r.zscore) ? r : a), null);
  const heatStr = HEAT_GROUPS.map(g => `${g.name} ${groupHeat[g.name].toFixed(0)}pp`).join(" / ");
  const ruleState = (id: string, reading: string, lamp: AlgoRuleState["lamp"]): AlgoRuleState => {
    const meta = ALGO_RULES_META.find(m => m.id === id)!;
    return { id: meta.id, name: meta.name, origin: meta.origin, level: meta.level, confidence: meta.confidence, quote: meta.quote, source: meta.source, reading, lamp };
  };

  const rules: AlgoRuleState[] = ALGO_RULES_META.map(meta => {
    if (!meta.dataDriven) {
      const staticReading: Record<string, [string, AlgoRuleState["lamp"]]> = {
        K9: ["專家命中率動態權重已於觀點管道生效（見「專家觀點庫」）；信號源連續 3 個月負貢獻 → 權重減半。說明卡，無交易條件。", "na"],
        K10: ["本站專家觀點聚合（YouTube 完整字幕 + 全網檢索）即「別人不看的數據」。C 級哲學卡，不作交易條件。", "na"],
        S2: ["本引擎全部 27 條規則均標注 A/B/C 級與文獻/訪談出處；無出處規則不得進入——本卡即執行證據。", "pass"],
        S11: ["數據質量投入：YouTube 字幕級抓取 + Brave 全網檢索 + Yahoo 復權日線，即現代「用間」。說明卡。", "na"],
        M5: ["流程審計：全部建議永不自動執行（人工複核為唯一出口）；零參數搜索；退役條件見「方法論」頁。Renaissance 實盤保密，本站僅採用其公開流程原則。", "pass"],
        X1: ["已剔除：破釜沉舟式重倉 = 破產路徑，與 S3「先為不可勝」直接衝突。本站永遠不會輸出孤注一擲的建議。", "fail"],
      };
      const [reading, lamp] = staticReading[meta.id] ?? ["—", "na"];
      return ruleState(meta.id, reading, lamp);
    }
    // K4 / S3 只依賴 performance.json，行情層失效時仍可給真實讀數；S10 依賴 DB
    switch (meta.id) {
      case "K4":
        if (!equity) return ruleState("K4", "performance.json 不可用，equity gate 狀態未知（保守視為未觸發）", "na");
        return equityGateOn
          ? ruleState("K4", `組合淨值 ${equity.nav.toFixed(2)} 低於 9 日均線 ${equity.ma9.toFixed(2)} → equity_gate=0.5，否決所有加倉`, "fail")
          : ruleState("K4", `組合淨值 ${equity.nav.toFixed(2)} 在 9 日均線 ${equity.ma9.toFixed(2)} 上方 → 引擎正常檔位`, "pass");
      case "S3":
        if (portfolioDD == null) return ruleState("S3", "performance.json 不可用，回撤狀態機讀數未知", "na");
        return portfolioDD <= -12
          ? ruleState("S3", `組合回撤 ${portfolioDD}% 跌穿 -12% → 只留防守倉（TLT/BND/SGOV/GLD）`, "fail")
          : portfolioDD <= -8
            ? ruleState("S3", `組合回撤 ${portfolioDD}% 跌穿 -8% → 風險倉減半狀態`, "warn")
            : ruleState("S3", `組合回撤 ${portfolioDD}%（閾值 -8% / -12%），狀態機未觸發`, "pass");
      case "S10":
        if (!expert.dbOk) return ruleState("S10", "DB 不可用，冷卻記錄無法讀取", "na");
        return s10Vetoes.length > 0
          ? ruleState("S10", `冷卻否決生效：${s10Vetoes.join("、")}（近 5 份快照曾建議減倉，禁止反向加倉）`, "warn")
          : ruleState("S10", expert.cooledDown.size > 0 ? `冷卻名單：${[...expert.cooledDown].join("、")}；本輪無加倉候選撞線` : "近 5 份快照無減倉建議，無冷卻標的", "pass");
      case "M4":
        return expert.dbOk
          ? expert.signalCount > 0
            ? ruleState("M4", `expert_score 已按命中率收縮因子加權（${expert.signalCount} 個信號；因子表見 contracts/expertWeights.ts，夾 [0.5, 1.5]）`, "pass")
            : ruleState("M4", "專家層本輪無新信號（expert_score 全為 0），IC 加權無輸入", "na")
          : ruleState("M4", "DB 不可用，專家信號層失效", "na");
      default: break;
    }
    if (!marketOk) return ruleState(meta.id, na, "na");
    switch (meta.id) {
      case "K1": return ruleState("K1", `${trendUp}/${tickers.length} 隻趨勢分為正（trend = 0.5×sign(price−SMA200) + 0.5×sign(mom126)，文獻標準參數）`, "pass");
      case "K2": return ruleState("K2", regime === "highVol" ? "高波動 regime：專家/趨勢權重 30/70（趨勢 0.7）" : "專家/趨勢權重 50/50——任何單一信號源不過半", "pass");
      case "K3":
        return overCap.length > 0
          ? ruleState("K3", `最低上限 ${minCapT?.[0]} ${minCapT?.[1]}pp；⚠ ${overCap.map(r => r.ticker).join("、")} 現倉已超自身 MDD 上限（只許減不許加）`, "warn")
          : ruleState("K3", `各標的 MDD 上限 ${Math.min(...Object.values(caps))}~15pp（最低 ${minCapT?.[0]} ${minCapT?.[1]}pp）；無現倉超上限`, "pass");
      case "K5":
        return k5Trims.length > 0
          ? ruleState("K5", `止盈觸發：${k5Trims.join("、")}（浮盈≥25% 且 z≥1.5）→ 建議各減現倉 1/4`, "warn")
          : ruleState("K5", "無持倉同時滿足「浮盈≥25% 且乖離 z≥1.5」，無止盈動作", "pass");
      case "K6":
        return voo
          ? regime === "highVol"
            ? ruleState("K6", `VOO 20日波動率 ${(voo.cur * 100).toFixed(1)}% > 1年80分位 ${(voo.p80 * 100).toFixed(1)}% → 高波動 regime，reversion 類停用、趨勢權重 0.7`, "warn")
            : ruleState("K6", `VOO 20日波動率 ${(voo.cur * 100).toFixed(1)}% ≤ 1年80分位 ${(voo.p80 * 100).toFixed(1)}% → 正常 regime`, "pass")
          : ruleState("K6", "VOO 行情缺失，regime 保守視為 normal", "na");
      case "K7": return ruleState("K7", adds.length > 0 ? `${adds.length} 項加倉建議均為「首筆試倉」≤2pp（${adds.map(r => `${r.ticker} +${r.targetDeltaPp}pp`).join("、")}），2 週確認後補齊` : "本輪無新加倉信號，無試倉動作", "pass");
      case "K8":
        return k8Dropped > 0
          ? ruleState("K8", `本輪建議總換手 ${turnover.toFixed(1)}pp（上限 15pp）；${k8Dropped} 項因預期收益<0.3pp 或容量截斷被丟棄`, "warn")
          : ruleState("K8", `本輪建議總換手 ${turnover.toFixed(1)}pp ≤ 15pp 上限；無低於 3×成本（0.3pp）的建議`, "pass");
      case "S1": {
        const g60 = tickers.filter(r => r.fusedScore >= 60).length, l40 = tickers.filter(r => r.fusedScore <= 40).length;
        return ruleState("S1", `廟算分布：≥60（可議加）${g60} 隻、≤40（可議減）${l40} 隻、持有區 ${tickers.length - g60 - l40} 隻`, "pass");
      }
      case "S4": {
        const vols = tickers.map(r => r.vol20).filter((x): x is number => x != null).sort((a, b) => a - b);
        const med = vols.length ? percentile(vols, 0.5) : null;
        return ruleState("S4", med != null ? `20日年化波動率中位數 ${(med * 100).toFixed(1)}%；高波動標的的加倉幅度經 K3 上限聯動受限（w ∝ 1/σ 精神）` : "波動率數據不足", med != null ? "pass" : "na");
      }
      case "S5": return ruleState("S5", `與 K1 合併執行（200DMA + TSMOM 過濾）；${trendUp}/${tickers.length} 隻趨勢為正。TSMOM 學術證據最強（MOP 2012）`, "pass");
      case "S6":
        return s6Hot.length > 0
          ? ruleState("S6", `避銳氣生效：${s6Hot.join("、")} z > +2σ，已禁追價；最高乖離 ${maxZ?.ticker} z=+${maxZ?.zscore}`, "warn")
          : ruleState("S6", `無標的觸及 ±2σ（最高乖離 ${maxZ?.ticker ?? "—"} z=${maxZ != null && maxZ.zscore != null && maxZ.zscore >= 0 ? "+" : ""}${maxZ?.zscore ?? "—"}，未觸線）`, "pass");
      case "S7":
        return adds.length + reduces.length + trims.length === 0
          ? ruleState("S7", "無廟算通過的候選 → 本週不動（默認動作=持有）", "pass")
          : ruleState("S7", `${adds.length + reduces.length + trims.length} 項候選通過廟算與閘門，其餘 ${tickers.length - adds.length - reduces.length - trims.length} 隻不動如山`, "pass");
      case "S8": return ruleState("S8", adds.length + reduces.length > 0 ? "廟算通過+趨勢確認的候選已一次給出完整目標倉位（見融合信號表），不拆多次猶豫" : "本輪無需雷震執行的候選", "pass");
      case "S9": {
        const hot = HEAT_GROUPS.filter(g => groupHeat[g.name] > 30);
        return hot.length > 0
          ? ruleState("S9", `${heatStr}（上限 30pp）→ ${hot.map(g => g.name).join("、")}超標，該組加倉已全部否決`, "warn")
          : ruleState("S9", `${heatStr}（上限 30pp），各組熱度合規`, "pass");
      }
      case "M1": {
        const podStr = HEAT_GROUPS.map(g => `${g.name} ${podDD[g.name] != null ? (podDD[g.name]! * 100).toFixed(1) + "%" : "—"}`).join(" / ");
        return podTripped.size > 0
          ? ruleState("M1", `pod 60日加權回撤：${podStr}（熔斷線 -10%）→ ${[...podTripped].join("、")} 已熔斷，整組停止加倉（回撤回到 -6% 內解除）`, "fail")
          : ruleState("M1", `pod 60日加權回撤：${podStr}（熔斷線 -10%），各組均未觸線`, "pass");
      }
      case "M2":
        return medVol != null
          ? m2Scaled > 0
            ? ruleState("M2", `組合 20 日波動率中位數 ${(medVol * 100).toFixed(1)}%；${m2Scaled} 項試倉按 σ 反向縮放（clamp 0.5~1.5）後輸出`, "pass")
            : ruleState("M2", `組合 20 日波動率中位數 ${(medVol * 100).toFixed(1)}%；本輪無加倉候選或波動率貼近中位，無需縮放`, "pass")
          : ruleState("M2", "波動率數據不足", "na");
      case "M3": {
        const adtvs = Object.entries(adtvBy).filter(([, v]) => v != null) as [string, number][];
        if (!adtvs.length) return ruleState("M3", "成交量數據不可用（網關兜底路徑無成交量），閘門跳過", "na");
        const minA = adtvs.sort((a, b) => a[1] - b[1])[0];
        return m3Blocked.length > 0
          ? ruleState("M3", `流動性否決：${m3Blocked.join("、")}（20日平均成交額 < $3M）；全組合最低 ADTV：${minA[0]} $${(minA[1] / 1e6).toFixed(1)}M`, "warn")
          : ruleState("M3", `全部標的 20 日平均成交額 ≥ $3M；最低者 ${minA[0]} $${(minA[1] / 1e6).toFixed(1)}M——執行成本可控`, "pass");
      }
      default: return ruleState(meta.id, "—", "na");
    }
  });

  const asOf = new Date().toISOString();
  const summary = !marketOk
    ? `行情源不可用（${failed.length} 隻全部抓取失敗），規則讀數灰化；K4/S3/S10 等僅依賴本地數據的規則仍為真實讀數。下一小時自動重試。`
    : `${status === "partial" ? `部分行情缺失（${failed.join("、")}）。` : ""}regime=${regime === "highVol" ? "高波動" : "正常"}，equity gate ${equityGateOn ? "觸發（否決加倉）" : "未觸發"}，組合回撤 ${portfolioDD ?? "—"}%；本輪建議：加倉 ${adds.length} 項、減倉 ${reduces.length} 項、止盈 ${trims.length} 項，總換手 ${turnover.toFixed(1)}pp。${expert.dbOk ? (expert.signalCount > 0 ? "" : "專家層無新信號（expert_score 全為 0）。") : "專家層 DB 不可用（expert_score 按 0 處理）。"}全部規則使用文獻標準參數、未做參數優化（Bailey/López de Prado 45-變體過擬合控制）。`;

  const data: AlgoAnalysis = { asOf, status, regime, equityGateOn, portfolioDD, tickers, rules, summary };
  // 全部失敗時不寫緩存（下次請求立刻重試），複用 quotes.ts 模式
  if (status !== "unavailable") cache = { at: Date.now(), data };
  return data;
}
