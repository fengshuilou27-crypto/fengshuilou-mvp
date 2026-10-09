# 專家觀點 ETF 組合追蹤系統 — 開發交接文檔

> **2026-09-05 強化版**：雙審計員全量復審後修復 12 項缺陷（含 K3 風控失效、調度器錯時 8 小時兩個 P0），新增批量貼鏈導入、信號命中率回測、Excel 導出、登入限流。詳見 §5、§10.10-10.13、§11。

> **2026-09-05 Phase 5（內容主動脈修復）**：用戶指出「網站係空殼，專家觀點從未真正更新」。根因有兩個：(a) 受限網絡下 YouTube API 被封，服務端無法做頻道發現；(b) **Moonshot 帳戶因餘額不足被暫停**（所有模型返回 `suspended due to insufficient balance`），LLM 結構化引擎完全停擺。修復：
> 1. 新增 `pipeline.addStructuredView` tRPC 端點——**繞過 Kimi**：字幕由 Agent（瀏覽器 + kome 字幕代理）取得並親自通讀全文後，把結構化信號直接 POST 入庫（同 addManualView 相同的快照合併路徑：去重 → 前插 → 重跑建議引擎 → 寫 DB+文件）。zod 嚴格校驗：URL 必填、日期格式、信號 1-12 個、asset 必須能映射到持倉工具否則剔除。
> 2. 首次實戰：5 條新觀點 26 個信號入庫（蔡金強 9/2、8/22、8/15；譚新強 8/29、8/22），觀點庫由 24 → 29 條。
> 3. `netCheck` 誠實化：Kimi 檢查由 TCP 探測改為真實最小 chat 調用，能分辨「帳戶已暫停：餘額不足」（之前欠費也顯示 ✓，屬誤報）。
> 4. 「專家觀點庫」頁合併即時快照：每張專家卡頂部顯示綠框「即時入庫」的管道觀點（按日期倒序），舊版靜態檔案降為歷史對照，頂部橫幅顯示入庫總數與最新日期。
> 5. **每日 HKT 09:00 Agent 掃描 cron**（平台提醒工具）：瀏覽器列舉 5 個頻道近 7 日新片 → 對比快照去重 → kome 抓字幕 → Agent 通讀全文結構化 → POST addStructuredView。呢條路**零 Moonshot 餘額都能運行**。
> 6. 待用戶行動：**Moonshot 帳戶需充值或更換 Key** 才能恢復 OCR/新聞搜索/全自動結構化。

> **給接手者（Kimi Work / 任何開發者）**：這份文檔是這個項目的完整「說明書 + 病歷 + 路線圖」。
> 讀完 §1–§5 你就理解系統在做什麼；§6–§9 是改代碼前必讀的技術細節；§10 是血淚教訓（每條都對應一個真實事故）；§11 是後續優化的優先級清單。
> 最後更新：2026-08-01（Franky）

---

## §1 項目概述

**一句話**：把 8 位投資專家（蔡金強、譚新強、洪灝、林本利、林一鳴、莊太量、Jurrien Timmer、蔡嘉民 Calvin）的公開觀點（YouTube 視頻 / 專欄 / 媒體訪談）系統化抓取、結構化成「資產方向信號」，經時間衰減加權後與 Calvin 量化算法融合，驅動一個 19 隻 ETF 組合的**調倉建議**引擎，並做前向實盤追蹤驗證。

**使用者**：Franky 個人真金白銀投資。私密部署（訪問密碼門禁），不公開。

**鐵律（不可違反）**：
1. **調倉建議永不自動執行**——永遠只是「建議」，必須人工複核（頁面有「我已複核」按鈕）。
2. **寧缺毋濫**——抓不到可靠證據時誠實記錄「跳過」，絕不允許 LLM 憑訓練知識編造專家觀點（見 §10.4，這是拿假鏈接換來的教訓）。
3. **證據等級透明**——每條觀點都標註來源通道與證據等級（完整字幕 > 字幕代理 > 全文報道 > 搜索摘要 > 主題掃描），用戶可點鏈接核實。
4. **.env 密鑰只在服務端使用**，前端代碼不得引用任何 `process.env.*KEY`；不向 DB 寫入密鑰。
5. 數據庫遷移**禁止 `db:push --force`**，禁止 drop 表。

**9 個頁面**（單頁應用 tab 切換）：總覽 / 組合配置 / 信號共識矩陣 / 量化算法 / 每日更新 / 調倉記錄 / 專家觀點庫 / 復盤驗證 / 方法論。（Phase 9「我的持倉」已於 Phase 10 撤回，富達持倉改為獨立網站，見 Phase 10。）

---

## §2 快速上手

```bash
# 環境：Node 20+，需要一個 MySQL（TiDB 兼容）連接串
npm install
cp .env.example .env   # 然後填入 §8 列出的所有值
npm run dev            # 開發：vite dev server（:3000，含 API 中間件）
npm run build          # 生產構建：vite build（前端→dist/public）+ esbuild（api/boot.ts→dist/boot.js）
npm start              # 生產運行：NODE_ENV=production node dist/boot.js（:3000）
npm run check          # tsc 類型檢查（改代碼後必跑）
npm run db:generate && npm run db:migrate   # schema 變更後的遷移（安全路徑）
```

**Docker（自部署，唯一依賴）**：項目根目錄 `Dockerfile` 已備好——`docker build -t etf-tracker . && docker run -d -p 3000:3000 etf-tracker`。.env 會被打進鏡像（私密部署可接受；若要分發鏡像請改走 secrets）。

**Kimi 平台部署**：此項目在 Kimi 平台（kimi.com）開發，預覽 = vite dev server（端口 3000 被平台佔用，見 §10.1），發布 = 用 Dockerfile 起生產容器。交接給 Kimi Work 後若仍在同平台，行為一致。

---

## §3 架構總覽

```
┌─ 抓取層（api/pipeline.ts，每日 HKT 08:00 + 手動觸發）─────────────┐
│  ① YouTube 頻道新視頻（Data API）→ 直連字幕軌 → kome.ai 字幕代理兜底 │
│  ② Wind 財經新聞搜索（agent-gw）× 8 位專家全名 → 名實相符過濾       │
│  ③ Kimi $web_search 主題掃描（7 個市場主題，媒體匯總級）            │
│  ④ Brave Search（開放網絡才可用）                                  │
│  ⑤ 手動錄入：貼鏈接抓字幕 / 截圖 OCR / 直接貼全文                  │
└──────────────┬───────────────────────────────────────────────────┘
               ▼  全部通道產出統一 SnapshotView（標題/日期/URL/信號[]/衰減權重）
┌─ 結構化層 ───────────────────────────────────────────────────────┐
│  Moonshot chat API（模型回退鏈 kimi-k2.5→kimi-k3→moonshot-v1-auto） │
│  → 每條內容提取 {summary, horizon, signals:[{asset,direction,strength}]}│
└──────────────┬───────────────────────────────────────────────────┘
               ▼  併入快照（跨輪保留 60 天未衰減觀點，URL+標題去重）
┌─ 融合算法層（api/algo.ts）───────────────────────────────────────┐
│  expert_score（觀點×衰減×強度）+ trend_score（SMA200/mom126）      │
│  → Calvin K1-K10 戰術閘門 × 孫子 S1-S11 戰略閘門 → 每隻 ETF 加/減倉建議│
└──────────────┬───────────────────────────────────────────────────┘
               ▼  寫入 snapshots 表 + public/data/snapshot.json + dist/public/data/
┌─ 展示層（React）─────────────────────────────────────────────────┐
│  tRPC（/api/trpc）+ 靜態 JSON（/data/*.json，vite 直出）→ 9 個 tab │
└──────────────────────────────────────────────────────────────────┘
```

**兩個運行時**（重要）：同一份代碼跑在 ① vite dev server（開發/平台預覽，@hono/vite-dev-server 只把 `/api/*` 交給 Hono）和 ② esbuild 打包的 `dist/boot.js`（生產/發布）。任何中間件級功能（如門禁）必須**兩邊都實現**——見 gate-core.ts 的設計。

---

## §4 目錄結構（逐文件註解）

```
app/
├── api/                        # 後端（Hono + tRPC 11）
│   ├── boot.ts                 # 生產入口：掛中間件、tRPC(/api/trpc)、靜態、啟動調度器
│   ├── router.ts               # tRPC 路由表：quotes/pipeline/algo/correlation 五組
│   ├── middleware.ts           # publicQuery/authedQuery/adminQuery 三級過程
│   ├── context.ts              # tRPC context
│   ├── pipeline.ts (832 行)    # ★核心：抓取管道+結構化+調度器+手動錄入+OCR+網絡自檢
│   ├── algo.ts (406 行)        # ★核心：Calvin×孫子融合算法（K1-K10 × S1-S11）
│   ├── correlation.ts          # 持倉相關性/重複曝光分析（近1年日收益皮爾遜相關，6h緩存）
│   ├── screener.ts             # 候選 ETF 篩選數據層（correlation.screen；bundle 6h 緩存+逐 ticker 緩存；
│   │                           #   ER 屬「百分數風格」口徑，見 §10.24）
│   ├── marketdata.ts           # 行情雙引擎（直連 Yahoo → agent-gw 兜底）+ RFC4180 CSV 解析
│   │                           #   + gwDatasourceCall/csvToRecords（通用數據源調用，給 pipeline 用）
│   ├── quotes.ts               # 實時報價（帶 in-flight 去重，見 §10.5）
│   ├── gate-core.ts            # 門禁共享核心（零 hono 依賴：token 計算/cookie 驗證/登錄頁 HTML）
│   ├── gate.ts                 # 生產側門禁：/api/auth/login|logout + gateMiddleware
│   ├── lib/env.ts              # dotenv/config 加載 + 必填環境變量校驗
│   ├── lib/http.ts             # tfetch 封裝（超時）
│   ├── lib/vite.ts             # vite 靜態服務輔助
│   └── queries/connection.ts   # Drizzle MySQL 連接（getDb）
├── contracts/                  # 前後端共享契約
│   ├── types.ts                # Snapshot/SnapshotView/SnapshotSignal/PipelineStatus/AlgoRuleState/CorrelationReport
│   ├── algoRules.ts            # 算法規則元數據（前端「量化算法」頁展示用）
│   ├── perfStats.ts            # 組合表現統計單一口徑計算器（前後端共用，netRet=portRet−costDrag）
│   ├── screener.ts             # 候選 ETF 篩選純函數層：pearson/retStats/weightedPortfolioReturns/screenVerdict（判語白名單）
│   ├── backtest.ts             # 信號回測純函數層：BT_WINDOWS(5/15/45/90)/scoreHit/evalWindows/aggregateWindow/aggregateExpert（ACWI 超額命中口徑，Phase 12）
│   └── errors.ts
├── db/
│   ├── schema.ts               # snapshots(id,kind,payload,created_at) + pipeline_runs
│   ├── relations.ts / seed.ts
├── src/                        # 前端（React 19 + Vite + Tailwind + shadcn/ui）
│   ├── pages/Home.tsx (1331 行) # ★全部 9 個 tab 的頁面 + ScreenerSection（單文件巨组件，見 §11 重構建議）
│   ├── App.tsx / main.tsx      # 路由/tab 框架；main.tsx 包了 ErrorBoundary（§10.3）
│   ├── components/ErrorBoundary.tsx  # 防白屏最後防線
│   ├── components/ui/*         # shadcn/ui 組件庫（勿手改，用 npx shadcn add）
│   ├── data/portfolio.ts       # ★靜態策展數據：19 隻 ETF 定義、3 次調倉記錄、當前權重
│   ├── data/experts.ts         # ★靜態策展數據：8 位專家檔案+手工策展觀點庫（基線）
│   ├── hooks/useLiveData.ts    # useQuotes/usePerformance/useFileSnapshot/useAlgo 等
│   ├── lib/consensus.ts        # 前端共識信號計算（computeConsensus/THEME_ACTIONS）
│   └── providers/trpc.tsx      # tRPC client（httpBatchLink /api/trpc，superjson，credentials:include）
├── public/data/                # 管道產出的靜態 JSON（snapshot.json / performance.json）
├── vite.config.ts              # ★含 gatePlugin()——開發側門禁中間件（§6）
├── Dockerfile / .dockerignore  # 自部署
├── .env                        # 真實密鑰（不入 git/交接包，見 §8）
└── HANDOVER.md                 # 本文檔
```

---

## §5 數據流與核心管道

**每日 HKT 08:00**（`startScheduler()`，服務啟動 60 秒後也補跑一次）執行 `runPipelineInner`：

1. **網絡探測**：googleapis/youtube/brave/agent-gw/kome 各 4 秒探針，日誌明確寫出哪個通道不可用。
2. **YouTube 專家通道**（開放網絡才生效）：`CHANNELS` 5 個頻道 → Data API 解析上傳清單 → 近 45 天（`LOOKBACK_DAYS`）新視頻 → 字幕（直連 captionTracks → **kome.ai 代理**兜底）→ 結構化。受限網絡時整段誠實跳過並寫日誌。
3. **Wind 專家新聞通道**（受限網絡也可達，主力）：`WIND_EXPERTS` 8 位 → `wind_get_financial_news`（agent-gw）→ **名實相符過濾**（簡繁/譯名變體必須出現在標題或正文，防「蔡金強」誤中「中信建投金强」）→ 近 45 天 → 每人最新 2 條 → 結構化。
4. **新聞面**：Brave 可達時按專家名搜；否則 Kimi `$web_search`（兩輪協議）按 7 個市場主題掃描（標註「媒體匯總，非專家背書」）。
5. **跨輪保留**：載入上一快照，60 天內未衰減觀點按 `URL+標題` 去重後併入（手動錄入不會被每日管道沖掉，§10.6）。
6. **融合算法** `buildSuggestions(views)` → 建議（永不自動執行）。
7. **落庫**：`snapshots` 表（kind=daily）+ 寫 `public/data/snapshot.json` 和 `dist/public/data/snapshot.json`（**兩個路徑都要寫**，dev 服 public/，生產服 dist/public/）。
8. `updatePerformance()`：把當日組合淨值追加到 `performance.json`（前向實盤追蹤）。

