from data.zero_main_god import ZERO_MAIN_GOD_TABLE, ZMG_SCORING
from data.flying_star import get_yun, FLYING_STAR_TABLE, CURRENT_LING_STAR
from data.goal import STAR_NUMBER_MAP as FS_STAR_NUMBER_MAP


def analyze_zero_main_god(building_year: int, building_facing: str, north_has_water: bool, south_has_mountain: bool, 
                          northeast_has_mountain: bool = None, southwest_has_mountain: bool = None,
                          east_has_water: bool = None, west_has_water: bool = None):
    """
    零正神分析模組 (v2.5 修正版)
    
    根據運數和宅運盤，動態判斷正神/零神位置，再根據山水配置打分。
    
    修正內容（v2.5）：
    - 修復七運正神方位映射：正神=西方（非南方）
    - 修復八運正神方位映射：正神=東北（非南方），零神=西南（非北方）
    - 引入可選方位參數（northeast_has_mountain, southwest_has_mountain, east_has_water, west_has_water）
      當有精確GIS方位數據時優先使用，否則回退到簡化映射（帶有警告）
    
    邏輯：
    1. 正神 = 當運星所在方位 (九運=9紫在南方)
    2. 零神 = 與正神相對的方位 (通常為未來星或失令星)
    3. 正神宜見山 (旺丁)，零神宜見水 (旺財)
    4. 到山到向 = 正神在坐山，零神在向方 = 大吉
    5. 上山下水 = 正神在向方，零神在坐山 = 大凶
    """
    yun = get_yun(building_year)
    
    if yun not in ZERO_MAIN_GOD_TABLE:
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 10,
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.5,
            "rationale": f"{yun}的零正神配置暫未收錄"
        }
    
    zmg = ZERO_MAIN_GOD_TABLE[yun]
    zheng_shen_dir = zmg["正神方位"]
    ling_shen_dir = zmg["零神方位"]
    
    # 獲取當運星數字
    current_star_num = CURRENT_LING_STAR.get(yun, 8)
    
    # 查找宅運盤中當運星的位置 (動態分析)
    star_positions = []
    if yun in FLYING_STAR_TABLE and building_facing in FLYING_STAR_TABLE[yun]:
        chart = FLYING_STAR_TABLE[yun][building_facing]
        mountain_stars = chart.get("mountain_stars", {})
        facing_stars = chart.get("facing_stars", {})
        pan_type = chart.get("pan_type", "其他")
        
        # 查找山星盤中當運星位置
        for direction, num in mountain_stars.items():
            if num == current_star_num:
                star_positions.append({"plate": "山星盤", "direction": direction, "star": num})
        
        # 查找向星盤中當運星位置
        for direction, num in facing_stars.items():
            if num == current_star_num:
                star_positions.append({"plate": "向星盤", "direction": direction, "star": num})
    
    score = 0
    details = []
    
    # 基於宅運盤類型判定
    if yun in FLYING_STAR_TABLE and building_facing in FLYING_STAR_TABLE[yun]:
        chart = FLYING_STAR_TABLE[yun][building_facing]
        pan_type = chart.get("pan_type", "其他")
        
        if pan_type == "到山到向":
            # 到山到向 = 正神在坐山，零神在向方 = 最佳配置
            score += 8
            details.append(f"{yun}到山到向，正神當令坐山，零神當令向方，大吉+8")
        elif pan_type == "上山下水":
            # 上山下水 = 正神在向方，零神在坐山 = 最差配置
            score -= 5
            details.append(f"{yun}上山下水，正神零神顛倒，損財傷丁-5")
        elif pan_type == "雙星會向":
            # 雙星會向 = 旺財不旺丁
            score += 3
            details.append(f"{yun}雙星會向，旺財之局+3")
        elif pan_type == "雙星會坐":
            # 雙星會坐 = 旺丁不旺財
            score += 3
            details.append(f"{yun}雙星會坐，旺丁之局+3")
    
    # 環境配置判定 (v2.5 修正：使用精確方位映射)
    if yun == "七運":
        # 正神=西方，零神=東方
        # 正神宜見山（西方有山=旺丁），零神宜見水（東方有水=旺財）
        if west_has_water is not None:
            # 精確模式：有 west_has_water 參數
            if west_has_water:
                score += ZMG_SCORING["正神見水"]  # 正神見水 = 凶
                details.append("七運正神在西方，西方見水-5")
            else:
                details.append("七運正神在西方，西方無水")
        elif east_has_water is not None:
            if east_has_water:
                score += ZMG_SCORING["零神見水"]  # 零神見水 = 吉
                details.append("七運零神在東方，東方見水+5")
            else:
                details.append("七運零神在東方，東方無水")
        else:
            # 回退到簡化映射（帶有警告）
            if south_has_mountain:
                score += ZMG_SCORING["正神見山"]
                details.append("七運正神見山(南側有山，簡化映射：南≈西南/西，回退模式)+5 ⚠️ 請提供精確方位數據")
            if north_has_water:
                score += ZMG_SCORING["零神見水"]
                details.append("七運零神見水(北側有水，簡化映射：北≈東北/東，回退模式)+5 ⚠️ 請提供精確方位數據")
            
    elif yun == "八運":
        # 正神=東北，零神=西南
        # 正神宜見山（東北有山=旺丁），零神宜見水（西南有水=旺財）
        if northeast_has_mountain is not None:
            # 精確模式
            if northeast_has_mountain:
                score += ZMG_SCORING["正神見山"]  # 正神見山 = 吉
                details.append("八運正神在東北，東北見山+5")
            else:
                details.append("八運正神在東北，東北無山")
        else:
            # 回退模式：無精確數據，使用 south_has_mountain 簡化映射
            if south_has_mountain:
                # 南有山 → 可能是西南有山（零神見山=凶）
                score += ZMG_SCORING["零神見山"]  # 修正：零神在西南，不是正神
                details.append("八運零神在西南，南/西南有山，零神見山-5 ⚠️ 請提供精確方位數據")
        
        if southwest_has_mountain is not None:
            if southwest_has_mountain:
                score += ZMG_SCORING["零神見山"]  # 零神見山 = 凶
                details.append("八運零神在西南，西南見山-5")
            else:
                details.append("八運零神在西南，西南無山")
        else:
            # 回退模式：north_has_water 映射
            if north_has_water:
                # 北有水 → 可能是東北有水（正神見水=凶）
                score += ZMG_SCORING["正神見水"]  # 修正：正神在東北，北≈東北
                details.append("八運正神在東北，北/東北有水，正神見水-5 ⚠️ 請提供精確方位數據")
            
    elif yun == "九運":
        # 正神=南方，零神=北方
        # 正神宜見山（南方有山=旺丁），零神宜見水（北方有水=旺財）
        # 九運的南北映射是正確的，因為正神=南方，零神=北方
        if south_has_mountain:
            score += ZMG_SCORING["正神見山"]
            details.append("九運正神見山(南側有山)+5")
        else:
            details.append("九運正神無山，不加分")
        
        if north_has_water:
            score += ZMG_SCORING["零神見水"]
            details.append("九運零神見水(北側有水)+5")
        else:
            details.append("九運零神無水，不加分")
    
    score = max(-10, min(10, score))
    
    # 動態置信度（v2.5：基於數據精確度）
    confidence = 0.7
    if yun in ["七運", "八運"] and (northeast_has_mountain is None and southwest_has_mountain is None and 
                                      east_has_water is None and west_has_water is None):
        confidence = 0.5  # 使用回退模式，置信度降低
    
    return {
        "status": "success",
        "yun": yun,
        "zheng_shen": zmg["正神名"],
        "ling_shen": zmg["零神名"],
        "current_star": current_star_num,
        "star_positions": star_positions,
        "score": score,
        "max_score": 10,
        "details": details,
        "data_source": "三六風水網專業知識庫",
        "confidence": confidence,
        "rationale": f"{yun}正神在{zmg['正神名']}，零神在{zmg['零神名']}，當運星為{current_star_num}。"
                     + ("".join(details) if details else "")
                     + " 基於三六風水網專業知識庫計算，僅供參考，建議實地勘察並諮詢專業師傅。"
    }
