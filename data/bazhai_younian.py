# -*- coding: utf-8 -*-
"""
八宅遊年模塊 (Bazhai Younian / Eight Mansions)

八宅風水根據命卦與宅卦的匹配，計算八個方位的吉凶：
- 四吉方：生氣、延年、天醫、伏位
- 四凶方：五鬼、六煞、禍害、絕命

來源：八宅明鏡 / 陽宅愛眾篇
"""

import math
from typing import Dict, List, Tuple, Optional

# ===================== 命卦計算 =====================

MALE_REMAINING_GUA = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "坤",
                       6: "乾", 7: "兌", 8: "艮", 9: "離", 0: "離"}
FEMALE_REMAINING_GUA = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "艮",
                         6: "乾", 7: "兌", 8: "艮", 9: "離", 0: "離"}

GUA_WUXING = {
    "坎": "水", "坤": "土", "震": "木", "巽": "木",
    "乾": "金", "兌": "金", "艮": "土", "離": "火"
}

GUA_NUMBER = {
    "坎": 1, "坤": 2, "震": 3, "巽": 4,
    "乾": 6, "兌": 7, "艮": 8, "離": 9
}

# 東四命 vs 西四命
EAST_GUA = {"坎", "震", "巽", "離"}
WEST_GUA = {"坤", "乾", "兌", "艮"}

# 八宅游年星序（從伏位開始順排）
YOUNIAN_SEQUENCE = ["伏位", "生氣", "延年", "天醫", "五鬼", "六煞", "禍害", "絕命"]

# 各宅卦的游年星方位（按順時針從伏位開始）
# 方位：北(0)、東北(1)、東(2)、東南(3)、南(4)、西南(5)、西(6)、西北(7)
YOUNIAN_STAR = {
    "坎":  ["伏位", "五鬼", "生氣", "天醫", "延年", "絕命", "禍害", "六煞"],  # 北
    "坤":  ["伏位", "禍害", "延年", "六煞", "生氣", "五鬼", "天醫", "絕命"],  # 西南
    "震":  ["伏位", "六煞", "天醫", "延年", "生氣", "禍害", "五鬼", "絕命"],  # 東
    "巽":  ["伏位", "絕命", "五鬼", "六煞", "禍害", "生氣", "延年", "天醫"],  # 東南
    "乾":  ["伏位", "生氣", "禍害", "延年", "絕命", "天醫", "六煞", "五鬼"],  # 西北
    "兌":  ["伏位", "天醫", "六煞", "絕命", "禍害", "延年", "生氣", "五鬼"],  # 西
    "艮":  ["伏位", "延年", "絕命", "五鬼", "六煞", "生氣", "禍害", "天醫"],  # 東北
    "離":  ["伏位", "禍害", "六煞", "五鬼", "絕命", "天醫", "生氣", "延年"],  # 南
}

# 方位名稱
DIRECTION_NAMES = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"]
DIRECTION_NAME_TO_DEGREE = {
    "北": 0, "東北": 45, "東": 90, "東南": 135,
    "南": 180, "西南": 225, "西": 270, "西北": 315
}

STAR_DESCRIPTION = {
    "生氣": {"type": "吉", "wuxing": "木", "description": "生氣勃勃，主事業發展、貴人相助", "score": 95},
    "延年": {"type": "吉", "wuxing": "金", "description": "延年益壽，主健康長壽、感情穩定", "score": 90},
    "天醫": {"type": "吉", "wuxing": "土", "description": "天醫祛病，主健康康復、財運穩定", "score": 85},
    "伏位": {"type": "吉", "wuxing": "木", "description": "伏位安穩，主平穩守成、家庭和睦", "score": 70},
    "五鬼": {"type": "凶", "wuxing": "火", "description": "五鬼鬧宅，主口舌是非、意外災禍", "score": 20},
    "六煞": {"type": "凶", "wuxing": "水", "description": "六煞桃花，主感情糾紛、桃花劫", "score": 30},
    "禍害": {"type": "凶", "wuxing": "土", "description": "禍害連連，主疾病纏身、財運不濟", "score": 25},
    "絕命": {"type": "凶", "wuxing": "金", "description": "絕命凶煞，主事業破敗、健康危機", "score": 10},
}

