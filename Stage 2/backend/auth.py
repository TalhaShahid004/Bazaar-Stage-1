import os
import time
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_401_UNAUTHORIZED

# Get API keys from environment variables
API_KEYS = {
    'store1': os.getenv('API_KEY_STORE1', 'store1_api_key'),
    'store2': os.getenv('API_KEY_STORE2', 'store2_api_key'),
    # Add more store API keys as needed
}

# Get rate limit from environment variables
RATE_LIMIT = int(os.getenv('RATE_LIMIT_MINUTE', '100'))

# In-memory store for rate limiting
# In a production environment, this would be replaced with Redis or similar
rate_limit_store = {}

# API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key and return store code."""
    if api_key is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API Key header missing"
        )
    
    for store_code, key in API_KEYS.items():
        if api_key == key:
            return store_code
    
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    )

async def rate_limit_middleware(request: Request, store_code: str = Depends(get_api_key)):
    """Apply rate limiting based on store code."""
    now = int(time.time())
    minute_window = now // 60
    
    # Create rate limit key for current store and minute window
    rate_key = f"{store_code}:{minute_window}"
    
    # Get current count or initialize to 0
    current_count = rate_limit_store.get(rate_key, 0)
    
    # Check if rate limit exceeded
    if current_count >= RATE_LIMIT:
        # Add headers for rate limit info
        request.state.rate_limit_remaining = 0
        request.state.rate_limit = RATE_LIMIT
        request.state.rate_limit_reset = (minute_window + 1) * 60
        
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Increment counter
    rate_limit_store[rate_key] = current_count + 1
    
    # Set rate limit info in request state for headers
    request.state.rate_limit_remaining = RATE_LIMIT - (current_count + 1)
    request.state.rate_limit = RATE_LIMIT
    request.state.rate_limit_reset = (minute_window + 1) * 60
    
    # Cleanup old entries every 10 requests
    if (current_count + 1) % 10 == 0:
        cleanup_old_rate_limits(now)
    
    return store_code

def cleanup_old_rate_limits(now):
    """Remove outdated rate limit entries."""
    current_minute = now // 60
    keys_to_delete = []
    
    for key in rate_limit_store:
        key_minute = int(key.split(':')[1])
        if key_minute < current_minute:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del rate_limit_store[key]