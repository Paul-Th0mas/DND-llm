"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { useRoomStore } from "@/domains/room/store/room.store";
import { useAuthStore, selectUser } from "@/shared/store/auth.store";
import { useGameSocket } from "@/domains/room/hooks/useGameSocket";
import { RoomTopBar } from "@/domains/room/components/RoomTopBar";
import { PlayerSidebar } from "@/domains/room/components/PlayerSidebar";
import { EventFeed } from "@/domains/room/components/EventFeed";
import { DiceRoller } from "@/domains/room/components/DiceRoller";
import { ChatInput } from "@/domains/room/components/ChatInput";

/**
 * Game room page — the primary multiplayer interface.
 * Full-viewport layout with a sidebar and a main panel containing the event
 * feed, dice roller, and chat input.
 * Mounts the WebSocket connection via useGameSocket on load.
 */
export default function RoomPage(): React.ReactElement {
  const params = useParams<{ roomId: string }>();
  const roomId = params.roomId;
  const router = useRouter();

  const user = useAuthStore(selectUser);
  const roomToken = useRoomStore((s) => s.roomToken);
  const clearRoom = useRoomStore((s) => s.clearRoom);

  // Retrieve the room token: store first, then localStorage fallback.
  const effectiveRoomToken =
    roomToken ?? (typeof window !== "undefined"
      ? (localStorage.getItem(`room_token_${roomId}`) ?? "")
      : "");

  const { send } = useGameSocket(
    roomId,
    effectiveRoomToken
  );

  // Redirect to dashboard if we have no room token (user hasn't joined).
  useEffect(() => {
    if (!effectiveRoomToken) {
      router.replace("/dashboard");
    }
  }, [effectiveRoomToken, router]);

  // Watch for the current user being removed from the player list
  // (kicked or session ended by DM) and redirect to dashboard.
  useEffect(() => {
    if (!user) return;
    const unsubscribe = useRoomStore.subscribe((state) => {
      const isStillPresent = state.players.some((p) => p.id === user.id);
      // Only redirect if the room is connected and the user is gone.
      if (state.isConnected && !isStillPresent && state.players.length > 0) {
        clearRoom();
        router.push("/dashboard");
      }
    });
    return unsubscribe;
  }, [user, clearRoom, router]);

  function handleLeave(): void {
    clearRoom();
    router.push("/dashboard");
  }

  if (!effectiveRoomToken) {
    return (
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "background.default",
        }}
      >
        <CircularProgress sx={{ color: "primary.main" }} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        bgcolor: "background.default",
      }}
    >
      {/* Top bar — full width */}
      <RoomTopBar onLeave={handleLeave} />

      {/* Body — sidebar + main content */}
      <Box sx={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left: player list */}
        <PlayerSidebar />

        {/* Right: feed + input stack */}
        <Box
          sx={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Event feed — fills remaining vertical space */}
          <EventFeed />

          {/* Dice roller row */}
          <DiceRoller send={send} />

          {/* Chat input row */}
          <ChatInput send={send} />
        </Box>
      </Box>
    </Box>
  );
}