**手動錄入四通道**（證據等級相同，都過同一個 `structureWithKimi`）：
- `fetchVideoTranscript(url)`：貼 YouTube 鏈接 → kome 代理取完整字幕（發佈者停字幕則誠實報錯）。
- `batchImportVideos(urls[], expertName?)`：**批量導入**（≤10 條/次）——逐條抓字幕+結構化，已入庫視頻按 videoId 去重跳過，全部完成後**只寫一次快照、只跑一次建議引擎**（避免 N 次重複計算）。
- `ocrTranscript(images[])`：截圖 → `moonshot-v1-32k-vision-preview` 轉錄。
- `addManualView(...)`：全文 ≥100 字門檻 → 結構化 → 併入最新快照 → 重跑建議 → kind=manual 落庫。**只有出現新建議時才重置 acknowledged**（修復：無新建議時不再把未復核建議誤標已復核）。

**信號命中率回測** `signalBacktest()`（6 小時緩存，復盤驗證頁頂部卡片；2026-09-11 Phase 12 升級）：觀點庫每條信號 → `mapAsset` 對應 ETF → 由發布日起喺 **5/15/45/90 四個交易日窗口**逐格驗證；命中以**對 ACWI 嘅超額收益**判定（看多 >+0.5pp / 看空 <−0.5pp / 中性 |超額|≤2pp——剔除大市順風，先係專家淨實力）；未到期窗口顯示「—」唔計入。聚合：`byWindow`（每窗 hitRate + 方向信號平均**簽名**超額（bear 取反），decided<10 標「樣本不足」）+ `byExpert`（15 交易日主窗，decided<3 標不足）。這是**前向樣本外**檢驗，與規則重放回測不同。截至 2026-09-11：5 日窗 52 條可判定、15 日窗 23 條、45/90 日窗全部未到期（觀點庫 2026-07-15 先開始）。

**Excel 導出**：總覽頁「📊 導出 Excel」按鈕——前端生成 UTF-8 BOM CSV（持倉+建議+淨值序列+統計四段），Excel 直接打開無亂碼。

**Agent 結構化錄入** `addStructuredView(...)`（2026-09-05 Phase 5 新增，**Kimi 失效時的備用主通道**）：字幕由 Agent 側（瀏覽器列舉頻道 + kome 代理抓字幕 + Agent 親自通讀全文）完成發現與結構化，此端點只校驗與合併，**不調用 LLM**。校驗規則：URL 必填（無鏈接不入庫）、日期 YYYY-MM-DD、摘要 ≥30 字、信號 1-12 個且 asset 必須可映射到持倉工具（`mapAsset`，不可映射則剔除並計數）。合併路徑與 addManualView 完全相同（載入最新快照 → URL/videoId 去重 → 前插 → buildSuggestions → kind=manual 落庫 + 雙寫文件）。配套：**每日 HKT 09:00 Agent 掃描 cron**（平台提醒任務）執行完整掃描循環，零 Moonshot 餘額可運行。

**衰減**：`decay(date, now, horizon)`——半衰期 21 天（theme），macro/event 檔位不同；超 90 天權重歸零僅存檔。

---

## §6 抓取通道矩陣（網絡現實，改代碼前必懂）

| 通道 | 受限網絡（Kimi 平台） | 開放網絡（自部署） | 說明 |
|---|---|---|---|
| YouTube Data API / 直連字幕軌 | ✗ 防火牆 | ✓ | 頻道發現只能靠它（或 Brave） |
| **kome.ai 字幕代理** | **✓（實測）** | ✓ | `POST https://kome.ai/api/transcript {"video_id"}` 免 key；發佈者停字幕時返回錯誤句（已用關鍵詞+長度雙判別） |
| **Wind 財經新聞（agent-gw）** | **✓（實測）** | ✓ | 專家全名搜索，真實 URL+日期+全文 |
| Moonshot chat + $web_search | ✓ | ✓ | api.moonshot.cn 被放行 |
| Moonshot vision（OCR） | ✓ | ✓ | moonshot-v1-32k-vision-preview |
| Brave Search | ✗ | ✓（需 BRAVE_API_KEY） | |
| agent-gw 行情（yahoo_finance） | ✓ | ✓ | 行情雙引擎的兜底腿 |

**教訓**：這個防火牆是「域名放行制」——不要假設某域名不通，用 `probeHost()` 實測。Invidious/Piped 公共實例全被封；youtubetranscript.com 可達但被 YouTube 反爬（返回 "blocking us"）。

---

## §7 Calvin × 孫子融合算法（api/algo.ts）

**輸入**：最新快照全部 views 的 signals（按 ticker 映射、衰減加權、強度歸一 → `expertScore ∈ [-1,1]`）+ 行情層（`trendScore = 0.5×sign(price−SMA200) + 0.5×sign(mom126)`，z-score，VOO 20 日波動率 regime）。

**融合**：`raw = (1−trendW)×expertScore + trendW×trendScore`（trendW 常態 0.5 / K6 高波動 regime 0.7）；S6 擊其惰歸（z<−2 且 trend≥0 → ×1.2）；K4 equity gate（組合淨值 < 9 日均線 → ×0.5 且**否決一切加倉**）；`fused = clamp(50+50×raw, 0, 100)`。

**閘門**（任一不過則否決）：S1 廟算 ≥60 加 / ≤40 減；S6 避其銳氣（z>+2 禁追）；S9 組合熱度（高相關分組 ≤30pp）；S10 冷卻期；K3 MDD 倉位上限；K7 首倉 ≤2pp；K5 頂部止盈（mom126≥25% 且 z≥1.5 → 減 1/4）；K8 單輪換手上限 15pp。

**輸出**：`suggested: SuggestedChange[]` + `suggestedNote` + 每規則的通過/否決明細（前端「量化算法」頁展示 `AlgoRuleState`）。**建議需要人工按「我已複核」**（`acknowledged` 旗標關閉全站橫幅）。

---

## §8 環境變量（.env）

| 變量 | 必填 | 用途 |
|---|---|---|
| `DATABASE_URL` | ✓ | MySQL/TiDB 連接串。**注意**：Kimi 平台給的是 privatelink 內網地址，導出代碼到平台外需自備 DB 並跑遷移 |
| `APP_ID` / `APP_SECRET` | ✓ | 應用配置；APP_SECRET 同時是門禁 token 的 HMAC 密鑰 |
| `KIMI_API_KEY` | ✓ | Moonshot API（結構化+搜索+OCR 都靠它） |
| `KIMI_BASE_URL` | | 默認 https://api.moonshot.cn/v1 |
| `KIMI_MODEL` | | 結構化模型覆蓋（不設則走回退鏈，§10.2） |
| `YOUTUBE_API_KEY` | 開放網絡必填 | YouTube Data API（頻道發現） |
| `BRAVE_API_KEY` | | Brave 新聞搜索 |
| `NEWS_API_KEY` | | 預留 |
| `ACCESS_CODE` | | 訪問門禁密碼（空 = 關閉門禁）；當前值見本地 .env——**密碼值不進 git、不寫入文檔**（2026-09-05 起脫敏） |
| `AGENT_GW_API_KEY` / `AGENT_GW_BASE_URL` | | 顯式覆蓋 agent-gw 憑證；不設則讀 `~/.kimi/agent-gw.json` |
| `VITE_APP_ID` | | 平台 OAuth 預留 |

**安全備忘**：主人曾把部分 key 貼到公開對話——建議儘快輪換全部 key；key 只允許出現在服務端 .env。

---

## §9 數據庫與門禁

**schema**（`db/schema.ts`）：`snapshots(id, kind['daily'|'manual'], payload JSON, created_at)`；`pipeline_runs(...)`。快照永遠 append（`desc(id) limit 1` 取最新），不更新歷史行——歷史快照即審計軌跡。

**門禁**（無狀態 HMAC）：`token = HMAC_SHA256(APP_SECRET, "etf-gate-v1:"+ACCESS_CODE)`；cookie `etf_auth`（httpOnly, sameSite=Lax, 30 天）；`timingSafeEqual` 比對。**兩個運行時各自實現**：生產 = `api/gate.ts` 的 Hono middleware；開發 = `vite.config.ts` 裡 `gatePlugin()` 的 connect middleware（因為 @hono/vite-dev-server 只把 `/api/*` 交給 Hono，頁面請求根本不經過它）。共享邏輯全在 `api/gate-core.ts`（零 hono 依賴，且 **env 從 .env 文件直讀**——vite 熱更新不會重讀 process.env，§10.1）。

---

## §10 血淚教訓（接手者必讀，每條都是真實事故）

**10.1 平台預覽 =  vite dev server 佔用 :3000**。你在這個環境 `npm start` 永遠 EADDRINUSE；驗證要對 dev server 做（它熱重載代碼但**不重讀 process.env**——所以 gate-core 直接讀 .env 文件）。別試圖殺掉它。

**10.2 LLM 模型會被平台下架**。硬編碼 `kimi-k2-0711-preview` 在某天 404 了，整條結構化管道靜默全滅。現在 `structureWithKimi` 有回退鏈（`KIMI_MODEL`→kimi-k2.5→kimi-k3→moonshot-v1-auto）+ 緩存可用模型 + 非 JSON 回應防御。**任何新的 LLM 調用都必須有降級路徑。**

**10.3 React hooks 順序崩潰導致白屏**。LiveStrip 把 `usePerformance()` 放在 early return 之後——數據到達時 hook 數量變化 → 整樹崩潰 → 白屏。規矩：**所有 hooks 必須在任何 early return 之前**；`main.tsx` 已包 `ErrorBoundary` 兜底。

**10.4 LLM 搜索會編造「專家觀點」**。曾用「專家名+觀點」讓模型搜索，產出 `youtube.com/watch?v=example123` 假鏈接和張冠李戴的舊聞——真金白銀場景這是毒藥。所以專家觀點**只接受**：字幕/全文級證據（管道①②⑤）或標註「非專家背書」的主題級掃描（③）。**永遠不要重新引入「讓 LLM 憑印象總結某專家觀點」的兜底。**

**10.5 tRPC 路徑與並發**。API 掛在 `/api/trpc/*`（不是 `/trpc/*`）；行情 21 隻並發打 agent-gw 會限流——quotes.ts 有 in-flight 去重，marketdata.ts 有 0-2s 抖動 + 指數退避重試 2 次。新增批量調用照這個模式做。

**10.6 每日管道曾沖掉手動錄入**。舊版每次運行生成全新快照 → 手動錄入隔夜消失。現在有跨輪保留（§5.6）。**改快照生成邏輯時不要破壞這個不變式。**

**10.7 CSV 必須狀態機解析**。數據源返回的 CSV 字段含引號內換行/逗號，naive split 會列錯位（VOO 價格曾被移成 15.42）。用 marketdata.ts 的 `csvToRecords`。

**10.8 同名異人**。Wind 按子串匹配，「蔡金強」會命中「金强」——`variants` 全名過濾是必須的，新增專家時記得加簡繁變體。

**10.9 snapshot.json 要寫兩個路徑**：`public/data`（dev）+ `dist/public/data`（生產）。漏一個就會出現「預覽有數據、發布站沒數據」。

**10.10 HKT 08:00 ≠ UTC 00:00 − 8h**。調度器曾多減一次 8 小時 → 實際在 HKT 00:00 午夜運行。`msUntilNext8amHKT` 的正確做法：把 UTC 時間 +8h 取「下個 UTC 日期零點」即是 HKT 08:00，**不要再減回去**。

**10.11 負數指標要取絕對值再用**。`mdd1y`（最大回撤）是負值，`Math.max(mdd1y*100, 5)` 永遠等於 5 → K3 風控上限恆為 15pp 形同虛設（2026-09-05 雙審計員獨立命中）。凡「虧損/回撤」類指標進公式前先 `Math.abs`。

**10.12 MM-DD 字串不能跨年比較**。`performance.json` 日期是 MM-DD 展示格式，"01-05" < "12-30" 會讓跨年追加靜默停擺——內部一律用完整 ISO 日期比較排序（updatePerformance 已修）。

**10.13 在線密碼要限流**。`/api/auth/login` 已加進程內滑動窗口（每 IP 10 分鐘 10 次）；若改為多實例部署，限流要移到 Redis/DB 層。

**10.14 「依賴可用」≠「帳戶可用」**。netCheck 曾對 api.moonshot.cn 做 TCP HEAD 探測，帳戶因欠費被暫停時 TCP 依然通，UI 顯示 ✓ Kimi API 誤導用戶以為管道正常——實際結構化引擎已死。教訓：外部服務健康檢查要用**最小真實業務調用**（1 token chat），並把帳戶級錯誤（suspended/insufficient balance）與網絡錯誤分開顯示。

