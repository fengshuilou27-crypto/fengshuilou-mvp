// 专家观点库 —— 快照日期 2026-07-24
// 时间衰减：半衰期 21 天，w = 0.5^(距今天数/21)，距今超过 90 天的观点不再计入配置

export interface ExpertView {
  date: string        // 观点发表日期
  channel: string     // 渠道
  title: string
  summary: string
  stance: { asset: string; dir: 'bull' | 'bear' | 'neutral'; note: string }[]
  url: string
}

export interface Expert {
  id: string
  name: string
  role: string
  weightInPortfolio: number  // 动态权重%（基础权重 × 命中率收缩因子，半年样本，向均值收缩）
  hitRate: number | null     // 复盘命中率（命中=1 部分=0.5 未兑现=0，观察中不计）；null=样本不足
  active: boolean
  inactiveNote?: string
  views: ExpertView[]
}

export const EXPERTS: Expert[] = [
  {
    id: 'hong', name: '洪灝', role: '莲华资管首席投资官 · 中国首席经济学家论坛理事', weightInPortfolio: 14, hitRate: 0.0, active: true,
    views: [
      { date: '2026-07-16', channel: '雪球 · 新浪全球资本峰会演讲', title: '人民币升值重估中国资产，是未来五年最大的机会',
        summary: '未来五年最重要主题：人民币升值带来中国资本市场价值重估。同日峰会发言：A股上证已涨逾千点，但整体估值仍处长期均值，非常合理，长期还要创新高。',
        stance: [
          { asset: 'A股/中国资产', dir: 'bull', note: '最新核心观点：升值重估+还要创新高' },
          { asset: '人民币', dir: 'bull', note: '升值周期' },
        ], url: 'https://xueqiu.com/3338215700/400745046' },
      { date: '2026-07-21', channel: 'HKET · 大行看法', title: '中国今轮牛市或「超乎想象」，续推升股市的关键是「反内卷」',
        summary: '北京应对通缩的政策转向是牛市真正成因且远未被消化；本轮牛市将无视技术面波动、坚守增长股；「反内卷」重要性被共识忽视。',
        stance: [
          { asset: 'A股/中国增长股', dir: 'bull', note: '政策转向未被定价' },
          { asset: '港股', dir: 'bull', note: '中国牛市外溢' },
        ], url: 'https://inews.hket.com/article/4003261/' },
      { date: '2026-07-08', channel: 'YouTube · etnet专访（7月8日录影）', title: '港建黄金仓「战略一步」，日圆180无悬念，人币被低估',
        summary: '香港建黄金仓储是战略一步，黄金为新信用体系的估值之锚；日圆贬值至180无悬念；人民币被低估、升值空间大——与7/16「人民币升值重估中国资产」演讲互为印证。',
        stance: [
          { asset: '黄金', dir: 'bull', note: '战略级配置，非交易性' },
          { asset: '日圆/日本资产', dir: 'bear', note: '日圆180' },
          { asset: '人民币/中国资产', dir: 'bull', note: '人币被低估' },
        ], url: 'https://www.etnet.com.hk/www/tc/video/haohong/' },
      { date: '2025-03-12', channel: 'YouTube · etnet专访（旧片，不计入配置）', title: '形势比想象严峻，炒作DS如淘金卖铲子先赚钱',
        summary: '⚠ 时间性纠错：此片常被误标为近期内容，实为2025年3月12日（针对2025年初DeepSeek行情）。已超过90天，按衰减规则权重=0，仅存档。「卖铲子先赚钱」的AI上游框架仍被其后观点沿用。',
        stance: [{ asset: 'AI上游', dir: 'bull', note: '框架沿用，信号本身已衰减' }],
        url: 'https://www.youtube.com/watch?v=MSvn4SexBWU' },
      { date: '2026-06-17', channel: 'YouTube · etnet专访', title: 'A股倍升股只看不买，黄金泡沫与比特币的买入时点',
        summary: 'A股个股炒作不追，但整体性价比超港股；贵金属长牛不改，黄金是新信用体系估值之「锚」。',
        stance: [
          { asset: '黄金/贵金属', dir: 'bull', note: '长牛（ETF版以GLD表达）' },
          { asset: '比特币', dir: 'bull', note: '候买入时点' },
        ], url: 'https://www.youtube.com/watch?v=zmk6hrBChE4' },
      { date: '2025-11-12', channel: '瑞士宝盛月度对话（投资报转载）', title: '展望2026：获利了结为时过早，望4000点成新支持位',
        summary: '黄金转入3500-4500美元宽幅震荡（为未上车者提供交易机会）；美元长期贬值趋势不变，建议配置非美元资产；人行重启债券交易=小型量宽。',
        stance: [
          { asset: '黄金', dir: 'neutral', note: '最新定性：宽幅震荡，非单边（旧观点已衰减）' },
          { asset: '非美资产', dir: 'bull', note: '美元长期贬值' },
        ], url: 'https://www.sina.cn/news/detail/5231964835807279.html' },
    ],
  },
  {
    id: 'choi', name: '蔡金強', role: '奧陸資本创办人兼首席投资官', weightInPortfolio: 25, hitRate: 1.0, active: true,
    views: [
      { date: '2026-07-08', channel: 'YouTube · @octalk999 金人金語', title: 'AI颠覆2028经济 / 全球HALO（heavy asset, low obsolescence）trade',
        summary: '最新核心框架：AI将于2028年前颠覆经济；资金转向「重资产、低淘汰」（HALO）资产——能源、材料、基建等实体资产重新定价。',
        stance: [
          { asset: '重资产(能源/材料/基建)', dir: 'bull', note: 'HALO trade 最新主线' },
          { asset: 'AI', dir: 'bull', note: '颠覆性趋势延续' },
          { asset: '轻资产旧经济', dir: 'bear', note: '被淘汰风险' },
        ], url: 'https://www.youtube.com/watch?v=yBRGco2M7FI' },
      { date: '2026-07-10', channel: 'YouTube · etnet专访', title: '全球晒冷炒AI，不「当造」神仙也难救，碳基世界不值钱',
        summary: '市场极端集中于AI单一叙事，非AI资产被全面边缘化——既是趋势确认，也警示市场广度极差、脆弱性高。',
        stance: [
          { asset: 'AI板块', dir: 'bull', note: '唯一主线' },
          { asset: '非AI股票', dir: 'bear', note: '广度不足警示' },
        ], url: 'https://www.youtube.com/results?search_query=%E8%94%A1%E9%87%91%E5%BC%B7+etnet+%E7%A2%B3%E5%9F%BA%E4%B8%96%E7%95%8C' },
      { date: '2026-06-12', channel: 'YouTube · @octalk999 金人金語', title: '鬼故事满天的6月股市 / SpaceX上市分析',
        summary: '6月中东冲突下「鬼故事」满天，但股市韧性超预期；SpaceX上市定价分析。',
        stance: [{ asset: '美股', dir: 'neutral', note: '恐慌中保持持仓' }],
        url: 'https://www.youtube.com/watch?v=Wq-8jUa62cw' },
      { date: '2026-06-17', channel: 'YouTube · 小金人', title: '股市最新睇法：AI供应链担忧已解除？金和油股前景',
        summary: '美股业绩有惊喜、AI供应链担忧缓解；讨论金、油股前景及中港板块。',
        stance: [
          { asset: '美股AI上游', dir: 'bull', note: '供应链担忧缓解' },
          { asset: '黄金/石油股', dir: 'bull', note: '地缘溢价' },
        ], url: 'https://www.youtube.com/watch?v=A4yL5rPrhMQ' },
      { date: '2026-02-15', channel: 'YouTube · @octalk999 金人金語', title: '伟大叙事下的金银铜——一骑绝尘',
        summary: '贵金属与铜的大叙事：金银铜齐齐跑赢。（约5个月前，权重已显著衰减）',
        stance: [{ asset: '金银铜', dir: 'bull', note: '旧观点，与洪灝黄金长牛互相印证' }],
        url: 'https://www.youtube.com/watch?v=LxQqJxOR4wM' },
      { date: '2026-03-13', channel: '富途投资展2026演讲（星岛3/16报道）', title: '忧高油价打乱减息：避开美股、转吼重资产、看好A股多于港股',
        summary: '市场低估伊朗冲突影响，油价中枢或由65升至75-80美元；美国今年最多减息一次。美股连升三四年应先避一避；资金分散至重资产低消耗板块；内地CPI/PPI现走出通缩迹象看好A股；看淡恒生科指；大幅减持日股，看好韩台。',
        stance: [
          { asset: '美股', dir: 'bear', note: '短期避锋芒' },
          { asset: 'A股', dir: 'bull', note: '走出通缩=超级利好' },
          { asset: '恒生科指', dir: 'bear', note: '平台股不受政策青睐' },
          { asset: '日股', dir: 'bear', note: '输入性通胀迫央行加息' },
          { asset: '韩台股市', dir: 'bull', note: '估值便宜+科技护城河' },
          { asset: '债券', dir: 'neutral', note: '减息次数少于预期' },
        ], url: 'https://www.stheadline.com/investment/3553216/' },
      { date: '2025-12-01', channel: '经济 digest 封面故事', title: '2026投资主题：AI仍是主线',
        summary: 'AI这件事不会变，但板块内部资金轮动：由GPU扩散至记忆体、电力能源、应用端；Mag 7中五间财政比美国政府更健康。',
        stance: [{ asset: '美股科技', dir: 'bull', note: '旧观点，权重已衰减' }],
        url: 'https://www.edigest.hk/投資/蔡金強專訪-美股-ai-封面故事-1968152/' },
    ],
  },
  {
    id: 'timmer', name: 'Jurrien Timmer', role: 'Fidelity 环球宏观研究总监', weightInPortfolio: 15, hitRate: 0.67, active: true,
    views: [
      { date: '2026-07-06', channel: 'YouTube · Fidelity Connects（已读完整字幕）', title: 'Trust the boom, but verify — 亚洲行后环球宏观解读',
        summary: '完整字幕要点：① 半导体指数仅20倍PE、盈利一年翻三倍，不算泡沫——但周期性行业低PE不代表便宜，需盈利验证；② 建议杠铃：AI增长 + ex-AI（金融、能源），标普下跌日ex-AI反而上涨；③ 欧元区银行股回购强劲、与Mag-7相关性低，是绝佳对冲；④ Mag-7烧钱搞CapEx、回购引擎熄火属「微妙变化」；⑤ 企业盈利同比+30%，周期中段罕见；⑥ Warsh联储口头鹰派意在市场自行收紧，不会真的加息；⑦ 黄金较货币供应超卖13%、未见反转催化剂但适合分段积累，比特币同理；⑧ 韩国散户亢奋≠泡沫信号。',
        stance: [
          { asset: '美股', dir: 'bull', note: '盈利+30%支撑，trust but verify' },
          { asset: '半导体', dir: 'bull', note: '盈利翻三倍，但周期性需验证' },
          { asset: '能源/金融(ex-AI)', dir: 'bull', note: '杠铃另一端' },
          { asset: '欧洲银行/欧股', dir: 'bull', note: '回购+低相关对冲' },
          { asset: '黄金', dir: 'bull', note: '超卖13%，分段积累' },
          { asset: '比特币', dir: 'bull', note: '与黄金同理超卖' },
          { asset: '债券', dir: 'neutral', note: 'Warsh不会真加息' },
        ], url: 'https://www.fidelity.ca/en/insights/videos/the-global-macro-view-timmer-july6/' },
      { date: '2026-07-20', channel: 'YouTube · Fidelity', title: "Jurrien Timmer's global macro view – July 20, 2026",
        summary: '每周环球宏观解读：盈利季表现、利率路径与市场轮动（延续7/6框架）。',
        stance: [{ asset: '美股', dir: 'bull', note: '盈利支撑估值' }],
        url: 'https://www.youtube.com/watch?v=ZgTkruUknbI' },
      { date: '2026-06-15', channel: 'Fidelity 2026年中展望', title: '油价未构成增长冲击；企业盈利保持强劲',
        summary: '霍尔木兹封锁后油价飙至120美元，但通胀调整后油价「没有看起来那么高」，期货曲线回落显示市场预期受控；估值虽高，但价格本身不代表转势。',
        stance: [
          { asset: '美股', dir: 'bull', note: '盈利强劲' },
          { asset: '债券', dir: 'neutral', note: '油价风险受控' },
        ], url: 'https://www.fidelity.com/learning-center/trading-investing/economic-outlook' },
      { date: '2026-04-09', channel: 'AdvisorAnalyst 专栏', title: 'Bent Not Broken',
        summary: '牛市「弯而未折」：调整属健康整固。（事后验证：标普500于6月2日创7,609新高）',
        stance: [{ asset: '美股', dir: 'bull', note: '旧观点，已兑现' }],
        url: 'https://advisoranalyst.com/2026/04/09/jurrien-timmer-bent-not-broken.html/' },
    ],
  },
  {
    id: 'tam', name: '譚新強', role: '中環資產管理董事總經理', weightInPortfolio: 12, hitRate: 0.5, active: true,
    views: [
      { date: '2026-07-18', channel: 'YouTube · @SunChannelHK 譚新強世界ZOOM', title: '美元霸权走进「Profit Dollar」年代 / 晶片美元取代石油？为何台韩日货币走弱',
        summary: '最新框架：美元由「石油美元」进入「利润美元/晶片美元」年代，从M7到兆富翁时代；晶片取代石油成为美元新锚，台韩日为晶片链核心但货币反而走弱——利好晶片链资产而非其货币。',
        stance: [
          { asset: '半导体/晶片链', dir: 'bull', note: '晶片美元新叙事' },
          { asset: '台韩股市', dir: 'bull', note: '晶片链核心（与蔡金強互证）' },
          { asset: '美元资产', dir: 'bull', note: '利润美元延续霸权' },
        ], url: 'https://www.youtube.com/watch?v=iDMSMPTy10s' },
      { date: '2026-07-18', channel: 'YouTube · @SunChannelHK 譚新強世界ZOOM', title: '不可危险假定投资者必将重投中国怀抱',
        summary: '警示：不要假设全球资金一定会回流中国/港股——对「北水定价权」「资金回流」叙事泼冷水，限制对中港资产的加仓幅度。',
        stance: [{ asset: '中港股票', dir: 'bear', note: '资金回流并非必然（对冲信号）' }],
        url: 'https://www.youtube.com/watch?v=J_VQHhrSBTE' },
      { date: '2026-07-24', channel: 'am730 专栏', title: '美股升如「永动鲨鱼」',
        summary: '美国金融市场如鲨鱼般不断向前；即使政治分裂加剧，资本对科技与算力产业的投入仍支撑美股大局。',
        stance: [{ asset: '美股', dir: 'bull', note: '结构性资金流入' }],
        url: 'https://www.am730.com.hk/財經/1043491/' },
      { date: '2026-07-24', channel: 'YouTube · am730', title: '美五大科企AI隐形债务被曝达1.65万亿美元',
        summary: '警示科技巨头表外AI投资杠杆——与「美股不能停」并读：趋势向上但脆弱性累积，限制组合美股加仓幅度。',
        stance: [{ asset: '美股科技', dir: 'bear', note: '隐形债务风险（对冲信号）' }],
        url: 'https://www.youtube.com/watch?v=MfyeWlNLkAI' },
      { date: '2026-07-18', channel: 'YouTube · am730', title: '中美AI造神竞赛美股升势不能停！联储局新主席不敢加息？',
        summary: 'AI竞赛下美股升势难止；利率上行风险有限。中国资金管制趋严，港股楼市成交大跌。',
        stance: [
          { asset: '美股', dir: 'bull', note: 'AI造神竞赛' },
          { asset: '港股', dir: 'neutral', note: '成交受压' },
        ], url: 'https://www.youtube.com/watch?v=ZA8mGkWhVUs' },
      { date: '2026-06-01', channel: 'Master Insight 专栏', title: '内地何时现万亿美元市值企业？',
        summary: '美股领头羊已不再是M7——Micron、Sandisk等记忆体股升幅远超Nvidia，资金在AI链内部轮动。',
        stance: [{ asset: '美股半导体', dir: 'bull', note: 'AI链内部轮动' }],
        url: 'https://www.master-insight.com/article/48564' },
    ],
  },
  {
    id: 'lam', name: '林本利', role: '理大会计及金融学院前副教授 · 活道教育中心创办人', weightInPortfolio: 14, hitRate: 1.0, active: true,
    views: [
      { date: '2026-05-20', channel: 'etnet 专访', title: '港股逢「七」必升，静候沟货时机',
        summary: '2026恒指虽全球包尾，但过去40年逢「七」例升，对2027年三万点目标有信心；持仓奉行本地大蓝筹/内地科技/美股各三分之一；本地蓝筹年初至今升逾20%；趁回吐吸纳中特估（中移动77元提示买入、建行有望破顶）；切勿高追宁德时代/SpaceX。',
        stance: [
          { asset: '港股本地蓝筹', dir: 'bull', note: '高息中特估趁跌买' },
          { asset: '内地科技股', dir: 'neutral', note: '高位跌两三成，候低吸' },
          { asset: '新股/热门股', dir: 'bear', note: '大户解禁出货，勿高追' },
        ], url: 'https://www.etnet.com.hk/www/tc/news/news-article.php?section=features&category=interview&newsid=395433' },
      { date: '2025-10-10', channel: '富途牛牛 专访', title: '大赚700万的「三注投资法」',
        summary: '组合升值超20%先套现部分转定存/高息公用股；分散持有十多只港股；MPF+TVC持续投资年省17%税。',
        stance: [{ asset: '港股高息股', dir: 'bull', note: '旧观点，权重已衰减' }],
        url: 'https://www.futunn.com/learn/detail-lin-benli-the-three-bet-investment-method-that-earned-7-million-91466-250877019' },
    ],
  },
  {
    id: 'lamy', name: '林一鳴', role: '资深投资者 · 香港都会大学助理教授', weightInPortfolio: 8, hitRate: null, active: true,
    views: [
      { date: '2026-06-10', channel: 'YouTube · 新城财经台', title: 'SpaceX IPO、中东局势下息口及汇价、最新股市及楼市分析',
        summary: '中东局势下的息口与汇价走势判断；最新股市楼市部署。',
        stance: [{ asset: '港股', dir: 'neutral', note: '局势观察期' }],
        url: 'https://www.youtube.com/watch?v=E-hGJXPT8qA' },
      { date: '2025-12-01', channel: 'HKET · ET财智Talk', title: '不再「远离港股」？预料恒指明年有望重上28000',
        summary: '调整多年来「珍惜生命，远离港股」的说法，看好两大潜力板块；楼市见底进入上升周期，港元资产受惠。',
        stance: [{ asset: '港股', dir: 'bull', note: '由淡转中性的标志性转向' }],
        url: 'https://inews.hket.com/article/4044666/' },
    ],
  },
  {
    id: 'chong', name: '莊太量', role: '中大全球经济及金融研究所常务所长', weightInPortfolio: 8, hitRate: 0.5, active: true,
    views: [
      { date: '2026-02-10', channel: 'YouTube · 经济人生', title: '2026年香港经济向好靠什么？',
        summary: '多地减息有利香港金融发展；中美贸易战影响微；2026年经济有正增长、港股可看高一线。',
        stance: [
          { asset: '港股', dir: 'bull', note: '减息利好（旧观点，权重已衰减）' },
          { asset: '香港债券', dir: 'bull', note: '利率下行' },
        ], url: 'https://www.youtube.com/watch?v=GZLzPgIm_jY' },
      { date: '2026-06-25', channel: 'YouTube · 经济人生', title: '香港2026年第二季经济增长预测、失业率、通胀、楼市股市',
        summary: '季度经济数据解读：增长、就业与资产价格；中东战事或促使部分避险资金流入香港。',
        stance: [{ asset: '港股', dir: 'neutral', note: '避险资金或流入' }],
        url: 'https://www.youtube.com/watch?v=mzv8fAHjpI8' },
    ],
  },
  {
    id: 'hui', name: '許佳龍', role: '科大协理副校长 · 资讯/商业统计及营运学讲座教授', weightInPortfolio: 3, hitRate: null, active: true,
    views: [
      { date: '2026-04-27', channel: '信报 专栏', title: '预测市场集体智慧测准未来迷思',
        summary: '学术性评论：去中心化预测市场「大众智慧比个人预测更准」的假设存疑，道德风险不容忽视。属方法论观点，不直接构成配置信号，仅作低权重参考。',
        stance: [{ asset: '—', dir: 'neutral', note: '学术观点，不构成市场方向信号' }],
        url: 'https://bm.hkust.edu.hk/school-in-media/2026/04/decentralized-prediction-markets-chinese-version-only' },
    ],
  },
  {
    id: 'au', name: '區偉志', role: '投资专家', weightInPortfolio: 1, hitRate: null, active: false,
    inactiveNote: '截至2026-07-24，于公开渠道（报章/YouTube/社交媒体）未检索到其近1个月的新市场观点。按时间衰减规则，其配置信号权重已降至接近零，仅保留档案；一旦有新观点发布将重新激活。',
    views: [],
  },
]

