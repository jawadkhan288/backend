"""
routers/notification_router.py — Notification CRUD endpoints with permission checks.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from database import get_db
from models import Notification, User
from schemas import NotificationCreate, NotificationOut, NotificationUpdate
from auth import get_current_user

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
    dependencies=[Depends(get_current_user)],  # all routes require auth
)


# ─────────────────────────────────────────────────────────────
#  GET /api/notifications  — List notifications
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve notifications belonging to the logged-in user, ordered by creation date descending."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(desc(Notification.created_at))
    )
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────
#  PATCH /api/notifications/{id}/read  — Mark notification as read
# ─────────────────────────────────────────────────────────────

@router.patch("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_as_read(
    notification_id: int,
    payload: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a specific notification as read/unread."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id={notification_id} not found.",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only update your own notifications.",
        )

    notification.is_read = payload.is_read
    await db.commit()
    await db.refresh(notification)
    return notification


# ─────────────────────────────────────────────────────────────
#  POST /api/notifications  — Create a notification
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a notification.
    - System or HR can trigger notifications for any user.
    """
    notification = Notification(
        user_id=payload.user_id,
        title=payload.title,
        message=payload.message,
        type=payload.type,
        is_read=False,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification
