from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import csv

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


def load_estates():
    """載入屋苑數據"""
    estates = []
    data_path = _find_data_path("estates_28hse.csv")
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("facing") in SUPPORTED_FACINGS:
                    estates.append(row)
    return estates


@router.post("/match/estates")
def match_estates(request: MatchEstatesRequest):
    """模組2：配對屋苑 — 批量匹配，返回TOP N"""
    profile = request.user_profile
    estates = load_estates()

    results = []
    for estate in estates:
        try:
            meta = RequestMeta(
                eval_year=profile.eval_year,
                user_gender=profile.user_gender,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                user_job=profile.user_job,
                household_weight_mode=profile.household_weight_mode,
                building_year=int(estate.get("year_built", 2000)),
                building_facing=estate["facing"],
                floor_number=10,  # 模組2用假設中層
                goal=profile.goal,
                north_has_water=False,
                south_has_mountain=False,
                detected_shas=[]
            )
            match_result = run_single_match(meta, district=estate.get("district", ""))
            yb = estate.get("building_year", estate.get("year_built", ""))
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
                "score": match_result["final_score"],
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
