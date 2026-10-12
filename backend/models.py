"""
Modèles SQLAlchemy — définition de toutes les tables de la base de données.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    ForeignKey, Enum, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


# ============================================================
# ÉNUMÉRATIONS
# ============================================================

class UserRole(str, enum.Enum):
    """Rôles possibles d'un utilisateur."""
    CLIENT = "client"
    SELLER = "seller"
    ADMIN = "admin"


class OrderStatus(str, enum.Enum):
    """Statuts possibles d'une commande."""
    PENDING = "pending"       # en attente
    CONFIRMED = "confirmed"   # confirmée par le vendeur
    DELIVERED = "delivered"   # livrée
    CANCELLED = "cancelled"   # annulée


# ============================================================
# UTILISATEURS
# ============================================================

class User(Base):
    """
    Table des utilisateurs.
    - Un CLIENT s'inscrit juste avec son téléphone.
    - Un SELLER ajoute nom, prénom, email.
    - Un ADMIN est créé manuellement en base.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(10), unique=True, index=True, nullable=False)
    
    # Champs vendeur (nullables pour les clients)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    
    # Rôle
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    
    # Vérification téléphone (OTP simulé en dev)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    shop = relationship("Shop", back_populates="owner", uselist=False)
    orders = relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    
    def __repr__(self):
        return f"<User {self.phone} ({self.role})>"


# ============================================================
# BOUTIQUES
# ============================================================

class Shop(Base):
    """
    Boutique créée par un vendeur.
    Un vendeur = une boutique (relation 1-1).
    """
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    photo_url = Column(String(255), nullable=True)
    
    # Statistiques
    views_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    owner = relationship("User", back_populates="shop")
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Shop {self.name}>"


# ============================================================
# PRODUITS
# ============================================================

class Product(Base):
    """
    Produit ajouté par un vendeur dans sa boutique.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    photo_url = Column(String(255), nullable=True)
    
    # Catégorisation (pour la recherche)
    category = Column(String(50), nullable=True, index=True)
    color = Column(String(30), nullable=True, index=True)
    
    # Statistiques
    views_count = Column(Integer, default=0, nullable=False)
    sales_count = Column(Integer, default=0, nullable=False)
    
    # Stock
    in_stock = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    shop = relationship("Shop", back_populates="products")
    orders = relationship("Order", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name} - {self.price} FCFA>"


# ============================================================
# COMMANDES
# ============================================================

class Order(Base):
    """
    Commande passée par un client sur un produit.
    Le vendeur reçoit une notification en temps réel.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    quantity = Column(Integer, default=1, nullable=False)
    total_price = Column(Float, nullable=False)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Note du client (optionnel)
    note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    product = relationship("Product", back_populates="orders")
    buyer = relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    
    def __repr__(self):
        return f"<Order #{self.id} - {self.status}>"


# ============================================================
# VISITES (pour les stats)
# ============================================================

class PageView(Base):
    """
    Enregistre chaque visite de page pour les statistiques.
    Utilisé par le dashboard admin (visiteurs/jour/semaine/mois)
    et le dashboard vendeur (visiteurs de la boutique).
    """
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    path = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)





# ============================================================
# CATÉGORIES
# ============================================================

class Category(Base):
    """
    Catégories de produits, gérées par l'admin.
    Les vendeurs sélectionnent une catégorie lors de l'ajout d'un produit.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    emoji = Column(String(10), nullable=True)  # 🏷️, 👗, 👟...
    
    # Ordre d'affichage (permet de mettre les catégories populaires en premier)
    display_order = Column(Integer, default=0, nullable=False)
    
    # Une catégorie peut être désactivée sans être supprimée
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Category {self.name}>"