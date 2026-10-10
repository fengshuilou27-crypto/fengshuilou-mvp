// 每日观点更新管道
// 流程：YouTube Data API 拉取追踪频道新视频 → Kimi(LLM) 结构化为「资产×方向×强度」信号
//      → 时间衰减(半衰期21天) → 生成建议调仓(待人工复核) → 写入 DB + public/data/snapshot.json
import { writeFileSync, mkdirSync, readFileSync } from "node:fs";
import { fetchCloses, gwDatasourceCall, csvToRecords } from "./marketdata";
import { getDb } from "./queries/connection";
import { snapshots, pipelineRuns } from "@db/schema";
import { desc, asc, inArray } from "drizzle-orm";
import type { Snapshot, SnapshotView, SnapshotSignal, SuggestedChange, PipelineStatus, WatchlistItem } from "@contracts/types";
import { computePerfStats } from "@contracts/perfStats";
import { BT_WINDOWS, evalWindows, aggregateWindow, aggregateExpert, type BtCells, type BtWindowAgg } from "@contracts/backtest";
import { applyRebalances, validateRebalance, weightsForDate, nextRebalanceTitle, type RuntimeRebalance, type WeightsTimelineEntry } from "@contracts/rebalance";
import { computePodStatus, groupOf } from "./podBreaker";
import { screenCandidateEtf } from "./screener";
import { aggregateWatchlist, watchProposal, THEME_CANDIDATES, WATCH_PROPOSE_LINE } from "@contracts/watchlist";

const YT_KEY = process.env.YOUTUBE_API_KEY ?? "";
const KIMI_KEY = process.env.KIMI_API_KEY ?? "";
const KIMI_BASE = process.env.KIMI_BASE_URL ?? "https://api.moonshot.cn/v1";
// Phase 14：兩站 key 互不通用（platform.moonshot.cn vs platform.moonshot.ai）——fallback 預設 .cn 站；
// 若用 .ai 站 key 而漏設 KIMI_BASE_URL，全部調用會靜默 401。開機響亮提示一次。
if (!process.env.KIMI_BASE_URL) {
  console.warn("[pipeline] ⚠ KIMI_BASE_URL 未設置，fallback 至 https://api.moonshot.cn/v1——若你嘅 key 來自 platform.moonshot.ai，請喺 .env 設 KIMI_BASE_URL=https://api.moonshot.ai/v1，否則 Kimi 通道會全部 401");
}
// 結構化模型：可用 .env KIMI_MODEL 覆蓋；平台會下架舊模型（如 kimi-k2-0711-preview 已 404），故設回退鏈並緩存可用者
// Phase 13 P0-1：kimi-k2.5 及全系列 moonshot-v1（含 moonshot-v1-auto / moonshot-v1-32k-vision-preview）
// 已於 2026-08-31 日落退役，call 佢哋會報錯——候選鏈改為 kimi-k2.6 → kimi-k3
const KIMI_MODEL_CANDIDATES = [process.env.KIMI_MODEL ?? "", "kimi-k2.6", "kimi-k3"]
  .filter((m, i, a) => m && a.indexOf(m) === i);
let workingKimiModel: string | null = null;

// Phase 13 P0-1：共享模型 resolver——所有 Kimi 調用（聯網搜索 / netCheck 探針）統一經佢攞可用模型。
// 首次成功後記住（module-level 緩存）；失敗時逐個候選試；全部失敗 → 響亮報警 + return null，caller 優雅降級。
async function resolveKimiModel(): Promise<string | null> {
  if (workingKimiModel) return workingKimiModel;
  if (!KIMI_KEY) return null;
  for (const model of KIMI_MODEL_CANDIDATES) {
    try {
      const r = await tfetch(`${KIMI_BASE}/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${KIMI_KEY}` },
        body: JSON.stringify({ model, messages: [{ role: "user", content: "ping" }], max_tokens: 1 }),
      }, 15000);
      if (r.ok) { workingKimiModel = model; return model; }
      console.log(`[pipeline] resolveKimiModel: ${model} → HTTP ${r.status}，試下一個候選`);
    } catch (e: any) {
      console.log(`[pipeline] resolveKimiModel: ${model} 網絡錯誤（${e.message?.slice(0, 80) ?? "timeout"}），試下一個候選`);
    }
  }
  console.log("[pipeline] ⚠ resolveKimiModel: 全部候選模型（KIMI_MODEL/kimi-k2.6/kimi-k3）調用失敗——Kimi 本輪不可用，相關通道降級");
  return null;
}

// Phase 13 P1-4：未來日期守衛——來源日期晚過今日+1日視為唔可靠，夾返今日並響亮記錄（唔准靜默）
export function clampFutureDate(dateStr: string, now: number = Date.now(), warn: (msg: string) => void = m => console.log("[pipeline]", m)): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
  if (new Date(dateStr + "T00:00:00Z").getTime() > now + 86400000) {
    warn(`⚠ 日期守衛：來源日期 ${dateStr} 喺未來（超過今日+1日），已夾返今日——原始日期唔可靠`);
    return new Date(now).toISOString().slice(0, 10);
  }
  return dateStr;
}

// Phase 13 P1-4：horizon 白名單——LLM/外部輸入嘅 horizon 只認 macro|theme|event，其餘一律歸 theme
export function normalizeHorizon(h: string | null | undefined): "macro" | "theme" | "event" {
  return h === "macro" || h === "theme" || h === "event" ? h : "theme";
}

// Phase 14：觀點去重 key——Wind 等來源 URL 帶隨機防緩存參數（useless=0.xxx，每次抓取都唔同），
// raw `url|title` 去重形同虛設，令同一篇新聞每輪管道當新觀點再入庫 + 舊版被 carry，
// 重複線性增長並重複計入共識分/建議/回測。改用「專家|正規化標題|日期」三件套：
// 同一來源同一篇內容三件套必然一致，與 URL 參數完全無關。
export function dedupeKey(v: Pick<SnapshotView, "expertName" | "title" | "date">): string {
  const t = (v.title ?? "").replace(/\s+/g, " ").trim();
  return `${(v.expertName ?? "").trim()}|${t}|${(v.date ?? "").slice(0, 10)}`;
}

// ---- 信號保留守衛（2026-10-09 根因修復）----
// 事故：Kimi 結構化失敗時，重抓產生「信號為空」嘅同名觀點；去重「新版優先」會將
// 舊版有信號嘅觀點覆蓋成空殼——2026-08-01 → 08-04 間 16 條帶信號觀點因此被清空。
// 規則：新觀點 signals 為空 + 舊快照同 key 觀點有信號 → 沿用舊信號（標 signalCarried），唔准清空。
export function preserveCarriedSignals<T extends SnapshotView>(newViews: T[], prevViews: SnapshotView[]): { merged: T[]; rescued: number } {
  const prevByKey = new Map<string, SnapshotView>();
  for (const v of prevViews) if (v.signals?.length) prevByKey.set(dedupeKey(v), v);
  let rescued = 0;
  const merged = newViews.map(v => {
    if (v.signals?.length) return v;
    const prev = prevByKey.get(dedupeKey(v));
    if (!prev) return v;
    rescued++;
    return { ...v, signals: prev.signals, horizon: v.horizon ?? prev.horizon, signalCarried: true } as T;
  });
  return { merged, rescued };
}

// Phase 13 P1-9：專家名匹配——先 exact match → 再雙向 includes → 複合名按 /、,、（ 切開逐段試，
// 全部唔中先 return null（caller 決定 fallback）。修復「洪灝/林本利等(etnet专访)」永遠 find-first 落喺洪灝嘅問題。
export function matchExpertName(name: string, candidates: string[]): string | null {
  const n = name.trim();
  if (!n || !candidates.length) return null;
  const exact = candidates.find(c => c.trim() === n);
  if (exact) return exact;
  const incl = candidates.find(c => { const c2 = c.trim(); return c2.includes(n) || n.includes(c2); });
  if (incl) return incl;
  for (const part of n.split(/[/、,，(（]/).map(s => s.trim()).filter(s => s.length >= 2)) {
    const hit = candidates.find(c => { const c2 = c.trim(); return c2 === part || c2.includes(part) || part.includes(c2); });
    if (hit) return hit;
  }
  return null;
}

// 所有外部调用统一超时（无超时 = 管道卡死的根因）
async function tfetch(url: string, opts: RequestInit = {}, ms = 15000): Promise<Response> {
  return fetch(url, { ...opts, signal: AbortSignal.timeout(ms) });
}

// 网络能力探测：环境出口受限时（如沙盒只放行 Kimi 系域名），一次性探测后整段跳过，
// 避免每个源白烧 15 秒超时（实测沙盒 YouTube×5 + Brave×7 = 浪费约 3 分钟）
async function probeHost(url: string, ms = 4000): Promise<boolean> {
  try { await tfetch(url, { method: "HEAD" }, ms); return true; } catch { return false; }
}
// 信息半衰期按信号视野分级（参考 Alpha Architect 信息衰减研究：宏观/价值信号衰减慢、动量/事件信号衰减快）
const HALF_LIFE_BY_HORIZON: Record<string, number> = { macro: 45, theme: 21, event: 7 };
const LOOKBACK_DAYS = 45;

// 追踪频道（handle → 专家）；multi=true 為多專家訪談頻道——逐條片按標題歸因（EXPERT_TITLE_MATCH）
const CHANNELS: { handle?: string; channelId?: string; expertId: string; expertName: string; multi?: boolean }[] = [
  { handle: "@octalk999", expertId: "choi", expertName: "蔡金強" },
  { handle: "@SunChannelHK", expertId: "tam", expertName: "譚新強" },
  // Phase 19e：etnet 改 multi——用戶 2026-10-06 提醒「呢個渠道經常有相關專家觀點」。
  // 舊模式成個頻道歸「洪灝/林本利等」一格，莊太量/許佳龍等 etnet 常客嘅片會錯歸洪灝；
  // multi 模式逐條按標題歸因（EXPERT_TITLE_MATCH 含洪灝/林本利/莊太量/許佳龍等 8 人），唔中即跳過。
  { handle: "@etnethk", expertId: "multi", expertName: "etnet 專訪（洪灝/林本利/莊太量等）", multi: true }, // 官方頻道 handle 係 @etnethk（@etnetTV 係錯誤 handle，導致洪灝專訪長期漏抓——2026-09-06 用戶發現）
  { handle: "@Fidelity", expertId: "timmer", expertName: "Jurrien Timmer(Fidelity)" },
  { handle: "@metroradiohk", expertId: "lamy", expertName: "林一鳴等(新城财经台)" },
  // Phase 16：多專家訪談頻道——片標題含追蹤專家名先入庫，唔中即跳過（唔好畀不相關片污染觀點庫）
  { handle: "@Invest4good", expertId: "multi", expertName: "Invest for Good 訪談", multi: true },
  { channelId: "UCcAkhVZQVpqNtT9fUdkAJBQ", handle: "@大师说-j6k", expertId: "multi", expertName: "大師說精選", multi: true },
  // Phase 19c：用戶指定——呢個頻道大量洪灝相關片（2026-10-06 用戶提供），每輪管道必須觸及
  { handle: "@jiedu369", expertId: "multi", expertName: "jiedu369 訪談（洪灝等）", multi: true },
];
// ⚠ 頻道清單 = 用戶歷來指定嘅全部來源，每輪管道必逐個觸及（2026-10-06 用戶明確要求「牢牢記住」）：
// @octalk999（蔡金強）、UCcAkhVZQVpqNtT9fUdkAJBQ/@大师说-j6k（大師說/蔡金強精選）、@jiedu369（洪灝等）、
// @SunChannelHK（譚新強）、@etnethk（洪灝/林本利/莊太量等，19e 起 multi 按標題歸因）、@Fidelity（Timmer）、@metroradiohk（林一鳴）、@Invest4good。
// 加新專家/新頻道只准加唔准刪；刪除要用戶明確指示。

// Phase 16：多專家頻道標題匹配表（有序，首命中即停；i flag 兼顧大小寫，繁簡變體並列）
export const EXPERT_TITLE_MATCH: [RegExp, { expertId: string; expertName: string }][] = [
  [/洪灝|洪灏|洪視全球|洪视全球/i, { expertId: "hong", expertName: "洪灝" }], // Phase 19e：補《洪視全球》（洪灝 etnet 欄目）——防標題冇「洪灝」字時漏歸因
  [/蔡金強|蔡金强/i, { expertId: "choi", expertName: "蔡金強" }],
  [/Jurrien Timmer|Timmer/i, { expertId: "timmer", expertName: "Jurrien Timmer(Fidelity)" }],
  [/譚新強|谭新强/i, { expertId: "tam", expertName: "譚新強" }],
  [/林本利/i, { expertId: "lam", expertName: "林本利" }],
  [/林一鳴|林一鸣/i, { expertId: "lamy", expertName: "林一鳴" }],
  [/莊太量|庄太量/i, { expertId: "chong", expertName: "莊太量" }],
  [/許佳龍|许佳龙/i, { expertId: "hui", expertName: "許佳龍" }],
];

export function matchExpertByTitle(title: string): { expertId: string; expertName: string } | null {
  for (const [re, e] of EXPERT_TITLE_MATCH) if (re.test(title)) return e;
  return null;
}

// 当前生效权重（2026-07-20 调仓后）——建议引擎以此为基准
// 定義已移至 contracts/rebalance.ts（葉子模組），此處 re-export 保持 API 兼容
import { CURRENT_WEIGHTS, LAST_REBALANCE_DATE } from "@contracts/rebalance";
export { CURRENT_WEIGHTS, LAST_REBALANCE_DATE };

// ---- Phase 17：DB 係唯一真相源，檔案降級做 build-time 種子 + 本地開發鏡像 ----
// 背景：發布容器文件系統係 ephemeral——容器一回收，runtime 寫入嘅 public/data/*.json
// 全部還原返 image 烘入時刻。所以快照/調倉記錄/淨值一律以 DB 為準，檔案只係鏡像。
// 快照 kind 白名單：rebalance_audit（調倉審計行，payload={record,effective}）同
// performance（淨值鏡像）唔係觀點快照——所有「攞最新快照」查詢必須過濾，
// 否則會將錯誤格式嘅 payload 當 Snapshot 返（潛伏 bug，詳見 HANDOVER Phase 17）。
// 'dedupe' 係 Phase 14 一次性清理腳本遺留嘅完整快照格式（scripts/dedupe-snapshot.ts），同屬觀點快照
const SNAPSHOT_KINDS = ["daily", "manual", "rebalance", "dedupe"] as const;
const snapshotKindFilter = () => inArray(snapshots.kind, [...SNAPSHOT_KINDS]);

// 純函數（俾測試）：由新→舊 rows 揀第一份 parse 到且 views 係 array 嘅快照，冇就 null
export function pickSnapshotFromRows(rows: { payload: string }[]): Snapshot | null {
  for (const r of rows) {
    try {
      const s = JSON.parse(r.payload) as Snapshot;
      if (s && typeof s === "object" && Array.isArray(s.views)) return s;
    } catch { /* 格式唔啱就 skip 落下一行 */ }
  }
  return null;
}

// ---- Phase 15：調倉閉環——runtime 調倉記錄（用戶喺券商真實執行後喺網站記錄） ----
// Phase 17：DB（snapshots kind='rebalance_audit' 行）係真相源；public/data/rebalances.json
//（+ dist 鏡像）只係本地開發/zip 鏡像。生效權重 = CURRENT_WEIGHTS + 記錄 replay。
// 鐵律不變：建議永遠唔自動執行——呢度只記錄「人已經做咗」嘅動作，唔會幫用戶落單。
const REBALANCES_FILE = "public/data/rebalances.json";

// 檔案鏡像讀取（sync；本地開發/boot 同步/DB 甩底 fallback 用）
function listRuntimeRebalancesFromFile(): RuntimeRebalance[] {
  try {
    if (!existsSync2(REBALANCES_FILE)) return [];
    const j = JSON.parse(readFileSync2(REBALANCES_FILE));
    const arr = j?.records;
    if (!Array.isArray(arr)) return [];
    return arr.filter((r: any) => r && /^\d{4}-\d{2}-\d{2}$/.test(r.date) && Array.isArray(r.changes));
  } catch (e: any) {
    console.warn("[pipeline] ⚠ rebalances.json 讀取失敗（當無 runtime 調倉處理）:", e?.message ?? e);
    return [];
  }
}

// 純函數（俾測試）：kind='rebalance_audit' rows → RuntimeRebalance[]，
// 逐條過 Phase 15 格式校驗（date YYYY-MM-DD、changes array），甩格式嘅行 skip
export function parseRebalanceAuditRows(rows: { payload: string }[]): RuntimeRebalance[] {
  const out: RuntimeRebalance[] = [];
  for (const r of rows) {
    try {
      const rec = JSON.parse(r.payload)?.record;
      if (rec && /^\d{4}-\d{2}-\d{2}$/.test(rec.date) && Array.isArray(rec.changes)) out.push(rec);
    } catch { /* 甩格式 skip */ }
  }
  return out;
}

// DB 版讀取：甩底（連線失敗等）回 null（俾 caller fallback 檔案），零行回 []
async function listRuntimeRebalancesFromDb(): Promise<RuntimeRebalance[] | null> {
  try {
    const db = getDb();
    const rows = await db.select().from(snapshots)
      .where(eq(snapshots.kind, "rebalance_audit"))
      .orderBy(asc(snapshots.id));
    return parseRebalanceAuditRows(rows);
  } catch (e: any) {
    console.warn("[pipeline] ⚠ 調倉記錄 DB 讀取失敗（fallback 檔案鏡像）:", e?.message ?? e);
    return null;
  }
}

// Phase 17：DB 優先——DB 有 audit 行就以 DB 為準；DB 甩底/零行 → fallback 檔案鏡像
export async function listRuntimeRebalances(): Promise<RuntimeRebalance[]> {
  const dbRows = await listRuntimeRebalancesFromDb();
  if (dbRows && dbRows.length) return dbRows;
  return listRuntimeRebalancesFromFile();
}

// 現行生效權重 = 靜態基準 + runtime 記錄 replay（建議引擎/淨值追蹤/前端餅圖同一口徑）
// Phase 17：呢兩個 sync helper 用檔案鏡像——recordRebalance 會雙寫 DB+檔案、
// boot 時亦會由 DB 覆寫檔案，所以檔案鏡像同 DB 真相保持一致（sync 唔可以 await DB）。
export function effectiveWeights(): Record<string, number> {
  return applyRebalances(CURRENT_WEIGHTS, listRuntimeRebalancesFromFile());
}

export function effectiveLastRebalanceDate(): string {
  let d = LAST_REBALANCE_DATE;
  for (const r of listRuntimeRebalancesFromFile()) if (r.date > d) d = r.date;
  return d;
}

function writeJsonBothDirs(filename: string, json: string, staleWarn: string): void {
  for (const dir of ["public/data", "dist/public/data"]) {
    try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/${filename}`, json); }
    catch (e: any) { console.warn(`[pipeline] ⚠ ${filename} 寫入 ${dir} 失敗（${staleWarn}）:`, e?.message ?? e); }
  }
}

// 記錄真實調倉：校驗（基於 DB 記錄）→ DB kind='rebalance_audit' 審計行（真相源）+ 檔案雙寫（鏡像）
// → 淨值 timeline 加分段 → 即場追加淨值
// → 按新權重重跑建議引擎（已執行嘅建議唔應該再掛住）→ 快照落 kind="rebalance"（完整觀點快照，保留）。
// dryRun=true 只校驗 + 回預覽，乜都唔寫（前端「檢查」掣 / E2E 測試用）。
export async function recordRebalance(input: {
  date: string; title?: string; trigger?: string; note?: string;
  changes: { etf: string; to: number }[]; dryRun?: boolean;
}): Promise<{ ok: boolean; error?: string; record?: RuntimeRebalance; effective?: Record<string, number>; suggested?: number; dryRun?: boolean }> {
  // Phase 17：校驗鏈（同日重複、effectiveWeights replay 等）全部基於 DB 版記錄（DB 係真相）
  const records = await listRuntimeRebalances();
  const ew = applyRebalances(CURRENT_WEIGHTS, records);
  const err = validateRebalance(ew, Object.keys(CURRENT_WEIGHTS), records, input, new Date());
  if (err) return { ok: false, error: err };
  const record: RuntimeRebalance = {
    date: input.date,
    title: input.title?.trim() || nextRebalanceTitle(3, records.length),
    trigger: input.trigger?.trim() ?? "",
    changes: input.changes.map(c => ({ etf: c.etf, from: ew[c.etf] ?? 0, to: c.to })),
    note: input.note?.trim() ?? "",
    recordedAt: new Date().toISOString(),
  };
  const nextWeights = applyRebalances(CURRENT_WEIGHTS, [...records, record]);
  if (input.dryRun) return { ok: true, dryRun: true, record, effective: nextWeights };

  // 1) 記錄落 DB（真相源，kind='rebalance_audit'）+ 檔案雙寫（本地開發/zip 鏡像；DB 係真相，檔案係鏡像）
  // Phase 17：kind 由 'rebalance' 改 'rebalance_audit'——舊版同重算快照共用 kind='rebalance'，
  // 一旦審計行成為最新行，latestSnapshot 會將 {record,effective} 當 Snapshot 返（潛伏 bug）
  const all = [...records, record];
  writeJsonBothDirs("rebalances.json", JSON.stringify({ records: all }, null, 2), "調倉記錄檔案鏡像將陳舊");
  try {
    const db = getDb();
    await db.insert(snapshots).values({ kind: "rebalance_audit", payload: JSON.stringify({ record, effective: nextWeights }) });
  } catch (e: any) {
    // DB 係真相源——寫入失敗即下次讀取會甩咗呢條記錄（檔案鏡像只係 fallback），必須響亮
    console.warn("[pipeline] ⚠ 調倉記錄 DB 審計行寫入失敗（真相源缺失此記錄！檔案鏡像已保存，請盡快補寫 DB）:", e?.message ?? e);
  }

  // 2) 淨值 timeline 加分段（調倉日收市執行 → 下一交易日起新權重），跟手追加已欠嘅淨值
  try {
    const perf = JSON.parse(readFileSync2("public/data/performance.json"));
    const tl: WeightsTimelineEntry[] = Array.isArray(perf.weightsTimeline) && perf.weightsTimeline.length
      ? perf.weightsTimeline
      : [{ from: String(perf.frozenSince ?? LAST_REBALANCE_DATE), w: { ...CURRENT_WEIGHTS } }];
    if (!tl.some(e => e.from === record.date)) {
      tl.push({ from: record.date, w: nextWeights });
      tl.sort((a, b) => a.from.localeCompare(b.from));
    }
    perf.weightsTimeline = tl;
    writeJsonBothDirs("performance.json", JSON.stringify(perf), "淨值將停止更新");
  } catch (e: any) { console.warn("[pipeline] ⚠ 淨值 timeline 寫入失敗:", e?.message ?? e); }
  await updatePerformance();

  // 3) 按新權重重跑建議（已執行嘅建議唔應再掛）；重跑即係人工覆核動作 → acknowledged
  let suggestedCount = 0;
  try {
    const base = await latestSnapshot();
    if (base) {
      const { changes, note, watchlist } = await buildSuggestions(base.views ?? []);
      suggestedCount = changes.length;
      const snap: Snapshot = {
        ...base,
        generatedAt: new Date().toISOString(),
        suggested: changes,
        watchlist,
        suggestedNote: `調倉 ${record.date} 已記錄，建議按新權重重算。${note}`,
        lastRebalanceDate: effectiveLastRebalanceDate(),
        acknowledged: true,
        acknowledgedAt: new Date().toISOString(),
      };
      const json = JSON.stringify(snap, null, 2);
      writeJsonBothDirs("snapshot.json", json, "靜態鏡像將陳舊");
      try {
        const db = getDb();
        await db.insert(snapshots).values({ kind: "rebalance", payload: JSON.stringify(snap) });
      } catch (e: any) { console.warn("[pipeline] ⚠ 重算快照 DB 寫入失敗（檔案已保存）:", e?.message ?? e); }
    }
  } catch (e: any) { console.warn("[pipeline] ⚠ 調倉後建議重算失敗（記錄本身已保存，下次管道會重算）:", e?.message ?? e); }

  console.log(`[pipeline] 調倉已記錄：${record.title} @ ${record.date}（${record.changes.map(c => `${c.etf} ${c.from}→${c.to}`).join("，")}），重算建議 ${suggestedCount} 項`);
  return { ok: true, record, effective: nextWeights, suggested: suggestedCount };
}

function readFileSync2(p: string): string {
  return readFileSync(p, "utf8");
}

// 信号关键词 → ETF 映射（有序，首个命中即停；金银铜为一对多特例）
// 适配度校验在此执行：只有能精确映射的信号才进入建议
// Phase 13 P1-7：逐條補齊繁體變體 alias（本港專家字幕/標題多為繁體，舊表大量 miss）
export const ASSET_MAP: [RegExp, string[]][] = [
  [/金银铜|金銀銅|贵金属组合|貴金屬組合/i, ["GLD", "SLV", "COPX"]],
  [/半导体|半導體|芯片|晶片|算力|AI上游|HBM|记忆体|記憶體/i, ["SMH"]],
  [/白银|白銀/i, ["SLV"]],
  [/黄金|黃金|金价|金價|贵金属|貴金屬/i, ["GLD"]],
  [/铜|銅/i, ["COPX"]],
  [/能源|石油|油价|油價|原油/i, ["XLE"]],
  [/原材料|材料/i, ["XLB"]],
  [/基建|电力|電力|数据中心|數據中心|資料中心/i, ["IFRA"]],
  [/中国资产|中國資產|人民币|人民幣|A股|沪深|滬深|在岸/i, ["ASHR"]],   // 复盘结论：中国观点以在岸工具为主（置于 MCHI 前）
  [/中国|中國|中概/i, ["MCHI"]],
  [/港股|恒指|恆指|香港股票|中特估|本地蓝筹|本地藍籌/i, ["EWH"]],
  [/韩国|韓國|韩股|韓股/i, ["EWY"]],
  [/台湾|台灣|台股|台积电|台積電/i, ["EWT"]],
  [/医疗|醫療|医药|醫藥|保健/i, ["XLV"]],
  [/欧洲|歐洲|欧股|歐股|欧元区|歐元區/i, ["VGK"]],
  [/比特币|比特幣|加密货币|加密貨幣|BTC/i, ["IBIT"]],
  [/美股|标普|標普|纳指|納指|S&P/i, ["VOO"]],
  [/长债|長債|国债|國債|美债|美債/i, ["TLT"]],
  [/债券|債券/i, ["BND"]],
];

export function mapAsset(asset: string): string[] {
  for (const [re, tickers] of ASSET_MAP) if (re.test(asset)) return tickers;
  return [];
}

function decay(dateStr: string, now: Date, horizon: string = "theme") {
  const hl = HALF_LIFE_BY_HORIZON[horizon] ?? 21;
  const days = Math.max(0, (now.getTime() - new Date(dateStr).getTime()) / 86400000);
  return Math.pow(0.5, days / hl);
}

async function resolveUploadsPlaylist(handle: string): Promise<string | null> {
  const r = await tfetch(`https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle=${encodeURIComponent(handle)}&key=${YT_KEY}`);
  // Phase 13 P1-5：YouTube API 非 2xx 要記 status + 頻道，唔准 silent return null
  if (!r.ok) { console.log(`[pipeline] ⚠ YouTube channels API HTTP ${r.status}（${handle}）——頻道解析失敗`); return null; }
  const j: any = await r.json();
  return j.items?.[0]?.contentDetails?.relatedPlaylists?.uploads ?? null;
}

async function latestVideos(playlistId: string): Promise<{ videoId: string; title: string; description: string; publishedAt: string }[]> {
  const r = await tfetch(`https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${playlistId}&maxResults=10&key=${YT_KEY}`);
  if (!r.ok) { console.log(`[pipeline] ⚠ YouTube playlistItems API HTTP ${r.status}（playlist=${playlistId}）——本頻道本輪無新片`); return []; } // Phase 13 P1-5：非 2xx 記 status
  const j: any = await r.json();
  const cutoff = Date.now() - LOOKBACK_DAYS * 86400000;
  return (j.items ?? [])
    .map((it: any) => ({
      videoId: it.snippet.resourceId.videoId as string,
      title: it.snippet.title as string,
      description: (it.snippet.description as string) ?? "",
      publishedAt: it.snippet.publishedAt as string,
    }))
    .filter((v: any) => new Date(v.publishedAt).getTime() >= cutoff);
}

// 抓取 YouTube 视频字幕（无需OAuth：解析播放页 captionTracks → timedtext）
// Phase 19：誠實化——失敗唔再靜靜雞 return null，逐種失敗回人話 reason（export 俾測試用）
// 2026-10-10：三通道兜底。YouTube 會封雲端 IP 嘅 /watch 頁（Render 實測中招），
// 但 Innertube player API（/youtubei/v1/player）同 oEmbed 通常仍通——改用「Innertube → /watch → Piped」鏈。
async function fetchCaptionXml(baseUrl: string): Promise<string | null> {
  const xml = await (await tfetch(baseUrl)).text();
  // 兩種格式：舊 srv3 用 <text>…</text>；現行 timedtext format=3 用 <p t d>…</p>（2026-10 實測 ANDROID client 全係呢種）
  const unesc = (s: string) => s.replace(/&amp;/g, "&").replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\n/g, " ");
  let texts = [...xml.matchAll(/<text[^>]*>([\s\S]*?)<\/text>/g)].map(x => unesc(x[1])).filter(Boolean);
  if (!texts.length) texts = [...xml.matchAll(/<p\s[^>]*\bt="\d+"[^>]*>([\s\S]*?)<\/p>/g)].map(x => unesc(x[1])).filter(Boolean);
  const joined = texts.join(" ");
  return joined.length > 200 ? joined.slice(0, 12000) : null; // 截断控制token
}

function pickTrack(tracks: any[]): any {
  return tracks.find(t => /zh-(Hant|HK|TW)/i.test(t.languageCode)) ??
    tracks.find(t => /zh/i.test(t.languageCode)) ??
    tracks.find(t => /en/i.test(t.languageCode)) ??
    tracks[0];
}

export async function getTranscript(videoId: string): Promise<{ text: string | null; reason?: string }> {
  const fail = (reason: string) => ({ text: null, reason });
  // 通道 A：Innertube player API（Android client——雲端 IP 友好度最高）
  try {
    const r = await tfetch("https://www.youtube.com/youtubei/v1/player?prettyPrint=false", {
      method: "POST",
      headers: { "Content-Type": "application/json", "User-Agent": "com.google.android.youtube/20.10.38 (Linux; U; Android 15) gzip" },
      body: JSON.stringify({ context: { client: { clientName: "ANDROID", clientVersion: "20.10.38", androidSdkVersion: 35, hl: "zh-HK" } }, videoId }),
    });
    if (r.ok) {
      const j: any = await r.json();
      const tracks = j?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
      if (Array.isArray(tracks) && tracks.length) {
        const pick = pickTrack(tracks);
        if (pick?.baseUrl) {
          const text = await fetchCaptionXml(pick.baseUrl);
          if (text) return { text };
        }
      }
    }
  } catch { /* 落下一通道 */ }
  // 通道 B：/watch 頁面解析 captionTracks
  let page: Response;
  try {
    page = await tfetch(`https://www.youtube.com/watch?v=${videoId}`, {
      headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8" },
    });
  } catch (e: any) {
    page = undefined as unknown as Response;
  }
  try {
    if (page?.ok) {
      const html = await page.text();
      const m = html.match(/"captionTracks":(\[.*?\])/);
      if (m) {
        const tracks: any[] = JSON.parse(m[1]);
        const pick = pickTrack(tracks);
        if (pick?.baseUrl) {
          const text = await fetchCaptionXml(pick.baseUrl);
          if (text) return { text };
        }
      }
    }
  } catch { /* 落下一通道 */ }
  return fail("YouTube 直連不可達（出口封鎖）");
}

