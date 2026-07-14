#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FXTI v3.0 六維度關係分析引擎
基於注定APP功能融合方案升級

六維度：
1. 五行命理 (25%) - 已有
2. 三觀契合 (20%) - 新增
3. 性格互補 (20%) - 擴展
4. 歲月磨合 (15%) - 已有
5. 溝通模式 (10%) - 新增
6. 目標一致性 (10%) - 新增
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# 導入現有模組
from data.fxti_relationship import (
    cosine_similarity, complement_score, determine_relation_type,
    generate_relationship_text, generate_combined_fengshui,
    generate_space_layout, generate_color_scheme
)
from data.fxti_timing_engine import analyze_timing_compatibility


# ============ 三觀契合度引擎 ============

VALUES_QUESTIONS = {
    "family": [
        {"id": "f1", "text": "婚後是否願意與父母同住？", "options": ["非常願意", "可以考慮", "視情況而定", "不太願意", "絕對不願意"]},
        {"id": "f2", "text": "你認為家庭在人生中的優先級？", "options": ["第一優先", "非常重要", "重要", "一般", "事業優先"]},
        {"id": "f3", "text": "育兒責任應該如何分配？", "options": ["完全共同承擔", "主要共同承擔", "分工明確", "傳統分工", "一方為主"]},
        {"id": "f4", "text": "你希望有幾個孩子？", "options": ["3個以上", "2個", "1個", "0個", "順其自然"]},
        {"id": "f5", "text": "家庭節日應該如何度過？", "options": ["大家族團聚", "小家庭為主", "雙方家庭輪流", "旅行度假", "各自安排"]},
    ],
    "money": [
        {"id": "m1", "text": "你的消費習慣是？", "options": ["精打細算", "量入為出", "適度消費", "享受生活", "隨心所欲"]},
        {"id": "m2", "text": "婚後財務應該如何管理？", "options": ["完全共同", "主要共同", "AA制", "各自獨立", "一方管理"]},
        {"id": "m3", "text": "你願意為體驗花多少錢？", "options": ["幾乎不花", "少量預算", "適度花費", "願意投資", "不惜代價"]},
        {"id": "m4", "text": "儲蓄佔收入的比例？", "options": ["50%以上", "30-50%", "20-30%", "10-20%", "幾乎不儲蓄"]},
        {"id": "m5", "text": "對方有債務，你的態度？", "options": ["完全接受", "可以理解", "視情況而定", "需要考慮", "難以接受"]},
    ],
    "career": [
        {"id": "c1", "text": "工作與生活平衡？", "options": ["生活優先", "偏向生活", "平衡", "偏向工作", "工作優先"]},
        {"id": "c2", "text": "對方事業比你成功，你的感受？", "options": ["非常自豪", "為對方高興", "平常心", "有些壓力", "難以接受"]},
        {"id": "c3", "text": "是否支持對方為事業異地發展？", "options": ["全力支持", "支持", "視情況", "不太支持", "不支持"]},
        {"id": "c4", "text": "你對職業發展的期望？", "options": ["追求頂峰", "穩步上升", "保持現狀", "工作穩定", "隨遇而安"]},
        {"id": "c5", "text": "週末加班的接受度？", "options": ["完全接受", "偶爾可以", "視情況", "盡量避免", "絕不接受"]},
    ],
    "social": [
        {"id": "s1", "text": "朋友在你生活中的重要性？", "options": ["非常重要", "重要", "一般", "不太重要", "不重要"]},
        {"id": "s2", "text": "你喜歡的社交頻率？", "options": ["每天", "每週幾次", "每週一次", "每月幾次", "很少"]},
        {"id": "s3", "text": "獨處時間的需求？", "options": ["不需要", "少量", "適中", "較多", "非常多"]},
        {"id": "s4", "text": "對方異性朋友的接受度？", "options": ["完全接受", "可以理解", "視情況", "有些介意", "難以接受"]},
        {"id": "s5", "text": "社交活動的偏好？", "options": ["大型派對", "小型聚會", "一對一", "線上交流", "不社交"]},
    ],
    "lifestyle": [
        {"id": "l1", "text": "作息習慣？", "options": ["早睡早起", "規律作息", "彈性作息", "經常熬夜", "夜貓子"]},
        {"id": "l2", "text": "飲食偏好？", "options": ["健康飲食", "均衡飲食", "隨意飲食", "外食為主", "不挑食"]},
        {"id": "l3", "text": "休閒活動偏好？", "options": ["戶外運動", "室內活動", "兩者皆可", "動態活動", "靜態活動"]},
        {"id": "l4", "text": "居家整潔度要求？", "options": ["一塵不染", "整潔有序", "適度整潔", "有些凌亂", "隨性自然"]},
        {"id": "l5", "text": "旅行偏好？", "options": ["自由行探索", "跟團省心", "豪華度假", "背包客", "宅在家"]},
    ],
    "life_goals": [
        {"id": "g1", "text": "1-3年內最重要的目標？", "options": ["事業突破", "穩定發展", "建立家庭", "環遊世界", "自我提升"]},
        {"id": "g2", "text": "3-10年的生活願景？", "options": ["事業有成", "家庭美滿", "財務自由", "環遊世界", "社會貢獻"]},
        {"id": "g3", "text": "對退休生活的想像？", "options": ["環遊世界", "含飴弄孫", "繼續工作", "田園生活", "城市養老"]},
        {"id": "g4", "text": "人生最重要的價值？", "options": ["家庭幸福", "事業成就", "財富積累", "自我實現", "社會貢獻"]},
        {"id": "g5", "text": "對方的人生目標與你不同，你會？", "options": ["全力支持", "尊重理解", "協商調整", "有些困擾", "難以接受"]},
    ]
}


