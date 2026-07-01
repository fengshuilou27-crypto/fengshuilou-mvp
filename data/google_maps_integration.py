#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Platform 集成模組
提供 Geocoding、Places 和 Elevation API 調用

API Key: 從環境變量或配置文件讀取
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import requests

# ===== 配置 =====
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
# 如果環境變量未設置，嘗試從配置文件讀取
if not API_KEY:
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            API_KEY = config.get("google_maps_api_key", "")

if not API_KEY:
    # 用戶已啟用 Google Maps Platform API，使用提供的 key
    API_KEY = "AIzaSyC-hLYqIjpLlG9I3jf6_fQkmYKQAezyY5g"

BASE_URL = "https://maps.googleapis.com/maps/api"
RATE_LIMIT_DELAY = 0.05  # 50ms 延遲，避免速率限制


# ===== 通用工具 =====

def _make_request(endpoint: str, params: dict) -> dict:
    """發送 Google Maps API 請求"""
    params["key"] = API_KEY
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "REQUEST_ERROR", "error": str(e)}


def _is_valid_result(data: dict) -> bool:
    """檢查 API 返回是否有效"""
    return data.get("status") == "OK"


# ===== Geocoding API =====

def geocode_address(address: str, region: str = "hk") -> Optional[Dict]:
    """
    將地址轉換為 WGS84 坐標
    
    Args:
        address: 地址或屋苑名稱（如「太古城 香港」）
        region: 區域代碼（hk = 香港）
    
    Returns:
        {
            "lat": 22.288,
            "lng": 114.220,
            "formatted_address": "香港太古城",
            "place_id": "ChIJ...",
            "types": ["premise", "geocode"]
        }
        或 None（如果失敗）
    """
    params = {
        "address": address,
        "region": region,
        "language": "zh-TW",
    }
    
    data = _make_request("geocode/json", params)
    time.sleep(RATE_LIMIT_DELAY)
    
    if not _is_valid_result(data):
        return None
    
    result = data["results"][0]
    location = result["geometry"]["location"]
    
    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "formatted_address": result.get("formatted_address", ""),
        "place_id": result.get("place_id", ""),
        "types": result.get("types", []),
    }


def batch_geocode_estates(estate_names: List[str]) -> Dict[str, Optional[Dict]]:
    """
    批量地理編碼屋苑名稱
    
    Args:
        estate_names: 屋苑名稱列表
    
    Returns:
        {屋苑名: 坐標信息, ...}
    """
    results = {}
    for name in estate_names:
        # 嘗試帶「香港」前綴
        result = geocode_address(f"{name} 香港")
        if not result:
            # 回退：不帶前綴
            result = geocode_address(name)
        results[name] = result
        print(f"  {name}: {result['lat']:.4f}, {result['lng']:.4f}" if result else f"  {name}: FAILED")
    
    return results


# ===== Places API =====

# 風水煞氣對應的 Google Places 類型
SHA_PLACE_TYPES = {
    "hospital": {"severity": "critical", "sha_type": "獨陰煞", "description": "醫院陰氣重"},
    "cemetery": {"severity": "severe", "sha_type": "陰煞", "description": "墳場/骨灰龕"},
    "funeral_home": {"severity": "severe", "sha_type": "陰煞", "description": "殯儀館/火葬場"},
    "police": {"severity": "moderate", "sha_type": "官非煞", "description": "警署/執法機構"},
    "power_plant": {"severity": "severe", "sha_type": "火煞", "description": "發電廠/變電站"},
    "substation": {"severity": "moderate", "sha_type": "電磁煞", "description": "變電站/高壓電塔"},
    "slaughterhouse": {"severity": "severe", "sha_type": "血光煞", "description": "屠宰場"},
    "prison": {"severity": "severe", "sha_type": "官非煞", "description": "監獄/拘留所"},
    "dump": {"severity": "moderate", "sha_type": "穢氣煞", "description": "垃圾處理站/堆填區"},
    "landfill": {"severity": "moderate", "sha_type": "穢氣煞", "description": "堆填區"},
    "place_of_worship": {"severity": "mild", "sha_type": "神煞", "description": "寺廟/教堂（中性，部分風水師認為為吉）"},
    "church": {"severity": "mild", "sha_type": "神煞", "description": "教堂"},
    "hindu_temple": {"severity": "mild", "sha_type": "神煞", "description": "印度廟"},
    "mosque": {"severity": "mild", "sha_type": "神煞", "description": "清真寺"},
}


