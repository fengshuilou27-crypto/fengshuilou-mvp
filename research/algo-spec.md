# 融合算法规格：Calvin-Replica × 孫子兵法 × 專家信號管道

研究輸入：`calvin_r1_text.md`（41KB）、`calvin_r2_video.md`（42KB）、`suntzu_r3_mapping.md`（44KB）。
目標項目：`/mnt/agents/output/app`（React19+Vite+Tailwind+shadcn / Hono+tRPC+Drizzle+MySQL）。

## 0. 誠實性原則（必須體現在 UI 與代碼註釋）
- 每條規則標註來源置信度：**[證實]**=訪談/專欄 verbatim；**[推斷]**=由方法論合理適配到 ETF；**[缺口]**=Calvin 明言保密（「吃飯的方法不能講」），本站用學術標準參數替代。
- 每條規則標註可驗證級別：**A 級**=可回測機制；**B 級**=流程/審計規則；**C 級**=哲學命名（禁止作為交易條件）。
- 明確剔除「投之亡地然後存」（破釜沉舟=破產路徑）。
- 展示 Bailey/López de Prado 警告：5 年日數據最多試 ~45 個變體，本站規則全部用文獻標準參數、不做參數優化，以此控制過擬合。

## 1. 三層融合架構
```
專家信號層（現有 pipeline：YouTube字幕+新聞→Kimi結構化→時間衰減→主題共識）
        │  expert_score(ticker) ∈ [-1, +1]
        ▼
Calvin 戰術層（趨勢/波動率/倉位規則 K1-K10）
        │  trend_score(ticker) ∈ [-1, +1]；倉位上限；全局閘門
        ▼
孫子戰略層（廟算/狀態機/冷卻/熱度 S1-S11）
        │  gates: 通過 / 否決 + 原因
        ▼
輸出：per-ETF {fused_score 0-100, action: 加倉/減倉/持有/止盈, target_delta_pp, 通過的層, 讀數}
```

**融合公式（K2 因子平均化的直接體現）**：
```
fused_raw = 0.5 × expert_score + 0.5 × trend_score        # 單一信號源不過半 [證實:A2]
regime_mult = 高波動 regime 時 trend 權重升至 0.7（K6：停 reversion 類）
equity_gate = 組合淨值 < 9日淨值均線 → 0.5（K4，全局降檔）
fused_score = round(50 + 50 × fused_raw × regime_mult × equity_gate)  # 0-100
```

## 2. Calvin 層規則（K1-K10）
| # | 規則 | 實現（ETF 適配） | 來源 |
|---|---|---|---|
| K1 | CTA 趨勢定方向 | trend_score = 0.5×sign(price−SMA200) + 0.5×sign(mom126)（SMA200/6個月動量，文獻標準參數 [缺口→學術替代]） | V5/A1 |
| K2 | 因子權重平均化 | 融合公式 0.5/0.5（見上）；任何單一信號源權重 ≤50% | A2 [證實] |
| K3 | MDD 反推倉位上限 | cap_i = min(15, round(可承受虧損預算6% ÷ max(MDD_i(1y),5%) × 100 / 1.25)) pp；MDD 預留 25% buffer | D1 [證實] |
| K4 | Equity Curve 開關 | 組合淨值序列（performance.json）< 其 9 日均線 → equity_gate=0.5，否決所有加倉 | D2 [證實,N=9最優,2-20穩健] |
| K5 | 頂部四軌退出 | 持倉浮盈≥25% 且乖離 z=(price−SMA20)/σ20 ≥1.5 → action=止盈，建議減 1/4 倉位（價格軌+信號軌的 ETF 簡化） | C1 [證實→推斷] |
| K6 | 波動率 regime 停用 | SPX 代理（VOO）20 日已實現波動率 > 1 年 80 分位 → 高波動 regime：reversion 類建議停用，trend 權重 0.7 | C2/B4 [證實] |
| K7 | 小額漸進上線 | 新信號首筆 ≤2pp；建議表標註「首筆試倉，2 週確認後補齊」 | E1/V5 [證實] |
| K8 | 成本與容量自覺 | 單次建議總換手 ≤15pp；預期收益 < 3×成本(10bps) 的建議不輸出 | V2/書 ch.4 [證實] |
| K9 | 失效判斷 | 信號源 3 個月負貢獻 → 權重減半（本站專家命中率已動態化，此處作說明卡） | E2 [證實] |
| K10 | 差異化數據 | 專家觀點聚合=「別人不看的數據」；說明卡 | A4 [證實] |