// 复盘：观点 vs 市场实际
export interface Review {
  expert: string; date: string; view: string; reality: string; verdict: '命中' | '部分命中' | '未兑现' | '观察中'; impact: string
}
export const REVIEWS: Review[] = [
  { expert: '蔡金強', date: '2026-03-13', view: '避开美股锋芒、转吼重资产（HALO前身）；看好韩台、减持日股；油价中枢上移打乱减息',
    reality: '真实行情：EWY韩国 +56.7%、EWT台湾 +50.0%、XLE能源 +26.5%（半年）；6月伊朗冲突油价一度120美元',
    verdict: '命中', impact: '★ 上半年最佳信号。韩台+HALO合计24%仓位贡献组合绝大部分超额收益' },
  { expert: 'Timmer', date: '2026-04-09 / 07-06', view: '牛市 Bent not Broken；半导体盈利翻三倍、20倍PE不算泡沫但需验证',
    reality: '真实行情：标普500半年 +9.6%且6月创新高；SMH半导体 +48.6%（6/22见顶后回落13%）',
    verdict: '命中', impact: 'SMH 8-10%核心仓位为组合第二大收益来源' },
  { expert: '林本利', date: '2026-05-20', view: '本地蓝筹跑赢、内地科技股高位跌两三成',
    reality: '真实行情：EWH香港 +2.3% vs MCHI离岸中国 -12.9%（半年）',
    verdict: '命中', impact: '港股以EWH而非MCHI为主体正确；MCHI仓位(4-5%)仍造成拖累' },
  { expert: '洪灝', date: '2026-01-11', view: '黄金/白银长牛、贵金属是估值之锚',
    reality: '⚠ 真实行情：金价1/29见顶后半年 -15%（自峰值-25%），白银 -39%（自峰值腰斩）',
    verdict: '未兑现', impact: '★ 上半年最大失误。GLD+SLV+COPX 15-16%权重拖累组合约3个百分点；教训：单边叙事观点须设硬性止损/衰减加速规则，6/15还把GLD加至12%是错上加错' },
  { expert: '洪灝', date: '2026-07-16', view: '人民币升值重估中国资产、A股还要创新高',
    reality: '真实行情：ASHR沪深300 半年+3.9%（平稳），但MCHI离岸中国 -12.9%；观点发表仅一周，7月下旬A股延续上行',
    verdict: '观察中', impact: '7/20调仓中国+2pp方向待验证；ASHR与MCHI走势分化提示应以A股在岸工具为主' },
  { expert: '洪灝 / Timmer', date: '2026-06-17 / 07-06', view: '比特币候买入时点 / 与黄金同理超卖可积累',
    reality: '真实行情：IBIT 半年 -27.8%，未见企稳',
    verdict: '未兑现', impact: 'IBIT仅1-2%试探仓，损失可控（约-0.4pp），验证「小仓位试探不确定信号」的风控价值' },
  { expert: '譚新強', date: '2026-07-24', view: '美五大科企AI隐形债务1.65万亿美元',
    reality: '真实行情：SMH自6/22峰值已回落13%、EWY自6/18峰值回落21%——半导体链7月确实转弱',
    verdict: '部分命中', impact: '支持7/20对SMH仅回补至10%而非更高的决定' },
  { expert: '莊太量', date: '2026-02-10', view: '多地减息利香港金融、2026港股看高一线',
    reality: '减息推迟；EWH半年仅+2.3%',
    verdict: '部分命中', impact: '时间衰减后权重已低，未主导配置' },
]

