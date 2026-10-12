"""
Configuration de la base de données.
Utilise SQLite en développement (fichier local), facile à migrer vers PostgreSQL en prod.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de la base de données
# SQLite crée un fichier "finest_global.db" dans le dossier backend/
SQLALCHEMY_DATABASE_URL = "sqlite:///./finest_global.db"

# Création du moteur
# check_same_thread=False est nécessaire pour SQLite + FastAPI (multi-thread)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session locale (une session par requête)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour tous les modèles
Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI : fournit une session de base de données
    et la ferme automatiquement après la requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()