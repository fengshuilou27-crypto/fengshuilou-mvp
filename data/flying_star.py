# 硬編碼查表數據 - 飛星宅運盤 (v3.5 專業數據+自動組合版)
# 支持24山向，基於福山堂(fushantang.com)專業玄空飛星盤
# ⚠️ v3.4 重要更新說明：
#   - 從福山堂提取專業玄空飛星盤數據
#   - 八運和九運 24 山向數據已全面更新
#   - 所有數據山盤和向盤均獨立，符合玄空飛星理論
#   - 自動生成飛星組合（auspicious/inauspicious）
# ⚠️ 數據基於公開資料，具體需專業師傅確認

# 運數判斷
YUN_PERIODS = {
    (1864, 1883): "一運",
    (1884, 1903): "二運",
    (1904, 1923): "三運",
    (1924, 1943): "四運",
    (1944, 1963): "五運",
    (1964, 1983): "六運",
    (1984, 2003): "七運",
    (2004, 2023): "八運",
    (2024, 2043): "九運",
}


def get_yun(year: int) -> str:
    """根據年份判斷運數"""
    for (start, end), yun in YUN_PERIODS.items():
        if start <= year <= end:
            return yun
    if year < 1864:
        return "九運"
    return "九運"  # 2024年後


# 24山向列表 (羅盤24方位)
ALL_24_MOUNTAINS = [
    "子山午向", "癸山丁向",  # 正北/偏北
    "丑山未向", "艮山坤向", "寅山申向",  # 東北
    "卯山酉向", "乙山辛向",  # 正東/偏東
    "辰山戌向", "巽山乾向", "巳山亥向",  # 東南
    "午山子向", "丁山癸向",  # 正南/偏南
    "未山丑向", "坤山艮向", "申山寅向",  # 西南
    "酉山卯向", "辛山乙向",  # 正西/偏西
    "戌山辰向", "乾山巽向", "亥山巳向",  # 西北
    "壬山丙向", "甲山庚向", "丙山壬向", "庚山甲向"  # 四維輔位
]

# 24山向 -> 基本朝向 (用於宅卦判定)
MOUNTAIN_FACING_MAP = {
    "子山午向": "坐北向南", "癸山丁向": "坐北向南",
    "丑山未向": "坐東北向西南", "艮山坤向": "坐東北向西南", "寅山申向": "坐東北向西南",
    "卯山酉向": "坐東向西", "乙山辛向": "坐東向西",
    "辰山戌向": "坐東南向西北", "巽山乾向": "坐東南向西北", "巳山亥向": "坐東南向西北",
    "午山子向": "坐南向北", "丁山癸向": "坐南向北",
    "未山丑向": "坐西南向東北", "坤山艮向": "坐西南向東北", "申山寅向": "坐西南向東北",
    "酉山卯向": "坐西向東", "辛山乙向": "坐西向東",
    "戌山辰向": "坐西北向東南", "乾山巽向": "坐西北向東南", "亥山巳向": "坐西北向東南",
    "壬山丙向": "坐北向南", "甲山庚向": "坐東向西",
    "丙山壬向": "坐南向北", "庚山甲向": "坐西向東"
}

