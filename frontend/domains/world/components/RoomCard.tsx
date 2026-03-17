"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import type { NarratedRoomResponse, RoomType } from "@/domains/world/types";

/** Color mapping for room type badges. */
const ROOM_TYPE_COLORS: Record<RoomType, "error" | "success" | "warning" | "secondary" | "primary" | "info"> = {
  BOSS: "error",
  REST: "success",
  SHOP: "warning",
  COMBAT: "secondary",
  TREASURE: "primary",
  EVENT: "info",
};

/** Props for the RoomCard component. */
interface RoomCardProps {
  readonly room: NarratedRoomResponse;
}

/**
 * Displays a single narrated room card with its type badge, name, description,
 * enemy names, NPC names, and any special notes.
 */
export function RoomCard({ room }: RoomCardProps): React.ReactElement {
  const chipColor = ROOM_TYPE_COLORS[room.room_type];

  return (
    <Box
      sx={{
        p: 2,
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2,
        bgcolor: "background.paper",
        display: "flex",
        flexDirection: "column",
        gap: 1,
      }}
    >
      {/* Header: room type badge and name */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
        <Chip
          label={room.room_type}
          size="small"
          color={chipColor}
          variant="filled"
          sx={{ fontWeight: 700, fontSize: "0.65rem" }}
        />
        <Typography variant="subtitle2" fontWeight={600}>
          {room.name}
        </Typography>
      </Box>

      {/* Description */}
      <Typography variant="body2" color="text.secondary">
        {room.description}
      </Typography>

      {/* Enemies */}
      {room.enemy_names.length > 0 && (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, alignItems: "center" }}>
          <Typography variant="caption" color="text.disabled" sx={{ mr: 0.25 }}>
            Enemies:
          </Typography>
          {room.enemy_names.map((name) => (
            <Chip key={name} label={name} size="small" color="error" variant="outlined" />
          ))}
        </Box>
      )}

      {/* NPCs */}
      {room.npc_names.length > 0 && (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, alignItems: "center" }}>
          <Typography variant="caption" color="text.disabled" sx={{ mr: 0.25 }}>
            NPCs:
          </Typography>
          {room.npc_names.map((name) => (
            <Chip key={name} label={name} size="small" variant="outlined" />
          ))}
        </Box>
      )}

      {/* Special notes */}
      {room.special_notes && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ fontStyle: "italic", borderTop: "1px solid", borderColor: "divider", pt: 0.75, mt: 0.25 }}
        >
          {room.special_notes}
        </Typography>
      )}
    </Box>
  );
}
