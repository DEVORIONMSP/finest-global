"""
Dashboard administrateur.
Toutes les routes sont protégées par require_admin.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from typing import Optional, List

from database import get_db
from models import User, Shop, Product, Order, PageView, UserRole, OrderStatus
from schemas import (
    UserOut, ShopOut, ProductOut, OrderOut,
    StatsOverview, VisitorsStats, TopSeller, TopProduct,
)
from auth import require_admin


router = APIRouter(prefix="/api/admin", tags=["Administration"])


# ============================================================
# 1. VUE D'ENSEMBLE
# ============================================================

@router.get("/stats/overview", response_model=StatsOverview)
def get_overview(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Statistiques globales de la plateforme.
    """
    total_users = db.query(User).count()
    total_clients = db.query(User).filter(User.role == UserRole.CLIENT).count()
    total_sellers = db.query(User).filter(User.role == UserRole.SELLER).count()
    total_shops = db.query(Shop).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    
    # Chiffre d'affaires (commandes confirmées ou livrées)
    revenue_query = (
        db.query(func.sum(Order.total_price))
        .filter(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.DELIVERED]))
        .scalar()
    )
    total_revenue = float(revenue_query or 0)
    
    pending_orders = (
        db.query(Order)
        .filter(Order.status == OrderStatus.PENDING)
        .count()
    )
    
    return StatsOverview(
        total_users=total_users,
        total_clients=total_clients,
        total_sellers=total_sellers,
        total_shops=total_shops,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        pending_orders=pending_orders,
    )


# ============================================================
# 2. VISITEURS PAR PÉRIODE
# ============================================================

@router.get("/stats/visitors", response_model=VisitorsStats)
def get_visitors_stats(
    period: str = "day",
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Statistiques de visiteurs par jour, semaine ou mois.
    """
    now = datetime.utcnow()
    
    if period == "day":
        start = now - timedelta(days=1)
        delta = timedelta(hours=1)
        fmt = "%H:00"
    elif period == "week":
        start = now - timedelta(days=7)
        delta = timedelta(days=1)
        fmt = "%Y-%m-%d"
    elif period == "month":
        start = now - timedelta(days=30)
        delta = timedelta(days=1)
        fmt = "%Y-%m-%d"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Période invalide. Utilisez 'day', 'week' ou 'month'.",
        )
    
    # Récupérer toutes les visites dans la période
    views = (
        db.query(PageView)
        .filter(PageView.created_at >= start)
        .all()
    )
    
    total_visits = len(views)
    unique_visitors = len(set(v.user_id for v in views if v.user_id))
    
    # Grouper par période
    from collections import defaultdict
    counts = defaultdict(int)
    
    for view in views:
        if view.created_at:
            key = view.created_at.strftime(fmt)
            counts[key] += 1
    
    # Générer les entrées (avec 0 pour les périodes vides)
    data = []
    current = start
    while current <= now:
        key = current.strftime(fmt)
        data.append({"date": key, "count": counts.get(key, 0)})
        current += delta
    
    return VisitorsStats(
        period=period,
        total_visits=total_visits,
        unique_visitors=unique_visitors,
        data=data,
    )


# ============================================================
# 3. TOP VENDEURS
# ============================================================

@router.get("/stats/top-sellers", response_model=List[TopSeller])
def get_top_sellers(
    limit: int = 10,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Classement des meilleurs vendeurs par chiffre d'affaires.
    """
    results = (
        db.query(
            User.id,
            User.first_name,
            User.last_name,
            Shop.name.label("shop_name"),
            func.count(Order.id).label("total_sales"),
            func.sum(Order.total_price).label("total_revenue"),
        )
        .join(Shop, Shop.owner_id == User.id)
        .join(Order, Order.seller_id == User.id)
        .filter(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.DELIVERED]))
        .group_by(User.id, Shop.name)
        .order_by(desc("total_revenue"))
        .limit(limit)
        .all()
    )
    
    return [
        TopSeller(
            seller_id=r.id,
            first_name=r.first_name,
            last_name=r.last_name,
            shop_name=r.shop_name,
            total_sales=r.total_sales,
            total_revenue=float(r.total_revenue or 0),
        )
        for r in results
    ]


# ============================================================
# 4. TOP PRODUITS
# ============================================================

@router.get("/stats/top-products", response_model=List[TopProduct])
def get_top_products(
    limit: int = 10,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Classement des produits les plus vendus.
    """
    results = (
        db.query(
            Product.id,
            Product.name,
            Shop.name.label("shop_name"),
            Product.sales_count,
            Product.views_count,
            Product.price,
        )
        .join(Shop, Shop.id == Product.shop_id)
        .order_by(desc(Product.sales_count), desc(Product.views_count))
        .limit(limit)
        .all()
    )
    
    return [
        TopProduct(
            product_id=r.id,
            name=r.name,
            shop_name=r.shop_name,
            sales_count=r.sales_count,
            views_count=r.views_count,
            revenue=float(r.price * r.sales_count),
        )
        for r in results
    ]


# ============================================================
# 5. LISTE DES UTILISATEURS
# ============================================================

@router.get("/users", response_model=List[UserOut])
def list_users(
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Liste tous les utilisateurs (filtrable par rôle).
    """
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    
    return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()


# ============================================================
# 6. LISTE DES BOUTIQUES
# ============================================================

@router.get("/shops", response_model=List[ShopOut])
def list_shops(
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Liste toutes les boutiques.
    """
    return (
        db.query(Shop)
        .order_by(desc(Shop.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================================
# 7. LISTE DES COMMANDES
# ============================================================

@router.get("/orders", response_model=List[OrderOut])
def list_orders(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Liste toutes les commandes (filtrable par statut).
    """
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()