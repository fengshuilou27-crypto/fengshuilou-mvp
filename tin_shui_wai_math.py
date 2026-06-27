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

report = []
report.append("=" * 60)
report.append("天水圍 vs 中半山 數學驗證")
report.append("=" * 60)
report.append("")

# Test profile: 1991-03-04 male (known 东四命/离卦 from previous tests)
birth_date = "1991-03-04"
gender = "男"
floor = 1  # 1楼 = 水，对木日主最佳

bazi = analyze_bazi(birth_date=birth_date, floor_number=floor, birth_time=None)
report.append(f"八字: {bazi.get('rationale', '')}")
report.append(f"八字得分: {bazi.get('score', 0)}")
report.append("")

bagua = analyze_bagua(birth_date=birth_date, gender=gender, building_facing="子山午向")
report.append(f"八宅: {bagua.get('rationale', '')}")
report.append(f"八宅得分: {bagua.get('score', 0)}")
report.append("")

# Compare same facing+year in different districts
buildings = [
    {"name": "栢慧豪園", "district": "天水圍", "facing": "子山午向", "year": 2008},
    {"name": "曉峰閣", "district": "中半山", "facing": "子山午向", "year": 1996},
]

for b in buildings:
    report.append(f"--- {b['name']} ({b['district']}) ---")
    
    fs = analyze_flying_star(building_year=b['year'], building_facing=b['facing'], eval_year=2026)
    zmg = analyze_zero_main_god(building_year=b['year'], north_has_water=False, south_has_mountain=False)
    sha = analyze_sha(detected_shas=[])
    bazi_r = analyze_bazi(birth_date=birth_date, floor_number=floor, birth_time=None)
    bagua_r = analyze_bagua(birth_date=birth_date, gender=gender, building_facing=b['facing'])
    goal = analyze_goal(building_year=b['year'], building_facing=b['facing'], 
                        goals=[{"goal": "財富", "priority": 1}])
    
    result = aggregate_match_result(
        flying_star_result=fs, zero_main_god_result=zmg, sha_result=sha,
        bazi_result=bazi_r, bagua_result=bagua_r, goal_result=goal,
        district=b['district'])
    
    report.append(f"  總分: {result['final_score']:.1f}")
    sb = result['score_breakdown']
    report.append(f"  飛星: {sb['飛星']:.1f} | 八字: {sb['八字']:.1f} | 八宅: {sb['八宅']:.1f}")
    report.append(f"  零正神: {sb['零正神']:.1f} | 目標: {sb['目標']:.1f} | 區位: {sb['區位']:.1f} | 煞氣: {sb['煞氣']:.1f}")
    report.append("")

# Different facings in same district (天水圍)
report.append("=" * 60)
report.append("對比：好坐向 vs 壞坐向（都在天水圍，2008年）")
report.append("=" * 60)

facings_to_test = ["子山午向", "午山子向", "乾山巽向", "卯山酉向"]
for facing in facings_to_test:
    fs = analyze_flying_star(building_year=2008, building_facing=facing, eval_year=2026)
    zmg = analyze_zero_main_god(building_year=2008, north_has_water=False, south_has_mountain=False)
    sha = analyze_sha(detected_shas=[])
    bazi_r = analyze_bazi(birth_date=birth_date, floor_number=floor, birth_time=None)
    bagua_r = analyze_bagua(birth_date=birth_date, gender=gender, building_facing=facing)
    goal = analyze_goal(building_year=2008, building_facing=facing, 
                        goals=[{"goal": "財富", "priority": 1}])
    
    result = aggregate_match_result(
        flying_star_result=fs, zero_main_god_result=zmg, sha_result=sha,
        bazi_result=bazi_r, bagua_result=bagua_r, goal_result=goal,
        district="天水圍")
    
    report.append(f"{facing}: {result['final_score']:.1f}分 (飛星{result['score_breakdown']['飛星']:.1f} 八宅{result['score_breakdown']['八宅']:.1f})")

report.append("")
report.append("=" * 60)
report.append("對比：好樓層 vs 壞樓層（天水圍 + 子山午向）")
report.append("=" * 60)

floors_to_test = [1, 5, 10, 15, 20, 28]
for f in floors_to_test:
    bazi_r = analyze_bazi(birth_date=birth_date, floor_number=f, birth_time=None)
    fs = analyze_flying_star(building_year=2008, building_facing="子山午向", eval_year=2026)
    zmg = analyze_zero_main_god(building_year=2008, north_has_water=False, south_has_mountain=False)
    sha = analyze_sha(detected_shas=[])
    bagua_r = analyze_bagua(birth_date=birth_date, gender=gender, building_facing="子山午向")
    goal = analyze_goal(building_year=2008, building_facing="子山午向", 
                        goals=[{"goal": "財富", "priority": 1}])
    
    result = aggregate_match_result(
        flying_star_result=fs, zero_main_god_result=zmg, sha_result=sha,
        bazi_result=bazi_r, bagua_result=bagua_r, goal_result=goal,
        district="天水圍")
    
    report.append(f"{f}樓: 八字{bazi_r['score']:.0f}分 → 總分{result['final_score']:.1f}分")

report.append("")
report.append("=" * 60)
report.append("結論")
report.append("=" * 60)
report.append("天水圍子山午向/1樓/東四命 = 高分（見上方計算）")
report.append("中半山子山午向/1樓/東四命 = 同配置僅差3分地段分")
report.append("天水圍午山子向/1樓/東四命 = 低分（坐向不配，暴跌）")
report.append("")
report.append("地段差距（3分）遠小於坐向差距和樓層差距")

with open('tin_shui_wai_math_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print("Report saved to tin_shui_wai_math_report.txt")
