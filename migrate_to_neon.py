# CSV → Neon Postgres 數據庫遷移腳本 (v3.5)
# 將CSV數據增量同步到Neon Postgres數據庫

import csv
import os
import re
import psycopg2
from urllib.parse import urlparse

# Neon數據庫連接字符串
DATABASE_URL = "postgresql://neondb_owner:npg_sVKUOn6P2BlW@ep-ancient-cherry-afmoe2xv-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

def get_db_connection():
    """獲取數據庫連接"""
    return psycopg2.connect(DATABASE_URL)


def sync_listings_incremental():
    """增量同步 listings（只插入CSV中有但數據庫中沒有的記錄）"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    csv_path = os.path.join(data_dir, 'listings_28hse.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return 0
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)
    
    print(f"📄 CSV listings: {len(csv_rows)}")
    
    # Get existing listings from DB
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM listings;")
    db_count = cur.fetchone()[0]
    print(f"🗄️  DB listings: {db_count}")
    
    # Get existing titles to avoid duplicates
    cur.execute("SELECT title, estate_name, unit_info FROM listings;")
    existing = set(cur.fetchall())
    
    inserted = 0
    skipped = 0
    
    for row in csv_rows:
        title = row.get('title', '')
        estate_name = row.get('estate', '')
        unit_info = row.get('unit_info', '')
        
        # Check if already exists
        if (title, estate_name, unit_info) in existing:
            skipped += 1
            continue
        
        # Parse price
        price_raw = row.get('price_raw', '')
        price_num = 0
        m = re.search(r'(\d+(?:\.\d+)?)\s*萬', price_raw)
        if m:
            price_num = float(m.group(1))
        
        # Parse floor
        floor_number = 10
        unit_info_val = row.get('unit_info', '')
        if unit_info_val:
            if '低層' in unit_info_val or '低层' in unit_info_val:
                floor_number = 5
            elif '中層' in unit_info_val or '中层' in unit_info_val:
                floor_number = 10
            elif '高層' in unit_info_val or '高层' in unit_info_val:
                floor_number = 20
            else:
                m = re.search(r'(\d+)', unit_info_val)
                if m:
                    fn = int(m.group(1))
                    if 3 <= fn <= 80:
                        floor_number = fn
        
        # Parse area
        build_area = None
        usable_area = None
        try:
            ba = row.get('build_area', '').replace('呎', '').replace('尺', '').strip()
            if ba:
                build_area = float(ba)
        except:
            pass
        try:
            ua = row.get('usable_area', '').replace('呎', '').replace('尺', '').strip()
            if ua:
                usable_area = float(ua)
        except:
            pass
        
        # Parse views
        views = row.get('views', '')
        has_sea = '海景' in views or '臨海' in views or '海' in views
        has_mountain = '山景' in views or '園景' in views or '山' in views
        
        # Parse year
        year_built = None
        try:
            yb = row.get('year_built', '')
            if yb and str(yb).strip().isdigit():
                year_built = int(yb)
        except:
            pass
        
        # Insert
        cur.execute("""
            INSERT INTO listings (
                title, estate_name, district, unit_info, floor_number,
                price_raw, price_num, build_area, usable_area, rooms,
                facing, yun, has_sea_view, has_mountain_view, decoration,
                views, features, agent, posted_time, listing_url, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
        """, (
            title, estate_name, row.get('district', ''), unit_info_val, floor_number,
            price_raw, price_num, build_area, usable_area, row.get('rooms', ''),
            row.get('facing', ''), row.get('yun', ''), has_sea, has_mountain,
            row.get('decoration', ''), views, row.get('features', ''),
            row.get('agent', ''), row.get('posted_time', ''), row.get('url', '')
        ))
        
        inserted += 1
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Inserted: {inserted}")
    print(f"⏭️  Skipped (already exists): {skipped}")
    return inserted


def create_estates_unified_table():
    """創建 estates_unified 表（如果還不存在）並同步數據"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'estates_unified'
        );
    """)
    exists = cur.fetchone()[0]
    
    if not exists:
        cur.execute("""
            CREATE TABLE estates_unified (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                district VARCHAR(100),
                facing VARCHAR(50),
                building_year INTEGER,
                price_range VARCHAR(100),
                transport_rating INTEGER DEFAULT 0,
                amenities_score INTEGER DEFAULT 0,
                has_sea_view BOOLEAN DEFAULT FALSE,
                has_mountain_view BOOLEAN DEFAULT FALSE,
                school_net VARCHAR(100),
                property_type VARCHAR(100),
                source_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        print("✅ Created estates_unified table")
    else:
        print("🗄️  estates_unified table already exists")
    
    # Read CSV and sync
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    csv_path = os.path.join(data_dir, 'estates_unified.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        cur.close()
        conn.close()
        return 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)
    
    print(f"📄 CSV estates_unified: {len(csv_rows)}")
    
    # Get existing
    cur.execute("SELECT name, district FROM estates_unified;")
    existing = set(cur.fetchall())
    
    inserted = 0
    
    for row in csv_rows:
        name = row.get('name', '')
        district = row.get('district', '')
        
        if (name, district) in existing:
            continue
        
        # Parse boolean fields
        has_sea = row.get('has_sea_view', 'False').lower() == 'true'
        has_mountain = row.get('has_mountain_view', 'False').lower() == 'true'
        
        # Parse integers
        transport_rating = 0
        amenities_score = 0
        try:
            tr = row.get('transport_rating', '')
            if tr and str(tr).isdigit():
                transport_rating = int(tr)
        except:
            pass
        try:
            am = row.get('amenities_score', '')
            if am and str(am).isdigit():
                amenities_score = int(am)
        except:
            pass
        
        building_year = None
        try:
            by = row.get('building_year', '')
            if by and str(by).isdigit():
                building_year = int(by)
        except:
            pass
        
        source_count = 0
        try:
            sc = row.get('source_count', '')
            if sc and str(sc).isdigit():
                source_count = int(sc)
        except:
            pass
        
        cur.execute("""
            INSERT INTO estates_unified (
                name, district, facing, building_year, price_range,
                transport_rating, amenities_score, has_sea_view, has_mountain_view,
                school_net, property_type, source_count, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            name, district, row.get('facing', ''), building_year,
            row.get('price_range', ''), transport_rating, amenities_score,
            has_sea, has_mountain, row.get('school_net', ''),
            row.get('property_type', ''), source_count
        ))
        
        inserted += 1
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ estates_unified inserted: {inserted}")
    return inserted


def verify_sync():
    """驗證同步結果"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("\n=== 同步驗證 ===")
    
    for table in ['estates', 'listings', 'sha_poi', 'estates_unified']:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    print("=== CSV → Neon Postgres 數據遷移 ===\n")
    
    # 1. 增量同步 listings
    sync_listings_incremental()
    
    print()
    
    # 2. 創建並同步 estates_unified
    create_estates_unified_table()
    
    print()
    
    # 3. 驗證
    verify_sync()
    
    print("\n✅ 數據遷移完成!")