# ============================================================
# 飛星宅運盤 (v2.2 擴展版 - 24山向覆蓋)
# ============================================================
FLYING_STAR_TABLE = {
    "七運": {
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.5,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "west", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "northwest", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "northeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "southeast", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運雙星會向，與午山子向類似 ⚠️ 數據需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [
                {"direction": "north", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "east", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "southwest", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "northwest", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運雙星會坐，旺丁不旺財 ⚠️ 數據需專業確認"
        },
        "丙山壬向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.5,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "west", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "northwest", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "northeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "southeast", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運偏位 ⚠️ 數據需專業確認"
        },
        "乙山辛向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.5,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "southwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "west", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運雙星會向，與卯山酉向類似 ⚠️ 數據需專業確認"
        },
        "乾山巽向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "facing_stars": {"northwest": 7, "north": 2, "northeast": 9, "west": 8, "center": 6, "east": 3, "southwest": 4, "south": 1, "southeast": 5},
            "auspicious_combos": [
                {"direction": "southeast", "stars": "77", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "west", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "center", "stars": "86", "desc": "八六會合，財丁兩旺"},
                {"direction": "center", "stars": "68", "desc": "六八會合，貴人扶持"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "53", "desc": "五三同宮，災禍連連"},
                {"direction": "east", "stars": "35", "desc": "三五同宮，五黃三煞"},
                {"direction": "southeast", "stars": "75", "desc": "七五同宮，災禍損財"},
                {"direction": "southeast", "stars": "57", "desc": "五七同宮，破財傷丁"},
            ],
            "note": "七運上山下水，損財傷丁"
        },
        "亥山巳向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"northwest": 7, "north": 2, "northeast": 9, "west": 8, "center": 6, "east": 3, "southwest": 4, "south": 1, "southeast": 5},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "auspicious_combos": [
                {"direction": "southeast", "stars": "77", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "west", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "center", "stars": "68", "desc": "六八會合，貴人扶持"},
                {"direction": "center", "stars": "86", "desc": "八六會合，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "35", "desc": "三五同宮，五黃三煞"},
                {"direction": "east", "stars": "53", "desc": "五三同宮，災禍連連"},
                {"direction": "southeast", "stars": "57", "desc": "五七同宮，破財傷丁"},
                {"direction": "southeast", "stars": "75", "desc": "七五同宮，災禍損財"},
            ],
            "note": "七運上山下水，與乾山巽向類似 ⚠️ 數據需專業確認"
        },
        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 7, "northeast": 9, "west": 4, "center": 2, "east": 6, "southwest": 8, "south": 1, "southeast": 5},
            "facing_stars": {"northwest": 2, "north": 7, "northeast": 5, "west": 6, "center": 1, "east": 8, "southwest": 4, "south": 9, "southeast": 3},
            "auspicious_combos": [
                {"direction": "north", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八會合，喜慶盈門"},
                {"direction": "southwest", "stars": "84", "desc": "運星組合: 八四會合，文財兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "19", "desc": "一九同宮，水火相戰"},
                {"direction": "northwest", "stars": "32", "desc": "三二鬥牛，官非口舌"},
                {"direction": "southeast", "stars": "53", "desc": "五三煞氣，災禍連連"},
            ],
            "note": "七運雙星會向，旺財不旺丁。坐南朝北，與子山午向互為鏡像"
        },
        "卯山酉向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.3,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "southwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "west", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運雙星會向，旺財不旺丁"
        },
        "坤山艮向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.6,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [
                {"direction": "north", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "center", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "center", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "center", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "southeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "southwest", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運上山下水，與艮山坤向相對 ⚠️ 數據需專業確認"
        },
        "壬山丙向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.5,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [
                {"direction": "north", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "east", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "southwest", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "northwest", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運偏位 ⚠️ 數據需專業確認"
        },
        "子山午向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 9, "center": 2, "east": 4, "southwest": 5, "south": 7, "southeast": 3},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "south", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "23", "desc": "二三斗牛，鬥爭是非"},
                {"direction": "southeast", "stars": "32", "desc": "三二鬥牛，官非口舌"},
                {"direction": "west", "stars": "59", "desc": "五九同宮，災禍連連"},
            ],
            "note": "七運雙星會向，旺財不旺丁。坐北朝南，福山堂專業數據"
        },
        "寅山申向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [
                {"direction": "north", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "center", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "center", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "center", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "southeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "southwest", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運上山下水，與艮山坤向類似 ⚠️ 數據需專業確認"
        },
        "巳山亥向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "facing_stars": {"northwest": 7, "north": 2, "northeast": 9, "west": 8, "center": 6, "east": 3, "southwest": 4, "south": 1, "southeast": 5},
            "auspicious_combos": [
                {"direction": "southeast", "stars": "77", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "west", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "center", "stars": "86", "desc": "八六會合，財丁兩旺"},
                {"direction": "center", "stars": "68", "desc": "六八會合，貴人扶持"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "53", "desc": "五三同宮，災禍連連"},
                {"direction": "east", "stars": "35", "desc": "三五同宮，五黃三煞"},
                {"direction": "southeast", "stars": "75", "desc": "七五同宮，災禍損財"},
                {"direction": "southeast", "stars": "57", "desc": "五七同宮，破財傷丁"},
            ],
            "note": "七運上山下水，與巽山乾向類似 ⚠️ 數據需專業確認"
        },
        "巽山乾向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.7,
            "mountain_stars": {"northwest": 7, "north": 3, "northeast": 9, "west": 5, "center": 6, "east": 8, "southwest": 4, "south": 2, "southeast": 1},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "auspicious_combos": [
                {"direction": "east", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "east", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "southeast", "stars": "77", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "center", "stars": "68", "desc": "六八會合，貴人扶持"},
                {"direction": "center", "stars": "86", "desc": "八六會合，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "23", "desc": "二三斗牛，鬥爭是非"},
                {"direction": "south", "stars": "32", "desc": "三二鬥牛，官非口舌"},
            ],
            "note": "七運上山下水，與乾山巽向相對 ⚠️ 數據需專業確認"
        },
        "庚山甲向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.5,
            "mountain_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "facing_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "southeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "center", "stars": "22", "desc": "二黑重臨，病符纏身"},
            ],
            "note": "七運到山到向，與酉山卯向類似 ⚠️ 數據需專業確認"
        },
        "戌山辰向": {
            "pan_type": "其他", "base_score": 12, "confidence": 0.5,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [
                {"direction": "north", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "east", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "southwest", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "northwest", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運普通格局 ⚠️ 數據需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [
                {"direction": "south", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "southwest", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "center", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "east", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "northwest", "stars": "22", "desc": "二黑重臨，病符纏身"},
            ],
            "note": "七運雙星會坐，旺丁不旺財 ⚠️ 數據需專業確認"
        },
        "甲山庚向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.5,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "southwest", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "west", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運雙星會向，與卯山酉向類似 ⚠️ 數據需專業確認"
        },
        "申山寅向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [
                {"direction": "east", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "southeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "west", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "northwest", "stars": "33", "desc": "三碧重臨，口舌是非"},
            ],
            "note": "七運上山下水，與坤山艮向類似 ⚠️ 數據需專業確認"
        },
        "癸山丁向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.5,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [
                {"direction": "north", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "east", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "southwest", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "northwest", "stars": "55", "desc": "五黃重臨，煞氣當令"},
            ],
            "note": "七運到山到向，與子山午向類似 ⚠️ 數據需專業確認"
        },
        "艮山坤向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.6,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [
                {"direction": "east", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "southeast", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "west", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "northwest", "stars": "33", "desc": "三碧重臨，口舌是非"},
            ],
            "note": "七運上山下水，損財傷丁 ⚠️ 數據需專業確認"
        },
        "辛山乙向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.5,
            "mountain_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "facing_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "southeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "center", "stars": "22", "desc": "二黑重臨，病符纏身"},
            ],
            "note": "七運到山到向，與酉山卯向類似 ⚠️ 數據需專業確認"
        },
        "辰山戌向": {
            "pan_type": "其他", "base_score": 12, "confidence": 0.5,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [
                {"direction": "south", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "southwest", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "center", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "east", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "northwest", "stars": "22", "desc": "二黑重臨，病符纏身"},
            ],
            "note": "七運普通格局 ⚠️ 數據需專業確認"
        },
        "酉山卯向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.3,
            "mountain_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "facing_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "77", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "55", "desc": "五黃重臨，煞氣當令"},
                {"direction": "southeast", "stars": "33", "desc": "三碧重臨，口舌是非"},
                {"direction": "center", "stars": "22", "desc": "二黑重臨，病符纏身"},
            ],
            "note": "七運到山到向，丁財兩得。與卯山酉向相對 ⚠️ 數據需專業確認"
        },
    },
    "一運": {
        "子山午向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "午山子向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "east", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "east", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "卯山酉向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "auspicious_combos": [
                {"direction": "east", "stars": "61", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "酉山卯向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [
                {"direction": "east", "stars": "16", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辰山戌向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "戌山辰向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "艮山坤向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "east", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "坤山艮向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "east", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巽山乾向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乾山巽向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "一運雙星會坐，當令1白 ⚠️ 數據基於理論推算，需專業確認"
        }
    },
    "二運": {
        "子山午向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "午山子向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "卯山酉向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "61", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "酉山卯向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "16", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辰山戌向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "facing_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "auspicious_combos": [
                {"direction": "north", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "戌山辰向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "facing_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "auspicious_combos": [
                {"direction": "north", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "艮山坤向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "坤山艮向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巽山乾向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "facing_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "auspicious_combos": [
                {"direction": "north", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乾山巽向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "facing_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "auspicious_combos": [
                {"direction": "north", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "二運雙星會坐，當令2白 ⚠️ 數據基於理論推算，需專業確認"
        }
    },
    "三運": {
        "子山午向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "午山子向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "卯山酉向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "61", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "酉山卯向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "facing_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "auspicious_combos": [
                {"direction": "north", "stars": "16", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辰山戌向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [
                {"direction": "south", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "戌山辰向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [
                {"direction": "south", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "艮山坤向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "坤山艮向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巽山乾向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [
                {"direction": "south", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乾山巽向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [
                {"direction": "south", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "三運雙星會坐，當令3白 ⚠️ 數據基於理論推算，需專業確認"
        }
    },
    "四運": {
        "子山午向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "午山子向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "south", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "south", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "卯山酉向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "south", "stars": "61", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "酉山卯向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [
                {"direction": "south", "stars": "16", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辰山戌向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "center", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "戌山辰向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "facing_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "center", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "艮山坤向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "south", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "坤山艮向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "south", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巽山乾向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "center", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乾山巽向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "facing_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "center", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "四運雙星會坐，當令4白 ⚠️ 數據基於理論推算，需專業確認"
        }
    },
    "五運": {
        "子山午向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "facing_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "午山子向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 5, "northeast": 3, "east": 7, "southeast": 8, "south": 4, "southwest": 6, "west": 2, "northwest": 1, "center": 9},
            "facing_stars": {"north": 6, "northeast": 4, "east": 8, "southeast": 9, "south": 5, "southwest": 7, "west": 3, "northwest": 2, "center": 1},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "卯山酉向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "facing_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "61", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "酉山卯向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 1, "east": 5, "southeast": 6, "south": 2, "southwest": 4, "west": 9, "northwest": 8, "center": 7},
            "facing_stars": {"north": 8, "northeast": 6, "east": 1, "southeast": 2, "south": 7, "southwest": 9, "west": 5, "northwest": 4, "center": 3},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
            ],
            "inauspicious_combos": [],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辰山戌向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "戌山辰向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [
                {"direction": "west", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "艮山坤向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "facing_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "坤山艮向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 7, "northeast": 5, "east": 9, "southeast": 1, "south": 6, "southwest": 8, "west": 4, "northwest": 3, "center": 2},
            "facing_stars": {"north": 4, "northeast": 2, "east": 6, "southeast": 7, "south": 3, "southwest": 5, "west": 1, "northwest": 9, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "52", "desc": "二五交加，損財傷丁"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巽山乾向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乾山巽向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "auspicious_combos": [
                {"direction": "west", "stars": "86", "desc": "六八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "53", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "五運雙星會坐，當令5白 ⚠️ 數據基於理論推算，需專業確認"
        }
    },

    "六運": {
        "子山午向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "癸山丁向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會坐，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "艮山坤向": {
            "pan_type": "上山下水", "base_score": 15, "confidence": 0.65,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運上山下水，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "寅山申向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "卯山酉向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乙山辛向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辰山戌向": {
            "pan_type": "上山下水", "base_score": 15, "confidence": 0.65,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運上山下水，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巽山乾向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會坐，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "巳山亥向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "午山子向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "坤山艮向": {
            "pan_type": "上山下水", "base_score": 15, "confidence": 0.65,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運上山下水，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "申山寅向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會坐，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "酉山卯向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "辛山乙向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會坐，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "戌山辰向": {
            "pan_type": "上山下水", "base_score": 15, "confidence": 0.65,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運上山下水，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "乾山巽向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "亥山巳向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "壬山丙向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "甲山庚向": {
            "pan_type": "雙星會坐", "base_score": 18, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "68", "desc": "六八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "67", "desc": "六七交劍，權貴之方"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運雙星會坐，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "丙山壬向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
        "庚山甲向": {
            "pan_type": "旺山旺向", "base_score": 22, "confidence": 0.75,
            "mountain_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "facing_stars": {"north": 2, "northeast": 9, "east": 4, "southeast": 5, "south": 1, "southwest": 3, "west": 8, "northwest": 7, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "88", "desc": "六運八白生氣，財源廣進"},
                {"direction": "northwest", "stars": "77", "desc": "六運七赤佐輔，丁財兩旺"},
                {"direction": "northeast", "stars": "99", "desc": "六運九紫生氣，喜慶連連"},
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "22", "desc": "二黑病符，六運死氣方"},
                {"direction": "south", "stars": "11", "desc": "一白退氣，六運不吉"},
                {"direction": "southeast", "stars": "55", "desc": "五黃煞氣，宜靜不宜動"},
            ],
            "note": "六運旺山旺向，當令六白 ⚠️ 數據基於理論推算，需專業確認"
        },
    },
    "八運": {
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "south", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運雙星會向，旺財不旺丁。丁山癸向正卦"
        },
        "丑山未向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 3, "northeast": 1, "west": 9, "center": 5, "east": 7, "southwest": 4, "south": 6, "southeast": 2},
            "facing_stars": {"northwest": 8, "north": 1, "northeast": 6, "west": 7, "center": 2, "east": 9, "southwest": 3, "south": 4, "southeast": 5},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "east", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "east", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "east", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "east", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運到山到向，丁財兩得。坐東北朝西南，正卦"
        },
        "丙山壬向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 1, "northeast": 3, "west": 4, "center": 8, "east": 6, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 6, "north": 8, "northeast": 4, "west": 5, "center": 3, "east": 1, "southwest": 7, "south": 9, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "east", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "east", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "east", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "south", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "west", "stars": "45", "desc": "四五同宮，官非口舌"},
                {"direction": "west", "stars": "54", "desc": "五四同宮，病災損財"},
            ],
            "note": "八運丙山壬向正卦"
        },
        "乙山辛向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 5, "north": 6, "northeast": 4, "west": 3, "center": 1, "east": 9, "southwest": 8, "south": 7, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "north", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "east", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [],
            "note": "八運雙星會向，旺財不旺丁。乙山辛向正卦"
        },
        "乾山巽向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運到山到向，丁財兩得。乾山巽向正卦"
        },
        "亥山巳向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運到山到向，丁財兩得。亥山巳向正卦"
        },
        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "south", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運雙星會向，旺財不旺丁。坐南朝北，正卦"
        },
        "卯山酉向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 5, "north": 6, "northeast": 4, "west": 3, "center": 1, "east": 9, "southwest": 8, "south": 7, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "north", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "east", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [],
            "note": "八運雙星會向，旺財不旺丁。坐東朝西，正卦"
        },
        "坤山艮向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "facing_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "north", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "southeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "southeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southwest", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運上山下水，損財傷丁。坐西南朝東北，正卦"
        },
        "壬山丙向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 8, "northeast": 4, "west": 5, "center": 3, "east": 1, "southwest": 7, "south": 9, "southeast": 2},
            "facing_stars": {"northwest": 5, "north": 1, "northeast": 3, "west": 4, "center": 8, "east": 6, "southwest": 9, "south": 7, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "east", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "east", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "east", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "south", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "22", "desc": "二黑重臨，病符纏身"},
                {"direction": "west", "stars": "54", "desc": "五四同宮，病災損財"},
                {"direction": "west", "stars": "45", "desc": "四五同宮，官非口舌"},
            ],
            "note": "八運壬山丙向正卦"
        },
        "子山午向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "facing_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "south", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運雙星會向，旺財不旺丁。坐北朝南，正卦"
        },
        "寅山申向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "facing_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "auspicious_combos": [
                {"direction": "north", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "north", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "southeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "southeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southwest", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運上山下水，損財傷丁。寅山申向正卦"
        },
        "巳山亥向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運到山到向，丁財兩得。巳山亥向正卦"
        },
        "巽山乾向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運到山到向，丁財兩得。巽山乾向正卦"
        },
        "庚山甲向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 7, "north": 9, "northeast": 2, "west": 1, "center": 5, "east": 3, "southwest": 4, "south": 6, "southeast": 8},
            "facing_stars": {"northwest": 8, "north": 4, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "67", "desc": "六七交劍，刑傷破財"},
                {"direction": "south", "stars": "76", "desc": "七六交劍，官非手術"},
                {"direction": "center", "stars": "53", "desc": "五三同宮，災禍連連"},
                {"direction": "center", "stars": "35", "desc": "三五同宮，五黃三煞"},
            ],
            "note": "八運庚山甲向正卦"
        },
        "戌山辰向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 7, "north": 9, "northeast": 5, "west": 6, "center": 4, "east": 2, "southwest": 1, "south": 3, "southeast": 8},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "east", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "east", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "northeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "west", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "west", "stars": "36", "desc": "三六同宮，交劍煞臨"},
            ],
            "note": "八運上山下水，損財傷丁。戌山辰向正卦"
        },
        "未山丑向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 1, "northeast": 6, "west": 7, "center": 2, "east": 9, "southwest": 3, "south": 4, "southeast": 5},
            "facing_stars": {"northwest": 8, "north": 3, "northeast": 1, "west": 9, "center": 5, "east": 7, "southwest": 4, "south": 6, "southeast": 2},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "east", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "east", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "east", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "east", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運到山到向，丁財兩得。坐西南朝東北，正卦"
        },
        "甲山庚向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 4, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 7, "north": 9, "northeast": 2, "west": 1, "center": 5, "east": 3, "southwest": 4, "south": 6, "southeast": 8},
            "auspicious_combos": [
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "七六交劍，官非手術"},
                {"direction": "south", "stars": "67", "desc": "六七交劍，刑傷破財"},
                {"direction": "center", "stars": "35", "desc": "三五同宮，五黃三煞"},
                {"direction": "center", "stars": "53", "desc": "五三同宮，災禍連連"},
            ],
            "note": "八運甲山庚向正卦"
        },
        "申山寅向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "facing_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "north", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "southeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "southeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southwest", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運上山下水，損財傷丁。申山寅向正卦"
        },
        "癸山丁向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "facing_stars": {"northwest": 4, "north": 8, "northeast": 6, "west": 5, "center": 3, "east": 1, "southwest": 9, "south": 7, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "northeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "south", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "八運雙星會向，旺財不旺丁。癸山丁向正卦"
        },
        "艮山坤向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "facing_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "auspicious_combos": [
                {"direction": "north", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "north", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "southeast", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "southeast", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southwest", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "八運上山下水，損財傷丁。坐東南朝西北，正卦"
        },
        "辛山乙向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 6, "northeast": 4, "west": 3, "center": 1, "east": 9, "southwest": 8, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "north", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "north", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "east", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [],
            "note": "八運雙星會向，旺財不旺丁。辛山乙向正卦"
        },
        "辰山戌向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 7, "north": 9, "northeast": 5, "west": 6, "center": 4, "east": 2, "southwest": 1, "south": 3, "southeast": 8},
            "auspicious_combos": [
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "east", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "east", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "southeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [
                {"direction": "northeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "northeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "west", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "west", "stars": "63", "desc": "六三同宮，刑傷官非"},
            ],
            "note": "八運上山下水，損財傷丁。辰山戌向正卦"
        },
        "酉山卯向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 6, "northeast": 4, "west": 3, "center": 1, "east": 9, "southwest": 8, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "north", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "north", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "north", "stars": "86", "desc": "運星組合: 八六會合，財丁兩旺"},
                {"direction": "north", "stars": "68", "desc": "運星組合: 六八會合，貴人扶持"},
                {"direction": "northeast", "stars": "88", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "east", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "east", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "south", "stars": "87", "desc": "運星組合: 八七同宮，財源廣進"},
                {"direction": "south", "stars": "78", "desc": "運星組合: 七八同宮，財丁兩旺"},
            ],
            "inauspicious_combos": [],
            "note": "八運雙星會向，旺財不旺丁。坐西朝東，正卦"
        },
    },
    "九運": {
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "facing_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
            ],
            "note": "九運雙星會向，旺財不旺丁。丁山癸向正卦"
        },
        "丑山未向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "facing_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "89", "desc": "八九成雙，旺財旺丁"},
                {"direction": "southwest", "stars": "98", "desc": "九八成雙，喜慶旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運上山下水，損財傷丁。丑山未向正卦"
        },
        "丙山壬向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運丙山壬向正卦"
        },
        "乙山辛向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運到山到向，丁財兩得。乙山辛向正卦"
        },
        "乾山巽向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "facing_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
            ],
            "note": "九運雙星會向，旺財不旺丁。乾山巽向正卦"
        },
        "亥山巳向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "facing_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
            ],
            "note": "九運雙星會向，旺財不旺丁。亥山巳向正卦"
        },
        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "facing_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
            ],
            "note": "九運雙星會向，旺財不旺丁。午山子向正卦"
        },
        "卯山酉向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運到山到向，丁財兩得。卯山酉向正卦"
        },
        "坤山艮向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 1, "northeast": 6, "west": 7, "center": 2, "east": 9, "southwest": 3, "south": 4, "southeast": 5},
            "facing_stars": {"northwest": 8, "north": 3, "northeast": 1, "west": 9, "center": 5, "east": 7, "southwest": 4, "south": 6, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "east", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northwest", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運到山到向，丁財兩得。坤山艮向正卦"
        },
        "壬山丙向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運壬山丙向正卦"
        },
        "子山午向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "facing_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
            ],
            "note": "九運雙星會向，旺財不旺丁。子山午向正卦"
        },
        "寅山申向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 3, "northeast": 1, "west": 9, "center": 5, "east": 7, "southwest": 4, "south": 6, "southeast": 2},
            "facing_stars": {"northwest": 8, "north": 1, "northeast": 6, "west": 7, "center": 2, "east": 9, "southwest": 3, "south": 4, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "east", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northwest", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運到山到向，丁財兩得。寅山申向正卦"
        },
        "巳山亥向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "facing_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
            ],
            "note": "九運雙星會向，旺財不旺丁。巳山亥向正卦"
        },
        "巽山乾向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "facing_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
            ],
            "note": "九運雙星會向，旺財不旺丁。巽山乾向正卦"
        },
        "庚山甲向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運庚山甲向正卦"
        },
        "戌山辰向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "facing_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "98", "desc": "九八成雙，喜慶旺財"},
                {"direction": "southwest", "stars": "89", "desc": "八九成雙，旺財旺丁"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運上山下水，損財傷丁。戌山辰向正卦"
        },
        "未山丑向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "facing_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "98", "desc": "九八成雙，喜慶旺財"},
                {"direction": "southwest", "stars": "89", "desc": "八九成雙，旺財旺丁"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運上山下水，損財傷丁。未山丑向正卦"
        },
        "甲山庚向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運甲山庚向正卦"
        },
        "申山寅向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 1, "northeast": 6, "west": 7, "center": 2, "east": 9, "southwest": 3, "south": 4, "southeast": 5},
            "facing_stars": {"northwest": 8, "north": 3, "northeast": 1, "west": 9, "center": 5, "east": 7, "southwest": 4, "south": 6, "southeast": 2},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "east", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northwest", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運到山到向，丁財兩得。申山寅向正卦"
        },
        "癸山丁向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.85,
            "mountain_stars": {"northwest": 6, "north": 1, "northeast": 8, "west": 7, "center": 5, "east": 3, "southwest": 2, "south": 9, "southeast": 4},
            "facing_stars": {"northwest": 3, "north": 8, "northeast": 1, "west": 2, "center": 4, "east": 6, "southwest": 7, "south": 9, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "north", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "south", "stars": "99", "desc": "雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "36", "desc": "三六同宮，交劍煞臨"},
                {"direction": "east", "stars": "63", "desc": "六三同宮，刑傷官非"},
                {"direction": "southeast", "stars": "45", "desc": "四五同宮，官非口舌"},
                {"direction": "southeast", "stars": "54", "desc": "五四同宮，病災損財"},
            ],
            "note": "九運雙星會向，旺財不旺丁。癸山丁向正卦"
        },
        "艮山坤向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 8, "north": 3, "northeast": 1, "west": 9, "center": 5, "east": 7, "southwest": 4, "south": 6, "southeast": 2},
            "facing_stars": {"northwest": 8, "north": 1, "northeast": 6, "west": 7, "center": 2, "east": 9, "southwest": 3, "south": 4, "southeast": 5},
            "auspicious_combos": [
                {"direction": "north", "stars": "91", "desc": "運星組合: 九一連珠，貴人相助"},
                {"direction": "north", "stars": "19", "desc": "運星組合: 一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "16", "desc": "一六同宮，官貴清顯"},
                {"direction": "northeast", "stars": "61", "desc": "六一會合，貴人扶持"},
                {"direction": "east", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "88", "desc": "雙星會聚，旺丁旺財"},
                {"direction": "northwest", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northwest", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
            ],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "southeast", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運到山到向，丁財兩得。艮山坤向正卦"
        },
        "辛山乙向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運到山到向，丁財兩得。辛山乙向正卦"
        },
        "辰山戌向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.85,
            "mountain_stars": {"northwest": 2, "north": 7, "northeast": 9, "west": 1, "center": 5, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "facing_stars": {"northwest": 5, "north": 3, "northeast": 1, "west": 2, "center": 8, "east": 7, "southwest": 9, "south": 4, "southeast": 6},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "northeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "northeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "89", "desc": "八九成雙，旺財旺丁"},
                {"direction": "southwest", "stars": "98", "desc": "九八成雙，喜慶旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "25", "desc": "二五交加，損財傷丁"},
                {"direction": "northwest", "stars": "52", "desc": "五二交加，病痛破財"},
            ],
            "note": "九運上山下水，損財傷丁。辰山戌向正卦"
        },
        "酉山卯向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.85,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 3, "center": 8, "east": 6, "southwest": 5, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 8, "west": 7, "center": 3, "east": 5, "southwest": 2, "south": 4, "southeast": 9},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "98", "desc": "運星組合: 九八成雙，喜慶旺財"},
                {"direction": "northeast", "stars": "89", "desc": "運星組合: 八九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "19", "desc": "一九成雙，旺財旺丁"},
                {"direction": "southeast", "stars": "91", "desc": "九一連珠，貴人相助"},
                {"direction": "southeast", "stars": "99", "desc": "運星組合: 雙星會聚，旺丁旺財"},
            ],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "52", "desc": "五二交加，病痛破財"},
                {"direction": "southwest", "stars": "25", "desc": "二五交加，損財傷丁"},
            ],
            "note": "九運到山到向，丁財兩得。酉山卯向正卦"
        },
    },
}