// ---- 字幕代理通道（kome.ai，受限網絡實測可達，免 key）----
// 出口防火牆只放行特定域名：youtube.com/googleapis 被斷，但 kome.ai 可達——
// 由它代抓 YouTube 官方/自動字幕。限制：發佈者停用字幕的視頻返回不可用（誠實失敗）。
// Phase 19：kome.ai 已死（Vercel Security Checkpoint + HTTP 429 付費牆）——
// 舊版唔識別 checkpoint HTML，靜靜雞 return null，用戶只見籠統「字幕不可用」。
// 而家逐種死因回人話 reason，caller 彙總俾用戶可執行嘅下一步指引。（export 俾測試用）
// ---- 字幕通道 C：Supadata API（2026-10-10 新增；Render 雲端 IP 被 YouTube 全站封鎖後嘅伺服器主力）----
// 免費層 100 次/月；失敗誠實回 reason（transcript-unavailable = 作者冇字幕，唔係故障）
export async function getTranscriptViaSupadata(videoId: string): Promise<{ text: string | null; reason?: string }> {
  const key = process.env.SUPADATA_API_KEY ?? "";
  if (!key) return { text: null, reason: "未配置 SUPADATA_API_KEY" };
  let r: Response;
  try {
    r = await tfetch(`https://api.supadata.ai/v1/youtube/transcript?url=${encodeURIComponent("https://www.youtube.com/watch?v=" + videoId)}`, {
      headers: { "x-api-key": key },
    }, 45000);
  } catch (e: any) {
    return { text: null, reason: `Supadata 連接失敗：${String(e?.message ?? e).slice(0, 100)}` };
  }
  if (r.status === 429) return { text: null, reason: "Supadata 免費額度用完（HTTP 429，100 次/月）" };
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    if (/transcript-unavailable/i.test(body)) return { text: null, reason: "該視頻無字幕（Supadata 確認）" };
    return { text: null, reason: `Supadata HTTP ${r.status}` };
  }
  try {
    const j: any = await r.json();
    const segs: any[] = j?.content ?? [];
    const text = segs.map(x => String(x?.text ?? "")).filter(Boolean).join(" ");
    if (text.length <= 200) return { text: null, reason: "Supadata 字幕過短" };
    return { text: text.slice(0, 12000) };
  } catch {
    return { text: null, reason: "Supadata 回應格式異常" };
  }
}

export async function getTranscriptViaKome(videoId: string): Promise<{ text: string | null; reason?: string }> {
  const fail = (reason: string) => ({ text: null, reason });
  let r: Response;
  try {
    r = await tfetch("https://kome.ai/api/transcript", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id: videoId }),
    }, 45000);
  } catch (e: any) {
    return fail(`字幕代理連接失敗：${String(e?.message ?? e).slice(0, 120)}`);
  }
  if (r.status === 429) return fail("字幕代理 kome.ai 已改為付費服務（HTTP 429 限流）");
  // 安全閘道攔截（Vercel Security Checkpoint）會回 HTML——即使 200/403 都係，唔好當 JSON parse
  const raw = await r.text().catch(() => "");
  if (/Vercel Security Checkpoint/i.test(raw) || /^\s*</.test(raw)) {
    return fail("字幕代理 kome.ai 已被安全閘道封鎖（服務失效）");
  }
  if (!r.ok) return fail(`字幕代理連接失敗：HTTP ${r.status}`);
  let j: any;
  try { j = JSON.parse(raw); } catch { return fail("字幕代理回應格式異常（非 JSON）——服務可能已失效"); }
  const t: string = String(j?.transcript ?? "").trim();
  // 失敗時 kome 也返回 200 但內容是英文錯誤句（"Transcripts aren't available..."）——用長度+關鍵詞雙重判別
  if (/aren't available|blocking us|currently unavailable/i.test(t)) return fail("該視頻冇可用字幕（發佈者可能停用了字幕）");
  if (t.length < 200) return fail("字幕過短");
  return { text: t.slice(0, 12000) };
}

