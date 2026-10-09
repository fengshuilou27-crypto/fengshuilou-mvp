# 孫子兵法 → 股票/ETF 量化交易系統映射研究報告（R3）

> 研究範圍：十三篇逐篇提取可量化原則 → 可編碼規則對照表 + 偽代碼 + 業界已有框架盤點 + 批判性評估 + 最小可行規則集（MVP）。
> 方法：28 組中英文搜索 + 原文逐篇核對（中國哲學書電子化計劃 ctext.org、UCSD Giles 英譯對照本、百度百科）。每條映射標註「可回測性」：✅ 可直接回測驗證 / ⚠️ 流程·執行·方法論層（可驗證但非 alpha）/ ❌ 哲學裝飾（不可證偽，僅作文化註腳）。
> 誠實聲明：**兵法原文本身不是交易策略**。本表的可驗證內容全部來自現代量化實踐（趨勢跟蹤、波動率定倉、期望值、回撤控制），兵法只提供組織框架與命名。詳見「批判性評估」。

---

## 一、十三篇 → 量化規則對照總表

### 第 1 篇 始計篇（Laying Plans）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 1.1 | 「夫未戰而廟算勝者，得算多也；未戰而廟算不勝者，得算少也。多算勝，少算不勝，而況於無算乎！」[^1^] | **廟算**：下單前先算勝率 | 下單前多因子評分 + 期望值門檻：綜合評分未達閾值或期望值 ≤ 0 則不交易 | score = Σwᵢ·fᵢ（動量、趨勢、波動 regime、估值/利差），θ 為歷史分位數；E = p·W̄ − (1−p)·L̄ > 0（Van Tharp expectancy [^30^]） | ✅ |
| 1.2 | 「故經之以五事，校之以計，而索其情：一曰道，二曰天，三曰地，四曰將，五曰法」[^1^] | **五事**：系統性盡職調查 | 固定資料管道：道=策略假設與適用市場、天=宏觀/流動性 regime、地=市場結構與標的流動性、將=自身執行與風控能力、法=交易規則與成本 | 每月/每季 checklist 自動生成報表 | ⚠️ 流程層 |
| 1.3 | 「強而避之……攻其無備，出其不意」[^1^] | **避強**：不與強勢對抗 | 不逆大趨勢開倉；不在無防護下暴露於重大事件 | 只做與 SMA200 同向的倉位（long-only 系統即「價格 > SMA200 才允許做多」）；FOMC/財報等重大事件前降倉或不開新倉 | ✅ |

### 第 2 篇 作戰篇（Waging War）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 2.1 | 「其用戰也勝，久則鈍兵挫銳……故兵聞拙速，未睹巧之久也；夫兵久而國利者，未之有也」[^2^] | **兵貴速，不貴久**：曠日持久必損 | 控制持有期與換手成本；時間止損（time stop）；資金不沉澱於無效倉位 | 月頻調倉為主（對齊動量信號半衰期約 3 個月 [^36^]）；回測成本 ≥ 5–10 bps/邊；time-stop：持倉 N 期未達預期收益即退出 | ✅ |
| 2.2 | 「故不盡知用兵之害者，則不能盡知用兵之利也」[^2^] | **先知害，後知利**：先算下行 | 任何倉位先定止損與最大回撤預算，再定倉位大小與收益目標（risk-first sizing） | stop 距離 d → size = equity × r / d，r = 0.5–2%（Minervini 同法 [^28^][^29^]） | ✅ |
| 2.3 | 「故兵貴勝，不貴久」[^2^] | **求勝不求久**：別跟虧損倉位「談戀愛」 | 弱勢倉位機械輪出：排名跌出前 N 或趨勢破位即換倉，不攤平、不戀戰 | RS 排名月度更新；跌破 SMA50/200 或 ATR 追蹤止損觸發即出 | ✅ |

### 第 3 篇 謀攻篇（Attack by Stratagem）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 3.1 | 「知彼知己，百戰不殆」[^3^] | **知己**：自身約束量化 | 硬性風險預算：單筆風險、組合總風險、相關性分組上限、回撤降倉曲線 | per-trade risk 0.5–2% equity；portfolio heat ≤ 5–6%；高相關組（如股票 ETF 同組）合併計算敞口；回撤每 −10% 倉位 −20%（海龜規則 [^24^]） | ✅ |
| 3.2 | 「知彼知己，百戰不殆」[^3^] | **知彼**：對手/標的畫像 | 可交易宇宙篩選：流動性、波動率、趨勢性、相關性畫像後才納入 | ADV（成交額）下限、ATR%、ADX、與組合現有持倉的相關係數上限 | ✅ |
| 3.3 | 「不戰而屈人之兵，善之善者也」「上兵伐謀」[^3^] | **不戰**：最好的仗是不用打的仗 | 預設倉位 = 防守（現金/短債/總合債券），僅在信號出現時暴露風險；收益主要來自「不虧」而非「戰勝」 | dual momentum 的防守腿：信號轉負 → 100% AGG/BIL [^37^] | ✅ |
| 3.4 | 「知可以戰與不可以戰者勝」（知勝有五）[^3^] | **知可不戰**：會空手 | 無信號/低評分期持幣觀望；現金是合法倉位 | 信號評分 < θ → 該部分資金停泊於短債 ETF | ✅ |

### 第 4 篇 軍形篇（Tactical Dispositions）— 全系統最重要一篇

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 4.1 | 「昔之善戰者，先為不可勝，以待敵之可勝；不可勝在己，可勝在敵」[^4^] | **先為不可勝**：先立於不敗 | 回撤控制狀態機：先保證不爆倉，再等待市場給機會 | DD ≥ 10% → 風險倉 × 0.5；DD ≥ 20% → 風險倉歸零轉防守資產；權益創新高後分階段加回（對應 Buffett「Rule #1: never lose money」[^49^]、Minervini risk-first [^28^]、海龜回撤降倉 [^24^]） | ✅ |
| 4.2 | 「是故勝兵先勝而後求戰，敗兵先戰而後求勝」[^4^] | **先勝後戰**：先驗證再上場 | 策略上線前統計門檻：樣本外 Sharpe ≥ 0.5、Deflated Sharpe Ratio ≥ 0.95、交易數 ≥ 100；盤前 expectancy gate：E ≤ 0 的訊號不下單 | DSR（Bailey & López de Prado 2014 [^45^]）、PBO/walk-forward [^46^]；E = p·W̄ − (1−p)·L̄ [^30^] | ✅ |
| 4.3 | 「兵法：一曰度，二曰量，三曰數，四曰稱，五曰勝」「故勝兵若以鎰稱銖，敗兵若以銖稱鎰」[^4^] | **度量數稱勝**：倉位由量化的稱量推出 | 倉位 = f(風險預算, 波動率) 的機械公式；只在賠率懸殊（以鎰稱銖）時進場 | unit = equity × r / ATR(20)；risk:reward ≥ 1:2 才進場 | ✅ |