def get_values_questionnaire() -> Dict[str, Any]:
    """獲取完整三觀問卷"""
    return {
        "total_questions": 30,
        "categories": {
            "family": {"name": "家庭觀", "questions": VALUES_QUESTIONS["family"], "weight": 0.25},
            "money": {"name": "金錢觀", "questions": VALUES_QUESTIONS["money"], "weight": 0.25},
            "career": {"name": "事業觀", "questions": VALUES_QUESTIONS["career"], "weight": 0.20},
            "social": {"name": "社交觀", "questions": VALUES_QUESTIONS["social"], "weight": 0.15},
            "lifestyle": {"name": "生活方式", "questions": VALUES_QUESTIONS["lifestyle"], "weight": 0.10},
            "life_goals": {"name": "人生目標", "questions": VALUES_QUESTIONS["life_goals"], "weight": 0.05},
        }
    }


def analyze_values_compatibility(answers_a: Dict[str, int], answers_b: Dict[str, int]) -> Dict[str, Any]:
    """
    三觀契合度分析
    
    算法：
    - 同一題目選項差異 <= 1：高度契合（+5分）
    - 同一題目選項差異 = 2：中度契合（+3分）
    - 同一題目選項差異 = 3：低度契合（+1分）
    - 同一題目選項差異 >= 4：不契合（0分）
    
    加權：家庭觀25% + 金錢觀25% + 事業觀20% + 社交觀15% + 生活方式10% + 人生目標5%
    """
    category_scores = {}
    category_details = {}
    
    for cat_key, cat_data in VALUES_QUESTIONS.items():
        cat_scores = []
        for q in cat_data:
            qid = q["id"]
            if qid in answers_a and qid in answers_b:
                diff = abs(answers_a[qid] - answers_b[qid])
                if diff <= 1:
                    score = 5
                elif diff == 2:
                    score = 3
                elif diff == 3:
                    score = 1
                else:
                    score = 0
                cat_scores.append(score)
        
        if cat_scores:
            avg_score = sum(cat_scores) / len(cat_scores) / 5 * 100  # 轉換為0-100
            category_scores[cat_key] = round(avg_score, 1)
            category_details[cat_key] = {
                "score": round(avg_score, 1),
                "matched_questions": len(cat_scores),
                "max_possible": len(cat_data) * 5
            }
    
    # 加權計算總分
    weights = {
        "family": 0.25, "money": 0.25, "career": 0.20,
        "social": 0.15, "lifestyle": 0.10, "life_goals": 0.05
    }
    
    total_score = sum(category_scores.get(k, 50) * w for k, w in weights.items())
    
    return {
        "overall_score": round(total_score, 1),
        "category_scores": category_scores,
        "category_details": category_details,
        "interpretation": _interpret_values_score(total_score)
    }


