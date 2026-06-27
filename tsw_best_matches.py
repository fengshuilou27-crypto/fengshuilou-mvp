import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data.flying_star import get_yun
from models.flying_star_analysis import analyze_flying_star
from models.zero_main_god import analyze_zero_main_god
from models.sha_assessment import analyze_sha
from models.bazi_matching import analyze_bazi
from models.bagua_matching import analyze_bagua
from models.goal_matching import analyze_goal
from models.match_result import aggregate_match_result

# Find Tin Shui Wai estates
import csv
tsw_estates = []
with open(Path(__file__).parent.parent / 'scraper_28hse' / 'data' / 'estates_28hse.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if '天水圍' in row.get('district', ''):
            tsw_estates.append(row)

report = []
report.append("天水圍屋苑列表：")
for e in tsw_estates:
    report.append(f"  {e['name']} | {e['facing']} | {e['year_built']}年 | {e['yun']}")
report.append("")

# Test multiple birth dates to find who scores high with Tin Shui Wai
# We need to find people whose 命卦 matches the estate facing

test_profiles = [
    # 东四命 - 离卦/巽卦/震卦/坎卦 = should match 子山午向/卯山酉向/午山子向/巽山乾向
    {"gender": "男", "birth": "1991-03-04", "time": None, "desc": "1991男(辛未) - 已知东四命/离卦"},
    {"gender": "男", "birth": "1984-02-15", "time": None, "desc": "1984男(甲子) - 东四命测试"},
    {"gender": "女", "birth": "1988-05-20", "time": None, "desc": "1988女(戊辰) - 东四命测试"},
    {"gender": "男", "birth": "1976-07-16", "time": None, "desc": "1976男(丙辰) - 已知西四命/乾卦"},
    {"gender": "男", "birth": "1985-10-10", "time": None, "desc": "1985男(乙丑) - 西四命测试"},
    {"gender": "女", "birth": "1993-08-08", "time": None, "desc": "1993女(癸酉) - 西四命测试"},
    {"gender": "男", "birth": "1970-01-01", "time": None, "desc": "1970男(庚戌) - 西四命测试"},
    {"gender": "男", "birth": "1995-12-01", "time": None, "desc": "1995男(乙亥) - 东四命测试"},
]

report.append("=" * 60)
report.append("測試不同八字在天水圍的分數")
report.append("=" * 60)
report.append("")

for profile in test_profiles:
    report.append(f"--- {profile['desc']} ---")
    
    # Check bagua (命卦)
    bagua_test = analyze_bagua(birth_date=profile['birth'], gender=profile['gender'], building_facing="子山午向")
    ming_gua = "東四命" if bagua_test.get('score', 0) >= 10 else "西四命"
    report.append(f"  命卦: {ming_gua} (八宅測試得分: {bagua_test.get('score', 0)})")
    
    best_score = 0
    best_estate = None
    
    for estate in tsw_estates:
        try:
            year = int(estate['year_built'])
            facing = estate['facing']
            
            fs = analyze_flying_star(building_year=year, building_facing=facing, eval_year=2026)
            zmg = analyze_zero_main_god(building_year=year, north_has_water=False, south_has_mountain=False)
            sha = analyze_sha(detected_shas=[])
            bazi_r = analyze_bazi(birth_date=profile['birth'], floor_number=10, birth_time=profile['time'])
            bagua_r = analyze_bagua(birth_date=profile['birth'], gender=profile['gender'], building_facing=facing)
            goal = analyze_goal(building_year=year, building_facing=facing, 
                                goals=[{"goal": "財富", "priority": 1}])
            
            result = aggregate_match_result(
                flying_star_result=fs, zero_main_god_result=zmg, sha_result=sha,
                bazi_result=bazi_r, bagua_result=bagua_r, goal_result=goal,
                district="天水圍")
            
            if result['final_score'] > best_score:
                best_score = result['final_score']
                best_estate = estate['name']
            
        except:
            pass
    
    report.append(f"  在天水圍最高分: {best_score:.1f} ({best_estate})")
    report.append("")

# Now find the BEST birth date for Tin Shui Wai
# We need someone whose 命卦 matches 午山子向 (坎卦=东四命) or 子山午向 (离卦=东四命)
# Let's test a few specific good matches

report.append("=" * 60)
report.append("最佳匹配案例：天水圍 + 高分八字")
report.append("=" * 60)
report.append("")

best_matches = [
    # For 栢慧豪園 (午山子向, 2008/八運) - 坎卦宅 = 东四命, 配离卦/巽卦/震卦人
    {"estate": "栢慧豪園", "facing": "午山子向", "year": 2008, 
     "profile": {"gender": "男", "birth": "1991-03-04", "floor": 1, "goal": "財富"},
     "desc": "1991男 + 栢慧豪園(午山子向) + 1樓"},
    
    # For 栢慧豪園 with 午山子向 - 配坎卦人 (东四命)
    {"estate": "栢慧豪園", "facing": "午山子向", "year": 2008,
     "profile": {"gender": "男", "birth": "1984-02-15", "floor": 1, "goal": "財富"},
     "desc": "1984男 + 栢慧豪園(午山子向) + 1樓"},
    
    # For 嘉湖山莊 (艮山坤向, 1992/七運) - 艮卦=西四命, 配乾卦/坤卦/艮卦/兑卦人
    {"estate": "嘉湖山莊", "facing": "艮山坤向", "year": 1992,
     "profile": {"gender": "男", "birth": "1976-07-16", "floor": 1, "goal": "財富"},
     "desc": "1976男 + 嘉湖山莊(艮山坤向) + 1樓"},
     
    # Test with different floors
    {"estate": "栢慧豪園", "facing": "午山子向", "year": 2008,
     "profile": {"gender": "男", "birth": "1991-03-04", "floor": 10, "goal": "財富"},
     "desc": "1991男 + 栢慧豪園 + 10樓(對比)"},
]

for case in best_matches:
    p = case['profile']
    report.append(f"--- {case['desc']} ---")
    
    fs = analyze_flying_star(building_year=case['year'], building_facing=case['facing'], eval_year=2026)
    zmg = analyze_zero_main_god(building_year=case['year'], north_has_water=False, south_has_mountain=False)
    sha = analyze_sha(detected_shas=[])
    bazi_r = analyze_bazi(birth_date=p['birth'], floor_number=p['floor'], birth_time=None)
    bagua_r = analyze_bagua(birth_date=p['birth'], gender=p['gender'], building_facing=case['facing'])
    goal = analyze_goal(building_year=case['year'], building_facing=case['facing'], 
                        goals=[{"goal": p['goal'], "priority": 1}])
    
    result = aggregate_match_result(
        flying_star_result=fs, zero_main_god_result=zmg, sha_result=sha,
        bazi_result=bazi_r, bagua_result=bagua_r, goal_result=goal,
        district="天水圍")
    
    report.append(f"  總分: {result['final_score']:.1f}")
    sb = result['score_breakdown']
    report.append(f"  飛星: {sb['飛星']:.1f} | 八字: {sb['八字']:.1f} | 八宅: {sb['八宅']:.1f}")
    report.append(f"  零正神: {sb['零正神']:.1f} | 目標: {sb['目標']:.1f} | 區位: {sb['區位']:.1f}")
    report.append("")

with open('tsw_best_matches.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print("Report saved to tsw_best_matches.txt")
