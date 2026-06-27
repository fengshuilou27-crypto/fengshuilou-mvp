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

# 時辰對照表（時辰 -> 地支）
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