# 坐向轉宅卦（八宅以坐山為宅卦）
FACING_TO_GUA = {
    "子": "坎", "午": "離", "卯": "震", "酉": "兌",
    "乾": "乾", "巽": "巽", "艮": "艮", "坤": "坤",
    "壬": "坎", "癸": "坎", "丙": "離", "丁": "離",
    "甲": "震", "乙": "震", "庚": "兌", "辛": "兌",
    "戌": "乾", "亥": "乾", "辰": "巽", "巳": "巽",
    "丑": "艮", "寅": "艮", "未": "坤", "申": "坤",
}


def calculate_ming_gua(birth_year: int, gender: str = "male") -> str:
    """
    計算命卦（八宅命卦）
    公式：出生年份各位數字相加，取個位，再取餘數
    """
    year_str = str(birth_year)
    total = sum(int(d) for d in year_str)
    while total >= 10:
        total = sum(int(d) for d in str(total))

    if gender == "male":
        remaining = (11 - total) % 9
        if remaining == 0:
            remaining = 9
    else:
        remaining = (4 + total) % 9
        if remaining == 0:
            remaining = 9

    # 映射到八卦
    gua_map = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "坤",
               6: "乾", 7: "兌", 8: "艮", 9: "離", 0: "離"}
    return gua_map.get(remaining, "坎")


def get_bazhai_analysis(birth_year: int, facing: str, gender: str = "male") -> Dict:
    """
    八宅遊年分析主入口
    """
    # 計算命卦
    ming_gua = calculate_ming_gua(birth_year, gender)
    # 計算宅卦（根據坐向）
    zhai_gua = FACING_TO_GUA.get(facing, "坎")

    # 判斷東西四命
    ming_group = "東四命" if ming_gua in EAST_GUA else "西四命"
    zhai_group = "東四宅" if zhai_gua in EAST_GUA else "西四宅"
    is_compatible = (ming_group == "東四命" and zhai_group == "東四宅") or \
                   (ming_group == "西四命" and zhai_group == "西四宅")

    # 計算各方位星曜
    directions = []
    for i, dir_name in enumerate(DIRECTION_NAMES):
        star = YOUNIAN_STAR[zhai_gua][i]
        star_info = STAR_DESCRIPTION[star]
        directions.append({
            "direction": dir_name,
            "degree": DIRECTION_NAME_TO_DEGREE[dir_name],
            "star": star,
            "type": star_info["type"],
            "wuxing": star_info["wuxing"],
            "score": star_info["score"],
            "description": star_info["description"]
        })

    # 命卦各方位星曜（以命卦為基準）
    ming_directions = []
    for i, dir_name in enumerate(DIRECTION_NAMES):
        star = YOUNIAN_STAR[ming_gua][i]
        star_info = STAR_DESCRIPTION[star]
        ming_directions.append({
            "direction": dir_name,
            "star": star,
            "type": star_info["type"],
            "score": star_info["score"]
        })

    # 找出最佳方位
    best_directions = [d for d in directions if d["type"] == "吉"]
    best_directions.sort(key=lambda x: x["score"], reverse=True)

    worst_directions = [d for d in directions if d["type"] == "凶"]
    worst_directions.sort(key=lambda x: x["score"])

    return {
        "birth_year": birth_year,
        "gender": gender,
        "ming_gua": {
            "name": ming_gua,
            "wuxing": GUA_WUXING[ming_gua],
            "group": ming_group,
            "number": GUA_NUMBER[ming_gua]
        },
        "zhai_gua": {
            "name": zhai_gua,
            "wuxing": GUA_WUXING[zhai_gua],
            "group": zhai_group,
            "number": GUA_NUMBER[zhai_gua]
        },
        "compatibility": {
            "match": is_compatible,
            "score": 90 if is_compatible else 40,
            "description": "東四命配東四宅，西四命配西四宅，為上吉" if is_compatible else "東西四命宅不配，需用風水化解"
        },
        "directions": directions,
        "ming_directions": ming_directions,
        "recommendations": {
            "best_bedroom": best_directions[0]["direction"] if best_directions else "北",
            "best_kitchen": best_directions[1]["direction"] if len(best_directions) > 1 else "東",
            "best_door": best_directions[2]["direction"] if len(best_directions) > 2 else "南",
            "avoid_toilet": worst_directions[0]["direction"] if worst_directions else "西北",
            "avoid_bedroom": worst_directions[1]["direction"] if len(worst_directions) > 1 else "西"
        },
        "confidence": 0.7  # 八宅遊年為傳統算法，置信度標記為0.7
    }


if __name__ == "__main__":
    # 測試
    result = get_bazhai_analysis(1991, "子")
    print(result)
