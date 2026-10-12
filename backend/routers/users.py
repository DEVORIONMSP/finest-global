"""
Routes liées aux utilisateurs :
- Inscription client (téléphone uniquement)
- OTP (simulé en dev)
- Connexion vendeur (téléphone/email + password)
- Upgrade client → vendeur
- Profil utilisateur
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import random
import string

from database import get_db
from models import User, UserRole
from schemas import (
    UserRegisterClient,
    UserRegisterSeller,
    UserLogin,
    UserUpgradeToSeller,
    UserOut,
    Token,
    OTPRequest,
    OTPVerify,
    detect_operator,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)


router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


# ============================================================
# STOCKAGE OTP EN MÉMOIRE (dev uniquement)
# En production → Redis ou base de données
# ============================================================

# { "0197123456": {"code": "1234", "expires_at": datetime} }
_otp_store: dict = {}

OTP_EXPIRE_MINUTES = 5


def _generate_otp() -> str:
    """Génère un code à 6 chiffres."""
    return "".join(random.choices(string.digits, k=6))


def _send_sms(phone: str, code: str) -> None:
    """
    Simule l'envoi d'un SMS.
    En production : brancher Twilio, MTN SMS API, ou un service local.
    """
    print(f"\n{'='*50}")
    print(f"📱 SMS SIMULÉ → {phone}")
    print(f"   Code OTP : {code}")
    print(f"{'='*50}\n")


# ============================================================
# 1. INSCRIPTION CLIENT (téléphone uniquement)
# ============================================================

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_client(payload: UserRegisterClient, db: Session = Depends(get_db)):
    """
    Inscription d'un client avec juste son numéro de téléphone.
    L'utilisateur est créé mais non vérifié (is_verified=False).
    Il devra valider un OTP pour se connecter.
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
        role=UserRole.CLIENT,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Générer et "envoyer" un OTP immédiatement
    code = _generate_otp()
    _otp_store[payload.phone] = {
        "code": code,
        "expires_at": datetime.utcnow().timestamp() + OTP_EXPIRE_MINUTES * 60,
    }
    _send_sms(payload.phone, code)
    
    return user


# ============================================================
# 2. DEMANDER UN OTP
# ============================================================

@router.post("/request-otp")
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    """
    Demande un nouveau code OTP pour un numéro déjà enregistré.
    """
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Numéro non enregistré. Inscrivez-vous d'abord.",
        )
    
    code = _generate_otp()
    _otp_store[payload.phone] = {
        "code": code,
        "expires_at": datetime.utcnow().timestamp() + OTP_EXPIRE_MINUTES * 60,
    }
    _send_sms(payload.phone, code)
    
    return {
        "message": "Code envoyé par SMS.",
        "operator": detect_operator(payload.phone),
    }


# ============================================================
# 3. VÉRIFIER L'OTP → CONNEXION
# ============================================================

@router.post("/verify-otp", response_model=Token)
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)):
    """
    Vérifie le code OTP et connecte l'utilisateur.
    """
    # Vérifier que le code existe
    stored = _otp_store.get(payload.phone)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun code en attente pour ce numéro.",
        )
    
    # Vérifier l'expiration
    if datetime.utcnow().timestamp() > stored["expires_at"]:
        del _otp_store[payload.phone]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code expiré. Demandez-en un nouveau.",
        )
    
    # Vérifier le code
    if stored["code"] != payload.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code incorrect.",
        )
    
    # Récupérer l'utilisateur
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )
    
    # Marquer comme vérifié
    user.is_verified = True
    db.commit()
    db.refresh(user)
    
    # Supprimer le code utilisé
    del _otp_store[payload.phone]
    
    # Générer le token JWT
    token = create_access_token({"sub": str(user.id)})
    
    return Token(access_token=token, user=user)


# ============================================================
# 4. INSCRIPTION VENDEUR DIRECTE
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
        is_verified=True,  # Pas d'OTP pour les vendeurs au MVP
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=user)


# ============================================================
# 5. CONNEXION VENDEUR
# ============================================================

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Connexion vendeur : téléphone + password.
    """
    user = db.query(User).filter(User.phone == payload.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Numéro ou mot de passe incorrect.",
        )
    
    # Les vendeurs ont un password_hash. Les clients non.
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est un compte client. Utilisez la connexion par OTP.",
        )
    
    if not payload.password or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Numéro ou mot de passe incorrect.",
        )
    
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=user)


# ============================================================
# 6. UPGRADE CLIENT → VENDEUR
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
    db.commit()
    db.refresh(current_user)
    
    # Nouveau token (le rôle a changé)
    token = create_access_token({"sub": str(current_user.id)})
    return Token(access_token=token, user=current_user)


# ============================================================
# 7. PROFIL UTILISATEUR CONNECTÉ
# ============================================================

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Renvoie le profil de l'utilisateur connecté."""
    return current_user