def _interpret_values_score(score: float) -> str:
    """解讀三觀分數"""
    if score >= 85:
        return "三觀高度契合，在核心價值上幾乎完全一致"
    elif score >= 70:
        return "三觀較為契合，主要價值觀一致，少數差異可調和"
    elif score >= 55:
        return "三觀基本相容，有共同基礎但需磨合"
    elif score >= 40:
        return "三觀存在差異，需要較多溝通和包容"
    else:
        return "三觀差異較大，需要慎重考慮長期關係"


# ============ 性格互補分析 ============

PERSONALITY_TRAITS = {
    "A1": {"name": "木行者", "yin": ["固執", "缺乏彈性"], "yang": ["仁慈", "正直", "有原則"]},
    "A2": {"name": "火靈者", "yin": ["急躁", "情緒化"], "yang": ["熱情", "光明", "有感染力"]},
    "A3": {"name": "土守者", "yin": ["保守", "固步自封"], "yang": ["穩重", "可靠", "有耐心"]},
    "A4": {"name": "金銳者", "yin": ["冷漠", "苛求"], "yang": ["果斷", "精確", "有原則"]},
    "A5": {"name": "水潤者", "yin": ["優柔寡斷", "情緒化"], "yang": ["智慧", "靈活", "有同理心"]},
    "B1": {"name": "木火通明", "yin": ["過度理想化", "不耐煩"], "yang": ["創意", "行動力", "領導力"]},
    "B2": {"name": "火土相生", "yin": ["控制欲強", "固執"], "yang": ["熱忱", "務實", "有擔當"]},
    "B3": {"name": "火木雙修", "yin": ["衝動", "三分鐘熱度"], "yang": ["活力", "創新", "有魅力"]},
    "B4": {"name": "木金相剋", "yin": ["內心矛盾", "自我懷疑"], "yang": ["多面性", "適應力", "有深度"]},
    "B5": {"name": "水火既濟", "yin": ["情緒波動", "難以捉摸"], "yang": ["洞察力", "創造力", "有魅力"]},
}


