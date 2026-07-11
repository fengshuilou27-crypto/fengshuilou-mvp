# 玄空飛星簡化算法工具 (v3.3)
# 用於驗證硬編碼數據的內部一致性，非完整排盤算法

# ============================================================
# 洛書九宮方位映射
# ============================================================
# 洛書九宮數字與方位對應：
#   4(東南)  9(南)  2(西南)
#   3(東)    5(中)  7(西)
#   8(東北)  1(北)  6(西北)

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

# 方位→數字反向映射
POSITION_TO_NUMBER = {v: k for k, v in LUOSHU_POSITIONS.items()}

# 順飛軌跡：按洛書數字順序（5→6→7→8→9→1→2→3→4→5）
SHUNFEI_ORDER = [5, 6, 7, 8, 9, 1, 2, 3, 4]

# 逆飛軌跡：按洛書數字逆序（5→4→3→2→1→9→8→7→6→5）
NIFEI_ORDER = [5, 4, 3, 2, 1, 9, 8, 7, 6]


def generate_flying_numbers(start_number: int, direction: str = "shun") -> dict:
    """
    生成九宮飛星數字（簡化版）
    
    根據入中數字和飛布方向，生成九宮格中的數字分佈。
    
    Args:
        start_number: 入中宮的數字（1-9）
        direction: "shun"=順飛, "ni"=逆飛
    
    Returns:
        {方位: 飛星數字}，方位為英文方向名
    
    Example:
        >>> generate_flying_numbers(8, "shun")
        {'center': 8, 'northwest': 9, 'west': 1, 'northeast': 2, 
         'south': 3, 'north': 4, 'southwest': 5, 'east': 6, 'southeast': 7}
    """
    if direction == "shun":
        order = SHUNFEI_ORDER
    else:
        order = NIFEI_ORDER
    
    result = {}
    for i, pos_num in enumerate(order):
        # 入中數字依次 +1（順飛）或 -1（逆飛），循環 1-9
        if direction == "shun":
            star_num = ((start_number - 1 + i) % 9) + 1
        else:
            star_num = ((start_number - 1 - i) % 9) + 1
        
        position = LUOSHU_POSITIONS[pos_num]
        result[position] = star_num
    
    return result


def verify_center_star(yun_number: int, mountain_stars: dict) -> bool:
    """
    驗證中宮數字是否等於運星
    
    玄空飛星基本規則：中宮數字 = 當運數字
    """
    center = mountain_stars.get("center")
    return center == yun_number


def count_differences(stars_a: dict, stars_b: dict) -> int:
    """
    計算兩個星盤的差異數量
    
    Args:
        stars_a: 第一個星盤 {方位: 數字}
        stars_b: 第二個星盤 {方位: 數字}
    
    Returns:
        差異的方位數量
    """
    differences = 0
    for direction in LUOSHU_POSITIONS.values():
        if stars_a.get(direction) != stars_b.get(direction):
            differences += 1
    return differences


def generate_expected_pan(yun_number: int, start_number: int, direction: str) -> dict:
    """
    生成預期的飛星盤（簡化驗證用）
    
    此函數用於驗證硬編碼數據的合理性，不替代完整排盤算法。
    
    Args:
        yun_number: 運星數字（1-9）
        start_number: 入中數字（1-9）
        direction: "shun"=順飛, "ni"=逆飛
    
    Returns:
        預期的飛星盤 {方位: 數字}
    """
    return generate_flying_numbers(start_number, direction)


def quick_verify_pan(mountain_stars: dict, facing_stars: dict, yun_number: int) -> dict:
    """
    快速驗證飛星盤的基本合理性
    
    Returns:
        {
            "center_ok": bool,       # 中宮是否等於運星
            "has_differences": bool, # 山盤向盤是否不同
            "diff_count": int,       # 差異方位數
            "has_all_directions": bool, # 是否包含全部9個方位
            "issues": list[str]      # 發現的問題
        }
    """
    issues = []
    
    # 1. 檢查中宮
    center_ok = verify_center_star(yun_number, mountain_stars)
    if not center_ok:
        issues.append(f"中宮{mountain_stars.get('center')} != 運星{yun_number}")
    
    # 2. 檢查山盤向盤差異
    diff_count = count_differences(mountain_stars, facing_stars)
    has_differences = diff_count > 0
    if not has_differences:
        issues.append("山盤與向盤完全相同（理論上應有差異）")
    
    # 3. 檢查是否包含全部方位
    required_dirs = set(LUOSHU_POSITIONS.values())
    m_dirs = set(mountain_stars.keys())
    f_dirs = set(facing_stars.keys())
    has_all_directions = required_dirs.issubset(m_dirs) and required_dirs.issubset(f_dirs)
    if not has_all_directions:
        issues.append("缺少部分方位數據")
    
    return {
        "center_ok": center_ok,
        "has_differences": has_differences,
        "diff_count": diff_count,
        "has_all_directions": has_all_directions,
        "issues": issues
    }


# ============================================================
# 批判性設計說明
# ============================================================
"""
為何不實現完整的動態排盤算法？

1. 完整排盤需要：二十四山陰陽屬性、運星入中規則、山向星確定、順逆飛判斷
2. 任何一項錯誤會導致整個排盤錯誤，風險高於收益
3. 硬編碼數據 + 驗證函數 + 低置信度標記，是MVP更務實的方案
4. 本模組僅用於：
   - 驗證中宮數字是否正確
   - 檢查山盤向盤是否有差異
   - 生成簡化的預期排盤進行對比

完整動態排盤的未來路線：
- 需專業風水師確認二十四山陰陽表
- 需實現「運星入中→山星入中→向星入中」的完整鏈路
- 建議在 v4.0+ 由專業人員指導下實現
"""
