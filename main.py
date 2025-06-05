#!/usr/bin/env python3
"""
AI Risk Management & Compliance Automation System
Enterprise-grade AI platform for financial risk management
"""

import uvicorn
from app.core.app import create_app
from app.core.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
