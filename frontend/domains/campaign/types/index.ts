/**
 * TypeScript types for the campaign domain.
 * Values must match the enums and schemas in app/campaigns/ on the backend.
 */

/**
 * Emotional register and narrative style of the campaign.
 * Maps to CampaignTone enum in the backend.
 */
export type CampaignTone =
  | "dark_fantasy"
  | "high_fantasy"
  | "horror"
  | "political_intrigue"
  | "swashbuckling";

/**
 * Published world or homebrew setting the campaign uses.
 * Maps to SettingPreference enum in the backend.
 */
export type SettingPreference =
  | "homebrew"
  | "forgotten_realms"
  | "eberron"
  | "ravenloft"
  | "greyhawk";

/** Level range for the campaign arc. start must be <= end. */
export interface LevelRange {
  readonly start: number;
  readonly end: number;
}

/**
 * Safety tool content boundaries.
 * Lines are never generated; Veils are referenced but not described.
 */
export interface ContentBoundaries {
  readonly lines: readonly string[];
  readonly veils: readonly string[];
}

/**
 * Request body for POST /api/v1/campaigns.
 * Captures all DM requirements for a new campaign.
 */
export interface CreateCampaignRequest {
  readonly campaign_name: string;
  readonly edition: string;
  readonly tone: CampaignTone;
  readonly player_count: number;
  readonly level_range: LevelRange;
  readonly session_count_estimate: number;
  readonly setting_preference: SettingPreference;
  readonly themes: readonly string[];
  readonly content_boundaries: ContentBoundaries;
  readonly homebrew_rules: readonly string[];
  readonly inspirations: string | null;
}

/**
 * Response from POST /api/v1/campaigns.
 * Returns the campaign ID and the URL for the next pipeline step.
 */
export interface CampaignResponse {
  readonly campaign_id: string;
  readonly status: string;
  readonly next_step: string;
}

/** Starting settlement within a generated campaign world. */
export interface SettlementResponse {
  readonly name: string;
  readonly population: number;
  readonly governance: string;
  readonly description: string;
}

/** A single faction in the campaign world. hidden_agenda is DM-only. */
export interface FactionResponse {
  readonly name: string;
  readonly goals: string;
  readonly public_reputation: string;
  /** Not shown to players — DM toggle controls visibility in the UI. */
  readonly hidden_agenda: string;
}

/** A key NPC in the campaign world. secret is DM-only. */
export interface NpcResponse {
  readonly name: string;
  readonly species: string;
  readonly role: string;
  readonly personality: string;
  /** Not shown to players — DM toggle controls visibility in the UI. */
  readonly secret: string;
  readonly stat_block_ref: string | null;
}

/** A single adventure hook, grouped by narrative pillar. */
export interface AdventureHookResponse {
  /** One of: COMBAT, EXPLORATION, SOCIAL. */
  readonly pillar: string;
  readonly hook: string;
  readonly connected_npc: string | null;
}

/**
 * Full detail response for a generated campaign world.
 * Used to populate CampaignWorldView — includes DM-only fields.
 */
export interface CampaignWorldDetailResponse {
  readonly world_id: string;
  readonly world_name: string;
  readonly premise: string;
  readonly starting_settlement: SettlementResponse;
  readonly factions: readonly FactionResponse[];
  readonly key_npcs: readonly NpcResponse[];
  readonly adventure_hooks: readonly AdventureHookResponse[];
  readonly central_conflict: string;
}

/**
 * Response from POST /api/v1/campaigns/{id}/world.
 * Summary of the generated world — full NPC/faction data is DM-side only.
 */
export interface GenerateCampaignWorldResponse {
  readonly world_id: string;
  readonly world_name: string;
  readonly premise: string;
  readonly starting_settlement: SettlementResponse;
  readonly npcs_generated: number;
  readonly factions_generated: number;
  readonly hooks_generated: number;
}
