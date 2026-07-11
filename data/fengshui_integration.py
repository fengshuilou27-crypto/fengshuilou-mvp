# -*- coding: utf-8 -*-
"""
風水功能集成層 (Fengshui Integration Layer)

將 v3.6 新增的三個風水工具（八宅遊年、納甲樓層、羅盤工具）
集成到核心匹配邏輯中，作為現有 100 分制的補充維度。

集成策略：
- 不直接修改現有 100 分制結構（避免回歸風險）
- 在匹配結果中新增 "fengshui_extended" 子字段
- 計算一個 0-5 分的「風水精細度加分」，納入總分（上限 100）
"""

from typing import Dict, Optional

from data.ming_gua import get_ming_gua
from data.bazhai_younian import get_bazhai_analysis
from data.najia_floor import get_najia_analysis
from data.compass_tool import get_compass_info


def get_extended_fengshui(
    birth_date: str,
    gender: str,
    floor_number: int = None,
    building_facing: str = None,
    building_year: int = None
) -> Dict:
    """
    獲取擴展風水分析（八宅 + 納甲 + 羅盤）
    
    Args:
        birth_date: 格式 "YYYY-MM-DD"
        gender: "male" 或 "female"
        floor_number: 樓層號（可選）
        building_facing: 坐向（可選，如 "子"）
        building_year: 建築年份（可選，用於羅盤三元判斷）
    
    Returns:
        {
            "enabled": bool,
            "bazhai": {...},      # 八宅遊年結果
            "najia": {...},       # 納甲樓層結果（如 floor_number 提供）
            "compass": {...},     # 羅盤工具結果（如 building_facing 提供）
            "fengshui_bonus": float,  # 0-5 分精細度加分
            "bonus_rationale": str
        }
    """
    result = {
        "enabled": False,
        "bazhai": None,
        "najia": None,
        "compass": None,
        "fengshui_bonus": 0.0,
        "bonus_rationale": ""
    }
    
    bonus = 0.0
    rationale_parts = []
    
    # 1. 八宅遊年（需要出生年份和坐向）
    try:
        birth_year = int(birth_date.split("-")[0])
        # 提取坐山（如 "子山午向" → "子"）
        mountain = None
        if building_facing:
            # 簡化：取第一個字或前兩個字
            if len(building_facing) >= 2:
                mountain = building_facing[0]
        
        if mountain:
            bazhai = get_bazhai_analysis(birth_year, mountain, gender)
            result["bazhai"] = {
                "ming_gua": bazhai["ming_gua"],
                "zhai_gua": bazhai["zhai_gua"],
                "compatibility": bazhai["compatibility"],
                "recommendations": bazhai["recommendations"]
            }
            
            # 八宅匹配度加分（0-2分）
            if bazhai["compatibility"]["match"]:
                bonus += 2.0
                rationale_parts.append(f"八宅：命宅匹配（{bazhai['ming_gua']['name']}配{bazhai['zhai_gua']['name']}），+2分")
            else:
                bonus += 0.5
                rationale_parts.append(f"八宅：命宅不配（{bazhai['ming_gua']['name']}配{bazhai['zhai_gua']['name']}），+0.5分")
            
            result["enabled"] = True
    except Exception as e:
        rationale_parts.append(f"八宅分析失敗：{str(e)}")
    
    # 2. 納甲樓層（需要樓層號）
    if floor_number and floor_number > 0:
        try:
            najia = get_najia_analysis(birth_year, floor_number, gender)
            result["najia"] = {
                "floor": najia["floor"],
                "relation": najia["relation"],
                "recommendations": najia["recommendations"]
            }
            
            # 納甲樓層匹配度加分（0-1.5分）
            relation_type = najia["relation"]["type"]
            if relation_type == "大吉":
                bonus += 1.5
                rationale_parts.append(f"納甲：樓層{floor_number}與命主{najia['relation']['relation']}，+1.5分")
            elif relation_type == "吉":
                bonus += 1.0
                rationale_parts.append(f"納甲：樓層{floor_number}與命主{najia['relation']['relation']}，+1.0分")
            elif relation_type == "中吉":
                bonus += 0.5
                rationale_parts.append(f"納甲：樓層{floor_number}與命主{najia['relation']['relation']}，+0.5分")
            else:
                rationale_parts.append(f"納甲：樓層{floor_number}與命主{najia['relation']['relation']}，不加減分")
            
            result["enabled"] = True
        except Exception as e:
            rationale_parts.append(f"納甲分析失敗：{str(e)}")
    
    # 3. 羅盤工具（需要坐向）
    if building_facing and mountain:
        try:
            # 提取向首
            facing = None
            if len(building_facing) >= 3:
                facing = building_facing[2] if building_facing[1] == "山" else None
            
            if not facing and len(building_facing) >= 4:
                # 處理 "子山午向" 這種格式
                if "山" in building_facing and "向" in building_facing:
                    idx_shan = building_facing.index("山")
                    idx_xiang = building_facing.index("向")
                    if idx_xiang > idx_shan + 1:
                        facing = building_facing[idx_shan + 1:idx_xiang]
            
            if facing and mountain != facing:
                compass = get_compass_info(mountain, facing)
                if "error" not in compass:
                    result["compass"] = {
                        "pair_analysis": compass.get("pair_analysis", {}),
                        "mountain": {
                            "name": compass["mountain"]["name"],
                            "center_degree": compass["mountain"]["center_degree"]
                        },
                        "facing": {
                            "name": compass["facing"]["name"],
                            "center_degree": compass["facing"]["center_degree"]
                        }
                    }
                    
                    # 羅盤驗證加分（0-1.5分）
                    if compass.get("pair_analysis", {}).get("valid_pair"):
                        bonus += 1.5
                        rationale_parts.append(f"羅盤：山向{mountain}對{facing}為有效配對，+1.5分")
                    else:
                        bonus += 0.5
                        rationale_parts.append(f"羅盤：山向{mountain}對{facing}配對異常，+0.5分")
                    
                    result["enabled"] = True
        except Exception as e:
            rationale_parts.append(f"羅盤分析失敗：{str(e)}")
    
    result["fengshui_bonus"] = round(min(bonus, 5.0), 1)
    result["bonus_rationale"] = "；".join(rationale_parts) if rationale_parts else "無擴展風水分析數據"
    
    return result
