"""
Alert-related Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    RISK_THRESHOLD = "risk_threshold"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_ERROR = "system_error"
    SECURITY_INCIDENT = "security_incident"
    DATA_ANOMALY = "data_anomaly"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertCreate(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    alert_id: str
    alert_type: str
    severity: str
    title: str
    description: Optional[str]
    source: Optional[str]
    status: str
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertDashboard(BaseModel):
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    alerts_by_type: Dict[str, int]
    alerts_by_severity: Dict[str, int]
    recent_alerts: List[AlertResponse]


class AlertSearchRequest(BaseModel):
    alert_type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    assigned_to: Optional[int] = None
    limit: int = 50


class AlertSearchResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    page: int
    per_page: int