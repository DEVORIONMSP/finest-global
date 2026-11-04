"""
Routes liées aux services.
Un vendeur peut gérer uniquement les services de sa propre boutique.
"""

from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File, Query
)
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from database import get_db
from models import User, Shop, Service, UserRole
from schemas import ServiceCreate, ServiceUpdate, ServiceOut
from auth import (
    require_seller, get_current_user, get_current_user_optional
)
from utils import save_image, save_video, delete_image, delete_video, PRODUCTS_DIR


router = APIRouter(prefix="/api/services", tags=["Services"])


# ============================================================
# HELPER : vérifier que le vendeur possède bien le service
# ============================================================

def _get_owned_service(
    service_id: int,
    current_user: User,
    db: Session,
) -> Service:
    """
    Récupère un service et vérifie que le vendeur en est bien le propriétaire.
    Lève 404 si introuvable, 403 si pas le propriétaire.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service introuvable.",
        )
    
    shop = db.query(Shop).filter(Shop.id == service.shop_id).first()
    if not shop or shop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que les services de votre boutique.",
        )
    
    return service


# ============================================================
# 1. AJOUTER UN SERVICE
# ============================================================

@router.post("/", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Ajoute un service dans la boutique du vendeur connecté.
    """
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez d'abord créer votre boutique.",
        )
    
    service = Service(
        shop_id=shop.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        is_price_fixed=payload.is_price_fixed,
        category=payload.category,
        service_area=payload.service_area,
        availability_info=payload.availability_info,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


# ============================================================
# 2. UPLOADER LA PHOTO D'UN SERVICE
# ============================================================

@router.post("/{service_id}/photo", response_model=ServiceOut)
async def upload_service_photo(
    service_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Upload la photo d'un service.
    """
    service = _get_owned_service(service_id, current_user, db)
    
    if service.photo_url:
        delete_image(service.photo_url)
    
    photo_url = await save_image(file, PRODUCTS_DIR, prefix=f"service_{service.id}")
    service.photo_url = photo_url
    db.commit()
    db.refresh(service)
    return service


# ============================================================
# 3. UPLOADER LA VIDÉO D'UN SERVICE (Exemples de travaux)
# ============================================================

@router.post("/{service_id}/video", response_model=ServiceOut)
async def upload_service_video(
    service_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Upload une vidéo de démonstration pour un service.
    """
    service = _get_owned_service(service_id, current_user, db)
    
    if service.video_url:
        delete_video(service.video_url)
    
    video_url = await save_video(file, PRODUCTS_DIR, prefix=f"service_vid_{service_id}")
    service.video_url = video_url
    db.commit()
    db.refresh(service)
    return service


# ============================================================
# 4. MES SERVICES (vendeur connecté)
# ============================================================

@router.get("/me", response_model=List[ServiceOut])
def get_my_services(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Liste tous les services de la boutique du vendeur connecté.
    """
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        return []
    
    services = (
        db.query(Service)
        .filter(Service.shop_id == shop.id)
        .order_by(desc(Service.created_at))
        .all()
    )
    return services


# ============================================================
# 5. SERVICES D'UNE BOUTIQUE (public)
# ============================================================

@router.get("/shop/{shop_id}", response_model=List[ServiceOut])
def get_services_by_shop(
    shop_id: int,
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    service_area: Optional[str] = Query(None, description="Filtrer par zone"),
    min_price: Optional[float] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[float] = Query(None, ge=0, description="Prix maximum"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Liste les services d'une boutique, avec filtres.
    """
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boutique introuvable.",
        )
    
    query = db.query(Service).filter(Service.shop_id == shop_id)
    
    if category:
        query = query.filter(func.lower(Service.category) == category.lower())
    if service_area:
        query = query.filter(func.lower(Service.service_area) == service_area.lower())
    if min_price is not None:
        query = query.filter(Service.price >= min_price)
    if max_price is not None:
        query = query.filter(Service.price <= max_price)
    
    query = query.order_by(desc(Service.created_at))
    
    return query.offset(skip).limit(limit).all()


# ============================================================
# 6. VOIR UN SERVICE (public, incrémente les vues)
# ============================================================

@router.get("/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Renvoie les infos publiques d'un service.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service introuvable.",
        )
    
    shop = db.query(Shop).filter(Shop.id == service.shop_id).first()
    is_owner = current_user and shop and shop.owner_id == current_user.id
    
    if not is_owner:
        service.views_count += 1
        db.commit()
        db.refresh(service)
    
    return service


# ============================================================
# 7. MODIFIER UN SERVICE
# ============================================================

@router.patch("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Modifie un service. Seul le propriétaire peut le faire.
    """
    service = _get_owned_service(service_id, current_user, db)
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    return service


# ============================================================
# 8. SUPPRIMER UN SERVICE
# ============================================================

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Supprime un service et ses médias associés.
    """
    service = _get_owned_service(service_id, current_user, db)
    
    if service.photo_url:
        delete_image(service.photo_url)
    if service.video_url:
        delete_video(service.video_url)
    
    db.delete(service)
    db.commit()
    return None