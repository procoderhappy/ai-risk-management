"""
Compliance endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import ComplianceCheck, User
from app.schemas.compliance import (
    ComplianceCheckCreate, ComplianceCheckResponse, ComplianceDashboard,
    ComplianceReport, ComplianceAuditRequest, ComplianceAuditResponse
)
from app.api.auth.security import get_current_active_user, check_region_access
from app.services.compliance_service import ComplianceService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/checks", response_model=ComplianceCheckResponse)
async def create_compliance_check(
    check_data: ComplianceCheckCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new compliance check"""
    # Check region access
    if not check_region_access(current_user, check_data.region):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this region"
        )
    
    compliance_service = ComplianceService()
    check = await compliance_service.create_compliance_check(
        check_data, current_user, db
    )
    
    logger.info(f"Compliance check created: {check.check_id} by {current_user.username}")
    return check


@router.get("/checks", response_model=List[ComplianceCheckResponse])
async def get_compliance_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    regulation_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of compliance checks"""
    query = db.query(ComplianceCheck)
    
    # Apply region filter based on user permissions
    if current_user.role != "admin":
        query = query.filter(ComplianceCheck.region == current_user.region)
    elif region:
        query = query.filter(ComplianceCheck.region == region)
    
    if regulation_type:
        query = query.filter(ComplianceCheck.regulation_type == regulation_type)
    if status:
        query = query.filter(ComplianceCheck.status == status)
    
    checks = query.offset(skip).limit(limit).all()
    return checks


@router.get("/checks/{check_id}", response_model=ComplianceCheckResponse)
async def get_compliance_check(
    check_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get compliance check by ID"""
    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.check_id == check_id
    ).first()
    
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found"
        )
    
    # Check region access
    if not check_region_access(current_user, check.region):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this region"
        )
    
    return check


@router.get("/dashboard", response_model=ComplianceDashboard)
async def get_compliance_dashboard(
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get compliance dashboard data"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    compliance_service = ComplianceService()
    dashboard_data = await compliance_service.get_dashboard_data(filter_region, db)
    
    return dashboard_data


@router.get("/status")
async def get_compliance_status(
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall compliance status"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    compliance_service = ComplianceService()
    status_data = await compliance_service.get_compliance_status(filter_region, db)
    
    return status_data


@router.post("/audit", response_model=ComplianceAuditResponse)
async def start_compliance_audit(
    audit_request: ComplianceAuditRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a compliance audit"""
    # Only managers and admins can start audits
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required"
        )
    
    compliance_service = ComplianceService()
    audit = await compliance_service.start_audit(audit_request, current_user, db)
    
    logger.info(f"Compliance audit started by {current_user.username}")
    return audit


@router.get("/reports", response_model=List[ComplianceReport])
async def get_compliance_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get compliance reports"""
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    compliance_service = ComplianceService()
    reports = await compliance_service.get_reports(filter_region, skip, limit, db)
    
    return reports


@router.post("/reports/generate")
async def generate_compliance_report(
    region: Optional[str] = Query(None),
    report_type: str = Query("comprehensive"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a new compliance report"""
    # Only managers and admins can generate reports
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required"
        )
    
    # Determine region filter
    if current_user.role == "admin" and region:
        filter_region = region
    else:
        filter_region = current_user.region
    
    compliance_service = ComplianceService()
    report = await compliance_service.generate_report(
        filter_region, report_type, current_user, db
    )
    
    logger.info(f"Compliance report generated by {current_user.username}")
    return {"message": "Report generation started", "report_id": report.report_id}