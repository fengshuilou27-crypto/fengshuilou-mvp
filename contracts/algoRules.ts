// 融合算法規則元數據（規格 research/algo-spec.md §0/§2/§3）
// 前後端共享：後端 algo.ts 填充「當前讀數 + 燈號」；前端後端未連接時仍用此表渲染規則卡（燈號灰化）。
// 誠實性原則：confidence [證實]=訪談/專欄 verbatim；[推斷]=由方法論合理適配到 ETF；[缺口]=Calvin 明言保密，用學術標準參數替代。
// level：A=可回測機制；B=流程/審計規則；C=哲學命名（禁止作為交易條件）。
export interface AlgoRuleMeta {
  id: string              // K1-K10 / S1-S11 / M1-M5（機構量化層）/ X1（剔除卡）
  name: string
  origin: 'calvin' | 'suntzu' | 'quant'
  level: 'A' | 'B' | 'C'
  confidence: '證實' | '推斷' | '缺口'
  quote: string           // Calvin 語錄 verbatim / 孫子原文
  source: string
  dataDriven: boolean     // false = 說明卡/流程卡（無市場讀數，燈號恒 na 或固定）
}

export const ALGO_RULES_META: AlgoRuleMeta[] = [
  // ---- Calvin 戰術層 K1-K10（規格 §2）----
  { id: 'K1', name: 'CTA 趨勢定方向', origin: 'calvin', level: 'A', confidence: '缺口',
    quote: '「我们做的是中高频CTA，用小时级别去判断市场涨还是跌。我们觉得它涨，我们就做多；觉得它跌，我们就做空。」',
    source: '騰訊/OKX《對話蔡嘉民》上篇 2025-11 · 其實盤均線參數保密（「吃飯的方法不能講」），本站以文獻標準 SMA200 + 6個月動量替代',
    dataDriven: true },
  { id: 'K2', name: '因子權重平均化', origin: 'calvin', level: 'A', confidence: '證實',
    quote: '「每一个指标、每一个因子的权重尽量平均。这样，如果某一个因子失效了，也不会对整个组合造成很大的影响。」',
    source: '騰訊/OKX《對話蔡嘉民》上篇 2025-11 · 融合公式 0.5/0.5，任何單一信號源權重 ≤50%',
    dataDriven: true },
  { id: 'K3', name: 'MDD 反推倉位上限', origin: 'calvin', level: 'A', confidence: '證實',
    quote: '「若最大能承受損失為10萬元，投入資金便不應大於12.5萬元。」「即使MDD是10%，也要預MDD額外2-3成空間。」',
    source: 'Patreon《一定要懂的風險管理 — MDD》2021-02-28 · cap=min(15, 6%÷MDD(1y)÷1.25)，預留25% buffer',
    dataDriven: true },
  { id: 'K4', name: 'Equity Curve 開關', origin: 'calvin', level: 'A', confidence: '證實',
    quote: '「把equity curve當成一個資產的價格。放上一個簡單移動平均線……在這均線下，那就暫時停止交易。」「天數是2到20天，表現大多都優於原本，因此overfitting機會偏低。」',
    source: 'Patreon《如何建立全天候策略？Equity curve trading有用嗎？》2023-08-17 · N=9最優、2-20穩健',
    dataDriven: true },
  { id: 'K5', name: '頂部四軌退出（止盈）', origin: 'calvin', level: 'A', confidence: '推斷',
    quote: '「我的出場策略有4大部分：1.按價格……2.按時間……3.按訊號……4.按event/macro」「分散是美德，若我總共有40顆比特幣要減持，那就分成4份。」',
    source: 'Patreon《比特幣的離場策略》2024-11-30 · [證實→推斷] ETF 簡化：浮盈≥25% 且乖離 z≥1.5 → 減 1/4 倉（價格軌+信號軌）',
    dataDriven: true },
  { id: 'K6', name: '波動率 regime 停用', origin: 'calvin', level: 'A', confidence: '證實',
    quote: '「盡量減少reversion類型的策略……這類策略需要低波動的環境才能成功執行。」',
    source: 'Patreon《波動率極低時期》2025-07-06 · VOO 20日已實現波動率 > 1年80分位 → 高波動 regime，趨勢權重升至 0.7',
    dataDriven: true },
  { id: 'K7', name: '小額漸進上線', origin: 'calvin', level: 'B', confidence: '證實',
    quote: '「确认它真的有用后，我才慢慢把它加入实盘，一块钱、两块钱地慢慢加上去。」',
    source: '騰訊/OKX《對話蔡嘉民》上篇 2025-11 · 新信號首筆 ≤2pp，2 週確認後補齊',
    dataDriven: true },
  { id: 'K8', name: '成本與容量自覺', origin: 'calvin', level: 'A', confidence: '證實',
    quote: '「滑點大於我們平均每筆盈利的話，那我就變成不能賺錢了。」「回測沒有任何成本的…你浪費電費咯。」',
    source: 'Tradveller 訪談 2023-11 / Anson Tan 訪談 · 單次建議總換手 ≤15pp；預期收益 < 3×成本(10bps) 不輸出',
    dataDriven: true },
  { id: 'K9', name: '失效判斷', origin: 'calvin', level: 'B', confidence: '證實',
    quote: '「有些策略可能会连续三个月、六个月不赚钱……我们要想，这个策略是不是失效了？我们要不要把它拿掉？」',
    source: '騰訊/OKX《對話蔡嘉民》上篇 2025-11 · 本站專家命中率已動態化（見「專家觀點庫」），此為說明卡',
    dataDriven: false },
  { id: 'K10', name: '差異化數據（哲學卡）', origin: 'calvin', level: 'C', confidence: '證實',
    quote: '「想赚别人赚不到的钱，就要看别人没有看的东西，或者别人忽略的东西。」「做別人不做的事情，你才會賺到別人沒有賺的錢。」',
    source: '騰訊/OKX《對話蔡嘉民》上篇 2025-11 · C 級哲學命名，不作交易條件；本站專家觀點聚合=「別人不看的數據」',
    dataDriven: false },

  // ---- 孫子戰略層 S1-S11（規格 §3）----
  { id: 'S1', name: '廟算門檻（始計）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「夫未戰而廟算勝者，得算多也……多算勝，少算不勝，而況於無算乎！」',
    source: '《始計篇》· fused ≥60 才允許加倉；≤40 才允許減倉；中間=持有',
    dataDriven: true },
  { id: 'S2', name: '勝兵先勝而後求戰（軍形）', origin: 'suntzu', level: 'B', confidence: '推斷',
    quote: '「是故勝兵先勝而後求戰，敗兵先戰而後求勝。」',
    source: '《軍形篇》· 上線驗證門：所有規則須標 A/B 級+文獻出處；禁止無出處規則進入引擎（本表即執行結果）',
    dataDriven: false },
  { id: 'S3', name: '先為不可勝（軍形/九地）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「昔之善戰者，先為不可勝，以待敵之可勝；不可勝在己，可勝在敵。」',
    source: '《軍形篇》· 回撤狀態機：組合回撤 >8% → 風險倉減半；>12% → 只留防守倉（TLT/BND/SGOV/GLD）；恢復後分 2-4 週加回',
    dataDriven: true },
  { id: 'S4', name: '度量數稱勝（軍形）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「兵法：一曰度，二曰量，三曰數，四曰稱，五曰勝。」',
    source: '《軍形篇》· 波動率定倉：w ∝ 1/σ(20d)，用於建議目標倉位的上下限修正',
    dataDriven: true },
  { id: 'S5', name: '求之於勢（兵勢）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「故善戰者，求之於勢，不責於人。」',
    source: '《兵勢篇》· 200DMA+TSMOM 過濾（與 K1 合併）；TSMOM 學術證據最強（Moskowitz-Ooi-Pedersen 2012）',
    dataDriven: true },
  { id: 'S6', name: '避其銳氣，擊其惰歸（軍爭）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「是故朝氣銳，晝氣惰，暮氣歸；善用兵者，避其銳氣，擊其惰歸。」',
    source: '《軍爭篇》· 乖離 z >+2σ 禁止追價加倉（等回踩）；z <−2σ 且 trend≥0 → 加倉加分 ×1.2',
    dataDriven: true },
  { id: 'S7', name: '不動如山（軍爭）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「其疾如風，其徐如林，侵掠如火，不動如山。」',
    source: '《軍爭篇》· 默認動作=持有；無廟算通過的候選 → 本週不動',
    dataDriven: true },
  { id: 'S8', name: '侵掠如火（軍爭）', origin: 'suntzu', level: 'B', confidence: '推斷',
    quote: '「其疾如風……侵掠如火……動如雷震。」',
    source: '《軍爭篇》· 廟算通過+趨勢確認 → 一次給出完整目標倉位（不拆成多次猶豫）',
    dataDriven: true },
  { id: 'S9', name: '雜於利害（九變）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「是故智者之慮，必雜於利害。」',
    source: '《九變篇》· 組合熱度：高相關組（美股系/中國系/商品系）合併計算，單組 ≤30% 總倉；超出 → 否決該組加倉',
    dataDriven: true },
  { id: 'S10', name: '主不可以怒而興師（火攻）', origin: 'suntzu', level: 'A', confidence: '推斷',
    quote: '「主不可以怒而興師，將不可以慍而致戰；合於利而動，不合於利而止。」',
    source: '《火攻篇》· 冷卻機制：近 5 份快照建議過減倉的標的，不得輸出反向加倉（複用 pipeline 冷卻概念）',
    dataDriven: true },
  { id: 'S11', name: '先知取於實證（用間）', origin: 'suntzu', level: 'B', confidence: '推斷',
    quote: '「先知者，不可取於鬼神，不可象於事，不可驗於度，必取於人，知敵之情者也。」',
    source: '《用間篇》· 數據質量投入=現代「用間」：本站字幕級抓取+全網檢索（說明卡）',
    dataDriven: false },


  // ---- 機構量化層 M1-M5（research/quant-model-synthesis.md）----
  // 來源誠實標注：四家機構（Renaissance/Citadel/Jane Street/Millennium）實盤模型全部保密，
  // 以下規則只採用公開書籍/論文/訪談中可考證的方法論，並適配到「低中頻 ETF 組合」場景；confidence 一律 [推斷]。
  { id: 'M1', name: 'Pod 熔斷（Millennium 式）', origin: 'quant', level: 'A', confidence: '推斷',
    quote: '「Every pod has tight drawdown limits — lose a few percent and your capital gets cut.」（Millennium pod 風控，公開報道）',
    source: 'Millennium pod 結構公開資料（Zuckerman《The Man Who Solved the Market》對照 + 媒體報道）· 本站適配：高相關組（S9 分組）60 日加權回撤 < -10% → 該組整體停止加倉（pod 熔斷），恢復需回撤回到 -6% 以內',
    dataDriven: true },
  { id: 'M2', name: '波動率定倉（Risk Parity / Vol Targeting）', origin: 'quant', level: 'A', confidence: '推斷',
    quote: '「Scaling positions inversely to volatility is the single most robust risk practice across macro pods.」（AQR / vol targeting 文獻共識）',
    source: 'Moreira & Muir (2017) Vol-Managed Portfolios · AQR 公開研究 · 本站適配：加倉幅度 × clamp(組合中位波動率 ÷ 個券波動率, 0.5, 1.5)，高波動標的試倉自動縮小（S4 由說明卡升級為執行規則）',
    dataDriven: true },
  { id: 'M3', name: '流動性閘門（Jane Street 式）', origin: 'quant', level: 'A', confidence: '推斷',
    quote: '「ETFs are derivatives — you only want to trade them when the underlying is liquid.」（Jane Street 公開部落格）',
    source: 'Jane Street 公開 ETF 造市文章 · 本站適配（低中頻簡化）：20 日平均成交額 ADTV < 300 萬美元 → 否決加倉；規則卡顯示全組合最低 ADTV 標的（流動性最差=執行成本最高）',
    dataDriven: true },
  { id: 'M4', name: '信號 IC 加權（Grinold 基本定律）', origin: 'quant', level: 'A', confidence: '推斷',
    quote: '「IR = IC × √breadth —— 預測力的平方根乘以獨立信號數。」（Grinold & Kahn《Active Portfolio Management》）',
    source: 'Grinold & Kahn 主動管理基本定律 · 本站適配：expert_score 按專家命中率收縮因子加權（contracts/expertWeights.ts + 學習環動態因子，夾 [0.5, 1.5]）；媒體級主題掃描不加權（因子 1.0）',
    dataDriven: true },
  { id: 'M5', name: '模型謙遜（Renaissance 式流程卡）', origin: 'quant', level: 'B', confidence: '推斷',
    quote: '「We never override the model.」（Jim Simons 公開訪談；Medallion 實盤參數與信號全部保密）',
    source: 'Zuckerman《The Man Who Solved the Market》· 本站適配：所有建議永不自動執行（人工複核優先於模型輸出）；零參數搜索；策略退役條件寫在「方法論」頁；本卡為流程審計，無交易條件',
    dataDriven: false },

  // ---- 剔除卡（規格 §3 末行）：與風控公理衝突時捨棄兵法 ----
  { id: 'X1', name: '已剔除：投之亡地然後存（九地）', origin: 'suntzu', level: 'C', confidence: '證實',
    quote: '「投之亡地然後存，陷之死地然後生。」',
    source: '《九地篇》· 明確剔除：破釜沉舟式重倉=破產路徑，與「先為不可勝」（S3）直接衝突；凡與風控公理衝突的兵法句子，一律捨棄兵法、保留風控',
    dataDriven: false },
]