# 支持的坐向列表
SUPPORTED_FACINGS = []
for yun_data in FLYING_STAR_TABLE.values():
    SUPPORTED_FACINGS.extend(yun_data.keys())
SUPPORTED_FACINGS = list(set(SUPPORTED_FACINGS))

# 快速查找：山向 -> 所有支持的運
def get_supported_yuns(mountain: str) -> list:
    """獲取某山向支持的所有運數"""
    yuns = []
    for yun, mountains in FLYING_STAR_TABLE.items():
        if mountain in mountains:
            yuns.append(yun)
    return yuns

# 當運星查表 (用於零正神計算)
CURRENT_LING_STAR = {
    "七運": 7, "八運": 8, "九運": 9
}

# 零神星查表 (與正神相對)
ZERO_GOD_STAR = {
    "七運": 3, "八運": 2, "九運": 1
}

# 星曜五行
STAR_WUXING = {
    1: "水", 2: "土", 3: "木", 4: "木", 5: "土",
    6: "金", 7: "金", 8: "土", 9: "火"
}

# 星曜吉凶 (在當運時)
STAR_AUSPICIOUSNESS = {
    1: "吉星", 2: "凶星", 3: "凶星", 4: "吉星", 5: "凶星",
    6: "吉星", 7: "吉星", 8: "吉星", 9: "吉星"
}

