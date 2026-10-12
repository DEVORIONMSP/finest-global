"""
Script d'initialisation : crée toutes les tables dans la base.
À exécuter une seule fois au début.
"""

from database import engine, Base
from models import User, Shop, Product, Order, PageView

def init_database():
    print("🔄 Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée avec succès !")
    print(f"📁 Fichier créé : finest_global.db")

if __name__ == "__main__":
    init_database()