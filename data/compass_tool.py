# -*- coding: utf-8 -*-
"""
羅盤工具模塊 (Compass Tool / Luopan)

二十四山羅盤詳細信息：
- 二十四山 = 十二地支 + 八天干 + 四維卦
- 每山15度，共360度
- 每山再分為五個分金（每分金3度）

來源：羅經解 / 欽定協紀辨方書
"""

from typing import Dict, List, Tuple, Optional
import math

# ===================== 二十四山數據 =====================

MOUNTAIN_24_DATA = [
    # 地支十二山
    {"name": "子", "type": "地支", "degree_start": 352.5, "degree_end": 7.5, "gua": "坎", "yinyang": "陽", "wuxing": "水"},
    {"name": "丑", "type": "地支", "degree_start": 22.5, "degree_end": 37.5, "gua": "艮", "yinyang": "陰", "wuxing": "土"},
    {"name": "寅", "type": "地支", "degree_start": 52.5, "degree_end": 67.5, "gua": "艮", "yinyang": "陽", "wuxing": "木"},
    {"name": "卯", "type": "地支", "degree_start": 82.5, "degree_end": 97.5, "gua": "震", "yinyang": "陰", "wuxing": "木"},
    {"name": "辰", "type": "地支", "degree_start": 112.5, "degree_end": 127.5, "gua": "巽", "yinyang": "陽", "wuxing": "土"},
    {"name": "巳", "type": "地支", "degree_start": 142.5, "degree_end": 157.5, "gua": "巽", "yinyang": "陰", "wuxing": "火"},
    {"name": "午", "type": "地支", "degree_start": 172.5, "degree_end": 187.5, "gua": "離", "yinyang": "陽", "wuxing": "火"},
    {"name": "未", "type": "地支", "degree_start": 202.5, "degree_end": 217.5, "gua": "坤", "yinyang": "陰", "wuxing": "土"},
    {"name": "申", "type": "地支", "degree_start": 232.5, "degree_end": 247.5, "gua": "坤", "yinyang": "陽", "wuxing": "金"},
    {"name": "酉", "type": "地支", "degree_start": 262.5, "degree_end": 277.5, "gua": "兌", "yinyang": "陰", "wuxing": "金"},
    {"name": "戌", "type": "地支", "degree_start": 292.5, "degree_end": 307.5, "gua": "乾", "yinyang": "陽", "wuxing": "土"},
    {"name": "亥", "type": "地支", "degree_start": 322.5, "degree_end": 337.5, "gua": "乾", "yinyang": "陰", "wuxing": "水"},
    # 天干八山
    {"name": "壬", "type": "天干", "degree_start": 337.5, "degree_end": 352.5, "gua": "坎", "yinyang": "陽", "wuxing": "水"},
    {"name": "癸", "type": "天干", "degree_start": 7.5, "degree_end": 22.5, "gua": "坎", "yinyang": "陰", "wuxing": "水"},
    {"name": "甲", "type": "天干", "degree_start": 67.5, "degree_end": 82.5, "gua": "震", "yinyang": "陽", "wuxing": "木"},
    {"name": "乙", "type": "天干", "degree_start": 97.5, "degree_end": 112.5, "gua": "震", "yinyang": "陰", "wuxing": "木"},
    {"name": "丙", "type": "天干", "degree_start": 157.5, "degree_end": 172.5, "gua": "離", "yinyang": "陽", "wuxing": "火"},
    {"name": "丁", "type": "天干", "degree_start": 187.5, "degree_end": 202.5, "gua": "離", "yinyang": "陰", "wuxing": "火"},
    {"name": "庚", "type": "天干", "degree_start": 247.5, "degree_end": 262.5, "gua": "兌", "yinyang": "陽", "wuxing": "金"},
    {"name": "辛", "type": "天干", "degree_start": 277.5, "degree_end": 292.5, "gua": "兌", "yinyang": "陰", "wuxing": "金"},
    # 四維卦四山
    {"name": "乾", "type": "維卦", "degree_start": 307.5, "degree_end": 322.5, "gua": "乾", "yinyang": "陽", "wuxing": "金"},
    {"name": "巽", "type": "維卦", "degree_start": 127.5, "degree_end": 142.5, "gua": "巽", "yinyang": "陰", "wuxing": "木"},
    {"name": "艮", "type": "維卦", "degree_start": 37.5, "degree_end": 52.5, "gua": "艮", "yinyang": "陽", "wuxing": "土"},
    {"name": "坤", "type": "維卦", "degree_start": 217.5, "degree_end": 232.5, "gua": "坤", "yinyang": "陰", "wuxing": "土"},
]

# 分金（每山分五個分金，每分金3度）
FEN_JIN_NAMES = ["甲子", "丙子", "戊子", "庚子", "壬子"]

# 山向配對（正對關係）
MOUNTAIN_PAIRS = {
    "子": "午", "午": "子",
    "丑": "未", "未": "丑",
    "寅": "申", "申": "寅",
    "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰",
    "巳": "亥", "亥": "巳",
    "乾": "巽", "巽": "乾",
    "艮": "坤", "坤": "艮",
    "壬": "丙", "丙": "壬",
    "癸": "丁", "丁": "癸",
    "甲": "庚", "庚": "甲",
    "乙": "辛", "辛": "乙",
}

