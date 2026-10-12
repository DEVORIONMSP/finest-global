"""
Routes publiques pour les catégories.
Utilisées par les vendeurs (formulaire produit) et les clients (filtres).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List

from database import get_db
from models import Category, Product
from schemas import CategoryOut, CategoryWithCount


router = APIRouter(prefix="/api/categories", tags=["Catégories"])


# ============================================================
# 1. LISTE DES CATÉGORIES ACTIVES (public)
# ============================================================

@router.get("/", response_model=List[CategoryWithCount])
def list_categories(db: Session = Depends(get_db)):
    """
    Liste toutes les catégories actives avec leur nombre de produits.
    Triées par display_order puis par nom.
    """
    # Récupérer les catégories actives
    categories = (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.display_order, Category.name)
        .all()
    )
    
    # Compter les produits par catégorie
    counts = dict(
        db.query(Product.category, func.count(Product.id))
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .all()
    )
    
    result = []
    for cat in categories:
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "emoji": cat.emoji,
            "display_order": cat.display_order,
            "is_active": cat.is_active,
            "created_at": cat.created_at,
            "product_count": counts.get(cat.name, 0),
        }
        result.append(cat_dict)
    
    return result


# ============================================================
# 2. AUTOCOMPLÉTION
# ============================================================

@router.get("/suggest")
def suggest_categories(
    q: str = Query(..., min_length=1),
    limit: int = 8,
    db: Session = Depends(get_db),
):
    """
    Autocomplétion pour les catégories.
    Utilisé dans le formulaire d'ajout de produit.
    """
    search = f"%{q.lower()}%"
    
    categories = (
        db.query(Category)
        .filter(
            Category.is_active == True,
            func.lower(Category.name).like(search)
        )
        .order_by(Category.display_order, Category.name)
        .limit(limit)
        .all()
    )
    
    return {
        "query": q,
        "suggestions": [
            {
                "id": c.id,
                "name": c.name,
                "emoji": c.emoji or "🏷️",
                "description": c.description,
            }
            for c in categories
        ],
    }


# ============================================================
# 3. DÉTAIL D'UNE CATÉGORIE
# ============================================================

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Détail d'une catégorie."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie introuvable.",
        )
    return cat