// 從各種 YouTube 鏈接形態提取 videoId（videoId 字集 [A-Za-z0-9_-]{11}，遇 ?&#/ 或空白即停；
// 已驗證：youtu.be 短鏈 + si 追蹤參數 + 尾 `?` 都食到）
export function parseVideoId(url: string): string | null {
  const m = url.match(/(?:youtube\.com\/(?:watch\?[^#]*v=|shorts\/|live\/)|youtu\.be\/)([\w-]{11})/);
  return m?.[1] ?? (/^[\w-]{11}$/.test(url.trim()) ? url.trim() : null);
}

// Phase 16：URL 正規化——parse 到 videoId 就回 canonical watch URL（youtu.be 短鏈/帶 si 參數全部歸一），
// 否則回 trim 後原串。入庫/去重統一用呢個，唔再俾短鏈繞過字串全等去重。
export function canonicalVideoUrl(url?: string): string {
  const t = (url ?? "").trim();
  if (!t) return "";
  const id = parseVideoId(t);
  return id ? `https://www.youtube.com/watch?v=${id}` : t;
}

// ---- Phase 16：RSS 兜底（免 YOUTUBE_API_KEY）----
// API 路唔得（無 key / googleapis 不可達）但 youtube.com 本身可達時，
// 頻道頁 HTML 解析 channelId → RSS feed 攞近排新片（標題/日期齊，簡介為空）。
const channelIdCache = new Map<string, string | null>();

async function resolveChannelIdAny(ch: { handle?: string; channelId?: string }): Promise<string | null> {
  if (ch.channelId) return ch.channelId;
  const handle = ch.handle ?? "";
  if (!handle) return null;
  if (channelIdCache.has(handle)) return channelIdCache.get(handle) ?? null;
  let id: string | null = null;
  // 路一：YouTube Data API（handle → channelId）
  if (YT_KEY) {
    try {
      const r = await tfetch(`https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=${encodeURIComponent(handle)}&key=${YT_KEY}`);
      if (r.ok) { const j: any = await r.json(); id = j.items?.[0]?.id ?? null; }
    } catch { /* fallthrough 去 HTML 路 */ }
  }
  // 路二：頻道頁 HTML 內嵌 externalId/channelId
  if (!id) {
    try {
      const r = await tfetch(`https://www.youtube.com/${handle}`, {
        headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
      });
      if (r.ok) {
        const html = await r.text();
        id = html.match(/"(?:externalId|channelId)":"(UC[\w-]{22})"/)?.[1] ?? null;
      }
    } catch { /* ignore */ }
  }
  channelIdCache.set(handle, id);
  return id;
}

// RSS feed 拆 <entry>：同 latestVideos 一樣嘅 shape（description 俾 ""），照舊 filter LOOKBACK_DAYS
async function latestVideosViaRss(channelId: string): Promise<{ videoId: string; title: string; description: string; publishedAt: string }[]> {
  try {
    const r = await tfetch(`https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`);
    if (!r.ok) { console.log(`[pipeline] ⚠ YouTube RSS feed HTTP ${r.status}（channel=${channelId}）——本頻道本輪無新片`); return []; }
    const xml = await r.text();
    const cutoff = Date.now() - LOOKBACK_DAYS * 86400000;
    const decode = (s: string) => s.replace(/&amp;/g, "&").replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">");
    const out: { videoId: string; title: string; description: string; publishedAt: string }[] = [];
    for (const m of xml.matchAll(/<entry>([\s\S]*?)<\/entry>/g)) {
      const e = m[1];
      const videoId = /<yt:videoId>([^<]+)<\/yt:videoId>/.exec(e)?.[1];
      const title = decode(/<title>([^<]*)<\/title>/.exec(e)?.[1] ?? "");
      const publishedAt = /<published>([^<]+)<\/published>/.exec(e)?.[1] ?? "";
      if (!videoId || !publishedAt) continue;
      if (new Date(publishedAt).getTime() < cutoff) continue;
      out.push({ videoId, title, description: "", publishedAt });
    }
    return out;
  } catch { return []; }
}

// 貼鏈接抓字幕（手動錄入表單用）：YouTube URL → 完整字幕文字
// Phase 19：兩路字幕死因逐個記低，合成可執行嘅人話 error（唔再籠統「字幕不可用」）；
// 同時經 noembed 攞標題/頻道名 metadata（8s 非致命）——就算字幕失敗，meta 成功都照返（前端自動填標題/揀專家用）。
export async function fetchVideoTranscript(url: string): Promise<{
  ok: boolean; videoId?: string; text?: string; chars?: number; error?: string;
  meta?: { title?: string; author?: string };
}> {
  const videoId = parseVideoId(url);
  if (!videoId) return { ok: false, error: "無法識別的 YouTube 鏈接——支持 watch?v= / youtu.be / shorts 形態" };
  const watchUrl = `https://www.youtube.com/watch?v=${videoId}`;
  // noembed metadata（標題/頻道名）——非致命，失敗照舊行字幕
  let meta: { title?: string; author?: string } | undefined;
  try {
    const r = await tfetch(`https://noembed.com/embed?url=${encodeURIComponent(watchUrl)}`, {}, 8000);
    if (r.ok) {
      const j: any = await r.json();
      const title = typeof j?.title === "string" ? j.title.trim() : "";
      const author = typeof j?.author_name === "string" ? j.author_name.trim() : "";
      if (title || author) meta = { ...(title ? { title: title.slice(0, 200) } : {}), ...(author ? { author: author.slice(0, 100) } : {}) };
    }
  } catch { /* 非致命——metadata 只係加分項 */ }
  // 受限網絡走代理；開放網絡（自部署）先試直連字幕軌，代理兜底
  const direct = await getTranscript(videoId);
  const viaSupa = direct.text ? null : await getTranscriptViaSupadata(videoId);
  const viaKome = (direct.text ?? viaSupa?.text) ? null : await getTranscriptViaKome(videoId);
  const text = direct.text ?? viaSupa?.text ?? viaKome?.text ?? null;
  if (!text) {
    const reasons = [direct.reason, viaSupa?.reason, viaKome?.reason].filter(Boolean).map((r, i) => `${["①", "②", "③"][i]} ${r}`).join("；");
    return {
      ok: false, videoId, ...(meta ? { meta } : {}),
      error: `自動抓字幕失敗：${reasons}。👉 請改用：YouTube App/網頁「顯示文字記錄」全選複製貼到下方文本框，或截圖用 OCR 上傳。`,
    };
  }
  return { ok: true, videoId, text, chars: text.length, ...(meta ? { meta } : {}) };
}

// ---- Kimi 內置聯網搜索（$web_search，Moonshot 服務端執行）----
// 出口受限環境下 Brave/YouTube 物理不可達，但 api.moonshot.cn 可達——
// 新聞與專家動態改走 Kimi 聯網搜索，無需發布、無需開放網絡即可恢復抓取。
// 協議：第一輪模型返回 tool_calls($web_search) → 客戶端回傳空 tool 消息 → 服務端注入搜索結果 → 第二輪出最終答案
async function kimiWebSearch(query: string): Promise<string | null> {
  if (!KIMI_KEY) return null;
  // Phase 13 P0-1：moonshot-v1-auto 已退役，改用共享 resolver（緩存可用模型；全失敗 → null 降級）
  const model = await resolveKimiModel();
  if (!model) return null; // resolver 已響亮報警
  const tools = [{ type: "builtin_function", function: { name: "$web_search" } }];
  // Phase 19：Round 1 係細請求（只係決定觸唔觸發搜索）但都要完整 message（tool_calls），
  // 故非 stream + 網絡錯誤重試（抗出口 TCP reset）；Round 2 係長 reasoning（實測可超 90s），
  // 必須走 kimiChat streaming——bytes 持續流動，出口代理唔會當閒置連接 reset。
  const callRound1 = async (messages: unknown[]): Promise<any> => {
    let attempt = 0;
    while (true) {
      try {
        const r = await tfetch(`${KIMI_BASE}/chat/completions`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${KIMI_KEY}` },
          // Phase 13.2：kimi-k2.6/k3 係 reasoning 模型，temperature 只接受 1（即默認值）——唔准設此欄，設 0.3 會 400 全滅
          // Phase 13.2：max_tokens 2000→6000——reasoning tokens 會食配額（實測 R2 reasoning 可達 2,500+），2000 會齋諗唔答
          body: JSON.stringify({ model, messages, tools, max_tokens: 6000 }),
        }, 150000); // Phase 13.2：90s→150s——R2 帶搜索結果嘅 reasoning 實測可超 90s
        if (!r.ok) throw new Error(`Kimi search HTTP ${r.status} (${model})`);
        return await r.json();
      } catch (e: any) {
        if (isNetworkError(e) && attempt < 2) { attempt++; await sleepMs(attempt * 1000); continue; }
        throw e;
      }
    }
  };
  try {
    const msgs: any[] = [{ role: "user", content: query }];
    const r1 = await callRound1(msgs);
    const m1 = r1.choices?.[0]?.message;
    const tcs = m1?.tool_calls ?? [];
    if (tcs.length === 0) return m1?.content ?? null; // 模型直接回答（未觸發搜索）
    msgs.push(m1);
    // Phase 13.2 協議修復：tool message content 必須帶 R1 tool_call 嘅 arguments——
    // kimi-k2.6 時代 $web_search 嘅搜索結果已由服務端執行並放入 arguments（含 search_result.search_id），
    // 舊協議回傳空字串 = 模型 R2 收唔到搜索結果，只會講「請稍等」或保守輸出 []
    for (const t of tcs) msgs.push({ role: "tool", tool_call_id: t.id, name: t.function.name, content: t.function?.arguments ?? "" });
    return await kimiChat({ model, messages: msgs, tools, maxTokens: 6000, timeoutMs: 150000 });
  } catch (e: any) {
    // Phase 13 P1-5：搜索失敗唔准靜默——記低原因與查詢主題
    console.log(`[pipeline] ⚠ Kimi 聯網搜索失敗（${query.slice(0, 40)}…）: ${e.message ?? e}`);
    return null;
  }
}

interface NewsItem { title: string; summary: string; url: string; date: string; source: string }

// 用 Kimi 聯網搜索收集某主題的近期市場動態，輸出嚴格 JSON 數組（≤3 條，限近 LOOKBACK_DAYS 天）
async function collectViaKimiSearch(themeName: string): Promise<NewsItem[]> {
  const topic = `${themeName} 市場 最新動態 觀點`;
  const today = new Date().toISOString().slice(0, 10);
  // 誠實性約束（真金白銀用途）：只收錄搜索結果中真實存在的內容，必須附真實鏈接與真實發布日期；
  // 嚴禁憑訓練知識概括專家觀點——寧可輸出 [] 也不允許編造
  const q = `今天是 ${today}。請用聯網搜索查找「${topic}」。
嚴格規則：
1. 只收錄搜索結果中真實存在、發布於過去 ${LOOKBACK_DAYS} 天內的具體文章/視頻/專訪；
2. 每條必須附搜索結果中實際出現的 URL 和該內容的真實發布日期；
3. 標題必須是原文真實標題，摘要必須基於原文實際內容（含其具體市場方向判斷）；
4. 嚴禁憑你的訓練知識概括或編造內容、鏈接或日期；搜索結果沒有符合條件的內容就輸出 []。
輸出嚴格 JSON 數組（最多 3 條）：
[{"title":"原文真實標題","summary":"120字內中文要點","url":"真實鏈接","date":"YYYY-MM-DD 真實發布日期","source":"媒體/平台名"}]
只輸出 JSON，不要任何其他文字。`;
  const text = await kimiWebSearch(q);
  if (!text) return [];
  try {
    const m = text.match(/\[[\s\S]*\]/);
    const arr = JSON.parse(m ? m[0] : text) as NewsItem[];
    const cutoff = Date.now() - LOOKBACK_DAYS * 86400000;
    return (Array.isArray(arr) ? arr : []).slice(0, 3)
      // 寧缺毋濫：無真實鏈接或無有效日期的條目直接丟棄（防止模型張冠李戴舊聞/編造內容混入觀點庫）
      .filter(it => it?.title && it?.summary && /^https?:\/\//.test(String(it.url ?? ""))
        && /^\d{4}-\d{2}-\d{2}$/.test(String(it.date ?? "")) && new Date(it.date).getTime() >= cutoff)
      .map(it => ({
        title: String(it.title).slice(0, 200),
        summary: String(it.summary).slice(0, 300), // Phase 13 P1-10：開頭 300 字足以去重，慳 token
        url: String(it.url),
        source: String(it.source ?? "Kimi搜索"),
        date: clampFutureDate(it.date), // Phase 13 P1-4：未來日期夾返今日（警告內置）
      }));
  } catch { return []; }
}

// 簡易並發池：限制同時進行的搜索/結構化請求數，避免觸發 API 限流
async function pool<T>(n: number, tasks: (() => Promise<T>)[]): Promise<T[]> {
  const out: T[] = new Array(tasks.length) as T[];
  let i = 0;
  await Promise.all(Array.from({ length: Math.min(n, tasks.length) }, async () => {
    while (i < tasks.length) { const k = i++; out[k] = await tasks[k](); }
  }));
  return out;
}

// ---- Phase 19：Kimi 調用抗 TCP reset ----
// 背景：kimi.pro 發布站出口代理會截斷「長時間無 bytes 流動」嘅連接——
// 非 streaming 長請求（reasoning 模型實測 40-90s 無輸出）中途被 TCP RESET（"fetch failed"）。
// 修法：① 首選 streaming（stream:true，bytes 持續流動 → 代理唔當閒置 reset）；
// ② network error 同一模型重試最多 2 次（指數退避 1s、2s，總共最多 3 次嘗試）。

// SSE 逐 chunk 累積 choices[0].delta.content——處理 "data: " 前綴、"[DONE]"、跨 chunk 不完整行 buffer。
// ⚠ kimi-k2.6/k3 係 reasoning 模型：delta 先入 reasoning_content（思考流，可達 100+ chunks），
// 然後先入 content——reasoning_content 必須忽略（唔係錯誤），只累積 content。（export 俾測試用）
export async function readSSE(r: Response): Promise<string> {
  const reader = r.body?.getReader();
  if (!reader) return "";
  const dec = new TextDecoder();
  let buf = "", out = "";
  const eatLine = (line: string): boolean => { // return true = 見到 [DONE]
    const t = line.trim();
    if (!t.startsWith("data:")) return false;
    const data = t.slice(5).trim();
    if (!data) return false;
    if (data === "[DONE]") return true;
    try {
      const j = JSON.parse(data);
      const c = j?.choices?.[0]?.delta?.content;
      if (typeof c === "string") out += c;
    } catch { /* 唔完整嘅 JSON 行（理論上按行切唔會）——skip */ }
    return false;
  };
  let done = false;
  while (!done) {
    const { done: rd, value } = await reader.read();
    if (rd) break;
    buf += dec.decode(value, { stream: true });
    let idx: number;
    while ((idx = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, idx);
      buf = buf.slice(idx + 1);
      if (eatLine(line)) { done = true; break; }
    }
  }
  if (!done && buf.trim()) eatLine(buf); // flush 尾部唔完整 buffer
  try { await reader.cancel().catch(() => {}); } catch { /* ignore */ }
  return out;
}

const sleepMs = (ms: number) => new Promise(res => setTimeout(res, ms));
// 網絡層錯誤（出口 reset / 超時 abort）——HTTP 層錯誤（我哋自己 throw 嘅 Error）唔算
function isNetworkError(e: any): boolean {
  return e instanceof TypeError || e?.name === "AbortError" || e?.name === "TimeoutError" || /fetch failed/i.test(String(e?.message ?? ""));
}

// Kimi chat 統一入口：streaming 優先 + 網絡錯誤重試（抗出口 TCP reset）。
// - jsonMode → response_format json_object（HTTP 400 時自動唔帶 format 非 stream 重試一次）
// - HTTP 404 → throw code=404（caller 跳下一個模型）
// - 欠費（suspended/insufficient balance）→ 人話錯誤（caller 直接 break 回退鏈）
// - stream 完 content 為空 → 當失敗，非 stream 重試一次（注意：k2.6/k3 reasoning 會食 max_tokens，
//   空 content 可能係 token 耗盡而唔係 stream 壞——fallback 都會空，觸發時 log 註明）
export async function kimiChat(opts: {
  model: string; prompt?: string; messages?: any[]; tools?: any[];
  maxTokens?: number; jsonMode?: boolean; timeoutMs?: number;
}): Promise<string> {
  const { model } = opts;
  const messages = opts.messages ?? [{ role: "user", content: opts.prompt ?? "" }];
  const maxTokens = opts.maxTokens ?? 4000;
  const timeoutMs = opts.timeoutMs ?? 120000;
  let useStream = true;
  let withFormat = opts.jsonMode ?? false;
  let formatFallbackDone = false, streamFallbackDone = false;
  let attempt = 0; // 網絡錯誤重試計數（HTTP 層重試唔計）
  while (true) {
    try {
      const r = await tfetch(`${KIMI_BASE}/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${KIMI_KEY}` },
        body: JSON.stringify({
          model, messages, max_tokens: maxTokens,
          // Phase 13.2：唔准設 temperature——kimi-k2.6/k3 只接受 1（默認）
          ...(opts.tools ? { tools: opts.tools } : {}),
          ...(useStream ? { stream: true } : {}),
          ...(withFormat ? { response_format: { type: "json_object" } } : {}),
        }),
      }, timeoutMs);
      if (r.status === 404) throw Object.assign(new Error(`Kimi API 404 (${model})`), { code: 404 });
      if (r.status === 400 && withFormat && !formatFallbackDone) {
        formatFallbackDone = true; useStream = false; withFormat = false; // 個別模型不收 response_format → 無格式非 stream 重試一次
        continue;
      }
      if (!r.ok) {
        const errBody = await r.text().catch(() => "");
        if (/suspended|insufficient balance/i.test(errBody)) {
          throw new Error("Moonshot 帳戶因餘額不足已被暫停（HTTP 429）——請到 platform.moonshot.cn 充值，或更換 .env 嘅 KIMI_API_KEY；充值前可改用對話嘅 Agent 結構化通道（唔經 Moonshot）");
        }
        throw new Error(`Kimi API ${r.status} (${model})`);
      }
      if (useStream) {
        const text = await readSSE(r);
        if (text.trim()) return text;
        // streaming 成功但累積內容為空——可能係 reasoning 食晒 max_tokens（k2.6/k3），唔一定係 stream 壞
        if (streamFallbackDone) throw new Error(`Kimi 回應內容為空 (${model})——可能係 reasoning 耗盡 max_tokens=${maxTokens}，請調大 maxTokens 或縮短輸入`);
        console.log(`[pipeline] ⚠ kimiChat(${model}): stream 完成但 content 為空——可能 reasoning 耗盡 max_tokens=${maxTokens}，非 stream 重試一次`);
        streamFallbackDone = true; useStream = false;
        continue;
      }
      const j: any = await r.json();
      const text: string = j?.choices?.[0]?.message?.content ?? "";
      if (!String(text).trim()) throw new Error(`Kimi 回應內容為空 (${model})——可能係 reasoning 耗盡 max_tokens=${maxTokens}`);
      return String(text);
    } catch (e: any) {
      if (isNetworkError(e) && attempt < 2) { // 網絡錯誤（TCP reset/timeout）→ 同一模型指數退避重試，最多 3 次嘗試
        attempt++;
        console.log(`[pipeline] ⚠ kimiChat(${model}) 網絡錯誤（${String(e?.message ?? e?.name).slice(0, 60)}）——${attempt}s 後第 ${attempt + 1}/3 次嘗試`);
        await sleepMs(attempt * 1000);
        continue;
      }
      throw e;
    }
  }
}

async function structureWithKimi(expertName: string, title: string, content: string, date: string, contentType: string): Promise<{ summary: string; signals: SnapshotSignal[]; horizon: "macro" | "theme" | "event" }> {
  // Phase 13 P1-10 prompt 升級：隱含睇淡歸 bear、strength 錨定、confidence 欄位（low→強度封頂 2）、舊事件前綴。
  // Phase 13 P1-7：例子移除「日圆」——ASSET_MAP 冇日圆對應持倉工具，prompt 例子必須同 map 一致，否則引出無法映射嘅信號
  const prompt = `你是投资观点结构化引擎。以下是${expertName}于${date}发布的视频标题与官方简介。
请输出严格JSON：{"summary":"80字内中文要点","horizon":"macro|theme|event","signals":[{"asset":"资产(如:美股/半导体/黄金/A股/港股/韩国/台湾/欧洲/能源/比特币/债券)","direction":"bull|bear|neutral","strength":1-5,"confidence":"high|low","note":"10字内理由"}]}
规则：
1. 只提取内容中明确表达的市场方向观点；无明确方向则signals为空数组。
2. 隐含看淡也算 bear：「估值过高」「谨慎」「回调风险」「不宜追高」等警示措辞 → direction=bear，且 strength 减 1。
3. strength 锚定：1=轻微倾向，3=明确看多/看空，5=呼吁立即行动（加仓/清仓级）。把握不足时 confidence=low。
4. 注意内容内的时间锚点：若内容实际指向旧事件（非本次发布的新观点），在 summary 开头加「[舊事件]」前缀。
5. horizon判断：macro=宏观/年度级观点，theme=行业/主题/季度级，event=事件/短线/周级。
标题：${title}
${contentType}：${content.slice(0, 9000)}`;
  // 模型回退鏈：優先用上次成功的模型；404（模型下架）逐個試下一個，成功後緩存
  // Phase 19：統一走 kimiChat——streaming 優先 + 網絡錯誤指數退避重試（抗出口 TCP reset）
  const models = workingKimiModel ? [workingKimiModel, ...KIMI_MODEL_CANDIDATES.filter(m => m !== workingKimiModel)] : KIMI_MODEL_CANDIDATES;
  let lastErr = "Kimi API error";
  for (const model of models) {
    try {
      const text = await kimiChat({ model, prompt, maxTokens: 4000, jsonMode: true, timeoutMs: 120000 }); // Phase 13.2：60s→120s——reasoning 模型處理長字幕/全文實測可達 40-90s
      try {
        const m = text.match(/\{[\s\S]*\}/);
        const parsed = JSON.parse(m ? m[0] : text);
        workingKimiModel = model;
        // Phase 13 P1-10：confidence=low → strength 封頂 2；strength 規整到 1-5 整數
        const signals: SnapshotSignal[] = (Array.isArray(parsed.signals) ? parsed.signals : []).slice(0, 6).map((s: any) => ({
          asset: String(s?.asset ?? ""),
          direction: s?.direction,
          strength: Math.max(1, Math.min(s?.confidence === "low" ? 2 : 5, Math.round(Number(s?.strength) || 1))),
          note: String(s?.note ?? "").slice(0, 300),
        })).filter((s: SnapshotSignal) => s.asset && ["bull", "bear", "neutral"].includes(s.direction));
        return { summary: parsed.summary ?? title, signals, horizon: normalizeHorizon(parsed.horizon) }; // Phase 13 P1-4：horizon 白名單
      } catch { lastErr = `Kimi 回應非 JSON (${model})`; continue; }
    } catch (e: any) {
      if (e?.code === 404) { lastErr = `Kimi API 404 (${model})`; continue; } // 模型不存在/無權限 → 試下一個
      if (/suspended|insufficient balance|餘額不足/i.test(String(e?.message ?? ""))) { lastErr = e.message; break; } // 欠費：逐個模型試都係同一結果，直接 break
      lastErr = `Kimi 網絡錯誤 (${model}): ${e.message}`; continue; // 重試耗盡後仍敗 → 繼續回退鏈
    }
  }
  throw new Error(lastErr);
}

// 风险刹车：持仓自60日峰值回撤>15%，且近45天窗口衰减加权净分 ≤0（即无新看多净信号）→ 强制建议降权（真实回测教训：黄金-25%、白银-50%无刹车）
// Phase 13 P1-8：註釋誠實化——舊註釋寫「近30天无新看多信号」，實際實現係 45 日窗口（LOOKBACK_DAYS）淨分判定，註釋改到同實現一致
async function fetchDrawdown(ticker: string): Promise<number | null> {
  // 雙引擎行情（直連 → agent-gw 網關兜底），受限網絡下風控剎車不再靜默失效
  const rows = await fetchCloses(ticker, "3mo");
  if (!rows || !rows.length) return null;
  const closes = rows.map(r => r.close);
  const last = closes[closes.length - 1], peak = Math.max(...closes);
  return (last / peak - 1) * 100;
}

let lastBrakeStatus: "ok" | "partial" | "unavailable" = "unavailable";

// 读取最近 n 份快照中已发出的建议（冷却期判定用）
async function recentSuggestions(n: number): Promise<Set<string>> {
  const db = getDb();
  // Phase 17：過濾快照 kind——否則 rebalance_audit/performance 行會霸佔窗口，冷卻期失效
  const rows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(n);
  const set = new Set<string>();
  for (const r of rows) {
    try {
      const s = JSON.parse(r.payload) as Snapshot;
      for (const c of s.suggested ?? []) set.add(`${c.ticker}:${c.to > c.from ? "up" : "down"}`);
    } catch {}
  }
  return set;
}

export async function buildSuggestions(views: SnapshotView[]): Promise<{ changes: SuggestedChange[]; note: string; watchlist: WatchlistItem[] }> {
  // 按 ETF 汇总衰减加权净方向（支持一对多映射）
  const score: Record<string, number> = {};
  const reasons: Record<string, string[]> = {};
  const reasonW: Record<string, number[]> = {}; // Phase 18.1：每條 reason 嘅簽名權重——展示時按對建議方向嘅貢獻排序
  for (const v of views) {
    for (const s of v.signals) {
      for (const ticker of mapAsset(s.asset)) {
        const dir = s.direction === "bull" ? 1 : s.direction === "bear" ? -1 : 0;
        const w = v.decayWeight * (s.strength / 5);
        score[ticker] = (score[ticker] ?? 0) + dir * w;
        (reasons[ticker] ??= []).push(`${v.expertName}(${v.date.slice(5)})${dir > 0 ? "看好" : dir < 0 ? "看淡" : "中性"}${s.asset}`);
        (reasonW[ticker] ??= []).push(dir * w);
      }
    }
  }
  // Phase 18.1：理由按「對建議方向嘅貢獻」降序——加倉建議唔會仲將看淡觀點排最前（舊版按時間序，會誤導批核）
  const topReasons = (t: string): string =>
    (reasons[t] ?? []).map((r, i) => [r, reasonW[t][i] ?? 0] as const)
      .sort((a, b) => b[1] - a[1]).slice(0, 3).map(x => x[0]).join("；");
  // 冷却期：近5份快照内已建议过的「同ETF同方向」不再重复建议（防止同一信号每天+1pp的假象）
  const recent = await recentSuggestions(5);
  const cooled = (t: string, dir: number) => !recent.has(`${t}:${dir > 0 ? "up" : "down"}`);
  // Phase 15：建議基準 = 現行生效權重（靜態基準 + runtime 調倉記錄 replay），唔係齋睇 07-20 凍結值
  const EW = effectiveWeights();
  // K4 equity gate 統一（快照層）：淨值跌穿 9 日均線時，本輪不輸出任何加倉建議（減倉/剎車不受限）
  // 數據源 = Phase 17 淨值 DB 化（latestPerformance：DB 優先、檔案 fallback）；不可用 → 保守放行
  const perf0 = await latestPerformance().catch(() => null);
  const navSeries: number[] = Array.isArray(perf0?.portfolio) ? perf0.portfolio : [];
  const equityGateOn = navSeries.length >= 9 ? navSeries[navSeries.length - 1] < navSeries.slice(-9).reduce((a, b) => a + b, 0) / 9 : null;

  // M1 pod 熔斷 + 價格風險剎車共用行情：先統一抓取全部持倉的 60 日回撤（%）
  // （與 algo.ts 分析層共用 ./podBreaker 的同一套分組、加權與 -10% 熔斷線，避免兩層漂移）
  const ddPct: Record<string, number | null> = {};
  let brakeChecked = 0, brakeFailed = 0;
  for (const [ticker, w] of Object.entries(EW)) {
    if (w <= 0 || ticker === "SGOV" || ticker === "BND") continue;
    const dd = await fetchDrawdown(ticker);
    ddPct[ticker] = dd;
    if (dd === null) brakeFailed++; else brakeChecked++;
  }
  const { podDD, tripped: podTripped } = computePodStatus(
    EW,
    Object.fromEntries(Object.entries(ddPct).map(([t, d]) => [t, d == null ? null : d / 100])),
  );
  const podBlocked = (t: string) => { const g = groupOf(t); return g != null && podTripped.has(g); };
  const podNote = podTripped.size > 0
    ? `M1 pod 熔斷：${[...podTripped].map(g => `${g}（60日加權回撤 ${podDD[g] != null ? (podDD[g]! * 100).toFixed(1) + "%" : "—"}）`).join("、")} 跌穿 -10% 熔斷線，該組加倉已全部否決（回撤回到 -6% 內解除）。`
    : "";

  const changes: SuggestedChange[] = [];
  for (const [ticker, sc] of Object.entries(score)) {
    const cur = EW[ticker] ?? 0;
    // 净分>0.5 → 建议+1pp；<-0.5 → 建议-1pp（每日管道限±1pp + 冷却期防重复）
    // K4：equity gate 觸發中否決加倉；M1：所屬 pod 熔斷中的標的否決加倉（與分析層同一條件）
    if (sc > 0.5 && cur < 20 && cooled(ticker, 1) && equityGateOn !== true && !podBlocked(ticker)) changes.push({ ticker, from: cur, to: cur + 1, reason: topReasons(ticker) });
    else if (sc < -0.5 && cur > 0 && cooled(ticker, -1)) changes.push({ ticker, from: cur, to: cur - 1, reason: topReasons(ticker) });
  }
  // 风险刹车检查（价格验证层：观点必须与价格走势交叉验证）；行情已在上方統一抓取，逐只記錄可用性
  for (const [ticker, w] of Object.entries(EW)) {
    if (w <= 2 || ticker === "SGOV" || ticker === "BND") continue;
    const dd = ddPct[ticker] ?? null;
    if (dd === null) continue;
    if (dd < -15 && (score[ticker] ?? 0) <= 0 && !changes.some(c => c.ticker === ticker) && cooled(ticker, -1)) {
      changes.push({ ticker, from: w, to: Math.max(0, w - 2), reason: `⚠ 风险刹车：自60日峰值回撤${dd.toFixed(1)}%且无新看多信号——强制降权建议` });
    }
  }
  lastBrakeStatus = brakeFailed === 0 ? "ok" : brakeChecked === 0 ? "unavailable" : "partial";
  const gateNote = equityGateOn === true ? "（equity gate 觸發中：淨值低於 9 日均線，加倉通道已關閉）" : "";
  const note = changes.length === 0
    ? `本轮新观点不足以触发任何±1pp变动，维持现有配置。${gateNote}${podNote}`
    : `基于近${LOOKBACK_DAYS}天新观点的衰减加权净方向 + 价格风险刹车生成；信号变动限±1pp/日、刹车限-2pp/日；需人工复核后生效。${gateNote}${podNote}`;
  // Phase 13 P1-8：建議按 |淨分| 降序輸出——最強信號排最前，slice(0,10) 截斷時唔會誤刪高分建議（剎車項冇淨分，按 -2pp 幅度排尾段）
  changes.sort((a, b) => Math.abs(score[b.ticker] ?? -2) - Math.abs(score[a.ticker] ?? -2));

  // ---- 新主題瞭望（2026-10-09）：組合未覆蓋嘅專家信號 → 主題聚合 → 候選 ETF 篩選 → 試倉提案 ----
  // 候選表人工策展（contracts/watchlist.ts），唔准 LLM 發明 ticker；bear 主題只觀望唔出提案
  const watchlist: WatchlistItem[] = [];
  try {
    const themes = aggregateWatchlist(views, (a) => mapAsset(a).length > 0);
    for (const t of themes) {
      const cand: WatchlistItem["candidates"] = [];
      const themeDef = THEME_CANDIDATES.find(c => c.theme === t.theme);
      // 只有 bull 且淨分接近閘嘅主題先拉行情篩選（慳 quota）；bear/mixed/弱分直接列觀點
      if (themeDef && t.direction === "bull" && t.netScore >= WATCH_PROPOSE_LINE - 0.3) {
        for (const tk of themeDef.tickers.slice(0, 3)) {
          try {
            const r = await screenCandidateEtf(tk);
            if (r.ok) cand.push({ ticker: tk, tier: r.result.verdict.tier, headline: r.result.verdict.headline });
            else cand.push({ ticker: tk, tier: "unknown", headline: `篩選失敗：${r.error.slice(0, 60)}` });
          } catch (e: any) {
            cand.push({ ticker: tk, tier: "unknown", headline: `篩選異常：${String(e?.message ?? e).slice(0, 60)}` });
          }
        }
      }
      const bestTier = cand.find(c => c.tier === "diversifier")?.tier ?? cand.find(c => c.tier === "substitute")?.tier ?? cand[0]?.tier ?? null;
      watchlist.push({ ...t, candidates: cand, proposal: watchProposal(t, bestTier) });
    }
  } catch (e: any) {
    console.warn("[pipeline] ⚠ 新主題瞭望聚合失敗（唔影響主建議）:", e?.message ?? e);
  }

  return { changes: changes.slice(0, 10), note, watchlist };
}

async function runPipelineInner(): Promise<{ ok: boolean; log: string }> {
  const db = getDb();
  const [run] = await db.insert(pipelineRuns).values({ status: "running", log: "" }).$returningId();
  const logs: string[] = [];
  const say = (s: string) => { logs.push(s); console.log("[pipeline]", s); };
  try {
    // 能力探测：不可达的源改走 Kimi 聯網搜索兜底（行情走 agent-gw 网关不受此限）
    // Phase 16：加探 youtube.com 本身——API 路唔得但 youtube.com 可達時，頻道抓取行 RSS 兜底（免 key）
    const [ytOk, ytWebOk, braveOk] = await Promise.all([
      probeHost("https://www.googleapis.com/"),
      probeHost("https://www.youtube.com/"),
      probeHost("https://api.search.brave.com/"),
    ]);
    if (!ytOk) say("⚠ googleapis 不可達（受限網絡）——YouTube Data API 本輪不可用");
    else if (!YT_KEY) say("无 YOUTUBE_API_KEY，YouTube Data API 本輪不可用");
    if (!braveOk) say("⚠ Brave 不可達 → 全網新聞改用 Kimi 聯網搜索（Moonshot 內置 web_search，受限網絡可用）");
    else if (!process.env.BRAVE_API_KEY) say("无 BRAVE_API_KEY，全網新聞改用 Kimi 聯網搜索");

    // Kimi 搜索兜底統一入口：收集 → Kimi 結構化 → 入 views（與字幕/Brave 路徑同一格式）
    const pushKimiViews = async (themeName: string, expertId: string, channelLabel: string): Promise<number> => {
      const items = await collectViaKimiSearch(themeName);
      let added = 0;
      for (const it of items) {
        let summary = it.summary, signals: SnapshotSignal[] = [], horizon: "macro" | "theme" | "event" = "theme";
        if (KIMI_KEY) {
          try {
            const out = await structureWithKimi(`市場新聞匯總（主題：${themeName}）`, it.title, `${it.summary}\n来源:${it.source} ${it.url}`, it.date, "搜索摘要");
            summary = out.summary; signals = out.signals; horizon = out.horizon;
          } catch (e: any) { say(`  Kimi結構化失敗（主題：${themeName}）: ${e.message}`); } // Phase 13 P1-5：唔准靜默
        }
        views.push({
          expertId, expertName: themeName, date: it.date, channel: channelLabel,
          title: it.title, summary, url: it.url,
          signals, horizon, decayWeight: decay(it.date, now, horizon),
        });
        added++;
      }
      return added;
    };
    const now = new Date();
    const views: SnapshotView[] = [];
    // Phase 13 P1-6：增量發現——由上一快照攞已知 videoIds 集，只對新片 call 結構化 LLM；
    // 已知片跳過（每日慳 ~20 calls），舊片由下方 carry 機制原樣併入，唔會丟失
    let knownVideoIds = new Set<string>();
    try {
      const prevRows0 = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
      if (prevRows0[0]) {
        const prev0 = JSON.parse(prevRows0[0].payload) as Snapshot;
        knownVideoIds = new Set((prev0.views ?? []).map(v => v.videoId).filter((x): x is string => !!x));
      }
    } catch {}
    // Phase 16：gating 兩級——API 路（ytApiOk）行舊邏輯；API 唔得但 youtube.com 可達 → RSS 兜底（免 key）；
    // youtube.com 都唔可達 → 寧缺毋濫（下方訊息）。RSS 路嘅 description 為空，字幕抓唔到時無簡介可降級，
    // 呢種情況該片跳過（無字幕級證據唔入庫，同「寧缺毋濫」原則一致）。
    const ytApiOk = ytOk && !!YT_KEY;
    if (!ytApiOk && ytWebOk) say("⚠ YouTube Data API 不可用，但 youtube.com 可達——本輪行 RSS feed 兜底（免 key；標題+日期齊，無官方簡介）");
    if (ytApiOk || ytWebOk) for (const ch of CHANNELS) {
      const chLabel = ch.handle ?? ch.channelId ?? ch.expertName;
      try {
        let vids: { videoId: string; title: string; description: string; publishedAt: string }[];
        if (ytApiOk) {
          const pl = ch.handle ? await resolveUploadsPlaylist(ch.handle) : null;
          if (!pl) { say(`${chLabel}: 频道解析失败`); continue; }
          vids = await latestVideos(pl);
        } else {
          const cid = await resolveChannelIdAny(ch);
          if (!cid) { say(`${chLabel}: 頻道 ID 解析失敗（API + 頻道頁 HTML 皆失敗），本輪跳過`); continue; }
          vids = await latestVideosViaRss(cid);
        }
        const fresh = vids.filter(v => !knownVideoIds.has(v.videoId)); // Phase 13 P1-6：已知片跳過 LLM
        say(`${chLabel}${ytApiOk ? "" : "（RSS）"}: ${vids.length} 个近${LOOKBACK_DAYS}天视频${vids.length - fresh.length ? `（${vids.length - fresh.length} 個已入庫，跳過結構化——增量發現慳 quota）` : ""}`);
        for (const v of fresh.slice(0, 4)) {
          // Phase 16：多專家訪談頻道——按標題歸因追蹤專家，唔中即跳過（唔入庫）
          let expertId = ch.expertId, expertName = ch.expertName;
          if (ch.multi) {
            const hit = matchExpertByTitle(v.title);
            if (!hit) { say(`  ${v.videoId}: 標題無追蹤專家，跳過——《${v.title.slice(0, 40)}》`); continue; }
            expertId = hit.expertId; expertName = hit.expertName;
            say(`  ${v.videoId}: 標題命中追蹤專家 ${expertName}`);
          }
          let summary = v.title, signals: SnapshotSignal[] = [], horizon: "macro" | "theme" | "event" = "theme";
          // 优先字幕级解读：Innertube 直連 → Supadata（伺服器主力）→ kome 代理兜底，都抓不到才退回官方简介
          const tDirect = await getTranscript(v.videoId);
          const tSupa = tDirect.text ? null : await getTranscriptViaSupadata(v.videoId);
          const tKome = (tDirect.text ?? tSupa?.text) ? null : await getTranscriptViaKome(v.videoId);
          const transcript = tDirect.text ?? tSupa?.text ?? tKome?.text ?? null;
          const content = transcript ?? v.description.slice(0, 3000);
          const contentType = transcript ? "完整字幕" : "官方简介";
          if (transcript) say(`  ${v.videoId}: 字幕 ${transcript.length} 字`);
          // Phase 13 P1-5 + Phase 19：字幕攞唔到要記低逐路死因（直連 / Supadata / kome 代理），唔准靜默降級
          else if (v.description) say(`  ${v.videoId}: ⚠ 字幕不可用（① ${tDirect.reason ?? "?"}；② ${tSupa?.reason ?? "未嘗試"}；③ ${tKome?.reason ?? "未嘗試"}）——降級用官方簡介（${Math.min(v.description.length, 3000)} 字）`);
          else { say(`  ${v.videoId}: ⚠ 字幕不可用且 RSS 無官方簡介——無字幕級證據，跳過`); continue; }
          if (KIMI_KEY) {
            try {
              const out = await structureWithKimi(expertName, v.title, content, v.publishedAt.slice(0, 10), contentType);
              summary = out.summary; signals = out.signals; horizon = out.horizon;
            } catch (e: any) { say(`  Kimi结构化失败(${v.videoId}): ${e.message}`); }
          }
          views.push({
            expertId, expertName,
            date: v.publishedAt.slice(0, 10), channel: `YouTube ${chLabel} · ${contentType}`,
            title: v.title, summary, url: `https://www.youtube.com/watch?v=${v.videoId}`,
            videoId: v.videoId, signals, horizon, decayWeight: decay(v.publishedAt, now, horizon),
          });
        }
      } catch (e: any) { say(`${chLabel} 失败: ${e.message}`); }
    }
    // YouTube 字幕源不可達時：不做專家名義的搜索兜底——實測模型會編造「某專家於某日說了某話」
    // 及假鏈接（example123/abc123），對真金決策的危害大於 0 條觀點。專家觀點必須字幕級證據，
    // 受限網絡下寧缺毋濫，顯式記錄；開放網絡（發布後）自動恢復字幕級抓取。
    if (!ytApiOk && !ytWebOk) {
      say("⚠ 專家 YouTube 字幕源本輪不可用——專家觀點需字幕級證據，受限網絡下寧缺毋濫跳過（新聞面由下方主題掃描補位）");
    }
    // ---- 專家新聞通道（Wind 財經新聞搜索 · 經 agent-gw，受限網絡可達）----
    // 以專家全名檢索財經媒體報道/訪談——真實 URL+日期+全文。防誤配：
    // ① 全名（含簡繁/譯名變體）必須出現在標題或正文，否則視為同名異人丟棄（實測「蔡金強」誤中「中信建投金强」）
    // ② 限近 LOOKBACK_DAYS 天 ③ 每人最多 2 條最新。零命中誠實記錄，不編造。
    const WIND_EXPERTS: { name: string; expertId: string; variants: string[] }[] = [
      { name: "蔡金強", expertId: "choi", variants: ["蔡金強", "蔡金强"] },
      { name: "譚新強", expertId: "tam", variants: ["譚新強", "谭新强"] },
      { name: "洪灝", expertId: "hong", variants: ["洪灝", "洪灏"] },
      { name: "林本利", expertId: "lambl", variants: ["林本利"] },
      { name: "林一鳴", expertId: "lamy", variants: ["林一鳴", "林一鸣"] },
      { name: "莊太量", expertId: "chong", variants: ["莊太量", "庄太量"] },
      { name: "Jurrien Timmer", expertId: "timmer", variants: ["jurrien timmer", "timmer", "蒂默"] },
      { name: "蔡嘉民", expertId: "calvin", variants: ["蔡嘉民"] },
    ];
    const gwOk = await probeHost("https://agent-gw.kimi.com/");
    if (gwOk) {
      const pushWindViews = async (name: string, expertId: string, variants: string[]): Promise<number> => {
        const csv = await gwDatasourceCall("wind", "wind_get_financial_news", { query: name, file_path: `/tmp/wind_news_${expertId}.csv` });
        if (!csv) { say(`Wind新聞(${name}): 網關無返回`); return 0; }
        const cutoff = Date.now() - LOOKBACK_DAYS * 86400000;
        const rows = csvToRecords(csv)
          .filter(r => {
            const hay = (String(r.title ?? "") + "\n" + String(r.content ?? "")).toLowerCase();
            return variants.some(v => hay.includes(v.toLowerCase()));
          })
          .filter(r => /^\d{4}-\d{2}-\d{2}/.test(String(r.date ?? "")) && new Date(String(r.date).slice(0, 10)).getTime() >= cutoff)
          .sort((a, b) => String(b.date).localeCompare(String(a.date)))
          .slice(0, 2);
        let added = 0;
        for (const r of rows) {
          const date = String(r.date).slice(0, 10);
          const title = String(r.title ?? "").trim().slice(0, 200);
          const content = String(r.content ?? "");
          const url = String(r.url ?? "");
          if (!title || content.length < 80) continue;
          let summary = title, signals: SnapshotSignal[] = [], horizon: "macro" | "theme" | "event" = "theme";
          if (KIMI_KEY) {
            try {
              const out = await structureWithKimi(name, title, content.slice(0, 9000), date, "財經媒體報道/訪談全文");
              summary = out.summary; signals = out.signals; horizon = out.horizon;
            } catch (e: any) { say(`  Kimi結構化失敗（Wind:${name}）: ${e.message}`); } // Phase 13 P1-5：唔准靜默
          }
          views.push({
            expertId, expertName: name, date, channel: "Wind財經新聞 · 媒體報道/訪談",
            title, summary, url, signals, horizon, decayWeight: decay(date, now, horizon),
          });
          added++;
        }
        say(`Wind新聞(${name}): ${added} 條命中（名實相符 · 近${LOOKBACK_DAYS}天）`);
        return added;
      };
      const windCounts = await pool(2, WIND_EXPERTS.map(e => () => pushWindViews(e.name, e.expertId, e.variants)));
      say(`Wind新聞(專家通道): 8 位專家共 ${windCounts.reduce((s, x) => s + x, 0)} 條`);
    } else {
      say("⚠ agent-gw 不可達——Wind 專家新聞通道本輪跳過");
    }
    // 来源扩展：Brave Search 全网检索各专家近期新闻/专栏（报章、X转载、媒体专访）
    const BRAVE_KEY = process.env.BRAVE_API_KEY ?? "";
    const EXPERT_QUERIES = ["蔡金強", "譚新強", "洪灝", "林本利", "林一鳴", "莊太量", "Jurrien Timmer"];
    if (BRAVE_KEY && braveOk) {
      for (const q of EXPERT_QUERIES) {
        try {
          const r = await tfetch(`https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(q + " 市場 投資 觀點")}&count=4&freshness=pm&text_decorations=false`, {
            headers: { "X-Subscription-Token": BRAVE_KEY, Accept: "application/json" },
          });
          if (!r.ok) { say(`Brave(${q}): HTTP ${r.status}`); continue; }
          const j: any = await r.json();
          const results = (j.web?.results ?? []).slice(0, 3);
          for (const it of results) {
            const age = it.age ?? "";
            let summary = it.description ?? it.title, signals: SnapshotSignal[] = [], horizon: "macro" | "theme" | "event" = "theme";
            const dm = /(\d{4})[年\-\/](\d{1,2})[月\-\/](\d{1,2})/.exec(age);
            if (!dm) { say(`Brave(${q}): 跳過無日期條目（不猜日期——日期不明的新聞不入庫）`); continue; }
            const dateGuess = `${dm[1]}-${dm[2].padStart(2, "0")}-${dm[3].padStart(2, "0")}`;
            if (KIMI_KEY) {
              try {
                const out = await structureWithKimi(q, it.title ?? "", `${it.description ?? ""}\n来源:${it.url}`, dateGuess, "新闻摘要");
                summary = out.summary; signals = out.signals; horizon = out.horizon;
              } catch (e: any) { say(`  Kimi結構化失敗（Brave:${q}）: ${e.message}`); } // Phase 13 P1-5：唔准靜默
            }
            views.push({
              expertId: "news", expertName: q,
              date: dateGuess, channel: `全网新闻 · Brave`,
              title: it.title ?? q, summary, url: it.url ?? "",
              signals, horizon, decayWeight: decay(dateGuess, now, horizon),
            });
          }
          say(`Brave(${q}): ${results.length} 条`);
        } catch (e: any) { say(`Brave(${q}) 失败: ${e.message}`); }
      }
    } else {
      // Brave 不可達/未配置時的兜底：Kimi 聯網搜索按「主題」掃描市場新聞面（不綁定專家個人名義——
      // 主題級媒體匯總的編造風險遠低於「某專家說了某話」，且與 Brave 新聞同級處理）
      const THEME_QUERIES = ["半導體 AI 芯片", "黃金 白銀 貴金屬", "中國A股 港股 中概", "美股 標普 納指", "美債 利率 聯儲局", "能源 銅 商品", "比特幣 加密貨幣"];
      const counts = await pool(4, THEME_QUERIES.map(q => () =>
        pushKimiViews(q, "scan", "主題掃描 · Kimi聯網搜索（媒體匯總，非專家背書）")));
      const total = counts.reduce((s, x) => s + x, 0);
      say(`Kimi搜索(主題掃描): ${THEME_QUERIES.length} 個主題共 ${total} 條`);
    }

    // 併入上一快照仍未衰減的觀點——否則每日管道會沖掉手動錄入與前幾輪抓取
    // Phase 14：去重 key 由 raw `url|title` 改為 dedupeKey（專家|標題|日期）——
    // Wind URL 帶隨機 useless 參數，raw URL 去重失效令同一觀點重複入庫
    try {
      const prevRows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
      if (prevRows[0]) {
        const prev = JSON.parse(prevRows[0].payload) as Snapshot;
        const seen = new Set(views.map(dedupeKey));
        const carry = (prev.views ?? [])
          .filter(v => !seen.has(dedupeKey(v)))
          // Phase 13 P0-3：carry TTL 60→120 日——90 交易日窗口（≈180 曆日）要先有機會成熟，60 日 TTL 會殺晒長窗樣本
          .filter(v => /^\d{4}-\d{2}-\d{2}/.test(v.date) && Date.now() - new Date(v.date).getTime() < 120 * 86400000)
          // Phase 13 P1-4：未來日期唔准 carry（上限今日+1日），響亮記錄
          .filter(v => {
            if (new Date(v.date).getTime() > Date.now() + 86400000) { say(`⚠ 日期守衛：上一快照觀點《${(v.title ?? "").slice(0, 30)}》日期 ${v.date} 喺未來，唔予 carry`); return false; }
            return true;
          });
        // Phase 13 P0-3：保留原 view.horizon 計衰減（舊數據無 horizon 欄 → 默認 theme）；加 carried 標記
        for (const v of carry) views.push({ ...v, carried: true, decayWeight: decay(v.date, now, normalizeHorizon(v.horizon)) });
        if (carry.length) say(`併入上一快照 ${carry.length} 條未衰減觀點（含手動錄入/前期抓取，TTL 120 日）`);
      }
    } catch (e: any) {
      // Phase 14：唔准靜默——carry 失敗即歷史觀點本輪全部唔見，必須響亮記錄
      say(`⚠ 上一快照讀取失敗，歷史觀點本輪唔併入: ${e?.message ?? e}`);
    }
    // 信號保留守衛（2026-10-09）：新抓觀點若結構化失敗（signals 空），而上一快照同 key 觀點有信號，
    // 沿用舊信號——唔准「重抓空殼覆蓋舊信號」（8 月事故根因：Moonshot 停擺期間 16 條信號被清空）
    {
      const prevRows2 = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1).catch(() => []);
      if (prevRows2[0]) {
        try {
          const prevViews = (JSON.parse(prevRows2[0].payload) as Snapshot).views ?? [];
          const { merged, rescued } = preserveCarriedSignals(views, prevViews);
          if (rescued) { views.length = 0; views.push(...merged); say(`信號保留：${rescued} 條觀點沿用上一快照嘅已結構化信號（今輪重抓未結構化）`); }
        } catch {}
      }
    }
    // Phase 14：全局觀點去重第二道防線（carry 階段已按 dedupeKey 擋咗舊版，呢度擋今輪新抓嘅自身重複，
    // 例如主題掃描 7 個主題撞返同一篇文）。正序保留先出現者（新抓優先），in-place 剔除重複。
    {
      const seenV = new Set<string>();
      let dupCount = 0;
      for (let i = 0; i < views.length; i++) {
        const k = dedupeKey(views[i]);
        if (seenV.has(k)) { views.splice(i, 1); i--; dupCount++; } else seenV.add(k);
      }
      if (dupCount) say(`⚠ 去重：剔除 ${dupCount} 條重複觀點（專家|標題|日期 相同）`);
    }
    if (views.length > 60) views.length = 60;

    const { changes, note, watchlist } = await buildSuggestions(views);
    const snapshot: Snapshot = {
      date: now.toISOString().slice(0, 10),
      generatedAt: now.toISOString(),
      views, suggested: changes, suggestedNote: note,
      lastRebalanceDate: effectiveLastRebalanceDate(),
      brakeStatus: lastBrakeStatus,
      watchlist,
    };
    await db.insert(snapshots).values({ kind: "daily", payload: JSON.stringify(snapshot) });
    await sendNotification(snapshot);
    const json = JSON.stringify(snapshot, null, 2);
    for (const dir of ["public/data", "dist/public/data"]) {  // 同上：serve 根目录是 dist/public
      try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/snapshot.json`, json); } catch (e: any) { console.warn(`[pipeline] ⚠ snapshot.json 寫入 ${dir} 失敗（靜態鏡像將陳舊）:`, e?.message ?? e); }
    }
    await updatePerformance();
    say(`完成：${views.length} 条观点，${changes.length} 项建议；刹车层状态=${lastBrakeStatus}`);
    await db.update(pipelineRuns).set({ status: "success", log: logs.join("\n"), finishedAt: new Date() }).where(eqRun(run.id));
    return { ok: true, log: logs.join("\n") };
  } catch (e: any) {
    say(`管道失败: ${e.message}`);
    // 管道前半段失败唔代表淨值唔可以追加——淨值追加同觀點採集解耦，失敗都照試
    try { await updatePerformance(); } catch (e2: any) { console.warn("[pipeline] ⚠ 失敗後淨值追加都失敗:", e2?.message ?? e2); }
    await db.update(pipelineRuns).set({ status: "failed", log: logs.join("\n"), finishedAt: new Date() }).where(eqRun(run.id));
    return { ok: false, log: logs.join("\n") };
  }
}

// 防并发锁：runNow / 调度器 / 手动重试不会同时跑两个管道
let runLock = false;

export async function runPipeline(): Promise<{ ok: boolean; log: string }> {
  if (runLock) { console.log("[pipeline] 已有运行中的管道，跳过"); return { ok: false, log: "已有运行中的管道，本次跳过" }; }
  runLock = true;
  // 硬超时兜底：即使某个内部调用逃逸了 tfetch 超时（如 DB 挂起），12 分钟后强制把 running 标记为 failed 并释放锁
  const watchdog = setTimeout(() => {
    void (async () => {
      try {
        const db = getDb();
        await db.update(pipelineRuns).set({ status: "failed", log: "管道超过 12 分钟硬超时，强制终止（兜底恢复）", finishedAt: new Date() })
          .where(eq(pipelineRuns.status, "running"));
        console.log("[pipeline] 硬超时：遗留 running 记录已强制标记 failed");
      } catch { /* ignore */ }
      runLock = false;
    })();
  }, 12 * 60 * 1000);
  try {
    return await runPipelineInner();
  } finally {
    clearTimeout(watchdog);
    runLock = false;
  }
}

import { eq, sql } from "drizzle-orm";
const eqRun = (id: number) => eq(pipelineRuns.id, id);

export async function getStatus(): Promise<PipelineStatus> {
  const db = getDb();
  const runs = await db.select().from(pipelineRuns).orderBy(desc(pipelineRuns.id)).limit(1);
  // Phase 17：snapshotDate 只睇觀點快照 kind——performance/rebalance_audit 行唔算快照
  const snaps = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
  return {
    lastRunAt: runs[0]?.createdAt?.toISOString() ?? null,
    lastStatus: runs[0]?.status ?? null,
    lastLog: runs[0]?.log ?? null,
    snapshotDate: snaps[0]?.createdAt?.toISOString() ?? null,
  };
}

// Phase 17：kind 過濾 + payload 驗證——rebalance_audit/performance 行唔係觀點快照；
// parse 後驗證 Array.isArray(views)，唔啱就 skip 落下一行（最多試最近 5 行）
export async function latestSnapshot(): Promise<Snapshot | null> {
  const db = getDb();
  const rows = await db.select().from(snapshots)
    .where(snapshotKindFilter())
    .orderBy(desc(snapshots.id)).limit(5);
  return pickSnapshotFromRows(rows);
}

// 前向实盘追踪：从冻结日(2026-07-20)起按 CURRENT_WEIGHTS 逐日追加净值 → public/data/performance.json
// 淨值追加（每日調度/調倉記錄後即場觸發；export 俾維運可以單獨手動補跑）
export async function updatePerformance(): Promise<void> {
  try {
    const { readFileSync } = await import("node:fs");
    const path = "public/data/performance.json";
    if (!existsSync2(path)) return;
    const perf = JSON.parse(readFileSync(path, "utf8"));
    const lastDate = perf.dates[perf.dates.length - 1]; // MM-DD（展示格式）
    // 跨年邊界：MM-DD 字串比較在 12-31 → 01-01 會斷裂，內部一律用完整日期比較
    const y0 = Number(String(perf.frozenSince ?? "2026-01-01").slice(0, 4));
    const lastYear = lastDate >= String(perf.frozenSince ?? "2026-01-01").slice(5, 10) ? y0 : y0 + 1;
    const lastFull = `${lastYear}-${lastDate}`;
    // 拉取所有持仓 ETF 日线（双引擎，受限网络走 agent-gw 网关）
    // f = 完整日期（排序/比較用，跨年安全）；d = MM-DD（沿用展示格式）
    const closes: Record<string, { d: string; c: number; f: string }[]> = {};
    // 雙引擎行情（直連 → agent-gw 網關兜底）：受限網絡下淨值追加不再靜默停擺
    for (const t of [...Object.keys(CURRENT_WEIGHTS), "ACWI", "AGG"]) {
      try {
        const rows = await fetchCloses(t, "6mo");
        if (!rows) continue;
        closes[t] = rows.filter(x => x.date >= lastFull).map(x => ({ d: x.date.slice(5, 10), c: x.close, f: x.date }));
      } catch {}
    }
    // 逐日追加：新交易日的组合日收益 = Σ w_i × 个券日收益（分段權重——調倉日收市執行，下一交易日起用新權重）
    // Phase 15：weightsTimeline 由 recordRebalance 寫入；舊檔無此欄 → 以 frozenSince + CURRENT_WEIGHTS 為基準段（口徑不變）
    const timeline: WeightsTimelineEntry[] = Array.isArray(perf.weightsTimeline) && perf.weightsTimeline.length
      ? perf.weightsTimeline
      : [{ from: String(perf.frozenSince ?? LAST_REBALANCE_DATE), w: { ...CURRENT_WEIGHTS } }];
    perf.weightsTimeline = timeline;
    if (!closes["ACWI"]?.length) {
      console.warn(`[pipeline] ⚠ ACWI 行情缺失或無新數據，淨值今輪無法追加（成功載入 ticker 數：${Object.keys(closes).length}，lastDate=${lastFull}）`);
    }
    const tickers = Object.keys(CURRENT_WEIGHTS);
    const newDates = (closes["ACWI"] ?? []).filter(x => x.f > lastFull).sort((x, y) => x.f.localeCompare(y.f));
    let port = perf.portfolio[perf.portfolio.length - 1];
    let bench = perf.benchmark[perf.benchmark.length - 1];
    const prevClose: Record<string, number> = {};
    for (const t of Object.keys(closes)) {
      const rows = closes[t];
      prevClose[t] = (rows.filter(x => x.f <= lastFull).pop() ?? rows[0])?.c;
    }
    for (const ndRow of newDates) {
      const nd = ndRow.d;
      const segW = weightsForDate(timeline, ndRow.f);
      let rp = 0, rb = 0, okCount = 0;
      for (const t of tickers) {
        const row = (closes[t] ?? []).find(x => x.f === ndRow.f);
        if (row && prevClose[t]) { rp += ((segW[t] ?? 0) / 100) * (row.c / prevClose[t] - 1); okCount++; }
      }
      const a = (closes["ACWI"] ?? []).find(x => x.f === ndRow.f)?.c, g = (closes["AGG"] ?? []).find(x => x.f === ndRow.f)?.c;
      if (a && prevClose["ACWI"]) rb += 0.6 * (a / prevClose["ACWI"] - 1);
      if (g && prevClose["AGG"]) rb += 0.4 * (g / prevClose["AGG"] - 1);
      if (okCount === 0) continue;
      port = +(port * (1 + rp)).toFixed(2); bench = +(bench * (1 + rb)).toFixed(2);
      perf.dates.push(nd); perf.portfolio.push(port); perf.benchmark.push(bench);
      for (const t of Object.keys(closes)) { const row = closes[t].find(x => x.f === ndRow.f); if (row) prevClose[t] = row.c; }
    }
    perf.asOf = perf.dates[perf.dates.length - 1];
    // 全部統計由淨值序列即時重算（舊版只更新兩行，netRet 凍結 45 日——Phase 8 修復）
    perf.stats = computePerfStats({
      dates: perf.dates, portfolio: perf.portfolio, benchmark: perf.benchmark,
      turnover: perf.stats?.turnover ?? 125, costDrag: perf.stats?.costDrag ?? 0.12,
    });
    const json = JSON.stringify(perf);
    // 生产静态根目录是 ./dist/public（api/lib/vite.ts serveStatic）——必须写 dist/public/data，
    // 否则管道每日追加的净值永远 serve 成 build 时快照（「回报不更新」的真正根因之一）
    // Phase 17：檔案係鏡像（本地開發/zip 用），DB 先係真相——檔案雙寫照舊保留
    for (const dir of ["public/data", "dist/public/data"]) {
      try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/performance.json`, json); } catch (e: any) { console.warn(`[pipeline] ⚠ performance.json 寫入 ${dir} 失敗（淨值將停止更新）:`, e?.message ?? e); }
    }
    // Phase 17：DB 寫入（真相源）——同最新 kind='performance' 行字串相同就 skip
    //（防 30 分鐘定時器喺無新交易日時刷行數）；DB 失敗只 warn 唔阻檔案鏡像
    try {
      const db = getDb();
      const rows = await db.select().from(snapshots)
        .where(eq(snapshots.kind, "performance"))
        .orderBy(desc(snapshots.id)).limit(1);
      if (!rows[0] || rows[0].payload !== json) {
        await db.insert(snapshots).values({ kind: "performance", payload: json });
      }
    } catch (e: any) { console.warn("[pipeline] ⚠ performance DB 寫入失敗（檔案鏡像已保存，前端 DB 優先讀取會暫時陳舊）:", e?.message ?? e); }
    console.log(`[pipeline] performance.json 已更新至 ${perf.asOf}（新增 ${newDates.length} 个交易日）`);
  } catch (e: any) { console.log("[pipeline] performance 更新失败:", e.message); }
}
function existsSync2(p: string) { try { return statSync(p).isFile(); } catch { return false; } }
import { statSync } from "node:fs";

