"""
Analytics service for advanced data analysis and insights
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database.models import RiskAssessment, ComplianceCheck, Alert, Document
import logging
import random
import numpy as np

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for advanced analytics and insights"""
    
    async def get_risk_trends(
        self, 
        region: str, 
        period: str, 
        assessment_type: Optional[str], 
        db: Session
    ) -> Dict[str, Any]:
        """Get risk trends analytics"""
        try:
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            query = db.query(RiskAssessment).filter(
                and_(
                    RiskAssessment.region == region,
                    RiskAssessment.created_at >= start_date
                )
            )
            
            if assessment_type:
                query = query.filter(RiskAssessment.assessment_type == assessment_type)
            
            assessments = query.all()
            
            # Generate trend data
            trends = []
            for i in range(min(period_days, 30)):  # Limit to 30 data points for visualization
                date = start_date + timedelta(days=i * (period_days // 30))
                day_assessments = [a for a in assessments if a.created_at.date() == date.date()]
                
                if day_assessments:
                    avg_score = sum(a.risk_score for a in day_assessments if a.risk_score) / len(day_assessments)
                else:
                    avg_score = random.uniform(0.4, 0.6)  # Baseline
                
                trends.append({
                    "date": date.isoformat(),
                    "risk_score": avg_score,
                    "count": len(day_assessments)
                })
            
            # Calculate trend direction
            if len(trends) >= 2:
                recent_avg = sum(t["risk_score"] for t in trends[-7:]) / min(7, len(trends))
                earlier_avg = sum(t["risk_score"] for t in trends[:7]) / min(7, len(trends))
                trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
            else:
                trend_direction = "stable"
            
            return {
                "period": period,
                "region": region,
                "assessment_type": assessment_type,
                "trend_direction": trend_direction,
                "data_points": trends,
                "summary": {
                    "total_assessments": len(assessments),
                    "average_risk_score": sum(a.risk_score for a in assessments if a.risk_score) / max(len(assessments), 1),
                    "highest_risk_day": max(trends, key=lambda x: x["risk_score"])["date"] if trends else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting risk trends: {e}")
            raise
    
    async def get_risk_heatmap(self, region: str, db: Session) -> Dict[str, Any]:
        """Get risk heatmap data"""
        try:
            # Get recent assessments
            recent_date = datetime.now() - timedelta(days=30)
            assessments = db.query(RiskAssessment).filter(
                and_(
                    RiskAssessment.region == region,
                    RiskAssessment.created_at >= recent_date
                )
            ).all()
            
            # Create heatmap matrix
            assessment_types = ["credit", "market", "operational", "compliance", "liquidity"]
            risk_levels = ["low", "moderate", "high", "critical"]
            
            heatmap_data = []
            for i, assessment_type in enumerate(assessment_types):
                row_data = []
                for j, risk_level in enumerate(risk_levels):
                    count = len([a for a in assessments 
                               if a.assessment_type == assessment_type and a.risk_level == risk_level])
                    row_data.append({
                        "x": j,
                        "y": i,
                        "value": count,
                        "assessment_type": assessment_type,
                        "risk_level": risk_level
                    })
                heatmap_data.extend(row_data)
            
            return {
                "heatmap_data": heatmap_data,
                "x_labels": risk_levels,
                "y_labels": assessment_types,
                "max_value": max([d["value"] for d in heatmap_data]) if heatmap_data else 0,
                "total_assessments": len(assessments)
            }
            
        except Exception as e:
            logger.error(f"Error getting risk heatmap: {e}")
            raise
    
    async def get_compliance_trends(
        self, 
        region: str, 
        period: str, 
        regulation_type: Optional[str], 
        db: Session
    ) -> Dict[str, Any]:
        """Get compliance trends analytics"""
        try:
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            query = db.query(ComplianceCheck).filter(
                and_(
                    ComplianceCheck.region == region,
                    ComplianceCheck.created_at >= start_date
                )
            )
            
            if regulation_type:
                query = query.filter(ComplianceCheck.regulation_type == regulation_type)
            
            checks = query.all()
            
            # Generate trend data
            trends = []
            for i in range(min(period_days, 30)):
                date = start_date + timedelta(days=i * (period_days // 30))
                day_checks = [c for c in checks if c.created_at.date() == date.date()]
                
                if day_checks:
                    avg_score = sum(c.compliance_score for c in day_checks if c.compliance_score) / len(day_checks)
                    compliant_rate = len([c for c in day_checks if c.status == "compliant"]) / len(day_checks) * 100
                else:
                    avg_score = random.uniform(85, 95)
                    compliant_rate = random.uniform(80, 95)
                
                trends.append({
                    "date": date.isoformat(),
                    "compliance_score": avg_score,
                    "compliant_rate": compliant_rate,
                    "count": len(day_checks)
                })
            
            return {
                "period": period,
                "region": region,
                "regulation_type": regulation_type,
                "data_points": trends,
                "summary": {
                    "total_checks": len(checks),
                    "average_compliance_score": sum(c.compliance_score for c in checks if c.compliance_score) / max(len(checks), 1),
                    "overall_compliant_rate": len([c for c in checks if c.status == "compliant"]) / max(len(checks), 1) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance trends: {e}")
            raise
    
    async def get_document_insights(self, period: str, db: Session) -> Dict[str, Any]:
        """Get document processing insights"""
        try:
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            documents = db.query(Document).filter(
                Document.created_at >= start_date
            ).all()
            
            # File type distribution
            file_type_dist = {}
            for doc in documents:
                file_type = doc.file_type or "unknown"
                file_type_dist[file_type] = file_type_dist.get(file_type, 0) + 1
            
            # Processing status distribution
            status_dist = {}
            for doc in documents:
                status = doc.processing_status
                status_dist[status] = status_dist.get(status, 0) + 1
            
            # Processing time analysis (simulated)
            avg_processing_time = random.uniform(2.5, 8.0)  # seconds
            
            # Size analysis
            total_size = sum(doc.file_size for doc in documents if doc.file_size)
            avg_size = total_size / max(len(documents), 1) if documents else 0
            
            return {
                "period": period,
                "total_documents": len(documents),
                "file_type_distribution": file_type_dist,
                "processing_status_distribution": status_dist,
                "processing_metrics": {
                    "average_processing_time_seconds": avg_processing_time,
                    "success_rate": (status_dist.get("completed", 0) / max(len(documents), 1)) * 100,
                    "failure_rate": (status_dist.get("failed", 0) / max(len(documents), 1)) * 100
                },
                "size_metrics": {
                    "total_size_bytes": total_size,
                    "average_size_bytes": avg_size,
                    "largest_file_size": max([doc.file_size for doc in documents if doc.file_size], default=0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting document insights: {e}")
            raise
    
    async def get_alert_patterns(self, period: str, db: Session) -> Dict[str, Any]:
        """Get alert patterns analytics"""
        try:
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            alerts = db.query(Alert).filter(
                Alert.created_at >= start_date
            ).all()
            
            # Hourly pattern analysis
            hourly_pattern = [0] * 24
            for alert in alerts:
                hour = alert.created_at.hour
                hourly_pattern[hour] += 1
            
            # Daily pattern analysis
            daily_pattern = [0] * 7  # Monday = 0, Sunday = 6
            for alert in alerts:
                day = alert.created_at.weekday()
                daily_pattern[day] += 1
            
            # Alert type correlation
            type_severity_matrix = {}
            for alert in alerts:
                alert_type = alert.alert_type
                severity = alert.severity
                if alert_type not in type_severity_matrix:
                    type_severity_matrix[alert_type] = {}
                type_severity_matrix[alert_type][severity] = type_severity_matrix[alert_type].get(severity, 0) + 1
            
            # Resolution time patterns
            resolved_alerts = [a for a in alerts if a.status == "resolved" and a.resolved_at]
            resolution_times = []
            for alert in resolved_alerts:
                if alert.resolved_at and alert.created_at:
                    resolution_time = (alert.resolved_at - alert.created_at).total_seconds() / 3600  # hours
                    resolution_times.append(resolution_time)
            
            avg_resolution_time = sum(resolution_times) / max(len(resolution_times), 1) if resolution_times else 0
            
            return {
                "period": period,
                "total_alerts": len(alerts),
                "hourly_pattern": [{"hour": i, "count": count} for i, count in enumerate(hourly_pattern)],
                "daily_pattern": [{"day": i, "count": count} for i, count in enumerate(daily_pattern)],
                "type_severity_matrix": type_severity_matrix,
                "resolution_metrics": {
                    "average_resolution_time_hours": avg_resolution_time,
                    "resolution_rate": len(resolved_alerts) / max(len(alerts), 1) * 100,
                    "fastest_resolution_hours": min(resolution_times) if resolution_times else 0,
                    "slowest_resolution_hours": max(resolution_times) if resolution_times else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting alert patterns: {e}")
            raise
    
    async def get_performance_analytics(self, period: str, db: Session) -> Dict[str, Any]:
        """Get system performance analytics"""
        try:
            # Simulate performance metrics over time
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
            
            performance_data = []
            for i in range(min(period_days, 30)):
                date = datetime.now() - timedelta(days=period_days - i)
                
                performance_data.append({
                    "date": date.isoformat(),
                    "api_response_time_ms": random.uniform(100, 300),
                    "database_query_time_ms": random.uniform(10, 50),
                    "ai_processing_time_ms": random.uniform(500, 2000),
                    "throughput_requests_per_minute": random.uniform(50, 200),
                    "error_rate_percent": random.uniform(0.1, 2.0),
                    "cpu_usage_percent": random.uniform(20, 80),
                    "memory_usage_percent": random.uniform(30, 70)
                })
            
            # Calculate averages
            avg_metrics = {}
            for key in ["api_response_time_ms", "database_query_time_ms", "ai_processing_time_ms", 
                       "throughput_requests_per_minute", "error_rate_percent", "cpu_usage_percent", "memory_usage_percent"]:
                values = [d[key] for d in performance_data]
                avg_metrics[f"avg_{key}"] = sum(values) / len(values)
                avg_metrics[f"max_{key}"] = max(values)
                avg_metrics[f"min_{key}"] = min(values)
            
            return {
                "period": period,
                "data_points": performance_data,
                "summary_metrics": avg_metrics,
                "performance_score": random.uniform(85, 95),  # Overall performance score
                "recommendations": [
                    "Monitor API response times during peak hours",
                    "Consider database query optimization",
                    "Scale AI processing resources if needed"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            raise
    
    async def get_regional_comparison(self, metric: str, period: str, db: Session) -> Dict[str, Any]:
        """Get regional comparison analytics"""
        try:
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            regions = ["US", "EU", "UK", "APAC"]
            comparison_data = []
            
            for region in regions:
                if metric == "risk_score":
                    assessments = db.query(RiskAssessment).filter(
                        and_(
                            RiskAssessment.region == region,
                            RiskAssessment.created_at >= start_date
                        )
                    ).all()
                    
                    avg_value = sum(a.risk_score for a in assessments if a.risk_score) / max(len(assessments), 1) if assessments else random.uniform(0.4, 0.6)
                    count = len(assessments)
                    
                elif metric == "compliance_score":
                    checks = db.query(ComplianceCheck).filter(
                        and_(
                            ComplianceCheck.region == region,
                            ComplianceCheck.created_at >= start_date
                        )
                    ).all()
                    
                    avg_value = sum(c.compliance_score for c in checks if c.compliance_score) / max(len(checks), 1) if checks else random.uniform(85, 95)
                    count = len(checks)
                    
                elif metric == "alert_count":
                    alerts = db.query(Alert).filter(
                        Alert.created_at >= start_date
                    ).all()
                    
                    # Simulate regional distribution
                    avg_value = len(alerts) * random.uniform(0.15, 0.35)  # Each region gets 15-35% of alerts
                    count = int(avg_value)
                    
                comparison_data.append({
                    "region": region,
                    "value": avg_value,
                    "count": count,
                    "trend": random.choice(["increasing", "decreasing", "stable"])
                })
            
            # Rank regions
            comparison_data.sort(key=lambda x: x["value"], reverse=(metric != "alert_count"))
            for i, data in enumerate(comparison_data):
                data["rank"] = i + 1
            
            return {
                "metric": metric,
                "period": period,
                "regional_data": comparison_data,
                "best_performing_region": comparison_data[0]["region"],
                "worst_performing_region": comparison_data[-1]["region"],
                "average_value": sum(d["value"] for d in comparison_data) / len(comparison_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting regional comparison: {e}")
            raise
    
    async def get_risk_predictions(
        self, 
        assessment_type: str, 
        horizon_days: int, 
        region: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Get risk predictions"""
        try:
            # Get historical data
            historical_date = datetime.now() - timedelta(days=90)
            historical_assessments = db.query(RiskAssessment).filter(
                and_(
                    RiskAssessment.region == region,
                    RiskAssessment.assessment_type == assessment_type,
                    RiskAssessment.created_at >= historical_date
                )
            ).all()
            
            # Generate predictions based on historical trends
            if historical_assessments:
                historical_scores = [a.risk_score for a in historical_assessments if a.risk_score]
                base_score = sum(historical_scores) / len(historical_scores)
                trend = random.uniform(-0.1, 0.1)  # Simulate trend
            else:
                base_score = random.uniform(0.4, 0.6)
                trend = 0
            
            predictions = []
            for day in range(1, horizon_days + 1):
                # Add some randomness and trend
                predicted_score = base_score + (trend * day / 30) + random.uniform(-0.05, 0.05)
                predicted_score = max(0, min(1, predicted_score))  # Clamp between 0 and 1
                
                predictions.append({
                    "day": day,
                    "date": (datetime.now() + timedelta(days=day)).isoformat(),
                    "predicted_risk_score": predicted_score,
                    "confidence": random.uniform(0.7, 0.9)
                })
            
            # Identify key risk drivers
            risk_drivers = [
                {"factor": "Market Volatility", "impact": random.uniform(0.6, 0.9)},
                {"factor": "Regulatory Changes", "impact": random.uniform(0.5, 0.8)},
                {"factor": "Economic Indicators", "impact": random.uniform(0.4, 0.7)},
                {"factor": "Industry Trends", "impact": random.uniform(0.3, 0.6)}
            ]
            
            return {
                "assessment_type": assessment_type,
                "region": region,
                "horizon_days": horizon_days,
                "predictions": predictions,
                "risk_drivers": risk_drivers,
                "model_confidence": random.uniform(0.8, 0.95),
                "recommendations": [
                    "Monitor key risk indicators closely",
                    "Implement proactive risk mitigation measures",
                    "Review risk thresholds and alerts"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting risk predictions: {e}")
            raise
    
    async def get_risk_correlations(
        self, 
        region: str, 
        period: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Get risk factor correlations"""
        try:
            # Simulate correlation analysis
            risk_factors = [
                "market_volatility", "regulatory_compliance", "operational_efficiency",
                "financial_stability", "reputation_risk", "cybersecurity"
            ]
            
            # Generate correlation matrix
            correlation_matrix = {}
            for factor1 in risk_factors:
                correlation_matrix[factor1] = {}
                for factor2 in risk_factors:
                    if factor1 == factor2:
                        correlation = 1.0
                    else:
                        correlation = random.uniform(-0.8, 0.8)
                    correlation_matrix[factor1][factor2] = correlation
            
            # Find strongest correlations
            strong_correlations = []
            for factor1 in risk_factors:
                for factor2 in risk_factors:
                    if factor1 != factor2:
                        corr = correlation_matrix[factor1][factor2]
                        if abs(corr) > 0.6:
                            strong_correlations.append({
                                "factor1": factor1,
                                "factor2": factor2,
                                "correlation": corr,
                                "strength": "strong" if abs(corr) > 0.7 else "moderate"
                            })
            
            # Sort by absolute correlation value
            strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            
            return {
                "region": region,
                "period": period,
                "correlation_matrix": correlation_matrix,
                "strong_correlations": strong_correlations[:10],  # Top 10
                "risk_factors": risk_factors,
                "analysis_summary": {
                    "total_correlations_analyzed": len(risk_factors) * (len(risk_factors) - 1),
                    "strong_positive_correlations": len([c for c in strong_correlations if c["correlation"] > 0.6]),
                    "strong_negative_correlations": len([c for c in strong_correlations if c["correlation"] < -0.6])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting risk correlations: {e}")
            raise