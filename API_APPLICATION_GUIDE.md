# 風水樓 API 申請建議清單

> 為提升系統數據準確度、覆蓋範圍和自動化能力，建議申請以下 API。按優先級排列。

---

## 🔴 高優先（立即申請，對系統核心功能有顯著提升）

### 1. Google Maps Platform API（Geocoding + Places）

**用途：**
- **Geocoding API**：將屋苑名稱/地址轉為精確 WGS84 坐標（解決目前手動標註 `estate_coordinates.json` 的問題）
- **Places API**：自動發現煞氣 POI（醫院、寺廟、發電廠、墳場、垃圾站等），替代手動維護的 `sha_poi_hk.json`
- **Elevation API**：獨立驗證 SRTM DEM 數據，提供 10m 分辨率高程（部分區域）

**為什麼需要：**
- 目前 `estate_coordinates.json` 僅有 30+ 個屋苑坐標，手動擴展效率低
- `sha_poi_hk.json` 的煞氣 POI 依賴手動收集，覆蓋不全
- Google Places 有香港最完整的 POI 數據庫（醫院、殯儀館、變電站等）

**費用：**
- 每月 $200 免費額度（Geocoding + Places 合計）
- 超出後：Geocoding $5/1000次, Places $17/1000次
- 對於 MVP 階段，200美元額度足夠

**申請鏈接：** https://developers.google.com/maps/documentation/javascript/get-api-key

**替代方案：**
- OpenStreetMap Nominatim（免費，但精度較低，有速率限制）
- 香港地政總署 GeoAddress（需政府申請，較複雜）

---

### 2. OpenTopography API（正式數據源）

**用途：**
- 下載 SRTM GL1 (30m) / COPDEM (30m) / ALOS World 3D (12.5m) DEM 數據
- 我們目前通過 Mapzen/AWS 獲取了相同數據，但 OpenTopography 提供更穩定、受支持的官方 API
- 未來可升級到 **COPDEM 30m**（比 SRTM 更新，2010-2015年測量）或 **ALOS 12.5m**（更高分辨率）

**為什麼需要：**
- 目前 SRTM 數據是 2000 年的，COPDEM (2010-2015) 更準確
- 若 AWS S3 鏈接失效，OpenTopography 是官方備份
- ALOS 12.5m 分辨率可提升地形分析精度 2.4 倍

**費用：** 免費（需註冊學術/研究用途帳號）

**申請鏈接：** https://portal.opentopography.org/request

**替代方案：** 已通過 AWS Open Data 獲取 SRTM（無需 API key）

---

### 3. 香港政府開放數據平台（data.gov.hk）

**用途：**
- 獲取香港建築物輪廓（Building Footprints）坐標
- 獲取官方地形圖等高線（1:5000 / 1:20000）
- 獲取規劃圖則（zoning data），識別工業區/墓園/焚化爐等煞氣區域
- 獲取公共交通數據（地鐵站、巴士站），用於「交通便利度」評分

**為什麼需要：**
- 政府數據是權威數據源，比 Google Maps 更準確
- 建築物輪廓可精確識別屋苑邊界，改善坐標定位
- 規劃圖則可識別「工業區/骨灰龕/垃圾站」等傳統風水忌諱地

**費用：** 免費（香港政府開放數據）

**申請鏈接：** https://data.gov.hk/

**建議下載數據集：**
- 建築物輪廓（Building Footprints）
- 地政總署地形圖（Topographic Maps）
- 規劃署圖則（Outline Zoning Plans）
- 運輸署公共交通數據

---

## 🟡 中優先（提升用戶體驗和數據覆蓋）

### 4. Copernicus DEM（歐洲太空總署）

**用途：**
- 替代/升級 SRTM，提供 10m 或 30m 分辨率全球 DEM
- COPDEM 比 SRTM 更新（2010-2015年 vs 2000年），精度更高
- 可通過 OpenTopography 或 Copernicus 官方門戶獲取

**為什麼需要：**
- SRTM 是 2000 年的數據，20 年間香港有大量填海和地形改變（如啟德、中環填海）
- COPDEM 對城市區域的精度顯著優於 SRTM

**費用：** 免費（Copernicus 為歐盟開放數據）

**申請鏈接：** https://spacedata.copernicus.eu/

**替代方案：** 通過 OpenTopography 間接獲取（同一數據源）

---

### 5. 香港中原/美聯/28HSE 房產數據（商業 API）

**用途：**
- 接入實時房源數據（價格、面積、樓齡、成交記錄）
- 目前系統使用的是靜態數據庫，無法反映市場實時變化
- 自動填充 `year_built`、`price_per_sqft` 等字段

