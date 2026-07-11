/**
 * FXTI 15 角色原型完整數據
 * A1-A5: 純格 | B1-B10: 複合格
 */

export interface FXTIProfile {
  id: string;
  type: 'pure' | 'composite';
  name: string;
  elements: string[];
  title: string;
  traits: string[];
  strengths: string;
  weaknesses: string;
  description: string;
  coreContradiction: string;
  fengshuiAdvice: string;
  color: string;
  colorSecondary: string;
  direction: string;
  interactionType?: string;
  icon: string;
  symbol: string;
  bgGradient: string;
}

// 五行色彩映射
export const ELEMENT_COLORS: Record<string, { primary: string; secondary: string; gradient: string; symbol: string }> = {
  '金': {
    primary: '#C0C0C0',
    secondary: '#8B8680',
    gradient: 'from-gray-100 to-gray-300',
    symbol: '⚙️',
  },
  '木': {
    primary: '#228B22',
    secondary: '#1a6b1a',
    gradient: 'from-green-100 to-green-300',
    symbol: '🌿',
  },
  '水': {
    primary: '#1E90FF',
    secondary: '#1565c0',
    gradient: 'from-blue-100 to-blue-300',
    symbol: '💧',
  },
  '火': {
    primary: '#FF4500',
    secondary: '#d32f2f',
    gradient: 'from-red-100 to-orange-300',
    symbol: '🔥',
  },
  '土': {
    primary: '#DAA520',
    secondary: '#b8860b',
    gradient: 'from-yellow-100 to-amber-300',
    symbol: '🏔️',
  },
};

