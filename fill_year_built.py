import csv, json, os, sys
import shutil

# Load lookup table
with open('estate_year_lookup.json', 'r', encoding='utf-8') as f:
    lookup = json.load(f)

# Backup original CSV
shutil.copy('data/listings_28hse.csv', 'data/listings_28hse.csv.bak')

# Read CSV
with open('data/listings_28hse.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    headers = rows[0].keys() if rows else []

# Fill missing year_built from lookup or defaults
filled_count = 0
default_count = 0
for r in rows:
    yb = r.get('year_built', '').strip()
    if not yb:
        estate = r['estate'].strip()
        if estate in lookup:
            r['year_built'] = str(lookup[estate])
            filled_count += 1
        elif '村屋' in estate or not estate:
            # Default for village houses or missing estate names
            r['year_built'] = '2000'
            default_count += 1

# Write updated CSV
with open('data/listings_28hse.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

# Count stats
with open('data/listings_28hse.csv', 'r', encoding='utf-8') as f:
    rows_after = list(csv.DictReader(f))

total = len(rows_after)
has_year = sum(1 for r in rows_after if r.get('year_built', '').strip())
missing = total - has_year

print(f'Filled {filled_count} entries from lookup table')
print(f'Filled {default_count} entries with default (2000)')
print(f'Total: {total}, Has year_built: {has_year}, Missing: {missing}')
print(f'Coverage: {has_year/total*100:.1f}%')
