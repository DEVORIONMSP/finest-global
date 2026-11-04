"""
Routes liées aux produits.
Un vendeur peut gérer uniquement les produits de sa propre boutique.
"""

from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File, Query
)
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from database import get_db
from models import User, Shop, Product, UserRole
from schemas import ProductCreate, ProductUpdate, ProductOut
from auth import (
    require_seller, get_current_user, get_current_user_optional
)
from utils import save_image, save_video, delete_image, delete_video, PRODUCTS_DIR


router = APIRouter(prefix="/api/products", tags=["Produits"])


# ============================================================
# HELPER : vérifier que le vendeur possède bien le produit
# ============================================================

def _get_owned_product(
    product_id: int,
    current_user: User,
    db: Session,
) -> Product:
    """
    Récupère un produit et vérifie que le vendeur en est bien le propriétaire.
    Lève 404 si introuvable, 403 si pas le propriétaire.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit introuvable.",
        )
    
    shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
    if not shop or shop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que les produits de votre boutique.",
        )
    
    return product


# ============================================================
# 1. AJOUTER UN PRODUIT
# ============================================================

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Ajoute un produit dans la boutique du vendeur connecté.
    """
    # Le vendeur doit avoir une boutique
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous devez d'abord créer votre boutique.",
        )
    
    availability = payload.availability or "in_stock"
    in_stock = (availability == "in_stock")
    
    product = Product(
        shop_id=shop.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        is_price_fixed=payload.is_price_fixed,
        category=payload.category,
        color=payload.color,
        availability=availability,
        stock_quantity=payload.stock_quantity,
        in_stock=in_stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ============================================================
# 2. UPLOADER LA PHOTO D'UN PRODUIT
# ============================================================

@router.post("/{product_id}/photo", response_model=ProductOut)
async def upload_product_photo(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Upload la photo d'un produit.
    Remplace l'ancienne si elle existe.
    """
    product = _get_owned_product(product_id, current_user, db)
    
    if product.photo_url:
        delete_image(product.photo_url)
    
    photo_url = await save_image(file, PRODUCTS_DIR, prefix=f"product_{product.id}")
    product.photo_url = photo_url
    db.commit()
    db.refresh(product)
    return product


# ============================================================
# 3. UPLOADER LA VIDÉO D'UN PRODUIT (Lot ou démonstration)
# ============================================================

@router.post("/{product_id}/video", response_model=ProductOut)
async def upload_product_video(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Upload la vidéo d'un produit (ex: lot de chaussures).
    Remplace l'ancienne si elle existe.
    """
    product = _get_owned_product(product_id, current_user, db)
    
    if product.video_url:
        delete_video(product.video_url)
    
    video_url = await save_video(file, PRODUCTS_DIR, prefix=f"product_vid_{product.id}")
    product.video_url = video_url
    db.commit()
    db.refresh(product)
    return product


# ============================================================
# 4. MES PRODUITS (vendeur connecté)
# ============================================================

@router.get("/me", response_model=List[ProductOut])
def get_my_products(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Liste tous les produits de la boutique du vendeur connecté.
    """
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        return []
    
    products = (
        db.query(Product)
        .filter(Product.shop_id == shop.id)
        .order_by(desc(Product.created_at))
        .all()
    )
    return products


# ============================================================
# 5. PRODUITS D'UNE BOUTIQUE (public)
# ============================================================

@router.get("/shop/{shop_id}", response_model=List[ProductOut])
def get_products_by_shop(
    shop_id: int,
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    color: Optional[str] = Query(None, description="Filtrer par couleur"),
    availability: Optional[str] = Query(None, description="in_stock | out_of_stock | to_confirm"),
    min_price: Optional[float] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[float] = Query(None, ge=0, description="Prix maximum"),
    sort_by: Optional[str] = Query("recent", description="recent | sales | price_asc | price_desc"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Liste les produits d'une boutique, avec filtres.
    """
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boutique introuvable.",
        )
    
    query = db.query(Product).filter(Product.shop_id == shop_id)
    
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())
    if color:
        query = query.filter(func.lower(Product.color) == color.lower())
    if availability:
        query = query.filter(Product.availability == availability)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if sort_by == "sales":
        query = query.order_by(desc(Product.sales_count))
    elif sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(desc(Product.created_at))
    
    return query.offset(skip).limit(limit).all()


# ============================================================
# 6. VOIR UN PRODUIT (public, incrémente les vues)
# ============================================================

@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Renvoie les infos publiques d'un produit.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit introuvable.",
        )
    
    shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
    is_owner = current_user and shop and shop.owner_id == current_user.id
    
    if not is_owner:
        product.views_count += 1
        db.commit()
        db.refresh(product)
    
    return product


# ============================================================
# 7. MODIFIER UN PRODUIT
# ============================================================

@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Modifie un produit. Seul le propriétaire peut le faire.
    """
    product = _get_owned_product(product_id, current_user, db)
    
    update_data = payload.model_dump(exclude_unset=True)
    
    if "availability" in update_data:
        update_data["in_stock"] = (update_data["availability"] == "in_stock")
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


# ============================================================
# 8. SUPPRIMER UN PRODUIT
# ============================================================

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Supprime un produit et ses médias associés.
    """
    product = _get_owned_product(product_id, current_user, db)
    
    if product.photo_url:
        delete_image(product.photo_url)
    if product.video_url:
        delete_video(product.video_url)
    
    db.delete(product)
    db.commit()
    return None