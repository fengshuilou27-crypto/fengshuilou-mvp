"""
28Hse Floor & Room Layout Scraper (Improved v2)
================================================
Better data quality: uses floor term mapping as fallback for narrow ranges.
Generates SQL for direct database update.

Usage:
    python scraper_28hse_floor_v2.py --generate-sql > update_floor.sql
"""

import csv
import re
import os
import json
import argparse
from collections import defaultdict, Counter

FLOOR_PATTERN_MAP = {
    '高層': ('15-30', 'high_floor'),
    '中層': ('8-14', 'mid_floor'),
    '低層': ('1-7', 'low_floor'),
    '全幢': ('1-30', 'whole_building'),
    '地下': ('0', 'ground_floor'),
    'G層': ('0', 'ground_floor'),
    'G室': ('0', 'ground_floor'),
    '平台': ('0', 'platform'),
    '複式': ('1-2', 'duplex'),
    '相連': ('1-30', 'connected'),
    '獨立屋': ('1-3', 'house'),
}

NUMERIC_FLOOR_RE = re.compile(r'(\d+)(?:[樓層F\/]|座.*(?:高層|中層|低層))')
FLOOR_TERM_RE = re.compile(r'(高層|中層|低層|全幢|地下|G層|G室|平台|複式|相連|獨立屋)')
TOWER_RE = re.compile(r'(?:第?\d+[座期]|[A-Z]座)')
UNIT_RE = re.compile(r'([A-Z]\d?室|\d+室)')


def extract_floor_info(unit_info: str) -> dict:
    if not unit_info or unit_info.strip() == '':
        return None
    unit_info = unit_info.strip()
    result = {
        'raw': unit_info,
        'floor_term': None,
        'floor_term_en': None,
        'floor_range': None,
        'extracted_floor': None,
        'tower': None,
        'unit': None,
    }
    
    floor_match = FLOOR_TERM_RE.search(unit_info)
    if floor_match:
        term = floor_match.group(1)
        result['floor_term'] = term
        mapped = FLOOR_PATTERN_MAP.get(term)
        if mapped:
            result['floor_range'] = mapped[0]
            result['floor_term_en'] = mapped[1]
    
    numeric_match = NUMERIC_FLOOR_RE.search(unit_info)
    if numeric_match:
        floor_num = int(numeric_match.group(1))
        if 1 <= floor_num <= 100:
            result['extracted_floor'] = floor_num
    
    tower_match = TOWER_RE.search(unit_info)
    if tower_match:
        result['tower'] = tower_match.group(0)
    
    unit_match = UNIT_RE.search(unit_info)
    if unit_match:
        result['unit'] = unit_match.group(1)
    
    return result


