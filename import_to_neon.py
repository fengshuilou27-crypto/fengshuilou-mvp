#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將本地 CSV/JSON 數據導入 Neon Postgres 數據庫
用法：py import_to_neon.py <database_url>
"""

import csv, json, os, sys, re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).parent


def parse_bool(v):
    if v is None or v == "":
        return None
    return v.lower() in ("true", "1", "yes", "true", "真")


def parse_int(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def parse_decimal(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def main():
    import psycopg2
    from psycopg2.extras import execute_values

    conn_str = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATABASE_URL")
    if not conn_str:
        print("ERROR: 請提供 DATABASE_URL 環境變量或命令行參數", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()

    # ---- 1. 導入 estates（批量 executemany）----
    print("[1/3] 導入 estates...")
    with open(BASE / "data" / "estates_28hse.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        estates = list(reader)

    coords = {}
    try:
        with open(BASE / "data" / "estate_coordinates.json", "r", encoding="utf-8") as f:
            coords = json.load(f).get("estates", {})
    except FileNotFoundError:
        pass

    estate_rows = []
    for row in estates:
        name = row.get("name", "").strip()
        if not name:
            continue
        coord = coords.get(name, {})
        lat = coord.get("lat")
        lng = coord.get("lng")
        geom = f"SRID=4326;POINT({lng} {lat})" if lat and lng else None

        estate_rows.append((
            name, row.get("district"), parse_int(row.get("building_year")),
            row.get("facing"), row.get("yun"),
            parse_bool(row.get("has_sea_view")), parse_bool(row.get("has_mountain_view")),
            parse_int(row.get("transport_rating")), parse_int(row.get("amenities_score")),
            row.get("developer"), row.get("management"), geom
        ))

    execute_values(cur, """
        INSERT INTO estates (name, district, building_year, facing, yun,
            has_sea_view, has_mountain_view, transport_rating, amenities_score,
            developer, management, geom)
        VALUES %s
        ON CONFLICT (name) DO UPDATE SET
            district = EXCLUDED.district,
            building_year = EXCLUDED.building_year,
            facing = EXCLUDED.facing,
            yun = EXCLUDED.yun,
            has_sea_view = EXCLUDED.has_sea_view,
            has_mountain_view = EXCLUDED.has_mountain_view,
            transport_rating = EXCLUDED.transport_rating,
            amenities_score = EXCLUDED.amenities_score,
            developer = EXCLUDED.developer,
            management = EXCLUDED.management,
            geom = EXCLUDED.geom
    """, estate_rows, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))")
    conn.commit()
    print(f"  estates: {len(estate_rows)} done")

    # ---- 2. 導入 listings（批量）----
    print("[2/3] 導入 listings...")
    with open(BASE / "data" / "listings_28hse.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        listings = list(reader)

    cur.execute("SELECT id, name FROM estates")
    estate_map = {name: id for id, name in cur.fetchall()}

    listing_rows = []
    for row in listings:
        title = row.get("title", "").strip()
        estate_name = row.get("estate", "").strip()
        estate_id = estate_map.get(estate_name)

        unit_info = row.get("unit_info", "")
        floor = 15 if "高層" in unit_info else (8 if "中層" in unit_info else (3 if "低層" in unit_info else None))

        price_num = None
        price_raw = row.get("price_raw", "")
        m = re.search(r'(\d+(?:\.\d+)?)', price_raw.replace(',', ''))
        if m:
            price_num = float(m.group(1))

        coord = coords.get(estate_name, {})
        lat = coord.get("lat")
        lng = coord.get("lng")
        geom = f"SRID=4326;POINT({lng} {lat})" if lat and lng else None

        listing_rows.append((
            title, estate_id, estate_name, row.get("district"), unit_info,
            floor, price_raw, price_num, parse_decimal(row.get("build_area")),
            parse_decimal(row.get("usable_area")), row.get("rooms"),
            row.get("facing"), row.get("yun"), parse_bool(row.get("views")), False,
            row.get("decoration"), row.get("views"), row.get("features"),
            row.get("agent"), row.get("url"), row.get("posted_time"), geom
        ))

    execute_values(cur, """
        INSERT INTO listings (title, estate_id, estate_name, district, unit_info,
            floor_number, price_raw, price_num, build_area, usable_area, rooms,
            facing, yun, has_sea_view, has_mountain_view, decoration, views, features,
            agent, listing_url, posted_time, geom)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, listing_rows, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))")
    conn.commit()
    print(f"  listings: {len(listing_rows)} done")

    # ---- 3. 導入 sha_poi（批量）----
    print("[3/3] 導入 sha_poi...")
    with open(BASE / "data" / "sha_poi_hk.json", "r", encoding="utf-8") as f:
        pois = json.load(f).get("pois", [])

    poi_rows = []
    for poi in pois:
        lat = poi.get("lat")
        lng = poi.get("lng")
        geom = f"SRID=4326;POINT({lng} {lat})" if lat and lng else None
        poi_rows.append((
            poi["name"], poi["sha_type"], poi.get("severity"), geom,
            poi.get("district"), poi.get("description"), poi.get("feng_shui_effect"), poi.get("source", "manual")
        ))

    execute_values(cur, """
        INSERT INTO sha_poi (name, sha_type, severity, geom, district, description, feng_shui_effect, source)
        VALUES %s
        ON CONFLICT (name) DO UPDATE SET
            sha_type = EXCLUDED.sha_type,
            severity = EXCLUDED.severity,
            geom = EXCLUDED.geom
    """, poi_rows, template="(%s, %s, %s, ST_GeomFromText(%s, 4326), %s, %s, %s, %s)")
    conn.commit()
    print(f"  sha_poi: {len(poi_rows)} done")

    # ---- 驗證 ----
    print("\n[Verify] DB stats:")
    for table in ["estates", "listings", "sha_poi"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table}: {count} rows")

    # 空間查詢驗證
    cur.execute("""
        SELECT s.name, s.sha_type, s.severity,
               ROUND(ST_Distance(e.geom::geography, s.geom::geography)) as dist_m
        FROM estates e
        JOIN sha_poi s ON ST_DWithin(e.geom::geography, s.geom::geography, 500)
        WHERE e.name = '太古城'
    """)
    rows = cur.fetchall()
    print(f"\n  太古城周邊 500m 煞氣: {len(rows)} 個")
    for r in rows:
        print(f"    {r[0]} ({r[1]}) - {r[3]:.0f}m")

    cur.close()
    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