# 三元九運對應（二十四山分上元、中元、下元）
YUAN_CLASS = {
    "子": "上元", "丑": "中元", "寅": "下元",
    "卯": "上元", "辰": "中元", "巳": "下元",
    "午": "上元", "未": "中元", "申": "下元",
    "酉": "上元", "戌": "中元", "亥": "下元",
    "壬": "上元", "癸": "上元", "甲": "上元", "乙": "上元",
    "丙": "下元", "丁": "下元", "庚": "下元", "辛": "下元",
    "乾": "下元", "巽": "中元", "艮": "上元", "坤": "中元",
}


def get_mountain_info(mountain_name: str) -> Optional[Dict]:
    """獲取單山的詳細信息"""
    for m in MOUNTAIN_24_DATA:
        if m["name"] == mountain_name:
            return m
    return None


def calculate_fen_jin(mountain_name: str) -> List[Dict]:
    """計算某山的五個分金"""
    mountain = get_mountain_info(mountain_name)
    if not mountain:
        return []

    start_deg = mountain["degree_start"]
    # 處理跨0度的情況（如子山）
    if start_deg > mountain["degree_end"]:
        start_deg = start_deg - 360

    fen_jin_list = []
    for i, name in enumerate(FEN_JIN_NAMES):
        fj_start = start_deg + i * 3
        fj_end = fj_start + 3
        # 處理跨0度
        if fj_start < 0:
            fj_start += 360
        if fj_end < 0:
            fj_end += 360
        if fj_end > 360:
            fj_end -= 360

        fen_jin_list.append({
            "name": f"{mountain_name}{name}",
            "degree_start": round(fj_start % 360, 1),
            "degree_end": round(fj_end % 360, 1),
            "center_degree": round((fj_start + 1.5) % 360, 1)
        })

    return fen_jin_list


def get_compass_info(mountain: str, facing: str) -> Dict:
    """
    羅盤工具主入口
    """
    mountain_info = get_mountain_info(mountain)
    facing_info = get_mountain_info(facing)

    if not mountain_info or not facing_info:
        return {"error": "無效的山向名稱"}

    # 驗證山向是否正對
    is_valid_pair = MOUNTAIN_PAIRS.get(mountain) == facing

    # 計算分金
    mountain_fen_jin = calculate_fen_jin(mountain)
    facing_fen_jin = calculate_fen_jin(facing)

    # 計算坐向中心度數
    mountain_center = (mountain_info["degree_start"] + mountain_info["degree_end"]) / 2
    if mountain_info["degree_start"] > mountain_info["degree_end"]:
        mountain_center = (mountain_info["degree_start"] - 360 + mountain_info["degree_end"]) / 2
        if mountain_center < 0:
            mountain_center += 360

    facing_center = (facing_info["degree_start"] + facing_info["degree_end"]) / 2
    if facing_info["degree_start"] > facing_info["degree_end"]:
        facing_center = (facing_info["degree_start"] - 360 + facing_info["degree_end"]) / 2
        if facing_center < 0:
            facing_center += 360

    # 山向夾角
    angle_diff = abs(facing_center - mountain_center)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff

    # 三元分類
    mountain_yuan = YUAN_CLASS.get(mountain, "未知")
    facing_yuan = YUAN_CLASS.get(facing, "未知")
    same_yuan = mountain_yuan == facing_yuan

    return {
        "mountain": {
            "name": mountain,
            "type": mountain_info["type"],
            "degree_start": mountain_info["degree_start"],
            "degree_end": mountain_info["degree_end"],
            "center_degree": round(mountain_center, 1),
            "gua": mountain_info["gua"],
            "yinyang": mountain_info["yinyang"],
            "wuxing": mountain_info["wuxing"],
            "yuan": mountain_yuan,
            "fen_jin": mountain_fen_jin
        },
        "facing": {
            "name": facing,
            "type": facing_info["type"],
            "degree_start": facing_info["degree_start"],
            "degree_end": facing_info["degree_end"],
            "center_degree": round(facing_center, 1),
            "gua": facing_info["gua"],
            "yinyang": facing_info["yinyang"],
            "wuxing": facing_info["wuxing"],
            "yuan": facing_yuan,
            "fen_jin": facing_fen_jin
        },
        "pair_analysis": {
            "valid_pair": is_valid_pair,
            "angle_difference": round(angle_diff, 1),
            "same_yuan": same_yuan,
            "yuan_compatibility": "三元配合" if same_yuan else "三元不純"
        },
        "all_mountains": [
            {
                "name": m["name"],
                "type": m["type"],
                "center_degree": round(
                    (m["degree_start"] + m["degree_end"]) / 2 if m["degree_start"] < m["degree_end"] else
                    (m["degree_start"] - 360 + m["degree_end"]) / 2 + 360 if (m["degree_start"] - 360 + m["degree_end"]) / 2 < 0 else
                    (m["degree_start"] - 360 + m["degree_end"]) / 2, 1
                ),
                "gua": m["gua"],
                "wuxing": m["wuxing"]
            }
            for m in MOUNTAIN_24_DATA
        ],
        "confidence": 0.9  # 羅盤度數為精確計算，置信度較高
    }


if __name__ == "__main__":
    # 測試
    result = get_compass_info("子", "午")
    print(result)
