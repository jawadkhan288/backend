"""
routers/candidate_router.py — Full CRUD + status-update endpoints for candidates.
These are the core "Candidate" section endpoints assigned in the project.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc

from database import get_db
from models import Candidate, CandidateStatus, User
from schemas import CandidateCreate, CandidateUpdate, CandidateStatusUpdate, CandidateOut
from auth import get_current_user

router = APIRouter(
    prefix="/api/candidates",
    tags=["Candidates"],
    dependencies=[Depends(get_current_user)],  # all routes require auth
)


# ─────────────────────────────────────────────────────────────
#  GET /api/candidates  — List all candidates
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CandidateOut])
async def list_candidates(db: AsyncSession = Depends(get_db)):
    """Return all candidates ordered by applied date descending."""
    result = await db.execute(
        select(Candidate).order_by(Candidate.applied_date.desc(), Candidate.id.desc())
    )
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────
#  POST /api/candidates  — Create a candidate
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
async def create_candidate(payload: CandidateCreate, db: AsyncSession = Depends(get_db)):
    """Create a new candidate record."""
    # Validate status value
    try:
        status_enum = CandidateStatus(payload.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status '{payload.status}'. Must be one of: {[s.value for s in CandidateStatus]}",
        )

    candidate = Candidate(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        position=payload.position,
        ai_score=payload.ai_score,
        experience=payload.experience,
        skills=payload.skills,
        status=status_enum,
        avatar=payload.avatar,
        applied_date=payload.applied_date,
        match_reasons=payload.match_reasons or [],
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate


# ─────────────────────────────────────────────────────────────
#  GET /api/candidates/{id}  — Get single candidate
# ─────────────────────────────────────────────────────────────

@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch a single candidate by ID."""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id={candidate_id} not found.",
        )
    return candidate


# ─────────────────────────────────────────────────────────────
#  PUT /api/candidates/{id}  — Update candidate details
# ─────────────────────────────────────────────────────────────

@router.put("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update candidate fields (partial update — only non-None fields are applied)."""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id={candidate_id} not found.",
        )

    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)
    return candidate


# ─────────────────────────────────────────────────────────────
#  PATCH /api/candidates/{id}/status  — Move candidate in pipeline
# ─────────────────────────────────────────────────────────────

@router.patch("/{candidate_id}/status", response_model=CandidateOut)
async def update_candidate_status(
    candidate_id: int,
    payload: CandidateStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update only the pipeline status of a candidate (used by Kanban drag-and-drop)."""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id={candidate_id} not found.",
        )

    try:
        candidate.status = CandidateStatus(payload.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status '{payload.status}'. Must be one of: {[s.value for s in CandidateStatus]}",
        )

    await db.commit()
    await db.refresh(candidate)
    return candidate


# ─────────────────────────────────────────────────────────────
#  DELETE /api/candidates/{id}  — Delete a candidate
# ─────────────────────────────────────────────────────────────

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Permanently delete a candidate record."""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id={candidate_id} not found.",
        )

    await db.delete(candidate)
    await db.commit()
