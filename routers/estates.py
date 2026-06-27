from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import csv
import os

from data.flying_star import SUPPORTED_FACINGS
from routers.evaluate import RequestMeta, run_single_match

router = APIRouter(prefix="/api")


class UserProfile(BaseModel):
    eval_year: int = Field(default=2026, description="評估年份")
    user_gender: str = Field(..., description="性別：男/女")
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="出生時間 HH:MM")
    user_job: Optional[str] = Field(None, description="職業")
    goal: str = Field(..., description="目標：財富/健康/事業/桃花/家庭和睦")
    household_weight_mode: Optional[str] = Field("balanced", description="家庭權重模式")


class MatchEstatesRequest(BaseModel):
    user_profile: UserProfile
    top_n: int = Field(default=3, description="返回前N個屋苑")


# 默認樓層 (當無法從數據獲取時)
DEFAULT_FLOOR = 10


def _get_data_path(filename: str) -> Path:
    """獲取數據文件路徑 (本地data目錄)"""
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"
    file_path = data_dir / filename
    if file_path.exists():
        return file_path
    return None


def load_estates():
    """載入屋苑數據 (從統一數據源)"""
    estates = []
    
    # 優先使用統一數據源
    data_path = _get_data_path("estates_unified.csv")
    if not data_path:
        data_path = _get_data_path("estates_28hse.csv")
    
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 檢查坐向是否在支持列表中
                if row.get("facing") in SUPPORTED_FACINGS:
                    estates.append(row)
    
    return estates


def _estimate_floor(estate: dict) -> int:
    """從屋苑數據估算樓層 (中層為默認)"""
    # 如果有總層數信息，取中層
    total_floors = estate.get("total_floors", "")
    if total_floors and total_floors.isdigit():
        return int(total_floors) // 2
    return DEFAULT_FLOOR


def _estimate_environment(estate: dict):
    """從屋苑數據估算環境特徵"""
    has_sea = estate.get("has_sea_view", "False").lower() == "true"
    has_mountain = estate.get("has_mountain_view", "False").lower() == "true"
    
    # 北水：臨海且面向南或東南/西南
    facing = estate.get("facing", "")
    north_water = has_sea and facing in ["子山午向", "癸山丁向", "丑山未向", "艮山坤向", "壬山丙向"]
    
    # 南山：靠山且面向北或東北/西北
    south_mountain = has_mountain and facing in ["午山子向", "丁山癸向", "未山丑向", "坤山艮向", "丙山壬向"]
    
    return north_water, south_mountain


@router.post("/match/estates")
def match_estates(request: MatchEstatesRequest):
    """模組2：配對屋苑 — 批量匹配，返回TOP N (v2.2)"""
    profile = request.user_profile
    estates = load_estates()
    
    if not estates:
        return {
            "status": "error",
            "module": "模組2 - 配對屋苑",
            "error": "無可用屋苑數據",
            "total_estates": 0,
            "top_results": [],
            "all_results": []
        }

    results = []
    for estate in estates:
        try:
            # 估算樓層和環境
            floor = _estimate_floor(estate)
            north_water, south_mountain = _estimate_environment(estate)
            
            meta = RequestMeta(
                eval_year=profile.eval_year,
                user_gender=profile.user_gender,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                user_job=profile.user_job,
                household_weight_mode=profile.household_weight_mode,
                building_year=int(estate.get("building_year", 2000)) if estate.get("building_year") else 2000,
                building_facing=estate["facing"],
                floor_number=floor,
                goal=profile.goal,
                north_has_water=north_water,
                south_has_mountain=south_mountain,
                detected_shas=[]
            )
            match_result = run_single_match(meta, district=estate.get("district", ""))
            yb = estate.get("building_year", "")
            try:
                year_built = int(yb) if yb else 0
            except ValueError:
                year_built = 0
            results.append({
                "name": estate["name"],
                "district": estate.get("district", ""),
                "facing": estate["facing"],
                "year_built": year_built,
                "yun": estate.get("yun", ""),
                "property_type": estate.get("property_type", estate.get("type", "私人屋苑")),
                "final_score": match_result["final_score"],
                "rating": match_result["rating"],
                "score_breakdown": match_result["score_breakdown"],
                "flags": match_result["flags"],
                "rationale": match_result["ai_rationale"],
                "match": match_result
            })
        except Exception as e:
            print(f"計算錯誤 {estate.get('name')}: {e}")

    results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = results[:request.top_n]

    return {
        "status": "success",
        "module": "模組2 - 配對屋苑",
        "total_estates": len(results),
        "top_results": top_results,
        "all_results": results
    }
