import json
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

def run_single_test(estates, gender, birth_date, birth_time, goal, report):
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
                birth_date=birth_date, floor_number=10, birth_time=birth_time)
            bagua_result = analyze_bagua(
                birth_date=birth_date, gender=gender, building_facing=building_facing)
            goal_result = analyze_goal(
                building_year=building_year, building_facing=building_facing,
                goals=[{"goal": goal, "priority": 1}])
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
            })
        except Exception as e:
            errors += 1
    
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    report.append(f"Matched: {len(results)} estates, Errors: {errors}")
    report.append(f"Top 10:")
    for i, r in enumerate(results[:10], 1):
        report.append(f"  {i}. {r['estate']} ({r['district']}) - {r['facing']} - {r['year_built']}年/{r['yun']} - {r['final_score']:.1f}")
    
    report.append(f"Bottom 3:")
    for i, r in enumerate(results[-3:], 1):
        report.append(f"  {i}. {r['estate']} ({r['district']}) - {r['facing']} - {r['year_built']}年/{r['yun']} - {r['final_score']:.1f}")
    
    if results:
        scores = [r['final_score'] for r in results]
        report.append(f"Score range: {min(scores):.1f} - {max(scores):.1f}, Avg: {sum(scores)/len(scores):.1f}")
    report.append("")
    return results

# Load estates
estates = load_estates()

report = []
report.append(f"=== Expanded Estate Database Test ===")
report.append(f"Total estates loaded: {len(estates)}")

facings = [e['facing'] for e in estates]
report.append(f"Facing distribution:")
for facing, count in Counter(facings).most_common():
    report.append(f"  {facing}: {count}")

yuns = [e['yun'] for e in estates]
report.append(f"Yun distribution:")
for yun, count in Counter(yuns).most_common():
    report.append(f"  {yun}: {count}")

districts = [e['district'] for e in estates]
report.append(f"District distribution ({len(set(districts))} districts):")
for district, count in Counter(districts).most_common(15):
    report.append(f"  {district}: {count}")

# Test 1: 男/1976-07-16/事業
report.append(f"{'='*50}")
report.append(f"Test 1: 男/1976-07-16/事業")
report.append(f"{'='*50}")
run_single_test(estates, "男", "1976-07-16", None, "事業", report)

# Test 2: 男/1991-03-04/財富
report.append(f"{'='*50}")
report.append(f"Test 2: 男/1991-03-04/財富")
report.append(f"{'='*50}")
run_single_test(estates, "男", "1991-03-04", None, "財富", report)

with open('expanded_test_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Test complete. {len(estates)} estates.")
print("Results saved to expanded_test_results.txt")
