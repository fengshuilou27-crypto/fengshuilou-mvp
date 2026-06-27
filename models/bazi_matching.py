from data.bazi import (
    GAN_WUXING, FLOOR_WUXING, WUXING_RELATIONS, ZHI_WUXING,
    calculate_bazi, get_year_ganzhi, CAREER_WUXING
)




def _judge_day_master_strength(bazi_result: dict) -> dict:
    """
    簡化版日主強弱判斷（MVP標註用）
    判斷依據：得令（月令是否同五行）、通根（其他柱是否有同五行）、生扶（是否有印星比劫）
    """
    day_master = bazi_result.get("day_master", {})
    dm_wuxing = day_master.get("wuxing", "未知")
    month_zhi = bazi_result.get("month_pillar", {}).get("zhi", "")
    month_zhi_wuxing = ZHI_WUXING.get(month_zhi, "未知")
    
    # 得令：月令五行與日主相同或相生
    season_score = 0
    if month_zhi_wuxing == dm_wuxing:
        season_score = 2  # 得令（比劫月）
    elif WUXING_RELATIONS["生"].get(month_zhi_wuxing) == dm_wuxing:
        season_score = 1  # 得令（印星月）
    
    # 通根：其他柱天干是否有同五行
    root_score = 0
    for pillar in ["year_pillar", "month_pillar", "hour_pillar"]:
        gan = bazi_result.get(pillar, {}).get("gan", "")
        if GAN_WUXING.get(gan) == dm_wuxing:
            root_score += 1
    
    # 生扶：其他柱是否有印星（生我的五行）
    support_score = 0
    for pillar in ["year_pillar", "month_pillar", "hour_pillar"]:
        zhi = bazi_result.get(pillar, {}).get("zhi", "")
        if WUXING_RELATIONS["生"].get(ZHI_WUXING.get(zhi)) == dm_wuxing:
            support_score += 1
    
    total_score = season_score + root_score + support_score
    
    if total_score >= 4:
        strength = "強"
        advice = f"日主{dm_wuxing}強旺，喜用神為克洩（金/水/土，視具體五行而定）。此樓盤匹配以「克洩」五行為優先。"
    elif total_score >= 2:
        strength = "中和"
        advice = f"日主{dm_wuxing}中和，五行較平衡，樓盤匹配以「調候」為優先。"
    else:
        strength = "弱"
        advice = f"日主{dm_wuxing}偏弱，喜用神為生扶（木/火/土，視具體五行而定）。此樓盤匹配以「生扶」五行為優先。"
    
    return {
        "strength": strength,
        "score": total_score,
        "season_score": season_score,
        "root_score": root_score,
        "support_score": support_score,
        "advice": advice,
        "note": "【MVP簡化版】日主強弱判斷僅考慮月令、通根、生扶三項，未考慮合化/沖克/空亡等複雜因素。具體判斷建議諮詢專業風水師。"
    }

