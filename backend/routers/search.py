"""
Routes de recherche intelligente avec autocomplétion.
Toutes les routes sont publiques (pas d'authentification requise).
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_
from typing import List, Optional
import math
from utils import save_image, delete_image, PRODUCTS_DIR # 🆕 Pour l'upload d'image de recherche

from database import get_db
from models import Product, Shop, User, Service # 🆕 Service ajouté
from schemas import ProductOut


router = APIRouter(prefix="/api/search", tags=["Recherche"])


# ============================================================
# HELPER : Calculer la distance entre 2 points GPS (Haversine)
# ============================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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
# 1. RECHERCHE MULTI-CRITÈRES (Texte)
# ============================================================

@router.get("/")
def search_products(
    q: Optional[str] = Query(None, description="Mot-clé (nom, description)"),
    category: Optional[str] = Query(None, description="Catégorie exacte"),
    color: Optional[str] = Query(None, description="Couleur exacte"),
    shop_id: Optional[int] = Query(None, description="Filtrer par boutique"),
    
    locality: Optional[str] = Query(None, description="Filtrer par localité"),
    market: Optional[str] = Query(None, description="Filtrer par marché"),
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude du client"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude du client"),
    radius_km: Optional[float] = Query(None, gt=0, le=100, description="Rayon de recherche en km"),
    
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    availability: Optional[str] = Query(None, description="in_stock | out_of_stock | to_confirm"),
    sort_by: str = Query("sales", description="sales | recent | price_asc | price_desc | views | distance"),
    skip: int = 0,
    limit: int = 40,
    db: Session = Depends(get_db),
):
    """
    Recherche textuelle multi-critères.
    """
    query = db.query(Product).join(Shop, Product.shop_id == Shop.id)
    query = query.filter(Shop.is_active == True)
    
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
    
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())
    if color:
        query = query.filter(func.lower(Product.color) == color.lower())
    if shop_id:
        query = query.filter(Product.shop_id == shop_id)
    if locality:
        query = query.filter(func.lower(Shop.locality) == locality.lower())
    if market:
        query = query.filter(func.lower(Shop.market) == market.lower())
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if availability:
        query = query.filter(Product.availability == availability)
    
    all_products = query.all()
    products_with_distance = []
    
    for product in all_products:
        shop = product.shop
        distance = None
        if latitude is not None and longitude is not None:
            if shop.latitude and shop.longitude:
                distance = haversine_distance(latitude, longitude, shop.latitude, shop.longitude)
        if radius_km is not None and distance is not None:
            if distance > radius_km:
                continue
        products_with_distance.append({"product": product, "distance": distance})
    
    if sort_by == "distance" and latitude is not None:
        products_with_distance.sort(key=lambda x: x["distance"] if x["distance"] is not None else float('inf'))
    elif sort_by == "sales":
        products_with_distance.sort(key=lambda x: (x["product"].sales_count, x["product"].created_at), reverse=True)
    elif sort_by == "views":
        products_with_distance.sort(key=lambda x: x["product"].views_count, reverse=True)
    elif sort_by == "recent":
        products_with_distance.sort(key=lambda x: x["product"].created_at, reverse=True)
    elif sort_by == "price_asc":
        products_with_distance.sort(key=lambda x: x["product"].price)
    elif sort_by == "price_desc":
        products_with_distance.sort(key=lambda x: x["product"].price, reverse=True)
    else:
        products_with_distance.sort(key=lambda x: x["product"].sales_count, reverse=True)
    
    total = len(products_with_distance)
    paginated = products_with_distance[skip:skip + limit]
    results = []
    
    for item in paginated:
        product = item["product"]
        product_dict = ProductOut.model_validate(product).model_dump()
        product_dict["shop_name"] = product.shop.name if product.shop else None
        product_dict["shop_code"] = product.shop.code if product.shop else None
        product_dict["shop_latitude"] = product.shop.latitude if product.shop else None
        product_dict["shop_longitude"] = product.shop.longitude if product.shop else None
        product_dict["shop_locality"] = product.shop.locality if product.shop else None
        product_dict["shop_market"] = product.shop.market if product.shop else None
        if item["distance"] is not None:
            product_dict["distance_km"] = round(item["distance"], 2)
        results.append(product_dict)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "query": q,
        "results": results,
    }


# ============================================================
# 🆕 1.5 RECHERCHE PAR IMAGE (Upload d'image)
# ============================================================

@router.post("/by-image")
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    🆕 Recherche par image.
    Le client upload une photo, le système extrait les caractéristiques
    (couleur dominante, forme via IA) et renvoie des produits similaires.
    
    Pour l'instant, on utilise une recherche basique par couleur détectée
    ou par mot-clé (si on intègre une API comme Google Vision plus tard).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image (JPEG, PNG, WEBP)."
        )
    
    # 1. Sauvegarder l'image temporairement pour l'analyse
    temp_url = await save_image(file, PRODUCTS_DIR, prefix="search_temp")
    
    try:
        # 2. Analyse de l'image
        # ⚠️ ÉTAPE FUTURE : Intégrer une IA (Google Vision, AWS Rekognition, ou un modèle local)
        # Pour l'instant, on simule une recherche basique.
        # Exemple : on cherche tous les produits qui ont une image et on prend les 20 premiers.
        
        # Simulation : On récupère les produits avec des images
        products = (
            db.query(Product)
            .join(Shop, Product.shop_id == Shop.id)
            .filter(Product.photo_url.isnot(None), Shop.is_active == True)
            .order_by(desc(Product.views_count))
            .limit(limit)
            .all()
        )
        
        results = [ProductOut.model_validate(p).model_dump() for p in products]
        
        return {
            "message": "Recherche par image effectuée (IA à venir).",
            "total": len(results),
            "results": results
        }
        
    finally:
        # 3. Supprimer l'image temporaire
        delete_image(temp_url)


# ============================================================
# 🆕 1.6 RECHERCHE PAR CODE VENDEUR (Raccourci)
# ============================================================

@router.get("/by-seller-code/{code}")
def search_by_seller_code(
    code: str,
    db: Session = Depends(get_db),
):
    """
    🆕 Recherche par code vendeur.
    Le client entre un code (ex: FG-0001), on renvoie directement la vitrine.
    """
    shop = db.query(Shop).filter(
        func.upper(Shop.code) == code.upper(),
        Shop.is_active == True
    ).first()
    
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune boutique trouvée avec ce code.",
        )
    
    return {
        "type": "shop",
        "shop_id": shop.id,
        "shop_name": shop.name,
        "shop_code": shop.code,
        "message": "Redirection vers la vitrine..."
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
    search_term = f"%{q.lower()}%"
    
    product_names = (
        db.query(Product.name)
        .join(Shop, Product.shop_id == Shop.id)
        .filter(func.lower(Product.name).like(search_term), Shop.is_active == True)
        .distinct().limit(limit).all()
    )
    
    categories = (
        db.query(Product.category)
        .join(Shop, Product.shop_id == Shop.id)
        .filter(Product.category.isnot(None), func.lower(Product.category).like(search_term), Shop.is_active == True)
        .distinct().limit(limit).all()
    )
    
    colors = (
        db.query(Product.color)
        .join(Shop, Product.shop_id == Shop.id)
        .filter(Product.color.isnot(None), func.lower(Product.color).like(search_term), Shop.is_active == True)
        .distinct().limit(limit).all()
    )
    
    shop_names = (
        db.query(Shop.name)
        .filter(func.lower(Shop.name).like(search_term), Shop.is_active == True)
        .distinct().limit(limit).all()
    )
    
    localities = (
        db.query(Shop.locality)
        .filter(Shop.locality.isnot(None), func.lower(Shop.locality).like(search_term), Shop.is_active == True)
        .distinct().limit(limit).all()
    )
    
    markets = (
        db.query(Shop.market)
        .filter(Shop.market.isnot(None), func.lower(Shop.market).like(search_term), Shop.is_active == True)
        .distinct().limit(limit).all()
    )
    
    suggestions = []
    for (name,) in product_names: suggestions.append({"text": name, "type": "product"})
    for (cat,) in categories: suggestions.append({"text": cat, "type": "category"})
    for (col,) in colors: suggestions.append({"text": col, "type": "color"})
    for (shop,) in shop_names: suggestions.append({"text": shop, "type": "shop"})
    for (loc,) in localities: suggestions.append({"text": loc, "type": "locality"})
    for (mk,) in markets: suggestions.append({"text": mk, "type": "market"})
    
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        key = s["text"].lower()
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(s)
    
    return {"query": q, "suggestions": unique_suggestions[:limit]}


# ============================================================
# 3. PRODUITS LES PLUS VENDUS (trending)
# ============================================================

@router.get("/trending")
def get_trending(
    limit: int = 12,
    db: Session = Depends(get_db),
):
    products = (
        db.query(Product)
        .join(Shop, Product.shop_id == Shop.id)
        .filter(Product.sales_count > 0, Shop.is_active == True)
        .order_by(desc(Product.sales_count), desc(Product.views_count))
        .limit(limit).all()
    )
    
    if not products:
        products = (
            db.query(Product)
            .join(Shop, Product.shop_id == Shop.id)
            .filter(Shop.is_active == True)
            .order_by(desc(Product.views_count), desc(Product.created_at))
            .limit(limit).all()
        )
    
    return {"count": len(products), "results": [ProductOut.model_validate(p) for p in products]}


# ============================================================
# 4. LISTE DES CATÉGORIES DISPONIBLES
# ============================================================

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Product.category, func.count(Product.id).label("count"), func.sum(Product.sales_count).label("total_sales"))
        .join(Shop, Product.shop_id == Shop.id)
        .filter(Product.category.isnot(None), Shop.is_active == True)
        .group_by(Product.category)
        .order_by(desc("count")).all()
    )
    return {"categories": [{"name": cat, "product_count": count, "total_sales": int(total_sales or 0)} for cat, count, total_sales in categories]}


# ============================================================
# 5. LISTE DES COULEURS DISPONIBLES
# ============================================================

@router.get("/colors")
def get_colors(db: Session = Depends(get_db)):
    colors = (
        db.query(Product.color, func.count(Product.id).label("count"))
        .join(Shop, Product.shop_id == Shop.id)
        .filter(Product.color.isnot(None), Shop.is_active == True)
        .group_by(Product.color)
        .order_by(desc("count")).all()
    )
    return {"colors": [{"name": color, "product_count": count} for color, count in colors]}


# ============================================================
# 6. RECHERCHES POPULAIRES
# ============================================================

@router.get("/popular")
def get_popular_searches(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    top_categories = (
        db.query(Product.category, func.sum(Product.sales_count).label("total_sales"))
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .order_by(desc("total_sales")).limit(limit).all()
    )
    top_products = (
        db.query(Product.name)
        .order_by(desc(Product.views_count)).limit(limit).all()
    )
    return {
        "popular_categories": [{"name": cat, "total_sales": int(sales or 0)} for cat, sales in top_categories],
        "popular_products": [name for (name,) in top_products],
    }