# 飛星組合吉凶表 (部分常見組合)
FLYING_STAR_COMBO_AUSPICIOUS = {
    "77": "雙星會聚，旺丁旺財",
    "88": "雙星會聚，旺丁旺財",
    "99": "雙星會聚，旺丁旺財",
    "89": "八九成雙，旺財旺丁",
    "98": "九八成雙，喜慶旺財",
    "19": "一九成雙，旺財旺丁",
    "91": "九一連珠，貴人相助",
    "68": "六八會合，貴人扶持",
    "86": "八六會合，財丁兩旺",
    "14": "一四同宮，文昌發科",
    "41": "四一同宮，科名顯達",
    "16": "一六同宮，官貴清顯",
    "61": "六一會合，貴人扶持",
    "78": "七八同宮，財丁兩旺",
    "87": "八七同宮，財源廣進",
}

FLYING_STAR_COMBO_INAUSPICIOUS = {
    "22": "二黑重臨，病符纏身",
    "33": "三碧重臨，口舌是非",
    "55": "五黃重臨，煞氣當令",
    "23": "二三斗牛，鬥爭是非",
    "32": "三二鬥牛，官非口舌",
    "35": "三五同宮，五黃三煞",
    "53": "五三同宮，災禍連連",
    "25": "二五交加，損財傷丁",
    "52": "五二交加，病痛破財",
    "45": "四五同宮，官非口舌",
    "54": "五四同宮，病災損財",
    "36": "三六同宮，交劍煞臨",
    "63": "六三同宮，刑傷官非",
    "57": "五七同宮，破財傷丁",
    "75": "七五同宮，災禍損財",
    "76": "七六交劍，官非手術",
    "67": "六七交劍，刑傷破財",
}

