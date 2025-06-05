"""
Audit middleware for logging security events and user actions
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from typing import Optional
from app.core.logging import get_logger

audit_logger = get_logger('audit')


class AuditMiddleware(BaseHTTPMiddleware):
    """Audit middleware for security and compliance logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.sensitive_paths = [
            "/auth/",
            "/admin/",
            "/api/v1/users/",
            "/api/v1/documents/",
            "/api/v1/risk-assessments/",
            "/api/v1/compliance/"
        ]
        self.sensitive_headers = [
            "authorization",
            "x-api-key",
            "cookie"
        ]
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request information
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Check if this is a sensitive operation
        is_sensitive = any(sensitive_path in path for sensitive_path in self.sensitive_paths)
        
        # Get user information if available
        user_info = await self.extract_user_info(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log audit event
        if is_sensitive or response.status_code >= 400:
            await self.log_audit_event(
                request=request,
                response=response,
                client_ip=client_ip,
                user_agent=user_agent,
                user_info=user_info,
                process_time=process_time
            )
        
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
    
    async def extract_user_info(self, request: Request) -> Optional[dict]:
        """Extract user information from request"""
        try:
            # Try to get user from JWT token
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # This would normally decode the JWT token
                # For now, we'll just note that authentication was attempted
                return {"auth_type": "bearer_token"}
            
            # Check for API key
            api_key = request.headers.get("x-api-key")
            if api_key:
                return {"auth_type": "api_key"}
            
            return None
        except Exception as e:
            audit_logger.error(f"Error extracting user info: {e}")
            return None
    
    async def log_audit_event(
        self,
        request: Request,
        response,
        client_ip: str,
        user_agent: str,
        user_info: Optional[dict],
        process_time: float
    ):
        """Log audit event"""
        
        # Prepare audit data
        audit_data = {
            "timestamp": time.time(),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "status_code": response.status_code,
            "process_time": round(process_time, 3),
            "user_info": user_info,
            "request_size": request.headers.get("content-length"),
            "response_size": response.headers.get("content-length"),
        }
        
        # Add security flags
        audit_data["security_flags"] = {
            "authentication_required": self.requires_authentication(request.url.path),
            "sensitive_operation": self.is_sensitive_operation(request.url.path),
            "admin_operation": "/admin/" in request.url.path,
            "data_modification": request.method in ["POST", "PUT", "PATCH", "DELETE"],
        }
        
        # Log the event
        if response.status_code >= 400:
            audit_logger.warning(f"FAILED_REQUEST: {json.dumps(audit_data)}")
        elif audit_data["security_flags"]["sensitive_operation"]:
            audit_logger.info(f"SENSITIVE_OPERATION: {json.dumps(audit_data)}")
        else:
            audit_logger.info(f"REQUEST: {json.dumps(audit_data)}")
    
    def requires_authentication(self, path: str) -> bool:
        """Check if path requires authentication"""
        public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
        return path not in public_paths and not path.startswith("/static/")
    
    def is_sensitive_operation(self, path: str) -> bool:
        """Check if operation is sensitive"""
        return any(sensitive_path in path for sensitive_path in self.sensitive_paths)
    
    def sanitize_headers(self, headers: dict) -> dict:
        """Remove sensitive headers from logging"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized