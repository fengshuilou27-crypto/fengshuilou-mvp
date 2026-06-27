import sys
from pathlib import Path
from collections import Counter

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

# User profile: 1991-03-04 18:55 男 香港 财运/健康/事业
USER_GENDER = "男"
USER_BIRTH_DATE = "1991-03-04"
USER_BIRTH_TIME = "18:55"
USER_GOALS = [
    {"goal": "財富", "priority": 1},
    {"goal": "健康", "priority": 2},
    {"goal": "事業", "priority": 2},
]

estates = load_estates()

report = []
report.append("=" * 60)
report.append("用戶真實資料匹配報告")
report.append("=" * 60)
report.append(f"性別: {USER_GENDER}")
report.append(f"出生日期: {USER_BIRTH_DATE}")
report.append(f"出生時間: {USER_BIRTH_TIME}")
report.append(f"目標: 財富(主) / 健康(次) / 事業(次)")
report.append(f"數據庫: {len(estates)} 個屋苑")
report.append("")

# Run bazi analysis standalone for user info
bazi_info = analyze_bazi(
    birth_date=USER_BIRTH_DATE,
    floor_number=10,
    birth_time=USER_BIRTH_TIME
)
report.append("=" * 60)
report.append("八字分析")
report.append("=" * 60)
report.append(bazi_info.get("rationale", ""))
report.append("")

# Run matches
results = []
errors = 0
for estate in estates:
    try:
        building_year = int(estate.get("year_built", 2000))
        building_facing = estate["facing"]
        
        flying_star_result = analyze_flying_star(
            building_year=building_year, building_facing=building_facing, eval_year=2026)
        zero_main_god_result = analyze_zero_main_god(
            building_year=building_year, north_has_water=False, south_has_mountain=False)
        sha_result = analyze_sha(detected_shas=[])
        bazi_result = analyze_bazi(
            birth_date=USER_BIRTH_DATE, floor_number=10, birth_time=USER_BIRTH_TIME)
        bagua_result = analyze_bagua(
            birth_date=USER_BIRTH_DATE, gender=USER_GENDER, building_facing=building_facing)
        goal_result = analyze_goal(
            building_year=building_year, building_facing=building_facing,
            goals=USER_GOALS)
        match_result = aggregate_match_result(
            flying_star_result=flying_star_result,
            zero_main_god_result=zero_main_god_result,
            sha_result=sha_result,
            bazi_result=bazi_result,
            bagua_result=bagua_result,
            goal_result=goal_result,
            district=estate.get("district", ""))
        
        results.append({
            "estate": estate["name"],
            "district": estate.get("district", ""),
            "facing": estate["facing"],
            "year_built": building_year,
            "yun": get_yun(building_year),
            "final_score": match_result["final_score"],
            "rating": match_result["rating"],
            "score_breakdown": match_result["score_breakdown"],
        })
    except Exception as e:
        errors += 1

results.sort(key=lambda x: x["final_score"], reverse=True)

report.append(f"匹配成功: {len(results)} 個屋苑, 錯誤: {errors}")
report.append("")

report.append("=" * 60)
report.append("Top 10 推薦")
report.append("=" * 60)
for i, r in enumerate(results[:10], 1):
    report.append(f"{i}. {r['estate']}")
    report.append(f"   地區: {r['district']} | 坐向: {r['facing']} | 年份: {r['year_built']}年/{r['yun']}")
    report.append(f"   總分: {r['final_score']:.1f}")
    sb = r['score_breakdown']
    report.append(f"   分項: 飛星{sb['飛星']:.1f} 八字{sb['八字']:.1f} 八宅{sb['八宅']:.1f} 零正神{sb['零正神']:.1f} 目標{sb['目標']:.1f} 區位{sb['區位']:.1f} 煞氣{sb['煞氣']:.1f}")
    report.append("")

report.append("=" * 60)
report.append("Bottom 5 (最不推薦)")
report.append("=" * 60)
for i, r in enumerate(results[-5:], 1):
    report.append(f"{i}. {r['estate']} ({r['district']}) - {r['facing']} - {r['year_built']}年/{r['yun']} - {r['final_score']:.1f}")

if results:
    scores = [r['final_score'] for r in results]
    report.append("")
    report.append(f"分數範圍: {min(scores):.1f} - {max(scores):.1f}, 平均: {sum(scores)/len(scores):.1f}")

# Analyze score distribution by facing
report.append("")
report.append("=" * 60)
report.append("坐向統計分析")
report.append("=" * 60)

facing_scores = {}
for r in results:
    f = r['facing']
    if f not in facing_scores:
        facing_scores[f] = []
    facing_scores[f].append(r['final_score'])

for f in sorted(facing_scores.keys()):
    sc = facing_scores[f]
    report.append(f"{f}: 平均 {sum(sc)/len(sc):.1f} (範圍 {min(sc):.1f}-{max(sc):.1f}, {len(sc)}個)")

with open('user_match_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Report saved to user_match_report.txt ({len(results)} estates matched)")
