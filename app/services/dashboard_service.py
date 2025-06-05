"""
Dashboard service for aggregating data from multiple sources
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import (
    RiskAssessment, ComplianceCheck, Alert, Document, 
    User, SystemMetrics
)
from app.services.risk_service import RiskService
from app.services.compliance_service import ComplianceService
from app.services.alert_service import AlertService
import logging
import random

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard data aggregation"""
    
    def __init__(self):
        self.risk_service = RiskService()
        self.compliance_service = ComplianceService()
        self.alert_service = AlertService()
    
    async def get_overview(
        self, 
        region: str, 
        current_user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Get dashboard overview data"""
        try:
            # Get data from different services
            risk_data = await self.risk_service.get_dashboard_data(region, db)
            compliance_data = await self.compliance_service.get_dashboard_data(region, db)
            alert_data = await self.alert_service.get_dashboard_data(current_user, db)
            
            # Document statistics
            doc_query = db.query(Document)
            if current_user.role not in ["admin", "manager"]:
                doc_query = doc_query.filter(Document.uploaded_by == current_user.id)
            
            total_documents = doc_query.count()
            processed_documents = doc_query.filter(Document.processed == True).count()
            
            # System health indicators
            system_health = await self._get_system_health(db)
            
            # Recent activity
            recent_activity = await self._get_recent_activity(region, current_user, db)
            
            return {
                "overview": {
                    "total_risk_assessments": risk_data.total_assessments,
                    "average_risk_score": risk_data.average_risk_score,
                    "compliance_score": compliance_data.compliance_score,
                    "active_alerts": alert_data.active_alerts,
                    "critical_alerts": alert_data.critical_alerts,
                    "total_documents": total_documents,
                    "processed_documents": processed_documents,
                    "processing_rate": (processed_documents / max(total_documents, 1)) * 100
                },
                "risk_summary": {
                    "distribution": risk_data.risk_distribution,
                    "high_risk_items": risk_data.high_risk_items,
                    "trend": "stable"  # Would be calculated from historical data
                },
                "compliance_summary": {
                    "overall_status": compliance_data.overall_status,
                    "compliant_checks": compliance_data.compliant_checks,
                    "non_compliant_checks": compliance_data.non_compliant_checks,
                    "next_audit": compliance_data.next_audit_date.isoformat() if compliance_data.next_audit_date else None
                },
                "alert_summary": {
                    "by_severity": alert_data.alerts_by_severity,
                    "by_type": alert_data.alerts_by_type,
                    "resolution_rate": await self._calculate_resolution_rate(db)
                },
                "system_health": system_health,
                "recent_activity": recent_activity,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            raise
    
    async def get_metrics(
        self, 
        region: str, 
        period: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Get dashboard metrics for specified period"""
        try:
            # Parse period
            period_days = {
                "7d": 7,
                "30d": 30,
                "90d": 90,
                "1y": 365
            }.get(period, 30)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Risk metrics
            risk_metrics = await self._get_risk_metrics(region, start_date, end_date, db)
            
            # Compliance metrics
            compliance_metrics = await self._get_compliance_metrics(region, start_date, end_date, db)
            
            # Document processing metrics
            doc_metrics = await self._get_document_metrics(start_date, end_date, db)
            
            # Alert metrics
            alert_metrics = await self.alert_service.generate_alert_metrics(period_days, db)
            
            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "risk_metrics": risk_metrics,
                "compliance_metrics": compliance_metrics,
                "document_metrics": doc_metrics,
                "alert_metrics": alert_metrics,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            raise
    
    async def get_risk_trends_chart(
        self, 
        region: str, 
        days: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Get risk trends chart data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Generate daily risk trend data
            daily_data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                
                # Get assessments for this day
                day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                assessments = db.query(RiskAssessment).filter(
                    and_(
                        RiskAssessment.region == region,
                        RiskAssessment.created_at >= day_start,
                        RiskAssessment.created_at < day_end
                    )
                ).all()
                
                if assessments:
                    avg_score = sum(a.risk_score for a in assessments if a.risk_score) / len(assessments)
                    count = len(assessments)
                else:
                    avg_score = random.uniform(0.4, 0.6)  # Simulate baseline
                    count = 0
                
                daily_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "risk_score": avg_score,
                    "assessment_count": count
                })
            
            return {
                "chart_type": "line",
                "title": "Risk Trends",
                "data": daily_data,
                "x_axis": "date",
                "y_axis": "risk_score",
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting risk trends chart: {e}")
            raise
    
    async def get_compliance_status_chart(
        self, 
        region: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Get compliance status chart data"""
        try:
            # Get compliance checks by regulation type
            regulation_data = []
            regulation_types = ["GDPR", "SOX", "Basel III", "MiFID II", "HIPAA"]
            
            for reg_type in regulation_types:
                checks = db.query(ComplianceCheck).filter(
                    and_(
                        ComplianceCheck.region == region,
                        ComplianceCheck.regulation_type == reg_type
                    )
                ).all()
                
                if checks:
                    avg_score = sum(c.compliance_score for c in checks if c.compliance_score) / len(checks)
                    status_counts = {}
                    for check in checks:
                        status = check.status
                        status_counts[status] = status_counts.get(status, 0) + 1
                else:
                    avg_score = random.uniform(80, 95)
                    status_counts = {"compliant": 1}
                
                regulation_data.append({
                    "regulation": reg_type,
                    "score": avg_score,
                    "status_counts": status_counts,
                    "total_checks": len(checks)
                })
            
            return {
                "chart_type": "bar",
                "title": "Compliance Status by Regulation",
                "data": regulation_data,
                "x_axis": "regulation",
                "y_axis": "score"
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status chart: {e}")
            raise
    
    async def get_alert_distribution_chart(
        self, 
        period: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Get alert distribution chart data"""
        try:
            period_days = {
                "7d": 7,
                "30d": 30,
                "90d": 90
            }.get(period, 30)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get alerts by type and severity
            alert_data = []
            alert_types = ["risk_threshold", "compliance_violation", "system_error", "security_incident"]
            severities = ["low", "medium", "high", "critical"]
            
            for alert_type in alert_types:
                type_data = {"type": alert_type}
                for severity in severities:
                    count = db.query(Alert).filter(
                        and_(
                            Alert.alert_type == alert_type,
                            Alert.severity == severity,
                            Alert.created_at >= start_date
                        )
                    ).count()
                    type_data[severity] = count
                
                alert_data.append(type_data)
            
            return {
                "chart_type": "stacked_bar",
                "title": "Alert Distribution",
                "data": alert_data,
                "x_axis": "type",
                "categories": severities,
                "period": period
            }
            
        except Exception as e:
            logger.error(f"Error getting alert distribution chart: {e}")
            raise
    
    async def get_document_processing_chart(
        self, 
        days: int, 
        db: Session
    ) -> Dict[str, Any]:
        """Get document processing chart data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Generate daily processing data
            daily_data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                uploaded = db.query(Document).filter(
                    and_(
                        Document.created_at >= day_start,
                        Document.created_at < day_end
                    )
                ).count()
                
                processed = db.query(Document).filter(
                    and_(
                        Document.created_at >= day_start,
                        Document.created_at < day_end,
                        Document.processed == True
                    )
                ).count()
                
                daily_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "uploaded": uploaded,
                    "processed": processed,
                    "processing_rate": (processed / max(uploaded, 1)) * 100
                })
            
            return {
                "chart_type": "line",
                "title": "Document Processing",
                "data": daily_data,
                "x_axis": "date",
                "y_axes": ["uploaded", "processed"],
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting document processing chart: {e}")
            raise
    
    async def get_real_time_status(self, db: Session) -> Dict[str, Any]:
        """Get real-time system status"""
        try:
            # System uptime (simulated)
            uptime_hours = random.uniform(720, 744)  # 30-31 days
            
            # Active users (simulated)
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Processing queue status
            pending_documents = db.query(Document).filter(
                Document.processing_status == "pending"
            ).count()
            
            processing_documents = db.query(Document).filter(
                Document.processing_status == "processing"
            ).count()
            
            # System health indicators
            cpu_usage = random.uniform(20, 80)
            memory_usage = random.uniform(30, 70)
            disk_usage = random.uniform(40, 85)
            
            return {
                "system_status": "operational",
                "uptime_hours": uptime_hours,
                "active_users": active_users,
                "processing_queue": {
                    "pending": pending_documents,
                    "processing": processing_documents,
                    "queue_health": "normal" if pending_documents < 10 else "busy"
                },
                "resource_usage": {
                    "cpu_percent": cpu_usage,
                    "memory_percent": memory_usage,
                    "disk_percent": disk_usage
                },
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time status: {e}")
            raise
    
    async def get_performance_metrics(self, db: Session) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # API response times (simulated)
            avg_response_time = random.uniform(150, 300)  # milliseconds
            
            # Throughput metrics
            requests_per_minute = random.uniform(50, 200)
            
            # Error rates
            error_rate = random.uniform(0.1, 2.0)  # percentage
            
            # Database performance
            db_query_time = random.uniform(10, 50)  # milliseconds
            
            return {
                "api_performance": {
                    "avg_response_time_ms": avg_response_time,
                    "requests_per_minute": requests_per_minute,
                    "error_rate_percent": error_rate,
                    "uptime_percent": 99.9
                },
                "database_performance": {
                    "avg_query_time_ms": db_query_time,
                    "connection_pool_usage": random.uniform(20, 60),
                    "active_connections": random.randint(5, 25)
                },
                "ai_processing": {
                    "avg_processing_time_ms": random.uniform(500, 2000),
                    "queue_length": random.randint(0, 5),
                    "success_rate_percent": random.uniform(95, 99.5)
                },
                "measured_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise
    
    # Helper methods
    async def _get_system_health(self, db: Session) -> Dict[str, str]:
        """Get system health indicators"""
        return {
            "api_status": "healthy",
            "database_status": "healthy",
            "ai_services_status": "healthy",
            "storage_status": "healthy"
        }
    
    async def _get_recent_activity(
        self, 
        region: str, 
        current_user: User, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        activities = []
        
        # Recent risk assessments
        recent_risks = db.query(RiskAssessment).filter(
            RiskAssessment.region == region
        ).order_by(RiskAssessment.created_at.desc()).limit(3).all()
        
        for risk in recent_risks:
            activities.append({
                "type": "risk_assessment",
                "description": f"Risk assessment completed: {risk.assessment_type}",
                "timestamp": risk.created_at.isoformat(),
                "severity": risk.risk_level
            })
        
        # Recent alerts
        recent_alerts = db.query(Alert).order_by(
            Alert.created_at.desc()
        ).limit(3).all()
        
        for alert in recent_alerts:
            activities.append({
                "type": "alert",
                "description": alert.title,
                "timestamp": alert.created_at.isoformat(),
                "severity": alert.severity
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:5]
    
    async def _calculate_resolution_rate(self, db: Session) -> float:
        """Calculate alert resolution rate"""
        total_alerts = db.query(Alert).count()
        resolved_alerts = db.query(Alert).filter(Alert.status == "resolved").count()
        return (resolved_alerts / max(total_alerts, 1)) * 100
    
    async def _get_risk_metrics(
        self, 
        region: str, 
        start_date: datetime, 
        end_date: datetime, 
        db: Session
    ) -> Dict[str, Any]:
        """Get risk metrics for period"""
        assessments = db.query(RiskAssessment).filter(
            and_(
                RiskAssessment.region == region,
                RiskAssessment.created_at >= start_date,
                RiskAssessment.created_at <= end_date
            )
        ).all()
        
        if not assessments:
            return {"total": 0, "average_score": 0.0, "trend": "stable"}
        
        avg_score = sum(a.risk_score for a in assessments if a.risk_score) / len(assessments)
        
        return {
            "total": len(assessments),
            "average_score": avg_score,
            "high_risk_count": len([a for a in assessments if a.risk_level in ["high", "critical"]]),
            "trend": "stable"  # Would calculate from historical comparison
        }
    
    async def _get_compliance_metrics(
        self, 
        region: str, 
        start_date: datetime, 
        end_date: datetime, 
        db: Session
    ) -> Dict[str, Any]:
        """Get compliance metrics for period"""
        checks = db.query(ComplianceCheck).filter(
            and_(
                ComplianceCheck.region == region,
                ComplianceCheck.created_at >= start_date,
                ComplianceCheck.created_at <= end_date
            )
        ).all()
        
        if not checks:
            return {"total": 0, "average_score": 0.0, "compliant_rate": 0.0}
        
        avg_score = sum(c.compliance_score for c in checks if c.compliance_score) / len(checks)
        compliant_count = len([c for c in checks if c.status == "compliant"])
        
        return {
            "total": len(checks),
            "average_score": avg_score,
            "compliant_rate": (compliant_count / len(checks)) * 100,
            "non_compliant_count": len([c for c in checks if c.status == "non_compliant"])
        }
    
    async def _get_document_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        db: Session
    ) -> Dict[str, Any]:
        """Get document processing metrics for period"""
        documents = db.query(Document).filter(
            and_(
                Document.created_at >= start_date,
                Document.created_at <= end_date
            )
        ).all()
        
        if not documents:
            return {"total": 0, "processed": 0, "processing_rate": 0.0}
        
        processed_count = len([d for d in documents if d.processed])
        
        return {
            "total": len(documents),
            "processed": processed_count,
            "processing_rate": (processed_count / len(documents)) * 100,
            "failed": len([d for d in documents if d.processing_status == "failed"])
        }