### 第 5 篇 兵勢篇（Energy）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 5.1 | 「凡戰者，以正合，以奇勝」[^5^] | **奇正**：正兵相持、奇兵制勝 | 核心–衛星結構：正 = 70–80% 戰略配置（股/債/金風險平價）；奇 = 20–30% 戰術動量/擇時倉位 | 衛星倉位上限硬編碼；奇兵虧損不影響正兵 | ✅ |
| 5.2 | 「故善戰者，求之於勢，不責於人」「故善戰人之勢，如轉圓石於千仞之山者，勢也」[^5^] | **任勢**：靠勢不靠人（不考驗主觀判斷） | 時序動量跟勢：資產自身 12 個月收益 > 0（或 > 短債）且價格 > SMA200 才持有風險倉；否則轉防守 | TSMOM：12M lookback、月度再平衡（Moskowitz–Ooi–Pedersen 2012，58 個市場、Sharpe≈1.0 [^34^][^35^]）；10 個月均线法（Faber 2007 [^35^]） | ✅ 學術支持最強的一條 |
| 5.3 | 「是故善戰者，其勢險，其節短；勢如彍弩，節如發機」[^5^] | **節短**：蓄勢後一觸即發 | 信號觸發即機械執行（T+1 開盤/收盤成交），不猶豫、不偷跑、不人工干預 | 執行延遲固定為 1 個交易日並在回測中如實建模 | ⚠️ 執行層 |

### 第 6 篇 虛實篇（Weak Points and Strong）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 6.1 | 「夫兵形象水……兵之形，避實而擊虛」[^6^] | **避實擊虛**：打弱點，不碰強點 | 橫截面相對強弱輪動：持有 RS 最強的前 N 檔 ETF，迴避後段（「虛」= 資金尚未流入的強勢起點 / 「實」= 擁擠交易） | 6M/12M 動量排名，月度調倉，top 2–3 檔等權或波動率倒數加權 [^42^] | ✅ |
| 6.2 | 「故兵無常勢，水無常形；能因敵變化而取勝者，謂之神」[^6^] | **無常勢**：因敵變化 | 參數自適應 / regime 切換：趨勢市用趨勢子策略、震盪市用均值回歸或減倉；參數 walk-forward 再估計 | ADX(14) > 25 = 趨勢、< 20 = 震盪 [^39^]；ATR 分位數（1–2 年窗口）判斷波動 regime [^39^]；200DMA + 斜率雙投票 [^39^] | ✅（但屬過擬合高風險區，需 DSR 把關） |
| 6.3 | 「故善戰者，致人而不致於人」[^6^] | **致人**：牽著對手走，不被牽著走 | 執行主動權：限價單/固定時點成交，不追價、不被新聞與盤中波動牽動 | 固定調倉日；禁用市價追單；事件日禁止手動加單 | ⚠️ 執行層 |

### 第 7 篇 軍爭篇（Maneuvering）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 7.1 | 「是故朝氣銳，晝氣惰，暮氣歸；善用兵者，避其銳氣，擊其惰歸」[^8^] | **避銳擊惰**：不追銳氣，等其衰竭 | 不追暴漲、等回調：順大勢、逆小勢的入場 | bias = P/SMA20 − 1 > +2σ 時禁止追價；等回踩 SMA20/50 或 RSI(3) < 20 再入場；長期趨勢向上 + 短期超賣 = 買點 | ✅ |
| 7.2 | 「其疾如風，其徐如林，侵掠如火，不動如山，難知如陰，動如雷震」[^8^] | **風林火山**：快慢收放按狀態 | 倉位隨趨勢狀態調節：趨勢確認時果斷加倉（火/風），震盪不明時減倉觀望（山/林） | ADX > 25 且 200DMA 斜率向上 → 允許加倉至滿配；ADX < 20 → 倉位 × 0.5 或觀望 | ✅ |
| 7.3 | 「軍爭之難者，以迂為直，以患為利」[^8^] | **以迂為直**：繞路反而是直路 | 接受分批建倉的短期落後，換取更好的成本與確認度 | 首倉 1/3，信號確認（價格越過關鍵位/站穩均线 N 日）後加至全倉 | ✅ |

### 第 8 篇 九變篇（Variation in Tactics）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 8.1 | 「途有所不由，軍有所不擊，城有所不攻，地有所不爭，君命有所不受」[^7^] | **有所不為**：明確的不做清單 | 負面清單（universe 過濾）：不交易槓桿/反向 ETF、流動性差、費率高、跟蹤誤差大者；規則外的「機會」一律不做 | 費率 > 0.5% 剔除；ADV 低於閾值剔除；偏離 NAV 過大剔除 | ✅ |
| 8.2 | 「無恃其不來，恃吾有以待也；無恃其不攻，恃吾有所不可攻也」[^7^] | **有以待之**：不靠僥倖，靠準備 | 常設防守機制，不依賴「不會崩盤」的假設：始終保留防禦資產 + 高波動時自動降槓桿 | 防禦腿 20–40%（短債/長債/黃金）；VIX > 30 或組合實現波動 > 目標 × 1.5 → 總風險倉 × 0.5（vol targeting [^32^][^33^]） | ✅ |
| 8.3 | 「故將有五危：必死可殺，必生可虜，忿速可侮，廉潔可辱，愛民可煩」[^7^] | **五危**：將帥的心理弱點 | 交易心理偏差清單：魯莽重倉（必死）、過度避險（必生）、易怒復仇交易（忿速）、愛面子不止損（廉潔）、對持倉產生感情（愛民）→ 對沖方法 = 全機械執行 | — | ❌ 哲學層（但對應的行為偏差可用系統化執行消除） |
| 8.4 | 「是故智者之慮，必雜於利害」[^7^] | **雜於利害**：利中見害、害中見利 | 每筆交易進場前寫明 bear/base/bull 三情境與對應動作；期望收益/期望虧損 ≥ 2 | R-multiple 框架：平均盈 R̄⁺ 與平均虧 R̄⁻ 的比值 [^30^] | ⚠️ 流程層 |

