import { mysqlTable, serial, varchar, mediumtext, text, timestamp } from "drizzle-orm/mysql-core";

// 每日快照：观点库 + 共识 + 建议权重 + 价格表现（JSON 整体存储，前端直接消费）
export const snapshots = mysqlTable("snapshots", {
  id: serial("id").primaryKey(),
  kind: varchar("kind", { length: 32 }).notNull(), // 'daily' / 'manual' / 'rebalance'（觀點快照）；'rebalance_audit'（調倉審計）；'performance'（淨值鏡像）
  // Phase 17：TEXT（65,535 bytes）唔够——快照 60 views 約 70KB 會超限；
  // 改 MEDIUMTEXT（16MB）。已有 DB 由 boot 時 idempotent ALTER 遷移（api/pipeline.ts ensurePayloadMediumtext）
  payload: mediumtext("payload").notNull(),        // JSON string (见 contracts/types.ts Snapshot)
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

// 管道运行日志
export const pipelineRuns = mysqlTable("pipeline_runs", {
  id: serial("id").primaryKey(),
  status: varchar("status", { length: 16 }).notNull(), // running / success / failed
  log: text("log"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  finishedAt: timestamp("finished_at"),
});
