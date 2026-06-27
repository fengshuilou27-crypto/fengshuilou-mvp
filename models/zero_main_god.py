from data.zero_main_god import ZERO_MAIN_GOD_TABLE, ZMG_SCORING
from data.flying_star import get_yun


def analyze_zero_main_god(building_year: int, north_has_water: bool, south_has_mountain: bool):
    """
    零正神分析模組
    根據運數判斷正神/零神方位，再根據實際山水配置打分
    """
    yun = get_yun(building_year)
    
    if yun not in ZERO_MAIN_GOD_TABLE:
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 10,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.5,
            "rationale": f"{yun}的零正神配置暫未收錄"
        }
    
    zmg = ZERO_MAIN_GOD_TABLE[yun]
    zheng_shen_dir = zmg["正神方位"]  # 正神方位
    ling_shen_dir = zmg["零神方位"]  # 零神方位
    
    score = 0
    details = []
    
    # 正神方位判斷 (MVP簡化：北側/南側)
    # 八運：正神=東北，零神=西南
    # 九運：正神=南方，零神=北方
    
    if yun == "七運":
        # 正神=西方，零神=東方
        # MVP簡化：沒有西/東環境數據，用南/北近似
        if south_has_mountain or north_has_water:
            score += ZMG_SCORING["正神見山"]
            details.append("七運環境有山/水（南有山或北有水，簡化映射）+5")
        else:
            score += 3
            details.append("七運環境無明顯山水，基礎分+3")
        
    elif yun == "八運":
        # 正神=東北 (簡化判斷：東北有山？)
        # MVP簡化：只判斷南側有山/北側有水
        # 八運正神東北，零神西南
        # 南側有山 ≈ 西南/南方有山（簡化映射）
        # 北側有水 ≈ 北方有水
        if south_has_mountain:
            score += ZMG_SCORING["正神見山"]
            details.append("八運正神見山（南側有山，簡化映射）+5")
        else:
            # 正神無山，不扣分（簡化版）
            pass
        
        if north_has_water:
            # 北側不是零神方位（零神是西南），簡化處理
            pass
        
    elif yun == "九運":
        # 正神=南方，零神=北方
        if south_has_mountain:
            score += ZMG_SCORING["正神見山"]
            details.append("九運正神見山（南側有山）+5")
        else:
            # 正神無山，不扣分
            pass
        
        if north_has_water:
            score += ZMG_SCORING["零神見水"]
            details.append("九運零神見水（北側有水）+5")
        else:
            # 零神無水，不扣分
            pass
    
    # 犯忌判斷（MVP簡化）
    penalties = 0
    penalty_desc = []
    
    if yun == "九運":
        if north_has_water and south_has_mountain:
            # 正神見山 + 零神見水 = 最佳配置
            pass
        elif not north_has_water and not south_has_mountain:
            # 無山無水，簡化判斷
            pass
    
    score = max(-10, min(10, score))
    
    return {
        "status": "success",
        "yun": yun,
        "zheng_shen": zmg["正神名"],
        "ling_shen": zmg["零神名"],
        "score": score,
        "max_score": 10,
        "details": details,
        "penalties": penalty_desc,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.55,
        "rationale": f"{yun}正神在{zmg['正神名']}，零神在{zmg['零神名']}。"
                     + ("".join(details) if details else "山水配置未提供明確加分。")
                     + " MVP為簡化計算，基於公開資料，僅供參考，建議實地勘察並諮詢專業師傅。"
    }