**10.15 工程拋光不能替代內容主動脈**。Phase 4 修了 12 個工程缺陷，但用戶一句「呢個只係空殼」點醒：系統存在的唯一理由係「新鮮專家觀點自動流進來」。受限網絡下服務端 YouTube 發現+LLM 結構化都斷咗，等於管道得個殼。解法係把「發現+結構化」搬到 Agent 側（瀏覽器可直連 YouTube、kome 字幕代理可達、Agent 自己讀字幕提取信號），服務端只做校驗與合併（addStructuredView）。呢個模式零 LLM 餘額都運行到，係受限環境下嘅長期方案。

**10.16 頻道 handle 錯一個字就係長期盲區**。`CHANNELS` 入面 etnet 寫咗 `@etnetTV`，官方實際係 `@etnethk`——洪灝嘅專訪全部喺 @etnethk，呢個錯 handle 令洪灝嘅字幕管道從未成功過（只有 Wind 新聞通道執到佢啲報道）。2026-09-06 用戶貼出 4 條鏈接先揭發。教訓：頻道清單要定期用瀏覽器人工核實 handle 真身；另洪灝仲會出現喺第三方頻道（如「大師說」），每日 cron 已加 web_search 補第三方轉載。kome 冇字幕時唔好直接放棄——etnet 專訪必有文字稿（newsid 頁全文），屬「全文報道級」證據可入庫。

**10.17 「即時計算」要有真數據流先算數**。2026-09-06 終審發現信號共識矩陣自稱「即時計算」，實則 `computeConsensus()` 只讀靜態 `EXPERTS` 檔案——31 條管道觀點從未入矩陣（黃金 +26 係舊數，長債 bear、比特幣 bull 全部冇影）。修復：`computeConsensus(now, liveViews)` 接受即時觀點（專家名雙向包含匹配 → 強度歸一化 × 同一衰減規則），TOP 5 卡同源；`useMergedConsensus()` 統一 tRPC→文件兜底；補 8 條回歸測試。教訓：**UI 文案話「即時」就要有測試證明佢即時**。
**10.18 深色站要設 `color-scheme: dark`**。唔設嘅話瀏覽器原生控件（date 輸入、select 下拉、滾動條）按淺色主題渲染——黑字黑圖標落喺深色背景上，「點進去根本看不清楚」。一行 CSS 根治全站原生控件對比度。
**10.19 訂閱會員 ≠ API 餘額，狀態燈要講「點解」**。用戶見「Kimi API ✗ 餘額不足」唔明點解自己嘅 Allegro 會員冇用——kimi.com 消費者訂閱同 platform.moonshot.cn 按量計費係兩套獨立帳務。教訓：紅燈狀態要附帶「點解會咁 + 咩唔受影響 + 點樣恢復」，齋報故障只會製造迷惑。

**10.20 部分更新 = 結構性分裂**。管道 `updatePerformance()` 每日追加淨值後只更新 `stats.portRet/benchRet` 兩行，`netRet/maxDD/vol/Sharpe` 永遠凍結喺 2026-07-23——結果頂部 pill 顯示毛 +12.3%、總覽大數字顯示舊淨值 +7.97%，差 4.3pp 但成本只得 0.12pp，差異全部係陳舊。教訓：**派生統計必須同源同刻重算**——任何一個數字係「舊快照嘅函數」而另一個係「新序列嘅函數」，全站數字就會互相矛盾。修法：單一純函數 `contracts/perfStats.ts`（方法學經反向驗證 100% 重現 07-23 錨定值：樣本 std×√252、日曆日 CAGR、rf=4%、netRet=portRet−costDrag），管道寫文件時調用、前端讀取時再即場重算（唔信文件 stats 欄位）；回歸測試鎖死「文件 stats ≡ 序列重算」。

## 2026-09-08 Phase 9：新增我的持倉頁（⚠ 已於 Phase 10 撤回——業主要求富達持倉做獨立新站，唔准混入本站）
1. 新增 `src/data/myHoldings.ts`：富達香港真實帳戶手工快照（截至 2026-09-08，12 隻基金、總市值 57,222.98 USD、累計盈虧 +4,092.06 USD / +7.70%），數字按帳戶截圖原樣錄入、不得改動；`computeMyHoldingsStats()` 單一純函數即時計算權重（value÷balance）、前三集中度、幣種/風險聚合（§10.20 同源口徑，權重不硬編碼）。
2. Home.tsx 新增第 10 個 tab「我的持倉」（置於「組合配置」之後）：帳戶總覽卡、權重 donut、各基金盈虧橫向圖、持倉明細表（市值降序、風險 4-5 級高亮）、觀察點評卡（全部由快照數據即時推導）；明確標注「本页数据为手工快照，不随每日管道自动更新」，與專家 ETF 組合互相獨立、不參與信號引擎。
3. 新增 `src/lib/myHoldings.test.ts` 5 條回歸：Σvalue=57,222.98、Σpnl=4,092.06、Σweights=100%、總盈虧率≈7.70%、持倉 12 行。

## 2026-09-08 Phase 9.5：修復「立即复核」橫幅掣冇反應（用戶手機回報）
1. **根因**：待覆核橫幅個掣舊版係 `onClick={() => setTab('每日更新')}`——用戶當時已經企咗喺「每日更新」頁，React setState 傳入相同值會 bail out（唔 re-render），所以**完全冇任何反應**；就算喺其他頁按，都只係切頁、唔會帶你去建議卡。
2. **修法**（Home.tsx 三處）：① 橫幅掣改為切頁 + `setTimeout(120ms)` 後 `document.getElementById('pending-review')?.scrollIntoView({behavior:'smooth'})`——同頁時 setTab 係 no-op，滾動先係實際回應；② `Card` 組件加可選 `id` prop，`section` 加 `scroll-mt-32`（避開 sticky header 約 128px 遮擋）；③ 「建議調倉」卡加 `id="pending-review"` 錨點。加 `active:bg-amber-500/45` 令按壓有即時視覺反饋。
3. **教訓（§10.21）**：**導航型按鈕唔可以齋靠 setState**——目標狀態已經係現狀時，React 會靜默吞咗次點擊，用戶睇落就係「掣壞咗」。凡「帶用戶去某處」嘅掣，要有唔依賴狀態變化嘅副作用（滾動/焦點/提示）做兜底回應。
4. 同日另一 session 已將相同修復推上 GitHub（bc5fdc5，+9/−5，只郁 Home.tsx）；本檔已與 remote main 逐字節對齊（Home.tsx blob `6abf1afb`）。tsc clean、vitest 22/22、build OK。

## 2026-09-09 Phase 10：撤回「我的持倉」頁（業主澄清：富達持倉要獨立新站，唔係改本站）
1. **業主原話**：「我富达基金的那个是想要你再开额外另外的一个网站来去建构，不是让你改动现有的网站来去处理」。Phase 9 由另一 session 誤解需求加入本站，現整頁撤回。
2. **還原內容**：Home.tsx 回到 Phase 8 基準（blob `58321680`）+ Phase 9.5「立即复核」三處修復 + bc5fdc5 嘅「tRPC 優先」comment 文字（新 blob `3b27b762`）；刪除 `src/data/myHoldings.ts` + `src/lib/myHoldings.test.ts`（本地 + GitHub 同步刪除）。§1 頁面數 10→9。
3. **閘門**：tsc clean、vitest 17/17（consensus 8 + gate-core 5 + perfStats 4；5 條 myHoldings 測試隨檔案移除）、build OK。
4. **富達持倉新站**：同一批快照數據（12 基金、57,222.98 USD、+4,092.06 / +7.70%，截至 2026-09-08）原樣搬去獨立靜態網站 `fidelity-portfolio/`（不屬本 repo），派生數字同樣由頁面 JS 即時計算（§10.20 同源口徑），手動快照、不隨管道更新。
5. **教訓（§10.22）**：**新需求先問「改現有站定開新站」**——用戶話「加我的持倉」時，默認改現有站係錯嘅假設；涉及真金白銀嘅站，結構變動（加頁/加功能）要先確認落點。

## 2026-09-10 Phase 10.1：入庫失敗 429 根因確診 + 錯誤改人話提示
1. **根因**：用戶報「Kimi 結構化失敗： Kimi API 429 (moonshot-v1-auto)」（貼 9/2 蔡金強《金人金語》10,082 字字幕入庫時）。直測 API 證實 **Moonshot 帳戶因餘額不足被暫停**（HTTP 429 "suspended due to insufficient balance"），kimi-k2.5 / kimi-k3 / moonshot-v1-auto / moonshot-v1-8k 全部同一結果——帳戶級，唔係單模型下架、唔係瞬時限流，代碼層面修唔到，必須用戶去 platform.moonshot.cn 充值或更換 .env 嘅 KIMI_API_KEY（§11 P0 阻塞項維持不變）。
2. **冇嘢丟失**：嗰條 9/2《金人金語》其實早已喺觀點庫（snapshot.json 51 條之一，videoId TJ9F4GCqT14，Agent 結構化通道入庫）；kome 抓字幕核對 10,082 字與用戶截圖一致。就算當時入庫成功，URL/videoId 去重都會跳過——數據零損失。
3. **修復（api/pipeline.ts `structureWithKimi`）**：回退鏈遇 `!r.ok` 時先讀 error body，含 `suspended|insufficient balance` → 直接設人話錯誤（「Moonshot 帳戶因餘額不足已被暫停（HTTP 429）——請到 platform.moonshot.cn 充值，或更換 .env 嘅 KIMI_API_KEY；充值前可改用對話嘅 Agent 結構化通道（唔經 Moonshot）」）並 `break`，唔再逐個模型白試。netCheck 嘅 moonshotDetail 早前已係同款處理。
4. **閘門**：tsc clean、vitest 17/17、build OK；E2E（gate 登錄 → addManualView 貼文）返回人話錯誤且失敗唔寫 DB。本地 commit 2126624；GitHub commit e80bd4fa（blob `91a92f35`，63,320 bytes，同本地 byte-exact 核對；首次推送因轉錄甩咗 6 bytes，逐 chunk 臨時檔二分定位後重推修正）。
5. **教訓（§10.23）**：**429 要讀 body 先定性**——同係 429，「瞬時限流」可以 retry，「帳戶暫停」retry 幾多次都冇用；拋俾用戶嘅錯誤要講埋「點做」，唔好齋拋個 status code。

## 2026-09-10 Phase 11：候選 ETF 篩選器（correlation.screen——買新嘢前必過呢關）
1. **源起**：用戶問「點解唔揀富達 passive ETF？covered call strategy ETF（JEPI/QYLD 等）同其他 ETF 相關性係咪都好高？總回報會打贏嗎？係咪應該喺 ETF 都做個篩選？」Yahoo 實測答案：相關性確實高（同標普系 ρ 約 0.68–0.95），但近 1 年牛市總回報全部跑輸本尊 8–28pp——covered call 嘅角色係「防守性替代」（波動/回撤較低、息率高但或含 ROC），唔係「加強版指數」。呢個結論嘅制度化落地就係：買任何新 ETF 前，用與相關性卡同一數據口徑做硬性篩選，判語規則寫死、唔經 LLM（§10.4 同一原則：唔俾模型憑印象編造）。
2. **架構**（本地 commit 448dcd0，5 檔 +577 行）：`contracts/screener.ts` 純函數層——`dailyReturnsByDate`/`pearson`（≥30 個共同交易日先出數，3dp）/`retStats`/`weightedPortfolioReturns`（共同日期交集，首 ticker keys 初始化、`slice(1)` 起循環，避開 TS null 收窄成 never 嘅陷阱）/`screenVerdict`（判語白名單），前後端共用可單測；`api/screener.ts` 數據層——持倉+ACWI 一年日線 bundle（6h 緩存 + in-flight 去重，§10.5 模式）、候選逐 ticker 6h 緩存、`fetchInfo` 攞名稱/基金家族/AUM/息率/費率；`api/router.ts` 加 `correlation.screen` mutation（ticker 先規範化，`^[A-Z][A-Z0-9.\-]{0,11}$`，拒絕現有持倉、拒絕空載；≥60 個收盤價 + ≥10 隻可用持倉先計）；Home.tsx 新增 `ScreenerSection` 插入 CorrelationCard 底部（快捷 chips JEPI/JEPQ/QYLD/XYLD，結果卡分「統計 chips／相關 chips／判語盒」三層 + 誠實聲明）。
3. **判語規則（screenVerdict 白名單，寫死唔經 LLM）**：ρ（候選 vs 組合加權）≥0.8 且 1y 回報 < VOO → ⛔ 唔建議加入（高重疊兼跑輸）；≥0.8 且 ≥VOO → 🔁 只宜替代式持有（唔好疊加）；<0.5 → ✓ 具分散價值；其餘（含數據不足 ρ=null）→ ◐ 有限分散價值。警示 flags：最高單一持倉 |ρ|≥0.75、息率 ≥6%（或含 ROC，港人股息 30% 預扣稅）、波動 ≤VOO×75%（標明防守性，唔係缺點）、ER >0.6%（偏貴）、AUM <US$500M（規模細）。**結論永遠只係建議，落唔落單人工決定**——與「調倉建議絕不自動執行」原則一致。
4. **教訓（§10.24）**：**Yahoo CSV 同名欄位口徑唔同，接入必用真實值錨定**——`yield` 係分數（0.0797 = 7.97%）；ETF 嘅 `dividendYield` 已係百分數；而 `annualReportExpenseRatio` 係「百分數風格」（0.35 即 0.35%，**唔好 ×100**）——初版 ×100 令 JEPI 費率顯示 35%。修法：raw parse + sanity bound（只接受 [0.01, 5] 區間，否則留空顯示「—」）。錨定值：JEPI ER=0.35%、QYLD ER=0.60%。
5. **閘門**：tsc clean；vitest 32/32（4 檔：consensus 8 + gate-core 5 + perfStats 4 + screener 15——pearson/retStats/weightedPortfolioReturns/四檔判語/null ρ→limited/flags/dailyReturnsByDate 邊界）；E2E（gate 登錄 → POST correlation.screen?batch=1）：JEPI → ER 0.35%、息率 7.97%、AUM $46.16B、1y +7.2%、波動 8.0%、vs 組合 ρ=0.51、最高重疊 VOO 0.68、同期 VOO +17.6% → ◐；QYLD → ER 0.60%、1y +22.1%、vs 組合 ρ=0.78、最高重疊 VOO 0.85 → ◐（數據截至 2026-09-10，failed=[]）。
6. **GitHub 同步事故與新診斷工具**：5 檔推送，4 檔一次 byte-exact；Home.tsx（95,831 bytes）首推甩咗 19 bytes——轉錄時將 RebalanceLog 嘅 `{c.from}%` 同行 `→` 兩個 span 併做一行（吞咗 `\n`+18 spaces）。診斷用新招 **blob-sha 暴力法證**：單行刪/複/改/換序全部唔啱後，改試「連續 k bytes 刪除」——每個 offset 計 `blob_sha(data[:i]+data[i+k:])`（95K offsets × sha1 ≈ 7 秒），一擊即中 offset 62073；重推後 blob `ec4f760f` 與本地逐字節一致（修復 commit 3c294041；其餘 blob：contracts/screener.ts `2afac0a8`、api/screener.ts `fb2f1260`、api/router.ts `d10c0f6a`、src/lib/screener.test.ts `0c803241`）。**教訓（§10.25）：大檔案重推必核對返回 blob sha；唔啱就用連續刪除掃描機械定位**——96KB 入面甩 19 bytes，肉眼同逐行對照都必漏，sha 掃描先係確定性方法。

