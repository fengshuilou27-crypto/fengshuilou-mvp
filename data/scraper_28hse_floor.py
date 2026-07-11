"""
28Hse Floor & Room Layout Scraper
=================================
Extracts floor_number and room_layout from listings_28hse.csv unit_info field,
with capability to scrape 28Hse property detail pages for additional data.

Usage:
    python scraper_28hse_floor.py --dry-run    # Preview without DB update
    python scraper_28hse_floor.py --apply      # Update database
"""

import csv
import re
import os
import json
import argparse
from collections import defaultdict, Counter

# Database imports (only used when --apply)
try:
    import psycopg2
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ============================================================
# FLOOR INFO EXTRACTION FROM unit_info
# ============================================================

FLOOR_PATTERN_MAP = {
    # Chinese floor terms → (typical_floor, description)
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

# Extract numeric floor patterns like "20/F", "3樓", "第5層"
NUMERIC_FLOOR_RE = re.compile(r'(\d+)(?:[樓層F\/]|座.*(?:高層|中層|低層))')
FLOOR_TERM_RE = re.compile(r'(高層|中層|低層|全幢|地下|G層|G室|平台|複式|相連|獨立屋)')
TOWER_RE = re.compile(r'(?:第?\d+[座期]|[A-Z]座)')
UNIT_RE = re.compile(r'([A-Z]\d?室|\d+室)')


def extract_floor_info(unit_info: str) -> dict:
    """Extract floor information from unit_info string."""
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
    
    # Extract floor term (高層/中層/低層 etc.)
    floor_match = FLOOR_TERM_RE.search(unit_info)
    if floor_match:
        term = floor_match.group(1)
        result['floor_term'] = term
        mapped = FLOOR_PATTERN_MAP.get(term)
        if mapped:
            result['floor_range'] = mapped[0]
            result['floor_term_en'] = mapped[1]
    
    # Try to extract numeric floor
    # Look for patterns like "20/F", "3樓", or number before floor term context
    numeric_match = NUMERIC_FLOOR_RE.search(unit_info)
    if numeric_match:
        floor_num = int(numeric_match.group(1))
        if 1 <= floor_num <= 100:  # Reasonable floor range
            result['extracted_floor'] = floor_num
    
    # Extract tower/block info
    tower_match = TOWER_RE.search(unit_info)
    if tower_match:
        result['tower'] = tower_match.group(0)
    
    # Extract unit info
    unit_match = UNIT_RE.search(unit_info)
    if unit_match:
        result['unit'] = unit_match.group(1)
    
    return result


def aggregate_floor_info(floor_infos: list) -> dict:
    """Aggregate floor info from multiple listings to get estate-level data."""
    if not floor_infos:
        return None
    
    # Count floor terms
    term_counts = Counter()
    extracted_floors = []
    towers = set()
    
    for info in floor_infos:
        if info.get('floor_term'):
            term_counts[info['floor_term']] += 1
        if info.get('extracted_floor') is not None:
            extracted_floors.append(info['extracted_floor'])
        if info.get('tower'):
            towers.add(info['tower'])
    
    if not term_counts and not extracted_floors:
        return None
    
    # Most common floor term
    most_common_term = term_counts.most_common(1)[0][0] if term_counts else None
    
    # Build floor range from extracted floors or term mapping
    if extracted_floors:
        min_floor = min(extracted_floors)
        max_floor = max(extracted_floors)
        floor_range = f"{min_floor}-{max_floor}"
    elif most_common_term:
        floor_range = FLOOR_PATTERN_MAP.get(most_common_term, ('', ''))[0]
    else:
        floor_range = None
    
    # Typical floor (median of extracted or midpoint of range)
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
        'tower_count': len(towers),
        'listing_count': len(floor_infos),
    }


# ============================================================
# ROOM LAYOUT EXTRACTION (from unit_info + rooms field)
# ============================================================

ROOM_LAYOUT_RE = re.compile(r'(\d+房|\d+房\d+廁|開放式|studio|連\s*天台|連\s*平台|複式)')

