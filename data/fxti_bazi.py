#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FXTI 八字計算模組
輸入公曆年月日時，計算四柱八字，統計五行屬性
"""

from datetime import datetime

# 天干
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

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


def get_year_ganzhi(year):
    """計算年柱"""
    tg_index = (year - 4) % 10
    dz_index = (year - 4) % 12
    return TIANGAN[tg_index] + DIZHI[dz_index]


def get_month_ganzhi(year, month):
    """計算月柱"""
    dz_index = (month + 1) % 12
    if dz_index < 2:
        dz_index += 12
    dz = DIZHI[dz_index - 2]

    year_gan = get_year_ganzhi(year)[0]
    start_gan_map = {
        '甲': '丙', '己': '丙',
        '乙': '戊', '庚': '戊',
        '丙': '庚', '辛': '庚',
        '丁': '壬', '壬': '壬',
        '戊': '甲', '癸': '甲'
    }

    start_gan = start_gan_map[year_gan]
    start_index = TIANGAN.index(start_gan)
    tg_index = (start_index + month - 1) % 10
    tg = TIANGAN[tg_index]

    return tg + dz


def get_day_ganzhi(year, month, day):
    """計算日柱"""
    base_date = datetime(1900, 1, 31)
    target_date = datetime(year, month, day)
    delta_days = (target_date - base_date).days

    base_gan = 0
    base_zhi = 4

    gan_index = (base_gan + delta_days) % 10
    zhi_index = (base_zhi + delta_days) % 12

    return TIANGAN[gan_index] + DIZHI[zhi_index]


def get_hour_ganzhi(day_gan, hour):
    """計算時柱"""
    zhi_index = (hour + 1) // 2 % 12
    dz = DIZHI[zhi_index]

    start_gan_map = {
        '甲': '甲', '己': '甲',
        '乙': '丙', '庚': '丙',
        '丙': '戊', '辛': '戊',
        '丁': '庚', '壬': '庚',
        '戊': '壬', '癸': '壬'
    }

    start_gan = start_gan_map[day_gan]
    start_index = TIANGAN.index(start_gan)
    tg_index = (start_index + (hour + 1) // 2) % 10
    tg = TIANGAN[tg_index]

    return tg + dz


def calculate_bazi(birth_year, birth_month, birth_day, birth_hour=None):
    """計算八字四柱"""
    year_gz = get_year_ganzhi(birth_year)
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
