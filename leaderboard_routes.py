from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from database import get_supabase_client, get_supabase_admin_client
from auth import get_current_user

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
async def get_leaderboard(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """Return a paginated leaderboard with dense ranks (ties share the same position)."""
    supabase = get_supabase_admin_client()

    offset = (page - 1) * page_size
    # Fetch page ordered deterministically
    page_resp = (
        supabase
        .table("users")
        .select("id, username, avatar, score, created_at")
        .order("score", desc=True)
        .order("created_at", desc=False)
        .order("id", desc=False)
        .range(offset, offset + page_size - 1)
        .execute()
    )

    if not page_resp:
        raise HTTPException(status_code=500, detail="Failed to query database")
    
    if hasattr(page_resp, 'error') and page_resp.error:
        raise HTTPException(status_code=500, detail=str(page_resp.error))

    rows = page_resp.data or []
    if not rows:
        return {"items": [], "page": page, "page_size": page_size}

    top_score = rows[0].get("score") or 0

    # Count distinct scores strictly greater than the top score of this page
    higher_resp = (
        supabase
        .table("users")
        .select("score")
        .gt("score", top_score)
        .order("score", desc=True)
        .limit(100000)
        .execute()
    )

    if not higher_resp:
        raise HTTPException(status_code=500, detail="Failed to query database")
    
    if hasattr(higher_resp, 'error') and higher_resp.error:
        raise HTTPException(status_code=500, detail=str(higher_resp.error))

    distinct_higher = {r.get("score") for r in (higher_resp.data or [])}
    base_rank = len(distinct_higher) + 1

    # Dense rank within the page
    unique_scores_desc = sorted({(r.get("score") or 0) for r in rows}, reverse=True)
    score_to_offset = {score: idx for idx, score in enumerate(unique_scores_desc)}

    items = [
        {
            "id": r.get("id"),
            "username": r.get("username"),
            "avatar": r.get("avatar"),
            "score": r.get("score") or 0,
            "position": base_rank + score_to_offset.get(r.get("score") or 0, 0),
        }
        for r in rows
    ]

    return {"items": items, "page": page, "page_size": page_size}


@router.get("/my-rank")
async def get_my_rank(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return dense rank for the current authenticated user."""
    supabase = get_supabase_admin_client()
    user_id = current_user["id"]

    user_resp = (
        supabase
        .table("users")
        .select("id, username, avatar, score, created_at")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    if not user_resp:
        raise HTTPException(status_code=500, detail="Failed to query database")
    
    if hasattr(user_resp, 'error') and user_resp.error:
        raise HTTPException(status_code=500, detail=str(user_resp.error))
    if not user_resp.data:
        raise HTTPException(status_code=404, detail="User not found")

    user_row = user_resp.data
    score = user_row.get("score") or 0

    higher_resp = (
        supabase
        .table("users")
        .select("score")
        .gt("score", score)
        .order("score", desc=True)
        .limit(100000)
        .execute()
    )

    if not higher_resp:
        raise HTTPException(status_code=500, detail="Failed to query database")
    
    if hasattr(higher_resp, 'error') and higher_resp.error:
        raise HTTPException(status_code=500, detail=str(higher_resp.error))

    distinct_higher = {r.get("score") for r in (higher_resp.data or [])}
    position = len(distinct_higher) + 1

    return {
        "id": user_row.get("id"),
        "username": user_row.get("username"),
        "avatar": user_row.get("avatar"),
        "score": score,
        "position": position,
    }


