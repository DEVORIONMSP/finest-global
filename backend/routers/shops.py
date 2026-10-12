"""
Routes liées aux boutiques.
Un vendeur = une boutique (relation 1-1).
"""

from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File, Form
)
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, Shop, UserRole
from schemas import ShopCreate, ShopUpdate, ShopOut
from auth import get_current_user, require_seller, get_current_user_optional
from utils import save_image, delete_image, SHOPS_DIR


router = APIRouter(prefix="/api/shops", tags=["Boutiques"])


# ============================================================
# 1. CRÉER SA BOUTIQUE (vendeur uniquement)
# ============================================================

@router.post("/", response_model=ShopOut, status_code=status.HTTP_201_CREATED)
def create_shop(
    payload: ShopCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Crée la boutique du vendeur connecté.
    Un vendeur ne peut avoir qu'une seule boutique.
    """
    # Déjà une boutique ?
    existing = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà une boutique. Modifiez-la au lieu d'en créer une nouvelle.",
        )
    
    shop = Shop(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


# ============================================================
# 2. MA BOUTIQUE (vendeur connecté)
# ============================================================

@router.get("/me", response_model=ShopOut)
def get_my_shop(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """Renvoie la boutique du vendeur connecté."""
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore de boutique. Créez-en une.",
        )
    return shop


# ============================================================
# 3. MODIFIER MA BOUTIQUE
# ============================================================

@router.patch("/me", response_model=ShopOut)
def update_my_shop(
    payload: ShopUpdate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """Modifie le nom et/ou la description de sa boutique."""
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore de boutique.",
        )
    
    if payload.name is not None:
        shop.name = payload.name
    if payload.description is not None:
        shop.description = payload.description
    
    db.commit()
    db.refresh(shop)
    return shop


# ============================================================
# 4. UPLOADER LA PHOTO DE MA BOUTIQUE
# ============================================================

@router.post("/me/photo", response_model=ShopOut)
async def upload_shop_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Upload la photo de la boutique.
    Si une photo existe déjà, elle est remplacée.
    """
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Créez d'abord votre boutique.",
        )
    
    # Supprimer l'ancienne photo si elle existe
    if shop.photo_url:
        delete_image(shop.photo_url)
    
    # Sauvegarder la nouvelle
    photo_url = await save_image(file, SHOPS_DIR, prefix=f"shop_{shop.id}")
    shop.photo_url = photo_url
    db.commit()
    db.refresh(shop)
    return shop


# ============================================================
# 5. LISTER TOUTES LES BOUTIQUES (public)
# ============================================================

@router.get("/", response_model=List[ShopOut])
def list_shops(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Liste toutes les boutiques.
    Triées par nombre de vues décroissant.
    """
    shops = (
        db.query(Shop)
        .order_by(Shop.views_count.desc(), Shop.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return shops


# ============================================================
# 6. VOIR UNE BOUTIQUE PUBLIQUE
# ============================================================

@router.get("/{shop_id}", response_model=ShopOut)
def get_shop(
    shop_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Renvoie les infos publiques d'une boutique.
    Incrémente le compteur de vues (sauf si c'est le propriétaire).
    """
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boutique introuvable.",
        )
    
    # Incrémenter les vues (sauf si c'est le propriétaire connecté)
    if not current_user or current_user.id != shop.owner_id:
        shop.views_count += 1
        db.commit()
        db.refresh(shop)
    
    return shop