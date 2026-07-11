from data.bagua import (
    ZHAIGUA_TABLE, GUA_WUXING, MING_GUA_MAP,
    EAST_FOUR_GUA, WEST_FOUR_GUA,
    BAGUA_DIRECTION_TABLE, DIRECTION_MAP, DIRECTION_REVERSE,
    AUSPICIOUS_WEIGHT, GOAL_DIRECTION_BONUS, ROOM_IMPORTANCE, ROOM_DIRECTION_PREFERENCE
)


def calc_ming_gua(birth_year: int, gender: str) -> int:
    """
    命卦計算公式（100年算法）
    
    ⚠️ v3.2 重要說明：
    此函數使用公曆年份計算。傳統風水命理應以農曆立春為分界，
    約15%用戶（1-2月出生）的農曆年可能與公曆年不同。
    例如：1991年1月15日公曆 = 庚午年農曆（非辛未年）。
    未來版本應增加農曆年轉換功能以提高準確度。
    
    男命：(100 - 出生年後兩位) ÷ 9，取餘數（整除取9）
    女命：(出生年後兩位 - 4) ÷ 9，取餘數（整除取9）
    餘5：男命寄艮(2)，女命寄坤(8)
    命卦數：1坎 2坤 3震 4巽 6乾 7兌 8艮 9離
    """
    year_last_two = int(str(birth_year)[-2:])
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


def _get_direction_score(gua: str, direction: str, goal: str = ""):
    """
    計算某個方位對於某個命卦的吉凶得分
    direction: 方位中文 (東, 南, 西, 北, 東南, 東北, 西南, 西北)
    """
    gua_directions = BAGUA_DIRECTION_TABLE.get(gua, {})
    
    # 找到這個方位對應的吉凶名稱
    direction_fate = None
    for fate_name, fate_dir in gua_directions.items():
        if fate_dir == direction:
            direction_fate = fate_name
            break
    
    if not direction_fate:
        return {"score": 0, "fate": "未知", "weight": 0}
    
    # 基礎分數
    base_score = AUSPICIOUS_WEIGHT.get(direction_fate, 0)
    
    # 目標加成
    goal_bonus = 0
    if goal and goal in GOAL_DIRECTION_BONUS:
        goal_bonus = GOAL_DIRECTION_BONUS[goal].get(direction_fate, 0)
    
    total_score = base_score + goal_bonus
    
    return {
        "score": total_score,
        "fate": direction_fate,
        "weight": AUSPICIOUS_WEIGHT.get(direction_fate, 0),
        "goal_bonus": goal_bonus,
        "is_auspicious": direction_fate in ["生氣", "延年", "天醫", "伏位"],
        "is_inauspicious": direction_fate in ["五鬼", "絕命", "六煞", "禍害"]
    }