// ---- Phase 17：淨值 DB 化——DB 係真相源，performance.json 檔案係鏡像/fallback ----
// DB-only 讀取（boot 檔案鏡像同步用）：有行回 parsed object，冇行/甩底回 null
async function latestPerformanceFromDb(): Promise<any | null> {
  try {
    const db = getDb();
    const rows = await db.select().from(snapshots)
      .where(eq(snapshots.kind, "performance"))
      .orderBy(desc(snapshots.id)).limit(1);
    if (!rows[0]) return null;
    const p = JSON.parse(rows[0].payload);
    return p && typeof p === "object" ? p : null;
  } catch (e: any) {
    console.warn("[pipeline] ⚠ performance DB 讀取失敗:", e?.message ?? e);
    return null;
  }
}

// DB 優先；冇行/甩底 → 檔案 fallback；都冇 → null（俾 tRPC pipeline.performance 用）
export async function latestPerformance(): Promise<any | null> {
  const fromDb = await latestPerformanceFromDb();
  if (fromDb) return fromDb;
  try {
    if (existsSync2("public/data/performance.json")) {
      const p = JSON.parse(readFileSync2("public/data/performance.json"));
      if (p && typeof p === "object") return p;
    }
  } catch (e: any) { console.warn("[pipeline] ⚠ performance.json 檔案 fallback 讀取失敗:", e?.message ?? e); }
  return null;
}

