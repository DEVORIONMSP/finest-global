"""
Routes pour gérer l'historique des notifications (la cloche 🔔).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from database import get_db
from models import Notification, User
from schemas import NotificationOut, NotificationMarkRead
from auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


# ============================================================
# 1. MES NOTIFICATIONS
# ============================================================

@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Récupère l'historique des notifications de l'utilisateur connecté.
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
        
    notifications = (
        query
        .order_by(desc(Notification.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return notifications


# ============================================================
# 2. NOMBRE DE NON-LUES (Pour le badge rouge)
# ============================================================

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Renvoie le nombre de notifications non lues.
    """
    count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).scalar()
    
    return {"unread_count": count}


# ============================================================
# 3. MARQUER COMME LU
# ============================================================

@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_as_read(
    notification_id: int,
    payload: NotificationMarkRead,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marque une notification comme lue ou non-lue.
    """
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification introuvable.",
        )
        
    notif.is_read = payload.is_read
    db.commit()
    db.refresh(notif)
    return notif


# ============================================================
# 4. TOUT MARQUER COMME LU
# ============================================================

@router.post("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marque toutes les notifications comme lues.
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return {"message": "Toutes les notifications ont été marquées comme lues."}