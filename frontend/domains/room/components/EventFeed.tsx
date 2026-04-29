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
 * Renders a single game event as a styled feed item using the Scriptorium
 * design language. Narrative events use Newsreader; metadata uses Work Sans.
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
            // Left accent border — the "Chronicler's quote" style.
            borderLeft: "3px solid #725a42",
            pl: 2.5,
            py: 1.5,
            // Slight tonal lift without an explicit box border.
            bgcolor: "rgba(114,90,66,0.05)",
            borderRadius: "0 0.375rem 0.375rem 0",
          }}
        >
          <Typography
            sx={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: "1.1rem",
              fontStyle: "italic",
              color: "#3a311b",
              lineHeight: 1.65,
              letterSpacing: "-0.01em",
            }}
          >
            &ldquo;{event.content}&rdquo;
          </Typography>
        </Box>
      );

    case "dice_roll":
      return (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            py: 0.5,
          }}
        >
          <CasinoIcon sx={{ fontSize: "1rem", color: "#a07d60", flexShrink: 0 }} />
          <Typography
            sx={{
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.875rem",
              color: "#3a311b",
            }}
          >
            <Box component="span" sx={{ fontWeight: 600, color: "#5c4230" }}>
              {resolvePlayerName(event.user_id, players)}
            </Box>{" "}
            rolled d{event.sides}{" "}
            <Box component="span" sx={{ color: "#695e45" }}>
              &rarr;
            </Box>{" "}
            <Box
              component="span"
              sx={{
                fontFamily: "var(--font-newsreader), serif",
                fontWeight: 800,
                fontSize: "1.1rem",
                color: "#725a42",
              }}
            >
              {event.result}
            </Box>
          </Typography>
        </Box>
      );

    case "chat_message":
      return (
        <Box sx={{ display: "flex", alignItems: "baseline", gap: 1.5, py: 0.5 }}>
          <Chip
            label={event.role === "dm" ? "DM" : "Player"}
            size="small"
            sx={{
              height: 18,
              fontSize: "0.6rem",
              fontWeight: 700,
              fontFamily: "var(--font-work-sans), sans-serif",
              letterSpacing: "0.05em",
              bgcolor:
                event.role === "dm"
                  ? "rgba(92,66,48,0.12)"
                  : "rgba(160,125,96,0.12)",
              color: event.role === "dm" ? "#5c4230" : "#7d5e45",
              flexShrink: 0,
            }}
          />
          <Typography
            sx={{
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.875rem",
              color: "#3a311b",
              lineHeight: 1.5,
            }}
          >
            <Box component="span" sx={{ fontWeight: 600 }}>
              {resolvePlayerName(event.user_id, players)}:
            </Box>{" "}
            {event.content}
          </Typography>
        </Box>
      );

    case "error":
      return (
        <Alert
          severity="error"
          sx={{
            py: 0.5,
            fontSize: "0.8rem",
            bgcolor: "rgba(158,66,44,0.05)",
            color: "#9e422c",
            "& .MuiAlert-icon": { color: "#9e422c" },
            border: "none",
          }}
        >
          {event.detail}
        </Alert>
      );

    /**
     * Dungeon introduction card emitted by the server when the DM starts a session.
     * Uses the Scriptorium card style — dark left accent, Newsreader heading,
     * Work Sans body. No explicit borders.
     */
    case "dungeon_intro":
      return (
        <Box
          sx={{
            bgcolor: "#f9ecd5",
            borderLeft: "4px solid #5c4230",
            borderRadius: "0 0.375rem 0.375rem 0",
            p: 2.5,
            display: "flex",
            flexDirection: "column",
            gap: 1.5,
          }}
        >
          {/* Dungeon name heading — Newsreader serif for narrative identity */}
          <Typography
            sx={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: "1.3rem",
              fontWeight: 700,
              color: "#1e1410",
              letterSpacing: "-0.01em",
            }}
          >
            {event.dungeon_name}
          </Typography>

          {/* Premise — italic narrative voice */}
          <Typography
            sx={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: "0.95rem",
              fontStyle: "italic",
              color: "#3a311b",
              lineHeight: 1.6,
            }}
          >
            {event.premise}
          </Typography>

          {/* Quest block */}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
            <Typography
              sx={{
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.75rem",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: "#725a42",
              }}
            >
              {event.quest.name}
            </Typography>
            <Typography
              sx={{
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.875rem",
                color: "#3a311b",
              }}
            >
              {event.quest.description}
            </Typography>
            {event.quest.stages.length > 0 && (
              <ol style={{ paddingLeft: "1.25rem", margin: 0 }}>
                {event.quest.stages.map((stage, i) => (
                  <li key={i}>
                    <Typography
                      sx={{
                        fontFamily: "var(--font-work-sans), sans-serif",
                        fontSize: "0.875rem",
                        color: "#3a311b",
                      }}
                    >
                      {stage}
                    </Typography>
                  </li>
                ))}
              </ol>
            )}
          </Box>

          {/* Rooms section */}
          {event.rooms.length > 0 && (
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              <Typography
                sx={{
                  fontFamily: "var(--font-work-sans), sans-serif",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  color: "#725a42",
                }}
              >
                Rooms
              </Typography>
              {event.rooms.map((room, i) => (
                <Box key={i} sx={{ display: "flex", flexDirection: "column", gap: 0.25 }}>
                  <Typography
                    sx={{
                      fontFamily: "var(--font-newsreader), serif",
                      fontSize: "0.95rem",
                      fontWeight: 700,
                      color: "#3a311b",
                    }}
                  >
                    {room.name}
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: "var(--font-work-sans), sans-serif",
                      fontSize: "0.8rem",
                      color: "#695e45",
                    }}
                  >
                    {room.description}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}

          {/* World and campaign footers */}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 0.25, pt: 0.5 }}>
            <Box sx={{ width: "100%", height: "1px", bgcolor: "rgba(191,177,147,0.2)", mb: 0.5 }} />
            <Typography
              sx={{
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.7rem",
                color: "#7d5e45",
                fontStyle: "italic",
              }}
            >
              {`World: ${event.world.name} — ${event.world.lore_summary} (${event.world.theme})`}
            </Typography>
            <Typography
              sx={{
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.7rem",
                color: "#7d5e45",
                fontStyle: "italic",
              }}
            >
              {`Campaign: ${event.campaign.name} · ${event.campaign.tone}`}
              {event.campaign.themes.length > 0 && ` · ${event.campaign.themes.join(", ")}`}
            </Typography>
          </Box>
        </Box>
      );

    /** Emitted when the DM advances to a new room (US-069). */
    case "room_advanced":
      return (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            py: 0.75,
            borderLeft: "3px solid #3a2870",
            pl: 2,
            bgcolor: "rgba(30,20,60,0.04)",
            borderRadius: "0 0.375rem 0.375rem 0",
          }}
        >
          <Typography
            sx={{
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.875rem",
              color: "#3a311b",
            }}
          >
            <Box component="span" sx={{ fontWeight: 700, color: "#3a2870" }}>
              The party enters room {event.room_index + 1}:
            </Box>{" "}
            <Box component="span" sx={{ fontStyle: "italic" }}>
              {event.room.name}
            </Box>
          </Typography>
        </Box>
      );

    /** Emitted when the DM marks a quest stage complete (US-069). */
    case "quest_stage_advanced":
      return (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            py: 0.75,
            borderLeft: "3px solid #2e7d32",
            pl: 2,
            bgcolor: "rgba(30,80,30,0.04)",
            borderRadius: "0 0.375rem 0.375rem 0",
          }}
        >
          <Typography
            sx={{
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.875rem",
              color: "#3a311b",
            }}
          >
            <Box component="span" sx={{ fontWeight: 700, color: "#2e7d32" }}>
              Quest stage complete:
            </Box>{" "}
            {event.stage_text}
          </Typography>
        </Box>
      );

    /** Emitted after a skill check is resolved server-side (US-070). */
    case "room_event_outcome":
      return (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 0.5,
            py: 1,
            pl: 2,
            borderLeft: `3px solid ${event.outcome === "success" ? "#a07d60" : "#9e422c"}`,
            bgcolor:
              event.outcome === "success"
                ? "rgba(160,125,96,0.05)"
                : "rgba(158,66,44,0.05)",
            borderRadius: "0 0.375rem 0.375rem 0",
          }}
        >
          <Typography
            sx={{
              fontFamily: "var(--font-work-sans), sans-serif",
              fontSize: "0.75rem",
              fontWeight: 700,
              color: event.outcome === "success" ? "#7d5e45" : "#9e422c",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            {event.skill_type} DC {event.dc} - Roll {event.roll_result}{" "}
            {event.outcome === "success" ? "- Success" : "- Failure"}
          </Typography>
          {event.narrative !== undefined && (
            <Typography
              sx={{
                fontFamily: "var(--font-newsreader), serif",
                fontSize: "0.95rem",
                fontStyle: "italic",
                color: "#3a311b",
                lineHeight: 1.6,
              }}
            >
              {event.narrative}
            </Typography>
          )}
        </Box>
      );

    /** player_joined and player_left events are handled in useGameSocket, not rendered here. */
    case "player_joined":
    case "player_left":
    case "room_state":
      return <></>;

    default:
      return <></>;
  }
}

/**
 * Scrollable event feed displaying all game events in chronological order.
 * Auto-scrolls to the latest event when new events arrive.
 * Uses the Scriptorium parchment background with the custom thin scrollbar.
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
        gap: 1.5,
        bgcolor: "#fdf2df",
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
          <Typography
            sx={{
              fontFamily: "var(--font-newsreader), serif",
              fontSize: "1rem",
              fontStyle: "italic",
              color: "#bfb193",
            }}
          >
            The adventure begins...
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