### 第 9 篇 行軍篇（The Army on the March）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 9.1 | 「兵非貴益多也，惟無武進，足以併力、料敵、取人而已」[^9^] | **併力料敵**：兵不在多，在集中與判斷 | 持倉集中上限；不盲目加倉（武進） | 同時持有 ≤ 5–8 檔；單一標的權重上限 25–30%；加倉必須由規則觸發 | ✅ |
| 9.2 | 「敵近而靜者，恃其險也……鳥起者，伏也；獸駭者，覆也」（相敵三十二徵候）[^9^] | **相敵**：從細微跡象讀敵情 | 市場內部結構監測：寬度、量能、波動率期限結構作為 regime 確認信號 | % 成分股 > SMA200（市場寬度）；成交量配合度；VIX 期限結構倒挂警示 | ✅（半定量） |
| 9.3 | 「令之以文，齊之以武，是謂必取」[^9^] | **文武齊一**：紀律一致 | 同一套規則對所有倉位一視同仁，無例外條款 | — | ⚠️ 治理層 |

### 第 10 篇 地形篇（Terrain）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 10.1 | 「地形有通者、有掛者、有支者、有隘者、有險者、有遠者」[^10^] | **六形**：六種地形六種打法 | 市場結構分類對應打法：趨勢市 → 跟勢滿配；區間市 → 均值回歸+減倉；高波動危機市 → 防守；每類預設子策略與倉位上限 | regime 分類器（SMA200±斜率 / ADX / 波動率分位）輸出 3–4 狀態 [^39^] | ✅ |
| 10.2 | 「知彼知己，勝乃不殆；知天知地，勝乃可全」[^10^] | **知天知地**：宏觀 + 結構全知 | 宏觀環境層納入倉位乘數：利率方向、信用利差、VIX 水平 | VIX > 30 → × 0.5；信用利差快速走闊 → × 0.75；10Y 利率上行且價格動量轉負 → 債券腿縮短久期 | ✅ |
| 10.3 | 「故戰道必勝，主曰無戰，必戰可也；戰道不勝，主曰必戰，無戰可也」[^10^] | **規則優先於命令** | 系統信號優先於任何人工判斷；人工不得覆蓋系統（斷線保護例外） | — | ⚠️ 治理層 |

### 第 11 篇 九地篇（The Nine Situations）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 11.1 | 「散地則無戰，輕地則無止，爭地則無攻……圍地則謀，死地則戰」[^11^] | **因地制宜**：所處之地決定打法 | 依組合所處狀態調倉（與 4.1 狀態機一體兩面）：試錯期輕倉（輕地）→ 主升重倉（爭地）→ 高位滯脹減碼（圍地）→ 破位清倉（死地） | 以 DD 深度與趨勢狀態定義狀態機：DD < 5% 全倉；5–10% × 0.75；10–20% × 0.5；> 20% 歸零 [^24^] | ✅ |
| 11.2 | 「是故始如處女，敵人開戶；後如脫兔，敵不及拒」[^11^] | **處女脫兔**：靜如處女，動如脫兔 | 平時低倉觀望；高質量信號出現時快速集中倉位 | 倉位 = f(信號強度)：score 前 10% 分位的信號給滿倉，後段信號給半倉或不交易 | ✅ |
| 11.3 | 「兵之情主速，乘人之不及」[^11^] | **兵情主速** | 信號有時效，過期作廢；再平衡按時執行不拖延 | 信號有效期限定（如動量信號 1 個月）；月末調倉 T+1 完成 | ✅ |
| 11.4 | 「投之亡地然後存，陷之死地然後生」[^11^] | **死地而後生** | ⚠️ **危險類比，明確不映射**：交易中「破釜沉舟式重倉」= 破產路徑，直接違反 4.1「先為不可勝」。僅可作為理解對手盤被逼空時行為的註腳 | — | ❌ 剔除 |

### 第 12 篇 火攻篇（The Attack by Fire）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 12.1 | 「主不可以怒而興師，將不可以慍而致戰；合於利而動，不合於利而止」[^12^] | **不以怒興師**：杜絕情緒化交易 | 冷卻機制：止損後同標的禁止立即重開；日虧損達上限當日停止開新倉 | 止損觸發 → 同標的冷卻 5–10 個交易日；日組合虧損 ≥ 2% → 當日不再開倉 | ✅（風控層） |
| 12.2 | 「非利不動，非得不用，非危不戰」[^12^] | **非利不動**：沒有邊際不動手 | 成本門檻：預期收益必須顯著大於交易成本才交易 | E(trade) ≥ 2 ×（佣金 + 滑點 + 稅）；信號強度低於閾值不交易 | ✅ |
| 12.3 | 「行火必有因……發火有時，起火有日」[^12^] | **發火有時**：特殊武器等特殊時機 | 高風險工具（槓桿、期權、集中倉位）只在特定 regime 啟用 | 僅在低波動 + 趨勢確認 regime 允許放大倉位上限 | ✅（半） |

### 第 13 篇 用間篇（The Use of Spies）

| # | 原文 | 原則 | 量化規則 | 指標與參數 | 可回測性 |
|---|------|------|----------|------------|----------|
| 13.1 | 「先知者，不可取於鬼神，不可象於事，不可驗於度，必取於人，知敵之情者也」[^13^] | **先知取於實證**：預知不靠占卜 | 只用可量化、可驗證的數據與信號；杜絕不可證偽的「玄學指標」與故事驅動交易 | 每個信號必須能寫成可回測的函數；不能回測的信號不進系統 | ⚠️ 方法論 |
| 13.2 | 「相守數年，以爭一日之勝……而愛爵祿百金，不知敵之情者，不仁之至也」[^13^] | **捨得投入情報** | 數據質量優先投入：復權價格、倖存者偏差校正、費用與滑點建模、多源校驗 | 資料 pipeline 驗收標準；回測必須含交易成本與停滯期 | ⚠️ 方法論 |