// Webhook 通知：按平台 URL 自动识别格式（企业微信 / Discord / Slack / 通用）
async function sendNotification(snap: Snapshot) {
  const url = process.env.NOTIFICATION_WEBHOOK_URL;
  if (!url || snap.suggested.length === 0) return;
  const lines = snap.suggested.map(c => `${c.ticker}: ${c.from}% → ${c.to}%（${c.reason.slice(0, 40)}）`);
  const text = `【ETF组合】${snap.date} 有 ${snap.suggested.length} 项待复核调仓建议：\n${lines.join("\n")}\n请打开网站「每日更新」页复核。`;
  let body: any;
  if (/qyapi\.weixin\.qq\.com/.test(url)) body = { msgtype: "text", text: { content: text } };       // 企业微信
  else if (/discord/.test(url)) body = { content: text };                                            // Discord
  else if (/hooks\.slack\.com/.test(url)) body = { text };                                           // Slack
  else body = { text };                                                                              // 通用
  try {
    await tfetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    console.log("[pipeline] 通知已推送");
  } catch (e: any) { console.log("[pipeline] 通知推送失败:", e.message); }
}

// 每日定时：固定在香港时间 08:00 运行（开盘前），之后每24小时；服务启动60秒后也会补跑一次
function msUntilNext8amHKT() {
  const now = new Date();
  const hkt = new Date(now.getTime() + 8 * 3600 * 1000);
  const next = new Date(Date.UTC(hkt.getUTCFullYear(), hkt.getUTCMonth(), hkt.getUTCDate(), 0, 0, 0)); // HKT 08:00 = UTC 00:00
  let t = next.getTime(); // HKT 08:00 = UTC 00:00，不得再減 8 小時（否則變成 HKT 00:00 午夜運行）
  if (t <= now.getTime()) t += 24 * 3600 * 1000;
  return t - now.getTime();
}

