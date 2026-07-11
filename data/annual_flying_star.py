# 年度飛星（流年飛星）計算模組 (v3.5)
# 基於玄空飛星理論計算每年流年飛星盤，並與宅運盤疊加分析

from data.flying_star_dynamic import fly_stars, LUOSHU_POSITIONS, POSITION_ORDER
from data.flying_star_dynamic import yun_to_number

# ============================================================
# 一、流年飛星基礎數據
# ============================================================

# 流年飛星入中數對照表（基準年2000年入中=2）
# 公式：入中數 = (2 + (year - 2000)) % 9，但需要注意0變9
# 陽年順飛，陰年順飛（流年飛星統一順飛）

def calculate_annual_center_star(year: int) -> int:
    """
    計算流年飛星入中數
    
    基準：2000年（庚辰）入中 = 2
    規則：每年順序遞增，模9循環
    """
    diff = year - 2000
    center = ((2 - 1 + diff) % 9) + 1
    return center


# 年干支對照（簡化版，覆蓋1900-2100）
# 用於更精確的流年飛星計算
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def get_year_ganzhi(year: int) -> tuple:
    """
    獲取年干支
    
    Returns: (天干, 地支)
    """
    # 1984年為甲子年
    offset = year - 1984
    tiangan = TIANGAN[offset % 10]
    dizhi = DIZHI[offset % 12]
    return tiangan, dizhi


# 天干陰陽
TIANGAN_YINYANG = {
    "甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
    "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"
}


# ============================================================
# 二、流年飛星盤計算
# ============================================================

def generate_annual_flying_star(year: int) -> dict:
    """
    生成流年飛星盤
    
    流年飛星統一順飛（無論陰年陽年）
    
    Returns:
        {
            "year": 年份,
            "ganzhi": 干支,
            "center_star": 入中數,
            "stars": {方位: 飛星數字}
        }
    """
    center_star = calculate_annual_center_star(year)
    ganzhi = get_year_ganzhi(year)
    
    # 流年飛星統一順飛
    stars = fly_stars(center_star, "shun")
    
    return {
        "year": year,
        "ganzhi": f"{ganzhi[0]}{ganzhi[1]}",
        "tiangan_yinyang": TIANGAN_YINYANG.get(ganzhi[0], "陽"),
        "center_star": center_star,
        "stars": stars
    }


# ============================================================
# 三、流年飛星與宅運盤疊加分析
# ============================================================

# 流年飛星與宅運盤組合的吉凶判定
ANNUAL_COMBO_MEANING = {
    # 當運星 + 當運星 = 旺上加旺
    (1, 1): {"level": "大旺", "desc": "一白重臨，官運文思皆旺"},
    (4, 4): {"level": "大旺", "desc": "四綠重臨，文昌大旺"},
    (6, 6): {"level": "大旺", "desc": "六白重臨，偏財大旺"},
    (8, 8): {"level": "大旺", "desc": "八白重臨，財源廣進"},
    (9, 9): {"level": "大旺", "desc": "九紫重臨，喜慶盈門"},
    
    # 吉星組合
    (1, 4): {"level": "中吉", "desc": "一四同宮，科甲聯登"},
    (4, 1): {"level": "中吉", "desc": "四一同宮，官運文思"},
    (1, 6): {"level": "中吉", "desc": "一六同宮，官運亨通"},
    (6, 1): {"level": "中吉", "desc": "六一同宮，偏財官運"},
    (6, 8): {"level": "中吉", "desc": "六八同宮，財丁兩旺"},
    (8, 6): {"level": "中吉", "desc": "八六同宮，貴人扶持"},
    (8, 9): {"level": "中吉", "desc": "八九同宮，喜慶生財"},
    (9, 8): {"level": "中吉", "desc": "九八同宮，喜事臨門"},
    
    # 凶煞組合
    (2, 5): {"level": "大凶", "desc": "二五交加，病符災禍"},
    (5, 2): {"level": "大凶", "desc": "五二同宮，災禍病符"},
    (2, 3): {"level": "凶", "desc": "二三鬥牛，爭鬥是非"},
    (3, 2): {"level": "凶", "desc": "三二鬥牛，官非口舌"},
    (3, 5): {"level": "凶", "desc": "三五鬥牛，災禍損財"},
    (5, 3): {"level": "凶", "desc": "五三煞氣，災禍連連"},
    (5, 7): {"level": "凶", "desc": "五七同宮，破財傷丁"},
    (7, 5): {"level": "凶", "desc": "七五同宮，損財災禍"},
    (5, 9): {"level": "凶", "desc": "五九同宮，災禍連連"},
    (9, 5): {"level": "凶", "desc": "九五同宮，災禍損丁"},
    
    # 中性組合（一般影響）
    (1, 2): {"level": "平", "desc": "一二同宮，官運平平"},
    (2, 1): {"level": "平", "desc": "二一同宮，病符平平"},
    (1, 3): {"level": "平", "desc": "一三同宮，文思受阻"},
    (3, 1): {"level": "平", "desc": "三一同宮，是非平平"},
    (1, 8): {"level": "中吉", "desc": "一八同宮，財運平順"},
    (8, 1): {"level": "中吉", "desc": "八一同宮，財源穩定"},
    (4, 6): {"level": "中吉", "desc": "四六同宮，文財兩旺"},
    (6, 4): {"level": "中吉", "desc": "六四同宮，偏財文思"},
    (7, 9): {"level": "平", "desc": "七九同宮，破財平平"},
    (9, 7): {"level": "平", "desc": "九七同宮，喜事平平"},
}