def aggregate_floor_info(floor_infos: list) -> dict:
    if not floor_infos:
        return None
    
    term_counts = Counter()
    extracted_floors = []
    
    for info in floor_infos:
        if info.get('floor_term'):
            term_counts[info['floor_term']] += 1
        if info.get('extracted_floor') is not None:
            extracted_floors.append(info['extracted_floor'])
    
    if not term_counts and not extracted_floors:
        return None
    
    most_common_term = term_counts.most_common(1)[0][0] if term_counts else None
    
    # Determine best floor range
    if extracted_floors and len(set(extracted_floors)) >= 2:
        # Multiple different floors → use actual range
        min_floor = min(extracted_floors)
        max_floor = max(extracted_floors)
        floor_range = f"{min_floor}-{max_floor}"
    elif most_common_term:
        # Use term mapping (better than single floor for typical range)
        floor_range = FLOOR_PATTERN_MAP.get(most_common_term, ('', ''))[0]
    elif extracted_floors:
        # Single floor only, no term → use that floor
        floor_range = f"{extracted_floors[0]}-{extracted_floors[0]}"
    else:
        floor_range = None
    
    # Typical floor: median of extracted, or midpoint of range
    typical_floor = None
    if extracted_floors:
        typical_floor = sorted(extracted_floors)[len(extracted_floors)//2]
    elif floor_range and '-' in floor_range:
        parts = floor_range.split('-')
        try:
            typical_floor = (int(parts[0]) + int(parts[1])) // 2
        except:
            pass
    
    return {
        'floor_range': floor_range,
        'typical_floor': typical_floor,
        'most_common_term': most_common_term,
        'term_distribution': dict(term_counts),
        'extracted_floors': sorted(set(extracted_floors)) if extracted_floors else [],
        'listing_count': len(floor_infos),
    }


def extract_room_layout(row: dict) -> dict:
    rooms = row.get('rooms', '')
    unit_info = row.get('unit_info', '')
    title = row.get('title', '')
    
    layout = {
        'rooms': None,
        'bathrooms': None,
        'studio': False,
        'duplex': False,
        'with_rooftop': False,
        'with_platform': False,
    }
    
    if rooms:
        rooms_str = str(rooms).strip()
        if '開放式' in rooms_str or 'studio' in rooms_str.lower():
            layout['studio'] = True
            layout['rooms'] = 0
        elif '房' in rooms_str:
            match = re.search(r'(\d+)', rooms_str)
            if match:
                layout['rooms'] = int(match.group(1))
    
    if title:
        title_match = re.search(r'(\d+)房\s*(\d+)廁', title)
        if title_match:
            layout['rooms'] = int(title_match.group(1))
            layout['bathrooms'] = int(title_match.group(2))
        elif '3房' in title:
            layout['rooms'] = 3
        elif '2房' in title:
            layout['rooms'] = 2
        elif '1房' in title:
            layout['rooms'] = 1
        elif '4房' in title:
            layout['rooms'] = 4
        
        if '複式' in title:
            layout['duplex'] = True
        if '天台' in title:
            layout['with_rooftop'] = True
        if '平台' in title:
            layout['with_platform'] = True
    
    return layout


def aggregate_room_layouts(layouts: list) -> dict:
    if not layouts:
        return None
    
    room_counts = Counter()
    bath_counts = Counter()
    has_studio = False
    has_duplex = False
    has_rooftop = False
    has_platform = False
    
    for layout in layouts:
        if layout.get('rooms') is not None:
            room_counts[layout['rooms']] += 1
        if layout.get('bathrooms') is not None:
            bath_counts[layout['bathrooms']] += 1
        if layout.get('studio'):
            has_studio = True
        if layout.get('duplex'):
            has_duplex = True
        if layout.get('with_rooftop'):
            has_rooftop = True
        if layout.get('with_platform'):
            has_platform = True
    
    most_common_rooms = room_counts.most_common(1)[0][0] if room_counts else None
    most_common_baths = bath_counts.most_common(1)[0][0] if bath_counts else None
    
    return {
        'typical_rooms': most_common_rooms,
        'typical_bathrooms': most_common_baths,
        'has_studio_option': has_studio,
        'has_duplex_option': has_duplex,
        'has_rooftop_option': has_rooftop,
        'has_platform_option': has_platform,
        'room_distribution': dict(room_counts),
        'listing_count': len(layouts),
    }


def generate_sql_updates(estate_data: dict) -> str:
    """Generate SQL UPDATE statements for all estates."""
    sql_lines = [
        "-- 28Hse Floor & Room Layout Update",
        "-- Generated by scraper_28hse_floor_v2.py",
        "",
    ]
    
    for estate_name, data in estate_data.items():
        floor_info = data.get('floor_info')
        room_layout = data.get('room_layout')
        
        if not floor_info and not room_layout:
            continue
        
        updates = []
        
        if floor_info and floor_info.get('typical_floor') is not None:
            updates.append(f"floor_number = {floor_info['typical_floor']}")
            # Also include floor_range in room_layout JSON for reference
            if room_layout:
                room_layout['floor_range'] = floor_info.get('floor_range')
        elif floor_info and floor_info.get('floor_range'):
            # Fallback: if typical_floor is None but floor_range exists, try to parse
            fr = floor_info['floor_range']
            if '-' in fr:
                parts = fr.split('-')
                try:
                    mid = (int(parts[0]) + int(parts[1])) // 2
                    updates.append(f"floor_number = {mid}")
                except:
                    pass
        
        if room_layout:
            layout_json = json.dumps(room_layout, ensure_ascii=False)
            # Escape single quotes for SQL
            layout_json_escaped = layout_json.replace("'", "''")
            updates.append(f"room_layout = '{layout_json_escaped}'::jsonb")
        
        if not updates:
            continue
        
        estate_name_escaped = estate_name.replace("'", "''")
        sql = f"UPDATE estates_unified SET {', '.join(updates)} WHERE name = '{estate_name_escaped}';"
        sql_lines.append(sql)
    
    return '\n'.join(sql_lines)


def run_scraper(csv_path: str = 'listings_28hse.csv', generate_sql: bool = False):
    print(f"[INFO] Loading listings from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV not found: {csv_path}")
        return
    
    estate_listings = defaultdict(list)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            estate = row.get('estate', '').strip()
            if estate:
                estate_listings[estate].append(row)
    
    print(f"[INFO] Found {len(estate_listings)} unique estates in listings")
    
    estate_data = {}
    for estate_name, listings in estate_listings.items():
        floor_infos = []
        room_layouts = []
        
        for listing in listings:
            unit_info = listing.get('unit_info', '')
            floor_info = extract_floor_info(unit_info)
            if floor_info:
                floor_infos.append(floor_info)
            
            room_layout = extract_room_layout(listing)
            if room_layout.get('rooms') is not None or room_layout.get('studio'):
                room_layouts.append(room_layout)
        
        aggregated_floor = aggregate_floor_info(floor_infos) if floor_infos else None
        aggregated_layout = aggregate_room_layouts(room_layouts) if room_layouts else None
        
        if aggregated_floor or aggregated_layout:
            estate_data[estate_name] = {
                'floor_info': aggregated_floor,
                'room_layout': aggregated_layout,
                'listing_count': len(listings),
            }
    
    print(f"[INFO] Extracted data for {len(estate_data)} estates")
    
    # Quality stats
    single_floor = 0
    good_range = 0
    for name, d in estate_data.items():
        fi = d.get('floor_info')
        if fi and fi.get('floor_range'):
            fr = fi['floor_range']
            if '-' in fr:
                parts = fr.split('-')
                try:
                    span = int(parts[1]) - int(parts[0])
                    if span == 0:
                        single_floor += 1
                    else:
                        good_range += 1
                except:
                    pass
    
    print(f"[INFO] Floor range quality: {good_range} good ranges, {single_floor} single-floor")
    
    # Save JSON
    output_path = 'scraper_output_28hse_v2.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(estate_data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Results saved to {output_path}")
    
    # Generate SQL if requested
    if generate_sql:
        sql = generate_sql_updates(estate_data)
        sql_path = 'update_floor_28hse.sql'
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write(sql)
        print(f"[INFO] SQL saved to {sql_path}")
        print(f"[INFO] Total {len(sql.split(chr(10)))} lines of SQL")
    
    return estate_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='28Hse Floor & Room Layout Scraper v2')
    parser.add_argument('--generate-sql', action='store_true',
                        help='Generate SQL UPDATE statements')
    parser.add_argument('--csv', default='listings_28hse.csv',
                        help='Path to listings CSV file')
    
    args = parser.parse_args()
    run_scraper(csv_path=args.csv, generate_sql=args.generate_sql)
