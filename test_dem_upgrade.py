#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 DEM 升級驗證測試
比較真實 SRTM 30m DEM 與簡化地形模型的差異
驗證 DEM 升級是否提升風水匹配邏輯
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
from pathlib import Path

# 確保能導入 mvp_code 模組
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import dem_parser
from data.gis_analysis import analyze_terrain_feng_shui, analyze_gis_feng_shui

# 測試屋苑（涵蓋不同地形類型）
test_estates = [
    ("太古城", 22.288, 114.220, "子山午向", "港島東臨海"),
    ("嘉湖山莊", 22.450, 113.995, "子山午向", "天水圍低地"),
    ("屯門市廣場", 22.391, 113.978, "子山午向", "屯門靠山"),
    ("山頂", 22.271, 114.150, "午山子向", "港島高海拔"),
    ("大帽山", 22.412, 114.123, "子山午向", "香港最高峰"),
    ("西貢", 22.381, 114.273, "午山子向", "西貢郊野"),
    ("荃灣", 22.370, 114.115, "子山午向", "荃灣谷地"),
    ("沙田", 22.383, 114.188, "子山午向", "沙田平原"),
]

print("=" * 80)
print("Phase 5 DEM 升級驗證測試")
print("=" * 80)
print(f"DEM 可用: {dem_parser.is_dem_available()}")
print(f"DEM 路徑: {dem_parser.DEM_PATH}")
print(f"DEM 信息: {dem_parser.get_dem_info()}")
print()

# 1. 高程比較
print("-" * 80)
print("1. 高程比較 (真實 DEM vs 簡化模型)")
print("-" * 80)
print(f"{'地點':<12} {'類型':<12} {'DEM高程':<10} {'簡化模型':<10} {'差異':<10} {'評估'}")
print("-" * 80)

for name, lat, lng, facing, desc in test_estates:
    dem_elev = dem_parser.query_elevation(lat, lng)
    fallback_elev = dem_parser._fallback_estimate_elevation(lat, lng)
    diff = (dem_elev - fallback_elev) if dem_elev else 0
    
    if dem_elev is None:
        assess = "DEM不可用"
    elif abs(diff) < 20:
        assess = "基本一致"
    elif diff > 50:
        assess = "簡化模型嚴重低估"
    elif diff < -50:
        assess = "簡化模型嚴重高估"
    elif diff > 0:
        assess = "簡化模型低估"
    else:
        assess = "簡化模型高估"
    
    dem_str = f"{dem_elev:.1f}m" if dem_elev else "N/A"
    print(f"{name:<12} {desc:<12} {dem_str:<10} {fallback_elev:<10.1f}m {diff:+7.1f}m  {assess}")

print()

# 2. 地形分析比較
print("-" * 80)
print("2. 地形風水分析 (DEM 升級後)")
print("-" * 80)

results = {}
for name, lat, lng, facing, desc in test_estates:
    result = analyze_terrain_feng_shui(lat, lng, facing)
    results[name] = result
    
    print(f"\n【{name}】{desc}")
    print(f"  DEM來源: {result['dem_source']}")
    print(f"  當前高程: {result['elevation']}m")
    print(f"  地形總分: {result['terrain_score']}/10")
    print(f"  靠山: {result['backing_mountain']['description']} ({result['backing_mountain']['score']:.0f}分)")
    print(f"  明堂: {result['ming_tang']['description']} ({result['ming_tang']['score']:.0f}分)")
    print(f"  龍脈: {result['dragon_vein']['description']} ({result['dragon_vein']['score']:.0f}分)")
    print(f"  信心度: {result['confidence']}")

print()

# 3. 坡度分析
print("-" * 80)
print("3. 坡度分析 (真實 DEM)")
print("-" * 80)
print(f"{'地點':<12} {'200m坡度':<12} {'500m坡度':<12} {'1000m坡度':<12} {'評估'}")
print("-" * 80)

for name, lat, lng, facing, desc in test_estates:
    slope_200 = dem_parser.calculate_slope(lat, lng, 200)
    slope_500 = dem_parser.calculate_slope(lat, lng, 500)
    slope_1000 = dem_parser.calculate_slope(lat, lng, 1000)
    
    if slope_200 is None:
        assess = "DEM不可用"
    elif slope_200 < 2:
        assess = "平坦"
    elif slope_200 < 5:
        assess = "微緩"
    elif slope_200 < 10:
        assess = "中等坡度"
    elif slope_200 < 20:
        assess = "較陡"
    else:
        assess = "陡峭"
    
    s200 = f"{slope_200:.1f}°" if slope_200 else "N/A"
    s500 = f"{slope_500:.1f}°" if slope_500 else "N/A"
    s1000 = f"{slope_1000:.1f}°" if slope_1000 else "N/A"
    print(f"{name:<12} {s200:<12} {s500:<12} {s1000:<12} {assess}")

print()

# 4. 關鍵發現
print("-" * 80)
print("4. 關鍵發現")
print("-" * 80)

findings = []

# 分析高程差異
for name, lat, lng, facing, desc in test_estates:
    dem_elev = dem_parser.query_elevation(lat, lng)
    fallback_elev = dem_parser._fallback_estimate_elevation(lat, lng)
    if dem_elev and abs(dem_elev - fallback_elev) > 50:
        findings.append(f"  • {name}({desc}): 簡化模型偏差 {dem_elev - fallback_elev:+.1f}m (DEM={dem_elev:.1f}m, 簡化={fallback_elev:.1f}m)")

# 分析地形評分變化
for name, lat, lng, facing, desc in test_estates:
    result = results[name]
    if result['terrain_score'] < 4:
        findings.append(f"  • {name}({desc}): 地形評分較低 ({result['terrain_score']}/10)，{result['backing_mountain']['description']}")
    elif result['terrain_score'] > 8:
        findings.append(f"  • {name}({desc}): 地形評分優秀 ({result['terrain_score']}/10)，{result['ming_tang']['description']}")

if findings:
    for f in findings:
        print(f)
else:
    print("  未發現顯著異常")

print()

# 5. 保存結果
output_path = Path("dem_upgrade_report.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        "dem_info": dem_parser.get_dem_info(),
        "elevation_comparison": [
            {
                "name": name,
                "lat": lat,
                "lng": lng,
                "dem_elevation": dem_parser.query_elevation(lat, lng),
                "fallback_elevation": dem_parser._fallback_estimate_elevation(lat, lng),
                "description": desc
            }
            for name, lat, lng, _, desc in test_estates
        ],
        "terrain_analysis": results,
    }, f, ensure_ascii=False, indent=2)

print(f"報告已保存: {output_path}")
print()
print("=" * 80)
print("Phase 5 DEM 升級驗證測試完成")
print("=" * 80)