def _analyze_room_positions(gua: str, room_positions: dict, goal: str = ""):
    """
    分析房間位置的吉凶
    room_positions: {"大門": "南", "臥室": "東北", "客廳": "東", ...}
    """
    room_scores = {}
    total_score = 0
    total_weight = 0
    suggestions = []
    
    for room, direction in room_positions.items():
        if not direction:
            continue
        
        importance = ROOM_IMPORTANCE.get(room, 1.0)
        dir_score = _get_direction_score(gua, direction, goal)
        
        weighted_score = dir_score["score"] * importance
        total_score += weighted_score
        total_weight += importance
        
        room_scores[room] = {
            "direction": direction,
            "fate": dir_score["fate"],
            "score": dir_score["score"],
            "weighted_score": round(weighted_score, 2),
            "is_auspicious": dir_score["is_auspicious"],
            "is_inauspicious": dir_score["is_inauspicious"]
        }
        
        # 生成建議
        if room in ROOM_DIRECTION_PREFERENCE:
            preferred = ROOM_DIRECTION_PREFERENCE[room]
            if dir_score["fate"] not in preferred and dir_score["is_inauspicious"]:
                if room == "廁所" and dir_score["fate"] in ["絕命", "五鬼"]:
                    # 廁所在凶方是合理的 (以穢制穢)
                    suggestions.append(f"{room}在{direction}({dir_score['fate']})，以穢制穢，尚合理")
                else:
                    better = "、".join([f"{d}({BAGUA_DIRECTION_TABLE.get(gua, {}).get(d, '')})" for d in preferred[:3]])
                    suggestions.append(f"{room}在{direction}({dir_score['fate']})，建議移至{better}")
    
    # 標準化分數 (0-10分)
    normalized_score = 0
    if total_weight > 0:
        # 理論最大: 所有房間都在生氣位 (4分 * 權重)
        # 理論最小: 所有房間都在絕命位 (-4分 * 權重)
        max_possible = sum(4 * ROOM_IMPORTANCE.get(r, 1) for r in room_positions if room_positions[r])
        min_possible = sum(-4 * ROOM_IMPORTANCE.get(r, 1) for r in room_positions if room_positions[r])
        
        if max_possible > min_possible:
            normalized_score = ((total_score - min_possible) / (max_possible - min_possible)) * 10
            normalized_score = round(max(0, min(10, normalized_score)), 2)
    
    return {
        "room_scores": room_scores,
        "total_score": round(total_score, 2),
        "normalized_score": normalized_score,
        "suggestions": suggestions
    }


def _analyze_single_bagua(birth_year: int, gender: str, building_facing: str, 
                           room_positions: dict = None, goal: str = "", person_label: str = ""):
    """單人八宅分析內部函數 (v2.2 擴展版)"""
    gua_num = calc_ming_gua(birth_year, gender)
    ming_gua = MING_GUA_MAP.get(gua_num, "未知")
    
    zhai_gua = ZHAIGUA_TABLE.get(building_facing)
    if not zhai_gua:
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 10,
            "person_label": person_label,
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.5,
            "rationale": f"MVP未收錄該坐向'{building_facing}'的宅卦信息"
        }
    
    is_ming_east = ming_gua in EAST_FOUR_GUA
    is_zhai_east = zhai_gua in EAST_FOUR_GUA
    
    score = 0
    mismatch_detected = False
    mismatch_desc = ""
    
    if is_ming_east == is_zhai_east:
        score += 4  # 宅命相配基礎分 (最高4分)
    else:
        mismatch_detected = True
        mismatch_desc = f"命卦{ming_gua}（{'東四命' if is_ming_east else '西四命'}）與宅卦{zhai_gua}（{'東四宅' if is_zhai_east else '西四宅'}）不相配"
    
    # 八宅吉凶方位
    gua_directions = BAGUA_DIRECTION_TABLE.get(ming_gua, {})
    auspicious = {k: v for k, v in gua_directions.items() if k in ["生氣", "延年", "天醫", "伏位"]}
    inauspicious = {k: v for k, v in gua_directions.items() if k in ["五鬼", "絕命", "六煞", "禍害"]}
    
    # 九宮房間分析 (v2.2新增)
    room_analysis = None
    if room_positions:
        room_analysis = _analyze_room_positions(ming_gua, room_positions, goal)
        score += room_analysis["normalized_score"] * 0.6  # 九宮分析佔60%權重
    else:
        # 無房間位置時，給宅命匹配的基礎分
        score += 6  # 默認中間分
    
    score = min(10, max(0, round(score, 2)))
    
    # 目標導向的吉位推薦
    goal_recommendations = []
    if goal and goal in GOAL_DIRECTION_BONUS:
        for direction_name, bonus in GOAL_DIRECTION_BONUS[goal].items():
            if direction_name in auspicious and bonus > 0:
                goal_recommendations.append({
                    "direction_name": direction_name,
                    "direction": auspicious[direction_name],
                    "purpose": goal,
                    "bonus": bonus
                })
        goal_recommendations.sort(key=lambda x: x["bonus"], reverse=True)
    
    result = {
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
        "data_source": "三六風水網專業知識庫",
        "confidence": 0.75,
        "room_analysis": room_analysis,
        "goal_recommendations": goal_recommendations[:3] if goal_recommendations else [],
        "rationale": f"{person_label}命卦為{ming_gua}（{'東四命' if is_ming_east else '西四命'}），宅卦為{zhai_gua}（{'東四宅' if is_zhai_east else '西四宅'}）。"
                     + (f"{mismatch_desc}。" if mismatch_detected else "宅命同類，基礎匹配。")
                     + (f" 九宮房間分析得分{room_analysis['normalized_score']}/10。" if room_analysis else "")
                     + (f" 目標'{goal}'的吉位推薦：{', '.join([r['direction_name'] + '(' + r['direction'] + ')' for r in goal_recommendations[:3]])}。" if goal_recommendations else "")
    }
    
    return result


