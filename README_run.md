# AI 風水樓盤匹配系統 — 本地運行指南

## 目錄結構要求

確保以下目錄結構存在：

```
workspace/
  ai-fengshui-mvp/          # 主應用
    app.py                  # FastAPI 入口
    static/                 # 前端文件
    requirements.txt
  scraper_28hse/            # 數據目錄（與主應用同級）
    data/
      estates_28hse.csv     # 屋苑數據（必須）
      listings_28hse.csv    # 樓盤數據（可選，缺失時自動創建空文件）
```

> 如數據路徑不同，代碼會自動搜索多個可能位置（同級目錄、上級目錄、運行目錄等）。

---

## 1. 安裝依賴

```bash
cd ai-fengshui-mvp
pip install -r requirements.txt
```

`requirements.txt` 內容：
```
fastapi
uvicorn
pydantic
```

---

## 2. 啟動服務

**方式 A：直接運行**
```bash
python app.py
```

**方式 B：用 uvicorn（推薦，支持熱重載）**
```bash
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

服務啟動後，控制台會顯示數據加載信息：
```
[INFO] 加载楼盘数据: .../scraper_28hse/data/listings_28hse.csv
[INFO] 楼盘数据加载完成: 357 条
[INFO] 加载屋苑数据: .../scraper_28hse/data/estates_28hse.csv
[INFO] 屋苑数据加载完成: 93 条
```

---

## 3. 訪問前端

打開瀏覽器訪問：

- **首頁**：http://localhost:8001/static/index.html
- **FXTI 測評**：http://localhost:8001/static/fxti/index.html
- **API 文檔**：http://localhost:8001/docs

---

## 4. 常見問題排查

### Q1: 啟動時顯示「未找到 estates_28hse.csv」

**原因**：數據文件不在預期路徑。  
**解決**：
1. 確認 `scraper_28hse/data/estates_28hse.csv` 存在
2. 確認它與 `ai-fengshui-mvp/` 是同級目錄（或按實際結構調整）
3. 可以用絕對路徑測試：把 CSV 放到 `ai-fengshui-mvp/` 同級的 `scraper_28hse/data/` 下

### Q2: 「楼盘数据加载完成: 0 条」或列表為空

**原因**：CSV 中的 `facing` 字段不在系統支持的坐向列表中。  
**解決**：查看 API 文檔 http://localhost:8001/docs → `/api/supported-facings` 獲取支持的坐向列表。  
確保 CSV 的 `facing` 列使用標準名稱（如 `子山午向`、`卯山酉向` 等）。

### Q3: `listings_28hse.csv` 缺失

**現象**：控制台顯示 `[WARN] listings_28hse.csv 缺失，自动创建空文件`。  
**影響**：模組3（樓盤篩選/匹配）會返回空列表，但模組1（自測）和模組2（屋苑匹配）仍可正常使用。  
**解決**：
- 如不需要樓盤級數據：無需處理，系統會自動使用空列表運行
- 如需要真實樓盤數據：運行 scraper 抓取，或手動填充 `scraper_28hse/data/listings_28hse.csv`

### Q4: 端口被佔用

```bash
# 查看佔用 8001 的進程
lsof -i :8001
# 改用其他端口
uvicorn app:app --host 0.0.0.0 --port 8002
```

### Q5: CORS 跨域問題

代碼已配置 `allow_origins=["*"]`，一般無需額外處理。  
如前端單獨部署，確保訪問 URL 與 API 地址一致。

---

## 5. 快速驗證

啟動後訪問以下 API 確認健康：

```bash
curl http://localhost:8001/api/health
```

預期返回：
```json
{"status": "ok", "version": "0.6.0", "supported_facings": 8, "modules": ["module1", "module2", "module3", "fxti"]}
```

---

## 6. 目錄結構示例（最小可運行）

```
ai-fengshui-mvp/
  app.py
  static/
    index.html
    fxti/
      index.html
      result.html
      share.html
  data/               # 算法數據（已內置）
    flying_star.py
    bazi.py
    ...
  models/             # 算法模型（已內置）
    flying_star_analysis.py
    ...
  routers/            # 路由（已內置）
    evaluate.py
    estates.py
    listings.py

scraper_28hse/
  data/
    estates_28hse.csv   # 93 條屋苑數據（必須）
    listings_28hse.csv  # 樓盤數據（可選）
```
