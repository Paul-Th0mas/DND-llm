"""
Pydantic DTOs for the character_options bounded context.

These are input/output schemas for the API layer — they are not domain models
and must not contain business logic.
"""

import uuid

from pydantic import BaseModel

from app.character_options.domain.models import CharacterClass, CharacterSpecies


class CharacterClassResponse(BaseModel):
    """Response schema for a single character class."""

    id: uuid.UUID
    display_name: str
    chassis_name: str
    hit_die: int
    primary_ability: str
    spellcasting_ability: str | None

    @classmethod
    def from_domain(cls, obj: CharacterClass) -> "CharacterClassResponse":
        """Map a CharacterClass domain object to a response DTO."""
        return cls(
            id=obj.id,
            display_name=obj.display_name,
            chassis_name=obj.chassis_name,
            hit_die=obj.hit_die,
            primary_ability=obj.primary_ability,
            spellcasting_ability=obj.spellcasting_ability,
        )


class CharacterClassListResponse(BaseModel):
    """Envelope for a list of character classes."""

    classes: list[CharacterClassResponse]


class CharacterSpeciesResponse(BaseModel):
    """Response schema for a single character species."""

    id: uuid.UUID
    display_name: str
    archetype_key: str
    size: str
    speed: int
    traits: list[str]

    @classmethod
    def from_domain(cls, obj: CharacterSpecies) -> "CharacterSpeciesResponse":
        """Map a CharacterSpecies domain object to a response DTO."""
        return cls(
            id=obj.id,
            display_name=obj.display_name,
            archetype_key=obj.archetype_key,
            size=obj.size,
            speed=obj.speed,
            traits=list(obj.traits),
        )


class CharacterSpeciesListResponse(BaseModel):
    """Envelope for a list of character species."""

    species: list[CharacterSpeciesResponse]


# ---------------------------------------------------------------------------
# Skill proficiency response schemas (US-048)
# ---------------------------------------------------------------------------


class SkillOptionSchema(BaseModel):
    """A single selectable skill with its governing ability."""

    name: str
    ability: str


class ClassSkillProficienciesResponse(BaseModel):
    """Response for GET /character-options/classes/{class_id}/skill-proficiencies."""

    class_id: uuid.UUID
    selectable_skills: list[SkillOptionSchema]
    choose_count: int


# ---------------------------------------------------------------------------
# Starting equipment response schemas (US-049)
# ---------------------------------------------------------------------------


class ClassStartingEquipmentResponse(BaseModel):
    """Response for GET /character-options/classes/{class_id}/starting-equipment."""

    class_id: uuid.UUID
    items: list[str]


# ---------------------------------------------------------------------------
# Spell options response schemas (US-050)
# ---------------------------------------------------------------------------


class SpellEntrySchema(BaseModel):
    """A single spell within a spell section."""

    name: str
    description: str


class SpellSectionSchema(BaseModel):
    """A group of spells at a specific level available for selection."""

    level: int
    label: str
    choose_count: int
    spells: list[SpellEntrySchema]


class ClassSpellOptionsResponse(BaseModel):
    """Response for GET /character-options/classes/{class_id}/spells."""

    class_id: uuid.UUID
    spellcasting_ability: str | None
    sections: list[SpellSectionSchema]