// 进程重启时把上次遗留的 running 记录标记为 failed（僵尸恢复，否则状态页永远卡在 running）
async function recoverStaleRuns() {
  try {
    const db = getDb();
    await db.update(pipelineRuns).set({ status: "failed", log: "进程重启：遗留 running 记录标记为 failed（僵尸恢复）", finishedAt: new Date() })
      .where(eq(pipelineRuns.status, "running"));
  } catch { /* ignore */ }
}

// ---- Phase 17 B4：payload MEDIUMTEXT idempotent 遷移 ----
// snapshots.payload 原本係 TEXT（上限 65,535 bytes）——快照 34 views ≈ 40KB，
// views 上限 60 → 約 70KB 會超限（潛伏炸彈）。boot 時 ALTER 一次；
// 已經係 MEDIUMTEXT 重複執行係無害嘅（MySQL 照樣成功），權限唔够就 warn 唔阻啟動。
async function ensurePayloadMediumtext(): Promise<void> {
  try {
    const db = getDb();
    await db.execute(sql`ALTER TABLE snapshots MODIFY payload MEDIUMTEXT NOT NULL`);
    console.log("[db] snapshots.payload MEDIUMTEXT 遷移完成（或已經係 MEDIUMTEXT）");
  } catch (e: any) {
    console.warn("[db] payload MEDIUMTEXT 遷移跳過/失敗:", e?.message ?? e);
  }
}

// ---- Phase 17 B5：boot 檔案鏡像同步 ----
// DB 係真相源；boot 時若 DB 版新過檔案（或檔案唔存在）就用 DB 覆寫雙目錄鏡像，
// 令 zip/本地靜態鏡像唔會長期陳舊；發布容器 ephemeral 都無所謂因為前端而家讀 API。
// 全部 warn-only，任何一步失敗都唔阻啟動。
async function syncFileMirrorsFromDb(): Promise<void> {
  // snapshot.json：DB 最新快照 generatedAt 新過檔案（或檔案唔存在）先覆寫
  try {
    const snap = await latestSnapshot();
    if (snap?.generatedAt) {
      let fileAt = 0;
      try { fileAt = new Date(JSON.parse(readFileSync2("public/data/snapshot.json"))?.generatedAt ?? 0).getTime() || 0; } catch { /* 檔案唔存在/甩格式 → 當 0 */ }
      if (new Date(snap.generatedAt).getTime() > fileAt) {
        writeJsonBothDirs("snapshot.json", JSON.stringify(snap, null, 2), "靜態鏡像將陳舊");
        console.log("[boot] snapshot.json 檔案鏡像已由 DB 覆寫（DB 較新/檔案缺失）");
      }
    }
  } catch (e: any) { console.warn("[boot] ⚠ snapshot.json 鏡像同步失敗（唔阻啟動）:", e?.message ?? e); }
  // performance.json：DB 有 kind='performance' 行先覆寫
  try {
    const perf = await latestPerformanceFromDb();
    if (perf) writeJsonBothDirs("performance.json", JSON.stringify(perf), "淨值檔案鏡像將陳舊");
  } catch (e: any) { console.warn("[boot] ⚠ performance.json 鏡像同步失敗（唔阻啟動）:", e?.message ?? e); }
  // rebalances.json：DB 有 audit 行先覆寫（唔好喺 DB 零行時用空檔案覆蓋種子）
  try {
    const recs = await listRuntimeRebalancesFromDb();
    if (recs && recs.length) writeJsonBothDirs("rebalances.json", JSON.stringify({ records: recs }, null, 2), "調倉記錄檔案鏡像將陳舊");
  } catch (e: any) { console.warn("[boot] ⚠ rebalances.json 鏡像同步失敗（唔阻啟動）:", e?.message ?? e); }
}

// ---- Phase 19c：build-time 種子真正落地（手動補錄觀點唔准再因重新發布而丟失） ----
// 背景：每次 build_version 發布都配全新空 DB——舊庫入面手動補錄嘅字幕級觀點（用戶真金白銀決策依據）
// 會隨舊容器一齊消失（實例：2026-10-05 補錄嘅蔡金強片，10-06 新部署上線後連同成個庫被重置）。
// 修法：boot 時若 DB 零觀點快照、且 image 烘入咗 public/data/snapshot.json 種子（發布前將生產快照 commit 入 repo），
// 就先灌入 DB（kind='manual'）；之後 60s 補跑會原樣 carry 呢批觀點 + 加新鮮掃描。
// warn-only 唔阻啟動；DB 有料/檔案缺失/格式唔啱 → 靜靜哋 skip（寧缺毋濫，唔會雙重灌入）。
async function seedDbFromFileIfEmpty(): Promise<void> {
  // A) 觀點快照種子：DB 零觀點快照 → 由 image 種子灌入
  try {
    const snap = await latestSnapshot();
    if (!snap) {
      let raw: string | null = null;
      try { raw = readFileSync2("public/data/snapshot.json"); } catch { /* image 無種子檔 → skip */ }
      if (raw) {
        const s = JSON.parse(raw) as Snapshot;
        if (s && Array.isArray(s.views) && s.views.length > 0) {
          const db = getDb();
          await db.insert(snapshots).values({ kind: "manual", payload: JSON.stringify(s) });
          console.log(`[boot] DB 空——已由 image 種子灌入 ${s.views.length} 條觀點（快照 ${s.date}），補跑管道會 carry 延續`);
        }
      }
    }
  } catch (e: any) { console.warn("[boot] ⚠ 觀點種子灌入失敗（唔阻啟動）:", e?.message ?? e); }
  // B) 調倉記錄種子：DB 零 audit 行 → 由 rebalances.json 逐條 replay 灌入（格式同 recordRebalance：payload={record,effective}）
  //    用戶批核過嘅調倉係真金白銀已執行動作——重新發布丟咗會令生效權重唔啱（實例：2026-10-06 調倉 #4 險些隨舊容器消失）
  try {
    const dbRows = await listRuntimeRebalancesFromDb();
    if (dbRows && dbRows.length) return; // DB 有 audit 行 → 唔使種子
    const recs = listRuntimeRebalancesFromFile();
    if (!recs.length) return;
    const db = getDb();
    let w: Record<string, number> = { ...CURRENT_WEIGHTS };
    for (const r of recs) {
      w = applyRebalances(w, [r]);
      await db.insert(snapshots).values({ kind: "rebalance_audit", payload: JSON.stringify({ record: r, effective: w }) });
    }
    console.log(`[boot] DB 無調倉記錄——已由 image 種子灌入 ${recs.length} 條調倉記錄（最新 ${recs[recs.length - 1].date}）`);
  } catch (e: any) { console.warn("[boot] ⚠ 調倉種子灌入失敗（唔阻啟動）:", e?.message ?? e); }
}

let started = false;
export function startScheduler() {
  if (started) return;
  started = true;
  void recoverStaleRuns();
  // Phase 17：boot 維護——payload MEDIUMTEXT 遷移（B4）+ 檔案鏡像同步（B5）。
  // 喺管道補跑判斷（下方 60s timer）之前觸發；兩者皆 warn-only 唔阻啟動。
  void ensurePayloadMediumtext();
  // Phase 19c：種子灌入要先於補跑判斷完成（否則補跑會喺空庫上由零開始，種子白灌）——
  // 攞住個 promise，下方 60s timer 開跑前 await 佢。種子本身 warn-only 唔會 reject。
  const seedDone: Promise<void> = seedDbFromFileIfEmpty().then(() => void syncFileMirrorsFromDb());
  void seedDone;
  if (!process.env.KIMI_API_KEY) { console.log("[pipeline] 无 KIMI_API_KEY，调度器未启动"); return; } // YouTube key 已非必需（kome 代理 + Wind 新聞通道），只要 Kimi 可用即可每日運行
  const ms = msUntilNext8amHKT();
  console.log(`[pipeline] 每日调度器已启动，下次运行：香港时间 08:00（${Math.round(ms / 60000)} 分钟后）`);
  setTimeout(() => {
    runPipeline().catch(console.error);
    setInterval(() => { runPipeline().catch(console.error); }, 24 * 3600 * 1000);
  }, ms);
  // 補跑機制：進程重啟 60 秒後檢查，錯過 08:00 就立即補跑一次。
  // Phase 16：門檻收緊——發布容器會瞓覺，舊版單一 20h 門檻太鬆（昨日快照 14h 舊都唔補 → 「專家觀點無更新」）。
  // 觸發條件：① 快照缺失；② 快照日期唔係今日（HKT）且齡 >6h；③ 任何情況齡 >20h。
  setTimeout(() => {
    void (async () => {
      try {
        await seedDone; // Phase 19c：等種子灌完先判斷——空庫場景下補跑要 carry 種子觀點，唔係由零開始
        const snap = await latestSnapshot();
        const ageH = snap ? (Date.now() - new Date(snap.generatedAt).getTime()) / 3600_000 : Infinity;
        const todayHKT = new Date(Date.now() + 8 * 3600_000).toISOString().slice(0, 10); // HKT 今日（同 Phase 15 口徑）
        let reason: string | null = null;
        if (!snap) reason = "無任何快照";
        else if (snap.date !== todayHKT && ageH > 6) reason = `快照日期 ${snap.date} 唔係今日（HKT ${todayHKT}）且已 ${ageH.toFixed(1)} 小時未更新`;
        else if (ageH > 20) reason = `最新快照已 ${ageH.toFixed(1)} 小時未更新`;
        if (reason) { console.log(`[pipeline] 補跑觸發：${reason}——立即補跑一次`); await runPipeline(); }
      } catch (e: any) { console.log("[pipeline] 補跑檢查失敗:", e.message); }
    })();
  }, 60_000);
  // Phase 16：淨值輕量定時刷新——唔經主管道（唔郁觀點/建議/快照），只按最新行情追加新交易日淨值點，
  // 令「組合表現」唔使等每日 08:00 主管道先更新。失敗只 warn（updatePerformance 內部已各自 catch）；
  // 周末/休市 quotes 無新日期就自然唔會加點（內部按 lastFull 過濾，同一日期唔會重複加）。
  let perfBusy = false;
  const perfTick = async () => {
    if (perfBusy) return;
    perfBusy = true;
    try { await updatePerformance(); }
    catch (e: any) { console.warn("[pipeline] ⚠ 定時淨值刷新失敗:", e?.message ?? e); }
    finally { perfBusy = false; }
  };
  setTimeout(() => { void perfTick(); }, 150_000); // boot 後 150 秒跑第一次（讓補跑/恢復先起步）
  setInterval(() => { void perfTick(); }, 30 * 60 * 1000);
}

// 标记最新快照的建议为「已复核」
export async function acknowledgeLatest(): Promise<boolean> {
  const db = getDb();
  // Phase 17：kind 過濾——唔可以將 acknowledged 寫落 performance/rebalance_audit 行
  const rows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
  if (!rows[0]) return false;
  try {
    const snap = JSON.parse(rows[0].payload) as Snapshot;
    snap.acknowledged = true;
    snap.acknowledgedAt = new Date().toISOString();
    await db.update(snapshots).set({ payload: JSON.stringify(snap) }).where(eq(snapshots.id, rows[0].id));
    // 文件雙寫：DB 是唯一事實源，但前端 dev/prod 都讀 snapshot.json，不寫文件會導致橫幅狀態不一致
    const json = JSON.stringify(snap, null, 2);
    for (const dir of ["public/data", "dist/public/data"]) {
      try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/snapshot.json`, json); }
      catch (e: any) { console.log(`[pipeline] acknowledgeLatest 寫 ${dir}/snapshot.json 失敗:`, e.message); }
    }
    return true;
  } catch { return false; }
}

// ---- Phase 18：批核即自動記錄調倉 ----
// 用戶喺「每日更新」頁撳「批核並記錄調倉」→ 按當時所見嘅建議權重生成調倉記錄，
// 調倉記錄頁、圖表黃點、生效權重、淨值分段全部即時聯動（即 recordRebalance 嘅完整鏈路）。
// 安全邊界（同用戶確認過嘅工作流）：① 只發生喺人工批核之後，冇任何全自動調倉；
// ② 呢個動作係簿記——系統永遠唔會亦冇辦法喺券商落單，用戶必須自己執行；
// ③ dryRun=true 行全部校驗但零寫入（E2E 測試通道，唔准污染真金白銀數據）。

// 純函數（可單測）：建議 → 調倉 changes。過濾兩種嘢：重複 ticker（首個勝出）、
// 同現行生效權重一樣嘅 no-op（快照可能係舊權重時代生成，stale 建議唔好阻塞批核）。
export function buildApprovalChanges(
  suggested: { ticker: string; to: number }[],
  effective: Record<string, number>,
): { etf: string; to: number }[] {
  const seen = new Set<string>();
  const out: { etf: string; to: number }[] = [];
  for (const c of suggested) {
    if (seen.has(c.ticker)) continue;
    seen.add(c.ticker);
    if (c.to === effective[c.ticker]) continue;
    out.push({ etf: c.ticker, to: c.to });
  }
  return out;
}

export async function approveAndRecordLatest(input: { dryRun?: boolean; fundFrom?: { etf: string; to: number } } = {}): Promise<{
  ok: boolean; recorded: boolean; error?: string;
  reason?: "no-snapshot" | "no-suggestions" | "duplicate-date" | "needs-funding";
  residualPp?: number;
  record?: RuntimeRebalance; effective?: Record<string, number>; dryRun?: boolean;
}> {
  const dryTail = input.dryRun ? { dryRun: true as const } : {};
  const snap = await latestSnapshot();
  if (!snap) return { ok: false, recorded: false, reason: "no-snapshot", error: "資料庫暫無快照——請先運行更新管道", ...dryTail };
  const suggested = Array.isArray(snap.suggested) ? snap.suggested : [];
  const records = await listRuntimeRebalances();
  const ew = applyRebalances(CURRENT_WEIGHTS, records);
  const changes = buildApprovalChanges(suggested, ew);
  if (!suggested.length || !changes.length) {
    // 冇建議（或建議全部已反映喺現行權重）：批核 = 標記知悉
    if (!input.dryRun) await acknowledgeLatest();
    return { ok: true, recorded: false, reason: "no-suggestions", ...dryTail };
  }
  const todayHKT = new Date(Date.now() + 8 * 3600_000).toISOString().slice(0, 10); // HKT 今日（同 validateRebalance 口徑）
  if (records.some(r => r.date === todayHKT)) {
    // 今日已有調倉記錄（例如朝早手動記咗）——唔准重複記，只標記知悉
    if (!input.dryRun) await acknowledgeLatest();
    return { ok: true, recorded: false, reason: "duplicate-date", ...dryTail };
  }
  // Phase 18.1：引擎建議係 ±1pp 方向性 nudge，唔保證零和（例：兩項 +1pp → 總權重 102%）。
  // 真金白銀紅線：差額嘅資金來源/去向必須由用戶指明（fundFrom），系統唔准靜默替用戶揀。
  const finalChanges = input.fundFrom ? [...changes, { etf: input.fundFrom.etf, to: input.fundFrom.to }] : changes;
  const projected = { ...ew };
  for (const c of finalChanges) projected[c.etf] = c.to;
  const total = Object.values(projected).reduce((s, v) => s + v, 0);
  if (Math.abs(total - 100) > 1e-9) {
    const residual = +(total - 100).toFixed(2);
    return {
      ok: false, recorded: false, reason: "needs-funding", residualPp: residual,
      error: `建議淨${residual > 0 ? "加" : "減"}倉 ${Math.abs(residual)}pp——建議本身唔零和，請揀定資金${residual > 0 ? "來源（由邊隻 ETF 扣減）" : "去向（加落邊隻 ETF）"}先記錄；系統唔會替你靜默揀。`,
      ...dryTail,
    };
  }
  const r = await recordRebalance({
    date: todayHKT,
    trigger: `批核 ${snap.date} 快照嘅 ${changes.length} 項建議（批核即記錄通道）`,
    note: `由「每日更新」頁批核後自動記錄：權重完全照批核時所見建議${input.fundFrom ? `，差額由用戶指明 ${input.fundFrom.etf}→${input.fundFrom.to}% 補足` : ""}。此動作只係簿記——系統永遠唔會喺券商落單，請確保你已按此權重真實執行。`,
    changes: finalChanges,
    dryRun: input.dryRun,
  });
  if (!r.ok) return { ok: false, recorded: false, error: r.error, ...dryTail };
  return { ok: true, recorded: true, record: r.record, effective: r.effective, ...dryTail };
}


// ---- 手動錄入專家觀點（字幕級證據）----
// 受限網絡下 YouTube 字幕無法自動抓取的正式解法：
// 用戶在 YouTube App/網頁「顯示文字記錄」複製字幕 → 貼到網站錄入表單 →
// 與自動管道完全相同的 Kimi 結構化 → 時間衰減 → 信號 → 建議引擎。
// Phase 16：主體抽成 doAddManualView——submitManualView（async job）同舊 addManualView 共用。
// dryRun=true：行全部邏輯（含 Kimi 結構化 + 重複檢查預覽 + 建議引擎重算預覽）但跳過所有寫入
// （DB insert、snapshot.json 雙目錄寫）——E2E 測試通道，唔准污染真金白銀數據。
async function doAddManualView(input: {
  expertName: string; title: string; url?: string; date?: string; content: string; dryRun?: boolean;
}, onStage?: (s: string) => void): Promise<{ ok: boolean; summary?: string; signalCount?: number; error?: string; dryRun?: boolean }> {
  const content = (input.content ?? "").trim();
  if (content.length < 100) return { ok: false, error: "內容少於 100 字——請貼上完整字幕或正文（字幕級證據是觀點入庫門檻，防止道聽途說混入）", ...(input.dryRun ? { dryRun: true } : {}) };
  if (!input.expertName?.trim()) return { ok: false, error: "請填寫專家名", ...(input.dryRun ? { dryRun: true } : {}) };
  if (!input.title?.trim()) return { ok: false, error: "請填寫視頻/文章標題", ...(input.dryRun ? { dryRun: true } : {}) };
  const date = /^\d{4}-\d{2}-\d{2}$/.test(input.date ?? "")
    ? input.date! : new Date().toISOString().slice(0, 10);

  let summary = input.title, signals: SnapshotSignal[] = [], horizon: "macro" | "theme" | "event" = "theme";
  if (KIMI_KEY) {
    try {
      onStage?.("Kimi 結構化中（streaming）");
      const out = await structureWithKimi(input.expertName.trim(), input.title.trim(), content.slice(0, 9000), date, "手動錄入字幕/正文");
      summary = out.summary; signals = out.signals; horizon = out.horizon;
    } catch (e: any) {
      return { ok: false, error: `Kimi 結構化失敗：${e.message}`, ...(input.dryRun ? { dryRun: true } : {}) };
    }
  }
  const now = new Date();
  // Phase 16：URL 正規化——youtu.be 短鏈/si 參數歸一為 canonical watch URL 先入庫
  const canonUrl = canonicalVideoUrl(input.url);
  const videoId = parseVideoId(input.url ?? "") ?? undefined;
  const view: SnapshotView = {
    expertId: "manual", expertName: input.expertName.trim(), date,
    channel: "手動錄入 · 字幕級證據",
    title: input.title.trim().slice(0, 200), summary,
    url: canonUrl, signals, horizon, decayWeight: decay(date, now, horizon),
  };
  if (videoId) view.videoId = videoId;

  // 併入最新快照：插到最前，用全部 views 重跑建議引擎（含冷卻期與風控剎車），寫 DB + 文件
  const db = getDb();
  const rows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
  let base: Snapshot;
  try { base = rows[0] ? JSON.parse(rows[0].payload) as Snapshot : null as unknown as Snapshot; } catch { base = null as unknown as Snapshot; }
  if (!base || !Array.isArray(base.views)) {
    base = {
      date: now.toISOString().slice(0, 10), generatedAt: now.toISOString(),
      views: [], suggested: [], suggestedNote: "",
      lastRebalanceDate: effectiveLastRebalanceDate(), brakeStatus: "ok",
    };
  }
  // Phase 13 P1-6：url|title 重複 → 拒絕並提示（防止同一觀點重複入庫放大信號權重）
  // Phase 16：去重升級——videoId 相同 OR canonical URL 相同 OR 標題相同先拒
  // （舊版 `v.url === view.url` 字串全等會被 youtu.be 短鏈繞過，同一條片重複入庫放大信號——真 bug）
  const isDup = base.views.some(v =>
    (!!view.videoId && (v.videoId === view.videoId || parseVideoId(v.url ?? "") === view.videoId)) ||
    (!!view.url && !!(v.url ?? "").trim() && canonicalVideoUrl(v.url) === view.url) ||
    v.title === view.title);
  if (isDup) {
    return { ok: false, error: "該觀點（相同 videoId / 相同 URL / 相同標題）已在觀點庫中——請勿重複錄入", ...(input.dryRun ? { dryRun: true } : {}) };
  }
  base.views = [view, ...base.views].slice(0, 60);
  onStage?.("合併快照＋重算建議");
  const { changes, note, watchlist } = await buildSuggestions(base.views);
  base.suggested = changes; base.suggestedNote = note; base.watchlist = watchlist;
  base.generatedAt = now.toISOString();
  // 只在新建议出现时重置复核状态；无新建议时保留原状态（否则会把未复核的待办建议静默标记为已复核）
  if (changes.length > 0) { base.acknowledged = false; base.acknowledgedAt = undefined; }
  else if (base.acknowledged == null) base.acknowledged = true;
  if (input.dryRun) {
    onStage?.("dryRun：跳過寫入");
    console.log(`[pipeline] 手動錄入 dryRun（唔寫入 DB/檔案）：${input.expertName}《${input.title.slice(0, 40)}》→ ${signals.length} 個信號，新建議預覽 ${changes.length} 項`);
    return { ok: true, summary, signalCount: signals.length, dryRun: true };
  }
  onStage?.("寫入數據庫");
  await db.insert(snapshots).values({ kind: "manual", payload: JSON.stringify(base) });
  const json = JSON.stringify(base, null, 2);
  for (const dir of ["public/data", "dist/public/data"]) {
    try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/snapshot.json`, json); } catch (e: any) { console.warn(`[pipeline] ⚠ snapshot.json 寫入 ${dir} 失敗（靜態鏡像將陳舊）:`, e?.message ?? e); }
  }
  console.log(`[pipeline] 手動錄入觀點：${input.expertName}《${input.title.slice(0, 40)}》→ ${signals.length} 個信號，新建議 ${changes.length} 項`);
  return { ok: true, summary, signalCount: signals.length };
}

