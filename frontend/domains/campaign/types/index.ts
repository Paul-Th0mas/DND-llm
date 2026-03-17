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

/** Level range for the campaign arc. start must be <= end. */
export interface LevelRange {
  readonly start: number;
  readonly end: number;
}

/**
 * Safety tool content boundaries.
 * Lines are hard limits — content that will never appear in the game.
 */
export interface ContentBoundaries {
  readonly lines: readonly string[];
}

/**
 * Request body for POST /api/v1/campaigns.
 * Captures all DM requirements for a new campaign.
 * world_id must reference an existing active world from GET /api/v1/worlds.
 */
export interface CreateCampaignRequest {
  readonly campaign_name: string;
  readonly edition: string;
  readonly tone: CampaignTone;
  readonly player_count: number;
  readonly level_range: LevelRange;
  /** UUID of the pre-seeded world this campaign is set in. Required. */
  readonly world_id: string;
  readonly themes: readonly string[];
  readonly content_boundaries: ContentBoundaries;
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

/**
 * Summary response item from GET /api/v1/campaigns.
 * Used to populate the campaign list view.
 * Extended (US-018) to include world_name and dungeon_count so the hub
 * can render cards without extra round-trips.
 */
export interface CampaignSummary {
  readonly campaign_id: string;
  readonly name: string;
  readonly tone: string;
  readonly player_count: number;
  readonly world_id: string;
  /** Name of the world linked to this campaign. Null if the world was deleted. */
  readonly world_name: string | null;
  /** Number of dungeons generated for this campaign. */
  readonly dungeon_count: number;
  readonly created_at: string;
}

/**
 * Full detail response from GET /api/v1/campaigns/{id}.
 * Used to populate the campaign detail and world view pages.
 */
export interface CampaignDetail {
  readonly campaign_id: string;
  readonly name: string;
  readonly edition: string;
  readonly tone: string;
  readonly player_count: number;
  readonly level_range: LevelRange;
  readonly themes: readonly string[];
  readonly content_boundaries: ContentBoundaries;
  readonly dm_id: string;
  readonly world_id: string;
  readonly created_at: string;
}

/**
 * Starting settlement data returned inside CampaignWorldDetailResponse.
 */
export interface StartingSettlement {
  readonly name: string;
  readonly population: string;
  readonly governance: string;
  readonly description: string;
}

/**
 * A faction returned inside CampaignWorldDetailResponse.
 * Includes DM-only hidden agenda not visible to players.
 */
export interface CampaignFaction {
  readonly name: string;
  readonly goals: string;
  readonly public_reputation: string;
  readonly hidden_agenda: string;
}

/**
 * A key NPC returned inside CampaignWorldDetailResponse.
 * Includes DM-only secret not visible to players.
 */
export interface CampaignNPC {
  readonly name: string;
  readonly species: string;
  readonly role: string;
  readonly personality: string;
  readonly secret: string;
  readonly stat_block_ref: string;
}

/**
 * An adventure hook returned inside CampaignWorldDetailResponse.
 * Grouped by narrative pillar (combat, exploration, or social).
 */
export interface AdventureHook {
  readonly pillar: "combat" | "exploration" | "social";
  readonly hook: string;
  readonly connected_npc: string;
}

/**
 * Full response from POST /api/v1/campaigns/{id}/world/generate.
 * Contains all LLM-generated campaign world content.
 */
export interface CampaignWorldDetailResponse {
  readonly world_id: string;
  readonly world_name: string;
  readonly premise: string;
  readonly starting_settlement: StartingSettlement;
  readonly factions: readonly CampaignFaction[];
  readonly key_npcs: readonly CampaignNPC[];
  readonly adventure_hooks: readonly AdventureHook[];
  readonly central_conflict: string;
}