def search_nearby_pois(
    lat: float, 
    lng: float, 
    radius: int = 1000,
    place_types: List[str] = None
) -> List[Dict]:
    """
    搜索指定坐標周邊的 POI（Places API Nearby Search）
    
    Args:
        lat, lng: 中心坐標
        radius: 搜索半徑（米），默認 1000m
        place_types: Google Places 類型列表，默認搜索所有煞氣類型
    
    Returns:
        [{
            "name": "醫院名稱",
            "lat": 22.288,
            "lng": 114.220,
            "distance_m": 350,
            "place_type": "hospital",
            "sha_type": "獨陰煞",
            "severity": "critical",
            "description": "醫院陰氣重"
        }, ...]
    """
    if place_types is None:
        place_types = list(SHA_PLACE_TYPES.keys())
    
    all_pois = []
    
    for place_type in place_types:
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "language": "zh-TW",
        }
        
        data = _make_request("place/nearbysearch/json", params)
        time.sleep(RATE_LIMIT_DELAY)
        
        if not _is_valid_result(data):
            continue
        
        for result in data.get("results", []):
            location = result["geometry"]["location"]
            
            # 計算距離（簡化計算，使用 haversine）
            from data.gis_analysis import haversine_distance
            distance = haversine_distance(lat, lng, location["lat"], location["lng"])
            
            # 獲取煞氣配置
            sha_config = SHA_PLACE_TYPES.get(place_type, {
                "severity": "mild", 
                "sha_type": "未知煞", 
                "description": ""
            })
            
            all_pois.append({
                "name": result.get("name", "未知"),
                "lat": location["lat"],
                "lng": location["lng"],
                "distance_m": int(distance),
                "place_type": place_type,
                "sha_type": sha_config["sha_type"],
                "severity": sha_config["severity"],
                "description": sha_config["description"],
                "place_id": result.get("place_id", ""),
                "vicinity": result.get("vicinity", ""),
            })
    
    # 按距離排序
    all_pois.sort(key=lambda x: x["distance_m"])
    
    # 去重（同坐標或同名的只保留最近的一個）
    seen = set()
    unique_pois = []
    for poi in all_pois:
        key = (poi["name"], round(poi["lat"], 4), round(poi["lng"], 4))
        if key not in seen:
            seen.add(key)
            unique_pois.append(poi)
    
    return unique_pois


def auto_scan_sha_pois(lat: float, lng: float, radius: int = 1000) -> Dict:
    """
    自動掃描周邊煞氣 POI（使用 Google Places API）
    替代手動維護的 sha_poi_hk.json
    
    Returns:
        {
            "shas_found": [...],
            "total_penalty": -15,
            "poi_count": 5,
            "scan_radius": 1000,
            "source": "Google Places API"
        }
    """
    pois = search_nearby_pois(lat, lng, radius)
    
    from data.gis_analysis import SHA_SEVERITY_PENALTY
    
    total_penalty = 0
    for poi in pois:
        penalty = SHA_SEVERITY_PENALTY.get(poi["severity"], -3)
        distance_factor = max(0.3, 1 - (poi["distance_m"] / radius))
        poi["penalty"] = round(penalty * distance_factor, 1)
        total_penalty += poi["penalty"]
    
    total_penalty = max(-25, total_penalty)
    
    return {
        "status": "success",
        "shas_found": pois,
        "total_penalty": round(total_penalty, 1),
        "poi_count": len(pois),
        "scan_radius": radius,
        "source": "Google Places API",
        "rationale": f"Google Places API 掃描到{len(pois)}項煞氣POI，總扣分{abs(total_penalty)}分"
    }


# ===== Elevation API =====

def get_elevation(lat: float, lng: float) -> Optional[float]:
    """
    查詢指定坐標的高程（Google Elevation API）
    用於獨立驗證 SRTM DEM 數據
    
    Returns:
        高程值（米），或 None
    """
    params = {
        "locations": f"{lat},{lng}",
    }
    
    data = _make_request("elevation/json", params)
    time.sleep(RATE_LIMIT_DELAY)
    
    if not _is_valid_result(data):
        return None
    
    result = data["results"][0]
    return result["elevation"]


def batch_elevation(coords: List[Tuple[float, float]]) -> List[Optional[float]]:
    """
    批量查詢高程
    
    Args:
        coords: [(lat, lng), ...]
    
    Returns:
        [elevation_or_None, ...]
    """
    # Google Elevation API 支持單次最多 512 個位置
    locations = "|".join([f"{lat},{lng}" for lat, lng in coords])
    
    params = {
        "locations": locations,
    }
    
    data = _make_request("elevation/json", params)
    time.sleep(RATE_LIMIT_DELAY)
    
    if not _is_valid_result(data):
        return [None] * len(coords)
    
    return [r["elevation"] for r in data.get("results", [])]


