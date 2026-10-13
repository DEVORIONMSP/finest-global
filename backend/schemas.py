"""
Schémas Pydantic — validation des entrées/sorties de l'API.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

from models import UserRole, OrderStatus


# ============================================================
# VALIDATION DES NUMÉROS BÉNINOIS
# ============================================================

MTN_PREFIXES = {"42", "46", "50", "51", "52", "53", "54", "56", "57", "59",
                "61", "62", "66", "67", "69", "90", "91", "96", "97"}
MOOV_PREFIXES = {"45", "55", "58", "60", "63", "64", "65", "68", "94", "95", "98", "99"}
CELTIIS_PREFIXES = {"20", "21", "22", "40", "41", "43", "44"}

VALID_PREFIXES = MTN_PREFIXES | MOOV_PREFIXES | CELTIIS_PREFIXES


def detect_operator(phone: str) -> str:
    """Détecte l'opérateur à partir du numéro béninois."""
    if len(phone) != 10 or not phone.startswith("01"):
        return "Inconnu"
    
    prefix = phone[2:4]
    
    if prefix in MTN_PREFIXES:
        return "MTN"
    if prefix in MOOV_PREFIXES:
        return "Moov"
    if prefix in CELTIIS_PREFIXES:
        return "Celtiis"
    return "Inconnu"


def validate_benin_phone(phone: str) -> str:
    """Valide un numéro de téléphone béninois."""
    phone = re.sub(r"[\s\-\(\)]", "", phone)
    if phone.startswith("+229"):
        phone = "0" + phone[4:]
    if phone.startswith("229"):
        phone = "0" + phone[3:]
    
    if len(phone) != 10:
        raise ValueError("Le numéro doit contenir exactement 10 chiffres.")
    
    if not phone.isdigit():
        raise ValueError("Le numéro ne doit contenir que des chiffres.")
    
    if not phone.startswith("01"):
        raise ValueError("Le numéro doit commencer par 01.")
    
    prefix = phone[2:4]
    if prefix not in VALID_PREFIXES:
        raise ValueError(
            f"Préfixe {prefix} non reconnu. "
            f"Opérateurs valides : MTN, Moov, Celtiis."
        )
    
    return phone


# ============================================================
# UTILISATEURS
# ============================================================

class UserBase(BaseModel):
    phone: str = Field(..., description="Numéro béninois à 10 chiffres")


class UserRegisterClient(UserBase):
    """Inscription d'un CLIENT : prénom + nom + téléphone + password."""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        return validate_benin_phone(v)


class UserRegisterSeller(UserBase):
    """Inscription d'un VENDEUR : téléphone + infos supplémentaires."""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        return validate_benin_phone(v)


class UserLogin(BaseModel):
    """Connexion : téléphone + mot de passe."""
    phone: str
    password: str = Field(..., min_length=1)
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        return validate_benin_phone(v)


class UserUpgradeToSeller(BaseModel):
    """Un CLIENT existant qui veut devenir VENDEUR."""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserOut(BaseModel):
    """Ce que l'API renvoie pour un utilisateur."""
    id: int
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: UserRole
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token JWT renvoyé après connexion."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ============================================================
# BOUTIQUES
# ============================================================

class ShopCreate(BaseModel):
    """Création d'une boutique avec géolocalisation."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    
    # 🆕 Géolocalisation
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    locality: Optional[str] = Field(None, max_length=100)
    market: Optional[str] = Field(None, max_length=100)


class ShopUpdate(BaseModel):
    """Mise à jour d'une boutique."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    
    # 🆕 Géolocalisation modifiable
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    locality: Optional[str] = Field(None, max_length=100)
    market: Optional[str] = Field(None, max_length=100)


class ShopOut(BaseModel):
    """Ce que l'API renvoie pour une boutique."""
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    photo_url: Optional[str]
    
    # 🆕 Géolocalisation
    latitude: Optional[float]
    longitude: Optional[float]
    locality: Optional[str]
    market: Optional[str]
    
    # 🆕 Code unique FG-0001
    code: Optional[str]
    
    # 🆕 Statut
    is_active: bool
    
    views_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# PRODUITS
