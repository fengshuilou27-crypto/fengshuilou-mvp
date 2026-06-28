from data.district_scores import get_district_score
from data.flying_star import analyze_multi_yun
from data.gis_analysis import analyze_gis_feng_shui

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
    聚合匹配結果
    加權計算總分，生成結構化報告
    100分制：飛星22 + 八字18 + 八宅13 + 零正神8 + 目標13 + 區位8 + 物業特徵5 + GIS 8 + 多運交叉±5 = 100
    扣分：煞氣（最多-20）/ 樓齡（最多-8）
    """
    # 提取分數
    flying_score = flying_star_result.get("score", 0)
    zmg_score = zero_main_god_result.get("score", 0)
    sha_score = sha_result.get("score", 0)
    bazi_score = bazi_result.get("score", 0)
    bagua_score = bagua_result.get("score", 0)
    goal_score = goal_result.get("score", 0)
    
    # 區位分數（基於地區評分，區分不同地段價值）
    region_score = get_district_score(district) if district else 5.0
    
    # 各模組正規化到100分制目標權重
    # 正規化公式：原始分數 × (目標權重 / 原始滿分)
    # 正分維度合計：22+18+13+8+13+8+8+5 = 95，+ 多運交叉±5 = 100
    # 煞氣模組（max_score=0）直接應用扣分
    flying_norm = (flying_score / 40) * 22   # 飛星 22 分（原30→25→22，核心但需為GIS留空間）
    zmg_norm = (zmg_score / 10) * 8          # 零正神 8 分
    bazi_norm = (bazi_score / 20) * 18       # 八字 18 分（原20分制）
    bagua_norm = (bagua_score / 10) * 13     # 八宅 13 分
    goal_norm = (goal_score / 15) * 13       # 目標 13 分
    region_norm = (region_score / 10) * 8     # 區位 8 分
    sha_norm = sha_score  # 直接應用扣分（負值）
    
    # === 樓齡懲罰 ===
    age_penalty = 0.0
    if building_year and eval_year:
        age = eval_year - building_year
        if age > 0:
            age_penalty = min(age * 0.15, 8.0)  # 每年扣0.15，最多扣8分
    
    # === 多運交叉分析 ===
    multi_yun_adjust = 0.0
    multi_yun_rationale = ""
    multi_yun_needs_renovation = False
    
    if building_year and building_facing:
        try:
            multi_yun_result = analyze_multi_yun(building_year, eval_year, building_facing)
            multi_yun_adjust = multi_yun_result.get("score_adjust", 0)
            multi_yun_rationale = multi_yun_result.get("rationale", "")
            multi_yun_needs_renovation = multi_yun_result.get("needs_renovation", False)
        except Exception:
            # 如果多運分析失敗，不影響其他計算
            multi_yun_adjust = 0.0
    
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
    
    # === 物業特徵加分 ===
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
        
        # 物業特徵總分上限 5 分
        property_bonus = min(property_bonus, 5.0)
    
    # === 樓層精確度微調（避免尾數相同導致分數相同）===
    floor_tie_breaker = 0.0
    if floor_number and isinstance(floor_number, int) and floor_number > 0:
        floor_tie_breaker = min(floor_number * 0.01, 0.3)  # 每層+0.01，最多+0.3
    
    # 計算總分（直接100分制，無需額外歸一化）
    total_score = (
        flying_norm + zmg_norm + bazi_norm + bagua_norm + goal_norm + region_norm + gis_norm + property_bonus
        + sha_norm + multi_yun_adjust - age_penalty + floor_tie_breaker
    )
    
    # 正分維度合計：22+18+13+8+13+8+8+5 = 95，+ 多運交叉(+5) = 100
    # 直接截斷到 0-100，無需再歸一化
    normalized_score = max(0, min(100, round(total_score, 1)))
    
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
    
    # 風險標記
    flying_yun = flying_star_result.get("yun", "")
    flying_current_yun = flying_star_result.get("current_yun", flying_yun)
    yun_converted = flying_yun != flying_current_yun
    
    flags = {
        "severe_penalty_applied": sha_score <= -12,
        "sha_detected": sha_score < 0,
        "remedies_required": sha_score < 0,
        "yun_conversion_considered": yun_converted,
        "theory_conflict_detected": bagua_result.get("mismatch_detected", False)
    }
    
    # 風險控制（基礎版：只計算數值，不做安全/危險判斷）
    family_risk = abs(sha_score) + abs(zmg_score) if zmg_score < 0 else abs(sha_score)
    # 基礎版不輸出 Safe/Caution/Risky 判斷，只輸出風險分值供參考
    
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
    
    # 計算整體置信度：各模組置信度的加權平均
    confidences = [
        flying_star_result.get("confidence", 0.6),
        zero_main_god_result.get("confidence", 0.6),
        sha_result.get("confidence", 0.6),
        bazi_result.get("confidence", 0.6),
        bagua_result.get("confidence", 0.6),
        goal_result.get("confidence", 0.6),
        gis_result.get("confidence", 0.5)
    ]
    overall_confidence = round(sum(confidences) / len(confidences), 2)
    
    # 8維度 Radar 圖數據（正規化到 0-100）
    radar_data = {
        "dimensions": ["飛星", "八字", "八宅", "零正神", "目標", "區位", "物業特徵", "GIS風水"],
        "scores": [
            round(min(100, max(0, (flying_norm / 22) * 100)), 1),
            round(min(100, max(0, (bazi_norm / 18) * 100)), 1),
            round(min(100, max(0, (bagua_norm / 13) * 100)), 1),
            round(min(100, max(0, (zmg_norm / 8) * 100)), 1),
            round(min(100, max(0, (goal_norm / 13) * 100)), 1),
            round(min(100, max(0, (region_norm / 8) * 100)), 1),
            round(min(100, max(0, (property_bonus / 5) * 100)), 1),
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
            "區位": round(region_norm, 1),
            "煞氣": round(sha_norm, 1),
            "八字": round(bazi_norm, 1),
            "八宅": round(bagua_norm, 1),
            "目標": round(goal_norm, 1),
            "物業特徵": round(property_bonus, 1),
            "GIS風水": round(gis_norm, 1),
            "多運交叉": round(multi_yun_adjust, 1),
            "樓層微調": round(floor_tie_breaker, 2),
            "樓齡懲罰": round(-age_penalty, 1)
        },
        "radar_chart": radar_data,
        "bagua_comparison": bagua_comparison,
        "goal_details": goal_details,
        "property_info": property_info,
        "dynamic_risk_control": {
            "family_risk_coefficient": family_risk,
            "note": "風險分值僅供參考，具體安全判斷建議諮詢專業師傅"
        },
        "flags": flags,
        "data_source": "三六風水網專業知識庫",
        "confidence": overall_confidence,
        "ai_rationale": ai_rationale,
        "recommended_remedies": all_remedies,
        "yun_conversion_advice": yun_conversion,
        "disclaimer": "本報告為v2.4優化版計算結果，基於三六風水網專業知識庫，飛星表已擴展至24山向，加入旺衰分析與喜用神計算，九宮吉凶方位分析，多運交叉分析（元運轉換評估），飛星盤自動推導刑煞，GIS地理風水分析（水法/地形/煞氣掃描）。僅供參考，具體入住/投資等重大決策建議諮詢專業風水師傅進行實地勘察。"
    }