---

## 二、核心規則偽代碼（可直接編碼）

以下偽代碼為 Python 風格，假設輸入為日頻 OHLCV。參數為業界常用預設值（海龜[^24^][^26^]、TSMOM[^34^]、vol targeting[^32^]、Minervini[^28^][^29^]），**上線前必須經 4.2 的驗證門檻**。

### P1. 廟算門檻（1.1）：下單前評分 + 期望值檢查
```python
def miao_suan_gate(asset, ctx):
    # 多因子評分（例：動量、趨勢、波動 regime）
    score = (0.5 * zscore(mom(asset, 126))           # 6M 動量
           + 0.3 * zscore(mom(asset, 252))           # 12M 動量
           + 0.2 * trend_strength(asset))            # ADX 標準化
    if score < THETA:                                # THETA = 歷史 60 分位
        return REJECT
    # 期望值檢查（用該子策略近 100+ 筆交易統計）
    p, avg_win, avg_loss = strategy_stats(ctx)       # 勝率、平均盈、平均虧
    expectancy = p * avg_win - (1 - p) * avg_loss    # Van Tharp [^30^]
    if expectancy <= 2 * (commission + slippage):    # 兼顧 12.2 成本門檻
        return REJECT
    return ACCEPT
```

### P2. 先為不可勝（4.1 + 11.1）：回撤狀態機
```python
def drawdown_throttle(equity_curve):
    dd = 1 - equity_curve / equity_curve.cummax()
    if dd < 0.05:   risk_mult = 1.00    # 全倉
    elif dd < 0.10: risk_mult = 0.75
    elif dd < 0.20: risk_mult = 0.50    # 海龜：每 -10% DD 砍 20% 倉位 [^24^]
    else:           risk_mult = 0.00    # 風險倉歸零，全轉防守資產
    return risk_mult
# 恢復規則：權益重新站上 20 日高點後，分 2-4 週加回，不一次補滿
```

### P3. 勝兵先勝（4.2）：策略上線前驗證門檻
```python
def validation_gate(backtest):
    ok = (backtest.oos_sharpe >= 0.5
          and backtest.deflated_sharpe_ratio(n_trials=N_TRIALS_TESTED) >= 0.95  # [^45^]
          and backtest.n_trades >= 100
          and backtest.pbo_cscv < 0.5)                 # 過擬合機率 [^46^]
    return ok
# MinBTL 自查：5 年日資料最多試 ~45 個策略變體，超出即不可信 [^44^]
```

### P4. 度量數稱勝（4.3）：ATR 定倉
```python
N = ATR(high, low, close, 20)                        # 海龜的 N [^26^]
def unit_size(equity, n, dollar_per_point=1.0, risk_pct=0.01):
    dollar_vol = n * dollar_per_point
    return floor((equity * risk_pct) / dollar_vol)   # 1 個 unit = 1N 波動 ≈ 1% 權益
# ETF 版：shares = floor(equity * risk_pct / (2 * ATR))，止損距離 2×ATR
```

### P5. 求之於勢（5.2）：TSMOM + 200DMA regime filter
```python
def trend_regime(asset):
    ts_mom   = price[-1] / price[-253] - 1           # 12M 時序動量 [^34^]
    above_ma = price[-1] > SMA(close, 200)           # Faber/PTJ 長線過濾 [^35^][^40^]
    return RISK_ON if (ts_mom > 0 and above_ma) else RISK_OFF
# RISK_OFF → 該倉位轉短債/總合債券 ETF（BIL/AGG），即「不戰而屈人之兵」的防守腿 [^37^]
```

### P6. 兵無常勢（6.2 + 7.2）：regime 切換與倉位乘數
```python
def regime_multiplier(asset):
    adx = ADX(high, low, close, 14)
    ma_slope = SMA200[-1] > SMA200[-21]              # 200DMA 一個月前比較 [^39^]
    vol_pct = percentile_rank(realized_vol(20), window=504)  # 2 年分位
    if adx > 25 and ma_slope:      return 1.0        # 趨勢 regime：滿配，允許加倉
    if adx < 20:                   return 0.5        # 震盪 regime：減半觀望（不動如山）
    if vol_pct > 0.90:             return 0.5        # 極端波動：降槓桿（有以待之 8.2）
    return 0.75
```

### P7. 避其銳氣（7.1）：不追高，順大勢逆小勢入場
```python
def entry_filter(asset):
    bias = price[-1] / SMA(close, 20) - 1
    if bias > 2 * rolling_std(bias, 252):            # 乖離過大 = 銳氣正盛
        return WAIT                                   # 不追價
    pullback = RSI(close, 3) < 20 or near(SMA(close, 20), tol=0.5*ATR)
    return ENTER if (trend_regime(asset) == RISK_ON and pullback) else WAIT
```

### P8. 其疾如風（7.2 + P6）：趨勢中金字塔加倉
```python
# 海龜式加倉（僅在趨勢 regime 啟用）
if regime == TREND and price >= last_entry + 0.5 * N:
    add(1 * unit);  n_units += 1
    stop = last_entry - 2 * N                        # 全體 unit 止損上移至新 2N [^24^]
    if n_units >= 4: freeze_adds()                   # 單市場最多 4 units
```

### P9. 避實擊虛（6.1）：相對強弱 ETF 輪動
```python
def monthly_rotation(etf_universe):
    mom = {e: adj_close[e][-1] / adj_close[e][-127] - 1 for e in etf_universe}  # 6M
    top3 = sorted(mom, key=mom.get, reverse=True)[:3]
    weights = {e: (1/3) * (TARGET_VOL / ann_vol(e, 20)) for e in top3}  # 波動率倒數
    weights = {e: w for e, w in weights.items() if mom[e] > 0}          # 絕對動量閘門
    cash = 1 - sum(weights.values())                 # 不補滿，防守停泊 [^42^]
    return weights, cash
```

### P10. 無恃其不來（8.2）：波動率目標
```python
def vol_target_weight(asset, target_vol=0.10):       # 組合年化目標波動 10%
    cur_vol = realized_vol(asset, 20) * sqrt(252)
    w = clip(target_vol / cur_vol, 0, 1.0)           # 波動翻倍 → 倉位減半 [^32^][^33^]
    return w
# 組合層：總風險倉 = min(個別權重加總, 1) ，每週再平衡一次避免過度交易
```