## 2026-09-11 Phase 12：信號回測多窗口階梯 + ACWI 超額命中口徑（signalBacktest 升級）
1. **源起**：用戶質疑「15 個交易日會唔會太少」——開放分析結論：方法論上用戶啱（horizon 錯配、短窗噪音主導、無基準調整嘅「免費順風」問題），但觀點庫 2026-07-15 先開始，單一長窗會令成張卡空白（45 日窗 0/71 可判定）。解法係**多窗口階梯**：四個窗口並行，短窗即時有數、長窗陸續成熟，唔使喺「快」同「準」之間二選一。
2. **架構**：`contracts/backtest.ts` 純函數層（前後端共用、可單測）——`BT_WINDOWS=[5,15,45,90]`、`scoreHit`（超額邊界：bull >+0.5pp / bear <−0.5pp / neutral |x|≤2pp）、`windowRetPct`（日期對齊：非交易日順延下一交易日）、`evalWindows`（每信號四窗 cell 或 null=未到期）、`aggregateWindow`（hitRate + 方向信號平均**簽名**超額——bear 取反——decided<10 標不足）、`aggregateExpert`（15 日主窗，decided<3 標不足）；`api/pipeline.ts` `signalBacktest()` 重寫：pool(3) 一次拉全部信號 ticker + ACWI 六個月日線，逐信號 `evalWindows`，回傳 `{asOf, windows, rows(cells), byWindow, byExpert}`；Home.tsx 卡片重寫：四窗格仔（未到期窗如實顯示「觀點庫最舊信號仲未夠 X 個交易日」）+ 點樣讀（edge 持續性邏輯）+ byExpert chips（hover 顯示簽名超額）+ 表格四窗列（hover 顯示超額 pp）+ 誠實邊界註腳（n≈35 → 95% CI ±16pp）。
3. **口徑改動嘅實質影響**（2026-09-11 E2E 實測）：舊口徑（絕對收益 ±1%/±3%）喺 2026 年 7-9 月升市入面係「免費順風」——升市咩都中；新口徑（ACWI 超額）即刻現形：5 日窗 hitRate 34.6%（52 條）、15 日窗 30.4%（23 條）、方向信號平均簽名超額 −0.85pp/−1.39pp——觀點庫整體**跑輸**大市，呢個先係誠實嘅鏡。45/90 日窗 0 條到期，卡片如實留空。
4. **教訓（§10.26）**：**單一固定窗唔等於驗證——多窗口階梯 + 基準調整先係誠實口徑**。信號驗證有兩個隱藏偏差：①窗口太短 → 噪音當實力；②無基準 → 牛市順風當命中（free-rider 問題）。解法唔係揀一個「啱」嘅窗，而係全部窗一齊睇——edge 持續性（命中率隨窗長企穩）先係證據；命中判定一律改用超額（對 ACWI），方向信號額外睇簽名平均超額（長期 >0 先有淨價值）。未到期必須留空——寧願卡片講「仲未夠日子」，唔好攞未成熟嘅窗充數。
5. **閘門**：tsc clean；vitest 47/47（新增 `src/lib/backtest.test.ts` 15 個 case）；build OK；E2E（dev server 實拉 Yahoo 日線 30.5s）：windows=[5,15,45,90]、45/90 日窗 decided=0 pending=59 如實留空、byExpert 聚合正常、row cells 結構 `{retPct, excessPct, hit}|null` 正確。

## 2026-09-11 Phase 13：全站深度 review 修復（對標成熟專家觀點平台）
1. **源起**：業主要求全站公開性思考 review，對標 TipRanks 等成熟專家觀點分析網站，四大領域逐個過：① 顯示層 ② 專家影片分析 ③ 專家文章語義分析 ④ 觀點→量化→組合分配管道。「有優化機會就優化掉，有錯誤就修改掉」。雙 coder 分域實施 + 四重閘門。
2. **P0 結構修復**（api/pipeline.ts）：
   - **模型日落（§10.27）**：kimi-k2.5 + moonshot-v1 全系列 2026-08-31 退役，舊回退鏈（§10.2 嗰條）全滅 → `KIMI_MODEL_CANDIDATES=[KIMI_MODEL, kimi-k2.6, kimi-k3]` + `resolveKimiModel()` 共享 resolver（module-level 緩存可用者；全失敗響亮報警 + return null 優雅降級）。kimiWebSearch、netCheck 探針、OCR（`OCR_MODELS=["kimi-k3"]`——唯一 vision-capable 模型）全部統一經佢，唔准再各自硬編碼模型名。
   - **signalBacktest 結構性 0（§10.28）**：舊版齋讀最新一份快照計回測——觀點庫 07-15 先開始，45/90 交易日窗**永遠** 0 條到期（快照日日新，歷史信號喺最新快照入面永遠「唔夠老」）。改為掃最近 120 份快照（`BT_SNAPSHOT_SCAN=120`，snapshots 表本來就 append-only，零 schema 改動）、view 級 `url|title` + signal 級 `url|title|asset|direction` 去重、per-mapped-ticker 逐 ticker 出 job（修 mapAsset[0] 齋做第一隻嘅分裂 bug）、回應加 `acwiMissing` 旗標。配套：carry TTL 60→**120 日**（90 交易日 ≈ 180 曆日要先有機會成熟，60 日 TTL 會殺晒長窗樣本）+ carry 保留原 `view.horizon` 計衰減 + `carried: true` 標記；contracts/types.ts SnapshotView 加 `horizon?` 同 `carried?`（additive）。
3. **P1 管道加固**（api/pipeline.ts）：`clampFutureDate`（來源日期 >今日+1日 → 夾返今日 + 響亮記錄；carry 同樣唔准未來日期）、`normalizeHorizon` 白名單（macro/theme/event，其餘一律歸 theme——LLM/外部輸入唔可信）、`matchExpertName`（exact → 雙向 includes → 複合名按 `/、,，(（` 切開逐段試——修「洪灝/林本利等(etnet专访)」永遠 find-first 落喺洪灝）、YouTube API 非 2xx 記 status+頻道（唔准 silent return null）、**增量發現**（上一快照已知 videoId 跳過 LLM 結構化，每日慳 ~20 calls；舊片由 carry 原樣併入唔會丟）、ASSET_MAP 繁體 alias 逐條補齊（半導體/記憶體/資料中心/滬深/恆指/醫療等——本港專家字幕多為繁體，舊表大量 miss）。
4. **P1 算法修復**（api/algo.ts）：`applyS6Boost` 抽出純函數——z<−2 且 trend≥0 觸發，且**只有正 raw 先准 ×1.2**（負 raw 放大會變加強睇淡信號，邏輯反轉）；K8 容量截斷改 **protect-reduce-first**——減倉/止盈屬風控動作永遠先保留，齋截多餘 add（按 fusedScore 降序保留強信號）；舊版齋按 fusedScore 排序會先犧牲 reduce（減倉 fused ≤40 必然排尾），風控動作被成本邏輯吃掉係本末倒置。
5. **前端修復**：consensus.ts——強度歸一化 **/3 → /5**（管道/algo 強度量表係 1-5，舊版 /3 令 5 級強信號權重虛高 67%）、`LiveSignalView.decayWeight?` 直通（後端分級半衰期 7/21/45 日口径；冇先 fallback 固定 21 日自己折）、債券 regex 由 /息/ 收窄為 /债券|长债|国债|债息|减息|降息|加息|利率/（舊版「高息股/派息/股息」全部誤歸債券主題）、美股 regex 剔「非美」（「非美資產」係睇淡美元/轉投非美市場，唔係美股信號）、新增「医疗 / 医药」主題 + THEME_MAP /医疗|医药|创新药|health/ + THEME_ACTIONS XLV 條目（XLV 信號此前無處歸類、無處展示）；useLiveData.ts——`onWindowRefocus`（focus+visibilitychange 監聽）+ useQuotes/useAlgo `refetchOnWindowFocus: true`（頁面長開數據隔夜變舊，返回分頁即自動重拉）；portfolio.ts——REBALANCES 調倉#1 補 `{TLT 4→3}`（§10.29）。
6. **教訓**：**§10.27 模型日落會再發生**——§10.2 嘅回退鏈本身都會過期（kimi-k2.5/moonshot-v1 全系列 2026-08-31 退役）；做法：共享 resolver + 全通道（含 OCR、netCheck 探針）統一經佢 + 候選鏈定期核對平台公告，任何新 LLM 調用唔准硬編碼模型名。**§10.28 回測窗會結構性永不成熟**——快照 append-only 但回測齋睇最新一份，歷史信號永遠唔會「變老」；長窗驗證必須掃 N 份歷史快照 + 去重，carry TTL ≥ 最長窗嘅日曆日（90 交易日 ≈ 180 曆日 → TTL 120 日仍偏緊， roadmap 考慮再延）。**§10.29 調倉鏈要同現行權重 replay 對賬**——REBALANCES 調倉#1 遺漏 TLT 4→3 一條，replay 出 TLT=4、Σ=101，同 CURRENT_WEIGHTS（TLT=3、Σ=100）矛盾咗成個月冇人發現；做法：`portfolio.test.ts` 鎖死三個不變量——鏈條連續（每條 from == 上一步 replay 值）、replay 終態 ≡ ETF_PORTFOLIO 權重、Σ=100。**§10.30 pkill -f 會自殺 + 非持久 shell 後台進程唔可靠**——命令行含 "vite" 嘅 shell 會俾 `pkill -f vite` SIGTERM 埋自己（exit -15）；nohup 起嘅 server 喺 shell tool calls 之間唔保證存活 → server + 全部 E2E curl 要喺**同一條鏈式命令**入面跑完，跨 call 嘅「先起 server 下個 call 先測」係靠唔住嘅。
7. **閘門**：tsc 0 錯；vitest **86/86**（7 檔——新增 pipelineGuards.test.ts 33 條：clampFutureDate 4 / normalizeHorizon 7 / mapAsset 繁體 21 / matchExpertName 4 / applyS6Boost 3；portfolio.test.ts 3 條 replay 不變量；backtest.test.ts +3 條 ±0.5 嚴格邊界；其餘原有）；build OK；E2E（production server `node dist/boot.js` 單命令鏈式）：登錄閘門 200/401、**signalBacktest 45 日窗 decided=3 史上首次非零**（5d 55 decided / hitRate 34.55%、15d 26 / 30.77%、90d 0 / 62 pending 如實留空）、algo.analyze / quotes.live / pipeline.snapshot 全 200、快照 57 條觀點 decayWeight 直通確認。本地 commit `7678e30`（11 檔 +561/−118）；GitHub 5 批推送全部 blob sha 逐字節驗證通過（`7b1e4698` 批1：vitest.config+types+2 新測試檔；`5ec38e3f` 批2：backtest.test+consensus+useLiveData；`6b660c9b` 批3：portfolio+algo；`42827d3b` 批4：pipeline；`6f3989c7` 批5：Home.tsx）。**遺留 roadmap**：consensus.ts `matchExpert` 仍係舊式雙向 includes（未改用管道 matchExpertName 嘅複合名切分）；45/90 日窗要歷史累積先陸續成熟；kimi-k3 vision OCR 未經真機驗證；Home.tsx 105KB 拆分維持 roadmap；Moonshot 充值仍係 P0（修復後鏈條落喺 kimi-k2.6 ≈ HK$16/月）。

