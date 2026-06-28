#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIS 風水分析模組
基於地理坐標的風水分析：煞氣掃描、地形分析、水法評估
Phase 1: 基於手動標註坐標 + 煞氣 POI 數據庫
Phase 2: 接入 DEM（數字高程模型）進行龍脈/靠山/明堂分析
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Optional

# ===== 常量 =====
HONG_KONG_CENTER = {"lat": 22.3193, "lng": 114.1694}  # 香港中心點
VICTORIA_HARBOR_CENTERS = [
    {"lat": 22.2870, "lng": 114.1750, "name": "維港東部"},
    {"lat": 22.2950, "lng": 114.1650, "name": "維港中部"},
    {"lat": 22.3050, "lng": 114.1550, "name": "維港西部"},
]
SHA_SEVERITY_PENALTY = {
    "critical": -10,
    "severe": -7,
    "moderate": -5,
    "mild": -3,
}
SHA_SCAN_RADIUS_METERS = 500  # 掃描半徑


# ===== 數據加載 =====

def _load_json_data(filename: str) -> dict:
    """加載 JSON 數據文件"""
    data_path = Path(__file__).parent / filename
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# 懶加載數據
_estate_coords = None
_sha_pois = None


def _get_estate_coords() -> dict:
    """獲取屋苑坐標數據"""
    global _estate_coords
    if _estate_coords is None:
        data = _load_json_data("estate_coordinates.json")
        _estate_coords = data.get("estates", {})
    return _estate_coords


def _get_sha_pois() -> list:
    """獲取煞氣 POI 數據"""
    global _sha_pois
    if _sha_pois is None:
        data = _load_json_data("sha_poi_hk.json")
        _sha_pois = data.get("pois", [])
    return _sha_pois


# ===== 地理計算工具 =====

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Haversine 公式計算兩點間距離（米）
    """
    R = 6371000  # 地球半徑（米）
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculate_bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    """
    計算從點1到點2的方位角，返回 24 山向
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lng2 - lng1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360) % 360

    # 將 360° 映射到 24 山向
    return _bearing_to_shanxiang(bearing)


def _bearing_to_shanxiang(bearing: float) -> str:
    """將方位角映射到 24 山向"""
    # 24 山向每個 15°
    shanxiang_list = [
        "子", "癸", "丑", "艮", "寅", "甲", "卯", "乙", "辰", "巽", "巳", "丙",
        "午", "丁", "未", "坤", "申", "庚", "酉", "辛", "戌", "乾", "亥", "壬"
    ]
    idx = round(bearing / 15) % 24
    return shanxiang_list[idx]


def _shanxiang_to_degrees(shanxiang: str) -> float:
    """24 山向轉為角度（中間值）"""
    shanxiang_map = {
        "子": 0, "癸": 15, "丑": 30, "艮": 45, "寅": 60, "甲": 75,
        "卯": 90, "乙": 105, "辰": 120, "巽": 135, "巳": 150, "丙": 165,
        "午": 180, "丁": 195, "未": 210, "坤": 225, "申": 240, "庚": 255,
        "酉": 270, "辛": 285, "戌": 300, "乾": 315, "亥": 330, "壬": 345,
    }
    return shanxiang_map.get(shanxiang, 0)


# ===== 煞氣掃描 =====

def scan_nearby_shas(lat: float, lng: float, radius: int = SHA_SCAN_RADIUS_METERS) -> dict:
    """
    掃描指定坐標周邊的煞氣 POI
    Returns: {
        "shas_found": [...],
        "total_penalty": -15,
        "nearest_sha_distance": 120,
        "scan_radius": 500
    }
    """
    pois = _get_sha_pois()
    found_shas = []
    total_penalty = 0
    nearest_distance = float('inf')

    for poi in pois:
        distance = haversine_distance(lat, lng, poi["lat"], poi["lng"])
        if distance <= radius:
            severity = poi.get("severity", "mild")
            penalty = SHA_SEVERITY_PENALTY.get(severity, -3)
            # 距離衰減：越近影響越大
            distance_factor = max(0.3, 1 - (distance / radius))
            adjusted_penalty = round(penalty * distance_factor, 1)

            found_shas.append({
                "name": poi["name"],
                "sha_type": poi["sha_type"],
                "severity": severity,
                "distance_m": int(distance),
                "penalty": adjusted_penalty,
                "description": poi.get("description", ""),
                "feng_shui_effect": poi.get("feng_shui_effect", "")
            })
            total_penalty += adjusted_penalty
            nearest_distance = min(nearest_distance, distance)

    # 限制總扣分上限
    total_penalty = max(-25, total_penalty)

    return {
        "status": "success",
        "shas_found": found_shas,
        "total_penalty": total_penalty,
        "nearest_sha_distance": int(nearest_distance) if found_shas else None,
        "scan_radius": radius,
        "confidence": 0.6 if found_shas else 0.5,
        "rationale": f"周邊{radius}m內掃描到{len(found_shas)}項煞氣，總扣分{abs(total_penalty)}分" if found_shas else
                     f"周邊{radius}m內未檢測到已知煞氣"
    }