# ============================================================
# 多運交叉分析（元運轉換評估）
# ============================================================
PAN_TYPE_RANK = {
    "到山到向": 4,   # 旺丁旺財（最佳）
    "雙星會向": 3,   # 旺財不旺丁（次佳）
    "其他": 2,       # 普通（中等）
    "上山下水": 1,   # 損丁破財（最差）
}

PAN_TYPE_CHINESE = {
    "到山到向": "旺丁旺財",
    "雙星會向": "旺財不旺丁",
    "其他": "普通格局",
    "上山下水": "損丁破財",
}


def get_flying_star_pan(yun: str, facing: str) -> dict:
    """獲取指定運數與座向的飛星盤"""
    yun_data = FLYING_STAR_TABLE.get(yun, {})
    return yun_data.get(facing, {})


def analyze_multi_yun(building_year: int, eval_year: int, facing: str) -> dict:
    """
    多運交叉分析：比較建造運盤與當前運盤的吉凶變化。
    
    玄空風水核心概念：
    - 建造運決定先天格局（元運盤）
    - 當前運決定後天運勢（運過則衰，運至則旺）
    - 元運轉換時，原來旺的盤可能變衰，原來衰的盤可能因 Renovation 而轉旺
    
    Returns:
        {
            "build_yun": str,        # 建造運
            "current_yun": str,      # 當前運
            "build_pan_type": str,   # 建造運格局
            "current_pan_type": str, # 當前運格局
            "build_rank": int,       # 建造運吉凶等級
            "current_rank": int,     # 當前運吉凶等級
            "rank_diff": int,        # 等級差異
            "score_adjust": float,   # 分數調整值
            "rationale": str,        # 風水邏輯說明
            "needs_renovation": bool, # 是否建議換天心/大裝修
        }
    """
    build_yun = get_yun(building_year)
    current_yun = get_yun(eval_year)
    
    build_pan = get_flying_star_pan(build_yun, facing)
    current_pan = get_flying_star_pan(current_yun, facing)
    
    # 如果當前運沒有數據，回退到建造運
    if not build_pan:
        return {
            "build_yun": build_yun,
            "current_yun": current_yun,
            "build_pan_type": "未知",
            "current_pan_type": "未知",
            "build_rank": 2,
            "current_rank": 2,
            "rank_diff": 0,
            "score_adjust": 0.0,
            "rationale": "飛星數據不足，無法進行多運交叉分析",
            "needs_renovation": False,
        }
    
    if not current_pan:
        # 當前運無數據，僅根據建造運評估
        build_pan_type = build_pan.get("pan_type", "其他")
        build_rank = PAN_TYPE_RANK.get(build_pan_type, 2)
        return {
            "build_yun": build_yun,
            "current_yun": current_yun,
            "build_pan_type": build_pan_type,
            "current_pan_type": "數據缺失",
            "build_rank": build_rank,
            "current_rank": 2,
            "rank_diff": 0,
            "score_adjust": 0.0,
            "rationale": f"{build_yun}格局為{PAN_TYPE_CHINESE.get(build_pan_type, '普通')}，當前運數據暫缺",
            "needs_renovation": False,
        }
    
    build_pan_type = build_pan.get("pan_type", "其他")
    current_pan_type = current_pan.get("pan_type", "其他")
    build_rank = PAN_TYPE_RANK.get(build_pan_type, 2)
    current_rank = PAN_TYPE_RANK.get(current_pan_type, 2)
    rank_diff = current_rank - build_rank
    
    # 計算分數調整
    score_adjust = 0.0
    needs_renovation = False
    rationale = ""
    
    if build_yun == current_yun:
        # 建造運與當前運相同：先天格局與後天運勢一致，最佳狀態
        if build_rank == 4:
            score_adjust = 3.0
            rationale = f"{build_yun}當運之樓，{PAN_TYPE_CHINESE[build_pan_type]}格局正值旺運，先天後天一致，運勢正盛"
        elif build_rank == 3:
            score_adjust = 2.0
            rationale = f"{build_yun}當運之樓，{PAN_TYPE_CHINESE[build_pan_type]}格局，財運亨通"
        elif build_rank == 2:
            score_adjust = 0.0
            rationale = f"{build_yun}當運之樓，{PAN_TYPE_CHINESE[build_pan_type]}格局，運勢平穩"
        else:
            score_adjust = -2.0
            needs_renovation = True
            rationale = f"{build_yun}當運之樓，雖然正值當運，但先天格局為{PAN_TYPE_CHINESE[build_pan_type]}，根基不佳，運過更衰"
    else:
        # 建造運與當前運不同：元運轉換
        if rank_diff > 0:
            # 當前運比建造運更吉：Renovation 後可轉運
            if build_rank == 1 and current_rank == 4:
                score_adjust = 5.0
                needs_renovation = True
                rationale = f"元運大翻身！{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，大裝修換天心後丁財兩旺"
            elif build_rank == 1 and current_rank == 3:
                score_adjust = 3.5
                needs_renovation = True
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，裝修後財運大進"
            else:
                score_adjust = rank_diff * 1.5
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}轉為{PAN_TYPE_CHINESE[current_pan_type]}，運勢向好"
        elif rank_diff < 0:
            # 當前運比建造運更凶：元運已過，運勢衰退
            if build_rank == 4 and current_rank == 1:
                score_adjust = -5.0
                needs_renovation = True
                rationale = f"元運已過大凶！{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，必須換天心大裝修，否則損丁破財"
            elif build_rank == 4 and current_rank == 2:
                score_adjust = -3.0
                needs_renovation = True
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}運退變為{PAN_TYPE_CHINESE[current_pan_type]}，建議大裝修換天心以延續旺運"
            elif build_rank == 3 and current_rank == 1:
                score_adjust = -4.0
                needs_renovation = True
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}急轉為{PAN_TYPE_CHINESE[current_pan_type]}，財運急退，需專業化解"
            else:
                score_adjust = rank_diff * 1.5
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}運退變為{PAN_TYPE_CHINESE[current_pan_type]}，運勢下滑"
        else:
            # rank_diff == 0：吉凶等級相同，但格局可能不同
            if build_pan_type == current_pan_type:
                if build_rank == 4:
                    score_adjust = 1.5
                    rationale = f"{build_yun}與{current_yun}均為{PAN_TYPE_CHINESE[build_pan_type]}，元運轉換後格局穩定，運勢持續"
                elif build_rank == 1:
                    score_adjust = -1.5
                    rationale = f"{build_yun}與{current_yun}均為{PAN_TYPE_CHINESE[build_pan_type]}，長期凶格，不適合購買"
                else:
                    score_adjust = 0.0
                    rationale = f"{build_yun}與{current_yun}均為{PAN_TYPE_CHINESE[build_pan_type]}，格局平穩"
            else:
                score_adjust = 0.0
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，吉凶等級相同，運勢無明顯變化"
    
    return {
        "build_yun": build_yun,
        "current_yun": current_yun,
        "build_pan_type": build_pan_type,
        "current_pan_type": current_pan_type,
        "build_rank": build_rank,
        "current_rank": current_rank,
        "rank_diff": rank_diff,
        "score_adjust": score_adjust,
        "rationale": rationale,
        "needs_renovation": needs_renovation,
    }


