# 完整八字四柱計算
# 年柱、月柱、日柱、時柱

# 天干地支列表
GAN_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
GAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}

# 地支五行
ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 樓層尾數 -> 五行
FLOOR_WUXING = {
    "1": "水", "6": "水",
    "2": "火", "7": "火",
    "3": "木", "8": "木",
    "4": "金", "9": "金",
    "5": "土", "0": "土"
}

# 職業 -> 五行映射（18個職業分類）
CAREER_WUXING = {
    "金融/銀行/投資": "金",
    "法律/司法": "金",
    "軍警/安保": "金",
    "外科/牙科醫生": "金",
    "機械/工程/製造": "金",
    "教育/文化/出版": "木",
    "醫療/中醫/藥材": "木",
    "設計/藝術/創意": "木",
    "園藝/農業/林業": "木",
    "物流/運輸/航運": "水",
    "旅遊/酒店/服務": "水",
    "餐飲/飲食/食品": "火",
    "傳媒/廣告/公關": "水",
    "科技/IT/電子": "火",
    "能源/電力/化工": "火",
    "演藝/娛樂/媒體": "火",
    "房地產/建築/裝修": "土",
    "會計/行政/文職": "金",
    "管理/顧問/策劃": "土"
}

# 五行生克關係
WUXING_RELATIONS = {
    "生": {
        "水": "木", "木": "火", "火": "土", "土": "金", "金": "水"
    },
    "克": {
        "水": "火", "火": "金", "金": "木", "木": "土", "土": "水"
    }
}

# 地支藏干 (本氣/中氣/餘氣)
ZHI_HIDDEN_GAN = {
    "子": ["癸"],           # 水
    "丑": ["己", "癸", "辛"],  # 土水金
    "寅": ["甲", "丙", "戊"],  # 木火土
    "卯": ["乙"],           # 木
    "辰": ["戊", "乙", "癸"],  # 土木水
    "巳": ["丙", "庚", "戊"],  # 火金土
    "午": ["丁", "己"],       # 火土
    "未": ["己", "丁", "乙"],  # 土火木
    "申": ["庚", "壬", "戊"],  # 金水土
    "酉": ["辛"],           # 金
    "戌": ["戊", "辛", "丁"],  # 土金火
    "亥": ["壬", "甲"]       # 水木
}

# 月令旺衰表 (月支 -> 各五行狀態)
# 旺: 當令, 相: 次旺, 休: 休息, 囚: 囚禁, 死: 最弱
MONTH_WANG_SHUAI = {
    "寅": {"木": "旺", "火": "相", "水": "休", "金": "囚", "土": "死"},
    "卯": {"木": "旺", "火": "相", "水": "休", "金": "囚", "土": "死"},
    "辰": {"土": "旺", "金": "相", "火": "休", "木": "囚", "水": "死"},
    "巳": {"火": "旺", "土": "相", "木": "休", "水": "囚", "金": "死"},
    "午": {"火": "旺", "土": "相", "木": "休", "水": "囚", "金": "死"},
    "未": {"土": "旺", "金": "相", "火": "休", "木": "囚", "水": "死"},
    "申": {"金": "旺", "水": "相", "土": "休", "火": "囚", "木": "死"},
    "酉": {"金": "旺", "水": "相", "土": "休", "火": "囚", "木": "死"},
    "戌": {"土": "旺", "金": "相", "火": "休", "木": "囚", "水": "死"},
    "亥": {"水": "旺", "木": "相", "金": "休", "土": "囚", "火": "死"},
    "子": {"水": "旺", "木": "相", "金": "休", "土": "囚", "火": "死"},
    "丑": {"土": "旺", "金": "相", "火": "休", "木": "囚", "水": "死"}
}

# 旺衰狀態分數 (用於量化計算)
WANG_SHUAI_SCORE = {
    "旺": 5, "相": 3, "休": 1, "囚": -1, "死": -3
}

