from data.sha import SHA_TABLE, SEVERITY_MAP


def analyze_sha(detected_shas: list):
    """
    煞氣分析模組
    根據輸入的煞氣列表，查表返回扣分和化解建議
    """
    if not detected_shas:
        return {
            "status": "success",
            "score": 0,
            "max_score": 0,
            "shas_found": [],
            "remedies": [],
            "data_source": "互联网公开资料碎片",
            "confidence": 0.5,
            "rationale": "未檢測到已知煞氣，該項目無扣分。 基於公開資料查表，僅供參考。"
        }
    
    total_penalty = 0
    sha_details = []
    remedies = []
    
    for sha_name in detected_shas:
        # 解析煞氣名稱和嚴重程度
        # 格式可能是 "天斬煞(輕度)" 或 "天斬煞"
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
            # 未知煞氣，使用通用配置
            total_penalty += -2
            sha_details.append({
                "name": base_name,
                "severity": "未知",
                "penalty": -2,
                "desc": "未收錄的煞氣類型"
            })
            remedies.append({
                "item": "請專業風水師勘察",
                "position": "視具體位置而定",
                "purpose": "化解%s" % base_name,
                "cost": "待評估"
            })
    
    # 煞氣分數上限為0（只扣分不加分）
    total_penalty = max(-30, total_penalty)
    
    return {
        "status": "success",
        "score": total_penalty,
        "max_score": 0,
        "shas_found": sha_details,
        "remedies": remedies,
        "data_source": "互联网公开资料碎片",
        "confidence": 0.55,
        "rationale": f"檢測到{len(sha_details)}項煞氣，總扣分{abs(total_penalty)}分。" +
                     ("建議按照化解方案處理。" if remedies else "")
                     + " 基於公開資料查表，僅供參考，具體判斷建議諮詢專業師傅。"
    }
