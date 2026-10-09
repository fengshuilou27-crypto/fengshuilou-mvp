import { z } from "zod";
import { createRouter, publicQuery } from "./middleware";
import { getStatus, latestSnapshot, latestPerformance, runPipeline, startScheduler, acknowledgeLatest, approveAndRecordLatest, addManualView, submitManualView, getManualViewJob, netCheck, ocrTranscript, fetchVideoTranscript, batchImportVideos, submitBatchImport, signalBacktest, addStructuredView, submitStructuredView, listRuntimeRebalances, recordRebalance } from "./pipeline";
import { getQuotes } from "./quotes";
import { getAlgoAnalysis } from "./algo";
import { getCorrelationReport } from "./correlation";
import { screenCandidateEtf } from "./screener";
import { getLearningReport } from "./learning";

export const appRouter = createRouter({
  ping: publicQuery.query(() => ({ ok: true, ts: Date.now() })),

  pipeline: createRouter({
    status: publicQuery.query(() => getStatus()),
    snapshot: publicQuery.query(() => latestSnapshot()),
    // 非阻塞：后台启动管道并立即返回，前端轮询 status 观察进度
    // （旧版 await 整个管道 → HTTP 请求挂住数分钟，页面看起来「没有反应」）
    runNow: publicQuery.mutation(() => {
      void runPipeline();
      return { started: true as const };
    }),
    acknowledge: publicQuery.mutation(() => acknowledgeLatest()),
    // Phase 18：批核即自動記錄調倉——按批核時所見建議權重生成調倉記錄（圖表黃點/生效權重/淨值分段即時聯動）。
    // 只係簿記，系統永遠唔會喺券商落單；建議唔零和時要附 fundFrom 指明資金來源/去向；
    // dryRun=true 只校驗+預覽零寫入（E2E 測試通道）。
    approveAndRecord: publicQuery
      .input(z.object({
        dryRun: z.boolean().optional(),
        fundFrom: z.object({ etf: z.string().min(1).max(12), to: z.number().min(0).max(40) }).optional(),
      }))
      .mutation(({ input }) => approveAndRecordLatest(input)),
    // 手動錄入專家觀點（YouTube 字幕複製粘貼，字幕級證據，走同一套結構化引擎）
    addManualView: publicQuery
      .input(z.object({
        expertName: z.string().min(1).max(50),
        title: z.string().min(1).max(200),
        url: z.string().max(500).optional(),
        date: z.string().max(10).optional(),
        content: z.string().min(100).max(20000),
      }))
      .mutation(({ input }) => addManualView(input)),
    // Phase 16：手動錄入 async job 化——Kimi 結構化實測 40-90s 超過平台代理逾時，
    // 同步等待會令前端收到非 JSON 回應。submit 即時回 jobId，前端輪詢 manualViewJob（同 runNow/status 模式）。
    // dryRun=true 行全部邏輯但唔寫入（E2E 測試通道）。
    submitManualView: publicQuery
      .input(z.object({
        expertName: z.string().min(1).max(50),
        title: z.string().min(1).max(200),
        url: z.string().max(500).optional(),
        date: z.string().max(10).optional(),
        content: z.string().min(100).max(20000),
        dryRun: z.boolean().optional(),
      }))
      .mutation(({ input }) => submitManualView(input)),
    manualViewJob: publicQuery
      .input(z.object({ jobId: z.string().min(8).max(64) }))
      .query(({ input }) => getManualViewJob(input.jobId)),
    // 網絡能力自檢：當前部署環境能走通哪些渠道
    netCheck: publicQuery.query(() => netCheck()),

    // 字幕截圖 OCR：上傳「文字記錄」截圖（dataURL 數組，≤8 張）→ vision 轉錄文字
    ocrTranscript: publicQuery
      .input(z.object({ images: z.array(z.string().max(2_500_000)).min(1).max(8) }))
      .mutation(({ input }) => ocrTranscript(input.images)),

    // 貼 YouTube 鏈接自動抓字幕（字幕代理通道，受限網絡可達）
    fetchVideoTranscript: publicQuery
      .input(z.object({ url: z.string().min(5).max(500) }))
      .mutation(({ input }) => fetchVideoTranscript(input.url)),

    // 批量貼鏈接導入：一次貼 N 個 YouTube URL（≤10），批量抓字幕+結構化，合併寫一次快照
    // （舊同步通道保留作 API 兼容——N 條片動輒幾分鐘會超平台代理逾時，前端請用 submitBatchImport）
    batchImportVideos: publicQuery
      .input(z.object({ urls: z.array(z.string().min(5).max(500)).min(1).max(10), expertName: z.string().max(60).optional() }))
      .mutation(({ input }) => batchImportVideos(input.urls, input.expertName)),
    // Phase 19：批量導入 async job 化——同步校驗即回 jobId，背景跑（stage 進度 + 10 分鐘 watchdog），
    // 前端輪詢 manualViewJob（同 submitManualView 模式），修同步逾時 Safari 非 JSON 錯誤。
    submitBatchImport: publicQuery
      .input(z.object({ urls: z.array(z.string().min(5).max(500)).min(1).max(10), expertName: z.string().max(60).optional() }))
      .mutation(({ input }) => submitBatchImport(input.urls, input.expertName)),

    // Agent 結構化錄入：字幕由 Agent 通讀全文後直接提交信號（Kimi 不可用時的備用通道）
    addStructuredView: publicQuery
      .input(z.object({
        expertName: z.string().min(1).max(60),
        title: z.string().min(1).max(200),
        url: z.string().url().max(500),
        date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
        summary: z.string().min(30).max(600),
        horizon: z.enum(["macro", "theme", "event"]).optional(),
        signals: z.array(z.object({
          asset: z.string().min(1).max(40),
          direction: z.enum(["bull", "bear", "neutral"]),
          strength: z.number().int().min(1).max(5),
          note: z.string().max(300).optional(),
        })).min(1).max(12),
      }))
      .mutation(({ input }) => addStructuredView(input)),
    // Phase 19b：結構化錄入 async job 化——同步 addStructuredView 喺受限網絡會超平台代理逾時（504），
    // 改 submit 即回 jobId + manualViewJob 輪詢（同 submitManualView 模式；input schema 與同步版完全一致）。
    submitStructuredView: publicQuery
      .input(z.object({
        expertName: z.string().min(1).max(60),
        title: z.string().min(1).max(200),
        url: z.string().url().max(500),
        date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
        summary: z.string().min(30).max(600),
        horizon: z.enum(["macro", "theme", "event"]).optional(),
        signals: z.array(z.object({
          asset: z.string().min(1).max(40),
          direction: z.enum(["bull", "bear", "neutral"]),
          strength: z.number().int().min(1).max(5),
          note: z.string().max(300).optional(),
        })).min(1).max(12),
      }))
      .mutation(({ input }) => submitStructuredView(input)),

    // 信號命中率回測：觀點庫信號 vs 其後 15 個交易日真實價格（6 小時緩存）
    signalBacktest: publicQuery.query(() => signalBacktest()),

    // 調倉記錄（runtime）：DB 優先（kind='rebalance_audit'），檔案鏡像 fallback，唔使登入
    rebalances: publicQuery.query(() => listRuntimeRebalances()),

    // Phase 17：淨值表現——DB 優先（kind='performance'），performance.json 檔案 fallback，都冇就 null
    performance: publicQuery.query(() => latestPerformance()),

    // 記錄調倉：用戶喺券商真實執行咗之後，喺度記低 → 圖表黃點、生效權重、淨值分段全部即時聯動
    // dryRun=true 只校驗+預覽，唔寫任何嘢（前端表單即時預檢用）
    recordRebalance: publicQuery
      .input(z.object({
        date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
        title: z.string().max(80).optional(),
        trigger: z.string().max(500).optional(),
        note: z.string().max(500).optional(),
        dryRun: z.boolean().optional(),
        changes: z.array(z.object({
          etf: z.string().min(1).max(12),
          to: z.number().min(0).max(40),
        })).min(1).max(25),
      }))
      .mutation(({ input }) => recordRebalance(input)),
  }),

  quotes: createRouter({
    live: publicQuery.query(() => getQuotes()),
  }),

  // 專家學習環（P0）：滾動命中率 → 因子自動調整 + 跑輸診斷；24h 緩存
  learning: createRouter({
    report: publicQuery.query(() => getLearningReport()),
  }),

  // 融合算法引擎（Calvin × 孫子兵法 × 專家信號）：內部 1 小時緩存，可直接調用
  algo: createRouter({
    analyze: publicQuery.query(() => getAlgoAnalysis()),
  }),

  // 持倉相關性 / 重複曝光分析：內部 6 小時緩存（日線級數據）
  correlation: createRouter({
    report: publicQuery.query(() => getCorrelationReport()),
    // 候選 ETF 篩選器：輸入 ticker → 重疊度/回報/風險/成本 + 誠實判語（白名單規則，唔經 LLM）
    screen: publicQuery
      .input(z.object({ ticker: z.string().min(1).max(12) }))
      .mutation(({ input }) => screenCandidateEtf(input.ticker)),
  }),
});

export type AppRouter = typeof appRouter;

// 启动每日调度（生产环境 + 已配置 YOUTUBE_API_KEY 时生效）
startScheduler();
