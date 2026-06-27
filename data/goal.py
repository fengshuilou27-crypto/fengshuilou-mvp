# 目標匹配查表數據

GOAL_STAR_TABLE = {
    "七運": {
        "財富": {"stars": ["七赤", "八白", "六白"], "score": 7, "rationale": "七赤當令財星，八白六白為輔"},
        "健康": {"stars": ["七赤", "八白"], "score": 7, "rationale": "七赤旺氣，八白輔旺"},
        "事業": {"stars": ["七赤", "一白"], "score": 7, "rationale": "七赤旺財，一白官星"},
        "桃花": {"stars": ["七赤", "一白"], "score": 7, "rationale": "七赤喜慶，一白桃花"},
        "家庭和睦": {"stars": ["七赤", "八白"], "score": 7, "rationale": "七赤當令和氣，八白輔旺"}
    },
    "八運": {
        "財富": {"stars": ["八白", "一白", "六白"], "score": 8, "rationale": "八白當令財星，一白六白為輔"},
        "健康": {"stars": ["八白", "九紫"], "score": 8, "rationale": "八白旺氣，九紫喜慶"},
        "事業": {"stars": ["一白", "八白"], "score": 8, "rationale": "一白官星，八白財星"},
        "桃花": {"stars": ["一白", "九紫"], "score": 8, "rationale": "一白桃花，九紫喜慶"},
        "家庭和睦": {"stars": ["八白", "九紫"], "score": 8, "rationale": "八白旺丁，九紫和氣"}
    },
    "九運": {
        "財富": {"stars": ["九紫", "一白", "六白"], "score": 10, "rationale": "九紫當令財星，一白六白為輔"},
        "健康": {"stars": ["九紫", "八白"], "score": 10, "rationale": "九紫當令，八白輔旺"},
        "事業": {"stars": ["九紫", "一白"], "score": 10, "rationale": "九紫旺財，一白官星"},
        "桃花": {"stars": ["九紫", "一白"], "score": 10, "rationale": "九紫喜慶，一白桃花"},
        "家庭和睦": {"stars": ["九紫", "八白"], "score": 10, "rationale": "九紫當令和氣，八白輔旺"}
    }
}

# 星名 -> 數字對照
STAR_NUMBER_MAP = {
    "一白": 1, "二黑": 2, "三碧": 3, "四綠": 4,
    "五黃": 5, "六白": 6, "七赤": 7, "八白": 8, "九紫": 9
}

# 數字 -> 星名
NUMBER_STAR_MAP = {v: k for k, v in STAR_NUMBER_MAP.items()}
