"""
Rate limiting middleware
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
from typing import Dict, Tuple
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app):
        super().__init__(app)
        # Rate limits: (requests, window_seconds)
        self.rate_limits = {
            "default": (100, 60),  # 100 requests per minute
            "auth": (10, 60),      # 10 auth requests per minute
            "upload": (5, 60),     # 5 uploads per minute
            "api": (200, 60),      # 200 API requests per minute
        }
        # Store request timestamps for each IP
        self.request_history: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(deque)
        )
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        endpoint_type = self.get_endpoint_type(request.url.path)
        
        # Check rate limit
        if self.is_rate_limited(client_ip, endpoint_type):
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_type}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Record request
        self.record_request(client_ip, endpoint_type)
        
        response = await call_next(request)
        
        # Add rate limit headers
        limit, window = self.rate_limits[endpoint_type]
        remaining = self.get_remaining_requests(client_ip, endpoint_type)
        reset_time = int(time.time()) + window
        
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if "/auth/" in path or "/login" in path or "/register" in path:
            return "auth"
        elif "/upload" in path or "/documents" in path:
            return "upload"
        elif "/api/" in path:
            return "api"
        else:
            return "default"
    
    def is_rate_limited(self, client_ip: str, endpoint_type: str) -> bool:
        """Check if client is rate limited"""
        limit, window = self.rate_limits[endpoint_type]
        now = time.time()
        
        # Clean old requests
        self.cleanup_old_requests(client_ip, endpoint_type, now, window)
        
        # Check current request count
        request_count = len(self.request_history[client_ip][endpoint_type])
        return request_count >= limit
    
    def record_request(self, client_ip: str, endpoint_type: str):
        """Record a request timestamp"""
        now = time.time()
        self.request_history[client_ip][endpoint_type].append(now)
    
    def cleanup_old_requests(self, client_ip: str, endpoint_type: str, now: float, window: int):
        """Remove old request timestamps outside the window"""
        cutoff = now - window
        history = self.request_history[client_ip][endpoint_type]
        
        while history and history[0] < cutoff:
            history.popleft()
    
    def get_remaining_requests(self, client_ip: str, endpoint_type: str) -> int:
        """Get remaining requests for client"""
        limit, _ = self.rate_limits[endpoint_type]
        current_count = len(self.request_history[client_ip][endpoint_type])
        return max(0, limit - current_count)