def analyze_bagua(birth_date: str, gender: str, building_facing: str, 
                  room_positions: dict = None, goal: str = ""):
    """
    八宅匹配模組（單人版）v2.2
    計算命卦、宅卦，判斷宅命匹配度，並分析九宮房間吉凶
    """
    try:
        birth_year = int(birth_date.split("-")[0])
    except (ValueError, IndexError):
        return {
            "status": "error",
            "score": 0,
            "max_score": 10,
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.3,
            "rationale": "出生日期格式错误，无法计算命卦"
        }
    
    return _analyze_single_bagua(birth_year, gender, building_facing, room_positions, goal, "")


def analyze_bagua_dual(person_a_birth_date: str, person_a_gender: str,
                       person_b_birth_date: str, person_b_gender: str,
                       building_facing: str, room_positions: dict = None, 
                       goal: str = "", weight_a: float = 0.5, weight_b: float = 0.5):
    """
    八宅匹配模組（雙人版）v2.2
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
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.3,
            "rationale": "出生日期格式错误，无法计算命卦"
        }
    
    result_a = _analyze_single_bagua(birth_year_a, person_a_gender, building_facing, room_positions, goal, "A")
    result_b = _analyze_single_bagua(birth_year_b, person_b_gender, building_facing, room_positions, goal, "B")
    
    if result_a["status"] == "unsupported" or result_b["status"] == "unsupported":
        return result_a if result_a["status"] == "unsupported" else result_b
    
    # 加權合併分數
    score_a = result_a.get("score", 0)
    score_b = result_b.get("score", 0)
    merged_score = round(score_a * weight_a + score_b * weight_b, 1)
    merged_score = min(10, max(0, merged_score))
    
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
    
    # 九宮分析對比
    room_comparison = {}
    if room_positions and result_a.get("room_analysis") and result_b.get("room_analysis"):
        for room in room_positions:
            a_room = result_a["room_analysis"]["room_scores"].get(room, {})
            b_room = result_b["room_analysis"]["room_scores"].get(room, {})
            if a_room and b_room:
                room_comparison[room] = {
                    "a_fate": a_room.get("fate", ""),
                    "b_fate": b_room.get("fate", ""),
                    "a_score": a_room.get("score", 0),
                    "b_score": b_room.get("score", 0),
                    "direction": room_positions[room]
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
    if room_comparison:
        rationale += f" 已分析{len(room_comparison)}個房間位置的九宮吉凶。"
    rationale += " 基於三六風水網專業知識庫計算，僅供參考，具體判斷建議諮詢專業師傅。"
    
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
        "room_comparison": room_comparison,
        "mismatch_detected": result_a.get("mismatch_detected", False) or result_b.get("mismatch_detected", False),
        "data_source": "三六風水網專業知識庫",
        "confidence": round((result_a.get("confidence", 0.75) + result_b.get("confidence", 0.75)) / 2, 2),
        "rationale": rationale
    }
