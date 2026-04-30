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
  /**
   * Called when a player submits a skill check roll from within a room card.
   * @param roomIndex - The room's index within the dungeon.
   * @param skillType - The skill check type (e.g. "Perception").
   * @param dc - The difficulty class for the check.
   * @param rollResult - The d20 roll value the player entered.
   */
  readonly onRollCheck?: (roomIndex: number, skillType: string, dc: number, rollResult: number) => void;
}

/**
 * Full read-only display of a generated dungeon loaded from the API.
 * Shows dungeon name, premise, global modifiers banner (US-068/US-070),
 * the main quest with stage breakdown, and a card for every generated room.
 * Passes onRollCheck down to each DungeonRoomCard for skill check resolution.
 */
export function GeneratedDungeonView({
  dungeon,
  onRollCheck,
}: GeneratedDungeonViewProps): React.ReactElement {
  const globalModifiers = dungeon.quest_metadata?.global_modifiers ?? null;
  const environment = dungeon.quest_metadata?.environment ?? null;

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

      {/* Global modifiers banner (US-068) - shown when quest_metadata is present */}
      {(globalModifiers !== null || environment !== null) && (
        <Box
          sx={{
            bgcolor: "#1a1a2e",
            border: "1px solid #3a2870",
            borderRadius: "4px",
            px: 2,
            py: 1.5,
            display: "flex",
            flexDirection: "column",
            gap: 0.5,
          }}
        >
          {environment !== null && (
            <Typography variant="caption" sx={{ color: "#9090d0", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em" }}>
              Environment: {environment}
            </Typography>
          )}
          {globalModifiers !== null && (
            <Typography variant="caption" sx={{ color: "#c0c0e8", fontStyle: "italic" }}>
              {globalModifiers}
            </Typography>
          )}
        </Box>
      )}

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
              <DungeonQuestStages
                stages={dungeon.quest.stages}
                completedIndices={dungeon.completed_stage_indices}
              />
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
            <DungeonRoomCard
              key={room.index}
              room={room}
              index={room.index}
              onRollCheck={onRollCheck}
            />
          ))}
        </Box>
      </Box>
    </Box>
  );
}
