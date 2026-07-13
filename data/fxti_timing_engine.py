"""
歲月磨合引擎 v1.0
基於大運流年交叉分析，預測雙方關係的「好年」和「壞年」

核心算法：
1. 計算雙方未來10年大運（每10年一運）
2. 計算每年流年干支
3. 對比雙方大運+流年的五行屬性
4. 標記和諧期/考驗期/衝突期/危機期
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class DayunInfo:
    """大運信息"""
    start_year: int
    end_year: int
    gan: str  # 天干
    zhi: str  # 地支
    element: str  # 五行屬性
    is_favorable: bool  # 是否為喜用神


@dataclass
class LiunianInfo:
    """流年信息"""
    year: int
    gan: str
    zhi: str
    element: str


@dataclass
class YearlyCompatibility:
    """年度相容性分析"""
    year: int
    score: int  # 0-100
    status: str  # harmony/test/conflict/crisis
    status_cn: str  # 和諧/考驗/衝突/危機
    note: str
    person_a_dayun: str
    person_b_dayun: str
    liunian: str
    interaction_type: str  # 相生/相剋/比和


# 天干五行對照
GAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

# 地支五行對照
ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 五行生剋關係
WUXING_RELATIONS = {
    '木': {'生': '火', '剋': '土', '被生': '水', '被剋': '金'},
    '火': {'生': '土', '剋': '金', '被生': '木', '被剋': '水'},
    '土': {'生': '金', '剋': '水', '被生': '火', '被剋': '木'},
    '金': {'生': '水', '剋': '木', '被生': '土', '被剋': '火'},
    '水': {'生': '木', '剋': '火', '被生': '金', '被剋': '土'}
}

# 六十甲子順序
JIAZI_CYCLE = [
    '甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉',
    '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未',
    '甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳',
    '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯',
    '甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑',
    '甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'
]


def get_year_ganzhi(year: int) -> Tuple[str, str]:
    """根據年份計算天干地支"""
    # 1984年是甲子年
    offset = (year - 1984) % 60
    if offset < 0:
        offset += 60
    ganzhi = JIAZI_CYCLE[offset]
    return ganzhi[0], ganzhi[1]


def calculate_dayun(birth_year: int, birth_month: int, birth_day: int, 
                    gender: str, current_year: int = 2026) -> List[DayunInfo]:
    """
    簡化版大運計算
    實際應該基於八字排盤，這裡使用簡化算法
    """
    # 根據出生年計算起運年齡（簡化：假設3歲起運）
    start_age = 3
    start_year = birth_year + start_age
    
    dayuns = []
    # 計算未來6個大運（60年）
    for i in range(6):
        dy_start = start_year + i * 10
        dy_end = dy_start + 9
        
        # 簡化：使用年份對應的天干地支
        gan, zhi = get_year_ganzhi(dy_start)
        element = GAN_WUXING.get(gan, '土')
        
        # 判斷是否為喜用神（簡化：假設木火為喜用）
        is_favorable = element in ['木', '火']
        
        dayuns.append(DayunInfo(
            start_year=dy_start,
            end_year=dy_end,
            gan=gan,
            zhi=zhi,
            element=element,
            is_favorable=is_favorable
        ))
    
    return dayuns


def analyze_wuxing_interaction(element_a: str, element_b: str) -> Tuple[str, int]:
    """
    分析兩個五行之間的互動關係
    返回: (關係類型, 分數加成)
    """
    if element_a == element_b:
        return '比和', 5  # 同屬性，平和
    
    relations_a = WUXING_RELATIONS.get(element_a, {})
    
    if relations_a.get('生') == element_b:
        return '相生', 10  # A生B，A付出，B受益
    elif relations_a.get('剋') == element_b:
        return '相剋', -10  # A剋B，衝突
    elif relations_a.get('被生') == element_b:
        return '被生', 8  # B生A，A受益
    elif relations_a.get('被剋') == element_b:
        return '被剋', -8  # B剋A，A受壓
    
    return '中性', 0


def analyze_timing_compatibility(
    birth_a: Dict[str, Any],
    birth_b: Dict[str, Any],
    analysis_years: int = 10,
    current_year: int = 2026
) -> Dict[str, Any]:
    """
    歲月磨合分析主函數
    
    參數:
        birth_a: {"year": 1990, "month": 5, "day": 15, "gender": "male"}
        birth_b: {"year": 1992, "month": 8, "day": 20, "gender": "female"}
        analysis_years: 分析未來多少年
        current_year: 從哪一年開始分析
    
    返回:
        {
            "timeline": [...],  # 每年分析
            "best_years": [...],  # 最佳年份
            "challenging_years": [...],  # 挑戰年份
            "marriage_window": [...],  # 適合結婚的年份
            "overall_timing_score": 78,  # 總體時間分數
            "summary": "..."  # 總結建議
        }
    """
    # 計算雙方大運
    dayuns_a = calculate_dayun(
        birth_a['year'], birth_a['month'], birth_a['day'], birth_a['gender']
    )
    dayuns_b = calculate_dayun(
        birth_b['year'], birth_b['month'], birth_b['day'], birth_b['gender']
    )
    
    timeline = []
    best_years = []
    challenging_years = []
    marriage_candidates = []
    total_score = 0
    
    for year in range(current_year, current_year + analysis_years):
        # 獲取當年流年
        liu_gan, liu_zhi = get_year_ganzhi(year)
        liu_element = GAN_WUXING.get(liu_gan, '土')
        
        # 找出雙方當前大運
        dayun_a = next((d for d in dayuns_a if d.start_year <= year <= d.end_year), None)
        dayun_b = next((d for d in dayuns_b if d.start_year <= year <= d.end_year), None)
        
        if not dayun_a or not dayun_b:
            continue
        
        # 分析三方互動（A大運 vs B大運 vs 流年）
        score = 50  # 基礎分
        
        # A大運 vs B大運
        interaction_ab = analyze_wuxing_interaction(dayun_a.element, dayun_b.element)
        score += interaction_ab[1]
        
        # 流年 vs A大運
        interaction_la = analyze_wuxing_interaction(liu_element, dayun_a.element)
        score += interaction_la[1] * 0.5
        
        # 流年 vs B大運
        interaction_lb = analyze_wuxing_interaction(liu_element, dayun_b.element)
        score += interaction_lb[1] * 0.5
        
        # 喜用神加成
        if dayun_a.is_favorable and dayun_b.is_favorable:
            score += 15  # 雙方都走喜用神運
        elif dayun_a.is_favorable or dayun_b.is_favorable:
            score += 5  # 一方走喜用神運
        else:
            score -= 5  # 雙方都不走喜用神運
        
        # 限制分數範圍
        score = max(0, min(100, score))
        total_score += score
        
        # 判斷狀態
        if score >= 80:
            status = 'harmony'
            status_cn = '和諧'
            best_years.append(year)
            if score >= 90:
                marriage_candidates.append(year)
        elif score >= 60:
            status = 'test'
            status_cn = '考驗'
        elif score >= 40:
            status = 'conflict'
            status_cn = '衝突'
            challenging_years.append(year)
        else:
            status = 'crisis'
            status_cn = '危機'
            challenging_years.append(year)
        
        # 生成說明
        note = generate_year_note(
            year, dayun_a, dayun_b, liu_element,
            interaction_ab[0], score
        )
        
        timeline.append(YearlyCompatibility(
            year=year,
            score=score,
            status=status,
            status_cn=status_cn,
            note=note,
            person_a_dayun=f"{dayun_a.gan}{dayun_a.zhi} ({dayun_a.element})",
            person_b_dayun=f"{dayun_b.gan}{dayun_b.zhi} ({dayun_b.element})",
            liunian=f"{liu_gan}{liu_zhi} ({liu_element})",
            interaction_type=interaction_ab[0]
        ))
    
    # 計算總體分數
    overall_score = round(total_score / len(timeline), 1) if timeline else 50
    
    # 生成總結
    summary = generate_summary(timeline, best_years, challenging_years, marriage_candidates)
    
    return {
        "timeline": [
            {
                "year": y.year,
                "score": y.score,
                "status": y.status,
                "status_cn": y.status_cn,
                "note": y.note,
                "person_a_dayun": y.person_a_dayun,
                "person_b_dayun": y.person_b_dayun,
                "liunian": y.liunian,
                "interaction_type": y.interaction_type
            }
            for y in timeline
        ],
        "best_years": best_years,
        "challenging_years": challenging_years,
        "marriage_window": marriage_candidates,
        "overall_timing_score": overall_score,
        "summary": summary
    }


def generate_year_note(year: int, dayun_a: DayunInfo, dayun_b: DayunInfo,
                       liu_element: str, interaction: str, score: int) -> str:
    """生成年度說明文字"""
    notes = []
    
    if interaction == '相生':
        notes.append(f"{dayun_a.element}生{dayun_b.element}，甲方運勢能滋養乙方")
    elif interaction == '被生':
        notes.append(f"{dayun_b.element}生{dayun_a.element}，乙方運勢能滋養甲方")
    elif interaction == '相剋':
        notes.append(f"{dayun_a.element}剋{dayun_b.element}，雙方易有摩擦")
    elif interaction == '被剋':
        notes.append(f"{dayun_b.element}剋{dayun_a.element}，甲方可能感到壓力")
    else:
        notes.append(f"雙方大運五行{dayun_a.element}與{dayun_b.element}比和，關係平穩")
    
    # 流年影響
    if score >= 80:
        notes.append(f"流年{liu_element}旺，整體運勢順遂")
    elif score <= 40:
        notes.append(f"流年{liu_element}不利，需多加注意")
    
    return "；".join(notes)


def generate_summary(timeline: List[YearlyCompatibility], 
                    best_years: List[int],
                    challenging_years: List[int],
                    marriage_candidates: List[int]) -> str:
    """生成總結建議"""
    parts = []
    
    # 總體評價
    if len(best_years) >= len(timeline) * 0.5:
        parts.append("整體來看，你們未來的時間線非常和諧，大部分年份都處於良好狀態。")
    elif len(best_years) >= len(timeline) * 0.3:
        parts.append("整體來看，你們未來的時間線有起伏，但好年居多。")
    else:
        parts.append("整體來看，你們未來的時間線挑戰較多，需要更多磨合。")
    
    # 最佳年份
    if best_years:
        if len(best_years) >= 3:
            parts.append(f"特別是{best_years[0]}、{best_years[1]}、{best_years[2]}年，雙方運勢極佳，適合推進關係。")
        else:
            parts.append(f"{', '.join(map(str, best_years))}年運勢較好，可以把握機會。")
    
    # 挑戰年份
    if challenging_years:
        parts.append(f"需要注意的是{', '.join(map(str, challenging_years[:2]))}年，這些年份可能會有較多挑戰，建議多溝通、互相體諒。")
    
    # 結婚建議
    if marriage_candidates:
        parts.append(f"從命理角度，{marriage_candidates[0]}年是非常適合結婚的年份，雙方大運和流年都非常有利。")
    
    return "".join(parts)


def get_daily_fortune(birth_info: Dict[str, Any], date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    每日運勢計算
    
    參數:
        birth_info: {"year": 1990, "month": 5, "day": 15}
        date: 指定日期，默認今天
    
    返回:
        {
            "date": "2026-07-14",
            "daily_element": "木",
            "fortune_score": 85,
            "lucky_color": "綠色",
            "lucky_direction": "東方",
            "suitable": ["社交", "表白", "約會"],
            "unsuitable": ["爭執", "簽約"],
            "advice": "..."
        }
    """
    if date is None:
        date = datetime.now()
    
    # 計算當日干支
    gan, zhi = get_year_ganzhi(date.year)
    daily_element = GAN_WUXING.get(gan, '土')
    
    # 計算個人五行（簡化：根據出生年）
    birth_gan, _ = get_year_ganzhi(birth_info['year'])
    person_element = GAN_WUXING.get(birth_gan, '土')
    
    # 分析互動
    interaction, base_score = analyze_wuxing_interaction(person_element, daily_element)
    
    # 計算運勢分數
    fortune_score = 50 + base_score * 3
    fortune_score = max(0, min(100, fortune_score))
    
    # 根據五行生成建議
    advice_map = {
        '木': {
            'lucky_color': '綠色、青色',
            'lucky_direction': '東方',
            'suitable': ['社交', '學習', '規劃', '植栽'],
            'unsuitable': ['爭執', '冒險投資']
        },
        '火': {
            'lucky_color': '紅色、紫色',
            'lucky_direction': '南方',
            'suitable': ['表白', '創作', '運動', '聚會'],
            'unsuitable': ['衝動消費', '熬夜']
        },
        '土': {
            'lucky_color': '黃色、棕色',
            'lucky_direction': '中央',
            'suitable': ['理財', '置產', '聚餐', '穩定工作'],
            'unsuitable': ['變動', '借貸']
        },
        '金': {
            'lucky_color': '白色、金色',
            'lucky_direction': '西方',
            'suitable': ['談判', '決策', '整理', '健身'],
            'unsuitable': ['拖延', '過度勞累']
        },
        '水': {
            'lucky_color': '黑色、藍色',
            'lucky_direction': '北方',
            'suitable': ['思考', '創意', '旅行', '溝通'],
            'unsuitable': ['孤立', '情緒化']
        }
    }
    
    advice = advice_map.get(daily_element, advice_map['土'])
    
    # 生成建議文字
    if fortune_score >= 80:
        advice_text = f"今日{daily_element}旺，與你的五行{person_element}相生，是充滿機遇的一天！"
    elif fortune_score >= 60:
        advice_text = f"今日運勢平穩，適合按部就班地完成計劃。"
    else:
        advice_text = f"今日五行與你有些衝突，建議低調行事，避免重大決策。"
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "daily_element": daily_element,
        "person_element": person_element,
        "interaction": interaction,
        "fortune_score": fortune_score,
        "lucky_color": advice['lucky_color'],
        "lucky_direction": advice['lucky_direction'],
        "suitable": advice['suitable'],
        "unsuitable": advice['unsuitable'],
        "advice": advice_text
    }


