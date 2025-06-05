"""
Database models for AI Risk Management System
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="analyst")  # admin, manager, analyst, viewer
    region = Column(String(10), default="US")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    """Document model for file management"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    content_hash = Column(String(64))
    processed = Column(Boolean, default=False)
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploader = relationship("User")
    risk_assessments = relationship("RiskAssessment", back_populates="document")
    document_analysis = relationship("DocumentAnalysis", back_populates="document")


class RiskAssessment(Base):
    """Risk assessment model"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(Integer, ForeignKey("documents.id"))
    assessment_type = Column(String(50), nullable=False)  # credit, market, operational, compliance
    risk_level = Column(String(20))  # low, moderate, high, critical
    risk_score = Column(Float)
    confidence_score = Column(Float)
    factors = Column(JSON)
    recommendations = Column(JSON)
    region = Column(String(10))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="risk_assessments")
    created_by_user = relationship("User", back_populates="risk_assessments")


class ComplianceCheck(Base):
    """Compliance check model"""
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    check_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    regulation_type = Column(String(50), nullable=False)  # GDPR, SOX, Basel III, etc.
    region = Column(String(10), nullable=False)
    status = Column(String(20), default="pending")  # pending, compliant, non_compliant, review_required
    compliance_score = Column(Float)
    findings = Column(JSON)
    recommendations = Column(JSON)
    next_review_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DocumentAnalysis(Base):
    """Document analysis results"""
    __tablename__ = "document_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    analysis_type = Column(String(50))  # sentiment, entity_extraction, classification
    results = Column(JSON)
    confidence = Column(Float)
    processing_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="document_analysis")


class AuditLog(Base):
    """Audit log for security and compliance tracking"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(String(50))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    success = Column(Boolean, default=True)
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Alert(Base):
    """Alert model for risk notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    alert_type = Column(String(50), nullable=False)  # risk_threshold, compliance_violation, system_error
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    source = Column(String(100))
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    assignee = relationship("User")


class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metrics_data = Column(JSON)