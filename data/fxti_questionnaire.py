#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FXTI 問卷處理模組
10題情境選擇題，每題5選項對應金木水火土
"""

# 10題問卷數據
QUESTIONNAIRE = [
    {
        "id": 1,
        "question": "當你面對一個重要決定時，你通常會怎麼做？",
        "options": [
            {"text": "仔細分析利弊，列出優缺點再做決定", "element": "金"},
            {"text": "聽取多方意見，尋求創新解決方案", "element": "木"},
            {"text": "跟隨直覺，靜待時機成熟", "element": "水"},
            {"text": "果斷行動，先做再說", "element": "火"},
            {"text": "徵求信任的人的意見，穩妥為上", "element": "土"}
        ]
    },
    {
        "id": 2,
        "question": "在團隊合作中，你通常扮演什麼角色？",
        "options": [
            {"text": "制定規則和標準，確保效率", "element": "金"},
            {"text": "提出新點子，推動改變", "element": "木"},
            {"text": "協調各方，化解衝突", "element": "水"},
            {"text": "帶領大家，鼓舞士氣", "element": "火"},
            {"text": "默默支持，穩定後方", "element": "土"}
        ]
    },
    {
        "id": 3,
        "question": "描述一下你理想的生活環境？",
        "options": [
            {"text": "簡潔有序，功能分區明確", "element": "金"},
            {"text": "充滿綠植，自然光充足", "element": "木"},
            {"text": "臨近水源，寧靜悠遠", "element": "水"},
            {"text": "明亮開闊，色彩鮮豔", "element": "火"},
            {"text": "溫馨踏實，有歸屬感", "element": "土"}
        ]
    },
    {
        "id": 4,
        "question": "當遇到挫折時，你的反應是？",
        "options": [
            {"text": "冷靜分析原因，調整策略", "element": "金"},
            {"text": "從挫折中學習，重新出發", "element": "木"},
            {"text": "順勢而為，等待時機轉變", "element": "水"},
            {"text": "愈挫愈勇，立刻反擊", "element": "火"},
            {"text": "接受現實，慢慢恢復", "element": "土"}
        ]
    },
    {
        "id": 5,
        "question": "你與朋友相處的方式是？",
        "options": [
            {"text": "重質不重量，深交幾個知己", "element": "金"},
            {"text": "喜歡結交不同領域的朋友", "element": "木"},
            {"text": "善於傾聽，給予情感支持", "element": "水"},
            {"text": "熱情主動，常常是聚會靈魂", "element": "火"},
            {"text": "忠誠可靠，長期維繫關係", "element": "土"}
        ]
    },
    {
        "id": 6,
        "question": "你選擇工作/居住地的首要考量是？",
        "options": [
            {"text": "發展機會和競爭力", "element": "金"},
            {"text": "創意空間和成長潛力", "element": "木"},
            {"text": "生活品質和環境氛圍", "element": "水"},
            {"text": "社交機會和娛樂活動", "element": "火"},
            {"text": "安全感和生活穩定性", "element": "土"}
        ]
    },
    {
        "id": 7,
        "question": "描述你的日常時間管理風格？",
        "options": [
            {"text": "精確規劃，按表操課", "element": "金"},
            {"text": "彈性安排，隨機應變", "element": "木"},
            {"text": "順其自然，不強求", "element": "水"},
            {"text": "多線並進，充滿活力", "element": "火"},
            {"text": "規律作息，穩定節奏", "element": "土"}
        ]
    },
    {
        "id": 8,
        "question": "你對金錢的態度是？",
        "options": [
            {"text": "理性投資，追求回報", "element": "金"},
            {"text": "願意為學習和體驗花錢", "element": "木"},
            {"text": "不特別在意，夠用就好", "element": "水"},
            {"text": "喜歡消費，享受當下", "element": "火"},
            {"text": "穩健儲蓄，未雨綢繆", "element": "土"}
        ]
    },
    {
        "id": 9,
        "question": "當別人與你意見不同時，你會？",
        "options": [
            {"text": "用邏輯說服對方", "element": "金"},
            {"text": "尊重差異，尋求共識", "element": "木"},
            {"text": "避免爭執，順應對方", "element": "水"},
            {"text": "熱烈辯論，堅持己見", "element": "火"},
            {"text": "包容接納，和而不同", "element": "土"}
        ]
    },
    {
        "id": 10,
        "question": "你認為自己最大的優勢是？",
        "options": [
            {"text": "分析能力和執行力", "element": "金"},
            {"text": "創造力和適應力", "element": "木"},
            {"text": "洞察力和同理心", "element": "水"},
            {"text": "領導力和感染力", "element": "火"},
            {"text": "耐心和可靠性", "element": "土"}
        ]
    }
]


def get_questionnaire():
    """獲取完整問卷（返回前端可用格式，不包含元素標記）"""
    return [
        {
            "id": q["id"],
            "question": q["question"],
            "options": [opt["text"] for opt in q["options"]]
        }
        for q in QUESTIONNAIRE
    ]


def calculate_acquired_wuxing(answers):
    """
    計算後天問卷五行得分
    Args:
        answers: list of int, 每題選擇的選項索引 (0-4)
               0=金, 1=木, 2=水, 3=火, 4=土
    Returns:
        dict: 五行百分比，含極端檢測警告
    """
    if len(answers) != 10:
        raise ValueError("必須回答10題")

    scores = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    element_map = ['金', '木', '水', '火', '土']

    for i, answer_idx in enumerate(answers):
        if not 0 <= answer_idx <= 4:
            raise ValueError(f"第{i+1}題答案必須在0-4之間")
        element = element_map[answer_idx]
        scores[element] += 1

    # === 防極端機制（2026-06-18 新增） ===
    max_score = max(scores.values())
    max_element = max(scores, key=scores.get)
    warning = None
    penalty_applied = False
    
    # 如果全部10題選同一元素，觸發降權
    if max_score == 10:
        warning = f"檢測到全部選擇『{max_element}』型答案，可能過於極端。已自動降權20%並分散其他元素。"
        # 降權：將最高元素扣2分，分給其他元素各0.5分
        scores[max_element] -= 2
        for e in scores:
            if e != max_element:
                scores[e] += 0.5
    # 如果8-9題選同一元素，觸發警告
    elif max_score >= 8:
        warning = f"檢測到『{max_element}』型答案佔比過高（{max_score}/10），建議重新檢視選擇。"
    # 如果5-7題選同一元素，輕微警告
    elif max_score >= 5:
        warning = f"『{max_element}』型傾向明顯（{max_score}/10），結果已記錄。"

    total = sum(scores.values())
    percentages = {
        element: round(score / total * 100, 2)
        for element, score in scores.items()
    }

    return {
        'scores': scores,
        'wuxing_percentage': percentages,
        'warning': warning,
        'penalty_applied': max_score == 10
    }
