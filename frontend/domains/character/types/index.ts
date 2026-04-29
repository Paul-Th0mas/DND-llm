/**
 * Score method chosen by the player during character creation.
 */
export type ScoreMethod = "standard_array" | "point_buy";

/**
 * The six D&D ability score keys.
 */
export type AbilityKey =
  | "strength"
  | "dexterity"
  | "constitution"
  | "intelligence"
  | "wisdom"
  | "charisma";

/**
 * All six ability scores as a record.
 */
export interface AbilityScores {
  readonly strength: number;
  readonly dexterity: number;
  readonly constitution: number;
  readonly intelligence: number;
  readonly wisdom: number;
  readonly charisma: number;
}

/**
 * A playable character class as returned by
 * GET /api/v1/character-options/classes?theme={theme}.
 */
export interface CharacterClass {
  readonly id: string;
  readonly display_name: string;
  readonly chassis_name: string;
  readonly hit_die: number;
  readonly primary_ability: string;
  readonly spellcasting_ability: string | null;
}

/**
 * Response envelope for GET /api/v1/character-options/classes.
 */
export interface CharacterClassListResponse {
  readonly classes: readonly CharacterClass[];
}

/**
 * A playable species as returned by
 * GET /api/v1/character-options/species?theme={theme}.
 */
export interface CharacterSpecies {
  readonly id: string;
  readonly display_name: string;
  readonly archetype_key: string;
  readonly size: string;
  readonly speed: number;
  readonly traits: readonly string[];
}

/**
 * Response envelope for GET /api/v1/character-options/species.
 */
export interface CharacterSpeciesListResponse {
  readonly species: readonly CharacterSpecies[];
}

/**
 * Class detail embedded inside a character sheet response.
 */
export interface ClassDetail {
  readonly id: string;
  readonly display_name: string;
  readonly hit_die: number;
  readonly primary_ability: string;
  readonly spellcasting_ability: string | null;
}

/**
 * Species detail embedded inside a character sheet response.
 */
export interface SpeciesDetail {
  readonly id: string;
  readonly display_name: string;
  readonly size: string;
  readonly speed: number;
  readonly traits: readonly string[];
}

/**
 * Full character sheet as returned by GET /api/v1/characters/{character_id}.
 */
export interface CharacterSheet {
  readonly id: string;
  readonly name: string;
  readonly background: string;
  readonly ability_scores: AbilityScores;
  readonly character_class: ClassDetail;
  readonly species: SpeciesDetail;
  readonly world_id: string;
  readonly campaign_id: string | null;
  readonly created_at: string;
}

/**
 * Response from POST /api/v1/characters (201).
 */
export interface CharacterCreatedResponse {
  readonly id: string;
  readonly name: string;
  readonly class_id: string;
  readonly species_id: string;
  readonly world_id: string;
  readonly owner_id: string;
  readonly ability_scores: AbilityScores;
  readonly background: string;
  readonly created_at: string;
}

/**
 * Character summary as returned by GET /api/v1/characters (list my characters).
 * Used in the "My Characters" dashboard tab (US-047).
 */
export interface CharacterSummary {
  readonly id: string;
  readonly name: string;
  readonly world_id: string;
  readonly world_name: string | null;
  readonly class_name: string | null;
  readonly species_name: string | null;
  readonly created_at: string;
}

/**
 * Response envelope for GET /api/v1/characters.
 */
export interface ListMyCharactersResponse {
  readonly characters: readonly CharacterSummary[];
}

/**
 * Request body for POST /api/v1/characters.
 */
export interface CreateCharacterRequest {
  readonly name: string;
  readonly class_id: string;
  readonly species_id: string;
  readonly world_id: string;
  readonly ability_scores: AbilityScores;
  readonly background: string;
  readonly skill_proficiencies: readonly string[];
  readonly starting_equipment: readonly string[];
  readonly spells: readonly string[];
}

/**
 * Request body for POST /api/v1/campaigns/{campaignId}/characters.
 */
export interface LinkCharacterRequest {
  readonly character_id: string;
}

/**
 * Response from POST /api/v1/campaigns/{campaignId}/characters (201).
 */
export interface LinkCharacterResponse {
  readonly campaign_id: string;
  readonly character_id: string;
  readonly player_id: string;
  readonly linked_at: string;
}

/**
 * Player summary embedded inside a roster entry.
 */
export interface PlayerSummary {
  readonly id: string;
  readonly username: string;
}

/**
 * Single character entry in the DM campaign roster.
 * Returned by GET /api/v1/campaigns/{campaignId}/characters.
 */
export interface CampaignRosterEntry {
  readonly id: string;
  readonly name: string;
  readonly background: string;
  readonly ability_scores: AbilityScores;
  readonly character_class: ClassDetail;
  readonly species: SpeciesDetail;
  readonly player: PlayerSummary;
}

/**
 * Response envelope for GET /api/v1/campaigns/{campaignId}/characters.
 */
export interface CampaignRosterResponse {
  readonly characters: readonly CampaignRosterEntry[];
}

/**
 * Wizard step state stored in the Zustand character store.
 * Tracks which step the player is on and what they have filled in so far.
 */
export interface CharacterWizardState {
  /** Current step index (0-based). 0=Name+Background, 1=Class, 2=Species, 3=Ability Scores. */
  readonly step: number;
  readonly name: string;
  readonly background: string;
  readonly selectedClassId: string | null;
  readonly selectedSpeciesId: string | null;
  readonly abilityScores: AbilityScores | null;
  readonly scoreMethod: ScoreMethod;
}
