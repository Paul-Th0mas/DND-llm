"""
Pydantic DTOs for the dungeons bounded context.

These are Data Transfer Objects -- they live at the application layer boundary
between the API (HTTP) and the domain. They are NOT domain models.

Inbound:  GenerateDungeonRequest  -> converted to DungeonSettings domain value object
Outbound: DungeonCreatedResponse  <- summary after POST (creation)
          DungeonSummaryResponse  <- list item for GET /campaigns/{id}/dungeons
          DungeonDetailResponse   <- full detail for GET /dungeons/{id}
"""

import logging
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.rooms.domain.models import Room as RoomDomain
from app.dungeons.domain.models import (
    Dungeon,
    DungeonQuest,
    DungeonRoom,
    DungeonSettings,
    EffectType,
    EnemyData,
    GameEffect,
    LootItem,
    NpcData,
    QuestMetadata,
    RoomMechanics,
    TriggerData,
    PARTY_SIZE_MAX,
    PARTY_SIZE_MIN,
    ROOM_COUNT_MAX,
    ROOM_COUNT_MIN,
    RoomType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Inbound DTOs
# ---------------------------------------------------------------------------


class GenerateDungeonRequest(BaseModel):
    """
    Inbound DTO for POST /campaigns/{id}/dungeons.

    campaign_id is taken from the URL path, not the body.
    difficulty_override allows the DM to change encounter difficulty for
    this session without affecting the campaign settings.
    dm_notes are appended to the LLM prompt as free-text hints.
    """

    room_count: int = Field(default=8, ge=ROOM_COUNT_MIN, le=ROOM_COUNT_MAX)
    party_size: int = Field(default=4, ge=PARTY_SIZE_MIN, le=PARTY_SIZE_MAX)
    difficulty_override: str | None = None
    dm_notes: str | None = None

    def to_domain(self, campaign_id: uuid.UUID) -> DungeonSettings:
        """Convert this request DTO into a DungeonSettings value object."""
        logger.debug(
            "Converting GenerateDungeonRequest to domain: campaign_id=%s rooms=%d",
            campaign_id,
            self.room_count,
        )
        return DungeonSettings(
            campaign_id=campaign_id,
            room_count=self.room_count,
            party_size=self.party_size,
            difficulty_override=self.difficulty_override,
            dm_notes=self.dm_notes,
        )


# ---------------------------------------------------------------------------
# Structured outbound DTOs (US-063 to US-067)
# ---------------------------------------------------------------------------


class EnemyDataResponse(BaseModel):
    """Outbound DTO for structured enemy data on a room."""

    initial: list[str]
    reinforcements: list[str]
    trigger_condition: str | None = None
    environmental_hazards: str | None = None
    boss: str | None = None
    special_attacks: list[str]

    @classmethod
    def from_domain(cls, enemy: EnemyData) -> "EnemyDataResponse":
        """Convert an EnemyData value object into this response DTO."""
        return cls(
            initial=list(enemy.initial),
            reinforcements=list(enemy.reinforcements),
            trigger_condition=enemy.trigger_condition,
            environmental_hazards=enemy.environmental_hazards,
            boss=enemy.boss,
            special_attacks=list(enemy.special_attacks),
        )


class SkillCheckResponse(BaseModel):
    """Outbound DTO for a single skill check."""

    type: str
    dc: int
    on_success: str
    on_failure: str | None = None


class TriggerDataResponse(BaseModel):
    """Outbound DTO for the trigger condition of a game effect."""

    trigger_action: str
    check_stat: str | None = None
    dc: int | None = None

    @classmethod
    def from_domain(cls, trigger: TriggerData) -> "TriggerDataResponse":
        """Convert a TriggerData value object into this response DTO."""
        return cls(
            trigger_action=trigger.trigger_action,
            check_stat=trigger.check_stat,
            dc=trigger.dc,
        )


class GameEffectResponse(BaseModel):
    """Outbound DTO for a discrete game effect attached to a room."""

    effect_type: EffectType
    trigger: TriggerDataResponse
    value: int | None = None
    status: str | None = None
    item_id: str | None = None

    @classmethod
    def from_domain(cls, ge: GameEffect) -> "GameEffectResponse":
        """Convert a GameEffect value object into this response DTO."""
        return cls(
            effect_type=ge.effect_type,
            trigger=TriggerDataResponse.from_domain(ge.trigger),
            value=ge.value,
            status=ge.status,
            item_id=ge.item_id,
        )


class RoomMechanicsResponse(BaseModel):
    """Outbound DTO for structured room mechanics."""

    skill_checks: list[SkillCheckResponse]
    rest_benefit: str | None = None
    victory_items: list[str]
    game_effects: list[GameEffectResponse]

    @classmethod
    def from_domain(cls, mechanics: RoomMechanics) -> "RoomMechanicsResponse":
        """Convert a RoomMechanics value object into this response DTO."""
        return cls(
            skill_checks=[
                SkillCheckResponse(
                    type=sc.type,
                    dc=sc.dc,
                    on_success=sc.on_success,
                    on_failure=sc.on_failure,
                )
                for sc in mechanics.skill_checks
            ],
            rest_benefit=mechanics.rest_benefit,
            victory_items=list(mechanics.victory_items),
            game_effects=[
                GameEffectResponse.from_domain(ge) for ge in mechanics.game_effects
            ],
        )


class LootItemResponse(BaseModel):
    """Outbound DTO for a single loot table entry."""

    item: str
    quantity: int
    value: str | None = None
    rarity: str | None = None

    @classmethod
    def from_domain(cls, loot: LootItem) -> "LootItemResponse":
        """Convert a LootItem value object into this response DTO."""
        return cls(
            item=loot.item,
            quantity=loot.quantity,
            value=loot.value,
            rarity=loot.rarity,
        )


class NpcInventoryItemResponse(BaseModel):
    """Outbound DTO for a single NPC inventory item."""

    item: str
    price: int


class NpcDataResponse(BaseModel):
    """Outbound DTO for structured NPC data on a room."""

    name: str
    role: str
    inventory: list[NpcInventoryItemResponse]
    interaction_dc: dict[str, object] | None = None

    @classmethod
    def from_domain(cls, npc: NpcData) -> "NpcDataResponse":
        """Convert an NpcData value object into this response DTO."""
        return cls(
            name=npc.name,
            role=npc.role,
            inventory=[
                NpcInventoryItemResponse(item=inv.item, price=inv.price)
                for inv in npc.inventory
            ],
            interaction_dc=npc.interaction_dc,
        )


class QuestMetadataResponse(BaseModel):
    """Outbound DTO for session-wide quest metadata (US-063)."""

    name: str
    recommended_level: int
    environment: str
    global_modifiers: str

    @classmethod
    def from_domain(cls, qm: QuestMetadata) -> "QuestMetadataResponse":
        """Convert a QuestMetadata value object into this response DTO."""
        return cls(
            name=qm.name,
            recommended_level=qm.recommended_level,
            environment=qm.environment,
            global_modifiers=qm.global_modifiers,
        )


# ---------------------------------------------------------------------------
# Room and Quest outbound DTOs
# ---------------------------------------------------------------------------


class DungeonRoomResponse(BaseModel):
    """Outbound DTO for a single dungeon room."""

    index: int
    room_type: RoomType
    name: str
    description: str
    # Legacy flat fields kept for backward compatibility.
    enemy_names: list[str]
    npc_names: list[str]
    # Structured fields (US-063 to US-071).
    enemies: EnemyDataResponse | None = None
    mechanics: RoomMechanicsResponse | None = None
    loot_table: list[LootItemResponse] | None = None
    npc_data: list[NpcDataResponse] | None = None

    @classmethod
    def from_domain(cls, room: DungeonRoom) -> "DungeonRoomResponse":
        """Convert a DungeonRoom value object into this response DTO."""
        return cls(
            index=room.index,
            room_type=room.room_type,
            name=room.name,
            description=room.description,
            enemy_names=list(room.enemy_names),
            npc_names=list(room.npc_names),
            enemies=(
                EnemyDataResponse.from_domain(room.enemies)
                if room.enemies is not None
                else None
            ),
            mechanics=(
                RoomMechanicsResponse.from_domain(room.mechanics)
                if room.mechanics is not None
                else None
            ),
            loot_table=(
                [LootItemResponse.from_domain(li) for li in room.loot_table]
                if room.loot_table is not None
                else None
            ),
            npc_data=(
                [NpcDataResponse.from_domain(nd) for nd in room.npc_data]
                if room.npc_data is not None
                else None
            ),
        )


class DungeonQuestResponse(BaseModel):
    """Outbound DTO for the dungeon's quest."""

    name: str
    description: str
    stages: list[str]

    @classmethod
    def from_domain(cls, quest: DungeonQuest) -> "DungeonQuestResponse":
        """Convert a DungeonQuest value object into this response DTO."""
        return cls(
            name=quest.name,
            description=quest.description,
            stages=list(quest.stages),
        )


# ---------------------------------------------------------------------------
# Top-level outbound DTOs
# ---------------------------------------------------------------------------


class DungeonCreatedResponse(BaseModel):
    """
    Outbound DTO for POST /campaigns/{id}/dungeons.

    Returns a summary of the generated dungeon and the URL for room creation.
    """

    dungeon_id: uuid.UUID
    name: str
    premise: str
    room_count: int
    quest_name: str
    next_step: str

    @classmethod
    def from_domain(cls, dungeon: Dungeon) -> "DungeonCreatedResponse":
        """Convert a Dungeon aggregate into this creation response DTO."""
        logger.debug(
            "DungeonCreatedResponse.from_domain: id=%s name='%s'",
            dungeon.id,
            dungeon.name,
        )
        return cls(
            dungeon_id=dungeon.id,
            name=dungeon.name,
            premise=dungeon.premise,
            room_count=len(dungeon.rooms),
            quest_name=dungeon.quest.name,
            next_step="/api/v1/rooms",
        )


class RoomStatusResponse(BaseModel):
    """
    Embedded room status on a DungeonSummaryResponse.

    Present when a room has been created with this dungeon_id; null otherwise.
    Allows the frontend to show Active / Closed / No Room status on each
    dungeon list entry without a separate per-dungeon HTTP request.
    """

    room_id: uuid.UUID
    room_name: str
    is_active: bool


class DungeonSummaryResponse(BaseModel):
    """
    Outbound DTO for GET /campaigns/{id}/dungeons list.

    Returns enough detail to identify each dungeon session without loading
    the full room data. Includes the most recently created linked room's
    status so the frontend can render Active / Closed / No Room chips
    without additional API calls (US-014).
    """

    dungeon_id: uuid.UUID
    name: str
    premise: str
    room_count: int
    created_at: datetime
    # Null when no room has been created for this dungeon yet.
    room: RoomStatusResponse | None = None

    @classmethod
    def from_domain(
        cls,
        dungeon: Dungeon,
        *,
        room: RoomDomain | None = None,
    ) -> "DungeonSummaryResponse":
        """
        Convert a Dungeon aggregate into this summary response DTO.

        @param dungeon - The Dungeon aggregate to summarise.
        @param room    - The most recently linked Room, or None if no room exists.
        """
        room_status: RoomStatusResponse | None = None
        if room is not None:
            room_status = RoomStatusResponse(
                room_id=room.id,
                room_name=room.name,
                is_active=room.is_active,
            )
        return cls(
            dungeon_id=dungeon.id,
            name=dungeon.name,
            premise=dungeon.premise,
            room_count=len(dungeon.rooms),
            created_at=dungeon.created_at,
            room=room_status,
        )


class DungeonDetailResponse(BaseModel):
    """
    Full dungeon detail for GET /dungeons/{id}.

    Returns all rooms, quest stages, and metadata so the DM can review
    the generated content before starting a room.
    """

    dungeon_id: uuid.UUID
    campaign_id: uuid.UUID
    world_id: uuid.UUID
    name: str
    premise: str
    rooms: list[DungeonRoomResponse]
    quest: DungeonQuestResponse
    created_at: datetime
    quest_metadata: QuestMetadataResponse | None = None
    current_room_index: int = 0
    completed_stage_indices: list[int] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, dungeon: Dungeon) -> "DungeonDetailResponse":
        """Convert a Dungeon aggregate into this detailed response DTO."""
        logger.debug(
            "DungeonDetailResponse.from_domain: id=%s rooms=%d",
            dungeon.id,
            len(dungeon.rooms),
        )
        return cls(
            dungeon_id=dungeon.id,
            campaign_id=dungeon.campaign_id,
            world_id=dungeon.world_id,
            name=dungeon.name,
            premise=dungeon.premise,
            rooms=[DungeonRoomResponse.from_domain(r) for r in dungeon.rooms],
            quest=DungeonQuestResponse.from_domain(dungeon.quest),
            created_at=dungeon.created_at,
            quest_metadata=(
                QuestMetadataResponse.from_domain(dungeon.quest_metadata)
                if dungeon.quest_metadata is not None
                else None
            ),
            current_room_index=dungeon.current_room_index,
            completed_stage_indices=list(dungeon.completed_stage_indices),
        )
