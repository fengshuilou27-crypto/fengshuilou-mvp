# 硬編碼查表數據 - 飛星宅運盤 (v2.2 擴展版)
# 支持24山向，基於三六風水網專業知識庫
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
    # ============================
    # 八運 (2004-2023)
    # ============================
    "八運": {
        # ---- 到山到向格局 (6組) ----
        "丑山未向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 9},
            "facing_stars": {"north": 7, "northeast": 8, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 9},
            "auspicious_combos": [
                {"direction": "northeast", "stars": "88", "desc": "東北八八雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "55", "desc": "正西五六合化，財運亨通"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "33", "desc": "正南三碧重臨，口舌是非"}
            ],
            "note": "八運到山到向，丁財兩得。旺山旺向格局"
        },
        "未山丑向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "88", "desc": "西南八八雙星會聚，旺丁旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "55", "desc": "正東五黃重臨，煞氣當令"}
            ],
            "note": "八運到山到向，與丑山未向相對"
        },
        "乾山巽向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"northwest": 6, "north": 2, "northeast": 4, "west": 5, "center": 8, "east": 9, "southwest": 3, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 8, "north": 6, "northeast": 1, "west": 4, "center": 3, "east": 2, "southwest": 7, "south": 5, "southeast": 9},
            "auspicious_combos": [
                {"direction": "southeast", "stars": "19", "desc": "東南一九成雙，旺財旺丁"},
                {"direction": "northwest", "stars": "68", "desc": "西北六八會合，貴人扶持"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "26", "desc": "正北二黑六白，病符損財"}
            ],
            "note": "八運到山到向，丁財兩得。沙田第一城等西北向樓宇"
        },
        "巽山乾向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"northwest": 1, "north": 7, "northeast": 3, "west": 9, "center": 8, "east": 5, "southwest": 4, "south": 2, "southeast": 6},
            "facing_stars": {"northwest": 9, "north": 1, "northeast": 6, "west": 2, "center": 3, "east": 4, "southwest": 5, "south": 7, "southeast": 8},
            "auspicious_combos": [
                {"direction": "northwest", "stars": "19", "desc": "西北一九成雙，旺財旺丁"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "72", "desc": "正南七赤二黑，破財病符"}
            ],
            "note": "八運到山到向，與乾山巽向相對"
        },
        "亥山巳向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"northwest": 6, "north": 2, "northeast": 4, "west": 5, "center": 8, "east": 9, "southwest": 3, "south": 7, "southeast": 1},
            "facing_stars": {"northwest": 8, "north": 6, "northeast": 1, "west": 4, "center": 3, "east": 2, "southwest": 7, "south": 5, "southeast": 9},
            "auspicious_combos": [
                {"direction": "southeast", "stars": "19", "desc": "東南一九成雙，旺財旺丁"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "26", "desc": "正北二黑六白，病符損財"}
            ],
            "note": "八運到山到向，與乾山巽向類似"
        },
        "巳山亥向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"northwest": 1, "north": 7, "northeast": 3, "west": 9, "center": 8, "east": 5, "southwest": 4, "south": 2, "southeast": 6},
            "facing_stars": {"northwest": 9, "north": 1, "northeast": 6, "west": 2, "center": 3, "east": 4, "southwest": 5, "south": 7, "southeast": 8},
            "auspicious_combos": [
                {"direction": "northwest", "stars": "19", "desc": "西北一九成雙，旺財旺丁"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "72", "desc": "正南七赤二黑，破財病符"}
            ],
            "note": "八運到山到向，與亥山巳向相對"
        },

        # ---- 上山下水格局 (6組) ----
        "坤山艮向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "55", "desc": "正北五黃重臨，大凶之局"}
            ],
            "note": "八運上山下水，損財傷丁。建議重新佈局或換天心"
        },
        "艮山坤向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "55", "desc": "西南五黃重臨，大凶之局"}
            ],
            "note": "八運上山下水，與坤山艮向相對"
        },
        "寅山申向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "55", "desc": "西南五黃重臨，大凶之局"}
            ],
            "note": "八運上山下水，與艮山坤向類似"
        },
        "申山寅向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "55", "desc": "正北五黃重臨，大凶之局"}
            ],
            "note": "八運上山下水，與坤山艮向類似"
        },
        "辰山戌向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "east", "stars": "55", "desc": "正東五黃重臨，大凶之局"}
            ],
            "note": "八運上山下水"
        },
        "戌山辰向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 9},
            "facing_stars": {"north": 7, "northeast": 8, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西五黃重臨，大凶之局"}
            ],
            "note": "八運上山下水"
        },

        # ---- 其他常見山向 (雙星會向/雙星會坐) ----
        "子山午向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 7},
            "facing_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 7},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "正北八八雙星會聚，旺丁旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西五黃重臨，煞氣當令"}
            ],
            "note": "八運到山到向，丁財兩得"
        },
        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [
                {"direction": "southwest", "stars": "88", "desc": "西南八八旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "east", "stars": "55", "desc": "正東五黃煞氣"}
            ],
            "note": "八運雙星會向，旺財不旺丁"
        },
        "卯山酉向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 9, "east": 2, "southeast": 7, "south": 3, "southwest": 8, "west": 5, "northwest": 1, "center": 6},
            "facing_stars": {"north": 4, "northeast": 9, "east": 2, "southeast": 7, "south": 3, "southwest": 8, "west": 5, "northwest": 1, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "44", "desc": "正北四綠重臨，文昌受阻"}
            ],
            "note": "八運雙星會向，YOHO Town等東向樓宇"
        },
        "酉山卯向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 1, "east": 5, "southeast": 3, "south": 7, "southwest": 9, "west": 2, "northwest": 4, "center": 8},
            "facing_stars": {"north": 6, "northeast": 1, "east": 5, "southeast": 3, "south": 7, "southwest": 9, "west": 2, "northwest": 4, "center": 8},
            "auspicious_combos": [
                {"direction": "east", "stars": "55", "desc": "正東雙星會向，旺財之局"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "22", "desc": "正西二黑重臨，病符纏身"}
            ],
            "note": "八運雙星會向，與卯山酉向相對"
        },
        "乙山辛向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 4, "northeast": 9, "east": 2, "southeast": 7, "south": 3, "southwest": 8, "west": 5, "northwest": 1, "center": 6},
            "facing_stars": {"north": 4, "northeast": 9, "east": 2, "southeast": 7, "south": 3, "southwest": 8, "west": 5, "northwest": 1, "center": 6},
            "auspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "44", "desc": "正北四綠重臨，文昌受阻"}
            ],
            "note": "八運雙星會向，與卯山酉向類似"
        },
        "辛山乙向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 6, "northeast": 1, "east": 5, "southeast": 3, "south": 7, "southwest": 9, "west": 2, "northwest": 4, "center": 8},
            "facing_stars": {"north": 6, "northeast": 1, "east": 5, "southeast": 3, "south": 7, "southwest": 9, "west": 2, "northwest": 4, "center": 8},
            "auspicious_combos": [
                {"direction": "east", "stars": "55", "desc": "正東雙星會向，旺財之局"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "22", "desc": "正西二黑重臨，病符纏身"}
            ],
            "note": "八運雙星會向，與酉山卯向類似"
        },
        "壬山丙向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 7},
            "facing_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "八運偏位，數據需專業確認"
        },
        "丙山壬向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "八運偏位，數據需專業確認"
        },
        "甲山庚向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 4, "northeast": 9, "east": 2, "southeast": 7, "south": 3, "southwest": 8, "west": 5, "northwest": 1, "center": 6},
            "facing_stars": {"north": 4, "northeast": 9, "east": 2, "southeast": 7, "south": 3, "southwest": 8, "west": 5, "northwest": 1, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "八運偏位，數據需專業確認"
        },
        "庚山甲向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 6, "northeast": 1, "east": 5, "southeast": 3, "south": 7, "southwest": 9, "west": 2, "northwest": 4, "center": 8},
            "facing_stars": {"north": 6, "northeast": 1, "east": 5, "southeast": 3, "south": 7, "southwest": 9, "west": 2, "northwest": 4, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "八運偏位，數據需專業確認"
        },
        "癸山丁向": {
            "pan_type": "其他", "base_score": 18, "confidence": 0.6,
            "mountain_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 7},
            "facing_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "八運偏位，與子山午向類似"
        },
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "八運雙星會向，與午山子向類似"
        },
    },

    # ============================
    # 九運 (2024-2043)
    # ============================
    "九運": {
        # ---- 到山到向格局 (10組) ----
        "子山午向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.9,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [
                {"direction": "south", "stars": "89", "desc": "正南八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "91", "desc": "正北九一連珠，貴人相助"}
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "56", "desc": "西北五黃六白交加，損財傷丁"}
            ],
            "note": "九運到山到向，丁財兩得。太古城等正南樓宇"
        },
        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.9,
            "mountain_stars": {"northwest": 8, "north": 5, "northeast": 3, "west": 1, "center": 6, "east": 4, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 9, "north": 7, "northeast": 5, "west": 2, "center": 1, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "57", "desc": "正北五七會合，偏財旺盛"},
                {"direction": "southwest", "stars": "98", "desc": "西南九八成雙，喜慶旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "正南七赤六白，交劍煞臨"}
            ],
            "note": "九運雙星會向，旺財之局"
        },
        "卯山酉向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "facing_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "auspicious_combos": [
                {"direction": "east", "stars": "88", "desc": "正東八八雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "99", "desc": "東南九九連珠，喜慶連連"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "11", "desc": "正西一白過旺，桃花劫臨"}
            ],
            "note": "九運到山到向，丁財兩得"
        },
        "酉山卯向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.8,
            "mountain_stars": {"north": 1, "northeast": 6, "east": 8, "southeast": 2, "south": 7, "southwest": 3, "west": 9, "northwest": 4, "center": 5},
            "facing_stars": {"north": 1, "northeast": 6, "east": 8, "southeast": 2, "south": 7, "southwest": 3, "west": 9, "northwest": 4, "center": 5},
            "auspicious_combos": [
                {"direction": "east", "stars": "88", "desc": "正東雙星會向，旺財旺丁"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "99", "desc": "正西九紫重臨，火煞過旺"}
            ],
            "note": "九運雙星會向，旺財之局"
        },
        "乾山巽向": {
            "pan_type": "上山下水", "base_score": 5, "confidence": 0.8,
            "mountain_stars": {"northwest": 3, "north": 7, "northeast": 5, "west": 9, "center": 1, "east": 2, "southwest": 6, "south": 4, "southeast": 8},
            "facing_stars": {"northwest": 3, "north": 7, "northeast": 5, "west": 9, "center": 1, "east": 2, "southwest": 6, "south": 4, "southeast": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "99", "desc": "正西九紫重臨，火煞過旺"},
                {"direction": "center", "stars": "11", "desc": "中宮一白過旺，桃花劫臨"}
            ],
            "note": "九運上山下水，損財傷丁。建議重新佈局或換天心"
        },
        "巽山乾向": {
            "pan_type": "上山下水", "base_score": 5, "confidence": 0.8,
            "mountain_stars": {"northwest": 8, "north": 4, "northeast": 6, "west": 2, "center": 1, "east": 5, "southwest": 7, "south": 3, "southeast": 9},
            "facing_stars": {"northwest": 8, "north": 4, "northeast": 6, "west": 2, "center": 1, "east": 5, "southwest": 7, "south": 3, "southeast": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southeast", "stars": "99", "desc": "東南九紫重臨，火煞過旺"}
            ],
            "note": "九運上山下水，與乾山巽向相對"
        },
        "丑山未向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 3, "northeast": 2, "east": 7, "southeast": 6, "south": 5, "southwest": 4, "west": 9, "northwest": 8, "center": 1},
            "facing_stars": {"north": 3, "northeast": 2, "east": 7, "southeast": 6, "south": 5, "southwest": 4, "west": 9, "northwest": 8, "center": 1},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "99", "desc": "正西九紫重臨，火煞過旺"}
            ],
            "note": "九運到山到向，數據需專業確認"
        },
        "未山丑向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "九運到山到向，與丑山未向相對"
        },
        "亥山巳向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "facing_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "auspicious_combos": [
                {"direction": "east", "stars": "88", "desc": "正東八八雙星會聚，旺丁旺財"}
            ],
            "inauspicious_combos": [],
            "note": "九運到山到向，與卯山酉向類似"
        },
        "巳山亥向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "facing_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "auspicious_combos": [
                {"direction": "east", "stars": "88", "desc": "正東八八雙星會聚，旺丁旺財"}
            ],
            "inauspicious_combos": [],
            "note": "九運到山到向，與亥山巳向相對"
        },

        # ---- 上山下水格局 (6組) ----
        "坤山艮向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "55", "desc": "正北五黃重臨，大凶之局"}
            ],
            "note": "九運上山下水，損財傷丁"
        },
        "艮山坤向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "55", "desc": "西南五黃重臨，大凶之局"}
            ],
            "note": "九運上山下水，與坤山艮向相對"
        },
        "寅山申向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "southwest", "stars": "55", "desc": "西南五黃重臨，大凶之局"}
            ],
            "note": "九運上山下水，與艮山坤向類似"
        },
        "申山寅向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "north", "stars": "55", "desc": "正北五黃重臨，大凶之局"}
            ],
            "note": "九運上山下水，與坤山艮向類似"
        },
        "辰山戌向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "east", "stars": "55", "desc": "正東五黃重臨，大凶之局"}
            ],
            "note": "九運上山下水"
        },
        "戌山辰向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "44", "desc": "正西四綠重臨，文曲受阻"}
            ],
            "note": "九運上山下水"
        },

        # ---- 其他常見山向 ----
        "乙山辛向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.8,
            "mountain_stars": {"northwest": 8, "north": 5, "northeast": 3, "west": 1, "center": 6, "east": 4, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 9, "north": 7, "northeast": 5, "west": 2, "center": 1, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "57", "desc": "正北五七會合，偏財旺盛"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "正南七赤六白，交劍煞臨"}
            ],
            "note": "九運雙星會向，旺財之局"
        },
        "辛山乙向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.8,
            "mountain_stars": {"northwest": 1, "north": 6, "northeast": 4, "west": 2, "center": 7, "east": 5, "southwest": 3, "south": 9, "southeast": 8},
            "facing_stars": {"northwest": 1, "north": 6, "northeast": 4, "west": 2, "center": 7, "east": 5, "southwest": 3, "south": 9, "southeast": 8},
            "auspicious_combos": [
                {"direction": "southeast", "stars": "88", "desc": "東南八白旺財"}
            ],
            "inauspicious_combos": [],
            "note": "九運雙星會向，數據需專業確認"
        },
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.8,
            "mountain_stars": {"northwest": 8, "north": 5, "northeast": 3, "west": 1, "center": 6, "east": 4, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 9, "north": 7, "northeast": 5, "west": 2, "center": 1, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [
                {"direction": "north", "stars": "57", "desc": "正北五七會合，偏財旺盛"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "正南七赤六白，交劍煞臨"}
            ],
            "note": "九運雙星會向，與午山子向類似"
        },
        "癸山丁向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [
                {"direction": "south", "stars": "89", "desc": "正南八九成雙，旺財旺丁"}
            ],
            "inauspicious_combos": [],
            "note": "九運到山到向，與子山午向類似"
        },
        "壬山丙向": {
            "pan_type": "其他", "base_score": 18, "confidence": 0.6,
            "mountain_stars": {"north": 9, "northeast": 7, "east": 2, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 5, "center": 4},
            "facing_stars": {"north": 1, "northeast": 8, "east": 3, "southeast": 4, "south": 9, "southwest": 2, "west": 7, "northwest": 6, "center": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "九運偏位，數據需專業確認"
        },
        "丙山壬向": {
            "pan_type": "其他", "base_score": 18, "confidence": 0.6,
            "mountain_stars": {"northwest": 8, "north": 5, "northeast": 3, "west": 1, "center": 6, "east": 4, "southwest": 9, "south": 7, "southeast": 2},
            "facing_stars": {"northwest": 9, "north": 7, "northeast": 5, "west": 2, "center": 1, "east": 3, "southwest": 8, "south": 6, "southeast": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "九運偏位，數據需專業確認"
        },
        "甲山庚向": {
            "pan_type": "其他", "base_score": 18, "confidence": 0.6,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "facing_stars": {"north": 2, "northeast": 3, "east": 8, "southeast": 9, "south": 4, "southwest": 5, "west": 1, "northwest": 6, "center": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "九運偏位，數據需專業確認"
        },
        "庚山甲向": {
            "pan_type": "其他", "base_score": 18, "confidence": 0.6,
            "mountain_stars": {"north": 1, "northeast": 6, "east": 8, "southeast": 2, "south": 7, "southwest": 3, "west": 9, "northwest": 4, "center": 5},
            "facing_stars": {"north": 1, "northeast": 6, "east": 8, "southeast": 2, "south": 7, "southwest": 3, "west": 9, "northwest": 4, "center": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "九運偏位，數據需專業確認"
        },
    },

    # ============================
    # 七運 (1984-2003) - 保留原有數據
    # ============================
    "七運": {
        "子山午向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [{"direction": "north", "stars": "77", "desc": "正北七七雙星會聚，旺丁旺財"}],
            "inauspicious_combos": [{"direction": "south", "stars": "22", "desc": "正南二黑重臨，病符纏身"}],
            "note": "七運到山到向，丁財兩得"
        },
        "乾山巽向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.8,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "facing_stars": {"northwest": 7, "north": 2, "northeast": 9, "west": 8, "center": 6, "east": 3, "southwest": 4, "south": 1, "southeast": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "18", "desc": "正西一白八白，財丁不聚"},
                {"direction": "center", "stars": "86", "desc": "中宮八白六白，運過即衰"}
            ],
            "note": "七運上山下水，損財傷丁"
        },
        "卯山酉向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [{"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"}],
            "inauspicious_combos": [{"direction": "north", "stars": "33", "desc": "正北三碧重臨，口舌是非"}],
            "note": "七運雙星會向，旺財不旺丁"
        },
    }
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
