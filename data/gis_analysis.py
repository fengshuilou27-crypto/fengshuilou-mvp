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

def _load_terrain_model() -> dict:
    """加載簡化地形模型"""
    data = _load_json_data("terrain_model.json")
    return data


# ===== DEM 地形分析（Phase 5: 真實 SRTM 30m DEM）=====

# 導入 DEM 解析器
try:
    from . import dem_parser
except ImportError:
    import dem_parser


def _estimate_elevation(lat: float, lng: float) -> float:
    """
    查詢指定坐標的高程（米）
    Phase 5: 優先使用真實 SRTM 30m DEM，若不可用則回退到簡化模型
    """
    return dem_parser.get_elevation(lat, lng)


def _calculate_slope_around(lat: float, lng: float, radius: int = 200) -> float:
    """
    計算某點周邊 radius 米內的平均坡度（度）
    Phase 5: 優先使用真實 DEM 數據，若不可用則回退到簡化模型
    """
    return dem_parser.get_slope(lat, lng, radius)


# 保留舊的簡化模型函數（供參考/後備）
def _estimate_elevation_legacy(lat: float, lng: float) -> float:
    """
    [Legacy] 基於簡化地形模型估算任意坐標的高程
    使用已知山峰 + 指數距離衰減模型
    保留作為後備方案
    """
    terrain = _load_terrain_model()
    peaks = terrain.get("peaks", [])
    zones = terrain.get("terrain_zones", [])
    
    # 先找到匹配的 terrain_zone
    base_elev = 20.0
    for zone in zones:
        if (zone["lat_min"] <= lat <= zone["lat_max"] and 
            zone["lng_min"] <= lng <= zone["lng_max"]):
            base_elev = zone["base_elevation"]
            break
    
    # 基於最近山峰的高程貢獻（指數衰減）
    peak_contribution = 0.0
    for peak in peaks:
        if peak.get("type") == "water":
            continue
        dist = haversine_distance(lat, lng, peak["lat"], peak["lng"])
        if dist < 50:  # 50m 內視為在山頂
            return float(peak["elevation"])
        # 指數衰減：山峰影響半徑約 2.5km
        contribution = peak["elevation"] * math.exp(-dist / 2500.0) * 0.15
        peak_contribution += contribution
    
    # 組合高程（基線 + 山峰貢獻）
    estimated = base_elev + peak_contribution
    return max(0, min(1000, estimated))


def _analyze_backing_mountain(lat: float, lng: float, facing: str) -> dict:
    """
    分析「靠山」
    根據坐向，確定「後方」（坐山）方向，計算後方區域的高程特徵
    Phase 5 修復：高地本身（>200m）視為有靠山
    """
    # 解析坐向：如 "子山午向" → 坐山 = 子
    mountain = "子"
    if "山" in facing:
        mountain = facing.split("山")[0].strip()
    
    shanxiang_degrees = {
        "子": 0, "癸": 15, "丑": 30, "艮": 45, "寅": 60, "甲": 75,
        "卯": 90, "乙": 105, "辰": 120, "巽": 135, "巳": 150, "丙": 165,
        "午": 180, "丁": 195, "未": 210, "坤": 225, "申": 240, "庚": 255,
        "酉": 270, "辛": 285, "戌": 300, "乾": 315, "亥": 330, "壬": 345,
    }
    mountain_deg = shanxiang_degrees.get(mountain, 0)
    
    current_elev = _estimate_elevation(lat, lng)
    
    # Phase 5 修復：若自身高程已 > 200m，視為有靠山（自身即為靠山/位於龍脈）
    if current_elev >= 200:
        return {
            "score": 10.0,
            "description": "位於高地之上，自身有靠，龍氣充沛",
            "elevation_diff": round(current_elev, 1),
            "backing_elevations": [round(current_elev, 1)],
            "current_elevation": round(current_elev, 1)
        }
    
    # 在後方（坐山方向）採樣 3 個點（200m, 500m, 1000m）
    backing_elevations = []
    backing_distances = [200, 500, 1000]
    
    for dist in backing_distances:
        lat_offset = (dist / 111000.0) * math.cos(math.radians(mountain_deg))
        lng_offset = (dist / (111000.0 * math.cos(math.radians(lat)))) * math.sin(math.radians(mountain_deg))
        sample_lat = lat + lat_offset
        sample_lng = lng + lng_offset
        elev = _estimate_elevation(sample_lat, sample_lng)
        backing_elevations.append(elev)
    
    avg_backing_elev = sum(backing_elevations) / len(backing_elevations)
    elev_diff = avg_backing_elev - current_elev
    
    if elev_diff >= 100:
        backing_score = 10.0
        backing_desc = "有強力靠山，龍脈有力"
    elif elev_diff >= 50:
        backing_score = 8.0
        backing_desc = "有良好靠山，氣場穩定"
    elif elev_diff >= 20:
        backing_score = 6.0
        backing_desc = "有小山為靠，略有支撐"
    elif elev_diff >= 0:
        backing_score = 4.0
        backing_desc = "靠山較弱，地勢平緩"
    else:
        backing_score = 2.0
        backing_desc = "無靠山，後方低窪（背後空虛）"
    
    return {
        "score": backing_score,
        "description": backing_desc,
        "elevation_diff": round(elev_diff, 1),
        "backing_elevations": [round(e, 1) for e in backing_elevations],
        "current_elevation": round(current_elev, 1)
    }