// 观点→ETF适配度检验（防止「看好小盘股却加仓标普500」式错配）
export interface FitCheck {
  signal: string; expert: string; etf: string; fit: number; note: string
}
export const FIT_CHECKS: FitCheck[] = [
  { signal: '人民币升值重估中国资产（7/16）', expert: '洪灝', etf: 'ASHR（非MCHI）', fit: 90, note: '观点明确指向A股在岸重估；真实数据佐证：ASHR半年+3.9% vs MCHI -12.9%，在岸/离岸错配将直接亏损' },
  { signal: '半导体盈利翻三倍、晶片美元', expert: 'Timmer/譚新強', etf: 'SMH', fit: 93, note: '纯半导体上游ETF直接表达；VOO内半导体权重仅约10%，用VOO表达会被稀释10倍' },
  { signal: '美股盈利+30%、牛市未破', expert: 'Timmer', etf: 'VOO', fit: 90, note: '观点指向大盘整体盈利，VOO匹配；若观点指向小盘则必须用IWM而非VOO——本组合未收到小盘信号' },
  { signal: 'HALO重资产低淘汰', expert: '蔡金強', etf: 'XLE/XLB/IFRA', fit: 92, note: '能源+材料+基建三分表达「重资产」；单一XLE会过度集中于油价变量' },
  { signal: '黄金为估值之锚/战略配置', expert: '洪灝', etf: 'GLD', fit: 88, note: '实物金ETF直接表达；不用金矿股ETF(GDX)——其含股票beta，非纯金价敞口' },
  { signal: '看好韩台（晶片链+估值便宜）', expert: '蔡金強/譚新強', etf: 'EWY/EWT', fit: 90, note: '纯单一国家ETF；用亚太宽基表达会混入日股（与减持日股信号矛盾）' },
  { signal: '日圆180/减持日股', expert: '洪灝/蔡金強/譚新強', etf: '（空仓0%）', fit: 95, note: '看空信号的正确表达是零配置，而非买入杠杆反向ETF（不适合中长线）' },
  { signal: '欧洲银行是Mag-7对冲', expert: 'Timmer', etf: 'VGK', fit: 70, note: '适配度中等：VGK为欧洲宽基，银行股权重约20%；精准表达应为EUFN（欧洲银行ETF），列入观察暂不执行' },
  { signal: '比特币超卖可积累', expert: 'Timmer/洪灝', etf: 'IBIT', fit: 85, note: '现货ETF直接表达；但信号已被市场证伪（-27.8%），仓位限制在2%试探级' },
  { signal: '减息受限、最多减一次', expert: '蔡金強', etf: 'TLT小仓/SGOV', fit: 80, note: '减息少于预期不利长久期→TLT仅3%；SGOV在减息推迟下仍有约4%年化' },
]
