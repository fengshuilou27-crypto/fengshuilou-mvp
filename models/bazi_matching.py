from data.bazi import (
    GAN_WUXING, FLOOR_WUXING, WUXING_RELATIONS,
    calculate_bazi, get_year_ganzhi, CAREER_WUXING
)


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
        "rationale": f"八字四柱：{pillars['year_pillar']['gan']}{pillars['year_pillar']['zhi']}年 "
                     f"{pillars['month_pillar']['gan']}{pillars['month_pillar']['zhi']}月 "
                     f"{pillars['day_pillar']['gan']}{pillars['day_pillar']['zhi']}日 "
                     f"{pillars['hour_pillar']['gan']}{pillars['hour_pillar']['zhi']}時。"
                     f"日主為{day_master_gan}（{day_master_wuxing}），樓層{floor_number}屬{floor_wuxing}，"
                     f"兩者關係為「{relation}」，基礎得分{score}分。{career_rationale}"
                     f"最終八字得分{final_score}分。"
                     " 基於公開資料計算，僅供參考，具體判斷建議諮詢專業師傅。"
    }