**為什麼需要：**
- 用戶體驗：展示「即時風水匹配」+「即時市場價格」才完整
- 商業價值：沒有實時房源數據的風水匹配系統價值有限

**費用：** 通常需商業合作（無公開免費 API）

**申請方式：**
- 中原地產：聯繫 Centaline 技術部門洽談 API 合作
- 美聯物業：聯繫 Midland 技術部門
- 28HSE：聯繫網站運營方（部分數據可通過網頁爬蟲獲取，但需遵守 robots.txt）

**替代方案：**
- 手動維護房源數據（目前做法）
- 網頁爬蟲（技術可行但法律風險需注意）

---

### 6. OpenWeatherMap / WeatherAPI

**用途：**
- 獲取香港歷史和實時氣候數據（風向、濕度、溫度）
- 進階風水分析：「風向水法」——傳統風水重視「藏風聚氣」，現代風水學可結合實際風向分析
- 季節性調整：香港夏季西南風、冬季東北風，影響「納氣」方向

**為什麼需要：**
- 雖然對基礎匹配影響不大，但對「專業風水師」用戶有吸引力
- 可區分「靜態風水」與「動態風水」（時間維度）

**費用：**
- OpenWeatherMap：每月 1000 次免費調用
- 超出後：$0.15/1000次

**申請鏈接：** https://openweathermap.org/api

---

## 🟢 低優先（錦上添花）

### 7. Google Earth Engine（衛星影像分析）

**用途：**
- 分析地表覆蓋（植被密度、水體、建築密度）
- 時間序列：觀察屋苑周邊 10 年間的環境變化（如新建築、填海）
- 生成地形陰影（Hillshade）和坡度圖，增強可視化效果

**費用：** 免費（學術/研究用途）

**申請鏈接：** https://earthengine.google.com/

**替代方案：** 本地 rasterio + matplotlib 生成坡度圖（已可實現）

---

### 8. NASA Earthdata（ASTER / SRTM Plus）

**用途：**
- ASTER Global DEM（30m，比 SRTM 覆蓋更完整，極地區域）
- SRTM Plus（填補水體區域的 SRTM，提供全球無縫 DEM）

**為什麼需要：**
- 香港沿海區域的 SRTM 有時會有水體噪點（如維港）
- SRTM Plus 對水體區域有插值處理

**費用：** 免費（需註冊 NASA Earthdata 帳號）

**申請鏈接：** https://urs.earthdata.nasa.gov/

---

## 📊 申請優先級總表

| 優先級 | API | 月費用 | 申請難度 | 核心提升 |
|--------|-----|--------|----------|----------|
| 🔴 | Google Maps Platform | $0（首$200免費） | 低 | 坐標+POI自動化 |
| 🔴 | OpenTopography | 免費 | 中 | DEM官方數據源 |
| 🔴 | data.gov.hk | 免費 | 低 | 香港權威建築/規劃數據 |
| 🟡 | Copernicus DEM | 免費 | 中 | 10m分辨率DEM |
| 🟡 | 房產數據（中原/美聯） | 商業洽談 | 高 | 實時房源+價格 |
| 🟡 | OpenWeatherMap | $0（首1000次免費）| 低 | 風向氣候風水 |
| 🟢 | Google Earth Engine | 免費 | 中 | 衛星影像分析 |
| 🟢 | NASA Earthdata | 免費 | 低 | DEM水體修復 |

---

## 🚀 推薦申請順序

**第一輪（本周）：**
1. **Google Maps Platform**（Geocoding + Places）— 立即自動化坐標和POI
2. **data.gov.hk** — 下載建築物輪廓和規劃圖則

**第二輪（下周）：**
3. **OpenTopography** — 申請正式帳號，獲取 COPDEM 30m
4. **OpenWeatherMap** — 免費，快速申請

**第三輪（持續）：**
5. 聯繫中原/美聯技術部門，洽談房產數據 API 合作
6. **Google Earth Engine** — 申請學術帳號（需說明研究用途）

---

## ⚠️ 注意事項

- **Google Maps API** 需要綁定信用卡，但 $200/月免費額度對 MVP 足夠，注意設置用量上限防止超支
- **房產數據 API** 可能需要提供商業計劃書或合作意向，CCMF 申請材料可作為信用背書
- **data.gov.hk** 部分數據需要簡單的政府帳號註冊（用香港身份證或公司註冊）
- **OpenTopography** 帳號申請時選擇「Academic/Research」用途最容易通過

---

*建議生成時間：2026-06-29*
*適用版本：風水樓 MVP v0.6.1*
