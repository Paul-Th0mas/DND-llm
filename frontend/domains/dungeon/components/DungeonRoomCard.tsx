"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Typography from "@mui/material/Typography";
import { AppCard } from "@/shared/components/AppCard";
import type { DungeonRoomResponse, RoomType } from "../types";

// Colour mapping for each room type badge.
const ROOM_TYPE_COLORS: Record<
  RoomType,
  "error" | "success" | "warning" | "info" | "default" | "primary"
> = {
  BOSS: "error",
  REST: "success",
  SHOP: "warning",
  TREASURE: "warning",
  COMBAT: "error",
  EVENT: "info",
};

/**
 * Converts a SCREAMING_SNAKE_CASE enum value to Title Case for display.
 * @param value - The raw enum string (e.g. "MEDIEVAL_FANTASY").
 * @returns A human-readable label (e.g. "Medieval Fantasy").
 */
function toLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Props for the DungeonRoomCard component. */
interface DungeonRoomCardProps {
  readonly room: DungeonRoomResponse;
  /** Optional stagger index for the card entrance animation. */
  readonly index?: number;
}

/**
 * Displays a single generated dungeon room with its type badge, name,
 * description, enemy list, NPC list, and any special notes.
 * Uses AppCard for consistent theming across card style modes.
 * Used inside GeneratedDungeonView as a card per room.
 */
export function DungeonRoomCard({ room, index = 0 }: DungeonRoomCardProps): React.ReactElement {
  const badgeColor = ROOM_TYPE_COLORS[room.room_type] ?? "default";

  return (
    <AppCard
      title={`${room.index + 1}. ${room.name}`}
      chips={[
        <Chip
          key="type"
          label={toLabel(room.room_type)}
          size="small"
          color={badgeColor}
          sx={{ fontWeight: 600, fontSize: "0.7rem" }}
        />,
      ]}
      staggerIndex={index}
    >
      <Typography variant="body2" color="text.secondary">
        {room.description}
      </Typography>

      {/* Enemies */}
      {room.enemy_names.length > 0 && (
        <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", alignItems: "center" }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            Enemies:
          </Typography>
          {room.enemy_names.map((name) => (
            <Chip key={name} label={name} size="small" variant="outlined" />
          ))}
        </Box>
      )}

      {/* NPCs */}
      {room.npc_names.length > 0 && (
        <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", alignItems: "center" }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            NPCs:
          </Typography>
          {room.npc_names.map((name) => (
            <Chip key={name} label={name} size="small" variant="outlined" />
          ))}
        </Box>
      )}

      {/* Special notes */}
      {room.special_notes !== null && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ fontStyle: "italic", mt: 0.5 }}
        >
          {room.special_notes}
        </Typography>
      )}
    </AppCard>
  );
}
