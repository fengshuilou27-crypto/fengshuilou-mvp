# 硬編碼查表數據 - 飛星宅運盤 (擴展版)
# 支持多種坐向，用於回測案例和 CCMF Demo
# ⚠️ MVP 簡化排盤，數據基於公開資料，具體需專業師傅確認

# 八運 (2004-2023) 宅運盤
# 九運 (2024-2043) 宅運盤

FLYING_STAR_TABLE = {
    # ============================
    # 七運 (1984-2003)
    # ============================
    "七運": {
        # ---- 子山午向 (到山到向) ----
        "子山午向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "north": 7, "northeast": 8, "east": 9,
                "southeast": 1, "south": 2, "southwest": 3,
                "west": 4, "northwest": 5, "center": 6
            },
            "facing_stars": {
                "north": 7, "northeast": 8, "east": 9,
                "southeast": 1, "south": 2, "southwest": 3,
                "west": 4, "northwest": 5, "center": 6
            },
            "auspicious_combos": [
                {"direction": "north", "stars": "77", "desc": "正北七七雙星會聚，旺丁旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "22", "desc": "正南二黑重臨，病符纏身"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.8,
            "note": "七運到山到向，丁財兩得。旺山旺向格局，base_score 30/40。⚠️ MVP 簡化排盤，需專業確認"
        },

        # ---- 乾山巽向 (上山下水) ----
        "乾山巽向": {
            "pan_type": "上山下水",
            "mountain_stars": {
                "northwest": 9, "north": 4, "northeast": 2,
                "west": 1, "center": 8, "east": 5,
                "southwest": 6, "south": 3, "southeast": 7
            },
            "facing_stars": {
                "northwest": 7, "north": 2, "northeast": 9,
                "west": 8, "center": 6, "east": 3,
                "southwest": 4, "south": 1, "southeast": 5
            },
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "18", "desc": "正西一白八白，財丁不聚"},
                {"direction": "center", "stars": "86", "desc": "中宮八白六白，運過即衰"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 8,
            "confidence": 0.8,
            "note": "七運上山下水，損財傷丁。base_score 8/40。⚠️ MVP 簡化排盤，需專業確認"
        },

        # ---- 卯山酉向 (雙星會向) ----
        "卯山酉向": {
            "pan_type": "雙星會向",
            "mountain_stars": {
                "north": 3, "northeast": 8, "east": 1,
                "southeast": 6, "south": 2, "southwest": 7,
                "west": 5, "northwest": 9, "center": 4
            },
            "facing_stars": {
                "north": 3, "northeast": 8, "east": 1,
                "southeast": 6, "south": 2, "southwest": 7,
                "west": 5, "northwest": 9, "center": 4
            },
            "auspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "33", "desc": "正北三碧重臨，口舌是非"}
            ],
            "annual_overlay": {
                2026: {"west": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 14,
            "confidence": 0.7,
            "note": "七運雙星會向，旺財不旺丁。⚠️ MVP 簡化排盤，需專業確認"
        },
    },

    # ============================
    # 八運 (2004-2023)
    # ============================
    "八運": {
        # ---- 丑山未向 (到山到向) ----
        "丑山未向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "north": 7, "northeast": 8, "east": 1,
                "southeast": 2, "south": 3, "southwest": 4,
                "west": 5, "northwest": 6, "center": 9
            },
            "facing_stars": {
                "north": 7, "northeast": 8, "east": 1,
                "southeast": 2, "south": 3, "southwest": 4,
                "west": 5, "northwest": 6, "center": 9
            },
            "auspicious_combos": [
                {"direction": "northeast", "stars": "88", "desc": "東北八八雙星會聚，旺丁旺財"},
                {"direction": "west", "stars": "55", "desc": "正西五六合化，財運亨通"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "33", "desc": "正南三碧重臨，口舌是非"},
                {"direction": "east", "stars": "11", "desc": "正東一白過旺，桃花劫"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.9,
            "note": "八運到山到向，丁財兩得。旺山旺向格局"
        },

        # ---- 乾山巽向 (到山到向) ----
        # 沙田第一城等西北向樓宇
        "乾山巽向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "northwest": 6, "north": 2, "northeast": 4,
                "west": 5, "center": 8, "east": 9,
                "southwest": 3, "south": 7, "southeast": 1
            },
            "facing_stars": {
                "northwest": 8, "north": 6, "northeast": 1,
                "west": 4, "center": 3, "east": 2,
                "southwest": 7, "south": 5, "southeast": 9
            },
            "auspicious_combos": [
                {"direction": "southeast", "stars": "19", "desc": "東南一九成雙，旺財旺丁"},
                {"direction": "northwest", "stars": "68", "desc": "西北六八會合，貴人扶持"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "26", "desc": "正北二黑六白，病符損財"},
                {"direction": "southwest", "stars": "37", "desc": "西南三碧七赤，口舌官非"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.9,
            "note": "八運到山到向，丁財兩得。旺山旺向格局"
        },

        # ---- 亥山巳向 (到山到向) ----
        "亥山巳向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "northwest": 6, "north": 2, "northeast": 4,
                "west": 5, "center": 8, "east": 9,
                "southwest": 3, "south": 7, "southeast": 1
            },
            "facing_stars": {
                "northwest": 8, "north": 6, "northeast": 1,
                "west": 4, "center": 3, "east": 2,
                "southwest": 7, "south": 5, "southeast": 9
            },
            "auspicious_combos": [
                {"direction": "southeast", "stars": "19", "desc": "東南一九成雙，旺財旺丁"},
                {"direction": "northwest", "stars": "68", "desc": "西北六八會合，貴人扶持"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "26", "desc": "正北二黑六白，病符損財"},
                {"direction": "southwest", "stars": "37", "desc": "西南三碧七赤，口舌官非"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.9,
            "note": "八運到山到向，與乾山巽向類似。旺山旺向格局"
        },

        # ---- 卯山酉向 (雙星會向) ----
        # YOHO Town 等東向樓宇
        # ⚠️ MVP 簡化排盤，數據基於公開資料推導，需專業確認
        "卯山酉向": {
            "pan_type": "雙星會向",
            "mountain_stars": {
                "north": 4, "northeast": 9, "east": 2,
                "southeast": 7, "south": 3, "southwest": 8,
                "west": 5, "northwest": 1, "center": 6
            },
            "facing_stars": {
                "north": 4, "northeast": 9, "east": 2,
                "southeast": 7, "south": 3, "southwest": 8,
                "west": 5, "northwest": 1, "center": 6
            },
            "auspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"},
                {"direction": "northeast", "stars": "99", "desc": "東北九紫會聚，喜慶連連"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "44", "desc": "正北四綠重臨，文昌受阻"},
                {"direction": "east", "stars": "22", "desc": "正東二黑重臨，病符纏身"}
            ],
            "annual_overlay": {
                2026: {"west": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 20,
            "confidence": 0.7,
            "note": "八運雙星會向，旺財不旺丁。⚠️ MVP 簡化排盤，需專業確認"
        },

        # ---- 乙山辛向 (雙星會向) ----
        "乙山辛向": {
            "pan_type": "雙星會向",
            "mountain_stars": {
                "north": 4, "northeast": 9, "east": 2,
                "southeast": 7, "south": 3, "southwest": 8,
                "west": 5, "northwest": 1, "center": 6
            },
            "facing_stars": {
                "north": 4, "northeast": 9, "east": 2,
                "southeast": 7, "south": 3, "southwest": 8,
                "west": 5, "northwest": 1, "center": 6
            },
            "auspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西雙星會向，旺財之局"},
                {"direction": "northeast", "stars": "99", "desc": "東北九紫會聚，喜慶連連"}
            ],
            "inauspicious_combos": [
                {"direction": "north", "stars": "44", "desc": "正北四綠重臨，文昌受阻"},
                {"direction": "east", "stars": "22", "desc": "正東二黑重臨，病符纏身"}
            ],
            "annual_overlay": {
                2026: {"west": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 20,
            "confidence": 0.7,
            "note": "八運雙星會向，與卯山酉向類似。⚠️ MVP 簡化排盤，需專業確認"
        },

        # ---- 子山午向 (到山到向) ----
        "子山午向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "north": 8, "northeast": 9, "east": 1,
                "southeast": 2, "south": 3, "southwest": 4,
                "west": 5, "northwest": 6, "center": 7
            },
            "facing_stars": {
                "north": 8, "northeast": 9, "east": 1,
                "southeast": 2, "south": 3, "southwest": 4,
                "west": 5, "northwest": 6, "center": 7
            },
            "auspicious_combos": [
                {"direction": "north", "stars": "88", "desc": "正北八八雙星會聚，旺丁旺財"},
                {"direction": "southwest", "stars": "44", "desc": "西南四綠文昌，學業有成"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "55", "desc": "正西五黃重臨，煞氣當令"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.9,
            "note": "八運到山到向，丁財兩得。旺山旺向格局"
        },
    },

    # ============================
    # 九運 (2024-2043)
    # ============================
    "九運": {
        # ---- 子山午向 (到山到向) ----
        # 太古城等正南樓宇
        "子山午向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "north": 9, "northeast": 7, "east": 2,
                "southeast": 3, "south": 8, "southwest": 1,
                "west": 6, "northwest": 5, "center": 4
            },
            "facing_stars": {
                "north": 1, "northeast": 8, "east": 3,
                "southeast": 4, "south": 9, "southwest": 2,
                "west": 7, "northwest": 6, "center": 5
            },
            "auspicious_combos": [
                {"direction": "south", "stars": "89", "desc": "正南八九成雙，旺財旺丁"},
                {"direction": "north", "stars": "91", "desc": "正北九一連珠，貴人相助"}
            ],
            "inauspicious_combos": [
                {"direction": "northwest", "stars": "56", "desc": "西北五黃六白交加，損財傷丁"},
                {"direction": "center", "stars": "45", "desc": "中宮四綠五黃，官非口舌"}
            ],
            "annual_overlay": {
                2026: {"southwest": "二黑+五黃(大凶)", "north": "一白+九紫(大吉)"}
            },
            "base_score": 30,
            "confidence": 0.9,
            "note": "九運到山到向，丁財兩得。旺山旺向格局"
        },

        # ---- 午山子向 (雙星會向) ----
        "午山子向": {
            "pan_type": "雙星會向",
            "mountain_stars": {
                "northwest": 8, "north": 5, "northeast": 3,
                "west": 1, "center": 6, "east": 4,
                "southwest": 9, "south": 7, "southeast": 2
            },
            "facing_stars": {
                "northwest": 9, "north": 7, "northeast": 5,
                "west": 2, "center": 1, "east": 3,
                "southwest": 8, "south": 6, "southeast": 4
            },
            "auspicious_combos": [
                {"direction": "north", "stars": "57", "desc": "正北五七會合，偏財旺盛"},
                {"direction": "southwest", "stars": "98", "desc": "西南九八成雙，喜慶旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "正南七赤六白，交劍煞臨"},
                {"direction": "center", "stars": "61", "desc": "中宮六白一白，官非損丁"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "north": "一白+九紫(中吉)"}
            },
            "base_score": 20,
            "confidence": 0.9,
            "note": "九運雙星會向，旺財之局"
        },

        # ---- 丁山癸向 (雙星會向) ----
        "丁山癸向": {
            "pan_type": "雙星會向",
            "mountain_stars": {
                "northwest": 8, "north": 5, "northeast": 3,
                "west": 1, "center": 6, "east": 4,
                "southwest": 9, "south": 7, "southeast": 2
            },
            "facing_stars": {
                "northwest": 9, "north": 7, "northeast": 5,
                "west": 2, "center": 1, "east": 3,
                "southwest": 8, "south": 6, "southeast": 4
            },
            "auspicious_combos": [
                {"direction": "north", "stars": "57", "desc": "正北五七會合，偏財旺盛"},
                {"direction": "southwest", "stars": "98", "desc": "西南九八成雙，喜慶旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "正南七赤六白，交劍煞臨"},
                {"direction": "center", "stars": "61", "desc": "中宮六白一白，官非損丁"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "north": "一白+九紫(中吉)"}
            },
            "base_score": 20,
            "confidence": 0.9,
            "note": "九運雙星會向，與午山子向類似"
        },

        # ---- 丑山未向 (上山下水) ----
        # 九運丑山未向格局不同
        "丑山未向": {
            "pan_type": "上山下水",
            "mountain_stars": {
                "north": 3, "northeast": 2, "east": 7,
                "southeast": 6, "south": 5, "southwest": 4,
                "west": 9, "northwest": 8, "center": 1
            },
            "facing_stars": {
                "north": 3, "northeast": 2, "east": 7,
                "southeast": 6, "south": 5, "southwest": 4,
                "west": 9, "northwest": 8, "center": 1
            },
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "99", "desc": "正西九紫重臨，火煞過旺"},
                {"direction": "center", "stars": "11", "desc": "中宮一白過旺，桃花劫臨"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 8,
            "confidence": 0.8,
            "note": "九運上山下水，損財傷丁。⚠️ 建議重新佈局或換天心"
        },

        # ---- 乾山巽向 (上山下水) ----
        "乾山巽向": {
            "pan_type": "上山下水",
            "mountain_stars": {
                "northwest": 3, "north": 7, "northeast": 5,
                "west": 9, "center": 1, "east": 2,
                "southwest": 6, "south": 4, "southeast": 8
            },
            "facing_stars": {
                "northwest": 3, "north": 7, "northeast": 5,
                "west": 9, "center": 1, "east": 2,
                "southwest": 6, "south": 4, "southeast": 8
            },
            "auspicious_combos": [],
            "inauspicious_combos": [
                {"direction": "west", "stars": "99", "desc": "正西九紫重臨，火煞過旺"},
                {"direction": "center", "stars": "11", "desc": "中宮一白過旺，桃花劫臨"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 5,
            "confidence": 0.8,
            "note": "九運上山下水，損財傷丁。⚠️ 建議重新佈局或換天心"
        },

        # ---- 卯山酉向 (到山到向) ----
        # 九運卯山酉向為到山到向
        "卯山酉向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "north": 2, "northeast": 3, "east": 8,
                "southeast": 9, "south": 4, "southwest": 5,
                "west": 1, "northwest": 6, "center": 7
            },
            "facing_stars": {
                "north": 2, "northeast": 3, "east": 8,
                "southeast": 9, "south": 4, "southwest": 5,
                "west": 1, "northwest": 6, "center": 7
            },
            "auspicious_combos": [
                {"direction": "east", "stars": "88", "desc": "正東八八雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "99", "desc": "東南九九連珠，喜慶連連"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "11", "desc": "正西一白過旺，桃花劫臨"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.8,
            "note": "九運到山到向，丁財兩得。旺山旺向格局。⚠️ MVP 簡化排盤，需專業確認"
        },

        # ---- 亥山巳向 (到山到向) ----
        # 與乾山巽向類似，九運為到山到向
        "亥山巳向": {
            "pan_type": "到山到向",
            "mountain_stars": {
                "north": 2, "northeast": 3, "east": 8,
                "southeast": 9, "south": 4, "southwest": 5,
                "west": 1, "northwest": 6, "center": 7
            },
            "facing_stars": {
                "north": 2, "northeast": 3, "east": 8,
                "southeast": 9, "south": 4, "southwest": 5,
                "west": 1, "northwest": 6, "center": 7
            },
            "auspicious_combos": [
                {"direction": "east", "stars": "88", "desc": "正東八八雙星會聚，旺丁旺財"},
                {"direction": "southeast", "stars": "99", "desc": "東南九九連珠，喜慶連連"}
            ],
            "inauspicious_combos": [
                {"direction": "west", "stars": "11", "desc": "正西一白過旺，桃花劫臨"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "center": "一白+九紫(中吉)"}
            },
            "base_score": 30,
            "confidence": 0.8,
            "note": "九運到山到向，與卯山酉向類似。旺山旺向格局。⚠️ MVP 簡化排盤，需專業確認"
        },

        # ---- 乙山辛向 (雙星會向) ----
        # 九運乙山辛向
        "乙山辛向": {
            "pan_type": "雙星會向",
            "mountain_stars": {
                "northwest": 8, "north": 5, "northeast": 3,
                "west": 1, "center": 6, "east": 4,
                "southwest": 9, "south": 7, "southeast": 2
            },
            "facing_stars": {
                "northwest": 9, "north": 7, "northeast": 5,
                "west": 2, "center": 1, "east": 3,
                "southwest": 8, "south": 6, "southeast": 4
            },
            "auspicious_combos": [
                {"direction": "north", "stars": "57", "desc": "正北五七會合，偏財旺盛"},
                {"direction": "southwest", "stars": "98", "desc": "西南九八成雙，喜慶旺財"}
            ],
            "inauspicious_combos": [
                {"direction": "south", "stars": "76", "desc": "正南七赤六白，交劍煞臨"},
                {"direction": "center", "stars": "61", "desc": "中宮六白一白，官非損丁"}
            ],
            "annual_overlay": {
                2026: {"south": "二黑+五黃(大凶)", "north": "一白+九紫(中吉)"}
            },
            "base_score": 20,
            "confidence": 0.8,
            "note": "九運雙星會向，旺財之局。⚠️ MVP 簡化排盤，需專業確認"
        },
    }
}

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
        return "八運"  # 默認
    return "九運"  # 2024年後


# 支持的坐向列表
SUPPORTED_FACINGS = []
for yun_data in FLYING_STAR_TABLE.values():
    SUPPORTED_FACINGS.extend(yun_data.keys())
SUPPORTED_FACINGS = list(set(SUPPORTED_FACINGS))
