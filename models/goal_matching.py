from data.goal import GOAL_STAR_TABLE, STAR_NUMBER_MAP, NUMBER_STAR_MAP
from data.flying_star import FLYING_STAR_TABLE, get_yun, FLYING_STAR_COMBO_AUSPICIOUS, FLYING_STAR_COMBO_INAUSPICIOUS


GOAL_SYNONYMS = {
    "財富": ["財富", "財運", "發財", "賺錢", "投資", "招財", "進財", "利市", "錢財", "利潤"],
    "健康": ["健康", "身體", "疾病", "養生", "長壽", "平安"],
    "事業": ["事業", "工作", "升職", "官運", "學業", "考試", "功名", "仕途"],
    "桃花": ["桃花", "感情", "婚姻", "姻緣", "愛情", "緣分", "人緣", "異性緣"],
    "家庭和睦": ["家庭和睦", "家庭", "和睦", "子女", "親情", "和諧", "六親", "家運"]
}

# 目標對應的關鍵星曜組合 (用於動態加分)
GOAL_KEY_COMBOS = {
    "財富": ["88", "89", "98", "99", "78", "87", "68", "86", "18", "81"],
    "健康": ["99", "89", "98", "88", "79", "97", "19", "91"],
    "事業": ["16", "61", "14", "41", "19", "91", "68", "86", "89", "98"],
    "桃花": ["99", "19", "91", "49", "94", "14", "41"],
    "家庭和睦": ["88", "99", "89", "98", "19", "91"]
}

# 目標對應的凶星避諱 (用於動態扣分)
GOAL_AVOID_COMBOS = {
    "財富": ["22", "33", "55", "25", "52", "35", "53", "45", "54"],
    "健康": ["22", "55", "25", "52", "35", "53", "45", "54", "57", "75"],
    "事業": ["33", "55", "35", "53", "36", "63", "45", "54"],
    "桃花": ["33", "55", "25", "52", "35", "53"],
    "家庭和睦": ["33", "55", "25", "52", "35", "53", "45", "54"]
}


def _standardize_goal(goal: str) -> str:
    """標準化目標名稱"""
    for std, synonyms in GOAL_SYNONYMS.items():
        if goal in synonyms:
            return std
    return None


def _analyze_chart_for_goal(chart: dict, goal: str):
    """分析宅運盤中對特定目標有利的星曜組合"""
    mountain_stars = chart.get("mountain_stars", {})
    facing_stars = chart.get("facing_stars", {})
    pan_type = chart.get("pan_type", "其他")
    
    key_combos = GOAL_KEY_COMBOS.get(goal, [])
    avoid_combos = GOAL_AVOID_COMBOS.get(goal, [])
    
    found_combos = []
    avoid_found = []
    
    # 檢查各宮位的山星+向星組合
    directions = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
    for direction in directions:
        m_star = mountain_stars.get(direction, 0)
        f_star = facing_stars.get(direction, 0)
        combo_str = f"{m_star}{f_star}"
        
        if combo_str in key_combos:
            found_combos.append({
                "direction": direction,
                "mountain_star": m_star,
                "facing_star": f_star,
                "combo": combo_str,
                "desc": FLYING_STAR_COMBO_AUSPICIOUS.get(combo_str, "吉星組合")
            })
        
        if combo_str in avoid_combos:
            avoid_found.append({
                "direction": direction,
                "mountain_star": m_star,
                "facing_star": f_star,
                "combo": combo_str,
                "desc": FLYING_STAR_COMBO_INAUSPICIOUS.get(combo_str, "凶星組合")
            })
    
    # 根據宅盤類型調整
    pan_type_bonus = 0
    if goal == "財富":
        if pan_type in ["到山到向", "雙星會向"]:
            pan_type_bonus = 3
        elif pan_type == "上山下水":
            pan_type_bonus = -3
    elif goal == "健康":
        if pan_type in ["到山到向", "雙星會坐"]:
            pan_type_bonus = 3
        elif pan_type == "上山下水":
            pan_type_bonus = -3
    elif goal == "事業":
        if pan_type == "到山到向":
            pan_type_bonus = 3
        elif pan_type == "上山下水":
            pan_type_bonus = -2
    elif goal == "桃花":
        if pan_type in ["到山到向", "雙星會向"]:
            pan_type_bonus = 2
    elif goal == "家庭和睦":
        if pan_type == "到山到向":
            pan_type_bonus = 3
        elif pan_type == "上山下水":
            pan_type_bonus = -3
    
    return {
        "found_combos": found_combos,
        "avoid_found": avoid_found,
        "pan_type_bonus": pan_type_bonus,
        "combo_bonus": len(found_combos) * 2,
        "avoid_penalty": len(avoid_found) * -2
    }


