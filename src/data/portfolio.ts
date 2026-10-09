// ETF 组合数据 —— 快照 2026-07-24
// 观点来源：YouTube 视频内容（含完整字幕/官方内容简介）、报章专栏、专访；时间衰减半衰期 21 天

export interface EtfHolding {
  ticker: string; name: string; theme: string
  weight: number; delta: number          // 最新调仓(2026-07-20)变动 pp
  halfRet: number                        // 半年代理回报 %(2026-01-23→07-24)
  signal: string; experts: string; tv: string
}

export const ETF_PORTFOLIO: EtfHolding[] = [
  { ticker: 'VOO', name: 'Vanguard 标普500', theme: '美股大盘', weight: 12, delta: 2, halfRet: 9.6,
    signal: 'Timmer(7/6完整字幕)：盈利同比+30%、「trust the boom but verify」；譚新強(7/18)：美股升势不能停——幅度受AI隐形债务(7/24)及市场广度不足(蔡7/10)对冲', experts: 'Timmer/譚新強 vs 對沖信號', tv: 'https://www.tradingview.com/symbols/AMEX-VOO/' },
  { ticker: 'SMH', name: 'VanEck 半导体', theme: 'AI上游/晶片', weight: 10, delta: 2, halfRet: 48.6,
    signal: '譚新強(7/18)：晶片美元取代石油；Timmer(7/6)：半导体盈利一年翻三倍、20倍PE不贵但属周期性需验证；洪灝：「卖铲子」先赚钱；蔡金強：AI唯一主线', experts: '四专家共识', tv: 'https://www.tradingview.com/symbols/NASDAQ-SMH/' },
  { ticker: 'ASHR', name: 'Xtrackers 沪深300', theme: '中国A股', weight: 8, delta: 1, halfRet: 3.9,
    signal: '洪灝(7/16)：人民币升值重估中国资产=未来五年最大机会、A股还要创新高；(7/21)牛市或超乎想象；蔡金強：走出通缩看好A股多于港股', experts: '洪灝/蔡金強', tv: 'https://www.tradingview.com/symbols/AMEX-ASHR/' },
  { ticker: 'MCHI', name: 'iShares MSCI中国', theme: '中国(离岸)', weight: 5, delta: 1, halfRet: -12.9,
    signal: '洪灝中国牛市外溢；但譚新強(7/18)警示「不可假定资金必回流中国」→ 幅度受限', experts: '洪灝 vs 譚新強', tv: 'https://www.tradingview.com/symbols/NASDAQ-MCHI/' },
  { ticker: 'EWH', name: 'iShares MSCI香港', theme: '港股', weight: 6, delta: -1, halfRet: 2.3,
    signal: '林本利(5/20)：本地蓝筹/中特估高息、逢七必升；林一鳴：不再远离港股；莊太量：减息利港——但譚新強泼冷水+恒指半年仅+1%', experts: '林本利/林一鳴/莊太量 vs 譚新強', tv: 'https://www.tradingview.com/symbols/AMEX-EWH/' },
  { ticker: 'GLD', name: 'SPDR 黄金', theme: '黄金', weight: 9, delta: -3, halfRet: -15.0,
    signal: '洪灝(7/8錄影)：港建黄金仓「战略一步」、黄金为估值之锚；Timmer(7/6)：黄金较货币供应超卖13%、适合分段积累；蔡金強：金银铜一骑绝尘。洪灝(2025/11)曾提示3500-4500宽幅震荡。⚠真实行情：金价1/29见顶后半年-15%（白银-39%），此信号为组合最大拖累——见复盘', experts: '洪灝/Timmer/蔡金強', tv: 'https://www.tradingview.com/symbols/AMEX-GLD/' },
  { ticker: 'SLV', name: 'iShares 白银', theme: '白银', weight: 3, delta: 0, halfRet: -39.0,
    signal: '蔡金強(2月)：金银铜大叙事。⚠真实行情：白银1/28见顶后腰斩，衰减引擎下调太慢是教训——见复盘', experts: '蔡金強/洪灝', tv: 'https://www.tradingview.com/symbols/AMEX-SLV/' },
  { ticker: 'COPX', name: 'GlobalX 铜矿', theme: '铜', weight: 3, delta: 0, halfRet: -4.4,
    signal: '蔡金強：铜一骑绝尘 + HALO重资产重新定价', experts: '蔡金強', tv: 'https://www.tradingview.com/symbols/AMEX-COPX/' },
  { ticker: 'XLE', name: 'SPDR 能源', theme: 'HALO·能源', weight: 6, delta: -1, halfRet: 26.5,
    signal: '蔡金強(7/8)：HALO(重资产低淘汰)交易；Timmer(7/6)：ex-AI杠铃含能源；油价中枢75-80', experts: '蔡金強/Timmer', tv: 'https://www.tradingview.com/symbols/AMEX-XLE/' },
  { ticker: 'XLB', name: 'SPDR 原材料', theme: 'HALO·材料', weight: 4, delta: 0, halfRet: 5.2,
    signal: '蔡金強(7/8)：HALO实体资产重新定价', experts: '蔡金強', tv: 'https://www.tradingview.com/symbols/AMEX-XLB/' },
  { ticker: 'IFRA', name: 'iShares 美国基建', theme: 'HALO·基建', weight: 5, delta: 0, halfRet: 13.3,
    signal: 'HALO + AI数据中心电力/基建需求；Timmer：工业复兴由AI引领', experts: '蔡金強/Timmer', tv: 'https://www.tradingview.com/symbols/AMEX-IFRA/' },
  { ticker: 'EWY', name: 'iShares MSCI韩国', theme: '韩国', weight: 4, delta: 0, halfRet: 56.7,
    signal: '蔡金強：韩台估值便宜+科技护城河；譚新強：晶片链核心；Timmer(7/6)：韩国散户亢奋非泡沫信号', experts: '蔡金強/譚新強/Timmer', tv: 'https://www.tradingview.com/symbols/AMEX-EWY/' },
  { ticker: 'EWT', name: 'iShares MSCI台湾', theme: '台湾', weight: 5, delta: 1, halfRet: 50.0,
    signal: '譚新強(7/18)：晶片美元核心(台积电)；蔡金強：看好韩台', experts: '譚新強/蔡金強', tv: 'https://www.tradingview.com/symbols/AMEX-EWT/' },
  { ticker: 'XLV', name: 'SPDR 医疗保健', theme: '医疗', weight: 4, delta: 0, halfRet: 4.8,
    signal: '蔡金強：医药受政策青睐；防御性敞口', experts: '蔡金強', tv: 'https://www.tradingview.com/symbols/AMEX-XLV/' },
  { ticker: 'VGK', name: 'Vanguard 欧洲股票', theme: '欧洲', weight: 3, delta: 0, halfRet: 5.3,
    signal: 'Timmer(7/6)：欧元区银行股是对冲Mag-7的绝佳工具、回购强劲；洪灝：非美资产轮动', experts: 'Timmer/洪灝', tv: 'https://www.tradingview.com/symbols/AMEX-VGK/' },
  { ticker: 'IBIT', name: 'iShares 比特币', theme: '比特币', weight: 2, delta: 1, halfRet: -27.8,
    signal: 'Timmer(7/6)：与黄金同理超卖、适合积累；洪灝(6/17)：候买入时点。⚠真实行情：比特币半年-28%，「超卖」判断待验证', experts: 'Timmer/洪灝', tv: 'https://www.tradingview.com/symbols/NASDAQ-IBIT/' },
  { ticker: 'TLT', name: 'iShares 20年+美债', theme: '长债', weight: 3, delta: 0, halfRet: -1.8,
    signal: '洪灝：流动性宽松利好长债；但蔡金強「最多减一次息」+Timmer「Warsh口头鹰派」→ 仅小仓位', experts: '洪灝 vs 蔡金強', tv: 'https://www.tradingview.com/symbols/NASDAQ-TLT/' },
  { ticker: 'BND', name: 'Vanguard 综合债券', theme: '债券', weight: 4, delta: -1, halfRet: -0.3,
    signal: '组合缓冲；减息推迟下维持基础配置', experts: '组合风控', tv: 'https://www.tradingview.com/symbols/NASDAQ-BND/' },
  { ticker: 'SGOV', name: 'iShares 0-3月国库券', theme: '现金', weight: 4, delta: -2, halfRet: 1.8,
    signal: '释放现金执行7/20信号(中国+2、美股+2、晶片+2)；保留地缘+AI债务缓冲', experts: '组合风控', tv: 'https://www.tradingview.com/symbols/AMEX-SGOV/' },
  // 日股：0% —— 蔡金強明确减持日股；譚新強：日圆走弱；洪灝(7/8)：日圆180无悬念
]

