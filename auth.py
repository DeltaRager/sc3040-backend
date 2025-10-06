"""
Supabase Authentication for FastAPI Backend
Handles JWT token verification and user authentication
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import os
from config import settings

# Initialize Supabase client (lazy initialization)
def get_supabase_client() -> Client:
    """Get Supabase client with lazy initialization"""
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration not properly set"
        )
    
    return create_client(
        settings.supabase_url,
        settings.supabase_publishable_key
    )

# Security scheme
security = HTTPBearer()

class SupabaseAuth:
    """Supabase authentication handler"""
    
    @staticmethod
    def verify_jwt_token(token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return user data
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Dict containing user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode JWT token without verification first to get header
            unverified_header = jwt.get_unverified_header(token)
            
            # Get the JWT secret from Supabase (this is the JWT secret, not the publishable key)
            jwt_secret = settings.supabase_jwt_secret
            
            if not jwt_secret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="JWT secret not configured",
                )
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )
            
            # Extract user information from the payload
            user_id = payload.get("sub")
            email = payload.get("email")
            user_metadata = payload.get("user_metadata", {})
            app_metadata = payload.get("app_metadata", {})
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return {
                "id": user_id,
                "email": email,
                "user_metadata": user_metadata,
                "app_metadata": app_metadata,
                "created_at": payload.get("iat"),  # Issued at
                "updated_at": payload.get("exp")   # Expires at
            }
            
        except JWTError as e:
            print(f"JWT verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            print(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    return SupabaseAuth.verify_jwt_token(token)

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user (doesn't raise exception if no token)
    
    Args:
        credentials: Optional HTTP Bearer token from request header
        
    Returns:
        Dict containing user information or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return SupabaseAuth.verify_jwt_token(token)
    except HTTPException:
        return None

# User model for type hints
class User:
    def __init__(self, user_data: Dict[str, Any]):
        self.id = user_data["id"]
        self.email = user_data["email"]
        self.user_metadata = user_data.get("user_metadata", {})
        self.app_metadata = user_data.get("app_metadata", {})
        self.created_at = user_data.get("created_at")
        self.updated_at = user_data.get("updated_at")
    
    def __str__(self):
        return f"User(id={self.id}, email={self.email})"
