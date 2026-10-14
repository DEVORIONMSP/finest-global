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


class ConnectionManager:
    """
    Gère les connexions WebSocket actives.
    Structure : { user_id: {websocket1, websocket2, ...} }
    Un utilisateur peut avoir plusieurs onglets ouverts.
    """
    
    def __init__(self):
        # { user_id: set(WebSocket) }
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        """Accepte une connexion et l'enregistre."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"🔌 WebSocket connecté : user_id={user_id} "
              f"(total: {len(self.active_connections[user_id])} onglets)")
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        """Retire une connexion."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"🔌 WebSocket déconnecté : user_id={user_id}")
    
    async def send_to_user(self, user_id: int, message: dict):
        """
        Envoie un message à toutes les connexions d'un utilisateur.
        """
        if user_id not in self.active_connections:
            return  # utilisateur pas connecté
        
        # Copier pour éviter les mutations pendant l'itération
        connections = list(self.active_connections[user_id])
        
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                # Connexion morte → nettoyer
                self.disconnect(user_id, websocket)
    
    async def broadcast(self, message: dict):
        """Envoie un message à tous les utilisateurs connectés."""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)


# Instance globale
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    Endpoint WebSocket : /ws/notifications?token=JWT
    
    Le token doit être passé en query string car les WebSockets
    ne supportent pas facilement les headers Authorization côté navigateur.
    """
    # Vérifier le token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Enregistrer la connexion
    await manager.connect(user_id, websocket)
    
    # Envoyer un message de bienvenue
    await websocket.send_json({
        "type": "connected",
        "message": "Connexion temps réel établie",
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    try:
        # Boucle : garder la connexion ouverte
        while True:
            # Recevoir des messages du client (ex: ping)
            data = await websocket.receive_text()
            
            # Répondre aux pings
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
# FONCTIONS UTILITAIRES POUR ENVOYER DES NOTIFICATIONS
# ============================================================

async def notify_new_order(seller_id: int, order_data: dict):
    """Notifie un vendeur qu'il a reçu une nouvelle commande."""
    await manager.send_to_user(seller_id, {
        "type": "new_order",
        "message": "Nouvelle commande reçue !",
        "order": order_data,
        "timestamp": datetime.utcnow().isoformat(),
    })


async def notify_order_status(buyer_id: int, order_id: int, new_status: str):
    """Notifie un client que sa commande a changé de statut."""
    await manager.send_to_user(buyer_id, {
        "type": "order_status_changed",
        "message": f"Votre commande #{order_id} est maintenant : {new_status}",
        "order_id": order_id,
        "status": new_status,
        "timestamp": datetime.utcnow().isoformat(),
    })