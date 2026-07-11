# -*- coding: utf-8 -*-
"""
納甲樓層模塊 (Najia Floor / Stems-Branches Floor Selection)

納甲風水根據天干地支與樓層的五行關係，判斷樓層吉凶：
- 河圖五行：1、6水；2、7火；3、8木；4、9金；5、10土
- 樓層五行 = 樓層數 mod 10，再映射到河圖五行
- 命卦五行與樓層五行相生為吉，相剋為凶

來源：河圖洛書 / 納甲法
"""

from typing import Dict, List
from data.ming_gua import get_ming_gua_by_year, GUA_WUXING

# 河圖五行
HE_TU_WUXING = {
    1: "水", 2: "火", 3: "木", 4: "金", 5: "土",
    6: "水", 7: "火", 8: "木", 9: "金", 0: "土"
}

# 五行相生：木→火→土→金→水→木
WUXING_SHENG = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
}

# 五行相剋：木→土→水→火→金→木
WUXING_KE = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木"
}

# 五行比和（相同）

FLOOR_WUXING_DESCRIPTION = {
    "水": {
        "description": "水層主智慧、流動、財運",
        "suitable": "商人、學者、創意工作者",
        "avoid": "心臟病患者、喜靜者"
    },
    "火": {
        "description": "火層主熱情、活力、名聲",
        "suitable": "演藝人員、領導者、創業者",
        "avoid": "脾氣急躁者、高血壓患者"
    },
    "木": {
        "description": "木層主生長、發展、仁慈",
        "suitable": "教師、醫生、環保工作者",
        "avoid": "肝病患者、情緒不穩者"
    },
    "金": {
        "description": "金層主果斷、收斂、財富",
        "suitable": "金融工作者、律師、管理者",
        "avoid": "肺病患者、優柔寡斷者"
    },
    "土": {
        "description": "土層主穩重、包容、誠信",
        "suitable": "公務員、建築師、農業工作者",
        "avoid": "脾胃病患者、變動頻繁者"
    }
}


def get_floor_wuxing(floor_number: int) -> str:
    """根據樓層數計算五行"""
    remainder = floor_number % 10
    return HE_TU_WUXING[remainder]


def analyze_floor_relation(person_wuxing: str, floor_wuxing: str) -> Dict:
    """分析個人五行與樓層五行的關係"""
    if person_wuxing == floor_wuxing:
        return {
            "relation": "比和",
            "type": "吉",
            "score": 80,
            "description": f"{person_wuxing}命配{floor_wuxing}層，五行比和，穩定和諧"
        }
    elif WUXING_SHENG.get(person_wuxing) == floor_wuxing:
        return {
            "relation": "相生",
            "type": "大吉",
            "score": 95,
            "description": f"{person_wuxing}生{floor_wuxing}，樓層助旺命主，事業財運亨通"
        }
    elif WUXING_KE.get(person_wuxing) == floor_wuxing:
        return {
            "relation": "相剋",
            "type": "凶",
            "score": 30,
            "description": f"{person_wuxing}剋{floor_wuxing}，樓層受命主壓制，需化解"
        }
    elif WUXING_SHENG.get(floor_wuxing) == person_wuxing:
        return {
            "relation": "被生",
            "type": "中吉",
            "score": 70,
            "description": f"{floor_wuxing}生{person_wuxing}，樓層生旺命主，貴人相助"
        }
    elif WUXING_KE.get(floor_wuxing) == person_wuxing:
        return {
            "relation": "被剋",
            "type": "凶",
            "score": 20,
            "description": f"{floor_wuxing}剋{person_wuxing}，樓層壓制命主，健康運勢受阻"
        }
    else:
        return {
            "relation": "中性",
            "type": "平",
            "score": 50,
            "description": "五行關係中性，無明顯吉凶"
        }


def get_najia_analysis(birth_year: int, floor_number: int, gender: str = "male") -> Dict:
    """
    納甲樓層分析主入口
    """
    # 統一命卦計算（與 bagua_matching.py / bazhai_younian.py 一致）
    ming = get_ming_gua_by_year(birth_year, gender)
    person_wuxing = ming["wuxing"]

    # 計算樓層五行
    floor_wuxing = get_floor_wuxing(floor_number)
    floor_info = FLOOR_WUXING_DESCRIPTION[floor_wuxing]

    # 分析關係
    relation = analyze_floor_relation(person_wuxing, floor_wuxing)

    # 計算所有樓層的匹配度（1-10層）
    all_floors = []
    for f in range(1, 11):
        fw = get_floor_wuxing(f)
        rel = analyze_floor_relation(person_wuxing, fw)
        all_floors.append({
            "floor": f,
            "wuxing": fw,
            "relation": rel["relation"],
            "type": rel["type"],
            "score": rel["score"]
        })

    all_floors.sort(key=lambda x: x["score"], reverse=True)

    # 推薦樓層
    best_floors = [f for f in all_floors if f["type"] in ["大吉", "吉"]]
    avoid_floors = [f for f in all_floors if f["type"] == "凶"]

    return {
        "birth_year": birth_year,
        "gender": gender,
        "ming_gua": ming["gua_name"],
        "person_wuxing": person_wuxing,
        "floor": {
            "number": floor_number,
            "wuxing": floor_wuxing,
            "description": floor_info["description"],
            "suitable": floor_info["suitable"],
            "avoid": floor_info["avoid"]
        },
        "relation": relation,
        "all_floors_analysis": all_floors,
        "recommendations": {
            "best_floors": [f["floor"] for f in best_floors[:3]],
            "avoid_floors": [f["floor"] for f in avoid_floors[:3]]
        },
        "confidence": 0.65  # 納甲樓層為輔助參考，置信度標記為0.65
    }


if __name__ == "__main__":
    # 測試
    result = get_najia_analysis(1991, 8)
    print(result)
