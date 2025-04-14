# lib/auth/jwt_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from redis import Redis
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Redis client for token blacklisting
redis_client = Redis(host=REDIS_HOST, db=1, decode_responses=True)

def create_access_token(data: Dict[str, Any]) -> str:
    """Create a new JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def validate_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Validate a JWT token and return its payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check if token is blacklisted
        if redis_client.exists(f"blacklisted_token:{token}"):
            raise credentials_exception
            
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if required fields exist
        if "sub" not in payload or "role" not in payload:
            raise credentials_exception
            
        return payload
        
    except JWTError:
        raise credentials_exception

def blacklist_token(token: str) -> None:
    """Add a token to the blacklist."""
    try:
        # Get token expiration time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp", 0)
        current_time = datetime.utcnow().timestamp()
        ttl = max(0, int(exp - current_time))
        
        # Add to blacklist with appropriate TTL
        redis_client.setex(f"blacklisted_token:{token}", ttl, "1")
    except JWTError:
        # If token is invalid, no need to blacklist
        pass