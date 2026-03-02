"""
Domain events for the worlds bounded context.

Events represent something meaningful that happened in the domain.
They are frozen dataclasses (value objects) — no identity, just data.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime

from app.worlds.domain.models import ThemeName


@dataclass(frozen=True)
class WorldCompiled:
    """
    Raised after a WorldSkeleton is successfully compiled and persisted.

    Downstream handlers (e.g. a WebSocket broadcaster) can subscribe to
    this event to notify players that the world is ready to enter.
    """

    world_id: uuid.UUID
    room_id: uuid.UUID
    theme: ThemeName
    room_count: int
    occurred_at: datetime
