import csv
from collections import Counter

# 分析屋苑數據
with open('../scraper_28hse/data/estates_28hse.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    estates = list(reader)

# 分析樓盤數據
with open('../scraper_28hse/data/listings_28hse.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    listings = list(reader)

report = []
report.append("=== 屋苑數據分析 ===")
report.append(f"總屋苑數: {len(estates)}")

# 坐向分布
facings = [e['facing'] for e in estates]
report.append(f"\n坐向分布:")
for facing, count in Counter(facings).most_common():
    report.append(f"  {facing}: {count}")

# 年份分布
years = [int(e['year_built']) for e in estates]
report.append(f"\n年份範圍: {min(years)} - {max(years)}")

# 運分布
yuns = [e['yun'] for e in estates]
report.append(f"\n運分布:")
for yun, count in Counter(yuns).most_common():
    report.append(f"  {yun}: {count}")

# 地區分布
districts = [e['district'] for e in estates]
report.append(f"\n地區分布:")
for district, count in Counter(districts).most_common():
    report.append(f"  {district}: {count}")

# 物業類型
prop_types = [e['property_type'] for e in estates]
report.append(f"\n物業類型:")
for pt, count in Counter(prop_types).most_common():
    report.append(f"  {pt}: {count}")

# 數據完整性檢查
report.append("\n=== 數據完整性 ===")
for field in ['name', 'district', 'property_type', 'facing', 'year_built', 'yun']:
    missing = sum(1 for e in estates if not e.get(field))
    report.append(f"{field}: {len(estates) - missing}/{len(estates)} ({(len(estates)-missing)/len(estates)*100:.0f}%)")

# 樓盤數據分析
report.append("\n=== 樓盤數據分析 ===")
report.append(f"總樓盤數: {len(listings)}")

# 每個屋苑有多少個樓盤
estate_listing_counts = Counter([l['estate'] for l in listings])
report.append(f"\n每屋苑平均樓盤數: {len(listings)/len(estate_listing_counts):.1f}")
report.append(f"有樓盤數據的屋苑數: {len(estate_listing_counts)}")

# 樓盤數據完整性
report.append("\n=== 樓盤數據完整性 ===")
for field in ['title', 'district', 'estate', 'price', 'facing', 'year_built', 'rooms']:
    missing = sum(1 for l in listings if not l.get(field))
    report.append(f"{field}: {len(listings) - missing}/{len(listings)} ({(len(listings)-missing)/len(listings)*100:.0f}%)")

# 香港主要屋苑參考數據
report.append("\n=== 覆蓋率評估 ===")
report.append("香港私人住宅屋苑總數估計: 3,000-5,000+")
report.append(f"當前覆蓋: {len(estates)} 個")
report.append(f"覆蓋率: ~{len(estates)/4000*100:.1f}% (以4,000為基準)")

# 地區覆蓋
total_districts = len(set(districts))
report.append(f"\n覆蓋地區數: {total_districts}")
report.append("主要地區都有覆蓋，但每個地區屋苑數很少")

with open('db_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(report))
print("Done")
