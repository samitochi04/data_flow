from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for user registration (admin only)"""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address (must be unique)")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserUpdate(BaseModel):
    """Schema for updating user profile (admin only)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    """Schema for user response (public data)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserAdmin(UserOut):
    """Extended schema for admin view (all fields)"""
    pass
