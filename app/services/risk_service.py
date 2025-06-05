"""
Risk assessment service
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import RiskAssessment, Document, User
from app.schemas.risk import (
    RiskAssessmentCreate, RiskAssessmentResponse, RiskDashboardData,
    RiskAnalyticsResponse, RiskPredictionRequest, RiskPredictionResponse,
    RiskTrendData, RiskLevel
)
from app.services.ai_service import AIService
import logging
import random

logger = logging.getLogger(__name__)


class RiskService:
    """Service for risk assessment operations"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def create_assessment(
        self, 
        assessment_data: RiskAssessmentCreate, 
        current_user: User, 
        db: Session
    ) -> RiskAssessmentResponse:
        """Create a new risk assessment"""
        try:
            # Generate assessment ID
            assessment_id = str(uuid.uuid4())
            
            # Perform risk analysis
            risk_analysis = await self._perform_risk_analysis(
                assessment_data, current_user, db
            )
            
            # Create database record
            db_assessment = RiskAssessment(
                assessment_id=assessment_id,
                document_id=assessment_data.document_id,
                assessment_type=assessment_data.assessment_type,
                risk_level=risk_analysis["risk_level"],
                risk_score=risk_analysis["risk_score"],
                confidence_score=risk_analysis["confidence"],
                factors=risk_analysis["factors"],
                recommendations=risk_analysis["recommendations"],
                region=assessment_data.region,
                created_by=current_user.id
            )
            
            db.add(db_assessment)
            db.commit()
            db.refresh(db_assessment)
            
            return RiskAssessmentResponse.from_orm(db_assessment)
            
        except Exception as e:
            logger.error(f"Error creating risk assessment: {e}")
            raise
    
    async def _perform_risk_analysis(
        self, 
        assessment_data: RiskAssessmentCreate, 
        current_user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Perform AI-powered risk analysis"""
        try:
            # Get document content if document_id is provided
            document_content = ""
            if assessment_data.document_id:
                document = db.query(Document).filter(
                    Document.id == assessment_data.document_id
                ).first()
                if document:
                    # In a real implementation, you would extract text from the document
                    document_content = f"Document: {document.original_filename}"
            
            # Simulate comprehensive risk analysis
            risk_factors = {
                "market_volatility": random.uniform(0.2, 0.8),
                "regulatory_compliance": random.uniform(0.1, 0.9),
                "operational_efficiency": random.uniform(0.3, 0.7),
                "financial_stability": random.uniform(0.2, 0.8),
                "reputation_risk": random.uniform(0.1, 0.6),
                "cybersecurity": random.uniform(0.2, 0.7)
            }
            
            # Calculate overall risk score
            risk_score = sum(risk_factors.values()) / len(risk_factors)
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.6:
                risk_level = "moderate"
            elif risk_score < 0.8:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                assessment_data.assessment_type, risk_level, risk_factors
            )
            
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "confidence": random.uniform(0.8, 0.95),
                "factors": risk_factors,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            return {
                "risk_level": "unknown",
                "risk_score": 0.0,
                "confidence": 0.0,
                "factors": {},
                "recommendations": []
            }
    
    def _generate_recommendations(
        self, 
        assessment_type: str, 
        risk_level: str, 
        risk_factors: Dict[str, float]
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # Base recommendations by assessment type
        type_recommendations = {
            "credit": [
                "Review credit exposure limits",
                "Enhance borrower assessment procedures",
                "Implement additional collateral requirements"
            ],
            "market": [
                "Diversify investment portfolio",
                "Implement hedging strategies",
                "Monitor market indicators closely"
            ],
            "operational": [
                "Strengthen internal controls",
                "Improve process documentation",
                "Enhance staff training programs"
            ],
            "compliance": [
                "Update compliance procedures",
                "Conduct regular compliance audits",
                "Enhance regulatory monitoring"
            ]
        }
        
        # Add type-specific recommendations
        if assessment_type in type_recommendations:
            recommendations.extend(type_recommendations[assessment_type])
        
        # Add risk level specific recommendations
        if risk_level in ["high", "critical"]:
            recommendations.extend([
                "Immediate management attention required",
                "Consider risk transfer mechanisms",
                "Implement enhanced monitoring"
            ])
        
        # Add factor-specific recommendations
        for factor, score in risk_factors.items():
            if score > 0.7:
                if factor == "market_volatility":
                    recommendations.append("Implement volatility controls")
                elif factor == "regulatory_compliance":
                    recommendations.append("Strengthen compliance framework")
                elif factor == "cybersecurity":
                    recommendations.append("Enhance cybersecurity measures")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def get_dashboard_data(self, region: str, db: Session) -> RiskDashboardData:
        """Get risk dashboard data"""
        try:
            # Get assessments for the region
            query = db.query(RiskAssessment).filter(RiskAssessment.region == region)
            
            # Total assessments
            total_assessments = query.count()
            
            # Risk distribution
            risk_distribution = {}
            for level in ["low", "moderate", "high", "critical"]:
                count = query.filter(RiskAssessment.risk_level == level).count()
                risk_distribution[level] = count
            
            # Average risk score
            avg_score_result = query.with_entities(func.avg(RiskAssessment.risk_score)).scalar()
            average_risk_score = float(avg_score_result) if avg_score_result else 0.0
            
            # High risk items
            high_risk_items = query.filter(
                RiskAssessment.risk_level.in_(["high", "critical"])
            ).count()
            
            # Recent assessments
            recent_assessments = query.order_by(
                RiskAssessment.created_at.desc()
            ).limit(5).all()
            
            return RiskDashboardData(
                total_assessments=total_assessments,
                risk_distribution=risk_distribution,
                average_risk_score=average_risk_score,
                high_risk_items=high_risk_items,
                recent_assessments=[
                    RiskAssessmentResponse.from_orm(assessment) 
                    for assessment in recent_assessments
                ]
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return RiskDashboardData(
                total_assessments=0,
                risk_distribution={},
                average_risk_score=0.0,
                high_risk_items=0,
                recent_assessments=[]
            )
    
    async def get_analytics_data(
        self, 
        region: str, 
        days: int, 
        db: Session
    ) -> RiskAnalyticsResponse:
        """Get risk analytics data"""
        try:
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get dashboard summary
            summary = await self.get_dashboard_data(region, db)
            
            # Generate trend data (simplified)
            trends = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                trends.append(RiskTrendData(
                    date=date,
                    risk_score=random.uniform(0.3, 0.7),
                    assessment_count=random.randint(1, 10)
                ))
            
            # Top risk factors
            top_risk_factors = [
                {"factor": "Market Volatility", "impact": 0.75, "frequency": 45},
                {"factor": "Regulatory Changes", "impact": 0.68, "frequency": 32},
                {"factor": "Operational Risk", "impact": 0.62, "frequency": 28},
                {"factor": "Credit Risk", "impact": 0.58, "frequency": 25}
            ]
            
            # Regional breakdown
            regional_breakdown = {
                region: {
                    "total_assessments": summary.total_assessments,
                    "average_risk_score": summary.average_risk_score,
                    "high_risk_percentage": (summary.high_risk_items / max(summary.total_assessments, 1)) * 100
                }
            }
            
            return RiskAnalyticsResponse(
                summary=summary,
                trends=trends,
                top_risk_factors=top_risk_factors,
                regional_breakdown=regional_breakdown
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            raise
    
    async def predict_risk(
        self, 
        prediction_request: RiskPredictionRequest, 
        current_user: User, 
        db: Session
    ) -> RiskPredictionResponse:
        """Predict risk based on input data"""
        try:
            # Use AI service for prediction
            prediction_data = await self.ai_service.predict_risk_trend(
                [prediction_request.input_data], 
                prediction_request.prediction_horizon
            )
            
            # Determine predicted risk level
            predicted_score = prediction_data.get("current_risk", 0.5)
            if predicted_score < 0.3:
                predicted_level = RiskLevel.LOW
            elif predicted_score < 0.6:
                predicted_level = RiskLevel.MODERATE
            elif predicted_score < 0.8:
                predicted_level = RiskLevel.HIGH
            else:
                predicted_level = RiskLevel.CRITICAL
            
            # Generate key drivers and recommendations
            key_drivers = [
                "Market conditions",
                "Regulatory environment",
                "Operational factors",
                "Financial indicators"
            ]
            
            recommendations = self._generate_recommendations(
                prediction_request.assessment_type,
                predicted_level.value,
                {"predicted_risk": predicted_score}
            )
            
            return RiskPredictionResponse(
                predicted_risk_level=predicted_level,
                predicted_risk_score=predicted_score,
                confidence=prediction_data.get("model_confidence", 0.8),
                key_drivers=key_drivers,
                recommendations=recommendations,
                prediction_date=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in risk prediction: {e}")
            raise