export interface Rebalance {
  date: string; title: string; trigger: string
  changes: { etf: string; from: number; to: number }[]
  note: string
}
export const REBALANCES: Rebalance[] = [
  { date: '2026-01-26', title: '初始建仓',
    trigger: '洪灝(1/11首席经济学家论坛)：2026全球央行同步宽松或诞生「伟大泡沫」、贵金属长牛；蔡金強(edigest)：AI仍是主线；林本利：三分原则；Timmer：流动性充裕',
    changes: [
      { etf: 'VOO', from: 0, to: 15 }, { etf: 'SMH', from: 0, to: 10 }, { etf: 'GLD', from: 0, to: 10 },
      { etf: 'SLV', from: 0, to: 3 }, { etf: 'COPX', from: 0, to: 2 }, { etf: 'ASHR', from: 0, to: 6 },
      { etf: 'MCHI', from: 0, to: 4 }, { etf: 'EWH', from: 0, to: 8 }, { etf: 'XLE', from: 0, to: 4 },
      { etf: 'XLB', from: 0, to: 3 }, { etf: 'IFRA', from: 0, to: 4 }, { etf: 'EWY', from: 0, to: 3 },
      { etf: 'EWT', from: 0, to: 3 }, { etf: 'XLV', from: 0, to: 3 }, { etf: 'VGK', from: 0, to: 3 },
      { etf: 'IBIT', from: 0, to: 2 }, { etf: 'TLT', from: 0, to: 4 }, { etf: 'BND', from: 0, to: 5 },
      { etf: 'SGOV', from: 0, to: 8 },
    ],
    note: '逐ETF列出（与回测引擎使用的W0完全一致）：股票69%/商品15%/数字资产2%/债券现金17% 起步' },
  { date: '2026-03-16', title: '调仓 #1：蔡金強富途演讲',
    trigger: '蔡金強(3/13)：油价中枢或上移至75-80打乱减息、美国最多减一次息；避开美股锋芒、转吼重资产；看好A股多于港股、看好韩台',
    changes: [
      { etf: 'VOO', from: 15, to: 11 }, { etf: 'SMH', from: 10, to: 9 }, { etf: 'ASHR', from: 6, to: 8 },
      { etf: 'MCHI', from: 4, to: 5 }, { etf: 'XLE', from: 4, to: 6 }, { etf: 'XLB', from: 3, to: 4 },
      { etf: 'IFRA', from: 4, to: 5 }, { etf: 'EWY', from: 3, to: 4 }, { etf: 'EWT', from: 3, to: 4 },
      { etf: 'XLV', from: 3, to: 4 }, { etf: 'COPX', from: 2, to: 3 }, { etf: 'SGOV', from: 8, to: 4 },
      // Phase 13 修復：補回 TLT 4→3——舊版遺漏令 replay 出 TLT=4、Σ=101，與 CURRENT_WEIGHTS（TLT=3、Σ=100）矛盾
      { etf: 'TLT', from: 4, to: 3 },
    ],
    note: '★ 事后验证：6月伊朗冲突、油价飙120美元——重资产+减仓美股方向正确，为上半年最大贡献决策' },
  { date: '2026-06-15', title: '调仓 #2：中东冲突升级',
    trigger: '霍尔木兹封锁、油价破100美元；恒指6月暴跌9.14%；林本利(5/20)逢跌吸纳中特估逻辑保留港股核心；提高黄金与现金防御',
    changes: [
      { etf: 'GLD', from: 10, to: 12 }, { etf: 'XLE', from: 6, to: 7 }, { etf: 'SGOV', from: 4, to: 6 },
      { etf: 'VOO', from: 11, to: 10 }, { etf: 'SMH', from: 9, to: 8 }, { etf: 'ASHR', from: 8, to: 7 },
      { etf: 'MCHI', from: 5, to: 4 }, { etf: 'EWH', from: 8, to: 7 }, { etf: 'IBIT', from: 2, to: 1 },
    ],
    note: '冲突高峰把黄金+能源+现金提至25%；6/26市场触底后组合回撤显著小于纯股票组合' },
  { date: '2026-07-20', title: '调仓 #3（最新）：人民币升值重估 + 盈利验证 + 晶片美元',
    trigger: '洪灝(7/16新浪峰会)：人民币升值重估中国资产=未来五年最大机会、A股还要创新高；(7/21)牛市超乎想象；洪灝(7/8錄影etnet)：港建黄金仓战略一步、日圆180、人币被低估；Timmer(7/6完整字幕)：盈利+30%、黄金超卖13%可积累、比特币同理、半导体盈利翻三倍但属周期性；譚新強(7/18)：晶片美元年代+美股不能停，但勿假设资金回流中国、(7/24)AI隐形债务1.65万亿；蔡金強(7/8)：HALO交易、(7/10)市场广度极差',
    changes: [
      { etf: 'VOO', from: 10, to: 12 }, { etf: 'SMH', from: 8, to: 10 }, { etf: 'ASHR', from: 7, to: 8 },
      { etf: 'MCHI', from: 4, to: 5 }, { etf: 'EWT', from: 4, to: 5 }, { etf: 'IBIT', from: 1, to: 2 },
      { etf: 'GLD', from: 12, to: 9 }, { etf: 'EWH', from: 7, to: 6 }, { etf: 'XLE', from: 7, to: 6 },
      { etf: 'BND', from: 5, to: 4 }, { etf: 'SGOV', from: 6, to: 4 },
    ],
    note: '最大单边：中国资产+2pp（洪灝最新信号）；GLD从高位兑现3pp锁定+20%收益但保留9%（Timmer超卖论+洪灝战略论仍在）；譚新強「资金未必回流」抑制中港加仓幅度' },
]

