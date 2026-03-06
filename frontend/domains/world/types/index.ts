/**
 * Narrative setting options for a generated world.
 * Values must match the Theme enum in the backend worlds domain.
 * This will be replaced with an API-driven select list in a later iteration.
 */
export type Theme =
  | "MEDIEVAL_FANTASY"
  | "CYBERPUNK"
  | "MANHWA"
  | "POST_APOCALYPTIC";

/**
 * Enemy scaling options for a generated world.
 * Values must match the Difficulty enum in the backend worlds domain.
 */
export type Difficulty = "EASY" | "NORMAL" | "HARD" | "NIGHTMARE";

/**
 * Primary narrative lens that shapes the generated quest.
 * Values must match the QuestFocus enum in the backend worlds domain.
 */
export type QuestFocus =
  | "EXPLORATION"
  | "RESCUE"
  | "ASSASSINATION"
  | "HEIST"
  | "MYSTERY";

/**
 * Function and flavour category of a single dungeon room.
 * Values must match the RoomType enum in the backend worlds domain.
 */
export type RoomType = "COMBAT" | "SHOP" | "REST" | "BOSS" | "TREASURE" | "EVENT";

/**
 * Response from GET /api/v1/worlds/options.
 * Contains all valid enum values for world generation settings so the client
 * can populate dropdowns dynamically without hardcoding them.
 * room_count_min and room_count_max mirror the backend domain constants.
 */
export interface WorldOptionsResponse {
  readonly themes: readonly string[];
  readonly difficulties: readonly string[];
  readonly quest_focuses: readonly string[];
  readonly room_types: readonly string[];
  readonly room_count_min: number;
  readonly room_count_max: number;
}

/**
 * Request body for POST /api/v1/worlds/generate.
 * room_count must be between 5 and 15 (enforced by the backend domain layer).
 * party_size must be between 1 and 6.
 */
export interface WorldSettingsRequest {
  readonly theme: Theme;
  readonly difficulty: Difficulty;
  readonly quest_focus: QuestFocus;
  readonly room_count: number;
  readonly party_size: number;
  /** Optional free-text hints for the narrator. Null means no notes provided. */
  readonly dm_notes: string | null;
}

/** A single generated room within the world. */
export interface NarratedRoomResponse {
  /** Zero-based position of the room in the dungeon sequence. */
  readonly index: number;
  readonly room_type: RoomType;
  readonly name: string;
  readonly description: string;
  readonly enemy_names: readonly string[];
  readonly npc_names: readonly string[];
  readonly special_notes: string | null;
}

/** The primary quest thread for the generated world. */
export interface MainQuestResponse {
  readonly name: string;
  readonly description: string;
  /** Ordered narrative milestones the party must reach to complete the quest. */
  readonly stages: readonly string[];
}

/**
 * Full response from POST /api/v1/worlds/generate.
 * Represents a complete generated world including rooms, quest, and factions.
 */
export interface GeneratedWorldResponse {
  readonly world_name: string;
  readonly world_description: string;
  readonly atmosphere: string;
  readonly theme: Theme;
  readonly rooms: readonly NarratedRoomResponse[];
  readonly main_quest: MainQuestResponse;
  readonly active_factions: readonly string[];
}
