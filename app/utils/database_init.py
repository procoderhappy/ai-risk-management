"""
Database initialization and sample data creation
"""

from sqlalchemy.orm import Session
from app.database.database import engine, SessionLocal, Base
from app.database.models import User, Document, RiskAssessment, ComplianceCheck, Alert
from app.api.auth.security import get_password_hash
from datetime import datetime, timedelta
import logging
import random
import uuid

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def create_sample_users(db: Session):
    """Create sample users"""
    try:
        # Check if users already exist
        if db.query(User).first():
            logger.info("Users already exist, skipping sample user creation")
            return
        
        sample_users = [
            {
                "username": "admin",
                "email": "admin@riskmanagement.com",
                "password": "admin123",
                "full_name": "System Administrator",
                "role": "admin",
                "region": "US"
            },
            {
                "username": "manager1",
                "email": "manager1@riskmanagement.com",
                "password": "manager123",
                "full_name": "Risk Manager",
                "role": "manager",
                "region": "US"
            },
            {
                "username": "analyst1",
                "email": "analyst1@riskmanagement.com",
                "password": "analyst123",
                "full_name": "Risk Analyst",
                "role": "analyst",
                "region": "US"
            },
            {
                "username": "viewer1",
                "email": "viewer1@riskmanagement.com",
                "password": "viewer123",
                "full_name": "Risk Viewer",
                "role": "viewer",
                "region": "EU"
            }
        ]
        
        for user_data in sample_users:
            hashed_password = get_password_hash(user_data["password"])
            
            db_user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                role=user_data["role"],
                region=user_data["region"],
                is_active=True
            )
            
            db.add(db_user)
        
        db.commit()
        logger.info("Sample users created successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample users: {e}")
        db.rollback()
        raise


def create_sample_documents(db: Session):
    """Create sample documents"""
    try:
        # Check if documents already exist
        if db.query(Document).first():
            logger.info("Documents already exist, skipping sample document creation")
            return
        
        sample_documents = [
            {
                "filename": "financial_report_q1_2024.pdf",
                "original_filename": "Q1 2024 Financial Report.pdf",
                "file_path": "./data/uploads/financial_report_q1_2024.pdf",
                "file_size": 2456789,
                "file_type": ".pdf",
                "content_hash": "abc123def456",
                "processed": True,
                "processing_status": "completed",
                "uploaded_by": 1
            },
            {
                "filename": "compliance_audit_2024.docx",
                "original_filename": "Compliance Audit 2024.docx",
                "file_path": "./data/uploads/compliance_audit_2024.docx",
                "file_size": 1876543,
                "file_type": ".docx",
                "content_hash": "def456ghi789",
                "processed": True,
                "processing_status": "completed",
                "uploaded_by": 2
            },
            {
                "filename": "risk_assessment_data.xlsx",
                "original_filename": "Risk Assessment Data.xlsx",
                "file_path": "./data/uploads/risk_assessment_data.xlsx",
                "file_size": 5432109,
                "file_type": ".xlsx",
                "content_hash": "ghi789jkl012",
                "processed": False,
                "processing_status": "processing",
                "uploaded_by": 3
            }
        ]
        
        for doc_data in sample_documents:
            db_document = Document(**doc_data)
            db.add(db_document)
        
        db.commit()
        logger.info("Sample documents created successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample documents: {e}")
        db.rollback()
        raise


def create_sample_risk_assessments(db: Session):
    """Create sample risk assessments"""
    try:
        # Check if risk assessments already exist
        if db.query(RiskAssessment).first():
            logger.info("Risk assessments already exist, skipping sample creation")
            return
        
        assessment_types = ["credit", "market", "operational", "compliance"]
        risk_levels = ["low", "moderate", "high", "critical"]
        regions = ["US", "EU", "UK", "APAC"]
        
        for i in range(20):
            assessment_data = {
                "assessment_id": str(uuid.uuid4()),
                "document_id": random.choice([1, 2, None]),
                "assessment_type": random.choice(assessment_types),
                "risk_level": random.choice(risk_levels),
                "risk_score": random.uniform(0.1, 0.9),
                "confidence_score": random.uniform(0.7, 0.95),
                "factors": {
                    "market_volatility": random.uniform(0.2, 0.8),
                    "regulatory_compliance": random.uniform(0.1, 0.9),
                    "operational_efficiency": random.uniform(0.3, 0.7)
                },
                "recommendations": [
                    "Monitor risk indicators closely",
                    "Review compliance procedures",
                    "Implement additional controls"
                ],
                "region": random.choice(regions),
                "created_by": random.choice([1, 2, 3]),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 30))
            }
            
            db_assessment = RiskAssessment(**assessment_data)
            db.add(db_assessment)
        
        db.commit()
        logger.info("Sample risk assessments created successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample risk assessments: {e}")
        db.rollback()
        raise