def analyze_bazi(birth_date: str, floor_number: int, birth_time: str = None, user_job: str = None):
    """
    八字匹配模組（完整四柱版 + 職業五行加成）
    使用年、月、日、時四柱完整八字，以日主（日柱天干）為命主五行，再與樓層五行匹配
    職業五行與日主五行相生/相同時加分（+2），相克時減分（-1）
    """
    # 解析出生日期
    try:
        year = int(birth_date.split("-")[0])
    except (ValueError, IndexError):
        return {
            "status": "error",
            "score": 0,
            "max_score": 20,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.3,
            "rationale": "出生日期格式错误，无法解析年份。"
        }
    
    # 計算完整四柱八字
    bazi_result = calculate_bazi(birth_date, birth_time)
    
    if not bazi_result:
        return {
            "status": "error",
            "score": 0,
            "max_score": 20,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.3,
            "rationale": "八字计算失败，无法解析日期。"
        }
    
    # 獲取日主（日柱天干）五行
    day_master_gan = bazi_result["day_master"]["gan"]
    day_master_wuxing = bazi_result["day_master"]["wuxing"]
    
    # 樓層五行
    floor_suffix = str(floor_number)[-1]
    floor_wuxing = FLOOR_WUXING.get(floor_suffix, "未知")
    
    # 匹配判斷
    score = 0
    relation = "未知"
    
    if day_master_wuxing != "未知" and floor_wuxing != "未知":
        if WUXING_RELATIONS["生"].get(floor_wuxing) == day_master_wuxing:
            # 樓層五行生我（生扶）→ 大吉
            score = 20
            relation = "生扶"
        elif WUXING_RELATIONS["生"].get(day_master_wuxing) == floor_wuxing:
            # 我生樓層（洩氣）→ 中平
            score = 10
            relation = "洩氣"
        elif WUXING_RELATIONS["克"].get(floor_wuxing) == day_master_wuxing:
            # 樓層五行克我（克制）→ 大凶
            score = 4
            relation = "克制"
        elif WUXING_RELATIONS["克"].get(day_master_wuxing) == floor_wuxing:
            # 我克樓層（耗財）→ 中吉
            score = 14
            relation = "耗財"
        elif day_master_wuxing == floor_wuxing:
            # 同五行（比劫）→ 中吉
            score = 16
            relation = "比劫"
    
    score = min(20, score)
    
    # 職業五行加成
    career_bonus = 0
    career_wuxing = None
    career_relation = None
    if user_job and user_job in CAREER_WUXING:
        career_wuxing = CAREER_WUXING[user_job]
        if WUXING_RELATIONS["生"].get(career_wuxing) == day_master_wuxing or career_wuxing == day_master_wuxing:
            # 職業五行生我或同我 → 加分
            career_bonus = 2
            career_relation = "相生/比劫"
        elif WUXING_RELATIONS["克"].get(career_wuxing) == day_master_wuxing:
            # 職業五行克我 → 減分
            career_bonus = -1
            career_relation = "相克"
        else:
            career_relation = "無明顯生克"
    
    final_score = max(0, min(20, score + career_bonus))
    
    # 四柱信息
    pillars = bazi_result
    
    career_rationale = ""
    if career_wuxing:
        career_rationale = f" 職業'{user_job}'屬{career_wuxing}，與日主{day_master_wuxing}關係為「{career_relation}」，職業加成{career_bonus:+d}分。"
    
    strength_analysis = _judge_day_master_strength(pillars)
    
    return {
        "status": "success",
        "day_master_gan": day_master_gan,
        "day_master_wuxing": day_master_wuxing,
        "floor_number": floor_number,
        "floor_wuxing": floor_wuxing,
        "relation": relation,
        "score": final_score,
        "base_score": score,
        "career_bonus": career_bonus,
        "max_score": 20,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.65,
        "bazi_full": {
            "year_pillar": f"{pillars['year_pillar']['gan']}{pillars['year_pillar']['zhi']}",
            "month_pillar": f"{pillars['month_pillar']['gan']}{pillars['month_pillar']['zhi']}",
            "day_pillar": f"{pillars['day_pillar']['gan']}{pillars['day_pillar']['zhi']}",
            "hour_pillar": f"{pillars['hour_pillar']['gan']}{pillars['hour_pillar']['zhi']}",
            "day_master": f"{day_master_gan}（{day_master_wuxing}）"
        },
        "strength_analysis": strength_analysis,
        "rationale": f"八字四柱：{pillars['year_pillar']['gan']}{pillars['year_pillar']['zhi']}年 "
                     f"{pillars['month_pillar']['gan']}{pillars['month_pillar']['zhi']}月 "
                     f"{pillars['day_pillar']['gan']}{pillars['day_pillar']['zhi']}日 "
                     f"{pillars['hour_pillar']['gan']}{pillars['hour_pillar']['zhi']}時。"
                     f"日主為{day_master_gan}（{day_master_wuxing}），日主強弱：{strength_analysis['strength']}（評分{strength_analysis['score']}/6）。"
                     f"樓層{floor_number}屬{floor_wuxing}，兩者關係為「{relation}」，基礎得分{score}分。{career_rationale}"
                     f"最終八字得分{final_score}分。"
                     f" {strength_analysis['advice']}"
                     " ⚠️ 基於公開資料計算，僅供參考，具體判斷建議諮詢專業師傅。"
    }
