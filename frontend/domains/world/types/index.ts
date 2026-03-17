/**
 * Theme values as returned by GET /api/v1/worlds.
 * Maps to the Theme enum in the backend worlds domain.
 */
export type WorldTheme =
  | "MEDIEVAL_FANTASY"
  | "CYBERPUNK"
  | "MANHWA"
  | "POST_APOCALYPTIC";

/**
 * Summary of a pre-seeded world returned by GET /api/v1/worlds (list).
 * Used to populate the world picker in the campaign creation wizard.
 */
export interface WorldSummary {
  readonly world_id: string;
  readonly name: string;
  readonly theme: WorldTheme;
  readonly description: string;
}

/**
 * A faction that belongs to a pre-seeded world.
 * Returned inside WorldDetail.
 */
export interface PresetFaction {
  readonly name: string;
  readonly description: string;
  readonly alignment: string;
  readonly public_reputation: string;
}

/**
 * A boss that belongs to a pre-seeded world.
 * Returned inside WorldDetail.
 */
export interface PresetBoss {
  readonly name: string;
  readonly description: string;
  readonly challenge_rating: string;
  readonly abilities: readonly string[];
  readonly lore: string;
}

/**
 * Full detail for a pre-seeded world returned by GET /api/v1/worlds/{world_id}.
 * Includes lore, factions, and bosses for the DM world view page.
 */
export interface WorldDetail {
  readonly world_id: string;
  readonly name: string;
  readonly theme: WorldTheme;
  readonly description: string;
  readonly lore_summary: string;
  readonly factions: readonly PresetFaction[];
  readonly bosses: readonly PresetBoss[];
}

/**
 * Room type values as returned by the world generation endpoint.
 * Maps to the RoomType enum in the backend worlds domain.
 */
export type RoomType =
  | "BOSS"
  | "REST"
  | "SHOP"
  | "COMBAT"
  | "TREASURE"
  | "EVENT";

/**
 * A single narrated room returned inside GeneratedWorldResponse.
 * Contains LLM-generated narrative content for the room.
 */
export interface NarratedRoomResponse {
  readonly room_type: RoomType;
  readonly name: string;
  readonly description: string;
  readonly enemy_names: readonly string[];
  readonly npc_names: readonly string[];
  readonly special_notes: string;
}

/**
 * The main quest object returned inside GeneratedWorldResponse.
 */
export interface MainQuestResponse {
  readonly title: string;
  readonly description: string;
  readonly stages: readonly string[];
}

/**
 * Full response from POST /api/v1/worlds/generate.
 * Contains all LLM-generated world content.
 */
export interface GeneratedWorldResponse {
  readonly world_name: string;
  readonly description: string;
  readonly atmosphere: string;
  readonly theme: WorldTheme;
  readonly active_factions: readonly string[];
  readonly main_quest: MainQuestResponse;
  readonly rooms: readonly NarratedRoomResponse[];
}
