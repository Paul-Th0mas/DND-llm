/** A game room managed by a Dungeon Master. */
export interface Room {
  readonly id: string;
  readonly name: string;
  readonly invite_code: string;
  readonly max_players: number;
  readonly is_active: boolean;
  readonly player_ids: readonly string[];
  /** UUID of the DM who owns this room. */
  readonly dm_id: string;
  /** UUID of the dungeon session linked to this room, or null if not set. */
  readonly dungeon_id: string | null;
  /** UUID of the campaign linked to this room, or null if not set. */
  readonly campaign_id: string | null;
}

/** Response shape returned by room create and join endpoints. */
export interface RoomResponse {
  readonly room: Room;
  /** Short-lived JWT scoped to this room, used for WebSocket authentication. */
  readonly room_token: string;
}

/** A player present in a room, enriched with profile data. */
export interface Player {
  readonly id: string;
  readonly name: string;
  readonly role: "dm" | "player";
}

/** Valid die face counts for dice-roll actions. */
export type DiceSides = 4 | 6 | 8 | 10 | 12 | 20;

// ---- WebSocket event types (server -> client) ----

/** A player entry as sent in the room_state players array. */
export interface RoomStatePlayer {
  readonly user_id: string;
  readonly username: string;
  readonly connected: boolean;
}

/** An HP entry as sent in the room_state player_hp array. */
export interface RoomStatePlayerHp {
  readonly user_id: string;
  readonly current_hp: number;
  readonly max_hp: number;
  readonly downed: boolean;
  readonly status_effects: readonly string[];
}

/** Emitted on connection to sync the full room state for all connected players. */
export interface RoomStateEvent {
  readonly type: "room_state";
  readonly players: ReadonlyArray<RoomStatePlayer>;
  readonly player_hp: ReadonlyArray<RoomStatePlayerHp>;
  readonly session_started: boolean;
  readonly session_ended: boolean;
  readonly current_room_index: number | null;
  readonly current_quest_stage: number | null;
  readonly recent_events: readonly unknown[];
  readonly current_mechanics: readonly unknown[];
}

/** Emitted when a new player connects to the room. */
export interface PlayerJoinedEvent {
  readonly type: "player_joined";
  readonly user_id: string;
  readonly username: string;
  readonly role: "dm" | "player";
}

/** Emitted when a player disconnects from the room. */
export interface PlayerLeftEvent {
  readonly type: "player_left";
  readonly user_id: string;
}

/** Emitted when any player rolls dice. */
export interface DiceRollEvent {
  readonly type: "dice_roll";
  readonly user_id: string;
  readonly sides: DiceSides;
  readonly result: number;
}

/** Emitted when the DM broadcasts an announcement to all players. */
export interface DmAnnouncementEvent {
  readonly type: "dm_announcement";
  readonly content: string;
}

/** Emitted when any player sends a chat message. */
export interface ChatMessageEvent {
  readonly type: "chat_message";
  readonly user_id: string;
  readonly role: "dm" | "player";
  readonly content: string;
}

/** Emitted by the server when a client action fails. */
export interface ErrorEvent {
  readonly type: "error";
  readonly detail: string;
}

/**
 * Emitted by the server after the DM starts a session.
 * Contains the generated dungeon narrative, world lore, and campaign context
 * for display in the event feed.
 */
export interface DungeonIntroEvent {
  readonly type: "dungeon_intro";
  readonly dungeon_name: string;
  readonly premise: string;
  readonly quest: {
    readonly name: string;
    readonly description: string;
    readonly stages: readonly string[];
  };
  readonly rooms: ReadonlyArray<{ readonly name: string; readonly description: string }>;
  readonly world: {
    readonly name: string;
    readonly lore_summary: string;
    readonly theme: string;
  };
  readonly campaign: {
    readonly name: string;
    readonly tone: string;
    readonly themes: readonly string[];
  };
  /** Global dungeon modifier string from quest_metadata (US-070). Null for legacy dungeons. */
  readonly global_modifiers?: string | null;
  /** Dungeon environment string from quest_metadata (US-070). Null for legacy dungeons. */
  readonly environment?: string | null;
}

/** Emitted when the DM advances the active room (US-069). */
export interface RoomAdvancedEvent {
  readonly type: "room_advanced";
  readonly room_index: number;
  /** The full room object at the new index. Typed loosely to avoid cross-domain imports. */
  readonly room: {
    readonly index: number;
    readonly room_type: string;
    readonly name: string;
    readonly description: string;
    readonly enemies?: unknown;
    readonly mechanics?: unknown;
    readonly loot_table?: unknown;
    readonly npc_data?: unknown;
  };
}

