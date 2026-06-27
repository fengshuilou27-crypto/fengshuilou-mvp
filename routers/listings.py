from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import csv
import re

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


class MatchListingsRequest(BaseModel):
    user_profile: UserProfile
    top_n: int = Field(default=15, description="返回前N個樓盤")
    call_buy_threshold: int = Field(default=70, description="觸發叫買市場的分數閾值")


def _find_data_path(filename: str) -> Path:
    """Robustly find a data file in the project directory tree."""
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / ".." / ".." / "scraper_28hse" / "data" / filename,
        script_dir / ".." / ".." / ".." / "scraper_28hse" / "data" / filename,
        script_dir / ".." / ".." / ".." / ".." / "scraper_28hse" / "data" / filename,
    ]
    cwd = Path.cwd()
    for depth in range(0, 4):
        candidates.append(cwd / (".." * depth) / "scraper_28hse" / "data" / filename)
    current = script_dir
    for _ in range(5):
        scraper_dir = current / "scraper_28hse" / "data" / filename
        candidates.append(scraper_dir)
        current = current.parent
        if current == current.parent:
            break
    for p in candidates:
        try:
            resolved = p.resolve()
            if resolved.exists():
                return resolved
        except (OSError, RuntimeError):
            continue
    return None


LISTINGS_HEADERS = [
    "title", "district", "estate", "unit_info", "price", "price_raw",
    "build_area", "usable_area", "rooms", "facing", "property_type",
    "decoration", "views", "features", "agent", "posted_time", "url",
    "year_built", "yun", "estate_facing"
]


def load_listings():
    """載入樓盤數據（若缺失则自动生成空文件）"""
    listings = []
    data_path = _find_data_path("listings_28hse.csv")
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("facing") in SUPPORTED_FACINGS:
                    listings.append(row)
    else:
        scraper_data = _find_data_path("estates_28hse.csv")
        if scraper_data:
            listings_dir = scraper_data.parent
            empty_listings = listings_dir / "listings_28hse.csv"
            with open(empty_listings, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=LISTINGS_HEADERS)
                writer.writeheader()
    return listings


@router.post("/match/listings")
def match_listings(request: MatchListingsRequest):
    """模組3：配對物業 — 批量匹配，支持叫買市場"""
    profile = request.user_profile
    listings = load_listings()

    results = []
    for listing in listings:
        try:
            year = int(listing.get("year_built", 2000)) if listing.get("year_built") else 2000
            floor = 10
            if listing.get("unit_info"):
                m = re.search(r'(\d+)', listing.get("unit_info", ""))
                if m:
                    floor = int(m.group(1))

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
                goal=profile.goal,
                north_has_water=False,
                south_has_mountain=False,
                detected_shas=[]
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
            "age_range": f"{2026 - max([r.get('year_built', 2026) for r in top3])}-{2026 - min([r.get('year_built', 2026) for r in top3])}年"
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
