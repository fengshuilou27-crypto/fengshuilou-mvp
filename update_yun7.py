# -*- coding: utf-8 -*-
"""
更新七運數據：
1. 從福山堂總局提取確認的子山午向/午山子向
2. 其他山向保持原有但降置信度至0.3
"""
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 從福山堂總局提取的七運下卦數據
# 格式：[山星] [向星]
YUN_7_CONFIRMED = {
    "子山午向": {
        "mountain": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
        "facing": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},
        "pan_type": "雙星會向",
        "note": "七運雙星會向，旺財不旺丁。坐北朝南，福山堂專業數據"
    },
    "午山子向": {
        "mountain": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},
        "facing": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
        "pan_type": "雙星會向",
        "note": "七運雙星會向，旺財不旺丁。坐南朝北，福山堂專業數據"
    },
}

# 讀取當前 flying_star.py
with open('data/flying_star.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到七運子山午向和午山子向的位置並更新
import re

# 更新子山午向
old_zi = '''        "子山午向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.3,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},'''

new_zi = '''        "子山午向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},'''

content = content.replace(old_zi, new_zi)

# 更新午山子向
old_wu = '''        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.3,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},'''

new_wu = '''        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},
            "facing_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},'''

content = content.replace(old_wu, new_wu)

# 將所有七運其他山向的置信度降到0.3（除了已更新的）
# 使用正則表達式替換七運中置信度>=0.5的為0.3
content = re.sub(
    r'("七運".*?"(?!子山午向|午山子向)[^"]+":\s*\{[^}]*?"confidence":\s*)0\.[5-9]',
    r'\g<1>0.3',
    content,
    flags=re.DOTALL
)

with open('data/flying_star.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 七運數據已更新！")
print("  - 子山午向: 已更新為福山堂專業數據（置信度0.85）")
print("  - 午山子向: 已更新為福山堂專業數據（置信度0.85）")
print("  - 其他22山向: 置信度降至0.3（待專業驗證）")
