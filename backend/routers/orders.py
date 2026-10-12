"""
Routes liées aux commandes.
Une commande relie un client (acheteur), un produit et son vendeur.
Le vendeur reçoit une notification WebSocket instantanée.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List

from database import get_db
from models import User, Shop, Product, Order, UserRole, OrderStatus
from schemas import OrderCreate, OrderOut, OrderUpdateStatus
from auth import require_seller, get_current_user
from websocket import notify_new_order, notify_order_status


router = APIRouter(prefix="/api/orders", tags=["Commandes"])


# ============================================================
# 1. PASSER UNE COMMANDE (client)
# ============================================================

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Un client connecté passe une commande sur un produit.
    Le vendeur reçoit une notification WebSocket instantanée.
    """
    # Vérifier le produit
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit introuvable.",
        )
    
    if not product.in_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce produit n'est plus en stock.",
        )
    
    # Récupérer la boutique et son propriétaire
    shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Boutique introuvable.",
        )
    
    # Un vendeur ne peut pas commander chez lui-même
    if shop.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas commander votre propre produit.",
        )
    
    # Créer la commande
    total_price = product.price * payload.quantity
    order = Order(
        product_id=product.id,
        buyer_id=current_user.id,
        seller_id=shop.owner_id,
        quantity=payload.quantity,
        total_price=total_price,
        note=payload.note,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Notifier le vendeur en temps réel
    await notify_new_order(shop.owner_id, {
        "order_id": order.id,
        "product_name": product.name,
        "quantity": order.quantity,
        "total_price": order.total_price,
        "buyer_phone": current_user.phone,
        "buyer_name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or "Client",
        "note": order.note,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    })
    
    return order


# ============================================================
# 2. MES COMMANDES (client)
# ============================================================

@router.get("/me", response_model=List[OrderOut])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Liste les commandes passées par le client connecté.
    """
    orders = (
        db.query(Order)
        .filter(Order.buyer_id == current_user.id)
        .order_by(desc(Order.created_at))
        .all()
    )
    return orders


# ============================================================
# 3. COMMANDES REÇUES (vendeur)
# ============================================================

@router.get("/received", response_model=List[OrderOut])
def get_received_orders(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Liste les commandes reçues par le vendeur connecté.
    """
    orders = (
        db.query(Order)
        .filter(Order.seller_id == current_user.id)
        .order_by(desc(Order.created_at))
        .all()
    )
    return orders


# ============================================================
# 4. VOIR UNE COMMANDE (partie prenante)
# ============================================================

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Renvoie une commande. Seul l'acheteur ou le vendeur peut la voir.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )
    
    if current_user.id not in (order.buyer_id, order.seller_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette commande.",
        )
    
    return order


# ============================================================
# 5. CHANGER LE STATUT D'UNE COMMANDE (vendeur)
# ============================================================

@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    payload: OrderUpdateStatus,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Le vendeur confirme, livre ou annule une commande.
    Le client est notifié en temps réel du changement.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )
    
    # Seul le vendeur peut changer le statut
    if order.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres commandes.",
        )
    
    # Empêcher de revenir en arrière depuis un état final
    if order.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette commande est déjà {order.status.value} et ne peut plus être modifiée.",
        )
    
    old_status = order.status
    order.status = payload.status
    
    # Si la commande est confirmée, incrémenter le compteur de ventes
    if payload.status == OrderStatus.CONFIRMED and old_status == OrderStatus.PENDING:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.sales_count += order.quantity
    
    db.commit()
    db.refresh(order)
    
    # Notifier le client en temps réel
    await notify_order_status(order.buyer_id, order.id, order.status.value)
    
    return order