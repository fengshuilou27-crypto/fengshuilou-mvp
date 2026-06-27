# District scoring for region matching
# Higher scores for prime locations
# Used to differentiate estates with same facing+yun

DISTRICT_SCORES = {
    # Tier 1: Prime central / luxury (9-10)
    "中半山": 10,
    "西半山": 9.5,
    "山頂": 10,
    "南區": 9,
    "九龍塘": 9,
    "何文田": 8.5,
    
    # Tier 2: Well-connected urban (7-8.5)
    "灣仔": 8,
    "跑馬地": 8,
    "大坑": 7.5,
    "銅鑼灣": 7.5,
    "北角": 7,
    "鰂魚涌": 7,
    "西灣河": 7,
    "堅尼地城": 7.5,
    "西營盤": 7.5,
    "上環": 7,
    "九龍站": 8.5,
    "奧運站": 8,
    "啟德": 8,
    "黃竹坑": 7.5,
    
    # Tier 3: Established residential (6-7)
    "紅磡": 6.5,
    "太子": 6.5,
    "旺角": 6,
    "大角咀": 6.5,
    "深水埗": 6,
    "長沙灣": 6,
    "荔枝角": 6,
    "美孚": 6.5,
    "觀塘": 5.5,
    "牛頭角": 5.5,
    "九龍灣": 5.5,
    "調景嶺": 6,
    "坑口": 6,
    "寶琳": 5.5,
    "油塘": 5.5,
    "茶果嶺": 5.5,
    
    # Tier 4: New Towns / Outer (4-6)
    "沙田": 6,
    "大圍": 6,
    "馬鞍山": 5.5,
    "火炭": 5.5,
    "荃灣": 5.5,
    "葵涌": 5,
    "青衣": 5,
    "東涌": 5,
    "將軍澳": 5.5,
    "康城": 5,
    
    # Tier 5: Northwest NT (3.5-5)
    "元朗": 4.5,
    "天水圍": 4,
    "屯門": 4,
    "深井": 4,
    "粉嶺": 4,
    "上水": 4,
    "大埔": 4.5,
    "白石角": 4.5,
    
    # Default
    "": 5,
}


def get_district_score(district: str) -> float:
    """Get region score for a district. Returns 5.0 as default."""
    return DISTRICT_SCORES.get(district, 5.0)