def analyze_annual_overlay(mountain_stars: dict, facing_stars: dict, annual_stars: dict, yun_number: int) -> dict:
    """
    分析流年飛星與宅運盤的疊加效應
    
    Args:
        mountain_stars: 宅運山盤 {方位: 數字}
        facing_stars: 宅運向盤 {方位: 數字}
        annual_stars: 流年飛星盤 {方位: 數字}
        yun_number: 當運數字（1-9）
    
    Returns:
        {
            "annual_effects": [
                {
                    "direction": 方位,
                    "mountain_star": 山星,
                    "facing_star": 向星,
                    "annual_star": 流年星,
                    "combo": 山星+流年星組合,
                    "level": 吉凶等級,
                    "desc": 描述
                }
            ],
            "summary": {
                "most_auspicious": 最吉方位,
                "most_inauspicious": 最凶方位,
                "annual_advice": 年度建議
            }
        }
    """
    annual_effects = []
    
    auspicious_count = 0
    inauspicious_count = 0
    
    most_auspicious = None
    most_inauspicious = None
    max_auspicious_score = -999
    max_inauspicious_score = 999
    
    for direction in LUOSHU_POSITIONS.values():
        m_star = mountain_stars.get(direction, 0)
        f_star = facing_stars.get(direction, 0)
        a_star = annual_stars.get(direction, 0)
        
        # 分析山星與流年星的組合
        combo_key = (m_star, a_star)
        combo_info = ANNUAL_COMBO_MEANING.get(combo_key, {"level": "平", "desc": "一般影響"})
        
        # 計算分數
        score = 0
        if combo_info["level"] == "大旺":
            score = 5
            auspicious_count += 1
        elif combo_info["level"] == "中吉":
            score = 3
            auspicious_count += 1
        elif combo_info["level"] == "大凶":
            score = -5
            inauspicious_count += 1
        elif combo_info["level"] == "凶":
            score = -3
            inauspicious_count += 1
        
        # 當運星加強效應
        if a_star == yun_number:
            score *= 2
            combo_info = dict(combo_info)
            combo_info["desc"] = f"流年當運星加強: {combo_info['desc']}"
        
        effect = {
            "direction": direction,
            "mountain_star": m_star,
            "facing_star": f_star,
            "annual_star": a_star,
            "combo": f"{m_star}{a_star}",
            "level": combo_info["level"],
            "desc": combo_info["desc"],
            "score": score
        }
        
        annual_effects.append(effect)
        
        # 追蹤最吉/最凶
        if score > max_auspicious_score:
            max_auspicious_score = score
            most_auspicious = effect
        
        if score < max_inauspicious_score:
            max_inauspicious_score = score
            most_inauspicious = effect
    
    # 生成年度建議
    advice = []
    if most_auspicious and max_auspicious_score > 0:
        advice.append(
            f"最吉方位在{most_auspicious['direction']}（{most_auspicious['desc']}），"
            f"宜在此方位活動或佈置旺氣物品。"
        )
    
    if most_inauspicious and max_inauspicious_score < 0:
        advice.append(
            f"最凶方位在{most_inauspicious['direction']}（{most_inauspicious['desc']}），"
            f"宜避免在此方位動土或長時間停留。"
        )
    
    if inauspicious_count > 3:
        advice.append(f"本年有{inauspicious_count}個方位出現凶煞組合，建議整體佈局化煞。")
    
    if auspicious_count > 3:
        advice.append(f"本年有{auspicious_count}個方位出現吉慶組合，整體運勢較佳。")
    
    return {
        "annual_effects": annual_effects,
        "summary": {
            "auspicious_count": auspicious_count,
            "inauspicious_count": inauspicious_count,
            "most_auspicious": most_auspicious,
            "most_inauspicious": most_inauspicious,
            "annual_advice": advice
        }
    }


