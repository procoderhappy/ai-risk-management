"""
Security middleware for request validation and protection
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
from typing import Dict, Set
import re

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for request validation and protection"""
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'union.*select',  # SQL injection
            r'drop.*table',  # SQL injection
            r'exec.*\(',  # Code injection
            r'eval.*\(',  # Code injection
        ]
        self.max_request_size = 50 * 1024 * 1024  # 50MB
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied"}
            )
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"Request too large from IP: {client_ip}")
            return JSONResponse(
                status_code=413,
                content={"error": "Request entity too large"}
            )
        
        # Security headers
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Log request
        process_time = time.time() - start_time
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} - {response.status_code} "
            f"({process_time:.3f}s)"
        )
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def is_suspicious_request(self, request: Request) -> bool:
        """Check if request contains suspicious patterns"""
        # Check URL path
        path = str(request.url.path).lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        
        # Check query parameters
        query = str(request.url.query).lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        logger.warning(f"IP blocked: {ip}")
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip)
        logger.info(f"IP unblocked: {ip}")