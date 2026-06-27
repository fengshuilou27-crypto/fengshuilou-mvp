from data.goal import GOAL_STAR_TABLE, STAR_NUMBER_MAP, NUMBER_STAR_MAP
from data.flying_star import FLYING_STAR_TABLE, get_yun


GOAL_SYNONYMS = {
    "財富": ["財富", "財運", "發財", "賺錢", "投資", "招財", "進財", "利市", "錢財", "利潤"],
    "健康": ["健康", "身體", "疾病", "養生", "長壽", "平安"],
    "事業": ["事業", "工作", "升職", "官運", "學業", "考試", "功名", "仕途"],
    "桃花": ["桃花", "感情", "婚姻", "姻緣", "愛情", "緣分", "人緣", "異性緣"],
    "家庭和睦": ["家庭和睦", "家庭", "和睦", "子女", "親情", "和諧", "六親", "家運"]
}


def _standardize_goal(goal: str) -> str:
    """標準化目標名稱"""
    for std, synonyms in GOAL_SYNONYMS.items():
        if goal in synonyms:
            return std
    return None


def _analyze_single_goal(building_year: int, building_facing: str, goal: str):
    """單一目標分析內部函數"""
    yun = get_yun(building_year)
    
    if yun not in GOAL_STAR_TABLE or building_facing not in FLYING_STAR_TABLE.get(yun, {}):
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 15,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.5,
            "rationale": f"{yun}的目標匹配數據暫未收錄"
        }
    
    standard_goal = _standardize_goal(goal)
    if standard_goal is None:
        return {
            "status": "unsupported",
            "score": 0,
            "max_score": 15,
            "data_source": "互联网公开资料碎片",
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
    
    bonus = len(found_stars) * 2
    total_score = base_score + bonus
    total_score = min(15, total_score)
    
    return {
        "status": "success",
        "yun": yun,
        "goal": standard_goal,
        "target_stars": target_stars,
        "found_stars": found_stars,
        "score": total_score,
        "max_score": 15,
        "base_score": base_score,
        "bonus": bonus,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.55,
        "rationale": f"{yun}{standard_goal}目標：吉星為{'、'.join(target_stars)}。{rationale}"
                     + (f"宅運盤中發現{len(found_stars)}處吉星飛臨，額外加{bonus}分。" if found_stars else "")
    }


def analyze_goal(building_year: int, building_facing: str, goals: list):
    """
    目標匹配模組（多目標版）
    goals: 目標列表，每項為 {"goal": str, "priority": int}，priority 1=主, 2=次, 3=第三
    權重：主100%、次50%、第三25%
    最終分數 = (主×1 + 次×0.5 + 第三×0.25) / 總權重
    """
    # 向後兼容：如果傳入字符串，包裝成單目標列表
    if isinstance(goals, str):
        goals = [{"goal": goals, "priority": 1}]
    
    if not goals:
        return {
            "status": "error",
            "score": 0,
            "max_score": 15,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.3,
            "rationale": "未選擇任何目標"
        }
    
    # 限制最多3個
    if len(goals) > 3:
        goals = goals[:3]
    
    priority_weights = {1: 1.0, 2: 0.5, 3: 0.25}
    
    results = []
    total_weight = 0
    weighted_score = 0
    all_rationales = []
    all_found_stars = []
    
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
                "target_stars": single_result["target_stars"],
                "found_stars": single_result["found_stars"]
            })
            all_rationales.append(f"[{single_result['goal']}](優先級{priority},權重{weight})：{single_result['rationale']}")
            all_found_stars.extend(single_result["found_stars"])
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
    
    return {
        "status": "success",
        "goals": results,
        "score": final_score,
        "max_score": 15,
        "total_weight": total_weight,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.55,
        "rationale": f"多目標加權分析：共選{len(goals)}項目標，總權重{total_weight}。{' '.join(all_rationales)}"
                     + (f" 綜合吉星發現{len(unique_stars)}處。" if unique_stars else "")
                     + warning
                     + " 基於公開資料查表計算，僅供參考，具體判斷建議諮詢專業師傅。"
    }