## 2026-09-11 Phase 13.1：Moonshot 國際站 Key 接入 + netCheck 探針硬編碼修復
1. **源起**：用戶開新 API key（名「etf-expert-management」）恢復 LLM 主動脈。實測發現：新 key 喺 `api.moonshot.cn` 返回 401 Invalid Authentication、喺 `api.moonshot.ai` 返回 200 OK——**Moonshot 國內站（.cn）同國際站（.ai）係兩套獨立帳號體系，key 互不通用**。呢張 key 係國際站開嘅。.env 更新：`KIMI_API_KEY` 換新 + `KIMI_BASE_URL=https://api.moonshot.ai/v1`。
2. **順藤摸到嘅 bug**：換好 key 後 netCheck 依然紅燈「Key 無效（401）」——查實 `resolveKimiModel()` 用 KIMI_BASE（.ai）已經成功，但 netCheck 嘅二次探針（pipeline.ts 行 1226）**寫死咗 .cn URL**，同一函數入面兩條路徑兩個答案。修復：探針統一改 `${KIMI_BASE}/chat/completions`。grep 全源碼確認其餘調用（resolveKimiModel / kimiWebSearch / structureWithKimi / OCR）全部行 KIMI_BASE，冇第二個硬編碼。
3. **教訓（§10.31）**：**同一服務嘅所有調用點（含健康檢查探針）必須共用同一個 base URL 變量**——探針同業務行唔同嘅路，就會出現「業務通、狀態燈紅」嘅誤導，同 §10.14 嘅「依賴可用≠帳戶可用」係同一族問題。**另：攞到新 Moonshot key 第一件事係兩站各 probe 一次定位歸屬**——key 唔通用，401 唔一定係 key 錯，可能係站錯。.env.example 已補齊全部環境變量並註明兩站分別（舊版只得 4 行，連 KIMI_API_KEY 都冇，接手者會迷失）。
4. **閘門**：tsc 0 錯；vitest 86/86；build OK；E2E（production server）：netCheck `moonshot: true（kimi-k2.6）` 由紅轉綠，kimi-k3 獨立 probe 200（OCR 通道同步恢復）；login gate 200。**效果**：聽日 HKT 08:00 調度器嘅全自動管道（YouTube 字幕→Kimi 結構化→建議引擎）正式恢復，唔再只靠 Agent 掃描通道。

## 2026-09-11 Phase 13.2：充值 US$25 全鏈路實戰測試——reasoning 模型（k2.6/k3）四大兼容修復 + 耗費分析
1. **源起**：用戶充值 Moonshot US$25（cash $20 + voucher $5，先扣 voucher），要求全面實戰測試所有 Kimi 通道兼分析耗費。測試基線餘額 $24.999890。
2. **逐通道實測發現四大 reasoning 模型兼容問題（全部已修）**：
   - **temperature 封殺**：kimi-k2.6 / kimi-k3 係 reasoning 模型，`temperature` 只接受 1（或不設，默認 1）——設 0.3/0.2/0 全部 400「invalid temperature: only 1 is allowed」。修復：kimiWebSearch（原 0.3）、structureWithKimi（原 0.2）、vision OCR（原 0）三個調用點全部移除 temperature 欄。
   - **reasoning tokens 食 max_tokens 配額**：max_tokens=10 實測 → 9 tokens 思考 → 空輸出；OCR max_tokens=1000 → 997 reasoning → 空輸出。修復：kimiWebSearch max_tokens 2000→6000；OCR 唔設 max_tokens（實測 2,864 tokens 正常完成轉錄）。
   - **$web_search 新協議**：k2.6 時代 R1 返回嘅 tool_call `function.arguments` **已包含服務端執行完嘅搜索結果**（`{"search_result":{"search_id":"..."}}`）——客戶端 R2 回傳嘅 tool message content 必須係 arguments 本身；舊代碼回傳空字串 → 模型 R2 收唔到搜索結果 → 保守輸出 `{"items":[]}`。修復：content 改為 `t.function?.arguments ?? ""`。
   - **timeout 誤殺**：reasoning 模型處理長文實測 40-90s，structureWithKimi 舊 timeout 60s 會誤殺（洪灝新聞結構化實例）；kimiWebSearch R2 實測可超 90s。修復：structureWithKimi 60s→120s；kimiWebSearch 90s→150s。
3. **兩次完整管道實跑（受限網絡：YouTube/Brave 跳過）**：第一次（修復前）status success——Wind 8 專家 7 條命中（洪灝 2 條結構化 timeout 降級標題入庫）、主題掃描 0 條、carry 53 條、共 60 觀點 4 建議。第二次（帶全部修復）status success——Wind 同樣 7 條命中、**洪灝 2 條結構化成功**（120s timeout 生效）、林本利 1 條仍 timeout（降級標題入庫，寧缺毋濫）、主題掃描仍 0 條、carry 60 條、共 60 觀點 2 建議、剎車 ok。
4. **主題掃描 0 條根因（唔係 bug）**：直接 API 對照實驗證實——協議修復後搜索結果確有送達模型，但 Moonshot web_search 索引返回嘅文章日期偏舊（2026 年初/年中），模型按 45 日窗（LOOKBACK_DAYS）**誠實篩走全部舊文** → `{"items":[]}`。呢個係「寧缺毋濫」設計正確運作。另觀察到模型有時想第二輪搜索但管道 R2 封頂會截斷。**Roadmap**：主題掃描放寬至 90 日窗 / 支持多輪 tool_call loop（上限 3-4 輪）/ 或評估停用（價值=媒體匯總級次要補位，專家通道先係主力）。
5. **耗費分析（2026-09-11 實測）**：總耗費 **$0.84483 ≈ HK$6.59**（$24.999890 → $24.155060），**全部扣 voucher**（$5.00 → $4.155），cash $20 未郁。拆分：直接 API 逐通道測試 + 第一次管道 = $0.32624；第二次管道 + 診斷實驗 = $0.51859。**推算**：每日管道單次約 $0.3-0.5（主力=8 專家結構化長文 + 7 主題搜索，reasoning tokens 佔比高）→ 月均 $9-15（≈ HK$70-117）→ **$25 約可支撐 50-80 日每日全自動運行**。注意 voucher 用罄後先扣 cash。
6. **教訓（§10.32）**：**換模型代際（k2 → k2.6/k3 reasoning 模型）必須全鏈路真實業務調用驗證**——resolver ping 通唔代表業務通：temperature 取值範圍、max_tokens 被 reasoning 分薄、內置工具回傳協議、業務 timeout 四樣都會靜靜哋變。netCheck 綠燈只證明「key 有效 + 模型存在」，唔證明「業務參數兼容」。另：**新 key/新站遷移後第一次實跑要逐項對照預期產出**（今次主題掃描 0 條表面似模型保守，實際藏咗協議錯——唔對照就會漏）。

## 2026-09-12 Phase 13.3：預覽 iframe 登入死循環修復（SameSite 第三方 cookie）
1. **症狀**：用戶喺平台預覽版本入唔到站——密碼啱但都彈返密碼頁。本地 production 模式以正確密碼登入完全正常。
2. **根因**：平台預覽係 iframe 嵌入（跨站上下文），`SameSite=Lax` 嘅 cookie 被瀏覽器當第三方 cookie 擋埋——POST 登入其實成功，但 cookie 存唔到 → 之後每個請求都冇凭证 → 永遠返密碼牆。
3. **修復**（api/gate.ts）：https 環境（`x-forwarded-proto: https`）cookie 改 `SameSite=None + Secure`（Chrome 硬性要求成對出現）；本地 http 維持 `Lax` 唔加 Secure（否則 http 下一樣存唔到）。logout 同步。本地兩條路徑都實測通過。
4. **教訓（§10.33）**：**本地通過 ≠ iframe 預覽通過**——凡係 cookie/儲存類認證，必須考慮嵌入上下文嘅第三方 cookie 政策；https 部署要用 `SameSite=None; Secure`。另：推送驗證時發現 emoji/特殊字符「→」同嵌套類型簽名 `) => unknown) => unknown` 易喺傳輸層走樣——凡 byte-exact 推送後 sha 唔夾，第一反應係搵呢類字符。

## 2026-09-12 Phase 14：全站功能實可用性深度排查 + 觀點重複入庫根因修復 + Docker secrets 封堵
1. **源起**：業主要求「仔細分析網站更新後是否實際可用、所有功能跑通、排查所有 code」。五階段排查：A 靜態閘門 / B API E2E / C 瀏覽器 9 tab 逐個驗證 / D 唯讀代碼審計（explore 子代理全倉 grep + 逐檔精讀）/ E 修復整合。
2. **排查結論（修復前）**：9 tab 全接駁無 phantom endpoint、12 按掣全有 handler、前端 bundle 零 secret（grep `sk-`/ACCESS_CODE 全 0 命中）、snapshot/performance 契約字段完全對齊、門禁 crypto（HMAC + timingSafeEqual + httpOnly + 限流 10 次/10 分鐘/IP）設計合格。但有三個真問題：
   - 🔴 **觀點重複入庫（Stage C 肉眼發現，最嚴重）**：專家觀點庫洪灝「中国AI行情进入第二阶段」出現 4 次、「周末写了一个chatbot」3 次。根因：Wind 新聞 URL 帶隨機防緩存參數 `useless=0.xxx`（每次抓取唔同），而 carry 去重 key 係 raw `url|title`（pipeline.ts 原 L639）→ 去重形同虛設 → 每輪管道同一篇當新觀點 + 舊版被 carry，**重複線性增長**，重複觀點重複計入共識分/建議/回測，仲霸佔 60 條 cap 擠走真觀點。
   - 🔴 **`.dockerignore` 冇排除 `.env`**（Stage D 審計發現）：Dockerfile `COPY . .` 會將 `.env`（KIMI_API_KEY、DATABASE_URL 含 DB 密碼、YOUTUBE/BRAVE/NEWS key、APP_SECRET、ACCESS_CODE）焗入 Docker image layer——任何拉到 image 嘅人 `docker run … cat .env` 攞齊全套 secrets。
   - 🟡 三處靜默 `catch {}`（carry 讀取失敗、snapshot/performance 鏡像檔寫入失敗）違反項目自身「唔准靜默失效」原則；`KIMI_BASE_URL` fallback 預設 .cn 站同現行 .ai key 唔匹配（漏設會靜默 401）；`_probe*.mjs`/`_vision_test.mjs`/`db/seed.ts`/`dist/data/` 舊殘留。
3. **修復（全部完成）**：
   - **去重 key 正規化**：新增 `dedupeKey(v) = 專家|正規化標題|日期` 三件套（與 URL 參數完全無關）；應用於四處——carry 去重、60 條 cap 前 in-place 全局去重第二道防線（新抓優先，剔除即 say() 記錄）、signalBacktest 觀點聚合 key、信號級 skey。
   - **現有快照清理**：`scripts/dedupe-snapshot.ts`（一次性，可重跑）——讀最新快照去重 → 重跑 `buildSuggestions`（純函數，export 咗）→ **append 新 row（kind: "dedupe"，保持 snapshots 表 append-only，唔郁歷史）** → 重寫兩份鏡像。結果：**60 → 26 條觀點（剔除 34 條重複，重複率 57%）**；建議由 2 項（XLE 6→7、VOO 12→13）重算為 **0 項**——證實之前兩項建議部分係重複觀點虛增共識分嘅產物；被擠出 cap 嘅真觀點（如洪灝「链上股票」7/31）重新浮現。
   - **`.dockerignore`** 加 `.env`/`.env.*`（保留 `!.env.example`）+ `_probe*.mjs`/`_vision_test.mjs`/交接文檔。
   - **6 處鏡像檔寫入 catch** 加 `console.warn`（指明邊個 dir、後果係「靜態鏡像將陳舊/淨值將停止更新」）；carry 讀取失敗 catch 加 `say()`（歷史觀點唔見必須響亮記錄）。
   - **KIMI_BASE_URL 未設時開機 console.warn** 提醒兩站 key 唔通用。
   - 刪 `_probe*.mjs`×5、`_vision_test.mjs`、`db/seed.ts`（drizzle.config/package.json 零引用）、`dist/data/`（舊 build 殘留嘅矛盾快照）、空目錄 `src/sections`/`src/types`。
4. **教訓（§10.34）**：**去重 key 永遠唔好依賴第三方 URL 嘅原始形態**——新聞/分享鏈接興帶隨機防緩存參數（Wind `useless=`、utm_*、fbclid 等），同一內容每次 URL 都唔同。穩定 identity 要從內容本身抽（專家+標題+日期），URL 只係佐證。呢類 bug 最陰濕之處：每輪只多一兩條，唔爆炸性增長，肉眼好難察覺，但共識分會被靜靜哋扭曲——**真金白銀用途嘅系統，數據完整性 bug 等同功能 bug**。另：**vite dev server 同 production build 係兩條命**（今次 Stage C 後段先發現 port 3000 一直係 vite dev）——驗收必須喺 `node dist/boot.js` production 模式重跑一次。
5. **閘門（修復後全綠）**：tsc 0 錯；vitest **86/86**；build OK（dist/boot.js 2.3mb）；production server E2E——login 200、snapshot 26 條觀點/suggested 0/brake ok、signalBacktest 50 rows（去重後乾淨版）、netCheck moonshot(kimi-k2.6)✅/agentGw✅/kome✅；瀏覽器 9/9 tab production build 全渲染（觀點庫每條觀點僅一份）。dist 雙 bundle grep `sk-`/ACCESS_CODE 零命中。
6. **遺留 roadmap（唔阻使用）**：ACCESS_CODE 現值係 4 位數字弱密碼（值見本地 .env，唔入文檔）（限流擋腳本小子，擋唔住定向窮舉——建議改 ≥12 位隨機串，但係用戶指定嘅密碼，等佢決定）；`.env` 曾隨交付物流轉建議 rotate 全部 key；55 個未引用 shadcn ui 組件 + ~30 條 radix 依賴（唔入 bundle，純 repo 體積）；主題掃描 90 日窗/多輪 loop（§10.32 尾）；45/90 日窗待歷史累積成熟。

