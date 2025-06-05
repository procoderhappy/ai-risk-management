"""
Analytics endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.api.auth.security import get_current_active_user
from app.services.analytics_service import AnalyticsService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/risk/trends")
async def get_risk_trends(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    assessment_type: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk trends analytics"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    analytics_service = AnalyticsService()
    trends_data = await analytics_service.get_risk_trends(
        filter_region, period, assessment_type, db
    )
    
    return trends_data


@router.get("/risk/heatmap")
async def get_risk_heatmap(
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk heatmap data"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    analytics_service = AnalyticsService()
    heatmap_data = await analytics_service.get_risk_heatmap(filter_region, db)
    
    return heatmap_data


@router.get("/compliance/trends")
async def get_compliance_trends(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    regulation_type: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get compliance trends analytics"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    analytics_service = AnalyticsService()
    trends_data = await analytics_service.get_compliance_trends(
        filter_region, period, regulation_type, db
    )
    
    return trends_data


@router.get("/documents/insights")
async def get_document_insights(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document processing insights"""
    analytics_service = AnalyticsService()
    insights_data = await analytics_service.get_document_insights(period, db)
    
    return insights_data


@router.get("/alerts/patterns")
async def get_alert_patterns(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert patterns analytics"""
    analytics_service = AnalyticsService()
    patterns_data = await analytics_service.get_alert_patterns(period, db)
    
    return patterns_data


@router.get("/performance/metrics")
async def get_performance_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get system performance analytics"""
    analytics_service = AnalyticsService()
    performance_data = await analytics_service.get_performance_analytics(period, db)
    
    return performance_data


@router.get("/regional/comparison")
async def get_regional_comparison(
    metric: str = Query("risk_score", regex="^(risk_score|compliance_score|alert_count)$"),
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get regional comparison analytics (admin only)"""
    if current_user.role != "admin":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    analytics_service = AnalyticsService()
    comparison_data = await analytics_service.get_regional_comparison(metric, period, db)
    
    return comparison_data


@router.get("/predictions/risk")
async def get_risk_predictions(
    assessment_type: str = Query(...),
    horizon_days: int = Query(30, ge=1, le=365),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk predictions"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    analytics_service = AnalyticsService()
    predictions_data = await analytics_service.get_risk_predictions(
        assessment_type, horizon_days, filter_region, db
    )
    
    return predictions_data


@router.get("/correlations")
async def get_risk_correlations(
    period: str = Query("90d", regex="^(30d|90d|1y)$"),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk factor correlations"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    analytics_service = AnalyticsService()
    correlations_data = await analytics_service.get_risk_correlations(
        filter_region, period, db
    )
    
    return correlations_data