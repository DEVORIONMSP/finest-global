"""
Modèles SQLAlchemy — définition de toutes les tables de la base de données.
"""
from pgvector.sqlalchemy import Vector
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
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(10), unique=True, index=True, nullable=False)
    
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    
    # 🆕 Photo de profil
    photo_url = Column(String(255), nullable=True)
    
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    shop = relationship("Shop", back_populates="owner", uselist=False)
    orders = relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    
    def __repr__(self):
        return f"<User {self.phone} ({self.role})>"


# ============================================================
# BOUTIQUES
# ============================================================

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    photo_url = Column(String(255), nullable=True)
    
    # GÉOLOCALISATION
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    locality = Column(String(100), nullable=True, index=True)
    market = Column(String(100), nullable=True, index=True)
    
    # CODE UNIQUE (FG-0001)
    code = Column(String(20), unique=True, nullable=True, index=True)
    
    # ACTIF
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Statistiques
    views_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    owner = relationship("User", back_populates="shop")
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="shop", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Shop {self.name}>"


# ============================================================
# PRODUITS
# ============================================================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # PRIX
    price = Column(Float, nullable=False) # 0 si non fixe
    is_price_fixed = Column(Boolean, default=True, nullable=False)
    
    photo_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    
    # Catégorisation
    category = Column(String(50), nullable=True, index=True)
    color = Column(String(30), nullable=True, index=True)
    
    # DISPONIBILITÉ / STOCK
    availability = Column(String(20), default="in_stock", nullable=False)
    stock_quantity = Column(String(50), nullable=True)
    
    # Ancien champ conservé pour compatibilité
    in_stock = Column(Boolean, default=True, nullable=False)
    
    # Statistiques
    views_count = Column(Integer, default=0, nullable=False)
    sales_count = Column(Integer, default=0, nullable=False)
    
    # 🆕 Vecteur Gemini pour la recherche sémantique (768 dimensions)
    embedding = Vector(768)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    shop = relationship("Shop", back_populates="products")
    orders = relationship("Order", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name} - {self.price} FCFA>"


# ============================================================
# SERVICES
# ============================================================

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # PRIX
    price = Column(Float, nullable=True)
    is_price_fixed = Column(Boolean, default=True, nullable=False)
    
    category = Column(String(50), nullable=True, index=True)
    service_area = Column(String(100), nullable=True, index=True)
    availability_info = Column(Text, nullable=True)
    
    photo_url = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    
    views_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    shop = relationship("Shop", back_populates="services")
    
    def __repr__(self):
        return f"<Service {self.name} - {self.price} FCFA>"


# ============================================================
# COMMANDES
# ============================================================

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    quantity = Column(Integer, default=1, nullable=False)
    total_price = Column(Float, nullable=False)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    note = Column(Text, nullable=True)
    screenshot_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", back_populates="orders")
    service = relationship("Service")
    buyer = relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    
    def __repr__(self):
        return f"<Order #{self.id} - {self.status}>"


# ============================================================
# VISITES (pour les stats)
# ============================================================

class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    
    path = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ============================================================
# CATÉGORIES
# ============================================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    type = Column(String(20), default="product", nullable=False)
    description = Column(String(255), nullable=True)
    emoji = Column(String(10), nullable=True)
    
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Category {self.name} ({self.type})>"


# ============================================================
# NOTIFICATIONS
# ============================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    
    link = Column(String(255), nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - User {self.user_id} - {self.title}>"