# 五行生扶關係 (用於喜用神計算)
# 生我者 = 印星, 我生者 = 食傷, 克我者 = 官殺, 我克者 = 財星, 同我者 = 比劫
WUXING_SHEN_FU = {
    "生我": {"水": "金", "木": "水", "火": "木", "土": "火", "金": "土"},  # 印星
    "我生": {"水": "木", "木": "火", "火": "土", "土": "金", "金": "水"},  # 食傷
    "克我": {"水": "土", "木": "金", "火": "水", "土": "木", "金": "火"},  # 官殺
    "我克": {"水": "火", "木": "土", "火": "金", "土": "水", "金": "木"},  # 財星
    "同我": {"水": "水", "木": "木", "火": "火", "土": "土", "金": "金"}   # 比劫
}

TIME_TO_ZHI = {
    (0, 1): "子",   # 23:00-01:00
    (1, 3): "丑",   # 01:00-03:00
    (3, 5): "寅",   # 03:00-05:00
    (5, 7): "卯",   # 05:00-07:00
    (7, 9): "辰",   # 07:00-09:00
    (9, 11): "巳",  # 09:00-11:00
    (11, 13): "午", # 11:00-13:00
    (13, 15): "未", # 13:00-15:00
    (15, 17): "申", # 15:00-17:00
    (17, 19): "酉", # 17:00-19:00
    (19, 21): "戌", # 19:00-21:00
    (21, 23): "亥", # 21:00-23:00
    (23, 24): "子", # 23:00-00:00
}

# 時干計算表（日干天干 -> 時辰地支 -> 時干）
# 日干為甲/己 -> 甲子起
# 日干為乙/庚 -> 丙子起
# 日干為丙/辛 -> 戊子起
# 日干為丁/壬 -> 庚子起
# 日干為戊/癸 -> 壬子起
SHI_GAN_BASE = {
    "甲": 0, "己": 0,  # 甲子
    "乙": 2, "庚": 2,  # 丙子
    "丙": 4, "辛": 4,  # 戊子
    "丁": 6, "壬": 6,  # 庚子
    "戊": 8, "癸": 8,  # 壬子
}


def get_hour_zhi(hour: int, minute: int = 0):
    """根據小時分鐘獲取時辰地支"""
    total_minutes = hour * 60 + minute
    
    # 子時跨越23:00-01:00，特殊處理
    if total_minutes >= 23 * 60 or total_minutes < 60:  # 23:00-01:00
        return "子"
    
    for (start, end), zhi in TIME_TO_ZHI.items():
        if start <= hour < end:
            return zhi
    
    return "子"


def get_year_ganzhi(year: int):
    """計算年柱天干地支
    1984年為甲子年
    """
    offset = (year - 1984) % 60
    if offset < 0:
        offset += 60
    gan_idx = offset % 10
    zhi_idx = offset % 12
    return GAN_LIST[gan_idx], ZHI_LIST[zhi_idx]


def get_month_ganzhi(year: int, month: int):
    """計算月柱天干地支（簡化版，以公曆月近似）
    
    傳統八字以節氣為界，MVP簡化以公曆月近似：
    - 正月(寅): 立春開始 (約2月4日)
    - 二月(卯): 驚蟄開始 (約3月6日)
    - ...
    
    月干由年干決定：
    甲己年 -> 丙寅起
    乙庚年 -> 戊寅起
    丙辛年 -> 庚寅起
    丁壬年 -> 壬寅起
    戊癸年 -> 甲寅起
    """
    # 月地支（簡化：公曆月+1，子=11月，丑=12月，寅=1月...）
    month_zhi_map = {
        1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午",
        7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥", 12: "子"
    }
    
    # 月干由年干決定
    year_gan, _ = get_year_ganzhi(year)
    
    # 月干起點
    month_gan_start = {
        "甲": 2, "己": 2,  # 丙寅
        "乙": 4, "庚": 4,  # 戊寅
        "丙": 6, "辛": 6,  # 庚寅
        "丁": 8, "壬": 8,  # 壬寅
        "戊": 0, "癸": 0,  # 甲寅
    }
    
    start_gan_idx = month_gan_start.get(year_gan, 0)
    
    # 月地支索引
    zhi_idx = ZHI_LIST.index(month_zhi_map.get(month, "寅"))
    
    # 月干索引：起點 + 月地支索引（寅=0, 卯=1, ...）
    gan_idx = (start_gan_idx + zhi_idx) % 10
    
    return GAN_LIST[gan_idx], ZHI_LIST[zhi_idx]


