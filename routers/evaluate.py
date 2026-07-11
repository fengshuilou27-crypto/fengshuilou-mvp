from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from data.flying_star import get_yun, SUPPORTED_FACINGS
from models.flying_star_analysis import analyze_flying_star
from models.zero_main_god import analyze_zero_main_god
from models.sha_assessment import analyze_sha
from models.bazi_matching import analyze_bazi
from models.bagua_matching import analyze_bagua
from models.goal_matching import analyze_goal
from models.match_result import aggregate_match_result

router = APIRouter(prefix="/api")


class RequestMeta(BaseModel):
    eval_year: int = Field(default=2026, description="評估年份")
    user_gender: str = Field(..., description="性別：男/女")
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="出生時間 HH:MM")
    birth_place: Optional[str] = Field(None, description="出生地")
    user_job: Optional[str] = Field(None, description="職業")
    floor_preference: Optional[str] = Field(None, description="樓層偏好")
    household_weight_mode: Optional[str] = Field("balanced", description="家庭權重模式")
    building_year: int = Field(..., description="建築年份")
    building_facing: str = Field(..., description="坐向：子山午向/丑山未向/乾山巽向/卯山酉向等")
    floor_number: int = Field(..., description="樓層")
    # 多目標支持（v2.5+）：goals 為列表，每項為 {"goal": str, "priority": int}
    goals: Optional[List[dict]] = Field(default=None, description="目標列表")
    # 向後兼容：單一目標字符串（舊版前端可能發送）
    goal: Optional[str] = Field(None, description="目標：財富/健康/事業/桃花/家庭和睦（舊版，優先使用 goals）")
    north_has_water: bool = Field(False, description="北側有水")
    south_has_mountain: bool = Field(False, description="南側有山")
    detected_shas: Optional[List[str]] = Field(default=[], description="已知煞氣")
    # 同住人（雙人模式）
    cohabitant_enabled: Optional[bool] = Field(False, description="同住人啟用")
    cohabitant_gender: Optional[str] = Field(None, description="同住人性別")
    cohabitant_birth_date: Optional[str] = Field(None, description="同住人出生日期")
    cohabitant_birth_time: Optional[str] = Field(None, description="同住人出生時間")
    cohabitant_user_job: Optional[str] = Field(None, description="同住人職業")
    cohabitant_weight_ratio: Optional[float] = Field(0.5, description="同住人權重比例")
    address: Optional[str] = Field(None, description="物業地址")


class EvaluateRequest(BaseModel):
    """評估請求模型"""
    request_meta: RequestMeta


def _get_goals(meta: RequestMeta) -> list:
    """從 RequestMeta 提取目標列表，支持多目標和向後兼容"""
    if meta.goals and isinstance(meta.goals, list) and len(meta.goals) > 0:
        return meta.goals
    if meta.goal:
        return [{"goal": meta.goal, "priority": 1}]
    return []


def run_single_match(meta: RequestMeta, district: str = None):
    """執行單次匹配計算"""
    # 提取目標
    goals = _get_goals(meta)

    # 1. 飛星分析
    flying_star_result = analyze_flying_star(
        building_year=meta.building_year,
        building_facing=meta.building_facing,
        eval_year=meta.eval_year
    )

    # 2. 雙期飛星
    current_yun = get_yun(meta.eval_year)
    building_yun = get_yun(meta.building_year)
    current_yun_result = None
    if current_yun != building_yun:
        from data.flying_star import FLYING_STAR_TABLE
        if current_yun in FLYING_STAR_TABLE and meta.building_facing in FLYING_STAR_TABLE[current_yun]:
            current_yun_result = analyze_flying_star(
                building_year=meta.eval_year,
                building_facing=meta.building_facing,
                eval_year=meta.eval_year
            )

    # 3. 零正神
    zero_main_god_result = analyze_zero_main_god(
        building_year=meta.building_year,
        building_facing=meta.building_facing,
        north_has_water=meta.north_has_water,
        south_has_mountain=meta.south_has_mountain
    )

    # 4. 煞氣
    sha_result = analyze_sha(detected_shas=meta.detected_shas or [])

    # 5. 八字（完整四柱，傳入出生時間 + v2.5 納甲樓層五行）
    bazi_result = analyze_bazi(
        birth_date=meta.birth_date,
        floor_number=meta.floor_number,
        birth_time=meta.birth_time,
        building_facing=meta.building_facing
    )

    # 6. 八宅（支持雙人模式）
    if meta.cohabitant_enabled and meta.cohabitant_birth_date and meta.cohabitant_gender:
        bagua_result = analyze_bagua(
            birth_date=meta.birth_date,
            gender=meta.user_gender,
            building_facing=meta.building_facing,
            cohabitant_birth_date=meta.cohabitant_birth_date,
            cohabitant_gender=meta.cohabitant_gender,
            weight_ratio=meta.cohabitant_weight_ratio
        )
    else:
        bagua_result = analyze_bagua(
            birth_date=meta.birth_date,
            gender=meta.user_gender,
            building_facing=meta.building_facing
        )

    # 7. 目標（多目標支持）
    goal_result = analyze_goal(
        building_year=meta.building_year,
        building_facing=meta.building_facing,
        goals=goals if goals else []
    )

    # 8. 聚合
    property_features = {}
    if meta.address:
        property_features["address"] = meta.address

    match_result = aggregate_match_result(
        flying_star_result=flying_star_result,
        zero_main_god_result=zero_main_god_result,
        sha_result=sha_result,
        bazi_result=bazi_result,
        bagua_result=bagua_result,
        goal_result=goal_result,
        district=district,
        building_year=meta.building_year,
        eval_year=meta.eval_year,
        property_features=property_features if property_features else None,
        floor_number=meta.floor_number,
        building_facing=meta.building_facing,
        estate_name=meta.address
    )

    match_result["dual_period_flying_star"] = {
        "building_yun": building_yun,
        "current_yun": current_yun,
        "building_yun_analysis": flying_star_result,
        "current_yun_analysis": current_yun_result,
        "yun_transition_note": f"該樓宇建於{building_yun}，當前為{current_yun}。"
                                + ("元運已轉換，建議進行大裝修換天心。" if building_yun != current_yun else "元運匹配，無需特別調整。")
    }

    # 添加樓盤信息
    if meta.address:
        match_result["property_info"] = {"address": meta.address}

    # 添加雙人模式標記
    if meta.cohabitant_enabled:
        match_result["cohabitant_enabled"] = True
        match_result["cohabitant_weight_ratio"] = meta.cohabitant_weight_ratio

    return match_result


@router.post("/evaluate")
def evaluate(request: EvaluateRequest):
    """模組1：自測現有住所 — 單一評估"""
    meta = request.request_meta
    match_result = run_single_match(meta)

    return {
        "status": "success",
        "match_result": match_result
    }
