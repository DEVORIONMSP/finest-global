"""
Routes de recherche intelligente avec autocomplétion.
Toutes les routes sont publiques (pas d'authentification requise).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from typing import List, Optional

from database import get_db
from models import Product, Shop, User
from schemas import ProductOut


router = APIRouter(prefix="/api/search", tags=["Recherche"])


# ============================================================
# 1. RECHERCHE MULTI-CRITÈRES
# ============================================================

@router.get("/")
def search_products(
    q: Optional[str] = Query(None, description="Mot-clé (nom, description)"),
    category: Optional[str] = Query(None, description="Catégorie exacte"),
    color: Optional[str] = Query(None, description="Couleur exacte"),
    shop_id: Optional[int] = Query(None, description="Filtrer par boutique"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: Optional[bool] = Query(None),
    sort_by: str = Query(
        "sales",
        description="sales (popularité) | recent | price_asc | price_desc | views"
    ),
    skip: int = 0,
    limit: int = 40,
    db: Session = Depends(get_db),
):
    """
    Recherche multi-critères avec tri par défaut sur le nombre de ventes.
    """
    query = db.query(Product)
    
    # Recherche textuelle (nom ou description)
    if q:
        search_term = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Product.name).like(search_term),
                func.lower(Product.description).like(search_term),
                func.lower(Product.category).like(search_term),
                func.lower(Product.color).like(search_term),
            )
        )
    
    # Filtres exacts
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())
    if color:
        query = query.filter(func.lower(Product.color) == color.lower())
    if shop_id:
        query = query.filter(Product.shop_id == shop_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is not None:
        query = query.filter(Product.in_stock == in_stock)
    
    # Tri
    if sort_by == "sales":
        query = query.order_by(desc(Product.sales_count), desc(Product.created_at))
    elif sort_by == "views":
        query = query.order_by(desc(Product.views_count))
    elif sort_by == "recent":
        query = query.order_by(desc(Product.created_at))
    elif sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(desc(Product.sales_count))
    
    # Compter le total avant pagination
    total = query.count()
    
    # Pagination
    products = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "query": q,
        "filters": {
            "category": category,
            "color": color,
            "shop_id": shop_id,
            "min_price": min_price,
            "max_price": max_price,
            "in_stock": in_stock,
            "sort_by": sort_by,
        },
        "results": [ProductOut.model_validate(p) for p in products],
    }


# ============================================================
# 2. AUTOCOMPLÉTION
# ============================================================

@router.get("/suggest")
def suggest(
    q: str = Query(..., min_length=1, description="Ce que l'utilisateur tape"),
    limit: int = 8,
    db: Session = Depends(get_db),
):
    """
    Autocomplétion : renvoie des suggestions basées sur les noms de produits,
    catégories et couleurs existants.
    
    Exemple : q=ch → ["chemise", "chaussure", "chemise en wax"]
    """
    search_term = f"%{q.lower()}%"
    
    # Récupérer les noms de produits qui matchent
    product_names = (
        db.query(Product.name)
        .filter(func.lower(Product.name).like(search_term))
        .distinct()
        .limit(limit)
        .all()
    )
    
    # Récupérer les catégories qui matchent
    categories = (
        db.query(Product.category)
        .filter(
            Product.category.isnot(None),
            func.lower(Product.category).like(search_term)
        )
        .distinct()
        .limit(limit)
        .all()
    )
    
    # Récupérer les couleurs qui matchent
    colors = (
        db.query(Product.color)
        .filter(
            Product.color.isnot(None),
            func.lower(Product.color).like(search_term)
        )
        .distinct()
        .limit(limit)
        .all()
    )
    
    # Récupérer les noms de boutiques
    shop_names = (
        db.query(Shop.name)
        .filter(func.lower(Shop.name).like(search_term))
        .distinct()
        .limit(limit)
        .all()
    )
    
    # Construire la réponse avec type
    suggestions = []
    
    for (name,) in product_names:
        suggestions.append({"text": name, "type": "product"})
    for (cat,) in categories:
        suggestions.append({"text": cat, "type": "category"})
    for (col,) in colors:
        suggestions.append({"text": col, "type": "color"})
    for (shop,) in shop_names:
        suggestions.append({"text": shop, "type": "shop"})
    
    # Dédupliquer par texte
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        key = s["text"].lower()
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(s)
    
    return {
        "query": q,
        "suggestions": unique_suggestions[:limit],
    }


# ============================================================
# 3. PRODUITS LES PLUS VENDUS (trending)
# ============================================================

@router.get("/trending")
def get_trending(
    limit: int = 12,
    db: Session = Depends(get_db),
):
    """
    Renvoie les produits les plus vendus.
    Utilisé pour la page d'accueil de la marketplace.
    """
    products = (
        db.query(Product)
        .filter(Product.sales_count > 0)
        .order_by(desc(Product.sales_count), desc(Product.views_count))
        .limit(limit)
        .all()
    )
    
    # Si pas encore de ventes, renvoyer les plus vus
    if not products:
        products = (
            db.query(Product)
            .order_by(desc(Product.views_count), desc(Product.created_at))
            .limit(limit)
            .all()
        )
    
    return {
        "count": len(products),
        "results": [ProductOut.model_validate(p) for p in products],
    }


# ============================================================
# 4. LISTE DES CATÉGORIES DISPONIBLES
# ============================================================

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Renvoie toutes les catégories avec leur nombre de produits.
    """
    categories = (
        db.query(
            Product.category,
            func.count(Product.id).label("count"),
            func.sum(Product.sales_count).label("total_sales"),
        )
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .order_by(desc("count"))
        .all()
    )
    
    return {
        "categories": [
            {
                "name": cat,
                "product_count": count,
                "total_sales": int(total_sales or 0),
            }
            for cat, count, total_sales in categories
        ]
    }


# ============================================================
# 5. LISTE DES COULEURS DISPONIBLES
# ============================================================

@router.get("/colors")
def get_colors(db: Session = Depends(get_db)):
    """
    Renvoie toutes les couleurs disponibles avec leur nombre de produits.
    """
    colors = (
        db.query(
            Product.color,
            func.count(Product.id).label("count"),
        )
        .filter(Product.color.isnot(None))
        .group_by(Product.color)
        .order_by(desc("count"))
        .all()
    )
    
    return {
        "colors": [
            {"name": color, "product_count": count}
            for color, count in colors
        ]
    }


# ============================================================
# 6. RECHERCHES POPULAIRES
# ============================================================

@router.get("/popular")
def get_popular_searches(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Renvoie les catégories et produits les plus populaires.
    Utilisé pour suggérer des recherches à l'utilisateur.
    """
    # Catégories les plus populaires
    top_categories = (
        db.query(
            Product.category,
            func.sum(Product.sales_count).label("total_sales"),
        )
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .order_by(desc("total_sales"))
        .limit(limit)
        .all()
    )
    
    # Produits les plus vus
    top_products = (
        db.query(Product.name)
        .order_by(desc(Product.views_count))
        .limit(limit)
        .all()
    )
    
    return {
        "popular_categories": [
            {"name": cat, "total_sales": int(sales or 0)}
            for cat, sales in top_categories
        ],
        "popular_products": [name for (name,) in top_products],
    }