def create_sample_compliance_checks(db: Session):
    """Create sample compliance checks"""
    try:
        # Check if compliance checks already exist
        if db.query(ComplianceCheck).first():
            logger.info("Compliance checks already exist, skipping sample creation")
            return
        
        regulation_types = ["GDPR", "SOX", "Basel III", "MiFID II", "HIPAA"]
        statuses = ["compliant", "non_compliant", "review_required", "pending"]
        regions = ["US", "EU", "UK", "APAC"]
        
        for i in range(15):
            check_data = {
                "check_id": str(uuid.uuid4()),
                "regulation_type": random.choice(regulation_types),
                "region": random.choice(regions),
                "status": random.choice(statuses),
                "compliance_score": random.uniform(75, 98),
                "findings": {
                    "overall_score": random.uniform(80, 95),
                    "areas_assessed": [
                        {"area": "Data Protection", "score": random.uniform(85, 95)},
                        {"area": "Privacy Rights", "score": random.uniform(80, 90)}
                    ]
                },
                "recommendations": [
                    "Update privacy policies",
                    "Conduct regular audits",
                    "Enhance monitoring procedures"
                ],
                "next_review_date": datetime.now() + timedelta(days=random.randint(30, 120)),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 60))
            }
            
            db_check = ComplianceCheck(**check_data)
            db.add(db_check)
        
        db.commit()
        logger.info("Sample compliance checks created successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample compliance checks: {e}")
        db.rollback()
        raise


def create_sample_alerts(db: Session):
    """Create sample alerts"""
    try:
        # Check if alerts already exist
        if db.query(Alert).first():
            logger.info("Alerts already exist, skipping sample creation")
            return
        
        alert_types = ["risk_threshold", "compliance_violation", "system_error", "security_incident"]
        severities = ["low", "medium", "high", "critical"]
        statuses = ["active", "acknowledged", "resolved"]
        
        sample_alerts = [
            {
                "alert_type": "risk_threshold",
                "severity": "critical",
                "title": "Credit risk threshold exceeded",
                "description": "Credit risk assessment shows critical level requiring immediate attention",
                "source": "risk_engine",
                "status": "active"
            },
            {
                "alert_type": "compliance_violation",
                "severity": "high",
                "title": "GDPR compliance issue detected",
                "description": "Data processing activity may violate GDPR requirements",
                "source": "compliance_monitor",
                "status": "acknowledged"
            },
            {
                "alert_type": "system_error",
                "severity": "medium",
                "title": "Document processing failure",
                "description": "Failed to process uploaded document due to format issues",
                "source": "document_processor",
                "status": "resolved"
            }
        ]
        
        for alert_data in sample_alerts:
            alert_data.update({
                "alert_id": str(uuid.uuid4()),
                "assigned_to": random.choice([1, 2, None]),
                "created_at": datetime.now() - timedelta(hours=random.randint(1, 48))
            })
            
            db_alert = Alert(**alert_data)
            db.add(db_alert)
        
        # Add more random alerts
        for i in range(10):
            alert_data = {
                "alert_id": str(uuid.uuid4()),
                "alert_type": random.choice(alert_types),
                "severity": random.choice(severities),
                "title": f"Sample alert {i+1}",
                "description": f"This is a sample alert for testing purposes",
                "source": "system",
                "status": random.choice(statuses),
                "assigned_to": random.choice([1, 2, 3, None]),
                "created_at": datetime.now() - timedelta(hours=random.randint(1, 168))
            }
            
            db_alert = Alert(**alert_data)
            db.add(db_alert)
        
        db.commit()
        logger.info("Sample alerts created successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample alerts: {e}")
        db.rollback()
        raise


def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        logger.info("Starting database initialization...")
        
        # Create tables
        create_tables()
        
        # Create sample data
        db = SessionLocal()
        try:
            create_sample_users(db)
            create_sample_documents(db)
            create_sample_risk_assessments(db)
            create_sample_compliance_checks(db)
            create_sample_alerts(db)
            
            logger.info("Database initialization completed successfully")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise


if __name__ == "__main__":
    initialize_database()