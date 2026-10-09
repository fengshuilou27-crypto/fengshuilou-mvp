# Kimi Work 任務指令書：重建（並優化）專家觀點 ETF 組合追蹤網站

> 畀 Kimi Work：你收到嘅 zip（`etf-tracker-handover.zip`）係一個**真金白銀實戰緊**嘅完整項目。任務係**一模一樣重建佢，仲要喺唔破壞現有邏輯嘅前提下做得更好**。交接人：Franky（項目主人，需求唯一權威）。本指令書係入口；細節以 zip 內 `HANDOVER.md`（55KB+，含 §1 鐵律、§10 教訓清單 32 條、§12 接手指引）為準。

---

## 1. 呢個網站係咩

- **用途**：追蹤 8 位真實財經專家（洪灝、林本利、林一鳴、蔡金強、譚新強、莊太量、蔡嘉民、Jurrien Timmer）嘅公開觀點，結構化成信號，驅動一個 19 隻 ETF 嘅模擬組合，每日更新、生成調倉建議（**永不自動執行，必須 Franky 人工覆核**）。
- **技術棧**：React 19 + Vite + Tailwind + shadcn/ui（前端 9 個 tab）；Hono + tRPC 11 + Drizzle ORM（後端）；MySQL/TiDB Serverless（數據庫）；Moonshot Kimi API（kimi-k2.6→kimi-k3 回退鏈，LLM 結構化 + 聯網搜索 + vision OCR）。
- **當前狀態（Phase 13.2，2026-09-11）**：生產可用。最近一次管道實跑 success：60 條觀點、2 項建議待覆核。86 項測試全綠。

## 2. 你要做咩（優先順序）

1. **先原樣跑通**（呢步唔過，唔准郁任何代碼）：
   - `npm install && npm run check && npm run build`
   - 補齊 `.env`（見 §3，向 Franky 攞真值）→ 起 production server
   - 用訪問碼登入 → 「每日更新」頁撳「立即運行更新管道」→ 日誌全綠
   - 9 個 tab 逐個行一遍
2. **跟住先談優化**。可選 roadmap（HANDOVER.md Phase 13.2 附錄有全文）：
   - 主題掃描通道改良：45 日窗放寬到 90 日 / 支持多輪 tool_call loop（而家 R2 封頂，模型想再搜會被截斷）
   - 結構化 timeout 120s 偶發仍唔夠（林本利實例）——可加重試或再調高
   - Home.tsx 105KB 拆分；consensus.ts matchExpert 改用管道嘅複合名切分
   - 45/90 日回測窗待歷史累積成熟
3. **優化嘅底線**：任何改動過四件閘——`npm run check`（tsc 0 錯）→ vitest 全綠 → 管道實跑 success → `npm run build` OK。

## 3. 環境變量（.env 唔喺 zip 入面，必須向 Franky 索取）

`.env.example` 有全部變量同註釋。關鍵：
- `KIMI_API_KEY` + `KIMI_BASE_URL`：**兩站 key 唔通用**——platform.moonshot.cn 開嘅 key 配 `https://api.moonshot.cn/v1`，platform.moonshot.ai 開嘅配 `https://api.moonshot.ai/v1`。攞到新 key 第一件事：兩站各 probe 一次定位歸屬。
- `DATABASE_URL`：MySQL/TiDB 連線字串。**永不 drop 表、永不 `db:push --force`**。
- `ACCESS_CODE`：訪問門禁密碼（向 Franky 索取；唔准寫入任何文檔/git）。
- `YOUTUBE_API_KEY` / `NEWS_API_KEY` / `BRAVE_API_KEY`：受限網絡下會跳過，屬正常。
- agent-gw 憑證：讀 `~/.kimi/agent-gw.json`，**永不寫入 repo**。

## 4. 鐵律（違反即返工）

1. **寧缺毋濫**：LLM 永不編造專家觀點/鏈接——只要字幕/全文級證據；結構化失敗降級標題入庫，唔准腦補。
2. **調倉建議永不自動執行**——必須人工覆核。
3. **密鑰只存服務端 .env**，永不 log/print/commit；交接包排除 .env。
4. **唔好郁數據庫結構**（除非加表），永不 drop。

## 5. 最容易中伏嘅位（§10 教訓精選）

- **kimi-k2.6/k3 係 reasoning 模型**：temperature 只准 1（唔好設）；reasoning tokens 食 max_tokens（OCR 唔設上限）；長文調用 timeout 要 ≥120s。
- **$web_search 新協議**：R1 返回嘅 tool_call `function.arguments` 已含搜索結果——R2 tool message content 必須回傳 arguments 本身，回傳空字串 = 模型收唔到搜索結果。
- **同一服務所有調用點（含健康檢查探針）共用同一 base URL 變量**——唔係就會「業務通、狀態燈紅」。
- **netCheck 綠燈 ≠ 業務通**：換模型/換 key 後要全鏈路真實業務調用驗證。
- **tRPC v11**：query 用 GET + `--data-urlencode 'batch=1'&'input={"0":{"json":null}}'`；mutation 要 POST `{"0":{"json":null}}`；runNow 係異步，要 poll pipeline.status。
- 登入端點係 `POST /api/auth/login`（body `{"code":"..."}`），唔係 tRPC。

## 6. 驗收標準

- [ ] `npm run check` 0 錯、vitest 86+/86+ 綠、`npm run build` OK
- [ ] 訪問碼登入 → 9 tab 全部正常渲染
- [ ] 手動觸發管道 → status success，日誌逐行合理（受限網絡下 YouTube/Brave 跳過屬正常）
- [ ] 觀點頁 ≥60 條、建議生成邏輯不變（±1pp/日信號閘、-2pp/日剎車閘）
- [ ] 所有優化改動有測試覆蓋、HANDOVER.md 加附錄記錄

## 7. 交接包內容

`etf-tracker-handover.zip`（149 檔）：全部源碼（api/ src/ contracts/ scripts/）、`HANDOVER.md`（完整歷史同教訓）、`public/data/`（觀點快照 60 條 + 表現序列）、`.env.example`、`Dockerfile`、package.json 等。**不含** .env、node_modules、.git、dist。

有疑問：所有決策以「Franky 嘅真金白銀安全」為最高原則——唔肯定就問，唔好賭。