def _analyze_single_goal(building_year: int, building_facing: str, goal: str):
    """單一目標分析內部函數 (v2.2 動態版)"""
    yun = get_yun(building_year)
    
    if yun not in GOAL_STAR_TABLE or building_facing not in FLYING_STAR_TABLE.get(yun, {}):
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 15,
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.5,
            "rationale": f"{yun}的目標匹配數據暫未收錄"
        }
    
    standard_goal = _standardize_goal(goal)
    if standard_goal is None:
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 15,
            "data_source": "三六風水網專業知識庫",
            "confidence": 0.5,
            "rationale": f"目標'{goal}'暫未收錄，MVP支持：財富/健康/事業/桃花/家庭和睦"
        }
    
    goal_info = GOAL_STAR_TABLE[yun][standard_goal]
    target_stars = goal_info["stars"]
    base_score = goal_info["score"]
    rationale = goal_info["rationale"]
    
    chart = FLYING_STAR_TABLE[yun][building_facing]
    mountain_stars = chart["mountain_stars"]
    facing_stars = chart["facing_stars"]
    
    # 查找目標星曜位置 (傳統方法)
    found_stars = []
    for star_name in target_stars:
        star_num = STAR_NUMBER_MAP.get(star_name)
        if star_num:
            for direction, num in mountain_stars.items():
                if num == star_num:
                    found_stars.append({
                        "star": star_name,
                        "number": star_num,
                        "direction": direction,
                        "plate": "山星盤"
                    })
            for direction, num in facing_stars.items():
                if num == star_num:
                    found_stars.append({
                        "star": star_name,
                        "number": star_num,
                        "direction": direction,
                        "plate": "向星盤"
                    })
    
    # v2.2 新增：動態分析星曜組合
    combo_analysis = _analyze_chart_for_goal(chart, standard_goal)
    
    # 計算總分
    bonus = len(found_stars) * 2
    combo_bonus = combo_analysis["combo_bonus"]
    avoid_penalty = combo_analysis["avoid_penalty"]
    pan_type_bonus = combo_analysis["pan_type_bonus"]
    
    total_score = base_score + bonus + combo_bonus + avoid_penalty + pan_type_bonus
    total_score = max(0, min(15, total_score))
    
    # 生成詳細分析文字
    combo_desc = ""
    if combo_analysis["found_combos"]:
        combo_desc = f" 發現{len(combo_analysis['found_combos'])}組有利星曜組合："
        for c in combo_analysis["found_combos"][:3]:
            combo_desc += f"{c['direction']}({c['combo']}-{c['desc']})，"
    
    avoid_desc = ""
    if combo_analysis["avoid_found"]:
        avoid_desc = f" 發現{len(combo_analysis['avoid_found'])}組不利星曜組合，"
    
    pan_desc = ""
    if pan_type_bonus > 0:
        pan_desc = f" 宅盤類型加成+{pan_type_bonus}。"
    elif pan_type_bonus < 0:
        pan_desc = f" 宅盤類型減分{pan_type_bonus}。"
    
    return {
        "status": "success",
        "yun": yun,
        "goal": standard_goal,
        "target_stars": target_stars,
        "found_stars": found_stars,
        "combo_analysis": combo_analysis,
        "score": total_score,
        "max_score": 15,
        "base_score": base_score,
        "bonus": bonus,
        "combo_bonus": combo_bonus,
        "avoid_penalty": avoid_penalty,
        "pan_type_bonus": pan_type_bonus,
        "data_source": "三六風水網專業知識庫",
        "confidence": 0.7,
        "rationale": f"{yun}{standard_goal}目標：吉星為{'、'.join(target_stars)}。{rationale}"
                     + (f"宅運盤中發現{len(found_stars)}處吉星飛臨，額外加{bonus}分。" if found_stars else "")
                     + combo_desc + avoid_desc + pan_desc
    }


