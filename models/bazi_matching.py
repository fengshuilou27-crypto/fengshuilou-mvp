from data.bazi import (
    GAN_WUXING, FLOOR_WUXING, WUXING_RELATIONS,
    calculate_bazi, get_year_ganzhi, CAREER_WUXING,
    calculate_wang_shuai, get_yong_shen_floor_match,
    calculate_floor_wuxing_na_jia
)


def analyze_bazi(birth_date: str, floor_number: int, birth_time: str = None, user_job: str = None, building_facing: str = None):
    """
    八字匹配模組（v2.5 修正版：樓層五行加入納甲計算）
    
    v2.5 修正：
    1. 樓層五行從單純河圖尾數法，擴展為河圖+天干納甲雙系統
    2. 當提供建築坐向時，納甲系統以本宅卦象為基礎，按後天八卦序循環定各樓層五行
    3. 兩系統不一致時，以河圖為主，置信度降低
    """
    # 解析出生日期
    try:
        year = int(birth_date.split("-")[0])
    except (ValueError, IndexError):
        return {
            "status": "error",
            "score": 0,
            "max_score": 20,
            "data_source": "三六風水網專業知識庫",
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
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.3,
            "rationale": "八字计算失败，无法解析日期。"
        }
    
    # 獲取日主（日柱天干）五行
    day_master_gan = bazi_result["day_master"]["gan"]
    day_master_wuxing = bazi_result["day_master"]["wuxing"]
    
    # 計算旺衰和喜用神
    wang_shuai = calculate_wang_shuai(bazi_result)
    
    # v2.5: 樓層五行 (河圖 + 納甲)
    floor_wuxing_info = calculate_floor_wuxing_na_jia(floor_number, building_facing)
    floor_wuxing = floor_wuxing_info["combined_wuxing"]
    hetu_wuxing = floor_wuxing_info["hetu_wuxing"]
    najia_wuxing = floor_wuxing_info["najia_wuxing"]
    
    # 基於喜用神的樓層匹配
    score = 0
    relation = "未知"
    match_detail = {}
    
    if wang_shuai and wang_shuai.get("yong_shen") and floor_wuxing != "未知":
        yong_shen = wang_shuai["yong_shen"]
        match_detail = get_yong_shen_floor_match(yong_shen, floor_wuxing)
        score = match_detail["score"]
        relation = match_detail["relation"]
    else:
        # 回退到舊邏輯：僅用日主五行
        if day_master_wuxing != "未知" and floor_wuxing != "未知":
            if WUXING_RELATIONS["生"].get(floor_wuxing) == day_master_wuxing:
                score = 20
                relation = "生扶"
            elif WUXING_RELATIONS["生"].get(day_master_wuxing) == floor_wuxing:
                score = 10
                relation = "洩氣"
            elif WUXING_RELATIONS["克"].get(floor_wuxing) == day_master_wuxing:
                score = 4
                relation = "克制"
            elif WUXING_RELATIONS["克"].get(day_master_wuxing) == floor_wuxing:
                score = 14
                relation = "耗財"
            elif day_master_wuxing == floor_wuxing:
                score = 16
                relation = "比劫"
    
    score = min(20, max(0, score))
    
    # 職業五行加成
    career_bonus = 0
    career_wuxing = None
    career_relation = None
    if user_job and user_job in CAREER_WUXING:
        career_wuxing = CAREER_WUXING[user_job]
        if wang_shuai and wang_shuai.get("yong_shen"):
            yong_shen = wang_shuai["yong_shen"]
            if career_wuxing == yong_shen:
                career_bonus = 3
                career_relation = "職業即喜用神"
            elif WUXING_RELATIONS["生"].get(career_wuxing) == yong_shen:
                career_bonus = 2
                career_relation = "職業生喜用神"
            elif career_wuxing == wang_shuai.get("ji_shen"):
                career_bonus = -2
                career_relation = "職業即忌神"
            else:
                career_relation = "無明顯生克"
        else:
            if WUXING_RELATIONS["生"].get(career_wuxing) == day_master_wuxing or career_wuxing == day_master_wuxing:
                career_bonus = 2
                career_relation = "相生/比劫"
            elif WUXING_RELATIONS["克"].get(career_wuxing) == day_master_wuxing:
                career_bonus = -1
                career_relation = "相克"
            else:
                career_relation = "無明顯生克"
    
    final_score = max(0, min(20, score + career_bonus))
    
    # 四柱信息
    pillars = bazi_result
    
    # 生成詳細分析文字
    wang_shuai_rationale = ""
    if wang_shuai:
        ws = wang_shuai
        wang_shuai_rationale = (
            f"旺衰分析：日主{day_master_gan}({day_master_wuxing})在月令{ws['month_status']}，"
            f"月令得分{ws['month_score']}，通根得分{ws['root_score']}，天干生扶得分{ws['support_score']}，"
            f"總分{ws['strength_score']}，判定為「{ws['strength']}」。"
            f"喜用神為{ws['yong_shen']}，忌神為{ws['ji_shen']}。"
        )
    
    career_rationale = ""
    if career_wuxing:
        career_rationale = f" 職業'{user_job}'屬{career_wuxing}，與喜用神關係為「{career_relation}」，職業加成{career_bonus:+d}分。"
    
    floor_rationale = ""
    if match_detail:
        floor_rationale = f"{match_detail['desc']}"
    else:
        floor_rationale = f"樓層{floor_number}屬{floor_wuxing}（河圖{hetu_wuxing}"
        if najia_wuxing:
            floor_rationale += f"，納甲{najia_wuxing}"
        floor_rationale += f"），與日主{day_master_wuxing}關係為「{relation}」"
    
    # v2.5 置信度：納甲系統可用時置信度更高，僅河圖時置信度較低
    confidence = 0.75
    if not najia_wuxing:
        confidence = 0.6  # 缺少建築坐向，納甲系統無法使用
    
    return {
        "status": "success",
        "day_master_gan": day_master_gan,
        "day_master_wuxing": day_master_wuxing,
        "floor_number": floor_number,
        "floor_wuxing": floor_wuxing,
        "hetu_wuxing": hetu_wuxing,
        "najia_wuxing": najia_wuxing,
        "relation": relation,
        "score": final_score,
        "base_score": score,
        "career_bonus": career_bonus,
        "career_wuxing": career_wuxing,
        "career_relation": career_relation,
        "max_score": 20,
        "data_source": "三六風水網專業知識庫",
        "confidence": confidence,
        "bazi_full": {
            "year_pillar": f"{pillars['year_pillar']['gan']}{pillars['year_pillar']['zhi']}",
            "month_pillar": f"{pillars['month_pillar']['gan']}{pillars['month_pillar']['zhi']}",
            "day_pillar": f"{pillars['day_pillar']['gan']}{pillars['day_pillar']['zhi']}",
            "hour_pillar": f"{pillars['hour_pillar']['gan']}{pillars['hour_pillar']['zhi']}",
            "day_master": f"{day_master_gan}（{day_master_wuxing}）"
        },
        "wang_shuai": wang_shuai,
        "rationale": f"八字四柱：{pillars['year_pillar']['gan']}{pillars['year_pillar']['zhi']}年 "
                     f"{pillars['month_pillar']['gan']}{pillars['month_pillar']['zhi']}月 "
                     f"{pillars['day_pillar']['gan']}{pillars['day_pillar']['zhi']}日 "
                     f"{pillars['hour_pillar']['gan']}{pillars['hour_pillar']['zhi']}時。"
                     f"{wang_shuai_rationale}"
                     f"{floor_rationale}，基礎得分{score}分。{career_rationale}"
                     f"最終八字得分{final_score}分。"
                     f" 樓層五行計算方法：{floor_wuxing_info['method']}。"
                     " 基於三六風水網專業知識庫計算，僅供參考，具體判斷建議諮詢專業師傅。"
    }
