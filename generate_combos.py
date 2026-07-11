# -*- coding: utf-8 -*-
"""
自動生成飛星組合（auspicious/inauspicious combos）
基於山盤和向盤的數字組合
"""
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from data.flying_star import FLYING_STAR_TABLE, FLYING_STAR_COMBO_AUSPICIOUS, FLYING_STAR_COMBO_INAUSPICIOUS

# 方位名稱映射
DIRECTION_NAMES = {
    "north": "正北", "northeast": "東北", "east": "正東", "southeast": "東南",
    "south": "正南", "southwest": "西南", "west": "正西", "northwest": "西北",
    "center": "中宮"
}

# 運星數字
YUN_STAR_NUM = {
    "七運": 7, "八運": 8, "九運": 9
}

def generate_combos_for_pan(mountain_stars, facing_stars, yun_star):
    """為一個飛星盤生成 auspicious 和 inauspicious 組合"""
    auspicious = []
    inauspicious = []
    
    for direction in ["north", "northeast", "east", "southeast", 
                      "south", "southwest", "west", "northwest", "center"]:
        m = mountain_stars.get(direction)
        f = facing_stars.get(direction)
        if m is None or f is None:
            continue
        
        # 山星+向星組合
        combo = f"{m}{f}"
        
        # 檢查吉凶組合
        if combo in FLYING_STAR_COMBO_AUSPICIOUS:
            auspicious.append({
                "direction": direction,
                "stars": combo,
                "desc": FLYING_STAR_COMBO_AUSPICIOUS[combo]
            })
        elif combo in FLYING_STAR_COMBO_INAUSPICIOUS:
            inauspicious.append({
                "direction": direction,
                "stars": combo,
                "desc": FLYING_STAR_COMBO_INAUSPICIOUS[combo]
            })
        
        # 檢查反向組合（如 68 vs 86）
        combo_rev = f"{f}{m}"
        if combo_rev in FLYING_STAR_COMBO_AUSPICIOUS and combo_rev != combo:
            auspicious.append({
                "direction": direction,
                "stars": combo_rev,
                "desc": FLYING_STAR_COMBO_AUSPICIOUS[combo_rev]
            })
        elif combo_rev in FLYING_STAR_COMBO_INAUSPICIOUS and combo_rev != combo:
            inauspicious.append({
                "direction": direction,
                "stars": combo_rev,
                "desc": FLYING_STAR_COMBO_INAUSPICIOUS[combo_rev]
            })
        
        # 檢查運星+山星/向星組合（運星在當運時為吉）
        yun_str = str(yun_star)
        
        # 運星+山星
        combo_yun_m = f"{yun_str}{m}"
        if combo_yun_m in FLYING_STAR_COMBO_AUSPICIOUS:
            auspicious.append({
                "direction": direction,
                "stars": combo_yun_m,
                "desc": f"運星+山星: {FLYING_STAR_COMBO_AUSPICIOUS[combo_yun_m]}"
            })
        
        # 運星+向星
        combo_yun_f = f"{yun_str}{f}"
        if combo_yun_f in FLYING_STAR_COMBO_AUSPICIOUS:
            auspicious.append({
                "direction": direction,
                "stars": combo_yun_f,
                "desc": f"運星+向星: {FLYING_STAR_COMBO_AUSPICIOUS[combo_yun_f]}"
            })
    
    # 去重
    seen = set()
    unique_auspicious = []
    for item in auspicious:
        key = (item["direction"], item["stars"])
        if key not in seen:
            seen.add(key)
            unique_auspicious.append(item)
    
    seen = set()
    unique_inauspicious = []
    for item in inauspicious:
        key = (item["direction"], item["stars"])
        if key not in seen:
            seen.add(key)
            unique_inauspicious.append(item)
    
    return unique_auspicious, unique_inauspicious


# 為所有飛星盤生成組合
print("=== 自動生成飛星組合 ===")
total_auspicious = 0
total_inauspicious = 0

for yun, mountains in FLYING_STAR_TABLE.items():
    yun_star = YUN_STAR_NUM.get(yun, 8)
    for mountain, data in mountains.items():
        m_stars = data.get("mountain_stars", {})
        f_stars = data.get("facing_stars", {})
        
        a, i = generate_combos_for_pan(m_stars, f_stars, yun_star)
        
        # 更新數據
        data["auspicious_combos"] = a
        data["inauspicious_combos"] = i
        
        total_auspicious += len(a)
        total_inauspicious += len(i)
        
        if a or i:
            print(f"{yun} {mountain}: {len(a)}吉 {len(i)}凶")

print(f"\n總計: {total_auspicious} 個吉組合, {total_inauspicious} 個凶組合")