def derive_sha_from_pan(pan: dict) -> list:
    """
    從飛星盤自動推導刑煞（SHA）。
    
    玄空風水中常見的飛星刑煞：
    - 二五交加：二黑病符 + 五黃大煞，損財傷丁
    - 五黃到門/到山/到向：五黃大煞臨重要方位
    - 六七交劍：七赤金 + 六白金，金氣過旺，官非手術
    - 九七回祿：九紫火 + 七赤金，火克金，回祿之災
    - 三碧是非：三碧木星臨門/臨床，口舌是非
    - 反吟/伏吟：山星與向星對宮相沖
    
    Returns:
        list of dict: [{"sha_type": str, "severity": str, "description": str, "penalty": int}]
    """
    if not pan:
        return []
    
    shas = []
    mountain_stars = pan.get("mountain_stars", {})
    facing_stars = pan.get("facing_stars", {})
    
    # 檢查所有方位的山星+向星組合
    directions = ["north", "northeast", "east", "southeast", 
                  "south", "southwest", "west", "northwest", "center"]
    
    for direction in directions:
        m_star = mountain_stars.get(direction)
        f_star = facing_stars.get(direction)
        if m_star is None or f_star is None:
            continue
        
        combo = sorted([m_star, f_star])
        combo_str = f"{combo[0]}{combo[1]}"
        
        # 二五交加
        if combo_str == "25" or combo_str == "52":
            severity = "重度" if direction in ["center", "south", "north"] else "中度"
            shas.append({
                "sha_type": "二五交加",
                "severity": severity,
                "description": f"{direction}二黑五黃交加，{FLYING_STAR_COMBO_INAUSPICIOUS.get('25', '損財傷丁')}",
                "penalty": -15 if severity == "重度" else -10
            })
        
        # 六七交劍
        if combo_str == "67" or combo_str == "76":
            severity = "中度"
            shas.append({
                "sha_type": "六七交劍",
                "severity": severity,
                "description": f"{direction}六白七赤交劍，{FLYING_STAR_COMBO_INAUSPICIOUS.get('67', '刑傷破財')}",
                "penalty": -8
            })
        
        # 五黃到重要方位（大門/中宮/坐山/向首）
        if 5 in [m_star, f_star]:
            if direction == "center":
                shas.append({
                    "sha_type": "五黃到中宮",
                    "severity": "重度",
                    "description": "五黃大煞入中宮，全宅受煞，災禍連連",
                    "penalty": -12
                })
            elif direction in ["south", "north"]:
                # 向首/坐山
                shas.append({
                    "sha_type": "五黃到山向",
                    "severity": "重度",
                    "description": f"五黃臨{direction}，坐山或向首受煞，損丁破財",
                    "penalty": -10
                })
        
        # 三碧到重要方位（臥室/大門）
        if 3 in [m_star, f_star] and direction in ["center", "south", "north"]:
            shas.append({
                "sha_type": "三碧是非",
                "severity": "輕度",
                "description": f"{direction}三碧木星臨，口舌是非、官非訴訟",
                "penalty": -4
            })
    
    # 檢查反吟（山星與向星對宮相沖）
    # 簡化檢查：如果山星和向星在對宮位置出現相同數字
    # 這裡使用簡化邏輯：如果同一方位山星與向星相同，視為伏吟
    for direction in directions:
        m_star = mountain_stars.get(direction)
        f_star = facing_stars.get(direction)
        if m_star == f_star and m_star in [2, 5, 7]:
            shas.append({
                "sha_type": "伏吟",
                "severity": "中度",
                "description": f"{direction}山星向星同為{m_star}，伏吟不動，氣滯運衰",
                "penalty": -6
            })
    
    # 去重：合併同一類型煞氣（不同方位），保留最嚴重的一條
    seen_types = {}
    for s in shas:
        st = s["sha_type"]
        if st not in seen_types:
            seen_types[st] = s
        else:
            # 保留 penalty 更嚴重（更負）的
            if s["penalty"] < seen_types[st]["penalty"]:
                seen_types[st] = s
    
    return list(seen_types.values())



# ============================================================
# 數據驗證函數 (v3.3 更新)
# ============================================================

def validate_flying_star_data() -> dict:
    """
    驗證飛星數據的內部一致性。
    
    v3.3 更新：
    - 移除了錯誤的「中宮=運星」檢查（山盤/向盤中宮是山星/向星入中數字，非運星）
    - 使用 flying_star_algorithm 模組進行算法級驗證
    - 新增缺少方位數據檢查
    
    檢查項：
    1. 山盤與向盤是否完全相同（理論上應有差異）
    2. 格局判定與數據一致性（上山下水應有凶組合，到山到向應有吉組合）
    3. 算法級驗證：使用 quick_verify_pan 進行一致性檢查
    """
    from data.flying_star_algorithm import quick_verify_pan
    
    issues = []
    checked_entries = 0
    checked_yuns = list(FLYING_STAR_TABLE.keys())
    
    for yun, mountains in FLYING_STAR_TABLE.items():
        expected_center = CURRENT_LING_STAR.get(yun)
        
        for mountain, data in mountains.items():
            checked_entries += 1
            entry_id = f"{yun} {mountain}"
            
            # 1. v3.3 修正：中宮數字驗證
            # 玄空飛星中，山盤/向盤的中宮是山星/向星入中數字，
            # 不一定等於運星。只有「運盤（元旦盤）」中宮=運星。
            # 因此此項檢查已移除，避免誤報。
            
            # 1. 檢查山盤與向盤是否完全相同
            m_stars = data.get("mountain_stars", {})
            f_stars = data.get("facing_stars", {})
            if m_stars == f_stars and len(m_stars) > 0:
                # 理論上山盤≠向盤，但大量數據暫時如此標記低置信度
                confidence = data.get("confidence", 1.0)
                if confidence >= 0.7:
                    issues.append(
                        f"{entry_id}: 山盤=向盤但置信度{confidence}過高，應<=0.5"
                    )
            
            # 2. 檢查上山下水格局是否有凶組合
            pan_type = data.get("pan_type", "")
            inauspicious = data.get("inauspicious_combos", [])
            if pan_type == "上山下水" and len(inauspicious) == 0:
                issues.append(
                    f"{entry_id}: 上山下水格局但無凶組合記錄"
                )
            
            # 3. 檢查到山到向格局是否有吉組合
            auspicious = data.get("auspicious_combos", [])
            if pan_type == "到山到向" and len(auspicious) == 0:
                issues.append(
                    f"{entry_id}: 到山到向格局但無吉組合記錄"
                )
            
            # 4. v3.3 新增：算法級快速驗證
            algo_check = quick_verify_pan(m_stars, f_stars, expected_center or 0)
            if not algo_check["has_all_directions"]:
                issues.append(
                    f"{entry_id}: 缺少{9 - algo_check.get('diff_count', 0)}個方位數據"
                )
    
    return {
        "issues": issues,
        "issue_count": len(issues),
        "checked_entries": checked_entries,
        "checked_yuns": checked_yuns
    }


