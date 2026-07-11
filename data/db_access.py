# 數據庫訪問層 (v3.5)
# 提供與 CSV 兼容的數據訪問接口，支持 Neon Postgres 和 CSV 回退

import os
import csv
import re
from pathlib import Path

# Neon 數據庫連接字符串
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_sVKUOn6P2BlW@ep-ancient-cherry-afmoe2xv-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
)

# 是否使用數據庫（強制啟用）
USE_DATABASE = True


def _get_db_connection():
    """獲取數據庫連接"""
    try:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    except ImportError:
        return None
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def _find_csv_path(filename: str) -> Path:
    """查找 CSV 文件路徑"""
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / filename
    if local_data.exists():
        return local_data
    
    # 搜索上級目錄
    current = script_dir
    for _ in range(3):
        data_dir = current / "data" / filename
        if data_dir.exists():
            return data_dir
        current = current.parent
    
    return None


# ============================================================
# 一、屋苑數據 (estates)
# ============================================================

def load_estates_from_db():
    """從數據庫加載屋苑數據"""
    conn = _get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, facing, district, building_year, 
                   transport_rating, amenities_score,
                   has_sea_view, has_mountain_view, school_net,
                   property_type, NULL as developer, NULL as management,
                   floor_number, room_layout
            FROM estates_unified
            ORDER BY name;
        """)
        
        columns = [desc[0] for desc in cur.description]
        rows = []
        for row in cur.fetchall():
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            # Convert boolean to string for compatibility
            if 'has_sea_view' in row_dict:
                row_dict['has_sea_view'] = str(row_dict['has_sea_view'])
            if 'has_mountain_view' in row_dict:
                row_dict['has_mountain_view'] = str(row_dict['has_mountain_view'])
            rows.append(row_dict)
        
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error loading estates from DB: {e}")
        return None


def load_estates_from_csv():
    """從 CSV 加載屋苑數據（原始實現）"""
    estates = []
    data_path = _find_csv_path("estates_28hse.csv")
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                estates.append(row)
    return estates


def load_estates():
    """加載屋苑數據（數據庫優先，CSV回退）"""
    if USE_DATABASE:
        db_data = load_estates_from_db()
        if db_data:
            return db_data
    return load_estates_from_csv()


# ============================================================
# 二、樓盤數據 (listings)
# ============================================================

def load_listings_from_db():
    """從數據庫加載樓盤數據（v3.6.5 修復版：兼容缺失列）"""
    conn = _get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        # v3.6.5: 先檢查 listings 表有哪些列，避免查詢不存在的列
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'listings';
        """)
        existing_cols = {row[0] for row in cur.fetchall()}
        
        # 構建安全的 SELECT 列列表
        desired_cols = [
            "title", "district", "estate_name", "unit_info",
            "price_raw", "price_num", "build_area", "usable_area",
            "rooms", "facing", "year_built", "yun", "agent", "posted_time",
            "listing_url", "has_sea_view", "has_mountain_view",
            "views", "features", "decoration", "created_at"
        ]
        
        select_cols = []
        alias_map = {}  # db_col -> output_key
        for col in desired_cols:
            if col in existing_cols:
                select_cols.append(col)
                alias_map[col] = col
            elif col == "estate_name":
                # 嘗試兼容舊 schema
                if "estate" in existing_cols:
                    select_cols.append("estate")
                    alias_map["estate"] = "estate"
            elif col == "price_num":
                if "price" in existing_cols:
                    select_cols.append("price")
                    alias_map["price"] = "price"
            elif col == "listing_url":
                if "url" in existing_cols:
                    select_cols.append("url")
                    alias_map["url"] = "url"
        
        if not select_cols:
            print("No recognizable columns found in listings table")
            return None
        
        # 構建查詢
        col_sql = ", ".join(select_cols)
        order_col = "created_at" if "created_at" in existing_cols else select_cols[0]
        
        cur.execute(f"""
            SELECT {col_sql}
            FROM listings
            ORDER BY {order_col} DESC;
        """)
        
        columns = [desc[0] for desc in cur.description]
        rows = []
        for row in cur.fetchall():
            row_dict = {}
            for i, col in enumerate(columns):
                val = row[i]
                if val is None:
                    val = ""
                row_dict[col] = str(val)
            # 確保關鍵字段存在（如果不存在則設為空字符串）
            for key in ["year_built", "yun", "estate", "price", "url"]:
                if key not in row_dict:
                    row_dict[key] = ""
            rows.append(row_dict)
        
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error loading listings from DB: {e}")
        return None


def load_listings_from_csv():
    """從 CSV 加載樓盤數據（原始實現）"""
    listings = []
    data_path = _find_csv_path("listings_28hse.csv")
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                listings.append(row)
    return listings


def load_listings():
    """加載樓盤數據（數據庫優先，CSV回退）"""
    if USE_DATABASE:
        db_data = load_listings_from_db()
        if db_data:
            return db_data
    return load_listings_from_csv()


# ============================================================
# 三、estates_unified 數據
# ============================================================

def load_estates_unified_from_db():
    """從數據庫加載 estates_unified 數據"""
    conn = _get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, facing, district, building_year, price_range,
                   transport_rating, amenities_score,
                   has_sea_view, has_mountain_view, school_net,
                   developer, management, property_type, source_count,
                   floor_number, room_layout
            FROM estates_unified
            ORDER BY name;
        """)
        
        columns = [desc[0] for desc in cur.description]
        rows = []
        for row in cur.fetchall():
            row_dict = {}
            for i, col in enumerate(columns):
                val = row[i]
                if val is None:
                    val = ""
                row_dict[col] = str(val)
            rows.append(row_dict)
        
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error loading estates_unified from DB: {e}")
        return None


def load_estates_unified_from_csv():
    """從 CSV 加載 estates_unified 數據"""
    estates = []
    data_path = _find_csv_path("estates_unified.csv")
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                estates.append(row)
    return estates


def load_estates_unified():
    """加載 estates_unified 數據（數據庫優先，CSV回退）"""
    if USE_DATABASE:
        db_data = load_estates_unified_from_db()
        if db_data:
            return db_data
    return load_estates_unified_from_csv()


# ============================================================
# 四、數據庫狀態
# ============================================================

def get_db_status():
    """獲取數據庫連接狀態"""
    conn = _get_db_connection()
    if not conn:
        return {
            "connected": False,
            "error": "無法連接數據庫",
            "use_database": USE_DATABASE
        }
    
    try:
        cur = conn.cursor()
        
        # Get table counts
        tables = {}
        for table in ['estates', 'listings', 'sha_poi', 'estates_unified']:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                tables[table] = cur.fetchone()[0]
            except:
                tables[table] = 0
        
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {
            "connected": True,
            "version": version[:50],
            "tables": tables,
            "use_database": USE_DATABASE
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "use_database": USE_DATABASE
        }
