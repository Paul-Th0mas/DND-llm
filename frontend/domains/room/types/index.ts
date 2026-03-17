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

/** Emitted on connection to sync the full list of connected player IDs. */
export interface RoomStateEvent {
  readonly type: "room_state";
  readonly players: readonly string[];
}

/** Emitted when a new player connects to the room. */
export interface PlayerJoinedEvent {
  readonly type: "player_joined";
  readonly user_id: string;
  /** Display name of the joining player, if provided by the server. */
  readonly name?: string;
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
  | DungeonIntroEvent;
