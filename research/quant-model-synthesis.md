# 機構量化方法綜合：Renaissance / Citadel / Jane Street / Millennium → 本系統 M1-M5 層

版本：v1.0（2026-08-01）
狀態：已實裝於 `api/algo.ts` + `contracts/algoRules.ts` + `contracts/expertWeights.ts`
適用場景：**低中頻** ETF 組合（月級信號、半年 4 次調倉、日線數據）

---

## 0. 誠實性聲明（先讀）

四家機構的實盤模型**全部保密**。本文件只採用以下公開可考證來源：

- 書籍：Zuckerman《The Man Who Solved the Market》（RenTec）、Mallaby《More Money Than God》（多家）
- 學術論文：Grinold & Kahn《Active Portfolio Management》（IR = IC × √breadth）；Moreira & Muir (2017)「Volatility-Managed Portfolios」*Journal of Finance*；Moskowitz, Ooi, Pedersen (2012)「Time Series Momentum」
- 公開訪談 / 報道：Millennium pod 風控機制（Business Insider / FT 多篇報道）、Jane Street 官方 ETF 造市技術文章與訪談、Citadel 中央風控（"central risk book"）公開描述
- Baillie Gifford / AQR 等公開研究（趨勢、波動率管理）

凡無法考證到公開來源的「內部參數」，**一律不採用**。M1-M5 全部規則的 confidence 標注為 **[推斷]** —— 即「方法論方向有公開依據，具體參數為本站適配 ETF 場景的選擇」。

反面證據同樣記錄：這些機構的超額收益大部分來自**高頻執行、融資槓桿、容量獨佔與人才密度**，而非任何單一信號公式。把「RenTec 方法」搬到月級 ETF 組合，能借鑑的只有**風控架構與研究紀律**，不是收益承諾。

---

## 1. 四家機構公開方法論提煉

### 1.1 Renaissance Technologies（大獎章基金）

| 公開可考證原則 | 來源 |
|---|---|
| 模型謙遜：不預設經濟邏輯，讓數據說話；但信號必須「統計上站得住 + 樣本外存活」 | Zuckerman 書 |
| 不人工干預模型輸出（2007、2018 回撤期也堅持系統執行） | Zuckerman 書、公開訪談 |
| 容量自覺：大獎章主動封閉在 ~$10B，超額收益依賴容量控制 | Zuckerman 書 |
| 信號衰減管理：持續淘汰失效信號，單一信號權重極小、靠數千弱信號聚合 | Zuckerman 書 |

**可遷移到本系統的部分**：
- 「數千弱信號聚合」→ 本系統 8 位專家 × 多主題的**共識矩陣**本質上就是弱信號聚合器；M4 把它升級為按信息係數（IC）加權的聚合。
- 「不人工干預」→ 本系統反方向取：**人工複核閘門**（快照建議不自動生效）。原因誠實標注：RenTec 有逐筆成交級風控系統兜底才敢不人工干預；本系統是月級信號 + 個人執行，人工複核本身就是風控層。
- 「容量自覺」→ 本系統容量約束在另一端：**信號頻寬極窄**（8 位專家的月級觀點），IR = IC × √breadth 中 breadth 天然受限，所以預期 IR 必須保守。

### 1.2 Millennium Management（多經理平台）

| 公開可考證原則 | 來源 |
|---|---|
| Pod 熔斷：單個 pod 回撤達約 -5% 警告、-7.5%~-10% 強制減倉/解散（報道值） | BI / FT 多篇報道 |
| 平台層中央風控：跨 pod 相關性、集中度、因子暴露每日監控 | 公開報道 |
| 止損紀律由平台強制執行，不依賴 pod 經理自覺 | 公開報道 |

**可遷移部分（M1 原型）**：
- 把每隻 ETF 視為一個「pod」：**60 日加權回撤 ≤ -10% 觸發熔斷**（否決加倉、建議減持）。這正是本系統「黃金 -25% 無剎車」教訓的機構化版本——原有的「60 日峰值 -15% + 30 天無新信號」管道剎車仍然保留，M1 是**純價格、不依賴信號新鮮度**的更硬一層。
- 平台層中央風控 → 本系統的 K4 equity gate（組合淨值 < 9 日均線時全局否決加倉）已承擔此角色，M 層不重複造。

### 1.3 Jane Street（ETF 造市商）

| 公開可考證原則 | 來源 |
|---|---|
| 對 ETF 的定價核心：NAV 對標 + 申購贖回機制 + 流動性分層 | Jane Street 官方技術文章 |
| 風險以「能在壓力情境下平掉」為準：流動性是頭寸規模的第一約束 | 公開訪談 / 技術文章 |
| 交易成本與衝擊成本建模是策略的一部分，不是事後附註 | 官方文章 |

**可遷移部分（M3 原型）**：
- **ADTV 流動性閘門**：20 日平均成交額 < $3M 的標的否決加倉（本組合 19 隻全部為大型 ETF，實測全部遠高於門檻——門檻是為未來新增小眾標的預置的）。
- 成本意識已在回測中（單邊 10bps × 換手），M3 把它提升為**事前否決項**而非事後統計。
- 誠實標注：Jane Street 的流動性建模是逐筆+訂單簿級別；日線 ADTV 是最粗的近似，級別 [推斷]。

### 1.4 Citadel（多策略 + 中央風控）

