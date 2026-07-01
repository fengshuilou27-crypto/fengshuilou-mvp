from data.district_scores import get_district_score
from data.flying_star import analyze_multi_yun
from data.gis_analysis import analyze_gis_feng_shui


def _get_district_tier(score: float) -> str:
    """根據地段評分返回地段等級"""
    if score >= 8:
        return "一線地段"
    elif score >= 6:
        return "二線地段"
    elif score >= 4:
        return "三線地段"
    else:
        return "一般地段"



def aggregate_match_result(
    flying_star_result: dict,
    zero_main_god_result: dict,
    sha_result: dict,
    bazi_result: dict,
    bagua_result: dict,
    goal_result: dict,
    district: str = None,
    building_year: int = None,
    eval_year: int = 2026,
    property_features: dict = None,
    floor_number: int = None,
    building_facing: str = None,
    estate_name: str = None
):
    """
    聚合匹配結果（v2.5 修復版）
    加權計算總分，生成結構化報告
    
    100分制結構（v2.5 修復後）：
    - 飛星 20 + 八字 18 + 八宅 13 + 零正神 8 + 目標 13 + 物業特徵 10 + GIS 8 + 煞氣防禦 7 + 多運交叉±5 = 100
    
    v2.5 修復內容：
    1. 煞氣從「直接扣分」改為「煞氣防禦分」（0-7分正向維度），避免負分截斷
    2. 樓齡從「直接扣分」改為「建築健康分」（融入物業特徵維度），避免老樓強制低分
    3. 區位（地段溢價）從風水評分中剝離，改為獨立的「投資屬性」字段
    4. 多運交叉從「加分/扣分」改為「元運適配係數」（0.9-1.1），平滑過渡
    """
    # 提取分數
    flying_score = flying_star_result.get("score", 0)
    zmg_score = zero_main_god_result.get("score", 0)
    sha_score = sha_result.get("score", 0)  # 現在為 0~7 的煞氣防禦分
    bazi_score = bazi_result.get("score", 0)
    bagua_score = bagua_result.get("score", 0)
    goal_score = goal_result.get("score", 0)
    
    # === 區位評分（地段溢價）—— 從風水評分中剝離，改為獨立投資屬性 ===
    region_score = get_district_score(district) if district else 5.0
    
    # 各模組正規化到100分制目標權重
    # v2.5: 飛星20 + 八字18 + 八宅13 + 零正神8 + 目標13 + 物業特徵10 + GIS8 + 煞氣防禦7 = 97
    # 多運交叉適配係數：0.9~1.1，乘以總分後實際調整範圍 ±~5分
    flying_norm = (flying_score / 40) * 20   # 飛星 20 分
    zmg_norm = (zmg_score / 10) * 8          # 零正神 8 分
    bazi_norm = (bazi_score / 20) * 18       # 八字 18 分
    bagua_norm = (bagua_score / 10) * 13     # 八宅 13 分
    goal_norm = (goal_score / 15) * 13       # 目標 13 分
    
    # === 煞氣防禦分（v2.5：從扣分改為正向維度）===
    # sha_score 原為負值（扣分），現已統一為 0~7 的防禦分
    # 0 = 無防禦（多項嚴重煞氣），7 = 完美防禦（無煞氣）
    sha_defense = max(0, min(7, sha_score))
    sha_norm = (sha_defense / 7) * 7  # 煞氣防禦 7 分
    
    # === 多運交叉分析（v2.5：從加減分改為適配係數）===
    multi_yun_adjust = 0.0
    multi_yun_rationale = ""
    multi_yun_needs_renovation = False
    yun_adaptation_factor = 1.0  # 0.9 ~ 1.1
    
    if building_year and building_facing:
        try:
            multi_yun_result = analyze_multi_yun(building_year, eval_year, building_facing)
            multi_yun_adjust = multi_yun_result.get("score_adjust", 0)
            multi_yun_rationale = multi_yun_result.get("rationale", "")
            multi_yun_needs_renovation = multi_yun_result.get("needs_renovation", False)
            # 將 ±5 分調整轉換為 0.9~1.1 的適配係數
            yun_adaptation_factor = 1.0 + (multi_yun_adjust / 50)  # ±5分 → ±0.1係數
            yun_adaptation_factor = max(0.85, min(1.15, yun_adaptation_factor))
        except Exception:
            yun_adaptation_factor = 1.0
    
    # === GIS 地理風水分析 ===
    gis_result = {"score": 0, "max_score": 0, "status": "skipped"}
    gis_norm = 0.0
    if estate_name or district:
        try:
            # 優先使用 estate_name，否則嘗試用 district 作為 fallback
            lookup_name = estate_name if estate_name else district
            gis_result = analyze_gis_feng_shui(
                estate_name=estate_name,
                facing=building_facing
            )
            # GIS 模組原始滿分20分，目標權重8分
            if gis_result.get("status") == "success":
                gis_norm = (gis_result.get("score", 0) / 20) * 8
            else:
                gis_norm = 0.0
        except Exception:
            gis_norm = 0.0
    
    # === 物業特徵加分（v2.5：樓齡融入物業特徵維度）===
    property_bonus = 0.0
    property_bonus_details = {}
    if property_features:
        # 海景/山景
        if property_features.get("has_sea_view"):
            property_bonus += 0.5
            property_bonus_details["海景"] = 0.5
        if property_features.get("has_mountain_view"):
            property_bonus += 0.5
            property_bonus_details["山景"] = 0.5
        
        # 裝修狀態
        decoration = property_features.get("decoration", "")
        deco_score = 0.0
        if "豪華" in decoration or "靚裝" in decoration:
            deco_score = 1.5
        elif "雅緻" in decoration or "精裝" in decoration:
            deco_score = 1.0
        elif "基本" in decoration:
            deco_score = 0.5
        if deco_score > 0:
            property_bonus += deco_score
            property_bonus_details["裝修"] = deco_score
        
        # 交通便利度 (1-5分)
        transport_rating = property_features.get("transport_rating", 0)
        if transport_rating and isinstance(transport_rating, (int, float)) and transport_rating > 0:
            transport_score = min(transport_rating * 0.4, 2.0)
            property_bonus += transport_score
            property_bonus_details["交通"] = round(transport_score, 1)
        
        # 配套設施 (0-100分)
        amenities_score = property_features.get("amenities_score", 0)
        if amenities_score and isinstance(amenities_score, (int, float)) and amenities_score > 0:
            amenities_bonus = min(amenities_score / 20 * 0.5, 2.0)
            property_bonus += amenities_bonus
            property_bonus_details["配套"] = round(amenities_bonus, 1)
    
    # === 建築健康分（v2.5：樓齡從「懲罰」改為「健康分」融入物業特徵）===
    # 新樓（<10年）= 4分，中年（10-30年）= 3分，老樓（30-50年）= 2分，極老樓（>50年）= 1分
    building_health = 0.0
    if building_year and eval_year:
        age = eval_year - building_year
        if age > 0:
            if age <= 10:
                building_health = 4.0
            elif age <= 30:
                building_health = 3.0
            elif age <= 50:
                building_health = 2.0
            else:
                building_health = 1.0
            property_bonus_details["樓齡健康"] = building_health
    
    property_bonus += building_health
    # 物業特徵總分上限 10 分（v2.5 從 5 提升到 10）
    property_bonus = min(property_bonus, 10.0)
    property_norm = (property_bonus / 10) * 10  # 物業特徵 10 分
    
    # === 樓層精確度微調（避免尾數相同導致分數相同）===
    floor_tie_breaker = 0.0
    if floor_number and isinstance(floor_number, int) and floor_number > 0:
        floor_tie_breaker = min(floor_number * 0.01, 0.3)  # 每層+0.01，最多+0.3
    
    # 計算總分（v2.5：正向維度合計 20+18+13+8+13+10+8+7 = 97，再乘元運適配係數）
    base_total = (
        flying_norm + zmg_norm + bazi_norm + bagua_norm + goal_norm + 
        property_norm + gis_norm + sha_norm
    )
    # 元運適配係數：0.85~1.15，使總分在 82~112 之間，截斷到 0-100
    total_score = base_total * yun_adaptation_factor + floor_tie_breaker
    
    # v2.5：不再截斷到 0-100（使用 round），如果超出範圍則提示
    normalized_score = round(total_score, 1)
    if normalized_score > 100:
        normalized_score = 100.0
    elif normalized_score < 0:
        normalized_score = 0.0
    
    # 評級（基礎版：只做分數區間標註，不做入住建議判斷）
    if normalized_score >= 85:
        rating = "★★★★★ 高分區間（需專業師傅確認）"
    elif normalized_score >= 70:
        rating = "★★★★☆ 中高分區間（需專業師傅確認）"
    elif normalized_score >= 60:
        rating = "★★★☆☆ 中分區間（需專業師傅確認）"
    elif normalized_score >= 45:
        rating = "★★☆☆☆ 中低分區間（需專業師傅確認）"
    elif normalized_score >= 30:
        rating = "★☆☆☆☆ 低分區間（需專業師傅確認）"
    else:
        rating = "☆☆☆☆☆ 極低分區間（需專業師傅確認）"
    
    # 風險標記（v2.5：sha_score 現在為 0~7 的防禦分，<3 表示風險較高）
    flying_yun = flying_star_result.get("yun", "")
    flying_current_yun = flying_star_result.get("current_yun", flying_yun)
    yun_converted = flying_yun != flying_current_yun
    
    # 獲取原始煞氣扣分（用於風險標記）
    raw_sha_penalty = sha_result.get("raw_penalty", 0)  # 負值
    
    flags = {
        "severe_penalty_applied": raw_sha_penalty <= -12,
        "sha_detected": raw_sha_penalty < 0,
        "remedies_required": raw_sha_penalty < 0,
        "yun_conversion_considered": yun_converted,
        "theory_conflict_detected": bagua_result.get("mismatch_detected", False)
    }
    
    # 風險控制（v2.5：使用原始煞氣扣分計算風險值）
    family_risk = abs(raw_sha_penalty) + abs(zmg_score) if zmg_score < 0 else abs(raw_sha_penalty)
    
    # 化解建議聚合
    all_remedies = []
    if sha_result.get("remedies"):
        all_remedies.extend(sha_result["remedies"])
    
    # 運轉建議（雙周期版 + 多運交叉分析）
    yun_conversion = None
    if yun_converted and flying_star_result.get("status") == "success":
        yun_conversion = (
            f"該單位為{flying_yun}樓，當前已進入{flying_current_yun}。"
            "元運已轉換，建議進行大裝修換天心以適應新運氣場。"
            "雙周期評分已綜合建造運盤（70%）與當運盤（30%）計算。"
        )
        if multi_yun_rationale:
            yun_conversion += f"\n多運交叉分析：{multi_yun_rationale}"
        if multi_yun_needs_renovation:
            yun_conversion += "\n⚠️ 建議立即進行大裝修換天心，否則元運已過，風水效力大減。"
        yun_conversion += "（僅供參考，建議諮詢專業師傅確認）"
    elif flying_yun == "八運" and flying_star_result.get("status") == "success":
        yun_conversion = "該單位為八運樓，建議在2024年後進行大裝修換天心，以適應九運氣場。（僅供參考，建議諮詢專業師傅確認）"
    
    # 綜合理由
    rationales = [
        flying_star_result.get("rationale", ""),
        zero_main_god_result.get("rationale", ""),
        sha_result.get("rationale", ""),
        bazi_result.get("rationale", ""),
        bagua_result.get("rationale", ""),
        goal_result.get("rationale", "")
    ]
    
    ai_rationale = "\n".join([r for r in rationales if r])
    
    # v2.5：動態置信度（基於數據覆蓋度）
    # 每個模組的置信度基礎值，根據數據質量調整
    flying_conf = flying_star_result.get("confidence", 0.6)
    zmg_conf = zero_main_god_result.get("confidence", 0.6)
    sha_conf = sha_result.get("confidence", 0.6)
    bazi_conf = bazi_result.get("confidence", 0.6)
    bagua_conf = bagua_result.get("confidence", 0.6)
    goal_conf = goal_result.get("confidence", 0.6)
    gis_conf = gis_result.get("confidence", 0.5)
    
    # 數據缺失懲罰：如果模組返回 error/unsupported，降低置信度
    module_status = {
        "flying_star": flying_star_result.get("status", ""),
        "zero_main_god": zero_main_god_result.get("status", ""),
        "sha": sha_result.get("status", ""),
        "bazi": bazi_result.get("status", ""),
        "bagua": bagua_result.get("status", ""),
        "goal": goal_result.get("status", ""),
        "gis": gis_result.get("status", "")
    }
    for module, status in module_status.items():
        if status in ["error", "unsupported", "mismatch"]:
            if module == "flying_star": flying_conf *= 0.6
            elif module == "zero_main_god": zmg_conf *= 0.6
            elif module == "sha": sha_conf *= 0.6
            elif module == "bazi": bazi_conf *= 0.6
            elif module == "bagua": bagua_conf *= 0.6
            elif module == "goal": goal_conf *= 0.6
            elif module == "gis": gis_conf *= 0.6
    
    confidences = [flying_conf, zmg_conf, sha_conf, bazi_conf, bagua_conf, goal_conf, gis_conf]
    overall_confidence = round(sum(confidences) / len(confidences), 2)
    
    # v2.5：8維度 Radar 圖數據（正規化到 0-100）
    # 維度：飛星、八字、八宅、零正神、目標、物業特徵、煞氣防禦、GIS風水
    radar_data = {
        "dimensions": ["飛星", "八字", "八宅", "零正神", "目標", "物業特徵", "煞氣防禦", "GIS風水"],
        "scores": [
            round(min(100, max(0, (flying_norm / 20) * 100)), 1),
            round(min(100, max(0, (bazi_norm / 18) * 100)), 1),
            round(min(100, max(0, (bagua_norm / 13) * 100)), 1),
            round(min(100, max(0, (zmg_norm / 8) * 100)), 1),
            round(min(100, max(0, (goal_norm / 13) * 100)), 1),
            round(min(100, max(0, (property_norm / 10) * 100)), 1),
            round(min(100, max(0, (sha_norm / 7) * 100)), 1),
            round(min(100, max(0, (gis_norm / 8) * 100)), 1),
        ],
        "max_values": [100, 100, 100, 100, 100, 100, 100, 100]
    }
    
    # 八字完整信息
    bazi_data = bazi_result.get("bazi_full", {})
    
    # 八宅雙人對照表（如果存在）
    bagua_comparison = bagua_result.get("comparison_table") if bagua_result.get("is_dual") else None
    
    # 多目標詳情（如果存在）
    goal_details = goal_result.get("goals") if isinstance(goal_result.get("goals"), list) else None
    
    # 樓盤信息區塊（預留，由app.py填充）
    property_info = {}
    
    return {
        "property_id": f"HK_{flying_star_result.get('building_facing', 'UNK')}_{normalized_score}",
        "final_score": normalized_score,
        "rating": rating,
        "bazi_data": bazi_data,
        "score_breakdown": {
            "飛星": round(flying_norm, 1),
            "零正神": round(zmg_norm, 1),
            "八字": round(bazi_norm, 1),
            "八宅": round(bagua_norm, 1),
            "目標": round(goal_norm, 1),
            "物業特徵": round(property_norm, 1),
            "煞氣防禦": round(sha_norm, 1),
            "GIS風水": round(gis_norm, 1),
            "多運交叉適配": round(yun_adaptation_factor, 2),
            "樓層微調": round(floor_tie_breaker, 2)
        },
        "radar_chart": radar_data,
        "bagua_comparison": bagua_comparison,
        "goal_details": goal_details,
        "property_info": property_info,
        "investment_attributes": {
            "地段評分": round(region_score, 1),
            "地段等級": _get_district_tier(region_score),
            "note": "地段評分為投資屬性，不計入風水匹配分數"
        },
        "dynamic_risk_control": {
            "family_risk_coefficient": family_risk,
            "sha_defense_score": sha_defense,
            "building_health": building_health,
            "note": "風險分值僅供參考，具體安全判斷建議諮詢專業師傅"
        },
        "flags": flags,
        "data_source": "三六風水網專業知識庫",
        "confidence": overall_confidence,
        "ai_rationale": ai_rationale,
        "recommended_remedies": all_remedies,
        "yun_conversion_advice": yun_conversion,
        "disclaimer": "本報告為v2.5修復版計算結果，修復內容：1)煞氣改為正向防禦分避免負分截斷；2)樓齡改為建築健康分避免老樓強制低分；3)地段溢價從風水評分中剝離；4)元運交叉改為適配係數平滑過渡。僅供參考，具體入住/投資等重大決策建議諮詢專業風水師傅進行實地勘察。"
    }
