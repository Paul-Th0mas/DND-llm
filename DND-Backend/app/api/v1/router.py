from fastapi import APIRouter

from app.users.api.router import auth_router, users_router
from app.rooms.api.router import rooms_router
from app.rooms.api.websocket import ws_router
from app.combat.api.router import combat_router
from app.worlds.api.router import worlds_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(rooms_router)
# WebSocket router has no prefix — the endpoint itself is /ws/{room_id}.
api_router.include_router(ws_router)
api_router.include_router(combat_router)
api_router.include_router(worlds_router)
