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


# 朝向到24山向映射表（2026-06-18 新增）
# 朝向 = 面向的方向，坐向 = 背靠的方向
# 例如：朝南 = 坐北朝南 = 子山午向
DIRECTION_TO_FACING = {
    # 朝向 = 面向的方向，坐向 = 背靠的方向
    # 例如：朝南 = 坐北朝南 = 子山午向
    "朝南": "子山午向",
    "朝北": "午山子向",
    "朝东": "卯山酉向",
    "朝西": "酉山卯向",
    "朝东南": "巽山乾向",
    "朝西北": "乾山巽向",
    "朝西南": "艮山坤向",   # 修正：面向西南 = 坐东北向西南 = 艮山坤向
    "朝东北": "坤山艮向",   # 修正：面向东北 = 坐西南向东北 = 坤山艮向
    "南": "子山午向",
    "北": "午山子向",
    "东": "卯山酉向",
    "西": "酉山卯向",
    "东南": "巽山乾向",
    "西北": "乾山巽向",
    "西南": "艮山坤向",
    "东北": "坤山艮向",
}


def load_estates():
    """載入屋苑數據（支持朝向映射）"""
    estates = []
    possible_paths = [
        Path(__file__).parent / ".." / "scraper_28hse" / "data" / "estates_28hse.csv",
        Path(__file__).parent / ".." / ".." / "scraper_28hse" / "data" / "estates_28hse.csv",
        Path("scraper_28hse/data/estates_28hse.csv"),
        Path("../scraper_28hse/data/estates_28hse.csv"),
        Path("../../scraper_28hse/data/estates_28hse.csv"),
    ]
    data_path = None
    for p in possible_paths:
        if p.exists():
            data_path = p
            break
    if data_path:
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 支持朝向映射：如果 facing 是朝向（如「朝南」），映射到24山向
                raw_facing = row.get("facing", "")
                mapped_facing = DIRECTION_TO_FACING.get(raw_facing, raw_facing)
                
                if mapped_facing in SUPPORTED_FACINGS:
                    row["facing"] = mapped_facing  # 更新为映射后的坐向
                    row["original_facing"] = raw_facing  # 保留原始朝向
                    estates.append(row)
    return estates


# === Module 5 整合： estates 為底 + listings 價格信息 ===

def load_listings():
    """載入在售物業列表（如果存在）"""
    listings = {}
    possible_paths = [
        Path(__file__).parent / ".." / "scraper_28hse" / "data" / "listings_28hse.csv",
        Path("scraper_28hse/data/listings_28hse.csv"),
    ]
    for p in possible_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    estate_name = row.get("estate_name", "")
                    if estate_name:
                        listings[estate_name] = row
            break
    return listings


@router.post("/match/estates")
def match_estates(request: MatchEstatesRequest):
    """模組5：配對屋苑 — 以 estates 為底，整合 listings 價格信息"""
    profile = request.user_profile
    estates = load_estates()
    listings = load_listings()  # 載入在售物業

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
            match_result = run_single_match(meta)
            
            # === Module 5 整合：檢查是否有在售物業 ===
            estate_name = estate.get("name", "")
            listing_info = listings.get(estate_name)
            
            result_item = {
                "estate": estate_name,
                "district": estate.get("district", ""),
                "facing": estate["facing"],
                "original_facing": estate.get("original_facing", ""),
                "year_built": int(estate.get("year_built", 0)),
                "yun": estate.get("yun", ""),
                "property_type": estate.get("property_type", ""),
                "final_score": match_result["final_score"],
                "rating": match_result["rating"],
                "score_breakdown": match_result["score_breakdown"],
                "flags": match_result["flags"],
                "rationale": match_result["ai_rationale"]
            }
            
            # 如果有在售物業，顯示價格；否則顯示「暫無在售」
            if listing_info:
                result_item["listing_status"] = "有在售"
                result_item["listing_price"] = listing_info.get("price", "N/A")
                result_item["listing_area"] = listing_info.get("area", "N/A")
                result_item["listing_url"] = listing_info.get("url", "")
            else:
                result_item["listing_status"] = "暫無在售"
                result_item["listing_price"] = None
                result_item["listing_area"] = None
            
            results.append(result_item)
        except Exception as e:
            print(f"計算錯誤 {estate.get('name')}: {e}")

    results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = results[:request.top_n]

    # 統計：有在售 vs 無在售
    with_listings = sum(1 for r in results if r["listing_status"] == "有在售")
    without_listings = len(results) - with_listings

    return {
        "status": "success",
        "module": "模組5 - 配對屋苑（整合estates+listings）",
        "total_estates": len(results),
        "with_listings": with_listings,
        "without_listings": without_listings,
        "top_results": top_results,
        "all_results": results
    }
