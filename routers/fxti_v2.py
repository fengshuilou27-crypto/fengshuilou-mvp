"""
FXTI Backend API Module - v4.0.0
Real user system, matching, chat, community, expert booking
Six Dimensions Analysis, Values Quiz, Hepan, Coin System
Neon Postgres + FastAPI
"""

import os
import json
import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Database connection
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_sVKUOn6P2BlW@ep-ancient-cherry-afmoe2xv-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# ============ Pydantic Models ============

class UserCreate(BaseModel):
    nickname: str = Field(..., max_length=50)
    gender: str = Field(..., pattern="^(male|female|other)$")
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_hour: int = Field(12, ge=0, le=23)
    birth_place: Optional[str] = ""
    bio: Optional[str] = ""
    preferred_gender: str = Field("both", pattern="^(male|female|both)$")
    fxti_element: Optional[str] = None
    fxti_profile_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    uuid: str
    nickname: str
    gender: str
    birth_date: str
    fxti_element: Optional[str]
    fxti_profile_name: Optional[str]
    fxti_color: Optional[str]
    avatar_url: str
    bio: str
    is_expert: bool
    is_premium: bool

class SwipeRequest(BaseModel):
    swiper_id: int
    swiped_id: int
    direction: str = Field(..., pattern="^(left|right|super)$")

class MessageCreate(BaseModel):
    match_id: int
    sender_id: int
    receiver_id: int
    content: str
    content_type: str = Field("text", pattern="^(text|image|fengshui_tip|daily_fortune)$")

class PostCreate(BaseModel):
    author_id: int
    title: str = Field(..., max_length=200)
    content: str
    post_type: str = Field("general", pattern="^(general|question|story|expert_advice|fengshui_case)$")
    tags: List[str] = []

class CommentCreate(BaseModel):
    post_id: int
    author_id: int
    content: str
    parent_id: Optional[int] = None

class BookingCreate(BaseModel):
    client_id: int
    expert_id: int
    booking_type: str = Field("consultation", pattern="^(consultation|fengshui_visit|bazi_reading|hepan_analysis)$")
    booking_date: str = Field(..., description="YYYY-MM-DD")
    booking_time: str = Field(..., description="HH:MM")
    topic: str = Field(..., max_length=200)
    description: Optional[str] = ""

class DailyFortuneRequest(BaseModel):
    user_id: int
    fortune_date: Optional[str] = None


class SixDimensionRequest(BaseModel):
    user_a_id: int
    user_b_id: int


class ValuesQuizAnswer(BaseModel):
    user_id: int
    answers: Dict[str, int] = Field(..., description="{question_id: score(1-5)}")


class ValuesQuizResult(BaseModel):
    user_id: int
    partner_id: int


# ============ 45 Values Questions Data ============
VALUES_QUESTIONS = [
    {"id": "f1", "category": "family", "text": "家庭是我人生中最重要的部分", "weight": 1.0},
    {"id": "f2", "category": "family", "text": "我願意為家人犧牲個人利益", "weight": 1.0},
    {"id": "f3", "category": "family", "text": "我希望未來的伴侶重視家庭關係", "weight": 1.2},
    {"id": "f4", "category": "career", "text": "事業成功對我來說非常重要", "weight": 1.0},
    {"id": "f5", "category": "career", "text": "我願意為了事業暫時犧牲愛情", "weight": 0.8},
    {"id": "f6", "category": "career", "text": "我希望伴侶支持我的事業發展", "weight": 1.2},
    {"id": "f7", "category": "growth", "text": "我渴望不斷學習和成長", "weight": 1.0},
    {"id": "f8", "category": "growth", "text": "我喜歡嘗試新事物和挑戰", "weight": 1.0},
    {"id": "f9", "category": "growth", "text": "我希望伴侶能和我一起成長", "weight": 1.2},
    {"id": "f10", "category": "health", "text": "健康生活方式對我很重要", "weight": 1.0},
    {"id": "f11", "category": "health", "text": "我注重飲食和運動習慣", "weight": 0.8},
    {"id": "f12", "category": "health", "text": "我希望伴侶也有健康的生活習慣", "weight": 1.0},
    {"id": "f13", "category": "freedom", "text": "我重視個人自由和獨立空間", "weight": 1.0},
    {"id": "f14", "category": "freedom", "text": "我不喜歡被過度約束或控制", "weight": 1.0},
    {"id": "f15", "category": "freedom", "text": "我認為伴侶之間應該給彼此空間", "weight": 1.2},
    {"id": "f16", "category": "adventure", "text": "我喜歡冒險和刺激", "weight": 1.0},
    {"id": "f17", "category": "adventure", "text": "旅行和探索對我很有吸引力", "weight": 1.0},
    {"id": "f18", "category": "adventure", "text": "我希望伴侶願意和我一起探索世界", "weight": 1.0},
    {"id": "f19", "category": "stability", "text": "我追求穩定和安全感", "weight": 1.0},
    {"id": "f20", "category": "stability", "text": "我不喜歡生活中有太多變數", "weight": 0.8},
    {"id": "f21", "category": "stability", "text": "我希望建立穩定的長期關係", "weight": 1.2},
    {"id": "f22", "category": "spirituality", "text": "我對命理、風水、玄學有興趣", "weight": 1.0},
    {"id": "f23", "category": "spirituality", "text": "我相信緣分和命運的安排", "weight": 1.0},
    {"id": "f24", "category": "spirituality", "text": "我希望伴侶也尊重傳統文化", "weight": 1.0},
    {"id": "f25", "category": "finance", "text": "我重視財務規劃和儲蓄", "weight": 1.0},
    {"id": "f26", "category": "finance", "text": "我認為經濟基礎對愛情很重要", "weight": 1.0},
    {"id": "f27", "category": "finance", "text": "我希望伴侶有理性的消費觀", "weight": 1.0},
    {"id": "f28", "category": "social", "text": "我喜歡社交和認識新朋友", "weight": 1.0},
    {"id": "f29", "category": "social", "text": "我認為良好的社交圈對生活很重要", "weight": 0.8},
    {"id": "f30", "category": "social", "text": "我希望伴侶能融入我的朋友圈", "weight": 1.0},
]


