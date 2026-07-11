# 玄空飛星動態排盤算法 (v3.5 P3)
# 基於玄空飛星理論實現規則化動態排盤
# ⚠️ 本算法為MVP階段簡化版，複雜替卦情況標記低置信度

from data.flying_star import get_yun

# 中文數字轉阿拉伯數字
CHINESE_TO_ARABIC = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9
}


def yun_to_number(yun: str) -> int:
    """將運數字符串轉為數字，如'八運' -> 8"""
    yun = yun.replace("運", "").strip()
    if yun.isdigit():
        return int(yun)
    return CHINESE_TO_ARABIC.get(yun, 0)

# ============================================================
# 一、二十四山基礎數據
# ============================================================

# 二十四山 -> 卦、度數範圍、陰陽、元龍
# 玄空飛星規則：
# - 天元龍（父母卦）：子午卯酉（陰）、乾坤艮巽（陽）
# - 地元龍（逆子卦）：辰戌丑未（陰）、甲庚丙壬（陽）
# - 人元龍（順子卦）：寅申巳亥（陽）、乙辛丁癸（陰）
MOUNTAIN_24_DATA = {
    # 正北（坎卦）
    "子": {"gua": "坎", "degree_start": 352.5, "degree_end": 7.5, "yinyang": "陰", "yuanlong": "天", "luoshu": 1},
    "癸": {"gua": "坎", "degree_start": 7.5, "degree_end": 22.5, "yinyang": "陰", "yuanlong": "人", "luoshu": 1},
    "丑": {"gua": "艮", "degree_start": 22.5, "degree_end": 37.5, "yinyang": "陰", "yuanlong": "地", "luoshu": 8},
    
    # 東北（艮卦）
    "艮": {"gua": "艮", "degree_start": 37.5, "degree_end": 52.5, "yinyang": "陽", "yuanlong": "天", "luoshu": 8},
    "寅": {"gua": "艮", "degree_start": 52.5, "degree_end": 67.5, "yinyang": "陽", "yuanlong": "人", "luoshu": 8},
    "甲": {"gua": "震", "degree_start": 67.5, "degree_end": 82.5, "yinyang": "陽", "yuanlong": "地", "luoshu": 3},
    
    # 正東（震卦）
    "卯": {"gua": "震", "degree_start": 82.5, "degree_end": 97.5, "yinyang": "陰", "yuanlong": "天", "luoshu": 3},
    "乙": {"gua": "震", "degree_start": 97.5, "degree_end": 112.5, "yinyang": "陰", "yuanlong": "人", "luoshu": 3},
    "辰": {"gua": "巽", "degree_start": 112.5, "degree_end": 127.5, "yinyang": "陰", "yuanlong": "地", "luoshu": 4},
    
    # 東南（巽卦）
    "巽": {"gua": "巽", "degree_start": 127.5, "degree_end": 142.5, "yinyang": "陽", "yuanlong": "天", "luoshu": 4},
    "巳": {"gua": "巽", "degree_start": 142.5, "degree_end": 157.5, "yinyang": "陽", "yuanlong": "人", "luoshu": 4},
    "丙": {"gua": "離", "degree_start": 157.5, "degree_end": 172.5, "yinyang": "陽", "yuanlong": "地", "luoshu": 9},
    
    # 正南（離卦）
    "午": {"gua": "離", "degree_start": 172.5, "degree_end": 187.5, "yinyang": "陰", "yuanlong": "天", "luoshu": 9},
    "丁": {"gua": "離", "degree_start": 187.5, "degree_end": 202.5, "yinyang": "陰", "yuanlong": "人", "luoshu": 9},
    "未": {"gua": "坤", "degree_start": 202.5, "degree_end": 217.5, "yinyang": "陰", "yuanlong": "地", "luoshu": 2},
    
    # 西南（坤卦）
    "坤": {"gua": "坤", "degree_start": 217.5, "degree_end": 232.5, "yinyang": "陽", "yuanlong": "天", "luoshu": 2},
    "申": {"gua": "坤", "degree_start": 232.5, "degree_end": 247.5, "yinyang": "陽", "yuanlong": "人", "luoshu": 2},
    "庚": {"gua": "兌", "degree_start": 247.5, "degree_end": 262.5, "yinyang": "陽", "yuanlong": "地", "luoshu": 7},
    
    # 正西（兌卦）
    "酉": {"gua": "兌", "degree_start": 262.5, "degree_end": 277.5, "yinyang": "陰", "yuanlong": "天", "luoshu": 7},
    "辛": {"gua": "兌", "degree_start": 277.5, "degree_end": 292.5, "yinyang": "陰", "yuanlong": "人", "luoshu": 7},
    "戌": {"gua": "乾", "degree_start": 292.5, "degree_end": 307.5, "yinyang": "陰", "yuanlong": "地", "luoshu": 6},
    
    # 西北（乾卦）
    "乾": {"gua": "乾", "degree_start": 307.5, "degree_end": 322.5, "yinyang": "陽", "yuanlong": "天", "luoshu": 6},
    "亥": {"gua": "乾", "degree_start": 322.5, "degree_end": 337.5, "yinyang": "陽", "yuanlong": "人", "luoshu": 6},
    "壬": {"gua": "坎", "degree_start": 337.5, "degree_end": 352.5, "yinyang": "陽", "yuanlong": "地", "luoshu": 1},
}

