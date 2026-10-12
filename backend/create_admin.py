"""
Crée un administrateur dans la base.
À exécuter une seule fois.
"""

from database import SessionLocal
from models import User, UserRole
from auth import hash_password


def create_admin():
    db = SessionLocal()
    try:
        # Vérifier si l'admin existe déjà
        existing = db.query(User).filter(User.phone == "0142000000").first()
        if existing:
            print("✅ Admin déjà existant.")
            return
        
        # Créer l'admin
        admin = User(
            phone="0142000000",  # numéro factice
            first_name="Super",
            last_name="Admin",
            email="admin@finestglobal.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Admin créé :")
        print(f"   ID       : {admin.id}")
        print(f"   Phone    : {admin.phone}")
        print(f"   Password : admin123")
        print(f"   Role     : {admin.role}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()