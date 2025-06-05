"""
Alert management service
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.database.models import Alert, User
from app.schemas.alert import (
    AlertCreate, AlertUpdate, AlertResponse, AlertDashboard,
    AlertSearchRequest, AlertSearchResponse
)
import logging
import random

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert management"""
    
    def __init__(self):
        self.alert_priorities = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
    
    async def create_alert(
        self, 
        alert_data: AlertCreate, 
        current_user: User, 
        db: Session
    ) -> AlertResponse:
        """Create a new alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            db_alert = Alert(
                alert_id=alert_id,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                title=alert_data.title,
                description=alert_data.description,
                source=alert_data.source or "system",
                status="active"
            )
            
            db.add(db_alert)
            db.commit()
            db.refresh(db_alert)
            
            # Auto-assign critical alerts
            if alert_data.severity == "critical":
                await self._auto_assign_critical_alert(db_alert, db)
            
            logger.info(f"Alert created: {alert_id}")
            return AlertResponse.from_orm(db_alert)
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def _auto_assign_critical_alert(self, alert: Alert, db: Session):
        """Auto-assign critical alerts to available managers"""
        try:
            # Find available managers
            managers = db.query(User).filter(
                and_(
                    User.role.in_(["manager", "admin"]),
                    User.is_active == True
                )
            ).all()
            
            if managers:
                # Assign to manager with least active alerts
                manager_alert_counts = {}
                for manager in managers:
                    count = db.query(Alert).filter(
                        and_(
                            Alert.assigned_to == manager.id,
                            Alert.status.in_(["active", "acknowledged"])
                        )
                    ).count()
                    manager_alert_counts[manager.id] = count
                
                # Find manager with minimum alerts
                assigned_manager_id = min(manager_alert_counts, key=manager_alert_counts.get)
                alert.assigned_to = assigned_manager_id
                db.commit()
                
                logger.info(f"Critical alert auto-assigned to user {assigned_manager_id}")
                
        except Exception as e:
            logger.error(f"Error auto-assigning critical alert: {e}")
    
    async def get_dashboard_data(self, current_user: User, db: Session) -> AlertDashboard:
        """Get alert dashboard data"""
        try:
            # Base query
            query = db.query(Alert)
            
            # Filter by user role
            if current_user.role not in ["admin", "manager"]:
                query = query.filter(Alert.assigned_to == current_user.id)
            
            # Total alerts
            total_alerts = query.count()
            
            # Active alerts
            active_alerts = query.filter(Alert.status == "active").count()
            
            # Critical alerts
            critical_alerts = query.filter(
                and_(
                    Alert.severity == "critical",
                    Alert.status.in_(["active", "acknowledged"])
                )
            ).count()
            
            # Alerts by type
            alerts_by_type = {}
            for alert_type in ["risk_threshold", "compliance_violation", "system_error", "security_incident"]:
                count = query.filter(Alert.alert_type == alert_type).count()
                alerts_by_type[alert_type] = count
            
            # Alerts by severity
            alerts_by_severity = {}
            for severity in ["low", "medium", "high", "critical"]:
                count = query.filter(Alert.severity == severity).count()
                alerts_by_severity[severity] = count
            
            # Recent alerts
            recent_alerts = query.order_by(Alert.created_at.desc()).limit(10).all()
            
            return AlertDashboard(
                total_alerts=total_alerts,
                active_alerts=active_alerts,
                critical_alerts=critical_alerts,
                alerts_by_type=alerts_by_type,
                alerts_by_severity=alerts_by_severity,
                recent_alerts=[AlertResponse.from_orm(alert) for alert in recent_alerts]
            )
            
        except Exception as e:
            logger.error(f"Error getting alert dashboard data: {e}")
            raise
    
    async def search_alerts(
        self, 
        search_request: AlertSearchRequest, 
        current_user: User, 
        db: Session
    ) -> AlertSearchResponse:
        """Search alerts based on criteria"""
        try:
            query = db.query(Alert)
            
            # Apply user permissions
            if current_user.role not in ["admin", "manager"]:
                query = query.filter(Alert.assigned_to == current_user.id)
            
            # Apply filters
            if search_request.alert_type:
                query = query.filter(Alert.alert_type == search_request.alert_type)
            
            if search_request.severity:
                query = query.filter(Alert.severity == search_request.severity)
            
            if search_request.status:
                query = query.filter(Alert.status == search_request.status)
            
            if search_request.assigned_to:
                query = query.filter(Alert.assigned_to == search_request.assigned_to)
            
            if search_request.date_from:
                query = query.filter(Alert.created_at >= search_request.date_from)
            
            if search_request.date_to:
                query = query.filter(Alert.created_at <= search_request.date_to)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            alerts = query.order_by(
                Alert.severity.desc(),
                Alert.created_at.desc()
            ).limit(search_request.limit).all()
            
            return AlertSearchResponse(
                alerts=[AlertResponse.from_orm(alert) for alert in alerts],
                total=total,
                page=1,
                per_page=search_request.limit
            )
            
        except Exception as e:
            logger.error(f"Error searching alerts: {e}")
            raise
    
    async def escalate_alert(self, alert_id: str, current_user: User, db: Session) -> bool:
        """Escalate alert to higher severity"""
        try:
            alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
            if not alert:
                return False
            
            # Escalate severity
            severity_escalation = {
                "low": "medium",
                "medium": "high",
                "high": "critical"
            }
            
            if alert.severity in severity_escalation:
                alert.severity = severity_escalation[alert.severity]
                
                # Auto-assign if escalated to critical
                if alert.severity == "critical":
                    await self._auto_assign_critical_alert(alert, db)
                
                db.commit()
                logger.info(f"Alert escalated: {alert_id} to {alert.severity}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error escalating alert: {e}")
            return False
    
    async def generate_alert_metrics(self, days: int, db: Session) -> Dict[str, Any]:
        """Generate alert metrics for specified period"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = db.query(Alert).filter(
                Alert.created_at >= start_date
            )
            
            # Total alerts in period
            total_alerts = query.count()
            
            # Resolution rate
            resolved_alerts = query.filter(Alert.status == "resolved").count()
            resolution_rate = (resolved_alerts / max(total_alerts, 1)) * 100
            
            # Average resolution time
            resolved_query = query.filter(
                and_(
                    Alert.status == "resolved",
                    Alert.resolved_at.isnot(None)
                )
            )
            
            avg_resolution_time = 0.0
            if resolved_query.count() > 0:
                # Calculate average resolution time in hours
                resolution_times = []
                for alert in resolved_query.all():
                    if alert.resolved_at and alert.created_at:
                        diff = alert.resolved_at - alert.created_at
                        resolution_times.append(diff.total_seconds() / 3600)
                
                if resolution_times:
                    avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            # Alert trends by day
            daily_trends = []
            for i in range(days):
                day_start = start_date + timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                day_count = db.query(Alert).filter(
                    and_(
                        Alert.created_at >= day_start,
                        Alert.created_at < day_end
                    )
                ).count()
                
                daily_trends.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "count": day_count
                })
            
            return {
                "period_days": days,
                "total_alerts": total_alerts,
                "resolved_alerts": resolved_alerts,
                "resolution_rate": resolution_rate,
                "avg_resolution_time_hours": avg_resolution_time,
                "daily_trends": daily_trends,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating alert metrics: {e}")
            raise