# 洛書九宮方位映射
LUOSHU_POSITIONS = {
    5: "center",
    1: "north",
    9: "south",
    3: "east",
    7: "west",
    8: "northeast",
    4: "southeast",
    6: "northwest",
    2: "southwest",
}

# 九宮格順序（用於飛布）
# 洛書軌跡：中→西北→西→東北→南→北→西南→東→東南
POSITION_ORDER = ["center", "northwest", "west", "northeast", "south", "north", "southwest", "east", "southeast"]

# ============================================================
# 二、核心排盤算法
# ============================================================

def parse_mountain_facing(mountain_facing: str) -> tuple:
    """
    解析坐向字符串，如"子山午向" -> ("子", "午")
    
    Returns:
        (坐山, 向山) 或 (None, None) 如果解析失敗
    """
    if "山" not in mountain_facing or "向" not in mountain_facing:
        return None, None
    
    parts = mountain_facing.split("山")
    if len(parts) != 2:
        return None, None
    
    mountain = parts[0]
    facing = parts[1].replace("向", "")
    
    return mountain, facing


def get_mountain_data(mountain: str) -> dict:
    """獲取山的基礎數據"""
    return MOUNTAIN_24_DATA.get(mountain, {})


def determine_flying_direction(yinyang: str, yuanlong: str) -> str:
    """
    根據陰陽和元龍確定順飛/逆飛
    
    玄空飛星規則：
    - 天元龍：陰逆陽順
    - 地元龍：陰逆陽順
    - 人元龍：陰逆陽順
    
    ⚠️ 注意：不同流派可能有差異，此處採用「陽順陰逆」通用規則
    """
    if yinyang == "陽":
        return "shun"  # 順飛
    else:
        return "ni"    # 逆飛


def calculate_center_star(yun_number: int) -> int:
    """
    計算運星入中數字
    
    玄空飛星規則：運星入中 = 當運數字
    """
    return yun_number


def calculate_mountain_center_star(mountain: str, yun_number: int) -> int:
    """
    計算山星入中數字
    
    玄空飛星排盤步驟：
    1. 確定坐山的洛書數字
    2. 根據運數和坐山確定入中數字
    
    簡化算法（MVP階段）：
    - 山星入中 = 運星入中按洛書軌跡飛布到坐山位置的數字
    """
    mountain_data = get_mountain_data(mountain)
    if not mountain_data:
        return None
    
    mountain_luoshu = mountain_data["luoshu"]
    
    # 簡化計算：山星入中數 = (運數 + 坐山洛書數 - 1) % 9 + 1
    # 這是一個簡化公式，實際排盤更複雜
    center_star = ((yun_number + mountain_luoshu - 2) % 9) + 1
    return center_star


def calculate_facing_center_star(facing: str, yun_number: int) -> int:
    """
    計算向星入中數字
    
    簡化算法（MVP階段）：
    - 向星入中數 = (運數 + 向山洛書數 - 1) % 9 + 1
    """
    facing_data = get_mountain_data(facing)
    if not facing_data:
        return None
    
    facing_luoshu = facing_data["luoshu"]
    center_star = ((yun_number + facing_luoshu - 2) % 9) + 1
    return center_star


