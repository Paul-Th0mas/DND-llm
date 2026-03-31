from fastapi import APIRouter

from app.users.api.router import auth_router, users_router
from app.rooms.api.router import rooms_router
from app.rooms.api.websocket import ws_router
from app.combat.api.router import combat_router
from app.worlds.api.router import worlds_router
from app.campaigns.api.router import campaigns_router
from app.dungeons.api.router import dungeons_router
from app.character_options.api.router import character_options_router
from app.characters.api.router import characters_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(rooms_router)
# WebSocket router has no prefix — the endpoint itself is /ws/{room_id}.
api_router.include_router(ws_router)
api_router.include_router(combat_router)
api_router.include_router(worlds_router, prefix="/worlds", tags=["worlds"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
# Dungeon routes use two URL shapes — no single prefix fits both, so the
# router declares its own full paths (/campaigns/{id}/dungeons and /dungeons/{id}).
api_router.include_router(dungeons_router, tags=["dungeons"])
api_router.include_router(
    character_options_router,
    prefix="/character-options",
    tags=["character-options"],
)
# Characters router declares its own full paths because it serves both
# /characters endpoints and /campaigns/{id}/characters endpoints.
api_router.include_router(characters_router, tags=["characters"])
