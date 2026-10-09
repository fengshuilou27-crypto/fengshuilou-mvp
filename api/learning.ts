// ---- 專家學習環（2026-09-12 P0）：滾動命中率 → 因子自動調整 + 跑輸診斷 ----
// 數據來源：signalBacktest（snapshots 歷史 × Yahoo 行情，6h 緩存）+ performance.json + ACWI
// 輸出：kind='learning' 快照（每日最多一行，append-only 留賬）+ 前端复盘验证頁學習卡
// 邊界：只調因子權重（夾 [0.5,1.5]、週步幅 ≤0.1、樣本不足減半），永不改規則、永不自動執行調倉。
import { readFileSync } from "node:fs";
import { getDb } from "./queries/connection";
import { snapshots } from "@db/schema";
import { desc } from "drizzle-orm";
import { signalBacktest, latestPerformance } from "./pipeline";
import { fetchCloses } from "./marketdata";
import { EXPERT_FACTOR } from "@contracts/expertWeights";
import {
  proposeFactor, classifyUnderperformance, dailyReturns, rSquared,
  type FactorProposal, type UnderperfVerdict,
} from "@contracts/learner";
import type { Snapshot } from "@contracts/types";

// 回測嘅專家歸屬係中文名（attributeExpert）；因子表用 expertId——此映射係兩者嘅橋
const NAME_TO_ID: Record<string, string> = {
  "蔡金強": "choi", "蔡金强": "choi",
  "譚新強": "tam", "谭新强": "tam",
  "洪灝": "hong", "洪灏": "hong",
  "林本利": "lambl", "林一鳴": "lamy", "莊太量": "chong", "许佳龙": "hui", "許佳龍": "hui",
  "Jurrien Timmer": "timmer", "蔡嘉民": "calvin",
};

export interface LearningDiagnosis {
  excess20dPp: number | null;
  marketRSq: number | null;
  verdict: UnderperfVerdict;
  detail: string;
}
export interface LearningReport {
  asOf: string;
  status: "ok" | "partial" | "unavailable";
  proposals: FactorProposal[];      // 每位有數據專家嘅因子提案（已過閘門）
  activeFactors: Record<string, number>; // 現行有效因子（學習快照優先，否則靜態表）
  factorsSource: "learning" | "static" | "none";
  diagnosis: LearningDiagnosis;
  note: string;
}

let cache: { at: number; data: LearningReport } | null = null;

/** 讀最新 learning 快照（7 日內有效）→ 現行動態因子 */
export async function readActiveFactors(): Promise<{ factors: Record<string, number>; source: "learning" | "static" | "none"; asOf?: string }> {
  try {
    const db = getDb();
    const rows = await db.select().from(snapshots).orderBy(desc(snapshots.id)).limit(60);
    for (const r of rows) {
      try {
        const p = JSON.parse(r.payload);
        if (p?.kind === "learningReport" && p.factors && typeof p.factors === "object") {
          const ageMs = Date.now() - new Date(p.asOf).getTime();
          if (ageMs <= 7 * 24 * 3600_000) return { factors: p.factors as Record<string, number>, source: "learning", asOf: p.asOf };
        }
      } catch { /* 非 learning 行，跳過 */ }
    }
    return { factors: { ...EXPERT_FACTOR }, source: "static" };
  } catch {
    return { factors: {}, source: "none" };
  }
}

