"""
Compliance-related Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ComplianceStatus(str, Enum):
    PENDING = "pending"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REVIEW_REQUIRED = "review_required"


class RegulationType(str, Enum):
    GDPR = "GDPR"
    SOX = "SOX"
    BASEL_III = "Basel III"
    MIFID_II = "MiFID II"
    DODD_FRANK = "Dodd-Frank"
    PCI_DSS = "PCI DSS"
    HIPAA = "HIPAA"


class ComplianceCheckResponse(BaseModel):
    id: int
    check_id: str
    regulation_type: str
    region: str
    status: str
    compliance_score: Optional[float]
    findings: Optional[Dict[str, Any]]
    recommendations: Optional[List[str]]
    next_review_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ComplianceCheckCreate(BaseModel):
    regulation_type: RegulationType
    region: str
    custom_parameters: Optional[Dict[str, Any]] = None


class ComplianceDashboard(BaseModel):
    overall_status: ComplianceStatus
    compliance_score: float
    total_checks: int
    compliant_checks: int
    non_compliant_checks: int
    pending_checks: int
    last_audit_date: Optional[datetime]
    next_audit_date: Optional[datetime]
    regional_compliance: Dict[str, Dict[str, Any]]


class ComplianceReport(BaseModel):
    report_id: str
    report_type: str
    region: str
    period_start: datetime
    period_end: datetime
    summary: Dict[str, Any]
    detailed_findings: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime
    generated_by: int


class ComplianceAuditRequest(BaseModel):
    regulation_types: List[RegulationType]
    regions: List[str]
    audit_scope: str = "full"  # full, partial, targeted
    custom_criteria: Optional[Dict[str, Any]] = None


class ComplianceAuditResponse(BaseModel):
    audit_id: str
    status: str
    progress: float
    estimated_completion: Optional[datetime]
    preliminary_findings: Optional[List[str]]
    created_at: datetime