def analyze_personality_compatibility(profile_a: str, profile_b: str) -> Dict[str, Any]:
    """
    性格互補分析
    基於15角色動物人格系統的陰陽面對比
    """
    p_a = PERSONALITY_TRAITS.get(profile_a, PERSONALITY_TRAITS["A1"])
    p_b = PERSONALITY_TRAITS.get(profile_b, PERSONALITY_TRAITS["A1"])
    
    # 計算陰陽面互補度
    # A的陽面能否彌補B的陰面，B的陽面能否彌補A的陰面
    yin_a = set(p_a["yin"])
    yin_b = set(p_b["yin"])
    yang_a = set(p_a["yang"])
    yang_b = set(p_b["yang"])
    
    # 互補度：A的陽面能否彌補B的陰面，B的陽面能否彌補A的陰面
    # 使用五行特質映射表進行智能匹配
    complement_map = {
        # 情緒/衝動類 -> 需要穩重/冷靜/理性
        "急躁": ["穩重", "可靠", "有耐心", "冷靜", "理性", "務實", "果斷", "精確"],
        "情緒化": ["穩重", "冷靜", "理性", "務實", "可靠", "有耐心", "智慧", "有同理心"],
        "情緒波動": ["穩重", "冷靜", "理性", "務實", "可靠", "智慧", "有同理心"],
        "難以捉摸": ["穩重", "可靠", "有耐心", "冷靜", "理性", "務實", "果斷"],
        "衝動": ["穩重", "可靠", "有耐心", "冷靜", "理性", "務實", "果斷", "精確"],
        "三分鐘熱度": ["穩重", "可靠", "有耐心", "務實", "冷靜", "果斷", "有原則"],
        # 固執/保守類 -> 需要靈活/創新/開放
        "固執": ["靈活", "有同理心", "創意", "創新", "適應力", "智慧", "多面性", "有深度"],
        "缺乏彈性": ["靈活", "有同理心", "適應力", "創意", "創新", "智慧", "多面性"],
        "保守": ["創意", "創新", "活力", "行動力", "靈活", "適應力", "領導力", "有魅力"],
        "固步自封": ["創意", "創新", "行動力", "領導力", "靈活", "適應力", "活力", "有魅力"],
        "過度理想化": ["務實", "可靠", "穩重", "有耐心", "理性", "冷靜", "果斷", "精確"],
        "不耐煩": ["穩重", "有耐心", "冷靜", "可靠", "務實", "果斷", "有原則"],
        # 冷漠/疏離類 -> 需要熱情/同理/關懷
        "冷漠": ["熱情", "有感染力", "有同理心", "仁慈", "關懷", "溫暖", "熱忱", "有擔當"],
        "苛求": ["寬容", "有同理心", "靈活", "仁慈", "包容", "智慧", "有耐心"],
        # 猶豫/不自信類 -> 需要果斷/自信/行動力
        "優柔寡斷": ["果斷", "有原則", "精確", "行動力", "自信", "決斷", "領導力", "有擔當"],
        "內心矛盾": ["穩重", "可靠", "冷靜", "智慧", "果斷", "有原則", "務實", "理性"],
        "自我懷疑": ["果斷", "有原則", "自信", "行動力", "決斷", "可靠", "領導力", "有擔當"],
        # 控制/壓迫類 -> 需要獨立/智慧/靈活
        "控制欲強": ["智慧", "靈活", "寬容", "獨立", "適應力", "包容", "多面性", "有深度"],
    }
    
    def check_complement(yin_traits, yang_traits):
        """檢查yang_traits能否彌補yin_traits"""
        matched = 0
        for yin in yin_traits:
            needed = complement_map.get(yin, [])
            found = False
            for need in needed:
                for yang in yang_traits:
                    if need in yang or yang in need:
                        matched += 1
                        found = True
                        break
                if found:
                    break
        return matched
    
    a_complement_b = check_complement(p_b["yin"], p_a["yang"])
    b_complement_a = check_complement(p_a["yin"], p_b["yang"])
    
    # 計算分數：基於互補覆蓋率
    total_yin = len(p_a["yin"]) + len(p_b["yin"])
    if total_yin > 0:
        complement_score = (a_complement_b + b_complement_a) / total_yin * 100
    else:
        complement_score = 50
    
    # 相似度（陽面重合度）
    yang_a_set = set(p_a["yang"])
    yang_b_set = set(p_b["yang"])
    if yang_a_set or yang_b_set:
        intersection = len(yang_a_set & yang_b_set)
        union = len(yang_a_set | yang_b_set)
        similarity = intersection / union * 100 if union > 0 else 50
    else:
        similarity = 50
    
    # 綜合：互補60% + 相似40%
    final_score = complement_score * 0.6 + similarity * 0.4
    
    # 保底分數：最低30分，避免完全0分
    final_score = max(30, min(100, final_score))
    
    return {
        "overall_score": round(final_score, 1),
        "complement_score": round(complement_score, 1),
        "similarity_score": round(similarity, 1),
        "person_a_traits": {"yin": p_a["yin"], "yang": p_a["yang"]},
        "person_b_traits": {"yin": p_b["yin"], "yang": p_b["yang"]},
        "interpretation": _interpret_personality_score(final_score, complement_score, similarity)
    }


def _interpret_personality_score(final: float, complement: float, similarity: float) -> str:
    """解讀性格分數"""
    if final >= 80:
        return f"性格高度互補（互補度{complement:.0f}%），你們的優點恰好彌補對方的不足"
    elif final >= 65:
        return f"性格較為互補（互補度{complement:.0f}%），有自然的化學反應"
    elif final >= 50:
        return f"性格基本相容（相似度{similarity:.0f}%），需要主動創造連結"
    else:
        return f"性格差異較大（相似度{similarity:.0f}%），需要更多理解和包容"


# ============ 溝通模式分析 ============