### P11. 主不可以怒而興師（12.1）：冷卻機制
```python
def cooldown_ok(asset, today):
    last_stop = trade_log.last_stop_out(asset)
    if last_stop and (today - last_stop.date).days < 5:   # 止損後 5 日冷卻
        return False
    if daily_pnl(today) <= -0.02 * equity:                # 日虧 2% 停止開新倉
        return False
    return True
```

### P12. 知彼知己（3.1）：組合熱度與相關性上限
```python
def portfolio_heat_check(new_trade):
    heat = sum(open_risk_dollars) / equity            # 所有未平倉止損風險加總
    if heat + new_trade.risk / equity > 0.06:         # 組合熱度 ≤ 6%
        return REJECT
    for pos in open_positions:
        if abs(corr(new_trade.asset, pos.asset, 60)) > 0.7:
            if combined_risk(new_trade, pos) > 0.02:  # 高相關合併計算
                return REJECT
    return ACCEPT
```

---

## 三、業界已有的「Sun Tzu × 交易」框架與書籍

### 3.1 直接以孫子兵法為框架的出版物
| 來源 | 內容 | 性質評估 |
|------|------|----------|
| Dean Lundell, *Sun Tzu's Art of War for Traders and Investors*, McGraw-Hill, 1997 [^14^][^15^] | 越戰退伍軍人出身的交易員，把兵法逐章對應到股票/商品/債券/外匯交易 | 最早也最常被引用的兵法交易書；**個人經驗敘事為主，無公開可驗證的量化績效** |
| 李國平《孫子兵法與貨幣戰爭：外匯期貨股票經典戰例》，北京大學出版社，2011 [^16^] | 系統工程博士所著，按十三篇分章、每章兵法思想 + 金融案例對照，提出「四叉一」技術組合 | 中文学術出版社出版，屬案例詮釋型，非可回測系統 |
| 《冷眼孫子股市兵法》 [^17^] | 以「避實擊虛找被忽視機會、奇正相生控風險」等對應股市 | 大眾讀物 |
| 部落格 *Stock Investing with Sun Tzu Art of War* [^18^] | 新加坡作者自 1993 年投資經驗出發，逐篇（勢/虛實/軍爭/九變/行軍）翻譯為投資原則；明確聲明是個人詮釋 | 散戶經驗談；其「九變 → 五個不為清單」「軍爭 → 不追公告後暴漲股」等對應與本報告一致 |
| 雪球《基于〈孙子兵法〉构建年化50%投资系统的核心逻辑框架》 [^19^] | 「五維評估」選股 + 「三三制」倉位（防禦 30%/進攻 50%/機動 20%）+ 奇正組合 | **標題黨（年化 50% 無實盤證據）**，但「正兵/奇兵分層 + 防禦/進攻/機動分倉」的結構可借鑑 |
| 技術分析博物館《〈孙子兵法〉13篇与股市应用》 [^20^] | 十三篇逐篇對應 A 股實戰案例 | 敘事型；其九地篇「行情初期輕倉→主升重倉→高位減倉→破位清倉」= 本報告 11.1 狀態機 |
| 雪球/新浪專欄《孫子兵法與投資：先為不可勝，以待市場之可勝》 [^21^][^22^] | 形篇逐句詮釋：先搭建「不可勝之形」（無永久性虧損），再等待市場給機會 | 價值投資視角的正確解讀，與 Buffett 安全邊際互通 |
| 《外匯交易三部曲》PDF [^23^] | 直言「孫子兵法講的是交易：用多少資源換多少資源 = 盈虧比」；批評 Livermore 違背「先為不可勝」故結局悲慘 | 民間交易員詮釋，觀點敏銳但無系統驗證 |

### 3.2 不掛兵法之名、但機制完全對應的成熟體系（真正可驗證的部分）
| 體系 | 對應兵法原則 | 關鍵機制 |
|------|--------------|----------|
| **海龜交易法則**（Dennis/Eckhardt 1983，Curtis Faith 公開）[^24^][^25^][^26^][^27^] | 度量數稱勝（4.3）、其疾如風（7.2）、先為不可勝（4.1） | Unit = equity×1% / ATR(N)；每 +0.5N 加一單位、最多 4 單位；止損 2N；回撤每 −10% 砍倉 20%；相關市場合併敞口上限 |
| **Mark Minervini SEPA**（兩屆美國投資冠軍）[^28^][^29^] | 先知害後知利（2.2）、先為不可勝（4.1）、避銳擊惰（7.1） | 「Line in the sand」單筆止損 ≤ 8%；從風險倒推倉位（1% 風險 ÷ 8% 止損 = 12.5% 倉位）；交易順利才加碼（progressive exposure）；+2R 後止損移至保本 |
| **Van Tharp**（《Trade Your Way to Financial Freedom》）[^30^][^31^] | 廟算（1.1）、雜於利害（8.4） | expectancy = p·W̄ − (1−p)·L̄；R-multiple 分布；「倉位管理比進場訊號重要」；30% 勝率也能有正期望 |
| **凱利公式 / 分數凱利** [^32^] | 度量數稱勝（4.3） | f* = W − (1−W)/R；實務用 1/4–1/2 凱利並受硬風控上限約束 |
| **波動率目標 / 風險平價** [^32^][^33^] | 有以待之（8.2）、水無常形（6.2） | w = σ_target / σ_current；逆波動率加權使各資產風險貢獻相等；研究顯示可降低最大回撤約 25% [^33^] |
| **時序動量 / 趨勢跟蹤（學術）** [^34^][^35^][^36^] | 求之於勢（5.2）、不動如山（7.2） | Moskowitz–Ooi–Pedersen (2012)：12M lookback 在 58 個期貨市場顯著，分散組合 Sharpe ≈ 1.0，極端行情中表現最好（crisis alpha）；Hurst–Ooi–Pedersen (2017) 回溯至 1880 年每個十年皆為正 [^34^]；Faber (2007) 10 月均线擇時大幅降低回撤 [^35^] |
| **Dual Momentum / GEM**（Antonacci 2014）[^37^][^38^] | 不戰而屈人之兵（3.3）、避實擊虛（6.1） | 絕對動量（SPY 12M > 短債）決定股/債切換，相對動量（SPY vs VEU）決定持有哪個；月度調倉，回測 Sharpe ≈ 0.98 |
| **200DMA regime 共識**（Paul Tudor Jones 等）[^39^][^40^][^41^] | 強而避之（1.3）、知天知地（10.2） | 「價格在 200 日均線之上/之下」作為最簡單的多空總開關；ADX > 25 趨勢、< 20 震盪 |

