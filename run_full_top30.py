import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routers.estates import load_estates
from data.flying_star import get_yun
from models.flying_star_analysis import analyze_flying_star
from models.zero_main_god import analyze_zero_main_god
from models.sha_assessment import analyze_sha
from models.bazi_matching import analyze_bazi
from models.bagua_matching import analyze_bagua
from models.goal_matching import analyze_goal
from models.match_result import aggregate_match_result

# User: 1991-03-04 18:55 男 財富/健康/事業
estates = load_estates()

report = []
report.append("=" * 60)
report.append("全部屋苑匹配 — 1991-03-04 18:55 男")
report.append("=" * 60)
report.append(f"數據庫: {len(estates)} 個屋苑")
report.append("")

# Run full match
results = []
errors = []
for estate in estates:
    try:
        building_year = int(estate.get("year_built", 2000))
        building_facing = estate["facing"]
        
        flying_star_result = analyze_flying_star(
            building_year=building_year, building_facing=building_facing, eval_year=2026)
        zero_main_god_result = analyze_zero_main_god(
            building_year=building_year, building_facing=building_facing,
            north_has_water=False, south_has_mountain=False)
        sha_result = analyze_sha(detected_shas=[], flying_star_pan=flying_star_result)
        bazi_result = analyze_bazi(
            birth_date="1991-03-04", floor_number=10, birth_time="18:55", building_facing=building_facing)
        bagua_result = analyze_bagua(
            birth_date="1991-03-04", gender="男", building_facing=building_facing)
        goal_result = analyze_goal(
            building_year=building_year, building_facing=building_facing,
            goals=[{"goal": "財富", "priority": 1}, {"goal": "健康", "priority": 2}, {"goal": "事業", "priority": 2}])
        
        match_result = aggregate_match_result(
            flying_star_result=flying_star_result,
            zero_main_god_result=zero_main_god_result,
            sha_result=sha_result,
            bazi_result=bazi_result,
            bagua_result=bagua_result,
            goal_result=goal_result,
            district=estate.get("district", ""),
            building_year=building_year,
            building_facing=building_facing,
            property_features={'age': 2026 - building_year},
            floor_number=10)
        
        results.append({
            "estate": estate["name"],
            "district": estate.get("district", ""),
            "facing": estate["facing"],
            "year_built": building_year,
            "yun": get_yun(building_year),
            "final_score": match_result["final_score"],
            "score_breakdown": match_result["score_breakdown"],
        })
    except Exception as e:
        errors.append(f"{estate.get('name', '?')}: {e}")

results.sort(key=lambda x: x["final_score"], reverse=True)

report.append(f"匹配成功: {len(results)} / {len(estates)}")
if errors:
    report.append(f"錯誤: {len(errors)} 個")
report.append("")

report.append("=" * 60)
report.append("Top 30 推薦")
report.append("=" * 60)
for i, r in enumerate(results[:30], 1):
    sb = r['score_breakdown']
    report.append(f"{i:2}. {r['estate']:<12} ({r['district']:<8}) {r['facing']:<8} {r['year_built']}年/{r['yun']:<3} | 總分:{r['final_score']:5.1f} | 飛星{sb['飛星']:4.1f} 八字{sb['八字']:4.1f} 八宅{sb['八宅']:4.1f} 煞防{sb['煞氣防禦']:4.1f}")

report.append("")
report.append("=" * 60)
report.append("Bottom 10")
report.append("=" * 60)
for i, r in enumerate(results[-10:], 1):
    report.append(f"{i:2}. {r['estate']:<12} ({r['district']:<8}) {r['facing']:<8} {r['year_built']}年/{r['yun']:<3} | 總分:{r['final_score']:5.1f}")

report.append("")
report.append(f"分數範圍: {results[-1]['final_score']:.1f} - {results[0]['final_score']:.1f}")
report.append(f"平均分: {sum(r['final_score'] for r in results)/len(results):.1f}")

with open('full_top30_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Full match complete. {len(results)} estates. Top 30 saved.")
