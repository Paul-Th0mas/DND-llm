"use client";

import { useEffect, useRef } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import CasinoIcon from "@mui/icons-material/Casino";
import { useRoomStore, selectEvents, selectPlayers } from "@/domains/room/store/room.store";
import type { GameEvent, Player } from "@/domains/room/types";

/**
 * Resolves a user_id to the player's display name.
 * Falls back to a truncated ID if the player is not found in the list.
 * @param userId - The user ID to resolve.
 * @param players - The current list of players in the room.
 * @returns The player's display name, or the first 8 characters of the ID.
 */
function resolvePlayerName(userId: string, players: readonly Player[]): string {
  return players.find((p) => p.id === userId)?.name ?? userId.slice(0, 8);
}

/** Props for the EventItem component. */
interface EventItemProps {
  readonly event: GameEvent;
  readonly players: readonly Player[];
}

/**
 * Renders a single game event as a styled feed item.
 * @param event - The game event to render.
 * @param players - The current player list, used to resolve display names.
 * @returns A styled feed entry.
 */
function EventItem({ event, players }: EventItemProps): React.ReactElement {
  switch (event.type) {
    case "dm_announcement":
      return (
        <Box
          sx={{
            borderLeft: "3px solid #5c4230",
            pl: 2,
            py: 0.75,
            bgcolor: "rgba(92,66,48,0.06)",
            borderRadius: "0 6px 6px 0",
          }}
        >
          <Typography
            variant="body2"
            sx={{ fontStyle: "italic", color: "#3a2820", lineHeight: 1.6 }}
          >
            {event.content}
          </Typography>
        </Box>
      );

    case "dice_roll":
      return (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            py: 0.5,
          }}
        >
          <CasinoIcon sx={{ fontSize: "1rem", color: "#a07d60", flexShrink: 0 }} />
          <Typography variant="body2" sx={{ color: "#3a2820" }}>
            <Box component="span" sx={{ fontWeight: 600, color: "#5c4230" }}>
              {resolvePlayerName(event.user_id, players)}
            </Box>{" "}
            rolled d{event.sides} →{" "}
            <Box component="span" sx={{ fontWeight: 800, fontSize: "1rem" }}>
              {event.result}
            </Box>
          </Typography>
        </Box>
      );

    case "chat_message":
      return (
        <Box sx={{ display: "flex", alignItems: "baseline", gap: 1, py: 0.25 }}>
          <Chip
            label={event.role === "dm" ? "DM" : "Player"}
            size="small"
            sx={{
              height: 16,
              fontSize: "0.6rem",
              fontWeight: 700,
              bgcolor:
                event.role === "dm"
                  ? "rgba(92,66,48,0.15)"
                  : "rgba(160,125,96,0.15)",
              color: event.role === "dm" ? "#5c4230" : "#7d5e45",
              flexShrink: 0,
            }}
          />
          <Typography variant="body2" sx={{ color: "#1e1410" }}>
            <Box component="span" sx={{ fontWeight: 600 }}>
              {resolvePlayerName(event.user_id, players)}:
            </Box>{" "}
            {event.content}
          </Typography>
        </Box>
      );

    case "error":
      return (
        <Alert severity="error" sx={{ py: 0.25, fontSize: "0.8rem" }}>
          {event.detail}
        </Alert>
      );

    default:
      return <></>;
  }
}

/**
 * Scrollable event feed displaying all game events in chronological order.
 * Auto-scrolls to the latest event when new events arrive.
 * Renders dice rolls, chat messages, DM announcements, and errors.
 */
export function EventFeed(): React.ReactElement {
  const events = useRoomStore(selectEvents);
  const players = useRoomStore(selectPlayers);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever events change.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  return (
    <Box
      sx={{
        flex: 1,
        overflowY: "auto",
        p: 3,
        display: "flex",
        flexDirection: "column",
        gap: 1,
        bgcolor: "#F9F8F6",
      }}
    >
      {events.length === 0 ? (
        <Box
          sx={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Typography variant="body2" color="text.disabled" fontStyle="italic">
            The adventure begins…
          </Typography>
        </Box>
      ) : (
        events.map((event, index) => (
          // Events are append-only; index is a stable key here.
          <EventItem key={index} event={event} players={players} />
        ))
      )}
      <div ref={bottomRef} />
    </Box>
  );
}
