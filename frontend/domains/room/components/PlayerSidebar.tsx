"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import Avatar from "@mui/material/Avatar";
import { useRoomStore, selectPlayers, selectRoom } from "@/domains/room/store/room.store";

/**
 * Left sidebar listing the DM and all players connected to the game room.
 * Displays the room name at the top followed by a player roster with online
 * status indicators. 256px fixed width; background color shift creates
 * separation — no explicit border (follows the "No-Line Rule").
 */
export function PlayerSidebar(): React.ReactElement {
  const players = useRoomStore(selectPlayers);
  const room = useRoomStore(selectRoom);

  return (
    <Box
      component="aside"
      sx={{
        width: 256,
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        bgcolor: "#fdf2df",
        boxShadow: "6px 0 32px rgba(58,49,27,0.06)",
        overflowY: "auto",
        zIndex: 10,
      }}
    >
      {/* Room identity — top brand area */}
      <Box sx={{ px: 3, pt: 4, pb: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 0.5 }}>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              bgcolor: "#5c4230",
              color: "#fff8f1",
              fontSize: "0.9rem",
              fontWeight: 700,
              fontFamily: "var(--font-newsreader), serif",
              flexShrink: 0,
            }}
          >
            {(room?.name ?? "R").charAt(0).toUpperCase()}
          </Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography
              sx={{
                fontFamily: "var(--font-newsreader), serif",
                fontSize: "1.15rem",
                fontWeight: 700,
                color: "#725a42",
                letterSpacing: "-0.01em",
                lineHeight: 1.2,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {room?.name ?? "The Scriptorium"}
            </Typography>
            <Typography
              sx={{
                fontFamily: "var(--font-work-sans), sans-serif",
                fontSize: "0.6rem",
                color: "rgba(58,49,27,0.5)",
                fontWeight: 400,
              }}
            >
              Game Room
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Players section */}
      <Box sx={{ px: 2, flex: 1 }}>
        <Typography
          sx={{
            fontFamily: "var(--font-work-sans), sans-serif",
            fontSize: "0.6rem",
            textTransform: "uppercase",
            letterSpacing: "0.3em",
            fontWeight: 700,
            color: "#bfb193",
            px: 1,
            mb: 2,
          }}
        >
          Players
        </Typography>

        <List dense disablePadding sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
          {players.length === 0 ? (
            <ListItem sx={{ py: 2 }}>
              <ListItemText
                primary={
                  <Typography
                    sx={{
                      fontFamily: "var(--font-work-sans), sans-serif",
                      fontSize: "0.8rem",
                      color: "#bfb193",
                      textAlign: "center",
                      fontStyle: "italic",
                    }}
                  >
                    Awaiting adventurers...
                  </Typography>
                }
              />
            </ListItem>
          ) : (
            players.map((player) => (
              <ListItem
                key={player.id}
                sx={{
                  px: 1,
                  py: 0.75,
                  borderRadius: "0.375rem",
                  cursor: "pointer",
                  transition: "background-color 150ms ease",
                  "&:hover": { bgcolor: "#fff8f1" },
                  gap: 0,
                  alignItems: "center",
                }}
              >
                <ListItemAvatar sx={{ minWidth: 48 }}>
                  {/* Wrapper for avatar + status dot */}
                  <Box sx={{ position: "relative", width: 40, height: 40 }}>
                    <Avatar
                      sx={{
                        width: 40,
                        height: 40,
                        border: `2px solid ${player.role === "dm" ? "#725a42" : "#bfb193"}`,
                        bgcolor: player.role === "dm" ? "#5c4230" : "#a07d60",
                        color: "#fff8f1",
                        fontSize: "0.85rem",
                        fontWeight: 700,
                        fontFamily: "var(--font-work-sans), sans-serif",
                      }}
                    >
                      {player.name.charAt(0).toUpperCase()}
                    </Avatar>
                    {/* Online status indicator — all players in store are connected */}
                    <Box
                      sx={{
                        position: "absolute",
                        bottom: 0,
                        right: 0,
                        width: 10,
                        height: 10,
                        bgcolor: "#4caf50",
                        borderRadius: "50%",
                        border: "2px solid #fdf2df",
                      }}
                    />
                  </Box>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography
                      sx={{
                        fontFamily: "var(--font-work-sans), sans-serif",
                        fontSize: "0.875rem",
                        fontWeight: 600,
                        color: "#3a311b",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        "&:hover": { color: "#725a42" },
                        transition: "color 150ms ease",
                      }}
                    >
                      {player.name}
                    </Typography>
                  }
                  secondary={
                    <Typography
                      sx={{
                        fontFamily: "var(--font-work-sans), sans-serif",
                        fontSize: "0.6rem",
                        fontWeight: 500,
                        color: "#bfb193",
                      }}
                    >
                      {player.role === "dm" ? "Dungeon Master" : "Adventurer"}
                    </Typography>
                  }
                />
              </ListItem>
            ))
          )}
        </List>
      </Box>
    </Box>
  );
}
