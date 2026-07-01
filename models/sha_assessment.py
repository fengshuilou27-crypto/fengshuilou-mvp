from data.sha import SHA_TABLE, SEVERITY_MAP
from data.flying_star import derive_sha_from_pan


def analyze_sha(detected_shas: list, flying_star_pan: dict = None):
    """
    煞氣分析模組 (v2.5 修正版)
    
    修正內容：
    1. 移除飛星盤 inauspicious_combo 的雙重扣分：飛星分析已獨立扣分，煞氣模組只處理外部物理環境煞氣
    2. 將煞氣扣分轉換為「煞氣防禦分」（0-7 正向維度），避免負分截斷
    3. 保留飛星盤煞氣推導，但只用於化解建議，不再重複扣分
    
    邏輯：
    - 外部煞氣（天斬煞、路沖等）→ 根據嚴重程度計算防禦分
    - 飛星盤煞氣（二五交加等）→ 僅記錄，用於化解建議，扣分已在飛星模組中計算
    - 防禦分：無煞氣=7，輕度=5，中度=3，重度=1，多項嚴重=0
    """
    # 從飛星盤自動推導刑煞（只用於化解建議，不額外扣分）
    derived_shas = []
    if flying_star_pan:
        derived_shas = derive_sha_from_pan(flying_star_pan)
    
    # 只處理外部輸入的煞氣（物理環境煞氣）
    all_shas = detected_shas or []
    
    if not all_shas and not derived_shas:
        return {
            "status": "success",
            "score": 7,  # v2.5: 無煞氣 = 完美防禦 7 分
            "max_score": 7,
            "raw_penalty": 0,  # 原始扣分（供 match_result.py 風險標記使用）
            "shas_found": [],
            "derived_shas": derived_shas,
            "remedies": [],
            "data_source": "互联网公开资料碎片",
            "confidence": 0.5,
            "rationale": "未檢測到已知煞氣，煞氣防禦完美。 基於公開資料查表，僅供參考。"
        }
    
    total_penalty = 0
    sha_details = []
    remedies = []
    
    for sha_name in all_shas:
        # 解析煞氣名稱和嚴重程度
        severity = "輕度"
        base_name = sha_name
        
        if "(" in sha_name and ")" in sha_name:
            base_name = sha_name.split("(")[0].strip()
            severity_str = sha_name.split("(")[1].split(")")[0]
            if severity_str in SEVERITY_MAP:
                severity = severity_str
        
        if base_name in SHA_TABLE:
            sha_info = SHA_TABLE[base_name]
            penalty = sha_info["penalty"]
            
            # 如果有指定嚴重程度，使用對應的扣分
            if severity in SEVERITY_MAP:
                penalty = SEVERITY_MAP[severity]
            
            total_penalty += penalty
            sha_details.append({
                "name": base_name,
                "severity": severity,
                "penalty": penalty,
                "desc": sha_info["desc"]
            })
            remedies.append({
                "item": sha_info["remedy"],
                "position": "視具體位置而定",
                "purpose": f"化解{base_name}",
                "cost": sha_info["cost"]
            })
        else:
            # 未知煞氣，使用通用配置：但避免重複添加默認建議
            total_penalty += -2
            sha_details.append({
                "name": base_name,
                "severity": "未知",
                "penalty": -2,
                "desc": "未收錄的煞氣類型"
            })
            existing_items = [r["item"] for r in remedies]
            if "請專業風水師勘察" not in existing_items:
                remedies.append({
                    "item": "請專業風水師勘察",
                    "position": "視具體位置而定",
                    "purpose": "化解%s" % base_name,
                    "cost": "待評估"
                })
    
    # 將飛星盤推導的煞氣加入化解建議（但不額外扣分）
    for ds in derived_shas:
        # 只添加尚未在 remedies 中的化解建議
        existing_items = [r["item"] for r in remedies]
        if ds["sha_type"] == "二五交加" and "六銅錢或金屬風水物化泄" not in existing_items:
            remedies.append({
                "item": "六銅錢或金屬風水物化泄",
                "position": "視具體位置而定",
                "purpose": f"化解{ds['sha_type']}",
                "cost": "低"
            })
        elif ds["sha_type"] == "六七交劍" and "水景或植物緩和金氣" not in existing_items:
            remedies.append({
                "item": "水景或植物緩和金氣",
                "position": "視具體位置而定",
                "purpose": f"化解{ds['sha_type']}",
                "cost": "中"
            })
    
    # v2.5: 將扣分轉換為防禦分（0-7）
    # 原始扣分範圍約 -30 ~ 0，映射到 7 ~ 0
    # 無煞氣=7，輕度(-4)=5，中度(-8)=3，重度(-15)=1，多項重度=0
    raw_penalty = max(-30, total_penalty)  # 保留原始扣分供風險標記使用
    
    if raw_penalty == 0:
        defense_score = 7
    elif raw_penalty >= -4:
        defense_score = 5
    elif raw_penalty >= -8:
        defense_score = 3
    elif raw_penalty >= -15:
        defense_score = 1
    else:
        defense_score = 0
    
    return {
        "status": "success",
        "score": defense_score,  # 0-7 的防禦分
        "max_score": 7,
        "raw_penalty": raw_penalty,  # 原始負分，供風險標記使用
        "shas_found": sha_details,
        "derived_shas": derived_shas,
        "remedies": remedies,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.55,
        "rationale": f"檢測到{len(sha_details)}項外部煞氣（飛星盤推導{len(derived_shas)}項僅供化解建議），"
                     f"原始扣分{abs(raw_penalty)}分，煞氣防禦分{defense_score}/7。"
                     + ("建議按照化解方案處理。" if remedies else "")
                     + " 基於公開資料查表，僅供參考，具體判斷建議諮詢專業師傅。"
    }
