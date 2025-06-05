"""
User-related Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserRegion(str, Enum):
    US = "US"
    EU = "EU"
    UK = "UK"
    APAC = "APAC"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.ANALYST
    region: UserRegion = UserRegion.US
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    region: Optional[UserRegion] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    region: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True