---

## 四、批判性評估：哪些是裝飾、哪些可驗證

### 4.1 把兵法套到交易的四個常見謬誤
1. **過度類比（false analogy）**：市場不是有意志的「敵人」，不會「銳氣」「惰歸」；你的對手盤是無數匿名參與者的統計集合。「擊敗市場」的戰爭敘事會誘發過度交易與對抗心態——而兵法原作最強調的恰恰是**不打**（不戰而屈人之兵、先為不可勝）。諷刺的是，多數「兵法交易」文章用它來包裝更激進的交易，方向正好相反。
2. **後見之明 / 敘事謬誤**：兵法原文足夠模糊，任何事後結果都能套入（PTT 軍事版的批評一針見血：「是把現狀代回去說你看孫武說過這句話，但這基本上就是馬後炮」[^47^]）。同一句「兵貴勝不貴久」既可解讀為短線快進快出，也可解讀為別戀戰套牢——**兩個相反的操作都能引用同一句原文，這就是不可證偽的定義**。
3. **倖存者與權威偏差**：Lundell 的書、各類「年化 50% 孫子系統」[^19^] 都沒有公開可驗證的實盤記錄。Buffett 的「Rule #1: never lose money」同樣被批評為不可照搬——普通人沒有 Berkshire 的永久資本與浮存金，照抄口號只是「穿上原則的戲服」[^48^]。
4. **驗證負債（回測過擬合）**：一旦把 13 篇 × 每篇 2–3 條原則全部參數化，策略變體數爆炸，挑出的「最優組合」幾乎必然是噪音。Bailey–López de Prado 的結論必須貼在系統首頁：**只有 5 年日資料時，嘗試超過約 45 個策略變體，最優結果的 Sharpe ≥ 1.0 也可以是純運氣**[^44^]；上線前必須用 Deflated Sharpe Ratio、PBO/CSCV、walk-forward 驗證 [^45^][^46^]。這正是 4.2「勝兵先勝而後求戰」的現代技術內容。

### 4.2 三級分類（系統中必須如實標註）
- **A 級｜可直接回測驗證的規則（alpha/風控機制）**：趨勢過濾（P5）、ATR 定倉（P4）、RS 輪動（P9）、波動率目標（P10）、回撤狀態機（P2）、金字塔加倉（P8）、不追高入場過濾（P7）、冷卻機制（P11）、組合熱度上限（P12）。這些規則的證據來自學術文獻與公開系統（TSMOM、海龜、GEM、VBPS），**兵法只是命名，不是證據來源**。注意：TSMOM 的部分超額被後續研究歸因於波動率縮放而非趨勢信號本身；GEM 類策略在 2022 年股債同跌時失效（防守腿 AGG 下跌 10–24%）[^34^][^38^]；ETF 輪動的超額在計入成本後會縮水 [^43^]。
- **B 級｜流程與方法論規則（可審計但非 alpha）**：五事 checklist（1.2）、上線前驗證門檻（4.2）、三情境分析（8.4）、機械執行（5.3）、數據質量投入（13.2）、規則優先於人工（10.3）。這些不能用回測證明「有效」，但可以用工程審計證明「被遵守」。
- **C 級｜哲學裝飾（不可證偽，僅文化註腳）**：五危（8.3）、文武齊一（9.3）、致人而不致於人（6.3 的心態面）、「市場如戰場」的整體隱喻。允許出現在文檔與命名中，**禁止作為任何交易條件的依據**。
- **明確剔除**：九地篇「投之亡地然後存，陷之死地然後生」（11.4）——破釜沉舟式重倉在交易中是破產路徑，與 4.1 直接衝突。這也是一個誠實性測試：**凡是與風控公理衝突的兵法句子，一律捨棄兵法、保留風控**。

### 4.3 判準：一條映射何時算「可驗證」
滿足全部三條才算 A 級：(i) 規則可以在不引用原文的情況下寫成確定性函數；(ii) 存在明確的反例條件（什麼樣的回測結果會證明它無效）；(iii) 有獨立於兵法的學術或實盤證據（動量、波動率縮放、期望值、凱利、回撤控制的現代文獻）。否則降入 B/C。

---

## 五、推薦的最小可行規則集（MVP，12 條，適用 ETF 組合系統）

設計取捨：全部為 A/B 級規則；只做多、月頻為主、ETF 宇宙（如 SPY/QQQ/EFA/EEM/TLT/IEF/GLD/DBC/現金）；每條都標注兵法出處但依賴現代證據。

| # | 規則 | 兵法出處 | 實現 | 級別 |
|---|------|----------|------|------|
| R1 | **Regime 總開關**：價格 > SMA200 且 12M 動量 > 0 才持有風險資產，否則轉債券/現金 | 求之於勢（勢篇）/ 強而避之（計篇） | P5 | A |
| R2 | **相對強弱輪動**：每月持有動量前 3 檔 ETF，負動量者該槽位轉現金 | 避實擊虛（虛實篇） | P9 | A |
| R3 | **ATR 定倉**：unit = equity × 1% / (2 × ATR₂₀)，單標的權重 ≤ 25% | 度量數稱勝（形篇） | P4 | A |
| R4 | **波動率目標**：w = min(1, 10% / σ₂₀)，組合年化目標波動 10% | 有以待之（九變篇） | P10 | A |
| R5 | **回撤狀態機**：DD 5/10/20% → 倉位 ×0.75/×0.5/歸零，創新高後分批加回 | 先為不可勝（形篇）/ 九地狀態（九地篇） | P2 | A |
| R6 | **硬止損**：單筆止損 2×ATR 或 −8%（取緊者），止損永不下移 | 不盡知用兵之害（作戰篇） | P4/P8 | A |
| R7 | **不追高**：乖離率 > +2σ 禁止追價；等回踩 SMA20 或 RSI(3) < 20 入場 | 避其銳氣，擊其惰歸（軍爭篇） | P7 | A |
| R8 | **趨勢中加倉、震盪中觀望**：ADX > 25 允許金字塔加倉（0.5N 間距、≤4 單位）；ADX < 20 倉位減半 | 其疾如風…不動如山（軍爭篇） | P6/P8 | A |
| R9 | **廟算門檻 + 成本門檻**：score ≥ θ 且 expectancy > 2 × 成本才下單；無信號持幣 | 廟算（計篇）/ 非利不動（火攻篇）/ 知可不戰（謀攻篇） | P1 | A |
| R10 | **核心–衛星**：70–80% 戰略配置（股債金風險平價）+ 20–30% 戰術倉，衛星虧損隔離 | 以正合，以奇勝（勢篇） | 結構 | A |
| R11 | **冷卻機制**：止損後同標的冷卻 5 日；日虧 ≥ 2% 當日停開新倉 | 主不可以怒而興師（火攻篇） | P11 | A |
| R12 | **上線前驗證 + 負面清單**：DSR ≥ 0.95、OOS Sharpe ≥ 0.5、n_trades ≥ 100；不碰槓桿/反向 ETF | 勝兵先勝而後求戰（形篇）/ 途有所不由（九變篇）/ 先知取於實證（用間篇） | P3 | B |