## 2026-09-25 Phase 15：調倉閉環——「批核後 chart 無標記」根因修復 + 淨值凍結根治 + 記錄調倉功能
1. **源起（業主原話）**：「为什么我批核了之后，调整了持仓，但是 chart 没有同步？没有显示一个点去代表调整了？我要你确定所有功能都是真实能跑的，然后给我一个最终的网页版…这个网站是需要每次按进去自动更新的。」
2. **診斷（三個根因，全部屬設計缺口唔係小 bug）**：
   - 🔴 **圖表黃點係第二份寫死數組**：`REBALANCE_MARKS`（3 條：03-16/06-15/07-20）同 `REBALANCES` 分開人手維護——第 4 次調倉無論點都唔會出現喺圖上，除非有人記得郁兩份檔。
   - 🔴 **系統根本冇「記錄調倉」呢個動作**：「批核」(acknowledge) 只設 `acknowledged=true` 關橫幅提醒；按鐵律建議永不自動執行、唔會郁權重——所以「批核＋調倉」之後系統乜都唔知，圖表自然唔會有點。
   - 🔴 **淨值凍結喺 09-11 無人知**：本地 sandbox server 冇跑（得 workspace 醒先存在）；`updatePerformance` 逐 ticker `catch {}` 靜默——ACWI 行情失敗 → 冇新日期 → 檔案照寫（mtime 郁咗似有生機，asOf 其實無推進）；兼且 `updatePerformance` 掛喺主管道大 try 尾段，前半段任何 throw 都會跳過淨值追加。
3. **修復（調倉閉環，全部完成）**：
   - **`contracts/rebalance.ts`（新，純函數層，前後端共用）**：`applyRebalances`（靜態基準 2026-07-20 調倉#3 + runtime 記錄按日期 replay）、`weightsForDate`（淨值分段——**約定：調倉日收市執行，新權重對「嚴格晚於執行日」嘅日期生效**）、`validateRebalance`（YYYY-MM-DD + 嚴格日子校驗【JS Date 會將 02-31 進位成 3 月，必須 round-trip 對返】+ 唔准未來【以 HKT 計今日】+ 同日唔准重複 + ticker 白名單 19 隻 + to∈[0,40] + to≠現行 + **調後 Σ 必須=100**）、`rebalanceMark`（圖表黃點由記錄衍生）、`nextRebalanceTitle`（自動編號 #4 起）。
   - **`api/pipeline.ts`**：`listRuntimeRebalances`/`effectiveWeights`/`effectiveLastRebalanceDate`/`writeJsonBothDirs`；`recordRebalance`（校驗→寫 `public/data/rebalances.json` 雙目錄→DB `snapshots` kind="rebalance" 審計行【DB 失敗唔阻檔案】→`performance.json.weightsTimeline` 加分段→即場 `updatePerformance()`→按新權重重跑建議引擎【已執行建議唔再掛】→快照 acknowledged=true；**`dryRun=true` 只校驗+預覽乜都唔寫**——E2E/前端預檢用）；`updatePerformance` 改分段權重（舊檔無 timeline → fallback 基準 entry）+ **ACWI 缺失 `console.warn`**（唔再靜默）+ **失敗 catch 加 `try{ await updatePerformance() }catch{}` 解耦**（管道前半段失敗都照舊追加淨值）；`buildSuggestions` 改用生效權重（基準同「from」即時跟上新調倉）；`lastRebalanceDate` ×4 全部動態化。
   - **`api/router.ts`**：`pipeline.rebalances` query + `pipeline.recordRebalance` mutation（zod：date regex、title/trigger/note 長度上限、changes `{etf,to}[]` min(1).max(25)、dryRun）。
   - **`src/hooks/useLiveData.ts`**：`useRebalances`（`/data/rebalances.json` cache-bust + refocus 重拉 + reload tick 提交後即時刷新；檔案格式 `{records:[...]}` 兼容 bare array）；`useEffectivePortfolio`（weight 按記錄 replay 覆寫、delta 顯示最新一次記錄嘅變動、`lastRebalanceDate` 動態）。
   - **`src/pages/Home.tsx`**：圖表黃點 = `REBALANCE_MARKS`（靜態歷史）+ `records.map(rebalanceMark)`（runtime 自動衍生）；**`RecordRebalance` 組件**（日期 default 今日/max 今日、待复核建議一鍵預填、逐行 from→to 即時預覽 + pp 變動、調後 Σ 紅綠指示、備註欄、警告文案「此動作只記錄你已在券商執行嘅真實調倉——系統永遠唔會幫你落單」）放每日更新建議卡下 + 调仓记录頁頂；`RebalanceLog` 合併 runtime 記錄（按日期倒序）+「即時記錄 ✓」badge + 記錄時間戳 + 動態註腳；總覽餅圖/配置詳情表/LiveStrip 今日估算/Excel 導出全部改用生效權重；「截至 2026-07-20」等寫死文案全部動態化。
4. **閘門（全綠）**：tsc 0 錯；vitest **107/107**（新增 `src/lib/rebalance.test.ts` 21 條：replay 順序/冚寫、分段權重前/當日/翌日邊界、校驗 10 個拒絕分支、標記衍生、自動編號）；build OK；**production server E2E**——login 200、`rebalances` 返回 []、dryRun 合法例 ok:true（自動 title「调仓 #4」、from 自動帶現行權重、effective 預覽正確）、三個拒絕例（Σ≠100「調整後總權重 = 101.00%」/未來日/未知 ticker）全部命中且**零檔案污染**（dryRun 前後雙目錄 rebalances.json 維持空）、`/data/*` 靜態檔門禁行為一致（無 cookie→access required，帶 cookie→200）、`quotes.live` 21 ticker 全中零失敗、**手動觸發 `updatePerformance()`：asOf 09-11 → 09-24（補回 9 個交易日），weightsTimeline 建立，最新淨值 組合 111.7 / 基準 106.81**；瀏覽器實測總覽（圖表標題「已追踪至 09-24」+ 三黃點 + 統計即時重算 +11.58%）/每日更新/调仓记录（記錄表單 + 19 隻下拉 + Σ 指示）全渲染。**意外實測兩個可靠性機制**：boot 偵測快照 68.3h 陳舊自動補跑 ✅；強殺進程後重啟，殭屍 running 行自動標 failed（「进程重启：遗留 running 记录标记为 failed（僵尸恢复）」）✅。
5. **教訓（§10.35）**：**派生視圖永遠唔准維護第二份寫死副本**——圖表標記、生效權重、lastRebalanceDate 全部要由 single source of truth（調倉記錄）即時衍生；凡係「兩份檔人手同步」嘅設計，遲早有一份唔記得郁（今次業主真金白銀調咗倉，圖表就係咁樣唔見咗個點）。**「批核≠執行」必須喺 UI 講到明**——用戶以為批核會觸發系統跟進，實際 acknowledge 只係關提醒；涉及真金白銀嘅語義，寧願囉唆都唔好俾人誤會。**靜默 catch 係呢個項目嘅反模式**（黃金 −25% 教訓嘅同族）：今次一次過補咗 ACWI warn、失敗解耦、寫檔 warn 三處。
6. **業主操作指引（記錄調倉）**：喺券商真實執行調倉 → 網站「每日更新」或「调仓记录」頁 → 「记录调仓」卡 → 揀日期（預設今日，唔准未來）→ 逐行揀 ETF + 輸入新權重（可用「用待复核建议预填」）→ 調後總和必須 =100%（紅綠即時顯示）→ 「📝 記錄此調倉」→ 總覽圖即日出黃點（如下一交易日淨值追加後）、配置表/餅圖/Excel 即時更新、建議引擎按新權重重算。**系統永遠唔會幫你落單——呢個動作只係記錄。**
7. **安全備註**：Phase 15 早段發現 HANDOVER.md 早前誤將 ACCESS_CODE 明文寫入兩處——已脫敏重推（commit 91fc0673）並重建交接 zip（grep 0 命中）；但 **git 歷史舊 commit 仍含明文**（MCP 通道無法改寫歷史），已建議業主更換密碼（順手升級做 ≥12 位隨機串，一舉兩得）。

## Phase 16（2026-09-26）：發布後五項修復 + DB 持久化層（ephemeral 容器根修）

### 根因總結
1. kimi.pro 容器文件系統 ephemeral：runtime 寫入嘅 `public/data/*.json` 容器回收後還原返 image 烘入時刻——「檔案做 serve 來源」嘅舊設計喺發布環境全部失效（觀點/淨值/調倉記錄「唔更新」嘅共同根因）。
2. 「提交失敗：The string did not match the expected pattern」= Safari/WebKit 對非 JSON 回應（平台代理逾時回 HTML/空）嘅通用 SyntaxError——同步 `addManualView` 等 Kimi 結構化 40-90 秒，超過代理逾時。
3. 批核（acknowledge）≠ 記錄調倉（recordRebalance）——舊 UX 引導不足，用戶以為批核後 chart 會加點。
4. `snapshots.payload` text 上限 65,535 bytes 潛伏炸彈（views 上限 60 時約 70KB 會超限）。

### 修復清單
- **手動錄入 async job 化**：`submitManualView`（同步校驗即拒 + 回 jobId 背景跑）+ `manualViewJob` 輪詢；`dryRun` 全路徑預覽零寫入；舊 `addManualView` 保留兼容。前端失敗時唔清表單內容。
- **URL 正規化**：`canonicalVideoUrl`（youtu.be+si 追蹤參數/尾 `?`/shorts 等形態 → `watch?v=`）；入庫去重升級做 videoId / canonical URL / 標題三重比對（舊字串全等會被短鏈繞過，同一條片可重複入庫放大信號——真 bug 已修）。
- **淨值定時器**：boot+150s 起每 30 分鐘 `updatePerformance()`（獨立 in-flight 鎖、失敗只 warn）——休市無新交易日數據時自然唔加點。
- **boot 補跑門檻收緊**：快照缺失 OR（快照日期 ≠ 今日 HKT AND 齡 >6h）OR 齡 >20h → 補跑一次。
- **頻道訂閱擴充**：新增 @Invest4good（Invest for Good 長知識）同 UCcAkhVZQVpqNtT9fUdkAJBQ（大師說 The Master Said）兩個多專家訪談頻道；`EXPERT_TITLE_MATCH`（8 位追蹤專家繁簡 regex）按標題匹配歸屬，唔中跳過；RSS 兜底（`feeds/videos.xml`，免 API key）+ handle→channelId 頻道頁 HTML 解析——YT Data API 無 key/唔可達時照樣同步。
- **DB 持久化層**（核心）：`latestSnapshot` 加 kind 白名單（daily/manual/rebalance/dedupe）+ views 校驗（修「審計行誤當快照」潛伏 bug）；調倉審計行 kind='rebalance_audit'，`listRuntimeRebalances` DB 優先、檔案 fallback；`updatePerformance` 寫 DB kind='performance'（內容唔變 skip，防定時器刷行數），新增 `latestPerformance()` + `pipeline.performance` 端點；所有 raw snapshots 查詢加 kind 過濾（algo.ts、recentSuggestions、carry 鏈、getStatus、acknowledgeLatest、doAddManualView、batchImportVideos、addStructuredView、signalBacktest、dedupe 腳本）。
- **payload text→mediumtext**：schema 更新 + boot idempotent `ALTER TABLE snapshots MODIFY payload MEDIUMTEXT NOT NULL`（warn-only，唔用 drizzle-kit push）。
- **boot 檔案鏡像同步** `syncFileMirrorsFromDb`：DB 較新先覆寫檔案（唔會用空覆蓋種子）——zip/本地靜態鏡像唔會長期陳舊；發布容器 ephemeral 無所謂，前端全面讀 API。
- **前端 hooks 轉源**：`usePerformance`/`useFileSnapshot`/`useRebalances` 改 tRPC/DB（react-query `refetchOnWindowFocus`+`staleTime` 30s），BUNDLED 打包快照做離線兜底，call site 零改動；Safari 通用錯誤訊息翻譯成人話；URL input onBlur 正規化；批核成功後琥珀色 banner 引導「📝 去記錄調倉」（`#record-rebalance` smooth scroll）。

### 驗證
- tsc 0 錯；vitest 138/138（10 檔）；build OK。
- production E2E：submitManualView 同步校驗即拒；dryRun job 全路徑（Kimi 結構化+去重拒絕重複片）零檔案污染（md5 前後一致）；recordRebalance dryRun Σ≠100 拒絕（DB 校驗鏈）；performance/rebalances/snapshot 三端點 DB 讀取正確；boot MEDIUMTEXT 遷移 + 檔案鏡像同步實測命中；淨值定時器實測追加（asOf 09-24→09-25）。
- 用戶 09-25「失敗」嘅手動錄入其實已入 DB（蔡金強《金发女郎到三高重临》）——mirror sync 後 34 條觀點全可見。

### 環境備注
- 本地開發同發布站共用同一遠端 MySQL——DB 係跨環境唯一真相。
- 容器 ephemeral 依舊：檔案只係 build-time 種子/本地鏡像。

## Phase 18（2026-09-26）：發布站行情根修 + 批核即自動記錄調倉

