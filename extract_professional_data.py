#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專業飛星數據提取與更新腳本
從福山堂 (fushantang.com) 提取正確的玄空飛星數據
更新 flying_star.py 中的硬編碼數據
"""

import json

# 九宮方位順序（從西北開始順時針）
GRID_POSITIONS = [
    "northwest", "north", "northeast",
    "west", "center", "east",
    "southwest", "south", "southeast"
]

# 中文數字到阿拉伯數字的映射
CHINESE_TO_NUM = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9
}

# ==================== 八運 正卦數據（從福山堂提取）====================
# 格式：每個山向 9 個數字，依次為 NW, N, NE, W, C, E, SW, S, SE
# 山星和向星分開存儲

YUN_8_DATA = {
    # 子山午向 / 癸山丁向（正卦相同）- 八運雙星會向
    "子山午向": {
        "mountain": [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "facing":   [4, 8, 6, 5, 3, 1, 9, 7, 2],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。坐北朝南，正卦"
    },
    "癸山丁向": {
        "mountain": [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "facing":   [4, 8, 6, 5, 3, 1, 9, 7, 2],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。癸山丁向正卦"
    },
    # 午山子向 / 丁山癸向（正卦相同）- 八運雙星會向
    "午山子向": {
        "mountain": [4, 8, 6, 5, 3, 1, 9, 7, 2],
        "facing":   [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。坐南朝北，正卦"
    },
    "丁山癸向": {
        "mountain": [4, 8, 6, 5, 3, 1, 9, 7, 2],
        "facing":   [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。丁山癸向正卦"
    },
    # 丑山未向 / 未山丑向（正卦相同）- 八運到山到向
    "丑山未向": {
        "mountain": [8, 3, 1, 9, 5, 7, 4, 6, 2],
        "facing":   [8, 1, 6, 7, 2, 9, 3, 4, 5],
        "pan_type": "到山到向",
        "note": "八運到山到向，丁財兩得。坐東北朝西南，正卦"
    },
    "未山丑向": {
        "mountain": [8, 1, 6, 7, 2, 9, 3, 4, 5],
        "facing":   [8, 3, 1, 9, 5, 7, 4, 6, 2],
        "pan_type": "到山到向",
        "note": "八運到山到向，丁財兩得。坐西南朝東北，正卦"
    },
    # 艮山坤向 / 寅山申向（正卦相同）- 八運上山下水
    "艮山坤向": {
        "mountain": [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "facing":   [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "pan_type": "上山下水",
        "note": "八運上山下水，損財傷丁。坐東南朝西北，正卦"
    },
    "寅山申向": {
        "mountain": [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "facing":   [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "pan_type": "上山下水",
        "note": "八運上山下水，損財傷丁。寅山申向正卦"
    },
    # 坤山艮向 / 申山寅向（正卦相同）- 八運上山下水
    "坤山艮向": {
        "mountain": [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "facing":   [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "pan_type": "上山下水",
        "note": "八運上山下水，損財傷丁。坐西南朝東北，正卦"
    },
    "申山寅向": {
        "mountain": [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "facing":   [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "pan_type": "上山下水",
        "note": "八運上山下水，損財傷丁。申山寅向正卦"
    },
    # 卯山酉向 / 乙山辛向（正卦相同）- 八運雙星會向
    "卯山酉向": {
        "mountain": [6, 1, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [5, 6, 4, 3, 1, 9, 8, 7, 2],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。坐東朝西，正卦"
    },
    "乙山辛向": {
        "mountain": [6, 1, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [5, 6, 4, 3, 1, 9, 8, 7, 2],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。乙山辛向正卦"
    },
    # 酉山卯向 / 辛山乙向（正卦相同）- 八運雙星會向
    "酉山卯向": {
        "mountain": [5, 6, 4, 3, 1, 9, 8, 7, 2],
        "facing":   [6, 1, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。坐西朝東，正卦"
    },
    "辛山乙向": {
        "mountain": [5, 6, 4, 3, 1, 9, 8, 7, 2],
        "facing":   [6, 1, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "雙星會向",
        "note": "八運雙星會向，旺財不旺丁。辛山乙向正卦"
    },
    # 辰山戌向 / 戌山辰向（正卦相同）- 八運上山下水
    "辰山戌向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [7, 9, 5, 6, 4, 2, 1, 3, 8],
        "pan_type": "上山下水",
        "note": "八運上山下水，損財傷丁。辰山戌向正卦"
    },
    "戌山辰向": {
        "mountain": [7, 9, 5, 6, 4, 2, 1, 3, 8],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "上山下水",
        "note": "八運上山下水，損財傷丁。戌山辰向正卦"
    },
    # 巽山乾向 / 巳山亥向（正卦相同）- 八運到山到向
    "巽山乾向": {
        "mountain": [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "到山到向",
        "note": "八運到山到向，丁財兩得。巽山乾向正卦"
    },
    "巳山亥向": {
        "mountain": [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "到山到向",
        "note": "八運到山到向，丁財兩得。巳山亥向正卦"
    },
    # 乾山巽向 / 亥山巳向（正卦相同）- 八運到山到向
    "乾山巽向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "到山到向",
        "note": "八運到山到向，丁財兩得。乾山巽向正卦"
    },
    "亥山巳向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "到山到向",
        "note": "八運到山到向，丁財兩得。亥山巳向正卦"
    },
    # 丙山壬向 / 甲山庚向（正卦）
    "丙山壬向": {
        "mountain": [5, 1, 3, 4, 8, 6, 9, 7, 2],
        "facing":   [6, 8, 4, 5, 3, 1, 7, 9, 2],
        "pan_type": "其他",
        "note": "八運丙山壬向正卦"
    },
    "甲山庚向": {
        "mountain": [8, 4, 6, 5, 3, 1, 9, 7, 2],
        "facing":   [7, 9, 2, 1, 5, 3, 4, 6, 8],
        "pan_type": "其他",
        "note": "八運甲山庚向正卦"
    },
    "壬山丙向": {
        "mountain": [6, 8, 4, 5, 3, 1, 7, 9, 2],
        "facing":   [5, 1, 3, 4, 8, 6, 9, 7, 2],
        "pan_type": "其他",
        "note": "八運壬山丙向正卦"
    },
    "庚山甲向": {
        "mountain": [7, 9, 2, 1, 5, 3, 4, 6, 8],
        "facing":   [8, 4, 6, 5, 3, 1, 9, 7, 2],
        "pan_type": "其他",
        "note": "八運庚山甲向正卦"
    },
}

# ==================== 九運 正卦數據（從福山堂提取）====================
YUN_9_DATA = {
    # 子山午向 / 癸山丁向（正卦相同）- 九運雙星會向
    "子山午向": {
        "mountain": [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "facing":   [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。子山午向正卦"
    },
    "癸山丁向": {
        "mountain": [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "facing":   [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。癸山丁向正卦"
    },
    # 午山子向 / 丁山癸向（正卦相同）- 九運雙星會向
    "午山子向": {
        "mountain": [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "facing":   [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。午山子向正卦"
    },
    "丁山癸向": {
        "mountain": [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "facing":   [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。丁山癸向正卦"
    },
    # 丑山未向 / 未山丑向（正卦相同）- 九運上山下水
    "丑山未向": {
        "mountain": [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "facing":   [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "pan_type": "上山下水",
        "note": "九運上山下水，損財傷丁。丑山未向正卦"
    },
    "未山丑向": {
        "mountain": [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "facing":   [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "pan_type": "上山下水",
        "note": "九運上山下水，損財傷丁。未山丑向正卦"
    },
    # 艮山坤向 / 寅山申向（正卦相同）- 九運到山到向
    "艮山坤向": {
        "mountain": [8, 3, 1, 9, 5, 7, 4, 6, 2],
        "facing":   [8, 1, 6, 7, 2, 9, 3, 4, 5],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。艮山坤向正卦"
    },
    "寅山申向": {
        "mountain": [8, 3, 1, 9, 5, 7, 4, 6, 2],
        "facing":   [8, 1, 6, 7, 2, 9, 3, 4, 5],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。寅山申向正卦"
    },
    # 坤山艮向 / 申山寅向（正卦相同）- 九運到山到向
    "坤山艮向": {
        "mountain": [8, 1, 6, 7, 2, 9, 3, 4, 5],
        "facing":   [8, 3, 1, 9, 5, 7, 4, 6, 2],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。坤山艮向正卦"
    },
    "申山寅向": {
        "mountain": [8, 1, 6, 7, 2, 9, 3, 4, 5],
        "facing":   [8, 3, 1, 9, 5, 7, 4, 6, 2],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。申山寅向正卦"
    },
    # 卯山酉向 / 乙山辛向（正卦相同）- 九運到山到向
    "卯山酉向": {
        "mountain": [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。卯山酉向正卦"
    },
    "乙山辛向": {
        "mountain": [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。乙山辛向正卦"
    },
    # 酉山卯向 / 辛山乙向（正卦相同）- 九運到山到向
    "酉山卯向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。酉山卯向正卦"
    },
    "辛山乙向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "到山到向",
        "note": "九運到山到向，丁財兩得。辛山乙向正卦"
    },
    # 辰山戌向 / 戌山辰向（正卦相同）- 九運上山下水
    "辰山戌向": {
        "mountain": [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "facing":   [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "pan_type": "上山下水",
        "note": "九運上山下水，損財傷丁。辰山戌向正卦"
    },
    "戌山辰向": {
        "mountain": [5, 3, 1, 2, 8, 7, 9, 4, 6],
        "facing":   [2, 7, 9, 1, 5, 3, 8, 6, 4],
        "pan_type": "上山下水",
        "note": "九運上山下水，損財傷丁。戌山辰向正卦"
    },
    # 巽山乾向 / 巳山亥向（正卦相同）- 九運雙星會向
    "巽山乾向": {
        "mountain": [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "facing":   [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。巽山乾向正卦"
    },
    "巳山亥向": {
        "mountain": [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "facing":   [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。巳山亥向正卦"
    },
    # 乾山巽向 / 亥山巳向（正卦相同）- 九運雙星會向
    "乾山巽向": {
        "mountain": [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "facing":   [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。乾山巽向正卦"
    },
    "亥山巳向": {
        "mountain": [3, 8, 1, 2, 4, 6, 7, 9, 5],
        "facing":   [6, 1, 8, 7, 5, 3, 2, 9, 4],
        "pan_type": "雙星會向",
        "note": "九運雙星會向，旺財不旺丁。亥山巳向正卦"
    },
    # 丙山壬向 / 甲山庚向（正卦）
    "丙山壬向": {
        "mountain": [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "其他",
        "note": "九運丙山壬向正卦"
    },
    "甲山庚向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "其他",
        "note": "九運甲山庚向正卦"
    },
    "壬山丙向": {
        "mountain": [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "facing":   [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "pan_type": "其他",
        "note": "九運壬山丙向正卦"
    },
    "庚山甲向": {
        "mountain": [1, 6, 8, 7, 3, 5, 2, 4, 9],
        "facing":   [9, 4, 2, 3, 8, 6, 5, 7, 1],
        "pan_type": "其他",
        "note": "九運庚山甲向正卦"
    },
}


def validate_data(data_dict, period_name):
    """驗證數據：檢查山盤和向盤是否不同"""
    print(f"\n=== {period_name} 數據驗證 ===")
    all_valid = True
    for mountain, data in data_dict.items():
        m = data["mountain"]
        f = data["facing"]
        if m == f:
            print(f"⚠️  {mountain}: 山盤=向盤（錯誤）")
            all_valid = False
        else:
            diffs = sum(1 for i in range(9) if m[i] != f[i])
            pan_type = data.get("pan_type", "未知")
            print(f"✓  {mountain}: 山盤≠向盤（差異{diffs}格）- {pan_type}")
    return all_valid


def generate_flying_star_dict(data_dict, period_name):
    """生成飛星盤字典格式"""
    result = {}
    for mountain, data in data_dict.items():
        mountain_dict = {}
        facing_dict = {}
        for i, pos in enumerate(GRID_POSITIONS):
            mountain_dict[pos] = data["mountain"][i]
            facing_dict[pos] = data["facing"][i]
        
        result[mountain] = {
            "mountain_stars": mountain_dict,
            "facing_stars": facing_dict,
            "confidence": 0.85,
            "source": "福山堂玄空飛星盤（專業數據）",
            "note": data.get("note", ""),
            "pan_type": data.get("pan_type", "未知")
        }
    return result


if __name__ == "__main__":
    # 驗證數據
    print("開始驗證專業飛星數據...")
    
    yun_8_valid = validate_data(YUN_8_DATA, "八運")
    yun_9_valid = validate_data(YUN_9_DATA, "九運")
    
    if yun_8_valid and yun_9_valid:
        print("\n✅ 所有數據驗證通過！山盤和向盤均不相同。")
    else:
        print("\n⚠️ 部分數據存在問題，需要檢查。")
    
    # 生成飛星盤字典
    print("\n=== 生成飛星盤字典 ===")
    yun_8_dict = generate_flying_star_dict(YUN_8_DATA, "八運")
    yun_9_dict = generate_flying_star_dict(YUN_9_DATA, "九運")
    
    # 保存為 JSON 供後續使用
    with open("yun_8_professional.json", "w", encoding="utf-8") as f:
        json.dump(yun_8_dict, f, ensure_ascii=False, indent=2)
    
    with open("yun_9_professional.json", "w", encoding="utf-8") as f:
        json.dump(yun_9_dict, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 數據已保存到:")
    print("  - yun_8_professional.json")
    print("  - yun_9_professional.json")
    
    # 顯示示例
    print("\n=== 示例：八運 子山午向 ===")
    example = yun_8_dict["子山午向"]
    print(f"山盤: {example['mountain_stars']}")
    print(f"向盤: {example['facing_stars']}")
    print(f"格局: {example['pan_type']}")
    print(f"來源: {example['source']}")
    
    print("\n=== 示例：九運 午山子向 ===")
    example = yun_9_dict["午山子向"]
    print(f"山盤: {example['mountain_stars']}")
    print(f"向盤: {example['facing_stars']}")
    print(f"格局: {example['pan_type']}")
    print(f"來源: {example['source']}")
