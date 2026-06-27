from data.bagua import (
    ZHAIGUA_TABLE, GUA_WUXING, MING_GUA_MAP,
    EAST_FOUR_GUA, WEST_FOUR_GUA,
    BAGUA_DIRECTION_TABLE, DIRECTION_MAP, DIRECTION_REVERSE
)


def calc_ming_gua(birth_year: int, gender: str) -> int:
    """
    命卦計算公式（100年算法）
    男命：(100 - 出生年後兩位) ÷ 9，取餘數（整除取9）
    女命：(出生年後兩位 - 4) ÷ 9，取餘數（整除取9）
    餘5：男命寄艮(2)，女命寄坤(8)
    命卦數：1坎 2坤 3震 4巽 6乾 7兌 8艮 9離
    """
    year_last_two = int(str(birth_year)[-2:])
    
    if gender == "男":
        gua_num = (100 - year_last_two) % 9
    else:
        gua_num = (year_last_two - 4) % 9
    
    if gua_num == 0:
        gua_num = 9
    if gua_num == 5:
        gua_num = 8 if gender == "男" else 2
    
    return gua_num


def _analyze_single_bagua(birth_year: int, gender: str, building_facing: str, person_label: str = ""):
    """單人八宅分析內部函數"""
    gua_num = calc_ming_gua(birth_year, gender)
    ming_gua = MING_GUA_MAP.get(gua_num, "未知")
    
    zhai_gua = ZHAIGUA_TABLE.get(building_facing)
    if not zhai_gua:
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 10,
            "person_label": person_label,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.5,
            "rationale": f"MVP未收录该坐向'{building_facing}'的宅卦信息"
        }
    
    is_ming_east = ming_gua in EAST_FOUR_GUA
    is_zhai_east = zhai_gua in EAST_FOUR_GUA
    
    score = 0
    mismatch_detected = False
    mismatch_desc = ""
    
    if is_ming_east == is_zhai_east:
        score += 10
    else:
        mismatch_detected = True
        mismatch_desc = f"命卦{ming_gua}（{'東四命' if is_ming_east else '西四命'}）與宅卦{zhai_gua}（{'東四宅' if is_zhai_east else '西四宅'}）不相配"
    
    score = min(10, score)
    
    # 八宅吉凶方位
    gua_directions = BAGUA_DIRECTION_TABLE.get(ming_gua, {})
    auspicious = {k: v for k, v in gua_directions.items() if k in ["生氣", "延年", "天醫", "伏位"]}
    inauspicious = {k: v for k, v in gua_directions.items() if k in ["五鬼", "絕命", "六煞", "禍害"]}
    
    return {
        "status": "success",
        "person_label": person_label,
        "ming_gua_num": gua_num,
        "ming_gua": ming_gua,
        "ming_gua_wuxing": GUA_WUXING.get(ming_gua, "未知"),
        "ming_type": "東四命" if is_ming_east else "西四命",
        "zhai_gua": zhai_gua,
        "zhai_wuxing": GUA_WUXING.get(zhai_gua, "未知"),
        "zhai_type": "東四宅" if is_zhai_east else "西四宅",
        "mismatch_detected": mismatch_detected,
        "mismatch_desc": mismatch_desc,
        "auspicious_directions": auspicious,
        "inauspicious_directions": inauspicious,
        "score": score,
        "max_score": 10,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.6,
        "rationale": f"{person_label}命卦為{ming_gua}（{'東四命' if is_ming_east else '西四命'}），宅卦為{zhai_gua}（{'東四宅' if is_zhai_east else '西四宅'}）。"
                     + (f"{mismatch_desc}，可按命卦重新定位吉位。" if mismatch_detected else "宅命同類（東四/西四），基礎計算結果。")
    }


def analyze_bagua(birth_date: str, gender: str, building_facing: str):
    """
    八宅匹配模組（單人版）
    計算命卦、宅卦，判斷宅命匹配度
    """
    try:
        birth_year = int(birth_date.split("-")[0])
    except (ValueError, IndexError):
        return {
            "status": "error",
            "score": 0,
            "max_score": 10,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.3,
            "rationale": "出生日期格式错误，无法计算命卦"
        }
    
    return _analyze_single_bagua(birth_year, gender, building_facing, "")