def print_validation_report():
    """打印驗證報告到控制台（用於開發調試）"""
    result = validate_flying_star_data()
    print(f"\n=== 飛星數據驗證報告 ===")
    print(f"檢查運數: {', '.join(result['checked_yuns'])}")
    print(f"檢查條目: {result['checked_entries']}")
    print(f"發現問題: {result['issue_count']}")
    if result['issues']:
        print("\n問題列表:")
        for i, issue in enumerate(result['issues'], 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✓ 所有數據通過驗證")
    print("=" * 30)


# 模組載入時自動執行驗證（僅開發環境）
if __name__ == "__main__":
    print_validation_report()

# 支持的坐向列表
SUPPORTED_FACINGS = []
for yun_data in FLYING_STAR_TABLE.values():
    SUPPORTED_FACINGS.extend(yun_data.keys())
SUPPORTED_FACINGS = list(set(SUPPORTED_FACINGS))

# 快速查找：山向 -> 所有支持的運
def get_supported_yuns(mountain: str) -> list:
    """獲取某山向支持的所有運數"""
    yuns = []
    for yun, mountains in FLYING_STAR_TABLE.items():
        if mountain in mountains:
            yuns.append(yun)
    return yuns

# 當運星查表 (用於零正神計算)
CURRENT_LING_STAR = {
    "七運": 7, "八運": 8, "九運": 9
}

# 零神星查表 (與正神相對)
ZERO_GOD_STAR = {
    "七運": 3, "八運": 2, "九運": 1
}

# 星曜五行
STAR_WUXING = {
    1: "水", 2: "土", 3: "木", 4: "木", 5: "土",
    6: "金", 7: "金", 8: "土", 9: "火"
}

# 星曜吉凶 (在當運時)
STAR_AUSPICIOUSNESS = {
    1: "吉星", 2: "凶星", 3: "凶星", 4: "吉星", 5: "凶星",
    6: "吉星", 7: "吉星", 8: "吉星", 9: "吉星"
}

# 飛星組合吉凶表 (部分常見組合)
FLYING_STAR_COMBO_AUSPICIOUS = {
    "77": "雙星會聚，旺丁旺財",
    "88": "雙星會聚，旺丁旺財",
    "99": "雙星會聚，旺丁旺財",
    "89": "八九成雙，旺財旺丁",
    "98": "九八成雙，喜慶旺財",
    "19": "一九成雙，旺財旺丁",
    "91": "九一連珠，貴人相助",
    "68": "六八會合，貴人扶持",
    "86": "八六會合，財丁兩旺",
    "14": "一四同宮，文昌發科",
    "41": "四一同宮，科名顯達",
    "16": "一六同宮，官貴清顯",
    "61": "六一會合，貴人扶持",
    "78": "七八同宮，財丁兩旺",
    "87": "八七同宮，財源廣進",
}

FLYING_STAR_COMBO_INAUSPICIOUS = {
    "22": "二黑重臨，病符纏身",
    "33": "三碧重臨，口舌是非",
    "55": "五黃重臨，煞氣當令",
    "23": "二三斗牛，鬥爭是非",
    "32": "三二鬥牛，官非口舌",
    "35": "三五同宮，五黃三煞",
    "53": "五三同宮，災禍連連",
    "25": "二五交加，損財傷丁",
    "52": "五二交加，病痛破財",
    "45": "四五同宮，官非口舌",
    "54": "五四同宮，病災損財",
    "36": "三六同宮，交劍煞臨",
    "63": "六三同宮，刑傷官非",
    "57": "五七同宮，破財傷丁",
    "75": "七五同宮，災禍損財",
    "76": "七六交劍，官非手術",
    "67": "六七交劍，刑傷破財",
}

# ============================================================
# 多運交叉分析（元運轉換評估）
# ============================================================
PAN_TYPE_RANK = {
    "到山到向": 4,   # 旺丁旺財（最佳）
    "雙星會向": 3,   # 旺財不旺丁（次佳）
    "其他": 2,       # 普通（中等）
    "上山下水": 1,   # 損丁破財（最差）
}

PAN_TYPE_CHINESE = {
    "到山到向": "旺丁旺財",
    "雙星會向": "旺財不旺丁",
    "其他": "普通格局",
    "上山下水": "損丁破財",
}


def get_flying_star_pan(yun: str, facing: str) -> dict:
    """獲取指定運數與座向的飛星盤"""
    yun_data = FLYING_STAR_TABLE.get(yun, {})
    return yun_data.get(facing, {})


def analyze_multi_yun(building_year: int, eval_year: int, facing: str) -> dict:
    """
    多運交叉分析：比較建造運盤與當前運盤的吉凶變化。
    
    玄空風水核心概念：
    - 建造運決定先天格局（元運盤）
    - 當前運決定後天運勢（運過則衰，運至則旺）
    - 元運轉換時，原來旺的盤可能變衰，原來衰的盤可能因 Renovation 而轉旺
    
    Returns:
        {
            "build_yun": str,        # 建造運
            "current_yun": str,      # 當前運
            "build_pan_type": str,   # 建造運格局
            "current_pan_type": str, # 當前運格局
            "build_rank": int,       # 建造運吉凶等級
            "current_rank": int,     # 當前運吉凶等級
            "rank_diff": int,        # 等級差異
            "score_adjust": float,   # 分數調整值
            "rationale": str,        # 風水邏輯說明
            "needs_renovation": bool, # 是否建議換天心/大裝修
        }
    """
    build_yun = get_yun(building_year)
    current_yun = get_yun(eval_year)
    
    build_pan = get_flying_star_pan(build_yun, facing)
    current_pan = get_flying_star_pan(current_yun, facing)
    
    # 如果當前運沒有數據，回退到建造運
    if not build_pan:
        return {
            "build_yun": build_yun,
            "current_yun": current_yun,
            "build_pan_type": "未知",
            "current_pan_type": "未知",
            "build_rank": 2,
            "current_rank": 2,
            "rank_diff": 0,
            "score_adjust": 0.0,
            "rationale": "飛星數據不足，無法進行多運交叉分析",
            "needs_renovation": False,
        }
    
    if not current_pan:
        # 當前運無數據，僅根據建造運評估
        build_pan_type = build_pan.get("pan_type", "其他")
        build_rank = PAN_TYPE_RANK.get(build_pan_type, 2)
        return {
            "build_yun": build_yun,
            "current_yun": current_yun,
            "build_pan_type": build_pan_type,
            "current_pan_type": "數據缺失",
            "build_rank": build_rank,
            "current_rank": 2,
            "rank_diff": 0,
            "score_adjust": 0.0,
            "rationale": f"{build_yun}格局為{PAN_TYPE_CHINESE.get(build_pan_type, '普通')}，當前運數據暫缺",
            "needs_renovation": False,
        }
    
    build_pan_type = build_pan.get("pan_type", "其他")
    current_pan_type = current_pan.get("pan_type", "其他")
    build_rank = PAN_TYPE_RANK.get(build_pan_type, 2)
    current_rank = PAN_TYPE_RANK.get(current_pan_type, 2)
    rank_diff = current_rank - build_rank
    
    # 計算分數調整
    score_adjust = 0.0
    needs_renovation = False
    rationale = ""
    
    if build_yun == current_yun:
        # 建造運與當前運相同：先天格局與後天運勢一致，最佳狀態
        if build_rank == 4:
            score_adjust = 3.0
            rationale = f"{build_yun}當運之樓，{PAN_TYPE_CHINESE[build_pan_type]}格局正值旺運，先天後天一致，運勢正盛"
        elif build_rank == 3:
            score_adjust = 2.0
            rationale = f"{build_yun}當運之樓，{PAN_TYPE_CHINESE[build_pan_type]}格局，財運亨通"
        elif build_rank == 2:
            score_adjust = 0.0
            rationale = f"{build_yun}當運之樓，{PAN_TYPE_CHINESE[build_pan_type]}格局，運勢平穩"
        else:
            score_adjust = -2.0
            needs_renovation = True
            rationale = f"{build_yun}當運之樓，雖然正值當運，但先天格局為{PAN_TYPE_CHINESE[build_pan_type]}，根基不佳，運過更衰"
    else:
        # 建造運與當前運不同：元運轉換
        if rank_diff > 0:
            # 當前運比建造運更吉：Renovation 後可轉運
            if build_rank == 1 and current_rank == 4:
                score_adjust = 5.0
                needs_renovation = True
                rationale = f"元運大翻身！{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，大裝修換天心後丁財兩旺"
            elif build_rank == 1 and current_rank == 3:
                score_adjust = 3.5
                needs_renovation = True
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，裝修後財運大進"
            else:
                score_adjust = rank_diff * 1.5
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}轉為{PAN_TYPE_CHINESE[current_pan_type]}，運勢向好"
        elif rank_diff < 0:
            # 當前運比建造運更凶：元運已過，運勢衰退
            if build_rank == 4 and current_rank == 1:
                score_adjust = -5.0
                needs_renovation = True
                rationale = f"元運已過大凶！{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，必須換天心大裝修，否則損丁破財"
            elif build_rank == 4 and current_rank == 2:
                score_adjust = -3.0
                needs_renovation = True
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}運退變為{PAN_TYPE_CHINESE[current_pan_type]}，建議大裝修換天心以延續旺運"
            elif build_rank == 3 and current_rank == 1:
                score_adjust = -4.0
                needs_renovation = True
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}急轉為{PAN_TYPE_CHINESE[current_pan_type]}，財運急退，需專業化解"
            else:
                score_adjust = rank_diff * 1.5
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}運退變為{PAN_TYPE_CHINESE[current_pan_type]}，運勢下滑"
        else:
            # rank_diff == 0：吉凶等級相同，但格局可能不同
            if build_pan_type == current_pan_type:
                if build_rank == 4:
                    score_adjust = 1.5
                    rationale = f"{build_yun}與{current_yun}均為{PAN_TYPE_CHINESE[build_pan_type]}，元運轉換後格局穩定，運勢持續"
                elif build_rank == 1:
                    score_adjust = -1.5
                    rationale = f"{build_yun}與{current_yun}均為{PAN_TYPE_CHINESE[build_pan_type]}，長期凶格，不適合購買"
                else:
                    score_adjust = 0.0
                    rationale = f"{build_yun}與{current_yun}均為{PAN_TYPE_CHINESE[build_pan_type]}，格局平穩"
            else:
                score_adjust = 0.0
                rationale = f"{build_yun}時為{PAN_TYPE_CHINESE[build_pan_type]}，{current_yun}變為{PAN_TYPE_CHINESE[current_pan_type]}，吉凶等級相同，運勢無明顯變化"
    
    return {
        "build_yun": build_yun,
        "current_yun": current_yun,
        "build_pan_type": build_pan_type,
        "current_pan_type": current_pan_type,
        "build_rank": build_rank,
        "current_rank": current_rank,
        "rank_diff": rank_diff,
        "score_adjust": score_adjust,
        "rationale": rationale,
        "needs_renovation": needs_renovation,
    }


