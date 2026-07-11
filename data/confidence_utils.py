"""
動態置信度計算工具 (v2.5)

為各風水模組提供基於數據質量的動態置信度計算，
替代硬編碼的固定置信度值。
"""


def calculate_module_confidence(
    status: str = "success",
    data_completeness: float = 1.0,
    fallback_used: bool = False,
    source_quality: str = "professional"  # "professional" | "public" | "estimated"
) -> float:
    """
    計算模組的動態置信度
    
    Args:
        status: 模組狀態 (success, error, unsupported, mismatch, partial)
        data_completeness: 數據完整度 (0.0 ~ 1.0)
        fallback_used: 是否使用了回退數據
        source_quality: 數據源質量
    
    Returns:
        置信度 (0.0 ~ 1.0)
    """
    # 基礎置信度由數據源質量決定
    base_confidence = {
        "professional": 0.75,  # 專業知識庫
        "public": 0.55,      # 公開資料
        "estimated": 0.40    # 估算/推導
    }.get(source_quality, 0.50)
    
    # 狀態懲罰
    status_multiplier = {
        "success": 1.0,
        "partial": 0.8,
        "fallback": 0.6,
        "mismatch": 0.5,
        "unsupported": 0.4,
        "error": 0.3
    }.get(status, 0.5)
    
    # 數據完整度調整
    completeness_multiplier = 0.5 + (data_completeness * 0.5)  # 0.5 ~ 1.0
    
    # 回退數據懲罰
    fallback_multiplier = 0.6 if fallback_used else 1.0
    
    # 計算最終置信度
    confidence = base_confidence * status_multiplier * completeness_multiplier * fallback_multiplier
    
    # 確保在合理範圍內
    return round(max(0.1, min(0.95, confidence)), 2)


# 便捷函數：根據模組結果字典自動計算
def confidence_from_result(result: dict, source_quality: str = "professional") -> float:
    """
    從模組結果字典中提取信息並計算置信度
    
    Args:
        result: 模組返回的結果字典
        source_quality: 數據源質量
    
    Returns:
        置信度 (0.0 ~ 1.0)
    """
    status = result.get("status", "error")
    fallback_used = result.get("fallback_used", False)
    
    # 評估數據完整度
    data_completeness = 1.0
    if status in ["error", "unsupported"]:
        data_completeness = 0.0
    elif status == "mismatch":
        data_completeness = 0.3
    elif fallback_used:
        data_completeness = 0.5
    elif "confidence" in result and result.get("confidence", 0.0) < 0.5:
        data_completeness = 0.6
    
    return calculate_module_confidence(
        status=status,
        data_completeness=data_completeness,
        fallback_used=fallback_used,
        source_quality=source_quality
    )
