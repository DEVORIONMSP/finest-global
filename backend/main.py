"""
Point d'entrée FastAPI.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database import engine, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finest Global API",
    description="API backend pour la marketplace Finest Global",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fichiers statiques (uploads)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
from routers import (
    users, shops, products, orders, search, admin, tracking,
    categories, admin_categories,
)

app.include_router(users.router)
app.include_router(shops.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(search.router)
app.include_router(admin.router)
app.include_router(tracking.router)
app.include_router(categories.router)
app.include_router(admin_categories.router)

# ============================================================
# WEBSOCKET TEMPS RÉEL
# ============================================================

@app.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket, token: str = None):
    """
    Endpoint WebSocket : ws://127.0.0.1:8000/ws/notifications?token=JWT
    """
    await websocket_endpoint(websocket, token)


@app.get("/")
def root():
    return {
        "name": "Finest Global API",
        "status": "online",
        "docs": "/docs",
        "websocket": "/ws/notifications?token=JWT",
    }