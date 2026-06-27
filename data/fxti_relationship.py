#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FXTI 雙人關係分析模組
根據 relationship_pseudocode.md 實現
"""

import math

# 五行相生關係
SHENG = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}
# 五行相剋關係
KE = {'金': '木', '木': '土', '土': '水', '水': '火', '火': '金'}

# 元素對應方位
ELEMENT_DIRECTION = {
    '金': '西方或西北',
    '木': '東方或東南',
    '水': '北方',
    '火': '南方',
    '土': '中央或西南'
}

# 元素補充建議
ELEMENT_SUGGESTION = {
    '金': '金屬飾品、白色或金色裝飾',
    '木': '綠植、木質家具',
    '水': '水景、鏡面、藍色裝飾',
    '火': '紅色點綴、燭光、暖光燈',
    '土': '陶藝、大地色系、石材'
}

# 元素對應顏色
ELEMENT_COLORS = {
    '金': '白色、金色、銀色',
    '木': '綠色、青色',
    '水': '藍色、黑色',
    '火': '紅色、橙色、紫色',
    '土': '黃色、棕色、米色'
}


def cosine_similarity(wuxing_a, wuxing_b):
    """計算五行向量夾角餘弦相似度"""
    elements = ['金', '木', '水', '火', '土']
    vec_a = [wuxing_a[e] for e in elements]
    vec_b = [wuxing_b[e] for e in elements]

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b) * 100


def complement_score(wuxing_a, wuxing_b):
    """計算互補度"""
    elements = ['金', '木', '水', '火', '土']

    sorted_a = sorted(elements, key=lambda e: wuxing_a[e], reverse=True)
    sorted_b = sorted(elements, key=lambda e: wuxing_b[e], reverse=True)

    strong_a = set(sorted_a[:2])
    weak_a = set(sorted_a[-2:])
    strong_b = set(sorted_b[:2])
    weak_b = set(sorted_b[-2:])

    complement = len(strong_b & weak_a) + len(strong_a & weak_b)
    return complement / 4 * 100


def determine_relation_type(top_a, top_b):
    """判定兩人五行關係類型"""
    if SHENG[top_a] == top_b:
        return 'supportive', '相生（A生助B）', f'{top_a}生{top_b}，A對B有滋養作用'
    elif SHENG[top_b] == top_a:
        return 'supported', '相生（B生助A）', f'{top_b}生{top_a}，B對A有滋養作用'
    elif KE[top_a] == top_b:
        return 'controlling', '相剋（A制約B）', f'{top_a}剋{top_b}，A對B有制約作用'
    elif KE[top_b] == top_a:
        return 'controlled', '相剋（B制約A）', f'{top_b}剋{top_a}，B對A有制約作用'
    else:
        return 'neutral', '平衡', '你們的五行關係較為平衡，無明顯生剋'


def generate_relationship_text(relation_type, harmony_score):
    """生成關係文案"""
    texts = {
        'supportive': {
            'high': '你們的關係如源流相生，一方的能量自然滋養另一方。這是理想的伴侶或合作關係。',
            'medium': '你們之間有自然的支持力，但需注意不要讓付出變成單方面的消耗。',
            'low': '理論上你們應該互相支持，但實際互動中可能因其他因素而受阻。'
        },
        'supported': {
            'high': '你們的關係如源流相生，一方的能量自然滋養另一方。這是理想的伴侶或合作關係。',
            'medium': '你們之間有自然的支持力，但需注意不要讓付出變成單方面的消耗。',
            'low': '理論上你們應該互相支持，但實際互動中可能因其他因素而受阻。'
        },
        'controlling': {
            'high': '你們的關係充滿張力，這種制約能讓彼此成長，但也需要更多磨合。',
            'medium': '你們的五行存在天然衝突，這既是挑戰也是彼此進化的動力。',
            'low': '你們的關係容易陷入對立，需要學習欣賞對方的不同，而非試圖改變。'
        },
        'controlled': {
            'high': '你們的關係充滿張力，這種制約能讓彼此成長，但也需要更多磨合。',
            'medium': '你們的五行存在天然衝突，這既是挑戰也是彼此進化的動力。',
            'low': '你們的關係容易陷入對立，需要學習欣賞對方的不同，而非試圖改變。'
        },
        'neutral': {
            'high': '你們的關係平衡而穩定，沒有強烈的生剋，這意味著你們需要主動創造連結。',
            'medium': '你們的五行分布各自獨立，關係的質量更多取決於後天的努力與溝通。',
            'low': '你們的互動模式較為平淡，可能需要更多共同興趣來加深連結。'
        }
    }

    level = 'high' if harmony_score > 70 else ('medium' if harmony_score > 40 else 'low')
    return texts.get(relation_type, texts['neutral'])[level]


def generate_combined_fengshui(wuxing_a, wuxing_b):
    """生成共同風水建議"""
    combined = {}
    for e in ['金', '木', '水', '火', '土']:
        combined[e] = (wuxing_a[e] + wuxing_b[e]) / 2

    top_combined = max(combined, key=combined.get)
    bottom_combined = min(combined, key=combined.get)

    advice = f'你們的共同主導能量是「{top_combined}」，建議選擇{ELEMENT_DIRECTION[top_combined]}方位的居住環境。'
    advice += f' 你們共同缺乏「{bottom_combined}」元素，可適當在空間中加入{ELEMENT_SUGGESTION[bottom_combined]}。'

    return advice


def generate_space_layout(relation_type):
    """生成空間布局建議"""
    layouts = {
        'supportive': '開放式公共空間為主，方便能量流動與互動',
        'supported': '開放式公共空間為主，方便能量流動與互動',
        'controlling': '明確分區，各自保留獨立空間，公共區域設置緩衝帶',
        'controlled': '明確分區，各自保留獨立空間，公共區域設置緩衝帶',
        'neutral': '平衡布局，既有共同區域也有各自獨立空間'
    }
    return layouts.get(relation_type, '靈活布局，可根據實際居住體驗調整')


def generate_color_scheme(wuxing_a, wuxing_b):
    """生成色彩搭配建議"""
    combined = {}
    for e in ['金', '木', '水', '火', '土']:
        combined[e] = (wuxing_a[e] + wuxing_b[e]) / 2

    sorted_elements = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    primary = ELEMENT_COLORS[sorted_elements[0][0]]
    secondary = ELEMENT_COLORS[sorted_elements[1][0]]

    return f'主色調：{primary}，輔助色：{secondary}'


def analyze_relationship(result_a, result_b):
    """
    分析兩個FXTI結果之間的關係
    Args:
        result_a: dict, 包含 profile 和 final_wuxing
        result_b: dict, 包含 profile 和 final_wuxing
    Returns:
        dict: 關係分析報告
    """
    wuxing_a = result_a['final_wuxing']
    wuxing_b = result_b['final_wuxing']
    top_a = max(wuxing_a, key=wuxing_a.get)
    top_b = max(wuxing_b, key=wuxing_b.get)

    # 1. 五行關係判定
    relation_type, relation_name, relation_desc = determine_relation_type(top_a, top_b)

    # 2. 相似度
    similarity = cosine_similarity(wuxing_a, wuxing_b)

    # 3. 互補度
    complement = complement_score(wuxing_a, wuxing_b)

    # 4. 和諧度
    harmony_base = 60
    if relation_type in ['supportive', 'supported']:
        harmony_base += 20
    elif relation_type in ['controlling', 'controlled']:
        harmony_base -= 15

    similarity_bonus = 20 - abs(similarity - 50) / 50 * 20
    complement_bonus = complement / 100 * 15

    harmony_score = min(100, max(0, harmony_base + similarity_bonus + complement_bonus))

    # 5. 關係文案
    relationship_text = generate_relationship_text(relation_type, harmony_score)

    # 6. 共同風水建議
    combined_fengshui = generate_combined_fengshui(wuxing_a, wuxing_b)

    # 7. 合併五行
    combined = {}
    for e in ['金', '木', '水', '火', '土']:
        combined[e] = round((wuxing_a[e] + wuxing_b[e]) / 2, 2)

    top_combined = max(combined, key=combined.get)

    return {
        'person_a': {
            'profile_id': result_a['profile']['id'],
            'profile_name': result_a['profile']['name'],
            'top_element': top_a,
            'wuxing': wuxing_a
        },
        'person_b': {
            'profile_id': result_b['profile']['id'],
            'profile_name': result_b['profile']['name'],
            'top_element': top_b,
            'wuxing': wuxing_b
        },
        'relationship': {
            'type': relation_type,
            'name': relation_name,
            'description': relation_desc,
            'harmony_score': round(harmony_score, 1),
            'similarity': round(similarity, 1),
            'complement': round(complement, 1),
            'relationship_text': relationship_text,
            'combined_fengshui_advice': combined_fengshui
        },
        'living_recommendations': {
            'ideal_direction': ELEMENT_DIRECTION[top_combined],
            'avoid_direction': ELEMENT_DIRECTION.get(KE.get(top_combined, ''), '根據個人喜好'),
            'space_layout': generate_space_layout(relation_type),
            'color_scheme': generate_color_scheme(wuxing_a, wuxing_b)
        }
    }
