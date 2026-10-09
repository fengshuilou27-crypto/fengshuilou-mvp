// Phase 14 一次性清理腳本：修復「Wind URL 隨機 useless 參數令 url|title 去重失效」遺留嘅重複觀點
// 做法（唔 drop 表、唔改歷史 row）：
//   1. 讀 DB 最新快照 → 用 dedupeKey（專家|標題|日期）去重 views（保留先出現者）
//   2. 用去重後嘅 views 重跑 buildSuggestions（純函數，無 LLM 調用）
//   3. append 一條新快照 row（kind: "dedupe"，保持 snapshots 表 append-only 設計）
//   4. 重寫 public/data + dist/public/data 兩份鏡像
// 運行：npx tsx scripts/dedupe-snapshot.ts
import "dotenv/config";
import { mkdirSync, writeFileSync } from "node:fs";
import { desc, inArray } from "drizzle-orm";
import { getDb } from "../api/queries/connection";
import { snapshots } from "../db/schema";
import { dedupeKey, buildSuggestions } from "../api/pipeline";
import type { Snapshot } from "../contracts/types";

async function main() {
  const db = getDb();
  // Phase 17：kind 過濾——performance/rebalance_audit 行唔係觀點快照，唔好誤讀
  const rows = await db.select().from(snapshots)
    .where(inArray(snapshots.kind, ["daily", "manual", "rebalance", "dedupe"]))
    .orderBy(desc(snapshots.id)).limit(1);
  if (!rows[0]) { console.log("冇快照，唔使清理"); process.exit(0); }
  const base = JSON.parse(rows[0].payload) as Snapshot;
  const before = base.views?.length ?? 0;

  const seen = new Set<string>();
  const kept = (base.views ?? []).filter(v => {
    const k = dedupeKey(v);
    if (seen.has(k)) {
      console.log(`  剔除重複：${v.expertName}《${(v.title ?? "").slice(0, 40)}》(${v.date})`);
      return false;
    }
    seen.add(k);
    return true;
  });
  const removed = before - kept.length;
  if (removed === 0) { console.log(`最新快照 ${before} 條觀點冇重複，唔使清理`); process.exit(0); }

  const now = new Date();
  const { changes, note } = await buildSuggestions(kept);
  const cleaned: Snapshot = {
    ...base,
    views: kept,
    suggested: changes,
    suggestedNote: note,
    generatedAt: now.toISOString(),
    // 同 addManualView 口徑：有新建议 → 重置复核状态待人工复核；冇 → true
    acknowledged: changes.length > 0 ? false : true,
    acknowledgedAt: changes.length > 0 ? undefined : now.toISOString(),
  };
  await db.insert(snapshots).values({ kind: "dedupe", payload: JSON.stringify(cleaned) });
  const json = JSON.stringify(cleaned, null, 2);
  for (const dir of ["public/data", "dist/public/data"]) {
    try { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/snapshot.json`, json); console.log(`  已寫 ${dir}/snapshot.json`); }
    catch (e: any) { console.warn(`  ⚠ 寫 ${dir} 失敗:`, e?.message ?? e); }
  }
  console.log(`完成：${before} → ${kept.length} 條觀點（剔除 ${removed} 條重複）；建議重算：${changes.length} 項`);
  process.exit(0);
}

main().catch(e => { console.error("清理失敗:", e); process.exit(1); });
