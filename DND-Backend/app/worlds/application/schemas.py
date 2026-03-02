"""
Pydantic DTOs (Data Transfer Objects) for the worlds bounded context.

These live in the application layer and are separate from both ORM models
and domain models. A request schema is never an ORM model.
"""

import uuid
from typing import Any

from pydantic import BaseModel

from app.worlds.domain.models import ThemeName


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CompileWorldRequest(BaseModel):
    """Body for POST /worlds/compile."""

    room_id: uuid.UUID
    theme: ThemeName
    difficulty: str = "normal"
    seed: int | None = None


class NarrateRoomRequest(BaseModel):
    """Body for POST /worlds/{world_id}/rooms/{n}/narrate."""

    world_id: uuid.UUID
    room_number: int
    # Caller supplies current game state: player HP, gold, narrative flags, etc.
    game_state: dict[str, Any]


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class EnemyPresetResponse(BaseModel):
    """Minimal enemy stat-block safe to expose via the API."""

    id: str
    name: str
    hp: int
    die_type: str
    pool_size: int
    ai_behavior: str
    lore_tags: list[str]


class NPCPresetResponse(BaseModel):
    id: str
    name: str
    role: str
    speech_style: str


class DungeonRoomResponse(BaseModel):
    """Full room detail returned by GET /worlds/{id}/rooms/{n}."""

    room_number: int
    room_type: str
    enemies: list[EnemyPresetResponse]
    npc: NPCPresetResponse | None
    lore_seed: str
    is_boss_room: bool


class WorldSkeletonResponse(BaseModel):
    """High-level world overview returned by POST /worlds/compile and GET /worlds/{id}."""

    id: uuid.UUID
    theme: str
    difficulty: str
    room_count: int
    active_quests: list[str]  # quest names — full quest detail is not exposed here


class NarrateRoomResponse(BaseModel):
    """Narrative text returned by POST /worlds/{id}/rooms/{n}/narrate."""

    description: str
    ambient_detail: str
    threat_level: str
    cached: bool