**擴充候選（第 13 條）**：R13 組合熱度 ≤ 6% + 相關性合併敞口（知彼知己，謀攻篇；P12）——多標的並行時建議納入。

---

## 引用來源

[^1^] 中國哲學書電子化計劃《孫子兵法·始計》 https://ctext.org/art-of-war/laying-plans/zh
[^2^] ctext《孫子兵法·作戰》 https://ctext.org/art-of-war/waging-war/zh
[^3^] ctext《孫子兵法·謀攻》 https://ctext.org/art-of-war/attack-by-stratagem/zh
[^4^] ctext《孫子兵法·軍形》 https://ctext.org/art-of-war/tactical-dispositions/zh
[^5^] ctext《孫子兵法·兵勢》 https://ctext.org/art-of-war/energy/zh
[^6^] ctext《孫子兵法·虛實》 https://ctext.org/art-of-war/weak-points-and-strong/zh
[^7^] ctext《孫子兵法·九變》 https://ctext.org/art-of-war/variation-in-tactics/zh
[^8^] ctext《孫子兵法·軍爭》 https://ctext.org/art-of-war/maneuvering/zhs ；百度百科《孙子兵法·军争篇》 https://baike.baidu.com/item/%E5%AD%99%E5%AD%90%E5%85%B5%E6%B3%95%C2%B7%E5%86%9B%E4%BA%89%E7%AF%87/19831526
[^9^] UCSD Giles 對照本《The Art of War 9 行軍》 https://pages.ucsd.edu/~dkjordan/chin/Suentzyy/Suentzyy09.html
[^10^] UCSD《The Art of War 10 地形》 https://pages.ucsd.edu/~dkjordan/chin/Suentzyy/Suentzyy10.html
[^11^] UCSD《The Art of War 11 九地》 https://pages.ucsd.edu/~dkjordan/chin/Suentzyy/Suentzyy11.html
[^12^] UCSD《The Art of War 12 火攻》 https://pages.ucsd.edu/~dkjordan/chin/Suentzyy/Suentzyy12.html
[^13^] UCSD《The Art of War 13 用間》 https://pages.ucsd.edu/~dkjordan/chin/Suentzyy/Suentzyy13.html
[^14^] Dean Lundell, *Sun Tzu's Art of War for Traders and Investors*, McGraw-Hill 1997（Amazon） https://www.amazon.ca/Sun-Tzus-Art-Traders-Investors/dp/0070391416
[^15^] El Economista「10 Libros de Trading」（Lundell 書介紹） https://www.eleconomist.com/2024/11/10-libros-de-trading-que-deberias-leer.html
[^16^] 百度百科：李國平《孫子兵法與貨幣戰爭：外匯期貨股票經典戰例》（北京大學出版社 2011） https://baike.baidu.com/item/%E5%AD%99%E5%AD%90%E5%85%B5%E6%B3%95%E4%B8%8E%E8%B4%A7%E5%B8%81%E6%88%98%E4%BA%89%EF%BC%9A%E5%A4%96%E6%B1%87%E6%9C%9F%E8%B4%A7%E8%82%A1%E7%A5%A8%E7%BB%8F%E5%85%B8%E6%88%98%E4%BE%8B/7317014
[^17^] 《冷眼孫子股市兵法》（淘寶圖書頁） https://world.taobao.com/lang/zh-tw/goods/505282.htm
[^18^] Stock Investing with Sun Tzu Art of War（部落格，逐篇映射） https://stockinvestingwithsuntzuartofwar.wordpress.com/
[^19^] 雪球《基于〈孙子兵法〉构建年化50%投资系统的核心逻辑框架》 http://xueqiu.com/6114319827/334208835
[^20^] 技術分析博物館《〈孙子兵法〉13篇与股市应用》 https://www.jsfx3.com/detail.php?id=355
[^21^] 雪球《孫子兵法與投資：先為不可勝，以待市場之可勝》 https://xueqiu.com/8589961169/297407983
[^22^] 新浪《孙子兵法投资法》（形篇原文+投資詮釋） https://www.sina.cn/news/detail/5312016358316739.html
[^23^] 《外匯交易三部曲》PDF（孫子兵法與盈虧比詮釋） https://16371929.s21i.faiusr.com/61/1/ABUIABA9GAAgqPaYhAYoreWB5wE.pdf
[^24^] Altrady「Turtle Trading Strategy Rules」（N/ATR 定倉、0.5N 加倉、2N 止損、回撤降倉、相關性上限） https://www.altrady.com/blog/crypto-trading-strategies/turtle-trading-strategy-rules
[^25^] AIClarity「Turtle Trading Strategy Explained」（35–40% 勝率、盈虧不對稱、現代改良） https://www.aiclarity.me/strategies/turtle-trading.html
[^26^] BigQuant《不懂策略？学习海龟交易法》（中文規則全文） https://bigquant.com/wiki/doc/JH3xC6GTf9
[^27^] Gitee 量化教程 PDF（海龜滬深300ETF 實現：TR/ATR/Unit 公式與代碼） https://gitee.com/CCHChenChangHong/changhong_quantizing_machine/wikis/pages/export?doc_id=152788&type=pdf
[^28^] Chartmill「Mark Minervini Strategy Part 2：Risk Management」（止損 0.5–2.5%、從風險倒推倉位、2R 保本規則） https://www.chartmill.com/documentation/stock-screener/fundamental-analysis-investing-strategies/465-Mark-Minervini-Strategy-Think-and-Trade-Like-a-Champion-Trading-Strategy
[^29^] Finer Market Points「Minervini SEPA 完整框架」（line in the sand 8%、progressive exposure、賣出一半放寬止損） https://www.finermarketpoints.com/post/mark-minervini-s-sepa-methodology-complete-framework-explained
[^30^] QuantStrategy「Understanding Expectancy: Van Tharp」（expectancy 公式、0.5R 基準、30–100 筆樣本） https://quantstrategy.io/blog/understanding-expectancy-the-core-of-van-tharps-trading
[^31^] ForTraders「10 Best Trading Books」之 Van Tharp《Trade Your Way to Financial Freedom》（R-multiple、倉位管理為主驅動） https://fortraders.com/blog/trading-books-read
[^32^] AlgoLab「Advanced Position Sizing: Kelly, Volatility Targeting, Risk Parity」（凱利 f=P−(1−P)/B、1/4 凱利、vol targeting 公式、風險平價示例、三層整合框架） https://algolabhk.com/en/blogs/position-sizing-strategies-kelly-volatility-risk-parity-2025-en
[^33^] ForTraders「Volatility-Based Position Sizing Explained」（公式、1.5–3.0× ATR 乘數、逆波動率加權改善 Sharpe 0.99→1.54、回撤 −30.8%→−13.8%） https://fortraders.com/blog/volatility-based-position-sizing-explained
[^34^] Foxholm 對 Moskowitz, Ooi & Pedersen (2012)「Time Series Momentum」的綜述（JFE 104(2):228-250，58 市場、12M lookback） https://foxholm.com/q/research/moskowitz-ooi-pedersen-time-series-momentum/ ；AQR 回溯 1880 年研究介紹 https://sharemaestro.com/blog/richard-dennis-turtle-traders-systematic-trend-following-profile/
[^35^] Alpha Architect「Avoiding the Big Drawdown with Trend-Following」（TMOM/MA 下行保護模型、Faber 2007、Clare et al. 2017） https://alphaarchitect.com/avoiding-the-big-drawdown-with-trend-following-investment-strategies/
[^36^] TechWhims《市場狀態識別 Regime Detection》（TSMOM 中文綜述、信號半衰期約 3 個月、Baltas & Kosowski 2013） https://techwhims.com/tradesys/macro/regime-detection/
[^37^] BestFolio「GEM (Global Equities Momentum) by Gary Antonacci」（規則全文、回測 Sharpe 0.98） https://bestfolio.app/strategies/gem ；Antonacci《Dual Momentum Investing》(2014) https://www.amazon.ca/Dual-Momentum-Investing-Innovative-Strategy/dp/0071849440
[^38^] BestFolio「Dual Momentum's 2022 Problem」（2022 年 GEM/ADM/CDM 跌 10–24%，防禦腿債券失效） https://bestfolio.app/strategies/cdm
[^39^] Bharath Shiksha「What is a regime filter?」（200DMA+斜率雙投票、ADX>25/<20、ATR 分位數、寬度指標、lag 的取捨） https://bharathshiksha.com/regime-filters-trading-india.html
[^40^] CycleDetective「Paul Tudor Jones and the 200-Day Moving Average」 https://cycledetective.com/blog/paul-tudor-jones-200-day-moving-average/
[^41^] PicturePerfectPortfolios「How To Invest Like David Druz」（ATR 噪音層外止損、regime filter、回撤降槓桿） https://pictureperfectportfolios.com/how-to-invest-like-david-druz-top-trend-following-trader-wizard/
[^42^] ReproQuant「ETF Momentum Rotation Backtest: SPY/QQQ/Sector」（126 日動量、Top1/Top3、T+1 防前視、成本建模） https://www.reproquant.com/studies/spy-qqq-sector-momentum-rotation-backtest/ ；相對 vs 絕對動量 https://www.reproquant.com/studies/relative-vs-absolute-momentum-etf-rotation
[^43^] QuantifiedStrategies「ETF Rotation Strategy」（回測有效但 2023 年研究：超額在計入成本後縮水、依賴後見之明） https://www.quantifiedstrategies.com/etf-rotation-strategy/
[^44^] David H. Bailey「Backtesting in quantitative finance: limitations」（MinBTL：2 年日資料 ≤7 變體、5 年 ≤45 變體；不報告試驗次數的回測不可評估） https://www.davidhbailey.com/dhbtalks/dhb-zurich-finance.pdf
[^45^] Bailey & López de Prado (2014)「The Deflated Sharpe Ratio」（JPM 40(5):94-107） https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
[^46^] OutOfSampleLab/oos-lab（PSR/DSR/PBO/CSCV/walk-forward 開源驗證工具） https://github.com/OutOfSampleLab/oos-lab
[^47^] PTT Military 版《孫子兵法在現代戰爭有沒有用？》（「把現狀代回去……基本上就是馬後炮」；「他就寫的很大方向，當然什麼都能套」） https://ptt-reviews.cc/Military/M.1664768774.A.793
[^48^] PicturePerfectPortfolios「Warren Buffett's Rule 'Never Lose Money' — Examining Its Viability」（口號 vs 機器；普通人不可照搬 Berkshire 結構） https://pictureperfectportfolios.com/warren-buffetts-rule-never-lose-money-examining-its-viability/
[^49^] Rule #1 Investing「Investing Basics: Rule Number 1 Never Lose Money」（Buffett 兩條規則出處） https://www.ruleoneinvesting.com/investing-basics/
[^50^] Winsmart《海龜交易法則》（0.5ATR 加碼、滿倉 4 碼、移動停利上移機制，中文圖解） https://winsmart.tw/online_teaching/%E6%B5%B7%E9%BE%9C%E4%BA%A4%E6%98%93%E6%B3%95%E5%89%87/

---
*報告完成。研究子代理 R3。*
