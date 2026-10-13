"""
Routes liées aux boutiques.
Un vendeur = une boutique (relation 1-1).
Géolocalisation + code unique FG-0001.
"""

from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
)
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from database import get_db
from models import User, Shop, UserRole
from schemas import ShopCreate, ShopUpdate, ShopOut
from auth import get_current_user, require_seller, get_current_user_optional
from utils import save_image, delete_image, SHOPS_DIR


router = APIRouter(prefix="/api/shops", tags=["Boutiques"])


# ============================================================
# HELPER : Générer un code unique FG-0001
# ============================================================

def generate_shop_code(db: Session) -> str:
    """Génère un code unique FG-0001, FG-0002, FG-0003..."""
    # Trouver le dernier shop par id
    last_shop = db.query(Shop).order_by(Shop.id.desc()).first()
    
    if not last_shop or not last_shop.id:
        next_number = 1
    else:
        next_number = last_shop.id + 1
    
    # Vérifier qu'il n'y a pas de collision (au cas où)
    while True:
        code = f"FG-{next_number:04d}"
        existing = db.query(Shop).filter(Shop.code == code).first()
        if not existing:
            return code
        next_number += 1


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
    Code unique généré automatiquement.
    """
    # Déjà une boutique ?
    existing = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà une boutique. Modifiez-la au lieu d'en créer une nouvelle.",
        )
    
    # Créer la boutique
    shop = Shop(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        # 🆕 Géolocalisation
        latitude=payload.latitude,
        longitude=payload.longitude,
        locality=payload.locality,
        market=payload.market,
        # 🆕 Code unique auto-généré
        code=generate_shop_code(db),
        # 🆕 Statut actif
        is_active=True,
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
    """
    Modifie les infos de sa boutique.
    Permet aussi de changer la localisation (lat/lng, locality, market).
    """
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore de boutique.",
        )
    
    # Mise à jour dynamique : ne modifier que les champs fournis
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shop, field, value)
    
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
    """Upload la photo de la boutique."""
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Créez d'abord votre boutique.",
        )
    
    if shop.photo_url:
        delete_image(shop.photo_url)
    
    photo_url = await save_image(file, SHOPS_DIR, prefix=f"shop_{shop.id}")
    shop.photo_url = photo_url
    db.commit()
    db.refresh(shop)
    return shop


# ============================================================
# 5. LISTER TOUTES LES BOUTIQUES (public, avec filtres)
# ============================================================

@router.get("/", response_model=List[ShopOut])
def list_shops(
    locality: Optional[str] = Query(None, description="Filtrer par localité"),
    market: Optional[str] = Query(None, description="Filtrer par marché"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Liste toutes les boutiques actives.
    Filtrable par localité et/ou marché.
    Triées par nombre de vues décroissant.
    """
    query = db.query(Shop).filter(Shop.is_active == True)
    
    # 🆕 Filtres géographiques
    if locality:
        query = query.filter(func.lower(Shop.locality) == locality.lower())
    if market:
        query = query.filter(func.lower(Shop.market) == market.lower())
    
    shops = (
        query
        .order_by(Shop.views_count.desc(), Shop.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return shops


# ============================================================
# 6. LISTER LES LOCALITÉS DISPONIBLES (public)
# ============================================================

@router.get("/localities")
def list_localities(db: Session = Depends(get_db)):
    """
    Renvoie la liste des localités qui ont au moins une boutique.
    Utilisé pour les filtres côté client.
    """
    localities = (
        db.query(
            Shop.locality,
            func.count(Shop.id).label("shop_count")
        )
        .filter(
            Shop.is_active == True,
            Shop.locality.isnot(None),
            Shop.locality != ""
        )
        .group_by(Shop.locality)
        .order_by(func.count(Shop.id).desc())
        .all()
    )
    
    return {
        "localities": [
            {"name": loc, "shop_count": count}
            for loc, count in localities
        ]
    }


# ============================================================
# 7. LISTER LES MARCHÉS DISPONIBLES (public)
# ============================================================

@router.get("/markets")
def list_markets(db: Session = Depends(get_db)):
    """
    Renvoie la liste des marchés qui ont au moins une boutique.
    """
    markets = (
        db.query(
            Shop.market,
            func.count(Shop.id).label("shop_count")
        )
        .filter(
            Shop.is_active == True,
            Shop.market.isnot(None),
            Shop.market != ""
        )
        .group_by(Shop.market)
        .order_by(func.count(Shop.id).desc())
        .all()
    )
    
    return {
        "markets": [
            {"name": market, "shop_count": count}
            for market, count in markets
        ]
    }


# ============================================================
# 8. RECHERCHER UNE BOUTIQUE PAR CODE (public)
# ============================================================

@router.get("/by-code/{code}", response_model=ShopOut)
def get_shop_by_code(
    code: str,
    db: Session = Depends(get_db),
):
    """
    Trouve une boutique par son code FG-0001.
    """
    shop = db.query(Shop).filter(
        func.upper(Shop.code) == code.upper(),
        Shop.is_active == True
    ).first()
    
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune entreprise trouvée avec ce code.",
        )
    
    return shop


# ============================================================
# 9. VOIR UNE BOUTIQUE PUBLIQUE
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