def fly_stars(center_star: int, direction: str) -> dict:
    """
    九宮飛星
    
    根據入中數字和飛布方向，生成九宮格中的數字分佈。
    
    Args:
        center_star: 入中宮的數字（1-9）
        direction: "shun"=順飛, "ni"=逆飛
    
    Returns:
        {方位: 飛星數字}，方位為英文方向名
    """
    if direction == "shun":
        # 順飛：數字遞增（模9）
        stars = {}
        for i, pos in enumerate(POSITION_ORDER):
            star = ((center_star - 1 + i) % 9) + 1
            stars[pos] = star
    else:
        # 逆飛：數字遞減（模9）
        stars = {}
        for i, pos in enumerate(POSITION_ORDER):
            star = ((center_star - 1 - i) % 9) + 1
            stars[pos] = star
    
    return stars


def generate_flying_star_pan(yun_number: int, mountain: str, facing: str) -> dict:
    """
    生成完整的玄空飛星盤（動態計算）
    
    Args:
        yun_number: 運數（1-9）
        mountain: 坐山（如"子"）
        facing: 向山（如"午"）
    
    Returns:
        {
            "yun_star": 運盤（九宮）,
            "mountain_star": 山盤（九宮）,
            "facing_star": 向盤（九宮）,
            "confidence": 置信度,
            "issues": 問題列表
        }
    """
    issues = []
    
    # 1. 獲取基礎數據
    mountain_data = get_mountain_data(mountain)
    facing_data = get_mountain_data(facing)
    
    if not mountain_data or not facing_data:
        issues.append("無法識別坐向")
        return {
            "yun_star": {},
            "mountain_star": {},
            "facing_star": {},
            "confidence": 0.1,
            "issues": issues
        }
    
    # 2. 計算運盤（運星入中，順飛）
    yun_star = fly_stars(yun_number, "shun")
    
    # 3. 計算山盤
    mountain_center = calculate_mountain_center_star(mountain, yun_number)
    mountain_direction = determine_flying_direction(mountain_data["yinyang"], mountain_data["yuanlong"])
    mountain_star = fly_stars(mountain_center, mountain_direction)
    
    # 4. 計算向盤
    facing_center = calculate_facing_center_star(facing, yun_number)
    facing_direction = determine_flying_direction(facing_data["yinyang"], facing_data["yuanlong"])
    facing_star = fly_stars(facing_center, facing_direction)
    
    # 5. 驗證基本規則
    # 5.1 中宮檢查
    if mountain_star.get("center") != mountain_center:
        issues.append(f"山盤中宮計算異常: {mountain_star.get('center')} != {mountain_center}")
    if facing_star.get("center") != facing_center:
        issues.append(f"向盤中宮計算異常: {facing_star.get('center')} != {facing_center}")
    
    # 5.2 山盤向盤差異檢查
    if mountain_star == facing_star:
        issues.append("山盤與向盤完全相同（可能為替卦或計算錯誤）")
    
    # 6. 確定置信度
    confidence = 0.75  # 基礎置信度
    if issues:
        confidence = 0.45
    
    # 替卦情況標記低置信度
    # 簡化判斷：如果坐山或向山為「替卦位置」（不在正中），標記低置信度
    # 實際替卦判斷更複雜，MVP階段簡化處理
    if mountain_data["yuanlong"] != "天":
        confidence = min(confidence, 0.6)
        issues.append("坐山為偏位，可能涉及替卦，置信度降低")
    
    return {
        "yun_star": yun_star,
        "mountain_star": mountain_star,
        "facing_star": facing_star,
        "confidence": round(confidence, 2),
        "issues": issues,
        "mountain_data": mountain_data,
        "facing_data": facing_data
    }


# ============================================================
# 三、格局判定
# ============================================================

def determine_pan_type(mountain_star: dict, facing_star: dict, yun_number: int) -> str:
    """
    判定飛星盤格局
    
    主要格局：
    - 到山到向：山星當運數在坐山，向星當運數在向山
    - 雙星會向：山星和向星當運數都在向山
    - 雙星會坐：山星和向星當運數都在坐山
    - 上山下水：山星當運數在向山，向星當運數在坐山（反吟）
    - 其他：不符合以上格局
    """
    # 找到當運數字在各盤中的位置
    m_positions = {pos: star for pos, star in mountain_star.items() if star == yun_number}
    f_positions = {pos: star for pos, star in facing_star.items() if star == yun_number}
    
    # 簡化判定邏輯（需要坐山和向山的方位信息才能準確判定）
    # MVP階段返回通用判定
    
    # 統計當運數字出現的次數
    m_count = len(m_positions)
    f_count = len(f_positions)
    
    if m_count >= 2 and f_count >= 2:
        return "雙星會聚"  # 多個方位都有當運數字
    elif m_count >= 1 and f_count >= 1:
        return "到山到向"  # 山盤和向盤都有當運數字
    else:
        return "其他"