# ============ Router ============

router = APIRouter(prefix="/api/fxti/v2", tags=["FXTI v2"])


# ============ User APIs ============

@router.get("/users")
def get_users(
    gender: Optional[str] = None,
    element: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get users with filters - for discovery/swipe cards"""
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, uuid, nickname, gender, birth_date, 
               fxti_element, fxti_profile_name, fxti_color, fxti_direction,
               avatar_url, bio, birth_place, is_expert, is_premium,
               total_swipes, total_matches, created_at
        FROM fxti_users 
        WHERE is_active = TRUE
    """
    params = []
    
    if gender:
        query += " AND gender = %s"
        params.append(gender)
    if element:
        query += " AND fxti_element = %s"
        params.append(element)
    if location:
        query += " AND birth_place ILIKE %s"
        params.append(f"%{location}%")
    
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    users = cur.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "total": len(users),
        "users": [dict(u) for u in users]
    }


@router.get("/users/{user_id}")
def get_user(user_id: int):
    """Get single user profile"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, uuid, nickname, gender, birth_date, birth_hour, birth_place,
               fxti_element, fxti_profile_name, fxti_color, fxti_direction,
               avatar_url, bio, preferred_gender, preferred_age_min, preferred_age_max,
               is_expert, is_premium, is_verified, total_swipes, total_matches,
               latitude, longitude, created_at
        FROM fxti_users WHERE id = %s AND is_active = TRUE
    """, (user_id,))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"status": "success", "user": dict(user)}


@router.post("/users")
def create_user(user: UserCreate):
    """Create new user"""
    conn = get_db()
    cur = conn.cursor()
    
    # Generate avatar based on gender
    seed = str(uuid.uuid4())[:8]
    avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}"
    
    cur.execute("""
        INSERT INTO fxti_users 
        (nickname, gender, birth_date, birth_hour, birth_place, bio,
         preferred_gender, fxti_element, fxti_profile_name, avatar_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, uuid, nickname, avatar_url, fxti_element, created_at
    """, (
        user.nickname, user.gender, user.birth_date, user.birth_hour,
        user.birth_place, user.bio, user.preferred_gender,
        user.fxti_element, user.fxti_profile_name, avatar_url
    ))
    
    new_user = cur.fetchone()
    conn.commit()
    conn.close()
    
    return {"status": "success", "user": dict(new_user)}


@router.get("/users/{user_id}/matches")
def get_user_matches(user_id: int):
    """Get all matches for a user"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.id, m.status, m.compatibility_score, m.wuxing_relation,
               m.matched_at, m.liked_by_a, m.liked_by_b,
               CASE WHEN m.user_a_id = %s THEN m.user_b_id ELSE m.user_a_id END as partner_id,
               u.nickname, u.avatar_url, u.fxti_element, u.fxti_profile_name, u.gender
        FROM fxti_matches m
        JOIN fxti_users u ON (
            CASE WHEN m.user_a_id = %s THEN m.user_b_id ELSE m.user_a_id END
        ) = u.id
        WHERE m.user_a_id = %s OR m.user_b_id = %s
        ORDER BY m.matched_at DESC NULLS LAST
    """, (user_id, user_id, user_id, user_id))
    
    matches = cur.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "total": len(matches),
        "matches": [dict(m) for m in matches]
    }


# ============ Swipe & Match APIs ============

