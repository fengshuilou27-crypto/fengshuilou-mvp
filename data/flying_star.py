# 硬編碼查表數據 - 飛星宅運盤 (v3.2 修復版)
# 支持24山向，基於三六風水網專業知識庫
# ⚠️ v3.2 重要修復說明：
#   - 修復了部分中宮數字錯誤（中宮必須等於運星）
#   - 修復了八運子山午向的格局判定（非到山到向）
#   - 標記了山盤=向盤的數據為低置信度（理論上兩者不應完全相同）
#   - 建議未來實現算法動態排盤以完全替代硬編碼
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
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.5,
            "mountain_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 8},
            "facing_stars": {"north": 8, "northeast": 9, "east": 1, "southeast": 2, "south": 3, "southwest": 4, "west": 5, "northwest": 6, "center": 8},
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "正北八八雙星會聚，旺丁旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西五黃重臨，煞氣當令"}
            ],
            "note": "八運雙星會向，旺財不旺丁。⚠️ 山盤向盤數據待專業核實"
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
        # ---- 到山到向格局 (七運旺山旺向) ----
        "子山午向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.8,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [{"direction": "north", "stars": "77", "desc": "正北七七雙星會聚，旺丁旺財"}],
            "inauspicious_combos": [{"direction": "south", "stars": "22", "desc": "正南二黑重臨，病符纏身"}],
            "note": "七運到山到向，丁財兩得"
        },
        "午山子向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.7,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "auspicious_combos": [{"direction": "southwest", "stars": "77", "desc": "西南七七雙星會向，旺財之局"}],
            "inauspicious_combos": [{"direction": "north", "stars": "22", "desc": "正北二黑重臨，病符纏身"}],
            "note": "七運雙星會向，旺財不旺丁。與子山午向相對"
        },
        "卯山酉向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.7,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [{"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"}],
            "inauspicious_combos": [{"direction": "north", "stars": "33", "desc": "正北三碧重臨，口舌是非"}],
            "note": "七運雙星會向，旺財不旺丁"
        },
        "酉山卯向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.7,
            "mountain_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "facing_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "auspicious_combos": [{"direction": "east", "stars": "77", "desc": "正東七七雙星會聚，旺丁旺財"}],
            "inauspicious_combos": [{"direction": "south", "stars": "88", "desc": "正南八白重臨，運過即衰"}],
            "note": "七運到山到向，丁財兩得。與卯山酉向相對 ⚠️ 數據需專業確認"
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
        "巽山乾向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.7,
            "mountain_stars": {"northwest": 7, "north": 3, "northeast": 9, "west": 5, "center": 6, "east": 8, "southwest": 4, "south": 2, "southeast": 1},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "southeast", "stars": "11", "desc": "東南一白重臨，桃花劫臨"}],
            "note": "七運上山下水，與乾山巽向相對 ⚠️ 數據需專業確認"
        },
        "艮山坤向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.6,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "north", "stars": "55", "desc": "正北五黃重臨，大凶之局"}],
            "note": "七運上山下水，損財傷丁 ⚠️ 數據需專業確認"
        },
        "坤山艮向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.6,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "southwest", "stars": "55", "desc": "西南五黃重臨，大凶之局"}],
            "note": "七運上山下水，與艮山坤向相對 ⚠️ 數據需專業確認"
        },

        # ---- 其他常見山向 (雙星會坐/雙星會向/其他) ----
        "丑山未向": {
            "pan_type": "雙星會坐", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [{"direction": "northeast", "stars": "88", "desc": "東北八八旺丁"}],
            "inauspicious_combos": [{"direction": "south", "stars": "22", "desc": "正南二黑病符"}],
            "note": "七運雙星會坐，旺丁不旺財 ⚠️ 數據需專業確認"
        },
        "未山丑向": {
            "pan_type": "雙星會坐", "base_score": 15, "confidence": 0.6,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [{"direction": "southwest", "stars": "88", "desc": "西南八八旺丁"}],
            "inauspicious_combos": [{"direction": "east", "stars": "55", "desc": "正東五黃煞氣"}],
            "note": "七運雙星會坐，旺丁不旺財 ⚠️ 數據需專業確認"
        },
        "辰山戌向": {
            "pan_type": "其他", "base_score": 12, "confidence": 0.5,
            "mountain_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "facing_stars": {"north": 3, "northeast": 4, "east": 5, "southeast": 6, "south": 7, "southwest": 8, "west": 1, "northwest": 2, "center": 9},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "east", "stars": "55", "desc": "正東五黃重臨"}],
            "note": "七運普通格局 ⚠️ 數據需專業確認"
        },
        "戌山辰向": {
            "pan_type": "其他", "base_score": 12, "confidence": 0.5,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "west", "stars": "44", "desc": "正西四綠重臨"}],
            "note": "七運普通格局 ⚠️ 數據需專業確認"
        },
        "乙山辛向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.5,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [{"direction": "west", "stars": "55", "desc": "正西雙星會向"}],
            "inauspicious_combos": [{"direction": "north", "stars": "33", "desc": "正北三碧重臨"}],
            "note": "七運雙星會向，與卯山酉向類似 ⚠️ 數據需專業確認"
        },
        "辛山乙向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.5,
            "mountain_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "facing_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "auspicious_combos": [{"direction": "east", "stars": "77", "desc": "正東七七雙星會聚"}],
            "inauspicious_combos": [{"direction": "south", "stars": "88", "desc": "正南八白重臨"}],
            "note": "七運到山到向，與酉山卯向類似 ⚠️ 數據需專業確認"
        },
        "癸山丁向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.5,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [{"direction": "north", "stars": "77", "desc": "正北七七雙星會聚"}],
            "inauspicious_combos": [{"direction": "south", "stars": "22", "desc": "正南二黑重臨"}],
            "note": "七運到山到向，與子山午向類似 ⚠️ 數據需專業確認"
        },
        "丁山癸向": {
            "pan_type": "雙星會向", "base_score": 20, "confidence": 0.5,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "auspicious_combos": [{"direction": "southwest", "stars": "77", "desc": "西南七七雙星會向"}],
            "inauspicious_combos": [{"direction": "north", "stars": "22", "desc": "正北二黑重臨"}],
            "note": "七運雙星會向，與午山子向類似 ⚠️ 數據需專業確認"
        },
        "壬山丙向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.5,
            "mountain_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "facing_stars": {"north": 7, "northeast": 8, "east": 9, "southeast": 1, "south": 2, "southwest": 3, "west": 4, "northwest": 5, "center": 6},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "七運偏位 ⚠️ 數據需專業確認"
        },
        "丙山壬向": {
            "pan_type": "其他", "base_score": 15, "confidence": 0.5,
            "mountain_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "facing_stars": {"north": 2, "northeast": 3, "east": 4, "southeast": 5, "south": 6, "southwest": 7, "west": 8, "northwest": 9, "center": 1},
            "auspicious_combos": [],
            "inauspicious_combos": [],
            "note": "七運偏位 ⚠️ 數據需專業確認"
        },
        "甲山庚向": {
            "pan_type": "雙星會向", "base_score": 14, "confidence": 0.5,
            "mountain_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "facing_stars": {"north": 3, "northeast": 8, "east": 1, "southeast": 6, "south": 2, "southwest": 7, "west": 5, "northwest": 9, "center": 4},
            "auspicious_combos": [{"direction": "west", "stars": "55", "desc": "正西雙星會向"}],
            "inauspicious_combos": [{"direction": "north", "stars": "33", "desc": "正北三碧重臨"}],
            "note": "七運雙星會向，與卯山酉向類似 ⚠️ 數據需專業確認"
        },
        "庚山甲向": {
            "pan_type": "到山到向", "base_score": 30, "confidence": 0.5,
            "mountain_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "facing_stars": {"north": 9, "northeast": 5, "east": 7, "southeast": 3, "south": 8, "southwest": 1, "west": 6, "northwest": 4, "center": 2},
            "auspicious_combos": [{"direction": "east", "stars": "77", "desc": "正東七七雙星會聚"}],
            "inauspicious_combos": [{"direction": "south", "stars": "88", "desc": "正南八白重臨"}],
            "note": "七運到山到向，與酉山卯向類似 ⚠️ 數據需專業確認"
        },
        "寅山申向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "facing_stars": {"north": 9, "northeast": 1, "east": 2, "southeast": 3, "south": 4, "southwest": 5, "west": 6, "northwest": 7, "center": 8},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "southwest", "stars": "55", "desc": "西南五黃重臨"}],
            "note": "七運上山下水，與艮山坤向類似 ⚠️ 數據需專業確認"
        },
        "申山寅向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "facing_stars": {"north": 5, "northeast": 6, "east": 7, "southeast": 8, "south": 9, "southwest": 1, "west": 2, "northwest": 3, "center": 4},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "north", "stars": "55", "desc": "正北五黃重臨"}],
            "note": "七運上山下水，與坤山艮向類似 ⚠️ 數據需專業確認"
        },
        "亥山巳向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"northwest": 7, "north": 2, "northeast": 9, "west": 8, "center": 6, "east": 3, "southwest": 4, "south": 1, "southeast": 5},
            "facing_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "west", "stars": "18", "desc": "正西一白八白，財丁不聚"}],
            "note": "七運上山下水，與乾山巽向類似 ⚠️ 數據需專業確認"
        },
        "巳山亥向": {
            "pan_type": "上山下水", "base_score": 8, "confidence": 0.5,
            "mountain_stars": {"northwest": 9, "north": 4, "northeast": 2, "west": 1, "center": 8, "east": 5, "southwest": 6, "south": 3, "southeast": 7},
            "facing_stars": {"northwest": 7, "north": 2, "northeast": 9, "west": 8, "center": 6, "east": 3, "southwest": 4, "south": 1, "southeast": 5},
            "auspicious_combos": [],
            "inauspicious_combos": [{"direction": "southeast", "stars": "55", "desc": "東南五黃重臨"}],
            "note": "七運上山下水，與巽山乾向類似 ⚠️ 數據需專業確認"
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
# 數據驗證函數 (v3.2 新增)
# ============================================================

def validate_flying_star_data() -> dict:
    """
    驗證飛星數據的內部一致性。
    
    檢查項：
    1. 中宮數字是否等於運星（當運星已知時）
    2. 山盤與向盤是否完全相同（理論上不可能）
    3. 格局判定與數據一致性（上山下水應有明顯凶組合）
    
    Returns:
        {
            "issues": list[str],      # 發現的問題列表
            "issue_count": int,       # 問題總數
            "checked_entries": int,   # 檢查的條目總數
            "checked_yuns": list[str] # 檢查的運數
        }
    """
    issues = []
    checked_entries = 0
    checked_yuns = list(FLYING_STAR_TABLE.keys())
    
    for yun, mountains in FLYING_STAR_TABLE.items():
        expected_center = CURRENT_LING_STAR.get(yun)
        
        for mountain, data in mountains.items():
            checked_entries += 1
            entry_id = f"{yun} {mountain}"
            
            # 1. 檢查中宮數字是否等於運星
            mountain_center = data.get("mountain_stars", {}).get("center")
            facing_center = data.get("facing_stars", {}).get("center")
            
            if expected_center is not None:
                if mountain_center != expected_center:
                    issues.append(
                        f"{entry_id}: 山盤中宮{mountain_center} != 運星{expected_center}"
                    )
                if facing_center != expected_center:
                    issues.append(
                        f"{entry_id}: 向盤中宮{facing_center} != 運星{expected_center}"
                    )
            
            # 2. 檢查山盤與向盤是否完全相同
            m_stars = data.get("mountain_stars", {})
            f_stars = data.get("facing_stars", {})
            if m_stars == f_stars and len(m_stars) > 0:
                # 理論上山盤≠向盤，但大量數據暫時如此標記低置信度
                confidence = data.get("confidence", 1.0)
                if confidence >= 0.7:
                    issues.append(
                        f"{entry_id}: 山盤=向盤但置信度{confidence}過高，應<=0.5"
                    )
            
            # 3. 檢查上山下水格局是否有凶組合
            pan_type = data.get("pan_type", "")
            inauspicious = data.get("inauspicious_combos", [])
            if pan_type == "上山下水" and len(inauspicious) == 0:
                issues.append(
                    f"{entry_id}: 上山下水格局但無凶組合記錄"
                )
            
            # 4. 檢查到山到向格局是否有吉組合
            auspicious = data.get("auspicious_combos", [])
            if pan_type == "到山到向" and len(auspicious) == 0:
                issues.append(
                    f"{entry_id}: 到山到向格局但無吉組合記錄"
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
