import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { RoomState, RoomActions } from "./room.store.types";
import type { Room, Player, GameEvent } from "@/domains/room/types";

// Combined store type merging state shape and actions.
type RoomStore = RoomState & RoomActions;

/**
 * Zustand store for the Room domain.
 * Manages the active room, connected players, game event feed, and socket status.
 */
export const useRoomStore = create<RoomStore>()(
  devtools(
    (set) => ({
      // Initial state
      roomId: null,
      room: null,
      roomToken: null,
      players: [],
      events: [],
      isConnected: false,

      setRoom: (room: Room, roomToken: string) =>
        set(
          { room, roomId: room.id, roomToken },
          false,
          "room/setRoom"
        ),

      setPlayers: (players: readonly Player[]) =>
        set({ players }, false, "room/setPlayers"),

      addPlayer: (player: Player) =>
        set(
          (state) => ({
            players: state.players.some((p) => p.id === player.id)
              ? state.players
              : [...state.players, player],
          }),
          false,
          "room/addPlayer"
        ),

      removePlayer: (userId: string) =>
        set(
          (state) => ({
            players: state.players.filter((p) => p.id !== userId),
          }),
          false,
          "room/removePlayer"
        ),

      addEvent: (event: GameEvent) =>
        set(
          (state) => ({ events: [...state.events, event] }),
          false,
          "room/addEvent"
        ),

      setConnected: (isConnected: boolean) =>
        set({ isConnected }, false, "room/setConnected"),

      updateRoom: (room: Room) =>
        set({ room }, false, "room/updateRoom"),

      clearRoom: () =>
        set(
          {
            roomId: null,
            room: null,
            roomToken: null,
            players: [],
            events: [],
            isConnected: false,
          },
          false,
          "room/clearRoom"
        ),
    }),
    { name: "RoomStore" }
  )
);

/**
 * Selects the active room object from the room store.
 * @param state - The current room store state.
 * @returns The Room or null if no room is active.
 */
export const selectRoom = (state: RoomStore): RoomState["room"] => state.room;

/**
 * Selects the room-scoped token from the room store.
 * @param state - The current room store state.
 * @returns The room token string or null.
 */
export const selectRoomToken = (state: RoomStore): RoomState["roomToken"] =>
  state.roomToken;

/**
 * Selects the player list from the room store.
 * @param state - The current room store state.
 * @returns The array of players currently in the room.
 */
export const selectPlayers = (state: RoomStore): RoomState["players"] =>
  state.players;

/**
 * Selects the game event feed from the room store.
 * @param state - The current room store state.
 * @returns The ordered array of game events.
 */
export const selectEvents = (state: RoomStore): RoomState["events"] =>
  state.events;

/**
 * Selects the WebSocket connection status from the room store.
 * @param state - The current room store state.
 * @returns True when the socket is open.
 */
export const selectIsConnected = (
  state: RoomStore
): RoomState["isConnected"] => state.isConnected;