@router.post("/swipe")
def swipe(req: SwipeRequest):
    """Record a swipe action and check for match"""
    conn = get_db()
    cur = conn.cursor()
    
    # Record swipe
    cur.execute("""
        INSERT INTO fxti_swipes (swiper_id, swiped_id, direction)
        VALUES (%s, %s, %s)
        ON CONFLICT (swiper_id, swiped_id) DO UPDATE SET direction = EXCLUDED.direction, created_at = NOW()
    """, (req.swiper_id, req.swiped_id, req.direction))
    
    # Update swipe count
    cur.execute("UPDATE fxti_users SET total_swipes = total_swipes + 1 WHERE id = %s", (req.swiper_id,))
    
    match_result = {"matched": False}
    
    if req.direction in ("right", "super"):
        # Check if other person also liked
        cur.execute("""
            SELECT direction FROM fxti_swipes 
            WHERE swiper_id = %s AND swiped_id = %s AND direction IN ('right', 'super')
        """, (req.swiped_id, req.swiper_id))
        
        other_swipe = cur.fetchone()
        
        if other_swipe:
            # It's a match!
            a_id, b_id = min(req.swiper_id, req.swiped_id), max(req.swiper_id, req.swiped_id)
            
            # Calculate compatibility
            cur.execute("SELECT fxti_element FROM fxti_users WHERE id IN (%s, %s)", (a_id, b_id))
            elements = {r['id']: r['fxti_element'] for r in cur.fetchall()}
            elem_a = elements.get(a_id, '木')
            elem_b = elements.get(b_id, '火')
            
            score, relation = _calculate_wuxing_compatibility(elem_a, elem_b)
            
            cur.execute("""
                INSERT INTO fxti_matches 
                (user_a_id, user_b_id, status, compatibility_score, wuxing_relation, 
                 liked_by_a, liked_by_b, matched_at)
                VALUES (%s, %s, 'matched', %s, %s, TRUE, TRUE, NOW())
                ON CONFLICT (user_a_id, user_b_id) DO UPDATE SET
                    status = 'matched',
                    compatibility_score = EXCLUDED.compatibility_score,
                    wuxing_relation = EXCLUDED.wuxing_relation,
                    matched_at = NOW()
                RETURNING id
            """, (a_id, b_id, score, relation))
            
            match_row = cur.fetchone()
            
            # Update match counts
            cur.execute("""
                UPDATE fxti_users SET total_matches = total_matches + 1 
                WHERE id IN (%s, %s)
            """, (a_id, b_id))
            
            match_result = {
                "matched": True,
                "match_id": match_row['id'],
                "compatibility_score": score,
                "wuxing_relation": relation,
                "message": "It's a match!"
            }
        else:
            # Create pending match
            a_id, b_id = min(req.swiper_id, req.swiped_id), max(req.swiper_id, req.swiped_id)
            liked_a = req.swiper_id == a_id
            
            cur.execute("""
                INSERT INTO fxti_matches (user_a_id, user_b_id, liked_by_a, liked_by_b)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_a_id, user_b_id) DO UPDATE SET
                    liked_by_a = CASE WHEN %s THEN TRUE ELSE fxti_matches.liked_by_a END,
                    liked_by_b = CASE WHEN %s THEN TRUE ELSE fxti_matches.liked_by_b END
            """, (a_id, b_id, liked_a, not liked_a, liked_a, not liked_a))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "result": match_result}


def _calculate_wuxing_compatibility(elem_a: str, elem_b: str) -> tuple:
    """Calculate compatibility score based on wuxing relations"""
    relations = {
        ('木', '火'): ('mutual', 88),
        ('火', '土'): ('mutual', 85),
        ('土', '金'): ('mutual', 82),
        ('金', '水'): ('mutual', 80),
        ('水', '木'): ('mutual', 86),
        ('木', '水'): ('supported', 78),
        ('火', '木'): ('supported', 78),
        ('土', '火'): ('supported', 75),
        ('金', '土'): ('supported', 75),
        ('水', '金'): ('supported', 76),
    }
    
    if elem_a == elem_b:
        return (75, 'same')
    
    key = (elem_a, elem_b)
    if key in relations:
        return relations[key]
    
    # Check reverse
    reverse = (elem_b, elem_a)
    if reverse in relations:
        score, rel = relations[reverse]
        return (score - 5, 'challenging' if 'mutual' in rel else 'supported')
    
    # Clashing elements
    clashes = [
        ('木', '金'), ('金', '木'),
        ('火', '水'), ('水', '火'),
        ('土', '木'), ('木', '土'),
    ]
    if key in clashes or reverse in clashes:
        return (55, 'clashing')
    
    return (65, 'neutral')


# ============ Chat APIs ============

@router.get("/matches/{match_id}/messages")
def get_messages(match_id: int, limit: int = Query(50, ge=1, le=200)):
    """Get messages for a match"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.id, m.sender_id, m.receiver_id, m.content, m.content_type,
               m.is_read, m.wuxing_tag, m.created_at,
               s.nickname as sender_name, s.avatar_url as sender_avatar
        FROM fxti_messages m
        JOIN fxti_users s ON m.sender_id = s.id
        WHERE m.match_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s
    """, (match_id, limit))
    
    messages = cur.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "total": len(messages),
        "messages": [dict(m) for m in reversed(messages)]
    }


@router.post("/messages")
def send_message(msg: MessageCreate):
    """Send a message"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO fxti_messages (match_id, sender_id, receiver_id, content, content_type)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, created_at
    """, (msg.match_id, msg.sender_id, msg.receiver_id, msg.content, msg.content_type))
    
    new_msg = cur.fetchone()
    
    # Update message count
    cur.execute("""
        UPDATE fxti_users SET total_messages = total_messages + 1 WHERE id = %s
    """, (msg.sender_id,))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": dict(new_msg)}


@router.post("/messages/{message_id}/read")
def mark_read(message_id: int):
    """Mark message as read"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE fxti_messages SET is_read = TRUE, read_at = NOW() WHERE id = %s
    """, (message_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}


# ============ Community APIs ============

@router.get("/posts")
def get_posts(
    post_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get community posts"""
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT p.id, p.title, p.content, p.post_type, p.tags,
               p.view_count, p.like_count, p.comment_count, p.is_pinned, p.is_featured,
               p.created_at, p.updated_at,
               u.id as author_id, u.nickname as author_name, u.avatar_url as author_avatar,
               u.is_expert as author_is_expert
        FROM fxti_posts p
        JOIN fxti_users u ON p.author_id = u.id
        WHERE 1=1
    """
    params = []
    
    if post_type:
        query += " AND p.post_type = %s"
        params.append(post_type)
    if tag:
        query += " AND %s = ANY(p.tags)"
        params.append(tag)
    
    query += " ORDER BY p.is_pinned DESC, p.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    posts = cur.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "total": len(posts),
        "posts": [dict(p) for p in posts]
    }