# ============================================================

class ProductCreate(BaseModel):
    """Création d'un produit avec disponibilité."""
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=30)
    
    # 🆕 Disponibilité
    availability: Optional[str] = Field("in_stock", max_length=20)
    
    @field_validator("availability")
    @classmethod
    def validate_availability(cls, v):
        allowed = {"in_stock", "out_of_stock", "to_confirm"}
        if v not in allowed:
            raise ValueError(f"Disponibilité invalide. Valeurs acceptées : {allowed}")
        return v


class ProductUpdate(BaseModel):
    """Mise à jour d'un produit."""
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    color: Optional[str] = None
    in_stock: Optional[bool] = None
    
    # 🆕 Disponibilité
    availability: Optional[str] = Field(None, max_length=20)
    
    @field_validator("availability")
    @classmethod
    def validate_availability(cls, v):
        if v is None:
            return v
        allowed = {"in_stock", "out_of_stock", "to_confirm"}
        if v not in allowed:
            raise ValueError(f"Disponibilité invalide. Valeurs acceptées : {allowed}")
        return v


class ProductOut(BaseModel):
    """Ce que l'API renvoie pour un produit."""
    id: int
    shop_id: int
    name: str
    description: Optional[str]
    price: float
    photo_url: Optional[str]
    category: Optional[str]
    color: Optional[str]
    
    # 🆕 Disponibilité
    availability: str
    
    # Ancien champ (compatibilité)
    in_stock: bool
    
    views_count: int
    sales_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithShopOut(ProductOut):
    """Produit enrichi avec les infos de sa boutique (pour la recherche par distance)."""
    shop_name: Optional[str] = None
    shop_code: Optional[str] = None
    shop_latitude: Optional[float] = None
    shop_longitude: Optional[float] = None
    shop_locality: Optional[str] = None
    shop_market: Optional[str] = None


# ============================================================
# COMMANDES
# ============================================================

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1)
    note: Optional[str] = Field(None, max_length=500)


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: int
    product_id: int
    buyer_id: int
    seller_id: int
    quantity: int
    total_price: float
    status: OrderStatus
    note: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# RECHERCHE
# ============================================================

class SearchResult(BaseModel):
    products: List[ProductOut]
    total: int
    query: Optional[str] = None


# ============================================================
# GÉOLOCALISATION — RECHERCHE
# ============================================================

class LocationSearchParams(BaseModel):
    """Paramètres de recherche par proximité."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(10.0, gt=0, le=100)


# ============================================================
# ADMIN — STATISTIQUES
# ============================================================

class StatsOverview(BaseModel):
    total_users: int
    total_clients: int
    total_sellers: int
    total_shops: int
    total_products: int
    total_orders: int
    total_revenue: float
    pending_orders: int

    class Config:
        from_attributes = True


class VisitorsStats(BaseModel):
    period: str
    total_visits: int
    unique_visitors: int
    data: List[dict]


class TopSeller(BaseModel):
    seller_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    shop_name: Optional[str]
    total_sales: int
    total_revenue: float


class TopProduct(BaseModel):
    product_id: int
    name: str
    shop_name: Optional[str]
    sales_count: int
    views_count: int
    revenue: float


# ============================================================
# PAGE VIEWS (tracking)
# ============================================================

class PageViewCreate(BaseModel):
    path: str
    shop_id: Optional[int] = None
    product_id: Optional[int] = None


# ============================================================
# CATÉGORIES
# ============================================================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    emoji: Optional[str] = Field(None, max_length=10)


class CategoryCreate(CategoryBase):
    display_order: Optional[int] = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    emoji: Optional[str] = Field(None, max_length=10)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryOut(CategoryBase):
    id: int
    display_order: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryWithCount(CategoryOut):
    """Catégorie avec le nombre de produits associés."""
    product_count: int = 0