"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import { RoomCard } from "@/domains/world/components/RoomCard";
import { QuestStages } from "@/domains/world/components/QuestStages";
import type { GeneratedWorldResponse } from "@/domains/world/types";

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

/** Props for the GeneratedWorldView component. */
interface GeneratedWorldViewProps {
  readonly world: GeneratedWorldResponse;
}

/**
 * Full read-only display of a generated world.
 * Shows world metadata, active factions, the main quest with stage breakdown,
 * and a card for every generated room.
 * Intended for DM view after generation — no editing controls.
 */
export function GeneratedWorldView({ world }: GeneratedWorldViewProps): React.ReactElement {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {/* World header */}
      <Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap", mb: 0.5 }}>
          <Typography variant="h5" fontWeight={700}>
            {world.world_name}
          </Typography>
          <Chip label={toLabel(world.theme)} size="small" color="primary" />
        </Box>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          {world.world_description}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: "italic" }}>
          {world.atmosphere}
        </Typography>
      </Box>

      <Divider />

      {/* Active factions */}
      {world.active_factions.length > 0 && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Active Factions
          </Typography>
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            {world.active_factions.map((faction) => (
              <Chip key={faction} label={faction} variant="outlined" size="small" />
            ))}
          </Box>
        </Box>
      )}

      <Divider />

      {/* Main quest */}
      <Box>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Main Quest: {world.main_quest.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {world.main_quest.description}
        </Typography>
        {world.main_quest.stages.length > 0 && (
          <Box sx={{ mt: 1.5 }}>
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              Stages
            </Typography>
            <Box sx={{ mt: 1 }}>
              <QuestStages stages={world.main_quest.stages} />
            </Box>
          </Box>
        )}
      </Box>

      <Divider />

      {/* Room list */}
      <Box>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Rooms ({world.rooms.length})
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
          {world.rooms.map((room) => (
            <RoomCard key={room.index} room={room} />
          ))}
        </Box>
      </Box>
    </Box>
  );
}
