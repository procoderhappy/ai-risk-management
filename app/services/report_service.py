"""
Report generation service
"""

import uuid
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.models import RiskAssessment, ComplianceCheck, Alert, AuditLog, User
import logging
import json

logger = logging.getLogger(__name__)


class ReportService:
    """Service for report generation"""
    
    def __init__(self):
        self.report_dir = "./data/reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    async def generate_risk_assessment_report(
        self, 
        region: str, 
        assessment_type: Optional[str], 
        period_days: int, 
        format: str, 
        current_user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Generate risk assessment report"""
        try:
            report_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Query risk assessments
            query = db.query(RiskAssessment).filter(
                and_(
                    RiskAssessment.region == region,
                    RiskAssessment.created_at >= start_date
                )
            )
            
            if assessment_type:
                query = query.filter(RiskAssessment.assessment_type == assessment_type)
            
            assessments = query.all()
            
            # Generate report data
            report_data = {
                "report_id": report_id,
                "report_type": "risk_assessment",
                "generated_by": current_user.username,
                "generated_at": datetime.now().isoformat(),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "filters": {
                    "region": region,
                    "assessment_type": assessment_type
                },
                "summary": {
                    "total_assessments": len(assessments),
                    "average_risk_score": sum(a.risk_score for a in assessments if a.risk_score) / max(len(assessments), 1),
                    "risk_distribution": self._calculate_risk_distribution(assessments),
                    "high_risk_items": len([a for a in assessments if a.risk_level in ["high", "critical"]])
                },
                "detailed_assessments": [
                    {
                        "assessment_id": a.assessment_id,
                        "assessment_type": a.assessment_type,
                        "risk_level": a.risk_level,
                        "risk_score": a.risk_score,
                        "confidence_score": a.confidence_score,
                        "created_at": a.created_at.isoformat(),
                        "factors": a.factors,
                        "recommendations": a.recommendations
                    }
                    for a in assessments
                ],
                "trends": self._calculate_risk_trends(assessments, period_days),
                "recommendations": self._generate_risk_report_recommendations(assessments)
            }
            
            # Save report
            filename = f"risk_assessment_report_{report_id}.{format}"
            file_path = os.path.join(self.report_dir, filename)
            
            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(report_data, f, indent=2)
            elif format == "pdf":
                await self._generate_pdf_report(report_data, file_path)
            elif format == "excel":
                await self._generate_excel_report(report_data, file_path)
            
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "format": format
            }
            
        except Exception as e:
            logger.error(f"Error generating risk assessment report: {e}")
            raise
    
    async def generate_compliance_report(
        self, 
        region: str, 
        regulation_type: Optional[str], 
        period_days: int, 
        format: str, 
        current_user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            report_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Query compliance checks
            query = db.query(ComplianceCheck).filter(
                and_(
                    ComplianceCheck.region == region,
                    ComplianceCheck.created_at >= start_date
                )
            )
            
            if regulation_type:
                query = query.filter(ComplianceCheck.regulation_type == regulation_type)
            
            checks = query.all()
            
            # Generate report data
            report_data = {
                "report_id": report_id,
                "report_type": "compliance",
                "generated_by": current_user.username,
                "generated_at": datetime.now().isoformat(),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "filters": {
                    "region": region,
                    "regulation_type": regulation_type
                },
                "summary": {
                    "total_checks": len(checks),
                    "average_compliance_score": sum(c.compliance_score for c in checks if c.compliance_score) / max(len(checks), 1),
                    "compliance_distribution": self._calculate_compliance_distribution(checks),
                    "non_compliant_items": len([c for c in checks if c.status == "non_compliant"])
                },
                "detailed_checks": [
                    {
                        "check_id": c.check_id,
                        "regulation_type": c.regulation_type,
                        "status": c.status,
                        "compliance_score": c.compliance_score,
                        "created_at": c.created_at.isoformat(),
                        "findings": c.findings,
                        "recommendations": c.recommendations
                    }
                    for c in checks
                ],
                "regulatory_breakdown": self._calculate_regulatory_breakdown(checks),
                "recommendations": self._generate_compliance_report_recommendations(checks)
            }
            
            # Save report
            filename = f"compliance_report_{report_id}.{format}"
            file_path = os.path.join(self.report_dir, filename)
            
            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(report_data, f, indent=2)
            elif format == "pdf":
                await self._generate_pdf_report(report_data, file_path)
            elif format == "excel":
                await self._generate_excel_report(report_data, file_path)
            
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "format": format
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    async def generate_executive_summary(
        self, 
        region: str, 
        period_days: int, 
        format: str, 
        current_user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Generate executive summary report"""
        try:
            report_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Gather data from multiple sources
            risk_assessments = db.query(RiskAssessment).filter(
                and_(
                    RiskAssessment.region == region,
                    RiskAssessment.created_at >= start_date
                )
            ).all()
            
            compliance_checks = db.query(ComplianceCheck).filter(
                and_(
                    ComplianceCheck.region == region,
                    ComplianceCheck.created_at >= start_date
                )
            ).all()
            
            alerts = db.query(Alert).filter(
                Alert.created_at >= start_date
            ).all()
            
            # Generate executive summary
            report_data = {
                "report_id": report_id,
                "report_type": "executive_summary",
                "generated_by": current_user.username,
                "generated_at": datetime.now().isoformat(),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "region": region,
                "executive_summary": {
                    "overall_risk_status": self._determine_overall_risk_status(risk_assessments),
                    "compliance_status": self._determine_compliance_status(compliance_checks),
                    "key_metrics": {
                        "total_risk_assessments": len(risk_assessments),
                        "average_risk_score": sum(a.risk_score for a in risk_assessments if a.risk_score) / max(len(risk_assessments), 1),
                        "compliance_score": sum(c.compliance_score for c in compliance_checks if c.compliance_score) / max(len(compliance_checks), 1),
                        "critical_alerts": len([a for a in alerts if a.severity == "critical"]),
                        "high_risk_items": len([a for a in risk_assessments if a.risk_level in ["high", "critical"]])
                    },
                    "key_findings": self._generate_key_findings(risk_assessments, compliance_checks, alerts),
                    "strategic_recommendations": self._generate_strategic_recommendations(risk_assessments, compliance_checks, alerts),
                    "action_items": self._generate_action_items(risk_assessments, compliance_checks, alerts)
                },
                "risk_overview": {
                    "distribution": self._calculate_risk_distribution(risk_assessments),
                    "top_risk_areas": self._identify_top_risk_areas(risk_assessments),
                    "trend": "stable"  # Would calculate from historical data
                },
                "compliance_overview": {
                    "distribution": self._calculate_compliance_distribution(compliance_checks),
                    "regulatory_status": self._calculate_regulatory_breakdown(compliance_checks),
                    "areas_of_concern": [c for c in compliance_checks if c.status == "non_compliant"]
                },
                "alert_overview": {
                    "total_alerts": len(alerts),
                    "by_severity": self._calculate_alert_distribution(alerts),
                    "resolution_rate": len([a for a in alerts if a.status == "resolved"]) / max(len(alerts), 1) * 100
                }
            }
            
            # Save report
            filename = f"executive_summary_{report_id}.{format}"
            file_path = os.path.join(self.report_dir, filename)
            
            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(report_data, f, indent=2)
            elif format == "pdf":
                await self._generate_pdf_report(report_data, file_path)
            elif format == "excel":
                await self._generate_excel_report(report_data, file_path)
            
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "format": format
            }
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            raise
    
    async def generate_audit_trail_report(
        self, 
        period_days: int, 
        user_id: Optional[int], 
        action_type: Optional[str], 
        format: str, 
        current_user: User, 
        db: Session
    ) -> Dict[str, Any]:
        """Generate audit trail report"""
        try:
            report_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Query audit logs
            query = db.query(AuditLog).filter(
                AuditLog.timestamp >= start_date
            )
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if action_type:
                query = query.filter(AuditLog.action.contains(action_type))
            
            audit_logs = query.order_by(AuditLog.timestamp.desc()).all()
            
            # Generate report data
            report_data = {
                "report_id": report_id,
                "report_type": "audit_trail",
                "generated_by": current_user.username,
                "generated_at": datetime.now().isoformat(),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "filters": {
                    "user_id": user_id,
                    "action_type": action_type
                },
                "summary": {
                    "total_events": len(audit_logs),
                    "unique_users": len(set(log.user_id for log in audit_logs if log.user_id)),
                    "successful_actions": len([log for log in audit_logs if log.success]),
                    "failed_actions": len([log for log in audit_logs if not log.success]),
                    "action_breakdown": self._calculate_action_breakdown(audit_logs)
                },
                "detailed_logs": [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "user_id": log.user_id,
                        "action": log.action,
                        "resource": log.resource,
                        "resource_id": log.resource_id,
                        "ip_address": log.ip_address,
                        "success": log.success,
                        "details": log.details
                    }
                    for log in audit_logs
                ],
                "security_analysis": self._analyze_security_events(audit_logs),
                "recommendations": self._generate_audit_recommendations(audit_logs)
            }
            
            # Save report
            filename = f"audit_trail_report_{report_id}.{format}"
            file_path = os.path.join(self.report_dir, filename)
            
            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(report_data, f, indent=2)
            elif format == "pdf":
                await self._generate_pdf_report(report_data, file_path)
            elif format == "excel":
                await self._generate_excel_report(report_data, file_path)
            
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "format": format
            }
            
        except Exception as e:
            logger.error(f"Error generating audit trail report: {e}")
            raise
    
    # Helper methods for report generation
    def _calculate_risk_distribution(self, assessments: List[RiskAssessment]) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
        for assessment in assessments:
            if assessment.risk_level in distribution:
                distribution[assessment.risk_level] += 1
        return distribution
    
    def _calculate_compliance_distribution(self, checks: List[ComplianceCheck]) -> Dict[str, int]:
        """Calculate compliance status distribution"""
        distribution = {"compliant": 0, "non_compliant": 0, "review_required": 0, "pending": 0}
        for check in checks:
            if check.status in distribution:
                distribution[check.status] += 1
        return distribution
    
    def _calculate_alert_distribution(self, alerts: List[Alert]) -> Dict[str, int]:
        """Calculate alert severity distribution"""
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in alerts:
            if alert.severity in distribution:
                distribution[alert.severity] += 1
        return distribution
    
    def _calculate_regulatory_breakdown(self, checks: List[ComplianceCheck]) -> Dict[str, Any]:
        """Calculate breakdown by regulation type"""
        breakdown = {}
        for check in checks:
            reg_type = check.regulation_type
            if reg_type not in breakdown:
                breakdown[reg_type] = {"total": 0, "compliant": 0, "non_compliant": 0}
            
            breakdown[reg_type]["total"] += 1
            if check.status == "compliant":
                breakdown[reg_type]["compliant"] += 1
            elif check.status == "non_compliant":
                breakdown[reg_type]["non_compliant"] += 1
        
        return breakdown
    
    def _calculate_action_breakdown(self, audit_logs: List[AuditLog]) -> Dict[str, int]:
        """Calculate breakdown of audit actions"""
        breakdown = {}
        for log in audit_logs:
            action = log.action
            breakdown[action] = breakdown.get(action, 0) + 1
        return breakdown
    
    def _determine_overall_risk_status(self, assessments: List[RiskAssessment]) -> str:
        """Determine overall risk status"""
        if not assessments:
            return "unknown"
        
        high_risk_count = len([a for a in assessments if a.risk_level in ["high", "critical"]])
        high_risk_percentage = (high_risk_count / len(assessments)) * 100
        
        if high_risk_percentage > 20:
            return "high"
        elif high_risk_percentage > 10:
            return "moderate"
        else:
            return "low"
    
    def _determine_compliance_status(self, checks: List[ComplianceCheck]) -> str:
        """Determine overall compliance status"""
        if not checks:
            return "unknown"
        
        compliant_count = len([c for c in checks if c.status == "compliant"])
        compliance_percentage = (compliant_count / len(checks)) * 100
        
        if compliance_percentage >= 95:
            return "excellent"
        elif compliance_percentage >= 85:
            return "good"
        elif compliance_percentage >= 75:
            return "acceptable"
        else:
            return "needs_improvement"
    
    async def _generate_pdf_report(self, report_data: Dict[str, Any], file_path: str):
        """Generate PDF report (simplified implementation)"""
        # In a real implementation, you would use a library like ReportLab
        # For demo purposes, we'll create a simple text file
        with open(file_path.replace('.pdf', '.txt'), 'w') as f:
            f.write(f"Report: {report_data['report_type']}\n")
            f.write(f"Generated: {report_data['generated_at']}\n")
            f.write(f"Generated by: {report_data['generated_by']}\n\n")
            f.write(json.dumps(report_data, indent=2))
    
    async def _generate_excel_report(self, report_data: Dict[str, Any], file_path: str):
        """Generate Excel report (simplified implementation)"""
        # In a real implementation, you would use a library like openpyxl
        # For demo purposes, we'll create a CSV file
        import csv
        csv_path = file_path.replace('.excel', '.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Report Type', report_data['report_type']])
            writer.writerow(['Generated', report_data['generated_at']])
            writer.writerow(['Generated By', report_data['generated_by']])
            writer.writerow([])
            
            # Add summary data
            if 'summary' in report_data:
                writer.writerow(['Summary'])
                for key, value in report_data['summary'].items():
                    writer.writerow([key, value])
    
    # Additional helper methods would be implemented here...