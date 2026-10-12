"""
Fonctions utilitaires : upload de fichiers, validation, etc.
"""

import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status


# Dossiers d'upload
UPLOAD_DIR = Path("uploads")
SHOPS_DIR = UPLOAD_DIR / "shops"
PRODUCTS_DIR = UPLOAD_DIR / "products"

# Créer les dossiers s'ils n'existent pas
SHOPS_DIR.mkdir(parents=True, exist_ok=True)
PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)


# Types MIME autorisés
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

# Taille max : 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_image(
    file: UploadFile,
    destination: Path,
    prefix: str = "img",
) -> str:
    """
    Sauvegarde une image uploadée.
    Retourne le chemin relatif (à stocker en base).
    """
    # Vérifier le type MIME
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non autorisé : {file.content_type}. "
                   f"Formats acceptés : JPEG, PNG, WEBP.",
        )
    
    # Lire le contenu
    content = await file.read()
    
    # Vérifier la taille
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Maximum : 5 MB.",
        )
    
    # Générer un nom unique
    extension = Path(file.filename).suffix.lower() or ".jpg"
    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        extension = ".jpg"
    
    filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
    filepath = destination / filename
    
    # Écrire le fichier
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Retourner le chemin relatif pour l'URL
    return f"/{filepath.as_posix()}"


def delete_image(relative_path: str) -> None:
    """Supprime une image si elle existe."""
    if not relative_path:
        return
    # Retirer le "/" initial
    path = Path(relative_path.lstrip("/"))
    if path.exists() and path.is_file():
        path.unlink()