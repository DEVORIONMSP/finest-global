"""
Routes publiques pour les catégories.
Utilisées par les vendeurs (formulaire produit/service) et les clients (filtres).
Support des 2 types de catégories : 'product' et 'service'.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from database import get_db
from models import Category, Product, Service
from schemas import CategoryOut, CategoryWithCount


router = APIRouter(prefix="/api/categories", tags=["Catégories"])


# ============================================================
# 1. LISTE DES CATÉGORIES ACTIVES (public, filtrable par type)
# ============================================================

@router.get("/", response_model=List[CategoryWithCount])
def list_categories(
    type: Optional[str] = Query(
        None,
        description="Filtrer par type : 'product' ou 'service'. Sans valeur → toutes."
    ),
    db: Session = Depends(get_db),
):
    """
    Liste toutes les catégories actives avec leur nombre d'éléments.
    
    - `?type=product` → uniquement les catégories de produits
    - `?type=service` → uniquement les catégories de services
    - sans `type` → toutes les catégories (produits + services)
    
    Le `product_count` renvoie le nombre de produits OU de services selon le type.
    Triées par display_order puis par nom.
    """
    # Récupérer les catégories actives (filtrées par type si fourni)
    query = db.query(Category).filter(Category.is_active == True)
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.display_order, Category.name).all()
    
    # Compter les produits par catégorie
    product_counts = dict(
        db.query(Product.category, func.count(Product.id))
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .all()
    )
    
    # Compter les services par catégorie
    service_counts = dict(
        db.query(Service.category, func.count(Service.id))
        .filter(Service.category.isnot(None))
        .group_by(Service.category)
        .all()
    )
    
    result = []
    for cat in categories:
        # Choisir le bon compteur selon le type de la catégorie
        if cat.type == "service":
            count = service_counts.get(cat.name, 0)
        else:
            count = product_counts.get(cat.name, 0)
        
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "type": cat.type,
            "description": cat.description,
            "emoji": cat.emoji,
            "display_order": cat.display_order,
            "is_active": cat.is_active,
            "created_at": cat.created_at,
            "product_count": count,
        }
        result.append(cat_dict)
    
    return result


# ============================================================
# 2. AUTOCOMPLÉTION (filtrable par type)
# ============================================================

@router.get("/suggest")
def suggest_categories(
    q: str = Query(..., min_length=1),
    type: Optional[str] = Query(
        None,
        description="Filtrer par type : 'product' ou 'service'."
    ),
    limit: int = 8,
    db: Session = Depends(get_db),
):
    """
    Autocomplétion pour les catégories.
    Utilisé dans le formulaire d'ajout de produit ou de service.
    
    - `?type=product` → propose uniquement les catégories de produits
    - `?type=service` → propose uniquement les catégories de services
    - sans `type` → propose toutes les catégories
    """
    search = f"%{q.lower()}%"
    
    query = db.query(Category).filter(
        Category.is_active == True,
        func.lower(Category.name).like(search)
    )
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = (
        query
        .order_by(Category.display_order, Category.name)
        .limit(limit)
        .all()
    )
    
    return {
        "query": q,
        "type": type,
        "suggestions": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catégorie introuvable.",
        )
    return cat