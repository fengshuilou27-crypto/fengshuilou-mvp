// 一次性修復腳本（2026-10-09 v2）：以交接包快照做種子恢復信號生態
// 背景：DB 現行快照 60 條觀點全部無信號（8 月「空信號覆蓋」事故 + 9 月代理入庫寫咗落另一存儲）。
// 交接包 public/data/snapshot.json（54 條觀點、40 條帶信號、日期 2026-10-09）係最新策展真相。
// 做法：以檔案快照嘅觀點為基礎，用現行引擎重跑建議+瞭望 → append 一條新 daily 行（唔改舊行）。
import { readFileSync } from "node:fs";
import { getDb } from "../api/queries/connection";
import { snapshots } from "../db/schema";
import { buildSuggestions } from "../api/pipeline";
import type { Snapshot } from "../contracts/types";

async function main() {
  const file = JSON.parse(readFileSync("public/data/snapshot.json", "utf8")) as Snapshot;
  const withSig = (file.views ?? []).filter(v => v.signals?.length).length;
  console.log(`檔案快照 ${file.date}：${file.views.length} 條觀點、${withSig} 條帶信號`);
  if (!withSig) throw new Error("檔案快照都冇信號，中止");

  const { changes, note, watchlist } = await buildSuggestions(file.views ?? []);
  const snap: Snapshot = {
    ...file,
    generatedAt: new Date().toISOString(),
    suggested: changes,
    suggestedNote: `信號生態修復：以交接包策展快照做種子（${withSig} 條帶信號觀點），建議已按現行生效權重重算。${note}`,
    watchlist,
    acknowledged: false,
  };
  delete (snap as Record<string, unknown>).acknowledgedAt;
  delete (snap as Record<string, unknown>).acknowledged;

  const db = getDb();
  await db.insert(snapshots).values({ kind: "daily", payload: JSON.stringify(snap) });
  console.log("已寫入修復快照 | 建議:", changes.length, "| 瞭望主題:", watchlist.length);
  for (const w of watchlist) console.log("  -", w.theme, w.direction, "net", w.netScore, "|", w.proposal ? "有提案" : "觀望", "|", w.candidates.map(c => `${c.ticker}:${c.tier}`).join(" "));
}

main().then(() => process.exit(0)).catch(e => { console.error("修復失敗:", e); process.exit(1); });
