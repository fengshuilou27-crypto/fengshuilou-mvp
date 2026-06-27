#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FXTI 八字計算模組（修復版 v2）
基於 data/bazi.py 的驗證邏輯，修復日柱/月柱/時柱計算
"""

from datetime import datetime

# 天干
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 農曆新年表（用於年柱邊界判斷）
LUNAR_NEW_YEAR_TABLE = {
    1990: (1, 27), 1991: (2, 15), 1992: (2, 4), 1993: (1, 23),
    1994: (2, 10), 1995: (1, 31), 1996: (2, 19), 1997: (2, 7),
    1998: (1, 28), 1999: (2, 16), 2000: (2, 5), 2001: (1, 24),
    2002: (2, 12), 2003: (2, 1), 2004: (1, 22), 2005: (2, 9),
    2006: (1, 29), 2007: (2, 18), 2008: (2, 7), 2009: (1, 26),
    2010: (2, 14), 2011: (2, 3), 2012: (1, 23), 2013: (2, 10),
    2014: (1, 31), 2015: (2, 19), 2016: (2, 8), 2017: (1, 28),
    2018: (2, 16), 2019: (2, 5), 2020: (1, 25), 2021: (2, 12),
    2022: (2, 1), 2023: (1, 22), 2024: (2, 10), 2025: (1, 29),
    2026: (2, 17),
}

# 天干五行屬性
TIANGAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

# 地支五行屬性（主氣）
DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 地支藏干
DIZHI_CANGGAN = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲']
}


# ==================== 年柱計算（含農曆新年邊界） ====================

def get_year_ganzhi(year, month, day):
    """
    計算年柱（修復版：農曆新年邊界）。
    
    1984年為甲子年。
    如果日期在農曆新年前，使用上一年的干支。
    """
    # 判斷是否過了農曆新年
    new_year = LUNAR_NEW_YEAR_TABLE.get(year)
    if new_year:
        ny_month, ny_day = new_year
        target_date = datetime(year, month, day)
        new_year_date = datetime(year, ny_month, ny_day)
        if target_date < new_year_date:
            # 農曆新年前，使用上一年
            year -= 1
    
    offset = (year - 1984) % 60
    if offset < 0:
        offset += 60
    gan_idx = offset % 10
    zhi_idx = offset % 12
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


# ==================== 月柱計算（data/bazi.py 簡化版） ====================

def get_month_ganzhi(year, month):
    """
    計算月柱（基於 data/bazi.py 的簡化版）。
    
    以公曆月近似，正月(寅)從立春開始（約2月4日）。
    月干由年干決定（五虎遁）。
    """
    # 月地支映射（公曆月 → 地支）
    month_zhi_map = {
        1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午",
        7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥", 12: "子"
    }
    
    # 月干起點（五虎遁）
    # 甲己年 -> 丙寅起, 乙庚年 -> 戊寅起, 丙辛年 -> 庚寅起, 丁壬年 -> 壬寅起, 戊癸年 -> 甲寅起
    month_gan_start = {
        "甲": 2, "己": 2,   # 丙寅
        "乙": 4, "庚": 4,   # 戊寅
        "丙": 6, "辛": 6,   # 庚寅
        "丁": 8, "壬": 8,   # 壬寅
        "戊": 0, "癸": 0,   # 甲寅
    }
    
    year_gan = get_year_ganzhi(year, month, 1)[0]  # 取年干
    start_gan_idx = month_gan_start.get(year_gan, 0)
    
    zhi = month_zhi_map.get(month, "寅")
    zhi_idx = DIZHI.index(zhi)
    
    gan_idx = (start_gan_idx + zhi_idx) % 10
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


# ==================== 日柱計算（data/bazi.py 基準） ====================

def get_day_ganzhi(year, month, day):
    """
    計算日柱（基於 data/bazi.py 基準：2000-01-01 = 己卯日）。
    """
    from datetime import date
    
    base_date = date(2000, 1, 1)
    base_gan_idx = 5   # 己
    base_zhi_idx = 3   # 卯
    
    target_date = date(year, month, day)
    delta_days = (target_date - base_date).days
    
    gan_idx = (base_gan_idx + delta_days) % 10
    zhi_idx = (base_zhi_idx + delta_days) % 12
    
    if gan_idx < 0:
        gan_idx += 10
    if zhi_idx < 0:
        zhi_idx += 12
    
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


# ==================== 時柱計算（data/bazi.py 邏輯） ====================

def get_hour_zhi(hour):
    """根據小時獲取時辰地支"""
    if hour >= 23 or hour < 1:
        return "子"
    elif 1 <= hour < 3:
        return "丑"
    elif 3 <= hour < 5:
        return "寅"
    elif 5 <= hour < 7:
        return "卯"
    elif 7 <= hour < 9:
        return "辰"
    elif 9 <= hour < 11:
        return "巳"
    elif 11 <= hour < 13:
        return "午"
    elif 13 <= hour < 15:
        return "未"
    elif 15 <= hour < 17:
        return "申"
    elif 17 <= hour < 19:
        return "酉"
    elif 19 <= hour < 21:
        return "戌"
    else:  # 21 <= hour < 23
        return "亥"


def get_hour_ganzhi(day_gan, hour):
    """
    計算時柱（基於 data/bazi.py 邏輯）。
    
    時干由日干決定：
    甲己日 -> 甲子起, 乙庚日 -> 丙子起, 丙辛日 -> 戊子起, 丁壬日 -> 庚子起, 戊癸日 -> 壬子起
    """
    shi_gan_base = {
        "甲": 0, "己": 0,   # 甲子
        "乙": 2, "庚": 2,   # 丙子
        "丙": 4, "辛": 4,   # 戊子
        "丁": 6, "壬": 6,   # 庚子
        "戊": 8, "癸": 8,   # 壬子
    }
    
    hour_zhi = get_hour_zhi(hour)
    zhi_idx = DIZHI.index(hour_zhi)
    
    base_gan_idx = shi_gan_base.get(day_gan, 0)
    gan_idx = (base_gan_idx + zhi_idx) % 10
    
    return TIANGAN[gan_idx] + hour_zhi


# ==================== 主計算函數 ====================

def calculate_bazi(birth_year, birth_month, birth_day, birth_hour=None):
    """計算八字四柱（修復版 v2）"""
    year_gz = get_year_ganzhi(birth_year, birth_month, birth_day)
    month_gz = get_month_ganzhi(birth_year, birth_month)
    day_gz = get_day_ganzhi(birth_year, birth_month, birth_day)
    
    result = {
        'year_pillar': year_gz,
        'month_pillar': month_gz,
        'day_pillar': day_gz,
        'hour_pillar': None,
        'hour_provided': birth_hour is not None
    }
    
    if birth_hour is not None:
        hour_gz = get_hour_ganzhi(day_gz[0], birth_hour)
        result['hour_pillar'] = hour_gz
    
    return result


def count_wuxing(bazi_result, use_canggan=True):
    """統計八字五行數量"""
    wuxing_count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    
    pillars = [bazi_result['year_pillar'], bazi_result['month_pillar'], bazi_result['day_pillar']]
    if bazi_result['hour_pillar']:
        pillars.append(bazi_result['hour_pillar'])
    
    for pillar in pillars:
        tg = pillar[0]
        dz = pillar[1]
        
        tg_wx = TIANGAN_WUXING[tg]
        wuxing_count[tg_wx] += 1
        
        if use_canggan:
            canggan = DIZHI_CANGGAN[dz]
            weights = [1.0, 0.6, 0.3]
            for i, gan in enumerate(canggan):
                wx = TIANGAN_WUXING[gan]
                weight = weights[i] if i < len(weights) else 0.3
                wuxing_count[wx] += weight
        else:
            dz_wx = DIZHI_WUXING[dz]
            wuxing_count[dz_wx] += 1
    
    return wuxing_count


def calculate_wuxing_percentage(wuxing_count):
    """計算五行百分比"""
    total = sum(wuxing_count.values())
    if total == 0:
        return {wx: 20.0 for wx in wuxing_count}
    
    percentages = {}
    for wx, count in wuxing_count.items():
        percentages[wx] = round(count / total * 100, 2)
    
    return percentages


def get_innate_wuxing(birth_year, birth_month, birth_day, birth_hour=None, use_canggan=True):
    """獲取先天五行屬性（完整流程）"""
    bazi = calculate_bazi(birth_year, birth_month, birth_day, birth_hour)
    wuxing_count = count_wuxing(bazi, use_canggan)
    percentages = calculate_wuxing_percentage(wuxing_count)
    
    return {
        'bazi': bazi,
        'wuxing_count': wuxing_count,
        'wuxing_percentage': percentages
    }