# ============================================================
# 四、主入口函數
# ============================================================

def calculate_annual_flying_star(building_year: int, building_facing: str, target_year: int = 2026) -> dict:
    """
    計算指定年份的流年飛星疊加分析
    
    Args:
        building_year: 建築年份
        building_facing: 坐向（如"子山午向"）
        target_year: 目標年份（默認2026年）
    
    Returns:
        完整的流年飛星疊加分析結果
    """
    from models.flying_star_analysis import analyze_flying_star
    
    # 1. 獲取宅運盤
    house_chart = analyze_flying_star(building_year, building_facing, target_year)
    
    if house_chart.get("status") != "success":
        return {
            "status": "error",
            "error": f"宅運盤查詢失敗: {house_chart.get('error', 'unknown')}",
            "target_year": target_year
        }
    
    # 2. 生成流年飛星盤
    annual_pan = generate_annual_flying_star(target_year)
    
    # 3. 獲取當運數字
    yun = house_chart.get("yun", "八運")
    yun_number = yun_to_number(yun) if "運" in yun else 8
    
    # 4. 疊加分析
    mountain_stars = house_chart.get("mountain_stars", {})
    facing_stars = house_chart.get("facing_stars", {})
    
    overlay = analyze_annual_overlay(
        mountain_stars, facing_stars, annual_pan["stars"], yun_number
    )
    
    # 5. 計算年度調整分
    annual_adjustment = 0
    for effect in overlay["annual_effects"]:
        annual_adjustment += effect.get("score", 0)
    
    # 限制調整幅度
    annual_adjustment = max(-10, min(10, annual_adjustment))
    
    # 6. 構建結果
    base_score = house_chart.get("score", 20)
    adjusted_score = max(5, min(40, base_score + annual_adjustment))
    
    return {
        "status": "success",
        "target_year": target_year,
        "year_ganzhi": annual_pan["ganzhi"],
        "yun": yun,
        "building_facing": building_facing,
        "house_chart": {
            "score": base_score,
            "pan_type": house_chart.get("pan_type", "未知"),
            "confidence": house_chart.get("confidence", 0.55)
        },
        "annual_pan": {
            "center_star": annual_pan["center_star"],
            "stars": annual_pan["stars"]
        },
        "overlay_analysis": overlay,
        "annual_adjustment": annual_adjustment,
        "adjusted_score": adjusted_score,
        "rationale": (
            f"{target_year}年（{annual_pan['ganzhi']}）流年飛星分析。"
            f"宅運基礎分{base_score}分，年度調整{annual_adjustment}分，"
            f"調整後{adjusted_score}分。"
            f"{overlay['summary']['annual_advice'][0] if overlay['summary']['annual_advice'] else ''}"
        )
    }


# ============================================================
# 五、批量年度分析
# ============================================================

def calculate_multi_year_analysis(building_year: int, building_facing: str, start_year: int = 2024, end_year: int = 2030) -> list:
    """
    計算多年度的流年飛星分析
    
    Returns:
        每年的分析結果列表
    """
    results = []
    for year in range(start_year, end_year + 1):
        result = calculate_annual_flying_star(building_year, building_facing, year)
        results.append(result)
    
    return results


# ============================================================
# 六、測試與驗證
# ============================================================
if __name__ == "__main__":
    # 測試2026年流年飛星
    print("=== 2026年流年飛星盤 ===")
    annual = generate_annual_flying_star(2026)
    print(f"年份: {annual['year']}")
    print(f"干支: {annual['ganzhi']}")
    print(f"入中數: {annual['center_star']}")
    print(f"飛星盤: {annual['stars']}")
    
    # 測試疊加分析
    print("\n=== 2026年疊加分析 (八運子山午向) ===")
    result = calculate_annual_flying_star(2004, "子山午向", 2026)
    print(f"狀態: {result['status']}")
    print(f"年度調整: {result['annual_adjustment']}")
    print(f"調整後分數: {result['adjusted_score']}")
    print(f"最吉方位: {result['overlay_analysis']['summary']['most_auspicious']}")
    print(f"最凶方位: {result['overlay_analysis']['summary']['most_inauspicious']}")