COMMUNICATION_STYLES = {
    "direct": {"name": "直接型", "desc": "有話直說，不繞彎子", "compatible_with": ["empathetic", "analytical"]},
    "indirect": {"name": "委婉型", "desc": "含蓄表達，避免衝突", "compatible_with": ["empathetic", "diplomatic"]},
    "emotional": {"name": "情感型", "desc": "重視感受，需要被理解", "compatible_with": ["empathetic", "supportive"]},
    "analytical": {"name": "分析型", "desc": "理性思考，注重邏輯", "compatible_with": ["direct", "diplomatic"]},
    "empathetic": {"name": "共情型", "desc": "善於傾聽，理解對方", "compatible_with": ["emotional", "indirect", "direct"]},
    "diplomatic": {"name": "外交型", "desc": "圓融處理，平衡各方", "compatible_with": ["indirect", "analytical"]},
    "supportive": {"name": "支持型", "desc": "給予鼓勵，陪伴成長", "compatible_with": ["emotional", "direct"]},
}


def analyze_communication_compatibility(style_a: str, style_b: str) -> Dict[str, Any]:
    """
    溝通模式匹配分析
    """
    s_a = COMMUNICATION_STYLES.get(style_a, COMMUNICATION_STYLES["direct"])
    s_b = COMMUNICATION_STYLES.get(style_b, COMMUNICATION_STYLES["direct"])
    
    # 直接匹配
    if style_b in s_a.get("compatible_with", []):
        score = 90
        relation = "天然契合"
    elif style_a == style_b:
        score = 75
        relation = "同頻共振"
    elif style_b in ["empathetic", "diplomatic"] or style_a in ["empathetic", "diplomatic"]:
        score = 70
        relation = "可以調和"
    else:
        score = 50
        relation = "需要磨合"
    
    # 根據五行微調
    if style_a in ["emotional", "supportive"] and style_b in ["analytical", "direct"]:
        score -= 10  # 情感型 vs 分析型需要更多磨合
    
    return {
        "overall_score": round(score, 1),
        "style_a": {"type": style_a, "name": s_a["name"], "desc": s_a["desc"]},
        "style_b": {"type": style_b, "name": s_b["name"], "desc": s_b["desc"]},
        "relation": relation,
        "advice": _generate_communication_advice(style_a, style_b, score)
    }


def _generate_communication_advice(a: str, b: str, score: float) -> str:
    """生成溝通建議"""
    if score >= 80:
        return "你們的溝通風格天然契合，能夠高效理解彼此"
    elif score >= 65:
        return "溝通基本順暢，注意在情緒激動時給對方空間"
    elif score >= 50:
        return "溝通風格有差異，建議建立固定的溝通儀式（如每週深度對話）"
    else:
        return "溝通風格差異較大，建議學習對方的表達方式，多用「我覺得」而非「你應該」"


# ============ 目標一致性分析 ============

LIFE_GOALS_CATEGORIES = [
    "事業成就", "家庭美滿", "財務自由", "環遊世界",
    "自我實現", "社會貢獻", "健康生活", "學習成長"
]


def analyze_goals_alignment(goals_a: List[str], goals_b: List[str]) -> Dict[str, Any]:
    """
    人生目標一致性分析
    """
    set_a = set(goals_a)
    set_b = set(goals_b)
    
    # 交集（共同目標）
    common = set_a & set_b
    # 差集（獨特目標）
    unique_a = set_a - set_b
    unique_b = set_b - set_a
    
    # 計算一致性
    if len(set_a | set_b) > 0:
        alignment = len(common) / len(set_a | set_b) * 100
    else:
        alignment = 50
    
    # 加權：共同目標數量也重要
    common_bonus = min(len(common) * 5, 20)
    final_score = min(alignment + common_bonus, 100)
    
    return {
        "overall_score": round(final_score, 1),
        "common_goals": list(common),
        "unique_goals_a": list(unique_a),
        "unique_goals_b": list(unique_b),
        "alignment_percentage": round(alignment, 1),
        "interpretation": _interpret_goals_score(final_score, len(common))
    }


def _interpret_goals_score(score: float, common_count: int) -> str:
    """解讀目標分數"""
    if score >= 80:
        return f"人生目標高度一致，有{common_count}個共同目標，未來方向清晰"
    elif score >= 65:
        return f"人生目標較為一致，有{common_count}個共同目標，可以共同規劃"
    elif score >= 50:
        return f"人生目標基本相容，有{common_count}個共同目標，需要協商調整"
    else:
        return f"人生目標差異較大，僅{common_count}個共同目標，需要深入溝通"


