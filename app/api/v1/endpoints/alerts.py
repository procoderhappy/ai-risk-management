"""
Alert management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Alert, User
from app.schemas.alert import (
    AlertCreate, AlertUpdate, AlertResponse, AlertDashboard,
    AlertSearchRequest, AlertSearchResponse
)
from app.api.auth.security import get_current_active_user
from app.services.alert_service import AlertService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    alert_service = AlertService()
    alert = await alert_service.create_alert(alert_data, current_user, db)
    
    logger.info(f"Alert created: {alert.alert_id} by {current_user.username}")
    return alert


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to_me: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of alerts"""
    query = db.query(Alert)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if assigned_to_me:
        query = query.filter(Alert.assigned_to == current_user.id)
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert by ID"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update alert"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update alert fields
    update_data = alert_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    # Set resolved timestamp if status is resolved
    if alert_update.status == "resolved":
        from datetime import datetime
        alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert updated: {alert_id} by {current_user.username}")
    return alert


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Acknowledge alert"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "acknowledged"
    alert.assigned_to = current_user.id
    db.commit()
    
    logger.info(f"Alert acknowledged: {alert_id} by {current_user.username}")
    return {"message": "Alert acknowledged successfully"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resolve alert"""
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    from datetime import datetime
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    if not alert.assigned_to:
        alert.assigned_to = current_user.id
    
    db.commit()
    
    logger.info(f"Alert resolved: {alert_id} by {current_user.username}")
    return {"message": "Alert resolved successfully"}


@router.get("/dashboard/data", response_model=AlertDashboard)
async def get_alert_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get alert dashboard data"""
    alert_service = AlertService()
    dashboard_data = await alert_service.get_dashboard_data(current_user, db)
    
    return dashboard_data


@router.post("/search", response_model=AlertSearchResponse)
async def search_alerts(
    search_request: AlertSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search alerts"""
    alert_service = AlertService()
    results = await alert_service.search_alerts(search_request, current_user, db)
    
    return results


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete alert (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    logger.info(f"Alert deleted: {alert_id} by {current_user.username}")
    return {"message": "Alert deleted successfully"}