def _analyze_ming_tang(lat: float, lng: float, facing: str) -> dict:
    """
    分析「明堂」
    根據坐向，確定「前方」（向首）方向，計算前方區域的開闊度
    """
    # 解析坐向：如 "子山午向" → 向首 = 午
    facing_dir = "午"  # 默認
    if "向" in facing:
        facing_dir = facing.split("向")[1].strip() if "向" in facing else "午"
    
    shanxiang_degrees = {
        "子": 0, "癸": 15, "丑": 30, "艮": 45, "寅": 60, "甲": 75,
        "卯": 90, "乙": 105, "辰": 120, "巽": 135, "巳": 150, "丙": 165,
        "午": 180, "丁": 195, "未": 210, "坤": 225, "申": 240, "庚": 255,
        "酉": 270, "辛": 285, "戌": 300, "乾": 315, "亥": 330, "壬": 345,
    }
    
    facing_deg = shanxiang_degrees.get(facing_dir, 180)
    
    # 在前方採樣 3 個點
    front_elevations = []
    front_distances = [200, 500, 1000]
    
    for dist in front_distances:
        lat_offset = (dist / 111000.0) * math.cos(math.radians(facing_deg))
        lng_offset = (dist / (111000.0 * math.cos(math.radians(lat)))) * math.sin(math.radians(facing_deg))
        
        sample_lat = lat + lat_offset
        sample_lng = lng + lng_offset
        
        elev = _estimate_elevation(sample_lat, sample_lng)
        front_elevations.append(elev)
    
    # 明堂評分：前方低且平坦 = 開闊
    current_elev = _estimate_elevation(lat, lng)
    avg_front_elev = sum(front_elevations) / len(front_elevations)
    
    # 前方坡度
    front_slope = _calculate_slope_around(lat, lng, 500)
    
    # 如果前方有明顯高山，阻擋視線
    if max(front_elevations) - current_elev > 100:
        ming_tang_score = 2.0
        ming_tang_desc = "前方有高山阻擋，明堂閉塞"
    elif max(front_elevations) - current_elev > 50:
        ming_tang_score = 4.0
        ming_tang_desc = "前方有丘陵，明堂略受限制"
    elif front_slope < 5:
        ming_tang_score = 9.0
        ming_tang_desc = "前方平坦開闊，明堂極佳"
    elif front_slope < 10:
        ming_tang_score = 7.0
        ming_tang_desc = "前方微緩，明堂尚可"
    else:
        ming_tang_score = 5.0
        ming_tang_desc = "前方有坡，明堂一般"
    
    return {
        "score": ming_tang_score,
        "description": ming_tang_desc,
        "front_slope": round(front_slope, 1),
        "front_elevations": [round(e, 1) for e in front_elevations]
    }


