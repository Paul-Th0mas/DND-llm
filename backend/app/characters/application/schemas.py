"""
Pydantic DTOs for the characters bounded context.

These are input/output schemas for the API layer — not domain models.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.characters.domain.models import (
    CHARACTER_BACKGROUND_MAX_LEN,
    CHARACTER_NAME_MAX_LEN,
    AbilityScores,
    Character,
)
from app.character_options.domain.models import CharacterClass, CharacterSpecies


# ---------------------------------------------------------------------------
# Nested response schemas
# ---------------------------------------------------------------------------


class AbilityScoresSchema(BaseModel):
    """Six D&D ability scores."""

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class ClassDetailSchema(BaseModel):
    """Class detail embedded in a character sheet response."""

    id: uuid.UUID
    display_name: str
    hit_die: int
    primary_ability: str
    spellcasting_ability: str | None


class SpeciesDetailSchema(BaseModel):
    """Species detail embedded in a character sheet response."""

    id: uuid.UUID
    display_name: str
    size: str
    speed: int
    traits: list[str]


class PlayerSummarySchema(BaseModel):
    """Owning player info embedded in the DM roster response."""

    id: uuid.UUID
    username: str


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class AbilityScoresRequest(BaseModel):
    """Ability scores as submitted in the character creation request."""

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    def to_domain(self) -> AbilityScores:
        """Convert this DTO to the domain value object."""
        return AbilityScores(
            strength=self.strength,
            dexterity=self.dexterity,
            constitution=self.constitution,
            intelligence=self.intelligence,
            wisdom=self.wisdom,
            charisma=self.charisma,
        )


class CreateCharacterRequest(BaseModel):
    """Request body for POST /characters."""

    name: str = Field(..., min_length=1, max_length=CHARACTER_NAME_MAX_LEN)
    class_id: uuid.UUID
    species_id: uuid.UUID
    world_id: uuid.UUID
    ability_scores: AbilityScoresRequest
    background: str = Field(..., max_length=CHARACTER_BACKGROUND_MAX_LEN)
    skill_proficiencies: list[str] = Field(default_factory=list)
    starting_equipment: list[str] = Field(default_factory=list)
    spells: list[str] = Field(default_factory=list)


class LinkCharacterRequest(BaseModel):
    """Request body for POST /campaigns/{campaign_id}/characters."""

    character_id: uuid.UUID


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class CharacterResponse(BaseModel):
    """Response for POST /characters (201) — minimal summary after creation."""

    id: uuid.UUID
    name: str
    class_id: uuid.UUID
    species_id: uuid.UUID
    world_id: uuid.UUID
    owner_id: uuid.UUID
    ability_scores: AbilityScoresSchema
    background: str
    created_at: datetime
    skill_proficiencies: list[str]
    starting_equipment: list[str]
    spells: list[str]

    @classmethod
    def from_domain(cls, character: Character) -> "CharacterResponse":
        """Map a Character domain aggregate to a creation response DTO."""
        scores = character.ability_scores
        return cls(
            id=character.id,
            name=character.name,
            class_id=character.class_id,
            species_id=character.species_id,
            world_id=character.world_id,
            owner_id=character.owner_id,
            ability_scores=AbilityScoresSchema(
                strength=scores.strength,
                dexterity=scores.dexterity,
                constitution=scores.constitution,
                intelligence=scores.intelligence,
                wisdom=scores.wisdom,
                charisma=scores.charisma,
            ),
            background=character.background,
            created_at=character.created_at,
            skill_proficiencies=character.skill_proficiencies,
            starting_equipment=character.starting_equipment,
            spells=character.spells,
        )


class CharacterSheetResponse(BaseModel):
    """
    Full character sheet response for GET /characters/{character_id}.

    Includes resolved class and species detail objects.
    """

    id: uuid.UUID
    name: str
    background: str
    ability_scores: AbilityScoresSchema
    character_class: ClassDetailSchema
    species: SpeciesDetailSchema
    world_id: uuid.UUID
    campaign_id: uuid.UUID | None
    created_at: datetime
    skill_proficiencies: list[str]
    starting_equipment: list[str]
    spells: list[str]

    @classmethod
    def from_domain(
        cls,
        character: Character,
        character_class: CharacterClass,
        species: CharacterSpecies,
    ) -> "CharacterSheetResponse":
        """Map a Character with resolved class/species to a sheet DTO."""
        scores = character.ability_scores
        return cls(
            id=character.id,
            name=character.name,
            background=character.background,
            ability_scores=AbilityScoresSchema(
                strength=scores.strength,
                dexterity=scores.dexterity,
                constitution=scores.constitution,
                intelligence=scores.intelligence,
                wisdom=scores.wisdom,
                charisma=scores.charisma,
            ),
            character_class=ClassDetailSchema(
                id=character_class.id,
                display_name=character_class.display_name,
                hit_die=character_class.hit_die,
                primary_ability=character_class.primary_ability,
                spellcasting_ability=character_class.spellcasting_ability,
            ),
            species=SpeciesDetailSchema(
                id=species.id,
                display_name=species.display_name,
                size=species.size,
                speed=species.speed,
                traits=list(species.traits),
            ),
            world_id=character.world_id,
            campaign_id=character.campaign_id,
            created_at=character.created_at,
            skill_proficiencies=character.skill_proficiencies,
            starting_equipment=character.starting_equipment,
            spells=character.spells,
        )


class CharacterRosterEntry(BaseModel):
    """
    Single entry in the DM campaign roster (GET /campaigns/{id}/characters).

    Includes resolved class, species, and player username.
    """

    id: uuid.UUID
    name: str
    background: str
    ability_scores: AbilityScoresSchema
    character_class: ClassDetailSchema
    species: SpeciesDetailSchema
    player: PlayerSummarySchema

    @classmethod
    def from_domain(
        cls,
        character: Character,
        character_class: CharacterClass,
        species: CharacterSpecies,
        player_id: uuid.UUID,
        player_username: str,
    ) -> "CharacterRosterEntry":
        """Map a Character with resolved class/species/player to a roster DTO."""
        scores = character.ability_scores
        return cls(
            id=character.id,
            name=character.name,
            background=character.background,
            ability_scores=AbilityScoresSchema(
                strength=scores.strength,
                dexterity=scores.dexterity,
                constitution=scores.constitution,
                intelligence=scores.intelligence,
                wisdom=scores.wisdom,
                charisma=scores.charisma,
            ),
            character_class=ClassDetailSchema(
                id=character_class.id,
                display_name=character_class.display_name,
                hit_die=character_class.hit_die,
                primary_ability=character_class.primary_ability,
                spellcasting_ability=character_class.spellcasting_ability,
            ),
            species=SpeciesDetailSchema(
                id=species.id,
                display_name=species.display_name,
                size=species.size,
                speed=species.speed,
                traits=list(species.traits),
            ),
            player=PlayerSummarySchema(id=player_id, username=player_username),
        )


class CampaignRosterResponse(BaseModel):
    """Envelope for GET /campaigns/{campaign_id}/characters."""

    characters: list[CharacterRosterEntry]


class LinkCharacterResponse(BaseModel):
    """Response for POST /campaigns/{campaign_id}/characters (201)."""

    campaign_id: uuid.UUID
    character_id: uuid.UUID
    player_id: uuid.UUID
    linked_at: datetime


class CharacterSummaryResponse(BaseModel):
    """
    Summary response for GET /characters (US-046).

    world_name, class_name, and species_name are resolved by the use case and
    may be None if the referenced records have been deleted.
    """

    id: uuid.UUID
    name: str
    world_id: uuid.UUID
    world_name: str | None
    class_name: str | None
    species_name: str | None
    created_at: datetime


class ListMyCharactersResponse(BaseModel):
    """Envelope for GET /characters."""

    characters: list[CharacterSummaryResponse]