export const FXTI_PROFILES: Record<string, FXTIProfile> = {
  // ===== 純格 A1-A5 =====
  A1: {
    id: 'A1',
    type: 'pure',
    name: '金型人',
    elements: ['金'],
    title: '精準執行者',
    traits: ['果斷', '理性', '精確', '有原則', '重效率'],
    strengths: '邏輯思維強，執行力高，重視品質與標準',
    weaknesses: '可能過於嚴苛，不夠圓融，容易鑽牛角尖',
    description: '你如金屬般堅毅果斷，做事講求效率與精確。你重視原則，有強烈的正義感，是天生的執行者與標準制定者。',
    coreContradiction: '內心追求完美與效率，但過度堅持原則可能讓人覺得難以親近',
    fengshuiAdvice: '適合居住在方正格局、光線充足、金屬元素適中的環境。方位以西方或西北為佳，樓層可選4、9尾數。避免過於潮濕或陰暗的空間。',
    color: '#C0C0C0',
    colorSecondary: '#8B8680',
    direction: '西方',
    icon: 'Scale',
    symbol: '⚙️',
    bgGradient: 'from-gray-50 via-gray-100 to-slate-200',
  },
  A2: {
    id: 'A2',
    type: 'pure',
    name: '木型人',
    elements: ['木'],
    title: '創新成長者',
    traits: ['積極', '創意', '靈活', '有愛心', '求進步'],
    strengths: '適應力強，善於創新，具有成長型思維',
    weaknesses: '可能過於理想化，缺乏耐心，容易三分鐘熱度',
    description: '你如樹木般充滿生機與成長力量。你熱愛學習，追求進步，總能帶來新想法和新可能。',
    coreContradiction: '渴望不斷成長與改變，但穩定性不足可能影響長期目標達成',
    fengshuiAdvice: '適合居住在綠意盎然、通風良好、有充足自然光的環境。東方或東南方位佳。',
    color: '#228B22',
    colorSecondary: '#1a6b1a',
    direction: '東方',
    icon: 'TreePine',
    symbol: '🌿',
    bgGradient: 'from-green-50 via-emerald-100 to-teal-200',
  },
  A3: {
    id: 'A3',
    type: 'pure',
    name: '水型人',
    elements: ['水'],
    title: '智慧流動者',
    traits: ['智慧', '冷靜', '適應', '包容', '有深度'],
    strengths: '洞察力強，善於溝通，能屈能伸，情商高',
    weaknesses: '可能過於隨波逐流，缺乏主見，容易情緒化',
    description: '你如流水般智慧且適應力強。你善於觀察與傾聽，能夠在各種環境中找到平衡，是天然的調解者。',
    coreContradiction: '內心深處渴望安定，但外在的適應力讓人難以捉摸你的真實想法',
    fengshuiAdvice: '適合居住在臨近水源或視野開闊的環境。北方位佳，裝飾可加入流動元素。',
    color: '#1E90FF',
    colorSecondary: '#1565c0',
    direction: '北方',
    icon: 'Waves',
    symbol: '💧',
    bgGradient: 'from-blue-50 via-sky-100 to-cyan-200',
  },
  A4: {
    id: 'A4',
    type: 'pure',
    name: '火型人',
    elements: ['火'],
    title: '熱情領導者',
    traits: ['熱情', '活力', '果斷', '感染力', '愛表現'],
    strengths: '領導力強，充滿熱情，能激勵他人，行動力強',
    weaknesses: '可能過於衝動，情緒起伏大，缺乏耐心',
    description: '你如火焰般熱情且充滿活力。你天生具有領導魅力，能夠感染周圍的人，是團隊的動力來源。',
    coreContradiction: '熱情如火能照亮他人，但過度燃燒可能導致自己精疲力竭',
    fengshuiAdvice: '適合居住在明亮、開闊、朝南的環境。保持空間通風，避免過於悶熱。',
    color: '#FF4500',
    colorSecondary: '#d32f2f',
    direction: '南方',
    icon: 'Flame',
    symbol: '🔥',
    bgGradient: 'from-orange-50 via-red-100 to-rose-200',
  },
  A5: {
    id: 'A5',
    type: 'pure',
    name: '土型人',
    elements: ['土'],
    title: '穩定支持者',
    traits: ['穩重', '務實', '包容', '可靠', '有耐力'],
    strengths: '踏實可靠，善於規劃，有強烈的責任感，能包容他人',
    weaknesses: '可能過於保守，不善變通，容易固執己見',
    description: '你如大地般穩重且包容。你重視承諾，是值得信賴的夥伴，能夠為他人提供安全感和支持。',
    coreContradiction: '渴望穩定與和諧，但過度保守可能錯失成長與改變的機會',
    fengshuiAdvice: '適合居住在方正、穩重、有厚實感的環境。中央或西南方位佳，裝飾以大地色系為主。',
    color: '#DAA520',
    colorSecondary: '#b8860b',
    direction: '中央',
    icon: 'Mountain',
    symbol: '🏔️',
    bgGradient: 'from-amber-50 via-yellow-100 to-orange-200',
  },

  // ===== 複合格 B1-B10 =====
  B1: {
    id: 'B1',
    type: 'composite',
    name: '金木型',
    elements: ['金', '木'],
    title: '革新者',
    traits: ['精確', '創意', '執行', '改革', '有遠見'],
    strengths: '能夠在既有框架中發掘新可能，並且有效執行',
    weaknesses: '有破局的衝動，但嚴謹讓你難以魯莽行事',
    description: '你結合金的精確與木的創新，是天然的改革者。你能夠在既有框架中發掘新可能，並且有效執行。',
    coreContradiction: '你有破局的衝動，但你的嚴謹讓你難以魯莽行事。這是你的矛盾，也是你的力量。',
    fengshuiAdvice: '適合居住在既有結構感又帶有自然元素的環境。東西方位均可，重視功能與美感的平衡。',
    color: '#6B8E23',
    colorSecondary: '#556b2f',
    direction: '東西皆宜',
    interactionType: '相剋（金剋木）',
    icon: 'Lightbulb',
    symbol: '💡',
    bgGradient: 'from-gray-50 via-green-100 to-emerald-200',
  },
  B2: {
    id: 'B2',
    type: 'composite',
    name: '金水型',
    elements: ['金', '水'],
    title: '策略家',
    traits: ['理性', '智慧', '冷靜', '謀略', '善分析'],
    strengths: '善於分析形勢，做出最優決策',
    weaknesses: '可能過度分析，行動力不足',
    description: '你結合金的理性與水的智慧，是天生的策略家。你善於分析形勢，做出最優決策。',
    coreContradiction: '你兼具金的理性與水的智慧，兩種能量互相滋養。學會在分析與直覺之間找到流動的平衡，是你的成長課題。',
    fengshuiAdvice: '適合居住在安靜、整潔、有書房或思考空間的環境。西北方位佳。',
    color: '#5F9EA0',
    colorSecondary: '#4a7c7e',
    direction: '西北',
    interactionType: '相生（金生水）',
    icon: 'Brain',
    symbol: '🧠',
    bgGradient: 'from-slate-50 via-cyan-100 to-teal-200',
  },
  B3: {
    id: 'B3',
    type: 'composite',
    name: '金火型',
    elements: ['金', '火'],
    title: '執行者',
    traits: ['果斷', '熱情', '行動', '領導', '有衝勁'],
    strengths: '說到做到，充滿行動力和影響力',
    weaknesses: '熱情與理性的碰撞可能導致衝動或壓抑',
    description: '你結合金的果斷與火的熱情，是天生的執行者。你說到做到，充滿行動力和影響力。',
    coreContradiction: '熱情驅動（火）與理性控制（金）的碰撞，可能讓你時而衝動時而壓抑。這是你的矛盾，也是你的力量。',
    fengshuiAdvice: '適合居住在明亮、開闊、有金屬裝飾的現代空間。西方或南方位均可。',
    color: '#CD853F',
    colorSecondary: '#a0522d',
    direction: '西/南',
    interactionType: '相剋（火剋金）',
    icon: 'Zap',
    symbol: '⚡',
    bgGradient: 'from-orange-50 via-amber-100 to-yellow-200',
  },
  B4: {
    id: 'B4',
    type: 'composite',
    name: '金土型',
    elements: ['金', '土'],
    title: '建構者',
    traits: ['務實', '穩定', '精確', '可靠', '有規劃'],
    strengths: '能夠建立穩固的基礎，並且持續優化',
    weaknesses: '可能過於注重細節，缺乏靈活性',
    description: '你結合金的精確與土的穩定，是天生的建構者。你能夠建立穩固的基礎，並且持續優化。',
    coreContradiction: '你兼具金的精確與土的穩定，兩種能量互相支持。學會在效率與品質之間找到節奏，而非苛責自己或他人，是你的成長課題。',
    fengshuiAdvice: '適合居住在結構堅固、裝修精緻、有品質感的環境。西南方或西方位佳。',
    color: '#BDB76B',
    colorSecondary: '#9a8b4f',
    direction: '西南',
    interactionType: '相生（土生金）',
    icon: 'Building2',
    symbol: '🏗️',
    bgGradient: 'from-yellow-50 via-amber-100 to-stone-200',
  },
  B5: {
    id: 'B5',
    type: 'composite',
    name: '木水型',
    elements: ['木', '水'],
    title: '創造者',
    traits: ['創意', '靈活', '智慧', '適應', '有想像力'],
    strengths: '思維活躍，能夠產生獨特的點子',
    weaknesses: '想法可能過於發散，難以落地執行',
    description: '你結合木的創意與水的智慧，是天生的創造者。你思維活躍，能夠產生獨特的點子。',
    coreContradiction: '你兼具木的創意與水的智慧，兩種能量互相滋養。學會將靈感轉化為具體行動，而非讓想法流於發散，是你的成長課題。',
    fengshuiAdvice: '適合居住在綠意與水景兼具的環境。東方或北方位均可，重視自然元素。',
    color: '#20B2AA',
    colorSecondary: '#008b8b',
    direction: '東/北',
    interactionType: '相生（水生木）',
    icon: 'Palette',
    symbol: '🎨',
    bgGradient: 'from-teal-50 via-green-100 to-cyan-200',
  },
  B6: {
    id: 'B6',
    type: 'composite',
    name: '木火型',
    elements: ['木', '火'],
    title: '激勵者',
    traits: ['熱情', '成長', '活力', '感染', '有願景'],
    strengths: '能夠激發潛能，帶動周圍的人一起成長',
    weaknesses: '可能過度燃燒，需要學習休息',
    description: '你結合木的成長與火的熱情，是天生的激勵者。你能夠激發潛能，帶動周圍的人一起成長。',
    coreContradiction: '你兼具木的成長力與火的熱情，兩種能量互相推動。學會在擴張與休息之間找到節奏，避免過度燃燒，是你的成長課題。',
    fengshuiAdvice: '適合居住在充滿生機、陽光充足的環境。東方或南方位均可，重視開闊感。',
    color: '#FF8C00',
    colorSecondary: '#e67e00',
    direction: '東/南',
    interactionType: '相生（木生火）',
    icon: 'Sun',
    symbol: '☀️',
    bgGradient: 'from-lime-50 via-green-100 to-orange-200',
  },
  B7: {
    id: 'B7',
    type: 'composite',
    name: '木土型',
    elements: ['木', '土'],
    title: '培育者',
    traits: ['穩定', '成長', '耐心', '包容', '有愛心'],
    strengths: '能夠耐心地支持他人成長，提供穩定的環境',
    weaknesses: '可能抗拒必要的改變，過度保護',
    description: '你結合木的成長與土的穩定，是天生的培育者。你能夠耐心地支持他人成長，提供穩定的環境。',
    coreContradiction: '渴望改變（木）與追求穩定（土）的內在衝突，可能讓你抗拒必要的改變。這是你的矛盾，也是你的力量。',
    fengshuiAdvice: '適合居住在穩重且帶有綠意的環境。東南方或中央位佳，重視花園或陽台。',
    color: '#9ACD32',
    colorSecondary: '#7cb342',
    direction: '東南',
    interactionType: '相剋（木剋土）',
    icon: 'Sprout',
    symbol: '🌱',
    bgGradient: 'from-green-50 via-lime-100 to-yellow-200',
  },
  B8: {
    id: 'B8',
    type: 'composite',
    name: '水火型',
    elements: ['水', '火'],
    title: '調和者',
    traits: ['平衡', '智慧', '熱情', '溝通', '有魅力'],
    strengths: '能夠在對立中找到平衡，化解衝突',
    weaknesses: '情緒冷熱交替，內在充滿張力',
    description: '你結合水的智慧與火的熱情，是天生的調和者。你能夠在對立中找到平衡，化解衝突。',
    coreContradiction: '情緒的冷熱交替（水與火）讓你內在充滿張力，需要學習平衡表達。這是你的矛盾，也是你的力量。',
    fengshuiAdvice: '適合居住在溫暖與清涼元素兼具的環境。南方或北方位均可，重視空間平衡。',
    color: '#9370DB',
    colorSecondary: '#7b68ee',
    direction: '南/北',
    interactionType: '相剋（水剋火）',
    icon: 'YinYang',
    symbol: '☯️',
    bgGradient: 'from-purple-50 via-pink-100 to-red-200',
  },
  B9: {
    id: 'B9',
    type: 'composite',
    name: '水土型',
    elements: ['水', '土'],
    title: '滋養者',
    traits: ['包容', '穩定', '智慧', '滋養', '有耐心'],
    strengths: '能夠提供情感支持，並且穩定地陪伴他人',
    weaknesses: '可能過度承擔，忽略自我需求',
    description: '你結合水的智慧與土的包容，是天生的滋養者。你能夠提供情感支持，並且穩定地陪伴他人。',
    coreContradiction: '情感的流動（水）與責任的穩定（土）可能讓你過度承擔而忽略自我需求。這是你的矛盾，也是你的力量。',
    fengshuiAdvice: '適合居住在溫潤、舒適、有安全感的環境。北方或中央位佳，重視臥室品質。',
    color: '#4682B4',
    colorSecondary: '#3d6a9c',
    direction: '北/中',
    interactionType: '相剋（土剋水）',
    icon: 'Heart',
    symbol: '💙',
    bgGradient: 'from-blue-50 via-indigo-100 to-slate-200',
  },
  B10: {
    id: 'B10',
    type: 'composite',
    name: '火土型',
    elements: ['火', '土'],
    title: '凝聚者',
    traits: ['熱情', '穩定', '領導', '包容', '有凝聚力'],
    strengths: '能夠團結人心，建立穩固的社群',
    weaknesses: '可能承擔過多責任，忽視自身需求',
    description: '你結合火的熱情與土的穩定，是天生的凝聚者。你能夠團結人心，建立穩固的社群。',
    coreContradiction: '你兼具火的熱情與土的穩定，兩種能量互相支持。學會在帶領他人與照顧自己之間找到平衡，避免承擔過多責任，是你的成長課題。',
    fengshuiAdvice: '適合居住在開闊且穩重的環境。南方或中央位佳，重視公共空間。',
    color: '#D2691E',
    colorSecondary: '#b3591a',
    direction: '南/中',
    interactionType: '相生（火生土）',
    icon: 'Users',
    symbol: '👥',
    bgGradient: 'from-orange-50 via-red-100 to-amber-200',
  },
};