/** 組合淨值序列（Phase 17：DB 優先、檔案鏡像 fallback）→ 20 交易日超額 vs ACWI + 60 日 R² */
async function diagnose(): Promise<{ excess20dPp: number | null; marketRSq: number | null }> {
  let port: { date: string; close: number }[] = [];
  const perfObj = await latestPerformance().catch(() => null);
  const sources = [perfObj, ...["public/data/performance.json", "dist/public/data/performance.json"].map(p => {
    try { return JSON.parse(readFileSync(p, "utf8")); } catch { return null; }
  })];
  for (const j of sources) {
    const dates: string[] = j?.dates ?? [], vals: number[] = j?.portfolio ?? [];
    if (dates.length >= 30 && dates.length === vals.length) {
      // performance.json 日期格式 MM-DD（年份隐含當年）；ACWI 係 YYYY-MM-DD——統一補年
      const yr = new Date().getFullYear();
      port = dates.map((d, i) => ({ date: d.length === 5 ? `${yr}-${d}` : d, close: vals[i] }));
      break;
    }
  }
  const acwi = await fetchCloses("ACWI", "6mo").catch(() => null);
  if (!port.length || !acwi?.length) return { excess20dPp: null, marketRSq: null };
  const last21p = port.slice(-21), last21a = acwi.slice(-21);
  const ret = (s: { close: number }[]) => (s[s.length - 1].close / s[0].close - 1) * 100;
  const excess20dPp = Math.round((ret(last21p) - ret(last21a)) * 100) / 100;
  const rsq = rSquared(dailyReturns(port.slice(-61)), dailyReturns(acwi.slice(-61)));
  return { excess20dPp, marketRSq: rsq };
}

export async function getLearningReport(): Promise<LearningReport> {
  if (cache && Date.now() - cache.at < 24 * 3600_000) return cache.data;

  const bt = await signalBacktest().catch(() => null);
  const active = await readActiveFactors();
  const proposals: FactorProposal[] = [];
  const nextFactors: Record<string, number> = { ...active.factors };

  if (bt) {
    for (const e of bt.byExpert) {
      const id = NAME_TO_ID[e.expert];
      if (!id) continue; // 複合名/媒體級條目唔入因子學習（佢哋唔屬於專家背書層）
      const prev = active.factors[id] ?? EXPERT_FACTOR[id] ?? 1.0;
      const p = proposeFactor(id, e.hitRate, e.decided, prev);
      proposals.push(p);
      nextFactors[id] = p.next;
    }
  }
  const consensus = bt?.byWindow?.find(w => w.window === 15) ?? null;
  const diag0 = await diagnose();
  const diagnosis: LearningDiagnosis = {
    ...diag0,
    ...classifyUnderperformance({
      excess20dPp: diag0.excess20dPp,
      marketRSq: diag0.marketRSq,
      expertHitRates: proposals.map(p => ({ expertId: p.expertId, hitRate: p.hitRate, decided: p.decided })),
      consensusHitRate: consensus?.hitRate ?? null,
    }),
  };

  const changed = proposals.filter(p => p.next !== p.prev);
  const asOf = new Date().toISOString();
  const status: LearningReport["status"] = bt ? "ok" : "unavailable";
  const note = `學習環 ${asOf.slice(0, 10)}：${proposals.length} 位專家有提案，${changed.length} 位因子有變（${changed.map(p => `${p.expertId} ${p.prev}→${p.next}`).join("、") || "無"}）；診斷：${diagnosis.verdict}。因子來源：${active.source}。邊界：夾 [0.5,1.5]、週步幅 ≤0.1、樣本<10 減半、永不自動執行調倉。`;

  const data: LearningReport = { asOf, status, proposals, activeFactors: nextFactors, factorsSource: active.source, diagnosis, note };

  // 每日最多寫一行 learning 快照（append-only 留賬；今日已有則跳過）
  try {
    const db = getDb();
    const rows = await db.select().from(snapshots).orderBy(desc(snapshots.id)).limit(20);
    const today = asOf.slice(0, 10);
    const hasToday = rows.some(r => {
      try { const p = JSON.parse(r.payload); return p?.kind === "learningReport" && typeof p.asOf === "string" && p.asOf.slice(0, 10) === today; } catch { return false; }
    });
    if (!hasToday) {
      const payload = JSON.stringify({ kind: "learningReport", asOf, date: today, factors: nextFactors, proposals, diagnosis, views: [], suggested: [], suggestedNote: note, brakeStatus: "ok" } satisfies Partial<Snapshot> & Record<string, unknown>);
      await db.insert(snapshots).values({ kind: "learning", payload });
    }
  } catch { /* DB 唔啱就唔寫，報告照出 */ }

  cache = { at: Date.now(), data };
  return data;
}
