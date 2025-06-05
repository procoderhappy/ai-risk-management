"""
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.app import create_app
from app.database.database import Base, get_db
from app.utils.database_init import create_sample_users

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test data
    db = TestingSessionLocal()
    create_sample_users(db)
    db.close()
    
    with TestClient(app) as test_client:
        yield test_client
    
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Risk Management & Compliance System"
    assert "features" in data
    assert "stats" in data

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["system"] == "AI Risk Management"

def test_login_success(client):
    """Test successful login"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client):
    """Test failed login"""
    login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 401

def test_protected_endpoint_with_token(client):
    """Test accessing protected endpoint with token"""
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200

def test_create_risk_assessment(client):
    """Test creating risk assessment"""
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Create risk assessment
    headers = {"Authorization": f"Bearer {token}"}
    assessment_data = {
        "assessment_type": "credit",
        "region": "US"
    }
    response = client.post("/api/v1/risk-assessments/", json=assessment_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["assessment_type"] == "credit"
    assert data["region"] == "US"

def test_get_dashboard_data(client):
    """Test getting dashboard data"""
    # Login first
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Get dashboard data
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/dashboard/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data