// 真实回测：Yahoo Finance 复权日线（2026-01-20 → 2026-07-23），按调仓路径逐日滚动计算
// 基准 = 60% ACWI + 40% AGG（真实ETF价格）；未计费用/点差/汇率
export const WEEKS = ["01-20", "01-21", "01-22", "01-23", "01-26", "01-27", "01-28", "01-29", "01-30", "02-02", "02-03", "02-04", "02-05", "02-06", "02-09", "02-10", "02-11", "02-12", "02-13", "02-17", "02-18", "02-19", "02-20", "02-23", "02-24", "02-25", "02-26", "02-27", "03-02", "03-03", "03-04", "03-05", "03-06", "03-09", "03-10", "03-11", "03-12", "03-13", "03-16", "03-17", "03-18", "03-19", "03-20", "03-23", "03-24", "03-25", "03-26", "03-27", "03-30", "03-31", "04-01", "04-02", "04-06", "04-07", "04-08", "04-09", "04-10", "04-13", "04-14", "04-15", "04-16", "04-17", "04-20", "04-21", "04-22", "04-23", "04-24", "04-27", "04-28", "04-29", "04-30", "05-01", "05-04", "05-05", "05-06", "05-07", "05-08", "05-11", "05-12", "05-13", "05-14", "05-15", "05-18", "05-19", "05-20", "05-21", "05-22", "05-26", "05-27", "05-28", "05-29", "06-01", "06-02", "06-03", "06-04", "06-05", "06-08", "06-09", "06-10", "06-11", "06-12", "06-15", "06-16", "06-17", "06-18", "06-22", "06-23", "06-24", "06-25", "06-26", "06-29", "06-30", "07-01", "07-02", "07-06", "07-07", "07-08", "07-09", "07-10", "07-13", "07-14", "07-15", "07-16", "07-17", "07-20", "07-21", "07-22", "07-23"]
export const PORTFOLIO = [100.0,101.35,101.85,102.36,102.89,104.05,104.97,105.03,101.89,101.26,102.17,101.72,100.07,102.49,103.63,103.31,104.29,102.55,103.25,102.67,103.49,103.51,104.66,104.74,105.21,105.91,105.38,105.72,105.49,102.8,103.48,102.26,101.6,102.71,102.89,103.02,101.42,100.85,102.11,102.22,100.51,99.99,97.65,98.67,98.68,100.09,97.68,97.68,97.26,99.97,100.66,100.06,100.37,100.61,103.41,103.69,103.98,104.49,105.75,105.37,105.59,106.71,106.44,105.19,106.79,106.22,107.22,106.92,106.06,105.97,107.7,107.87,107.07,108.44,110.67,109.71,110.97,112.12,111.32,112.3,111.96,109.41,109.18,108.3,109.66,109.97,110.02,111.64,110.92,111.4,111.39,111.61,112.69,112.07,111.84,107.49,108.34,107.92,106.13,109.09,109.8,111.57,110.75,109.62,110.5,110.94,108.24,107.44,108.49,107.84,108.26,108.82,107.77,107.65,108.8,107.54,107.44,108.38,108.57,106.85,108.21,108.05,106.89,106.25,106.31,108.41,108.86,108.09]
export const BENCHMARK = [100.0,100.83,101.17,101.36,101.65,102.18,102.07,102.02,101.51,101.8,101.48,101.23,100.66,101.98,102.46,102.54,102.61,101.94,102.19,102.22,102.43,102.31,102.86,102.37,102.82,103.35,103.12,102.96,102.45,101.2,101.74,100.92,100.18,100.89,100.76,100.53,99.33,98.91,99.89,100.14,99.05,98.96,97.42,98.53,98.1,98.79,97.31,96.52,96.56,98.46,99.04,99.03,99.26,99.33,101.32,101.53,101.45,102.1,102.92,103.14,103.13,104.11,103.91,103.06,103.71,103.26,103.84,103.78,103.4,103.02,104.07,104.17,103.65,104.4,105.83,105.13,105.82,105.77,105.29,105.81,106.11,104.8,104.91,104.25,105.3,105.59,105.76,106.63,106.59,106.92,107.06,107.27,107.63,107.01,107.27,105.14,105.36,105.31,104.32,106.04,106.25,107.35,107.12,106.33,107.25,107.07,105.82,105.94,106.16,106.03,106.67,106.98,106.57,106.63,107.39,106.58,106.28,106.8,107.02,106.15,106.69,106.99,106.51,105.98,105.66,106.31,106.2,105.34]

export const REBALANCE_MARKS = [
  { week: '03-16', label: '调仓#1' },
  { week: '06-15', label: '调仓#2' },
  { week: '07-20', label: '调仓#3' },
]

export const REAL_STATS = {
  portRet: 8.09, benchRet: 5.34, maxDD: -8.17, benchMaxDD: -6.61,
  netRet: 7.97,            // 含交易成本(单边10bps×总换手125%)
  annRet: 16.7, benchAnnRet: 10.9,
  vol: 18.4, benchVol: 10.8,
  sharpe: 0.69, benchSharpe: 0.64,
  turnover: 125, costDrag: 0.12,
  source: 'Yahoo Finance 复权日线 · 2026-01-20→07-23',
}

// 注：旧的手工维护 CONSENSUS 矩阵已废除（会与衰减规则漂移），现由 src/lib/consensus.ts 即时计算

export const EXPERT_NAMES: Record<string, string> = {
  hong: '洪灝', choi: '蔡金強', timmer: 'Timmer', tam: '譚新強', lam: '林本利', lamy: '林一鳴', chong: '莊太量', hui: '許佳龍',
}