def get_day_ganzhi(year: int, month: int, day: int):
    """計算日柱天干地支
    
    使用基準日法：已知某天的干支，推算其他日期
    基準日：2000-01-01 = 己卯日
    
    算法：
    1. 計算目標日期與基準日期的天數差
    2. 天數差 % 60 = 干支偏移
    """
    from datetime import date
    
    # 基準日
    base_date = date(2000, 1, 1)
    base_gan_idx = 5  # 己
    base_zhi_idx = 3  # 卯
    
    try:
        target_date = date(year, month, day)
    except ValueError:
        # 日期無效，返回默认值
        return "戊", "辰"
    
    # 計算天數差
    delta_days = (target_date - base_date).days
    
    # 計算干支偏移
    gan_idx = (base_gan_idx + delta_days) % 10
    zhi_idx = (base_zhi_idx + delta_days) % 12
    
    if gan_idx < 0:
        gan_idx += 10
    if zhi_idx < 0:
        zhi_idx += 12
    
    return GAN_LIST[gan_idx], ZHI_LIST[zhi_idx]


def get_hour_ganzhi(day_gan: str, hour_zhi: str):
    """計算時柱天干地支
    
    時干由日干決定：
    甲己日 -> 甲子起
    乙庚日 -> 丙子起
    丙辛日 -> 戊子起
    丁壬日 -> 庚子起
    戊癸日 -> 壬子起
    """
    base_gan_idx = SHI_GAN_BASE.get(day_gan, 0)
    
    # 時辰地支索引
    zhi_idx = ZHI_LIST.index(hour_zhi)
    
    # 時干索引
    gan_idx = (base_gan_idx + zhi_idx) % 10
    
    return GAN_LIST[gan_idx], hour_zhi