# ============ 六維度整合分析 ============

def analyze_relationship_full_v3(
    person_a_data: Dict[str, Any],
    person_b_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    六維度完整關係分析（FXTI v3.0 核心）
    
    參數：
        person_a_data: {
            "birth": {"year": 1990, "month": 5, "day": 15, "gender": "male"},
            "wuxing": {"金": 10, "木": 30, "水": 20, "火": 25, "土": 15},
            "profile_id": "A1",
            "values_answers": {"f1": 2, "f2": 3, ...},
            "communication_style": "direct",
            "life_goals": ["事業成就", "家庭美滿"],
        }
    """
    # 1. 五行命理維度 (25%)
    wuxing_result = _analyze_wuxing_dimension(person_a_data, person_b_data)
    
    # 2. 三觀契合維度 (20%)
    values_result = analyze_values_compatibility(
        person_a_data.get("values_answers", {}),
        person_b_data.get("values_answers", {})
    )
    
    # 3. 性格互補維度 (20%)
    personality_result = analyze_personality_compatibility(
        person_a_data.get("profile_id", "A1"),
        person_b_data.get("profile_id", "A1")
    )
    
    # 4. 歲月磨合維度 (15%)
    timing_result = _analyze_timing_dimension(person_a_data, person_b_data)
    
    # 5. 溝通模式維度 (10%)
    communication_result = analyze_communication_compatibility(
        person_a_data.get("communication_style", "direct"),
        person_b_data.get("communication_style", "direct")
    )
    
    # 6. 目標一致性維度 (10%)
    goals_result = analyze_goals_alignment(
        person_a_data.get("life_goals", []),
        person_b_data.get("life_goals", [])
    )
    
    # 加權總分
    weights = {
        "wuxing": 0.25, "values": 0.20, "personality": 0.20,
        "timing": 0.15, "communication": 0.10, "goals": 0.10
    }
    
    final_score = (
        wuxing_result["score"] * weights["wuxing"] +
        values_result["overall_score"] * weights["values"] +
        personality_result["overall_score"] * weights["personality"] +
        timing_result["score"] * weights["timing"] +
        communication_result["overall_score"] * weights["communication"] +
        goals_result["overall_score"] * weights["goals"]
    )
    
    # 雷達圖數據
    radar_data = {
        "五行命理": wuxing_result["score"],
        "三觀契合": values_result["overall_score"],
        "性格互補": personality_result["overall_score"],
        "歲月磨合": timing_result["score"],
        "溝通模式": communication_result["overall_score"],
        "目標一致": goals_result["overall_score"],
    }
    
    return {
        "final_score": round(final_score, 1),
        "rating": _get_six_dimension_rating(final_score),
        "dimensions": {
            "五行命理": wuxing_result,
            "三觀契合": values_result,
            "性格互補": personality_result,
            "歲月磨合": timing_result,
            "溝通模式": communication_result,
            "目標一致": goals_result,
        },
        "radar_chart": radar_data,
        "summary": _generate_full_summary(final_score, radar_data),
        "recommendations": _generate_recommendations(radar_data)
    }


def _analyze_wuxing_dimension(a: Dict, b: Dict) -> Dict[str, Any]:
    """五行命理維度分析"""
    wuxing_a = a.get("wuxing", {})
    wuxing_b = b.get("wuxing", {})
    
    if not wuxing_a or not wuxing_b:
        return {"score": 50, "detail": "五行數據缺失"}
    
    top_a = max(wuxing_a, key=wuxing_a.get)
    top_b = max(wuxing_b, key=wuxing_b.get)
    
    relation_type, relation_name, relation_desc = determine_relation_type(top_a, top_b)
    similarity = cosine_similarity(wuxing_a, wuxing_b)
    complement = complement_score(wuxing_a, wuxing_b)
    
    harmony_base = 60
    if relation_type in ['supportive', 'supported']:
        harmony_base += 20
    elif relation_type in ['controlling', 'controlled']:
        harmony_base -= 15
    
    similarity_bonus = 20 - abs(similarity - 50) / 50 * 20
    complement_bonus = complement / 100 * 15
    
    score = min(100, max(0, harmony_base + similarity_bonus + complement_bonus))
    
    return {
        "score": round(score, 1),
        "relation_type": relation_type,
        "relation_name": relation_name,
        "top_element_a": top_a,
        "top_element_b": top_b,
        "similarity": round(similarity, 1),
        "complement": round(complement, 1),
    }


def _analyze_timing_dimension(a: Dict, b: Dict) -> Dict[str, Any]:
    """歲月磨合維度分析"""
    birth_a = a.get("birth", {})
    birth_b = b.get("birth", {})
    
    if not birth_a or not birth_b:
        return {"score": 50, "detail": "出生資料缺失"}
    
    try:
        result = analyze_timing_compatibility(
            birth_a, birth_b, analysis_years=10, current_year=datetime.now().year
        )
        return {
            "score": result.get("overall_timing_score", 50),
            "timeline": result.get("timeline", []),
            "best_years": result.get("best_years", []),
            "challenging_years": result.get("challenging_years", []),
            "marriage_window": result.get("marriage_window", []),
            "summary": result.get("summary", "")
        }
    except Exception as e:
        return {"score": 50, "detail": f"歲月磨合計算錯誤: {str(e)}"}


def _get_six_dimension_rating(score: float) -> str:
    """六維度評級"""
    if score >= 90:
        return "天作之合"
    elif score >= 80:
        return "非常契合"
    elif score >= 70:
        return "相得益彰"
    elif score >= 60:
        return "基本相容"
    elif score >= 50:
        return "需要磨合"
    elif score >= 40:
        return "挑戰較大"
    else:
        return "緣分淺薄"


def _generate_full_summary(score: float, radar: Dict[str, float]) -> str:
    """生成完整摘要"""
    # 找出最強和最弱維度
    sorted_dims = sorted(radar.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_dims[0]
    weakest = sorted_dims[-1]
    
    return (
        f"你們的六維度匹配總分為 {score:.0f} 分，屬於「{_get_six_dimension_rating(score)}」級別。"
        f"最強維度是「{strongest[0]}」（{strongest[1]:.0f}分），"
        f"最需要關注的是「{weakest[0]}」（{weakest[1]:.0f}分）。"
        f"建議在{weakest[0]}方面多加溝通，發揮{strongest[0]}的優勢。"
    )


def _generate_recommendations(radar: Dict[str, float]) -> List[Dict[str, str]]:
    """生成針對性建議"""
    recommendations = []
    
    for dim, score in radar.items():
        if score < 50:
            recommendations.append({
                "dimension": dim,
                "priority": "高",
                "advice": f"{dim}維度較弱（{score:.0f}分），建議優先改善"
            })
        elif score < 65:
            recommendations.append({
                "dimension": dim,
                "priority": "中",
                "advice": f"{dim}維度有提升空間（{score:.0f}分）"
            })
    
    # 按優先級排序
    recommendations.sort(key=lambda x: 0 if x["priority"] == "高" else 1)
    
    return recommendations


# ============ 快捷API ============

def quick_six_dimension_match(
    birth_a: Dict, birth_b: Dict,
    wuxing_a: Dict, wuxing_b: Dict,
    profile_a: str = "A1", profile_b: str = "A1",
    values_a: Dict = None, values_b: Dict = None,
    comm_style_a: str = "direct", comm_style_b: str = "direct",
    goals_a: List = None, goals_b: List = None
) -> Dict[str, Any]:
    """
    快速六維度匹配（簡化版API）
    """
    person_a = {
        "birth": birth_a,
        "wuxing": wuxing_a,
        "profile_id": profile_a,
        "values_answers": values_a or {},
        "communication_style": comm_style_a,
        "life_goals": goals_a or []
    }
    person_b = {
        "birth": birth_b,
        "wuxing": wuxing_b,
        "profile_id": profile_b,
        "values_answers": values_b or {},
        "communication_style": comm_style_b,
        "life_goals": goals_b or []
    }
    
    return analyze_relationship_full_v3(person_a, person_b)
