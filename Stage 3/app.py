# api_gateway/app.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth import validate_token, RateLimiter
import httpx

app = FastAPI(title="Bazaar Inventory API Gateway")

# Service registry (would be replaced by service discovery in production)
SERVICES = {
    "catalog": "http://catalog-service:8000",
    "inventory": "http://inventory-service:8000",
    "transaction": "http://transaction-service:8000",
    "analytics": "http://analytics-service:8000",
    "notification": "http://notification-service:8000"
}

# Add rate limiter middleware
app.add_middleware(RateLimiter)

# Route requests to appropriate services
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_route(
    service: str, 
    path: str, 
    request: Request, 
    token_data: dict = Depends(validate_token)
):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
        
    # Forward the request to the appropriate service
    target_url = f"{SERVICES[service]}/{path}"
    
    # Add user info from token
    headers = {
        "Authorization": request.headers.get("Authorization"),
        "X-User-ID": token_data["user_id"],
        "X-User-Role": token_data["role"]
    }
    
    # Forward the request
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            json=await request.json() if request.method in ["POST", "PUT"] else None,
            params=request.query_params
        )
        
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )