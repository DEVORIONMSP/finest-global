"""
Upload de fichiers vers Cloudinary (production) ou local (dev).
Gère les images ET les vidéos.
"""

import os
import uuid
import time
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

# Configuration Cloudinary
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")

if CLOUDINARY_URL:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)
    USE_CLOUDINARY = True
    print("✅ Cloudinary configuré")
else:
    USE_CLOUDINARY = False
    print("⚠️  Cloudinary non configuré, utilisation du stockage local")

# Dossiers d'upload locaux (dev uniquement)
UPLOAD_DIR = Path("uploads")
SHOPS_DIR = UPLOAD_DIR / "shops"
PRODUCTS_DIR = UPLOAD_DIR / "products"
VIDEOS_DIR = UPLOAD_DIR / "videos" # 🆕 Dossier pour les vidéos

SHOPS_DIR.mkdir(parents=True, exist_ok=True)
PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Types autorisés
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

# 🆕 Types vidéo autorisés
ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime", # .mov
    "video/x-msvideo", # .avi
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024 # 50 MB (limite pour les vidéos)


# ============================================================
# IMAGES
# ============================================================

async def save_image(
    file: UploadFile,
    destination: Path = None,
    prefix: str = "img",
) -> str:
    """
    Sauvegarde une image.
    - Si CLOUDINARY_URL configuré → upload vers Cloudinary (URL HTTPS)
    - Sinon → sauvegarde locale
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type d'image non autorisé : {file.content_type}",
        )
    
    content = await file.read()
    
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image trop volumineuse (max 5 MB)",
        )
    
    # ============================
    # UPLOAD CLOUDINARY
    # ============================
    if USE_CLOUDINARY:
        try:
            result = cloudinary.uploader.upload(
                content,
                folder="finest-global/images",
                public_id=f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                resource_type="image",
            )
            return result["secure_url"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur upload Cloudinary : {str(e)}",
            )
    
    # ============================
    # UPLOAD LOCAL (dev)
    # ============================
    extension = Path(file.filename).suffix.lower() or ".jpg"
    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        extension = ".jpg"
    
    filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
    
    # Si pas de destination précisée, on utilise PRODUCTS_DIR par défaut
    dest = destination or PRODUCTS_DIR
    filepath = dest / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    return f"/{filepath.as_posix()}"


def delete_image(relative_path: str) -> None:
    """
    Supprime une image (Cloudinary ou local).
    """
    if not relative_path:
        return
    
    # Cloudinary (URL complète)
    if USE_CLOUDINARY and relative_path.startswith("http"):
        try:
            # Extraire le public_id depuis l'URL Cloudinary
            parts = relative_path.split("/upload/")[-1].split("/")
            filename = parts[-1].split(".")[0]
            folder = "/".join(parts[:-1])
            public_id = f"{folder}/{filename}" if folder else filename
            
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Erreur suppression Cloudinary (image) : {e}")
        return
    
    # Local
    path = Path(relative_path.lstrip("/"))
    if path.exists() and path.is_file():
        path.unlink()


# ============================================================
# 🆕 VIDÉOS
# ============================================================

async def save_video(
    file: UploadFile,
    destination: Path = None,
    prefix: str = "vid",
) -> str:
    """
    Sauvegarde une vidéo.
    - Si CLOUDINARY_URL configuré → upload vers Cloudinary (URL HTTPS)
    - Sinon → sauvegarde locale
    """
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de vidéo non autorisé : {file.content_type}. Formats acceptés : MP4, WEBM, MOV, AVI.",
        )
    
    content = await file.read()
    
    if len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vidéo trop volumineuse (max 50 MB)",
        )
    
    # ============================
    # UPLOAD CLOUDINARY
    # ============================
    if USE_CLOUDINARY:
        try:
            result = cloudinary.uploader.upload(
                content,
                folder="finest-global/videos",
                public_id=f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                resource_type="video", # Important pour Cloudinary
            )
            return result["secure_url"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur upload vidéo Cloudinary : {str(e)}",
            )
    
    # ============================
    # UPLOAD LOCAL (dev)
    # ============================
    extension = Path(file.filename).suffix.lower() or ".mp4"
    if extension not in [".mp4", ".webm", ".mov", ".avi"]:
        extension = ".mp4"
    
    filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
    
    # Si pas de destination précisée, on utilise VIDEOS_DIR
    dest = destination or VIDEOS_DIR
    filepath = dest / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    return f"/{filepath.as_posix()}"


def delete_video(relative_path: str) -> None:
    """
    Supprime une vidéo (Cloudinary ou local).
    """
    if not relative_path:
        return
    
    # Cloudinary (URL complète)
    if USE_CLOUDINARY and relative_path.startswith("http"):
        try:
            parts = relative_path.split("/upload/")[-1].split("/")
            filename = parts[-1].split(".")[0]
            folder = "/".join(parts[:-1])
            public_id = f"{folder}/{filename}" if folder else filename
            
            # Important : resource_type="video"
            cloudinary.uploader.destroy(public_id, resource_type="video")
        except Exception as e:
            print(f"Erreur suppression Cloudinary (vidéo) : {e}")
        return
    
    # Local
    path = Path(relative_path.lstrip("/"))
    if path.exists() and path.is_file():
        path.unlink()