# -*- coding: utf-8 -*-
"""
公共命卦計算模塊 (data/ming_gua.py)

統一所有風水模塊的命卦計算，避免算法不一致：
- 八宅匹配（models/bagua_matching.py）
- 八宅遊年（data/bazhai_younian.py）
- 納甲樓層（data/najia_floor.py）

算法：100 年算法（v3.3 含立春分界）
男命：(100 - 出生年後兩位) ÷ 9，取餘數（整除取9）
女命：(出生年後兩位 - 4) ÷ 9，取餘數（整除取9）
餘5：男命寄艮(8)，女命寄坤(2)
命卦數：1坎 2坤 3震 4巽 6乾 7兌 8艮 9離

立春分界：1-2月出生的用戶需按農曆年調整（見 get_lunar_year_for_ming_gua）
"""

from data.solar_term import get_lunar_year_for_ming_gua

# 命卦數 -> 卦名
MING_GUA_MAP = {
    1: "坎", 2: "坤", 3: "震", 4: "巽",
    6: "乾", 7: "兌", 8: "艮", 9: "離"
}

# 八卦五行
GUA_WUXING = {
    "坎": "水", "艮": "土", "震": "木", "巽": "木",
    "離": "火", "坤": "土", "兌": "金", "乾": "金"
}

# 東四命 / 西四命
EAST_FOUR_GUA = {"坎", "震", "巽", "離"}
WEST_FOUR_GUA = {"坤", "兌", "乾", "艮"}


def calc_ming_gua(birth_year: int, gender: str) -> int:
    """
    命卦計算公式（100年算法）
    
    Args:
        birth_year: 已調整後的年份（如需立春調整，先調用 get_lunar_year_for_ming_gua）
        gender: "男" 或 "女"
    
    Returns:
        命卦數（1-9，不含5）
    """
    year_last_two = int(str(birth_year)[-2:])
    
    if gender == "男":
        gua_num = (100 - year_last_two) % 9
    else:
        gua_num = (year_last_two - 4) % 9
    
    if gua_num == 0:
        gua_num = 9
    if gua_num == 5:
        gua_num = 8 if gender == "男" else 2
    
    return gua_num


def get_ming_gua(birth_date: str, gender: str) -> dict:
    """
    完整命卦計算（含立春分界調整）
    
    Args:
        birth_date: 格式 "YYYY-MM-DD"
        gender: "male" 或 "female"（也接受 "男" 或 "女"）
    
    Returns:
        {
            "gua_num": 命卦數,
            "gua_name": 卦名,
            "wuxing": 五行,
            "group": "東四命" 或 "西四命",
            "lunar_year_adjusted": bool,
            "original_year": int,
            "lunar_year": int
        }
    """
    # 標準化性別
    gender_std = "男" if gender in ("男", "male") else "女"
    
    # 立春調整
    lunar_year = get_lunar_year_for_ming_gua(birth_date)
    original_year = int(birth_date.split("-")[0]) if "-" in birth_date else lunar_year
    
    # 計算命卦
    gua_num = calc_ming_gua(lunar_year, gender_std)
    gua_name = MING_GUA_MAP.get(gua_num, "未知")
    wuxing = GUA_WUXING.get(gua_name, "未知")
    group = "東四命" if gua_name in EAST_FOUR_GUA else "西四命"
    
    return {
        "gua_num": gua_num,
        "gua_name": gua_name,
        "wuxing": wuxing,
        "group": group,
        "lunar_year_adjusted": lunar_year != original_year,
        "original_year": original_year,
        "lunar_year": lunar_year
    }


def get_ming_gua_by_year(birth_year: int, gender: str) -> dict:
    """
    僅按年份計算命卦（無立春調整）
    
    用於 API 端點只提供年份（如 /api/fengshui/bazhai）時的快速查詢。
    注意：1-2月出生的用戶可能與完整計算結果不同。
    
    Args:
        birth_year: 公曆年份
        gender: "male" 或 "female"（也接受 "男" 或 "女"）
    """
    gender_std = "男" if gender in ("男", "male") else "女"
    gua_num = calc_ming_gua(birth_year, gender_std)
    gua_name = MING_GUA_MAP.get(gua_num, "未知")
    wuxing = GUA_WUXING.get(gua_name, "未知")
    group = "東四命" if gua_name in EAST_FOUR_GUA else "西四命"
    
    return {
        "gua_num": gua_num,
        "gua_name": gua_name,
        "wuxing": wuxing,
        "group": group
    }
