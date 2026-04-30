import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { RoomState, RoomActions, PlayerHpEntry } from "./room.store.types";
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
      playerHp: new Map<string, PlayerHpEntry>(),

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

      replaceEvents: (events: readonly GameEvent[]) =>
        set({ events }, false, "room/replaceEvents"),

      setPlayerHp: (userId: string, hp: PlayerHpEntry) =>
        set(
          (state) => {
            const next = new Map(state.playerHp);
            next.set(userId, hp);
            return { playerHp: next };
          },
          false,
          "room/setPlayerHp"
        ),

      setAllPlayerHp: (entries) =>
        set(
          () => {
            const next = new Map<string, PlayerHpEntry>();
            for (const entry of entries) {
              next.set(entry.user_id, {
                current_hp: entry.current_hp,
                max_hp: entry.max_hp,
                downed: entry.downed,
                status_effects: entry.status_effects,
              });
            }
            return { playerHp: next };
          },
          false,
          "room/setAllPlayerHp"
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
            playerHp: new Map<string, PlayerHpEntry>(),
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

/**
 * Selects the playerHp map from the room store.
 * @param state - The current room store state.
 * @returns A Map of user_id to HP snapshot.
 */
export const selectPlayerHp = (state: RoomStore): RoomState["playerHp"] =>
  state.playerHp;
