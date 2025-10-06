"""
Example protected routes demonstrating authentication usage
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from auth import get_current_user, get_current_user_optional, User
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["protected"])

# Example data models
class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    learning_goals: str
    created_at: str

class LearningProgress(BaseModel):
    user_id: str
    module: str
    lesson: str
    score: int
    completed_at: str

# Example protected endpoint - requires authentication
@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user's profile - requires authentication
    """
    # In a real app, you'd fetch this from your database
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("user_metadata", {}).get("full_name", ""),
        learning_goals=current_user.get("user_metadata", {}).get("learning_goals", ""),
        created_at=current_user.get("created_at", "")
    )

# Example protected endpoint with user object
@router.get("/my-data")
async def get_my_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user-specific data - requires authentication
    """
    user = User(current_user)
    
    return {
        "message": f"Hello {user.email}!",
        "user_id": user.id,
        "is_authenticated": True,
        "user_metadata": user.user_metadata
    }

# Example protected endpoint for learning progress
@router.post("/progress", response_model=LearningProgress)
async def save_learning_progress(
    progress_data: LearningProgress,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Save learning progress - requires authentication
    """
    # Ensure the progress belongs to the authenticated user
    if progress_data.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot save progress for another user"
        )
    
    # In a real app, you'd save this to your database
    print(f"Saving progress for user {current_user['id']}: {progress_data}")
    
    return progress_data

# Example endpoint with optional authentication
@router.get("/public-data")
async def get_public_data(current_user: Dict[str, Any] = Depends(get_current_user_optional)):
    """
    Get public data - authentication optional
    """
    if current_user:
        return {
            "message": "Hello authenticated user!",
            "user_id": current_user["id"],
            "is_authenticated": True
        }
    else:
        return {
            "message": "Hello guest user!",
            "is_authenticated": False
        }

# Example admin-only endpoint
@router.get("/admin/stats")
async def get_admin_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Admin-only endpoint - requires authentication and admin role
    """
    # Check if user has admin role (you'd implement this based on your user roles)
    user_metadata = current_user.get("user_metadata", {})
    if not user_metadata.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "message": "Admin statistics",
        "total_users": 1000,  # Example data
        "active_sessions": 50
    }

# Example endpoint that uses user ID for database operations
@router.get("/my-learning-history")
async def get_learning_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user's learning history - requires authentication
    """
    user_id = current_user["id"]
    
    # In a real app, you'd query your database with the user_id
    # Example: SELECT * FROM learning_sessions WHERE user_id = ?
    
    return {
        "user_id": user_id,
        "learning_sessions": [
            {
                "module": "Basic Signs",
                "lesson": "Alphabet",
                "score": 95,
                "completed_at": "2024-01-15T10:30:00Z"
            },
            {
                "module": "Basic Signs", 
                "lesson": "Numbers",
                "score": 88,
                "completed_at": "2024-01-16T14:20:00Z"
            }
        ]
    }
