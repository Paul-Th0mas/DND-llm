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
 */
export interface DungeonRoomStatus {
  readonly room_id: string;
  readonly room_name: string;
  readonly is_active: boolean;
}

/**
 * Summary item from GET /api/v1/campaigns/{campaignId}/dungeons.
 */
export interface DungeonSummary {
  readonly dungeon_id: string;
  readonly name: string;
  readonly premise: string;
  readonly room_count: number;
  readonly created_at: string;
  readonly room: DungeonRoomStatus | null;
}

// ---------------------------------------------------------------------------
// Structured room data types (US-063 to US-071)
// ---------------------------------------------------------------------------

/**
 * Structured enemy data for COMBAT and BOSS rooms.
 * Replaces the legacy flat enemy_names array.
 */
export interface EnemyData {
  readonly initial: readonly string[];
  readonly reinforcements: readonly string[];
  readonly trigger_condition: string | null;
  readonly environmental_hazards: string | null;
  readonly boss: string | null;
  readonly special_attacks: readonly string[];
}

/**
 * A single skill check within a room's mechanics block.
 */
export interface SkillCheck {
  readonly type: string;
  readonly dc: number;
  readonly on_success: string;
  readonly on_failure: string | null;
}

/**
 * The mechanical effect category a GameEffect produces when triggered.
 * Maps to the EffectType enum on the backend.
 */
export type EffectType =
  | "DAMAGE"
  | "HEAL"
  | "APPLY_STATUS"
  | "GRANT_LOOT"
  | "SPAWN_ENEMY"
  | "UNLOCK_PATH"
  | "NONE";

/**
 * Describes the action or check that fires a GameEffect.
 * trigger_action is a domain event name (e.g. "on_enemy_death").
 */
export interface TriggerData {
  readonly trigger_action: string;
  readonly check_stat: string | null;
  /** Difficulty Class for the triggering check. Null when no check is required. */
  readonly dc: number | null;
}

/**
 * A discrete mechanical consequence attached to a room trigger (US-071).
 * effect_type determines what happens; trigger describes when it fires.
 */
export interface GameEffect {
  readonly effect_type: EffectType;
  readonly trigger: TriggerData;
  /** Numeric magnitude (e.g. damage points or heal amount). Null when not applicable. */
  readonly value: number | null;
  /** Status effect identifier. Populated only for APPLY_STATUS effects. */
  readonly status: string | null;
  /** Loot item identifier. Populated only for GRANT_LOOT effects. */
  readonly item_id: string | null;
}

/**
 * Structured mechanical content for a dungeon room.
 * rest_benefit is populated for REST rooms; victory_items for BOSS rooms.
 * game_effects lists structured mechanical consequences (US-071).
 */
export interface RoomMechanics {
  readonly skill_checks: readonly SkillCheck[];
  readonly rest_benefit: string | null;
  readonly victory_items: readonly string[];
  readonly game_effects: readonly GameEffect[];
}

/**
 * A single mechanic entry in the dungeon room's mechanics array (US-073).
 * Represents one trigger-effects-description unit from LLM generation.
 * Used when iterating room.mechanics to match player actions.
 */
export interface RoomMechanic {
  readonly trigger: TriggerData;
  readonly effects: readonly GameEffect[];
  readonly description: string;
}

/** A single loot table entry for TREASURE rooms. */
export interface LootItem {
  readonly item: string;
  readonly quantity: number;
  readonly value: string | null;
  readonly rarity: string | null;
}

/** An item sold or offered by an NPC. */
export interface NpcInventoryItem {
  readonly item: string;
  readonly price: number;
}

/**
 * Structured NPC data for SHOP rooms.
 * interaction_dc maps skill names to DC integers, with an optional note key.
 */
export interface NpcData {
  readonly name: string;
  readonly role: string;
  readonly inventory: readonly NpcInventoryItem[];
  readonly interaction_dc: Record<string, unknown> | null;
}

/**
 * Session-wide quest metadata returned alongside a generated dungeon (US-063).
 */
export interface QuestMetadata {
  readonly name: string;
  readonly recommended_level: number;
  readonly environment: string;
  readonly global_modifiers: string;
}

// ---------------------------------------------------------------------------
// Room and dungeon types
// ---------------------------------------------------------------------------

/**
 * A single room within a generated dungeon.
 * Returned inside DungeonDetail.
 */
export interface DungeonRoom {
  readonly index: number;
  readonly room_type: RoomType;
  readonly name: string;
  readonly description: string;
  // Legacy flat fields -- present in old records.
  readonly enemy_names: readonly string[];
  readonly npc_names: readonly string[];
  // Structured fields added in US-063 to US-071. Non-optional; callers must handle null.
  readonly enemies: EnemyData | null;
  readonly mechanics: RoomMechanics | null;
  readonly loot_table: readonly LootItem[] | null;
  readonly npc_data: readonly NpcData[] | null;
}

/**
 * Alias for DungeonRoom used by component props.
 * Keeps backward compatibility with components that import DungeonRoomResponse.
 */
export type DungeonRoomResponse = DungeonRoom;

/**
 * The primary quest thread for a generated dungeon session.
 * Returned inside DungeonDetail.
 */
export interface DungeonQuest {
  readonly name: string;
  readonly description: string;
  readonly stages: readonly string[];
}

/**
 * Alias for DungeonQuest used by component props.
 * Keeps backward compatibility with components that import DungeonQuestResponse.
 */
export type DungeonQuestResponse = DungeonQuest;

/**
 * Full dungeon detail from GET /api/v1/dungeons/{dungeonId}.
 * Contains all rooms, quest stages, metadata, and progression state.
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
  /** Session-wide quest metadata. Null for dungeons generated before US-063. */
  readonly quest_metadata: QuestMetadata | null;
  /** Zero-based index of the room the party is currently in (US-069). */
  readonly current_room_index: number;
  /** Indices of quest stages that have been completed (US-069). */
  readonly completed_stage_indices: readonly number[];
}