def analyze_bagua_dual(person_a_birth_date: str, person_a_gender: str,
                       person_b_birth_date: str, person_b_gender: str,
                       building_facing: str, weight_a: float = 0.5, weight_b: float = 0.5):
    """
    八宅匹配模組（雙人版）
    分別計算兩人命卦、宅卦，加權合併，並列顯示吉位凶位對照表
    """
    try:
        birth_year_a = int(person_a_birth_date.split("-")[0])
        birth_year_b = int(person_b_birth_date.split("-")[0])
    except (ValueError, IndexError):
        return {
            "status": "error",
            "score": 0,
            "max_score": 10,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.3,
            "rationale": "出生日期格式错误，无法计算命卦"
        }
    
    result_a = _analyze_single_bagua(birth_year_a, person_a_gender, building_facing, "A")
    result_b = _analyze_single_bagua(birth_year_b, person_b_gender, building_facing, "B")
    
    if result_a["status"] == "unsupported" or result_b["status"] == "unsupported":
        return result_a if result_a["status"] == "unsupported" else result_b
    
    # 加權合併分數
    score_a = result_a.get("score", 0)
    score_b = result_b.get("score", 0)
    merged_score = round(score_a * weight_a + score_b * weight_b, 1)
    merged_score = min(10, merged_score)
    
    # 檢查吉位/凶位衝突
    conflicts = []
    a_auspicious = result_a.get("auspicious_directions", {})
    a_inauspicious = result_a.get("inauspicious_directions", {})
    b_auspicious = result_b.get("auspicious_directions", {})
    b_inauspicious = result_b.get("inauspicious_directions", {})
    
    # A的吉位是否為B的凶位
    for direction_name, dir_value in a_auspicious.items():
        for b_bad_name, b_bad_value in b_inauspicious.items():
            if dir_value == b_bad_value:
                conflicts.append({
                    "direction": dir_value,
                    "a_status": f"吉（{direction_name}）",
                    "b_status": f"凶（{b_bad_name}）",
                    "note": "需調和"
                })
    
    # B的吉位是否為A的凶位
    for direction_name, dir_value in b_auspicious.items():
        for a_bad_name, a_bad_value in a_inauspicious.items():
            if dir_value == a_bad_value and not any(c["direction"] == dir_value for c in conflicts):
                conflicts.append({
                    "direction": dir_value,
                    "a_status": f"凶（{a_bad_name}）",
                    "b_status": f"吉（{direction_name}）",
                    "note": "需調和"
                })
    
    # 生成對照表
    comparison_table = {
        "person_a": {
            "ming_gua": result_a["ming_gua"],
            "ming_type": result_a["ming_type"],
            "auspicious": a_auspicious,
            "inauspicious": a_inauspicious
        },
        "person_b": {
            "ming_gua": result_b["ming_gua"],
            "ming_type": result_b["ming_type"],
            "auspicious": b_auspicious,
            "inauspicious": b_inauspicious
        },
        "conflicts": conflicts
    }
    
    rationale = (
        f"雙人八宅分析：A命卦{result_a['ming_gua']}（{result_a['ming_type']}），"
        f"B命卦{result_b['ming_gua']}（{result_b['ming_type']}），"
        f"宅卦{result_a['zhai_gua']}（{result_a['zhai_type']}）。"
        f"A得分{score_a}分，B得分{score_b}分，"
        f"加權({weight_a:.0%}/{weight_b:.0%})合併後{merged_score}分。"
    )
    if conflicts:
        rationale += f" 發現{len(conflicts)}處方位衝突：{', '.join([c['direction'] for c in conflicts])}。"
    else:
        rationale += " 無方位衝突。"
    rationale += " 基於公開資料計算，僅供參考，具體判斷建議諮詢專業師傅。"
    
    return {
        "status": "success",
        "is_dual": True,
        "weight_a": weight_a,
        "weight_b": weight_b,
        "person_a": {k: v for k, v in result_a.items() if k != "rationale"},
        "person_b": {k: v for k, v in result_b.items() if k != "rationale"},
        "merged_score": merged_score,
        "score": merged_score,
        "max_score": 10,
        "comparison_table": comparison_table,
        "mismatch_detected": result_a.get("mismatch_detected", False) or result_b.get("mismatch_detected", False),
        "data_source": "互联网公开资料碎片",
        "confidence": round((result_a.get("confidence", 0.6) + result_b.get("confidence", 0.6)) / 2, 2),
        "rationale": rationale
    }