def calculate_wang_shuai(bazi_result: dict):
    """
    計算日主旺衰和喜用神
    
    Args:
        bazi_result: calculate_bazi 返回的四柱結果
    
    Returns:
        dict: {
            'strength': '旺'/'中和'/'弱',
            'strength_score': 分數 (-10 到 10),
            'yong_shen': 喜用神 (五行),
            'ji_shen': 忌神 (五行),
            'wang_shuai_details': 詳細分析
        }
    """
    if not bazi_result:
        return None
    
    day_master = bazi_result["day_master"]["wuxing"]
    day_gan = bazi_result["day_pillar"]["gan"]
    day_zhi = bazi_result["day_pillar"]["zhi"]
    month_zhi = bazi_result["month_pillar"]["zhi"]
    month_gan = bazi_result["month_pillar"]["gan"]
    year_zhi = bazi_result["year_pillar"]["zhi"]
    year_gan = bazi_result["year_pillar"]["gan"]
    hour_zhi = bazi_result["hour_pillar"]["zhi"]
    hour_gan = bazi_result["hour_pillar"]["gan"]
    
    # 1. 月令判斷 (最重要，佔40%)
    month_status = MONTH_WANG_SHUAI.get(month_zhi, {}).get(day_master, "平")
    month_score = WANG_SHUAI_SCORE.get(month_status, 0) * 2  # 月令權重加倍
    
    # 2. 通根判斷 (地支藏干有無日主同類) (佔30%)
    root_score = 0
    root_details = []
    
    # 檢查日支藏干
    day_zhi_hidden = ZHI_HIDDEN_GAN.get(day_zhi, [])
    for g in day_zhi_hidden:
        if GAN_WUXING.get(g) == day_master:
            root_score += 3
            root_details.append(f"日支{day_zhi}藏{g}({day_master})")
    
    # 檢查月支藏干
    month_zhi_hidden = ZHI_HIDDEN_GAN.get(month_zhi, [])
    for g in month_zhi_hidden:
        if GAN_WUXING.get(g) == day_master:
            root_score += 2
            root_details.append(f"月支{month_zhi}藏{g}({day_master})")
    
    # 檢查年支藏干
    year_zhi_hidden = ZHI_HIDDEN_GAN.get(year_zhi, [])
    for g in year_zhi_hidden:
        if GAN_WUXING.get(g) == day_master:
            root_score += 1
            root_details.append(f"年支{year_zhi}藏{g}({day_master})")
    
    # 檢查時支藏干
    if hour_zhi != "?":
        hour_zhi_hidden = ZHI_HIDDEN_GAN.get(hour_zhi, [])
        for g in hour_zhi_hidden:
            if GAN_WUXING.get(g) == day_master:
                root_score += 1
                root_details.append(f"時支{hour_zhi}藏{g}({day_master})")
    
    # 3. 天干生扶判斷 (佔30%)
    support_score = 0
    support_details = []
    
    # 印星 (生我者)
    yin_shen = WUXING_SHEN_FU["生我"].get(day_master, "")
    # 比劫 (同我者)
    bi_jie = WUXING_SHEN_FU["同我"].get(day_master, "")
    
    all_gans = [year_gan, month_gan, hour_gan]
    for gan in all_gans:
        if gan == "?":
            continue
        gan_wx = GAN_WUXING.get(gan, "")
        if gan_wx == yin_shen:
            support_score += 2
            support_details.append(f"{gan}({gan_wx})生扶日主")
        elif gan_wx == bi_jie:
            support_score += 1.5
            support_details.append(f"{gan}({gan_wx})比劫幫身")
        elif gan_wx == WUXING_SHEN_FU["克我"].get(day_master, ""):
            support_score -= 2
            support_details.append(f"{gan}({gan_wx})克制日主")
        elif gan_wx == WUXING_SHEN_FU["我克"].get(day_master, ""):
            support_score -= 1
            support_details.append(f"{gan}({gan_wx})耗泄日主")
    
    # 計算總分
    total_score = month_score + root_score + support_score
    
    # 判定旺衰
    if total_score >= 5:
        strength = "旺"
    elif total_score <= -5:
        strength = "弱"
    else:
        strength = "中和"
    
    # 計算喜用神
    if strength == "旺":
        yong_shen = WUXING_SHEN_FU["克我"].get(day_master, "")  # 官殺
        if not yong_shen:
            yong_shen = WUXING_SHEN_FU["我生"].get(day_master, "")  # 食傷
        ji_shen = WUXING_SHEN_FU["同我"].get(day_master, "")  # 比劫
    elif strength == "弱":
        yong_shen = WUXING_SHEN_FU["生我"].get(day_master, "")  # 印星
        if not yong_shen:
            yong_shen = WUXING_SHEN_FU["同我"].get(day_master, "")  # 比劫
        ji_shen = WUXING_SHEN_FU["克我"].get(day_master, "")  # 官殺
    else:  # 中和
        yong_shen = WUXING_SHEN_FU["生我"].get(day_master, "")
        ji_shen = WUXING_SHEN_FU["克我"].get(day_master, "")
    
    return {
        "strength": strength,
        "strength_score": round(total_score, 2),
        "yong_shen": yong_shen,
        "ji_shen": ji_shen,
        "month_status": month_status,
        "month_score": month_score,
        "root_score": root_score,
        "root_details": root_details,
        "support_score": support_score,
        "support_details": support_details,
        "yin_shen": yin_shen,
        "bi_jie": bi_jie,
    }


