/**
 * TypeScript types for the dungeon domain.
 * All values must match the enums and schemas in app/dungeons/ on the backend.
 */

/**
 * Function and encounter flavour category of a single dungeon room.
 * Maps to the RoomType enum in the backend dungeons domain.
 */
export type RoomType =
  | "COMBAT"
  | "SHOP"
  | "REST"
  | "BOSS"
  | "TREASURE"
  | "EVENT";

/**
 * Request body for POST /api/v1/campaigns/{campaignId}/dungeons.
 * Generates a new dungeon session for the given campaign.
 */
export interface GenerateDungeonRequest {
  /** Number of rooms to generate. Must be between 5 and 15. */
  readonly room_count: number;
  /** Number of players in the party. Must be between 1 and 8. */
  readonly party_size: number;
  /** Optional difficulty override for this session (e.g. "Hard"). Null means use campaign defaults. */
  readonly difficulty_override: string | null;
  /** Optional free-text hints appended to the LLM prompt. */
  readonly dm_notes: string | null;
}

/**
 * Response from POST /api/v1/campaigns/{campaignId}/dungeons.
 * A summary returned immediately after dungeon generation and persistence.
 */
export interface DungeonCreatedResponse {
  readonly dungeon_id: string;
  readonly name: string;
  readonly premise: string;
  readonly room_count: number;
  readonly quest_name: string;
  /** URL for the next step in the pipeline (room creation). */
  readonly next_step: string;
}

/**
 * Embedded room status object returned inside DungeonSummary when a game
 * room has been created for this dungeon. Null when no room exists yet.
 * Matches the shape of the room field in GET /api/v1/campaigns/{id}/dungeons.
 */
export interface DungeonRoomStatus {
  readonly room_id: string;
  readonly room_name: string;
  readonly is_active: boolean;
}

/**
 * Summary item from GET /api/v1/campaigns/{campaignId}/dungeons.
 * Used to populate the past-dungeons list on the campaign detail page.
 * The room field is present when a game room has been opened for this dungeon.
 */
export interface DungeonSummary {
  readonly dungeon_id: string;
  readonly name: string;
  readonly premise: string;
  readonly room_count: number;
  readonly created_at: string;
  /** Linked room status, or null if no room has been created for this dungeon. */
  readonly room: DungeonRoomStatus | null;
}

/**
 * A single room within a generated dungeon.
 * Returned inside DungeonDetail.
 */
export interface DungeonRoom {
  /** Zero-based position of this room in the dungeon sequence. */
  readonly index: number;
  readonly room_type: RoomType;
  readonly name: string;
  readonly description: string;
  readonly enemy_names: readonly string[];
  readonly npc_names: readonly string[];
  readonly special_notes: string | null;
}

/**
 * Alias for DungeonRoom used by component props.
 * Components imported before the type rename used DungeonRoomResponse — keep
 * both names pointing at the same shape to avoid a cascade of import changes.
 */
export type DungeonRoomResponse = DungeonRoom;

/**
 * The primary quest thread for a generated dungeon session.
 * Returned inside DungeonDetail.
 */
export interface DungeonQuest {
  readonly name: string;
  readonly description: string;
  /** Ordered narrative milestones the party must complete. */
  readonly stages: readonly string[];
}

/**
 * Alias for DungeonQuest used by component props.
 * Keeps backward compatibility with components that import DungeonQuestResponse.
 */
export type DungeonQuestResponse = DungeonQuest;

/**
 * Full dungeon detail from GET /api/v1/dungeons/{dungeonId}.
 * Contains all rooms, quest stages, and metadata.
 */
export interface DungeonDetail {
  readonly dungeon_id: string;
  readonly campaign_id: string;
  readonly world_id: string;
  readonly name: string;
  readonly premise: string;
  readonly rooms: readonly DungeonRoom[];
  readonly quest: DungeonQuest;
  readonly created_at: string;
}
