# 部署手冊：專家觀點 ETF 組合追蹤 → 真實前向追蹤上線

> 目標：把系統從「快照演示」轉為「每日真實運行」——這是 M4 專家 IC 加權能從人工因子升級為滾動實測值的唯一數據來源。
> 最後更新：2026-08-01（Kimi Work 生成；與 HANDOVER.md §8/§9 互補）

---

## 0. 本機環境體檢結果（2026-08-01 實測）

| 項 | 結果 | 影響 |
|---|---|---|
| 網絡出口 | **開放**（YouTube 200、googleapis 可達、kome 200、Brave 301、Moonshot 401=可達需 key） | 專家字幕管道**可以全自動運行**，無需手動錄入兜底 |
| Docker | ❌ 未安裝 | 本機走 `node dist/boot.js` 直跑；Docker 路徑留給 VPS/NAS |
| 本地 MySQL | ❌ 無 | 需要雲 DB（推薦 TiDB Cloud Serverless 免費層，MySQL 兼容） |
| agent-gw 憑證 | ❌ `~/.kimi/agent-gw.json` 不存在 | Wind 專家新聞通道不可用（會誠實降級寫日誌，不影響主流程）；開放網絡下字幕+Brave+Kimi 搜索已足夠 |

## 1. 需要你做的 4 個決定/動作

| # | 事項 | 選項與建議 |
|---|---|---|
| 1 | **數據庫** | 建議 [TiDB Cloud Serverless](https://tidbcloud.com/)（免費層，MySQL 兼容，HANDOVER 指明 TiDB 兼容）→ 建 cluster → 拿 `mysql://user:pass@host:4000/db?ssl={}` 連接串。替代：任何 MySQL 8（VPS、NAS、PlanetScale 類） |
| 2 | **KIMI_API_KEY** | [platform.moonshot.cn](https://platform.moonshot.cn/) 申請。**HANDOVER §8 安全備忘：舊 key 曾外洩到公開對話，請順便輪換全部 key** |
| 3 | **YOUTUBE_API_KEY** | Google Cloud Console → YouTube Data API v3（免費配額每日 10,000 單位，本系統每日用量 <500） |
| 4 | **跑在哪裡** | ① 這台筆電（簡單，但睡眠會錯過 HKT 08:00 調度——適合先試跑）② 常開機的 NAS/VPS（正式，用 Dockerfile）③ 我幫你裝 Docker Desktop 後本機容器化（折中） |

## 2. 已為你預置的值（寫入下方 .env 模板）

- `APP_ID=etf-tracker-b80cdff3`（隨機生成）
- `APP_SECRET=fc8c8fdf8b323a4f057a6ee66875dc17cc681be96fc415ce1e69e714df15c347`（隨機 64 位 hex，門禁 HMAC 密鑰——只存 .env）
- `ACCESS_CODE=2TZL-5X5Z-VQDR`（沿用現門禁密碼；想換就改這行）

## 3. 部署步驟（拿到 DB 連接串 + 兩把 key 後，約 15 分鐘）

```bash
# ① 在 app/ 目錄建立正式 .env（模板見 §4），填入 DATABASE_URL / KIMI_API_KEY / YOUTUBE_API_KEY

# ② 安裝依賴 + 建表（drizzle 安全路徑，禁止 db:push --force）
npm install
npm run db:generate && npm run db:migrate

# ③ 構建 + 啟動
npm run build
npm start        # NODE_ENV=production node dist/boot.js（:3000）
```

## 4. .env 模板（複製為 app/.env 後填三個空）

```ini
APP_ID=etf-tracker-b80cdff3
APP_SECRET=fc8c8fdf8b323a4f057a6ee66875dc17cc681be96fc415ce1e69e714df15c347
ACCESS_CODE=2TZL-5X5Z-VQDR
DATABASE_URL=          # ← TiDB Cloud 連接串（ssl 參數照它給的保留）
KIMI_API_KEY=          # ← Moonshot key（新申請/已輪換的）
YOUTUBE_API_KEY=       # ← YouTube Data API v3 key
# BRAVE_API_KEY=       # 可選：開放網絡下新聞通道更全
# AGENT_GW_API_KEY=    # 可選：Wind 專家新聞通道
```

## 5. 上線後驗收清單（按順序打勾）

1. 瀏覽器開 `http://localhost:3000/` → 門禁頁輸入 ACCESS_CODE → 進站
2. 「每日更新」頁 → **網絡能力自檢卡**五項全綠（YouTube 直連 ✓ 即可，agent-gw ✗ 屬預期）
3. 「每日更新」頁 → 按「立即運行更新管道」（最長 12 分鐘）→ 狀態轉 success
4. 檢查快照：views 有真實專家內容、suggestedNote 無報錯、brakeStatus=ok
5. 「量化算法」頁 → M4 讀數從「DB 不可用」變為真實 IC 加權讀數（專家信號層復活）
6. 次日 HKT 08:00 後回來確認調度器自動跑了一輪（pipeline_runs 有新記錄）

## 6. 常見坑（來自 HANDOVER §10 血淚史）

- TiDB 連接串的 `ssl` 參數要原樣保留，刪了會握手失敗
- 筆電部署：系統設定 → 電源 → 插電時永不睡眠，否則 HKT 08:00 調度錯過（錯過也不會壞，啟動 60 秒後會補跑一次）
- 首次管道運行要抓 5 頻道 × 近 45 天視頻字幕，12 分鐘超時內屬正常；失敗看「數據引擎狀態」的日誌框
- 密鑰只存在 .env；.env 已在 .gitignore/.dockerignore 排除，交接包也不含