def extract_room_layout(row: dict) -> dict:
    """Extract room layout from CSV row."""
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
    
    # Parse rooms field like "2房", "3房", "開放式"
    if rooms:
        rooms_str = str(rooms).strip()
        if '開放式' in rooms_str or 'studio' in rooms_str.lower():
            layout['studio'] = True
            layout['rooms'] = 0
        elif '房' in rooms_str:
            match = re.search(r'(\d+)', rooms_str)
            if match:
                layout['rooms'] = int(match.group(1))
    
    # Try to extract from title for more detail
    if title:
        # "3房2廁" → 3 rooms, 2 bathrooms
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
    """Aggregate room layouts from multiple listings."""
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


# ============================================================
# DATABASE UPDATE
# ============================================================

def update_database(estate_data: dict, dry_run: bool = True):
    """Update estates_unified table with scraped data."""
    if not DB_AVAILABLE:
        print("[WARN] psycopg2 not available, skipping DB update")
        return
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[WARN] DATABASE_URL not set, skipping DB update")
        return
    
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        updated = 0
        for estate_name, data in estate_data.items():
            floor_info = data.get('floor_info')
            room_layout = data.get('room_layout')
            
            if not floor_info and not room_layout:
                continue
            
            # Build update fields
            updates = []
            params = []
            
            if floor_info:
                if floor_info.get('floor_range'):
                    updates.append("floor_number = %s")
                    params.append(floor_info['floor_range'])
            
            if room_layout:
                layout_json = json.dumps(room_layout, ensure_ascii=False)
                updates.append("room_layout = %s")
                params.append(layout_json)
            
            if not updates:
                continue
            
            params.append(estate_name)
            sql = f"UPDATE estates_unified SET {', '.join(updates)} WHERE name = %s"
            
            if dry_run:
                print(f"[DRY-RUN] {estate_name}: {updates}")
            else:
                cur.execute(sql, params)
                updated += cur.rowcount
        
        if not dry_run:
            conn.commit()
            print(f"[DB] Updated {updated} estates")
        
        cur.close()
    except Exception as e:
        print(f"[ERROR] DB update failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# ============================================================
# MAIN SCRAPER
# ============================================================

def run_scraper(csv_path: str = 'listings_28hse.csv', dry_run: bool = True):
    """Main scraper function."""
    print(f"[INFO] Loading listings from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV not found: {csv_path}")
        return
    
    # Read CSV and group by estate
    estate_listings = defaultdict(list)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            estate = row.get('estate', '').strip()
            if estate:
                estate_listings[estate].append(row)
    
    print(f"[INFO] Found {len(estate_listings)} unique estates in listings")
    
    # Process each estate
    estate_data = {}
    for estate_name, listings in estate_listings.items():
        # Extract floor info from all listings
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
    
    # Preview results
    print("\n" + "="*60)
    print("SAMPLE OUTPUT (first 10 estates):")
    print("="*60)
    for i, (name, data) in enumerate(list(estate_data.items())[:10]):
        print(f"\n{name}:")
        if data.get('floor_info'):
            fi = data['floor_info']
            print(f"  Floor: {fi.get('floor_range')} (typical: {fi.get('typical_floor')}, term: {fi.get('most_common_term')})")
            print(f"  Distribution: {fi.get('term_distribution')}")
        if data.get('room_layout'):
            rl = data['room_layout']
            print(f"  Rooms: {rl.get('typical_rooms')}房, Bath: {rl.get('typical_bathrooms')}廁")
    
    # Update database
    print("\n" + "="*60)
    update_database(estate_data, dry_run=dry_run)
    
    # Save results to JSON for inspection
    output_path = 'scraper_output_28hse.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(estate_data, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] Results saved to {output_path}")
    
    return estate_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='28Hse Floor & Room Layout Scraper')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Preview without updating database (default)')
    parser.add_argument('--apply', dest='dry_run', action='store_false',
                        help='Apply updates to database')
    parser.add_argument('--csv', default='listings_28hse.csv',
                        help='Path to listings CSV file')
    
    args = parser.parse_args()
    run_scraper(csv_path=args.csv, dry_run=args.dry_run)
