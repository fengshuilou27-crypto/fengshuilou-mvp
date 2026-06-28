from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import csv
import re
import os

from data.flying_star import SUPPORTED_FACINGS
from routers.evaluate import RequestMeta, run_single_match

router = APIRouter(prefix="/api")


class GoalItem(BaseModel):
    goal: str = Field(..., description="目標：財富/健康/事業/桃花/家庭和睦")
    priority: int = Field(1, description="優先級：1=主, 2=次, 3=第三")

class UserProfile(BaseModel):
    eval_year: int = Field(default=2026, description="評估年份")
    user_gender: str = Field(..., description="性別：男/女")
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="出生時間 HH:MM")
    user_job: Optional[str] = Field(None, description="職業")
    goals: List[GoalItem] = Field(..., description="目標列表，最多3個")
    household_weight_mode: Optional[str] = Field("balanced", description="家庭權重模式")


class MatchListingsRequest(BaseModel):
    user_profile: UserProfile
    top_n: int = Field(default=15, description="返回前N個樓盤")
    call_buy_threshold: int = Field(default=70, description="觸發叫買市場的分數閾值")


LISTINGS_HEADERS = [
    "title", "district", "estate", "unit_info", "price", "price_raw",
    "build_area", "usable_area", "rooms", "facing", "property_type",
    "decoration", "views", "features", "agent", "posted_time", "url",
    "year_built", "yun", "estate_facing"
]


def _get_data_path(filename: str) -> Path:
    """獲取數據文件路徑 (本地data目錄)"""
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"
    file_path = data_dir / filename
    if file_path.exists():
        return file_path
    return None


def load_listings():
    """載入樓盤數據"""
    listings = []
    data_path = _get_data_path("listings_28hse.csv")
    
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("facing") in SUPPORTED_FACINGS:
                    listings.append(row)
    
    return listings


def _extract_floor_from_unit_info(unit_info: str) -> int:
    """從單位信息中提取樓層"""
    if not unit_info:
        return 10  # 默認中層
    
    # 常見格式："中層", "高層", "低層", "10座 中層", "A座 高層 15樓"
    # 先嘗試提取數字
    m = re.search(r'(\d+)', unit_info)
    if m:
        floor = int(m.group(1))
        # 如果是座數(通常<5)，忽略，返回默認
        if floor <= 5 and "座" in unit_info:
            return 10
        return min(max(floor, 1), 80)  # 限制在1-80層
    
    # 中/高/低層關鍵詞映射
    if "高層" in unit_info:
        return 25
    elif "低層" in unit_info:
        return 5
    elif "中層" in unit_info:
        return 10
    elif "地下" in unit_info or "G" in unit_info:
        return 1
    elif "頂層" in unit_info or "天台" in unit_info:
        return 30
    
    return 10


@router.post("/match/listings")
def match_listings(request: MatchListingsRequest):
    """模組3：配對物業 — 批量匹配，支持叫買市場 (v2.2)"""
    profile = request.user_profile
    listings = load_listings()
    
    if not listings:
        return {
            "status": "success",
            "module": "模組3 - 配對物業",
            "total_listings": 0,
            "top_results": [],
            "call_buy_market": {
                "triggered": False,
                "threshold": request.call_buy_threshold,
                "high_score_count": 0,
                "anonymous_profile": None
            },
            "all_results": []
        }

    results = []
    for listing in listings:
        try:
            year = int(listing.get("year_built", 2000)) if listing.get("year_built") else 2000
            
            # 從unit_info提取樓層 (v2.2 改進)
            floor = _extract_floor_from_unit_info(listing.get("unit_info", ""))
            
            # 從listing數據估算環境 (v2.2 改進)
            has_sea = listing.get("views", "").lower() in ["海景", "開揚景", "好景"]
            has_mountain = listing.get("views", "").lower() in ["山景", "園景", "綠化"]
            
            # 根據坐向估算北水南山
            facing = listing.get("facing", "")
            north_water = has_sea and facing in ["子山午向", "癸山丁向", "丑山未向", "艮山坤向", "壬山丙向"]
            south_mountain = has_mountain and facing in ["午山子向", "丁山癸向", "未山丑向", "坤山艮向", "丙山壬向"]
            
            meta = RequestMeta(
                eval_year=profile.eval_year,
                user_gender=profile.user_gender,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                user_job=profile.user_job,
                household_weight_mode=profile.household_weight_mode,
                building_year=year,
                building_facing=listing["facing"],
                floor_number=floor,
                goal=profile.goals[0].goal if profile.goals else "財富",
                north_has_water=north_water,
                south_has_mountain=south_mountain,
                detected_shas=[],
                estate_name=listing.get("estate", "")
            )
            match_result = run_single_match(meta, district=listing.get("district", ""))
            results.append({
                "title": listing.get("title", ""),
                "estate": listing.get("estate", ""),
                "district": listing.get("district", ""),
                "facing": listing["facing"],
                "price_raw": listing.get("price_raw", ""),
                "build_area": listing.get("build_area", ""),
                "usable_area": listing.get("usable_area", ""),
                "rooms": listing.get("rooms", ""),
                "unit_info": listing.get("unit_info", ""),
                "year_built": listing.get("year_built", ""),
                "agent": listing.get("agent", ""),
                "final_score": match_result["final_score"],
                "rating": match_result["rating"],
                "score_breakdown": match_result["score_breakdown"],
                "flags": match_result["flags"],
                "rationale": match_result["ai_rationale"]
            })
        except Exception as e:
            print(f"計算錯誤 {listing.get('title')}: {e}")

    results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = results[:request.top_n]

    # 叫買市場判斷
    high_score = [r for r in results if r["final_score"] >= request.call_buy_threshold]
    call_buy_triggered = len(high_score) == 0

    call_buy_profile = None
    if call_buy_triggered and results:
        top3 = results[:3]
        call_buy_profile = {
            "facing": list(set([r["facing"] for r in top3])),
            "district": list(set([r["district"] for r in top3])),
            "age_range": f"{2026 - max([int(r.get('year_built', 2026)) if r.get('year_built') and r.get('year_built').isdigit() else 2026 for r in top3])}-{2026 - min([int(r.get('year_built', 2026)) if r.get('year_built') and r.get('year_built').isdigit() else 2026 for r in top3])}年"
        }

    return {
        "status": "success",
        "module": "模組3 - 配對物業",
        "total_listings": len(results),
        "top_results": top_results,
        "call_buy_market": {
            "triggered": call_buy_triggered,
            "threshold": request.call_buy_threshold,
            "high_score_count": len(high_score),
            "anonymous_profile": call_buy_profile
        },
        "all_results": results
    }