@router.get("/posts/{post_id}")
def get_post(post_id: int):
    """Get single post with comments"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get post
    cur.execute("""
        SELECT p.*, u.nickname as author_name, u.avatar_url as author_avatar, u.is_expert
        FROM fxti_posts p
        JOIN fxti_users u ON p.author_id = u.id
        WHERE p.id = %s
    """, (post_id,))
    post = cur.fetchone()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    cur.execute("UPDATE fxti_posts SET view_count = view_count + 1 WHERE id = %s", (post_id,))
    
    # Get comments
    cur.execute("""
        SELECT c.id, c.content, c.is_expert_reply, c.expert_tip, c.like_count, c.created_at,
               u.id as author_id, u.nickname as author_name, u.avatar_url as author_avatar, u.is_expert
        FROM fxti_comments c
        JOIN fxti_users u ON c.author_id = u.id
        WHERE c.post_id = %s
        ORDER BY c.created_at ASC
    """, (post_id,))
    comments = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "post": dict(post),
        "comments": [dict(c) for c in comments]
    }


@router.post("/posts")
def create_post(post: PostCreate):
    """Create a new post"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO fxti_posts (author_id, title, content, post_type, tags)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, created_at
    """, (post.author_id, post.title, post.content, post.post_type, post.tags))
    
    new_post = cur.fetchone()
    conn.commit()
    conn.close()
    
    return {"status": "success", "post": dict(new_post)}


@router.post("/posts/{post_id}/comments")
def create_comment(post_id: int, comment: CommentCreate):
    """Add a comment to a post"""
    conn = get_db()
    cur = conn.cursor()
    
    # Check if author is expert
    cur.execute("SELECT is_expert FROM fxti_users WHERE id = %s", (comment.author_id,))
    user = cur.fetchone()
    is_expert = user['is_expert'] if user else False
    
    cur.execute("""
        INSERT INTO fxti_comments (post_id, author_id, content, parent_id, is_expert_reply)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, created_at
    """, (post_id, comment.author_id, comment.content, comment.parent_id, is_expert))
    
    new_comment = cur.fetchone()
    
    # Update comment count
    cur.execute("""
        UPDATE fxti_posts SET comment_count = comment_count + 1 WHERE id = %s
    """, (post_id,))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "comment": dict(new_comment)}


# ============ Expert APIs ============

@router.get("/experts")
def get_experts(
    specialty: Optional[str] = None,
    min_rating: float = Query(0, ge=0, le=5),
    limit: int = Query(20, ge=1, le=100)
):
    """Get verified experts/fengshui masters"""
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT e.id, e.user_id, e.real_name, e.title, e.credentials, e.specialties,
               e.consultation_price, e.currency, e.rating, e.review_count, 
               e.total_consultations, e.bio, e.is_verified, e.is_featured,
               u.nickname, u.avatar_url, u.fxti_element
        FROM fxti_experts e
        JOIN fxti_users u ON e.user_id = u.id
        WHERE e.is_verified = TRUE
    """
    params = []
    
    if specialty:
        query += " AND %s = ANY(e.specialties)"
        params.append(specialty)
    
    if min_rating > 0:
        query += " AND e.rating >= %s"
        params.append(min_rating)
    
    query += " ORDER BY e.is_featured DESC, e.rating DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(query, params)
    experts = cur.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "total": len(experts),
        "experts": [dict(e) for e in experts]
    }


@router.get("/experts/{expert_id}")
def get_expert(expert_id: int):
    """Get expert profile with availability"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.*, u.nickname, u.avatar_url, u.bio as user_bio, u.fxti_element, u.fxti_profile_name
        FROM fxti_experts e
        JOIN fxti_users u ON e.user_id = u.id
        WHERE e.id = %s
    """, (expert_id,))
    expert = cur.fetchone()
    conn.close()
    
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    return {"status": "success", "expert": dict(expert)}


@router.post("/bookings")
def create_booking(booking: BookingCreate):
    """Book an expert consultation"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get expert price
    cur.execute("SELECT consultation_price FROM fxti_experts WHERE id = %s", (booking.expert_id,))
    expert = cur.fetchone()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    cur.execute("""
        INSERT INTO fxti_bookings 
        (client_id, expert_id, booking_type, booking_date, booking_time, topic, description, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, status, created_at
    """, (
        booking.client_id, booking.expert_id, booking.booking_type,
        booking.booking_date, booking.booking_time, booking.topic,
        booking.description, expert['consultation_price']
    ))
    
    new_booking = cur.fetchone()
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "booking": dict(new_booking),
        "price": expert['consultation_price']
    }


@router.get("/users/{user_id}/bookings")
def get_user_bookings(user_id: int, as_expert: bool = False):
    """Get bookings for a user (as client or expert)"""
    conn = get_db()
    cur = conn.cursor()
    
    if as_expert:
        cur.execute("""
            SELECT b.*, u.nickname as client_name, u.avatar_url as client_avatar
            FROM fxti_bookings b
            JOIN fxti_users u ON b.client_id = u.id
            WHERE b.expert_id = (SELECT id FROM fxti_experts WHERE user_id = %s)
            ORDER BY b.booking_date DESC
        """, (user_id,))
    else:
        cur.execute("""
            SELECT b.*, e.real_name as expert_name, u.avatar_url as expert_avatar
            FROM fxti_bookings b
            JOIN fxti_experts e ON b.expert_id = e.id
            JOIN fxti_users u ON e.user_id = u.id
            WHERE b.client_id = %s
            ORDER BY b.booking_date DESC
        """, (user_id,))
    
    bookings = cur.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "total": len(bookings),
        "bookings": [dict(b) for b in bookings]
    }


# ============ Daily Fortune API ============

@router.post("/daily-fortune")
def get_daily_fortune(req: DailyFortuneRequest):
    """Get or generate daily fortune for a user"""
    conn = get_db()
    cur = conn.cursor()
    
    fortune_date = req.fortune_date or date.today().isoformat()
    
    # Check if already exists
    cur.execute("""
        SELECT * FROM fxti_daily_fortune 
        WHERE user_id = %s AND fortune_date = %s
    """, (req.user_id, fortune_date))
    existing = cur.fetchone()
    
    if existing:
        conn.close()
        return {"status": "success", "fortune": dict(existing), "cached": True}
    
    # Get user element
    cur.execute("SELECT fxti_element FROM fxti_users WHERE id = %s", (req.user_id,))
    user = cur.fetchone()
    user_element = user['fxti_element'] if user else '木'
    
    # Generate fortune
    fortune = _generate_daily_fortune(user_element, fortune_date)
    fortune['user_id'] = req.user_id
    fortune['fortune_date'] = fortune_date
    
    # Save to DB
    cur.execute("""
        INSERT INTO fxti_daily_fortune 
        (user_id, fortune_date, gua_name, gua_number, gua_type, overall_score,
         love_score, career_score, wealth_score, health_score,
         daily_element, personal_element, interaction,
         lucky_color, lucky_direction, lucky_numbers, suitable, unsuitable,
         advice, love_advice, love_direction)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (
        fortune['user_id'], fortune['fortune_date'], fortune['gua_name'],
        fortune['gua_number'], fortune['gua_type'], fortune['overall_score'],
        fortune['love_score'], fortune['career_score'], fortune['wealth_score'],
        fortune['health_score'], fortune['daily_element'], fortune['personal_element'],
        fortune['interaction'], fortune['lucky_color'], fortune['lucky_direction'],
        fortune['lucky_numbers'], fortune['suitable'], fortune['unsuitable'],
        fortune['advice'], fortune['love_advice'], fortune['love_direction']
    ))
    
    new_fortune = cur.fetchone()
    conn.commit()
    conn.close()
    
    return {"status": "success", "fortune": dict(new_fortune), "cached": False}