def verify_dem_against_google(lat: float, lng: float) -> Dict:
    """
    比較 SRTM DEM 與 Google Elevation API 的高程差異
    
    Returns:
        {
            "srtm_elevation": 8.0,
            "google_elevation": 10.2,
            "difference": 2.2,
            "assessment": "基本一致"
        }
    """
    from dem_parser import query_elevation
    
    srtm_elev = query_elevation(lat, lng)
    google_elev = get_elevation(lat, lng)
    
    if srtm_elev is None or google_elev is None:
        return {
            "srtm_elevation": srtm_elev,
            "google_elevation": google_elev,
            "difference": None,
            "assessment": "無法比較"
        }
    
    diff = google_elev - srtm_elev
    
    if abs(diff) < 5:
        assessment = "基本一致"
    elif abs(diff) < 15:
        assessment = "輕微差異"
    else:
        assessment = "顯著差異，需進一步調查"
    
    return {
        "srtm_elevation": round(srtm_elev, 1),
        "google_elevation": round(google_elev, 1),
        "difference": round(diff, 1),
        "assessment": assessment
    }


# ===== 批量擴展 estate_coordinates.json =====

def expand_estate_coordinates(estate_names: List[str], output_file: str = None) -> Dict:
    """
    批量擴展屋苑坐標數據庫
    
    Args:
        estate_names: 需要查詢的屋苑名稱列表
        output_file: 輸出 JSON 文件路徑（默認不保存）
    
    Returns:
        {屋苑名: {"lat": ..., "lng": ...}, ...}
    """
    print(f"正在批量地理編碼 {len(estate_names)} 個屋苑...")
    
    results = batch_geocode_estates(estate_names)
    
    # 轉換為標準格式
    estates = {}
    for name, data in results.items():
        if data:
            estates[name] = {
                "lat": data["lat"],
                "lng": data["lng"],
                "source": "Google Geocoding API",
                "place_id": data["place_id"]
            }
    
    if output_file and estates:
        output_path = Path(output_file)
        # 合併現有數據
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            existing_estates = existing.get("estates", {})
            existing_estates.update(estates)
            estates = existing_estates
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"estates": estates}, f, ensure_ascii=False, indent=2)
        print(f"已保存到 {output_file}")
    
    return estates


# ===== 測試 =====
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    # 讀取 API key
    API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not API_KEY:
        # 嘗試從配置文件讀取
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                API_KEY = config.get("google_maps_api_key", "")
    
    if API_KEY in ("", "YOUR_API_KEY_HERE"):
        print("ERROR: 未設置 GOOGLE_MAPS_API_KEY 環境變量或 config.json")
        print("請設置：export GOOGLE_MAPS_API_KEY='your_key'")
        sys.exit(1)
    
    print(f"=== Google Maps API 測試 ===")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    print()
    
    # 1. 測試 Geocoding
    print("1. Geocoding API 測試")
    print("-" * 40)
    test_addresses = ["太古城 香港", "嘉湖山莊 天水圍", "屯門市廣場 香港"]
    for addr in test_addresses:
        result = geocode_address(addr)
        if result:
            print(f"  {addr}: {result['lat']:.4f}, {result['lng']:.4f} ({result['formatted_address']})")
        else:
            print(f"  {addr}: FAILED")
    
    print()
    
    # 2. 測試 Elevation
    print("2. Elevation API 測試")
    print("-" * 40)
    test_coords = [
        ("太古城", 22.288, 114.220),
        ("山頂", 22.271, 114.150),
        ("大帽山", 22.412, 114.123),
    ]
    for name, lat, lng in test_coords:
        elev = get_elevation(lat, lng)
        if elev:
            print(f"  {name}: {elev:.1f}m")
        else:
            print(f"  {name}: FAILED")
    
    print()
    
    # 3. 測試 Places Nearby Search
    print("3. Places API 測試（太古城周邊 1000m）")
    print("-" * 40)
    pois = search_nearby_pois(22.288, 114.220, radius=1000, place_types=["hospital"])
    for poi in pois[:5]:
        print(f"  {poi['name']}: {poi['distance_m']}m ({poi['sha_type']})")
    
    print()
    
    # 4. DEM 驗證
    print("4. DEM 驗證（SRTM vs Google Elevation）")
    print("-" * 40)
    for name, lat, lng in test_coords:
        result = verify_dem_against_google(lat, lng)
        print(f"  {name}: SRTM={result['srtm_elevation']}m, Google={result['google_elevation']}m, 差異={result['difference']}m ({result['assessment']})")
    
    print()
    print("=== 測試完成 ===")
