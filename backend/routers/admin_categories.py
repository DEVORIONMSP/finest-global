"""
CRUD des catégories — réservé aux admins.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models import Category, Product, User
from schemas import CategoryCreate, CategoryUpdate, CategoryOut, CategoryWithCount
from auth import require_admin


router = APIRouter(prefix="/api/admin/categories", tags=["Admin — Catégories"])


# ============================================================
# 1. CRÉER UNE CATÉGORIE
# ============================================================

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Crée une nouvelle catégorie."""
    # Vérifier l'unicité
    existing = db.query(Category).filter(
        func.lower(Category.name) == payload.name.lower()
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Une catégorie '{payload.name}' existe déjà.",
        )
    
    cat = Category(
        name=payload.name.strip(),
        description=payload.description,
        emoji=payload.emoji or "🏷️",
        display_order=payload.display_order or 0,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ============================================================
# 2. LISTE (admin — inclut inactives)
# ============================================================

@router.get("/", response_model=List[CategoryWithCount])
def list_all_categories(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Liste toutes les catégories (actives et inactives)."""
    categories = (
        db.query(Category)
        .order_by(Category.display_order, Category.name)
        .all()
    )
    
    counts = dict(
        db.query(Product.category, func.count(Product.id))
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .all()
    )
    
    result = []
    for cat in categories:
        result.append({
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "emoji": cat.emoji,
            "display_order": cat.display_order,
            "is_active": cat.is_active,
            "created_at": cat.created_at,
            "product_count": counts.get(cat.name, 0),
        })
    return result


# ============================================================
# 3. MODIFIER
# ============================================================

@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Modifie une catégorie."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie introuvable.",
        )
    
    # Vérifier unicité si on change le nom
    if payload.name and payload.name.lower() != cat.name.lower():
        existing = db.query(Category).filter(
            func.lower(Category.name) == payload.name.lower(),
            Category.id != category_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Une catégorie '{payload.name}' existe déjà.",
            )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cat, field, value)
    
    db.commit()
    db.refresh(cat)
    return cat


# ============================================================
# 4. SUPPRIMER
# ============================================================

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Supprime une catégorie.
    Refusé si des produits l'utilisent encore.
    """
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie introuvable.",
        )
    
    # Vérifier qu'aucun produit n'utilise cette catégorie
    product_count = db.query(Product).filter(
        Product.category == cat.name
    ).count()
    
    if product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de supprimer : {product_count} produit(s) utilisent cette catégorie. "
                   f"Désactivez-la plutôt.",
        )
    
    db.delete(cat)
    db.commit()
    return None


# ============================================================
# 5. SEED — créer les catégories de base
# ============================================================

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_categories(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Crée les catégories de base pour démarrer.
    Idempotent : ne recrée pas celles qui existent déjà.
    """
    default_categories = [
        {"name": "mode", "emoji": "👗", "description": "Vêtements, robes, chemises", "display_order": 1},
        {"name": "chaussures", "emoji": "👟", "description": "Chaussures homme, femme, enfant", "display_order": 2},
        {"name": "sacs", "emoji": "👜", "description": "Sacs à main, sacs à dos, pochettes", "display_order": 3},
        {"name": "bijoux", "emoji": "💍", "description": "Colliers, bracelets, bagues", "display_order": 4},
        {"name": "cosmetiques", "emoji": "🧴", "description": "Soins, parfums, maquillage", "display_order": 5},
        {"name": "electronique", "emoji": "📱", "description": "Téléphones, accessoires, gadgets", "display_order": 6},
        {"name": "maison", "emoji": "🏠", "description": "Décoration, literie, ustensiles", "display_order": 7},
        {"name": "alimentation", "emoji": "🍲", "description": "Produits alimentaires, épices", "display_order": 8},
        {"name": "beaute", "emoji": "💄", "description": "Produits de beauté et soins", "display_order": 9},
        {"name": "sport", "emoji": "⚽", "description": "Équipements sportifs, vêtements", "display_order": 10},
        {"name": "livres", "emoji": "📚", "description": "Livres, fournitures scolaires", "display_order": 11},
        {"name": "jouets", "emoji": "🧸", "description": "Jouets enfants, jeux", "display_order": 12},
    ]
    
    created_count = 0
    for cat_data in default_categories:
        existing = db.query(Category).filter(
            func.lower(Category.name) == cat_data["name"].lower()
        ).first()
        if not existing:
            cat = Category(**cat_data)
            db.add(cat)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"{created_count} catégorie(s) créée(s) sur {len(default_categories)}.",
        "total": len(default_categories),
        "created": created_count,
    }