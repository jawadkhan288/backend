"""
models.py — SQLAlchemy ORM models for users and candidates tables.
"""
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Date,
    Enum as SAEnum, JSON, ForeignKey, func, text
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base


class CandidateStatus(str, enum.Enum):
    Applied   = "Applied"
    Screened  = "Screened"
    Interview = "Interview"
    Offer     = "Offer"
    Hired     = "Hired"
    Approved  = "Approved"
    Rejected  = "Rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="candidate", nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    bio = Column(String(1000), nullable=True)
    avatar = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    position = Column(String(255), nullable=False)
    ai_score = Column(Integer, default=0, nullable=False)
    experience = Column(String(100), nullable=True)
    skills = Column(JSON, default=list, nullable=False)
    education = Column(JSON, default=list, nullable=True)
    certifications = Column(JSON, default=list, nullable=True)
    status = Column(
        SAEnum(CandidateStatus, name="candidate_status", create_constraint=True),
        default=CandidateStatus.Applied,
        nullable=False,
    )
    avatar = Column(String(500), nullable=True)
    applied_date = Column(Date, default=date.today, nullable=False)
    match_reasons = Column(JSON, default=list, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_name = Column(String(255), nullable=False)
    candidate_email = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    duration = Column(String(50), nullable=False)
    type = Column(String(100), nullable=False)
    interviewer = Column(String(255), nullable=False)
    meeting_link = Column(String(500), nullable=True)
    avatar = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)
    type = Column(String(50), default="info", nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

