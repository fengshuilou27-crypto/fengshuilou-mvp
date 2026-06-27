#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FXTI 角色原型數據庫與結果合成模組
15角色原型：A1-A5純格，B1-B10複合格
"""

# 純格角色（A1-A5）
PURE_PROFILES = {
    'A1': {
        'name': '金型人',
        'element': '金',
        'title': '精準執行者',
        'traits': ['果斷', '理性', '精確', '有原則', '重效率'],
        'strengths': '邏輯思維強，執行力高，重視品質與標準',
        'weaknesses': '可能過於嚴苛，不夠圓融，容易鑽牛角尖',
        'description': '你如金屬般堅毅果斷，做事講求效率與精確。你重視原則，有強烈的正義感，是天生的執行者與標準制定者。',
        'core_contradiction': '內心追求完美與效率，但過度堅持原則可能讓人覺得難以親近',
        'fengshui_advice': '適合居住在方正格局、光線充足、金屬元素適中的環境。方位以西方或西北為佳，樓層可選4、9尾數。避免過於潮濕或陰暗的空間。',
        'color': '#C0C0C0',
        'direction': '西方'
    },
    'A2': {
        'name': '木型人',
        'element': '木',
        'title': '創新成長者',
        'traits': ['積極', '創意', '靈活', '有愛心', '求進步'],
        'strengths': '適應力強，善於創新，具有成長型思維',
        'weaknesses': '可能過於理想化，缺乏耐心，容易三分鐘熱度',
        'description': '你如樹木般充滿生機與成長力量。你熱愛學習，追求進步，總能帶來新想法和新可能。',
        'core_contradiction': '渴望不斷成長與改變，但穩定性不足可能影響長期目標達成',
        'fengshui_advice': '適合居住在綠意盎然、通風良好、有充足自然光的環境。東方或東南方位佳。',
        'color': '#228B22',
        'direction': '東方'
    },
    'A3': {
        'name': '水型人',
        'element': '水',
        'title': '智慧流動者',
        'traits': ['智慧', '冷靜', '適應', '包容', '有深度'],
        'strengths': '洞察力強，善於溝通，能屈能伸，情商高',
        'weaknesses': '可能過於隨波逐流，缺乏主見，容易情緒化',
        'description': '你如流水般智慧且適應力強。你善於觀察與傾聽，能夠在各種環境中找到平衡，是天然的調解者。',
        'core_contradiction': '內心深處渴望安定，但外在的適應力讓人難以捉摸你的真實想法',
        'fengshui_advice': '適合居住在臨近水源或視野開闊的環境。北方位佳，裝飾可加入流動元素。',
        'color': '#1E90FF',
        'direction': '北方'
    },
    'A4': {
        'name': '火型人',
        'element': '火',
        'title': '熱情領導者',
        'traits': ['熱情', '活力', '果斷', '感染力', '愛表現'],
        'strengths': '領導力強，充滿熱情，能激勵他人，行動力強',
        'weaknesses': '可能過於衝動，情緒起伏大，缺乏耐心',
        'description': '你如火焰般熱情且充滿活力。你天生具有領導魅力，能夠感染周圍的人，是團隊的動力來源。',
        'core_contradiction': '熱情如火能照亮他人，但過度燃燒可能導致自己精疲力竭',
        'fengshui_advice': '適合居住在明亮、開闊、朝南的環境。保持空間通風，避免過於悶熱。',
        'color': '#FF4500',
        'direction': '南方'
    },
    'A5': {
        'name': '土型人',
        'element': '土',
        'title': '穩定支持者',
        'traits': ['穩重', '務實', '包容', '可靠', '有耐力'],
        'strengths': '踏實可靠，善於規劃，有強烈的責任感，能包容他人',
        'weaknesses': '可能過於保守，不善變通，容易固執己見',
        'description': '你如大地般穩重且包容。你重視承諾，是值得信賴的夥伴，能夠為他人提供安全感和支持。',
        'core_contradiction': '渴望穩定與和諧，但過度保守可能錯失成長與改變的機會',
        'fengshui_advice': '適合居住在方正、穩重、有厚實感的環境。中央或西南方位佳，裝飾以大地色系為主。',
        'color': '#DAA520',
        'direction': '中央'
    }
}

# 複合格角色（B1-B10）
COMPOSITE_PROFILES = {
    'B1': {
        'name': '金木型',
        'elements': ['金', '木'],
        'title': '革新者',
        'traits': ['精確', '創意', '執行', '改革', '有遠見'],
        'description': '你結合金的精確與木的創新，是天然的改革者。你能夠在既有框架中發掘新可能，並且有效執行。',
        'core_contradiction': '你有破局的衝動，但你的嚴謹讓你難以魯莽行事。這是你的矛盾，也是你的力量。',
        'fengshui_advice': '適合居住在既有結構感又帶有自然元素的環境。東西方位均可，重視功能與美感的平衡。',
        'interaction_type': '相剋（金剋木）'
    },
    'B2': {
        'name': '金水型',
        'elements': ['金', '水'],
        'title': '策略家',
        'traits': ['理性', '智慧', '冷靜', '謀略', '善分析'],
        'description': '你結合金的理性與水的智慧，是天生的策略家。你善於分析形勢，做出最優決策。',
        'core_contradiction': '你兼具金的理性與水的智慧，兩種能量互相滋養。學會在分析與直覺之間找到流動的平衡，是你的成長課題。',
        'fengshui_advice': '適合居住在安靜、整潔、有書房或思考空間的環境。西北方位佳。',
        'interaction_type': '相生（金生水）'
    },
    'B3': {
        'name': '金火型',
        'elements': ['金', '火'],
        'title': '執行者',
        'traits': ['果斷', '熱情', '行動', '領導', '有衝勁'],
        'description': '你結合金的果斷與火的熱情，是天生的執行者。你說到做到，充滿行動力和影響力。',
        'core_contradiction': '熱情驅動（火）與理性控制（金）的碰撞，可能讓你時而衝動時而壓抑。這是你的矛盾，也是你的力量。',
        'fengshui_advice': '適合居住在明亮、開闊、有金屬裝飾的現代空間。西方或南方位均可。',
        'interaction_type': '相剋（火剋金）'
    },
    'B4': {
        'name': '金土型',
        'elements': ['金', '土'],
        'title': '建構者',
        'traits': ['務實', '穩定', '精確', '可靠', '有規劃'],
        'description': '你結合金的精確與土的穩定，是天生的建構者。你能夠建立穩固的基礎，並且持續優化。',
        'core_contradiction': '你兼具金的精確與土的穩定，兩種能量互相支持。學會在效率與品質之間找到節奏，而非苛責自己或他人，是你的成長課題。',
        'fengshui_advice': '適合居住在結構堅固、裝修精緻、有品質感的環境。西南方或西方位佳。',
        'interaction_type': '相生（土生金）'
    },
    'B5': {
        'name': '木水型',
        'elements': ['木', '水'],
        'title': '創造者',
        'traits': ['創意', '靈活', '智慧', '適應', '有想像力'],
        'description': '你結合木的創意與水的智慧，是天生的創造者。你思維活躍，能夠產生獨特的點子。',
        'core_contradiction': '你兼具木的創意與水的智慧，兩種能量互相滋養。學會將靈感轉化為具體行動，而非讓想法流於發散，是你的成長課題。',
        'fengshui_advice': '適合居住在綠意與水景兼具的環境。東方或北方位均可，重視自然元素。',
        'interaction_type': '相生（水生木）'
    },
    'B6': {
        'name': '木火型',
        'elements': ['木', '火'],
        'title': '激勵者',
        'traits': ['熱情', '成長', '活力', '感染', '有願景'],
        'description': '你結合木的成長與火的熱情，是天生的激勵者。你能夠激發潛能，帶動周圍的人一起成長。',
        'core_contradiction': '你兼具木的成長力與火的熱情，兩種能量互相推動。學會在擴張與休息之間找到節奏，避免過度燃燒，是你的成長課題。',
        'fengshui_advice': '適合居住在充滿生機、陽光充足的環境。東方或南方位均可，重視開闊感。',
        'interaction_type': '相生（木生火）'
    },
    'B7': {
        'name': '木土型',
        'elements': ['木', '土'],
        'title': '培育者',
        'traits': ['穩定', '成長', '耐心', '包容', '有愛心'],
        'description': '你結合木的成長與土的穩定，是天生的培育者。你能夠耐心地支持他人成長，提供穩定的環境。',
        'core_contradiction': '渴望改變（木）與追求穩定（土）的內在衝突，可能讓你抗拒必要的改變。這是你的矛盾，也是你的力量。',
        'fengshui_advice': '適合居住在穩重且帶有綠意的環境。東南方或中央位佳，重視花園或陽台。',
        'interaction_type': '相剋（木剋土）'
    },
    'B8': {
        'name': '水火型',
        'elements': ['水', '火'],
        'title': '調和者',
        'traits': ['平衡', '智慧', '熱情', '溝通', '有魅力'],
        'description': '你結合水的智慧與火的熱情，是天生的調和者。你能夠在對立中找到平衡，化解衝突。',
        'core_contradiction': '情緒的冷熱交替（水與火）讓你內在充滿張力，需要學習平衡表達。這是你的矛盾，也是你的力量。',
        'fengshui_advice': '適合居住在溫暖與清涼元素兼具的環境。南方或北方位均可，重視空間平衡。',
        'interaction_type': '相剋（水剋火）'
    },
    'B9': {
        'name': '水土型',
        'elements': ['水', '土'],
        'title': '滋養者',
        'traits': ['包容', '穩定', '智慧', '滋養', '有耐心'],
        'description': '你結合水的智慧與土的包容，是天生的滋養者。你能夠提供情感支持，並且穩定地陪伴他人。',
        'core_contradiction': '情感的流動（水）與責任的穩定（土）可能讓你過度承擔而忽略自我需求。這是你的矛盾，也是你的力量。',
        'fengshui_advice': '適合居住在溫潤、舒適、有安全感的環境。北方或中央位佳，重視臥室品質。',
        'interaction_type': '相剋（土剋水）'
    },
    'B10': {
        'name': '火土型',
        'elements': ['火', '土'],
        'title': '凝聚者',
        'traits': ['熱情', '穩定', '領導', '包容', '有凝聚力'],
        'description': '你結合火的熱情與土的穩定，是天生的凝聚者。你能夠團結人心，建立穩固的社群。',
        'core_contradiction': '你兼具火的熱情與土的穩定，兩種能量互相支持。學會在帶領他人與照顧自己之間找到平衡，避免承擔過多責任，是你的成長課題。',
        'fengshui_advice': '適合居住在開闊且穩重的環境。南方或中央位佳，重視公共空間。',
        'interaction_type': '相生（火生土）'
    }
}

# 所有角色
ALL_PROFILES = {**PURE_PROFILES, **COMPOSITE_PROFILES}

# 複合格 map 使用的元素排序（與 composite_map 鍵名一致）
_ELEMENT_ORDER = {'金': 0, '木': 1, '水': 2, '火': 3, '土': 4}


def determine_profile(wuxing_percentage, threshold_pure=30, threshold_gap=20):
    """
    判定角色原型
    Args:
        wuxing_percentage: dict, 五行百分比
        threshold_pure: int, 純格判定門檻（top1百分比）
        threshold_gap: int, 純格判定門檻（top1-top2差距）
    Returns:
        dict: 角色信息
    """
    sorted_wuxing = sorted(wuxing_percentage.items(), key=lambda x: x[1], reverse=True)
    top1_element, top1_pct = sorted_wuxing[0]
    top2_element, top2_pct = sorted_wuxing[1]

    gap = top1_pct - top2_pct

    if top1_pct >= threshold_pure and gap >= threshold_gap:
        element_to_profile = {'金': 'A1', '木': 'A2', '水': 'A3', '火': 'A4', '土': 'A5'}
        profile_id = element_to_profile[top1_element]
        profile_type = 'pure'
    else:
        # FIX: 使用與 composite_map 鍵名一致的元素排序，避免 Unicode 排序錯配
        composite_key = ''.join(
            sorted([top1_element, top2_element], key=lambda e: _ELEMENT_ORDER[e])
        )
        composite_map = {
            '金木': 'B1', '金水': 'B2', '金火': 'B3', '金土': 'B4',
            '木水': 'B5', '木火': 'B6', '木土': 'B7',
            '水火': 'B8', '水土': 'B9', '火土': 'B10'
        }
        profile_id = composite_map.get(composite_key, 'B1')
        profile_type = 'composite'

    profile = ALL_PROFILES[profile_id].copy()
    profile['id'] = profile_id
    profile['type'] = profile_type
    profile['top_elements'] = [top1_element, top2_element]
    profile['top_percentages'] = [top1_pct, top2_pct]
    profile['all_percentages'] = wuxing_percentage

    return profile


def synthesize_result(innate_pct, acquired_pct, innate_weight=0.4, acquired_weight=0.6):
    """
    合成先天與後天五行百分比
    """
    final_pct = {}
    for element in innate_pct:
        final_pct[element] = round(
            innate_pct[element] * innate_weight + acquired_pct[element] * acquired_weight,
            2
        )

    total = sum(final_pct.values())
    if total > 0:
        final_pct = {k: round(v / total * 100, 2) for k, v in final_pct.items()}

    return final_pct
