#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人命卦計算模組（漢五派）
算法：生年數字相加→取個位→男用11減/女用加4減9
輸出：八卦命卦（乾1/兌2/離3/震4/巽5/坎6/艮7/坤8）
"""

from typing import Dict, Any, Optional

# 八卦名稱
GUA_NAMES = ["", "乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]

# 八卦五行屬性
GUA_WUXING = {
    "乾": "金", "兌": "金",
    "離": "火",
    "震": "木", "巽": "木",
    "坎": "水",
    "艮": "土", "坤": "土"
}

# 東四命 / 西四命分類
EAST_WEST_GUA = {
    "東四命": ["震", "巽", "離", "坎"],
    "西四命": ["乾", "兌", "艮", "坤"]
}

# 八宅九宮吉凶（命卦 × 坐向）
# 格式：{命卦: {方位: 吉凶}}
BAZHAI_NINE_PALACE = {
    "乾": {
        "西北": "伏位", "西": "生氣", "西南": "延年", "南": "絕命",
        "東南": "五鬼", "東": "禍害", "北": "六煞", "東北": "天醫"
    },
    "兌": {
        "西": "伏位", "西北": "生氣", "東北": "延年", "東": "絕命",
        "南": "五鬼", "東南": "禍害", "西南": "六煞", "北": "天醫"
    },
    "離": {
        "南": "伏位", "東南": "生氣", "東": "延年", "北": "絕命",
        "東北": "五鬼", "西": "禍害", "西北": "六煞", "西南": "天醫"
    },
    "震": {
        "東": "伏位", "南": "生氣", "北": "延年", "東南": "絕命",
        "西": "五鬼", "西北": "禍害", "東北": "六煞", "西南": "天醫"
    },
    "巽": {
        "東南": "伏位", "東": "生氣", "南": "延年", "北": "絕命",
        "西南": "五鬼", "西": "禍害", "西北": "六煞", "東北": "天醫"
    },
    "坎": {
        "北": "伏位", "東": "生氣", "東南": "延年", "南": "絕命",
        "西南": "五鬼", "東北": "禍害", "西": "六煞", "西北": "天醫"
    },
    "艮": {
        "東北": "伏位", "西南": "生氣", "西北": "延年", "東": "絕命",
        "北": "五鬼", "東南": "禍害", "南": "六煞", "西": "天醫"
    },
    "坤": {
        "西南": "伏位", "東北": "生氣", "東": "延年", "東南": "絕命",
        "西北": "五鬼", "南": "禍害", "東北": "六煞", "北": "天醫"
    }
}

# 吉凶分數（通用版，待袁師傅提供漢五派專用分數）
AUSPICIOUS_SCORES = {
    "生氣": 10,
    "延年": 8,
    "天醫": 6,
    "伏位": 4
}

INAUSPICIOUS_SCORES = {
    "五鬼": -8,
    "六煞": -6,
    "禍害": -4,
    "絕命": -10
}


def calculate_life_gua(birth_year: int, gender: str) -> Dict[str, Any]:
    """
    計算人命卦
    
    算法：
    1. 生年數字相加（如1991 → 1+9+9+1 = 20）
    2. 取個位（20 → 0）
    3. 男命：11 - 個位（11 - 0 = 11）
    4. 女命：個位 + 4（0 + 4 = 4），若>9則減9（4 < 9，所以是4）
    5. 結果為1-8，對應八卦
    
    注意：個位為0時，視為10（即個位為0）
    
    Args:
        birth_year: 出生年份（如1991）
        gender: 性別（男/女）
    
    Returns:
        {
            "life_gua": 命卦名稱,
            "gua_number": 卦數（1-8）,
            "wuxing": 五行屬性,
            "east_west": 東四命/西四命,
            "auspicious_directions": 吉方列表,
            "inauspicious_directions": 凶方列表
        }
    """
    # 生年數字相加
    year_sum = sum(int(d) for d in str(birth_year))
    
    # 取個位
    unit_digit = year_sum % 10
    
    # 計算卦數
    gender_key = "男" if gender in ["男", "M", "Male", "male"] else "女"
    
    if gender_key == "男":
        # 男命：11 - 個位
        gua_number = 11 - unit_digit
    else:
        # 女命：個位 + 4，若>9則減9
        gua_number = unit_digit + 4
        if gua_number > 9:
            gua_number -= 9
    
    # 確保在1-8範圍內
    if gua_number < 1:
        gua_number += 8
    elif gua_number > 8:
        gua_number = gua_number % 8
        if gua_number == 0:
            gua_number = 8
    
    life_gua = GUA_NAMES[gua_number]
    wuxing = GUA_WUXING.get(life_gua, "未知")
    
    # 判斷東四命/西四命
    east_west = "東四命" if life_gua in EAST_WEST_GUA["東四命"] else "西四命"
    
    # 吉方/凶方（根據八宅法）
    if life_gua in BAZHAI_NINE_PALACE:
        palace = BAZHAI_NINE_PALACE[life_gua]
        auspicious = [d for d, g in palace.items() if g in AUSPICIOUS_SCORES]
        inauspicious = [d for d, g in palace.items() if g in INAUSPICIOUS_SCORES]
    else:
        auspicious = []
        inauspicious = []
    
    return {
        "birth_year": birth_year,
        "gender": gender_key,
        "year_sum": year_sum,
        "unit_digit": unit_digit,
        "life_gua": life_gua,
        "gua_number": gua_number,
        "wuxing": wuxing,
        "east_west": east_west,
        "auspicious_directions": auspicious,
        "inauspicious_directions": inauspicious,
        "rationale": f"{birth_year}年{gender_key}命，生年數字和為{year_sum}，個位{unit_digit}，經{'男命11減' if gender_key=='男' else '女命加4減9'}計算得卦數{gua_number}，為{life_gua}卦（{wuxing}），屬{east_west}。"
    }


def analyze_bazhai_nine_palace(life_gua: str, building_facing: str) -> Dict[str, Any]:
    """
    分析人命卦與樓盤坐向的八宅九宮匹配
    
    Args:
        life_gua: 命卦（乾/兌/離/震/巽/坎/艮/坤）
        building_facing: 樓盤朝向（如"南"、"東北"等）
    
    Returns:
        {
            "life_gua": 命卦,
            "building_facing": 朝向,
            "nine_palace_result": 九宮吉凶,
            "score": 分數(0-10),
            "level": 吉凶等級
        }
    """
    if life_gua not in BAZHAI_NINE_PALACE:
        return {
            "life_gua": life_gua,
            "building_facing": building_facing,
            "error": f"不支持的命卦: {life_gua}",
            "score": 0
        }
    
    palace = BAZHAI_NINE_PALACE[life_gua]
    result = palace.get(building_facing, "未知")
    
    # 計算分數
    if result in AUSPICIOUS_SCORES:
        score = AUSPICIOUS_SCORES[result]
        level = "吉"
    elif result in INAUSPICIOUS_SCORES:
        score = INAUSPICIOUS_SCORES[result]
        level = "凶"
    else:
        score = 0
        level = "平"
    
    return {
        "life_gua": life_gua,
        "building_facing": building_facing,
        "nine_palace_result": result,
        "score": score,
        "level": level,
        "rationale": f"{life_gua}命人居{building_facing}向之宅，八宅九宮為「{result}」，屬{level}。"
    }


def analyze_life_gua(birth_year: int, gender: str, building_facing: Optional[str] = None) -> Dict[str, Any]:
    """
    主分析函數：計算人命卦並可選分析與樓盤坐向的匹配
    
    Args:
        birth_year: 出生年份
        gender: 性別
        building_facing: 樓盤朝向（可選）
    
    Returns:
        完整的人命卦分析結果
    """
    life_gua_result = calculate_life_gua(birth_year, gender)
    
    result = {
        "status": "success",
        "module": "life_gua",
        "life_gua": life_gua_result
    }
    
    if building_facing:
        palace_result = analyze_bazhai_nine_palace(
            life_gua_result["life_gua"], 
            building_facing
        )
        result["bazhai_match"] = palace_result
    
    return result


# 簡單測試
if __name__ == "__main__":
    import json
    
    # 測試：1991年男性
    result = analyze_life_gua(1991, "男", "南")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 批量測試各年份
    print("\n各年份人命卦測試:")
    for year in [1984, 1985, 1990, 1991, 2000, 2001]:
        for gender in ["男", "女"]:
            r = calculate_life_gua(year, gender)
            print(f"{year}年{gender}: {r['life_gua']}卦({r['wuxing']}) - {r['east_west']}")
