import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routers.listings import match_listings, MatchListingsRequest

# Test with same user profile
req = MatchListingsRequest(
    user_profile={
        "eval_year": 2026, "user_gender": "男", "birth_date": "1991-03-04",
        "birth_time": "18:55", "goal": "財富"},
    top_n=10)

result = match_listings(req)

report = []
report.append(f"Total listings matched: {result['total_listings']}")
report.append(f"Call buy triggered: {result['call_buy_market']['triggered']}")
report.append("")
report.append("Top 10 listings:")
for i, r in enumerate(result['top_results'], 1):
    report.append(f"{i}. {r['estate']} ({r['district']}) - {r['facing']} - {r['final_score']:.1f}分")
    sb = r['score_breakdown']
    report.append(f"   飛星{sb['飛星']:.1f} 八字{sb['八字']:.1f} 八宅{sb['八宅']:.1f} 區位{sb['區位']:.1f}")

# Check if 曉峰閣 is in top results
has_xiaofeng = any('曉峰閣' in r['estate'] for r in result['top_results'])
report.append("")
report.append(f"曉峰閣 in top 10: {has_xiaofeng}")

with open('listings_fixed_test.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Test complete. {result['total_listings']} listings. Report saved.")
