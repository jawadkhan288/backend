"""
routers/interview_router.py — Full CRUD endpoints for interview schedules with RBAC.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Interview, User
from schemas import InterviewCreate, InterviewOut
from auth import get_current_user

router = APIRouter(
    prefix="/api/interviews",
    tags=["Interviews"],
    dependencies=[Depends(get_current_user)],  # all routes require auth
)


# ─────────────────────────────────────────────────────────────
#  GET /api/interviews  — List interviews
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[InterviewOut])
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List interviews.
    - HR: returns all interviews.
    - Candidate: returns only interviews matching candidate's registration email.
    """
    if current_user.role in ("hr", "admin"):
        result = await db.execute(select(Interview).order_by(Interview.date.asc()))
        return result.scalars().all()
    else:
        result = await db.execute(
            select(Interview)
            .where(Interview.candidate_email == current_user.email)
            .order_by(Interview.date.asc())
        )
        return result.scalars().all()


# ─────────────────────────────────────────────────────────────
#  POST /api/interviews  — Create an interview
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview schedule (HR only)."""
    if current_user.role not in ("hr", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only HR users can schedule interviews.",
        )

    interview = Interview(
        candidate_name=payload.candidate_name,
        candidate_email=payload.candidate_email,
        position=payload.position,
        date=payload.date,
        time=payload.time,
        duration=payload.duration,
        type=payload.type,
        interviewer=payload.interviewer,
        meeting_link=payload.meeting_link,
        avatar=payload.avatar,
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


# ─────────────────────────────────────────────────────────────
#  GET /api/interviews/{id}  — Get interview details
# ─────────────────────────────────────────────────────────────

@router.get("/{interview_id}", response_model=InterviewOut)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch an interview by ID with permission checks."""
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with id={interview_id} not found.",
        )

    if current_user.role not in ("hr", "admin") and interview.candidate_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own interviews.",
        )
    return interview


# ─────────────────────────────────────────────────────────────
#  DELETE /api/interviews/{id}  — Cancel/delete an interview
# ─────────────────────────────────────────────────────────────

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently cancel/delete an interview schedule (HR only)."""
    if current_user.role not in ("hr", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only HR users can cancel interviews.",
        )

    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with id={interview_id} not found.",
        )

    await db.delete(interview)
    await db.commit()