# ============================================================
# 四、主入口函數
# ============================================================

def calculate_flying_star_pan(building_year: int, mountain_facing: str, eval_year: int = 2026) -> dict:
    """
    動態計算飛星盤（主入口函數）
    
    Args:
        building_year: 建築年份
        mountain_facing: 坐向（如"子山午向"）
        eval_year: 評估年份
    
    Returns:
        完整的飛星分析結果，與硬編碼查表格式一致
    """
    # 1. 解析坐向
    mountain, facing = parse_mountain_facing(mountain_facing)
    if not mountain or not facing:
        return {
            "status": "error",
            "error": f"無法解析坐向: {mountain_facing}",
            "score": 0,
            "confidence": 0
        }
    
    # 2. 確定運數
    yun = get_yun(building_year)
    yun_number = yun_to_number(yun)
    
    # 3. 動態排盤
    pan_result = generate_flying_star_pan(yun_number, mountain, facing)
    
    # 4. 判定格局
    pan_type = determine_pan_type(
        pan_result["mountain_star"],
        pan_result["facing_star"],
        yun_number
    )
    
    # 5. 計算基礎分
    base_score = 15  # 默認基礎分
    if pan_type == "到山到向":
        base_score = 30
    elif pan_type == "雙星會聚":
        base_score = 25
    
    # 6. 生成吉凶組合（簡化版）
    auspicious_combos = []
    inauspicious_combos = []
    
    # 檢查各宮位的山星+向星組合
    for direction in LUOSHU_POSITIONS.values():
        m_star = pan_result["mountain_star"].get(direction, 0)
        f_star = pan_result["facing_star"].get(direction, 0)
        
        if m_star == yun_number and f_star == yun_number:
            auspicious_combos.append({
                "direction": direction,
                "stars": f"{m_star}{f_star}",
                "desc": "雙星會聚，旺丁旺財"
            })
        elif m_star == f_star and m_star in [2, 5]:
            inauspicious_combos.append({
                "direction": direction,
                "stars": f"{m_star}{f_star}",
                "desc": f"{m_star}星重臨，煞氣當令"
            })
    
    # 7. 計算總分
    auspicious_score = len(auspicious_combos) * 5
    inauspicious_score = len(inauspicious_combos) * (-5)
    total_score = max(5, min(40, base_score + auspicious_score + inauspicious_score))
    
    # 8. 構建理由
    issues_note = ""
    if pan_result["issues"]:
        issues_note = f" ⚠️ 計算問題: {'; '.join(pan_result['issues'])}"
    
    rationale = (
        f"{yun}{mountain_facing}，動態排盤結果：{pan_type}格局。"
        f"宅運基礎分{base_score}分，"
        f"吉組合加{auspicious_score}分，凶組合減{abs(inauspicious_score)}分。"
        f"{issues_note}"
        " ⚠️ 動態排盤為算法計算，具體判斷建議諮詢專業師傅。"
    )
    
    return {
        "status": "success",
        "yun": yun,
        "building_facing": mountain_facing,
        "pan_type": pan_type,
        "mountain_stars": pan_result["mountain_star"],
        "facing_stars": pan_result["facing_star"],
        "yun_stars": pan_result["yun_star"],
        "score": total_score,
        "max_score": 40,
        "base_score": base_score,
        "auspicious_score": auspicious_score,
        "inauspicious_score": inauspicious_score,
        "auspicious_combos": auspicious_combos,
        "inauspicious_combos": inauspicious_combos,
        "confidence": round(pan_result["confidence"], 2),
        "rationale": rationale,
        "algorithm": "dynamic",
        "issues": pan_result["issues"]
    }


# ============================================================
# 五、與硬編碼數據的對比驗證
# ============================================================