| 公開可考證原則 | 來源 |
|---|---|
| Central risk book：跨策略因子暴露（股票 beta、利率、商品、波動率）集中對沖 | 公開報道 / 訪談 |
| 波動率定倉：頭寸規模與實現波動率掛鉤（風險平價思想） | 學術文獻（vol targeting / risk parity 一脈） |
| 嚴格止損與降槓桿紀律（2008 年教訓後強化） | Mallaby 書 / 公開報道 |

**可遷移部分（M2 原型）**：
- **波動率定倉**：建議倉位縮放係數 = clamp(組合中位 σ / 個券 σ, 0.5, 1.5)——高波標的（IBIT、SLV 級）建議幅度自動打折，低波標的（AGG、SGOV 級）不打折。學術依據：Moreira & Muir (2017) 波動率管理組合 Sharpe 顯著改善。
- 因子暴露集中管理 → 本系統以主題層面近似（共識矩陣的「組合動作」列 + S9 組合熱度上限），不做逐因子回歸，級別 [推斷]。

### 1.5 學術底座（四家共用的公開框架）

| 框架 | 用途 |
|---|---|
| Grinold：IR = IC × √breadth | M4 的理論依據：按專家歷史 IC 加權，而非一律等權；同時誠實承認本系統 breadth ≈ 主題數，天花板明確 |
| Moreira & Muir (2017)：波動率定時 | M2 + 既有 K6 regime 的學術出處 |
| Moskowitz et al. (2012)：TSMOM | 既有 K1 趨勢層的出處（已實裝） |
| Bailey & López de Prado：回測過擬合控制 | 零參數搜索原則（已實裝於誠實聲明） |

---

## 2. M1-M5 規則映射表

| ID | 名稱 | 原型來源 | 機制（已實裝） | 級別 | confidence |
|---|---|---|---|---|---|
| M1 | Pod 熔斷 | Millennium | 60 日加權回撤 ≤ -10% → 否決該組加倉；**雙層執行**：分析層（algo.ts）+ 快照層（pipeline.ts buildSuggestions，唯一可執行出口），兩層共用 `api/podBreaker.ts` 同一套分組/加權/熔斷線 | A | 推斷 |
| M2 | 波動率定倉 | Citadel / Moreira & Muir | 加倉幅度 × clamp(中位σ/個券σ, 0.5, 1.5) | A | 推斷 |
| M3 | 流動性閘門 | Jane Street | 20 日 ADTV < $3M → 否決加倉 | A | 推斷 |
| M4 | IC 加權信號 | RenTec 弱信號聚合 / Grinold | 專家信號 × EXPERT_FACTOR（夾 [0.5, 1.5]，lambl=lam 別名，未知 id=1.0） | A | 推斷 |
| M5 | 流程卡：研究紀律 | RenTec 模型謙遜 + 容量自覺 | 不可回測流程規則（dataDriven:false）：不人工干預 vs 人工複核的取捨、容量/頻寬自覺 | B | 推斷 |

實裝位置：
- `api/podBreaker.ts` — M1 共享模組：HEAT_GROUPS 分組、windowDD、computePodStatus（分析層與快照層共用，單測 11 條鎖定邊界）
- `api/algo.ts` — M1/M2/M3 在加倉分支的閘門鏈；M1 狀態同時進 `summary`；M4 經 `expertFactor()` 作用於 expert_score
- `api/pipeline.ts` — M1 接入 buildSuggestions（唯一可執行出口）：pod 熔斷中的組否決所有加倉，note 顯性標注；行情與價格剎車層統一抓取不重複請求
- `contracts/expertWeights.ts` — EXPERT_FACTOR 表（獨立檔案，便於未來以滾動 IC 實測值更新）
- `contracts/algoRules.ts` — M1-M5 元數據（quote/source/level/confidence）
- `api/marketdata.ts` — DayClose 補 `volume?`（M3 需要 ADTV）
- 前端：`src/pages/tabs/AlgoEngine.tsx` 卡 4.5「機構量化層」

---

## 3. 低中頻適配的取捨記錄

1. **頻率**：四家原型的持倉週期從秒級（JS/CT 造市）到週級（Millennium pod）不等；本系統是月級。凡依賴日內/高頻結構的方法（訂單簿失衡、毫秒套利）**全部放棄**，只保留日線可表達的部分。
2. **槓桿**：四家全部用槓桿；本系統零槓桿。波動率定倉在無槓桿下退化成「打折」而非「放大」——所以 clamp 上界設 1.5 而非對稱放大。
3. **空頭**：Millennium/Citadel 大量依賴多空；本系統 ETF 只做多，空頭信號只能映射為「減倉/歸零」——已在共識矩陣層處理，M 層不重複。
4. **數據**：日線 OHLCV（Yahoo/網關）是全部輸入；無 intraday、無訂單簿、無持倉數據。M3 的 ADTV 是數據邊界內的最優近似。

## 4. 已知局限（前向監控項）

- M1 的 -10% 熔斷線是報道值中取較嚴一端；實測 SLV 級標的在 2026-03 白銀崩跌中會觸發（正確行為），但 IBIT 這類天然高波標的可能頻繁誤觸 → 前向追蹤 6 個月後可考慮按標的波動率分層（-10% / -1.5σ 取較寬）。
- M4 的 EXPERT_FACTOR 目前由人工復盤命中率靜態設定；真正的滾動 IC 需要 ≥12 個月的前向信號-收益對——數據積累夠之前不做動態化，避免小樣本過擬合（Bailey 警告）。
- M3 對當前 19 隻全部閒置（均為大流動性 ETF）；它是「新增小眾標的」的預置保險，不是現役規則。