# 測試函數
if __name__ == "__main__":
    # 測試歲月磨合分析
    birth_a = {"year": 1990, "month": 5, "day": 15, "gender": "male"}
    birth_b = {"year": 1992, "month": 8, "day": 20, "gender": "female"}
    
    result = analyze_timing_compatibility(birth_a, birth_b, analysis_years=10)
    
    print("=" * 60)
    print("歲月磨合分析結果")
    print("=" * 60)
    print(f"\n總體時間分數: {result['overall_timing_score']}/100")
    print(f"最佳年份: {result['best_years']}")
    print(f"挑戰年份: {result['challenging_years']}")
    print(f"適合結婚: {result['marriage_window']}")
    print(f"\n總結: {result['summary']}")
    
    print("\n" + "=" * 60)
    print("逐年分析")
    print("=" * 60)
    for year_data in result['timeline']:
        print(f"\n{year_data['year']}年:")
        print(f"  分數: {year_data['score']}/100")
        print(f"  狀態: {year_data['status_cn']}")
        print(f"  甲方大運: {year_data['person_a_dayun']}")
        print(f"  乙方大運: {year_data['person_b_dayun']}")
        print(f"  流年: {year_data['liunian']}")
        print(f"  說明: {year_data['note']}")
    
    # 測試每日運勢
    print("\n" + "=" * 60)
    print("每日運勢")
    print("=" * 60)
    fortune = get_daily_fortune(birth_a)
    print(f"\n日期: {fortune['date']}")
    print(f"今日五行: {fortune['daily_element']}")
    print(f"個人五行: {fortune['person_element']}")
    print(f"互動: {fortune['interaction']}")
    print(f"運勢分數: {fortune['fortune_score']}/100")
    print(f"幸運色: {fortune['lucky_color']}")
    print(f"幸運方向: {fortune['lucky_direction']}")
    print(f"適合: {', '.join(fortune['suitable'])}")
    print(f"不適合: {', '.join(fortune['unsuitable'])}")
    print(f"建議: {fortune['advice']}")
