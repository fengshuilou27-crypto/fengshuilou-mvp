from data.flying_star import FLYING_STAR_TABLE, get_yun, SUPPORTED_FACINGS


def _analyze_single_yun(yun: str, building_facing: str, eval_year: int = 2026):
    """
    分析單一運數的宅運盤（內部輔助函數）
    """
    # 檢查坐向是否支持
    if building_facing not in SUPPORTED_FACINGS:
        return {
            "status": "unsupported",
            "error": f"該坐向'{building_facing}'暫未收錄。MVP 支持: {', '.join(SUPPORTED_FACINGS)}",
            "score": 0,
            "max_score": 40,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.0,
            "rationale": "該坐向暫未收錄，具體判斷建議諮詢專業師傅。"
        }
    
    # 檢查運數與坐向是否匹配
    if yun not in FLYING_STAR_TABLE or building_facing not in FLYING_STAR_TABLE[yun]:
        return {
            "status": "mismatch",
            "error": f"{yun}的{building_facing}暫未收錄",
            "score": 0,
            "max_score": 40,
            "data_source": "互联网公开资料碎片",
            "confidence": 0.0,
            "rationale": f"MVP未收錄該坐向的{yun}宅運盤。"
        }
    
    chart = FLYING_STAR_TABLE[yun][building_facing]
    
    # 基礎分
    base_score = chart.get("base_score", 10)
    
    # 吉凶組合加減分
    auspicious_score = len(chart.get("auspicious_combos", [])) * 5
    inauspicious_score = len(chart.get("inauspicious_combos", [])) * (-5)
    
    # 年度疊加（簡化版）
    annual_adjustment = 0
    annual_overlay = chart.get("annual_overlay", {}).get(eval_year, {})
    annual_desc = []
    for direction, desc in annual_overlay.items():
        annual_desc.append(f"{direction}: {desc}")
        if "大凶" in desc:
            annual_adjustment -= 3
        elif "中吉" in desc or "大吉" in desc:
            annual_adjustment += 2
    
    total_score = base_score + auspicious_score + inauspicious_score + annual_adjustment
    total_score = max(5, min(40, total_score))  # 飛星分數上限40，下限5
    
    return {
        "status": "success",
        "yun": yun,
        "building_facing": building_facing,
        "pan_type": chart["pan_type"],
        "mountain_stars": chart["mountain_stars"],
        "facing_stars": chart["facing_stars"],
        "score": total_score,
        "max_score": 40,
        "base_score": base_score,
        "auspicious_score": auspicious_score,
        "inauspicious_score": inauspicious_score,
        "annual_adjustment": annual_adjustment,
        "auspicious_combos": chart.get("auspicious_combos", []),
        "inauspicious_combos": chart.get("inauspicious_combos", []),
        "annual_overlay": annual_desc,
        "data_source": "互联网公开资料碎片",
        "confidence": chart.get("confidence", 0.55),
        "rationale": f"{yun}{building_facing}，{chart['pan_type']}格局。宅運基礎分{base_score}分，"
                     f"吉組合加{auspicious_score}分，凶組合減{abs(inauspicious_score)}分，"
                     f"年度調整{annual_adjustment}分。 {chart.get('note', '基於公開資料排盤計算，僅供參考。')}"
    }


