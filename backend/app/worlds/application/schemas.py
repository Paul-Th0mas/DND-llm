"""
Pydantic DTOs for the worlds bounded context.

These are Data Transfer Objects — they live at the application layer boundary
between the API (HTTP) and the domain. They are NOT domain models.

Inbound:  WorldSettingsRequest  → converted to WorldSettings domain object
Outbound: GeneratedWorldResponse ← converted from GeneratedWorld domain object
"""

import logging

from pydantic import BaseModel, Field

from app.worlds.domain.models import (
    Difficulty,
    GeneratedWorld,
    MainQuest,
    NarratedRoom,
    QuestFocus,
    ROOM_COUNT_MAX,
    ROOM_COUNT_MIN,
    RoomType,
    Theme,
    WorldSettings,
)

logger = logging.getLogger(__name__)


class WorldOptionsResponse(BaseModel):
    """
    Outbound DTO for GET /worlds/options.

    Returns all valid enum values for world generation settings so the
    frontend can populate dropdowns dynamically without hardcoding them.
    Also exposes the room_count bounds so the frontend slider stays in sync.
    """

    themes: list[str]
    difficulties: list[str]
    quest_focuses: list[str]
    room_types: list[str]
    room_count_min: int
    room_count_max: int

    @classmethod
    def from_domain(cls, theme: Theme | None = None) -> "WorldOptionsResponse":
        """
        Build the response from the domain enums and constants.

        theme is accepted for future theme-specific filtering. Currently all
        enum values are valid regardless of theme. When filtering is needed,
        replace the list comprehensions with a domain mapping such as
        THEME_QUEST_FOCUS_MAP[theme] defined in domain/models.py.
        """
        logger.debug("Building WorldOptionsResponse: theme_filter=%s", theme)
        return cls(
            themes=[t.value for t in Theme],
            difficulties=[d.value for d in Difficulty],
            quest_focuses=[q.value for q in QuestFocus],
            room_types=[r.value for r in RoomType],
            room_count_min=ROOM_COUNT_MIN,
            room_count_max=ROOM_COUNT_MAX,
        )


class WorldSettingsRequest(BaseModel):
    """
    Inbound DTO for POST /worlds/generate.

    Pydantic validates field types and the ge/le constraints on room_count
    and party_size. Domain-level rules (e.g. business meaning of room_count
    bounds) are enforced by WorldSettings.validate() after to_domain() is called.
    """

    theme: Theme
    difficulty: Difficulty
    room_count: int = Field(default=10, ge=5, le=15)
    quest_focus: QuestFocus
    dm_notes: str | None = None
    party_size: int = Field(default=1, ge=1, le=6)

    def to_domain(self) -> WorldSettings:
        """Convert this request DTO into a domain value object."""
        logger.debug(
            "Converting WorldSettingsRequest to domain: theme=%s rooms=%d",
            self.theme,
            self.room_count,
        )
        return WorldSettings(
            theme=self.theme,
            difficulty=self.difficulty,
            room_count=self.room_count,
            quest_focus=self.quest_focus,
            dm_notes=self.dm_notes,
            party_size=self.party_size,
        )


class NarratedRoomResponse(BaseModel):
    """Output DTO representing a single room in the generated world."""

    index: int
    room_type: RoomType
    name: str
    description: str
    enemy_names: list[str]
    npc_names: list[str]
    special_notes: str | None = None

    @classmethod
    def from_domain(cls, room: NarratedRoom) -> "NarratedRoomResponse":
        """Convert a NarratedRoom domain value object into this response DTO."""
        return cls(
            index=room.index,
            room_type=room.room_type,
            name=room.name,
            description=room.description,
            enemy_names=list(room.enemy_names),
            npc_names=list(room.npc_names),
            special_notes=room.special_notes,
        )


class MainQuestResponse(BaseModel):
    """Output DTO representing the generated main quest."""

    name: str
    description: str
    stages: list[str]

    @classmethod
    def from_domain(cls, quest: MainQuest) -> "MainQuestResponse":
        """Convert a MainQuest domain value object into this response DTO."""
        return cls(
            name=quest.name,
            description=quest.description,
            stages=list(quest.stages),
        )


class GeneratedWorldResponse(BaseModel):
    """
    Full outbound response for POST /worlds/generate.

    Returned to the DM after successful world generation.
    """

    world_name: str
    world_description: str
    atmosphere: str
    theme: Theme
    rooms: list[NarratedRoomResponse]
    main_quest: MainQuestResponse
    active_factions: list[str]

    @classmethod
    def from_domain(cls, world: GeneratedWorld) -> "GeneratedWorldResponse":
        """Convert a GeneratedWorld aggregate into this response DTO."""
        logger.debug(
            "Converting GeneratedWorld to response DTO: name=%s rooms=%d",
            world.world_name,
            len(world.rooms),
        )
        return cls(
            world_name=world.world_name,
            world_description=world.world_description,
            atmosphere=world.atmosphere,
            theme=world.theme,
            rooms=[NarratedRoomResponse.from_domain(r) for r in world.rooms],
            main_quest=MainQuestResponse.from_domain(world.main_quest),
            active_factions=list(world.active_factions),
        )
