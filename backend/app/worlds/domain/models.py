"""
Domain models for the worlds bounded context.

Worlds are admin-seeded settings (lore, factions, bosses) that DMs select when
creating a campaign. They are static — not generated on demand.

No SQLAlchemy or FastAPI imports belong here. Pure Python domain logic only.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Theme(str, Enum):
    """The narrative genre of a world setting."""

    MEDIEVAL_FANTASY = "MEDIEVAL_FANTASY"
    CYBERPUNK = "CYBERPUNK"
    MANHWA = "MANHWA"
    POST_APOCALYPTIC = "POST_APOCALYPTIC"


# ---------------------------------------------------------------------------
# Value Objects (frozen dataclasses — immutable, identity-less)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PresetFaction:
    """
    A faction that exists within the world's lore.

    hidden_agenda is DM-only information — it must never be exposed to players
    via API responses. The repository loads it but the response schema omits it.
    """

    name: str
    description: str
    alignment: str
    public_reputation: str
    hidden_agenda: str


@dataclass(frozen=True)
class PresetBoss:
    """
    A named boss that inhabits the world.

    challenge_rating follows D&D notation (e.g. "CR 15"). abilities is an
    ordered tuple of notable skill or power names. lore is narrative context
    fed to the LLM during dungeon generation to maintain consistency.
    """

    name: str
    description: str
    challenge_rating: str
    abilities: tuple[str, ...]
    lore: str


# ---------------------------------------------------------------------------
# Aggregate Root
# ---------------------------------------------------------------------------


@dataclass
class World:
    """
    Aggregate root for the Worlds bounded context.

    Admin-created and seeded directly into the database. DMs browse and select
    a World when creating a Campaign. The world's lore, factions, and bosses
    are passed to the Dungeon narrator as generation context.

    is_active allows soft-deletion without breaking existing Campaign references.
    """

    id: uuid.UUID
    name: str
    theme: Theme
    description: str
    lore_summary: str
    factions: tuple[PresetFaction, ...]
    bosses: tuple[PresetBoss, ...]
    is_active: bool
    created_at: datetime

    def __post_init__(self) -> None:
        logger.debug(
            "World loaded: id=%s name='%s' theme=%s", self.id, self.name, self.theme
        )