### 根因總結
1. 發布站「行情源暫時不可用」+ 淨值唔更新嘅共同根因：kimi.pro 出口只放行李 Kimi 系域名（googleapis/youtube/brave 全封），行情唯一路徑係 agent-gw 網關；但容器 `.env` 冇 `AGENT_GW_API_KEY`（憑證舊版只放本地 `~/.kimi/agent-gw.json`），`netCheck` 嘅 agentGw 只係 TCP 探測唔包鉴权 → 21 隻 quotes 全fail、`updatePerformance` 每日追加全fail。
2. 用戶工作流確認：「批核 → 自動調倉 → 自動出現喺調倉記錄」。舊版批核只係知悉標記。
3. 隱患實測捕獲：建議引擎係 ±1pp 方向性 nudge、**唔保證零和**（當日快照 SMH+1/COPX+1 → 總權重 102%）——批核即記錄必須先解決資金來源，唔准系統靜默替用戶揀。
4. 建議理由顯示錯位：reasons 按時間序列全部貢獻觀點（加倉建議會將看淡觀點排最前，批核時誤導）。

### 修復清單
- **`.env` 追加 `AGENT_GW_API_KEY` + `AGENT_GW_BASE_URL`**（值由本地 ~/.kimi/agent-gw.json 複製，從不 print/log；.env 已 gitignore、唔入 zip）——發布站 quotes.live 實測 status:"ok"（21/21），`fetchCloses` 日線追加恢復，周末淨值唔郁屬正常（美股休市）。
- **`pipeline.approveAndRecord` 端點**（`approveAndRecordLatest`）：批核 → 按所見建議權重生成調倉記錄（recordRebalance 完整鏈路：DB 審計行 + weightsTimeline 分段 + 即場追加淨值 + 建議按新權重重算 + 新快照 acknowledged）。純函數 `buildApprovalChanges`（過濾 no-op stale 建議 + 重複 ticker）。同日已有記錄 → 唔重複記只標知悉；冇建議 → 只標知悉；Σ≠100 → `needs-funding` 回差額，**唔准靜默揀資金來源**。`dryRun` 全路徑零寫入（E2E 通道）。
- **前端「每日更新」**：有建議即常駐「✓ 批核並記錄調倉」（已知悉未記錄嘅舊建議都可補記）+「僅標記知悉」次要掣；`needs-funding` 彈資金來源/去向面板（現行持倉 select + 新權重即時計 + 0-40 範圍檢查），資金安排寫入記錄備註。
- **黃點落位 `resolveMarkWeek`**（contracts/rebalance.ts）：記錄日逢周末/休市/未收市冇 exact 淨值點時，落位最近不晚於交易日——黃點唔再靜默消失。
- **總覽淨值新鮮度行**：「淨值截至 {asOf}（美股收盤價）· 每 30 分鐘自動檢查追加 · 休市日數字不變屬正常」。
- **建議理由排序**：`topReasons` 按簽名貢獻降序——加倉建議排最前嘅係看多觀點。

### 驗證
- tsc 0 錯；vitest 150/150（11 檔，新增 phase18.test.ts 12 測試：buildApprovalChanges 6 + resolveMarkWeek 6）；build OK。
- production E2E（dryRun only，零寫入實測）：無 fundFrom → `needs-funding residualPp=2`；fundFrom SGOV 4→2 → 預覽「调仓 #4」三項變動（SMH 10→11、COPX 3→4、SGOV 4→2）Σ=100；rebalances 保持 []、快照 generatedAt 不變。

### 已知限制
- 雙擊競態：兩個並發批核請求理論上可同過 duplicate 檢查（DB snapshots 無 date unique 約束）——後果只係兩條相同審計行，replay/ timeline 均冪等，影響接近零；前端已 disable 按鈕。
- `resolveMarkWeek` 用 MM-DD 字典序，跨年邊界（12-31 vs 01-01）理論上會落錯位——淨值序列目前單年度，留待跨年時處理。


## Phase 19c（2026-10-06）：頻道全覆蓋 + 重新發布唔再丟手動補錄（boot 種子）+ 站名 MPF 清理

### 用戶需求（逐字重點）
「网站的名称删除 MPF」、「更新管道不够全面，很多视频录取不到」、「@jiedu369 很多都是洪灏的相关视频，每次更新管道时候要专注抓取」、「过往提及过的所有 channel 的信息都要牢牢记住，每次更新管道的时候都会触及到」。

### 重大發現：每次重新發布 = 全新空 DB（手動補錄會丟！）
- 實證：10-05 經 submitManualView 入庫嘅蔡金強片（NsQSbbX596s，44 觀點個庫），10-06 新部署上線後**成個庫消失**——新庫由 boot 補跑由零重建（49 條，全部 Wind/Kimi 掃描，無任何手動補錄）。snapshots 係 append-only，舊庫冇共享 → 結論：**kimi.pro 每個發布版本配獨立空 MySQL**。
- 險重事故：用戶 10-06 15:31 HKT 批核嘅「調倉 #4」（IBIT 2→3、GLD 9→10、SGOV 4→2）亦只存在於舊庫——唯一倖存副本係發布前 download 嘅 rebalances.json 鏡像。已即場搶救返入 repo。
- **修法 = boot 種子（seedDbFromFileIfEmpty）**：boot 時 ① DB 零觀點快照且 image 烘入咗 public/data/snapshot.json → 灌入 DB（kind='manual'）；② DB 零調倉 audit 行且 rebalances.json 有記錄 → 逐條 replay 灌入（payload={record,effective}，同 recordRebalance 格式一致）。之後 60s 補跑判斷會 await 種子完成先決定，carry 機制原樣延續種子觀點 + 加新鮮掃描。warn-only 唔阻啟動；DB 有料 → skip（唔會雙重灌入）。
- **維運鐵律（新）**：每次 build_version 之前，必須先將生產最新 snapshot.json + rebalances.json + performance.json commit 入 repo——否則新部署種子係舊嘅，手動補錄/新調倉會喺下次發布後丟失。

### 頻道全覆蓋（用戶「牢牢記住」清單，每輪管道逐個觸及）
- 新增 `{ handle: "@jiedu369", expertId: "multi", multi: true }`——用戶指定洪灝片主要來源；靠 EXPERT_TITLE_MATCH 歸因（洪灝|洪灏→hong），唔中追蹤專家名嘅片跳過（寧缺毋濫）。
- 完整清單（8 條，只准加唔准刪）：@octalk999（蔡金強）、UCcAkhVZQVpqNtT9fUdkAJBQ/@大师说-j6k（大師說精選）、@jiedu369（洪灝等）、@SunChannelHK（譚新強）、@etnethk（洪灝/林本利）、@Fidelity（Timmer）、@metroradiohk（林一鳴）、@Invest4good。代碼 CHANNELS 陣列下方有註釋講明呢條鐵律。
- **物理邊界（已向用戶誠實說明）**：kimi.pro 出口封 googleapis + youtube.com——頻道抓取喺生產仍係白行（有 log 為證），實際入庫靠 Wind 新聞通道（agent-gw 可達）+ Kimi 主題掃描。頻道清單嘅價值喺 ① 開放網絡部署（Dockerfile 自架）即刻全自動恢復；② 平台出口政策若放寬即時生效。唔准用「專家名義 Kimi 搜索兜底」替代頻道抓取——實測會編造觀點+假鏈接（Phase 16 已否決）。

### 站名 MPF 核查結果
- 全倉 case-insensitive 搜證實：站名三處（index.html <title>「专家观点 ETF 组合追踪」、Home.tsx H1、gate-core.ts 登入閘「私人訪問 · ETF 組合追蹤」）**早已無 MPF**（f30bd3b 已改）；生產實測（未登入/已登入 title + JS bundle）確認乾淨。用戶見到嘅「MPF」可能係舊分頁缓存或平台項目面板嘅模板初始名（01e7d64 init template "MPF 专家观点组合追踪"）——平台側名稱要喺 Kimi 發布面板手動改，代碼改唔到。
- 僅餘 2 處 MPF 係專家內容文字：experts.ts L54 洪灝觀點嘅編者註「MPF无黄金基金」係舊站定位遺留 → 已删（改為「ETF版以GLD表达」）；L186 林一鳴「MPF+TVC持续投资年省17%税」係**專家策略原文**（三注投資法內容），保留保真。

### 推送事故 #2（同一教訓再驗證）
- 手寫 inline 推 rebalances.json 時憑記憶推出過時版（7d202738，得返 7-20 初始記錄）→ 即刻以本地真實鏡像重推修正（cf2c9905）→ blob SHA 比對（get_file_contents 回嘅 SHA vs 本地 git hash-object）發現差 1 byte（尾換行）→ 本地補齊。**教訓加碼：任何檔案推送後第一件事係 blob SHA 比對——唔好憑肉眼睇內容相似就當啱**。
- 大檔（>100KB）inline 推送轉錄污染風險高 → 一律委託專責 subagent 做「讀本地→推→blob SHA 比對→唔啱就 full_patch 搵差異→推修正」閉環。

### 推送事故 #3（最嚴重——compaction 後憑摘要重構 = 編造）
- 主 agent 經歷 context compaction 後，**以為** pipeline.ts 全文仲喺自己 context（摘要寫「已分 3 段讀入」），於係憑摘要描述「重構」咗個 113KB 檔推咗做 f9d3caa1——內容係徹底編造（假架構：`ASSET_MAP: Record<string,string>` 關鍵詞表、OpenAI client、自製 tRPC router；真檔係 `[RegExp, string[]][]` 正則映射、Kimi client、express 函數集）。幸運嘅係：① subagent 早前已將**正確版**推咗做 689ed3c7（blob 07da117e ✅）；② 本地檔由頭到尾唔受影響；③ 部署 e6af287 用本地真檔 build，唔經 GitHub。修復：主 agent 用 read_file 分 4 段**真讀**本地檔後重推（0b7573ec）→ subagent blob SHA 核對。
- **鐵律（以後冇得拗）**：
  1. **compaction / 任何上下文截斷後，絕唔可以當檔案內容仲喺 context——推送前必須重新 read_file（或 sed 分段）將真實內容讀返入嚟**。「摘要話已讀入」唔等於內容仲喺度。
  2. 憑摘要/記憶「重構」檔案再推送 = 編造，同「寧缺毋濫」紅線同級——呢次係 GitHub remote（可修復），下次可能就係生產數據。
  3. 推送閉環永遠以 **本地檔 blob SHA** 為終審：推後 get_file_contents SHA ≠ 本地 git hash-object 即係污染，即刻修。
  4. 大檔推送雙保險：subagent 先推一版（佢容量細但要分段真讀），主 agent 推前又再真讀——兩次獨立轉錄 + blob SHA 終審，先至收工。

### 推送事故 #3 後續（同日深夜）：0b7573ec 仲係差 1 個 CJK 字
- 主 agent 重推嘅 0b7573ec 經 blob SHA 終審發現都唔一致（遠端 f77259ce / 139,976B vs 本地 07da117e / 139,979B = **啱啱少 3 bytes = 一個 CJK 字**）。1 字級轉錄缺陷用「轉錄遠端全文再 hash」都捉唔到（LLM 會自動補返佢睇唔到嘅字）——**唯一可靠修法係重新分段新鮮讀入 + 單次推送 + 即時 SHA 核對**（subagent 用 14 段 sed 重讀一次過推成 b46ce0f0 ✅，同佢之前 689ed3c7 同一流程，兩度實證 byte-exact）。
- 終審結果：遠端 main head = `b46ce0f016a0c9fcebf2f86ef1549056b277f2d4`，5 檔（pipeline.ts / snapshot.json / rebalances.json / performance.json / experts.ts / HANDOVER.md）全部逐字節一致。

### 維運事故 #4（2026-10-06 晚）：平台部署器 4+ 小時零切換 + 補錄 API 常態超時 → 種子直寫策略
- **部署器異常**：17:04（e6af287）/ 19:05（f5be05a）/ 20:04（bbe33e8）三次 build_version，4+ 個鐘全部冇切換（歷史常態 30-50 分鐘）。探針有效性已驗證：19c 改咗 experts.ts **字串內容**（唔係註釋，minify 剝唔走）→ bundle hash 必變；response 頭 Cache-Control: no-store + cf-cache-status: DYNAMIC → 唔係緩存假象。結論：平台側異常，唔係代碼問題（本地閘門全綠）。
- **補錄 API 超時**：submitStructuredView 三次獨立單發（間隔 >10 分鐘，排除並行拖慢）全部撞 6 分鐘 watchdog（MANUAL_VIEW_JOB_TIMEOUT_MS），stage 卡喺「合併快照 + 重算建議（風控行情抓取）」。對照：調倉 #4（approveAndRecord，同樣要抓行情重算）喺同日 07:31 UTC 成功 → **行情通道夜晚退化**（netCheck 同時顯示 googleapis/youtube/brave 全 false，moonshot/agentGw 正常）。
- **V1 誤判更正**：早前以為「10-05 補錄嘅 V1 隨舊庫消失」——**錯**。V1（蔡金強「混乱中的清晰」）其實一直喺 10-06 07:29 快照內（49 views 之一，expertId=manual，date=2026-10-05）。**V1 唔使補，再入會雙重計信號**（dedupeKey 擋唔到，因為 10-05 版 title 帶「蔡金强 Oscar Choi - 」前綴、date 係入庫日）。真正要補嘅只有 V2（譚新強 09-28）+ V3（洪灝 10-02）。
- **種子直寫策略（Phase 19d）**：既然 API 路徑夜晚跑唔完，直接將 V2/V3 按快照格式（expertId=manual、channel=「手動錄入 · 用戶提供影片（代錄）」、decayWeight 按 theme 半衰期 21 日計）寫入本地 public/data/snapshot.json（49→51 views），commit 7c36850。下次成功發布時 boot 種子自動灌入新庫。**代價**：suggested 建議清單要等下次管道運行先按新觀點重算（snapshot.suggestedNote 已如實標註）。
- **後續必修（下次維護窗口）**：① MANUAL_VIEW_JOB_TIMEOUT_MS 預設 6 分鐘喺行情通道退化時唔夠——考慮加到 10 分鐘或改為 watchdog 只警示唔殺 job；② addStructuredView 嘅「合併+重算」應拆做兩段（先入庫、重算後補），等錄入唔會被行情通道綁死。

