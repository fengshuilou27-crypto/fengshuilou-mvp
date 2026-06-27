#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生命磁向模組（漢五派）
根據生肖+性別查詢吉位/凶位方位
純查表實現，無複雜算法
"""

from typing import Dict, List, Tuple, Any

# 生肖列表
ZODIAC_ANIMALS = [
    "鼠", "牛", "虎", "兔", "龍", "蛇",
    "馬", "羊", "猴", "雞", "狗", "豬"
]

# 方位列表
DIRECTIONS = ["北", "南", "東", "西", "東北", "東南", "西北", "西南"]

# 生命磁向對照表
# 格式: {生肖: {性別: {"吉位": [...], "凶位": [...]}}}
LIFE_MAGNETIC_TABLE = {
    "鼠": {
        "男": {
            "吉位": ["東北", "西", "西南", "北"],
            "凶位": ["南", "東", "東南", "西北"],
            "大凶": ["南"]
        },
        "女": {
            "吉位": ["西", "東北", "北", "西南"],
            "凶位": ["東", "南", "西北", "東南"],
            "大凶": ["東"]
        }
    },
    "牛": {
        "男": {
            "吉位": ["南", "東南", "東", "北"],
            "凶位": ["西", "西北", "西南", "東北"],
            "大凶": ["西"]
        },
        "女": {
            "吉位": ["東南", "南", "北", "東"],
            "凶位": ["西北", "西", "東北", "西南"],
            "大凶": ["西北"]
        }
    },
    "虎": {
        "男": {
            "吉位": ["北", "東", "東南", "南"],
            "凶位": ["西南", "西", "西北", "東北"],
            "大凶": ["西南"]
        },
        "女": {
            "吉位": ["東", "北", "南", "東南"],
            "凶位": ["西", "西南", "東北", "西北"],
            "大凶": ["西"]
        }
    },
    "兔": {
        "男": {
            "吉位": ["西北", "西南", "西", "東北"],
            "凶位": ["東南", "東", "北", "南"],
            "大凶": ["東南"]
        },
        "女": {
            "吉位": ["西南", "西北", "東北", "西"],
            "凶位": ["東", "東南", "南", "北"],
            "大凶": ["東"]
        }
    },
    "龍": {
        "男": {
            "吉位": ["西", "東北", "西南", "西北"],
            "凶位": ["北", "東南", "東", "南"],
            "大凶": ["北"]
        },
        "女": {
            "吉位": ["東北", "西", "西北", "西南"],
            "凶位": ["東南", "北", "南", "東"],
            "大凶": ["東南"]
        }
    },
    "蛇": {
        "男": {
            "吉位": ["南", "東", "北", "東南"],
            "凶位": ["東北", "西北", "西", "西南"],
            "大凶": ["東北"]
        },
        "女": {
            "吉位": ["北", "南", "東南", "東"],
            "凶位": ["西北", "東北", "西南", "西"],
            "大凶": ["西北"]
        }
    },
    "馬": {
        "男": {
            "吉位": ["東南", "東", "東北", "南"],
            "凶位": ["北", "西", "西南", "西北"],
            "大凶": ["北"]
        },
        "女": {
            "吉位": ["東", "東南", "南", "東北"],
            "凶位": ["西", "北", "西北", "西南"],
            "大凶": ["西"]
        }
    },
    "羊": {
        "男": {
            "吉位": ["西北", "北", "西", "西南"],
            "凶位": ["東", "南", "東北", "東南"],
            "大凶": ["東"]
        },
        "女": {
            "吉位": ["北", "西北", "西南", "西"],
            "凶位": ["南", "東", "東南", "東北"],
            "大凶": ["南"]
        }
    },
    "猴": {
        "男": {
            "吉位": ["東北", "西南", "西北", "西"],
            "凶位": ["南", "東", "東南", "北"],
            "大凶": ["南"]
        },
        "女": {
            "吉位": ["西南", "東北", "西", "西北"],
            "凶位": ["東", "南", "北", "東南"],
            "大凶": ["東"]
        }
    },
    "雞": {
        "男": {
            "吉位": ["南", "東南", "北", "東"],
            "凶位": ["西北", "西南", "東北", "西"],
            "大凶": ["西北"]
        },
        "女": {
            "吉位": ["東南", "南", "東", "北"],
            "凶位": ["西南", "西北", "西", "東北"],
            "大凶": ["西南"]
        }
    },
    "狗": {
        "男": {
            "吉位": ["東", "北", "東南", "東北"],
            "凶位": ["西", "西北", "西南", "南"],
            "大凶": ["西"]
        },
        "女": {
            "吉位": ["北", "東", "東北", "東南"],
            "凶位": ["西北", "西", "南", "西南"],
            "大凶": ["西北"]
        }
    },
    "豬": {
        "男": {
            "吉位": ["西南", "西北", "東北", "西"],
            "凶位": ["東南", "南", "東", "北"],
            "大凶": ["東南"]
        },
        "女": {
            "吉位": ["西北", "西南", "西", "東北"],
            "凶位": ["南", "東南", "北", "東"],
            "大凶": ["南"]
        }
    }
}


def get_zodiac_from_year(year: int) -> str:
    """
    根據年份獲取生肖
    
    注意：農曆新年邊界需外部處理，這裡使用簡化版（按公曆年份）
    """
    # 1984年是甲子年（鼠年）
    zodiac_index = (year - 1984) % 12
    if zodiac_index < 0:
        zodiac_index += 12
    return ZODIAC_ANIMALS[zodiac_index]


def get_life_magnetic_direction(zodiac: str, gender: str) -> Dict[str, Any]:
    """
    獲取生命磁向信息
    
    Args:
        zodiac: 生肖（鼠/牛/虎/.../豬）
        gender: 性別（男/女）
    
    Returns:
        {
            "zodiac": 生肖,
            "gender": 性別,
            "auspicious": 吉位列表,
            "inauspicious": 凶位列表,
            "severely_inauspicious": 大凶位列表,
            "best_direction": 最佳方位,
            "worst_direction": 最差方位,
            "score": 該維度得分(0-15)
        }
    """
    if zodiac not in LIFE_MAGNETIC_TABLE:
        return {
            "zodiac": zodiac,
            "gender": gender,
            "error": f"不支持的生肖: {zodiac}",
            "score": 0
        }
    
    gender_key = "男" if gender in ["男", "M", "Male", "male"] else "女"
    
    data = LIFE_MAGNETIC_TABLE[zodiac].get(gender_key, LIFE_MAGNETIC_TABLE[zodiac]["男"])
    
    auspicious = data.get("吉位", [])
    inauspicious = data.get("凶位", [])
    severely = data.get("大凶", [])
    
    # 計算分數：基於吉位數量（簡化版）
    # 4個吉位 = 15分，3個 = 11分，2個 = 8分，1個 = 4分，0個 = 0分
    score_map = {4: 15, 3: 11, 2: 8, 1: 4, 0: 0}
    score = score_map.get(len(auspicious), 0)
    
    return {
        "zodiac": zodiac,
        "gender": gender_key,
        "auspicious": auspicious,
        "inauspicious": inauspicious,
        "severely_inauspicious": severely,
        "best_direction": auspicious[0] if auspicious else None,
        "worst_direction": severely[0] if severely else (inauspicious[0] if inauspicious else None),
        "score": score,
        "rationale": f"{zodiac}年{gender_key}命，吉位在{'、'.join(auspicious)}，凶位在{'、'.join(inauspicious)}，大凶位在{'、'.join(severely)}。"
    }


def analyze_life_magnetic_direction(birth_year: int, gender: str) -> Dict[str, Any]:
    """
    主分析函數：根據出生年份和性別分析生命磁向
    
    Args:
        birth_year: 出生年份（如1991）
        gender: 性別（男/女）
    
    Returns:
        完整的生命磁向分析結果
    """
    zodiac = get_zodiac_from_year(birth_year)
    result = get_life_magnetic_direction(zodiac, gender)
    
    return {
        "status": "success" if "error" not in result else "error",
        "module": "life_magnetic_direction",
        "birth_year": birth_year,
        **result
    }


def check_direction_compatibility(zodiac: str, gender: str, building_facing: str) -> Dict[str, Any]:
    """
    檢查樓盤朝向與生命磁向的匹配度
    
    Args:
        zodiac: 生肖
        gender: 性別
        building_facing: 樓盤朝向（如"南"、"東北"等）
    
    Returns:
        匹配度分析結果
    """
    lmd = get_life_magnetic_direction(zodiac, gender)
    
    if "error" in lmd:
        return lmd
    
    auspicious = lmd.get("auspicious", [])
    inauspicious = lmd.get("inauspicious", [])
    severely = lmd.get("severely_inauspicious", [])
    
    # 匹配度判斷
    if building_facing in auspicious:
        match_level = "大吉"
        match_score = 100
    elif building_facing in severely:
        match_level = "大凶"
        match_score = 0
    elif building_facing in inauspicious:
        match_level = "凶"
        match_score = 30
    else:
        match_level = "平"
        match_score = 50
    
    return {
        "zodiac": zodiac,
        "gender": gender,
        "building_facing": building_facing,
        "match_level": match_level,
        "match_score": match_score,
        "auspicious_directions": auspicious,
        "inauspicious_directions": inauspicious,
        "recommendation": f"該樓盤朝向為{building_facing}，對{zodiac}年{gender}命人來說屬{match_level}。"
    }


# 簡單測試
if __name__ == "__main__":
    # 測試：1991年（羊年）男性
    result = analyze_life_magnetic_direction(1991, "男")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 測試朝向匹配
    compat = check_direction_compatibility("羊", "男", "南")
    print("\n朝向匹配:")
    print(json.dumps(compat, ensure_ascii=False, indent=2))