// 舊通道保留（同步等待整個結構化+合併）——新前端請用 submitManualView + manualViewJob 輪詢
export async function addManualView(input: {
  expertName: string; title: string; url?: string; date?: string; content: string;
}): Promise<{ ok: boolean; summary?: string; signalCount?: number; error?: string }> {
  return doAddManualView(input);
}

// ---- Phase 16：手動錄入 async job（修平台代理逾時）----
// Kimi 結構化（reasoning 模型實測 40-90 秒）超過平台代理逾時，同步等待會令前端收到
// 非 JSON 回應（Safari: "The string did not match the expected pattern."）。
// 改為：submit 即時回 jobId，背景跑 doAddManualView，前端輪詢 manualViewJob（同 runNow/status 模式）。
export interface ManualViewJobResult {
  ok: boolean; summary?: string; signalCount?: number; error?: string; dryRun?: boolean;
  // Phase 19：批量導入結果欄位（submitBatchImport 通道）
  imported?: number; failedList?: { url: string; error: string }[];
}
interface ManualViewJob { status: "running" | "done" | "failed"; startedAt: number; stage?: string; result?: ManualViewJobResult; error?: string }
const manualViewJobs = new Map<string, ManualViewJob>();
const MANUAL_VIEW_JOB_TTL = 30 * 60 * 1000; // 30 分鐘 lazy 過期

function sweepManualViewJobs(): void {
  const cutoff = Date.now() - MANUAL_VIEW_JOB_TTL;
  for (const [id, j] of manualViewJobs) if (j.startedAt < cutoff) manualViewJobs.delete(id);
}

// Phase 19：watchdog——background runner 理論上唔會 hang 死（全部調用有 timeout），但 DB 掛起等
// 逃逸路徑會令 job 永遠 running（前端無限輪詢）。到時仍 running → 強制 failed 俾用戶明確人話錯誤。
function armJobWatchdog(jobId: string, ms: number, label: string): () => void {
  const timer = setTimeout(() => {
    const j = manualViewJobs.get(jobId);
    if (j && j.status === "running") {
      j.status = "failed";
      j.error = `${label}超時（${Math.max(1, Math.round(ms / 60000))} 分鐘上限）——請重試；反覆出現請縮短字幕或稍後再試`;
      console.log(`[pipeline] ⚠ job ${jobId} watchdog 觸發：${j.error}`);
    }
  }, ms);
  (timer as any).unref?.();
  return () => clearTimeout(timer);
}

// 測試注入點（vitest）：覆蓋手動錄入 background runner，唔准用嚟繞過真實邏輯（只供 watchdog 單測）
let manualViewRunner: typeof doAddManualView = doAddManualView;
export function _setManualViewRunnerForTest(fn: typeof doAddManualView | null): void {
  manualViewRunner = fn ?? doAddManualView;
}

export function submitManualView(input: {
  expertName: string; title: string; url?: string; date?: string; content: string; dryRun?: boolean;
}): { ok: true; jobId: string } | { ok: false; error: string } {
  // 平嘢校驗同步做——唔啱即返 error，前端即時見到，唔使等輪詢
  if (!input.expertName?.trim()) return { ok: false, error: "請填寫專家名" };
  if (!input.title?.trim()) return { ok: false, error: "請填寫視頻/文章標題" };
  if ((input.content ?? "").trim().length < 100) return { ok: false, error: "內容少於 100 字——請貼上完整字幕或正文（字幕級證據是觀點入庫門檻，防止道聽途說混入）" };
  sweepManualViewJobs();
  const jobId = crypto.randomUUID();
  manualViewJobs.set(jobId, { status: "running", startedAt: Date.now(), stage: "排隊中" });
  const WATCHDOG_MS = Number(process.env.MANUAL_VIEW_JOB_TIMEOUT_MS) || 6 * 60 * 1000;
  const disarm = armJobWatchdog(jobId, WATCHDOG_MS, "結構化");
  const setStage = (s: string) => { const j = manualViewJobs.get(jobId); if (j && j.status === "running") j.stage = s; };
  void (async () => {
    const job = manualViewJobs.get(jobId);
    try {
      const result = await manualViewRunner(input, setStage);
      if (!job) return;
      job.result = result;
      if (result.ok) job.status = "done";
      else { job.status = "failed"; job.error = result.error ?? "錄入失敗"; }
    } catch (e: any) {
      if (!job) return;
      job.status = "failed";
      job.error = e?.message ?? String(e);
    } finally {
      disarm();
    }
  })();
  return { ok: true, jobId };
}

export function getManualViewJob(jobId: string): {
  status: "running" | "done" | "failed" | "unknown"; stage?: string; result?: ManualViewJobResult; error?: string;
} {
  sweepManualViewJobs();
  const j = manualViewJobs.get(jobId);
  if (!j) return { status: "unknown" };
  return {
    status: j.status,
    ...(j.stage !== undefined ? { stage: j.stage } : {}),
    ...(j.result !== undefined ? { result: j.result } : {}),
    ...(j.error !== undefined ? { error: j.error } : {}),
  };
}

// ---- 批量貼鏈接導入：N 個 YouTube URL → kome 抓字幕 → Kimi 結構化 → 單次快照合併 ----
// 與逐條錄入的差別：只寫一次快照、只跑一次建議引擎（避免 N 次重複計算與 N 條 DB 記錄）
export async function batchImportVideos(urls: string[], expertName?: string, onStage?: (s: string) => void): Promise<{
  ok: boolean; imported: number; failed: { url: string; error: string }[]; signalCount: number; error?: string;
}> {
  // Phase 13 P1-6：同批 URL 去重（按解析出嘅 videoId，唔同形態同一條片只抓一次）
  const seenIds = new Set<string>();
  const list = urls.map(u => u.trim()).filter(Boolean)
    .filter(u => { const id = parseVideoId(u) ?? u; if (seenIds.has(id)) return false; seenIds.add(id); return true; })
    .slice(0, 10);
  if (!list.length) return { ok: false, imported: 0, failed: [], signalCount: 0, error: "沒有有效鏈接" };
  if (!KIMI_KEY) return { ok: false, imported: 0, failed: [], signalCount: 0, error: "未配置 KIMI_API_KEY" };
  const now = new Date();
  const today = now.toISOString().slice(0, 10);
  const db = getDb();
  const rows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
  let base: Snapshot;
  try { base = rows[0] ? JSON.parse(rows[0].payload) as Snapshot : null as unknown as Snapshot; } catch { base = null as unknown as Snapshot; }
  if (!base || !Array.isArray(base.views)) {
    base = { date: today, generatedAt: now.toISOString(), views: [], suggested: [], suggestedNote: "", lastRebalanceDate: effectiveLastRebalanceDate(), brakeStatus: "ok" };
  }
  // 去重：已入庫的 videoId 不重複抓取（逐條喺下方用 base.views 檢查）
  const failed: { url: string; error: string }[] = [];
  const newViews: SnapshotView[] = [];
  let doneCount = 0; // Phase 19：進度回報（pool 並發下 x 係「已完成」計數，唔係處理中次序）
  await pool(2, list.map(url => async () => {
    const myIdx = ++doneCount; // 開始處理次序（近似進度）
    onStage?.(`抓取第 ${myIdx}/${list.length} 條字幕`);
    const t = await fetchVideoTranscript(url);
    if (!t.ok || !t.text) { failed.push({ url, error: t.error ?? "抓字幕失敗" }); return; }
    const pageUrl = `https://www.youtube.com/watch?v=${t.videoId}`;
    if (base.views.some(v => v.url.includes(t.videoId!))) { failed.push({ url, error: "該視頻已在觀點庫中（跳過）" }); return; } // Phase 13 P1-6：刪除死代碼（seen key 係 url|title，`${pageUrl}|${pageUrl}` 永遠唔會命中）
    try {
      onStage?.(`結構化第 ${myIdx}/${list.length} 條`);
      const out = await structureWithKimi(expertName?.trim() || "YouTube 頻道", `YouTube 視頻 ${t.videoId}`, t.text.slice(0, 9000), today, "視頻字幕全文（批量導入）");
      newViews.push({
        expertId: "manual", expertName: expertName?.trim() || "YouTube 頻道", date: today,
        channel: "批量導入 · 字幕級證據",
        title: `YouTube 視頻 ${t.videoId}`, summary: out.summary, url: pageUrl,
        videoId: t.videoId, signals: out.signals, horizon: out.horizon, decayWeight: decay(today, now, out.horizon),
      });
    } catch (e: any) { failed.push({ url, error: `結構化失敗：${e.message}` }); }
  }));
  if (newViews.length) {
    onStage?.("合併快照＋重算建議");
    base.views = [...newViews, ...base.views].slice(0, 60);
    const { changes, note, watchlist } = await buildSuggestions(base.views);
    base.suggested = changes; base.suggestedNote = note; base.watchlist = watchlist;
    base.generatedAt = now.toISOString();
    if (changes.length > 0) { base.acknowledged = false; base.acknowledgedAt = undefined; }
    else if (base.acknowledged == null) base.acknowledged = true; // Phase 13 P1-6：補 acknowledged==null 分支（同 addManualView/addStructuredView 一致）
    await db.insert(snapshots).values({ kind: "manual", payload: JSON.stringify(base) });
    const json = JSON.stringify(base, null, 2);
    for (const dir of ["public/data", "dist/public/data"]) {
      try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/snapshot.json`, json); } catch (e: any) { console.warn(`[pipeline] ⚠ snapshot.json 寫入 ${dir} 失敗（靜態鏡像將陳舊）:`, e?.message ?? e); }
    }
  }
  const signalCount = newViews.reduce((s, v) => s + v.signals.length, 0);
  console.log(`[pipeline] 批量導入：${newViews.length}/${list.length} 成功，${signalCount} 個信號`);
  return { ok: true, imported: newViews.length, failed, signalCount };
}

// ---- Phase 19：批量導入 async job 化（修同步逾時）----
// 舊 batchImportVideos endpoint 係同步 mutation——N 條片動輒幾分鐘，必然超過平台代理逾時
//（Safari 拋非 JSON 錯誤）。呢度同 submitManualView 同一模式：同步校驗 → 即回 jobId →
// 背景跑 batchImportVideos（stage 進度回報）→ 前端輪詢 manualViewJob。watchdog 10 分鐘（批量較耐）。
// 舊同步 endpoint 保留唔刪（API 兼容），前端改用新 job 通道。
export function submitBatchImport(urls: string[], expertName?: string): { ok: true; jobId: string } | { ok: false; error: string } {
  const valid = (urls ?? []).map(u => u.trim()).filter(u => parseVideoId(u) !== null).slice(0, 10);
  if (!valid.length) return { ok: false, error: "沒有有效 YouTube 鏈接——每行一條 watch?v= / youtu.be / shorts 鏈接" };
  if (!KIMI_KEY) return { ok: false, error: "未配置 KIMI_API_KEY" };
  sweepManualViewJobs();
  const jobId = crypto.randomUUID();
  manualViewJobs.set(jobId, { status: "running", startedAt: Date.now(), stage: `排隊中（${valid.length} 條）` });
  const WATCHDOG_MS = Number(process.env.BATCH_IMPORT_JOB_TIMEOUT_MS) || 10 * 60 * 1000;
  const disarm = armJobWatchdog(jobId, WATCHDOG_MS, "批量導入");
  const setStage = (s: string) => { const j = manualViewJobs.get(jobId); if (j && j.status === "running") j.stage = s; };
  void (async () => {
    const job = manualViewJobs.get(jobId);
    try {
      const r = await batchImportVideos(valid, expertName, setStage);
      if (!job) return;
      const result: ManualViewJobResult = { ok: r.ok, imported: r.imported, failedList: r.failed, signalCount: r.signalCount, ...(r.error ? { error: r.error } : {}) };
      job.result = result;
      if (r.ok) job.status = "done";
      else { job.status = "failed"; job.error = r.error ?? "批量導入失敗"; }
    } catch (e: any) {
      if (!job) return;
      job.status = "failed";
      job.error = e?.message ?? String(e);
    } finally {
      disarm();
    }
  })();
  return { ok: true, jobId };
}

// ---- Agent 結構化錄入：Kimi 不可用時的備用通道 ----
// 字幕已由 Agent（瀏覽器+kome）取得並由 Agent 親自通讀全文提取信號，此端點只做校驗與合併，
// 不再調用 LLM。與手動錄入同一規格：信號必須可映射、來源必須是字幕級證據（URL 必填）。
export async function addStructuredView(input: {
  expertName: string; title: string; url: string; date: string;
  summary: string; horizon?: string;
  signals: { asset: string; direction: "bull" | "bear" | "neutral"; strength: number; note?: string }[];
}): Promise<{ ok: boolean; signalCount?: number; mappedCount?: number; error?: string }> {
  if (!input.expertName?.trim()) return { ok: false, error: "請填寫專家名" };
  if (!input.title?.trim()) return { ok: false, error: "請填寫標題" };
  if (!/^https?:\/\//.test(input.url ?? "")) return { ok: false, error: "必須提供來源 URL（寧缺毋濫：無鏈接不入庫）" };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.date ?? "")) return { ok: false, error: "日期格式須為 YYYY-MM-DD" };
  if (!Array.isArray(input.signals) || !input.signals.length) return { ok: false, error: "至少需要 1 個信號" };
  if (input.signals.length > 12) return { ok: false, error: "單條觀點最多 12 個信號" };
  const summary = (input.summary ?? "").trim();
  if (summary.length < 30) return { ok: false, error: "摘要少於 30 字——請提供實質內容摘要" };

  const now = new Date();
  const horizon = normalizeHorizon(input.horizon); // Phase 13 P1-4：horizon 白名單統一走守衛函數
  const date = clampFutureDate(input.date, now.getTime()); // Phase 13 P1-4：未來日期夾返今日（警告內置）
  // 校驗並規整信號：方向/強度白名單，asset 必須能映射到持倉工具（否則剔除並計數）
  const signals: SnapshotSignal[] = [];
  let dropped = 0;
  for (const s of input.signals) {
    const dir = s.direction;
    if (!["bull", "bear", "neutral"].includes(dir)) { dropped++; continue; }
    const strength = Math.max(1, Math.min(5, Math.round(Number(s.strength) || 0)));
    const asset = (s.asset ?? "").trim();
    if (!asset || !mapAsset(asset).length) { dropped++; continue; }
    signals.push({ asset, direction: dir, strength, note: (s.note ?? "").slice(0, 300) });
  }
  if (!signals.length) return { ok: false, error: `所有信號均無法映射到持倉工具（剔除 ${dropped} 個）——請檢查 asset 命名` };

  const view: SnapshotView = {
    expertId: "manual", expertName: input.expertName.trim(), date,
    channel: "Agent 結構化 · 字幕級證據",
    title: input.title.trim().slice(0, 200), summary: summary.slice(0, 600),
    url: input.url.trim(), signals, horizon, decayWeight: decay(date, now, horizon),
  };
  const m = input.url.match(/[?&]v=([\w-]{11})/); if (m) view.videoId = m[1];

  // 與 addManualView/batchImportVideos 相同的合併路徑：載入最新快照 → 去重 → 前插 → 重跑建議 → 寫 DB+文件
  const db = getDb();
  const rows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(1);
  let base: Snapshot;
  try { base = rows[0] ? JSON.parse(rows[0].payload) as Snapshot : null as unknown as Snapshot; } catch { base = null as unknown as Snapshot; }
  if (!base || !Array.isArray(base.views)) {
    base = { date: now.toISOString().slice(0, 10), generatedAt: now.toISOString(), views: [], suggested: [], suggestedNote: "", lastRebalanceDate: effectiveLastRebalanceDate(), brakeStatus: "ok" };
  }
  if (base.views.some(v => v.url === view.url || (view.videoId && v.url.includes(view.videoId)))) {
    return { ok: false, error: "該來源已在觀點庫中（跳過）" };
  }
  base.views = [view, ...base.views].slice(0, 60);
  const { changes, note, watchlist } = await buildSuggestions(base.views);
  base.suggested = changes; base.suggestedNote = note; base.watchlist = watchlist;
  base.generatedAt = now.toISOString();
  if (changes.length > 0) { base.acknowledged = false; base.acknowledgedAt = undefined; }
  else if (base.acknowledged == null) base.acknowledged = true;
  await db.insert(snapshots).values({ kind: "manual", payload: JSON.stringify(base) });
  const json = JSON.stringify(base, null, 2);
  for (const dir of ["public/data", "dist/public/data"]) {
    try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/snapshot.json`, json); } catch (e: any) { console.warn(`[pipeline] ⚠ snapshot.json 寫入 ${dir} 失敗（靜態鏡像將陳舊）:`, e?.message ?? e); }
  }
  console.log(`[pipeline] Agent結構化錄入：${input.expertName}《${input.title.slice(0, 40)}》→ ${signals.length} 個信號（剔除 ${dropped}），新建議 ${changes.length} 項`);
  return { ok: true, signalCount: signals.length, mappedCount: signals.length };
}