/** Emitted when the DM marks a quest stage complete (US-069). */
export interface QuestStageAdvancedEvent {
  readonly type: "quest_stage_advanced";
  readonly stage_index: number;
  readonly stage_text: string;
}

/** Emitted after a skill check is resolved server-side (US-070). */
export interface RoomEventOutcomeEvent {
  readonly type: "room_event_outcome";
  readonly room_index: number;
  readonly skill_type: string;
  readonly roll_result: number;
  readonly dc: number;
  readonly outcome: "success" | "failure";
  /** The narrative result text. Absent when on_failure is null and outcome is failure. */
  readonly narrative?: string;
}

/**
 * Emitted to all participants when a player action resolves against room mechanics (US-073).
 * effects_applied values correspond to the EffectType enum in the dungeon domain.
 */
export interface ResolutionEvent {
  readonly type: "event:resolution";
  readonly player_id: string;
  /** Display name of the acting player, if provided by the server. */
  readonly username?: string;
  readonly action: string;
  /** The d20 roll result plus stat modifier. Null for auto-success (no DC check). */
  readonly roll: number | null;
  /** The Difficulty Class for the check. Null when no DC check was required. */
  readonly dc: number | null;
  readonly outcome: "success" | "failure";
  /** List of effect type strings applied (e.g. ["DAMAGE", "APPLY_STATUS"]). */
  readonly effects_applied: readonly string[];
  readonly narrative: string;
}

/**
 * Emitted to all participants when a player takes DAMAGE and their HP changes (US-073).
 */
export interface PlayerUpdateEvent {
  readonly type: "state:player_update";
  readonly player_id: string;
  readonly current_hp: number;
  readonly max_hp: number;
  readonly downed: boolean;
  readonly status_effects: readonly string[];
}

/**
 * Emitted to all participants when a player receives loot on success (US-073).
 */
export interface LootAwardedEvent {
  readonly type: "loot:awarded";
  readonly player_id: string;
  /** Display name of the player receiving loot, if provided by the server. */
  readonly username?: string;
  readonly items: ReadonlyArray<{
    readonly item_id: string;
    readonly name: string;
    readonly quantity: number;
  }>;
}

/**
 * Emitted to all participants when an UNLOCK_PATH effect fires (US-073).
 */
export interface PathUnlockedEvent {
  readonly type: "event:path_unlocked";
  readonly room_index: number;
  readonly target: string | null;
}

/**
 * Emitted to all participants when a SPAWN_ENEMY effect fires (US-073).
 */
export interface EnemySpawnedEvent {
  readonly type: "event:enemy_spawned";
  readonly room_index: number;
  readonly enemy_id: string | null;
}

/**
 * Emitted to all participants when the DM attacks an enemy targeting a player (US-082).
 */
export interface EnemyAttackResultEvent {
  readonly type: "event:enemy_attack_result";
  readonly enemy_id: string;
  readonly target_player_id: string;
  readonly username: string;
  readonly roll: number;
  readonly ac: number;
  readonly hit: boolean;
  readonly damage: number;
  readonly new_hp: number;
  readonly downed: boolean;
}

/** Sent to the sender when they attempted a DM-only action without the DM role. */
export interface PermissionDeniedEvent {
  readonly type: "permission_denied";
  readonly detail: string;
}

/** Sent to the sender when a message fails server-side validation. */
export interface ValidationErrorEvent {
  readonly type: "validation_error";
  readonly detail: string;
}

/** Union of all possible server-to-client WebSocket events. */
export type GameEvent =
  | RoomStateEvent
  | PlayerJoinedEvent
  | PlayerLeftEvent
  | DiceRollEvent
  | DmAnnouncementEvent
  | ChatMessageEvent
  | ErrorEvent
  | DungeonIntroEvent
  | RoomAdvancedEvent
  | QuestStageAdvancedEvent
  | RoomEventOutcomeEvent
  | PermissionDeniedEvent
  | ValidationErrorEvent
  | ResolutionEvent
  | PlayerUpdateEvent
  | LootAwardedEvent
  | PathUnlockedEvent
  | EnemySpawnedEvent
  | EnemyAttackResultEvent;