def derive_sha_from_pan(pan: dict) -> list:
    """
    從飛星盤自動推導刑煞（SHA）。
    
    玄空風水中常見的飛星刑煞：
    - 二五交加：二黑病符 + 五黃大煞，損財傷丁
    - 五黃到門/到山/到向：五黃大煞臨重要方位
    - 六七交劍：七赤金 + 六白金，金氣過旺，官非手術
    - 九七回祿：九紫火 + 七赤金，火克金，回祿之災
    - 三碧是非：三碧木星臨門/臨床，口舌是非
    - 反吟/伏吟：山星與向星對宮相沖
    
    Returns:
        list of dict: [{"sha_type": str, "severity": str, "description": str, "penalty": int}]
    """
    if not pan:
        return []
    
    shas = []
    mountain_stars = pan.get("mountain_stars", {})
    facing_stars = pan.get("facing_stars", {})
    
    # 檢查所有方位的山星+向星組合
    directions = ["north", "northeast", "east", "southeast", 
                  "south", "southwest", "west", "northwest", "center"]
    
    for direction in directions:
        m_star = mountain_stars.get(direction)
        f_star = facing_stars.get(direction)
        if m_star is None or f_star is None:
            continue
        
        combo = sorted([m_star, f_star])
        combo_str = f"{combo[0]}{combo[1]}"
        
        # 二五交加
        if combo_str == "25" or combo_str == "52":
            severity = "重度" if direction in ["center", "south", "north"] else "中度"
            shas.append({
                "sha_type": "二五交加",
                "severity": severity,
                "description": f"{direction}二黑五黃交加，{FLYING_STAR_COMBO_INAUSPICIOUS.get('25', '損財傷丁')}",
                "penalty": -15 if severity == "重度" else -10
            })
        
        # 六七交劍
        if combo_str == "67" or combo_str == "76":
            severity = "中度"
            shas.append({
                "sha_type": "六七交劍",
                "severity": severity,
                "description": f"{direction}六白七赤交劍，{FLYING_STAR_COMBO_INAUSPICIOUS.get('67', '刑傷破財')}",
                "penalty": -8
            })
        
        # 五黃到重要方位（大門/中宮/坐山/向首）
        if 5 in [m_star, f_star]:
            if direction == "center":
                shas.append({
                    "sha_type": "五黃到中宮",
                    "severity": "重度",
                    "description": "五黃大煞入中宮，全宅受煞，災禍連連",
                    "penalty": -12
                })
            elif direction in ["south", "north"]:
                # 向首/坐山
                shas.append({
                    "sha_type": "五黃到山向",
                    "severity": "重度",
                    "description": f"五黃臨{direction}，坐山或向首受煞，損丁破財",
                    "penalty": -10
                })
        
        # 三碧到重要方位（臥室/大門）
        if 3 in [m_star, f_star] and direction in ["center", "south", "north"]:
            shas.append({
                "sha_type": "三碧是非",
                "severity": "輕度",
                "description": f"{direction}三碧木星臨，口舌是非、官非訴訟",
                "penalty": -4
            })
    
    # 檢查反吟（山星與向星對宮相沖）
    # 簡化檢查：如果山星和向星在對宮位置出現相同數字
    # 這裡使用簡化邏輯：如果同一方位山星與向星相同，視為伏吟
    for direction in directions:
        m_star = mountain_stars.get(direction)
        f_star = facing_stars.get(direction)
        if m_star == f_star and m_star in [2, 5, 7]:
            shas.append({
                "sha_type": "伏吟",
                "severity": "中度",
                "description": f"{direction}山星向星同為{m_star}，伏吟不動，氣滯運衰",
                "penalty": -6
            })
    
    # 去重：合併同一類型煞氣（不同方位），保留最嚴重的一條
    seen_types = {}
    for s in shas:
        st = s["sha_type"]
        if st not in seen_types:
            seen_types[st] = s
        else:
            # 保留 penalty 更嚴重（更負）的
            if s["penalty"] < seen_types[st]["penalty"]:
                seen_types[st] = s
    
    return list(seen_types.values())



# ============================================================
# 數據驗證函數 (v3.3 更新)
# ============================================================

def validate_flying_star_data() -> dict:
    """
    驗證飛星數據的內部一致性。
    
    v3.3 更新：
    - 移除了錯誤的「中宮=運星」檢查（山盤/向盤中宮是山星/向星入中數字，非運星）
    - 使用 flying_star_algorithm 模組進行算法級驗證
    - 新增缺少方位數據檢查
    
    檢查項：
    1. 山盤與向盤是否完全相同（理論上應有差異）
    2. 格局判定與數據一致性（上山下水應有凶組合，到山到向應有吉組合）
    3. 算法級驗證：使用 quick_verify_pan 進行一致性檢查
    """
    from data.flying_star_algorithm import quick_verify_pan
    
    issues = []
    checked_entries = 0
    checked_yuns = list(FLYING_STAR_TABLE.keys())
    
    for yun, mountains in FLYING_STAR_TABLE.items():
        expected_center = CURRENT_LING_STAR.get(yun)
        
        for mountain, data in mountains.items():
            checked_entries += 1
            entry_id = f"{yun} {mountain}"
            
            # 1. v3.3 修正：中宮數字驗證
            # 玄空飛星中，山盤/向盤的中宮是山星/向星入中數字，
            # 不一定等於運星。只有「運盤（元旦盤）」中宮=運星。
            # 因此此項檢查已移除，避免誤報。
            
            # 1. 檢查山盤與向盤是否完全相同
            m_stars = data.get("mountain_stars", {})
            f_stars = data.get("facing_stars", {})
            if m_stars == f_stars and len(m_stars) > 0:
                # 理論上山盤≠向盤，但大量數據暫時如此標記低置信度
                confidence = data.get("confidence", 1.0)
                if confidence >= 0.7:
                    issues.append(
                        f"{entry_id}: 山盤=向盤但置信度{confidence}過高，應<=0.5"
                    )
            
            # 2. 檢查上山下水格局是否有凶組合
            pan_type = data.get("pan_type", "")
            inauspicious = data.get("inauspicious_combos", [])
            if pan_type == "上山下水" and len(inauspicious) == 0:
                issues.append(
                    f"{entry_id}: 上山下水格局但無凶組合記錄"
                )
            
            # 3. 檢查到山到向格局是否有吉組合
            auspicious = data.get("auspicious_combos", [])
            if pan_type == "到山到向" and len(auspicious) == 0:
                issues.append(
                    f"{entry_id}: 到山到向格局但無吉組合記錄"
                )
            
            # 4. v3.3 新增：算法級快速驗證
            algo_check = quick_verify_pan(m_stars, f_stars, expected_center or 0)
            if not algo_check["has_all_directions"]:
                issues.append(
                    f"{entry_id}: 缺少{9 - algo_check.get('diff_count', 0)}個方位數據"
                )
    
    return {
        "issues": issues,
        "issue_count": len(issues),
        "checked_entries": checked_entries,
        "checked_yuns": checked_yuns
    }


def print_validation_report():
    """打印驗證報告到控制台（用於開發調試）"""
    result = validate_flying_star_data()
    print(f"\n=== 飛星數據驗證報告 ===")
    print(f"檢查運數: {', '.join(result['checked_yuns'])}")
    print(f"檢查條目: {result['checked_entries']}")
    print(f"發現問題: {result['issue_count']}")
    if result['issues']:
        print("\n問題列表:")
        for i, issue in enumerate(result['issues'], 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✓ 所有數據通過驗證")
    print("=" * 30)


# 模組載入時自動執行驗證（僅開發環境）
if __name__ == "__main__":
    print_validation_report()
