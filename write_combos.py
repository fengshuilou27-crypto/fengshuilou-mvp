# -*- coding: utf-8 -*-
"""
將自動生成的飛星組合寫回 flying_star.py
"""
import sys, json, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from data.flying_star import FLYING_STAR_TABLE, FLYING_STAR_COMBO_AUSPICIOUS, FLYING_STAR_COMBO_INAUSPICIOUS

YUN_STAR_NUM = {"七運": 7, "八運": 8, "九運": 9}

def generate_combos(mountain_stars, facing_stars, yun_star):
    a, i = [], []
    seen_a, seen_i = set(), set()
    for direction in ["north","northeast","east","southeast","south","southwest","west","northwest","center"]:
        m = mountain_stars.get(direction)
        f = facing_stars.get(direction)
        if m is None or f is None: continue
        for combo in [f"{m}{f}", f"{f}{m}"]:
            if combo in FLYING_STAR_COMBO_AUSPICIOUS and combo not in seen_a:
                seen_a.add(combo)
                a.append({"direction": direction, "stars": combo, "desc": FLYING_STAR_COMBO_AUSPICIOUS[combo]})
            elif combo in FLYING_STAR_COMBO_INAUSPICIOUS and combo not in seen_i:
                seen_i.add(combo)
                i.append({"direction": direction, "stars": combo, "desc": FLYING_STAR_COMBO_INAUSPICIOUS[combo]})
        # 運星組合
        for combo in [f"{yun_star}{m}", f"{yun_star}{f}", f"{m}{yun_star}", f"{f}{yun_star}"]:
            if combo in FLYING_STAR_COMBO_AUSPICIOUS and combo not in seen_a:
                seen_a.add(combo)
                a.append({"direction": direction, "stars": combo, "desc": f"運星組合: {FLYING_STAR_COMBO_AUSPICIOUS[combo]}"})
    return a, i

# 生成所有組合
for yun, mountains in FLYING_STAR_TABLE.items():
    yun_star = YUN_STAR_NUM.get(yun, 8)
    for mountain, data in mountains.items():
        a, i = generate_combos(data.get("mountain_stars", {}), data.get("facing_stars", {}), yun_star)
        data["auspicious_combos"] = a
        data["inauspicious_combos"] = i

# 讀取原文件
with open('data/flying_star.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替換 FLYING_STAR_TABLE 定義
start = content.find('FLYING_STAR_TABLE = {')
if start == -1:
    print("Error: FLYING_STAR_TABLE not found")
    sys.exit(1)

# 找到結束位置（最後一個 "七運" 後面的 }）
end = content.find('\n# 支持的坐向列表', start)
if end == -1:
    end = content.find('\n\n# 支持的坐向列表', start)

prefix = content[:start]
suffix = content[end:]

# 生成新的表格字符串
new_table = "FLYING_STAR_TABLE = {\n"
for yun in ["七運", "八運", "九運"]:
    mountains = FLYING_STAR_TABLE.get(yun, {})
    if not mountains:
        continue
    new_table += f'    "{yun}": {{\n'
    for mountain_name in sorted(mountains.keys()):
        data = mountains[mountain_name]
        new_table += f'        "{mountain_name}": {{\n'
        new_table += f'            "pan_type": "{data["pan_type"]}", "base_score": {data["base_score"]}, "confidence": {data["confidence"]},\n'
        # mountain_stars
        ms = data["mountain_stars"]
        new_table += '            "mountain_stars": {' + ', '.join([f'"{k}": {v}' for k, v in ms.items()]) + '},\n'
        # facing_stars
        fs = data["facing_stars"]
        new_table += '            "facing_stars": {' + ', '.join([f'"{k}": {v}' for k, v in fs.items()]) + '},\n'
        # auspicious_combos
        a = data.get("auspicious_combos", [])
        if a:
            new_table += '            "auspicious_combos": [\n'
            for item in a:
                new_table += f'                {{"direction": "{item["direction"]}", "stars": "{item["stars"]}", "desc": "{item["desc"]}"}},\n'
            new_table += '            ],\n'
        else:
            new_table += '            "auspicious_combos": [],\n'
        # inauspicious_combos
        i = data.get("inauspicious_combos", [])
        if i:
            new_table += '            "inauspicious_combos": [\n'
            for item in i:
                new_table += f'                {{"direction": "{item["direction"]}", "stars": "{item["stars"]}", "desc": "{item["desc"]}"}},\n'
            new_table += '            ],\n'
        else:
            new_table += '            "inauspicious_combos": [],\n'
        # note
        note = data.get("note", "")
        new_table += f'            "note": "{note}"\n'
        new_table += '        },\n'
    new_table += '    },\n'
new_table += '}\n'

# 更新 header
new_prefix = prefix.replace(
    '# 硬編碼查表數據 - 飛星宅運盤 (v3.4 專業數據版)',
    '# 硬編碼查表數據 - 飛星宅運盤 (v3.5 專業數據+自動組合版)'
).replace(
    '#   - 七運數據待後續更新，格局判定基於飛星組合',
    '#   - 自動生成飛星組合（auspicious/inauspicious）'
)

new_content = new_prefix + new_table + suffix

with open('data/flying_star.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ flying_star.py 已更新，包含自動生成的飛星組合！")
