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
    max_price: Optional[int] = Field(None, description="最高預算（萬港幣）")
    preferred_districts: Optional[List[str]] = Field(None, description="偏好地區（如 ['西半山','中半山']），不填則不限制")


class MatchListingsRequest(BaseModel):
    user_profile: UserProfile
    top_n: int = Field(default=15, description="返回前N個樓盤")
    call_buy_threshold: int = Field(default=70, description="觸發叫買市場的分數閾值")


# 朝向到24山向映射表（列表页用：爬取的朝向是"向東/向東南"等）
# ⚠️ 坐向 = 背靠山向 + 面向山向，例如：向南 = 坐北朝南 = 子山午向
# 朝向为8个基本方向（東/南/西/北/東南/東北/西南/西北），24山向精度需详情确认
# "向西南" = 面向西南 = 坐东北向西南 = 艮山坤向
# "向东北" = 面向东北 = 坐西南向东北 = 坤山艮向（需FLYING_STAR_TABLE支持）
DIRECTION_TO_FACING = {
    # 精确方向 -> 首选坐向（24山向）
    "向東": "卯山酉向",
    "向南": "子山午向",
    "向西": "酉山卯向",
    "向北": "午山子向",
    "向東南": "巽山乾向",
    "向東北": "坤山艮向",   # 修正：面向东北=坐西南向东北=坤山艮向（正确！）
    "向西南": "艮山坤向",   # 修正：面向西南=坐东北向西南=艮山坤向（正确！）
    "向西北": "乾山巽向",
    # 简写（无"向"前缀）
    "東": "卯山酉向",
    "南": "子山午向",
    "西": "酉山卯向",
    "北": "午山子向",
    "東南": "巽山乾向",
    "東北": "坤山艮向",
    "西南": "艮山坤向",
    "西北": "乾山巽向",
    # estates.csv 格式（"朝"前缀）
    "朝東": "卯山酉向",
    "朝南": "子山午向",
    "朝西": "酉山卯向",
    "朝北": "午山子向",
    "朝東南": "巽山乾向",
    "朝東北": "艮山坤向",
    "朝西南": "艮山坤向",
    "朝西北": "乾山巽向",
}



def load_estate_years():
    """从 estates_28hse.csv 加载屋苑名称 -> 年份映射 (C方案)"""
    estate_years = {}
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
                name = row.get("name", "").strip()
                year = row.get("year_built", "").strip()
                if name and year:
                    try:
                        estate_years[name] = int(year)
                    except ValueError:
                        pass
    return estate_years