def _generate_daily_fortune(user_element: str, fortune_date: str) -> dict:
    """Generate a daily fortune based on user element and date"""
    import hashlib
    
    # Deterministic random based on date + element
    seed = f"{fortune_date}-{user_element}"
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    
    gua_names = ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']
    gua_types = ['大吉', '中吉', '小吉', '平', '小凶', '凶']
    elements = ['木', '火', '土', '金', '水']
    colors = ['綠色', '紅色', '黃色', '白色', '黑色']
    directions = ['東', '南', '中', '西', '北']
    
    daily_elem = elements[hash_val % 5]
    
    # Calculate interaction
    if daily_elem == user_element:
        interaction = '比和'
        base_score = 70
    else:
        wuxing_cycle = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        if wuxing_cycle.get(user_element) == daily_elem:
            interaction = '相生'
            base_score = 85
        elif wuxing_cycle.get(daily_elem) == user_element:
            interaction = '被生'
            base_score = 80
        else:
            interaction = '相剋'
            base_score = 55
    
    # Add some randomness
    overall = min(100, max(0, base_score + (hash_val % 20) - 10))
    
    return {
        'gua_name': gua_names[hash_val % 8],
        'gua_number': (hash_val % 8) + 1,
        'gua_type': gua_types[hash_val % 6],
        'overall_score': overall,
        'love_score': min(100, max(0, overall + (hash_val % 15) - 7)),
        'career_score': min(100, max(0, overall + (hash_val % 15) - 7)),
        'wealth_score': min(100, max(0, overall + (hash_val % 15) - 7)),
        'health_score': min(100, max(0, overall + (hash_val % 15) - 7)),
        'daily_element': daily_elem,
        'personal_element': user_element,
        'interaction': interaction,
        'lucky_color': colors[hash_val % 5],
        'lucky_direction': directions[hash_val % 5],
        'lucky_numbers': f"{(hash_val % 9) + 1}, {(hash_val % 9) + 2}, {(hash_val % 9) + 5}",
        'suitable': ['社交', '學習', '規劃'] if overall > 60 else ['休息', '反思', '整理'],
        'unsuitable': ['爭執', '冒險'] if overall > 60 else ['投資', '決策', '出行'],
        'advice': f"今日{daily_elem}氣旺盛，與你的{user_element}命{interaction}。{'適合主動出擊，把握機遇！' if overall > 75 else '宜穩守待時，低調行事。' if overall < 50 else '運勢平穩，按部就班即可。'}",
        'love_advice': f"愛情運{'大吉，適合表白或約會！' if overall > 75 else '一般，多溝通理解對方。' if overall > 50 else '較弱，避免衝動決定。'}",
        'love_direction': directions[(hash_val + 1) % 5]
    }


# ============ Discovery / Feed API ============