export const PURE_PROFILE_IDS = ['A1', 'A2', 'A3', 'A4', 'A5'];
export const COMPOSITE_PROFILE_IDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10'];
export const ALL_PROFILE_IDS = [...PURE_PROFILE_IDS, ...COMPOSITE_PROFILE_IDS];

// 五行關係說明
export const WUXING_RELATIONS: Record<string, { relation: string; description: string }> = {
  '金木': { relation: '相剋', description: '金剋木 — 金的精確約束木的散漫，但也可能限制創意' },
  '金水': { relation: '相生', description: '金生水 — 金的理性滋養水的智慧，相得益彰' },
  '金火': { relation: '相剋', description: '火剋金 — 火的熱情融化金的堅持，充滿張力' },
  '金土': { relation: '相生', description: '土生金 — 土的穩定孕育金的精確，基礎堅實' },
  '木水': { relation: '相生', description: '水生木 — 水的智慧滋養木的創意，靈感源源' },
  '木火': { relation: '相生', description: '木生火 — 木的成長點燃火的熱情，生生不息' },
  '木土': { relation: '相剋', description: '木剋土 — 木的變革動搖土的穩定，需要平衡' },
  '水火': { relation: '相剋', description: '水剋火 — 水的冷靜澆滅火的衝動，調和對立' },
  '水土': { relation: '相剋', description: '土剋水 — 土的穩定阻擋水的流動，需要空間' },
  '火土': { relation: '相生', description: '火生土 — 火的熱情溫暖土的包容，凝聚力量' },
};