def scan_sha_by_estate(estate_name: str) -> dict:
    """
    根據屋苑名稱掃描周邊煞氣（使用預存坐標）
    """
    coords = _get_estate_coords()
    estate_data = coords.get(estate_name)

    if not estate_data:
        return {
            "status": "no_coords",
            "shas_found": [],
            "total_penalty": 0,
            "rationale": f"屋苑「{estate_name}」尚未標註地理坐標，無法進行周邊煞氣掃描"
        }

    return scan_nearby_shas(estate_data["lat"], estate_data["lng"])


# ===== 水法分析 =====

def analyze_water_feng_shui(lat: float, lng: float, facing: str) -> dict:
    """
    分析水法風水（維港/河流/海景）
    Phase 1: 基於維港中心點計算相對方位和距離
    Phase 2: 接入 DEM + 海岸線數據進行精確分析
    """
    # 找到最近的維港中心點
    nearest_harbor = None
    min_dist = float('inf')
    for harbor in VICTORIA_HARBOR_CENTERS:
        dist = haversine_distance(lat, lng, harbor["lat"], harbor["lng"])
        if dist < min_dist:
            min_dist = dist
            nearest_harbor = harbor

    # 計算單位朝向與維港方向的夾角
    if nearest_harbor:
        harbor_direction = calculate_bearing(lat, lng, nearest_harbor["lat"], nearest_harbor["lng"])
        facing_deg = _shanxiang_to_degrees(facing.split("向")[0] if "向" in facing else facing)
        harbor_deg = _shanxiang_to_degrees(harbor_direction)
        angle_diff = abs(facing_deg - harbor_deg)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # 水法評分：朝向維港 = 旺財（0-10 分）
        if angle_diff <= 30:
            water_score = 10
            water_rating = "正對維港，極旺財"
        elif angle_diff <= 60:
            water_score = 7
            water_rating = "偏對維港，財運佳"
        elif angle_diff <= 90:
            water_score = 4
            water_rating = "側對維港，財運一般"
        else:
            water_score = 1
            water_rating = "背對維港，財運受限"
    else:
        water_score = 0
        water_rating = "無法判斷水法"
        min_dist = None

    return {
        "status": "success",
        "water_score": water_score,  # 0-10 分
        "water_rating": water_rating,
        "nearest_harbor": nearest_harbor["name"] if nearest_harbor else None,
        "harbor_distance_m": int(min_dist) if min_dist else None,
        "harbor_direction": harbor_direction if nearest_harbor else None,
        "facing_harbor_angle_diff": int(angle_diff) if nearest_harbor else None,
        "confidence": 0.5,  # Phase 1 精度有限
        "rationale": f"{water_rating}，距離維港約{int(min_dist/1000) if min_dist else '?'}km" if nearest_harbor else "暫無法分析水法"
    }


# ===== 地形風水分析（Phase 1 骨架）=====

