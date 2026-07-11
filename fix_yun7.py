# -*- coding: utf-8 -*-
import sys, re

# Read file
with open('data/flying_star.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update 七運子山午向
old_zi = '''        "子山午向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.3,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},'''

new_zi = '''        "子山午向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},'''

content = content.replace(old_zi, new_zi)

# Update 七運午山子向
old_wu = '''        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.3,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},'''

new_wu = '''        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},
            "facing_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},'''

content = content.replace(old_wu, new_wu)

# Update notes
content = content.replace(
    '"note": "七運到山到向，丁財兩得"',
    '"note": "七運雙星會向，旺財不旺丁。坐北朝南，福山堂專業數據"'
)
content = content.replace(
    '"note": "七運雙星會向，旺財不旺丁。與子山午向相對"',
    '"note": "七運雙星會向，旺財不旺丁。坐南朝北，福山堂專業數據"'
)

with open('data/flying_star.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
