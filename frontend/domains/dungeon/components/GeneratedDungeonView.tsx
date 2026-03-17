"use client";

import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import { DungeonRoomCard } from "./DungeonRoomCard";
import { DungeonQuestStages } from "./DungeonQuestStages";
import type { DungeonDetail } from "../types";

/** Props for the GeneratedDungeonView component. */
export interface GeneratedDungeonViewProps {
  readonly dungeon: DungeonDetail;
}

/**
 * Full read-only display of a generated dungeon loaded from the API.
 * Shows dungeon name, premise, the main quest with stage breakdown,
 * and a card for every generated room.
 * Intended for DM view after generation or on the dungeon detail page.
 */
export function GeneratedDungeonView({
  dungeon,
}: GeneratedDungeonViewProps): React.ReactElement {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      {/* Dungeon header */}
      <Box>
        <Typography variant="h5" fontWeight={700} gutterBottom>
          {dungeon.name}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {dungeon.premise}
        </Typography>
      </Box>

      <Divider />

      {/* Main quest */}
      <Box>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Main Quest: {dungeon.quest.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {dungeon.quest.description}
        </Typography>
        {dungeon.quest.stages.length > 0 && (
          <Box sx={{ mt: 1.5 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              fontWeight={600}
            >
              Stages
            </Typography>
            <Box sx={{ mt: 1 }}>
              <DungeonQuestStages stages={dungeon.quest.stages} />
            </Box>
          </Box>
        )}
      </Box>

      <Divider />

      {/* Room list */}
      <Box>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Rooms ({dungeon.rooms.length})
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
          {dungeon.rooms.map((room) => (
            <DungeonRoomCard key={room.index} room={room} />
          ))}
        </Box>
      </Box>
    </Box>
  );
}
