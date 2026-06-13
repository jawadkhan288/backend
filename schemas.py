"""
schemas.py — Pydantic v2 schemas for request/response validation.
"""
from __future__ import annotations
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ─────────────────────────────────────────────────────────────
#  Auth Schemas
# ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Minimum 6 characters")
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    phone: Optional[str] = None
    location: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─────────────────────────────────────────────────────────────
#  Candidate Schemas
# ─────────────────────────────────────────────────────────────

class CandidateCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    position: str = Field(min_length=1)
    ai_score: int = Field(default=0, ge=0, le=100)
    experience: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: Optional[List[dict]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    status: str = Field(default="Applied")
    avatar: Optional[str] = None
    applied_date: Optional[date] = None
    match_reasons: Optional[List[str]] = Field(default_factory=list)


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    ai_score: Optional[int] = Field(default=None, ge=0, le=100)
    experience: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[dict]] = None
    certifications: Optional[List[str]] = None
    avatar: Optional[str] = None
    match_reasons: Optional[List[str]] = None


class CandidateStatusUpdate(BaseModel):
    status: str = Field(description="One of: Applied, Screened, Interview, Offer, Hired, Approved, Rejected")


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    position: str
    ai_score: int
    experience: Optional[str] = None
    skills: List[str] = []
    education: Optional[List[dict]] = []
    certifications: Optional[List[str]] = []
    status: str
    avatar: Optional[str] = None
    applied_date: date
    match_reasons: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime


# ─────────────────────────────────────────────────────────────
#  Interview Schemas
# ─────────────────────────────────────────────────────────────

class InterviewCreate(BaseModel):
    candidate_name: str = Field(min_length=1)
    candidate_email: EmailStr
    position: str = Field(min_length=1)
    date: str = Field(min_length=1)
    time: str = Field(min_length=1)
    duration: str = Field(min_length=1)
    type: str = Field(min_length=1)
    interviewer: str = Field(min_length=1)
    meeting_link: Optional[str] = None
    avatar: Optional[str] = None


class InterviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_name: str
    candidate_email: str
    position: str
    date: str
    time: str
    duration: str
    type: str
    interviewer: str
    meeting_link: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime


# ─────────────────────────────────────────────────────────────
#  Notification Schemas
# ─────────────────────────────────────────────────────────────

class NotificationCreate(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    type: str = "info"


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationUpdate(BaseModel):
    is_read: bool