// 輔助函數：根據五行百分比判斷角色
export function determineProfile(wuxingPercentage: Record<string, number>, thresholdPure = 30, thresholdGap = 20) {
  const sorted = Object.entries(wuxingPercentage).sort((a, b) => b[1] - a[1]);
  const [top1Element, top1Pct] = sorted[0];
  const [top2Element, top2Pct] = sorted[1];
  const gap = top1Pct - top2Pct;

  const elementOrder: Record<string, number> = { '金': 0, '木': 1, '水': 2, '火': 3, '土': 4 };

  let profileId: string;
  let profileType: 'pure' | 'composite';

  if (top1Pct >= thresholdPure && gap >= thresholdGap) {
    const elementToProfile: Record<string, string> = { '金': 'A1', '木': 'A2', '水': 'A3', '火': 'A4', '土': 'A5' };
    profileId = elementToProfile[top1Element];
    profileType = 'pure';
  } else {
    const compositeKey = [top1Element, top2Element].sort((a, b) => elementOrder[a] - elementOrder[b]).join('');
    const compositeMap: Record<string, string> = {
      '金木': 'B1', '金水': 'B2', '金火': 'B3', '金土': 'B4',
      '木水': 'B5', '木火': 'B6', '木土': 'B7',
      '水火': 'B8', '水土': 'B9', '火土': 'B10',
    };
    profileId = compositeMap[compositeKey] || 'B1';
    profileType = 'composite';
  }

  const profile = FXTI_PROFILES[profileId];
  return {
    ...profile,
    topElements: [top1Element, top2Element],
    topPercentages: [top1Pct, top2Pct],
    allPercentages: wuxingPercentage,
  };
}

// 輔助函數：合成先天與後天五行
export function synthesizeResult(
  innatePct: Record<string, number>,
  acquiredPct: Record<string, number>,
  innateWeight = 0.4,
  acquiredWeight = 0.6
) {
  const finalPct: Record<string, number> = {};
  for (const element of Object.keys(innatePct)) {
    finalPct[element] = Math.round(
      (innatePct[element] * innateWeight + acquiredPct[element] * acquiredWeight) * 100
    ) / 100;
  }
  const total = Object.values(finalPct).reduce((a, b) => a + b, 0);
  if (total > 0) {
    for (const element of Object.keys(finalPct)) {
      finalPct[element] = Math.round((finalPct[element] / total) * 10000) / 100;
    }
  }
  return finalPct;
}