def load_listings():
    """载入楼盘数据，支持朝向映射和年份匹配"""
    listings = []
    estate_years = load_estate_years()
    possible_paths = [
        Path(__file__).parent / ".." / "scraper_28hse" / "data" / "listings_28hse.csv",
        Path(__file__).parent / ".." / ".." / "scraper_28hse" / "data" / "listings_28hse.csv",
        Path("scraper_28hse/data/listings_28hse.csv"),
        Path("../scraper_28hse/data/listings_28hse.csv"),
        Path("../../scraper_28hse/data/listings_28hse.csv"),
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
                raw_facing = row.get("facing", "").strip()
                mapped_facing = DIRECTION_TO_FACING.get(raw_facing, raw_facing)
                
                # 只保留支持的坐向
                if mapped_facing in SUPPORTED_FACINGS:
                    row["facing"] = mapped_facing
                    row["original_facing"] = raw_facing
                    
                    # C方案：用屋苑名称匹配年份
                    estate_name = row.get("estate", "").strip()
                    if estate_name and estate_name in estate_years:
                        row["year_built"] = str(estate_years[estate_name])
                    
                    # price_raw -> price_hkd (万港币)
                    price_raw = row.get("price_raw", "").strip()
                    if price_raw and price_raw != "面議":
                        try:
                            row["price_hkd"] = str(int(price_raw) * 10000)
                            row["price_display"] = f"{price_raw}万"
                        except ValueError:
                            row["price_hkd"] = ""
                            row["price_display"] = price_raw
                    else:
                        row["price_hkd"] = ""
                        row["price_display"] = price_raw or "面议"
                    
                    listings.append(row)
    return listings


@router.post("/match/listings")
def match_listings(request: MatchListingsRequest):
    """模組3：配對物業 — 批量匹配，支持叫買市場"""
    profile = request.user_profile
    listings = load_listings()

    results = []
    # Step 2: 遍历匹配的listing，逐一打分
    for listing in listings:
            # --- 價格過濾 ---
            if profile.max_price is not None and listing.get("price_hkd"):
                try:
                    price = int(listing["price_hkd"])
                    if price > profile.max_price * 10000:
                        continue
                except ValueError:
                    pass
            # 如果没有价格信息，不过滤（保留所有）
            # --- /價格過濾 ---
            
            # --- 地區偏好加分 ---
            district_boost = 0
            if profile.preferred_districts and listing.get("district"):
                district = listing["district"].strip()
                for pref in profile.preferred_districts:
                    if pref in district or district in pref:
                        district_boost = 3  # 偏好地区加分3分
                        break
            # --- /地區偏好加分 ---

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
                match_result = run_single_match(meta)
                
                # 應用地區偏好加分
                final_score = match_result["final_score"] + district_boost
                final_score = min(100, round(final_score, 1))
                
                results.append({
                    "title": listing.get("title", ""),
                    "estate": listing.get("estate", ""),
                    "district": listing.get("district", ""),
                    "facing": listing["facing"],
                    "original_facing": listing.get("original_facing", ""),
                    "price_raw": listing.get("price_raw", ""),
                    "price_hkd": listing.get("price_hkd", ""),
                    "price_display": listing.get("price_display", ""),
                    "build_area": listing.get("build_area", ""),
                    "usable_area": listing.get("usable_area", ""),
                    "rooms": listing.get("rooms", ""),
                    "unit_info": listing.get("unit_info", ""),
                    "year_built": listing.get("year_built", ""),
                    "agent": listing.get("agent", ""),
                    "final_score": final_score,
                    "rating": match_result["rating"],
                    "score_breakdown": match_result["score_breakdown"],
                    "flags": match_result["flags"],
                    "rationale": match_result["ai_rationale"],
                    "district_boost": district_boost
                })
            except Exception as e:
                print(f"計算錯誤 {listing.get('title')}: {e}")

    results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = results[:request.top_n]

    # 叫買市場判斷：高分樓盤不足（<5個）或完全沒有（>=閾值）時觸發
    high_score = [r for r in results if r["final_score"] >= request.call_buy_threshold]
    call_buy_triggered = len(high_score) < 5  # 高分不足5個即觸發叫買

    call_buy_profile = None
    if call_buy_triggered and results:
        top5 = results[:5]
        # 安全計算樓齡範圍（過濾有效年份）
        valid_years = []
        for r in top5:
            yb = r.get("year_built")
            if yb and str(yb).strip():
                try:
                    valid_years.append(int(yb))
                except ValueError:
                    pass
        if valid_years:
            age_range = f"{2026 - max(valid_years)}-{2026 - min(valid_years)}年"
        else:
            age_range = "不詳（建議查詢詳情）"
        
        # 分析偏好
        district_pref = list(set([r["district"] for r in top5]))
        facing_pref = list(set([r["facing"] for r in top5]))
        
        call_buy_profile = {
            "facing": facing_pref,
            "district": district_pref,
            "age_range": age_range,
            "note": "叫買市場已觸發：高分匹配樓盤不足，建議擴大搜尋範圍或調整偏好"
        }

    return {
        "status": "success",
        "module": "模組3 - 配對物業",
        "total_listings": len(results),
        "filters_applied": {
            "max_price": profile.max_price,
            "preferred_districts": profile.preferred_districts,
        },
        "top_results": top_results,
        "call_buy_market": {
            "triggered": call_buy_triggered,
            "threshold": request.call_buy_threshold,
            "high_score_count": len(high_score),
            "anonymous_profile": call_buy_profile
        },
        "all_results": results
    }
