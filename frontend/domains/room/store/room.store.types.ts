import type { Room, Player, GameEvent } from "@/domains/room/types";

/** HP snapshot for a single player as stored in the room state. */
export interface PlayerHpEntry {
  readonly current_hp: number;
  readonly max_hp: number;
  readonly downed: boolean;
  readonly status_effects: readonly string[];
}

/** State shape for the room domain store. */
export interface RoomState {
  readonly roomId: string | null;
  readonly room: Room | null;
  /** Short-lived JWT scoped to the current room, used for WebSocket auth. */
  readonly roomToken: string | null;
  readonly players: readonly Player[];
  /** Ordered log of all game events received from the WebSocket. */
  readonly events: readonly GameEvent[];
  /** True while the WebSocket connection is open. */
  readonly isConnected: boolean;
  /** Map of user_id to current HP snapshot. Updated by state:player_update events. */
  readonly playerHp: ReadonlyMap<string, PlayerHpEntry>;
}

/** Actions available on the room domain store. */
export interface RoomActions {
  /**
   * Sets the active room and its room-scoped token after joining or creating.
   * @param room - The room object returned by the API.
   * @param roomToken - The room-scoped JWT for WebSocket authentication.
   */
  setRoom: (room: Room, roomToken: string) => void;
  /**
   * Replaces the full player list (used when syncing from room_state events).
   * @param players - The complete list of players currently in the room.
   */
  setPlayers: (players: readonly Player[]) => void;
  /**
   * Adds a single player to the list (used for player_joined events).
   * @param player - The player who just joined.
   */
  addPlayer: (player: Player) => void;
  /**
   * Removes a player from the list by user ID (used for player_left events).
   * @param userId - The ID of the player who left.
   */
  removePlayer: (userId: string) => void;
  /**
   * Appends a game event to the event feed.
   * @param event - The event received from the WebSocket.
   */
  addEvent: (event: GameEvent) => void;
  /**
   * Updates the WebSocket connection status.
   * @param connected - True when the socket is open.
   */
  setConnected: (connected: boolean) => void;
  /**
   * Replaces the stored room object with an updated version.
   * Used after PATCH operations such as linking a dungeon.
   * @param room - The updated room returned by the API.
   */
  updateRoom: (room: Room) => void;
  /**
   * Replaces the full event feed (used for reconnection state restore).
   * @param events - The replacement event array.
   */
  replaceEvents: (events: readonly GameEvent[]) => void;
  /**
   * Updates the HP snapshot for a single player.
   * @param userId - The player's user ID.
   * @param hp - The new HP snapshot.
   */
  setPlayerHp: (userId: string, hp: PlayerHpEntry) => void;
  /**
   * Replaces all HP snapshots from the room_state payload.
   * @param entries - Array of HP entries from the server.
   */
  setAllPlayerHp: (
    entries: ReadonlyArray<{
      readonly user_id: string;
      readonly current_hp: number;
      readonly max_hp: number;
      readonly downed: boolean;
      readonly status_effects: readonly string[];
    }>
  ) => void;
  /** Clears all room state when the user leaves or disconnects. */
  clearRoom: () => void;
}
