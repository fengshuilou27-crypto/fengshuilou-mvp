# AI 風水樓盤匹配系統 MVP v0.6

> **智尋·風水樓** — AI × 風水 × 置業匹配平台
> **技術棧：FastAPI + Uvicorn + SQLite + 原生 HTML/JS 前端**

---

## 快速開始（Step-by-Step）

### 前提條件

- **Python 3.10 或更高版本**（必需）
- **pip**（Python 包管理器，通常隨 Python 安裝）
- **瀏覽器**（Chrome / Edge / Safari 均可）

### 第一步：安裝 Python 依賴

打開終端（Windows 用 PowerShell 或 CMD，Mac 用 Terminal），進入項目目錄：

```bash
cd ai-fengshui-mvp
pip install -r requirements.txt
```

預期輸出：
```
Collecting fastapi
  Downloading fastapi-0.115.0-py3-none-any.whl
Collecting uvicorn
  Downloading uvicorn-0.32.0-py3-none-any.whl
...
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 pydantic-2.9.0
```

如果報錯 `pip 不是內部或外部命令`，請先確保 Python 已安裝並添加到系統 PATH。

### 第二步：運行後端服務

```bash
python app.py
```

**成功標誌** — 終端應顯示類似以下內容：
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

**重點**：看到 `Uvicorn running on http://0.0.0.0:8001` 才算成功。此時後端已啟動，不要關閉這個終端窗口。

### 第三步：打開前端頁面

**方式 A：直接開啟 HTML 文件（最簡單）**

用瀏覽器直接打開項目目錄下的 `static/index.html` 文件：
- Windows：雙擊 `static/index.html`，或在瀏覽器地址欄輸入 `file:///C:/Users/.../ai-fengshui-mvp/static/index.html`
- Mac：`open static/index.html`

**方式 B：通過後端服務訪問**

在瀏覽器開 `http://127.0.0.1:8001/static/index.html`

### 第四步：驗證運行

- 瀏覽器開 `http://127.0.0.1:8001/api/health` → 應返回 JSON：`{"status": "ok", "version": "0.6.0", "modules": ["module1", "module2", "module3", "fxti"]}`
- 瀏覽器開 `http://127.0.0.1:8001/docs` → 應看到 FastAPI 自動生成的 API 文檔

---

## 常見錯誤處理

| 錯誤 | 原因 | 解決方法 |
|------|------|----------|
| `端口 8001 已被佔用` | 其他程序佔用了 8001 | 修改 `app.py` 最後一行的 `port=8001` 為 `port=8080`，然後瀏覽器訪問 `http://127.0.0.1:8080` |
| `ModuleNotFoundError: No module named 'fastapi'` | 依賴未安裝 | 運行 `pip install -r requirements.txt` |
| `Python 版本過低` | Python < 3.10 | 升級到 Python 3.10+ |
| 前端表單提交後無反應 | 後端未啟動 | 確認終端有 `Uvicorn running` 輸出，且沒有關閉終端 |
| 中文顯示亂碼 | 終端編碼問題 | Windows PowerShell 運行 `chcp 65001` 切換 UTF-8 |

---

## 版本信息

- **版本**: v0.6.1
- **數據持久化**: SQLite（用戶/FXTI結果/匹配記錄持久化，重啟不丟失）
- **認證系統**: 簡易JWT Session（註冊/登入/Token）
- **八字增強**: 加入簡化版日主強弱判斷（得令/通根/生扶）
- **八宅增強**: 擴展為九宮吉凶評分（生氣/延年/天醫/伏位/五鬼/絕命/六煞/禍害）
- **更新日期**: 2026-06-17
- **核心功能**: 雙周期飛星 + 六維度風水匹配 + FXTI五行人格測評 + 雙人關係分析 + 四模組完整前端
- **權重配置**: 飛星30 / 八字20 / 八宅15 / 零正神10 / 目標15 / 區位10

## 功能模組

| 模組 | 說明 | 路由 |
|------|------|------|
| 模組1：自測住所 | 輸入樓盤資料，六維度風水評分 | `index.html` |
| 模組2：配對屋苑 | 批量匹配屋苑，返回TOP N | `module2.html` |
| 模組3：配對物業 | 篩選樓盤並匹配，支持叫買市場 | `module3.html` |
| **模組4：FXTI五行人格** | 先天八字+後天問卷，15角色原型 | `fxti/index.html` |

## FXTI 五行人格測評

FXTI（Five Elements Type Indicator）是基於五行理論的人格測評系統：

- **先天分析**：根據出生年月日時計算四柱八字，統計五行分布
- **後天問卷**：10道情境選擇題，每題5選項對應金木水火土
- **15種角色原型**：A1-A5純格（金木水火土），B1-B10複合格
- **雙人關係分析**：五行相生相剋、相似度、互補度、和諧度評分
- **專屬風水建議**：根據角色原型推薦居住方位、樓層、色彩

### FXTI API 接口

```bash
# 1. 獲取角色列表
GET /api/fxti/profiles

# 2. 計算五行人格
POST /api/fxti/calculate
Content-Type: application/json
{
  "birth_year": 1990,
  "birth_month": 5,
  "birth_day": 15,
  "birth_hour": 12,
  "gender": "male",
  "occupation": "engineer",
  "answers": [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
}

# 3. 獲取結果
GET /api/fxti/result/{fxti_id}

# 4. 雙人關係分析
POST /api/fxti/relationship
Content-Type: application/json
{
  "person_a": { "fxti_id": "fxti_0001" },
  "person_b": { "birth_year": 1992, "birth_month": 3, "birth_day": 20, "answers": [1,2,3,4,0,1,2,3,4,0] }
}
```

