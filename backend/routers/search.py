"""
Routes de recherche intelligente avec autocomplétion.
Toutes les routes sont publiques (pas d'authentification requise).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from typing import List, Optional
import math

from database import get_db
from models import Product, Shop, User
from schemas import ProductOut


router = APIRouter(prefix="/api/search", tags=["Recherche"])


# ============================================================
# HELPER : Calculer la distance entre 2 points GPS (Haversine)
# ============================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en km entre 2 points GPS.
    Formule de Haversine.
    """
    R = 6371  # Rayon de la Terre en km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


# ============================================================
# 1. RECHERCHE MULTI-CRITÈRES (avec filtres géographiques)
# ============================================================

@router.get("/")
def search_products(
    q: Optional[str] = Query(None, description="Mot-clé (nom, description)"),
    category: Optional[str] = Query(None, description="Catégorie exacte"),
    color: Optional[str] = Query(None, description="Couleur exacte"),
    shop_id: Optional[int] = Query(None, description="Filtrer par boutique"),
    
    # 🆕 Filtres géographiques
    locality: Optional[str] = Query(None, description="Filtrer par localité (Cotonou, Akpakpa...)"),
    market: Optional[str] = Query(None, description="Filtrer par marché (Dantokpa, PK3...)"),
    
    # 🆕 Coordonnées du client pour tri par distance
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude du client"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude du client"),
    radius_km: Optional[float] = Query(None, gt=0, le=100, description="Rayon de recherche en km"),
    
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    availability: Optional[str] = Query(None, description="in_stock | out_of_stock | to_confirm"),
    
    sort_by: str = Query(
        "sales",
        description="sales | recent | price_asc | price_desc | views | distance"
    ),
    skip: int = 0,
    limit: int = 40,
    db: Session = Depends(get_db),
):
    """
    Recherche multi-critères avec :
    - Filtres par localité et marché
    - Tri par distance (si lat/lng fournis)
    - Filtres prix et disponibilité
    """
    # Joindre Shop pour accéder aux filtres géographiques
    query = db.query(Product).join(Shop, Product.shop_id == Shop.id)
    
    # ============================================
    # Recherche textuelle
    # ============================================
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
    
    # ============================================
    # Filtres exacts
    # ============================================
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())
    if color:
        query = query.filter(func.lower(Product.color) == color.lower())
    if shop_id:
        query = query.filter(Product.shop_id == shop_id)
    
    # 🆕 Filtres géographiques
    if locality:
        query = query.filter(func.lower(Shop.locality) == locality.lower())
    if market:
        query = query.filter(func.lower(Shop.market) == market.lower())
    
    # Prix
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # 🆕 Disponibilité
    if availability:
        query = query.filter(Product.availability == availability)
    
    # Filtrer sur boutiques actives
    query = query.filter(Shop.is_active == True)
    
    # ============================================
    # Récupérer TOUS les résultats (avant tri par distance)
    # ============================================
    all_products = query.all()
    
    # ============================================
    # Tri par distance (si lat/lng fournis)
    # ============================================
    products_with_distance = []
    
    for product in all_products:
        shop = product.shop
        distance = None
        
        if latitude is not None and longitude is not None:
            if shop.latitude and shop.longitude:
                distance = haversine_distance(
                    latitude, longitude,
                    shop.latitude, shop.longitude
                )
        
        # Filtrer par radius si demandé
        if radius_km is not None and distance is not None:
            if distance > radius_km:
                continue
        
        products_with_distance.append({
            "product": product,
            "distance": distance,
        })
    
    # ============================================
    # Tri
    # ============================================
    if sort_by == "distance" and latitude is not None:
        # Trier par distance (les None à la fin)
        products_with_distance.sort(
            key=lambda x: x["distance"] if x["distance"] is not None else float('inf')
        )
    elif sort_by == "sales":
        products_with_distance.sort(
            key=lambda x: (x["product"].sales_count, x["product"].created_at),
            reverse=True
        )
    elif sort_by == "views":
        products_with_distance.sort(
            key=lambda x: x["product"].views_count,
            reverse=True
        )
    elif sort_by == "recent":
        products_with_distance.sort(
            key=lambda x: x["product"].created_at,
            reverse=True
        )
    elif sort_by == "price_asc":
        products_with_distance.sort(key=lambda x: x["product"].price)
    elif sort_by == "price_desc":
        products_with_distance.sort(
            key=lambda x: x["product"].price,
            reverse=True
        )
    else:
        products_with_distance.sort(
            key=lambda x: x["product"].sales_count,
            reverse=True
        )
    
    # ============================================
    # Total avant pagination
    # ============================================
    total = len(products_with_distance)
    
    # ============================================
    # Pagination
    # ============================================
    paginated = products_with_distance[skip:skip + limit]
    
    # ============================================
    # Construire la réponse
    # ============================================
    results = []
    for item in paginated:
        product = item["product"]
        product_dict = ProductOut.model_validate(product).model_dump()
        
        # Ajouter les infos de la boutique
        product_dict["shop_name"] = product.shop.name if product.shop else None
        product_dict["shop_code"] = product.shop.code if product.shop else None
        product_dict["shop_latitude"] = product.shop.latitude if product.shop else None
        product_dict["shop_longitude"] = product.shop.longitude if product.shop else None
        product_dict["shop_locality"] = product.shop.locality if product.shop else None
        product_dict["shop_market"] = product.shop.market if product.shop else None
        
        # Ajouter la distance si calculée
        if item["distance"] is not None:
            product_dict["distance_km"] = round(item["distance"], 2)
        
        results.append(product_dict)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "query": q,
        "filters": {
            "category": category,
            "color": color,
            "shop_id": shop_id,
            "locality": locality,
            "market": market,
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "min_price": min_price,
            "max_price": max_price,
            "availability": availability,
            "sort_by": sort_by,
        },
        "results": results,
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
    catégories, couleurs, localités et boutiques existantes.
    """
    search_term = f"%{q.lower()}%"
    
    # Noms de produits
    product_names = (
        db.query(Product.name)
        .filter(func.lower(Product.name).like(search_term))
        .distinct()
        .limit(limit)
        .all()
    )
    
    # Catégories
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
    
    # Couleurs
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
    
    # Boutiques
    shop_names = (
        db.query(Shop.name)
        .filter(func.lower(Shop.name).like(search_term))
        .distinct()
        .limit(limit)
        .all()
    )
    
    # 🆕 Localités
    localities = (
        db.query(Shop.locality)
        .filter(
            Shop.locality.isnot(None),
            func.lower(Shop.locality).like(search_term)
        )
        .distinct()
        .limit(limit)
        .all()
    )
    
    # 🆕 Marchés
    markets = (
        db.query(Shop.market)
        .filter(
            Shop.market.isnot(None),
            func.lower(Shop.market).like(search_term)
        )
        .distinct()
        .limit(limit)
        .all()
    )
    
    # Construire
    suggestions = []
    
    for (name,) in product_names:
        suggestions.append({"text": name, "type": "product"})
    for (cat,) in categories:
        suggestions.append({"text": cat, "type": "category"})
    for (col,) in colors:
        suggestions.append({"text": col, "type": "color"})
    for (shop,) in shop_names:
        suggestions.append({"text": shop, "type": "shop"})
    for (loc,) in localities:
        suggestions.append({"text": loc, "type": "locality"})
    for (mk,) in markets:
        suggestions.append({"text": mk, "type": "market"})
    
    # Dédupliquer
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
    """Renvoie les produits les plus vendus."""
    products = (
        db.query(Product)
        .join(Shop, Product.shop_id == Shop.id)
        .filter(
            Product.sales_count > 0,
            Shop.is_active == True
        )
        .order_by(desc(Product.sales_count), desc(Product.views_count))
        .limit(limit)
        .all()
    )
    
    if not products:
        products = (
            db.query(Product)
            .join(Shop, Product.shop_id == Shop.id)
            .filter(Shop.is_active == True)
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
    """Renvoie toutes les catégories avec leur nombre de produits."""
    categories = (
        db.query(
            Product.category,
            func.count(Product.id).label("count"),
            func.sum(Product.sales_count).label("total_sales"),
        )
        .join(Shop, Product.shop_id == Shop.id)
        .filter(
            Product.category.isnot(None),
            Shop.is_active == True
        )
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
    """Renvoie toutes les couleurs disponibles."""
    colors = (
        db.query(
            Product.color,
            func.count(Product.id).label("count"),
        )
        .join(Shop, Product.shop_id == Shop.id)
        .filter(
            Product.color.isnot(None),
            Shop.is_active == True
        )
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
    """Renvoie les catégories et produits les plus populaires."""
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