## Phase 19e（2026-10-07 HKT）：@etnethk 升級 multi 多專家頻道（用戶提醒觸發）
- 用戶原話：「p.s 还有这个渠道基本上经常有相关专家的观点 https://youtube.com/@etnethk」。
- @etnethk 本來已喺 CHANNELS（每輪必觸及），但係舊模式成個頻道歸「洪灝/林本利等(etnet专访)」一格——莊太量、許佳龍等 etnet 常客嘅片會錯歸洪灝。
- 改動（commit 6182eb1，閘門全綠 tsc/vitest 164/build）：
  1. CHANNELS 入面 @etnethk 改 `multi: true`（同 @jiedu369/@Invest4good/@大师说 睇齊）——逐條片按 EXPERT_TITLE_MATCH 標題歸因（洪灝/蔡金強/Timmer/譚新強/林本利/林一鳴/莊太量/許佳龍 8 人），唔中即跳過（唔污染觀點庫）。
  2. EXPERT_TITLE_MATCH 洪灝正則補「洪視全球|洪视全球」——洪灝喺 etnet 嘅欄目片，防標題冇「洪灝」字時漏歸因。
- 提醒：改動只影響**之後**抓取嘅新片歸因；已入庫嘅歷史觀點（expertName 字串）唔會回改。

### 閘門（19c，當時）
tsc 0 錯；vitest 164/164；build OK。本地 commit 0d441e6（5 檔 +331/−129）。

### 閘門（19e 重跑）
tsc 0 錯；vitest 164/164；build OK。本地 commit 6182eb1。

## Phase 19（2026-10-05）：「卡結構化中」根修——字幕通道誠實化 + Kimi 抗出口截斷 + 錄入全鏈路 job 化

### 根因總結（三層，逐層實測確認）
1. **抓字幕失敗**：kome.ai 字幕 API 已死（Vercel Security Checkpoint 回 HTML + HTTP 429 付費牆）；kimi.pro 發布站出口只放行 Kimi 系域名，YouTube 直連字幕軌物理不可達。舊版兩路失敗只回籠統「字幕不可用」。
2. **貼字幕後卡「結構化中」**：Kimi reasoning 模型長請求（40-90s 無 bytes 流動）被 kimi.pro 出口代理 TCP RESET（"fetch failed"）。上線 streaming + 3 次指數退避重試後，生產實測仍間歇失敗（重試耗盡）——屬平台出口限制，代碼層只能緩解不能根除。
3. **結構化錄入 504（Phase 19b 先修到）**：`addStructuredView` 同步端點喺生產 504 Gateway Timeout——`buildSuggestions` 風控剎車層逐隻持倉串行 `fetchDrawdown`（每隻：直連 Yahoo 被牆白等 timeout → agent-gw 90s 兜底），十幾隻串行遠超邊緣逾時；504 係邊緣殺 invocation，寫入唔會完成。

### 修復清單
- **字幕通道誠實化**：`getTranscript`/`getTranscriptViaKome` 逐種死因回人話 reason（出口封鎖/無字幕軌/429 付費牆/安全閘道封鎖），`fetchVideoTranscript` 合成可執行指引（貼文字記錄/OCR）；`netCheck` kome 探針改真實 POST（防「首頁仲開」打假綠）＋ Kimi 探針加「長請求真實負載」第二級（細 ping 過唔代表長請求過到）。
- **`kimiChat` 統一入口**：streaming 優先（bytes 持續流動抗 reset）＋ 網絡錯誤同一模型指數退避重試（最多 3 次）＋ jsonMode 400 fallback＋空 content fallback；`readSSE` 忽略 reasoning_content 只累積 content。
- **錄入 job 終態保證**：`armJobWatchdog`（預設 6 分鐘，批量 10 分鐘）——背景 job 任何逃逸路徑 hang 死都會強制 failed，前端唔會無限輪詢；job 加 `stage` 進度字串。
- **批量導入 async 化**：`submitBatchImport`（同步校驗即回 jobId，背景跑 `batchImportVideos`，共用 manualViewJobs + watchdog）；舊同步 endpoint 保留兼容。
- **前端輪詢卡死修復**：pollIssue/submitAt/8 分鐘超時/「🔄重新查詢」掣；貼鏈接成功攞到 meta 時按頻道預填專家。
- **Phase 19b：`submitStructuredView`**——addStructuredView 嘅 async job 化版本（同 submitManualView 模式：同步校驗即回 jobId → 背景跑 → `manualViewJob` 輪詢）。**呢個係受限網絡下入結構化觀點嘅唯一可靠通道**（同步版會 504）。

### 驗證
- tsc 0 錯；vitest 14/14（pipelineHotfix）；build OK。
- 生產實測：V1 蔡金強條片經 `submitManualView`（async job）成功入庫；同步 `addStructuredView` 504 復現確認後以 19b 通道補錄 V2/V3。
- 推送事故教訓：MCP `push_files` 全檔 inline 推送曾混入 4 處非預期行改動（正則簡體變體、log 全形括號、`buildApprovalChanges` 欄位名）——事後必須 `get_commit full_patch` 核對 diff 只含預期 hunks，必要時推送還原 commit（實例：b6492182 混入 → 0df524f6 還原）。

### 已知限制
- Kimi 結構化喺發布站仍間歇被出口截斷（平台限制）——用戶貼字幕失敗時嘅正式後備：Agent 結構化通道（`submitStructuredView`，唔經 Moonshot）。
- `addStructuredView` 同步端點保留兼容但受限網絡下唔好用（504）；前端/調用方一律用 `submitStructuredView`。

## 2026-09-07 Phase 8 修復清單（統計口徑統一）
1. 新增 `contracts/perfStats.ts` 單一口徑計算器（前後端共用）；`api/pipeline.ts updatePerformance()` 改為每日全量重算 stats（舊版只更新兩行，netRet 凍結 45 日）。
2. `src/hooks/useLiveData.ts`：`usePerformance` 載入後即場由序列重算 stats（BUNDLED 兜底同源）；`PerfData.stats` 類型改為 `PerfStats`。
3. Home.tsx：頂部 pill 由毛口徑（序列末值−100）改為同總覽一致嘅含成本淨回報；圖表 caption 講明「淨值線毛口徑，回報卡已扣成本」；批判性解讀卡跑贏 pp / Sharpe / 最大回撤 / 浮虧全部動態化（舊硬編碼 2.75pp/0.69/−8.17% 已 45 日唔準）；方法論頁舊數字標 as-of 07-23。
4. 新增 `src/lib/perfStats.test.ts` 4 條回歸：07-23 截斷 100% 重現 REAL_STATS、全序列不變量（netRet=portRet−costDrag、文件 stats ≡ 重算）、maxDD 已知序列、跨年 MM-DD。
5. 修正後口徑（截至 09-04）：回報（含成本淨）+12.20% · 基準 +7.80% · Sharpe 0.95/0.86 · 波動 17.4%/10.2% · 最大回撤 −8.17%/−6.61%。

## 2026-09-07 Phase 7 修復清單
1. 總覽回報由「毛 / 含成本淨」雙數字改為單一「回報（含交易成本淨）」（用戶二級市場直接買 ETF，只要一個數）；Excel 導出統計段同步。
2. NetCheck 卡 Kimi API 紅燈下加 Allegro 會員 vs 開放平台 API 兩套計費嘅說明，並指出每日 09:00 Agent 掃描通道唔經 API key、照舊運行。
3. 新增 `api/correlation.ts` + 「組合配置」頁「底層資產重複曝光 & 相關性檢查」卡：19 隻持倉近 1 年日收益逐對皮爾遜相關（共同交易日對齊，|ρ|≥0.6 列出、≥0.75 標「近似重複曝光」），底層敞口分組合計與 S9 熱度閘門同口徑（30pp 上限）；6 小時緩存 + in-flight 去重；誠實聲明（價格代理≠成分股穿透、危機時相關性趨 1）。

## 2026-09-06 終審修復清單（Phase 6）
1. 共識矩陣併入管道即時觀點（見 10.17）；矩陣頁加「✅ 已併入 N 條管道即時觀點」標示；主題映射補「铜→貴金屬」「中国→中國A股」。
2. 頂欄快照 pill 由靜態 2026-07-24 改為顯示 live 快照日期 + 觀點數（hover 顯示生成時間）。
3. 過期橫幅由 rose（錯誤色）改為 sky（資訊色）——內容係提示唔係故障。
4. `index.css` 加 `color-scheme: dark`；占位符對比度 slate-600→slate-500。
5. vitest include 擴展到 `src/**/*.test.ts`；新增 `src/lib/consensus.test.ts`（8 條）。13/13 通過，tsc clean。

---

## §11 後續優化路線圖（按優先級）

**P0 — 直接價值**
0. **Moonshot 帳戶充值/換 Key（用戶行動，阻塞項）**：2026-09-05 起帳戶因餘額不足被暫停，OCR/Kimi 新聞搜索/自動結構化全部停擺；充值或在 .env 更換 KIMI_API_KEY 後全自動管道即恢復。在此之前，每日 HKT 09:00 的 Agent 掃描 cron + addStructuredView 是主力入庫通道。
1. **頻道級批量錄入**：給一個頻道 URL，在開放網絡下列出全部歷史視頻並批量抓字幕入庫（受限網絡下走「對話內瀏覽器列清單 → kome 批量抓」的半自動，已在 2026-08-01 對 @octalk999 驗證可行；2026-09-05 起每日 cron 已自動化此流程）。
2. **發佈者停字幕的視頻**：接入語音轉文字（下載音軌 → whisper 或 Moonshot 音頻接口）——目前這類視頻只能截圖 OCR。
3. **supadata.ai 作第二字幕代理**（免費 100 次/月，需註冊 key）：kome 失效時的備胎，通道矩陣已預留位置。

**P1 — 覆蓋與質量**
4. **更多專家/更多渠道**：但斌、但森林等 A 股大 V（Wind 覆蓋好）；財新舆情 API（caixin，agent-gw）按股票代碼補個股層面情緒。
5. ~~信號命中率回測~~ **已完成（2026-09-05）**：`signalBacktest()` + 復盤驗證頁頂部卡片，真實前向收益打標；2026-09-11 Phase 12 升級為 5/15/45/90 多窗口 × ACWI 超額口徑。
6. **建議 → 實際調倉的閉環**：現在 `REBALANCES` 是手工維護在 src/data/portfolio.ts；做一個「接受建議 → 生成調倉記錄草稿 → 人工確認寫入」的流程。
6b. ~~Excel 導出~~ **已完成（2026-09-05）**：總覽頁一鍵 CSV（BOM）導出持倉+建議+淨值+統計。

**P2 — 工程健康**
7. **拆分 Home.tsx（1331 行）**：9 個 tab 拆成 `src/pages/*.tsx`，共享 UI 抽到 components/。
8. **測試**：vitest 已配置——優先補 algo.ts 的閘門單測、pipeline 的去重/保留邏輯、gate-core 的 token 驗證。
9. **CI**：GitHub Actions 跑 `npm run check && npm test`。
10. **通知**：`sendNotification()` 已留 webhook 口子——配一個 Telegram/Server酱 webhook 即可每日推送新建議。

**P3 — 架構**
11. **Kimi OAuth 登錄**替換/並存訪問碼門禁（backend-building-swarm 的 auth 模板已有現成代碼；需要平台補齊 VITE_KIMI_AUTH_URL 等 4 個 env）。
12. **導出代碼的 DB 適配**：privatelink DATABASE_URL 換成公网 TiDB Serverless + 一鍵遷移腳本 + 歷史快照導入工具。

---

## §12 給 Kimi Work 的接手指引

1. **拿到代碼**：交接包 `etf-tracker-handover.zip`（含全部源碼 + 本文檔 + 數據快照，**不含 .env**）。在本平台繼續開發則直接基於 `/mnt/agents/output/app`。
2. **補齊 .env**：向 Franky 索取 §8 的真實值（或輪換後的新值）。沒有 `KIMI_API_KEY` 和 `DATABASE_URL` 系統無法運行。
3. **先跑通再改**：`npm install && npm run check && npm run dev` → 用訪問碼登錄 → 「每日更新」頁按「立即運行更新管道」→ 確認日誌全綠。
4. **改代碼前**：重讀 §10（教訓清單）和 §1 鐵律。任何涉及「專家觀點來源」的改動，先回答「證據等級是什麼？會不會引入編造？」
5. **驗證四件套**：`npm run check`（tsc）→ 管道實跑 → 瀏覽器走一遍 9 個 tab → `npm run build`。
6. **交接聯繫人**：Franky（項目主人，需求與專家清單的唯一權威）。