## 3. 孫子層規則（S1-S11 + 1 剔除）
| # | 篇目 | 原文 | 量化規則 | 級別 |
|---|---|---|---|---|
| S1 | 始計 | 多算勝，少算不勝 | 廟算門檻：fused_score ≥60 才允許加倉；≤40 才允許減倉；中間=持有 | A |
| S2 | 軍形 | 勝兵先勝而後求戰 | 上線驗證門：所有規則須標 A/B 級+文獻出處；禁止無出處規則進入引擎 | B |
| S3 | 軍形/九地 | 先為不可勝 | 回撤狀態機：組合回撤 >8% → 風險倉減半；>12% → 只留防守倉（TLT/BND/SGOV/GLD）；恢復後分 2-4 週加回 | A |
| S4 | 軍形 | 度→量→數→稱→勝 | 波動率定倉：w_i ∝ 1/σ_i(20d)，用於建議目標倉位的上下限修正 | A |
| S5 | 兵勢 | 求之於勢，不責於人 | 200DMA+TSMOM 過濾（與 K1 合併）；TSMOM 學術證據最強（MOP 2012） | A |
| S6 | 軍爭 | 避其銳氣，擊其惰歸 | 乖離率 z >+2σ → 禁止追價加倉（等回踩）；z <−2σ 且 trend≥0 → 加倉加分 ×1.2 | A |
| S7 | 軍爭 | 不動如山 | 默認動作=持有；無廟算通過的候選 → 本週不動 | A |
| S8 | 軍爭 | 其疾如風，侵掠如火 | 廟算通過+趨勢確認 → 一次給出完整目標倉位（不拆成多次猶豫） | B |
| S9 | 九變 | 雜於利害 | 組合熱度：高相關組（如 VOO/XLV/XLB 美股系；ASHR/MCHI/EWH 中國系；GLD/SLV/COPX 商品系）合併計算，單組 ≤30% 總倉；超出 → 否決加倉 | A |
| S10 | 火攻 | 主不可以怒而興師 | 冷卻機制：同一標的減倉建議後 5 個交易日內不得輸出反向加倉（複用 pipeline 冷卻邏輯，已存在 recentSuggestions） | A |
| S11 | 用間 | 先知迂直之計者勝 | 數據質量投入=現代「用間」：本站字幕級抓取+全網檢索（說明卡） | B |
| 剔除 | 九地 | 投之亡地然後存 | **明確剔除**：破釜沉舟=破產路徑，與風控公理衝突時捨棄兵法 | — |

## 4. 後端實現（api/algo.ts，新增）
- **數據**：Yahoo v8 chart `range=1y&interval=1d`，19 持倉 ETF（VOO SMH ASHR MCHI EWH GLD SLV COPX XLE XLB IFRA EWY EWT XLV VGK IBIT TLT BND SGOV）+ 組合淨值讀 public/data/performance.json；1 小時緩存；tfetch 10s；per-ticker 失敗標記，status ok/partial/unavailable（複用 quotes.ts 模式）。
- **計算**（全部 1y 日線可算，無外部依賴）：SMA200、mom126、σ20 年化、MDD(1y)、乖離 z、VOO 波動率分位（regime）、組合淨值 9 日均線、組合回撤（vs 60 日峰值，複用 brake 概念）。
- **expert_score**：從 DB 最新 snapshot 的 views→signals，用 pipeline.ts 的 ASSET_MAP 邏輯映射到 ticker，加權（decayWeight）淨值歸一化到 [-1,1]；無信號=0 並標註「專家層無新信號」。
- **引擎**：按 §1-3 計算 per-ETF fused + gates + action + target_delta_pp；輸出每條規則的當前讀數與燈號（pass/warn/fail/na）。
- **tRPC**：`algo.analyze` publicQuery（直接調用，內部緩存）。contracts/types.ts 新增：
```ts
export interface AlgoTickerReading { ticker: string; price: number; sma200: number|null; mom126: number|null; vol20: number|null; mdd1y: number|null; zscore: number|null; trendScore: number; expertScore: number; fusedScore: number; action: 'add'|'reduce'|'hold'|'trim'; targetDeltaPp: number; gates: { rule: string; passed: boolean; note: string }[] }
export interface AlgoRuleState { id: string; name: string; origin: 'calvin'|'suntzu'; level: 'A'|'B'|'C'; confidence: '證實'|'推斷'|'缺口'; quote: string; source: string; reading: string; lamp: 'pass'|'warn'|'fail'|'na' }
export interface AlgoAnalysis { asOf: string; status: 'ok'|'partial'|'unavailable'; regime: 'normal'|'highVol'; equityGateOn: boolean; portfolioDD: number|null; tickers: AlgoTickerReading[]; rules: AlgoRuleState[]; summary: string }
```

## 5. 前端（Home.tsx 新增 section「量化算法」，插入在「信號共識矩陣」之後）
1. **架構卡**：三層流程圖（專家信號層→Calvin 戰術層→孫子戰略層→建議輸出），純 JSX 橫向流程。
2. **融合信號表**：19 ETF ×（expert/trend/fused 分數、action 徽章、gates 通過數、建議調整 pp）。靜態模式（backendDown）顯示規則卡但讀數灰化。
3. **Calvin 規則庫**：K1-K10 卡片（規則名、原文語錄、來源標籤[證實/推斷/缺口]、當前讀數、燈號）。
4. **孫子兵法矩陣**：S1-S11 卡片（篇目、原文、量化規則、讀數、燈號）+ 一張**剔除卡**（投之亡地，玫瑰色，標明為何剔除）。
5. **誠實聲明卡**（琥珀色）：逆向工程局限（實盤參數保密）、A/B/C 級定義、45-變體過擬合警告、TSMOM/成本等反面證據一句話。
配色沿用現有 slate-900 深色主題；燈號：pass=emerald / warn=amber / fail=rose / na=slate。
SECTIONS 數組加「量化算法」。

## 6. Access 需求清單（最終回覆給用戶）
分「已有/免費可加/付費決定/執行層」四檔（在回覆正文中呈現，不必入代碼）。