def _analyze_dragon_vein(lat: float, lng: float) -> dict:
    """
    分析「龍脈」
    檢查屋苑是否位於主要山脈的延伸線上
    """
    terrain = _load_terrain_model()
    peaks = terrain.get("peaks", [])
    
    # 找到最近的主要山峰
    nearest_peak = None
    min_dist = float('inf')
    for peak in peaks:
        if peak.get("type") != "peak":
            continue
        dist = haversine_distance(lat, lng, peak["lat"], peak["lng"])
        if dist < min_dist:
            min_dist = dist
            nearest_peak = peak
    
    if not nearest_peak:
        return {"score": 5.0, "description": "無法確定龍脈", "nearest_peak": None}
    
    # 龍脈評分：距離主要山峰越近，龍脈越強
    if min_dist < 2000:
        dragon_score = 10.0
        desc = f"位於{nearest_peak['name']}龍脈近處，龍氣充沛"
    elif min_dist < 5000:
        dragon_score = 8.0
        desc = f"承接{nearest_peak['name']}龍脈餘氣"
    elif min_dist < 10000:
        dragon_score = 6.0
        desc = f"距離{nearest_peak['name']}龍脈較遠"
    else:
        dragon_score = 4.0
        desc = f"遠離主要龍脈，氣場較弱"
    
    return {
        "score": dragon_score,
        "description": desc,
        "nearest_peak": nearest_peak["name"],
        "distance_m": int(min_dist),
        "feng_shui_role": nearest_peak.get("feng_shui_role", "")
    }


def analyze_terrain_feng_shui(lat: float, lng: float, facing: str) -> dict:
    """
    地形風水分析（龍脈 / 靠山 / 明堂）
    Phase 5: 基於真實 SRTM 30m DEM 數據進行分析
    
    使用 rasterio 讀取 GeoTIFF 高程數據，提供 ~30m 分辨率的高程和坡度信息。
    若真實 DEM 不可用，自動回退到簡化地形模型（terrain_model.json）。
    """
    # DEM 估算高程
    current_elevation = _estimate_elevation(lat, lng)
    
    # 靠山分析
    backing = _analyze_backing_mountain(lat, lng, facing)
    
    # 明堂分析
    ming_tang = _analyze_ming_tang(lat, lng, facing)
    
    # 龍脈分析
    dragon = _analyze_dragon_vein(lat, lng)
    
    # 綜合地形評分
    # 靠山 40% + 明堂 35% + 龍脈 25%
    terrain_score = (
        backing["score"] * 0.40 +
        ming_tang["score"] * 0.35 +
        dragon["score"] * 0.25
    )
    
    # 根據坐向微調：坐北向南為理想格局
    if facing in ["子山午向", "壬山丙向", "癸山丁向"]:
        terrain_score += 1.0
    
    terrain_score = min(10, max(0, terrain_score))
    
    # Phase 5: 檢查是否使用真實 DEM
    dem_available = dem_parser.is_dem_available() if hasattr(dem_parser, 'is_dem_available') else False
    confidence = 0.75 if dem_available else 0.60
    dem_status = "真實SRTM30m DEM" if dem_available else "簡化地形模型"
    
    return {
        "status": "success",
        "terrain_score": round(terrain_score, 1),  # 0-10 分
        "backing_mountain": {
            "score": backing["score"],
            "description": backing["description"],
            "elevation_diff": backing["elevation_diff"],
            "current_elevation": backing["current_elevation"]
        },
        "ming_tang": {
            "score": ming_tang["score"],
            "description": ming_tang["description"],
            "front_slope": ming_tang["front_slope"]
        },
        "dragon_vein": {
            "score": dragon["score"],
            "description": dragon["description"],
            "nearest_peak": dragon["nearest_peak"],
            "distance_m": dragon["distance_m"]
        },
        "elevation": round(current_elevation, 1),
        "dem_source": dem_status,
        "confidence": confidence,
        "rationale": (
            f"[{dem_status}] 靠山{backing['description']}({backing['score']:.0f}分) + "
            f"明堂{ming_tang['description']}({ming_tang['score']:.0f}分) + "
            f"龍脈{dragon['description']}({dragon['score']:.0f}分) → "
            f"地形綜合{terrain_score:.1f}分"
        )
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
