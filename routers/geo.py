from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
import json

router = APIRouter(prefix="/api/geo")

BASE = Path(__file__).parent.parent


def _load_json(filename: str) -> dict:
    path = BASE / "data" / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@router.get("/estates")
def get_estates_geojson(
    district: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 500
):
    """
    返回屋苑 GeoJSON（用於 Leaflet 地圖顯示）
    Supports: ?district=沙田&min_score=70&limit=100
    """
    coords = _load_json("estate_coordinates.json").get("estates", {})
    estates_csv = []
    with open(BASE / "data" / "estates_28hse.csv", "r", encoding="utf-8") as f:
        import csv
        reader = csv.DictReader(f)
        estates_csv = list(reader)

    features = []
    for estate in estates_csv:
        name = estate.get("name", "").strip()
        coord = coords.get(name, {})
        lat = coord.get("lat")
        lng = coord.get("lng")
        if not lat or not lng:
            continue

        # 地區篩選
        if district and estate.get("district") != district:
            continue

        # 構建屬性
        props = {
            "name": name,
            "district": estate.get("district", ""),
            "facing": estate.get("facing", ""),
            "building_year": estate.get("building_year", ""),
            "yun": estate.get("yun", ""),
            "has_sea_view": estate.get("has_sea_view", ""),
            "has_mountain_view": estate.get("has_mountain_view", ""),
            "transport_rating": estate.get("transport_rating", ""),
            "amenities_score": estate.get("amenities_score", ""),
        }

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": props
        })

        if len(features) >= limit:
            break

    return {
        "type": "FeatureCollection",
        "features": features,
        "total": len(features)
    }


@router.get("/sha-pois")
def get_sha_pois_geojson(
    sha_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 500
):
    """
    返回煞氣 POI GeoJSON（用於 Leaflet 地圖顯示）
    Supports: ?sha_type=醫院煞&severity=severe
    """
    data = _load_json("sha_poi_hk.json")
    pois = data.get("pois", [])

    features = []
    for poi in pois:
        # 篩選
        if sha_type and poi.get("sha_type") != sha_type:
            continue
        if severity and poi.get("severity") != severity:
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [poi.get("lng"), poi.get("lat")]
            },
            "properties": {
                "name": poi.get("name", ""),
                "sha_type": poi.get("sha_type", ""),
                "severity": poi.get("severity", ""),
                "description": poi.get("description", ""),
                "feng_shui_effect": poi.get("feng_shui_effect", ""),
                "district": poi.get("district", "")
            }
        })

        if len(features) >= limit:
            break

    return {
        "type": "FeatureCollection",
        "features": features,
        "total": len(features)
    }


@router.get("/estate/{estate_name}/nearby-shas")
def get_estate_nearby_shas(estate_name: str, radius_m: int = 500):
    """
    查詢指定屋苑周邊 radius_m 內的煞氣
    """
    coords = _load_json("estate_coordinates.json").get("estates", {})
    estate = coords.get(estate_name)
    if not estate:
        raise HTTPException(status_code=404, detail=f"屋苑 {estate_name} 未找到坐標")

    from data.gis_analysis import scan_nearby_shas
    result = scan_nearby_shas(estate["lat"], estate["lng"], radius_m)

    return {
        "estate_name": estate_name,
        "estate_lat": estate["lat"],
        "estate_lng": estate["lng"],
        "radius_m": radius_m,
        **result
    }


@router.get("/estate/{estate_name}/feng-shui")
def get_estate_feng_shui(estate_name: str, facing: Optional[str] = None):
    """
    查詢指定屋苑的 GIS 風水分析
    """
    from data.gis_analysis import analyze_gis_feng_shui
    result = analyze_gis_feng_shui(estate_name=estate_name, facing=facing)
    return result
