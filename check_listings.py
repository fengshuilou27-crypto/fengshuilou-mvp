import csv

from pathlib import Path

csv_path = Path(__file__).parent.parent / "scraper_28hse" / "data" / "listings_28hse.csv"
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    listings = list(reader)

# Find 曉峰閣
report = []
report.append(f"Total listings: {len(listings)}")
report.append("")

report.append("=== 曉峰閣 in listings ===")
for row in listings:
    if '曉峰閣' in row.get('estate', ''):
        report.append(f"Estate: {row['estate']}, Facing: {row['facing']}, Year: {row['year_built']}, District: {row['district']}")

report.append("")
report.append("=== Top estates by listing count ===")
from collections import Counter
counts = Counter([r['estate'] for r in listings])
for estate, count in counts.most_common(20):
    report.append(f"{estate}: {count}")

report.append("")
report.append("=== Facing distribution in listings ===")
facing_counts = Counter([r['facing'] for r in listings if r.get('facing')])
for facing, count in facing_counts.most_common():
    report.append(f"{facing}: {count}")

report.append("")
report.append("=== Year distribution in listings ===")
year_counts = Counter([r['year_built'] for r in listings if r.get('year_built')])
for year, count in year_counts.most_common():
    report.append(f"{year}: {count}")

with open('listings_analysis.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Analysis saved. Total: {len(listings)} listings")
