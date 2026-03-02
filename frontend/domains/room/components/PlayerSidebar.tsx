"use client";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import Avatar from "@mui/material/Avatar";
import Chip from "@mui/material/Chip";
import ShieldIcon from "@mui/icons-material/Shield";
import { useRoomStore, selectPlayers } from "@/domains/room/store/room.store";

/**
 * Sidebar listing all players currently connected to the game room.
 * Each entry shows the player's avatar initial, display name, and role chip.
 * The DM is indicated with a shield icon. Fixed width, scrollable on overflow.
 */
export function PlayerSidebar(): React.ReactElement {
  const players = useRoomStore(selectPlayers);

  return (
    <Box
      component="aside"
      sx={{
        width: 240,
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        bgcolor: "#EFE9E3",
        borderRight: "1px solid #D9CFC7",
        overflowY: "auto",
      }}
    >
      <Box
        sx={{
          px: 2,
          py: 1.5,
          borderBottom: "1px solid #D9CFC7",
        }}
      >
        <Typography
          variant="overline"
          sx={{
            fontSize: "0.65rem",
            letterSpacing: "0.14em",
            color: "#7d5e45",
            fontWeight: 600,
          }}
        >
          Players ({players.length})
        </Typography>
      </Box>

      <List dense disablePadding sx={{ flex: 1, overflowY: "auto" }}>
        {players.length === 0 ? (
          <ListItem sx={{ py: 2 }}>
            <ListItemText
              primary={
                <Typography variant="body2" color="text.disabled" textAlign="center">
                  No players yet
                </Typography>
              }
            />
          </ListItem>
        ) : (
          players.map((player) => (
            <ListItem
              key={player.id}
              sx={{
                px: 2,
                py: 1,
                "&:hover": { bgcolor: "rgba(0,0,0,0.04)" },
              }}
            >
              <ListItemAvatar sx={{ minWidth: 40 }}>
                <Avatar
                  sx={{
                    width: 30,
                    height: 30,
                    fontSize: "0.8rem",
                    bgcolor: player.role === "dm" ? "#5c4230" : "#a07d60",
                    color: "#F9F8F6",
                  }}
                >
                  {player.name.charAt(0).toUpperCase()}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Typography
                    variant="body2"
                    fontWeight={500}
                    sx={{
                      color: "#1e1410",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {player.name}
                  </Typography>
                }
                secondary={
                  <Chip
                    icon={
                      player.role === "dm" ? (
                        <ShieldIcon sx={{ fontSize: "0.65rem !important" }} />
                      ) : undefined
                    }
                    label={player.role === "dm" ? "DM" : "Player"}
                    size="small"
                    sx={{
                      height: 18,
                      fontSize: "0.62rem",
                      mt: 0.25,
                      bgcolor:
                        player.role === "dm"
                          ? "rgba(92,66,48,0.12)"
                          : "rgba(160,125,96,0.12)",
                      color: player.role === "dm" ? "#5c4230" : "#7d5e45",
                      "& .MuiChip-icon": { ml: 0.5 },
                    }}
                  />
                }
              />
            </ListItem>
          ))
        )}
      </List>
    </Box>
  );
}