def analyze_terrain_feng_shui(lat: float, lng: float, facing: str) -> dict:
    """
    地形風水分析（龍脈 / 靠山 / 明堂）
    Phase 1: 基於香港宏觀地形的簡化分析
    Phase 2: 接入 DEM 進行精確計算
    """
    # 香港宏觀地形：北高南低（九龍山脈），西高東低（大嶼山/港島）
    # 簡化規則：
    # - 新界北部（粉嶺/上水/元朗）：背靠山脈，有靠山
    # - 九龍：背靠獅子山/飛鵝山，有靠山
    # - 港島：背山面海，但山勢較陡
    # - 離島：平地為主，靠山較弱

    # 基於緯度/經度的簡化地形評估
    terrain_score = 5.0  # 基礎分
    backing = "一般"
    ming_tang = "一般"

    # 新界北（有靠山）
    if lat > 22.45:
        terrain_score = 8.0
        backing = "九龍山脈為靠，山勢綿長"
        ming_tang = "開闊，面向元朗平原"
    # 九龍/沙田（獅子山為靠）
    elif 22.35 < lat <= 22.45 and 114.15 < lng < 114.25:
        terrain_score = 8.5
        backing = "獅子山/飛鵝山為靠，龍脈有力"
        ming_tang = "面向維港，明堂開闊"
    # 港島（背山面海）
    elif lng > 114.15 and 22.20 < lat < 22.30:
        terrain_score = 7.5
        backing = "太平山為靠，但山勢較陡"
        ming_tang = "面對維港，明堂極佳"
    # 西貢/將軍澳（依山傍海）
    elif lng > 114.25 and 22.25 < lat < 22.35:
        terrain_score = 7.0
        backing = "西貢山脈為靠"
        ming_tang = "面向吐露港/牛尾海"
    # 屯門/元朗（平原）
    elif lng < 114.10:
        terrain_score = 6.0
        backing = "青山為靠，但距離較遠"
        ming_tang = "面向后海灣/珠江口"
    # 東涌/大嶼山
    elif lat < 22.30 and lng < 114.05:
        terrain_score = 5.5
        backing = "大嶼山為靠，但地勢平緩"
        ming_tang = "面向機場/海景"

    # 根據朝向微調
    if facing in ["子山午向", "壬山丙向", "癸山丁向"]:
        # 坐北向南，符合香港「背山面海」理想格局
        terrain_score += 1.5

    terrain_score = min(10, max(0, terrain_score))

    return {
        "status": "success",
        "terrain_score": round(terrain_score, 1),  # 0-10 分
        "backing_mountain": backing,
        "ming_tang": ming_tang,
        "dragon_vein": "Phase 1 簡化評估，Phase 2 接入 DEM 後可精確計算龍脈",
        "confidence": 0.45,  # Phase 1 精度較低
        "rationale": f"{backing}，{ming_tang}，地形綜合得分{terrain_score}分"
    }


# ===== 主入口：整合 GIS 分析 =====

def analyze_gis_feng_shui(
    estate_name: str = None,
    lat: float = None,
    lng: float = None,
    facing: str = None
) -> dict:
    """
    整合 GIS 風水分析入口
    優先使用 estate_name 查詢預存坐標，否則使用 lat/lng
    """
    # 獲取坐標
    if estate_name and not (lat and lng):
        coords = _get_estate_coords()
        estate_data = coords.get(estate_name)
        if estate_data:
            lat = estate_data["lat"]
            lng = estate_data["lng"]
        else:
            return {
                "status": "no_coords",
                "score": 0,
                "max_score": 0,
                "rationale": f"屋苑「{estate_name}」尚未標註地理坐標"
            }

    if not (lat and lng):
        return {
            "status": "error",
            "score": 0,
            "max_score": 0,
            "rationale": "未提供坐標或屋苑名稱"
        }

    # 執行各項分析
    sha_result = scan_nearby_shas(lat, lng)
    water_result = analyze_water_feng_shui(lat, lng, facing) if facing else {"status": "no_facing", "water_score": 0}
    terrain_result = analyze_terrain_feng_shui(lat, lng, facing) if facing else {"status": "no_facing", "terrain_score": 5}

    # 整合分數（GIS 模組總分 20 分）
    # 煞氣：直接扣分（已負值）
    # 水法：0-10 → 轉為 0-8 分
    # 地形：0-10 → 轉為 0-7 分
    water_norm = (water_result.get("water_score", 0) / 10) * 8
    terrain_norm = (terrain_result.get("terrain_score", 5) / 10) * 7
    sha_penalty = sha_result.get("total_penalty", 0)

    total_gis_score = water_norm + terrain_norm + sha_penalty
    total_gis_score = max(-10, min(20, total_gis_score))

    return {
        "status": "success",
        "score": round(total_gis_score, 1),
        "max_score": 20,
        "water_feng_shui": water_result,
        "terrain_feng_shui": terrain_result,
        "sha_scan": sha_result,
        "confidence": 0.55,
        "rationale": (
            f"GIS風水分析：水法{water_result.get('water_rating', '未知')}({water_norm:.1f}分) + "
            f"地形{terrain_result.get('terrain_score', 0)}分({terrain_norm:.1f}分) + "
            f"煞氣{sha_penalty:.1f}分 = 總分{total_gis_score:.1f}分"
        )
    }


# ===== 測試 =====
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    results = {}
    
    # 測試太古城
    results["太古城"] = analyze_gis_feng_shui(estate_name="太古城", facing="子山午向")
    
    # 測試嘉湖山莊
    results["嘉湖山莊"] = analyze_gis_feng_shui(estate_name="嘉湖山莊", facing="子山午向")
    
    # 測試屯門（靠近發電廠）
    results["屯門市廣場"] = analyze_gis_feng_shui(estate_name="屯門市廣場", facing="子山午向")
    
    # 寫入文件
    output_path = Path(__file__).parent.parent / "gis_test_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Test results saved to {output_path}")
