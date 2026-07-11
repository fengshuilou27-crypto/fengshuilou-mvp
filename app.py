from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import csv
import json
import os
import re
import logging
import time
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 版本號
VERSION = "3.6.7"

# ===== 安全中間件：API 限流 =====
class RateLimiter:
    """簡易內存限流器（基於 IP）—— Render 無狀態實例已足夠，日後可遷移至 Redis"""
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._storage = defaultdict(list)  # ip -> [timestamp, ...]
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        # 清理過期記錄
        self._storage[client_ip] = [
            t for t in self._storage[client_ip]
            if now - t < self.window
        ]
        if len(self._storage[client_ip]) >= self.max_requests:
            return False
        self._storage[client_ip].append(now)
        return True

rate_limiter = RateLimiter(max_requests=60, window_seconds=60)

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """添加安全響應頭"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """API 限流中間件"""
    async def dispatch(self, request: Request, call_next):
        # 靜態文件和合法頁面不限流
        if request.url.path.startswith("/static") or request.method == "OPTIONS":
            return await call_next(request)
        
        # 獲取客戶端 IP（Render 會透過 X-Forwarded-For）
        client_ip = request.headers.get("x-forwarded-for", request.client.host)
        if client_ip and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content='{"detail":"Too many requests. Please try again later."}',
                status_code=429,
                media_type="application/json"
            )
        
        return await call_next(request)

from data.flying_star import get_yun, SUPPORTED_FACINGS, FLYING_STAR_TABLE
from models.flying_star_analysis import analyze_flying_star
from models.zero_main_god import analyze_zero_main_god
from models.sha_assessment import analyze_sha
from models.bazi_matching import analyze_bazi
from models.bagua_matching import analyze_bagua, analyze_bagua_dual
from models.goal_matching import analyze_goal
from models.match_result import aggregate_match_result

from routers.geo import router as geo_router

from data.fxti_bazi import get_innate_wuxing
from data.fxti_questionnaire import get_questionnaire, calculate_acquired_wuxing
from data.fxti_profile import determine_profile, synthesize_result, ALL_PROFILES
from data.fxti_relationship import analyze_relationship

app = FastAPI(
    title="AI風水樓盤匹配系統",
    description="v3.6 - 24山向飛星表 + 八宅遊年 + 納甲樓層 + 羅盤工具 + 風水集成層 + 數據庫適配",
    version="3.6.7"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fengshuilou.com",
        "https://www.fengshuilou.com",
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(geo_router)


class GoalItem(BaseModel):
    goal: str = Field(..., description="目標名稱")
    priority: int = Field(1, description="優先級：1=主, 2=次, 3=第三")


class RequestMeta(BaseModel):
    eval_year: int = Field(default=2026, description="評估年份")
    user_gender: str = Field(..., description="性別：男/女")
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="出生時間 HH:MM")
    birth_place: Optional[str] = Field(None, description="出生地")
    user_job: Optional[str] = Field(None, description="職業")
    floor_preference: Optional[str] = Field(None, description="樓層偏好")
    household_weight_mode: Optional[str] = Field("balanced", description="家庭權重模式")
    # 同住人（雙人模式）
    cohabitant_enabled: bool = Field(False, description="啟用同住人雙人模式")
    cohabitant_gender: Optional[str] = Field(None, description="同住人性別：男/女")
    cohabitant_birth_date: Optional[str] = Field(None, description="同住人出生日期 YYYY-MM-DD")
    cohabitant_birth_time: Optional[str] = Field(None, description="同住人出生時間 HH:MM")
    cohabitant_user_job: Optional[str] = Field(None, description="同住人職業")
    cohabitant_weight_ratio: float = Field(0.5, description="同住人比例：0.5=50/50, 0.7=70/30, 0.3=30/70")
    # 樓盤資料
    building_year: int = Field(..., description="建築年份")
    building_facing: str = Field(..., description="坐向：子山午向/丑山未向/乾山巽向/卯山酉向等")
    floor_number: int = Field(..., description="樓層")
    address: Optional[str] = Field(None, description="物業地址")
    # 目標（多選）
    goals: List[GoalItem] = Field(..., description="目標列表，最多3個")
    north_has_water: bool = Field(False, description="北側有水")
    south_has_mountain: bool = Field(False, description="南側有山")
    detected_shas: Optional[List[str]] = Field(default=[], description="已知煞氣")
    estate_name: Optional[str] = Field(None, description="屋苑名稱（用於GIS風水分析）")
    property_features: Optional[dict] = Field(default=None, description="物業特徵：海景/山景/裝修/交通等")
    room_layout: Optional[dict] = Field(default=None, description="房間方位佈局：{\"大門\":\"南\",\"臥室\":\"東\",\"廚房\":\"北\",\"廁所\":\"西\"}")


class EvaluateRequest(BaseModel):
    request_meta: RequestMeta


class UserProfile(BaseModel):
    eval_year: int = Field(default=2026, description="評估年份")
    user_gender: str = Field(..., description="性別：男/女")
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_time: Optional[str] = Field(None, description="出生時間 HH:MM")
    birth_place: Optional[str] = Field(None, description="出生地")
    user_job: Optional[str] = Field(None, description="職業")
    floor_number: Optional[int] = Field(None, description="樓層號碼（可選）")
    # 同住人
    cohabitant_enabled: bool = Field(False, description="啟用同住人雙人模式")
    cohabitant_gender: Optional[str] = Field(None, description="同住人性別")
    cohabitant_birth_date: Optional[str] = Field(None, description="同住人出生日期")
    cohabitant_birth_time: Optional[str] = Field(None, description="同住人出生時間")
    cohabitant_user_job: Optional[str] = Field(None, description="同住人職業")
    cohabitant_weight_ratio: float = Field(0.5, description="同住人比例")
    # 目標
    goals: List[GoalItem] = Field(..., description="目標列表")
    household_weight_mode: Optional[str] = Field("balanced", description="家庭權重模式")


class PropertyFilter(BaseModel):
    price_min: Optional[int] = Field(None, description="最低價格（萬）")
    price_max: Optional[int] = Field(None, description="最高價格（萬）")
    districts: Optional[List[str]] = Field(None, description="地區列表")
    facings: Optional[List[str]] = Field(None, description="坐向列表")
    floor_min: Optional[int] = Field(None, description="最低樓層")
    floor_max: Optional[int] = Field(None, description="最高樓層")


class SearchPropertiesRequest(BaseModel):
    user_profile: UserProfile
    filters: PropertyFilter
    top_n: int = Field(default=15, description="返回前N個物業")


class EvaluateFromDbRequest(BaseModel):
    user_profile: UserProfile
    property_id: str = Field(..., description="物業ID")


class MatchEstatesRequest(BaseModel):
    user_profile: UserProfile
    top_n: int = Field(default=3, description="返回前N個屋苑")


class MatchListingsRequest(BaseModel):
    user_profile: UserProfile
    top_n: int = Field(default=15, description="返回前N個樓盤")
    call_buy_threshold: int = Field(default=50, description="觸發叫買市場的分數閾值")
    filters: Optional[PropertyFilter] = Field(None, description="物業篩選條件")


# FXTI Models
class FXTICalculateRequest(BaseModel):
    birth_year: int = Field(..., description="出生年")
    birth_month: int = Field(..., description="出生月")
    birth_day: int = Field(..., description="出生日")
    birth_hour: Optional[int] = Field(None, description="出生時（0-23）")
    gender: Optional[str] = Field(None, description="性別 male/female")
    occupation: Optional[str] = Field(None, description="職業")
    answers: List[int] = Field(..., description="10題問卷答案，每題0-4")


class FXTIResultResponse(BaseModel):
    id: str
    profile: Dict[str, Any]
    final_wuxing: Dict[str, float]
    innate_wuxing: Dict[str, float]
    acquired_wuxing: Dict[str, float]
    bazi: Dict[str, Any]


class FXTIPersonInput(BaseModel):
    fxti_id: Optional[str] = Field(None, description="FXTI結果ID")
    birth_year: Optional[int] = Field(None, description="出生年")
    birth_month: Optional[int] = Field(None, description="出生月")
    birth_day: Optional[int] = Field(None, description="出生日")
    birth_hour: Optional[int] = Field(None, description="出生時")
    gender: Optional[str] = Field(None, description="性別")
    occupation: Optional[str] = Field(None, description="職業")
    answers: Optional[List[int]] = Field(None, description="10題問卷答案")


class FXTIRelationshipRequest(BaseModel):
    person_a: FXTIPersonInput
    person_b: FXTIPersonInput


# FXTI in-memory storage
fxti_results_db: Dict[str, dict] = {}


def _find_data_path(filename: str) -> Path:
    """Robustly find a data file in the project directory tree."""
    script_dir = Path(__file__).resolve().parent
    # Strategy 0: local data/ directory (same folder as app.py)
    local_data = script_dir / "data" / filename
    if local_data.exists():
        return local_data
    # Strategy 1: sibling directory (ai-fengshui-mvp/../scraper_28hse)
    candidates = [
        script_dir / ".." / "scraper_28hse" / "data" / filename,
        script_dir / ".." / ".." / "scraper_28hse" / "data" / filename,
        script_dir / ".." / ".." / ".." / "scraper_28hse" / "data" / filename,
    ]
    # Strategy 2: relative to cwd (for running from workspace root)
    cwd = Path.cwd()
    for depth in range(0, 4):
        candidates.append(cwd / (".." * depth) / "scraper_28hse" / "data" / filename)
    # Strategy 3: search upward from script_dir for a directory containing scraper_28hse
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


# v3.5: 數據庫訪問層（支持 Neon Postgres + CSV 回退）
from data.db_access import (
    load_estates as _db_load_estates,
    load_listings as _db_load_listings,
    load_estates_unified as _db_load_estates_unified,
    get_db_status
)


def load_estates():
    """載入屋苑數據（數據庫優先，CSV回退）"""
    # 嘗試從數據庫加載
    db_estates = _db_load_estates()
    if db_estates:
        logger.info("Estates loaded from database: %d records", len(db_estates))
        return db_estates

    # 回退到 CSV
    estates = []
    data_path = _find_data_path("estates_28hse.csv")
    if data_path:
        logger.info("Loading estates data from CSV: %s", data_path)
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("facing") in SUPPORTED_FACINGS:
                    estates.append(row)
        logger.info("Estates loaded from CSV: %d records", len(estates))
    else:
        logger.warning("estates_28hse.csv not found. Ensure scraper_28hse/data/estates_28hse.csv exists.")
    return estates


LISTINGS_HEADERS = [
    "title", "district", "estate", "unit_info", "price", "price_raw",
    "build_area", "usable_area", "rooms", "facing", "property_type",
    "decoration", "views", "features", "agent", "posted_time", "url",
    "year_built", "yun", "estate_facing"
]


def load_listings():
    """載入樓盤數據（數據庫優先，CSV回退）"""
    # 嘗試從數據庫加載
    db_listings = _db_load_listings()
    if db_listings:
        logger.info("Listings loaded from database: %d records", len(db_listings))
        return db_listings

    # 回退到 CSV
    listings = []
    data_path = _find_data_path("listings_28hse.csv")
    if data_path:
        logger.info("Loading listings data from CSV: %s", data_path)
        with open(data_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("facing") in SUPPORTED_FACINGS:
                    listings.append(row)
        logger.info("Listings loaded from CSV: %d records", len(listings))
    else:
        # 自動在 scraper_28hse/data/ 創建空 listings 文件
        scraper_data = _find_data_path("estates_28hse.csv")
        if scraper_data:
            listings_dir = scraper_data.parent
            empty_listings = listings_dir / "listings_28hse.csv"
            logger.warning("listings_28hse.csv missing, creating empty file: %s", empty_listings)
            with open(empty_listings, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=LISTINGS_HEADERS)
                writer.writeheader()
            logger.info("Empty listings_28hse.csv created. Populate with real data to use Module 3.")
        else:
            logger.warning("listings_28hse.csv not found and scraper_28hse/data directory not located.")
    return listings


ALL_LISTINGS = load_listings()
ALL_ESTATES = load_estates()

# Build estate year lookup from estates_unified.csv for listings with missing year_built
ESTATE_YEAR_LOOKUP = {}
for estate in ALL_ESTATES:
    name = estate.get("name", "").strip()
    year = estate.get("building_year", "")
    if name and year and str(year).isdigit():
        ESTATE_YEAR_LOOKUP[name] = int(year)

logger.info("ESTATE_YEAR_LOOKUP built: %d estates", len(ESTATE_YEAR_LOOKUP))


def _parse_goals(goals):
    """解析目標列表，向後兼容字符串"""
    if isinstance(goals, str):
        return [{"goal": goals, "priority": 1}]
    if isinstance(goals, list) and len(goals) > 0:
        if isinstance(goals[0], dict):
            return goals
        # Handle GoalItem objects (Pydantic models) and strings
        if hasattr(goals[0], 'goal'):
            return [{"goal": g.goal, "priority": getattr(g, 'priority', 1)} for g in goals]
        return [{"goal": g, "priority": 1} for g in goals]
    return []


def _run_single_person_match(birth_date, gender, birth_time, user_job, building_year, building_facing, floor_number, goals, detected_shas, north_has_water, south_has_mountain, eval_year=2026, address=None, property_features=None, estate_name=None, room_layout=None):
    """單人匹配計算"""
    # 1. 飛星分析
    flying_star_result = analyze_flying_star(
        building_year=building_year,
        building_facing=building_facing,
        eval_year=eval_year
    )

    # 2. 零正神
    zero_main_god_result = analyze_zero_main_god(
        building_year=building_year,
        building_facing=building_facing,
        north_has_water=north_has_water,
        south_has_mountain=south_has_mountain
    )

    # 3. 煞氣（含飛星盤自動推導刑煞）
    sha_result = analyze_sha(
        detected_shas=detected_shas or [],
        flying_star_pan=flying_star_result if flying_star_result.get("status") == "success" else None
    )

    # 4. 八字（含職業 + v2.5 納甲樓層五行）
    bazi_result = analyze_bazi(
        birth_date=birth_date,
        floor_number=floor_number,
        birth_time=birth_time,
        user_job=user_job,
        building_facing=building_facing
    )

    # 5. 八宅
    bagua_result = analyze_bagua(
        birth_date=birth_date,
        gender=gender,
        building_facing=building_facing
    )

    # 6. 目標（多選）
    goal_result = analyze_goal(
        building_year=building_year,
        building_facing=building_facing,
        goals=goals
    )

    # 7. 聚合
    match_result = aggregate_match_result(
        flying_star_result=flying_star_result,
        zero_main_god_result=zero_main_god_result,
        sha_result=sha_result,
        bazi_result=bazi_result,
        bagua_result=bagua_result,
        goal_result=goal_result,
        district=address,
        building_year=building_year,
        eval_year=eval_year,
        property_features=property_features,
        floor_number=floor_number,
        building_facing=building_facing,
        estate_name=estate_name
    )

    # 8. 填充樓盤信息
    if address:
        match_result["property_info"] = {"address": address}

    # 9. 雙周期飛星詳細報告
    dual_period = flying_star_result.get("dual_period", {})
    building_yun = dual_period.get("building_yun", flying_star_result.get("yun", "未知"))
    current_yun = dual_period.get("current_yun", building_yun)

    match_result["dual_period_flying_star"] = {
        "building_yun": building_yun,
        "current_yun": current_yun,
        "dual_period_enabled": dual_period.get("enabled", False),
        "building_weight": dual_period.get("building_weight", 1.0),
        "current_weight": dual_period.get("current_weight", 0.0),
        "pan_type_change": dual_period.get("pan_type_change", False),
        "building_yun_analysis": {
            "pan_type": flying_star_result.get("pan_type"),
            "score": flying_star_result.get("building_score", flying_star_result.get("score")),
            "mountain_stars": flying_star_result.get("mountain_stars"),
            "facing_stars": flying_star_result.get("facing_stars"),
            "auspicious_combos": flying_star_result.get("auspicious_combos", []),
            "inauspicious_combos": flying_star_result.get("inauspicious_combos", [])
        },
        "current_yun_analysis": {
            "pan_type": flying_star_result.get("current_pan_type"),
            "score": flying_star_result.get("current_score"),
            "mountain_stars": flying_star_result.get("current_mountain_stars"),
            "facing_stars": flying_star_result.get("current_facing_stars"),
            "auspicious_combos": flying_star_result.get("current_auspicious_combos", []),
            "inauspicious_combos": flying_star_result.get("current_inauspicious_combos", [])
        } if dual_period.get("enabled") else None,
        "yun_transition_note": dual_period.get("note", f"該樓宇建於{building_yun}，當前為{current_yun}。")
    }

    # 10. v3.6 擴展風水分析（八宅遊年 + 納甲樓層 + 羅盤工具）
    try:
        from data.fengshui_integration import get_extended_fengshui
        extended = get_extended_fengshui(
            birth_date=birth_date,
            gender=gender,
            floor_number=floor_number,
            building_facing=building_facing,
            building_year=building_year,
            room_layout=room_layout
        )
        match_result["fengshui_extended"] = extended
        
        # 將風水精細度加分加到總分（上限 100）
        bonus = extended.get("fengshui_bonus", 0)
        if bonus > 0:
            new_score = match_result.get("final_score", 0) + bonus
            match_result["final_score"] = round(min(new_score, 100.0), 1)
            match_result["score_breakdown"]["風水精細度"] = round(bonus, 1)
    except Exception as e:
        logger.warning("Extended fengshui analysis failed: %s", e)
        match_result["fengshui_extended"] = {"enabled": False, "error": str(e)}

    return match_result


def run_single_match(meta: RequestMeta, district: str = None):
    """執行單次匹配計算（支持單人/雙人）v3.6.5 修復版"""
    goals = _parse_goals(meta.goals)
    
    # 如果外部傳入 district，覆蓋 meta.address
    if district and not meta.address:
        meta.address = district

    # v3.6.5: 根據 household_weight_mode 自動設置權重
    weight_mode = getattr(meta, 'household_weight_mode', 'balanced')
    if weight_mode == 'single':
        # 單人模式：100% 主用戶
        meta.cohabitant_enabled = False
        meta.cohabitant_weight_ratio = 0.0
    elif weight_mode == 'family':
        # 家庭模式：60% 主用戶 + 40% 同住人
        meta.cohabitant_weight_ratio = 0.4
    elif weight_mode == 'balanced':
        # 二人模式：50/50
        meta.cohabitant_weight_ratio = 0.5
    # else: 使用用戶自定義的 cohabitant_weight_ratio

    # v3.6.5: 檢查同住人資料是否完整，不完整則自動回退到單人模式（不報錯）
    partner_data_complete = (
        meta.cohabitant_enabled and
        meta.cohabitant_birth_date and
        meta.cohabitant_gender and
        meta.cohabitant_birth_date.strip() != '' and
        meta.cohabitant_gender.strip() != ''
    )

    if partner_data_complete:
        # 雙人模式：宅不變，人加權
        weight_a = 1 - meta.cohabitant_weight_ratio
        weight_b = meta.cohabitant_weight_ratio

        # 分別計算兩人
        result_a = _run_single_person_match(
            birth_date=meta.birth_date, gender=meta.user_gender,
            birth_time=meta.birth_time, user_job=meta.user_job,
            building_year=meta.building_year, building_facing=meta.building_facing,
            floor_number=meta.floor_number, goals=goals,
            detected_shas=meta.detected_shas,
            north_has_water=meta.north_has_water,
            south_has_mountain=meta.south_has_mountain,
            eval_year=meta.eval_year,
            address=meta.address,
            property_features=meta.property_features,
            estate_name=meta.estate_name,
            room_layout=meta.room_layout
        )

        result_b = _run_single_person_match(
            birth_date=meta.cohabitant_birth_date, gender=meta.cohabitant_gender,
            birth_time=meta.cohabitant_birth_time, user_job=meta.cohabitant_user_job,
            building_year=meta.building_year, building_facing=meta.building_facing,
            floor_number=meta.floor_number, goals=goals,
            detected_shas=meta.detected_shas,
            north_has_water=meta.north_has_water,
            south_has_mountain=meta.south_has_mountain,
            eval_year=meta.eval_year,
            address=meta.address,
            property_features=meta.property_features,
            estate_name=meta.estate_name,
            room_layout=meta.room_layout
        )

        # 八宅雙人分析（專門用於對照表）
        try:
            bagua_dual = analyze_bagua_dual(
                meta.birth_date, meta.user_gender,
                meta.cohabitant_birth_date, meta.cohabitant_gender,
                meta.building_facing,
                weight_a=weight_a, weight_b=weight_b
            )
        except Exception as e:
            logger.warning("Bagua dual analysis failed: %s", e)
            bagua_dual = {"comparison_table": None}

        # 合併分數：宅客觀分不變，人主觀分加權
        merged = dict(result_a)  # 複製A的結果作為基礎

        # v3.6.5: 安全訪問 score_breakdown，避免 KeyError
        sb_a = result_a.get("score_breakdown", {})
        sb_b = result_b.get("score_breakdown", {})
        
        # 人主觀分：八字、八宅、目標（使用 .get() 安全訪問）
        bazi_merged = round(
            sb_a.get("八字", 0) * weight_a + sb_b.get("八字", 0) * weight_b, 1
        )
        bagua_merged = round(
            sb_a.get("八宅", 0) * weight_a + sb_b.get("八宅", 0) * weight_b, 1
        )
        goal_merged = round(
            sb_a.get("目標", 0) * weight_a + sb_b.get("目標", 0) * weight_b, 1
        )

        merged["score_breakdown"]["八字"] = bazi_merged
        merged["score_breakdown"]["八宅"] = bagua_merged
        merged["score_breakdown"]["目標"] = goal_merged

        # 重新計算總分
        total = sum(merged["score_breakdown"].values())
        merged["final_score"] = max(0, min(100, round(total, 1)))

        # 更新評級
        fs = merged["final_score"]
        if fs >= 85: merged["rating"] = "★★★★★ 高分區間（需專業師傅確認）"
        elif fs >= 70: merged["rating"] = "★★★★☆ 中高分區間（需專業師傅確認）"
        elif fs >= 60: merged["rating"] = "★★★☆☆ 中分區間（需專業師傅確認）"
        elif fs >= 45: merged["rating"] = "★★☆☆☆ 中低分區間（需專業師傅確認）"
        elif fs >= 30: merged["rating"] = "★☆☆☆☆ 低分區間（需專業師傅確認）"
        else: merged["rating"] = "☆☆☆☆☆ 極低分區間（需專業師傅確認）"

        # 更新理由
        rationale_a = result_a.get("ai_rationale", "")
        rationale_b = result_b.get("ai_rationale", "")
        merged["ai_rationale"] = (
            f"【雙人模式】A({meta.user_gender},{meta.birth_date})權重{weight_a:.0%}，"
            f"B({meta.cohabitant_gender},{meta.cohabitant_birth_date})權重{weight_b:.0%}。\n"
            f"{rationale_a}\n"
            f"{rationale_b}"
        )

        # 合併八字信息
        merged["bazi_data"] = {
            "person_a": result_a.get("bazi_data", {}),
            "person_b": result_b.get("bazi_data", {})
        }

        # 八宅對照表
        merged["bagua_comparison"] = bagua_dual.get("comparison_table")
        merged["is_dual"] = True
        merged["weight_a"] = weight_a
        merged["weight_b"] = weight_b

        return merged
    else:
        # 單人模式（或同住人資料不完整自動回退）
        if meta.cohabitant_enabled and not partner_data_complete:
            logger.info("Partner data incomplete, falling back to single mode")
        return _run_single_person_match(
            birth_date=meta.birth_date, gender=meta.user_gender,
            birth_time=meta.birth_time, user_job=meta.user_job,
            building_year=meta.building_year, building_facing=meta.building_facing,
            floor_number=meta.floor_number, goals=goals,
            detected_shas=meta.detected_shas,
            north_has_water=meta.north_has_water,
            south_has_mountain=meta.south_has_mountain,
            eval_year=meta.eval_year,
            address=meta.address,
            property_features=meta.property_features,
            estate_name=meta.estate_name,
            room_layout=meta.room_layout
        )


@app.get("/logo.png")
def serve_logo():
    """提供 logo 圖片"""
    logo_path = Path("static/logo.png")
    if logo_path.exists():
        return FileResponse(str(logo_path), media_type="image/png")
    # 回退到 SVG
    svg_path = Path("frontend/public/logo.svg")
    if svg_path.exists():
        return FileResponse(str(svg_path), media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Logo not found")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/index.html")
def index_html():
    return FileResponse("static/index.html")


@app.get("/module1")
def module1():
    return FileResponse("static/module1.html")


@app.get("/module1.html")
def module1_html():
    return FileResponse("static/module1.html")


@app.get("/module2")
def module2():
    return FileResponse("static/module2.html")


@app.get("/module2.html")
def module2_html():
    return FileResponse("static/module2.html")


@app.get("/module3")
def module3():
    return FileResponse("static/module3.html")


@app.get("/module3.html")
def module3_html():
    return FileResponse("static/module3.html")


@app.get("/flying-star")
def flying_star_page():
    return FileResponse("static/flying-star.html")


@app.get("/fxti")
def fxti():
    return FileResponse("static/fxti/index.html")


@app.get("/fxti/index.html")
def fxti_index():
    return FileResponse("static/fxti/index.html")


@app.get("/fxti/result.html")
def fxti_result_html():
    return FileResponse("static/fxti/result.html")


@app.get("/fxti/share.html")
def fxti_share_html():
    return FileResponse("static/fxti/share.html")


@app.get("/disclaimer")
def disclaimer_page():
    return FileResponse("static/disclaimer.html")


@app.get("/privacy")
def privacy_page():
    return FileResponse("static/privacy.html")


@app.get("/terms")
def terms_page():
    return FileResponse("static/terms.html")


@app.post("/api/evaluate")
def evaluate(request: EvaluateRequest):
    """模組1：自測現有住所 — 單一評估"""
    meta = request.request_meta
    match_result = run_single_match(meta)
    return {"status": "success", "match_result": match_result}


@app.post("/api/search-properties")
def search_properties(request: SearchPropertiesRequest):
    """模組3：根據用戶偏好篩選物業並匹配"""
    profile = request.user_profile
    filters = request.filters

    listings = ALL_LISTINGS

    # 應用篩選
    filtered = []
    for listing in listings:
        # 坐向篩選
        if filters.facings and listing.get("facing") not in filters.facings:
            continue
        # 地區篩選
        if filters.districts and listing.get("district") not in filters.districts:
            continue
        # 價格篩選（簡化：解析price_raw中的數字）
        if filters.price_min or filters.price_max:
            price_str = listing.get("price_raw", "")
            price_num = 0
            m = re.search(r'(\d+(?:\.\d+)?)\s*萬', price_str)
            if m:
                price_num = float(m.group(1))
            if filters.price_min and price_num < filters.price_min:
                continue
            if filters.price_max and price_num > filters.price_max:
                continue
        # 樓層篩選
        if filters.floor_min or filters.floor_max:
            floor = 10
            if listing.get("unit_info"):
                m = re.search(r'(\d+)', listing.get("unit_info", ""))
                if m:
                    floor = int(m.group(1))
            if filters.floor_min and floor < filters.floor_min:
                continue
            if filters.floor_max and floor > filters.floor_max:
                continue
        filtered.append(listing)

    results = []
    for listing in filtered:
        try:
            year = int(listing.get("year_built", 2000)) if listing.get("year_built") else 2000
            floor = 10
            if listing.get("unit_info"):
                m = re.search(r'(\d+)', listing.get("unit_info", ""))
                if m:
                    floor = int(m.group(1))

            goals = _parse_goals(profile.goals)
            meta = RequestMeta(
                eval_year=profile.eval_year,
                user_gender=profile.user_gender,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_place=profile.birth_place,
                user_job=profile.user_job,
                cohabitant_enabled=profile.cohabitant_enabled,
                cohabitant_gender=profile.cohabitant_gender,
                cohabitant_birth_date=profile.cohabitant_birth_date,
                cohabitant_birth_time=profile.cohabitant_birth_time,
                cohabitant_user_job=profile.cohabitant_user_job,
                cohabitant_weight_ratio=profile.cohabitant_weight_ratio,
                building_year=year,
                building_facing=listing["facing"],
                floor_number=floor,
                goals=goals,
                north_has_water=False,
                south_has_mountain=False,
                detected_shas=[]
            )
            match_result = run_single_match(meta)
            results.append({
                "id": f"listing_{len(results)}",
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
                "rationale": match_result["ai_rationale"],
                "match_result": match_result
            })
        except Exception as e:
            print(f"計算錯誤 {listing.get('title')}: {e}")

    results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = results[:request.top_n]

    # 分數<50或無匹配時引導叫買市場
    call_buy_triggered = len(results) == 0 or (len(top_results) > 0 and top_results[0]["final_score"] < 50)

    return {
        "status": "success",
        "module": "模組3 - 物業篩選匹配",
        "total_filtered": len(filtered),
        "matched_count": len(results),
        "top_results": top_results,
        "call_buy_market": {
            "triggered": call_buy_triggered,
            "message": "目前篩選條件下無高分匹配物業。您可以瀏覽「叫買市場」查看所有物業，或放寬篩選條件。"
        }
    }


@app.get("/api/market-list")
def market_list():
    """叫買市場：列出所有物業"""
    listings = ALL_LISTINGS
    results = []
    for listing in listings:
        year = listing.get("year_built", "")
        facing = listing.get("facing", "")
        data_confirmed = bool(year and facing in SUPPORTED_FACINGS)
        results.append({
            "id": f"listing_{len(results)}",
            "title": listing.get("title", ""),
            "estate": listing.get("estate", ""),
            "district": listing.get("district", ""),
            "facing": facing,
            "price_raw": listing.get("price_raw", ""),
            "build_area": listing.get("build_area", ""),
            "usable_area": listing.get("usable_area", ""),
            "rooms": listing.get("rooms", ""),
            "unit_info": listing.get("unit_info", ""),
            "year_built": year,
            "agent": listing.get("agent", ""),
            "data_confirmed": data_confirmed,
            "data_note": "" if data_confirmed else "資料待確認（坐向或年份缺失）"
        })
    return {"status": "success", "total": len(results), "listings": results}


@app.post("/api/evaluate-from-db")
def evaluate_from_db(request: EvaluateFromDbRequest):
    """從數據庫選擇物業進行自測（跳轉模組1邏輯）"""
    profile = request.user_profile
    property_id = request.property_id

    # 查找物業
    listing = None
    for l in ALL_LISTINGS:
        if f"listing_{ALL_LISTINGS.index(l)}" == property_id:
            listing = l
            break

    if not listing:
        raise HTTPException(status_code=404, detail="物業未找到")

    year = int(listing.get("year_built", 2000)) if listing.get("year_built") else 2000
    floor = 10
    if listing.get("unit_info"):
        m = re.search(r'(\d+)', listing.get("unit_info", ""))
        if m:
            floor = int(m.group(1))

    goals = _parse_goals(profile.goals)
    meta = RequestMeta(
        eval_year=profile.eval_year,
        user_gender=profile.user_gender,
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        birth_place=profile.birth_place,
        user_job=profile.user_job,
        cohabitant_enabled=profile.cohabitant_enabled,
        cohabitant_gender=profile.cohabitant_gender,
        cohabitant_birth_date=profile.cohabitant_birth_date,
        cohabitant_birth_time=profile.cohabitant_birth_time,
        cohabitant_user_job=profile.cohabitant_user_job,
        cohabitant_weight_ratio=profile.cohabitant_weight_ratio,
        building_year=year,
        building_facing=listing["facing"],
        floor_number=floor,
        goals=goals,
        north_has_water=False,
        south_has_mountain=False,
        detected_shas=[]
    )
    match_result = run_single_match(meta)

    return {
        "status": "success",
        "module": "模組3 - 自測",
        "property": {
            "title": listing.get("title", ""),
            "estate": listing.get("estate", ""),
            "district": listing.get("district", ""),
            "facing": listing["facing"],
            "price_raw": listing.get("price_raw", ""),
            "year_built": listing.get("year_built", ""),
            "unit_info": listing.get("unit_info", ""),
        },
        "match_result": match_result
    }


@app.post("/api/match/estates")
def match_estates(request: MatchEstatesRequest):
    """模組2：配對屋苑 — 批量匹配，返回TOP N"""
    profile = request.user_profile
    estates = ALL_ESTATES

    results = []
    for estate in estates:
        try:
            goals = _parse_goals(profile.goals)
            
            # 估算樓層：優先使用用戶輸入的樓層，其次從 total_floors 取中層，最後默認10
            user_floor = getattr(profile, 'floor_number', None)
            if user_floor and user_floor > 0:
                floor = user_floor
            else:
                total_floors = estate.get("total_floors", "")
                if total_floors and total_floors.isdigit():
                    floor = int(total_floors) // 2
                else:
                    floor = 10
            
            # 從數據提取環境特徵
            has_sea = estate.get("has_sea_view", "False").lower() == "true"
            has_mountain = estate.get("has_mountain_view", "False").lower() == "true"
            facing = estate.get("facing", "")
            north_water = has_sea and facing in ["子山午向", "癸山丁向", "丑山未向", "艮山坤向", "壬山丙向"]
            south_mountain = has_mountain and facing in ["午山子向", "丁山癸向", "未山丑向", "坤山艮向", "丙山壬向"]
            
            # 構建物業特徵
            property_features = {
                "has_sea_view": has_sea,
                "has_mountain_view": has_mountain,
                "decoration": "",  # 屋苑數據無裝修信息
                "transport_rating": 0,
                "amenities_score": 0
            }
            try:
                tr = estate.get("transport_rating", "")
                if tr and tr.isdigit():
                    property_features["transport_rating"] = int(tr)
            except:
                pass
            try:
                am = estate.get("amenities_score", "")
                if am and am.isdigit():
                    property_features["amenities_score"] = int(am)
            except:
                pass
            
            meta = RequestMeta(
                eval_year=profile.eval_year,
                user_gender=profile.user_gender,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_place=profile.birth_place,
                user_job=profile.user_job,
                cohabitant_enabled=profile.cohabitant_enabled,
                cohabitant_gender=profile.cohabitant_gender,
                cohabitant_birth_date=profile.cohabitant_birth_date,
                cohabitant_birth_time=profile.cohabitant_birth_time,
                cohabitant_user_job=profile.cohabitant_user_job,
                cohabitant_weight_ratio=profile.cohabitant_weight_ratio,
                building_year=int(estate.get("building_year", 2000)),
                building_facing=estate["facing"],
                floor_number=floor,
                goals=goals,
                north_has_water=north_water,
                south_has_mountain=south_mountain,
                detected_shas=[],
                property_features=property_features
            )
            match_result = run_single_match(meta)
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

    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:request.top_n]

    return {
        "status": "success",
        "module": "模組2 - 配對屋苑",
        "total_estates": len(results),
        "top_results": top_results,
        "all_results": results
    }


@app.post("/api/match/listings")
def match_listings(request: MatchListingsRequest):
    """模組3：配對物業 — 批量匹配，支持叫買市場"""
    profile = request.user_profile
    listings = ALL_LISTINGS

    # 應用篩選（如果提供）
    if request.filters:
        filters = request.filters
        filtered = []
        for listing in listings:
            if filters.facings and listing.get("facing") not in filters.facings:
                continue
            if filters.districts and listing.get("district") not in filters.districts:
                continue
            filtered.append(listing)
        listings = filtered

    results = []
    for listing in listings:
        try:
            # 年份提取：優先使用 year_built，其次查 estates 表，最後默認 2000
            raw_year = listing.get("year_built", "")
            if raw_year and str(raw_year).strip().isdigit():
                year = int(raw_year)
            else:
                estate_name = listing.get("estate", "").strip()
                if estate_name in ESTATE_YEAR_LOOKUP:
                    year = ESTATE_YEAR_LOOKUP[estate_name]
                    logger.debug("Filled year_built for %s from estate lookup: %d", estate_name, year)
                else:
                    year = 2000
            
            # 樓層提取：優先解析低層/中層/高層，其次提取數字
            unit_info = listing.get("unit_info", "")
            floor = 10
            if unit_info:
                if "低層" in unit_info or "低层" in unit_info:
                    floor = 5
                elif "中層" in unit_info or "中层" in unit_info:
                    floor = 10
                elif "高層" in unit_info or "高层" in unit_info:
                    floor = 20
                else:
                    m = re.search(r'(\d+)', unit_info)
                    if m:
                        floor_num = int(m.group(1))
                        # 過濾掉座號（通常小於3或介於20-100之間）
                        if 3 <= floor_num <= 80:
                            floor = floor_num
            
            # 從 views 字段推斷環境特徵
            views = listing.get("views", "")
            has_sea = "海景" in views or "臨海" in views or "海" in views
            has_mountain = "山景" in views or "園景" in views or "山" in views
            facing = listing.get("facing", "")
            north_water = has_sea and facing in ["子山午向", "癸山丁向", "丑山未向", "艮山坤向", "壬山丙向"]
            south_mountain = has_mountain and facing in ["午山子向", "丁山癸向", "未山丑向", "坤山艮向", "丙山壬向"]
            
            # 構建物業特徵
            property_features = {
                "has_sea_view": has_sea,
                "has_mountain_view": has_mountain,
                "decoration": listing.get("decoration", ""),
                "transport_rating": 0,
                "amenities_score": 0
            }
            
            goals = _parse_goals(profile.goals)
            meta = RequestMeta(
                eval_year=profile.eval_year,
                user_gender=profile.user_gender,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_place=profile.birth_place,
                user_job=profile.user_job,
                cohabitant_enabled=profile.cohabitant_enabled,
                cohabitant_gender=profile.cohabitant_gender,
                cohabitant_birth_date=profile.cohabitant_birth_date,
                cohabitant_birth_time=profile.cohabitant_birth_time,
                cohabitant_user_job=profile.cohabitant_user_job,
                cohabitant_weight_ratio=profile.cohabitant_weight_ratio,
                building_year=year,
                building_facing=listing["facing"],
                floor_number=floor,
                goals=goals,
                north_has_water=north_water,
                south_has_mountain=south_mountain,
                detected_shas=[],
                property_features=property_features
            )
            match_result = run_single_match(meta)
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
                "year_built": year,
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
        # 安全地解析 year_built
        valid_years = []
        for r in top3:
            yb = r.get('year_built', '')
            if yb and str(yb).isdigit():
                valid_years.append(int(yb))
        if valid_years:
            age_range = f"{2026 - max(valid_years)}-{2026 - min(valid_years)}年"
        else:
            age_range = "未知"
        call_buy_profile = {
            "facing": list(set([r["facing"] for r in top3])),
            "district": list(set([r["district"] for r in top3])),
            "age_range": age_range
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


@app.get("/api/supported-facings")
def get_supported_facings():
    facings_by_yun = {}
    for yun, facings in FLYING_STAR_TABLE.items():
        facings_by_yun[yun] = list(facings.keys())

    return {
        "supported": SUPPORTED_FACINGS,
        "by_yun": facings_by_yun,
        "total": len(SUPPORTED_FACINGS),
        "note": "支持以上坐向，其他坐向標註為'待確認'"
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": VERSION, "supported_facings": len(SUPPORTED_FACINGS), "modules": ["module1", "module2", "module3", "fxti"]}


# ==================== v3.5 New API Routes ====================

class AnnualFlyingStarRequest(BaseModel):
    building_year: int = Field(..., description="建築年份")
    building_facing: str = Field(..., description="坐向：子山午向/丑山未向等")
    target_year: int = Field(default=2026, description="目標年份（默認2026）")


class DynamicPanRequest(BaseModel):
    building_year: int = Field(..., description="建築年份")
    building_facing: str = Field(..., description="坐向：子山午向/丑山未向等")


class MultiYearAnalysisRequest(BaseModel):
    building_year: int = Field(..., description="建築年份")
    building_facing: str = Field(..., description="坐向：子山午向/丑山未向等")
    start_year: int = Field(default=2024, description="開始年份")
    end_year: int = Field(default=2030, description="結束年份")


@app.post("/api/annual-flying-star")
def api_annual_flying_star(request: AnnualFlyingStarRequest):
    """年度飛星分析：計算指定年份的流年飛星與宅運盤疊加分析"""
    from data.annual_flying_star import calculate_annual_flying_star
    
    result = calculate_annual_flying_star(
        building_year=request.building_year,
        building_facing=request.building_facing,
        target_year=request.target_year
    )
    return result


@app.post("/api/dynamic-pan")
def api_dynamic_pan(request: DynamicPanRequest):
    """動態排盤：使用算法動態計算飛星盤（硬編碼數據缺失時的後備方案）"""
    from data.flying_star_dynamic import calculate_flying_star_pan
    
    result = calculate_flying_star_pan(
        building_year=request.building_year,
        mountain_facing=request.building_facing
    )
    return result


@app.post("/api/multi-year-analysis")
def api_multi_year_analysis(request: MultiYearAnalysisRequest):
    """多年度飛星分析：計算多年度的流年飛星疊加分析"""
    from data.annual_flying_star import calculate_multi_year_analysis
    
    results = calculate_multi_year_analysis(
        building_year=request.building_year,
        building_facing=request.building_facing,
        start_year=request.start_year,
        end_year=request.end_year
    )
    return {
        "status": "success",
        "building_year": request.building_year,
        "building_facing": request.building_facing,
        "start_year": request.start_year,
        "end_year": request.end_year,
        "total_years": len(results),
        "results": results
    }


@app.get("/api/annual-flying-star/{year}")
def api_annual_flying_star_simple(year: int, building_year: int, building_facing: str):
    """簡易年度飛星分析（GET版本）"""
    from data.annual_flying_star import calculate_annual_flying_star
    
    result = calculate_annual_flying_star(
        building_year=building_year,
        building_facing=building_facing,
        target_year=year
    )
    return result


# ==================== FXTI Routes ====================

@app.get("/api/fxti/profiles")
def fxti_profiles():
    """獲取所有15個FXTI角色列表"""
    profiles_list = []
    for pid, pdata in ALL_PROFILES.items():
        profiles_list.append({
            "id": pid,
            "name": pdata.get("name"),
            "title": pdata.get("title"),
            "type": "pure" if pid.startswith("A") else "composite",
            "elements": pdata.get("elements") if pid.startswith("B") else [pdata.get("element")],
            "traits": pdata.get("traits", [])[:3],
            "color": pdata.get("color", "#667eea")
        })
    return {"status": "success", "total": len(profiles_list), "profiles": profiles_list}


@app.post("/api/fxti/calculate")
def fxti_calculate(request: FXTICalculateRequest):
    """FXTI：計算五行人格"""
    # 1. 先天八字
    innate = get_innate_wuxing(
        request.birth_year, request.birth_month, request.birth_day, request.birth_hour
    )

    # 2. 後天問卷
    acquired = calculate_acquired_wuxing(request.answers)

    # 3. 合成
    final_wuxing = synthesize_result(
        innate["wuxing_percentage"],
        acquired["wuxing_percentage"]
    )

    # 4. 判定角色
    profile = determine_profile(final_wuxing)

    # 5. 存儲
    result_id = f"fxti_{len(fxti_results_db) + 1:04d}"
    result_data = {
        "id": result_id,
        "birth_info": {
            "year": request.birth_year,
            "month": request.birth_month,
            "day": request.birth_day,
            "hour": request.birth_hour,
            "gender": request.gender,
            "occupation": request.occupation
        },
        "bazi": innate["bazi"],
        "innate_wuxing": innate["wuxing_percentage"],
        "acquired_wuxing": acquired["wuxing_percentage"],
        "final_wuxing": final_wuxing,
        "profile": {
            "id": profile["id"],
            "name": profile["name"],
            "title": profile["title"],
            "type": profile["type"],
            "elements": profile.get("elements", [profile.get("element")]),
            "description": profile["description"],
            "core_contradiction": profile["core_contradiction"],
            "fengshui_advice": profile["fengshui_advice"],
            "traits": profile.get("traits", []),
            "color": profile.get("color", "#667eea"),
            "direction": profile.get("direction", "")
        }
    }
    fxti_results_db[result_id] = result_data

    return {
        "status": "success",
        "data": result_data,
        "share_url": f"/static/fxti/result.html?id={result_id}"
    }


@app.get("/api/fxti/result/{fxti_id}")
def fxti_result(fxti_id: str):
    """FXTI：獲取結果（含分享卡URL）"""
    if fxti_id not in fxti_results_db:
        raise HTTPException(status_code=404, detail="FXTI結果未找到")

    result = fxti_results_db[fxti_id]
    return {
        "status": "success",
        "data": result,
        "share_url": f"/static/fxti/result.html?id={fxti_id}"
    }


def _get_or_create_fxti_result(person: FXTIPersonInput) -> dict:
    """輔助函數：根據輸入獲取或創建FXTI結果"""
    if person.fxti_id and person.fxti_id in fxti_results_db:
        return fxti_results_db[person.fxti_id]

    # 需要現場計算
    if not all([person.birth_year, person.birth_month, person.birth_day, person.answers]):
        raise HTTPException(status_code=400, detail="缺少出生資料或問卷答案")

    innate = get_innate_wuxing(
        person.birth_year, person.birth_month, person.birth_day, person.birth_hour
    )
    acquired = calculate_acquired_wuxing(person.answers)
    final_wuxing = synthesize_result(
        innate["wuxing_percentage"],
        acquired["wuxing_percentage"]
    )
    profile = determine_profile(final_wuxing)

    result_id = f"fxti_rel_{len(fxti_results_db) + 1:04d}"
    result_data = {
        "id": result_id,
        "birth_info": {
            "year": person.birth_year,
            "month": person.birth_month,
            "day": person.birth_day,
            "hour": person.birth_hour,
            "gender": person.gender,
            "occupation": person.occupation
        },
        "bazi": innate["bazi"],
        "innate_wuxing": innate["wuxing_percentage"],
        "acquired_wuxing": acquired["wuxing_percentage"],
        "final_wuxing": final_wuxing,
        "profile": {
            "id": profile["id"],
            "name": profile["name"],
            "title": profile["title"],
            "type": profile["type"],
            "elements": profile.get("elements", [profile.get("element")]),
            "description": profile["description"],
            "core_contradiction": profile["core_contradiction"],
            "fengshui_advice": profile["fengshui_advice"],
            "traits": profile.get("traits", []),
            "color": profile.get("color", "#667eea"),
            "direction": profile.get("direction", "")
        }
    }
    fxti_results_db[result_id] = result_data
    return result_data


@app.post("/api/fxti/relationship")
def fxti_relationship(request: FXTIRelationshipRequest):
    """FXTI：雙人關係分析"""
    result_a = _get_or_create_fxti_result(request.person_a)
    result_b = _get_or_create_fxti_result(request.person_b)

    report = analyze_relationship(result_a, result_b)

    return {
        "status": "success",
        "data": report
    }


@app.get("/api/db-status")
def api_db_status():
    """數據庫連接狀態和數據統計"""
    try:
        status = get_db_status()
        estates_count = len(ALL_ESTATES) if 'ALL_ESTATES' in globals() else 0
        listings_count = len(ALL_LISTINGS) if 'ALL_LISTINGS' in globals() else 0
        return {
            "status": "success",
            "data": {
                **status,
                "app_version": VERSION,
                "estates_csv_loaded": estates_count,
                "listings_csv_loaded": listings_count
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "app_version": VERSION,
            "estates_csv_loaded": len(ALL_ESTATES) if 'ALL_ESTATES' in globals() else 0,
            "listings_csv_loaded": len(ALL_LISTINGS) if 'ALL_LISTINGS' in globals() else 0
        }


@app.get("/api/fengshui/bazhai")
def api_bazhai(year: int, facing: str):
    """八宅遊年：根據出生年份和朝向計算宅命"""
    try:
        from data.bazhai_younian import get_bazhai_analysis
        result = get_bazhai_analysis(year, facing)
        return {"status": "success", "data": result}
    except ImportError:
        return {"status": "error", "message": "八宅模塊尚未部署"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/fengshui/najia-floor")
def api_najia_floor(year: int, floor: int):
    """納甲樓層：根據出生年份和樓層計算吉凶"""
    try:
        from data.najia_floor import get_najia_analysis
        result = get_najia_analysis(year, floor)
        return {"status": "success", "data": result}
    except ImportError:
        return {"status": "error", "message": "納甲樓層模塊尚未部署"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/fengshui/compass")
def api_compass(mountain: str, facing: str):
    """羅盤工具：根據山向返回二十四山詳細信息"""
    try:
        from data.compass_tool import get_compass_info
        result = get_compass_info(mountain, facing)
        return {"status": "success", "data": result}
    except ImportError:
        return {"status": "error", "message": "羅盤工具模塊尚未部署"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
