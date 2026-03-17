"use client";

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import type { GeneratedWorldResponse } from "@/domains/world/types";
import { QuestStages } from "@/domains/world/components/QuestStages";
import { RoomCard } from "@/domains/world/components/RoomCard";

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
 * Full read-only display of an LLM-generated world.
 * Shows world name, description, atmosphere, theme badge, active factions,
 * main quest (with QuestStages), and the room list (with RoomCard per room).
 */
export function GeneratedWorldView({ world }: GeneratedWorldViewProps): React.ReactElement {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {/* World name, theme, and atmosphere */}
      <Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1, flexWrap: "wrap" }}>
          <Typography variant="h5" fontWeight={700}>
            {world.world_name}
          </Typography>
          <Chip label={toLabel(world.theme)} variant="outlined" />
        </Box>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          {world.description}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: "italic" }}>
          {world.atmosphere}
        </Typography>
      </Box>

      {/* Active factions */}
      {world.active_factions.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Active Factions
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.75 }}>
              {world.active_factions.map((faction) => (
                <Chip key={faction} label={faction} size="small" variant="outlined" />
              ))}
            </Box>
          </Box>
        </>
      )}

      {/* Main quest */}
      <Divider />
      <Box>
        <Typography variant="h6" fontWeight={700} gutterBottom>
          Main Quest — {world.main_quest.title}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {world.main_quest.description}
        </Typography>
        {world.main_quest.stages.length > 0 && (
          <QuestStages stages={world.main_quest.stages} />
        )}
      </Box>

      {/* Rooms */}
      {world.rooms.length > 0 && (
        <>
          <Divider />
          <Box>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Rooms ({world.rooms.length})
            </Typography>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {world.rooms.map((room, index) => (
                <RoomCard key={index} room={room} />
              ))}
            </div>
          </Box>
        </>
      )}
    </Box>
  );
}