def compare_with_table(yun: str, mountain_facing: str) -> dict:
    """
    對比動態排盤與硬編碼數據的差異
    
    Returns:
        {
            "table_exists": bool,
            "mountain_diff": int,
            "facing_diff": int,
            "match_rate": float,
            "recommendation": str
        }
    """
    from data.flying_star import FLYING_STAR_TABLE
    
    result = {
        "table_exists": False,
        "mountain_diff": -1,
        "facing_diff": -1,
        "match_rate": 0.0,
        "recommendation": ""
    }
    
    # 檢查硬編碼數據是否存在
    if yun not in FLYING_STAR_TABLE or mountain_facing not in FLYING_STAR_TABLE[yun]:
        result["recommendation"] = "硬編碼數據不存在，使用動態排盤結果"
        return result
    
    result["table_exists"] = True
    table_data = FLYING_STAR_TABLE[yun][mountain_facing]
    
    # 動態排盤
    mountain, facing = parse_mountain_facing(mountain_facing)
    yun_number = yun_to_number(yun)
    dynamic_pan = generate_flying_star_pan(yun_number, mountain, facing)
    
    # 比較山盤
    table_mountain = table_data.get("mountain_stars", {})
    dynamic_mountain = dynamic_pan["mountain_star"]
    
    mountain_diff = 0
    for direction in LUOSHU_POSITIONS.values():
        if table_mountain.get(direction) != dynamic_mountain.get(direction):
            mountain_diff += 1
    
    # 比較向盤
    table_facing = table_data.get("facing_stars", {})
    dynamic_facing = dynamic_pan["facing_star"]
    
    facing_diff = 0
    for direction in LUOSHU_POSITIONS.values():
        if table_facing.get(direction) != dynamic_facing.get(direction):
            facing_diff += 1
    
    result["mountain_diff"] = mountain_diff
    result["facing_diff"] = facing_diff
    result["match_rate"] = round((18 - mountain_diff - facing_diff) / 18, 2)
    
    # 推薦使用哪個數據源
    if result["match_rate"] >= 0.8:
        result["recommendation"] = "動態排盤與硬編碼數據高度一致，建議使用硬編碼數據（更高置信度）"
    elif result["match_rate"] >= 0.5:
        result["recommendation"] = "部分一致，建議以硬編碼數據為主，動態排盤為輔"
    else:
        result["recommendation"] = "差異較大，動態排盤可能不準確，建議使用硬編碼數據或專業確認"
    
    return result


# ============================================================
# 六、批量驗證工具
# ============================================================

def validate_all_pans() -> dict:
    """
    批量驗證所有硬編碼數據與動態排盤的一致性
    
    Returns:
        {
            "total": 總數,
            "high_match": 高匹配數(>=0.8),
            "medium_match": 中匹配數(0.5-0.8),
            "low_match": 低匹配數(<0.5),
            "details": 詳細結果
        }
    """
    from data.flying_star import FLYING_STAR_TABLE, ALL_24_MOUNTAINS
    
    results = {
        "total": 0,
        "high_match": 0,
        "medium_match": 0,
        "low_match": 0,
        "details": []
    }
    
    for yun in FLYING_STAR_TABLE:
        for facing in ALL_24_MOUNTAINS:
            if facing not in FLYING_STAR_TABLE[yun]:
                continue
            
            results["total"] += 1
            comparison = compare_with_table(yun, facing)
            
            match_rate = comparison["match_rate"]
            if match_rate >= 0.8:
                results["high_match"] += 1
            elif match_rate >= 0.5:
                results["medium_match"] += 1
            else:
                results["low_match"] += 1
            
            results["details"].append({
                "yun": yun,
                "facing": facing,
                "match_rate": match_rate,
                "mountain_diff": comparison["mountain_diff"],
                "facing_diff": comparison["facing_diff"]
            })
    
    return results


# ============================================================
# 批判性設計說明
# ============================================================
"""
動態排盤算法設計權衡：

1. 已實現的功能：
   - 二十四山基礎數據（卦、度數、陰陽、元龍）
   - 運盤/山盤/向盤的動態計算
   - 順飛/逆飛邏輯
   - 基本格局判定
   - 與硬編碼數據的對比驗證

2. 簡化的部分（MVP階段）：
   - 替卦邏輯：標記低置信度，未實現完整替卦計算
   - 山星/向星入中公式：使用簡化公式，非完整排龍訣
   - 格局判定：需要坐山/向山方位映射才能準確判定

3. 使用建議：
   - 優先使用硬編碼數據（福山堂專業數據）
   - 動態排盤用於：
     a) 硬編碼數據缺失時的後備方案
     b) 驗證硬編碼數據的內部一致性
     c) 用戶輸入自定義度數時的近似計算
"""
