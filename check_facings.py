import csv
from pathlib import Path

# Load supported facings
import sys
sys.path.insert(0, str(Path(__file__).parent))
from data.flying_star import SUPPORTED_FACINGS

# Load estates
estates_path = Path(__file__).parent.parent / "scraper_28hse" / "data" / "estates_28hse.csv"
with open(estates_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    all_estates = list(reader)

# Filter like estates.py does
filtered = [e for e in all_estates if e.get("facing") in SUPPORTED_FACINGS]
filtered_out = [e for e in all_estates if e.get("facing") not in SUPPORTED_FACINGS]

report = []
report.append(f"Total estates in CSV: {len(all_estates)}")
report.append(f"Supported facings count: {len(SUPPORTED_FACINGS)}")
report.append(f"Estates with supported facing: {len(filtered)}")
report.append(f"Estates filtered OUT: {len(filtered_out)}")

report.append(f"\nSupported facings ({len(SUPPORTED_FACINGS)}):")
for f in sorted(SUPPORTED_FACINGS):
    report.append(f"  {f}")

if filtered_out:
    report.append(f"\nFiltered out estates:")
    for e in filtered_out:
        report.append(f"  {e['name']} - facing: '{e.get('facing', '')}'")

with open('facing_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Total: {len(all_estates)}, Supported: {len(filtered)}, Filtered: {len(filtered_out)}")
print("Report saved to facing_check.txt")
