"""
Risk assessment endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import RiskAssessment, User
from app.schemas.risk import (
    RiskAssessmentCreate, RiskAssessmentResponse, RiskDashboardData,
    RiskAnalyticsResponse, RiskPredictionRequest, RiskPredictionResponse
)
from app.api.auth.security import get_current_active_user, check_region_access
from app.services.risk_service import RiskService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=RiskAssessmentResponse)
async def create_risk_assessment(
    assessment_data: RiskAssessmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new risk assessment"""
    # Check region access
    if not check_region_access(current_user, assessment_data.region):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this region"
        )
    
    risk_service = RiskService()
    assessment = await risk_service.create_assessment(
        assessment_data, current_user, db
    )
    
    logger.info(f"Risk assessment created: {assessment.assessment_id} by {current_user.username}")
    return assessment


@router.get("/", response_model=List[RiskAssessmentResponse])
async def get_risk_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    assessment_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of risk assessments"""
    query = db.query(RiskAssessment)
    
    # Apply region filter based on user permissions
    if current_user.role != "admin":
        query = query.filter(RiskAssessment.region == current_user.region)
    elif region:
        query = query.filter(RiskAssessment.region == region)
    
    if assessment_type:
        query = query.filter(RiskAssessment.assessment_type == assessment_type)
    if risk_level:
        query = query.filter(RiskAssessment.risk_level == risk_level)
    
    assessments = query.offset(skip).limit(limit).all()
    return assessments


@router.get("/{assessment_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk assessment by ID"""
    assessment = db.query(RiskAssessment).filter(
        RiskAssessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found"
        )
    
    # Check region access
    if not check_region_access(current_user, assessment.region):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this region"
        )
    
    return assessment


@router.get("/dashboard/data", response_model=RiskDashboardData)
async def get_risk_dashboard_data(
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk dashboard data"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    risk_service = RiskService()
    dashboard_data = await risk_service.get_dashboard_data(filter_region, db)
    
    return dashboard_data


@router.get("/analytics/trends", response_model=RiskAnalyticsResponse)
async def get_risk_analytics(
    days: int = Query(30, ge=1, le=365),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk analytics and trends"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    risk_service = RiskService()
    analytics_data = await risk_service.get_analytics_data(filter_region, days, db)
    
    return analytics_data


@router.post("/predict", response_model=RiskPredictionResponse)
async def predict_risk(
    prediction_request: RiskPredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Predict risk based on input data"""
    risk_service = RiskService()
    prediction = await risk_service.predict_risk(prediction_request, current_user, db)
    
    logger.info(f"Risk prediction generated for {prediction_request.assessment_type} by {current_user.username}")
    return prediction


@router.delete("/{assessment_id}")
async def delete_risk_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete risk assessment"""
    assessment = db.query(RiskAssessment).filter(
        RiskAssessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found"
        )
    
    # Check permissions
    if (current_user.role not in ["admin", "manager"] and 
        assessment.created_by != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check region access
    if not check_region_access(current_user, assessment.region):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this region"
        )
    
    db.delete(assessment)
    db.commit()
    
    logger.info(f"Risk assessment deleted: {assessment_id} by {current_user.username}")
    return {"message": "Risk assessment deleted successfully"}