def analyze_flying_star(building_year: int, building_facing: str, eval_year: int = 2026, current_yun: str = None):
    """
    飛星分析模組（雙周期版）
    
    支持「建造運 + 當運」雙參數計算：
    - building_year: 建築年份 → 推導建造運
    - eval_year: 評估年份 → 推導當運
    - current_yun: 可選，直接指定當運（覆蓋eval_year推導）
    
    雙周期評分邏輯：
    - 同運：單一運盤評分
    - 異運：建造運佔70%權重，當運佔30%權重（未換天心情況下）
    - 異運且已換天心：當運佔70%，建造運佔30%
    """
    building_yun = get_yun(building_year)
    current_yun = current_yun or get_yun(eval_year)
    
    # 計算建造運盤
    building_chart = _analyze_single_yun(building_yun, building_facing, eval_year)
    
    # 如果建造運盤本身出錯，直接返回錯誤（附帶雙周期信息）
    if building_chart.get("status") != "success":
        building_chart["dual_period"] = {
            "enabled": False,
            "building_yun": building_yun,
            "current_yun": current_yun,
            "note": f"建造運盤查詢失敗（{building_chart.get('status')}），無法進行雙周期分析。"
        }
        return building_chart
    
    # 同運情況：直接返回單一盤
    if building_yun == current_yun:
        building_chart["dual_period"] = {
            "enabled": False,
            "building_yun": building_yun,
            "current_yun": current_yun,
            "note": "建造運與當運一致，單一運盤分析。"
        }
        return building_chart
    
    # 異運情況：計算雙盤並加權
    current_chart = _analyze_single_yun(current_yun, building_facing, eval_year)
    
    # 如果當運盤查詢失敗，退化为單一建造運盤（降低置信度）
    if current_chart.get("status") != "success":
        building_chart["score"] = max(5, building_chart.get("score", 0) - 5)  # 異運但無當運數據，扣5分保守處理
        building_chart["dual_period"] = {
            "enabled": True,
            "building_yun": building_yun,
            "current_yun": current_yun,
            "building_weight": 1.0,
            "current_weight": 0.0,
            "current_yun_unavailable": True,
            "note": f"當運（{current_yun}）該坐向暫未收錄，僅以建造運盤評分（已扣5分保守處理）。"
        }
        building_chart["confidence"] = round(building_chart.get("confidence", 0.55) * 0.8, 2)
        building_chart["rationale"] += f"\n【雙周期】當運（{current_yun}）該坐向暫未收錄，僅以建造運盤評分。"
        return building_chart
    
    # 雙周期加權評分（未換天心：建造運70% + 當運30%）
    building_score = building_chart.get("score", 0)
    current_score = current_chart.get("score", 0)
    
    # 加權計算
    combined_score = round(building_score * 0.7 + current_score * 0.3, 1)
    combined_score = max(5, min(40, combined_score))
    
    # 雙周期風水判斷
    yun_transition_note = (
        f"該樓宇建於{building_yun}，當前為{current_yun}。"
        "元運已轉換，建議進行大裝修換天心以適應新運氣場。"
        "以下評分綜合建造運盤（70%）與當運盤（30%）計算。"
    )
    
    # 格局變化判斷（如建造運到山到向，當運變上山下水）
    pan_type_change = ""
    if building_chart.get("pan_type") != current_chart.get("pan_type"):
        pan_type_change = (
            f"格局變化：建造運為「{building_chart.get('pan_type')}」，"
            f"當運變為「{current_chart.get('pan_type')}」。"
            "運過即衰，建議重新佈局。"
        )
    
    # 置信度：取兩盤中較低者（異運情況複雜度更高）
    combined_confidence = min(
        building_chart.get("confidence", 0.55),
        current_chart.get("confidence", 0.55)
    ) * 0.9  # 異運情況降低10%置信度
    
    # 綜合理由
    combined_rationale = (
        f"【雙周期分析】{yun_transition_note}\n"
        f"建造運（{building_yun}）：{building_chart.get('rationale', '')}\n"
        f"當運（{current_yun}）：{current_chart.get('rationale', '')}\n"
        f"加權評分：建造運{building_score}×0.7 + 當運{current_score}×0.3 = {combined_score}分。"
        f" {pan_type_change}"
        " ⚠️ 雙周期計算為MVP簡化版，具體風水判斷建議諮詢專業師傅。"
    )
    
    return {
        "status": "success",
        "yun": building_yun,
        "current_yun": current_yun,
        "building_facing": building_facing,
        "pan_type": building_chart.get("pan_type"),
        "current_pan_type": current_chart.get("pan_type"),
        "mountain_stars": building_chart.get("mountain_stars"),
        "facing_stars": building_chart.get("facing_stars"),
        "current_mountain_stars": current_chart.get("mountain_stars"),
        "current_facing_stars": current_chart.get("facing_stars"),
        "score": combined_score,
        "building_score": building_score,
        "current_score": current_score,
        "max_score": 40,
        "base_score": building_chart.get("base_score"),
        "auspicious_score": building_chart.get("auspicious_score"),
        "inauspicious_score": building_chart.get("inauspicious_score"),
        "annual_adjustment": building_chart.get("annual_adjustment"),
        "auspicious_combos": building_chart.get("auspicious_combos", []),
        "inauspicious_combos": building_chart.get("inauspicious_combos", []),
        "current_auspicious_combos": current_chart.get("auspicious_combos", []),
        "current_inauspicious_combos": current_chart.get("inauspicious_combos", []),
        "annual_overlay": building_chart.get("annual_overlay", []),
        "dual_period": {
            "enabled": True,
            "building_yun": building_yun,
            "current_yun": current_yun,
            "building_weight": 0.7,
            "current_weight": 0.3,
            "pan_type_change": pan_type_change != "",
            "note": yun_transition_note
        },
        "data_source": "互联网公开资料碎片",
        "confidence": round(combined_confidence, 2),
        "rationale": combined_rationale
    }