def analyze_goal(building_year: int, building_facing: str, goals: list):
    """
    目標匹配模組（多目標版）v2.2
    goals: 目標列表，每項為 {"goal": str, "priority": int}，priority 1=主, 2=次, 3=第三
    權重：主100%、次50%、第三25%
    最終分數 = (主×1 + 次×0.5 + 第三×0.25) / 總權重
    """
    # 向後兼容：如果傳入字符串，包裝成單目標列表
    if isinstance(goals, str):
        goals = [{"goal": goals, "priority": 1}]
    
    if not goals:
        # 默認目標：無目標時使用「財富」並標記
        goals = [{"goal": "財富", "priority": 1}]
        is_default = True
    else:
        is_default = False
    
    # 限制最多3個
    if len(goals) > 3:
        goals = goals[:3]
    
    priority_weights = {1: 1.0, 2: 0.5, 3: 0.25}
    
    results = []
    total_weight = 0
    weighted_score = 0
    all_rationales = []
    all_found_stars = []
    all_combos = []
    
    for item in goals:
        goal_str = item["goal"] if isinstance(item, dict) else item
        priority = item.get("priority", 1) if isinstance(item, dict) else 1
        weight = priority_weights.get(priority, 1.0)
        
        single_result = _analyze_single_goal(building_year, building_facing, goal_str)
        
        if single_result["status"] == "success":
            weighted_score += single_result["score"] * weight
            total_weight += weight
            results.append({
                "goal": single_result["goal"],
                "priority": priority,
                "weight": weight,
                "score": single_result["score"],
                "base_score": single_result["base_score"],
                "bonus": single_result["bonus"],
                "combo_bonus": single_result.get("combo_bonus", 0),
                "avoid_penalty": single_result.get("avoid_penalty", 0),
                "pan_type_bonus": single_result.get("pan_type_bonus", 0),
                "target_stars": single_result["target_stars"],
                "found_stars": single_result["found_stars"],
                "combo_analysis": single_result.get("combo_analysis", {})
            })
            all_rationales.append(f"[{single_result['goal']}](優先級{priority},權重{weight})：{single_result['rationale']}")
            all_found_stars.extend(single_result["found_stars"])
            if single_result.get("combo_analysis"):
                all_combos.extend(single_result["combo_analysis"].get("found_combos", []))
        else:
            results.append({
                "goal": goal_str,
                "priority": priority,
                "weight": weight,
                "score": single_result["score"],
                "status": single_result["status"],
                "rationale": single_result["rationale"]
            })
            all_rationales.append(f"[{goal_str}](優先級{priority})：{single_result['rationale']}")
    
    if total_weight == 0:
        final_score = 0
    else:
        final_score = round(weighted_score / total_weight, 1)
    
    final_score = max(0, min(15, final_score))
    
    # 去重複的found_stars
    seen = set()
    unique_stars = []
    for star in all_found_stars:
        key = (star["star"], star["direction"], star["plate"])
        if key not in seen:
            seen.add(key)
            unique_stars.append(star)
    
    warning = ""
    if len(goals) >= 3:
        warning = " 注意：選擇過多目標會稀釋分析精度，建議選取最關鍵的1-3項。"
    
    default_notice = "（系統已默認使用「財富」作為目標，您可返回修改）" if is_default else ""
    
    return {
        "status": "success",
        "goals": results,
        "score": final_score,
        "max_score": 15,
        "total_weight": total_weight,
        "data_source": "三六風水網專業知識庫",
        "confidence": 0.7,
        "rationale": f"多目標加權分析：共選{len(goals)}項目標，總權重{total_weight}。{' '.join(all_rationales)}"
                     + (f" 綜合吉星發現{len(unique_stars)}處，有利組合{len(all_combos)}處。" if unique_stars or all_combos else "")
                     + warning
                     + default_notice
                     + " 基於三六風水網專業知識庫計算，僅供參考，具體判斷建議諮詢專業師傅。",
        "is_default": is_default
    }