def get_yong_shen_floor_match(yong_shen: str, floor_wuxing: str) -> dict:
    """
    根據喜用神判斷樓層匹配度
    """
    if not yong_shen or not floor_wuxing or floor_wuxing == "未知":
        return {"score": 10, "relation": "未知", "desc": "無法判斷"}
    
    if floor_wuxing == yong_shen:
        return {"score": 20, "relation": "喜用神", "desc": f"樓層屬{floor_wuxing}，為喜用神，大吉"}
    
    if WUXING_RELATIONS["生"].get(floor_wuxing) == yong_shen:
        return {"score": 16, "relation": "生扶", "desc": f"樓層屬{floor_wuxing}，生扶喜用神{yong_shen}，吉"}
    
    if WUXING_RELATIONS["克"].get(floor_wuxing) == yong_shen:
        return {"score": 4, "relation": "克制", "desc": f"樓層屬{floor_wuxing}，克制喜用神{yong_shen}，凶"}
    
    if WUXING_RELATIONS["生"].get(yong_shen) == floor_wuxing:
        return {"score": 8, "relation": "泄氣", "desc": f"樓層屬{floor_wuxing}，喜用神{yong_shen}生之，泄氣"}
    
    if WUXING_RELATIONS["克"].get(yong_shen) == floor_wuxing:
        return {"score": 12, "relation": "耗財", "desc": f"樓層屬{floor_wuxing}，喜用神{yong_shen}克之，耗財"}
    
    if floor_wuxing == yong_shen:
        return {"score": 14, "relation": "比劫", "desc": f"樓層屬{floor_wuxing}，與喜用神同，比劫"}
    
    return {"score": 10, "relation": "未知", "desc": "無法判斷"}


def calculate_bazi(birth_date: str, birth_time: str = None):
    """
    計算完整四柱八字
    
    Args:
        birth_date: YYYY-MM-DD 格式
        birth_time: HH:MM 格式（可選）
    
    Returns:
        dict: {
            'year_pillar': (年干, 年支),
            'month_pillar': (月干, 月支),
            'day_pillar': (日干, 日支),  # 日主
            'hour_pillar': (時干, 時支),
            'day_master': (日干, 日干五行)
        }
    """
    try:
        parts = birth_date.split("-")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
    except (ValueError, IndexError):
        return None
    
    # 年柱
    year_gan, year_zhi = get_year_ganzhi(year)
    
    # 月柱
    month_gan, month_zhi = get_month_ganzhi(year, month)
    
    # 日柱
    day_gan, day_zhi = get_day_ganzhi(year, month, day)
    
    # 時柱
    hour_gan = ""
    hour_zhi = ""
    if birth_time:
        try:
            time_parts = birth_time.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            hour_zhi = get_hour_zhi(hour, minute)
            hour_gan, hour_zhi = get_hour_ganzhi(day_gan, hour_zhi)
        except (ValueError, IndexError):
            hour_gan = "?"
            hour_zhi = "?"
    else:
        hour_gan = "?"
        hour_zhi = "?"
    
    # 日主 = 日干
    day_master_gan = day_gan
    day_master_wuxing = GAN_WUXING.get(day_gan, "未知")
    
    return {
        "year_pillar": {"gan": year_gan, "zhi": year_zhi, "gan_wuxing": GAN_WUXING.get(year_gan, "未知")},
        "month_pillar": {"gan": month_gan, "zhi": month_zhi, "gan_wuxing": GAN_WUXING.get(month_gan, "未知")},
        "day_pillar": {"gan": day_gan, "zhi": day_zhi, "gan_wuxing": GAN_WUXING.get(day_gan, "未知")},
        "hour_pillar": {"gan": hour_gan, "zhi": hour_zhi, "gan_wuxing": GAN_WUXING.get(hour_gan, "未知") if hour_gan != "?" else "未知"},
        "day_master": {
            "gan": day_master_gan,
            "wuxing": day_master_wuxing,
            "full": f"{day_master_gan}（{day_master_wuxing}）"
        }
    }


# 為向後兼容保留舊函數
get_year_ganzhi_old = get_year_ganzhi
YEAR_GAN_WUXING = GAN_WUXING
FLOOR_WUXING = FLOOR_WUXING
WUXING_RELATIONS = WUXING_RELATIONS
GAN_LIST = GAN_LIST
ZHI_LIST = ZHI_LIST
