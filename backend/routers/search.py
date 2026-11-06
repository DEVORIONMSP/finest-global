"""
Routes de recherche intelligente avec autocomplétion.
Toutes les routes sont publiques (pas d'authentification requise).
"""
import os
import math
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_, and_, text
from google import genai
from google.genai import types

from database import get_db
from models import Product, Shop, User, Service
from schemas import ProductOut

router = APIRouter(prefix="/api/search", tags=["Recherche"])

# 🆕 Initialisation du client Gemini pour la recherche sémantique
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


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
# 1. RECHERCHE MULTI-CRITÈRES (Texte classique)
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
# 2. RECHERCHE PAR CODE VENDEUR (Raccourci)
# ============================================================

@router.get("/by-seller-code/{code}")
def search_by_seller_code(
    code: str,
    db: Session = Depends(get_db),
):
    """
    Recherche par code vendeur.
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
# 3. AUTOCOMPLÉTION
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
# 4. PRODUITS LES PLUS VENDUS (trending)
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
# 5. LISTE DES CATÉGORIES DISPONIBLES
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
# 6. LISTE DES COULEURS DISPONIBLES
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
# 7. RECHERCHES POPULAIRES
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


# ============================================================
# 8. 🆕 RECHERCHE SÉMANTIQUE (Texte ou Image via Gemini)
# ============================================================

@router.post("/semantic")
async def semantic_search(
    query_text: str = Form(None, description="Texte à rechercher"),
    file: UploadFile = File(None, description="Image à rechercher"),
    limit: int = Form(12),
    db: Session = Depends(get_db),
):
    """
    Recherche intelligente : accepte un texte OU une image.
    Utilise Gemini Embeddings pour trouver les produits les plus similaires.
    """
    if not gemini_client:
        raise HTTPException(
            status_code=500,
            detail="Clé API Gemini manquante sur le serveur.",
        )

    # 1. Construire la requête (texte, image, ou les deux)
    contents = []
    
    # On nettoie le texte pour éviter les chaînes vides
    clean_text = query_text.strip() if query_text else ""
    
    if clean_text:
        contents.append(clean_text)
    
    if file:
        image_bytes = await file.read()
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=file.content_type)
        )
        # 🆕 Si on a une image mais pas de texte, on ajoute un texte par défaut
        # (Gemini exige au moins une partie texte pour comprendre le contexte)
        if not clean_text:
            contents.insert(0, "Analyse cette image pour trouver des produits similaires.")

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Veuillez fournir un texte ou une image.",
        )

    try:
        # 2. Générer l'embedding de la requête utilisateur
        result = gemini_client.models.embed_content(
            model="gemini-embedding-001",
            contents=contents,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768,
            ),
        )
        query_vector = result.embeddings[0].values
        vector_str = '[' + ','.join(str(x) for x in query_vector) + ']'

        # 3. Chercher les produits les plus proches (similarité cosinus)
        sql = text("""
            SELECT 
                id, name, description, price, photo_url, category, color,
                1 - (embedding <=> CAST(:vec AS vector)) AS similarity
            FROM products
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:vec AS vector)
            LIMIT :limit;
        """)

        rows = db.execute(sql, {"vec": vector_str, "limit": limit}).fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "price": row.price,
                "photo_url": row.photo_url,
                "category": row.category,
                "color": row.color,
                "similarity": round(float(row.similarity), 4),
            })

        return {
            "query": query_text,
            "type": "image" if file else "text",
            "count": len(results),
            "results": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de recherche : {str(e)}",
        )