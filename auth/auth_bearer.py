from fastapi import Request, HTTPException, status
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth_handler import decode_jwt

class JWTBearer(HTTPBearer):
    """
    Custom JWT Bearer token authenticator for FastAPI
    
    This class extends FastAPI's HTTPBearer to add JWT validation
    """
    
    def __init__(self, auto_error: bool = True):
        """
        Initialize JWT Bearer authenticator
        
        Args:
            auto_error: Whether to automatically raise HTTPException on auth failure
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Process incoming request and validate JWT token
        
        Args:
            request: FastAPI Request object
        
        Returns:
            JWT token string if valid
        
        Raises:
            HTTPException: If authentication fails
        """
        # Get Authorization header
        credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            # Check if it's Bearer token
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme. Expected 'Bearer'"
                )
            
            # Validate JWT token
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token"
                )
            
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code"
            )

    def verify_jwt(self, token: str) -> bool:
        """
        Verify JWT token validity
        
        Args:
            token: JWT token string
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            payload = decode_jwt(token)
            return True
        except Exception:
            return False
