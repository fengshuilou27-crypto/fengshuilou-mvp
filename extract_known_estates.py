#!/usr/bin/env python3
"""
Extract KNOWN_ESTATES from scraper_28hse_estates_v2.py 
and convert to estates_28hse.csv format.
"""

import csv
import re
from collections import Counter
from pathlib import Path

v2_path = Path(__file__).parent.parent / "scraper_28hse" / "scraper_28hse_estates_v2.py"
with open(v2_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract KNOWN_ESTATES list - find between the list start and the yun calc section
start_marker = "KNOWN_ESTATES = ["
end_marker = "# ============== 風水運計算 =============="

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find KNOWN_ESTATES")
    exit(1)

# Extract the list content
list_content = content[start_idx:end_idx]

# Parse each estate dict using regex
# Pattern matches: {"name": "...", "district": "...", ...}
estates = []

# Split by lines and find dict blocks
depth = 0
current = []
for line in list_content.split('\n'):
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        continue
    
    # Count braces to track dict boundaries
    for char in line:
        if char == '{':
            if depth == 0:
                current = []
            depth += 1
        if depth > 0:
            current.append(char)
        if char == '}':
            depth -= 1
            if depth == 0:
                # We have a complete dict
                dict_str = ''.join(current)
                # Parse key-value pairs
                estate = {}
                # Match "key": "value" or "key": number or "key": [...]
                # Simple regex approach for string values
                for match in re.finditer(r'"(\w+)":\s*"([^"]*)"', dict_str):
                    estate[match.group(1)] = match.group(2)
                # Match numeric values
                for match in re.finditer(r'"(\w+)":\s*(\d+)', dict_str):
                    key = match.group(1)
                    if key not in estate:  # Don't overwrite string matches
                        try:
                            estate[key] = int(match.group(2))
                        except:
                            pass
                if estate.get('name'):
                    estates.append(estate)

print(f"Extracted {len(estates)} estates")

# Convert to matching system format
output_estates = []
for e in estates:
    year = e.get('year_built', 0)
    if isinstance(year, str):
        try:
            year = int(year)
        except:
            year = 0
    
    # Calculate yun
    if 1964 <= year <= 1983:
        yun = "六運"
    elif 1984 <= year <= 2003:
        yun = "七運"
    elif 2004 <= year <= 2023:
        yun = "八運"
    elif 2024 <= year <= 2043:
        yun = "九運"
    else:
        yun = "未知"
    
    output_estates.append({
        'name': e['name'],
        'district': e.get('district', ''),
        'property_type': e.get('property_type', '私人屋苑'),
        'source_listings': 1,
        'facing': e.get('facing', ''),
        'year_built': year,
        'yun': yun,
    })

# Analysis
report = []
report.append(f"=== Analysis ===")
report.append(f"Total estates: {len(output_estates)}")

facings = [e['facing'] for e in output_estates if e['facing']]
report.append(f"\nFacing distribution ({len(facings)} with facing):")
for facing, count in Counter(facings).most_common():
    report.append(f"  {facing}: {count}")

years = [e['year_built'] for e in output_estates if e['year_built']]
report.append(f"\nYear range: {min(years)} - {max(years)}")

yuns = [e['yun'] for e in output_estates]
report.append(f"\nYun distribution:")
for yun, count in Counter(yuns).most_common():
    report.append(f"  {yun}: {count}")

districts = [e['district'] for e in output_estates if e['district']]
report.append(f"\nDistricts covered: {len(set(districts))}")
for district, count in Counter(districts).most_common(15):
    report.append(f"  {district}: {count}")

with open('estate_extract_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

# Save to CSV
data_dir = Path(__file__).parent.parent / "scraper_28hse" / "data"
data_dir.mkdir(exist_ok=True)

output_path = data_dir / "estates_28hse.csv"
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'district', 'property_type', 'source_listings', 'facing', 'year_built', 'yun'])
    writer.writeheader()
    for e in output_estates:
        writer.writerow(e)

print(f"Extracted {len(output_estates)} estates")
print(f"Saved to {output_path}")
print(f"Report saved to estate_extract_report.txt")
