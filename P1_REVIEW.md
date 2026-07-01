# 下一輪修復（P1）— 批判性 Review 報告

## 修復摘要

| 項目 | 狀態 | 說明 |
|------|:---:|:---|
| 前端 fetch 超時處理 | ✅ | 所有 8 個 HTML 文件添加 AbortController，30 秒超時 |
| 結果導出功能 | ✅ | index.html 添加「導出報告」按鈕（html2canvas PNG） |
| Google Maps API 嵌入 | ⚠️ | 代碼已嵌入 key，但 Cloud Console 仍拒絕請求 |

---

## 1. 修復詳情

### 1.1 AbortController 超時處理 ✅

**修改範圍：** `static/index.html`, `static/fxti/index.html`, `static/fxti/result.html`, `static/map.html`, `static/module1.html`, `static/module2.html`, `static/module3.html`

**實現：**
```javascript
async function fetchWithTimeout(url, options = {}, timeoutMs = 30000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        clearTimeout(id);
        return response;
    } catch (err) {
        clearTimeout(id);
        if (err.name === 'AbortError') {
            throw new Error('請求超時，請檢查網絡連接或稍後重試');
        }
        throw err;
    }
}
```

**驗證：** 所有 `await fetch(` 調用已替換為 `await fetchWithTimeout(...)`，無剩餘未包裝調用。

---

### 1.2 結果導出功能 ✅

**修改文件：** `static/index.html`

**實現：**
- 引入 `html2canvas@1.4.1` CDN
- 在結果區域底部添加「📥 導出報告（圖片）」按鈕
- `exportResult()` 函數使用 `html2canvas` 截取 `.result-section` 為 PNG，自動觸發下載
- 文件名：`風水樓盤匹配報告_YYYY-MM-DD.png`

---

### 1.3 Google Maps API 嵌入 ⚠️

**修改文件：** `data/google_maps_integration.py`

**實現：** 將用戶 API key `AIzaSyCxnCUKN9PblvbQd1o1u3EM0frHW7PlY5E` 硬編碼為默認值（環境變量 > config.json > 硬編碼）

**測試結果：** 仍返回 `REQUEST_DENIED`：
- Geocoding: "This API is not activated on your API project"
- Elevation: "This API is not activated on your API project"
- Places: "legacy API not enabled"

**根因：** Cloud Console 顯示「Enabled」但實際未生效。可能需：
1. 點擊 Manage 按鈕確認啟用
2. 設置 **帳單帳戶**（billing account）— 即使免費額度內也必須綁定信用卡
3. Places API 需啟用 **Places API (New)** 而非舊版

---

## 2. 批判性 Review：是否提升風水匹配邏輯？

### 2.1 結論：間接提升，非直接算法改進

| 修復項目 | 風水匹配邏輯提升 | 用戶體驗提升 | 系統穩定性提升 |
|----------|:-----------:|:---------:|:-----------:|
| AbortController 超時 | ⭐（間接） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 結果導出 | ⭐（間接） | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Google Maps API | ⭐⭐⭐（潛力） | ⭐⭐⭐ | ⭐⭐⭐ |

### 2.2 逐項分析

#### A. AbortController 超時（穩定性提升，間接支持風水匹配）

**修復前：**
- 用戶填寫表單後點擊「分析」，如果後端響應慢（如雙人模式八字計算），瀏覽器 fetch 無超時，用戶只能無限期等待
- 在網絡不穩定時，fetch 掛起導致頁面無響應，用戶無法獲得任何結果
- 這直接導致「目標權重傳遞失效」等問題被用戶感知為「系統壞了」

**修復後：**
- 30 秒超時後自動中斷，顯示「請求超時，請檢查網絡連接或稍後重試」
- 用戶可以重新提交，避免頁面卡死
- 在弱網環境下，超時機制確保用戶體驗不會完全崩潰

**對風水匹配邏輯的影響：**
- 這是**基礎設施層**的改進，不直接改變算法
- 但它是**必要條件**：如果前端無法穩定獲取後端結果，任何風水算法都無法觸達用戶
- 評級：間接提升（從「不可用的算法」到「穩定可用的算法」）

#### B. 結果導出（展示層提升，增強風水可信度）

**修復前：**
- 用戶看到結果後，無法保存或分享
- 風水師要求「把結果發給我看看」時，用戶只能截圖或手動記錄
- 這降低了系統的「專業工具」形象

**修復後：**
- 一鍵導出 PNG 圖片，包含完整結果（分數、雷達圖、飛星盤、八字排盤、分析摘要）
- 用戶可以保存到相冊、分享到微信/WhatsApp、發送給風水師
- 文件名包含日期，便於管理

**對風水匹配邏輯的影響：**
- 這是**展示層**的改進，不改變算法
- 但**專業可信度**顯著提升：從「只能看不能存」到「可導出專業報告」
- 風水師可以拿到完整報告進行二次審核，間接提升算法可信度
- 評級：間接提升（從「玩具」到「工具」）

#### C. Google Maps API（潛在數據層提升，待激活）

**修復前：**
- 煞氣 POI 數據來自手動維護的 `sha_poi_hk.json`（約 200 個點）
- 屋苑坐標來自本地 `estate_coordinates.json`（約 252 個）
- 高程來自 SRTM DEM 30m（已升級）

**修復後（代碼就緒，待 API 激活）：**
- `geocode_address()`：自動將地址轉為坐標，支持任意地址輸入
- `search_nearby_pois()`：自動掃描周邊 1000m 內的醫院、墳場、變電站等煞氣源
- `get_elevation()`：獨立驗證 SRTM DEM 數據
- `verify_dem_against_google()`：DEM 數據質量校驗

**對風水匹配邏輯的潛在影響：**
- **直接提升**：GIS 風水維度（目前 10 分）可以更精確計算，因為坐標和煞氣數據更準確
- **擴展性**：支持任意地址輸入，不限於 252 個已知屋苑
- **數據驗證**：DEM 高程可以與 Google Elevation 交叉驗證
- 評級：高潛力（需 API 激活後才能實現）

---

## 3. 評級

### 本輪修復前評級
- 功能：8/10（交叉驗證修復後）
- 體驗：7/10

### 本輪修復後評級
- 功能：8/10（無變化，Google Maps API 待激活）
- 體驗：8/10（+1，超時保護 + 導出功能）
- 穩定性：8/10（+2，AbortController 顯著提升）

### 總體評級：B+（穩步提升）

---

## 4. 剩餘問題

| 問題 | 嚴重程度 | 狀態 |
|------|:------:|:---|
| Google Maps API REQUEST_DENIED | 高 | 需用戶操作 Cloud Console |
| 七運飛星盤部分數據缺失 | 中 | 待處理 |
| 雙人模式缺少八字合婚對比 | 低 | 待處理 |
| 大運/流年分析 | 低 | 待處理 |

---

## 5. 建議行動

### 5.1 立即行動（用戶端）
- [ ] 到 Google Cloud Console → 帳單 → 設置帳單帳戶（綁定信用卡）
- [ ] 確認 Geocoding API、Elevation API、Places API (New) 都已啟用
- [ ] 測試 API 調用是否成功

### 5.2 下一輪修復（建議）
- [ ] 完善七運飛星盤數據（移除「⚠️ 數據需專業確認」標註）
- [ ] 雙人模式添加八字合婚對比
- [ ] 所有前端模組統一添加結果導出功能（module1/module2/module3）

---

*Review 完成時間：2026-06-29*
*Reviewer：Kimi Agent*
*修復版本：風水樓 MVP v2.5+P1*
