#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEM 解析模組 (Phase 5)
使用 rasterio 讀取真實 SRTM 30m GeoTIFF 數據
替換簡化地形模型，提供更準確的高程和坡度分析

數據源：Mapzen / AWS Open Data (SRTM 1 Arc-Second, ~30m 分辨率)
"""

import math
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

# rasterio 為可選依賴，若未安裝則回退到簡化模型
try:
    import rasterio
    from rasterio.sample import sample_gen
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

# DEM 文件路徑（相對於本文件）
DEM_PATH = Path(__file__).parent / "dem" / "hong_kong_dem.tif"

# 全局 DEM 數據集（懶加載）
_dem_dataset = None


def _get_dem_dataset():
    """懶加載 DEM 數據集"""
    global _dem_dataset
    if _dem_dataset is None and RASTERIO_AVAILABLE and DEM_PATH.exists():
        try:
            _dem_dataset = rasterio.open(str(DEM_PATH))
            print(f"[DEM] Loaded: {DEM_PATH.name} ({_dem_dataset.width}x{_dem_dataset.height}, {_dem_dataset.crs})")
        except Exception as e:
            print(f"[DEM] Failed to load: {e}")
            _dem_dataset = False  # 標記為失敗，避免重試
    return _dem_dataset if _dem_dataset is not False else None


def is_dem_available() -> bool:
    """檢查真實 DEM 是否可用"""
    return _get_dem_dataset() is not None


def get_dem_info() -> dict:
    """獲取 DEM 數據集信息"""
    ds = _get_dem_dataset()
    if not ds:
        return {"available": False}
    
    data = ds.read(1)
    valid = data[~np.isnan(data)]
    
    return {
        "available": True,
        "path": str(DEM_PATH),
        "width": ds.width,
        "height": ds.height,
        "crs": str(ds.crs),
        "bounds": ds.bounds,
        "resolution": ds.res,
        "elevation_min": float(valid.min()) if len(valid) > 0 else None,
        "elevation_max": float(valid.max()) if len(valid) > 0 else None,
        "elevation_mean": float(valid.mean()) if len(valid) > 0 else None,
    }


def query_elevation(lat: float, lng: float) -> Optional[float]:
    """
    查詢指定坐標的高程（米）
    使用真實 DEM 數據，若不可用則返回 None
    
    Args:
        lat: 緯度 (WGS84)
        lng: 經度 (WGS84)
    
    Returns:
        高程值（米），或 None（如果 DEM 不可用或坐標在範圍外）
    """
    ds = _get_dem_dataset()
    if not ds:
        return None
    
    # 檢查是否在 bounds 內
    if not (ds.bounds.left <= lng <= ds.bounds.right and 
            ds.bounds.bottom <= lat <= ds.bounds.top):
        return None
    
    try:
        # 使用 rasterio.sample 採樣（支持重投影）
        for val_arr in sample_gen(ds, [(lng, lat)]):
            val = val_arr[0] if hasattr(val_arr, '__getitem__') else val
            if val is None or (isinstance(val, float) and np.isnan(val)):
                return None
            # 修復：負高程視為海平面（0m）
            if val < 0:
                val = 0.0
            return float(val)
    except Exception as e:
        # 回退：手動計算像素坐標
        try:
            row, col = ds.index(lng, lat)
            if 0 <= row < ds.height and 0 <= col < ds.width:
                val = ds.read(1)[row, col]
                if not np.isnan(val):
                    # 修復：負高程視為海平面
                    if val < 0:
                        val = 0.0
                    return float(val)
        except Exception:
            pass
    return None


def query_elevation_batch(coords: list) -> list:
    """
    批量查詢高程
    
    Args:
        coords: [(lat, lng), ...]
    
    Returns:
        [elevation_or_None, ...]
    """
    ds = _get_dem_dataset()
    if not ds:
        return [None] * len(coords)
    
    results = []
    for lat, lng in coords:
        results.append(query_elevation(lat, lng))
    return results


def calculate_slope(lat: float, lng: float, radius: int = 200) -> Optional[float]:
    """
    計算某點周邊 radius 米內的平均坡度（度）
    使用真實 DEM 數據的 4 方向採樣
    
    Args:
        lat: 緯度
        lng: 經度
        radius: 採樣半徑（米），默認 200m
    
    Returns:
        平均坡度（度），或 None（如果 DEM 不可用）
    """
    ds = _get_dem_dataset()
    if not ds:
        return None
    
    center_elev = query_elevation(lat, lng)
    if center_elev is None:
        return None
    
    # 4 方向採樣（北東南西）
    # 將米轉換為度偏移
    lat_offset_m = radius / 111000.0
    lng_offset_m = radius / (111000.0 * math.cos(math.radians(lat)))
    
    directions = [
        (lat + lat_offset_m, lng, "N"),
        (lat, lng + lng_offset_m, "E"),
        (lat - lat_offset_m, lng, "S"),
        (lat, lng - lng_offset_m, "W"),
    ]
    
    slopes = []
    for dlat, dlng, _ in directions:
        elev = query_elevation(dlat, dlng)
        if elev is not None:
            delta_elev = abs(elev - center_elev)
            slope = math.degrees(math.atan(delta_elev / radius))
            slopes.append(slope)
    
    return sum(slopes) / len(slopes) if slopes else 0.0


def sample_direction(
    lat: float, 
    lng: float, 
    direction_deg: float, 
    distances: list = [200, 500, 1000]
) -> list:
    """
    沿指定方向採樣高程
    
    Args:
        lat, lng: 起點坐標
        direction_deg: 方向角度（0=北, 90=東, 180=南, 270=西）
        distances: 採樣距離列表（米）
    
    Returns:
        [(distance, elevation), ...] 或 None
    """
    ds = _get_dem_dataset()
    if not ds:
        return None
    
    results = []
    for dist in distances:
        lat_offset = (dist / 111000.0) * math.cos(math.radians(direction_deg))
        lng_offset = (dist / (111000.0 * math.cos(math.radians(lat)))) * math.sin(math.radians(direction_deg))
        
        sample_lat = lat + lat_offset
        sample_lng = lng + lng_offset
        
        elev = query_elevation(sample_lat, sample_lng)
        results.append((dist, elev))
    
    return results


def analyze_elevation_profile(
    lat: float, 
    lng: float, 
    direction_deg: float, 
    max_distance: int = 2000, 
    step: int = 100
) -> list:
    """
    分析指定方向的高程剖面
    
    Args:
        lat, lng: 起點
        direction_deg: 方向角度
        max_distance: 最大距離（米）
        step: 步長（米）
    
    Returns:
        [(distance, elevation), ...]
    """
    ds = _get_dem_dataset()
    if not ds:
        return []
    
    results = []
    for dist in range(0, max_distance + 1, step):
        lat_offset = (dist / 111000.0) * math.cos(math.radians(direction_deg))
        lng_offset = (dist / (111000.0 * math.cos(math.radians(lat)))) * math.sin(math.radians(direction_deg))
        
        sample_lat = lat + lat_offset
        sample_lng = lng + lng_offset
        
        elev = query_elevation(sample_lat, sample_lng)
        if elev is not None:
            results.append((dist, elev))
    
    return results


# ===== 簡化模型回退（當 DEM 不可用時）=====

def _fallback_estimate_elevation(lat: float, lng: float) -> float:
    """
    簡化地形模型回退
    從 terrain_model.json 載入已知山峰和地形區域進行估算
    """
    import json
    
    data_path = Path(__file__).parent / "terrain_model.json"
    if not data_path.exists():
        return 20.0
    
    with open(data_path, 'r', encoding='utf-8') as f:
        terrain = json.load(f)
    
    peaks = terrain.get("peaks", [])
    zones = terrain.get("terrain_zones", [])
    
    # 找到匹配的 terrain_zone
    base_elev = 20.0
    for zone in zones:
        if (zone["lat_min"] <= lat <= zone["lat_max"] and 
            zone["lng_min"] <= lng <= zone["lng_max"]):
            base_elev = zone["base_elevation"]
            break
    
    # 基於最近山峰的指數衰減
    peak_contribution = 0.0
    for peak in peaks:
        if peak.get("type") == "water":
            continue
        # 使用 haversine 計算距離
        R = 6371000
        phi1 = math.radians(lat)
        phi2 = math.radians(peak["lat"])
        delta_phi = math.radians(peak["lat"] - lat)
        delta_lambda = math.radians(peak["lng"] - lng)
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        if dist < 50:
            return float(peak["elevation"])
        contribution = peak["elevation"] * math.exp(-dist / 2500.0) * 0.15
        peak_contribution += contribution
    
    estimated = base_elev + peak_contribution
    return max(0, min(1000, estimated))


def get_elevation(lat: float, lng: float) -> float:
    """
    獲取高程：優先使用真實 DEM，若不可用則回退到簡化模型
    """
    elev = query_elevation(lat, lng)
    if elev is not None:
        return elev
    return _fallback_estimate_elevation(lat, lng)


def get_slope(lat: float, lng: float, radius: int = 200) -> float:
    """
    獲取坡度：優先使用真實 DEM，若不可用則回退到簡化模型估算
    """
    slope = calculate_slope(lat, lng, radius)
    if slope is not None:
        return slope
    
    # 簡化模型回退：估算坡度
    center_elev = _fallback_estimate_elevation(lat, lng)
    lat_offset_m = radius / 111000.0
    lng_offset_m = radius / (111000.0 * math.cos(math.radians(lat)))
    
    directions = [
        (lat + lat_offset_m, lng),
        (lat, lng + lng_offset_m),
        (lat - lat_offset_m, lng),
        (lat, lng - lng_offset_m),
    ]
    
    slopes = []
    for dlat, dlng in directions:
        elev = _fallback_estimate_elevation(dlat, dlng)
        delta_elev = abs(elev - center_elev)
        slope = math.degrees(math.atan(delta_elev / radius))
        slopes.append(slope)
    
    return sum(slopes) / len(slopes) if slopes else 0.0


# ===== 測試 =====
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== DEM Parser Test ===")
    print(f"rasterio available: {RASTERIO_AVAILABLE}")
    print(f"DEM file exists: {DEM_PATH.exists()}")
    print(f"DEM file path: {DEM_PATH}")
    
    if is_dem_available():
        info = get_dem_info()
        print(f"\nDEM Info:")
        for k, v in info.items():
            print(f"  {k}: {v}")
        
        # 測試幾個香港地點
        test_points = [
            ("太古城", 22.288, 114.220),
            ("嘉湖山莊", 22.450, 113.995),
            ("屯門市廣場", 22.391, 113.978),
            ("山頂", 22.271, 114.150),
            ("大帽山", 22.412, 114.123),
        ]
        
        print("\nElevation queries:")
        for name, lat, lng in test_points:
            elev = query_elevation(lat, lng)
            fallback = _fallback_estimate_elevation(lat, lng)
            print(f"  {name}: DEM={elev:.1f}m, fallback={fallback:.1f}m")
    else:
        print("DEM not available, testing fallback only...")
        test_points = [
            ("太古城", 22.288, 114.220),
            ("嘉湖山莊", 22.450, 113.995),
        ]
        for name, lat, lng in test_points:
            fallback = _fallback_estimate_elevation(lat, lng)
            print(f"  {name}: fallback={fallback:.1f}m")
