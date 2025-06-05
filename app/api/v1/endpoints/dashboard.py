"""
Dashboard endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.api.auth.security import get_current_active_user
from app.services.dashboard_service import DashboardService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard overview data"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    dashboard_service = DashboardService()
    overview_data = await dashboard_service.get_overview(filter_region, current_user, db)
    
    return overview_data


@router.get("/metrics")
async def get_dashboard_metrics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for specified period"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    dashboard_service = DashboardService()
    metrics_data = await dashboard_service.get_metrics(filter_region, period, db)
    
    return metrics_data


@router.get("/charts/risk-trends")
async def get_risk_trends_chart(
    days: int = Query(30, ge=7, le=365),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk trends chart data"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    dashboard_service = DashboardService()
    chart_data = await dashboard_service.get_risk_trends_chart(filter_region, days, db)
    
    return chart_data


@router.get("/charts/compliance-status")
async def get_compliance_status_chart(
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get compliance status chart data"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    dashboard_service = DashboardService()
    chart_data = await dashboard_service.get_compliance_status_chart(filter_region, db)
    
    return chart_data


@router.get("/charts/alert-distribution")
async def get_alert_distribution_chart(
    period: str = Query("30d", regex="^(7d|30d|90d)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert distribution chart data"""
    dashboard_service = DashboardService()
    chart_data = await dashboard_service.get_alert_distribution_chart(period, db)
    
    return chart_data


@router.get("/charts/document-processing")
async def get_document_processing_chart(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document processing chart data"""
    dashboard_service = DashboardService()
    chart_data = await dashboard_service.get_document_processing_chart(days, db)
    
    return chart_data


@router.get("/real-time/status")
async def get_real_time_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get real-time system status"""
    dashboard_service = DashboardService()
    status_data = await dashboard_service.get_real_time_status(db)
    
    return status_data


@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    dashboard_service = DashboardService()
    performance_data = await dashboard_service.get_performance_metrics(db)
    
    return performance_data