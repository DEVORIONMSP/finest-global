"""
Crée un administrateur dans la base.

Usage :
    python create_admin.py                          # Crée l'admin par défaut
    python create_admin.py <phone> <password> <first_name> <last_name> <email>

Exemples :
    python create_admin.py
    python create_admin.py 0142000001 motdepasse123 Marie Admin marie@finestglobal.com
"""

import sys
from database import SessionLocal
from models import User, UserRole
from auth import hash_password


def create_admin(phone, password, first_name, last_name, email):
    db = SessionLocal()
    try:
        # Vérifier si un utilisateur avec ce téléphone existe déjà
        existing = db.query(User).filter(User.phone == phone).first()
        if existing:
            if existing.role == UserRole.ADMIN:
                print(f"⚠️  Un admin avec ce numéro existe déjà : {existing.phone}")
            else:
                print(f"⚠️  Un utilisateur avec ce numéro existe déjà (rôle: {existing.role.value})")
            return False
        
        # Vérifier l'email
        if email:
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                print(f"⚠️  Cet email est déjà utilisé : {email}")
                return False
        
        # Créer l'admin
        admin = User(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("=" * 55)
        print("✅ NOUVEAU ADMIN CRÉÉ AVEC SUCCÈS")
        print("=" * 55)
        print(f"   ID       : {admin.id}")
        print(f"   Phone    : {admin.phone}")
        print(f"   Nom      : {admin.first_name} {admin.last_name}")
        print(f"   Email    : {admin.email}")
        print(f"   Password : {password}")
        print(f"   Rôle     : {admin.role.value}")
        print("=" * 55)
        return True
        
    finally:
        db.close()


def create_default_admin():
    """Crée l'admin par défaut (utilisé pour le développement local)."""
    return create_admin(
        phone="0142000000",
        password="admin123",
        first_name="Super",
        last_name="Admin",
        email="admin@finestglobal.com",
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Pas d'arguments → admin par défaut
        create_default_admin()
    elif len(sys.argv) == 6:
        # Arguments fournis
        phone, password, first_name, last_name, email = sys.argv[1:6]
        create_admin(phone, password, first_name, last_name, email)
    else:
        print("Usage :")
        print("  python create_admin.py")
        print("  python create_admin.py <phone> <password> <first_name> <last_name> <email>")
        print()
        print("Exemples :")
        print("  python create_admin.py")
        print('  python create_admin.py 0142000001 motdepasse123 Marie Admin marie@finestglobal.com')
        sys.exit(1)