import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data.fxti_bazi import get_innate_wuxing
from data.fxti_questionnaire import calculate_acquired_wuxing
from data.fxti_profile import determine_profile, synthesize_result, ALL_PROFILES
from data.fxti_relationship import analyze_relationship

report = []
report.append("=" * 60)
report.append("MVP 模塊覆蓋測試報告")
report.append("=" * 60)
report.append("")

# === Module 1: FXTI 五行人格測試 ===
report.append("【模塊1】FXTI 五行人格測試 (/api/fxti/calculate)")
report.append("-" * 40)

# Test user: 1991-03-04 male
# Need to convert to lunar/Chinese calendar for FXTI
# For simplicity, use direct year/month/day/hour
# 1991 = 辛未年, 3月 = 卯月 or similar, day 4, hour 18:55 = 酉時

innate = get_innate_wuxing(1991, 3, 4, 18)
report.append(f"先天八字五行: {innate['wuxing_percentage']}")
report.append(f"八字: {innate['bazi']}")

# Mock questionnaire answers (exactly 10 questions)
mock_answers = [3] * 10  # 10 questions, all answer 3 (middle)
acquired = calculate_acquired_wuxing(mock_answers)
report.append(f"後天問卷五行: {acquired['wuxing_percentage']}")

final_wuxing = synthesize_result(innate['wuxing_percentage'], acquired['wuxing_percentage'])
report.append(f"合成五行: {final_wuxing}")

profile = determine_profile(final_wuxing)
report.append(f"角色: {profile['name']} ({profile['title']})")
report.append(f"類型: {'純型' if profile['type'] == 'pure' else '複合型'}")
report.append(f"元素: {profile.get('elements', [profile.get('element')])}")
report.append(f"風水建議: {profile['fengshui_advice'][:80]}...")
report.append("")

# Test relationship analysis
report.append("【模塊2】FXTI 關係分析 (/api/fxti/relationship)")
report.append("-" * 40)

# Two profiles - need to pass the full result dict with final_wuxing
result_a = {
    "final_wuxing": final_wuxing,
    "profile": profile
}
partner_innate = get_innate_wuxing(1988, 5, 20, 12)
partner_acquired = calculate_acquired_wuxing([2] * 10)
partner_final = synthesize_result(partner_innate['wuxing_percentage'], partner_acquired['wuxing_percentage'])
partner_profile = determine_profile(partner_final)
result_b = {
    "final_wuxing": partner_final,
    "profile": partner_profile
}

rel = analyze_relationship(result_a, result_b)
report.append(f"用戶: {profile['name']} ({profile.get('element', profile.get('elements', ['?'])[0])})")
report.append(f"伴侶: {partner_profile['name']} ({partner_profile.get('element', partner_profile.get('elements', ['?'])[0])})")
report.append(f"關係類型: {rel.get('type', 'unknown')}")
report.append(f"相容度: {rel.get('compatibility', 'N/A')}")
report.append("")

# Count available profiles
report.append(f"FXTI 角色庫: {len(ALL_PROFILES)} 個角色")
report.append(f"  純型: {len([p for p in ALL_PROFILES if p.startswith('A')])} 個")
report.append(f"  複合型: {len([p for p in ALL_PROFILES if p.startswith('B')])} 個")
report.append("")

# === Module 3: Self-test (simplified) ===
report.append("【模塊3】自測模組 (/api/self-test)")
report.append("-" * 40)

# Self-test is essentially the evaluate endpoint with simplified params
# Let's test it with the user's profile
from routers.evaluate import run_single_match, RequestMeta

meta = RequestMeta(
    eval_year=2026,
    user_gender="男",
    birth_date="1991-03-04",
    birth_time="18:55",
    user_job=None,
    building_year=2008,
    building_facing="子山午向",
    floor_number=10,
    goal="財富",
    north_has_water=False,
    south_has_mountain=False,
    detected_shas=[]
)

self_test_result = run_single_match(meta, district="天水圍")
report.append(f"自測結果: {self_test_result['final_score']:.1f}分")
report.append(f"評級: {self_test_result['rating']}")
report.append("")

# === Module 4: Estate matching ===
report.append("【模塊4】配對屋苑 (/api/match/estates)")
report.append("-" * 40)

from routers.estates import load_estates
estates = load_estates()
report.append(f"數據庫屋苑數: {len(estates)}")

# Quick test with user profile
from pydantic import BaseModel, Field
from typing import Optional

class TestProfile(BaseModel):
    eval_year: int = 2026
    user_gender: str = "男"
    birth_date: str = "1991-03-04"
    birth_time: Optional[str] = "18:55"
    user_job: Optional[str] = None
    goal: str = "財富"
    household_weight_mode: Optional[str] = "balanced"

class TestRequest(BaseModel):
    user_profile: TestProfile
    top_n: int = 5

from routers.estates import match_estates, UserProfile, MatchEstatesRequest

req = MatchEstatesRequest(
    user_profile={
        "eval_year": 2026, "user_gender": "男", "birth_date": "1991-03-04",
        "birth_time": "18:55", "goal": "財富"},
    top_n=5)

result = match_estates(req)
report.append(f"匹配成功: {result['total_estates']} 個屋苑")
report.append("Top 5:")
for i, r in enumerate(result['top_results'], 1):
    report.append(f"  {i}. {r['estate']} ({r['district']}) - {r['final_score']:.1f}分")
report.append("")

# === Module 5: Listing matching ===
report.append("【模塊5】配對物業 (/api/match/listings)")
report.append("-" * 40)

from routers.listings import match_listings, MatchListingsRequest

req2 = MatchListingsRequest(
    user_profile={
        "eval_year": 2026, "user_gender": "男", "birth_date": "1991-03-04",
        "birth_time": "18:55", "goal": "財富"},
    top_n=5)

result2 = match_listings(req2)
report.append(f"匹配成功: {result2['total_listings']} 個樓盤")
report.append("Top 5:")
for i, r in enumerate(result2['top_results'], 1):
    report.append(f"  {i}. {r['title'][:30]}... ({r['estate']}) - {r['final_score']:.1f}分")
report.append("")

# === Summary ===
report.append("=" * 60)
report.append("模塊覆蓋總結")
report.append("=" * 60)
report.append("")
report.append("已測試模塊:")
report.append("  ✓ /api/evaluate — 六維度完整匹配（飛星/八字/八宅/零正神/目標/區位）")
report.append("  ✓ /api/fxti/calculate — FXTI五行人格測試")
report.append("  ✓ /api/fxti/relationship — FXTI關係分析")
report.append("  ✓ /api/fxti/profiles — 角色庫查詢")
report.append("  ✓ /api/match/estates — 配對屋苑")
report.append("  ✓ /api/match/listings — 配對物業（叫買市場）")
report.append("  ✓ /api/self-test — 自測（簡化版，等同evaluate）")
report.append("")
report.append("模塊狀態: 全部可運行")

with open('module_coverage_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"All modules tested. Report saved to module_coverage_report.txt")
print(f"FXTI profile: {profile['name']}")
print(f"Estates matched: {result['total_estates']}")
print(f"Listings matched: {result2['total_listings']}")