## 雙周期飛星

- **同運**：單一運盤分析（建造運=當運）
- **異運**：建造運盤70% + 當運盤30% 加權
- **當運缺失**：降置信度並扣5分保守處理
- **格局變化檢測**：自動檢測建造運與當運格局是否變化（如到山到向→上山下水）

## 安裝指南

### 環境要求

- Python 3.10+
- pip

### 安裝步驟

```bash
# 1. 進入項目目錄
cd ai-fengshui-mvp

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 啟動服務
python app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8001
```

### 依賴列表

```
fastapi
uvicorn
pydantic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

## 運行指南

### 啟動後端

```bash
python app.py
```

服務啟動後：
- API 文檔: http://localhost:8001/docs
- 健康檢查: http://localhost:8001/api/health

### 前端頁面

直接打開 `static/index.html` 即可使用前端界面（需後端已啟動）。

支持四個模組：
- **模組1** (`index.html`): 自測現有住所
- **模組2** (`module2.html`): 配對屋苑
- **模組3** (`module3.html`): 配對物業
- **模組4** (`fxti/index.html`): FXTI五行人格測評

## API 接口

### 風水匹配接口

```bash
# 1. 單一評估
POST /api/evaluate

# 2. 配對屋苑
POST /api/match/estates

# 3. 配對物業
POST /api/match/listings

# 4. 支持坐向查詢
GET /api/supported-facings
```

### FXTI 接口

```bash
# 1. 獲取角色列表
GET /api/fxti/profiles

# 2. 計算五行人格
POST /api/fxti/calculate

# 3. 獲取結果
GET /api/fxti/result/{fxti_id}

# 4. 雙人關係分析
POST /api/fxti/relationship
```

## 測試確認

全部模組已通過整合測試：

| 測試項目 | 狀態 |
|---------|------|
| 飛星分析（雙周期） | ✅ 通過 |
| 八字匹配（四柱） | ✅ 通過 |
| 八宅匹配 | ✅ 通過 |
| 零正神 | ✅ 通過 |
| 煞氣評估 | ✅ 通過 |
| 目標匹配 | ✅ 通過 |
| 聚合結果 | ✅ 通過 |
| FXTI計算 | ✅ 通過 |
| FXTI關係分析 | ✅ 通過 |

### 三個基準案例

| 案例 | 坐向 | 建造運 | 當運 | 飛星分 | 總分 | 格局 |
|------|------|--------|------|--------|------|------|
| 太古城 | 子山午向 | 七運 | 九運 | 29.0/40 | 55.8/100 | 到山到向 |
| 沙田第一城 | 乾山巽向 | 七運 | 九運 | 5.0/40 | 62.7/100 | 上山下水 |
| YOHO Town | 卯山酉向 | 八運 | 九運 | 23.5/40 | 62.6/100 | 雙星會向 |

## 項目結構

```
ai-fengshui-mvp/
├── app.py                  # FastAPI 主應用（含FXTI路由）
├── requirements.txt       # 依賴
├── data/                  # 數據層
│   ├── flying_star.py    # 飛星查表數據
│   ├── bazi.py           # 八字計算
│   ├── bagua.py          # 八宅數據
│   ├── sha.py            # 煞氣數據
│   ├── goal.py           # 目標數據
│   ├── zero_main_god.py  # 零正神數據
│   ├── fxti_bazi.py      # FXTI八字計算
│   ├── fxti_questionnaire.py  # FXTI問卷
│   ├── fxti_profile.py   # FXTI角色判定
│   └── fxti_relationship.py   # FXTI雙人關係
├── models/               # 分析模組
│   ├── flying_star_analysis.py
│   ├── bazi_matching.py
│   ├── bagua_matching.py
│   ├── sha_assessment.py
│   ├── goal_matching.py
│   ├── zero_main_god.py
│   └── match_result.py
├── static/               # 前端頁面
│   ├── index.html        # 模組1：自測住所
│   ├── module2.html      # 模組2：配對屋苑
│   ├── module3.html      # 模組3：配對物業
│   └── fxti/             # 模組4：FXTI
│       ├── index.html    # FXTI問卷頁
│       └── result.html   # FXTI結果頁
└── test_results/         # 測試結果
    ├── *.json            # 風水匹配測試
    └── fxti_test_samples.json  # FXTI測試樣本
```

## 重要聲明

⚠️ **本系統為 MVP 基礎版，基於互聯網公開資料碎片計算：**

- 所有模組標註 `data_source` + `confidence` + 免責聲明
- 不輸出權威判斷，只提供分數區間 +「需專業師傅確認」
- 具體入住/投資等重大決策建議諮詢專業風水師傅進行實地勘察

## 雙軌路線

- **基礎版**（當前）：互聯網查表硬編碼，快速驗證
- **專業版/算法包**（未來）：師傅工作流程，算法推導排盤

## 開發者

- **KimiClaw Desktop**: 開發
- **風水claw**: 風水審核

---

*智尋·風水樓 MVP v0.6 | 2026-06-16*
