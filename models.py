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
