"use client";

import { useEffect, useRef, useCallback } from "react";
import { useRoomStore } from "@/domains/room/store/room.store";
import { useDungeonStore } from "@/domains/dungeon/store/dungeon.store";
import type { GameEvent } from "@/domains/room/types";

// WebSocket server base URL.
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

// Initial reconnect delay in milliseconds.
const INITIAL_RETRY_MS = 1000;

// Maximum reconnect delay in milliseconds.
const MAX_RETRY_MS = 30_000;

/**
 * Return type for the useGameSocket hook.
 */
export interface UseGameSocketReturn {
  /**
   * Sends a message to the server over the WebSocket connection.
   * No-ops if the socket is not currently open.
   * @param message - The message object to serialize and send.
   */
  send: (message: Record<string, unknown>) => void;
}

/**
 * Manages a WebSocket connection to the game room server.
 * Handles automatic reconnection with exponential backoff,
 * dispatches incoming events to the room store, and cleans up on unmount.
 * @param roomId - The UUID of the room to connect to.
 * @param roomToken - The room-scoped JWT for WebSocket authentication.
 * @returns An object with a send function to emit messages.
 */
export function useGameSocket(
  roomId: string,
  roomToken: string
): UseGameSocketReturn {
  const socketRef = useRef<WebSocket | null>(null);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryDelayRef = useRef<number>(INITIAL_RETRY_MS);

  const {
    setConnected,
    setPlayers,
    addPlayer,
    removePlayer,
    addEvent,
    setPlayerHp,
    setAllPlayerHp,
  } = useRoomStore.getState();

  const connect = useCallback((): void => {
    const url = `${WS_BASE}/api/v1/ws/${roomId}?token=${roomToken}`;
    const socket = new WebSocket(url);
    socketRef.current = socket;

    socket.onopen = (): void => {
      setConnected(true);
      retryDelayRef.current = INITIAL_RETRY_MS;
    };

    socket.onmessage = (event: MessageEvent): void => {
      let parsed: unknown;
      try {
        parsed = JSON.parse(event.data as string) as unknown;
      } catch {
        // Ignore malformed frames.
        return;
      }

      if (typeof parsed !== "object" || parsed === null || !("type" in parsed)) {
        return;
      }

      const gameEvent = parsed as GameEvent;

      switch (gameEvent.type) {
        case "room_state":
          // Players now come as objects with user_id, username, connected.
          setPlayers(
            gameEvent.players.map((p) => ({
              id: p.user_id,
              name: p.username,
              role: "player" as const,
            }))
          );
          // Restore HP state from the room_state payload.
          setAllPlayerHp(gameEvent.player_hp);
          // Restore current room index if the session is already running.
          if (gameEvent.current_room_index !== null) {
            useDungeonStore
              .getState()
              .setCurrentRoomIndex(gameEvent.current_room_index);
          }
          break;

        case "player_joined":
          addPlayer({
            id: gameEvent.user_id,
            name: gameEvent.username,
            role: gameEvent.role,
          });
          break;

        case "player_left":
          removePlayer(gameEvent.user_id);
          break;

        case "room_advanced":
          useDungeonStore.getState().setCurrentRoomIndex(gameEvent.room_index);
          addEvent(gameEvent);
          break;

        case "quest_stage_advanced":
          useDungeonStore.getState().markQuestStageComplete(gameEvent.stage_index);
          addEvent(gameEvent);
          break;

        case "permission_denied":
        case "validation_error":
          // Map to error event shape for the event feed.
          addEvent({ type: "error", detail: gameEvent.detail });
          break;

        default:
          // dice_roll, chat_message, dm_announcement, error, room_event_outcome — append to feed.
          addEvent(gameEvent);
          break;
      }
    };

    socket.onclose = (): void => {
      setConnected(false);
      // Schedule reconnect with exponential backoff.
      retryTimerRef.current = setTimeout(() => {
        connect();
      }, retryDelayRef.current);
      retryDelayRef.current = Math.min(
        retryDelayRef.current * 2,
        MAX_RETRY_MS
      );
    };

    // onerror fires before onclose; onclose handles reconnect.
    socket.onerror = (): void => {
      // Intentionally silent — onclose will handle the retry.
    };
  }, [roomId, roomToken, setConnected, setPlayers, addPlayer, removePlayer, addEvent]);

  useEffect(() => {
    connect();

    return (): void => {
      if (retryTimerRef.current !== null) {
        clearTimeout(retryTimerRef.current);
      }
      if (socketRef.current !== null) {
        // Prevent onclose from scheduling a reconnect after unmount.
        socketRef.current.onclose = null;
        socketRef.current.close();
      }
      setConnected(false);
    };
    // Re-connect when roomId or roomToken changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId, roomToken]);

  const send = useCallback((message: Record<string, unknown>): void => {
    if (
      socketRef.current !== null &&
      socketRef.current.readyState === WebSocket.OPEN
    ) {
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  return { send };
}
