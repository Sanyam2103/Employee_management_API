from fastapi import Depends, HTTPException, status
from .auth_bearer import JWTBearer
from .auth_handler import decode_jwt
from .user_service import get_user_by_username
from app.models import TokenData
from typing import Optional

# Create JWT bearer instance
jwt_bearer = JWTBearer()

def get_current_user(token: str = Depends(jwt_bearer)) -> dict:
    """
    Dependency to get current authenticated user
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        Current user document
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Decode JWT token
        payload = decode_jwt(token)
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(username=username, role=payload.get("role"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    if token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username missing in token"
        )
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin role
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user if they are admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure user is active
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user if active
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user