@router.get("/discover")
def discover_users(
    user_id: int,
    gender_filter: Optional[str] = None,
    element_filter: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Discover users for swipe cards - exclude already swiped"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get user's preference
    cur.execute("SELECT preferred_gender, fxti_element FROM fxti_users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    
    # Get already swiped users
    cur.execute("SELECT swiped_id FROM fxti_swipes WHERE swiper_id = %s", (user_id,))
    swiped_ids = [r['swiped_id'] for r in cur.fetchall()]
    swiped_ids.append(user_id)  # Exclude self
    
    query = """
        SELECT id, uuid, nickname, gender, birth_date, 
               fxti_element, fxti_profile_name, fxti_color, fxti_direction,
               avatar_url, bio, birth_place, is_expert, is_premium,
               total_swipes, total_matches
        FROM fxti_users 
        WHERE is_active = TRUE AND id NOT IN %s
    """
    params = [tuple(swiped_ids) if swiped_ids else (0,)]
    
    # Apply gender filter
    pref_gender = user['preferred_gender'] if user else 'both'
    if pref_gender == 'male':
        query += " AND gender = 'male'"
    elif pref_gender == 'female':
        query += " AND gender = 'female'"
    
    if gender_filter:
        query += " AND gender = %s"
        params.append(gender_filter)
    if element_filter:
        query += " AND fxti_element = %s"
        params.append(element_filter)
    
    query += " ORDER BY RANDOM() LIMIT %s"
    params.append(limit)
    
    cur.execute(query, tuple(params))
    users = cur.fetchall()
    conn.close()
    
    # Calculate compatibility with each
    user_elem = user['fxti_element'] if user else '木'
    results = []
    for u in users:
        score, relation = _calculate_wuxing_compatibility(user_elem, u['fxti_element'] or '木')
        results.append({
            **dict(u),
            'compatibility_score': score,
            'wuxing_relation': relation
        })
    
    # Sort by compatibility
    results.sort(key=lambda x: x['compatibility_score'], reverse=True)
    
    return {
        "status": "success",
        "total": len(results),
        "users": results
    }


# ============ Stats API ============

@router.get("/stats")
def get_stats():
    """Get FXTI platform statistics"""
    conn = get_db()
    cur = conn.cursor()
    
    stats = {}
    
    cur.execute("SELECT COUNT(*) FROM fxti_users WHERE is_active = TRUE")
    stats['total_users'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM fxti_matches WHERE status = 'matched'")
    stats['total_matches'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM fxti_messages")
    stats['total_messages'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM fxti_posts")
    stats['total_posts'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM fxti_experts WHERE is_verified = TRUE")
    stats['total_experts'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM fxti_bookings WHERE status = 'completed'")
    stats['total_bookings'] = cur.fetchone()['count']
    
    # Element distribution
    cur.execute("""
        SELECT fxti_element, COUNT(*) as count 
        FROM fxti_users 
        WHERE fxti_element IS NOT NULL 
        GROUP BY fxti_element
    """)
    stats['element_distribution'] = {r['fxti_element']: r['count'] for r in cur.fetchall()}
    
    conn.close()
    
    return {"status": "success", "stats": stats}


# ============ Wuxing Card Reveal (Patent Workaround) ============

@router.get("/matches/{match_id}/reveal")
def get_reveal_status(match_id: int, user_id: int):
    """Check if photos are revealed for a match"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT user_a_id, user_b_id, a_revealed_to_b, b_revealed_to_a, reveal_method
        FROM fxti_matches WHERE id = %s
    """, (match_id,))
    match = cur.fetchone()
    conn.close()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    is_a = user_id == match['user_a_id']
    revealed = match['a_revealed_to_b'] if is_a else match['b_revealed_to_a']
    
    return {
        "status": "success",
        "revealed": revealed,
        "reveal_method": match['reveal_method'],
        "message": "Photos revealed" if revealed else "Complete the wuxing quiz to reveal photos"
    }


@router.post("/matches/{match_id}/reveal")
def reveal_photos(match_id: int, user_id: int):
    """Reveal photos for a match (after quiz completion)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT user_a_id, user_b_id FROM fxti_matches WHERE id = %s
    """, (match_id,))
    match = cur.fetchone()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    is_a = user_id == match['user_a_id']
    
    if is_a:
        cur.execute("UPDATE fxti_matches SET a_revealed_to_b = TRUE WHERE id = %s", (match_id,))
    else:
        cur.execute("UPDATE fxti_matches SET b_revealed_to_a = TRUE WHERE id = %s", (match_id,))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "revealed": True}


# ============ Six Dimensions Analysis API ============

@router.post("/six-dimensions")
def analyze_six_dimensions(req: SixDimensionRequest):
    """Analyze six dimensions compatibility between two users"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.fxti_six_dimensions import analyze_relationship_full_v3
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get user A data
    cur.execute("""
        SELECT id, nickname, gender, birth_date, birth_hour, birth_place,
               fxti_element, fxti_profile_name, fxti_color, fxti_direction,
               avatar_url, bio, preferred_gender, preferred_age_min, preferred_age_max,
               is_expert, is_premium, is_verified, total_swipes, total_matches,
               latitude, longitude, values_answers, created_at
        FROM fxti_users WHERE id = %s AND is_active = TRUE
    """, (req.user_a_id,))
    user_a = cur.fetchone()
    
    # Get user B data
    cur.execute("""
        SELECT id, nickname, gender, birth_date, birth_hour, birth_place,
               fxti_element, fxti_profile_name, fxti_color, fxti_direction,
               avatar_url, bio, preferred_gender, preferred_age_min, preferred_age_max,
               is_expert, is_premium, is_verified, total_swipes, total_matches,
               latitude, longitude, values_answers, created_at
        FROM fxti_users WHERE id = %s AND is_active = TRUE
    """, (req.user_b_id,))
    user_b = cur.fetchone()
    
    conn.close()
    
    if not user_a or not user_b:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse birth date
    from datetime import datetime
    birth_a = user_a['birth_date']
    birth_b = user_b['birth_date']
    
    # Build person data for six dimensions - USE REAL DB DATA
    # Get values answers from DB if available
    values_a = user_a.get('values_answers') or {}
    values_b = user_b.get('values_answers') or {}
    
    # Parse values_answers if stored as JSON string
    if isinstance(values_a, str):
        try:
            values_a = json.loads(values_a)
        except:
            values_a = {}
    if isinstance(values_b, str):
        try:
            values_b = json.loads(values_b)
        except:
            values_b = {}
    
    # Build wuxing dict from real element
    elem_a = user_a['fxti_element'] or '木'
    elem_b = user_b['fxti_element'] or '木'
    
    # Create balanced wuxing distribution based on element
    def build_wuxing(element):
        base = {"金": 10, "木": 10, "水": 10, "火": 10, "土": 10}
        if element in base:
            base[element] = 40  # Primary element gets higher weight
            # Secondary based on generation cycle
            cycle = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
            if element in cycle:
                base[cycle[element]] = 20
        return base
    
    person_a_data = {
        "birth": {
            "year": birth_a.year if hasattr(birth_a, 'year') else int(str(birth_a)[:4]),
            "month": birth_a.month if hasattr(birth_a, 'month') else int(str(birth_a)[5:7]),
            "day": birth_a.day if hasattr(birth_a, 'day') else int(str(birth_a)[8:10]),
            "gender": user_a['gender']
        },
        "wuxing": build_wuxing(elem_a),
        "profile_id": user_a['fxti_profile_name'] or 'A1',
        "values_answers": values_a,
        "communication_style": "direct",
        "life_goals": ["事業成就", "家庭美滿"],
    }
    
    person_b_data = {
        "birth": {
            "year": birth_b.year if hasattr(birth_b, 'year') else int(str(birth_b)[:4]),
            "month": birth_b.month if hasattr(birth_b, 'month') else int(str(birth_b)[5:7]),
            "day": birth_b.day if hasattr(birth_b, 'day') else int(str(birth_b)[8:10]),
            "gender": user_b['gender']
        },
        "wuxing": build_wuxing(elem_b),
        "profile_id": user_b['fxti_profile_name'] or 'A1',
        "values_answers": values_b,
        "communication_style": "empathetic",
        "life_goals": ["自我成長", "家庭美滿"],
    }
    
    # Run six dimensions analysis
    result = analyze_relationship_full_v3(person_a_data, person_b_data)
    
    return {
        "status": "success",
        "user_a": {"id": user_a['id'], "nickname": user_a['nickname'], "avatar_url": user_a['avatar_url']},
        "user_b": {"id": user_b['id'], "nickname": user_b['nickname'], "avatar_url": user_b['avatar_url']},
        "analysis": result
    }


# ============ Values Quiz APIs ============

@router.get("/values-quiz/questions")
def get_values_questions():
    """Get the 30 values questions for the quiz"""
    return {
        "status": "success",
        "total": len(VALUES_QUESTIONS),
        "questions": VALUES_QUESTIONS
    }


@router.post("/values-quiz/submit")
def submit_values_quiz(answer: ValuesQuizAnswer):
    """Submit user's values quiz answers"""
    conn = get_db()
    cur = conn.cursor()
    
    # Save answers as JSON
    answers_json = json.dumps(answer.answers)
    
    cur.execute("""
        UPDATE fxti_users 
        SET values_answers = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id
    """, (answers_json, answer.user_id))
    
    updated = cur.fetchone()
    conn.commit()
    conn.close()
    
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate values profile
    profile = _calculate_values_profile(answer.answers)
    
    return {
        "status": "success",
        "message": "Quiz submitted successfully",
        "values_profile": profile
    }


def _calculate_values_profile(answers: Dict[str, int]) -> Dict[str, Any]:
    """Calculate user's values profile from answers"""
    categories = {
        "family": [], "career": [], "growth": [], "health": [],
        "freedom": [], "adventure": [], "stability": [],
        "spirituality": [], "finance": [], "social": []
    }
    
    for q in VALUES_QUESTIONS:
        cat = q["category"]
        score = answers.get(q["id"], 3)
        categories[cat].append(score * q["weight"])
    
    profile = {}
    for cat, scores in categories.items():
        if scores:
            avg = sum(scores) / len(scores)
            profile[cat] = round(avg, 1)
        else:
            profile[cat] = 3.0
    
    # Determine top 3 values
    sorted_values = sorted(profile.items(), key=lambda x: x[1], reverse=True)
    top_values = [v[0] for v in sorted_values[:3]]
    
    return {
        "scores": profile,
        "top_values": top_values,
        "primary_value": top_values[0] if top_values else "family",
        "secondary_value": top_values[1] if len(top_values) > 1 else "growth",
        "tertiary_value": top_values[2] if len(top_values) > 2 else "health"
    }


@router.post("/values-quiz/compare")
def compare_values_quiz(req: ValuesQuizResult):
    """Compare two users' values quiz results"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT values_answers FROM fxti_users WHERE id = %s", (req.user_id,))
    user_a = cur.fetchone()
    
    cur.execute("SELECT values_answers FROM fxti_users WHERE id = %s", (req.partner_id,))
    user_b = cur.fetchone()
    
    conn.close()
    
    if not user_a or not user_b:
        raise HTTPException(status_code=404, detail="User not found")
    
    answers_a = json.loads(user_a['values_answers'] or '{}')
    answers_b = json.loads(user_b['values_answers'] or '{}')
    
    if not answers_a or not answers_b:
        return {
            "status": "success",
            "compatibility_score": 50,
            "message": "One or both users haven't completed the quiz",
            "details": {}
        }
    
    # Calculate compatibility
    from data.fxti_six_dimensions import analyze_values_compatibility
    result = analyze_values_compatibility(answers_a, answers_b)
    
    return {
        "status": "success",
        "compatibility_score": result["overall_score"],
        "details": result
    }


# ============ Hepan (合盤) API ============

@router.post("/hepan")
def generate_hepan(req: SixDimensionRequest):
    """Generate 合盤 analysis (Bazi compatibility)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT birth_date, birth_hour, gender FROM fxti_users WHERE id = %s", (req.user_a_id,))
    user_a = cur.fetchone()
    
    cur.execute("SELECT birth_date, birth_hour, gender FROM fxti_users WHERE id = %s", (req.user_b_id,))
    user_b = cur.fetchone()
    
    conn.close()
    
    if not user_a or not user_b:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate hepan analysis
    hepan = _generate_hepan_analysis(user_a, user_b)
    
    return {
        "status": "success",
        "hepan": hepan
    }


def _generate_hepan_analysis(a: Dict, b: Dict) -> Dict[str, Any]:
    """Generate simplified 合盤 analysis"""
    import hashlib
    
    # Create deterministic hash from birth dates
    seed = f"{a['birth_date']}-{b['birth_date']}"
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    
    # Determine compatibility level
    levels = ["天作之合", "金玉良緣", "相輔相成", "平淡是真", "需要磨合", "緣分淺薄"]
    level = levels[hash_val % 6]
    
    scores = {
        "天作之合": 95, "金玉良緣": 88, "相輔相成": 78,
        "平淡是真": 65, "需要磨合": 52, "緣分淺薄": 38
    }
    
    aspects = [
        {"name": "日柱合婚", "score": min(100, scores[level] + (hash_val % 10) - 5), "comment": "日干相生，性格互補"},
        {"name": "五行流通", "score": min(100, scores[level] + (hash_val % 10) - 5), "comment": "五行相生，氣場和諧"},
        {"name": "大運同步", "score": min(100, scores[level] + (hash_val % 10) - 5), "comment": "大運方向一致"},
        {"name": "桃花姻緣", "score": min(100, scores[level] + (hash_val % 10) - 5), "comment": "桃花運勢相合"},
    ]
    
    return {
        "level": level,
        "overall_score": scores[level],
        "aspects": aspects,
        "advice": f"你們的合盤結果為「{level}」。{ '緣分深厚，建議珍惜彼此，共同經營感情。' if scores[level] > 80 else '需要多溝通理解，培養共同興趣。' if scores[level] > 60 else '緣分較淺，需要更多努力維繫關係。'}",
        "lucky_dates": ["農曆初八", "農曆十五", "農曆廿三"],
        "avoid_dates": ["農曆初七", "農曆十四"]
    }


# ============ Blurred Photo System ============

@router.get("/users/{user_id}/blurred-photo")
def get_blurred_photo(user_id: int, viewer_id: int):
    """Get blurred photo for a user (patent workaround)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT avatar_url FROM fxti_users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already revealed
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a_revealed_to_b, b_revealed_to_a FROM fxti_matches
        WHERE (user_a_id = %s AND user_b_id = %s) OR (user_a_id = %s AND user_b_id = %s)
    """, (user_id, viewer_id, viewer_id, user_id))
    match = cur.fetchone()
    conn.close()
    
    revealed = False
    if match:
        is_a = (user_id == viewer_id) if match else False
        # Simplified check
        revealed = match.get('a_revealed_to_b', False) or match.get('b_revealed_to_a', False)
    
    return {
        "status": "success",
        "original_url": user['avatar_url'] if revealed else None,
        "blurred_url": user['avatar_url'],  # Frontend applies pixelation
        "is_revealed": revealed,
        "reveal_progress": 0 if not revealed else 100,
        "interaction_needed": 5 if not revealed else 0  # Messages needed to reveal
    }


# ============ Coin / Virtual Currency API ============

@router.get("/users/{user_id}/coins")
def get_user_coins(user_id: int):
    """Get user's coin balance"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT coins, total_coins_earned, total_coins_spent FROM fxti_users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "coins": user['coins'] or 0,
        "total_earned": user['total_coins_earned'] or 0,
        "total_spent": user['total_coins_spent'] or 0
    }


@router.post("/users/{user_id}/coins/earn")
def earn_coins(user_id: int, action: str = "daily_login"):
    """Earn coins for various actions"""
    earn_amounts = {
        "daily_login": 10,
        "complete_profile": 50,
        "complete_quiz": 30,
        "daily_fortune": 5,
        "send_message": 2,
        "receive_like": 5,
        "expert_consultation": 100,
    }
    
    amount = earn_amounts.get(action, 0)
    if amount == 0:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE fxti_users 
        SET coins = COALESCE(coins, 0) + %s,
            total_coins_earned = COALESCE(total_coins_earned, 0) + %s
        WHERE id = %s
        RETURNING coins
    """, (amount, amount, user_id))
    
    result = cur.fetchone()
    conn.commit()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "action": action,
        "coins_earned": amount,
        "new_balance": result['coins']
    }


@router.post("/users/{user_id}/coins/spend")
def spend_coins(user_id: int, action: str = "reveal_photo", target_id: int = None):
    """Spend coins for premium features"""
    costs = {
        "reveal_photo": 50,
        "super_like": 30,
        "expert_consultation": 200,
        "premium_match": 100,
        "hepan_analysis": 150,
    }
    
    cost = costs.get(action, 0)
    if cost == 0:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check balance
    cur.execute("SELECT coins FROM fxti_users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    current = user['coins'] or 0
    if current < cost:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Insufficient coins. Need {cost}, have {current}")
    
    # Deduct coins
    cur.execute("""
        UPDATE fxti_users 
        SET coins = COALESCE(coins, 0) - %s,
            total_coins_spent = COALESCE(total_coins_spent, 0) + %s
        WHERE id = %s
        RETURNING coins
    """, (cost, cost, user_id))
    
    result = cur.fetchone()
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "action": action,
        "coins_spent": cost,
        "new_balance": result['coins']
    }
