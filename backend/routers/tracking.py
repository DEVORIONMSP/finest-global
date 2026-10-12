"""
Tracking des visites de pages.
Utilisé pour les statistiques (dashboard vendeur + admin).
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import PageView, User
from schemas import PageViewCreate
from auth import get_current_user_optional


router = APIRouter(prefix="/api/track", tags=["Tracking"])


@router.post("/pageview", status_code=204)
def track_pageview(
    payload: PageViewCreate,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Enregistre une visite de page.
    Appelé par le frontend à chaque changement de page.
    """
    view = PageView(
        user_id=current_user.id if current_user else None,
        shop_id=payload.shop_id,
        product_id=payload.product_id,
        path=payload.path,
        ip_address=request.client.host if request.client else None,
    )
    db.add(view)
    db.commit()
    return None