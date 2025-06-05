"""
Risk assessment-related Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AssessmentType(str, Enum):
    CREDIT = "credit"
    MARKET = "market"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    LIQUIDITY = "liquidity"
    REPUTATION = "reputation"


class RiskFactors(BaseModel):
    market_volatility: Optional[float] = None
    credit_exposure: Optional[float] = None
    operational_incidents: Optional[int] = None
    regulatory_changes: Optional[int] = None
    liquidity_ratio: Optional[float] = None
    reputation_score: Optional[float] = None


class RiskAssessmentCreate(BaseModel):
    document_id: Optional[int] = None
    assessment_type: AssessmentType
    region: str = "US"
    custom_factors: Optional[Dict[str, Any]] = None


class RiskAssessmentResponse(BaseModel):
    id: int
    assessment_id: str
    document_id: Optional[int]
    assessment_type: str
    risk_level: Optional[str]
    risk_score: Optional[float]
    confidence_score: Optional[float]
    factors: Optional[Dict[str, Any]]
    recommendations: Optional[List[str]]
    region: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RiskDashboardData(BaseModel):
    total_assessments: int
    risk_distribution: Dict[str, int]
    average_risk_score: float
    high_risk_items: int
    recent_assessments: List[RiskAssessmentResponse]


class RiskTrendData(BaseModel):
    date: datetime
    risk_score: float
    assessment_count: int


class RiskAnalyticsResponse(BaseModel):
    summary: RiskDashboardData
    trends: List[RiskTrendData]
    top_risk_factors: List[Dict[str, Any]]
    regional_breakdown: Dict[str, Dict[str, Any]]


class RiskPredictionRequest(BaseModel):
    assessment_type: AssessmentType
    input_data: Dict[str, Any]
    prediction_horizon: int = 30  # days


class RiskPredictionResponse(BaseModel):
    predicted_risk_level: RiskLevel
    predicted_risk_score: float
    confidence: float
    key_drivers: List[str]
    recommendations: List[str]
    prediction_date: datetime