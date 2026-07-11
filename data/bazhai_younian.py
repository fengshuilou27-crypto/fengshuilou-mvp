# -*- coding: utf-8 -*-
"""
八宅遊年模塊 (Bazhai Younian / Eight Mansions) — v3.6 修復版

修復內容：
- 命卦計算統一使用 data.ming_gua 的 100 年算法（與 bagua_matching.py 一致）
- 移除本地獨立算法，避免系統不一致

八宅風水根據命卦與宅卦的匹配，計算八個方位的吉凶：
- 四吉方：生氣、延年、天醫、伏位
- 四凶方：五鬼、六煞、禍害、絕命

來源：八宅明鏡 / 陽宅愛眾篇
"""

from typing import Dict, List, Tuple, Optional

# 統一命卦計算
from data.ming_gua import (
    get_ming_gua_by_year, GUA_WUXING,
    EAST_FOUR_GUA, WEST_FOUR_GUA, MING_GUA_MAP
)

# 八宅方位表從 bagua 導入（與 bagua_matching.py 一致）
from data.bagua import BAGUA_DIRECTION_TABLE

# GUA_NUMBER 為 MING_GUA_MAP 的反向映射
GUA_NUMBER = {v: k for k, v in MING_GUA_MAP.items()}

# 東四命 vs 西四命（與 data.ming_gua 一致）
EAST_GUA = EAST_FOUR_GUA
WEST_GUA = WEST_FOUR_GUA

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


def get_bazhai_analysis(birth_year: int, facing: str, gender: str = "male") -> Dict:
    """
    八宅遊年分析主入口
    """
    # 統一命卦計算（與 bagua_matching.py 一致）
    ming = get_ming_gua_by_year(birth_year, gender)
    ming_gua = ming["gua_name"]
    
    # 計算宅卦（根據坐向）
    zhai_gua = FACING_TO_GUA.get(facing, "坎")
    
    # 判斷東西四命
    ming_group = ming["group"]
    zhai_group = "東四宅" if zhai_gua in EAST_GUA else "西四宅"
    is_compatible = (ming_group == "東四命" and zhai_group == "東四宅") or \
                   (ming_group == "西四命" and zhai_group == "西四宅")
    
    # 使用 BAGUA_DIRECTION_TABLE 生成八宅方位（與 bagua_matching.py 一致）
    gua_directions = BAGUA_DIRECTION_TABLE.get(ming_gua, {})
    
    # 構建各方位詳細信息
    directions = []
    for star_name, direction in gua_directions.items():
        star_info = STAR_DESCRIPTION.get(star_name, {"type": "未知", "score": 50, "description": ""})
        directions.append({
            "direction": direction,
            "star": star_name,
            "type": star_info["type"],
            "wuxing": star_info["wuxing"],
            "score": star_info["score"],
            "description": star_info["description"]
        })
    
    # 找出最佳方位（四吉方）
    best_directions = [d for d in directions if d["type"] == "吉"]
    best_directions.sort(key=lambda x: x["score"], reverse=True)
    
    worst_directions = [d for d in directions if d["type"] == "凶"]
    worst_directions.sort(key=lambda x: x["score"])
    
    # 從 BAGUA_DIRECTION_TABLE 生成宅卦各方位（與命卦對比）
    zhai_directions = BAGUA_DIRECTION_TABLE.get(zhai_gua, {})
    
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
        "gua_directions": gua_directions,
        "zhai_directions": zhai_directions,
        "recommendations": {
            "best_bedroom": best_directions[0]["direction"] if best_directions else "北",
            "best_kitchen": best_directions[1]["direction"] if len(best_directions) > 1 else "東",
            "best_door": best_directions[2]["direction"] if len(best_directions) > 2 else "南",
            "avoid_toilet": worst_directions[0]["direction"] if worst_directions else "西北",
            "avoid_bedroom": worst_directions[1]["direction"] if len(worst_directions) > 1 else "西"
        },
        "confidence": 0.75,  # 與 bagua_matching.py 一致
        "note": "八宅遊年分析已統一使用 data.ming_gua 算法，與 bagua_matching.py 一致。"
    }


if __name__ == "__main__":
    # 測試
    result = get_bazhai_analysis(1991, "子")
    print(result)