// Phase 19b：addStructuredView async job 化——同步版喺受限網絡下，buildSuggestions 嘅風控剎車
// 要逐隻持倉抓行情（直連 Yahoo 被牆 → 逐隻等 timeout 先落 agent-gw 兜底，串行十幾隻隨時 2-3 分鐘），
// 實測生產同步調用 504 Gateway Timeout（邊緣殺連接，寫入唔會完成）。同 submitManualView 同一模式：
// 同步校驗 → 即回 jobId → 背景跑 → 前端/調用方輪詢 manualViewJob（任務Map共用，watchdog 共用）。
export function submitStructuredView(input: {
  expertName: string; title: string; url: string; date: string;
  summary: string; horizon?: string;
  signals: { asset: string; direction: "bull" | "bear" | "neutral"; strength: number; note?: string }[];
}): { ok: true; jobId: string } | { ok: false; error: string } {
  // 平嘢校驗同步做（同 addStructuredView 開段一致）——唔啱即返 error，調用方即時見到
  if (!input.expertName?.trim()) return { ok: false, error: "請填寫專家名" };
  if (!input.title?.trim()) return { ok: false, error: "請填寫標題" };
  if (!/^https?:\/\//.test(input.url ?? "")) return { ok: false, error: "必須提供來源 URL（寧缺毋濫：無鏈接不入庫）" };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.date ?? "")) return { ok: false, error: "日期格式須為 YYYY-MM-DD" };
  if (!Array.isArray(input.signals) || !input.signals.length) return { ok: false, error: "至少需要 1 個信號" };
  if (input.signals.length > 12) return { ok: false, error: "單條觀點最多 12 個信號" };
  if ((input.summary ?? "").trim().length < 30) return { ok: false, error: "摘要少於 30 字——請提供實質內容摘要" };
  sweepManualViewJobs();
  const jobId = crypto.randomUUID();
  manualViewJobs.set(jobId, { status: "running", startedAt: Date.now(), stage: "排隊中" });
  const WATCHDOG_MS = Number(process.env.MANUAL_VIEW_JOB_TIMEOUT_MS) || 6 * 60 * 1000;
  const disarm = armJobWatchdog(jobId, WATCHDOG_MS, "結構化錄入");
  const setStage = (s: string) => { const j = manualViewJobs.get(jobId); if (j && j.status === "running") j.stage = s; };
  void (async () => {
    const job = manualViewJobs.get(jobId);
    try {
      setStage("合併快照 + 重算建議（風控行情抓取需時，請耐心等候）");
      const result = await addStructuredView(input);
      if (!job) return;
      job.result = result;
      if (result.ok) job.status = "done";
      else { job.status = "failed"; job.error = result.error ?? "錄入失敗"; }
    } catch (e: any) {
      if (!job) return;
      job.status = "failed";
      job.error = e?.message ?? String(e);
    } finally {
      disarm();
    }
  })();
  return { ok: true, jobId };
}

// ---- 信號命中率回測：多窗口階梯 × ACWI 超額命中（2026-09-11 Phase 12 升級）----
// 這是「專家命中率」的真實數據源（取代靜態手填數字）。
// 口徑全部喺 contracts/backtest.ts（純函數、可單測）：5/15/45/90 交易日四窗階梯；
// 命中以超額判定（ETF 窗口收益 − ACWI 同窗收益：bull >+0.5pp / bear <−0.5pp / neutral |excess|≤2pp），
// 剔除大市順風車——上升市齋睇多唔再自動命中；未到期窗口 cell=null，誠實留空。
// 舊版單一 15 日窗 + 絕對方向（bull>+1%）嘅缺陷見 HANDOVER Phase 12 附錄。
let backtestCache: { at: number; data: SignalBacktestResult } | null = null;
export interface SignalBacktestRow {
  expert: string; date: string; asset: string; ticker: string; direction: string;
  cells: BtCells; // 每窗口 {retPct, excessPct, hit} 或 null（未到期）
}
export interface SignalBacktestResult {
  asOf: string; windows: readonly number[];
  rows: SignalBacktestRow[];
  byWindow: BtWindowAgg[];
  byExpert: ReturnType<typeof aggregateExpert>; // 按專家（主窗 15 交易日）
  acwiMissing?: boolean; // Phase 13 P0-2：ACWI 基準序列缺失時明確 flag（前端要顯示警告），唔好靜靜雞 skip
}
// Phase 13 P1-9：複合頻道名（如「洪灝/林本利等(etnet专访)」）按標題內實際受訪者歸因——
// 逐段候選同標題做 exact/includes 匹配，全部唔中先 fallback 用第一段（唔再永遠成個複合名落一格）
function attributeExpert(view: SnapshotView): string {
  const n = view.expertName;
  if (!/[/、,，]/.test(n)) return n;
  // 先剝括號註釋同結尾「等」字（「林本利等(etnet专访)」→「林本利」），否則複合名第二段永遠被過濾
  const parts = n.split(/[/、,，]/).map(s => s.replace(/[（(].*$/, "").replace(/等$/, "").trim()).filter(s => s.length >= 2);
  const hit = matchExpertName(view.title, parts);
  return hit ?? parts[0] ?? n;
}
export async function signalBacktest(): Promise<SignalBacktestResult> {
  if (backtestCache && Date.now() - backtestCache.at < 6 * 3600_000) return backtestCache.data;
  // Phase 13 P0-2：舊版淨係讀最新快照（views ≤60 日 × carry TTL 殺晒）→ 45/90 交易日窗結構性永遠 0 decided。
  // snapshots 表本身係 append-only 歷史（每次管道/錄入都 insert 一行），直接掃近 120 份快照，
  // 按 url|title|asset|direction 去重聚合（新快照優先），唔需要新表。
  // Phase 14：觀點 key 改用 dedupeKey（專家|標題|日期）——raw url 帶隨機參數會令跨快照重複聚合失效
  const BT_SNAPSHOT_SCAN = 120; // 120 份日快照 ≈ 4 個月，足以覆蓋 90 交易日（≈180 曆日）窗口
  const rows: SignalBacktestRow[] = [];
  const all: { expert: string; direction: string; cells: BtCells }[] = [];
  const db = getDb();
  // Phase 17：kind 過濾——performance/rebalance_audit 行會霸佔 120 行掃描窗口
  const snapRows = await db.select().from(snapshots).where(snapshotKindFilter()).orderBy(desc(snapshots.id)).limit(BT_SNAPSHOT_SCAN);
  const viewsByKey = new Map<string, SnapshotView>();
  for (const r of snapRows) { // snapRows 新→舊：首次出現即最新版本
    let s: Snapshot;
    try { s = JSON.parse(r.payload) as Snapshot; } catch { continue; }
    for (const v of s.views ?? []) {
      const key = dedupeKey(v);
      if (!viewsByKey.has(key)) viewsByKey.set(key, v);
    }
  }
  const views = [...viewsByKey.values()];
  let acwiMissing = false;
  if (views.length) {
    // 收集涉及的 ticker（+ ACWI 基準），每隻只拉一次行情
    const need = new Set<string>(["ACWI"]);
    const jobs: { view: SnapshotView; sig: SnapshotSignal; ticker: string }[] = [];
    const sigSeen = new Set<string>(); // Phase 13 P0-2：信號級去重；Phase 14：key 改用 dedupeKey（理由同上）
    for (const v of views) {
      for (const sig of v.signals ?? []) {
        const skey = `${dedupeKey(v)}|${sig.asset}|${sig.direction}`;
        if (sigSeen.has(skey)) continue;
        sigSeen.add(skey);
        // Phase 13 P0-2：每個映射 ticker 獨立一個 job（同 suggestions/algo 全 ticker 口徑對齊，
        // 舊版 mapAsset(...)[0] 淨測第一個 ticker，金银铜→GLD 一對多信號嘅 SLV/COPX 永遠唔入回測）
        for (const t of mapAsset(sig.asset)) { need.add(t); jobs.push({ view: v, sig, ticker: t }); }
      }
    }
    const closesBy: Record<string, { date: string; close: number }[]> = {};
    await pool(3, [...need].map(t => async () => {
      try { const c = await fetchCloses(t, "6mo"); if (c?.length) closesBy[t] = c; } catch {}
    }));
    const acwi = closesBy["ACWI"] ?? [];
    acwiMissing = acwi.length === 0;
    if (acwiMissing) console.log("[pipeline] ⚠ signalBacktest: ACWI 基準序列缺失——超額命中無法計算，回傳空表 + acwiMissing flag");
    for (const { view, sig, ticker } of jobs) {
      const closes = closesBy[ticker];
      if (!closes || !acwi.length) continue;
      if (closes.findIndex(x => x.date >= view.date) < 0) continue; // 發布日晚過最新收盤：唔入表（同舊版口徑）
      const cells = evalWindows(closes, acwi, view.date, sig.direction);
      const expert = attributeExpert(view); // Phase 13 P1-9
      rows.push({
        expert, date: view.date, asset: sig.asset, ticker,
        direction: sig.direction, cells,
      });
      all.push({ expert, direction: sig.direction, cells });
    }
  }
  rows.sort((a, b) => b.date.localeCompare(a.date));
  const data: SignalBacktestResult = {
    asOf: new Date().toISOString().slice(0, 10),
    windows: BT_WINDOWS,
    rows: rows.slice(0, 50),
    byWindow: BT_WINDOWS.map(w => aggregateWindow(all, w)),
    byExpert: aggregateExpert(all),
    ...(acwiMissing ? { acwiMissing: true } : {}),
  };
  backtestCache = { at: Date.now(), data };
  return data;
}

// ---- 字幕截圖 OCR（Moonshot vision，受限網絡可達）----
// 手機上 YouTube「文字記錄」無法複製——用戶截圖上傳，vision 模型轉錄成文字，
// 回填到手動錄入文本框（用戶確認後走 addManualView 入庫，證據等級不變）。
export async function ocrTranscript(images: string[]): Promise<{ ok: boolean; text?: string; chars?: number; error?: string }> {
  if (!KIMI_KEY) return { ok: false, error: "未配置 KIMI_API_KEY" };
  if (!images.length) return { ok: false, error: "沒有收到圖片" };
  // Phase 13 P0-1：moonshot-v1-32k-vision-preview 已退役 → 改用 kimi-k3（原生視覺）。
  // fallback 鏈只有 [kimi-k3]——得佢支援視覺；失敗要響亮記錄，唔准呃係「圖片冇字」
  const OCR_MODELS = ["kimi-k3"];
  const PROMPT = "這是 YouTube「文字記錄」面板的截圖。請完整轉錄圖中所有字幕文字（忽略時間戳、進度條、按鈕、搜尋框等界面元素），保持原文語言與用字，不要翻譯、不要總結、不要添加任何評論或說明。只輸出轉錄的文字。";
  const per = async (dataUrl: string): Promise<string> => {
    let lastErr = "vision 調用失敗";
    for (const model of OCR_MODELS) {
      try {
        const r = await tfetch(`${KIMI_BASE}/chat/completions`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${KIMI_KEY}` },
          body: JSON.stringify({
            model, // Phase 13.2：唔准設 temperature——kimi-k3 只接受 1（默認），設 0 會 400
            messages: [{ role: "user", content: [
              { type: "image_url", image_url: { url: dataUrl } },
              { type: "text", text: PROMPT },
            ] }],
          }),
        }, 90000);
        if (!r.ok) { lastErr = `OCR vision API HTTP ${r.status} (${model})`; continue; }
        const j: any = await r.json();
        return String(j.choices?.[0]?.message?.content ?? "").trim();
      } catch (e: any) { lastErr = `OCR vision 網絡錯誤 (${model}): ${e.message}`; }
    }
    throw new Error(lastErr);
  };
  // Phase 13 P1-5：逐張記錄失敗原因，唔准靜默吞錯
  let failCount = 0, lastFail = "";
  const parts = await pool(2, images.slice(0, 8).map(u => async () => {
    if (!/^data:image\//.test(u)) { failCount++; lastFail = "唔係 data:image/ 格式"; return ""; }
    try { return await per(u); }
    catch (e: any) { failCount++; lastFail = e.message; console.log(`[pipeline] ⚠ OCR 圖片轉錄失敗: ${e.message}`); return ""; }
  }));
  const ok = parts.filter(p => p.length > 0);
  const text = ok.join("\n");
  if (text.length < 20) {
    // Phase 13 P1-5：訊息誠實化——區分「vision 調用失敗」同「識別結果過短」，唔好誤導用戶以為係圖片冇字
    if (failCount > 0 && ok.length === 0) {
      console.log(`[pipeline] ⚠ OCR 全部 ${failCount} 張圖片 vision 調用失敗（${lastFail}）`);
      return { ok: false, error: `OCR vision 模型調用失敗（${lastFail}）——唔係圖片冇字，係模型請求本身失敗，請稍後再試或檢查 KIMI_API_KEY` };
    }
    return { ok: false, error: "識別結果過短——請確認截圖是「文字記錄」面板、畫面清晰，再試一次" };
  }
  return { ok: true, text, chars: text.length };
}

// ---- 網絡能力自檢：用戶（在任何部署環境）可一鍵確認當前環境能走通哪些渠道 ----
// Phase 19：kome 探針誠實化——HEAD 首頁會喺「API 已死但首頁仲開」時打假綠。
// 改為真實 POST /api/transcript：只有 HTTP 200 + JSON content-type + parse 到 transcript 欄位先算可用。
async function probeKome(): Promise<{ ok: boolean; detail: string }> {
  let r: Response;
  try {
    r = await tfetch("https://kome.ai/api/transcript", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id: "dQw4w9WgXcQ" }),
    }, 8000);
  } catch { return { ok: false, detail: "不可達" }; }
  if (r.status === 429) return { ok: false, detail: "已失效：HTTP 429 付費牆" };
  const raw = await r.text().catch(() => "");
  if (/Vercel Security Checkpoint/i.test(raw) || /^\s*</.test(raw)) return { ok: false, detail: "已被安全閘道封鎖" };
  if (!r.ok) return { ok: false, detail: `已失效：HTTP ${r.status}` };
  const ct = r.headers.get("content-type") ?? "";
  if (!/json/i.test(ct)) return { ok: false, detail: "已被安全閘道封鎖" };
  try {
    const j = JSON.parse(raw);
    if (typeof j?.transcript === "string") return { ok: true, detail: "可用" };
    return { ok: false, detail: "回應異常（無 transcript 欄位）" };
  } catch { return { ok: false, detail: "已被安全閘道封鎖" }; }
}

export async function netCheck(): Promise<{
  googleapis: boolean; youtube: boolean; brave: boolean; moonshot: boolean; moonshotDetail: string; agentGw: boolean; kome: boolean; komeDetail: string; supadata: boolean; supadataDetail: string; checkedAt: string;
}> {
  const [googleapis, youtube, brave, agentGw, komeProbe] = await Promise.all([
    probeHost("https://www.googleapis.com/"),
    probeHost("https://www.youtube.com/"),
    probeHost("https://api.search.brave.com/"),
    probeHost("https://agent-gw.kimi.com/"),
    probeKome(),
  ]);
  const kome = komeProbe.ok, komeDetail = komeProbe.detail;
  // Kimi 檢查必須係真實最小 chat 調用——純 TCP 探測會喺「帳戶欠費暫停」時誤報 ✓
  let moonshot = false, moonshotDetail = "未配置 KIMI_API_KEY";
  if (KIMI_KEY) {
    // Phase 13 P0-1：probe model 由寫死 kimi-k2.5（已退役）改用共享 resolver——成功即代表帳戶+網絡+模型鏈全部可用
    const probeModel = await resolveKimiModel();
    if (!probeModel) {
      moonshotDetail = "所有候選模型均不可用（KIMI_MODEL/kimi-k2.6/kimi-k3 調用失敗）——檢查 Key 餘額或網絡";
    } else try {
      // Phase 13.1 修復：探針 URL 唔准寫死 .cn——國際站（.ai）開嘅 key 喺 .cn 會 401；統一用 KIMI_BASE
      const r = await tfetch(`${KIMI_BASE}/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${KIMI_KEY}` },
        body: JSON.stringify({ model: probeModel, messages: [{ role: "user", content: "ping" }], max_tokens: 1 }),
      }, 12000);
      if (r.ok) {
        // Phase 19 第二級：細 ping 通過唔代表長請求過到——kimi.pro 發布站出口代理會 TCP reset
        // 「長時間無 bytes 流動」嘅連接。做「真實負載探針」：約 3000 字 prompt + streaming，
        // HTTP 200 + 有 SSE chunks 流動即算過（k2.6/k3 reasoning 會食 max_tokens，唔強求 content 非空）。
        const probePrompt = `請以 JSON 輸出一句市場短評：{"note":"..."}。以下係填充文本：${"環球市場波動，投資者宜分散配置。".repeat(170)}`;
        try {
          const r2 = await tfetch(`${KIMI_BASE}/chat/completions`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${KIMI_KEY}` },
            body: JSON.stringify({
              model: probeModel,
              messages: [{ role: "user", content: probePrompt }],
              max_tokens: 800, // 要包埋 reasoning 消耗（實測 max_tokens 太細會全部耗喺 reasoning，content 為空）
              stream: true, // streaming 保持 bytes 流動——本身就係抗 reset 姿態
              response_format: { type: "json_object" },
            }),
          }, 60000);
          if (!r2.ok) throw new Error(`HTTP ${r2.status}`);
          const body = await r2.text(); // 讀晒成個 stream；有 data: chunks 即證明長連接冇被截
          if (!/data:/.test(body)) throw new Error("stream 無任何 chunk");
          moonshot = true; moonshotDetail = `可用（${probeModel}，長請求探針通過）`;
        } catch (e: any) {
          const msg = String(e?.message ?? e?.name ?? "unknown").slice(0, 60);
          moonshot = false;
          moonshotDetail = isNetworkError(e)
            ? "API 可達，但結構化級長請求被部署出口截斷（fetch failed）——錄入功能間歇失敗，重試或改用較短字幕"
            : `API 可達，但結構化級長請求失敗（${msg}）——錄入功能可能間歇失敗`;
        }
      } else {
        const t = (await r.text().catch(() => "")).slice(0, 300);
        if (/suspended|insufficient balance/i.test(t)) moonshotDetail = "帳戶已暫停：餘額不足，請充值或更換 Key";
        else if (r.status === 401) moonshotDetail = "Key 無效（401）";
        else if (r.status === 429) moonshotDetail = /suspended|insufficient/i.test(t) ? "帳戶已暫停：餘額不足，請充值或更換 Key" : "觸發限流（429）";
        else moonshotDetail = `HTTP ${r.status}`;
      }
    } catch (e: any) { moonshotDetail = `網絡不可達：${e.message?.slice(0, 80) ?? "timeout"}`; }
  }
  const supadataDetail = process.env.SUPADATA_API_KEY ? "已配置（伺服器字幕主力）" : "未配置 SUPADATA_API_KEY";
  return { googleapis, youtube, brave, moonshot, moonshotDetail, agentGw, kome, komeDetail, supadata: !!process.env.SUPADATA_API_KEY, supadataDetail, checkedAt: new Date().toISOString() };
}
