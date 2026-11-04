"""
Gestion des connexions WebSocket pour les notifications en temps réel.
Un vendeur se connecte à /ws/notifications avec son token JWT.
"""

from fastapi import WebSocket, WebSocketDisconnect, status
from typing import Dict, Set
from jose import JWTError, jwt
import json
from datetime import datetime

from auth import SECRET_KEY, ALGORITHM
from database import SessionLocal # 🆕 Pour sauvegarder en base
from models import Notification # 🆕


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"🔌 WebSocket connecté : user_id={user_id}")
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"🔌 WebSocket déconnecté : user_id={user_id}")
    
    async def send_to_user(self, user_id: int, message: dict):
        if user_id not in self.active_connections:
            return
        
        connections = list(self.active_connections[user_id])
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(user_id, websocket)
    
    async def broadcast(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await manager.connect(user_id, websocket)
    
    await websocket.send_json({
        "type": "connected",
        "message": "Connexion temps réel établie",
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        print(f"❌ Erreur WebSocket : {e}")
        manager.disconnect(user_id, websocket)


# ============================================================
# 🆕 FONCTION CENTRALE : SAUVEGARDER EN BASE PUIS ENVOYER
# ============================================================

async def send_and_save_notification(
    user_id: int, 
    title: str, 
    message: str, 
    notif_type: str, 
    link: str = None,
    extra_data: dict = None
):
    """
    Sauvegarde la notification en base de données (pour l'historique),
    puis l'envoie en temps réel via WebSocket (pour le pop-up).
    """
    db = SessionLocal()
    try:
        # 1. Sauvegarder en base
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            link=link,
            is_read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        # 2. Envoyer en temps réel
        payload = {
            "type": notif_type,
            "notification_id": notif.id,
            "title": title,
            "message": message,
            "link": link,
            "timestamp": notif.created_at.isoformat()
        }
        if extra_data:
            payload.update(extra_data)

        await manager.send_to_user(user_id, payload)
        
    except Exception as e:
        print(f"❌ Erreur notification : {e}")
        db.rollback()
    finally:
        db.close()


# ============================================================
# FONCTIONS UTILITAIRES (Mises à jour pour utiliser send_and_save)
# ============================================================

async def notify_new_order(seller_id: int, order_data: dict):
    """Notifie un vendeur qu'il a reçu une nouvelle commande."""
    await send_and_save_notification(
        user_id=seller_id,
        title="Nouvelle commande !",
        message=f"Vous avez reçu une commande pour : {order_data.get('product_name')}",
        notif_type="new_order",
        link=f"/dashboard-seller.html", # Lien vers le dashboard
        extra_data={"order": order_data}
    )


async def notify_order_status(buyer_id: int, order_id: int, new_status: str):
    """Notifie un client que sa commande a changé de statut."""
    await send_and_save_notification(
        user_id=buyer_id,
        title="Mise à jour de commande",
        message=f"Votre commande #{order_id} est maintenant : {new_status}",
        notif_type="order_status_changed",
        link=f"/orders.html", # Lien vers la page commandes du client
        extra_data={"order_id": order_id, "status": new_status}
    )