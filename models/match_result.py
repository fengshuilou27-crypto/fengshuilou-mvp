from data.district_scores import get_district_score

def aggregate_match_result(
    flying_star_result: dict,
    zero_main_god_result: dict,
    sha_result: dict,
    bazi_result: dict,
    bagua_result: dict,
    goal_result: dict,
    district: str = None
):
    """
    聚合匹配結果
    加權計算總分，生成結構化報告
    100分制：飛星30 / 八字20 / 八宅15 / 零正神10 / 目標15 / 區位10 / 煞氣扣分
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
    # 煞氣模組（max_score=0）直接應用扣分
    flying_norm = (flying_score / 40) * 30
    zmg_norm = (zmg_score / 10) * 10
    bazi_norm = bazi_score  # bazi_matching 已改為20分制，直接等於目標權重20
    bagua_norm = (bagua_score / 10) * 15
    goal_norm = (goal_score / 15) * 15
    region_norm = (region_score / 10) * 10  # 固定10分
    sha_norm = sha_score  # 直接應用扣分
    
    # 計算總分
    total_score = (
        flying_norm + zmg_norm + sha_norm + bazi_norm + bagua_norm + goal_norm + region_norm
    )
    
    # 理論最高分（100分制）
    max_possible = 30 + 10 + 0 + 20 + 15 + 15 + 10  # = 100
    
    # 標準化到100分制
    normalized_score = (total_score / max_possible) * 100
    normalized_score = max(0, min(100, round(normalized_score, 1)))
    
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
    
    # 運轉建議（雙周期版）
    yun_conversion = None
    if yun_converted and flying_star_result.get("status") == "success":
        yun_conversion = (
            f"該單位為{flying_yun}樓，當前已進入{flying_current_yun}。"
            "元運已轉換，建議進行大裝修換天心以適應新運氣場。"
            "雙周期評分已綜合建造運盤（70%）與當運盤（30%）計算。"
            "（僅供參考，建議諮詢專業師傅確認）"
        )
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
        goal_result.get("confidence", 0.6)
    ]
    overall_confidence = round(sum(confidences) / len(confidences), 2)
    
    # 6維度 Radar 圖數據（正規化到 0-100）
    radar_data = {
        "dimensions": ["飛星", "八字", "八宅", "零正神", "目標", "區位"],
        "scores": [
            round(min(100, max(0, (flying_norm / 30) * 100)), 1),
            round(min(100, max(0, (bazi_norm / 20) * 100)), 1),
            round(min(100, max(0, (bagua_norm / 15) * 100)), 1),
            round(min(100, max(0, (zmg_norm / 10) * 100)), 1),
            round(min(100, max(0, (goal_norm / 15) * 100)), 1),
            round(min(100, max(0, (region_norm / 10) * 100)), 1),
        ],
        "max_values": [100, 100, 100, 100, 100, 100]
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
            "目標": round(goal_norm, 1)
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
        "data_source": "互联网公开资料碎片",
        "confidence": overall_confidence,
        "ai_rationale": ai_rationale,
        "recommended_remedies": all_remedies,
        "yun_conversion_advice": yun_conversion,
        "disclaimer": "本報告為基礎版計算結果，基於互聯網公開資料碎片，僅供參考。具體入住/投資等重大決策建議諮詢專業風水師傅進行實地勘察。"
    }
