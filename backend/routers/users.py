"""
Routes liées aux utilisateurs :
- Inscription client (nom + téléphone + password)
- Inscription vendeur (nom + email + téléphone + password)
- Connexion (téléphone + password) pour TOUS
- Upgrade client → vendeur
- Profil utilisateur
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole
from schemas import (
    UserRegisterClient,
    UserRegisterSeller,
    UserLogin,
    UserUpgradeToSeller,
    UserOut,
    Token,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)


router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


# ============================================================
# 1. INSCRIPTION CLIENT (nom + téléphone + password)
# ============================================================

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_client(payload: UserRegisterClient, db: Session = Depends(get_db)):
    """
    Inscription d'un client avec prénom, nom, téléphone et password.
    Le client est directement connecté après inscription.
    """
    # Vérifier si le numéro existe déjà
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro est déjà enregistré. Connectez-vous.",
        )
    
    # Créer l'utilisateur
    user = User(
        phone=payload.phone,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=hash_password(payload.password),
        role=UserRole.CLIENT,
        is_verified=True,  # Plus besoin de vérification OTP
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Générer le token JWT immédiatement (connexion automatique)
    token = create_access_token({"sub": str(user.id)})
    
    return Token(access_token=token, user=user)


# ============================================================
# 2. INSCRIPTION VENDEUR DIRECTE
# ============================================================

@router.post("/register-seller", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_seller(payload: UserRegisterSeller, db: Session = Depends(get_db)):
    """
    Inscription directe d'un vendeur.
    Téléphone + nom + prénom + email + password.
    """
    # Vérifier téléphone
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro est déjà enregistré.",
        )
    
    # Vérifier email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé.",
        )
    
    # Créer le vendeur
    user = User(
        phone=payload.phone,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.SELLER,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=user)


# ============================================================
# 3. CONNEXION (téléphone + password) — pour TOUS les rôles
# ============================================================

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Connexion : téléphone + password.
    Fonctionne pour les clients, les vendeurs et les admins.
    """
    user = db.query(User).filter(User.phone == payload.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Numéro ou mot de passe incorrect.",
        )
    
    # Vérifier que le compte a bien un mot de passe
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte n'a pas de mot de passe. Contactez le support.",
        )
    
    # Vérifier le mot de passe
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Numéro ou mot de passe incorrect.",
        )
    
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=user)


# ============================================================
# 4. UPGRADE CLIENT → VENDEUR
# ============================================================

@router.post("/upgrade-to-seller", response_model=Token)
def upgrade_to_seller(
    payload: UserUpgradeToSeller,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Un client connecté devient vendeur.
    Ajoute les infos manquantes : nom, prénom, email, password.
    """
    # Déjà vendeur ?
    if current_user.role == UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous êtes déjà vendeur.",
        )
    
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un admin ne peut pas devenir vendeur.",
        )
    
    # Vérifier email
    if db.query(User).filter(
        User.email == payload.email,
        User.id != current_user.id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé.",
        )
    
    # Mettre à jour
    current_user.first_name = payload.first_name
    current_user.last_name = payload.last_name
    current_user.email = payload.email
    current_user.password_hash = hash_password(payload.password)
    current_user.role = UserRole.SELLER
    current_user.is_verified = True
    db.commit()
    db.refresh(current_user)
    
    # Nouveau token (le rôle a changé)
    token = create_access_token({"sub": str(current_user.id)})
    return Token(access_token=token, user=current_user)


# ============================================================
# 5. PROFIL UTILISATEUR CONNECTÉ
# ============================================================

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Renvoie le profil de l'utilisateur connecté."""
    return current_user